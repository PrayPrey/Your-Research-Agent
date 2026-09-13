# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-24T05:00:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MECHANISM_NOT_DETECTED
**Gate Type:** MUST_WORK

## Hypothesis Statement

Order parameter phi variance peaks at identifiable epoch (critical point exists)

## Performance Gap

| Metric | Expected | Actual | Result |
|--------|----------|--------|--------|
| Peak/Baseline Ratio | >2.0 | 0.98 | FAILED |
| Critical Epoch Consistency | std<5 | std=0.0 | PASSED |

## Root Cause Analysis

- Phi metric (spurious_acc - core_acc) does not exhibit variance spike during training
- Peak variance (4.21e-05) actually slightly lower than baseline variance (4.31e-05)
- Linear probe approach may not capture spurious-core transition dynamics as hypothesized
- The expected phase transition signal in phi is not present in Waterbirds/ResNet-50

## Lessons Learned

1. Phi definition (spurious_acc - core_acc) insufficient to detect critical epoch
2. Rolling variance window of 5 epochs may be inappropriate scale
3. Linear probes may not be sensitive enough to representation changes
4. Alternative metrics needed: gradient norms, loss landscape curvature, or representation similarity

## Feedback for Next Phase

### Suggested Modifications
- Try alternative order parameters: gradient norm variance, feature correlation with spurious attribute
- Investigate loss landscape metrics instead of probe accuracy
- Consider representation-level metrics (CKA, SVCCA) between epochs

### What NOT To Do
- Do not assume linear probe accuracy captures all relevant representation dynamics
- Do not use same phi definition without modification

### What Showed Promise
- Critical epoch detection was perfectly consistent across seeds (std=0.0)
- Infrastructure for probe training and variance calculation works correctly

---
*For cross-phase reference*
*Written at: 2026-08-24T05:00:00Z*
