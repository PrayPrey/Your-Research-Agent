# Product Requirements Document: H-M2 BAI-Reward Disagreement Analysis

**Date:** 2026-08-08
**Hypothesis:** H-M2 (MECHANISM)
**Author:** Anonymous
**Base Hypothesis:** H-E1 (VALIDATED)

---

## Executive Summary

Validate that BAI (Behavioral Agency Index) and reward model scores show systematic disagreement, with ≥20% of response pairs falling in opposing quartiles (high-BAI/low-reward or low-BAI/high-reward). This MECHANISM hypothesis tests whether agency-preserving behaviors captured by BAI represent an independent dimension from standard reward optimization.

---

## Problem Statement

H-E1 validated that four agency proxies can be reliably extracted (AUROC 0.9836). The next question: does this BAI signal capture something different from what reward models optimize? If BAI and reward scores correlate perfectly, BAI is redundant. If they systematically disagree, BAI captures a distinct dimension that RLHF may be trading off against reward. This hypothesis quantifies that disagreement.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HH-RLHF test split (~8,500 preference pairs)
- Load RewardBench evaluation set
- Extract chosen/rejected response pairs with prompts
- Reuse H-E1 data loading infrastructure

### FR-2: BAI Score Computation (from H-E1)
- Load H-E1 trained proxy models (4 TF-IDF + LogisticRegression classifiers)
- Compute proxy scores for each response
- Aggregate via mean of 4 proxy scores
- Apply length normalization: `BAI / (1 + 0.1 * log(word_count))`

### FR-3: Reward Score Computation
- Load pre-trained reward model: `OpenAssistant/reward-model-deberta-v3-large-v2`
- Compute reward score per prompt-response pair
- Handle truncation for long inputs (max 512 tokens)

### FR-4: Quartile-Based Disagreement Analysis
- Standardize BAI and reward scores (z-scores)
- Compute quartile boundaries (Q25, Q75) for each score type
- Count pairs in each quadrant:
  - High-BAI/High-Reward (Q4-BAI × Q4-Reward)
  - High-BAI/Low-Reward (Q4-BAI × Q1-Reward) ← DISAGREEMENT
  - Low-BAI/High-Reward (Q1-BAI × Q4-Reward) ← DISAGREEMENT
  - Low-BAI/Low-Reward (Q1-BAI × Q1-Reward)
- Compute disagreement rate: (disagreement quadrants) / total

### FR-5: Correlation Analysis
- Compute Pearson correlation between BAI and reward scores
- Compute Spearman correlation (rank-based)
- Expected: |r| < 0.5 for meaningful independence

### FR-6: Mechanism Verification
- Verify BAI score variance > 0.01 (discriminating)
- Verify reward score variance > 0.01 (discriminating)
- Verify disagreement rate in valid range (0 < rate < 0.5)
- Verify sample count ≥ 500 pairs

### FR-7: Visualization
- **Required**: Bar chart comparing disagreement rate vs 20% threshold
- Scatter plot: BAI (x) vs Reward (y) with Q25/Q75 quadrant lines
- 2D histogram/heatmap of BAI-Reward density
- Distribution histograms for BAI and reward scores
- Save all figures to h-m2/figures/

---

## Non-Functional Requirements

### NFR-1: Performance
- Full analysis completes in <60 minutes (GPU optional, CPU sufficient for reward model)
- Batch processing for reward model inference (batch_size=32)

### NFR-2: Reproducibility
- Fixed random_state=42 for all stochastic operations
- Dataset versions pinned via HuggingFace
- H-E1 model paths explicitly referenced

### NFR-3: Dependencies
- Python 3.8+
- datasets, sklearn, matplotlib, numpy, scipy
- transformers (for reward model)
- torch (for reward model inference)

### NFR-4: GPU Optional
- Reward model runs on CPU (slower) or GPU (faster)
- Auto-detect device availability

---

## Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| Disagreement rate ≥ 20% | Hypothesis PASS | SHOULD_WORK |
| Disagreement rate ∈ [10%, 20%) | PARTIAL result | Continue with limitations |
| Disagreement rate < 10% | Hypothesis FAIL | Reflection triggered |
| |r| < 0.5 (Pearson) | Independence indicator | Supporting |
| Mechanism verification passed | Code correctness | Required |

---

## Dependencies

### From H-E1 (Prerequisite)
- Trained proxy models: `h-e1/models/` or inline training
- Data loading utilities (reusable)
- Proxy extraction pipeline

### External
- HuggingFace datasets library
- HuggingFace transformers library
- OpenAssistant reward model weights (~1.5GB download)

---

## Data Flow

```
HH-RLHF/RewardBench → [Response Extraction] → responses[]
                                                   │
                    ┌──────────────────────────────┴──────────────────────────────┐
                    │                                                              │
                    ▼                                                              ▼
           [H-E1 Proxy Models]                                         [Reward Model]
           4 × TF-IDF + LogReg                                         DeBERTa-v3-large
                    │                                                              │
                    ▼                                                              ▼
              bai_scores[]                                               reward_scores[]
                    │                                                              │
                    └──────────────────────────┬───────────────────────────────────┘
                                               │
                                               ▼
                                    [Quartile Disagreement Analysis]
                                               │
                                               ▼
                                       disagreement_rate
```

---

## Out of Scope

- Training new reward models
- Fine-tuning proxy extractors
- Manual annotation of new data
- Real-time inference optimization
- Causal analysis of disagreement causes (future hypothesis)
