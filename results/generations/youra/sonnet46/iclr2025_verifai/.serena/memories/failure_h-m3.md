# Phase 4 Failure Record: h-m3
**Date:** 2026-03-19
**Phase:** Phase 4
**Failure Type:** MUST_WORK_FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Hypothesis
Within difficulty tiers (medium primary: 0 < pass@1 < 0.6), Spearman rho(D_p, pass@k) >= 0.20 with bootstrap 95% CI (n=1000, one-tailed) excluding 0, for >=3/5 model-benchmark pairs AND >=2/3 distinct models.

## Gate Result
- **Primary gate (Spearman):** FAIL (0/5 pairs pass, rho=null for all — constant pass_k)
- **Secondary gate (OLS):** PASS (5/5 pairs, beta_dp: 0.197-0.726, all p << 0.0001)

## Root Cause
**Fundamental structural flaw**: In the medium tier (0 < pass@1 < 0.6), pass@k (pass@5) = 1.0 uniformly for ALL problems. When pass@1 > 0 and k=5, pass@5 = 1 - (1-pass@1)^5 ≈ 1.0. The medium tier filter (pass@1 > 0) guarantees pass@5 = 1.0 → zero variance → Spearman undefined. NOT a code bug — mathematical constraint.

## Positive OLS Signal
- delta_R2: 0.108-0.190 across all 5 pairs when D_p added to OLS model
- D_p IS a real predictor of pass_k in full-tier regression
- Future redesign should leverage this OLS evidence

## Lessons Learned
1. Verify both variables have variance in target tier before designing within-tier Spearman
2. pass@k = 1-(1-pass@1)^k → saturates quickly; use smaller k or continuous metrics
3. OLS full-tier is more robust than within-tier Spearman
4. h-m4 CASCADE_FAILED (depends on h-m3)

## Routing
ROUTED_TO_PHASE_0 — fundamental redesign needed.
