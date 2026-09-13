# Research Proposal: Probing-Based Model Selection for Time Series Foundation Models: Characterizing Semantic vs. Temporal Knowledge

## 1. Introduction

### 1.1 Background

The emergence of foundation models has fundamentally transformed machine learning paradigms across multiple domains. In natural language processing and computer vision, large-scale pretrained models have demonstrated remarkable capabilities in zero-shot and few-shot transfer to diverse downstream tasks. This paradigm shift has recently extended to time series analysis, where Time Series Foundation Models (TSFMs) are gaining significant traction for tasks including forecasting, classification, and anomaly detection.

The current TSFM landscape comprises two distinct architectural families. **Native TSFMs**, such as Chronos and Lag-Llama, are designed and pretrained specifically for time series data, incorporating inductive biases tailored to temporal patterns, seasonality, and trend dynamics. **LLM-adapted TSFMs**, including Time-LlaMA and ChatTime, leverage pretrained Large Language Models and adapt them for time series tasks through various techniques such as tokenization schemes, prompting strategies, and fine-tuning approaches. Recent theoretical work by Riachi et al. (2025) has demonstrated a "non-vanishing transfer gap," suggesting that LLM-adapted models bring unique transferable knowledge that cannot be replicated by training from random initialization.

Despite the proliferation of TSFMs, practitioners face a critical challenge: **principled model selection**. Currently, selecting between native and LLM-adapted TSFMs relies on expensive trial-and-error experimentation across benchmarks, with limited understanding of why certain models excel on specific tasks. This knowledge gap stems from the black-box nature of these models—we lack interpretable frameworks for understanding what types of knowledge each architecture captures and how task characteristics should inform model choice.

### 1.2 Research Objectives

This research proposes a novel **probing-based model selection framework** that addresses the fundamental question: *What knowledge types do different TSFM architectures capture, and how can this understanding guide model selection?*

Our primary objectives are:

1. **Develop a probing methodology** to quantify semantic versus temporal information content in TSFM intermediate representations using linear classifiers as information-theoretic probes.

2. **Establish the relationship** between the semantic-to-temporal information ratio and model type performance advantage across diverse forecasting tasks.

3. **Create a practical model selection framework** that achieves significantly better-than-random selection accuracy (>65% vs. 50% baseline) while providing interpretable insights into TSFM knowledge attribution.

4. **Validate the framework** across multiple benchmarks (Monash, FinTSB, GIFT-Eval) spanning diverse domains including finance, healthcare, retail, and energy.

### 1.3 Research Significance

This research addresses multiple critical gaps in the time series foundation model literature:

**Theoretical Contribution:** We provide the first systematic framework for characterizing knowledge types in TSFMs, bridging the gap between NLP probing methodologies (Belinkov & Glass, 2019) and time series representation analysis. By connecting linear probing to mutual information estimation (Choi et al., 2023), we establish a theoretically grounded approach for understanding TSFM representations.

**Practical Impact:** Our framework offers practitioners actionable guidance for model selection, potentially reducing the computational cost and time associated with exhaustive model comparison. For organizations deploying TSFMs in production, this translates to faster deployment cycles and more informed architectural decisions.

**Interpretability Advancement:** By revealing what knowledge types different architectures capture, we address the criticism that pretrained time series models are opaque compared to interpretable statistical methods. This contributes to the broader goal of making foundation models more transparent and trustworthy.

---

## 2. Methodology

### 2.1 Research Design Overview

Our methodology comprises four interconnected components: (1) probing classifier design and training, (2) information content quantification, (3) model selection rule derivation, and (4) comprehensive experimental validation. Figure 1 illustrates the overall framework architecture.

### 2.2 Probing Classifier Design

#### 2.2.1 Representation Extraction

For each TSFM $\mathcal{M}$, we extract intermediate representations from multiple layers. Given an input time series $\mathbf{x} = (x_1, x_2, \ldots, x_T)$, we obtain layer-wise representations:

$$\mathbf{h}^{(l)} = f^{(l)}_{\mathcal{M}}(\mathbf{x}) \in \mathbb{R}^{d_l}$$

where $l \in \{1, 2, \ldots, L\}$ denotes the layer index and $d_l$ is the representation dimensionality at layer $l$.

#### 2.2.2 Semantic Probing Tasks

We design probing tasks to measure semantic information content—knowledge related to contextual metadata, domain characteristics, and cross-modal signals:

**Task S1 (Domain Classification):** Predict the domain label $y_{\text{domain}} \in \{1, \ldots, K\}$ from representations:
$$\hat{y}_{\text{domain}} = \text{softmax}(\mathbf{W}_{\text{domain}} \mathbf{h}^{(l)} + \mathbf{b}_{\text{domain}})$$

**Task S2 (Metadata Prediction):** Predict categorical metadata attributes (e.g., industry sector, geographic region) from representations.

**Task S3 (Textual Alignment):** For datasets with textual descriptions, predict whether a representation aligns with a given text embedding using contrastive probing.

#### 2.2.3 Temporal Probing Tasks

We design probing tasks to measure temporal information content—knowledge related to patterns, dynamics, and forecasting-relevant features:

**Task T1 (Periodicity Detection):** Predict the dominant periodicity class $y_{\text{period}} \in \{\text{daily}, \text{weekly}, \text{monthly}, \text{yearly}, \text{none}\}$:
$$\hat{y}_{\text{period}} = \text{softmax}(\mathbf{W}_{\text{period}} \mathbf{h}^{(l)} + \mathbf{b}_{\text{period}})$$

**Task T2 (Trend Direction):** Predict trend direction $y_{\text{trend}} \in \{\text{increasing}, \text{decreasing}, \text{stationary}\}$.

**Task T3 (Next-Step Regression):** Predict the next value $x_{T+1}$ using a linear probe:
$$\hat{x}_{T+1} = \mathbf{w}_{\text{next}}^\top \mathbf{h}^{(l)} + b_{\text{next}}$$

#### 2.2.4 Probe Training Protocol

All probes are linear classifiers or regressors to ensure interpretability and prevent memorization. We train probes using the following protocol:

1. **Freeze TSFM parameters** to ensure probes measure existing information rather than learning new representations.
2. **Train with cross-entropy loss** (classification) or MSE loss (regression).
3. **Apply 5-fold cross-validation** within the probe training set.
4. **Use early stopping** based on validation performance to prevent overfitting.

### 2.3 Information Content Quantification

#### 2.3.1 Probe-Based Mutual Information Estimation

Following Choi et al. (2023), we connect linear probe accuracy to mutual information. For a probing task predicting target $Y$ from representation $\mathbf{H}$, the probe accuracy $\text{Acc}(\mathbf{H} \rightarrow Y)$ provides a lower bound on mutual information:

$$I(\mathbf{H}; Y) \geq H(Y) - H(Y | \hat{Y})$$

where $H(Y)$ is the entropy of the target and $H(Y | \hat{Y})$ is the conditional entropy given probe predictions.

#### 2.3.2 Semantic and Temporal Information Scores

We aggregate probe accuracies into composite scores:

**Semantic Information Score:**
$$S_{\text{sem}}(\mathcal{M}) = \frac{1}{|S|} \sum_{s \in S} \text{Acc}_s(\mathcal{M})$$

where $S = \{S1, S2, S3\}$ is the set of semantic probing tasks.

**Temporal Information Score:**
$$S_{\text{temp}}(\mathcal{M}) = \frac{1}{|T|} \sum_{t \in T} \text{Acc}_t(\mathcal{M})$$

where $T = \{T1, T2, T3\}$ is the set of temporal probing tasks.

#### 2.3.3 Semantic-to-Temporal Ratio

We compute the knowledge characterization ratio:

$$R_{\text{ST}}(\mathcal{M}) = \frac{S_{\text{sem}}(\mathcal{M})}{S_{\text{temp}}(\mathcal{M})}$$

This ratio characterizes the relative emphasis of semantic versus temporal knowledge in model $\mathcal{M}$.

### 2.4 Model Selection Rule

#### 2.4.1 Task-Specific Context Richness

For each forecasting task $\tau$, we compute a **context richness score** $C(\tau) \in [0, 1]$ based on:
- Availability of domain metadata (0.3 weight)
- Presence of textual descriptions (0.3 weight)
- Cross-domain signal availability (0.2 weight)
- Historical context length (0.2 weight)

#### 2.4.2 Selection Decision Rule

Given a task $\tau$ with context richness $C(\tau)$ and candidate models $\mathcal{M}_{\text{LLM}}$ (LLM-adapted) and $\mathcal{M}_{\text{native}}$ (native TSFM), we recommend:

$$\text{Recommend}(\tau) = \begin{cases} \mathcal{M}_{\text{LLM}} & \text{if } R_{\text{ST}}(\mathcal{M}_{\text{LLM}}) \cdot C(\tau) > \theta \\ \mathcal{M}_{\text{native}} & \text{otherwise} \end{cases}$$

where $\theta$ is a threshold learned from validation data.

#### 2.4.3 Threshold Optimization

We optimize $\theta$ to maximize selection accuracy on a held-out validation set:

$$\theta^* = \arg\max_{\theta} \frac{1}{|\mathcal{T}_{\text{val}}|} \sum_{\tau \in \mathcal{T}_{\text{val}}} \mathbb{1}[\text{Recommend}(\tau) = \text{BestModel}(\tau)]$$

### 2.5 Experimental Design

#### 2.5.1 Datasets and Benchmarks

We evaluate on three diverse benchmarks:

| Benchmark | Domains | Tasks | Context Richness |
|-----------|---------|-------|------------------|
| Monash | Energy, Traffic, Finance, Health | 30+ | Variable |
| FinTSB | Financial markets | 20+ | High (news, metadata) |
| GIFT-Eval | General forecasting | 40+ | Variable |

**Total task-model pairs:** ≥88 (satisfying statistical power requirements)

#### 2.5.2 Model Selection

**Native TSFMs:**
- Chronos-Base (~200M parameters)
- Lag-Llama (~300M parameters)

**LLM-Adapted TSFMs:**
- Time-LlaMA-7B with LoRA (~300M effective parameters)
- ChatTime (~350M parameters)

We control for parameter count by comparing models of similar scale.

#### 2.5.3 Evaluation Metrics

**Primary Metric - Model Selection Accuracy:**
$$\text{MSA} = \frac{\text{Number of correct recommendations}}{\text{Total number of tasks}} \times 100\%$$

**Secondary Metrics:**
- **Forecasting Performance:** MSE, MAE, CRPS (Continuous Ranked Probability Score)
- **Probe Accuracy Gap:** $|S_{\text{sem}} - S_{\text{temp}}|$ to validate information separability
- **Computational Overhead:** Probing time as percentage of inference time

#### 2.5.4 Statistical Analysis

**Sample Size Justification:**
- Effect size (Cohen's h): 0.30 (detecting 65% vs. 50%)
- Required sample size: $n \geq 88$ task-model pairs
- Statistical power: 0.80
- Significance level: $\alpha = 0.05$

**Statistical Tests:**
- One-sample proportion test against 50% baseline
- 95% confidence intervals for selection accuracy
- Paired t-tests for within-task model comparisons

#### 2.5.5 Ablation Studies

1. **Layer Selection:** Compare probing at early, middle, and late layers
2. **Probe Complexity:** Linear vs. 2-layer MLP probes
3. **Task Subset:** Individual probing tasks vs. aggregated scores
4. **Threshold Sensitivity:** Robustness of $\theta$ across different validation splits

#### 2.5.6 Baseline Comparisons

| Baseline | Description | Expected Accuracy |
|----------|-------------|-------------------|
| Random | Uniform random selection | 50% |
| Always-LLM | Always select LLM-adapted model | ~50% |
| Always-Native | Always select native TSFM | ~50% |
| Oracle | Perfect selection (upper bound) | 100% |
| Probing-Based (Ours) | Proposed framework | >65% |

### 2.6 Implementation Details

**Computational Resources:**
- GPU: 4× NVIDIA A100 (80GB)
- Probe training: ~2 hours per model-benchmark combination
- Total experimental time: ~200 GPU-hours

**Software Stack:**
- PyTorch for model implementation
- HuggingFace Transformers for LLM-adapted models
- GluonTS for time series utilities
- Scikit-learn for probe training and evaluation

---

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Outcome 1: Validated Model Selection Framework**
We expect to achieve model selection accuracy exceeding 65% (vs. 50% random baseline) with statistical significance ($p < 0.05$). This represents a meaningful improvement that translates to practitioners making correct model choices approximately two-thirds of the time based on interpretable probing analysis.

**Outcome 2: Knowledge Attribution Insights**
We anticipate confirming our hypothesis that LLM-adapted models encode richer semantic information (higher $S_{\text{sem}}$) while native TSFMs specialize in temporal patterns (higher $S_{\text{temp}}$). Specifically, we predict:
- LLM-adapted models: $R_{\text{ST}} > 1.2$
- Native TSFMs: $R_{\text{ST}} < 0.8$

**Outcome 3: Task Characterization Guidelines**
We will produce actionable guidelines mapping task characteristics to recommended model types:
- High context richness ($C(\tau) > 0.7$): Recommend LLM-adapted models
- Low context richness ($C(\tau) < 0.3$): Recommend native TSFMs
- Intermediate cases: Use probing-based decision rule

### 3.2 Secondary Expected Outcomes

**Outcome 4: Probing Methodology for TSFMs**
We will release a standardized probing toolkit for analyzing TSFM representations, enabling future research on model interpretability and knowledge attribution.

**Outcome 5: Benchmark Annotations**
We will provide context richness annotations for Monash, FinTSB, and GIFT-Eval benchmarks, facilitating reproducibility and future research.

### 3.3 Potential Negative Results and Contingencies

If our primary hypothesis is rejected (selection accuracy ≤55%), this would indicate that:
1. Semantic and temporal information may not be separable in TSFM representations
2. The relationship between information content and forecasting performance may be more complex than hypothesized
3. Alternative selection criteria (e.g., based on task complexity metrics) should be explored

Such negative results would still contribute valuable knowledge about TSFM representation structure and inform future research directions.

### 3.4 Broader Impact

**Scientific Impact:**
This research bridges the gap between NLP probing methodologies and time series analysis, establishing a new paradigm for understanding foundation model representations. The theoretical connection between probe accuracy and mutual information provides a principled framework applicable beyond time series to other modalities.

**Practical Impact:**
For practitioners deploying TSFMs in production environments, our framework reduces the cost of model selection from exhaustive benchmarking to efficient probing analysis. This is particularly valuable in resource-constrained settings or when rapid deployment is required.

**Community Impact:**
By providing interpretable insights into TSFM knowledge attribution, we address the criticism that foundation models are opaque black boxes. This contributes to the broader goal of trustworthy AI and may inform regulatory discussions around model transparency.

### 3.5 Limitations and Future Work

**Current Limitations:**
- Probing analysis adds computational overhead (~10-20% of inference time)
- Framework requires validation for each new TSFM architecture
- Limited to forecasting tasks; extension to classification and anomaly detection requires additional probing task design

**Future Directions:**
1. **Dynamic Model Selection:** Extend to online settings where model selection adapts based on streaming data characteristics
2. **Multi-Modal Probing:** Incorporate probing tasks for additional modalities (images, graphs) in multi-modal time series settings
3. **Automated Probe Design:** Develop meta-learning approaches to automatically design probing tasks for new domains
4. **Causal Analysis:** Investigate causal relationships between representation structure and forecasting performance using intervention-based methods

---
