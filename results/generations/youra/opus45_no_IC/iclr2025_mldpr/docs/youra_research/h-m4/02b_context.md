# Phase 2B Context: H-M4

**Hypothesis ID:** H-M4
**Type:** MECHANISM
**Statement:** Reduced diversity hides benchmark-specific overfitting

## Full Statement (Under-If-Then-Because)

Under low evaluation diversity, if papers only evaluate on standard benchmarks, then benchmark-specific overfitting goes undetected, because no out-of-distribution tests exist.

## Rationale

This is the harm mechanism—why concentration matters. Requires proxy since we can't directly observe "hidden" overfitting.

## Variables

- **IV:** Evaluation diversity (entropy) per venue-year
- **DV:** Cross-benchmark performance variance (proxy for overfitting)
- **CV:** Model architecture, training data

## Success Criteria

- **Primary:** Negative correlation between entropy and cross-benchmark variance
- **Secondary:** Effect detectable in at least 2 of 3 venues

## Gate

- **Type:** SHOULD_WORK
- **If Fail:** PIVOT to qualitative evidence review

## Prerequisites

- H-M3 (COMPLETED): Papers follow standards for comparability
  - Result: Mann-Whitney U = 5,932,406,853.5, p ≈ 0, Cohen's d = 1.93
  - Mean citing overlap = 0.318 vs random = 0.014

## Verification Protocol

1. Identify papers with multi-benchmark evaluation (rare but exist)
2. Compute performance variance across benchmarks
3. Test if low-diversity venue-years have higher cross-benchmark variance
4. Use meta-analysis of existing multi-benchmark papers

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Dataset-Paper Links | PWC provides dataset tags for papers in target venues at 80%+ coverage |
| **Model** | N/A - Statistical Analysis | Cross-benchmark variance analysis |

## Connection to Hypothesis Chain

```
H-E1 (PASS) → H-M1 (PASS) → H-M2 (PASS) → H-M3 (PASS) → **H-M4** → H-M5
```

---

*Generated: 2026-08-10*
*Source: 02b_verification_plan.md Section 2.2*
