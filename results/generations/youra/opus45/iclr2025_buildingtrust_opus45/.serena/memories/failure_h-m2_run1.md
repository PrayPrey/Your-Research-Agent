# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-03-23T04:41:50Z
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** PARTIAL
**Failure Type:** HYPOTHESIS_NOT_SUPPORTED

## Hypothesis Statement

> Under longer reasoning contexts (CoT vs 0-shot), if autoregressive conditioning is applied, then H_rest decreases, because additional context tokens sharpen next-token probability distributions as a mathematical consequence of conditional probability factorization.

## Performance Summary

| Condition | Mean delta_H_rest | p-value | Cohen's d | Direction |
|-----------|-------------------|---------|-----------|-----------|
| Short CoT | +0.0116 | 0.703 | 0.025 | WRONG (positive) |
| Extended CoT | +0.0766 | >0.999 | 0.195 | WRONG (positive, significant) |
| Reflection | -0.0261 | 0.120 | -0.054 | CORRECT (not significant) |

## Root Cause Analysis

- **Primary hypothesis NOT supported:** CoT prompting does NOT systematically reduce H_rest (conditional non-max entropy) as predicted.
- **Extended CoT shows OPPOSITE effect:** Significantly INCREASES H_rest (+0.077, t=4.23, p<0.001), contradicting the sharpening hypothesis.
- **Reflection shows correct trend but lacks significance:** Mean decrease of -0.026 (p=0.12) is in predicted direction but not statistically significant.
- **Secondary criterion partially satisfied:** Short CoT shows marginally significant negative correlation (r=-0.089, p=0.054) between delta_H_rest and delta_tokens.

## Lessons Learned

1. **Autoregressive conditioning does NOT universally sharpen distributions.** The mathematical expectation that more context tokens should reduce entropy does not hold for CoT reasoning in LLMs.

2. **Extended reasoning may EXPLORE more alternatives.** The increased H_rest under Extended CoT suggests the model considers a broader set of possible answers during extended reasoning, rather than narrowing to a single choice.

3. **Prompt-induced effects on H_rest are condition-specific.** Different prompt types affect distributional geometry differently, with no universal sharpening mechanism.

4. **The mechanism connecting CoT to calibration is more complex.** If H_rest increases under CoT but calibration is still affected, the causal pathway must involve factors beyond simple distribution sharpening.

## Feedback for Next Phase

### Suggested Modifications
- Revise theoretical framework to account for CoT-induced distribution BROADENING
- Investigate whether H_rest variation (regardless of direction) predicts calibration residuals (H-M3)
- Consider alternative mechanisms: attention-based uncertainty, token-level confidence aggregation

### What NOT To Do
- Do not assume autoregressive conditioning always sharpens distributions
- Do not conflate prompt type effects with general entropy reduction

### What Showed Promise
- Reflection prompts show trend toward expected sharpening (though not significant)
- Short CoT shows negative correlation between more tokens and more sharpening
- H_rest variation IS systematic across conditions (confirmed by H-E1)

## Gate Evaluation

- **Gate Type:** MUST_WORK
- **Result:** PARTIAL
- **Primary Criterion:** NOT SATISFIED (no condition shows significant H_rest decrease)
- **Secondary Criterion:** PARTIALLY SATISFIED (Short CoT correlation r=-0.089, p=0.054)

## Implications for Pipeline

- H-M2's PARTIAL result does NOT block H-M3 testing
- H-M3 can still test whether H_rest variation (regardless of sharpening direction) predicts calibration residuals
- The broader hypothesis about distributional geometry's role in calibration remains testable

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this failure informs new research directions
- **Phase 2A:** Informs hypothesis refinement to avoid similar assumptions
- **Phase 6 Discussion:** Included in paper's Discussion section as a falsified mechanism

---
*Failure recorded at: 2026-03-23T04:41:50Z*
*For cross-phase reference*
