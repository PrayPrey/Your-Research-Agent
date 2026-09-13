# Failure Record: h-e1 (MUST_WORK FAIL)

**Hypothesis ID:** h-e1
**Phase:** Phase 4
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Date:** 2026-08-09

## Hypothesis Statement
Final-layer gradient cosine similarity is significantly lower on Waterbirds (spurious) than Shuffled Waterbirds (decorrelated) during early training, with non-overlapping 95% CIs.

## Experiment Results
- **Spurious (Waterbirds):** cosine_sim = 0.926 (95% CI: [0.926, 0.926])
- **Control (Shuffled):** cosine_sim = 0.393 (95% CI: [0.172, 0.601])
- **CI Overlap:** False
- **Hypothesis Supported:** False

## Root Cause Analysis
**DIRECTION REVERSED:** The hypothesis predicted spurious correlations would produce LOWER gradient cosine similarity due to "opposing group-conditional feature-label correlations inducing directional gradient conflict."

Actual finding: Spurious correlations produce HIGHER gradient cosine similarity (0.926 vs 0.393).

This indicates the underlying mechanism is fundamentally incorrect:
1. Spurious correlations do NOT induce gradient conflict as theorized
2. Instead, spurious correlations appear to ALIGN gradients (possibly because majority/minority groups both learn the spurious feature initially)
3. The decorrelated control shows MORE gradient variance, not less

## Lessons Learned
1. **Mechanism prediction was inverted:** High spurious correlation → high gradient alignment, not conflict
2. **Early training dynamics differ from theory:** Groups may converge on spurious features together before diverging
3. **Gradient cosine similarity may still be diagnostic** but in the opposite direction than hypothesized

## Routing Decision
**Route to:** Phase 0 (New research question needed)
**Reason:** Core existence hypothesis falsified - fundamental mechanism prediction incorrect
