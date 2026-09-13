# Research Proposal: Uncertainty-Aware Generative Downscaling with Physics-Constrained Diffusion Models

## 1. Introduction

### Background

Climate change poses an existential threat to human civilization, demanding accurate projections at spatial scales relevant for adaptation and mitigation planning. While Global Climate Models (GCMs) have advanced substantially, their coarse resolution (~100 km) fundamentally limits their utility for regional impact assessments, which require kilometer-scale predictions to capture complex topographic effects, localized extreme events, and land-atmosphere interactions. Dynamical downscaling—running high-resolution regional climate models nested within GCMs—remains the gold standard for generating physically consistent fine-scale projections but incurs prohibitive computational costs, often requiring thousands of CPU hours for single decadal simulations.

Statistical downscaling methods offer computational efficiency but have historically sacrificed either physical consistency or probabilistic completeness. Traditional approaches like bias correction and spatial disaggregation (BCSD) or quantile mapping fail to capture spatial coherence and multivariate dependencies. More recent machine learning approaches, including convolutional neural networks and generative adversarial networks, improve spatial structure but typically produce deterministic outputs that inadequately characterize uncertainty—a critical limitation given the inherent stochasticity in climate systems and the need for risk-based adaptation planning.

Diffusion models have emerged as state-of-the-art generative frameworks, demonstrating remarkable capabilities in image synthesis and increasingly in scientific applications. Recent work has begun exploring their application to climate downscaling, with promising results. Rosu et al. (2025) introduced PDE-informed latent diffusion for temperature downscaling, demonstrating that physics conditioning improves output plausibility. Brusaferri and Ballarino (2025) addressed calibration issues through conformal prediction frameworks. Hess et al. (2024) showed that consistency models can achieve fast, scale-adaptive downscaling with good generalization. However, existing approaches either incorporate physics as soft constraints (loss terms) that can be violated during inference, lack rigorous uncertainty quantification, or fail to explicitly handle extreme events that dominate climate impact assessments.

### Research Objectives

This research proposes **Physics-Constrained Diffusion Models (PCDM)**, a novel framework that addresses three fundamental limitations in current climate downscaling approaches:

1. **Hard Physical Constraints**: Embed conservation laws and topographic consistency directly into the diffusion sampling process as inviolable constraints, rather than soft penalties.

2. **Comprehensive Uncertainty Quantification**: Generate calibrated ensemble predictions that capture both aleatoric uncertainty (inherent climate variability) and reduce epistemic uncertainty through physics-informed architecture design.

3. **Extreme Event Fidelity**: Employ classifier-free guidance conditioned on large-scale atmospheric patterns to improve the representation of high-impact, low-likelihood events crucial for adaptation planning.

### Significance

This research directly addresses the workshop's emphasis on dynamical downscaling with physical consistency. Success would enable climate scientists to generate thousands of physically plausible high-resolution scenarios at a fraction of current computational costs, fundamentally transforming regional climate impact assessment. The explicit uncertainty quantification provides decision-makers with the probabilistic information necessary for robust adaptation planning under deep uncertainty.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathbf{x}_c \in \mathbb{R}^{C \times H_c \times W_c}$ denote coarse-resolution climate fields (e.g., from GCM output) with $C$ variables, and $\mathbf{x}_f \in \mathbb{R}^{C \times H_f \times W_f}$ the corresponding high-resolution fields where $H_f = sH_c$ and $W_f = sW_c$ for downscaling factor $s$. Our goal is to learn the conditional distribution $p(\mathbf{x}_f | \mathbf{x}_c)$ subject to physical constraints $\mathcal{G}(\mathbf{x}_f) = 0$, where $\mathcal{G}$ encodes conservation laws and boundary conditions.

### 2.2 Physics-Constrained Diffusion Framework

#### 2.2.1 Base Diffusion Architecture

We adopt the denoising diffusion probabilistic model (DDPM) framework with a conditional U-Net architecture. The forward process gradually adds Gaussian noise to high-resolution fields:

$$q(\mathbf{x}_f^{(t)} | \mathbf{x}_f^{(t-1)}) = \mathcal{N}(\mathbf{x}_f^{(t)}; \sqrt{1-\beta_t}\mathbf{x}_f^{(t-1)}, \beta_t \mathbf{I})$$

where $\beta_t$ is the noise schedule. The reverse process learns to denoise conditioned on coarse inputs:

$$p_\theta(\mathbf{x}_f^{(t-1)} | \mathbf{x}_f^{(t)}, \mathbf{x}_c) = \mathcal{N}(\mathbf{x}_f^{(t-1)}; \boldsymbol{\mu}_\theta(\mathbf{x}_f^{(t)}, \mathbf{x}_c, t), \sigma_t^2 \mathbf{I})$$

The conditioning on $\mathbf{x}_c$ is achieved through cross-attention layers and channel concatenation after bicubic upsampling.

#### 2.2.2 Hard Physical Constraints via Projection

Unlike soft constraint approaches that add PDE loss terms, we enforce physical constraints through differentiable projection layers applied at each denoising step. For a predicted mean $\hat{\boldsymbol{\mu}}$, we compute the physically consistent output as:

$$\boldsymbol{\mu}_\theta = \text{Proj}_\mathcal{C}(\hat{\boldsymbol{\mu}}) = \arg\min_{\mathbf{z} \in \mathcal{C}} \|\mathbf{z} - \hat{\boldsymbol{\mu}}\|_2^2$$

where $\mathcal{C} = \{\mathbf{x} : \mathcal{G}(\mathbf{x}) = 0\}$ is the constraint manifold.

**Mass Conservation**: For precipitation downscaling, we enforce that the spatial integral of high-resolution precipitation matches the coarse-resolution total over each coarse grid cell:

$$\sum_{i,j \in \Omega_k} P_f(i,j) \cdot \Delta A_{ij} = P_c(k) \cdot A_k$$

where $\Omega_k$ indexes fine grid cells within coarse cell $k$, $\Delta A_{ij}$ are fine cell areas, and $A_k$ is the coarse cell area. This constraint is implemented via a differentiable redistribution layer:

$$P_f^{\text{proj}}(i,j) = P_f(i,j) \cdot \frac{P_c(k) \cdot A_k}{\sum_{i',j' \in \Omega_k} P_f(i',j') \cdot \Delta A_{i'j'}}$$

**Energy Conservation**: For temperature fields, we enforce consistency with the surface energy balance:

$$R_{net} = H + LE + G$$

where $R_{net}$ is net radiation, $H$ is sensible heat flux, $LE$ is latent heat flux, and $G$ is ground heat flux. A residual correction layer adjusts temperature predictions to satisfy this balance.

**Topographic Consistency**: Temperature fields must respect orographic lapse rates. We parameterize temperature anomalies relative to a topography-aware baseline:

$$T_f(i,j) = T_{\text{base}}(\mathbf{x}_c) + \Gamma \cdot (z_f(i,j) - \bar{z}_c) + \Delta T_\theta(i,j)$$

where $\Gamma$ is the environmental lapse rate (~6.5 K/km), $z_f$ is high-resolution topography, and $\Delta T_\theta$ is the learned residual.

#### 2.2.3 Classifier-Free Guidance for Extremes

To improve extreme event representation, we employ classifier-free guidance with atmospheric pattern conditioning. Let $\mathbf{a}$ represent large-scale atmospheric indices (e.g., 500 hPa geopotential height patterns, moisture flux convergence). During training, we randomly drop $\mathbf{a}$ with probability $p_{drop} = 0.1$ to learn both conditional and unconditional models. At inference, we guide sampling toward atmospheric-consistent outputs:

$$\tilde{\boldsymbol{\epsilon}}_\theta = (1 + w) \cdot \boldsymbol{\epsilon}_\theta(\mathbf{x}_f^{(t)}, \mathbf{x}_c, \mathbf{a}, t) - w \cdot \boldsymbol{\epsilon}_\theta(\mathbf{x}_f^{(t)}, \mathbf{x}_c, \varnothing, t)$$

where $w$ is the guidance scale, increased during extreme event sampling to strengthen physical consistency.

### 2.3 Training Procedure

**Training Objective**: We combine the standard diffusion loss with auxiliary physics losses for improved constraint learning:

$$\mathcal{L} = \mathbb{E}_{t, \mathbf{x}_f, \boldsymbol{\epsilon}}\left[\|\boldsymbol{\epsilon} - \boldsymbol{\epsilon}_\theta(\mathbf{x}_f^{(t)}, \mathbf{x}_c, \mathbf{a}, t)\|_2^2\right] + \lambda_{\text{phys}} \mathcal{L}_{\text{phys}}$$

where $\mathcal{L}_{\text{phys}}$ penalizes constraint violations on denoised predictions at intermediate timesteps, serving as a curriculum that gradually improves constraint satisfaction.

**Data**: We utilize paired ERA5 reanalysis data (0.25° resolution as "coarse") and HRES operational analysis or regional reanalysis (e.g., ERA5-Land at ~9 km) as high-resolution targets. Training covers 1979-2015, validation 2016-2018, testing 2019-2023. Variables include 2m temperature, precipitation, 10m wind components, and surface pressure.

### 2.4 Experimental Design

#### Baselines
1. **Dynamical**: WRF regional model nested in ERA5
2. **Statistical**: BCSD, DeepSD (CNN-based)
3. **Generative**: Vanilla conditional diffusion, PDE-informed latent diffusion (Rosu et al., 2025), Consistency model (Hess et al., 2024)

#### Evaluation Metrics

**Distributional Accuracy**:
- Continuous Ranked Probability Score (CRPS): $\text{CRPS} = \mathbb{E}[|X - x|] - \frac{1}{2}\mathbb{E}[|X - X'|]$
- Wasserstein distance between predicted and observed distributions
- Spatial correlation and RMSE for ensemble mean

**Physical Consistency**:
- Water budget closure error: $\epsilon_{WB} = |P - ET - R - \Delta S|$ integrated over watersheds
- Energy balance residual
- Lapse rate consistency: correlation between $\Delta T$ and $\Delta z$

**Extreme Event Statistics**:
- Return level estimation accuracy for 10, 50, 100-year events
- Fraction of Attributable Risk for threshold exceedances
- Spatial extent of extreme events (object-based verification)

**Uncertainty Calibration**:
- Prediction Interval Coverage Probability (PICP)
- Reliability diagrams for probabilistic forecasts
- Spread-skill relationship

**Computational Efficiency**:
- Wall-clock time per ensemble member
- GPU memory requirements
- Scaling with resolution

### 2.5 Implementation Details

- Architecture: U-Net with attention at 16×16 and 8×8 resolutions, 256 base channels
- Diffusion steps: 1000 training, 50 inference (DDIM sampling)
- Downscaling factor: 8× (from ~80 km to ~10 km effective resolution)
- Ensemble size: 50 members per prediction
- Hardware: 8× NVIDIA A100 GPUs, estimated 72 hours training

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Performance**: We anticipate PCDM will achieve CRPS improvements of 15-25% over vanilla diffusion baselines and match or exceed dynamical downscaling skill while being approximately 1000× faster computationally.

2. **Physical Consistency**: Hard constraint enforcement should eliminate water budget closure errors (currently 5-15% in soft-constraint methods) and ensure strict topographic consistency.

3. **Extreme Events**: Classifier-free guidance conditioning on atmospheric patterns is expected to improve 100-year return level estimation by 30-40% compared to unconditioned approaches, addressing a critical gap in current methods.

4. **Calibration**: Integration of conformal prediction post-processing (following Brusaferri and Ballarino, 2025) should achieve nominal coverage rates (e.g., 95% intervals containing observations 95% of the time).

### Scientific Impact

This research advances the intersection of generative AI and climate science by demonstrating that hard physical constraints can be embedded in diffusion models without sacrificing generative quality. The methodology generalizes beyond downscaling to other physics-constrained generation tasks in Earth system modeling.

### Societal Impact

Reliable probabilistic downscaled projections are essential for climate adaptation. By providing calibrated uncertainty estimates for regional climate impacts—including extreme precipitation, heat waves, and drought—PCDM enables risk-informed infrastructure planning, agricultural adaptation, and emergency preparedness. The computational efficiency democratizes access to high-resolution climate information for resource-limited regions most vulnerable to climate change.

### Limitations and Future Work

The reliance on reanalysis data for training introduces observational biases that may not transfer to future climate states. Future work will explore transfer learning approaches and hybrid training with GCM outputs. Additionally, extending the framework to fully coupled multivariate fields (atmosphere-ocean-land) presents opportunities for more comprehensive Earth system downscaling.