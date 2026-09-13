# Research Proposal: Counterfactual Explanation Generation for Medical Foundation Models via Multimodal Perturbation Learning

## 1. Introduction

### Background

The rapid advancement of Medical Foundation Models (MFMs) has demonstrated unprecedented capabilities in clinical decision support, ranging from diagnostic imaging interpretation to comprehensive patient prognosis. These large-scale models, trained on vast repositories of medical data, exhibit remarkable performance in tasks such as disease classification, treatment recommendation, and surgical planning. However, their deployment in real-world clinical settings remains hindered by a fundamental challenge: the "black-box" nature of these models undermines physician trust and poses significant risks to patient safety.

Healthcare represents a domain where explainability is not merely desirable but essential. Clinicians must understand the reasoning behind AI-generated recommendations to integrate them responsibly into their decision-making workflows. Current explanation methods, including gradient-based saliency maps, attention visualization, and feature attribution techniques, provide insights into *what* input features the model focuses on. However, they fundamentally fail to address the more clinically relevant questions: *why* did the model arrive at a specific diagnosis, and *what changes* in the patient's presentation would alter this conclusion?

Counterfactual explanations offer a compelling solution to this interpretability gap. By identifying the minimal modifications to input data that would change a model's prediction, counterfactuals align naturally with clinical reasoning processes. Physicians routinely engage in counterfactual thinking—"If the lesion were smaller, would it still indicate malignancy?" or "If the patient's lab values normalized, would the prognosis improve?" This cognitive alignment makes counterfactual explanations particularly valuable for bridging the gap between AI systems and human medical experts.

### Research Objectives

This research proposes **MedCF** (Medical Counterfactual Framework), a comprehensive framework for generating multimodal counterfactual explanations for Medical Foundation Models. The primary objectives are:

1. **Develop a unified counterfactual generation architecture** that operates across heterogeneous medical data modalities, including radiology images, clinical notes, and structured electronic health record (EHR) data.

2. **Ensure clinical plausibility** of generated counterfactuals by integrating medical knowledge graphs and anatomical constraints into the perturbation learning process.

3. **Optimize for actionability** by introducing a minimal change objective that identifies the smallest clinically meaningful modifications sufficient to alter model predictions.

4. **Validate clinical utility** through comprehensive evaluation involving both computational metrics and expert physician assessment.

### Significance

This research addresses critical needs in the deployment of trustworthy AI in healthcare. By providing interpretable, actionable explanations, MedCF will: (1) enhance physician confidence in AI-assisted diagnoses; (2) enable identification of potential model failures and biases before they impact patient care; (3) support clinical education by illustrating decision boundaries in medical reasoning; and (4) facilitate regulatory compliance by providing transparent documentation of AI decision-making processes.

## 2. Methodology

### 2.1 Overall Framework Architecture

MedCF comprises three interconnected components: (1) a Multimodal Latent Space Encoder, (2) a Knowledge-Guided Perturbation Generator, and (3) a Counterfactual Optimization Module. The framework operates on the principle of learning semantically meaningful perturbations in a shared latent representation that respects clinical constraints while minimizing the distance from the original input.

### 2.2 Multimodal Latent Space Encoder

We construct a shared latent space that captures clinically relevant features across modalities. Let $\mathbf{x} = \{x_I, x_T, x_S\}$ denote a multimodal medical sample comprising image data $x_I$, clinical text $x_T$, and structured EHR data $x_S$.

**Image Encoder**: For radiology images, we employ a Vision Transformer (ViT) backbone pretrained on medical imaging datasets:
$$z_I = E_I(x_I) = \text{ViT}(x_I; \theta_I) \in \mathbb{R}^{d}$$

**Text Encoder**: Clinical notes are processed using a biomedical language model (e.g., ClinicalBERT):
$$z_T = E_T(x_T) = \text{ClinicalBERT}(x_T; \theta_T) \in \mathbb{R}^{d}$$

**Structured Data Encoder**: For tabular EHR data, we utilize a transformer-based encoder with feature-specific embeddings:
$$z_S = E_S(x_S) = \text{TabTransformer}(x_S; \theta_S) \in \mathbb{R}^{d}$$

**Fusion Mechanism**: The modality-specific embeddings are projected into a unified latent space using cross-modal attention:
$$z = \text{CrossModalFusion}(z_I, z_T, z_S) = \sum_{m \in \{I,T,S\}} \alpha_m \cdot W_m z_m$$

where attention weights $\alpha_m$ are computed via:
$$\alpha_m = \frac{\exp(q^\top W_q z_m)}{\sum_{m'} \exp(q^\top W_q z_{m'})}$$

### 2.3 Knowledge-Guided Perturbation Generator

To ensure clinical plausibility, we integrate a medical knowledge graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where vertices $\mathcal{V}$ represent medical concepts (diseases, symptoms, anatomical structures) and edges $\mathcal{E}$ encode relationships (causes, manifests, located_in).

**Knowledge Graph Embedding**: We learn embeddings for medical concepts using a graph neural network:
$$h_v = \text{GNN}(v, \mathcal{N}(v); \theta_G)$$

where $\mathcal{N}(v)$ denotes the neighborhood of concept $v$.

**Plausibility Constraint Function**: We define a clinical plausibility score that penalizes perturbations violating medical constraints:
$$\mathcal{P}(\delta) = \sum_{(v_i, v_j) \in \mathcal{E}} \mathbb{1}[\delta \text{ violates } (v_i, v_j)] \cdot w_{ij}$$

where $w_{ij}$ represents the confidence weight of the relationship.

**Conditional Perturbation Generator**: We train a conditional variational autoencoder (CVAE) to generate perturbations conditioned on the target prediction:
$$p(\delta | z, y_{target}) = \mathcal{N}(\mu_\delta(z, y_{target}), \sigma_\delta(z, y_{target}))$$

The generator is trained with the following objective:
$$\mathcal{L}_{gen} = \mathbb{E}_{q(\delta|z,y)}[\log p(y_{target}|z + \delta)] - \beta \cdot D_{KL}(q(\delta|z,y) || p(\delta)) - \lambda \cdot \mathcal{P}(\delta)$$

### 2.4 Counterfactual Optimization Module

The core optimization seeks to find the minimal perturbation $\delta^*$ that changes the model prediction while maintaining clinical validity.

**Objective Function**: Given a target Medical Foundation Model $f$, original prediction $y_{orig} = f(\mathbf{x})$, and target outcome $y_{target}$, we optimize:

$$\delta^* = \arg\min_{\delta} \mathcal{L}_{total}(\delta)$$

where:
$$\mathcal{L}_{total}(\delta) = \mathcal{L}_{pred}(\delta) + \lambda_1 \mathcal{L}_{min}(\delta) + \lambda_2 \mathcal{L}_{plaus}(\delta) + \lambda_3 \mathcal{L}_{recon}(\delta)$$

**Prediction Loss**: Ensures the counterfactual achieves the target prediction:
$$\mathcal{L}_{pred}(\delta) = -\log p(y_{target} | f(D(z + \delta)))$$

where $D$ is the decoder reconstructing multimodal inputs from latent representations.

**Minimal Change Loss**: Encourages sparse, minimal perturbations:
$$\mathcal{L}_{min}(\delta) = ||\delta||_1 + \gamma ||\delta||_2^2$$

**Plausibility Loss**: Enforces clinical validity:
$$\mathcal{L}_{plaus}(\delta) = \mathcal{P}(\delta) + \text{AnatomicalConstraint}(D_I(z_I + \delta_I))$$

**Reconstruction Loss**: Ensures generated counterfactuals remain realistic:
$$\mathcal{L}_{recon}(\delta) = ||D(z + \delta) - \tilde{\mathbf{x}}||_2^2$$

### 2.5 Modality-Specific Decoders

**Image Decoder**: We employ a diffusion-based generator for synthesizing counterfactual medical images:
$$x_I^{cf} = D_I(z_I + \delta_I) = \text{DiffusionDecoder}(z_I + \delta_I; \theta_{D_I})$$

**Text Decoder**: Clinical text counterfactuals are generated using a fine-tuned medical language model:
$$x_T^{cf} = D_T(z_T + \delta_T) = \text{MedicalLM}(z_T + \delta_T; \theta_{D_T})$$

**Structured Data Decoder**: Tabular data is reconstructed with appropriate constraints on valid value ranges:
$$x_S^{cf} = D_S(z_S + \delta_S) = \text{Clip}(\text{MLP}(z_S + \delta_S), \text{valid\_ranges})$$

### 2.6 Experimental Design

**Datasets**: We utilize:
- MIMIC-CXR: 377,110 chest X-rays with associated radiology reports
- MIMIC-IV: Structured EHR data including demographics, lab values, and diagnoses
- CheXpert: 224,316 chest radiographs with uncertainty labels

**Target MFMs**: We evaluate explanations for:
- Med-PaLM 2: Multimodal medical foundation model
- BiomedCLIP: Vision-language model for medical imaging
- Clinical transformer models for EHR prediction

**Evaluation Metrics**:

1. **Validity Rate**: Proportion of counterfactuals that successfully flip the prediction:
$$\text{Validity} = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[f(\mathbf{x}_i^{cf}) = y_{target}]$$

2. **Proximity**: Average distance between original and counterfactual:
$$\text{Proximity} = \frac{1}{N}\sum_{i=1}^N ||\mathbf{x}_i - \mathbf{x}_i^{cf}||_2$$

3. **Sparsity**: Number of features changed:
$$\text{Sparsity} = \frac{1}{N}\sum_{i=1}^N ||\mathbf{x}_i - \mathbf{x}_i^{cf}||_0$$

4. **Clinical Plausibility Score**: Expert physician ratings on a 5-point Likert scale evaluating medical coherence, anatomical validity, and clinical meaningfulness.

5. **Actionability Score**: Physician assessment of whether identified changes correspond to clinically actionable interventions.

**Physician Evaluation Study**: We conduct a study with 20 board-certified radiologists and internal medicine physicians who will evaluate 200 randomly sampled counterfactual explanations across three dimensions: plausibility, usefulness, and alignment with clinical reasoning.

**Bias Detection Experiment**: We assess whether MedCF can identify model biases by generating counterfactuals for demographically diverse patient subgroups and analyzing systematic differences in required perturbations.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Technical Deliverables**: A fully implemented MedCF framework with open-source code, pretrained models, and comprehensive documentation enabling reproduction and extension by the research community.

2. **Performance Benchmarks**: We anticipate achieving validity rates exceeding 85% while maintaining proximity scores within clinically acceptable ranges, outperforming existing counterfactual methods by at least 15% on composite metrics.

3. **Clinical Validation**: Physician evaluation studies are expected to demonstrate significantly higher plausibility and actionability scores compared to baseline explanation methods (saliency maps, attention visualization).

4. **Bias Detection Capabilities**: The framework is expected to reveal previously unidentified biases in MFMs, particularly regarding demographic subgroups and rare presentations.

### Broader Impact

**Clinical Practice**: MedCF will enable clinicians to understand and appropriately calibrate their trust in AI recommendations, supporting more informed clinical decision-making. The actionable nature of counterfactual explanations provides specific guidance on what patient factors most influence diagnoses.

**Regulatory Compliance**: As healthcare AI regulations increasingly mandate explainability (e.g., EU AI Act), MedCF provides a robust technical solution for documenting and auditing AI decision-making processes.

**Model Development**: By revealing decision boundaries and potential failure modes, MedCF will inform the development of more robust and fair medical foundation models.

**Patient Safety**: Enhanced transparency in AI reasoning will reduce the risk of undetected errors propagating through clinical workflows, ultimately improving patient outcomes.

**Educational Applications**: Counterfactual explanations serve as powerful educational tools, helping medical trainees understand the relationships between clinical findings and diagnoses through interactive exploration of "what-if" scenarios.

This research represents a significant step toward trustworthy AI in healthcare, addressing the critical need for interpretable medical foundation models that can be safely and effectively integrated into clinical practice.