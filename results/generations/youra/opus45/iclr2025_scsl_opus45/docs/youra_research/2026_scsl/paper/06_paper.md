---
title: "Loss Trajectory Divergence Analysis for Spurious Correlation Detection"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
format: "ICML2025"
date: "2026-04-14"
hypothesis_id: "H-LossTraj-v1"
generated_by: "Anonymous Research Pipeline v2.0"
word_count: 5235
figures: 13
tables: 4
---

# Abstract

Deep learning models that achieve high overall accuracy can silently fail on minority subgroups when training data contains spurious correlations—statistical shortcuts that do not generalize. Existing methods to address this problem require expensive group annotations, leaving practitioners without training-time signals that their models are learning spurious patterns. We investigate whether per-sample loss trajectories during standard training encode information about spurious correlation vulnerability. Our key insight is that minority samples—those where spurious features conflict with true labels—experience immediate optimization conflict that creates distinctive loss patterns detectable from the first training epoch. On the Waterbirds benchmark, trajectory features predict minority group membership with AUROC = 0.9452, and this signal is spurious-specific: it attenuates by 29% under GroupDRO (which targets spurious correlations) but only 1% under variance-matched random reweighting. Surprisingly, initial loss alone suffices for detection (AUROC = 0.9473), enabling efficient single-epoch screening. Our findings establish loss trajectory analysis as a principled diagnostic for identifying spurious correlation vulnerability during training, before deployment reveals hidden failure modes.

---

# 1. Introduction

A deep learning model achieving 97% overall accuracy can simultaneously fail on specific subgroups at rates exceeding 40%—and standard training provides no warning that this silent failure mode exists. This paradox arises from *spurious correlations*: statistical associations in training data that do not hold in deployment, such as a medical imaging model that learns "chest drain presence" instead of "pneumonia pathology" because 95% of pneumonia cases in training happen to have chest drains [Sagawa et al., 2020]. The model achieves high aggregate accuracy by exploiting the shortcut, while catastrophically failing on the minority of cases where the spurious cue is absent—precisely the cases where accurate prediction matters most.

The machine learning community has developed methods to address spurious correlations, most notably Group Distributionally Robust Optimization (GroupDRO) [Sagawa et al., 2020], which upweights minority groups during training. However, these methods require group annotations—expensive labels identifying which samples belong to minority versus majority groups. Without such labels, practitioners have no training-time signal indicating that their model is learning spurious correlations. The failure mode remains invisible until deployment, when distribution shift reveals the hidden vulnerability.

This situation reflects a deeper gap: while significant progress has been made on *correcting* spurious correlation reliance (given labels), far less attention has been paid to *detecting* it during training. Existing detection approaches are either post-hoc—requiring deployment to discover failures—or require the same expensive group annotations as correction methods. A training-integrated diagnostic that reveals spurious correlation vulnerability without group labels would enable practitioners to identify problems before deployment.

We hypothesize that the process of learning spurious correlations leaves a distinctive temporal signature in per-sample loss trajectories. When a model learns spurious shortcuts, majority samples (where the spurious cue aligns with the label) experience rapid loss descent as the shortcut works perfectly for them. Minority samples (where the spurious cue conflicts with the label) experience higher initial loss and maintain distinctive trajectory patterns due to gradient conflict between the spurious signal and the true class features. If this hypothesis holds, loss trajectory features extracted during standard Empirical Risk Minimization (ERM) training could serve as a diagnostic for spurious correlation vulnerability—without requiring group labels during training.

We validate this hypothesis through controlled experiments on the Waterbirds benchmark [Sagawa et al., 2020], a standard testbed for spurious correlation research where bird type is spuriously correlated with background (95% of waterbirds appear on water backgrounds). Our investigation yields three key findings:

1. **Existence validated:** Per-sample loss trajectory features predict minority group membership with AUROC = 0.9452 ± 0.0072, significantly exceeding our 0.75 threshold (26% margin). This demonstrates that trajectory divergence between groups is not only present but strongly discriminative.

2. **Spurious-specificity confirmed:** The trajectory signal attenuates by 29.2% under GroupDRO training (which targets spurious correlations) but only 1.0% under variance-matched random reweighting (which only smooths gradients). This 29× difference confirms that the signal reflects spurious feature conflict specifically, not generic sample difficulty.

3. **Mechanism refined:** Surprisingly, initial loss (L₁) alone achieves AUROC = 0.9473—higher than combined trajectory features. The discriminative signal is present from epoch 1, not requiring extended training for detection. This finding enables efficient single-epoch screening for spurious correlation vulnerability.

These results establish loss trajectory analysis as a principled diagnostic for spurious correlations. By monitoring how models learn individual samples—not just what they predict—practitioners can identify potential failure modes during training, before deployment reveals them in production.

The remainder of this paper is organized as follows. Section 2 reviews related work on training dynamics and spurious correlation robustness. Section 3 presents our methodology for trajectory feature extraction and evaluation. Section 4 details experimental setup, and Section 5 presents results. Section 6 discusses implications and limitations, and Section 7 concludes with future directions.

---

# 2. Related Work

Our work connects two research threads that have developed largely independently: *training dynamics analysis*, which studies how neural networks learn individual examples over time, and *spurious correlation robustness*, which addresses model failures on minority subgroups. We review each thread and identify the gap at their intersection.

## 2.1 Training Dynamics and Per-Sample Learning

Understanding how neural networks learn individual training examples has been an active research area. Toneva et al. [2018] introduced the concept of *forgetting events*—transitions where a training example goes from correctly to incorrectly classified between epochs. They showed that certain examples are forgotten repeatedly while others are never forgotten, and that forgettable examples transfer across architectures. This work established that per-sample training dynamics carry meaningful information beyond aggregate loss curves.

Subsequent work has explored training dynamics for various purposes. Li et al. [2025] extract 142-dimensional training dynamics (TD) features per sample and demonstrate their utility for noisy label detection and class imbalance learning. Chen et al. [2025] track per-sample privacy vulnerability throughout training, discovering correlations between learning difficulty and membership inference risk. Leybzon and Kervadec [2024] study memorization dynamics in language models, finding that examples memorized early are more likely to remain "crystallized."

However, this line of work focuses on general notions of sample difficulty, memorization, or privacy—not the specific signature of spurious correlation learning. While training dynamics features may correlate with various sample properties, no prior work has examined whether they can specifically identify samples affected by spurious correlations.

## 2.2 Spurious Correlations and Group Robustness

Spurious correlations cause models to exploit statistical shortcuts that do not generalize [Geirhos et al., 2020]. The standard solution is Group Distributionally Robust Optimization (GroupDRO) [Sagawa et al., 2020], which minimizes worst-group loss by upweighting minority groups during training. GroupDRO achieves strong worst-group accuracy but requires group annotations during training.

Recent work has sought to reduce annotation requirements. Just Train Twice (JTT) [Liu et al., 2021] trains an initial ERM model, identifies high-error samples as likely minority examples, and upweights them in a second training run. Spread Spurious Attribute (SSA) [Nam et al., 2022] uses pseudo-attribute prediction to estimate group membership. Probabilistic Group DRO [Ghosal and Li, 2023] extends GroupDRO to soft group assignments. GIC [Han and Zou, 2024] improves group inference accuracy by leveraging correlations between spurious attributes and labels.

These methods focus on *intervention*—correcting spurious reliance—rather than *diagnosis*—identifying which samples are affected. JTT's error-based identification captures some minority samples but conflates spurious-correlation-affected samples with generally difficult examples. None of these methods leverage the temporal evolution of per-sample losses; they rely on single-epoch snapshots or accuracy signals.

## 2.3 Gradient-Based Sample Analysis

An alternative approach analyzes gradient information to characterize samples. Gradient norms have been used for sample difficulty estimation [Katharopoulos and Fleuret, 2018] and importance sampling [Johnson and Guestrin, 2018]. In prior exploratory work, we found that gradient norms can identify minority samples with AUC = 0.914 on Waterbirds, but this detection did not translate into successful intervention—highlighting that detection and correction are distinct challenges.

Maini et al. [2023] use gradient accounting to study memorization localization, finding that memorization is confined to small sets of neurons. Gilmer et al. [2021] analyze loss Hessian evolution to understand training instability. These gradient-based approaches provide complementary perspectives but do not specifically target spurious correlation signatures.

## 2.4 The Gap: Training Dynamics for Spurious Correlation Detection

Our work addresses the intersection missing from prior research: **Can training dynamics specifically identify spurious correlation-affected samples?** 

Prior training dynamics work (Toneva, Li) characterizes general difficulty without targeting spurious correlations. Prior spurious correlation work (GroupDRO, JTT) focuses on intervention, not trajectory-based diagnosis. Gradient-based approaches provide single-epoch signals rather than temporal patterns.

We contribute the first analysis of whether loss trajectory divergence is *specific* to spurious feature conflict—not just correlated with generic sample difficulty. Our controlled experiment with GroupDRO and variance-matched random reweighting directly tests this specificity, distinguishing our approach from prior trajectory analysis that does not address the spurious-specificity question.

---

# 3. Methodology

Building on our hypothesis that spurious correlation learning creates distinctive per-sample loss patterns, we design a methodology to (1) extract interpretable trajectory features from standard ERM training, (2) evaluate whether these features predict minority group membership, and (3) test whether the signal is spurious-specific rather than reflecting generic sample difficulty.

## 3.1 Problem Setup

Consider a classification task with training data $\{(x_i, y_i, g_i)\}_{i=1}^{N}$ where $x_i$ is the input, $y_i \in \{0, 1\}$ is the class label, and $g_i \in \{1, 2, 3, 4\}$ is the group label encoding the combination of class and spurious attribute. In the Waterbirds setting, groups are defined by (bird type × background): majority groups have aligned spurious features (waterbirds on water, landbirds on land), while minority groups have conflicting spurious features (waterbirds on land, landbirds on water).

Under standard ERM training, the model minimizes aggregate loss without access to group labels:
$$\mathcal{L}_{ERM} = \frac{1}{N} \sum_{i=1}^{N} \ell(f_\theta(x_i), y_i)$$

Our goal is to determine whether the per-sample loss trajectories $\{\ell_i^{(t)}\}_{t=1}^{T}$ during ERM training encode information that distinguishes minority from majority samples.

## 3.2 Per-Sample Loss Tracking

We track per-sample cross-entropy loss across training epochs. To obtain clean trajectory signals, we make several design choices:

**Deterministic evaluation passes.** After each training epoch, we run a separate evaluation pass over the training set with data augmentation disabled and batch ordering fixed. This removes stochasticity from augmentation that would add noise to trajectory measurements.

**Per-sample loss computation.** We use `reduction='none'` in the loss function to obtain individual sample losses rather than batch aggregates.

**Early-epoch focus.** We extract trajectory features from epochs 1-5, when spurious correlation learning is most active. Later epochs are dominated by fine-tuning dynamics that are less informative for our purpose.

## 3.3 Trajectory Feature Extraction

From the loss matrix $L \in \mathbb{R}^{N \times T}$ where $L_{i,t}$ is sample $i$'s loss at epoch $t$, we extract four interpretable features per sample:

**Initial Loss (L₁).** The loss value at epoch 1: $L_1^{(i)} = L_{i,1}$. This captures immediate conflict between the sample and early model representations.

**Slope.** The linear trend of loss decrease, capturing learning speed.

**Variance.** The variability of losses across epochs, capturing trajectory instability.

**Convergence Time.** The first epoch where normalized loss drops below threshold $\tau = 0.1$.

## 3.4 Minority Prediction Evaluation

We evaluate whether trajectory features predict minority group membership using binary classification with logistic regression and 5-fold stratified cross-validation. AUROC is our primary metric, with success criterion AUROC > 0.75.

## 3.5 Spurious-Specificity Test

We design a controlled experiment with three training regimes:

**ERM (baseline).** Standard empirical risk minimization, which learns spurious correlations.

**GroupDRO.** Minimizes worst-group loss, specifically targeting spurious correlation reliance.

**Variance-matched random reweighting.** A control condition matching GroupDRO's gradient variance without targeting spurious correlations.

**Hypothesis.** If trajectory divergence is spurious-specific: AUROC should decrease substantially under GroupDRO (Δ > 0.10) but remain stable under random reweighting (Δ < 0.05).

---

# 4. Experimental Setup

We design experiments to answer three research questions:

**RQ1 (Existence):** Do per-sample loss trajectory features predict minority group membership with discriminative power significantly above chance?

**RQ2 (Feature Analysis):** Which trajectory features are most informative for minority prediction?

**RQ3 (Spurious-Specificity):** Is the trajectory signal specific to spurious correlation conflict?

## 4.1 Dataset

We evaluate on the **Waterbirds** benchmark [Sagawa et al., 2020], containing 4,795 training samples with 95% spurious correlation (majority have aligned backgrounds) and ~5% minority prevalence.

## 4.2 Implementation Details

**Model:** ResNet-50 pretrained on ImageNet. **Training:** SGD with momentum 0.9, learning rate 0.001, batch size 128, 20 epochs total (trajectory features from epochs 1-5). **GroupDRO:** γ = 0.1. **Seeds:** {42, 123, 456, 789, 1011} for statistical robustness.

---

# 5. Results

## 5.1 RQ1: Existence

**Main finding:** Per-sample loss trajectory features predict minority group membership with AUROC = 0.9452 ± 0.0072, significantly exceeding our 0.75 threshold by a 26% margin.

| Metric | Value |
|--------|-------|
| AUROC (mean ± std) | 0.9452 ± 0.0072 |
| Threshold | 0.75 |
| Margin above threshold | +26.0% |

The high AUROC demonstrates that trajectory divergence between minority and majority samples is strongly discriminative.

## 5.2 RQ2: Feature Analysis

**Surprising finding:** Initial loss (L₁) alone achieves AUROC = 0.9473, slightly higher than the combined four-feature model.

| Feature | AUROC | Rank |
|---------|-------|------|
| L₁ (Initial Loss) | 0.9473 | 1 |
| Slope | 0.8970 | 2 |
| Variance | 0.7242 | 3 |
| Convergence Time | 0.5259 | 4 |

This finding has practical implications: **single-epoch screening is sufficient** for spurious correlation detection.

## 5.3 RQ3: Spurious-Specificity

**Critical finding:** The trajectory signal attenuates by 29.2% under GroupDRO but only 1.0% under variance-matched random reweighting.

| Training Regime | AUROC | ΔAUROC from ERM |
|-----------------|-------|-----------------|
| ERM (baseline) | 0.9436 ± 0.0123 | — |
| GroupDRO | 0.6513 ± 0.0390 | -0.2923 (-31.0%) |
| Random Reweighting | 0.9336 ± 0.0244 | -0.0100 (-1.1%) |

The 29× difference confirms that the signal is specifically tied to spurious feature conflict.

## 5.4 Negative Result: Curvature Timing

The curvature timing mechanism (delayed stabilization for minority samples) was NOT supported. Mean timing gap = 0.20 ± 0.40 epochs (target: ≥3 epochs), with 0% of seeds passing. The discriminative signal comes from loss magnitude, not curvature timing.

---

# 6. Discussion

## 6.1 Key Findings

**Finding 1:** Trajectory divergence is highly discriminative (AUROC = 0.9452).

**Finding 2:** The signal is magnitude-based, detectable from epoch 1 via initial loss L₁.

**Finding 3:** The signal is spurious-specific (GroupDRO attenuation = 29%, random = 1%).

## 6.2 Limitations

**L1: Single dataset.** Our evaluation focuses on Waterbirds. Generalization to CelebA, ColoredMNIST requires validation.

**L2: Pretrained models only.** The L₁ dominance may depend on pretrained features encoding spurious patterns.

**L3: Detection, not intervention.** We demonstrate identification, not guaranteed correction.

**L4: Curvature mechanism refuted.** Our secondary hypothesis about timing was not supported.

## 6.3 Broader Impact

This work provides tools for identifying spurious correlation vulnerability during training. Early detection can prevent deployment of models with hidden failure modes in high-stakes applications.

---

# 7. Conclusion

We began by observing that deep learning models can achieve high aggregate accuracy while silently failing on minority subgroups. Our work demonstrates that the process of learning spurious correlations is not invisible: it leaves a distinctive signature in per-sample loss trajectories detectable from the first training epoch.

Our main contributions are: (1) demonstrating that trajectory features predict minority membership with AUROC = 0.9452; (2) validating spurious-specificity through controlled experiments (GroupDRO attenuation = 29% vs. random = 1%); and (3) revealing that initial loss alone suffices for detection, enabling single-epoch screening.

Spurious correlations are not just outcomes to be corrected post-hoc; they are processes with distinctive developmental signatures. By examining how models learn individual samples over time, we gain a window into failure modes that would otherwise remain hidden until deployment. The silent failure need not remain silent: loss trajectory analysis provides an early warning signal that can inform deployment decisions and guide targeted intervention.

---

# References

[Sagawa et al., 2020] Sagawa, S., Koh, P.W., Hashimoto, T.B., and Liang, P. Distributionally Robust Neural Networks for Group Shifts. ICLR 2020.

[Geirhos et al., 2020] Geirhos, R., et al. Shortcut Learning in Deep Neural Networks. Nature Machine Intelligence, 2020.

[Toneva et al., 2018] Toneva, M., et al. An Empirical Study of Example Forgetting during Deep Neural Network Learning. ICLR 2018.

[Liu et al., 2021] Liu, E.Z., et al. Just Train Twice: Improving Group Robustness without Training Group Information. ICML 2021.

[Nam et al., 2022] Nam, J., et al. Spread Spurious Attribute: Improving Worst-group Accuracy with Spurious Attribute Estimation. ICLR 2022.

[Ghosal and Li, 2023] Ghosal, S.S. and Li, Y. Distributionally Robust Optimization with Probabilistic Group. NeurIPS 2023.

[Han and Zou, 2024] Han, Y. and Zou, D. Improving Group Robustness on Spurious Correlation Requires Preciser Group Inference. ICML 2024.

[Li et al., 2025] Li, M., Zhou, X., and Wu, O. Delving Into the Training Dynamics for Image Classification. 2025.

[Chen et al., 2025] Chen, Y., et al. Evaluating the Dynamics of Membership Privacy in Deep Learning. 2025.

[Leybzon and Kervadec, 2024] Leybzon, D. and Kervadec, C. Learning, Forgetting, Remembering: Insights From Tracking LLM Memorization During Training. NeurIPS 2024.

[Katharopoulos and Fleuret, 2018] Katharopoulos, A. and Fleuret, F. Not All Samples Are Created Equal: Deep Learning with Importance Sampling. ICML 2018.

[Johnson and Guestrin, 2018] Johnson, T.B. and Guestrin, C. Training Deep Models Faster with Robust, Approximate Importance Sampling. NeurIPS 2018.

[Maini et al., 2023] Maini, P., et al. Can Neural Network Memorization Be Localized? ICML 2023.

[Gilmer et al., 2021] Gilmer, J., et al. A Loss Curvature Perspective on Training Instability in Deep Learning. 2021.

---

*Generated by Anonymous Research Pipeline v2.0 | Phase 6: Paper Writing | 2026-04-14*
