# Research Proposal: Physics-Informed Neural Operators with Attention-Based Multiscale Decomposition for Turbulent Flow Simulation

## 1. Introduction

### Background

Turbulent flows, governed by the Navier-Stokes equations, represent one of the most fundamental yet computationally challenging problems in fluid dynamics and computational physics. The inherent multiscale nature of turbulence—spanning from large-scale coherent structures down to the Kolmogorov microscale—demands extraordinarily fine spatial and temporal resolution for accurate numerical simulation. Direct Numerical Simulation (DNS), which resolves all scales of turbulence, requires computational resources that scale as $O(Re^3)$ where $Re$ denotes the Reynolds number, making high-Reynolds-number simulations computationally prohibitive for practical engineering applications.

The emergence of Scientific Machine Learning (SciML) has opened new avenues for accelerating computational fluid dynamics. Neural operators, particularly Fourier Neural Operators (FNOs), have demonstrated remarkable success in learning solution mappings for partial differential equations. However, existing approaches face critical limitations when applied to turbulent flows: (1) they struggle to capture the energy cascade across scales accurately, (2) they lack mechanisms to adaptively focus computational resources on dynamically important regions such as vortices, shear layers, and boundary layers, and (3) they often fail to preserve essential physical invariants like the Kolmogorov energy spectrum scaling.

Recent advances in physics-informed neural networks (PINNs) and neural operators have shown promise in addressing some of these challenges. Works such as PT-PINNs and LESnets have demonstrated that incorporating physical constraints can improve prediction accuracy without extensive training data. However, these methods still struggle with the fundamental challenge of multiscale dynamics in fully developed turbulence, where energy transfer between scales must be accurately captured to maintain physical fidelity.

### Research Objectives

This research proposes the development of a **Multiscale Attention Neural Operator (MANO)** that synergistically combines three key innovations:

1. **Hierarchical Wavelet-Based Decomposition**: Decompose turbulent flow fields into scale-specific components using learnable wavelet lifting schemes, enabling explicit treatment of different spectral bands.

2. **Scale-Aware Attention Mechanisms**: Implement adaptive attention modules that dynamically allocate model capacity across spatial regions and scales based on local flow complexity.

3. **Physics-Constrained Spectral Energy Loss**: Enforce the Kolmogorov energy cascade through a differentiable spectral energy loss that preserves the $k^{-5/3}$ inertial range scaling.

### Significance

This research addresses a critical gap at the intersection of machine learning and computational fluid dynamics. The proposed MANO framework has the potential to:

- Enable real-time high-fidelity turbulence simulations for applications in climate modeling, aerospace design, and weather prediction
- Provide interpretable predictions through attention maps that highlight dynamically important flow regions
- Establish a principled framework for incorporating multiscale physics into neural operators
- Achieve 10-100× computational speedup over DNS while maintaining spectral accuracy

## 2. Methodology

### 2.1 Problem Formulation

We consider the incompressible Navier-Stokes equations in their dimensionless form:

$$\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\nabla p + \frac{1}{Re}\nabla^2\mathbf{u} + \mathbf{f}$$

$$\nabla \cdot \mathbf{u} = 0$$

where $\mathbf{u}(\mathbf{x}, t)$ is the velocity field, $p(\mathbf{x}, t)$ is the pressure, $Re$ is the Reynolds number, and $\mathbf{f}$ represents external forcing. Our goal is to learn an operator $\mathcal{G}_\theta: \mathbf{u}(\cdot, t) \mapsto \mathbf{u}(\cdot, t+\Delta t)$ that advances the solution in time while preserving multiscale turbulent dynamics.

### 2.2 Wavelet-Based Multiscale Decomposition

The first component of MANO employs a learnable wavelet lifting scheme to decompose the velocity field into scale-specific components. Given an input field $\mathbf{u}$, we apply a $J$-level wavelet decomposition:

$$\mathbf{u} = \sum_{j=0}^{J} \mathbf{u}^{(j)}$$

where $\mathbf{u}^{(j)}$ represents the component at scale $j$, with $j=0$ corresponding to the coarsest scale. The decomposition is implemented through learnable lifting operators:

$$\mathbf{u}^{(j)}_{low} = \mathbf{u}^{(j)} - \mathcal{P}_\theta^{(j)}(\mathbf{u}^{(j)}_{high})$$
$$\mathbf{u}^{(j)}_{high} = \mathcal{U}_\theta^{(j)}(\mathbf{u}^{(j)}_{low}) + \mathbf{d}^{(j)}$$

Here, $\mathcal{P}_\theta^{(j)}$ and $\mathcal{U}_\theta^{(j)}$ are the learnable predict and update operators, and $\mathbf{d}^{(j)}$ captures the detail coefficients at scale $j$. Unlike fixed wavelet bases, these operators are parameterized as small convolutional networks, allowing the decomposition to adapt to the specific statistics of turbulent flows.

### 2.3 Scale-Aware Attention Module

The core innovation of MANO is the scale-aware attention mechanism that processes each scale component with adaptive computational focus. For each scale $j$, we compute attention weights that identify regions requiring enhanced modeling:

$$\alpha^{(j)}(\mathbf{x}) = \text{softmax}\left(\frac{Q^{(j)}(\mathbf{u}^{(j)}) \cdot K^{(j)}(\mathbf{u}^{(j)})^T}{\sqrt{d_k}} + B^{(j)}(\mathbf{x})\right)$$

where $Q^{(j)}$, $K^{(j)}$ are query and key projections, $d_k$ is the key dimension, and $B^{(j)}(\mathbf{x})$ is a physics-informed positional bias computed from local flow characteristics:

$$B^{(j)}(\mathbf{x}) = \lambda_1 \|\nabla \times \mathbf{u}^{(j)}\| + \lambda_2 \|\mathbf{S}^{(j)}\| + \lambda_3 Q^{(j)}_{criterion}$$

Here, $\|\nabla \times \mathbf{u}^{(j)}\|$ is the vorticity magnitude, $\|\mathbf{S}^{(j)}\|$ is the strain rate magnitude, and $Q^{(j)}_{criterion}$ is the Q-criterion for vortex identification. The parameters $\lambda_1, \lambda_2, \lambda_3$ are learned during training.

The attended features are then processed through scale-specific neural operator blocks:

$$\hat{\mathbf{u}}^{(j)} = \mathcal{F}_\theta^{(j)}\left(\sum_{\mathbf{x}'} \alpha^{(j)}(\mathbf{x}, \mathbf{x}') V^{(j)}(\mathbf{u}^{(j)}(\mathbf{x}'))\right)$$

where $\mathcal{F}_\theta^{(j)}$ is a Fourier neural operator layer operating in the spectral domain at scale $j$.

### 2.4 Cross-Scale Interaction Module

Turbulent energy cascade involves nonlinear interactions between scales. We model these interactions through a cross-scale attention mechanism:

$$\mathbf{c}^{(j)} = \sum_{k \neq j} \beta^{(j,k)} \cdot \mathcal{T}_\theta^{(j,k)}(\hat{\mathbf{u}}^{(k)})$$

where $\beta^{(j,k)}$ are learned cross-scale coupling coefficients and $\mathcal{T}_\theta^{(j,k)}$ are scale-transfer operators implemented as spectral convolutions:

$$\mathcal{T}_\theta^{(j,k)}(\hat{\mathbf{u}}^{(k)}) = \mathcal{F}^{-1}\left(W_\theta^{(j,k)} \cdot \mathcal{F}(\hat{\mathbf{u}}^{(k)})\right)$$

The final scale component prediction incorporates both the scale-specific update and cross-scale interactions:

$$\tilde{\mathbf{u}}^{(j)} = \hat{\mathbf{u}}^{(j)} + \gamma^{(j)} \mathbf{c}^{(j)}$$

### 2.5 Physics-Constrained Spectral Energy Loss

A critical requirement for turbulent flow prediction is preservation of the energy spectrum. We enforce the Kolmogorov $-5/3$ scaling through a differentiable spectral energy loss. The energy spectrum is computed as:

$$E(k) = \frac{1}{2} \sum_{k \leq |\mathbf{k}| < k+1} |\hat{\mathbf{u}}(\mathbf{k})|^2$$

where $\hat{\mathbf{u}}(\mathbf{k})$ is the Fourier transform of the velocity field. Our spectral energy loss combines three components:

$$\mathcal{L}_{spectral} = \mathcal{L}_{spectrum} + \mu_1 \mathcal{L}_{cascade} + \mu_2 \mathcal{L}_{dissipation}$$

The spectrum matching loss ensures the predicted spectrum matches the target:

$$\mathcal{L}_{spectrum} = \int_{k_{min}}^{k_{max}} \left(\log E_{pred}(k) - \log E_{target}(k)\right)^2 dk$$

The cascade loss enforces the $-5/3$ scaling in the inertial range:

$$\mathcal{L}_{cascade} = \int_{k_\eta}^{k_L} \left(\frac{d \log E_{pred}(k)}{d \log k} + \frac{5}{3}\right)^2 dk$$

where $k_\eta$ and $k_L$ are the Kolmogorov and integral scale wavenumbers.

The dissipation loss ensures proper energy dissipation at small scales:

$$\mathcal{L}_{dissipation} = \left|\epsilon_{pred} - \epsilon_{target}\right|, \quad \epsilon = 2\nu \int k^2 E(k) dk$$

### 2.6 Complete Training Objective

The total loss function combines data fidelity with physics constraints:

$$\mathcal{L}_{total} = \mathcal{L}_{data} + \lambda_{PDE}\mathcal{L}_{PDE} + \lambda_{spectral}\mathcal{L}_{spectral} + \lambda_{div}\mathcal{L}_{div}$$

where:
- $\mathcal{L}_{data} = \|\mathbf{u}_{pred} - \mathbf{u}_{target}\|_2^2$ is the data reconstruction loss
- $\mathcal{L}_{PDE}$ enforces the Navier-Stokes residual
- $\mathcal{L}_{div} = \|\nabla \cdot \mathbf{u}_{pred}\|_2^2$ enforces incompressibility

### 2.7 Experimental Design

**Datasets**: We will evaluate MANO on three benchmark turbulent flow datasets:
1. **Forced isotropic turbulence**: 3D periodic domain at $Re_\lambda = 100-500$, generated via DNS using a pseudo-spectral code on $512^3$ grids
2. **Turbulent channel flow**: Wall-bounded turbulence at $Re_\tau = 180-590$ from the Johns Hopkins Turbulence Database
3. **Decaying homogeneous turbulence**: Temporal evolution of unforced turbulence to test long-term stability

**Baselines**: We will compare against:
- Fourier Neural Operator (FNO)
- U-Net based neural surrogates
- LESnets (physics-informed neural operator)
- Traditional LES with dynamic Smagorinsky model

**Evaluation Metrics**:
1. **Relative $L^2$ error**: $\epsilon_{L^2} = \|\mathbf{u}_{pred} - \mathbf{u}_{ref}\|_2 / \|\mathbf{u}_{ref}\|_2$
2. **Spectral accuracy**: Mean squared error of energy spectrum in log-space
3. **Cascade preservation**: Deviation from $-5/3$ slope in inertial range
4. **Structure functions**: Accuracy of second and third-order velocity structure functions
5. **Computational speedup**: Wall-clock time comparison with DNS
6. **Interpretability**: Correlation of attention weights with known turbulent structures (vortices, shear layers)

**Training Protocol**: Models will be trained using the AdamW optimizer with cosine annealing learning rate schedule, starting at $10^{-3}$ and decaying to $10^{-6}$ over 500 epochs. We employ gradient clipping with max norm 1.0 and mixed-precision training for efficiency.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Computational Efficiency**: We anticipate achieving 10-100× speedup over DNS while maintaining less than 5% relative error in velocity field predictions and less than 10% error in energy spectrum across all resolved scales.

2. **Spectral Accuracy**: The physics-constrained spectral loss is expected to preserve the Kolmogorov $-5/3$ scaling within 2% deviation across the inertial range, a significant improvement over existing neural operators that typically show 10-20% deviation.

3. **Interpretable Predictions**: Attention maps will provide physically meaningful visualizations, with high attention weights correlating strongly (Pearson $r > 0.8$) with vorticity magnitude and Q-criterion, enabling domain experts to understand and trust model predictions.

4. **Generalization**: The multiscale architecture is expected to generalize across Reynolds numbers within a factor of 5 of training conditions without retraining, addressing a key limitation of current approaches.

### Scientific Impact

This research will establish a new paradigm for incorporating multiscale physics into neural operators, with immediate applications in:

- **Climate Modeling**: Enabling high-resolution turbulence parameterization in ocean and atmospheric models
- **Aerospace Engineering**: Real-time aerodynamic analysis for design optimization
- **Energy Systems**: Improved modeling of turbulent combustion and heat transfer

The interpretability provided by attention mechanisms addresses a critical barrier to adoption of machine learning methods in scientific computing, fostering trust and enabling scientific discovery through visualization of learned flow physics.

### Broader Impact

By dramatically reducing the computational cost of turbulent flow simulation, MANO will democratize access to high-fidelity CFD, enabling researchers with limited computational resources to conduct studies previously restricted to supercomputing centers. The open-source release of our code and pretrained models will further accelerate adoption and reproducibility in the scientific community.