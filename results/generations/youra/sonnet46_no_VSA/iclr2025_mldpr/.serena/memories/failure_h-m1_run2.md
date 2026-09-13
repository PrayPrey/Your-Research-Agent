# Phase 4 Failure Record: h-m1 (Run 2)

**Date:** 2026-08-02T23:15:00+00:00
**Hypothesis:** h-m1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL — statistical null (no significant Δscore effect on displacement hazard)

## Gate Criteria Results

| Criterion | Value | Threshold | Pass |
|-----------|-------|-----------|------|
| HR ≤ 0.80 | 0.871 | ≤ 0.80 | FAIL |
| CI_upper < 1.0 | 1.393 | < 1.0 | FAIL |
| LRT p < 0.05 | 0.565 | < 0.05 | FAIL |
| Abs risk ≥ 5pp | 2.97pp | ≥ 5pp | FAIL |
| Rel risk ≥ 25% | 8.89% | ≥ 25% | FAIL |

**Gates passed: 0/5**

## Root Cause Analysis

- Coverage gap: only 34.1% of h-e2 panel rows have dscore_lag1_z (252/740 rows); 35 of 87 tasks have no matching evaluation-tables data in 2017–2023 range
- Low statistical power: only 22 displacement events in dscore-available subset vs 83 in full panel; below 10 EPV rule-of-thumb for a 3-covariate model
- Small effect size: HR=0.871 (coef=-0.14), directionally correct but not strong enough to achieve statistical significance with available data
- Mechanistically activated (3/4 indicators: convergence_ok, coefficient_negative, hr_below_1) but LRT not significant (p=0.565)

## Model Summary

- M0 LL: -80.836; M1 LL: -80.670; LRT stat=0.332, df=1, p=0.565
- dscore_lag1_z: coef=-0.14, HR=0.871, 95% CI [0.543, 1.393]
- High VIF for controls: task_age=22.3, log_publication_volume=22.4 (collinear, but does not affect dscore inference)

## Lessons Learned

1. Data coverage is the binding constraint: Δscore_lag1_z can only be computed for tasks where evaluation-tables has SOTA records across ≥2 consecutive years — 40% of h-e2 tasks fail this criterion
2. With only 22 events and 3 covariates, the model is underpowered; 10+ EPV requires ≥30 events minimum
3. The effect direction (HR < 1.0) is correct and consistent with theory — failure is power, not direction
4. Schoenfeld PH test not available for CoxTimeVaryingFitter (no `.durations` attribute); must use alternative diagnostics
5. add_covariate_to_timeline with pre-lagged dscore works correctly — no delay= needed

## Feedback for Next Phase (Phase 0 / Brainstorming)

### Suggested Modifications
- Increase coverage: use all benchmark-level (not task-level) units as survival entities — would give ~1,693 non-null rows as events instead of task-level aggregation
- Alternative exposure: use proportion of benchmarks saturated per task (robust to missing years)
- Extend temporal window beyond 2015–2023 if more data available
- Consider Poisson regression or logistic regression formulations that don't require long-format panel

### What NOT To Do
- Do not aggregate dscore_lag1_z to task level via mean — loses power by discarding benchmark variation
- Do not use `formula=` with CoxTimeVaryingFitter (not supported)
- Do not use `robust=True` (NotImplementedError in lifelines 0.30.x)

### What Showed Promise
- Direction of effect is correct (HR < 1.0, coef < 0) across both run 1 and run 2
- Mechanism activation confirmed (3/4 indicators), suggesting a real signal exists but is currently underpowered
- Pipeline and data loading work correctly; penalizer=0.1 achieves clean convergence

---
*For cross-phase reference (Phase 0 / Phase 2A)*
*Written at: 2026-08-02T23:15:00+00:00*
