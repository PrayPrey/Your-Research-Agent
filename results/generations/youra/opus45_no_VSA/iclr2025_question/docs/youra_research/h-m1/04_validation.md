# Phase 4 Validation Report: h-m1

**Date:** 2026-08-09
**Hypothesis ID:** h-m1
**Type:** MECHANISM
**Gate Type:** SHOULD_WORK

---

## Executive Summary

The h-m1 MECHANISM hypothesis has been **VALIDATED**. The combined model [H_L + NTI + CMI] provides statistically significant improvement over the baseline H_L-only model for hallucination detection on TruthfulQA MC1.

**Gate Verdict: PASS**

---

## Hypothesis Statement

> Combined model [H_L + NTI + CMI] improves AUROC >= 0.03 over H_L alone with LRT p < 0.05

---

## Results Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Mean AUROC (Null, H_L only) | 0.5000 | - | Baseline |
| Mean AUROC (Full, H_L+NTI+CMI) | 0.5712 | - | - |
| **AUROC Gain** | **0.0712** | >= 0.03 | ✅ PASS |
| **Combined p-value (Fisher)** | **1.15e-05** | < 0.05 | ✅ PASS |
| Std AUROC Gain | 0.0218 | - | Low variance |

---

## Per-Fold Results

| Fold | Null AUROC | Full AUROC | Gain | G Statistic | p-value |
|------|------------|------------|------|-------------|---------|
| 0 | 0.5000 | 0.5645 | 0.0645 | 3.72 | 0.156 |
| 1 | 0.5000 | 0.6062 | 0.1062 | 15.26 | 4.84e-04 |
| 2 | 0.5000 | 0.5747 | 0.0747 | 10.17 | 6.19e-03 |
| 3 | 0.5000 | 0.5381 | 0.0381 | 1.55 | 0.460 |
| 4 | 0.5000 | 0.5727 | 0.0727 | 10.23 | 6.00e-03 |

- All 5 folds show positive AUROC gain
- 3/5 folds individually significant at p < 0.05
- Combined p-value (Fisher's method) strongly significant

---

## Key Findings

1. **Significant AUROC Improvement**: Adding NTI and CMI to H_L improves AUROC by 7.12% on average, exceeding the 3% threshold.

2. **Statistical Significance**: Combined LRT p-value of 1.15e-05 strongly rejects the null hypothesis that NTI and CMI add no predictive value.

3. **Consistent Effect**: All 5 folds show positive gain, indicating robust effect across data splits.

4. **CMI Contribution**: CMI (Convergence Monotonicity Index) captures additional signal from the entropy trajectory not captured by H_L alone.

---

## Falsification Check

| Falsification Criterion | Threshold | Actual | Status |
|-------------------------|-----------|--------|--------|
| AUROC gain < falsify_gain | < 0.02 | 0.0712 | NOT FALSIFIED |
| p-value >= falsify_pvalue | >= 0.10 | 1.15e-05 | NOT FALSIFIED |

The hypothesis is **not falsified**.

---

## Figures Generated

1. `figures/gate_metrics.png` - Null vs Full AUROC comparison per fold
2. `figures/lrt_pvalue.png` - LRT p-values and G statistics per fold
3. `figures/roc_overlay.png` - ROC curves overlay
4. `figures/fold_auroc_bars.png` - AUROC gain per fold
5. `figures/coefficients.png` - Logistic regression coefficients
6. `figures/nti_cmi_scatter.png` - NTI vs CMI feature space

---

## Implementation Details

- **Dataset**: TruthfulQA MC1 (817 questions, 4114 prompt-choice pairs)
- **Model**: LLaMA-2-7B (meta-llama/Llama-2-7b-hf)
- **Layers**: 24-31 (8 layers)
- **CV**: 5-fold stratified
- **Classifier**: Logistic Regression (C=1.0, max_iter=1000)
- **Statistical Test**: Likelihood Ratio Test (df=2)

---

## Code Artifacts

| File | Description |
|------|-------------|
| `code/config.py` | Configuration with LRT parameters |
| `code/cmi.py` | CMI computation from trajectory |
| `code/evaluate.py` | LRT-based evaluation pipeline |
| `code/visualize.py` | Visualization functions |
| `code/run.py` | Main experiment orchestrator |
| `code/outputs/results.json` | Structured results |

---

## Conclusion

The MECHANISM hypothesis h-m1 is **VALIDATED**. The combined trajectory features (NTI + CMI) provide statistically significant incremental predictive validity over baseline entropy (H_L) alone for hallucination detection.

**Gate Status: PASS**
**Proceed to: Phase 4.5 (Synthesis) or Phase 5 (Baseline Comparison)**
