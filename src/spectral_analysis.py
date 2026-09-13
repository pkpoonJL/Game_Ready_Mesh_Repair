from  mesh_analyzer import *
AdjacencyList: TypeAlias = list[set[int]]
from scipy.sparse import csr_matrix
def build_sparse_adjacency_matrix(adjacency: AdjacencyList)->csr_matrix:
    n:int=len(adjacency)
    rows: list[int]=[]
    cols:list[int]=[]
    data:list[int]=[]
    for index in range(n):
        u:int=index
        for v in adjacency[u]:
            #define u->v to be A[u][v]=1
            rows.append(u)
            cols.append(v)
            data.append(1)
    A = csr_matrix((data, (rows, cols)), shape=(n, n))
    return A
def build_combinatorial_laplacian(adjacency: AdjacencyList)->csr_matrix:
    A:csr_matrix=build_sparse_adjacency_matrix(adjacency)
    n:int=len(adjacency)
    rows:list[int]=[]
    cols:list[int]=[]
    data:list[int]=[]
    for index in range(n):
        rows.append(index)
        cols.append(index)
        data.append(len(adjacency[index]))
    D = csr_matrix((data,(rows,cols)), shape=(n, n))
    L:csr_matrix=D-A
    return L
def build_symmetric_normalized_laplacian(adjacency: AdjacencyList)->csr_matrix:
    #L_sym=D^{-1/2}(D-A)D^{-1/2}
    c_laplacian:csr_matrix=build_combinatorial_laplacian(adjacency)
    n: int = len(adjacency)
    rows: list[int]=[]
    cols: list[int]=[]
    data: list[float]=[]
    for index in range(n):
        rows.append(index)
        cols.append(index)
        degree:int=len(adjacency[index])
        entry:float=0.0
        if(degree==0):
            entry=0.0
        else:
            entry=1/sqrt(degree)
        data.append(entry)
    D_inv_sqrt=csr_matrix((data, (rows, cols)), shape=(n, n))
    symmetric_normalized_laplacian=D_inv_sqrt@c_laplacian@D_inv_sqrt
    return symmetric_normalized_laplacian

