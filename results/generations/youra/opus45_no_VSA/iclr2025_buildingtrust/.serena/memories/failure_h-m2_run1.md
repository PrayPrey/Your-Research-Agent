# Phase 4 Failure Record: h-m2 (Run 1)

**Date:** 2026-08-08T07:36:00Z
**Hypothesis:** h-m2
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_PREMISE_INVALID
**Gate Type:** MUST_WORK

## Hypothesis Statement

Benchmarks were designed to measure different constructs (truthfulness vs. bias vs. toxicity), causing low cross-correlation

## Performance Summary

| Metric | Expected | Actual | Status |
|--------|----------|--------|--------|
| Low-ρ Pairs Found | ≥1 | 0 | FAIL |
| Construct Alignment Score | >0.5 | N/A | FAIL |

## Root Cause Analysis

- All benchmark pairs showed HIGH correlation (ρ = 0.80-0.87), contradicting hypothesis premise
- No low-ρ pairs exist (threshold |ρ| < 0.5)
- Model quality appears to be confounding variable — good models score well on ALL benchmarks
- Safety training may affect all trustworthiness dimensions similarly, creating correlation

## Lessons Learned

1. Different construct labels (truthfulness/bias/toxicity) do NOT guarantee low correlation
2. Model-level factors (training data, scale, RLHF) may dominate over construct-specific effects
3. Synthetic HELM data may overestimate correlation due to shared generative process
4. Need to examine alternative mechanisms for cross-benchmark orthogonality

## Feedback for Next Phase

### Suggested Modifications
- Investigate model-level factors (training data source, scale, RLHF intensity) as mechanism
- Consider benchmark methodology differences rather than construct differences
- Try analysis on real HELM data to avoid synthetic correlation artifacts

### What NOT To Do
- Do not assume construct labels predict correlation structure
- Do not rely solely on construct taxonomy for orthogonality explanation

### What Showed Promise
- H-M1 validated significant between-family variance — mechanism exists, just different than hypothesized
- Correlation analysis methodology itself is sound

## Routing Decision

**MUST_WORK FAIL → Route to Phase 0**

This mechanism hypothesis fails to explain the expected pattern. Pipeline should route to Phase 0 for new research direction.

---
*For cross-phase reference*
*Written at: 2026-08-08T07:36:00Z*