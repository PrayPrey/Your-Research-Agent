# Research Proposal: Entropy-Guided Adaptive Routing (EGAR): Dynamic Strategy Selection Between ICL and LoRA for Robust Foundation Model Adaptation

## 1. Introduction

### 1.1 Background

Foundation models have revolutionized machine learning by demonstrating unprecedented capabilities across diverse tasks through large-scale pretraining on heterogeneous data corpora. Models such as CLIP for vision-language understanding and LLaMA for natural language processing have achieved remarkable performance on standard benchmarks. However, a persistent challenge remains: distribution shifts—where deployment data differs systematically from training data—continue to degrade model performance substantially in real-world applications spanning biomedicine, autonomous systems, and scientific discovery.

The robustness of foundation models under distribution shift presents a nuanced picture. While these models often exhibit improved out-of-distribution (OOD) generalization compared to traditionally trained models, significant gaps persist between in-distribution (ID) and OOD performance. More critically, adaptation strategies designed to specialize foundation models for downstream tasks frequently compromise their inherent distributional robustness. Fine-tuning, while effective for improving ID performance, has been shown to reduce the OOD generalization capabilities that foundation models acquire during pretraining.

Two prominent adaptation paradigms have emerged with distinct robustness profiles. **In-Context Learning (ICL)** leverages the model's ability to learn from demonstrations provided at inference time without modifying parameters, thereby preserving pretrained representations and their associated robustness properties. **Low-Rank Adaptation (LoRA)** introduces trainable low-rank matrices to adapt model weights efficiently, enabling deeper specialization but potentially disrupting robust feature representations. Recent empirical evidence from URIAL and related work suggests these strategies exhibit complementary strengths: ICL maintains robustness but may lack task-specific depth, while LoRA provides specialization at potential robustness cost.

A critical insight from recent research, particularly the DaWin framework, reveals that predictive entropy—a measure of model uncertainty—serves as a reliable indicator of model competence on individual samples. Samples yielding low-entropy predictions indicate high model confidence and likely sufficient pretrained knowledge, while high-entropy predictions signal uncertainty and potential need for deeper adaptation. This observation raises a fundamental question: can we leverage per-sample entropy to dynamically route between adaptation strategies, applying lightweight ICL where the model is confident and deeper LoRA adaptation where uncertainty indicates insufficient pretrained knowledge?

### 1.2 Research Objectives

This research proposes **Entropy-Guided Adaptive Routing (EGAR)**, a novel framework for dynamic strategy selection between ICL and LoRA based on per-sample predictive entropy. Our primary objectives are:

1. **Develop a principled routing mechanism** that uses Shannon entropy as a decision criterion for selecting between ICL and LoRA adaptation strategies at inference time.

2. **Validate the causal hypothesis** that entropy reliably indicates model competence, with low entropy signaling sufficient pretrained knowledge (favoring ICL) and high entropy indicating need for parameter adaptation (favoring LoRA).

3. **Demonstrate superior OOD robustness** compared to uniform single-strategy baselines and existing adaptive methods such as DaWin.

4. **Achieve computational efficiency** by reducing inference costs through selective application of expensive LoRA adaptation only when necessary.

### 1.3 Significance

This research addresses a critical gap in foundation model deployment: the lack of principled methods for sample-adaptive strategy selection under distribution shift. Current approaches apply uniform adaptation strategies regardless of per-sample model confidence, missing opportunities for both improved robustness and computational efficiency. EGAR establishes a new paradigm for adaptive foundation model deployment that:

- Provides theoretical grounding for entropy-based routing through causal mechanism analysis
- Offers practical efficiency gains crucial for resource-constrained deployment scenarios
- Advances understanding of the complementary roles of ICL and parameter-efficient fine-tuning
- Contributes to the broader goal of developing foundation models that maintain robustness across diverse deployment conditions

## 2. Methodology

### 2.1 Problem Formulation

Consider a foundation model $f_\theta$ with pretrained parameters $\theta$, and a downstream task with training distribution $P_{train}$ and test distribution $P_{test}$ where $P_{test} \neq P_{train}$ (distribution shift). Given a test sample $x$, our goal is to select the optimal adaptation strategy $s \in \{ICL, LoRA\}$ that maximizes prediction accuracy while minimizing computational cost.

**Formal Objective:**
$$\max_{s(\cdot)} \mathbb{E}_{x \sim P_{test}}\left[\mathbb{1}[\hat{y}_{s(x)} = y] - \lambda \cdot C_{s(x)}\right]$$

where $\hat{y}_{s(x)}$ is the prediction using strategy $s(x)$, $y$ is the true label, $C_{s(x)}$ is the computational cost of strategy $s(x)$, and $\lambda$ is a cost-accuracy trade-off parameter.

### 2.2 EGAR Framework

#### 2.2.1 Entropy Computation

For each input sample $x$, we first obtain the predictive distribution from the foundation model:
$$p(y|x) = \text{softmax}(f_\theta(x))$$

The Shannon entropy of this distribution is computed as:
$$H(x) = -\sum_{k=1}^{K} p(y_k|x) \log p(y_k|x)$$

where $K$ is the number of classes. The entropy is bounded: $0 \leq H(x) \leq \log(K)$, with low values indicating confident predictions and high values indicating uncertainty.

#### 2.2.2 Routing Decision

The routing function $R: \mathbb{R}^+ \rightarrow \{ICL, LoRA\}$ is defined as:
$$R(x) = \begin{cases} ICL & \text{if } H(x) < \tau \\ LoRA & \text{if } H(x) \geq \tau \end{cases}$$

where $\tau$ is a threshold determined through calibration on a held-out validation set.

**Threshold Calibration:** We employ percentile-based calibration using a small validation set $\mathcal{D}_{val}$ from the target domain:
$$\tau = \text{Percentile}_q(\{H(x) : x \in \mathcal{D}_{val}\})$$

where $q$ is optimized to maximize validation accuracy. In practice, we find $q \in [40, 60]$ percentile works well across benchmarks.

#### 2.2.3 Adaptation Strategies

**ICL Strategy:** For samples routed to ICL, we construct a prompt with $k$ demonstration examples:
$$\hat{y}_{ICL} = \arg\max_y p(y|[D_1, D_2, ..., D_k, x])$$

where $D_i = (x_i, y_i)$ are demonstration pairs selected from the training set. For vision models like CLIP, we use text-based class descriptions as implicit demonstrations.

**LoRA Strategy:** For samples routed to LoRA, we use a pre-trained LoRA adapter with low-rank matrices $A \in \mathbb{R}^{r \times d}$ and $B \in \mathbb{R}^{d \times r}$:
$$W' = W + BA$$

where $W$ is the original weight matrix, $r$ is the rank (we use $r=8$), and the adapter is trained on task-specific data. The prediction is:
$$\hat{y}_{LoRA} = \arg\max_y p(y|x; \theta + \Delta\theta_{LoRA})$$

#### 2.2.4 Complete Algorithm

```
Algorithm 1: EGAR Inference
Input: Test sample x, foundation model f_θ, LoRA adapter Δθ, 
       ICL demonstrations D, threshold τ
Output: Prediction ŷ

1. Compute predictive distribution: p(y|x) = softmax(f_θ(x))
2. Compute entropy: H(x) = -Σ p(y_k|x) log p(y_k|x)
3. Route based on entropy:
   if H(x) < τ:
       ŷ = ICL_predict(x, D, f_θ)  // Preserve pretrained robustness
   else:
       ŷ = LoRA_predict(x, f_θ, Δθ)  // Apply deeper adaptation
4. Return ŷ
```

### 2.3 Experimental Design

#### 2.3.1 Datasets and Benchmarks

We evaluate EGAR on established distribution shift benchmarks:

**Vision Domain (CLIP ViT-B/16):**
- **ImageNet-C**: 15 corruption types at 5 severity levels (75 test conditions)
- **ImageNet-R**: Rendition shifts (art, cartoons, sketches) with 200 classes
- **ImageNet-Sketch**: Sketch renditions of ImageNet classes

**Language Domain (LLaMA-7B):**
- **WILDS-CivilComments**: Demographic distribution shifts in toxicity detection
- **WILDS-Amazon**: Temporal and reviewer distribution shifts in sentiment analysis

**Multimodal Domain (LLaVA-1.5):**
- **VQA-v2 with distribution shifts**: Question type and image domain variations

#### 2.3.2 Baselines

1. **ICL-only**: Uniform application of in-context learning
2. **LoRA-only**: Uniform application of LoRA adaptation
3. **DaWin**: Entropy-based continuous weight interpolation between two models
4. **Random Routing**: Random selection between ICL and LoRA (ablation)
5. **Oracle Routing**: Upper bound using ground-truth optimal strategy per sample

#### 2.3.3 Implementation Details

**CLIP Configuration:**
- Model: ViT-B/16 pretrained on LAION-400M
- LoRA: rank=8, α=16, applied to attention layers
- ICL: Zero-shot with class name prompts

**LLaMA Configuration:**
- Model: LLaMA-7B
- LoRA: rank=8, α=16, applied to query/value projections
- ICL: 4-shot demonstrations

**Training Protocol:**
- LoRA training: 3 epochs on ID training data, AdamW optimizer, lr=1e-4
- Threshold calibration: 500 validation samples, grid search over percentiles

#### 2.3.4 Evaluation Metrics

**Primary Metrics:**
1. **OOD Accuracy**: Top-1 accuracy on distribution-shifted test sets
2. **Robustness Gap**: $|Acc_{ID} - Acc_{OOD}|$
3. **Effective Robustness**: OOD accuracy relative to ID accuracy

**Efficiency Metrics:**
4. **Computational Cost**: Average FLOPs per sample
$$\text{Cost}_{EGAR} = p_{ICL} \cdot \text{FLOPs}_{ICL} + p_{LoRA} \cdot \text{FLOPs}_{LoRA}$$
5. **Routing Ratio**: Proportion of samples routed to each strategy

**Mechanism Validation Metrics:**
6. **Entropy-Strategy Correlation**: Spearman correlation between entropy and optimal strategy
7. **Per-Stratum Accuracy**: Accuracy within entropy quantiles

### 2.4 Statistical Analysis Plan

**Sample Size Justification:** Based on power analysis for paired t-test with Cohen's d=0.5, α=0.05, power=0.80, we require n≥25 independent measurements. We achieve this through 5 random seeds × 5+ benchmarks.

**Hypothesis Testing:**
- Primary comparison: Paired t-test between EGAR and best baseline
- Multiple comparison correction: Bonferroni adjustment (α_adjusted = 0.05/3 ≈ 0.017)
- Effect size reporting: Cohen's d with 95% confidence intervals

**Causal Mechanism Validation:**
- Ablation: Replace entropy with random values (tests necessity)
- Intervention: Swap routing decisions for entropy quantiles (tests sufficiency)
- Correlation analysis: Entropy vs. strategy-specific accuracy improvement

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcomes:**
1. **OOD Accuracy Improvement**: We expect EGAR to achieve >1.5% accuracy improvement over the best single-strategy baseline (ICL-only or LoRA-only) across benchmarks, with statistical significance (p<0.05).

2. **Computational Efficiency**: We anticipate >20% reduction in average FLOPs compared to uniform LoRA application, as a substantial portion of samples (estimated 40-60%) will be routed to the computationally cheaper ICL pathway.

3. **Robustness Gap Reduction**: EGAR should reduce the ID-OOD accuracy gap by 15-25% compared to LoRA-only, by preserving pretrained robustness for confident predictions.

**Mechanism Validation Outcomes:**
4. **Entropy-Strategy Correlation**: We expect Spearman correlation >0.3 between sample entropy and benefit from LoRA over ICL, validating the causal mechanism.

5. **Complementary Expertise**: Analysis should reveal distinct entropy regions where each strategy excels, confirming the complementary expertise assumption.

### 3.2 Potential Challenges and Mitigations

1. **Threshold Sensitivity**: If performance is highly sensitive to threshold choice, we will explore learned routing functions or soft routing with probability-weighted ensemble predictions.

2. **Domain-Specific Calibration**: If optimal thresholds vary significantly across domains, we will develop domain-adaptive calibration using minimal target domain samples.

3. **Extreme Distribution Shifts**: For shifts where both strategies fail, EGAR cannot improve; we will characterize the boundary conditions of applicability.

### 3.3 Broader Impact

**Scientific Contributions:**
- Establishes entropy as a principled criterion for adaptation strategy selection
- Provides empirical evidence for complementary expertise profiles of ICL and LoRA
- Advances theoretical understanding of foundation model robustness under distribution shift

**Practical Applications:**
- Enables efficient deployment of foundation models in resource-constrained environments
- Provides a framework for adaptive model serving in production systems
- Reduces computational costs and associated environmental impact of foundation model inference

**Future Directions:**
- Extension to multi-strategy routing (adding test-time adaptation as third option)
- Application to generative tasks and instruction-following scenarios
- Development of learned routing functions for continuous strategy interpolation

### 3.4 Limitations and Ethical Considerations

**Limitations:**
- Requires pre-trained LoRA adapter (one-time training cost)
- May require per-domain threshold calibration
- Assumes availability of ICL capability in the foundation model

**Ethical Considerations:**
- Routing decisions may exhibit demographic biases if entropy correlates with protected attributes
- We will analyze routing patterns across demographic subgroups to identify and mitigate potential fairness concerns
- Computational savings should be weighed against potential accuracy disparities across subpopulations

This research establishes EGAR as a principled framework for sample-adaptive foundation model deployment, contributing both theoretical insights and practical tools for robust machine learning under distribution shift.