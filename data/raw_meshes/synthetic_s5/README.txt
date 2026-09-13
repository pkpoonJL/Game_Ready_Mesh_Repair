S5/S6 Synthetic Mesh Set
========================

Purpose: controlled experiments for the current unweighted vertex-adjacency spectral pipeline.

Important: changing only bridge coordinates while keeping exactly the same graph topology would not change the current graph Laplacian, eigenvalues, or conductance. Thin/medium/thick therefore use different voxel cross-sections, so graph connectivity changes too.

Files:
- baseline_cube.obj
  voxels=512, vertices=386, triangular_faces=768
  Baseline 8x8x8 cube; no intended weak bridge.
- bridge_thin.obj
  voxels=1032, vertices=800, triangular_faces=1596
  Two 8x8x8 bodies connected by an 8-long 1x1 bridge.
- bridge_medium.obj
  voxels=1056, vertices=826, triangular_faces=1648
  Two 8x8x8 bodies connected by an 8-long 2x2 bridge.
- bridge_thick.obj
  voxels=1152, vertices=866, triangular_faces=1728
  Two 8x8x8 bodies connected by an 8-long 4x4 bridge.
- small_protrusion.obj
  voxels=1031, vertices=670, triangular_faces=1336
  Large 10x10x10 body with a 1x1 neck leading to a small 3x3x3 blob; defect-like positive case.
- legitimate_thin_appendage.obj
  voxels=1010, vertices=642, triangular_faces=1280
  Large 10x10x10 body with a long 1x1 bar; intended hard-negative case for spectral-only detection.

Suggested S5 outputs: component size, Fiedler value, best conductance, cut edge count, partition sizes, and visual cut location.

Primary controlled comparison: bridge_thin.obj -> bridge_medium.obj -> bridge_thick.obj
