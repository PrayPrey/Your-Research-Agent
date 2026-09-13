# Introduction

Can we predict model quality from weights alone—across architectures? Model hubs like HuggingFace host over 10,000 pretrained vision models spanning diverse architectures: ResNets, Vision Transformers (ViT), ConvNeXt, and beyond. Practitioners face a challenging selection problem: evaluating each model requires expensive inference on validation sets. Weight-based quality metrics promise a compute-free alternative, but their cross-architecture validity remains untested.

Prior work established that weight statistics correlate with generalization for convolutional networks. Unterthiner et al. (2020) demonstrated that spectral norms and layer-wise statistics predict ImageNet accuracy within CNN families. Martin and Mahoney (2021) provided theoretical grounding through Heavy-Tailed Self-Regularization (HT-SR) theory, showing that power-law exponents in weight distributions indicate implicit regularization quality. These results suggest a tantalizing possibility: architecture-agnostic weight features that enable unified model selection across diverse model hubs.

However, a critical gap remains. Heavy-tailed theory was validated exclusively on convolutional architectures. Vision Transformers, with their attention mechanisms and fundamentally different parameter structures, may not exhibit the same statistical signatures. Without systematic validation, we cannot recommend weight-based selection for the heterogeneous model populations that define modern hubs.

We address this gap by conducting the first systematic measurement of heavy-tailed exponents on 53 Vision Transformer models from HuggingFace Model Hub. Our experiment reveals a surprising finding: heavy-tailed exponents *can* be computed for ViT attention layers (confirming theoretical applicability), but cross-model variance (σ = 2.868) far exceeds our target threshold (σ < 0.5). The twist: when controlling for model family (google/vit-*), variance drops to σ = 0.24—a 12× reduction. Training provenance, not architecture, dominates the variance.

This finding carries practical implications. Weight-based model selection tools for diverse hubs must account for training origin. Models fine-tuned for task-specific objectives (violence detection, medical imaging) exhibit dramatically different α distributions than general-purpose pretrained models, regardless of architectural similarity.

We make the following contributions:

1. **Extension of HT-SR to Transformers.** We demonstrate that heavy-tailed exponents can be computed for ViT attention weight matrices using the Hill estimator, extending Martin and Mahoney's theoretical framework to attention mechanisms.

2. **Variance decomposition.** We identify training provenance—not architectural variation—as the dominant factor in cross-model α variance, with 12× variance reduction through family stratification.

3. **Practical guidance.** We establish that cross-architecture weight analysis requires family-aware stratification, informing the design of future unified model selection tools.

The remainder of this paper is organized as follows. Section 2 positions our work against prior research on weight-space analysis. Section 3 describes our measurement methodology. Section 4 presents experimental setup, Section 5 reports results, and Section 6 discusses implications. We conclude in Section 7 with directions for future work.
