# Related Work

Our work builds on three research lines: neural functionals, weight-space tokenization, and equivariant architectures. We position our compositional approach as extending prior single-architecture methods to heterogeneous model zoo settings.

## Neural Functionals

**Neural Functional Transformers (NFTs)** [Zhou et al., 2023] demonstrated that attention-based mechanisms could process neural network weights for downstream tasks. Their work showed +17% improvement on INR classification tasks over prior methods, establishing transformers as effective architectures for weight-space learning. However, their validation focused on homogeneous MNIST MLP zoos—collections where all models share the same architecture family. Our work extends this foundation to heterogeneous zoos containing CNNs, Transformers, and MLPs through compositional tokenization.

**Universal Neural Functionals** [Zhou et al., 2024] provided a theoretical framework for automatically constructing permutation-equivariant models for arbitrary neural network architectures. Their algorithm handles complex architectural features like recurrence and residual connections. While this work laid important theoretical groundwork, it lacked large-scale empirical validation on heterogeneous model populations. We provide empirical validation of architecture-agnostic weight encoding at 150-model proof-of-concept scale.

**Permutation Equivariant Neural Functionals** [Zhou et al., 2023] established the foundational framework for handling permutation symmetries in neural network weights through NF-Layers with parameter sharing. Their work demonstrated success on generalization prediction, winning ticket masks, and INR classification/editing. Our compositional design builds on these principles while addressing heterogeneous architecture challenges.

## Weight-Space Tokenization

**SANE** [Schürholt et al., 2024] introduced sequential weight chunking with transformer backbones, demonstrating that scalable weight-space learning was achievable through task-agnostic representations. Their approach processed weight subsets sequentially, enabling embedding of larger neural networks. However, SANE used generic sequential chunking without explicit architecture-specific handling. In contrast, our architecture-specific tokenizers (CNN kernels vs Q/K/V matrices vs MLP weights) preserve family-specific signals in the shared token space.

The **NWS dataset** [Eilertsen et al., 2020] provided 320K weight snapshots from 16K trained DNNs, establishing weight space as a viable high-dimensional research domain. This foundational work demonstrated that meta-classifiers could predict training properties from weights. Our work extends this direction to cross-architecture settings.

## Equivariant Weight Processing

**DWSNets** pioneered permutation-equivariant weight processing for deep learning models. While conceptually important, DWSNets impose CNN-specific architecture assumptions that cause runtime failures on fully-connected MLP and Transformer weights. Our compositional tokenization approach avoids this architecture lock-in by handling CNN, Transformer, and MLP weights through specialized preprocessors followed by a shared architecture-agnostic backbone.

**Graph Neural Networks for Neural Network Weights** [Kofinas et al., 2024] proposed representing neural networks as computational graphs, enabling a single GNN model to encode diverse architectures. Their approach outperformed state-of-the-art on INR classification, editing, and generalization prediction. While GNN-based approaches provide an alternative architecture-aware solution, we demonstrate that attention-based NFT processing combined with architecture-specific tokenization offers a simpler compositional design that achieves comparable mechanism validation.

## Model Zoo Resources

The **ViT Model Zoo** [Falk et al., 2025] provided the first systematic collection of 250 unique Vision Transformer models with diverse generating factors, extending model population methods from small models to SOTA architectures. This resource enables research at scales beyond synthetic model populations. Our work leverages such resources alongside existing CNN (torchvision) and MLP collections to validate heterogeneous weight encoding.

## Our Position

Prior work established that (1) attention mechanisms are effective for weight-space learning [Zhou et al., 2023], (2) tokenization strategies enable scalability [Schürholt et al., 2024], and (3) architecture-specific processing captures important structural information [Kofinas et al., 2024]. However, no prior work empirically validated cross-architecture weight encoding on heterogeneous model zoos mixing CNNs, Transformers, and MLPs.

We demonstrate that compositional hybrid design—architecture-specific tokenization followed by shared NFT processing—preserves per-family quality signals (ρ ≥ 0.68) while enabling cross-architecture learning. This approach avoids the library lock-in limitations of architecture-specific methods like DWSNets while maintaining the structural awareness that generic sequential tokenization lacks.
