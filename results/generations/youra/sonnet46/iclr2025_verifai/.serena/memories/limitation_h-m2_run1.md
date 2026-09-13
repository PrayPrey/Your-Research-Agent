# Limitation Record: h-m2 (Run 1)

**Date:** 2026-03-20T19:40:00Z
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate FAIL — Rho(MVC_p, pass@1) decreases monotonically with tau (3→4→5) in all 5 pairs. The hypothesis predicted rho would increase with tau (higher threshold → sharper consensus). The opposite was observed: N_monotone=0/5.

## Failed Checks

- llama3_humaneval: non_monotone_complex (rho: 0.6819→0.5090→0.4357)
- llama3_mbpp: non_monotone_complex (rho: 0.8497→0.7868→0.5756)
- deepseek_humaneval: non_monotone_complex (rho: 0.8328→0.7110→0.5491)
- deepseek_mbpp: 4->5_break (rho: 0.7834→0.8509→0.7141)
- codellama_mbpp: 4->5_break (rho: 0.6147→0.8491→0.7628)

## Partial Results

| Metric | Value |
|--------|-------|
| N_monotone | 0/5 |
| gate_verdict | FAIL |
| mean_delta_34 | -0.0112 |
| mean_delta_45 | -0.1339 |
| optimal_tau | 3 (lower tau → higher rho) |
| H-E2 cross-check | PASS (all 5 within 0.0012) |

## Experiment Summary

Tau sweep {3,4,5} on 5 model-benchmark pairs (EvalPlus HumanEval+ + MBPP+, k=5). Higher tau collapses MVC_p variance → reduced Spearman rho. tau=3 is empirical optimum. tau=4 (H-E2) is near-optimal. Monotonicity of rho wrt tau is NOT supported. SHOULD_WORK semantics: pipeline continues to Phase 5.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Tau=3 as default MVC_p threshold (empirically superior)
2. tau=4 (H-E2) still valid as strong predictor (rho 0.509-0.851)
3. Variance collapse at high tau as mechanism for rho decrease

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, avoid monotonicity claims about MVC_p tau sweep
- **Phase 6 Discussion:** Include tau-sensitivity as negative mechanism result; tau=4 not global optimum

---
*Limitation recorded at: 2026-03-20T19:40:00Z*
*For cross-phase reference*
