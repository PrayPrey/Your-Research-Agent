# Hypothesis Completion Snapshot: h-m1

**Date:** 2026-03-20T16:40:00Z
**Hypothesis:** h-m1 (H-MVC_p-v12)
**Title:** MVC_p Independent OLS Signal Beyond LOOM Difficulty Proxy
**Statement:** OLS regression pass@1 ~ beta0 + beta1*LOOM + beta2*MVC_p with HC3 robust SEs; gate: DeltaR2(MVC_p|LOOM) >= 0.02 AND beta2 > 0 AND p_beta2 < 0.05 for >=3/5 model-benchmark pairs
**Final Status:** COMPLETED
**Gate Type:** MUST_WORK
**Gate Result:** PASS

## Results

| Pair | n | DeltaR2 | beta2 | p_beta2 | VIF_ok | Gate |
|------|---|---------|-------|---------|--------|------|
| llama3_humaneval | 164 | 0.1562 | 0.3569 | 6.24e-11 | OK | PASS |
| llama3_mbpp | 378 | 0.3073 | 0.4673 | 2.16e-44 | OK | PASS |
| deepseek_humaneval | 164 | 0.1546 | 0.3119 | 8.87e-09 | OK | PASS |
| deepseek_mbpp | 378 | 0.2737 | 0.4665 | 1.17e-36 | HIGH - ridge confirms + | PASS |
| codellama_mbpp | 378 | 0.4347 | 0.3817 | 2.06e-63 | OK | PASS |

- n_passing: 5/5
- Mean DeltaR2: 0.2653 (range 0.155-0.435)
- Mean beta2: 0.3969 (all positive)
- All p << 0.0001

## Key Lessons

- HC3 robust SEs: conf_int() returns ndarray not DataFrame with newer statsmodels; use hasattr(ci,'iloc') check
- VIF > 5 for deepseek_mbpp; ridge sensitivity alpha=[0.1,1.0,10.0] confirms sign=+1.0
- HumanEval pairs have only 1 LOOM source (documented in JSON, not a gate violation)
- numpy._core ModuleNotFoundError when loading pkl with numpy 1.26 + scipy mismatch; fix: upgrade scipy
- evaluate_gate: secondary metrics conditional on 'delta_r2' key present in results

## Reusable Functions (h-m1/code/run_experiment.py)

- compute_loom: string containment filter `focal_benchmark in k`, warns on 1-source
- compute_vif: predictor-only DataFrame (NO intercept column)
- fit_ols_mechanism: HC3, beta2=params[2], version-compatible CI extraction
- evaluate_gate(per_pair_results, gate_min_pairs=3)

## For h-m2 (tau sensitivity, READY)

- Extend PAIRS loop over tau in {3,4,5}
- Reuse all functions from h-m1
- Keep sorted(B_p_dict.keys()) for determinism
- PAIRS must retain "benchmark" key
