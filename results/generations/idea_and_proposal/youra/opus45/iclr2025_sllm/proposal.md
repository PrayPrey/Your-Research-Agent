# Research Proposal: SAE-Guided Contextual Sparsity for Interpretable LLM Inference Acceleration

## 1. Title

**SAE-Guided Contextual Sparsity: Interpretable Acceleration of LLM Inference via Sparse Autoencoder Feature Importance**

---

## 2. Introduction

### 2.1 Background

Large Language Models (LLMs) have revolutionized natural language processing, demonstrating remarkable capabilities across diverse tasks including reasoning, code generation, and creative writing. However, their deployment faces significant challenges: inference costs scale with model size, energy consumption raises environmental concerns, and the opacity of decision-making processes limits trustworthy deployment in high-stakes applications. These challenges have spawned two largely independent research directions—efficiency optimization and interpretability research—that rarely intersect despite their complementary goals.

**Contextual sparsity** has emerged as a promising efficiency technique, exploiting the observation that only a subset of neurons activates meaningfully for any given input. Methods like DejaVu achieve 2× inference speedup by training lightweight predictors to identify and skip inactive neurons. ShadowLLM further improves accuracy by 15% through better predictor architectures that shadow LLM behavior. However, these approaches treat sparsity decisions as black-box predictions, offering no insight into *why* particular neurons are deemed important or expendable.

**Sparse Autoencoders (SAEs)** represent a parallel breakthrough in interpretability research. By decomposing neural activations into sparse, human-interpretable features, SAEs enable researchers to understand what concepts models represent internally. The Gemma Scope project provides pre-trained SAEs across the Gemma 2 model family, offering unprecedented access to interpretable feature decompositions. Recent work like FGAA demonstrates that SAE features can precisely steer model behavior through activation manipulation, suggesting these features capture semantically meaningful computation.

### 2.2 Research Gap and Motivation

Despite their complementary strengths, efficiency and interpretability research remain disconnected. Contextual sparsity methods achieve impressive speedups but provide no explanation for their decisions—a critical limitation for debugging, auditing, and trustworthy deployment. Meanwhile, SAEs offer rich interpretability but have not been leveraged for computational efficiency. This gap represents a missed opportunity: if SAE features encode semantic relevance, they may also encode *computational importance* for task performance.

We hypothesize that SAE features, trained for interpretability, capture task-relevance patterns that correlate with the computational importance of individual neurons. This correlation, if validated, would enable a novel approach: using SAE feature importance to guide contextual sparsity decisions, achieving both efficiency gains and interpretable explanations for which computations are skipped.

### 2.3 Research Objectives

This research pursues three interconnected objectives:

1. **Validate the SAE-Sparsity Correlation Hypothesis**: Establish whether SAE feature importance scores meaningfully correlate with contextual sparsity patterns, providing theoretical grounding for our approach.

2. **Develop SAE-Guided Contextual Sparsity**: Design and implement a method that uses pre-computed SAE feature importance as soft weights to bias sparsity predictor outputs, achieving sparse inference with interpretable decision traces.

3. **Demonstrate Practical Benefits**: Achieve ≥1.3× inference speedup with ≥98% accuracy retention while enabling ≥80% of sparsity decisions to be traced to human-interpretable SAE features.

### 2.4 Significance

This research bridges two critical but disconnected areas of LLM research, offering several contributions:

- **Theoretical**: Establishes a novel connection between interpretability features and computational importance, potentially revealing fundamental properties of neural network computation.
- **Practical**: Enables faster LLM inference with explainable sparsity decisions, critical for deployment in regulated domains requiring auditability.
- **Methodological**: Provides a framework for leveraging interpretability tools for efficiency optimization, opening new research directions at this intersection.

---

## 3. Methodology

### 3.1 Overview

Our methodology comprises four phases: (1) offline SAE feature importance computation, (2) SAE-weighted sparsity predictor design, (3) sparse inference implementation, and (4) comprehensive evaluation. We target the Gemma 2 model family (2B and 9B parameters) with Gemma Scope SAEs.

### 3.2 Phase 1: Offline SAE Feature Importance Computation

#### 3.2.1 SAE Feature Extraction

For each layer $l$ in the target LLM, we utilize pre-trained Gemma Scope SAEs that decompose MLP activations into sparse feature representations. Given an input activation $\mathbf{h}_l \in \mathbb{R}^{d}$, the SAE encoder produces:

$$\mathbf{f}_l = \text{JumpReLU}(\mathbf{W}_{\text{enc}} \mathbf{h}_l + \mathbf{b}_{\text{enc}})$$

where $\mathbf{f}_l \in \mathbb{R}^{k}$ represents the sparse feature activations ($k \gg d$, typically 16× expansion), and JumpReLU enforces sparsity through a learned threshold.

#### 3.2.2 Gradient-Weighted Importance Scoring

We compute feature importance using gradient-weighted activation analysis on a calibration dataset $\mathcal{D}_{\text{cal}}$ (C4 subset, 1000 samples). For each SAE feature $i$ at layer $l$, the importance score is:

$$I_{l,i} = \mathbb{E}_{x \sim \mathcal{D}_{\text{cal}}} \left[ \left| f_{l,i}(x) \cdot \frac{\partial \mathcal{L}(x)}{\partial f_{l,i}(x)} \right| \right]$$

where $\mathcal{L}(x)$ is the language modeling loss. This gradient-weighted formulation captures both feature activation magnitude and downstream task relevance.

#### 3.2.3 Neuron-Level Importance Mapping

SAE features map to MLP neurons through the decoder weights. We compute neuron importance by aggregating feature importance weighted by decoder contributions:

$$N_{l,j} = \sum_{i=1}^{k} I_{l,i} \cdot |W_{\text{dec}}[i,j]|$$

where $N_{l,j}$ is the importance score for neuron $j$ at layer $l$, and $W_{\text{dec}}[i,j]$ is the decoder weight connecting feature $i$ to neuron $j$. Scores are normalized to $[0, 1]$ per layer.

### 3.3 Phase 2: SAE-Weighted Sparsity Predictor

#### 3.3.1 Baseline Sparsity Predictor

We adopt the ShadowLLM architecture as our baseline predictor. For each layer $l$, a lightweight MLP predicts neuron activation patterns:

$$\mathbf{p}_l = \sigma(\mathbf{W}_2 \cdot \text{ReLU}(\mathbf{W}_1 \cdot \mathbf{h}_{l-1}))$$

where $\mathbf{p}_l \in [0,1]^{d_{\text{mlp}}}$ represents predicted activation probabilities for each MLP neuron.

#### 3.3.2 SAE-Weighted Prediction

We introduce SAE importance as soft weights that bias predictor outputs before thresholding:

$$\mathbf{p}_l^{\text{weighted}} = \mathbf{p}_l \odot (\alpha \cdot \mathbf{N}_l + (1-\alpha))$$

where $\mathbf{N}_l$ is the pre-computed neuron importance vector, $\odot$ denotes element-wise multiplication, and $\alpha \in [0,1]$ is a tunable weighting coefficient. This formulation:
- Preserves predictor outputs when $\alpha = 0$ (baseline behavior)
- Fully relies on SAE importance when $\alpha = 1$
- Allows smooth interpolation for optimal trade-offs

#### 3.3.3 Adaptive Thresholding

Sparsity decisions are made via adaptive thresholding:

$$\mathbf{m}_l = \mathbb{1}[\mathbf{p}_l^{\text{weighted}} > \tau_l]$$

where $\tau_l$ is calibrated per-layer to achieve target sparsity ratio $s$ (e.g., 40% neurons skipped). The mask $\mathbf{m}_l$ determines which neurons execute.

### 3.4 Phase 3: Sparse Inference Implementation

#### 3.4.1 Sparse MLP Execution

During inference, we execute only selected neurons:

$$\mathbf{y}_l = \mathbf{W}_{\text{down}}[:, \mathbf{m}_l] \cdot \text{SiLU}(\mathbf{W}_{\text{gate}}[\mathbf{m}_l, :] \cdot \mathbf{x}) \odot (\mathbf{W}_{\text{up}}[\mathbf{m}_l, :] \cdot \mathbf{x})$$

This reduces computation proportionally to sparsity ratio while maintaining output dimensionality.

#### 3.4.2 Interpretability Trace Generation

For each sparsity decision, we generate an interpretability trace by identifying the top-$k$ SAE features contributing to each pruned neuron:

$$\text{Trace}(j) = \text{TopK}_{i}\left( I_{l,i} \cdot |W_{\text{dec}}[i,j]| \right)$$

This enables post-hoc explanation: "Neuron $j$ was pruned because SAE features $\{f_1, f_2, ...\}$ (representing concepts X, Y, Z) had low importance for this input."

### 3.5 Phase 4: Experimental Design

#### 3.5.1 Models and Datasets

**Models:**
- Gemma 2 2B (development and ablation studies)
- Gemma 2 9B (primary evaluation)

**Evaluation Benchmarks:**
- MMLU (5-shot): Measures knowledge and reasoning across 57 subjects
- HellaSwag (0-shot): Measures commonsense reasoning
- GSM8K (8-shot): Measures mathematical reasoning
- HumanEval (0-shot): Measures code generation

**Calibration Data:**
- C4 subset (1000 samples) for importance computation
- Held-out C4 (500 samples) for correlation analysis

#### 3.5.2 Baselines

| Method | Description |
|--------|-------------|
| Dense Baseline | Full model inference without sparsity |
| DejaVu | Original contextual sparsity predictor |
| ShadowLLM | State-of-the-art sparsity predictor |
| Random Sparsity | Random neuron selection at matched sparsity ratio |
| Magnitude Pruning | Static pruning based on weight magnitude |

#### 3.5.3 Evaluation Metrics

**Efficiency Metrics:**
- **Speedup Ratio**: $\text{Speedup} = \frac{T_{\text{dense}}}{T_{\text{sparse}}}$ (wall-clock latency)
- **Sparsity Ratio**: Percentage of neurons skipped per forward pass
- **FLOPs Reduction**: Theoretical computation savings

**Accuracy Metrics:**
- **Accuracy Retention**: $\frac{\text{Acc}_{\text{sparse}}}{\text{Acc}_{\text{dense}}} \times 100\%$
- **Absolute Accuracy**: Raw benchmark scores

**Interpretability Metrics:**
- **Traceability**: Percentage of decisions traceable to ≤5 SAE features
- **Feature Coherence**: Human evaluation of trace meaningfulness (n=100 samples)

**Correlation Metrics:**
- **Pearson Correlation**: Between SAE importance and sparsity decisions
- **Spearman Rank Correlation**: For robustness to outliers

#### 3.5.4 Experimental Protocol

**Experiment 1: Correlation Validation (SH1)**
- Compute SAE importance scores on calibration set
- Extract DejaVu/ShadowLLM sparsity decisions on held-out set
- Measure Pearson correlation per layer
- Success criterion: $r > 0.3$, $p < 0.01$

**Experiment 2: Accuracy-Speedup Trade-off (SH3)**
- Sweep $\alpha \in \{0, 0.25, 0.5, 0.75, 1.0\}$
- Sweep sparsity ratio $s \in \{0.3, 0.4, 0.5, 0.6\}$
- Measure accuracy and speedup for each configuration
- Report Pareto frontier

**Experiment 3: Ablation Studies (SH2)**
- Ablate SAE weighting (compare weighted vs. unweighted)
- Ablate importance computation (gradient-weighted vs. activation-only)
- Ablate feature aggregation (decoder-weighted vs. uniform)

**Experiment 4: Interpretability Evaluation**
- Generate traces for 100 random sparsity decisions
- Human annotators rate trace coherence (1-5 scale)
- Measure percentage meeting traceability criterion

#### 3.5.5 Statistical Analysis

- **Sample Size**: n ≥ 20 runs per configuration (different random seeds)
- **Statistical Tests**: Paired t-test for comparisons, α = 0.05
- **Effect Size**: Report Cohen's d for practical significance
- **Confidence Intervals**: 95% CI for all primary metrics

### 3.6 Implementation Details

**Hardware**: NVIDIA A100 80GB GPUs
**Software**: PyTorch 2.0+, HuggingFace Transformers, custom sparse kernels
**Offline Computation**: Estimated 4-8 GPU-hours per model for importance scores
**Inference Overhead**: Importance lookup adds <1ms latency (pre-loaded in GPU memory)

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

**Primary Outcomes:**

1. **Correlation Validation**: We expect to observe Pearson correlation $r > 0.3$ between SAE feature importance and contextual sparsity patterns, validating our core hypothesis that interpretability features encode computational importance.

2. **Efficiency Gains**: We anticipate achieving ≥1.3× inference speedup at 40% sparsity with ≥98% accuracy retention on MMLU and HellaSwag benchmarks. This would demonstrate that SAE-guided sparsity matches or exceeds existing methods while adding interpretability.

3. **Interpretability Benefits**: We expect ≥80% of sparsity decisions to be traceable to ≤5 human-interpretable SAE features, enabling novel debugging and auditing capabilities.

**Secondary Outcomes:**

- Identification of optimal weighting coefficient $\alpha$ for different accuracy-speedup trade-offs
- Layer-wise analysis revealing which layers benefit most from SAE guidance
- Characterization of failure modes where SAE guidance degrades performance

### 4.2 Potential Challenges and Mitigations

| Challenge | Mitigation Strategy |
|-----------|---------------------|
| Weak SAE-sparsity correlation | Explore alternative importance formulations; accept graceful degradation |
| Importance computation overhead | Amortize across inference; cache per-layer scores |
| SAE quality limitations | Focus on layers with high-quality SAE coverage |
| Interpretability subjectivity | Develop standardized evaluation protocol with multiple annotators |

### 4.3 Broader Impact

**Scientific Impact:**
This research establishes a novel theoretical connection between interpretability and efficiency, suggesting that understanding *what* models compute may inform *how* to compute efficiently. This could inspire new research directions exploring interpretability-guided optimization across machine learning.

**Practical Impact:**
Interpretable sparsity decisions enable:
- **Debugging**: Identify why specific inputs cause performance degradation
- **Auditing**: Verify that sparsity decisions align with intended behavior
- **Trust**: Provide explanations for deployment in regulated domains (healthcare, finance, legal)

**Environmental Impact:**
Achieving 1.3× speedup translates directly to reduced energy consumption and carbon emissions for LLM inference, contributing to sustainable AI deployment.

### 4.4 Limitations and Future Work

**Limitations:**
- Requires pre-trained SAEs (currently available only for Gemma family)
- Offline importance computation adds one-time setup cost
- Interpretability benefits require human evaluation infrastructure

**Future Directions:**
- Extend to attention sparsity using attention-head SAEs
- Develop online importance adaptation for distribution shift
- Explore SAE-guided quantization for complementary efficiency gains
- Scale to larger models (70B+) with distributed inference

### 4.5 Falsification Criteria

The hypothesis will be **rejected** if:
1. Accuracy drops below 95% of dense baseline at any sparsity level
2. Speedup fails to exceed 1.1× (indicating overhead negates benefits)
3. SAE-sparsity correlation is negligible ($r < 0.1$, $p > 0.05$)

These clear falsification criteria ensure scientific rigor and prevent confirmation bias.

### 4.6 Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Importance Computation | 2 weeks | Pre-computed importance scores for Gemma 2 2B/9B |
| Phase 2: Predictor Implementation | 3 weeks | SAE-weighted sparsity predictor codebase |
| Phase 3: Correlation Validation | 2 weeks | Correlation analysis results (SH1) |
| Phase 4: Main Experiments | 4 weeks | Accuracy-speedup results, ablations (SH2, SH3) |
| Phase 5: Interpretability Evaluation | 2 weeks | Human evaluation results |
| Phase 6: Paper Writing | 3 weeks | Workshop submission |

**Total Duration**: 16 weeks

---

## Conclusion

This proposal presents SAE-Guided Contextual Sparsity, a novel approach that bridges LLM efficiency and interpretability research. By leveraging pre-trained Sparse Autoencoder features to guide sparsity decisions, we aim to achieve faster inference with explainable computation patterns. Our rigorous experimental design, clear falsification criteria, and comprehensive evaluation metrics ensure scientific validity while addressing practical deployment needs. Success would establish a new paradigm for interpretability-guided efficiency optimization, with implications extending beyond LLM inference to broader machine learning systems.