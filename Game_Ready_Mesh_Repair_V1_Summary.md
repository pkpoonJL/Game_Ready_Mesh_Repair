# Game-Ready Mesh Repair V1

## 1. Project Scope

This V1 implements a conservative mesh-diagnostics and repair pipeline based on graph spectral analysis and geometric validation.

> **Detect aggressively, repair conservatively.**

The system:

1. detects structurally weak attachments,
2. characterizes their geometry,
3. makes an interpretable decision,
4. attempts repair only when strict safety conditions are satisfied,
5. validates the repaired mesh afterward.

---

## 2. Pipeline Overview

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
S8  Conservative Repair + Post-validation
    ↓
S9  Evaluation / Robustness / Failure Analysis
```

---

## 3. S1–S4: Spectral Backbone

V1 converts the triangle mesh into an undirected vertex-adjacency graph and analyzes connected components independently.

The current Laplacian is

$$
L_{\mathrm{sym}}
=
I-D^{-1/2}AD^{-1/2}
$$

where $A$ is the vertex-adjacency matrix and $D$ is the degree matrix.

The Fiedler pair is

$$
(\lambda_2,v_2)
$$

where $v_2$ is used to generate the spectral ordering for the sweep cut.

For a sweep candidate $S$, conductance is

$$
\phi(S)
=
\frac{|E(S,\bar S)|}
{\min(\operatorname{vol}(S),\operatorname{vol}(\bar S))}
$$

The key interpretation is:

> **Low conductance measures structural separability, not defect probability.**

Every connected graph has a best cut, and legitimate geometry can also produce strong bottlenecks.

---

## 4. S5: Structural Localization

S5 interprets the spectral result as a structural candidate rather than a semantic defect.

Useful evidence includes:

- conductance,
- cut edges,
- candidate partition fraction,
- Fiedler eigenvalue,
- Fiedler eigengap.

The candidate fraction is

$$
p=
\frac{|S_{\mathrm{candidate}}|}
{|V_{\mathrm{component}}|}
$$

Current working V1 thresholds:

```text
localized threshold: 0.35
global threshold:    0.45
conductance:         0.03
eigengap:            0.001
```

These are controlled V1 thresholds, not universal constants.

The final interpretation of S5 is:

> **S5 detects structural separability, not semantic defects.**

---

## 5. S6: Geometry Characterization

For candidate vertices $p_i$, define

$$
q_i=p_i-\bar p
$$

and construct the covariance matrix

$$
C=
\frac{1}{n}
\sum_i q_iq_i^T
$$

Let

$$
\lambda_1\ge\lambda_2\ge\lambda_3
$$

be the covariance eigenvalues.

V1 uses

$$
r_2=\frac{\lambda_2}{\lambda_1}
$$

and

$$
r_3=\frac{\lambda_3}{\lambda_1}
$$

to characterize candidate geometry.

Current working shape rules are:

```text
rod:
    r2 < 0.08 and r3 < 0.08

compact:
    r2 > 0.5 and r3 > 0.5

sheet:
    r2 > 0.5 and r3 < 0.08

otherwise:
    intermediate
```

The PCA shape class is explanatory evidence only.

It does **not** establish semantic intent.

---

## 6. S7: Interpretable Decision

S7 outputs:

```text
keep
repair_candidate
manual_review
```

### Meaning of `repair_candidate`

`repair_candidate` means:

> A structurally clear localized weak attachment worth sending into the S8 repair-safety pipeline.

It does **not** mean:

```text
confirmed defect
safe to delete
semantically unwanted
```

The controlled pair

```text
legitimate_knob
protrusion_medium
```

has identical geometry but different semantic labels.

Therefore a deterministic geometry-only system must behave identically on both.

This gives an important V1 conclusion:

> **Geometry alone cannot recover design intent.**

---

## 7. S8: Conservative Repair

Automatic repair is attempted only when all current safety conditions pass:

```text
non-empty repair boundary
single closed boundary loop
candidate fraction <= 0.35
stable spectral evidence
planar boundary
nondegenerate boundary
convex boundary
```

The current planar condition uses PCA on the repair boundary.

The primary criterion is

$$
r_3<0.01
$$

with the additional nondegeneracy condition

$$
r_2>0.01
$$

### Repair Procedure

```text
remove candidate-touching faces
    ↓
extract newly exposed repair boundary
    ↓
order boundary loop
    ↓
insert boundary centroid
    ↓
centroid-fan triangulation
    ↓
orient cap faces consistently
    ↓
remove unreferenced vertices
```

This is intentionally a narrow repair primitive.

V1 does not attempt general non-planar hole filling or arbitrary remeshing.

---

## 8. Post-repair Validation

After repair, the output mesh is checked for:

```text
open boundary edges
non-manifold edges
degenerate faces
unexpected connected components
```

A repair is accepted only when post-validation passes.

Current positive control:

```text
appendage_long
→ repair_candidate
→ safety passed
→ repair executed
→ post-validation passed
```

Other candidates are safely refused when their exposed repair boundary cannot be handled by the current primitive.

---

# 9. S9 Evaluation

## 9.1 Controlled Dataset

Current controlled dataset:

```text
11 cases
10 unique geometries
```

The duplicate geometry is intentional and acts as a semantic-control pair.

### S7 Outcome

```text
keep              2
manual_review     2
repair_candidate  7
```

### S8 Outcome

```text
safety passed     1
safety refused    6

valid repairs     1
invalid repairs   0

safety coverage   1 / 7 = 14.3%
```

The correct interpretation is:

> The single repair attempted under the current conservative safety gate passed all post-repair validity checks.

It would not be justified to claim a general 100% repair success rate from one attempted repair.

---

## 9.2 Regression Checks

Current baseline regression checks:

```text
PASS  baseline_cube_is_keep
PASS  appendage_long_safe_repair
PASS  appendage_medium_safe_refusal
PASS  compact_boss_is_keep
PASS  duplicate_geometry_consistency
```

The duplicate-geometry test ensures that geometry-only processing remains internally consistent.

---

## 9.3 Semantic Audit

The only automatically repaired controlled case was labeled legitimate:

```text
appendage_long
```

Therefore

$$
\text{geometrically safe to remove}
\neq
\text{semantically correct to remove}
$$

This is a central V1 result.

A destructive automatic system would require external context such as:

```text
user annotation
asset metadata
generation history
known defect labels
protected regions
upstream semantic intent
```

---

# 10. Coordinate Scale Robustness

Initial tests used:

```text
0.1x
1x
10x
```

and passed.

Extreme stress testing then used:

```text
1e-6
1e-4
1e-2
1
1e2
1e4
1e6
```

This exposed two scale-dependent implementation bugs.

## Bug 1 — Absolute Geometric Tolerance

Absolute geometric tolerances caused valid very-small-scale boundaries to be incorrectly rejected.

The fix was to replace dimensional tests with normalized or dimensionless criteria.

## Bug 2 — Absolute Degenerate-face Area Threshold

The original degenerate-face test compared triangle area against a fixed epsilon.

Triangle area scales as

$$
A' = s^2A
$$

so very small but perfectly valid triangles could be classified as degenerate.

The test was changed to use

$$
\frac{\|AB\times AC\|}
{\|AB\|\|AC\|}
$$

which is dimensionless.

After these fixes:

```text
1e-6  PASS
1e-4  PASS
1e-2  PASS
1      PASS
1e2   PASS
1e4   PASS
1e6   PASS
```

Supported claim:

> Pipeline behavior remained invariant under uniform coordinate scaling across the tested range $10^{-6}$ to $10^6$.

---

# 11. Controlled Boundary Perturbation

Starting from the planar repair boundary of `appendage_long`, one boundary vertex was moved out of plane while topology and spectral evidence were held fixed.

Results:

```text
delta=0.00   r3=0.00000000   safe=True
delta=0.01   r3=0.00002500   safe=True
delta=0.05   r3=0.00062344   safe=True
delta=0.10   r3=0.00247512   safe=True

delta=0.25   r3=0.01467870   safe=False
delta=0.50   r3=0.04874779   safe=False
delta=1.00   r3=0.09850768   safe=False
```

The transition is consistent with the current threshold

$$
t_{\mathrm{planar}}=0.01
$$

The `delta=1.0` construction reproduces the observed non-planarity level of `appendage_medium`.

This confirms that its S8 refusal comes from repair-boundary geometry rather than spectral randomness.

---

# 12. Repeatability

Representative meshes were repeatedly analyzed:

```text
4 meshes × 20 runs = 80 runs
```

Results:

```text
80 / 80 final decisions stable
80 / 80 S8 safety outcomes stable
```

The tested cases included:

```text
baseline_cube
appendage_long
legitimate_compact_boss
protrusion_medium
```

Observed Fiedler-value variation remained near floating-point precision.

---

# 13. Rigid-transform Invariance

The pipeline was tested under:

```text
identity
rotation about x
rotation about arbitrary axis
translation
rotation + translation
```

Across four representative meshes:

```text
4 meshes × 5 transforms = 20 runs
20 / 20 PASS
```

No tested transform changed:

```text
S7 decision
shape class
S8 safety behavior
repair validity
```

---

# 14. Tessellation / Subdivision Limitation

This is the most important structural limitation discovered in S9.

Uniform subdivision changes mesh discretization density while preserving the underlying continuous surface.

## Candidate Fraction

Candidate fraction remained nearly stable.

For `appendage_long`:

```text
level 0: 0.076759
level 1: 0.075814
level 2: 0.075978
```

## Shape Classification

PCA shape class remained stable:

```text
rod     → rod     → rod
sheet   → sheet   → sheet
compact → compact → compact
```

## Spectral Quantities

Spectral quantities did not remain stable.

For `appendage_long`:

```text
conductance:
0.018779
0.009423
0.004691

eigengap:
0.005315
0.001333
0.000334
```

The observed conductance approximately halves with each subdivision level.

The observed eigengap approximately quarters.

At subdivision level 2:

```text
eigengap < 0.001
→ spectral_instability
→ manual_review
```

The same general trend was observed across multiple geometry families.

Therefore:

> **The current unweighted graph spectral quantities are mesh-resolution dependent.**

This means the current absolute spectral thresholds are not tessellation invariant.

---

# 15. Discrete Repair-boundary Sensitivity

Subdivision also changes the exact discrete spectral cut and therefore the exposed repair boundary.

For `appendage_long`:

```text
level 0
→ repair_candidate
→ planar repair boundary
→ S8 safe

level 1
→ repair_candidate
→ boundary_not_planar
→ S8 refuses

level 2
→ spectral_instability
→ manual_review
```

Therefore

$$
\text{same continuous geometry}
\not\Rightarrow
\text{same discrete repair loop}
$$

This is an explicit V1 limitation.

---

# 16. Performance Limitation

The current sweep-cut implementation materializes sweep candidate sets and recomputes conductance from scratch for every candidate.

Dense subdivision therefore produces a large runtime increase.

This was directly observed on meshes with more than ten thousand vertices.

V1 treats this as a performance limitation rather than a correctness blocker.

A future implementation should incrementally maintain:

```text
cut size
volume(S)
volume(V \ S)
```

while moving through the Fiedler ordering.

---

# 17. What V1 Can Claim

V1 supports the following claim:

> The system can identify weak graph attachments through spectral partitioning, characterize candidate geometry using PCA, route ambiguous cases through interpretable decision rules, and perform a narrowly defined conservative repair when strict geometric safety conditions are satisfied.

Controlled experiments additionally show:

- stable behavior under tested coordinate scaling,
- rigid-transform invariance,
- repeatable final decisions,
- predictable sensitivity to repair-boundary non-planarity,
- successful execution and validation of the supported repair primitive,
- explicit detection of resolution-dependent spectral limitations.

---

# 18. What V1 Does Not Claim

V1 does **not** establish:

```text
general automatic defect recognition
semantic design-intent recovery
arbitrary hole filling
general non-planar remeshing
tessellation invariance
universal threshold validity
production-scale runtime
generalization to arbitrary real assets
```

These are intentionally outside the V1 scope.

---

# 19. Main V1 Conclusions

## 1. Spectral structure detects separability, not defect intent

A strong graph bottleneck can occur in both legitimate and defect-like geometry.

## 2. PCA provides useful geometric explanation

Rod, sheet, compact, and intermediate candidate geometries can be described using covariance eigenvalue ratios.

## 3. Geometry alone cannot determine semantic intent

Identical geometry can correspond to different intended meanings.

## 4. Repairability and desirability are different questions

A region can be geometrically safe to remove while still being semantically legitimate.

## 5. Conservative refusal is a valid system outcome

When the supported repair primitive is not justified, V1 refuses instead of forcing a repair.

## 6. Normalized geometric checks improve scale robustness

S9 exposed and corrected scale-dependent absolute-tolerance bugs.

## 7. Unweighted spectral quantities remain discretization-dependent

Subdivision is the main structural limitation of the current spectral formulation.

---

# 20. V2 Directions

Natural V2 directions include:

```text
cotangent / geometry-weighted Laplacian
resolution-aware or relative spectral stability criteria
area-weighted PCA
better discrete-to-continuous cut formulation
non-planar boundary triangulation
general remeshing
external semantic authorization
incremental sweep-cut optimization
real-asset benchmark dataset
```

These should be treated as V2 method improvements rather than patches to V1.

---

# 21. Final V1 Status

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

# V1 Final Status

> **Game-Ready Mesh Repair V1 is complete.**

The project now has a complete research loop:

$$
\boxed{
\text{hypothesis}
\rightarrow
\text{implementation}
\rightarrow
\text{controlled experiment}
\rightarrow
\text{failure analysis}
\rightarrow
\text{justified fixes}
\rightarrow
\text{documented limitations}
}
$$

Recommended tag:

```text
v1.0-spectral-safe-repair
```