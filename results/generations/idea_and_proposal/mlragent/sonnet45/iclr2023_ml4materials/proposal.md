# Research Proposal: Periodic-Aware Diffusion Models for Crystal Structure Generation with Coherent Boundary Conditions

## 1. Title

**Periodic-Aware Diffusion Models for Crystal Structure Generation with Coherent Boundary Conditions**

## 2. Introduction

### 2.1 Background

Materials discovery represents one of the most critical bottlenecks in addressing global challenges such as renewable energy, energy storage, and catalysis. Traditional methods for discovering new crystalline materials rely heavily on computationally expensive density functional theory (DFT) calculations combined with human intuition, limiting the exploration of the vast chemical space. While machine learning has revolutionized molecular design and protein structure prediction, the application to crystalline materials faces unique challenges that distinguish it from these domains.

Crystalline materials, unlike isolated molecules, exist in the condensed phase and must be represented under periodic boundary conditions (PBC). This periodicity means that a crystal structure extends infinitely through the repetition of a unit cell, introducing fundamental challenges for both representation learning and generative modeling. Current generative approaches adapted from molecular generation—including variational autoencoders (VAEs), generative adversarial networks (GANs), and diffusion models—typically treat periodicity as an afterthought, leading to boundary discontinuities where atoms at cell edges exhibit inconsistent interactions with their periodic images. These artifacts result in physically invalid structures with high formation energies and poor synthesizability.

Recent advances in diffusion models have shown remarkable success in generating molecular structures and other complex data modalities. Works such as DiffCrysGen and MiAD have begun adapting diffusion frameworks to crystal generation, demonstrating the potential of score-based approaches. However, these methods still struggle with maintaining coherent boundary conditions throughout the denoising process, and the joint optimization of atomic positions and lattice parameters remains challenging. The coupling between fractional coordinates and lattice vectors—where small changes in lattice parameters can dramatically affect interatomic distances—is not adequately captured by existing approaches that treat these components separately or sequentially.

### 2.2 Research Objectives

This research proposes to develop a novel diffusion framework that natively incorporates periodic symmetry into the generative process. The primary objectives are:

1. **Design PBC-equivariant denoising networks** that utilize periodic convolutions on toroidal lattice representations, ensuring atoms at cell boundaries maintain physically consistent interactions with their periodic images throughout the diffusion process.

2. **Develop a joint diffusion framework** for fractional atomic coordinates and lattice parameters that captures their coupled evolution, avoiding the inconsistencies that arise from treating these components independently.

3. **Integrate space group symmetry priors** into the sampling process to guide generation toward experimentally realizable structures while maintaining the ability to explore novel configurations.

4. **Validate the approach** on large-scale crystallographic databases and demonstrate improved performance in generating diverse, stable, and synthesizable crystal structures compared to existing methods.

### 2.3 Significance

This research addresses a fundamental gap in the application of generative models to materials discovery. By solving the periodic boundary condition problem, we enable the reliable generation of novel crystal structures that could accelerate the discovery of materials for critical applications including:

- **Battery materials**: Novel cathode and anode compositions with improved energy density and cycle life
- **Catalysts**: Multi-component systems with optimized active sites for chemical transformations
- **Structural materials**: Compounds with enhanced mechanical properties and thermal stability

The proposed framework will provide the foundation for subsequent property-guided optimization, enabling inverse design workflows where crystal structures are generated to meet specific target properties. Moreover, the methodological advances in handling periodic systems will benefit other domains requiring periodic representations, such as polymer modeling and surface catalysis.

## 3. Methodology

### 3.1 Data Collection and Preprocessing

We will utilize two primary crystallographic databases:

1. **Materials Project**: Containing over 140,000 inorganic crystal structures with computed properties including formation energies, band gaps, and elastic constants.

2. **Inorganic Crystal Structure Database (ICSD)**: Providing experimentally determined structures for validation and ensuring our model learns physically realizable configurations.

**Preprocessing steps**:
- Standardize crystal structures to primitive cells using spglib
- Normalize lattice parameters to a reference scale
- Convert Cartesian coordinates to fractional coordinates
- Filter structures based on data quality (removing duplicates, partial occupancies > 5%, and structures with formation energy > 1 eV/atom above hull)
- Augment training data through space group operations to increase diversity

### 3.2 Mathematical Framework

#### 3.2.1 Crystal Structure Representation

A crystal structure $\mathcal{C}$ is represented as a tuple:

$$\mathcal{C} = (\mathbf{L}, \{\mathbf{f}_i, z_i\}_{i=1}^N)$$

where:
- $\mathbf{L} \in \mathbb{R}^{3 \times 3}$ is the lattice matrix with column vectors defining the unit cell
- $\mathbf{f}_i \in [0,1)^3$ are fractional coordinates of atom $i$
- $z_i \in \{1, ..., 118\}$ is the atomic number
- $N$ is the number of atoms in the unit cell

The Cartesian position of atom $i$ and its periodic images are given by:
$$\mathbf{x}_i^{(\mathbf{n})} = \mathbf{L}(\mathbf{f}_i + \mathbf{n})$$
where $\mathbf{n} \in \mathbb{Z}^3$ indexes periodic images.

#### 3.2.2 Periodic-Aware Diffusion Process

We define a joint diffusion process on both fractional coordinates and lattice parameters. The forward process adds Gaussian noise:

$$q(\mathbf{F}_t, \mathbf{L}_t | \mathbf{F}_0, \mathbf{L}_0) = \mathcal{N}(\mathbf{F}_t; \sqrt{\bar{\alpha}_t}\mathbf{F}_0, (1-\bar{\alpha}_t)\mathbf{I}) \cdot \mathcal{N}(\mathbf{L}_t; \sqrt{\bar{\beta}_t}\mathbf{L}_0, (1-\bar{\beta}_t)\mathbf{I})$$

where $\mathbf{F}_t \in \mathbb{R}^{N \times 3}$ stacks all fractional coordinates, and separate noise schedules $\{\bar{\alpha}_t\}$ and $\{\bar{\beta}_t\}$ control the diffusion rates for coordinates and lattice parameters respectively.

To ensure fractional coordinates remain in $[0,1)^3$, we apply periodic wrapping:
$$\mathbf{f}_i^{\text{wrapped}} = \text{mod}(\mathbf{f}_i, 1)$$

The reverse process learns to denoise:
$$p_\theta(\mathbf{F}_{t-1}, \mathbf{L}_{t-1} | \mathbf{F}_t, \mathbf{L}_t, \mathbf{Z}) = \mathcal{N}(\boldsymbol{\mu}_\theta(\mathbf{F}_t, \mathbf{L}_t, \mathbf{Z}, t), \boldsymbol{\Sigma}_\theta)$$

where $\mathbf{Z}$ encodes atomic numbers and $\theta$ represents network parameters.

#### 3.2.3 PBC-Equivariant Neural Architecture

The denoising network $\epsilon_\theta$ must respect periodic boundary conditions. We design a graph neural network operating on a periodic graph $\mathcal{G}_{\text{periodic}}$ where:

1. **Node features**: Each atom $i$ has features $\mathbf{h}_i^{(0)} = [\text{embed}(z_i), \mathbf{f}_i^t]$

2. **Edge construction**: Include edges between atom $i$ and all atoms $j$ (including periodic images) within cutoff radius $r_c$:
$$\mathcal{E} = \{(i,j,\mathbf{n}) : \|\mathbf{L}_t(\mathbf{f}_j^t - \mathbf{f}_i^t + \mathbf{n})\| < r_c, \mathbf{n} \in \mathbb{Z}^3\}$$

3. **Periodic message passing**: At layer $\ell$:
$$\mathbf{m}_{ij}^{(\ell)} = \phi_{\text{msg}}^{(\ell)}(\mathbf{h}_i^{(\ell)}, \mathbf{h}_j^{(\ell)}, \mathbf{r}_{ij}^{\mathbf{n}}, \|\mathbf{r}_{ij}^{\mathbf{n}}\|)$$
$$\mathbf{h}_i^{(\ell+1)} = \phi_{\text{update}}^{(\ell)}(\mathbf{h}_i^{(\ell)}, \sum_{j,\mathbf{n}} \mathbf{m}_{ij}^{(\ell)})$$

where $\mathbf{r}_{ij}^{\mathbf{n}} = \mathbf{L}_t(\mathbf{f}_j^t - \mathbf{f}_i^t + \mathbf{n})$ is the periodic displacement vector.

4. **Lattice encoding**: Lattice parameters are encoded using Gram matrix features:
$$\mathbf{G} = \mathbf{L}^T\mathbf{L} = \begin{pmatrix} a^2 & ab\cos\gamma & ac\cos\beta \\ ab\cos\gamma & b^2 & bc\cos\alpha \\ ac\cos\beta & bc\cos\alpha & c^2 \end{pmatrix}$$

The network predicts noise for both components:
$$(\epsilon_{\mathbf{F}}, \epsilon_{\mathbf{L}}) = \epsilon_\theta(\mathbf{F}_t, \mathbf{L}_t, \mathbf{Z}, t)$$

#### 3.2.4 Training Objective

The training loss combines coordinate and lattice denoising:

$$\mathcal{L}_{\text{simple}} = \mathbb{E}_{t, \mathbf{F}_0, \mathbf{L}_0, \boldsymbol{\epsilon}_F, \boldsymbol{\epsilon}_L}\left[\lambda_F\|\boldsymbol{\epsilon}_F - \epsilon_{\mathbf{F}}(\mathbf{F}_t, \mathbf{L}_t, \mathbf{Z}, t)\|^2 + \lambda_L\|\boldsymbol{\epsilon}_L - \epsilon_{\mathbf{L}}(\mathbf{F}_t, \mathbf{L}_t, \mathbf{Z}, t)\|^2\right]$$

We augment this with auxiliary losses:

1. **Boundary consistency loss**: Penalize differences in predicted interactions for atoms and their periodic images
$$\mathcal{L}_{\text{boundary}} = \sum_{i,j,\mathbf{n}\neq\mathbf{0}} \|\mathbf{m}_{ij}^{\mathbf{0}} - \mathbf{m}_{ij}^{\mathbf{n}}\|^2$$

2. **Space group consistency loss**: Encourage adherence to symmetry operations
$$\mathcal{L}_{\text{sym}} = \sum_{g \in G} \|\epsilon_\theta(g\cdot\mathcal{C}_t) - g\cdot\epsilon_\theta(\mathcal{C}_t)\|^2$$

where $G$ is a subset of common space groups and $g\cdot\mathcal{C}_t$ applies symmetry operation $g$.

Total training objective:
$$\mathcal{L} = \mathcal{L}_{\text{simple}} + \lambda_b\mathcal{L}_{\text{boundary}} + \lambda_s\mathcal{L}_{\text{sym}}$$

### 3.3 Symmetry-Guided Sampling

During generation, we incorporate space group priors through:

1. **Conditional generation**: Sample space group $s \sim p(s)$ from the empirical distribution, then generate structures conditioned on $s$ by enforcing symmetry constraints during denoising.

2. **Projection step**: After each denoising step, project coordinates onto the nearest symmetric configuration for the target space group using:
$$\mathbf{F}_{t-1}^{\text{sym}} = \arg\min_{\mathbf{F}' \in \text{Sym}(s)} \|\mathbf{F}' - \mathbf{F}_{t-1}\|^2$$

3. **Wyckoff position initialization**: Initialize the diffusion process from high-symmetry Wyckoff positions for the target space group.

### 3.4 Experimental Design and Evaluation

#### 3.4.1 Baselines

We compare against:
- **CDVAE**: Crystal Diffusion VAE (Xie et al., 2021)
- **DiffCrysGen**: Score-based diffusion without explicit PBC handling
- **MiAD**: Mirage atom diffusion model
- **Random structure search**: Using USPEX for comparison

#### 3.4.2 Evaluation Metrics

**Structural validity**:
- **Boundary coherence score**: Average force discontinuity at cell boundaries
$$\text{BCS} = \frac{1}{N}\sum_i \|\mathbf{F}_i - \mathbf{F}_i^{\text{periodic image}}\|$$
- **Minimum interatomic distance**: Percentage of structures with $d_{\min} > 0.5$ Å
- **Space group classification accuracy**: Using spglib

**Physical plausibility**:
- **Formation energy distribution**: Compare DFT-computed energies of generated structures against training distribution
- **Energy above hull**: Fraction of structures within 0.1 eV/atom of convex hull
- **Phonon stability**: Absence of imaginary frequencies (sampled subset)

**Diversity and novelty**:
- **Coverage**: Fraction of chemical space covered using SOAP distance metrics
- **Novelty score**: Average minimum distance to nearest training structure
- **Polymorph generation**: Number of distinct stable phases per composition

**Synthesizability**:
- **SMOMAT score**: Using learned synthesizability classifier
- **Experimental match rate**: Percentage matching known ICSD structures for held-out compositions

#### 3.4.3 Experimental Protocol

1. **Training**: 
   - 80/10/10 train/validation/test split by composition
   - Train for 500K iterations with batch size 64
   - AdamW optimizer with learning rate $10^{-4}$
   - Cosine annealing schedule

2. **Generation experiments**:
   - **Unconditional generation**: Sample 10K structures, evaluate all metrics
   - **Compositional constraint**: Generate structures for specific chemical systems (Li-Ni-Co-O for batteries, transition metal oxides for catalysis)
   - **Property-guided**: Incorporate classifier guidance for target band gaps and formation energies

3. **Ablation studies**:
   - Remove periodic convolutions (replace with standard message passing)
   - Independent vs. joint diffusion for coordinates and lattice
   - Effect of space group conditioning
   - Impact of boundary consistency loss

4. **Computational validation**:
   - Perform DFT relaxations on top 1000 generated structures using VASP
   - Compute formation energies and compare to predicted stability
   - Calculate synthesizability indicators

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Technical achievements**:
1. **10x reduction in boundary artifacts** as measured by boundary coherence score, demonstrating that the PBC-equivariant architecture successfully maintains consistent interactions across cell boundaries.

2. **20% improvement in valid structure generation rate** compared to baseline methods, with >95% of generated structures having physically reasonable interatomic distances and no overlapping atoms.

3. **Discovery of novel metastable phases**: Generation of 100+ computationally stable structures (within 0.05 eV/atom above hull) for compositions not present in training data, validated through DFT calculations.

4. **Enhanced diversity**: Achieve 2x higher coverage of SOAP descriptor space while maintaining physical plausibility, enabling exploration of underrepresented structural motifs.

5. **Improved synthesizability**: 30% higher SMOMAT scores on average compared to structures generated by methods without space group guidance, indicating better alignment with experimentally realizable materials.

**Scientific contributions**:
- First diffusion model architecture specifically designed for periodic systems with mathematically rigorous treatment of boundary conditions
- Demonstration that joint diffusion of coordinates and lattice parameters captures their coupling more effectively than sequential or independent approaches
- Open-source implementation and trained models to enable broader community adoption
- Curated dataset of 10K+ generated novel structures with DFT-validated stabilities for future benchmarking

### 4.2 Impact

**Immediate impact**:
- Provide materials researchers with a reliable generative tool for exploring chemical spaces difficult to access through traditional structure search methods
- Accelerate high-throughput screening campaigns by generating diverse candidate structures that can be filtered computationally before expensive synthesis attempts
- Enable inverse design workflows where the model can be extended with property guidance to generate structures meeting specific target criteria

**Long-term impact**:
- **Energy storage**: Discover novel battery electrode materials with improved capacity and ionic conductivity through targeted generation in Li/Na-containing systems
- **Catalysis**: Generate complex multi-component oxide surfaces with optimized active site configurations for reactions like CO₂ reduction and ammonia synthesis
- **Sustainability**: Identify earth-abundant alternatives to materials currently requiring rare or toxic elements

**Broader scientific impact**:
- Establish design principles for machine learning models on periodic systems applicable to polymers, surfaces, and other condensed-phase materials
- Demonstrate the value of embedding physical constraints (periodicity, symmetry) directly into neural architectures rather than post-hoc corrections
- Contribute to the growing ecosystem of ML tools for materials discovery, complementing property prediction models and structure optimization methods

**Methodological contributions**:
The periodic-aware diffusion framework developed in this work will serve as a foundation for:
- Multi-fidelity approaches combining fast ML potentials with DFT validation
- Active learning loops for targeted materials discovery
- Integration with experimental synthesis robots for automated materials synthesis-characterization cycles

By solving the fundamental challenge of periodic boundary conditions in generative models, this research removes a critical bottleneck in ML-driven materials discovery and opens new avenues for accelerating the development of materials addressing society's most pressing challenges in energy, environment, and sustainability.