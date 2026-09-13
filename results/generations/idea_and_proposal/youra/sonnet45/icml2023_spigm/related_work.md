## Related Work

**Related Papers**

1. **Title**: Neural Discrete Representation Learning (VQ-VAE) (SS ID: f466157848d1a7772fb6d02cdac9a7a5e7ef982e)
   - **Authors**: van den Oord et al.
   - **Summary**: Introduced Vector-Quantized Variational Autoencoder using discrete codebooks for representation learning, demonstrating discrete codes avoid posterior collapse and learn hierarchical patterns across images, audio, and video domains.
   - **Year**: 2017

2. **Title**: Generating Diverse High-Fidelity Images with VQ-VAE-2 (SS ID: 6be216d93421bf19c1659e7721241ae73d483baf)
   - **Authors**: Razavi et al.
   - **Summary**: Extended VQ-VAE with hierarchical spatial organization to achieve high-fidelity image generation competitive with GANs on ImageNet, demonstrating discrete codes scale to complex generation tasks.
   - **Year**: 2019

3. **Title**: Learning Transferable Visual Models From Natural Language Supervision (CLIP)
   - **Authors**: Radford et al.
   - **Summary**: Unified vision-language representation learning via contrastive learning on continuous embeddings, enabling zero-shot transfer across modalities and demonstrating cross-modal alignment effectiveness.
   - **Year**: 2021

4. **Title**: Neural Methods for Amortized Inference (SS ID: 756c95fbde7f205513d68f31ead0a459e3e63d31)
   - **Authors**: Zammit-Mangion et al.
   - **Summary**: Reviews amortized inference scaling via neural networks, introducing orthogonal transformations for structured variational noise in neural network-based inference methods.
   - **Year**: 2024

5. **Title**: Conformalized-DeepONet (SS ID: 23f075d22eac4836c46839f9fa6b3f723d0fb6e2)
   - **Authors**: Moya et al.
   - **Summary**: Applied conformal prediction to continuous neural operators, demonstrating distribution-free coverage guarantees for uncertainty quantification in neural operator models.
   - **Year**: 2024

6. **Title**: Structured Dropout Variational Inference for Bayesian Neural Networks (SS ID: 8dd77a23c65a4452ffd9e12167b4106bad3d6ff7)
   - **Authors**: Nguyen et al.
   - **Summary**: Addresses structured variational inference via orthogonal transformations, providing alternative approach to discrete latent codes through continuous structured posterior.
   - **Year**: 2021

7. **Title**: How do Probabilistic Graphical Models and Graph Neural Networks Look at Network Data? (SS ID: 847de2cee2803b25894c6a10f83400561acc6baa)
   - **Authors**: Lapenna & D. Bacco
   - **Summary**: Compared PGMs and GNNs for network data analysis, finding PGMs outperform GNNs with low-dimensional/noisy features while GNNs excel with high-quality high-dimensional features.
   - **Year**: 2025

8. **Title**: Sum-Product-Set Networks: Deep Tractable Models for Tree-Structured Graphs (SS ID: 4761f446eb1020a1c9de2471d3653c7d022c3a61)
   - **Authors**: Papez et al.
   - **Summary**: Developed probabilistic circuits for exact inference on tree-structured graphs (XML, JSON trees), providing alternative probabilistic approach for structured data.
   - **Year**: 2024

9. **Title**: Cross-Domain Integration for General Sensor Data Synthesis (SS ID: a84da5fa6720df1e3e1833f9fb93d14efdfa9da9)
   - **Authors**: Zhou et al.
   - **Summary**: Proposed LLM-based approach that interprets tasks and delegates to domain-specific generative models for multi-modal sensor data synthesis without unified latent space.
   - **Year**: 2024

10. **Title**: A Comprehensive Survey on Graph Neural Networks (SS ID: 81a4fd3004df0eb05d6c1cef96ad33d5407820df)
    - **Authors**: Wu et al.
    - **Summary**: Comprehensive survey establishing GNN taxonomy and design space (GCN, GAT, GraphSAGE) for graph representation learning and molecular property prediction.
    - **Year**: 2019

11. **Title**: Deep Generative Modelling: A Comparative Review (SS ID: bc519f58ae61afbf6318d6e4239d2d565c7ba467)
    - **Authors**: Bond-Taylor et al.
    - **Summary**: Positions VQ-VAE among generative model landscape including VAEs, GANs, Normalizing Flows, and Autoregressive models with comparative analysis.
    - **Year**: 2021

12. **Title**: Evaluating Probabilistic Deep Learning Methods for Uncertainty Quantification (SS ID: f700b36c5db4b6ee52480b84f86810f9efb17647)
    - **Authors**: Lops et al.
    - **Summary**: Compared Deep Ensembles, MC Dropout, and Flipout for uncertainty quantification, finding Deep Ensembles achieve ECE ≈0.35 and MC Dropout ≈0.36.
    - **Year**: 2025

13. **Title**: ProGen: Probabilistic Spatiotemporal Forecasting (SS ID: 5d145cbf3d3d04454f9f869a07135f3085d4628a)
    - **Authors**: Gong et al.
    - **Summary**: Alternative approach for temporal structured data using stochastic differential equations and diffusion models for spatiotemporal forecasting.
    - **Year**: 2024

14. **Title**: PyTorch Geometric
    - **Authors**: Fey & Lenssen
    - **Summary**: Production-ready library for graph neural networks with GPU support, batching, and message passing layers. Implementation foundation for GCN and GAT graph encoders.
    - **Year**: Not specified

15. **Title**: AntixK/PyTorch-VAE
    - **Authors**: AntixK
    - **Summary**: Modular, config-driven PyTorch implementation of various VAE architectures including VQ-VAE baseline implementation for multi-modal extension.
    - **Year**: Not specified

**Key Challenges**

1. **Modality-Specific vs. Cross-Modal Trade-off**: Shared codebooks may under-represent modality-specific nuances (e.g., graph chirality, time series oscillation frequency) if codes are forced to be too generic, creating tension between cross-modal generalization and within-modality specialization.

2. **Codebook Collapse**: Risk of discrete codebooks having low utilization (<50%) where only a small fraction of codes are actively used, particularly when scaling to multiple heterogeneous modalities with different structural characteristics.

3. **Continuous vs. Discrete Latent Spaces**: Existing cross-modal work (CLIP) uses continuous embeddings while VQ-VAE uses discrete codes for single modalities. No prior work combines discrete latent codes with contrastive multi-modal alignment for structured data.

4. **Structured Non-Grid Modalities**: VQ-VAE demonstrated success on grid-structured data (images, audio, video) but not on heterogeneous structured modalities (graphs + time series + text) which have fundamentally different topological properties.

5. **Uncertainty Quantification for Discrete Codes**: Conformal prediction has been applied to continuous neural operators but not to discrete codebook posteriors, requiring adaptation for categorical discrete codes with Gumbel-Softmax relaxation.

6. **Contrastive Learning on Discrete Indices**: Standard contrastive methods (SimCLR, MoCo, CLIP) operate on continuous embeddings. Applying InfoNCE loss to discrete codebook indices introduces optimization challenges.

7. **Multi-Modal Optimization Conflicts**: Joint training on three modalities with different reconstruction losses creates conflicting gradients that may hinder convergence, requiring careful loss weight balancing and potentially staged training protocols.

8. **Cross-Modal Semantic Overlap**: Assumption that molecular graphs, chemical text (SMILES), and binding affinity time series share sufficient semantic structure for meaningful cross-modal codes may not hold if modalities are semantically disjoint.

9. **Scalability to Large Datasets**: While QM9 has 133,885 molecules, scaling to larger datasets like PubChem (100M+ molecules) presents computational challenges for discrete codebook training with contrastive learning.

10. **GNN vs. PGM Architecture Choice**: Recent work shows PGMs outperform GNNs with low-dimensional/noisy features while GNNs excel with high-quality features, requiring careful encoder selection based on molecular feature quality.
