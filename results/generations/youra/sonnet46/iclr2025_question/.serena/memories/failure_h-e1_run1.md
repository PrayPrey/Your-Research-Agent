# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-03-15T12:00:00
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL — H_token AUROC below threshold on Dialogue and Summarization

## Gate Criteria

- **Gate Type:** MUST_WORK
- **Criteria:** H_token AUROC >= 0.65 on Dialogue AND Summarization (>=1 model), DeLong p < 0.05
- **Result:** FAIL
- **Routing:** PHASE_0_REFORMULATION

## Performance Gap

| Metric | Result | Threshold | Pass? |
|--------|--------|-----------|-------|
| H_token AUROC (LLaMA, Dialogue) | 0.5442 | >= 0.65 | FAIL |
| H_token AUROC (LLaMA, Summarization) | 0.4242 | >= 0.65 | FAIL |
| H_token AUROC (Mistral, Dialogue) | 0.5737 | >= 0.65 | FAIL |
| H_token AUROC (Mistral, Summarization) | 0.3451 | >= 0.65 | FAIL |
| H_token AUROC (LLaMA, QA) | 0.6734 | >= 0.65 | PASS (but gate requires Dialogue+Summarization) |
| P(True) AUROC (LLaMA, Dialogue) | 0.8401 | N/A | Strong signal |
| P(True) AUROC (LLaMA, Summarization) | 0.7287 | N/A | Strong signal |

## Root Cause Analysis

- Mean token entropy (H_token) fails for fluent generative hallucinations — these hallucinations do not produce high per-token entropy
- H_token is discriminative on QA (factual recall) but not on open-ended dialogue/summarization
- The hypothesis incorrectly assumed token-level entropy would signal hallucination across all task types
- P(True) (verbalized confidence) is a much stronger signal for generative hallucination detection

## Lessons Learned

1. Mean token entropy is task-specific — works for factual QA but not for fluent hallucinations in dialogue/summarization
2. P(True) (model's verbalized confidence) is more robust across task types — AUROC 0.84 dialogue, 0.73 summarization
3. Gate threshold of 0.65 AUROC on Dialogue AND Summarization is achievable with P(True) but not H_token
4. Reformulation should focus on verbalized confidence signals rather than token entropy
5. HaluEval-QA shows H_token works (0.67) — QA-only hypotheses may be viable

## Feedback for Next Phase (Phase 0 Reformulation)

### Suggested Modifications
- Reformulate gate around P(True) signal instead of H_token
- Consider separating QA hypothesis from Dialogue/Summarization hypothesis
- Explore verbalized uncertainty (P(True), semantic entropy) as primary signal

### What NOT To Do
- Do not use mean token entropy as sole signal for generative hallucination detection
- Do not require AUROC >= 0.65 on ALL task types with token entropy alone

### What Showed Promise
- P(True) AUROC 0.84 on dialogue, 0.73 on summarization — strong reformulation candidate
- H_token works on QA (0.67) — viable for factual hallucination sub-hypothesis

---
*For cross-phase reference*
*Written at: 2026-03-15T12:00:00*
