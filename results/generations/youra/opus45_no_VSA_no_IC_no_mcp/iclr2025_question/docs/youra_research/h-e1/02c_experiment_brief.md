# Experiment Brief: H-E1 Individual Method Predictive Validity

**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Generated:** 2026-08-28

---

## 1. Hypothesis Statement

**Under-If-Then-Because:**
Under closed-book QA conditions (TruthfulQA), if we compute token entropy and N-sample consistency for LLM responses, then both methods individually predict factual correctness above chance (AUROC > 0.55 each), because each captures a distinct uncertainty signal.

**Success Criteria:**
- Primary: entropy_AUROC > 0.55 AND consistency_AUROC > 0.55
- Secondary: Both methods significantly better than random (p < 0.05)

**Failure Response:** ABANDON — fundamental assumption violated

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
- Sufficient for AUROC estimation with 95% CI ± 0.03
- No subsampling needed

**Data Loading:**
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

**Model Loading:**
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

## 4. Metric Computation

### 4.1 Token Entropy

**Definition:** Mean Shannon entropy over token-level logit distributions during generation.

```python
import torch
import torch.nn.functional as F

def compute_token_entropy(logits: torch.Tensor) -> float:
    # logits: [seq_len, vocab_size]
    probs = F.softmax(logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    entropy = -torch.sum(probs * log_probs, dim=-1)  # [seq_len]
    return entropy.mean().item()
```

**Aggregation:** Mean over generated tokens (excluding prompt)

**Reference:** 
- [logtoku](https://github.com/MaHuanAAA/logtoku) - Logits-based uncertainty
- [LLM-Uncertainty-Bench](https://github.com/smartyfh/LLM-Uncertainty-Bench)

### 4.2 N-Sample Consistency

**Definition:** Semantic similarity between N=5 sampled responses using embedding cosine similarity.

```python
from sentence_transformers import SentenceTransformer
import numpy as np

encoder = SentenceTransformer('all-MiniLM-L6-v2')

def compute_consistency(responses: list[str]) -> float:
    # responses: list of N=5 sampled responses
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
```

**Parameters:**
- N = 5 samples per question
- Temperature = 1.0 for sampling diversity
- Embedding model: sentence-transformers/all-MiniLM-L6-v2

**Reference:**
- [SelfCheckGPT](https://github.com/potsawee/selfcheckgpt) - Original implementation
- pip install selfcheckgpt

---

## 5. Ground Truth Labels

**Labeling Strategy:**
TruthfulQA provides reference answers. Label model response as:
- **Correct (0):** Response semantically matches `best_answer` (BERTScore F1 > 0.5 with best_answer)
- **Incorrect/Hallucinated (1):** Response matches `incorrect_answers` better OR BERTScore < 0.5 with best_answer

```python
from bert_score import score as bert_score

def label_response(response: str, best_answer: str, incorrect_answers: list[str]) -> int:
    # Compute BERTScore with best answer
    P, R, F1 = bert_score([response], [best_answer], lang="en", rescale_with_baseline=True)
    best_score = F1.item()
    
    # Compute max BERTScore with incorrect answers
    if incorrect_answers:
        _, _, F1_inc = bert_score(
            [response] * len(incorrect_answers), 
            incorrect_answers, 
            lang="en", 
            rescale_with_baseline=True
        )
        worst_score = F1_inc.max().item()
    else:
        worst_score = 0.0
    
    # Label: 1 if hallucinated (matches incorrect better or low match with best)
    if worst_score > best_score or best_score < 0.5:
        return 1  # hallucinated
    return 0  # correct
```

---

## 6. Evaluation Protocol

### 6.1 Pipeline

```
For each question in TruthfulQA (817 total):
  1. Generate response with greedy decoding → get logits → compute entropy
  2. Generate N=5 responses with temperature=1.0 → compute consistency
  3. Label response correctness using BERTScore against reference
  4. Store: (question_id, entropy_score, consistency_score, label)
```

### 6.2 AUROC Computation

```python
from sklearn.metrics import roc_auc_score

# entropy: higher = more uncertain = more likely hallucinated
entropy_auroc = roc_auc_score(labels, entropy_scores)

# consistency: lower = less consistent = more likely hallucinated  
# Flip sign for AUROC (higher score = more hallucinated)
consistency_auroc = roc_auc_score(labels, -np.array(consistency_scores))
```

### 6.3 Statistical Significance

```python
from scipy import stats

def auroc_ci(y_true, y_score, n_bootstrap=1000):
    """Bootstrap 95% CI for AUROC"""
    rng = np.random.default_rng(42)
    aurocs = []
    n = len(y_true)
    for _ in range(n_bootstrap):
        idx = rng.choice(n, n, replace=True)
        aurocs.append(roc_auc_score(y_true[idx], y_score[idx]))
    return np.percentile(aurocs, [2.5, 97.5])
```

---

## 7. Success Criteria Verification

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Entropy AUROC | > 0.55 | roc_auc_score(labels, entropy_scores) |
| Consistency AUROC | > 0.55 | roc_auc_score(labels, -consistency_scores) |
| Lower CI bound | > 0.50 | Bootstrap 95% CI lower bound |

**Gate Decision:**
- PASS: Both AUROC > 0.55 with CI lower bound > 0.50
- FAIL: Either AUROC ≤ 0.55 → ABANDON hypothesis chain

---

## 8. Resource Estimates

| Resource | Estimate |
|----------|----------|
| GPU | 1x A100 40GB or 2x RTX 3090 |
| Time | 2-4 hours (817 questions × 6 generations each) |
| Storage | ~2GB (logits + embeddings cache) |

**Compute Breakdown:**
- Greedy generation: ~10s/question → 2.3 hours
- Sampled generation (N=5): ~50s/question → 11 hours
- **Optimization:** Batch generation, cache embeddings

---

## 9. Implementation Checklist

- [ ] HuggingFace token with Meta LLaMA access
- [ ] GPU with ≥16GB VRAM
- [ ] Dependencies: transformers, datasets, sentence-transformers, bert-score, sklearn, scipy
- [ ] TruthfulQA dataset downloaded
- [ ] LLaMA-2-7B weights cached

---

## 10. Output Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Raw scores | `results/h-e1/scores.csv` | question_id, entropy, consistency, label |
| Metrics | `results/h-e1/metrics.json` | AUROC values, CIs, sample counts |
| Plots | `results/h-e1/roc_curves.png` | ROC curves for both methods |

---

## 11. References

### Implementation Resources
- [logtoku](https://github.com/MaHuanAAA/logtoku) - Logits-based LLM uncertainty
- [SelfCheckGPT](https://github.com/potsawee/selfcheckgpt) - N-sample consistency
- [LLM-Uncertainty-Bench](https://github.com/smartyfh/LLM-Uncertainty-Bench) - Benchmarking framework
- [kernel-language-entropy](https://github.com/AlexanderVNikitin/kernel-language-entropy) - Semantic entropy (NeurIPS'24)

### Papers
- Manakul et al. 2023 - SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection
- Lin et al. 2022 - TruthfulQA: Measuring How Models Mimic Human Falsehoods
- Kuhn et al. 2023 - Semantic Uncertainty

---

**Phase 2C Complete** | Ready for Phase 3 Implementation Planning
