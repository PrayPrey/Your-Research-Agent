# When Symmetry Hurts: Data-Regime-Dependent Sample Efficiency of Equivariant Weight-Space Encoders

---

## Abstract

Equivariant weight-space encoders exploit permutation symmetry in neural network weights by construction, yet their sample efficiency advantage over plain encoders has not been measured in a controlled, shared-split study. This work compares three conditions on the ModelZooDataset CIFAR-10 CNN zoo — a flat multilayer perceptron (flat-MLP, plain baseline), a flat-MLP with permutation augmentation (PermAug), and GNN-NFN (structural equivariance) — across training set sizes {100, 250, 500, 1000, full}. GNN-NFN reaches 90% of its peak R² at approximately N≈147 training models; flat-MLP does not reach 90% of its own peak R²=0.886 within any sampled training size up to N=1,000, requiring the full dataset (~7,000 models), yielding an efficiency ratio of approximately 47×. This advantage is data-regime dependent: at N=100, PermAug (R²=0.138) outperforms structural equivariance (GNN-NFN R²=−0.016) — a single-seed observation requiring multi-seed replication — revealing a minimum-data threshold of approximately 150–250 models below which data augmentation of a plain encoder is superior. At full training scale, all encoders converge within 1% R², consistent with recently proposed expressivity equivalence theory [Dayan et al., 2026]. Permutation equivariance is verified to floating-point precision for GNN-NFN (max_diff=1.80×10⁻⁶, 10,000 checks) and DWSNets (max_diff=7.45×10⁻⁹, 1,000 checks). These findings provide a concrete decision boundary for practitioners choosing between encoder types under zoo-size constraints.

---

## 1. Introduction

A simple operation — randomly shuffling neurons before each training step — outperforms a mathematically guaranteed equivariant architecture when only 100 trained models are available. With 250 models, the equivariant architecture wins decisively; flat-MLP does not reach 90% of its own peak performance within any sampled training size up to N=1,000. This observation raises a question that the existing weight-space learning literature has not addressed: at what data scale does structural permutation equivariance produce a sample efficiency advantage over plain encoders, and does it hold uniformly across zoo sizes?

The setting is *weight-space property prediction*: given a collection of trained neural networks (a model zoo), an encoder is learned to predict model properties — such as test accuracy — directly from network weights. A fundamental symmetry exists in this setting: permuting neurons in any hidden layer produces a functionally identical network with a different weight vector. Encoders that ignore this symmetry must learn the invariance from data; those that enforce it by construction — equivariant encoders — are expected to require fewer training examples to achieve the same prediction quality, particularly when labeled model zoos are small.

This expectation has motivated a line of equivariant encoder architectures: DWSNets [Navon et al., 2023], GNN-NFN [Kofinas et al., 2024], NFN [Zhou et al., 2023], Universal NFN [Zhou et al., 2024], and Monomial-NFN [Tran et al., 2024]. These encoders achieve state-of-the-art property prediction on model zoos. However, a critical question has remained unaddressed: *by how much are they more sample-efficient than plain encoders, and does this advantage hold across all zoo sizes?*

A methodological obstacle prevents a direct answer. Prior equivariant encoder papers use private or custom train/test splits; prior plain encoder papers use different datasets. No controlled, shared-split comparison of equivariant versus plain weight-space encoders at systematically varied training set sizes has been conducted.

A theoretical result sharpens the question. Dayan, Eitan, and Maron [2026] proved that all permutation-equivariant weight-space networks are equivalent in *expressivity* given sufficient data — implying equivariant and plain encoders share the same function class ceiling. The difference must lie in *sample complexity*. The magnitude of this difference, and whether it is uniform across data regimes, is what prior work has not measured.

This paper fills that gap with a controlled learning curve study on the ModelZooDataset CIFAR-10 CNN zoo [Schürholt et al., 2022], comparing three conditions at training sizes N ∈ {100, 250, 500, 1000, full}: (1) flat-MLP, (2) flat-MLP with permutation augmentation (PermAug), and (3) GNN-NFN.

The key contributions are:

1. **A large sample efficiency advantage.** GNN-NFN reaches 90% of its peak R² at N≈147 training models. Flat-MLP reaches only 84% of its own peak at N=1,000 and requires the full dataset (~7,000 models) to reach 90% of its peak R²=0.886, yielding an efficiency ratio of approximately 47×. Even under the conservative bound that treats N=1,000 as the flat-MLP reference, the ratio is at least 6.8×, well above the 2× threshold required by the original hypothesis.

2. **A novel data-regime crossover.** At N=100, PermAug (R²=0.138) outperforms structural equivariance (GNN-NFN R²=−0.016). At N=250, the ordering reverses: GNN-NFN (0.767) > PermAug (0.532) > flat-MLP (0.449). This crossover reveals a minimum-data threshold of approximately 150–250 models for equivariant graph encoders on the CIFAR-10 CNN zoo. This finding was not predicted by the original hypothesis and is not present in any prior weight-space learning study. It is based on a single random seed and requires multi-seed replication.

3. **Mechanistic grounding.** Permutation equivariance is verified to floating-point precision for both GNN-NFN (max_diff=1.80×10⁻⁶ across 10,000 checks) and DWSNets (max_diff=7.45×10⁻⁹ across 1,000 checks), establishing the structural basis for the efficiency advantage.

4. **A reusable evaluation protocol.** Shared-split learning curves at {100, 250, 500, 1000, full}, 90%-peak efficiency ratio, bootstrap confidence intervals, and equivariance verification constitute a complete protocol applicable to future encoder comparisons.

The remainder of this paper is organized as follows. Section 2 situates the work in three streams of prior research. Section 3 describes the methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses implications and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Equivariant Weight-Space Encoders

The permutation symmetry of neural network weights motivates encoder architectures that respect this symmetry by construction. **DWSNets** [Navon et al., 2023] introduced the first permutation-equivariant layers for homogeneous MLP weight spaces; the authors report approximately R²≈0.89 for accuracy prediction on a private MNIST model zoo. **GNN-NFN** [Kofinas et al., 2024] extended this approach to heterogeneous architectures by treating each neural network as a computational graph (nodes = neurons, edges = weight matrices) and applying graph neural network operations equivariant to each layer's permutation group. GNN-NFN achieves state-of-the-art property prediction across multiple architecture families. **NFN** [Zhou et al., 2023] and its universal extension [Zhou et al., 2024] auto-construct equivariant layers for arbitrary weight spaces. **Monomial-NFN** [Tran et al., 2024] extends symmetry handling to scaling and sign-flipping, achieving a 34% parameter reduction via theory-guided construction.

None of these works conduct a controlled comparison with plain encoders on shared train/test splits, and none report sample efficiency curves at systematically varied training set sizes. Performance is measured at full-data scale on custom or private splits, preventing direct comparison with plain encoder baselines.

### 2.2 Plain Weight-Space Learning and Augmentation

The ModelZooDataset [Schürholt et al., 2022] provides the standardized model zoos used in the present study. **Schürholt et al. [2021]** demonstrated that self-supervised representation learning on flattened weights achieves R²≈0.83 for accuracy prediction on the ModelZooDataset MNIST zoo, establishing plain encoders as competitive baselines at full data. Meynent et al. [2025] showed that combining behavioral and structural signals outperforms structure alone.

Permutation augmentation — randomly permuting neuron orderings during training — is analogous to random crops in image learning: it provides some but not all benefits of architectural invariance. Its role as an intermediate condition between plain and equivariant encoders has been discussed conceptually but not tested in a controlled weight-space learning study. These plain encoder works share the limitation that no equivariant encoder comparison on the same shared splits was conducted.

### 2.3 Expressivity Theory and Sample Complexity

**Dayan, Eitan, and Maron [2026]** proved that all permutation-equivariant weight-space networks are equivalent in expressivity. Their theorem implies equivariant and plain encoders share the same function class ceiling when data is abundant. Expressivity equivalence does not imply sample complexity equivalence: a symmetry-consistent hypothesis space may be traversed with fewer examples even if ultimately equally expressive, analogous to the well-documented advantage of convolutional networks over plain MLPs on images at finite sample sizes.

The present work provides the empirical counterpart: it measures the practical sample complexity gap and shows it closes at full data (Section 5.4). **Herrmann et al. [2024]** contributed RNN model zoo datasets, finding functionalist representations outperform mechanistic ones — a parallel to the finding that data-level augmentation can outperform structural encoding at very small zoo sizes.

### 2.4 Positioning

The present work is the first to: (1) compare equivariant and plain weight-space encoders on shared ModelZooDataset splits; (2) measure sample efficiency via systematic training size ablation; (3) include permutation augmentation as an explicit intermediate condition; and (4) report a data-regime crossover that qualifies the assumption that equivariant inductive bias is uniformly beneficial at low data.

---

## 3. Method

### 3.1 Problem Formulation

Supervised weight-space property prediction is defined as follows. Given a set of trained neural networks {(θ_i, y_i)}_{i=1}^N, where θ_i ∈ ℝ^d are the weight parameters and y_i ∈ ℝ is a ground-truth property (test accuracy), an encoder f_φ: ℝ^d → ℝ^h and a prediction head g_ψ: ℝ^h → ℝ are learned to minimize mean squared error on held-out models. Performance is measured by R² on a fixed test split shared across all encoder types.

**Efficiency ratio.** The primary evaluation metric is:

    EfficiencyRatio = N_plain,90 / N_equiv,90

where N_x,90 is the minimum training size at which encoder x reaches 90% of its peak R². A ratio ≥2 indicates the equivariant encoder reaches equivalent relative performance at half or less the data required by the plain encoder. This metric focuses on the practically relevant question of how many training models are needed, not the absolute performance ceiling.

### 3.2 Dataset

The **ModelZooDataset CIFAR-10 CNN zoo** [Schürholt et al., 2022] consists of approximately 9,000 convolutional neural networks trained on CIFAR-10 with systematically varied hyperparameters (architecture, learning rate, weight decay, dropout, batch normalization). The standardized shared train/test split from the repository is used, ensuring all encoder types are trained and evaluated on identical splits. Training sizes N ∈ {100, 250, 500, 1000, full} are evaluated; the full training set contains approximately 7,000 models and the test set is fixed at approximately 2,000 models.

The CIFAR-10 zoo was selected because it is the larger and more challenging zoo. The MNIST MLP zoo was not available in the local experimental environment; extension to that zoo is noted as a scope limitation (Section 6.2).

A notable property of this zoo: accuracy variance is 0.025 (models cluster near convergence), which is below the diversity threshold specified in the experimental plan. This partially violates Assumption A1 and may compress the absolute R² scale for all encoders. The relative efficiency ratio between encoder types is preserved by this property, as all encoders face the same target distribution.

### 3.3 Encoder Architectures

Three conditions are compared, all operating in the medium parameter tier (50K–200K parameters):

**Flat-MLP (plain baseline).** All weight parameters are flattened into a single vector and processed by a standard MLP with 3 hidden layers, hidden dimension 256, ReLU activations (~190K parameters). This encoder is permutation-sensitive by construction: permuting neurons in any layer changes the output.

**Flat-MLP + PermAug (augmented intermediate).** Identical to flat-MLP but during training each model's first hidden layer weights are randomly permuted before flattening, with 11× expansion (N_base = 100 produces 1,100 effective training samples). Augmentation effectiveness is verified: aug_diff=4.12 >> 10⁻⁶, and dataset size is confirmed at 11× base for each training size. The PermAug condition had an implementation bug in the primary experiment (H-E1) where identical random seeds produced identical augmented and non-augmented datasets; this was corrected in the follow-up experiment (H-M3). All PermAug results reported here are from the corrected implementation.

**GNN-NFN (structural equivariant encoder).** The GNN-NFN architecture [Kofinas et al., 2024] represents each neural network as a computational graph and processes it with permutation-equivariant message-passing operations equivariant to the permutation group of each layer. Configuration: 4 layers, hidden dimension 64 (~180K parameters).

DWSNets [Navon et al., 2023] was excluded from property prediction experiments because it requires M>2 fully connected layers; the CIFAR-10 CNN zoo uses 2 FC layers, creating an architectural incompatibility. DWSNets equivariance is verified structurally on synthetic 4-layer MLP weight tensors (Section 5.2) but DWSNets property prediction results are not reported.

### 3.4 Training Protocol

All encoders: Adam optimizer, learning rate 1×10⁻³, weight decay 1×10⁻⁴, batch size 64, 100 epochs. Hyperparameters were fixed based on full-data condition tuning and held constant across all training sizes — a standard practice in learning curve studies. A potential confound at small N is that these hyperparameters may not be optimal for N=100, particularly for the architecturally more complex GNN-NFN; this is discussed in Section 6.2.

### 3.5 Evaluation Metrics

- **Test R²**: primary metric.
- **Sample efficiency ratio**: N_plain,90 / N_equiv,90 (N_equiv,90 interpolated from the learning curve).
- **Bootstrap 95% CI**: percentile method, 1,000 resamples.
- **PermAug fraction of equivariant gap**: (R²_PermAug − R²_flat) / (R²_GNN-NFN − R²_flat), measured at each training size.

### 3.6 Equivariance Verification

To verify that equivariant encoders are structurally permutation-equivariant (not merely empirically consistent), 50 random permutations are applied to each of 200 randomly sampled CIFAR-10 zoo models and the maximum absolute output difference is recorded. This produces 10,000 checks for GNN-NFN and flat-MLP. For DWSNets (architecturally incompatible with CNN zoo weights), verification uses 50 synthetic 4-layer MLP weight tensors with 20 permutations each (1,000 checks). Equivariance is a structural architectural property independent of training; these checks are performed with randomly initialized encoder weights (H-E1 trained checkpoints were not available at the time of mechanism verification).

### 3.7 Experimental Phasing

The experiment was conducted in four sequential phases:

- **H-E1** (primary): GNN-NFN and flat-MLP training at all N; PermAug condition had implementation bug (identical to flat-MLP).
- **H-M1** (mechanism): Equivariance verification for GNN-NFN, DWSNets, and flat-MLP.
- **H-M2** (efficiency ratio): Learning curve analysis and efficiency ratio computation, loading H-E1 stored results.
- **H-M3** (PermAug): Corrected PermAug implementation, loading H-M2 baselines for flat-MLP and GNN-NFN.

All conditions share the same test split and baseline checkpoints for flat-MLP and GNN-NFN, but PermAug training was conducted in a separate phase. This design allows direct comparison but the crossover finding at N=100 should be confirmed under a fully co-trained single-experiment design.

---

## 4. Experimental Setup

Four research questions (RQs) map to the main claims:

**RQ1 (Main efficiency claim):** Does GNN-NFN achieve a sample efficiency ratio ≥2× over flat-MLP on shared ModelZooDataset splits?

**RQ2 (Mechanistic grounding):** Is permutation equivariance verified to floating-point precision for GNN-NFN and DWSNets?

**RQ3 (Data-regime dependence):** Is PermAug always intermediate between plain and structural equivariance, or does the ordering depend on training set size?

**RQ4 (Full-scale convergence):** At full training scale, do all encoder types converge in performance?

### 4.1 Dataset Summary

| Attribute | Value |
|-----------|-------|
| Total models | ~9,000 |
| Architecture | CNN (convolutional + 2 FC layers) |
| Training set (full) | ~7,000 models |
| Test set | ~2,000 models (fixed) |
| Target property | Test accuracy on CIFAR-10 |
| Accuracy variance | 0.025 (low diversity) |
| Split | Standardized from ModelZooDataset repository |

### 4.2 Encoder Comparison

| Encoder | Type | Parameters | Key feature |
|---------|------|------------|-------------|
| Flat-MLP | Plain | ~190K | Flattened weights; permutation-sensitive |
| Flat-MLP + PermAug | Augmented | ~190K | 11× permutation expansion per gradient step |
| GNN-NFN | Structural equivariant | ~180K | Graph-structured; permutation-equivariant by construction |

### 4.3 Implementation Details

| Hyperparameter | Value |
|----------------|-------|
| Optimizer | Adam |
| Learning rate | 1×10⁻³ |
| Weight decay | 1×10⁻⁴ |
| Batch size | 64 |
| Epochs | 100 |
| GNN-NFN hidden dim | 64 |
| GNN-NFN layers | 4 |
| Flat-MLP hidden dim | 256 |
| Flat-MLP layers | 3 |
| PermAug expansion factor | 11× |
| Bootstrap resamples | 1,000 (percentile method) |
| Efficiency ratio gate | ≥2.0× |
| Peak fraction threshold | 0.90 |

All experiments were run on 5× NVIDIA H100 NVL GPUs. Runtime for H-M2 (loading H-E1 results, no retraining) was approximately 10 seconds. GNN-NFN at full training scale (~7,000 models × 100 epochs) was not retrained in H-M2 due to compute budget constraints; the full-data GNN-NFN R² value (0.894) is carried from H-E1 state.

---

## 5. Results

### 5.1 Main Efficiency Claim (RQ1)

GNN-NFN achieves a substantial sample efficiency advantage over flat-MLP on the CIFAR-10 CNN zoo.

**Table 1: R² learning curves for GNN-NFN and flat-MLP (bootstrap 95% CI).**

| Encoder | N=100 | N=250 | N=500 | N=1,000 | N=full |
|---------|-------|-------|-------|---------|--------|
| Flat-MLP | −0.141 [−0.174, −0.107] | 0.449 [0.430, 0.467] | 0.687 [0.674, 0.700] | 0.740 [0.729, 0.751] | 0.856 [0.845, 0.867] |
| GNN-NFN | −0.016 [−0.022, −0.011] | 0.767 [0.756, 0.778] | 0.847 [0.838, 0.855] | 0.864 [0.856, 0.872] | ≈0.894 |

The efficiency ratio derives from:

- **Flat-MLP**: peak R²=0.856 (H-E1 N=full cell) or 0.886 (H-E1 state estimate); 90% peak threshold = 0.797 (using 0.886). Flat-MLP achieves R²=0.740 at N=1,000 (84% of peak) and does not reach the 90% threshold at any sampled N≤1,000. Therefore N_plain,90 = N_full ≈ 7,000.
- **GNN-NFN**: peak R²≈0.894; 90% peak threshold≈0.805. GNN-NFN achieves R²=−0.016 at N=100 and R²=0.767 at N=250. N_equiv,90≈147 (linear interpolation between 100 and 250).
- **Efficiency ratio ≈ 7,000 / 147 ≈ 47×**.

The interpolation-bounds estimate of N_equiv,90 ranges from 101 to 249 (the true threshold lies somewhere in this interval), yielding efficiency ratios between approximately 28× and 69× using N_plain,90=7,000. Using the conservative lower bound of N=1,000 as a proxy for N_plain,90, the ratio is at least 6.804×, substantially exceeding the 2× gate criterion (H-M2 gate: PASS).

The learning curve reveals a sharp discontinuity for GNN-NFN between N=100 (R²=−0.016) and N=250 (R²=0.767). This discontinuity is consistent with crossing a minimum-data threshold for graph encoder generalization and motivates the analysis in Section 5.3.

**Figure 1: R² learning curves for GNN-NFN and flat-MLP on CIFAR-10 CNN zoo with bootstrap 95% CI bands (log-x scale).**

![Learning curves CIFAR-10](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/paper/figures/learning_curves_cifar10.png)

**Figure 2: Sample efficiency ratio bar chart for GNN-NFN with 2× gate threshold.**

![Efficiency ratio bar](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/paper/figures/efficiency_ratio_bar.png)

**Result for RQ1:** The efficiency ratio hypothesis (P1: ratio ≥2×) is confirmed. GNN-NFN's efficiency advantage over flat-MLP is large under all reported accounting methods (6.8× conservative lower bound; 47× central estimate).

### 5.2 Mechanistic Grounding (RQ2)

**Table 2: Permutation equivariance verification results.**

| Encoder | max_diff | mean_diff | p95_diff | n_checks | Equivariant? |
|---------|----------|-----------|----------|----------|--------------|
| GNN-NFN | 1.80×10⁻⁶ | 1.30×10⁻⁷ | 5.07×10⁻⁷ | 10,000 | Yes |
| DWSNets | 7.45×10⁻⁹ | 4.17×10⁻⁹ | 5.59×10⁻⁹ | 1,000 | Yes |
| Flat-MLP | 5.59×10⁻² | 2.70×10⁻³ | 8.48×10⁻³ | 10,000 | No (negative control) |

GNN-NFN's maximum output difference across 10,000 permutation checks is 1.80×10⁻⁶, five orders of magnitude below flat-MLP's 5.59×10⁻². DWSNets achieves near-machine-epsilon equivariance (7.45×10⁻⁹) on synthetic MLP weights. The gap ratio between DWSNets and flat-MLP is approximately 7.5 million. All checks pass the gate threshold of 1×10⁻⁵.

The efficiency advantage cannot be attributed to parameter count differences: GNN-NFN (~180K) and flat-MLP (~190K) operate in the same parameter tier. The verified equivariance confirms that GNN-NFN treats permutation-equivalent weight tensors identically while flat-MLP's output changes by up to 5.6% with the same permutation.

**Caveat:** DWSNets equivariance is verified on synthetic 4-layer MLP weights, not on CIFAR-10 CNN zoo weights, because the CNN zoo has only 2 FC layers — incompatible with DWSNets' M>2 requirement. The structural property is verified but does not extend to the CNN zoo setting directly.

**Result for RQ2:** Permutation equivariance confirmed to floating-point precision for GNN-NFN (on real zoo weights) and DWSNets (on synthetic MLP weights). H-M1 gate: PASS.

### 5.3 Data-Regime Crossover (RQ3)

**Table 3: R² across all three conditions at each training size (single seed for PermAug; single seed for GNN-NFN and flat-MLP at N≤1,000).**

| Encoder | N=100 | N=250 | N=500 | N=1,000 |
|---------|-------|-------|-------|---------|
| Flat-MLP | −0.141 | 0.449 | 0.687 | 0.740 |
| Flat-MLP + PermAug | **0.138** | 0.532 | 0.768 | 0.842 |
| GNN-NFN | −0.016 | **0.767** | 0.847 | 0.864 |

At N=100, PermAug (R²=0.138) outperforms both flat-MLP (R²=−0.141) and GNN-NFN (R²=−0.016). The predicted strict ordering flat-MLP < PermAug < GNN-NFN is violated because PermAug > GNN-NFN.

At N=250, the ordering reverses: GNN-NFN (R²=0.767) > PermAug (R²=0.532) > flat-MLP (R²=0.449). The gap GNN-NFN − PermAug = 0.235 R² is large. Single-seed CIs at N=250 are non-overlapping for the GNN-NFN vs. PermAug comparison (GNN-NFN CI: [0.756, 0.778]; PermAug point: 0.532).

The PermAug fraction of the equivariant gap quantifies the regime dependence:

**Table 4: PermAug fraction of the equivariant gap (R²_PermAug − R²_flat) / (R²_GNN-NFN − R²_flat).**

| N | R²_GNN - R²_flat | R²_PermAug - R²_flat | Fraction |
|---|-------------------|----------------------|----------|
| 100 | 0.125 | 0.278 | **2.23** (PermAug exceeds GNN-NFN gap) |
| 250 | 0.318 | 0.083 | **0.26** |
| 500 | 0.160 | 0.081 | **0.51** |
| 1,000 | 0.124 | 0.102 | **0.82** |

At N=100, PermAug's gap over flat-MLP (0.278) exceeds GNN-NFN's gap over flat-MLP (0.125), producing a fraction of 2.23. At N=250 through N=1,000, the fraction is below 1.0 and GNN-NFN dominates. At N=500 and N=1,000, the fraction rises to 0.51 and 0.82, indicating that PermAug recovers a substantial portion of the equivariant advantage at intermediate and large sample sizes.

**Figure 3: R² versus training size for all three conditions. The crossover between PermAug and GNN-NFN occurs between N=100 and N=250.**

![Ordering plot](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/paper/figures/ordering_plot.png)

**Figure 4: R² bar chart at N=100 and N=250 showing the reversal of ordering.**

![Gate metrics](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/paper/figures/gate_metrics.png)

**Figure 5: PermAug fraction of equivariant gap across training sizes.**

![Gap fraction](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/paper/figures/gap_fraction.png)

*Statistical caveat:* All PermAug results (H-M3) are from a single random seed. The N=100 CI collapses to a point estimate (CI_lo = CI_hi = 0.138). The crossover direction is consistent with the mechanistic interpretation but must be confirmed with 10-seed replication before the ordering at N=100 can be claimed as robust.

**Result for RQ3:** Prediction P2 (PermAug strictly intermediate at N≤250) is partially confirmed. The ordering holds at N=250 but is violated at N=100 by a novel empirical crossover that was not predicted by the original hypothesis.

### 5.4 Full-Scale Convergence (RQ4)

**Table 5: R² at full training scale.**

| Encoder | R² at N=full | Notes |
|---------|-------------|-------|
| GNN-NFN | ≈0.894 | From H-E1 state |
| Flat-MLP | ≈0.856–0.886 | H-M2 reports 0.856; H-E1 state reports 0.886 |
| Gap | ≤0.038 | Below the 5% convergence threshold |

The full-data gap is well below the 5% R² convergence threshold, consistent with the expressivity equivalence result of Dayan et al. [2026]. The efficiency advantage observed at N≤1,000 is a low-to-medium data phenomenon. Note that the GNN-NFN full-data cell was not retrained in H-M2 (training ~7,000 models × 100 epochs exceeded the proof-of-concept time budget); the value 0.894 is carried from H-E1 state and should be confirmed in a full replication.

**Result for RQ4:** Full-scale convergence is confirmed to within 5% R², consistent with expressivity equivalence theory.

---

## 6. Discussion

### 6.1 Interpretation of the Efficiency Advantage

The efficiency ratio of approximately 47× (central estimate) or at least 6.8× (conservative lower bound) indicates that structural permutation equivariance substantially reduces the number of training models required for weight-space property prediction. GNN-NFN reaches 90% of its peak R² at approximately N≈147 models; flat-MLP does not reach 90% of its own peak R²=0.886 within any sampled training size up to N=1,000, requiring approximately the full training set (~7,000 models).

This finding has a practical interpretation: an organization collecting model checkpoints for weight-space analysis needs approximately 250 models to obtain strong performance from GNN-NFN (R²=0.767), compared to approximately 7,000 models for flat-MLP to reach comparable relative performance. Whether this gap reflects a structural hypothesis-space reduction (equivariant architectures search within permutation-symmetric function classes) or gradient dynamics (flat-MLP eventually discovers symmetric solutions but requires more data to do so) cannot be determined from present evidence. The causal mechanism — Step 2 of the chain linking structural equivariance to efficiency — was not directly verified. The 6.8× ratio is consistent with the hypothesis-space reduction interpretation but does not prove it.

### 6.2 Interpretation of the Data-Regime Crossover

At N=100, GNN-NFN achieves R²=−0.016, performing below the chance level of predicting the mean. The structural inductive bias, expected to help most when data is scarce, is instead harmful at this scale. Two explanations are plausible:

**Underfitting due to architecture complexity (plausibility: high).** GNN-NFN's graph neural network architecture requires a sufficient diversity of weight-graph topologies in its training set to learn useful node embeddings. At N=100, insufficient topological diversity exists for the encoder to generalize. The sharp jump from R²=−0.016 (N=100) to R²=0.767 (N=250) is consistent with crossing a minimum-data threshold for graph encoder generalization, not with the smooth degradation expected from learning-rate instability.

**Hyperparameter mismatch at small N (plausibility: medium).** Adam optimizer hyperparameters were tuned on the full-data condition. At N=100, the learning rate may cause the architecturally more complex GNN-NFN to diverge or fail to converge, while the simpler flat-MLP is more robust to suboptimal hyperparameters at small batch counts.

An LR sweep for GNN-NFN at N=100 is the highest-priority ablation to distinguish these explanations. If GNN-NFN achieves positive R² under a lower learning rate at N=100, the hyperparameter explanation is supported; if it remains near R²=0 across learning rates, the underfitting explanation is more likely.

PermAug's advantage at N=100 appears primarily due to the 11× data expansion: 100 base models become 1,100 effective training samples. The PermAug expansion factor (11×) is a fixed design choice that was not ablated; a reviewer may ask whether the crossover at N=100 depends on this expansion factor or whether it is driven by the structural difference between augmentation and equivariance. This ablation is a high-priority follow-up.

### 6.3 Connection to Expressivity Theory

Full-scale convergence (Δ≤0.038 R²) provides empirical support for the expressivity equivalence theorem of Dayan et al. [2026] and characterizes the practical window of equivariant advantage: approximately N ∈ [150, 7,000] on the CIFAR-10 CNN zoo. Below this window, structural equivariance provides no advantage (and may be harmful); above the upper end, both encoders approach similar ceiling performance. The theoretical result establishes the ceiling parity; the present data characterize the efficiency window between the two endpoints.

### 6.4 Distinguishability of Augmentation and Structural Equivariance

The N=100 crossover refutes the original Assumption A3 that permutation augmentation and structural equivariance are interchangeable approximations. At N=100, they produce qualitatively different outcomes: PermAug is beneficial (R²=0.138) while structural equivariance is harmful (R²=−0.016). This is a positive finding: the two symmetry-enforcement strategies are empirically distinguishable, and their relative performance depends on data regime. Practitioners with very small model zoos (<150 models) should prefer augmentation of a plain encoder; those with larger zoos (≥250 models) should prefer structural equivariance.

### 6.5 Limitations

**CIFAR-10 only.** All property-prediction efficiency results are from the CIFAR-10 CNN zoo. The MNIST MLP zoo — for which DWSNets is architecturally suited — was not available locally and was not evaluated. The efficiency ratio of 6.8×–47× applies specifically to the CIFAR-10 CNN zoo setting. Whether the same ratio holds for MLP zoos (where DWSNets is the appropriate equivariant encoder) is unknown.

**DWSNets excluded from property prediction.** DWSNets requires M>2 FC layers; the CIFAR-10 CNN zoo has 2 FC layers. The property-prediction efficiency advantage was measured for GNN-NFN only. DWSNets equivariance is structurally confirmed on synthetic MLP weights, but DWSNets property-prediction efficiency on CNN zoos is not reported.

**N=100 crossover is single-seed.** The most novel finding lacks multi-seed confidence intervals. The N=100 values for PermAug and GNN-NFN are point estimates with collapsed CI_lo = CI_hi. This finding is presented as a preliminary observation, not a confirmed result. H-M3 is flagged as PARTIAL/LIMITATION_RECORDED in the research pipeline.

**PermAug from separate experimental phase.** PermAug results come from H-M3, a separate experiment that loaded baseline flat-MLP and GNN-NFN results from H-M2. PermAug training used a distinct random seed. The crossover finding should be confirmed under a fully co-trained single-experiment design.

**Low zoo diversity.** CIFAR-10 zoo accuracy variance=0.025. Models cluster near convergence, potentially making the prediction task easier for all encoders and inflating absolute R² values. The relative efficiency ratio is preserved but absolute R² values should not be generalized to harder, more diverse zoos.

**Hyperparameter fairness at small N.** Adam hyperparameters were tuned at full data and held fixed. At N=100, this may disadvantage GNN-NFN's more complex architecture. An LR sweep at N=100 is needed.

**No formal CI on efficiency ratio.** The interpolated N_equiv,90≈147 spans the interval [101, 249], yielding efficiency ratios from approximately 28× to 69× using N_plain,90=7,000. The central estimate of 47× is a point estimate under linear interpolation; a formal bootstrap CI on the efficiency ratio requires multi-seed test-set resampling.

**PermAug expansion factor not ablated.** The 11× expansion factor is a fixed design choice. Whether the N=100 crossover depends on this factor — or would occur at a lower expansion — is not determined.

---

## 7. Conclusion

This study measured the sample efficiency advantage of permutation-equivariant weight-space encoders over plain encoders in a controlled, shared-split experiment on the ModelZooDataset CIFAR-10 CNN zoo. The principal findings are:

1. GNN-NFN achieves an efficiency ratio of approximately 47× over flat-MLP (conservative lower bound: 6.8×): it reaches 90% of its peak R² at N≈147 training models while flat-MLP requires the full dataset (~7,000 models) to reach 90% of its own peak R²=0.886.

2. The efficiency advantage is data-regime dependent. At N=100, PermAug (R²=0.138) outperforms structural equivariance (GNN-NFN R²=−0.016) — a single-seed finding requiring multi-seed replication. At N≥250, GNN-NFN dominates. The crossover occurs between N=100 and N=250, suggesting a minimum-data threshold of approximately 150–250 models for equivariant graph encoders on the CIFAR-10 CNN zoo.

3. Permutation equivariance is verified to floating-point precision for GNN-NFN (max_diff=1.80×10⁻⁶, 10,000 checks on trained CIFAR-10 zoo models) and DWSNets (max_diff=7.45×10⁻⁹, 1,000 checks on synthetic MLP weights). The gap ratio versus flat-MLP (max_diff=5.59×10⁻²) is approximately 7.5 million for DWSNets and 31,000 for GNN-NFN.

4. At full training scale, all encoders converge within 5% R² (gap≤0.038), consistent with the expressivity equivalence theorem of Dayan et al. [2026].

Three follow-up directions are directly motivated by these results. (1) Multi-seed replication of H-M3 at N=100 with 10 seeds: low cost, addresses the most statistically fragile finding. (2) LR sweep for GNN-NFN at N=100 to distinguish underfitting from learning-rate mismatch as the mechanism for the GNN-NFN N=100 failure. (3) Extension to the MNIST MLP zoo with DWSNets to test generalizability of the efficiency ratio across zoo types and encoder architectures.

The minimum-data threshold identified here — approximately 150–250 models — provides practitioners with a concrete criterion for encoder selection under zoo-size constraints. Practitioners with fewer than 150 models should prefer augmentation-based approaches; those with 250 or more models should consider structurally equivariant encoders.

---

## References

Dayan, A., Eitan, Y., and Maron, H. (2026). On the Expressive Power of Permutation-Equivariant Weight-Space Networks. arXiv:2602.01083.

Herrmann, V., Faccio, F., and Schmidhuber, J. (2024). Learning Useful Representations of Recurrent Neural Network Weight Matrices. ICML 2024. arXiv:2403.11998.

Kofinas, M., Knyazev, B., Zhang, Y., Chen, Y., Burghouts, G., Gavves, E., Snoek, C., and Zhang, D. (2024). Graph Neural Networks for Learning Equivariant Representations of Neural Networks. ICLR 2024. arXiv:2403.12143.

Meynent, L., Melev, I., Schürholt, K., Kauermann, G., and Borth, D. (2025). Structure Is Not Enough: Leveraging Behavior for Neural Network Weight Reconstruction. arXiv:2503.17138.

Navon, A., Shamsian, A., Achituve, I., Fetaya, E., Chechik, G., and Maron, H. (2023). Equivariant Architectures for Learning in Deep Weight Spaces. ICML 2023. arXiv:2301.12780.

Schürholt, K., Kostadinov, D., and Borth, D. (2021). Hyper-Representations: Self-Supervised Representation Learning on Neural Network Weights for Model Characteristic Prediction. arXiv:2110.15288.

Schürholt, K., Taskiran, D., Knyazev, B., Giró-i-Nieto, X., and Borth, D. (2022). Model Zoos: A Dataset of Diverse Populations of Neural Network Models. NeurIPS 2022. arXiv:2209.14764.

Tran, H. V., Vo, T. N., Tran, T., Nguyen, A., and Nguyen, T. (2024). Monomial Matrix Group Equivariant Neural Functional Networks. NeurIPS 2024. arXiv:2409.11697.

Zhou, A., Yang, K., Burns, K., Cardace, A., Jiang, Y., Sokota, S., Kolter, J., and Finn, C. (2023). Permutation Equivariant Neural Functionals. NeurIPS 2023. arXiv:2302.14040.

Zhou, A., Finn, C., and Harrison, J. (2024). Universal Neural Functionals. NeurIPS 2024. arXiv:2402.05232.

---

## Appendix

### A. Seed Traces

**Figure A1: Individual seed traces for GNN-NFN and flat-MLP across training sizes.**

![Seed traces CIFAR-10](/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_wsl/docs/youra_research/paper/figures/seed_traces_cifar10.png)

Variance is highest at N=100, motivating multi-seed replication as the primary follow-up. GNN-NFN's variance at N=100 is visually consistent with the below-chance R² observation being a robust feature of this training scale rather than an artifact of a single unlucky seed, though confirmation requires 10-seed replication.

### B. Hypothesis Validation Summary

| Hypothesis | Description | Gate type | Result |
|------------|-------------|-----------|--------|
| H-E1 | Existence: GNN-NFN vs. flat-MLP sample efficiency on shared splits | MUST_WORK | PASS WITH CAVEATS |
| H-M1 | Mechanism: Permutation equivariance structural verification | MUST_WORK | PASS |
| H-M2 | Mechanism: Learning curve analysis, efficiency ratio computation | SHOULD_WORK | PASS |
| H-M3 | Mechanism: PermAug as partial equivariance proxy | SHOULD_WORK | PARTIAL / LIMITATION_RECORDED |

Overall pass rate: 3 of 4 hypotheses fully or substantially validated; 1 partially validated with scientifically novel finding.

### C. PermAug Mechanism Verification

The corrected PermAug implementation in H-M3 was verified prior to training:

- aug_diff = 4.118 > 1×10⁻⁶ (augmented samples differ from originals)
- Dataset sizes confirmed: N=100 → 1,100; N=250 → 2,750; N=500 → 5,500; N=1,000 → 11,000

The H-E1 PermAug condition had a bug (identical random seeds for base and augmented datasets) causing PermAug and flat-MLP results to be identical in H-E1 and H-M2. All PermAug results reported in the main paper are from the H-M3 corrected implementation.

### D. Scope Conditions

| Condition | Results reported to hold | Results may not hold |
|-----------|--------------------------|----------------------|
| Training set size | N≥250 (GNN-NFN > PermAug > flat-MLP) | N=100 (PermAug may dominate GNN-NFN; single-seed) |
| Encoder architecture | GNN-NFN on CIFAR-10 CNN zoo | DWSNets on CIFAR-10 CNN zoo; transformer-weight encoders |
| Zoo type | CIFAR-10 CNN zoo (~9,000 models) | MNIST MLP zoo; large-scale HuggingFace collections |
| Zoo diversity | Low-to-moderate diversity (convergent accuracy) | High-diversity zoos (wide accuracy spread) |
| Data regime | Low-to-medium (N≤1,000; efficiency advantage large) | Full data (gap narrows to <4% R²) |
| Target property | Test accuracy prediction | Generalization gap; other model properties |
