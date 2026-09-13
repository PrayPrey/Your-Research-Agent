# H-M1 Phase 4 Failure Record

## Hypothesis
H-M1: MECHANISM — DWSNet Permutation Invariance Verification

**Statement:** Under evaluation of a trained DWSNet backbone on the Unterthiner MNIST FC-MLP zoo, if K=20 random neuron permutations are applied to test-set weight vectors at any N-level, then DWSNet's predicted property values have near-zero variance (Var_pi < 1e-6), because equivariant linear maps enforce permutation invariance as an architectural constraint requiring zero data.

## Outcome
- **Gate Type:** MUST_WORK
- **Gate Result:** FAIL
- **Routing:** ROUTE_TO_PHASE_0

## Experiment Results
| N-level | median_var_pi | Threshold | Status |
|---------|--------------|-----------|--------|
| N=50    | 2.95e-3      | 1e-6      | FAIL   |
| N=100   | 2.04e-3      | 1e-6      | FAIL   |
| N=200   | 6.06e-3      | 1e-6      | FAIL   |
| N=500   | 9.09e-3      | 1e-6      | FAIL   |
| N=1000  | 8.85e-3      | 1e-6      | FAIL   |

## Root Cause Analysis

### Primary Root Cause: DWSNets Library Runtime Failure
The DWSNets external library fails at runtime with a shape mismatch error when processing MNIST FC-MLP zoo weight vectors:
- **Error location:** `weight_to_weight.py:832` — `RuntimeError: The size of tensor a (9) must match the size of tensor b (16) at non-singleton dimension 2`
- **Cause:** DWSNets library assumes CNN-style weight shapes but MNIST FC-MLP weights have different dimension structure
- **Effect:** DWSNet silently falls back to MLP backbone (model._use_dws=True flag remains set, but equivariant forward path fails)
- **Consequence:** MLP backbone is NOT permutation-equivariant → produces large var_pi ~1e-3

### Secondary Issue
H-E1 validation already noted "DWSNet MLP fallback due to OOM with 784-dim inputs" but this was attributed to OOM. H-M1 revealed the deeper issue: DWSNets library cannot handle FC-MLP weight dimensions at all.

## Lessons Learned
1. **Library compatibility must be verified BEFORE designing hypothesis:** DWSNets was designed for CNN weight spaces; its applicability to FC-MLP weight spaces was assumed but not verified
2. **model._use_dws flag is unreliable indicator:** The flag indicates intent but not successful execution
3. **H-E1 "DWSNet MLP fallback" was a warning sign:** Should have triggered deeper investigation before H-M1
4. **Permutation invariance verification requires confirmed equivariant path**

## Cascade Effects
- **H-M3** (depends on h-m1): BLOCKED

## Pipeline Action
Route to Phase 0 for hypothesis redesign. Core issue is library incompatibility, not a parameter issue.

## Timestamp
2026-03-16T12:00:00Z
