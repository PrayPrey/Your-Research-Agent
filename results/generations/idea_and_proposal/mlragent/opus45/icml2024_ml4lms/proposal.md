# Research Proposal: Adaptive Multi-Scale Molecular Representation Learning for Cross-Domain Property Prediction

## 1. Introduction

### Background

The application of machine learning to life and material sciences holds transformative potential for addressing critical global challenges, including drug discovery, sustainable materials development, and agrochemical innovation. However, a fundamental bottleneck persists: the fragmentation of molecular representations across different scales and domains. Current machine learning approaches typically operate within narrow domains—small molecule property prediction models struggle with proteins, organic compound models fail on crystalline materials, and electronic structure methods rarely connect to biological activity predictions.

This fragmentation stems from the inherent complexity of molecular systems, which span multiple scales of representation. At the finest scale, quantum mechanical descriptions capture electronic structure and bonding. At intermediate scales, molecular graphs and 3D geometries encode atomic connectivity and spatial arrangements. At larger scales, protein sequences, crystal lattices, and macromolecular assemblies require entirely different representational paradigms. Existing models, including recent advances such as MolGraph-xLSTM and DMCA, have demonstrated impressive performance within specific domains but lack the architectural flexibility to bridge these representational gaps.

The literature reveals promising directions toward addressing this challenge. ReactEmbed demonstrates that contrastive learning can unify protein and molecule embeddings through biochemical reaction networks. Multi-MoleScale shows that combining graph contrastive learning with sequence models improves property prediction. MMSA leverages structure awareness for multi-modal self-supervised pre-training. However, none of these approaches provides a unified framework capable of dynamically adapting to inputs across the full spectrum of molecular scales.

### Research Objectives

This research proposes the development of a **Hierarchical Scale-Bridging Transformer (HSBT)**, a foundation model architecture designed to learn unified molecular representations across diverse chemical spaces while respecting the inherent multi-scale nature of molecular systems. The specific objectives are:

1. Design a multi-scale tokenization framework that maps diverse molecular inputs (SMILES, 3D coordinates, protein sequences, crystal structures) to a shared embedding space
2. Develop scale-aware attention mechanisms that dynamically route information across representational hierarchies
3. Implement a curriculum pre-training strategy that progressively builds from quantum properties to biological activities
4. Validate the framework across cross-domain property prediction tasks spanning small molecules, proteins, and materials

### Significance

Successful development of HSBT would significantly lower barriers to industrial adoption of ML in chemistry and biology by eliminating the need for domain-specific models. Scientists could leverage a single unified tool for rapid hypothesis testing across therapeutic targets, materials candidates, and agrochemical leads. This aligns directly with the workshop's focus on bridging theoretical advances with practical applications and connecting academic and industry researchers.

## 2. Methodology

### 2.1 Multi-Scale Tokenization Framework

The foundation of HSBT is a unified tokenization scheme that converts diverse molecular inputs into a common representational format while preserving scale-specific information.

**SMILES Tokenization**: We employ a substructure-aware tokenizer inspired by MolCL-SP, decomposing molecules into chemically meaningful fragments:

$$T_{SMILES}(m) = \{t_1, t_2, ..., t_n\} \text{ where } t_i \in \mathcal{V}_{substructure}$$

**3D Coordinate Tokenization**: Atomic positions are encoded using radial basis functions and spherical harmonics:

$$T_{3D}(\mathbf{r}_i) = \sum_{l=0}^{L_{max}} \sum_{m=-l}^{l} c_{lm}^i Y_l^m(\hat{\mathbf{r}}_i) \odot \phi_{RBF}(|\mathbf{r}_i|)$$

where $Y_l^m$ are spherical harmonics, $\phi_{RBF}$ represents radial basis functions, and $\odot$ denotes element-wise multiplication.

**Protein Sequence Tokenization**: We extend standard amino acid tokenization with structural motif awareness:

$$T_{protein}(s) = \{e_{aa}^1 + e_{pos}^1 + e_{ss}^1, ..., e_{aa}^N + e_{pos}^N + e_{ss}^N\}$$

where $e_{aa}$, $e_{pos}$, and $e_{ss}$ represent amino acid, positional, and secondary structure embeddings respectively.

**Crystal Structure Tokenization**: Unit cells are encoded through periodic graph representations:

$$T_{crystal}(\mathcal{C}) = \{h_i | h_i = f_{GNN}(x_i, \mathcal{N}_i^{periodic})\}$$

where $\mathcal{N}_i^{periodic}$ captures periodic boundary conditions.

All tokenizers project to a common embedding dimension $d_{model}$, augmented with a scale indicator embedding $e_{scale} \in \{e_{electronic}, e_{molecular}, e_{sequence}, e_{crystal}\}$.

### 2.2 Scale-Aware Attention Architecture

HSBT employs a hierarchical transformer architecture with three key components:

**Intra-Scale Self-Attention**: Standard multi-head self-attention within each scale:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

**Cross-Scale Bridge Attention**: Learnable cross-attention between adjacent scales enables knowledge transfer:

$$\text{Bridge}_{s \rightarrow s'}(H_s, H_{s'}) = \text{MultiHead}(H_{s'}W_Q, H_sW_K, H_sW_V)$$

where $H_s$ and $H_{s'}$ represent hidden states from source and target scales.

**Dynamic Scale Routing**: A gating mechanism learns to weight contributions from different scales:

$$g_s = \sigma(W_g \cdot [\bar{h}_{input}; e_{task}])$$

$$H_{final} = \sum_{s \in \mathcal{S}} g_s \cdot H_s$$

where $\bar{h}_{input}$ is the mean-pooled input representation and $e_{task}$ is a task-specific embedding.

The complete forward pass proceeds as:

$$H^{(l+1)} = \text{FFN}(\text{LayerNorm}(H^{(l)} + \text{ScaleAwareAttn}(H^{(l)})))$$

### 2.3 Curriculum Pre-Training Strategy

Pre-training follows a structured curriculum progressing from fundamental to complex property relationships:

**Stage 1: Quantum Foundation (Weeks 1-2)**
- Dataset: QM9, OE62, ANI-1x
- Objective: Predict electronic properties (HOMO, LUMO, dipole moment, atomization energy)
- Loss: $\mathcal{L}_1 = \sum_{p \in \mathcal{P}_{quantum}} \text{MSE}(\hat{y}_p, y_p)$

**Stage 2: Molecular Bridge (Weeks 3-4)**
- Dataset: PubChem, ZINC, GDB-17
- Objectives: Masked atom prediction, contrastive learning between 2D/3D representations
- Loss: $\mathcal{L}_2 = \mathcal{L}_{MAM} + \lambda_{CL}\mathcal{L}_{contrastive}$

where the contrastive loss follows:

$$\mathcal{L}_{contrastive} = -\log\frac{\exp(\text{sim}(z_{2D}, z_{3D})/\tau)}{\sum_{j}\exp(\text{sim}(z_{2D}, z_{3D}^j)/\tau)}$$

**Stage 3: Biological Integration (Weeks 5-6)**
- Dataset: BindingDB, ChEMBL, UniProt
- Objectives: Cross-modal alignment between ligands and protein binding sites
- Loss: $\mathcal{L}_3 = \mathcal{L}_{binding} + \mathcal{L}_{protein-ligand-alignment}$

**Stage 4: Materials Extension (Weeks 7-8)**
- Dataset: Materials Project, OQMD, ICSD
- Objectives: Crystal property prediction, structure-property relationships
- Loss: $\mathcal{L}_4 = \mathcal{L}_{formation} + \mathcal{L}_{bandgap} + \mathcal{L}_{stability}$

### 2.4 Experimental Design and Evaluation

**Datasets for Evaluation**:

*Small Molecules*: MoleculeNet benchmark (8 datasets including BBBP, Tox21, ESOL, FreeSolv)

*Proteins*: TAPE benchmark, ProteinGym, enzyme function prediction

*Materials*: MatBench suite, perovskite stability, thermoelectric performance

*Cross-Domain*: Drug-target interaction (DTI), protein-ligand binding affinity, catalyst activity prediction

**Baseline Comparisons**:
- Domain-specific SOTA: MolGraph-xLSTM, ESM-2, CGCNN
- Multi-modal methods: DMCA, ReactEmbed, MMSA
- General foundation models: Uni-Mol, MolBERT

**Evaluation Metrics**:

For classification tasks:
$$\text{AUROC} = \int_0^1 TPR(FPR^{-1}(t))dt$$

For regression tasks:
$$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^n(y_i - \hat{y}_i)^2}, \quad R^2 = 1 - \frac{\sum_i(y_i - \hat{y}_i)^2}{\sum_i(y_i - \bar{y})^2}$$

**Cross-domain transfer efficiency**:
$$\eta_{transfer} = \frac{P_{HSBT} - P_{scratch}}{P_{domain-specific} - P_{scratch}}$$

where $P$ denotes performance on the target domain.

**Ablation Studies**:
1. Scale-aware attention vs. standard attention
2. Curriculum pre-training vs. joint training
3. Impact of each tokenization modality
4. Dynamic routing effectiveness

**Computational Setup**: Training on 8× A100 GPUs with mixed precision, AdamW optimizer ($\beta_1=0.9$, $\beta_2=0.999$), cosine learning rate schedule with warmup, batch size 256 per GPU.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Technical Deliverables**:
1. A unified foundation model achieving competitive performance (within 5% of domain-specific SOTA) across all benchmark domains
2. Demonstration of positive transfer ($\eta_{transfer} > 0.8$) on cross-domain tasks
3. Reduced fine-tuning requirements: achieving 90% of full fine-tuning performance with only 10% of domain-specific data
4. Open-source release of model weights, tokenizers, and training code

**Quantitative Performance Targets**:
- MoleculeNet average improvement: +3-5% over DMCA
- DTI prediction: AUROC > 0.92 on BindingDB
- Materials bandgap prediction: MAE < 0.3 eV on MatBench
- Cross-domain zero-shot: meaningful predictions (>0.7 correlation) without fine-tuning

### Scientific Impact

HSBT addresses three critical challenges identified in the literature review. First, it provides a principled solution to cross-domain representation integration through scale-bridging attention mechanisms. Second, the multi-scale tokenization framework offers a systematic approach to hierarchical molecular representation that previous methods lack. Third, the curriculum pre-training strategy provides a template for leveraging diverse data sources of varying quality and annotation depth.

### Industrial Impact

For pharmaceutical companies, HSBT enables rapid virtual screening across diverse compound libraries and target classes without maintaining separate modeling pipelines. Materials scientists gain a unified tool for exploring structure-property relationships across organic, inorganic, and hybrid materials. Agrochemical developers can leverage transfer from pharmaceutical datasets to accelerate crop protection compound optimization.

### Broader Societal Impact

By accelerating molecular discovery workflows, HSBT contributes to addressing urgent societal challenges including: development of novel therapeutics for age-related diseases, design of sustainable materials to combat climate change, and creation of more effective and environmentally benign agrochemicals to ensure global food security.

The proposed research directly addresses the workshop's mission of bridging theoretical ML advances with practical applications in life and material sciences, providing a foundation model architecture that democratizes access to sophisticated molecular property prediction across academic and industrial settings.