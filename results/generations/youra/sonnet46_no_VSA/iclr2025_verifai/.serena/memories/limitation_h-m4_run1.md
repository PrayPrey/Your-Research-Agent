# Limitation Record: h-m4 (Run 1)

**Date:** 2026-08-03T18:00:00+00:00
**Hypothesis:** h-m4
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate PARTIAL: Kendall τ ≤ 0.60 criterion met (τ = 0.40), but permutation p-value (0.4833) failed p < 0.05 threshold and partial ΔR² (0.0044) and cross-model gap (0.0069) both far below 0.10 thresholds. Root cause is structural: with n=5 models, exact permutation tests on Kendall τ cannot achieve p < 0.05 for τ = 0.4. The minimum two-sided p achievable at n=5 is ≈ 0.017 (only at |τ| = 1.0). All rank-correlation statistical tests on n=5 face the same discrete power floor — no code or method modification can fix this. ΔR² and cross-model gap are genuine null findings (not low-power artifacts): model-family identity adds negligible explanatory power beyond pass@1⋆ and log(size).

## Failed Checks

- permutation_p_value < 0.05 (actual: 0.4833 — structurally unachievable at n=5 for τ=0.4)
- partial_delta_r2 ≥ 0.10 (actual: 0.0044 — genuine null finding)
- cross_model_gap ≥ 0.10 (actual: 0.0069 — genuine null finding, very homogeneous task-level behavior)

## Partial Results

| Metric | Value |
|--------|-------|
| kendall_tau | 0.4000 (PASS: ≤ 0.60) |
| permutation_p_value | 0.4833 (FAIL: need < 0.05) |
| partial_delta_r2 | 0.0044 (FAIL: need ≥ 0.10) |
| cross_model_gap | 0.0069 (FAIL: need ≥ 0.10) |
| n_model_task_pairs | 1815 |
| mixedlm_converged | True |
| spearman_rho | 0.6000 |
| r2_full | 0.5005 |
| r2_reduced | 0.4961 |

## Experiment Summary

Cross-model contract-satisfaction orthogonality study across 5 LLM families (gpt-4o-mini, deepseek-coder-v2-lite, codellama-34b, codellama-13b, claude-3-haiku), 363 tasks (HumanEval+, MBPP+), 1,815 model-task pairs. Kendall τ = 0.40 between contract-satisfaction ranking and pass@1⋆ ranking — moderate, consistent with partial orthogonality. However, with only n=5 models, the exact permutation test (SciPy pairings mode, 14,400 null samples) yields p = 0.4833 — correct for n=5 but not significant. Model rankings partially invert: gpt-4o-mini ranks 1st on contract-satisfaction but 2nd on pass@1⋆; claude-3-haiku ranks last on contract but 3rd on pass@1⋆. Task-controlled residual variance across models extremely small (gap = 0.007), indicating high between-task variance dominates, low between-model variance at task level.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Expand model set to n ≥ 10 for adequate statistical power at α = 0.05 with τ ≈ 0.4
2. The near-zero ΔR² is interpretable as genuine: after controlling for capability and size, model-family contract behavior is largely homogeneous — this itself is a finding worth reporting
3. Consider reframing as a publishable null/partial result: moderate τ = 0.40 shows rankings are not identical (not perfectly correlated), but sample size insufficient for confirmation
4. HumanEval+ shows lower τ (0.20) vs MBPP+ (0.40) — orthogonality stronger on algorithmic tasks; worth investigating with larger model sets

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-03T18:00:00+00:00*
*For cross-phase reference*
