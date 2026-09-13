# Phase 4 Failure Record: sh2 (Run 1)

**Date:** 2026-08-03T17:00:00Z
**Hypothesis:** sh2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL

## Hypothesis Statement

Hungarian canonical ordering (scipy.optimize.linear_sum_assignment) reduces OrbitVar(CISE) by ≥100× (from >0.01 to <0.0001) by driving all models to consistent canonical channel arrangement

## Performance Gap

| Metric | Result | Gate Threshold | Gap |
|--------|--------|----------------|-----|
| mean OrbitVar(CISE_aligned) | 0.010325 | <0.0001 | 103× too large |
| Reduction ratio | 1.0× | ≥100× | 99× short |

## Root Cause Analysis

- within-orbit OrbitVar is **intrinsic** to the CISE sinusoidal positional encoding — it measures variance within a single model's orbit under channel permutations
- Hungarian alignment is a **cross-model** operation that aligns different models to a reference ordering
- These are orthogonal operations: cross-model alignment cannot reduce within-orbit (within-model) variance
- The mechanism assumption was fundamentally wrong: LAP alignment addresses inter-model consistency, NOT intra-model permutation symmetry

## Key Findings

- LAP assignments are non-identity (alignment does occur mechanically)
- L2(ref, aligned) < L2(ref, orig) — models do become closer to reference after alignment
- CISE output changes after alignment — mechanism is active
- BUT OrbitVar remains unchanged — because OrbitVar measures within-model orbit, not cross-model distance

## Lessons Learned

1. Within-orbit variance (OrbitVar) and cross-model alignment are orthogonal: fixing one does not affect the other
2. Hungarian LAP is the right tool for cross-model canonicalization, but wrong tool for reducing within-orbit variance
3. To reduce within-orbit OrbitVar, need to modify the CISE encoder itself (e.g., invariant PE, equivariant architecture)
4. Future hypotheses targeting OrbitVar reduction should focus on encoder-level changes, not post-hoc alignment
5. Ablations (ref stability, layer scope, iter count) all confirmed alignment works mechanically but is orthogonal to OrbitVar

## Feedback for Next Phase (Phase 0 / Phase 2A)

### Suggested Modifications
- Redesign hypothesis to target encoder-level permutation invariance
- Consider: invariant pooling, symmetric activation functions, or learned canonical ordering within encoder
- Explore: whether a permutation-invariant PE design can achieve OrbitVar < 0.0001

### What NOT To Do
- Do not attempt post-hoc alignment (LAP/Hungarian) as a mechanism for reducing OrbitVar
- Do not assume cross-model canonicalization reduces within-model orbit variance

### What Showed Promise
- sh1 result (OrbitVar > 0.01) is solid — sinusoidal PE does create measurable within-orbit variance
- The alignment mechanism works correctly — just addresses the wrong variance source
- Ablation methodology is sound and reusable

---
*For cross-phase reference*
*Written at: 2026-08-03T17:00:00Z*
