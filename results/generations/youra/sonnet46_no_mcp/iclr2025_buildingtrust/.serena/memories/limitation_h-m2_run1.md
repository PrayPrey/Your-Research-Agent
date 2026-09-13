# Limitation Record: h-m2 (Run 1)

**Date:** 2026-04-30T14:34:29Z
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate PARTIAL: The epistemic composite predictor (ECE + TruthfulQA% + Brier) achieves
LOO-AUC ≥ 0.70 (observed: 0.739) and partial ρ(ECE, AdvGLUE|MMLU) ≥ 0.40 (observed: -0.719),
but the delta AUC improvement over MMLU-only baseline is 0.051, below the 0.10 threshold,
and the bootstrap confidence interval [-0.194, 0.449] does not exclude zero, indicating the
incremental predictive gain is not statistically significant.

## Failed Checks

- delta_auc = 0.0511 < threshold 0.10
- delta_auc_ci = [-0.1944, 0.4492] does not exclude zero (CI lo > 0 required)

## Partial Results

| Metric | Value |
|--------|-------|
| partial rho(ECE, AdvGLUE\|MMLU) | -0.7185 (BCa 95% CI [-0.882, -0.386]) |
| partial rho(ECE, ANLI\|MMLU) | -0.6667 (BCa 95% CI [-0.819, -0.385]) |
| LOO-AUC composite | 0.7386 |
| LOO-AUC MMLU-only baseline | 0.6875 |
| ΔAUC | 0.0511 (95% CI [-0.1944, 0.4492]) |

## Experiment Summary

H-M2 statistical analysis on N=30 open-weight LLM score matrix. Partial Spearman correlations
strongly confirm ECE → adversarial robustness link (rho=-0.72, CI excludes zero). LOO-AUC
composite predictor passes the 0.70 threshold. However, the marginal gain over MMLU-only
baseline (ΔAUC=0.051) is small and statistically uncertain — the composite adds calibration
signal but the incremental improvement over raw capability is not robustly demonstrated
with N=30 models.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. The specific checks that failed: delta AUC threshold and CI significance
2. Whether the limitation is fundamental (N=30 too small for reliable ΔAUC estimation) or circumstantial
3. Alternative approaches: larger N, different composite features, or relaxed delta threshold

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-04-30T14:34:29Z*
*For cross-phase reference*
