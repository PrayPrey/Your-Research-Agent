# Product Requirements Document: H-M2
# Permutation Orbit Variance Dominance — Var_perm / (Var_perm + Var_GL) > 0.60

**Hypothesis**: H-M2 (MECHANISM — INCREMENTAL on H-E1, H-M1)
**Date**: 2026-05-21
**Author**: Anonymous Pipeline (Phase 3 — UNATTENDED)
**Source**: Phase 2C Experiment Brief (`02c_experiment_brief.md`)
**Tier**: FULL (MECHANISM hypothesis, max 30 tasks)

---

## 1. Executive Summary

H-M2 measures whether permutation orbit variance dominates GL orbit variance in CNN Zoo checkpoint trajectory geometry. Specifically, the experiment computes:

**Var_perm / (Var_perm + Var_GL)**

across full Small CNN Zoo training trajectories (epochs 0..50) and tests if this ratio exceeds 0.60.

The experiment reuses the `OrbitPEComputer` module built and validated in H-M1, extending it to measure variance fractions on full trajectory data rather than single-checkpoint overhead. The `VarianceDecomposer` module projects flattened checkpoint weight vectors onto:
1. Permutation orbit subspace (via orbit-aligned PCA basis from H-M1)
2. GL orbit subspace (via polar decomposition residual, per arXiv:2410.04207)

Gate: **MUST_WORK** — Var_perm / (Var_perm + Var_GL) > 0.60 (mean across CIFAR-10-GS subset, minimum 200 models).

**PIVOT condition**: If ratio < 0.60, implement hybrid orbit-PE + GL trace features (tr(W^Q W^{K,T})) before H-M3.

---

## 2. Problem Statement

NFN achieves τ > 0.93 on CNN Zoo using **only permutation equivariance** (no GL-invariant features). This implies permutation orbit structure captures the dominant predictive variance in checkpoint geometry. However, this has never been directly measured as a variance decomposition. H-M2 provides that direct measurement.

H-M1 validated that orbit-PE computation is architecture-agnostic with 1.167x overhead. H-M2 now uses that validated module to answer: *How much of the total variance in CNN Zoo checkpoint trajectories is explained by permutation orbit directions vs GL orbit directions?*

If permutation orbits dominate (ratio > 0.60), orbit-PE is justified as the primary positional encoding for H-M3's cross-architecture experiment. If they don't, a hybrid strategy is needed.

---

## 3. Goals and Non-Goals

### Goals
- Implement `VarianceDecomposer` module using H-M1's `OrbitPEComputer` + SVD-based trajectory projection
- Load full checkpoint trajectories (epochs 0..50) for all available CNN Zoo models in CIFAR-10-GS and SVHN-GS subsets
- Compute Var_perm and Var_GL per model trajectory and aggregate mean ± std ratio
- Verify cross-dataset stability: |ratio_CIFAR10 - ratio_SVHN| < 0.10
- Generate visualizations (ratio histogram, epoch-wise evolution, per-layer breakdown)

### Non-Goals
- Model training (pure analysis)
- Cross-architecture analysis (H-M3 covers this)
- Transformer Zoo analysis (CNN Zoo only for this hypothesis)
- Hyperparameter tuning of variance decomposition

---

## 4. Data Specification

### 4.1 Primary Dataset: Small CNN Zoo (CIFAR-10-GS)

| Property | Value |
|----------|-------|
| Source | ModelZoos/ModelZooDataset (Schürholt et al., NeurIPS 2022) + wsl-modelzoo CLI |
| Architecture | cnn-small (Conv2d + Linear + global pooling, ~2.5k params) |
| Checkpoint range | Epochs 0..50 (51 checkpoints per model trajectory) |
| Zoo identifier | `core / cnn-small / cifar10 / uniform` |
| Minimum sample | **200 models** with complete 0..50 trajectories |
| Format | PyTorch checkpoint files via wsl-modelzoo |
| Download method | `modelzoo fetch --zoo core --arch cnn-small --dataset cifar10 --config uniform --seed all --ckpts all --dir ./data/cnn_zoo_cifar10/` |

**Task**: Requires `pip install wsl-modelzoo` + dataset fetch → generates `data-preparation` task.

### 4.2 Secondary Dataset: Small CNN Zoo (SVHN-GS)

| Property | Value |
|----------|-------|
| Source | Same Zenodo repository as CIFAR-10-GS |
| Architecture | Same cnn-small architecture |
| Checkpoint range | Epochs 0..50 |
| Zoo identifier | `core / cnn-small / svhn / uniform` |
| Minimum sample | **200 models** with complete trajectories |
| Download method | `modelzoo fetch --zoo core --arch cnn-small --dataset svhn --config uniform --seed all --ckpts all --dir ./data/cnn_zoo_svhn/` |
| Purpose | Cross-dataset stability check (secondary success criterion) |

### 4.3 Prerequisite Module: H-M1 OrbitPEComputer

| Property | Value |
|----------|-------|
| Source | H-M1 validated implementation |
| Location | `docs/youra_research/20260521_wsl/h-m1/code/` |
| Import | `from orbit_pe import OrbitPEComputer` |
| Validated for | Conv2d, Linear layers (cnn-small layer types) |
| Overhead | 1.167x ± 0.061 (PASS, H-M1 gate satisfied) |

### 4.4 Data Loading Code

```bash
pip install wsl-modelzoo
modelzoo fetch --zoo core --arch cnn-small --dataset cifar10 --config uniform \
  --seed all --ckpts all --dir ./data/cnn_zoo_cifar10/
modelzoo fetch --zoo core --arch cnn-small --dataset svhn --config uniform \
  --seed all --ckpts all --dir ./data/cnn_zoo_svhn/
```

```python
import torch
from pathlib import Path

def load_trajectory(model_dir: Path, n_checkpoints: int = 51):
    """Load all epoch checkpoints for one model."""
    ckpt_files = sorted(model_dir.glob("epoch_*.pt"))[:n_checkpoints]
    return [torch.load(f, map_location='cpu') for f in ckpt_files]
```

---

## 5. Functional Requirements

### FR-1: VarianceDecomposer Module

| Requirement | Description |
|-------------|-------------|
| FR-1.1 | Implement `VarianceDecomposer` class with `compute_trajectory_variance_ratio(trajectory)` method |
| FR-1.2 | `flatten_weights(state_dict)` → concatenate all weight tensors to 1D vector of shape (P,) |
| FR-1.3 | `compute_perm_orbit_projection(W_flat, orbit_basis)` → project onto orbit-aligned PCA subspace; return (W_perm, Var_perm) |
| FR-1.4 | `compute_gl_orbit_projection(W_layer)` → polar decomposition W = QS; return Var_GL = ||W_polar_S - W_layer||^2 |
| FR-1.5 | Compute orbit_basis from `orbit_pe_computer.get_orbit_basis(trajectory[0])` → shape (D, P) where D ≤ 64 |
| FR-1.6 | Aggregate Var_perm and Var_GL across all T checkpoints in trajectory; return ratio = Var_perm / (Var_perm + Var_GL + 1e-8) |
| FR-1.7 | Handle memory-constrained case: subsample to ≤ 50 checkpoints if full trajectory (51 ckpts) causes OOM |

### FR-2: OrbitPEComputer Integration (H-M1 Reuse)

| Requirement | Description |
|-------------|-------------|
| FR-2.1 | Import `OrbitPEComputer` from H-M1 code (`docs/youra_research/20260521_wsl/h-m1/code/`) |
| FR-2.2 | Use `orbit_pe_computer.get_orbit_basis(state_dict)` to extract orbit-aligned subspace basis |
| FR-2.3 | Verify H-M1 module handles Conv2d and Linear layers (cnn-small layer types confirmed in H-M1 validation) |

### FR-3: Full Trajectory Analysis

| Requirement | Description |
|-------------|-------------|
| FR-3.1 | Load all models with complete trajectories (epoch 0 through epoch 50 checkpoints present) |
| FR-3.2 | Filter: skip models with fewer than 10 trajectory checkpoints |
| FR-3.3 | Analyze minimum 200 CIFAR-10-GS models and 200 SVHN-GS models |
| FR-3.4 | Per-model: compute ratio using `VarianceDecomposer.compute_trajectory_variance_ratio()` |
| FR-3.5 | Aggregate: `ratio_mean = np.mean(ratios)`, `ratio_std = np.std(ratios)` for each subset |

### FR-4: Cross-Dataset Stability Check

| Requirement | Description |
|-------------|-------------|
| FR-4.1 | Run identical analysis on SVHN-GS subset |
| FR-4.2 | Compute `|ratio_CIFAR10 - ratio_SVHN|` as stability metric |
| FR-4.3 | Log WARNING if stability gap ≥ 0.10 (secondary criterion failure) |
| FR-4.4 | Report both ratios side-by-side in results summary |

### FR-5: Mechanism Activation Verification

| Requirement | Description |
|-------------|-------------|
| FR-5.1 | Implement `verify_mechanism_activated(results)` as specified in Phase 2C |
| FR-5.2 | Check: `n_trajectories > 100`, `orbit_basis_shape[0] > 0`, `0.0 <= var_ratio <= 1.0`, `var_perm > 0 and var_gl > 0` |
| FR-5.3 | Log each indicator result; fail fast if any indicator is False |

### FR-6: Visualization

| Requirement | Description |
|-------------|-------------|
| FR-6.1 | **Gate figure (MANDATORY)**: Bar chart showing Var_perm, Var_GL, and ratio for CIFAR-10-GS and SVHN-GS side by side with 0.60 threshold line |
| FR-6.2 | Trajectory variance ratio histogram: distribution of per-model ratios across all CNN Zoo models |
| FR-6.3 | Ratio vs training epoch: line plot of mean ratio at each epoch step (early vs late training) |
| FR-6.4 | Per-layer breakdown: bar chart of Conv2d vs Linear contribution to Var_perm and Var_GL |
| FR-6.5 | Scatter: ratio vs final model accuracy (secondary analysis) |
| FR-6.6 | Save all figures to `docs/youra_research/20260521_wsl/h-m2/figures/` |

### FR-7: Result Reporting

| Requirement | Description |
|-------------|-------------|
| FR-7.1 | Save metrics JSON: `{var_ratio_mean, var_ratio_std, n_models, ratio_cifar10, ratio_svhn, stability_gap, gate_pass}` |
| FR-7.2 | Generate `04_validation.md` with gate pass/fail determination and PIVOT recommendation if fail |
| FR-7.3 | Print `"Var_perm / (Var_perm + Var_GL) = {ratio_mean:.4f} ± {ratio_std:.4f}"` to stdout |

---

## 6. Non-Functional Requirements

| NFR | Description |
|-----|-------------|
| NFR-1 | Runtime ≤ 60 minutes total on single GPU (CPU-bound SVD operations) |
| NFR-2 | Single GPU (lowest-memory GPU via `nvidia-smi`) — set `CUDA_VISIBLE_DEVICES` before run |
| NFR-3 | Memory: < 8GB GPU VRAM; CPU RAM: < 16GB (checkpoint loading per-model, not all at once) |
| NFR-4 | Deterministic: SVD-based projection is deterministic given fixed checkpoints (seed=1) |
| NFR-5 | Numerical stability: add 1e-8 to denominator in ratio computation |
| NFR-6 | No Internet during experiment (all data pre-downloaded) |

---

## 7. Success Criteria (Gate: MUST_WORK)

| Criterion | Threshold | Gate Type |
|-----------|-----------|-----------|
| `var_ratio_mean` (CIFAR-10-GS) | > 0.60 | PRIMARY (MUST_WORK) |
| `n_models_analyzed` | ≥ 200 (CIFAR-10-GS) | PRIMARY |
| `var_ratio_std` | > 0.01 (non-degenerate) | PRIMARY |
| `ratio_stable` | \|ratio_CIFAR10 - ratio_SVHN\| < 0.10 | SECONDARY |

**PASS**: ratio_mean > 0.60 AND n_models ≥ 200 AND non-degenerate → proceed to H-M3 with orbit-PE as primary PE strategy

**FAIL (PIVOT)**: ratio_mean < 0.60 → implement hybrid orbit-PE + low-degree GL invariant polynomial traces (tr(W^Q W^{K,T})) before H-M3; re-design H-M3 with hybrid model

---

## 8. Dependencies

### 8.1 Python Packages

```
torch>=1.12.0
numpy>=1.21.0
scipy>=1.7.0           # scipy.linalg.svd, scipy.linalg.polar
matplotlib>=3.5.0
pyyaml>=6.0
tqdm>=4.62.0
wsl-modelzoo           # pip install wsl-modelzoo (dataset download CLI)
```

### 8.2 External Repositories

| Repository | Purpose | URL |
|------------|---------|-----|
| AllanYangZhou/nfn | NFN orbit structure, WeightSpaceFeatures, CNN Zoo loading | https://github.com/AllanYangZhou/nfn |
| ModelZoos/ModelZooDataset | dataset_base.py PyTorch class for checkpoint loading | https://github.com/ModelZoos/ModelZooDataset |
| tomgoldstein/loss-landscape | trajectory PCA (SVD-based projection) pattern reference | https://github.com/tomgoldstein/loss-landscape |

### 8.3 Prerequisite Hypothesis Dependencies

| Hypothesis | Status | Contribution to H-M2 |
|------------|--------|----------------------|
| H-E1 | VALIDATED (PASS) | Confirmed orbit-PE is accuracy-preserving; nfn layer compatibility |
| H-M1 | VALIDATED (PASS) | Built and validated `OrbitPEComputer`; unified codebase (HAS_ARCH_BRANCHES=False); overhead 1.167x |

**H-M1 code location**: `docs/youra_research/20260521_wsl/h-m1/code/`

---

## 9. Constraints

| Constraint | Value |
|-----------|-------|
| Experiment type | Pure analysis (no gradient computation) |
| Dataset | Small CNN Zoo only (CNN checkpoints with full trajectories) |
| Minimum trajectory length | 10 checkpoints (filter shorter trajectories) |
| Maximum checkpoint subsample | 50 checkpoints per trajectory (memory constraint fallback) |
| Orbit basis dimension | D ≤ 64 (H-M1 token_dim=64) |
| Analysis scope | CIFAR-10-GS (primary) + SVHN-GS (secondary stability check) |

---

## 10. Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| CNN Zoo checkpoints missing full trajectory (epoch 0..50) | Medium | Filter: use only models with complete checkpoints; adapt to available epoch range |
| SVD divergence (NaN in singular values) | Low | Add numerical stability (1e-8 regularization); check for zero-weight layers before SVD |
| Ratio = 0 or 1 (degenerate projection) | Low | Verify orbit_basis spans non-trivial subspace; check var_perm > 0 and var_gl > 0 |
| Memory OOM (200 models × 51 checkpoints) | Medium | Subsample to 100 models × 25 checkpoints; load trajectories sequentially, not in batch |
| H-M1 OrbitPEComputer doesn't export `get_orbit_basis()` | Medium | Implement wrapper if method not present; derive orbit basis from orbit membership vectors |
| ratio < 0.60 (gate fail / pivot) | Low-Medium | Per hypothesis design: PIVOT to hybrid orbit-PE + GL trace features; H-M3 re-scoped |

---

*Generated by Phase 3 PRD Generation (UNATTENDED — inline execution) from Phase 2C experiment brief*
*Source: docs/youra_research/20260521_wsl/h-m2/02c_experiment_brief.md*
*Based on: NFN orbit structure (AllanYangZhou/nfn), trajectory PCA (tomgoldstein/loss-landscape), GL orbit theory (arXiv:2410.04207)*
