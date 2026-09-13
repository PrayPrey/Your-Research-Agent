# Product Requirements Document: H-M2

**Hypothesis:** H-M2 - Semantic Consistency as Hallucination Predictor
**Date:** 2026-08-19
**Author:** Anonymous
**Phase 2C Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

Implement semantic consistency measurement for QA responses to validate that low pairwise similarity across N generated responses predicts hallucination-prone questions. This extends H-M1's entropy-based approach by adding a complementary consistency metric.

**Key Deliverable:** Compute average pairwise cosine similarity across 10 responses per question using SentenceTransformer embeddings, then validate predictive power via t-test and AUROC.

---

## 2. Problem Statement

**Research Question:** Does semantic consistency (measured via embedding similarity) discriminate between correct and incorrect model responses?

**Hypothesis:** Low consistency across multiple responses indicates the model cannot reliably converge on an answer, signaling hallucination-prone questions.

**Success Criteria:**
- p-value < 0.05 (consistency differs between correct/incorrect)
- AUROC > 0.55 (consistency predicts correctness)
- Direction: Higher consistency for correct answers

---

## 3. Functional Requirements

### FR-1: Response Generation (Reuse from H-M1)
- Generate 10 responses per question using Llama-2-7B-chat
- Temperature: 0.7
- Max new tokens: 100
- Seed: 42 (reproducibility)

### FR-2: Semantic Embedding Generation
- Encode each response using SentenceTransformer
- Model: all-MiniLM-L6-v2 (384-dimensional embeddings)
- Batch encoding for efficiency

### FR-3: Consistency Score Calculation
- Compute pairwise cosine similarity for all response pairs
- For N=10 responses: 45 pairs (N*(N-1)/2)
- Average similarities to get single consistency score per question

### FR-4: Correctness Labeling (Reuse from H-M1)
- Exact-match evaluation against TriviaQA answer aliases
- Majority voting across 10 responses
- Binary label: correct/incorrect

### FR-5: Statistical Validation
- Independent t-test: mean_consistency_correct vs mean_consistency_incorrect
- Alternative hypothesis: greater (correct > incorrect)
- AUROC: consistency predicting correctness
- Effect size: Cohen's d

### FR-6: Visualization
- Consistency distribution histograms (correct vs incorrect)
- ROC curve with AUC annotation
- Scatter plot: entropy vs consistency (preview for H-M3)

---

## 4. Data Specification

### Primary Dataset: TriviaQA
- **Source:** mandarjoshi/trivia_qa (HuggingFace)
- **Split:** rc.nocontext validation
- **Sample Size:** 100 questions (matching H-M1 for controlled comparison)
- **Format:** Question + answer aliases

### Data Loading
```python
from datasets import load_dataset
ds = load_dataset("trivia_qa", "rc.nocontext", split="validation")
# Select same 100 questions as H-M1 for consistency
questions = ds.select(range(100))
```

---

## 5. Models

### Base Model: Llama-2-7B-chat
- **Source:** meta-llama/Llama-2-7b-chat-hf
- **Parameters:** 7B
- **Context:** 4096 tokens
- **Purpose:** Response generation

### Embedding Model: SentenceTransformer
- **Primary:** all-MiniLM-L6-v2 (fast, 384-dim)
- **Fallback:** all-mpnet-base-v2 (higher accuracy, 768-dim)
- **Purpose:** Semantic embedding for similarity computation

---

## 6. Evaluation Metrics

### Primary Metrics
| Metric | Threshold | Purpose |
|--------|-----------|---------|
| p-value | < 0.05 | Statistical significance |
| AUROC | > 0.55 | Predictive power |

### Secondary Metrics
| Metric | Purpose |
|--------|---------|
| Cohen's d | Effect size magnitude |
| mean_correct | Mean consistency for correct answers |
| mean_incorrect | Mean consistency for incorrect answers |
| Pearson r | Correlation with entropy (H-M3 preview) |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.30.0
sentence-transformers>=2.2.0
datasets>=2.14.0
scipy>=1.10.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
```

### 7.2 Hardware Requirements
- GPU: NVIDIA GPU with 16GB+ VRAM (for Llama-2-7B)
- RAM: 32GB+ system memory

### 7.3 External Resources
- HuggingFace Hub access for model downloads
- ~15GB disk space for Llama-2-7B model

---

## 8. Non-Functional Requirements

### NFR-1: Performance
- Response generation: ~1-2 min per question (10 samples)
- Embedding generation: <1 second per question
- Total runtime: ~3 hours for 100 questions

### NFR-2: Reproducibility
- Fixed seed for all random operations
- Deterministic model loading
- Saved intermediate results

### NFR-3: Compatibility
- Reuse H-M1 response data if available
- Same evaluation framework as H-M1

---

## 9. Success Criteria (PoC)

1. Code runs without error
2. mean_consistency_correct > mean_consistency_incorrect
3. p-value < 0.05
4. AUROC > 0.55

**Gate Type:** SHOULD_WORK
- If fails: Document as limitation, continue to H-M3

---

## 10. Output Files

| File | Description |
|------|-------------|
| consistency_scores.json | Per-question consistency scores |
| validation_results.json | Statistical test results |
| figures/consistency_dist.png | Distribution histogram |
| figures/roc_curve.png | ROC curve |
| figures/entropy_vs_consistency.png | Scatter plot |
| 04_validation.md | Validation report |

---

*Generated for Phase 3 Implementation Planning*
*Experiment scale: 100 TriviaQA questions, 10 responses each*
