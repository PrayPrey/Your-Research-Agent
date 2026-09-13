# Product Requirements Document: h-e1

**Hypothesis:** Under controlled experimental conditions on knowledge-gap errors (NaturalQuestions unanswerable subset), if we compare semantic entropy (K=10 with clustering) against ensemble baseline (K=10 majority vote without clustering), then semantic entropy will outperform by ≥0.07 AUROC, because semantic clustering captures answer diversity beyond simple sampling frequency.

**Type:** EXISTENCE (Proof-of-Concept)
**Date:** 2026-04-22
**Author:** Anonymous
---

## 1. Executive Summary

This PoC validates whether semantic entropy (semantic clustering of K=10 samples) outperforms ensemble baseline (majority vote without clustering) for uncertainty estimation on knowledge-gap errors. Success requires AUROC_semantic - AUROC_ensemble ≥ 0.07 and AUROC_semantic ≥ 0.70.

**Scope:** Minimal implementation to test "does semantic clustering add value?"

---

## 2. Problem Statement

**Research Question:** Does semantic clustering of generated answers improve uncertainty estimation compared to simple majority voting?

**Hypothesis Gate:** MUST_WORK - AUROC_semantic - AUROC_ensemble ≥ 0.07 AND AUROC_semantic ≥ 0.70

**Consequence if fails:** PIVOT to simpler uncertainty methods (no clustering advantage demonstrated)

---

## 3. Functional Requirements

### FR-1: Data Preparation
**Priority:** P0 (Blocker)
- Load NaturalQuestions dataset from HuggingFace
- Filter for unanswerable questions (knowledge-gap errors)
- Select 100 examples for PoC evaluation
- **Acceptance:** Dataset loaded with 100 unanswerable questions

### FR-2: Model Setup
**Priority:** P0 (Blocker)
- Load Mistral-7B-v0.1 from HuggingFace
- Configure for text generation (temperature=0.7, max_tokens=50)
- **Acceptance:** Model loads and generates K=10 diverse answers per question

### FR-3: Semantic Entropy Method
**Priority:** P0 (Blocker)
- Generate K=10 answers per question
- Embed answers using sentence-transformers (all-MiniLM-L6-v2)
- Cluster semantically similar answers (agglomerative, threshold=0.5)
- Compute entropy over cluster distribution
- **Acceptance:** Semantic entropy scores computed for all questions

### FR-4: Ensemble Baseline
**Priority:** P0 (Blocker)
- Use same K=10 answers as semantic entropy method
- Compute disagreement rate via majority voting
- **Acceptance:** Ensemble baseline scores computed for all questions

### FR-5: Evaluation
**Priority:** P0 (Blocker)
- Compute AUROC for semantic entropy method
- Compute AUROC for ensemble baseline
- Calculate difference: AUROC_semantic - AUROC_ensemble
- **Acceptance:** Gate condition validated (≥0.07 difference, ≥0.70 absolute)

### FR-6: Visualization
**Priority:** P1 (Important)
- Bar chart: AUROC comparison with gate threshold line
- ROC curves for both methods
- Uncertainty distribution histograms
- **Acceptance:** Figures saved to h-e1/figures/

---

## 4. Data Specification

### Dataset: NaturalQuestions
**Source:** HuggingFace datasets library
**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("natural_questions", split="validation")
unanswerable = dataset.filter(lambda x: x['annotations']['yes_no_answer'][0] == -1)
```

**Subset:** 100 unanswerable questions
**Preprocessing:** Extract question text only
**Ground Truth:** Unanswerable questions (knowledge gaps) = positive class for uncertainty detection

---

## 5. Model Specification

### Mistral-7B-v0.1
**Source:** HuggingFace transformers
**Loading:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
```

**Generation Config:**
- Temperature: 0.7 (diverse sampling)
- Max tokens: 50 (short answers)
- K samples: 10 per question
- Seed: 42 (reproducibility)

---

## 6. Success Criteria

### Primary Metrics
- **AUROC_semantic:** Semantic entropy method AUROC ≥ 0.70
- **AUROC_difference:** AUROC_semantic - AUROC_ensemble ≥ 0.07

### PoC Pass Condition
1. Code runs without error
2. AUROC_semantic > AUROC_ensemble (clustering adds value)
3. If gap ≥ 0.07: MUST_WORK gate PASSES
4. If gap < 0.07 but positive: Partial success, may need refinement
5. If AUROC_semantic < AUROC_ensemble: Gate FAILS, pivot required

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0.0
transformers>=4.30.0
datasets>=2.14.0
sentence-transformers>=2.2.0
scikit-learn>=1.3.0
numpy>=1.24.0
matplotlib>=3.7.0
```

### 7.2 External Repositories
**Reference Implementation:** jlko/semantic_uncertainty (Kuhn et al., 2023)
- URL: https://github.com/jlko/semantic_uncertainty
- Purpose: Reference for semantic entropy implementation details
- Usage: Code patterns for clustering and entropy computation

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed: 42
- Deterministic generation where possible
- Version pinning for all dependencies

### NFR-2: Performance
- Single GPU execution
- Runtime: < 30 minutes for 100 questions
- Memory: < 16GB GPU VRAM

### NFR-3: Code Quality
- Minimal implementation (PoC quality)
- Basic error handling
- Clear variable names

---

## 9. Out of Scope

For EXISTENCE hypothesis, the following are OUT OF SCOPE:
- ❌ Hyperparameter tuning (use defaults from research)
- ❌ Multiple datasets (only NaturalQuestions)
- ❌ Ablation studies (tested in future hypotheses)
- ❌ Multiple model sizes (only Mistral-7B)
- ❌ K-sensitivity analysis (fixed K=10)
- ❌ Production-quality code
- ❌ Extensive testing

---

## 10. Acceptance Criteria

**Definition of Done:**
1. ✅ All FR-1 to FR-5 implemented
2. ✅ AUROC values computed for both methods
3. ✅ Gate condition evaluated
4. ✅ Figures generated
5. ✅ Results interpretable (pass/fail clear)

**Phase 4 Deliverable:**
- Working experiment code
- AUROC comparison results
- Visualization figures
- Gate validation outcome
