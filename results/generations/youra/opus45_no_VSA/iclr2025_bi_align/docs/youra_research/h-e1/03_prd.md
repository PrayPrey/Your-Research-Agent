# Product Requirements Document: H-E1 Agency Proxy Extraction

**Date:** 2026-08-08
**Hypothesis:** H-E1 (EXISTENCE)
**Author:** Anonymous

---

## Executive Summary

Validate that four agency-preserving behavior proxies (clarifying questions, option enumeration, epistemic hedging, explicit deferral) can be reliably extracted from HH-RLHF and RewardBench responses with AUROC ≥0.8 against annotation-derived labels.

---

## Problem Statement

Current RLHF training may inadvertently suppress user agency by training models to be overly decisive. Before investigating mechanisms (H-M1, H-M2), we must first confirm that agency-preserving behaviors can be detected in existing preference data. This EXISTENCE hypothesis gates all downstream research.

---

## Functional Requirements

### FR-1: Dataset Loading
- Load HH-RLHF dataset (harmless-base, helpful-base subsets)
- Load RewardBench Safety subset
- Extract assistant responses from dialogue transcripts
- Total: ~17,100 responses (HH-RLHF test) + RewardBench Safety

### FR-2: Baseline Models
- **Random Classifier**: Predicts 50% probability, expected AUROC = 0.5
- **Majority Class Classifier**: Predicts most frequent label, expected AUROC ≈ 0.5

### FR-3: Agency Proxy Detector
- Implement four regex-based pattern detectors
- Compute TF-IDF features (ngram_range=(1,2), max_features=5000)
- Train LogisticRegression classifier per proxy type (C=1.0, max_iter=1000)

### FR-4: Four Proxy Types
1. **Clarifying Questions**: "what do you mean", "could you clarify", "are you asking"
2. **Option Enumeration**: "there are several options", "you could either", numbered lists
3. **Epistemic Hedging**: "I'm not sure", "it's possible", "I think", "maybe"
4. **Explicit Deferral**: "recommend consulting", "a professional would", "I can't advise"

### FR-5: Evaluation Pipeline
- Compute AUROC per proxy type using sklearn.metrics.roc_auc_score
- Generate ROC curves for visualization
- Compare against baselines

### FR-6: Visualization
- Bar chart: AUROC per proxy with 0.8 target line
- ROC curves: 4 subplots (one per proxy)
- Save to h-e1/figures/

---

## Non-Functional Requirements

### NFR-1: Performance
- Full evaluation completes in <30 minutes on CPU

### NFR-2: Reproducibility
- Fixed random_state=42 for all stochastic operations
- Dataset versions pinned via HuggingFace

### NFR-3: Dependencies
- Python 3.8+
- datasets, sklearn, matplotlib, numpy

---

## Success Criteria

| Criterion | Target | Gate |
|-----------|--------|------|
| All 4 proxies AUROC > 0.5 | Baseline beat | Required |
| ≥3 of 4 proxies AUROC ≥ 0.7 | Strong signal | Required |
| Mean AUROC ≥ 0.8 | Hypothesis satisfied | MUST_WORK |

---

## Dependencies

- HuggingFace datasets library
- sklearn for ML pipeline
- No GPU required (CPU-only evaluation)

---

## Out of Scope

- Fine-tuning language models
- Manual annotation (using existing dataset structure)
- Real-time inference optimization
