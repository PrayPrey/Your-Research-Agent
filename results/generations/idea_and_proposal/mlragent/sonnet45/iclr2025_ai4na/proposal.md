# Multimodal Foundation Models for RNA Structure-Function Prediction via Contrastive Learning

## 1. Introduction

### Background

Ribonucleic acids (RNAs) play fundamental roles in cellular biology, functioning far beyond their traditional role as mere messengers between DNA and proteins. From catalytic ribozymes to regulatory microRNAs and long non-coding RNAs, these molecules exhibit remarkable structural and functional diversity. The intricate relationship between RNA sequence, structure, and function follows a hierarchical organization: primary sequences fold into secondary structures through canonical and non-canonical base pairing, which subsequently collapse into complex three-dimensional tertiary structures that ultimately determine biological function.

Despite significant advances in computational biology, current approaches to RNA modeling predominantly treat these hierarchical levels as independent problems. Sequence-based models excel at capturing evolutionary patterns but struggle with structural predictions. Structure prediction methods, while increasingly accurate for secondary structures, face substantial challenges in tertiary structure prediction due to the complex interplay of long-range interactions, non-canonical base pairs, and pseudoknots. Furthermore, the connection between structure and function remains largely unexplored in unified computational frameworks, limiting our ability to design RNA therapeutics with desired properties.

Recent breakthroughs in foundation models for biological sequences, such as RNA-FM trained on 23 million non-coding RNAs, demonstrate the power of self-supervised learning on unannotated data. However, these models primarily focus on sequence information, leaving rich structural and functional knowledge underutilized. Similarly, generative models like RiboGen have shown promise in co-generating RNA sequences and structures, but lack explicit functional reasoning capabilities. The emerging paradigm of multimodal learning, successfully applied in domains ranging from vision-language models to medical AI (as demonstrated by Med-Gemini), offers a compelling framework to bridge these gaps in RNA research.

### Research Objectives

This research proposes to develop **RNA-MultiModal** (RNA-MM), a comprehensive foundation model that jointly learns representations across four key modalities:

1. **Sequence modality**: Primary nucleotide sequences capturing evolutionary and compositional information
2. **Secondary structure modality**: Base-pairing patterns, stem-loops, and topological features
3. **Tertiary structure modality**: 3D atomic coordinates and geometric relationships
4. **Functional modality**: Binding sites, catalytic activities, subcellular localization, and interaction partners

The specific objectives are:

- **Objective 1**: Design and implement hierarchical encoders that capture multi-scale structural dependencies from sequence to secondary to tertiary structure
- **Objective 2**: Develop contrastive learning frameworks to align representations across modalities, enabling cross-modal knowledge transfer
- **Objective 3**: Create a unified embedding space that enables novel downstream tasks including zero-shot function prediction, structure-conditioned sequence design, and multi-objective RNA therapeutic optimization
- **Objective 4**: Validate the model on diverse RNA families and demonstrate superior performance on structure prediction, function annotation, and inverse design tasks

### Significance

This research addresses critical gaps at the intersection of AI and nucleic acid biology with far-reaching implications:

**Scientific Impact**: By learning joint representations across RNA modalities, this work will advance our fundamental understanding of structure-function relationships, potentially revealing novel RNA functional categories and design principles that are currently invisible to single-modality approaches.

**Therapeutic Applications**: The unified embedding space will enable rational design of RNA therapeutics (mRNA vaccines, siRNAs, aptamers) with simultaneously optimized structural stability, target specificity, and functional efficacy—a capability currently unavailable in existing tools.

**Methodological Contributions**: The hierarchical contrastive learning framework developed here will establish new paradigms for multimodal biological foundation models, with potential applications extending to DNA-RNA-protein interactions and beyond.

**Accessibility**: By enabling zero-shot predictions on novel RNA sequences without requiring extensive experimental characterization, this model will democratize RNA research and accelerate discovery in resource-limited settings.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

**Dataset Construction**:

We will construct a comprehensive multimodal RNA dataset by integrating data from multiple sources:

1. **Sequence Data**: 
   - Primary source: RNAcentral (50M+ sequences)
   - Supplementary: Rfam families, ncRNA databases
   - Preprocessing: Clustering at 90% sequence identity to reduce redundancy while maintaining diversity

2. **Secondary Structure Data**:
   - Experimentally validated: RNA STRAND database, bpRNA-1m dataset
   - Computationally predicted: ViennaRNA predictions for sequences lacking experimental data
   - Representation: Dot-bracket notation, base-pairing probability matrices, and structural motif annotations

3. **Tertiary Structure Data**:
   - Experimental structures: Protein Data Bank (PDB) - RNA-only and RNA-protein complexes (~5,000 structures)
   - Predicted structures: RNA3DB, RNAsolo predictions
   - Representation: All-atom coordinates, backbone torsion angles, distance matrices

4. **Functional Annotations**:
   - Gene Ontology (GO) terms for molecular function, biological process
   - Interaction data: RNA-protein binding sites from POSTAR, RBP binding motifs
   - Localization data: RNALocate database
   - Chemical modifications: MODOMICS database

**Data Alignment Protocol**:

For each RNA instance, we create multimodal tuples $(s, ss, ts, f)$ where available, representing sequence, secondary structure, tertiary structure, and function respectively. For incomplete tuples (missing modalities), we employ masking strategies during training.

### 2.2 Model Architecture

**RNA-MultiModal** consists of four specialized encoders, a cross-modal fusion module, and contrastive alignment objectives.

#### 2.2.1 Modality-Specific Encoders

**Sequence Encoder ($E_{seq}$)**:

Building upon transformer architectures, we employ a bidirectional encoder with nucleotide-level tokenization:

$$h_{seq} = E_{seq}(s) = \text{Transformer}(\text{Embed}(s)) \in \mathbb{R}^{L \times d}$$

where $s = [s_1, s_2, ..., s_L]$ represents the nucleotide sequence of length $L$, and $d$ is the embedding dimension (set to 768). We incorporate positional encodings and apply learned nucleotide embeddings with vocabulary {A, U, G, C, N, [CLS], [MASK]}.

**Secondary Structure Encoder ($E_{ss}$)**:

We design a hierarchical encoder that processes both sequential (dot-bracket) and relational (base-pairing matrix) representations:

$$h_{ss} = E_{ss}(ss) = \text{GCN}(BP) \oplus \text{LSTM}(DB) \in \mathbb{R}^{L \times d}$$

where $BP \in \mathbb{R}^{L \times L}$ is the base-pairing probability matrix, $DB$ is the dot-bracket sequence, GCN denotes a graph convolutional network operating on the base-pairing graph, and $\oplus$ represents concatenation followed by projection.

**Tertiary Structure Encoder ($E_{ts}$)**:

We employ an equivariant graph neural network (EGNN) to process 3D geometric information while preserving rotational and translational invariance:

$$h_{ts} = E_{ts}(X, E) = \text{EGNN}(X, E) \in \mathbb{R}^{L \times d}$$

where $X \in \mathbb{R}^{L \times 3}$ represents nucleotide coordinates (C4' carbon positions), and $E$ represents edge features including inter-nucleotide distances and bond types.

**Function Encoder ($E_{func}$)**:

Functional annotations are encoded using a multi-label embedding approach:

$$h_{func} = E_{func}(f) = \text{MLP}(\text{MultiHotEmbed}(f)) \in \mathbb{R}^{d}$$

where GO terms, binding sites, and other annotations are represented as multi-hot vectors and projected to the shared embedding space.

#### 2.2.2 Hierarchical Cross-Modal Attention

To capture dependencies across structural hierarchies, we implement directed attention mechanisms:

$$h_{seq \rightarrow ss} = \text{CrossAttn}(Q=h_{seq}, K=h_{ss}, V=h_{ss})$$

$$h_{ss \rightarrow ts} = \text{CrossAttn}(Q=h_{ss}, K=h_{ts}, V=h_{ts})$$

$$h_{unified} = \text{Concat}(h_{seq}, h_{seq \rightarrow ss}, h_{ss \rightarrow ts}, h_{ts}) \cdot W_{proj}$$

where $W_{proj}$ projects the concatenated representations to a unified embedding space.

#### 2.2.3 Contrastive Learning Objectives

**Intra-Modal Contrastive Loss**:

For each modality, we apply instance discrimination to learn distinctive representations:

$$\mathcal{L}_{intra}^{m} = -\log \frac{\exp(sim(h_i^m, h_j^m)/\tau)}{\sum_{k=1}^{N} \exp(sim(h_i^m, h_k^m)/\tau)}$$

where $m \in \{seq, ss, ts, func\}$, $(i,j)$ form a positive pair (augmented views of the same RNA), and $\tau$ is a temperature parameter.

**Cross-Modal Alignment Loss**:

We align representations from different modalities of the same RNA molecule:

$$\mathcal{L}_{align} = \sum_{(m_1, m_2) \in \mathcal{P}} -\log \frac{\exp(sim(h_i^{m_1}, h_i^{m_2})/\tau)}{\sum_{k=1}^{N} \exp(sim(h_i^{m_1}, h_k^{m_2})/\tau)}$$

where $\mathcal{P} = \{(seq, ss), (ss, ts), (seq, func), (ts, func)\}$ represents modality pairs.

**Hierarchical Consistency Loss**:

To enforce the natural hierarchy sequence → secondary → tertiary structure:

$$\mathcal{L}_{hier} = \|h_{seq} \cdot W_1 - h_{ss}\|_2^2 + \|h_{ss} \cdot W_2 - h_{ts}\|_2^2$$

where $W_1, W_2$ are learnable transformation matrices.

**Total Training Objective**:

$$\mathcal{L}_{total} = \lambda_1 \sum_m \mathcal{L}_{intra}^{m} + \lambda_2 \mathcal{L}_{align} + \lambda_3 \mathcal{L}_{hier} + \lambda_4 \mathcal{L}_{mask}$$

where $\mathcal{L}_{mask}$ represents masked modality prediction losses (similar to BERT), and $\lambda_i$ are weighting hyperparameters.

### 2.3 Training Strategy

**Phase 1: Modality-Specific Pre-training** (100 epochs)
- Train individual encoders on large-scale single-modality data
- Apply modality-specific augmentations (sequence mutations, structure perturbations)

**Phase 2: Multimodal Alignment** (50 epochs)
- Freeze lower layers of modality encoders
- Train cross-modal attention and contrastive objectives on aligned multimodal tuples
- Gradually increase temperature $\tau$ from 0.07 to 0.1

**Phase 3: End-to-End Fine-tuning** (30 epochs)
- Unfreeze all parameters
- Joint optimization with full objective
- Apply curriculum learning: start with complete modality tuples, gradually introduce missing modalities

**Optimization Details**:
- Optimizer: AdamW with learning rate 1e-4, weight decay 0.01
- Batch size: 256 (with gradient accumulation for effective batch size of 2048)
- Hardware: 8× NVIDIA A100 GPUs (80GB)
- Mixed precision training (FP16)

### 2.4 Experimental Design and Evaluation

#### 2.4.1 Downstream Tasks

**Task 1: RNA Tertiary Structure Prediction**

Given sequence and secondary structure, predict 3D coordinates:
- Datasets: RNA-Puzzles, CASP-RNA targets
- Metrics: Template Modeling Score (TM-score), Root Mean Square Deviation (RMSD), Interaction Network Fidelity (INF)
- Baselines: RosettaFold-NA, RhoFold, RNAComposer

**Task 2: Zero-Shot Function Prediction**

Predict GO terms and binding partners for novel RNAs without task-specific training:
- Datasets: Hold-out RNA families from Rfam
- Metrics: Precision@k, Recall@k, F1-score, Area Under ROC Curve (AUROC)
- Baselines: DeepGO, RNA-FM fine-tuned, sequence similarity transfer

**Task 3: Structure-Conditioned Sequence Design**

Generate sequences that fold into target structures with desired functions:
- Datasets: Synthetic design targets, experimentally validated designs from Eterna
- Metrics: Structure recovery rate, sequence diversity, predicted function retention, structural stability (free energy)
- Baselines: RiboGen, RNA inverse folding algorithms, evolutionary algorithms

**Task 4: RNA-Protein Binding Site Prediction**

Identify nucleotide positions involved in protein binding:
- Datasets: RBPsuite, POSTAR validation sets
- Metrics: AUROC, AUPRC, Matthew's Correlation Coefficient (MCC)
- Baselines: GraphProt, iDeepV, RNANetMotif

#### 2.4.2 Ablation Studies

To validate design choices, we conduct systematic ablations:

1. **Modality Ablation**: Remove individual modalities (sequence-only, structure-only, etc.)
2. **Architecture Ablation**: Replace hierarchical attention with simple concatenation
3. **Objective Ablation**: Remove contrastive, alignment, or hierarchical losses individually
4. **Scale Ablation**: Train on 10%, 50%, 100% of data to assess data efficiency

#### 2.4.3 Interpretability Analysis

**Attention Visualization**: Generate attention heatmaps showing cross-modal dependencies for well-characterized RNAs (tRNA, riboswitches)

**Embedding Space Analysis**: 
- t-SNE/UMAP visualization colored by RNA family, function, and structural class
- Measure cluster purity and silhouette scores

**Motif Discovery**: Use integrated gradients to identify sequence and structural motifs most predictive of specific functions

### 2.5 Validation Protocol

**Cross-Validation**: 5-fold cross-validation stratified by RNA family

**Temporal Validation**: Train on structures deposited before 2020, test on 2020-2024 structures

**Family-Level Holdout**: Test generalization by holding out entire RNA families unseen during training

**Statistical Significance**: Report mean ± std across 3 independent runs with different random seeds; use Wilcoxon signed-rank tests for baseline comparisons

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Quantitative Performance Improvements**:

Based on preliminary experiments and literature benchmarks, we anticipate:

1. **Tertiary Structure Prediction**: 15-20% improvement in TM-score over current state-of-the-art (RosettaFold-NA), particularly for RNAs with complex pseudoknots and long-range interactions

2. **Function Prediction**: AUROC >0.85 for zero-shot GO term prediction, compared to 0.70-0.75 for transfer learning baselines

3. **Sequence Design**: >80% structure recovery rate for designed sequences (compared to 60-70% for existing methods), with 3-5× greater sequence diversity

4. **Data Efficiency**: Achieve comparable performance to single-modality models using only 30-50% of the training data, demonstrating effective cross-modal knowledge transfer

**Qualitative Outcomes**:

1. **Unified Embedding Space**: A shared representation space enabling novel queries such as "find RNAs with similar function but different structures" or "design sequences structurally similar to A but functionally similar to B"

2. **Interpretable Structure-Function Rules**: Discovery of previously unrecognized structural motifs associated with specific functions through attention analysis and embedding clustering

3. **Multi-Objective Design Tool**: A practical system allowing researchers to specify constraints across multiple modalities simultaneously (e.g., "design an RNA with stem-loop at positions 10-30, binding affinity to protein X, and nuclear localization")

**Model Artifacts**:

1. Pre-trained RNA-MM foundation model with weights publicly released
2. Multimodal RNA dataset with aligned sequence-structure-function annotations (estimated 100K aligned instances)
3. Interactive web interface for structure prediction, function annotation, and sequence design
4. Comprehensive benchmark suite for evaluating multimodal RNA models

### 3.2 Scientific Impact

**Advancing RNA Biology**: 

The joint modeling of structure and function will enable systematic investigation of previously intractable questions: How do subtle structural variations modulate function? What are the minimal structural requirements for specific catalytic activities? This model will serve as a hypothesis generation engine for experimental RNA biologists.

**Bridging Computational Approaches**: 

By demonstrating the value of multimodal integration, this work will catalyze a paradigm shift from isolated task-specific models to holistic foundation models in nucleic acid research. The methodologies developed here (hierarchical encoders, cross-modal contrastive learning) will establish templates for future DNA-RNA-protein multimodal systems.

**Expanding Foundation Model Capabilities**: 

While foundation models have transformed NLP and computer vision, their application to structured biological data remains nascent. This work will contribute architectural innovations (equivariant encoders with cross-modal attention) and training strategies (hierarchical contrastive learning) applicable to broader scientific domains involving multi-scale, multi-modal data.

### 3.3 Therapeutic and Biotechnological Impact

**RNA Therapeutics Design**:

The pharmaceutical industry faces critical challenges in RNA therapeutic development: mRNA vaccines require optimization of stability and translation efficiency, siRNAs need precise target specificity to avoid off-target effects, and RNA aptamers must achieve high binding affinity. RNA-MM's multi-objective design capability directly addresses these challenges by enabling simultaneous optimization across structural stability (via tertiary structure modeling), target binding (via function prediction), and deliverability (via localization prediction).

**Concrete Applications**:

1. **mRNA Vaccine Optimization**: Design 5' and 3' UTRs with enhanced stability and translation efficiency while maintaining immunogenicity
2. **siRNA Specificity Enhancement**: Generate sequences with minimal off-target binding predicted through structure-aware functional modeling
3. **Aptamer Engineering**: Accelerate aptamer discovery by predicting binding partners from structure, reducing experimental screening by 10-100×

**Accelerating Discovery Timelines**:

By enabling in silico screening of millions of candidate RNAs with predicted structure-function properties, RNA-MM could compress the design-test-optimize cycle from months to weeks, substantially reducing development costs and time-to-clinic for RNA therapeutics.

### 3.4 Broader Impact and Accessibility

**Democratizing RNA Research**:

The zero-shot prediction capabilities will enable researchers without access to expensive structural biology facilities (X-ray crystallography, cryo-EM) to obtain structural and functional insights for their RNAs of interest. This is particularly impactful for scientists in resource-limited settings and for studying non-model organisms.

**Educational Applications**:

The interpretable attention visualizations and embedding space explorations will serve as powerful educational tools, helping students and researchers build intuition about RNA structure-function relationships through interactive exploration.

**Open Science Commitment**:

All model weights, training code, datasets, and benchmarks will be released under permissive open-source licenses (MIT/Apache 2.0). We will establish a community-driven platform for continuous model improvement through federated contributions of new RNA data.

**Ethical Considerations**:

While RNA-MM enhances beneficial applications, its design capabilities could theoretically be misused for creating harmful RNA constructs. We will implement responsible release protocols including usage guidelines, engage with biosecurity experts, and potentially implement safeguards against generating sequences with predicted pathogenic properties.

### 3.5 Future Extensions

This foundational work opens numerous research directions:

1. **Dynamic RNA Modeling**: Extending to model conformational ensembles and RNA dynamics
2. **RNA-Protein Co-Design**: Expanding to joint RNA-protein interaction modeling
3. **Active Learning Integration**: Coupling with robotic experimentation for closed-loop design-test cycles
4. **Evolutionary Modeling**: Incorporating evolutionary constraints to predict RNA fitness landscapes

By establishing RNA-MM as a comprehensive foundation model, this research will position nucleic acids as a premier application domain for AI, catalyzing sustained interdisciplinary collaboration between machine learning and RNA biology communities.