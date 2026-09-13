from pathlib import Path

from stage7_dataset_test import analyze_mesh


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
        "baseline_cube",
        "appendage_long",
        "legitimate_compact_boss",
        "protrusion_medium"
    ]

    repeats:int=20

    print("="*80)
    print("S9 REPEATABILITY TEST")
    print("="*80)

    for case in cases:
        mesh_path:Path=dataset_dir/f"{case}.obj"

        decisions:set[str]=set()
        shapes:set[str]=set()
        s8_states:set[str]=set()

        fiedler_values:list[float]=[]
        conductance_values:list[float]=[]

        for _ in range(repeats):
            result:dict=analyze_mesh(
                mesh_path
            )

            decisions.add(
                result["decision"]
            )

            shapes.add(
                result["shape_class"]
            )

            s8_states.add(
                str(result.get("s8_safe"))
            )

            fiedler_values.append(
                result["fiedler"]
            )

            conductance_values.append(
                result["conductance"]
            )

        stable:bool=(
            len(decisions)==1
            and len(s8_states)==1
        )

        print()
        print(case)
        print(
            " status:",
            "PASS" if stable else "FAIL"
        )
        print(
            " decisions:",
            decisions
        )
        print(
            " shapes:",
            shapes
        )
        print(
            " s8_safe:",
            s8_states
        )
        print(
            " fiedler range:",
            min(fiedler_values),
            "->",
            max(fiedler_values)
        )
        print(
            " conductance range:",
            min(conductance_values),
            "->",
            max(conductance_values)
        )

    print()
    print("="*80)


if __name__=="__main__":
    main()