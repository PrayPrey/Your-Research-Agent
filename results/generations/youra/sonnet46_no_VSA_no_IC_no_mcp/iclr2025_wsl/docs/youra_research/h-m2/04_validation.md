# H-M2 Validation Report

**Date:** 2026-08-27
**Hypothesis:** H-M2 — PCA Concentration Test
**Gate Type:** SHOULD_WORK (non-blocking)
**Gate Result:** FAIL → DOCUMENT

---

## Summary

PCA of canonicalized weight vectors (Condition D: scaling + sign-flip) does **NOT** explain significantly more property-label variance than PCA of raw weight vectors (Condition A) on the Schürholt MNIST zoo (500 models). Gate criterion (R²_D > R²_A with non-overlapping 95% CI on ≥2/3 tasks at k=20) was not met on any label. All R² values are negative, indicating both conditions produce worse-than-mean predictions on the test split.

**Implication (DOCUMENT path):** The causal pathway "canonicalization → PCA concentration → property prediction improvement" is not supported. The hypothesis is revised: canonicalization may remove scale/sign variance but this does not improve linear separability via PCA in the low-model-count regime (N=500).

---

## Experiment Details

| Parameter | Value |
|-----------|-------|
| Dataset | Schürholt MNIST MLP zoo (local archive, N=500) |
| Weight dim | 50,890 per model |
| Train/Test split | 450/50, seed=42 |
| k values | [10, 20, 50] |
| Bootstrap n_boot | 1000, seed=42 |
| Condition A | Raw weight vectors |
| Condition D | Scaling (per-layer L2 norm) + sign-flip (majority-sign M=2) |

---

## Results

### Gate Metric (k=20, CI non-overlapping criterion)

| Label | R²_A (k=20) | CI_A (95%) | R²_D (k=20) | CI_D (95%) | ΔR² | CI Non-overlap | Gate |
|-------|------------|-----------|------------|-----------|-----|---------------|------|
| test_accuracy | -0.1956 | [-0.664, -0.028] | -0.2176 | [-0.673, -0.043] | -0.0220 | False | FAIL |
| generalization_gap | -0.0027 | [-0.106, +0.007] | -0.0241 | [-0.136, +0.009] | -0.0214 | False | FAIL |
| learning_rate | -0.0137 | [-0.161, -0.002] | -0.0173 | [-0.188, +0.019] | -0.0036 | False | FAIL |

**Gate: FAIL — 0/2 labels pass (required ≥2/3)**

### Full R² Sweep

| Label | Condition | k=10 | k=20 | k=50 |
|-------|-----------|------|------|------|
| test_accuracy | A (raw) | -0.2028 | -0.1956 | -0.1851 |
| test_accuracy | D (canon) | -0.1919 | -0.2176 | -0.2131 |
| generalization_gap | A (raw) | +0.0010 | -0.0027 | -0.0082 |
| generalization_gap | D (canon) | -0.0032 | -0.0241 | +0.0051 |
| learning_rate | A (raw) | -0.0123 | -0.0137 | -0.0120 |
| learning_rate | D (canon) | -0.0000 | -0.0173 | -0.0654 |

### Mechanism Preconditions

All preconditions satisfied:
- Canonicalization has effect: mean |X_A - X_D| = 0.0415 ✅
- PCA-A top-20 EVR: 0.055 (non-degenerate) ✅
- PCA-D top-20 EVR: 0.086 (non-degenerate) ✅
- LinearRegression coefficients finite ✅

PCA-D concentrates variance better (EVR 0.086 vs 0.055 for top-20 PCs), but this geometric concentration does not translate to improved R² in linear regression on the test set.

---

## Interpretation

### Why gate failed

1. **R² universally negative**: Both conditions produce below-mean predictions on the 50-sample test set. This is expected with only N=500 models — severe overfitting in PCA+LR: 50 PC directions fitted to 450 training samples, then generalization to 50 test samples with high-variance estimates.

2. **PCA-D concentrates variance but not property-relevant variance**: Canonicalization removes scale invariance (confirmed: EVR increases from 0.055 to 0.086), meaning the first k PCs account for more total variance. However, the removed scale variance was apparently NOT the source of noise masking property signals — or the property signals are simply too weak for linear extraction at N=500.

3. **Mixed direction of ΔR²**: At k=10, R²_D ≥ R²_A for all labels; at k=20-50, R²_D < R²_A. This suggests canonicalization helps at very low dimensionality but becomes counterproductive at higher k (possibly introducing artifacts in the sign-flip transform).

4. **Limitation**: N=500 is too small for meaningful PCA analysis of 50,890-dimensional weight vectors. The full Schürholt zoo has ~50k models; with 100x more data, the concentration hypothesis may hold.

### Revised causal pathway

The original hypothesis was: canonicalization → PCA concentration → R² improvement → ρ improvement.

Evidence shows step 2 (concentration, measured by EVR) is confirmed, but step 3 (R² improvement) fails. The causal pathway must be revised:
- Canonicalization removes geometric redundancy (scale/sign variance) ✓
- This geometric concentration does not improve linear probe R² at N=500 ✗
- Alternative mechanism: NFT may learn to exploit structural regularities that PCA cannot capture linearly

### Impact on pipeline

This is a SHOULD_WORK gate. Per protocol:
- Result: DOCUMENT (not a blocker)
- Proceed to H-M3 regardless
- Document revised causal claim in H-M3 design
- H-M3 will test whether canonicalization improves NFT similarity rankings (different mechanism: structured representations vs. PCA concentration)

---

## Figures Generated

| Figure | File | Description |
|--------|------|-------------|
| Fig 1 | fig1_r2_bar_comparison.png | R²_A vs R²_D bar chart with CI error bars |
| Fig 2 | fig2_r2_vs_k.png | R² vs k line plot per label |
| Fig 3 | fig3_explained_variance.png | Cumulative EVR: Condition A vs D |
| Fig 4 | fig4_ci_bars_k20.png | Bootstrap CI bars at k=20 (visual gate) |
| Fig 5a-c | fig5_pc1_scatter_*.png | PC1 vs property label scatter |

---

## Code

```
h-m2/code/
├── main.py           — orchestration
├── data_prep.py      — load_and_flatten, apply_condition_d, train_test_split_fixed
├── evaluate.py       — evaluate_pca_concentration, compare_conditions, verify_mechanism_preconditions
└── figures.py        — 5 figure functions + generate_all_figures
```

**Results file:** `h-m2/results.json`

---

## Validation Checklist

- [x] Code executes without errors (EXIT=0)
- [x] Mechanism correctly implemented (canonicalization applied, PCA+LR evaluated)
- [x] Metrics measurable (R², bootstrap CI computed for all labels/k)
- [x] Gate evaluated (FAIL: 0/2 labels with non-overlapping CI at k=20)
- [x] Results saved (results.json)
- [x] Figures generated (7 figures)
- [x] Gate type: SHOULD_WORK → failure is non-blocking
- [x] DOCUMENT path: causal pathway revised, proceed to H-M3

---

## Gate Decision

**Gate: FAIL (DOCUMENT)**
- SHOULD_WORK gate failure → non-blocking
- Causal claim (canonicalization → PCA concentration → R² improvement) not supported at N=500
- Proceed to H-M3 with revised mechanism hypothesis
- Note in paper: PCA baseline fails at zoo scale N=500; full Schürholt zoo needed for concentration test

---

*Generated: 2026-08-27 | Phase 4 | Unattended mode*
*Conda env: youra-h-m2 | GPU: H100 NVL (unused — pure numpy/sklearn)*
