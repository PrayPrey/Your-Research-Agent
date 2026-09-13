# Limitation Record: h-c1 (Run 1)

**Date:** 2026-08-02T18:30:00+00:00
**Hypothesis:** h-c1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

SHOULD_WORK gate not satisfied: η² criterion shows source identity effect NOT attenuated at 7B vs 1.3B scale. η²_7B (0.9772) > η²_1.3B (0.9119) on HumanEval — opposite direction to hypothesis prediction.

Root cause: At 7B scale, seed variance collapsed to near-zero (σ² ≈ 0.00043 vs 0.01655 at 1.3B). With within-group variance near zero, η² = SS_between / SS_total approaches 1.0 even when absolute between-condition spread is smaller (0.055 vs 0.319 at 1.3B). η² metric inflates at 7B due to seed convergence, not larger condition effects.

## Failed Checks

- η²_7B < η²_1.3B on HumanEval (0.9772 > 0.9119 — NOT attenuated)
- η²_7B < η²_1.3B on MBPP (incomplete — 4/12 evals failed with parse errors)

## Partial Results

| Metric | Value |
|--------|-------|
| η²_7B (HumanEval) | 0.9772 |
| η²_1.3B (HumanEval) | 0.9119 |
| absolute_spread_7B | 0.055 |
| absolute_spread_1B | 0.319 |
| humaneval_evals_complete | 12/12 |
| mbpp_evals_complete | 8/12 |

## Experiment Summary

All 12 SFT checkpoints trained on deepseek-coder-7b-base (4 conditions × 3 seeds). HumanEval evaluation 12/12 complete; MBPP 8/12 (4 parse failures). The source identity effect is preserved at 7B but becomes more deterministic (seeds converge within condition). This constitutes a qualitatively different learning dynamic — not attenuation. Absolute between-condition spread (0.055) is smaller than 1.3B (0.319) but η² inflates due to seed collapse.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Use absolute condition spread as primary scale-comparison metric alongside η²
2. η² is not appropriate for scale comparison when seed variance differs substantially between scales
3. Variance-normalized effect size (Cohen's d on condition means) as alternative metric
4. MBPP evaluation at 7B needs fresh run (4 parse failures not recovered in this run)

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-02T18:30:00+00:00*
*For cross-phase reference*
