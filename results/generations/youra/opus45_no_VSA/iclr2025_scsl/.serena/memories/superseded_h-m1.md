# Superseded Hypothesis Record

**Date:** 2026-08-09T12:49:00Z
**Hypothesis:** h-m1
**Superseded By:** Phase2A (new mechanism hypothesis needed)
**Status:** SUPERSEDED

## Supersede Reason

MUST_WORK gate FAILED. Mechanism hypothesis disproved by experimental evidence.

The hypothesis stated: "Gradient signal imbalance (majority contributes ~95% of gradients) causes anisotropic curvature smoothing where majority-aligned directions are preferentially flattened."

Experimental results showed the OPPOSITE:
- GCDR = 0.175 (< 1.0): Minority has MORE gradient concentration, not less
- HSR = 0.097 (< 1.0): Minority eigenvalues decrease at similar/slower rate
- SR > 1.0 (2.27-3.98): Confirms minority has higher curvature (from h-e1)

The mechanism exists but operates in the OPPOSITE direction to what was hypothesized.

## Compatibility Assessment

| Factor | Score/Result |
|--------|--------------|
| Compatibility Score | 0.0 |
| Recommendation | SUPERSEDE - Route to Phase 2A |
| Reasoning | Core mechanism claim falsified. Cannot modify - need fundamentally different explanation for why SR > 1.0 |

## Key Findings to Preserve

1. **h-e1 VALIDATED**: SR > 1.0 is real (range 2.32-4.17 across training)
2. **Gradient flow**: Minority actually has MORE concentrated gradients (GCDR < 1)
3. **Curvature evolution**: Minority eigenvalues don't flatten faster (HSR < 1)
4. **New direction needed**: Alternative mechanism explaining why minority maintains higher curvature

## Suggested Phase 2A Focus

- Why does minority maintain higher λ_max despite smaller sample size?
- Is it feature complexity? Harder decision boundary? Memorization?
- Consider: minority may be underfitting (high curvature = high loss landscape roughness)

## Timeline

1. h-e1 VALIDATED: SR > 1.0 confirmed
2. h-m1 implemented: gradient covariance + Hessian evolution analysis
3. GCDR and HSR both < 1.0 (opposite of prediction)
4. Decision: SUPERSEDE (mechanism falsified, not modifiable)
5. Route: Phase 2A for new mechanism hypothesis

---
*Superseded at: 2026-08-09T12:49:00Z*
*For cross-phase reference*