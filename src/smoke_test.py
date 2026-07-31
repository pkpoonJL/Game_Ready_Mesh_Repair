from pathlib import Path
from mesh_analyzer import load_as_mesh, analyze_mesh, print_metrics, compute_component_sizes, count_connected_components, count_tiny_components, count_tiny_component_vertices
def main() -> None:
    #complete cube
    project_root=Path(__file__).resolve().parents[1]
    print("=====================complete cube====================")
    mesh_path1=project_root / "data" / "raw_meshes" / "model.obj"
    mesh1=load_as_mesh(mesh_path1)
    metrics1=analyze_mesh(mesh1)
    print_metrics(metrics1)
    print("component_sizes:", compute_component_sizes(mesh1))
    print("connected_components:", count_connected_components(mesh1))
    component_sizes = compute_component_sizes(mesh1)
    print("tiny_components:", count_tiny_components(component_sizes, min_vertices=4))
    print("tiny_component_vertices:", count_tiny_component_vertices(component_sizes, min_vertices=4))
    #face deficit cube
    print("===================face deficit cube===================")
    mesh_path2=project_root / "data" / "raw_meshes" / "model_face_deficit.obj"
    mesh2=load_as_mesh(mesh_path2)
    metrics2=analyze_mesh(mesh2)
    print_metrics(metrics2)
    print("component_sizes:", compute_component_sizes(mesh2))
    print("connected_components:", count_connected_components(mesh2))
    component_sizes = compute_component_sizes(mesh2)
    print("tiny_components:", count_tiny_components(component_sizes, min_vertices=4))
    print("tiny_component_vertices:", count_tiny_component_vertices(component_sizes, min_vertices=4))
    # face deficit cube
    print("===================degenerate face cube===================")
    mesh_path3 = project_root / "data" / "raw_meshes" / "model_degenerate_face.obj"
    mesh3 = load_as_mesh(mesh_path3)
    metrics3 = analyze_mesh(mesh3)
    print_metrics(metrics3)
    print("component_sizes:", compute_component_sizes(mesh3))
    print("connected_components:", count_connected_components(mesh3))
    component_sizes = compute_component_sizes(mesh3)
    print("tiny_components:", count_tiny_components(component_sizes, min_vertices=4))
    print("tiny_component_vertices:", count_tiny_component_vertices(component_sizes, min_vertices=4))
    print("================nonmanifold edge cube================")
    mesh_path4 = project_root / "data" / "raw_meshes" / "nonmanifold_edge_cube.obj"
    mesh4 = load_as_mesh(mesh_path4)
    metrics4 = analyze_mesh(mesh4)
    print_metrics(metrics4)
    print("component_sizes:", compute_component_sizes(mesh4))
    print("connected_components:", count_connected_components(mesh4))
    component_sizes = compute_component_sizes(mesh4)
    print("tiny_components:", count_tiny_components(component_sizes, min_vertices=4))
    print("tiny_component_vertices:", count_tiny_component_vertices(component_sizes, min_vertices=4))
if __name__ == "__main__":
    main()