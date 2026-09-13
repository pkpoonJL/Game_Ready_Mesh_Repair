# S7 Controlled Synthetic Dataset

This dataset is for **Stage 7 decision logic**, after S5 spectral localization and S6 geometry validation.

The goal is **not** to hard-code a threshold from two easy examples. The dataset deliberately contains both clean controls and adversarial cases so that a proposed S7 rule can fail in an informative way.

## Cases

| Mesh | Semantic label | Geometry role | Why it is here |
|---|---|---|---|
| `baseline_cube.obj` | legitimate | baseline | A normal connected body. S5 will still have a mathematically best cut, so this checks that “best cut” is not automatically treated as a defect. |
| `protrusion_small.obj` | defect-like | compact protrusion | Small bulb attached by a narrow neck. |
| `protrusion_medium.obj` | defect-like | compact protrusion | Same neck, larger bulb. |
| `protrusion_large.obj` | defect-like | compact protrusion | Same neck, still larger bulb. |
| `appendage_short.obj` | legitimate | thin rod | Legitimate elongated appendage. |
| `appendage_medium.obj` | legitimate | thin rod | Same family with larger length. |
| `appendage_long.obj` | legitimate | thin rod | Same family with still larger length. |
| `flat_flap.obj` | legitimate | thin sheet | Tests whether S6 can distinguish sheet-like from blob-like geometry rather than only “thin vs thick.” |
| `defect_spike.obj` | defect-like | adversarial elongated defect | Intentionally breaks the naive rule “rod-like => legitimate.” |
| `legitimate_knob.obj` | legitimate | adversarial compact feature | Intentionally breaks the naive rule “compact + narrow neck => defect.” |

## Intended S7 workflow

Run every mesh through the existing pipeline:

```text
OBJ
 -> adjacency / components
 -> S5 spectral localization
 -> smaller S5 partition
 -> S6 principal variances + ratios
 -> collect evidence table
 -> inspect separation and failure cases
 -> only then define S7 decision logic
```

Useful fields to record per case:

```text
fiedler_value
conductance
cut_edge_count
partition_size_1
partition_size_2
smaller_partition_fraction
lambda_1, lambda_2, lambda_3
lambda_2 / lambda_1
lambda_3 / lambda_1
semantic_label
```

Do **not** assume a weighted score such as `0.4 * conductance + 0.3 * ratio_2 + ...` before looking at the controlled results.

## Important interpretation

The two adversarial meshes are intentional.

- A `defect_spike` can be elongated.
- A `legitimate_knob` can be compact and weakly attached.

Therefore geometry alone cannot recover **semantic intent** in every case. A conservative S7 should be allowed to output `manual_review` rather than pretending every geometry is automatically decidable.

## Reproducibility

`generate_s7_synthetic.py` recreates all OBJ files deterministically. The meshes are voxel-surface meshes, triangulated with shared vertices, so the graph topology is explicit and reproducible without requiring a Boolean-mesh engine.
