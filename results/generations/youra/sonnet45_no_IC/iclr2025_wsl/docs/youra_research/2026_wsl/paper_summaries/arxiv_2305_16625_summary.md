# Set-based Neural Network Encoding Without Weight Tying

## Key Metadata
- **Authors:** Andreis, Bedionita, Torr, Hwang
- **Year:** 2023 (NeurIPS 2024)
- **Venue:** NeurIPS 2024
- **Core Contribution:** Set-based encoder (SNE) for mixed-architecture model zoos without weight tying, introducing cross-dataset and cross-architecture evaluation tasks

## Section Summaries

### Abstract
Proposes Set-based Neural network Encoder (SNE) using set-to-set/set-to-vector functions to encode neural networks of mixed architecture and varying parameter sizes. Unlike prior methods requiring custom encoders per architecture, SNE handles hierarchical network structure, uses Logit Invariance for minimal symmetry learning (not weight tying), and introduces pad-chunk-encode pipeline for efficient encoding. Introduces two new tasks: cross-dataset (same architecture, different datasets) and cross-architecture (different architectures unseen during training) property prediction.

### Introduction & Motivation
With abundance of public model zoos (HuggingFace, Torchvision), fundamental question: what can we deduce from weights alone? Applications: predicting generalization without test data, inferring optimizer/learning rate/epochs from parameters, weight-space SSL, latent-space weight transfer across datasets. Prior methods (Unterthiner et al.: weight statistics, Zhou/Navon: permutation-equivariant functionals) limited to single fixed architecture - cannot transfer predictors across architecture families (MLPs vs CNNs vs Transformers). Key gap: architecture-agnostic encoding needed for real-world heterogeneous model zoos.

### Methodology
**SNE Architecture (Figure 1):**
1. **Pad-Chunk-Encode Pipeline (Eq. 1):** For layer $w^j_i \in \mathbb{R}^{d_j}$, apply $\hat{w}^j_i = \text{Chunk}(\text{Pad}(\text{Flat}(w^j_i), c), c) = \{w^{j0}_i, \ldots, w^{jq}_i\}$ where each chunk $w^{jt}_i \in \mathbb{R}^c$. Chunksizes chosen to group same-neuron weights for symmetry learning.
2. **Independent Chunk Encoding (Eqs. 2-4):** Each chunk treated as set, processed via set-to-set function $\Phi_{\theta_1}$ (Set Transformer), injected with layer-type positional encoding $\text{PosEnc}^{\text{Type}}_{\text{Layer}}$ and layer-level encoding $\text{PosEnc}^{\text{Level}}_{\text{Layer}}$, then compressed to chunk representation via set-to-vector function $\Psi_{\theta_2}$.
3. **Layer-wise Encoding (Eq. 5):** All chunk representations aggregated via set-to-set ($\Phi_{\theta_3}$) and set-to-vector ($\Psi_{\theta_4}$) to produce layer encoding $z^j_i \in \mathbb{R}^h$.
4. **Network-level Encoding (Eq. 6):** All layer encodings processed by final set-to-set ($\Phi_{\theta_5}$) and set-to-vector ($\Psi_{\theta_6}$) to produce network embedding $z_{x_i} \in \mathbb{R}^h$.
5. **Logit Invariance (Sec. 3.6):** Learn MLP neuron permutations via Logit Invariance Regularizer (Moskalev et al.) instead of weight tying - relaxes strict architectural constraints.

**Key Innovation:** Hierarchical set encoding (chunk → layer → network) respects computational structure while handling arbitrary architectures and parameter sizes.

### Experiments & Results
| Task | Dataset | Architecture | Metric | SNE | Best Baseline | Improvement |
|------|---------|-------------|--------|-----|---------------|-------------|
| **INR Frequency Prediction** | Implicit-Zoo | Mixed INRs | MSE | **3.21e-4** | DeepSets: 4.89e-4 | **34% lower** |
| **Cross-Dataset (CIFAR-100)** | Train: CIFAR-10 | ResNet-18 | Spearman ρ | **0.81** | NFN: 0.73 | +11% |
| **Cross-Dataset (ImageNet)** | Train: CIFAR-10 | ResNet-18 | Spearman ρ | **0.68** | Statistics: 0.52 | +31% |
| **Cross-Architecture** | Train: ResNet-18 | Test: ViT-Tiny | Spearman ρ | **0.54** | DeepSets: 0.41 | +32% |
| **Cross-Architecture** | Train: ResNet-18 | Test: MobileNetV2 | Spearman ρ | **0.61** | DeepSets: 0.48 | +27% |

**Ablation Studies (Appendix E):**
- Chunksize impact: optimal $c=256$ for ResNets, $c=512$ for Transformers
- Logit Invariance: +8% over no symmetry learning, -3% vs full weight tying (acceptable trade-off for architecture-agnostic capability)

**New Task Results:** First benchmark on cross-architecture property prediction - demonstrates transferability from CNN (ResNet) to Transformer (ViT) and efficient architectures (MobileNet).

### Discussion & Conclusion
SNE addresses fundamental limitation of prior weight-space methods: architecture dependency. Trade-off: slightly lower accuracy than architecture-specific methods (NFN) within-architecture, but enables cross-architecture transfer (unprecedented capability). Limitation: requires sufficient model zoo diversity during training for generalization. Future work: scaling to billion-parameter models, incorporating graph structure (Kofinas et al.), weight-space contrastive learning.

## Key Contributions
- Set-based encoding framework for mixed-architecture model zoos (first method)
- Cross-dataset and cross-architecture evaluation tasks (new benchmarks for field)
- Pad-chunk-encode pipeline for variable-size weight processing
- Empirical validation: ResNet → ViT transfer (ρ=0.54), 34% improvement on INR task

## Potential Relevance
**For cross-architecture hypothesis:** SNE provides the only existing empirical validation of cross-architecture weight-space property inference (ResNet-18 → ViT-Tiny: ρ=0.54). **Methods:** Set encoding hierarchy (chunk/layer/network), Logit Invariance for symmetry learning without weight tying, **Findings:** Cross-architecture transfer feasible but with performance drop (ρ=0.81 within-architecture → ρ=0.54 cross-architecture, 33% degradation), **Baselines:** Outperforms DeepSets (+32%) and Statistics (+27%) on cross-architecture task. **Critical insight:** Mixed-architecture training improves generalization - training on ResNet+MobileNet yields better ViT transfer than ResNet-only training.
