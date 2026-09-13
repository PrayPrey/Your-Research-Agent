# H-E1 Routing Decision: ROUTED_TO_PHASE_2A

**Date:** 2026-08-21
**Hypothesis:** H-E1 (EXISTENCE / FOUNDATION)
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**reflection_outcome:** ROUTED_TO_PHASE_2A

## Failure Summary

- `complete_metadata_count = 1` (threshold: 200)
- PwC benchmark names and OpenML dataset names are from different domains — fuzzy join at threshold=85 yields only 36 matches from 1,096 PwC × 4,931 OpenML datasets
- `rank_reversal_rate` NaN for 97.2% of benchmarks (insufficient year-cohort data at min_models=3)

## Root Cause

PwC benchmarks are ML research leaderboards (GoPro, nuScenes, WN18RR, SQuAD).
OpenML is a repository of traditional tabular ML datasets (anneal, letter, mushroom).
They describe different entities — the join assumption in H-E1 is empirically falsified.

## Redesign Recommendations for Phase 2A

1. Drop OpenML join requirement — use PwC-internal data only
2. Drop Yang 2024 (HF Hub unavailable, proxy adds noise)
3. Reformulate gate: "PwC benchmarks with ≥10 papers and ≥3 result rows yield ≥500 records with reuse_rate + result_CoV"
4. Lower `min_models_per_cohort` to 2 for rank_reversal_rate (current: 3 — too sparse)
5. Source `class_count` from PwC task metadata rather than OpenML

## Reusable Code (carry forward to H-E1-v2)

- `ingest_pwc.py` — fetches 1,096 benchmarks + 30,928 result rows from `pwc-archive/evaluation-tables` (HF Hub; PwC REST API is down)
- `derive.py` — compute_reuse_rate, compute_result_cov, compute_rank_reversal_rate all correct
- `report.py` — coverage metrics + 5 figures
- `run.py` — pipeline entry point
