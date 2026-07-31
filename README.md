# Game-Ready Mesh Repair

This project studies structural defects in 3D character meshes, especially meshes that may look visually valid but are not directly ready for game or animation pipelines.

The long-term goal is to build a pipeline for detecting, evaluating, and eventually repairing mesh defects that affect downstream usability, including game engine import, rigging, and animation.

At the current stage, the project focuses on a lightweight mesh analyzer for detecting basic topology and geometry defects in triangular meshes.

---

## Motivation

Modern 3D generation tools can produce visually plausible assets, but visual plausibility does not guarantee that a mesh is game-ready.

A generated or manually created mesh may contain hidden structural problems such as:

- open boundaries or holes
- non-manifold edges
- degenerate faces
- disconnected floating components
- tiny mesh fragments

These issues may not be obvious in preview renders, but they can affect downstream tasks such as mesh cleanup, rigging, animation, and importing assets into game engines.

This project aims to bridge the gap between visually plausible 3D assets and structurally reliable game-ready assets.

---

## Current Features

The current analyzer supports the following metrics:

### 1. Boundary edge count

A boundary edge is an edge used by exactly one triangular face.

This usually indicates an open boundary or a hole in the mesh.

### 2. Non-manifold edge count

A non-manifold edge is an edge used by more than two triangular faces.

This is problematic because a normal surface mesh should locally behave like a 2D manifold, where each interior edge is shared by exactly two faces.

### 3. Degenerate face count

A degenerate face is a triangular face with zero or near-zero area.

This can happen when:

- two vertices overlap
- three vertices are collinear
- the triangle is extremely thin

### 4. Connected component analysis

The mesh is treated as an undirected graph:

- each vertex is a graph node
- each triangle edge is a graph edge

The analyzer computes:

- the number of connected components
- the size of each connected component

This helps detect isolated floating components or disconnected mesh fragments.

---

## Project Structure

```text
Game_Ready_Mesh_Repair/
├── data/
│   └── raw_meshes/
│       ├── model.obj
│       ├── model_face_deficit.obj
│       ├── model_degenerate_face.obj
│       └── nonmanifold_edge_cube.obj
│
├── src/
│   ├── mesh_analyzer.py
│   └── smoke_test.py
│
├── Outputs/
│   └── Screenshot/
│       ├── complete_cube_wireframe.png
│       ├── face_deficit_cube_hole.png
│       ├── degenerate_face_line.png
│       └── nonmanifold_edge.png
│
├── Notes/
│   ├── problem_statement.md
│   └── weekly_log.md
│
├── requirements.txt
├── .gitignore
└── README.md