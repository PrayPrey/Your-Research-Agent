# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Under RLHF benchmark evaluation, if we compute calibration scores across all tasks, then tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) will cluster non-randomly (silhouette > 0.3), because systematic model behavior patterns exist.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - Silhouette > 0.3 required

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK gate. If silhouette score < 0.3, the entire research stops. This validates whether calibration inversion clusters exist systematically before testing mechanism hypotheses.

---

## Continuation Context

First hypothesis in dependency chain. No previous results to build on.

### Previous Hypothesis Results (if applicable)
N/A - This is the foundation hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP server unavailable - using web research*

**Calibration in LLMs:**
- Calibration measures alignment between model confidence and actual correctness
- Length-normalized log probabilities standard approach for sequence-level calibration
- K-means clustering well-established for identifying behavioral patterns

### Archon Code Examples

*MCP server unavailable - using web research*

**Silhouette Score Implementation:**
```python
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

score = silhouette_score(X, kmeans.labels_, metric='euclidean')
```

### Exa GitHub Implementations

*MCP server unavailable - using web research*

**Key References:**
- scikit-learn silhouette_score: Standard implementation for cluster validation
- lm-evaluation-harness: EleutherAI's framework for benchmark evaluation
- HuggingFace datasets: TruthfulQA, ETHICS available via `datasets` library

### 🎯 Implementation Priority Assessment

**CRITICAL: Standard libraries sufficient for this existence test**

**Recommended Implementation Path:**
- Primary: HuggingFace Transformers + scikit-learn clustering
- Fallback: Manual logprob extraction + numpy clustering
- Justification: Standard tools, well-documented, reproducible

### Code Analysis (Serena MCP)

*MCP server unavailable - no codebase analysis performed*

---

## Experiment Specification

### Dataset

| Attribute | Value |
|-----------|-------|
| **Name** | Combined RLHF Benchmarks |
| **Type** | standard |
| **Source** | TruthfulQA + ETHICS justice + HHH single-turn |
| **Total Samples** | ~1,517 tasks |
| **Split** | Full evaluation set (no train/test split needed - clustering analysis) |

**Component Datasets:**
1. **TruthfulQA:** 817 questions across 38 categories (health, law, finance, politics)
2. **ETHICS justice:** ~500 moral reasoning tasks
3. **HHH single-turn:** ~200 helpfulness/harmlessness preference pairs

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthfulqa/truthful_qa`, `hendrycks/ethics`, `HuggingFaceH4/hhh_alignment`
- Code:
```python
from datasets import load_dataset

# TruthfulQA
truthfulqa = load_dataset("truthfulqa/truthful_qa", "multiple_choice")

# ETHICS - justice subset
ethics = load_dataset("hendrycks/ethics", "justice")

# HHH alignment
hhh = load_dataset("HuggingFaceH4/hhh_alignment")
```

### Models

#### Baseline Model

| Attribute | Value |
|-----------|-------|
| **Name** | Llama-2-7B-Chat |
| **Type** | Instruction-following LLM |
| **Source** | meta-llama/Llama-2-7b-chat-hf |
| **Purpose** | Extract calibration scores for clustering |

**Additional Models (for cross-validation):**
- Llama-2-13B-Chat (meta-llama/Llama-2-13b-chat-hf)
- Mistral-7B-Instruct (mistralai/Mistral-7B-Instruct-v0.2)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Llama-2-7b-chat-hf`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
```

#### Proposed Model

**Architecture:** No proposed model - this is an EXISTENCE test analyzing baseline model behavior.

**Core Mechanism Implementation:**

```python
# Calibration Inversion Detection & Clustering
# 10-30 lines pseudo-code

def compute_calibration_scores(model, tokenizer, dataset):
    """Compute per-task calibration scores."""
    calibration_scores = []
    
    for task in dataset:
        # Get model logprobs for correct and incorrect answers
        correct_logprob = get_sequence_logprob(model, tokenizer, task.correct_answer)
        wrong_logprobs = [get_sequence_logprob(model, tokenizer, ans) 
                         for ans in task.incorrect_answers]
        max_wrong_logprob = max(wrong_logprobs)
        
        # Normalize by sequence length
        correct_logprob_norm = correct_logprob / len(task.correct_answer.split())
        wrong_logprob_norm = max_wrong_logprob / len(task.max_wrong_answer.split())
        
        # Calibration inversion: P(wrong) > P(correct) + threshold
        inversion_score = wrong_logprob_norm - correct_logprob_norm
        calibration_scores.append(inversion_score)
    
    return np.array(calibration_scores)

def cluster_and_evaluate(calibration_scores, k=3):
    """Cluster calibration scores and compute silhouette."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    
    # Reshape for sklearn
    X = calibration_scores.reshape(-1, 1)
    
    # K-means clustering
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)
    
    # Silhouette score
    sil_score = silhouette_score(X, labels)
    
    return {
        "silhouette_score": sil_score,
        "cluster_labels": labels,
        "cluster_centers": kmeans.cluster_centers_,
        "gate_passed": sil_score > 0.3
    }
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **Training Required** | No | This is analysis, not training |
| **Inference Mode** | Evaluation only | Extract logprobs from pre-trained models |
| **Batch Size** | 8 | Memory-efficient inference |
| **Device** | GPU (float16) | Fast inference |
| **Seed** | 42 | Reproducibility |

### Evaluation

| Metric | Target | Justification |
|--------|--------|---------------|
| **Silhouette Score** | > 0.3 | Gate condition for MUST_WORK |
| **Cluster Count** | k=3 | Informed by calibration literature |
| **Inversion Threshold** | 0.1 | P(wrong) > P(correct) + 0.1 |

**PoC Success Criteria (Direction-based):**
1. Silhouette score > 0.3 (primary gate)
2. Clusters show distinct calibration profiles (secondary)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Clustering evaluation
- Library: scikit-learn
- Code:
```python
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.cluster import KMeans

# Compute silhouette
sil_score = silhouette_score(X, labels)
sil_samples = silhouette_samples(X, labels)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Silhouette score vs 0.3 threshold bar chart

#### Additional Figures (LLM Autonomous)

1. **Calibration Score Distribution**: Histogram of calibration inversion scores across all tasks
2. **Cluster Visualization**: Scatter plot of tasks colored by cluster membership
3. **Cluster Profiles**: Box plot showing calibration score distribution per cluster
4. **Cross-Model Consistency**: Heatmap of cluster agreement across models

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `silhouette_score > 0.3` (gate threshold)

**Expected Runtime:** ~30-60 minutes (inference on ~1500 tasks × 3 models)

---

## Appendix: Reference Implementations

### Clustering & Silhouette
- [scikit-learn silhouette_score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.silhouette_score.html)
- [K-Means Silhouette Analysis Tutorial](https://machinelearningmastery.com/k-means-cluster-evaluation-with-silhouette-analysis/)

### Benchmark Datasets
- [TruthfulQA on HuggingFace](https://huggingface.co/datasets/truthfulqa/truthful_qa)
- [ETHICS on HuggingFace](https://huggingface.co/datasets/hendrycks/ethics)
- [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness)

### LLM Calibration
- Lin et al. (2022) "Teaching Models to Express Their Uncertainty in Words"
- Kadavath et al. (2022) "Language Models (Mostly) Know What They Know"

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-E1 set to IN_PROGRESS (Phase 2C experiment design)

---

*MCP Tools Used: Web research (Archon/Exa unavailable)*
*All specifications grounded in standard implementations*
*Next Phase: Phase 3 - Implementation Planning*
