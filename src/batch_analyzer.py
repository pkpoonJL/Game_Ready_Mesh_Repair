from pathlib import Path
import csv
import trimesh
from mesh_analyzer import load_as_mesh, analyze_mesh, MeshMetrics
def component_sizes_to_string(component_sizes: list[int])->str:
    output:str=""
    n:int = len(component_sizes)
    for index in range(n):
        output+=str(component_sizes[index])
        if index<n-1:
            output+=";"
    return output
def analyze_one_mesh(mesh_path: Path) -> dict[str, str | int]:
    mesh = load_as_mesh(mesh_path)
    metrics: MeshMetrics = analyze_mesh(mesh)
    vertex_count: int = len(mesh.vertices)
    face_count: int = len(mesh.faces)
    (boundary_edges,nonmanifold_edges,degenerate_faces,component_sizes,connected_components,tiny_components,tiny_component_vertices,quality_flag)=metrics
    row: dict[str, str | int] = {
        "filename": mesh_path.name,
        "vertex_count": vertex_count,
        "face_count": face_count,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "degenerate_faces": degenerate_faces,
        "component_sizes": component_sizes_to_string(component_sizes),
        "connected_components": connected_components,
        "tiny_components": tiny_components,
        "tiny_component_vertices": tiny_component_vertices,
        "quality_flag": quality_flag,
    }
    return row
def write_csv_report(mesh_folder:Path,output_csv_path: Path)->None:
    fieldnames: list[str] = [
        "filename",
        "vertex_count",
        "face_count",
        "boundary_edges",
        "nonmanifold_edges",
        "degenerate_faces",
        "component_sizes",
        "connected_components",
        "tiny_components",
        "tiny_component_vertices",
        "quality_flag",
    ]
    rows:list[dict[str,str|int]]=[]
    for mesh_path in mesh_folder.glob("*.obj"):
        row = analyze_one_mesh(mesh_path)
        rows.append(row)
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer=csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
def main() -> None:
        project_root: Path=Path(__file__).resolve().parents[1]
        mesh_folder: Path=project_root / "data" / "raw_meshes"
        output_csv_path: Path=project_root / "Outputs" / "mesh_report.csv"
        write_csv_report(mesh_folder, output_csv_path)
        print("CSV report written to:", output_csv_path)
if __name__ == "__main__":
        main()