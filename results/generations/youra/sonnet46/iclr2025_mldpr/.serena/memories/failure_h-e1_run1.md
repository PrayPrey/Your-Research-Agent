# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-15T05:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Hypothesis Statement

A Robust Concentration Index (RCI) — computed as consensus across Gini, HHI, and normalized entropy over Papers With Code benchmark submission counts per task per year — is robustly computable for ≥15 ML task categories and shows a significant positive trend in ≥60% of those tasks over 2018-2024, under both active-only and cumulative inclusion policies.

## Performance Gap

| Metric | Result | Threshold | Status |
|--------|--------|-----------|--------|
| n_tasks_computable | 31 | ≥15 | PASS |
| pct_positive_trend | 0.258 (25.8%) | ≥0.60 (60%) | FAIL |
| permutation_p | 0.498 | <0.05 | FAIL |

## Root Cause Analysis

- The RCI shows a **negative** or flat trend in ~74% of tasks (only 8/31 show positive slope)
- The permutation test p=0.498 confirms the observed trend rate is indistinguishable from random
- Tasks with significant negative trends include: Image Classification (p=0.011, slope=-0.039), Object Detection (p=0.012, slope=-0.105), Fine-Grained Image Classification (p=0.030, slope=-0.078), Video Retrieval (p=0.019, slope=-0.132)
- The dominant empirical signal is **decreasing** benchmark concentration, not increasing
- This contradicts the hypothesis that concentration *increases* over 2018-2024
- The underlying mechanism assumption may be wrong: competitive leaderboard evaluation may diversify rather than concentrate benchmark participation

## Lessons Learned

1. The hypothesis assumed increasing benchmark concentration (competitive homogenization) but real PwC data shows predominantly decreasing concentration trends
2. The RCI computation itself is valid (31 tasks computed, mechanism indicators partially working), but the directional assumption is wrong
3. pct_positive_trend=0.258 is far below the 0.60 threshold - this is not a marginal miss
4. No parameter tuning can recover from a fundamental directional reversal in the empirical data
5. Future hypotheses should consider that benchmark diversity may *increase* over time rather than decrease

## Feedback for Next Phase (Phase 0 Re-brainstorm)

### Suggested Modifications
- Investigate decreasing concentration as the primary phenomenon
- Reframe: does benchmark diversity increase predict SOTA acceleration (not decline)?
- Consider task maturity as moderating variable (early tasks may show concentration, mature tasks show diversification)
- Explore bidirectional concentration: early growth phase vs. saturation phase

### What NOT To Do
- Do not assume positive concentration trend as prior — empirical evidence contradicts this
- Do not set threshold at 60% positive trend when data shows only 25.8%
- Do not use synthetic fallback data that encodes trending_up=True (prior mock data issue)

### What Showed Promise
- RCI computation pipeline is technically sound (all 31 tasks computed successfully)
- Real PwC API data retrieval via HuggingFace datasets works
- Significant negative trends found in major tasks (Image Classification, Object Detection) — these are real phenomena worth studying

## Routing Decision

**ROUTED_TO_PHASE_0**: Fundamental directional assumption failure requires complete hypothesis redesign.

---
*For cross-phase reference*
*Written at: 2026-03-15T05:00:00Z*
