# Experiment Design: h-m1

**Date:** 2026-08-10
**Author:** Anonymous
**Hypothesis Statement:** LLMs produce category-specific confidence distributions on TruthfulQA
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Tests causal mechanism underlying calibration variation.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 PASS)
**Gate Status:** MUST_WORK - KS test p < 0.05 for majority of cluster pairs

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (COMPLETED, PASS)

### Gate Condition
KS test p < 0.05 for majority of cluster pairs (≥ 11 of 21 pairs significant)

---

## Continuation Context

Building on h-e1 validation which confirmed category-dependent ECE variation exists:
- ANOVA F=8.45, p=0.00012
- ECE range across clusters = 0.099 (exceeds 0.05 threshold)

This mechanism hypothesis tests whether different ECE values arise from genuinely different underlying confidence distributions.

### Previous Hypothesis Results (if applicable)
**h-e1 Results:**
- Gate: PASS
- Evidence: Significant variation in per-cluster ECE (ANOVA p < 0.05)
- Implication: Clusters exhibit different calibration behavior — now test if distributions differ

---

## Implementation Research Summary

### Archon Knowledge Base Findings

No direct matches for KS test or confidence distribution analysis in Archon KB. Knowledge base primarily contains diffusion model examples.

### Archon Code Examples

No relevant statistical test code found in Archon. Will use scipy.stats standard implementations.

### Exa GitHub Implementations

**Key Resources Found:**

1. **scipy.stats.ks_2samp** (Official Documentation)
   - Two-sample Kolmogorov-Smirnov test for goodness of fit
   - Compares underlying continuous distributions of two samples
   - Returns: statistic (D), p-value
   - Usage: `ks_2samp(sample1, sample2, alternative='two-sided')`
   - p < 0.05 rejects null hypothesis that samples from same distribution

2. **TruthfulQA Calibration Research** (EMNLP/ACL 2024)
   - "When to Trust LLMs: Aligning Confidence with Response" - Uses TruthfulQA + ECE
   - "Calibrating Language Models with Adaptive Temperature Scaling"
   - Confirms LLM confidence varies by question category

3. **honest-confidence** (GitHub)
   - TruthfulQA eval measuring calibration (ECE, AUROC)
   - 817 questions benchmark
   - Reports confidence distributions differ by question type

4. **Reuse from h-e1:**
   - TruthfulQA loading code
   - Category-to-cluster mapping (38 → 7 clusters)
   - Confidence extraction infrastructure

### 🎯 Implementation Priority Assessment

**Reuse h-e1 infrastructure, add KS test layer**

**Recommended Implementation Path:**
- Primary: scipy.stats.ks_2samp for pairwise cluster comparisons
- Fallback: scipy.stats.kstest (unified interface)
- Justification: Standard scipy implementation, well-documented, exact p-values for n < 10000

### Code Analysis (Serena MCP)

Reusing h-e1 codebase infrastructure (confidence extraction, cluster assignment). No additional code analysis needed.

---

## Experiment Specification

### Dataset

**Name:** TruthfulQA
**Version:** HuggingFace `truthfulqa/truthful_qa` (multiple_choice split)
**Type:** standard

| Property | Value |
|----------|-------|
| Total Questions | 817 |
| Categories | 38 original |
| Clusters | 7 (semantic grouping) |
| Samples per Cluster | ~100-150 |

**Reuse from h-e1:** Same dataset, same cluster mapping. This experiment extracts confidence values for distribution analysis.

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets
- Identifier: `truthfulqa/truthful_qa`
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
```

### Models

#### Baseline Model

**Name:** Llama-2-7B
**Source:** HuggingFace Hub (`meta-llama/Llama-2-7b-hf`)
**Type:** Decoder-only transformer

| Property | Value |
|----------|-------|
| Parameters | 7B |
| Architecture | LlamaForCausalLM |
| Precision | float16 |
| Device | Single GPU (A100 recommended) |

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

#### Proposed Model

**Architecture:** Same as baseline (MECHANISM test — no model changes)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Pairwise KS tests on cluster confidence distributions
# Lines: 28 (within spec)

import numpy as np
from scipy.stats import ks_2samp
from itertools import combinations

def extract_cluster_confidences(logits_by_cluster):
    """Extract confidence values (max softmax) per cluster."""
    cluster_confidences = {}
    for cluster_id, logits in logits_by_cluster.items():
        probs = torch.softmax(torch.tensor(logits), dim=-1)
        confidences = probs.max(dim=-1).values.numpy()
        cluster_confidences[cluster_id] = confidences
    return cluster_confidences

def pairwise_ks_tests(cluster_confidences):
    """Run KS tests on all cluster pairs."""
    cluster_ids = sorted(cluster_confidences.keys())
    results = {}
    
    for c1, c2 in combinations(cluster_ids, 2):
        conf1 = cluster_confidences[c1]
        conf2 = cluster_confidences[c2]
        stat, pvalue = ks_2samp(conf1, conf2, alternative='two-sided')
        results[(c1, c2)] = {'statistic': stat, 'pvalue': pvalue}
    
    return results

def evaluate_gate_condition(ks_results):
    """Check if majority of pairs have p < 0.05."""
    total_pairs = len(ks_results)  # 21 pairs for 7 clusters
    significant_pairs = sum(1 for r in ks_results.values() if r['pvalue'] < 0.05)
    majority_threshold = total_pairs // 2 + 1  # 11 of 21
    gate_passed = significant_pairs >= majority_threshold
    return gate_passed, significant_pairs, total_pairs
```

### Training Protocol

**Note:** This is a MECHANISM test — no training required.

| Parameter | Value |
|-----------|-------|
| Training | None (inference only) |
| Inference Mode | Teacher-forced MC evaluation |
| Batch Size | 8 |
| Precision | float16 |

**Inference Protocol (reuse from h-e1):**
1. For each question, compute log-probabilities for each answer choice
2. Extract softmax confidence (max probability)
3. Group confidences by cluster
4. Run pairwise KS tests

### Evaluation

**Primary Metric:** Count of significant KS tests (p < 0.05) out of 21 pairs

**Success Criteria (PoC):**
- Primary: ≥ 11 of 21 cluster pairs have KS test p < 0.05
- Secondary: Mean confidence differs by > 0.1 across clusters

| Metric | Formula | Target |
|--------|---------|--------|
| KS significant pairs | count(p < 0.05) | ≥ 11/21 |
| Per-cluster mean confidence | mean(conf) per cluster | Report all 7 |
| Per-cluster std confidence | std(conf) per cluster | Report all 7 |
| Confidence range | max(mean) - min(mean) | > 0.1 |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Distribution comparison
- Library: scipy.stats
- Code:
```python
from scipy.stats import ks_2samp
from itertools import combinations

# For each cluster pair
stat, pvalue = ks_2samp(conf_cluster_i, conf_cluster_j)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **KS Test Results Matrix**: Heatmap of p-values for all 21 cluster pairs (significant pairs highlighted)

#### Additional Figures (LLM Autonomous)

1. **Confidence Histogram per Cluster**: 7 overlaid histograms showing confidence distributions
2. **Cluster Confidence Box Plot**: Box plot comparing confidence distributions across clusters
3. **CDF Comparison**: Empirical CDFs for each cluster (visual KS test)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. KS test p < 0.05 for ≥ 11 of 21 cluster pairs (majority)
3. Mean confidence range across clusters > 0.1

**Failure Response:** IF < 11 pairs significant → PIVOT to alternative clustering strategy

---

## Appendix: Reference Implementations

### scipy.stats.ks_2samp (from SciPy documentation)

```python
from scipy.stats import ks_2samp
import numpy as np

# Example: Two samples from different distributions
np.random.seed(12345678)
x = np.random.normal(0, 1, 1000)
z = np.random.normal(1.1, 0.9, 1000)

# KS test - different distributions
result = ks_2samp(x, z)
# Ks_2sampResult(statistic=0.418, pvalue=3.7e-77)
# p < 0.05 → reject null → distributions differ
```

### Pairwise Comparison Pattern

```python
from itertools import combinations
from scipy.stats import ks_2samp

def pairwise_ks_matrix(cluster_data):
    """Generate KS test matrix for all cluster pairs."""
    cluster_ids = sorted(cluster_data.keys())
    n_clusters = len(cluster_ids)
    
    # Initialize result matrix
    pvalue_matrix = np.ones((n_clusters, n_clusters))
    stat_matrix = np.zeros((n_clusters, n_clusters))
    
    for i, c1 in enumerate(cluster_ids):
        for j, c2 in enumerate(cluster_ids):
            if i < j:
                stat, pval = ks_2samp(cluster_data[c1], cluster_data[c2])
                pvalue_matrix[i, j] = pval
                pvalue_matrix[j, i] = pval
                stat_matrix[i, j] = stat
                stat_matrix[j, i] = stat
    
    return pvalue_matrix, stat_matrix, cluster_ids
```

### Reused Infrastructure from h-e1

```python
# Category to Cluster Mapping (same as h-e1)
CATEGORY_TO_CLUSTER = {
    "Health": 1, "Nutrition": 1, "Psychology": 1,
    "Law": 2, "Politics": 2, "Government": 2,
    "Finance": 3, "Economics": 3,
    "Science": 4, "Technology": 4, "Math": 4, "Physics": 4, "Biology": 4,
    "History": 5, "Geography": 5, "Culture": 5,
    "Religion": 6, "Philosophy": 6, "Ethics": 6,
    "Misconceptions": 7, "Myths": 7, "Superstitions": 7, "Conspiracies": 7,
    # ... (full mapping in h-e1/02c_experiment_brief.md)
}

# Confidence extraction (same as h-e1)
def extract_confidence(model, tokenizer, question, choices):
    # ... (reuse from h-e1)
    pass
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-10

### Workflow History for This Hypothesis
- h-e1 completed with PASS (ANOVA p=0.00012, ECE range=0.099)
- h-m1 experiment design IN_PROGRESS → COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
