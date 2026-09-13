# Title
**Adaptive Variance Reduction for Learned MCMC Samplers via Meta-Learned Control Variates**

# Motivation
While learned samplers (e.g., neural transport, flow-based MCMC) show promise in accelerating convergence, they often suffer from high variance in practice, making them unreliable for critical applications like Bayesian inference and molecular dynamics. Classical variance reduction techniques (control variates, Rao-Blackwellization) are underutilized in learned samplers because they require problem-specific design. We need adaptive methods that automatically learn variance reduction strategies alongside the sampler itself.

# Main Idea
We propose a meta-learning framework that jointly trains: (1) a neural sampler (e.g., learned transition kernel), and (2) a control variate network that learns optimal variance reduction functions across a distribution of sampling tasks. 

**Methodology:** During meta-training, the control variate network observes samples from various target distributions and learns to predict low-variance estimators by minimizing a combined objective of sampling efficiency and variance. The framework uses bi-level optimization where the inner loop optimizes sampling trajectories and the outer loop optimizes the control variate parameters.

**Expected Outcomes:** Reduced variance in expectation estimates by 2-5× compared to vanilla learned samplers, improved sample efficiency on Bayesian inverse problems and molecular simulation tasks.

**Impact:** This bridges classical variance reduction theory with modern learning-based sampling, providing more reliable learned samplers for scientific computing and enabling deployment in high-stakes applications where uncertainty quantification is critical.