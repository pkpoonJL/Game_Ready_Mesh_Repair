import numpy as np
from spectral_analysis import (
    build_symmetric_normalized_laplacian,
)
from spectral_eigen_analysis import (
    compute_smallest_eigenpairs,
    reordering,
    extract_fiedler_pair,
)
from spectral_sweep_analysis import (
    build_fiedler_ordering,
    generate_sweep_candidates,
    find_best_sweep_cut,
    extract_cut_edges,
)
def DFS_to_list(start_vertex:int,adjacency:list[set[int]],checked:list[int])->set[int]:
    stack:list[int]=[start_vertex]
    checked[start_vertex]=1
    result:set[int]=set()
    result.add(start_vertex)
    while stack:
        vertex=stack.pop()
        adjacent:set[int]=adjacency[vertex]
        for v in adjacent:
            if checked[v]==-1:
                stack.append(v)
                result.add(v)
                checked[v]=1
    return result
def extract_connected_components(
    vertices_count: int,
    adjacency: list[set[int]]
) -> list[set[int]]:
    n:int=vertices_count
    checked:list[int]=[-1]*n
    result:list[set[int]]=[]
    for index in range(n):
        if checked[index]==-1:
            DFS_result:set[int]=DFS_to_list(index,adjacency,checked).copy()
            result.append(DFS_result)
    return result
def build_component_adjacency(
    component: set[int],
    adjacency: list[set[int]]
) -> tuple[
    list[set[int]],
    dict[int, int],
    list[int]
]:
    #local_adjacency
    #original_to_local
    #local_to_original
    #assune component is sorted
    ordered_component:list[int]=sorted(component)
    original_to_local:dict[int, int]={}
    local_to_original=ordered_component.copy()
    local_index=0
    for v in ordered_component:
        original_to_local[v]=local_index
        local_index+=1
    local_adjacency:list[set[int]]=[]
    for v in ordered_component:
        Localset:set[int]=set()
        for neighbor in adjacency[v]:
            Localset.add(original_to_local[neighbor])
        local_adjacency.append(Localset)
    return(local_adjacency,original_to_local,local_to_original)
def map_cut_edges_to_original(
    cut_edges: list[tuple[int, int]],
    local_to_original: list[int]
) -> list[tuple[int, int]]:
    result:list[tuple[int,int]]=[]
    for e in cut_edges:
        result.append((local_to_original[e[0]],local_to_original[e[1]]))
    return result
def analyze_mesh_components(
    adjacency:list[set[int]],
    k:int=3
)->list[dict]:
    vertices_count:int=len(adjacency)

    components:list[set[int]]=extract_connected_components(
        vertices_count,
        adjacency
    )

    result:list[dict]=[]

    for component_index in range(len(components)):
        component:set[int]=components[component_index]
        component_size:int=len(component)

        if component_size<3:
            component_result:dict={
                "component_index":component_index,
                "component_size":component_size,
                "status":"skipped",
                "reason":"Component too small for spectral analysis",
                "cut_edges":[]
            }

            result.append(component_result)
            continue

        component_data:tuple[
            list[set[int]],
            dict[int,int],
            list[int]
        ]=build_component_adjacency(
            component,
            adjacency
        )

        local_adjacency:list[set[int]]=component_data[0]
        original_to_local:dict[int,int]=component_data[1]
        local_to_original:list[int]=component_data[2]

        local_k:int=min(k,component_size-1)

        laplacian=build_symmetric_normalized_laplacian(
            local_adjacency
        )

        eigenpairs:tuple[np.ndarray,np.ndarray]=compute_smallest_eigenpairs(
            laplacian,
            local_k
        )

        eigenpairs=reordering(eigenpairs)
        eigenvalues: np.ndarray = eigenpairs[0]
        fiedler_pair:tuple[float,np.ndarray]=extract_fiedler_pair(
            eigenpairs
        )

        fiedler_value:float=fiedler_pair[0]
        fiedler_vector:np.ndarray=fiedler_pair[1]
        fiedler_eigengap: float | None = None

        if len(eigenvalues) >= 3:
            fiedler_eigengap = float(
                eigenvalues[2] - eigenvalues[1]
            )
        ordering:list[int]=build_fiedler_ordering(
            fiedler_vector
        )

        candidates:list[set[int]]=generate_sweep_candidates(
            ordering
        )

        best_cut:tuple[set[int],float]=find_best_sweep_cut(
            candidates,
            local_adjacency
        )

        best_candidate:set[int]=best_cut[0]
        best_phi:float=best_cut[1]
        partition_size_1: int = len(best_candidate)
        partition_size_2: int = component_size-partition_size_1
        original_partition_1: set[int] = map_partition_to_original(
            best_candidate,
            local_to_original
        )
        original_partition_2: set[int] = component - original_partition_1
        local_cut_edges:list[tuple[int,int]]=extract_cut_edges(
            best_candidate,
            local_adjacency
        )

        original_cut_edges:list[tuple[int,int]]=map_cut_edges_to_original(
            local_cut_edges,
            local_to_original
        )

        component_result:dict={
            "component_index":component_index,
            "component_size":component_size,
            "status":"analyzed",
            "fiedler_value":fiedler_value,
            "fiedler_eigengap": fiedler_eigengap,
            "best_conductance":best_phi,
            "partition_size_1": partition_size_1,
            "partition_size_2": partition_size_2,
            "partition_1": original_partition_1,
            "partition_2": original_partition_2,
            "cut_edges":original_cut_edges
        }

        result.append(component_result)

    return result
def map_partition_to_original(
    partition:set[int],
    local_to_original:list[int]
)->set[int]:
    original:set[int]=set()
    for local_index in partition:
        original.add(local_to_original[local_index])
    return original




