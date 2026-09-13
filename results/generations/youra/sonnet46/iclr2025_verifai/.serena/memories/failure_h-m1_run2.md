# Phase 4 Failure Record: h-m1 (Run 2)

**Date:** 2026-03-20T08:26:00+00:00
**Hypothesis:** h-m1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** GATE_FAIL_MUST_WORK — LOO-decoupled C_p mixed-effects regression beta negative in 4/5 pairs

## Performance Gap

| Metric | Result | Threshold | Pass |
|--------|--------|-----------|------|
| Pairs passing (beta>0, p<0.05, ΔR²≥0.02) | 0/5 | ≥3/5 | FAIL |
| Beta direction (positive) | 1/5 | — | — |

## Per-Pair Results

| Pair | Beta | p_one_sided | ΔR² | Pass |
|------|------|-------------|-----|------|
| llama3-8b_humaneval | -0.0932 | 0.7183 | 0.0022 | FAIL |
| llama3-8b_mbpp | -0.5164 | 1.0000 | 0.0566 | FAIL |
| deepseek-6.7b_humaneval | -0.3832 | 0.9458 | 0.0265 | FAIL |
| deepseek-6.7b_mbpp | -0.2397 | 1.0000 | 0.0215 | FAIL |
| codellama-7b_humaneval | 0.0508 | 0.0001 | -0.0015 | FAIL |

## Root Cause Analysis

- LOO-decoupled C_p does not predict pass@1 via mixed-effects regression with positive beta
- C_p_LOO has negative beta in 4/5 pairs — consensus similarity is inversely correlated or unrelated
- The mechanism (C_p as predictor of pass@1 via LOO-mixed-effects) is not activated in the data
- H-C_p-v10 sub-hypothesis H-M1 (mechanism) has fundamentally failed

## Lessons Learned

1. LOO-decoupled C_p (consensus similarity) does not positively predict pass@1 when modeled via mixed-effects regression
2. Negative beta across most pairs suggests the mechanism hypothesis is incorrect or the measure is inverted
3. H-E1 and H-E2 passed (existence of C_p variation confirmed), but mechanism link to pass@1 is absent
4. Future hypotheses should reconsider whether consensus similarity causally relates to pass@1
5. Mixed-effects regression with LOO decoupling is a valid methodology — the problem is the theoretical assumption

## Failed Checks

- beta_negative_4_of_5_pairs
- p_one_sided_above_threshold_4_of_5
- delta_r2_below_threshold_4_of_5

## Reflection Outcome

- **Gate type:** MUST_WORK
- **Decision:** ROUTED_TO_PHASE_0
- **Cascade:** h-m2, h-m3 CASCADE_FAILED (dependent on h-m1 MUST_WORK passing)

---
*For cross-phase reference*
*Written at: 2026-03-20T08:26:00+00:00*
