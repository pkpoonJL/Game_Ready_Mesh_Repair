from pathlib import Path
from tempfile import TemporaryDirectory
import math
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

    if not math.isclose(
        reference["candidate_fraction"],
        current["candidate_fraction"],
        rel_tol=1e-6,
        abs_tol=1e-9
    ):
        failures.append("candidate_fraction_changed")

    if not math.isclose(
        reference["conductance"],
        current["conductance"],
        rel_tol=1e-6,
        abs_tol=1e-9
    ):
        failures.append("conductance_changed")

    return failures


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
        "appendage_long"
    ]

    scales: list[float] = [
        1e-6,
        1e-4,
        1e-2,
        1.0,
        1e2,
        1e4,
        1e6
    ]

    print("="*80)
    print("S9 SCALE ROBUSTNESS")
    print("="*80)

    for case in cases:
        original_path:Path=dataset_dir/f"{case}.obj"

        mesh:Trimesh=trimesh.load_mesh(
            original_path,
            process=False
        )

        results:dict[float,dict]={}

        with TemporaryDirectory() as temp_dir:
            temp_root:Path=Path(temp_dir)

            for scale in scales:
                scaled:Trimesh=mesh.copy()
                scaled.vertices=scaled.vertices*scale

                output_path:Path=(
                    temp_root
                    /f"{case}_{scale}.obj"
                )

                scaled.export(output_path)

                results[scale]=analyze_mesh(
                    output_path
                )

        reference:dict=results[1.0]

        print()
        print(case)

        for scale in scales:
            current:dict=results[scale]

            failures:list[str]=compare_result(
                reference,
                current
            )

            status:str=(
                "PASS"
                if len(failures)==0
                else "FAIL"
            )

            print(
                f" scale={scale:<5} "
                f"{status:<4} "
                f"decision={current['decision']:<18} "
                f"shape={current['shape_class']:<12} "
                f"s8_safe={current.get('s8_safe')} "
                f"{failures}"
            )

    print()
    print("="*80)


if __name__=="__main__":
    main()