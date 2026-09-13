from pathlib import Path
from stage7_decision import classify_stage7
import trimesh
from trimesh import Trimesh
from stage8_repair import (
    evaluate_repair_safety,
    repair_candidate_region,
    validate_repaired_mesh
)
from mesh_graph import build_vertex_adjacency
from mesh_spectral_pipeline import analyze_mesh_components
from geometry_validation import analyze_partition_geometry


def select_smaller_partition(
    component_result: dict,
    adjacency: list[set[int]]
) -> set[int]:

    partition_1: set[int] = component_result["partition_1"]
    partition_2: set[int] = component_result["partition_2"]

    volume_1: int = 0
    volume_2: int = 0

    for vertex in partition_1:
        volume_1 += len(adjacency[vertex])

    for vertex in partition_2:
        volume_2 += len(adjacency[vertex])

    if volume_1 <= volume_2:
        return partition_1

    return partition_2


def analyze_mesh(
    mesh_path: Path
) -> dict:

    mesh: Trimesh = trimesh.load_mesh(
        mesh_path,
        process=False
    )

    adjacency: list[set[int]] = build_vertex_adjacency(
        mesh
    )

    spectral_results: list[dict] = analyze_mesh_components(
        adjacency
    )

    analyzed_results: list[dict] = []

    for component_result in spectral_results:

        if component_result["status"] == "analyzed":
            analyzed_results.append(
                component_result
            )

    if len(analyzed_results) == 0:
        raise RuntimeError(
            f"No analyzable component found in {mesh_path.name}"
        )

    main_component: dict = max(
        analyzed_results,
        key=lambda result: result["component_size"]
    )

    smaller_partition: set[int] = select_smaller_partition(
        main_component,
        adjacency
    )

    candidate_fraction: float = (
            len(smaller_partition)
            / main_component["component_size"]
    )

    geometry_result: dict = analyze_partition_geometry(
        mesh,
        smaller_partition
    )

    stage7_result: dict = classify_stage7(
        main_component,
        geometry_result,
        candidate_fraction
    )
    safety_result: dict | None = None
    validation_result: dict | None = None

    if stage7_result["decision"] == "repair_candidate":
        safety_result = evaluate_repair_safety(
            mesh,
            smaller_partition,
            main_component
        )

        if safety_result["safe_to_attempt"]:
            repaired_mesh: Trimesh | None = repair_candidate_region(
                mesh,
                smaller_partition,
                safety_result
            )

            if repaired_mesh is not None:
                validation_result = validate_repaired_mesh(
                    repaired_mesh
                )
    principal_variances = geometry_result[
        "principal_variances"
    ]

    principal_variance_ratios = geometry_result[
        "principal_variance_ratios"
    ]

    result: dict = {
        "mesh":
            mesh_path.stem,

        "vertices":
            len(mesh.vertices),

        "fiedler":
            main_component["fiedler_value"],

        "conductance":
            main_component["best_conductance"],

        "cut_edges":
            len(main_component["cut_edges"]),

        "small_partition":
            len(smaller_partition),

        "candidate_fraction":
            candidate_fraction,

        "lambda_1":
            float(principal_variances[0]),

        "lambda_2":
            float(principal_variances[1]),

        "lambda_3":
            float(principal_variances[2]),

        "ratio_2":
            float(principal_variance_ratios[0]),

        "ratio_3":
            float(principal_variance_ratios[1]),

        "fiedler_eigengap":
            main_component["fiedler_eigengap"],

        "decision": stage7_result["decision"],
        "shape_class": stage7_result["shape_class"],
        "ambiguity_flags": stage7_result["ambiguity_flags"],
        "reason_codes": stage7_result["reason_codes"],
        "s8_safe":
            None if safety_result is None
            else safety_result["safe_to_attempt"],

        "s8_safety_reason":
            [] if safety_result is None
            else safety_result["reason_codes"],

        "s8_valid":
            None if validation_result is None
            else validation_result["valid"],

        "s8_validation_reason":
            [] if validation_result is None
            else validation_result["reason_codes"],
    }

    return result


def main() -> None:

    project_root: Path = (
        Path(__file__)
        .resolve()
        .parents[1]
    )

    dataset_dir: Path = (
        project_root
        / "data"
        / "raw_meshes"
        / "synthetic_s7"
    )

    mesh_paths: list[Path] = sorted(
        dataset_dir.glob("*.obj")
    )

    if len(mesh_paths) == 0:
        raise RuntimeError(
            f"No OBJ files found in {dataset_dir}"
        )

    results: list[dict] = []

    for mesh_path in mesh_paths:

        print(
            f"Running: {mesh_path.name}"
        )

        result: dict = analyze_mesh(
            mesh_path
        )
        print(
            "S7:",
            result["decision"],
            "| S8 safe:",
            result["s8_safe"],
            "| S8 valid:",
            result["s8_valid"],
            "| safety reason:",
            result["s8_safety_reason"],
            "| validation reason:",
            result["s8_validation_reason"]
        )
        results.append(
            result
        )

    print()

    print("=" * 170)

    header: str = (
        f"{'Mesh':<28}"
        f"{'Verts':>8}"
        f"{'Fiedler':>15}"
        f"{'Conductance':>15}"
        f"{'Cut':>8}"
        f"{'Small':>10}"
        f"{'Fraction':>12}"
        f"{'lambda1':>15}"
        f"{'lambda2':>15}"
        f"{'lambda3':>15}"
        f"{'r2':>15}"
        f"{'r3':>15}"
        f"{'Eigengap':>14}"
    )

    print(
        header
    )

    print("-" * 170)

    for result in results:
        print(
            f"{result['mesh']:<28}"
            f"{result['vertices']:>8}"
            f"{result['fiedler']:>15.8f}"
            f"{result['conductance']:>15.8f}"
            f"{result['cut_edges']:>8}"
            f"{result['small_partition']:>10}"
            f"{result['candidate_fraction']:>12.6f}"
            f"{result['lambda_1']:>15.8f}"
            f"{result['lambda_2']:>15.8f}"
            f"{result['lambda_3']:>15.8f}"
            f"{result['ratio_2']:>15.8f}"
            f"{result['ratio_3']:>15.8f}"
            f"{result['fiedler_eigengap']:>14.8f}"
            f"{result['decision']:>20}"
            f"{result['shape_class']:>15}"
            f"{','.join(result['ambiguity_flags']):>25}"
        )

    print("=" * 170)


if __name__ == "__main__":
    main()