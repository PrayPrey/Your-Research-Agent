# Methodology

Building on our observation that LoRA constrains weight updates to interpretable low-rank subspaces, we design a methodology to test whether these subspaces encode task-specific geometric signatures. Our approach has two components: (1) controlled adapter generation that isolates task as the only experimental variable, and (2) Grassmann distance analysis that measures subspace alignment between adapters.

## Overview

The core hypothesis is that semantically similar tasks require similar functional transformations, which manifest as similar $B$ matrix column spaces in LoRA adapters. To test this, we need:

1. **Controlled provenance:** Adapters trained under identical conditions except for the task, eliminating confounds from base model mismatch, hyperparameter variation, or training procedure differences.

2. **Geometric comparison:** A metric that captures subspace alignment between $B$ matrices, quantifying how "similar" the learned transformation subspaces are.

Figure 1 illustrates our approach: multiple tasks are fine-tuned with LoRA under controlled conditions, yielding adapters whose $B$ matrix column spaces are compared via Grassmann distance.

## Controlled Adapter Generation

### Design Rationale

Previous attempts to analyze LoRA adapter geometry used public collections (e.g., HuggingFace Hub) where adapters have mixed provenance: different base model checkpoints, quantization levels, LoRA configurations, and training hyperparameters. These uncontrolled variables confound any geometric signal with experimental artifacts.

**Our approach:** We generate adapters in-house with verified provenance. A single base model checkpoint (SHA-256 hash verified) is fine-tuned with identical LoRA configuration and training hyperparameters across all tasks. The *only* variable that changes is the training task.

### LoRA Configuration

We use standard LoRA with the following fixed configuration:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Rank ($r$) | 32 | Balance between expressivity and low-rank constraint |
| Alpha ($\alpha$) | 64 | Standard scaling factor ($\alpha/r = 2$) |
| Dropout | 0.05 | Mild regularization |
| Target modules | q, k, v, o, up, down, gate | All attention and MLP projections |

The LoRA update for a weight matrix $W_0$ is:
$$W = W_0 + \frac{\alpha}{r} BA$$
where $B \in \mathbb{R}^{d \times r}$ and $A \in \mathbb{R}^{r \times k}$. The $B$ matrix projects into the output dimension, encoding task-specific output transformations.

### Training Protocol

All adapters are trained with identical hyperparameters:

| Parameter | Value |
|-----------|-------|
| Learning rate | $2 \times 10^{-4}$ |
| Batch size | 8 |
| Epochs | 3 |
| Optimizer | AdamW |
| Warmup ratio | 0.1 |
| Max sequence length | 512 |

For each task, we train multiple adapters with different random seeds (42, 43, 44, 45, 46) to assess within-task variance. This yields a P3 control condition: if geometric signatures reflect task structure, within-task adapters (same task, different seeds) should be more similar than within-category adapters (different tasks, same category).

### Task Selection

We select 8 tasks spanning two FLAN categories [Wei et al., 2022]:

**Reasoning (4 tasks):**
- GSM8K: Grade school math word problems
- ARC-Challenge: Science reasoning questions
- LogiQA: Logical reasoning
- StrategyQA: Multi-hop reasoning

**Natural Language Understanding (4 tasks):**
- MNLI: Natural language inference
- QQP: Paraphrase detection
- SST-2: Sentiment classification
- MRPC: Semantic similarity

This selection provides clear category separation (reasoning vs. NLU) while using established benchmarks with standardized evaluation protocols.

## Grassmann Distance Analysis

### Why Grassmann Distance?

The $B$ matrix column space defines the subspace of possible output transformations. To compare two adapters, we need a metric that captures how aligned their transformation subspaces are, invariant to basis choice within each subspace.

The Grassmann manifold $\text{Gr}(r, d)$ is the space of $r$-dimensional linear subspaces of $\mathbb{R}^d$. The Grassmann geodesic distance measures the "angle" between two subspaces, providing a principled metric for subspace comparison.

### Computing Grassmann Distance

Given two $B$ matrices $B_1, B_2 \in \mathbb{R}^{d \times r}$, we compute their Grassmann distance as follows:

**Step 1: Orthonormal bases.** Compute orthonormal bases for the column spaces via QR decomposition or SVD:
$$B_i = U_i \Sigma_i V_i^T \implies \text{basis}_i = U_i[:, :r]$$

**Step 2: Principal angles.** Compute the principal angles $\theta_1, \ldots, \theta_r$ between the subspaces using:
$$\cos(\theta_j) = \sigma_j(U_1^T U_2)$$
where $\sigma_j$ denotes the $j$-th singular value.

**Step 3: Grassmann distance.** The geodesic distance is:
$$d_G(B_1, B_2) = \sqrt{\sum_{j=1}^{r} \theta_j^2}$$

This distance is zero when subspaces are identical and maximal ($\frac{\pi}{2}\sqrt{r}$) when subspaces are orthogonal.

### Implementation

We use `scipy.linalg.subspace_angles` to compute principal angles, which provides numerically stable computation even for near-rank-deficient matrices:

```python
from scipy.linalg import subspace_angles
import numpy as np

def grassmann_distance(B1, B2):
    """Compute Grassmann geodesic distance between B matrix column spaces."""
    # Get orthonormal bases via SVD
    U1, _, _ = np.linalg.svd(B1, full_matrices=False)
    U2, _, _ = np.linalg.svd(B2, full_matrices=False)
    # Principal angles
    angles = subspace_angles(U1, U2)
    # Geodesic distance
    return np.sqrt(np.sum(angles**2))
```

### Aggregation Across Layers

Each LoRA adapter contains $B$ matrices for multiple layers (7 layer types × 22 layers = 154 matrices for TinyLlama-1.1B). We compute Grassmann distances per layer and aggregate:

**Default aggregation:** Mean across all layers, giving equal weight to each layer's geometric contribution.

**Layer-type analysis:** Separate computation per layer type (q_proj, k_proj, etc.) to test for layer-specific clustering.

## Statistical Analysis

### Hypothesis Testing

We test the main hypothesis using the Mann-Whitney U test, which compares the distributions of within-category and between-category Grassmann distances without assuming normality:

$$H_0: \text{median}(d_{\text{within}}) = \text{median}(d_{\text{between}})$$
$$H_1: \text{median}(d_{\text{within}}) < \text{median}(d_{\text{between}})$$

### Effect Size

We report Cohen's $d$ as the standardized effect size:
$$d = \frac{\bar{x}_{\text{between}} - \bar{x}_{\text{within}}}{s_{\text{pooled}}}$$

Following standard conventions: $d > 0.2$ (small), $d > 0.5$ (medium), $d > 0.8$ (large).

### Correlation Analysis

To validate the mechanism---that geometric similarity reflects semantic similarity---we compute Spearman rank correlation between:
- Pairwise Grassmann distances (continuous)
- FLAN taxonomy distances (binary: 0 = same category, 1 = different category)

### Sample Size Justification

Power analysis for Cohen's $d = 0.9$ (based on prior underpowered results) with $\alpha = 0.05$ and power $= 0.80$ requires $n \geq 17$ samples per group. With 8 tasks × 5 seeds = 40 adapters, we have:
- Within-category pairs: $2 \times \binom{20}{2} = 380$
- Between-category pairs: $20 \times 20 = 400$

This provides adequate statistical power for detecting medium-to-large effects.
