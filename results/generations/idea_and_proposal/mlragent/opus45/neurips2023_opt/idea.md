# Title: Learning Rate Transfer via Loss Landscape Curvature Scaling Laws

## Motivation
Training large language models requires extensive hyperparameter tuning, particularly for learning rates, which is prohibitively expensive at scale. Current practice involves costly grid searches for each model size. If we could predict optimal learning rates for large models based on experiments with smaller ones, we could save millions of dollars in compute and significantly reduce the environmental impact of AI development. While existing scaling laws focus on loss prediction, the relationship between model scale and optimal optimization hyperparameters remains poorly understood.

## Main Idea
We propose to derive learning rate transfer rules by studying how loss landscape curvature (Hessian spectral properties) scales with model size. Our methodology involves:

1. **Empirical characterization**: Systematically measure the Hessian's maximum eigenvalue, trace, and spectral density across model sizes (from millions to billions of parameters) during training trajectories.

2. **Scaling law derivation**: Fit power-law relationships between model dimensions (width, depth, parameters) and curvature statistics, accounting for training dynamics.

3. **Transfer rule construction**: Using the curvature scaling laws, derive analytical formulas for transferring learning rates: if optimal LR for small model relates to curvature as η* ∝ 1/λ_max, and λ_max scales predictably with size, we obtain direct transfer rules.

**Expected outcomes**: Practical formulas enabling researchers to tune hyperparameters on small proxies and reliably transfer to target scales, validated on transformer architectures across 10x-1000x scale jumps.