# Product Requirements Document: h-e1

**Hypothesis:** SEPs achieve AUROC within 0.05 of multi-sample SE on Llama-3-8B, Mistral-7B, Qwen-2-7B on TruthfulQA (817 samples)
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-24
**Author:** Anonymous

---

## Executive Summary

Validate that Semantic Entropy Probes (SEPs) — linear classifiers trained on LLM hidden states — can predict hallucination likelihood with AUROC within 0.05 of computationally expensive multi-sample Semantic Entropy across three model families.

**Key Value Proposition:** Single-pass inference (~5x faster) vs multi-sample generation while maintaining detection accuracy.

---

## Problem Statement

Multi-sample Semantic Entropy requires 5+ forward passes per query for hallucination detection. SEPs promise equivalent detection from single-pass hidden state extraction. This PoC validates the AUROC equivalence claim across model families.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA (817 questions) from HuggingFace Datasets
- Split: 80% train / 20% val for probe training
- Store preprocessed data for reproducibility

### FR-2: Model Loading
- Load 3 target models with hidden state access:
  - `meta-llama/Meta-Llama-3-8B-Instruct`
  - `mistralai/Mistral-7B-Instruct-v0.2`
  - `Qwen/Qwen2-7B-Instruct`
- Configure `output_hidden_states=True`
- Use float16 precision with device_map="auto"

### FR-3: Baseline - Multi-Sample Semantic Entropy
- Generate 5 responses per question (T=0.7)
- Cluster responses by semantic equivalence (NLI model: DeBERTa-v3-large-mnli)
- Compute entropy over cluster distribution
- Compute AUROC against ground truth (truthful/untruthful)

### FR-4: Proposed - Semantic Entropy Probe
- Extract hidden states at specified layer (~2/3 depth)
- Token position: last token (SLT)
- Train LogisticRegression on (hidden_state, binarized_SE) pairs
- Predict P(high_SE) for test samples
- Compute AUROC against ground truth

### FR-5: Evaluation
- Compute AUROC for both methods per model family
- Compute gap = |AUROC_SEP - AUROC_SE|
- Report pass/fail per success criteria

### FR-6: Visualization
- Generate AUROC comparison bar chart (SEP vs SE per family)
- Save to `h-e1/figures/`

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic data splits
- Logged hyperparameters

### NFR-2: Resource Efficiency
- GPU memory: ≤24GB per model
- Runtime: ≤4 hours total

### NFR-3: Modularity
- Separate modules for: data loading, hidden state extraction, SE computation, probe training, evaluation

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| AUROC gap ≤0.05 | At least 2/3 model families |
| AUROC gap ≤0.10 | All model families |
| Code executes | All 3 models without error |

---

## Dependencies

### External Libraries
- transformers>=4.40.0
- datasets
- torch>=2.0
- sklearn
- numpy
- matplotlib

### Models (HuggingFace)
- meta-llama/Meta-Llama-3-8B-Instruct
- mistralai/Mistral-7B-Instruct-v0.2
- Qwen/Qwen2-7B-Instruct
- microsoft/deberta-v3-large-mnli (for SE clustering)

### Dataset
- truthful_qa (generation subset)

---

## Out of Scope

- Hyperparameter optimization beyond layer selection
- Multi-seed experiments (PoC uses single seed)
- Deployment pipeline
- Latency benchmarking (future work)

---

## Reference Implementation

Primary: OATML/semantic-entropy-probes (official)
Secondary: zazamrykh/internal_probing (multi-model support)
