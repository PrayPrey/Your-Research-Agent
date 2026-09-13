# Phase 2B Context: H-M3

**Date:** 2026-08-10
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Gate:** SHOULD_WORK

---

## Hypothesis Statement

Under implicit evaluation standards, if authors cite prior work, then they use same benchmarks as cited papers, because comparability requires shared evaluation.

## Rationale

Tests whether citation network drives benchmark homogeneity. If papers cite work X, they should evaluate on same datasets as X.

## Variables

- **IV:** Citation overlap between papers
- **DV:** Dataset overlap between papers
- **CV:** Venue, year, topic

## Success Criteria

- Primary: Citing pairs have higher dataset overlap than random (p < 0.01)
- Secondary: Effect size (Cohen's d) > 0.3

## Verification Protocol

1. Build citation network within venue-year
2. Compute Jaccard similarity of datasets between citing/cited pairs
3. Compare to random baseline (non-cited pairs)
4. Test if citation predicts dataset overlap beyond topic similarity

## Prerequisites

- H-M2: Convergence creates implicit evaluation standards - **PASSED**
  - β(prior_HHI) = 56.75, p = 1.51e-11
  - Effect persists with venue controls (β = 25.66, p = 0.0414)

## Gate Condition

- **Type:** SHOULD_WORK
- **Pass:** Citation-dataset overlap > random (p < 0.01)
- **Fail Action:** Document as limitation, continue to H-M4

## Failure Response

IF fails: EXPLORE alternative comparability mechanisms

## Dependencies

- H-E1: PASSED (21/21 venue-years valid HHI)
- H-M1: PASSED (Mann-Whitney p = 0.000319)
- H-M2: PASSED (β > 0, p < 0.05)

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| Dataset | PWC + Citation Data (Semantic Scholar API) | Need paper-to-paper citations + dataset tags |
| Model | N/A - Statistical Analysis | Jaccard similarity + permutation test |

## Data Requirements

1. **Citation Network:** Semantic Scholar API for NeurIPS/ICML/ICLR 2018-2024
2. **Dataset Tags:** PWC data from H-E1 cache
3. **Sample Size:** All citing/cited pairs within venue-years (~10K+ pairs expected)

## Previous Context (from H-M2)

- H-M2 established that high prior-year HHI predicts standard benchmark adoption
- This creates the "implicit standards" that H-M3 tests papers following
- H-M3 tests the mechanism: do papers actually follow citations for benchmark choice?

---

*Generated from 02b_verification_plan.md for Phase 2C experiment design*
