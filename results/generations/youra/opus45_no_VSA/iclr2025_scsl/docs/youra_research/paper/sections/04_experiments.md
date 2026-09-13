# Experiments

## Dataset

We use **Waterbirds** (Sagawa et al., 2019), a standard benchmark for spurious correlations. The dataset pairs bird type (landbird/waterbird) with background (land/water), creating four groups with 95/5 majority/minority split. Training set: 4,795 samples; validation: 1,199; test: 5,794.

| Group | Bird | Background | Train % | Role |
|-------|------|------------|---------|------|
| 0 | Landbird | Land | 73% | Majority |
| 1 | Landbird | Water | 4% | Minority |
| 2 | Waterbird | Water | 22% | Majority |
| 3 | Waterbird | Land | 1% | Minority |

## Experiment 1: Initialization Symmetry (H-E1)

**Hypothesis:** SR ≈ 1.0 at random initialization, ruling out intrinsic curvature asymmetry.

**Setup:** We initialize a SmallCNN architecture with random weights across 5 seeds and compute SR₀ using power iteration (20 iterations, 100 samples per group).

**Rationale:** If SR₀ significantly deviates from 1.0, the curvature asymmetry is intrinsic to the model-data combination rather than training-induced. This would falsify the DCR mechanism hypothesis.

**Note:** We use a minimal architecture (SmallCNN, ~1K params) to enable CPU execution. The core hypothesis—random initialization produces symmetric curvature—is architecture-agnostic.

## Experiment 2: Temporal Precedence (H-M1)

**Hypothesis:** Per-sample gradient ratio decay precedes SR divergence (τ_r→SR > 0).

**Setup:** We train ResNet-50 (ImageNet pretrained) on Waterbirds for 10 epochs using SGD (lr=0.001, momentum=0.9). At each epoch, we measure:
- Gradient ratio $r_t$: per-sample gradient norms, majority/minority
- Sharpness ratio $\text{SR}_t$: Hessian max eigenvalue ratio

We compute lagged cross-correlation for $\tau \in [-5, +5]$ epochs across 3 seeds.

**Rationale:** If gradient ratio decay (majority converging faster) causes SR divergence (minority becoming sharper), gradient changes should temporally precede curvature changes. A positive lag ($\tau > 0$) supports causation; zero or negative lag would suggest reverse causation or confounding.

## Experiment 3: Intervention Validation (H-M2)

**Hypothesis:** Update-norm parity attenuates SR divergence.

**Setup:** We implement an **update-norm parity** intervention that scales per-group gradients toward the mean norm:
$$\tilde{g}_g = g_g \cdot \frac{\bar{n}}{\|g_g\|}$$
where $\bar{n}$ is the mean gradient norm across groups.

**Status:** Code implementation complete and unit-tested. Full experiment execution blocked by hardware constraints (CPU-only environment). We report code validation results; full experimental validation is future work.

## Evaluation Metrics

| Metric | Definition | Success Criterion |
|--------|------------|-------------------|
| SR₀ | Sharpness ratio at initialization | ∈ [0.9, 1.1], CI includes 1.0 |
| τ_r→SR | Optimal lag in cross-correlation | > 0, CI excludes zero |
| SR_parity | SR under parity intervention | ≤ 1.1 (vs baseline > 1.2) |
