# Research Proposal: Saliency-Guided Adaptive Neural Operators for Efficient PDE Solving with Localized Complexity

## 1. Title

**AGANO: Adaptive Gumbel-softmax Allocation Neural Operator for Efficient Partial Differential Equation Solving via Saliency-Guided Spectral Mode Allocation**

---

## 2. Introduction

### 2.1 Background

The numerical solution of partial differential equations (PDEs) constitutes a cornerstone of computational science, underpinning simulations in fluid dynamics, climate modeling, materials science, and countless other domains. Traditional numerical methods—finite differences, finite elements, and spectral methods—while mathematically rigorous, often demand prohibitive computational resources when high-resolution solutions are required, particularly for problems exhibiting multi-scale phenomena, sharp gradients, or turbulent behavior.

The emergence of Scientific Machine Learning (SciML) has catalyzed a paradigm shift in PDE solving. Neural operators, particularly the Fourier Neural Operator (FNO) introduced by Li et al. (2020), have demonstrated remarkable capability to learn solution mappings directly in function space, achieving orders-of-magnitude speedups over classical solvers while maintaining competitive accuracy. The FNO's key innovation lies in performing convolutions in Fourier space, where global information can be efficiently captured through a truncated set of spectral modes.

However, a fundamental limitation persists: current neural operator architectures employ fixed, uniform spectral mode allocation regardless of local solution complexity. This design philosophy, while computationally elegant, creates an inherent inefficiency. In regions where solutions are smooth—such as the interior of laminar flow domains—the full complement of spectral modes represents computational waste. Conversely, in regions exhibiting sharp gradients, boundary layers, shocks, or discontinuities, the fixed mode count may prove insufficient to capture critical high-frequency content. Recent benchmarking studies have revealed significant limitations of present architectures precisely in handling high-frequency components critical to turbulent flows and discontinuous solutions.

This inefficiency mirrors a well-understood principle in biological vision systems: the visual cortex does not process all regions of the visual field with equal computational resources. Instead, saliency-driven attention mechanisms concentrate processing power on regions of high information content—edges, motion boundaries, and areas of rapid change. This biological insight suggests a compelling direction for neural operator design.

### 2.2 Research Objectives

This research proposes AGANO (Adaptive Gumbel-softmax Allocation Neural Operator), a novel neural operator architecture that dynamically allocates Fourier spectral modes based on learned solution complexity. Our primary objectives are:

1. **Develop a lightweight complexity detection mechanism** that identifies high-gradient regions from coarse solution estimates with minimal computational overhead (target: ≤2% of total FLOPs).

2. **Design a differentiable mode allocation framework** using Gumbel-softmax transformations that enables end-to-end training while converging to near-discrete mode selection.

3. **Demonstrate significant efficiency gains** achieving either ≥30% L2 error reduction at equal FLOPs or equivalent accuracy with ≥50% fewer FLOPs on PDEs with localized sharp gradients.

4. **Validate the causal mechanism** through systematic ablation studies confirming that adaptive allocation, rather than increased model capacity, drives performance improvements.

### 2.3 Significance

This research addresses a critical gap in the neural operator literature by introducing principled adaptive computation to spectral methods. The significance extends across multiple dimensions:

**Scientific Impact:** Enabling higher-resolution simulations within fixed computational budgets directly advances capabilities in climate modeling, turbulence simulation, and computational fluid dynamics—domains where resolution limitations currently constrain scientific discovery.

**Methodological Innovation:** The integration of saliency-guided attention with spectral neural operators represents a novel architectural paradigm with potential applications beyond PDE solving to any domain requiring adaptive spectral processing.

**Practical Efficiency:** For practitioners deploying neural operators in resource-constrained environments, AGANO offers a pathway to maintain accuracy while reducing computational costs, democratizing access to high-fidelity scientific simulations.

---

## 3. Methodology

### 3.1 Problem Formulation

Consider a PDE of the general form:

$$\mathcal{L}[u](x) = f(x), \quad x \in \Omega \subset \mathbb{R}^d$$

with appropriate boundary conditions on $\partial\Omega$. Our goal is to learn a neural operator $\mathcal{G}_\theta: \mathcal{A} \rightarrow \mathcal{U}$ mapping input functions (initial conditions, forcing terms, coefficients) to solution functions.

The standard FNO parameterizes this mapping through Fourier integral layers:

$$v_{l+1}(x) = \sigma\left(W_l v_l(x) + \mathcal{F}^{-1}\left(R_l \cdot \mathcal{F}(v_l)\right)(x)\right)$$

where $\mathcal{F}$ denotes the Fourier transform, $R_l$ is a learnable spectral weight tensor, and $\sigma$ is a nonlinear activation. Critically, $R_l$ operates on a fixed set of $k_{max}$ modes, truncating higher frequencies uniformly across the domain.

### 3.2 AGANO Architecture

AGANO introduces three key components that transform the fixed-allocation FNO into an adaptive architecture:

#### 3.2.1 Complexity Detector Module

We design a lightweight complexity detector $\mathcal{D}_\phi$ based on MobileNet-style depthwise separable convolutions to minimize computational overhead while maintaining detection accuracy.

**Architecture:** The detector consists of three depthwise separable convolutional blocks:

$$\mathcal{D}_\phi(v) = \text{Conv}_{1\times1} \circ \text{DWConv}_{3\times3} \circ \text{BN} \circ \text{ReLU} \circ [\cdot]^3 (v)$$

**Input:** Coarse solution estimate $\tilde{u}$ from an initial FNO layer or downsampled input.

**Output:** Complexity map $C(x) \in [0,1]^{N_r}$ where $N_r$ is the number of spatial regions (typically $8 \times 8 = 64$ regions for a $256 \times 256$ domain).

**Computational Budget:** The detector is constrained to ≤2% of total inference FLOPs through aggressive channel reduction (16→32→16 channels) and spatial pooling.

**Training Signal:** The complexity detector is trained with auxiliary supervision using ground-truth gradient magnitude maps:

$$\mathcal{L}_{det} = \text{BCE}\left(C(x), \mathbf{1}[\|\nabla u_{true}\| > \tau_g]\right)$$

where $\tau_g$ is a gradient threshold determined by the 75th percentile of gradient magnitudes in the training set.

#### 3.2.2 Gumbel-Softmax Mode Allocation

The complexity scores must be converted to discrete mode allocation decisions while maintaining differentiability for end-to-end training. We employ the Gumbel-softmax relaxation:

**Mode Categories:** We define $K=4$ mode allocation levels: $\{4, 8, 16, 32\}$ modes, representing low to high spectral resolution.

**Allocation Logits:** A small MLP converts complexity scores to allocation logits:

$$\pi_i = \text{MLP}(C_i) \in \mathbb{R}^K$$

**Gumbel-Softmax Sampling:** For each region $i$, we compute soft allocation weights:

$$w_{i,k} = \frac{\exp((\pi_{i,k} + g_k)/\tau)}{\sum_{j=1}^{K}\exp((\pi_{i,j} + g_j)/\tau)}$$

where $g_k \sim \text{Gumbel}(0,1)$ are i.i.d. Gumbel noise samples and $\tau$ is the temperature parameter.

**Temperature Annealing Schedule:** We anneal temperature from $\tau=5.0$ to $\tau=0.1$ over training:

$$\tau(t) = \max(0.1, 5.0 \cdot \exp(-0.001 \cdot t))$$

where $t$ is the training iteration. This schedule ensures smooth optimization early in training while converging to near-discrete allocation.

#### 3.2.3 Adaptive Spectral Convolution

The core innovation lies in modifying the Fourier layer to accept region-dependent mode counts:

**Regional Spectral Decomposition:** We partition the spatial domain into $N_r$ regions and compute regional Fourier transforms:

$$\hat{v}_i = \mathcal{F}_{local}(v \cdot \psi_i)$$

where $\psi_i$ is a smooth partition-of-unity function for region $i$.

**Adaptive Mode Masking:** For each region, we construct a soft mode mask:

$$M_i(k) = \sum_{j=1}^{K} w_{i,j} \cdot \mathbf{1}[|k| \leq m_j]$$

where $m_j \in \{4, 8, 16, 32\}$ are the mode counts for each allocation level.

**Masked Spectral Convolution:**

$$\hat{v}'_i = M_i \odot (R \cdot \hat{v}_i)$$

**Reconstruction:** The output is reconstructed via inverse Fourier transform and summation:

$$v_{out}(x) = \sum_{i=1}^{N_r} \mathcal{F}^{-1}(\hat{v}'_i)(x) \cdot \psi_i(x)$$

### 3.3 Training Procedure

**Multi-Task Loss Function:**

$$\mathcal{L}_{total} = \mathcal{L}_{PDE} + \lambda_{det}\mathcal{L}_{det} + \lambda_{ent}\mathcal{L}_{ent}$$

where:
- $\mathcal{L}_{PDE} = \|u_{pred} - u_{true}\|_2 / \|u_{true}\|_2$ is the relative L2 loss
- $\mathcal{L}_{det}$ is the complexity detector supervision loss
- $\mathcal{L}_{ent} = -\sum_i \sum_k w_{i,k} \log w_{i,k}$ is an entropy regularizer encouraging discrete allocation

**Hyperparameters:** $\lambda_{det} = 0.1$, $\lambda_{ent} = 0.01$ (annealed to 0.1 as temperature decreases).

**Optimizer:** AdamW with learning rate $10^{-3}$, weight decay $10^{-4}$, cosine annealing over 500 epochs.

### 3.4 Experimental Design

#### 3.4.1 Datasets

We evaluate on four PDE families from PDEBench:

1. **Navier-Stokes (2D):** Incompressible flow with Reynolds numbers $Re \in \{100, 1000, 10000\}$, exhibiting vortex shedding and boundary layers.

2. **Burgers' Equation:** 1D and 2D viscous Burgers with shock formation.

3. **Darcy Flow:** Heterogeneous permeability fields with sharp coefficient discontinuities.

4. **Reaction-Diffusion:** Turing patterns with localized reaction fronts.

**Data Splits:** 1000 training / 200 validation / 200 test samples per PDE family.

**Resolutions:** Primary evaluation at $256 \times 256$; generalization tests at $512 \times 512$.

#### 3.4.2 Baselines

1. **FNO (fixed 12 modes):** Standard architecture from Li et al. (2020)
2. **FNO (fixed 32 modes):** High-resolution baseline matching AGANO's maximum modes
3. **Geo-FNO:** Geometry-aware extension
4. **U-FNO:** Multi-scale architecture with U-Net skip connections
5. **AGANO-Uniform:** Ablation with complexity detector but uniform allocation

#### 3.4.3 Evaluation Metrics

**Primary Metrics:**
- **L2 Relative Error:** $\epsilon_{L2} = \|u_{pred} - u_{true}\|_2 / \|u_{true}\|_2$
- **FLOPs per Inference:** Measured via PyTorch profiler
- **Accuracy-per-FLOP Ratio:** $\eta = (1/\epsilon_{L2}) / \text{FLOPs}$

**Secondary Metrics:**
- **Complexity Detector IoU:** Intersection-over-Union with ground-truth gradient maps
- **Allocation Entropy:** $H = -\sum_k w_k \log w_k$ (target: $<0.5$ bits at convergence)
- **Regional Error Distribution:** Error breakdown by complexity region

#### 3.4.4 Statistical Analysis

- **Sample Size:** $n \geq 20$ runs per configuration (power analysis: effect size $d=0.8$, power $=0.8$)
- **Statistical Tests:** Paired t-tests for primary comparisons, ANOVA for multi-factor analysis
- **Reporting:** Mean ± Std Dev [95% CI], Cohen's d effect size, p-values

### 3.5 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

1. **Detector Ablation:** Replace learned detector with (a) random allocation, (b) oracle gradient-based allocation
2. **Gumbel-Softmax Ablation:** Compare with (a) straight-through estimator, (b) REINFORCE gradient
3. **Mode Range Ablation:** Test allocation ranges $\{2,4,8,16\}$ vs $\{4,8,16,32\}$ vs $\{8,16,32,64\}$
4. **Temperature Schedule Ablation:** Compare linear, exponential, and step annealing

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcome (P1):** We anticipate AGANO will achieve ≥30% reduction in L2 relative error compared to FNO baseline at equal FLOPs on PDEs with localized sharp gradients. Alternatively, AGANO should achieve equivalent accuracy with ≥50% fewer FLOPs. Based on preliminary analysis of spectral energy distributions in target PDEs, we expect the largest gains on Navier-Stokes at high Reynolds numbers (40-50% improvement) and Burgers' equation with shocks (35-45% improvement), with more modest gains on Darcy flow (20-30% improvement).

**Secondary Outcomes:**
- **P2:** Complexity detector achieving >90% IoU in localizing high-gradient regions
- **P3:** Allocation entropy converging to <0.5 bits per region at $\tau \leq 0.5$
- **P4:** Cross-PDE generalization maintaining >80% of single-PDE performance

### 4.2 Potential Failure Modes and Mitigations

We acknowledge several scenarios that could lead to hypothesis rejection:

1. **Overhead Exceeds Savings:** If complexity detector overhead exceeds 15% of total FLOPs, net efficiency gains disappear. *Mitigation:* Further architectural compression; shared detector across layers.

2. **Soft Allocation Remains Fuzzy:** If Gumbel-softmax fails to converge to discrete allocation, efficiency gains from mode reduction will be minimal. *Mitigation:* Alternative discretization methods (straight-through estimator with learned temperature).

3. **Complexity-Gradient Decorrelation:** If solution complexity is not well-correlated with gradient magnitude, the detector will misallocate modes. *Mitigation:* Multi-feature complexity detection incorporating curvature and spectral energy.

### 4.3 Broader Impact

**Scientific Computing:** AGANO enables practitioners to achieve higher-fidelity simulations within fixed computational budgets, directly advancing capabilities in climate modeling, aerodynamic design, and materials simulation.

**Methodological Contribution:** The saliency-guided adaptive computation paradigm extends beyond PDEs to any domain requiring spatially-varying spectral resolution, including image processing, signal analysis, and graph neural networks.

**Sustainability:** By reducing computational requirements for equivalent accuracy, AGANO contributes to more sustainable AI practices in scientific computing, reducing energy consumption and carbon footprint of large-scale simulations.

**Reproducibility Commitment:** All code, trained models, and experimental configurations will be released under open-source licenses. We will provide detailed documentation enabling reproduction of all reported results.

### 4.4 Future Directions

Success of AGANO opens several research avenues:

1. **Temporal Adaptation:** Extending adaptive allocation to time-stepping, concentrating computation on time intervals with rapid dynamics.

2. **3D Extension:** Scaling the approach to three-dimensional PDEs where computational savings become even more critical.

3. **Physics-Informed Adaptation:** Incorporating physical constraints (conservation laws, symmetries) into the complexity detection mechanism.

4. **Hardware Co-Design:** Developing specialized accelerators that exploit the sparse, adaptive computation patterns of AGANO.

---

**Word Count:** ~2,150 words