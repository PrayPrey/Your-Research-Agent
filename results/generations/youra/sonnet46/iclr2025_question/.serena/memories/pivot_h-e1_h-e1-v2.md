# Hypothesis Pivot Record

**Date:** 2026-03-15T15:00:00
**From:** h-e1
**To:** h-e1-v2

## Pivot Reason

PARTIAL result (gate_result=PARTIAL, MUST_WORK): P(True) mechanism validated for instruction-tuned models on dialogue (LLaMA-3 AUROC=0.766) but failed to generalize to summarization (AUROC=0.547). Mistral-7B-v0.1 (base model) underperformed on both tasks (~0.58). Single generic prompt template insufficient for cross-task generalization.

## What Changed

- Scope narrowed to instruction-tuned models only (LLaMA-3-8B-Instruct; Mistral-7B-v0.1 excluded)
- Task-adaptive meta-evaluation prompt: dialogue-specific framing for conversation tasks; factual-consistency framing for summarization
- Gate criterion updated: AUROC >= 0.65 on both dialogue AND summarization for LLaMA-3-8B-Instruct

## What Was Preserved

- Core P(True) mechanism: softmax([True, False] logits from meta-evaluation prompt
- Dataset: HaluEval (pminervini/HaluEval) — dialogue + summarization
- Gate threshold: AUROC >= 0.65, DeLong test p < 0.05
- Implementation infrastructure: data.py, model.py, evaluate.py, visualize.py, run.py
- Strong result: LLaMA-3 dialogue AUROC=0.766 (Cohen's d=1.054) preserved as anchor

## Partial Results Preserved

| Metric | Value | Notes |
|--------|-------|-------|
| llama3_dialogue_p_true | 0.7658 | From h-e1 |
| llama3_summarization_p_true | 0.5466 | From h-e1 |
| mistral7_dialogue_p_true | 0.5840 | From h-e1 |
| mistral7_summarization_p_true | 0.5813 | From h-e1 |
| max_auroc | 0.7658 | From h-e1 |

## Key Insight for h-e1-v2

The P(True) mechanism is NOT fundamentally flawed. The failures stem from:
1. Task-specific prompt mismatch: Generic prompt does not frame summarization hallucination correctly
2. Model-type constraint: Instruction-following capability required; base models inadequate
3. No per-task prompt optimization was performed in h-e1

For h-e1-v2: Use task-adaptive prompts (dialogue: "Is this response accurate?"; summarization: "Is this summary factually consistent with the source?") and restrict to instruction-tuned LLaMA-3-8B-Instruct.

## LLM Self-Assessment

- Interface Compatibility: YES (P(True) computation infrastructure intact for h-m1/h-m2/h-c1)
- Data Flow Impact: YES (per-sample P(True) scores and AUROC metrics correctly typed; all 42 tests pass)
- Behavioral Assumptions: YES (P(True) as a valid signal confirmed on at least one condition)
- Recovery Potential: YES (prompt engineering + model selection — no core mechanism change)
- Decision: SELF_MODIFY (all 4 factors YES)

## Lineage

```
h-e1 (PARTIAL: generic prompt, mixed models)
    └── (PIVOT: task-adaptive prompts + instruction-tuned models only...)
        └── h-e1-v2
```

---
*Pivot recorded at: 2026-03-15T15:00:00*
