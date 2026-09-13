# Phase 4 Failure Record: h-e1 (Run 1)

**Date:** 2026-08-04T13:56:00Z
**Hypothesis:** h-e1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** MUST_WORK_GATE_FAIL
**Routing:** ROUTED_TO_PHASE_0

## Hypothesis Statement

Under white-box open-source LLM inference (LLaMA-2-7B, Mistral-7B, LLaMA-3-8B) with greedy decoding, mean token logit entropy achieves AUROC > 0.52 against correct/incorrect hallucination labels on at least one of TriviaQA or TruthfulQA (after direction correction).

## Performance Data

| Model | Dataset | AUROC_corrected | Direction | CI [2.5%, 97.5%] | n | Gate |
|-------|---------|-----------------|-----------|-------------------|---|------|
| llama2 | trivia_qa | 0.5186 | inverted | [0.5008, 0.5548] | 1000 | FAIL |
| llama2 | truthful_qa | 0.5153 | positive | [0.5014, 0.6105] | 817 | FAIL |
| mistral | trivia_qa | 0.5268 | positive | [0.5028, 0.5680] | 1000 | PASS |
| mistral | truthful_qa | 0.5886 | positive | [0.5163, 0.6599] | 817 | PASS |
| llama3 | trivia_qa | 0.6583 | positive | [0.6140, 0.7031] | 1000 | PASS |
| llama3 | truthful_qa | 0.6161 | positive | [0.5525, 0.6820] | 817 | PASS |

Gate threshold: AUROC_corrected > 0.52 on ≥1 dataset for ALL 3 model families.
Result: 2/3 families pass (mistral, llama3). llama2 fails on both datasets.

## Root Cause Analysis

- llama2/Llama-2-7b-hf produces weak entropy signal; best AUROC_corrected=0.5186 (misses by 0.0014)
- llama2/trivia_qa direction is inverted (entropy higher for correct answers), suggesting anti-correlation
- Older RLHF-free base model may calibrate token probabilities differently, dampening entropy spread
- Instruct fine-tuning (llama3-instruct) appears to amplify entropy differences between correct/hallucinated

## Lessons Learned

1. Mean token logit entropy is a real signal for mistral and llama3 (AUROC 0.52–0.66)
2. Signal strength is model-architecture dependent — llama2 base does not generalize
3. Direction inversion on llama2/trivia_qa suggests the entropy-correctness relationship is not monotone across models
4. Using instruct vs. base variants introduces confound; llama3-instruct used due to cache availability
5. Bootstrap CI (n=1000) is essential — llama2 CI barely includes 0.52, confirming marginal signal

## Feedback for Next Phase

### Suggested Modifications
- Test entropy variants: max-token entropy, entropy variance, entropy of top-k tokens only
- Add per-layer entropy to find layers with stronger signal for llama2
- Normalize entropy by sequence length or vocabulary size

### What NOT To Do
- Do not assume entropy direction is consistent across model families
- Do not use llama2-7b-hf base as primary validation model for entropy-based features

### What Showed Promise
- llama3-instruct: strong, robust signal (AUROC 0.66, CI fully above 0.52)
- mistral: consistent moderate signal on both benchmarks
- Direction correction handles sign-ambiguity correctly

---
*For cross-phase reference*
*Written at: 2026-08-04T13:56:00Z*
