# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under QA task conditions, if we measure pairwise semantic similarity across N generated responses, then low consistency indicates hallucination-prone questions, because unstable outputs reflect the model's inability to reliably converge on an answer.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests predictive mechanism with statistical validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS: p=0.0246, AUROC=0.6454)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (COMPLETED, PASS)

### Gate Condition
SHOULD_WORK gate - If fails, document as limitation and continue to H-M3

---

## Continuation Context

### Previous Hypothesis Results (H-M1)
From H-M1 validation (02b_verification_plan.md + 04_validation.md):
- **Result:** PASS
- **p-value:** 0.0246 (< 0.05 threshold)
- **AUROC:** 0.6454 (> 0.55 threshold)
- **Cohen's d:** 0.47 (medium effect)
- **Direction:** mean_entropy_incorrect (0.1342) > mean_entropy_correct (0.1104)
- **n_questions:** 100 TriviaQA validation samples
- **n_correct:** 60, **n_incorrect:** 40

**Proven:** Token entropy discriminates correct vs incorrect answers.

**Reuse for H-M2:** Same experimental setup (model, dataset, 10 responses per question, temp=0.7). This ensures controlled comparison - only IV changes (entropy → consistency).

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP servers unavailable in this session. Findings derived from Phase 2B verification plan and established literature.

**Semantic Consistency Patterns (from Phase 2B §2.2 H-M2):**
- Pairwise embedding cosine similarity across N samples
- SentenceTransformers for embedding generation
- Average similarity as consistency score per question

**Implementation References:**
- Manakul et al. (2023) SelfCheckGPT: Uses consistency-based hallucination detection
- Standard approach: Generate N responses, compute pairwise similarity, average

### Archon Code Examples

**Semantic Similarity Pattern (established):**
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def compute_consistency(responses: list[str]) -> float:
    embeddings = model.encode(responses)
    n = len(embeddings)
    similarities = []
    for i in range(n):
        for j in range(i+1, n):
            sim = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            similarities.append(sim)
    return np.mean(similarities)
```

### Exa GitHub Implementations

**Note:** MCP servers unavailable. Using established patterns from SentenceTransformers documentation.

**Key Implementation:**
- `sentence-transformers/sentence-transformers`: Official library
- Model: `all-MiniLM-L6-v2` (384-dim, fast, accurate)
- Alternative: `all-mpnet-base-v2` (768-dim, higher accuracy)

### 🎯 Implementation Priority Assessment

**CRITICAL: For consistency metric, use well-validated embedding model**

**Recommended Implementation Path:**
- Primary: SentenceTransformers with all-MiniLM-L6-v2
- Fallback: all-mpnet-base-v2 if quality insufficient
- Justification: Standard approach, validated in prior work, efficient for 10 samples/question

### Code Analysis (Serena MCP)

**Note:** MCP servers unavailable. Using H-M1 codebase patterns as reference.

From H-M1 implementation:
- Response generation: Already implemented (10 samples, temp=0.7)
- Correctness labeling: Already implemented (exact-match + majority voting)
- Statistical testing: Already implemented (t-test, AUROC)

**Additions for H-M2:**
- Embedding generation for each response
- Pairwise similarity computation
- Averaging to get consistency score per question

---

## Experiment Specification

### Dataset

**Dataset:** TriviaQA
**Type:** standard
**Source:** mandarjoshi/trivia_qa (HuggingFace)
**Path:** trivia_qa/rc.nocontext
**Split:** Validation (full ~11K questions, using 100 for PoC matching H-M1)

**Statistics:**
- Total: ~11K validation questions
- PoC sample: 100 questions (matching H-M1 for controlled comparison)
- Format: Question + ground-truth answer aliases

**Preprocessing:**
- Extract question text
- Extract answer aliases for exact-match evaluation

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `mandarjoshi/trivia_qa`
- Code: 
```python
from datasets import load_dataset
ds = load_dataset("trivia_qa", "rc.nocontext", split="validation")
```

### Models

#### Baseline Model

**Architecture:** Llama-2-7B-chat
**Type:** instruction-tuned LLM
**Source:** meta-llama/Llama-2-7b-chat-hf (HuggingFace)

**Configuration:**
- Parameters: 7B
- Context length: 4096
- Generation: 10 responses per question, temperature=0.7, max_new_tokens=100

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** Baseline + Semantic Consistency Metric

**Core Mechanism Implementation:**

```python
# Core Mechanism: Semantic Consistency Scoring
# Based on: SelfCheckGPT (Manakul et al., 2023), SentenceTransformers

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List

class SemanticConsistencyScorer:
    """
    Compute semantic consistency across N generated responses.
    High consistency = model reliably converges on similar answer.
    Low consistency = hallucination-prone (unstable outputs).
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
    
    def compute_consistency(self, responses: List[str]) -> float:
        """
        Args:
            responses: List of N responses for one question
        Returns:
            float: Average pairwise cosine similarity [0, 1]
        """
        # Encode all responses (N, 384)
        embeddings = self.encoder.encode(responses, convert_to_numpy=True)
        
        # Compute pairwise cosine similarities
        n = len(embeddings)
        similarities = []
        for i in range(n):
            for j in range(i + 1, n):
                # Cosine similarity
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                )
                similarities.append(sim)
        
        # Return average similarity as consistency score
        return float(np.mean(similarities)) if similarities else 0.0

# Usage: scorer = SemanticConsistencyScorer()
#        consistency = scorer.compute_consistency(responses)
```

### Training Protocol

**Note:** This is an inference-only experiment (no training required).

**Generation Protocol (from H-M1):**
- **Samples per question:** 10
- **Temperature:** 0.7
- **Max new tokens:** 100
- **Seed:** 42 (fixed)

**Embedding Model:**
- **Model:** all-MiniLM-L6-v2
- **Source:** SentenceTransformers (HuggingFace)
- **Batch encoding:** Yes (for efficiency)

### Evaluation

**Task Type:** Binary classification (correct vs incorrect based on consistency)

**Primary Metrics:**
- **t-test p-value:** Test if mean_consistency_correct > mean_consistency_incorrect
- **AUROC:** Consistency score predicting correctness

**Success Criteria (PoC):**
- Primary: p < 0.05 (statistically significant difference)
- Secondary: AUROC > 0.55 (consistency predicts correctness)
- Direction: Higher consistency for correct answers

**Expected Performance (from literature):**
- SelfCheckGPT shows consistency discriminates hallucinations
- Expected: Similar effect size to H-M1 (d ~ 0.3-0.5)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary_classification
- Library: scipy + sklearn
- Code:
```python
from scipy import stats
from sklearn.metrics import roc_auc_score

# t-test
t_stat, p_value = stats.ttest_ind(
    consistency_correct, consistency_incorrect, alternative='greater'
)

# AUROC
auroc = roc_auc_score(is_correct, consistency_scores)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart (p-value, AUROC thresholds)

#### Additional Figures (LLM Autonomous)
- **Consistency Distribution**: Histograms of consistency scores for correct vs incorrect answers
- **ROC Curve**: With AUC annotation
- **Scatter Plot**: Entropy vs Consistency (preview for H-M3 combination)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** True - Semantic embedding comparison is a defined operation
- **mechanism_isolatable:** True - Consistency computed independently from entropy
- **baseline_measurable:** True - Same correctness labels from H-M1

### Architecture Compatibility
- **Sentence embedding model:** Independent of Llama (separate model)
- **Response availability:** Reuse responses from H-M1 generation if available, else regenerate

### Activation Indicators
- **mechanism_log_message:** "Computing pairwise semantic similarity for {n} responses"
- **tensor_shape_change:** responses (N,) → embeddings (N, 384) → consistency (scalar)
- **metric_delta_expected:** Consistency values should range [0.3, 1.0] with variance

### Failure Detection
- All similarities = 1.0 → Degenerate embeddings
- All similarities = 0.0 → Embedding failure
- No variance in consistency scores → Metric not discriminative

### Success Criteria
- **hypothesis_support_metric:** AUROC
- **hypothesis_support_threshold:** > 0.55 AND p < 0.05

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. mean_consistency_correct > mean_consistency_incorrect
3. p-value < 0.05
4. AUROC > 0.55

---

## Appendix: Reference Implementations

### Key Papers
1. **Manakul et al. (2023)** - SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection
   - Uses consistency across samples for hallucination detection
   - Validates consistency as hallucination signal

2. **Reimers & Gurevych (2019)** - Sentence-BERT
   - Sentence embeddings via BERT fine-tuning
   - Foundation for semantic similarity

### Code References
1. **SentenceTransformers:** https://sbert.net/
   - Model: all-MiniLM-L6-v2
   - Usage: `SentenceTransformer('all-MiniLM-L6-v2').encode(texts)`

2. **H-M1 Implementation:** `../h-m1/code/`
   - Response generation pipeline (reusable)
   - Correctness evaluation (reusable)
   - Statistical testing framework (reusable)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19T04:09:06: H-M2 set to IN_PROGRESS (Hypothesis Loop)
- 2026-08-19: Phase 2C experiment design started

---

*MCP Tools Used: None (unavailable - using established patterns)*
*All specifications grounded in Phase 2B verification plan and H-M1 results*
*Next Phase: Phase 3 - Implementation Planning*
