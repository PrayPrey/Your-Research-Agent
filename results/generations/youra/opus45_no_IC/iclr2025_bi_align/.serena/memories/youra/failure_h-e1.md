# Failure Record: H-E1

**Hypothesis:** Bidirectional adaptation signals exist and are extractable from multi-turn dialogue datasets
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Result:** FAIL
**Date:** 2026-08-10

## Failure Summary

Coverage rate 43.6% failed to meet 80% threshold.

## Root Cause

The hh-rlhf helpful-base dataset contains many short conversations (1-2 turns per side). Requiring ≥3 turns per participant filters out 56% of conversations, making 80% coverage impossible.

## What Worked

- Feature extraction pipeline correctly implemented
- All 5 trajectory features computable on valid conversations
- All feature variances > 0 (signal exists in data)
- 20,140 conversations successfully processed

## What Failed

- Coverage threshold (80%) incompatible with dataset structure
- Dataset assumption (most conversations have ≥3 turns) incorrect

## Metrics

| Metric | Value |
|--------|-------|
| Total Conversations | 46,189 |
| Valid (≥3 turns/side) | 20,140 (43.6%) |
| Coverage Threshold | 80% |
| Gap | -36.4% |

## Recommended Pivot Options

1. Lower MIN_TURNS from 3 to 2
2. Lower coverage threshold from 80% to 40-50%
3. Use LMSYS-Chat-1M (longer conversations)
4. Compute per-turn features instead of trajectories

## Files

- Validation report: `h-e1/04_validation.md`
- Experiment results: `h-e1/experiment_results.json`
- Code: `h-e1/code/`

## Routing

Returns to Phase 2A for hypothesis redesign.
