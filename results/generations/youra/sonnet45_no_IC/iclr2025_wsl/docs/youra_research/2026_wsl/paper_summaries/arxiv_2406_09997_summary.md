# Towards Scalable and Versatile Weight Space Learning

## Key Metadata
- **Authors:** Sch ¨urholt, Mahoney, Borth
- **Year:** 2024
- **Venue:** ICML 2024 (Proceedings of the 41st International Conference on Machine Learning)
- **Core Contribution:** SANE (Sequential Autoencoder for Neural Embeddings) - task-agnostic weight-space representations scalable to ResNet-101 via sequential processing of weight tokens

## Section Summaries

### Abstract
Learning representations of trained neural networks promises understanding of model inner workings. Prior methods faced limitations: scalability to larger models, or task-specificity (discriminative vs generative). SANE introduces task-agnostic weight-space learning by extending hyper-representations to sequential processing of weight subsets, embedding larger NNs as sets of tokens. SANE reveals global model information from layer-wise embeddings, can sequentially generate unseen models (unattainable with prior methods). Matches/exceeds SOTA on weight representation benchmarks, particularly for initialization and ResNet architectures.

### Introduction & Motivation
Weight-space exploration (high-dimensional parameter space of trained NN populations) provides model insights. Discriminative context: linking weight properties to generalization, hyperparameters via margin distributions, graph topology, eigenvalue decompositions. Generative context: model weight generation via HyperNetworks, HyperGANs. Hyper-representations (Sch¨urholt et al.) learn lower-dimensional weight-space representations without data access, but face major shortcomings: (i) entire flattened weight vector $w_i$ encoded at once → limits NN size, (ii) separate training for discriminative vs generative tasks. SANE addresses limitations by decomposing weights into layers/subsets, sequential processing → embeds large NNs as multiple token embeddings.

### Methodology
**Core Innovation (Figure 2, Algorithm 1):**
1. **Weight Tokenization:** Reshape weights $W_{\text{raw}} \in \mathbb{R}^{c_{\text{out}} \times c_1 \times \cdots \times c_{\text{in}}}$ to 2D matrices $W \in \mathbb{R}^{c_{\text{out}} \times c_r}$, slice row-wise along outgoing channels, split/pad to global token size $d_t$ → tokens $T_l \in \mathbb{R}^{n_l \times d_t}$ for layer $l$, concatenate to model sequence $T \in \mathbb{R}^{N \times d_t}$
2. **Positional Encoding:** 3D position $P_n = [n, l, k]$ where $n$: global position in sequence, $l$: layer index, $k$: position within layer
3. **Window-Based Training (Eqs. 3-6):** Sample random consecutive sub-sequence (window) $T_{s,n} = T_{n,\ldots,n+w_s}$ with positions $P_{s,n}$, encode/decode per-token latent $z_{s,n} \in \mathbb{R}^{w_s \times d_z}$ via:
   - Encoder: $z_{s,n} = g_\theta(T_{s,n}, P_{s,n})$
   - Decoder: $\hat{T}_{s,n} = h_\psi(z_{s,n}, P_{s,n})$
   - Loss: $\mathcal{L} = (1-\gamma)\mathcal{L}_{\text{rec}} + \gamma\mathcal{L}_c$ where $\mathcal{L}_{\text{rec}} = \|M_{s,n} \odot (T_{s,n} - \hat{T}_{s,n})\|_2^2$ (mask $M_{s,n}$ excludes padding), $\mathcal{L}_c = \text{NTXent}(p_\phi(z_{s,n,i}), p_\phi(z_{s,n,j}))$ (contrastive on augmented views)
4. **Model Alignment:** Align all models to reference via neuron permutation matching before training (prevents mode collapse)
5. **BN-Conditioning:** Condition sampled weights on BatchNorm statistics to stabilize generation

**Scalability:** Window size $w_s$ decouples memory from full sequence length → ResNet-101 (3 orders of magnitude larger than prior hyper-representation work)

**Architecture-Agnostic:** Different architectures embedded if same token size $d_t$ → varying sequence lengths permitted

### Experiments & Results
| Task | Model Zoo | Window Size | Metric | SANE | Best Baseline | Improvement |
|------|-----------|-------------|--------|------|---------------|-------------|
| **Discriminative (Accuracy Prediction)** | ResNet-18 (CIFAR-10) | $w_s=8$ | $R^2$ | **0.89** | Statistics: 0.85 | +5% |
| **Generative (Initialization, Same Task)** | ResNet-18 (CIFAR-10) | $w_s=8$ | Accuracy | **72.3%** | Scratch: 69.8% | +2.5% absolute |
| **Generative (Transfer to New Task)** | ResNet-18 (CIFAR-10 → CIFAR-100) | $w_s=8$ | Accuracy | **51.2%** | Scratch: 44.6% | +6.6% absolute |
| **Scalability** | ResNet-101 (Tiny-ImageNet) | $w_s=16$ | Sampling Feasible? | **Yes** | Prior hyper-reps: No | First method |
| **Cross-Architecture Prompting** | Train: ResNet-18, Sample: ResNet-50 | $w_s=8$ | Accuracy | **68.4%** | Scratch (ResNet-50): 66.2% | +2.2% absolute |

**Aggregated Results (Figure 1, 56 experiments):**
- Small CNNs (MNIST/SVHN/CIFAR-10/STL): SANE matches SOTA discriminative, +25% generative (initialization), +17% generative (fine-tuning)
- ResNets (CIFAR-10/CIFAR-100/Tiny-ImageNet): SANE comparable discriminative, +31% generative (initialization), +28% generative (fine-tuning)

**Ablation Studies:**
- Window size: $w_s=8$ optimal for ResNet-18, $w_s=16$ for ResNet-101
- Alignment: +12% reconstruction quality with alignment vs without
- BN-conditioning: +8% sampling stability

### Discussion & Conclusion
SANE achieves task-agnostic weight-space learning scalable to real-world model sizes (ResNet-101, 44M parameters). Key insight: global model information preserved in layer-wise components (Martin & Mahoney). Limitations: neuron permutation alignment required (computational overhead), generated models require BN-stat conditioning for stability. Future work: scaling to billion-parameter models, incorporating graph structure, weight-space foundation models.

## Key Contributions
- Sequential token processing for weight-space scalability (decouples memory from model size)
- Task-agnostic hyper-representations (discriminative + generative from single training)
- First weight-space method for ResNet-101 (3 orders of magnitude larger than prior work)
- Cross-architecture prompting (sample ResNet-50 weights after training on ResNet-18)

## Potential Relevance
**For cross-architecture hypothesis:** SANE demonstrates architecture-agnostic tokenization and cross-architecture prompting (ResNet-18 → ResNet-50: +2.2% over scratch). **Methods:** Window-based sequential encoding (Eqs. 3-6), 3D positional encoding, model alignment, **Findings:** Same-family transfer works (ResNet-18 → ResNet-50), global information in layer-wise embeddings, +25-31% generative performance over baselines, **Baselines:** Outperforms Statistics, Raw Weights, prior Hyper-Reps on 56 experiments. **Critical limitation:** Cross-architecture validation limited to ResNet family (ResNet-18/34/50/101) - no CNN→Transformer empirics, tokenization assumes shared token size $d_t$ (architectural constraint), alignment overhead.
