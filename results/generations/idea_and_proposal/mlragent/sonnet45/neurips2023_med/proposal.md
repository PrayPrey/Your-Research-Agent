# Uncertainty-Aware Active Learning for Multi-Modal Medical Image Segmentation with Limited Expert Annotations

## 1. Introduction

### Background

Medical imaging has become an indispensable diagnostic tool in modern healthcare, with modalities such as Computed Tomography (CT), Magnetic Resonance Imaging (MRI), and Positron Emission Tomography (PET) providing complementary anatomical and functional information. The accurate segmentation of anatomical structures and pathological regions from these images is crucial for diagnosis, treatment planning, and monitoring disease progression. However, the interpretation and annotation of medical images require extensive expertise and time, creating a significant bottleneck in developing robust AI-assisted diagnostic systems.

Deep learning, particularly convolutional neural networks (CNNs), has demonstrated remarkable success in medical image segmentation tasks. Despite these advances, several critical challenges persist. First, the performance of deep learning models heavily depends on the availability of large annotated datasets, which are expensive and time-consuming to acquire in the medical domain. Expert radiologists may require 30-60 minutes to annotate a single 3D medical image volume, and annotations from multiple experts are often needed to ensure reliability. Second, current approaches often fail to effectively leverage complementary information from multiple imaging modalities, which could significantly improve segmentation accuracy and robustness. Third, most existing deep learning models produce point estimates without quantifying prediction uncertainty, limiting their trustworthiness in critical clinical applications where understanding model confidence is essential for informed decision-making.

Recent literature has highlighted the importance of uncertainty quantification in medical image analysis (Mehta et al., 2022) and the potential of active learning to reduce annotation requirements (Gaillochet et al., 2023; Ma et al., 2024). However, existing approaches have primarily focused on single-modality scenarios and have not fully exploited the synergies between multi-modal data fusion, uncertainty estimation, and active learning strategies.

### Research Objectives

This research proposes a unified framework that addresses these critical challenges through the following objectives:

1. **Develop a multi-modal fusion network** that effectively integrates complementary information from multiple imaging modalities while quantifying both aleatoric (data) and epistemic (model) uncertainties using Bayesian deep learning principles.

2. **Design an uncertainty-guided active learning strategy** that intelligently selects the most informative samples and specific image regions for expert annotation, prioritizing areas where the model exhibits high uncertainty and where modalities show disagreement.

3. **Incorporate cross-modal consistency regularization** to leverage unlabeled multi-modal data through semi-supervised learning, further reducing the annotation burden while maintaining segmentation performance.

4. **Validate the framework** on multiple clinical datasets and segmentation tasks to demonstrate annotation efficiency, segmentation accuracy, and clinical utility.

### Significance

This research addresses the unmet needs in medical imaging AI identified by the Medical Imaging meets NeurIPS workshop. The proposed framework has the potential to:

- **Reduce annotation costs** by 50-70% while maintaining or improving segmentation accuracy, making AI-assisted diagnosis more accessible and scalable
- **Enhance clinical trust** by providing interpretable uncertainty maps that communicate model confidence to clinicians, enabling informed decision-making
- **Improve detection of rare pathologies** by strategically focusing annotation efforts on challenging cases and uncertain regions
- **Advance multi-modal learning** by developing principled methods for fusing complementary imaging information under uncertainty
- **Contribute to the broader ML community** by establishing best practices for uncertainty-aware active learning in multi-modal settings

## 2. Methodology

### 2.1 Overall Framework Architecture

Our proposed framework consists of three main components: (1) a Bayesian multi-modal fusion network for segmentation with uncertainty quantification, (2) an uncertainty-guided active learning module for intelligent sample and region selection, and (3) a cross-modal consistency regularization mechanism for semi-supervised learning.

### 2.2 Bayesian Multi-Modal Fusion Network

#### 2.2.1 Network Architecture

We design a multi-encoder, single-decoder architecture where each imaging modality $m \in \{1, ..., M\}$ has a dedicated encoder $E_m$ to extract modality-specific features, followed by a fusion module $F$ and a shared decoder $D$ for segmentation.

For an input consisting of $M$ modalities $\mathbf{X} = \{\mathbf{X}_1, ..., \mathbf{X}_M\}$, the feature extraction is:

$$\mathbf{z}_m = E_m(\mathbf{X}_m; \theta_m), \quad m = 1, ..., M$$

where $\theta_m$ represents the parameters of encoder $m$. The fusion module combines multi-scale features using an attention-based mechanism:

$$\mathbf{z}_{fused} = F(\mathbf{z}_1, ..., \mathbf{z}_M; \phi) = \sum_{m=1}^{M} \alpha_m \cdot \mathbf{z}_m$$

where attention weights $\alpha_m$ are computed as:

$$\alpha_m = \frac{\exp(\mathbf{w}_m^T \cdot \text{GAP}(\mathbf{z}_m))}{\sum_{k=1}^{M} \exp(\mathbf{w}_k^T \cdot \text{GAP}(\mathbf{z}_k))}$$

with GAP denoting global average pooling and $\mathbf{w}_m$ being learnable weight vectors. The final segmentation is:

$$\mathbf{y} = D(\mathbf{z}_{fused}; \psi)$$

#### 2.2.2 Uncertainty Quantification

We employ Monte Carlo Dropout (MC-Dropout) to approximate Bayesian inference. During both training and inference, dropout layers with rate $p$ are applied after each convolutional block. For $T$ stochastic forward passes:

$$\mathbf{y}^{(t)} = D(F(E_1(\mathbf{X}_1; \hat{\theta}_1^{(t)}), ..., E_M(\mathbf{X}_M; \hat{\theta}_M^{(t)}); \hat{\phi}^{(t)}); \hat{\psi}^{(t)})$$

where $\hat{\theta}_m^{(t)}, \hat{\phi}^{(t)}, \hat{\psi}^{(t)}$ represent dropout-perturbed parameters at iteration $t$.

The predictive mean and variance are:

$$\bar{\mathbf{y}} = \frac{1}{T}\sum_{t=1}^{T} \mathbf{y}^{(t)}$$

$$\sigma^2_{total} = \frac{1}{T}\sum_{t=1}^{T} (\mathbf{y}^{(t)} - \bar{\mathbf{y}})^2$$

We decompose total uncertainty into epistemic (model) and aleatoric (data) components:

$$\sigma^2_{epistemic} = \frac{1}{T}\sum_{t=1}^{T} (\mathbf{y}^{(t)} - \bar{\mathbf{y}})^2$$

$$\sigma^2_{aleatoric} = \frac{1}{T}\sum_{t=1}^{T} \mathbf{y}^{(t)} \odot (1 - \mathbf{y}^{(t)})$$

where $\odot$ denotes element-wise multiplication.

#### 2.2.3 Cross-Modal Disagreement

We quantify cross-modal disagreement by computing individual modality predictions and measuring their variance:

$$\mathbf{y}_m = D(E_m(\mathbf{X}_m; \theta_m); \psi), \quad m = 1, ..., M$$

$$\sigma^2_{disagreement}(i) = \frac{1}{M}\sum_{m=1}^{M} (\mathbf{y}_m(i) - \bar{\mathbf{y}}_{modal}(i))^2$$

where $\bar{\mathbf{y}}_{modal} = \frac{1}{M}\sum_{m=1}^{M} \mathbf{y}_m$ and $i$ indexes pixels/voxels.

### 2.3 Uncertainty-Guided Active Learning Strategy

#### 2.3.1 Acquisition Function

We design a composite acquisition function that combines multiple uncertainty sources to select the most informative samples and regions:

$$\mathcal{A}(\mathbf{X}) = \lambda_1 \mathcal{U}_{epistemic}(\mathbf{X}) + \lambda_2 \mathcal{U}_{disagreement}(\mathbf{X}) + \lambda_3 \mathcal{D}_{diversity}(\mathbf{X})$$

where:

$$\mathcal{U}_{epistemic}(\mathbf{X}) = \frac{1}{N}\sum_{i=1}^{N} \sigma^2_{epistemic}(i)$$

$$\mathcal{U}_{disagreement}(\mathbf{X}) = \frac{1}{N}\sum_{i=1}^{N} \sigma^2_{disagreement}(i)$$

$$\mathcal{D}_{diversity}(\mathbf{X}) = \min_{\mathbf{X}' \in \mathcal{L}} \|\mathbf{z}_{fused}(\mathbf{X}) - \mathbf{z}_{fused}(\mathbf{X}')\|_2$$

where $N$ is the number of pixels/voxels, $\mathcal{L}$ is the labeled set, and $\lambda_1, \lambda_2, \lambda_3$ are weighting coefficients.

#### 2.3.2 Region-Based Annotation Selection

Instead of requesting full image annotations, we implement region-based selection by identifying uncertain regions using spatial clustering:

1. Compute pixel-wise uncertainty map: $\mathbf{U}(i) = \sigma^2_{epistemic}(i) + \sigma^2_{disagreement}(i)$
2. Apply threshold $\tau$ to obtain high-uncertainty regions: $\mathcal{R} = \{i | \mathbf{U}(i) > \tau\}$
3. Apply morphological operations and connected component analysis to extract contiguous regions
4. Select top-$K$ regions based on size and average uncertainty

This region-based approach significantly reduces annotation time by focusing expert attention on critical areas.

#### 2.3.3 Active Learning Algorithm

**Algorithm: Uncertainty-Aware Active Learning**

```
Input: Unlabeled multi-modal dataset U, initial labeled set L, 
       budget B, region selection threshold τ
Output: Trained model with reduced annotation requirements

1. Initialize model parameters θ, φ, ψ randomly
2. Train initial model on L using supervised loss
3. for b = 1 to B do:
4.    for each X in U do:
5.       Compute acquisition score A(X)
6.       Compute uncertainty maps U(X)
7.    end for
8.    Select sample X* = argmax A(X)
9.    Extract high-uncertainty regions R from X*
10.   Request expert annotations for regions R
11.   Add (X*, annotations) to L, remove X* from U
12.   Update model using combined supervised and 
       semi-supervised loss
13. end for
14. Return final model
```

### 2.4 Cross-Modal Consistency Regularization

To leverage unlabeled data, we introduce a consistency regularization loss that encourages agreement between predictions from different modality combinations:

$$\mathcal{L}_{consistency} = \frac{1}{|\mathcal{U}|} \sum_{\mathbf{X} \in \mathcal{U}} \sum_{m=1}^{M} \|\mathbf{y}_m - \text{sg}(\bar{\mathbf{y}})\|^2$$

where $\mathcal{U}$ is the unlabeled set, sg(·) denotes stop-gradient operation, and $\bar{\mathbf{y}}$ is the prediction from the full multi-modal fusion network.

### 2.5 Training Objective

The complete training objective combines supervised segmentation loss, consistency regularization, and uncertainty calibration:

$$\mathcal{L}_{total} = \mathcal{L}_{seg} + \beta \mathcal{L}_{consistency} + \gamma \mathcal{L}_{calibration}$$

where:

$$\mathcal{L}_{seg} = -\frac{1}{|\mathcal{L}|N} \sum_{(\mathbf{X}, \mathbf{Y}) \in \mathcal{L}} \sum_{i=1}^{N} \sum_{c=1}^{C} Y_i^c \log(\bar{y}_i^c)$$

$$\mathcal{L}_{calibration} = \text{ECE}(\bar{\mathbf{y}}, \sigma^2_{epistemic})$$

where ECE is the Expected Calibration Error ensuring uncertainty estimates are well-calibrated.

### 2.6 Data Collection and Experimental Design

#### 2.6.1 Datasets

We will validate our framework on three multi-modal medical imaging datasets:

1. **BraTS (Brain Tumor Segmentation)**: Multi-parametric MRI including T1, T1-contrast, T2, and FLAIR sequences for brain tumor segmentation
2. **Prostate segmentation dataset**: T2-weighted MRI and apparent diffusion coefficient (ADC) maps
3. **Cardiac segmentation dataset**: Cine-MRI and late gadolinium enhancement (LGE) sequences

#### 2.6.2 Baseline Methods

We compare against:
- Standard supervised learning with full annotations
- Random sampling active learning
- Entropy-based active learning (single modality)
- TAAL (Gaillochet et al., 2023)
- Selective uncertainty-based AL (Ma et al., 2024)
- Standard multi-modal fusion without uncertainty

#### 2.6.3 Evaluation Metrics

**Segmentation Performance:**
- Dice Similarity Coefficient (DSC)
- Hausdorff Distance (HD95)
- Average Surface Distance (ASD)

**Annotation Efficiency:**
- Annotation time reduction (%)
- Number of samples required to reach target DSC
- Region-based vs. full image annotation comparison

**Uncertainty Calibration:**
- Expected Calibration Error (ECE)
- Negative Log-Likelihood (NLL)
- Area Under Uncertainty-Error Curve (AU-UEC)

**Clinical Utility:**
- Detection rate of rare pathologies
- False positive rate in high-confidence regions
- Agreement with expert uncertainty assessment

#### 2.6.4 Implementation Details

- **Architecture**: U-Net backbone with ResNet-50 encoders
- **Optimization**: Adam optimizer, learning rate 1e-4 with cosine annealing
- **MC-Dropout**: T=20 forward passes, dropout rate p=0.5
- **Active learning**: Budget B=100 iterations, 5 samples per iteration
- **Hyperparameters**: $\lambda_1=0.4, \lambda_2=0.3, \lambda_3=0.3, \beta=0.1, \gamma=0.05$
- **Data augmentation**: Random rotation, scaling, elastic deformation, intensity variation

#### 2.6.5 Experimental Protocol

1. **Initialization**: Randomly select 5% of training data for initial labeled set
2. **Active learning cycles**: Run 20 cycles, each selecting 5 samples/regions
3. **Cross-validation**: 5-fold cross-validation for each dataset
4. **Statistical testing**: Paired t-tests with Bonferroni correction for multiple comparisons
5. **Ablation studies**: Evaluate contribution of each component (fusion, uncertainty types, consistency loss)

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Annotation Efficiency**: We anticipate achieving 50-70% reduction in annotation requirements compared to standard supervised learning while maintaining comparable or superior segmentation accuracy. Specifically, we expect to reach 85% DSC with approximately 30-40% of full annotations, compared to baseline methods requiring 60-80% of annotations for similar performance.

**Segmentation Accuracy**: The multi-modal fusion with uncertainty-aware learning is expected to improve segmentation accuracy by 5-8% DSC over single-modality approaches and 2-4% over standard multi-modal fusion without active learning, particularly in challenging cases with ambiguous boundaries or rare pathologies.

**Uncertainty Calibration**: We expect to achieve well-calibrated uncertainty estimates with ECE < 0.05, significantly outperforming standard deep learning approaches (typical ECE > 0.15). This will enable reliable confidence assessment for clinical decision-making.

**Rare Pathology Detection**: The uncertainty-guided approach is expected to improve detection of rare pathological patterns by 15-25% compared to random sampling, as the active learning strategy specifically targets unusual and challenging cases.

**Computational Efficiency**: Region-based annotation selection is expected to reduce annotation time by 40-60% compared to full-image annotation, as experts focus only on uncertain regions rather than entire volumes.

### 3.2 Scientific Impact

**Advancement of Bayesian Deep Learning**: This research will contribute novel methods for uncertainty decomposition in multi-modal settings, advancing the theoretical understanding of uncertainty quantification in complex neural architectures.

**Active Learning Theory**: The proposed acquisition function combining multiple uncertainty sources and cross-modal disagreement will provide new insights into optimal sample selection strategies for multi-modal data.

**Semi-Supervised Learning**: The cross-modal consistency regularization framework will establish new approaches for leveraging unlabeled multi-modal medical data, potentially applicable to other multi-view learning scenarios.

**Reproducibility and Open Science**: We will release open-source implementations, trained models, and comprehensive documentation to facilitate reproducibility and accelerate research in this domain.

### 3.3 Clinical Impact

**Reduced Annotation Burden**: By dramatically reducing annotation requirements, our framework will make AI-assisted diagnosis more accessible to healthcare institutions with limited resources, potentially democratizing access to advanced diagnostic tools.

**Enhanced Clinical Trust**: Interpretable uncertainty maps will enable clinicians to identify cases requiring additional scrutiny, improving diagnostic confidence and reducing the risk of missed diagnoses.

**Improved Patient Outcomes**: More accurate segmentation, particularly for rare pathologies, can lead to earlier detection and more precise treatment planning, potentially improving patient survival and quality of life.

**Workflow Integration**: The uncertainty-aware framework provides a natural mechanism for human-AI collaboration, where the AI system identifies challenging cases requiring expert attention, optimizing the use of limited expert time.

**Scalability**: The reduced annotation requirements will enable rapid deployment of segmentation models for new anatomical structures or pathologies, accelerating clinical validation and adoption.

### 3.4 Broader Impact

**Other Medical Imaging Tasks**: While focused on segmentation, the uncertainty-aware active learning framework can be extended to other medical imaging tasks such as classification, detection, and registration.

**Beyond Medical Imaging**: The proposed methods are applicable to other domains requiring expensive annotations and multi-view data, including autonomous driving (multi-sensor fusion), remote sensing (multi-spectral imaging), and industrial quality control.

**Educational Value**: The framework can serve as a teaching tool for understanding uncertainty quantification, active learning, and multi-modal fusion, contributing to the training of future AI researchers and practitioners.

**Ethical Considerations**: By quantifying and communicating uncertainty, our approach promotes responsible AI deployment in healthcare, addressing concerns about overconfidence in AI predictions and supporting informed consent and shared decision-making.

This research addresses critical challenges identified by the medical imaging community and has the potential to significantly advance both the science of machine learning and the practice of AI-assisted medical diagnosis, ultimately contributing to improved patient care and more efficient healthcare delivery.