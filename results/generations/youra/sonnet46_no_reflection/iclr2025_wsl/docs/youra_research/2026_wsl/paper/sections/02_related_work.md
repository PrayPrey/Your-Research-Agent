# Related Work

## Permutation Equivariant Weight Space Learning

The foundational insight that neural network weights possess permutation symmetries dates to the
observation that any permutation of neurons in a hidden layer, matched with the corresponding
inverse permutation in the adjacent layer, preserves network function. Neural Functional Networks
(NFN) [Zhou et al., NeurIPS 2023] formalize this insight into a class of equivariant architectures
for MLP and CNN weights, achieving Kendall's τ = 0.934 on CIFAR-10-GS and τ = 0.931 on SVHN-GS
generalization prediction within the CNN family. Monomial-NFN [Tran, Vo et al., 2024] extends
NFN to scaling and sign-flip symmetries, proving that all invariant groups are subsets of the
monomial matrix group — a theoretical generalization that nevertheless remains within the
architecture-specific regime.

Transformer-NFN [Tran-Viet et al., 2024] extends the NFN framework to transformer architectures,
identifying the maximal symmetric group of multi-head attention weights and achieving τ = 0.905–0.910
on within-architecture transformer benchmarks. Critically, Transformer-NFN requires a separate
equivariant construction for attention layers — the CNN and transformer approaches are not unified.
Our work asks whether a *single* group action (input/output channel permutation) can serve as a
universal foundation for all layer types, and empirically measures what fraction of weight-space
variance this group captures for each layer type.

## Token-Based and Scalable Weight Representations

SANE (Sequential Autoencoder for Neural Embeddings) [Schürholt et al., ICML 2024] takes a
complementary approach: rather than enforcing equivariance, it represents weights as sequences of
tokens and trains a transformer-based autoencoder. SANE achieves strong within-architecture results
(linear probe accuracy 0.978 on MNIST, 0.991 on CIFAR-10) while scaling to ResNets — a capability
that equivariant methods struggle with. However, SANE's sequential positional encodings do not
encode symmetry structure, limiting cross-architecture transfer. Our orbit-PE augments SANE's
tokenization with orbit membership information derived from the channel permutation group, preserving
SANE's scalability while adding structured positional information.

ProbeGen [Kahana, Horwitz et al., 2024] achieves 30–1000× fewer FLOPs than SANE by learning probe
generators that directly address permutation symmetry in its weight processing. While more efficient,
ProbeGen remains architecture-specific in its symmetry handling. The efficiency gains motivate
our constraint of ≤ 1.2× orbit-PE computation overhead relative to sequential PE.

## GL Orbit Symmetry and Weight Space Geometry

The role of the General Linear group in weight space geometry has received recent theoretical
attention. arXiv:2410.04207 [Tran-Viet et al., 2024] (the Transformer-NFN paper) proposes
GL-invariant features for attention weights — specifically, polynomial trace features
tr(WW^T) and tr(W^Q W^{K,T}) — motivated by the theoretical argument that GL symmetry
is the relevant group for attention weight structure. Our H-M2 result provides independent
empirical confirmation of this theoretical prediction: Linear/attention layers in the CNN Zoo
show GL-orbit variance 6.6× larger than permutation orbit variance (ratio = 0.133).

Loss landscape analysis [Goldstein et al., 2023] and neural network trajectory studies
[arXiv:2602.23696] document the existence of flat directions along symmetry orbits in trained
networks. Our training trajectory finding — permutation variance ratio decreasing from ~0.49
(epoch 0) to ~0.28 (epoch 50) — connects weight-space geometry measurement to this literature,
suggesting that optimizers progressively exploit GL-type reparameterizations during training.

## Weight Space Learning Surveys and Benchmarks

The WSL Survey [Han et al., 2026] introduces the WSU/WSR/WSG taxonomy (understanding, representation,
generation) and identifies cross-architecture generalization as the primary open problem in WSR.
Model zoo datasets enabling this research include the Small CNN Zoo [Unterthiner et al., 2020]
(10,000+ CIFAR-10-GS/SVHN-GS trained networks with trajectories) and the Transformer Zoo
[Tran-Viet et al., 2024] (125,000 checkpoints). Our variance decomposition uses 1,000 CNN Zoo
models × 50 epoch checkpoints — an order of magnitude more than prior symmetry studies.

## Positioning

Our work differs from prior weight space learning in one key respect: rather than *assuming*
which symmetry group is appropriate and building an equivariant architecture, we *measure*
which symmetry groups explain the dominant weight-space variance for each layer type at zoo
scale. This empirical measurement approach reveals the layer-type stratification that prior
work — whether architecture-specific (NFN family) or agnostic to equivariance (SANE) — did
not observe. The result directly motivates the hybrid encoding design that prior theoretical
work (GL features for attention) suggested but did not empirically ground.
