# Research Proposal: Geometry-Aware Modular Diffusion Priors for Cross-Modality Medical Imaging Inverse Problems

## 1. Introduction

### 1.1 Background

Inverse problems constitute a fundamental challenge across scientific and engineering disciplines, where the goal is to recover an unknown signal or image from indirect, often corrupted measurements. In medical imaging, inverse problems arise naturally: reconstructing anatomical structures from sparse MRI k-space samples, recovering tissue density from limited-angle CT projections, or denoising X-ray images acquired under low-dose protocols. The mathematical formulation typically follows $\mathbf{y} = \mathcal{A}(\mathbf{x}) + \boldsymbol{\eta}$, where $\mathbf{y}$ represents measurements, $\mathcal{A}$ is the forward operator encoding acquisition physics, $\mathbf{x}$ is the unknown image, and $\boldsymbol{\eta}$ denotes noise.

Recent advances in deep learning have revolutionized approaches to inverse problems. Diffusion models, in particular, have emerged as powerful learned priors capable of modeling complex high-dimensional data distributions. These models learn to reverse a gradual noising process, effectively capturing the score function $\nabla_{\mathbf{x}} \log p(\mathbf{x})$ that guides reconstruction toward plausible solutions. State-of-the-art methods such as score-based diffusion models have demonstrated remarkable success in MRI reconstruction, CT imaging, and computational photography.

However, a critical limitation persists: current diffusion-based solutions require extensive modality-specific training data. A diffusion model trained for MRI reconstruction cannot be directly applied to CT or X-ray problems without complete retraining. This constraint is particularly problematic in clinical settings where acquiring large annotated datasets for every imaging modality and acquisition protocol is prohibitively expensive and time-consuming. Furthermore, emerging imaging technologies and specialized clinical applications often lack sufficient training data to leverage modern deep learning approaches effectively.

### 1.2 Research Gap and Motivation

Despite the apparent differences in physical acquisition mechanisms across medical imaging modalities, fundamental geometric regularities are shared: anatomical structures exhibit consistent edges, boundaries between tissues follow predictable patterns, and smoothness priors apply universally. An MRI scan and a CT scan of the same patient reveal the same underlying anatomy, albeit with different contrast mechanisms and noise characteristics. This observation motivates a central question: can we design diffusion priors that explicitly capture these shared geometric structures, enabling efficient transfer across modalities?

Current approaches treat each modality independently, training separate models that redundantly learn similar geometric priors while specializing for modality-specific characteristics. This paradigm ignores the potential for knowledge sharing and results in inefficient use of available data. Recent work on adapter-based transfer learning (e.g., LoRA) and geometric manifold learning (e.g., MARBLE) suggests that decomposing representations into shared and task-specific components can dramatically improve transfer efficiency in other domains.

### 1.3 Research Objectives

This research proposes **Geometry-Aware Modular Diffusion Priors (GAMDP)**, a novel framework that decomposes diffusion models into a universal geometry-aware encoder and lightweight modality-specific adapters. Our specific objectives are:

1. **Design a geometry-preserving latent space** trained on multi-modal medical imaging data (MRI, CT, X-ray) that captures modality-invariant structural features while remaining agnostic to modality-specific characteristics.

2. **Develop a universal diffusion prior** operating in this geometric latent space that learns structural regularities applicable across imaging modalities.

3. **Implement efficient cross-modality transfer** using LoRA-style adapters comprising less than 5% of total model parameters, enabling adaptation to new modalities with limited training data.

4. **Validate the framework** through comprehensive experiments demonstrating that GAMDP achieves reconstruction quality within 1dB PSNR of modality-specific baselines while requiring ≤50% of target modality training data.

### 1.4 Significance

Success in this research would significantly reduce data requirements for deploying diffusion-based reconstruction in data-limited clinical settings. This has immediate practical implications for rare imaging protocols, pediatric imaging (where data collection is ethically constrained), and emerging imaging technologies. Furthermore, the proposed framework advances theoretical understanding of how geometric priors transfer across domains, contributing to the broader machine learning community's understanding of representation learning and domain adaptation.

## 2. Methodology

### 2.1 Problem Formulation

Consider a medical imaging inverse problem where we observe measurements $\mathbf{y} \in \mathbb{R}^m$ related to the unknown image $\mathbf{x} \in \mathbb{R}^n$ through:

$$\mathbf{y} = \mathcal{A}_\omega(\mathbf{x}) + \boldsymbol{\eta}_\omega$$

where $\omega \in \Omega = \{\text{MRI}, \text{CT}, \text{X-ray}, \ldots\}$ indexes the imaging modality, $\mathcal{A}_\omega$ is the modality-specific forward operator, and $\boldsymbol{\eta}_\omega$ represents modality-specific noise. Our goal is to learn a reconstruction framework that transfers efficiently across modalities.

### 2.2 Architecture Design

The GAMDP framework consists of three components:

**Component 1: Geometry-Aware Encoder $\mathcal{E}_\theta$**

The encoder maps images from any modality to a shared geometric latent space:

$$\mathbf{z} = \mathcal{E}_\theta(\mathbf{x}), \quad \mathbf{z} \in \mathbb{R}^{h \times w \times c}$$

where $c \in \{4, 8, 16\}$ is the latent channel dimension. The encoder architecture follows a convolutional design with residual blocks, trained with geometry-preserving losses detailed in Section 2.3.

**Component 2: Universal Latent Diffusion Model $\mathcal{D}_\phi$**

A diffusion model operates in the geometric latent space, learning the score function:

$$\mathbf{s}_\phi(\mathbf{z}_t, t) \approx \nabla_{\mathbf{z}_t} \log p_t(\mathbf{z}_t)$$

where $\mathbf{z}_t$ is the noised latent at diffusion timestep $t$. The diffusion process follows:

$$d\mathbf{z}_t = -\frac{1}{2}\beta(t)\mathbf{z}_t \, dt + \sqrt{\beta(t)} \, d\mathbf{w}_t$$

with $\beta(t)$ as the noise schedule and $\mathbf{w}_t$ as standard Brownian motion.

**Component 3: Modality-Specific LoRA Adapters $\mathcal{L}_\psi^\omega$**

For each target modality $\omega$, lightweight adapters modify the diffusion model's behavior:

$$\mathbf{W}'_l = \mathbf{W}_l + \mathbf{B}_l^\omega \mathbf{A}_l^\omega$$

where $\mathbf{W}_l$ is the frozen weight matrix at layer $l$, and $\mathbf{B}_l^\omega \in \mathbb{R}^{d \times r}$, $\mathbf{A}_l^\omega \in \mathbb{R}^{r \times k}$ are low-rank adapter matrices with rank $r \in \{4, 8, 16\}$. The adapter parameters $\psi^\omega = \{\mathbf{A}_l^\omega, \mathbf{B}_l^\omega\}_{l=1}^L$ constitute less than 5% of total model parameters.

### 2.3 Training Procedure

**Stage 1: Multi-Modal Geometry-Aware Encoder Training**

The encoder is trained on pooled data from multiple modalities $\mathcal{D}_{\text{multi}} = \bigcup_{\omega \in \Omega_{\text{train}}} \mathcal{D}_\omega$ with the following loss:

$$\mathcal{L}_{\text{encoder}} = \mathcal{L}_{\text{recon}} + \lambda_{\text{edge}}\mathcal{L}_{\text{edge}} + \lambda_{\text{smooth}}\mathcal{L}_{\text{smooth}} + \lambda_{\text{align}}\mathcal{L}_{\text{align}}$$

where:

- **Reconstruction loss:** $\mathcal{L}_{\text{recon}} = \mathbb{E}_{\mathbf{x}}[\|\mathbf{x} - \mathcal{G}_\xi(\mathcal{E}_\theta(\mathbf{x}))\|_2^2]$ with decoder $\mathcal{G}_\xi$

- **Edge preservation loss:** $\mathcal{L}_{\text{edge}} = \mathbb{E}_{\mathbf{x}}[\|\nabla \mathbf{x} - \nabla \mathcal{G}_\xi(\mathcal{E}_\theta(\mathbf{x}))\|_1]$ using Sobel gradients

- **Smoothness regularization:** $\mathcal{L}_{\text{smooth}} = \mathbb{E}_{\mathbf{z}}[\|\nabla \mathbf{z}\|_2^2]$ encouraging smooth latent representations

- **Cross-modal alignment loss:** $\mathcal{L}_{\text{align}} = \mathbb{E}_{(\mathbf{x}_i, \mathbf{x}_j) \sim \mathcal{P}_{\text{paired}}}[\|\mathcal{E}_\theta(\mathbf{x}_i) - \mathcal{E}_\theta(\mathbf{x}_j)\|_2^2]$ for paired multi-modal images when available

**Stage 2: Universal Diffusion Prior Training**

With the encoder frozen, the diffusion model is trained on latent representations:

$$\mathcal{L}_{\text{diffusion}} = \mathbb{E}_{t, \mathbf{z}_0, \boldsymbol{\epsilon}}\left[\|\boldsymbol{\epsilon} - \boldsymbol{\epsilon}_\phi(\mathbf{z}_t, t)\|_2^2\right]$$

where $\mathbf{z}_0 = \mathcal{E}_\theta(\mathbf{x})$, $\mathbf{z}_t = \sqrt{\bar{\alpha}_t}\mathbf{z}_0 + \sqrt{1-\bar{\alpha}_t}\boldsymbol{\epsilon}$, and $\boldsymbol{\epsilon} \sim \mathcal{N}(\mathbf{0}, \mathbf{I})$.

**Stage 3: Modality-Specific Adapter Training**

For a new target modality $\omega_{\text{target}}$, only adapter parameters are trained:

$$\mathcal{L}_{\text{adapter}} = \mathbb{E}_{t, \mathbf{z}_0, \boldsymbol{\epsilon}}\left[\|\boldsymbol{\epsilon} - \boldsymbol{\epsilon}_{\phi, \psi^{\omega_{\text{target}}}}(\mathbf{z}_t, t)\|_2^2\right]$$

where $\boldsymbol{\epsilon}_{\phi, \psi^{\omega}}$ denotes the diffusion model with frozen base parameters $\phi$ and trainable adapters $\psi^\omega$.

### 2.4 Inference for Inverse Problems

Given measurements $\mathbf{y}$ from modality $\omega$, reconstruction proceeds via posterior sampling:

$$p(\mathbf{x}|\mathbf{y}) \propto p(\mathbf{y}|\mathbf{x})p(\mathbf{x})$$

We employ diffusion posterior sampling (DPS) in the latent space:

$$\mathbf{z}_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(\mathbf{z}_t - \frac{1-\alpha_t}{\sqrt{1-\bar{\alpha}_t}}\boldsymbol{\epsilon}_{\phi, \psi^\omega}(\mathbf{z}_t, t)\right) + \sigma_t \mathbf{w} - \zeta_t \nabla_{\mathbf{z}_t}\|\mathbf{y} - \mathcal{A}_\omega(\mathcal{G}_\xi(\hat{\mathbf{z}}_0))\|_2^2$$

where $\hat{\mathbf{z}}_0$ is the predicted clean latent and $\zeta_t$ is a step-size schedule.

### 2.5 Data Collection and Preprocessing

**Datasets:**
- **MRI:** FastMRI knee and brain datasets (~10,000 volumes)
- **CT:** LIDC-IDRI lung CT dataset (~1,000 scans)
- **X-ray:** CheXpert chest X-ray dataset (~200,000 images)
- **Paired data:** A subset of patients with both CT and X-ray available for alignment loss

**Preprocessing:**
- Resize all images to 256×256 resolution
- Intensity normalization to [0, 1] range
- Data augmentation: random flips, rotations (±15°), intensity scaling (±10%)

**Train/Validation/Test Splits:**
- Pre-training (MRI+CT): 80%/10%/10%
- Transfer target (X-ray): Variable (10%, 25%, 50%, 100%) for training, fixed 10% test

### 2.6 Experimental Design

**Experiment 1: Transfer Efficiency (Primary)**

*Objective:* Validate that GAMDP achieves comparable reconstruction quality with reduced target modality data.

*Protocol:*
1. Pre-train GAMDP on MRI+CT data
2. Train modality-specific baseline on 100% X-ray data
3. Adapt GAMDP to X-ray using {10%, 25%, 50%} of training data
4. Evaluate on held-out X-ray test set

*Baselines:* Modality-specific diffusion model, HFS-SDE, MCG, SMRD

**Experiment 2: Geometric Feature Analysis (Mechanism Validation)**

*Objective:* Verify that the geometric latent space captures modality-invariant features.

*Protocol:*
1. Extract latent representations for paired MRI-CT-X-ray images
2. Compute cosine similarity across modalities
3. Compare with standard VAE latent space

**Experiment 3: Adapter Efficiency**

*Objective:* Confirm that LoRA adapters with <5% parameters match full fine-tuning.

*Protocol:*
1. Compare LoRA (r=4, 8, 16) vs. full fine-tuning
2. Measure reconstruction quality and parameter count

**Experiment 4: Ablation Studies**

*Objective:* Isolate contributions of each component.

*Ablations:*
- Without edge preservation loss
- Without cross-modal alignment
- Single-modality pre-training vs. multi-modal
- Different latent dimensions (c=4, 8, 16)

### 2.7 Evaluation Metrics

**Primary Metrics:**
- **PSNR (Peak Signal-to-Noise Ratio):** $\text{PSNR} = 10 \log_{10}\left(\frac{\text{MAX}^2}{\text{MSE}}\right)$
- **SSIM (Structural Similarity Index):** Measures structural similarity considering luminance, contrast, and structure

**Secondary Metrics:**
- **LPIPS:** Perceptual similarity using deep features
- **FID:** Distribution-level quality assessment
- **Cross-modal latent similarity:** Cosine similarity of latent representations

**Statistical Analysis:**
- Paired t-tests with significance level $\alpha = 0.05$
- Report mean ± standard deviation over 20 runs (5 seeds × 4 test variations)
- 95% confidence intervals and Cohen's d effect size

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect GAMDP pre-trained on MRI+CT and adapted to X-ray with 50% training data to achieve PSNR within 1dB of the modality-specific baseline trained on 100% data. Specifically, if the baseline achieves 32dB PSNR, GAMDP should achieve ≥31dB.

**Secondary Outcomes:**
- **P2:** Cross-modal latent similarity in GAMDP will exceed standard VAE by >0.1 (cosine similarity)
- **P3:** LoRA adapters with 5% parameters will achieve reconstruction within 0.5dB of full fine-tuning

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. PSNR(GAMDP@50%) < PSNR(Baseline@100%) - 3dB
2. Cross-modal latent similarity for GAMDP ≤ standard VAE
3. LoRA adapters require >20% parameters to match full fine-tuning

### 3.3 Scientific Impact

This research contributes to multiple areas:

**Inverse Problems:** Establishes a new paradigm for cross-modality transfer in imaging inverse problems, reducing the data requirements that currently limit deployment of learning-based methods.

**Representation Learning:** Provides empirical evidence for the existence of modality-invariant geometric representations in medical imaging, advancing understanding of what features transfer across domains.

**Diffusion Models:** Demonstrates that diffusion priors can be effectively decomposed into universal and task-specific components, informing future architectural designs.

### 3.4 Practical Impact

**Clinical Translation:** Enables deployment of state-of-the-art reconstruction methods in data-limited clinical settings, including rare diseases, pediatric imaging, and emerging imaging technologies.

**Resource Efficiency:** Reduces computational and data collection costs by enabling knowledge sharing across modalities, making advanced reconstruction accessible to resource-constrained healthcare systems.

**Regulatory Pathway:** The modular architecture facilitates regulatory approval by allowing validation of the universal prior separately from modality-specific adapters.

### 3.5 Limitations and Future Directions

**Limitations:**
- Transfer efficiency gains are empirically quantified but not theoretically guaranteed
- Computational cost of diffusion models may limit real-time applications
- Validation limited to structural medical imaging; functional imaging requires separate investigation

**Future Directions:**
- Extension to 3D volumetric imaging
- Integration with uncertainty quantification for clinical decision support
- Application to inverse problems with unknown forward models
- Theoretical analysis of geometric transfer bounds