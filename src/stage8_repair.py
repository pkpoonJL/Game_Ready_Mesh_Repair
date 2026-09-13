import trimesh
from mesh_analyzer import (
    count_boundary_edges,
    count_nonmanifold_edges,
    count_degenerate_faces,
    compute_component_sizes
)
#from scipy.cluster.hierarchy import centroid
from trimesh import Trimesh
from mesh_analyzer import DFS_component_size
import numpy as np
def find_repair_boundary_edges(
    mesh: Trimesh,
    candidate_partition: set[int]
) -> set[tuple[int, int]]:
    original_count:dict[tuple[int,int],int]={}
    original_boundary_edges:set[tuple[int,int]]=set()
    for u,v in mesh.edges:
        #reorder to uv,u<=v
        if v<u:
            u,v=v,u
        original_count[(u,v)]=original_count.get((u,v),0)+1
    for edge,count in original_count.items():
        if count==1:
            original_boundary_edges.add(edge)
    new_count: dict[tuple[int, int], int] = {}
    for face in mesh.faces:
        u, v, w = face

        if (
                u in candidate_partition
                or v in candidate_partition
                or w in candidate_partition
        ):
            continue
        # this face is retained
        sorted_list:list[int]=[u,v,w]
        sorted_list.sort()
        new_count[(sorted_list[0], sorted_list[1])]=new_count.get((sorted_list[0], sorted_list[1]), 0)+1
        new_count[(sorted_list[1], sorted_list[2])] = new_count.get((sorted_list[1], sorted_list[2]), 0)+1
        new_count[(sorted_list[0], sorted_list[2])] = new_count.get((sorted_list[0], sorted_list[2]), 0)+1
    new_boundary_edges:set[tuple[int,int]]=set()
    for edge,count in new_count.items():
        if count==1:
            new_boundary_edges.add(edge)
    extra:set[tuple[int,int]]=set()
    for edges in new_boundary_edges:
        if edges not in original_boundary_edges:
            extra.add(edges)
    return extra
def is_single_closed_loop(
            boundary_edges: set[tuple[int, int]]
    ) -> bool:
    if len(boundary_edges) == 0:
        return False
    vertex_degree:dict[int,int]={}
    for u,v in boundary_edges:
        vertex_degree[u]=vertex_degree.get(u,0)+1
        vertex_degree[v]=vertex_degree.get(v,0)+1
    for _,degree in vertex_degree.items():
        if degree!=2:
            return False
    max_vertex: int = max(vertex_degree.keys())
    adjacency: list[set[int]] = [
        set() for _ in range(max_vertex + 1)
    ]
    for u, v in boundary_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    visited: list[bool] = [
        False for _ in range(max_vertex + 1)
    ]
    start_vertex: int = next(iter(vertex_degree))
    component_size: int = DFS_component_size(
        start_vertex,
        adjacency,
        visited
    )
    if component_size != len(vertex_degree):
        return False
    return True
def evaluate_repair_safety(
    mesh: Trimesh,
    candidate_partition: set[int],
    spectral_result: dict
) -> dict:
    #"safe_to_attempt": bool,
    #"reason_codes": list[str],
    #"boundary_edges": set[tuple[int, int]]
    boundary:set[tuple[int, int]]=find_repair_boundary_edges(mesh, candidate_partition)
    if len(boundary)==0:
        return{
            "safe_to_attempt":False,
            "reason_codes":["Empty_boundary_edges"],
            "boundary_edges":boundary}
    isSingleClosed:bool=is_single_closed_loop(boundary)
    if not isSingleClosed:
        return {
            "safe_to_attempt": False,
            "reason_codes": ["Not Singleclosed"],
            "boundary_edges": boundary}
    candidate_fraction: float = (
            len(candidate_partition)
            / spectral_result["component_size"]
    )
    t_max_candidate: float = 0.35
    if candidate_fraction > t_max_candidate:
        return {
            "safe_to_attempt": False,
            "reason_codes": ["candidate_too_large"],
            "boundary_edges": boundary
        }
    eigengap: float | None = spectral_result["fiedler_eigengap"]

    if eigengap is None or eigengap < 0.001:
        return {
            "safe_to_attempt": False,
            "reason_codes": ["spectral_instability"],
            "boundary_edges": boundary
        }
    ordered_boundary: list[int] = order_boundary_loop(boundary)
    if not is_boundary_planar(mesh, ordered_boundary):
        return {
            "safe_to_attempt": False,
            "reason_codes": ["boundary_not_planar"],
            "boundary_edges": boundary
        }

    if not is_boundary_convex(mesh, ordered_boundary):
        return {
            "safe_to_attempt": False,
            "reason_codes": ["boundary_not_convex"],
            "boundary_edges": boundary
        }
    return{
        "safe_to_attempt": True,
        "reason_codes": ["safety_checks_passed"],
        "boundary_edges": boundary,
        "ordered_boundary": ordered_boundary
    }
def order_boundary_loop(
    boundary_edges: set[tuple[int, int]]
) -> list[int]:
    if len(boundary_edges) == 0:
        return []
    adjacency:dict[int,set[int]]={}
    for u, v in boundary_edges:
        if u not in adjacency:
            adjacency[u] = set()
        if v not in adjacency:
            adjacency[v] = set()
        adjacency[u].add(v)
        adjacency[v].add(u)
    start:int=(next(iter(adjacency)))
    cur:int=start
    result:list[int]=[cur]
    nxt:int=next(iter(adjacency[cur]))
    while(nxt!=start):
        result.append(nxt)
        for u in adjacency[nxt]:
            if u != cur:
                cur=nxt
                nxt=u
                break
    return result
def is_boundary_planar(
    mesh: Trimesh,
    ordered_boundary: list[int]
) -> bool:
    if len(ordered_boundary) < 3:
        return False
    x_component:float=0.0
    y_component:float=0.0
    z_component:float=0.0
    for index in ordered_boundary:
        x,y,z=mesh.vertices[index]
        x_component+=x
        y_component+=y
        z_component+=z
    x_component=x_component/len(ordered_boundary)
    y_component=y_component/len(ordered_boundary)
    z_component=z_component/len(ordered_boundary)
    centroid:list[float]=[x_component, y_component, z_component]
    C:np.ndarray=np.zeros((3,3))
    for index in ordered_boundary:
        x, y, z = mesh.vertices[index]
        q=np.array([x- centroid[0],y - centroid[1],z - centroid[2]])
        q_col=q.reshape(3,1)
        outer=q_col@q_col.T
        C+=outer
    C/=len(ordered_boundary)
    eigenvalues,_ = np.linalg.eigh(C)
    lambda_3 = float(eigenvalues[0])
    lambda_2 = float(eigenvalues[1])
    lambda_1 = float(eigenvalues[2])
    if lambda_1 <= np.finfo(float).tiny:
        return False
    r3: float = lambda_3 / lambda_1
    r2: float = lambda_2 / lambda_1

    #print(
    #    f"Boundary PCA: n={len(ordered_boundary)}, "
    #    f"r2={r2:.8f}, r3={r3:.8f}"
    #)
    #print("Boundary vertices:")
    #for index in ordered_boundary:
     #   print(index, mesh.vertices[index])
    t_planar: float = 0.01
    t_nondegenerate: float = 0.01
    if r3<t_planar and r2>t_nondegenerate:
        return True
    return False
def boundary_direction_matches_face(
    mesh: Trimesh,
    u: int,
    v: int
) -> bool:
    for face in mesh.faces:
        a, b, c = map(int, face)
        directed_edges = [
            (a, b),
            (b, c),
            (c, a)
        ]
        if (u, v) in directed_edges:
            return True
        if (v, u) in directed_edges:
            return False
    raise RuntimeError("Boundary edge has no retained adjacent face")
def repair_candidate_region(
    mesh: Trimesh,
    candidate_partition: set[int],
    safety_result: dict
) -> Trimesh | None:
    if not safety_result["safe_to_attempt"]:
        return None
    repaired_mesh=mesh.copy()
    keep:list[bool]=[]
    for face in mesh.faces:
        u,v,w=face
        if u in candidate_partition or v in candidate_partition or w in candidate_partition:
            keep.append(False)
        else:
            keep.append(True)
    repaired_mesh.update_faces(keep)
    ordered_boundary: list[int] = safety_result["ordered_boundary"]
    x_component: float = 0.0
    y_component: float = 0.0
    z_component: float = 0.0
    for index in ordered_boundary:
        x, y, z = mesh.vertices[index]
        x_component += x
        y_component += y
        z_component += z
    x_component = x_component / len(ordered_boundary)
    y_component = y_component / len(ordered_boundary)
    z_component = z_component / len(ordered_boundary)
    boundary_count: int = len(ordered_boundary)
    centroid_index: int = len(repaired_mesh.vertices)
    centroid_array: np.ndarray = np.array(
        [[x_component, y_component, z_component]]
    )
    repaired_mesh.vertices = np.vstack(
        [repaired_mesh.vertices, centroid_array]
    )
    cap_faces: list[list[int]]=[]
    first_u: int = ordered_boundary[0]
    first_v: int = ordered_boundary[1]

    same_direction: bool = boundary_direction_matches_face(
        repaired_mesh,
        first_u,
        first_v
    )
    for i in range(boundary_count):
        current_vertex: int = ordered_boundary[i]
        next_vertex: int = ordered_boundary[(i + 1) % boundary_count]

        if same_direction:
            cap_faces.append([
                next_vertex,
                current_vertex,
                centroid_index
            ])
        else:
            cap_faces.append([
                current_vertex,
                next_vertex,
                centroid_index
            ])
    repaired_mesh.faces = np.vstack(
        [
            repaired_mesh.faces,
            np.array(cap_faces, dtype=int)
        ]
    )
    repaired_mesh.remove_unreferenced_vertices()
    return repaired_mesh
def is_boundary_convex(
    mesh: Trimesh,
    ordered_boundary: list[int]
) -> bool:
    if len(ordered_boundary) < 3:
        return False
    x_component:float=0.0
    y_component:float=0.0
    z_component:float=0.0
    for index in ordered_boundary:
        x,y,z=mesh.vertices[index]
        x_component+=x
        y_component+=y
        z_component+=z
    x_component=x_component/len(ordered_boundary)
    y_component=y_component/len(ordered_boundary)
    z_component=z_component/len(ordered_boundary)
    centroid:list[float]=[x_component, y_component, z_component]
    C:np.ndarray=np.zeros((3,3))
    for index in ordered_boundary:
        x, y, z = mesh.vertices[index]
        q=np.array([x- centroid[0],y - centroid[1],z - centroid[2]])
        q_col=q.reshape(3,1)
        outer=q_col@q_col.T
        C+=outer
    C/=len(ordered_boundary)
    _,eigenvectors= np.linalg.eigh(C)
    normal: np.ndarray = eigenvectors[:, 0]
    sampled:bool=False
    sampled_result:float=0.0
    eps: float = 1e-10
    n: int = len(ordered_boundary)
    for i in range(n):
        p0 = mesh.vertices[ordered_boundary[i]]
        p1 = mesh.vertices[ordered_boundary[(i + 1) % n]]
        p2 = mesh.vertices[ordered_boundary[(i + 2) % n]]
        edge_1: np.ndarray = p1 - p0
        edge_2: np.ndarray = p2 - p1
        cross: np.ndarray = np.cross(edge_1, edge_2)
        turn: float = float(np.dot(cross, normal))
        turn_scale: float = float(
            np.linalg.norm(edge_1)
            * np.linalg.norm(edge_2)
        )
        if turn_scale <= np.finfo(float).tiny:
            continue
        normalized_turn: float = turn / turn_scale
        if abs(normalized_turn) <= eps:
            continue
        if not sampled:
            sampled_result = normalized_turn
            sampled = True
        else:
            if normalized_turn * sampled_result < 0:
                return False
    if not sampled:
        return False
    return True
def validate_repaired_mesh(
    repaired_mesh:Trimesh
)->dict:
    reasons:list[str]=[]
    boundary:int=count_boundary_edges(repaired_mesh)
    nonmanifold:int=count_nonmanifold_edges(repaired_mesh)
    degenerate:int=count_degenerate_faces(repaired_mesh)
    components:list[int]=compute_component_sizes(repaired_mesh)

    if boundary>0:
        reasons.append("open_boundary")
    if nonmanifold>0:
        reasons.append("nonmanifold_edges")
    if degenerate>0:
        reasons.append("degenerate_faces")
    if len(components)!=1:
        reasons.append("unexpected_components")

    return{
        "valid":len(reasons)==0,
        "reason_codes":reasons,
        "boundary_edges":boundary,
        "nonmanifold_edges":nonmanifold,
        "degenerate_faces":degenerate,
        "connected_components":len(components)
    }