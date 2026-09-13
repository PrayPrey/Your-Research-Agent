# Research Proposal

## Title
**PediDiff: Uncertainty-Aware Diffusion Models for Reliable Pediatric Medical Image Synthesis with Automatic Quality Validation**

---

## 1. Introduction

### Background

Pediatric medical imaging represents one of the most challenging domains in healthcare AI due to severe data scarcity arising from ethical constraints surrounding research involving minors, smaller patient populations compared to adults, and the remarkable anatomical variability across developmental stages from neonates to adolescents. These limitations significantly impede the development of robust machine learning models for pediatric diagnosis, treatment planning, and disease monitoring. While synthetic data generation through deep generative models offers a promising solution, existing approaches fail to address the unique requirements of pediatric applications.

Recent advances in diffusion models have demonstrated unprecedented capabilities in generating high-fidelity images across various domains, including medical imaging. Models such as MAISI-v2 have shown remarkable progress in 3D medical image synthesis, while frameworks like IMPROVE have addressed the challenge of medical plausibility without human validation. However, these advances have primarily focused on adult populations, leaving the pediatric domain underserved. The application of diffusion models to pediatric imaging faces two critical gaps that prevent clinical adoption: the absence of uncertainty quantification mechanisms to identify unreliable synthetic samples, and the lack of objective validation metrics specifically designed for pediatric anatomical assessment.

The challenge of uncertainty quantification in generative models has received growing attention, with recent work exploring ensemble-based approaches and measurement-conditioned methods for medical image reconstruction. Simultaneously, age-conditioned generative models have emerged as a strategy to capture developmental changes. However, no existing framework comprehensively addresses uncertainty-aware generation, age-conditioning, and automatic quality validation within a unified architecture tailored for pediatric applications.

### Research Objectives

This research proposes **PediDiff**, a novel diffusion framework designed to generate reliable pediatric medical images with built-in uncertainty quantification and automatic quality validation. Our specific objectives are:

1. To develop an age-conditioned diffusion model that captures the continuous spectrum of anatomical changes across pediatric developmental stages
2. To implement an ensemble-based uncertainty estimation mechanism that produces pixel-wise confidence maps alongside generated images
3. To design an anatomical validity scoring system trained on pediatric priors that provides interpretable quality metrics
4. To establish a comprehensive validation pipeline enabling automatic rejection of unreliable synthetic samples

### Significance

This research directly addresses the workshop's focus on minority data groups by targeting pediatrics—a critically underserved population in medical AI. The proposed framework will provide clinicians with trustworthy synthetic data accompanied by transparent quality indicators, facilitating the practical integration of generative models into pediatric diagnostic pipelines. By enabling automatic validation without human oversight, PediDiff addresses the key challenge of designing objective validation procedures highlighted in the workshop's call. The uncertainty quantification component ensures interpretability and accountability, essential requirements for clinical adoption of generative methodologies.

---

## 2. Methodology

### 2.1 Overview

PediDiff consists of three interconnected components: (1) an age-conditioned diffusion backbone for pediatric image generation, (2) an ensemble-based uncertainty estimation module, and (3) an anatomical validity scoring network. We describe each component in detail below.

### 2.2 Age-Conditioned Diffusion Model

#### Architecture Design

We build upon the denoising diffusion probabilistic model (DDPM) framework, extending it with continuous age conditioning. Given an input image $x_0$ and patient age $a \in [0, 18]$ years, the forward diffusion process progressively adds Gaussian noise over $T$ timesteps:

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t}x_{t-1}, \beta_t I)$$

where $\beta_t$ is the noise schedule. The reverse process learns to denoise, conditioned on both timestep $t$ and age $a$:

$$p_\theta(x_{t-1} | x_t, a) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t, a), \Sigma_\theta(x_t, t, a))$$

#### Age Embedding

To capture continuous developmental changes, we employ a sinusoidal positional encoding for age, combined with a learnable MLP:

$$e_a = \text{MLP}([\sin(\omega_1 a), \cos(\omega_1 a), ..., \sin(\omega_d a), \cos(\omega_d a)])$$

where $\omega_i = 10000^{-2i/d}$ and $d$ is the embedding dimension. This embedding is injected into the U-Net denoising network through adaptive group normalization layers:

$$\text{AdaGN}(h, e_a, e_t) = e_a^{(s)} \cdot \text{GroupNorm}(h) + e_a^{(b)} + e_t$$

where $h$ is the hidden representation, $e_t$ is the timestep embedding, and $e_a^{(s)}, e_a^{(b)}$ are learned scale and bias parameters derived from $e_a$.

### 2.3 Ensemble-Based Uncertainty Estimation

#### Multiple Prediction Heads

To quantify epistemic uncertainty arising from model limitations and data scarcity, we employ an ensemble approach with $K$ prediction heads sharing a common backbone. Each head $k$ produces its own noise prediction:

$$\epsilon_\theta^{(k)}(x_t, t, a) = f_k(\phi(x_t, t, a))$$

where $\phi$ represents shared U-Net features and $f_k$ is the $k$-th prediction head. During training, each head receives independent initialization and dropout masks to encourage diversity.

#### Uncertainty Map Generation

Given the ensemble predictions, we compute pixel-wise uncertainty maps through the variance of predicted noise:

$$U(x_t, t, a) = \frac{1}{K} \sum_{k=1}^{K} \left(\epsilon_\theta^{(k)}(x_t, t, a) - \bar{\epsilon}_\theta(x_t, t, a)\right)^2$$

where $\bar{\epsilon}_\theta = \frac{1}{K}\sum_{k=1}^{K}\epsilon_\theta^{(k)}$ is the mean prediction. The final generated image uses the ensemble mean, while the accumulated uncertainty across denoising steps provides the pixel-wise confidence map:

$$U_{\text{final}} = \frac{1}{T} \sum_{t=1}^{T} U(x_t, t, a)$$

#### Training Objective

The ensemble is trained with a combined loss:

$$\mathcal{L}_{\text{ensemble}} = \frac{1}{K} \sum_{k=1}^{K} \mathbb{E}_{x_0, \epsilon, t} \left[ \|\epsilon - \epsilon_\theta^{(k)}(x_t, t, a)\|^2 \right] + \lambda_{\text{div}} \mathcal{L}_{\text{diversity}}$$

where the diversity loss encourages disagreement among heads:

$$\mathcal{L}_{\text{diversity}} = -\frac{1}{K(K-1)} \sum_{i \neq j} \|\epsilon_\theta^{(i)} - \epsilon_\theta^{(j)}\|^2$$

### 2.4 Anatomical Validity Scoring Network

#### Architecture

We design a discriminator network $D_\phi$ trained on pediatric anatomical priors to assess structural plausibility. The network takes as input a generated image $\hat{x}_0$ and age $a$, producing:

1. A global validity score $s_{\text{global}} \in [0, 1]$
2. Regional validity scores $s_{\text{region}}^{(r)}$ for predefined anatomical regions
3. An interpretable feature vector highlighting specific anatomical concerns

#### Training with Anatomical Priors

The discriminator is trained on real pediatric images with anatomical annotations:

$$\mathcal{L}_D = -\mathbb{E}_{x \sim p_{\text{real}}}[\log D_\phi(x, a)] - \mathbb{E}_{\hat{x} \sim p_{\text{gen}}}[\log(1 - D_\phi(\hat{x}, a))] + \lambda_{\text{anat}} \mathcal{L}_{\text{anatomical}}$$

The anatomical loss enforces consistency with developmental norms:

$$\mathcal{L}_{\text{anatomical}} = \sum_{r} w_r \cdot \text{MSE}(m_r(\hat{x}), \mu_r(a))$$

where $m_r$ extracts measurements from region $r$, and $\mu_r(a)$ represents age-specific anatomical norms derived from pediatric growth charts.

### 2.5 Automatic Quality Validation Pipeline

We combine uncertainty estimation and anatomical validity scoring into an automatic rejection criterion. A generated sample $\hat{x}_0$ is accepted if:

$$\mathcal{Q}(\hat{x}_0) = \alpha \cdot (1 - \bar{U}_{\text{final}}) + (1-\alpha) \cdot s_{\text{global}} > \tau$$

where $\bar{U}_{\text{final}}$ is the mean normalized uncertainty, $\alpha$ balances the two components, and $\tau$ is the acceptance threshold calibrated on a validation set.

### 2.6 Data Collection and Preprocessing

#### Datasets

We will utilize the following publicly available datasets:

1. **Pediatric Chest X-rays**: PediCXR dataset (approximately 5,000 images) with age annotations, supplemented by pediatric subsets from CheXpert and MIMIC-CXR
2. **Pediatric Brain MRI**: Pediatric subset of IXI dataset, ABIDE (Autism Brain Imaging Data Exchange), and Calgary-Campinas dataset

#### Preprocessing Pipeline

- Standardization of image resolution (256×256 for 2D, 128×128×128 for 3D)
- Intensity normalization using z-score standardization
- Age normalization to [0, 1] range
- Data augmentation: random rotations (±15°), scaling (0.9-1.1), and intensity variations

### 2.7 Experimental Design

#### Baselines

We compare PediDiff against:
1. Standard DDPM without age conditioning
2. Age-conditioned diffusion without uncertainty estimation
3. IMPROVE framework adapted for pediatric data
4. StyleGAN3 with age conditioning

#### Evaluation Metrics

**Image Quality Metrics:**
- Fréchet Inception Distance (FID) stratified by age groups
- Structural Similarity Index (SSIM) compared to matched real samples
- Peak Signal-to-Noise Ratio (PSNR)

**Uncertainty Calibration Metrics:**
- Expected Calibration Error (ECE) for uncertainty estimates
- Correlation between uncertainty and actual reconstruction error
- Area Under Sparsification Error curve (AUSE)

**Anatomical Validity Metrics:**
- Anatomical landmark detection accuracy
- Age-specific measurement compliance rate
- Radiologist assessment scores (Likert scale 1-5)

**Downstream Task Performance:**
- Classification accuracy on synthetic data augmented training sets
- Segmentation Dice scores when training on mixed real/synthetic data

#### Ablation Studies

We conduct ablations on:
1. Number of ensemble heads ($K \in \{3, 5, 7, 10\}$)
2. Age embedding strategies (sinusoidal vs. learned vs. binned)
3. Acceptance threshold $\tau$ sensitivity
4. Impact of anatomical loss weight $\lambda_{\text{anat}}$

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Technical Deliverables:**
   - A fully trained PediDiff model for pediatric chest X-ray synthesis with age-conditioned generation spanning 0-18 years
   - A brain MRI variant demonstrating generalizability across imaging modalities
   - Open-source code repository with pre-trained weights and inference pipelines

2. **Quantitative Performance:**
   - FID scores competitive with or superior to state-of-the-art adult medical image synthesis methods
   - Well-calibrated uncertainty estimates with ECE < 0.05
   - Anatomical validity acceptance rates >85% on held-out test sets

3. **Clinical Utility Demonstrations:**
   - Improved pediatric disease classification accuracy (+3-5% AUC) when augmenting limited training sets with validated synthetic samples
   - Demonstrated reliability through radiologist evaluation confirming clinical plausibility

### Scientific Impact

This research advances the field by:
- Establishing the first comprehensive uncertainty-aware framework specifically designed for pediatric medical image synthesis
- Providing methodological contributions in age-conditioned diffusion modeling that capture continuous developmental changes
- Introducing interpretable quality metrics that bridge the gap between generative model outputs and clinical requirements

### Clinical Impact

The practical implications include:
- Enabling data augmentation for rare pediatric conditions where training data is extremely limited
- Providing transparent quality indicators that build clinician trust in synthetic data
- Facilitating privacy-preserving data sharing through synthetic equivalents with validated fidelity

### Broader Impact

PediDiff establishes a template for uncertainty-aware generative modeling in sensitive medical applications, particularly those involving vulnerable populations. The automatic validation pipeline addresses a critical barrier to clinical adoption identified in the workshop's scope, potentially accelerating the translation of generative AI methods from research to practice in healthcare settings.

---

## References

The methodology builds upon recent advances in diffusion models for medical imaging (IMPROVE, MAISI-v2), uncertainty quantification in medical image synthesis, and age-conditioned generative modeling. Our framework synthesizes these approaches into a unified solution tailored for the unique challenges of pediatric medical imaging.