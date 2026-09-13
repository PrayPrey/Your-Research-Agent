# Phase 4 Failure Record: h-m2_v3 (Run 1)

**Date:** 2026-03-19T14:30:00
**Hypothesis:** h-m2_v3
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL — β₂ negative in 4/5 pairs

## Hypothesis Statement

OLS regression of pass@1 on D_p_residual + cross-model difficulty shows β₂(D_p_residual) > 0 with p < 0.05 for ≥3/5 model-benchmark pairs.

## Performance Data

| Pair | β₂ | p-val (1-sided) | Gate |
|------|----|-----------------|------|
| llama3_8b_humaneval | -0.5317 | 8.86e-06 | FAIL |
| llama3_8b_mbpp | -0.4838 | 1.28e-07 | FAIL |
| codellama_7b_mbpp | +0.3855 | 3.61e-07 | PASS |
| deepseek_coder_6.7b_humaneval | -0.2771 | 8.11e-03 | FAIL |
| deepseek_coder_6.7b_mbpp | -0.6774 | 7.60e-12 | FAIL |

**Gate Result:** 1/5 pairs pass primary (required ≥3) → GATE FAIL

**Bootstrap CIs:** All 4 failing pairs have CI entirely negative (no zero crossing). Only codellama_7b_mbpp: CI=[0.229, 0.595].

## Root Cause Analysis

- D_p_residual negatively predicts pass@1 in 4/5 pairs after controlling for cross-model difficulty
- The negative relationship is not concentrated in extremes (regime analysis confirms consistent direction)
- Spearman difficulty correlation = 0.7975 (expected, ≥0.6 threshold passed) — multicollinearity not the issue (VIF < 2 for all pairs)
- The residualization approach may measure noise rather than signal for most model-benchmark pairs
- Heteroscedasticity and non-normality present in all pairs (common for bounded [0,1] outcomes, non-gating)
- Model-architecture specificity: only codellama_7b_mbpp shows positive β₂

## Lessons Learned

1. D_p_residual as defined (Bernoulli residual) does NOT positively predict pass@1 in augmented OLS — the signal is predominantly negative
2. The h-e1_v3 result (|mean_null| < 0.002, unbiasedness confirmed) does NOT imply the residual will predict pass@1 positively
3. Cross-model difficulty control may expose a suppression or confound effect where higher diversity after Bernoulli removal actually correlates with harder problems where models fail
4. Model-architecture heterogeneity is real — codellama_7b shows positive relationship while all others show negative
5. OLS with cross-difficulty control may be too conservative/partialling out the mechanism signal

## Feedback for Phase 0 Reformulation

### What to Avoid
- Using D_p_residual directly as positive predictor of pass@1 in standard OLS with difficulty control
- Assuming h-e1_v3 unbiasedness result implies positive predictive direction

### What Showed Promise
- codellama_7b_mbpp: positive β₂=+0.386 suggests model-specific signal exists
- ΔR² significant in all pairs (though negative direction) — D_p_residual does explain variance
- VIF < 2 for all pairs — multicollinearity not an issue, data quality good

### Suggested Reformulation Directions
- Investigate WHY D_p_residual negatively predicts — may be capturing a "confusion" signal rather than "exploration" signal
- Consider non-linear relationship or interaction terms (difficulty × D_p_residual)
- Consider using D_p_residual as predictor in opposite direction (predictor of DIFFICULTY, not pass@1)
- Consider model-stratified analysis or mixed effects models

## Routing

**Routing Decision:** ROUTED_TO_PHASE_0
**Reason:** Fundamental hypothesis refuted. β₂ negative in 4/5 pairs — the theoretical basis that D_p_residual positively predicts pass@1 is not supported. Requires hypothesis reformulation from Phase 0.

---
*Failure recorded at: 2026-03-19T14:30:00*
*For cross-phase reference*
