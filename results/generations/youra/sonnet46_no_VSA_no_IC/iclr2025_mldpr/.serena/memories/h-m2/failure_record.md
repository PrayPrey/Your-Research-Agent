# H-M2 Failure Record — ROUTED_TO_PHASE_0

**Date:** 2026-08-21
**Hypothesis:** H-M2 — Benchmark-stitching sigmoid difficulty calibration
**Phase:** Phase 4
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Failure Summary

- 20 qualifying pairs from H-E1 top20_pairs processed
- 13/20 skipped (n_pre2020 < 5) — few-shot benchmarks lack pre-2020 history
- 7/20 attempted — all degenerate (R² < 0, mean=-0.40)
- fraction_pass = 0.0% (required ≥80%)

## Root Cause

H-E1 top20_pairs are few-shot learning benchmarks (Mini-ImageNet, Tiered ImageNet, CIFAR-FS k-shot variants). These benchmarks:
1. Emerged post-2018 — minimal pre-2020 model coverage
2. Score variance dominated by shot-count, not model capability
3. Incompatible with sigmoid difficulty model assumptions

Implementation is correct (TRF optimizer, L2 regularization, expit). Domain is wrong.

## Lessons Learned

- Sigmoid difficulty calibration requires ≥20 pre-2020 models per benchmark pair
- k-shot variant pairs (same dataset, different shots) are unsuitable calibration targets
- H-E1 pair selection by overlap_count does not ensure pre-2020 temporal depth
- Mean-proxy C_m for val R² is too crude for small val sets (n_val=2–12)

## Recommendations for Phase 0 Redesign

1. Require ≥20 pre-2020 models per pair in qualifying criteria
2. Exclude k-shot variant pairs from difficulty calibration scope
3. Consider IRT 3-parameter model for narrow-score-range benchmarks
4. Focus on traditional classification benchmarks (ImageNet, CIFAR-10 full) with confirmed pre-2020 depth
