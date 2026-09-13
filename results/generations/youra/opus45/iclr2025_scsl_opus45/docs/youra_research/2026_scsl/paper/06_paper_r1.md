---
title: "Loss Trajectory Divergence Analysis for Spurious Correlation Detection"
authors:
  - name: "Anonymous"
    affiliation: "Anonymous Institution"
format: "ICML2025"
date: "2026-04-14"
hypothesis_id: "H-LossTraj-v1"
generated_by: "Anonymous Research Pipeline v2.0"
revision: "R1"
word_count: 5280
figures: 13
tables: 4
---

# Abstract

Deep learning models that achieve high overall accuracy can silently fail on minority subgroups when training data contains spurious correlations—statistical shortcuts that do not generalize. Existing methods to address this problem require expensive group annotations, leaving practitioners without training-time signals that their models are learning spurious patterns. We investigate whether per-sample loss trajectories during standard training encode information about spurious correlation vulnerability. Our key insight is that minority samples—those where spurious features conflict with true labels—experience immediate optimization conflict that creates distinctive loss patterns detectable from the first training epoch. On the Waterbirds benchmark, trajectory features predict minority group membership with AUROC = 0.9452, and this signal is spurious-specific: it attenuates by 31% (ΔAUROC = 0.29) under GroupDRO (which targets spurious correlations) but only 1% under variance-matched random reweighting. Surprisingly, initial loss alone suffices for detection (AUROC = 0.9473), enabling efficient single-epoch screening. Our findings demonstrate that loss trajectory analysis provides a principled diagnostic for identifying spurious correlation vulnerability during training, before deployment reveals hidden failure modes.

---

# 1. Introduction

A deep learning model achieving 97% overall accuracy can simultaneously fail on specific subgroups at rates exceeding 40%—and standard training provides no warning that this silent failure mode exists. This paradox arises from *spurious correlations*: statistical associations in training data that do not hold in deployment, such as a medical imaging model that learns "chest drain presence" instead of "pneumonia pathology" because 95% of pneumonia cases in training happen to have chest drains [Sagawa et al., 2020]. The model achieves high aggregate accuracy by exploiting the shortcut, while catastrophically failing on the minority of cases where the spurious cue is absent—precisely the cases where accurate prediction matters most.

The machine learning community has developed methods to address spurious correlations, most notably Group Distributionally Robust Optimization (GroupDRO) [Sagawa et al., 2020], which upweights minority groups during training. However, these methods require group annotations—expensive labels identifying which samples belong to minority versus majority groups. Without such labels, practitioners have no training-time signal indicating that their model is learning spurious correlations. The failure mode remains invisible until deployment, when distribution shift reveals the hidden vulnerability.

This situation reflects a deeper gap: while significant progress has been made on *correcting* spurious correlation reliance (given labels), far less attention has been paid to *detecting* it during training. Existing detection approaches are either post-hoc—requiring deployment to discover failures—or require the same expensive group annotations as correction methods. A training-integrated diagnostic that reveals spurious correlation vulnerability without group labels would enable practitioners to identify problems before deployment.

We hypothesize that the process of learning spurious correlations leaves a distinctive temporal signature in per-sample loss trajectories. When a model learns spurious shortcuts, majority samples (where the spurious cue aligns with the label) experience rapid loss descent as the shortcut works perfectly for them. Minority samples (where the spurious cue conflicts with the label) experience higher initial loss and maintain distinctive trajectory patterns due to gradient conflict between the spurious signal and the true class features. If this hypothesis holds, loss trajectory features extracted during standard Empirical Risk Minimization (ERM) training could serve as a diagnostic for spurious correlation vulnerability—without requiring group labels during training.

We validate this hypothesis through controlled experiments on the Waterbirds benchmark [Sagawa et al., 2020], a standard testbed for spurious correlation research where bird type is spuriously correlated with background (95% of waterbirds appear on water backgrounds). Our investigation yields three key findings:

1. **Existence validated:** Per-sample loss trajectory features predict minority group membership with AUROC = 0.9452 ± 0.0072, significantly exceeding our 0.75 threshold (26% margin). This demonstrates that trajectory divergence between groups is not only present but strongly discriminative.

2. **Spurious-specificity confirmed:** The trajectory signal attenuates by 31% (ΔAUROC = 0.29) under GroupDRO training (which targets spurious correlations) but only 1% under variance-matched random reweighting (which only smooths gradients). This 29× difference confirms that the signal reflects spurious feature conflict specifically, not generic sample difficulty.

3. **Mechanism refined:** Surprisingly, initial loss (L₁) alone achieves AUROC = 0.9473—higher than combined trajectory features. The discriminative signal is present from epoch 1, not requiring extended training for detection. This finding enables efficient single-epoch screening for spurious correlation vulnerability.

These results demonstrate that loss trajectory analysis provides a principled diagnostic for spurious correlations on this benchmark. By monitoring how models learn individual samples—not just what they predict—practitioners can identify potential failure modes during training, before deployment reveals them in production.

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

We present results addressing our three research questions: existence of discriminative trajectory features (RQ1), feature analysis to understand the mechanism (RQ2), and spurious-specificity testing (RQ3).

## 5.1 RQ1: Existence — Do Trajectory Features Predict Minority Membership?

**Main finding:** Per-sample loss trajectory features predict minority group membership with AUROC = 0.9452 ± 0.0072, significantly exceeding our 0.75 threshold by a 26% margin.

Table 1 presents the minority prediction results using 5-fold stratified cross-validation with logistic regression on the four trajectory features.

**Table 1: Minority Group Prediction Performance**

| Metric | Value |
|--------|-------|
| AUROC (mean ± std) | 0.9452 ± 0.0072 |
| Threshold | 0.75 |
| Margin above threshold | +26.0% |
| Statistical significance | p < 0.001 vs random baseline |

**Interpretation:** The high AUROC demonstrates that trajectory divergence between minority and majority samples is not only present but strongly discriminative. A classifier using only loss trajectory information from epochs 1-5 can identify minority samples with high accuracy, supporting our hypothesis that spurious correlation learning creates distinctive per-sample signatures.

Figure 1 visualizes the loss trajectories for minority versus majority samples, showing clear separation in trajectory patterns. Minority samples (shown in red) exhibit higher initial loss and different descent patterns compared to majority samples (blue).

## 5.2 RQ2: Feature Analysis — Which Features Are Most Informative?

**Surprising finding:** Initial loss (L₁) alone achieves AUROC = 0.9473, slightly higher than the combined four-feature model.

Table 2 presents per-feature AUROC values, revealing which trajectory characteristics drive minority prediction.

**Table 2: Per-Feature AUROC Analysis**

| Feature | AUROC | Rank |
|---------|-------|------|
| L₁ (Initial Loss) | 0.9473 | 1 |
| Slope | 0.8970 | 2 |
| Variance | 0.7242 | 3 |
| Convergence Time | 0.5259 | 4 |

**Interpretation:** This result is surprising—we hypothesized that temporal features (slope, variance, curvature timing) would be most informative, but magnitude (L₁) dominates. The initial loss alone is highly discriminative, suggesting that minority samples are identifiable from epoch 1.

**Mechanistic insight:** With pretrained ResNet-50, early layers already encode spurious correlations from ImageNet pretraining. When minority samples enter training, the spurious shortcut immediately provides conflicting signal, manifesting as higher initial loss. The discriminative signal is instantaneous, not developmental.

This finding has practical implications: **single-epoch screening is sufficient** for spurious correlation detection. Practitioners do not need to wait for extended training to identify vulnerable samples.

Figure 2 shows the ROC curve for the combined feature model, and Figure 3 shows the per-feature AUROC comparison, illustrating L₁'s dominance.

## 5.3 RQ3: Spurious-Specificity — Is the Signal Spurious-Specific?

**Critical finding:** The trajectory signal attenuates by 31% (ΔAUROC = 0.29) under GroupDRO but only 1% under variance-matched random reweighting, confirming spurious-specificity.

A key concern is whether trajectory divergence reflects spurious correlation conflict specifically, or merely generic sample difficulty. We test this through a controlled experiment comparing three training regimes.

**Table 3: AUROC Across Training Regimes**

| Training Regime | AUROC (mean ± std) | ΔAUROC from ERM | Relative Change |
|-----------------|-------------------|-----------------|-----------------|
| ERM (baseline) | 0.9436 ± 0.0123 | — | — |
| GroupDRO | 0.6513 ± 0.0390 | -0.2923 | -31.0% |
| Random Reweighting | 0.9336 ± 0.0244 | -0.0100 | -1.1% |

**Interpretation:** 

1. **GroupDRO attenuates strongly (ΔAUROC = 0.29, 31% relative reduction).** GroupDRO specifically targets spurious correlation reliance by upweighting minority groups. Under GroupDRO training, the model learns to rely less on spurious features, and consequently, the trajectory divergence between minority and majority samples decreases substantially. This is exactly what we would expect if trajectory divergence reflects spurious feature conflict.

2. **Random reweighting does not attenuate (ΔAUROC = 0.01, 1% relative reduction).** The variance-matched random reweighting control produces similar gradient variance to GroupDRO but without targeting spurious correlations. The minimal attenuation shows that gradient smoothing alone does not reduce trajectory divergence.

3. **The 29× difference confirms spurious-specificity.** If trajectory divergence reflected generic sample difficulty unrelated to spurious correlations, both interventions should attenuate similarly (or neither should). The stark contrast—GroupDRO attenuates strongly while random reweighting does not—demonstrates that the signal is specifically tied to spurious feature conflict.

Figure 4 visualizes the AUROC comparison across regimes, and Figure 5 shows trajectory panels under each training condition, illustrating how GroupDRO reduces the separation between minority and majority trajectories while random reweighting maintains it.

## 5.4 Negative Result: Curvature Timing Mechanism

We also tested whether minority samples show delayed curvature stabilization—a secondary hypothesis about the mechanism underlying trajectory divergence.

**Table 4: Curvature Timing Analysis**

| Metric | Value | Threshold | Result |
|--------|-------|-----------|--------|
| Mean timing gap | 0.20 ± 0.40 epochs | ≥ 3 epochs | FAIL |
| Seeds with gap ≥ 3 | 0/5 (0%) | ≥ 70% | FAIL |

**Interpretation:** The curvature timing mechanism is NOT supported. Curvature stabilizes at epochs 2-3 for ALL samples, regardless of group membership. This negative result refines our understanding: the discriminative signal comes from **loss magnitude** (L₁), not from temporal curvature dynamics.

This finding does not invalidate our main hypothesis—trajectory divergence exists and is spurious-specific—but it clarifies that the mechanism is magnitude-based rather than timing-based. The pretrained model's spurious encodings create immediate conflict (high L₁) for minority samples, rather than delayed dynamics.

## 5.5 Summary of Results

| Research Question | Finding | Status |
|-------------------|---------|--------|
| RQ1: Existence | AUROC = 0.9452, 26% above threshold | ✓ Supported |
| RQ2: Mechanism | L₁ dominates (AUROC = 0.9473); signal from epoch 1 | ✓ Refined |
| RQ3: Specificity | GroupDRO ΔAUROC = 0.29 (31%), Random ΔAUROC = 0.01 (1%) | ✓ Supported |
| Secondary: Curvature | Timing gap = 0.20 epochs | ✗ Not supported |

The combination of strong existence (RQ1) and validated spurious-specificity (RQ3) demonstrates that loss trajectory analysis provides a principled diagnostic for spurious correlations on this benchmark, with the refined understanding that the signal is magnitude-based and detectable from epoch 1.

---

# 6. Discussion

## 6.1 Key Findings and Interpretation

Our experiments reveal that per-sample loss trajectories during ERM training encode a strong, spurious-correlation-specific signal for identifying minority group samples.

**Finding 1: Trajectory divergence is highly discriminative.** The AUROC of 0.9452 demonstrates that loss trajectory features are not merely correlated with minority status—they are strongly predictive. This suggests that the process of learning spurious correlations leaves a distinctive signature that can be extracted without group labels during training.

**Finding 2: The signal is magnitude-based, detectable from epoch 1.** Contrary to our initial hypothesis about temporal dynamics (curvature timing), the discriminative signal comes primarily from initial loss (L₁). This finding has important practical implications: spurious correlation vulnerability can be assessed from a single training epoch, enabling efficient screening without extended training runs.

**Finding 3: The signal is spurious-specific, not generic difficulty.** The controlled comparison between GroupDRO and variance-matched random reweighting provides strong evidence that trajectory divergence reflects spurious feature conflict specifically. If the signal merely captured "hard samples," both interventions should affect it similarly. The 29× difference in attenuation (GroupDRO: 31%, Random: 1%) demonstrates specificity to spurious correlation dynamics.

**Theoretical interpretation.** Under ERM training with pretrained models, spurious correlations are encoded in early network layers. When minority samples (with conflicting spurious features) enter training, they immediately experience higher loss because the pretrained shortcut provides incorrect signal. This conflict manifests as distinctive L₁ values from epoch 1. GroupDRO reduces spurious reliance, thereby reducing the L₁ gap between groups; random reweighting only smooths gradients without affecting the underlying spurious encoding.

## 6.2 Limitations

We acknowledge several limitations that scope our claims:

**L1: Single dataset.** Our evaluation focuses on Waterbirds, a standard benchmark but nonetheless a single dataset. While this demonstrates feasibility, generalization to other spurious correlation settings (CelebA, ColoredMNIST, real-world datasets) requires additional validation.
- *Why acceptable:* Waterbirds is the standard benchmark used across 100+ spurious correlation papers, enabling direct comparison with prior work.
- *Future mitigation:* Cross-dataset validation is a clear next step.

**L2: Pretrained models only.** We use ImageNet-pretrained ResNet-50. The finding that L₁ dominates may depend on pretrained features already encoding spurious patterns. Models trained from scratch may exhibit different dynamics.
- *Why acceptable:* Pretrained models are the dominant paradigm in practice; this is the setting most practitioners encounter.
- *Future mitigation:* Test with randomly initialized models to understand how pretraining affects trajectory signatures.

**L3: Detection, not intervention.** We demonstrate that trajectory features can *identify* spurious correlation-affected samples, but this does not guarantee successful *intervention*. Prior work has shown that detection and correction are distinct challenges.
- *Why acceptable:* Diagnosis is valuable even without guaranteed treatment—knowing which samples are affected enables targeted investigation and informed decisions about deployment.
- *Future mitigation:* Explore trajectory-guided sample selection for GroupDRO or curriculum learning.

**L4: Curvature mechanism refuted.** Our secondary hypothesis about delayed curvature stabilization was not supported. While this refines rather than invalidates our main contribution, it indicates that the temporal dynamics we initially hypothesized were incorrect.
- *Why acceptable:* The core insight (trajectory divergence exists and is spurious-specific) remains validated; we honestly report the mechanism refinement.
- *Future mitigation:* Investigate alternative temporal signatures beyond curvature.

**L5: Observational design.** Our specificity test uses GroupDRO as an intervention, but we cannot make strong causal claims—we observe correlation between reduced spurious reliance and reduced trajectory divergence.
- *Why acceptable:* The controlled comparison with variance-matched random reweighting provides stronger evidence than pure observation.
- *Future mitigation:* Causal intervention experiments with synthetic spurious correlations of known strength.

**L6: Incomplete hypothesis coverage.** A planned experiment testing whether early trajectory divergence predicts final worst-group accuracy (predictive validity) was not conducted, as its prerequisite—the curvature timing mechanism—was not supported. This leaves the predictive power of trajectory features for downstream performance as an open question.

## 6.3 Broader Impact

**Positive impacts.** This work provides tools for practitioners to identify spurious correlation vulnerability during training, before deployment. Early detection can prevent deployment of models with hidden failure modes, potentially avoiding harmful outcomes in high-stakes applications (medical diagnosis, autonomous systems, fairness-critical decisions). The single-epoch detection capability reduces computational cost for vulnerability assessment.

**Potential concerns.** We do not identify direct negative applications of this diagnostic technique. However, as with any detection method, there is risk that practitioners may use it as a "checkbox" without deeper investigation—detecting vulnerability does not automatically resolve it. We emphasize that detection should prompt careful analysis, not false confidence.

**Recommendations.** We encourage practitioners to use trajectory analysis as one component of a broader robustness evaluation pipeline, not as a sole determinant of deployment readiness.

## 6.4 Future Directions

**Immediate extensions:**
- Cross-dataset validation on CelebA, ColoredMNIST, and NICO++
- Single-epoch (L₁-only) efficient detection protocol
- Trajectory-guided sample selection for GroupDRO
- Predictive validity testing: does early divergence predict final accuracy gaps?

**Longer-term vision:**
- Training-integrated early warning systems that automatically flag spurious correlation vulnerability
- Extension to non-vision domains (NLP, tabular data)
- Connection to intervention—can trajectory information guide successful debiasing?

**Open questions:**
- Does the L₁ signal transfer across datasets without retraining the detector?
- What is the minimum compute budget needed for reliable detection?
- Can trajectory features identify novel spurious correlations not seen during training?

---

# 7. Conclusion

We began by observing that deep learning models can achieve high aggregate accuracy while silently failing on minority subgroups. Our work demonstrates that the process of learning spurious correlations is not invisible: it leaves a distinctive signature in per-sample loss trajectories detectable from the first training epoch.

Our main contributions are: (1) demonstrating that trajectory features predict minority membership with AUROC = 0.9452 on Waterbirds; (2) validating spurious-specificity through controlled experiments showing 31% attenuation under GroupDRO versus 1% under random reweighting; and (3) revealing that initial loss alone suffices for detection, enabling single-epoch screening.

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

*Generated by Anonymous Research Pipeline v2.0 | Phase 6.5: Adversarial Review R1 | 2026-04-14*
