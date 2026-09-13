# Research Idea

## Title
Unifying Diffusion Models and Optimal Control: Score Matching as Hamilton-Jacobi-Bellman Optimality

## Motivation
Diffusion models achieve state-of-the-art generative performance, yet their training objectives (denoising score matching) lack principled theoretical grounding—they work empirically but the *why* remains unclear. Separately, stochastic optimal control theory provides rigorous frameworks for sequential decision-making via Hamilton-Jacobi-Bellman (HJB) equations. A fundamental connection between these fields could explain score matching's effectiveness and enable principled improvements to training algorithms.

## Main Idea
We hypothesize that denoising score matching objectives are mathematically equivalent to HJB optimality conditions when the log-probability density is identified as the negative value function of a stochastic optimal control problem. The causal mechanism operates in three steps: (1) setting V(x,t) = -log p(x,t) maps diffusion to control, (2) the score function ∇log p equals the optimal control signal -∇V, and (3) the HJB residual reduces to the score matching loss.

**Methodology:** We will derive explicit mathematical equivalence for VP-SDE and VE-SDE formulations, validate numerically on tractable distributions (expecting >0.99 correlation between DSM loss and HJB residual), and test whether TD-inspired training modifications improve convergence (targeting 10-20% faster training on CIFAR-10).

**Impact:** This unification provides theoretical justification for score matching and opens pathways for control-theoretic training innovations in generative modeling.