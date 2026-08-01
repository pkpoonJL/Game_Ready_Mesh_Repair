from typing import TypeAlias
import trimesh
from  mesh_analyzer import *
AdjacencyList: TypeAlias = list[set[int]]
def build_vertex_adjacency(mesh: trimesh.Trimesh)->AdjacencyList:
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
def get_degrees(adjacency: AdjacencyList)->list[int]:
    degrees:list[int]=[]
    for v in adjacency:
        degrees.append(len(v))
    return degrees
def count_graph_edges(adjacency: AdjacencyList)->int:
    degrees:list[int]=get_degrees(adjacency)
    total_degree:int=0
    for d in degrees:
        total_degree+=d
    return total_degree//2
def DFS(start_vertex:int,adjacency:AdjacencyList, labels: list[int],
    component_id: int,)->None:
    stack:list[int]=[start_vertex]
    labels[start_vertex]=component_id
    while stack:
        vertex=stack.pop()
        adjacent:set[int]=adjacency[vertex]
        for v in adjacent:
            if labels[v]==-1:
                stack.append(v)
                labels[v]=component_id
def relabel_components_by_size(labels: list[int])->list[int]:
    component_size:dict[int,int]={}
    for old_id in labels:
        if old_id not in component_size:
            component_size[old_id]=0
        component_size[old_id]+=1
    component_info: list[tuple[int, int]]=[]
    for old_id,size in component_size.items():
        component_info.append((-size,old_id))
    component_info.sort()
    mapping:list[int]=[-1]*len(labels)
    for index in range(len(component_info)):
        mapping[component_info[index][1]]=index
    relabeled_index:list[int]=labels.copy()
    for index in range(len(relabeled_index)):
        old_id:int=relabeled_index[index]
        relabeled_index[index]=mapping[old_id]
    return relabeled_index
def compute_vertex_component_labels(mesh: trimesh.Trimesh)->list[int]:
    Adjacency=build_vertex_adjacency(mesh)
    n=len(mesh.vertices)
    component_id:int=0
    label:list[int]=[-1 for _ in range(n)]
    for v in range (n):
        if label[v]==-1:
            DFS(v,Adjacency,label,component_id)
            component_id+=1
    return label

