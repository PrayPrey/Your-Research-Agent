# Research Proposal: Hierarchical Contrastive Learning for Multi-Scale Biological Representations

## 1. Introduction

### Background

Biological systems are inherently hierarchical, with information flowing across multiple scales—from genomic sequences that encode proteins, to proteins that orchestrate cellular functions, to cells that constitute tissues and organisms. Understanding these cross-scale dependencies is fundamental to deciphering how genetic variations manifest as phenotypic changes, how molecular perturbations propagate through cellular networks, and ultimately how diseases arise from molecular dysfunction. The emergence of large-scale biological datasets, including the JUMP Cell Painting Consortium (JUMP-CP), Human Cell Atlas, and comprehensive protein structure databases, has created unprecedented opportunities for machine learning approaches to model these complex biological relationships.

Foundation models for biological data have shown remarkable success in capturing patterns within individual biological scales. Protein language models like ESM-2 have demonstrated that evolutionary information encoded in protein sequences can predict three-dimensional structures with high accuracy (Lin et al., 2022). Similarly, models for single-cell transcriptomics have enabled cell type annotation and trajectory inference. However, these models predominantly operate at a single biological scale, treating each level of biological organization in isolation. This siloed approach fundamentally limits our ability to understand how information propagates across scales—how a single nucleotide polymorphism affects protein function, cellular behavior, and ultimately organism-level phenotypes.

Recent advances in hierarchical representation learning offer promising directions for addressing this challenge. The HIPPO framework (Liu et al., 2025) demonstrated that hierarchical contrastive learning can capture structured relationships among protein functional classes, enabling zero-shot transfer across species. Similarly, hierarchy-preserving contrastive learning for medical imaging (Khan, 2025) showed that embedding taxonomic relationships directly into training objectives improves representation quality. The bidirectional hierarchical fusion framework for protein multimodal learning (Liu et al., 2025) established that attention-based mechanisms can effectively integrate information across different representation modalities. These developments, combined with advances in hyperbolic representation learning for biological taxonomies (Gong et al., 2025), suggest that explicitly modeling hierarchical biological relationships could yield more meaningful and generalizable representations.

### Research Objectives

This proposal introduces a Hierarchical Contrastive Learning framework for Multi-Scale Biological Representations (HCL-Bio) that explicitly models cross-scale biological relationships through scale-bridging representations. Our primary objectives are:

1. **Develop scale-specific encoders** with modality-appropriate architectures that capture the unique characteristics of genomic sequences, protein structures, single-cell transcriptomics, and cellular morphology data.

2. **Design cross-scale contrastive objectives** that align representations between adjacent biological scales using known biological mappings as supervision, enabling the learning of representations that capture mechanistic relationships across scales.

3. **Create scale-conditioned prediction heads** that enable bidirectional inference—from molecular perturbations to cellular phenotypes (upward) and from observed phenotypes to potential molecular mechanisms (downward).

4. **Establish rigorous evaluation protocols** using multi-scale perturbation datasets to assess whether learned representations capture biologically meaningful cross-scale dependencies.

### Significance

This research addresses a critical gap in biological foundation models by explicitly modeling the hierarchical organization of living systems. Success in this endeavor would provide: (1) representations that generalize across biological scales, enabling transfer learning from data-rich scales (e.g., genomics) to data-sparse scales (e.g., tissue phenotypes); (2) interpretable cross-scale embeddings that reveal mechanistic links between genetic variants and phenotypic outcomes; (3) a foundational component for virtual cell simulators that require modeling interactions across multiple biological scales. This work directly addresses the LMRL workshop's focus on multiscale representation learning and represents a concrete step toward foundation models that capture the full complexity of biological systems.

## 2. Methodology

### 2.1 Framework Overview

HCL-Bio consists of three main components: (1) scale-specific encoders $\{E_s\}_{s=1}^{S}$ for $S$ biological scales, (2) a cross-scale alignment module using hierarchical contrastive objectives, and (3) scale-conditioned prediction heads for bidirectional inference. We consider four primary scales: genomic sequences ($s=1$), protein structures ($s=2$), single-cell transcriptomics ($s=3$), and cellular morphology ($s=4$).

### 2.2 Scale-Specific Encoders

Each encoder is designed to capture the unique characteristics of its respective biological modality:

**Genomic Encoder ($E_1$):** We employ a transformer-based architecture with nucleotide-level tokenization. Given a genomic sequence $x_1 \in \{A, C, G, T\}^{L_1}$, the encoder produces:
$$z_1 = E_1(x_1) = \text{TransformerPool}(\text{NucleotideEmbed}(x_1)) \in \mathbb{R}^d$$
where $d$ is the unified embedding dimension across all scales.

**Protein Structure Encoder ($E_2$):** We utilize a geometric graph neural network that processes protein structures as graphs $G = (V, E)$ where nodes represent residues and edges capture spatial proximity:
$$z_2 = E_2(G) = \text{ReadOut}(\text{SE(3)-GNN}(G)) \in \mathbb{R}^d$$
The SE(3)-equivariant architecture ensures representations are invariant to rotations and translations.

**Single-Cell Transcriptomics Encoder ($E_3$):** For gene expression profiles $x_3 \in \mathbb{R}^{G}$ where $G$ is the number of genes, we use a transformer encoder with gene-wise tokenization:
$$z_3 = E_3(x_3) = \text{TransformerPool}(\text{GeneEmbed}(x_3)) \in \mathbb{R}^d$$

**Cellular Morphology Encoder ($E_4$):** For Cell Painting images $x_4 \in \mathbb{R}^{C \times H \times W}$ with $C$ channels, we employ a vision transformer:
$$z_4 = E_4(x_4) = \text{ViT}(x_4) \in \mathbb{R}^d$$

### 2.3 Cross-Scale Contrastive Objectives

The core innovation lies in our hierarchical contrastive learning objectives that align representations between adjacent biological scales.

**Adjacent-Scale Alignment:** For adjacent scales $s$ and $s+1$, we leverage known biological mappings to define positive pairs. Let $\mathcal{M}_{s \rightarrow s+1}$ denote the mapping from scale $s$ to scale $s+1$ (e.g., gene-to-protein, genotype-to-transcriptome). For a batch of $N$ samples with known correspondences, the cross-scale contrastive loss is:

$$\mathcal{L}_{s \rightarrow s+1} = -\frac{1}{N}\sum_{i=1}^{N} \log \frac{\exp(\text{sim}(z_s^i, z_{s+1}^{m(i)})/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(z_s^i, z_{s+1}^j)/\tau)}$$

where $m(i)$ denotes the mapped index for sample $i$, $\text{sim}(\cdot, \cdot)$ is cosine similarity, and $\tau$ is a temperature hyperparameter.

**Hard Negative Mining:** To ensure discriminative representations, we implement biologically-informed hard negative sampling. For a positive pair $(z_s^i, z_{s+1}^{m(i)})$, hard negatives are entities that are structurally or sequentially similar but functionally distinct. We define the hard negative set:
$$\mathcal{N}_{hard}^i = \{j : \text{sim}(z_s^i, z_s^j) > \theta_{sim} \land \text{func}(i) \neq \text{func}(j)\}$$
where $\theta_{sim}$ is a similarity threshold and $\text{func}(\cdot)$ returns functional annotation.

**Hierarchical Weighting:** Following insights from hierarchy-preserving contrastive learning (Khan, 2025), we incorporate scale-distance weighting that reflects the biological relationship strength:
$$\mathcal{L}_{total} = \sum_{s=1}^{S-1} \lambda_s \mathcal{L}_{s \rightarrow s+1} + \gamma \sum_{s=1}^{S} \mathcal{L}_{within}^s$$

where $\lambda_s$ weights the importance of each cross-scale alignment, and $\mathcal{L}_{within}^s$ is a within-scale contrastive loss (similar to SimCLR) that maintains modality-specific structure.

### 2.4 Scale-Conditioned Prediction Heads

To enable bidirectional inference across scales, we introduce scale-conditioned prediction heads:

**Upward Prediction (Molecule → Cell → Tissue):**
$$\hat{z}_{s+1} = f_{up}^s(z_s, c_s) = \text{MLP}([z_s; \text{Embed}(c_s)])$$
where $c_s$ is a scale conditioning variable and $[\cdot; \cdot]$ denotes concatenation.

**Downward Prediction (Phenotype → Mechanism):**
$$\hat{z}_{s-1} = f_{down}^s(z_s, c_s) = \text{MLP}([z_s; \text{Embed}(c_s)])$$

The prediction heads are trained with reconstruction losses:
$$\mathcal{L}_{pred} = \sum_{s=1}^{S-1} \|z_{s+1} - \hat{z}_{s+1}\|_2^2 + \|z_s - \hat{z}_s\|_2^2$$

### 2.5 Training Procedure

The complete training objective combines all components:
$$\mathcal{L} = \mathcal{L}_{total} + \alpha \mathcal{L}_{pred} + \beta \mathcal{L}_{reg}$$

where $\mathcal{L}_{reg}$ includes regularization terms (weight decay, embedding normalization) and $\alpha$, $\beta$ are hyperparameters.

Training proceeds in three phases:
1. **Phase 1 (Within-Scale Pre-training):** Train each encoder independently with within-scale contrastive objectives.
2. **Phase 2 (Cross-Scale Alignment):** Freeze lower-scale encoders progressively and train cross-scale alignment objectives.
3. **Phase 3 (End-to-End Fine-tuning):** Jointly fine-tune all components with the complete objective.

### 2.6 Experimental Design

**Datasets:**
- **JUMP-CP:** Contains Cell Painting images and associated genetic/chemical perturbation metadata (~140,000 perturbations).
- **Human Cell Atlas:** Single-cell transcriptomics data with tissue and cell type annotations.
- **AlphaFold Database:** Predicted protein structures for mapping gene-to-structure relationships.
- **GTEx:** Gene expression data across tissues with genetic variant information.

**Biological Mappings:**
- Gene → Protein: Gene ID to protein structure via UniProt mapping
- Genotype → Transcriptome: GTEx eQTL data linking genetic variants to expression
- Transcriptome → Morphology: JUMP-CP genetic perturbation data with matched expression and imaging

**Evaluation Tasks:**

1. **Cross-Scale Perturbation Prediction:** Given a genetic perturbation, predict the cellular morphology phenotype. Metrics: Mean Average Precision (mAP), Recall@k.

2. **Mechanism Retrieval:** Given a cellular phenotype, retrieve the most likely causal genetic variants. Metrics: Hit Rate@k, Mean Reciprocal Rank (MRR).

3. **Zero-Shot Transfer:** Evaluate generalization to unseen gene families or cell types. Metrics: Accuracy, AUROC on held-out categories.

4. **Representation Quality:** Assess biological meaningfulness via:
   - Clustering alignment with known functional categories (Adjusted Rand Index)
   - Linear probing for functional annotation tasks
   - Nearest-neighbor consistency across scales

**Baselines:**
- Single-scale foundation models (ESM-2, scGPT, MAE for Cell Painting)
- Concatenation-based multimodal fusion
- CLIP-style dual-encoder alignment without hierarchy
- HIPPO-style hierarchical contrastive learning adapted to our setting

**Ablation Studies:**
- Effect of hard negative sampling strategy
- Contribution of each cross-scale alignment term
- Impact of hierarchical weighting vs. uniform weighting
- Comparison of Euclidean vs. hyperbolic embedding spaces

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Cross-Scale Prediction:** We anticipate that HCL-Bio will outperform single-scale models and naive multimodal fusion approaches by 15-25% on perturbation effect prediction tasks, as measured by mAP on JUMP-CP held-out perturbations.

2. **Emergent Cross-Scale Retrieval:** The learned representations should enable novel capabilities such as retrieving molecular mechanisms from phenotypic descriptions, with expected Hit Rate@10 improvements of 20-30% over baseline approaches.

3. **Interpretable Scale Bridges:** Analysis of the cross-scale alignment space should reveal interpretable clusters corresponding to biological pathways and functional categories, providing mechanistic insights into how molecular perturbations manifest as cellular phenotypes.

4. **Zero-Shot Generalization:** We expect the hierarchical structure to enable better generalization to unseen gene families and cell types, with performance degradation limited to 10-15% compared to seen categories (vs. 30-40% for single-scale models).

### Scientific Impact

This research contributes to the LMRL community's goal of developing foundation models that capture the full complexity of biological systems. By explicitly modeling cross-scale dependencies, HCL-Bio addresses a fundamental limitation of current approaches and provides a framework that can be extended to additional biological scales (tissue, organ, organism). The cross-scale contrastive objectives and hierarchical alignment strategies developed here are generalizable to other domains with inherent hierarchical structure.

### Practical Applications

The framework has immediate applications in:
- **Drug Discovery:** Predicting how molecular perturbations will affect cellular phenotypes, reducing experimental screening costs.
- **Disease Mechanism Discovery:** Tracing phenotypic observations back to potential molecular causes.
- **Virtual Cell Simulation:** Providing learned representations that capture cross-scale dynamics, a critical component for AI-powered virtual cell simulators.

### Open-Source Contributions

We will release: (1) pre-trained scale-specific encoders and cross-scale alignment modules, (2) curated biological mapping datasets linking different scales, (3) evaluation benchmarks for cross-scale prediction tasks, and (4) tutorials for extending the framework to new biological scales. These contributions directly address the LMRL workshop's objective of creating open-source standardization for biological representation learning.