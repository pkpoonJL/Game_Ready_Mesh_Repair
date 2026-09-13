import numpy as np
from mesh_graph import *
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
def build_fiedler_ordering(fiedler_vector: np.ndarray)->list[int]:
    sorting_list:list[tuple[float,int]]=[]
    n:int=len(fiedler_vector)
    for index in range(n):
        sorting_list.append((fiedler_vector[index],index))
    sorting_list.sort()
    result:list[int]=[]
    for index in range(n):
        _,i=sorting_list[index]
        result.append(i)
    return result
def generate_sweep_candidates(ordering: list[int]) -> list[set[int]]:
    n:int=len(ordering)
    vertice_set:list[set[int]]=[set()for _ in range(n-1)]
    for i in range(n-1):
        if i==0:
            vertice_set[0]={ordering[0]}
            continue
        vertice_set[i]=vertice_set[i-1].copy()
        vertice_set[i].add(ordering[i])
    return vertice_set
def compute_candidate_conductance(candidate:set[int],adjacency:list[set[int]])->float:
    #examine quality of the cut
    degree:list[int]=get_degrees(adjacency)
    cut:int=0
    n:int=len(adjacency)
    for v in candidate:
        for neighbor in adjacency[v]:
            if neighbor not in candidate:
                cut+=1
    vol_1:int=0
    vol_2:int=0
    for index in range(n):
        if index in candidate:
            vol_1+=degree[index]
        else:
            vol_2+=degree[index]
    if min(vol_1,vol_2)==0:
        raise ValueError("MinVolume equals to 0")
    return cut/min(vol_1,vol_2)
def find_best_sweep_cut(candidates: list[set[int]],adjacency: list[set[int]])->tuple[set[int], float]:
    if len(candidates)==0:
        raise ValueError("No sweep candidates")
    best_phi:float=compute_candidate_conductance(candidates[0],adjacency)
    best_phi_index:int=0
    for index in range (1,len(candidates)):
        cur_candidate_conductance:float=compute_candidate_conductance(candidates[index],adjacency)
        if cur_candidate_conductance<best_phi:
            best_phi=cur_candidate_conductance
            best_phi_index=index
    return(candidates[best_phi_index],best_phi)
def extract_cut_edges(candidate: set[int],adjacency: list[set[int]])->list[tuple[int, int]]:
    result:list[tuple[int, int]]=[]
    for v in candidate:
        for neighbor in adjacency[v]:
            if neighbor not in candidate:
                result.append((v,neighbor))#(ES,ES')
    return result







        
        