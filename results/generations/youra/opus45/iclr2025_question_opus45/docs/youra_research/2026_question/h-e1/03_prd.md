# Product Requirements Document: H-E1 SEDP Existence Validation

**Version:** 1.0
**Date:** 2026-03-28
**Author:** Phase 3 Implementation Planning
**Hypothesis ID:** h-e1
**Type:** EXISTENCE (PoC)

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-E1: demonstrating that a probe trained on hidden states with semantic similarity auxiliary signal produces meaningful SE predictions (Spearman rho >= 0.3) on the same model it was trained on.

**Core Deliverable:** A proof-of-concept implementation comparing SEDP (SE-Distilled Probe with Similarity) against baseline SEP (Semantic Entropy Probe) on TruthfulQA dataset using Llama-3-8B-Instruct.

---

## Problem Statement

### Background
Semantic Entropy Probes (SEPs) achieve near-full-SE performance using single-pass inference on LLM hidden states. However, SEPs are trained per-model and may not transfer well across different LLM architectures due to overfitting to model-specific hidden state patterns.

### Hypothesis
Adding semantic similarity structure as an auxiliary training signal may provide model-agnostic regularization, enabling better generalization. This EXISTENCE hypothesis validates the foundational assumption that such augmentation produces meaningful SE predictions.

### Success Criteria
- **Gate Threshold (MUST_WORK):** Spearman rho >= 0.3
- **Target Performance:** Spearman rho >= 0.7
- **Effect Direction:** SEDP rho > SEP baseline rho

---

## Functional Requirements

### FR-1: Data Pipeline

#### FR-1.1: Dataset Loading
- **Dataset:** TruthfulQA (generation split)
- **Source:** HuggingFace `truthfulqa/truthful_qa`
- **Split:** 80/20 train/test (~653/164 questions)
- **Seed:** 42 (fixed)

#### FR-1.2: Response Generation
- **Model:** Llama-3-8B-Instruct (`meta-llama/Meta-Llama-3-8B-Instruct`)
- **Responses per question:** N=20
- **Temperature:** 0.7
- **Output:** Generated responses + hidden states

#### FR-1.3: Hidden State Extraction
- **Layer:** 25 (of 32)
- **Token Position:** TBG (Token Before Generation)
- **Output shape:** (N_questions, hidden_dim=4096)

### FR-2: SE Label Generation

#### FR-2.1: Semantic Clustering
- **Method:** Bidirectional NLI entailment checking
- **Model:** DeBERTa-v3-large (`microsoft/deberta-v3-large-mnli`)
- **Output:** Cluster assignments per response set

#### FR-2.2: SE Computation
- **Formula:** `H_SE = -sum(p_i * log(p_i))` over semantic clusters
- **Output:** SE value per question (continuous)
- **Binarization:** High/Low SE labels for classification

### FR-3: Similarity Feature Computation

#### FR-3.1: Response Embeddings
- **Method:** Sentence embeddings from response text
- **Model:** sentence-transformers or DeBERTa embeddings
- **Output shape:** (N_questions, N_responses=20, embed_dim)

#### FR-3.2: Similarity Matrix
- **Method:** Cosine similarity between response embeddings
- **Statistics:** mean, std, min, max per question
- **Output shape:** (N_questions, 4) similarity features

### FR-4: Probe Training

#### FR-4.1: Baseline SEP
- **Input:** Hidden states only (4096 features)
- **Model:** Logistic Regression (sklearn)
- **Regularization:** L2, C=1.0
- **Optimizer:** LBFGS

#### FR-4.2: Proposed SEDP
- **Input:** Hidden states + similarity features (4096 + 4 = 4100 features)
- **Model:** Logistic Regression (sklearn)
- **Regularization:** L2, C=1.0
- **Optimizer:** LBFGS

### FR-5: Evaluation

#### FR-5.1: Primary Metrics
- **Spearman rho:** Correlation between predicted SE and true SE
- **AUROC:** Binary classification (high/low SE)

#### FR-5.2: Comparison Analysis
- SEP baseline rho vs SEDP rho
- Effect direction validation (SEDP > SEP)
- Gate threshold check (rho >= 0.3)

### FR-6: Visualization

#### FR-6.1: Required Figures
- **Gate Metrics Bar Chart:** rho values for SEP vs SEDP with threshold line at 0.3
- **Scatter Plot:** Predicted SE vs True SE for both methods
- **ROC Curves:** Hallucination detection comparison

#### FR-6.2: Output Location
- All figures saved to `h-e1/figures/`

---

## Non-Functional Requirements

### NFR-1: Performance
- Single GPU execution (select lowest memory usage GPU)
- Expected runtime: 2-4 hours for full pipeline

### NFR-2: Reproducibility
- Fixed seed: 42
- All random operations seeded
- Version-pinned dependencies

### NFR-3: Resource Constraints
- GPU Memory: ~20GB for Llama-3-8B-Instruct
- Disk: ~50GB for model weights + cache

---

## Data Specifications

### Input Data
| Data | Source | Format |
|------|--------|--------|
| TruthfulQA | HuggingFace | Dataset object |
| Llama-3-8B-Instruct | HuggingFace | AutoModelForCausalLM |
| DeBERTa-v3-large-mnli | HuggingFace | AutoModelForSequenceClassification |

### Output Data
| Data | Location | Format |
|------|----------|--------|
| Hidden states | Cache | .pt tensors |
| SE labels | Cache | .npy arrays |
| Similarity features | Cache | .npy arrays |
| Metrics | `h-e1/04_validation.md` | Markdown |
| Figures | `h-e1/figures/` | PNG |

---

## Dependencies

### Software Dependencies
- Python >= 3.10
- PyTorch >= 2.1
- transformers >= 4.36
- scikit-learn >= 1.3
- scipy >= 1.11
- datasets (HuggingFace)
- sentence-transformers (optional)

### Model Dependencies
- meta-llama/Meta-Llama-3-8B-Instruct (requires access token)
- microsoft/deberta-v3-large-mnli

### Hardware Dependencies
- CUDA-capable GPU with >= 24GB VRAM
- 64GB+ system RAM recommended

---

## Success Metrics

| Metric | Gate Threshold | Target | Measurement |
|--------|----------------|--------|-------------|
| Spearman rho | >= 0.3 | >= 0.7 | `scipy.stats.spearmanr` |
| Effect Direction | SEDP > SEP | - | Direct comparison |
| AUROC | > 0.5 | ~0.85 | `sklearn.metrics.roc_auc_score` |

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| GPU OOM | Medium | High | Use gradient checkpointing, reduce batch size |
| Llama access denied | Low | High | Pre-verify HuggingFace token |
| Low SE variance | Medium | Medium | Verify TruthfulQA SE distribution first |
| Similarity features uninformative | Medium | High | This is what H-E1 tests |

---

## Implementation Notes

### Reference Implementations
1. **OATML/semantic-entropy-probes** - Official SEP implementation
2. **jlko/semantic_uncertainty** - Base SE computation

### Key Implementation Decisions
- Use sklearn LogisticRegression (matches SEP paper)
- Extract TBG token hidden states (matches SEP paper)
- Layer 25 selection (middle-to-late, matches SEP recommendation)

---

## Appendix: Traceability

| Requirement | Source |
|-------------|--------|
| Dataset selection | Phase 2A + Exa research |
| Model architecture | OATML/semantic-entropy-probes |
| Success criteria | Phase 2B verification plan |
| Hyperparameters | SEP paper (Kossen et al., 2024) |

---

*Generated by Phase 3 Implementation Planning*
*Source: h-e1/02c_experiment_brief.md*
