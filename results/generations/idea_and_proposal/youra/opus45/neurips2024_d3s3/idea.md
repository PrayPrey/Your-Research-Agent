# Research Idea

## Title
Gradient-Guided Predictive Coding Networks for Sample-Efficient Simulation-Based Inference

## Motivation
Simulation-based inference (SBI) enables scientific discovery but requires thousands of expensive simulations to estimate posterior distributions. While differentiable simulators provide gradient information (∂x/∂θ) and Predictive Coding Networks (PCNs) offer biologically-inspired hierarchical inference, no existing method combines these complementary strengths. Current approaches either use gradients only during training (missing inference-time benefits) or ignore available gradient information entirely. This gap limits sample efficiency in domains where simulations are computationally expensive, such as physics modeling and molecular design.

## Main Idea
We propose Gradient-Guided Predictive Coding (G2PC), which injects differentiable simulator gradients as layer-wise error signals within a PCN architecture for posterior estimation. The core mechanism operates through four steps: (1) compute simulator gradients via autodiff, (2) transform gradients into prediction errors at each PCN layer, (3) perform local parameter updates through ODE-based settling dynamics, and (4) refine posteriors hierarchically. This constrains the posterior landscape through local error minimization at each layer.

We will evaluate G2PC against NPE baselines on standard SBI benchmarks (Two Moons, SLCP, Lotka-Volterra), measuring simulations required to achieve target accuracy (C2ST < 0.55). We predict >50% reduction in simulation budget compared to standard NPE, validated through ablations on settling iterations and hierarchical depth. Success would enable practical SBI in simulation-constrained scientific domains.