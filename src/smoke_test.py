from pathlib import Path
from mesh_analyzer import load_as_mesh, analyze_mesh, print_metrics, compute_component_sizes, count_connected_components, count_tiny_components, count_tiny_component_vertices
from mesh_graph import *
def main() -> None:
    #complete cube
    project_root=Path(__file__).resolve().parents[1]
    print("=====================complete cube====================")
    mesh_path1=project_root / "data" / "raw_meshes" / "model.obj"
    mesh1=load_as_mesh(mesh_path1)
    metrics1=analyze_mesh(mesh1)
    print_metrics(metrics1)
    adjacency = build_vertex_adjacency(mesh1)
    degrees = get_degrees(adjacency)
    graph_edges = count_graph_edges(adjacency)
    print("vertex_count:", len(mesh1.vertices))
    print("graph_edges:", graph_edges)
    print("degrees:", degrees)
    component_labels = compute_vertex_component_labels(mesh1)
    print("component_labels:", component_labels)
    #face deficit cube
    print("===================face deficit cube===================")
    mesh_path2=project_root / "data" / "raw_meshes" / "model_face_deficit.obj"
    mesh2=load_as_mesh(mesh_path2)
    metrics2=analyze_mesh(mesh2)
    print_metrics(metrics2)
    adjacency = build_vertex_adjacency(mesh2)
    degrees = get_degrees(adjacency)
    graph_edges = count_graph_edges(adjacency)
    print("vertex_count:", len(mesh2.vertices))
    print("graph_edges:", graph_edges)
    print("degrees:", degrees)
    component_labels = compute_vertex_component_labels(mesh2)
    print("component_labels:", component_labels)
    # face deficit cube
    print("===================degenerate face cube===================")
    mesh_path3 = project_root / "data" / "raw_meshes" / "model_degenerate_face.obj"
    mesh3 = load_as_mesh(mesh_path3)
    metrics3 = analyze_mesh(mesh3)
    print_metrics(metrics3)
    adjacency = build_vertex_adjacency(mesh3)
    degrees = get_degrees(adjacency)
    graph_edges = count_graph_edges(adjacency)
    print("vertex_count:", len(mesh3.vertices))
    print("graph_edges:", graph_edges)
    print("degrees:", degrees)
    component_labels = compute_vertex_component_labels(mesh3)
    print("component_labels:", component_labels)
    print("================nonmanifold edge cube================")
    mesh_path4 = project_root / "data" / "raw_meshes" / "nonmanifold_edge_cube.obj"
    mesh4 = load_as_mesh(mesh_path4)
    metrics4 = analyze_mesh(mesh4)
    print_metrics(metrics4)
    adjacency = build_vertex_adjacency(mesh4)
    degrees = get_degrees(adjacency)
    graph_edges = count_graph_edges(adjacency)
    print("vertex_count:", len(mesh4.vertices))
    print("graph_edges:", graph_edges)
    print("degrees:", degrees)
    component_labels = compute_vertex_component_labels(mesh4)
    print("component_labels:", component_labels)
if __name__ == "__main__":
    main()