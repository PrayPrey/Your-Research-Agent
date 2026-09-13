# Phase 4 Failure Record: h-e1 (Run 2)

**Date:** 2026-08-09T07:40:00Z
**Hypothesis:** h-e1
**Run:** 2
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_NOT_SUPPORTED
**Gate Type:** MUST_WORK

## Hypothesis Statement

Converged ERM models show R_final > 1.0 (background-dominant attribution) on majority groups

## Performance Gap

| Metric | Observed | Threshold | Gap |
|--------|----------|-----------|-----|
| R_final | 0.62 ± 0.02 | > 1.0 | -0.38 |
| 95% CI | [0.567, 0.681] | > 1.0 | Entirely below threshold |

## Root Cause Analysis

- ERM models focus on center/foreground features (bird), not background
- GradCAM visualizations confirm attribution concentrated on object, not spurious correlation
- R_final metric consistently < 1.0 across all 3 seeds
- Overall accuracy 91.47% achieved without background-dominant attribution

## Lessons Learned

1. The premise that ERM models rely on background features may be incorrect for Waterbirds
2. High accuracy can be achieved through foreground (bird) features alone
3. R_final metric design may need reconsideration - ratio assumes background dominance exists
4. Consider alternative metrics that don't assume direction of spurious correlation

## Feedback for Phase 2A-Dialogue

### Suggested Modifications
- Re-examine the definition of "spurious feature reliance"
- Consider that models may use foreground shortcuts (bird appearance) instead of background
- Investigate whether the spurious correlation manifests differently than assumed

### What NOT To Do
- Do not assume background dominance without empirical verification
- Do not set threshold > 1.0 without baseline measurements

### What Showed Promise
- Attribution measurement methodology (GradCAM) works correctly
- Seed-based reproducibility achieved
- Statistical analysis framework is sound

---
*For cross-phase reference*
*Written at: 2026-08-09T07:40:00Z*
*Routed to: Phase 2A-Dialogue*
