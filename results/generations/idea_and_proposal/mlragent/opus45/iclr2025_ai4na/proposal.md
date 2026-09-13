# Research Proposal: Multi-Scale Geometric Foundation Model for RNA Tertiary Structure Prediction

## 1. Introduction

### Background

Ribonucleic acid (RNA) plays fundamental roles in cellular processes, from encoding genetic information to catalyzing biochemical reactions and regulating gene expression. Understanding RNA function critically depends on knowledge of its three-dimensional (3D) tertiary structure, which determines how RNA molecules interact with proteins, small molecules, and other nucleic acids. With the emergence of RNA-based therapeutics, including mRNA vaccines and RNA interference drugs, accurate RNA structure prediction has become increasingly important for rational drug design and therapeutic development.

Unlike proteins, which have benefited from revolutionary advances such as AlphaFold, RNA structure prediction remains a significant challenge. RNA molecules exhibit unique characteristics that complicate computational modeling: (1) high conformational flexibility with multiple stable states, (2) hierarchical folding patterns where secondary structure motifs (stems, loops, bulges) organize into complex 3D architectures, (3) abundant non-canonical base pairings and tertiary interactions, and (4) limited availability of experimentally determined structures. The Protein Data Bank contains approximately 200,000 protein structures but fewer than 5,000 RNA structures, creating a severe data scarcity problem.

Current approaches to RNA structure prediction generally fall into three categories: physics-based methods that rely on energy minimization, comparative modeling based on sequence homology, and machine learning methods. While recent deep learning approaches have shown promise, they typically focus on either secondary structure prediction or treat tertiary structure prediction as an isolated task. Few methods explicitly model the hierarchical, multi-scale nature of RNA folding—from nucleotide-level chemical interactions to motif-level organization to global 3D architecture.

### Research Objectives

This proposal introduces **RNAGeom-FM**, a multi-scale geometric foundation model designed to address the fundamental challenges in RNA tertiary structure prediction. Our primary objectives are:

1. To develop a hierarchical SE(3)-equivariant architecture that explicitly models RNA structure across multiple scales while maintaining geometric consistency.

2. To design effective self-supervised pre-training strategies that leverage the limited available structural data alongside abundant sequence and secondary structure information.

3. To integrate physics-informed constraints that ensure chemically and physically valid structure predictions.

4. To demonstrate state-of-the-art performance on RNA tertiary structure prediction benchmarks and establish transferable representations for downstream tasks.

### Significance

This research addresses a critical gap in computational biology and has direct implications for RNA therapeutic development. A successful multi-scale foundation model would: (1) accelerate the discovery of functional RNA structures, (2) enable rational design of RNA-based drugs, (3) provide transferable representations applicable to diverse RNA-related tasks, and (4) establish a paradigm for hierarchical geometric deep learning applicable beyond RNA to other biomolecular systems.

## 2. Methodology

### 2.1 Overall Architecture

RNAGeom-FM employs a hierarchical architecture that processes RNA at three interconnected scales, with information flowing bidirectionally between levels through geometric message passing.

**Scale 1: Nucleotide-Level Representation**

At the finest scale, we represent RNA as a graph $\mathcal{G}_1 = (\mathcal{V}_1, \mathcal{E}_1)$ where nodes $v_i \in \mathcal{V}_1$ correspond to individual nucleotides and edges $e_{ij} \in \mathcal{E}_1$ represent covalent bonds and spatial proximity. Each node is characterized by:

$$h_i^{(0)} = \text{Embed}(s_i) \oplus f_i^{\text{chem}}$$

where $s_i \in \{A, U, G, C\}$ is the nucleotide identity, $\text{Embed}(\cdot)$ is a learnable embedding, and $f_i^{\text{chem}}$ encodes chemical features (torsion angles, sugar pucker states).

**Scale 2: Motif-Level Representation**

Secondary structure motifs (stems, hairpin loops, internal loops, multi-way junctions) form the intermediate scale. We construct $\mathcal{G}_2 = (\mathcal{V}_2, \mathcal{E}_2)$ where nodes represent motifs and edges capture their connectivity and spatial relationships. Motif features are initialized by pooling nucleotide representations:

$$h_m^{(0)} = \text{MotifPool}\left(\{h_i^{(0)} : i \in \mathcal{M}_m\}\right)$$

where $\mathcal{M}_m$ denotes the set of nucleotides belonging to motif $m$.

**Scale 3: Global Coarse-Grained Representation**

At the coarsest scale, we represent the RNA as a reduced set of anchor points capturing global topology. Each anchor point aggregates information from neighboring motifs, enabling efficient modeling of long-range tertiary contacts.

### 2.2 Hierarchical SE(3)-Equivariant Message Passing

To ensure geometric consistency, we employ SE(3)-equivariant operations throughout the architecture. For any rotation matrix $R \in SO(3)$ and translation vector $t \in \mathbb{R}^3$, our model satisfies:

$$f(R\mathbf{X} + t, \mathbf{H}) = R \cdot f(\mathbf{X}, \mathbf{H})$$

where $\mathbf{X}$ represents coordinates and $\mathbf{H}$ represents invariant features.

**Intra-Scale Message Passing**

Within each scale, we use equivariant graph neural networks. For scale $l$, the update at layer $k$ follows:

$$m_{ij}^{(k)} = \phi_m^{(l)}\left(h_i^{(k-1)}, h_j^{(k-1)}, \|x_i - x_j\|, \langle \vec{v}_i, \vec{r}_{ij} \rangle\right)$$

$$h_i^{(k)} = \phi_h^{(l)}\left(h_i^{(k-1)}, \sum_{j \in \mathcal{N}(i)} m_{ij}^{(k)}\right)$$

$$\vec{v}_i^{(k)} = \vec{v}_i^{(k-1)} + \sum_{j \in \mathcal{N}(i)} \phi_v^{(l)}(m_{ij}^{(k)}) \cdot \vec{r}_{ij}$$

where $\vec{r}_{ij} = (x_j - x_i)/\|x_j - x_i\|$ is the unit direction vector, $\vec{v}_i$ is an equivariant vector feature, and $\phi_m, \phi_h, \phi_v$ are learnable MLPs.

**Cross-Scale Message Passing**

Information flows between scales through specialized pooling and unpooling operations:

*Upward (fine-to-coarse):*
$$h_m^{\uparrow} = \text{AttentionPool}\left(\{h_i : i \in \mathcal{M}_m\}, \mathbf{X}_{\mathcal{M}_m}\right)$$

*Downward (coarse-to-fine):*
$$\Delta h_i = \text{AttentionBroadcast}(h_m, h_i) \quad \text{for } i \in \mathcal{M}_m$$

The attention mechanisms incorporate geometric information to ensure proper coordinate transformations.

### 2.3 Multi-Task Pre-Training Strategy

Given data scarcity, we design a comprehensive pre-training strategy utilizing multiple data sources and self-supervised objectives.

**Data Sources:**
- PDB RNA structures (~5,000 high-resolution structures)
- Cryo-EM density maps (RNA regions from ribosome structures)
- Secondary structure databases (RNAcentral, bpRNA)
- Sequence data (Rfam families)

**Pre-Training Objectives:**

*Objective 1: Masked Nucleotide Prediction*

We randomly mask 15% of nucleotide identities and predict them from structural context:

$$\mathcal{L}_{\text{mask}} = -\sum_{i \in \mathcal{M}} \log p(s_i | \mathbf{X}, \mathbf{s}_{\backslash \mathcal{M}})$$

*Objective 2: Secondary Structure Denoising*

We corrupt secondary structure annotations by adding/removing base pairs and train the model to reconstruct correct pairings:

$$\mathcal{L}_{\text{SS}} = -\sum_{i<j} \left[y_{ij}\log \hat{p}_{ij} + (1-y_{ij})\log(1-\hat{p}_{ij})\right]$$

where $y_{ij} \in \{0,1\}$ indicates base pairing and $\hat{p}_{ij}$ is the predicted probability.

*Objective 3: 3D Coordinate Reconstruction*

We remove portions of 3D coordinates and predict them conditioned on remaining structure:

$$\mathcal{L}_{\text{3D}} = \frac{1}{|\mathcal{C}|}\sum_{i \in \mathcal{C}} \|\hat{x}_i - x_i\|^2 + \lambda_{\text{FAPE}} \cdot \mathcal{L}_{\text{FAPE}}$$

where $\mathcal{L}_{\text{FAPE}}$ is the Frame Aligned Point Error ensuring local structural accuracy.

*Objective 4: Density Fitting (for cryo-EM data)*

$$\mathcal{L}_{\text{density}} = 1 - \text{CC}\left(\rho_{\text{pred}}, \rho_{\text{exp}}\right)$$

where CC denotes cross-correlation between predicted and experimental density maps.

The total pre-training loss combines all objectives:

$$\mathcal{L}_{\text{pretrain}} = \mathcal{L}_{\text{mask}} + \alpha \mathcal{L}_{\text{SS}} + \beta \mathcal{L}_{\text{3D}} + \gamma \mathcal{L}_{\text{density}}$$

### 2.4 Physics-Informed Constraints

We incorporate physical priors to ensure chemically valid predictions:

**Base-Pairing Energy Prior:**

$$\mathcal{L}_{\text{energy}} = \left|E_{\text{pred}} - E_{\text{Turner}}\right|$$

where $E_{\text{Turner}}$ is computed from Turner nearest-neighbor parameters.

**Backbone Geometry Constraints:**

$$\mathcal{L}_{\text{geom}} = \sum_i \left[(d_i^{\text{P-P}} - d_0)^2 + \sum_{\theta} (\theta_i - \theta_0)^2\right]$$

enforcing ideal phosphate-phosphate distances and bond angles.

**Steric Clash Penalty:**

$$\mathcal{L}_{\text{clash}} = \sum_{i<j} \max(0, r_{\text{min}} - d_{ij})^2$$

### 2.5 Experimental Design and Evaluation

**Datasets:**
- Training: PDB structures (release date < 2022), augmented with secondary structure data
- Validation: PDB structures (2022-2023)
- Test: RNA-Puzzles dataset, CASP15 RNA targets, recent PDB deposits (2024)

**Evaluation Metrics:**
- Root Mean Square Deviation (RMSD)
- Global Distance Test (GDT-TS)
- Interaction Network Fidelity (INF) for base-pairing accuracy
- TM-score adapted for RNA
- Clash score and stereochemical quality (MolProbity)

**Baselines:**
- Physics-based: SimRNA, FARFAR2, RNAComposer
- Learning-based: RhoFold, ARES, trRosettaRNA
- Ablated versions of RNAGeom-FM

**Downstream Tasks:**
- RNA-ligand binding affinity prediction
- RNA-protein interaction prediction
- RNA design (inverse folding)

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **State-of-the-Art Performance:** We anticipate RNAGeom-FM will achieve >20% improvement in RMSD on RNA-Puzzles benchmarks compared to existing methods, particularly for RNAs with complex tertiary interactions.

2. **Transferable Representations:** Pre-trained embeddings should demonstrate strong performance when fine-tuned for downstream tasks, requiring significantly less task-specific data.

3. **Physically Valid Structures:** Physics-informed constraints will ensure predictions with minimal steric clashes and correct stereochemistry, suitable for downstream molecular dynamics simulations.

4. **Efficient Inference:** Multi-scale architecture enables prediction of large RNA complexes (>500 nucleotides) within minutes on standard GPU hardware.

### Broader Impact

**Scientific Impact:** RNAGeom-FM will establish a new paradigm for hierarchical geometric learning in structural biology, with methodological contributions applicable to other biomolecular systems including protein-RNA complexes and DNA nanostructures.

**Therapeutic Impact:** Accurate RNA structure prediction directly enables rational design of RNA therapeutics, including antisense oligonucleotides, aptamers, and mRNA vaccines with optimized stability and function.

**Community Resource:** We will release pre-trained models, code, and curated training datasets to accelerate research in RNA biology and AI for nucleic acids.

**Educational Impact:** This work bridges machine learning and RNA biology communities, providing accessible tools for researchers without extensive computational expertise to leverage AI in their RNA research.

In conclusion, RNAGeom-FM represents a principled approach to RNA tertiary structure prediction that addresses the fundamental challenges of data scarcity, structural complexity, and multi-scale modeling through innovative geometric deep learning techniques. Success in this endeavor would mark a significant step toward understanding RNA biology and developing RNA-based therapeutics.