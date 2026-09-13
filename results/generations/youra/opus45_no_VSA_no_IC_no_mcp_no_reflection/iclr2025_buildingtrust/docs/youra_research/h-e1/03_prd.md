# Product Requirements Document: h-e1

**Hypothesis:** Both semantic entropy and self-consistency detect hallucinations above random baseline (AUROC > 0.55) on TruthfulQA and HaluEval
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-28
**Gate:** MUST_WORK

---

## Executive Summary

Validate that two uncertainty-based hallucination detection methods—semantic entropy and self-consistency—achieve above-chance performance on standard benchmarks. This is a proof-of-concept validation establishing baseline capability before mechanism/comparison studies.

---

## Problem Statement

LLMs generate plausible-sounding but factually incorrect responses (hallucinations). Two promising detection approaches exist:
1. **Semantic Entropy**: Cluster multiple responses by semantic equivalence, compute entropy over clusters
2. **Self-Consistency**: Measure pairwise similarity across multiple responses

Both methods require empirical validation that they detect hallucinations better than random guessing.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load TruthfulQA generation subset (817 questions, full test set)
- Load HaluEval-QA subset (10,000 samples)
- Extract ground truth labels (truthful/hallucinated)

### FR-2: Response Generation
- Use Llama-3-8B-Instruct as generator
- Generate N=10 responses per query at temperature=0.7
- Max tokens: 256
- Single seed (42) for reproducibility

### FR-3: Semantic Entropy Detector
- Load microsoft/deberta-v3-large-mnli for NLI
- Cluster responses by bidirectional entailment
- Compute entropy over cluster distribution
- Return uncertainty score per query

### FR-4: Self-Consistency Detector
- Compute pairwise BERTScore (roberta-large)
- Average F1 scores (excluding diagonal)
- Return consistency score per query
- Lower consistency = higher hallucination likelihood

### FR-5: Evaluation Pipeline
- Compute AUROC for each method on each dataset
- Generate bootstrap 95% CI (n=1000)
- Compare against 0.55 threshold

### FR-6: Visualization
- ROC curves (both methods overlaid)
- Score distributions (hallucinated vs truthful)
- Gate metrics comparison bar chart

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed (42)
- Deterministic NLI inference
- Logged model versions

### NFR-2: Performance
- Process TruthfulQA in <2 hours on single A100
- Memory: fit within 40GB GPU

---

## Success Criteria

| Metric | Threshold | Condition |
|--------|-----------|-----------|
| Semantic Entropy AUROC | > 0.55 | MUST pass |
| Self-Consistency AUROC | > 0.55 | MUST pass |
| Both methods pass | AND | Gate satisfied |

---

## Dependencies

### External Libraries
- transformers (Llama-3, Deberta)
- datasets (HuggingFace)
- bert-score
- scikit-learn
- numpy, torch

### Models
- meta-llama/Meta-Llama-3-8B-Instruct
- microsoft/deberta-v3-large-mnli
- roberta-large (BERTScore)

### Datasets
- truthful_qa (HuggingFace)
- pminervini/HaluEval

---

## Out of Scope
- Hyperparameter optimization
- Multiple seeds
- Training/fine-tuning
- Comparison between methods (separate hypothesis)
