# Phase 4 Failure Record: h-e1 (Run 3)

**Date:** 2026-08-09T09:37:00Z
**Hypothesis:** h-e1
**Run:** 3
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAILED

## Performance Gap

| Metric | Achieved | Threshold | Gap |
|--------|----------|-----------|-----|
| AUROC | 0.5190 | 0.55 | -0.031 (-5.6%) |

## Root Cause Analysis

- Mean entropy alone provides weak discriminative signal for hallucination detection
- Entropy difference between hallucinated/non-hallucinated classes only 2.8%
- Single scalar feature insufficient to capture hallucination patterns
- Token-level entropy may need positional/contextual interactions to be informative

## Lessons Learned

1. Raw mean entropy is near-random for hallucination detection (AUROC ~0.52)
2. The mechanism assumption (entropy correlates with factual errors) is too simplistic
3. Need richer feature interactions (position, frequency, context) not just aggregate entropy
4. Existence hypothesis failed to demonstrate basic effect - methodology needs fundamental revision

## Feedback for Next Phase

### Suggested Modifications
- Add positional entropy interactions (entropy at specific sequence positions)
- Include token frequency context (entropy relative to expected entropy for token frequency)
- Consider multi-scale entropy features (local vs global patterns)

### What NOT To Do
- Do not retry with same single-feature approach
- Do not assume linear relationship between entropy and hallucination

### What Showed Promise
- Infrastructure for entropy computation is sound
- TruthfulQA MC1 dataset properly loaded and processed
- Evaluation pipeline correctly measures AUROC

---
*For cross-phase reference*
*Written at: 2026-08-09T09:37:00Z*
*Routing: Phase 2A - methodology needs redesign, not fundamental approach abandonment*
