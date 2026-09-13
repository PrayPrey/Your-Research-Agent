# Product Requirements Document: h-m1

**Hypothesis:** Probes trained on TriviaQA (~11K) achieve AUROC >0.70 when evaluated on TruthfulQA (cross-dataset transfer)
**Type:** MECHANISM
**Date:** 2026-08-24

---

## Executive Summary

Validate that Semantic Entropy Probes (SEPs) generalize across datasets by training on TriviaQA and evaluating on TruthfulQA. Success criterion: cross-dataset AUROC > 0.70.

---

## Problem Statement

Single-sample hallucination detection via SEPs was validated in h-e1. This experiment tests whether the learned representations transfer to a different evaluation domain, critical for practical deployment.

---

## Functional Requirements

### FR-1: Data Pipeline
- Load TriviaQA rc.nocontext split (11,000 training samples)
- Load TruthfulQA generation split (817 evaluation samples)
- Format: question-answer pairs

### FR-2: Hidden State Extraction
- Model: meta-llama/Meta-Llama-3-8B-Instruct
- Extract hidden states at layer L (default: last layer)
- Token position: last token of generated answer
- Output: (N, 4096) tensor per dataset

### FR-3: Semantic Entropy Computation
- Generate 5 responses per question at temperature=1.0
- Compute semantic entropy using NLI-based clustering
- Binarize labels: high SE (>median) = 1, low SE = 0

### FR-4: Probe Training
- Algorithm: LogisticRegression (sklearn)
- Solver: LBFGS, max_iter=1000
- Regularization: L2 with C=1.0
- Train on TriviaQA hidden states + SE labels

### FR-5: Cross-Dataset Evaluation
- Apply trained probe to TruthfulQA hidden states
- Compute AUROC: probe predictions vs correctness labels
- Success threshold: AUROC > 0.70

### FR-6: Visualization
- ROC curve for cross-dataset evaluation
- Layer analysis: AUROC by layer (if multi-layer ablation)
- Calibration plot: predicted probability vs accuracy

---

## Non-Functional Requirements

### NFR-1: Compute
- GPU: Single A100 or equivalent
- Memory: 40GB+ for Llama-3-8B

### NFR-2: Reproducibility
- Random seed: 42
- All hyperparameters logged

---

## Success Criteria

| Metric | Threshold | Source |
|--------|-----------|--------|
| Cross-dataset AUROC | > 0.70 | Gate condition |
| Falsification | < 0.60 | Gate failure |

---

## Dependencies

- h-e1: SEP mechanism validated (COMPLETED, PASS)
- HuggingFace: trivia_qa, truthful_qa datasets
- HuggingFace: meta-llama/Meta-Llama-3-8B-Instruct

---

## Out of Scope

- Multi-model comparison (separate hypothesis)
- In-distribution evaluation on TriviaQA
- Alternative probe architectures (MLP, etc.)
