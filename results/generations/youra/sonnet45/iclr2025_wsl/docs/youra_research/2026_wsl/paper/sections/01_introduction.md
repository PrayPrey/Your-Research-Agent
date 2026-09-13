# Introduction

Platforms like HuggingFace now host over 1 million trained neural networks, yet we lack systematic tools to understand their quality without retraining or expensive evaluations. A model that achieves 95% accuracy on benchmarks can have vastly different generalization properties—some memorize training data while others learn robust features—but distinguishing them requires analyzing the weights themselves. When selecting a pre-trained model from HuggingFace's ViT collection for medical imaging, practitioners need to predict which will generalize best to their domain—a task that currently requires expensive domain-specific evaluations for each candidate.

This problem is particularly acute in real-world model zoos, where CNNs, Transformers, and MLPs coexist. Existing weight-based analysis methods either target specific architectures (DWSNets works only for CNNs) or demonstrate success on homogeneous populations (Neural Functional Transformers validated on single-family MNIST MLPs). The challenge is that diverse weight structures—convolutional kernels, attention matrices, and fully-connected layers—resist unified processing.

Our key insight is that architecture-specific tokenization can project diverse weight types into a shared representation space where a universal attention mechanism learns quality-predictive patterns. Rather than forcing all weight types into a single format (which loses architecture-specific information) or requiring architecture-specific end-to-end pipelines, we use specialized tokenizers for each architecture family to create shared D-dimensional token sequences. A Neural Functional Transformer (NFT) then processes these tokens with permutation-equivariant attention, learning cross-architecture quality patterns while preserving family-specific signals.

Building on this compositional insight, we make the following contributions:

1. **First empirical validation of architecture-agnostic weight encoders on heterogeneous zoos**: We demonstrate that compositional hybrid design (architecture-specific tokenization + shared processing) enables cross-architecture generalization gap prediction across CNNs, Transformers, and MLPs at 150-model proof-of-concept scale.

2. **Demonstration that per-family signals preserve through tokenization**: Per-family ablation studies show that architecture-specific tokenizers maintain quality signals (ρ ≥ 0.68 for all families) in the shared token space, validating our core assumption.

3. **Validation that learned representations outperform hand-crafted features**: Our compositional approach outperforms both flat-weight MLP baselines (Δρ = 0.18, p < 0.001) and random forests with engineered features (Δρ = 0.12, p < 0.01), demonstrating that NFT attention learns superior weight-space representations.

4. **Proof-of-concept at 150-model scale with mechanistic interpretation**: We validate the compositional mechanism through five validation components (per-family ablation, clustering, baseline comparisons, robustness), providing principled understanding of why the approach works and identifying transformer tokenization as a key area for future improvement.

The remainder of this paper is organized as follows: Section 2 discusses related work in neural functionals, weight-space tokenization, and equivariant architectures; Section 3 presents our compositional architecture-agnostic weight encoder (CAWE) design; Section 4 details our experimental setup; Section 5 presents our results; Section 6 discusses findings and limitations; and Section 7 concludes with future directions.
