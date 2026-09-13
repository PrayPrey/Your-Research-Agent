# Phase 2B Context: H-M3

**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Statement:** Attribution approximation methods make different assumptions about curvature (EK-FAC: Kronecker, TracIn: gradient-only, TRAK: random projection)

## Gate Condition

**Type:** SHOULD_WORK
**Success Criteria:** EK-FAC approximation error lower on GPT-2 than BERT; TracIn gradient signal stronger on BERT than GPT-2

## Prerequisites

- **H-M2:** PASSED (Hessian curvature divergence confirmed)
  - BERT top_eigenvalue: 0.0455
  - GPT-2 top_eigenvalue: 0.502
  - Difference: 90.93%

## Experimental Setup (from Phase 2A)

| Component | Selection |
|-----------|-----------|
| Dataset | SST-2 (GLUE benchmark) |
| Models | BERT-base-uncased, GPT-2 |
| Methods | EK-FAC (kronfluence), TracIn, TRAK |

## Continuation Context

H-M2 established that GPT-2 has 11x higher top eigenvalue than BERT. H-M3 tests whether this curvature difference affects approximation method accuracy:
- EK-FAC assumes Kronecker structure (should fit GPT-2's block structure better)
- TracIn uses raw gradients (may benefit from BERT's denser gradient patterns)
- TRAK uses random projections (theoretically architecture-invariant)

## Key Variables

- **IV:** Architecture type (BERT vs GPT-2)
- **DV:** Approximation error / reconstruction quality
- **CV:** Compute budget, dataset, model size
