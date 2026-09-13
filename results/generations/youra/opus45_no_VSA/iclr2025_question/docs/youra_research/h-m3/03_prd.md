# Product Requirements Document: h-m3

**Hypothesis:** RCI flip pattern appears in >= 30% hallucinations and < 10% correct responses
**Type:** MECHANISM
**Date:** 2026-08-09
**Author:** Anonymous

---

## Executive Summary

Implement RCI (Representational Competition Index) flip pattern detection to validate that hallucinated responses exhibit significantly higher top-token instability across transformer layers compared to correct responses. This mechanism hypothesis builds on h-e1's validated NTI signal (AUROC 0.5657) by examining the discrete flip events that contribute to trajectory instability.

---

## Problem Statement

h-e1 established that NTI discriminates hallucinations from correct responses. However, the underlying mechanism remains uncharacterized. The RCI flip pattern hypothesis proposes that hallucinations exhibit discrete top-token changes between consecutive layers (flips) at higher rates than correct responses. Validating this mechanism would:

1. Explain WHY NTI works (flips drive instability)
2. Provide interpretable detection signal (binary flip vs continuous score)
3. Enable targeted intervention at flip-prone layers

---

## Functional Requirements

### FR-1: Hidden State Extraction Pipeline
Reuse h-e1 infrastructure for extracting hidden states from LLaMA-2-7B layers 24-32.
- Input: TruthfulQA MC1 question + answer
- Output: Hidden states tuple (9 layers x batch x hidden_dim)
- Constraint: output_hidden_states=True

### FR-2: Logit-Lens Projection
Project each layer's hidden state to vocabulary space using unembedding matrix.
- Input: Hidden state (batch, 4096)
- Operation: h @ lm_head.weight.T
- Output: Logits (batch, vocab_size)

### FR-3: Top-Token Extraction
Extract argmax token ID from each layer's logits.
- Input: Layer logits (9, batch, vocab_size)
- Output: Top tokens (9, batch)

### FR-4: Flip Detection
Detect when top-1 token changes between consecutive layers.
- Input: Top tokens array
- Output: Binary flip indicator per sample, flip count, flip positions

### FR-5: Rate Computation
Compute flip rates for hallucinated vs correct response groups.
- hallucination_flip_rate = count(flip AND hallucination) / count(hallucination)
- correct_flip_rate = count(flip AND correct) / count(correct)

### FR-6: Visualization
Generate gate metrics bar chart with threshold lines at 30% and 10%.

---

## Non-Functional Requirements

### NFR-1: Reproducibility
Fixed seed=42, deterministic operations, greedy decoding (temp=0).

### NFR-2: Computational Efficiency
Single A100 GPU, ~30 min for 817 samples, batch_size=1 for hidden state extraction.

### NFR-3: Compatibility
Reuse h-e1 model/dataset cache paths.

---

## Success Criteria

| Metric | Threshold | Falsification |
|--------|-----------|---------------|
| hallucination_flip_rate | >= 0.30 | < 0.20 |
| correct_flip_rate | < 0.10 | >= 0.15 |
| separation | >= 0.20 | < 0.05 |

---

## Dependencies

- **h-e1**: Validated (AUROC 0.5657) - provides working logit-lens pipeline
- **TruthfulQA MC1**: Cached at ~/.cache/huggingface/datasets/truthful_qa
- **LLaMA-2-7B**: Cached at ~/.cache/huggingface/hub

---

## Out of Scope

- Model fine-tuning
- Multi-model comparison
- Real-time inference optimization
