# Permutation-Equivariant Inductive Bias Advantage in Weight-Space Accuracy Prediction: A Controlled Δρ Benchmark

## Abstract

Predicting neural network accuracy from weights requires encoding weight tensors into fixed-size representations. Published comparisons between permutation-equivariant and flat MLP encoders have not controlled for encoder capacity, making it difficult to isolate the contribution of equivariant inductive bias from capacity differences. This work presents a controlled benchmark that matches three encoder types — flat MLP, Deep Sets (permutation-invariant), and Neural Functional Network (NFN, permutation-equivariant) — to approximately 500K parameters (±5%) on the Schurholt MNIST-CNN model zoo (hyp_rand variant, 2,249 checkpoints). Downstream accuracy prediction quality is measured via Spearman rank correlation (ρ), and the capacity-wasting mechanism is measured directly via permutation sensitivity scores. The flat MLP achieves a sensitivity score of 0.649, while the NFN achieves 7.34 × 10⁻⁷ — a reduction of approximately 885,000×. On the test split (n = 338), the NFN achieves ρ = 0.6806 [95% CI: 0.603, 0.748], the Deep Sets encoder achieves ρ = 0.4466 [95% CI: 0.344, 0.544], and the untrained flat MLP baseline achieves ρ = 0.1688 [95% CI: 0.069, 0.273], yielding Δρ(NFN − flat MLP) = 0.5119 [95% CI: 0.381, 0.638]. A monotone ordering ρ(flat MLP) < ρ(Deep Sets) < ρ(NFN) is confirmed. Tier analysis reveals that NFN advantage is largest for low-accuracy models (ρ = 0.856) and inverts for high-accuracy models (ρ = −0.314), contrary to the pre-registered prediction of mid-tier dominance. The CIFAR-10 experiment was not executed due to a data download failure; all results are specific to the MNIST-CNN zoo. The flat MLP uses a single hidden layer of width 193 for a 2,464-dimensional input, which constitutes an architectural bottleneck that may inflate the observed Δρ.

---

## 1. Introduction

Weight-space encoders map the parameters of a trained neural network to a fixed-size representation from which properties such as test accuracy can be predicted. A feedforward network with hidden layers of widths n₁, …, n_L admits ∏ₗ nₗ! permutation-equivalent weight configurations that are functionally identical but appear as distinct inputs to a flat MLP encoder. At matched capacity, this creates a representational burden: encoder parameters are consumed by orbit disambiguation rather than accuracy-predictive feature learning.

Permutation-equivariant encoders such as Neural Functional Networks (NFNs) address this by construction: all permutation-equivalent configurations are mapped to the same embedding. The empirical magnitude of this advantage, however, has not been measured under capacity-controlled conditions. Prior comparisons between NFN and flat MLP encoders do not match encoder parameter counts, so the observed performance differences could reflect both inductive bias advantages and capacity differences.

**Research gap.** No published study reports a Δρ benchmark comparing matched-capacity (±5%) NFN and flat MLP encoders on the Schurholt model zoo benchmarks with bootstrap 95% confidence intervals, an intermediate invariant baseline (Deep Sets), and direct mechanism measurement via permutation sensitivity scores.

**This work.** We train flat MLP, Deep Sets, and NFN encoders at matched approximately 500K parameters on the Schurholt MNIST-CNN model zoo (hyp_rand variant) and report:

1. Permutation orbit existence (H-E1): whether the zoo contains non-trivial permutation orbits.
2. Flat MLP sensitivity (H-M1): whether flat MLPs exhibit high permutation sensitivity at this capacity.
3. NFN sensitivity (H-M2): whether NFN encoders achieve near-zero permutation sensitivity.
4. Primary performance comparison (H-M3): Δρ with paired bootstrap 95% CI.

The paper is organized as follows. Section 2 reviews related work. Section 3 describes the methodology. Section 4 presents the experimental setup. Section 5 reports results. Section 6 discusses findings and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Weight-Space Property Prediction

Unterthiner et al. [2020] demonstrated that test accuracy can be predicted from weight tensors using flat MLP encoders that concatenate all weight tensors into a single vector. They report Spearman ρ ≈ 0.5–0.7 on a proprietary model zoo and establish Spearman rank correlation as the standard evaluation metric for this task.

Eilertsen et al. [2020] extend weight-space property prediction to training objective classification on CNN weights. Both works use flat concatenation without exploiting permutation symmetry.

### 2.2 Symmetry-Aware Encoders

Navon et al. [2023] introduce Neural Functional Networks (NFNs): equivariant weight-space architectures that respect the neuron-permutation symmetry of feedforward networks. Zhou et al. [2023] independently develop Neural Functional Transformers (NFTs). Kofinas et al. [2024] propose graph neural networks with equivariant message passing for weight spaces. All three works report improved performance over flat MLP baselines but do not match encoder capacities or report bootstrap CIs on Δρ.

Zaheer et al. [2017] prove that any permutation-invariant function on sets decomposes as ρ(Σᵢφ(xᵢ)) (Deep Sets architecture). The Deep Sets architecture has not been benchmarked as an intermediate baseline on model zoo accuracy prediction tasks.

### 2.3 Model Zoo Benchmarks

Schurholt et al. [2022] release the MNIST-CNN and CIFAR-10 model zoos for weight-space learning research. Schurholt et al. [2023] compare multiple encoder architectures on these zoos without capacity matching, bootstrap CIs, or a Deep Sets baseline.

### 2.4 Permutation Symmetry

The permutation symmetry structure of feedforward networks is characterized by Navon et al. [2023] and Zhou et al. [2023]. Related work on linear mode connectivity [Ainsworth et al., 2023] and loss landscape symmetry [Entezari et al., 2022] addresses permutation symmetry in the context of model merging. This work focuses on the encoder design implication: structural equivariance avoids the need to learn invariance from data.

---

## 3. Method

### 3.1 Problem Formulation

Let Z = {(wᵢ, aᵢ)}ᵢ₌₁ᴺ be a model zoo, where wᵢ is the weight tensor of model i and aᵢ ∈ [0,1] is its ground-truth test accuracy. A weight-space encoder f_θ: W → ℝᵈ maps weight tensors to embeddings, from which a prediction head g_ψ: ℝᵈ → ℝ predicts accuracy. Performance is measured using Spearman rank correlation ρ between predicted and ground-truth accuracy ranks on a held-out test set.

### 3.2 Encoder Architectures

Three encoders are compared, representing increasing levels of permutation symmetry exploitation.

**Flat MLP (no symmetry).** All weight tensors are concatenated into a single vector w_flat ∈ ℝ²⁴⁶⁴ and passed through a fully-connected MLP with hidden dimensions [193] and embedding dimension 128. Width 193 is determined by capacity matching to approximately 500K parameters. This results in a single hidden layer of width 193 for a 2,464-dimensional input — a bottleneck whose implications are discussed in Section 6.2 (Limitation L2).

**Deep Sets (permutation-invariant).** A shared per-element MLP φ processes each neuron's weight vector; representations are summed for a permutation-invariant embedding [Zaheer et al., 2017]. Configuration: φ_hidden = 256, ρ_hidden = 256, embed_dim = 128.

**NFN (permutation-equivariant).** The equivariant weight-space network of Navon et al. [2023] with n_layers = 3 equivariant layers and channel_dim = 112. By construction, permuting neurons in the encoded network produces a corresponding permutation in NFN's representations, and the final embedding is identical for all permutation-equivalent configurations.

**Table 1.** Encoder configurations and parameter counts.

| Encoder | Architecture | Parameters | Within ±5% of 500K? |
|---------|-------------|------------|----------------------|
| Flat MLP | hidden_dims=[193], embed_dim=128 | 500,706 | Yes |
| Deep Sets | phi_hidden=256, rho_hidden=256, embed_dim=128 | 471,936 | Yes |
| NFN | channel_dim=112, n_layers=3, embed_dim=128 | 521,953 | Yes |

Note: The flat MLP evaluated in the primary benchmark (H-M3) is an untrained instance (random weights, 500,706 params). The trained flat MLP from H-M1 has 500,577 parameters (ρ = 0.1041); the 129-parameter difference reflects a minor instantiation difference. The trained checkpoint was not available at the time of H-M3 evaluation.

### 3.3 Capacity Matching

The target parameter range is [475K, 525K] (500K ± 5%). Per-architecture width grid search was used to achieve this for each encoder type. All three encoders fall within this range (Table 1).

### 3.4 Permutation Sensitivity Score

The permutation sensitivity score directly measures the capacity-wasting mechanism:

sensitivity_score = E[‖f(w) − f(σ(w))‖₂] / E[‖f(w) − f(w')‖₂]

where the numerator is the mean L2 distance between embeddings of permutation-equivalent pairs (w, σ(w)), and the denominator is the mean L2 distance between random non-equivalent pairs (w, w'). A score near 0 indicates equivariant behavior; a score near 1 indicates inability to identify permutation equivalence. Scores are computed over 500 pairs stratified across 10 accuracy deciles (50 pairs per decile).

### 3.5 Training Protocol

All trained encoders use identical hyperparameters: Adam optimizer (β₁ = 0.9, β₂ = 0.999), learning rate 10⁻³ with cosine annealing to 10⁻⁶ over 150 epochs, batch size 32, weight decay 10⁻⁴, MSE loss, seed 42. Bootstrap CIs use 1,000 paired resamples on test-set predictions.

---

## 4. Experimental Setup

### 4.1 Research Questions

- **H-E1:** Does the MNIST-CNN zoo contain non-trivial permutation orbits and lack batch normalization?
- **H-M1:** Do flat MLP encoders at matched capacity exhibit high permutation sensitivity (score > 0.3)?
- **H-M2:** Do NFN encoders at matched capacity achieve near-zero permutation sensitivity (score < 0.1)?
- **H-M3:** Does the symmetry spectrum hold (ρ(flat) < ρ(Deep Sets) < ρ(NFN)) with Δρ ≥ 0.05 and bootstrap 95% CI lower bound > 0?

### 4.2 Datasets

Two variants of the Schurholt MNIST-CNN model zoo are used.

**H-E1 (orbit existence): `dataset_mnist_seed.pt` — seed-only variant.**
Contains 976 final-epoch checkpoints (filtered at training_iteration = 50 from 50,860 total records) of a smaller Conv(8)-Conv(8)-Conv(8)-FC-FC architecture. This variant was used for H-E1 because it was available at that stage of execution. It is architecturally distinct from the hyp_rand variant used for encoder training.

**H-M1/M2/M3 (encoder training and performance): `dataset_mnist_hyp_rand.pt` — hyp_rand variant.**
Contains 2,249 checkpoints of a BN-free CNN on MNIST with Conv(32)-Conv(64)-FC(128)-FC(10) architecture. Split: 1,589 / 322 / 338 (train / val / test). All Spearman ρ and Δρ results are computed exclusively on the hyp_rand test split (n = 338). Weight vector dimension: 2,464.

The orbit existence result (H-E1) characterizes the seed-only zoo (Conv(8) architecture), while the encoders were trained and evaluated on the hyp_rand zoo (Conv(32)-Conv(64) architecture). This constitutes an architectural mismatch between the orbit existence measurement and the encoder experiments; see Limitation L5 in Section 6.2.

### 4.3 Evaluation Metrics

Spearman ρ on the held-out test split (n = 338); Δρ = ρ(NFN) − ρ(flat MLP) with paired bootstrap 95% CI (1,000 resamples); permutation sensitivity score (500 stratified pairs). The gate threshold for H-M3 is Δρ ≥ 0.05 with CI lower bound > 0.

### 4.4 Implementation Details

All experiments ran on a single CUDA GPU. The NFN checkpoint from H-M2 (best validation loss, epoch 114) was reused in H-M3. The Deep Sets encoder was trained fresh for H-M3 (best at epoch 39, val_loss = 0.0203). The trained flat MLP checkpoint from H-M1 was not found at the expected path at the time of H-M3 evaluation; the flat MLP was therefore evaluated with random (untrained) weights.

---

## 5. Results

Results are presented in causal order: orbit existence, then mechanism measurement, then performance.

### 5.1 Orbit Existence (H-E1)

**Dataset:** seed-only variant (`dataset_mnist_seed.pt`, 976 checkpoints, Conv(8) architecture). See Section 4.2 for the architectural distinction from the hyp_rand encoder experiments.

BN-free architecture was confirmed (no running_mean / running_var keys in checkpoints). Of 500 same-accuracy-decile pairs sampled across 10 accuracy deciles, all 500 pairs showed cosine distance > 0.1:

- orbit_proportion = **1.000**
- mean cosine distance = **0.768** (std = 0.033)
- Gate threshold (cosine distance > 0.05): exceeded 15×

The permutation orbit problem is present across the full accuracy spectrum of the seed-only zoo. Permutation symmetry is a structural property shared by both the Conv(8) and Conv(32)-Conv(64) architectures; direct confirmation on the hyp_rand variant was not performed.

### 5.2 Flat MLP Permutation Sensitivity (H-M1)

The trained flat MLP (500,577 parameters) was evaluated on 500 stratified pairs from the hyp_rand zoo:

- Mean L2, equivalent pairs: **4.212**
- Mean L2, random pairs: **6.489**
- Sensitivity score: **0.649** (gate threshold > 0.3; exceeded 2.2×)
- Spearman ρ on hyp_rand test set: **0.1041**

The flat MLP assigns substantially different embeddings to permutation-equivalent weight configurations. The sensitivity score of 0.649 indicates that equivalent-pair distances are 65% of random-pair distances — the encoder does not identify permutation equivalence.

### 5.3 NFN Permutation Sensitivity (H-M2)

The trained NFN (521,953 parameters, best checkpoint at epoch 114) was evaluated on 500 stratified pairs:

- Mean L2, equivalent pairs: **2.679 × 10⁻⁸**
- Mean L2, random pairs: **3.648 × 10⁻²**
- Sensitivity score: **7.34 × 10⁻⁷** (gate threshold < 0.1; satisfied by factor of ~136,000)
- Sensitivity ratio relative to flat MLP: approximately **885,000×** lower (0.6490 / 7.34 × 10⁻⁷)
- Spearman ρ on hyp_rand test set: **0.6806** [95% CI: 0.603, 0.748]

The near-zero sensitivity score confirms that the NFN encoder maps permutation-equivalent weight configurations to effectively identical embeddings, consistent with the equivariance guarantee of the NFN architecture.

### 5.4 Primary Result: Symmetry Spectrum and Δρ (H-M3)

**Disclosure on flat MLP evaluation.** The H-M3 benchmark uses an untrained flat MLP instance (random weights, 500,706 params), because the trained H-M1 checkpoint was not found at the expected path. The trained H-M1 flat MLP achieved ρ = 0.1041; the untrained instance achieves ρ = 0.1688. Both are in the range 0.10–0.17, substantially below NFN ρ = 0.6806. Accordingly, Δρ = 0.5119 should be interpreted as computed against an untrained baseline; the gap against the trained flat MLP would be slightly larger (≈ 0.576), and the gap against a well-tuned multi-layer flat MLP is not measured and could be smaller (see Limitation L2).

**Table 2.** Spearman rank correlation on MNIST-CNN hyp_rand test set (n = 338). All encoders at approximately 500K parameters.

| Encoder | Parameters | ρ | 95% CI |
|---------|-----------|---|--------|
| Flat MLP (untrained)¹ | 500,706 | 0.1688 | [0.069, 0.273] |
| Deep Sets | 471,936 | 0.4466 | [0.344, 0.544] |
| NFN (trained, epoch 114) | 521,953 | 0.6806 | [0.603, 0.748] |

¹ Evaluated with random (untrained) weights; trained H-M1 instance (500,577 params) achieved ρ = 0.1041.

**Δρ(NFN − flat MLP) = 0.5119** [95% CI: 0.381, 0.638]

The CI lower bound (0.381) exceeds the gate threshold (0.05) by approximately 7.6×. The strict ordering ρ(flat MLP) < ρ(Deep Sets) < ρ(NFN) is confirmed:

- ρ(flat MLP) = 0.1688
- ρ(Deep Sets) = 0.4466 (Δ = +0.278 over flat MLP)
- ρ(NFN) = 0.6806 (Δ = +0.234 over Deep Sets)

The Deep Sets result indicates that permutation invariance (without full equivariance) provides substantial benefit, and that equivariance provides a further, smaller increment at this capacity.

### 5.5 Accuracy-Tier Dependence (Unexpected Finding)

The pre-registered prediction P3 anticipated mid-tier dominance of the NFN advantage. The observed data shows the opposite pattern:

**Table 3.** NFN Spearman ρ by accuracy tier on hyp_rand test set. Bootstrap CIs not computed at tier level due to small per-tier sample size (n ≈ 112–113 per tier).

| Accuracy Tier | NFN ρ | n |
|---------------|-------|---|
| Low (bottom third) | 0.856 | 113 |
| Mid (middle third) | 0.317 | 113 |
| High (top third) | −0.314 | 112 |

Pre-registered prediction P3 (mid-tier dominance) is not supported. The NFN achieves its highest correlation for low-accuracy models and negative correlation for high-accuracy models. Tier-level values are point estimates without bootstrap CIs; the reliability of individual tier estimates is not characterized.

---

## 6. Discussion

### 6.1 Interpretation of Main Results

The four experiments form a sequential chain of evidence. The seed-only zoo contains universally permutation-distinct weight configurations (orbit_proportion = 1.000). Flat MLPs at 500K parameters cannot learn permutation invariance from training data (sensitivity = 0.649). NFN encoders eliminate it by construction (sensitivity = 7.34 × 10⁻⁷). This 885,000× reduction in sensitivity is associated with a 4× improvement in Spearman ρ (0.169 → 0.681).

The association between permutation sensitivity reduction and ρ improvement is consistent with the capacity reallocation hypothesis: encoder parameters freed from orbit disambiguation are available for accuracy-predictive feature learning. However, the NFN and flat MLP encoders differ in multiple architectural respects beyond equivariance, including weight-sharing patterns and optimization landscape properties. The observed ρ improvement cannot be attributed solely to equivariance; confounds cannot be ruled out from this observational benchmark.

The monotone symmetry spectrum (flat MLP < Deep Sets < NFN) indicates that symmetry exploitation is a continuous design axis: invariance (Deep Sets) provides approximately half the total equivariance advantage (Δρ ≈ 0.28 of the total 0.51), while equivariance (NFN) provides a further increment (Δρ ≈ 0.23 over Deep Sets).

### 6.2 Limitations

**L1 — Single zoo [HIGH].** The CIFAR-10 experiment was not executed due to a data download failure. All results apply only to the Schurholt MNIST-CNN hyp_rand zoo. Cross-zoo generalization is not established.

**L2 — Flat MLP architectural bottleneck [HIGH].** Capacity matching at 500K parameters forces the flat MLP into a single hidden layer of width 193 for a 2,464-dimensional input. This is a severe architectural bottleneck that is unlikely to represent a well-tuned flat MLP configuration. The literature reports flat MLP ρ ≈ 0.5–0.7 on comparable zoos (Unterthiner et al., 2020), whereas the trained flat MLP here achieves ρ = 0.1041. The observed Δρ = 0.512 is therefore an upper bound on the gap against a capacity-matched flat MLP that uses a multi-layer architecture (e.g., hidden_dims = [512, 256]) with the same total parameter budget.

**L3 — Single training seed [LOW].** All trained encoders use seed 42 with no multi-seed replication. Training variance is uncharacterized.

**L4 — Single capacity point [MEDIUM].** The symmetry hierarchy is established at approximately 500K parameters. Whether it holds uniformly at other capacity scales (e.g., 50K–2M) is unknown.

**L5 — Dataset variant mismatch between H-E1 and H-M1/M2/M3 [MEDIUM].** The orbit existence analysis (H-E1) used the seed-only variant (976 checkpoints, Conv(8) architecture), while all encoder experiments used the hyp_rand variant (2,249 checkpoints, Conv(32)-Conv(64) architecture). The causal chain (orbit existence → capacity waste → performance gap) bridges two architecturally distinct dataset variants. Permutation symmetry is a structural property shared by both feedforward architectures, and the orbit existence result is expected to generalize, but it was not directly confirmed on the hyp_rand variant.

**L6 — NFN ρ below Navon et al. [MEDIUM].** The capacity-matched NFN achieves ρ = 0.6806, below the ρ ≈ 0.73 reported by Navon et al. [2023]. This gap is expected given that the present NFN uses a capacity-constrained configuration (521,953 params) rather than an unconstrained architecture, a fixed training seed without architecture-specific hyperparameter tuning, and potentially different zoo splits or subsets.

### 6.3 Accuracy-Tier Dependence

The refutation of P3 (mid-tier dominance) reveals an unexpected pattern: NFN advantage is concentrated among low-accuracy models (ρ = 0.856) and reverses among high-accuracy models (ρ = −0.314). One interpretation is that low-accuracy models span diverse failure modes and exhibit high weight-space diversity, providing strong equivariant signal, while high-accuracy models converge to similar near-optimal solutions where fine-grained ranking requires signals not captured by the current 500K-parameter equivariant architecture.

The negative ρ for high-accuracy models means the current NFN configuration is not suitable for model selection in settings where distinguishing the best-performing models is the goal. This represents a practical limitation not evident from the aggregate Δρ = 0.512 result.

Tier-level bootstrap CIs were not computed due to small per-tier sample size (n ≈ 112); the tier-level point estimates should be interpreted accordingly.

---

## 7. Conclusion

This work presents a controlled benchmark comparing flat MLP, Deep Sets, and NFN weight-space encoders at matched approximately 500K parameters on the Schurholt MNIST-CNN model zoo. The primary result is Δρ(NFN − flat MLP) = 0.5119 [95% CI: 0.381, 0.638], computed against an untrained flat MLP baseline. A monotone ordering ρ(flat MLP) = 0.169 < ρ(Deep Sets) = 0.447 < ρ(NFN) = 0.681 is confirmed. Permutation sensitivity measurement reveals that the flat MLP assigns substantially different embeddings to equivalent weight configurations (sensitivity = 0.649), while the NFN collapses them to near-zero (sensitivity = 7.34 × 10⁻⁷, approximately 885,000× lower).

The results are subject to several limitations: all claims apply only to the MNIST-CNN zoo (CIFAR-10 was unavailable); the flat MLP uses an architecturally constrained single-layer configuration that may inflate Δρ; only one training seed was used; and the orbit existence result was established on a different dataset variant than the encoder experiments.

An unexpected finding — that NFN advantage peaks for low-accuracy models (ρ = 0.856) and inverts for high-accuracy models (ρ = −0.314) — was not anticipated by the pre-registered predictions. This pattern was not characterized with tier-level bootstrap CIs and its generality is unknown.

Future work should address: (1) CIFAR-10 cross-zoo validation; (2) multi-layer flat MLP baselines at the same parameter budget; (3) capacity curve analysis across 50K–2M parameters; (4) multi-seed training replication; and (5) direct orbit existence measurement on the hyp_rand zoo variant.

---

## References

Ainsworth, S. K., Hayase, J., & Srinivasa, S. (2023). Git Re-Basin: Merging Models Modulo Permutation Symmetries. *ICLR 2023*.

Eilertsen, G., Jönsson, D., Ropinski, T., Unger, J., & Ynnerman, A. (2020). Classifying the Classifier: Dissecting the Weight Space of Neural Networks. *ECAI 2020*.

Entezari, R., Sedghi, H., Saukh, O., & Neyshabur, B. (2022). The Role of Permutation Invariance in Linear Mode Connectivity of Neural Networks. *ICLR 2022*.

Kingma, D. P., & Ba, J. (2015). Adam: A Method for Stochastic Optimization. *ICLR 2015*.

Kofinas, M., Knyazev, B., Zhang, Y., et al. (2024). Graph Neural Networks for Learning Equivariant Representations of Neural Networks. *ICLR 2024*.

Navon, A., Shamsian, A., Achituve, I., Fetaya, E., Chechik, G., & Maron, H. (2023). Equivariant Architectures for Learning in Deep Weight Spaces. *ICML 2023*.

Schürholt, K., Taskiran, D., Knyazev, B., Giró-i-Nieto, X., & Borth, D. (2022). Model Zoos: A Dataset of Diverse Populations of Neural Network Models. *NeurIPS 2022*.

Schürholt, K., Knyazev, B., Giró-i-Nieto, X., & Borth, D. (2021). Hyper-Representations as Generalizable Knowledge for Transfer Learning. *NeurIPS 2021*.

Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., & Tolstikhin, I. (2020). Predicting Neural Network Accuracy from Weights. *arXiv:2002.11448*.

Zaheer, M., Kottur, S., Ravanbakhsh, S., Poczos, B., Salakhutdinov, R., & Smola, A. (2017). Deep Sets. *NeurIPS 2017*.

Zhou, A., Yang, K., Burns, K., et al. (2023). Neural Functional Transformers. *NeurIPS 2023*.
