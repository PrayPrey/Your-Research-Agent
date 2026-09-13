# H-E2 SPD-v9 Phase 4 State

**Phase 4 COMPLETE 2026-03-20: H-E2 Spearman Correlation gate FAIL (MUST_WORK).**

## Result
- Gate: MUST_WORK FAIL
- Pairs passing: 0/5 (required: 3)
- All Spearman rho values NEGATIVE (range -0.183 to -0.516)
- Routing: ROUTED_TO_PHASE_0

## Per-Pair Results
| Pair | N | rho_obs | p_boot | null_95th | PASS? |
|------|---|---------|--------|-----------|-------|
| llama3_8b_humaneval | 164 | -0.1825 | 0.984 | 0.126 | FAIL |
| llama3_8b_mbpp | 377 | -0.3844 | 1.000 | 0.085 | FAIL |
| deepseek_coder_humaneval | 164 | -0.5162 | 1.000 | 0.133 | FAIL |
| deepseek_coder_mbpp | 377 | -0.3875 | 1.000 | 0.085 | FAIL |
| codellama_7b_mbpp | 377 | -0.3575 | 1.000 | 0.090 | FAIL |

## Root Cause
Z_p (normalized excess IQR via Bernoulli null) is NEGATIVELY correlated with soft_pass@k.
Hypothesis direction was wrong. The normalization creates structural negative coupling:
- Problems where mu=1.0 (all tests pass, easy problems) -> degenerate Z_p=0.0 at high soft_pass@k
- Non-degenerate problems with real IQR variation tend to be medium difficulty
- Z_p increases for problems where IID null predicts low IQR -> structurally intermediate difficulty

## Cascade Failures
- H-M1: CASCADE_FAILED (blocked by h-e2 FAIL)
- H-M2: CASCADE_FAILED (blocked by h-e2 FAIL)
- H-M3: CASCADE_FAILED (blocked by h-e2 FAIL)

## Archon
- Task ID: 98709031-0d8a-4932-86e9-83d25adbd942 -> done
- Project: ba263d33-bfec-4ca0-a017-1f94a432d656

## Lessons Learned for Phase 0
1. Z_p is negatively (not positively) correlated with soft_pass@k
2. Possible alternative hypotheses: Z_p as difficulty predictor (not performance calibrator)
3. Degenerate fraction is high (10-32%) -- mu=1.0 problems need better handling
4. The Bernoulli null normalization inverts expected signal direction
5. Consider using raw IQR (not normalized) or inverse Z_p as predictor

## Files
- Code: h-e2/code/main.py
- Results: h-e2/results/h-e2_results.json
- Report: h-e2/04_validation.md
- Figures: h-e2/figures/ (5 PNG files)
- State: 20260316_verifia/verification_state.yaml -> workflow.status = ROUTED_TO_PHASE_0
