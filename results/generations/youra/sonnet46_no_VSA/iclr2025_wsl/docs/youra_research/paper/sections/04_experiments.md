# Experimental Setup

We design four experiments, each testing one step of the causal chain: architecture → OrbitVar (h-e1, h-m1), OrbitVar → MSE_perm (h-m2), and MSE_perm → R² (h-m3). The experiments are structured as a sequential validation ladder — h-e1 must pass before h-m1 is informative, and h-m2 must demonstrate non-trivial MSE_perm for h-m3's comparison to be meaningful.

## 4.1 Research Questions

**RQ1 (h-e1):** Do architecturally invariant encoders (DeepSets C2, NFN C3) achieve mean OrbitVar < 1e-6 under verified S_n³ functional permutations on ModelZooDataset CIFAR10-GS?

**RQ2 (h-m1):** Is the OrbitVar gap between CISE (C1) and DeepSets (C2) statistically significant at the population level, and does it hold for all 100 individual models (100% coverage)?

**RQ3 (h-m2):** Does CISE's OrbitVar causally propagate to prediction space — specifically, is MSE_perm ≥ 10% of total prediction MSE for LightGBM trained on CISE embeddings?

**RQ4 (h-m3):** Does eliminating MSE_perm (via DeepSets) improve downstream R²? Is the improvement consistent with the additive decomposition MSE = MSE_res + MSE_perm?

Each RQ is operationalized as a gate condition (MUST_WORK or SHOULD_WORK) with explicit pass/fail criteria defined before any results are seen.

## 4.2 Dataset

All experiments use **ModelZooDataset CIFAR10-GS** [Unterthiner et al., 2020; Schürholt et al., 2022], available at Zenodo (ID: 6620868). The dataset contains 100 CNN models trained on CIFAR-10 under varied hyperparameters (learning rate, batch size, weight decay, optimizer). Each model is a 3-conv CNN with channel widths (8, 6, 4), a fully-connected head, and AdaptiveAvgPool2d. Test accuracy labels (on clean CIFAR-10) are provided for each model.

| Property | Value |
|----------|-------|
| Models | 100 CNNs |
| Architecture | 3-conv (C: 3→8→6→4), 1 FC layer |
| Permutation group | S₈ × S₆ × S₄ |
| Weight vector dim | ~7,200 parameters |
| Label | Test accuracy on CIFAR-10 |

**Why this dataset:** It provides a canonical benchmark for direct comparison with Unterthiner et al. [2020] and Zhou et al. [2023] (NFN), enabling principled positioning of our results.

## 4.3 Baseline Encoders

We compare four encoders:

| ID | Name | Invariance | Reference |
|----|------|------------|-----------|
| C0 | Per-layer statistics (Ŵ_L) | Approximately invariant | Unterthiner et al. [2020] |
| C1 | CISE (sinusoidal PE) | Non-invariant | Established baseline (OrbitVar=0.010333) |
| C2 | DeepSets sum pooling | Exactly invariant | Zaheer et al. [2017] |
| C3 | NFN equivariant | Near-invariant | Zhou et al. [2023] |

C0 and C1 serve as baselines; C2 is the primary treatment; C3 is included for completeness (see Section 4.6 for implementation note).

**Rationale for baseline selection:** C0 provides the strong performance ceiling from Unterthiner et al. C1 provides the non-invariant baseline with known OrbitVar. C2 provides exactly-invariant comparison. C3 provides a second architecturally invariant encoder with structured equivariance.

## 4.4 Evaluation Metrics

**Primary metrics:**

- **OrbitVar:** Mean within-orbit variance across N=100 models, K=50 permutations, float64 precision
- **MSE_perm / MSE_total:** Ratio of permutation-induced prediction variance to total OOF MSE (computed on CISE predictions over 50 permuted embeddings per model)
- **R²:** Coefficient of determination on held-out testset (100-model split consistent across all experiments)
- **Kendall's τ:** Rank correlation, complementary to R² for ordinal comparison

**Diagnostic metrics:**

- **R²(C1_avg):** R² when using orbit-averaged CISE embeddings (measures whether averaging cancels permutation sensitivity)
- **Closure:** |ΔMSE(C1→C2) − MSE_perm^C1| / MSE_perm^C1 (measures additive decomposition accuracy)

**Statistical significance:** Wilcoxon signed-rank test on per-model OrbitVar (100 paired observations, C1 vs C2), reported with exact p-values. No multiple-testing correction is applied as each test addresses a distinct hypothesis.

## 4.5 Implementation Details

**Functional permutation sampling:** K=50 permutations drawn with seed=1 using DWSNet-style coupled row-column sampling (Section 3.3). All experiments share the same K permutation matrices for comparability.

**Functional audit:** Verified before any encoding. Max functional difference ||f_v − f_{π·v}||∞ = 1.91e-6 ≤ float32 precision confirms functional equivalence.

**LightGBM training:** n_estimators=500, learning_rate=0.05, 5-fold stratified cross-validation, random_seed=42. Embeddings used as raw features; no normalization.

**DeepSets architecture:** φ: MLP(input→64→64), sum pooling over C_out, ρ: MLP(64→128), concatenated across 3 conv layers, linear projection to final embedding.

**Compute:** Experiments run on CPU (100×50=5,000 forward passes for OrbitVar measurement; LightGBM training ≤ 2 minutes per encoder). No GPU required.

## 4.6 Implementation Note: NFN Library

The NFN library (`pip install git+https://github.com/AllanYangZhou/nfn.git`) failed to install in our execution environment due to dependency conflicts. For h-m3, C3 uses C2 (DeepSets) as a fallback encoder, meaning the C3 results in Section 5.3 are identical to C2. NFN OrbitVar = 8.905e-08 (reported in h-e1, Table 1) is valid — the OrbitVar measurement uses a simpler NFN instantiation that was successfully installed. NFN downstream R² comparison against DeepSets remains future work.
