# Product Requirements Document: H-M1

**Date:** 2026-08-10
**Author:** YouRA Research Pipeline
**Hypothesis:** LLM uncertainty signals (semantic entropy) correlate with error-generation processes
**Type:** MECHANISM
**Gate:** MUST_WORK (p < 0.05, Cohen's d > 0.3)

---

## 1. Executive Summary

This experiment validates that semantic entropy—computed via bidirectional entailment clustering of LLM responses—separates correct from incorrect answers. Success demonstrates that uncertainty signals capture meaningful error-generation processes, enabling hallucination detection.

**Key Deliverable:** Statistical validation showing semantic entropy is significantly higher for incorrect responses (p < 0.05, Cohen's d > 0.3).

---

## 2. Problem Statement

Current hallucination detection relies on heuristics without principled uncertainty quantification. H-M1 tests whether semantic entropy (Kuhn 2023, Farquhar 2024) provides a theoretically grounded uncertainty measure that correlates with model errors.

**Success Criteria:**
- Mann-Whitney U test: p < 0.05 (incorrect entropy > correct entropy)
- Effect size: Cohen's d > 0.3 (medium effect)
- Secondary: AUROC for entropy as correctness predictor

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load TriviaQA (rc subset) from HuggingFace
- Sample 1,000 questions from validation split (seed=42)
- Extract question and answer fields
- Normalize answers (lowercase, strip punctuation)

### FR-2: Response Generation
- Load Llama-2-7B-Chat model (full precision for logprobs)
- Generate N=10 responses per question at temperature=0.7
- Capture token-level log probabilities
- Max 50 new tokens per response

### FR-3: Entailment Clustering
- Load DeBERTa-v3-large NLI model (MNLI fine-tuned)
- Implement bidirectional entailment check (A⊨B AND B⊨A)
- Greedy clustering: assign response to first matching cluster
- Threshold: entailment probability > 0.5

### FR-4: Semantic Entropy Computation
- Aggregate log probabilities per semantic cluster
- Normalize cluster probabilities
- Compute Shannon entropy in nats

### FR-5: Correctness Labeling
- Compare generated responses to ground truth aliases
- Correct: exact match OR token F1 > 0.5
- Label each question-response pair

### FR-6: Statistical Analysis
- Separate entropy values by correctness label
- Mann-Whitney U test (one-sided: incorrect > correct)
- Cohen's d effect size calculation
- AUROC for entropy as binary classifier

### FR-7: Visualization
- **Required:** Bar chart comparing mean entropy (correct vs incorrect) with error bars, p-value, Cohen's d
- Entropy distribution violin plots
- ROC curve for entropy predictor

### FR-8: Ablation Studies
- Ablation A1: Temperature sensitivity (0.5, 0.7, 1.0)
- Ablation A2: Sample count (N=5, 10, 15)
- Ablation A3: Entailment threshold (0.3, 0.5, 0.7)

---

## 4. Data Specification

### 4.1 Primary Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | TriviaQA |
| **Version** | rc (reading comprehension) |
| **Source** | HuggingFace datasets |
| **Split** | validation (test hidden) |
| **Sample Size** | 1,000 questions |
| **Preprocessing** | Normalize answers, filter single-answer |

**Loading Code:**
```python
from datasets import load_dataset
dataset = load_dataset("trivia_qa", "rc", split="validation")
dataset = dataset.shuffle(seed=42).select(range(1000))
```

### 4.2 Static Baselines

No static baselines—this is a mechanism validation experiment, not model comparison.

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Process 1,000 questions within 24 hours on single A100 GPU
- Generation: ~10 samples/min with Llama-2-7B
- NLI inference: ~100 pairs/sec with DeBERTa

### NFR-2: Reproducibility
- Fixed random seeds (42) for dataset sampling
- Model temperature fixed at 0.7
- All hyperparameters documented

### NFR-3: Memory
- Peak GPU memory < 40GB (Llama-2-7B fp16 + DeBERTa)
- Batch NLI inference for efficiency

---

## 6. Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| p-value | < 0.05 | GATE (required) |
| Cohen's d | > 0.3 | GATE (required) |
| AUROC | > 0.65 | Secondary |

**Gate Evaluation:**
- PASS: Both p < 0.05 AND d > 0.3
- FAIL: Either condition not met → PIVOT to alternative uncertainty signal

---

## 7. Dependencies

### 7.1 Python Packages

| Package | Version | Purpose |
|---------|---------|---------|
| transformers | ≥4.35.0 | Llama-2, DeBERTa |
| datasets | ≥2.14.0 | TriviaQA loading |
| torch | ≥2.1.0 | Model inference |
| scipy | ≥1.11.0 | Mann-Whitney U test |
| scikit-learn | ≥1.3.0 | AUROC, metrics |
| numpy | ≥1.24.0 | Numerical operations |
| matplotlib | ≥3.7.0 | Visualization |
| seaborn | ≥0.12.0 | Violin plots |

### 7.2 External Repositories

| Repository | Purpose |
|------------|---------|
| jlko/semantic_uncertainty | Reference implementation (Farquhar 2024) |
| cvs-health/uqlm | Alternative SemanticEntropy class |

### 7.3 Hardware Requirements

- GPU: NVIDIA A100 40GB (or 2× RTX 3090)
- RAM: 64GB system memory
- Storage: 50GB for model weights

---

## 8. Out of Scope

- Multi-model comparison (single model: Llama-2-7B)
- Training or fine-tuning (inference only)
- Alternative uncertainty measures (lexical entropy, p(true))
- Cross-benchmark generalization (single benchmark: TriviaQA)

---

## 9. Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Setup | 0.5 days | Environment, model download |
| Generation | 1 day | 10K responses (1K questions × 10) |
| Entropy | 0.5 days | Semantic entropy computation |
| Analysis | 0.5 days | Statistical tests, visualization |
| **Total** | **2.5 days** | Validated H-M1 |

---

*Generated from Phase 2C: 02c_experiment_brief.md*
*Pipeline Position: Phase 3 Implementation Planning*
