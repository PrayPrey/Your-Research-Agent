# Loss Trajectory Divergence Analysis for Spurious Correlation Detection

## Abstract

Deep learning models trained with empirical risk minimization can achieve high aggregate accuracy while failing on minority subgroups where spurious correlations do not hold. This work investigates whether per-sample loss trajectories during training encode information about spurious correlation vulnerability. Experiments on the Waterbirds benchmark show that trajectory features extracted from the first five epochs predict minority group membership with AUROC = 0.9452 ± 0.0072, exceeding the pre-specified threshold of 0.75. Initial loss (L₁) alone achieves AUROC = 0.9473, indicating that the discriminative signal is present from the first epoch. A controlled comparison of training regimes provides evidence for spurious-specificity: trajectory-based AUROC decreases by 0.29 under GroupDRO training but only by 0.01 under variance-matched random reweighting. A secondary hypothesis proposing delayed curvature stabilization in minority samples was not supported; curvature stabilized at epochs 2-3 for both groups. These results suggest that loss trajectory analysis may serve as a diagnostic tool for spurious correlation detection on this benchmark, though generalization to other datasets remains to be established.

## 1. Introduction

Deep learning models can achieve high overall accuracy while exhibiting poor performance on specific subgroups. This failure mode arises when training data contains spurious correlations—statistical associations between input features and labels that do not hold across all subpopulations. For example, in the Waterbirds benchmark, 95% of waterbird images appear on water backgrounds, leading models to associate "water background" with "waterbird" rather than learning features of the birds themselves. Models exploiting this shortcut achieve high aggregate accuracy but fail on the minority of waterbirds appearing on land backgrounds.

Group Distributionally Robust Optimization (GroupDRO) addresses this problem by minimizing worst-group loss during training, but requires group annotations identifying which samples belong to minority versus majority groups. Without such annotations, practitioners lack training-time signals indicating whether their models are learning spurious correlations. The failure mode remains invisible until deployment on data where the spurious correlation does not hold.

This work investigates whether per-sample loss trajectories during standard training encode information distinguishing minority from majority samples. The underlying hypothesis is that minority samples—where spurious features conflict with true labels—experience different optimization dynamics than majority samples. If loss trajectory features can predict minority group membership, they could serve as a diagnostic tool for spurious correlation vulnerability.

The experiments reported here address three questions:

1. **Existence:** Do per-sample loss trajectory features predict minority group membership with discriminative power above chance?
2. **Feature analysis:** Which trajectory features are most informative?
3. **Spurious-specificity:** Is the trajectory signal specific to spurious correlation, or does it reflect generic sample difficulty?

The main findings are as follows. First, trajectory features extracted from epochs 1-5 predict minority membership with AUROC = 0.9452 on Waterbirds, exceeding the pre-specified 0.75 threshold. Second, initial loss (L₁) alone achieves AUROC = 0.9473, suggesting the signal is present from the first training epoch. Third, the signal attenuates substantially under GroupDRO (ΔAUROC = 0.29) but minimally under variance-matched random reweighting (ΔAUROC = 0.01), providing evidence for spurious-specificity. Fourth, a secondary hypothesis about delayed curvature stabilization in minority samples was not supported by the data.

## 2. Related Work

### 2.1 Training Dynamics and Per-Sample Learning

Research on per-sample training dynamics has established that individual examples exhibit distinct learning patterns. Toneva et al. (2018) introduced the concept of forgetting events—transitions where correctly classified examples become misclassified between epochs—and showed that certain examples are forgotten repeatedly while others remain learned throughout training. Li et al. (2025) extract 142-dimensional training dynamics features per sample and demonstrate their utility for noisy label detection. Chen et al. (2025) track per-sample privacy vulnerability throughout training, finding correlations between learning difficulty and membership inference risk. Leybzon and Kervadec (2024) study memorization dynamics in language models, observing that examples memorized early are more likely to remain retained.

This line of work establishes that per-sample training dynamics carry information beyond aggregate metrics, but does not specifically address whether such dynamics can identify samples affected by spurious correlations.

### 2.2 Spurious Correlations and Group Robustness

Spurious correlations cause models to exploit statistical shortcuts that do not generalize (Geirhos et al., 2020). GroupDRO (Sagawa et al., 2020) addresses this by minimizing worst-group loss, but requires group annotations. Methods reducing annotation requirements include Just Train Twice (Liu et al., 2021), which identifies high-error samples after initial training; Spread Spurious Attribute (Nam et al., 2022), which uses pseudo-attribute prediction; and GIC (Han and Zou, 2024), which improves group inference accuracy.

These methods focus on intervention rather than diagnosis, and rely on single-epoch signals or accuracy metrics rather than temporal loss patterns. No prior work has examined whether loss trajectory divergence between groups can specifically identify spurious correlation-affected samples.

### 2.3 Gradient-Based Sample Analysis

Gradient norms have been used for sample difficulty estimation (Katharopoulos and Fleuret, 2018) and importance sampling (Johnson and Guestrin, 2018). Prior exploratory work found that gradient norms can identify minority samples with AUC = 0.914 on Waterbirds, though this detection did not translate into successful intervention. Maini et al. (2023) use gradient accounting to study memorization localization. These approaches provide complementary perspectives but do not specifically target spurious correlation signatures through temporal analysis.

## 3. Method

### 3.1 Problem Setup

Consider a classification task with training data {(xᵢ, yᵢ, gᵢ)}ᵢ₌₁ᴺ where xᵢ is the input, yᵢ ∈ {0, 1} is the class label, and gᵢ ∈ {1, 2, 3, 4} encodes the combination of class and spurious attribute. In Waterbirds, groups are defined by (bird type × background): majority groups have aligned spurious features (waterbirds on water, landbirds on land), while minority groups have conflicting features (waterbirds on land, landbirds on water).

Under standard ERM training, the model minimizes aggregate loss without access to group labels:

L_ERM = (1/N) Σᵢ ℓ(f_θ(xᵢ), yᵢ)

The goal is to determine whether the per-sample loss trajectories {ℓᵢ⁽ᵗ⁾}ₜ₌₁ᵀ during ERM training encode information distinguishing minority from majority samples.

### 3.2 Per-Sample Loss Tracking

Per-sample cross-entropy loss is tracked across training epochs. To reduce stochastic noise, evaluation passes after each epoch are run with data augmentation disabled and batch ordering fixed. Individual sample losses are computed using reduction='none' in the loss function. Trajectory features are extracted from epochs 1-5.

### 3.3 Trajectory Feature Extraction

From the loss matrix L ∈ ℝᴺˣᵀ where Lᵢ,ₜ is sample i's loss at epoch t, four features are extracted per sample:

- **Initial Loss (L₁):** The loss value at epoch 1, capturing immediate conflict between the sample and early model representations.
- **Slope:** The linear trend of loss decrease across epochs, capturing learning speed.
- **Variance:** The variability of losses across epochs, capturing trajectory instability.
- **Convergence Time:** The first epoch where normalized loss drops below a threshold τ = 0.1.

### 3.4 Minority Prediction Evaluation

Trajectory features are evaluated for their ability to predict minority group membership using logistic regression with 5-fold stratified cross-validation. AUROC is the primary metric, with a pre-specified success criterion of AUROC > 0.75.

### 3.5 Spurious-Specificity Test

To test whether trajectory divergence reflects spurious correlation specifically rather than generic sample difficulty, a controlled experiment compares three training regimes:

- **ERM (baseline):** Standard empirical risk minimization.
- **GroupDRO:** Minimizes worst-group loss, specifically targeting spurious correlation reliance.
- **Variance-matched random reweighting:** A control condition matching GroupDRO's gradient variance without targeting spurious correlations.

If trajectory divergence is spurious-specific, AUROC should decrease substantially under GroupDRO (Δ > 0.10) but remain stable under random reweighting (Δ < 0.05).

### 3.6 Curvature Timing Analysis

A secondary hypothesis proposed that minority samples exhibit delayed curvature stabilization—the epoch at which the second derivative of the loss curve transitions from negative to near-zero. This was tested by computing curvature via central differences on smoothed loss curves (Gaussian σ = 1.0) and detecting the sign-flip epoch where curvature exceeds -0.002 for two consecutive epochs. The hypothesis predicted a timing gap of ≥3 epochs between minority and majority groups in ≥70% of seeds.

## 4. Experimental Setup

### 4.1 Dataset

Experiments were conducted on the Waterbirds benchmark (Sagawa et al., 2020). The training set contains 4,795 samples with 95% spurious correlation (majority samples have aligned backgrounds). Minority samples constitute approximately 5% of the training data (240 samples). The four groups are: landbird on land (3,498 samples, majority), landbird on water (184 samples, minority), waterbird on land (56 samples, minority), and waterbird on water (1,057 samples, majority).

### 4.2 Model and Training

The model is ResNet-50 pretrained on ImageNet. Training uses SGD with momentum 0.9, learning rate 0.001, batch size 128, and weight decay 0.0001. Models are trained for 20 epochs, with trajectory features extracted from epochs 1-5. For GroupDRO experiments, γ = 0.1 and weight decay = 1.0 following standard configurations.

### 4.3 Evaluation Protocol

For the existence test (H-E1), a single seed (42) was used with 5-fold stratified cross-validation for AUROC computation. For the curvature timing test (H-M1), five seeds (42, 123, 456, 789, 1011) were used to assess reproducibility. For the spurious-specificity test (H-M2), three seeds (42, 43, 44) were used across all three training regimes.

## 5. Results

### 5.1 Existence: Trajectory Features Predict Minority Membership

Per-sample loss trajectory features predict minority group membership with AUROC = 0.9452 ± 0.0072, exceeding the pre-specified threshold of 0.75 by a margin of 26%.

**Table 1: Minority Group Prediction Performance**

| Metric | Value |
|--------|-------|
| AUROC (mean ± std) | 0.9452 ± 0.0072 |
| Pre-specified threshold | 0.75 |
| Margin above threshold | +26.0% |

This result indicates that trajectory features extracted from epochs 1-5 contain substantial information about minority group membership on this benchmark.

### 5.2 Feature Analysis: Initial Loss Dominates

Analysis of individual features reveals that initial loss (L₁) alone achieves AUROC = 0.9473, slightly exceeding the combined four-feature model.

**Table 2: Per-Feature AUROC**

| Feature | AUROC |
|---------|-------|
| L₁ (Initial Loss) | 0.9473 |
| Slope | 0.8970 |
| Variance | 0.7242 |
| Convergence Time | 0.5259 |

The dominance of L₁ suggests that minority samples are distinguishable from the first training epoch. With pretrained ResNet-50, early layers already encode features that cause immediate conflict for minority samples where the spurious cue provides incorrect signal. This finding has practical implications: single-epoch screening may suffice for detection on this benchmark.

### 5.3 Spurious-Specificity: Differential Attenuation Under GroupDRO

The trajectory signal attenuates by 0.29 (31% relative) under GroupDRO but only by 0.01 (1% relative) under variance-matched random reweighting.

**Table 3: AUROC Across Training Regimes**

| Training Regime | AUROC (mean ± std) | ΔAUROC from ERM |
|-----------------|-------------------|-----------------|
| ERM (baseline) | 0.9436 ± 0.0123 | — |
| GroupDRO | 0.6513 ± 0.0390 | -0.2923 |
| Random Reweighting | 0.9336 ± 0.0244 | -0.0100 |

GroupDRO specifically targets spurious correlation reliance by upweighting minority groups. The substantial attenuation under GroupDRO (ΔAUROC = 0.29, exceeding the 0.10 threshold) combined with minimal attenuation under random reweighting (ΔAUROC = 0.01, below the 0.05 threshold) is consistent with the hypothesis that trajectory divergence reflects spurious feature conflict rather than generic sample difficulty. The 29-fold difference in attenuation between the two interventions provides evidence for spurious-specificity.

Variance matching was verified: GroupDRO gradient variance was 0.015 and random reweighting gradient variance was 0.014, confirming that the control condition matched gradient variance without targeting spurious correlations.

### 5.4 Negative Result: Curvature Timing Mechanism Not Supported

The hypothesis that minority samples exhibit delayed curvature stabilization was not supported by the data.

**Table 4: Curvature Timing Analysis**

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Mean timing gap | 0.20 ± 0.40 epochs | ≥ 3 epochs | Not met |
| Seeds with gap ≥ 3 | 0/5 (0%) | ≥ 70% | Not met |

**Per-seed results:**

| Seed | Minority Median | Majority Median | Gap |
|------|-----------------|-----------------|-----|
| 42 | 2.0 | 2.0 | 0.0 |
| 123 | 2.0 | 2.0 | 0.0 |
| 456 | 2.0 | 2.0 | 0.0 |
| 789 | 3.0 | 2.0 | 1.0 |
| 1011 | 2.0 | 2.0 | 0.0 |

Curvature stabilized at epochs 2-3 for both minority and majority samples across all seeds. The proposed timing gap of ≥3 epochs was not observed in any seed. This negative result indicates that the discriminative signal comes from loss magnitude (L₁) rather than from temporal curvature dynamics. With pretrained models, convergence occurs quickly for all samples, leaving insufficient dynamic range to detect timing differences.

### 5.5 Summary of Hypothesis Outcomes

| Hypothesis | Type | Threshold | Result | Outcome |
|------------|------|-----------|--------|---------|
| H-E1: Trajectory prediction | Existence | AUROC > 0.75 | 0.9452 | Supported |
| H-M1: Curvature timing | Mechanism | Gap ≥ 3 epochs, 70% seeds | Gap = 0.20 epochs, 0% | Not supported |
| H-M2: Spurious-specificity | Mechanism | Δ_GroupDRO > 0.10, Δ_Random < 0.05 | 0.29, 0.01 | Supported |

## 6. Discussion

### 6.1 Interpretation of Results

The experiments provide evidence that loss trajectory features can identify minority samples on the Waterbirds benchmark, and that this signal is associated with spurious correlation dynamics rather than generic sample difficulty. The finding that initial loss alone (L₁) achieves comparable performance to multi-feature trajectory analysis suggests that the discriminative information is present from the first epoch, rather than emerging through extended training dynamics.

The mechanism underlying this finding may be understood as follows: pretrained models encode visual features that are spuriously correlated with labels in the Waterbirds dataset (background features). When minority samples—where these features provide incorrect signal—enter training, they experience higher initial loss. GroupDRO reduces spurious reliance by upweighting minority groups, thereby reducing the initial loss gap; random reweighting only smooths gradients without affecting the underlying feature reliance.

The negative result on curvature timing refines understanding of the mechanism. The original hypothesis proposed that minority samples would show delayed curvature stabilization due to prolonged optimization conflict. The data do not support this: curvature stabilizes early (epoch 2-3) for all samples. The discriminative signal is magnitude-based (high L₁ for minority samples) rather than timing-based.

### 6.2 Limitations

Several limitations scope the claims that can be made from these experiments:

**Single dataset.** All experiments were conducted on Waterbirds. While this is a standard benchmark, generalization to other spurious correlation settings (CelebA, ColoredMNIST, real-world datasets) has not been established.

**Pretrained models only.** The finding that L₁ dominates may depend on pretrained features already encoding spurious patterns. Models trained from scratch may exhibit different dynamics.

**Detection, not intervention.** These experiments demonstrate that trajectory features can identify minority samples, not that this identification translates to successful debiasing. Prior work has shown that detection and intervention are distinct challenges.

**Limited seed variance for H-E1.** The existence test used a single seed with cross-validation. While H-M2 used three seeds and confirmed consistency, broader seed analysis would strengthen robustness claims.

**Observational design for specificity.** The specificity test uses GroupDRO as an intervention, but causal claims are limited. The comparison with variance-matched random reweighting provides stronger evidence than pure observation, but does not establish causation.

**Incomplete hypothesis coverage.** A planned experiment testing whether early trajectory divergence predicts final worst-group accuracy (H-M3) was not conducted, as it depended on the curvature timing mechanism that was not supported.

### 6.3 Relation to Prior Work

The results are consistent with prior findings that per-sample training dynamics carry meaningful information (Toneva et al., 2018; Li et al., 2025). The contribution here is demonstrating that such dynamics can specifically identify spurious correlation-affected samples, not just generally difficult samples. The controlled comparison with random reweighting provides evidence for this specificity that is absent from prior trajectory analysis work.

The finding that initial loss dominates is consistent with the observation that pretrained models already encode spurious features. This differs from the forgetting-based analysis of Toneva et al. (2018), where temporal patterns (repeated forgetting) were informative. For spurious correlation detection with pretrained models, the initial state appears more informative than subsequent dynamics.

## 7. Conclusion

This work investigated whether per-sample loss trajectories during training can identify samples affected by spurious correlations. On the Waterbirds benchmark, trajectory features predicted minority group membership with AUROC = 0.9452, and this signal showed differential attenuation under GroupDRO versus random reweighting, providing evidence for spurious-specificity. Initial loss alone achieved comparable performance (AUROC = 0.9473), suggesting detection is possible from the first training epoch. A secondary hypothesis about delayed curvature stabilization was not supported.

These results demonstrate that loss trajectory analysis can serve as a diagnostic for spurious correlation vulnerability on this benchmark. The approach requires only standard training with per-sample loss logging and could be integrated into existing training pipelines. Whether these findings generalize to other spurious correlation settings, other model architectures, or translate to successful intervention remain open questions for future work.

## References

Sagawa, S., Koh, P.W., Hashimoto, T.B., and Liang, P. (2020). Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization. ICLR.

Geirhos, R., Jacobsen, J.H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., and Wichmann, F.A. (2020). Shortcut Learning in Deep Neural Networks. Nature Machine Intelligence, 2(11), 665-673.

Toneva, M., Sordoni, A., Tachet des Combes, R., Trischler, A., Bengio, Y., and Gordon, G.J. (2018). An Empirical Study of Example Forgetting during Deep Neural Network Learning. ICLR.

Liu, E.Z., Haghgoo, B., Chen, A.S., Raghunathan, A., Koh, P.W., Sagawa, S., Liang, P., and Finn, C. (2021). Just Train Twice: Improving Group Robustness without Training Group Information. ICML, 6781-6792.

Nam, J., Kim, J., Lee, J., and Shin, J. (2022). Spread Spurious Attribute: Improving Worst-group Accuracy with Spurious Attribute Estimation. ICLR.

Ghosal, S.S. and Li, Y. (2023). Distributionally Robust Optimization with Probabilistic Group. NeurIPS.

Han, Y. and Zou, D. (2024). Improving Group Robustness on Spurious Correlation Requires Preciser Group Inference. ICML.

Li, M., Zhou, X., and Wu, O. (2025). Delving Into the Training Dynamics for Image Classification.

Chen, Y., Wang, Z., Baracaldo, N., Kadhe, S., and Yu, L. (2025). Evaluating the Dynamics of Membership Privacy in Deep Learning.

Leybzon, D. and Kervadec, C. (2024). Learning, Forgetting, Remembering: Insights From Tracking LLM Memorization During Training. NeurIPS.

Katharopoulos, A. and Fleuret, F. (2018). Not All Samples Are Created Equal: Deep Learning with Importance Sampling. ICML, 2525-2534.

Johnson, T.B. and Guestrin, C. (2018). Training Deep Models Faster with Robust, Approximate Importance Sampling. NeurIPS.

Maini, P., Mozer, M.C., Sedghi, H., Lipton, Z.C., Kolter, J.Z., and Zhang, C. (2023). Can Neural Network Memorization Be Localized? ICML.

Gilmer, J., Ghorbani, B., Garg, A., Kudugunta, S., Neyshabur, B., Cardenas, D., Dahl, G.E., Nado, Z., and Firat, O. (2021). A Loss Curvature Perspective on Training Instability in Deep Learning.
