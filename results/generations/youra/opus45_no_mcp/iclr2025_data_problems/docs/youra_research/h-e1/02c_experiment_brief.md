# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under standard FM evaluation on MMLU, if SSI is computed for benchmark items, then SSI will differ significantly between clean and contaminated models, because contaminated models exhibit uniform confidence across paraphrases.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
- **Type:** MUST_WORK
- **Pass:** AUC > 0.7 for clean vs contaminated classification
- **Fail Action:** ABANDON — core mechanism invalid

---

## Continuation Context

This is the first hypothesis in the verification chain (H-E1 → H-M1 → H-M2 → H-M3 → H-M4).

### Previous Hypothesis Results (if applicable)
N/A - H-E1 has no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Contamination Detection Approaches (Web Research):**
1. **N-gram overlap detection** (GPT-3 style): Uses 13-gram exact matching to detect verbatim contamination. Fails on paraphrased contamination.
2. **Rephrasing-based detection** (LLM-Decontaminator): Identifies training samples that are rephrasings of benchmark test cases using vector similarity. Uses F1 scores as primary metric.
3. **Person-fit analysis**: Statistical approach using response matrices to detect anomalous performance patterns.
4. **Jaccard similarity**: Text overlap detection using set-based similarity measures.

**Key Insight:** Existing methods focus on surface-form matching. SSI approach is novel in measuring behavioral uniformity (confidence variance across paraphrases).

### Archon Code Examples

**LLM-Decontaminator Code Structure:**
- `main.py` - orchestrates detection pipeline
- `llm_detect.py` - implements detection logic
- `vector_db.py` - manages vector-based similarity matching
- Datasets supported: HumanEval, MMLU, MATH, StarCoder-Data

**Relevant Pattern:** Vector similarity for paraphrase matching is established; confidence variance measurement is the novel component.

### Exa GitHub Implementations

**Related Repositories:**
1. **lm-sys/llm-decontaminator** - Rephrasing-based contamination quantification
2. **nate-daba/detect-benchmark-contamination** - LLM benchmark contamination framework
3. **Shreyaskc/leaklens** - Unified contamination detection toolkit
4. **artemisveizi/contamination-person-fit** - Person-fit analysis approach

**Key Finding:** No existing implementation uses confidence variance across paraphrases (SSI). This confirms novelty.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is a novel method (SSI) without prior implementation. Must build from scratch using:
1. Standard MMLU evaluation pipeline (lm-evaluation-harness)
2. Confidence extraction via model logits
3. Paraphrase generation (T5/GPT-4/rule-based)
4. Custom SSI computation

**Recommended Implementation Path:**
- Primary: Custom implementation using HuggingFace Transformers + datasets library
- Fallback: Adapt lm-evaluation-harness for confidence extraction
- Justification: SSI is novel; no existing implementation. HuggingFace stack is well-documented and supports Mistral-7B.

### Code Analysis (Serena MCP)

*Serena MCP not available. Analysis based on web research.*

Key implementation components identified:
1. Model loading: `AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")`
2. Tokenizer: `AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")`
3. Dataset: `load_dataset("cais/mmlu")`
4. Confidence extraction: Softmax over logits for answer tokens

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | MMLU (Massive Multitask Language Understanding) |
| **Source** | HuggingFace: cais/mmlu |
| **Type** | standard |
| **Test Split Size** | 14,042 items |
| **Subjects** | 57 subjects (abstract algebra to virology) |
| **Format** | Multiple-choice (4 options: A, B, C, D) |

**Splits Used:**
- `test`: 14,042 items (primary evaluation)
- `auxiliary_train`: 99,842 items (for contamination injection)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `cais/mmlu`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("cais/mmlu", "all")
test_data = dataset["test"]  # 14,042 items
train_data = dataset["auxiliary_train"]  # 99,842 items for fine-tuning
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | Mistral-7B-v0.1 |
| **Parameters** | 7 billion |
| **Architecture** | Decoder-only transformer with Grouped-Query Attention, Sliding-Window Attention |
| **Source** | HuggingFace: mistralai/Mistral-7B-v0.1 |
| **Precision** | BF16 |

**Variants for Contamination Study:**
| Variant | Contamination Level | MMLU Items in Training |
|---------|---------------------|------------------------|
| Clean | 0% | 0 |
| Low | 10% | 1,404 |
| High | 50% | 7,021 |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `mistralai/Mistral-7B-v0.1`
- Code:
```python
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```

#### Proposed Model

**Architecture:** Baseline Mistral-7B + SSI Computation Pipeline

**Core Mechanism Implementation:**

```python
def compute_ssi(model, tokenizer, item, paraphrases, answer_tokens):
    """
    Compute Semantic Saturation Index for a single MMLU item.
    SSI = 1 / variance(confidence_scores)
    
    Args:
        model: Loaded Mistral-7B model
        tokenizer: Mistral tokenizer
        item: Original MMLU question + choices
        paraphrases: List of K=20 paraphrased versions
        answer_tokens: Token IDs for A, B, C, D
    
    Returns:
        ssi: float, higher = more uniform confidence (contamination signal)
    """
    confidences = []
    
    # Include original + K paraphrases
    all_versions = [item] + paraphrases
    
    for version in all_versions:
        # Format as multiple-choice prompt
        prompt = format_mmlu_prompt(version)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            # Get logits for last token position
            last_logits = outputs.logits[0, -1, :]
            
            # Extract probabilities for answer tokens (A, B, C, D)
            answer_logits = last_logits[answer_tokens]
            probs = torch.softmax(answer_logits, dim=0)
            
            # Confidence = max probability (model's prediction confidence)
            confidence = probs.max().item()
            confidences.append(confidence)
    
    # Compute SSI = inverse variance
    variance = np.var(confidences)
    ssi = 1.0 / (variance + 1e-8)  # Epsilon for numerical stability
    
    return ssi, confidences

def classify_contamination(ssi_clean, ssi_contaminated):
    """
    Evaluate AUC for binary classification.
    """
    from sklearn.metrics import roc_auc_score
    
    labels = [0] * len(ssi_clean) + [1] * len(ssi_contaminated)
    scores = ssi_clean + ssi_contaminated
    
    auc = roc_auc_score(labels, scores)
    return auc
```

### Training Protocol

**Contamination Injection (Fine-tuning):**

| Parameter | Value |
|-----------|-------|
| **Base Model** | Mistral-7B-v0.1 |
| **Method** | LoRA fine-tuning |
| **LoRA Rank** | 16 |
| **LoRA Alpha** | 32 |
| **Learning Rate** | 2e-4 |
| **Batch Size** | 4 (gradient accumulation: 8) |
| **Epochs** | 3 |
| **Optimizer** | AdamW |
| **Scheduler** | Cosine with warmup |
| **Warmup Steps** | 100 |

**Training Data Composition:**
- Clean (0%): General instruction data only (Alpaca-style)
- Low (10%): General data + 1,404 MMLU items (question-answer pairs)
- High (50%): General data + 7,021 MMLU items

**Paraphrase Generation:**

| Method | Count per Item | Total |
|--------|---------------|-------|
| T5-paraphrase | 7 | 98,294 |
| GPT-4 API | 7 | 98,294 |
| Rule-based synonym | 6 | 84,252 |
| **Total per item** | **20** | **280,840** |

### Evaluation

**Primary Metrics:**

| Metric | Target | Description |
|--------|--------|-------------|
| **AUC** | > 0.7 | Area Under ROC Curve for clean vs contaminated classification |
| **Cohen's d** | > 0.5 | Effect size between clean and contaminated SSI distributions |

**Secondary Metrics:**

| Metric | Purpose |
|--------|---------|
| Mean SSI (clean) | Baseline SSI distribution |
| Mean SSI (contaminated) | Contaminated SSI distribution |
| SSI variance | Distribution characteristics |
| Per-contamination-level AUC | Sensitivity analysis |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (contamination detection)
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import roc_auc_score, roc_curve
import scipy.stats as stats

def evaluate_ssi_discrimination(ssi_clean, ssi_contaminated):
    # AUC
    labels = [0]*len(ssi_clean) + [1]*len(ssi_contaminated)
    scores = ssi_clean + ssi_contaminated
    auc = roc_auc_score(labels, scores)
    
    # Cohen's d
    pooled_std = np.sqrt((np.var(ssi_clean) + np.var(ssi_contaminated)) / 2)
    cohens_d = (np.mean(ssi_contaminated) - np.mean(ssi_clean)) / pooled_std
    
    return {"auc": auc, "cohens_d": cohens_d}
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing AUC (target: 0.7) vs achieved AUC

#### Additional Figures (LLM Autonomous)

1. **SSI Distribution Plot**: Violin/box plot comparing SSI distributions for clean vs contaminated models
2. **ROC Curve**: ROC curve with AUC annotation
3. **Contamination Level Analysis**: Line plot of mean SSI vs contamination percentage (0%, 10%, 50%)
4. **Confidence Variance Histogram**: Distribution of confidence variance across items

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. AUC > 0.7 for SSI-based contamination classification
3. Cohen's d > 0.5 (effect size)

**Gate Decision:**
- PASS: Proceed to H-M1 (mechanism hypotheses)
- FAIL: ABANDON entire SSI approach

---

## Appendix: Reference Implementations

### A. LLM-Decontaminator
- **URL:** https://github.com/lm-sys/llm-decontaminator
- **Relevance:** Rephrasing-based detection approach; vector similarity matching
- **Key Files:** `main.py`, `llm_detect.py`, `vector_db.py`

### B. LM-Evaluation-Harness
- **URL:** https://github.com/EleutherAI/lm-evaluation-harness
- **Relevance:** Standard MMLU evaluation framework
- **Usage:** Reference for MMLU prompt formatting

### C. HuggingFace MMLU Dataset
- **URL:** https://huggingface.co/datasets/cais/mmlu
- **Usage:** Direct dataset loading

### D. Mistral-7B Model Card
- **URL:** https://huggingface.co/mistralai/Mistral-7B-v0.1
- **Usage:** Model loading and architecture reference

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- Phase 2B completed: verification plan created
- Phase 2C started: experiment design in progress
- Phase 2C Step 02: Archon/web research completed
- Phase 2C Step 03: Exa GitHub search completed
- Phase 2C Step 04: Code analysis completed (Serena N/A)
- Phase 2C Step 05: Dataset and baseline specified
- Phase 2C Step 06: Experiment synthesis completed
- Phase 2C Step 07: References compiled
- Phase 2C Step 08: Validation complete

---

*Research Tools Used: WebFetch (GitHub, HuggingFace)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
