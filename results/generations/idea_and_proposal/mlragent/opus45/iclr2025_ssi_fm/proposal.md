# Research Proposal: Curriculum-Aware Verifier Ensembles for Robust Self-Improvement in Foundation Models

## 1. Introduction

### Background

Foundation models (FMs), particularly large language models (LLMs), have achieved remarkable capabilities through pre-training on vast internet-scale datasets. However, the field faces an imminent crisis: high-quality training data is finite and growing slower than model consumption demands. Recent projections suggest that we will exhaust high-quality internet data within the next few years, creating a fundamental bottleneck for continued progress. This data scarcity problem extends beyond language models to embodied AI, where real robot interaction data remains severely limited.

Self-improvement—the paradigm where models train on their own generated synthetic data—offers a promising path forward. Unlike supervised learning with human annotations or standard reinforcement learning with ground-truth rewards, self-improvement operates in a unique regime where models must bootstrap their own training signal. This creates both opportunities and challenges: models can potentially scale beyond human-provided data, but they must navigate the treacherous landscape of unreliable self-evaluation.

A critical challenge in self-improvement is the reliance on learned verifiers or reward models that can fail arbitrarily. When a model generates candidate outputs and a verifier evaluates them, errors in verification compound across training iterations. Without ground-truth rewards available in traditional RL settings, these accumulated errors can lead to model collapse—a catastrophic failure mode where model quality degrades rather than improves with additional training. Recent work on self-play fine-tuning and intrinsic self-correction demonstrates that self-improvement is achievable, but current methods remain fragile and often plateau prematurely.

### Research Objectives

This research proposes a **Curriculum-Aware Verifier Ensemble (CAVE)** framework that addresses the fundamental unreliability of learned verifiers in self-improvement pipelines. Our key insight is that verifier reliability varies systematically with problem difficulty: easier problems are verified more accurately than harder ones. Current approaches ignore this structure, treating all verifier errors uniformly as noise. We exploit this observation to design a principled framework that:

1. **Stratifies verification by difficulty**, training specialized verifiers for different difficulty regimes
2. **Estimates verification confidence** through inter-verifier disagreement patterns
3. **Implements adaptive curricula** that prioritize high-confidence examples while gradually expanding to harder problems
4. **Co-evolves verifiers with generators** through regularized retraining that prevents bias drift

### Significance

This research addresses a fundamental gap between theoretical self-improvement potential and practical outcomes. By grounding verifier reliability in problem difficulty—a measurable and exploitable property—we transform the abstract challenge of "unreliable feedback" into a tractable algorithmic problem. Success would enable sustained self-improvement beyond current plateaus, with direct applications to language models, robotic systems, and multi-modal foundation models. Furthermore, our framework provides principled mechanisms for knowing when to defer to human oversight, contributing to safer deployment of self-improving systems.

## 2. Methodology

### 2.1 Problem Formulation

Let $\pi_\theta$ denote a foundation model parameterized by $\theta$ that generates outputs $y$ given inputs $x$. Let $V_\phi: (x, y) \rightarrow [0, 1]$ denote a learned verifier that estimates the quality of generation $y$ for input $x$. In self-improvement, we iteratively:

1. Sample generations: $y \sim \pi_\theta(\cdot | x)$
2. Evaluate with verifier: $s = V_\phi(x, y)$
3. Update model on high-scoring examples: $\theta \leftarrow \text{Update}(\theta, \{(x, y) : s > \tau\})$

The fundamental challenge is that $V_\phi$ is imperfect. Define the verifier error rate at difficulty level $d$ as:

$$\epsilon(d) = \mathbb{E}_{(x,y): \text{diff}(x)=d}\left[|V_\phi(x, y) - V^*(x, y)|\right]$$

where $V^*$ is the true (unknown) quality function. Our key assumption, supported by empirical observations, is that $\epsilon(d)$ increases monotonically with difficulty $d$.

### 2.2 Difficulty-Stratified Verifier Training

We train an ensemble of $K$ verifiers $\{V_{\phi_1}, \ldots, V_{\phi_K}\}$, each specialized for different difficulty regimes. First, we estimate problem difficulty using a lightweight difficulty estimator $D_\psi: x \rightarrow [0, 1]$ trained on proxy signals (e.g., solution length, number of reasoning steps required, historical model performance).

**Training Procedure:**
1. Partition the training data into $K$ difficulty strata: $\mathcal{S}_k = \{(x, y, v) : d_{k-1} \leq D_\psi(x) < d_k\}$ where $0 = d_0 < d_1 < \ldots < d_K = 1$
2. Train verifier $V_{\phi_k}$ primarily on stratum $\mathcal{S}_k$ with curriculum mixing:

$$\mathcal{L}_k = \sum_{j=1}^{K} w_{kj} \cdot \mathbb{E}_{(x,y,v) \sim \mathcal{S}_j}\left[(V_{\phi_k}(x, y) - v)^2\right]$$

where weights $w_{kj} \propto \exp(-\lambda |k - j|)$ ensure focus on the target stratum while maintaining some generalization.

3. Additionally, train a generalist verifier $V_{\phi_0}$ on all data uniformly to provide a calibration baseline.

### 2.3 Agreement-Based Confidence Estimation

Given an input-output pair $(x, y)$, we compute ensemble predictions and estimate confidence through disagreement analysis.

**Confidence Score Computation:**

Let $s_k = V_{\phi_k}(x, y)$ for $k \in \{0, 1, \ldots, K\}$. We compute:

1. **Difficulty-weighted prediction:**
$$\hat{s}(x, y) = \sum_{k=1}^{K} \alpha_k(x) \cdot s_k$$

where $\alpha_k(x) \propto \exp(-\gamma |D_\psi(x) - \bar{d}_k|)$ and $\bar{d}_k = (d_{k-1} + d_k)/2$

2. **Disagreement measure:**
$$\sigma^2(x, y) = \frac{1}{K} \sum_{k=1}^{K} (s_k - \hat{s})^2 + \beta \cdot |s_0 - \hat{s}|$$

where the second term penalizes deviation from the generalist baseline.

3. **Confidence score:**
$$C(x, y) = \exp\left(-\frac{\sigma^2(x, y)}{\sigma_0^2}\right) \cdot \text{clip}\left(\frac{\hat{s}(x, y)}{\tau_{\text{base}}}, 0, 1\right)$$

where $\sigma_0^2$ is a normalization constant and $\tau_{\text{base}}$ is a baseline acceptance threshold.

**Deferral Mechanism:** When $C(x, y) < C_{\text{defer}}$, the example is flagged for human review rather than automatic acceptance or rejection, enabling graceful degradation in uncertain regions.

### 2.4 Adaptive Curriculum for Self-Training

We implement a curriculum that evolves with model capability, prioritizing high-confidence regions while gradually expanding coverage.

**Curriculum Schedule:**

At training iteration $t$, define the acceptance criterion:

$$A_t(x, y) = \mathbb{1}\left[\hat{s}(x, y) > \tau_t(x) \text{ and } C(x, y) > C_t\right]$$

where:
- $\tau_t(x) = \tau_{\text{base}} + \eta \cdot D_\psi(x) \cdot (1 - \rho^t)$ is a difficulty-adaptive, time-decaying threshold
- $C_t = C_{\text{max}} - (C_{\text{max}} - C_{\text{min}}) \cdot (1 - \rho^t)$ relaxes confidence requirements over time

**Curriculum Loss Function:**

The training objective incorporates example weights based on confidence and curriculum position:

$$\mathcal{L}_{\text{self-improve}}(\theta) = -\mathbb{E}_{x \sim \mathcal{D}, y \sim \pi_\theta(\cdot|x)}\left[A_t(x, y) \cdot w_t(x, y) \cdot \log \pi_\theta(y|x)\right]$$

where $w_t(x, y) = C(x, y)^\alpha \cdot \exp(\mu \cdot D_\psi(x))$ upweights confident, challenging examples.

### 2.5 Verifier Co-Evolution with Regularization

To prevent verifiers from drifting toward generator biases, we periodically retrain verifiers on accepted generations with careful regularization.

**Co-Evolution Protocol:**

Every $T_{\text{retrain}}$ iterations:
1. Collect accepted generations: $\mathcal{G}_t = \{(x, y) : A_t(x, y) = 1\}$
2. Obtain pseudo-labels through ensemble consensus: $\tilde{v}(x, y) = \hat{s}(x, y)$
3. Retrain verifiers with regularization:

$$\mathcal{L}_{\text{verifier}}(\phi_k) = \mathbb{E}_{(x,y,\tilde{v}) \sim \mathcal{G}_t}\left[(V_{\phi_k}(x, y) - \tilde{v})^2\right] + \lambda_{\text{anchor}} \cdot \mathcal{L}_{\text{anchor}}(\phi_k) + \lambda_{\text{div}} \cdot \mathcal{L}_{\text{diversity}}$$

where:
- $\mathcal{L}_{\text{anchor}}(\phi_k) = \|V_{\phi_k} - V_{\phi_k}^{(0)}\|^2_{\mathcal{D}_{\text{held}}}$ anchors to original behavior on held-out data
- $\mathcal{L}_{\text{diversity}} = -\sum_{k \neq j} \text{KL}(V_{\phi_k} \| V_{\phi_j})$ maintains ensemble diversity

### 2.6 Experimental Design

**Datasets and Domains:**
1. **Mathematical Reasoning:** GSM8K, MATH, and AIME problems with varying difficulty levels
2. **Code Generation:** HumanEval, MBPP, and CodeContests with execution-based verification
3. **General Language Tasks:** MMLU subsets with verifiable answers

**Baselines:**
- Standard self-training with single verifier
- Self-Play Fine-Tuning (SPIN) 
- Rejection sampling with reward model (Best-of-N)
- Iterative DPO with self-generated preferences

**Evaluation Metrics:**
1. **Task Performance:** Accuracy/pass@k on held-out test sets across iterations
2. **Collapse Rate:** $\text{CR}_t = \max(0, \text{Perf}_0 - \text{Perf}_t) / \text{Perf}_0$
3. **Improvement Sustainability:** Number of iterations before performance plateaus (defined as $<1\%$ gain over 5 iterations)
4. **Verifier Calibration:** Expected Calibration Error (ECE) of confidence estimates
5. **Deferral Efficiency:** Precision/recall of deferral decisions against oracle labels

**Ablation Studies:**
- Impact of ensemble size $K$
- Effect of curriculum schedule parameters $(\rho, \eta, \mu)$
- Contribution of each component (stratification, confidence estimation, co-evolution)
- Sensitivity to difficulty estimator accuracy

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following concrete outcomes from this research:

1. **Reduced Model Collapse:** We expect CAVE to reduce collapse rates by 60-80% compared to single-verifier baselines, enabling sustained improvement over significantly more training iterations.

2. **Extended Improvement Horizon:** Current self-improvement methods typically plateau within 3-5 iterations. We target sustained improvement for 10+ iterations, potentially doubling effective self-improvement gains.

3. **Improved Verification Reliability:** Difficulty-stratified verifiers should achieve 15-25% lower expected calibration error than monolithic verifiers, with agreement-based confidence providing well-calibrated uncertainty estimates.

4. **Efficient Human Oversight:** The deferral mechanism should identify 80%+ of verifier failure cases while flagging less than 10% of total examples, enabling efficient human-in-the-loop scaling.

5. **Theoretical Contributions:** We will provide formal analysis of conditions under which curriculum-aware verification provably prevents collapse, extending theoretical frameworks for the verification-generation gap.

### Broader Impact

**Advancing Self-Improvement Science:** This research contributes fundamental algorithmic principles for self-improvement that transcend specific domains. The curriculum-aware verification framework provides a template for designing robust self-improvement systems across foundation model applications.

**Safety and Alignment Implications:** By explicitly modeling verifier uncertainty and providing deferral mechanisms, CAVE contributes to safer self-improvement pipelines. The framework naturally accommodates human oversight at uncertainty boundaries, supporting responsible scaling of autonomous model improvement.

**Resource Efficiency:** Successful self-improvement reduces dependence on costly human annotation and limited high-quality data, democratizing access to capable AI systems and reducing environmental costs of data collection.

**Theoretical Foundations:** Our analysis of difficulty-dependent verification reliability contributes to theoretical understanding of when and how self-improvement succeeds or fails, informing future algorithm design and safety analysis.

### Limitations and Future Directions

We acknowledge that CAVE introduces additional complexity through multiple verifiers and curriculum management. Future work should explore distillation techniques to compress ensemble knowledge into efficient single-model deployments. Additionally, extending the framework to settings with minimal initial labeled data and investigating connections to weak-to-strong generalization represent promising research directions.

In conclusion, this research addresses a critical bottleneck in scaling foundation models beyond human-curated data by developing principled algorithms for robust self-improvement. By exploiting the structure of verifier reliability across problem difficulties, CAVE promises to unlock sustained model improvement while maintaining safety through calibrated uncertainty and human deferral mechanisms.