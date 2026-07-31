from pathlib import Path
from typing import TypeAlias
from math import sqrt
import pandas as pd
import trimesh
SUPPORTED_EXTENSIONS = {".obj", ".ply", ".stl", ".glb", ".gltf"}
Vec3: TypeAlias = tuple[float, float, float]
MeshMetrics: TypeAlias = tuple[int, int, int]
AdjacencyList: TypeAlias = list[set[int]]
def cross(vector_1:Vec3,vector_2:Vec3)->Vec3:
    u1,u2,u3=vector_1
    v1,v2,v3=vector_2
    return u2*v3-u3*v2,u3*v1-u1*v3,u1*v2-u2*v1
def norm(vector_1:Vec3)->float:
    dx,dy,dz=vector_1
    return sqrt(dx*dx+dy*dy+dz*dz)
def load_as_mesh(path:Path)->trimesh.Trimesh:
    loaded = trimesh.load(path, force=None)
    if isinstance(loaded, trimesh.Scene):#case:multiple meshes
        meshes=[]
        for geo_object in loaded.geometry.values():
            if isinstance(geo_object,trimesh.Trimesh):
                meshes.append(geo_object)
        if not meshes: raise ValueError(f"No mesh geometry found in scene: {path}")
        return trimesh.util.concatenate(meshes)
    if isinstance(loaded,trimesh.Trimesh):#case:single mesh
        return loaded
    raise TypeError(f"Unsupported loaded object type: {type(loaded)}")#case object type not supported
def build_edge_count(faces)->dict[Vec3]:
    #enumerate faces
    edge_count={}#empty map for counting
    for face in faces:#face=[int,int,int]
        a,b,c=int(face[0]),int(face[1]),int(face[2])
        #create pairs
        edges=[(a,b),(b,c),(c,a)]
        for Edge in edges:
            v1,v2=Edge
            if v1>v2:
                v1,v2=v2,v1
            e=(v1,v2)
            if e not in edge_count:
                edge_count[e]=0
            edge_count[e]+=1
    return edge_count
def count_boundary_edges(mesh:trimesh.Trimesh)->int:
    faces=mesh.faces
    edge_count=build_edge_count(faces)
    boundary_edges=0
    for edge,count in edge_count.items():
        if count==1:
            boundary_edges+=1
    return boundary_edges
def count_nonmanifold_edges(mesh:trimesh.Trimesh)->int:
    faces=mesh.faces
    edge_count=build_edge_count(faces)
    nonmanifold_edges_count=0
    for edge,count in edge_count.items():
        if count>2:
            nonmanifold_edges_count+=1
    return nonmanifold_edges_count
def count_degenerate_faces(mesh:trimesh.Trimesh, eps:float=1e-12)->int:
    faces=mesh.faces
    degenerate_face_count=0
    for face in faces:
        ia,ib,ic =int(face[0]),int(face[1]),int(face[2])
        ax,ay,az=mesh.vertices[ia]
        bx,by,bz=mesh.vertices[ib]
        cx,cy,cz=mesh.vertices[ic]
        vector_ab=(bx-ax,by-ay,bz-az)
        vector_ac=(cx-ax,cy-ay,cz-az)
        area=0.5*norm(cross(vector_ab,vector_ac))
        if area<eps:
            degenerate_face_count+=1
    return degenerate_face_count
def analyze_mesh(mesh:trimesh.Trimesh,eps:float=1e-12)->MeshMetrics:
    boundary_edges=count_boundary_edges(mesh)
    nonmanifold_edges=count_nonmanifold_edges(mesh)
    degenerate_face_count=count_degenerate_faces(mesh, eps)
    return boundary_edges,nonmanifold_edges,degenerate_face_count
def print_metrics(metrics: MeshMetrics) -> None:
    boundary_edges,nonmanifold_edges,degenerate_faces=metrics
    print("boundary_edges:", boundary_edges)
    print("nonmanifold_edges:", nonmanifold_edges)
    print("degenerate_faces:", degenerate_faces)
def build_vertex_adjacency(mesh: trimesh.Trimesh) -> AdjacencyList:
    faces=mesh.faces
    n=len(mesh.vertices)
    adjacency:list[set[int]]=[set()for _ in range(n)]#prepare an array of empty sets
    for face in faces:
        va:int=int(face[0])
        vb:int=int(face[1])
        vc:int=int(face[2])
        adjacency[va].add(vb)
        adjacency[va].add(vc)
        adjacency[vb].add(va)
        adjacency[vb].add(vc)
        adjacency[vc].add(va)
        adjacency[vc].add(vb)
    return adjacency
def DFS_component_size(start_vertex:int,adjacency:AdjacencyList,visited:list[bool])->int:
    stack:list[int]=[start_vertex]
    visited[start_vertex]=True
    size:int=0
    while stack:
        vertex=stack.pop()
        size+=1
        adjacent:set[int]=adjacency[vertex]
        for v in adjacent:
            if visited[v]==False:
                stack.append(v)
                visited[v]=True
    return size
def compute_component_sizes(mesh: trimesh.Trimesh) -> list[int]:
    adjacency:AdjacencyList=build_vertex_adjacency(mesh)
    n=len(mesh.vertices)
    visited:list[bool]=[False for _ in range(n)]
    component_sizes:list[int]=[]
    for index in range(n):
        if not visited[index]:
            component_sizes.append(DFS_component_size(index,adjacency,visited))
    component_sizes.sort(reverse=True)
    return component_sizes
def count_connected_components(mesh: trimesh.Trimesh) -> int:
    component_sizes:list[int]=compute_component_sizes(mesh)
    return len(component_sizes)
def count_tiny_components(component_sizes:list[int],min_vertices:int=10)->int:
    for index in range(len(component_sizes)):
        if index==0:
            continue
        if component_sizes[index]<min_vertices:
            return len(component_sizes)-index
    return 0
def count_tiny_component_vertices(component_sizes:list[int],min_vertices:int=10)->int:
    vertices_count:int=0
    for index in range(1,len(component_sizes)):
        if component_sizes[index]<min_vertices:
            vertices_count+=component_sizes[index]
    return vertices_count
def main()->None:
    if __name__ == "__main__":
        main()