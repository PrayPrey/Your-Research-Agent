# Phase 2B Context: H-M2

**Generated:** 2026-08-18
**Source:** 02b_verification_plan.md

---

## Hypothesis Information

- **ID:** H-M2
- **Type:** MECHANISM
- **Statement:** Different attention structures create different Hessian curvature patterns (block-diagonal vs dense)
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-M1 (PASSED)

## Rationale

This tests whether attention structure differences propagate to affect curvature—the key link to why approximation methods behave differently. If attention patterns differ (proven by H-M1), then gradient computation through these patterns should create different Hessian structures.

## Success Criteria

- **Primary:** Measurable difference in Hessian spectrum between architectures
- **Secondary:** GPT-2 shows better Kronecker factorization fit

## Variables

- **IV:** Attention pattern structure (bidirectional vs causal)
- **DV:** Hessian spectrum characteristics
- **CV:** Model size (~110-125M), Training state (fine-tuned on SST-2)

## Verification Protocol

1. Compute Hessian eigenvalue spectrum for both architectures
2. Analyze Jacobian structure of attention layers
3. Compare curvature characteristics using random matrix theory metrics
4. Test Kronecker factorization fit quality

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | SST-2 (standard) | Binary sentiment classification allows both BERT and GPT-2 to perform natively |
| **Model** | BERT-base-uncased and GPT-2 | Matched layer count (12), similar params (110M vs 124M) |

## Previous Hypothesis Results

### H-M1 Results (Prerequisite - PASSED)
- BERT upper_sparsity: 0.0118 (near-zero = bidirectional full attention)
- GPT-2 upper_sparsity: 1.0 (fully sparse upper triangle = causal mask)
- Sparsity difference: 0.9882
- Samples tested: 872
- **Conclusion:** Attention pattern structure differs fundamentally between architectures

## Failure Response

IF fails: PIVOT to alternative curvature metrics

## Dependencies

- H-E1: PASSED (Architecture-method interaction exists)
- H-M1: PASSED (Attention patterns differ)

---

*Extracted from 02b_verification_plan.md for Phase 2C experiment design*
