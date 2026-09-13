# Research Proposal: Diffusion Models with Clinical Constraint Learning for Trustworthy Pediatric Medical Image Synthesis

## 1. Title

**Clinically-Constrained Diffusion Models with Age-Adaptive Priors for Trustworthy Synthetic Pediatric Medical Imaging**

## 2. Introduction

### 2.1 Background

Pediatric healthcare represents one of the most underserved domains in medical artificial intelligence, facing a critical intersection of challenges that severely limit the development and deployment of AI-assisted diagnostic tools. The scarcity of pediatric medical imaging data stems from multiple factors: stringent privacy regulations protecting minors (COPPA, GDPR-K), smaller patient populations compared to adult medicine, ethical constraints on pediatric research participation, and the inherent risks of repeated imaging procedures involving ionizing radiation in developing bodies. This data scarcity creates a paradoxical situation where the populations most vulnerable and in need of precise diagnostic support are least represented in AI training datasets.

Recent advances in deep generative models, particularly denoising diffusion probabilistic models (DDPMs), have demonstrated remarkable capabilities in generating high-fidelity synthetic images across various domains. Diffusion models have shown superior performance compared to GANs and VAEs in terms of sample quality, training stability, and mode coverage. In medical imaging, works such as MedLoRD and seg2med have demonstrated that diffusion models can generate anatomically plausible medical images conditioned on segmentation masks. However, these approaches lack explicit mechanisms to encode and enforce clinical domain knowledge, particularly the age-dependent anatomical variations critical in pediatric imaging.

The unique challenge in pediatric medical imaging lies in the dynamic nature of anatomical development. Unlike adult anatomy, which remains relatively stable, pediatric anatomy undergoes systematic, age-dependent changes in organ sizes, proportions, tissue densities, and spatial relationships. For instance, the brain-to-body ratio, ventricular sizes, fontanelle closure patterns, bone ossification centers, and organ proportions all follow well-documented developmental trajectories. Current generative models fail to incorporate these constraints, potentially producing anatomically implausible images that undermine clinical trust and limit their utility for data augmentation.

### 2.2 Research Objectives

This research proposes a novel framework that integrates clinical domain knowledge directly into the diffusion process through constraint learning mechanisms. Our primary objectives are:

1. **Develop a constraint-aware diffusion architecture** that incorporates age-conditioned anatomical priors derived from pediatric growth atlases and developmental charts, ensuring generated images respect age-specific anatomical proportions and developmental stages.

2. **Design differentiable clinical validity constraints** that encode domain knowledge (organ size ratios, tissue density ranges, spatial relationships) as soft constraints within the reverse diffusion process, guiding generation toward clinically valid configurations.

3. **Establish interpretable validation metrics** based on clinician-defined anatomical landmarks and pathology-specific features, enabling quantitative assessment of clinical realism and providing transparency for clinical adoption.

4. **Validate the framework** through comprehensive evaluation including radiologist assessment, downstream task performance (diagnostic classification, segmentation), and comparison with existing synthetic data generation approaches.

### 2.3 Significance

This research addresses multiple critical gaps identified in the workshop's call for submissions:

**Clinical Trustworthiness**: By explicitly encoding clinical constraints, our approach provides interpretable guarantees about the validity of synthetic images, addressing the primary barrier to clinical adoption of generative models.

**Underserved Populations**: Focusing on pediatric imaging directly targets one of the workshop's highlighted minority data groups, potentially enabling AI development for rare pediatric conditions.

**Actionable Research**: The proposed validation framework with clinician-in-the-loop evaluation ensures that outputs are immediately relevant to clinical practice rather than purely methodological contributions.

**Methodological Innovation**: Combining diffusion models with learned constraint embeddings represents a novel approach to incorporating domain knowledge in generative models, with potential applications beyond pediatrics to other specialized medical domains.

## 3. Methodology

### 3.1 Data Collection and Preprocessing

**Dataset Acquisition**: We will utilize multiple pediatric imaging datasets:
- Pediatric Brain MRI from the National Institutes of Health (NIH) Pediatric MRI Data Repository
- Chest X-rays from the Pediatric Chest X-ray dataset
- CT scans from collaborating pediatric hospitals (subject to IRB approval)

Each dataset will include age metadata (ranging from neonates to 18 years) and associated anatomical annotations. Age groups will be stratified into: neonates (0-1 month), infants (1-12 months), toddlers (1-3 years), preschool (3-6 years), school-age (6-12 years), and adolescents (12-18 years).

**Preprocessing Pipeline**:
1. Image normalization to standard intensity ranges
2. Registration to age-appropriate anatomical atlases
3. Extraction of anatomical landmarks using automated segmentation models validated by radiologists
4. Computation of anatomical measurements (organ volumes, ratios, spatial coordinates)

**Clinical Knowledge Base Construction**: We will construct a structured knowledge base encoding:
- Age-specific anatomical measurements from pediatric growth charts
- Normal ranges for organ size ratios (e.g., brain-to-body ratio, ventricular indices)
- Tissue density distributions for different age groups
- Spatial relationship constraints between anatomical structures

### 3.2 Constraint-Aware Diffusion Model Architecture

#### 3.2.1 Foundation: Denoising Diffusion Probabilistic Model

Our framework builds upon the DDPM formulation. The forward diffusion process gradually adds Gaussian noise to real images $\mathbf{x}_0$ over $T$ timesteps:

$$q(\mathbf{x}_t | \mathbf{x}_{t-1}) = \mathcal{N}(\mathbf{x}_t; \sqrt{1-\beta_t}\mathbf{x}_{t-1}, \beta_t\mathbf{I})$$

where $\beta_t$ is a variance schedule. The reverse process learns to denoise:

$$p_\theta(\mathbf{x}_{t-1}|\mathbf{x}_t) = \mathcal{N}(\mathbf{x}_{t-1}; \mu_\theta(\mathbf{x}_t, t), \Sigma_\theta(\mathbf{x}_t, t))$$

#### 3.2.2 Age-Conditioned Anatomy Priors

We introduce an age-conditioning mechanism that modulates the denoising process based on pediatric developmental stage. Let $a$ denote the patient age. We encode age information through a learnable embedding:

$$\mathbf{e}_a = \text{MLP}_{\text{age}}([a, a^2, \sin(2\pi a/18), \cos(2\pi a/18)])$$

This embedding incorporates both linear and periodic components to capture non-linear growth patterns. The age embedding is integrated into the U-Net denoising network through:

$$\epsilon_\theta(\mathbf{x}_t, t, a, \mathbf{c}) = \text{U-Net}(\mathbf{x}_t, t, \mathbf{e}_a, \mathbf{e}_c)$$

where $\mathbf{c}$ represents additional conditioning (e.g., anatomical masks), and $\mathbf{e}_c$ is its embedding.

**Developmental Atlas Integration**: We extract age-specific anatomical priors from pediatric atlases. For each age group, we compute statistical anatomical maps encoding expected spatial distributions of anatomical structures. These are encoded as spatial attention maps $\mathbf{A}_a(\mathbf{x})$ that modulate intermediate U-Net features:

$$\mathbf{h}'_l = \mathbf{h}_l \odot (1 + \alpha \cdot \mathbf{A}_a)$$

where $\mathbf{h}_l$ is the feature map at layer $l$, and $\alpha$ is a learnable scaling parameter.

#### 3.2.3 Clinical Validity Constraints

We encode clinical constraints as differentiable functions that can guide the generation process. Let $\mathcal{C} = \{c_1, c_2, ..., c_K\}$ represent a set of clinical constraints. Each constraint $c_k$ is formulated as:

$$c_k(\mathbf{x}, a) = \|\mathcal{M}_k(\mathbf{x}) - \mathcal{R}_k(a)\|^2$$

where $\mathcal{M}_k$ extracts a measurable anatomical feature (e.g., organ volume ratio), and $\mathcal{R}_k(a)$ returns the age-appropriate reference range.

**Specific Constraints**:

1. **Organ Volume Ratios**: For brain MRI, we enforce brain-to-intracranial volume ratios:
$$c_{\text{brain}}(\mathbf{x}, a) = \left(\frac{V_{\text{brain}}(\mathbf{x})}{V_{\text{ICV}}(\mathbf{x})} - r_{\text{brain}}(a)\right)^2$$

2. **Tissue Density Constraints**: For CT imaging, we constrain Hounsfield unit distributions:
$$c_{\text{density}}(\mathbf{x}, a) = \sum_{t \in \text{tissues}} D_{KL}(p_t(\mathbf{x}) \| p_t^{\text{ref}}(a))$$

3. **Spatial Relationship Constraints**: We enforce expected spatial configurations:
$$c_{\text{spatial}}(\mathbf{x}, a) = \sum_{i,j} \|\mathbf{d}_{ij}(\mathbf{x}) - \mathbf{d}_{ij}^{\text{ref}}(a)\|^2$$

where $\mathbf{d}_{ij}$ represents the distance vector between landmarks $i$ and $j$.

**Constraint-Guided Sampling**: We integrate constraints into the reverse diffusion process using classifier-free guidance extended with constraint gradients:

$$\tilde{\epsilon}_\theta = \epsilon_\theta(\mathbf{x}_t, t, \emptyset) + s \cdot (\epsilon_\theta(\mathbf{x}_t, t, a, \mathbf{c}) - \epsilon_\theta(\mathbf{x}_t, t, \emptyset)) - \lambda \nabla_{\mathbf{x}_t} \sum_{k=1}^K w_k c_k(\hat{\mathbf{x}}_0, a)$$

where $\hat{\mathbf{x}}_0$ is the predicted clean image, $s$ is the guidance scale, $\lambda$ controls constraint strength, and $w_k$ are constraint weights. The constraint gradient encourages the denoising process toward clinically valid configurations.

#### 3.2.4 Learned Constraint Embeddings

Rather than hand-designing all constraints, we learn constraint representations from data through a constraint encoder network:

$$\mathbf{z}_c = \text{ConstraintEncoder}(\mathbf{x}, a, \{\mathcal{M}_k(\mathbf{x})\}_{k=1}^K)$$

This embedding captures high-level clinical validity features and is injected into the denoising network through cross-attention mechanisms:

$$\text{Attention}(\mathbf{Q}, \mathbf{K}_c, \mathbf{V}_c) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}_c^T}{\sqrt{d}}\right)\mathbf{V}_c$$

where $\mathbf{K}_c, \mathbf{V}_c$ are derived from $\mathbf{z}_c$.

### 3.3 Training Procedure

**Loss Function**: The total training objective combines the standard DDPM loss with constraint regularization:

$$\mathcal{L} = \mathbb{E}_{t, \mathbf{x}_0, \epsilon}\left[\|\epsilon - \epsilon_\theta(\mathbf{x}_t, t, a, \mathbf{c})\|^2\right] + \beta \sum_{k=1}^K w_k c_k(\mathbf{x}_0, a) + \gamma \mathcal{L}_{\text{perceptual}}$$

where $\mathcal{L}_{\text{perceptual}}$ is a perceptual loss computed using features from a pretrained medical image encoder to encourage anatomical realism.

**Training Strategy**:
1. **Phase 1 (Warm-up)**: Train base diffusion model without constraints for 100K iterations
2. **Phase 2 (Constraint Introduction)**: Gradually introduce constraint losses with increasing weights over 50K iterations
3. **Phase 3 (Fine-tuning)**: Joint optimization of all components for 100K iterations

**Implementation Details**:
- Architecture: U-Net with attention layers, 128M parameters
- Optimizer: AdamW with learning rate 1e-4, cosine annealing
- Batch size: 16 per GPU, distributed training across 8 V100 GPUs
- Noise schedule: Cosine schedule with $T=1000$ steps
- Training time: Approximately 5 days for 250K iterations

### 3.4 Interpretable Validation Framework

We develop a multi-faceted validation approach combining automated metrics with clinician evaluation.

#### 3.4.1 Automated Metrics

**Anatomical Landmark Accuracy**: We compute the deviation of automatically detected landmarks from age-appropriate norms:

$$\text{ALA}(a) = \frac{1}{L}\sum_{l=1}^L \frac{\|\mathbf{p}_l - \mathbf{p}_l^{\text{ref}}(a)\|}{\sigma_l(a)}$$

where $L$ is the number of landmarks, $\mathbf{p}_l$ is the detected position, and $\sigma_l(a)$ is the age-specific standard deviation.

**Clinical Constraint Satisfaction Rate**: Percentage of generated images satisfying predefined clinical constraints:

$$\text{CCSR} = \frac{1}{K}\sum_{k=1}^K \mathbb{1}[c_k(\mathbf{x}, a) < \tau_k]$$

**Age Prediction Consistency**: Train an age regression model on real images and evaluate whether synthetic images yield consistent age predictions:

$$\text{APC} = 1 - \frac{|\text{Age}_{\text{predicted}} - \text{Age}_{\text{conditioned}}|}{\text{Age}_{\text{conditioned}}}$$

**Fréchet Radiological Distance (FRD)**: Adapt FID using features from a radiological vision transformer pretrained on diverse medical imaging tasks.

#### 3.4.2 Clinician-in-the-Loop Evaluation

We design a structured evaluation protocol involving board-certified pediatric radiologists:

1. **Realism Assessment**: Radiologists rate synthetic images on a 5-point Likert scale for overall realism, anatomical correctness, and age-appropriateness
2. **Turing Test**: Mixed batches of real and synthetic images; radiologists classify each as real or synthetic
3. **Diagnostic Utility**: Radiologists assess whether synthetic images could be used for training purposes
4. **Constraint Violation Detection**: Radiologists identify any anatomical abnormalities or developmental inconsistencies

**Inter-rater Reliability**: Compute Fleiss' kappa to ensure consistency across multiple radiologist evaluators.

### 3.5 Downstream Task Validation

To demonstrate practical utility, we evaluate synthetic data augmentation on downstream diagnostic tasks:

**Experimental Design**:
- **Tasks**: Pediatric brain tumor classification, ventricular segmentation, developmental anomaly detection
- **Baseline**: Models trained only on limited real data
- **Augmented**: Models trained on real data + synthetic data from our method
- **Comparisons**: Synthetic data from standard diffusion models, GANs, and traditional augmentation

**Evaluation Metrics**:
- Classification: Accuracy, AUC-ROC, F1-score
- Segmentation: Dice coefficient, Hausdorff distance
- Statistical significance testing using paired t-tests with Bonferroni correction

**Sample Size**: For each downstream task, we simulate low-data regimes with 50, 100, and 200 real training images, augmented with 500 synthetic images.

### 3.6 Ablation Studies

We conduct systematic ablation studies to assess the contribution of each component:

1. **Baseline Diffusion**: Standard DDPM without constraints
2. **+ Age Conditioning**: Adding age embeddings only
3. **+ Age Priors**: Adding developmental atlas attention
4. **+ Hard Constraints**: Adding explicit constraint gradients
5. **+ Learned Constraints**: Full model with constraint encoder
6. **Constraint Weight Sensitivity**: Varying $\lambda$ from 0.1 to 10.0

## 4. Expected Outcomes & Impact

### 4.1 Expected Technical Outcomes

**High-Quality Synthetic Pediatric Images**: We expect to generate synthetic pediatric medical images that are:
- Indistinguishable from real images in radiologist Turing tests (>40% misclassification rate)
- Anatomically consistent with age-specific developmental norms (CCSR >90%)
- Clinically rated as appropriate for training purposes (mean Likert score >4.0)

**Improved Downstream Performance**: Synthetic data augmentation should yield:
- 10-15% improvement in diagnostic classification accuracy in low-data regimes
- 5-8 percentage point increase in segmentation Dice scores
- More robust models with better generalization to unseen age groups

**Interpretable Quality Metrics**: Establishment of quantitative metrics correlating with clinician assessments (correlation coefficient >0.7), providing objective quality assurance for synthetic data.

**Computational Efficiency**: Despite added constraint mechanisms, inference time should remain practical (<5 minutes per 3D volume on standard clinical hardware).

### 4.2 Clinical and Societal Impact

**Addressing Pediatric Data Scarcity**: This framework directly tackles one of the most pressing challenges in pediatric AI development, potentially enabling:
- Development of diagnostic AI tools for rare pediatric conditions with extremely limited real data
- More inclusive AI systems that perform equitably across different pediatric age groups
- Reduced need for repeated imaging procedures in pediatric populations

**Building Clinical Trust**: By providing interpretable validation and explicit constraint satisfaction, our approach addresses the primary barrier to clinical adoption of synthetic medical data. The transparency offered by our constraint-based framework allows clinicians to understand and verify the quality of synthetic data, fostering trust in AI-augmented training pipelines.

**Broader Applicability**: While focused on pediatrics, our constraint learning methodology is generalizable to other specialized medical domains facing similar challenges:
- Rare diseases with limited patient populations
- Longitudinal studies requiring temporal consistency
- Multi-site studies requiring anatomical standardization
- Other vulnerable populations (pregnancy imaging, elderly care)

**Ethical Considerations**: Our approach offers significant ethical advantages:
- Reduces the need for data sharing that might compromise pediatric patient privacy
- Enables research on pediatric conditions without requiring additional patient recruitment
- Supports development of AI tools for underserved pediatric populations in resource-limited settings

### 4.3 Contributions to the Field

**Methodological Innovation**: Introduction of differentiable clinical constraint learning as a principled approach to incorporating domain knowledge in diffusion models, potentially influencing future work in domain-constrained generation.

**Validation Framework**: Establishment of comprehensive, clinician-grounded validation protocols for medical image synthesis, addressing a critical gap in current generative modeling research.

**Open-Source Release**: We commit to releasing code, pretrained models, and validation protocols to facilitate reproducibility and enable the research community to build upon our work.

**Clinical Collaboration Model**: Demonstration of effective collaboration between machine learning researchers and clinician domain experts, providing a template for future interdisciplinary medical AI research.

### 4.4 Limitations and Future Work

**Acknowledged Limitations**:
- Constraint design requires significant domain expertise and may not capture all clinical nuances
- Computational overhead of constraint evaluation during sampling
- Generalization to imaging modalities and anatomical regions not seen during training

**Future Directions**:
- Extension to 4D imaging capturing developmental trajectories over time
- Integration with federated learning for privacy-preserving multi-institutional model training
- Development of interactive tools allowing clinicians to specify custom constraints for specific use cases
- Investigation of constraint learning from natural language descriptions of clinical requirements

**Long-term Vision**: This work represents a step toward "clinically-aware" generative models that seamlessly integrate medical domain knowledge, potentially transforming how AI systems are developed for healthcare applications. By establishing trust through interpretability and constraint satisfaction, we aim to accelerate the responsible adoption of generative AI in clinical practice, ultimately improving diagnostic capabilities and patient outcomes in underserved pediatric populations.

---

**Word Count**: Approximately 4,200 words (extended format to ensure comprehensive coverage of all technical details and evaluation protocols)