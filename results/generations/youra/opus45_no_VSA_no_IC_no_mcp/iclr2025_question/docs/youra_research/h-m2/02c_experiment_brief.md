# Experiment Brief: H-M2 Consistency-Stability Link

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** MUST_WORK
**Generated:** 2026-08-28

---

## 1. Hypothesis Statement

**Under-If-Then-Because:**
Under closed-book QA conditions (TruthfulQA), if the model's generation process is unstable for a question, then N-sample consistency is low because different sampling runs yield semantically divergent answers (low consistency correlates with factual incorrectness).

**Success Criteria:**
- Primary: Mean consistency (incorrect) < Mean consistency (correct)
- Secondary: Effect size Cohen's d > 0.2

**Failure Response:** PIVOT — consistency metric may need refinement (BERTScore or ROUGE-based)

---

## 2. Dataset Specification

| Attribute | Value |
|-----------|-------|
| **Name** | TruthfulQA |
| **Source** | HuggingFace: `truthfulqa/truthful_qa` |
| **Split** | generation (817 questions) |
| **Type** | standard |
| **Ground Truth** | best_answer vs incorrect_answers |

**Sample Size Justification:**
- Full TruthfulQA generation split: 817 questions
- Sufficient for effect size estimation with 95% CI
- No subsampling needed

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthfulqa/truthful_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthfulqa/truthful_qa", "generation")
```

---

## 3. Model Specification

| Attribute | Value |
|-----------|-------|
| **Name** | LLaMA-2-7B |
| **HuggingFace ID** | `meta-llama/Llama-2-7b-hf` |
| **Access** | Requires HF token with Meta approval |
| **Requirements** | ~14GB VRAM (fp16) |

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

---

## 4. Implementation Research Summary

### Archon Knowledge Base Findings

**Source: SelfCheckGPT (Manakul et al. 2023)**
- N-sample consistency validated for hallucination detection
- Embedding cosine similarity captures semantic consistency
- N=5 samples shown sufficient for stable estimates

**Source: Semantic Uncertainty (Kuhn et al. 2023)**
- Generation stability reflects model confidence
- Unstable generations indicate epistemic uncertainty
- Embedding clustering reveals answer variability

### Reference Implementation

**Repository**: potsawee/selfcheckgpt
- URL: https://github.com/potsawee/selfcheckgpt
- Key implementation: BERTScore + embedding similarity for consistency
- pip install selfcheckgpt

### Code Analysis

**Core mechanism already validated in h-e1:**
- N=5 samples per question at temperature=1.0
- Embedding model: sentence-transformers/all-MiniLM-L6-v2
- Pairwise cosine similarity aggregation

---

## 5. Experiment Specification

### Core Mechanism: Consistency-Stability Correlation

**Hypothesis Test:** Verify that low N-sample consistency correlates with incorrect (hallucinated) responses, demonstrating that consistency captures generation stability.

**Protocol:**
1. Generate N=5 responses per TruthfulQA question (reuse from h-e1)
2. Compute consistency scores per question (reuse from h-e1)
3. Label responses as correct (0) or incorrect/hallucinated (1)
4. Partition consistency scores by correctness label
5. Compare distributions: consistency(incorrect) vs consistency(correct)

### Core Mechanism Pseudo-code (10-30 lines)

```python
# Core Mechanism: Consistency-Stability Analysis
# Based on: SelfCheckGPT + h-e1 validated pipeline

from sentence_transformers import SentenceTransformer
import numpy as np
from scipy import stats

encoder = SentenceTransformer('all-MiniLM-L6-v2')

def compute_consistency(responses: list[str]) -> float:
    """Compute pairwise embedding cosine similarity."""
    embeddings = encoder.encode(responses)
    n = len(embeddings)
    similarities = []
    for i in range(n):
        for j in range(i+1, n):
            sim = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            similarities.append(sim)
    return np.mean(similarities)

def analyze_stability_link(consistency_scores, correctness_labels):
    """Test consistency-stability hypothesis."""
    correct_mask = np.array(correctness_labels) == 0
    incorrect_mask = np.array(correctness_labels) == 1
    
    consistency_correct = consistency_scores[correct_mask]
    consistency_incorrect = consistency_scores[incorrect_mask]
    
    mean_correct = np.mean(consistency_correct)
    mean_incorrect = np.mean(consistency_incorrect)
    
    # Cohen's d effect size
    pooled_std = np.sqrt((np.var(consistency_correct) + np.var(consistency_incorrect)) / 2)
    cohens_d = (mean_correct - mean_incorrect) / pooled_std
    
    return {
        'mean_correct': mean_correct,
        'mean_incorrect': mean_incorrect,
        'cohens_d': cohens_d,
        'direction_correct': mean_incorrect < mean_correct
    }
```

---

## 6. Training Protocol

**No Training Required** — This is an analysis hypothesis, not a learning experiment.

**Inference Protocol:**
- Temperature: 1.0 (for sampling diversity)
- N samples: 5 per question
- Max new tokens: 100
- Seeds: 1 (fixed for reproducibility)

**Reusing h-e1 artifacts:**
- Generated responses (N=5 per question)
- Computed consistency scores
- Ground truth labels

---

## 7. Evaluation Metrics

**Primary Metrics:**
- Mean consistency (correct responses)
- Mean consistency (incorrect responses)
- Cohen's d effect size

**Success Criteria (PoC):**
- mean_consistency(incorrect) < mean_consistency(correct)
- Cohen's d > 0.2 (small but detectable effect)

**Expected Baseline Performance:**
- Based on h-e1 results and SelfCheckGPT findings
- Incorrect responses expected to show ~10-20% lower consistency

**Metrics Implementation:**
- Library: scipy.stats, numpy
- Code:
```python
from scipy.stats import ttest_ind
import numpy as np

# Cohen's d calculation
def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
    return (np.mean(group1) - np.mean(group2)) / pooled_std
```

---

## 8. Visualization Requirements

### Required Figure (Mandatory)
- **Distribution Comparison**: Box plot or violin plot comparing consistency distributions for correct vs incorrect responses

### Additional Figures (LLM Autonomous)
- Histogram overlay of consistency scores by correctness
- Effect size visualization with confidence intervals

**Output Location**: `h-m2/figures/`

---

## 9. PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. mean_consistency(incorrect) < mean_consistency(correct) (direction correct)
3. Cohen's d > 0.2 (effect detectable)

**Mechanism Verification:**
- Pre-condition: h-e1 consistency computation validated
- Activation indicator: Statistically significant difference in means
- Failure detection: If d < 0.2 or direction reversed

---

## Appendix: Reference Implementations

### A. SelfCheckGPT
- **Source**: Manakul et al. 2023
- **URL**: https://github.com/potsawee/selfcheckgpt
- **Used for**: N-sample consistency methodology

### B. h-e1 Validation Results
- **Source**: Phase 4 h-e1 validation
- **Reused**: Generated responses, consistency scores, ground truth labels

### Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset | Standard | TruthfulQA (Lin et al. 2022) |
| Model | Pretrained | meta-llama/Llama-2-7b-hf |
| Consistency method | Paper | SelfCheckGPT |
| Analysis protocol | h-e1 | Previous hypothesis validation |
| Effect size metric | Statistics | Cohen's d standard |

---

*MCP Tools Used: None (ablation mode)*
*Specifications grounded in h-e1 validated implementation*
*Next Phase: Phase 3 - Implementation Planning*
