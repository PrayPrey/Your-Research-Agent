# Research Proposal: Multi-Scale Foundation Model for RNA Therapeutic Design with Hierarchical Structure-Function Learning

## 1. Introduction

### Background

RNA therapeutics have emerged as a transformative modality in modern medicine, exemplified by the rapid development and deployment of mRNA vaccines during the COVID-19 pandemic. Beyond vaccines, therapeutic RNAs—including messenger RNAs (mRNAs), antisense oligonucleotides (ASOs), and small interfering RNAs (siRNAs)—offer unprecedented opportunities for treating genetic disorders, cancers, and infectious diseases. However, the rational design of therapeutic RNAs remains challenging due to the complex interplay between sequence composition, structural folding, and biological function.

Current AI approaches for therapeutic RNA design suffer from a fundamental limitation: they typically optimize individual components in isolation. For instance, codon optimization algorithms focus solely on maximizing translation elongation rates without considering how codon choices affect mRNA secondary structure and stability. Similarly, UTR design methods often neglect the downstream effects on ribosome loading and tissue-specific expression. This fragmented approach fails to capture the hierarchical dependencies inherent in RNA biology—where nucleotide-level modifications propagate through local structural motifs to global tertiary conformations, ultimately determining cellular function.

Recent advances in foundation models have demonstrated the power of large-scale pre-training for capturing complex patterns across diverse data modalities. In the protein domain, models like AlphaFold2 and ESM have revolutionized structure prediction and design. However, RNA presents unique challenges: the conformational flexibility of RNA molecules, the importance of non-canonical base pairing, and the context-dependent nature of RNA function in different cellular environments. Existing work such as RDesign has shown promise in leveraging hierarchical representations for RNA design, while RiboPO has demonstrated the value of reinforcement learning from physical feedback. Yet, a unified foundation model that jointly learns across multiple RNA modalities and structural scales remains elusive.

### Research Objectives

This proposal introduces **RNAFoundation**, a hierarchical foundation model designed to address the limitations of current RNA therapeutic design approaches. Our primary objectives are:

1. **Develop a multi-scale transformer architecture** that explicitly models RNA at sequence, secondary structure, and tertiary structure levels through hierarchical attention mechanisms.

2. **Create structure-aware tokenization schemes** that encode both sequence information and predicted local structural features, enabling the model to learn structure-function relationships.

3. **Enable conditional generation** of therapeutic RNA elements (UTRs, coding sequences, regulatory elements) given target cell types, desired expression profiles, and stability requirements.

4. **Establish a reinforcement learning framework** for fine-tuning from experimental feedback, including ribosome profiling data and stability assays.

### Significance

This research addresses critical gaps in AI-driven drug discovery for RNA therapeutics. By developing a unified foundation model that captures multi-scale structure-function relationships, we aim to:

- Accelerate the design cycle for mRNA vaccines and therapeutics by enabling in silico optimization across multiple objectives simultaneously
- Discover novel regulatory elements with tissue-specific activity, expanding the toolkit for targeted gene expression
- Provide interpretable insights into RNA structure-function relationships, advancing fundamental biological understanding
- Establish a foundation for transfer learning across diverse RNA therapeutic modalities

## 2. Methodology

### 2.1 Data Collection and Preprocessing

**Primary Data Sources:**
We will curate a comprehensive RNA dataset from multiple sources:

1. **Sequence Data**: RefSeq mRNA sequences (~200,000), lncRNA sequences from GENCODE (~60,000), and regulatory RNA elements from UTRdb and REDfly databases
2. **Structural Data**: Experimentally determined RNA structures from the Protein Data Bank (~5,000 structures), SHAPE/DMS probing data from RMDB (~10,000 experiments)
3. **Functional Data**: Ribosome profiling datasets from GEO (>500 experiments), translation efficiency measurements, mRNA half-life data, and tissue-specific expression profiles from GTEx

**Preprocessing Pipeline:**
- Sequences are tokenized using a hybrid scheme combining k-mer tokens (k=3,4,5) with structure-aware tokens
- Secondary structures predicted using ViennaRNA and LinearFold algorithms
- Tertiary structure features extracted from experimental data or predicted using existing tools
- Expression and stability data normalized across experiments using quantile normalization

### 2.2 Model Architecture

**Hierarchical Multi-Scale Transformer:**

RNAFoundation employs a novel hierarchical architecture with three interconnected levels:

**Level 1 - Nucleotide Encoder:**
The base level processes individual nucleotides with their local structural context:

$$\mathbf{h}_i^{(1)} = \text{TransformerBlock}^{(1)}(\mathbf{e}_i + \mathbf{p}_i + \mathbf{s}_i)$$

where $\mathbf{e}_i$ is the nucleotide embedding, $\mathbf{p}_i$ is the positional encoding, and $\mathbf{s}_i$ is the local structure encoding derived from predicted base-pairing probabilities.

**Level 2 - Motif Encoder:**
The motif level aggregates nucleotide representations into structural motifs (stems, loops, bulges):

$$\mathbf{h}_j^{(2)} = \text{TransformerBlock}^{(2)}\left(\text{Pool}_{\text{motif}}\left(\{\mathbf{h}_i^{(1)}\}_{i \in M_j}\right)\right)$$

where $M_j$ represents the set of nucleotides belonging to motif $j$, and $\text{Pool}_{\text{motif}}$ uses attention-weighted pooling based on structural importance.

**Level 3 - Domain Encoder:**
The domain level captures global tertiary interactions and long-range dependencies:

$$\mathbf{h}_k^{(3)} = \text{TransformerBlock}^{(3)}\left(\text{Pool}_{\text{domain}}\left(\{\mathbf{h}_j^{(2)}\}_{j \in D_k}\right) + \mathbf{c}_k\right)$$

where $\mathbf{c}_k$ represents cellular context embeddings (cell type, subcellular localization).

**Cross-Scale Attention Mechanism:**
To enable information flow across scales, we introduce bidirectional cross-attention:

$$\mathbf{A}^{(l \rightarrow l+1)} = \text{softmax}\left(\frac{\mathbf{Q}^{(l+1)} (\mathbf{K}^{(l)})^T}{\sqrt{d_k}}\right) \mathbf{V}^{(l)}$$

$$\mathbf{A}^{(l+1 \rightarrow l)} = \text{softmax}\left(\frac{\mathbf{Q}^{(l)} (\mathbf{K}^{(l+1)})^T}{\sqrt{d_k}}\right) \mathbf{V}^{(l+1)}$$

**Structure-Aware Tokenization:**
We develop a novel tokenization scheme that encodes structural information:

$$\mathbf{s}_i = \text{MLP}\left([\mathbf{p}_{bp}(i); \mathbf{f}_{loop}(i); \mathbf{a}_{access}(i)]\right)$$

where $\mathbf{p}_{bp}(i)$ encodes base-pairing probabilities, $\mathbf{f}_{loop}(i)$ indicates loop membership, and $\mathbf{a}_{access}(i)$ represents predicted solvent accessibility.

### 2.3 Pre-training Objectives

**Multi-Task Self-Supervised Learning:**
RNAFoundation is pre-trained with three complementary objectives:

**Objective 1 - Masked Language Modeling (MLM) with Structure Constraints:**
$$\mathcal{L}_{\text{MLM}} = -\sum_{i \in \mathcal{M}} \log P(x_i | \mathbf{x}_{\backslash \mathcal{M}}, \mathbf{S})$$

where $\mathcal{M}$ is the set of masked positions and $\mathbf{S}$ represents structural constraints.

**Objective 2 - Structure Prediction:**
$$\mathcal{L}_{\text{struct}} = \text{BCE}\left(\hat{\mathbf{P}}_{bp}, \mathbf{P}_{bp}^*\right) + \lambda_1 \|\hat{\mathbf{T}} - \mathbf{T}^*\|_2$$

where $\hat{\mathbf{P}}_{bp}$ is the predicted base-pairing probability matrix and $\hat{\mathbf{T}}$ represents predicted tertiary contact maps.

**Objective 3 - Function Prediction:**
$$\mathcal{L}_{\text{func}} = \text{MSE}(\hat{y}_{\text{TE}}, y_{\text{TE}}^*) + \lambda_2 \text{MSE}(\hat{y}_{\text{stability}}, y_{\text{stability}}^*)$$

predicting translation efficiency (TE) and stability from sequence and structure representations.

**Combined Pre-training Loss:**
$$\mathcal{L}_{\text{pretrain}} = \mathcal{L}_{\text{MLM}} + \alpha \mathcal{L}_{\text{struct}} + \beta \mathcal{L}_{\text{func}}$$

### 2.4 Conditional Generation Framework

For therapeutic RNA design, we implement conditional generation using a decoder architecture:

$$P(\mathbf{x} | \mathbf{c}, \mathbf{y}) = \prod_{t=1}^{T} P(x_t | x_{<t}, \mathbf{c}, \mathbf{y})$$

where $\mathbf{c}$ represents cellular context (target tissue, expression system) and $\mathbf{y}$ specifies desired properties (stability, immunogenicity, translation efficiency).

**Controllable Generation via Guided Diffusion:**
We additionally implement a discrete diffusion approach for sequence generation:

$$q(\mathbf{x}_t | \mathbf{x}_{t-1}) = \text{Cat}(\mathbf{x}_t; \mathbf{x}_{t-1} \mathbf{Q}_t)$$

with guidance from property predictors:

$$p_\theta(\mathbf{x}_{t-1} | \mathbf{x}_t, \mathbf{y}) \propto p_\theta(\mathbf{x}_{t-1} | \mathbf{x}_t) \cdot p_\phi(\mathbf{y} | \mathbf{x}_{t-1})^\gamma$$

### 2.5 Reinforcement Learning from Experimental Feedback

Following the approach of RiboPO, we implement preference optimization from physical and experimental feedback:

**Reward Model:**
$$R(\mathbf{x}) = w_1 R_{\text{stability}}(\mathbf{x}) + w_2 R_{\text{structure}}(\mathbf{x}) + w_3 R_{\text{expression}}(\mathbf{x})$$

**Policy Optimization:**
Using Direct Preference Optimization (DPO):

$$\mathcal{L}_{\text{DPO}} = -\mathbb{E}_{(\mathbf{x}^+, \mathbf{x}^-) \sim \mathcal{D}} \left[\log \sigma\left(\beta \log \frac{\pi_\theta(\mathbf{x}^+)}{\pi_{\text{ref}}(\mathbf{x}^+)} - \beta \log \frac{\pi_\theta(\mathbf{x}^-)}{\pi_{\text{ref}}(\mathbf{x}^-)}\right)\right]$$

where preference pairs $(\mathbf{x}^+, \mathbf{x}^-)$ are constructed from experimental validation results.

### 2.6 Experimental Validation

**In Silico Validation:**
1. **Structure Prediction Accuracy**: Evaluate on held-out RNA structures using F1-score for base pairs and RMSD for tertiary structures
2. **Translation Efficiency Prediction**: Pearson correlation on ribosome profiling datasets
3. **Generative Quality**: Assess novelty, validity, and property distributions of generated sequences

**Benchmark Comparisons:**
- Compare against RDesign, RiboGen, and conventional codon optimization tools
- Evaluate on standardized benchmark from RDesign paper

**Wet-Lab Validation (Collaboration):**
1. **Reporter Assays**: Test generated 5' UTRs using dual-luciferase reporters in HEK293 and tissue-specific cell lines
2. **Ribosome Profiling**: Validate predicted translation efficiency for top candidates
3. **Stability Measurements**: Assess mRNA half-life using actinomycin D chase experiments

**Evaluation Metrics:**
- Structure prediction: Precision, Recall, F1 for base pairs; TM-score for 3D structures
- Property prediction: Pearson/Spearman correlation, RMSE
- Generation: Validity rate, diversity (pairwise sequence identity), property improvement over baselines
- Experimental: Fold-improvement in expression, correlation between predicted and measured properties

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Performance Improvements**: We anticipate achieving 2-3x improvement in translation efficiency prediction accuracy compared to existing methods, with Pearson correlations exceeding 0.7 on held-out ribosome profiling data.

2. **Novel Regulatory Elements**: Generation of synthetic 5' UTRs with tissue-specific activity, demonstrating >5-fold expression differences between target and off-target cell types.

3. **Unified Design Platform**: A publicly available foundation model capable of designing mRNAs, ASOs, and regulatory RNAs within a single framework.

4. **Interpretable Insights**: Identification of novel sequence-structure motifs associated with high translation efficiency and stability, advancing mechanistic understanding.

### Broader Impact

**Scientific Impact:**
- Establish new paradigms for multi-scale representation learning in RNA biology
- Provide interpretable models that can generate testable hypotheses about RNA function

**Therapeutic Impact:**
- Accelerate development of next-generation mRNA vaccines with improved immunogenicity profiles
- Enable design of cell-type-specific gene therapies with reduced off-target effects
- Reduce experimental iteration cycles from months to weeks through accurate in silico optimization

**Community Resources:**
- Release pre-trained model weights and fine-tuning code
- Publish curated benchmark datasets for RNA therapeutic design
- Develop user-friendly web interface for non-expert users

This research directly addresses the workshop's goals of bridging AI and emerging drug modalities, specifically advancing AI for therapeutic RNAs while contributing foundational model methodologies applicable across drug discovery. By integrating multi-scale structural understanding with conditional generation capabilities, RNAFoundation represents a significant step toward automated, rational design of RNA therapeutics.