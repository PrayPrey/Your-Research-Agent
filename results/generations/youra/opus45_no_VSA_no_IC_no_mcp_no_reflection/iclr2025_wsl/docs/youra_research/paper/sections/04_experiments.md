# Experimental Setup

We design experiments to test whether heavy-tailed self-regularization theory extends to Vision Transformer architectures and whether cross-model measurements achieve bounded variance.

## Research Questions

**RQ1:** Can heavy-tailed exponents α be reliably computed for ViT attention weight matrices using the Hill estimator?

**RQ2:** Is the variance of α bounded (σ < 0.5) across heterogeneous ViT models, enabling cross-model comparison?

**RQ3:** Does controlling for model family (training origin) reduce variance?

## Model Collection

We collect Vision Transformer models from HuggingFace Model Hub.

| Parameter | Value |
|-----------|-------|
| Filter | image-classification |
| Search term | "vit" |
| Sort | Downloads (descending) |
| Target | 100 models |
| Achieved | 53 models |

**Model families included:**
- google/vit-* (n=6)
- facebook/deit-* (n=4)
- microsoft/swin-* (subset)
- Various fine-tuned variants

**Why HuggingFace Hub.** Unlike curated model zoos, the Hub represents realistic heterogeneity: models from diverse organizations, training procedures, and fine-tuning tasks. This tests whether heavy-tailed analysis works under real-world conditions.

## Baselines

This is a measurement study rather than a method comparison. Our baseline is the variance threshold:

**Gate condition:** σ(α) < 0.5

This threshold is informed by prior CNN analysis where stable measurements (low variance) enabled accurate quality prediction. We evaluate whether ViT measurements meet this stability criterion.

## Evaluation Protocol

For each model, we:

1. Load model via HuggingFace Transformers
2. Initialize WeightWatcher analyzer
3. Compute layer-wise α values via Hill estimator
4. Extract α for attention layers specifically
5. Aggregate per-model mean α

**Aggregation metrics:**
- Global mean: μ = mean(α) across all models
- Global variance: σ = std(α) across all models
- Within-family variance: σ_family = std(α) within organizational families

## Implementation Details

| Parameter | Value |
|-----------|-------|
| Framework | PyTorch + WeightWatcher |
| Hardware | Single GPU |
| Per-model time | 30–60 seconds |
| Total runtime | 1744 seconds |

**WeightWatcher configuration:** Default Hill estimator settings, analyzing all weight matrices with automatic layer type detection.

**Failure handling:** Models that fail to load (incompatible architecture, missing weights) are skipped and excluded from analysis. We achieved 53/100 target models (53% success rate).

## Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| α computability | >80% success rate | 53% achieved |
| Variance bound | σ < 0.5 | σ = 2.868 (global), σ = 0.24 (family) |
| α range | [1.5, 4.0] | [2.20, 18.92] observed |

The gate condition (σ < 0.5) determines whether cross-architecture weight analysis is feasible without additional controls.
