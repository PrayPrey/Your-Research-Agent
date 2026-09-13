# Title: Scale-Adaptive Learning Rates via Loss Landscape Curvature Transfer

## Motivation
Training large language models requires extensive hyperparameter tuning, with learning rate being the most critical yet expensive to optimize. Current practice involves costly grid searches at full scale or unreliable heuristics when transferring from smaller models. A principled method to predict optimal learning rates for large models based on small-scale experiments would dramatically reduce computational costs and environmental impact. The key insight is that loss landscape geometry exhibits predictable scaling patterns that can be exploited for hyperparameter transfer.

## Main Idea
We propose learning a **curvature-based scaling function** that maps optimal learning rates across model sizes. Our methodology:

1. **Curvature Profiling**: For a sequence of small models (e.g., 10M-500M parameters), measure local Hessian spectral properties (top eigenvalue, trace, effective rank) at initialization and during early training.

2. **Scaling Law Derivation**: Fit power-law relationships between model size, curvature statistics, and empirically optimal learning rates, discovering size-dependent correction factors.

3. **Transfer Protocol**: Given a target large model, compute its curvature profile cheaply (via Hutchinson estimator) and apply the learned scaling function to predict the optimal learning rate.

**Expected Outcomes**: Accurate learning rate prediction (within 10% of grid-search optimal) for billion-parameter models using only million-parameter experiments, achieving 100x+ reduction in tuning compute. This bridges classical optimization theory (curvature-based step sizes) with modern scaling law research.