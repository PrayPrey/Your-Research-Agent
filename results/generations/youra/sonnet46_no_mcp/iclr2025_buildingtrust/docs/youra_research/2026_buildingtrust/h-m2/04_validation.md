# H-M2 Validation Report

**Hypothesis:** Epistemic composite (ECE + TruthfulQA% + Brier) predicts top-quartile AdvGLUE failure
**Gate Type:** SHOULD_WORK
**Gate Result:** PARTIAL
**Generated:** 2026-04-30T14:45:10.558768Z

---

## Gate Criteria

| Criterion | Value | Threshold | Result |
|-----------|-------|-----------|--------|
| partial ρ(ECE, AdvGLUE\|MMLU) | -0.7185 | ≥ 0.40 (abs) | ✅ PASS |
| BCa 95% CI excludes zero | [-0.8822, -0.3862] | CI excl. zero | ✅ PASS |
| LOO-AUC composite | 0.7386 | ≥ 0.70 | ✅ PASS |
| ΔR² (composite - baseline) | 0.0511 | ≥ 0.10 | ❌ FAIL |
| ΔR² CI excludes zero | [-0.1944, 0.4492] | CI lo > 0 | ❌ FAIL |

---

## Key Metrics

| Metric | Value |
|--------|-------|
| partial ρ(ECE, AdvGLUE\|MMLU) | -0.7185 (BCa 95% CI [-0.8822, -0.3862]) |
| partial ρ(ECE, ANLI\|MMLU) | -0.6667 (BCa 95% CI [-0.8187, -0.3852]) |
| LOO-AUC composite | 0.7386 |
| LOO-AUC MMLU-only | 0.6875 |
| ΔAUC | 0.0511 (95% CI [-0.1944, 0.4492]) |

---

## Figures

| Figure | Description |
|--------|-------------|
| fig1_gate_metrics_comparison.png | LOO-AUC comparison bar chart |
| fig2_roc_curves_comparison.png | ROC curve overlay |
| fig3_partial_correlation_comparison.png | Partial rho comparison |
| fig4_advglue_drop_distribution.png | AdvGLUE drop distribution |
| fig5_feature_importance.png | LOO logistic regression coefficients |
| fig6_epistemic_vs_adversarial_scatter.png | PC1 composite vs AdvGLUE scatter |

---

## Interpretation

The composite epistemic predictor achieves gate result **PARTIAL**. H-M3 proceeds regardless of H-M2 outcome (SHOULD_WORK gate).

**Prerequisite confirmation (H-E1 + H-M1):** Results build on confirmed partial ρ(ECE, TruthfulQA%|MMLU) = -0.758 and survival fraction 0.943 from H-M1.

---

## Conclusion

Gate: **PARTIAL** → Proceed to H-M3 in all cases (SHOULD_WORK).
