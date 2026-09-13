# H-M2 Null Result — DPO vs SFT Q1 Delta Variance (SHOULD_WORK)

**Date:** 2026-03-17
**Gate:** SHOULD_WORK NULL RESULT → LIMITATION_RECORDED

## Finding

Directional hypothesis (DPO > SFT mean delta_var in Q1) FAILED on all 3 datasets:
- MMLU: d=-0.490, p=1.000 (SFT > DPO)
- TruthfulQA: d=-1.536, p=1.000 (SFT > DPO strongly)
- ARC: d=-0.225, p=0.992 (SFT > DPO)

## Behavioral Signature

DPO quintile trend (MMLU): Q1=0.71, Q2=1.00, Q3=1.19, Q4=2.61, Q5=3.38
SFT flat: Q1=0.22, Q2=0.23, Q3=0.25, Q4=0.29, Q5=0.28

DPO has high spread but low mean in Q1; SFT has higher mean but uniform distribution.

## Key Implementation Fix

OLS residuals are zero-mean — must use raw `delta_var_q` for t-test (not residuals).
Fix: `q1_residuals = delta_var_q` in compute_variance_by_quintile().

## Pipeline Action

LIMITATION_RECORDED → pipeline continues to Phase 5.
