# Phase 4 Validation Report: H-E2

**Hypothesis**: CV_PR correlates negatively with ImageNet accuracy (r < -0.3, p < 0.05)  
**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Date**: 2026-08-10

---

## 1. Executive Summary

| Criterion | Required | Observed | Status |
|-----------|----------|----------|--------|
| Pearson r | < -0.3 | +0.6065 | FAIL |
| p-value | < 0.05 | 9.24e-11 | PASS |
| Sample size | >= 80 | 94 | PASS |

**VERDICT: FAIL** — Strong positive correlation observed, opposite to hypothesis.

---

## 2. Experiment Results

### 2.1 Correlation Statistics

| Metric | Value |
|--------|-------|
| Pearson r | +0.6065 |
| Pearson p | 9.24e-11 |
| Spearman r | +0.6368 |
| Spearman p | 5.26e-12 |
| 95% CI | [0.506, 0.703] |
| n | 94 models |

### 2.2 Data Summary

| Variable | Mean | Std |
|----------|------|-----|
| CV_PR | 0.0116 | 0.0057 |
| Top-1 Accuracy | 80.3% | 3.9% |

### 2.3 Match Rate

- **Matched**: 94/100 models (94%)
- **Unmatched**: aimv2_large_patch14_224.apple_pt, convnextv2_atto.fcmae, csatv2.r512_in1k, csatv2_21m.sw_r512_in1k, eva02_base_patch14_224.mim_in22k, gemma4_vit_167m.gemma4_e4b_it

---

## 3. Interpretation

The observed **positive** correlation (r=+0.61) indicates that **higher CV_PR is associated with higher accuracy**, directly contradicting the hypothesis that CV_PR should correlate negatively with accuracy.

### 3.1 Possible Explanations

1. **Confounding variable**: Larger models have more parameters, higher accuracy, AND higher CV_PR variability
2. **Mechanistic reinterpretation**: Higher spectral variability (CV_PR) may reflect richer feature representations, not instability
3. **Sample bias**: 100 models from diverse architectures may not represent a controlled comparison

### 3.2 Implications for Main Hypothesis

The MUST_WORK gate is **FAILED**. The fundamental assumption that CV_PR negatively correlates with model quality is contradicted by empirical evidence. This blocks:
- h-m1 (Threshold experiment)
- h-m2 (Predictor experiment)

---

## 4. Gate Verdict

| Gate Type | Result | Action |
|-----------|--------|--------|
| MUST_WORK | FAIL | Route to Phase 0 for hypothesis reformulation |

The correlation is statistically significant (p < 1e-10) but in the **wrong direction**. The hypothesis as stated is falsified.

---

## 5. Artifacts

| File | Description |
|------|-------------|
| h-e2/code/correlate.py | Analysis script |
| h-e2/results/correlation_results.json | Full statistics |
| h-e2/figures/scatter_cv_pr_vs_accuracy.png | Scatter plot with regression |

---

## 6. Recommendations

1. **Phase 0 re-entry**: Reformulate hypothesis with opposite sign (positive correlation) OR different metric
2. **Partial correlation**: Control for param_count to isolate CV_PR effect
3. **Architecture-stratified analysis**: Check if correlation direction varies by model family (ResNet vs ViT vs ConvNeXt)
