# Research Proposal: Disagreement-Driven Data Refinement (D3R): Leveraging Ensemble Model Disagreement as Quality Signals for Large-Scale Dataset Curation

## 1. Introduction

### Background

The emergence of large-scale foundation models has fundamentally transformed machine learning across vision, language, and multimodal domains. Models such as GPT-4, CLIP, and LLaMA have demonstrated remarkable capabilities by leveraging massive datasets containing billions of samples. However, as the research community has increasingly recognized, the quality of training data is as critical—if not more so—than model architecture in determining final model performance. This paradigm shift toward data-centric machine learning has exposed a fundamental challenge: how can we efficiently assess and curate datasets at scales where human annotation is economically and logistically infeasible?

Current approaches to large-scale data curation face significant limitations. Human annotation, while accurate, cannot scale to datasets containing hundreds of millions or billions of samples. Simple heuristics such as perplexity filtering or image resolution thresholds provide coarse-grained quality signals but miss nuanced issues including subtle label noise, semantic ambiguity, and context-dependent quality problems. Recent work like EcoDatum (Xu et al., 2025) has demonstrated the promise of learning-driven ensemble approaches for multimodal data curation, yet systematic methods for extracting interpretable quality signals from model behavior remain underexplored.

A particularly promising but underutilized signal for data quality assessment is model disagreement—the phenomenon where multiple models trained on overlapping data produce conflicting predictions for specific samples. When architecturally diverse models consistently disagree on a sample, this disagreement often indicates intrinsic properties of the data (ambiguity, label noise, out-of-distribution characteristics) rather than model-specific artifacts. This insight forms the foundation of our proposed research.

### Research Objectives

This research proposes **Disagreement-Driven Data Refinement (D3R)**, a comprehensive framework that transforms ensemble model disagreement patterns into actionable quality signals for large-scale dataset curation. Our specific objectives are:

1. To develop a theoretically grounded and computationally efficient method for computing disagreement-based quality scores across diverse model architectures
2. To create an interpretable taxonomy that maps disagreement patterns to specific data quality issues (label noise, ambiguity, out-of-distribution samples, near-duplicates)
3. To validate the framework on large-scale benchmarks including DataComp and LAION subsets, demonstrating improved downstream model performance through disagreement-guided filtering
4. To establish scaling laws that characterize the relationship between ensemble diversity, dataset size, and quality signal reliability

### Significance

This research addresses multiple critical challenges identified in the data-centric machine learning community. First, it provides a scalable alternative to expensive human annotation by leveraging computational resources that are already being expended during model development. Second, it bridges the gap between model-assisted dataset construction and quality assessment, creating a unified framework where model training and data curation become synergistic processes. Third, by categorizing quality issues into interpretable categories, D3R enables targeted interventions rather than blanket filtering, potentially preserving valuable edge cases while removing genuinely problematic samples. The expected impact includes a 10x reduction in curation costs while improving data utility for foundation model training.

## 2. Methodology

### 2.1 Framework Overview

The D3R framework consists of four interconnected components: (1) Diverse Ensemble Construction, (2) Disagreement Score Computation, (3) Quality Issue Categorization, and (4) Refinement Strategy Selection. We describe each component in detail below.

### 2.2 Diverse Ensemble Construction

The foundation of D3R rests on the principle that meaningful disagreement requires architectural diversity. We construct an ensemble $\mathcal{E} = \{f_1, f_2, ..., f_K\}$ of $K$ lightweight models spanning different architectural families. For vision tasks, this includes ConvNets (EfficientNet-B0), Vision Transformers (DeiT-Tiny), and hybrid architectures (ConvNeXt-Tiny). For language tasks, we employ BERT-base, DistilGPT-2, and ELECTRA-small.

Each model $f_k$ is trained on a randomly sampled subset $\mathcal{D}_k \subset \mathcal{D}$ of the target dataset, where $|\mathcal{D}_k| = \alpha \cdot |\mathcal{D}|$ with overlap ratio $\alpha \in [0.3, 0.7]$. This partial overlap ensures that disagreement signals arise from both data-intrinsic properties and sampling variation, which we subsequently disentangle.

**Training Protocol**: Each ensemble member is trained using standard supervised learning with early stopping based on validation loss. We deliberately use minimal hyperparameter tuning to ensure that disagreement reflects data properties rather than optimization artifacts. Training employs the following objective:

$$\mathcal{L}_k = \mathbb{E}_{(x,y) \sim \mathcal{D}_k} \left[ \ell(f_k(x), y) \right]$$

where $\ell$ is the task-appropriate loss function (cross-entropy for classification, contrastive loss for multimodal tasks).

### 2.3 Disagreement Score Computation

For each sample $x$ in the dataset, we compute a multi-dimensional disagreement score $\mathbf{d}(x) = [d_1(x), d_2(x), d_3(x), d_4(x)]$ capturing complementary aspects of model disagreement.

**Prediction Entropy Variance ($d_1$)**: Measures variability in uncertainty across models:

$$d_1(x) = \text{Var}_{k \in \mathcal{E}} \left[ H(f_k(x)) \right]$$

where $H(f_k(x)) = -\sum_c p_k(c|x) \log p_k(c|x)$ is the predictive entropy of model $k$.

**Confidence Calibration Misalignment ($d_2$)**: Captures disagreement in calibrated confidence:

$$d_2(x) = \max_{i,j \in \mathcal{E}} \left| \max_c p_i(c|x) - \max_c p_j(c|x) \right|$$

**Prediction Divergence ($d_3$)**: Measures pairwise prediction disagreement using Jensen-Shannon divergence:

$$d_3(x) = \frac{2}{K(K-1)} \sum_{i < j} \text{JSD}(f_i(x) \| f_j(x))$$

**Label Consistency Score ($d_4$)**: Quantifies hard prediction agreement:

$$d_4(x) = 1 - \frac{1}{K} \max_c \sum_{k=1}^{K} \mathbb{I}[\hat{y}_k(x) = c]$$

where $\hat{y}_k(x) = \arg\max_c p_k(c|x)$.

**Composite Score**: The overall disagreement score combines these metrics:

$$D(x) = \sum_{i=1}^{4} w_i \cdot \frac{d_i(x) - \mu_i}{\sigma_i}$$

where $\mu_i$ and $\sigma_i$ are the mean and standard deviation of $d_i$ across the dataset, and weights $w_i$ are learned through validation (initialized uniformly).

### 2.4 Quality Issue Categorization

A key innovation of D3R is mapping disagreement patterns to interpretable quality categories. We define a categorization function $\mathcal{C}: \mathbb{R}^4 \rightarrow \{1, 2, 3, 4, 5\}$ that assigns each sample to one of five categories:

1. **Clean** (Category 1): Low disagreement across all metrics
2. **Label Noise** (Category 2): High $d_4$ with low $d_1$ (models confidently disagree)
3. **Ambiguous** (Category 3): High $d_1$ and $d_3$ (models are uncertain and diverse)
4. **Out-of-Distribution** (Category 4): High $d_2$ with inconsistent confidence patterns
5. **Near-Duplicate Artifacts** (Category 5): Detected via embedding similarity clustering combined with disagreement

The categorization uses a learned decision tree classifier trained on a small labeled subset of quality annotations. For a sample $x$ with disagreement vector $\mathbf{d}(x)$:

$$\mathcal{C}(x) = \text{DecisionTree}(\mathbf{d}(x); \theta_{\text{tree}})$$

where $\theta_{\text{tree}}$ is learned from approximately 5,000 human-annotated samples stratified across disagreement levels.

### 2.5 Refinement Strategy Selection

Rather than simple filtering, D3R applies category-specific refinement strategies:

- **Category 1 (Clean)**: Retain with high priority
- **Category 2 (Label Noise)**: Flag for re-labeling or remove
- **Category 3 (Ambiguous)**: Retain with soft labels $\tilde{y}(x) = \frac{1}{K}\sum_k f_k(x)$
- **Category 4 (OOD)**: Quarantine for domain analysis
- **Category 5 (Near-Duplicates)**: Deduplicate, keeping highest-quality representative

### 2.6 Experimental Design

**Datasets**: We evaluate D3R on three large-scale benchmarks:
- **DataComp-Medium**: 128M image-text pairs with known quality variations
- **LAION-400M Subset**: 50M samples with synthetic noise injection at rates $\{5\%, 10\%, 20\%\}$
- **C4-Validation**: 10M text samples for language model evaluation

**Baselines**: We compare against:
- Random filtering
- Perplexity-based filtering (language) / CLIP score filtering (vision)
- Influence function-based methods
- EcoDatum (Xu et al., 2025)
- Single-model uncertainty thresholding

**Evaluation Protocol**:
1. **Intrinsic Evaluation**: Precision/recall of detecting synthetically injected noise
2. **Downstream Performance**: Train foundation models on D3R-curated data and evaluate on standard benchmarks (ImageNet, COCO, GLUE)
3. **Efficiency Analysis**: Compare computational cost (FLOPs) per quality annotation against baselines

**Metrics**:
- Area Under the Precision-Recall Curve (AUPRC) for noise detection
- Downstream accuracy improvement: $\Delta_{\text{acc}} = \text{Acc}_{\text{D3R}} - \text{Acc}_{\text{baseline}}$
- Curation efficiency: $\eta = \frac{\text{Quality improvement}}{\text{Compute cost}}$
- Inter-annotator agreement (Cohen's $\kappa$) between D3R categories and human annotations

**Ablation Studies**:
- Ensemble size ($K \in \{3, 5, 7, 9\}$)
- Architectural diversity (homogeneous vs. heterogeneous ensembles)
- Subset overlap ratio ($\alpha \in \{0.3, 0.5, 0.7\}$)
- Individual disagreement metric contributions

### 2.7 Implementation Details

All experiments use PyTorch with distributed training across 8 A100 GPUs. Ensemble models are trained for 10 epochs with batch size 256. Disagreement computation is parallelized across samples with approximate inference latency of 50ms per sample for the full ensemble.

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following concrete outcomes from this research:

1. **Validated Quality Scoring Pipeline**: A reusable, open-source toolkit for computing disagreement-based quality scores on arbitrary datasets, validated on DataComp-scale data with demonstrated reliability (expected AUPRC > 0.85 for noise detection).

2. **Improved Downstream Performance**: Foundation models trained on D3R-curated data are expected to achieve 2-5% accuracy improvements on standard benchmarks compared to uncurated baselines, with larger gains (5-10%) when the original data contains significant noise.

3. **Interpretable Quality Taxonomy**: A validated mapping between disagreement patterns and quality issues, enabling practitioners to understand *why* samples are flagged rather than receiving opaque quality scores.

4. **Scaling Laws**: Empirical characterization of how ensemble size, diversity, and dataset scale affect quality signal reliability, providing practical guidance for deployment.

5. **Efficiency Gains**: Demonstrated 10x reduction in per-sample curation cost compared to human annotation while maintaining comparable quality assessment accuracy.

### Broader Impact

This research contributes to the broader data-centric machine learning agenda in several ways. By providing scalable quality signals, D3R enables democratization of high-quality dataset curation—organizations without resources for massive human annotation campaigns can still produce well-curated training data. The interpretable categorization supports ethical considerations by making data filtering decisions transparent and auditable. Furthermore, by identifying ambiguous and out-of-distribution samples rather than simply discarding them, D3R preserves dataset diversity while improving quality, addressing the critical challenge of balancing these competing objectives.

The framework also opens new research directions, including active learning strategies guided by disagreement signals, curriculum learning based on quality categories, and federated quality assessment where disagreement is computed across institutionally distributed models without sharing raw data.

### Limitations and Future Work

We acknowledge that D3R requires training multiple models, introducing computational overhead that may be prohibitive for the largest datasets. Future work will explore distillation techniques to reduce ensemble size while preserving disagreement signal quality. Additionally, the quality taxonomy may require domain-specific adaptation; we plan to develop transfer learning approaches for the categorization model.