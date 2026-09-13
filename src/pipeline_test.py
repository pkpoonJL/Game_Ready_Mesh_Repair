from pathlib import Path
from trimesh import Trimesh

from mesh_analyzer import (
    load_as_mesh,
    build_vertex_adjacency,
)

from mesh_spectral_pipeline import (
    analyze_mesh_components,
)


def test_real_mesh_spectral_pipeline() -> None:
    project_root:Path=Path(__file__).resolve().parents[1]

    mesh_path:Path=project_root/"data"/"raw_meshes"/"synthetic_s5"/"small_protrusion.obj"

    mesh:Trimesh=load_as_mesh(mesh_path)

    vertices_count:int=len(mesh.vertices)

    adjacency:list[set[int]]=build_vertex_adjacency(
        mesh
    )

    print("=== Stage 5 Real Mesh Spectral Test ===")
    print("Mesh path:")
    print(mesh_path)

    print("\nVertices:")
    print(vertices_count)

    print("\nFaces:")
    print(len(mesh.faces))

    results:list[dict]=analyze_mesh_components(
        adjacency,
        k=3
    )

    print("\nConnected components:")
    print(len(results))

    for index in range(len(results)):
        component_result:dict=results[index]

        print("\n------------------------------")
        print("Component:")
        print(component_result["component_index"])

        print("Component size:")
        print(component_result["component_size"])

        print("Status:")
        print(component_result["status"])

        if component_result["status"]=="skipped":
            print("Reason:")
            print(component_result["reason"])
            continue

        print("Fiedler value:")
        print(component_result["fiedler_value"])

        print("Best conductance:")
        print(component_result["best_conductance"])

        print("Partition size 1:")
        print(component_result["partition_size_1"])

        print("Partition size 2:")
        print(component_result["partition_size_2"])

        print("Cut edges:")
        print(component_result["cut_edges"])

        print("Cut edge count:")
        print(len(component_result["cut_edges"]))

    print("\nStage 5 real mesh spectral pipeline finished.")


if __name__=="__main__":
    test_real_mesh_spectral_pipeline()