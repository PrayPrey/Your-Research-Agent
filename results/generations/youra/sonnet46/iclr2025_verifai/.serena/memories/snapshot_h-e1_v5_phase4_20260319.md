# Hypothesis Completion Snapshot: h-e1_v5

**Date:** 2026-03-19T19:36:00Z
**Hypothesis:** h-e1_v5
**Statement:** gamma_p = D_p^w / E[D_p^w] is well-defined (E[D_p^w] > 0 for >95% problems) and non-degenerate (IQR > 0.1) for ≥4/5 model-benchmark pairs
**Final Status:** FAILED
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results
- valid_fraction: 0/5 pairs exceed 0.95 (best: 0.890)
- IQR(gamma_p): ~4.4e-16 (machine epsilon, analytically zero) for all 5 pairs
- Pairs passing: 0/5 (required: ≥4)

## Root Cause
gamma_p = D_p^w / E[D_p^w] is **analytically constant = 1.25** for k=5 solutions.
The ratio of a weighted diversity to its own Bernoulli expectation (same weights) is a fixed constant — mathematical identity, not a data issue.

## Cascade
- h-e2_v5: CASCADE_FAILED
- h-m1_v5: CASCADE_FAILED

## Key Lesson
**Never use self-normalizing ratio metrics** (metric / expected_value_of_same_metric).
Prefer: raw D_p^w (unnormalized), entropy of pass vectors, or comparison against a DIFFERENT null distribution.

---
*Per-hypothesis snapshot for Phase 2A reference*
