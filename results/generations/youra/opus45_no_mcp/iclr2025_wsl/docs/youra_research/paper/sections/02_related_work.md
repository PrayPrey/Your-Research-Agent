# Related Work

## Weight Space Learning

Neural network weights exist in high-dimensional spaces with rich geometric structure. Linear mode connectivity demonstrates that trained networks can be connected via low-loss paths in weight space, suggesting meaningful structure beyond random initialization. This motivates learning representations that capture weight space semantics.

**Hyper-Representations** train variational autoencoders on collections of neural network weights, demonstrating that latent spaces capture training dynamics and model relationships. However, evaluation focused on weight generation rather than property prediction, and comparisons used different datasets and metrics across papers.

**Statistical approaches** (StatNN and variants) compute simple statistics (mean, variance) over weights for property prediction. While computationally efficient, these methods ignore network structure entirely, treating all parameters as an unordered bag.

## Permutation Symmetries in Weight Space

Neural networks exhibit permutation symmetries: reordering hidden neurons with corresponding weight adjustments preserves function. This symmetry complicates weight space learning—functionally identical networks may have distant representations.

**Git Re-Basin** addresses this through weight alignment, finding permutations that minimize distance between networks. Originally developed for model merging, alignment could preprocess weights before embedding. The computational cost scales quadratically with model count, creating challenges at scale.

**Neural Functional Transformers (NFN)** take an architectural approach, designing layers that are permutation-equivariant by construction. This avoids alignment preprocessing but requires specialized architectures. NFN achieves strong results on weight processing tasks but has not been systematically compared to simpler alternatives for property prediction.

## Model Zoos and Benchmarks

Large collections of pretrained models with metadata enable systematic evaluation. **Model Zoos** provide thousands of checkpoints with ground-truth accuracy labels, establishing infrastructure for weight embedding benchmarks. However, existing evaluations compare methods on different zoo subsets with incompatible protocols.

**Task Arithmetic** demonstrates that weight differences (task vectors) encode semantic information enabling model editing. This validates that weight spaces contain property-relevant structure worth embedding.

## Gap in Existing Work

Prior work evaluates embedding methods in isolation on different datasets with different metrics. We cannot determine:
- Whether structural biases (layer-awareness, alignment, equivariance) provide measurable benefit
- Which structural biases matter most for property prediction
- Whether complex approaches (NFN, GRB) justify their overhead versus simpler alternatives

This paper provides the missing systematic comparison through a controlled ablation study.
