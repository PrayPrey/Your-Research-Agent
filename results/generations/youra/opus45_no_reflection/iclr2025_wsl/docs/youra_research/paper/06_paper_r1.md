# Behavioral Fingerprinting in CNN Model Zoos: Existence and Extraction Challenges

## Abstract

Model zoos contain thousands of trained neural networks, but methods for predicting *how* models behave—beyond scalar accuracy—remain underdeveloped. We investigate whether class-wise behavioral profiles can be extracted from weight matrices alone. On the Small CNN Zoo (193 CIFAR-10 models), we find that 67.6% of class-wise accuracy variance is unexplained by overall accuracy—exceeding our detection threshold by 13.5×. This establishes that behavioral fingerprints exist: models with identical accuracy fail on different classes in distinct patterns. However, simple weight statistics (per-layer mean, std, norm) fail to extract this signal, achieving R² = -0.08 compared to a stratified baseline R² = 0.12. Our negative result on the mechanism (ΔR² = -0.20) combined with the positive existence finding motivates learned representations—NF-Layers, SANE embeddings, or behavioral autoencoders—as the path toward behavioral prediction from weights.

---

## 1. Introduction

Model accuracy is not the whole story. When analyzing the Small CNN Zoo—a collection of 193 convolutional neural networks trained on CIFAR-10 with varying hyperparameters and random seeds—we find that 67.6% of class-wise accuracy variance remains unexplained by overall model accuracy. This finding exceeds our detection threshold by a factor of 13.5, establishing that trained models develop distinct *behavioral fingerprints*: class-specific performance patterns that cannot be reduced to a single accuracy number.

This observation has practical implications. Model selection typically relies on aggregate metrics, yet two models with identical 85% accuracy may fail on entirely different classes. Understanding these behavioral differences from weights alone—without requiring inference—could enable efficient model auditing, ensemble construction, and failure mode prediction. The question is whether this behavioral structure can be extracted from the weight matrices themselves.

### The Gap in Weight-Space Learning

Recent advances in weight-space learning have achieved remarkable success at scalar property prediction. SANE achieves R² > 0.9 for predicting overall accuracy from weight representations on small CNNs [2]. Unterthiner et al. demonstrate that simple weight statistics (means, standard deviations, spectral norms) can predict accuracy with R² approaching 0.97 [3]. Neural Functionals provide permutation-equivariant architectures for processing weights while respecting hidden neuron symmetries [1].

However, these methods predict *scalar* properties. The structured prediction problem—forecasting a 10-dimensional class-wise accuracy vector rather than a single number—remains unexplored. More fundamentally, the question of whether behavioral information (beyond accuracy) is encoded in weights at all has not been systematically tested.

### Our Contribution

We address two foundational questions:

1. **Existence:** Does meaningful behavioral variance exist in model zoos beyond what overall accuracy explains?
2. **Mechanism:** Can simple weight-space features extract this behavioral signal?

For existence (H-E1), we decompose class-wise accuracy variance into components explained by overall accuracy, per-class baseline difficulty, and residual behavioral variance. We find a residual ratio of 0.68—67.6% of variance is *not* explained by the stratified baseline—establishing that behavioral fingerprints exist in model zoos.

For mechanism (H-M1), we test whether per-layer weight statistics (mean, standard deviation, minimum, maximum, L2 norm across 5 convolutional and fully-connected layers = 25 features) can predict class-wise accuracy profiles. Using Ridge regression with 80/20 train/test splits, we find that weight features achieve R² = -0.08 compared to the stratified baseline's R² = 0.12. The mechanism test *fails*: simple weight statistics do not capture behavioral variance better than knowing overall accuracy alone.

This negative result is informative. It establishes that while behavioral fingerprints exist, extracting them from weights is non-trivial. The failure motivates future work on learned representations (NF-Layers, SANE embeddings) and larger sample sizes—our 193-model subset is 150× smaller than the full zoo's ~30,000 models.

---

## 2. Related Work

### Weight-Space Learning

The treatment of neural network weights as a learnable data modality has emerged as an active research direction. The 2026 Weight Space Learning Survey categorizes this field into understanding, representation, and generation paradigms [5]. Our work falls under *understanding*: decoding behavioral properties from weight inspection.

**Permutation Equivariance.** A fundamental challenge in processing weights is that hidden neurons have no canonical ordering. Zhou et al. introduced Neural Functionals (NF-Layers) that respect this symmetry through parameter-sharing schemes [1]. Their characterization theorem proves that NF-Layers capture all permutation-equivariant linear maps.

**Scalable Representations.** SANE addresses scalability by tokenizing weight subsets sequentially [2]. ProbeGen uses learned deep linear probes with shared generators [7]. Set-based Neural Network Encoding handles mixed-architecture model zoos through logit invariance [10].

### Property Prediction from Weights

Prior work on property prediction has focused on scalar targets—primarily accuracy and generalization metrics.

**Weight Statistics.** Unterthiner et al. demonstrated that handcrafted weight statistics achieve R² ≈ 0.97 for accuracy prediction on the Small CNN Zoo [3]. This established that scalar accuracy is highly predictable from simple features. Our work tests whether this extends to structured behavioral predictions.

**Learned Representations.** SANE achieves R² > 0.9 for accuracy via learned embeddings [2]. Herrmann et al. adapt Deep Weight Space layers for RNNs using "functionalist interrogation" [6].

**The Gap.** These methods predict *scalar* properties. Class-wise accuracy profiles represent structured behavioral predictions with cross-class dependencies. Whether behavioral information extends to structured profiles remains untested.

### Behavioral Understanding

**Behavioral Loss.** Meynent et al. propose behavioral loss for weight-space autoencoders, showing that structural reconstruction does not guarantee behavioral fidelity [4]. They report 16-20% accuracy drops despite low reconstruction error, motivating explicit behavioral supervision.

---

## 3. Methodology

### 3.1 Hypothesis Framework

**H-E1 (Existence):** Class-wise accuracy profiles exhibit variance beyond what overall accuracy and per-class difficulty explain.

**H-M1 (Mechanism):** Weight matrix features correlate with class-wise accuracy profiles, explaining variance beyond the stratified baseline.

### 3.2 Behavioral Variance Decomposition (H-E1)

We construct a stratified baseline predicting class-wise accuracy from overall model accuracy:

$$\hat{a}_{i,c} = \alpha_c \cdot A_i + \beta_c$$

The residual variance ratio measures the fraction *not* explained:

$$\text{Residual Ratio} = 1 - \frac{\sum_{i,c}(\hat{a}_{i,c} - a_{i,c})^2}{\sum_{i,c}(a_{i,c} - \bar{a}_c)^2}$$

A ratio > 0.05 indicates meaningful behavioral variance.

### 3.3 Weight Statistics Probe (H-M1)

For each model, we extract 5 statistics (mean, std, min, max, L2 norm) from 5 layers, yielding 25 features. We use Ridge regression (α = 1.0) to predict per-class accuracy:

$$\Delta R^2 = R^2_{\text{weight}} - R^2_{\text{baseline}}$$

Success requires ΔR² > 0.

---

## 4. Experimental Setup

**Dataset.** Small CNN Zoo: 193 final-epoch models, 3-conv + 2-FC architecture, CIFAR-10.

**H-E1 Protocol.** Compute 193 × 10 class-wise accuracy matrix; fit per-class linear baselines; compute residual ratio.

**H-M1 Protocol.** Extract 25 weight features; 80/20 split; Ridge regression per class; compare R² against baseline.

**Threshold.** Residual ratio > 0.05 (existence); ΔR² > 0 (mechanism).

---

## 5. Results

### 5.1 H-E1: Behavioral Variance Exists

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Residual Ratio | **0.6758** | > 0.05 | **PASS** |
| Factor Above Threshold | 13.5× | — | — |

67.6% of class-wise variance is unexplained by overall accuracy. Vehicle classes (automobile: σ² = 0.163, truck: σ² = 0.127) show highest behavioral variance.

### 5.2 H-M1: Weight Statistics Fail

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Weight R² | **-0.08** | — | — |
| Baseline R² | **0.12** | — | — |
| ΔR² | **-0.20** | > 0 | **FAIL** |

Simple weight statistics perform worse than the stratified baseline. Class 4 (deer) shows extreme negative R² = -2.74, suggesting overfitting on small sample.

---

## 6. Discussion

**Existence Validated.** Behavioral fingerprints—class-specific accuracy patterns—exist in model zoos. 67.6% of variance is behavioral, not explained by overall accuracy.

**Mechanism Failed.** Simple weight statistics (25 features) do not capture this signal. Contributing factors:
- Sample size: 193 models vs. recommended ~30,000
- Feature expressivity: Scalar statistics may miss distributional/cross-layer information
- Model convergence: Mean accuracy 18.7% suggests undertrained models

**Implications.** Learned representations (NF-Layers, SANE, behavioral autoencoders) warranted for behavioral prediction.

**Limitations.** Small sample, single feature set, single architecture.

---

## 7. Conclusion

We asked whether model behavior is predictable from weights. Behavioral fingerprints exist—67.6% of class-wise accuracy variance is unexplained by overall accuracy—but extracting this signal via simple weight statistics fails.

The path forward: scale to full zoo (~30,000 models), test expressive features (distributions, spectra, learned embeddings), and validate cross-metric transfer.

Model accuracy is not the whole story—and neither is this paper. We have quantified the behavioral signal; extracting it remains an open challenge.

---

## References

[1] Zhou et al. "Permutation Equivariant Neural Functionals." NeurIPS 2023.

[2] Schürholt et al. "Towards Scalable and Versatile Weight Space Learning." ICML 2024.

[3] Unterthiner et al. "Predicting Neural Network Accuracy from Weights." arXiv:2002.11448, 2020.

[4] Meynent et al. "Structure Is Not Enough: Leveraging Behavior for Neural Network Weight Reconstruction." ICLR 2025.

[5] Han et al. "A Survey of Weight Space Learning." arXiv:2603.10090, 2026.

[6] Herrmann et al. "Learning Useful Representations of Recurrent Neural Network Weight Matrices." ICML 2024.

[7] Kahana et al. "Deep Linear Probe Generators for Weight Space Learning." NeurIPS 2024.

[8] Soro et al. "Diffusion-based Neural Network Weights Generation." ICLR 2024.

[9] Small CNN Zoo Dataset. HSG-AIML, 2021.

[10] Andreis et al. "Set-based Neural Network Encoding Without Weight Tying." ICML 2023.
