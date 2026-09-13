# Phase 4 Failure Record: h-e1-v2 (Run 1)

**Date:** 2026-03-15T16:30:00
**Hypothesis:** h-e1-v2
**Run:** 1
**Final Status:** PARTIAL/FAIL
**Failure Type:** MUST_WORK gate failed — both tasks below 0.65 AUROC threshold

## Performance Gap

| Metric | Ours | Baseline | Gap |
|--------|------|----------|-----|
| LLaMA-3.1-8B Dialogue AUROC | 0.5314 | 0.65 (threshold) | -0.1186 (-18.2%) |
| LLaMA-3.1-8B Summarization AUROC | 0.5258 | 0.65 (threshold) | -0.1242 (-19.1%) |

## Gate Details

- **Gate Type:** MUST_WORK
- **Criterion:** AUROC >= 0.65 on BOTH tasks (dialogue and summarization)
- **Result:** FAIL — both_pass=False, max_auroc=0.5314
- **Routing:** Phase 0

## Failed Checks

- llama3 dialogue AUROC=0.5314 < 0.65
- llama3 summarization AUROC=0.5258 < 0.65

## Root Cause Analysis

- Task-adaptive PROMPT_TEMPLATES framing (h-e1-v2 modification) did not improve hallucination detection AUROC on either task
- LLaMA-3.1-8B (base, not instruct) model appears insufficient for reliable P(True) scoring at this threshold
- Task-adaptive prompt framing alone is insufficient to lift AUROC above 0.65 from near-random performance (~0.53)

## Lessons Learned

1. Near-random AUROC (~0.53) on both tasks suggests the P(True) scoring approach with this model/prompt combination does not provide discriminative signal
2. Task-adaptive framing (h-e1-v2) failed to improve over h-e1's approach — the bottleneck may be model capability, not prompt framing
3. Future hypotheses should consider: different scoring methods, stronger base models, or fundamentally different detection mechanisms
4. The MUST_WORK gate (0.65 AUROC) was not met on either task — this is a fundamental failure, not a marginal miss

## Hypothesis Lineage

```
h-e1 (base)
    └── (INCREMENTAL PIVOT: task-adaptive prompt framing)
        └── h-e1-v2 → FAIL (ROUTED_TO_PHASE_0)
```

## Feedback for Next Phase (Phase 0)

### What NOT To Do
- Do not rely on P(True) scoring with LLaMA-3.1-8B base for hallucination detection at 0.65+ AUROC threshold
- Do not use task-adaptive prompt framing as the sole modification over h-e1

### What Showed Promise
- The experimental infrastructure (data pipeline, evaluation framework) worked correctly
- HaluEval dataset setup and caching from h-e1 run was reused successfully

### Suggested Modifications
- Explore alternative hallucination detection mechanisms beyond P(True) scoring
- Consider using instruction-tuned models or models with stronger reasoning capabilities
- Consider contrastive or consistency-based detection methods

---
*For cross-phase reference*
*Written at: 2026-03-15T16:30:00*
