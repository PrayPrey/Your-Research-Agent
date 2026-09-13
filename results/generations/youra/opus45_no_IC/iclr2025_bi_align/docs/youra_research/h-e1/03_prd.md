# Product Requirements Document: H-E1

**Hypothesis:** Accommodation Patterns Detectable in LMSYS-Chat-1M
**Date:** 2026-08-10
**Author:** Anonymous
**Phase 2C Source:** 02c_experiment_brief.md

---

## 1. Executive Summary

This PRD defines requirements for validating that formality accommodation patterns are measurable in LMSYS-Chat-1M multi-turn conversations using DeBERTa formality scoring. This is an EXISTENCE hypothesis establishing the foundation for subsequent mechanism hypotheses.

**Success Criteria:** Coverage ≥50% of conversations meeting turn threshold AND Cohen's d > 0.3 (observed deltas < shuffled baseline).

---

## 2. Problem Statement

### 2.1 Background
Communication Accommodation Theory (Giles, 1973) suggests that successful interactions involve mutual linguistic adaptation. Formality accommodation occurs when AI responses match human formality levels, signaling attentiveness.

### 2.2 Core Question
Can formality accommodation patterns be reliably detected in LMSYS-Chat-1M using DeBERTa formality scoring?

### 2.3 Gate Condition
- **Pass:** Coverage ≥50%, Cohen's d > 0.3 (observed < shuffled)
- **Fail Action:** PIVOT to alternative dataset (WildChat) or relax turn threshold

---

## 3. Functional Requirements

### FR-1: Data Loading and Preprocessing
**Priority:** P0 (Critical)

Load LMSYS-Chat-1M dataset:
- **Source:** HuggingFace (`lmsys/lmsys-chat-1m`)
- **Access:** Requires license agreement

Preprocessing steps:
1. Filter to ≥2 turns per participant side (human ≥2, AI ≥2)
2. Language filter: English only (using `language` field)
3. Remove redacted entries (check `redacted` field)
4. Extract turn pairs for formality scoring

**Expected coverage:** ~50% of 1M = ~500K conversations after filtering

### FR-2: Formality Scoring
**Priority:** P0 (Critical)

Using DeBERTa formality ranker:
- **Model:** `s-nlp/deberta-large-formality-ranker`
- **Accuracy:** 87.8% on GYAFC corpus
- **Output:** Probability score [0, 1], higher = more formal

```python
def score_formality(text: str) -> float:
    """Get formality score (0-1, higher = more formal)."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1)
        return probs[0, 1].item()  # index 1 = formal class
```

### FR-3: Accommodation Delta Computation
**Priority:** P0 (Critical)

For each turn pair:
```
delta = |formality(AI_response) - formality(Human_prompt)|
```

Lower delta = more accommodation (AI matching human formality).

### FR-4: Shuffled Baseline Generation
**Priority:** P0 (Critical)

Destroy real pairing to create null model:
```python
def create_shuffled_baseline(formality_human, formality_ai):
    """Shuffle AI formality to destroy real pairing."""
    shuffled_ai = np.random.permutation(formality_ai)
    return formality_human, shuffled_ai
```

### FR-5: Statistical Analysis
**Priority:** P0 (Critical)

Compute Cohen's d effect size:
```python
def compute_cohens_d(observed_deltas, shuffled_deltas):
    """Effect size: observed should be SMALLER than shuffled if accommodation exists."""
    pooled_std = np.sqrt((np.var(observed_deltas) + np.var(shuffled_deltas)) / 2)
    d = (np.mean(shuffled_deltas) - np.mean(observed_deltas)) / pooled_std
    return d  # Positive d = observed < shuffled (accommodation detected)
```

Gate check: Cohen's d > 0.3 AND p < 0.001 (Welch's t-test)

### FR-6: Visualization
**Priority:** P1 (Important)

Required figures:
1. Gate metrics bar chart (coverage target 50% vs actual; Cohen's d target 0.3 vs actual)
2. Delta distribution histogram: Observed vs Shuffled overlay

Optional figures:
- Formality score distributions (human vs AI)
- Delta by model type (25 models in LMSYS)
- Early accommodation (turn 1) vs later turns

---

## 4. Data Specification

### 4.1 Primary Dataset: LMSYS-Chat-1M
- **Source:** HuggingFace (`lmsys/lmsys-chat-1m`)
- **Access:** Requires license agreement
- **Size:** 1M conversations, 25 LLM models
- **Format:** JSON with conversation_id, model, conversation (list of role/content), turn, language

### 4.2 Loading Code
```python
from datasets import load_dataset

# LMSYS-Chat-1M (requires HF login + license acceptance)
dataset = load_dataset("lmsys/lmsys-chat-1m", split="train")
print(f"Total conversations: {len(dataset)}")
# Features: conversation_id, model, conversation, turn, language, openai_moderation, redacted
```

---

## 5. Non-Functional Requirements

### NFR-1: Performance
- Processing time: < 8 hours for full dataset
- Memory: ~16GB GPU VRAM for DeBERTa-large batch processing
- GPU recommended for inference

### NFR-2: Reproducibility
- Single seed (42) for shuffled baseline
- Deterministic formality scoring

### NFR-3: Scalability
- Batch processing with configurable batch size
- GPU acceleration for DeBERTa inference

---

## 6. Success Criteria

| Metric | Target | Gate Type |
|--------|--------|-----------|
| Coverage | ≥ 50% | MUST_WORK |
| Cohen's d | > 0.3 | MUST_WORK |
| p-value | < 0.001 | MUST_WORK |

---

## 7. Dependencies

### 7.1 Python Packages
```
torch
transformers
scipy
numpy
pandas
datasets
matplotlib
seaborn
```

### 7.2 Pretrained Model
```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

model_name = "s-nlp/deberta-large-formality-ranker"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```

### 7.3 External References
- DeBERTa Formality Ranker: https://huggingface.co/s-nlp/deberta-large-formality-ranker
- LMSYS-Chat-1M: https://huggingface.co/datasets/lmsys/lmsys-chat-1m

---

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| R5: Dataset representativeness | Low | Standard dataset; 1M conversations, 210K IPs |
| R2: DeBERTa measurement noise | Medium | Use well-validated model (87.8% accuracy) |
| Insufficient multi-turn data | High | PIVOT to WildChat or relax turn threshold |

---

## 9. Out of Scope

- Model training (inference only)
- Real-time formality scoring
- User interface
- Multi-language support (English only)

---

## Appendix: FormalityAccommodationAnalyzer Reference

From Phase 2C experiment brief:
```python
class FormalityAccommodationAnalyzer:
    """
    Detect formality accommodation patterns in human-AI conversations.
    Accommodation = small |formality(AI_response) - formality(Human_prompt)|
    """
    def __init__(self, model_name='s-nlp/deberta-large-formality-ranker'):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.eval()
    
    def score_formality(self, text: str) -> float:
        """Get formality score (0-1, higher = more formal)."""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1)
            return probs[0, 1].item()
    
    def compute_accommodation_delta(self, human_text: str, ai_text: str) -> float:
        """Compute formality delta (lower = more accommodation)."""
        h_formality = self.score_formality(human_text)
        ai_formality = self.score_formality(ai_text)
        return abs(ai_formality - h_formality)
```
