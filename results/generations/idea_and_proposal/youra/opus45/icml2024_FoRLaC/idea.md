## Title
Verified Neural Contraction Metrics for Provable Regret Bounds in Nonlinear Adaptive Control

## Motivation
Reinforcement learning has achieved remarkable empirical success, yet lacks theoretical guarantees critical for high-stakes applications like autonomous systems and industrial automation. Control theory provides stability guarantees but struggles with unknown nonlinear dynamics. A fundamental gap exists: no framework currently delivers finite-time regret bounds for adaptive control of nonlinear systems with formal verification. This research bridges RL and control theory by leveraging contraction theory—which guarantees trajectory convergence—combined with neural network verification to provide the missing theoretical foundation.

## Main Idea
We propose jointly learning a neural contraction metric M_φ(x) and controller π_θ(x), then verifying the contraction rate ρ using α,β-CROWN neural network verification. The core mechanism: verified contraction rate ρ∈(0,1) guarantees trajectory perturbations decay as ρ^t, enabling rigorous perturbation analysis that connects parameter estimation errors to cumulative regret. This yields provable bounds R(T)≤O(√T·poly(1/(1-ρ),d)) for incrementally stabilizable systems with dimension d≤10.

Key methodology: (1) train neural metric/controller with contraction regularization, (2) verify contraction via α,β-CROWN, (3) derive regret bounds from trajectory sensitivity analysis. We predict √T regret scaling (log-log slope ≤0.55) and polynomial dependence on 1/(1-ρ). This provides the first verified regret guarantees for nonlinear adaptive control, enabling trustworthy deployment in safety-critical applications.