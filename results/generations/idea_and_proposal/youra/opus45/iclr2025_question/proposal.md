# Research Proposal: Position-Adaptive Conformal Prediction for Uncertainty Quantification in Constrained Language Model Generation

## 1. Title

**Position-Adaptive Conformal Prediction with Entropy-Weighted Nonconformity Scores for Reliable Uncertainty Quantification in Constrained Language Model Generation**

---

## 2. Introduction

### 2.1 Background

Large language models (LLMs) have achieved remarkable performance across diverse natural language processing tasks, from question answering and code generation to entity extraction and summarization. However, a critical limitation undermines their deployment in high-stakes domains: LLMs generate outputs with apparent confidence regardless of their actual reliability, frequently producing hallucinations—plausible-sounding but factually incorrect or unsupported content. In healthcare, legal, and autonomous systems applications, such unreliable outputs can lead to catastrophic consequences, making uncertainty quantification (UQ) an essential capability for trustworthy AI deployment.

Existing approaches to LLM uncertainty quantification fall into two broad categories. First, sampling-based methods generate multiple outputs and measure consistency, but lack formal statistical guarantees and incur substantial computational overhead. Second, conformal prediction (CP) methods provide distribution-free coverage guarantees but face a fundamental challenge when applied to autoregressive generation: the standard exchangeability assumption required for valid CP is violated because token distributions depend heavily on their position within the sequence. Early tokens establish context that constrains later tokens, creating position-dependent uncertainty characteristics that invalidate naive application of conformal methods.

Recent advances in conformal prediction for language models, including ConU and ResCP frameworks, have demonstrated promising results. However, these methods either ignore position-dependent structure entirely or require computationally expensive resampling procedures. A critical gap remains: how to achieve rigorous coverage guarantees while producing practically useful (small) prediction sets with reasonable computational overhead.

### 2.2 Research Objectives

This research proposes **Position-Adaptive Conformal Prediction with Entropy-Weighted Nonconformity Scores (PACPA)**, a novel framework that addresses the exchangeability violation in autoregressive generation through position stratification while leveraging entropy-based weighting to improve prediction set efficiency. Our specific objectives are:

1. **Develop a theoretically grounded position stratification scheme** that groups tokens with similar autoregressive dynamics, restoring approximate exchangeability within strata to enable valid conformal prediction.

2. **Design entropy-weighted nonconformity scores** that leverage the informativeness of LLM logit distributions to focus conformity assessment on uncertain positions, reducing prediction set sizes while maintaining coverage guarantees.

3. **Empirically validate PACPA** on constrained generation tasks (extractive QA, code completion, entity extraction) demonstrating ≥90% coverage with 20-50% smaller prediction sets than baselines and ≤30% computational overhead.

4. **Establish falsification criteria** to rigorously test the hypothesis that position adaptation provides meaningful improvements over position-agnostic approaches.

### 2.3 Significance

This research addresses multiple critical challenges identified in the workshop call:

- **Scalable and computationally efficient UQ methods**: PACPA achieves efficiency through position stratification rather than expensive ensemble sampling.
- **Theoretical foundations for generative model uncertainty**: We provide formal analysis connecting position stratification to approximate exchangeability and valid coverage.
- **Hallucination detection and mitigation**: Prediction sets that exclude hallucinated content provide a principled mechanism for identifying unreliable outputs.
- **Practical benchmarks**: We establish evaluation protocols across three constrained generation domains with clear success criteria.

By bridging the gap between theoretical conformal prediction guarantees and practical LLM deployment, this research enables safer, more reliable use of foundation models in high-stakes applications.

---

## 3. Methodology

### 3.1 Problem Formulation

Consider an autoregressive language model $\mathcal{M}$ that generates a sequence of tokens $\mathbf{y} = (y_1, y_2, \ldots, y_T)$ given input $\mathbf{x}$. At each position $t$, the model produces a probability distribution over the vocabulary $\mathcal{V}$:

$$P(y_t | \mathbf{x}, y_{1:t-1}) = \text{softmax}(\mathbf{z}_t)$$

where $\mathbf{z}_t \in \mathbb{R}^{|\mathcal{V}|}$ denotes the logit vector at position $t$.

Our goal is to construct prediction sets $\mathcal{C}(\mathbf{x})$ that satisfy the marginal coverage guarantee:

$$P(y^* \in \mathcal{C}(\mathbf{x})) \geq 1 - \alpha$$

where $y^*$ is the ground truth output and $\alpha$ is the user-specified miscoverage rate (typically 0.1).

### 3.2 Position-Adaptive Conformal Prediction Framework

#### 3.2.1 Position Stratification

The key insight of PACPA is that tokens at similar sequence positions share uncertainty characteristics due to the autoregressive generation process. We partition positions into $K$ strata $\{S_1, S_2, \ldots, S_K\}$ based on position indices and entropy profiles.

**Adaptive Stratification Scheme:**
For a sequence of length $T$, we define strata boundaries using entropy-based clustering:

1. Compute position-averaged entropy across calibration set:
$$\bar{H}(t) = \frac{1}{|D_{cal}|} \sum_{(\mathbf{x}, \mathbf{y}) \in D_{cal}} H(P(y_t | \mathbf{x}, y_{1:t-1}))$$

where $H(\cdot)$ denotes Shannon entropy.

2. Apply $K$-means clustering on $\{\bar{H}(t)\}_{t=1}^{T}$ to obtain position strata.

3. Assign each position $t$ to stratum $S_k$ based on cluster membership.

This adaptive scheme groups positions with similar uncertainty profiles, enabling approximate exchangeability within each stratum.

#### 3.2.2 Entropy-Weighted Nonconformity Scores

We define a novel nonconformity score that weights token-level conformity by entropy, focusing assessment on informative (uncertain) positions:

**Token-Level Nonconformity:**
For token $y_t$ at position $t$, the base nonconformity score is:

$$s_t(y_t) = 1 - P(y_t | \mathbf{x}, y_{1:t-1})$$

**Entropy Weight:**
The entropy weight for position $t$ is:

$$w_t = \frac{H(P(y_t | \mathbf{x}, y_{1:t-1}))}{\sum_{j=1}^{T} H(P(y_j | \mathbf{x}, y_{1:j-1}))}$$

**Sequence-Level Entropy-Weighted Score:**
The overall nonconformity score for sequence $\mathbf{y}$ is:

$$S(\mathbf{x}, \mathbf{y}) = \sum_{t=1}^{T} w_t \cdot s_t(y_t)$$

This formulation ensures that positions with high entropy (where the model is uncertain) contribute more to the conformity assessment, while confident positions have reduced influence.

#### 3.2.3 Position-Stratified Calibration

Given a calibration set $D_{cal} = \{(\mathbf{x}_i, \mathbf{y}_i)\}_{i=1}^{n}$, we compute stratum-specific quantiles:

1. **Compute nonconformity scores** for all calibration examples:
$$s_i = S(\mathbf{x}_i, \mathbf{y}_i), \quad i = 1, \ldots, n$$

2. **Stratify scores** by dominant position stratum:
$$D_{cal}^{(k)} = \{s_i : \text{argmax}_j \sum_{t \in S_j} w_t^{(i)} = k\}$$

3. **Compute stratum-specific thresholds:**
$$\hat{q}_k = \text{Quantile}_{1-\alpha}\left(D_{cal}^{(k)} \cup \{\infty\}\right)$$

The addition of $\{\infty\}$ ensures finite-sample validity following standard CP practice.

#### 3.2.4 Prediction Set Construction

At test time, for input $\mathbf{x}_{test}$:

1. **Generate candidate set** $\mathcal{Y}_{cand}$ via beam search or nucleus sampling.

2. **Compute nonconformity scores** for each candidate:
$$s(\mathbf{y}) = S(\mathbf{x}_{test}, \mathbf{y}), \quad \forall \mathbf{y} \in \mathcal{Y}_{cand}$$

3. **Determine dominant stratum** for each candidate based on entropy weights.

4. **Construct prediction set:**
$$\mathcal{C}(\mathbf{x}_{test}) = \{\mathbf{y} \in \mathcal{Y}_{cand} : s(\mathbf{y}) \leq \hat{q}_{k(\mathbf{y})}\}$$

where $k(\mathbf{y})$ is the dominant stratum for candidate $\mathbf{y}$.

### 3.3 Theoretical Analysis

**Proposition 1 (Approximate Coverage):** Under the assumption that tokens within each stratum $S_k$ are approximately exchangeable with bounded total variation distance $\epsilon_k$ from exact exchangeability, PACPA achieves:

$$P(y^* \in \mathcal{C}(\mathbf{x})) \geq 1 - \alpha - \sum_{k=1}^{K} \pi_k \epsilon_k$$

where $\pi_k$ is the probability mass of stratum $k$.

**Proposition 2 (Set Size Reduction):** When entropy weights concentrate on a subset of positions with high uncertainty, the effective calibration sample size increases within those positions, leading to tighter quantile estimates and smaller prediction sets compared to uniform weighting.

### 3.4 Experimental Design

#### 3.4.1 Datasets and Tasks

We evaluate PACPA on three constrained generation benchmarks:

| Task | Dataset | Metric | Ground Truth |
|------|---------|--------|--------------|
| Extractive QA | SQuAD 2.0 | Exact Match, F1 | Annotated spans |
| Code Completion | HumanEval | pass@k | Unit tests |
| Entity Extraction | CoNLL-2003 NER | Entity F1 | Annotated entities |

**Data Splits:**
- Calibration: 2,500 examples (500 per stratum × 5 strata)
- Test: 500+ examples per task
- Validation: 500 examples for hyperparameter tuning

#### 3.4.2 Models

We evaluate across model scales to assess generalizability:
- **Small**: LLaMA-2-7B, CodeLLaMA-7B
- **Medium**: LLaMA-2-13B
- **Large**: LLaMA-2-70B (grey-box access via API)

#### 3.4.3 Baselines

1. **Sampling-Based Ensemble**: Generate 20 samples, measure consistency
2. **Position-Agnostic CP**: Standard conformal prediction without stratification
3. **ConU**: Self-consistency based conformal prediction (EMNLP 2024)
4. **ResCP**: Residual conformal prediction with reweighting

#### 3.4.4 Evaluation Metrics

**Primary Metrics:**
- **Coverage Rate**: $\frac{1}{n}\sum_{i=1}^{n} \mathbb{1}[y_i^* \in \mathcal{C}(\mathbf{x}_i)]$
- **Average Set Size**: $\frac{1}{n}\sum_{i=1}^{n} |\mathcal{C}(\mathbf{x}_i)|$
- **Computational Overhead**: Additional inference time relative to standard generation

**Secondary Metrics:**
- **Conditional Coverage**: Coverage stratified by difficulty/entropy
- **Set Size Variance**: Stability of prediction set sizes
- **Calibration Error**: Deviation from target coverage across subgroups

#### 3.4.5 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

| Ablation | Component Removed | Tests Hypothesis |
|----------|-------------------|------------------|
| A1 | Position stratification | H-M1: Stratification → Exchangeability |
| A2 | Entropy weighting | H-M3: Entropy → Smaller sets |
| A3 | Adaptive strata boundaries | Optimal stratification scheme |
| A4 | Stratum-specific thresholds | Per-stratum calibration value |

#### 3.4.6 Statistical Analysis

**Sample Size Justification:**
With $n = 500$ test instances, we achieve 80% power to detect coverage differences of 5% at $\alpha = 0.05$.

**Hypothesis Tests:**
- **P1 (Coverage)**: One-sample proportion test, $H_0: \text{coverage} < 0.90$
- **P2 (Set Size)**: Paired t-test comparing PACPA vs. baselines
- **P3 (Overhead)**: Descriptive statistics with 95% confidence intervals

**Falsification Criteria:**
1. Coverage < 85% → Reject primary hypothesis
2. Set size reduction < 10% → Reject mechanism hypothesis
3. Overhead > 50% → Reject efficiency hypothesis

### 3.5 Implementation Details

**Hyperparameters:**
- Number of strata $K \in \{3, 5, 7, 10\}$ (tuned on validation)
- Candidate set size: 50 (beam search) or 100 (nucleus sampling)
- Miscoverage rate $\alpha = 0.1$

**Computational Requirements:**
- GPU: 4× A100 80GB for LLaMA-70B experiments
- Estimated runtime: 48 hours for full experimental suite

**Code and Reproducibility:**
All code, trained models, and evaluation scripts will be released under MIT license with detailed documentation for reproducibility.

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Results

Based on our theoretical analysis and preliminary experiments, we anticipate the following outcomes:

**Primary Outcome (P1 - Coverage):**
PACPA will achieve ≥90% coverage (target: 92-95%) across all three constrained generation tasks at $\alpha = 0.1$. The position stratification mechanism will restore sufficient exchangeability to maintain valid coverage guarantees, with coverage rates stable across different model scales.

**Secondary Outcome (P2 - Set Efficiency):**
Prediction sets will be 20-50% smaller than position-agnostic CP baselines and 30-60% smaller than sampling-based ensembles at equivalent coverage levels. The entropy-weighted scoring mechanism will concentrate conformity assessment on informative positions, enabling tighter prediction sets without sacrificing coverage.

**Tertiary Outcome (P3 - Computational Efficiency):**
PACPA will incur ≤30% computational overhead compared to standard generation, significantly lower than the 10-20× overhead of sampling-based ensemble methods. The efficiency gain comes from avoiding multiple forward passes while leveraging single-pass logit information.

### 4.2 Scientific Contributions

1. **Theoretical Contribution**: We establish formal connections between position stratification and approximate exchangeability in autoregressive generation, extending conformal prediction theory to sequential models.

2. **Methodological Contribution**: The entropy-weighted nonconformity score provides a principled mechanism for leveraging LLM logit informativeness, applicable beyond the specific PACPA framework.

3. **Empirical Contribution**: Comprehensive evaluation across three domains with rigorous falsification criteria establishes new benchmarks for LLM uncertainty quantification.

### 4.3 Practical Impact

**Safer LLM Deployment:**
PACPA enables practitioners to deploy LLMs with formal reliability guarantees in high-stakes domains. When prediction sets are large, users receive clear signals that human oversight is needed; when sets are small, users can trust model outputs with quantified confidence.

**Hallucination Detection:**
Prediction sets that exclude hallucinated content provide a principled mechanism for identifying unreliable outputs without requiring external knowledge bases or fact-checking systems.

**Decision Support:**
In clinical, legal, and autonomous systems applications, PACPA prediction sets can guide risk-aware decision-making by quantifying the range of plausible model outputs.

### 4.4 Limitations and Future Work

**Current Limitations:**
- Requires grey-box or white-box LLM access (logits)
- Validated only on constrained generation tasks
- Assumes well-defined ground truth exists

**Future Directions:**
1. Extension to open-ended generation through hierarchical prediction sets
2. Black-box adaptation using output probability estimation
3. Multimodal extension for vision-language models
4. Online calibration for distribution shift adaptation

### 4.5 Broader Impact

This research contributes to the broader goal of trustworthy AI by providing rigorous uncertainty quantification for foundation models. As LLMs become increasingly integrated into critical infrastructure, methods like PACPA that combine theoretical guarantees with practical efficiency will be essential for responsible deployment. By establishing clear falsification criteria and open-sourcing our implementation, we also contribute to reproducible research practices in the uncertainty quantification community.

---

**Word Count:** ~2,100 words