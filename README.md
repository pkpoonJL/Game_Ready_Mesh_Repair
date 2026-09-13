# Game-Ready Mesh Repair

A conservative mesh-diagnostics and repair pipeline based on **spectral graph analysis** and **geometry-aware validation**.

> **Detect aggressively, repair conservatively.**

Version: **V1 — Spectral Safe Repair**

---

## Overview

The project investigates whether structural defects or suspicious attachments in triangle meshes can be detected through graph spectral analysis and repaired safely using geometric constraints.

The V1 pipeline does **not** treat every spectral bottleneck as a defect.

Instead, it separates the problem into:

```text
structural detection
        ↓
geometric characterization
        ↓
interpretable decision
        ↓
conservative safety validation
        ↓
optional repair
```

The core idea is that:

> A mesh region can be structurally separable without being semantically wrong.

---

## Pipeline

```text
Input Mesh
    ↓
S1  Mesh Graph / Connected Components
    ↓
S2  Symmetric Normalized Graph Laplacian
    ↓
S3  Eigen-analysis / Fiedler Vector
    ↓
S4  Sweep Cut / Conductance
    ↓
S5  Structural Localization
    ↓
S6  PCA Geometry Characterization
    ↓
S7  Interpretable Decision
    ↓
S8  Conservative Repair + Validation
    ↓
S9  Evaluation / Robustness Testing
```

All stages S1–S9 are complete for V1.

---

## Spectral Detection

The mesh is converted into an unweighted vertex-adjacency graph.

V1 uses the symmetric normalized graph Laplacian:

$$
L_{\mathrm{sym}}
=
I-D^{-1/2}AD^{-1/2}
$$

The Fiedler vector is used to generate sweep cuts.

For a candidate partition $S$:

$$
\phi(S)
=
\frac{|E(S,\bar S)|}
{\min(\operatorname{vol}(S),\operatorname{vol}(\bar S))}
$$

Low conductance indicates a graph bottleneck.

It does **not** by itself imply a defect.

---

## Geometry Characterization

Localized candidate regions are characterized using PCA.

For centered candidate vertices $q_i$:

$$
C=
\frac{1}{n}
\sum_i q_iq_i^T
$$

with covariance eigenvalues

$$
\lambda_1\ge\lambda_2\ge\lambda_3
$$

and normalized ratios

$$
r_2=\frac{\lambda_2}{\lambda_1},
\qquad
r_3=\frac{\lambda_3}{\lambda_1}.
$$

V1 uses these ratios to describe candidates as:

```text
rod
sheet
compact
intermediate
```

These labels describe geometry only; they do not infer semantic intent.

---

## Decision Layer

S7 outputs one of:

```text
keep
repair_candidate
manual_review
```

`repair_candidate` means that the region is a sufficiently clear localized weak attachment to be passed to the repair-safety stage.

It does **not** mean that the region is definitely unwanted.

A controlled experiment contains two byte-identical geometries with different semantic labels, demonstrating that:

> **Geometry alone cannot recover design intent.**

---

## Conservative Repair

V1 only performs automatic repair when strict safety checks pass.

Current conditions include:

```text
single closed repair boundary
localized candidate region
stable spectral evidence
planar boundary
nondegenerate boundary
convex boundary
```

The supported repair primitive is:

```text
remove candidate region
        ↓
extract exposed boundary
        ↓
order boundary loop
        ↓
insert centroid
        ↓
fan triangulation
        ↓
validate repaired mesh
```

Unsafe or unsupported cases are deliberately refused instead of being force-repaired.

---

## V1 Evaluation

The controlled V1 dataset currently contains:

```text
11 test cases
10 unique geometries
```

### S7 Results

```text
keep              2
manual_review     2
repair_candidate  7
```

### S8 Results

```text
safety passed     1
safety refused    6

valid repairs     1
invalid repairs   0
```

The single repair attempted under the current conservative safety gate passed all post-repair validation checks.

This should not be interpreted as a general 100% repair success rate.

---

## Robustness Results

### Coordinate Scaling

Tested uniform coordinate scales:

```text
1e-6
1e-4
1e-2
1
1e2
1e4
1e6
```

Final result:

```text
7 / 7 PASS
```

Stress testing exposed several absolute-tolerance bugs, which were replaced with normalized, dimensionless geometric criteria.

---

### Repeatability

```text
4 representative meshes
× 20 repeated runs
= 80 runs
```

Result:

```text
80 / 80 decision stable
80 / 80 S8 safety stable
```

---

### Rigid Transformations

Tested:

```text
identity
rotation
arbitrary-axis rotation
translation
rotation + translation
```

Result:

```text
4 meshes × 5 transforms
20 / 20 PASS
```

---

### Boundary Perturbation

Controlled out-of-plane perturbation of a repair boundary produced the expected transition at the current planarity threshold:

$$
r_3 < 0.01
$$

Small perturbations remained repairable, while sufficiently non-planar boundaries were safely rejected.

---

## Known V1 Limitation: Tessellation Dependence

Uniform subdivision preserves the continuous surface but changes the graph discretization.

Candidate geometry remained stable:

```text
rod     → rod     → rod
sheet   → sheet   → sheet
compact → compact → compact
```

but spectral quantities changed significantly.

For example:

```text
appendage_long

conductance:
0.018779
0.009423
0.004691

eigengap:
0.005315
0.001333
0.000334
```

Therefore:

> **The current unweighted graph spectral quantities are mesh-resolution dependent.**

The current absolute spectral thresholds are not tessellation invariant.

This is intentionally documented as a V1 limitation rather than hidden by threshold tuning.

---

## Performance Limitation

The current sweep-cut implementation materializes sweep candidates and recomputes conductance for each candidate.

This becomes slow on densely subdivided meshes.

A future implementation should incrementally maintain graph volume and cut size along the Fiedler ordering.

---

## Repository Structure

```text
Game_Ready_Mesh_Repair/
│
├── data/
│   └── raw_meshes/
│       ├── synthetic_s5/
│       ├── synthetic_s7/
│       └── two_cubes_thin_bridge.obj
│
├── src/
│   ├── mesh_analyzer.py
│   ├── spectral_analysis.py
│   ├── spectral_eigen_analysis.py
│   ├── spectral_sweep_analysis.py
│   ├── mesh_spectral_pipeline.py
│   ├── geometry_validation.py
│   ├── stage7_decision.py
│   ├── stage7_dataset_test.py
│   ├── stage8_repair.py
│   ├── stage9_evaluation.py
│   ├── stage9_scale_test.py
│   ├── stage9_boundary_perturbation_test.py
│   ├── stage9_repeatability_test.py
│   ├── stage9_transform_test.py
│   └── stage9_subdivision_test.py
│
├── requirements.txt
├── Game_Ready_Mesh_Repair_V1_Summary.md
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/pkpoonJL/Game_Ready_Mesh_Repair.git
cd Game_Ready_Mesh_Repair
```

Create a virtual environment:

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the V1 Evaluation

Run the baseline S9 evaluation:

```bash
python src/stage9_evaluation.py
```

Additional robustness tests:

```bash
python src/stage9_scale_test.py
python src/stage9_boundary_perturbation_test.py
python src/stage9_repeatability_test.py
python src/stage9_transform_test.py
python src/stage9_subdivision_test.py
```

---

## What V1 Does Not Claim

V1 does not claim:

```text
general automatic defect recognition
semantic design-intent recovery
arbitrary hole filling
general non-planar remeshing
tessellation invariance
universal threshold validity
production-scale performance
generalization to arbitrary real assets
```

---

## V2 Directions

Potential V2 work includes:

```text
cotangent / geometry-weighted Laplacian
resolution-aware spectral criteria
area-weighted geometric statistics
better discrete-to-continuous cuts
general non-planar remeshing
semantic / user repair authorization
incremental sweep-cut optimization
real-asset benchmark evaluation
```

---

## Documentation

For the full V1 experimental record, design decisions, robustness tests, and limitations, see:

[`Game_Ready_Mesh_Repair_V1_Summary.md`](Game_Ready_Mesh_Repair_V1_Summary.md)

---

## Status

```text
S1  Mesh graph                       COMPLETE
S2  Laplacian                        COMPLETE
S3  Eigen-analysis                   COMPLETE
S4  Sweep cut                        COMPLETE
S5  Structural localization          COMPLETE
S6  Geometry characterization        COMPLETE
S7  Interpretable decision           COMPLETE
S8  Conservative repair              COMPLETE
S9  Evaluation and robustness        COMPLETE
```

**Game-Ready Mesh Repair V1 is complete.**

Release tag:

```text
v1.0-spectral-safe-repair
```