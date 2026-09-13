# Title
Physics-Residual-Guided Adaptive Conformal Prediction for Robust Uncertainty Quantification in Physics-Informed Neural Networks

# Motivation
Physics-informed neural networks (PINNs) are increasingly deployed in safety-critical applications, yet they struggle with reliable uncertainty quantification under distribution shift. Standard conformal prediction provides valid coverage guarantees but produces overly conservative intervals. Existing adaptive methods require expensive Bayesian inference, causal modeling, or high-dimensional density estimation. This creates a critical gap: practitioners need uncertainty quantification that is simultaneously valid, efficient, computationally tractable, and prior-free for real-world PINN deployment in engineering, climate modeling, and medical applications.

# Main Idea
We propose using PDE residuals—the degree to which a PINN violates governing equations—as similarity metrics to adaptively weight conformal prediction. The core mechanism: distribution shift causes elevated residuals in under-sampled regions, which correlate with prediction errors (ρ > 0.6). By reweighting calibration samples via kernel functions of residual similarity K(r_test, r_cal), we adapt conformal quantiles to local error regimes without requiring priors or causal models.

We test this across five PDEs (Burgers, heat, Allen-Cahn, cylinder flow) under three shift severities, comparing against seven baselines. Expected outcomes: maintain valid coverage (≥85%) while achieving 20-40% tighter intervals than standard conformal prediction, with only 10% computational overhead. This bridges the gap between conservative standard methods and expensive Bayesian approaches, enabling trustworthy PINN deployment.