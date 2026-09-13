
from trimesh import Trimesh
import numpy as np
def extract_partition_coordinates(
    mesh:Trimesh,
    partition:set[int]
)->np.ndarray:
    #partition is in original vertex ids
    coordinates: list[np.ndarray] = []
    for v_id in partition:
        coordinates.append(mesh.vertices[v_id])
    result:np.ndarray=np.array(coordinates)
    return result
def compute_principal_variances(
    coordinates:np.ndarray
)->np.ndarray:
    centroid:np.ndarray=np.zeros(3)
    for v in coordinates:
        centroid+=v
    centroid/=len(coordinates)
    covariance_matrix: np.ndarray=np.zeros((3, 3))
    for v in coordinates:
        q:np.ndarray=v-centroid
        covariance_matrix+=np.outer(q,q)
    covariance_matrix/=len(coordinates)
    eigenvalues:np.ndarray=np.linalg.eigvalsh(covariance_matrix)
    eigenvalues=eigenvalues[::-1]
    return eigenvalues
def compute_principal_variance_ratios(

    principal_variances:np.ndarray
)->np.ndarray:
    eps: float = 1e-12
    if abs(principal_variances[0])<eps:
        raise ValueError('principal_variance0 is Zero')
    result_arr:list[float]=[]
    for index in range(1,len(principal_variances)):
        result_arr.append(float(principal_variances[index]/principal_variances[0]))
    result:np.ndarray=np.array(result_arr)
    return result
def analyze_partition_geometry(
    mesh:Trimesh,
    partition:set[int]
)->dict:
    coordinates:np.ndarray=extract_partition_coordinates(
        mesh,
        partition
    )
    principal_variances:np.ndarray=compute_principal_variances(
        coordinates
    )
    principal_variance_ratios:np.ndarray=compute_principal_variance_ratios(
        principal_variances
    )
    result:dict={
        "partition_size":len(partition),
        "principal_variances":principal_variances,
        "principal_variance_ratios":principal_variance_ratios
    }
    return result
