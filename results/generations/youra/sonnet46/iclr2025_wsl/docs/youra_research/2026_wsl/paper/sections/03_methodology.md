# Methodology

## Overview

Our experimental design is motivated by a simple structural observation: FC-MLP model zoos
exhibit neuron permutation symmetry — any permutation of neurons within a layer produces a
functionally equivalent network — yet standard flat-MLP encoders treat neuron position as
meaningful signal. We test whether aligning the encoder with this symmetry structure provides
measurable advantages for generalization gap prediction, and whether the mechanism can be
confirmed via mediation analysis.

We formalize this as a controlled comparison between a flat-MLP encoder (position-dependent,
no equivariance) and a Neural Functional Transformer encoder (position-independent, architecturally
equivariant), extended to a 6-encoder ablation suite that covers the full spectrum from no
equivariance to oracle equivariance by construction.

## Problem Formulation

Let Z = {(w_i, g_i)}_{i=1}^N be a model zoo, where w_i ∈ ℝ^D are the weight parameters of
the i-th trained network and g_i = train_loss_i − test_loss_i is the generalization gap.
We train an encoder φ: ℝ^D → ℝ^d followed by a regression head h: ℝ^d → ℝ to predict g from w.

**Permutation Sensitivity.** For a permutation π applied to neurons in layer l, let w^π denote
the permuted weight representation. A permutation-sensitive encoder satisfies φ(w^π) ≠ φ(w),
leading to different predictions for functionally equivalent networks. A permutation-equivariant
encoder satisfies φ(w^π) = π̂(φ(w)) for a corresponding action π̂, and any permutation-invariant
head h produces h(φ(w^π)) = h(φ(w)).

**Permutation Stress Test.** We evaluate encoders at permutation severity s ∈ {0, 0.25, 0.5, 1.0},
where s is the fraction of neurons randomly permuted within each layer at test time.
At s = 0, the original neuron ordering is preserved. At s = 1.0, all neurons are fully randomly
permuted. We measure Δρ = ρ(s=0) − ρ(s=1.0), where ρ is the Spearman rank correlation
between predicted and true generalization gap. Large Δρ indicates high permutation sensitivity.

## Encoder Suite

We compare six encoder variants that span the spectrum of permutation handling strategies:

**E1 — flat-MLP (baseline):** Concatenates all weight matrices into a single vector of
dimension 4,912 (total parameters of a 4-layer CNN with fan_in=16), then applies a 3-layer
MLP with hidden dimension 512. Total parameters: 3.04M. This is the Unterthiner et al. [2020]
baseline approach. No permutation handling; serves as the lower bound on permutation robustness.

**E2 — flat-MLP + augmentation:** Identical to E1 architecture, but trained with permutation
augmentation: at each training batch, a random neuron permutation is applied to input weight
vectors. This implements the Schürholt et al. [2021] data augmentation strategy. Permutation
handling is stochastic (training-time only), not architectural.

**E3 — flat-MLP + L2-norm canonicalization:** Identical to E1 architecture, but each neuron's
weight vector is normalized to unit L2 norm before encoding, to remove neuron ordering dependence
via standardization. This is a post-hoc symmetry-breaking approach.

**E4 — NFT-base:** Neural Functional Transformer (Zhou et al. [2023]) with per-neuron token
representation. Each neuron's weight vector (fan_in = 16 weights per neuron) is projected to a
d_model = 128 dimensional token. Multi-head attention (n_heads = 4) is applied within each layer,
with permutation equivariance enforced. Cross-layer aggregation is applied after within-layer
attention. Total parameters: 75K (40× fewer than flat-MLP). Permutation handling is architectural:
the equivariance theorem guarantees Δρ = 0 for a permutation-invariant downstream head.

**E5 — NFT + augmentation:** NFT-base combined with permutation augmentation during training.
Tests whether augmentation provides additional benefit to an already-equivariant architecture.

**E6 — Oracle canonicalization:** Flat-MLP with oracle Hungarian alignment canonicalization:
each test model's neurons are aligned to a reference model via the optimal permutation
(minimizing L2 distance to the reference). This requires oracle access to the reference model's
exact neuron ordering — impractical in deployment but provides the theoretical upper bound for
post-hoc canonicalization approaches. Expected Δρ ≈ 0 by construction.

**Rationale for this design:** The 6-encoder suite tests all plausible alternatives along
two axes: (1) no handling → augmentation → canonicalization → architectural equivariance;
(2) impractical (oracle) vs. practical. If architectural equivariance (E4) matches oracle
performance (E6) while outperforming augmentation (E2) and canonicalization (E3), this
establishes architectural equivariance as the practical path to symmetry-aligned encoding.

## NFT Architecture Details

NFT processes FC-MLP weight matrices as per-neuron token sequences.
For a layer with n neurons and fan_in = k incoming weights per neuron, the weight matrix
W ∈ ℝ^{n×k} is treated as a sequence of n tokens, each of dimension k.
A linear projection maps each token to d_model = 128 dimensions.
Multi-head attention (n_heads = 4, key/value dimension 32) is applied within the layer,
with attention masks allowing each neuron to attend to all other neurons in the same layer.
The within-layer equivariance is enforced by the attention mechanism: permuting the input
token sequence permutes the output token sequence correspondingly.
After within-layer attention, a cross-layer aggregation module combines per-layer embeddings
into a fixed-size representation, followed by a regression head for generalization gap prediction.

The key insight is that per-neuron tokens encode the relationship structure relevant to
generalization gap — neuron influence concentration, measured by the Gini coefficient of
attention weights and the spectral decay ratio of the weight matrix. These concentration metrics
are permutation-invariant under NFT's equivariant processing, whereas flat-MLP encodes them
in a position-dependent manner that depends on the arbitrary ordering of neurons.

## Mediation Analysis

To test the mechanism — not just the performance correlation — we conduct a mediation analysis
following the hierarchical regression framework of Baron & Kenny [1986].

**Hypothesis:** NFT's permutation robustness advantage is mediated by equivariant attention
capturing neuron influence concentration signals (Gini coefficient, spectral decay ratio)
invariantly under permutation.

**Protocol (3 steps):**
1. Regress generalization gap on flat-MLP+aug embeddings → obtain baseline R²_aug.
2. Regress generalization gap on NFT-base embeddings → obtain R²_NFT.
3. Compute ΔR² = R²_NFT − R²_aug, measuring the additional variance explained by NFT's
   equivariant embedding beyond what augmentation alone captures.

**Gate condition:** ΔR² ≥ 0.10 (10 percentage points) constitutes confirmation of the
mechanism — NFT's equivariant attention explains substantially more variance than augmentation
alone, specifically because it captures concentration signals invariantly.

This design allows us to distinguish structural advantage (NFT captures the right signal
invariantly) from incidental advantage (NFT happens to work better for unrelated reasons).

## Dataset and Evaluation Protocol

**Dataset.** We use the Unterthiner MNIST zoo: 29,997 trained 4-layer CNN models with per-neuron
weight vectors reshaped to FC-MLP token format (fan_in = 16 per layer, 4 layers). The original
Unterthiner FC-MLP zoo URL was unavailable at pipeline execution time; the CNN zoo is adapted
to maintain the permutation structure relevant to our claims. See Section 6 for discussion of
this adaptation.

**Splits.** 80% train (23,997 models), 20% test (6,000 models), split by random seed 42.
All encoders train on the same split.

**Training.** Adam optimizer (lr = 0.001, β = (0.9, 0.999), weight decay = 0.0001),
CosineAnnealingLR scheduler (T_max = 100, η_min = 1e-5), 100 epochs, batch size 64.
Each encoder trained with 3 random seeds (42, 123, 456). Results reported as mean ± std.

**Evaluation.** Spearman ρ between predicted and true generalization gap across 6,000 test models.
Permutation stress applied at test time at severity s ∈ {0, 0.25, 0.5, 1.0}.
Bootstrap testing for Δρ significance: n = 10,000 paired resamples; Holm correction for
multiple comparison correction across severity levels.

**Fairness.** All encoders use the same training hyperparameters, dataset splits, random seeds,
and evaluation protocol. NFT and flat-MLP differ only in encoder architecture, not in optimizer,
scheduler, or training epochs.
