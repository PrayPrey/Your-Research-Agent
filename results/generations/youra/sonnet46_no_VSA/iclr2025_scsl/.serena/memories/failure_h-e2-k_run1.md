# Phase 4 Failure Record: h-e2-k (Run 1)

**Date:** 2026-08-04T09:00:00+00:00
**Hypothesis:** h-e2-k
**Run:** 1
**Final Status:** FAIL
**Failure Type:** GATE_THRESHOLD_NOT_MET

## Performance Gap

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| delta_10_20 (AUROC_K=20 - AUROC_K=10) | 0.01117 | < 0.01 | FAIL |
| K=10 AUROC | 0.8974 ± 0.0028 | — | — |
| K=20 AUROC | 0.9086 ± 0.0022 | — | — |
| K=20→50 delta | 0.0044 | < 0.01 | PASS |
| K=50 vs analytical gap | 0.0059 | < 0.05 | PASS |

## Root Cause Analysis

- K=10 Hutchinson trace estimator does NOT achieve adequate SNR at K=10 — delta_10_20 = 0.01117 exceeds the 0.01 plateau threshold
- Plateau is only reached at K=20→50 (delta=0.0044 < 0.01)
- K=20 or K=50 required as primary K for adequate discrimination

## Lessons Learned

1. K=10 Rademacher probes insufficient for per-sample minority/majority discrimination with AUROC plateau criterion
2. K=20 achieves near-plateau; K=50 achieves full plateau vs analytical
3. Failure route: use K=20 or K=50 as primary K in H-E2-exist

## Feedback for Next Phase

### Suggested Modifications
- Use K=50 as primary K in H-E2-exist (plateau confirmed at K=50 vs analytical gap=0.0059)
- K=20 is a viable compromise (delta=0.0044 < 0.01) if compute is a concern

### What NOT To Do
- Do not use K=10 as primary K for Hutchinson trace estimator in this task

### What Showed Promise
- Estimator is otherwise valid: K=50 vs analytical gap = 0.0059 < 0.05
- AUROC discrimination signal exists (K=20 AUROC = 0.9086) — mechanism is sound, just needs more probes

---
*For cross-phase reference*
*Written at: 2026-08-04T09:00:00+00:00*
