# Limitation Record: h-m1 (Run 1)

**Date:** 2026-08-02T15:45:00+00:00
**Hypothesis:** h-m1
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Cross-benchmark inversion pattern is absent on MBPP+. Full directional inversion (both HE+ and MBPP+) confirmed in 0/3 seeds, below the ≥2/3 threshold. HumanEval-only SFT achieves *higher* MBPP+ pass@1 than MBPP-only SFT across all seeds — the opposite of the expected specialization pattern.

## Failed Checks

- MBPP+ inversion absent: HumanEval-only outperforms MBPP-only on MBPP+ in all 3 seeds
- Full inversion (both directions) requires 0/3 seeds, threshold 2/3

## Partial Results

| Metric | Value |
|--------|-------|
| HE+ inversion (HE-only > MBPP-only) | 2/3 seeds (partial) |
| MBPP+ inversion (MBPP-only > HE-only) | 0/3 seeds |
| HE-only mean HE+ | 35.9% |
| MBPP-only mean HE+ | 27.6% |
| HE-only mean MBPP+ | 51.9% |
| MBPP-only mean MBPP+ | 50.5% |

## Experiment Summary

Analysis-only experiment using H-E2 SFT checkpoints. EvalPlus MBPP+ scores computed for all 12 (condition × seed) pairs. HumanEval-only training confers a bidirectional coding advantage — it improves performance on BOTH HumanEval+ AND MBPP+, while MBPP-only training does not show symmetric same-source specialization. This suggests HumanEval+ problems develop more general Python programming skills than MBPP+ problems develop specialized utility-script skills.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Whether MBPP+ task format is too similar to HumanEval+ for source specialization to emerge
2. Whether larger model scale (7B+) would show clearer MBPP+ specialization
3. Whether benchmark difficulty asymmetry (HumanEval harder) drives the bidirectional transfer

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-02T15:45:00+00:00*
*For cross-phase reference*
