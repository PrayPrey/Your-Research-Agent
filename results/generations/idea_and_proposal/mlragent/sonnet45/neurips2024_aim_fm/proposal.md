# Research Proposal: Counterfactual Visual Explanations for Medical Foundation Models

## 1. Title

**Anatomically-Constrained Counterfactual Explanation Framework for Medical Foundation Models: Enhancing Clinical Interpretability through Diffusion-Based Visual Reasoning**

## 2. Introduction

### 2.1 Background

Medical Foundation Models (MFMs) have demonstrated remarkable capabilities in diagnostic tasks, ranging from radiology interpretation to pathology analysis. These large-scale models, often pre-trained on extensive medical imaging datasets, can achieve expert-level performance in identifying diseases, abnormalities, and clinical patterns. However, their deployment in clinical settings faces a critical barrier: the "black-box" nature of these models fundamentally conflicts with the transparency and accountability requirements of medical decision-making.

Clinical decision-making is inherently interpretable and evidence-based. When a radiologist diagnoses a malignant lesion, they articulate specific visual features—irregular borders, heterogeneous texture, spiculated margins—that inform their judgment. Moreover, clinical reasoning often involves counterfactual thinking: "If this lesion were more uniform in texture, it would likely be benign" or "Had the nodule been smaller, further monitoring might suffice." This natural mode of reasoning is absent in current MFM explanation approaches.

Existing explainability methods for MFMs primarily rely on attention mechanisms, saliency maps, or gradient-based attribution techniques. While these methods highlight regions of importance, they suffer from several limitations: (1) they lack actionability—identifying an important region doesn't explain what changes would alter the diagnosis; (2) they often reveal spurious correlations rather than causal relationships; (3) they don't align with the counterfactual reasoning patterns familiar to clinicians; and (4) they provide limited insights for model debugging and improvement.

### 2.2 Research Objectives

This research proposes a novel counterfactual explanation framework specifically designed for MFMs that generates clinically plausible visual modifications to medical images, revealing the decision boundaries and reasoning processes of these models. The primary objectives are:

1. **Develop a constraint-aware counterfactual generation system** that leverages diffusion models to produce anatomically plausible medical image modifications while minimizing changes to clinically relevant features.

2. **Create a hierarchical feature attribution mechanism** that maps low-level pixel changes in counterfactual images to high-level clinical concepts, bridging the semantic gap between model representations and medical terminology.

3. **Establish a rigorous clinical validation pipeline** involving radiologists and clinicians to evaluate the clinical relevance, plausibility, and actionability of generated counterfactual explanations.

4. **Demonstrate improved model debugging capabilities** by using counterfactual explanations to identify spurious correlations, dataset biases, and failure modes in existing MFMs.

### 2.3 Significance

This research addresses critical gaps at the intersection of explainable AI and medical decision support:

**Clinical Trust and Adoption**: By providing explanations that align with clinical reasoning patterns, this framework can accelerate the adoption of MFMs in real-world healthcare settings, potentially improving diagnostic accuracy and efficiency.

**Patient Safety**: Counterfactual explanations expose decision boundaries, helping identify cases where models might fail or rely on spurious features, thereby enhancing patient safety through better understanding of model limitations.

**Educational Value**: The framework can serve as an educational tool for medical trainees, illustrating how subtle visual changes impact diagnoses and reinforcing pattern recognition skills.

**Regulatory Compliance**: As healthcare AI faces increasing regulatory scrutiny, interpretable counterfactual explanations can facilitate compliance with transparency requirements in medical AI deployment.

**Model Improvement**: By revealing failure modes and spurious correlations, counterfactual analysis provides actionable insights for improving MFM architectures and training procedures.

## 3. Methodology

### 3.1 Overall Framework Architecture

The proposed framework consists of four integrated components: (1) Anatomically-Constrained Counterfactual Generator, (2) Hierarchical Clinical Feature Attributor, (3) Plausibility Verification Module, and (4) Clinical Validation Pipeline. Figure 1 (conceptual) illustrates the overall architecture.

### 3.2 Anatomically-Constrained Counterfactual Generator

#### 3.2.1 Diffusion Model Foundation

We employ a conditional latent diffusion model (LDM) as the generative backbone. Given an input medical image $\mathbf{x}_0 \in \mathbb{R}^{H \times W \times C}$ and the MFM's prediction $y_{\text{orig}}$, our goal is to generate a counterfactual image $\mathbf{x}_{cf}$ that: (1) yields a different prediction $y_{cf} \neq y_{\text{orig}}$, (2) minimizes perceptual distance from the original, and (3) maintains anatomical plausibility.

The diffusion process is formulated in the latent space of a pre-trained medical image autoencoder $\mathcal{E}$:

$$\mathbf{z}_0 = \mathcal{E}(\mathbf{x}_0)$$

The forward diffusion process adds Gaussian noise over $T$ timesteps:

$$q(\mathbf{z}_t | \mathbf{z}_{t-1}) = \mathcal{N}(\mathbf{z}_t; \sqrt{1-\beta_t}\mathbf{z}_{t-1}, \beta_t\mathbf{I})$$

The reverse process is modeled by a neural network $\epsilon_\theta$ that predicts the noise:

$$p_\theta(\mathbf{z}_{t-1}|\mathbf{z}_t, \mathbf{c}) = \mathcal{N}(\mathbf{z}_{t-1}; \mu_\theta(\mathbf{z}_t, t, \mathbf{c}), \Sigma_\theta(\mathbf{z}_t, t))$$

where $\mathbf{c}$ represents conditioning information.

#### 3.2.2 Counterfactual Optimization Objective

To generate meaningful counterfactuals, we optimize a multi-objective loss function:

$$\mathcal{L}_{total} = \lambda_1\mathcal{L}_{prediction} + \lambda_2\mathcal{L}_{proximity} + \lambda_3\mathcal{L}_{anatomy} + \lambda_4\mathcal{L}_{sparsity}$$

**Prediction Loss** ensures the counterfactual achieves the target prediction:
$$\mathcal{L}_{prediction} = -\log P_{MFM}(y_{target}|\mathbf{x}_{cf})$$

**Proximity Loss** minimizes perceptual distance using LPIPS (Learned Perceptual Image Patch Similarity):
$$\mathcal{L}_{proximity} = \text{LPIPS}(\mathbf{x}_0, \mathbf{x}_{cf}) + \alpha||\mathbf{x}_0 - \mathbf{x}_{cf}||_2^2$$

**Anatomical Plausibility Loss** leverages a pre-trained anatomy segmentation network $\mathcal{S}$ to ensure structural consistency:
$$\mathcal{L}_{anatomy} = ||\mathcal{S}(\mathbf{x}_0) - \mathcal{S}(\mathbf{x}_{cf})||_2^2 + \mathcal{L}_{freq}$$

where $\mathcal{L}_{freq}$ is a frequency-domain constraint ensuring realistic texture:
$$\mathcal{L}_{freq} = ||\mathcal{F}(\mathbf{x}_0) - \mathcal{F}(\mathbf{x}_{cf})||_1$$

with $\mathcal{F}$ denoting the Fourier transform.

**Sparsity Loss** encourages minimal modifications:
$$\mathcal{L}_{sparsity} = ||\mathbf{m} \odot (\mathbf{x}_0 - \mathbf{x}_{cf})||_1$$

where $\mathbf{m}$ is a learned binary mask highlighting modification regions.

#### 3.2.3 Guided Diffusion Sampling

We implement classifier-free guidance for controlled generation:

$$\tilde{\epsilon}_\theta(\mathbf{z}_t, t, \mathbf{c}) = \epsilon_\theta(\mathbf{z}_t, t, \emptyset) + s \cdot (\epsilon_\theta(\mathbf{z}_t, t, \mathbf{c}) - \epsilon_\theta(\mathbf{z}_t, t, \emptyset))$$

where $s$ is the guidance scale and $\mathbf{c}$ includes: (1) target diagnosis, (2) anatomical region preservation masks, and (3) clinical feature constraints.

### 3.3 Hierarchical Clinical Feature Attribution

#### 3.3.1 Multi-Level Feature Extraction

We establish a three-tier attribution hierarchy:

**Tier 1: Pixel-level changes** - Direct difference map:
$$\Delta\mathbf{x} = \mathbf{x}_{cf} - \mathbf{x}_0$$

**Tier 2: Semantic regions** - Map changes to anatomical structures using segmentation:
$$R_i = \int_{\Omega_i} |\Delta\mathbf{x}| \, d\Omega$$

where $\Omega_i$ represents the $i$-th anatomical region.

**Tier 3: Clinical concepts** - Project changes onto a clinical feature vocabulary $\mathcal{V} = \{v_1, ..., v_K\}$ (e.g., "lesion border irregularity", "tissue density", "calcification pattern"):

$$a_k = \text{sim}(\phi(\Delta\mathbf{x}), \psi(v_k))$$

where $\phi$ is a medical vision encoder and $\psi$ is a text encoder from a medical vision-language model (e.g., BiomedCLIP).

#### 3.3.2 Concept Activation Mapping

We compute concept-specific attribution scores using TCAV (Testing with Concept Activation Vectors):

$$S_{CAV}(c, k) = \nabla_{h^l}P_{MFM}(c|\mathbf{x}) \cdot v_k^l$$

where $h^l$ is the activation at layer $l$, $c$ is the class, and $v_k^l$ is the concept activation vector for clinical concept $k$.

### 3.4 Plausibility Verification Module

#### 3.4.1 Anatomical Consistency Checking

We employ multiple verification mechanisms:

1. **Segmentation Consistency**: Verify organ boundaries remain intact:
$$\text{IoU}(\mathcal{S}(\mathbf{x}_0), \mathcal{S}(\mathbf{x}_{cf})) > \tau_{seg}$$

2. **Physical Constraints**: Check Hounsfield unit ranges for CT, signal intensity distributions for MRI

3. **Texture Realism**: Use a pre-trained medical image discriminator $\mathcal{D}$:
$$\mathcal{D}(\mathbf{x}_{cf}) > \tau_{real}$$

#### 3.4.2 Clinical Feature Plausibility

Validate that modified features align with medical knowledge using a medical knowledge graph $\mathcal{G}$:

$$\text{Plausible}(v_i, v_j) = \exists \text{ path}(\mathcal{G}, v_i, v_j) \land \text{distance}(\mathcal{G}, v_i, v_j) \leq d_{max}$$

### 3.5 Data Collection and Experimental Design

#### 3.5.1 Datasets

**Primary Datasets**:
- **Chest X-ray**: MIMIC-CXR (227,835 studies), CheXpert (224,316 studies)
- **Breast Imaging**: CBIS-DDSM (10,239 studies), VinDr-Mammo (20,000 studies)
- **Brain MRI**: BraTS (2,000+ studies), RSNA-MICCAI Brain Tumor (2,000 studies)
- **Dermatology**: HAM10000 (10,015 images), ISIC Archive (50,000+ images)

**Auxiliary Datasets** for anatomy segmentation and knowledge graph construction:
- RadGraph for clinical knowledge extraction
- SNOMED CT for medical ontology

#### 3.5.2 MFM Baselines

We evaluate counterfactual explanations for:
1. **Vision-only MFMs**: BiomedCLIP, Med-PaLM M (vision component)
2. **Task-specific models**: CheXNet (chest X-ray), DeepDerm (dermatology)
3. **Foundation models**: SAM-Med, MedSAM

#### 3.5.3 Experimental Protocol

**Phase 1: Model Training** (Months 1-6)
- Train diffusion model on each medical imaging modality
- Fine-tune on specific anatomical regions (chest, breast, brain, skin)
- Develop anatomical segmentation networks
- Construct clinical feature vocabulary and knowledge graph

**Phase 2: Counterfactual Generation** (Months 7-12)
- Generate counterfactuals for 1,000 test cases per dataset
- Vary target predictions (binary flips, multi-class transitions)
- Generate multiple counterfactuals per image with different sparsity levels

**Phase 3: Computational Evaluation** (Months 10-15)
- Quantitative metrics assessment
- Ablation studies
- Comparison with baseline explanation methods

**Phase 4: Clinical Validation** (Months 13-18)
- Radiologist evaluation study (n=10 radiologists, 200 cases each)
- Structured questionnaires and Likert scales
- Inter-rater reliability analysis

### 3.6 Evaluation Metrics

#### 3.6.1 Quantitative Metrics

**Validity**: Proportion of counterfactuals achieving target prediction:
$$\text{Validity} = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[P_{MFM}(y_{target}|\mathbf{x}_{cf}^{(i)}) > P_{MFM}(y_{orig}|\mathbf{x}_{cf}^{(i)})]$$

**Proximity**: Average perceptual distance:
$$\text{Proximity} = \frac{1}{N}\sum_{i=1}^N \text{LPIPS}(\mathbf{x}_0^{(i)}, \mathbf{x}_{cf}^{(i)})$$

**Sparsity**: Percentage of modified pixels:
$$\text{Sparsity} = \frac{1}{N}\sum_{i=1}^N \frac{||\mathbf{x}_0^{(i)} - \mathbf{x}_{cf}^{(i)}||_0}{H \times W}$$

**Anatomical Preservation**:
$$\text{AP} = \frac{1}{N}\sum_{i=1}^N \text{IoU}(\mathcal{S}(\mathbf{x}_0^{(i)}), \mathcal{S}(\mathbf{x}_{cf}^{(i)}))$$

**Feature Consistency**: Alignment between modified features and clinical concepts:
$$\text{FC} = \frac{1}{N}\sum_{i=1}^N \max_k a_k^{(i)}$$

#### 3.6.2 Clinical Evaluation Metrics

Radiologists rate each counterfactual on 5-point Likert scales:

1. **Anatomical Plausibility**: Could this image represent a real patient?
2. **Clinical Relevance**: Do the modifications correspond to diagnostically relevant features?
3. **Actionability**: Does this explanation provide useful insights for clinical decision-making?
4. **Educational Value**: Would this be useful for teaching medical students?
5. **Trust Impact**: Does this increase your trust in the MFM's decision?

We compute inter-rater agreement using Krippendorff's alpha and Fleiss' kappa.

#### 3.6.3 Comparative Baselines

We compare against:
- **Attention-based**: GradCAM, Attention Rollout
- **Perturbation-based**: LIME, SHAP
- **Counterfactual**: DiCE, COIN (medical-specific)
- **Concept-based**: TCAV, ACE

### 3.7 Model Debugging Applications

We systematically investigate:

**Spurious Correlation Detection**: Generate counterfactuals that flip predictions by modifying background regions or imaging artifacts, revealing when models rely on non-anatomical features.

**Robustness Testing**: Create adversarial counterfactuals at decision boundaries to identify vulnerable cases.

**Bias Identification**: Analyze whether counterfactual modifications required differ across demographic groups, revealing potential fairness issues.

## 4. Expected Outcomes & Impact

### 4.1 Expected Technical Outcomes

1. **High-Quality Counterfactual Generation**: We expect to achieve >90% validity (successful prediction flips) while maintaining anatomical plausibility scores >4.0/5.0 from radiologist evaluations and proximity (LPIPS) <0.15.

2. **Clinically Grounded Attribution**: The hierarchical feature attribution mechanism should successfully map >80% of pixel-level changes to recognized clinical concepts with concept activation scores >0.7.

3. **Superior Explanation Quality**: Compared to attention-based methods, our counterfactual explanations are expected to score significantly higher (p<0.01) on actionability and clinical relevance metrics in radiologist evaluations.

4. **Effective Model Debugging**: We anticipate identifying spurious correlations in at least 15-20% of test cases, with concrete examples of MFMs relying on imaging artifacts, text annotations, or irrelevant anatomical regions.

### 4.2 Scientific Contributions

**Methodological Innovation**: This research introduces the first comprehensive counterfactual explanation framework specifically designed for medical foundation models, integrating anatomical constraints, hierarchical attribution, and clinical validation in a unified pipeline.

**Theoretical Advancement**: By bridging pixel-level image modifications with high-level clinical concepts through hierarchical attribution, this work advances our understanding of how to make complex AI models interpretable in domain-specific contexts requiring expert knowledge.

**Benchmarking Resource**: The clinical evaluation protocol, annotated counterfactual datasets, and evaluation metrics will serve as benchmarks for future research in medical AI explainability.

### 4.3 Clinical Impact

**Enhanced Clinician Trust**: By providing explanations aligned with clinical reasoning patterns, this framework can significantly improve clinician trust in MFMs, potentially accelerating adoption in diagnostic workflows. Preliminary surveys suggest that counterfactual explanations resonate more strongly with clinical users than attention maps.

**Improved Diagnostic Safety**: The ability to visualize decision boundaries helps identify cases where MFMs might be uncertain or relying on inappropriate features, enabling clinicians to exercise appropriate caution and override incorrect AI suggestions.

**Educational Applications**: Medical schools and residency programs can use generated counterfactuals as teaching tools, illustrating how subtle feature variations impact diagnoses and strengthening pattern recognition skills.

**Regulatory Facilitation**: Transparent, interpretable counterfactual explanations can support regulatory submissions for medical AI systems by demonstrating that models make decisions based on clinically appropriate features.

### 4.4 Broader Impact on Medical AI

**Model Development Insights**: By revealing failure modes and spurious correlations, counterfactual analysis provides actionable feedback for improving MFM architectures, training procedures, and dataset curation.

**Fairness and Bias Mitigation**: Systematic analysis of counterfactuals across demographic groups can reveal biases in MFM decision-making, guiding development of more equitable medical AI systems.

**Framework Generalizability**: While demonstrated on imaging tasks, the core methodology—constraint-aware generation, hierarchical attribution, domain-expert validation—is applicable to other medical modalities (EHR data, genomics) and other high-stakes domains (autonomous vehicles, financial systems).

**Interdisciplinary Collaboration**: This research exemplifies productive collaboration between AI researchers and medical professionals, establishing methodological templates for co-designing AI systems that meet both technical excellence and clinical utility requirements.

### 4.5 Long-term Vision

This research represents a foundational step toward truly interpretable medical AI. Future extensions include:
- **Interactive counterfactual exploration**: Enabling clinicians to specify desired feature modifications and observe prediction changes in real-time
- **Personalized explanations**: Adapting counterfactual complexity to user expertise levels
- **Causal counterfactuals**: Extending beyond associative patterns to causal relationships
- **Multi-modal counterfactuals**: Generating synchronized counterfactual modifications across imaging, clinical notes, and lab results

Ultimately, this framework aims to transform MFMs from opaque prediction systems into transparent decision-support partners, fostering a future where AI augments rather than replaces human expertise in healthcare.

**Total Word Count**: ~2,950 words