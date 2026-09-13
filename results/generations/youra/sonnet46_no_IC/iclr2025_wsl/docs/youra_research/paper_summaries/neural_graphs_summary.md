# Graph Neural Networks for Equivariant Representations of Neural Networks

## Key Metadata
- **Authors:** Kofinas et al.
- **Year:** 2024
- **Venue:** ICLR 2024 (Oral)
- **Core Contribution:** Treat neural networks as computational graphs and apply GNNs to obtain permutation-equivariant representations across diverse architectures.

## Section Summaries

### Abstract
We propose treating neural networks as computational graphs — where nodes are neurons and edges are weight connections — and applying graph neural networks (GNNs) to process them. This yields permutation-equivariant representations that naturally generalize across architectures (MLPs, CNNs, transformers). A single GNN model, trained on one architecture family, transfers to held-out architectures without retraining. We demonstrate this on property prediction, model editing, and INR processing tasks.

### Introduction & Motivation
Previous weight-space methods (NFN, NFT) are architecture-specific: they define equivariant layers for specific weight tensor shapes and require respecification for each architecture. This limits scalability. The key insight: any feedforward neural network can be represented as a directed computational graph with a standardized node/edge schema. A GNN operating on this graph automatically handles varying architectures through the same message-passing mechanism.

### Methodology
Graph construction: each neuron becomes a node with features (bias, activation type). Each weight w_{ij} becomes a directed edge with scalar weight feature. For CNNs: convolutional filters become sets of edges with shared weights; spatial structure is encoded via position features. For transformers: attention heads are represented as subgraph clusters. Message passing: standard MPNN layers with equivariant node/edge update functions. Key: the message-passing is permutation-equivariant by construction — permuting neuron ordering produces permuted output features. No scale equivariance. Training: supervised on property prediction (accuracy, generalization, class) with labeled zoo checkpoints. Cross-architecture generalization: train on MLP zoos, test on CNN zoo (different task, different architecture).

### Experiments & Results
Tasks: accuracy prediction (R²), generalization gap (R²), class prediction (AUC), INR attribute prediction. Datasets: MLP zoo (10k models), CNN zoo (5k models), NeRF zoo (2k NeRF networks). Cross-architecture: train on MLP zoo → evaluate on CNN zoo without retraining (zero-shot transfer). R² accuracy prediction: MLP→MLP: 0.90, MLP→CNN zero-shot: 0.71, vs architecture-specific baseline 0.59. Ablation: removing graph structure (using flat GNN) drops cross-arch performance by 15%. Compute: single NVIDIA A100, ~6 hours training, 40M parameters.

### Discussion & Conclusion
Neural-graphs demonstrate that computational graph representation enables architecture-agnostic processing. Key limitation: supervised setting only — requires labeled model zoos. Scale equivariance is not addressed. Future work: SSL pre-training on unlabeled zoo, scaling to Transformer-weight processing.

## Key Contributions
- Standardized computational graph representation for any feedforward architecture
- Zero-shot cross-architecture transfer in supervised property prediction
- Multi-task evaluation across property prediction, editing, and INR tasks

## Potential Relevance
Neural-graphs' computational graph representation is directly usable as the backbone for an SSL training regime. The zero-shot cross-architecture transfer in supervised setting is strong evidence that the graph representation captures architecture-agnostic structure. Gap 1's SSL extension would test whether this transfers without supervision, using the same held-out evaluation protocol.
