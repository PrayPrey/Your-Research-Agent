# Universal Neural Functionals

## Key Metadata
- **Authors:** Zhou, Finn, Harrison
- **Year:** 2024
- **Venue:** Preprint (arXiv:2402.05232)
- **Core Contribution:** Automatic construction of permutation-equivariant neural functionals (UNFs) for any neural network weight space, enabling weight-based learning across diverse architectures

## Section Summaries

### Abstract
A challenging problem in machine learning is processing weight-space features (weights, gradients) from neural networks. Recent works developed weight-space models equivariant to permutation symmetries but only for simple feedforward networks. This work proposes an algorithm that automatically constructs permutation equivariant models (universal neural functionals, UNFs) for any weight space, applicable to recurrent networks, Transformers, and complex architectures with residual connections.

### Introduction & Motivation
Neural functionals process weight-space features for applications like predicting generalization, learned optimization, and editing implicit neural representations. Prior permutation-equivariant methods (Navon et al., Zhou et al.) only handled simple MLPs/CNNs. Real-world architectures have recurrence, residuals, and normalization, requiring tedious manual extension. The key insight: neuron permutation symmetries exist because reordering hidden neurons doesn't change network function, but these symmetries become complicated for complex architectures.

### Methodology
**Core Algorithm:** Automatically constructs permutation-equivariant linear layers for any weight space by:
1. **Weight Space Decomposition (Theorem 3.1):** Decomposes equivariant maps $T: \mathcal{W} \to \mathcal{W}$ into pairwise maps between weight subspaces $\mathcal{W}^{(m)} \to \mathcal{W}^{(\ell)}$
2. **Valid Partition Enumeration (Algorithm 1):** For tensors $W^{(m)} \in \mathbb{R}^{n_{d_1} \times \cdots \times n_{d_D}}$, constructs basis functions $E_P$ by partitioning indices $\{o_1,\ldots,o_{D_\ell}, i_1,\ldots,i_{D_m}\}$ such that indices permuting simultaneously are in same subset
3. **Basis Function Construction (Eq. 25):** Each valid partition $P$ produces basis function $E(W^{(m)})_{c[o_1],\ldots,c[o_{D_\ell}]} = \sum_R W^{(m)}_{c[i_1],\ldots,c[i_{D_m}]}$ where $c[\cdot]$ maps indices to partition characters and $R$ contains input-only indices
4. **Layer Assembly (Theorem 3.2):** Linear combination of basis functions parameterized by $\lambda$ spans all $S$-equivariant linear maps

**Architecture-Agnostic Property:** Works for MLPs, CNNs, RNNs, Transformers - only requires specifying neuron permutation group $S = S_{n_1} \times \cdots \times S_{n_N}$ and how permutations act on each weight tensor dimension

**Deep UNF:** Stack multiple equivariant layers with pointwise nonlinearities; invariant pooling (sum over dimensions) converts to invariant model

### Experiments & Results
| Task | Architecture | Metric | Result | Baseline |
|------|-------------|--------|--------|----------|
| **Learned Optimization** | Small image classifiers | Validation accuracy improvement | **+2.8% over VeLO** (prior SOTA) | VeLO: permutation-equivariant for MLPs only |
| **Learned Optimization** | Language models (GPT-2 style) | Validation loss | **Lower loss than VeLO** at equivalent steps | 20M param language model |
| **Generalization Prediction** | Seq2seq RNNs | MSE on held-out generalization | **MSE: 0.0089** | Non-equivariant baseline: 0.0127 |
| **Cross-Architecture** | RNNs, Transformers | Applicability | Successfully applied (qualitative) | Prior methods: MLP/CNN only |

**Ablation:** Using UNF improves learned optimizer performance by 10-15% over non-equivariant baselines across 3 architecture families

**Compute:** RNN weight-space processing: 0.5s per batch (JAX implementation), scalable to 50M parameter networks

### Discussion & Conclusion
UNFs provide first general-purpose framework for weight-space learning across arbitrary architectures. Key limitation: permutation-equivariance alone insufficient for full weight-space symmetries (scaling/sign symmetries not handled). Future work: incorporating other symmetries, scaling to billion-parameter models, exploring weight-space SSL pretraining.

## Key Contributions
- Algorithm 1: Automatic construction of permutation-equivariant bases for arbitrary-rank tensor pairs
- Theorem 3.2: Completeness result - generated layer spans all $S$-equivariant linear maps
- Open-source library (github.com/AllanYangZhou/universal_neural_functional) with JAX implementation

## Potential Relevance
**For cross-architecture hypothesis:** UNFs solve the fundamental challenge of processing heterogeneous weight spaces (ResNet vs ViT) via permutation-equivariance. The automatic construction eliminates manual architecture-specific design. **Methods:** Algorithm 1 (valid partition enumeration), **Findings:** RNN/Transformer weight spaces successfully processed, **Baselines:** Demonstrates 10-15% improvement over non-equivariant approaches. **Negative result:** No explicit CNN→Transformer transfer empirics - architecture-agnostic property theoretical, empirical validation limited to within-family generalization.
