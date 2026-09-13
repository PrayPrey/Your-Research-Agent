# Title
Gradient-Informed Adaptive Proposals for Discrete Sampling via Local Continuous Relaxations

# Motivation
Current discrete sampling methods face a fundamental trade-off: gradient-based MCMC methods struggle with the non-smoothness of discrete spaces, while embedding methods lose fidelity when mapping back to discrete space. This is particularly problematic for black-box objectives and problems with long-range correlations in language models. We need methods that can leverage gradient information effectively while respecting the discrete nature of the space.

# Main Idea
We propose a hybrid approach that constructs **local continuous relaxations** around the current discrete state, uses gradient information to identify promising directions in this relaxed space, then designs adaptive discrete proposals based on these directions. Specifically:

1. **Local Smoothing**: At each discrete state, create a localized continuous relaxation using learned kernels that preserve the problem's correlation structure.

2. **Gradient-Guided Direction Finding**: Compute gradients in the relaxed space and use them to identify a low-dimensional manifold of promising moves.

3. **Adaptive Discrete Proposals**: Design discrete proposal distributions that favor moves aligned with gradient directions, with proposal complexity adapted to the local landscape smoothness.

4. **Meta-Learning Relaxation**: Learn the relaxation kernel parameters across problem instances to capture domain-specific structures (e.g., syntax in language models).

**Expected Outcomes**: Improved sampling efficiency on black-box objectives and better handling of long-range correlations, with applications to constrained text generation and protein design.