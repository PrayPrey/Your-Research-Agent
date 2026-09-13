# Hypothesis Completion Snapshot: h-m2

**Date:** 2026-05-21T04:15:00Z
**Hypothesis:** h-m2
**Type:** MECHANISM (INCREMENTAL on h-e1, h-m1)
**Final Status:** FAILED
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0 (step-06b executed 2026-05-21T04:15:00Z)

## Statement

Under weight space analysis on Small CNN Zoo checkpoint trajectories, if weight vectors are projected onto permutation orbit directions and GL orbit directions, then Var_perm / (Var_perm + Var_GL) > 0.60.

## Results

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| var_ratio_mean (overall) | 0.3479 ± 0.054 | > 0.60 | FAIL |
| Conv2d ratio | 0.637 | > 0.60 | PASS |
| Linear ratio | 0.133 | > 0.60 | FAIL |
| n_models | 1000 | ≥ 200 | PASS |

## Reflection (Step 06b)

- **Outcome:** ROUTED_TO_PHASE_0
- **Reason:** MUST_WORK FAIL (not PARTIAL) — fundamental assumption falsified for Linear layers
- **Key insight:** Layer-type asymmetry — Conv2d shows permutation dominance, Linear layers show GL orbit dominance
- **Pre-specified pivot:** Hybrid orbit-PE + GL trace features (from h-m2 gate condition)

## Cascade Effects

- h-m3: BLOCKED (prerequisite h-m2 FAILED)
- h-c1: BLOCKED (cascade from h-m2)

## For Phase 0

- Preserve: h-e1 (PASS) + h-m1 (PASS) + Conv2d permutation orbit result (0.637)
- Incorporate: GL orbit encoding for Linear/FC layers
- New mechanism: Hybrid orbit-PE (perm for Conv2d + GL for Linear)

---
*Updated by step-06b-reflection batch-mode recovery: 2026-05-21T04:15:00Z*
*Per-hypothesis snapshot for Phase 2A / Phase 0 reference*
