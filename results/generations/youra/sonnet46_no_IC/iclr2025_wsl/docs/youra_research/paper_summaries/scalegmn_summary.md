# Scale Equivariant Graph Metanetworks

## Key Metadata
- **Authors:** Kalogeropoulos et al.
- **Year:** 2024
- **Venue:** NeurIPS 2024 (Oral)
- **Core Contribution:** First weight-space architecture equivariant to both permutation and scaling symmetries via graph metanetworks.

## Section Summaries

### Abstract
Neural networks exhibit two fundamental symmetries in weight space: permutation symmetry (neurons can be reordered without changing network function) and scaling symmetry (incoming and outgoing weights of a neuron can be scaled inversely). Existing methods handle permutation equivariance but ignore scaling. We propose Scale Equivariant Graph Metanetworks (ScaleGMN), which processes neural network weights as graphs and enforces equivariance to the full monomial matrix group (permutation × sign changes, extended to positive scaling). ScaleGMN achieves state-of-the-art results on property prediction and generalization tasks.

### Introduction & Motivation
Weight-space methods must handle two symmetry groups simultaneously to be theoretically grounded. Prior work (NFN, NFT, neural-graphs) addresses permutation but ignores scaling. Scaling symmetry matters for ReLU networks: scaling a neuron's incoming weights by α and outgoing by 1/α preserves function but changes weight magnitudes significantly. Ignoring scaling means the representation space is unnecessarily large and the learned representations conflate genuinely different networks with functionally identical ones.

### Methodology
ScaleGMN represents neural networks as bipartite graphs where nodes are neurons and edges are weights. The key insight is that the symmetry group of an MLP is the monomial matrix group M_n = S_n ⋉ D_n, where S_n is the permutation group and D_n is the group of positive diagonal matrices (scaling). For equivariance: a layer σ: W → W' is equivariant to the monomial group if σ(g·w) = g'·σ(w) for all g in M_n. The architecture uses message-passing on the weight graph with special attention to node features representing pre-activation scaling factors. Key innovation: the normalization of node features is done in a scale-equivariant manner using layer-wise weight norms. Training uses standard cross-entropy or regression losses on property labels — no SSL objective. The model is evaluated on MLP weight zoos constructed from training diverse small MLPs on MNIST/CIFAR variants.

### Experiments & Results
Datasets: model zoo with ~10,000 MLPs (3-5 layer, width 16-64) trained on MNIST, FashionMNIST, CIFAR-10 variants. Tasks: accuracy prediction (R² score), generalization gap prediction. Baselines: NFN (Navon 2023), neural-graphs (Kofinas 2024), plain GNN on flattened weights. Results: ScaleGMN achieves R²=0.91 on accuracy prediction vs NFN R²=0.84, neural-graphs R²=0.88. On cross-architecture generalization (train on 3-layer, test on 5-layer MLPs): ScaleGMN R²=0.79 vs NFN R²=0.61. Ablation: removing scale equivariance drops accuracy prediction by 8-12 R² points.

### Discussion & Conclusion
ScaleGMN demonstrates that enforcing scale equivariance is empirically beneficial, not just theoretically motivated. Key limitation: evaluated only on supervised property prediction with ground-truth labels. Future work: extending to SSL/unsupervised objectives and larger architectures like CNNs and Transformers.

## Key Contributions
- First formalization of monomial matrix group equivariance for weight-space processing
- ScaleGMN architecture: scale+permutation equivariant graph metanetwork
- State-of-the-art on property prediction with superior cross-architecture generalization

## Potential Relevance
ScaleGMN's equivariant encoder is the ideal backbone for a unified SSL framework — it handles both symmetries correctly but lacks an SSL training objective. Pairing ScaleGMN's encoder with SANE-style contrastive or masked modeling objectives is the direct path to Gap 1's missing piece. The bipartite graph representation makes it naturally compatible with heterogeneous architecture processing.
