# Limitation Record: h-m2 (Run 1)

**Date:** 2026-03-17T04:15:00Z
**Hypothesis:** h-m2
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

h-m2: SHOULD_WORK gate failed - DPO does not have higher mean Q1 delta_var vs SFT (direction reversed). No improvement path found after 1 retry.

## Failed Checks

- DPO Q1 delta_var not significantly higher than SFT (p>0.05 for all datasets)
- Cross-benchmark gate: 0/3 datasets significant (required: 2/3)
- Direction of effect reversed: SFT shows higher Q1 delta_var than DPO

## Partial Results

| Metric | Value |
|--------|-------|
| n_significant | 0 |
| mmlu_p | 1.0 |
| truthfulqa_p | 1.0 |
| arc_p | 0.9924 |
| gate_pass | false |
| datasets_tested | MMLU(14042) + TruthfulQA(817) + ARC(1172) |

## Experiment Summary

Full inference on MMLU (14042 samples), TruthfulQA (817 samples), ARC (1172 samples). 0/3 datasets showed significant DPO > SFT Q1 delta_var. SHOULD_WORK gate failed — pipeline continued with null result documented. No improvement attempt was viable after direction reversal confirmed.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted as NULL_RESULT.

Future research attempts should consider:
1. The specific checks that failed: DPO direction assumption may be wrong for KL-residualized variance
2. Whether the limitation is fundamental or circumstantial: possibly fundamental — DPO training may not systematically increase Q1 token uncertainty variance
3. Alternative approaches: test on different model pairs, or investigate whether higher quintiles show the expected pattern instead

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-03-17T04:15:00Z*
*For cross-phase reference*
