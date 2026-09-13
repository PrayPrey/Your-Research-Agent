# Limitation Record: h-m3 (Run 1)

**Date:** 2026-08-09T14:05:00Z
**Hypothesis:** h-m3
**Run:** 1
**Gate Type:** SHOULD_WORK
**Result:** LIMITATION_RECORDED
**Pipeline Status:** Continued (not blocked)

## Limitation Details

RCI flip pattern near-universal across both hallucinated and correct responses. The mechanism exists but does not discriminate between response types.

## Failed Checks

- Hallucination flip rate (95.1%) exceeds 30% threshold but also appears in correct responses (90.9%)
- Separation of 4.2% far below required 20% threshold
- Pattern not discriminative for hallucination detection

## Partial Results

| Metric | Value |
|--------|-------|
| hallucination_flip_rate | 0.951 |
| correct_flip_rate | 0.909 |
| separation | 0.042 |
| poc_pass | true |
| full_pass | false |

## Experiment Summary

RCI (Residual Competition Index) flip pattern was successfully implemented and measured. The experiment correctly identified layer-wise competition dynamics where attention weights flip between competing representations. However, this phenomenon occurs nearly universally in both hallucinated and factually correct responses, making it unsuitable as a discriminative signal for hallucination detection.

The mechanism itself is valid and measurable, but the hypothesis that it differentiates hallucinations from correct responses is falsified.

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded with this limitation noted.

Future research attempts should consider:
1. RCI flips are a general inference phenomenon, not hallucination-specific
2. Alternative metrics combining RCI with other signals might be more discriminative
3. The flip pattern magnitude or timing might differ even if occurrence rate does not

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-09T14:05:00Z*
*For cross-phase reference*
