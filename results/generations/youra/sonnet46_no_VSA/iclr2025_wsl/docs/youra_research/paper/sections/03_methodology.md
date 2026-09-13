# Methodology

Our key insight — that architectural permutation-invariance causally determines weight encoder utility through the chain *architecture → OrbitVar → MSE_perm → R²* — motivates a measurement-first methodology. Rather than proposing a new encoder and evaluating downstream performance, we design a framework that directly quantifies each step of this causal chain.

## 3.1 Notation and Problem Setup

Let V = {v₁, ..., v_N} be a model zoo of N neural networks, where each vᵢ ∈ ℝ^d is a flattened weight vector. For each network, let y_i ∈ ℝ be a scalar performance label (test accuracy). A weight encoder e: ℝ^d → ℝ^k maps weight vectors to fixed-size representations; a downstream predictor f: ℝ^k → ℝ predicts performance from representations.

The **permutation group** for a K-layer CNN with channel widths c₁, ..., c_K is the direct product S_{c₁} × ... × S_{c_K}, acting via *coupled* row-column permutations: permuting the output channels of layer ℓ simultaneously permutes the input channels of layer ℓ+1, preserving functional equivalence [Navon et al., 2023]. We denote the orbit of network v under this group as O(v) = {π·v : π ∈ S_{c₁} × ... × S_{c_K}}.

**OrbitVar** of an encoder e on network v is defined as:

OrbitVar(v) = Var_{π ∼ Uniform(orbit)} [ e(π·v) ]

averaged over the embedding dimension. The population-level OrbitVar is E_v[OrbitVar(v)].

**MSE_perm** is the component of the total prediction MSE attributable to permutation-induced variance. For an encoder-predictor pair (e, f):

MSE_perm = E_v[ E_{π,π'}[ (f(e(π·v)) − f(e(π'·v)))² / 2 ] ]

where π, π' are independent random permutations. MSE_res = MSE_total − MSE_perm is the residual (non-permutation-induced) component.

## 3.2 Encoder Designs

We evaluate four encoders spanning the invariance spectrum, implementing the ladder C0 ≤ C1 < C2 ≤ C3 in terms of architectural invariance:

**C0 — Per-Layer Statistics (Approximately Invariant).** The Ŵ_L encoder from Unterthiner et al. [2020] computes per-layer summary statistics: mean, variance, and spectral norm of each weight matrix. These statistics are permutation-invariant under row permutations but not under column permutations; in practice, the compact representation achieves R² > 0.98 on CIFAR10-GS. We use C0 as the reference baseline.

**C1 — CISE (Non-Invariant).** The channel-index sinusoidal encoder applies per-channel learned projections with sinusoidal positional encodings indexed by channel position. Formally, for layer ℓ with weights W^(ℓ) ∈ ℝ^{C_out × C_in × k × k}:

e_C1(W^(ℓ))_c = φ(W^(ℓ)_c) + PE(c)

where φ is a learned MLP and PE(c) encodes channel index c via sinusoidal functions. Concatenating across channels and layers yields a 64-dim × 16-channel embedding (1024-dim total). Since PE(c) ≠ PE(π(c)) for permutation π, CISE has OrbitVar > 0 by design. The established CISE OrbitVar on ModelZooDataset CIFAR10-GS is 0.010333 (verified in our preliminary work, sh1).

**C2 — DeepSets (Exactly Invariant).** We implement doubly-invariant DeepSets [Zaheer et al., 2017] for each convolutional layer:

e_C2(W^(ℓ)) = ρ( Σ_{c=1}^{C_out} φ(W^(ℓ)_c) )

where φ: ℝ^{C_in × k × k} → ℝ^{h} is a learned MLP (hidden_dim=64) and ρ: ℝ^h → ℝ^{embed_dim} is another MLP (embed_dim=128). Sum pooling over C_out ensures invariance to output channel order; per-channel features φ applied to W^(ℓ)_c ∈ ℝ^{C_in × k × k} treat input channels symmetrically within each output channel. Layer embeddings are concatenated and linearly projected to the final representation.

By Deep Sets Theorem 2, this architecture guarantees OrbitVar(C2) = 0 exactly — any permutation of output channels produces the same sum, any permutation of input channels is handled within each φ application.

**C3 — NFN (Near-Invariant).** We use Neural Functional Networks [Zhou et al., 2023] via the official `nfn` library. The encoder applies two NF-Linear layers (NPLinear) with ReLU activations, followed by HNPPool for invariant aggregation and a final linear projection:

e_C3 = Linear ∘ HNPPool ∘ ReLU ∘ NPLinear ∘ ReLU ∘ NPLinear

NFN achieves equivariance rather than strict invariance at intermediate layers, converging to near-invariance after HNPPool. OrbitVar(C3) is predicted to be small by the equivariance guarantee but not exactly zero due to finite-precision HNPPool aggregation of spatial interaction terms.

## 3.3 Functional Permutation Implementation

**Critical design decision:** We implement S_n³ functional permutations as *coupled* row-column actions, following DWSNet Eq. 5 [Navon et al., 2023]. For a 3-conv CNN with channel widths (c₁=8, c₂=6, c₃=4):

```
Layer 1 (conv1): Permute output channels (rows of W^(1)) with π₁
Layer 2 (conv2): Permute input channels (columns of W^(2)) with π₁,
                 permute output channels (rows of W^(2)) with π₂
Layer 3 (conv3): Permute input channels (columns of W^(3)) with π₂,
                 permute output channels (rows of W^(3)) with π₃
BatchNorm: Permute parameters consistently with corresponding conv
```

Independent per-layer permutations would not preserve functional equivalence (the coupled structure is required). We verify this with a functional audit before any experiment runs:

**Functional audit:** For K_audit=5 randomly drawn permutations and n_checks=5 random inputs x ∈ [0,1]^{3×32×32}, we compute ||f_v(x) − f_{π·v}(x)||∞ and require this to be ≤ 1e-6. In our experiments, max_diff = 1.91e-6 ≤ float32 precision, confirming implementation correctness. This audit is a hard gate: if it fails, no encoding runs.

## 3.4 OrbitVar Measurement Protocol

For each encoder and each model vᵢ, we draw K=50 functional permutations (seed=1) and compute:

OrbitVar(vᵢ) = mean_dim( Var_{k=1}^{K} [ e(π_k · vᵢ) ] )

where mean_dim averages the per-dimension variance over the embedding dimension. We use float64 precision to avoid numerical cancellation in the variance computation, and report mean and max over N=100 models.

## 3.5 MSE Bias-Variance Decomposition

For the C1 (CISE) encoder, we decompose prediction error over orbits. Given LightGBM predictor f trained on C1 embeddings (standard training, no permutation augmentation):

For each model vᵢ, we compute predictions f(e(π_k · vᵢ)) for K=50 permutations, yielding per-model prediction variance PredVar(vᵢ).

**MSE_perm** for the full dataset is defined as the sum of per-model prediction variances:

MSE_perm = (1/N) Σᵢ PredVar(vᵢ)

**MSE_total** is the out-of-fold OOF MSE from 5-fold cross-validation on the standard (non-permuted) training set.

**Orbit-averaged diagnostic:** We also compute R²(C1_avg) — the R² when predicting using f(mean_{k=1}^K e(π_k · vᵢ)) as the input. This measures what happens when we try to "cancel out" permutation sensitivity by averaging embeddings across orbits. If the encoder were approximately invariant, orbit-averaging would have no effect; if non-invariant, it produces a representation that no longer corresponds to any natural arrangement of weights.

## 3.6 Downstream Prediction

We use LightGBM with 5-fold cross-validation, following Unterthiner et al. [2020]:

- n_estimators: 500
- learning_rate: 0.05
- Cross-validation: 5-fold stratified

Embeddings from each encoder are used directly as features; no dimensionality reduction or normalization is applied. We report R² on a held-out testset (100-model split used consistently across all hypotheses).

**Linear head ablation:** We additionally fit Ridge regression on C2 embeddings to test linear separability of the DeepSets representation. This tests whether R²(C2) = 0.9148 requires non-linear prediction or whether the invariant representation is linearly predictive.

## 3.7 Experimental Design Summary

Our four sub-experiments cover each step of the causal chain independently:

| Hypothesis | Tests | Gate |
|------------|-------|------|
| h-e1 | OrbitVar(C2) < 1e-6, OrbitVar(C3) < 1e-6 | MUST_WORK |
| h-m1 | OOM gap C1/C2 ≥ 4, Wilcoxon p < 0.001 (population-level) | MUST_WORK |
| h-m2 | MSE_perm^C1/MSE_total ≥ 0.10 | MUST_WORK |
| h-m3 | R²(C2) > R²(C1); additive closure ΔR² ≈ MSE_perm^C1 | SHOULD_WORK |

Each hypothesis is evaluated independently; h-e1 is a prerequisite (if OrbitVar targets fail, the causal chain is broken at Step 1 and subsequent experiments are not informative).
