# Research Proposal: HiMamba-CL: Hierarchical Bidirectional Mamba with Contrastive Learning for Unified RNA Representation

## 1. Introduction

### 1.1 Background

Ribonucleic acids (RNA) serve as fundamental molecules in cellular biology, performing diverse functions ranging from genetic information transfer to catalytic activity and gene regulation. The rapid advancement of high-throughput sequencing technologies has generated unprecedented volumes of RNA data, creating both opportunities and challenges for computational analysis. Understanding RNA structure and function is critical for numerous applications, including drug discovery, therapeutic development, and fundamental biological research.

Recent years have witnessed remarkable progress in applying artificial intelligence to biological sequence analysis. Foundation models, pre-trained on large-scale datasets, have demonstrated exceptional capabilities in capturing complex patterns within protein sequences, leading to breakthroughs such as AlphaFold for protein structure prediction. However, RNA foundation models remain comparatively underdeveloped despite RNA's central importance in cellular processes and its emerging role as a therapeutic modality.

A fundamental challenge in RNA representation learning lies in the inherently multi-scale nature of RNA biology. RNA molecules exhibit hierarchical organization spanning multiple levels: local sequence motifs (3-10 nucleotides) determine binding specificity and regulatory function; secondary structure domains (50-200 nucleotides) form stable stem-loops and pseudoknots; and full transcript context (hundreds to thousands of nucleotides) governs overall molecular behavior and cellular localization. Current RNA foundation models predominantly employ flat architectures that process sequences uniformly, failing to explicitly capture these hierarchical patterns that are essential for accurate functional prediction.

Furthermore, existing approaches typically focus on single modalities—either sequence or structure—limiting their ability to learn comprehensive representations that generalize across diverse downstream tasks. While sequence information encodes the primary genetic content, structural information captures the three-dimensional arrangement that ultimately determines molecular function. The disconnect between these modalities in current models represents a significant barrier to developing truly universal RNA representations.

### 1.2 Research Objectives

This research proposes HiMamba-CL, a novel framework that addresses these limitations through two synergistic innovations: (1) hierarchical bidirectional Mamba layers that explicitly capture multi-scale RNA patterns, and (2) contrastive cross-modal alignment that learns modality-invariant representations bridging sequence and structure information.

The primary objectives of this research are:

1. **Develop a hierarchical state space model architecture** specifically designed for RNA sequences, with progressively expanding receptive fields that capture patterns from local motifs to global transcript context.

2. **Establish a contrastive learning framework** utilizing biologically meaningful augmentations (orthologs, splice isoforms, synonymous mutations) to align sequence and structure modalities into a unified embedding space.

3. **Validate the approach** through comprehensive benchmarking on RNA structure prediction, function classification, and cross-task transfer efficiency, demonstrating significant improvements over existing methods.

4. **Release pre-trained models and code** to facilitate adoption by the broader research community and accelerate progress in RNA therapeutics and functional genomics.

### 1.3 Significance

This research addresses a critical gap in AI for nucleic acids by providing the first hierarchical multimodal foundation model specifically designed for RNA. Success would establish a new paradigm for RNA representation learning with direct applications in:

- **RNA therapeutics**: Improved structure prediction enables better design of mRNA vaccines, antisense oligonucleotides, and RNA-based drugs
- **Functional annotation**: Unified representations accelerate characterization of non-coding RNAs with unknown functions
- **Disease understanding**: Better models of RNA behavior illuminate mechanisms underlying genetic disorders and cancer

## 2. Methodology

### 2.1 Overall Architecture

HiMamba-CL consists of three main components: (1) a hierarchical bidirectional Mamba encoder for sequence processing, (2) parallel structure encoders for secondary and tertiary structure information, and (3) a contrastive alignment module that unifies representations across modalities.

#### 2.1.1 Hierarchical Bidirectional Mamba Encoder

The core innovation lies in our hierarchical stacking of bidirectional Mamba layers with progressively expanding receptive fields. Given an input RNA sequence $\mathbf{x} = (x_1, x_2, ..., x_L)$ of length $L$, we first embed each nucleotide using a learnable embedding matrix:

$$\mathbf{h}^{(0)} = \text{Embed}(\mathbf{x}) + \text{PE}(\mathbf{x})$$

where $\text{PE}$ denotes positional encodings. The hierarchical Mamba encoder then processes these embeddings through $K$ layers (default $K=4$), where each layer $k$ operates with a receptive field expansion factor of $2^k$:

$$\mathbf{h}^{(k)} = \text{BiMamba}_k(\mathbf{h}^{(k-1)}; r_k)$$

where $r_k = r_0 \cdot 2^k$ represents the effective receptive field at layer $k$, with base receptive field $r_0 = 8$ nucleotides.

Each bidirectional Mamba layer combines forward and backward state space models:

$$\mathbf{h}^{(k)}_{\text{fwd}} = \text{SSM}_{\text{fwd}}(\mathbf{h}^{(k-1)})$$
$$\mathbf{h}^{(k)}_{\text{bwd}} = \text{SSM}_{\text{bwd}}(\text{flip}(\mathbf{h}^{(k-1)}))$$
$$\mathbf{h}^{(k)} = \text{LayerNorm}(\mathbf{h}^{(k)}_{\text{fwd}} + \text{flip}(\mathbf{h}^{(k)}_{\text{bwd}}) + \mathbf{h}^{(k-1)})$$

The state space model (SSM) at each layer follows the selective scan mechanism:

$$\mathbf{h}'_t = \bar{\mathbf{A}}_t \mathbf{h}'_{t-1} + \bar{\mathbf{B}}_t x_t$$
$$y_t = \mathbf{C}_t \mathbf{h}'_t$$

where $\bar{\mathbf{A}}_t$ and $\bar{\mathbf{B}}_t$ are discretized state matrices computed from input-dependent parameters, enabling selective information propagation.

The hierarchical design ensures that:
- Layer 1 captures local motifs (8-16 nt): binding sites, splice signals
- Layer 2 captures short-range interactions (16-32 nt): stem-loops, hairpins
- Layer 3 captures domain-level patterns (32-64 nt): secondary structure domains
- Layer 4 captures global context (64-128+ nt): long-range interactions, tertiary contacts

#### 2.1.2 Structure Encoders

**Secondary Structure Encoder**: We encode RNA secondary structure as a graph where nodes represent nucleotides and edges represent base pairs. A graph neural network processes this representation:

$$\mathbf{s}^{(2D)} = \text{GNN}_{2D}(\mathbf{A}_{2D}, \mathbf{h}^{(0)})$$

where $\mathbf{A}_{2D}$ is the adjacency matrix derived from secondary structure annotations.

**Tertiary Structure Encoder**: For RNAs with available 3D structure (experimental or predicted), we employ an equivariant graph neural network operating on atomic coordinates:

$$\mathbf{s}^{(3D)} = \text{EGNN}_{3D}(\mathbf{X}_{coords}, \mathbf{h}^{(0)})$$

#### 2.1.3 Contrastive Cross-Modal Alignment

The contrastive learning module aligns representations from different modalities using the InfoNCE loss with biologically meaningful augmentations. For a batch of $N$ RNA molecules, let $\mathbf{z}^{seq}_i$ and $\mathbf{z}^{str}_i$ denote the sequence and structure embeddings for molecule $i$, obtained by pooling the respective encoder outputs:

$$\mathbf{z}^{seq}_i = \text{MeanPool}(\mathbf{h}^{(K)}_i)$$
$$\mathbf{z}^{str}_i = \text{MeanPool}(\mathbf{s}^{(2D)}_i \oplus \mathbf{s}^{(3D)}_i)$$

The contrastive loss is defined as:

$$\mathcal{L}_{contrast} = -\frac{1}{2N}\sum_{i=1}^{N}\left[\log\frac{\exp(\text{sim}(\mathbf{z}^{seq}_i, \mathbf{z}^{str}_i)/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\mathbf{z}^{seq}_i, \mathbf{z}^{str}_j)/\tau)} + \log\frac{\exp(\text{sim}(\mathbf{z}^{str}_i, \mathbf{z}^{seq}_i)/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\mathbf{z}^{str}_i, \mathbf{z}^{seq}_j)/\tau)}\right]$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity and $\tau = 0.07$ is the temperature parameter.

**Biological Augmentations**: We construct positive pairs using three biologically grounded augmentation strategies:

1. **Ortholog pairs**: Sequences from different species with conserved function (sourced from Zoonomia project)
2. **Splice isoforms**: Alternative transcript variants from the same gene
3. **Synonymous mutations**: Sequences with nucleotide changes that preserve codon meaning (for coding regions)

### 2.2 Data Collection and Preprocessing

**Training Data**: We compile a comprehensive dataset from multiple sources:

- **RNAcentral**: 5 million non-redundant RNA sequences spanning all RNA types
- **Rfam**: 4,000+ RNA families with curated secondary structure annotations
- **PDB**: ~5,000 experimentally determined RNA 3D structures
- **Predicted structures**: AlphaFold-RNA predictions for sequences lacking experimental structures

**Preprocessing Pipeline**:
1. Sequence filtering: Remove sequences <50 nt or >10,000 nt; cluster at 80% identity
2. Secondary structure: Obtain from Rfam annotations or predict using ViennaRNA
3. Tertiary structure: Use experimental structures where available; predict using RhoFold for remaining
4. Ortholog mapping: Construct pairs using reciprocal best BLAST hits across species

### 2.3 Training Procedure

**Pre-training**: The model is trained with a combined objective:

$$\mathcal{L}_{total} = \mathcal{L}_{contrast} + \lambda_1 \mathcal{L}_{MLM} + \lambda_2 \mathcal{L}_{struct}$$

where $\mathcal{L}_{MLM}$ is masked language modeling loss (15% masking rate), $\mathcal{L}_{struct}$ is secondary structure prediction loss, and $\lambda_1 = \lambda_2 = 0.5$.

**Hyperparameters**:
- Model dimension: 512
- Number of layers: 4 (default configuration)
- Total parameters: ~100M
- Batch size: 256
- Learning rate: 1e-4 with cosine decay
- Training epochs: 100
- Hardware: 8× A100 GPUs, ~100 GPU-hours

### 2.4 Experimental Design

#### 2.4.1 Ablation Studies

We conduct systematic ablations to validate each component:

**A1: Architecture Depth**
- Configurations: 2, 4, 6 hierarchical layers
- Hypothesis: 4 layers optimal; fewer miss long-range patterns, more overfit

**A2: Modality Configurations**
- Configurations: sequence-only, sequence+2D, sequence+2D+3D
- Hypothesis: Each modality provides additive benefit

**A3: Alignment Methods**
- Configurations: contrastive (InfoNCE), reconstruction (MSE), hybrid
- Hypothesis: Contrastive alignment produces superior transfer

**A4: Hierarchical vs. Flat**
- Compare hierarchical Mamba (2x expansion) vs. flat Mamba (uniform receptive field)
- Critical test for primary hypothesis

#### 2.4.2 Benchmark Evaluation

**Structure Prediction**:
- Dataset: CASP-RNA test set, RNA-Puzzles
- Metrics: RMSD (Å), TM-score, GDT-TS
- Baseline: DGRNA (TM-score ~0.65)
- Target: TM-score ≥ 0.72

**Function Classification**:
- Dataset: BEACON benchmark (13 tasks)
- Metrics: AUC-ROC, accuracy, F1-score
- Baselines: DGRNA, HydraRNA, Orthrus, PlantRNA-FM
- Target: >84.5% mean accuracy

**Embedding Quality**:
- Evaluation: k-means clustering of RNA family embeddings
- Metric: Normalized Mutual Information (NMI)
- Target: NMI ≥ 0.8

**Transfer Efficiency**:
- Protocol: Fine-tune with 10%, 25%, 50%, 100% of task-specific data
- Metric: Samples needed for 90% of maximum performance
- Target: ≥15% reduction vs. baselines

#### 2.4.3 Statistical Analysis

All experiments use:
- Sample size: n ≥ 25 independent runs
- Statistical test: Paired t-test with Bonferroni correction
- Significance level: α = 0.05
- Effect size: Report Cohen's d
- Reporting: Mean ± standard deviation, 95% confidence intervals

### 2.5 Falsification Criteria

The hypothesis will be rejected if:
1. Hierarchical Mamba shows ≤5% improvement over flat Mamba (TM-score ≤ 0.68)
2. Contrastive alignment provides no benefit over reconstruction (NMI difference < 0.1)
3. Multimodal training shows no improvement over sequence-only
4. HiMamba-CL underperforms existing baselines on majority of BEACON tasks

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcomes**:
1. **Structure Prediction**: We expect HiMamba-CL to achieve TM-score ≥ 0.72 on RNA 3D structure prediction, representing a ≥10% relative improvement over the DGRNA baseline (0.65). This improvement stems from the hierarchical architecture's ability to capture long-range dependencies critical for tertiary structure formation.

2. **Function Classification**: We anticipate >84.5% mean accuracy across BEACON benchmark tasks, surpassing current state-of-the-art methods by 2.5%. The multimodal training enables the model to leverage both sequence patterns and structural features for functional annotation.

3. **Transfer Efficiency**: We expect ≥15% improvement in fine-tuning data efficiency, meaning HiMamba-CL will require 15% fewer labeled samples to achieve equivalent performance on new tasks. This efficiency gain results from the modality-invariant embeddings learned through contrastive alignment.

4. **Embedding Quality**: RNA embeddings should exhibit NMI ≥ 0.8 when clustered by functional family, demonstrating that the learned representations capture biologically meaningful relationships.

**Secondary Outcomes**:
- Validated hierarchical Mamba architecture for biological sequences
- Comprehensive ablation analysis quantifying contribution of each component
- Open-source codebase and pre-trained models for community use

### 3.2 Scientific Impact

This research will advance the field of AI for nucleic acids in several ways:

1. **Architectural Innovation**: HiMamba-CL establishes that hierarchical state space models, previously validated on continuous sensor data, transfer effectively to discrete biological sequences. This opens new directions for architecture design in computational biology.

2. **Multimodal Learning**: The contrastive cross-modal alignment framework provides a principled approach for integrating heterogeneous biological data types, applicable beyond RNA to other molecular modalities.

3. **Benchmark Contributions**: Our comprehensive evaluation across multiple tasks and datasets will provide valuable reference points for future RNA foundation model development.

### 3.3 Practical Applications

**RNA Therapeutics**: Improved structure prediction directly benefits the design of mRNA vaccines, where secondary structure influences translation efficiency and immunogenicity. Better functional predictions accelerate identification of therapeutic targets among non-coding RNAs.

**Drug Discovery**: The unified embeddings enable efficient virtual screening of RNA-targeting compounds by providing meaningful similarity metrics across diverse RNA types.

**Functional Genomics**: Transfer learning capabilities allow rapid annotation of newly discovered RNA transcripts, particularly valuable for characterizing the vast non-coding transcriptome.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

1. **Sequence Length**: Current architecture handles sequences up to 10,000 nt; longer transcripts require chunking with potential context loss. Future work will explore sparse attention mechanisms for full-length processing.

2. **Generative Capabilities**: HiMamba-CL is a discriminative model; extending to RNA design and generation represents an important future direction.

3. **Real-time Applications**: Pre-training requires substantial computational resources; model distillation could enable deployment in resource-constrained settings.

4. **Tertiary Structure Data**: Limited experimental 3D structures constrain the tertiary modality; as prediction methods improve, retraining with higher-quality structures will enhance performance.

In conclusion, HiMamba-CL represents a significant step toward unified RNA representation learning, combining architectural innovations in hierarchical state space models with principled multimodal alignment. Success in this research will establish new benchmarks for RNA foundation models and accelerate applications across therapeutics, functional genomics, and fundamental RNA biology.