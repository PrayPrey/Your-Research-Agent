# Normalized Last-Layer Gradient Norms as Label-Free Minority Group Proxies: An Empirical Study on Spurious Correlation Benchmarks

## Abstract

Neural networks trained via empirical risk minimization (ERM) on data with spurious correlations achieve high average accuracy but perform poorly on minority groups that lack the spurious feature. Addressing this failure typically requires group annotations, which are expensive to obtain. This work investigates whether per-sample normalized last-layer gradient norms can serve as a label-free proxy for minority group membership during standard ERM training. Specifically, the normalized gradient norm g̃ᵢ = ‖∇_W ℓᵢ‖ / ‖h(xᵢ)‖ is computed via the outer-product decomposition of the fully connected layer gradient, which reduces to the prediction-error residual ‖pᵢ − yᵢ‖ when feature norms are approximately equalized by batch normalization. On the Waterbirds benchmark with a single random seed, g̃ achieves an AUC of 0.914 for binary minority group prediction at epoch 5 without any group annotations, with a minority-to-majority mean ratio of 8.8. Feature norm analysis confirms approximate equalization across groups (coefficient of variation ≈ 0.10), supporting the interpretation that the gradient norm gap reflects prediction-error differences rather than feature-scale artifacts. The overall hypothesis gate (requiring all three pre-specified criteria to pass) was not satisfied, as the class-balance deviation criterion failed due to a design mismatch with the dataset's inherent group imbalance. These results are based on a single seed and a single dataset; no downstream worst-group accuracy evaluation was performed. The findings suggest that gradient norms merit further investigation as minority proxies, pending multi-seed validation and end-to-end pipeline evaluation.

---

## 1. Introduction

Models trained by empirical risk minimization on data containing spurious correlations learn to exploit shortcut features that are predictive on average but fail for subpopulations where the shortcut does not hold. On the Waterbirds benchmark (Sagawa et al., 2019), where 95% of training images pair waterbirds with water backgrounds and landbirds with land backgrounds, an ERM-trained ResNet-50 achieves high average accuracy by relying on background features while performing poorly on minority groups — waterbirds on land (56 samples, 1.2% of training data) and landbirds on water (184 samples, 3.8%). This worst-group accuracy (WGA) failure is the central problem addressed by the spurious correlation robustness literature.

The standard remedy, Group Distributionally Robust Optimization (GroupDRO; Sagawa et al., 2019), minimizes worst-group loss and achieves high WGA, but requires per-sample group annotations for all training data. Obtaining such annotations (e.g., labeling whether each bird image has a matching or mismatching background) requires domain expertise and is costly at scale. This has motivated a line of work on label-free methods that attempt to identify minority samples without group annotations, typically by using training-dynamic signals such as misclassification (Liu et al., 2021) or relative loss (Nam et al., 2020) as indirect proxies.

This paper examines whether per-sample gradient norms computed from the last fully connected layer provide a useful minority identification signal. The motivation derives from the outer-product structure of the cross-entropy gradient for a linear classification head: for a fully connected layer W ∈ ℝ^{C×d}, the per-sample gradient satisfies ∇_W ℓᵢ = (pᵢ − yᵢ) ⊗ h(xᵢ), where pᵢ = softmax(Wh(xᵢ)) and h(xᵢ) is the penultimate-layer feature vector. The Frobenius norm factors as ‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ‖ · ‖h(xᵢ)‖. In architectures with batch normalization (Ioffe and Szegedy, 2015), feature norms ‖h(xᵢ)‖ are approximately equalized across samples, so normalizing by the feature norm yields g̃ᵢ ≈ ‖pᵢ − yᵢ‖, the prediction-error residual magnitude. During ERM training on spuriously correlated data, majority-group samples that exploit the shortcut feature converge to low prediction residuals, while minority-group samples that cannot use the shortcut maintain elevated residuals. This asymmetry is expected to manifest as a gap in normalized gradient norms between minority and majority groups.

The present study tests four pre-specified research questions on the Waterbirds benchmark using a single ResNet-50 model trained with ERM: (1) whether g̃ achieves AUC > 0.70 for minority group prediction at epoch 5; (2) whether the minority-to-majority g̃ ratio exceeds 3.0 at epoch 5; (3) whether the ratio persists above 1.2 at epoch 10; and (4) whether batch normalization equalizes feature norms across groups (coefficient of variation < 0.5). Of the three pre-specified gate criteria (ratio ≥ 3.0, AUC > 0.70, and class-balance deviation ≤ 0.10 in the top-25% subset), two passed and one failed. The balance deviation failure was attributed to a criterion design issue: on a dataset where minority groups constitute approximately 5% of training samples, any minority-enriched subset will deviate from class uniformity.

The contributions of this work are as follows. First, an empirical measurement showing that g̃ achieves AUC = 0.914 and a minority/majority ratio of 8.8 at epoch 5 on Waterbirds with a single seed, without group annotations. Second, verification that batch normalization produces approximate feature norm equalization (coefficient of variation ≈ 0.10), consistent with the interpretation that the gradient norm gap reflects prediction-error differences. Third, an efficient implementation of g̃ computation using a forward hook on the FC layer that requires no additional backward passes. Fourth, identification of a criterion design issue: class-balance deviation is an inappropriate metric for evaluating minority-focused subset selection on imbalanced datasets. These results are preliminary, based on a single seed and a single dataset, and no downstream WGA evaluation has been performed.

---

## 2. Related Work

### 2.1 Group-Robust Training with Annotations

Sagawa et al. (2019) introduced the Waterbirds and CelebA benchmarks alongside GroupDRO, which minimizes worst-group loss at each training step. GroupDRO achieves high WGA but requires group annotations for every training sample. Idrissi et al. (2021) demonstrated that simple data balancing across known groups is a competitive baseline, highlighting that the core difficulty lies in identifying which samples belong to underrepresented groups.

### 2.2 Label-Free Two-Stage Methods

Just Train Twice (JTT; Liu et al., 2021) trains an initial ERM model, identifies its misclassified training samples as a proxy for minority membership, and upweights these samples in a second training stage. The proxy signal is binary (correct vs. incorrect) and does not provide a continuous ranking. Learning from Failure (LfF; Nam et al., 2020) trains a biased and a debiased network simultaneously, using the generalized cross-entropy loss ratio to reweight samples. This requires two parallel training streams.

Deep Feature Reweighting (DFR; Kirichenko et al., 2022) demonstrated that ERM-trained feature representations already encode non-spurious information, and that retraining only the last classification layer on a group-balanced subset recovers high WGA. DFR requires group annotations for constructing the balanced subset. The gradient-norm proxy studied in this paper could, in principle, replace the group annotations in the DFR pipeline, though this end-to-end evaluation was not performed in the present work.

### 2.3 Data-Centric Training Signals

The normalized gradient norm g̃ᵢ = ‖pᵢ − yᵢ‖ is mathematically equivalent to the EL2N score introduced by Paul et al. (2021) for dataset pruning. Paul et al. used EL2N to identify easy (low-error) samples for coreset selection — the opposite selection direction from minority identification, which targets high-error samples. Forgetting events (Toneva et al., 2019) and influence functions (Koh and Liang, 2017) also characterize individual training samples via training dynamics, but neither has been applied to minority group identification in the spurious correlation setting. GEORGE (Zhang et al., 2022) discovers pseudo-groups via unsupervised clustering in representation space and then applies GroupDRO; this requires a full clustering step rather than a per-sample scalar signal.

### 2.4 Gradient Dynamics

Cohen et al. (2021) established that gradient descent on neural networks typically operates at the edge of stability, where the loss Hessian's top eigenvalue hovers near 2/η. This regime can amplify per-sample learning rate differences, which may contribute to gradient norm disparity between groups, though this connection is speculative in the present context.

---

## 3. Method

### 3.1 Normalized Per-Sample Last-Layer Gradient Norm

Consider a classification model with a fully connected last layer W ∈ ℝ^{C×d}. For sample i with feature vector h(xᵢ) ∈ ℝ^d and softmax output pᵢ = softmax(Wh(xᵢ)), the per-sample gradient of the cross-entropy loss with respect to W is:

∇_W ℓᵢ = (pᵢ − yᵢ) ⊗ h(xᵢ)

where yᵢ is the one-hot label vector. The Frobenius norm of this rank-1 outer product factors as:

‖∇_W ℓᵢ‖_F = ‖pᵢ − yᵢ‖₂ · ‖h(xᵢ)‖₂

The normalized gradient norm is defined as:

g̃ᵢ = ‖∇_W ℓᵢ‖_F / ‖h(xᵢ)‖₂ = ‖pᵢ − yᵢ‖₂

For architectures employing batch normalization (Ioffe and Szegedy, 2015), the feature norms ‖h(xᵢ)‖ are approximately equalized across samples. When this equalization holds, g̃ᵢ isolates the prediction-error residual magnitude as the informative component of the gradient norm.

The expected behavior during ERM training on spuriously correlated data is as follows: majority-group samples that can exploit the spurious feature converge to low prediction residuals (g̃ → 0), while minority-group samples that cannot exploit the shortcut maintain elevated residuals (g̃ remains large). This produces a persistent gap in g̃ between minority and majority groups.

### 3.2 Efficient Computation via Forward Hook

Rather than computing per-sample backward passes, the outer-product decomposition enables efficient computation of g̃ using only a forward pass:

```
Input: model f, dataloader D, epoch T
Output: {g̃ᵢ}_{i=1}^N

1. Register forward hook on model.fc to capture h(xᵢ)
2. Set model to eval mode
3. For each batch (x_b, y_b) in D:
   a. Compute logits = f(x_b)  [hook captures h(x_b)]
   b. Compute p_b = softmax(logits)
   c. Compute residual_b = p_b − onehot(y_b)
   d. Compute g̃_b = ‖residual_b‖₂ per sample
4. Return concatenation of all g̃ values
```

The computational cost is O(N) beyond standard inference, with O(N) storage. No additional backward passes are required.

### 3.3 Pseudo-Minority Subset Construction

Given g̃ values computed at a chosen epoch T_id, a minority-enriched subset is constructed by selecting the top-k% of samples ranked by g̃ (high prediction error, expected to be enriched for minority samples) and the bottom-k% (low prediction error, expected to be majority-enriched). In the experiments reported here, k = 25 and T_id = 5.

### 3.4 Proposed Two-Stage Pipeline (Not Evaluated)

The intended downstream application is a two-stage pipeline: Stage 1 performs standard ERM training and collects g̃ to construct a pseudo-balanced subset; Stage 2 freezes the ERM feature extractor and retrains the last layer on this subset, following the DFR principle (Kirichenko et al., 2022). This paper evaluates only the Stage 1 proxy signal quality. Stage 2, which would produce WGA measurements, was not implemented or evaluated and constitutes future work.

---

## 4. Experimental Setup

### 4.1 Dataset

Experiments were conducted on Waterbirds (Sagawa et al., 2019), constructed by compositing bird images from CUB-200 (Welinder et al., 2010) onto backgrounds from Places (Zhou et al., 2018) to create a 95% spurious correlation between bird type and background.

| Split | Total | G0 (Landbird/Land) | G1 (Landbird/Water) | G2 (Waterbird/Land) | G3 (Waterbird/Water) |
|-------|-------|---------------------|----------------------|----------------------|----------------------|
| Train | 4,795 | 3,498 (72.9%) | 184 (3.8%) | 56 (1.2%) | 1,057 (22.1%) |
| Val   | 1,199 | — | — | — | — |
| Test  | 5,794 | — | — | — | — |

Groups are defined as G = y × 2 + place. Minority groups are G1 ∪ G2, comprising approximately 5% of training data (240 of 4,795 samples). Preprocessing consisted of resizing to 256×256, center-cropping to 224×224, and ImageNet normalization (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]).

### 4.2 Model and Training

The model was ResNet-50 with ImageNet-pretrained weights (ResNet50_Weights.IMAGENET1K_V1), with the final fully connected layer replaced to produce two outputs (FC: 2048 → 2).

| Hyperparameter | Value |
|---------------|-------|
| Optimizer | SGD |
| Learning rate | 0.001 |
| Momentum | 0.9 |
| Weight decay | 1e-4 |
| Batch size | 128 |
| Epochs | 10 |
| Collection epochs | {1, 3, 5, 10} |
| Random seed | 42 |
| GPU | NVIDIA H100 NVL |

All 4,795 training samples were collected per epoch in eval mode for gradient norm computation. A single random seed was used throughout; no multi-seed replication was performed.

### 4.3 Evaluation Metrics

Four metrics were pre-specified:

- **AUC**: Area under the ROC curve for predicting binary minority membership (G1 ∪ G2 = 1, G0 ∪ G3 = 0) using g̃ as the score. Target: > 0.70.
- **Ratio**: Mean g̃ over minority samples divided by mean g̃ over majority samples. Target: ≥ 3.0 at T_id = 5.
- **h_norm_std_ratio**: Standard deviation of ‖h(xᵢ)‖ divided by mean ‖h(xᵢ)‖, measuring feature norm uniformity. Target: < 0.5.
- **Balance deviation**: Maximum within-class group deviation from uniformity in the top-25% subset selected by g̃. Target: ≤ 0.10.

The overall gate required all three primary criteria (ratio, AUC, balance deviation) to pass simultaneously.

### 4.4 Implementation

The gradient norm computation was implemented via a `GradientNormAnalyzer` class that registers a forward hook on `model.fc` to capture the penultimate-layer features h(xᵢ), then computes g̃ᵢ = ‖softmax(logits_i) − onehot(y_i)‖₂ using the outer-product decomposition. Features were stored on CPU to prevent GPU memory accumulation during full-dataset passes. The implementation comprised approximately 786 lines of Python across six source files, with 67 unit and integration tests passing.

---

## 5. Results

### 5.1 Proxy Signal Quality at T_id = 5

Table 1 presents the three pre-specified gate criteria evaluated at the primary epoch (T_id = 5).

**Table 1.** Gate criteria evaluation at T_id = 5.

| Metric | Value | Target | Result |
|--------|-------|--------|--------|
| Minority/majority g̃ ratio | 8.805 | ≥ 3.0 | Pass |
| AUC (minority prediction) | 0.914 | > 0.70 | Pass |
| Balance deviation (top-25%) | 0.379 | ≤ 0.10 | Fail |

The overall gate result was PARTIAL (2 of 3 criteria satisfied). The ratio of 8.805 indicates that minority samples had, on average, gradient norms approximately 8.8 times larger than majority samples. The AUC of 0.914 indicates that g̃ provides substantial discrimination between minority and majority groups when used as a ranking score. However, the balance deviation criterion was not met.

![Figure 1: Bar chart of three gate criteria at T_id=5 showing ratio, AUC, and balance deviation values against their respective targets](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/gate_metrics.png)

Table 2 reports per-group g̃ values at T_id = 5.

**Table 2.** Per-group normalized gradient norm values at T_id = 5.

| Group | Description | N | g̃ mean | g_raw mean | h_norm mean |
|-------|-------------|---|---------|------------|-------------|
| G0 | Landbird + Land (majority) | 3,498 | 0.022 | 0.553 | 25.25 |
| G1 | Landbird + Water (minority) | 184 | 0.313 | 8.100 | 25.68 |
| G2 | Waterbird + Land (minority) | 56 | 0.433 | 10.487 | 25.56 |
| G3 | Waterbird + Water (majority) | 1,057 | 0.094 | 2.350 | 26.41 |

G2, the smallest minority group (56 samples), exhibited the highest mean g̃ (0.433). Both minority groups showed g̃ values substantially above both majority groups, with G0 (the largest majority group) showing the lowest mean g̃ (0.022).

![Figure 2: Distribution of normalized gradient norms per group at epoch 5, showing separation between minority groups G1 and G2 and majority groups G0 and G3](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/distribution_epoch5.png)

### 5.2 Balance Deviation Failure Analysis

The balance deviation of 0.379 (against a target of ≤ 0.10) reflects a mismatch between the criterion and the dataset structure, rather than a failure of the gradient norm signal. Minority groups constitute approximately 5% of the training data (240 of 4,795 samples). Even if 100% of minority samples were captured in the top-25% subset (1,199 samples), minority proportion would be 240/1,199 ≈ 20%, far from the 50% that would yield low balance deviation. Class-balanced selection is mathematically incompatible with minority-focused selection when the minority prevalence is low.

The more relevant property for downstream DFR-style retraining is minority recall — the fraction of true minority samples captured in the selected subset — rather than class uniformity. The AUC of 0.914 provides indirect evidence of high minority recall, though direct recall was not computed in this experiment.

![Figure 4: Group composition of the top-25% high-g̃ subset compared to the full training set, showing overrepresentation of minority groups G1 and G2](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/balance_heatmap.png)

### 5.3 Temporal Trajectory

Table 3 reports proxy signal metrics across epochs 1, 3, 5, and 10.

**Table 3.** Per-epoch proxy signal metrics.

| Epoch | Ratio | AUC | Balance dev. | h_norm_std_ratio |
|-------|-------|-----|-------------|-----------------|
| 1 | 6.513 | 0.952 | 0.400 | 0.102 |
| 3 | 7.493 | 0.912 | 0.404 | 0.097 |
| 5 | 8.805 | 0.914 | 0.379 | 0.105 |
| 10 | 8.509 | 0.888 | 0.374 | 0.118 |

The ratio increased monotonically from epoch 1 to epoch 5 (6.5 → 8.8) and decreased slightly to 8.5 at epoch 10, remaining well above the 3.0 threshold at all measured epochs. AUC was highest at epoch 1 (0.952) and decreased gradually to 0.888 by epoch 10, remaining above 0.70 at all epochs. The signal was present from the first epoch and did not collapse through epoch 10.

![Figure 3: Temporal trajectory of minority/majority ratio and AUC across epochs 1–10, showing increasing ratio and stable AUC](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/trajectory.png)

The pattern of increasing ratio with training is consistent with majority-group samples converging toward zero prediction residuals as they are fit by the shortcut, while minority-group residuals decrease more slowly. Whether the ratio eventually declines at later epochs (beyond epoch 10) was not measured.

### 5.4 Feature Norm Equalization

Table 4 reports per-group feature norm statistics at T_id = 5.

**Table 4.** Feature norm statistics at T_id = 5.

| Group | h_norm mean |
|-------|-------------|
| G0 | 25.25 |
| G1 | 25.68 |
| G2 | 25.56 |
| G3 | 26.41 |

The overall h_norm_std_ratio was 0.105, indicating that the standard deviation of feature norms was approximately 10.5% of the mean. This approximate equalization was observed at all four collection epochs (coefficient of variation ranging from 0.097 to 0.118). The result is consistent with batch normalization approximately equalizing feature magnitudes across groups, supporting the interpretation that differences in g̃ reflect differences in prediction-error residuals rather than feature-scale variation.

![Figure 5: Feature norm distributions per group at T_id=5, showing approximately uniform distributions with coefficient of variation ≈ 0.10](/home/anonymous/YouRA_results_new_4/TEST_scsl/docs/youra_research/20260315_scsl/paper/figures/feature_norms.png)

### 5.5 Per-Group Temporal Detail

Table 5 provides a complete breakdown of per-group g̃ values across all measured epochs.

**Table 5.** Per-group mean g̃ at each evaluation epoch.

| Epoch | G0 (maj.) | G1 (min.) | G2 (min.) | G3 (maj.) |
|-------|-----------|-----------|-----------|-----------|
| 1 | 0.082 | 0.727 | 0.931 | 0.241 |
| 3 | 0.028 | 0.360 | 0.646 | 0.154 |
| 5 | 0.022 | 0.313 | 0.433 | 0.094 |
| 10 | 0.011 | 0.140 | 0.211 | 0.044 |

All groups showed decreasing g̃ over training, consistent with continued learning. The rate of decrease was faster for majority groups: G0 decreased from 0.082 to 0.011 (7.5× reduction), while G2 decreased from 0.931 to 0.211 (4.4× reduction), producing the increasing ratio observed in Table 3. G2 (waterbird on land, n=56) maintained the highest g̃ at all epochs, while G0 (landbird on land, n=3,498) had the lowest at all epochs.

---

## 6. Discussion

### 6.1 Interpretation of Results

The observed AUC of 0.914 and ratio of 8.8 at epoch 5 indicate that the normalized gradient norm g̃ provides a high-quality ranking signal for distinguishing minority from majority samples on Waterbirds. The signal is present from epoch 1 (AUC = 0.952, ratio = 6.5) and persists through epoch 10 (AUC = 0.888, ratio = 8.5), suggesting that the choice of collection epoch is not critical within this range. The per-group g̃ values follow a consistent ordering (G2 > G1 > G3 > G0) that aligns with group size — smaller groups exhibit larger mean gradient norms — consistent with the prediction that samples unable to benefit from the shortcut maintain higher prediction residuals.

The mathematical equivalence between g̃ and the EL2N score (Paul et al., 2021) is notable. The EL2N score was developed for identifying easy samples for dataset pruning; the present work examines the opposite tail of the same distribution for a different purpose (minority identification). This connection suggests that the observed signal is not specific to the gradient-norm framing but rather reflects a general property of prediction-error magnitudes during training on spuriously correlated data.

The failure of the balance deviation criterion does not indicate a failure of the gradient norm signal but rather an incompatibility between the criterion and the dataset structure. On datasets where minority groups constitute a small fraction of the total (≈5% for Waterbirds), any selection method that enriches for minority samples will necessarily produce class-imbalanced subsets. The appropriate metric for evaluating such subsets is minority recall (fraction of true minority samples captured), not class uniformity. This criterion was reformulated for subsequent experiments.

### 6.2 Limitations

Several limitations constrain the conclusions that can be drawn from these results.

First, all results are from a single random seed (seed = 42). The observed AUC and ratio values may vary across seeds, and no confidence intervals can be computed. Multi-seed replication is necessary before drawing general conclusions.

Second, only the Waterbirds dataset was evaluated. Whether the gradient norm signal provides a useful minority proxy on other spuriously correlated benchmarks (e.g., CelebA, MultiNLI) is unknown.

Third, no downstream worst-group accuracy evaluation was performed. The proxy signal quality (AUC, ratio) is a necessary but not sufficient condition for the end-to-end pipeline to improve WGA. It remains an open empirical question whether using g̃ to construct a pseudo-balanced subset for last-layer retraining would yield competitive WGA.

Fourth, minority recall in the top-25% subset was not directly computed, although the AUC of 0.914 provides indirect evidence that a substantial fraction of minority samples rank highly by g̃.

Fifth, the temporal analysis extends only to epoch 10. The behavior of the gradient norm signal at later training stages, and whether it eventually degrades, was not measured.

Sixth, the method assumes an architecture with batch normalization and an explicit fully connected last layer. The feature norm equalization that enables clean isolation of the prediction-error residual depends on batch normalization; architectures without this component may not exhibit the same property.

### 6.3 Future Directions

Three directions follow from this work. First, executing the full two-stage pipeline (ERM training with g̃-based subset construction, followed by last-layer retraining) to measure WGA, which is the primary metric of interest for spurious correlation robustness. Second, replicating the proxy signal measurements across multiple seeds and on additional datasets (CelebA, MultiNLI). Third, directly comparing g̃-based minority identification against JTT's misclassification-based proxy and other baselines in terms of minority recall and downstream WGA.

---

## 7. Conclusion

This paper measured the effectiveness of normalized last-layer gradient norms as a label-free proxy for minority group membership on the Waterbirds benchmark. Using a single ResNet-50 model trained with standard ERM, the per-sample normalized gradient norm g̃ᵢ = ‖pᵢ − yᵢ‖ achieved AUC = 0.914 for minority group prediction at epoch 5, with a minority-to-majority mean ratio of 8.8. The signal was present from epoch 1 and persisted through epoch 10. Feature norm analysis confirmed approximate equalization across groups (coefficient of variation ≈ 0.10), consistent with the interpretation that the gradient norm gap reflects prediction-error magnitude differences.

These results establish that, on this benchmark with a single seed, the gradient norm provides a high-AUC ranking signal for minority identification without group annotations. Whether this signal translates to improved worst-group accuracy in an end-to-end pipeline, and whether it generalizes across datasets and random seeds, remain open questions requiring further investigation.

---

## References

Cohen, J. M., Kaur, S., Li, Y., Kolter, J. Z., and Talwalkar, A. (2021). Gradient Descent on Neural Networks Typically Occurs at the Edge of Stability. ICLR 2021.

Idrissi, B. Y., Arjovsky, M., Pezeshki, M., and Lopez-Paz, D. (2021). Simple data balancing achieves competitive worst-group-accuracy. CLEaR 2022.

Ioffe, S. and Szegedy, C. (2015). Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift. ICML 2015.

Kirichenko, P., Izmailov, P., and Wilson, A. G. (2022). Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations. ICLR 2023.

Koh, P. W. and Liang, P. (2017). Understanding Black-box Predictions via Influence Functions. ICML 2017.

Liu, E., Haghgoo, B., Chen, A. S., Raghunathan, A., Koh, P. W., Sagawa, S., Liang, P., and Finn, C. (2021). Just Train Twice: Improving Group Robustness without Training Group Information. ICML 2021.

Nam, J., Cha, H., Ahn, S., Lee, J., and Shin, J. (2020). Learning from Failure: Training Debiased Classifier from Biased Classifier. NeurIPS 2020.

Paul, M., Ganguli, S., and Dziugaite, G. K. (2021). Deep Learning on a Data Diet: Finding Important Examples Early in Training. NeurIPS 2021.

Sagawa, S., Koh, P. W., Hashimoto, T. B., and Liang, P. (2019). Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization. arXiv:1911.08731.

Toneva, M., Sordoni, A., Combes, R. T. d., Trischler, A., Bengio, Y., and Gordon, G. J. (2019). An Empirical Study of Example Forgetting during Deep Neural Network Learning. ICLR 2019.

Welinder, P. et al. (2010). Caltech-UCSD Birds 200. Technical Report CNS-TR-2010-001, Caltech.

Zhang, M., Sohoni, N. S., Zhang, H. R., Finn, C., and Ré, C. (2022). GEORGE: No Annotations Needed: Group Discovery and Distributionally Robust Optimization. ICLR 2022.

Zhou, B., Lapedriza, A., Khosla, A., Oliva, A., and Torralba, A. (2018). Places: A 10 Million Image Database for Scene Recognition. IEEE TPAMI 2018.
