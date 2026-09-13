---
source_paper: "arxiv_2302_14040.md"
generated_at: "2026-08-18T23:53:01.339620"
model: "openai/gpt-5.2"
summary_chars: 16658
---

# Permutation Equivariant Neural Functionals

## Key Metadata
- **Authors:** Allan Zhou et al.
- **Year:** 2023
- **Venue:** NeurIPS 2023
- **Core Contribution:** A symmetry-driven framework for **neural functional networks (NFNs)** that process other networks’ weights/gradients by enforcing **neuron-permutation equivariance** via structured **NF-Layers**.

## Section Summaries

### Abstract
This work studies the design of neural networks that can process the weights or
gradients of other neural networks, which we refer to as neural functional networks
(NFNs). Despite a wide range of potential applications, including learned opti-
mization, processing implicit neural representations, network editing, and policy
evaluation, there are few unifying principles for designing effective architectures
that process the weights of other networks. We approach the design of neural
functionals through the lens of symmetry, in particular by focusing on the permuta-
tion symmetries that arise in the weights of deep feedforward networks because
hidden layer neurons have no inherent order. We introduce a framework for build-
ing permutation equivariant neural functionals, whose architectures encode these
symmetries as an inductive bias. The key building blocks of this framework are
NF-Layers (neural functional layers) that we constrain to be permutation equiv-
ariant through an appropriate parameter sharing scheme. In our experiments, we
find that permutation equivariant neural functionals are effective on a diverse set of
tasks that require processing the weights of MLPs and CNNs, such as predicting
classifier generalization, producing “winning ticket” sparsity masks for initializa-
tions, and classifying or editing implicit neural representations (INRs). In addition,
we provide code for our models and experiments1.

### Introduction & Motivation
Neural networks’ **weights and gradients** can themselves be treated as data, enabling applications like learned optimization, extracting semantics from implicit neural representations (INRs), network editing, and policy evaluation. However, designing architectures that operate on weight space lacks unifying principles, and naive architectures can waste data/parameters by relearning known invariances. The key observation is that many feedforward networks have **neuron permutation symmetries** because hidden units are unordered: permuting hidden neurons (with a coupled permutation of adjacent weight-matrix rows/columns) preserves the represented function. The paper’s goal is to build **neural functionals** whose architectures are **equivariant/invariant** to these symmetries, yielding better inductive bias, efficiency, and generalization on weight-space tasks.

### Methodology
The paper formalizes the “network-as-input” setting by defining a **weight space** \(U=(W,v)\) for an \(L\)-layer feedforward net with widths \(n_0,\dots,n_L\). Weights are \(W=\{W^{(i)}\in\mathbb{R}^{n_i\times n_{i-1}}\}_{i=1}^L\) and biases \(v=\{v^{(i)}\in\mathbb{R}^{n_i}\}_{i=1}^L\). A *neural functional* is any function of such objects (weights, gradients, masks, or intermediate “weight-space features”); a **neural functional network (NFN)** is a neural net implementing such a function.

**Symmetry groups.** Two permutation-symmetry assumptions are considered:
- **HNP** (hidden neuron permutations): \(\tilde S=\prod_{i=1}^{L-1} S_{n_i}\) (always valid for standard MLP/CNN hidden layers).
- **NP** (all-layer permutations): \(S=\prod_{i=0}^{L} S_{n_i}\) (stronger, often not semantically correct, but yields cheaper layers).

For \(\sigma=(\sigma_0,\dots,\sigma_L)\in S\), the group action on weights/biases is (their Eq. 1):
\[
[\sigma W]^{(i)}_{jk}=W^{(i)}_{\sigma_i^{-1}(j),\,\sigma_{i-1}^{-1}(k)},\quad
[\sigma v]^{(i)}_{j}=v^{(i)}_{\sigma_i^{-1}(j)}.
\]
They also extend inputs to **multi-channel weight-space features** \(U^c\) where each \(W^{(i)}\in\mathbb{R}^{n_i\times n_{i-1}\times c}\) (channels are *not* permuted).

**Design principle: linear equivariant layers + pointwise nonlinearities.** Since pointwise nonlinearities are already permutation equivariant, the key is to construct a **linear** layer \(T:U^{c_i}\to U^{c_o}\) that is \(S\)-equivariant:
\[
\sigma\,T(U)=T(\sigma U)\quad \forall \sigma\in S.
\]
They derive the most general form of such a layer via **equivariant parameter sharing**: flatten \(U\) into \(\mathrm{vec}(U)\), consider a generic linear map \(\theta\mathrm{vec}(U)\), and constrain \(\theta\) so its entries are constant on index orbits under the group action (standard approach in geometric deep learning / Ravanbakhsh et al.). This reduces an \(O(\mathrm{dim}(U)^2)\)-parameter matrix to a structured layer.

**Core building block: the NP equivariant NF-Layer \(H\).** Ignoring biases for exposition (full form includes biases in the appendix), the NF-Layer maps \(W^{(1:L)}\mapsto H(W)^{(1:L)}\). For each layer \(i\), output entry \(H(W)^{(i)}_{jk}\in\mathbb{R}^{c_o}\) is computed from input weight-space features using shared parameters across indices (their Eq. 2):
\[
H(W)^{(i)}_{jk}=
\left(\sum_s a_{i,s} W^{(s)}_{\star,\star}\right)
+ b_{i,i}W^{(i)}_{\star,k}
+ b_{i,i-1}W^{(i-1)}_{k,\star}
+ c_{i,i}W^{(i)}_{j,\star}
+ c_{i,i+1}W^{(i+1)}_{\star,j}
+ d_i W^{(i)}_{jk}.
\]
Here “\(\star\)” denotes summation/averaging over the corresponding axis (row-sum, col-sum, or global sum). In the multi-channel case, each parameter (e.g., \(a_{i,s}\)) is a matrix in \(\mathbb{R}^{c_o\times c_i}\). The terms couple **adjacent layers** via \(W^{(i-1)}\) and \(W^{(i+1)}\), ensuring the layer respects the coupled row/column permutations that define neuron relabelings. The authors prove: (i) \(H\) is \(S\)-equivariant, and (ii) **any linear \(S\)-equivariant map** \(T\) is representable as \(H\) for some parameters \((a,b,c,d)\) (a characterization / “basis” result for linear equivariant maps under this group).

**HNP variant and efficiency tradeoff.** They also derive a full HNP-equivariant layer \(\tilde H\) (appendix), which is more appropriate when input/output neurons are ordered but hidden neurons are not. Parameter counts (Table 1):
- Generic linear \(T\): \(c_ic_o\,\mathrm{dim}(U)^2\).
- NP equivariant \(H\): \(O(c_ic_o L^2)\).
- HNP equivariant \(\tilde H\): \(O\!\big(c_ic_o(L+n_0+n_L)^2\big)\), which can be prohibitive when \(n_0\) or especially \(n_L\) is large.

**IO-encoding to “break” NP symmetry.** Because NP wrongly assumes input/output neurons are exchangeable, they introduce an **input-output positional encoding**: add learned or sinusoidal embeddings to columns of \(W^{(1)}\) and rows of \(W^{(L)}\) (and \(v^{(L)}\)). This injects identity into input/output axes while keeping the efficient NP-equivariant core.

**Invariant NF-Layers for tasks requiring invariance.** For scalar/label prediction, they stack equivariant NF-Layers with a final invariant pooling operator \(P\) that averages/sums over all permutable axes, producing a fixed-size vector (their \(P:U\to\mathbb{R}^{2L}\)):
\[
P(U)=\big(W^{(1)}_{\star,\star},\dots,W^{(L)}_{\star,\star},v^{(1)}_\star,\dots,v^{(L)}_\star\big),
\]
then apply an MLP head.

**CNN extension.** For convolutional layers, neuron permutations act on **channel** dimensions; spatial filter coordinates are not permuted. They fold spatial filter dimensions into the feature-channel dimension (e.g., for 1D conv \(W^{(i)}\in\mathbb{R}^{n_i\times n_{i-1}\times w}\), treat it as \(w\) “channels”), allowing the same NF-Layer \(H\) to be applied to CNN weight spaces. This covers common CNN→global-pool→FC pipelines (e.g., ResNet-like heads) where spatial dimensions are removed before FC.

### Experiments & Results
They evaluate NFNs on four weight-space tasks spanning both **invariant** (predict a scalar/class) and **equivariant** (output a structured object like a mask or edited weights) objectives. NFN variants:
- **NFN\(_\text{NP}\)**: uses NP-equivariant NF-Layer \(H\) (parameter efficient).
- **NFN\(_\text{HNP}\)**: uses HNP-equivariant \(\tilde H\) (more faithful symmetry, more expensive).
- **NFN\(_\text{PT}\)**: pointwise ablation using only \(d_iW^{(i)}_{jk}\) (no cross-weight interactions).
Baselines include (i) **STATNN** from Unterthiner et al. (handcrafted weight statistics + predictor), (ii) **MLP** and **MLP\(_\text{Aug}\)** (3-layer ReLU MLP with permutation augmentation), and (iii) **inr2vec** for INR weight classification on 3D shapes.

**(1) Predicting CNN generalization from weights (invariance; metric: Kendall’s \(\tau\)).** Dataset: **Small CNN Zoo** (thousands of small CNNs trained on multiple datasets/hyperparameters; exact counts/splits not specified in the excerpt). Task: predict **test accuracy** given CNN weights; metric is **Kendall’s \(\tau\)** rank correlation. Results on grayscale subsets (Table 2) show NFN\(_\text{HNP}\) is best:

| Dataset | NFN\(_\text{HNP}\) | NFN\(_\text{NP}\) | STATNN |
|---|---:|---:|---:|
| CIFAR-10-GS | \(0.934\pm0.001\) | \(0.922\pm0.001\) | \(0.915\pm0.002\) |
| SVHN-GS | \(0.931\pm0.005\) | \(0.856\pm0.001\) | \(0.843\pm0.000\) |

Uncertainty here is max/min over two runs. Takeaway: directly processing raw weights with the right symmetry prior beats handcrafted stats; HNP helps when IO symmetry should not be assumed.

**(2) Classifying implicit neural representations (INRs) from weights (invariance; metric: accuracy).** They build datasets of **SIREN** INRs encoding:
- Images: MNIST, FashionMNIST, CIFAR-10 (each INR maps coordinate \(\to\) pixel/RGB).
- 3D shapes: ShapeNet-10, ScanNet-10 (each INR encodes SDF/UDF).
Train/val/test splits exist but ratios/sizes are not included in the provided excerpt. Baselines: MLP and MLP\(_\text{Aug}\) (explicitly stated as 3-layer ReLU, 1000 hidden units/layer), plus **inr2vec** for shapes (notably, inr2vec assumes shared initialization originally; here they allow independent random initializations).

Image INR classification (Table 3, test accuracy %):
| Dataset | NFN\(_\text{HNP}\) | NFN\(_\text{NP}\) | MLP | MLP\(_\text{Aug}\) |
|---|---:|---:|---:|---:|
| MNIST-10 | \(92.5\pm0.071\) | \(92.9\pm0.218\) | \(14.5\pm0.035\) | \(21.0\pm0.172\) |
| FashionMNIST | \(72.7\pm1.53\) | \(75.6\pm1.07\) | \(12.5\pm0.111\) | \(15.9\pm0.181\) |
| CIFAR-10 | \(44.1\pm0.471\) | \(46.6\pm0.072\) | \(16.9\pm0.250\) | \(18.9\pm0.432\) |

3D INR classification (Table 4, test accuracy %):
| Dataset | NFN\(_\text{HNP}\) | NFN\(_\text{NP}\) | MLP | MLP\(_\text{Aug}\) | inr2vec |
|---|---:|---:|---:|---:|---:|
| ShapeNet-10 | \(86.9\pm0.860\) | \(88.7\pm0.461\) | \(25.4\pm0.121\) | \(33.8\pm0.126\) | \(39.1\pm0.385\) |
| ScanNet-10 | \(64.1\pm0.572\) | \(65.9\pm1.10\) | \(32.9\pm0.351\) | \(45.5\pm0.126\) | \(38.2\pm0.409\) |

Uncertainty is standard error over three runs. Key finding: equivariant/invariant NFNs can decode semantic class information from weights far better than non-equivariant MLPs, even with augmentation; NP can match/exceed HNP with fewer parameters (they note e.g. ~35% parameters on CIFAR-10 INR classification).

**(3) Predicting “winning ticket” sparsity masks from initialization (equivariance; metric: downstream test accuracy).** They treat a winning ticket as a mask \(M\in\{0,1\}^{\mathrm{dim}(U)}\) that prunes an initialization \(U_0\) so that training the sparse network matches dense performance. Training data: pairs \((U_0, M)\) where \(M\) is produced by **one step of IMP** at sparsity \(P_m=0.95\) (95% pruned) for (a) MLP on MNIST and (b) CNN on CIFAR-10. Model: a **conditional VAE** that generates \(M\) conditioned on \(U_0\); NFNs parameterize the conditional model (exact ELBO / architecture hyperparameters not given in the excerpt). Baselines: IMP itself, Random mask with matching Bernoulli(\(1-P_m\)), and Dense training.

Downstream test accuracy after training with predicted masks (Table 5, %):
| Dataset | Dense | IMP | Random | NFN\(_\text{NP}\) | NFN\(_\text{PT}\) |
|---|---:|---:|---:|---:|---:|
| CIFAR-10 | \(63.1\pm0.06\) | \(44.0\pm0.06\) | \(21.1\pm0.26\) | \(41.4\pm0.08\) | \(42.6\pm0.07\) |
| MNIST | \(97.8\pm0.0\) | \(96.2\pm0.04\) | \(89.6\pm0.36\) | \(94.8\pm0.01\) | \(95.0\pm0.01\) |

Here NFN\(_\text{HNP}\) is stated to be too parameter-inefficient. A notable ablation result: **NFN\(_\text{PT}\)** performs comparably to NFN\(_\text{NP}\), suggesting that (in this setup) a large portion of ticket predictability may come from per-weight statistics rather than higher-order interactions (they further analyze this in an appendix).

**(4) Weight-space “style editing” of INRs (equivariance; metric: image MSE).** Goal: edit a trained SIREN’s weights so the *represented image* undergoes a target transformation, without operating in pixel space. Two tasks:
- **Dilate** MNIST digits (thicken strokes).
- **Contrast** adjustment on CIFAR-10.
Training data: apply OpenCV image transforms to generate target images; train NFN editor to minimize **MSE** between images rendered by edited INR and the transformed targets. This task requires modeling interactions between weights because the transformation is structured in image space.

Test MSE (Table 6; lower is better):
| Method | Contrast (CIFAR-10) | Dilate (MNIST) |
|---|---:|---:|
| MLP | 0.031 | 0.306 |
| MLP\(_\text{Aug}\) | 0.029 | 0.307 |
| NFN\(_\text{PT}\) | 0.029 | 0.197 |
| NFN\(_\text{HNP}\) | 0.021 | 0.070 |
| NFN\(_\text{NP}\) | **0.020** | **0.068** |

Qualitative samples show NFNs better match dilation geometry and contrast scaling. Crucially, unlike winning-ticket prediction, here the pointwise ablation is substantially worse—evidence that **cross-weight / cross-layer aggregation terms in Eq. 2 matter** for structured edits.

**Compute/statistics.** The excerpt does not report GPU hours, wall-clock, or inference speed. Reported uncertainties are either standard errors over 3 runs (INR tasks, editing) or min/max over 2 runs (generalization prediction).

### Discussion & Conclusion
The paper shows that explicitly encoding **neuron permutation equivariance** yields NFNs that generalize better and are more sample/parameter-efficient than non-equivariant MLP baselines for multiple weight-space tasks. NP-equivariant layers offer strong scalability via drastic parameter sharing, and IO-encoding partially mitigates the overly-strong NP symmetry assumption. Limitations noted include activation-size growth (memory) for large networks and the lack of extensions to more complex architectures (e.g., ResNets with nontrivial flattening, Transformers).

## Key Contributions
- **Formal symmetry framework for neural functionals:** Defines weight-space features \(U^c\) and permutation group actions (Eq. 1), and frames NFN design as constructing equivariant/invariant maps under neuron relabelings.
- **NF-Layer characterization for NP equivariance:** Derives the general **linear \(S\)-equivariant** map \(H:U^{c_i}\to U^{c_o}\) via orbit-based parameter sharing and gives an explicit closed form (Eq. 2), with a proof sketch that \(H\) spans all linear NP-equivariant maps.
- **HNP vs NP tradeoff + IO-encoding:** Introduces both HNP- and NP-based layers, quantifies parameter scaling (Table 1), and proposes **input/output positional encoding** to retain efficiency while breaking inappropriate IO symmetry.
- **Invariant head construction:** Provides invariant pooling \(P\) to reduce equivariant weight-space features to fixed-size vectors suitable for regression/classification.
- **CNN weight-space extension:** Shows how convolution filter spatial dimensions can be folded into channels so the same NF-Layer machinery applies to CNN weights (when permutation symmetry is over channels).
- **Broad empirical validation across tasks:** Demonstrates improvements on (i) CNN generalization prediction (Kendall’s \(\tau\)), (ii) INR classification (accuracy), (iii) winning-ticket mask prediction (downstream test accuracy), and (iv) INR weight-space editing (MSE), including informative ablations (NFN\(_\text{PT}\)).

## Potential Relevance
If you need to build models that *consume networks as inputs* (meta-learning, learned optimizers, model auditing, mechanistic comparisons, INR analytics), this paper provides a concrete recipe for injecting the correct **relabeling symmetries** rather than relying on augmentation. The explicit NF-Layer formula (Eq. 2) is useful as a drop-in primitive for weight-space message passing across adjacent layers, and the experiments suggest a practical guideline: **pointwise features may suffice for sparse-mask prediction**, but **full interaction terms are critical for structured edits** (and likely other “semantic transformation” tasks).