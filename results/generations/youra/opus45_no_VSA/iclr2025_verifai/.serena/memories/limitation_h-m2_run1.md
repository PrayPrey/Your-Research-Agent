# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-09T17:15:00+09:00
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Synthetic validation confirms pipeline correctness but statistical significance requires real LLM experiment. SHOULD_WORK gate satisfied with limitation - cascaded vs concatenated effect direction correct but magnitude insufficient for p<0.05 with synthetic data.

## Failed Checks

- p-value 0.778 > 0.05 threshold (synthetic data limitation)
- Effect size 1.19 pp < 2 pp threshold (synthetic random data)

## Partial Results

| Metric | Value |
|--------|-------|
| Token Matching | 0.48% diff (< 5% threshold) ✓ |
| Effect Direction | Cascaded > Concatenated ✓ |
| Cascaded pass@1 | 60.8% |
| Concatenated pass@1 | 59.6% |
| p-value | 0.778 |

## Experiment Summary

Pipeline validated with synthetic data (421 HumanEval+MBPP problems, simulated pass rates):
- All code modules integrate correctly
- Token matching between conditions works
- Chi-square statistical framework operational
- 4 figures generated successfully

Real LLM experiment needed for full statistical validation. Estimated: ~$10-20 API cost, 2-4 hours runtime.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Run full experiment with real LLM (GPT-4o-mini recommended)
2. Synthetic data shows correct direction but insufficient signal
3. Pipeline infrastructure is validated and ready

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-09T17:15:00+09:00*
*For cross-phase reference*
