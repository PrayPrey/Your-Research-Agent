# Research Proposal: Periodic Equivariant Diffusion Models for Crystal Structure Generation with Compositional Constraints

## 1. Introduction

### Background

The discovery of novel materials underpins solutions to humanity's most pressing challenges, from renewable energy systems and advanced batteries to clean water technologies and carbon capture. Traditional materials discovery relies on labor-intensive experimental synthesis and characterization, often guided by chemical intuition or high-throughput computational screening. While density functional theory (DFT) calculations have accelerated this process, the vast chemical space of possible crystal structures—estimated to exceed $10^{100}$ configurations—remains largely unexplored. Machine learning offers a transformative paradigm for navigating this space efficiently.

Recent advances in geometric deep learning have demonstrated remarkable success in molecular modeling, exemplified by AlphaFold's protein structure prediction and generative models for drug discovery. However, materials modeling presents fundamentally distinct challenges. Unlike molecules with well-defined boundaries, crystalline materials exhibit periodic boundary conditions where atoms interact with infinite replicas of themselves across unit cell boundaries. This periodicity, combined with strict compositional requirements such as charge neutrality and stoichiometric ratios, creates unique modeling obstacles that molecular-focused approaches cannot directly address.

Current generative approaches for crystal structures have made significant progress. Diffusion models, in particular, have emerged as powerful frameworks for structure generation due to their ability to model complex distributions through iterative denoising. Notable works include vector field-oriented diffusion models that jointly consider atomic positions and lattice parameters, and symmetry-preserving approaches like SymmCD that explicitly incorporate crystallographic symmetry. However, existing methods face critical limitations: they often treat lattice parameters and atomic positions as decoupled entities, struggle to enforce compositional constraints during generation (relying instead on post-hoc rejection sampling), and fail to maintain physical densities throughout the diffusion process.

### Research Objectives

This research proposes **CrystalFlow**, a novel periodic SE(3)-equivariant diffusion model designed to address these fundamental challenges through three interconnected innovations:

1. **Develop a wrapped Gaussian diffusion process** operating in fractional coordinates that inherently respects periodic boundary conditions, eliminating artifacts from coordinate discontinuities at unit cell boundaries.

2. **Design a differentiable constraint module** that guides the reverse diffusion process to enforce charge balance, target stoichiometry, and other compositional requirements without sacrificing generation diversity.

3. **Establish a hierarchical coupling mechanism** between lattice deformation and atomic positions that maintains physically reasonable densities and structural coherence throughout generation.

### Significance

This research addresses a critical gap in computational materials science by providing a principled framework for generating physically plausible, chemically feasible crystal structures. Successful development of CrystalFlow would:

- Accelerate materials discovery by generating synthesizable candidate structures for targeted applications
- Reduce computational waste from generating invalid or unstable structures
- Enable inverse design of materials with specified compositional and functional requirements
- Provide a foundation for property-conditioned generation in energy storage, catalysis, and semiconductor applications

## 2. Methodology

### 2.1 Problem Formulation

A crystal structure $\mathcal{C}$ is defined by the tuple $(\mathbf{L}, \mathbf{X}, \mathbf{A})$ where:
- $\mathbf{L} \in \mathbb{R}^{3 \times 3}$ represents the lattice matrix with column vectors $\mathbf{a}, \mathbf{b}, \mathbf{c}$
- $\mathbf{X} = \{\mathbf{x}_1, ..., \mathbf{x}_N\}$ with $\mathbf{x}_i \in [0, 1)^3$ represents fractional coordinates of $N$ atoms
- $\mathbf{A} = \{a_1, ..., a_N\}$ with $a_i \in \{1, ..., K\}$ represents atomic species from $K$ element types

Our goal is to learn a generative distribution $p_\theta(\mathbf{L}, \mathbf{X}, \mathbf{A})$ that produces valid crystal structures satisfying compositional constraints $\mathcal{G}$.

### 2.2 Wrapped Gaussian Diffusion in Fractional Coordinates

To respect periodic boundary conditions, we perform diffusion directly in fractional coordinate space using a wrapped Gaussian process. For fractional coordinates $\mathbf{x} \in [0, 1)^3$, the forward diffusion process is defined as:

$$q(\mathbf{x}_t | \mathbf{x}_0) = \mathcal{W}(\mathbf{x}_t; \mathbf{x}_0, \beta_t \mathbf{I})$$

where $\mathcal{W}$ denotes the wrapped normal distribution on the 3-torus $\mathbb{T}^3$:

$$\mathcal{W}(\mathbf{x}; \boldsymbol{\mu}, \boldsymbol{\Sigma}) = \sum_{\mathbf{k} \in \mathbb{Z}^3} \mathcal{N}(\mathbf{x} + \mathbf{k}; \boldsymbol{\mu}, \boldsymbol{\Sigma})$$

In practice, we truncate this sum to $|\mathbf{k}|_\infty \leq 2$ for computational efficiency while maintaining accuracy for typical noise levels.

The score function for wrapped Gaussians is computed as:

$$\nabla_{\mathbf{x}} \log \mathcal{W}(\mathbf{x}; \boldsymbol{\mu}, \sigma^2\mathbf{I}) = \frac{\sum_{\mathbf{k}} (\boldsymbol{\mu} - \mathbf{x} - \mathbf{k}) \cdot \mathcal{N}(\mathbf{x} + \mathbf{k}; \boldsymbol{\mu}, \sigma^2\mathbf{I})}{\sigma^2 \sum_{\mathbf{k}} \mathcal{N}(\mathbf{x} + \mathbf{k}; \boldsymbol{\mu}, \sigma^2\mathbf{I})}$$

For lattice parameters, we parameterize $\mathbf{L}$ through its Cholesky decomposition to ensure positive definiteness and apply standard Gaussian diffusion in log-space for lattice lengths and bounded diffusion for angles.

### 2.3 Periodic SE(3)-Equivariant Score Network

The score network $\mathbf{s}_\theta(\mathbf{L}_t, \mathbf{X}_t, \mathbf{A}_t, t)$ must be equivariant to periodic translations and rotations of the entire crystal. We construct this using a periodic equivariant graph neural network (PEGNN).

**Graph Construction**: For a crystal with fractional coordinates $\mathbf{X}$ and lattice $\mathbf{L}$, we construct a multi-graph where edges connect atoms within a cutoff radius $r_c$ considering periodic images:

$$\mathcal{E} = \{(i, j, \mathbf{k}) : \|\mathbf{L}(\mathbf{x}_j + \mathbf{k} - \mathbf{x}_i)\| < r_c, \mathbf{k} \in \{-1, 0, 1\}^3\}$$

**Message Passing**: Each layer $l$ updates node features $\mathbf{h}_i^{(l)}$ and coordinate predictions through:

$$\mathbf{m}_{ij}^{(l)} = \phi_m\left(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, \|\mathbf{r}_{ij}\|, e(\mathbf{r}_{ij}), t\right)$$

$$\mathbf{h}_i^{(l+1)} = \phi_h\left(\mathbf{h}_i^{(l)}, \sum_{(j,\mathbf{k}) \in \mathcal{N}(i)} \mathbf{m}_{ij}^{(l)}\right)$$

$$\Delta \mathbf{x}_i^{(l)} = \sum_{(j,\mathbf{k}) \in \mathcal{N}(i)} \phi_x(\mathbf{m}_{ij}^{(l)}) \cdot \frac{\mathbf{r}_{ij}}{\|\mathbf{r}_{ij}\| + \epsilon}$$

where $\mathbf{r}_{ij} = \mathbf{L}(\mathbf{x}_j + \mathbf{k} - \mathbf{x}_i)$ is the displacement vector, $e(\cdot)$ denotes radial basis function encodings, and $\phi_m, \phi_h, \phi_x$ are learnable MLPs.

### 2.4 Constraint-Guided Sampling

We incorporate compositional constraints through a differentiable guidance mechanism during reverse diffusion. Let $\mathcal{G}(\mathbf{A})$ represent a constraint function that measures violation of compositional requirements:

$$\mathcal{G}(\mathbf{A}) = \lambda_1 \mathcal{G}_{\text{charge}}(\mathbf{A}) + \lambda_2 \mathcal{G}_{\text{stoich}}(\mathbf{A})$$

**Charge Neutrality**: Using predicted oxidation states $o_i$ for species $a_i$:
$$\mathcal{G}_{\text{charge}}(\mathbf{A}) = \left(\sum_{i=1}^N o_{a_i}\right)^2$$

**Stoichiometry**: For target composition ratios $\{r_k\}_{k=1}^K$:
$$\mathcal{G}_{\text{stoich}}(\mathbf{A}) = \sum_{k=1}^K \left(\frac{n_k}{N} - r_k\right)^2$$

where $n_k = \sum_i \mathbb{1}[a_i = k]$.

During reverse diffusion, we modify the sampling step with guidance:

$$\mathbf{A}_{t-1} = \text{SoftCategorical}\left(\mathbf{p}_\theta(\mathbf{A}_{t-1}|\mathbf{A}_t) - \gamma_t \nabla_{\mathbf{A}} \mathcal{G}(\mathbf{A}_t)\right)$$

where $\gamma_t$ is a time-dependent guidance strength that increases as $t \to 0$.

### 2.5 Hierarchical Lattice-Atom Coupling

To maintain physical densities throughout generation, we introduce correlated noise schedules between lattice and atomic components. Define the volume $V = \det(\mathbf{L})$ and density $\rho = N/V$. We parameterize coupled noise as:

$$\beta_t^{\text{lattice}} = \beta_t \cdot (1 + \alpha \cdot f(\rho_t))$$

$$\beta_t^{\text{atoms}} = \beta_t \cdot (1 - \alpha \cdot f(\rho_t))$$

where $f(\rho) = \tanh((\rho - \rho_{\text{target}})/\sigma_\rho)$ encourages density toward physically reasonable values and $\alpha$ controls coupling strength.

### 2.6 Training Procedure

**Dataset**: We use the Materials Project database containing approximately 150,000 experimentally validated crystal structures. We apply standard preprocessing: removing structures with >200 atoms per unit cell, filtering for charge-balanced compositions, and splitting 80/10/10 for train/validation/test.

**Loss Function**: The training objective combines denoising score matching across all components:

$$\mathcal{L} = \mathbb{E}_{t, \mathcal{C}_0, \epsilon}\left[\omega_L \|\mathbf{s}_\theta^L - \nabla \log q(\mathbf{L}_t|\mathbf{L}_0)\|^2 + \omega_X \|\mathbf{s}_\theta^X - \nabla \log q(\mathbf{X}_t|\mathbf{X}_0)\|^2 + \omega_A \text{CE}(\mathbf{p}_\theta^A, \mathbf{A}_0)\right]$$

where $\omega_L, \omega_X, \omega_A$ are loss weights and CE denotes cross-entropy for discrete species prediction.

**Implementation Details**: 
- PEGNN with 8 layers, hidden dimension 256, 64 radial basis functions
- Cutoff radius $r_c = 8$ Å
- Adam optimizer with learning rate $10^{-4}$, cosine annealing
- Batch size 32, trained for 500 epochs on 4 NVIDIA A100 GPUs

### 2.7 Evaluation Metrics

We evaluate CrystalFlow using comprehensive metrics:

1. **Validity Rate**: Percentage of generated structures passing SMACT charge neutrality checks and having positive formation energies from pre-trained MEGNet predictions.

2. **Uniqueness**: Percentage of distinct structures using StructureMatcher with tolerances (ltol=0.2, stol=0.3, angle_tol=5).

3. **Coverage**: Earth Mover's Distance between property distributions (density, formation energy) of generated vs. test set structures.

4. **Novelty**: Percentage of valid structures not matching any training examples.

5. **Synthesizability Score**: Predicted synthesizability using trained classifiers on ICSD-matched structures.

**Baselines**: We compare against CDVAE, DiffCSP, SymmCD, and CrysBFN using identical evaluation protocols.

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate CrystalFlow will achieve:

1. **>90% validity rate** for generated structures, significantly exceeding current state-of-the-art methods (~70-85%)

2. **Near-perfect constraint satisfaction** (<5% violation rate) for charge neutrality and specified stoichiometry

3. **Improved property distribution matching** with >30% reduction in EMD compared to baselines

4. **Demonstration of novel stable compositions** validated through DFT calculations, particularly targeting lithium-ion conductor and photovoltaic absorber chemistries

### Scientific Impact

This research will advance the field through:

- **Theoretical contributions**: A principled framework for periodic equivariant generative modeling with constraint satisfaction
- **Methodological innovations**: Wrapped Gaussian diffusion and hierarchical coupling mechanisms applicable beyond crystals
- **Practical tools**: Open-source implementation enabling materials researchers to generate candidate structures for specific applications

### Broader Impact

Successful development of CrystalFlow will accelerate discovery of materials for clean energy technologies. By generating synthesizable candidates with targeted compositions, we can reduce the experimental trial-and-error cycle from years to months. The constraint-guided framework generalizes to other domains requiring structured generation under physical laws, including molecular design, protein engineering, and metamaterial optimization.