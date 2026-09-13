# Title: 
Hierarchical Diffusion Models with Learnable Structure Priors for Multi-Scale Time Series Generation

## Motivation:
Time series data in science and industry (e.g., climate patterns, physiological signals, financial markets) exhibit complex multi-scale dependencies and domain-specific structural constraints that current generative models struggle to capture. Existing diffusion models for time series treat all temporal scales uniformly, failing to encode known hierarchical structures (seasonality, trends, sudden regime changes) and leading to physically implausible generations. This limits their adoption in critical domains like healthcare and climate science where structural validity is paramount.

## Main Idea:
I propose a hierarchical diffusion framework that decomposes time series generation across multiple temporal scales with explicit structure-aware priors. The key innovation is a **learnable structure extraction module** that:

1. Automatically discovers multi-scale patterns through wavelet-based decomposition combined with attention mechanisms
2. Injects domain knowledge via differentiable constraint layers (e.g., energy conservation, causality)
3. Employs scale-specific diffusion processes—slow diffusion for trends, fast for high-frequency noise

The model uses a coarse-to-fine generation strategy where each scale conditions on coarser predictions, ensuring coherence. A structure preservation loss enforces learned constraints during training.

**Expected outcomes**: Superior sample quality on scientific time series benchmarks, guaranteed constraint satisfaction, and 40% faster sampling through hierarchical processing. This enables reliable synthetic data generation for data-scarce scientific domains while maintaining physical validity.