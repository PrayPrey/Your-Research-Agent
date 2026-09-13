# Research Proposal: Adaptive Conformal Prediction with Sequential Change-Point Detection for Robust LLM Deployment

## 1. Title

Adaptive Conformal Prediction with Sequential Change-Point Detection for Distribution Shift Monitoring and Risk Management in Large Language Model Deployments

## 2. Introduction

### 2.1 Background

Large Language Models (LLMs) and foundation models have become integral components of production systems across industries, from customer service chatbots to medical diagnosis assistants. However, these deployments face a critical challenge: the operational environment is non-stationary. User query distributions evolve, adversarial inputs emerge, and the relationship between inputs and desired outputs shifts over time. Traditional statistical frameworks assume exchangeability—that training and test data are drawn from the same distribution—an assumption that is routinely violated in real-world LLM deployments.

Conformal prediction has emerged as a promising framework for uncertainty quantification in machine learning, providing distribution-free, finite-sample valid prediction sets without requiring distributional assumptions about the model. However, standard conformal prediction critically depends on the exchangeability assumption. When distribution shifts occur, conformal guarantees break down, potentially leading to overconfident predictions and hidden operational risks. Recent work has begun addressing distribution shift in conformal prediction through worst-case robust approaches or importance weighting, but these methods often produce overly conservative prediction sets or require explicit knowledge of the shift structure.

Simultaneously, the field of sequential change-point detection has developed sophisticated statistical tools for monitoring stochastic processes and detecting distributional changes. Methods such as CUSUM (Cumulative Sum Control Chart) and EWMA (Exponentially Weighted Moving Average) provide principled approaches to anomaly detection with theoretical guarantees on false alarm rates and detection delays. However, these techniques have rarely been integrated with modern uncertainty quantification frameworks for black-box models.

### 2.2 Research Objectives

This research proposes a novel framework that bridges conformal prediction and sequential change-point detection to address the critical need for robust, adaptive uncertainty quantification in LLM deployments. The primary objectives are:

1. **Develop an integrated framework** that combines conformal prediction with sequential statistical monitoring to provide both calibrated uncertainty sets and real-time distribution shift detection.

2. **Design computationally efficient conformity scores** specifically tailored to LLM outputs, leveraging model logits, embedding representations, and semantic similarity metrics.

3. **Establish theoretical guarantees** on coverage validity, false alarm rates, and detection delays under various distribution shift scenarios.

4. **Create adaptive recalibration protocols** that maintain valid uncertainty quantification when shifts are detected, using minimal human feedback.

5. **Validate the framework empirically** on diverse LLM tasks including text generation, question answering, and code generation under realistic distribution shift scenarios.

### 2.3 Significance

This research addresses several critical gaps at the intersection of statistical foundations and LLM deployment:

- **Proactive Risk Management**: Current LLM deployment practices are largely reactive, identifying failures only after they occur. This framework enables proactive monitoring, alerting operators before performance degrades critically.

- **Auditing and Safety**: Regulators and stakeholders increasingly demand auditable AI systems. Our approach provides statistical evidence of when model reliability changes, supporting compliance and accountability.

- **Resource Optimization**: By automatically detecting when recalibration is needed, organizations can efficiently allocate human annotation resources only when necessary, rather than continuous expensive monitoring.

- **Theoretical Foundations**: This work contributes to the theoretical understanding of uncertainty quantification under non-stationarity, extending conformal prediction theory to sequential settings.

## 3. Methodology

### 3.1 Framework Overview

Our framework, **Adaptive Conformal Prediction with Change-Point Detection (ACP-CPD)**, operates in three integrated stages: (1) conformity score computation, (2) sequential monitoring, and (3) adaptive recalibration.

### 3.2 Conformal Prediction Foundation

#### 3.2.1 Standard Conformal Prediction

Let $(X_1, Y_1), \ldots, (X_n, Y_n)$ be calibration data, where $X_i$ represents inputs (e.g., prompts) and $Y_i$ represents outputs (e.g., responses or labels). For a new input $X_{n+1}$, standard conformal prediction constructs a prediction set $C(X_{n+1})$ such that:

$$P(Y_{n+1} \in C(X_{n+1})) \geq 1 - \alpha$$

for a chosen miscoverage rate $\alpha \in (0,1)$, under the exchangeability assumption.

This is achieved through a conformity score function $s: \mathcal{X} \times \mathcal{Y} \rightarrow \mathbb{R}$ that measures how "conforming" a candidate output is with respect to the model. For classification, a common choice is:

$$s(x, y) = 1 - \hat{\pi}_{\theta}(y|x)$$

where $\hat{\pi}_{\theta}(y|x)$ is the model's predicted probability for class $y$.

The $(1-\alpha)$-quantile of calibration scores $\hat{q} = \text{Quantile}_{1-\alpha}(\{s(X_i, Y_i)\}_{i=1}^n)$ defines the prediction set:

$$C(X_{n+1}) = \{y : s(X_{n+1}, y) \leq \hat{q}\}$$

#### 3.2.2 LLM-Specific Conformity Scores

For LLM outputs, we propose multiple conformity score variants:

**Token-level scores** for generation tasks:
$$s_{\text{token}}(x, y) = -\frac{1}{|y|}\sum_{t=1}^{|y|} \log \hat{\pi}_{\theta}(y_t | x, y_{<t})$$

**Embedding-based scores** using semantic similarity:
$$s_{\text{embed}}(x, y) = 1 - \cos(h_{\theta}(x, y), h_{\text{ref}}(x))$$

where $h_{\theta}(x, y)$ is the contextualized embedding and $h_{\text{ref}}(x)$ is a reference embedding from calibration data.

**Ensemble-based scores** for uncertainty:
$$s_{\text{ensemble}}(x, y) = \text{Var}(\{\hat{\pi}_{\theta_k}(y|x)\}_{k=1}^K)$$

where $\{\theta_k\}$ represents different model checkpoints or prompt variations.

### 3.3 Sequential Change-Point Detection

#### 3.3.1 Sliding Window Conformity Score Monitoring

In deployment, we maintain a sliding window of conformity scores from recent predictions: $W_t = \{s_{t-w+1}, \ldots, s_t\}$ where $w$ is the window size and $s_t$ represents the conformity score at time $t$.

We monitor the distributional properties of this window using statistical process control methods. Under exchangeability, conformity scores follow a uniform distribution on $[0,1]$ after probability integral transformation:

$$u_i = F_s(s_i)$$

where $F_s$ is the cumulative distribution function of the conformity scores.

#### 3.3.2 CUSUM-Based Detection

We employ a CUSUM statistic to detect shifts in the mean conformity score:

$$C_t = \max(0, C_{t-1} + (s_t - \mu_0) - k)$$

where $\mu_0$ is the expected score under null distribution, and $k$ is a slack parameter (typically $k = \delta/2$ for detecting shift of magnitude $\delta$).

An alarm is triggered when $C_t > h$, where the threshold $h$ is chosen to control the Average Run Length (ARL) under no change. For a target false alarm rate $\beta$, we set:

$$h = -\log(\beta) \cdot \sigma_0 / \delta$$

where $\sigma_0$ is the score standard deviation under the null.

#### 3.3.3 Entropy-Based Detection

For LLMs, we additionally monitor the entropy of conformity score distributions:

$$H_t = -\sum_{i \in W_t} u_i \log u_i$$

A decrease in entropy indicates concentration of scores (potential overconfidence), while an increase suggests heightened uncertainty. We use an EWMA control chart:

$$Z_t = \lambda H_t + (1-\lambda) Z_{t-1}$$

with detection threshold based on:

$$|Z_t - \mu_H| > L\sigma_H$$

where $L$ is chosen for desired false alarm rate and $\mu_H, \sigma_H$ are estimated from calibration.

### 3.4 Adaptive Recalibration Protocol

#### 3.4.1 Active Sample Selection

Upon detecting a shift at time $\tau$, we activate a recalibration protocol. To minimize annotation burden, we employ uncertainty-based sample selection. We request labels for the $m$ samples with highest conformity scores (most non-conforming):

$$\mathcal{S}_{\text{recal}} = \text{TopK}(\{s_t\}_{t=\tau-w'}^{\tau}, m)$$

where $w'$ is a recalibration window size and $m$ is the annotation budget.

#### 3.4.2 Weighted Conformal Recalibration

To handle gradual shifts, we use importance-weighted conformal prediction. We estimate the likelihood ratio between post-shift and pre-shift distributions using the conformity scores:

$$\hat{w}_t = \frac{\hat{p}_{\text{post}}(s_t)}{\hat{p}_{\text{pre}}(s_t)}$$

The recalibrated quantile becomes:

$$\hat{q}_{\text{new}} = \inf\left\{q : \frac{\sum_{i=1}^n \hat{w}_i \mathbb{1}(s_i \leq q)}{\sum_{i=1}^n \hat{w}_i} \geq 1-\alpha\right\}$$

#### 3.4.3 Multi-Resolution Monitoring

To capture shifts at different timescales, we maintain multiple monitoring streams with different window sizes $\{w_1, w_2, \ldots, w_k\}$ where $w_1 < w_2 < \cdots < w_k$. This enables detection of both abrupt and gradual shifts, with aggregated detection using:

$$D_t = \max_{j=1}^k \phi_j(W_t^{(j)})$$

where $\phi_j$ is the test statistic for window $j$ and $W_t^{(j)}$ is the corresponding window.

### 3.5 Data Collection and Experimental Design

#### 3.5.1 Datasets and Tasks

We will evaluate our framework on:

1. **Question Answering**: Natural Questions dataset with temporal evolution simulation
2. **Text Classification**: AG News and IMDB with synthetic label noise and semantic drift
3. **Code Generation**: HumanEval with evolving API specifications
4. **Dialogue**: MultiWOZ with shifting user intent distributions

#### 3.5.2 Distribution Shift Scenarios

We simulate realistic shift patterns:

- **Temporal drift**: Gradual vocabulary and topic evolution
- **Subpopulation shift**: Changing proportions of demographic groups or domains
- **Adversarial drift**: Introduction of challenging edge cases
- **Concept shift**: Changing relationship between inputs and desired outputs

#### 3.5.3 Baseline Methods

We compare against:
- Standard conformal prediction (no adaptation)
- Worst-case robust conformal prediction
- Importance-weighted conformal prediction with oracle weights
- Recent methods from literature (Wasserstein-regularized CP, Lévy-Prokhorov robust CP)
- Traditional drift detection methods (ADWIN, DDM) without uncertainty quantification

#### 3.5.4 Evaluation Metrics

**Coverage metrics**:
- Empirical coverage rate: $\frac{1}{T}\sum_{t=1}^T \mathbb{1}(Y_t \in C(X_t))$
- Coverage gap under shift: $|(1-\alpha) - \text{coverage}|$

**Efficiency metrics**:
- Average prediction set size: $\frac{1}{T}\sum_{t=1}^T |C(X_t)|$
- Conditional coverage by subgroup

**Detection metrics**:
- False alarm rate (FAR): Proportion of false alarms under null
- Average Detection Delay (ADD): Mean time from true change point to detection
- Area Under ROC Curve (AUC) for shift detection

**Computational metrics**:
- Inference latency overhead
- Memory footprint
- Annotation budget required

### 3.6 Implementation Details

The framework will be implemented in Python using PyTorch for model inference and scipy.stats for statistical testing. Key components:

- **Conformity score computation**: Batched GPU processing with caching
- **Window management**: Efficient circular buffer implementation
- **Statistical testing**: Optimized CUSUM/EWMA with incremental updates
- **Integration**: RESTful API wrapper for deployment compatibility

We will release open-source code and pre-computed results for reproducibility.

## 4. Expected Outcomes & Impact

### 4.1 Theoretical Contributions

**Theorem 1 (Coverage under monitoring)**: Under mild assumptions on the detection procedure, our framework maintains:

$$\limsup_{T \to \infty} \frac{1}{T}\sum_{t=1}^T \mathbb{1}(Y_t \notin C(X_t)) \leq \alpha + \epsilon(\beta, \delta)$$

where $\epsilon(\beta, \delta)$ is a small term depending on false alarm rate $\beta$ and minimum detectable shift $\delta$.

**Theorem 2 (Detection guarantees)**: For shifts of magnitude $\delta > \delta_0$, the detection delay satisfies:

$$E[\tau_d - \tau] \leq O\left(\frac{\log(1/\beta)}{\delta^2}\right)$$

where $\tau$ is the true change point and $\tau_d$ is the detection time.

### 4.2 Empirical Expected Results

Based on preliminary analysis, we anticipate:

1. **Maintained coverage**: 90-95% coverage rate under distribution shift (vs. 60-70% for standard CP)
2. **Improved efficiency**: 20-30% smaller prediction sets compared to worst-case robust methods
3. **Fast detection**: Detection delays of 50-200 samples for moderate shifts (effect size > 0.3)
4. **Low false alarms**: <5% false alarm rate over 10,000 sample deployments
5. **Computational feasibility**: <10ms overhead per prediction for monitoring

### 4.3 Practical Impact

**For LLM Developers**: The framework provides a principled approach to deployment monitoring, reducing the need for expensive continuous human evaluation while maintaining safety guarantees.

**For Auditors and Regulators**: Our method generates statistical evidence of model reliability over time, supporting compliance with emerging AI regulations requiring ongoing monitoring and documentation.

**For End Users**: More reliable LLM systems with quantified uncertainties improve trust and enable better human-AI collaboration, particularly in high-stakes domains like healthcare and legal applications.

**For Research Community**: This work establishes connections between conformal prediction, sequential analysis, and LLM evaluation, opening new directions for statistical foundations of foundation models.

### 4.4 Limitations and Future Work

This framework assumes access to some feedback signal (even if delayed or partial) for recalibration. Future work should explore:
- Fully unsupervised adaptation using self-consistency checks
- Extensions to multi-modal foundation models
- Integration with active learning for optimal annotation strategies
- Theoretical analysis under adversarial distribution shifts
- Privacy-preserving implementations for federated LLM deployments

By providing practical tools with theoretical guarantees, this research contributes to the critical goal of making foundation model deployments more transparent, reliable, and auditable—essential requirements for the responsible scaling of AI systems in society.