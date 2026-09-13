# Failure Record: H-M1

**Hypothesis:** ECE Calibration Loss Mechanism Test
**Date:** 2026-08-10
**Gate Type:** MUST_WORK
**Result:** FAIL

## Summary

H-M1 tested whether adding ECE (Expected Calibration Error) calibration loss during PPO training improves model calibration. The hypothesis failed at PoC-level validation.

## Metrics

| Metric | Baseline | Proposed | Delta |
|--------|----------|----------|-------|
| ECE | 0.7572 | 0.7653 | +1.08% |

## Failure Analysis

1. **ECE increased** instead of decreased with ECE-augmented training
2. PoC scale (50 steps, 1 seed) - may not reflect full-scale behavior
3. High baseline miscalibration (~76% ECE) in both conditions
4. Both models showed overconfidence pattern (82% confidence, 6% accuracy)

## Possible Causes

- Insufficient training steps for ECE loss to take effect
- ECE weight (0.1) may be too low
- Simplified reward model (length-based proxy) may not provide meaningful signal
- ECE loss gradient through confidence term may conflict with PPO objective

## Recommendations for Phase 2A Redesign

1. Increase ECE weight (try 0.5, 1.0)
2. Use proper reward model (not length proxy)
3. Consider alternative calibration methods (temperature scaling, focal loss)
4. Run full-scale experiment (100K steps, 3 seeds) before concluding

## Files

- Report: `h-m1/04_validation.md`
- Results: `h-m1/code/outputs/results.json`
- Figures: `h-m1/figures/`

## Route

ROUTED_TO_PHASE_2A for hypothesis redesign
