# Methodology

Building on Martin and Mahoney's observation that heavy-tailed weight distributions indicate generalization quality, we design a measurement pipeline to test whether this theory extends to Vision Transformer attention mechanisms.

## Overview

Our methodology has three components: (1) model collection from HuggingFace Hub, (2) heavy-tailed exponent computation via the Hill estimator, and (3) variance analysis across model populations.

**Design Rationale.** We use WeightWatcher, the canonical implementation of HT-SR analysis by Martin and Mahoney. This ensures methodological continuity with prior CNN analysis while testing on a new architecture class. By sampling from HuggingFace rather than a curated zoo, we test under realistic heterogeneity conditions.

## Model Collection

We collect Vision Transformer models from HuggingFace Model Hub using the following criteria:

```
Filter: pipeline_tag = image-classification
Search: model name contains "vit"
Sort: downloads (descending)
Target: 100 models
```

**Rationale.** Filtering by downloads prioritizes well-established models with community validation, reducing noise from abandoned or experimental checkpoints. The ViT architecture family provides a clean test case with standardized attention mechanisms.

Models are loaded via HuggingFace Transformers:

```python
from transformers import AutoModel
model = AutoModel.from_pretrained(model_id)
```

## Heavy-Tailed Exponent Computation

For each model, we compute the heavy-tailed exponent α using WeightWatcher:

```python
import weightwatcher as ww

watcher = ww.WeightWatcher(model=model)
details = watcher.analyze()
```

WeightWatcher performs singular value decomposition on each weight matrix and fits a power-law distribution p(x) ∝ x^(-α) using the Hill estimator. The α value characterizes the tail behavior: lower values indicate heavier tails, correlating with better generalization per HT-SR theory.

**Focus on attention layers.** We extract α values specifically for attention-related weight matrices (query, key, value projections) to isolate Transformer-specific behavior:

```python
attention_alphas = details[
    details['layer_name'].str.contains('attention|qkv|query|key|value')
]['alpha'].values
```

## Variance Analysis

We compute two variance metrics:

1. **Global variance** σ_global: Standard deviation of mean α across all models
2. **Within-family variance** σ_family: Standard deviation within model families sharing training origin (e.g., google/vit-*)

**Gate condition.** We set a threshold of σ < 0.5 for bounded variance. This threshold is informed by Unterthiner et al. (2020), who found that predictive accuracy within CNN families required within-population variance below roughly half a standard deviation for stable feature extraction. We adopt this as a conservative bound for cross-architecture analysis.

**Family stratification.** We group models by organizational prefix (google/, facebook/, microsoft/) to test whether training origin affects measurement stability. This addresses the confound that Hub models originate from diverse sources with varying training procedures.

## Outlier Analysis

We characterize outliers (α > 10) to understand variance sources. For each outlier, we examine:

1. Model card metadata (training task, fine-tuning history)
2. Parameter count and architecture variant
3. Training origin and organizational source

This analysis identifies whether outliers reflect methodological limitations or meaningful signal about model characteristics.

## Implementation

All experiments run on a single GPU node. Model loading and α computation typically complete in 30–60 seconds per model. Total pipeline runtime for 53 models: approximately 1744 seconds.

Code and results are available in the supplementary materials.
