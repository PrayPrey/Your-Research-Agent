# Product Requirements Document: H-E1
# Permutation Orbit Non-Triviality Analysis in Schurholt MNIST-CNN Model Zoo

**stepsCompleted:** [PRD-1, PRD-2, PRD-3, PRD-4, PRD-5]
**Hypothesis:** H-E1 (EXISTENCE)
**Gate Type:** MUST_WORK
**PRD Version:** 1.0
**Date:** 2026-05-05
**Author:** Anonymous
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## 1. Executive Summary

H-E1 is a data analysis experiment (no model training) that verifies two foundational assumptions required for the NFN Delta-Rho benchmark:

1. **BN-free confirmation:** The Schurholt MNIST-CNN model zoo uses plain feedforward CNNs without BatchNorm layers — a prerequisite for valid permutation symmetry analysis.
2. **Orbit non-triviality:** A non-trivial proportion (>5%) of model pairs with similar test accuracy (|Δacc| < 0.01) exhibit high weight-space distance (cosine_distance > 0.1), confirming that permutation-equivalent weight configurations are prevalent in the zoo.

If both checks pass, the MUST_WORK gate is satisfied and the H-M1 → H-M2 → H-M3 chain can proceed. If either fails, the entire NFN Delta-Rho hypothesis chain requires Phase 2A redesign.

---

## 2. Problem Statement

Feedforward neural networks with L layers of widths n_1, ..., n_L have |S_{n_1}| × ... × |S_{n_L}| symmetry-equivalent weight configurations per function. This means two models with the same learned function can have radically different weight vectors. Before comparing NFN vs. flat MLP encoder performance on accuracy prediction, we must verify:

- The zoo's architecture family (MNIST-CNN) is BN-free (BN breaks the permutation symmetry group structure)
- The zoo contains enough permutation-orbit diversity to make the H-M1/M2 encoder comparison meaningful

---

## 3. Scope

**In Scope:**
- Loading Schurholt MNIST-CNN model zoo checkpoints
- BN-free architecture verification
- Stratified random sampling of 500 model pairs by accuracy decile
- Cosine distance computation between flattened weight vectors
- Orbit candidate proportion computation and gate evaluation
- Visualization: 4 figures (gate metrics bar, cosine distance histogram, accuracy vs. distance scatter, per-decile orbit proportion)

**Out of Scope:**
- Model training or fine-tuning
- NFN or MLP encoder experiments (H-M1/M2/M3)
- CIFAR-10 zoo (H-E1 focuses on MNIST-CNN only)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| **Name** | Schurholt ModelZooDataset — MNIST-CNN Zoo |
| **Source** | Schurholt et al. (2022) arXiv:2209.12892 |
| **GitHub** | https://github.com/ModelZoos/ModelZooDataset |
| **Size** | ~4,100 checkpoints (state_dict + test accuracy labels) |
| **Architecture** | Conv(32)-Conv(64)-FC(128)-FC(10), ReLU, NO BatchNorm |
| **Accuracy Range** | ~0.85–0.99 test accuracy (MNIST) |
| **Splits** | Standard train/val/test from Schurholt et al. |
| **Download Method** | `pip install model-zoo-dataset` OR `git clone https://github.com/ModelZoos/ModelZooDataset` |
| **Local Cache Path** | `./data/model_zoo/` |

**Sampling for Analysis:**
- Use **full zoo** (~4,100 checkpoints) for BN verification and pair sampling pool
- **500 model pairs** for orbit statistics (50 pairs × 10 accuracy deciles), statistically meaningful

### 4.2 No Secondary Datasets

H-E1 uses only the Schurholt MNIST-CNN zoo. No synthetic data. No CIFAR-10 (reserved for H-M3).

---

## 5. Functional Requirements

### FR-1: Dataset Loading
- **FR-1.1:** Load Schurholt MNIST-CNN zoo using `ModelZooDataset` API or direct file loading
- **FR-1.2:** Extract `(state_dict, test_accuracy)` pairs for all checkpoints
- **FR-1.3:** Support both pip package and direct clone loading paths

### FR-2: BN-Free Verification
- **FR-2.1:** Inspect each checkpoint's state_dict keys for BatchNorm parameter names (`bn`, `batch_norm`, `running_mean`, `running_var`)
- **FR-2.2:** `verify_bn_free(state_dict)` returns True if NO BatchNorm keys found
- **FR-2.3:** Run verification on a sample of ≥5 random checkpoints
- **FR-2.4:** Gate check: ALL sampled checkpoints must return True

### FR-3: Weight Flattening
- **FR-3.1:** `flatten_weights(state_dict)` concatenates all weight/bias tensors into a single 1D float tensor
- **FR-3.2:** Handles arbitrary state_dict key names (filter by 'weight' or 'bias' in key)
- **FR-3.3:** Output is CPU float32 tensor

### FR-4: Stratified Pair Sampling
- **FR-4.1:** Bin all ~4,100 checkpoints into 10 accuracy deciles using `np.percentile`
- **FR-4.2:** Within each decile, sample up to 50 pairs with |Δacc| < 0.01
- **FR-4.3:** Total: 500 pairs (10 deciles × 50 pairs)
- **FR-4.4:** Fixed random seed = 42 for reproducibility
- **FR-4.5:** Each pair record: `(model_1, model_2, decile_index)`

### FR-5: Cosine Distance Computation
- **FR-5.1:** `compute_cosine_distance(w1, w2)` = 1 - F.cosine_similarity(w1, w2)
- **FR-5.2:** `is_orbit_candidate` = True if cosine_distance > 0.1
- **FR-5.3:** Store per-pair: `{decile, cosine_dist, is_orbit_candidate}`

### FR-6: Orbit Statistics
- **FR-6.1:** `orbit_proportion` = fraction of 500 pairs where `is_orbit_candidate` = True
- **FR-6.2:** `mean_cos_dist` = mean cosine distance across all pairs
- **FR-6.3:** Per-decile orbit proportion breakdown
- **FR-6.4:** Gate evaluation: `gate_passed = bn_free_confirmed AND (orbit_proportion > 0.05)`

### FR-7: Visualization
- **FR-7.1 (REQUIRED):** Bar chart — gate metrics (orbit_proportion vs. 0.05 threshold, per-decile)
- **FR-7.2:** Histogram — cosine distance distribution for all 500 pairs, colored by decile
- **FR-7.3:** Scatter — |Δacc| vs. cosine_distance for all pairs
- **FR-7.4:** Bar chart — per-decile orbit candidate proportion
- **FR-7.5:** Save all figures to `docs/youra_research/20260505_wsl/h-e1/figures/`

### FR-8: Gate Reporting
- **FR-8.1:** Print gate result: PASS or FAIL
- **FR-8.2:** Print: `BN-free: {bool}`, `Orbit proportion: {float:.3f} (threshold: >0.05)`
- **FR-8.3:** Save results to structured output (JSON or YAML)

---

## 6. Non-Functional Requirements

| NFR | Requirement |
|-----|-------------|
| **Hardware** | CPU sufficient — no GPU required |
| **Runtime** | ≤ 15 minutes on standard CPU |
| **Reproducibility** | Fixed seed=42; deterministic sampling |
| **Memory** | All ~4,100 weight vectors held in RAM (expected ~500MB) |
| **Code Style** | Type-annotated Python, docstrings for public functions |

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Purpose | Version |
|---------|---------|---------|
| `torch` | Weight tensor operations, cosine similarity | ≥1.12 |
| `numpy` | Statistics, percentile, array ops | ≥1.21 |
| `scipy` | Optional: `scipy.stats` for Spearman check | ≥1.7 |
| `matplotlib` | Figure generation | ≥3.5 |
| `model-zoo-dataset` | Schurholt zoo loading | latest |
| `pyyaml` | Results output | ≥5.4 |
| `tqdm` | Progress bars for checkpoint loading | ≥4.60 |

### 7.2 External Repositories

| Repository | URL | Purpose |
|-----------|-----|---------|
| ModelZoos/ModelZooDataset | https://github.com/ModelZoos/ModelZooDataset | Primary data source |
| AvivNavon/equivariant-weight-space-networks | https://github.com/AvivNavon/equivariant-weight-space-networks | Architecture confirmation (BN-free) |

---

## 8. Success Criteria (MUST_WORK Gate)

| Check | Threshold | Expected |
|-------|-----------|---------|
| **P1: BN-free confirmed** | ALL sampled models return True | True (Navon et al. confirms `has_bn: False`) |
| **P2: Orbit proportion** | > 0.05 | 0.3–0.7 (MNIST-CNN zoo is intentionally diverse) |
| **P3: Code runs without error** | No exceptions | Yes |

**Gate PASS condition:** P1 AND P2 AND P3

**Gate FAIL consequence:** Entire H-NFNDeltaRho-v1 causal chain is invalid → Phase 2A redesign required.

---

## 9. Output Artifacts

| Artifact | Path | Description |
|---------|------|-------------|
| Experiment script | `h-e1/code/run_experiment.py` | Main analysis script |
| BN verification module | `h-e1/code/bn_verify.py` | `verify_bn_free()` function |
| Weight analysis module | `h-e1/code/weight_analysis.py` | `flatten_weights()`, `compute_cosine_distance()`, `stratified_pair_sample()`, `compute_orbit_statistics()` |
| Results YAML | `h-e1/results/h_e1_results.yaml` | Gate pass/fail + metrics |
| Figure 1 | `h-e1/figures/gate_metrics.png` | Gate metrics bar chart (REQUIRED) |
| Figure 2 | `h-e1/figures/cosine_dist_histogram.png` | Cosine distance distribution |
| Figure 3 | `h-e1/figures/acc_vs_distance.png` | Accuracy vs. cosine distance scatter |
| Figure 4 | `h-e1/figures/per_decile_proportion.png` | Per-decile orbit proportion |

---

## 10. Traceability

| Requirement | Source |
|------------|--------|
| Dataset: Schurholt MNIST-CNN | Phase 2C §Dataset; Schurholt et al. (2022) |
| BN-free check | Phase 2C §BN Verification; Navon et al. (2023) `has_bn: False` |
| cosine_distance > 0.1 threshold | Phase 2C §Evaluation; Entezari et al. (2022) |
| |Δacc| < 0.01 pairing | Phase 2B 02b_verification_plan.md H-E1 spec |
| 500 pairs, stratified by decile | Phase 2B 02b_verification_plan.md H-E1 protocol |
| >5% orbit proportion gate | Phase 2B 02b_verification_plan.md H-E1 criteria |
| Fixed seed=42 | Phase 2C §Training Protocol |
