# Phase 4 Failure Record: h-c1 (Run 1)

**Date:** 2026-08-09T16:37:00+00:00
**Hypothesis:** h-c1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** GEOMETRIC_FOUNDATION_VIOLATION

## Hypothesis Statement

Group-conditional Hessian eigenspaces share sufficient geometry (principal angle < 45°) for valid GHSA interpretation

## Gate Result

**MUST_WORK Gate: NOT SATISFIED**

All 6 group-pair max principal angles exceeded 45° threshold (range 87.2°-89.9°). Group eigenspaces are near-orthogonal, not aligned.

## Performance Summary

| Metric | Result |
|--------|--------|
| Pairs passing threshold | 0/6 |
| Mean max principal angle | 88.5° |
| Range | 87.2° - 89.9° |

## Root Cause Analysis

- Group-conditional Hessian eigenspaces are near-orthogonal (~90°), not aligned
- Majority group (landbird_land) eigenvalues ~3 orders of magnitude smaller than minority groups
- Different groups occupy completely different curvature directions in parameter space
- GHSA interpretation fundamentally invalid — comparing alignment scores across orthogonal subspaces is meaningless

## Lessons Learned

1. **Geometric assumptions must be validated first** — GHSA mechanism assumes shared curvature structure that does not exist in practice
2. **Majority/minority eigenvalue disparity is extreme** — suggests ERM flattens loss for majority while keeping high curvature for minorities
3. **Eigenspace orthogonality is robust** — unlikely to change with different model/data configurations
4. **Alternative mechanisms needed** — gradient-Hessian alignment differential cannot explain group loss disparity when groups have orthogonal eigenspaces

## Feedback for Next Attempt (Phase 0/2A)

### What NOT To Do
- Do not assume group-conditional Hessians share common top eigenvectors
- Do not compare GHSA scores across groups without validating geometric compatibility
- Do not use eigenvalue-weighted metrics when eigenvalue scales differ by 3+ orders

### What Showed Promise
- Eigenvalue magnitude disparity itself may explain loss dynamics (majority flat, minority sharp)
- Per-group curvature analysis reveals structural differences hidden by global Hessian
- The observation that groups occupy orthogonal subspaces is itself a finding worth exploring

### Suggested New Directions
- Investigate eigenvalue-based mechanism instead of eigenvector alignment
- Explore loss landscape geometry differences (flatness vs sharpness) as explanation
- Consider that ERM optimization naturally separates group representations into orthogonal subspaces

---
*For cross-phase reference*
*Written at: 2026-08-09T16:37:00+00:00*
