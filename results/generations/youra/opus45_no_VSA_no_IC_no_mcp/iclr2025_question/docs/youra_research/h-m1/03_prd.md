# Product Requirements Document: H-M1

**Hypothesis:** Token entropy captures epistemic uncertainty — when model lacks knowledge about answer, logit distribution is diffuse (high entropy correlates with factual incorrectness)

**Date:** 2026-08-28
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

Validate the causal mechanism linking token entropy to epistemic uncertainty. Building on H-E1's confirmation that entropy predicts correctness above chance, this experiment tests whether incorrect responses exhibit systematically higher entropy than correct ones.

---

## Problem Statement

H-E1 established entropy as a predictive signal. H-M1 investigates the underlying mechanism: does high entropy reflect genuine model uncertainty (diffuse logit distribution when knowledge is lacking)?

---

## Functional Requirements

### FR-1: Response Generation Pipeline
- Generate single response per TruthfulQA question (817 questions)
- Use greedy decoding (do_sample=False)
- Extract token-level logits during generation
- Model: LLaMA-2-7B (meta-llama/Llama-2-7b-hf)

### FR-2: Entropy Computation
- Compute per-token entropy: `-sum(p * log(p))`
- Aggregate to mean entropy per response
- Store entropy values for all responses

### FR-3: Correctness Labeling
- Label each response as correct/incorrect using TruthfulQA ground truth
- Use substring matching against correct_answers list

### FR-4: Statistical Analysis
- Partition responses by correctness label
- Compute mean entropy for correct vs incorrect groups
- Calculate Cohen's d effect size
- Perform Mann-Whitney U test (one-sided, alternative='greater')

### FR-5: Visualization
- Box/violin plot: entropy distributions by correctness
- Histogram overlay with KDE
- ROC curve: entropy as binary classifier

---

## Non-Functional Requirements

### NFR-1: Hardware
- GPU: H100 (5x available)
- Memory: float16 inference

### NFR-2: Reproducibility
- Greedy decoding ensures deterministic outputs
- Fixed random seed where applicable

---

## Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Direction | Mean(incorrect) > Mean(correct) | PRIMARY |
| Effect Size | Cohen's d > 0.2 | SECONDARY |
| Significance | p < 0.05 (informative) | TERTIARY |

---

## Data Specifications

### Dataset
- **Name:** TruthfulQA (generation subset)
- **Size:** 817 questions
- **Source:** HuggingFace `truthful_qa` (generation config)
- **Split:** Full validation set (no train/test split)

### Model
- **Name:** LLaMA-2-7B
- **Identifier:** meta-llama/Llama-2-7b-hf
- **Type:** Pre-trained (no fine-tuning)

---

## Dependencies

- H-E1: VALIDATED (entropy computation verified working)
- Existing code: `src/metrics/entropy.py` from H-E1

---

## Out of Scope

- Semantic entropy (Kuhn et al. method) — fallback if MUST_WORK gate fails
- Multi-model comparison
- Fine-tuning or training
