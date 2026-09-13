# Phase 4 Validation Report: h-m3

## Hypothesis

**h-m3 (MECHANISM):** RCI flip pattern appears in >= 30% hallucinations and < 10% correct responses

## Gate Type

SHOULD_WORK

## Validation Result

**Status:** COMPLETED
**Result:** LIMITATION_RECORDED
**Gate Satisfied:** false

## Metrics

| Metric | Value | Threshold | Pass |
|--------|-------|-----------|------|
| Hallucination Flip Rate | 95.1% | >= 30% | ✓ |
| Correct Flip Rate | 90.9% | < 10% | ✗ |
| Separation | 4.2% | >= 20% | ✗ |

## Key Findings

1. **RCI flip pattern near-universal** - Both hallucinated (95.1%) and correct (90.9%) responses exhibit the flip pattern
2. **Separation insufficient** - Only 4.2% difference between groups (far below 20% threshold)
3. **Mechanism valid, hypothesis falsified** - The RCI flip pattern exists and is measurable, but does not discriminate between response types

## Analysis

The RCI (Residual Competition Index) tracks layer-wise competition between attention representations. The experiment successfully implemented this metric and measured flip patterns where dominant attention weights shift between layers 24-32.

However, the flip pattern appears as a general inference phenomenon rather than a hallucination-specific signal. Both factually correct and hallucinated responses show nearly identical flip rates, indicating that representational competition is inherent to the model's inference process regardless of output correctness.

## Conclusion

The mechanism implementation is correct, but the underlying hypothesis—that RCI flips differentiate hallucinations—is falsified. This is recorded as a limitation rather than a failure because:

1. SHOULD_WORK gate type allows proceeding with limitations
2. The mechanism provides scientific insight even if not discriminative
3. Future work might combine RCI with other metrics for better discrimination

## Serena Memory

Limitation record written: `limitation_h-m3_run1.md`

---
*Generated: 2026-08-09T14:05:00Z*
