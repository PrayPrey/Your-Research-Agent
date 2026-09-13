# Limitation Record: h-m1 (Run 1)

**Date:** 2026-08-28T01:35:00Z
**Hypothesis:** h-m1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Calibration does not moderate the truthfulness-robustness correlation as hypothesized. The experiment found:
1. ECE correlations with TruthfulQA and AdvGLUE are weak and non-significant
2. The moderation direction is opposite to expectation: high-ECE (poorly calibrated) models show stronger truthfulness-robustness correlation than low-ECE models
3. Fisher z-test for moderation is non-significant (p=0.165)

## Failed Checks

- ECE-TruthfulQA r=-0.12 > threshold -0.2
- ECE-AdvGLUE r=-0.16 > threshold -0.2
- Moderation direction opposite (high-ECE stronger)
- Fisher p=0.165 > threshold 0.05

## Partial Results

| Metric | Value |
|--------|-------|
| ECE-TruthfulQA partial r | -0.1196 |
| ECE-AdvGLUE partial r | -0.1632 |
| Low-ECE group correlation | r=0.65 |
| High-ECE group correlation | r=0.99 |
| Fisher z-test p-value | 0.165 |
| Models evaluated | 14 |

## Experiment Summary

H-M1 tested whether calibration (measured by ECE) moderates the correlation between truthfulness and robustness established in H-E1. Results show calibration is NOT the mechanism: ECE correlates weakly with both metrics, and contrary to hypothesis, poorly-calibrated models show stronger truthfulness-robustness correlation.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted. Alternative mechanism hypotheses (H-M2, H-C1) remain for exploration.

Future research attempts should consider:
1. Calibration may be orthogonal to truthfulness-robustness relationship
2. Other mechanisms may explain the correlation (representation quality, training data diversity)
3. ECE as calibration measure may have limitations for this analysis

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-28T01:35:00Z*
*For cross-phase reference*
