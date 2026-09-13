# Phase 4 Failure Record: sh2-corr (Run 1)

**Date:** 2026-07-29T20:15:00+00:00
**Hypothesis:** sh2-corr
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL — empirical direction opposite to hypothesis

## Performance Gap

| Metric | Ours | Target | Result |
|--------|------|--------|--------|
| Spearman rho | +0.6607 | < -0.10 | FAIL (opposite direction) |
| p-value (one-tailed) | 1.0000 | < 0.05 | FAIL |
| N | 52 | >= 50 | PASS |

## Root Cause Analysis

- The empirical Spearman correlation between AlpacaEval 2.0 LC win rate and TruthfulQA MC1 accuracy is **strongly positive** (rho=+0.661, 95% CI=[0.38, 0.82]), directly opposite to the hypothesized negative direction (< -0.10).
- The assumed alignment-helpfulness tradeoff is not supported at the benchmark aggregate level across 52 open-weight models.
- The positive correlation likely reflects that model scale/capability simultaneously drives both helpfulness and truthfulness metrics, masking any within-training tradeoff.

## Lessons Learned

1. Benchmark-level aggregate correlations across models may reflect scaling confounds rather than alignment tradeoffs.
2. The positive correlation (rho=+0.661) is a robust and publishable finding — not noise.
3. The tradeoff hypothesis may require controlling for model size (SH3-PARTIAL) or examining within-family variation (SH4-FAMILY).
4. One-tailed p-value direction logic is correct: rho > 0 → p_one_tailed = 1.0.
5. Family-clustered bootstrap with 10k iterations confirmed robustness (39 families, 10000/10000 valid).

## Feedback for Next Phase

### Suggested Modifications
- Re-frame: investigate whether partial correlation (controlling for model scale proxy like MMLU or param count) reveals suppressed tradeoff (SH3-PARTIAL)
- Consider within-family analysis: local negative correlations may exist within families even if cross-family trend is positive (SH4-FAMILY)

### What NOT To Do
- Do not assume a negative baseline correlation — empirically it is strongly positive (+0.661)
- Do not use this hypothesis as-is for Phase 0 redesign without controlling for scaling

### What Showed Promise
- The correlation analysis infrastructure (load_data, extract_family, cluster_bootstrap) works correctly and is reusable for SH3+
- N=52 merged dataset with 39 families provides robust statistical power
- The positive finding itself is scientifically meaningful for the paper

---
*For cross-phase reference*
*Written at: 2026-07-29T20:15:00+00:00*
