# Research Proposal: Safety-Aware Data Selection (SADS) for Preemptive Safety Filtering in Multimodal Foundation Model Pre-training

## 1. Introduction

### 1.1 Background

The rapid advancement of multimodal foundation models—systems that integrate language, image, video, and audio understanding—has transformed artificial intelligence applications across robotics, healthcare, creative industries, and human-computer interaction. These models, trained on web-scale datasets comprising billions of text-image pairs, demonstrate remarkable capabilities in understanding and generating content across modalities. However, this power comes with significant responsibility challenges: Large Language Models (LLMs) produce hallucinations, Text-to-Image (T2I) diffusion models generate harmful content, and multimodal systems exhibit biases that reflect and amplify societal inequities.

Current approaches to addressing these safety concerns predominantly rely on post-hoc interventions. Reinforcement Learning from Human Feedback (RLHF), Constitutional AI, and representation engineering methods like RepBend are applied after pre-training to align model behavior with human values. While effective to varying degrees, these reactive approaches suffer from fundamental limitations: they are computationally expensive (often requiring resources comparable to initial training), they address symptoms rather than root causes, and they engage in an ongoing arms race against adversarial exploitation of already-encoded problematic patterns.

Recent research has begun illuminating the data-centric origins of safety vulnerabilities. The Layer-Aware Representation Filtering (LARF) framework demonstrates that safety-degrading features can be detected in fine-tuning data, suggesting that problematic patterns are identifiable before they influence model behavior. Similarly, work on model-based data selection reveals that only 15% of pre-training tokens are necessary for maintaining capability benchmarks, indicating substantial headroom for selective curation. The RefinedWeb methodology has established scalable approaches for quality-based filtering of web-scale data, processing CommonCrawl to produce 5 trillion high-quality tokens.

Despite these advances, a critical gap remains: no systematic approach exists for filtering safety risks at the pre-training stage—the phase where problematic patterns first become encoded into model representations. This gap perpetuates the costly cycle of training potentially unsafe models and subsequently patching them through resource-intensive alignment procedures.

### 1.2 Research Objectives

This research proposes Safety-Aware Data Selection (SADS), a methodology that integrates multi-dimensional safety classification into pre-training data curation for multimodal foundation models. Our primary objectives are:

1. **Develop a scalable safety-aware data curation pipeline** that employs an ensemble of safety classifiers to score web-scale text-image data across multiple safety dimensions (toxicity, bias, NSFW content, violence, misinformation).

2. **Validate the hypothesis** that filtering training samples based on composite safety scores before pre-training prevents safety-problematic patterns from being encoded into model representations, thereby reducing downstream vulnerabilities more efficiently than post-hoc alignment.

3. **Establish the safety-capability tradeoff frontier** by systematically varying filtering thresholds and measuring both safety violation rates and capability preservation metrics.

4. **Demonstrate computational efficiency advantages** of preemptive safety filtering compared to post-hoc alignment methods on total resource expenditure.

### 1.3 Significance

This research addresses the workshop's core themes of responsible design principles, reliability enhancement, and sustainable development of multimodal generative models. By shifting safety interventions from post-hoc correction to preemptive curation, SADS offers several significant contributions:

- **Proactive Safety**: Establishes a paradigm where safety is designed into foundation models from inception rather than retrofitted after deployment.
- **Resource Efficiency**: Reduces the substantial computational burden of post-hoc alignment by preventing problematic patterns from being encoded initially.
- **Scalability**: Leverages one-time curation costs that amortize across all downstream applications of the curated dataset.
- **Transparency**: Creates auditable data selection criteria that enable understanding of what content was filtered and why.

## 2. Methodology

### 2.1 Overview

The SADS methodology comprises four integrated components: (1) safety classifier ensemble construction, (2) multi-dimensional safety scoring of pre-training data, (3) threshold-based filtering with capability preservation constraints, and (4) comparative evaluation against baseline approaches. Figure 1 illustrates the complete pipeline.

### 2.2 Safety Classifier Ensemble Construction

We construct an ensemble of $K$ safety classifiers, each targeting a distinct safety dimension. Let $\mathcal{C} = \{c_1, c_2, \ldots, c_K\}$ denote the classifier ensemble, where each classifier $c_k: \mathcal{X} \rightarrow [0, 1]$ maps a multimodal sample $x \in \mathcal{X}$ to a safety risk score in the specified dimension.

**Classifier Selection Criteria:**
- **Coverage**: Classifiers must collectively address toxicity, bias, NSFW content, violence, and misinformation
- **Modality Awareness**: Classifiers must process both text and image components
- **Computational Efficiency**: Per-sample inference must be feasible at web-scale (billions of samples)
- **Calibration**: Classifier outputs must be well-calibrated probability estimates

**Proposed Ensemble Composition ($K=5$):**

| Classifier | Safety Dimension | Input Modality | Base Model |
|------------|------------------|----------------|------------|
| $c_1$: Toxicity Classifier | Toxic language, hate speech | Text | Perspective API / fine-tuned RoBERTa |
| $c_2$: Bias Detector | Gender, racial, religious bias | Text + Image | Custom CLIP-based classifier |
| $c_3$: NSFW Detector | Explicit sexual content | Image | CLIP-based NSFW classifier |
| $c_4$: Violence Detector | Graphic violence, gore | Image | Fine-tuned ViT classifier |
| $c_5$: Misinformation Detector | Factual inconsistency | Text + Image | Cross-modal consistency checker |

**Ensemble Calibration:**
Each classifier undergoes temperature scaling calibration on a held-out validation set $\mathcal{V}$ to ensure probability estimates reflect true risk frequencies:

$$\hat{c}_k(x) = \sigma\left(\frac{z_k(x)}{T_k}\right)$$

where $z_k(x)$ is the pre-softmax logit, $T_k$ is the learned temperature parameter, and $\sigma$ is the sigmoid function.

### 2.3 Multi-Dimensional Safety Scoring

For each sample $x_i$ in the pre-training dataset $\mathcal{D} = \{x_1, x_2, \ldots, x_N\}$, we compute a multi-dimensional safety score vector:

$$\mathbf{s}_i = [c_1(x_i), c_2(x_i), \ldots, c_K(x_i)] \in [0, 1]^K$$

**Composite Safety Score:**
We aggregate dimension-specific scores into a composite safety risk score using a weighted maximum approach:

$$S(x_i) = \max_{k \in \{1, \ldots, K\}} w_k \cdot c_k(x_i)$$

where $w_k \geq 0$ are dimension-specific weights satisfying $\sum_k w_k = K$. The maximum aggregation ensures that samples with high risk in any single dimension are flagged, while weights allow prioritization of certain safety dimensions.

**Alternative Aggregation (Ablation):**
We also evaluate weighted average aggregation for comparison:

$$S_{\text{avg}}(x_i) = \frac{1}{K} \sum_{k=1}^{K} w_k \cdot c_k(x_i)$$

### 2.4 Threshold-Based Filtering

**Binary Filtering:**
Given a safety threshold $T \in [0, 1]$, we partition the dataset into safe and unsafe subsets:

$$\mathcal{D}_{\text{safe}} = \{x_i \in \mathcal{D} : S(x_i) < T\}$$
$$\mathcal{D}_{\text{unsafe}} = \{x_i \in \mathcal{D} : S(x_i) \geq T\}$$

The filtered dataset $\mathcal{D}_{\text{SADS}} = \mathcal{D}_{\text{safe}}$ is used for pre-training.

**Loss Weighting (Alternative):**
Instead of binary filtering, we explore continuous loss weighting inversely proportional to safety risk:

$$\mathcal{L}_{\text{SADS}} = \sum_{i=1}^{N} (1 - S(x_i))^\alpha \cdot \ell(x_i; \theta)$$

where $\ell(x_i; \theta)$ is the standard pre-training loss for sample $x_i$ with model parameters $\theta$, and $\alpha > 0$ controls the weighting strength.

**Threshold Tuning Protocol:**
We tune the threshold $T$ using a held-out safety validation set $\mathcal{V}_{\text{safety}}$ containing samples with ground-truth safety labels. The optimal threshold $T^*$ is selected to maximize the F1-score on safety classification:

$$T^* = \arg\max_{T \in [0.3, 0.9]} F_1(\mathcal{V}_{\text{safety}}, T)$$

We additionally constrain $T^*$ such that the filtered dataset retains at least 50% of original samples to ensure sufficient training data.

### 2.5 Experimental Design

**Research Questions:**
- **RQ1**: Does SADS-filtered pre-training reduce downstream safety vulnerability rates compared to quality-only filtering?
- **RQ2**: What is the safety-capability tradeoff frontier across filtering thresholds?
- **RQ3**: Does SADS reduce post-hoc alignment requirements for achieving target safety levels?

**Experimental Conditions:**

| Condition | Data Curation | Post-hoc Alignment |
|-----------|---------------|-------------------|
| Baseline-Q | Quality-only (RefinedWeb methodology) | None |
| Baseline-Q+A | Quality-only | RepBend / RLHF |
| SADS-T0.5 | SADS with $T=0.5$ | None |
| SADS-T0.7 | SADS with $T=0.7$ | None |
| SADS-T0.5+A | SADS with $T=0.5$ | RepBend / RLHF |

**Data Collection:**

We utilize a subset of the LAION-5B dataset, applying the following pipeline:
1. **Initial Quality Filtering**: Apply RefinedWeb-style quality filters (language identification, deduplication, perplexity filtering)
2. **Safety Scoring**: Apply SADS classifier ensemble to quality-filtered data
3. **Threshold Filtering**: Generate filtered datasets at multiple thresholds

**Pilot Study**: 100 billion tokens, 1B parameter model
**Full Study**: 1 trillion tokens, 7B parameter model

**Model Architecture:**
We adopt a LLaVA-style vision-language architecture:
- Vision encoder: ViT-L/14 (frozen)
- Language model: LLaMA-style transformer
- Cross-modal projector: 2-layer MLP

All architectural choices and hyperparameters (learning rate: $3 \times 10^{-4}$, batch size: 2048, optimizer: AdamW) are held constant across conditions.

### 2.6 Evaluation Metrics

**Safety Metrics:**

1. **MMDT Safety Violation Rate**: Percentage of model outputs flagged as unsafe across 5 categories (toxicity, bias, NSFW, violence, misinformation) on the Multimodal Safety Benchmark

2. **CrossCheckGPT Hallucination Score**: Factual consistency ranking using cross-reference verification

3. **OutSafe-Bench Score**: Comprehensive multimodal safety evaluation across adversarial prompts

**Capability Metrics:**

1. **MMLU Accuracy**: Multi-task language understanding benchmark
2. **HellaSwag Score**: Commonsense reasoning benchmark
3. **VQA-v2 Accuracy**: Visual question answering capability
4. **COCO Captioning CIDEr**: Image captioning quality

**Efficiency Metrics:**

1. **Total Compute (FLOPs)**: Pre-training + alignment compute
2. **Alignment Iterations**: Number of RLHF/RepBend iterations to reach target safety level

### 2.7 Statistical Analysis

**Sample Size**: $n = 5$ independent training runs per condition (different random seeds)

**Primary Analysis (RQ1)**:
Two-proportion z-test comparing SADS vs. Baseline-Q safety violation rates:

$$z = \frac{\hat{p}_{\text{SADS}} - \hat{p}_{\text{Baseline}}}{\sqrt{\hat{p}(1-\hat{p})\left(\frac{1}{n_1} + \frac{1}{n_2}\right)}}$$

**Capability Equivalence Testing**:
Two one-sided t-tests (TOST) for equivalence within $\pm 2\%$ margin:

$$H_0: |\mu_{\text{SADS}} - \mu_{\text{Baseline}}| \geq \delta \quad \text{vs.} \quad H_1: |\mu_{\text{SADS}} - \mu_{\text{Baseline}}| < \delta$$

where $\delta = 0.02 \times \mu_{\text{Baseline}}$.

**Effect Size Reporting**: Cohen's h for proportions, Cohen's d for continuous metrics, with 95% confidence intervals.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1):**
We expect SADS-filtered models to achieve a statistically significant reduction in safety violation rates on the MMDT benchmark. Specifically, we predict:
- Safety violation rate reduction: $\geq 5$ percentage points (from baseline ~20% to SADS ~15% or lower)
- Statistical significance: $p < 0.05$ (one-tailed)
- Effect size: Cohen's h $\geq 0.3$ (medium effect)

**Capability Preservation (P1 continued):**
- MMLU accuracy within 2% of baseline: $|\Delta_{\text{MMLU}}| \leq 2\%$
- HellaSwag score within 2% of baseline: $|\Delta_{\text{HellaSwag}}| \leq 2\%$

**Mechanism Validation (P2):**
We expect to observe a monotonic relationship between filtering threshold and safety improvement, with diminishing returns at extreme thresholds. The Pareto frontier analysis will identify optimal operating points balancing safety and capability.

**Efficiency Advantage (P3):**
SADS-trained models requiring post-hoc alignment (SADS-T0.5+A) will achieve equivalent safety levels to Baseline-Q+A with:
- $\geq 30\%$ fewer RLHF iterations, OR
- $\geq 20\%$ lower total compute (pre-training + alignment)

### 3.2 Potential Negative Results and Contingencies

If the primary hypothesis is not supported, we will investigate:

1. **Classifier Failure Mode**: If safety classifiers show poor precision ($<0.5$) on pre-training data, we will develop domain-adapted classifiers using active learning on pre-training data samples.

2. **Safety-Capability Entanglement**: If capability degradation exceeds 5%, we will explore hybrid approaches combining lighter filtering with targeted loss weighting.

3. **Architecture Dependence**: If effects vary significantly across model scales, we will characterize the scale-dependent nature of data-level safety interventions.

### 3.3 Broader Impact

**Scientific Contributions:**
- First systematic study of safety-aware data curation for multimodal pre-training
- Empirical characterization of the safety-capability tradeoff in data selection
- Open-source release of safety-scored dataset annotations and curation pipeline

**Practical Impact:**
- Actionable guidelines for responsible foundation model development
- Reduced computational burden for achieving safety compliance
- Auditable data selection criteria for regulatory transparency

**Societal Implications:**
- Proactive harm prevention rather than reactive mitigation
- More equitable AI systems through bias-aware data curation
- Sustainable AI development through resource-efficient safety practices

### 3.4 Limitations and Future Work

**Current Limitations:**
- Initial scope limited to text-image modality; video and audio require modality-specific classifiers
- Classifier biases may propagate to data selection; ensemble diversity partially mitigates this
- Over-filtering may remove valuable edge cases important for robustness

**Future Directions:**
- Extension to video-language and audio-language modalities
- Integration with synthetic data generation for safety-aware data augmentation
- Development of adaptive filtering that adjusts thresholds based on data distribution shifts
- Investigation of safety-aware architecture design complementing data-level interventions

This research establishes foundational principles for proactive, resource-efficient safety in multimodal foundation model development, contributing to the responsible advancement of AI systems that benefit society while minimizing potential harms.