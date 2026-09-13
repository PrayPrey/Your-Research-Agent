# Research Proposal: EcoNiche-Former: Hierarchical Multi-Scale Spatial Encoding for Single-Cell Foundation Models

## 1. Introduction

### 1.1 Background

The advent of spatial transcriptomics technologies has revolutionized our understanding of tissue biology by enabling the measurement of gene expression while preserving spatial context. Technologies such as 10x Visium, Stereo-seq, MERFISH, and Xenium now allow researchers to map transcriptomic profiles to precise cellular locations within tissues, revealing how cells organize into functional units and interact within their microenvironments. This spatial dimension is critical for understanding disease mechanisms, particularly in complex conditions like cancer where the tumor microenvironment plays a decisive role in disease progression and treatment response.

Recent advances in foundation models for single-cell genomics have demonstrated remarkable success in learning generalizable representations from large-scale datasets. Models such as scGPT, Geneformer, and most recently Nicheformer have shown that pre-training on millions of cells enables superior performance on downstream tasks including cell type annotation, perturbation prediction, and gene expression imputation. Nicheformer, in particular, represents a significant advancement by incorporating spatial transcriptomics data into pre-training, utilizing a dataset of 110 million cells (57 million dissociated and 53 million spatial) to learn representations that capture both intrinsic cellular states and spatial context.

However, current approaches to modeling spatial context in single-cell foundation models treat spatial relationships with unified representations that may not fully capture the hierarchical organization inherent in tissue microenvironments. Biological tissues exhibit multi-scale spatial organization: cells interact with immediate neighbors through direct contact and paracrine signaling, organize into functional niches with shared microenvironmental features, and participate in broader tissue-level structures that define organ function. This hierarchical organization mirrors ecological systems where species-environment relationships operate across distinct landscape scales—a parallel that motivates our proposed approach.

### 1.2 Research Objectives

The primary objective of this research is to develop and validate EcoNiche-Former, a hierarchical multi-scale spatial encoding framework that augments single-cell foundation models with explicit multi-scale spatial representations. Specifically, we aim to:

1. **Design a hierarchical spatial encoding mechanism** that captures cellular context at three distinct spatial resolutions (cell-cell, niche, and region levels) through learned scale parameters and distance-weighted attention.

2. **Validate the hypothesis** that explicit multi-scale spatial encoding improves spatial transcriptomics analysis compared to flat single-scale approaches, achieving >5% reduction in spatial composition prediction MAE and >2% improvement in spatial label prediction accuracy.

3. **Demonstrate interpretable scale-specific attention patterns** that reveal biologically meaningful spatial organization across different cell types and tissue contexts.

4. **Enable improved drug discovery applications** by providing richer microenvironment representations for tumor microenvironment analysis and developmental biology studies.

### 1.3 Significance

This research addresses a fundamental gap in current single-cell foundation models: the lack of explicit hierarchical spatial modeling. By introducing multi-scale spatial encoding inspired by ecological niche theory, we expect to:

- **Advance methodological understanding** of how spatial context should be incorporated into foundation models for genomics
- **Improve practical performance** on critical spatial transcriptomics tasks relevant to drug target identification
- **Provide interpretable insights** into tissue organization through scale-specific attention analysis
- **Enable better transfer learning** between spatial and dissociated single-cell data

The proposed work directly addresses the workshop's focus on foundation models for genomics, modeling long-range dependencies in spatial omics, and interpretability—contributing both methodological innovation and practical tools for drug discovery applications.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{D} = \{(x_i, s_i, y_i)\}_{i=1}^{N}$ denote a spatial transcriptomics dataset where $x_i \in \mathbb{R}^{G}$ represents the gene expression vector for cell $i$ across $G$ genes, $s_i \in \mathbb{R}^{2}$ represents the spatial coordinates, and $y_i$ represents associated labels (cell type, niche identity, etc.). Our goal is to learn a representation function $f_\theta: (x_i, \mathcal{N}_i) \rightarrow z_i$ that maps each cell's expression and spatial neighborhood $\mathcal{N}_i$ to an embedding $z_i$ that captures multi-scale spatial context.

### 2.2 Hierarchical Multi-Scale Spatial Encoding

#### 2.2.1 Scale-Specific Distance Kernels

We define three spatial scales with learnable scale parameters $\sigma_1 < \sigma_2 < \sigma_3$ corresponding to cell-cell ($\sim$10-50μm), niche ($\sim$50-200μm), and region ($\sim$200-1000μm) contexts. For each scale $k \in \{1, 2, 3\}$, we compute distance-weighted attention using a Gaussian kernel:

$$w_{ij}^{(k)} = \exp\left(-\frac{\|s_i - s_j\|^2}{2\sigma_k^2}\right)$$

where $\|s_i - s_j\|$ is the Euclidean distance between cells $i$ and $j$. The scale parameters $\sigma_k$ are initialized based on biological priors but learned during training to adapt to dataset-specific spatial organization.

#### 2.2.2 Multi-Scale Attention Mechanism

For each cell $i$, we compute scale-specific context representations through distance-weighted attention:

$$c_i^{(k)} = \sum_{j \in \mathcal{N}_i} \alpha_{ij}^{(k)} \cdot h_j$$

where $h_j$ is the hidden representation of cell $j$ from the transformer backbone, and the attention weights are:

$$\alpha_{ij}^{(k)} = \frac{w_{ij}^{(k)} \cdot \exp(q_i^{(k)T} k_j^{(k)} / \sqrt{d})}{\sum_{l \in \mathcal{N}_i} w_{il}^{(k)} \cdot \exp(q_i^{(k)T} k_l^{(k)} / \sqrt{d})}$$

Here, $q_i^{(k)} = W_Q^{(k)} h_i$ and $k_j^{(k)} = W_K^{(k)} h_j$ are scale-specific query and key projections, and $d$ is the embedding dimension.

#### 2.2.3 Hierarchical Aggregation

The multi-scale context representations are aggregated through a learned gating mechanism:

$$z_i^{spatial} = \sum_{k=1}^{3} g_i^{(k)} \cdot c_i^{(k)}$$

where the gate values are computed as:

$$g_i = \text{softmax}(W_g [c_i^{(1)}; c_i^{(2)}; c_i^{(3)}; h_i])$$

This allows the model to dynamically weight different spatial scales based on cell type and local context.

#### 2.2.4 Integration with Transformer Backbone

The final cell representation combines intrinsic transcriptomic features with hierarchical spatial context:

$$z_i = \text{LayerNorm}(h_i + W_o z_i^{spatial})$$

This representation is used for all downstream tasks, maintaining compatibility with the Nicheformer architecture while adding explicit multi-scale spatial encoding.

### 2.3 Training Procedure

#### 2.3.1 Pre-training Objectives

Following Nicheformer, we employ masked gene expression prediction as the primary pre-training objective:

$$\mathcal{L}_{MLM} = -\sum_{i} \sum_{g \in \mathcal{M}_i} \log p(x_{ig} | x_{i,\backslash\mathcal{M}_i}, z_i)$$

where $\mathcal{M}_i$ is the set of masked genes for cell $i$.

We add a spatial consistency loss to encourage coherent multi-scale representations:

$$\mathcal{L}_{spatial} = \sum_{k=1}^{3} \sum_{i} \sum_{j \in \mathcal{N}_i^{(k)}} w_{ij}^{(k)} \cdot \|z_i - z_j\|^2$$

The total loss is:

$$\mathcal{L} = \mathcal{L}_{MLM} + \lambda \mathcal{L}_{spatial}$$

with $\lambda = 0.1$ determined through validation.

#### 2.3.2 Scale Parameter Regularization

To prevent scale collapse (where $\sigma_1 \approx \sigma_2 \approx \sigma_3$), we add a separation regularizer:

$$\mathcal{L}_{sep} = -\sum_{k=1}^{2} \log(\sigma_{k+1} - \sigma_k + \epsilon)$$

with $\epsilon = 1\mu m$ for numerical stability.

### 2.4 Experimental Design

#### 2.4.1 Dataset

We utilize the Nicheformer 110M cell dataset comprising:
- **Dissociated scRNA-seq:** 57 million cells from diverse tissues and conditions
- **Spatial transcriptomics:** 53 million cells from 10x Visium, Stereo-seq, and other platforms

For evaluation, we use held-out spatial transcriptomics datasets including:
- Human breast cancer (10x Visium, n=12 samples)
- Mouse brain (MERFISH, n=8 samples)
- Human developmental tissues (Stereo-seq, n=6 samples)

#### 2.4.2 Experimental Conditions

| Condition | Description | Purpose |
|-----------|-------------|---------|
| Baseline-1 | Nicheformer (no explicit spatial encoding) | SOTA comparison |
| Baseline-2 | Single-scale spatial encoding ($\sigma$ fixed) | Ablation |
| EcoNiche-2 | Two-scale hierarchical encoding | Ablation |
| EcoNiche-3 | Three-scale hierarchical encoding (full model) | Primary evaluation |
| EcoNiche-3-fixed | Three-scale with fixed $\sigma$ values | Learned vs. fixed comparison |

#### 2.4.3 Evaluation Tasks and Metrics

**Task 1: Spatial Composition Prediction**
- Predict cell type proportions for each spatial spot
- Metric: Mean Absolute Error (MAE)
- Expected baseline: ~0.12 MAE
- Target: <0.114 MAE (>5% reduction)

**Task 2: Spatial Label Prediction**
- Classify cells into niche/region categories
- Metric: Accuracy
- Expected baseline: ~80%
- Target: >82% accuracy (>2% improvement)

**Task 3: Scale Interpretability Analysis**
- Analyze learned $\sigma$ parameters and attention patterns
- Metric: ANOVA F-statistic for cell type-specific scale preferences
- Target: p < 0.01 for scale differentiation across cell types

**Task 4: Cross-Dataset Transfer**
- Predict spatial context for dissociated scRNA-seq cells
- Metric: Pearson correlation with ground truth (matched spatial-dissociated pairs)
- Target: r > 0.5

#### 2.4.4 Statistical Analysis

All experiments are conducted with n=25 independent runs using different random seeds. We report:
- Mean ± standard deviation
- 95% confidence intervals
- Cohen's d effect size
- Paired t-test p-values (one-tailed, α=0.05)

**Falsification Criteria:**
1. Spatial label prediction accuracy ≤ 78%
2. Scale parameters collapse: $|\sigma_2 - \sigma_1| < 10\mu m$ AND $|\sigma_3 - \sigma_2| < 10\mu m$
3. Transfer correlation r < 0.3

### 2.5 Implementation Details

- **Architecture:** Transformer backbone with 12 layers, 768 hidden dimensions, 12 attention heads
- **Training:** AdamW optimizer, learning rate 1e-4 with cosine decay, batch size 256
- **Compute:** 8× NVIDIA A100 GPUs, estimated training time ~7 days
- **Neighborhood size:** $|\mathcal{N}_i| = 100$ nearest neighbors
- **Initial scale parameters:** $\sigma_1 = 25\mu m$, $\sigma_2 = 100\mu m$, $\sigma_3 = 400\mu m$

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcomes:**
1. **Performance Improvement:** We expect EcoNiche-Former to achieve spatial label prediction accuracy of 82-85% (compared to Nicheformer baseline of ~80%) and spatial composition prediction MAE reduction of 5-8%.

2. **Scale Separation:** Learned scale parameters are expected to converge to biologically meaningful values: $\sigma_1 \approx 20-40\mu m$ (direct cell-cell contact), $\sigma_2 \approx 80-150\mu m$ (local niche), $\sigma_3 \approx 300-600\mu m$ (tissue region).

3. **Interpretable Attention Patterns:** Different cell types should exhibit distinct scale preferences—e.g., immune cells may show stronger attention at niche scales due to their migratory behavior, while epithelial cells may emphasize cell-cell scale due to tight junction organization.

4. **Transfer Learning:** Successful bidirectional transfer between spatial and dissociated data, enabling spatial context inference for the vast majority of existing scRNA-seq datasets.

### 3.2 Scientific Impact

This research will advance the field in several ways:

1. **Methodological Contribution:** Establishing hierarchical multi-scale spatial encoding as a principled approach for incorporating spatial context into foundation models, with potential applications beyond single-cell genomics to other spatial data modalities.

2. **Biological Insights:** The interpretable scale-specific attention patterns will provide new insights into tissue organization principles, potentially revealing previously unrecognized spatial relationships in disease contexts.

3. **Benchmark Establishment:** Our comprehensive evaluation framework will serve as a benchmark for future spatial foundation model development.

### 3.3 Translational Impact

For drug discovery applications, EcoNiche-Former will enable:

1. **Tumor Microenvironment Analysis:** Better characterization of immune cell infiltration patterns and tumor-stroma interactions at multiple spatial scales, informing immunotherapy target selection.

2. **Developmental Biology:** Improved understanding of cell fate decisions in spatial context, relevant for cell therapy development.

3. **Biomarker Discovery:** Identification of spatially-defined cell states that may serve as diagnostic or prognostic biomarkers.

### 3.4 Limitations and Future Directions

We acknowledge several limitations:
- Current implementation is restricted to 2D spatial context
- Computational cost is approximately 2× baseline
- Temporal dynamics are not captured

Future work will address these through 3D spatial encoding, efficient attention mechanisms, and integration with time-series spatial data.

### 3.5 Conclusion

EcoNiche-Former represents a principled approach to incorporating hierarchical spatial context into single-cell foundation models. By drawing inspiration from ecological niche theory and implementing learnable multi-scale spatial encoding, we expect to achieve meaningful improvements in spatial transcriptomics analysis while providing interpretable insights into tissue organization. This work will contribute both methodological advances and practical tools for accelerating drug discovery through improved understanding of cellular microenvironments.