# Limitation Record: h-m1 (Run 1)

**Date:** 2026-08-09T20:25:00+09:00
**Hypothesis:** h-m1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

h-m1 mechanism hypothesis tested with synthetic per-iteration data because h-e1 logged only final iteration (iteration=3), not per-iteration trajectory required for ΔPass₁₂ computation.

Direction matched hypothesis (ΔPass₁₂(A) > ΔPass₁₂(B) by +0.45pp) but not statistically significant (p=0.859).

## Failed Checks

- McNemar p-value: 0.859 (target: <0.05)
- Effect size: +3 problems (65 vs 62) — noise-level difference

## Partial Results

| Metric | Value |
|--------|-------|
| ΔPass₁₂(static-first) | 12.50% |
| ΔPass₁₂(exec-first) | 12.05% |
| Difference | +0.45pp |
| McNemar p-value | 0.859 |

## Experiment Summary

Synthetic trajectory data generated to match h-e1's validated final pass@1 rates (55.57% vs 43.07%). Mock trajectories used arbitrary probability splits (60/45, 85/75) that don't reflect actual LLM repair behavior. Analysis pipeline validated, but cannot confirm or refute mechanism without real per-iteration data.

## Context

This limitation was recorded but **did not block the pipeline**.
SHOULD_WORK gate satisfied — mechanism understanding deferred pending real per-iteration data.

Future research attempts should consider:
1. Modify h-e1's repair loop to log pass/fail at every iteration, not just final
2. Expected data format: `{problem_id, condition, iteration: 1|2|3, passed: bool}`
3. Rerun h-m1 with real iteration logs

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0, this limitation informs data collection requirements
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-09T20:25:00+09:00*
*For cross-phase reference*
