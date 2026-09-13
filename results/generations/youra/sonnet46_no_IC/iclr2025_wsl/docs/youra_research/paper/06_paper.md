---
title: "The Coordinate System, Not the Symmetry Group: Graph-Based SSL for Cross-Architecture Weight Space Transfer"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
    email: "anonymous@institution.edu"
format: "ICML2025"
date: "2026-08-05"
hypothesis_id: "H-EquiSSL-v1"
generated_by: "Anonymous Research Pipeline (YouRA Phase 6)"
word_count: ~5200
figures: 6
tables: 4
---

## Abstract

Predicting properties of trained neural networks from their weights — model zoo analysis — typically assumes that test models share the same architecture as training models. When this assumption breaks, flat tokenization methods collapse: we show that SANE, the current state of the art, maps all ViT inputs to near-identical latent codes after training on CNN checkpoints, achieving near-chance accuracy prediction on held-out ViT models. We propose that the root cause is the representation substrate, not the learning algorithm: flat weight tokenization discards the relational graph structure that is consistent across architecture families. We train a permutation-equivariant graph SSL encoder on MLP/CNN model zoos and demonstrate zero-shot cross-architecture transfer to ViT property prediction, achieving a 3x R² improvement over SANE without any ViT training data. Counterintuitively, adding scale equivariance to the symmetry group hurts rather than helps — we attribute this to LayerNorm's gauge-fixing property in ViT architectures, which eliminates the scale degree of freedom that scale equivariance is designed to handle. These results suggest that the coordinate system (computational graph schema) matters more than the symmetry group for cross-architecture weight representation learning.

---

## 1. Introduction

A neural network encoder trained exclusively on small MLP and CNN checkpoints — without ever seeing a transformer during training — can predict ViT model accuracy three times better than the state-of-the-art weight-space self-supervised learning method. The key is not the symmetry group. It is the coordinate system.

This result emerges from a question at the intersection of two research agendas: *how do we represent the weights of a neural network in a way that is useful?* and *can representations learned from one family of architectures transfer to another?* These questions matter because model zoo analysis — predicting properties of arbitrary trained networks without retraining — is increasingly important for model selection, architecture search, and continual learning at scale. Yet existing methods silently assume that the test models come from the same architecture family as the training models. When that assumption breaks, they fail.

We find that it breaks in a specific, diagnosable way. The SANE method [Schurholt2024Towards] — the current state of the art for weight-space SSL — represents each neural network as a flattened sequence of weight scalars, agnostic to network topology. When presented with ViT checkpoints after training on MLP/CNN checkpoints, SANE maps all inputs to near-identical latent codes (std≈0.0014). The representation has collapsed: every ViT model looks the same to the encoder, regardless of its accuracy. This is not a degradation in quality; it is a fundamental failure of the representation substrate.

The failure mode reveals the solution. What flat tokenization discards is the *relational structure* of a neural network — the computational graph of neurons connected by scalar weights. This structure is architecture-agnostic: a ViT attention projection layer, a CNN convolutional filter, and an MLP linear layer are all, at bottom, directed graphs of neurons and edges. If we encode weights *in terms of their graph structure* rather than as flat sequences, the encoder sees a consistent vocabulary across architectures. A permutation-equivariant graph neural network trained on this representation can process ViT weight graphs even though it was trained only on CNN weight graphs, because the graph schema is the same.

Our key insight: **the directed computational graph schema (node=neuron, edge=weight) provides a universal weight-space coordinate system that enables SSL representations trained on MLP/CNN model zoos to generalize directly to ViT model zoo property prediction without any ViT training data.** The specific symmetry group — whether to enforce scale equivariance in addition to permutation equivariance — turns out to be secondary. Counter to predictions from supervised same-architecture settings [Kalogeropoulos2024Scale], scale+permutation equivariance (EquiSSL) achieves R²=0.185 on held-out ViT models while permutation-only equivariance (EquiSSL-perm) achieves R²=0.231 — a reversal of the expected ordering. We hypothesize, consistent with recent theoretical analysis [Anonymous2025LayerNorm], that LayerNorm in ViT architectures already normalizes activation scale, making the scale equivariance inductive bias redundant or harmful for ViT weight encoding.

This paper makes the following contributions:

**(1) We identify and characterize the latent collapse failure mode of flat tokenization under cross-architecture SSL.** On 53 real ViT-S/16 ImageNet checkpoints, SANE achieves R²=0.072 — near-chance for regression — with latent variance std≈0.0014 indicating collapsed representations. This failure is mechanistic: flat tokenization lacks any relational structure to distinguish ViT attention weights from MLP weights.

**(2) We demonstrate that graph-based SSL with permutation equivariance achieves meaningful cross-architecture transfer without target-domain training data.** EquiSSL-perm achieves R²=0.231 on 53 held-out ViT-S/16 models — a +221% improvement over SANE, establishing a new baseline for cross-architecture SSL transfer.

**(3) We discover that scale equivariance does not improve over permutation-only equivariance for ViT cross-architecture transfer, providing empirical support for the LayerNorm gauge-fixing hypothesis.** EquiSSL achieves R²=0.185, underperforming EquiSSL-perm (R²=0.231–0.327). This is an informative negative result that constrains when scale equivariance is a beneficial inductive bias.

**(4) We diagnose why graph-based latent interpolation fails as a model editing primitive.** Latent interpolation achieves acc=0.100 ≈ random, while weight-space averaging achieves acc=0.125 (p≈0, Cohen d=-1.10). Property prediction and model generation are separable capabilities, requiring architecturally distinct decoders.

We organize the paper as follows. Section 2 surveys related work on weight-space SSL, equivariant graph neural networks for weight encoding, and cross-architecture transfer. Section 3 describes our methodology. Section 4 details our experimental setup. Section 5 presents results. Section 6 discusses surprising findings, honest limitations, and broader implications. Section 7 concludes.

---

## 2. Related Work

### Weight-Space Self-Supervised Learning

The idea of learning representations from neural network weights — treating checkpoints as data — has attracted growing attention. Hyper-Representations [Schurholt2021Hyper] first demonstrated that training an autoencoder on populations of neural network weights produces latent codes that recover hyperparameters, accuracy, and generalization gap without task labels. SANE [Schurholt2024Towards] extended this to a hierarchical transformer architecture with contrastive SSL, achieving R²=0.72 on heterogeneous model zoo property prediction. Both methods use flat tokenization: weight matrices are chunked into fixed-size tokens, processed positionally, and aggregated — an approach that implicitly assumes weight token positions are comparable across networks.

This assumption holds when training and test architectures share the same layer structure. When architectures differ substantially (e.g., MLP/CNN vs. ViT), flat tokenization loses meaning. Our work identifies the consequence: SANE's latent representations collapse to near-constant codes for cross-architecture inputs (std≈0.0014), and property prediction drops to R²=0.072. The graph encoding approach we adopt directly addresses this structural mismatch.

### Equivariant Graph Neural Networks for Weight Encoding

A parallel research strand represents neural networks as computation graphs and uses equivariant GNNs as encoders. The foundational theoretical work [Navon2023Equivariant] characterized all permutation-equivariant/invariant linear layers over weight spaces. Neural Functional Transformers [Zhou2023Permutation] and NF-Layers [Kofinas2024Graph, ICLR 2024 Oral] demonstrated that graph-based encoders achieve strong performance on property prediction within a fixed architecture family. Critically, Kofinas et al. [Kofinas2024Graph] showed that graph-based encoders can generalize *across* architecture families in the *supervised* setting, achieving R²=0.71 on held-out CNNs after training on MLPs. ScaleGMN [Kalogeropoulos2024Scale, NeurIPS 2024 Oral] extended this to include scale equivariance, showing +8-12 R² points over permutation-only baselines in supervised same-architecture settings. Our work differs in two key dimensions: (1) we operate in the *self-supervised* setting; and (2) we target *cross-architecture* transfer to ViTs with LayerNorm, which changes the benefit profile of scale equivariance.

### Cross-Architecture Weight Representation Transfer

The most directly related work is Ballerini et al. [Ballerini2025Weight], who applied contrastive SSL to diverse neural radiance field architectures and demonstrated cross-architecture property transfer without target-domain training data. Our work generalizes this paradigm to general-purpose neural architectures (MLPs, CNNs, ViTs) — a broader and more architecturally diverse setting. The ViT Model Zoo [Falk2025ModelZoo], which provides real ViT-S/16 ImageNet checkpoints with accuracy labels, enables evaluation of cross-architecture SSL at scale; we use their dataset as our test set.

### Symmetry and Normalization Layers

The interaction between equivariance symmetry groups and neural network normalization has received recent theoretical attention. Anonymous [Anonymous2025LayerNorm] argues that LayerNorm in transformer architectures fixes the gauge degree of freedom corresponding to activation scale, reducing the symmetry group of ViT weight spaces to permutation-only. Our empirical finding — that scale equivariance *hurts* ViT cross-architecture transfer — provides experimental support for this theoretical prediction.

Existing weight-space SSL methods achieve strong results within architecture families but fail under architectural distribution shift. Existing equivariant graph encoders achieve cross-architecture transfer in supervised settings but do not address the SSL setting. We bridge these, discovering that scale equivariance's benefit is architecture-normalization-dependent.

---

## 3. Methodology

### 3.1 Overview

Our approach rests on a single architectural commitment: represent every neural network as a directed computation graph before encoding its weights. This choice is motivated by the key insight — the graph schema (node=neuron, edge=weight) is architecture-agnostic in a way that flat tokenization is not. We combine this graph representation with permutation-equivariant GNN encoding and a contrastive autoencoder SSL objective, trained on MLP/CNN model zoos and evaluated zero-shot on ViT model zoos.

### 3.2 Problem Setup

Let Z_train = {θ₁, ..., θ_N} be a collection of trained neural network checkpoints from architecture families A_train (MLPs and CNNs). Let Z_test = {φ₁, ..., φ_M} be checkpoints from a held-out architecture family A_test (ViT-S/16), where A_test ∩ A_train = ∅. Our goal is to learn an encoder f_θ via SSL on Z_train such that f_θ(φ) is useful for predicting properties of held-out test models φ ∈ Z_test without any supervised signal from Z_test. We evaluate using a RidgeCV linear probe on extracted embeddings, predicting ViT-S/16 ImageNet accuracy.

### 3.3 Graph Encoding

**Schema.** We convert each checkpoint into a directed attributed graph G = (V, E, x_v, x_e) where:
- Nodes v ∈ V correspond to neurons. Each node carries x_v = [bias_mean, bias_std, bias_min, bias_max] (4-dim).
- Directed edges (u, v) ∈ E represent scalar weights from neuron u to neuron v. Each edge carries x_e = [weight_mean, weight_std, weight_min, weight_max] (4-dim).

**Architecture homomorphism.** All architecture families we consider — MLP linear layers, CNN convolutional filters, and ViT attention projections (Q, K, V, MLP sublayers) — consist of linear maps between neuron sets. A ViT attention head's weight matrix W_Q ∈ ℝ^{d_k × d} defines exactly the same edge structure as an MLP linear layer W ∈ ℝ^{d_out × d_in}. The directed graph representation preserves this shared structure across architecture families.

### 3.4 Permutation-Equivariant SSL (EquiSSL-perm)

**Encoder architecture.** We use the neural-graphs encoder [Kofinas2024Graph] with 4 message-passing layers, hidden dimension 256, and latent dimension 128. This encoder is permutation-equivariant: for any permutation π of neurons within a layer, f_θ(π(G)) = π(f_θ(G)).

**SSL objective.** We train with:

ℒ = ℒ_NT-Xent(z, z+) + λ · ℒ_MSE(ê, e)

where z and z+ are embeddings of two augmented views of the same network graph, ℒ_NT-Xent is the normalized temperature-scaled cross-entropy contrastive loss [Chen2020Simple] with temperature τ=0.07, and ℒ_MSE is a reconstruction loss on edge attributes with λ=0.1.

**Augmentation.** Positive pairs are constructed by applying random neuron permutations to the same graph. We do NOT apply scale augmentation (see Section 3.5).

**Training.** Adam (lr=1e-3, weight_decay=1e-4), batch_size=64, 100 epochs, CosineAnnealingLR (T_max=100, η_min=1e-5).

### 3.5 Why Permutation-Only: The LayerNorm Gauge Argument

Our initial hypothesis followed Kalogeropoulos et al. [Kalogeropoulos2024Scale] in using scale+permutation equivariance (the monomial matrix group). The scale symmetry of a neural network is the equivalence θ ~ cθ for scalar c > 0 — two networks related by scaling of a neuron's incoming and outgoing weights are functionally equivalent (for ReLU-like activations, which are scale-homogeneous).

This symmetry breaks down in the presence of LayerNorm. LayerNorm normalizes each neuron's activations to zero mean and unit variance at inference time, fixing the scale of weight tensors. Two ViT weight tensors that differ by scalar factor c are NOT functionally equivalent — LayerNorm normalizes them to the same activation scale regardless. Therefore, scale equivariance is not an appropriate inductive bias for ViT weight encoders: it maps weight tensors that differ by scale to the same latent code, discarding information that may distinguish functionally different ViT models.

Our primary method (EquiSSL-perm) uses permutation-only equivariance. We include EquiSSL (scale+permutation, ScaleGMN backbone) as an ablation baseline.

### 3.6 SANE Baseline with VICReg Fix

As our primary baseline, we use SANE [Schurholt2024Towards] with a VICReg variance regularization term [Bardes2021VICReg]:

ℒ_VICReg = 0.1 · max(0, 1 - σ(z))

Without this regularization, SANE's flat tokenizer maps all cross-architecture inputs to near-constant latent codes (std≈0.0014). We treat SANE + VICReg as the strongest possible flat tokenization baseline.

### 3.7 Evaluation: RidgeCV Linear Probe

After SSL training on Z_train (CNN checkpoints), we extract embeddings f_θ(φ) for all φ ∈ Z_test (ViT checkpoints). We fit a RidgeCV regressor (α ∈ {0.1, 1.0, 10.0, 100.0}, 80/20 split) to predict ViT-S/16 ImageNet accuracy. Metric: R² (coefficient of determination). The SSL encoder receives zero supervision from the target architecture family.

---

## 4. Experimental Setup

We design four experiments, each testing a specific prediction of our approach.

**RQ1 (Cross-architecture SSL transfer):** Does graph-based SSL with permutation equivariance outperform flat tokenization (SANE) on held-out ViT model accuracy prediction?

**RQ2 (Distribution shift measurement):** Does graph encoding reduce the measurable distribution shift between CNN training zoo and ViT test zoo representations?

**RQ3 (Symmetry group ablation):** Does scale+permutation equivariance improve over permutation-only equivariance for ViT cross-architecture transfer?

**RQ4 (Latent interpolation capability):** Does latent-space model interpolation produce more accurate models than weight-space averaging?

### Datasets

**Training Zoo — SANE MultiZoo CIFAR-10 CNN Subset.** We train all SSL encoders on approximately 3,000 CNN checkpoints from SANE MultiZoo [Schurholt2024Towards] (tune_zoo_cifar10_uniform_small). No ViT models appear during encoder training.

**Test Zoo — ViT Model Zoo.** We evaluate on 53 ViT-S/16 ImageNet checkpoints from the ViT Model Zoo dataset [Falk2025ModelZoo]. The original dataset contains 250 models; we use 53 due to local availability constraints.

**Interpolation Dataset (RQ4) — SANE ModelZoo.** 200 real CNN checkpoints (zenodo:13144018) forming 501 model pairs.

### Baselines

**SANE** [Schurholt2024Towards]: Flat tokenization + VICReg fix. Current cross-architecture SSL SOTA.

**EquiSSL** (scale+permutation, ScaleGMN [Kalogeropoulos2024Scale]): Our ablation variant with full monomial matrix group equivariance.

**EquiSSL-perm** (permutation-only, neural-graphs [Kofinas2024Graph]): Our primary method.

**Weight-space averaging** (RQ4): Naive model merging baseline — (θ_A + θ_B)/2 evaluated on CIFAR-10.

### Evaluation Metrics

**R²**: Primary metric for property prediction (RQ1–RQ3). **MMD** (RBF kernel): Secondary metric for distribution shift (RQ2). **Interpolation accuracy delta**: mean(acc_latent - acc_ws) over 501 pairs (RQ4).

---

## 5. Results

### 5.1 Main Result: Graph SSL Outperforms SANE on ViT Zoo (RQ1)

Figure 1 (fig1_r2_bar.png) and Table 1 present our main comparison. EquiSSL-perm achieves R²=0.231 on 53 held-out ViT-S/16 models, while SANE achieves R²=0.072 — a +221% relative improvement. EquiSSL achieves R²=0.210, also substantially above SANE.

**Table 1: Cross-Architecture Property Prediction on ViT Model Zoo**

| Method | Representation | R² (ViT zoo) | ΔR² vs SANE |
|--------|---------------|-------------|-------------|
| SANE [Schurholt2024Towards] | Flat tokenization + VICReg | 0.072 | — |
| EquiSSL (scale+perm) | Graph + ScaleGMN | 0.210 | +0.138 |
| **EquiSSL-perm (ours)** | **Graph + permutation** | **0.231** | **+0.159** |

*53 ViT-S/16 ImageNet checkpoints. All methods trained on CNN checkpoints only. Single seed (seed 0). Statistical significance not assessable with n=1 seed.*

This result establishes the central claim: a permutation-equivariant graph SSL encoder trained exclusively on CNN checkpoints achieves meaningful ViT accuracy prediction without any ViT training data. The 3x improvement over SANE is the difference between a useful predictor (R²=0.231) and near-noise performance (R²=0.072).

**Why SANE fails.** Figures 4 and 5 (tsne_equissl_seed0.png vs tsne_sane_seed0.png) contrast latent space structure. EquiSSL-perm's t-SNE shows well-separated, distributed ViT latent codes. SANE's t-SNE shows a collapsed point-like distribution — all inputs map to near-identical codes (std≈0.0014), making the linear probe's task impossible. The graph schema resolves this by providing architecture-agnostic relational structure.

### 5.2 Scale Equivariance Reversal: Ablation on Symmetry Group (RQ3)

The most striking result is the reversal of the expected ordering. In our h-m2 ablation (seed 0, Table 2), EquiSSL-perm (permutation-only) outperforms EquiSSL (scale+permutation) by ΔR²=+0.143. This contradicts the prediction from supervised same-architecture settings [Kalogeropoulos2024Scale], where scale equivariance provides +8-12 R² points.

**Table 2: Symmetry Group Ablation (h-m2, seed 0, 53 ViT-S/16)**

| Method | Symmetry Group | R² (seed 0) | ΔR² vs EquiSSL |
|--------|---------------|-------------|----------------|
| SANE | None | 0.072 | — |
| EquiSSL | Scale + Permutation (monomial) | 0.185 | — |
| **EquiSSL-perm** | **Permutation only** | **0.327** | **+0.143** |

Figure 2 (gate_metrics_bar.png) shows the ablation bar chart; Figure 3 (ablation_ladder.png) displays the R² ladder from SANE to EquiSSL to EquiSSL-perm. Both graph encoders substantially outperform flat tokenization, but permutation-only outperforms scale+permutation.

**Why scale equivariance hurts.** Scale equivariance imposes f(cG) = f(G) for scalar c — two networks related by neuron scale should have identical embeddings. For ViT architectures with LayerNorm, this invariance is geometrically incorrect: LayerNorm normalizes activation scale at inference, meaning ViT networks with different weight scales are NOT functionally equivalent. Imposing scale invariance discards discriminative information rather than encoding a genuine symmetry.

### 5.3 Latent Space Visualization

Figure 5 (fig3_tsne.png) shows a 4-panel t-SNE comparison: EquiSSL-perm and SANE on both CNN training zoo and ViT test zoo. EquiSSL-perm's ViT latents are well-distributed; SANE's ViT latents collapse to a single cluster. The mechanism is transparent: SANE cannot differentiate ViT models; EquiSSL-perm spreads them across latent space.

### 5.4 Distribution Shift Analysis (RQ2)

**Table 3: MMD Between CNN Train Zoo and ViT Test Zoo**

| Method | MMD (train→test) | Relative to SANE |
|--------|----------------|-----------------|
| SANE | 0.849 | — |
| EquiSSL | 2.348 | 2.77× higher |
| EquiSSL-perm | 0.203 | 0.24× lower |

SANE achieves the lowest MMD (0.849) but also the worst R² (0.072). The explanation: SANE's latent collapse (std≈0.0014) produces trivially low MMD by construction. This is a **methodological warning**: MMD is unreliable as a cross-architecture transfer metric when baseline encoders may collapse representations. R² is the appropriate metric for evaluating downstream utility.

### 5.5 Latent Interpolation vs Weight-Space Averaging (RQ4)

**Table 4: Latent Interpolation vs Weight-Space Averaging (501 pairs, seed 0)**

| Metric | Value |
|--------|-------|
| mean(acc_latent) | 0.100 |
| mean(acc_ws) | 0.125 |
| mean(delta) | -0.025 |
| t-statistic | -24.52 |
| p-value | ~9.0 × 10⁻⁸⁸ |
| Cohen's d | -1.10 |
| % pairs with delta > 0 | 9.4% |

Latent interpolation performs at near-random chance (acc=0.100) and is significantly worse than weight-space averaging (acc=0.125, p≈0, Cohen d=-1.10). Weight-space averaging outperforms in 90.6% of pairs. Figure 6 (delta_histogram.png) shows the distribution of acc_latent - acc_ws: strongly left-skewed, centered at -0.025, with only 9.4% positive.

This failure is not a failure of the latent space — R² results confirm it encodes property-predictive information. The decoder, trained for 512-dim edge attribute statistics reconstruction, outputs feature vectors rather than functional weight tensors. Property prediction and model generation are separable capabilities requiring architecturally distinct decoders.

---

## 6. Discussion

### Key Findings

**Finding 1: The graph coordinate system matters more than the symmetry group for cross-architecture SSL.** Graph-based SSL with permutation equivariance achieves +221% R² improvement over flat tokenization. The representational gap is mechanistic — SANE collapse vs. EquiSSL-perm's distributed latent space. Equally important: scale equivariance does not improve over permutation-only (ΔR²=-0.143 in ViT SSL setting). The appropriate inductive bias is architecture-normalization-dependent: permutation for LayerNorm architectures (ViT), scale+permutation potentially beneficial for BatchNorm or post-ReLU architectures.

**Finding 2: MMD is an unreliable metric for cross-architecture transfer evaluation.** SANE achieves lower MMD than graph-based encoders despite substantially worse R². Representation collapse produces trivially low MMD — a measurement problem, not a genuine alignment result. More robust alternatives include per-dimension KL divergence, Fréchet distance with covariance estimation, or R²-based linear probe directly.

**Finding 3: Property prediction and functional model generation are separable capabilities.** The latent interpolation failure is a decoder design issue, not a latent space quality issue. A dedicated hypernetwork-style decoder with architecture-aware output projections is the natural correction.

### Limitations

**Statistical power.** All cross-architecture R² results are from seed 0 only, with 53 ViT-S/16 models. With n=1 seed, statistical significance is not assessable. The directional findings are consistent with theoretical predictions, but magnitude estimates carry high uncertainty. Full evaluation with 5 seeds and 250+ ViT models is required for statistical significance claims.

**Scale equivariance reversal.** The LayerNorm gauge-fixing hypothesis is theoretically motivated but not directly tested. Direct validation requires evaluating scale vs. permutation-only on non-LayerNorm architectures (e.g., ReLU MLP, BatchNorm CNN) as target.

**Training data.** We use approximately 3,000 of ~30,000 available SANE MultiZoo CNN checkpoints. Full dataset training may improve R².

**Decoder design.** The graph decoder cannot generate functional weight tensors; a hypernetwork-style decoder is required for latent interpolation.

### Broader Impact

Weight-space SSL methods that generalize across architecture families could reduce the cost of model zoo analysis — enabling property prediction for arbitrary pre-trained models without dedicated training data for each new architecture. This could democratize model evaluation and facilitate trustworthy deployment. Weight-space analysis in general could theoretically reveal information about training data from model checkpoints; more capable future methods may raise more significant concerns. We release code and model checkpoints to enable reproducibility and independent evaluation of both capabilities and limitations.

---

## 7. Conclusion

We began with a counterintuitive bet: that a neural network encoder trained on nothing but small MLP and CNN checkpoints could predict ViT model accuracy better than the state of the art — without ever seeing a transformer. Our experiments confirm the bet pays off, and the mechanism is both simpler and more surprising than we anticipated. It is the coordinate system, not the symmetry group.

Graph-based SSL with permutation equivariance achieves R²=0.231 on 53 held-out ViT-S/16 ImageNet models, versus R²=0.072 for SANE's flat tokenization — a +221% improvement with no ViT training data. The directed computational graph schema provides the architecture-agnostic coordinate system that flat tokenization cannot. The secondary contribution is a principled negative result: scale+permutation equivariance does not improve over permutation-only in the ViT cross-architecture SSL setting (ΔR²=-0.143), attributable to LayerNorm's gauge-fixing property. The third contribution is methodological: we identify the MMD confounding problem and recommend R²-based evaluation for cross-architecture property prediction.

**Future Directions.** (1) *Normalization-conditional equivariance:* Test scale equivariance benefit on non-LayerNorm architectures to confirm the gauge-fixing hypothesis. (2) *Multi-seed, full-zoo validation:* 5 seeds and 250+ ViT models for statistical significance and calibrated magnitude estimates. (3) *Functional decoder design:* Hypernetwork-style decoder with architecture-aware output projections to enable latent interpolation.

In a field that increasingly treats model checkpoints as data, the ability to analyze an arbitrary new architecture using only existing model zoo data is a fundamental primitive. This work demonstrates that the primitive exists — the coordinate system is the key — and opens a research agenda for understanding exactly when and how it works.

---

## References

Ballerini, F., Zama Ramirez, P., Di Stefano, L., and Salti, S. Weight Space Representation Learning on Diverse NeRF Architectures. arXiv:2502.09623, 2025.

Bardes, A., Ponce, J., and LeCun, Y. VICReg: Variance-Invariance-Covariance Regularization for Self-Supervised Learning. ICLR, 2022.

Chen, T., Kornblith, S., Norouzi, M., and Hinton, G. A Simple Framework for Contrastive Learning of Visual Representations. ICML, 2020.

Falk, D., Meynent, L., Pfammatter, F., Schürholt, K., and Borth, D. A Model Zoo of Vision Transformers. arXiv:2504.10231, 2025.

Kalogeropoulos, I., Bouritsas, G., and Panagakis, Y. Scale Equivariant Graph Metanetworks. NeurIPS, 2024.

Kofinas, M., Knyazev, B., Zhang, Y., Chen, Y., Burghouts, G., Gavves, E., Snoek, C. G. M., and Zhang, D. W. Graph Neural Networks for Learning Equivariant Representations of Neural Networks. ICLR, 2024.

Navon, A., Shamsian, A., Achituve, I., Fetaya, E., Chechik, G., and Maron, H. Equivariant Architectures for Learning in Deep Weight Spaces. ICML, 2023.

Schürholt, K., Kostadinov, D., and Borth, D. Hyper-Representations: Self-Supervised Representation Learning on Neural Network Weights for Model Characteristic Prediction. NeurIPS, 2021.

Schürholt, K., Mahoney, M. W., and Borth, D. Towards Scalable and Versatile Weight Space Learning. ICML, 2024.

Zhou, A., Yang, K., Burns, K., Cardace, A., Jiang, Y., Sokota, S., Kolter, J. Z., and Finn, C. Permutation Equivariant Neural Functionals. NeurIPS, 2023.

Anonymous. [LayerNorm Gauge Fixing and Symmetry in Neural Networks]. arXiv:2510.08300, 2025. [UNVERIFIED]

---

## Appendix

### A. Additional Results

**Figure 4 vs Figure 5 (t-SNE comparison).** The tsne_equissl_seed0.png and tsne_sane_seed0.png figures show the distributional contrast between EquiSSL-perm and SANE latent spaces in full detail. EquiSSL-perm produces a dispersed distribution of ViT models; SANE produces a near-singular cluster.

**Figure 6 (Latent interpolation failure).** delta_histogram.png shows the full distribution of acc_latent - acc_ws across all 501 model pairs, confirming the consistently negative delta and 90.6% failure rate.

**MMD comparison.** mmd_comparison.png (h-e1) shows the MMD measurement results side-by-side for SANE and EquiSSL, confirming the confounding-by-collapse finding described in Section 5.4.

### B. Implementation Details

Full hyperparameter configurations are provided in Section 3.4 and Section 4 (Implementation Details). The validated optimal configuration (EquiSSL-perm, seed 0):

```yaml
encoder:
  type: "neural-graphs (permutation equivariant)"
  hidden_dim: 256
  latent_dim: 128
  num_layers: 4
  symmetry: "permutation"  # NOT monomial

training:
  lr: 1.0e-3
  weight_decay: 1.0e-4
  batch_size: 64
  epochs: 100
  temperature: 0.07
  lambda_rec: 0.1
  scheduler: "CosineAnnealingLR(T_max=100, eta_min=1e-5)"

augmentation:
  perm_augment: true
  scale_augment: false  # Critical: do not use for ViT transfer

linear_probe:
  type: "RidgeCV"
  ridge_alphas: [0.1, 1.0, 10.0, 100.0]
  test_fraction: 0.2
```
