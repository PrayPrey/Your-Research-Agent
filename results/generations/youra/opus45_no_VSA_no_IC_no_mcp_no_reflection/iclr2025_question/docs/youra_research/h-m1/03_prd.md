# Product Requirements Document: h-m1

**Hypothesis:** Semantic entropy achieves AUROC >= 0.70 on TruthfulQA mc1 by clustering semantically equivalent generations before entropy computation
**Type:** MECHANISM
**Date:** 2026-08-29
**Author:** Anonymous

---

## Executive Summary

Implement semantic entropy for hallucination detection, testing whether clustering semantically equivalent LLM generations before computing entropy improves discrimination over token-level UQ methods.

**Success Criterion:** AUROC >= 0.70 on TruthfulQA mc1 (prerequisite h-e1 achieved 0.8068 with max_prob).

---

## Problem Statement

Simple UQ methods (max_prob, choice_entropy) show strong hallucination detection (AUROC ~0.77-0.81). Semantic entropy claims improvement by clustering semantically equivalent responses. Need to verify this mechanism on TruthfulQA mc1.

---

## Functional Requirements

### FR-1: Multi-Sample Generation
- Generate N=10 diverse samples per question using Llama-3-8B-Instruct
- Temperature=0.7, max_tokens=128
- Store all samples for clustering

### FR-2: NLI-Based Semantic Clustering
- Load DeBERTa-v3-large-mnli for bidirectional entailment
- For each sample pair: compute entailment probability both directions
- Cluster samples where min(p1, p2) > 0.7 threshold
- Greedy clustering: assign to first matching cluster

### FR-3: Semantic Entropy Computation
- Compute cluster size distribution: p(cluster) = size / total_samples
- Entropy: H = -Σ p(cluster) * log(p(cluster))
- Higher entropy = more semantic inconsistency = likely hallucination

### FR-4: TruthfulQA mc1 Evaluation
- Load full dataset (817 questions)
- Ground truth: correct_mc1_answer match = 0, mismatch = 1 (hallucination)
- Compute AUROC using semantic entropy as score

### FR-5: Baseline Comparison
- Compare against h-e1 validated methods:
  - max_prob: AUROC=0.8068
  - choice_entropy: AUROC=0.7703
- Generate comparison visualization

### FR-6: Mechanism Verification
- Verify clustering reduces samples (avg_clusters < 10)
- Verify entropy variance > 0
- Log cluster statistics per question

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Set random seed=42 for all stochastic operations
- Log all hyperparameters

### NFR-2: Compute Efficiency
- Batch NLI calls where possible
- Cache NLI results to avoid redundant calls
- Expected runtime: 4-6 hours on single A100

### NFR-3: Modularity
- SemanticEntropy class with clear interface
- Separate generation, clustering, entropy computation

---

## Data Requirements

| Dataset | Source | Size | Purpose |
|---------|--------|------|---------|
| TruthfulQA mc1 | HuggingFace | 817 | Primary evaluation |

| Model | Source | Purpose |
|-------|--------|---------|
| Llama-3-8B-Instruct | meta-llama/Meta-Llama-3-8B-Instruct | LLM generation |
| DeBERTa-v3-large-mnli | microsoft/deberta-v3-large-mnli | NLI clustering |

---

## Success Criteria

| Metric | Target | Gate |
|--------|--------|------|
| Semantic entropy AUROC | >= 0.70 | MUST_WORK |
| Clustering active | avg_clusters < 10 | Mechanism verification |
| Entropy variance | > 0 | Mechanism verification |

---

## Dependencies

- **h-e1 (VALIDATED):** Provides max_prob/choice_entropy baselines and dataset preprocessing code
- **HuggingFace transformers:** Model loading
- **scikit-learn:** AUROC computation

---

## Out of Scope

- Hyperparameter tuning (N samples, temperature, threshold)
- Alternative NLI models
- Datasets other than TruthfulQA mc1
