# Research Proposal: Hierarchical Physics-Informed Neural Operators for Million-Particle Molecular Dynamics

## 1. Introduction

### Background

Molecular dynamics (MD) simulations serve as an indispensable tool in computational biology, materials science, and drug discovery, providing atomic-level insights into complex physical and chemical processes. However, the computational cost of traditional MD simulations scales poorly with system size, typically requiring $O(N^2)$ or $O(N \log N)$ operations per timestep for $N$ particles. This limitation severely constrains our ability to simulate biologically and industrially relevant systems—such as entire protein complexes, cellular membranes, or large-scale crystallization processes—that involve millions of particles over microsecond to millisecond timescales.

Recent advances in machine learning force fields (MLFFs) have demonstrated remarkable success in accelerating MD simulations while maintaining near-quantum accuracy for small molecular systems. Frameworks such as chemtrain-deploy have enabled million-atom simulations using neural network potentials, while approaches like BoostMD achieve significant speedups by leveraging temporal correlations. However, critical challenges remain unresolved. Current neural network potentials are typically trained on small systems containing hundreds to thousands of atoms and exhibit systematic degradation when applied to larger scales. This generalization gap arises from accumulated errors, distributional shift, and the absence of hard physical constraints in most architectures.

The fundamental issue lies in the tension between learning flexibility and physical consistency. While neural networks excel at capturing complex potential energy surfaces, they often violate fundamental conservation laws (momentum, energy, angular momentum) that govern physical dynamics. These violations, though small per timestep, accumulate over long trajectories and lead to catastrophic instabilities—unphysical heating, drift, and eventual simulation breakdown.

### Research Objectives

This proposal introduces **Hierarchical Physics-Informed Neural Operators (HiPINO)**, a novel architecture designed to overcome these limitations through three key innovations:

1. **Multi-scale representation learning** that captures both local atomic interactions and long-range collective phenomena through hierarchical coarse-graining
2. **Hard conservation constraint embedding** that guarantees fundamental physical laws by construction, not approximation
3. **Self-correcting dynamics** that detects and rectifies instabilities using physical invariants as supervisory signals

### Significance

Successfully developing HiPINO would represent a paradigm shift in computational molecular science. By enabling stable, accurate simulations of million-particle systems over microsecond timescales with 100-1000× speedup over classical MD, this work would unlock previously intractable applications: simulating entire viral capsids, modeling drug interactions with cellular membranes, and capturing nucleation and crystallization in realistic material samples. Furthermore, the methodological innovations—particularly the hard constraint embedding and error-correcting mechanisms—would provide broadly applicable principles for physics-informed machine learning beyond molecular dynamics.

## 2. Methodology

### 2.1 Overall Architecture

HiPINO consists of three interconnected modules operating in a hierarchical framework:

**Module A: Scale-Adaptive Hierarchical Encoder**
**Module B: Conservation-Preserving Dynamics Predictor**  
**Module C: Error-Correcting Refinement Network**

Given a system of $N$ particles with positions $\mathbf{r} = \{\mathbf{r}_1, ..., \mathbf{r}_N\}$ and velocities $\mathbf{v} = \{\mathbf{v}_1, ..., \mathbf{v}_N\}$, HiPINO learns the mapping:

$$(\mathbf{r}(t), \mathbf{v}(t)) \xrightarrow{\text{HiPINO}} (\mathbf{r}(t+\Delta t), \mathbf{v}(t+\Delta t))$$

### 2.2 Module A: Scale-Adaptive Hierarchical Encoder

To efficiently capture interactions across length scales, we employ a hierarchical clustering strategy with adaptive resolution.

**Hierarchical Clustering**: Particles are organized into $L$ hierarchical levels. At level $\ell = 0$ (finest), each node represents an individual atom. At coarser levels $\ell > 0$, nodes represent clusters of particles:

$$\mathcal{C}^{(\ell)} = \{C_1^{(\ell)}, C_2^{(\ell)}, ..., C_{K_\ell}^{(\ell)}\}$$

where $K_\ell$ decreases with increasing $\ell$. Cluster assignments are computed using a differentiable soft clustering mechanism based on spatial proximity and learned chemical similarity:

$$\alpha_{ij}^{(\ell)} = \text{softmax}\left(-\frac{\|\mathbf{r}_i^{(\ell-1)} - \mathbf{c}_j^{(\ell)}\|^2}{\sigma_\ell^2} + \phi(\mathbf{h}_i^{(\ell-1)}, \mathbf{h}_j^{(\ell)})\right)$$

where $\mathbf{c}_j^{(\ell)}$ are learnable cluster centers, $\sigma_\ell$ is a scale parameter, and $\phi$ is a learned compatibility function.

**Multi-Scale Message Passing**: At each level $\ell$, we perform equivariant message passing:

$$\mathbf{m}_{ij}^{(\ell)} = \phi_m^{(\ell)}\left(\mathbf{h}_i^{(\ell)}, \mathbf{h}_j^{(\ell)}, \|\mathbf{r}_{ij}^{(\ell)}\|, \hat{\mathbf{r}}_{ij}^{(\ell)}\right)$$

$$\mathbf{h}_i^{(\ell)'} = \phi_u^{(\ell)}\left(\mathbf{h}_i^{(\ell)}, \sum_{j \in \mathcal{N}(i)} \mathbf{m}_{ij}^{(\ell)}\right)$$

where $\hat{\mathbf{r}}_{ij} = \mathbf{r}_{ij}/\|\mathbf{r}_{ij}\|$ and $\phi_m, \phi_u$ are SE(3)-equivariant neural networks based on tensor field networks.

**Fourier Neural Operator for Long-Range Effects**: At the coarsest level, we employ a Fourier Neural Operator (FNO) to capture long-range electrostatic and dispersion interactions:

$$\mathbf{H}^{(L)'} = \sigma\left(\mathbf{W}\mathbf{H}^{(L)} + \mathcal{F}^{-1}\left(\mathbf{R}_\theta \cdot \mathcal{F}(\mathbf{H}^{(L)})\right)\right)$$

where $\mathcal{F}$ denotes the Fourier transform, $\mathbf{R}_\theta$ are learnable spectral weights, and $\sigma$ is a nonlinearity.

### 2.3 Module B: Conservation-Preserving Dynamics Predictor

The core innovation of HiPINO lies in encoding conservation laws as hard architectural constraints rather than soft regularization penalties.

**Hamiltonian Structure**: We parameterize the system dynamics through a learned Hamiltonian $H_\theta$:

$$H_\theta(\mathbf{r}, \mathbf{p}) = T(\mathbf{p}) + V_\theta(\mathbf{r})$$

where $T(\mathbf{p}) = \sum_i \frac{\|\mathbf{p}_i\|^2}{2m_i}$ is the kinetic energy and $V_\theta$ is a neural network potential. The equations of motion follow Hamilton's equations:

$$\dot{\mathbf{r}}_i = \frac{\partial H_\theta}{\partial \mathbf{p}_i} = \frac{\mathbf{p}_i}{m_i}, \quad \dot{\mathbf{p}}_i = -\frac{\partial H_\theta}{\partial \mathbf{r}_i} = -\nabla_{\mathbf{r}_i} V_\theta$$

**Momentum Conservation**: We ensure total momentum conservation by constructing forces as pairwise antisymmetric:

$$\mathbf{F}_i = \sum_{j \neq i} \mathbf{f}_{ij}, \quad \text{where} \quad \mathbf{f}_{ij} = -\mathbf{f}_{ji}$$

This is achieved by parameterizing $\mathbf{f}_{ij} = g_\theta(\mathbf{r}_i, \mathbf{r}_j, \mathbf{h}_i, \mathbf{h}_j) \cdot \hat{\mathbf{r}}_{ij}$ where $g_\theta$ is symmetric in its arguments.

**Angular Momentum Conservation**: We employ SE(3)-equivariant networks that produce forces along the interatomic axis $\hat{\mathbf{r}}_{ij}$, automatically satisfying:

$$\sum_i \mathbf{r}_i \times \mathbf{F}_i = 0$$

**Symplectic Integration**: To preserve the Hamiltonian structure during time integration, we use a learned symplectic integrator:

$$\mathbf{p}_{t+\Delta t/2} = \mathbf{p}_t - \frac{\Delta t}{2}\nabla_{\mathbf{r}} V_\theta(\mathbf{r}_t)$$
$$\mathbf{r}_{t+\Delta t} = \mathbf{r}_t + \Delta t \cdot \mathbf{M}^{-1}\mathbf{p}_{t+\Delta t/2}$$
$$\mathbf{p}_{t+\Delta t} = \mathbf{p}_{t+\Delta t/2} - \frac{\Delta t}{2}\nabla_{\mathbf{r}} V_\theta(\mathbf{r}_{t+\Delta t})$$

### 2.4 Module C: Error-Correcting Refinement Network

Even with hard constraints, systematic errors accumulate over long trajectories. We introduce a lightweight correction module that monitors physical invariants and applies corrections.

**Invariant Monitoring**: At each timestep, we compute a set of physical invariants:

$$\mathcal{I} = \{E_{total}, \mathbf{P}_{total}, \mathbf{L}_{total}, T_{kinetic}\}$$

Deviations from expected values trigger the correction mechanism:

$$\delta_E = |E(t) - E(0)|, \quad \delta_P = \|\mathbf{P}(t)\|, \quad \delta_L = \|\mathbf{L}(t) - \mathbf{L}(0)\|$$

**Correction Network**: A small neural network $\psi_\theta$ predicts corrections conditioned on the invariant violations:

$$\Delta \mathbf{v}_i = \psi_\theta(\mathbf{h}_i, \delta_E, \delta_P, \delta_L)$$

The corrections are constrained to preserve conservation laws by projecting onto the null space of the constraint Jacobian.

### 2.5 Training Procedure

**Data Collection**: Training data is generated from classical MD simulations using established force fields (AMBER, CHARMM) and ab initio MD where feasible. We employ a curriculum learning strategy, starting with small systems (1,000 atoms) and progressively increasing to larger systems (100,000+ atoms).

**Loss Function**: The total loss combines multiple objectives:

$$\mathcal{L} = \mathcal{L}_{force} + \lambda_1 \mathcal{L}_{energy} + \lambda_2 \mathcal{L}_{trajectory} + \lambda_3 \mathcal{L}_{distribution}$$

where:
- $\mathcal{L}_{force} = \frac{1}{N}\sum_i \|\mathbf{F}_i^{pred} - \mathbf{F}_i^{true}\|^2$
- $\mathcal{L}_{energy} = |E^{pred} - E^{true}|^2$
- $\mathcal{L}_{trajectory}$ penalizes trajectory divergence over $K$ steps
- $\mathcal{L}_{distribution}$ ensures correct Boltzmann sampling via maximum mean discrepancy

### 2.6 Experimental Design

**Benchmark Systems**:
1. **Protein-membrane systems**: GPCR embedded in lipid bilayer (~500,000 atoms)
2. **Protein folding**: Villin headpiece and larger proteins
3. **Crystallization dynamics**: Lennard-Jones systems and realistic metals
4. **Water systems**: Bulk water up to 1 million molecules

**Evaluation Metrics**:
- **Accuracy**: Force RMSE, energy MAE, radial distribution function (RDF) error
- **Stability**: Maximum stable simulation time, energy drift per nanosecond
- **Efficiency**: Speedup vs. classical MD, GPU memory usage, scaling with system size
- **Physical fidelity**: Conservation law violations, diffusion coefficients, free energy accuracy

**Baselines**: We compare against chemtrain-deploy, BoostMD, NequIP, MACE, and traditional MD packages (GROMACS, LAMMPS).

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Performance**: We anticipate 100-1000× speedup over classical MD while maintaining force accuracy within 5% of reference calculations
2. **Stability**: Stable trajectories exceeding 1 microsecond for million-particle systems without thermostat intervention
3. **Scalability**: Near-linear scaling up to 10 million particles on multi-GPU systems
4. **Generalization**: Models trained on 10,000-atom systems that transfer to million-atom systems with <20% accuracy degradation

### Scientific Impact

HiPINO will enable previously impossible simulations: complete viral assembly, drug permeation through realistic membranes, and large-scale nucleation events. The open-source release of code, trained models, and benchmarks will accelerate research across computational biology and materials science.

### Methodological Impact

The principles of hard constraint embedding and self-correcting dynamics extend beyond MD to any physics-informed machine learning application requiring long-term stability and conservation law preservation, including climate modeling, fluid dynamics, and plasma physics.