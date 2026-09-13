import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
def compute_smallest_eigenpairs(laplacian: csr_matrix,k: int)->tuple[np.ndarray, np.ndarray]:
    #return tuple[np.ndarray,np.ndarray]
    #eigenvalue[i]-> the i th smallest eigenvalue
    #eigenvectors[:, i] is the eigenvector corresponding to eigenvalues[i]
    eigenvalues, eigenvectors = eigsh(laplacian, k=k, which="SM")
    return eigenvalues, eigenvectors
def reordering(EigenPairs:tuple[np.ndarray,np.ndarray])->tuple[np.ndarray,np.ndarray]:
    eigenvalues,eigenvectors=EigenPairs
    k:int=len(eigenvalues)
    n:int=len(eigenvectors)
    pairs:list[tuple[float,int]]=[]
    for i in range(k):
        eigenvalue:float=float(eigenvalues[i])
        pairs.append((eigenvalue,i))
    pairs.sort()
    reordered_eigenvalues:np.ndarray=np.zeros(k)
    for i in range(k):
        reordered_eigenvalues[i]=pairs[i][0]
    reordered_eigenvectors:np.ndarray=np.zeros((n,k))
    for i in range(k):
        old_index:int=pairs[i][1]
        correspond:np.ndarray=eigenvectors[:,old_index]
        reordered_eigenvectors[:,i]=correspond
    return reordered_eigenvalues, reordered_eigenvectors
def count_zero_eigenvalues(EigenPairs:tuple[np.ndarray,np.ndarray],eps:float=1e-8)->int:
    eigenval,eigenvec=EigenPairs
    count=0
    for val in eigenval:
        if abs(val)<eps:
            count+=1
    return count
def eigenpair_residuals(laplacian: csr_matrix,EigenPairs:tuple[np.ndarray,np.ndarray])->list[float]:
    eigenval,eigenvec=EigenPairs
    n,k=eigenvec.shape
    ans=[]
    for index in range(k):
        Lambda=eigenval[index]
        u=eigenvec[:,index]
        result:np.ndarray=laplacian@u-Lambda*u
        acc:float=0.0
        for e in result:
            acc+=e*e
        ans.append(np.sqrt(acc))
    return ans
def extract_fiedler_pair(EigenPairs: tuple[np.ndarray, np.ndarray],eps: float = 1e-8)->tuple[float, np.ndarray]:
    eigenval,eigenvec=EigenPairs
    n,k=eigenvec.shape
    if k<2:
        raise ValueError("Not enough eigenvalues")
    if abs(eigenval[0])<eps and abs(eigenval[1])>=eps:
        return(eigenval[1],eigenvec[:,1])
    raise ValueError("Fieder pair not found")



