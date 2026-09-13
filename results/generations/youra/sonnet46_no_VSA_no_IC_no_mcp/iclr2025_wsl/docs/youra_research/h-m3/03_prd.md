# Product Requirements Document: H-M3
# SymCanon-WSL — NFT with Weight Symmetry Canonicalization

**Hypothesis:** H-M3
**Type:** MECHANISM (Incremental — extends H-M2)
**Generated:** 2026-08-27
**Phase 2C Source:** docs/youra_research/h-m3/02c_experiment_brief.md

---

## 1. Executive Summary

H-M3 is the primary performance claim test for SymCanon-WSL. It measures whether applying scaling + sign-flip canonicalization (Condition D) before NFT encoding raises Spearman ρ by ≥0.05 on test accuracy compared to raw-weight NFT (Condition A), and whether this improvement is symmetry-specific (ρ_D > ρ_E random-norm control on ≥2/3 tasks). This is a controlled 6-condition NFT training ablation (A, B, C, D, E, F) on the Schürholt MNIST model zoo, plus a frozen-encoder sub-experiment.

---

## 2. Problem Statement

NFT encodes neural network weight vectors to predict properties (accuracy, generalization gap, learning rate recovery). Weight spaces have permutation and scaling symmetries; canonicalizing them before encoding may improve the encoder's signal-to-noise ratio. H-M1 confirmed raw-weight NFT achieves ρ≈0.11; H-M2 confirmed canonicalization geometrically concentrates the weight distribution (higher PCA EVR) but could not measure ρ improvement due to small test set (n=500). H-M3 uses the full ~5,000-model test split to directly measure the ρ improvement.

---

## 3. Hypothesis and Success Criteria

### Gate: SHOULD_WORK (non-blocking)

**P1 (Primary):**
- `ρ_D − ρ_A ≥ 0.05` for test_accuracy
- 95% bootstrap CI of Δρ does not include 0

**P2 (Secondary — symmetry-specificity):**
- `ρ_D > ρ_E` on ≥ 2/3 tasks (test_accuracy, gen_gap, lr_recovery)

**Failure path:** EXPLORE — document full condition table; check B and C for partial improvement; report as negative empirical finding.

---

## 4. Data Specification

### 4.1 Primary Dataset

| Field | Value |
|-------|-------|
| Name | Schürholt MNIST Model Zoo |
| Source | Schürholt et al. 2022 — Model Zoos |
| Loading | `load_zoo()` from `h-m1/code/data_loader.py` (already validated in H-E1/M1/M2) |
| Size | ~50,000 MLP models (784→64→10) |
| Weight dim | 51,850 floats/model (SPLITS=[50176, 64, 640, 10] from actual h-m2 code) |
| Labels | test_accuracy, generalization_gap (gen_gap), learning_rate (lr) |

### 4.2 Dataset Splits

| Split | Size (approx.) | Purpose |
|-------|----------------|---------|
| Train | ~40,000 | NFT training |
| Val | ~5,000 | Early stopping, hyperparameter selection |
| Test | ~5,000 | Final Spearman ρ evaluation (held out until final run) |

> **Note from H-M2:** n=500 test set is underpowered for linear regression. Use the full ~5,000-model test split for ρ evaluation. This is the key lesson from H-M2.

### 4.3 Download / Acquisition

Dataset is already available via the H-M1 codebase loader (`load_zoo()` from `h-m1/code/data_loader.py`). **No separate download task required.**

### 4.4 Preprocessing Conditions

| Condition | Label | Preprocessing | Implementation |
|-----------|-------|---------------|----------------|
| A | Raw weights | None (flatten only) | Identity |
| B | Scale canon | Per-layer Frobenius norm normalization | `apply_condition_b(X)` |
| C | Sign-flip canon | Majority-sign flip for M=2 hidden layer | `apply_condition_c(X)` |
| D | Both (B+C) | Scale then sign-flip | `apply_condition_d(X)` — from h-m2/data_prep.py |
| E | Random norm control | Random unit-norm direction × same scale as B | `apply_condition_e(X, seed=42)` |
| F | flat_mlp + canon | Condition D + linear regressor (no NFT) | `apply_condition_f(X)` + sklearn LinearRegression |

> Condition G (PCA baseline from H-M2) is referenced for reporting but does not require new training. Include G results from h-m2 results.json in final comparison table.

---

## 5. Functional Requirements

### FR-1: Data Pipeline

- FR-1.1: Load zoo using `load_zoo()` from `h-m1/code/data_loader.py`
- FR-1.2: Apply condition-specific preprocessing for all 6 conditions (A–F)
- FR-1.3: Use standard zoo splits: train (~40k), val (~5k), test (~5k)
- FR-1.4: Verify canonicalization activation via `verify_canonicalization_activated()`
- FR-1.5: Support `--condition` CLI flag to select A|B|C|D|E|F

### FR-2: NFT Model (Conditions A–E)

- FR-2.1: NFT architecture from H-E1/H-M1 codebase (Zhou 2023 variant)
- FR-2.2: `CanonicalWeightEncoder(nft, condition)` wrapper: apply preprocessing → encode → predict
- FR-2.3: Output: 3 property predictions (test_accuracy, gen_gap, lr)
- FR-2.4: Train from scratch for each condition (independent runs)
- FR-2.5: Support frozen-encoder sub-experiment: freeze NFT encoder, retrain only final regressor on Conditions B/C/D

### FR-3: Baseline Model (Condition F: flat_mlp + canon)

- FR-3.1: Apply Condition D preprocessing → flatten → sklearn LinearRegression
- FR-3.2: Evaluate with same Spearman ρ metric on test set
- FR-3.3: No NFT training; provides simple linear baseline with canonicalization

### FR-4: Training Protocol

- FR-4.1: Optimizer: Adam, lr=1e-3, weight_decay=1e-4, betas=(0.9, 0.999)
- FR-4.2: LR schedule: ReduceLROnPlateau(patience=5, factor=0.5, min_lr=1e-5)
- FR-4.3: Batch size: 64 models
- FR-4.4: Max epochs: 100 with early stopping (patience=10) on val Spearman ρ
- FR-4.5: Loss: MSE on all 3 property labels jointly
- FR-4.6: Seeds: 3 seeds (42, 123, 456); average ρ across seeds
- FR-4.7: Save checkpoint at best val ρ per condition × seed

### FR-5: Evaluation

- FR-5.1: Spearman ρ via `scipy.stats.spearmanr` on full test set (~5,000 models)
- FR-5.2: Bootstrap 95% CI: 1000 samples, percentile method (BCa if available)
- FR-5.3: Report ρ ± CI for each condition × task (6 conditions × 3 tasks)
- FR-5.4: Compute Δρ = ρ_D − ρ_A and its bootstrap CI
- FR-5.5: P1 check: Δρ(test_accuracy) ≥ 0.05 AND CI excludes 0
- FR-5.6: P2 check: count tasks where ρ_D > ρ_E; pass if ≥ 2/3

### FR-6: Verification / Mechanism Checks

- FR-6.1: `verify_canonicalization_activated(condition, W_before, W_after)` — returns (pass, indicators dict)
- FR-6.2: For Condition B/D: assert norms ~1.0 per layer (mean abs error < 0.01)
- FR-6.3: For Condition C/D: assert ≥95% of hidden neurons have positive majority sign
- FR-6.4: For Condition E: verify weights differ from Condition B (random direction)
- FR-6.5: Log all verification results to experiment log

### FR-7: Frozen-Encoder Sub-Experiment

- FR-7.1: Train NFT on Condition A to convergence; save checkpoint
- FR-7.2: Freeze encoder: `nft.encoder.requires_grad_(False)`
- FR-7.3: Retrain only final regressor on Conditions B, C, D inputs
- FR-7.4: Evaluate frozen-encoder ρ vs full-training ρ (side-by-side bar chart)
- FR-7.5: Purpose: isolates representation quality from training dynamics

### FR-8: Figures (Mandatory)

- FR-8.1: Bar chart: Spearman ρ for Conditions A–F × 3 tasks with 95% CIs (gate metrics)
- FR-8.2: Δρ improvement plot: Δρ vs Condition (B,C,D,E,F relative to A) with CI bars
- FR-8.3: Frozen-encoder vs full-training comparison bar chart
- FR-8.4: Per-task ρ heatmap: 6 conditions × 3 tasks, colored by ρ value
- FR-8.5: Bootstrap CI overlap: CI intervals for ρ_D and ρ_A showing non-overlap criterion
- FR-8.6: Save all figures to `docs/youra_research/h-m3/figures/`

---

## 6. Non-Functional Requirements

- NFR-1: Reproducibility — all runs seeded; results reproducible from `main.py --seed <seed>`
- NFR-2: Runtime — full 6-condition × 3-seed experiment should complete in <24h on single GPU
- NFR-3: Modularity — condition flag (`--condition A|B|C|D|E|F`) selects preprocessing; same NFT code path
- NFR-4: Code reuse — extend h-m2 codebase; do not rewrite validated components
- NFR-5: Results storage — save per-condition × per-seed results to `results.json`

---

## 7. Technical Dependencies

### 7.1 Python Packages

```
torch>=2.0
numpy>=1.24
scipy>=1.10
scikit-learn>=1.3
matplotlib>=3.7
tqdm>=4.65
```

### 7.2 Inherited from Prior Experiments

| Component | Source | Usage |
|-----------|--------|-------|
| `load_zoo()` | `h-m1/code/data_loader.py` | Zoo loading |
| `apply_condition_d()` | `h-m2/code/data_prep.py` | Condition D preprocessing |
| NFT architecture | `h-m1/code/` or `h-e1/code/` | Encoder |
| `bootstrap_spearman()` | Implement anew or reuse from h-m1 | Evaluation |

### 7.3 External Repositories

- Schürholt et al. 2022 Model Zoos: accessed via h-m1 data_loader (no new download needed)
- Zhou 2023 NFT: implemented in h-e1/h-m1 codebase

---

## 8. Ablation Variants Summary

All 6 conditions are first-class experiment variants:

| Condition | Is Primary | Tests |
|-----------|-----------|-------|
| A (raw NFT) | Baseline | Reference ρ≈0.11 |
| B (scale) | Yes | Partial canon |
| C (sign-flip) | Yes | Partial canon |
| D (both) | **Primary** | Full canon — P1 gate |
| E (random norm) | Yes | Symmetry-specificity — P2 gate |
| F (flat_mlp+canon) | Yes | Linear baseline |

---

## 9. Success Criteria Summary

| Criterion | Threshold |
|-----------|-----------|
| P1: Δρ_D ≥ 0.05 | ρ_D − ρ_A ≥ 0.05 on test_accuracy, CI excludes 0 |
| P2: Symmetry-specific | ρ_D > ρ_E on ≥2/3 tasks |
| Mechanism check | All `verify_canonicalization_activated()` checks pass |
| Code runs | All 6 conditions complete without error |
| NFT converges | Val ρ improves first 20 epochs on all conditions |
