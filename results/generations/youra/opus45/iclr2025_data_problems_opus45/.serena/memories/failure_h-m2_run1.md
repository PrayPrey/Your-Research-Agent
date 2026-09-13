# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-03-24T03:05:00+00:00
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_FALSIFIED
**Gate Type:** MUST_WORK

## Hypothesis Statement

> Under entropy contraction, if we measure Hessian spectral properties, then spectral norm/trace ratio increases with generation, because narrower output distributions concentrate loss landscape curvature in fewer directions.

## Performance Gap

| Metric | Expected | Observed | Gap |
|--------|----------|----------|-----|
| Spectral Ratio Trend | Monotonic INCREASE | Monotonic DECREASE (after Gen 1) | OPPOSITE |
| Gen 0→5 Ratio Change | Positive | -0.068 (negative) | OPPOSITE |
| Correlation with Entropy | |r| > 0.5 | r = 0.14 | INSUFFICIENT |

## Key Observations

1. **Spectral ratio spiked at Gen 1** (0.08 → 0.62) due to temporary trace collapse
2. **Then monotonically DECREASED** from 0.62 to 0.016 (Gen 1→5)
3. **Trace INCREASED** from 2643 to 4090 (opposite of curvature concentration)
4. **Spectral norm DECREASED** from 221 to 64

## Root Cause Analysis

- The hypothesis assumed model collapse would CONCENTRATE curvature (higher spectral ratio)
- Instead, the loss landscape became MORE complex (higher trace, lower dominance)
- The "curvature concentration" mechanism is NOT supported by empirical evidence
- The transient spike at Gen 1 is likely model quickly fitting to simplified synthetic data

## Gate Criteria Evaluation

| Criterion | Required | Actual | Result |
|-----------|----------|--------|--------|
| SC-2: Monotonic Increase | 5/5 positive transitions | 1/5 positive | FAIL |
| SC-3: Control Stability | < 10x range | 13.82x range | FAIL |
| SC-4: Entropy Correlation | |r| > 0.5 | r = 0.14 | FAIL |

## Lessons Learned

1. **Hessian spectral properties do NOT track model collapse** - The ratio decreases, not increases
2. **Loss landscape complexity INCREASES during collapse** - Trace grows, suggesting more directions, not fewer
3. **Curvature concentration is not the mechanism** - Attribution concentration (if it exists) must have different cause
4. **Initial fitting creates transient artifacts** - Gen 1 spike is not representative of trend

## Impact on Hypothesis Chain

- **h-m3 (Damping Sweep):** BLOCKED - Premise of curvature concentration invalid
- **h-m4 (Diversity Anchoring):** Indirectly affected - Mechanism chain broken
- **Main Hypothesis:** Curvature concentration path FALSIFIED

## Feedback for Next Phase

### What NOT To Do
- Do not pursue Hessian-based mechanisms for model collapse
- Do not assume curvature concentration correlates with entropy reduction
- Do not use spectral ratio as indicator of collapse severity

### Alternative Directions to Explore
- Output distribution narrowing (entropy-based, not curvature-based)
- Effective rank reduction in hidden representations
- Gradient similarity collapse between training examples
- Feature collapse / representation degeneration

### What Showed Promise
- Entropy tracking correctly captured model collapse progression
- Experimental setup (NanoGPT, Shakespeare, 6 generations) was reliable
- Reality check tests passed - no mock model issues

---
*For cross-phase reference*
*Written at: 2026-03-24T03:05:00+00:00*
*Gate Result: MUST_WORK FAIL - Hypothesis FALSIFIED*
