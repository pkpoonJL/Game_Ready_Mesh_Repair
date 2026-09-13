from pathlib import Path
import numpy as np
import trimesh
from trimesh import Trimesh

from mesh_graph import build_vertex_adjacency
from mesh_spectral_pipeline import analyze_mesh_components
from stage7_dataset_test import select_smaller_partition
from stage8_repair import (
    find_repair_boundary_edges,
    order_boundary_loop,
    evaluate_repair_safety
)


def boundary_pca_ratio(
    mesh:Trimesh,
    ordered_boundary:list[int]
)->float:
    points:np.ndarray=np.array([
        mesh.vertices[index]
        for index in ordered_boundary
    ])

    centroid:np.ndarray=np.mean(
        points,
        axis=0
    )

    centered:np.ndarray=points-centroid
    C:np.ndarray=(
        centered.T@centered
        /len(points)
    )

    eigenvalues,_=np.linalg.eigh(C)

    lambda_3:float=float(eigenvalues[0])
    lambda_1:float=float(eigenvalues[2])

    if lambda_1<=1e-12:
        return float("inf")

    return lambda_3/lambda_1


def main()->None:
    project_root:Path=(
        Path(__file__)
        .resolve()
        .parents[1]
    )

    mesh_path:Path=(
        project_root
        /"data"
        /"raw_meshes"
        /"synthetic_s7"
        /"appendage_long.obj"
    )

    original:Trimesh=trimesh.load_mesh(
        mesh_path,
        process=False
    )

    adjacency:list[set[int]]=build_vertex_adjacency(
        original
    )

    spectral_results:list[dict]=analyze_mesh_components(
        adjacency
    )

    analyzed:list[dict]=[
        result
        for result in spectral_results
        if result["status"]=="analyzed"
    ]

    main_component:dict=max(
        analyzed,
        key=lambda result:result["component_size"]
    )

    candidate_partition:set[int]=select_smaller_partition(
        main_component,
        adjacency
    )

    boundary:set[tuple[int,int]]=find_repair_boundary_edges(
        original,
        candidate_partition
    )

    ordered_boundary:list[int]=order_boundary_loop(
        boundary
    )

    perturb_vertex:int=ordered_boundary[0]

    deltas:list[float]=[
        0.0,
        0.01,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0
    ]

    print("="*80)
    print("S9 BOUNDARY PERTURBATION TEST")
    print("="*80)

    print(
        "Perturbed boundary vertex:",
        perturb_vertex
    )

    for delta in deltas:
        mesh:Trimesh=original.copy()

        mesh.vertices[
            perturb_vertex,
            0
        ]+=delta

        ratio:float=boundary_pca_ratio(
            mesh,
            ordered_boundary
        )

        safety:dict=evaluate_repair_safety(
            mesh,
            candidate_partition,
            main_component
        )

        print(
            f" delta={delta:<5} "
            f"r3={ratio:<12.8f} "
            f"safe={str(safety['safe_to_attempt']):<5} "
            f"reason={safety['reason_codes']}"
        )

    print("="*80)


if __name__=="__main__":
    main()