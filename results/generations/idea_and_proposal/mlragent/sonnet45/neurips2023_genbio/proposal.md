# Multi-Scale Geometric Diffusion Models for RNA Structure-Function Co-Design

## 1. Introduction

### Background

The field of RNA therapeutics has experienced remarkable growth in recent years, catalyzed by the success of mRNA vaccines during the COVID-19 pandemic. RNA-based molecules, including messenger RNA (mRNA), small interfering RNA (siRNA), aptamers, and riboswitches, offer unique advantages over traditional small molecule drugs and protein therapeutics due to their programmability, rapid development timelines, and potential for transient therapeutic effects. However, despite these successes, the rational design of functional RNA molecules remains a formidable challenge.

Unlike protein design, where tools like AlphaFold have revolutionized structure prediction and recent generative models have enabled de novo protein design, RNA design lacks comparable computational frameworks. This disparity stems from RNA's unique complexities: its structure-function relationship operates across multiple hierarchical scales—from primary sequence to secondary structure base-pairing patterns to tertiary 3D conformations—each critically influencing biological function. Furthermore, RNA molecules exhibit significant conformational flexibility, can adopt multiple stable structures, and their functional properties (binding affinity, thermodynamic stability, immunogenicity) depend on subtle structural features that are difficult to capture with existing computational approaches.

Recent advances in geometric deep learning and diffusion models have shown promise in molecular generation tasks. Works such as gRNAde have demonstrated the feasibility of using geometric neural networks for RNA inverse folding, while RiboGen has explored sequence-structure co-generation. However, these approaches primarily focus on two-level relationships (sequence-structure or structure-function) and lack the hierarchical, multi-scale integration necessary for comprehensive RNA design. Additionally, existing methods do not adequately incorporate functional constraints or enable iterative refinement through experimental feedback.

### Research Objectives

This research proposes to develop a novel **Multi-Scale Geometric Diffusion Model (MS-GDM)** for RNA structure-function co-design that addresses these limitations through the following specific objectives:

1. **Develop a hierarchical diffusion architecture** that simultaneously generates RNA molecules across three scales: secondary structure topology, 3D geometric coordinates, and nucleotide sequence, with bidirectional information flow between scales.

2. **Incorporate physics-based constraints and functional objectives** as conditioning signals, including thermodynamic stability, binding affinity, structural motifs, and immunogenicity profiles.

3. **Create a comprehensive training framework** that leverages existing structural databases, physics-based energy functions, and experimental stability data to learn realistic RNA design principles.

4. **Establish a wet-lab-in-the-loop validation pipeline** that enables iterative model refinement through high-throughput experimental screening.

5. **Demonstrate practical applicability** by designing novel RNA therapeutics and biosensors with specified functional properties.

### Significance

This research will make several significant contributions to both machine learning and biological sciences:

**Scientific Impact**: The proposed model will advance our fundamental understanding of RNA structure-function relationships by learning transferable representations across multiple organizational scales. By explicitly modeling the hierarchical dependencies between sequence, structure, and function, the framework will reveal design principles that are currently inaccessible through traditional approaches.

**Technological Impact**: MS-GDM will provide a practical tool for accelerating RNA therapeutic development, potentially reducing the time and cost associated with designing functional RNA molecules from years to weeks. This capability is particularly crucial for rapid response to emerging infectious diseases and personalized medicine applications.

**Methodological Impact**: The multi-scale diffusion architecture developed in this work will be generalizable to other biomolecular design problems, including protein-RNA complexes, DNA nanostructures, and hybrid biomolecular systems, establishing a new paradigm for hierarchical molecular generation.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

**Structural Data Sources**: We will compile a comprehensive dataset from multiple sources:
- RNA 3D structures from the Protein Data Bank (PDB), focusing on high-resolution structures (< 3Å resolution)
- RNA-puzzles benchmark dataset for structural validation
- Experimentally validated secondary structures from RNA STRAND and RNAcentral
- Functional annotation data from Rfam and RNAcentral databases

**Preprocessing Pipeline**: Each RNA structure will be processed to extract:
1. **Secondary structure representation**: Base-pairing matrix $\mathbf{S} \in \{0,1\}^{n \times n}$ where $S_{ij} = 1$ indicates base pairing between positions $i$ and $j$
2. **3D geometric coordinates**: Backbone atoms (C3', C4', P, O5') and base centroids, represented as point clouds $\mathbf{X} \in \mathbb{R}^{n \times 3}$
3. **Sequence representation**: One-hot encoded nucleotide identities $\mathbf{A} \in \{0,1\}^{n \times 4}$ for A, U, G, C

**Augmentation**: To address data scarcity, we will implement:
- Structure-preserving rotations and translations for geometric augmentation
- Sequence mutations consistent with structural constraints
- Synthetic structures generated using physics-based RNA folding simulators (e.g., MC-Fold, RNAComposer)

### 2.2 Multi-Scale Diffusion Architecture

#### 2.2.1 Hierarchical Diffusion Process

Our model implements three coupled diffusion processes operating at different organizational scales:

**Scale 1: Secondary Structure Topology Diffusion**

We model secondary structure as a graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where vertices represent nucleotides and edges represent base pairs. The forward diffusion process corrupts the base-pairing adjacency matrix:

$$q(\mathbf{S}_t | \mathbf{S}_{t-1}) = \mathcal{N}(\mathbf{S}_t; \sqrt{1-\beta_t^{(s)}}\mathbf{S}_{t-1}, \beta_t^{(s)}\mathbf{I})$$

where $\beta_t^{(s)}$ is the noise schedule for secondary structure. The reverse process is modeled by a graph neural network:

$$p_\theta(\mathbf{S}_{t-1} | \mathbf{S}_t, \mathbf{c}) = \mathcal{N}(\mathbf{S}_{t-1}; \mu_\theta^{(s)}(\mathbf{S}_t, t, \mathbf{c}), \sigma_t^{(s)}\mathbf{I})$$

where $\mathbf{c}$ represents conditioning information (functional constraints).

**Scale 2: 3D Geometric Coordinate Diffusion**

For 3D structure generation, we employ an SE(3)-equivariant diffusion process to ensure rotational and translational invariance. The forward process:

$$q(\mathbf{X}_t | \mathbf{X}_{t-1}) = \mathcal{N}(\mathbf{X}_t; \sqrt{1-\beta_t^{(x)}}\mathbf{X}_{t-1}, \beta_t^{(x)}\mathbf{I})$$

The reverse process uses a geometric vector perceptron (GVP) network conditioned on both secondary structure and functional constraints:

$$p_\phi(\mathbf{X}_{t-1} | \mathbf{X}_t, \mathbf{S}_t, \mathbf{c}) = \mathcal{N}(\mathbf{X}_{t-1}; \mu_\phi^{(x)}(\mathbf{X}_t, \mathbf{S}_t, t, \mathbf{c}), \sigma_t^{(x)}\mathbf{I})$$

**Scale 3: Sequence Assignment Diffusion**

Sequence generation is modeled as a discrete diffusion process in the categorical space:

$$q(\mathbf{A}_t | \mathbf{A}_{t-1}) = \text{Cat}(\mathbf{A}_t; (1-\gamma_t^{(a)})\mathbf{A}_{t-1} + \gamma_t^{(a)}\mathbf{u})$$

where $\mathbf{u}$ is the uniform distribution and $\gamma_t^{(a)}$ is the corruption rate. The reverse process employs a transformer architecture:

$$p_\psi(\mathbf{A}_{t-1} | \mathbf{A}_t, \mathbf{X}_t, \mathbf{S}_t, \mathbf{c}) = \text{Cat}(\mathbf{A}_{t-1}; f_\psi(\mathbf{A}_t, \mathbf{X}_t, \mathbf{S}_t, t, \mathbf{c}))$$

#### 2.2.2 Cross-Scale Attention Mechanism

To enable information flow between scales, we implement a cross-attention module that integrates features across hierarchies:

$$\mathbf{h}_i^{(l)} = \text{Attention}(Q_i^{(l)}, K^{(l')}, V^{(l')}) + \text{FFN}(\mathbf{h}_i^{(l)})$$

where $l, l' \in \{\text{sequence}, \text{structure}, \text{geometry}\}$ denote different scales. This allows, for example, geometric constraints to inform sequence generation and vice versa.

#### 2.2.3 Network Architecture Details

**Secondary Structure Module**: A message-passing neural network (MPNN) with 6 layers, hidden dimension 256, operating on the base-pairing graph.

**3D Geometry Module**: A GVP network with 8 layers, processing both scalar (128-dim) and vector (64-dim) features, ensuring SE(3)-equivariance.

**Sequence Module**: A Transformer with 12 layers, 8 attention heads, hidden dimension 512, incorporating positional encodings and structure-aware attention masks.

### 2.3 Physics-Based Conditioning

To ensure generated RNA molecules are physically realistic, we incorporate energy-based conditioning:

**Thermodynamic Stability**: The Vienna RNA package's energy model is integrated as a differentiable function:

$$E_{\text{fold}}(\mathbf{A}, \mathbf{S}) = \sum_{(i,j) \in \mathbf{S}} E_{\text{pair}}(A_i, A_j) + \sum_{\text{loops}} E_{\text{loop}}$$

**Structural Constraints**: Distance-based constraints ensuring physical plausibility:

$$\mathcal{L}_{\text{geom}} = \sum_{i,j} \max(0, ||x_i - x_j||_2 - d_{\max}(A_i, A_j))^2$$

where $d_{\max}$ is the maximum allowed distance based on base pairing.

**Functional Objectives**: Task-specific objectives encoded as:

$$\mathbf{c}_{\text{func}} = [\text{binding\_affinity}, \text{stability\_score}, \text{immunogenicity}]$$

These are incorporated through classifier-free guidance:

$$\tilde{\epsilon}_\theta(\mathbf{z}_t, t, \mathbf{c}) = \epsilon_\theta(\mathbf{z}_t, t, \emptyset) + w \cdot (\epsilon_\theta(\mathbf{z}_t, t, \mathbf{c}) - \epsilon_\theta(\mathbf{z}_t, t, \emptyset))$$

where $w$ is the guidance weight.

### 2.4 Training Procedure

**Loss Function**: The overall training objective combines losses across all scales:

$$\mathcal{L}_{\text{total}} = \mathbb{E}_{t,\mathbf{z}_0,\epsilon}[\lambda_s \|\epsilon_s - \epsilon_\theta^{(s)}(\mathbf{S}_t, t)\|^2 + \lambda_x \|\epsilon_x - \epsilon_\phi^{(x)}(\mathbf{X}_t, t)\|^2 + \lambda_a \mathcal{L}_{\text{CE}}(\mathbf{A}_0, \hat{\mathbf{A}}_0)]$$

where $\lambda_s, \lambda_x, \lambda_a$ are scale-specific weights, and $\mathcal{L}_{\text{CE}}$ is cross-entropy loss for discrete sequence.

**Training Strategy**:
1. **Curriculum learning**: Start with single-scale training, progressively add scales
2. **Multi-task learning**: Jointly optimize structure prediction and generation tasks
3. **Optimizer**: AdamW with learning rate $10^{-4}$, cosine annealing schedule
4. **Batch size**: 32 structures, gradient accumulation over 4 steps
5. **Regularization**: Dropout (0.1), weight decay (0.01)

**Computational Resources**: Training on 4× NVIDIA A100 GPUs for approximately 2 weeks.

### 2.5 Experimental Validation

#### 2.5.1 Computational Validation

**Metrics**:
- **Sequence Recovery Rate**: Percentage of native sequence recovered in inverse folding tasks
- **Structure Accuracy**: TM-score and RMSD compared to target structures
- **Secondary Structure Prediction**: F1 score for base-pair prediction
- **Thermodynamic Stability**: Free energy comparison with native structures
- **Diversity**: Pairwise sequence/structure similarity distributions

**Benchmark Comparisons**: Evaluate against gRNAde, RDesign, RiboGen, and traditional methods (Rosetta, MC-Fold) on RNA-puzzles test set.

#### 2.5.2 Wet-Lab-in-the-Loop Pipeline

**Phase 1: High-Throughput Screening**
- Generate 10,000 diverse RNA designs per target specification
- Computational filtering based on predicted stability and synthesizability
- Select top 100 candidates for experimental synthesis

**Phase 2: Experimental Validation**
- **In vitro transcription**: Synthesize RNA candidates
- **Structural probing**: SHAPE-MaP or DMS-MaP for secondary structure validation
- **Functional assays**: 
  - Binding affinity measurements (SPR, ITC) for aptamers
  - Gene silencing efficiency for siRNA
  - Translation efficiency for mRNA
- **Stability assays**: Serum stability, thermal denaturation

**Phase 3: Iterative Refinement**
- Incorporate experimental measurements as additional training data
- Fine-tune model with reinforcement learning signal:

$$\mathcal{L}_{\text{RL}} = -\mathbb{E}_{\mathbf{z} \sim p_\theta}[R(\mathbf{z})]$$

where $R(\mathbf{z})$ is the experimental reward (e.g., measured binding affinity)
- Repeat generation-validation cycle

**Collaborations**: Partner with experimental RNA biology labs for validation studies.

### 2.6 Application Scenarios

**Use Case 1: mRNA Vaccine Design**
- Target: Generate mRNA sequences with optimal codon usage, structural stability, and low immunogenicity
- Constraints: 5' UTR and 3' UTR regulatory elements, coding sequence compatibility
- Validation: Translation efficiency in cell lines, immunogenicity profiling

**Use Case 2: Aptamer Generation**
- Target: RNA aptamers binding specific protein targets (e.g., VEGF, thrombin)
- Constraints: Binding affinity ($K_d < 10$ nM), serum stability (> 24h), specific 3D binding pocket
- Validation: SPR binding assays, competition assays, cellular uptake

**Use Case 3: Riboswitch Design**
- Target: Synthetic riboswitches responsive to small molecule ligands
- Constraints: Ligand-induced conformational change, expression dynamic range
- Validation: Fluorescence reporter assays, RNA structure probing with/without ligand

## 3. Expected Outcomes & Impact

### 3.1 Scientific Outcomes

**Quantitative Performance Targets**:
- Achieve > 60% sequence recovery rate on RNA inverse folding benchmarks (surpassing current state-of-the-art gRNAde at ~50%)
- Generate structures with < 4Å RMSD to target conformations
- Design functional RNA molecules with > 80% success rate in wet-lab validation
- Reduce design-to-validation cycle time from months to weeks

**Fundamental Insights**:
The multi-scale diffusion framework will provide unprecedented insights into:
- Hierarchical dependencies between RNA sequence, secondary structure, and tertiary conformation
- Transferable design principles across different RNA families and functions
- Critical structural motifs that determine functional properties
- The navigability of RNA sequence-structure-function landscape

### 3.2 Technological Impact

**Immediate Applications**:
1. **Therapeutic RNA Design**: Enable rapid development of mRNA vaccines for emerging pathogens, personalized cancer vaccines, and protein replacement therapies
2. **Diagnostic Tools**: Generate RNA aptamer-based biosensors for point-of-care diagnostics
3. **Synthetic Biology**: Design regulatory RNA elements for metabolic engineering and gene circuit construction

**Broader Implications**:
- **Accelerated Drug Discovery**: Reduce development timeline for RNA therapeutics from 5-7 years to 2-3 years
- **Precision Medicine**: Enable patient-specific RNA therapeutic design based on individual genetic profiles
- **Cost Reduction**: Decrease experimental screening burden by 10-100×, making RNA therapeutics more accessible

### 3.3 Methodological Contributions

**Generalizable Framework**: The multi-scale diffusion architecture developed in this work will be adaptable to:
- Protein-RNA complex design
- DNA nanostructure engineering
- Hybrid biomolecular systems (e.g., protein-nucleic acid conjugates)
- Other hierarchical molecular generation problems in chemistry and materials science

**Open-Source Ecosystem**: We will release:
- Trained model weights and inference code
- Curated and preprocessed RNA structure dataset
- Benchmark suite for RNA design evaluation
- Interactive web interface for RNA design (similar to RoseTTAFold Server)

### 3.4 Addressing Key Challenges

This proposal directly addresses the challenges identified in the literature review:

1. **Data Scarcity**: Multi-scale architecture with physics-based conditioning reduces data requirements; augmentation strategies and synthetic data generation further mitigate limitations
2. **Complex Structure-Function Relationship**: Explicit multi-scale modeling captures dependencies across organizational levels
3. **Multi-Scale Modeling**: Novel hierarchical diffusion framework with cross-scale attention mechanisms
4. **Controllable Generation**: Classifier-free guidance enables precise functional constraint specification
5. **Experimental Validation**: Wet-lab-in-the-loop pipeline with reinforcement learning refinement closes the computational-experimental gap

### 3.5 Timeline and Milestones

**Year 1**:
- Months 1-3: Data collection, preprocessing, and augmentation pipeline development
- Months 4-6: Implementation of single-scale diffusion models
- Months 7-9: Integration into multi-scale architecture with cross-attention
- Months 10-12: Initial training and computational validation

**Year 2**:
- Months 13-15: Model refinement and hyperparameter optimization
- Months 16-18: Computational benchmark evaluations and ablation studies
- Months 19-21: First round of experimental validation (aptamer design)
- Months 22-24: Iterative refinement with wet-lab feedback

**Year 3**:
- Months 25-27: Extended experimental validation (mRNA, riboswitch applications)
- Months 28-30: Performance optimization and user interface development
- Months 31-33: Publication preparation and open-source release
- Months 34-36: Community engagement and application to collaborative projects

### 3.6 Risk Mitigation

**Technical Risks**:
- *Model convergence issues*: Implement curriculum learning and careful initialization strategies
- *Computational constraints*: Develop efficient sampling algorithms and model distillation techniques
- *Overfitting to limited data*: Strong regularization, physics-based constraints, and transfer learning from related domains

**Experimental Risks**:
- *Low wet-lab validation rates*: Start with well-characterized systems (aptamers) before complex applications
- *Synthesis challenges*: Incorporate synthesizability constraints in design phase
- *Unexpected functional failures*: Build interpretability tools to diagnose failure modes

### 3.7 Long-Term Vision

Beyond the immediate three-year scope, this research lays the foundation for:
- **Automated RNA Foundry**: Fully automated pipeline from therapeutic target specification to synthesized, validated RNA molecules
- **Multi-Modal Biomolecular Design**: Extension to simultaneous design of RNA-protein, RNA-small molecule, and other biomolecular systems
- **Foundational RNA Models**: Large-scale pre-trained models analogous to AlphaFold for proteins, enabling broad scientific discovery

The successful development of MS-GDM will represent a significant step toward the ultimate goal of programmable RNA design, democratizing access to RNA therapeutics and accelerating the transition from digital biology to real-world healthcare impact. By bridging the gap between computational prediction and experimental validation, this work will establish a new paradigm for AI-driven molecular design that is both scientifically rigorous and practically useful for addressing pressing biomedical challenges.