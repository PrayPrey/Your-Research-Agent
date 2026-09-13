# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-09T16:40:00+09:00
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Gate Type:** MUST_WORK

## Hypothesis Statement

Conditional repair lift Δ decreases monotonically with Jaccard overlap (β_overlap < -0.1 attenuation-corrected); Model B (with overlap) reduces CV RMSE by ≥5% vs Model A.

## Performance Summary

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| β_corrected | -0.0401 | < -0.1 | FAIL |
| RMSE Improvement | -2.15% | ≥ 5% | FAIL |
| β p-value | 0.008 | < 0.05 | PASS |

## Root Cause Analysis

- Mock mode execution: No OPENAI_API_KEY available
- H-E1 data has binary overlap distribution (0 or 1 only)
- No partial overlaps limit gradient estimation
- Mock model uses deterministic hash-based simulation

## Lessons Learned

1. Real API access required for valid hypothesis testing
2. Binary overlap distribution from H-E1 insufficient for regression
3. Mock validates pipeline correctness but not hypothesis validity
4. Direction correct (β negative) but effect size insufficient

## What Showed Promise

- Statistical significance achieved (p=0.008)
- Negative correlation direction matches hypothesis
- Pipeline and code structure validated

## Feedback for Re-run

- Set OPENAI_API_KEY environment variable
- Consider H-E1 with continuous Jaccard values (not binary)
- Increase problem sample size beyond 50

---
*Failure recorded at: 2026-08-09T16:40:00+09:00*
*For cross-phase reference*
