from pathlib import Path
from trimesh import Trimesh

from mesh_analyzer import (
    load_as_mesh,
    build_vertex_adjacency,
)

from mesh_spectral_pipeline import (
    analyze_mesh_components,
)

from geometry_validation import (
    analyze_partition_geometry,
)


def test_stage6_geometry_validation(
    mesh_name:str
)->None:
    project_root:Path=Path(__file__).resolve().parents[1]

    mesh_path:Path=(
        project_root
        /"data"
        /"raw_meshes"
        /"synthetic_s5"
        /mesh_name
    )

    mesh:Trimesh=load_as_mesh(mesh_path)

    adjacency:list[set[int]]=build_vertex_adjacency(
        mesh
    )

    spectral_results:list[dict]=analyze_mesh_components(
        adjacency,
        k=3
    )

    print("\n======================================")
    print("Stage 6 Geometry Validation")
    print("Mesh:")
    print(mesh_name)
    print("======================================")

    for index in range(len(spectral_results)):
        component_result:dict=spectral_results[index]

        if component_result["status"]!="analyzed":
            continue

        partition_1:set[int]=component_result["partition_1"]
        partition_2:set[int]=component_result["partition_2"]

        if len(partition_1)<=len(partition_2):
            smaller_partition:set[int]=partition_1
        else:
            smaller_partition:set[int]=partition_2

        geometry_result:dict=analyze_partition_geometry(
            mesh,
            smaller_partition
        )

        print("\nComponent:")
        print(component_result["component_index"])

        print("Fiedler value:")
        print(component_result["fiedler_value"])

        print("Best conductance:")
        print(component_result["best_conductance"])

        print("Smaller partition size:")
        print(geometry_result["partition_size"])

        print("Principal variances:")
        print(geometry_result["principal_variances"])

        print("Principal variance ratios:")
        print(geometry_result["principal_variance_ratios"])


if __name__=="__main__":
    test_stage6_geometry_validation(
        "small_protrusion.obj"
    )

    test_stage6_geometry_validation(
        "legitimate_thin_appendage.obj"
    )