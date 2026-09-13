# Introduction

A neural network trained to predict how well another network generalizes loses 89% of its
predictive correlation when the target network's neurons are randomly shuffled — yet an
equivariant architecture is completely unaffected by the same perturbation.
This striking fragility reveals a fundamental mismatch between the representational assumptions
of standard weight-space encoders and the symmetry structure of the objects they encode.

Predicting properties of trained neural networks directly from their weights — generalization gap,
test accuracy, training loss — has emerged as a productive research program with applications to
model selection, hyperparameter sensitivity analysis, and automated machine learning.
Unterthiner et al. [2020] demonstrated that a flat multi-layer perceptron (flat-MLP) applied to
concatenated weight vectors achieves remarkable predictive performance (R² > 0.98) on large model
zoos, establishing this as the baseline approach for weight-space property prediction.

Yet this approach contains a hidden structural assumption: it treats the ordering of neurons within
a layer as meaningful signal. In reality, any permutation of neurons in a fully-connected network
yields a functionally identical network — the same input-output mapping, the same generalization
behavior, the same gap between training and test loss. Flat-MLP encoders cannot distinguish between
a network and its permuted equivalent, creating representations that depend on an arbitrary labeling
artifact rather than on functional structure. Under standard in-distribution evaluation, this
artifact is consistent across models (same training procedure, same random seed behavior), and
performance appears high. Under permutation stress — when neurons are deliberately shuffled at
test time — the encoding collapses, and predictive correlation degrades severely.

This is not merely a theoretical concern. Within the same model zoo, models trained with different
random seeds have neurons that happen to be in different orders due to random initialization and
gradient dynamics. Cross-architecture comparison is even more sensitive to this artifact.
As weight-space analysis scales to larger and more diverse model zoos — a natural direction as
model repositories grow — the permutation sensitivity of flat-MLP encoders becomes an increasingly
costly practical limitation.

Neural Functional Transformers (NFT; Zhou et al. [2023]) were designed to address exactly this
structural mismatch. NFT applies permutation-equivariant multi-head attention over per-neuron
token sequences, where each token represents one neuron's incoming weight vector.
The equivariance theorem (Theorem 1 of Zhou et al. [2023]) guarantees that permuting neurons
permutes the attention outputs correspondingly, such that any permutation-invariant downstream
head produces identical predictions regardless of neuron ordering. NFT is natively compatible
with FC-MLP weight shapes and has an open PyTorch implementation [Zhou et al., 2023].
However, NFT was evaluated only on implicit neural representation (INR) classification tasks —
never on model zoo property prediction (generalization gap, accuracy). The Unterthiner et al. [2020]
benchmark predates equivariant weight-space architectures; no controlled comparison exists.

We bridge this gap. We show that aligning the encoder with the symmetry group of the
task eliminates permutation brittleness entirely (Δρ ≈ 4.7×10⁻⁷) while simultaneously
improving baseline performance with 40× fewer parameters (75K vs. 3.04M). The mechanism
is confirmed via mediation analysis (ΔR² = 0.228): NFT's equivariant attention specifically
captures the neuron influence concentration signals that encode generalization gap, invariantly
under permutation.

Building on this structural alignment principle, we make the following contributions:

**(1) First controlled comparison of NFT vs. flat-MLP for model zoo property prediction.**
We conduct the first empirical comparison of a permutation-equivariant encoder (NFT) against
flat-MLP baselines for generalization gap prediction on the Unterthiner MNIST zoo, with a
systematic 6-encoder ablation suite spanning the spectrum from flat-MLP (no equivariance)
to oracle canonicalization (perfect equivariance by construction).

**(2) Empirical confirmation of architectural equivariance advantage via mediation analysis.**
Beyond demonstrating the robustness differential, we confirm the *mechanism* via hierarchical
regression (ΔR² = 0.228 across 18 training runs), showing that NFT equivariant attention mediates
robustness specifically through neuron influence concentration signals. This is a stronger claim
than showing performance correlation — we identify *why* NFT works.

**(3) Principled negative result: L2-norm canonicalization is categorically non-viable.**
We demonstrate that L2-norm canonicalization systematically collapses the predictor to a constant
output (output std = 0 across all 3 seeds), because it destroys the relative weight magnitudes
that encode generalization gap signal. This resolves a design question for the field: magnitude-
destructive canonicalization is incompatible with weight-space property prediction.

**(4) Parameter efficiency of equivariant architectures.**
NFT achieves higher baseline prediction performance (ρ = 0.489 vs. 0.303) with 40× fewer parameters
than flat-MLP, suggesting that architectural alignment with task symmetry provides compounding
efficiency benefits beyond robustness alone.

We organize the paper as follows: Section 2 surveys related work on weight-space representation
learning, equivariant architectures, and model zoo analysis. Section 3 presents the methodology
including the 6-encoder ablation design and mediation analysis framework. Section 4 describes
the experimental setup. Section 5 presents results. Section 6 discusses findings, limitations,
and implications. Section 7 concludes.
