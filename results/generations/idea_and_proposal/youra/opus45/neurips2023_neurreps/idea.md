# Research Idea

## Title
Attractor-Equivariant Layers: Inducing Geometric Symmetries via Soft Topological Constraints on Neural Manifolds

## Motivation
Biological neural circuits (e.g., head direction cells, grid cells) naturally encode symmetries through attractor dynamics on manifolds matching task geometry. Meanwhile, geometric deep learning achieves equivariance through hard architectural constraints, sacrificing flexibility and biological plausibility. A critical gap exists: can soft, learnable constraints on network dynamics induce equivariant representations while maintaining trainability? Bridging this gap would unify neuroscience findings with deep learning principles and enable more interpretable, biologically-grounded equivariant architectures.

## Main Idea
We hypothesize that constraining recurrent neural network dynamics to specific manifold topologies (ring, torus, sphere) via differentiable topological loss terms induces equivariant representations when the manifold is isomorphic to the task's symmetry group. The mechanism: activity bump position encodes group elements, and bump translation implements group actions.

**Methodology:** Train Attractor-Equivariant Layers (AELs) with soft topological regularization (persistent homology-based loss). Measure equivariance error via Lie derivatives, validate manifold emergence through Betti numbers, and compare against e3nn baselines on RotMNIST.

**Predictions:** AELs achieve equivariance error <0.1; removing topological constraints increases error >50%; task accuracy remains within 2% of hard-constraint methods.

**Impact:** Establishes substrate-agnostic principles linking attractor dynamics to equivariance, enabling interpretable geometric representations bridging neuroscience and machine learning.