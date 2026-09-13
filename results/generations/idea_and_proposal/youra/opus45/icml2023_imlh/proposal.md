# Research Proposal: Variational Concept Bottleneck Models for Calibrated Medical Image Interpretation

## 1. Introduction

### 1.1 Background

The integration of machine learning (ML) into healthcare has accelerated dramatically, with deep learning models achieving expert-level performance in medical image interpretation tasks ranging from chest X-ray analysis to pathology slide classification. However, the deployment of these systems in clinical practice faces a fundamental barrier: the black-box nature of neural networks undermines physician trust and prevents meaningful human-AI collaboration. When a model predicts pneumonia from a chest radiograph, clinicians need to understand not only the prediction but also the reasoning pathway and the confidence associated with each clinical finding.

Concept Bottleneck Models (CBMs) represent a significant advancement toward interpretable medical AI by introducing an intermediate layer of human-understandable concepts between raw inputs and final predictions. In medical imaging, these concepts correspond to clinical findings—such as "cardiomegaly," "pleural effusion," or "lung opacity"—that radiologists routinely assess. By first predicting these concepts and then using them for final diagnosis, CBMs provide a transparent reasoning pathway that aligns with clinical practice.

Despite their interpretability advantages, current CBMs suffer from a critical limitation: they produce deterministic point estimates for concept predictions without quantifying uncertainty. In high-stakes medical settings, this limitation has profound implications. A model might predict "lung opacity present" with equal apparent confidence whether the finding is unambiguous or highly uncertain due to image quality, anatomical variation, or borderline presentation. Clinicians cannot distinguish between confident and uncertain predictions, preventing them from knowing when to trust the model versus when to apply additional scrutiny.

Uncertainty quantification (UQ) has emerged as essential for trustworthy medical AI. Calibrated confidence estimates—where predicted probabilities align with actual accuracy—enable appropriate clinical decision-making. When a model reports 90% confidence, that prediction should be correct approximately 90% of the time. Poor calibration leads to either over-reliance on incorrect predictions or unnecessary dismissal of accurate ones.

### 1.2 Research Objectives

This research proposes Variational Concept Bottleneck Models (V-CBM), a novel architecture that integrates variational inference into the concept prediction layer to provide calibrated, per-concept uncertainty estimates. Our primary objectives are:

1. **Develop V-CBM Architecture:** Design and implement variational concept layers that output Gaussian distribution parameters (μ, σ²) for each clinical concept, enabling principled uncertainty quantification through learned distributions.

2. **Improve Concept-Level Calibration:** Demonstrate that V-CBM achieves superior calibration compared to vanilla CBMs, with a target of >30% reduction in Expected Calibration Error (ECE) at the concept level.

3. **Enable Targeted Clinical Intervention:** Validate that concept-level uncertainty estimates identify predictions requiring clinician review, improving human-AI collaboration efficiency.

4. **Establish Evaluation Framework:** Develop comprehensive metrics and protocols for assessing calibrated interpretability in medical imaging systems.

### 1.3 Significance

This research addresses the critical intersection of interpretability and uncertainty quantification in medical AI. By providing calibrated confidence at the concept level—the level at which clinicians reason—V-CBM enables a new paradigm of human-AI collaboration. Physicians can focus their attention on uncertain findings while trusting confident predictions, optimizing workflow efficiency without compromising patient safety.

Furthermore, this work contributes to the broader goal of developing ML systems aligned with clinical reasoning. By embedding uncertainty into interpretable intermediate representations, we move toward AI systems that communicate their limitations in clinically meaningful terms, facilitating appropriate trust calibration and ultimately safer deployment in healthcare settings.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathbf{x} \in \mathcal{X}$ denote a medical image and $y \in \mathcal{Y}$ the diagnostic label. In CBMs, we introduce intermediate concepts $\mathbf{c} = (c_1, c_2, \ldots, c_K)$ representing $K$ clinical findings. The standard CBM factorizes prediction as:

$$P(y|\mathbf{x}) = P(y|\mathbf{c}) \cdot P(\mathbf{c}|\mathbf{x})$$

where $P(\mathbf{c}|\mathbf{x})$ is typically modeled as deterministic point predictions. Our V-CBM instead models each concept as a latent variable with learned uncertainty:

$$P(c_k|\mathbf{x}) = \mathcal{N}(c_k; \mu_k(\mathbf{x}), \sigma_k^2(\mathbf{x}))$$

### 2.2 V-CBM Architecture

#### 2.2.1 Base Encoder

We employ DenseNet-121 pretrained on ImageNet as the feature extractor $f_\theta: \mathcal{X} \rightarrow \mathbb{R}^d$, producing a $d$-dimensional representation $\mathbf{h} = f_\theta(\mathbf{x})$.

#### 2.2.2 Variational Concept Layer

For each concept $k \in \{1, \ldots, K\}$, we define dual prediction heads:

$$\mu_k = W_\mu^{(k)} \mathbf{h} + b_\mu^{(k)}$$
$$\log \sigma_k^2 = W_\sigma^{(k)} \mathbf{h} + b_\sigma^{(k)}$$

where $W_\mu^{(k)}, W_\sigma^{(k)} \in \mathbb{R}^{1 \times d}$ and $b_\mu^{(k)}, b_\sigma^{(k)} \in \mathbb{R}$ are learnable parameters.

#### 2.2.3 Reparameterization Trick

To enable gradient-based optimization through the stochastic sampling, we apply the reparameterization trick:

$$\hat{c}_k = \mu_k + \sigma_k \cdot \epsilon_k, \quad \epsilon_k \sim \mathcal{N}(0, 1)$$

During training, we sample once per forward pass. During inference, we perform Monte Carlo sampling with $M$ samples to estimate predictive uncertainty.

#### 2.2.4 Label Predictor

The final diagnosis is predicted from sampled concepts:

$$P(y|\mathbf{x}) = \text{softmax}(W_y \hat{\mathbf{c}} + b_y)$$

where $\hat{\mathbf{c}} = (\hat{c}_1, \ldots, \hat{c}_K)^T$.

### 2.3 Training Objective

We optimize the Evidence Lower Bound (ELBO) combining reconstruction of concept labels and KL regularization:

$$\mathcal{L} = \mathcal{L}_{\text{concept}} + \mathcal{L}_{\text{label}} + \beta \cdot \mathcal{L}_{\text{KL}}$$

**Concept Reconstruction Loss:**
$$\mathcal{L}_{\text{concept}} = \sum_{k=1}^{K} \text{BCE}(\sigma(\hat{c}_k), c_k^*)$$

where $c_k^*$ is the ground-truth concept annotation and $\sigma(\cdot)$ is the sigmoid function.

**Label Prediction Loss:**
$$\mathcal{L}_{\text{label}} = \text{CE}(P(y|\mathbf{x}), y^*)$$

**KL Divergence Regularization:**
$$\mathcal{L}_{\text{KL}} = \sum_{k=1}^{K} D_{\text{KL}}(\mathcal{N}(\mu_k, \sigma_k^2) \| \mathcal{N}(0, 1))$$

$$= \frac{1}{2} \sum_{k=1}^{K} \left( \mu_k^2 + \sigma_k^2 - \log \sigma_k^2 - 1 \right)$$

The hyperparameter $\beta \in [0.001, 0.1]$ controls the strength of regularization.

### 2.4 Inference and Uncertainty Estimation

#### 2.4.1 Monte Carlo Inference

At test time, we draw $M$ samples from each concept distribution:

$$\hat{c}_k^{(m)} = \mu_k + \sigma_k \cdot \epsilon_k^{(m)}, \quad m = 1, \ldots, M$$

The predictive distribution is approximated as:

$$P(y|\mathbf{x}) \approx \frac{1}{M} \sum_{m=1}^{M} P(y|\hat{\mathbf{c}}^{(m)})$$

#### 2.4.2 Concept-Level Confidence

For each concept, we compute calibrated confidence as:

$$\text{Conf}_k = \sigma\left(\frac{\mu_k}{\sqrt{1 + \sigma_k^2}}\right)$$

This formulation accounts for both the mean prediction and its uncertainty, providing confidence estimates that naturally decrease when uncertainty is high.

### 2.5 Data Collection and Preprocessing

#### 2.5.1 Datasets

**CheXpert:** A large chest radiograph dataset containing 224,316 images from 65,240 patients with annotations for 14 observations (concepts) including cardiomegaly, edema, consolidation, atelectasis, and pleural effusion. Importantly, CheXpert provides multi-level labels (positive, negative, uncertain, not mentioned) that align with our uncertainty-aware framework.

**MIMIC-CXR:** A complementary dataset with 377,110 chest X-rays and free-text radiology reports. We extract concept labels using the CheXpert labeler, providing additional validation data.

#### 2.5.2 Preprocessing Pipeline

1. **Image Standardization:** Resize to 224×224 pixels, normalize using ImageNet statistics
2. **Concept Label Processing:** Convert multi-level labels to continuous targets: positive=1.0, uncertain=0.5, negative=0.0
3. **Data Augmentation:** Random horizontal flip, rotation (±15°), and intensity scaling during training
4. **Train/Validation/Test Split:** 70%/10%/20% stratified by patient ID to prevent data leakage

### 2.6 Experimental Design

#### 2.6.1 Baseline Methods

1. **Vanilla CBM:** Standard Concept Bottleneck Model with deterministic concept predictions
2. **MC Dropout CBM:** CBM with dropout (p=0.2) applied during inference for uncertainty estimation
3. **Temperature Scaling CBM:** Post-hoc calibration applied to vanilla CBM predictions
4. **Ensemble CBM:** Ensemble of 5 independently trained CBMs

#### 2.6.2 Ablation Studies

1. **Architecture Ablations:**
   - V-CBM without KL regularization ($\beta = 0$)
   - V-CBM with shared variance across concepts
   - V-CBM with different prior distributions

2. **Hyperparameter Sensitivity:**
   - KL weight: $\beta \in \{0.001, 0.005, 0.01, 0.05, 0.1\}$
   - MC samples: $M \in \{5, 10, 20, 50\}$

#### 2.6.3 Evaluation Protocol

**Cross-Validation:** 5-fold cross-validation with fixed random seeds (42, 123, 456, 789, 1011) for reproducibility.

**Statistical Analysis:** Paired t-tests with Bonferroni correction ($\alpha = 0.017$), reporting mean differences, 95% confidence intervals, and Cohen's d effect sizes.

### 2.7 Evaluation Metrics

#### 2.7.1 Calibration Metrics

**Concept-Level Expected Calibration Error (ECE):**

$$\text{ECE}_k = \sum_{b=1}^{B} \frac{|S_b|}{N} |\text{acc}(S_b) - \text{conf}(S_b)|$$

where $S_b$ is the set of predictions in bin $b$, $\text{acc}(S_b)$ is the accuracy within the bin, and $\text{conf}(S_b)$ is the average confidence.

**Aggregate ECE:** Average ECE across all concepts:
$$\text{ECE} = \frac{1}{K} \sum_{k=1}^{K} \text{ECE}_k$$

**Maximum Calibration Error (MCE):** Worst-case calibration across bins.

#### 2.7.2 Predictive Performance

- **Concept AUC:** Area under ROC curve for each concept prediction
- **Label Accuracy:** Final diagnostic classification accuracy
- **Label AUC:** Area under ROC curve for final diagnosis

#### 2.7.3 Uncertainty Quality

**Uncertainty-Error Correlation:** Spearman correlation between $\sigma_k$ and prediction error $|c_k^* - \hat{c}_k|$

**Selective Prediction:** Accuracy when rejecting predictions with uncertainty above threshold $\tau$

#### 2.7.4 Clinical Utility

**Intervention Efficiency:** Accuracy improvement per clinician intervention, measured as:

$$\text{IE} = \frac{\text{Acc}_{\text{post-intervention}} - \text{Acc}_{\text{pre-intervention}}}{\text{Number of interventions}}$$

**OOD Detection AUROC:** Using concept uncertainty to detect out-of-distribution samples

### 2.8 Implementation Details

- **Framework:** PyTorch with torch-uncertainty library for variational layers
- **Optimization:** AdamW optimizer, learning rate $10^{-4}$ with cosine annealing
- **Batch Size:** 32 images
- **Training Epochs:** 50 with early stopping (patience=10)
- **Hardware:** 4× NVIDIA A100 GPUs
- **Reproducibility:** All code and trained models will be released publicly

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Calibration Improvement:** We hypothesize that V-CBM will achieve >30% reduction in concept-level ECE compared to vanilla CBM. Based on preliminary analysis and related work in variational inference for calibration, we expect:

- Vanilla CBM ECE: ~0.15-0.20
- V-CBM ECE: ~0.08-0.12
- Relative improvement: 35-45%

**Maintained Predictive Performance:** V-CBM should maintain comparable or slightly improved diagnostic accuracy (within 1-2% of vanilla CBM) while providing calibrated uncertainty.

**Uncertainty-Error Alignment:** High-uncertainty concepts should correlate strongly (Spearman ρ > 0.6) with prediction errors, enabling targeted intervention.

### 3.2 Secondary Expected Outcomes

**Intervention Efficiency:** When clinicians correct high-uncertainty concept predictions, accuracy improvement should exceed random intervention by >2×, demonstrating the clinical utility of uncertainty-guided review.

**OOD Detection:** Concept-level uncertainty should outperform prediction-level entropy for detecting out-of-distribution samples by >15% AUROC, as uncertainty at the reasoning level captures distributional shift more effectively.

**Interpretable Uncertainty:** Unlike black-box uncertainty methods, V-CBM provides uncertainty estimates for each clinical finding, enabling clinicians to understand *which aspects* of the prediction are uncertain.

### 3.3 Potential Limitations

1. **Computational Overhead:** MC sampling increases inference time by approximately 10× compared to deterministic inference. For time-critical applications, this may require optimization through amortized inference or reduced sample counts.

2. **Concept Annotation Requirement:** V-CBM requires concept-annotated training data, limiting applicability to domains with established clinical ontologies.

3. **Gaussian Assumption:** The assumption of Gaussian-distributed concept predictions may not capture all forms of uncertainty, particularly for inherently binary concepts.

### 3.4 Broader Impact

**Clinical Translation:** By providing calibrated, interpretable uncertainty, V-CBM addresses a key barrier to clinical AI adoption. Physicians can appropriately calibrate their trust in AI predictions, improving both efficiency and safety.

**Regulatory Alignment:** Regulatory bodies increasingly require uncertainty quantification for medical AI devices. V-CBM provides a principled framework meeting these requirements while maintaining interpretability.

**Research Foundation:** This work establishes a foundation for uncertainty-aware interpretable AI, with potential extensions to other medical domains (pathology, dermatology), multi-modal data, and concept correlation modeling.

**Ethical Considerations:** By making AI uncertainty explicit and interpretable, V-CBM supports informed clinical decision-making and helps prevent over-reliance on AI predictions. The framework also enables identification of systematic uncertainties that may indicate dataset biases or underrepresented populations.

### 3.5 Dissemination Plan

1. **Open-Source Release:** Complete codebase, trained models, and evaluation scripts
2. **Benchmark Contribution:** Standardized evaluation protocol for calibrated interpretable medical AI
3. **Clinical Collaboration:** Partnership with radiology departments for prospective validation
4. **Publication:** Target venues include MICCAI, NeurIPS (ML4H workshop), and Nature Medicine

In conclusion, Variational Concept Bottleneck Models represent a significant advancement toward trustworthy medical AI by unifying interpretability and calibrated uncertainty quantification. By providing confidence estimates at the level of clinical reasoning, V-CBM enables effective human-AI collaboration and supports the safe deployment of AI in healthcare settings.