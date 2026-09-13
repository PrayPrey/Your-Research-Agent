# Title: Hierarchical Latent Diffusion for Discrete Optimization with Long-Range Dependencies

## Motivation
Current discrete sampling and optimization methods struggle with long-range, high-order correlations prevalent in modern language models and protein sequences. Gradient-based discrete MCMC methods often get trapped in local modes, while embedding approaches fail to capture complex discrete structures faithfully. GFlowNets require extensive training and struggle with black-box objectives. There is a critical need for methods that can efficiently navigate discrete spaces while respecting long-range dependencies without requiring differentiable objectives.

## Main Idea
I propose a hierarchical latent diffusion framework that operates across multiple abstraction levels of discrete structures. The key insight is to learn a hierarchy of coarse-to-fine discrete representations, where higher levels capture long-range correlations and lower levels refine local details.

**Methodology:**
1. Train a discrete variational autoencoder with multiple latent hierarchy levels, where each level represents progressively coarser structure
2. Perform diffusion-based sampling in the learned hierarchical latent space, starting from coarse levels (capturing global structure) and progressively refining to fine levels
3. Use a surrogate model trained on sparse evaluations for black-box objectives, enabling gradient-guided transitions between hierarchy levels

**Expected Outcomes:**
- 3-5x faster convergence on combinatorial optimization benchmarks (TSP, MaxSAT)
- Improved sample diversity in constrained text generation
- Effective handling of black-box protein fitness landscapes

**Impact:** This bridges continuous diffusion's efficiency with discrete structure preservation, enabling practical optimization in high-dimensional discrete spaces with complex dependencies.