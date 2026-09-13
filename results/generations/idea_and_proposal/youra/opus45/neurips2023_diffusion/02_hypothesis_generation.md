# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SBAD-C-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under standard 3D point cloud generation conditions (ShapeNet/Objaverse datasets), if we decompose point cloud representations into K spectral frequency bands via graph Laplacian eigenvectors and apply band-specific diffusion processes with fewer steps for low-frequency (coarse) bands and more steps for high-frequency (detail) bands with cross-band message passing, then we achieve 2-3x inference speedup while matching or exceeding geometric quality (Chamfer Distance, F-Score) because low-frequency geometric structure requires fewer denoising iterations than high-frequency details (physics coarse-graining principle).

**Alternative Hypothesis (H0):**
There is no significant speedup achievable through spectral band decomposition in 3D diffusion, OR spectral decomposition degrades geometric quality to the point where any speedup is not practically useful (quality-speed trade-off remains linear).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Spectral decomposition method | Independent | Graph Laplacian eigenvector computation with K=3-5 bands | K ∈ {3, 4, 5} |
| Band-specific step allocation | Independent | Learnable noise schedules per band (beta_start, beta_end, num_steps) | Low-freq: 10-20 steps, High-freq: 40-60 steps |
| Cross-band coupling | Independent | Lightweight attention mechanism between band representations | Attention heads: 2-4, hidden dim: 64-128 |
| Generation speed | Dependent | Effective NFE (Number of Function Evaluations), wall-clock time | Target: 2-3x speedup vs uniform 50-step baseline |
| Geometric quality | Dependent | Chamfer Distance (CD), F-Score@1%, IoU on ShapeNet categories | CD ≤ baseline, F-Score ≥ baseline |
| 3D representation | Controlled | Point cloud format | 2048-4096 points per shape |
| Dataset | Controlled | ShapeNet (Chair, Airplane, Car) and Objaverse subset | Standard train/test splits |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Spectral Decomposition
    ↓
Step 2: Differential Band Scheduling
    ↓
Step 3: Cross-Band Coupling + Reconstruction
    ↓
Outcome: Speedup with Quality Preservation
```

**Step 1: Spectral Decomposition → Band Separation**
Graph Laplacian eigenvectors project point cloud features onto K orthogonal frequency bands. Low-frequency bands capture coarse global structure (overall shape), while high-frequency bands capture fine local details (surface texture, edges).

**Step 2: Band Separation → Differential Scheduling**
Low-frequency bands require fewer denoising steps because they represent simpler, more stable features. High-frequency bands need more steps to resolve fine details. This mirrors physics coarse-graining where macroscopic properties equilibrate before microscopic ones.

**Step 3: Differential Scheduling + Cross-Band Coupling → Speedup with Quality**
By allocating computational budget proportionally to band complexity and maintaining geometric coherence via lightweight cross-band attention, total NFE decreases while generation quality is preserved through coherent multi-scale reconstruction.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Graph signal processing (DGCNN) | Laplacian eigenvectors capture meaningful geometric scales | Strong |
| Step2 → Step3 | DPM-Solver (Lu et al. 2022) | Different frequency components converge at different rates in diffusion | Strong |
| Step3 → Outcome | PFGM++, Neural TI | Physics principles (thermodynamic integration) enhance diffusion efficiency | Medium |

**Key Tension:**
- **Tension:** Benita et al. (2025) show spectral analysis improves 2D diffusion scheduling, but their approach modifies schedule shape rather than using parallel diffusion trajectories. It's unclear if the parallel trajectory approach provides additional benefits beyond schedule modification in 3D.
- **Resolution:** This verification plan tests whether parallel band-specific diffusion (SBAD-C) provides speedup beyond what schedule optimization alone achieves, particularly in the 3D domain where computational costs are higher.

### 1.4 Key Assumptions

1. **Spectral decomposition captures meaningful geometric hierarchy**
   - Evidence: Graph Laplacian eigenvectors are well-established in point cloud processing (DGCNN, PointNet++)
   - Consequence if violated: Band separation would be arbitrary, preventing differential scheduling from providing speedup

2. **Low-frequency bands converge faster than high-frequency bands**
   - Evidence: DPM-Solver analysis shows frequency-dependent convergence; physics analogy from coarse-graining
   - Consequence if violated: No computational savings from differential step allocation; hypothesis fails

3. **Band-specific schedules can be learned end-to-end**
   - Evidence: Learnable noise schedules exist in consistency models and Align Your Steps
   - Consequence if violated: Training instability; requires manual schedule tuning

4. **Cross-band coupling overhead is small (~5%)**
   - Evidence: Lightweight attention mechanisms (2-4 heads) add minimal compute
   - Consequence if violated: Net speedup reduced below 2x threshold

5. **Spectral reconstruction preserves quality**
   - Evidence: Spectral methods are lossless for frequency decomposition
   - Consequence if violated: Quality degradation even with perfect band denoising

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- 3D point cloud generation (unconditional and class-conditional)
- Datasets with clear multi-scale geometric structure (ShapeNet, Objaverse)
- Shapes with 2048-4096 points
- Single-GPU training and inference scenarios

**Where Hypothesis Does NOT Apply:**
- Arbitrary 3D representations without graph structure (raw voxels, implicit functions)
- Real-time generation requirements (<10ms latency)
- Extremely large point clouds (>100K points) where Laplacian computation becomes bottleneck
- Shapes with no multi-scale structure (simple primitives)

**Known Limitations:**
- Graph Laplacian eigenvector computation adds O(n log n) preprocessing overhead
- Cross-band coupling adds ~5% computational overhead per step
- Currently focused on point clouds; extension to meshes/voxels requires additional work
- Band boundary selection (eigenvalue thresholds) may require per-dataset tuning

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Speedup vs Baseline):**
SBAD-C will achieve effective NFE ≤ 25 steps (total across all bands) while uniform-schedule baseline requires 50 steps for equivalent quality, yielding 2x speedup.

*Measurement*:
- Wall-clock inference time comparison (SBAD-C vs PVD baseline)
- Effective NFE = Σ(steps per band × band computation ratio)
- Statistical test: Paired t-test across 1000 generated samples, p < 0.05

*Basis*:
Physics coarse-graining principle suggests 50-70% of diffusion steps are spent on coarse structure that resolves quickly. Conservative 2x target accounts for overhead.

*Success Criteria for Phase 2B*:
- Primary: Speedup ≥ 2x with quality parity (p < 0.05)
- Stretch: Speedup ≥ 2.5x with quality improvement

**Secondary Predictions:**
**P2 (Quality Preservation):**
SBAD-C will achieve Chamfer Distance ≤ 1.05× baseline CD and F-Score@1% ≥ 0.95× baseline F-Score on ShapeNet Chair/Airplane/Car categories.

**P3 (Band Convergence Validation):**
Low-frequency bands (eigenvalues 0-10) will reach quality plateau in ≤15 steps, while high-frequency bands (eigenvalues >50) require ≥40 steps.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Speedup < 1.5x (after accounting for overhead)
2. **Quality Failure**: CD > 1.2× baseline OR F-Score < 0.85× baseline
3. **Mechanism Failure**: Low-frequency bands do NOT converge faster than high-frequency bands
4. **Overhead Failure**: Cross-band coupling adds >20% overhead

### 1.7 SOTA Baseline (Comparison Mode)

| Method | Type | Dataset | Key Metric | Notes |
|--------|------|---------|------------|-------|
| PVD (Zhou et al. 2021) | Point-Voxel Diffusion | ShapeNet | CD, 1-NN | Strong unconditional generation |
| Point-E (OpenAI 2023) | Point Cloud Diffusion | Internal 3M | Qualitative | Fast but lower quality |
| Shap-E (OpenAI 2023) | Implicit Function Diffusion | Internal 3M | Qualitative | Faster than Point-E, multi-rep |

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect for 2x speedup)
- Required runs: n ≥ 20 per category (Chair, Airplane, Car)
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds for SBAD-C and baseline)
- Significance level: α = 0.05 (one-tailed for speedup, two-tailed for quality)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does spectral band-adaptive diffusion produce valid 3D point clouds with measurable geometric quality (CD, F-Score) under standard generation conditions?"
- Maps to: Primary prediction P1
- Verification type: Empirical generation + quality measurement
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the spectral band decomposition → differential scheduling → cross-band reconstruction mechanism the actual cause of efficiency gains?"

This will decompose into 3 sub-hypotheses in Phase 2B:
- **H-M1:** Spectral decomposition effectively separates geometric scales (Step 1)
- **H-M2:** Low-frequency bands converge faster than high-frequency bands (Step 2)
- **H-M3:** Cross-band coupling preserves coherence during parallel diffusion (Step 3)

**SH3 (Comparison):**
"Does SBAD-C outperform uniform-schedule baselines (PVD, Point-E) in speed-quality trade-off?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical benchmarking
- Critical: Determines practical value of the approach

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-SBAD-C-v1)
- [x] Confidence level specified (0.78)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and documented
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (P1 primary, P2/P3 secondary)
- [x] Falsification criteria are defined (4 failure conditions)
- [x] Baselines are identified for comparison (PVD, Point-E, Shap-E)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What GPU memory is needed for spectral decomposition + multi-band diffusion? (Estimated: 24GB for 4096-point clouds with K=5 bands)

2. **Data Availability:** Are pretrained PVD checkpoints available for fair comparison, or must we train from scratch? (ShapeNet data is public)

3. **Band Boundary Selection:** How to determine optimal eigenvalue thresholds for band separation? (Start with uniform quantiles, then learn)

4. **Priority Verification Order:** Should we validate SH2 (mechanism) first to ensure physics principle holds before full implementation? (Recommended: quick pilot on band convergence rates)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
