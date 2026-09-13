# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-24T03:15:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_NOT_SUPPORTED
**Gate Type:** MUST_WORK

## Hypothesis Statement

Human vote entropy and RM ensemble variance are positively correlated (r > 0.2, p < 0.001, N > 5000)

## Performance Gap

| Metric | Observed | Threshold | Gap |
|--------|----------|-----------|-----|
| Pearson r | -0.0624 | > 0.2 | -0.2624 (wrong direction) |
| p-value | 1.30e-06 | < 0.001 | PASS |
| Sample N | 6000 | > 5000 | PASS |

## Root Cause Analysis

- Correlation is **negative** (-0.062), opposite to hypothesized positive relationship
- When human voters disagree (high entropy), RM models tend to **agree more**, not less
- Human vote entropy captures "preference ambiguity" while RM variance captures "model confidence" — these appear to be orthogonal constructs
- Two-model ensemble (2/3 RMs loaded) may lack diversity needed
- Aggregated entropy (by model pair) may not align temporally with specific battle decisions

## Lessons Learned

1. Human disagreement and RM disagreement are NOT measuring the same underlying construct
2. The "shared ambiguity" assumption is fundamentally flawed
3. Need alternative mechanism to explain quadrant distribution from H-E1
4. High human entropy samples may be "easy" for RMs (clear quality difference, humans just have diverse preferences)

## Feedback for Next Phase

### Suggested Modifications
- Test alternative uncertainty metrics
- Use larger/more diverse RM ensemble (5 models as planned)
- Investigate per-battle entropy instead of aggregated pair entropy

### What NOT To Do
- Do not assume human and model uncertainty stem from same source
- Do not aggregate entropy across model pairs

### What Showed Promise
- Statistical significance achieved (p < 0.001)
- Sample size exceeded requirements (N = 6000)
- Data pipeline and RM scoring infrastructure works

---
*Written at: 2026-08-24T03:15:00Z*
