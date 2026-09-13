# Research Proposal: Cross-Modal Time Series Pre-training via Synthetic Narrative Generation

## 1. Title

**Learning Time Series Representations through Automated Narrative Generation and Language Model Alignment: A Self-Supervised Framework for Cross-Modal Time Series Foundation Models**

## 2. Introduction

### 2.1 Background

The emergence of foundation models has fundamentally transformed machine learning across multiple domains, particularly in natural language processing and computer vision. These models leverage massive pretraining on diverse datasets to develop generalizable representations that transfer effectively to downstream tasks. However, the time series domain faces unique challenges that have hindered the development of comparable foundation models: (1) extreme heterogeneity in data characteristics across domains, (2) limited availability of large-scale labeled datasets, (3) domain-specific semantics that are difficult to transfer, and (4) the lack of natural alignment mechanisms similar to those available in vision-language tasks.

Recent research has explored two promising directions to address these challenges. First, works like VisionTS++ have investigated leveraging pretrained models from other modalities, particularly vision models, for time series analysis through creative data transformation techniques. Second, studies such as Context-Alignment and HiTime have attempted to bridge time series data with large language models (LLMs) to exploit their rich world knowledge and reasoning capabilities. However, these approaches face a critical bottleneck: the semantic gap between numerical time series patterns and natural language representations.

The fundamental problem lies in the scarcity of paired (time series, text description) data at the scale necessary for effective cross-modal pretraining. While datasets like TS-Insights have begun addressing this gap with 100k annotated samples, manual annotation remains expensive, domain-limited, and difficult to scale. Moreover, existing approaches often treat alignment as a one-way adaptation problem—either converting time series to images or forcing LLMs to process numerical sequences—rather than creating genuine bidirectional semantic bridges.

### 2.2 Research Objectives

This research proposes a novel self-supervised framework that addresses the data scarcity and semantic alignment challenges through automated narrative generation. Our primary objectives are:

1. **Develop a scalable narrative generation system** that automatically produces multi-granular natural language descriptions of time series patterns without requiring manual annotation, enabling unlimited generation of aligned (time series, narrative) pairs.

2. **Design a dual-encoder architecture** that learns joint representations of time series and text through contrastive learning on synthetic narratives, creating a shared semantic space that bridges numerical patterns and linguistic concepts.

3. **Implement knowledge distillation mechanisms** that transfer reasoning capabilities from frozen pretrained LLMs to time series encoders through the narrative bridge, enabling time series models to leverage linguistic priors.

4. **Validate cross-domain transferability** by demonstrating that models pretrained with our framework achieve superior zero-shot and few-shot performance across diverse time series domains compared to existing approaches.

### 2.3 Significance

This research addresses several critical challenges in time series foundation model development:

**Scientific Impact**: Our work introduces a paradigm shift from requiring expensive paired annotations to generating unlimited aligned data through automated narratives. This self-supervised approach democratizes cross-modal pretraining for time series, making it accessible to domains with limited resources.

**Methodological Contribution**: By creating an explicit narrative layer between time series and language models, we enable interpretable cross-modal alignment. Unlike black-box adaptation methods, our narratives provide human-readable explanations of what patterns the model learns to align.

**Practical Value**: The framework reduces dependency on large-scale labeled datasets while improving generalization. Pretrained models can be applied zero-shot to new domains by leveraging linguistic knowledge about domain contexts, trends, and patterns embedded in LLMs.

**Broader Implications**: Our approach aligns with the workshop's focus on building time series foundation models, analyzing their capabilities, and leveraging pretrained models from other modalities. It directly addresses the data scarcity challenge highlighted as a key limitation in time series research.

## 3. Methodology

### 3.1 Overall Framework Architecture

Our framework consists of three interconnected components that work synergistically to enable cross-modal alignment:

**Component 1: Multi-Granular Narrative Generator (MG-NG)**
**Component 2: Dual-Encoder Contrastive Learning Architecture (DE-CLA)**
**Component 3: LLM-Guided Knowledge Distillation (LLM-KD)**

The complete training pipeline operates in two stages: (1) synthetic narrative generation from unlabeled time series, and (2) joint pretraining of time series and text encoders with knowledge distillation.

### 3.2 Multi-Granular Narrative Generator

#### 3.2.1 Statistical Pattern Extraction

For a given time series $\mathbf{x} = \{x_1, x_2, ..., x_T\}$ of length $T$, we extract multiple levels of patterns:

**Trend Analysis**: We apply Seasonal-Trend decomposition using LOESS (STL) to extract trend component $\mathbf{t}$:
$$\mathbf{x} = \mathbf{t} + \mathbf{s} + \mathbf{r}$$
where $\mathbf{s}$ is seasonal component and $\mathbf{r}$ is residual. We characterize trends using:
- Slope: $\beta = \frac{\sum_{i=1}^T (i - \bar{i})(t_i - \bar{t})}{\sum_{i=1}^T (i - \bar{i})^2}$
- Monotonicity score: $M = \frac{1}{T-1}\sum_{i=1}^{T-1} \text{sign}(t_{i+1} - t_i)$

**Seasonality Detection**: We identify periodicities using autocorrelation function (ACF):
$$\rho(k) = \frac{\sum_{i=1}^{T-k}(x_i - \bar{x})(x_{i+k} - \bar{x})}{\sum_{i=1}^T(x_i - \bar{x})^2}$$
Significant peaks in $\rho(k)$ indicate periods $P = \{p_1, p_2, ..., p_m\}$.

**Volatility Characterization**: We compute rolling statistics:
$$\sigma_w(i) = \sqrt{\frac{1}{w}\sum_{j=i-w+1}^{i}(x_j - \mu_w(i))^2}$$
where $w$ is window size and $\mu_w(i)$ is rolling mean.

**Anomaly Detection**: Using Isolation Forest and statistical thresholds:
$$\mathcal{A} = \{i : |x_i - \mu| > \alpha\sigma \text{ or } \text{IsolationScore}(x_i) > \tau\}$$

#### 3.2.2 Template-Based Narrative Construction

We design hierarchical templates that transform statistical features into coherent narratives:

**Level 1 - Basic Description**:
```
"This time series shows {trend_descriptor} with {volatility_descriptor}. 
The overall pattern indicates {pattern_type}."
```

**Level 2 - Statistical Details**:
```
"The series exhibits a {trend_direction} trend with slope {slope_value}. 
Seasonality is detected at {period_list}. Volatility ranges from 
{min_vol} to {max_vol}."
```

**Level 3 - Contextual Reasoning** (LLM-enhanced):
We use a frozen LLM (e.g., GPT-3.5) with prompting:
```
Given features: {extracted_features} and domain: {domain_hint}
Generate interpretive context: potential causes, implications, 
and domain-specific insights.
```

#### 3.2.3 Multi-View Narrative Generation

For each time series, we generate narratives at different temporal granularities:
- **Global view**: Full sequence characteristics
- **Local views**: Sliding windows $W = \{[i, i+w] : i = 1, 2, ..., T-w\}$
- **Multi-scale views**: Different resolutions through downsampling

This produces a set of narratives $\mathcal{N}(\mathbf{x}) = \{n_1, n_2, ..., n_K\}$ for each series $\mathbf{x}$.

### 3.3 Dual-Encoder Architecture with Contrastive Learning

#### 3.3.1 Time Series Encoder

We employ a Transformer-based architecture with temporal convolutions:

$$\mathbf{h}_0 = \text{TemporalConv}(\mathbf{x}) + \text{PositionalEncoding}(T)$$

$$\mathbf{h}_l = \text{TransformerBlock}(\mathbf{h}_{l-1}), \quad l = 1, 2, ..., L$$

$$\mathbf{z}_{ts} = \text{Projection}(\text{GlobalPool}(\mathbf{h}_L))$$

where $\mathbf{z}_{ts} \in \mathbb{R}^d$ is the time series embedding.

#### 3.3.2 Text Encoder

We use a pretrained language model (e.g., BERT, RoBERTa) with additional projection:

$$\mathbf{h}_{text} = \text{LM}(n_i), \quad n_i \in \mathcal{N}(\mathbf{x})$$

$$\mathbf{z}_{text} = \text{Projection}(\mathbf{h}_{text}[\text{CLS}])$$

where $\mathbf{z}_{text} \in \mathbb{R}^d$ shares dimension with $\mathbf{z}_{ts}$.

#### 3.3.3 Contrastive Learning Objective

We implement a multi-positive contrastive loss inspired by CLIP:

$$\mathcal{L}_{contrast} = -\frac{1}{B}\sum_{i=1}^B \log \frac{\sum_{j \in \mathcal{P}(i)} \exp(\text{sim}(\mathbf{z}_{ts}^i, \mathbf{z}_{text}^j)/\tau)}{\sum_{k=1}^B \exp(\text{sim}(\mathbf{z}_{ts}^i, \mathbf{z}_{text}^k)/\tau)}$$

where:
- $B$ is batch size
- $\mathcal{P}(i)$ is the set of positive narrative indices for time series $i$
- $\text{sim}(\cdot, \cdot)$ is cosine similarity
- $\tau$ is temperature parameter

Additionally, we include a symmetric text-to-timeseries loss:

$$\mathcal{L}_{total} = \mathcal{L}_{contrast}^{ts \to text} + \mathcal{L}_{contrast}^{text \to ts}$$

### 3.4 LLM-Guided Knowledge Distillation

To transfer reasoning capabilities from LLMs, we implement a distillation mechanism:

#### 3.4.1 Semantic Similarity Distillation

For a frozen pretrained LLM that generates embeddings $\mathbf{z}_{LLM}$ from narratives, we minimize:

$$\mathcal{L}_{distill} = \text{MSE}(\mathbf{z}_{ts}, \text{StopGrad}(\mathbf{z}_{LLM})) + \text{KL}(P_{ts}||P_{LLM})$$

where $P_{ts}$ and $P_{LLM}$ are probability distributions over a shared vocabulary of concepts.

#### 3.4.2 Relation Preservation

We preserve relationships between samples:

$$\mathcal{L}_{relation} = \sum_{i,j} (\text{sim}(\mathbf{z}_{ts}^i, \mathbf{z}_{ts}^j) - \text{sim}(\mathbf{z}_{LLM}^i, \mathbf{z}_{LLM}^j))^2$$

The final training objective combines all components:

$$\mathcal{L} = \lambda_1 \mathcal{L}_{total} + \lambda_2 \mathcal{L}_{distill} + \lambda_3 \mathcal{L}_{relation}$$

### 3.5 Data Collection and Preprocessing

#### 3.5.1 Pretraining Data

We collect diverse unlabeled time series from:
- **Public repositories**: UCR Archive, Monash Forecasting Repository
- **Domain-specific sources**: Energy (electricity demand), Finance (stock prices), Healthcare (vital signs), Climate (weather stations)
- **Synthetic augmentation**: Generate diverse patterns using controllable synthesis

Target: 1M+ time series spanning 50+ domains with varying lengths (100-10,000 steps), frequencies, and characteristics.

#### 3.5.2 Preprocessing Pipeline

1. **Normalization**: z-score normalization per series
2. **Length handling**: Segment long series, pad short series
3. **Missing value imputation**: Linear interpolation with mask tokens
4. **Multi-resolution sampling**: Create views at 1x, 2x, 4x downsampling

### 3.6 Experimental Design

#### 3.6.1 Pretraining Phase

**Setup**:
- Time series encoder: 6-layer Transformer (d=512, h=8)
- Text encoder: RoBERTa-base with projection layer
- Batch size: 256, effective batch size: 4096 (with gradient accumulation)
- Optimizer: AdamW ($\beta_1=0.9, \beta_2=0.999$, weight decay=0.01)
- Learning rate: 1e-4 with cosine schedule
- Training steps: 500K
- Hardware: 8x A100 GPUs

**Ablation studies**:
1. Effect of narrative granularity (1-level vs. 3-level)
2. Impact of multi-view generation (single vs. multi-scale)
3. Contribution of distillation components
4. Temperature parameter $\tau$ sensitivity

#### 3.6.2 Evaluation Tasks

**Zero-shot Transfer**:
- Forecasting on unseen domains (8 datasets from different sectors)
- Classification on UCR benchmark (20 datasets)
- Anomaly detection on Yahoo, NASA datasets

**Few-shot Learning**:
- Fine-tune with k={1, 5, 10, 50} labeled examples per class
- Measure sample efficiency vs. baselines

**Domain Adaptation**:
- Train on source domain, test on target with distribution shift
- Measure robustness to temporal and statistical drift

#### 3.6.3 Baseline Comparisons

We compare against:
1. **Time series models**: Lag-Llama, TimesFM, Chronos
2. **Cross-modal methods**: VisionTS++, Context-Alignment
3. **Supervised baselines**: PatchTST, TimesNet (with full labels)
4. **Traditional methods**: ARIMA, Prophet (for forecasting)

#### 3.6.4 Evaluation Metrics

**Forecasting**:
- Mean Absolute Error (MAE), Root Mean Squared Error (RMSE)
- Mean Absolute Percentage Error (MAPE)
- Continuous Ranked Probability Score (CRPS) for probabilistic forecasts

**Classification**:
- Accuracy, F1-score (macro/micro)
- Area Under ROC Curve (AUC-ROC)

**Anomaly Detection**:
- Precision, Recall, F1-score
- Area Under Precision-Recall Curve (AUPRC)

**Interpretability**:
- Human evaluation of narrative quality (coherence, relevance)
- Alignment score: correlation between model attention and narrative segments
- Retrieval accuracy: correct time series retrieval given narrative query

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes**:

1. **Scalable Cross-Modal Pretraining**: We expect to demonstrate that synthetic narrative generation enables pretraining on effectively unlimited (time series, text) pairs, overcoming the labeled data bottleneck. Our framework should generate 10M+ high-quality narrative-aligned pairs from 1M unlabeled time series.

2. **Superior Zero-Shot Transfer**: Pretrained models should achieve 15-25% improvement in zero-shot forecasting accuracy compared to domain-specific models trained from scratch, and 10-15% improvement over existing foundation models that lack cross-modal alignment.

3. **Enhanced Few-Shot Learning**: With access to linguistic priors through LLM knowledge distillation, we anticipate 2-5x sample efficiency improvement in few-shot scenarios (achieving comparable performance with 5 examples vs. 25 examples for baselines).

4. **Interpretable Representations**: The narrative bridge should enable novel interpretability features—retrieving relevant time series given text queries with >80% accuracy, and generating coherent explanations for model predictions validated through human studies (>75% coherence rating).

**Technical Deliverables**:

1. Open-source implementation of the complete framework
2. Pretrained model weights for time series encoder
3. Generated dataset of 10M+ (time series, narrative) pairs
4. Comprehensive benchmark results across 50+ datasets
5. Interactive demo for narrative-based time series retrieval

### 4.2 Scientific Impact

**Advancing Time Series Foundation Models**: This research introduces a new paradigm for building time series foundation models that explicitly leverages cross-modal alignment. By demonstrating that synthetic narratives can effectively bridge numerical patterns and linguistic knowledge, we provide a blueprint for future foundation model architectures that combine the strengths of statistical time series analysis and language model reasoning.

**Theoretical Contributions**: Our work will provide empirical evidence and theoretical insights into:
- How different granularities of narrative description affect representation learning
- The relationship between statistical pattern complexity and narrative expressiveness
- Conditions under which cross-modal pretraining outperforms single-modality approaches

**Methodological Innovation**: The automated narrative generation approach represents a novel self-supervised learning paradigm that could extend beyond time series to other structured data modalities (graphs, tabular data, scientific measurements) where paired text descriptions are scarce.

### 4.3 Practical Impact

**Democratizing Time Series AI**: By eliminating the need for extensive labeled datasets, our framework makes advanced time series modeling accessible to:
- Small organizations without resources for large-scale annotation
- Emerging domains with limited historical data
- Rapid prototyping scenarios requiring quick deployment

**Domain-Specific Applications**:

*Healthcare*: Zero-shot transfer of models pretrained on vital signs monitoring to rare diseases with limited patient data, with narratives providing clinical interpretability.

*Energy*: Adaptation of forecasting models to new renewable energy installations using linguistic descriptions of weather patterns and generation profiles.

*Finance*: Cross-market transfer learning leveraging economic narratives and shared market dynamics across different instruments and regions.

**Industrial Adoption**: The interpretable nature of narrative-aligned models addresses a critical barrier to deploying AI in regulated industries (finance, healthcare) where explainability is mandatory.

### 4.4 Broader Implications

**Bridging AI Subdisciplines**: This work exemplifies productive synergy between time series analysis, natural language processing, and multimodal learning. Success would encourage more cross-pollination of techniques across AI subfields.

**Addressing Workshop Themes**: Our proposal directly addresses multiple workshop priorities:
- Building time series foundation models with novel design choices
- Leveraging pretrained models from other modalities (LLMs)
- Creating large-scale datasets through synthetic generation
- Enhancing interpretability of pretrained models
- Demonstrating real-world applications

**Future Research Directions**: This work opens several promising avenues:
- Extending to multimodal time series with video, audio, or sensor fusion
- Interactive learning where human feedback on narratives improves model alignment
- Causal reasoning by incorporating causal language in narratives
- Online adaptation where models generate and learn from narratives in deployment

### 4.5 Validation and Robustness

To ensure the reliability and generalizability of our results, we commit to:

1. **Comprehensive ablations** isolating the contribution of each component
2. **Cross-domain validation** on held-out domains not seen during pretraining
3. **Statistical significance testing** with multiple random seeds and confidence intervals
4. **Failure mode analysis** documenting scenarios where the approach underperforms
5. **Computational efficiency benchmarks** measuring training and inference costs
6. **Reproducibility package** with detailed documentation and containerized environments

### 4.6 Timeline and Milestones

- **Months 1-3**: Implement narrative generator and validate quality through human studies
- **Months 4-6**: Develop dual-encoder architecture and pretraining pipeline
- **Months 7-9**: Large-scale pretraining on 1M+ time series
- **Months 10-12**: Comprehensive evaluation on downstream tasks and baseline comparisons
- **Months 13-15**: Ablation studies, failure mode analysis, and refinement
- **Months 16-18**: Real-world case studies, open-source release, and publication

This research proposal presents a comprehensive plan to advance time series foundation models through innovative cross-modal alignment using synthetic narratives. By addressing critical challenges in data scarcity, interpretability, and transferability, we aim to push the frontier of time series research in the age of large models while maintaining scientific rigor and practical applicability.