# Limitation Record: h-m3 (Run 1)

**Date:** 2026-03-20T15:30:00
**Hypothesis:** h-m3
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

MVC_p signal is driven by per-problem marginal pass rates, not cross-sample co-occurrence structure. Permuted baseline (which preserves marginals) achieves higher or equal Spearman rho with pass@1 in all 5 pairs. This means delta_rho = rho_orig - rho_perm is negative for all pairs, indicating MVC_p does not capture co-occurrence information beyond what marginals alone provide.

## Failed Checks

- llama3_humaneval: delta_rho=-0.1989, p_perm=1.000
- llama3_mbpp: delta_rho=-0.0558, p_perm=0.982
- deepseek_humaneval: delta_rho=-0.0658, p_perm=0.967
- deepseek_mbpp: delta_rho=-0.0251, p_perm=0.808
- codellama_mbpp: delta_rho=-0.0213, p_perm=0.745

## Partial Results

| Metric | Value |
|--------|-------|
| pass_rate | 0.0/5 |
| mean_delta_rho | -0.0734 |
| gate_type | SHOULD_WORK |
| gate_result | FAIL |

## Experiment Summary

TAU=4, K=5, N_PERM=1000, SEED=42. 0/5 pairs pass (required >=3/5 with delta_rho>0.05 OR p_perm<0.05). All delta_rho values are negative, meaning permuted MVC_p correlates better with pass@1 than original MVC_p. This is a fundamental limitation: MVC_p signal comes from marginal pass rates, not structural co-occurrence.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. Using a metric that explicitly captures co-occurrence structure beyond marginals (e.g., conditional entropy, mutual information)
2. Normalizing MVC_p by expected value under independence to isolate co-occurrence signal
3. Alternative diversity metrics that are not dominated by marginal effects

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-03-20T15:30:00*
*For cross-phase reference*
