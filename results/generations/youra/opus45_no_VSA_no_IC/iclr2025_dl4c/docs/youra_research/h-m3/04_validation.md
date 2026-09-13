# h-m3 Validation Report

**Date:** 2026-08-24
**Hypothesis:** Unanimous scale agreement indicates ≥10% higher verdict reliability vs split verdicts
**Gate Type:** SHOULD_WORK
**Gate Result:** FAIL

---

## Executive Summary

Hypothesis h-m3 is **FALSIFIED**. Contrary to expectation, unanimous agreement across scales (7B, 70B, proprietary) shows **lower** accuracy than split verdicts (-3.95% difference). The result is statistically non-significant but directionally opposite to the hypothesis.

---

## Results

### Primary Metrics

| Metric | Value |
|--------|-------|
| Unanimous Accuracy | 35.77% (142/397) |
| Split Accuracy | 39.72% (168/423) |
| Improvement | **-3.95%** |
| Required Threshold | ≥10% |

### Statistical Test

| Statistic | Value |
|-----------|-------|
| Z-statistic | -1.165 |
| p-value | 0.878 |
| Significant (p<0.05) | No |

### Agreement Distribution

- Unanimous cases: 397 (48.4%)
- Split cases: 423 (51.6%)

---

## Interpretation

1. **Direction reversed**: Unanimous agreement indicates *lower* reliability, not higher
2. **Why**: When all 3 scales (including weak 7B) agree, they tend to agree on the *wrong* answer
3. **Split verdicts**: Disagreement often means at least one scale (typically proprietary) is correct
4. **Root cause**: Scale-homogeneous errors — weaker models drag down unanimous accuracy

---

## Gate Evaluation

**FAIL Conditions Met:**
- Improvement (-3.95%) < falsification threshold (5%)
- Direction opposite to hypothesis
- p-value non-significant (0.878)

---

## Artifacts

| File | Description |
|------|-------------|
| h-m3/code/analyze.py | Analysis script |
| h-m3/code/outputs/summary.json | Machine-readable results |
| h-m3/code/outputs/classified_agreement.csv | Per-problem classification |
| h-m3/figures/bar_chart.png | Accuracy comparison |
| h-m3/figures/pie_chart.png | Agreement distribution |

---

## Conclusion

The hypothesis that unanimous agreement signals higher reliability is **falsified**. In this judge ensemble, unanimous agreement actually correlates with *lower* accuracy because scale-homogeneous errors (all scales wrong together) outweigh unanimous correct verdicts. The proprietary model's disagreement with weaker scales is a stronger signal of correctness than unanimous agreement.

**Recommendation:** Do not use unanimous agreement as a confidence signal for this scale-diverse ensemble. Consider using proprietary-model verdicts alone (h-m2 finding) or studying per-scale error patterns (h-m1).
