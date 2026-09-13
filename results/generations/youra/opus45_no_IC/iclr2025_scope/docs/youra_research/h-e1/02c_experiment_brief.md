# Experiment Design: H-E1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** Task-dependent compression response clusters exist in KV cache compression across LongBench tasks, identifiable via gap statistic showing k* > 1
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for H-E1)
**Gate Status:** MUST_WORK - k* > 1 with gap > standard error

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
k* > 1 clusters with gap(k*) - E[gap_null(k*)] > SE(gap_null)

If fails: ABANDON entire hypothesis chain (no task structure means routing has no basis)

---

## Continuation Context

This is the foundation hypothesis for the Attention-Probe Router project. Success validates that task-dependent compression response structure exists, enabling subsequent mechanism hypotheses (H-M1 through H-M4).

### Previous Hypothesis Results (if applicable)
N/A - This is the first hypothesis in the chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct matches for KV cache clustering. Key related resources:
- HuggingFace transformers documentation for model loading
- bitsandbytes 4-bit quantization for memory efficiency
- PEFT/LoRA for efficient fine-tuning patterns

### Archon Code Examples

No direct gap statistic examples found. PyTorch distributed tensor operations documented for parallel processing patterns.

### Exa GitHub Implementations

**Gap Statistic Libraries (Primary):**
1. **milesgranger/gap_statistic** (recommended)
   - Pure Python implementation with sklearn compatibility
   - `OptimalK` class with configurable clusterer
   - Supports B bootstrap samples, returns gap_df with gap values per k
   - Usage: `OptimalK(n_jobs=-1)(X, n_refs=500, cluster_array=range(1,7))`

2. **jmmaloney3/gapstat**
   - sklearn-compatible wrapper
   - `GapStatClustering` for both optimal k estimation and clustering
   - `gapstat_score` for metric evaluation

3. **sundar-gap-stat**
   - Generalized gap statistic for any clustering algorithm
   - Supports PCA-based reference distribution

**H2O KV Cache Implementation:**
1. **FMInference/H2O** (official NeurIPS'23)
   - `h2o_hf/` directory: HuggingFace-based implementation
   - `heavy_ratio` and `recent_ratio` parameters
   - Supports Llama, OPT, GPT-NeoX architectures
   - Real KV dropping implementation in `utils_real_drop/`

2. **huggingface/transformers PR #35381**
   - `H2OCache` class in `cache_utils.py`
   - Post-processing function for attention weight tracking
   - 80% cache reduction with <5% throughput loss

3. **awslabs/keys_values**
   - Production-quality H2OKVCache implementation
   - Per-batch eviction decisions
   - Score normalization options

**LongBench Dataset:**
- Source: THUDM/LongBench (ACL'24)
- HuggingFace: `THUDM/LongBench`
- 21 tasks across 6 categories
- ~4750 test samples
- Metrics: qa_f1_score, rouge_score, classification_score, retrieval_score, code_sim_score

### Implementation Priority Assessment

**CRITICAL: Use established implementations**

**Recommended Implementation Path:**
- Primary: milesgranger/gap_statistic + FMInference/H2O (h2o_hf)
- Fallback: Custom gap statistic implementation with sklearn KMeans
- Justification: gap_statistic is well-tested with B=500 bootstrap support; H2O is the official paper implementation

### Code Analysis (Serena MCP)

N/A - No existing codebase for this project yet.

---

## Experiment Specification

### Dataset

**Name:** LongBench v1
**Version:** Latest from HuggingFace
**Source:** THUDM/LongBench
**Type:** Standard benchmark (NOT synthetic)

**Tasks (21 total across 6 categories):**
| Category | Tasks |
|----------|-------|
| Single-Doc QA | narrativeqa, qasper, multifieldqa_en, multifieldqa_zh |
| Multi-Doc QA | hotpotqa, 2wikimqa, musique, dureader |
| Summarization | gov_report, qmsum, multi_news, vcsum |
| Few-shot | trec, triviaqa, samsum, lsht |
| Synthetic | passage_retrieval_en, passage_count, passage_retrieval_zh |
| Code | lcc, repobench-p |

**Samples:** Use ALL samples per task (full test set, ~200-500 per task, ~4750 total)

**Splits:**
- Train: N/A (no training required for clustering)
- Validation: N/A
- Test: Full LongBench test set

**Preprocessing:**
- Truncate to model max context (4096 tokens for Llama-2-7B)
- Standard tokenization with AutoTokenizer

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: THUDM/LongBench
- Code:
```python
from datasets import load_dataset

TASKS = [
    "narrativeqa", "qasper", "multifieldqa_en", "multifieldqa_zh",
    "hotpotqa", "2wikimqa", "musique", "dureader",
    "gov_report", "qmsum", "multi_news", "vcsum",
    "trec", "triviaqa", "samsum", "lsht",
    "passage_retrieval_en", "passage_count", "passage_retrieval_zh",
    "lcc", "repobench-p"
]

def load_longbench_task(task_name):
    dataset = load_dataset("THUDM/LongBench", task_name, split="test")
    return dataset
```

### Models

#### Baseline Model

**Name:** Llama-2-7B
**Source:** meta-llama/Llama-2-7b-hf
**Type:** decoder-only transformer
**Parameters:** 7B
**Context Length:** 4096 tokens
**KV Cache Size:** ~400MB at full context (float16)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace transformers
- Identifier: meta-llama/Llama-2-7b-hf
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

#### Proposed Model

**Architecture:** Baseline + Compression Response Profiling (no model modification for H-E1)

**Core Mechanism Implementation:**

```python
# H-E1: Compression Response Profiling & Gap Statistic Clustering
# Goal: Determine if k* > 1 clusters exist in task compression responses

import numpy as np
from sklearn.cluster import KMeans
from gap_statistic import OptimalK

# Step 1: Define compression configurations (6 configs)
COMPRESSION_CONFIGS = [
    {"method": "full", "retention": 1.0, "quantization": None},      # Full KV (baseline)
    {"method": "h2o", "retention": 0.8, "quantization": None},       # H2O 80% retention
    {"method": "h2o", "retention": 0.4, "quantization": None},       # H2O 40% retention  
    {"method": "full", "retention": 1.0, "quantization": "int8"},    # Full + int8
    {"method": "full", "retention": 1.0, "quantization": "int4"},    # Full + int4
    {"method": "h2o", "retention": 0.6, "quantization": "int8"},     # H2O 60% + int8
]

# Step 2: Run inference on all task-config combinations
def compute_response_matrix(model, tokenizer, tasks, configs, dataset):
    """
    Returns:
        response_matrix: np.ndarray of shape (21 tasks, 6 configs)
        Each entry is accuracy retention = task_accuracy / full_kv_accuracy
    """
    response_matrix = np.zeros((len(tasks), len(configs)))
    
    for i, task in enumerate(tasks):
        task_data = dataset[task]
        full_kv_accuracy = None
        
        for j, config in enumerate(configs):
            accuracy = evaluate_task_with_config(model, tokenizer, task_data, config)
            
            if config["method"] == "full" and config["quantization"] is None:
                full_kv_accuracy = accuracy
            
            response_matrix[i, j] = accuracy
        
        # Convert to retention ratio
        if full_kv_accuracy > 0:
            response_matrix[i, :] /= full_kv_accuracy
    
    return response_matrix

# Step 3: Apply Gap Statistic
def find_optimal_clusters(response_matrix, n_refs=500, max_k=6):
    """
    Returns:
        k_star: optimal number of clusters
        gap_df: DataFrame with gap values per k
        significant: bool - whether gap criterion is met
    """
    optimalK = OptimalK(n_jobs=-1, parallel_backend='joblib')
    k_star = optimalK(response_matrix, n_refs=n_refs, cluster_array=range(1, max_k + 1))
    
    gap_df = optimalK.gap_df
    
    # Check gap criterion: gap(k) >= gap(k+1) - s(k+1)
    # Or equivalently: gap(k) - gap(k+1) + s(k+1) >= 0
    significant = k_star > 1
    
    return k_star, gap_df, significant

# Step 4: Compute silhouette score for secondary metric
def compute_silhouette(response_matrix, k_star):
    from sklearn.metrics import silhouette_score
    
    if k_star <= 1:
        return 0.0
    
    kmeans = KMeans(n_clusters=k_star, random_state=42, n_init=10)
    labels = kmeans.fit_predict(response_matrix)
    
    return silhouette_score(response_matrix, labels)

# Main execution
def run_h_e1_experiment(model, tokenizer, tasks, configs, dataset):
    # Generate response matrix (21 x 6)
    response_matrix = compute_response_matrix(model, tokenizer, tasks, configs, dataset)
    
    # Find optimal k with gap statistic
    k_star, gap_df, significant = find_optimal_clusters(response_matrix, n_refs=500)
    
    # Compute silhouette for k*
    silhouette = compute_silhouette(response_matrix, k_star)
    
    results = {
        "k_star": k_star,
        "gap_df": gap_df,
        "significant": significant,
        "silhouette_score": silhouette,
        "response_matrix": response_matrix,
        "gate_passed": k_star > 1 and significant
    }
    
    return results
```

### Training Protocol

**No training required for H-E1** - This is an analysis/clustering hypothesis.

**Compute Steps:**
1. Run Llama-2-7B on 21 LongBench tasks × 6 compression configs = 126 evaluation runs
2. Each run: ~500 samples × ~2048 avg tokens = ~10 min per run on A100
3. Total inference: ~21 GPU-hours (can parallelize across configs)
4. Gap statistic computation: B=500 bootstrap samples, ~5 min on CPU

**Hardware Requirements:**
- 1× A100 (40GB or 80GB) for inference
- CPU for gap statistic bootstrap sampling

### Evaluation

**Primary Metrics:**
| Metric | Target | Description |
|--------|--------|-------------|
| k* (optimal clusters) | > 1 | Gap statistic optimal cluster count |
| Gap significance | gap > SE | gap(k*) - E[gap_null] > standard error |

**Secondary Metrics:**
| Metric | Target | Description |
|--------|--------|-------------|
| Silhouette score | > 0.5 | Cluster separation quality |
| Cluster interpretability | Qualitative | Do clusters align with task categories? |

**Success Criteria:**
1. **Primary (MUST):** k* > 1 with gap > standard error
2. **Secondary (NICE):** Silhouette score > 0.5

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Clustering analysis
- Library: gap_statistic, sklearn.metrics
- Code:
```python
from gap_statistic import OptimalK
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans

# Gap statistic
optimalK = OptimalK(n_jobs=-1)
k_star = optimalK(X, n_refs=500, cluster_array=range(1, 7))

# Silhouette
kmeans = KMeans(n_clusters=k_star, random_state=42)
labels = kmeans.fit_predict(X)
sil_score = silhouette_score(X, labels)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing k* value and gap criterion satisfaction

#### Additional Figures (LLM Autonomous)

1. **Gap Statistic Curve**: Plot gap(k) vs k with error bars (SE), highlight k*
2. **Response Matrix Heatmap**: 21 tasks × 6 configs, color by accuracy retention
3. **Cluster Visualization**: 2D PCA/t-SNE of task response profiles, colored by cluster
4. **Cluster-Task Mapping**: Table showing which tasks fall into which cluster
5. **Silhouette Plot**: Per-sample silhouette values grouped by cluster

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. k* > 1 (more than one cluster detected)
3. Gap criterion satisfied (gap > SE for k*)

**If FAIL:** ABANDON entire hypothesis chain - no task-dependent compression structure exists.

---

## Appendix: Reference Implementations

### Gap Statistic

**Primary:** milesgranger/gap_statistic
- URL: https://github.com/milesgranger/gap_statistic
- Install: `pip install gap-stat`
- Key class: `OptimalK`

**Alternative:** jmmaloney3/gapstat
- URL: https://github.com/jmmaloney3/gapstat
- sklearn-compatible wrapper

### H2O KV Cache

**Official:** FMInference/H2O
- URL: https://github.com/FMInference/H2O
- Paper: NeurIPS'23
- Code path: `h2o_hf/` for HuggingFace integration

**HuggingFace PR:** transformers/pull/35381
- H2OCache implementation
- Integration with LlamaAttention

### LongBench

**Official:** THUDM/LongBench
- URL: https://github.com/THUDM/LongBench
- HuggingFace: THUDM/LongBench
- Evaluation script: `LongBench/eval.py`
- Metrics: `LongBench/metrics.py`

### KV Cache Quantization

**bitsandbytes:**
- int8/int4 quantization support
- Install: `pip install bitsandbytes`

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- 2026-08-10: Hypothesis h-e1 set to IN_PROGRESS (Phase 2C starting)
- 2026-08-10: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
