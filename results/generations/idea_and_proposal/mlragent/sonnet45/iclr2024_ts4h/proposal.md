# Research Proposal: Uncertainty-Aware Multimodal Time Series Imputation with Diffusion Models for Robust Clinical Decision Support

## 1. Title

**Uncertainty-Aware Multimodal Time Series Imputation with Diffusion Models for Robust Clinical Decision Support**

## 2. Introduction

### 2.1 Background

Healthcare time series data represent a cornerstone of modern clinical decision-making, encompassing electronic health records (EHR), continuous vital sign monitoring, wearable device measurements, and physiological signals. However, these data sources are invariably plagued by missing values—a pervasive challenge that significantly impedes the deployment of machine learning systems in clinical settings. Studies estimate that up to 80% of clinical variables in intensive care units may have missing entries, arising from irregular measurement protocols, sensor failures, patient mobility, or systematic biases in clinical workflows.

Traditional imputation methods, including mean imputation, forward filling, and simple interpolation, produce deterministic point estimates that fail to capture the inherent uncertainty in the imputed values. This limitation becomes critically problematic in healthcare, where incorrect imputations can propagate through downstream predictive models and lead to erroneous clinical recommendations with potentially life-threatening consequences. Furthermore, missing data mechanisms in healthcare are rarely missing completely at random (MCAR); instead, they often follow missing at random (MAR) or missing not at random (MNAR) patterns, where the missingness itself carries clinical information about patient severity or treatment protocols.

Recent advances in diffusion models have demonstrated remarkable success in generative modeling tasks, offering a principled framework for uncertainty quantification through their iterative denoising process. Unlike variational autoencoders or generative adversarial networks, diffusion models provide stable training dynamics and can naturally generate multiple plausible samples, making them ideally suited for probabilistic imputation. However, existing diffusion-based imputation methods (e.g., CSDI, FADTI) predominantly focus on univariate time series or fail to explicitly model different missing data mechanisms. Moreover, they neglect the rich multimodal context available in healthcare settings—clinical notes, demographic information, laboratory results, and medical imaging—that could significantly inform the imputation process.

### 2.2 Research Objectives

This research proposes a novel **Uncertainty-Aware Multimodal Diffusion Imputation (UAMDI)** framework with three primary objectives:

1. **Develop missingness-aware representations** by explicitly modeling different missing data mechanisms (MCAR, MAR, MNAR) through specialized pattern encoders that capture the structural and temporal characteristics of missingness.

2. **Design a multimodal conditional diffusion architecture** that leverages cross-modal attention mechanisms to incorporate complementary data modalities (clinical text, tabular features, and time series) for context-rich, clinically informed imputation.

3. **Generate calibrated uncertainty estimates** that provide interpretable confidence bounds for imputed values, enabling risk-aware decision-making and supporting clinical workflow integration.

### 2.3 Significance

This research addresses a critical gap at the intersection of time series modeling, uncertainty quantification, and healthcare AI deployment. The significance of this work manifests across multiple dimensions:

**Clinical Safety**: By providing calibrated uncertainty estimates, clinicians can identify high-risk imputations and request additional measurements rather than relying on potentially erroneous imputed values, thereby preventing adverse clinical decisions.

**Model Trustworthiness**: Transparent uncertainty quantification enhances the interpretability and trustworthiness of AI systems, addressing a fundamental barrier to clinical adoption identified by regulatory bodies and healthcare professionals.

**Multimodal Integration**: The framework establishes a principled approach for incorporating diverse healthcare data modalities, moving beyond siloed single-modality analyses toward holistic patient representation.

**Methodological Contributions**: The explicit modeling of missing data mechanisms and the integration of these mechanisms into diffusion-based generative models represent novel methodological contributions with implications beyond healthcare to domains like finance, climate science, and industrial monitoring.

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathbf{X} = \{\mathbf{x}_1, \mathbf{x}_2, ..., \mathbf{x}_T\}$ denote a multivariate time series with $T$ timestamps and $D$ dimensions, where $\mathbf{x}_t \in \mathbb{R}^D$. We define a binary mask $\mathbf{M} \in \{0,1\}^{T \times D}$ where $m_{t,d} = 1$ indicates that value $x_{t,d}$ is observed, and $m_{t,d} = 0$ indicates missingness. The observed data is denoted as $\mathbf{X}^{obs} = \mathbf{X} \odot \mathbf{M}$ and missing data as $\mathbf{X}^{mis} = \mathbf{X} \odot (1-\mathbf{M})$, where $\odot$ represents element-wise multiplication.

Additionally, we have access to multimodal context data: clinical text embeddings $\mathbf{C}^{text} \in \mathbb{R}^{d_{text}}$, tabular features $\mathbf{C}^{tab} \in \mathbb{R}^{d_{tab}}$, and potentially other time-aligned modalities. Our objective is to learn a conditional distribution $p(\mathbf{X}^{mis}|\mathbf{X}^{obs}, \mathbf{M}, \mathbf{C})$ that generates multiple plausible imputations with calibrated uncertainty estimates.

### 3.2 Architecture Design

#### 3.2.1 Missingness Pattern Encoder

We design a specialized module to encode the structural characteristics of missingness patterns:

$$\mathbf{h}_m = \text{MPE}(\mathbf{M}, \mathbf{X}^{obs})$$

The Missingness Pattern Encoder (MPE) consists of three parallel pathways:

1. **Temporal Pattern Pathway**: A bidirectional LSTM processes the mask sequence $\mathbf{M}$ to capture temporal dependencies in missingness patterns, identifying systematic gaps versus sporadic missing values.

2. **Statistical Feature Pathway**: Computes hand-crafted features including missing rate per variable, length of consecutive missing intervals, and co-occurrence patterns between variables.

3. **Mechanism Classification Pathway**: A neural network classifier that predicts the likely missing data mechanism (MCAR, MAR, MNAR) for each variable based on observed correlations between missingness patterns and observed values:

$$p(\text{mechanism}|\mathbf{M}, \mathbf{X}^{obs}) = \text{softmax}(W_m [\mathbf{h}_m^{temp}; \mathbf{h}_m^{stat}] + b_m)$$

These pathways are concatenated and projected to produce the missingness representation $\mathbf{h}_m \in \mathbb{R}^{d_m}$.

#### 3.2.2 Multimodal Context Encoder

To leverage complementary information from different modalities, we design a cross-modal fusion module:

$$\mathbf{h}_c = \text{MCE}(\mathbf{C}^{text}, \mathbf{C}^{tab}, \mathbf{X}^{obs})$$

The Multimodal Context Encoder (MCE) employs transformer-based cross-attention:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

where queries are derived from time series embeddings, and keys/values from text and tabular modalities. We apply multi-head attention with $h$ heads:

$$\mathbf{h}_c = \text{Concat}(\text{head}_1, ..., \text{head}_h)W^O$$

This architecture enables the model to selectively attend to relevant contextual information from clinical notes (e.g., mentions of treatment changes) or tabular features (e.g., comorbidities) that inform plausible value ranges for imputation.

#### 3.2.3 Conditional Diffusion Model

Our core imputation model is based on denoising diffusion probabilistic models (DDPMs). The forward diffusion process gradually adds Gaussian noise to the complete data:

$$q(\mathbf{x}_t^{(k)}|\mathbf{x}_t^{(k-1)}) = \mathcal{N}(\mathbf{x}_t^{(k)}; \sqrt{1-\beta_k}\mathbf{x}_t^{(k-1)}, \beta_k \mathbf{I})$$

where $k \in \{1, ..., K\}$ indexes the diffusion steps and $\{\beta_k\}$ is a variance schedule. The reverse process learns to denoise:

$$p_\theta(\mathbf{x}_t^{(k-1)}|\mathbf{x}_t^{(k)}, \mathbf{X}^{obs}, \mathbf{h}_m, \mathbf{h}_c) = \mathcal{N}(\mathbf{x}_t^{(k-1)}; \mu_\theta(\mathbf{x}_t^{(k)}, k, \mathbf{c}), \sigma_k^2 \mathbf{I})$$

where $\mathbf{c} = [\mathbf{X}^{obs}; \mathbf{h}_m; \mathbf{h}_c]$ represents the full conditioning context.

The denoising network $\mu_\theta$ is implemented as a temporal transformer with the following modifications:

1. **Position-aware embeddings** that combine timestamp indices, diffusion step $k$, and missingness indicators
2. **Masked self-attention** that prevents information leakage from missing positions
3. **Conditioning injection** via FiLM (Feature-wise Linear Modulation) layers:

$$\text{FiLM}(\mathbf{h}, \mathbf{c}) = \gamma(\mathbf{c}) \odot \mathbf{h} + \beta(\mathbf{c})$$

### 3.3 Training Objective

Our training loss combines multiple components:

$$\mathcal{L} = \mathcal{L}_{denoise} + \lambda_1 \mathcal{L}_{recon} + \lambda_2 \mathcal{L}_{calib} + \lambda_3 \mathcal{L}_{mech}$$

**Denoising Loss**: Standard diffusion objective that minimizes the prediction error of added noise:

$$\mathcal{L}_{denoise} = \mathbb{E}_{k, \epsilon, \mathbf{X}} \left[\|\epsilon - \epsilon_\theta(\mathbf{x}^{(k)}, k, \mathbf{c})\|^2\right]$$

**Reconstruction Loss**: On observed values to ensure consistency:

$$\mathcal{L}_{recon} = \|\mathbf{M} \odot (\hat{\mathbf{X}}^{(0)} - \mathbf{X}^{obs})\|^2$$

**Calibration Loss**: Encourages well-calibrated uncertainty estimates using a proper scoring rule:

$$\mathcal{L}_{calib} = \mathbb{E}_{\mathbf{X}_{val}} \left[\sum_{i=1}^N (\mathbb{I}[\mathbf{X}_{val} \in \text{CI}_i] - \alpha_i)^2\right]$$

where $\text{CI}_i$ are prediction intervals at confidence level $\alpha_i$.

**Mechanism Loss**: Auxiliary loss for missing mechanism classification:

$$\mathcal{L}_{mech} = -\sum_{i} y_i^{mech} \log p(\text{mechanism}_i|\mathbf{M}, \mathbf{X}^{obs})$$

### 3.4 Inference and Uncertainty Quantification

At inference, we generate $S$ imputation samples through the reverse diffusion process:

$$\mathbf{X}^{(s)} \sim p_\theta(\mathbf{X}^{mis}|\mathbf{X}^{obs}, \mathbf{M}, \mathbf{C}), \quad s=1,...,S$$

For each missing value $x_{t,d}^{mis}$, we compute:

1. **Point estimate**: $\hat{x}_{t,d} = \frac{1}{S}\sum_{s=1}^S x_{t,d}^{(s)}$
2. **Epistemic uncertainty**: $\sigma_{epis}^2 = \frac{1}{S}\sum_{s=1}^S (x_{t,d}^{(s)} - \hat{x}_{t,d})^2$
3. **Prediction intervals**: 95% CI = $[\text{Percentile}_{2.5}\{x_{t,d}^{(s)}\}, \text{Percentile}_{97.5}\{x_{t,d}^{(s)}\}]$

### 3.5 Data Collection

**Primary Dataset**: MIMIC-IV (Medical Information Mart for Intensive Care) will serve as our primary evaluation dataset, providing:
- Vital signs time series (heart rate, blood pressure, SpO2) sampled irregularly
- Laboratory measurements with systematic missingness
- Clinical notes and discharge summaries
- Structured EHR data (demographics, diagnoses, medications)

**Secondary Dataset**: We will utilize the eICU Collaborative Research Database to assess generalization across healthcare systems.

**Wearable Dataset**: The WESAD (Wearable Stress and Affect Detection) dataset will evaluate performance on high-frequency consumer wearable data.

**Data Preprocessing**:
1. Temporal alignment of multimodal data to common time grids
2. Text embedding using BioClinicalBERT for clinical notes
3. Normalization of continuous variables using robust scaling
4. Synthetic missingness injection under controlled mechanisms for evaluation

### 3.6 Experimental Design

#### 3.6.1 Baselines

We compare against state-of-the-art methods:
- **Traditional**: MICE, KNN imputation, forward filling
- **Deep Learning**: BRITS, GRU-D, M-RNN
- **Diffusion-based**: CSDI, FADTI, STDiff
- **Gaussian Processes**: MAGIC

#### 3.6.2 Evaluation Protocol

**Imputation Quality Metrics**:
- Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) on held-out missing values
- Normalized RMSE (NRMSE) for scale-invariant comparison
- Distributional metrics: Wasserstein distance between true and imputed distributions

**Uncertainty Calibration Metrics**:
- Expected Calibration Error (ECE)
- Prediction Interval Coverage Probability (PICP) at multiple confidence levels
- Negative Log-Likelihood (NLL) as a proper scoring rule

**Downstream Task Performance**:
- **Mortality prediction**: AUROC, AUPRC
- **Sepsis early warning**: AUROC, sensitivity at fixed specificity
- **Length-of-stay prediction**: MAE, R²

We evaluate robustness by:
1. Varying missingness rates (20%, 40%, 60%, 80%)
2. Testing under different missing mechanisms (MCAR, MAR, MNAR)
3. Cross-hospital generalization (train on MIMIC-IV, test on eICU)

#### 3.6.3 Ablation Studies

To validate our design choices:
1. **Missingness encoder ablation**: Remove MPE to assess impact on mechanism-aware learning
2. **Multimodal ablation**: Evaluate with only time series vs. full multimodal context
3. **Uncertainty components**: Compare aleatoric vs. epistemic uncertainty contributions
4. **Conditioning strategies**: Cross-attention vs. concatenation vs. adaptive fusion

#### 3.6.4 Implementation Details

- **Framework**: PyTorch with Hugging Face Transformers for text encoding
- **Architecture**: 8-layer transformer with 8 attention heads, hidden dimension 256
- **Diffusion**: 1000 diffusion steps with cosine variance schedule
- **Training**: AdamW optimizer, learning rate 1e-4, batch size 32, 100 epochs
- **Hardware**: 4× NVIDIA A100 GPUs (40GB)
- **Inference**: 50 imputation samples per instance for uncertainty quantification

### 3.7 Clinical Deployment Considerations

To facilitate clinical translation, we will:
1. Develop a **risk-stratification module** that flags high-uncertainty imputations for clinician review
2. Create **interpretable visualizations** showing imputation confidence over time
3. Implement **computationally efficient inference** via distillation to enable real-time deployment
4. Conduct **fairness audits** across demographic subgroups to ensure equitable performance

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Methodological Advances**:
1. A novel diffusion-based architecture that explicitly models missing data mechanisms, expected to improve imputation accuracy by 15-25% over baselines, particularly under MNAR scenarios where existing methods struggle.
2. A principled multimodal fusion framework demonstrating that incorporating clinical text and tabular features reduces imputation error by 10-20% compared to unimodal approaches.
3. Well-calibrated uncertainty estimates with Expected Calibration Error < 0.05, enabling reliable confidence bounds for clinical decision-making.

**Empirical Findings**:
1. Comprehensive benchmarking on three diverse healthcare datasets (MIMIC-IV, eICU, WESAD) establishing new state-of-the-art performance across multiple imputation quality and calibration metrics.
2. Demonstration that uncertainty-aware imputation improves downstream task robustness: we expect 5-10% improvement in AUROC for mortality prediction when using uncertainty-weighted samples versus point estimates.
3. Identification of clinically meaningful patterns in missingness mechanisms across different patient populations and clinical contexts.

**Practical Deliverables**:
1. Open-source implementation of the UAMDI framework with pre-trained models on MIMIC-IV
2. Clinical decision support visualization toolkit for displaying imputation uncertainty to healthcare providers
3. Comprehensive ablation study results providing guidance for practitioners on architecture design choices

### 4.2 Scientific Impact

This research advances multiple scientific frontiers:

**Time Series Modeling**: Establishes diffusion models as a principled approach for probabilistic imputation with explicit missingness mechanism modeling, extending beyond current methods that treat all missing data uniformly.

**Uncertainty Quantification**: Contributes novel calibration techniques for generative models in high-stakes domains, with implications for AI safety research.

**Multimodal Learning**: Demonstrates effective cross-modal attention mechanisms for integrating structured (time series, tabular) and unstructured (text) healthcare data, informing future foundation model development.

**Healthcare AI**: Addresses critical deployment barriers by providing transparent, interpretable uncertainty estimates that align with clinical workflows and regulatory requirements.

### 4.3 Clinical Impact

The translational potential of this work is substantial:

**Patient Safety**: By identifying unreliable imputations, the framework prevents propagation of errors through clinical decision pipelines, potentially reducing adverse events associated with incorrect data.

**Clinical Workflow Integration**: Uncertainty visualization tools enable clinicians to make informed decisions about when to trust imputed values versus ordering additional tests, optimizing resource allocation.

**Health Equity**: Explicit fairness audits and subgroup analysis ensure that imputation quality remains consistent across demographic groups, preventing algorithmic bias from exacerbating health disparities.

**Regulatory Pathway**: Well-calibrated uncertainty estimates facilitate regulatory approval by providing transparent risk assessment, aligning with FDA guidance on AI/ML-based medical devices.

### 4.4 Broader Impact

Beyond immediate healthcare applications, this research has broader implications:

**Cross-Domain Applicability**: The proposed techniques generalize to any domain with multimodal time series and missing data, including climate science (sensor networks), finance (irregular trading data), and industrial IoT (equipment monitoring).

**Foundation Model Development**: The multimodal conditioning framework provides architectural insights for developing time series foundation models that integrate diverse data types, a key challenge identified in the workshop's call for papers.

**Responsible AI**: By prioritizing uncertainty quantification and calibration, this work exemplifies responsible AI development principles, contributing to the broader discourse on trustworthy machine learning systems.

**Educational Resource**: The open-source release will serve as an educational resource for researchers entering the field, lowering barriers to conducting research on healthcare time series.

### 4.5 Limitations and Future Directions

We acknowledge several limitations that suggest future research directions:

1. **Computational Cost**: Diffusion models require iterative sampling, increasing inference latency. Future work will explore distillation techniques and consistency models for faster inference.

2. **Data Requirements**: Deep generative models require substantial training data. We will investigate few-shot and meta-learning approaches for data-scarce clinical scenarios.

3. **Causal Inference**: While we model missingness mechanisms, explicitly incorporating causal graphs could further improve imputation under MNAR. Integration with causal discovery methods represents a promising direction.

4. **Temporal Distribution Shift**: Healthcare data distributions evolve over time (e.g., new treatments, changing demographics). Developing continual learning strategies for maintaining model performance represents critical future work.

5. **Multimodal Scalability**: As the number of modalities increases (adding imaging, genomics), more sophisticated fusion architectures may be needed. Graph neural networks for modality relationships could be explored.

In conclusion, this research proposes a comprehensive framework addressing critical gaps in healthcare time series imputation, with strong potential for both scientific contribution and clinical translation. By providing uncertainty-aware, multimodal imputation with explicit missingness mechanism modeling, we aim to advance the field toward safer, more trustworthy AI systems for clinical deployment.