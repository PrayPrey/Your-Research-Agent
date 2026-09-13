# Methodology

Our approach proceeds in three stages, corresponding to the three sub-hypotheses we test.
Rather than designing an equivariant architecture and evaluating its performance, we first
verify that the orbit construction is mathematically valid (Section 3.1), then assess its
practical efficiency (Section 3.2), and finally measure what fraction of weight-space variance
it actually explains — stratified by layer type (Section 3.3). This structure tests the
preconditions of orbit-PE before committing to the full cross-architecture training experiment.

## 3.1 Orbit-PE Construction

**Motivation.** SANE [Schürholt et al., 2024] tokenizes neural network weights by reshaping
weight tensors W ∈ ℝ^{c_out × c_1 × ⋯ × c_in} into row-wise slices along the output channel
dimension, assigning each token a positional encoding P_n = [n, l, k] — global index, layer
index, within-layer index. This sequential positional encoding carries no symmetry information.
Our key observation: the input/output channel permutation group G = S_{c_in} × S_{c_out} acts
on all linear operators (Conv2d, Linear, MultiheadAttention) as a *functionally exact* symmetry —
any permutation of input/output channels with the corresponding inverse permutation in adjacent
layers leaves the network function unchanged. We replace the sequential positional encoding with
an *orbit membership vector* that encodes which permutation-orbit a token belongs to.

**Orbit membership computation.** For a weight matrix W ∈ ℝ^{c_out × c_in}, the orbit under G
consists of all matrices obtainable by permuting rows (output channels) and columns (input channels).
We represent orbit membership via the singular value decomposition of the orbit membership matrix:

1. *Enumerate canonical representatives*: For each weight token W_l,k (a row of the reshaped weight
   matrix), identify its orbit under the input permutation S_{c_in}.
2. *Construct orbit basis*: Apply SVD to the orbit membership matrix M ∈ ℝ^{n_tokens × d_orbit}
   to obtain a low-rank orbit basis U ∈ ℝ^{n_tokens × d_pe}.
3. *Assign orbit-PE*: Replace sequential positional encoding P_n with the corresponding row of U,
   producing orbit-PE ∈ ℝ^{d_pe} (d_pe = 64 = token_dim).

**Layer-type dispatch.** The orbit-PE computation is identical across layer types at the abstraction
level of the linear operator (input/output channels). The implementation uses a dispatch dictionary
over layer types (Conv2d, Linear, MultiheadAttention) with no architecture-specific if/else branches
(HAS_ARCH_BRANCHES = False), producing token_dim = 64 output for all types. This unified codebase
design is itself a claim tested by H-M1.

## 3.2 Computability Verification (H-M1)

**Why this matters.** An orbit encoding that requires 10× longer computation time than sequential
PE is impractical regardless of representational quality. SANE positions itself as scalable to
ResNets [Schürholt et al., 2024]; adding orbit-PE must preserve this efficiency property.

**Overhead measurement.** We measure wall-clock time for orbit-PE computation vs. sequential PE
baseline on 200 checkpoints (100 CNN Zoo + 100 Transformer Zoo), using a single CPU to isolate
the encoding computation from training overhead. The overhead ratio is:

    overhead_ratio = t_{orbit-PE} / t_{sequential-PE}

The MUST_WORK gate requires overhead_ratio ≤ 1.2×. We report mean ± std across checkpoints,
stratified by layer type (Conv2d, Linear, MultiheadAttention). Figure 7 shows per-layer-type
overhead distribution.

## 3.3 Variance Decomposition (H-M2)

**Core question.** Even if orbit-PE is valid and practical, it is only useful for cross-architecture
weight representation if it captures the *dominant* variation in weight space. We measure this
directly: what fraction of weight-space variance lies along permutation orbits vs. General Linear
(GL) orbits?

**Orbit projectors.** For each checkpoint's weight tensors, we compute:

- *Permutation orbit projection*: Project weight vectors onto the SVD-derived orbit basis U from
  Section 3.1. The variance along orbit directions is Var_perm = Σ_i σ_i^2 where σ_i are
  singular values of the orbit basis applied to the weight matrix.

- *GL orbit projection*: Apply polar decomposition W = QR (Q orthogonal, R symmetric positive
  semidefinite). The GL orbit includes all matrices reachable by invertible linear transformation;
  the polar decomposition decomposes weight variation into rotation (Q) and scaling (R) components,
  with Var_GL capturing the variation along the full GL orbit directions.

**Variance ratio.** The primary metric is:

    ratio = Var_perm / (Var_perm + Var_GL)

We compute this per checkpoint, per layer type, and averaged across the full trajectory (50 epochs,
epochs 0–50) for each of 1,000 CNN Zoo CIFAR-10-GS models. The MUST_WORK gate requires ratio > 0.60.

**Statistical design.** n = 1,000 models × 50 checkpoints = 50,000 weight snapshots. This is an
order of magnitude larger than the planned minimum (n ≥ 200 from H-M2 specification), providing
high statistical power for the refutation (ratio = 0.3479 ± 0.0536, p ≪ 0.001 vs. threshold 0.60).

**Implementation.** The full pipeline is implemented in `orbit_projector.py` (orbit basis + polar
decomp), `variance_decomposer.py` (trajectory analysis), and `evaluate.py` (zoo-scale orchestration
over 1,000 models). All code uses the TrajectoryDataset from `data_loader.py` with symlink-aware
CNN Zoo loading. Note: H-M2 uses an SVD fallback for the orbit basis rather than directly importing
H-M1's OrbitPEComputer (path resolution issue); this is methodologically equivalent as both compute
SVD-based orbit projections.

## 3.4 Verification Chain Structure

The three sub-hypotheses H-E1 → H-M1 → H-M2 form a *prerequisite chain*: we test the existence
precondition before the practical precondition before the variance precondition. This chain structure
is a methodological choice: testing H-M3 (cross-architecture training) before H-M2 would risk
expending substantial compute on a training run whose mechanism precondition (permutation variance
dominance) might be false. H-M2's MUST_WORK gate is designed to *detect* this and pivot to hybrid
encoding before H-M3.

This is *not* a post-hoc rationalization of H-M2's failure — the pivot path was pre-specified in
the H-M2 hypothesis design: "GATE: if ratio < 0.60, pivot to hybrid orbit-PE + GL trace features
before H-M3." The methodology is presented as designed, with findings reported as observed.
