# Research Proposal

## Title
Physics-Guided Foundation Models with Learnable Conservation Law Constraints for Multi-Physics Systems

## 1. Introduction

### Background

Foundation models have emerged as transformative tools across machine learning, demonstrating remarkable capabilities in natural language processing, computer vision, and scientific applications. Recent advances have extended these models to physical sciences, with developments such as PDE-FM for partial differential equations, the General Physics Transformer (GPhyT), and specialized models for quantum many-body systems. These models promise to revolutionize scientific computing by learning generalizable representations across diverse physical systems.

However, a fundamental tension exists between the flexibility of foundation models and the rigorous requirements of physical sciences. Physical systems are governed by conservation laws—fundamental principles stating that certain quantities (energy, momentum, mass, charge) remain constant in isolated systems. When foundation models violate these laws, their predictions become physically meaningless, regardless of how well they fit observational data. This is particularly problematic in high-stakes applications such as climate modeling, where energy conservation violations can lead to unphysical temperature drifts, or in molecular dynamics simulations, where momentum conservation is essential for accurate trajectory prediction.

Current approaches to incorporating physics into machine learning fall into two categories. Hard-constraint methods embed physical laws directly into network architectures, ensuring exact conservation but sacrificing the flexibility and transferability that make foundation models powerful. Soft-constraint methods add physics-based penalty terms to loss functions, preserving flexibility but providing only approximate conservation with no guarantees. Neither approach adequately addresses the challenge of building foundation models that are both flexible and physically consistent.

### Research Objectives

This research proposes a novel framework—Physics-Guided Foundation Models with Learnable Conservation Law Constraints (PGFM-LC)—that bridges this gap through three interconnected innovations:

1. **Automatic Conservation Law Discovery**: Develop a neural divergence operator module that identifies conserved quantities directly from simulation data without requiring explicit specification of conservation laws.

2. **Differentiable Constraint Enforcement**: Design projection layers that map foundation model outputs onto the manifold of physically valid solutions while maintaining differentiability for end-to-end training.

3. **Adaptive Constraint Integration**: Create a dynamic weighting mechanism that optimally balances data fidelity with physical consistency during fine-tuning, adapting to different physical regimes.

### Significance

This research addresses a critical need at the intersection of machine learning and physical sciences. By enabling foundation models to respect conservation laws while maintaining their expressive power, PGFM-LC will:

- Enhance scientific trustworthiness of AI predictions in physical sciences
- Improve generalization to out-of-distribution physical regimes where conservation laws provide essential inductive biases
- Reduce data requirements by leveraging physics as a regularization mechanism
- Provide a general framework applicable across multiple physical domains, from fluid dynamics to materials science

## 2. Methodology

### 2.1 Overall Framework Architecture

The PGFM-LC framework augments a pre-trained foundation model $\mathcal{F}_\theta$ with three learnable modules: a Conservation Law Discovery Module (CLDM), a Differentiable Projection Layer (DPL), and an Adaptive Constraint Weighting mechanism (ACW). Given input state $\mathbf{x}_t$ representing a physical system at time $t$, the framework produces physically consistent predictions $\hat{\mathbf{x}}_{t+\Delta t}$ for future states.

The overall forward pass is:
$$\hat{\mathbf{x}}_{t+\Delta t} = \text{DPL}\left(\mathcal{F}_\theta(\mathbf{x}_t), \mathcal{C}(\mathbf{x}_t)\right)$$

where $\mathcal{C}(\mathbf{x}_t)$ represents the discovered conservation constraints evaluated at the current state.

### 2.2 Conservation Law Discovery Module (CLDM)

The CLDM automatically identifies conserved quantities from simulation data using neural divergence operators. For a physical system with state variables $\mathbf{u}(\mathbf{r}, t) \in \mathbb{R}^d$ defined over spatial coordinates $\mathbf{r}$ and time $t$, conservation laws take the general form:

$$\frac{\partial \rho}{\partial t} + \nabla \cdot \mathbf{J} = 0$$

where $\rho$ is a conserved density and $\mathbf{J}$ is the associated flux.

We parameterize both the density $\rho_\phi$ and flux $\mathbf{J}_\psi$ as neural networks:

$$\rho_\phi(\mathbf{u}) = \text{MLP}_\phi(\mathbf{u}), \quad \mathbf{J}_\psi(\mathbf{u}, \nabla\mathbf{u}) = \text{MLP}_\psi([\mathbf{u}, \nabla\mathbf{u}])$$

The CLDM is trained to minimize the conservation residual:

$$\mathcal{L}_{\text{CLDM}} = \mathbb{E}_{(\mathbf{u}, t) \sim \mathcal{D}}\left[\left\|\frac{\partial \rho_\phi}{\partial t} + \nabla \cdot \mathbf{J}_\psi\right\|_2^2\right] + \lambda_{\text{reg}}\mathcal{R}(\phi, \psi)$$

where $\mathcal{D}$ is the training dataset and $\mathcal{R}$ is a regularization term promoting simplicity and functional independence of discovered laws.

To discover multiple independent conservation laws, we employ a neural deflation strategy inspired by prior work. After discovering the first conserved quantity $Q_1 = \int \rho_{\phi_1} d\mathbf{r}$, subsequent quantities are constrained to be functionally independent:

$$\mathcal{L}_{\text{deflation}} = \sum_{i<j} \left|\langle \nabla Q_i, \nabla Q_j \rangle\right|^2$$

This ensures the discovery of a complete set of independent conservation laws.

### 2.3 Differentiable Projection Layer (DPL)

The DPL enforces discovered conservation laws by projecting foundation model outputs onto the constraint manifold. Let $\hat{\mathbf{x}}^{\text{raw}} = \mathcal{F}_\theta(\mathbf{x}_t)$ be the raw foundation model output, and let $\{Q_k\}_{k=1}^K$ be the discovered conserved quantities. The projection solves:

$$\hat{\mathbf{x}}_{t+\Delta t} = \arg\min_{\mathbf{x}} \|\mathbf{x} - \hat{\mathbf{x}}^{\text{raw}}\|_2^2 \quad \text{s.t.} \quad Q_k(\mathbf{x}) = Q_k(\mathbf{x}_t), \; \forall k$$

For linear conservation laws (e.g., mass conservation), this admits a closed-form solution. For the linear constraint $\mathbf{A}\mathbf{x} = \mathbf{b}$, the projection is:

$$\hat{\mathbf{x}}_{t+\Delta t} = \hat{\mathbf{x}}^{\text{raw}} - \mathbf{A}^T(\mathbf{A}\mathbf{A}^T)^{-1}(\mathbf{A}\hat{\mathbf{x}}^{\text{raw}} - \mathbf{b})$$

For nonlinear conservation laws (e.g., energy conservation), we employ an iterative Newton-type projection:

$$\mathbf{x}^{(n+1)} = \mathbf{x}^{(n)} - \mathbf{J}_Q^T(\mathbf{J}_Q\mathbf{J}_Q^T)^{-1}\mathbf{g}(\mathbf{x}^{(n)})$$

where $\mathbf{g}(\mathbf{x}) = [Q_1(\mathbf{x}) - Q_1(\mathbf{x}_t), \ldots, Q_K(\mathbf{x}) - Q_K(\mathbf{x}_t)]^T$ and $\mathbf{J}_Q$ is the Jacobian of the constraint functions.

To maintain differentiability, we unroll a fixed number of Newton iterations and backpropagate through the iterative process using implicit differentiation:

$$\frac{\partial \hat{\mathbf{x}}_{t+\Delta t}}{\partial \theta} = \left(\mathbf{I} - \mathbf{J}_Q^T(\mathbf{J}_Q\mathbf{J}_Q^T)^{-1}\mathbf{J}_Q\right)\frac{\partial \hat{\mathbf{x}}^{\text{raw}}}{\partial \theta}$$

### 2.4 Adaptive Constraint Weighting (ACW)

Different physical regimes may require different balances between data fidelity and constraint enforcement. The ACW module learns this balance dynamically. We define the total loss as:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{data}} + \sum_{k=1}^K \alpha_k(c) \mathcal{L}_{\text{constraint}}^{(k)}$$

where the constraint weights $\alpha_k(c)$ depend on a context embedding $c$ extracted from the input:

$$\alpha_k(c) = \sigma\left(\text{MLP}_{\alpha_k}(c)\right) \cdot \alpha_{\max}$$

Here, $\sigma$ is the sigmoid function and $\alpha_{\max}$ is a hyperparameter controlling maximum constraint strength. The context embedding $c$ captures physical regime information such as Reynolds number in fluid dynamics or temperature in molecular dynamics.

The ACW module is trained jointly with the foundation model fine-tuning, allowing the system to automatically increase constraint weights in regimes where conservation is critical and relax them where data provides sufficient guidance.

### 2.5 Training Procedure

Training proceeds in three stages:

**Stage 1: Conservation Law Discovery**
- Pre-train CLDM on simulation datasets to discover conservation laws
- Use neural deflation to identify $K$ independent conserved quantities
- Validate discovered laws against known physics (energy, momentum, mass)

**Stage 2: Foundation Model Augmentation**
- Initialize with pre-trained foundation model weights $\theta_0$
- Attach DPL with discovered conservation laws
- Initialize ACW weights uniformly

**Stage 3: Joint Fine-tuning**
- Fine-tune entire system end-to-end on target domain data
- Optimize combined objective:
$$\mathcal{L} = \mathcal{L}_{\text{data}} + \sum_k \alpha_k \mathcal{L}_{\text{constraint}}^{(k)} + \beta \mathcal{L}_{\text{CLDM}}$$
- Use gradient clipping and learning rate warmup for stability

### 2.6 Experimental Design

#### Datasets

We will evaluate PGFM-LC on three multi-physics benchmarks:

1. **Incompressible Navier-Stokes (2D/3D)**: Fluid dynamics simulations at varying Reynolds numbers (Re = 100 to 10,000), testing mass and momentum conservation.

2. **Molecular Dynamics**: Lennard-Jones particle systems with 1,000-10,000 particles, testing energy and momentum conservation.

3. **Magnetohydrodynamics (MHD)**: Coupled fluid-electromagnetic simulations testing mass, momentum, energy, and magnetic flux conservation.

Each dataset will include in-distribution test sets and out-of-distribution test sets with shifted physical parameters.

#### Baselines

We will compare against:
- **Vanilla Foundation Model**: Pre-trained model without physics constraints
- **Soft-Constraint PINN**: Foundation model with physics loss penalties
- **Hard-Constraint Architecture**: Physics-embedded architectures (e.g., Hamiltonian Neural Networks)
- **PINN-Proj**: Recent projection-based conservation method
- **ProbConserv**: Probabilistic conservation framework

#### Evaluation Metrics

1. **Prediction Accuracy**: 
   - Relative $L_2$ error: $\epsilon_{L_2} = \|\hat{\mathbf{x}} - \mathbf{x}^*\|_2 / \|\mathbf{x}^*\|_2$
   - Spectral error for multi-scale features

2. **Conservation Violation**:
   - Absolute conservation error: $\Delta Q_k = |Q_k(\hat{\mathbf{x}}_{t+\Delta t}) - Q_k(\mathbf{x}_t)|$
   - Relative conservation drift over long rollouts

3. **Generalization**:
   - Performance degradation on out-of-distribution parameters
   - Zero-shot transfer to unseen physical regimes

4. **Computational Efficiency**:
   - Training time overhead
   - Inference latency comparison

#### Ablation Studies

We will conduct ablations to understand each component's contribution:
- CLDM vs. prescribed conservation laws
- DPL with varying projection iterations
- ACW vs. fixed constraint weights
- Impact of foundation model size and pre-training

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Demonstrated Conservation Compliance**: We expect PGFM-LC to achieve near-exact conservation (relative error < $10^{-6}$) compared to $10^{-2}$ to $10^{-3}$ for soft-constraint methods, while maintaining competitive prediction accuracy.

2. **Improved Generalization**: By leveraging conservation laws as inductive biases, we anticipate 20-40% reduction in prediction error on out-of-distribution test sets compared to vanilla foundation models.

3. **Automatic Law Discovery**: The CLDM should successfully recover known conservation laws (energy, momentum, mass) from data and potentially discover emergent conserved quantities in complex systems.

4. **Computational Efficiency**: The projection-based approach should add minimal overhead (< 15% increase in inference time) compared to the base foundation model.

### Scientific Impact

This research will contribute to both machine learning methodology and physical sciences applications:

**For Machine Learning**:
- Novel framework for incorporating hard constraints into foundation models while maintaining differentiability
- Advances in automatic scientific knowledge discovery through neural divergence operators
- New adaptive mechanisms for balancing data-driven and physics-driven learning

**For Physical Sciences**:
- Trustworthy AI tools for scientific simulation and prediction
- Reduced simulation costs through accelerated surrogate models that respect physics
- Potential discovery of previously unknown conservation laws in complex systems

### Broader Impact

The PGFM-LC framework addresses a fundamental challenge in scientific AI: ensuring that powerful machine learning models respect the physical laws governing natural systems. Success in this research will:

- Build trust in AI-assisted scientific discovery by providing physically meaningful predictions
- Enable application of foundation models in safety-critical domains (climate, energy systems)
- Establish a template for incorporating domain knowledge into large-scale pre-trained models

This work exemplifies the bidirectional nature of ML-physics research: physical principles improve machine learning models, while machine learning enables new approaches to understanding physical systems.