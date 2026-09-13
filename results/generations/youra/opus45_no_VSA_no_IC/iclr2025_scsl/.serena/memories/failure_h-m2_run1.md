# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-08-24T13:42:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** COMPUTATIONAL_INFEASIBILITY

## Performance Gap

| Metric | Target | Actual | Gap |
|--------|--------|--------|-----|
| Experiment Completion | 100% | ~80% (training only) | -20% |
| Gate Evaluation | PASS/FAIL | NOT_EVALUATED | N/A |

## Root Cause Analysis

- Hessian eigenvector computation using pytorch-hessian-eigenthings Lanczos iteration is too slow
- ResNet-50 has ~23M parameters, making full Hessian analysis impractical
- Each checkpoint requires 2-3+ minutes for eigenvector computation
- 6 checkpoints × 3 seeds = 18+ computations = hours of analysis time
- Timeout triggered before first checkpoint analysis completed

## Lessons Learned

1. Full Hessian eigenvector computation on ImageNet-scale models is computationally prohibitive
2. Training time (10 min) << Analysis time (hours) for Hessian-based methods
3. pytorch-hessian-eigenthings library not suitable for rapid experimentation
4. Need approximation methods (power iteration, stochastic Lanczos) for practical use

## Feedback for Next Phase

### Suggested Modifications
- Use ResNet-18 or smaller backbone for Hessian analysis feasibility
- Reduce number of eigenvectors (k=5 instead of k=20)
- Use power iteration instead of full Lanczos
- Consider gradient-only proxy metrics (no Hessian)
- Sample fewer checkpoints (3 instead of 6)

### What NOT To Do
- Do not attempt full Lanczos on ResNet-50+ models
- Do not schedule Hessian analysis within standard timeout windows
- Do not assume pytorch-hessian-eigenthings runs quickly

### What Showed Promise
- Training loop works correctly
- Gradient direction computation is fast
- Checkpoint saving/loading works
- Probe training is efficient

---
*For cross-phase reference*
*Written at: 2026-08-24T13:42:00+00:00*
