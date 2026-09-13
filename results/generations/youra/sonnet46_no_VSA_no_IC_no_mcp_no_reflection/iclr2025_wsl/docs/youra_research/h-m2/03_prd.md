# Product Requirements Document: h-m2
# Differential Advantage of Permutation-Equivariant Encoders on Generalization Gap vs. Test Accuracy

**Hypothesis ID:** h-m2
**Type:** MECHANISM (INCREMENTAL — extends h-m1)
**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Phase:** 3 — Implementation Planning
**Status:** DRAFT

---

## 1. Executive Summary

This experiment tests whether permutation-equivariant weight-space encoders (DWSNet, NFT, GNN) exhibit a *target-specific* differential advantage on generalization gap prediction compared to test accuracy prediction. The hypothesis claims that equivariant architectural inductive biases are disproportionately beneficial for predicting generalization gap (which encodes overfitting signal distributed across the full weight tensor) relative to test accuracy (which is more position-recoverable). The experiment continues directly from H-M1 by reusing all gap-target checkpoints and adding a symmetric test_acc training run under identical protocol.

**Gate (MUST_WORK):** Δ(encoder) > 0.02 Spearman units for ≥2 of {DWSNet, NFT, GNN}, where:
```
Δ(encoder) = [Spearman(gap, encoder) − Spearman(gap, FlatMLP)]
           − [Spearman(test_acc, encoder) − Spearman(test_acc, FlatMLP)]
```

---

## 2. Problem Statement

H-M1 demonstrated that NFT achieves Spearman(gap)=0.5752 vs. FlatMLP's 0.5330 (+0.0422 Δ_gap). However, it is unknown whether this advantage is specific to gap prediction or whether equivariant encoders improve equally on any regression target. If equivariant encoders improve test_acc prediction by a similar amount, the H-M1 finding is a generic encoder quality improvement, not a mechanism tied to overfitting signal structure.

H-M2 isolates this by computing the differential advantage Δ(encoder) — the excess gap improvement over the simultaneous test_acc improvement. A positive Δ for equivariant encoders would confirm that equivariance specifically exploits gap's distributed weight-space signal.

---

## 3. Scope and Boundaries

### In Scope
- Train all 4 encoders (FlatMLP, DWSNet, NFT, GNN) on test_acc target using identical H-M1 protocol
- Reuse H-M1 gap checkpoints and gap Spearman values (no re-training for gap target)
- Compute Δ(encoder) for each equivariant encoder
- Compute partial Spearman(NFT_pred_gap, true_gap | true_test_acc) as secondary metric P3
- Bootstrap 95% CI on Δ values (N=1000 resamples over top-5 configurations)
- Generate 4 required figures

### Out of Scope
- Re-training any encoder on gap target (h-m1 checkpoints are canonical)
- Architecture modifications to any encoder
- New datasets or splits
- Hyperparameter search on gap target

---

## 4. Data Specification

### Primary Dataset
- **Name:** Unterthiner CIFAR-10 CNN Model Zoo
- **Source:** Unterthiner et al. 2020 (arxiv:2002.11448), public release
- **Location:** `./data/unterthiner_zoo/` (already downloaded from H-M1)
- **N:** ~10,000 trained CNN models
- **D:** 33,890 weight parameters per model (flattened, sorted)
- **Splits:** 80/10/10 (train/val/test), seed=42 — MUST reuse H-M1 split identically
  - N_train = 8,000, N_val = 1,000, N_test = 1,000

### Prediction Targets
| Target | Description | Source |
|--------|-------------|--------|
| `generalization_gap` | train_acc − test_acc | H-M1 checkpoints (reused, not retrained) |
| `test_acc` | Model test accuracy on CIFAR-10 | NEW — all 4 encoders trained here |

### Target Correlation
- Spearman(gap, −test_acc) = −0.1422 (H-E1 A1 audit) — targets carry largely independent information; gap and test_acc are suitable as distinct regression targets.

### Loading Code
```python
weights, labels = load_zoo(
    zoo_path="./data/unterthiner_zoo/",
    targets=["generalization_gap", "test_acc"],
    split="test",
    seed=42
)
gap_labels = labels["generalization_gap"]
test_acc_labels = labels["test_acc"]
```

---

## 5. Functional Requirements

### FR-1: Environment Setup
- FR-1.1: Python environment with torch, scipy, sklearn, numpy, matplotlib
- FR-1.2: All H-M1 encoder implementations available (DWSNet, NFT, GNN, FlatMLP)
- FR-1.3: H-M1 gap checkpoints accessible at `h-m1/checkpoints/`

### FR-2: Dataset Loading
- FR-2.1: Load Unterthiner zoo from `./data/unterthiner_zoo/`
- FR-2.2: Extract both `generalization_gap` and `test_acc` label columns
- FR-2.3: Apply identical 80/10/10 split with seed=42 as H-M1
- FR-2.4: Verify N_test=1,000 models available for evaluation

### FR-3: Baseline Encoder (FlatMLP) — Test Accuracy Target
- FR-3.1: Train FlatMLP (D=33890 → [512,512] → scalar) on test_acc target
- FR-3.2: 3-trial random LR search in [5e-4, 2e-3], AdamW, batch=64, 100 epochs
- FR-3.3: Early stopping on val Spearman(test_acc); select best trial
- FR-3.4: Save checkpoint to `h-m2/checkpoints/flat_mlp_testacc_best.pt`
- FR-3.5: Evaluate Spearman(test_acc) on held-out test split; report with 95% CI

### FR-4: DWSNet Encoder — Test Accuracy Target
- FR-4.1: Train DWSNet (same architecture as H-M1) on test_acc target
- FR-4.2: Identical protocol to FR-3 (3-trial, AdamW, batch=64, 100 epochs, seed=42)
- FR-4.3: Save checkpoint to `h-m2/checkpoints/dws_net_testacc_best.pt`
- FR-4.4: Evaluate Spearman(test_acc) on test split; report with 95% CI

### FR-5: NFT Encoder — Test Accuracy Target
- FR-5.1: Train NFT (same architecture as H-M1) on test_acc target
- FR-5.2: Identical protocol to FR-3
- FR-5.3: Save checkpoint to `h-m2/checkpoints/nft_testacc_best.pt`
- FR-5.4: Evaluate Spearman(test_acc) on test split; report with 95% CI

### FR-6: GNN Encoder — Test Accuracy Target
- FR-6.1: Train GNN (same architecture as H-M1) on test_acc target
- FR-6.2: Identical protocol to FR-3
- FR-6.3: Save checkpoint to `h-m2/checkpoints/gnn_testacc_best.pt`
- FR-6.4: Evaluate Spearman(test_acc) on test split; report with 95% CI

### FR-7: Differential Advantage Computation
- FR-7.1: Load H-M1 gap Spearman values from h-m1 results (FlatMLP=0.5330, DWSNet=0.4881, NFT=0.5752, GNN=0.3747)
- FR-7.2: For each equivariant encoder {DWSNet, NFT, GNN}:
  - `gap_improvement = Spearman(gap, enc) − Spearman(gap, FlatMLP)`
  - `acc_improvement = Spearman(test_acc, enc) − Spearman(test_acc, FlatMLP)`
  - `Δ(enc) = gap_improvement − acc_improvement`
- FR-7.3: Count N_pass = number of encoders with Δ > 0.02
- FR-7.4: Gate check: N_pass ≥ 2 → PASS; else FAIL (report with full Δ values)
- FR-7.5: Bootstrap 95% CI on Δ for each encoder (N=1000 resamples, top-5 trial configs)

### FR-8: Secondary Metric — Partial Spearman (P3)
- FR-8.1: Compute Spearman(NFT_pred_gap_residuals, true_gap_residuals | true_test_acc)
- FR-8.2: Residuals computed by regressing out rank(true_test_acc) from both NFT gap predictions and true gap labels
- FR-8.3: Report r and p-value; success if r > 0 and p < 0.05

### FR-9: Mechanism Verification Check
- FR-9.1: All 4 encoders produce test_acc predictions (no NaN/inf)
- FR-9.2: FlatMLP Spearman(test_acc) in expected range [0.75, 0.95]
- FR-9.3: NFT gap consistency check: |Spearman(gap, NFT) − 0.5752| < 0.05
- FR-9.4: All Δ values non-null and finite

### FR-10: Visualization
- FR-10.1 (MANDATORY): Gate metrics bar chart — Δ(encoder) for {DWSNet, NFT, GNN} with threshold line at Δ=0.02
- FR-10.2: Dual-target Spearman comparison — side-by-side bars for gap and test_acc per encoder (4×2)
- FR-10.3: Δ decomposition plot — stacked bar showing gap_improvement and acc_improvement components per encoder
- FR-10.4: Partial correlation scatter — NFT pred_gap residuals vs. true_gap residuals (P3 visualization)
- FR-10.5: Bootstrap CI error bar plot — Δ(encoder) ± 95% CI for all 3 equivariant encoders
- FR-10.6: Save all figures to `h-m2/figures/`

### FR-11: Results Reporting
- FR-11.1: Print per-encoder results table (encoder, Spearman(gap), Spearman(test_acc), gap_imp, acc_imp, Δ)
- FR-11.2: Print gate result (N_pass/3, PASS/FAIL)
- FR-11.3: Save results to `h-m2/04_results.json` with all values

---

## 6. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds fixed at 42 (matching H-M1/H-E1)
- Identical data split to H-M1 — split must not be regenerated
- Results must be deterministic across runs with same seed

### NFR-2: Computational Budget
- 3-trial random search per encoder × 4 encoders = 12 training runs total
- Expected wall time: ~30 minutes (matching H-M1's 27.4 min)
- Checkpoint saves after each encoder completes

### NFR-3: Code Reuse
- Maximize reuse of H-M1 codebase (found in `h-m1/code/`)
- Only change: `target="test_acc"` in training loop
- Do NOT copy encoder implementations — import from H-M1 code

### NFR-4: Statistical Validity
- Report all Spearman values with 95% CI
- Bootstrap CI on Δ with N=1000 resamples
- Do not selectively report only favorable results

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=1.13
scipy>=1.9
scikit-learn>=1.1
numpy>=1.23
matplotlib>=3.6
pyyaml>=6.0
```

### 7.2 H-M1 Artifacts (Pre-existing)
| Artifact | Path | Usage |
|----------|------|-------|
| Gap checkpoints | `h-m1/checkpoints/*.pt` | Spearman(gap) values (reused from H-M1 results) |
| H-M1 gap Spearman values | `h-m1/04_results.json` | Direct input to Δ formula |
| Encoder implementations | `h-m1/code/models/` | Import for test_acc training |
| Zoo data | `./data/unterthiner_zoo/` | Already downloaded |
| Data pipeline | `h-m1/code/data_loader.py` | Reuse with target extension |

### 7.3 Reference Papers
- Unterthiner et al. 2020 (arxiv:2002.11448) — FlatMLP, zoo, test_acc baseline
- Navon et al. 2023 (arxiv:2301.12780) — DWSNet test_acc expected ≈ 0.90
- Zhou et al. 2023 (NeurIPS) — NFT test_acc expected ≈ 0.90–0.92
- Kofinas et al. 2024 — GNN test_acc expected ≈ 0.88–0.90

---

## 8. Success Criteria

| Criterion | Threshold | Type |
|-----------|-----------|------|
| Training complete | All 4 encoders produce test_acc predictions | Required |
| Gate (primary) | Δ > 0.02 for ≥2 of {DWSNet, NFT, GNN} | MUST_WORK |
| Secondary (P3) | Partial Spearman(NFT) > 0, p < 0.05 | Informational |
| Reproducibility | NFT gap consistency within ±0.05 of 0.5752 | Required |
| Budget | Total tasks ≤ 30 (FULL tier) | Required |

### Expected Values
| Encoder | Spearman(test_acc) expected | acc_improvement | gap_improvement | Expected Δ |
|---------|----------------------------|-----------------|-----------------|------------|
| FlatMLP | 0.85–0.88 | baseline | baseline | — |
| DWSNet | ~0.90 | ~+0.04 | −0.0449 | ≈ −0.08 |
| NFT | ~0.90–0.92 | ~+0.04–0.06 | +0.0422 | ≈ −0.02 to 0.00 |
| GNN | ~0.88–0.90 | ~+0.02–0.04 | −0.1583 | ≈ −0.18 |

**Critical Note:** Based on pre-computation, gate passage is difficult — this is the scientific question. Results must be reported regardless of gate outcome.

---

## 9. Risk Assessment

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Gate fails (Δ ≤ 0.02 for all encoders) | Medium-High | Report fully; document as mechanism not confirmed |
| NFT test_acc training unstable | Low | H-M1 found NFT hyperparameter-sensitive; use same LR range |
| H-M1 gap Spearman inconsistency | Low | Sanity check NFT gap vs 0.5752 ± 0.05 |
| Data split mismatch | Low | Use exact seed=42 and same split code as H-M1 |

---

*stepsCompleted: [FR extraction, scope definition, data spec, functional requirements, NFRs, dependencies, success criteria]*
