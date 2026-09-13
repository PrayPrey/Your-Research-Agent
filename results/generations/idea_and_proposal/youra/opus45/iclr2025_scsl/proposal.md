# Research Proposal: Multi-Signal Detection of Spurious Correlations via Training Dynamics and Augmentation Consistency

## 1. Introduction

### 1.1 Background

Deep learning models have achieved remarkable success across diverse domains, from computer vision to natural language processing. However, a persistent challenge undermines their reliability: the tendency to exploit spurious correlations—superficial patterns that correlate with labels in training data but fail to generalize under distribution shift. This phenomenon, often termed "shortcut learning," arises from the statistical nature of deep learning algorithms and their inherent inductive biases during data preprocessing, architecture design, and optimization.

The simplicity bias of neural networks, which causes them to preferentially learn simpler features before more complex ones, plays a central role in this problem. Spurious features such as image backgrounds, texture patterns, or linguistic artifacts are often simpler than the core semantic features that define true class membership. Consequently, models trained via standard empirical risk minimization (ERM) frequently rely on these shortcuts, leading to catastrophic failures when deployed in real-world scenarios where spurious correlations no longer hold—particularly affecting under-represented groups or minority populations.

Current approaches to detecting and mitigating spurious correlations face significant limitations. Methods like Group Distributionally Robust Optimization (GroupDRO) and Just Train Twice (JTT) require expensive group annotations that specify which examples belong to spurious-correlated subgroups. Such annotations are not scalable and may overlook spurious correlations that do not align with human perceptions. Furthermore, existing evaluation benchmarks provide limited guarantees of robustness, addressing only a few known spurious correlations while leaving unknown spurious features undetected.

### 1.2 Research Objectives

This research proposes Multi-Signal Detection (MSD), a novel framework for identifying spurious-reliant examples without requiring group labels. Our primary objectives are:

1. **Develop a dual-signal detection mechanism** that combines training dynamics (loss trajectory slopes and Prediction Depth) with prediction consistency under semantic-preserving augmentations to identify examples relying on spurious correlations.

2. **Validate the causal mechanism** underlying MSD by demonstrating that the conjunction of fast learning and augmentation inconsistency specifically flags spurious reliance, whereas neither signal alone achieves sufficient specificity.

3. **Demonstrate practical utility** by showing that targeted mitigation strategies applied to MSD-flagged examples significantly improve worst-group accuracy and out-of-distribution generalization.

4. **Extend applicability to foundation models** by adapting MSD to fine-tuning scenarios where full training dynamics are unavailable.

### 1.3 Significance

This research addresses a critical gap in the robustness literature: the inability to detect spurious-reliant examples without prior knowledge of what spurious features exist. By leveraging behavioral signatures that emerge naturally during training, MSD enables scalable robustness evaluation for foundation models across modalities. The foundational insights gained will advance our understanding of how neural networks learn shortcuts and inform the development of more robust training procedures. Furthermore, the proposed framework aligns with the workshop's objectives of developing comprehensive evaluation methods and exploring the foundations of spurious correlations in deep learning.

## 2. Methodology

### 2.1 Overview of Multi-Signal Detection (MSD)

MSD identifies spurious-reliant examples by combining two complementary behavioral signatures:

1. **Fast Learning Dynamics:** Measured via loss trajectory slopes during early training and Prediction Depth (the network layer at which correct predictions stabilize).

2. **Prediction Inconsistency:** Measured via variance of model outputs across semantic-preserving augmentations.

The theoretical foundation rests on simplicity bias: spurious features are simpler, learned faster at shallower layers, and produce unstable predictions when augmentations alter superficial cues while preserving core semantics.

### 2.2 Data Collection and Preprocessing

**Primary Datasets:**
- **Waterbirds:** A benchmark combining bird images with spurious background correlations (waterbirds on water backgrounds, landbirds on land backgrounds). Contains 4,795 training examples with known group labels for validation.
- **CelebA:** Celebrity face images where hair color spuriously correlates with gender classification. Contains 162,770 training examples.
- **CIFAR-10-S:** A controlled synthetic benchmark with single-pixel spurious features for ablation studies.

**Preprocessing Pipeline:**
1. Standard normalization and resizing appropriate to each dataset
2. No group label access during training (labels reserved for evaluation only)
3. Augmentation ensemble generation: For each example, generate $K=10$ semantic-preserving augmentations

**Augmentation Strategy:**
For vision tasks, we employ augmentations that preserve semantic content while potentially disrupting spurious features:
- Random cropping (preserves object, may alter background)
- Color jittering (preserves shape, alters texture/color cues)
- Gaussian blur (preserves structure, removes fine-grained artifacts)
- Random horizontal flipping (preserves identity for symmetric objects)

### 2.3 Algorithmic Framework

#### 2.3.1 Training Dynamics Extraction

During standard ERM training, we extract per-example dynamics:

**Loss Trajectory Slope:** For each example $i$, compute the loss at each epoch $t$ and fit a linear regression over the first $T_{\text{early}} = 0.1 \times T_{\text{total}}$ epochs:

$$s_i = \frac{\sum_{t=1}^{T_{\text{early}}} (t - \bar{t})(\mathcal{L}_i^{(t)} - \bar{\mathcal{L}}_i)}{\sum_{t=1}^{T_{\text{early}}} (t - \bar{t})^2}$$

where $\mathcal{L}_i^{(t)}$ is the loss for example $i$ at epoch $t$, and $\bar{t}$, $\bar{\mathcal{L}}_i$ are the respective means.

**Prediction Depth (PD):** Following Murali et al. (2023), we define Prediction Depth as the earliest layer $l$ at which a linear probe achieves correct classification:

$$\text{PD}_i = \min \{l : f_l(h_i^{(l)}) = y_i\}$$

where $h_i^{(l)}$ is the hidden representation at layer $l$ and $f_l$ is a linear classifier trained on layer $l$ representations.

**Fast Learning Score:** Combine slope and depth into a normalized fast learning score:

$$\text{FL}_i = \alpha \cdot \text{Normalize}(-s_i) + (1-\alpha) \cdot \text{Normalize}(L - \text{PD}_i)$$

where $L$ is the total number of layers and $\alpha = 0.5$ balances the two signals. Higher $\text{FL}_i$ indicates faster learning.

#### 2.3.2 Augmentation Consistency Measurement

After training converges, measure prediction consistency:

**Consistency Score:** For each example $i$, compute the variance of softmax outputs across $K$ augmentations:

$$\text{IC}_i = \frac{1}{C} \sum_{c=1}^{C} \text{Var}_{k=1}^{K} \left[ p_\theta(y=c | \text{Aug}_k(x_i)) \right]$$

where $C$ is the number of classes and $\text{Aug}_k$ denotes the $k$-th augmentation. Higher $\text{IC}_i$ indicates greater inconsistency.

#### 2.3.3 Multi-Signal Detection Score

The MSD score combines both signals:

$$\text{MSD}_i = \text{FL}_i \times \text{IC}_i$$

The multiplicative combination ensures that only examples exhibiting both fast learning AND prediction inconsistency receive high scores. This addresses the specificity problem: fast learning alone could indicate easy examples; inconsistency alone could indicate ambiguous examples.

**Threshold Selection:** Flag examples as spurious-reliant if:

$$\text{MSD}_i > \tau_{\text{MSD}}$$

where $\tau_{\text{MSD}}$ is set at the 75th percentile of MSD scores (tunable hyperparameter).

#### 2.3.4 Anchor Set Identification

To validate the mechanism, we identify an anchor set of examples likely relying on core features:

$$\mathcal{A} = \{i : \text{PD}_i > \text{Percentile}_{90}(\text{PD})\}$$

Examples with the highest Prediction Depth are assumed to require deeper processing, indicating reliance on more complex (core) features.

#### 2.3.5 Mitigation Strategy

Apply targeted loss upweighting to flagged examples during retraining:

$$\mathcal{L}_{\text{robust}} = \frac{1}{N} \sum_{i=1}^{N} w_i \cdot \mathcal{L}(f_\theta(x_i), y_i)$$

where:

$$w_i = \begin{cases} \lambda & \text{if } \text{MSD}_i > \tau_{\text{MSD}} \\ 1 & \text{otherwise} \end{cases}$$

with upweighting factor $\lambda \in [2, 5]$ determined via validation.

### 2.4 Experimental Design

#### 2.4.1 Experiment 1: Detection Accuracy (Primary)

**Objective:** Validate that MSD achieves high detection AUC without group labels.

**Protocol:**
1. Train ResNet-50 on Waterbirds/CelebA using standard ERM
2. Extract training dynamics and compute MSD scores
3. Evaluate detection AUC-ROC against ground-truth group labels

**Evaluation Metrics:**
- Primary: AUC-ROC > 0.75 (success threshold)
- Falsification: AUC-ROC ≤ 0.60 triggers hypothesis rejection
- Statistical test: Bootstrap 95% confidence intervals, $n \geq 20$ random seeds

#### 2.4.2 Experiment 2: Mechanism Validation

**Objective:** Confirm the causal mechanism linking simplicity bias to detection.

**Protocol:**
1. Compare Prediction Depth distributions between MSD-flagged and non-flagged examples
2. Compare augmentation variance distributions
3. Ablate individual signals (FL-only, IC-only) versus combined MSD

**Evaluation Metrics:**
- Two-sample t-test for distribution differences ($p < 0.01$)
- Cohen's d effect size > 0.5 (medium effect)
- Ablation: MSD AUC > max(FL-only AUC, IC-only AUC)

#### 2.4.3 Experiment 3: Mitigation Effectiveness

**Objective:** Demonstrate practical utility through worst-group accuracy improvement.

**Protocol:**
1. Retrain model with MSD-based loss upweighting
2. Compare against baselines: ERM, JTT, GroupDRO (with oracle labels)

**Evaluation Metrics:**
- Worst-group accuracy improvement > 10% over ERM
- Average accuracy degradation < 2% (maintain overall performance)
- Comparison with JTT (no group labels) and GroupDRO (oracle upper bound)

#### 2.4.4 Experiment 4: Foundation Model Extension

**Objective:** Validate MSD applicability to fine-tuning scenarios.

**Protocol:**
1. Fine-tune CLIP/ViT on Waterbirds with limited epochs
2. Adapt dynamics extraction to fine-tuning regime (probe-based PD)
3. Evaluate detection and mitigation performance

**Evaluation Metrics:**
- Detection AUC > 0.70 (relaxed threshold for transfer setting)
- Worst-group improvement > 5%

### 2.5 Baseline Methods

| Method | Group Labels Required | Description |
|--------|----------------------|-------------|
| ERM | No | Standard empirical risk minimization |
| JTT | No | Identifies misclassified examples after initial training |
| GEORGE | No | Clustering-based group discovery |
| GroupDRO | Yes (oracle) | Optimizes worst-group performance |
| CVaR DRO | No | Conditional value-at-risk optimization |

### 2.6 Implementation Details

- **Architecture:** ResNet-50 (vision), BERT-base (language)
- **Optimizer:** SGD with momentum 0.9, learning rate 0.001
- **Training:** 100 epochs with early stopping
- **Dynamics storage:** Per-example loss logged every epoch; gradient norms sampled every 10 iterations
- **Computational overhead:** Estimated 20% increase in training time for dynamics tracking
- **Hardware:** 4× NVIDIA A100 GPUs
- **Random seeds:** Minimum 20 seeds for statistical validity

## 3. Expected Outcomes

### 3.1 Primary Outcomes

1. **Detection Performance:** We expect MSD to achieve AUC-ROC > 0.75 on Waterbirds and CelebA benchmarks, representing a significant improvement over single-signal methods (JTT: ~0.65-0.70 AUC).

2. **Mechanism Validation:** Flagged examples will exhibit significantly lower Prediction Depth (Cohen's d > 0.5) and higher augmentation variance compared to non-flagged examples, confirming the proposed causal mechanism.

3. **Mitigation Effectiveness:** Worst-group accuracy will improve by >10% over ERM baseline (e.g., from 60% to 72% on Waterbirds), approaching GroupDRO performance without requiring group labels.

### 3.2 Secondary Outcomes

4. **Signal Complementarity:** Ablation studies will demonstrate that the multiplicative combination of FL and IC signals outperforms either signal alone by at least 5% AUC.

5. **Foundation Model Applicability:** MSD will maintain detection AUC > 0.70 in fine-tuning scenarios, enabling scalable robustness evaluation for large pre-trained models.

### 3.3 Potential Limitations and Mitigations

- **Augmentation-invariant spurious features:** Some spurious features may be preserved under all augmentations. Mitigation: Develop domain-specific augmentation strategies; combine with complementary detection methods.

- **Threshold sensitivity:** Performance may vary with hyperparameter choices. Mitigation: Comprehensive sensitivity analysis; adaptive threshold selection based on score distributions.

- **Computational overhead:** Dynamics tracking increases training cost. Mitigation: Efficient implementation with checkpoint-based logging; sampling strategies for large datasets.

## 4. Impact

### 4.1 Scientific Impact

This research advances the foundational understanding of shortcut learning in deep neural networks by:

1. **Mechanistic Insight:** Providing empirical evidence for the causal chain linking simplicity bias to spurious feature reliance, contributing to the theoretical foundations of deep learning generalization.

2. **Methodological Innovation:** Introducing a principled dual-signal framework that addresses the specificity limitations of single-signal detection methods.

3. **Benchmark Contribution:** Establishing evaluation protocols for spurious correlation detection that do not require group annotations, enabling more comprehensive robustness assessment.

### 4.2 Practical Impact

1. **Scalable Robustness Evaluation:** MSD enables practitioners to identify potential spurious correlations in large-scale models without expensive annotation efforts, facilitating safer deployment of AI systems.

2. **Foundation Model Auditing:** The extension to fine-tuning scenarios provides tools for auditing large language models and multimodal models for spurious reliance, addressing a critical need as these models become ubiquitous.

3. **Domain-Agnostic Framework:** The behavioral signature approach generalizes across modalities (vision, language, multimodal), providing a unified framework for robustness evaluation.

### 4.3 Broader Implications

By improving the detection and mitigation of spurious correlations, this research contributes to the ethical deployment of machine learning systems. Models that rely on spurious features often exhibit disparate performance across demographic groups, perpetuating biases and causing harm to minority populations. MSD provides a pathway toward more equitable AI systems by enabling targeted interventions that improve worst-group performance without requiring explicit demographic annotations.

The insights gained from this research will inform future work on causal representation learning, robust optimization, and the development of training procedures that inherently resist shortcut learning. By bridging the gap between theoretical understanding and practical solutions, this work advances the broader goal of building AI systems that are reliable, robust, and trustworthy.