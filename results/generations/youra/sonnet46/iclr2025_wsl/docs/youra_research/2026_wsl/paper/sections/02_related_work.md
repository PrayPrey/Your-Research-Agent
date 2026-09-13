# Related Work

Our work sits at the intersection of three research lines: weight-space property prediction,
permutation-equivariant neural architectures, and model zoo representation learning.
We survey each, highlighting the limitations that motivate our approach.

## Weight-Space Property Prediction

The foundational work by Unterthiner et al. [2020] demonstrated that properties of trained neural
networks — including accuracy, generalization gap, and training loss — are predictable from their
weights with high fidelity (R² > 0.98 on a zoo of 120K+ models). Their flat-MLP baseline
concatenates all weight matrices into a single vector and applies a standard MLP regression head.
This approach is simple, effective within a single model zoo, and remains the standard baseline
for weight-space property prediction.

Eilertsen et al. [2020] extended this direction by introducing meta-classifiers that operate on
weight snapshots to classify training dynamics and model properties. Their NWS dataset (320K
snapshots across 16K networks) established weight-space analysis as a viable data modality.
Both of these foundational works operate in the in-distribution setting: train and test on the
same zoo with the same training protocol, where neuron ordering is implicitly consistent.
Neither work investigates the behavior of flat-MLP encoders under permutation stress, nor
compares against equivariant alternatives.

Schürholt et al. [2021] introduced hyper-representations — self-supervised representations of
neural network weights via contrastive learning with permutation augmentation. Their key insight
is that augmenting with random neuron permutations during training can improve generalization of
weight-space encoders. We build on this work in our ablation: the flat-MLP+aug encoder
replicates the Schürholt et al. [2021] data augmentation strategy. Importantly, we show
empirically that augmentation provides partial but unreliable robustness (67% mean Δρ reduction,
but with seed variance spanning 0.096–0.317) — augmentation-based robustness is stochastic,
not structural.

More recent work has extended weight-space property prediction to reinforcement learning agents
[2025], graph-structured model representations [WS-KAN, 2026], and large-scale benchmarking
across diverse model zoos [Schürholt et al., 2025]. Our contribution is orthogonal to these
scaling directions: we address the architectural inductive bias question, which applies regardless
of zoo scale.

## Permutation-Equivariant Architectures for Weight Spaces

Zhou et al. [2023] introduced Neural Functional Transformers (NFT), which apply permutation-
equivariant attention layers to neural network weight representations. NFT represents each
neuron as a token — a row of the weight matrix corresponding to that neuron's incoming weights
— and applies multi-head attention where the equivariance is enforced across the neuron dimension.
The key theoretical guarantee (Theorem 1) is that for any permutation π of neurons, NFT's
encoding satisfies: φ(π(W)) = π(φ(W)), where W is the weight matrix and φ is the NFT encoder.
NFT is natively compatible with FC-MLP weight shapes and is implemented in PyTorch at
github.com/AllanYangZhou/nfn. Crucially, Zhou et al. [2023] evaluate NFT on implicit neural
representation (INR) classification tasks — classifying implicit function networks (NeRFs,
StyleGAN latents) — but not on model zoo property prediction (regression tasks on trained
classifiers). Our work provides the first empirical test of NFT on the latter problem class.

Navon et al. [2023] developed Deep Weight Space Networks (DWSNets), which achieve equivariance
for CNN weight spaces by operating on weight matrices with cross-channel symmetry structure.
DWSNets is theoretically applicable to FC-MLP weights but requires weight shapes compatible
with its internal operations (weight_to_weight layers). In practice, DWSNets fails at runtime
with FC-MLP weight vectors due to a shape mismatch (FC-MLP has no spatial dimensions expected
by DWSNets). We do not include DWSNets as a baseline; NFT is the appropriate equivariant
architecture for FC-MLP weight spaces.

Subsequent work has extended equivariant weight-space representations to graph metanetworks
[Kofinas et al., 2024; 2025] and architecture-agnostic encoders [NNiT, 2026]. These directions
complement our contribution: where we establish the benefit of equivariance for property
prediction on flat-MLP zoos, graph metanetwork approaches extend equivariance to more
expressive structural representations.

## Model Zoo Analysis and Meta-Learning

The model zoo framework — large collections of trained networks with known properties — has
been developed as a benchmark for weight-space learning algorithms. The Unterthiner MNIST zoo
(29,997 models, 4-layer CNN) provides a standard benchmark for property prediction.
Schürholt et al. [2025] released a large-scale benchmark of 12 model zoos for systematic
weight-space learning evaluation.

Our approach relates to meta-learning in that we learn an encoder on a population of networks
rather than a single target. However, our goal is discriminative property prediction rather
than generative modeling. Peebles et al. [2022] showed that diffusion Transformers applied to
weight checkpoints can achieve impressive weight-space generative modeling, confirming that
Transformer architectures are viable for weight-space tasks. Our work demonstrates that the
equivariance property of the Transformer (not just its capacity) is critical for robust
discriminative prediction.

## Positioning Our Contribution

Prior work in weight-space property prediction (Unterthiner et al. [2020], Eilertsen et al.
[2020]) establishes high in-distribution performance for flat encoders but does not evaluate
under permutation stress. Prior work on equivariant weight-space encoders (Zhou et al. [2023],
Navon et al. [2023]) proves equivariance and demonstrates it on INR tasks but does not test
on model zoo property prediction. Our work bridges these two lines: we take the equivariant
architecture (NFT) from Zhou et al. [2023] and test it directly on the model zoo property
prediction task of Unterthiner et al. [2020], providing the controlled comparison that neither
line of work has conducted.
