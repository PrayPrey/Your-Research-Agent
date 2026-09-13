# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-03-16T12:00:00Z
**Hypothesis:** h-m1
**Statement:** Under evaluation of a trained DWSNet backbone on the Unterthiner MNIST FC-MLP zoo, if K=20 random neuron permutations are applied to test-set weight vectors at any N-level, then DWSNet's predicted property values have near-zero variance (Var_pi < 1e-6), because equivariant linear maps enforce permutation invariance as an architectural constraint requiring zero data.
**Final Status:** COMPLETED (FAILED)
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Routing:** ROUTE_TO_PHASE_0

## Results Summary
- All 5 N-levels FAIL: median_var_pi range 2e-3 to 9e-3 (threshold 1e-6)
- Root cause: DWSNets library runtime failure at weight_to_weight.py:832
- MLP fallback active; not permutation-equivariant

## Reflection
- Outcome: ROUTED_TO_PHASE_0
- Serena memory: failure_h-m1
- Self-modification: NOT viable (library incompatibility, not parameter issue)

---
*Per-hypothesis snapshot for Phase 2A reference*
