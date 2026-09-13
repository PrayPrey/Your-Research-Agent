# Research Idea

## Title
Symmetry-Aware Variational Autoencoders for Neural Network Weight Generation

## Motivation
Generating high-quality neural network weights for specific tasks could revolutionize transfer learning and model initialization. However, current weight generation methods struggle with the inherent symmetries in weight spaces—permutation invariance of neurons and scaling symmetries between layers create redundant representations that confuse generative models. This leads to poor sample quality and wasted capacity learning equivalent weight configurations. Addressing these symmetries is crucial for practical weight synthesis.

## Main Idea
We propose **SymVAE**, a variational autoencoder that operates on canonicalized weight representations to handle weight space symmetries. Our approach consists of three components:

1. **Canonicalization Module**: Before encoding, we apply a learned canonicalization network that maps weights to a canonical form, resolving permutation and scaling ambiguities using optimal transport-based neuron alignment.

2. **Equivariant Encoder-Decoder**: The encoder uses graph neural networks treating weights as bipartite graphs between layers, producing symmetry-invariant latent codes. The decoder generates weights conditioned on task descriptors.

3. **Hierarchical Latent Space**: We structure latents to separately capture architecture-agnostic task knowledge and architecture-specific weight patterns.

**Expected Outcomes**: Improved weight generation quality, better interpolation in weight space, and efficient task-conditioned model synthesis. We will evaluate on INR generation and few-shot model adaptation benchmarks. This work could enable "model synthesis on demand," significantly reducing training costs for new tasks.