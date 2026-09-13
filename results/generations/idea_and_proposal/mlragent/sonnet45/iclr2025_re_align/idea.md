# Title
Causal Interventions for Controlled Representational Alignment in Neural Networks

# Motivation
Current representational alignment research primarily focuses on measuring similarity between systems, but lacks systematic frameworks for *controlling* alignment. Understanding how to deliberately increase or decrease alignment between artificial and biological neural systems is crucial for: (1) testing causal hypotheses about what drives alignment, (2) improving AI interpretability by steering models toward human-like representations, and (3) potentially enhancing human-AI collaboration. Existing methods modify architectures or training procedures ad-hoc, without principled intervention strategies.

# Main Idea
Develop a causal intervention framework that systematically manipulates representational alignment through targeted, interpretable mechanisms. The approach involves:

1. **Intervention Operators**: Design differentiable operators that act on intermediate representations (e.g., rotation matrices, selective pruning, contrastive losses) with controllable strength parameters.

2. **Alignment Gradients**: Compute gradients of alignment metrics (CKA, RSA) with respect to intervention parameters, enabling optimization toward target alignment levels with biological systems.

3. **Multi-scale Validation**: Test interventions across layers and modalities, measuring downstream effects on both behavioral alignment (task performance similarity) and value alignment (decision preferences).

4. **Causal Discovery**: Use interventions to identify which representational properties (geometry, dimensionality, sparsity) causally influence alignment versus mere correlation.

Expected outcomes include a toolkit for controlled alignment experiments and insights into computational principles shared between biological and artificial intelligence, directly addressing the workshop's central question of how scientists can intervene on representational alignment.