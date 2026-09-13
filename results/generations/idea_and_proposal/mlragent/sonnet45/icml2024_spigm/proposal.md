# Hierarchical Diffusion Models with Learnable Structure Priors for Multi-Scale Time Series Generation

## 1. Introduction

### Background

Time series data pervade scientific and industrial applications, from climate modeling and physiological monitoring to financial forecasting and industrial process control. These data inherently exhibit complex multi-scale temporal dependencies, encompassing slow-varying trends, periodic patterns, and high-frequency fluctuations. Traditional generative models for time series, including autoregressive models, GANs, and more recently, diffusion models, have shown promise in capturing temporal dynamics. However, they face critical limitations when applied to structured scientific time series where domain-specific constraints and hierarchical temporal patterns are paramount.

Recent advances in diffusion probabilistic models have demonstrated remarkable success in generating high-quality images, audio, and text. Several works have extended diffusion models to time series generation (DiffStyleTS, DS-Diffusion, T2S), showing improved performance over traditional approaches. However, these methods largely treat time series as uniform temporal sequences, applying diffusion processes uniformly across all temporal scales. This approach fails to encode the known hierarchical structure of many scientific time series, where different temporal scales exhibit distinct statistical properties and are governed by different physical processes.

Consider climate data, where long-term trends span decades, seasonal patterns recur annually, and weather fluctuations occur daily. Similarly, physiological signals like electrocardiograms exhibit hierarchical structure with heart rate variability at multiple timescales, each governed by different physiological mechanisms. Generating synthetic data that preserves these multi-scale structures while satisfying domain constraints (e.g., energy conservation, causality) remains an open challenge.

### Research Objectives

This research proposes a novel **Hierarchical Diffusion Model with Learnable Structure Priors (HDM-LSP)** that addresses these limitations through three primary objectives:

1. **Develop a multi-scale diffusion framework** that decomposes time series generation across hierarchical temporal scales, with scale-specific diffusion processes tailored to the statistical properties of each scale.

2. **Design a learnable structure extraction module** that automatically discovers multi-scale patterns while incorporating domain-specific constraints through differentiable constraint layers.

3. **Enable physically plausible generation** through structure-preserving losses and coarse-to-fine generation strategies that ensure coherence across scales.

### Significance

This research addresses several critical gaps in structured probabilistic inference and generative modeling:

- **Scientific validity**: By enforcing domain constraints during generation, the model produces physically plausible synthetic data suitable for scientific applications where structural validity is non-negotiable.

- **Sample efficiency**: The hierarchical approach enables better generalization from limited data by leveraging known structural properties, crucial for data-scarce scientific domains.

- **Interpretability**: Explicit decomposition into interpretable scales (trends, seasonality, noise) provides transparency in the generation process, essential for scientific trust and debugging.

- **Computational efficiency**: Scale-specific processing enables faster sampling through parallel generation of independent scales and focused diffusion on relevant temporal frequencies.

## 2. Methodology

### 2.1 Overall Framework Architecture

The HDM-LSP framework consists of four interconnected components: (1) Multi-scale Decomposition Module, (2) Structure Extraction Network, (3) Hierarchical Diffusion Process, and (4) Coarse-to-Fine Generator. The complete pipeline is illustrated in the following formulation.

### 2.2 Multi-Scale Decomposition Module

Given an input time series $\mathbf{x} \in \mathbb{R}^T$, we decompose it into $K$ hierarchical scales using a hybrid wavelet-learned decomposition:

$$\mathbf{x} = \sum_{k=1}^{K} \mathbf{x}^{(k)} + \mathbf{r}$$

where $\mathbf{x}^{(k)}$ represents the $k$-th scale component and $\mathbf{r}$ is the residual. We employ the Maximal Overlap Discrete Wavelet Transform (MODWT) as the base decomposition, modified with learnable reconstruction filters:

$$\mathbf{x}^{(k)} = \mathcal{W}_k^{-1}(\phi_{\theta_k}(\mathcal{W}_k(\mathbf{x})))$$

where $\mathcal{W}_k$ and $\mathcal{W}_k^{-1}$ are wavelet transform and inverse transform at scale $k$, and $\phi_{\theta_k}$ is a learnable refinement network that adapts the decomposition to the data distribution.

**Implementation Details:**
- Use Daubechies wavelets (db4) as base wavelets for their good time-frequency localization
- Refinement network $\phi_{\theta_k}$: 3-layer 1D CNN with residual connections
- Scales: $K=4$ capturing high-frequency (daily), medium (weekly), low-frequency (monthly), and trend components
- Ensure perfect reconstruction through orthogonality constraints on learned filters

### 2.3 Structure Extraction Network

The Structure Extraction Network (SEN) learns to identify and encode structural patterns within each scale through a multi-head attention mechanism combined with domain-specific constraint layers.

**Architecture:**

For each scale $k$, we define:

$$\mathbf{s}^{(k)} = \text{SEN}_k(\mathbf{x}^{(k)}) = \text{ConstraintLayer}_k(\text{Attention}_k(\text{Embed}_k(\mathbf{x}^{(k)})))$$

where $\mathbf{s}^{(k)} \in \mathbb{R}^{d_s}$ is the structural encoding.

**Multi-Head Attention Layer:**

$$\text{Attention}_k(\mathbf{h}) = \text{Concat}(\text{head}_1, ..., \text{head}_H)\mathbf{W}^O$$

$$\text{head}_i = \text{softmax}\left(\frac{\mathbf{Q}_i\mathbf{K}_i^T}{\sqrt{d_k}}\right)\mathbf{V}_i$$

where $\mathbf{Q}_i = \mathbf{h}\mathbf{W}_i^Q$, $\mathbf{K}_i = \mathbf{h}\mathbf{W}_i^K$, $\mathbf{V}_i = \mathbf{h}\mathbf{W}_i^V$.

**Differentiable Constraint Layers:**

Domain knowledge is encoded through differentiable constraint functions. For example:

1. **Energy Conservation (for physical systems):**
$$\mathcal{L}_{\text{energy}}^{(k)} = \left|\sum_{t=1}^T (\mathbf{x}_t^{(k)})^2 - E_{\text{target}}\right|$$

2. **Causality Constraint (ensuring no future information leakage):**
$$\mathcal{L}_{\text{causal}}^{(k)} = \sum_{t=1}^T \text{ReLU}(\text{MutualInfo}(\mathbf{x}_{\leq t}^{(k)}, \mathbf{x}_{>t}^{(k)}) - \epsilon)$$

3. **Monotonicity/Trend Constraint (for cumulative processes):**
$$\mathcal{L}_{\text{mono}}^{(k)} = \sum_{t=1}^{T-1} \text{ReLU}(-(\mathbf{x}_{t+1}^{(k)} - \mathbf{x}_t^{(k)}))$$

These constraints are applied as soft penalties during training and hard constraints during generation through projected gradient descent.

### 2.4 Hierarchical Diffusion Process

We define scale-specific diffusion processes with different noise schedules tailored to each temporal scale's characteristics.

**Forward Process:**

For scale $k$ at timestep $t$ of the diffusion process:

$$q(\mathbf{x}_t^{(k)}|\mathbf{x}_0^{(k)}) = \mathcal{N}(\mathbf{x}_t^{(k)}; \sqrt{\bar{\alpha}_t^{(k)}}\mathbf{x}_0^{(k)}, (1-\bar{\alpha}_t^{(k)})\mathbf{I})$$

where $\bar{\alpha}_t^{(k)} = \prod_{i=1}^t \alpha_i^{(k)}$ and the noise schedule $\{\alpha_i^{(k)}\}$ is scale-dependent:

- **Trend scale ($k=1$):** Slow noise schedule with $\beta_t^{(1)} = 0.0001$ to $0.02$ (linear)
- **Seasonal scale ($k=2,3$):** Medium noise schedule with $\beta_t^{(2,3)} = 0.0005$ to $0.05$ (cosine)
- **High-frequency scale ($k=4$):** Fast noise schedule with $\beta_t^{(4)} = 0.001$ to $0.1$ (quadratic)

**Reverse Process:**

The reverse process uses a shared-backbone, scale-specific denoising network:

$$p_\theta(\mathbf{x}_{t-1}^{(k)}|\mathbf{x}_t^{(k)}, \mathbf{s}^{(k)}, \mathbf{c}) = \mathcal{N}(\mathbf{x}_{t-1}^{(k)}; \boldsymbol{\mu}_\theta(\mathbf{x}_t^{(k)}, t, \mathbf{s}^{(k)}, \mathbf{c}), \sigma_t^{(k)}\mathbf{I})$$

where $\mathbf{c}$ represents optional conditioning information and $\mathbf{s}^{(k)}$ is the structural encoding from SEN.

**Denoising Network Architecture:**

We employ a U-Net style architecture with temporal convolutions and cross-attention to structural encodings:

$$\boldsymbol{\mu}_\theta(\mathbf{x}_t^{(k)}, t, \mathbf{s}^{(k)}, \mathbf{c}) = \text{UNet}_k(\mathbf{x}_t^{(k)}, \gamma(t), \mathbf{s}^{(k)}, \mathbf{c})$$

where $\gamma(t)$ is a sinusoidal timestep embedding.

### 2.5 Coarse-to-Fine Generation Strategy

To ensure coherence across scales, we implement a conditional generation strategy where finer scales are conditioned on coarser predictions:

1. **Stage 1:** Generate trend component $\tilde{\mathbf{x}}^{(1)}$ from noise
2. **Stage 2:** Generate seasonal components $\tilde{\mathbf{x}}^{(2)}, \tilde{\mathbf{x}}^{(3)}$ conditioned on $\tilde{\mathbf{x}}^{(1)}$
3. **Stage 3:** Generate high-frequency component $\tilde{\mathbf{x}}^{(4)}$ conditioned on $\sum_{k=1}^3 \tilde{\mathbf{x}}^{(k)}$

The conditioning is implemented through cross-attention in the denoising network and additive guidance:

$$\tilde{\boldsymbol{\epsilon}}_\theta^{(k)} = \boldsymbol{\epsilon}_\theta^{(k)} + \lambda_k \nabla_{\mathbf{x}_t^{(k)}} \log p(\mathbf{x}_t^{(k)}|\sum_{j<k}\tilde{\mathbf{x}}^{(j)})$$

### 2.6 Training Objective

The complete training objective combines diffusion losses across scales with structure preservation terms:

$$\mathcal{L}_{\text{total}} = \sum_{k=1}^K \left[\mathcal{L}_{\text{diff}}^{(k)} + \lambda_{\text{struct}}^{(k)}\mathcal{L}_{\text{struct}}^{(k)}\right] + \lambda_{\text{coherence}}\mathcal{L}_{\text{coherence}}$$

where:

**Diffusion Loss:**
$$\mathcal{L}_{\text{diff}}^{(k)} = \mathbb{E}_{t,\mathbf{x}_0^{(k)},\boldsymbol{\epsilon}}\left[\|\boldsymbol{\epsilon} - \boldsymbol{\epsilon}_\theta(\mathbf{x}_t^{(k)}, t, \mathbf{s}^{(k)})\|^2\right]$$

**Structure Preservation Loss:**
$$\mathcal{L}_{\text{struct}}^{(k)} = \mathcal{L}_{\text{energy}}^{(k)} + \mathcal{L}_{\text{causal}}^{(k)} + \mathcal{L}_{\text{mono}}^{(k)}$$

**Coherence Loss (ensures reconstruction):**
$$\mathcal{L}_{\text{coherence}} = \left\|\mathbf{x} - \sum_{k=1}^K \tilde{\mathbf{x}}^{(k)}\right\|^2$$

### 2.7 Data Collection and Experimental Design

**Datasets:**

We evaluate on diverse scientific time series datasets:

1. **Climate Data:** ERA5 reanalysis (temperature, precipitation) - 100k sequences, length 365 days
2. **Physiological Signals:** PhysioNet ECG database - 50k sequences, 10-second recordings at 250Hz
3. **Energy Systems:** Smart meter data - 75k sequences, hourly consumption over 1 year
4. **Financial Markets:** High-frequency trading data - 200k sequences, minute-level prices
5. **Synthetic Benchmarks:** Controlled multi-scale signals with known ground truth structures

**Baseline Comparisons:**

- TimeGAN (Yoon et al., 2019)
- TTS-GAN (Li et al., 2022)
- DiffStyleTS (Nagda et al., 2025)
- DS-Diffusion (Sun et al., 2025)
- TimeDiff (basic diffusion for time series)
- TIMEMIXER (Wang et al., 2024)

**Evaluation Metrics:**

1. **Generation Quality:**
   - Discriminative Score: Train-on-Synthetic-Test-on-Real (TSTR) accuracy
   - Predictive Score: Train-on-Real-Test-on-Synthetic (TRTS) accuracy
   - Frechet Inception Distance (FID) adapted for time series

2. **Structural Validity:**
   - Constraint Violation Rate (CVR): Percentage of generated samples violating domain constraints
   - Spectral Coherence: Correlation between power spectral densities of real vs. generated data
   - Multi-Scale Entropy: Comparing complexity across temporal scales

3. **Diversity Metrics:**
   - Coverage: Proportion of real data modes captured
   - Inception Score for time series

4. **Computational Efficiency:**
   - Sampling time per sequence
   - Training time and memory footprint

**Implementation Details:**

- **Framework:** PyTorch with custom CUDA kernels for wavelet transforms
- **Hardware:** 4× NVIDIA A100 GPUs
- **Optimization:** AdamW optimizer, learning rate 1e-4 with cosine annealing
- **Training:** 200 epochs with batch size 64, gradient clipping at norm 1.0
- **Diffusion Steps:** $T=1000$ for training, adaptive sampling with 50-250 steps
- **Architecture Details:**
  - Embedding dimension: $d=256$
  - UNet channels: [64, 128, 256, 512]
  - Attention heads: $H=8$
  - Structure encoding dimension: $d_s=128$

### 2.8 Ablation Studies

To validate design choices, we conduct systematic ablation studies:

1. **Scale-specific vs. uniform noise schedules**
2. **Impact of constraint layers** (removing each constraint type)
3. **Coarse-to-fine vs. parallel generation**
4. **Learnable vs. fixed wavelet decomposition**
5. **Effect of number of scales** ($K \in \{2,3,4,5\}$)

## 3. Expected Outcomes & Impact

### Expected Research Outcomes

1. **Superior Generation Quality:** We anticipate achieving 15-25% improvement in discriminative and predictive scores over current state-of-the-art diffusion models (DiffStyleTS, DS-Diffusion) on scientific time series benchmarks, particularly on datasets with strong multi-scale structure.

2. **Guaranteed Constraint Satisfaction:** The differentiable constraint layers should achieve <5% constraint violation rate compared to >40% for baseline methods, enabling deployment in safety-critical applications.

3. **Computational Efficiency:** The hierarchical processing strategy is expected to reduce sampling time by 40-50% compared to uniform diffusion approaches, through:
   - Parallel generation across independent scales
   - Reduced diffusion steps required for stable convergence
   - Efficient wavelet transforms (O(T) complexity)

4. **Interpretable Decomposition:** The learned multi-scale representations should align with domain-known structures (e.g., circadian rhythms in physiological data, seasonal patterns in climate data), validated through spectral analysis and expert evaluation.

5. **Data-Efficient Learning:** By leveraging structural priors, we expect the model to achieve competitive performance with 30-50% less training data compared to structure-agnostic baselines, critical for scientific domains with limited observations.

### Scientific Impact

**Advancement in Structured Probabilistic Inference:**

This research contributes novel methodological advances to the workshop's focus areas:

- **Scaling inference on structured data:** The hierarchical diffusion framework provides a principled approach to scaling generative modeling to long sequences by exploiting temporal structure
- **Encoding domain knowledge:** Differentiable constraint layers offer a general mechanism for incorporating scientific knowledge into deep generative models
- **Multi-modal structured generation:** The framework extends naturally to multivariate time series and hybrid discrete-continuous structures

**Applications in Science and Industry:**

1. **Climate Science:** Generate plausible climate scenarios for risk assessment while preserving physical laws (energy balance, thermodynamic constraints)

2. **Healthcare:** Synthesize physiological signals for medical device testing and privacy-preserving data sharing, with guaranteed clinical validity

3. **Energy Systems:** Create synthetic load profiles for grid planning that respect operational constraints and rare event distributions

4. **Drug Discovery:** Model molecular dynamics trajectories with chemical constraint preservation

5. **Anomaly Detection:** Use high-quality synthetic data to augment training for rare event detection in data-scarce regimes

### Broader Impact

**Reproducibility and Open Science:**
All code, pre-trained models, and experimental protocols will be released open-source, fostering reproducibility and enabling the community to build upon this work.

**Trustworthy AI:**
By prioritizing interpretability and constraint satisfaction, this research contributes to developing trustworthy AI systems for scientific applications where blind application of black-box models is inappropriate.

**Educational Value:**
The explicit decomposition into interpretable scales serves as an educational tool for understanding multi-scale phenomena in data, bridging machine learning and domain sciences.

**Limitations and Future Work:**

While promising, this approach has limitations that suggest future research directions:

- **Constraint specification:** Requires domain expertise to formulate appropriate constraints; future work could explore meta-learning constraints from data
- **Computational overhead:** Structure extraction adds overhead; investigating lightweight alternatives is valuable
- **Extension to irregular sampling:** Current framework assumes regular sampling; adapting to irregularly-sampled series is important for real-world applications

This research represents a significant step toward reliable, interpretable, and efficient generative modeling for structured scientific time series, with the potential to enable new applications where current methods fall short due to insufficient structural awareness.