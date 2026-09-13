# Hypothesis Completion Snapshot: h-e1

**Date:** 2026-03-28T19:33:00+00:00
**Hypothesis:** h-e1 (FTE-SE Correlation)
**Statement:** First-Token Entropy achieves Spearman correlation |rho| >= 0.20 with Semantic Entropy on TruthfulQA (817 questions, N=20 responses, Mistral-7B-v0.1).
**Final Status:** FAILED
**Gate Result:** FAIL
**Gate Type:** MUST_WORK

## Results

- **Spearman rho:** 0.1307 (required >= 0.20)
- **p-value:** 1.79e-04 (required < 0.05) - PASS
- **CI lower:** 0.0647 (required > 0.05) - PASS
- **Overall Gate:** FAIL (effect size insufficient)

## Reflection

- **Outcome:** ROUTED_TO_PHASE_0
- **Root Cause:** First-Token Entropy captures structural variation (which token starts the response), not semantic uncertainty
- **Risk Materialized:** R1 (Structural-Semantic Independence, probability 0.45)

## Lessons Learned

1. FTE reflects lexical/structural variation, not semantic uncertainty
2. Statistical significance (p < 0.001) achieved due to large sample size, but effect size too small
3. Different uncertainty quantification approaches may capture fundamentally different phenomena

## Cascade Effects

- h-m1: CASCADE_FAILED
- h-m2: CASCADE_FAILED
- h-m3: CASCADE_FAILED

## Recommendations for Phase 0

- Do NOT pursue FTE variations
- Focus on metrics that measure semantic content variation
- Consider response embedding variance or clustering-based approaches

---
*Phase 4 Step 08 completion snapshot*
*Next action: ROUTE_TO_PHASE_0*
