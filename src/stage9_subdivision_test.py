from pathlib import Path
from tempfile import TemporaryDirectory
import trimesh
from trimesh import Trimesh

from stage7_dataset_test import analyze_mesh


def compare_result(
    reference:dict,
    current:dict
)->list[str]:
    failures:list[str]=[]

    if reference["decision"]!=current["decision"]:
        failures.append("decision_changed")

    if reference["shape_class"]!=current["shape_class"]:
        failures.append("shape_changed")

    if reference.get("s8_safe")!=current.get("s8_safe"):
        failures.append("s8_safety_changed")

    if reference.get("s8_valid")!=current.get("s8_valid"):
        failures.append("s8_validation_changed")

    return failures


def subdivide_mesh(
    mesh:Trimesh
)->Trimesh:
    vertices,faces=trimesh.remesh.subdivide(
        mesh.vertices,
        mesh.faces
    )

    return Trimesh(
        vertices=vertices,
        faces=faces,
        process=False
    )


def main()->None:
    project_root:Path=(
        Path(__file__)
        .resolve()
        .parents[1]
    )

    dataset_dir:Path=(
        project_root
        /"data"
        /"raw_meshes"
        /"synthetic_s7"
    )

    cases: list[str] = [
        "appendage_long",
        "flat_flap",
        "protrusion_medium"
    ]

    levels:int=2

    print("="*80)
    print("S9 SUBDIVISION ROBUSTNESS")
    print("="*80)

    for case in cases:
        original_path:Path=dataset_dir/f"{case}.obj"

        original:Trimesh=trimesh.load_mesh(
            original_path,
            process=False
        )

        results:list[dict]=[]
        meshes:list[Trimesh]=[
            original
        ]

        current:Trimesh=original

        for _ in range(levels):
            current=subdivide_mesh(
                current
            )
            meshes.append(current)

        with TemporaryDirectory() as temp_dir:
            temp_root:Path=Path(temp_dir)

            for level,mesh in enumerate(meshes):
                output_path:Path=(
                    temp_root
                    /f"{case}_subdiv_{level}.obj"
                )

                mesh.export(
                    output_path
                )

                results.append(
                    analyze_mesh(
                        output_path
                    )
                )

        reference:dict=results[0]

        print()
        print(case)

        for level,result in enumerate(results):
            failures:list[str]=compare_result(
                reference,
                result
            )

            status:str=(
                "PASS"
                if len(failures)==0
                else "FAIL"
            )

            print(
                f" level={level} "
                f"verts={result['vertices']:<7} "
                f"{status:<4} "
                f"decision={result['decision']:<18} "
                f"shape={result['shape_class']:<12} "
                f"conductance={result['conductance']:.6f} "
                f"eigengap={result['fiedler_eigengap']:.8f} "
                f"fraction={result['candidate_fraction']:.6f} "
                f"s8_safe={result.get('s8_safe')} "
                f"safety_reason={result.get('s8_safety_reason')} "
                f"ambiguity={result.get('ambiguity_flags')} "
                f"{failures}"
            )

    print()
    print("="*80)


if __name__=="__main__":
    main()