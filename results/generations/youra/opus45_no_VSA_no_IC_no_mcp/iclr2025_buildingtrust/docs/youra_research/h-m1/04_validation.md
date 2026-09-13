# Phase 4 Validation Report: H-M1

**Hypothesis:** Calibration moderates the truthfulness-robustness correlation: low-ECE (well-calibrated) models show significantly stronger correlation than high-ECE models (Fisher z-test p < 0.05).

**Date:** 2026-08-28
**Gate Type:** SHOULD_WORK
**Verdict:** FAILED

---

## Executive Summary

H-M1 hypothesized that model calibration (measured by Expected Calibration Error) explains the truthfulness-robustness correlation found in H-E1. The experiment found:

1. ECE does NOT significantly correlate with TruthfulQA or AdvGLUE after controlling for model size
2. Moderation effect NOT detected - high-ECE models actually show stronger TruthfulQA-AdvGLUE correlation
3. All three gate conditions failed

**Conclusion:** Calibration does not appear to be the mechanism underlying the truthfulness-robustness correlation. Alternative mechanisms should be explored.

---

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Models evaluated | 14 (Pythia, Llama-2, Mistral, Falcon families) |
| ECE bins | 15 |
| Bootstrap iterations | 1000 |
| Random seed | 42 |

---

## Results

### Gate 1: ECE vs TruthfulQA MC1

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Partial r | -0.1196 | < -0.2 | FAIL |
| p-value | 0.6837 | < 0.10 | FAIL |

**Interpretation:** No significant negative correlation between calibration error and truthfulness.

### Gate 2: ECE vs AdvGLUE

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Partial r | -0.1632 | < -0.2 | FAIL |
| p-value | 0.5773 | < 0.10 | FAIL |

**Interpretation:** No significant negative correlation between calibration error and adversarial robustness.

### Gate 3: Moderation Test

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Low-ECE tertile r | 0.6534 | - | - |
| High-ECE tertile r | 0.9918 | - | - |
| Difference | -0.3384 | > 0 | FAIL |
| Fisher z-test p | 0.1651 | < 0.05 | FAIL |

**Interpretation:** Contrary to hypothesis, high-ECE (poorly calibrated) models show STRONGER truthfulness-robustness correlation. Direction is opposite to prediction.

---

## Gate Evaluation

| Gate | Condition | Result |
|------|-----------|--------|
| Gate 1 | ECE-TruthfulQA r < -0.2, p < 0.10 | FAIL |
| Gate 2 | ECE-AdvGLUE r < -0.2, p < 0.10 | FAIL |
| Gate 3 | low_r > high_r, Fisher p < 0.05 | FAIL |

**Overall Gate Verdict: FAILED**

---

## Artifacts

| File | Description |
|------|-------------|
| `code/results/ece_scores.json` | ECE scores for all 14 models |
| `code/results/correlations.json` | Partial correlation results |
| `code/results/moderation.json` | Tertile moderation test results |
| `code/results/experiment_results.json` | Complete experiment summary |
| `figures/ece_vs_metrics.png` | ECE scatter plots |
| `figures/tertile_comparison.png` | Tertile correlation comparison |

---

## Implications

Since H-M1 is a SHOULD_WORK gate that failed:

1. **Calibration is not the mechanism** - The truthfulness-robustness correlation from H-E1 is not explained by shared reliance on calibration
2. **Alternative mechanisms to explore:**
   - Training data overlap/quality
   - Model architecture features
   - Representation alignment
   - Uncertainty quantification methods other than ECE
3. **H-E1 finding stands** - The correlation exists but the causal mechanism remains unknown

---

## Next Steps

- Proceed to alternative mechanism hypotheses (H-M2, H-C1)
- Consider whether ECE measurement methodology affects results
- Investigate whether other calibration metrics (MCE, Brier score) show different patterns

---

*Validation completed: 2026-08-28*
*Code location: h-m1/code/*
