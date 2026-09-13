# Methodology

Our approach proceeds in two phases: (1) compression response profiling to generate a task-configuration matrix, and (2) statistical analysis to determine whether tasks cluster and whether attention features predict cluster membership.

## Overview

The core insight motivating our methodology is that if tasks respond differently to compression strategies, this difference should be measurable and potentially predictable. We operationalize this through systematic evaluation across task-configuration combinations, followed by gap statistic analysis to determine whether clusters exist without assuming their number.

## Compression Response Profiling

### Compression Configurations

We define 6 compression configurations spanning eviction and quantization dimensions:

| Config | Method | Retention | Quantization |
|--------|--------|-----------|--------------|
| C1 | Full | 100% | FP16 |
| C2 | H2O | 80% | FP16 |
| C3 | H2O | 40% | FP16 |
| C4 | Full | 100% | INT8 |
| C5 | Full | 100% | INT4 |
| C6 | H2O | 60% | INT8 |

**Rationale:** C1 serves as the baseline. C2-C3 test eviction at conservative and aggressive levels. C4-C5 test quantization at 8-bit and 4-bit. C6 tests a hybrid combining eviction with quantization. This spans the strategy space without exhaustive enumeration.

### Task Evaluation

For each of 21 LongBench tasks $t \in \mathcal{T}$ and each configuration $c \in \mathcal{C}$, we compute accuracy $A(t, c)$ using task-appropriate metrics (F1 for QA, ROUGE for summarization, etc.). The response matrix $\mathbf{R} \in \mathbb{R}^{21 \times 6}$ contains accuracy retention ratios:

$$R_{tc} = \frac{A(t, c)}{A(t, c_{\text{full}})}$$

where $c_{\text{full}}$ is the full-KV baseline (C1). This normalization controls for task difficulty, focusing on *relative* compression sensitivity.

## Cluster Discovery via Gap Statistic

### Why Gap Statistic

Standard clustering algorithms require specifying $k$ a priori. We instead use the gap statistic [Tibshirani et al., 2001] to determine the optimal number of clusters $k^*$ directly from data. This avoids bias from assuming task-compression structure exists.

### Gap Statistic Computation

For $k = 1, \ldots, K_{\max}$:
1. Cluster $\mathbf{R}$ into $k$ groups using $k$-means, computing within-cluster dispersion $W_k$
2. Generate $B$ reference datasets from uniform distribution on the same bounding box
3. Compute expected dispersion $E^*[\log W_k]$ under the null (no structure)
4. Gap: $\text{Gap}(k) = E^*[\log W_k] - \log W_k$

The optimal $k^*$ is the smallest $k$ satisfying:
$$\text{Gap}(k) \geq \text{Gap}(k+1) - s_{k+1}$$

where $s_{k+1}$ is the standard error from bootstrap samples.

**Rationale:** If $k^* > 1$, task-compression structure exists beyond random variation. The gap criterion guards against overfitting by penalizing additional clusters that don't sufficiently reduce dispersion.

### Cluster Validation

We compute silhouette score as a secondary metric:
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

where $a(i)$ is mean intra-cluster distance and $b(i)$ is mean nearest-cluster distance. Silhouette > 0.5 indicates strong separation; > 0.25 indicates reasonable structure.

## Attention Entropy Analysis

### Hypothesis

If attention patterns reflect task structure, early-layer entropy should discriminate task types. High entropy indicates distributed attention (many tokens contribute equally); low entropy indicates focused attention (few tokens dominate).

### Entropy Computation

For each task, we compute attention entropy from the first 100 tokens across all layers and heads:

$$H(\alpha) = -\sum_{i=1}^{n} \alpha_i \log(\alpha_i + \epsilon)$$

where $\alpha$ is the attention probability distribution over keys and $\epsilon = 10^{-10}$ for numerical stability.

**Rationale:** First-100-token entropy is computable before full inference, making it a practical routing signal. If entropy discriminates tasks, it could inform strategy selection without task labels.

### Statistical Test

We perform one-way ANOVA across 6 LongBench task categories (single-doc QA, multi-doc QA, summarization, few-shot, synthetic, code) with entropy as the dependent variable. We report:
- F-statistic and p-value
- Effect size $\eta^2 = SS_{\text{between}} / SS_{\text{total}}$

**Rationale:** Significant F with large $\eta^2$ (> 0.14) indicates entropy meaningfully varies by task domain, supporting the mechanism hypothesis that attention patterns encode task structure.

## Implementation Details

### Model

We use Llama-2-7B (meta-llama/Llama-2-7b-hf) with 32 layers, 32 attention heads, and 4096 context length. KV cache at full context is approximately 400MB in FP16.

### H2O Implementation

We implement H2O eviction following Zhang et al. [2023]:
- Track cumulative attention scores per token
- Retain top-k by attention score plus recent window
- Heavy ratio and recent ratio configurable per experiment

### Evaluation

We use LongBench evaluation scripts with task-appropriate metrics. For clustering analysis, we use the gap_statistic library with $B=500$ bootstrap samples and $K_{\max}=6$.

### Computational Requirements

- 126 inference runs (21 tasks × 6 configs)
- Approximately 21 GPU-hours on A100
- Gap statistic: ~5 minutes CPU

## Summary

Our methodology tests two predictions: (1) task compression responses cluster into $k > 1$ groups (gap statistic on response matrix), and (2) attention entropy discriminates task domains (ANOVA). Positive findings would establish that task-conditioned compression selection has both structure to exploit and a potential detection mechanism.
