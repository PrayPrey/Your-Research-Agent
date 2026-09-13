# Research Proposal: Temporal Concept Bottleneck Models with Multi-Scale Hierarchical Residuals for Interpretable Clinical Time Series

## 1. Introduction

### 1.1 Background

Clinical time series data—including electrocardiograms (ECG), intensive care unit (ICU) vital signs, and wearable health monitoring signals—represent a cornerstone of modern healthcare decision-making. These temporal data streams encode rich diagnostic and prognostic information that, when properly analyzed, can support early disease detection, risk stratification, and personalized treatment planning. Deep learning methods, particularly transformer-based architectures, have demonstrated remarkable performance on clinical time series tasks, often matching or exceeding human expert accuracy in specific diagnostic scenarios.

However, a critical barrier impedes the clinical adoption of these powerful models: the interpretability gap. Current state-of-the-art deep learning models operate as "black boxes," providing predictions without explanations that clinicians can understand, trust, or act upon. While attention-based visualization methods have emerged as a popular explanation technique, they fundamentally address only "what" the model focuses on (temporal regions with high attention weights) rather than "why" in clinically meaningful terms. A clinician presented with attention heatmaps cannot readily translate these into actionable clinical reasoning such as "elevated heart rate segment indicating tachycardia" or "ST-segment depression suggesting ischemia."

This interpretability deficit is particularly problematic in healthcare settings where clinical decisions carry life-or-death consequences. Regulatory frameworks increasingly require explainable AI systems, and clinicians rightfully demand understanding of model reasoning before incorporating AI recommendations into patient care. The challenge is compounded by the inherent complexity of clinical time series: multi-scale temporal patterns (from individual heartbeats to hour-long episodes), high dimensionality from multimodal sources, irregular sampling, and missing values.

Concept Bottleneck Models (CBMs) offer a promising paradigm for interpretable machine learning by constraining model representations to pass through human-understandable concepts before making predictions. Originally developed for static image classification, CBMs have demonstrated that interpretability need not come at the cost of accuracy when properly designed. However, existing CBM approaches fail to capture the multi-scale temporal dynamics inherent in clinical time series, where clinically meaningful patterns manifest across vastly different time scales—from sub-second waveform morphology to hour-long physiological trends.

### 1.2 Research Objectives

This research proposes **Temporal Concept Bottleneck Models with Multi-scale Hierarchical Residuals (T-CBM-MHR)**, a novel architecture that bridges the interpretability-performance gap for clinical time series analysis. Our primary objectives are:

1. **Develop a hierarchical temporal concept framework** that captures clinical patterns across multiple time scales (beat-level: ~1 second, segment-level: ~5 minutes, episode-level: ~1 hour), aligned with how clinicians naturally reason about temporal health data.

2. **Design a hybrid representation mechanism** that combines clinically-defined concepts with a learned residual pathway, preserving predictive capacity for patterns not captured by predefined concepts while maintaining interpretability.

3. **Validate the interpretability-performance tradeoff** through rigorous empirical evaluation, demonstrating that T-CBM-MHR achieves clinician interpretability ratings significantly higher than attention-based methods (target: >3.5/5) while maintaining accuracy within 3% of black-box transformers.

4. **Establish causal mechanisms** through systematic ablation studies verifying each component's contribution to the overall system performance.

### 1.3 Significance

This research addresses a fundamental challenge in healthcare AI: making powerful deep learning models trustworthy and actionable in clinical practice. By providing explanations in terms clinicians understand—clinical concepts rather than attention weights—T-CBM-MHR can accelerate the translation of AI research into clinical deployment. The multi-scale hierarchical design specifically addresses the temporal complexity of health data, while the residual pathway ensures that interpretability does not sacrifice predictive performance.

The proposed approach is particularly relevant for minority data groups and under-explored clinical domains (pediatrics, rare diseases, critical care) where limited data availability makes interpretable models essential for building clinician trust and enabling meaningful human-AI collaboration.

## 2. Methodology

### 2.1 Problem Formulation

Given a clinical time series $\mathbf{X} = \{x_1, x_2, ..., x_T\} \in \mathbb{R}^{T \times D}$ with $T$ time steps and $D$ features, and a set of predefined clinical concepts $\mathcal{C} = \{c_1, c_2, ..., c_K\}$ organized hierarchically across $S$ temporal scales, our goal is to learn a mapping $f: \mathbf{X} \rightarrow (y, \mathbf{c})$ that simultaneously predicts the clinical outcome $y$ and produces interpretable concept activations $\mathbf{c} \in [0,1]^K$.

### 2.2 Architecture Overview

T-CBM-MHR consists of four main components operating in sequence:

**Component 1: Multi-Scale Temporal Encoder**

We employ a transformer-based encoder with scale-specific processing. For each scale $s \in \{1, 2, 3\}$ (beat, segment, episode), we extract features:

$$\mathbf{H}^{(s)} = \text{TransformerEncoder}_s(\text{Pool}_s(\mathbf{X}))$$

where $\text{Pool}_s$ applies temporal pooling appropriate for scale $s$, and $\text{TransformerEncoder}_s$ consists of 4 layers with hidden dimension 256 and standard positional encoding. The multi-scale representation is:

$$\mathbf{H}_{multi} = \text{Concat}[\mathbf{H}^{(1)}, \mathbf{H}^{(2)}, \mathbf{H}^{(3)}]$$

**Component 2: Concept Alignment Layer**

For each clinical concept $c_k$ at scale $s$, we learn a concept predictor:

$$\hat{c}_k = \sigma(\mathbf{W}_k^T \mathbf{h}^{(s)} + b_k)$$

where $\mathbf{h}^{(s)}$ is the scale-appropriate hidden representation, $\mathbf{W}_k$ and $b_k$ are learnable parameters, and $\sigma$ is the sigmoid function. The concept alignment loss ensures representations align with clinically-defined concepts:

$$\mathcal{L}_{concept} = \frac{1}{K} \sum_{k=1}^{K} \text{BCE}(\hat{c}_k, c_k^{gt})$$

where $c_k^{gt}$ denotes ground-truth concept labels when available, or pseudo-labels derived from clinical rules.

**Component 3: Hybrid Representation with Residual Pathway**

The hybrid representation combines concept activations with a learned residual:

$$\mathbf{z}_{hybrid} = (1-\alpha) \cdot \mathbf{z}_{concept} + \alpha \cdot \mathbf{z}_{residual}$$

where $\mathbf{z}_{concept} = [\hat{c}_1, \hat{c}_2, ..., \hat{c}_K]$ is the concept activation vector, $\mathbf{z}_{residual} = \text{MLP}(\mathbf{H}_{multi})$ captures patterns not covered by predefined concepts, and $\alpha \in [0.1, 0.3]$ controls the residual pathway ratio.

**Component 4: Prediction Head**

The final prediction is made from the hybrid representation:

$$\hat{y} = \text{Classifier}(\mathbf{z}_{hybrid})$$

### 2.3 Training Objective

The joint training objective balances task performance with concept alignment:

$$\mathcal{L}_{total} = \lambda_{task} \cdot \mathcal{L}_{task} + \lambda_{concept} \cdot \mathcal{L}_{concept} + \lambda_{reg} \cdot \mathcal{L}_{reg}$$

where $\mathcal{L}_{task}$ is the cross-entropy loss for classification, $\lambda_{concept} \in [0.1, 1.0]$ (default 0.5) weights concept alignment, and $\mathcal{L}_{reg}$ includes standard regularization terms.

### 2.4 Clinical Concept Definition

We define clinical concepts hierarchically:

**Beat-level concepts (Scale 1, ~1s):** QRS morphology, P-wave presence, T-wave inversion, premature beats
**Segment-level concepts (Scale 2, ~5min):** Heart rate variability, rhythm regularity, ST-segment changes, blood pressure trends
**Episode-level concepts (Scale 3, ~1hr+):** Sustained tachycardia, hypotensive episodes, respiratory deterioration patterns

Concepts are derived from: (1) clinical guidelines (ICD-10, SNOMED-CT), (2) expert annotations in datasets (PTB-XL diagnostic labels), and (3) rule-based extraction from physiological thresholds.

### 2.5 Data Collection and Preprocessing

**Dataset 1: PTB-XL (ECG)**
- 21,837 12-lead ECG recordings from 18,885 patients
- 10-second recordings at 500Hz
- Expert-annotated diagnostic labels (71 classes)
- Preprocessing: Bandpass filtering (0.5-40Hz), baseline wander removal, z-score normalization

**Dataset 2: MIMIC-IV (ICU Vitals)**
- ICU stays from Beth Israel Deaconess Medical Center
- Vital signs: heart rate, blood pressure, respiratory rate, SpO2, temperature
- Preprocessing: Resampling to 1-minute intervals, forward-fill imputation for missing values (<20%), outlier removal (>5 SD)

**Train/Validation/Test Split:** 70%/15%/15% with patient-level stratification to prevent data leakage.

### 2.6 Experimental Design

**Experiment 1: Interpretability Evaluation (Primary)**

*Objective:* Validate that T-CBM-MHR provides clinically meaningful explanations superior to attention-based methods.

*Protocol:*
1. Select 50 representative cases spanning diagnostic categories
2. Generate explanations from: (a) T-CBM-MHR concept activations, (b) Transformer attention weights, (c) Post-hoc SHAP values
3. Present explanations to 5 board-certified clinicians (blinded to method)
4. Clinicians rate each explanation on 5-point Likert scale for: clinical relevance, actionability, trustworthiness

*Metrics:*
- Mean clinician rating (target: T-CBM-MHR > 3.5/5)
- Rating difference vs. attention baseline (target: > 0.5 points, p < 0.05)
- Inter-rater reliability (Fleiss' κ, target: > 0.6)

**Experiment 2: Concept Intervention Accuracy**

*Objective:* Verify that concept activations causally influence predictions.

*Protocol:*
1. For each test case, identify the top-3 activated concepts
2. Intervene by setting concept activation to opposite value
3. Measure prediction change

*Metric:* Concept intervention accuracy (target: > 70%)

$$\text{CIA} = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}[\text{sign}(\hat{y}_i - \hat{y}_i^{intervened}) = \text{expected}]$$

**Experiment 3: Performance Preservation**

*Objective:* Confirm accuracy within 3% of black-box transformer.

*Baselines:*
- Black-box Transformer (same architecture, no concept bottleneck)
- LSTM baseline
- XGBoost with hand-crafted features

*Metrics:*
- AUROC, AUPRC for classification tasks
- Performance ratio: $\text{AUROC}_{T-CBM} / \text{AUROC}_{black-box} \geq 0.97$

**Experiment 4: Ablation Studies**

*Objective:* Verify causal mechanism components.

| Ablation | Configuration | Tests |
|----------|---------------|-------|
| A1: Single-scale | Remove multi-scale, use only segment-level | H-M1 |
| A2: No concept alignment | Remove $\mathcal{L}_{concept}$ | H-M2 |
| A3: No residual pathway | Set $\alpha = 0$ | H-M3 |
| A4: Random concepts | Replace clinical concepts with random vectors | H-M4 |

*Success Criteria:* Each ablation should show statistically significant degradation (p < 0.05) in either interpretability or accuracy.

**Experiment 5: Residual Pathway Analysis**

*Objective:* Ensure residual pathway does not dominate representation.

*Metric:* Residual information ratio

$$\text{RIR} = \frac{\text{MI}(\mathbf{z}_{residual}; y)}{\text{MI}(\mathbf{z}_{hybrid}; y)}$$

*Threshold:* RIR < 0.5 (concepts should capture majority of predictive information)

### 2.7 Evaluation Metrics Summary

| Metric | Target | Measurement |
|--------|--------|-------------|
| Clinician interpretability rating | > 3.5/5 | 5-point Likert scale |
| Rating improvement vs. attention | > 0.5 points (p < 0.05) | Paired t-test |
| Inter-rater reliability | κ > 0.6 | Fleiss' kappa |
| Concept intervention accuracy | > 70% | Prediction change rate |
| AUROC preservation | ≥ 97% of black-box | Ratio comparison |
| Residual information ratio | < 50% | Mutual information |

### 2.8 Statistical Analysis Plan

- **Sample size:** 20+ clinician evaluations for interpretability (power = 0.8, effect size d = 0.8)
- **Significance level:** α = 0.05 with Bonferroni correction for multiple comparisons
- **Reporting:** Mean ± SD, 95% confidence intervals, Cohen's d effect sizes, exact p-values
- **Reproducibility:** 5 random seeds for all experiments, report mean and standard deviation

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome:** We expect T-CBM-MHR to achieve clinician interpretability ratings of 3.8-4.2/5, significantly exceeding attention-based explanations (expected: 2.8-3.2/5) with a difference of approximately 0.8-1.0 points (p < 0.01). This would validate our core hypothesis that concept-based explanations aligned with clinical reasoning are more interpretable than attention visualizations.

**Secondary Outcomes:**
1. **Performance preservation:** AUROC within 1-2% of black-box transformers, demonstrating that the interpretability-performance tradeoff is manageable with proper hybrid representation design.
2. **Multi-scale value:** 5-10% improvement in both interpretability and accuracy compared to single-scale concept designs, validating the importance of hierarchical temporal concepts.
3. **Causal mechanism validation:** All four ablation studies showing significant degradation, confirming each component's contribution.

### 3.2 Scientific Impact

This research advances the field of interpretable machine learning for healthcare in several ways:

1. **Novel architecture:** T-CBM-MHR represents the first concept bottleneck model specifically designed for multi-scale temporal data, addressing a gap in the existing CBM literature.

2. **Methodological contribution:** The hybrid representation with residual pathway provides a principled approach to balancing interpretability constraints with predictive capacity.

3. **Evaluation framework:** Our clinician-centered evaluation protocol establishes a rigorous standard for assessing interpretability in clinical AI systems.

### 3.3 Clinical Impact

**Immediate applications:**
- ECG interpretation support with concept-level explanations
- ICU early warning systems with transparent risk factors
- Clinical decision support that clinicians can understand and trust

**Long-term implications:**
- Accelerated regulatory approval through demonstrable interpretability
- Improved human-AI collaboration in clinical settings
- Foundation for interpretable AI in other temporal health domains (wearables, continuous glucose monitoring)

### 3.4 Broader Impact

This work addresses the critical need for trustworthy AI in healthcare, particularly relevant for:
- **Minority data groups:** Interpretable models enable clinicians to identify when AI reasoning may not apply to underrepresented populations
- **Rare diseases:** Concept-based explanations facilitate knowledge transfer and expert validation
- **Critical care:** Transparent predictions support high-stakes decision-making

### 3.5 Limitations and Future Work

We acknowledge several limitations: (1) concept completeness depends on available clinical knowledge, (2) clinician evaluation is resource-intensive, and (3) the approach requires domain-specific concept definition. Future work will explore automated concept discovery, extension to additional clinical domains, and real-world deployment studies.

In conclusion, T-CBM-MHR offers a principled approach to interpretable clinical time series analysis that maintains competitive accuracy while providing explanations clinicians can understand, trust, and act upon—a critical step toward realizing the potential of AI in healthcare.