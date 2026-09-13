from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
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

    cases:list[str]=[
        "appendage_long",
        "appendage_medium",
        "flat_flap",
        "protrusion_medium"
    ]

    transforms:list[tuple[str,np.ndarray]]=[]

    identity:np.ndarray=np.eye(4)
    transforms.append(("identity",identity))

    rot_x:np.ndarray=trimesh.transformations.rotation_matrix(
        np.radians(37.0),
        [1,0,0]
    )
    transforms.append(("rotate_x_37",rot_x))

    rot_axis:np.ndarray=trimesh.transformations.rotation_matrix(
        np.radians(53.0),
        [1,2,3]
    )
    transforms.append(("rotate_axis_53",rot_axis))

    translated:np.ndarray=np.eye(4)
    translated[:3,3]=[100.0,-57.0,23.0]
    transforms.append(("translate",translated))

    combined:np.ndarray=translated@rot_axis
    transforms.append(("rotate_translate",combined))

    print("="*80)
    print("S9 RIGID TRANSFORM ROBUSTNESS")
    print("="*80)

    for case in cases:
        original_path:Path=dataset_dir/f"{case}.obj"

        original:Trimesh=trimesh.load_mesh(
            original_path,
            process=False
        )

        results:dict[str,dict]={}

        with TemporaryDirectory() as temp_dir:
            temp_root:Path=Path(temp_dir)

            for name,matrix in transforms:
                mesh:Trimesh=original.copy()
                mesh.apply_transform(matrix)

                output_path:Path=temp_root/f"{case}_{name}.obj"
                mesh.export(output_path)

                results[name]=analyze_mesh(
                    output_path
                )

        reference:dict=results["identity"]

        print()
        print(case)

        for name,_ in transforms:
            current:dict=results[name]

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
                f" {name:<20} "
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