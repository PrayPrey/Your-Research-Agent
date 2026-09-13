---
source_paper: "arxiv_2301_12780.md"
generated_at: "2026-08-03T17:30:46.991476"
model: "openai/gpt-5.2"
summary_chars: 14409
---

# Equivariant Architectures for Learning in Deep Weight Spaces (DWSNet)

## Key Metadata
- **Authors:** Aviv Navon et al.
- **Year:** 2023
- **Venue:** ICML 2023 (Proceedings of the 40th International Conference on Machine Learning; PMLR 202)
- **Core Contribution:** A principled, permutation-equivariant architecture (DWSNet) for learning directly on MLP weight spaces, including a full characterization of affine equivariant/invariant layers for MLP neuron-permutation symmetries.

## Section Summaries

### Abstract
Designing machine learning architectures for pro-
cessing neural networks in their raw weight ma-
trix form is a newly introduced research direction.
Unfortunately, the unique symmetry structure of
deep weight spaces makes this design very chal-
lenging. If successful, such architectures would
be capable of performing a wide range of intrigu-
ing tasks, from adapting a pre-trained network to a
new domain to editing objects represented as func-
tions (INRs or NeRFs). As a first step towards
this goal, we present here a novel network archi-
tecture for learning in deep weight spaces. It takes
as input a concatenation of weights and biases of
a pre-trained MLP and processes it using a com-
position of layers that are equivariant to the natu-
ral permutation symmetry of the MLP’s weights:
Changing the order of neurons in intermediate
layers of the MLP does not affect the function it
represents. We provide a full characterization of
all affine equivariant and invariant layers for these
symmetries and show how these layers can be im-
plemented using three basic operations: pooling,
broadcasting, and fully connected layers applied
to the input in an appropriate manner. We demon-
strate the effectiveness of our architecture and its
advantages over natural baselines in a variety of
learning tasks.

### Introduction & Motivation
The paper studies **learning directly in neural network weight space**, where each datapoint is itself a trained neural network (e.g., an INR/NeRF representing an object, or a classifier trained on a task). A key obstacle is that weight vectors are *not* a canonical representation: many parameterizations correspond to the **same function** due to neuron-permutation symmetries in MLP hidden layers (known since Hecht-Nielsen, 1990). Prior work often flattens weights or uses generic attention/MLPs, which struggles to respect these symmetries and generalize across independently trained networks. The authors propose a symmetry-principled solution: characterize the full class of affine maps that are equivariant/invariant to MLP permutation symmetries and build deep architectures (DWSNets) by stacking such layers with nonlinearities.

### Methodology
**Object of interest (deep weight space).** For an \(M\)-layer MLP
\[
f(x)=x_M,\quad x_{m+1}=\sigma(W_{m+1}x_m+b_{m+1}),\quad x_0=x,
\tag{1}
\]
define the weight-space as the direct sum
\[
V=\bigoplus_{m=1}^{M}\left(\mathbb{R}^{d_m\times d_{m-1}}\oplus\mathbb{R}^{d_m}\right)=\bigoplus_{m=1}^M (W_m\oplus B_m).
\tag{3}
\]
Hidden-layer neuron permutations form the symmetry group
\[
G := S_{d_1}\times\cdots\times S_{d_{M-1}}.
\tag{4}
\]
A group element \(g=(\tau_1,\ldots,\tau_{M-1})\) acts by simultaneously permuting rows/columns of adjacent weights (and biases) using permutation matrices \(P_{\tau_m}\):
\[
\begin{aligned}
W'_1&=P_{\tau_1}^\top W_1,\quad b'_1=P_{\tau_1}^\top b_1, \\
W'_m&=P_{\tau_m}^\top W_m P_{\tau_{m-1}},\quad b'_m=P_{\tau_m}^\top b_m,\ \ m\in[2,M-1],\\
W'_M&=W_M P_{\tau_{M-1}},\quad b'_M=b_M.
\end{aligned}
\tag{5}
\]
These transformations preserve the represented function for any pointwise \(\sigma\).

**DWSNet architecture.** A DWSNet is an equivariant network in weight-space built as
\[
F_{\text{equi}}(x)=L_k\circ \sigma\circ\cdots\circ \sigma\circ L_1(x),
\tag{2}
\]
where each \(L_i(v)=Av+b\) is **affine \(G\)-equivariant**. For invariant tasks, append a **linear invariant** map plus an MLP head.

**Main technical result: characterization of all linear equivariant maps \(V\to V\).** The authors exploit that \(V\) is a direct sum of subrepresentations \(\{W_m,B_m\}\). A classical block-decomposition principle (their Proposition 5.2) implies that any linear equivariant map between direct sums decomposes into blocks mapping between constituent representations. They first coarsen \(V=W\oplus B\) (weights vs. biases) and decompose any linear equivariant operator into four parts:
- \(L_{ww}:W\to W\),
- \(L_{wb}:W\to B\),
- \(L_{bw}:B\to W\),
- \(L_{bb}:B\to B\),
and then further into block matrices between specific \((W_m,B_\ell)\) pairs.

**Implementable basis via three primitives.** Every block is shown to be implementable using only:
1) **Pooling** (sum-reduction over a permuted/set index),
2) **Broadcasting** (replicating along a permuted/set index),
3) **Dense linear maps** on free indices,
plus known permutation-equivariant linear forms:
- **DeepSets linear layer** (Zaheer et al., 2017) for a single shared set index,
- **Hartford et al. (2018)** linear equivariant layer for a Cartesian product of two sets (needed for \(W_m\in\mathbb{R}^{d_m\times d_{m-1}}\) when both indices are permuted and shared).

They introduce “set indices” (hidden-layer dimensions \(m\in[1,M-1]\), permuted by \(G\)) vs. “free indices” (\(m\in\{0,M\}\), not permuted), and “shared indices” (same permuted dimension in input/output). Construction rules: contract unshared set indices via pooling; extend output set indices via broadcast; handle free indices via dense linear maps. A dimension-counting argument (Appendix D/E, referenced) proves these blocks **span** all equivariant linear maps (Theorem 5.1).

**How blocks aggregate in practice.** For an interior layer \(m\) (example shown for weight–weight mapping), the update decomposes into position-dependent contributions:
\[
F(v)_m
=H_{\text{self}}(W_m)
+H_{\text{adjacent}}(W_{m-1},W_{m+1})
+H_{\text{sum}}(\{W_j\}_{j\notin\{m-1,m,m+1,1,M\}})
+H_{\text{boundary}}(W_1,W_M),
\]
where \(H_{\text{self}}\) uses the Hartford et al. equivariant form, adjacent interactions use DeepSets-style equivariant mixing, and distant/boundary terms use pooled summaries + broadcast + dense linear transforms. Nonlinearities are pointwise across features.

**Expressivity results (why equivariance doesn’t cripple power).** They prove DWSNets can approximate a **forward pass evaluator** (Proposition 6.1): given weights \(v\) and input \(x\), approximate \(f_v(x)\) uniformly on compact sets. They further argue (Proposition 6.2, informal) that DWSNets can approximate Lipschitz functionals defined over the **function space** induced by MLPs (i.e., functionals constant over permutation orbits), under mild assumptions (in Appendix G).

**Hyperparameters/training details.** Many training hyperparameters (optimizer, LR, batch size, epochs, schedulers) are stated to be in Appendix J, which is not included in the provided excerpt; the summary below therefore reports only what is explicitly given in the main text.

### Experiments & Results
**Goal.** Evaluate whether enforcing the correct permutation symmetry yields better learning on collections of independently trained networks, compared to (a) naive flattening, (b) permutation augmentation, (c) explicit weight alignment, and (d) recent weight-space architectures.

**Baselines (same data/loss/training protocol per task).**
1) **MLP** on vectorized weights,
2) **MLP + permutation augmentation** (random \(g\in G\) applied to inputs),
3) **MLP + alignment** using Ainsworth et al. (2022) weight-matching pre-processing,
4) **INR2Vec (Arch.)** (Luigi et al., 2023) without their pretraining,
5) **Transformer** weight-space encoder from Schürholt et al. (2021) that attends over rows of weight/bias matrices.

**Data preparation protocol.** Input networks are trained **independently from different random seeds** to create diverse “network datasets.” Unless stated otherwise, there is **one trained network per underlying datapoint** (e.g., one INR per image).

**Tasks & datasets.**
- **Sine-wave INR regression (frequency).** INRs fit sine waves on \([-\pi,\pi]\) with frequency \(b\sim U(0.5,10)\). The DWSNet predicts \(b\) from INR weights. Performance reported as test MSE (log scale) vs. number of training networks (plot only; no exact numbers in excerpt).
- **INR classification (MNIST, Fashion-MNIST).** INRs represent images; predict the image class from INR weights. Metric: **test accuracy (mean ± std)**.
- **Self-supervised dense representations (SimCLR-like).** INRs fit \(a\sin(bx)\) on \([-\pi,\pi]\), with \(a,b\sim U(0,10)\), \(x\) a grid of size **2000**. Views: add Gaussian noise (std **0.2**) + random masking (prob **0.5**). Evaluate learned embeddings by fitting a **linear regressor** to predict \((a,b)\); metric: **MSE**; also show t-SNE qualitatively.
- **Domain adaptation in weight space (CIFAR-10 \(\to\) corrupted CIFAR-10).** Train a model that outputs residual weights \(\Delta v\) such that \(v-\Delta v\) performs well on target domain. Input classifiers are trained on **binary tasks** (distinguish two randomly sampled CIFAR-10 classes) to increase diversity. Target corruptions: random rotation, flipping, Gaussian noise, color jittering. Metric: **test accuracy** on CIFAR10-corrupted. Baseline includes “No adaptation.”

**Main quantitative results.**

**Table A — INR classification accuracy (mean ± std).**

| Method | MNIST INR Acc. | Fashion-MNIST INR Acc. |
|---|---:|---:|
| MLP | 17.55 ± 0.01 | 19.91 ± 0.47 |
| MLP + Perm. aug | 29.26 ± 0.18 | 22.76 ± 0.13 |
| MLP + Alignment | 58.98 ± 0.52 | 47.79 ± 1.03 |
| INR2Vec (Arch.) | 23.69 ± 0.10 | 22.33 ± 0.41 |
| Transformer | 26.57 ± 0.18 | 26.97 ± 0.33 |
| **DWSNets (ours)** | **85.71 ± 0.57** | **67.06 ± 0.29** |

**Table B — Self-supervised embedding quality (linear regression MSE for \((a,b)\)).**

| Method | MSE |
|---|---:|
| MLP | 7.39 ± 0.19 |
| MLP + Perm. aug | 5.65 ± 0.01 |
| MLP + Alignment | 4.47 ± 0.15 |
| INR2Vec (Arch.) | 3.86 ± 0.32 |
| Transformer | 5.11 ± 0.12 |
| **DWSNets (ours)** | **1.39 ± 0.06** |

**Table C — Domain adaptation accuracy (CIFAR10 \(\to\) CIFAR10-Corrupted).**

| Method | Test Acc. |
|---|---:|
| No adaptation | 60.92 ± 0.41 |
| MLP | 64.33 ± 0.36 |
| MLP + Perm. aug | 64.69 ± 0.56 |
| MLP + Alignment | 67.66 ± 0.90 |
| INR2Vec (Arch.) | 65.69 ± 0.41 |
| Transformer | 61.37 ± 0.13 |
| **DWSNets (ours)** | **71.36 ± 0.38** |

**Table D — Multi-view INR augmentation (Fashion-MNIST INR classification; DWSNet).**

| #INR views per image | 1 | 2 | 4 | 6 | 8 | 10 |
|---:|---:|---:|---:|---:|---:|---:|
| Acc. | 67.06 ± 0.29 | 70.22 ± 0.38 | 70.31 ± 0.09 | 73.32 ± 0.11 | 74.87 ± 0.18 | 75.12 ± 0.05 |

**Findings / analysis reported by authors.**
- DWSNets consistently outperform all baselines, often by large margins, especially on INR classification (e.g., **85.71% vs 58.98%** best baseline on MNIST INRs).
- Compared to explicit alignment (Ainsworth et al., 2022), DWSNets are argued to **scale better** with data and avoid the difficulty of solving hard weight-matching problems.
- Multi-view training (multiple independently trained INRs per image) improves generalization by \(\approx 8\%\) absolute on Fashion-MNIST (67.06 \(\to\) 75.12).

**What is not reported in excerpt.** Exact dataset sizes, train/val/test splits, compute budgets (GPU hours), and statistical tests beyond mean±std are not included in the provided text (they are referenced as being in appendices).

### Discussion & Conclusion
DWSNets provide a symmetry-correct way to process MLP parameters, yielding strong empirical gains over flattening, augmentation, alignment, and transformer-based baselines on INR understanding and weight-space domain adaptation. Limitations include (i) layer structure tied to a fixed input MLP architecture (potentially mitigated by parameter sharing across blocks), (ii) training instability tied to initialization difficulty, and (iii) implementation complexity. Future work includes incorporating additional symmetries (e.g., scaling), better initialization, heterogeneous input networks, improved augmentation, and extending to other architectures (CNNs, Transformers) via analogous channel/permutation symmetries.

## Key Contributions
- **Symmetry-first formulation of learning in weight space:** Treats MLP parameters as elements of a structured direct-sum space \(V=\bigoplus_m(W_m\oplus B_m)\) with an explicit permutation group \(G=S_{d_1}\times\cdots\times S_{d_{M-1}}\) acting as in Eq. (5), capturing the fundamental non-identifiability of neuron order.
- **Complete characterization of affine equivariant/invariant layers for MLP weight-space permutations:** Proves (Theorem 5.1) that all linear equivariant maps \(V\to V\) decompose into blocks between \(\{W_m,B_\ell\}\), and each block is implementable via **pooling**, **broadcasting**, and **dense linear maps**, plus known DeepSets/Hartford equivariant forms; yields parameter-efficient alternatives to generic FC layers.
- **Expressive power guarantees aligned with functional semantics:** Shows DWSNets can approximate an input network’s forward pass (Proposition 6.1) and can approximate Lipschitz functionals over the induced function space (Proposition 6.2 informal), supporting the claim that equivariance does not prevent learning meaningful properties of represented functions.
- **Empirical validation across INR understanding and network editing/adaptation:** Large improvements on INR classification (MNIST INRs **85.71%**, Fashion-MNIST INRs **67.06%**) and on CIFAR-10 \(\to\) corrupted adaptation (**71.36%**), plus strong self-supervised embeddings (MSE **1.39** vs **3.86** best baseline).

## Potential Relevance
This paper is a concrete blueprint for building **weight-space foundation models** that respect the true equivalence classes of networks (permutation orbits), which is directly relevant to hypotheses about better generalization across independently trained models and to tasks like **one-shot model adaptation** or **editing INRs/NeRFs**. The block-based characterization suggests a modular way to extend equivariant processing to other parameterized function families (e.g., CNNs via channel permutations), and the reported failures/limitations (initialization difficulty, architecture-specificity) are useful constraints when proposing new weight-space architectures or training schemes.