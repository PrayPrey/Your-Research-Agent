---
title: "PRD: H-M2 — PCA Concentration Test (Canonicalization vs Raw)"
hypothesis_id: H-M2
hypothesis_type: MECHANISM
tier: FULL
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
date: 2026-08-27
author: Anonymous
source: Phase 2C Experiment Brief (02c_experiment_brief.md)
base_hypothesis: H-M1
---

# Product Requirements Document: H-M2

## 1. Executive Summary

This experiment tests whether PCA of canonicalized weight vectors (Condition D: scaling + sign-flip) explains more property-label variance (R²) than PCA of raw weight vectors (Condition A) on the Schürholt MNIST model zoo. The experiment is a **linear diagnostic study** — no neural network training required. We fit PCA on training-split weight matrices under each condition, then measure R² of LinearRegression from the first k principal components onto three property labels (test_accuracy, gen_gap, lr_recovery) with bootstrap 95% CIs.

**Gate:** SHOULD_WORK — R²_canonical(k=20) > R²_raw(k=20) on ≥2/3 property tasks with non-overlapping bootstrap 95% CIs. Failure → DOCUMENT; proceed to H-M3 regardless.

**Reuses from H-M1:** Local zoo loader (500 MNIST models), canonicalization implementations (scaling + sign-flip M=2), train/test split (450/50, seed=42), bootstrap CI protocol (n_boot=1000).

---

## 2. Problem Statement

H-M1 established that NFT (Condition A) does NOT naturally collapse scaling orbits (gap=+0.024, CI=[0.023, 0.024]), confirming NFT allocates representational capacity to within-orbit variation rather than achieving invariance. The causal claim for YOURA is: canonicalization → geometric concentration → improved property prediction (ρ improvement observed in H-E1).

H-M2 tests the **concentration** link in this causal chain:

- **If canonicalization concentrates geometry**: the first k PCs of canonical weight vectors align more strongly with property-predictive directions → higher R² than raw PCA
- **If no concentration**: R²_canonical ≈ R²_raw → concentration is not the operative mechanism; the causal pathway claim must be revised

**Research Question:** Does PCA of Condition D weight vectors explain significantly more property-label variance than PCA of Condition A weight vectors on the Schürholt MNIST zoo?

---

## 3. Scope

### In Scope
- Local zoo loading (reuse H-M1 `load_local_zoo()`)
- Weight vector flattening to (n_models, 50890)
- Condition A: raw weight vectors (no canonicalization)
- Condition D: scaling (L2 norm per layer) → sign-flip (majority-sign M=2) applied sequentially
- PCA sweep: k ∈ {10, 20, 50}
- LinearRegression R² for 3 property labels × 2 conditions × 3 k values = 18 evaluations
- Bootstrap 95% CI on each R² (n_boot=1000, seed=42)
- Gate comparison: R²_D vs R²_A at k=20, non-overlapping CI check
- Figure generation (5 figures: 1 mandatory gate metric + 4 diagnostic)
- Mechanism precondition verification

### Out of Scope
- NFT training or inference (H-M2 is pure PCA + linear probe)
- Condition B (scaling only) or Condition C (sign-flip only) — only A vs D
- Permutation or other symmetry types
- Hyperparameter search or multiple seeds
- Multi-GPU or distributed execution
- Any model zoo other than Schürholt MNIST local archive

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schürholt MNIST MLP Model Zoo (local archive) |
| Source | Schürholt et al. 2022 — "Model Zoos: A Dataset of Diverse Populations of Neural Network Models" |
| Local Path | `./data/` (same as H-M1) |
| Available size | 500 MNIST models (HuggingFace unavailable — confirmed H-M1) |
| Architecture | 784→64→10 (2-layer MLP, M=2 layer pairs) |
| Weight vector dim | 784×64 + 64 + 64×10 + 10 = **50,890** |
| Labels per model | test_accuracy (continuous), gen_gap (continuous), lr_recovery (continuous) |
| Train/test split | 450 / 50, seed=42 (consistent with H-M1) |
| Download method | Local (no download needed — reuse H-M1 cached data) |

**Loading code (reuse from H-M1):**
```python
# Reuse H-M1 local archive loader
import torch
data = torch.load('./data/mnist_models.pt')
# Returns list of dicts: {'weights': [...], 'test_accuracy': float, ...}
# Reuse H-M1 load_local_zoo() function directly
```

### 4.2 Condition Definitions

| Condition | Description | Canonicalization |
|-----------|-------------|-----------------|
| A | Raw weight vectors | None |
| D | Canonical weight vectors | Scaling (L2-norm per layer) → Sign-flip (majority-sign M=2), sequential |

### 4.3 Labels

| Label | Type | Description |
|-------|------|-------------|
| test_accuracy | Continuous [0,1] | Test accuracy of each MNIST model |
| gen_gap | Continuous | Train accuracy minus test accuracy |
| lr_recovery | Continuous | Learning rate recovery metric (model zoo metadata) |

---

## 5. Functional Requirements

### FR-1: Data Loading and Preprocessing

**FR-1.1:** Load Schürholt MNIST zoo from local archive (`./data/mnist_models.pt`) using H-M1 `load_local_zoo()` function.

**FR-1.2:** Flatten all weight parameters (W1: 784×64, b1: 64, W2: 64×10, b2: 10) into a (500, 50890) weight matrix.

**FR-1.3:** Extract three property label vectors: test_accuracy, gen_gap, lr_recovery — shape (500,) each.

**FR-1.4:** Split into train (450) and test (50) using `sklearn.model_selection.train_test_split(random_state=42)`.

### FR-2: Condition A — Raw Weight PCA

**FR-2.1:** Apply PCA with k ∈ {10, 20, 50} components to raw weight matrix (Condition A). Fit on train split, transform both splits.

**FR-2.2:** For each (k, property_label): fit LinearRegression on (X_train_pca, y_train_prop) and predict on X_test_pca.

**FR-2.3:** Compute R² (sklearn r2_score) on test split for each (k, property_label).

**FR-2.4:** Compute bootstrap 95% CI on each R²: n_boot=1000, seed=42, sampling test indices with replacement.

### FR-3: Condition D — Canonical Weight PCA

**FR-3.1:** Apply scaling canonicalization: divide each layer's weight matrix by its Frobenius norm (per-model, per-layer). Reuse H-M1 `apply_scaling_canon()`.

**FR-3.2:** Apply sign-flip canonicalization (M=2): for each hidden neuron, flip sign of incoming (W1 column) and outgoing (W2 row) weights if majority sign of incoming weights is negative. Reuse H-M1 `apply_sign_flip_canon()`.

**FR-3.3:** Apply PCA with k ∈ {10, 20, 50} to canonicalized weight matrix. Fit on canonicalized train split, transform both.

**FR-3.4:** Repeat FR-2.2–FR-2.4 on Condition D embeddings for all (k, property_label) combinations.

### FR-4: Gate Comparison

**FR-4.1:** For each (k, property_label): compute ΔR² = R²_D - R²_A.

**FR-4.2:** Check non-overlapping CI: `R²_D_CI_low > R²_A_CI_high` for statistical significance.

**FR-4.3:** Gate evaluation at k=20: count how many of 3 property tasks show non-overlapping CI with R²_D > R²_A.

**FR-4.4:** Report gate result: PASS if ≥2/3 tasks pass; FAIL otherwise. Both outcomes produce documented output.

### FR-5: Mechanism Precondition Verification

**FR-5.1:** Verify Condition A ≠ Condition D: `assert not np.allclose(X_A_train, X_D_train)`.

**FR-5.2:** Verify PCA is non-degenerate for both conditions: `explained_variance_ratio_.sum() > 0.01`.

**FR-5.3:** Verify LinearRegression produces finite coefficients.

**FR-5.4:** Print activation indicators and return precondition status.

### FR-6: Figure Generation

**FR-6.1 (Mandatory Gate Figure):** Bar chart — R²_canonical vs R²_raw with 95% CI error bars, for each (k, property_label). Save to `docs/youra_research/h-m2/figures/gate_r2_comparison.png`.

**FR-6.2:** R² vs k curve — line plot for R²_A and R²_D as function of k ∈ {10, 20, 50} per property. Save to `figures/r2_vs_k.png`.

**FR-6.3:** PCA explained variance ratio — cumulative plot: Condition A vs D. Save to `figures/pca_explained_variance.png`.

**FR-6.4:** Bootstrap CI overlap visualization — horizontal CI bars for R²_A and R²_D at k=20 per property. Save to `figures/bootstrap_ci_overlap.png`.

**FR-6.5:** Scatter PC1 vs property label — Condition A vs D side-by-side scatter for test_accuracy. Save to `figures/pc1_vs_property.png`.

---

## 6. Non-Functional Requirements

**NFR-1 Performance:** Full experiment (500 models, PCA sweep, 18 evaluations, n_boot=1000×18 = 18,000 bootstrap fits) must complete in ≤ 5 minutes on CPU.

**NFR-2 Reproducibility:** All random operations seeded with seed=42. No stochastic elements beyond bootstrap sampling.

**NFR-3 Code Quality:** Reuse H-M1 functions without modification where possible. New code ≤ 200 lines total.

**NFR-4 Output:** Save all results to `docs/youra_research/h-m2/results/h_m2_results.json` (structured) and figures to `docs/youra_research/h-m2/figures/`.

**NFR-5 Compatibility:** Python 3.9+, numpy, sklearn, torch (for data loading only). No GPU required.

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | ≥1.21 | Array operations, bootstrap sampling |
| scikit-learn | ≥1.0 | PCA, LinearRegression, r2_score |
| torch | ≥1.9 | Data loading (torch.load) |
| matplotlib | ≥3.4 | Figure generation |
| scipy | ≥1.7 | Statistical utilities (optional) |

### 7.2 External Repositories / Codebases

| Resource | Path | Usage |
|----------|------|-------|
| H-M1 codebase | `docs/youra_research/h-m1/code/` | Reuse: load_local_zoo(), apply_scaling_canon(), apply_sign_flip_canon() |
| Local zoo data | `./data/mnist_models.pt` | Dataset (cached from H-M1 run) |

### 7.3 Hardware

| Resource | Requirement |
|----------|-------------|
| CPU | Standard laptop (≥4 cores) |
| RAM | ≥2 GB (weight matrix: 500×50890×4 bytes ≈ 100 MB) |
| GPU | Not required |

---

## 8. Success Criteria

### Gate Metric (SHOULD_WORK)

| Metric | Target | Evaluation |
|--------|--------|------------|
| R²_D vs R²_A at k=20 | R²_D_CI_low > R²_A_CI_high on ≥2/3 tasks | PASS = proceed as confirmed; FAIL = document and proceed to H-M3 |

### Secondary Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Improvement monotonicity | R²_D(k) − R²_A(k) non-decreasing for k ∈ {10,20,50} | Bonus |
| PCA variance concentration | Cumulative explained variance ratio (D) > (A) for first 20 PCs | Diagnostic |
| All 5 figures generated | Saved to figures/ | Required |

### Mechanism Preconditions (All Must Pass)

| Check | Requirement |
|-------|-------------|
| mechanism_exists | PCA fits successfully on both conditions |
| mechanism_isolatable | `not np.allclose(X_A_train, X_D_train)` |
| baseline_measurable | R² finite on test split for Condition A |

---

## 9. Implementation Notes

### Reuse Strategy (INCREMENTAL from H-M1)

This is an incremental experiment. The following H-M1 functions are reused **without modification**:

- `load_local_zoo(path='./data/mnist_models.pt')` → list of model dicts
- `apply_scaling_canon(weights_flat, layer_shapes)` → (n_models, 50890) canonical array
- `apply_sign_flip_canon(weights_flat, W1_shape, W2_shape)` → (n_models, 50890) canonical array
- `compute_bootstrap_ci(values, n_boot=1000, seed=42)` → (ci_low, ci_high)

H-M2-specific new code:
- `flatten_weights(model_list)` → (n_models, 50890) array + label extraction
- `evaluate_pca_concentration(X_train, X_test, y_train, y_test, k_values)` → nested dict of {k: {r2, ci}}
- `run_h_m2_experiment()` → main orchestration
- Figure generation functions (5 figures)

### Key Implementation Risk

**Small test set (n=50):** R² estimates will have high bootstrap variance. Expected CIs will be wide. Document this limitation prominently in results. The gate is designed for this — non-overlapping CIs despite wide variance constitutes strong evidence.

---

*PRD generated: 2026-08-27 | Phase 3 Step 2 | Unattended mode*
