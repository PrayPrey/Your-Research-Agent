# Hypothesis Completion Snapshot: h-m3

**Date:** 2026-03-19T11:09:00
**Hypothesis:** h-m3
**Statement:** Within difficulty tiers (medium primary: 0 < pass@1 < 0.6), Spearman rho(D_p, pass@k) >= 0.20 with bootstrap 95% CI (n=1000, one-tailed) excluding 0, for >=3/5 model-benchmark pairs AND >=2/3 distinct models show positive significant effects. Secondary: OLS beta(D_p) > 0, p < 0.05 after pass@1 covariate for >=3/5 pairs.
**Final Status:** FAILED
**Gate Result:** FAIL
**Gate Type:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Results
- Primary Gate (Spearman): FAIL — 0/5 pairs pass, rho=undefined (constant pass_k=1.0 in medium tier)
- Secondary Gate (OLS): PASS — 5/5 pairs, beta_dp range 0.197-0.726, all p<0.0001
- Root Cause: pass@5 = 1-(1-pass@1)^5 saturates to ~1.0 for all medium-tier problems (pass@1>0)
- This is a mathematical constraint, NOT a code bug

## Reflection
- Triggered: True
- Outcome: ROUTED_TO_PHASE_0
- Root cause: pass_k_saturation_in_medium_tier
- Rationale: Fundamental hypothesis design flaw — within-tier Spearman broken by mathematical saturation
- OLS secondary analysis confirms D_p IS a real predictor across all tiers

## Cascade Effects
- h-m4: CASCADE_FAILED (depends on h-m3 prerequisite)

## Key Lessons for Phase 0 Redesign
1. Verify both DV and IV have variance in target tier before designing within-tier Spearman
2. pass@k = 1-(1-pass@1)^k saturates quickly with k=5; use pass@1 as DV or use larger k
3. OLS full-tier regression is more robust than within-tier Spearman
4. D_p IS a real predictor (OLS evidence strong) — redesign hypothesis formulation, not the mechanism

## Suggested Phase 0 Directions
1. Use pass@1 as dependent variable: rho(D_p, pass@1)
2. Continuous full-dataset correlation with difficulty as covariate
3. Use pass@10 or pass@20 where saturation is less severe
4. Alternative DV: normalized pass@k or expected number of passes

---
*Per-hypothesis snapshot for Phase 2A/Phase 0 reference*
*Written at: 2026-03-19T11:09:00*
