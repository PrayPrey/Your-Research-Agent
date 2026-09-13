# Research Proposal: HierarchicalGenomeFM: Bidirectional Cross-Scale Attention for Multi-Omics Foundation Models

## 1. Introduction

### 1.1 Background

The integration of machine learning with genomics has emerged as a transformative approach to understanding disease mechanisms and accelerating drug discovery. Despite significant advances in sequencing technologies and the accumulation of vast multi-omics datasets, our understanding of how genetic information flows across biological scales—from DNA regulatory elements to gene expression patterns to spatial tissue organization—remains fragmented. This knowledge gap represents a critical bottleneck in identifying therapeutic targets and developing effective treatments.

Current genomic foundation models have achieved remarkable success within individual biological scales. DNA sequence models such as HyenaDNA and Enformer excel at predicting regulatory elements and chromatin accessibility from nucleotide sequences. Single-cell RNA sequencing models like scGPT and Geneformer capture gene expression dynamics across diverse cell types. Spatial transcriptomics models leverage vision transformer architectures to understand tissue organization. However, these models operate in isolation, missing the fundamental biological reality that information flows bidirectionally across scales: DNA regulatory elements control gene expression, which determines cellular identity and spatial organization, while tissue-level signals feed back to modulate gene expression programs.

Existing approaches to multi-modal genomics typically employ late fusion strategies—training separate models on each modality and combining their outputs through concatenation or simple attention mechanisms. This paradigm fails to capture the intricate cross-scale dependencies that govern biological systems. Recent evidence from the HESCAPE benchmark demonstrates that while contrastive pretraining improves certain downstream tasks, it can degrade direct prediction performance, suggesting that naive multi-modal combination strategies are insufficient.

### 1.2 Research Objectives

This research proposes HierarchicalGenomeFM, a novel three-level hierarchical foundation model with sparse bidirectional cross-scale attention designed to capture the full complexity of genomic information flow. Our primary objectives are:

1. **Develop a unified hierarchical architecture** that processes DNA sequences, gene expression, and spatial transcriptomics within a single coherent framework, enabling both bottom-up feature extraction and top-down contextual modulation.

2. **Design efficient sparse cross-scale attention mechanisms** that capture critical inter-scale dependencies while maintaining computational tractability for large-scale genomic datasets.

3. **Validate the biological relevance** of learned cross-scale representations through comprehensive ablation studies and downstream task evaluation on disease mechanism discovery and therapeutic target identification.

### 1.3 Significance

This research addresses fundamental limitations in current genomic AI systems by introducing a biologically-motivated hierarchical architecture inspired by visual cortex processing. The bidirectional information flow mechanism mirrors how biological systems actually operate—where higher-level tissue organization influences gene expression programs through feedback signaling. Success in this endeavor would provide:

- **Unified genomic representations** enabling more accurate prediction of disease mechanisms across biological scales
- **Improved therapeutic target identification** by capturing how genetic variants propagate effects through expression to tissue phenotypes
- **A new paradigm for multi-omics integration** that respects the hierarchical nature of biological information processing

## 2. Methodology

### 2.1 Model Architecture

HierarchicalGenomeFM comprises three specialized levels connected through sparse bidirectional cross-scale attention:

**Level 1 (DNA Sequence Processing):** We employ a Mamba-based state space model to process DNA sequences at 100kb-1Mb resolution. The Mamba architecture provides linear-time complexity for long sequences while capturing long-range regulatory dependencies. For an input DNA sequence $\mathbf{x}^{(1)} \in \{A, C, G, T\}^L$ where $L \in [100\text{kb}, 1\text{Mb}]$, Level 1 produces representations:

$$\mathbf{H}^{(1)} = \text{Mamba}(\text{Embed}(\mathbf{x}^{(1)})) \in \mathbb{R}^{N_1 \times d_1}$$

where $N_1$ is the number of sequence tokens and $d_1 = 256$ is the hidden dimension.

**Level 2 (Gene Expression Processing):** A standard Transformer encoder processes gene-level expression vectors. For input expression profile $\mathbf{x}^{(2)} \in \mathbb{R}^{G}$ across $G$ genes:

$$\mathbf{H}^{(2)} = \text{Transformer}(\mathbf{x}^{(2)} \mathbf{W}_{\text{embed}} + \mathbf{E}_{\text{gene}}) \in \mathbb{R}^{G \times d_2}$$

where $\mathbf{W}_{\text{embed}} \in \mathbb{R}^{1 \times d_2}$ projects expression values and $\mathbf{E}_{\text{gene}} \in \mathbb{R}^{G \times d_2}$ provides learnable gene embeddings with $d_2 = 384$.

**Level 3 (Spatial Transcriptomics Processing):** A Vision Transformer (ViT) processes spatial gene expression maps. For spatial input $\mathbf{x}^{(3)} \in \mathbb{R}^{H \times W \times G}$:

$$\mathbf{H}^{(3)} = \text{ViT}(\text{PatchEmbed}(\mathbf{x}^{(3)})) \in \mathbb{R}^{N_3 \times d_3}$$

where $N_3 = (H/p)(W/p)$ for patch size $p$ and $d_3 = 512$.

### 2.2 Sparse Bidirectional Cross-Scale Attention

The key innovation is our sparse top-k cross-scale attention mechanism enabling bidirectional information flow. For adjacent levels $\ell$ and $\ell+1$, we define:

**Bottom-Up Attention (Level $\ell \rightarrow \ell+1$):**

$$\mathbf{A}^{\uparrow}_{\ell \rightarrow \ell+1} = \text{TopK}\left(\frac{\mathbf{Q}^{(\ell+1)} (\mathbf{K}^{(\ell)})^\top}{\sqrt{d_k}}, k\right)$$

$$\mathbf{Z}^{\uparrow}_{\ell+1} = \text{Softmax}(\mathbf{A}^{\uparrow}_{\ell \rightarrow \ell+1}) \mathbf{V}^{(\ell)}$$

**Top-Down Attention (Level $\ell+1 \rightarrow \ell$):**

$$\mathbf{A}^{\downarrow}_{\ell+1 \rightarrow \ell} = \text{TopK}\left(\frac{\mathbf{Q}^{(\ell)} (\mathbf{K}^{(\ell+1)})^\top}{\sqrt{d_k}}, k\right)$$

$$\mathbf{Z}^{\downarrow}_{\ell} = \text{Softmax}(\mathbf{A}^{\downarrow}_{\ell+1 \rightarrow \ell}) \mathbf{V}^{(\ell+1)}$$

where $\text{TopK}(\cdot, k)$ retains only the top-$k$ attention scores per query, setting others to $-\infty$. The queries, keys, and values are computed as:

$$\mathbf{Q}^{(\ell)} = \mathbf{H}^{(\ell)} \mathbf{W}_Q^{(\ell)}, \quad \mathbf{K}^{(\ell)} = \mathbf{H}^{(\ell)} \mathbf{W}_K^{(\ell)}, \quad \mathbf{V}^{(\ell)} = \mathbf{H}^{(\ell)} \mathbf{W}_V^{(\ell)}$$

The updated representations incorporate bidirectional information:

$$\tilde{\mathbf{H}}^{(\ell)} = \mathbf{H}^{(\ell)} + \alpha_{\uparrow} \mathbf{Z}^{\uparrow}_{\ell} + \alpha_{\downarrow} \mathbf{Z}^{\downarrow}_{\ell}$$

where $\alpha_{\uparrow}, \alpha_{\downarrow}$ are learnable scaling parameters initialized to 0.1.

### 2.3 Training Objectives

We employ a multi-task training objective combining cross-scale prediction and hierarchical contrastive learning:

**Cross-Scale Prediction Loss:**

$$\mathcal{L}_{\text{pred}} = \lambda_1 \mathcal{L}_{\text{seq} \rightarrow \text{expr}} + \lambda_2 \mathcal{L}_{\text{expr} \rightarrow \text{spatial}}$$

For sequence-to-expression prediction:

$$\mathcal{L}_{\text{seq} \rightarrow \text{expr}} = \frac{1}{G} \sum_{g=1}^{G} \text{MSE}(\hat{y}_g^{\text{expr}}, y_g^{\text{expr}})$$

where $\hat{y}_g^{\text{expr}} = \text{MLP}(\text{Pool}(\tilde{\mathbf{H}}^{(1)}))_g$.

**Hierarchical Contrastive Loss:**

$$\mathcal{L}_{\text{contrast}} = -\sum_{\ell=1}^{2} \log \frac{\exp(\text{sim}(\mathbf{z}^{(\ell)}_i, \mathbf{z}^{(\ell+1)}_i) / \tau)}{\sum_{j=1}^{B} \exp(\text{sim}(\mathbf{z}^{(\ell)}_i, \mathbf{z}^{(\ell+1)}_j) / \tau)}$$

where $\mathbf{z}^{(\ell)} = \text{Proj}(\text{Pool}(\tilde{\mathbf{H}}^{(\ell)}))$ are projected pooled representations, $\tau = 0.07$ is the temperature, and $B$ is the batch size.

**Total Loss:**

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pred}} + \lambda_c \mathcal{L}_{\text{contrast}}$$

with $\lambda_1 = 1.0$, $\lambda_2 = 1.0$, and $\lambda_c = 0.5$.

### 2.4 Data Collection and Preprocessing

**Primary Data Source:** Human Cell Atlas (HCA) matched multi-scale datasets, targeting >10,000 samples with paired DNA accessibility, gene expression, and spatial transcriptomics measurements.

**Supplementary Sources:** 10x Genomics Visium spatial transcriptomics datasets, ENCODE regulatory element annotations, GTEx expression data for cross-tissue validation.

**Preprocessing Pipeline:**
1. DNA sequences: Extract 500kb windows centered on gene transcription start sites; one-hot encode nucleotides
2. Gene expression: Log-normalize counts, select top 5,000 highly variable genes, z-score standardize
3. Spatial data: Segment into 256×256 patches, normalize per-spot expression, apply batch correction using Harmony

**Data Splits:** 70% training, 15% validation, 15% test, stratified by tissue type and disease status.

### 2.5 Experimental Design

**Baseline Models:**
1. **Ensemble Baseline:** Separately trained HyenaDNA (Level 1) + scGPT (Level 2) + spatial ViT (Level 3) with late fusion via concatenation
2. **Adapter Baseline:** Frozen single-scale models with trainable adapter layers for cross-modal alignment
3. **Simple Fusion:** Single-scale models with standard (non-sparse, unidirectional) cross-attention

**Ablation Studies:**
- Full model vs. bottom-up only (remove top-down attention)
- Full model vs. dense attention (remove sparsity)
- Full model vs. single-task (remove contrastive loss)
- Sparsity parameter sweep: $k \in \{100, 250, 500, 1000\}$

**Evaluation Metrics:**
- **Primary:** Spearman correlation ($\rho$) for cross-scale predictions
- **Secondary:** Downstream classification accuracy (cell type, disease state), AUROC for regulatory element prediction
- **Efficiency:** Training time (GPU-hours), peak memory (GB), inference latency (ms)

**Statistical Analysis:**
- 5-fold cross-validation × 5 random seeds = 25 runs per configuration
- Paired t-tests with Bonferroni correction ($\alpha = 0.05$)
- Report mean, 95% confidence intervals, Cohen's d effect size
- ANOVA with Tukey HSD for ablation comparisons

### 2.6 Implementation Details

**Model Configuration:** ~100M total parameters distributed as Level 1 (30M), Level 2 (35M), Level 3 (35M)

**Training:** AdamW optimizer, learning rate $3 \times 10^{-4}$ with cosine decay, batch size 32, gradient accumulation over 4 steps, mixed-precision (FP16), 100 epochs

**Hardware:** 4× NVIDIA A100 80GB GPUs, estimated 100-150 GPU-hours for full training

**Software:** PyTorch 2.0, HuggingFace Transformers, custom Mamba implementation

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Cross-Scale Prediction Performance:** We hypothesize that HierarchicalGenomeFM will achieve Spearman correlation improvements of 15-25% over ensemble baselines for cross-scale prediction tasks. Specifically:
- Sequence → Expression prediction: Expected $\rho = 0.65-0.75$ vs. baseline $\rho = 0.50-0.60$
- Expression → Spatial prediction: Expected $\rho = 0.60-0.70$ vs. baseline $\rho = 0.45-0.55$

**Mechanism Validation:** Ablation studies will demonstrate that bidirectional cross-scale attention contributes 5-15% of performance gains, with top-down attention providing unique contextual information not captured by bottom-up processing alone.

**Computational Efficiency:** Sparse attention ($k=500$) will maintain ≥95% of dense attention performance while reducing training time by 40-60% and memory requirements by 30-50%.

### 3.2 Scientific Impact

This research will establish a new paradigm for multi-omics foundation models that respects the hierarchical nature of biological information processing. The bidirectional cross-scale attention mechanism provides a principled approach to integrating diverse genomic modalities, moving beyond naive fusion strategies that ignore biological structure.

The learned representations will enable:
- **Improved disease mechanism discovery** by tracing how genetic variants propagate effects across scales
- **Enhanced therapeutic target identification** through unified representations capturing regulatory, expression, and spatial contexts
- **Better understanding of gene-environment interactions** via top-down contextual modulation

### 3.3 Translational Impact

For drug discovery applications, HierarchicalGenomeFM will provide:
- More accurate prediction of drug target effects across biological scales
- Improved identification of biomarkers spanning multiple omics modalities
- Enhanced understanding of cell and gene therapy mechanisms through spatial context

### 3.4 Broader Impact

This work contributes to the broader goal of bridging machine learning and genomics for therapeutic development. By demonstrating that biologically-motivated architectural choices (hierarchical processing, bidirectional information flow) improve model performance, we provide a template for future foundation model development in biology. The open-source release of model weights, code, and benchmark datasets will accelerate community progress in this critical area.

### 3.5 Limitations and Future Directions

We acknowledge limitations including: restriction to human genomics initially, potential batch effects in cross-dataset training, and computational requirements limiting accessibility. Future work will extend to cross-species transfer learning, incorporate protein structure information, and develop efficient inference strategies for clinical deployment.