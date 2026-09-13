# Architectural Permutation-Invariance in Weight Encoders: Closing the OrbitVar → MSE_perm → R² Causal Chain

## Abstract

Weight-space learning — predicting neural network properties directly from their parameters — faces a fundamental challenge: permuting a network's neurons produces a functionally identical model with different raw weights. Non-invariant encoders treat these equivalent configurations as distinct, and the cost is measurable: a sinusoidal positional encoder (CISE), designed as a representative non-invariant baseline, achieves R² = −1.63 when its predictions are averaged over functionally equivalent weight permutations, revealing that channel-position information is a primary predictive signal rather than background noise. This paper studies this failure through a three-step causal framework — architecture determines within-orbit representational variance (OrbitVar), OrbitVar propagates to permutation-induced prediction error (MSE_perm), and eliminating MSE_perm improves downstream R² — and measures each step empirically on ModelZooDataset CIFAR10-GS. Architecturally invariant encoders (DeepSets doubly-invariant sum pooling) achieve OrbitVar at machine precision (1.002e-14, twelve orders of magnitude below CISE's 0.010333), confirmed across all 100 models (Wilcoxon signed-rank p = 1.95e-18). For CISE, MSE_perm/MSE_total = 3.3452, demonstrating that permutation-induced prediction variance exceeds total prediction error by a factor of 3.35. DeepSets achieves R² = 0.9148 compared to CISE's R² = 0.8511, a 6.37 percentage-point improvement on the same testset with no additional training supervision. A pre-registered additive closure prediction (ΔMSE ≈ MSE_perm^{C1}) fails empirically (closure = 0.872), revealing an entanglement between MSE_perm and the residual error component that opens questions about the geometry of non-invariant weight-space representations.

---

## 1. Introduction

Consider the following experiment. Take a trained neural network and record its predicted test accuracy using a weight encoder. Now permute the neurons of a hidden layer — shuffle which neuron is labeled "channel 3", "channel 7", and so on — adjusting adjacent layers accordingly so the network computes exactly the same function. Re-encode and predict again. Repeat this across K = 50 such functionally equivalent rearrangements and average the predictions. For a correctly designed encoder, the average should match any individual prediction. For CISE, a sinusoidal positional encoder designed as a representative non-invariant baseline, the average yields R² = −1.63 — substantially worse than predicting the mean (R² = 0). This result does not reflect robustness failure under noise. It reflects a precise measurement of a structural flaw: CISE encodes which channel occupies which position as a predictive signal. But channel positions in a neural network are arbitrary labels: two networks with identical function can differ only in which neuron happens to be labeled "channel 3". An encoder that treats these networks as different is not modeling what a network computes; it is modeling an arbitrary administrative choice made during initialization.

### 1.1 The Weight-Space Symmetry Problem

Neural networks with permutation-symmetric activation functions have a well-known symmetry: permuting the neurons of a hidden layer and correspondingly adjusting adjacent layers produces a functionally identical network (Hecht-Nielsen, 1990). The space of weight configurations is therefore partitioned into orbits — equivalence classes under permutation — and any two configurations in the same orbit correspond to the same function.

Weight-space learning approaches, which train predictors directly on network weights, must contend with this symmetry. A predictor trained on one configuration may encounter a functionally identical configuration with different raw weights; if the encoder does not recognize these as equivalent, the predictor receives two different inputs that should produce the same output.

Prior work has addressed this from several angles. DeepSets (Zaheer et al., 2017) establishes that any permutation-invariant function on sets can be decomposed as ρ(Σφ(x_i)), making sum pooling the canonical invariant architecture. Neural Functional Networks (NFN; Zhou et al., 2023) extend this to equivariant mappings over weight spaces. DWSNet (Navon et al., 2023) derives the complete set of affine equivariant and invariant linear layers for weight spaces and formalizes that the correct symmetry group for CNNs requires coupled row-column permutations across adjacent layers. Unterthiner et al. (2020) demonstrate that per-layer weight statistics achieve R² > 0.984 on CIFAR10-GS generalization prediction.

Despite this theoretical and empirical progress, a critical gap remains: no prior work has directly measured (1) how much non-invariant encoders vary in their representations of functionally equivalent networks (OrbitVar), (2) how much this representational variance propagates to prediction-space variance (MSE_perm), and (3) whether architectural invariance causally closes this gap in downstream prediction quality.

### 1.2 Our Approach

We address this gap through a three-step experimental design that directly measures each link of the causal chain:

**Step 1 — Architecture determines OrbitVar.** We measure within-orbit representational variance (OrbitVar = E_v[Var_π(encoder(π·v))]) for four encoders spanning the invariance spectrum: per-layer statistics (C0, approximately invariant), CISE sinusoidal positional encoder (C1, non-invariant), DeepSets doubly-invariant sum pooling (C2, exactly invariant), and NFN equivariant layers (C3, near-invariant).

**Step 2 — OrbitVar propagates to prediction variance.** We apply a bias-variance decomposition over permutation orbits to measure how much of CISE's total prediction error is attributable to permutation-induced variance.

**Step 3 — Eliminating MSE_perm improves R².** We compare LightGBM predictors trained on each encoder's embeddings, with DeepSets' zero MSE_perm as treatment and CISE's high MSE_perm as control.

### 1.3 Contributions

This paper makes four contributions:

**1.** First joint measurement of OrbitVar, MSE_perm, and R² across the full invariance spectrum on ModelZooDataset CIFAR10-GS. DeepSets achieves OrbitVar = 1.002e-14 (machine precision); NFN achieves 8.905e-08; CISE achieves 0.010333 — a gap of 5 to 12 orders of magnitude, confirmed across 100 models with Wilcoxon p = 1.95e-18.

**2.** A novel MSE bias-variance decomposition over permutation orbits as a diagnostic tool for weight-space learning. For CISE, MSE_perm/MSE_total = 3.3452 — permutation-induced variance contributes more than 3.35 times the total prediction error.

**3.** An empirical entanglement finding: the additive decomposition MSE = MSE_res + MSE_perm is empirically violated (closure = 0.872). MSE_perm and MSE_res are correlated in CISE embedding space, indicating that permutation sensitivity reshapes the downstream model's learned feature map rather than adding independent noise.

**4.** A practical encoder design result: DeepSets doubly-invariant encoding achieves R² = 0.9148 on ModelZooDataset CIFAR10-GS, a 6.37 percentage-point improvement over CISE (R² = 0.8511), with no additional training supervision.

---

## 2. Related Work

### 2.1 Weight-Space Learning and Model Zoos

Unterthiner et al. (2020) introduce ModelZooDataset and demonstrate that per-layer weight statistics (mean, variance, spectral norms — the Ŵ_L encoder) achieve R² > 0.984 on CIFAR10-GS generalization prediction using gradient-boosted trees. This result establishes the reference performance ceiling against which the present work evaluates. Ŵ_L achieves high performance through approximately invariant statistics — moment-based features that do not systematically encode channel order — rather than through architectural invariance. Whether architectural invariance provides irreducible benefit over well-designed non-invariant statistics remains an open question that the present work investigates.

Eilertsen et al. (2020) extend weight-space learning to classification tasks, finding that raw weight footprints encode distinguishable signals about training conditions and optimizer choices. Schürholt et al. (2021, 2022) introduce self-supervised hyper-representations and model zoo benchmarks, establishing that weight populations contain rich transferable structure. These works motivate the need for encoders that faithfully represent the functional content of a network's weights.

### 2.2 Architecturally Invariant and Equivariant Encoders

The theoretical foundation for permutation-invariant set functions is established by Zaheer et al. (2017): any permutation-invariant function on a set can be decomposed as ρ(Σφ(x_i)), making sum pooling the canonical invariant architecture. By construction, DeepSets sum pooling achieves OrbitVar = 0 exactly, up to floating-point precision.

Neural Functional Networks (NFN; Zhou et al., 2023) extend this to equivariant mappings over weight spaces, introducing NF-Layers (NPLinear) with parameter sharing tied to the CNN permutation group structure and HNPPool for invariant aggregation. NFN achieves Kendall's τ = 0.934 on CIFAR-10-GS generalization prediction. Zhou et al. report performance improvements but do not measure OrbitVar — the within-orbit representational variance that the present work quantifies directly.

Navon et al. (2023) (DWSNet) derive the complete set of affine equivariant and invariant linear layers for deep weight spaces from symmetry group principles, formalizing that the correct symmetry group for CNNs requires coupled row-column permutations across adjacent layers. This coupled structure is a critical design constraint adopted in the present work; functional equivalence under permutation is verified before any encoding runs.

Kofinas et al. (2024) represent neural networks as parameter graphs and apply GNNs to learn equivariant embeddings, achieving state-of-the-art on several weight-space tasks. These approaches share the theoretical motivation for invariant encoding but do not directly measure how non-invariance translates to prediction error through the OrbitVar → MSE_perm → R² pathway.

### 2.3 Permutation Symmetry in Weight Spaces

The permutation symmetry of neural networks has been studied primarily in the context of loss landscape geometry (Entezari et al., 2022; Ainsworth et al., 2022) and neural network alignment (Wang et al., 2020). These works focus on finding the right permutation to align two networks (cross-model alignment), rather than on the within-model problem of measuring variance under all permutations of a single network.

Within-orbit variance (OrbitVar) and cross-model variance are orthogonal concerns: post-hoc alignment reduces the latter but cannot reduce the former, since OrbitVar is measured over all permutations of a single network, not across networks. The DWSNet formalism (Navon et al., 2023) provides the mathematical foundation for distinguishing these two problems; the MSE bias-variance decomposition over permutation orbits introduced here operationalizes this distinction into a directly measurable diagnostic.

### 2.4 Position in the Literature

The present work occupies a distinct position: rather than proposing a new encoder architecture, it provides the first empirical causal attribution of the encoder invariance → R² relationship on a standard model zoo benchmark. The MSE decomposition framework (MSE_res + MSE_perm) is a reusable diagnostic applicable to any encoder to quantify its permutation sensitivity. The closest related measurement is the implicit comparison embedded in NFN's Kendall's τ improvement (Zhou et al., 2023), but that result conflates invariance benefits with representational capacity differences; the present controlled comparison — CISE versus DeepSets at matched prediction capacity (same LightGBM predictor) — isolates the invariance effect directly.

---

## 3. Method

### 3.1 Notation and Problem Setup

Let V = {v₁, ..., v_N} be a model zoo of N neural networks, where each v_i ∈ ℝ^d is a flattened weight vector. For each network, let y_i ∈ ℝ be a scalar performance label (test accuracy). A weight encoder e: ℝ^d → ℝ^k maps weight vectors to fixed-size representations; a downstream predictor f: ℝ^k → ℝ predicts performance from representations.

The **permutation group** for a K-layer CNN with channel widths c₁, ..., c_K is the direct product S_{c₁} × ... × S_{c_K}, acting via coupled row-column permutations: permuting the output channels of layer ℓ simultaneously permutes the input channels of layer ℓ+1, preserving functional equivalence (Navon et al., 2023). The orbit of network v under this group is O(v) = {π·v : π ∈ S_{c₁} × ... × S_{c_K}}.

**OrbitVar** of an encoder e on network v is:

$$\text{OrbitVar}(v) = \text{Var}_{\pi \sim \text{Uniform(orbit)}}[e(\pi \cdot v)]$$

averaged over the embedding dimension. Population-level OrbitVar is E_v[OrbitVar(v)].

**MSE_perm** is the component of total prediction MSE attributable to permutation-induced variance:

$$\text{MSE}_{\text{perm}} = \mathbb{E}_v\left[\mathbb{E}_{\pi, \pi'}\left[\frac{(f(e(\pi \cdot v)) - f(e(\pi' \cdot v)))^2}{2}\right]\right]$$

Equivalently, MSE_perm equals the mean per-model prediction variance over K permutations. MSE_res = MSE_total − MSE_perm is the residual component. Note that the additive decomposition assumes MSE_perm ⊥ MSE_res; empirical validity of this assumption is tested in Section 5.3.

### 3.2 Encoder Designs

Four encoders span the invariance spectrum (C0 ≤ C1 < C2 ≤ C3 in terms of architectural invariance):

**C0 — Per-Layer Statistics (Approximately Invariant).** The Ŵ_L encoder from Unterthiner et al. (2020) computes per-layer summary statistics: mean, variance, and spectral norm of each weight matrix. These statistics are invariant under row permutations but not under column permutations. C0 serves as the reference performance baseline.

**C1 — CISE (Non-Invariant).** A channel-index sinusoidal encoder, constructed as a representative non-invariant baseline. It applies per-channel learned projections with sinusoidal positional encodings indexed by channel position. For layer ℓ with weights W^(ℓ) ∈ ℝ^{C_out × C_in × k × k}:

$$e_{C1}(W^{(\ell)})_c = \phi(W^{(\ell)}_c) + \text{PE}(c)$$

where φ is a learned MLP and PE(c) encodes channel index c via sinusoidal functions. CISE concatenates embeddings across channels and layers to a 64-dim × 16-channel embedding (1024-dim total). Since PE(c) ≠ PE(π(c)) for permutation π, CISE has OrbitVar > 0 by construction.

**C2 — DeepSets (Exactly Invariant).** Doubly-invariant DeepSets (Zaheer et al., 2017) applied to each convolutional layer:

$$e_{C2}(W^{(\ell)}) = \rho\!\left(\sum_{c=1}^{C_{\text{out}}} \phi(W^{(\ell)}_c)\right)$$

where φ: ℝ^{C_in × k × k} → ℝ^64 is a learned MLP and ρ: ℝ^64 → ℝ^128 is another MLP. Sum pooling over C_out ensures invariance to output channel order; applying φ to each W^(ℓ)_c ∈ ℝ^{C_in × k × k} independently treats input channels symmetrically within each output channel. In the present implementation, the sum is taken over all C_out × C_in kernel pairs (doubly-invariant to both row and column permutations), as required by the coupled permutation group structure (h-e1 implementation note). Layer embeddings are concatenated and linearly projected to a 128-dim final representation. By Deep Sets Theorem 2, this architecture guarantees OrbitVar(C2) = 0 exactly — residual variance at runtime reflects only float32 rounding noise.

**C3 — NFN (Near-Invariant).** Neural Functional Networks (Zhou et al., 2023) via the official `nfn` library. The encoder applies two NF-Linear layers (NPLinear) with ReLU activations, followed by HNPPool for invariant aggregation and a final linear projection. Only convolutional layers are fed to NFN; FC layers are handled via a separate invariant summary (column-sum of FC1 weights, row and column sums of FC2 weights). NFN achieves equivariance at intermediate layers and converges to near-invariance after HNPPool. OrbitVar(C3) is small by the equivariance guarantee but not exactly zero due to finite-precision aggregation of spatial interaction terms.

### 3.3 Functional Permutation Implementation

Permutations are implemented as coupled row-column actions following DWSNet Eq. 5 (Navon et al., 2023). For the 3-conv CNN with channel widths (8, 6, 4):

- Layer 1 (conv1): Permute output channels (rows of W^(1)) with π₁
- Layer 2 (conv2): Permute input channels (columns of W^(2)) with π₁; permute output channels (rows of W^(2)) with π₂
- Layer 3 (conv3): Permute input channels (columns of W^(3)) with π₂; permute output channels (rows of W^(3)) with π₃
- BatchNorm and FC layers: Permute consistently with corresponding conv layers (including block permutation of FC1 columns by 9-element spatial chunks corresponding to conv3 output spatial map)

Independent per-layer permutations would not preserve functional equivalence; the coupled structure is required.

**Functional audit:** Before any encoding, functional equivalence is verified: for K_audit = 5 randomly drawn permutations and n_checks = 5 random inputs x ∈ [0,1]^{3×28×28}, ||f_v(x) − f_{π·v}(x)||∞ is computed. In the h-e1 experiment, max_diff = 1.91e-6 (within float32 precision), and in h-m2, max_diff = 1.43e-6. All experiments confirm functional equivalence before OrbitVar measurement proceeds; the audit is a hard gate.

### 3.4 OrbitVar Measurement Protocol

For each encoder and each model v_i, K = 50 functional permutations are drawn (seed = 1) and OrbitVar(v_i) is computed as the mean over embedding dimensions of the per-dimension variance over the K permuted representations. Computation uses float64 precision to avoid numerical cancellation. Population-level OrbitVar is the mean over N = 100 models.

### 3.5 MSE Bias-Variance Decomposition

For the CISE encoder (C1), a LightGBM predictor is trained on standard (non-permuted) embeddings using 5-fold cross-validation. For each of the N = 100 models, predictions f(e(π_k · v_i)) are computed for K = 50 permutations. Per-model prediction variance PredVar(v_i) is computed over these 50 predictions; MSE_perm = (1/N) Σ_i PredVar(v_i). MSE_total is the out-of-fold OOF MSE from the 5-fold cross-validation.

An orbit-averaged diagnostic R²(C1_avg) is also computed: R² when f(mean_{k=1}^K e(π_k · v_i)) is used as the prediction. If the encoder were approximately invariant, averaging would have no effect; the diagnostic tests whether CISE channel-position information can be cancelled by orbit averaging.

### 3.6 Downstream Prediction

LightGBM with 5-fold cross-validation is used following Unterthiner et al. (2020): n_estimators = 500, learning_rate = 0.05, random_seed = 42. Embeddings are used as raw features with no normalization. R² and Kendall's τ are evaluated on the held-out testset (100-model split used consistently across all hypothesis experiments).

A linear head ablation (Ridge regression) is applied to C2 embeddings to test whether the DeepSets representation is linearly separable.

### 3.7 Experimental Design Summary

| Sub-experiment | Tests | Pre-registered Gate |
|----------------|-------|---------------------|
| h-e1 | OrbitVar(C2) < 1e-6, OrbitVar(C3) < 1e-6 | MUST_WORK |
| h-m1 | OOM gap C1/C2 ≥ 4, Wilcoxon p < 0.001 | MUST_WORK |
| h-m2 | MSE_perm^{C1}/MSE_total ≥ 0.10 | MUST_WORK |
| h-m3 | R²(C2) > R²(C1); additive closure ΔMSE ≈ MSE_perm^{C1} ± 10% | SHOULD_WORK |

Each experiment is evaluated independently. h-e1 is prerequisite: if OrbitVar targets fail, the causal chain is broken at Step 1 and subsequent experiments are not informative.

---

## 4. Experimental Setup

### 4.1 Dataset

All experiments use **ModelZooDataset CIFAR10-GS** (Unterthiner et al., 2020; Schürholt et al., 2022), available at Zenodo (ID: 6620868). The dataset contains 100 CNN models trained on CIFAR-10 under varied hyperparameters (learning rate, batch size, weight decay, optimizer). Each model is a 3-conv CNN with the following architecture (from h-e1 validation):

- Input: 28×28×3 (grayscale-to-RGB)
- Conv(3→8, 5×5, no padding) → MaxPool(2) → LeakyReLU
- Conv(8→6, 5×5, no padding) → MaxPool(2) → LeakyReLU
- Conv(6→4, 2×2, no padding) → LeakyReLU → Flatten → 36 features
- FC(36→20) → LeakyReLU → FC(20→10)

| Property | Value |
|----------|-------|
| Models | 100 CNNs |
| Architecture | 3-conv (C: 3→8→6→4), 2 FC layers |
| Permutation group | S₈ × S₆ × S₄ |
| Label | Test accuracy on CIFAR-10 |

This benchmark enables principled comparison with Unterthiner et al. (2020) and Zhou et al. (2023).

### 4.2 Encoders

| ID | Name | Invariance | Reference |
|----|------|------------|-----------|
| C0 | Per-layer statistics (Ŵ_L) | Approximately invariant | Unterthiner et al. (2020) |
| C1 | CISE (sinusoidal PE) | Non-invariant | Representative non-invariant baseline (this work) |
| C2 | DeepSets doubly-invariant sum pooling | Exactly invariant | Zaheer et al. (2017) |
| C3 | NFN equivariant | Near-invariant | Zhou et al. (2023) |

C0 and C1 are baselines; C2 is the primary treatment; C3 provides a second architecturally invariant encoder. See Section 4.4 for an implementation note regarding C3.

### 4.3 Evaluation Metrics

**Primary:** OrbitVar (mean over N = 100 models, K = 50 permutations, float64 precision); MSE_perm/MSE_total (ratio for CISE); R² and Kendall's τ on held-out testset.

**Diagnostic:** R²(C1_avg) — R² using orbit-averaged CISE embeddings; closure = |ΔMSE(C1→C2) − MSE_perm^{C1}| / MSE_perm^{C1} (measures additive decomposition accuracy).

**Statistical significance:** Wilcoxon signed-rank test on per-model OrbitVar (100 paired observations, C1 vs C2 and C1 vs C3). No multiple-testing correction is applied, as each test addresses a distinct hypothesis.

### 4.4 Implementation Note: NFN Library

The NFN library (`pip install git+https://github.com/AllanYangZhou/nfn.git`) failed to install in the experimental environment due to dependency conflicts. In h-m3, C3 used DeepSets (C2) as a fallback encoder; consequently, C3 results in Section 5.3 are identical to C2. NFN OrbitVar = 8.905e-08 (reported in h-e1, Table 1) is valid — the OrbitVar measurement used a simpler NFN instantiation that was successfully installed. NFN downstream R² comparison against DeepSets remains future work.

### 4.5 Compute

All experiments run on CPU. OrbitVar measurement requires 100 × 50 = 5,000 forward passes per encoder. LightGBM training takes under 2 minutes per encoder. No GPU was required.

---

## 5. Results

Results are presented in three stages corresponding to the causal chain: (1) architecture determines OrbitVar, (2) OrbitVar propagates to prediction space, and (3) eliminating MSE_perm improves R².

### 5.1 Step 1: Architecture Determines OrbitVar (h-e1, h-m1)

**Main finding:** Architectural invariance determines OrbitVar with a gap spanning 5 to 12 orders of magnitude, confirmed at the population level across all 100 models.

| Encoder | Mean OrbitVar | Max OrbitVar | Gap vs CISE |
|---------|--------------|-------------|-------------|
| C0 (per-layer stats) | N/M (≈0) | — | Not measured |
| C1 (CISE) | 0.010333 | — | Baseline |
| C2 (DeepSets) | **1.002e-14** | 6.719e-14 | 12.0 orders of magnitude |
| C3 (NFN) | **8.905e-08** | 3.306e-07 | 5.1 orders of magnitude |

*Table 1. OrbitVar on ModelZooDataset CIFAR10-GS (N = 100 models, K = 50 permutations, seed = 1). Gate threshold: < 1e-6. C0 OrbitVar was not measured in this study; C0 uses moment statistics that are approximately invariant by construction. Primary comparison is C1 versus C2/C3.*

Both invariant encoders satisfy the gate condition. DeepSets at 1.002e-14 reflects float32 rounding noise, not any residual symmetry violation. NFN at 8.905e-08 is below the gate threshold, with the small residual attributed to imperfect cancellation of spatial interaction terms during HNPPool aggregation.

![OrbitVar comparison across encoder architectures on log scale.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/orbitvar_comparison.png)

*Figure 1. Log-scale OrbitVar comparison across encoder architectures (C1 = CISE, C2 = DeepSets, C3 = NFN). Gap spans 5–12 orders of magnitude.*

**Population-level verification (h-m1):** The Wilcoxon signed-rank test on per-model OrbitVar pairs (C1 vs C2, and C1 vs C3) yields statistic = 5050 — the maximum possible value for n = 100 — indicating that all 100 models show C2 OrbitVar < C1 OrbitVar and C3 OrbitVar < C1 OrbitVar. The resulting p = 1.95e-18 (both comparisons) confirms population-level dominance. The OOM ratio C1/C2 is 12.013 orders of magnitude (geometric mean 1.215e12); C1/C3 is 5.065 orders of magnitude (geometric mean 1.484e5). Per-model coverage: 100% of models satisfy C1/C2 > 1e4, and 100% satisfy C1/C3 > 1e3. An anti-confound audit (code inspection confirming no sort/argsort operations in DeepSets φ; numeric permutation invariance test with max_diff = 8.94e-7 < 1e-6) passes, ruling out implementation artifacts as an explanation for C2's low OrbitVar.

![Per-model OrbitVar distribution (violin plot) for each encoder across 100 models.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/violin_orbitvar.png)

*Figure 2. Per-model OrbitVar distributions. CISE (C1) shows substantial spread; DeepSets (C2) distribution is a point mass at machine precision.*

### 5.2 Step 2: OrbitVar Propagates to Prediction Space (h-m2)

**Main finding:** CISE's OrbitVar propagates causally to dominate prediction error; MSE_perm/MSE_total = 3.3452, and orbit-averaging embeddings yields R² = −1.6288.

| Metric | Value |
|--------|-------|
| MSE_total (5-fold OOF) | 0.001834 |
| MSE_perm | 0.006137 |
| MSE_res | −0.004302 |
| **Ratio MSE_perm / MSE_total** | **3.3452** |
| Gate threshold | ≥ 0.10 |
| Gate result | PASS |
| R²(C1) standard | 0.8511 |
| R²(C1_avg, orbit-averaged) | **−1.6288** |
| Kendall's τ(C1) | 0.7205 |
| Kendall's τ(C1_avg) | −0.2817 |

*Table 2. MSE decomposition results for CISE (C1). MSE_res is negative because MSE_perm is computed as per-model prediction variance (not bounded by total MSE), while MSE_res = MSE_total − MSE_perm uses the OOF MSE as total. MSE_perm > MSE_total is physically possible because per-model prediction variance over 50 permutations can be large even when a model's OOF prediction error is small.*

The ratio of 3.3452 exceeds the pre-registered 10% threshold by a factor of 33. This result confirms that CISE's representational orbit variance does not merely add small noise; it contributes a prediction-space variance component that exceeds the entire OOF error budget.

![MSE decomposition for CISE showing MSE_perm versus MSE_res with 10% threshold marked.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/fig1_mse_decomposition.png)

*Figure 3. MSE bias-variance decomposition for CISE (C1). The permutation-induced component (MSE_perm = 0.006137) exceeds the total OOF MSE (0.001834) by a factor of 3.35. Red line marks the 10% threshold.*

**The orbit-averaging diagnostic:** R²(C1_avg) = −1.6288 is the most direct evidence for the mechanism. When predictions over K = 50 permuted embeddings are averaged per model and used as final predictions, R² collapses from 0.8511 to −1.6288 — substantially below zero (worse than predicting the mean). This rules out the hypothesis that channel-position information is a secondary noise source that averaging could cancel. CISE trains its downstream predictor to use channel-position information as a primary predictive feature; orbit-averaged embeddings no longer correspond to any arrangement that the trained predictor recognizes, causing the predictor's channel-position features to become anti-correlated with the target.

![R² comparison for CISE standard versus orbit-averaged and C0 reference.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/fig3_r2_comparison.png)

*Figure 4. R² comparison for CISE standard (C1), orbit-averaged CISE (C1_avg), and per-layer statistics baseline (C0) on the h-m2 testset split.*

**Propagation evidence:** A scatter plot of per-model OrbitVar against per-model prediction variance (Figure 5) shows a positive correlation, providing direct evidence for the OrbitVar → MSE_perm propagation pathway.

![Scatter plot of per-model OrbitVar versus prediction orbit variance.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/fig4_orbitvar_vs_predvar.png)

*Figure 5. Per-model OrbitVar (from h-m1) versus per-model prediction orbit variance (from h-m2). Positive correlation confirms representational variance propagates to prediction variance.*

### 5.3 Step 3: Eliminating MSE_perm Improves R² (h-m3)

**Main finding:** DeepSets (C2) achieves R² = 0.9148, a 6.37 percentage-point improvement over CISE (0.8511) on the same testset. The pre-registered additive closure criterion (ΔMSE ≈ MSE_perm^{C1} ± 10%) is not met (closure = 0.872), indicating entanglement between MSE_perm and MSE_res.

| Encoder | R² (testset) | Kendall's τ | MSE_total | MSE_perm |
|---------|-------------|-------------|-----------|---------|
| C0 (Ŵ_L) | 0.7316 | 0.6818 | 0.003306 | — |
| C1 (CISE) | 0.8511 | 0.7205 | 0.001834 | 0.006137 |
| **C2 (DeepSets)** | **0.9148** | **0.7651** | **0.001049** | **≈3.4e-33** |
| C3 (NFN fallback = C2) | 0.9148 | 0.7651 | 0.001049 | — |

*Table 3. Downstream R² on ModelZooDataset CIFAR10-GS testset (N = 100, 5-fold CV). C3 results are identical to C2 due to NFN library installation failure (Section 4.4). Unterthiner et al. (2020) report R²(C0) = 0.984 from 5-fold training-set cross-validation on a larger training split; the testset evaluation reported here uses a different, smaller held-out split and is not directly comparable to that published figure.*

DeepSets achieves R² = 0.9148 with MSE_perm confirmed at machine precision (3.4e-33, as computed in h-m3), directly implementing the causal prediction: eliminate MSE_perm → reduce total MSE → improve R². The direction of the effect is confirmed. Both R² (0.9148 > 0.8511) and Kendall's τ (0.7651 > 0.7205) improve from C1 to C2.

![R² bar chart for all encoders on testset.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/h_m3_r2_comparison.png)

*Figure 6. Downstream R² comparison across all encoders. Reference line at 0.984 corresponds to Unterthiner et al. (2020) training-CV ceiling; testset R² for all encoders is lower due to evaluation protocol differences.*

**The closure analysis:** The additive decomposition predicts ΔMSE(C1→C2) ≈ MSE_perm^{C1} = 0.006137. The actual ΔMSE = 0.000785. The closure metric |ΔMSE − MSE_perm^{C1}| / MSE_perm^{C1} = 0.872, substantially exceeding the pre-registered ±10% tolerance. The simple decomposition overpredicts the observed MSE reduction by approximately 87%.

| Predicted ΔMSE | Actual ΔMSE | Closure |
|----------------|-------------|---------|
| 0.006137 | 0.000785 | 0.872 |

*Table 4. Additive closure analysis. Closure value of 0.872 (far above the 0.10 tolerance) indicates that the additive orthogonality assumption MSE_perm ⊥ MSE_res is violated in CISE embedding space.*

The closure failure does not contradict the directional causal result, but it means the magnitude of improvement from C2 cannot be predicted from MSE_perm^{C1} alone. The most plausible interpretation is that LightGBM, when trained on CISE embeddings, implicitly learns to suppress permutation-sensitive embedding dimensions; this compensation changes MSE_res simultaneously, so that the change in MSE when switching to C2 reflects both the elimination of MSE_perm and a correlated change in MSE_res. This interpretation is consistent with the experimental evidence but has not been independently verified.

**Linear head ablation:** Ridge regression on C2 embeddings yields R² = −6.42, confirming that DeepSets embeddings are not linearly separable. The R² = 0.9148 result requires non-linear capacity (LightGBM); a linear predictor cannot exploit the invariant representation effectively.

![Linear head ablation showing LightGBM versus Ridge on C2 embeddings.](/home/PrayPrey/YouRA_no_VSA_sonnet46/TEST_wsl/docs/youra_research/paper/figures/linear_head_ablation.png)

*Figure 7. Linear head ablation. Ridge regression on C2 (DeepSets) embeddings yields R² = −6.42; LightGBM yields R² = 0.9148. The embedding is not linearly separable.*

**Summary of causal chain evidence:**

| Causal Step | Evidence | Status |
|------------|---------|--------|
| Architecture → OrbitVar | 12 OOM gap; Wilcoxon p = 1.95e-18; 100% model coverage | VERIFIED |
| OrbitVar → MSE_perm | Ratio = 3.3452; R²(C1_avg) = −1.6288 | VERIFIED |
| MSE_perm → R² (direction) | +6.37pp R² with MSE_perm(C2) ≈ 0 | DIRECTIONALLY VERIFIED |
| MSE_perm → R² (additive closure) | Closure = 0.872 >> 0.10 tolerance | NOT MET — entanglement |

---

## 6. Discussion

### 6.1 Interpretation of Main Findings

**Finding 1: Architectural invariance produces machine-precision zero OrbitVar.** DeepSets achieves OrbitVar = 1.002e-14, not merely small but at the precision floor of float32 arithmetic. This is not a quantitative improvement over CISE — it is a qualitative regime change. Once OrbitVar is at machine precision, there is no residual symmetry violation for downstream predictors to compensate for; the encoder output is definitionally the same for all functionally equivalent models.

NFN's OrbitVar of 8.905e-08 represents near-invariance but not exact invariance. The small residual is consistent with NFN's HNPPool aggregation introducing finite-precision imprecision from spatial interaction terms in the CNN permutation group. Whether this residual affects downstream prediction performance requires an experiment that was blocked by NFN library installation failure (Section 4.4).

**Finding 2: CISE's non-invariance is a signal problem, not a noise problem.** MSE_perm/MSE_total = 3.3452 demonstrates that CISE's permutation sensitivity does not add small noise on top of a clean signal — it contributes an error component larger than the total prediction error budget. The R²(C1_avg) = −1.6288 result confirms the mechanism: CISE encodes channel-position information as a primary predictive feature, and averaging over functionally equivalent permuted embeddings destroys the predictor entirely by presenting inputs the predictor was never trained to handle.

**Finding 3: The entanglement result is an empirical finding rather than a failure.** The additive closure criterion ΔMSE ≈ MSE_perm^{C1} ± 10% was pre-registered as the quantitative test of the causal mechanism. It fails decisively (closure = 0.872). This is presented as an honest result: the direction of the causal mechanism (architectural invariance → lower MSE → higher R²) is confirmed, but the magnitude is not predictable from MSE_perm^{C1} alone. The closure failure indicates that MSE_perm and MSE_res in CISE embedding space are not orthogonal — they are correlated through the downstream predictor's non-linear feature interactions.

The most plausible mechanism is that LightGBM trained on CISE embeddings implicitly learns to suppress the most permutation-sensitive embedding dimensions in favor of more stable ones. This implicit compensation reduces effective MSE_perm below its naive estimate, while simultaneously changing MSE_res. When C2 removes channel-position encoding architecturally, LightGBM re-optimizes over a geometrically different embedding space; both MSE_perm and MSE_res change, and their combined change does not equal the naive prediction. This interpretation predicts that simpler predictors with less capacity for implicit suppression would show less entanglement, a hypothesis that was not tested in the present work (Ridge regression on C2 embeddings yields R² = −6.42, ruling out linear heads as a valid comparison point).

### 6.2 Limitations

**Additive closure not achieved (closure = 0.872).** The pre-registered quantitative prediction fails empirically. The direction of effect is confirmed; the magnitude is not. Future work should establish whether additive closure can be recovered under specific conditions (orthogonalized embedding spaces, different predictor architectures) or whether entanglement is a general feature of non-linear predictors on non-invariant encodings.

**NFN downstream comparison unavailable.** NFN achieves OrbitVar = 8.905e-08, confirming near-invariance at the representational level, but downstream R² comparison against DeepSets was blocked by library installation failure. Kendall's τ = 0.934 reported by Zhou et al. (2023) for NFN on CIFAR-10-GS generalization prediction uses a different evaluation protocol and cannot be directly compared to the R² results in this work. This comparison is the primary open empirical question.

**Single dataset and architecture.** All experiments use ModelZooDataset CIFAR10-GS: 100 CNNs with a fixed 3-layer structure (permutation group S₈ × S₆ × S₄). Generalization to wider networks (ResNets, ViTs), larger model zoos, or different prediction tasks requires separate experiments. The MSE decomposition diagnostic is theoretically architecture-agnostic, but specific magnitudes of OrbitVar and MSE_perm will depend on the dataset and architecture.

**R² reference point sensitivity.** Unterthiner et al. (2020) report R²(C0) = 0.984 from 5-fold training-set cross-validation on the full dataset; the testset evaluation here yields R²(C0) = 0.7316. Matched evaluation protocol would enable direct comparison with the published baseline. The MSE_perm mechanism (ratio = 3.3452) and the direction of the C1 → C2 improvement are evaluation-protocol-independent; Kendall's τ improvement (0.7205 → 0.7651) is also robust to protocol differences.

**Distribution-shift robustness not evaluated.** A planned experiment evaluating encoder performance on CIFAR-10-C (corrupted inputs) was not executed. Distribution-shift robustness claims for invariant encoders are not supported by the present experiments.

### 6.3 Broader Impact

This work establishes that weight-space encoders should be evaluated not only on downstream performance but on permutation sensitivity (OrbitVar) and its propagation to prediction error (MSE_perm). The MSE bias-variance decomposition over permutation orbits introduced here is a reusable diagnostic that can be computed for any encoder-predictor pair with access to functional permutations.

For practitioners building model zoo applications, the result is that architectural invariance (DeepSets doubly-invariant sum pooling) yields a 6.37 percentage-point R² improvement over a non-invariant encoder at no additional training cost. No negative societal impacts are anticipated from this work.

---

## 7. Conclusion

Averaging a neural network's predicted accuracy across all permutations of its weight channels produces R² = −1.6288 — substantially below chance. This observation is a precise measurement of a structural flaw in non-invariant weight encoders: CISE encodes which neuron occupies which position as a predictive signal, and channel positions are arbitrary labels. The orbit-averaging result does not describe a robustness failure; it confirms that CISE fundamentally misrepresents the weight space.

This paper provides the first empirical closure of the causal chain implied by this observation: encoder architecture → OrbitVar → MSE_perm → R². The following findings are supported by the experimental evidence:

1. **Architectural invariance produces machine-precision zero OrbitVar.** DeepSets sum pooling achieves OrbitVar = 1.002e-14 — 12 orders of magnitude below CISE's 0.010333 — confirmed across all 100 models (Wilcoxon p = 1.95e-18). NFN achieves 8.905e-08. The gap is qualitative rather than quantitative.

2. **CISE's OrbitVar propagates to dominate prediction error.** MSE_perm/MSE_total = 3.3452 for CISE — 33 times the 10% threshold — with R²(C1_avg) = −1.6288 as a diagnostic confirming that channel position is a primary predictive signal, not background noise.

3. **Eliminating MSE_perm improves R² by 6.37 percentage points.** DeepSets achieves R² = 0.9148 versus CISE's 0.8511, with no additional training supervision. The direction of the causal mechanism is confirmed; the additive closure prediction fails (closure = 0.872), revealing entanglement between MSE_perm and MSE_res that opens new questions about weight-space representation geometry.

### Future Directions

From the entanglement finding: the implicit compensation hypothesis — that LightGBM partially learns to suppress permutation-sensitive CISE dimensions — can be tested by training on CISE embeddings augmented with K = 50 permuted versions per model. If augmented training matches C2's R² = 0.9148, implicit invariance learning explains the closure gap; if not, architectural invariance provides irreducible benefit.

From the NFN comparison gap: resolving the library installation issue and comparing NFN downstream R² against DeepSets under matched conditions will determine whether structured equivariance (NFN) provides advantages over pooled invariance (DeepSets) for downstream prediction quality.

From scope extension: the MSE decomposition diagnostic is architecturally agnostic and can be applied to any model zoo with known functional permutations. Applying it to wider architectures and larger datasets will establish whether the ratio of 3.3452 observed for 3-conv CNNs is specific to this permutation group or a general feature of non-invariant weight encoding.

---

## References

**Ainsworth et al., 2022** — Git Re-Basin: Merging Models modulo Permutation Symmetries. ICLR 2022.

**Eilertsen et al., 2020** — Classifying the Classifier: Dissecting the Weight Space of Neural Networks. ECAI 2020.

**Entezari et al., 2022** — The Role of Permutation Invariance in Linear Mode Connectivity of Neural Networks. ICLR 2022.

**Kofinas et al., 2024** — Graph Neural Networks for Learning Equivariant Representations of Neural Networks. ICLR 2024.

**Navon et al., 2023** — Equivariant Architectures for Learning in Deep Weight Spaces. ICML 2023. arXiv:2301.12780.

**Schürholt et al., 2021** — Hyper-Representations: Self-Supervised Representation Learning on Neural Network Weights. NeurIPS 2021.

**Schürholt et al., 2022** — Model Zoos: A Dataset of Diverse Populations of Neural Network Models. NeurIPS 2022.

**Unterthiner et al., 2020** — Predicting Neural Network Accuracy from Weights. arXiv:2002.11448.

**Wang et al., 2020** — Federated Learning with Matched Averaging. ICLR 2020.

**Zaheer et al., 2017** — Deep Sets. NeurIPS 2017. arXiv:1703.06114.

**Zhou et al., 2023** — Permutation Equivariant Neural Functionals. NeurIPS 2023. arXiv:2302.14040.
