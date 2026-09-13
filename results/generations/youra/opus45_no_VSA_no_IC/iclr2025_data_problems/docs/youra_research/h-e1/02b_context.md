# Phase 2B Context: h-e1

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None

## Hypothesis Statement

Attribution methods (TRAK, TracIn, Kronfluence) compute influence via mathematically distinct operations.

## Rationale

This is the foundational hypothesis establishing that the three attribution methods under study use fundamentally different mathematical operations:
- **TRAK:** Uses random projections and gradient sketching
- **TracIn:** Uses gradient dot products across training checkpoints
- **Kronfluence:** Uses Kronecker-factored approximations to Fisher information

## Success Criteria (PoC Level)

1. Code runs without error
2. Demonstrate each method computes influence differently (mathematical verification)
3. Show distinct computational signatures for each method

## Experimental Setup (from Phase 2B)

- **Models:** Start with small model for PoC validation
- **Methods:** TRAK, TracIn, Kronfluence
- **Dataset:** Standard benchmark (CIFAR-10 or similar for efficiency)
- **Validation:** Mathematical verification that operations differ

## Dependencies

None - this is the foundational hypothesis.

## Notes

This EXISTENCE hypothesis establishes the premise that methods are mathematically distinct before testing whether those distinctions create different sensitivity profiles (h-m1, h-m2).
