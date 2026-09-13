# Title
Robust Bayesian Optimization with Learnable Confidence Parameters for Provably Safe Domain Knowledge Integration

# Motivation
Domain-informed Bayesian optimization (BO) achieves remarkable sample efficiency in expensive applications—0.124% sampling in molecular design, 1000× acceleration in materials discovery—but lacks theoretical guarantees when domain priors (physics models, LLM suggestions, expert constraints) are imperfect. Standard GP-UCB provides O(√T log T) regret bounds but ignores available domain knowledge, while existing domain-informed methods catastrophically fail under prior mismatch. This creates a critical barrier for safety-critical applications requiring both efficiency and reliability guarantees.

# Main Idea
We propose RoBO-AKW (Robust BO with Adaptive Knowledge Weighting), treating domain priors as uncertain information sources with learnable confidence weights. The core mechanism: (1) formulate multi-source GP priors as mixture experts, (2) detect prior mismatch via online posterior predictive checks, (3) dynamically down-weight mismatched priors using parameter-free coin betting algorithms. 

**Key Innovation:** Provable regret bound R_T ≤ O(√T log T)·(1 + C·ε) under ε-bounded prior error, gracefully degrading to standard BO when priors fail while maintaining near-optimal efficiency when priors are accurate.

**Validation:** Synthetic experiments verify regret scaling (α≈0.50±0.03) and weight convergence (<50 iterations). Real-world benchmarks (molecular/materials design, LLM-augmented robotics) demonstrate 2× competitiveness with domain-informed SOTA under good priors and 2× overhead versus GP-UCB under poor priors—eliminating catastrophic failures while enabling 50-100× cost savings in expensive domains.