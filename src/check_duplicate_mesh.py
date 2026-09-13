from pathlib import Path

import numpy as np
import trimesh


project_root: Path = Path(__file__).resolve().parents[1]

dataset_dir: Path = (
    project_root
    / "data"
    / "raw_meshes"
    / "synthetic_s7"
)

mesh_a = trimesh.load_mesh(
    dataset_dir / "legitimate_knob.obj",
    process=False
)

mesh_b = trimesh.load_mesh(
    dataset_dir / "protrusion_medium.obj",
    process=False
)

print(
    "Vertices identical:",
    np.array_equal(
        mesh_a.vertices,
        mesh_b.vertices
    )
)

print(
    "Faces identical:",
    np.array_equal(
        mesh_a.faces,
        mesh_b.faces
    )
)