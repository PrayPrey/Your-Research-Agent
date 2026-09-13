# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-08-10T02:20:00Z
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED
**Gate Type:** MUST_WORK

## Hypothesis Statement

NFN reaches 0.70 AUC crossover point at significantly lower N than Hyper-Rep (non-overlapping 95% bootstrap CI), demonstrating sample efficiency advantage.

## Performance Gap

| Metric | NFN | HyperRep | Gap |
|--------|-----|----------|-----|
| AUC at N=500 | 0.47 | 0.78 | -0.31 |
| AUC at N=5000 | 0.47 | 0.96 | -0.49 |
| Crossover Point | ∞ (never) | 130 | N/A |
| Cohen's d | 0.579 | - | Below 0.80 threshold |

## Root Cause Analysis

- NFN single-layer architecture (NPLinear + MeanPool) lacks capacity for pairwise ranking task
- NFN embeddings remain near-random (AUC ~0.47) regardless of training data size
- Architecture designed for equivariance verification, not ranking task
- HyperRep's flatten+MLP approach learns ranking effectively

## Lessons Learned

1. Equivariance alone does not guarantee sample efficiency for ranking tasks
2. Single NPLinear layer insufficient for complex relational tasks
3. Need deeper NFN architecture or task-specific head for ranking
4. Architecture capacity must match task complexity

## Feedback for Next Phase

### Suggested Modifications
- Use deeper NFN encoder (2-3 NPLinear layers)
- Add task-specific ranking head after pooling
- Consider pairwise NFN architecture (Siamese-style)

### What NOT To Do
- Do not use single-layer NFN for ranking tasks
- Do not assume equivariance transfers directly to sample efficiency

### What Showed Promise
- NFN equivariance is valid (h-m1 passed)
- HyperRep baseline implementation is correct and learns well

---
*For cross-phase reference*
*Written at: 2026-08-10T02:20:00Z*
