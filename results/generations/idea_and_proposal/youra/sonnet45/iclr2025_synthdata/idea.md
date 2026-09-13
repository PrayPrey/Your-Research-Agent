# Title
Adaptive Data Portfolio Optimization: Dynamic Synthetic-Natural Data Mixing via Portfolio Theory

# Motivation
Synthetic data promises to address privacy, cost, and access barriers in machine learning, but practitioners face a critical question: *how much* synthetic versus natural data should be used? Current approaches rely on fixed mixing ratios throughout training, ignoring that optimal proportions may vary across training phases and depend on data quality, privacy budgets, and cost constraints. This creates a gap between synthetic data's potential and its practical deployment, particularly when multiple synthetic generators with different quality-risk profiles are available.

# Main Idea
We propose Adaptive Data Portfolio Optimization (ADPO), which frames synthetic-natural data mixing as a dynamic portfolio optimization problem. Each data source is treated as an "asset" with quality-risk profiles measured via empirically validated metrics (SDMetrics). Every K epochs, ADPO solves a quadratic programming problem to maximize expected performance while minimizing variance, subject to privacy (ε-differential privacy) and cost constraints. Damped weight updates prevent training instability. 

**Core hypothesis**: ADPO achieves ≥2% accuracy improvement over best fixed ratios by discovering curriculum learning patterns—higher synthetic data early in training, transitioning to natural data later. We test this across 5 datasets with 8 baselines, predicting quality metrics correlate with performance (r≥0.5) and ADPO reaches convergence 20% faster. This provides practitioners a principled, constraint-aware answer to optimal data mixing.