# Related Work

## Weight-Space Learning and Model Zoos

The idea that a neural network's weights carry learnable signals — about its generalization behavior, training history, or task identity — has been established by a series of works spanning datasets, architectures, and prediction tasks.

Unterthiner et al. [2020] introduce ModelZooDataset and demonstrate that per-layer weight statistics (mean, variance, spectral norms — the Ŵ_L encoder) achieve R² > 0.984 on CIFAR10-GS generalization prediction using gradient-boosted trees. This result establishes a strong baseline that is difficult to surpass with more complex encoders, and it is the primary benchmark against which we evaluate. However, Ŵ_L achieves its performance through *approximately* invariant statistics — moment-based features that do not systematically encode channel order — rather than through *architectural* invariance. The question of whether architectural invariance provides irreducible benefit over well-designed non-invariant statistics is left open.

Eilertsen et al. [2020] extend weight-space learning to classification tasks, finding that raw weight footprints encode distinguishable signals about training conditions and optimizer choices. Schürholt et al. [2021, 2022] introduce self-supervised hyper-representations and model zoo benchmarks, establishing that weight populations contain rich transferable structure. These works motivate the need for encoders that faithfully represent the *functional content* of a network's weights — but none measure the cost of permutation sensitivity on prediction quality.

## Architecturally Invariant and Equivariant Encoders

The theoretical foundation for permutation-invariant set functions is established by Zaheer et al. [2017] (Deep Sets): any permutation-invariant function on a set can be decomposed as ρ(Σφ(xᵢ)), making sum pooling the canonical invariant architecture. By construction, DeepSets sum pooling achieves OrbitVar = 0 — not approximately, but exactly, up to floating-point precision. This theorem is the backbone of our C2 encoder design.

Neural Functional Networks (NFN) [Zhou et al., 2023] extend this to *equivariant* mappings over weight spaces, introducing NF-Layers (NPLinear) with parameter sharing tied to the CNN permutation group structure and HNPPool for invariant aggregation. NFN achieves Kendall's τ = 0.934 on CIFAR-10-GS generalization prediction, outperforming simpler baselines while maintaining equivariance guarantees. Zhou et al. report performance improvements but do not measure OrbitVar — the within-orbit representational variance that our work quantifies directly.

Navon et al. [2023] (DWSNet/DWSN) derive the complete set of affine equivariant and invariant linear layers for deep weight spaces from symmetry group principles, formalizing that the correct symmetry group for CNNs requires *coupled* row-column permutations across adjacent layers — not independent per-layer permutations. This coupled structure (DWSNet Eq. 5) is a critical contribution to our experimental design: we verify that our permutation implementation satisfies this coupling with ||f_v − f_{π·v}||∞ ≤ 2e-6, confirming functional equivalence before any measurement is taken.

Kofinas et al. [2024] (ICLR oral) represent neural networks as parameter graphs and apply GNNs to learn equivariant embeddings, achieving state-of-the-art on several weight-space tasks. These approaches share the theoretical motivation for invariant/equivariant encoding but, like NFN and DWSNet, do not directly measure how non-invariance translates to prediction error through the OrbitVar → MSE_perm → R² pathway.

**Gap:** All of the above works demonstrate that invariant/equivariant encoders perform well, but none close the causal loop: *how much* representational variance exists within orbits (OrbitVar), *how much* of that propagates to prediction error (MSE_perm), and whether the downstream R² improvement can be causally attributed to these quantities.

## Permutation Symmetry in Weight Spaces

The permutation symmetry of neural networks has been studied primarily in the context of loss landscape geometry [Entezari et al., 2022; Ainsworth et al., 2022] and neural network alignment [Wang et al., 2020]. These works focus on *finding* the right permutation to align two networks (cross-model alignment), rather than on the within-model problem of measuring variance under all permutations of a single network.

Post-hoc alignment methods such as Hungarian algorithm matching (as investigated in our preliminary work with sh2) aim to reduce the effective number of distinct weight configurations by finding canonical representatives. However, within-orbit variance (OrbitVar) and cross-model variance are orthogonal: alignment reduces the latter but cannot reduce the former, since OrbitVar is measured over all permutations of a *single* network, not across networks.

The DWSNet formalism [Navon et al., 2023] provides the mathematical foundation for distinguishing these two problems, and our MSE bias-variance decomposition over permutation orbits operationalizes this distinction into a directly measurable diagnostic.

## Our Position

We occupy a novel position in this landscape: not proposing a new encoder architecture, but providing the first *empirical causal attribution* of the encoder invariance → R² relationship on a standard model zoo benchmark. Our MSE decomposition framework (MSE_res + MSE_perm) is a reusable diagnostic that can be applied to any encoder to quantify its permutation sensitivity and predict its downstream utility — independently of the specific architecture used.

The closest related measurement is the implicit comparison embedded in NFN's Kendall's τ improvement [Zhou et al., 2023], but that result conflates invariance benefits with representational capacity differences (NFN has more parameters than Ŵ_L). Our controlled comparison — CISE vs DeepSets at matched prediction capacity (same LightGBM predictor) — isolates the invariance effect directly.
