# Research Proposal: Calibration-Free Diffusion Priors for Inverse Problems with Unknown Forward Models

## 1. Introduction

### Background

Inverse problems—the task of recovering unknown signals from indirect, noisy, or incomplete observations—are fundamental across science, medicine, and engineering. From reconstructing internal body structures in medical tomography to inferring subsurface properties in seismic imaging, these problems share a common mathematical structure: given measurements $y$ and a forward model $\mathcal{A}$, recover the original signal $x$ such that $y = \mathcal{A}(x) + \eta$, where $\eta$ represents measurement noise.

Recent advances in deep learning, particularly diffusion models, have revolutionized approaches to inverse problems. Diffusion models learn powerful generative priors by modeling the data distribution through a gradual denoising process, enabling high-quality reconstructions that respect the natural statistics of the underlying signals. Methods such as Diffusion Posterior Sampling (DPS), Score-based Diffusion Models, and their variants have demonstrated remarkable success in tasks ranging from MRI reconstruction to image restoration.

However, a critical assumption underlies virtually all existing diffusion-based inverse problem solvers: precise knowledge of the forward model $\mathcal{A}$. This assumption is often violated in practice. In medical imaging, actual system responses deviate from idealized models due to hardware imperfections, patient-specific variations (e.g., tissue heterogeneity affecting signal attenuation), and environmental factors. In seismic imaging, calibration drift and unmodeled physics create significant model-reality gaps. Even in computational photography, lens aberrations and sensor non-linearities introduce systematic discrepancies between assumed and actual forward models.

Recent work has begun addressing aspects of this challenge. Ensemble Kalman Diffusion Guidance (EnKG) provides derivative-free methods for black-box forward models, while DMPlug demonstrates robustness to unknown noise types. DAWN-SI incorporates noise embeddings for handling noisy observations. However, none of these approaches directly address the fundamental problem of jointly estimating unknown forward model parameters while leveraging diffusion priors for reconstruction.

### Research Objectives

This research aims to develop a comprehensive framework for solving inverse problems when the forward model is partially unknown or subject to calibration uncertainty. Specifically, our objectives are:

1. **Design a hierarchical Bayesian inference framework** that simultaneously estimates forward model parameters and reconstructs signals using pre-trained diffusion priors.

2. **Develop efficient algorithms** for joint posterior sampling that alternate between forward model parameter estimation and conditional signal reconstruction.

3. **Establish theoretical foundations** characterizing convergence properties and uncertainty quantification under model misspecification.

4. **Validate the framework** across diverse inverse problem domains including medical imaging, computational photography, and seismic inversion.

### Significance

This research addresses a fundamental barrier to deploying powerful diffusion-based methods in real-world applications. By enabling calibration-free operation, our framework could significantly impact:

- **Portable medical imaging devices** where precise calibration is impractical
- **Field-deployed sensing systems** subject to environmental variations
- **Adaptive imaging systems** that must operate across varying conditions
- **Scientific instruments** where the forward model contains unknown parameters of physical interest

## 2. Methodology

### 2.1 Problem Formulation

We consider inverse problems where the forward model belongs to a parameterized family $\mathcal{A}_\theta$, with $\theta \in \Theta$ representing unknown parameters. The observation model is:

$$y = \mathcal{A}_\theta(x) + \eta, \quad \eta \sim \mathcal{N}(0, \sigma^2 I)$$

Our goal is to compute the joint posterior distribution:

$$p(x, \theta | y) \propto p(y | x, \theta) p(x) p(\theta)$$

where $p(x)$ is implicitly defined through a pre-trained diffusion model and $p(\theta)$ encodes prior knowledge about plausible forward model parameters.

### 2.2 Forward Model Parameterization

We propose a physics-informed neural network architecture to parameterize the forward model family. Let $\mathcal{A}_\theta = \mathcal{A}_{\text{nom}} \circ \mathcal{D}_\phi$, where $\mathcal{A}_{\text{nom}}$ is the nominal (idealized) forward model and $\mathcal{D}_\phi$ represents learnable deviations parameterized by a neural network with weights $\phi$.

The deviation network is designed to capture:
- **Spatially-varying perturbations**: $\mathcal{D}_\phi(x) = x \odot (1 + \delta_\phi(x))$
- **Linear operator corrections**: $\mathcal{D}_\phi(x) = (I + \Delta_\phi)x$
- **Nonlinear distortions**: $\mathcal{D}_\phi(x) = x + f_\phi(x)$

To ensure physical plausibility, we incorporate constraints:

$$\mathcal{L}_{\text{physics}} = \lambda_1 \|\Delta_\phi\|_F^2 + \lambda_2 \|\nabla \delta_\phi\|_2^2 + \lambda_3 \mathcal{R}_{\text{domain}}(\phi)$$

where $\mathcal{R}_{\text{domain}}$ encodes domain-specific constraints (e.g., positivity of attenuation coefficients in CT imaging).

### 2.3 Hierarchical Posterior Sampling Algorithm

Our core algorithm alternates between two stages within each iteration:

**Stage 1: Forward Model Parameter Update**

Given current signal estimate $x^{(k)}$, update forward model parameters via:

$$\theta^{(k+1)} = \theta^{(k)} + \alpha_k \nabla_\theta \log p(\theta | y, x^{(k)})$$

The gradient is computed as:

$$\nabla_\theta \log p(\theta | y, x) = -\frac{1}{\sigma^2}(y - \mathcal{A}_\theta(x))^\top \nabla_\theta \mathcal{A}_\theta(x) + \nabla_\theta \log p(\theta)$$

For complex forward models, we employ ensemble-based gradient estimation inspired by EnKG:

$$\nabla_\theta \mathcal{A}_\theta(x) \approx \frac{1}{M}\sum_{i=1}^{M} \frac{\mathcal{A}_{\theta + \epsilon_i}(x) - \mathcal{A}_{\theta}(x)}{\epsilon_i}$$

**Stage 2: Conditional Diffusion Sampling**

Given current forward model estimate $\theta^{(k+1)}$, sample from $p(x | y, \theta^{(k+1)})$ using score-based diffusion:

Starting from $x_T \sim \mathcal{N}(0, I)$, iterate for $t = T, T-1, \ldots, 1$:

$$x_{t-1} = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{1-\alpha_t}{\sqrt{1-\bar{\alpha}_t}} s_\psi(x_t, t)\right) + \sigma_t z_t + \gamma_t \nabla_{x_t} \log p(y | x_t, \theta^{(k+1)})$$

where $s_\psi$ is the pre-trained score network, $z_t \sim \mathcal{N}(0, I)$, and the likelihood gradient is approximated via:

$$\nabla_{x_t} \log p(y | x_t, \theta) \approx -\frac{1}{\sigma^2} \nabla_{x_t} \|y - \mathcal{A}_\theta(\hat{x}_0(x_t))\|_2^2$$

with $\hat{x}_0(x_t) = \frac{x_t - \sqrt{1-\bar{\alpha}_t} s_\psi(x_t, t)}{\sqrt{\bar{\alpha}_t}}$ being the denoised estimate.

**Complete Algorithm:**

```
Input: Measurements y, initial θ⁰, pre-trained score network s_ψ
Output: Posterior samples {(x^(k), θ^(k))}_{k=1}^K

for k = 1 to K do:
    # Stage 1: Update forward model parameters
    for j = 1 to J do:
        g_θ ← ∇_θ log p(θ | y, x^(k-1))  # Gradient estimation
        θ ← θ + α_k · g_θ
    end for
    θ^(k) ← θ
    
    # Stage 2: Conditional diffusion sampling
    x_T ~ N(0, I)
    for t = T to 1 do:
        x̂_0 ← Denoise(x_t, s_ψ, t)
        g_x ← ∇_{x_t} ||y - A_{θ^(k)}(x̂_0)||²
        x_{t-1} ← DiffusionStep(x_t, s_ψ, t) + γ_t · g_x
    end for
    x^(k) ← x_0
end for
```

### 2.4 Uncertainty Quantification

Our framework naturally provides uncertainty estimates for both the reconstruction and forward model parameters. We compute:

**Reconstruction uncertainty:**
$$\text{Var}[x | y] \approx \frac{1}{K}\sum_{k=1}^{K}(x^{(k)} - \bar{x})^2$$

**Forward model uncertainty:**
$$\text{Var}[\theta | y] \approx \frac{1}{K}\sum_{k=1}^{K}(\theta^{(k)} - \bar{\theta})^2$$

**Prediction uncertainty** (accounting for both sources):
$$\text{Var}[\mathcal{A}(x) | y] \approx \mathbb{E}_\theta[\text{Var}[x|\theta,y]] + \text{Var}_\theta[\mathbb{E}[x|\theta,y]]$$

### 2.5 Experimental Design

**Datasets and Domains:**

1. **Medical Imaging (CT/MRI):**
   - FastMRI dataset for MRI reconstruction
   - LIDC-IDRI dataset for CT reconstruction
   - Forward model uncertainty: coil sensitivity variations (MRI), beam hardening (CT)

2. **Computational Photography:**
   - DIV2K and FFHQ datasets
   - Forward model uncertainty: spatially-varying blur, lens aberrations

3. **Seismic Imaging:**
   - OpenFWI benchmark dataset
   - Forward model uncertainty: velocity model perturbations

**Baseline Methods:**
- Standard DPS with known forward model (oracle)
- DPS with misspecified forward model
- EnKG for derivative-free guidance
- DMPlug for noise-robust reconstruction
- DAWN-SI for data-aware reconstruction

**Evaluation Metrics:**

1. **Reconstruction Quality:**
   - Peak Signal-to-Noise Ratio (PSNR)
   - Structural Similarity Index (SSIM)
   - Learned Perceptual Image Patch Similarity (LPIPS)

2. **Forward Model Estimation:**
   - Parameter estimation error: $\|\hat{\theta} - \theta^*\|_2$
   - Forward model prediction error: $\|\mathcal{A}_{\hat{\theta}} - \mathcal{A}_{\theta^*}\|_{op}$

3. **Uncertainty Calibration:**
   - Expected Calibration Error (ECE)
   - Negative Log-Likelihood (NLL)
   - Coverage probability of credible intervals

4. **Computational Efficiency:**
   - Wall-clock time per reconstruction
   - Number of forward model evaluations

**Ablation Studies:**
- Impact of forward model parameterization complexity
- Sensitivity to prior specification $p(\theta)$
- Effect of alternation frequency between stages
- Comparison of gradient estimation methods (exact vs. ensemble-based)

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Robust Reconstruction Under Model Uncertainty:** We anticipate achieving reconstruction quality within 1-2 dB PSNR of oracle methods (with known forward models) while significantly outperforming existing methods under model misspecification (5-10 dB improvement expected).

2. **Automatic Forward Model Calibration:** The framework should recover unknown forward model parameters with <10% relative error across tested domains, enabling joint inference of physical parameters of scientific interest.

3. **Well-Calibrated Uncertainty Estimates:** Unlike existing methods that either ignore or poorly quantify model uncertainty, our approach should provide calibrated uncertainty estimates with ECE < 0.05 across experiments.

4. **Scalable Implementation:** We expect computational overhead of 2-3× compared to standard diffusion-based methods, making the approach practical for real applications.

### Broader Impact

**Scientific Impact:**
This research bridges the gap between theoretical advances in diffusion models and practical deployment in scientific and medical imaging. By removing the requirement for precise forward model knowledge, we enable principled uncertainty quantification in settings where it was previously impossible.

**Practical Impact:**
The framework could transform deployment of AI-based reconstruction in:
- Low-resource medical settings with limited calibration infrastructure
- Environmental monitoring systems subject to changing conditions
- Scientific instruments where forward model parameters are quantities of interest

**Methodological Impact:**
Our hierarchical inference framework provides a template for combining learned priors with physics-based models under uncertainty, potentially inspiring applications beyond inverse problems in scientific machine learning more broadly.

### Limitations and Future Work

We acknowledge potential limitations including computational cost scaling with forward model complexity, sensitivity to the choice of forward model parameterization, and the need for domain expertise in specifying physics-informed constraints. Future work will address scalability to 3D problems, extension to non-Gaussian observation models, and integration with online learning for adaptive calibration.