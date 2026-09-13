from pathlib import Path
import json


Voxel = tuple[int, int, int]
Vertex = tuple[float, float, float]
Face = tuple[int, int, int]


FACE_DEFINITIONS: list[
    tuple[tuple[int, int, int], list[tuple[int, int, int]]]
] = [
    ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),
    ((1, 0, 0), [(1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)]),
    ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),
    ((0, 1, 0), [(0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)]),
    ((0, 0, -1), [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)]),
    ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),
]


def make_box_voxels(
    x_start: int,
    x_end: int,
    y_start: int,
    y_end: int,
    z_start: int,
    z_end: int,
) -> set[Voxel]:
    result: set[Voxel] = set()
    for x in range(x_start, x_end):
        for y in range(y_start, y_end):
            for z in range(z_start, z_end):
                result.add((x, y, z))
    return result


def build_surface_mesh(
    voxels: set[Voxel],
) -> tuple[list[Vertex], list[Face]]:
    vertex_to_index: dict[tuple[int, int, int], int] = {}
    vertices: list[Vertex] = []
    faces: list[Face] = []

    def get_vertex_index(vertex: tuple[int, int, int]) -> int:
        if vertex not in vertex_to_index:
            vertex_to_index[vertex] = len(vertices)
            vertices.append(
                (float(vertex[0]), float(vertex[1]), float(vertex[2]))
            )
        return vertex_to_index[vertex]

    for voxel in sorted(voxels):
        x: int = voxel[0]
        y: int = voxel[1]
        z: int = voxel[2]

        for normal, corners in FACE_DEFINITIONS:
            dx: int = normal[0]
            dy: int = normal[1]
            dz: int = normal[2]

            neighbor: Voxel = (x + dx, y + dy, z + dz)
            if neighbor in voxels:
                continue

            quad: list[int] = []
            for corner in corners:
                cx: int = corner[0]
                cy: int = corner[1]
                cz: int = corner[2]
                quad.append(
                    get_vertex_index((x + cx, y + cy, z + cz))
                )

            faces.append((quad[0], quad[1], quad[2]))
            faces.append((quad[0], quad[2], quad[3]))

    return vertices, faces


def write_obj(
    path: Path,
    vertices: list[Vertex],
    faces: list[Face],
) -> None:
    with path.open("w", encoding="utf-8") as file:
        file.write("# S7 controlled synthetic mesh\n")
        for vertex in vertices:
            file.write(
                f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n"
            )
        for face in faces:
            file.write(
                f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n"
            )


def build_case(case_name: str) -> set[Voxel]:
    # Shared 12 x 12 x 12 body. Keeping the body identical makes the
    # controlled comparisons easier to interpret.
    voxels: set[Voxel] = make_box_voxels(0, 12, 0, 12, 0, 12)

    if case_name == "baseline_cube":
        return voxels

    if case_name.startswith("protrusion_"):
        size_map: dict[str, int] = {
            "protrusion_small": 4,
            "protrusion_medium": 6,
            "protrusion_large": 8,
        }
        bulb_size: int = size_map[case_name]

        # Narrow neck followed by a compact block-like bulb.
        voxels |= make_box_voxels(12, 15, 5, 7, 5, 7)
        y_start: int = 6 - bulb_size // 2
        z_start: int = 6 - bulb_size // 2
        voxels |= make_box_voxels(
            15,
            15 + bulb_size,
            y_start,
            y_start + bulb_size,
            z_start,
            z_start + bulb_size,
        )
        return voxels

    if case_name.startswith("appendage_"):
        length_map: dict[str, int] = {
            "appendage_short": 10,
            "appendage_medium": 14,
            "appendage_long": 18,
        }
        appendage_length: int = length_map[case_name]

        # A one-voxel cross-section rod. This is intentionally very
        # anisotropic so S6 should identify a rod-like partition.
        voxels |= make_box_voxels(
            12,
            12 + appendage_length,
            6,
            7,
            6,
            7,
        )
        return voxels

    if case_name == "flat_flap":
        # Narrow stem followed by a broad, one-voxel-thick plate.
        voxels |= make_box_voxels(12, 15, 5, 7, 5, 7)
        voxels |= make_box_voxels(15, 24, 2, 10, 5, 6)
        return voxels

    if case_name == "defect_spike":
        # Deliberately adversarial: semantically marked defect-like,
        # but geometrically elongated. A PCA-only rule should not be
        # trusted to classify this automatically.
        voxels |= make_box_voxels(12, 15, 6, 7, 6, 7)
        voxels |= make_box_voxels(15, 18, 4, 8, 4, 8)
        voxels |= make_box_voxels(18, 22, 5, 7, 5, 7)
        voxels |= make_box_voxels(22, 27, 6, 7, 6, 7)
        return voxels

    if case_name == "legitimate_knob":
        # Deliberately adversarial: semantically legitimate, but its
        # compact bulb + narrow neck resembles a defect protrusion.
        voxels |= make_box_voxels(12, 15, 5, 7, 5, 7)
        voxels |= make_box_voxels(15, 21, 3, 9, 3, 9)
        return voxels
    if case_name == "legitimate_compact_boss":
        # Legitimate compact feature with a broad attachment and gradual taper.
        # Unlike the narrow-neck bulb cases, this boss blends into the main body.
        voxels |= make_box_voxels(12, 14, 3, 9, 3, 9)
        voxels |= make_box_voxels(14, 16, 4, 8, 4, 8)
        voxels |= make_box_voxels(16, 18, 5, 7, 5, 7)
        return voxels
    raise ValueError(f"Unknown case: {case_name}")


def main() -> None:
    output_root: Path = Path(__file__).resolve().parent
    mesh_root: Path = output_root
    mesh_root.mkdir(parents=True, exist_ok=True)

    cases: list[dict] = [
        {
            "name": "baseline_cube",
            "semantic_label": "legitimate",
            "shape_family": "baseline",
            "purpose": "Negative control: S5 still has a best cut, but there is no attached defect.",
        },
        {
            "name": "protrusion_small",
            "semantic_label": "defect_like",
            "shape_family": "compact_protrusion",
            "purpose": "Small compact bulb attached through a narrow neck.",
        },
        {
            "name": "protrusion_medium",
            "semantic_label": "defect_like",
            "shape_family": "compact_protrusion",
            "purpose": "Medium compact bulb with the same neck geometry.",
        },
        {
            "name": "protrusion_large",
            "semantic_label": "defect_like",
            "shape_family": "compact_protrusion",
            "purpose": "Large compact bulb with the same neck geometry.",
        },
        {
            "name": "appendage_short",
            "semantic_label": "legitimate",
            "shape_family": "thin_rod",
            "purpose": "Short legitimate rod-like appendage.",
        },
        {
            "name": "appendage_medium",
            "semantic_label": "legitimate",
            "shape_family": "thin_rod",
            "purpose": "Medium legitimate rod-like appendage.",
        },
        {
            "name": "appendage_long",
            "semantic_label": "legitimate",
            "shape_family": "thin_rod",
            "purpose": "Long legitimate rod-like appendage.",
        },
        {
            "name": "flat_flap",
            "semantic_label": "legitimate",
            "shape_family": "thin_sheet",
            "purpose": "Legitimate sheet-like appendage; tests rod-vs-sheet geometry handling.",
        },
        {
            "name": "defect_spike",
            "semantic_label": "defect_like",
            "shape_family": "elongated_adversarial",
            "purpose": "Failure case for any rule that assumes elongated means legitimate.",
        },
        {
            "name": "legitimate_knob",
            "semantic_label": "legitimate",
            "shape_family": "compact_adversarial",
            "purpose": "Failure case for any rule that assumes compact + weak neck means defect.",
        },
        {
            "name": "legitimate_compact_boss",
            "semantic_label": "legitimate",
            "shape_family": "compact_broad_base",
            "purpose": (
                "Legitimate compact broad-base feature; tests whether attachment "
                "constriction distinguishes blended compact geometry from a "
                "narrow-neck compact protrusion."
            ),
        },
    ]

    for case in cases:
        case_name: str = case["name"]
        voxels: set[Voxel] = build_case(case_name)
        vertices, faces = build_surface_mesh(voxels)
        write_obj(mesh_root / f"{case_name}.obj", vertices, faces)
        case["vertex_count"] = len(vertices)
        case["face_count"] = len(faces)

    manifest: dict = {
        "dataset": "S7 controlled synthetic decision dataset",
        "design": (
            "Controlled geometry for deriving and breaking interpretable S7 rules. "
            "Semantic labels are intentional experimental labels, not thresholds."
        ),
        "cases": cases,
    }

    with (output_root / "manifest.json").open("w", encoding="utf-8") as file:
        json.dump(manifest, file, indent=2)


if __name__ == "__main__":
    main()
