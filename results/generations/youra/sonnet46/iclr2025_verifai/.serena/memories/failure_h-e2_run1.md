# Phase 4 Failure Record: h-e2 (Run 1)

**Date:** 2026-03-20T06:30:00Z
**Hypothesis:** h-e2 (H-SoftPassDiversity-v9, SPD-v9)
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_DIRECTION_WRONG
**Gate:** MUST_WORK
**Reflection Outcome:** ROUTED_TO_PHASE_0

## Performance Summary

| Pair | N | rho_obs | p_bootstrap | null_95th | passes |
|------|---|---------|-------------|-----------|--------|
| llama3_8b_humaneval | 164 | -0.1825 | 0.9840 | 0.1260 | FAIL |
| llama3_8b_mbpp | 377 | -0.3844 | 1.0000 | 0.0851 | FAIL |
| deepseek_coder_humaneval | 164 | -0.5162 | 1.0000 | 0.1329 | FAIL |
| deepseek_coder_mbpp | 377 | -0.3875 | 1.0000 | 0.0852 | FAIL |
| codellama_7b_mbpp | 377 | -0.3575 | 1.0000 | 0.0898 | FAIL |

**Pairs passing: 0/5 (required: 3)**
**Gate satisfied: false**

## Root Cause Analysis

- Hypothesis direction wrong: Z_p is NEGATIVELY correlated with soft_pass@k across ALL 5 pairs
- Z_p normalization by Bernoulli null creates systematic negative coupling with soft_pass@k
- Z_p=0 forced for mu=1.0 problems (easy problems), losing signal precisely where soft_pass@k is high
- Degenerate problems (std_null=0): 10-32% per pair (mu=1.0 or 0.0) — forced Z_p=0
- Medium-difficulty problems have real IQR variation but rho is still negative
- The normalized excess dispersion Z_p does not track soft_pass@k — it tracks uncertainty/hardness inversely

## Lessons Learned

1. IQR-based dispersion normalized by Bernoulli null is negatively coupled to pass rate, not positively
2. Problems with mu≈1.0 (easy) have near-zero IQR and near-zero Z_p, but high soft_pass@k — this anti-correlation is structural
3. The Bernoulli null normalization (std_null in denominator) amplifies noise for medium-difficulty problems
4. Excess dispersion beyond IID noise does NOT predict soft_pass@k — it may predict uncertainty instead
5. H-E1 passed (IQR > 0 exists), but H-E2 failed (IQR does not positively predict soft_pass@k)

## What NOT to Do in Phase 0

- Do NOT use IQR of soft_pass scores normalized by Bernoulli null as pass@k predictor
- Do NOT assume excess dispersion predicts performance — it predicts DIFFICULTY, not ABILITY
- Do NOT use Z_p = (IQR_obs - E_null) / std_null as the core metric

## Cascade Effects

- H-M1 (partial Spearman across difficulty strata): CASCADE_FAILED
- H-M2 (cross-model generalization): CASCADE_FAILED
- H-M3 (calibration via ECE): CASCADE_FAILED

## Pipeline Routing

- **Route to:** Phase 0
- **Reason:** MUST_WORK gate failure — methodology fundamentally wrong direction
- **Action:** Redesign hypothesis — explore alternative diversity metrics that positively predict pass@k

---
*Written at: 2026-03-20T06:30:00Z*
*For cross-phase reference*
