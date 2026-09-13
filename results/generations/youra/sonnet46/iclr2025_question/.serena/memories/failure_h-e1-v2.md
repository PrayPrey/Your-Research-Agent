# Phase 4 Failure: h-e1-v2 (P(True) Task-Adaptive, Base Model)

Type: failure_record
Hypothesis: h-e1-v2
Phase: Phase 4
Gate: MUST_WORK
Result: FAIL
Date: 2026-03-15

## Root Cause
- Experiment ran on meta-llama/Llama-3.1-8B (BASE model), not instruction-tuned
- P(True) mechanism requires instruction-following capability
- Base model AUROC: dialogue=0.5314, summarization=0.5258 (near chance)
- Max modification attempts (1) reached → ROUTED_TO_PHASE_0

## Key Lessons
1. VERIFY MODEL VARIANT before experiment: check tokenizer.chat_template or model config for instruction-tuning signature
2. P(True) probe ONLY works with instruction-tuned models (RLHF/SFT trained)
3. Base models respond with arbitrary P(True) scores near 0.5
4. Task-adaptive prompts are necessary but not sufficient for base models
5. h-e1 AUROC=0.766 was from instruction-tuned model — verified this mechanism works when model is correct

## What Worked (code is correct, reusable)
- Task-adaptive PROMPT_TEMPLATES structure
- TASK_PROMPTS dispatch in model.py
- evaluate_gate_v2() dual-task gate
- 79/79 tests pass
- Full pipeline infrastructure

## Routing
- Routing: Phase 0
- Cascade: h-m1, h-m2, h-c1 → CASCADE_FAILED
