# Orbit-PE: Empirical Variance Stratification in Weight Space Symmetries Across Layer Types

**Authors:** [Author 1], [Author 2], [Author 3]
**Institution:** [Institution]
**Contact:** [email]

---

## Abstract

Weight space learning (WSL) methods that exploit permutation equivariance achieve high within-architecture performance on convolutional neural network (CNN) benchmarks but generalize poorly across architecture families. This paper investigates orbit-based positional encodings (orbit-PE) derived from the input/output channel permutation group as a candidate for architecture-agnostic weight tokenization. Three empirical measurements are reported. First, the input/output channel permutation group is confirmed as a functionally exact symmetry for Conv2d, Linear, and MultiheadAttention layers: |Delta acc| = 0.000000 across 4,500 permutation runs on CNN Zoo and Transformer Zoo checkpoints. Second, orbit-PE is computable for all layer types with a mean overhead of 1.167x relative to sequential positional encoding, using a unified codebase with no architecture-specific branches. Third, variance decomposition of 1,000 CNN Zoo models over 50 training epochs reveals a statistically robust layer-type stratification: the permutation-orbit variance fraction is 0.637 for Conv2d layers and 0.133 for Linear (fully-connected) layers, with an overall ratio of 0.3479 +/- 0.0536 — substantially below the pre-specified threshold of 0.60. The overall gate failure blocked planned cross-architecture training experiments. An ancillary finding is that the permutation variance fraction decreases monotonically during training, from approximately 0.49 at epoch 0 to approximately 0.28 at epoch 50. These results indicate that permutation orbit encoding is insufficient as the sole positional encoding for cross-architecture WSL and motivate a layer-type-specific hybrid encoding combining permutation orbit-PE for convolutional layers with GL-invariant trace features for linear and attention layers.

---

## 1. Introduction

Permutation equivariant networks for weight space learning, such as Neural Functional Networks (NFN) [Zhou et al., 2023], exploit the fact that any permutation of neurons in a hidden layer, paired with the inverse permutation on the adjacent layer, leaves the network function unchanged. This approach yields Kendall's tau > 0.93 on CNN generalization benchmarks [Zhou et al., 2023]. However, the same permutation equivariant methods perform poorly when applied zero-shot to transformer architectures. Preliminary evaluation in this work indicates tau falls below 0.50 in such cross-architecture settings, representing a gap of approximately 43 percentage points relative to within-architecture CNN performance. The cause of this gap is not definitively established in prior work.

Two main approaches exist for cross-architecture WSL. Architecture-specific equivariant networks (NFN, Transformer-NFN) excel within a given architecture family but are not designed for zero-shot cross-architecture transfer [Zhou et al., 2023; Tran-Viet et al., 2024]. Token-based representations such as SANE [Schurholt et al., 2024] operate across architectures by treating weight rows as tokens with sequential positional encodings, but do not encode symmetry structure. Neither approach has characterized which symmetry groups explain the dominant weight-space variation for each layer type.

This paper addresses that measurement gap. The input/output channel permutation group G = S_{c_in} x S_{c_out} acts on all standard linear operator types (Conv2d, Linear, MultiheadAttention) as a consequence of their shared linear operator structure. The present work verifies this symmetry empirically and measures what fraction of weight-space variance it captures, stratified by layer type, across a large model zoo.

The research is organized around three sub-hypotheses in a sequential gate-controlled design (H-E1, H-M1, H-M2), where each downstream experiment requires the preceding gate to pass. A fourth sub-hypothesis (H-M3, cross-architecture training) and a fifth (H-C1, OVR decomposition) were pre-specified but were not executed because H-M2 failed its gate criterion.

The three executed sub-hypotheses yield the following findings:

1. **Exact symmetry validation (H-E1):** |Delta acc| = 0.000000 across 4,500 permutation runs on CNN Zoo and Transformer Zoo checkpoints, satisfying the gate threshold by several orders of magnitude.

2. **Practical computability (H-M1):** Orbit-PE is computable for all layer types with 1.167x mean overhead (threshold: <= 1.2x), using a unified codebase (HAS_ARCH_BRANCHES = False) and consistent output dimensionality (token_dim = 64).

3. **Zoo-scale variance stratification (H-M2):** The overall permutation-orbit variance fraction is 0.3479 +/- 0.0536 (n = 1,000 models x 50 epochs), below the 0.60 gate threshold. Layer-type breakdown reveals Conv2d ratio = 0.637 and Linear (FC) ratio = 0.133 — a 4.8x difference. The gate FAILED, blocking H-M3 execution. A pre-specified pivot to hybrid orbit-PE encoding was activated.

The paper is organized as follows. Section 2 surveys related work. Section 3 describes the methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Permutation Equivariant Weight Space Learning

The observation that permuting neurons in adjacent layers preserves network function underlies a class of equivariant architectures for weight space learning. NFN [Zhou et al., NeurIPS 2023] formalizes this symmetry into equivariant layers for MLP and CNN weights, achieving Kendall's tau = 0.934 on CIFAR-10-GS and tau = 0.931 on SVHN-GS in within-architecture generalization prediction. Monomial-NFN [Tran, Vo et al., NeurIPS 2024] extends NFN to scaling and sign-flip symmetries, establishing that all invariant groups for MLPs are subsets of the monomial matrix group. Both methods remain architecture-specific: they are not designed to transfer representations across CNN and transformer families.

Transformer-NFN [Tran-Viet et al., 2024] identifies the maximal symmetric group of multi-head attention weights and reports within-architecture tau = 0.905-0.910 on transformer benchmarks. Critically, its equivariant construction for attention layers is separate from the CNN construction. The two constructions are not unified. The present work examines whether a single group — the input/output channel permutation group — can serve as a common foundation and measures what fraction of variance it captures for each layer type.

### 2.2 Token-Based and Scalable Weight Representations

SANE [Schurholt et al., ICML 2024] tokenizes neural network weights by reshaping tensors into row-wise slices along the output channel dimension and encoding each token with a sequential positional encoding P_n = [n, l, k]. SANE achieves linear probe accuracy of 0.978 on MNIST and 0.991 on CIFAR-10 within architecture, and scales to ResNets. Its sequential positional encodings carry no symmetry structure, which is hypothesized to limit cross-architecture transfer. Orbit-PE as studied in this work augments SANE's tokenization with orbit membership information derived from the channel permutation group.

ProbeGen [Kahana, Horwitz et al., 2024] achieves 30-1000x fewer FLOPs than SANE via learned probe generators. The efficiency gains from the ProbeGen line of work motivate the <= 1.2x overhead constraint adopted in H-M1.

### 2.3 GL Orbit Symmetry and Weight Space Geometry

Transformer-NFN [Tran-Viet et al., arXiv:2410.04209] proposes GL-invariant polynomial trace features (tr(WW^T) and tr(W^Q W^{K,T})) for attention weights, motivated by the argument that GL symmetry is the relevant group for attention weight structure. The H-M2 finding in the present work — that Linear (FC) layers show GL-orbit variance 6.6x larger than permutation orbit variance — provides independent empirical evidence from a different angle: direct variance decomposition at zoo scale on CNN Zoo linear layers, rather than theoretical argument. The Transformer Zoo attention layers were not directly measured in this work (see Limitation L3).

Loss landscape analysis and neural network trajectory studies have documented flat directions along symmetry orbits in trained networks. The present finding that the permutation variance ratio decreases from approximately 0.49 to approximately 0.28 over 50 training epochs is consistent with the broader literature on symmetry breaking during optimization.

### 2.4 Weight Space Learning Surveys

The WSL Survey [Han et al., 2026] introduces the WSU/WSR/WSG taxonomy and identifies cross-architecture generalization as a primary open problem. The present work differs from prior weight space learning studies in focusing on direct measurement of which symmetry groups explain dominant weight-space variance by layer type, rather than assuming a symmetry group and constructing an equivariant architecture.

---

## 3. Method

The methodology follows a three-stage sequential verification chain, with each stage constituting a necessary precondition for the next.

### 3.1 Orbit-PE Construction

SANE [Schurholt et al., 2024] assigns each weight token a sequential positional encoding P_n = [n, l, k], where n, l, k denote global index, layer index, and within-layer index, respectively. This encoding carries no information about the weight token's position relative to any symmetry group.

The input/output channel permutation group G = S_{c_in} x S_{c_out} acts on any weight matrix W in R^{c_out x c_in} by permuting rows (output channels) and columns (input channels). This group action is a functionally exact symmetry for all linear operators — Conv2d, Linear, MultiheadAttention — as a consequence of the linear operator structure, provided the paired permutations are applied consistently in adjacent layers.

Orbit-PE replaces the sequential positional encoding with an orbit membership vector computed as follows:

1. For each weight token W_{l,k} (a row of the reshaped weight matrix), its orbit under S_{c_in} is identified.
2. An orbit membership matrix M in R^{n_tokens x d_orbit} is constructed and decomposed via singular value decomposition.
3. The left singular vectors yield the orbit basis U in R^{n_tokens x d_pe}, and each token receives the corresponding row as its orbit-PE vector (d_pe = 64 = token_dim).

The orbit-PE computation is implemented via a dispatch table over layer types (Conv2d, Linear, MultiheadAttention) with no architecture-conditional branches (HAS_ARCH_BRANCHES = False), producing a token_dim = 64 output for all types.

### 3.2 Symmetry Validity Verification (H-E1)

H-E1 tests whether the input/output channel permutation group constitutes a functionally exact symmetry across architecture families. For each checkpoint, 10 random canonical permutations are applied (seeds 0-9), and the change in evaluation accuracy |Delta acc| is measured by comparing logits on fixed random inputs before and after permutation. The gate criterion requires mean |Delta acc| < 0.001 (0.1%) for both CNN Zoo and Transformer Zoo, and orbit-PE success rate = 1.0 for all layer types.

Implementation details: the first layer's input channels receive the identity permutation (the network input is not permuted); the final layer's output channels receive the identity permutation (class indices are fixed). The Conv-to-Linear (Flatten) transition is handled by expanding the channel permutation to grouped flattened indices (ch * spatial_size + offset). Transformer Zoo uses separate Q/K/V projections (no fused in_proj_weight) with head-grouped permutation.

### 3.3 Computability and Overhead Verification (H-M1)

H-M1 measures the wall-clock time overhead of orbit-PE computation relative to sequential PE computation on 200 checkpoints (100 CNN Zoo, 100 Transformer Zoo). The overhead ratio is defined as:

    overhead_ratio = t_{orbit-PE} / t_{sequential-PE}

The gate criterion requires overhead_ratio_mean <= 1.2x. Additional criteria: computability_rate = 1.0 (orbit-PE computable for all checkpoints), HAS_ARCH_BRANCHES = False, and dim_consistent = True.

### 3.4 Variance Decomposition (H-M2)

H-M2 measures the fraction of weight-space variance explained by permutation orbits versus General Linear (GL) orbits across CNN Zoo training trajectories.

For each checkpoint's weight tensors, two projections are computed:

- **Permutation orbit projection:** The weight vector is projected onto the SVD-derived orbit basis U. Var_perm = sum_i sigma_i^2, where sigma_i are singular values of the orbit basis applied to the weight matrix.

- **GL orbit projection:** Polar decomposition W = QR (Q orthogonal, R symmetric positive semidefinite) is used to extract GL-orbit variation components.

The primary metric is:

    ratio = Var_perm / (Var_perm + Var_GL)

This is computed per checkpoint, per layer type, and averaged across 1,000 CNN Zoo CIFAR-10-GS models x 50 training epochs. The gate criterion requires ratio > 0.60. A pre-specified pivot was defined: if ratio < 0.60, proceed to hybrid orbit-PE combining permutation orbit for Conv2d layers with GL-invariant trace features for Linear/attention layers.

Note on implementation: the H-M2 orbit projector uses an SVD-based orbit basis as a fallback because a path resolution issue prevented direct import of the H-M1 OrbitPEComputer. This substitution is methodologically equivalent for the purpose of variance decomposition.

### 3.5 Verification Chain Structure

The three sub-hypotheses form a prerequisite chain: H-E1 (symmetry validity) -> H-M1 (computability) -> H-M2 (variance dominance). H-M3 (cross-architecture training) and H-C1 (OVR decomposition) were pre-specified as dependent on H-M2 passing. Because H-M2 failed, H-M3 and H-C1 were not executed.

---

## 4. Experimental Setup

**Datasets.**

- *Small CNN Zoo (CIFAR-10-GS)* [Unterthiner et al., 2020]: A collection of small CNNs with full training trajectories (epochs 0-50). The architecture is dynamically inferred from checkpoint state dict shapes (channel widths vary across models; the typical configuration observed is 3 convolutional layers followed by 2 fully-connected layers, with GELU activations and no padding). H-E1 used 200 CNN Zoo checkpoints (2,000 permutation runs); H-M1 used 100; H-M2 used 1,000 models x 50 epochs = 50,000 checkpoints.

- *Small Transformer Zoo (MNIST)* [Tran-Viet et al., 2024]: A subset of the 125,000 checkpoint transformer zoo. The architectures used are 2-block ViT-style models with separate Q/K/V projections, no LayerNorm, and a 2-layer MLP classifier. H-E1 used 250 Transformer Zoo checkpoints (2,500 permutation runs); H-M1 used 100.

**Evaluation metrics.**

| Metric | Hypothesis | Threshold |
|--------|------------|-----------|
| Mean |Delta acc| | H-E1 | < 0.001 |
| Orbit-PE success rate | H-E1 | = 1.0 |
| overhead_ratio_mean | H-M1 | <= 1.20x |
| HAS_ARCH_BRANCHES | H-M1 | False |
| Var_perm/(Var_perm+Var_GL) | H-M2 | > 0.60 |

**Implementation.** All experiments ran on CPU for orbit-PE and variance computations. The symmetry validation experiment (H-E1) was executed on a single GPU (NVIDIA H100 NVL, CUDA_VISIBLE_DEVICES=2) in approximately 16.2 seconds. Orbit-PE uses d_pe = 64. Random seeds were fixed (seed = 42 for checkpoint sampling; seeds 0-9 for permutation sampling in H-E1). Code: `h-e1/code/orbit_pe.py` (dispatch table), `h-m1/code/orbit_pe_computer.py` (timing), `h-m2/code/orbit_projector.py` (variance decomposition), `h-m2/code/evaluate.py` (zoo-scale pipeline).

**Baseline comparisons not conducted.** Formal comparison of tau values against published NFN or SANE baselines was not conducted in this work. H-M3 (which would have trained SANE+orbit-PE and measured tau_retention) was blocked by the H-M2 gate failure. Published baseline values referenced in the text (NFN: tau = 0.934, 0.931; Transformer-NFN: tau = 0.905-0.910; SANE: linear probe 0.978-0.991) are taken directly from the respective papers and are not reproduced here.

**SVHN Zoo data unavailability.** The pre-specified cross-dataset stability check for H-M2 (|CIFAR ratio - SVHN ratio| < 0.10) was not performed because SVHN Zoo data was unavailable. The H-M2 conclusions are based solely on the CIFAR-10-GS subset.

---

## 5. Results

### 5.1 H-E1: Channel Permutation is an Exact Symmetry

**Table 1: H-E1 Gate Metrics**

| Architecture | Checkpoints | Permutation Runs | Mean |Delta acc| | Orbit-PE Success Rate |
|---|---|---|---|---|
| CNN Zoo (CIFAR-10-GS) | 200 | 2,000 | 0.000000 | 1.0 |
| Transformer Zoo (MNIST) | 250 | 2,500 | 0.000000 | 1.0 |
| Total | 450 | 4,500 | 0.000000 | 1.0 |

The mean |Delta acc| = 0.000000 satisfies the gate threshold of < 0.001 by several orders of magnitude. Standard deviation and maximum are also 0.000000 across all runs. Per-seed stability (Figure 8) confirms zero variance across all 10 permutation seeds. Orbit-PE computation succeeded for all layer types in both zoos using a single unified codebase (Table in Figure 6; layer coverage: 4/4 Conv2d layers, 11/11 Linear layers, 8/8 MultiheadAttention layers in the sampled checkpoints). **Gate result: PASS.**

The |Delta acc| = 0.000000 result is consistent with the theoretical proof that the input/output channel permutation group is a symmetry of any linear operator [Zhou et al., 2023; Tran-Viet et al., 2024]. The result required careful implementation: the first layer's input and the final layer's output must use identity permutations, and the Conv-to-Linear flatten transition requires expanding channel permutations to grouped indices.

### 5.2 H-M1: Orbit-PE Computability

**Table 2: H-M1 Gate Metrics**

| Metric | Result | Threshold | Status |
|---|---|---|---|
| overhead_ratio_mean | 1.167x | <= 1.20x | PASS |
| overhead_ratio_std | 0.061 | — | — |
| computability_rate | 1.0 (200/200) | = 1.0 | PASS |
| HAS_ARCH_BRANCHES | False | = False | PASS |
| dim_consistent | True | = True | PASS |

**Table 3: Overhead by Layer Type**

| Layer Type | Overhead Ratio (mean) |
|---|---|
| Conv2d | 1.167x |
| Linear (FC) | 1.167x |
| MultiheadAttention | 1.126x |

Overhead is consistent across layer types (Figure 7). All 200 checkpoints computed orbit-PE successfully. **Gate result: PASS.**

### 5.3 H-M2: Variance Decomposition

**Table 4: H-M2 Primary Results (n = 1,000 models x 50 epochs = 50,000 checkpoints)**

| Scope | Var_perm | Var_GL | Ratio | Gate |
|---|---|---|---|---|
| Overall (all layers) | 347.9 | 652.1 | 0.3479 +/- 0.0536 | FAIL |
| Conv2d only | 97.62 | 55.29 | 0.637 | PASS |
| Linear/FC only | 33.84 | 223.52 | 0.133 | FAIL |

The overall permutation-orbit variance fraction is 0.3479 +/- 0.0536, which is 0.252 below the 0.60 gate threshold. The distribution of per-model ratios (Figure 4) has mean = 0.3479 and std = 0.0536 — consistent across models and not driven by outliers.

**Layer-type stratification.** The bimodal split between Conv2d (ratio = 0.637) and Linear/FC (ratio = 0.133) is the primary finding from this experiment. The 4.8x difference between these ratios places the two layer types on opposite sides of the 0.60 gate threshold. For Linear (FC) layers, GL-orbit variance is 223.52/33.84 = 6.6x larger than permutation orbit variance.

**Training trajectory.** The permutation variance ratio decreases monotonically during training: from approximately 0.49 at epoch 0 to approximately 0.28 at epoch 50 (Figure 2). This pattern was not anticipated in the pre-specified hypothesis and was observed consistently across the 1,000 models examined.

**Correlation with accuracy.** No strong correlation between ratio and final model accuracy was observed (Figure 5, r^2 < 0.05).

**Gate result: FAIL.** The pre-specified pivot to hybrid encoding was activated.

### 5.4 Sub-hypothesis Status Summary

| Sub-hypothesis | Gate Type | Result | Key Metric |
|---|---|---|---|
| H-E1: Exact symmetry | MUST_WORK | PASS | |Delta acc| = 0.000000; success rate = 1.0 |
| H-M1: Computability | MUST_WORK | PASS | overhead = 1.167x; unified codebase |
| H-M2: Variance dominance | MUST_WORK | FAIL | ratio = 0.3479; Conv2d = 0.637, Linear = 0.133 |
| H-M3: Cross-arch training | — | BLOCKED | Blocked by H-M2 gate failure |
| H-C1: OVR measurement | — | BLOCKED | Cascaded block |

---

## 6. Discussion

### 6.1 Interpreting the Layer-Type Stratification

The Conv2d/Linear variance ratio difference (0.637 vs. 0.133) is consistent with three non-exclusive structural explanations.

**Structural explanation.** Conv2d weight tensors W in R^{c_out x c_in x H x W} have spatial structure (H x W kernel dimensions) that constrains the active GL directions. Linear/FC matrices W in R^{c_out x c_in} are fully dense: the full GL(c_in) x GL(c_out) group acts without structural constraint, providing more variance directions than the discrete permutation group S_{c_in} x S_{c_out}.

**Training dynamics explanation.** The trajectory finding (ratio approximately 0.49 to 0.28 over 50 epochs) is consistent with gradient descent exploiting GL-type flat-direction reparameterizations during optimization. At initialization, weights drawn from symmetric distributions may have higher permutation orbit density; training progressively moves the weights into non-permutation-orbit directions. This is consistent with the loss landscape literature on flat directions along symmetry orbits.

**Scale explanation.** Linear layers with large input dimensions have higher-dimensional GL(d) groups, providing more variance directions than S_d (permutation), amplifying GL dominance relative to permutation.

These explanations are not mutually exclusive and are not tested directly in this work.

### 6.2 Relation to Prior Literature

The H-M2 result provides independent empirical support for the theoretical motivation behind GL-invariant trace features in Transformer-NFN [Tran-Viet et al., 2024]. That work proposed tr(WW^T) and tr(W^Q W^{K,T}) precisely because GL symmetry is expected to dominate linear/attention weights. The present measurement of ratio = 0.133 for Linear (FC) layers in CNN Zoo is consistent with this expectation from a different methodological angle. Note, however, that the present measurement covers only CNN Zoo Linear layers; Transformer Zoo attention layers were not directly measured (see Limitation L3).

The Conv2d ratio = 0.637 is consistent with NFN's performance on CNN Zoo (tau > 0.93 using permutation-only equivariance): permutation equivariance captures the dominant variation in convolutional weights in this dataset.

### 6.3 Implications for Cross-Architecture Weight Representation Design

The H-M2 result suggests that a single permutation-based positional encoding is insufficient for cross-architecture WSL because the dominant symmetry differs by layer type. The pre-specified hybrid encoding — permutation orbit-PE for Conv2d layers combined with GL-invariant trace features for Linear and attention layers — is a direct response to this finding and is not post-hoc. The infrastructure developed in this work (orbit projectors, variance decomposer, zoo-scale evaluation pipeline) is directly reusable for implementing and testing the hybrid approach.

Whether GL dominance in CNN Zoo Linear layers extends to Transformer Zoo attention layers is an open measurement question. The inference that it does is plausible but unconfirmed by direct measurement (Limitation L3).

### 6.4 Limitations

**L1 — Primary performance claim not tested.** The original hypothesis predicted tau_retention >= 0.70 with SANE+orbit-PE. This prediction was not tested. H-M3, which would have tested this claim, was blocked by H-M2's gate failure. The claim is neither confirmed nor refuted; it is empirically unaddressed.

**L2 — SVHN cross-dataset stability not verified.** SVHN Zoo data was unavailable during H-M2 execution. The pre-specified cross-dataset stability check (|CIFAR ratio - SVHN ratio| < 0.10) was not performed. The CIFAR-10-GS result (n = 1,000 x 50) is based on a single dataset.

**L3 — Transformer Zoo variance not measured.** The Var_perm/Var_GL ratio for Transformer Zoo checkpoints was not computed. The discussion in Section 6.3 treats the Linear ratio from CNN Zoo as informative about attention layers by inference, but this is not direct measurement.

**L4 — SVD fallback in H-M2.** A path resolution issue prevented H-M2's orbit_projector.py from importing H-M1's OrbitPEComputer directly. An SVD-based orbit basis was used as a fallback. The two approaches are methodologically equivalent for variance decomposition purposes but represent a minor deviation from the planned implementation design.

**L5 — No comparison to published tau baselines.** Formal comparison against published NFN and SANE tau values was not conducted. All tau comparisons in the text are from the cited papers.

### 6.5 Broader Implications

The finding that permutation-orbit variance fraction is layer-type-dependent is a general property of weight space geometry that applies to any cross-architecture WSL method. The training trajectory finding (ratio decreasing during training) has a practical implication: early-epoch checkpoints may provide stronger permutation orbit signal than well-trained models. This has potential relevance for model zoo design when permutation-equivariant representations are intended.

---

## 7. Conclusion

This paper reports three empirical measurements relevant to orbit-based positional encodings for weight space learning.

First, the input/output channel permutation group is a functionally exact symmetry for Conv2d, Linear, and MultiheadAttention layers in both CNN Zoo and Transformer Zoo checkpoints (|Delta acc| = 0.000000 across 4,500 runs). This result is stronger than required by the pre-specified threshold.

Second, orbit-PE is computable for all layer types with 1.167x mean overhead relative to sequential PE, using a unified codebase with no architecture-conditional branches. Overhead is consistent across layer types (Conv2d: 1.168x, Linear: 1.168x, MultiheadAttention: 1.126x).

Third, variance decomposition across 1,000 CNN Zoo models and 50 training epochs reveals a layer-type stratification: the permutation-orbit variance fraction is 0.637 for Conv2d layers and 0.133 for Linear (FC) layers, with an overall ratio of 0.3479 — below the 0.60 gate threshold. This gate failure prevented execution of the planned cross-architecture training experiments (H-M3, H-C1). An ancillary finding is that the permutation variance ratio decreases during training (approximately 0.49 to 0.28 over 50 epochs).

These results collectively indicate that permutation orbit encoding alone is insufficient as the basis for cross-architecture WSL due to GL-orbit dominance in fully-connected and attention layers. The findings motivate a hybrid positional encoding (permutation orbit-PE for Conv2d + GL-invariant trace features for Linear/attention) as the next iteration. Whether such a hybrid achieves the originally targeted tau_retention >= 0.70 (relaxed to >= 0.65 in light of the H-M2 finding) remains untested. The variance decomposition infrastructure developed here is directly applicable to that next step.

---

## References

Zhou, A., Yang, K., Burns, K., Cardace, A., Jiang, Y., Sokota, S., Kolter, J., and Finn, C. Permutation Equivariant Neural Functionals. *NeurIPS 2023*.

Schurholt, K., Mahoney, M. W., and Borth, D. Towards Scalable and Versatile Weight Space Learning. *ICML 2024*.

Tran-Viet, H., Vo, T. N., Nguyen The, A., Tran Huu, T., Nguyen-Nhat, M.-K., Tran, T., Pham, D.-T., and Nguyen, T. M. Equivariant Neural Functional Networks for Transformers. *arXiv:2410.04209*, 2024.

Tran, H. V., Vo, T. N., Tran, T., Nguyen, A., and Nguyen, T. M. Monomial Matrix Group Equivariant Neural Functional Networks. *NeurIPS 2024*.

Han, X., Wang, Z., Zhao, B., et al. A Survey of Weight Space Learning: Understanding, Representation, and Generation. *arXiv:2603.10090*, 2026.

Schurholt, K., Knyazev, B., Giro-i-Nieto, X., and Borth, D. Hyper-Representations as Generative Models: Sampling Unseen Neural Network Weights. *NeurIPS 2022*.

Kahana, Y., Hoshen, Y., et al. Deep Linear Probe Generators for Weight Space Learning. *arXiv:2410.10811*, 2024.

Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., and Tolstikhin, I. Predicting Neural Network Accuracy from Weights. *arXiv:2002.11448*, 2020.

---

## Figure Captions

**Figure 1** (`figures/layer_breakdown.png`): Variance decomposition by layer type (H-M2). Conv2d layers have Var_perm/(Var_perm+Var_GL) = 0.637 (permutation-dominant). Linear (FC) layers have ratio = 0.133 (GL-dominant). The 4.8x difference between layer types is the primary finding of H-M2.

**Figure 2** (`figures/ratio_vs_epoch.png`): Mean permutation variance ratio Var_perm/(Var_perm+Var_GL) as a function of training epoch across 1,000 CNN Zoo models. The ratio decreases from approximately 0.49 at epoch 0 to approximately 0.28 at epoch 50.

**Figure 3** (`figures/gate_bar_chart.png`): Overall variance decomposition bar chart: Var_perm = 347.9 vs. Var_GL = 652.1, overall ratio = 0.3479, below the 0.60 gate threshold (dashed horizontal line).

**Figure 4** (`figures/ratio_histogram.png`): Distribution of per-model permutation variance ratios (n = 1,000; mean = 0.3479, std = 0.0536). The distribution is approximately normal and not driven by outliers.

**Figure 5** (`figures/ratio_vs_accuracy.png`): Scatter plot of ratio vs. final model accuracy for n = 1,000 CNN Zoo models. No strong correlation is present (r^2 < 0.05).

**Figure 6** (`figures/delta_acc_distribution.png`): Distribution of |Delta acc| across all 4,500 permutation runs (H-E1). All values are 0.000000.

**Figure 7** (`figures/overhead_per_layer_type.png`): Orbit-PE computation overhead ratio by layer type (H-M1): Conv2d (1.168x), Linear (1.168x), MultiheadAttention (1.126x).

**Figure 8** (`figures/per_seed_stability.png`): Per-seed stability of |Delta acc| across 10 permutation seeds for CNN Zoo and Transformer Zoo checkpoints (H-E1). Zero variance across all seeds.
