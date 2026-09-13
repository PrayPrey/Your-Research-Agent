# Research Proposal: Neural Coarse-Graining via Hierarchical Variational Autoencoders for Multiscale Molecular Dynamics

## 1. Title

**Hierarchical Variational Autoencoders with Uncertainty-Guided Refinement for Learning Multi-Scale Molecular Dynamics and Bridging the Timescale Gap in Computational Chemistry**

## 2. Introduction

### 2.1 Background

The grand challenge of modeling complex molecular systems lies in the fundamental tension between computational accuracy and accessible timescales. While quantum mechanical simulations provide high-fidelity descriptions of molecular behavior, they are limited to femtosecond timescales and systems containing fewer than a few hundred atoms. Meanwhile, phenomena of practical interest—such as protein folding, catalytic reactions, and materials degradation—occur over microseconds to seconds and involve thousands to millions of atoms. This "timescale gap" represents one of the most significant barriers to in silico discovery in chemistry, materials science, and drug design.

Traditional coarse-graining (CG) methods address this challenge by reducing degrees of freedom, grouping atoms into effective "beads" and deriving simplified interaction potentials. Classical approaches like MARTINI and structure-based models have achieved remarkable success in specific systems but suffer from critical limitations: they require extensive manual parameterization, lack systematic transferability across molecular systems, and often fail to capture essential many-body correlations and entropic effects. Each new molecular system effectively demands a new coarse-graining procedure, limiting their utility for high-throughput computational screening.

Recent advances in machine learning offer a promising path forward. Deep learning models have demonstrated unprecedented capabilities in learning complex representations from high-dimensional data, and variational autoencoders (VAEs) provide a principled probabilistic framework for dimensionality reduction. However, existing ML approaches for molecular simulation face significant challenges: they often operate at a single resolution, lack mechanisms for hierarchical scale bridging, provide no guarantees of thermodynamic consistency, and offer limited uncertainty quantification to guide adaptive refinement.

### 2.2 Research Objectives

This research proposes a novel framework—**Hierarchical Variational Autoencoders for Multiscale Molecular Dynamics (HVAE-MMD)**—that addresses these limitations through three primary objectives:

1. **Develop a hierarchical architecture** that learns multiple levels of coarse-grained representations simultaneously, from atomic to mesoscale, with explicit enforcement of physical constraints and thermodynamic consistency across scales.

2. **Design scale-bridging dynamics modules** that learn effective equations of motion at each hierarchical level, trained to reproduce statistical properties and dynamics from fine-scale simulations while remaining computationally efficient.

3. **Implement uncertainty-guided adaptive refinement** that dynamically determines when and where fine-scale simulations are necessary, enabling optimal allocation of computational resources while maintaining overall accuracy.

### 2.3 Significance

The successful development of HVAE-MMD would represent a significant advance toward universal AI methods for scale transition, directly addressing the workshop's core mission. The framework's potential impact includes:

- **Accelerating materials discovery**: Enabling rapid in silico screening of catalyst candidates and novel materials by bridging quantum mechanical accuracy with mesoscale dynamics, potentially reducing the time and cost of materials development by orders of magnitude.

- **Advancing biological simulation**: Making long-timescale simulations of protein folding, membrane dynamics, and drug-target interactions computationally tractable, facilitating rational drug design and understanding of biological mechanisms.

- **Establishing transferability**: Creating learned coarse-graining procedures that can generalize across molecular families, reducing the need for system-specific parameterization and enabling high-throughput computational experiments.

- **Methodological contributions**: Advancing the state-of-the-art in hierarchical representation learning, physics-informed neural networks, and uncertainty quantification for scientific machine learning, with potential applications beyond molecular simulation.

## 3. Methodology

### 3.1 Data Collection and Preparation

**Training Data Generation**: We will construct a diverse molecular dynamics dataset spanning multiple systems and scales:

1. **Small organic molecules** (100-500 atoms): All-atom MD simulations using classical force fields (AMBER, CHARMM) for 100-500 ns, providing ground truth for validation. Systems will include drug-like molecules, solvent systems, and simple catalysts.

2. **Peptides and small proteins** (500-5000 atoms): Explicit solvent simulations of 10-20 different peptide sequences ranging from 10-50 residues, with trajectories of 50-100 ns each.

3. **Polymer systems** (1000-10000 atoms): Simulations of polymer melts and solutions to test scaling to larger, more complex systems.

4. **Ab initio reference data**: For select systems, we will generate short (1-10 ps) but highly accurate quantum mechanical/molecular mechanical (QM/MM) trajectories to anchor the finest scale of our hierarchy.

**Data preprocessing**: Trajectories will be aligned, centered, and augmented with rotational and translational symmetries. We will extract multi-scale features including atomic positions, residue center-of-mass coordinates, and domain-level descriptors.

### 3.2 HVAE-MMD Architecture

#### 3.2.1 Multi-Resolution Hierarchical Encoder

The encoder maps atomic configurations to a hierarchy of latent representations at $L$ different scales:

$$\mathbf{x}^{(0)} \xrightarrow{E_1} \mathbf{z}^{(1)} \xrightarrow{E_2} \mathbf{z}^{(2)} \xrightarrow{E_3} \cdots \xrightarrow{E_L} \mathbf{z}^{(L)}$$

where $\mathbf{x}^{(0)} \in \mathbb{R}^{N \times 3}$ represents $N$ atomic positions, and $\mathbf{z}^{(l)} \in \mathbb{R}^{N_l \times d_l}$ represents $N_l$ coarse-grained particles at level $l$ with feature dimension $d_l$.

Each encoder $E_l$ is implemented as an equivariant graph neural network (EGNN) to preserve rotational and translational symmetries:

$$q_{\phi_l}(\mathbf{z}^{(l)}|\mathbf{z}^{(l-1)}) = \mathcal{N}(\boldsymbol{\mu}_l(\mathbf{z}^{(l-1)}), \boldsymbol{\Sigma}_l(\mathbf{z}^{(l-1)}))$$

where $\boldsymbol{\mu}_l$ and $\boldsymbol{\Sigma}_l$ are outputs of the EGNN. The graph structure at level $l$ is determined by a learned coarsening operation that groups particles from level $l-1$ based on spatial proximity and chemical similarity.

**Coarsening Operation**: We employ a differentiable clustering approach:

$$C_l = \text{softmax}(\mathbf{A}^{(l)} \mathbf{W}_l^T / \tau)$$

where $\mathbf{A}^{(l)} \in \mathbb{R}^{N_{l-1} \times d_{l-1}}$ are node features at level $l-1$, $\mathbf{W}_l \in \mathbb{R}^{N_l \times d_{l-1}}$ are learnable cluster centers, and $\tau$ is a temperature parameter. The assignment matrix $C_l \in \mathbb{R}^{N_{l-1} \times N_l}$ determines which fine-scale particles belong to each coarse-grained particle.

#### 3.2.2 Multi-Resolution Hierarchical Decoder

The decoder reconstructs fine-scale configurations from coarse-grained latent representations through a top-down generative process:

$$p_{\theta}(\mathbf{x}^{(0)}|\mathbf{z}^{(1:L)}) = p_{\theta_1}(\mathbf{x}^{(0)}|\mathbf{z}^{(1)}) \prod_{l=2}^{L} p_{\theta_l}(\mathbf{z}^{(l-1)}|\mathbf{z}^{(l)})$$

Each conditional distribution $p_{\theta_l}(\mathbf{z}^{(l-1)}|\mathbf{z}^{(l)})$ is modeled using equivariant graph neural networks that "refine" coarse representations by adding fine-scale details:

$$p_{\theta_l}(\mathbf{z}^{(l-1)}|\mathbf{z}^{(l)}) = \mathcal{N}(\boldsymbol{\mu}_{D_l}(\mathbf{z}^{(l)}), \boldsymbol{\Sigma}_{D_l}(\mathbf{z}^{(l)}))$$

The decoder uses the transpose of the coarsening assignment matrix to distribute coarse-grained information to fine-scale particles.

#### 3.2.3 Scale-Bridging Dynamics Modules

At each hierarchical level $l$, we learn effective dynamics that predict temporal evolution in the latent space. The dynamics module consists of:

**Hamiltonian Neural Network (HNN) Component**: To ensure energy conservation and symplectic structure, we parameterize dynamics using learned Hamiltonian functions:

$$\mathcal{H}_l(\mathbf{q}^{(l)}, \mathbf{p}^{(l)}) = \text{NN}_{\psi_l}(\mathbf{q}^{(l)}, \mathbf{p}^{(l)})$$

where $\mathbf{q}^{(l)}$ and $\mathbf{p}^{(l)}$ are generalized positions and momenta at level $l$. The equations of motion are:

$$\frac{d\mathbf{q}^{(l)}}{dt} = \frac{\partial \mathcal{H}_l}{\partial \mathbf{p}^{(l)}}, \quad \frac{d\mathbf{p}^{(l)}}{dt} = -\frac{\partial \mathcal{H}_l}{\partial \mathbf{q}^{(l)}}$$

**Dissipative Correction**: Real molecular systems exhibit dissipation and thermal fluctuations. We augment the Hamiltonian dynamics with learned dissipative forces and stochastic terms:

$$d\mathbf{z}^{(l)} = \mathbf{f}_{\text{Ham}}(\mathbf{z}^{(l)})dt + \mathbf{f}_{\text{diss}}(\mathbf{z}^{(l)})dt + \boldsymbol{\Sigma}_{\text{noise}}(\mathbf{z}^{(l)})d\mathbf{W}_t$$

where $\mathbf{f}_{\text{Ham}}$ derives from the Hamiltonian, $\mathbf{f}_{\text{diss}}$ is a learned dissipative force, and $d\mathbf{W}_t$ is Brownian noise with learned state-dependent variance $\boldsymbol{\Sigma}_{\text{noise}}$.

**Free Energy Correction**: To maintain thermodynamic consistency, we learn scale-dependent free energy corrections:

$$F^{(l)}(\mathbf{z}^{(l)}) = -k_B T \log \int p(\mathbf{z}^{(l-1)}|\mathbf{z}^{(l)}) e^{-U^{(l-1)}(\mathbf{z}^{(l-1)})/k_B T} d\mathbf{z}^{(l-1)}$$

This is approximated using a neural network trained to match free energy profiles computed from fine-scale simulations.

#### 3.2.4 Uncertainty Quantification and Adaptive Refinement

To determine when coarse-grained predictions are reliable, we implement Bayesian uncertainty quantification using ensembles and dropout variational inference:

**Epistemic Uncertainty**: We maintain an ensemble of $K$ HVAE-MMD models and compute prediction variance:

$$\sigma^2_{\text{epistemic}}(\mathbf{z}^{(l)}_t) = \frac{1}{K}\sum_{k=1}^{K} \|\mathbf{z}^{(l)}_{t+\Delta t,k} - \bar{\mathbf{z}}^{(l)}_{t+\Delta t}\|^2$$

**Aleatoric Uncertainty**: The learned covariance $\boldsymbol{\Sigma}_{D_l}$ from the decoder directly provides aleatoric uncertainty estimates.

**Refinement Criterion**: When total uncertainty exceeds a threshold:

$$\sigma^2_{\text{total}} = \sigma^2_{\text{epistemic}} + \text{tr}(\boldsymbol{\Sigma}_{D_l}) > \tau_{\text{refine}}$$

we trigger refinement by either: (a) performing a short fine-scale simulation from the current state, or (b) switching to a finer hierarchical level for subsequent predictions.

### 3.3 Training Procedure

The complete HVAE-MMD is trained end-to-end using a multi-objective loss function:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{ELBO}} + \lambda_{\text{dyn}}\mathcal{L}_{\text{dynamics}} + \lambda_{\text{phys}}\mathcal{L}_{\text{physics}} + \lambda_{\text{cons}}\mathcal{L}_{\text{consistency}}$$

**Evidence Lower Bound (ELBO)**:
$$\mathcal{L}_{\text{ELBO}} = \mathbb{E}_{q_{\phi}}\left[\log p_{\theta}(\mathbf{x}^{(0)}|\mathbf{z}^{(1:L)})\right] - \sum_{l=1}^{L} \beta_l \text{KL}(q_{\phi_l}(\mathbf{z}^{(l)}|\mathbf{z}^{(l-1)}) \| p(\mathbf{z}^{(l)}))$$

where $\beta_l$ are scale-dependent KL weights implementing $\beta$-VAE regularization.

**Dynamics Loss**: Measures prediction accuracy of temporal evolution at all scales:
$$\mathcal{L}_{\text{dynamics}} = \sum_{l=1}^{L} \sum_{t=1}^{T-1} \|\mathbf{z}^{(l)}_{t+1} - \hat{\mathbf{z}}^{(l)}_{t+1}(\mathbf{z}^{(l)}_t)\|^2$$

**Physics-Informed Loss**: Enforces physical constraints:
$$\mathcal{L}_{\text{physics}} = \mathcal{L}_{\text{energy}} + \mathcal{L}_{\text{force}} + \mathcal{L}_{\text{momentum}}$$

where $\mathcal{L}_{\text{energy}}$ penalizes energy drift, $\mathcal{L}_{\text{force}}$ matches force distributions, and $\mathcal{L}_{\text{momentum}}$ enforces momentum conservation.

**Cross-Scale Consistency Loss**: Ensures predictions are consistent across hierarchical levels:
$$\mathcal{L}_{\text{consistency}} = \sum_{l=1}^{L-1} \|\mathcal{C}_l(\hat{\mathbf{z}}^{(l)}_{t+1}) - \hat{\mathbf{z}}^{(l+1)}_{t+1}\|^2$$

where $\mathcal{C}_l$ is the coarsening operation from level $l$ to $l+1$.

**Training Strategy**: We employ a curriculum learning approach:
1. **Phase 1** (50 epochs): Train reconstruction (ELBO only) with increasing $\beta$ annealing
2. **Phase 2** (100 epochs): Add dynamics loss with short time predictions (1-10 steps)
3. **Phase 3** (100 epochs): Add physics and consistency losses, extend to longer predictions
4. **Phase 4** (50 epochs): Fine-tune with adaptive refinement in the loop

Optimization uses Adam with learning rate $10^{-4}$, reduced by factor of 0.5 when validation loss plateaus.

### 3.4 Experimental Design and Validation

**Experimental Systems**: We will validate HVAE-MMD on three benchmark systems of increasing complexity:

1. **Alanine dipeptide in water**: A well-studied system with known metastable states, providing ground truth for free energy landscapes and transition kinetics.

2. **Protein G (56 residues)**: Tests ability to capture protein folding dynamics and multi-domain behavior at longer timescales.

3. **Zeolite-confined alkanes**: Represents materials science application relevant to catalysis, testing transferability across different chemical environments.

**Evaluation Metrics**:

1. **Reconstruction Quality**:
   - Root mean square deviation (RMSD) between reconstructed and true atomic positions
   - Structural similarity metrics (TM-score for proteins)

2. **Thermodynamic Accuracy**:
   - Free energy profile error: $\text{MAE}(F_{\text{pred}}, F_{\text{true}})$
   - Radial distribution function (RDF) comparison using Kullback-Leibler divergence
   - Heat capacity and other ensemble averages

3. **Dynamic Properties**:
   - Mean square displacement (MSD) curves
   - Autocorrelation functions for key observables
   - Transition rate constants between metastable states
   - Diffusion coefficients

4. **Computational Efficiency**:
   - Speedup factor: $S = T_{\text{reference}}/T_{\text{HVAE-MMD}}$ for equivalent simulation time
   - Wall-clock time to reach specified accuracy thresholds
   - Scaling with system size

5. **Transferability**:
   - Performance on held-out molecular systems with similar chemistry
   - Few-shot adaptation: accuracy after fine-tuning on limited data from new systems

6. **Uncertainty Calibration**:
   - Calibration plots comparing predicted uncertainty to actual errors
   - Correlation between uncertainty and refinement trigger frequency

**Baseline Comparisons**: We will compare against:
- Classical CG methods (MARTINI, custom structure-based models)
- Single-scale ML approaches (SchNet, DimeNet for force fields)
- Recent learned CG methods (CGnets, RelativeNets)
- Multi-scale methods without hierarchical VAE structure

**Ablation Studies**: To validate design choices:
- Importance of hierarchical structure vs. single-level VAE
- Contribution of each loss component
- Impact of uncertainty-guided refinement vs. fixed-resolution prediction
- Effect of number of hierarchical levels on accuracy/efficiency trade-off

### 3.5 Implementation Details

The framework will be implemented in PyTorch with PyTorch Geometric for graph operations. Key implementation specifications:

- **Hardware**: Training on 4× NVIDIA A100 GPUs (40GB), inference deployable on single GPU or CPU
- **Model sizes**: Encoders/decoders with 4-6 layers, 128-256 hidden dimensions per layer
- **Batch processing**: Mini-batches of 32 molecular configurations, trajectory segments of 100-500 steps
- **Parallelization**: Data parallelism across GPUs, with gradient accumulation for effective larger batch sizes
- **Code release**: All code, trained models, and datasets will be released open-source under MIT license

## 4. Expected Outcomes & Impact

### 4.1 Technical Outcomes

**Quantitative Performance Targets**:
- Achieve 100-1000× speedup compared to all-atom MD while maintaining RMSD < 2 Å for structural predictions
- Reproduce free energy profiles within 1 kcal/mol accuracy for well-studied benchmark systems
- Demonstrate stable simulations extending 2-3 orders of magnitude beyond training trajectory lengths
- Show successful transfer learning with <10% performance degradation on related molecular systems using <10% additional training data

**Methodological Contributions**:
- First hierarchical VAE framework explicitly designed for multi-scale molecular dynamics with provable thermodynamic consistency
- Novel uncertainty quantification approach for adaptive resolution switching in molecular simulation
- Theoretical analysis of approximation quality and convergence properties as a function of hierarchy depth
- Open-source software framework enabling researchers to apply HVAE-MMD to diverse molecular systems

### 4.2 Scientific Impact

**Enabling New Science**:
- **Catalyst discovery**: Enable computational screening of thousands of catalyst candidates for CO₂ reduction, hydrogen production, and other reactions critical for sustainable energy
- **Protein engineering**: Make microsecond-scale simulations of protein folding and conformational changes routine, accelerating rational protein design
- **Materials design**: Facilitate exploration of polymer degradation mechanisms, membrane transport properties, and other long-timescale phenomena in materials

**Broader Methodological Impact**:
The hierarchical representation learning and uncertainty-guided refinement strategies developed for molecular systems have potential applicability to other multi-scale problems:
- Climate modeling (molecular → mesoscale → global)
- Turbulent fluid dynamics (Kolmogorov cascade)
- Astrophysical simulations (particle → stellar → galactic scales)

### 4.3 Validation of Core Workshop Themes

This proposal directly addresses the workshop's central challenge of building "universal AI methods that would be able to find efficient and accurate approximations" for scale transition:

- **Universality**: The architecture is agnostic to specific chemical systems, learning appropriate coarse-graining from data rather than requiring manual parameterization
- **Efficiency**: Hierarchical structure enables orders-of-magnitude computational savings
- **Accuracy**: Physics-informed constraints and adaptive refinement maintain fidelity to underlying fine-scale dynamics
- **Practical applicability**: Demonstrated on high-impact problems (catalysis, protein folding) with clear paths to real-world deployment

### 4.4 Limitations and Future Directions

**Known Limitations**:
- Training requires substantial amounts of fine-scale simulation data, which may be prohibitively expensive for some quantum-level calculations
- Generalization to completely novel chemical scaffolds (beyond interpolation in training data) remains challenging
- Theoretical guarantees on long-time stability and ergodicity are limited

**Future Extensions**:
- Integration with active learning to efficiently explore chemical space and minimize required training data
- Incorporation of experimental data (spectroscopy, scattering) as additional constraints to reduce reliance on simulations
- Extension to reactive systems with bond breaking/forming through graph restructuring
- Coupling with symbolic regression to extract interpretable coarse-grained force fields from learned representations

### 4.5 Timeline and Milestones

- **Months 1-3**: Data generation, baseline implementations, initial single-scale VAE experiments
- **Months 4-6**: Development of hierarchical encoder/decoder architecture, preliminary training
- **Months 7-9**: Implementation of dynamics modules and physics-informed losses
- **Months 10-12**: Uncertainty quantification and adaptive refinement mechanisms
- **Months 13-15**: Comprehensive validation studies, transferability experiments
- **Months 16-18**: Scaling to larger systems, application to catalysis case studies, paper writing

This research proposal presents a comprehensive approach to learning multi-scale molecular dynamics through hierarchical variational autoencoders. By combining principled probabilistic modeling, physics-informed machine learning, and uncertainty-guided adaptive computation, HVAE-MMD promises to make significant progress toward the workshop's vision of universal AI methods for scale transition in complex systems.