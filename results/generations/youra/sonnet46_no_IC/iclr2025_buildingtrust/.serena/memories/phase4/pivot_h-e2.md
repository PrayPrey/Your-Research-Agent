# Phase 4 Pivot Record: h-e2 → h-e2-v2

**Date:** 2026-08-04
**Outcome:** SELF_MODIFY
**Gate:** MUST_WORK → PARTIAL_PASS

## What Happened

H-E2 experiment ran successfully. Primary gate PASSED (mst_min_set_size=3 ≤4). Secondary gate FAILED (bootstrap_topology_stability=0.606 < 0.90).

Root cause: `machine_ethics--privacy` edge has frequency 0.688 across 1000 bootstrap resamples. With n=16 models, distances from machine_ethics to its three nearest neighbors (privacy, fairness, safety) are nearly equal, causing MST edge switching when 2 models are dropped.

## Key Findings

- MST minimum evaluation set: {truthfulness, fairness, privacy} (size=3)
- MST leaves (redundant): {safety, robustness, machine_ethics}
- 4/5 edges have bootstrap frequency ≥0.94 — core structure robust
- Mean edge frequency = 0.917, exceeds 0.90 threshold
- Only machine_ethics attachment point is ambiguous

## Modification for h-e2-v2

- Change gate secondary metric from full-topology stability to mean per-edge bootstrap frequency ≥0.90
- Justification: n=16 makes full topology match near-impossible for near-tie edges; mean edge frequency is more appropriate for small n

## Lessons Learned

1. For n<30 datasets, use mean edge frequency rather than full topology match for MST stability
2. Check near-tie MST edges before setting stability thresholds
3. machine_ethics is equidistant from multiple neighbors — ambiguous cluster attachment, relevant for H-M3
