# Spectral Estimator Variance Does Not Indicate Model Quality: A Falsification Study

## Abstract

Spectral properties of neural network weights are increasingly used to predict model quality without expensive evaluation. This study tested the hypothesis that low variance in randomized SVD estimates indicates well-conditioned weight matrices and better generalization. The coefficient of variation of participation ratio (CV\_PR) was computed across 100 pretrained models from the timm library using 20 random seeds per layer, then correlated with ImageNet top-1 accuracy for 94 matched models. Contrary to the hypothesis predicting r < -0.3, the observed correlation was strongly positive (Pearson r = +0.6065, p = 9.24 × 10⁻¹¹). The 95% confidence interval [0.506, 0.703] excludes all negative values and zero. Spearman rank correlation confirmed the result (ρ = +0.6368, p = 5.26 × 10⁻¹²). These findings falsify the stability-as-quality assumption for this metric. Two alternative explanations are proposed: confounding by model size, and the possibility that higher spectral variance reflects richer feature representations rather than instability.

## 1. Introduction

This study set out to test whether stable spectral properties indicate model quality—and obtained the opposite result. The coefficient of variation of participation ratio (CV\_PR), a measure of randomized SVD estimator variance, was hypothesized to correlate negatively with ImageNet accuracy: models with flat spectra should produce consistent singular value estimates across random projections, and this stability should signal better generalization. Experiments on 100 pretrained models from the timm library revealed a strong positive correlation (r = +0.61, p < 10⁻¹⁰).

Spectral analysis of neural network weights has become a method for assessing model quality without requiring evaluation data. Martin and Mahoney (2019) established that heavy-tailed eigenvalue distributions reflect training quality. Unterthiner et al. (2020) demonstrated that simple weight statistics predict accuracy with R² > 0.98. However, the directional relationship between spectral variance and generalization had not been systematically tested. The timm library hosts over 1,000 architectures with pretrained weights, and practitioners selecting models rely on implicit assumptions about spectral properties.

Prior work computed spectral features directly (effective rank, participation ratio, power-law exponents) but did not examine the variance of these estimates under randomized computation. Randomized SVD introduces stochasticity: projecting a weight matrix onto random subspaces yields different singular value approximations across seeds. The reasoning was that this variance reflects spectral shape—flat spectra should produce stable estimates, peaked spectra should not. No prior study had tested whether this computational variance predicts model quality.

The main finding is that CV\_PR positively correlates with accuracy. The assumption that stability signals quality does not hold for this metric. Two competing explanations are considered: (1) model size confounds both accuracy and spectral diversity—larger models have more parameters, higher accuracy, and potentially more varied spectral structure; (2) higher CV\_PR may reflect diverse feature representations rather than instability. Distinguishing these requires partial correlation analysis controlling for parameter count.

This work makes three contributions:

1. **Methodology validation**: CV\_PR can be reliably extracted from 100 pretrained models using randomized SVD with 20 seeds (100% completion rate, CV\_PR values in [0.0014, 0.0326]).

2. **Hypothesis falsification**: CV\_PR correlates positively with ImageNet accuracy (r = +0.6065, 95% CI [0.506, 0.703]), contradicting the hypothesized negative correlation.

3. **Interpretive framework**: Alternative explanations (confounding, inverted mechanism) are identified to guide future hypothesis reformulation.

## 2. Related Work

### Spectral Analysis of Neural Networks

Martin and Mahoney (2019) showed that heavy-tailed eigenvalue distributions emerge during training and correlate with generalization. Their alpha exponent captures power-law decay, though alpha failed to discriminate model quality in prior attempts on this research program (p = 0.55). The WeightWatcher tool (Martin et al., 2021) operationalized this framework for computing spectral metrics across layers. These methods compute features directly but do not examine the variance of randomized estimators.

Li et al. (2018) estimated intrinsic dimensionality of objective landscapes using random subspace training. Their participation ratio (PR = (Σλ)² / Σλ²) captures effective rank. The present work adopts PR but focuses on its coefficient of variation across SVD seeds.

Randomized SVD algorithms (Halko et al., 2011) underpin the extraction methodology. By projecting onto random subspaces, these algorithms trade exactness for speed. The projection introduces variance that is typically treated as noise to minimize; this study treats it as a potential signal.

### Model Quality Prediction

Unterthiner et al. (2020) achieved R² > 0.98 for predicting model accuracy from weights using simple statistics aggregated across layers. Their approach is architecture-agnostic. The present work tests whether spectral variance adds interpretable signal beyond direct spectral features.

### Architecture-Aware Analysis

The timm library (Wightman, 2019) provides access to pretrained models with documented accuracy. Model soups (Wortsman et al., 2022) and Git Re-Basin (Ainsworth et al., 2023) explore weight-space relationships but focus on interpolation and alignment rather than spectral variance. Architecture-family effects (BatchNorm, GroupNorm, LayerNorm creating different spectral signatures) remain underexplored.

## 3. Method

### Overview

The core approach computes participation ratio 20 times per weight matrix (with different random seeds), measures the coefficient of variation, and aggregates across layers to obtain a per-model CV\_PR score. This score is then correlated with ImageNet accuracy.

### Randomized SVD

For a weight matrix W ∈ ℝ^{m×n}, randomized SVD (Halko et al., 2011) approximates truncated singular value decomposition by projecting onto a random subspace:

1. Draw random matrix Ω ∈ ℝ^{n×k} where k = rank + oversampling
2. Form Y = WΩ
3. Orthonormalize: Q = orth(Y)
4. Form B = Q^T W
5. Compute SVD of small matrix: B = UΣV^T
6. Recover approximate singular values from Σ

Implementation used torch.linalg.svd with QR-based random projection. Rank was fixed at 50; oversampling was 10. For 4D convolutional weights (c\_out × c\_in × h × w), matrices were reshaped to 2D by flattening spatial dimensions: (c\_out, c\_in × h × w).

### Participation Ratio

Given singular values σ = (σ\_1, ..., σ\_k), the participation ratio is:

PR = (Σσ\_i²)² / Σσ\_i⁴

This equals n for uniform singular values and approaches 1 when one singular value dominates. Squared singular values (eigenvalues of W^T W) were used.

### Coefficient of Variation

For each weight matrix, PR was computed across 20 random seeds (fixed sequence starting at seed 0):

CV\_PR = std(PR) / mean(PR)

### Model-Level Aggregation

Layer-wise CV\_PR values were aggregated via mean:

CV\_PR\_model = (1/L) Σ CV\_PR\_layer

All Conv2d and Linear layers with ≥100 elements were included. BatchNorm, LayerNorm, and bias vectors were excluded.

### Model Selection

Models were selected from the timm library satisfying:
- Pretrained on ImageNet-1K
- Has reported top-1 accuracy in timm metadata
- Architecture families include ResNet, ViT, EfficientNet, ConvNeXt, DenseNet, and others

Target was 100 models minimum, stratified across architecture families.

### Correlation Test

The primary test was Pearson correlation between CV\_PR\_model and ImageNet top-1 accuracy. Spearman correlation and 95% confidence intervals via bootstrap (10,000 iterations) were also computed.

Original success criterion: r < -0.3, p < 0.05

Falsification criterion: r ≥ 0 or p ≥ 0.05

## 4. Experimental Setup

### Dataset

Models were drawn from the timm library (PyTorch Image Models).

| Statistic | Value |
|-----------|-------|
| Models processed | 100 |
| Models with matched accuracy | 94 |
| Architecture families | 7+ |
| Accuracy range | 64.9% – 88.0% |

### Implementation Details

| Parameter | Value |
|-----------|-------|
| n\_seeds | 20 |
| SVD rank | 50 |
| Oversampling | 10 |
| Seed base | 0 |
| Framework | PyTorch 2.0+ |

Compute: Single GPU, approximately 2–30 seconds per model depending on architecture size.

### Evaluation Metrics

**RQ1 (Feasibility):**
- Completion rate (threshold: ≥95%)
- CV\_PR finite range: values in (0, 10)

**RQ2 (Correlation):**
- Pearson correlation coefficient
- Spearman rank correlation
- 95% confidence interval via bootstrap
- p-value

## 5. Results

### RQ1: Extraction Feasibility

CV\_PR extraction succeeded for all 100 models tested (100% completion rate).

| Metric | Value |
|--------|-------|
| Models processed | 100 |
| Completion rate | 100% |
| CV\_PR mean | 0.0116 |
| CV\_PR std | 0.0059 |
| CV\_PR min | 0.0014 |
| CV\_PR max | 0.0326 |

All CV\_PR values were finite and within expected range. The low absolute values (< 0.04) indicate that participation ratio estimates are consistent across random projections.

### RQ2: Correlation with Accuracy

The hypothesis predicted r < -0.3. The observed correlation was positive.

| Statistic | Value |
|-----------|-------|
| Pearson r | +0.6065 |
| Pearson p | 9.24 × 10⁻¹¹ |
| Spearman ρ | +0.6368 |
| Spearman p | 5.26 × 10⁻¹² |
| 95% CI | [0.506, 0.703] |
| n (matched) | 94 |

The hypothesis is falsified. CV\_PR shows a strong positive correlation with ImageNet accuracy. The 95% confidence interval excludes all negative values and zero.

![CV\_PR vs Accuracy](/home/PrayPrey/YOURA_no_VSA_opus45/TEST_wsl/docs/youra_research/paper/figures/scatter_cv_pr_vs_accuracy.png)

*Figure 1: CV\_PR positively correlates with ImageNet top-1 accuracy (r = +0.61). Each point represents one pretrained model from timm. n = 94 matched models.*

### Data Quality

| Variable | Mean | Std |
|----------|------|-----|
| CV\_PR | 0.0116 | 0.0057 |
| Top-1 Accuracy | 80.3% | 3.9% |

Match rate between CV\_PR extraction and accuracy metadata: 94/100 (94%). Six models lacked accuracy data in the timm results file.

### Outliers

Two models with notably low CV\_PR and accuracy were identified:
- dla46\_c.in1k: CV\_PR = 0.0035, top1 = 64.88%
- dla46x\_c.in1k: CV\_PR = 0.0045, top1 = 66.01%

These did not substantially affect the correlation.

### Summary

| Hypothesis | Gate | Criterion | Observed | Result |
|------------|------|-----------|----------|--------|
| H-E1 (Extraction) | MUST\_WORK | Completion ≥ 95%, CV\_PR finite | 100%, [0.0014, 0.0326] | PASS |
| H-E2 (Correlation) | MUST\_WORK | r < -0.3, p < 0.05 | r = +0.61, p < 10⁻¹⁰ | FAIL |

The extraction methodology is validated. The negative correlation hypothesis is falsified with a complete directional reversal.

## 6. Discussion

### Key Findings

**Finding 1: CV\_PR positively correlates with accuracy (r = +0.61).**

The original mechanism—flat spectra lead to stable SVD estimates, indicating smooth loss landscapes enabling generalization—is contradicted. Models with higher accuracy exhibit more variance in participation ratio across random projections.

**Finding 2: The extraction methodology is reliable.**

100% completion across 100 diverse models, with CV\_PR values consistently finite and in a narrow range [0.0014, 0.0326], validates that randomized SVD with 20 seeds produces meaningful variance estimates.

**Finding 3: The falsification redirects research.**

The decisive falsification (r = +0.61 vs predicted r < -0.3) indicates that future work should investigate why higher variance accompanies better models rather than pursuing stability-as-quality mechanisms.

### Alternative Explanations

**Confounding by model size.** Larger models tend to have higher accuracy and potentially more spectral diversity. Without partial correlation controlling for parameter count, it is not possible to determine whether CV\_PR has independent predictive value or proxies model size.

**Richer representations.** Higher CV\_PR may reflect diverse feature extraction at different scales. Better models may learn more varied spectral structures across layers, increasing projection-dependent variance.

### Limitations

**Limitation 1: Confounding not controlled.**

This was designed as an existence test. The purpose was to establish whether correlation exists and in which direction, not to fully characterize causal mechanisms. Partial correlation controlling for parameter count would be required to distinguish whether CV\_PR has independent predictive value.

**Limitation 2: Mechanism hypotheses blocked.**

The MUST\_WORK failure on H-E2 blocked dependent hypotheses (H-M1: partial correlation controlling condition number; H-M2: within-family correlation). The mechanism for why CV\_PR relates to accuracy remains unknown.

**Limitation 3: Limited architecture stratification.**

While multiple architecture families (ResNet, ViT, EfficientNet, ConvNeXt, etc.) were included, within-family versus cross-family correlation patterns were not analyzed. The relationship may differ by architecture type.

### Broader Impact

This work contributes to rigorous hypothesis testing in machine learning research. The falsification provides a concrete starting point for reformulated hypotheses. Misinterpretation of results should be avoided—the observed positive correlation may be spurious (driven by confounding) and should not be used for model selection without controlling for model size.

## 7. Conclusion

The coefficient of variation of participation ratio (CV\_PR), hypothesized to correlate negatively with ImageNet accuracy, instead shows a strong positive correlation (r = +0.6065, p = 9.24 × 10⁻¹¹). Models with higher accuracy exhibit more variance in randomized SVD estimates, not less. The 95% confidence interval [0.506, 0.703] excludes all negative values.

### Summary of Contributions

1. **Methodology validation:** CV\_PR can be reliably extracted from 100 pretrained models using randomized SVD with 20 seeds (100% completion, CV\_PR in [0.0014, 0.0326]).

2. **Hypothesis falsification:** The negative correlation hypothesis is rejected. CV\_PR positively correlates with accuracy.

3. **Interpretive framework:** Confounding by model size and richer representations are identified as competing explanations.

### Future Directions

**Confound analysis:** Partial correlation controlling for parameter count would distinguish whether CV\_PR has independent predictive value.

**Mechanism investigation:** The question of why higher spectral variance accompanies better generalization warrants investigation with reformulated hypotheses.

**Architecture stratification:** Within-family versus cross-family analysis may reveal whether the positive correlation varies by architecture type.

## References

- Ainsworth, S. K., Hayase, J., & Srinivasa, S. (2023). Git Re-Basin: Merging Models modulo Permutation Symmetries. In *International Conference on Learning Representations (ICLR)*.

- Eilertsen, G., Jönsson, D., Ropinski, T., Unger, J., & Ynnerman, A. (2020). Classifying the classifier: dissecting the weight space of neural networks. *arXiv preprint arXiv:2002.05688*.

- Frankle, J., Dziugaite, G. K., Roy, D. M., & Carbin, M. (2020). Linear Mode Connectivity and the Lottery Ticket Hypothesis. In *International Conference on Machine Learning (ICML)*.

- Halko, N., Martinsson, P.-G., & Tropp, J. A. (2011). Finding Structure with Randomness: Probabilistic Algorithms for Constructing Approximate Matrix Decompositions. *SIAM Review*, 53(2), 217–288.

- Li, C., Farkhoor, H., Liu, R., & Yosinski, J. (2018). Measuring the Intrinsic Dimension of Objective Landscapes. In *International Conference on Learning Representations (ICLR)*.

- Martin, C. H., & Mahoney, M. W. (2019). Traditional and Heavy-Tailed Self Regularization in Neural Network Models. *arXiv preprint arXiv:1901.08276*.

- Martin, C. H., Peng, T., & Mahoney, M. W. (2021). Predicting trends in the quality of state-of-the-art neural networks without access to training or testing data. *Nature Communications*, 12, 4122.

- Unterthiner, T., Keysers, D., Gelly, S., Bousquet, O., & Tolstikhin, I. (2020). Predicting Neural Network Accuracy from Weights. *arXiv preprint arXiv:2002.11448*.

- Wightman, R. (2019). PyTorch Image Models. https://github.com/huggingface/pytorch-image-models

- Wortsman, M., Ilharco, G., Gadre, S. Y., Roelofs, R., Gontijo-Lopes, R., Morcos, A. S., Namkoong, H., Farhadi, A., Carmon, Y., Kornblith, S., & Schmidt, L. (2022). Model soups: averaging weights of multiple fine-tuned models improves accuracy without increasing inference time. In *International Conference on Machine Learning (ICML)*.

- Wu, Y., & He, K. (2018). Group Normalization. In *European Conference on Computer Vision (ECCV)*.
