# Research Idea

## Title
Linear-PCCP: Physics-Constrained Conformal Prediction via Linear Manifold Projection for Rigorous Uncertainty Quantification

## Motivation
Physics-informed neural networks (PINNs) lack rigorous uncertainty quantification, limiting their deployment in safety-critical applications. Existing conformal prediction methods for PINNs treat physics constraints as soft regularization, allowing predictions that violate fundamental conservation laws. This creates a critical gap: how can we achieve distribution-free coverage guarantees while ensuring zero physics violations? This is essential for domains like fluid dynamics and materials science where violating mass or momentum conservation renders predictions physically meaningless.

## Main Idea
We propose Linear-PCCP, which projects conformal prediction sets onto linear physics constraint manifolds (Ax=b) derived from conservation laws. The key insight is that projection onto linear subspaces preserves the exchangeability property required for conformal coverage guarantees while restricting predictions to physically valid regions.

**Methodology:** (1) Compute physics-aware nonconformity scores combining prediction error and constraint violation; (2) Project prediction sets using P = I - A'(AA')⁻¹A; (3) Calibrate coverage quantiles on projected sets.

**Expected Outcomes:** Achieve target coverage rates (e.g., 95%) with exactly zero physics violations, compared to soft-constraint baselines that permit violations. We will validate on Burgers, Navier-Stokes, and heat equations.

**Impact:** Enables trustworthy PINN deployment in safety-critical physical simulations by providing the first hard-constraint uncertainty quantification framework with formal coverage guarantees.