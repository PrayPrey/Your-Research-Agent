---
title: "PRD: H-E1 — Orbit Diameter Characterization in Schürholt MNIST Model Zoo"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
date: 2026-08-26
author: Anonymous
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
---

# Product Requirements Document: H-E1

## 1. Executive Summary

This experiment characterizes the geometric diameter of scaling and sign-flip symmetry orbits within the Schürholt MNIST MLP model zoo (~50k trained 2-layer MLPs). The goal is to confirm that symmetry-induced within-orbit variance is geometrically substantial (cosine distance > 0.05 for ≥90% of oracle-constructed orbit pairs), validating the premise that canonicalization has measurable effect. H-E1 is a pure geometric measurement — no neural network training occurs.

**Gate:** MUST_WORK — failure blocks all downstream hypotheses H-M1, H-M2, H-M3, H-C1.

---

## 2. Problem Statement

Trained MLP weight vectors from the Schürholt zoo are stored in raw form with no canonical normalization. Scaling symmetry (per-neuron positive rescaling) and sign-flip symmetry (±1 per-neuron flip for ReLU MLPs) each produce infinite/exponential families of functionally identical weight vectors. If orbit diameters are negligible, canonicalization adds no value. If substantial, it motivates the YOURA canonicalization research direction.

**Research Question:** Are scaling and sign-flip symmetry orbit diameters non-negligible (cosine distance > 0.05) in the Schürholt MNIST zoo?

---

## 3. Scope

### In Scope
- Schürholt MNIST zoo weight vector loading
- Oracle orbit construction (scaling, sign-flip, combined symmetry transforms)
- Pairwise cosine and L2 distance computation
- Statistical aggregation (mean, std, percentiles, bootstrap 95% CI)
- Figure generation (3 figures + 1 gate metric bar chart)

### Out of Scope
- Model training or fine-tuning
- NFT/transformer encoders (H-M1 concern)
- Permutation symmetry (not in H-E1 scope)
- Multi-GPU or distributed execution
- Other zoo architectures (only 784→64→10 MLP)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schürholt MNIST MLP Model Zoo |
| Source | Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" |
| HuggingFace Identifier | `ModelZoos/ModelZooDataset` config `mnist-mlp` |
| Fallback | Direct download from https://github.com/ModelZoos/ModelZooDataset releases |
| Size | ~50,000 trained 2-layer MLP models |
| Architecture | 784→64→10 (ReLU activation, no BatchNorm) |
| Weight vector dim | D = 784×64 + 64 + 64×10 + 10 = **51,850** |
| Labels per model | test_accuracy, generalization_gap, learning_rate |
| Splits | Pre-defined train/val/test from Schürholt 2022 |
| Download method | Automatic (HuggingFace datasets library) |

**Loading code:**
```python
from datasets import load_dataset
zoo = load_dataset("ModelZoos/ModelZooDataset", "mnist-mlp", split="train")
# Each row: {"weights": List[float] (len=51850), "test_acc": float, ...}
```

**Preprocessing:**
- Load raw weight vectors as flat tensors — NO normalization (measuring raw orbit geometry)
- Convert to `torch.float32` tensors of shape `(D,)` per model
- Sample N_models = 1,000 from train+val split (for diversity)
- Verify D = 51,850 for each loaded model; fail fast on mismatch

**Augmentation:** None.

**Synthetic Data Policy:** REAL data only. Schürholt zoo models genuinely trained on MNIST.

### 4.2 No Static Baselines

H-E1 uses no held-out test set in the ML sense. The "test set" is 1,000 sampled zoo models × 5 orbit members × 3 symmetry types = 15,000 distance measurements per metric.

---

## 5. Functional Requirements

### FR-1: Data Loading and Validation
- **FR-1.1** Load Schürholt MNIST zoo via HuggingFace datasets with automatic download
- **FR-1.2** Fallback to local parquet/pkl files if HuggingFace identifier fails
- **FR-1.3** Verify weight vector dimension D = 51,850 for each loaded model; raise `ValueError` if mismatch
- **FR-1.4** Verify ReLU architecture (no BatchNorm layers); fail early if unexpected architecture detected
- **FR-1.5** Sample N_models = 1,000 models from train+val split using fixed seed = 42

### FR-2: Orbit Construction

For each of 3 symmetry types (scaling, signflip, combined), construct K=5 orbit members per model:

- **FR-2.1 Scaling orbit**: For 2-layer MLP (W1: 784×64, b1: 64, W2: 64×10, b2: 10):
  - Sample per-neuron scales α_i ~ 10^Uniform(-1, 1) (log-uniform over [0.1, 10])
  - Apply: W1[:,i] *= α_i, b1[i] *= α_i, W2[i,:] /= α_i (inverse on output)
  - b2 unchanged

- **FR-2.2 Sign-flip orbit**: Sample signs s_i ∈ {-1, +1} uniformly per hidden neuron:
  - Apply: W1[:,i] *= s_i, b1[i] *= s_i, W2[i,:] *= s_i

- **FR-2.3 Combined orbit**: Apply scaling then sign-flip (sequential composition)

- **FR-2.4** Each of K=5 orbit members uses a distinct random seed (base_seed + k)
- **FR-2.5** Verify orbit member shape matches original: `orbit.shape == (51850,)`
- **FR-2.6** Verify orbit member is non-trivially different: cosine_dist > 1e-6 (fail if ≡ original)

### FR-3: Distance Computation

- **FR-3.1 Cosine distance**: `1 - dot(v1/‖v1‖, v2/‖v2‖)` with ε=1e-8 denominator guard
- **FR-3.2 L2 distance**: `‖v1 - v2‖₂`
- **FR-3.3** Compute both metrics for all 15,000 pairs per metric
- **FR-3.4** Store results in structured dict: `{symmetry_type: {"cosine": [...], "l2": [...]}}`

### FR-4: Statistical Aggregation

For each symmetry type:
- **FR-4.1** Compute: mean, std, 5th/95th percentiles of cosine distances
- **FR-4.2** Compute fraction of pairs with cosine_dist > 0.05 (threshold)
- **FR-4.3** Bootstrap 95% CI for mean cosine distance (n_boot=1000, seed=42)
- **FR-4.4** Log all statistics to stdout in structured format

### FR-5: Success Criterion Evaluation

- **FR-5.1** Evaluate PoC gate: `mean_cosine_dist_scaling > 0.05` AND `fraction_above_threshold_scaling ≥ 0.90` AND `bootstrap_CI_lower > 0`
- **FR-5.2** Report gate result (PASS/FAIL) with supporting statistics to stdout
- **FR-5.3** Write JSON results file: `docs/youra_research/h-e1/results.json`

### FR-6: Visualization

Four figures saved to `docs/youra_research/h-e1/figures/`:

- **FR-6.1 Gate Metric Bar Chart** (`fig_gate_metrics.png`): Mean cosine distance per symmetry type vs. threshold line at 0.05. Error bars = bootstrap 95% CI.
- **FR-6.2 Orbit Diameter Distribution** (`fig_orbit_distribution.png`): Histogram of cosine distances for all 3 symmetry types overlaid. Vertical line at 0.05 threshold.
- **FR-6.3 L2 vs Cosine Scatter** (`fig_l2_vs_cosine.png`): Scatter of L2 vs cosine distance, color-coded by symmetry type.
- **FR-6.4 Scale Factor vs Orbit Diameter** (`fig_scale_vs_diameter.png`): Scatter of max(α_i, 1/α_i) vs cosine distance for scaling orbits.

All figures: matplotlib, saved as PNG at 150 DPI, with axis labels and titles.

### FR-7: Mechanism Verification Logging

- **FR-7.1** Log `"Orbit member constructed: cosine_dist={val:.4f}"` per construction
- **FR-7.2** Log mechanism verification dict per symmetry type (shape_preserved, nonzero_distance, above_threshold)
- **FR-7.3** Log final gate pass/fail with all three sub-conditions

### FR-8: Ablation Variants (All Required)

| Variant | Description |
|---------|-------------|
| Scaling only | FR-2.1 applied alone |
| Sign-flip only | FR-2.2 applied alone |
| Combined | FR-2.3 (scaling then signflip) |

All 3 variants are PRIMARY measurements, not optional ablations. All must be computed and reported.

---

## 6. Non-Functional Requirements

- **NFR-1 Reproducibility**: Fixed seed = 42 everywhere; all random state controlled
- **NFR-2 Runtime**: Complete in < 10 minutes on CPU (1,000 models × 5 members × 3 types = 15k distance computations — trivially fast)
- **NFR-3 Memory**: Peak memory < 2GB (weight vectors are float32, 51850 × 1000 × float32 ≈ 200MB)
- **NFR-4 Fail-fast**: Architecture mismatch or D≠51850 → immediate error with clear message
- **NFR-5 No training dependencies**: No CUDA required; pure CPU NumPy/PyTorch sufficient

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `torch` | ≥1.13 | Tensor operations, orbit construction |
| `numpy` | ≥1.21 | Statistics, bootstrap CI |
| `scipy` | ≥1.7 | stats (quantile computation) |
| `datasets` | ≥2.0 | HuggingFace zoo loading |
| `matplotlib` | ≥3.5 | Figure generation |
| `tqdm` | ≥4.0 | Progress bars |

### 7.2 External Repositories (Reference Only)

| Repo | URL | Use |
|------|-----|-----|
| ModelZoos/ModelZooDataset | https://github.com/ModelZoos/ModelZooDataset | Fallback data download |

---

## 8. Success Criteria

### Primary Gate (MUST_WORK)

| Criterion | Threshold | Metric |
|-----------|-----------|--------|
| Mean cosine distance (scaling) | > 0.05 | `mean_cosine_dist_scaling` |
| Fraction of pairs above threshold | ≥ 90% | `fraction_above_0.05_scaling` |
| Bootstrap CI lower bound | > 0 | `ci_lower_scaling` |

### Supporting Evidence (Informational)

| Criterion | Expected |
|-----------|----------|
| Mean cosine distance (signflip) | > 0.05 |
| Mean cosine distance (combined) | > 0.10 (combined effect) |
| All orbit members non-trivial | cosine_dist > 1e-6 for 100% |

---

## 9. File Structure

```
docs/youra_research/h-e1/
├── 03_prd.md                  (this file)
├── 03_architecture.md
├── 03_logic.md
├── 03_config.md
├── 03_tasks.yaml
├── results.json               (Phase 4 output)
├── figures/
│   ├── fig_gate_metrics.png
│   ├── fig_orbit_distribution.png
│   ├── fig_l2_vs_cosine.png
│   └── fig_scale_vs_diameter.png
└── code/
    ├── main.py
    ├── data_loader.py
    ├── orbit_construction.py
    ├── distance_metrics.py
    ├── statistics.py
    └── visualization.py
```

---

## 10. Phase 2C Completeness Verification

| Phase 2C Item | Captured in PRD |
|---------------|-----------------|
| Dataset: Schürholt MNIST zoo | FR-1, Section 4.1 |
| Baseline: raw weight representation | FR-2 (orbit from original) |
| Scaling orbit construction | FR-2.1 |
| Sign-flip orbit construction | FR-2.2 |
| Combined orbit (ablation variant) | FR-2.3, FR-8 |
| N_models=1000, K=5 | FR-1.5, FR-2.4 |
| Cosine + L2 distance metrics | FR-3 |
| Bootstrap 95% CI | FR-4.3 |
| Gate success threshold 0.05 | FR-5, Section 8 |
| 4 required figures | FR-6 |
| Mechanism verification logging | FR-7 |
