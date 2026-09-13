# Phase 4 Failure Record: H-E1 (Run 1)

**Date:** 2026-08-02T10:30:00Z
**Hypothesis:** H-E1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** ASSUMPTION_VIOLATION_A1
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Performance Gap

| Metric | Actual | Threshold | Gap |
|--------|--------|-----------|-----|
| degenerate_fraction | 0.5556 | < 0.30 | +0.2556 (FAIL) |
| mean_group_std | 0.1743 | > 0.30 | -0.1257 (FAIL) |

## Root Cause Analysis

**Primary:** Model capability mismatch with training dataset.
- Hypothesis assumed p_effective ≈ 0.39 (HumanEval pass@1 for DeepSeek-Coder-7B)
- Training pool mixed HumanEval (164 easy) + MBPP-sanitized (374 harder problems)
- Effective pass rate on combined pool ≈ 10-15% per group problem, not 39%
- At p_eff ≈ 0.12, K=8: P(all-fail) = 0.88^8 ≈ 0.35 (vs assumed ~2%)

**Secondary:** Phase 2B binomial used p=0.39 from HumanEval-only. MBPP+ is significantly harder.

**Key Insight:** Assumption A1 ("E[passes]=3.1 per group") was wrong because p_effective << p_humaneval when MBPP+ is included in the training pool.

## Lessons Learned

1. Always pre-validate effective pass rate on the actual training dataset before running GRPO
2. HumanEval pass@1 ≠ effective pass rate on mixed training pools
3. MBPP+ problems are significantly harder than HumanEval for 7B models
4. Early abort callback worked correctly — detected A1 violation at step 50

## Suggestions for Phase 0

- Use only HumanEval (164 problems) for training to maintain p_eff ≈ 0.39
- Pre-validate: sample K=8 from training pool, measure actual pass rate BEFORE GRPO
- Try more capable model (>50% HumanEval pass@1) to ensure p_eff stays high
- Increase K to 16 to reduce degenerate probability
- Add a pre-experiment pass rate check as mandatory gate before GRPO training

## Cascade Effects

Dependent hypotheses all CASCADE_FAILED:
- H-M1 (MUST_WORK prerequisite on H-E1)
- H-M2, H-M3, H-M4 (downstream)

---
*Failure recorded at: 2026-08-02T10:30:00Z*
*For cross-phase reference*
