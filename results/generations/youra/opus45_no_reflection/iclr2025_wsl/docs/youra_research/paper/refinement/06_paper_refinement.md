# Behavioral Fingerprinting in CNN Model Zoos: Existence and Extraction Challenges

## Abstract

Model zoos contain thousands of trained neural networks, but methods for predicting class-wise behavioral profiles—beyond scalar accuracy—remain underdeveloped. This work investigates whether class-wise behavioral profiles can be extracted from weight matrices alone. On the Small CNN Zoo (193 CIFAR-10 models), 67.6% of class-wise accuracy variance is unexplained by overall accuracy, exceeding the detection threshold of 0.05 by a factor of 13.5. This establishes that behavioral fingerprints exist: models with identical accuracy fail on different classes in distinct patterns. However, simple weight statistics (per-layer mean, standard deviation, minimum, maximum, and L2 norm across 5 layers, yielding 25 features) fail to extract this signal. Ridge regression on weight features achieves mean R² = -0.08 compared to a stratified baseline mean R² = 0.12, yielding ΔR² = -0.20. The negative result on the mechanism, combined with the positive existence finding, motivates future work on learned representations such as Neural Functionals, SANE embeddings, or behavioral autoencoders for behavioral prediction from weights.

## 1. Introduction

Model accuracy does not capture the complete picture of model behavior. Analysis of the Small CNN Zoo—a collection of 193 convolutional neural networks trained on CIFAR-10 with varying hyperparameters and random seeds—reveals that 67.6% of class-wise accuracy variance remains unexplained by overall model accuracy. This finding exceeds the detection threshold of 0.05 by a factor of 13.5, establishing that trained models develop distinct behavioral fingerprints: class-specific performance patterns that cannot be reduced to a single accuracy number.

This observation has practical implications. Model selection typically relies on aggregate metrics, yet two models with identical 85% accuracy may fail on entirely different classes. Understanding these behavioral differences from weights alone—without requiring inference—could enable efficient model auditing, ensemble construction, and failure mode prediction. The central question is whether this behavioral structure can be extracted from weight matrices.

### The Gap in Weight-Space Learning

Recent advances in weight-space learning have achieved success at scalar property prediction. SANE achieves R² > 0.9 for predicting overall accuracy from weight representations on small CNNs. Unterthiner et al. demonstrate that simple weight statistics (means, standard deviations, spectral norms) can predict accuracy with R² approaching 0.97. Neural Functionals provide permutation-equivariant architectures for processing weights while respecting hidden neuron symmetries.

However, these methods predict scalar properties. The structured prediction problem—forecasting a 10-dimensional class-wise accuracy vector rather than a single number—remains unexplored. More fundamentally, the question of whether behavioral information (beyond accuracy) is encoded in weights at all has not been systematically tested.

### Contributions

This work addresses two foundational questions:

1. **Existence (H-E1):** Does meaningful behavioral variance exist in model zoos beyond what overall accuracy explains?
2. **Mechanism (H-M1):** Can simple weight-space features extract this behavioral signal?

For existence, decomposition of class-wise accuracy variance into components explained by overall accuracy, per-class baseline difficulty, and residual behavioral variance yields a residual ratio of 0.676—67.6% of variance is not explained by the stratified baseline—establishing that behavioral fingerprints exist in model zoos.

For mechanism, per-layer weight statistics (mean, standard deviation, minimum, maximum, L2 norm across 5 layers = 25 features) are tested for predicting class-wise accuracy profiles. Using Ridge regression (α = 1.0) with 80/20 train/test splits (154 training, 39 test models), weight features achieve mean R² = -0.08 compared to the stratified baseline mean R² = 0.12. The mechanism test fails: simple weight statistics do not capture behavioral variance better than knowing overall accuracy alone.

This negative result is informative. It establishes that while behavioral fingerprints exist, extracting them from weights using simple statistics is non-trivial.

## 2. Related Work

### Weight-Space Learning

The treatment of neural network weights as a learnable data modality has emerged as an active research direction. The 2026 Weight Space Learning Survey categorizes this field into understanding, representation, and generation paradigms. The present work falls under understanding: decoding behavioral properties from weight inspection.

**Permutation Equivariance.** A fundamental challenge in processing weights is that hidden neurons have no canonical ordering. Zhou et al. introduced Neural Functionals (NF-Layers) that respect this symmetry through parameter-sharing schemes. Their characterization theorem establishes that NF-Layers capture all permutation-equivariant linear maps.

**Scalable Representations.** SANE addresses scalability by tokenizing weight subsets sequentially. ProbeGen uses learned deep linear probes with shared generators. Set-based Neural Network Encoding handles mixed-architecture model zoos through logit invariance.

### Property Prediction from Weights

Prior work on property prediction has focused on scalar targets—primarily accuracy and generalization metrics.

**Weight Statistics.** Unterthiner et al. demonstrated that handcrafted weight statistics achieve R² ≈ 0.97 for accuracy prediction on the Small CNN Zoo with approximately 30,000 models. The present work tests whether this extends to structured behavioral predictions with a smaller sample of 193 models.

**Learned Representations.** SANE achieves R² > 0.9 for accuracy via learned embeddings. Herrmann et al. adapt Deep Weight Space layers for RNNs using functionalist interrogation approaches.

### Behavioral Understanding

**Behavioral Loss.** Meynent et al. propose behavioral loss for weight-space autoencoders, showing that structural reconstruction does not guarantee behavioral fidelity. They report 16-20% accuracy drops despite low reconstruction error, motivating explicit behavioral supervision.

## 3. Method

### 3.1 Hypothesis Framework

**H-E1 (Existence):** Class-wise accuracy profiles exhibit variance beyond what overall accuracy and per-class difficulty explain.

**H-M1 (Mechanism):** Weight matrix features correlate with class-wise accuracy profiles, explaining variance beyond the stratified baseline.

### 3.2 Behavioral Variance Decomposition (H-E1)

A stratified baseline predicts class-wise accuracy from overall model accuracy:

$$\hat{a}_{i,c} = A_i \cdot \frac{d_c}{\bar{d}}$$

where $A_i$ is overall accuracy of model $i$, $d_c$ is mean accuracy on class $c$ across all models, and $\bar{d}$ is mean of class difficulties.

The residual variance ratio measures the fraction not explained:

$$\text{Residual Ratio} = \frac{\text{Var}(a_{i,c} - \hat{a}_{i,c})}{\text{Var}(a_{i,c})}$$

A ratio > 0.05 indicates meaningful behavioral variance beyond what the stratified baseline captures.

### 3.3 Weight Statistics Probe (H-M1)

For each model, 5 statistics (mean, standard deviation, minimum, maximum, L2 norm) are extracted from 5 layers (3 convolutional, 2 fully-connected), yielding 25 features. The layer keys are:
- `module_list.0.weight` (conv1)
- `module_list.3.weight` (conv2)
- `module_list.6.weight` (conv3)
- `module_list.9.weight` (fc1)
- `module_list.11.weight` (fc2)

Ridge regression (α = 1.0) predicts per-class accuracy:

$$\Delta R^2 = R^2_{\text{weight}} - R^2_{\text{baseline}}$$

Success requires ΔR² > 0.

## 4. Experimental Setup

**Dataset.** Small CNN Zoo: 193 unique final-epoch models with a 3-conv + 2-FC architecture trained on CIFAR-10. The dataset originates from Zenodo (DOI: 10.5281/zenodo.6620868). Test evaluation uses the 10,000-sample CIFAR-10 test set.

**H-E1 Protocol.** A 193 × 10 class-wise accuracy matrix is computed by evaluating each model on the CIFAR-10 test set. Per-class linear baselines are fit using overall accuracy as the predictor. The residual ratio is computed as the ratio of residual variance to total variance.

**H-M1 Protocol.** 25 weight features are extracted per model. An 80/20 train/test split (154/39 models, seed=42) is applied. Ridge regression (α = 1.0) with standardized features predicts class-wise accuracy. Mean R² across 10 classes is compared against the stratified baseline.

**Thresholds.** Residual ratio > 0.05 for existence; ΔR² > 0 for mechanism.

## 5. Results

### 5.1 H-E1: Behavioral Variance Exists

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Total Variance | 0.0842 | — | — |
| Residual Variance | 0.0569 | — | — |
| Residual Ratio | **0.6758** | > 0.05 | **PASS** |
| R² of Stratified Baseline | 0.3242 | — | — |
| Factor Above Threshold | 13.5× | — | — |

67.6% of class-wise variance is unexplained by overall accuracy.

**Per-Class Analysis:**

| Class | Name | Mean Accuracy (Difficulty) | Variance |
|-------|------|---------------------------|----------|
| 0 | airplane | 0.196 | 0.080 |
| 1 | automobile | 0.465 | 0.163 |
| 2 | bird | 0.080 | 0.057 |
| 3 | cat | 0.029 | 0.007 |
| 4 | deer | 0.039 | 0.013 |
| 5 | dog | 0.182 | 0.059 |
| 6 | frog | 0.138 | 0.044 |
| 7 | horse | 0.212 | 0.057 |
| 8 | ship | 0.217 | 0.081 |
| 9 | truck | 0.309 | 0.127 |

Automobile (variance 0.163) and truck (variance 0.127) show the highest per-class variance, indicating models differentiate substantially on vehicle recognition capability.

**Model Statistics:**
- Mean overall accuracy: 18.7%
- Standard deviation of overall accuracy: 9.1%

The low mean accuracy (18.7%) indicates models in this subset are undertrained, which is expected for a zoo containing models across different training stages and hyperparameter configurations.

### 5.2 H-M1: Weight Statistics Fail

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Proposed (Weight Features) Mean R² | **-0.084** | — | — |
| Baseline (Stratified) Mean R² | **0.117** | — | — |
| ΔR² | **-0.201** | > 0 | **FAIL** |

Simple weight statistics perform worse than the stratified baseline.

**Per-Class R² Comparison:**

| Class | Baseline R² | Proposed R² | Winner |
|-------|-------------|-------------|--------|
| 0 | -0.014 | 0.202 | Proposed |
| 1 | 0.187 | 0.220 | Proposed |
| 2 | -0.111 | 0.112 | Proposed |
| 3 | -0.025 | -0.041 | Baseline |
| 4 | -0.090 | **-2.739** | Baseline |
| 5 | 0.276 | 0.252 | Baseline |
| 6 | 0.187 | 0.231 | Proposed |
| 7 | 0.286 | 0.158 | Baseline |
| 8 | 0.135 | 0.262 | Proposed |
| 9 | 0.336 | 0.501 | Proposed |

Class 4 (deer) shows extreme negative R² = -2.74 for the proposed model, indicating severe overfitting or feature-target misalignment for this class. The proposed method outperforms baseline on 6 of 10 classes individually, but the large failure on class 4 dominates the mean.

## 6. Discussion

**Existence Validated.** Behavioral fingerprints—class-specific accuracy patterns—exist in model zoos. 67.6% of variance is behavioral, not explained by overall accuracy. This confirms that models with the same aggregate accuracy exhibit different failure patterns across classes.

**Mechanism Failed.** Simple weight statistics (25 features) do not capture this signal. Contributing factors include:

1. **Sample size:** 193 models versus approximately 30,000 used by Unterthiner et al. for scalar accuracy prediction. With 25 features and only 39 test samples, overfitting on training data and poor generalization are expected.

2. **Feature expressivity:** Per-layer scalar statistics (mean, std, min, max, norm) may not capture the distributional or cross-layer structure encoding behavioral differences.

3. **Model convergence:** Mean accuracy of 18.7% indicates many models are undertrained. Weight statistics may be noisier for undertrained models.

4. **Class 4 anomaly:** The extreme negative R² on deer (-2.74) suggests the weight features capture noise rather than signal for this low-variance class (variance = 0.013).

**Implications.** The failure of simple statistics combined with confirmed existence of behavioral variance motivates learned representations. Neural Functionals (NF-Layers), SANE embeddings, and behavioral autoencoders with explicit behavioral supervision represent promising directions.

**Limitations.**
- Sample size is small (193 models versus ~30,000 in full zoo)
- Single feature set tested (per-layer scalar statistics)
- Single architecture family (3-conv + 2-FC CNNs on CIFAR-10)
- No cross-architecture or cross-dataset validation

## 7. Conclusion

This work addressed whether model behavior is predictable from weights. Behavioral fingerprints exist—67.6% of class-wise accuracy variance is unexplained by overall accuracy—but extracting this signal via simple weight statistics fails (ΔR² = -0.20).

The path forward includes:
1. Scaling to the full zoo (~30,000 models)
2. Testing expressive features (weight distributions, spectral properties, learned embeddings)
3. Applying gradient boosting or other nonlinear methods
4. Validating cross-metric transfer to other behavioral properties

Model accuracy does not capture the complete picture—and neither does this study. The behavioral signal has been quantified; extracting it remains an open challenge.

## References

[1] Zhou, A., Yang, K., Burns, K., Cardace, A., Jiang, Y., Sokota, S., Kolter, J. Z., and Finn, C. Permutation Equivariant Neural Functionals. NeurIPS, 2023.

[2] Schürholt, K., Mahoney, M., and Borth, D. Towards Scalable and Versatile Weight Space Learning. ICML, 2024.

[3] Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., and Tolstikhin, I. Predicting Neural Network Accuracy from Weights. arXiv:2002.11448, 2020.

[4] Meynent, S., Melev, M., Schürholt, K., Kauermann, G., and Borth, D. Structure Is Not Enough: Leveraging Behavior for Neural Network Weight Reconstruction. ICLR, 2025.

[5] Han, Z., Wang, L., Zhao, Y., Zhang, X., et al. A Survey of Weight Space Learning. arXiv:2603.10090, 2026.

[6] Herrmann, V., Faccio, F., and Schmidhuber, J. Learning Useful Representations of Recurrent Neural Network Weight Matrices. ICML, 2024.

[7] Kahana, J., Horwitz, E., Shuval, O., and Hoshen, Y. Deep Linear Probe Generators for Weight Space Learning. NeurIPS, 2024.

[8] Soro, B., Andreis, B., Lee, H., Chong, D., Hutter, F., and Hwang, S. J. Diffusion-based Neural Network Weights Generation. ICLR, 2024.

[9] Small CNN Zoo Dataset. HSG-AIML, Zenodo DOI: 10.5281/zenodo.6620868, 2021.

[10] Andreis, B., Soro, B., and Hwang, S. J. Set-based Neural Network Encoding Without Weight Tying. ICML, 2023.
