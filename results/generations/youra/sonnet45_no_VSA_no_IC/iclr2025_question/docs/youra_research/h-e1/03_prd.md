# Product Requirements Document: h-e1 - Uncertainty Quantification for Selective Prediction

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis:** h-e1 (EXISTENCE)
**Version:** 1.0

---

## 1. Executive Summary

### Purpose
Implement and evaluate six single-pass uncertainty quantification (UQ) methods on TruthfulQA to determine if selective prediction can achieve AUROC ≥ 0.70 using Llama-3.1-8B-Instruct.

### Success Criteria
**MUST_WORK Gate:** At least one of the 6 UQ methods achieves AUROC ≥ 0.70 on the test split (490 questions).

### Scope
- **In Scope:** Temperature scaling, conformal prediction, MC dropout (k=1/3/5/10), AUROC evaluation
- **Out of Scope:** Training/fine-tuning (model frozen), ensemble methods, token-level uncertainty

---

## 2. Problem Statement

### Background
LLMs hallucinate on TruthfulQA (Llama-3.1-8B ~30% accuracy). Selective prediction requires reliable uncertainty estimates to abstain from incorrect predictions.

### Requirements
1. Generate answers for 817 TruthfulQA questions using Llama-3.1-8B-Instruct
2. Apply 6 UQ methods to extract uncertainty scores
3. Calibrate temperature scaling + conformal prediction on 40% split (327 questions)
4. Evaluate AUROC on 60% test split (490 questions)
5. Determine if max(AUROC) ≥ 0.70 threshold is met

---

## 3. Functional Requirements

### FR-1: Dataset Acquisition
**Priority:** P0 (Blocker)
**Description:** Download TruthfulQA dataset (817 questions) from HuggingFace or GitHub.
**Acceptance Criteria:**
- CSV loaded with columns: question, correct_answers, incorrect_answers
- 40/60 split created (seeded, reproducible)
- Ground truth labels extracted (binary: correct=0, incorrect=1)

**Dependencies:** None

---

### FR-2: Model Loading
**Priority:** P0 (Blocker)
**Description:** Load Llama-3.1-8B-Instruct from HuggingFace with FP16 + device_map.
**Acceptance Criteria:**
- Model loaded successfully with HF token
- Inference runs on GPU (batch_size=8)
- Generation config: max_tokens=100, temp=1.0, top_p=1.0

**Dependencies:** HuggingFace access token for gated Llama models

---

### FR-3: Baseline Answer Generation
**Priority:** P0 (Blocker)
**Description:** Generate 1-2 sentence answers for all 817 questions.
**Acceptance Criteria:**
- Answers saved to file (question_id, answer, logits)
- Logits extracted for each token position (needed for UQ)
- Generation reproducible (seed=42)

**Dependencies:** FR-2

---

### FR-4: Temperature Scaling
**Priority:** P1 (Core)
**Description:** Fit single temperature parameter T on calibration split, apply to test split.
**Acceptance Criteria:**
- T fitted via LBFGS (50 epochs, cross-entropy loss)
- Uncertainty score = 1 - max(softmax(logits/T))
- Outputs: uncertainty scores for 490 test questions

**Dependencies:** FR-3

---

### FR-5: Conformal Prediction
**Priority:** P1 (Core)
**Description:** Calibrate nonconformity threshold on calibration split (1-α quantile).
**Acceptance Criteria:**
- Nonconformity scores computed (1 - max_prob)
- Threshold = 90th percentile (α=0.1)
- Outputs: uncertainty scores for 490 test questions

**Dependencies:** FR-3

---

### FR-6: MC Dropout (k=1, 3, 5, 10)
**Priority:** P1 (Core)
**Description:** Enable dropout during inference, run k forward passes, measure epistemic uncertainty.
**Acceptance Criteria:**
- Dropout enabled (rate=0.1, standard for Llama)
- k passes executed per question (k ∈ {1, 3, 5, 10})
- Uncertainty = entropy across k predictions
- 4 variants evaluated (mc_k1, mc_k3, mc_k5, mc_k10)

**Dependencies:** FR-2

---

### FR-7: AUROC Evaluation
**Priority:** P0 (Blocker)
**Description:** Compute AUROC for each of 6 methods on test split.
**Acceptance Criteria:**
- AUROC computed using sklearn.metrics.roc_auc_score
- Input: y_true (binary correctness), y_score (uncertainty)
- Outputs: 6 AUROC values (temp_scaling, conformal, mc_k1, mc_k3, mc_k5, mc_k10)
- Gate check: max(AUROC) ≥ 0.70

**Dependencies:** FR-4, FR-5, FR-6

---

### FR-8: Results Logging
**Priority:** P2 (Nice-to-have)
**Description:** Save AUROC results and example predictions to JSON/CSV.
**Acceptance Criteria:**
- Results JSON: {method: AUROC, Spearman_rho}
- Example predictions CSV: question, answer, uncertainty, correctness
- Plots: ROC curves for all 6 methods (optional)

**Dependencies:** FR-7

---

## 4. Data Specification

### Input Data

**Dataset:** TruthfulQA
- **Source:** HuggingFace (`truthfulqa/truthful_qa`) OR GitHub CSV
- **Size:** 817 questions
- **Format:** CSV (question, correct_answers, incorrect_answers)
- **Splits:**
  - Calibration: 327 questions (40%, seed=42)
  - Test: 490 questions (60%, seed=42)

**Loading Code:**
```python
from datasets import load_dataset
ds = load_dataset("truthfulqa/truthful_qa", "generation")
# OR
import pandas as pd
df = pd.read_csv("TruthfulQA.csv")
```

### Static Baselines

**Model:** Llama-3.1-8B-Instruct
- **Source:** HuggingFace (`meta-llama/Llama-3.1-8B-Instruct`)
- **Type:** Pretrained LLM (8B params, instruction-tuned)
- **License:** Llama 3.1 Community License (gated, requires HF token)

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- **Metric:** Inference time ≤ 5 hours for 817 questions (single GPU)
- **Constraint:** Batch size = 8 (GPU memory limit)
- **MC Dropout:** k=10 increases time 10×, acceptable for PoC

### NFR-2: Reproducibility
- **Seed:** 42 (fixed for splits, generation, calibration)
- **Determinism:** Generation deterministic (temp=1.0, top_p=1.0, no sampling)

### NFR-3: Resource Constraints
- **GPU:** Single A100/V100 (40GB VRAM)
- **Storage:** ~5GB (model weights) + 10MB (dataset)
- **Compute:** ~5 hours total runtime (including MC k=10)

---

## 6. Success Criteria

### Gate Condition (MUST_WORK)
**Primary:** max(AUROC across 6 methods) ≥ 0.70

If met → H-E1 validated, proceed to H-M1 (mechanism hypothesis)
If failed → Document 8B limitation, recommend ≥70B model follow-up

### Secondary Metrics
- **Spearman ρ:** Correlation between uncertainty and incorrectness > 0.2 (sanity check)
- **Baseline Accuracy:** ~30% (expected for Llama-8B on TruthfulQA)

---

## 7. Dependencies

### Python Packages
```
torch>=2.0.0
transformers>=4.36.0
datasets>=2.14.0
sklearn>=1.3.0
numpy>=1.24.0
pandas>=2.0.0
```

### External Resources
- **HuggingFace Token:** Required for Llama-3.1-8B-Instruct (gated model)
- **TruthfulQA Dataset:** HF or GitHub CSV

### Reference Repositories
- mc-dropout-pytorch (PyPI): Standard MC dropout patterns
- honest-confidence (GitHub): TruthfulQA selective prediction baseline
- retinal-selective-prediction (GitHub): Temperature scaling + AUROC code

---

## 8. Out of Scope

The following are explicitly excluded from this hypothesis (may be addressed in H-M1/H-M2):
- **Training/Fine-tuning:** Model frozen (no parameter updates)
- **Ensemble Methods:** Single model only (6 UQ variants, not ensemble)
- **Token-level Uncertainty:** Question-level uncertainty only
- **Multi-model Comparison:** Llama-8B only (not 70B, GPT-4, etc.)
- **Alternative Benchmarks:** TruthfulQA only (not MMLU, GSM8K, etc.)

---

## 9. Timeline and Milestones

### Phase 4 Implementation (Estimated: 2-3 days)
- **Day 1:** FR-1, FR-2, FR-3 (Dataset + Model + Baseline Generation)
- **Day 2:** FR-4, FR-5, FR-6 (UQ Methods Implementation)
- **Day 3:** FR-7, FR-8 (AUROC Evaluation + Results Logging)

**Total Effort:** ~15 tasks (within LIGHT tier budget)

---

## Appendix A: Experiment Brief Reference

Full experiment specification: `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_question/docs/youra_research/h-e1/02c_experiment_brief.md`

Core mechanism pseudo-code, baseline repos, and calibration details in Section "Experiment Specification".
