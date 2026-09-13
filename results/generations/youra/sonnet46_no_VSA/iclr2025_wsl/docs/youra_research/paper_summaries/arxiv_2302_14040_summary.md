---
source_paper: "arxiv_2302_14040.md"
generated_at: "2026-08-03T17:31:42.048232"
model: "openai/gpt-5.2"
summary_chars: 14083
---

# Permutation Equivariant Neural Functionals

## Key Metadata
- **Authors:** Allan Zhou et al.
- **Year:** 2023
- **Venue:** NeurIPS 2023
- **Core Contribution:** Introduces permutation-equivariant **Neural Functional Networks (NFNs)** via novel **NF-Layers** that encode neuron-permutation symmetries of feedforward networks, enabling effective learning on tasks where inputs are other networks’ weights/gradients/masks.

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
Neural networks increasingly need to **process other networks’ weights/gradients/masks** for tasks like learned optimization, extracting information from implicit neural representations (INRs), network editing, and policy evaluation. A key difficulty is that weight tensors of feedforward networks exhibit **neuron permutation symmetries** (hidden units have no inherent order), so naïvely processing weights with standard MLPs can waste capacity and data. The paper’s gap: few unifying architecture principles for “networks over networks.” The authors propose designing neural functionals by **hard-coding permutation equivariance/invariance** into the architecture via specialized linear layers (NF-Layers) derived from group actions and equivariant parameter sharing.

### Methodology
The paper formalizes weight-space objects as \(U=(W,v)\) for an \(L\)-layer feedforward net with widths \((n_0,\dots,n_L)\), weights \(W^{(i)}\in\mathbb{R}^{n_i\times n_{i-1}}\), and biases \(v^{(i)}\in\mathbb{R}^{n_i}\). It defines a neuron-permutation group action \(\sigma=(\sigma_0,\dots,\sigma_L)\) (NP) acting as simultaneous row/column permutations (and bias permutations):
\[
[\sigma W]^{(i)}_{jk}=W^{(i)}_{\sigma_i^{-1}(j),\,\sigma_{i-1}^{-1}(k)},\quad
[\sigma v]^{(i)}_{j}=v^{(i)}_{\sigma_i^{-1}(j)} \tag{1}
\]
and extends this to multi-channel weight-space features \(U^c\) (channels stored in the last dimension). The goal is to build \(f:U^{c_i}\to U^{c_o}\) that is **\(S\)-equivariant** (\(\sigma f(U)=f(\sigma U)\)) or invariant.

**Core building block (linear equivariant NF-Layer).** Starting from a generic linear layer \(T(\cdot;\theta):\mathrm{vec}(U)\mapsto \theta\,\mathrm{vec}(U)\), the authors derive the most general form satisfying equivariant parameter sharing (via orbit partitioning under the group action). Ignoring biases for exposition, the resulting NF-Layer \(H:W^{c_i}\to W^{c_o}\) computes each output tensor entry as a structured combination of (i) global sums, (ii) row/column sums, (iii) adjacent-layer couplings, and (iv) a pointwise term:
\[
H(W)^{(i)}_{jk}
=
\Big(\sum_s a_{i,s} W^{(s)}_{\star,\star}\Big)
+ b_{i,i} W^{(i)}_{\star,k}
+ b_{i,i-1} W^{(i-1)}_{k,\star}
+ c_{i,i} W^{(i)}_{j,\star}
+ c_{i,i+1} W^{(i+1)}_{\star,j}
+ d_i W^{(i)}_{jk}. \tag{2}
\]
Here \(\star\) denotes summation/averaging over the corresponding permuted axis. In the multi-channel case, each scalar parameter becomes a matrix in \(\mathbb{R}^{c_o\times c_i}\). They prove: (1) \(H\) is \(S\)-equivariant; (2) **any** linear \(S\)-equivariant map \(T:U^{c_i}\to U^{c_o}\) can be expressed by some parameters \((a,b,c,d)\) (i.e., \(H\) is a complete characterization for NP-equivariant linear maps). Stacking NF-Layers with pointwise nonlinearities yields an equivariant NFN because pointwise nonlinearities preserve equivariance.

**Two symmetry regimes.**
- **NP (Neuron Permutation):** allows permuting *all* layers including input/output; yields more parameter-efficient \(H\) with parameter count \(O(c_i c_o L^2)\).
- **HNP (Hidden Neuron Permutation):** only hidden layers permutable; yields a richer but potentially expensive layer \(\tilde H\) with \(O\!\left(c_i c_o (L+n_0+n_L)^2\right)\) parameters (quadratic in input/output dims), sometimes infeasible.

**Invariant heads.** For tasks requiring invariance \(f:U^c\to\mathbb{R}\), they compose several equivariant NF-Layers then apply an invariant pooling layer \(P:U\to\mathbb{R}^{2L}\) that averages/sums along all permutation-symmetric axes:
\[
P(U)=\big(W^{(1)}_{\star,\star},\dots,W^{(L)}_{\star,\star},\, v^{(1)}_{\star},\dots,v^{(L)}_{\star}\big).
\]
An MLP can then map \(P(\cdot)\) to the final prediction.

**CNN extension.** For convolutional layers, channels are permutable but spatial filter dimensions are not. They “fold” spatial/filter dimensions into the channel dimension (analogous to multi-channel features) so \(H\) applies directly to CNN weight spaces. For CNNs with global pooling before FC layers, the same action definition remains consistent.

**IO-encoding to break NP symmetry.** Because NP incorrectly assumes input/output neurons are unordered, they add learned or sinusoidal positional embeddings to columns of \(W^{(1)}\) and rows of \(W^{(L)}\) and \(v^{(L)}\), breaking input/output symmetry while retaining the efficient NP layer.

**Ablation layer.** A pointwise-only variant uses only the last term of Eq. (2): \(H(W)^{(i)}_{jk}:=d_i W^{(i)}_{jk}\), denoted **NFNPT**, removing cross-weight interactions.

(Training hyperparameters such as optimizer, LR, batch size, epochs are not specified in the provided excerpt; several experiment sections describe objectives but omit full schedules.)

### Experiments & Results
They evaluate permutation-equivariant NFNs across four tasks; NFNs are denoted **NFN\(_\text{NP}\)** or **NFN\(_\text{HNP}\)** depending on the symmetry assumption in the NF-Layer. Baselines include (i) **STATNN** (Unterthiner et al. 2020) using handcrafted weight statistics for generalization prediction; (ii) 3-layer **MLP** with ReLU and **1000 hidden units per layer**, and **MLP\(_\text{Aug}\)** with permutation augmentation; and (iii) **inr2vec** for 3D INR classification.

**(1) Predict CNN generalization from weights (invariant).** Dataset: **Small CNN Zoo** [61], subsets **CIFAR-10-GS** and **SVHN-GS** (thousands of trained CNN weight snapshots; exact counts not in excerpt). Metric: **Kendall’s \(\tau\)** rank correlation between predicted and true test accuracy. Results (Table 2): NFN\(_\text{HNP}\) is best.
- CIFAR-10-GS: NFN\(_\text{HNP}\) **0.934 ± 0.001**, NFN\(_\text{NP}\) 0.922 ± 0.001, STATNN 0.915 ± 0.002  
- SVHN-GS: NFN\(_\text{HNP}\) **0.931 ± 0.005**, NFN\(_\text{NP}\) 0.856 ± 0.001, STATNN 0.843 ± 0.000  
Interpretation: direct weight processing with correct symmetry improves over handcrafted features.

**(2) Classify INR content from weights (invariant).** Data: datasets of **SIREN** INRs encoding images (**MNIST**, **FashionMNIST**, **CIFAR-10**) and 3D shapes (**ShapeNet-10**, **ScanNet-10**), split into train/val/test (ratios not provided). Task: predict class label from INR weights only. Metric: accuracy (%), report standard error over 3 runs.
Main results (Tables 3–4): equivariant NFNs dramatically outperform MLP baselines (even with permutation augmentation) and outperform inr2vec on 3D.
- MNIST-10 test acc: NFN\(_\text{NP}\) **92.9 ± 0.218**, NFN\(_\text{HNP}\) 92.5 ± 0.071, MLP 14.5 ± 0.035, MLP\(_\text{Aug}\) 21.0 ± 0.172
- FashionMNIST test acc: NFN\(_\text{NP}\) **75.6 ± 1.07**, NFN\(_\text{HNP}\) 72.7 ± 1.53, MLP 12.5 ± 0.111, MLP\(_\text{Aug}\) 15.9 ± 0.181
- CIFAR-10 test acc: NFN\(_\text{NP}\) **46.6 ± 0.072**, NFN\(_\text{HNP}\) 44.1 ± 0.471, MLP 16.9 ± 0.250, MLP\(_\text{Aug}\) 18.9 ± 0.432
- ShapeNet-10: NFN\(_\text{NP}\) **88.7 ± 0.461**, NFN\(_\text{HNP}\) 86.9 ± 0.860, MLP 25.4 ± 0.121, MLP\(_\text{Aug}\) 33.8 ± 0.126, inr2vec 39.1 ± 0.385
- ScanNet-10: NFN\(_\text{NP}\) **65.9 ± 1.10**, NFN\(_\text{HNP}\) 64.1 ± 0.572, MLP 32.9 ± 0.351, MLP\(_\text{Aug}\) 45.5 ± 0.126, inr2vec 38.2 ± 0.409
Notably, MLPs struggle even to fit training data (per appendix note), suggesting symmetry-inductive bias is crucial.

**(3) Predict “winning ticket” sparsity masks from initialization (equivariant).** They learn to map an initialization \(U_0\) to a binary mask \(M\in\{0,1\}^{\dim(U)}\) matching a winning ticket found by **one step of IMP** at sparsity \(P_m=0.95\). Model: a **conditional VAE (cVAE)** that generates masks conditioned on \(U_0\). Evaluation: train the pruned network and report downstream **test accuracy**; compare to Dense, IMP-derived ticket, Random mask (Bernoulli\((1-P_m)\)), and NFN variants. Results (Table 5; standard error over initializations):
- CIFAR-10 (CNN): Dense 63.1 ± 0.06; IMP 44.0 ± 0.06; Random 21.1 ± 0.26; NFN\(_\text{NP}\) 41.4 ± 0.08; **NFNPT 42.6 ± 0.07**
- MNIST (MLP): Dense 97.8 ± 0.0; IMP 96.2 ± 0.04; Random 89.6 ± 0.36; NFN\(_\text{NP}\) 94.8 ± 0.01; **NFNPT 95.0 ± 0.01**
Takeaway: at high sparsity, learned mask predictors approach IMP performance; surprisingly, the pointwise ablation NFNPT matches/slightly beats NFN\(_\text{NP}\), suggesting limited need for cross-weight interactions here (further analysis in appendix).

**(4) Weight-space “style editing” of INRs (equivariant).** Goal: given an INR (SIREN) encoding an image, an NFN outputs edited weights whose rendered image matches a target image transformation. Two tasks: **Dilate** MNIST digits and **Contrast** increase on CIFAR-10. Supervision: image-processing libraries (OpenCV) generate “ground-truth” transformed images; objective minimizes **test MSE** between images rendered from edited INR vs transformed images. Results (Table 6; lower is better):
- Contrast (CIFAR-10) MSE: MLP 0.031, MLP\(_\text{Aug}\) 0.029, NFNPT 0.029, NFN\(_\text{HNP}\) 0.021, **NFN\(_\text{NP}\) 0.020**
- Dilate (MNIST) MSE: MLP 0.306, MLP\(_\text{Aug}\) 0.307, NFNPT 0.197, NFN\(_\text{HNP}\) 0.070, **NFN\(_\text{NP}\) 0.068**
Here, unlike winning-ticket prediction, **NFNPT is much worse**, indicating the need for modeling interactions among weights/layers for geometric edits.

**Compact main-results table (from provided excerpt).**

| Task / Dataset | Metric | Best method | Best value | Key baselines |
|---|---:|---|---:|---|
| CNN generalization (CIFAR-10-GS) | Kendall’s \(\tau\) | NFN\(_\text{HNP}\) | **0.934 ± 0.001** | NFN\(_\text{NP}\) 0.922; STATNN 0.915 |
| CNN generalization (SVHN-GS) | Kendall’s \(\tau\) | NFN\(_\text{HNP}\) | **0.931 ± 0.005** | NFN\(_\text{NP}\) 0.856; STATNN 0.843 |
| INR cls (MNIST-10) | Acc % | NFN\(_\text{NP}\) | **92.9 ± 0.218** | MLP 14.5; MLP\(_\text{Aug}\) 21.0 |
| INR cls (ShapeNet-10) | Acc % | NFN\(_\text{NP}\) | **88.7 ± 0.461** | inr2vec 39.1; MLP\(_\text{Aug}\) 33.8 |
| Winning tickets (CIFAR-10, 95% sparse) | Acc % | NFNPT | **42.6 ± 0.07** | IMP 44.0; Random 21.1 |
| INR editing (Dilate MNIST) | MSE | NFN\(_\text{NP}\) | **0.068** | MLP 0.306; NFNPT 0.197 |

(Statistical significance tests, CIs beyond standard errors, and computational cost such as GPU-hours are not reported in the provided excerpt.)

### Discussion & Conclusion
Encoding neuron permutation symmetries via equivariant parameter sharing yields NFNs that are consistently stronger than non-equivariant MLP baselines and handcrafted feature methods across weight-space tasks. The NP vs HNP tradeoff is central: NP layers are far more parameter-efficient and, with IO-encoding, can match or exceed HNP on several tasks; HNP can be better when true input/output ordering matters (e.g., CNN generalization). Limitations include potentially large activation sizes for NF-Layers (scaling concerns) and lack of extensions to more complex architectures (e.g., ResNets, Transformers).

## Key Contributions
- **Permutation-equivariant NF-Layers:** Derives and characterizes a linear **NP-equivariant** NF-Layer \(H\) (Eq. 2) via equivariant parameter sharing, and notes the richer **HNP-equivariant** variant \(\tilde H\).
- **Scalable symmetry design choices:** Introduces the **NP setting** for efficiency plus **IO-encoding** to break inappropriate input/output symmetry while retaining efficient equivariance.
- **Empirical validation on diverse weight-space tasks:** Demonstrates strong performance on CNN generalization prediction, INR classification, winning-ticket mask prediction, and INR weight-space editing—often with large margins over MLP(+augmentation) and other baselines.

## Potential Relevance
This paper provides a concrete recipe for building **weight-space models** with correct permutation inductive biases, which is directly relevant to hypotheses about when and why “networks over networks” should generalize. The NF-Layer form (Eq. 2) suggests specific interaction pathways (global/row/col/adjacent-layer couplings) that can be ablated to test which weight statistics drive downstream predictability/editability. The contrasting findings—NFNPT suffices for winning-ticket prediction but fails for INR editing—offer a useful negative/diagnostic result about when cross-weight interactions are essential.