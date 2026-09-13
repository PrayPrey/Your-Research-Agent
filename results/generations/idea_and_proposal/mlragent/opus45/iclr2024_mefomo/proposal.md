# Research Proposal: Understanding the Geometry of In-Context Learning Through Representation Dynamics

## 1. Introduction

### Background

In-context learning (ICL) has emerged as one of the most surprising and practically important capabilities of large language models (LLMs). Unlike traditional machine learning paradigms that require extensive parameter updates during training, ICL enables models to solve novel tasks by simply conditioning on a few input-output demonstrations provided in the prompt. This emergent capability, first prominently observed in GPT-3, has fundamentally changed how we interact with and deploy foundation models across diverse applications.

Despite the widespread adoption of ICL in practical applications—from code generation to mathematical reasoning—our theoretical understanding of this phenomenon remains remarkably limited. Current explanations fall into two categories: (1) theoretical analyses that rely on simplified linear settings, which fail to capture the complexity of real transformer architectures, and (2) empirical studies that treat the model as a black box, offering little insight into the underlying mechanisms. Recent work by Yang et al. (2025) has begun to investigate the geometric properties of hidden states during ICL, identifying separability and alignment stages, but a comprehensive framework connecting representation geometry to ICL success remains elusive.

The selection of in-context examples significantly impacts ICL performance, yet principled methods for example selection are lacking. Practitioners often resort to heuristics or expensive trial-and-error approaches. Understanding why certain examples facilitate learning while others fail could dramatically improve the reliability and efficiency of ICL-based systems.

### Research Objectives

This research aims to develop a comprehensive understanding of ICL through the lens of representation geometry dynamics. Our specific objectives are:

1. **Characterize representation trajectories**: Systematically track how query representations evolve across transformer layers as in-context examples are processed, establishing a geometric vocabulary for describing ICL dynamics.

2. **Identify predictive geometric signatures**: Discover measurable geometric features that correlate with and predict ICL success, providing interpretable metrics for evaluating prompt quality.

3. **Develop principled example selection algorithms**: Leverage geometric insights to create automatic methods for selecting optimal in-context examples that maximize task performance.

4. **Establish theoretical connections**: Ground our empirical findings in function class learning theory, relating geometric convergence patterns to implicit Bayesian inference mechanisms.

### Significance

This research addresses fundamental questions about emergent capabilities in foundation models—a central theme of current machine learning research. By providing interpretable geometric metrics for ICL quality, we enable practitioners to move beyond trial-and-error prompt engineering. Our theoretical framework will contribute to the broader goal of understanding how transformers implement learning algorithms implicitly, potentially informing the design of more efficient and capable architectures. Furthermore, understanding ICL geometry may reveal insights into model robustness and failure modes, contributing to AI safety and alignment efforts.

## 2. Methodology

### 2.1 Data Collection and Experimental Setup

#### Datasets and Tasks

We will conduct experiments across diverse task categories to ensure generalizability:

1. **Classification Tasks**: Sentiment analysis (SST-2, IMDB), topic classification (AG News), natural language inference (SNLI, MNLI)
2. **Generation Tasks**: Translation (WMT subsets), summarization (CNN/DailyMail)
3. **Reasoning Tasks**: Arithmetic, symbolic reasoning, BIG-Bench Hard subsets
4. **Structured Tasks**: Named entity recognition, relation extraction

For each task, we will create controlled experimental sets with varying numbers of in-context examples ($k \in \{1, 2, 4, 8, 16, 32\}$) and diverse example orderings.

#### Models

We will analyze multiple model families and scales:
- LLaMA-2 (7B, 13B, 70B parameters)
- GPT-2 (124M to 1.5B parameters)
- Pythia suite (70M to 12B parameters)

This selection enables analysis of scale effects while maintaining computational feasibility.

### 2.2 Representation Extraction and Trajectory Analysis

#### Hidden State Extraction

For a prompt $P = [e_1, e_2, ..., e_k, q]$ containing $k$ in-context examples and query $q$, we extract hidden representations at each layer $l \in \{1, ..., L\}$:

$$h_q^{(l)} = \text{Transformer}^{(l)}(P)[pos(q)]$$

where $pos(q)$ denotes the token position(s) of the query. For multi-token queries, we aggregate using mean pooling or the final token representation.

#### Trajectory Characterization

We define the **representation trajectory** as the sequence of query representations across layers:

$$\mathcal{T}(q | E) = \{h_q^{(0)}, h_q^{(1)}, ..., h_q^{(L)}\}$$

where $E = \{e_1, ..., e_k\}$ is the set of in-context examples. To quantify trajectory dynamics, we compute:

**Inter-layer displacement**:
$$\delta^{(l)} = \|h_q^{(l)} - h_q^{(l-1)}\|_2$$

**Cumulative trajectory length**:
$$\mathcal{L}(\mathcal{T}) = \sum_{l=1}^{L} \delta^{(l)}$$

**Trajectory curvature** at layer $l$:
$$\kappa^{(l)} = \frac{\|v^{(l)} - v^{(l-1)}\|}{\|v^{(l-1)}\|}$$

where $v^{(l)} = h_q^{(l)} - h_q^{(l-1)}$ is the velocity vector.

### 2.3 Geometric Signatures of Successful ICL

#### Task Subspace Identification

For each task $\tau$, we construct a **task subspace** $\mathcal{S}_\tau$ from the representations of correctly-solved examples. Given a set of successful query representations $\{h_{q_i}^{(L)}\}_{i=1}^{N}$ at the final layer, we compute:

$$\mathcal{S}_\tau = \text{span}(U_d)$$

where $U_d$ contains the top-$d$ principal components from PCA on the centered representations.

#### Convergence Metrics

We hypothesize that successful ICL corresponds to query representations converging toward task-specific subspaces. We measure this through:

**Subspace projection magnitude**:
$$\pi_\tau(h_q^{(l)}) = \|U_d^T (h_q^{(l)} - \mu_\tau)\|_2$$

where $\mu_\tau$ is the mean of task exemplar representations.

**Convergence rate**:
$$\rho = \frac{\pi_\tau(h_q^{(L)}) - \pi_\tau(h_q^{(0)})}{\pi_\tau(h_q^{(0)})}$$

**Alignment score** between query trajectory and task subspace:
$$\alpha^{(l)} = \cos(v^{(l)}, \mathcal{S}_\tau) = \frac{\|U_d^T v^{(l)}\|}{\|v^{(l)}\|}$$

#### Separability Metrics

Following insights from Yang et al. (2025), we measure class separability evolution:

**Fisher discriminant ratio** at layer $l$:
$$\mathcal{F}^{(l)} = \frac{\|\mu_+^{(l)} - \mu_-^{(l)}\|^2}{\sigma_+^{(l)2} + \sigma_-^{(l)2}}$$

where $\mu_{\pm}^{(l)}$ and $\sigma_{\pm}^{(l)}$ are class-conditional means and standard deviations.

### 2.4 Predictive Framework for ICL Success

#### Feature Engineering

We construct a geometric feature vector $\phi(q, E)$ for each query-example configuration:

$$\phi(q, E) = [\mathcal{L}(\mathcal{T}), \rho, \{\alpha^{(l)}\}_{l=1}^{L}, \{\mathcal{F}^{(l)}\}_{l=1}^{L}, \pi_\tau(h_q^{(L)})]$$

#### Prediction Model

We train a lightweight predictor $f_\theta$ to estimate ICL success probability:

$$\hat{p}_{success} = f_\theta(\phi(q, E))$$

We will compare:
1. **Linear models**: Logistic regression for interpretability
2. **Gradient boosted trees**: XGBoost for capturing nonlinear relationships
3. **Neural networks**: Small MLPs for flexibility

The predictor is trained on held-out tasks to ensure generalization.

### 2.5 Principled Example Selection Algorithm

Based on our geometric framework, we propose **Geometric Example Selection (GES)**:

**Algorithm: GES**
```
Input: Query q, candidate example pool C, model M, target task τ
Output: Optimal example set E* of size k

1. Compute task subspace Sτ from validation examples
2. For each candidate c ∈ C:
   a. Compute h_q^(L) conditioned on {c}
   b. Calculate geometric score: g(c) = α_τ(h_q^(L)) + λ·π_τ(h_q^(L))
3. Initialize E* = {} 
4. For i = 1 to k:
   a. For each remaining candidate c ∈ C \ E*:
      - Compute h_q^(L) conditioned on E* ∪ {c}
      - Calculate marginal geometric gain: Δg(c) = g(E* ∪ {c}) - g(E*)
   b. E* = E* ∪ {argmax_c Δg(c)}
5. Return E*
```

The hyperparameter $\lambda$ balances alignment and projection magnitude, tuned via cross-validation.

### 2.6 Theoretical Framework

We connect our geometric findings to implicit Bayesian inference. Under the hypothesis that transformers implement approximate Bayesian inference:

$$p(y|q, E) \propto \int p(y|q, f) p(f|E) df$$

where $f$ represents the implicit task function, we posit that:

1. **Task subspaces encode function posteriors**: The geometric convergence toward $\mathcal{S}_\tau$ reflects concentration of the implicit posterior $p(f|E)$.

2. **Alignment measures posterior precision**: Higher alignment scores correspond to lower posterior variance.

We will formalize these connections using tools from information geometry, relating representation distances to KL divergences between implicit posteriors.

### 2.7 Evaluation Metrics

**For geometric characterization**:
- Explained variance ratio of task subspaces
- Correlation between geometric metrics and task accuracy

**For prediction**:
- ROC-AUC for success prediction
- Calibration error (ECE)

**For example selection**:
- Task accuracy improvement over baselines (random, similarity-based, influence functions)
- Computational efficiency (FLOPs, wall-clock time)

**Baselines**: We compare against:
1. Random selection
2. Embedding similarity-based selection
3. KATE (kNN-based selection)
4. EPR (retrieval-based selection)

### 2.8 Experimental Design

**Experiment 1: Trajectory Characterization**
- Track representations across all layers for 10,000 queries per task
- Analyze trajectory statistics as function of example count and quality

**Experiment 2: Geometric Signatures**
- Identify signatures that distinguish successful vs. failed ICL
- Test consistency across model scales and families

**Experiment 3: Prediction Validation**
- Train predictors on subset of tasks, evaluate on held-out tasks
- Ablate feature importance

**Experiment 4: Example Selection**
- Compare GES against baselines across all task categories
- Analyze computational-accuracy tradeoffs

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Comprehensive geometric characterization of ICL**: We expect to establish that successful ICL exhibits consistent geometric patterns—specifically, monotonic convergence toward task subspaces with increasing alignment scores in deeper layers. We anticipate identifying critical "transition layers" where task-specific structure emerges.

2. **Predictive geometric metrics**: We expect our geometric features to predict ICL success with AUC > 0.85 on held-out tasks, significantly outperforming baseline predictors that use only surface-level features.

3. **Effective example selection algorithm**: GES is expected to improve ICL accuracy by 5-15% over random selection and 2-8% over existing retrieval-based methods, while providing interpretable selection rationale.

4. **Theoretical insights**: We anticipate formalizing connections between geometric convergence and implicit Bayesian inference, providing mathematical grounding for observed phenomena.

5. **Open-source toolkit**: We will release a comprehensive toolkit for representation analysis and example selection, enabling further research.

### Impact

**Scientific Impact**: This research will advance our fundamental understanding of emergent capabilities in foundation models—a critical gap identified by the research community. By providing a geometric vocabulary for ICL, we enable more precise scientific discourse about these phenomena.

**Practical Impact**: Our example selection algorithm will directly improve ICL performance in real applications, reducing the need for expensive trial-and-error prompt engineering. The predictive framework enables early detection of ICL failures, improving system reliability.

**Broader Impact**: Understanding ICL geometry may reveal failure modes and biases encoded in representation spaces, contributing to AI safety. Our interpretable metrics could support alignment efforts by providing windows into model behavior.

**Future Directions**: This work opens avenues for geometry-aware model training, where pretraining objectives explicitly encourage favorable ICL geometry, and for architecture design informed by representation dynamics requirements.

In conclusion, this research addresses fundamental questions about foundation model capabilities through a novel geometric lens, promising both theoretical advances and practical tools for the research community.