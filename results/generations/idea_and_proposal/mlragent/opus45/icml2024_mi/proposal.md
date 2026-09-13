# Research Proposal: Calibrating Human Feedback Models via Cognitive Load-Aware Preference Learning

## 1. Introduction

### Background

The alignment of artificial intelligence systems with human values and intentions stands as one of the most critical challenges in modern AI research. Reinforcement Learning from Human Feedback (RLHF) has emerged as a dominant paradigm for this purpose, enabling the fine-tuning of large language models and other AI systems based on human preference judgments. However, the foundational assumptions underlying RLHF—that human feedback is consistent, unbiased, and representative of true preferences—are increasingly being questioned by both the AI safety community and cognitive science research.

The standard approach to preference learning typically employs the Bradley-Terry model or similar frameworks that assume homoscedastic noise in human judgments. Under this assumption, the probability that a human prefers response $A$ over response $B$ is modeled as:

$$P(A \succ B) = \frac{\exp(r(A))}{\exp(r(A)) + \exp(r(B))}$$

where $r(\cdot)$ represents the underlying reward function. This formulation implicitly assumes that the noise in human judgments remains constant across all comparisons and throughout the annotation process. However, extensive research in cognitive psychology demonstrates that human decision-making quality systematically degrades under conditions of mental fatigue, time pressure, and high cognitive load.

When annotators engage in lengthy preference labeling sessions—common in large-scale RLHF data collection—they experience progressive cognitive depletion. This manifests as increased response time variability, higher error rates, and a systematic bias toward selecting simpler or more familiar options. Such degradation introduces heteroscedastic noise that standard preference models fail to capture, potentially leading to reward models that reflect cognitively-impaired approximations rather than genuine human values.

Recent work by Alsagheer et al. (2025) demonstrated that evaluator rationality significantly impacts the consistency of RLHF signals, with lower-rationality participants showing considerable variability in reinforcement decisions. Similarly, research on capacity-limited Bayesian reinforcement learning by Arumugam et al. (2024) provides theoretical foundations for understanding how processing constraints affect decision-making. These findings underscore the urgent need for preference learning frameworks that explicitly account for cognitive limitations.

### Research Objectives

This research aims to develop and validate a cognitive load-aware preference learning framework (CLAP) that:

1. **Models cognitive load dynamics**: Develop a principled approach to estimate annotator cognitive load from observable behavioral indicators during preference annotation sessions.

2. **Incorporates heteroscedastic noise**: Design a preference model that explicitly accounts for varying feedback reliability as a function of estimated cognitive state.

3. **Optimizes annotation protocols**: Create an active querying strategy that maximizes information acquisition while respecting cognitive resource constraints.

4. **Validates alignment improvements**: Demonstrate that accounting for cognitive load leads to reward models that better capture true human preferences.

### Significance

This research addresses a fundamental but overlooked assumption violation in human-AI alignment. By bridging cognitive science insights with RLHF methodology, we contribute to:

- **More robust reward models** that distinguish between genuine preferences and fatigue-induced noise
- **Practical guidelines** for annotation protocol design that optimize data quality
- **Theoretical foundations** for understanding human feedback as a cognitively-constrained process
- **Improved AI alignment** by ensuring systems learn from high-quality human judgments

## 2. Methodology

### 2.1 Overview

Our methodology comprises four interconnected components: (1) cognitive load estimation from behavioral signals, (2) heteroscedastic preference modeling, (3) cognitive budget-aware active learning, and (4) comprehensive experimental validation.

### 2.2 Cognitive Load Estimation

We propose tracking multiple observable indicators that serve as proxies for cognitive load. Let $\mathbf{z}_t = (z_t^{(1)}, z_t^{(2)}, ..., z_t^{(K)})$ denote the vector of $K$ cognitive load indicators observed at annotation time $t$:

**Response Time Features:**
- Raw response time: $z_t^{(1)} = \tau_t$
- Response time deviation from personal baseline: $z_t^{(2)} = \tau_t - \bar{\tau}_i$ for annotator $i$
- Response time coefficient of variation over recent window: $z_t^{(3)} = \text{CV}(\tau_{t-w:t})$

**Session Context Features:**
- Time since session start: $z_t^{(4)} = t - t_{\text{start}}$
- Number of comparisons completed: $z_t^{(5)} = n_t$
- Time since last break: $z_t^{(6)} = t - t_{\text{break}}$

**Decision Complexity Features:**
- Length differential between compared responses: $z_t^{(7)} = |len(A) - len(B)|$
- Semantic similarity between options: $z_t^{(8)} = \text{sim}(A, B)$
- Estimated comparison difficulty from pilot data: $z_t^{(9)} = d_t$

We model the latent cognitive load $c_t \in [0, 1]$ as a function of these observables using a Bayesian approach:

$$c_t = \sigma\left(\mathbf{w}^\top \mathbf{z}_t + \epsilon_t\right)$$

where $\sigma(\cdot)$ is the sigmoid function, $\mathbf{w}$ are learnable weights, and $\epsilon_t \sim \mathcal{N}(0, \sigma_\epsilon^2)$ captures estimation uncertainty. We place a Gaussian prior on $\mathbf{w}$ and perform variational inference to obtain posterior estimates.

### 2.3 Heteroscedastic Preference Model

We extend the standard Bradley-Terry model to incorporate cognitive load-dependent noise. For a comparison between responses $A$ and $B$ made at time $t$ with estimated cognitive load $c_t$, we define:

$$P(A \succ B | c_t) = \Phi\left(\frac{r(A) - r(B)}{\sigma(c_t)}\right)$$

where $\Phi(\cdot)$ is the standard normal CDF and $\sigma(c_t)$ is the load-dependent noise scale:

$$\sigma(c_t) = \sigma_0 + \alpha \cdot c_t + \beta \cdot c_t^2$$

Here, $\sigma_0$ represents baseline noise under optimal cognitive conditions, while $\alpha$ and $\beta$ capture linear and quadratic increases in noise with cognitive load. This formulation ensures that feedback from fatigued annotators contributes less to the reward model through implicit down-weighting.

The full generative model becomes:

$$\mathcal{L}(\theta, \phi) = \sum_{(A,B,y,t) \in \mathcal{D}} \log P(y | A, B, c_t; \theta) + \log p(\theta) + \log p(\phi)$$

where $\theta = \{r(\cdot), \sigma_0, \alpha, \beta\}$ are the preference model parameters, $\phi = \{\mathbf{w}, \sigma_\epsilon\}$ are the cognitive load model parameters, $y \in \{0, 1\}$ indicates the preference label, and $\mathcal{D}$ is the dataset of annotated comparisons.

We optimize this objective using a two-stage procedure:
1. **Stage 1**: Fit the cognitive load model $\phi$ using annotator consistency metrics as supervision
2. **Stage 2**: Jointly optimize $\theta$ with fixed or slowly-adapting $\phi$

### 2.4 Cognitive Budget-Aware Active Learning

Rather than selecting queries solely based on expected information gain, we propose an active learning strategy that optimizes the trade-off between informativeness and cognitive cost. For a candidate comparison $(A, B)$, we define:

**Expected Information Gain:**
$$I(A, B) = H[r(A) - r(B)] - \mathbb{E}_{y}[H[r(A) - r(B) | y]]$$

where $H[\cdot]$ denotes entropy under the current posterior.

**Cognitive Cost:**
$$C(A, B, t) = \gamma_1 \cdot d(A, B) + \gamma_2 \cdot \hat{c}_t + \gamma_3 \cdot \mathbb{1}[\hat{c}_t > \tau_{\text{break}}]$$

where $d(A, B)$ is the estimated decision difficulty, $\hat{c}_t$ is the predicted cognitive load at time $t$, and the indicator function triggers mandatory breaks when load exceeds threshold $\tau_{\text{break}}$.

**Acquisition Function:**
$$a(A, B, t) = I(A, B) - \lambda \cdot C(A, B, t) \cdot \sigma(\hat{c}_t)$$

The weighting by $\sigma(\hat{c}_t)$ ensures that as cognitive load increases, we increasingly favor simpler comparisons to maintain feedback quality. The algorithm proceeds as:

```
Algorithm 1: Cognitive Budget-Aware Active Query Selection
Input: Candidate pool Q, current cognitive load estimate ĉ_t, budget B
Output: Selected query (A*, B*)

1. For each (A, B) ∈ Q:
   a. Compute I(A, B) using current reward posterior
   b. Compute C(A, B, t) based on complexity and load
   c. Compute acquisition score a(A, B, t)
2. If ĉ_t > τ_break: trigger break, update t_break
3. Return (A*, B*) = argmax a(A, B, t)
4. After annotation: update ĉ_{t+1} using observed z_{t+1}
```

### 2.5 Experimental Design

We design a comprehensive experimental protocol to validate our framework across multiple dimensions:

#### Dataset Construction

**Phase 1 - Pilot Study (N=50 annotators):**
- Collect preference annotations on 1,000 response pairs from existing LLM outputs
- Record all behavioral signals (response times, session metadata)
- Include attention checks and repeated pairs to measure consistency
- Administer validated cognitive load questionnaires (NASA-TLX) at intervals

**Phase 2 - Main Annotation (N=200 annotators):**
- Collect 50,000 preference annotations using standard protocol (control)
- Collect 50,000 annotations using CLAP-guided protocol (treatment)
- Randomize annotators to conditions with stratification

#### Evaluation Metrics

**Reward Model Quality:**
- *Prediction accuracy*: Agreement with held-out gold-standard preferences
- *Consistency score*: $\text{Cons} = 1 - \frac{1}{|\mathcal{R}|}\sum_{(A,B) \in \mathcal{R}} |P(A \succ B) - P(A \succ B)'|$ for repeated pairs
- *Inter-annotator agreement*: Fleiss' kappa on overlapping annotations

**Cognitive Load Calibration:**
- Correlation between estimated $\hat{c}_t$ and self-reported NASA-TLX scores
- Predictive accuracy for annotation inconsistencies

**Downstream Alignment:**
- Win rate of CLAP-trained model vs. baseline in human evaluation
- Safety metric: Rate of harmful outputs in adversarial evaluation
- Helpfulness rating on standardized benchmark tasks

#### Baselines

1. **Standard Bradley-Terry**: Homoscedastic preference model
2. **Time-weighted**: Heuristic down-weighting of late-session annotations
3. **Annotator-specific**: Separate noise parameters per annotator (without cognitive dynamics)
4. **Oracle**: Model trained only on high-consistency annotations (upper bound)

#### Statistical Analysis

We will employ mixed-effects models to account for annotator-level variation:

$$y_{ij} = \beta_0 + \beta_1 \cdot \text{CLAP}_{ij} + u_i + \epsilon_{ij}$$

where $u_i \sim \mathcal{N}(0, \sigma_u^2)$ represents annotator random effects. We will report 95% confidence intervals and conduct power analysis to ensure adequate sample sizes for detecting meaningful effect sizes (Cohen's d ≥ 0.3).

### 2.6 Implementation Details

- **Reward model architecture**: Transformer-based reward model initialized from LLaMA-7B
- **Optimization**: AdamW with learning rate 1e-5, cosine decay schedule
- **Cognitive load model**: Bayesian neural network with 2 hidden layers (64 units each)
- **Infrastructure**: Implementation using OpenRLHF framework for scalability
- **Reproducibility**: All code, data, and trained models will be publicly released

## 3. Expected Outcomes & Impact

### Primary Outcomes

1. **Validated Cognitive Load Model**: We expect to demonstrate strong correlation (r > 0.6) between our estimated cognitive load and ground-truth measures (NASA-TLX, annotation consistency), establishing behavioral signals as reliable proxies for annotator mental state.

2. **Improved Reward Model Accuracy**: Our heteroscedastic preference model should achieve 5-10% improvement in prediction accuracy on held-out gold-standard preferences compared to standard Bradley-Terry, with larger gains for comparisons made during high-load periods.

3. **Enhanced Annotation Efficiency**: The cognitive budget-aware active learning strategy should achieve equivalent reward model quality with 20-30% fewer annotations by strategically avoiding queries during fatigued states.

4. **Better Downstream Alignment**: LLMs fine-tuned using CLAP-calibrated reward models should show statistically significant improvements in human evaluation win rates (≥55% vs. baseline) and reduced harmful output rates.

### Broader Impact

**Scientific Contributions:**
- First systematic integration of cognitive load dynamics into RLHF preference modeling
- Theoretical framework bridging rate-distortion theory with practical preference learning
- Empirical characterization of how annotation fatigue affects AI alignment

**Practical Applications:**
- Guidelines for annotation protocol design (session length, break scheduling, difficulty sequencing)
- Open-source tools for monitoring annotator cognitive state in real-time
- Recommendations for crowdsourcing platforms to improve data quality

**AI Safety Implications:**
- More accurate reward models reduce risk of misalignment from corrupted feedback
- Explicit uncertainty quantification enables identification of under-specified preference regions
- Framework extensible to other cognitive biases affecting human feedback

### Limitations and Future Directions

We acknowledge that cognitive load is one of many factors affecting feedback quality. Future work should extend this framework to incorporate:
- Individual differences in cognitive capacity and expertise
- Emotional state and motivation dynamics
- Cultural and demographic variation in decision-making patterns
- Multi-modal feedback beyond pairwise preferences

By addressing the fundamental assumption that human feedback quality is constant, this research contributes to building AI systems that truly align with human values as expressed under optimal cognitive conditions, rather than fatigue-impaired approximations. This represents a critical step toward trustworthy and beneficial AI.