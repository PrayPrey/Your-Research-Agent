# Research Proposal: Learned Environment Complexity: Meta-Training Neural Predictors for Algorithm-Specific RL Performance

## 1. Introduction

### 1.1 Background

Reinforcement learning (RL) has achieved remarkable success in diverse domains, from game playing to robotic control and resource management. However, a persistent and widening gap exists between theoretical developments and practical applications. RL theory has made substantial progress in characterizing the sample complexity of learning, identifying structural properties that enable efficient learning, and designing algorithms with provable guarantees. Yet these theoretical advances often focus on worst-case scenarios and simplified settings that fail to capture the nuances of real-world applications.

On the practical side, empirical RL research has produced algorithms that achieve impressive performance on complex benchmarks, but these successes often rely on extensive hyperparameter tuning, domain-specific heuristics, and engineering fixes that lack theoretical justification. A critical manifestation of this theory-practice gap is the algorithm selection problem: given a new RL task, practitioners must often resort to exhaustive experimentation to determine which algorithm will perform best, as theoretical complexity measures provide limited guidance.

Recent work has attempted to bridge this gap through hand-crafted complexity measures. The Effective Horizon metric, introduced by Laidlaw et al. (2023), measures Q-value alignment under random policies and achieves moderate correlation (Pearson $r \approx 0.5$) with deep RL algorithm performance. While this represents progress, such measures treat all algorithms identically, fundamentally missing the crucial algorithm-environment interaction that determines practical success. The same MDP can yield dramatically different outcomes for different algorithms—a phenomenon well-documented in the "deadly triad" literature—yet static complexity measures cannot capture this variability.

### 1.2 Research Objectives

This research proposes **Learned Environment Complexity (LEC)**, a meta-learned neural predictor that estimates algorithm-specific RL performance from MDP structural features and early training signals. Our core insight is that algorithm-environment interaction patterns—which static measures inherently miss—can be learned from diverse training data rather than manually designed.

The primary objectives of this research are:

1. **Develop a meta-learning framework** that trains neural predictors on MDP-algorithm pairs across diverse benchmarks to capture algorithm-specific complexity patterns.

2. **Demonstrate superior predictive performance** by achieving Pearson correlation $r > 0.70$ with final algorithm performance, significantly exceeding hand-crafted baselines ($r \approx 0.50$).

3. **Enable practical algorithm selection** with accuracy exceeding 70%, providing practitioners with principled guidance for choosing algorithms without exhaustive experimentation.

4. **Generate theoretical insights** by analyzing learned representations to identify what structural and dynamic features drive algorithm-specific performance.

### 1.3 Significance

This research addresses a fundamental challenge in making RL more accessible and efficient. By providing reliable performance predictions, LEC can:

- **Reduce computational costs** by eliminating the need for exhaustive algorithm comparisons on new tasks
- **Bridge theory and practice** by offering data-driven insights into algorithm-environment interactions that can inform theoretical analysis
- **Accelerate RL deployment** in real-world applications where computational resources are limited
- **Identify new problem structures** by revealing which MDP features most strongly predict algorithm success or failure

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{M}$ denote an MDP characterized by state space $\mathcal{S}$, action space $\mathcal{A}$, transition dynamics $P$, reward function $R$, and discount factor $\gamma$. Let $\mathcal{A}lg = \{PPO, DQN, SAC, TD3, A2C\}$ denote our set of target algorithms. For each MDP-algorithm pair $(M, a)$, we observe:

- **Static features** $\phi_s(M) \in \mathbb{R}^{d_s}$: structural properties extractable from environment specification
- **Early training signals** $\phi_e(M, a) \in \mathbb{R}^{d_e}$: statistics from the first 10% of training
- **Final performance** $y(M, a) \in \mathbb{R}$: normalized return at training completion

Our goal is to learn a predictor $f_\theta: \mathbb{R}^{d_s} \times \mathcal{A}lg \times \mathbb{R}^{d_e} \rightarrow \mathbb{R}$ such that:

$$\hat{y}(M, a) = f_\theta(\phi_s(M), a, \phi_e(M, a))$$

minimizes prediction error and achieves high correlation with actual performance $y(M, a)$.

### 2.2 Data Collection

#### 2.2.1 Benchmark Selection

We collect training data from four diverse benchmark suites:

| Benchmark | # Environments | Characteristics |
|-----------|---------------|-----------------|
| Atari | 50 games | Discrete actions, visual observations, diverse dynamics |
| MuJoCo | 8 tasks | Continuous control, dense rewards, physics simulation |
| Procgen | 16 games | Procedural generation, generalization challenges |
| BRIDGE | 155 MDPs | Systematic complexity variation, theoretical grounding |

Total: 229 unique environments × 5 algorithms = 1,145 MDP-algorithm pairs.

#### 2.2.2 Feature Extraction

**Static MDP Features** ($d_s = 12$):

1. State space dimensionality: $\log(|\mathcal{S}|)$ or observation dimension
2. Action space size: $\log(|\mathcal{A}|)$ for discrete, dimension for continuous
3. Reward sparsity: fraction of transitions with non-zero reward
4. Reward range: $(\max R - \min R)$
5. Episode length statistics: mean $\mu_L$, standard deviation $\sigma_L$
6. Transition entropy: $H(P) = -\sum_{s,a,s'} P(s'|s,a) \log P(s'|s,a)$ (estimated from samples)
7. State visitation entropy under random policy
8. Action effect magnitude: average state change per action
9. Discount factor $\gamma$
10. Observation type indicator (visual/vector)
11. Action type indicator (discrete/continuous)
12. Environment stochasticity estimate

**Early Training Signals** ($d_e = 11$):

From the first 10% of training (e.g., first 100K of 1M steps):

1-5. Return trajectory: 5 evenly-spaced return measurements
6-7. Gradient norm: mean and standard deviation
8-10. Policy entropy: initial value, final value, linear slope
11. Value loss trajectory slope

**Algorithm Encoding**:

One-hot encoding $e_a \in \{0,1\}^5$ for algorithm identity.

#### 2.2.3 Training Data Generation

For each environment, we run all 5 algorithms using CleanRL standardized implementations with default hyperparameters. Each run uses 3 random seeds, yielding:

$$N_{total} = 229 \times 5 \times 3 = 3,435 \text{ training runs}$$

Performance is normalized per-environment to $[0, 1]$ range:

$$y_{norm}(M, a) = \frac{y(M, a) - y_{min}(M)}{y_{max}(M) - y_{min}(M)}$$

### 2.3 Model Architecture

The LEC predictor employs a modular architecture with three components:

**Component 1: Static Encoder**

$$h_s = \text{MLP}_s(\phi_s(M)) \in \mathbb{R}^{64}$$

A 3-layer MLP with hidden dimensions [64, 128, 64], ReLU activations, and layer normalization.

**Component 2: Algorithm-Conditioned Fusion**

$$h_{sa} = \text{MLP}_{fuse}([h_s; e_a]) \in \mathbb{R}^{64}$$

Concatenates static encoding with algorithm one-hot, processes through 2-layer MLP.

**Component 3: Temporal Signal Encoder**

$$h_e = \text{LSTM}(\phi_e(M, a)) \in \mathbb{R}^{32}$$

Processes early training signals as a sequence, capturing temporal dynamics.

**Final Prediction**:

$$\hat{y} = \text{MLP}_{out}([h_{sa}; h_e]) \in \mathbb{R}$$

Two-layer MLP producing scalar performance prediction.

Total parameters: approximately 50K, enabling efficient training and inference.

### 2.4 Training Procedure

**Loss Function**:

We use a combination of MSE loss and ranking loss to optimize both absolute prediction and relative ordering:

$$\mathcal{L} = \mathcal{L}_{MSE} + \lambda \mathcal{L}_{rank}$$

where:

$$\mathcal{L}_{MSE} = \frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i - y_i)^2$$

$$\mathcal{L}_{rank} = \frac{1}{|\mathcal{P}|}\sum_{(i,j) \in \mathcal{P}} \max(0, -(\hat{y}_i - \hat{y}_j)(y_i - y_j) + \epsilon)$$

with $\mathcal{P}$ being pairs from the same environment and $\lambda = 0.1$, $\epsilon = 0.1$.

**Meta-Training Protocol**:

1. Split data: 70% train, 15% validation, 15% test (stratified by benchmark)
2. Optimizer: AdamW with learning rate $10^{-3}$, weight decay $10^{-4}$
3. Batch size: 64 MDP-algorithm pairs
4. Early stopping: patience of 20 epochs on validation correlation
5. Training budget: approximately 100 GPU-hours on A100

### 2.5 Experimental Design

#### 2.5.1 Primary Experiment: Correlation Analysis

**Hypothesis Test (H-LEC-v1)**:

- $H_1$: LEC achieves $r > 0.70$ on held-out test MDPs
- $H_0$: LEC achieves $r \leq 0.55$ (no meaningful improvement over baselines)

**Statistical Analysis**:

- Compute Pearson correlation $r$ with 95% confidence intervals via Fisher z-transformation
- Sample size: $n \geq 150$ test predictions (30 MDPs × 5 algorithms)
- Significance level: $\alpha = 0.05$ (one-tailed)
- Effect size: Cohen's $q$ for correlation comparison

#### 2.5.2 Baseline Comparisons

| Baseline | Description |
|----------|-------------|
| Effective Horizon | Hand-crafted measure from Laidlaw et al. (2023) |
| Random Forest | Traditional ML on same features |
| Static-Only LEC | LEC without early training signals |
| Single-Domain LEC | LEC trained on one benchmark only |

#### 2.5.3 Ablation Studies

**H-M1 (Static Contribution)**: Compare full LEC vs. early-signals-only model

**H-M2 (Early Signal Value)**: Compare full LEC vs. static-only model

**H-M3 (Cross-Domain Transfer)**: Compare multi-domain vs. single-domain training

#### 2.5.4 Algorithm Selection Evaluation

For each test environment, predict performance for all 5 algorithms and select the predicted best. Measure:

- **Top-1 Accuracy**: Fraction where predicted best = actual best
- **Top-2 Accuracy**: Fraction where actual best is in predicted top 2
- **Regret**: $(y_{best} - y_{selected}) / y_{best}$

Success criterion: Top-1 accuracy > 70%.

### 2.6 Evaluation Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Pearson Correlation | $r = \frac{\sum(y - \bar{y})(\hat{y} - \bar{\hat{y}})}{\sqrt{\sum(y-\bar{y})^2}\sqrt{\sum(\hat{y}-\bar{\hat{y}})^2}}$ | $r > 0.70$ |
| Spearman Correlation | Rank-based correlation | $\rho > 0.65$ |
| RMSE | $\sqrt{\frac{1}{N}\sum(\hat{y} - y)^2}$ | Minimize |
| Algorithm Selection Accuracy | $\frac{1}{|\mathcal{M}|}\sum_M \mathbb{1}[\arg\max_a \hat{y} = \arg\max_a y]$ | $> 70\%$ |
| Mean Regret | $\frac{1}{|\mathcal{M}|}\sum_M \frac{y_{best} - y_{selected}}{y_{best}}$ | $< 0.15$ |

### 2.7 Falsification Criteria

The hypothesis is falsified if:

1. **Primary Failure**: $r \leq 0.55$ on held-out test MDPs
2. **Mechanism Failure**: Early signals provide $\Delta r < 0.05$ improvement over static-only
3. **Transfer Failure**: Multi-domain training underperforms single-domain by $\Delta r > 0.05$

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate:

1. **Superior Correlation**: LEC will achieve Pearson $r > 0.70$ on held-out test MDPs, representing a 40%+ relative improvement over Effective Horizon ($r \approx 0.50$). This improvement stems from capturing algorithm-specific patterns that static measures cannot represent.

2. **Effective Algorithm Selection**: Top-1 accuracy exceeding 70% for identifying the best-performing algorithm, with mean regret below 15%. This enables practitioners to make informed algorithm choices with minimal experimentation.

3. **Validated Causal Mechanism**: Ablation studies will confirm that both static features and early training signals contribute meaningfully, with multi-domain training providing superior generalization.

4. **Interpretable Insights**: Analysis of learned representations will reveal which MDP features most strongly predict algorithm-specific success, potentially identifying new structural properties of theoretical interest.

### 3.2 Scientific Impact

**Bridging Theory and Practice**: LEC provides a concrete bridge between theoretical complexity analysis and practical algorithm selection. By learning what makes problems tractable for specific algorithms, we generate hypotheses that theorists can investigate formally.

**New Problem Characterization**: The learned predictor implicitly defines algorithm-specific complexity measures. Analyzing these learned measures may reveal new structural properties—beyond those currently studied theoretically—that govern practical RL performance.

**Methodology Transfer**: The meta-learning approach for complexity prediction can extend to other machine learning domains facing similar theory-practice gaps, including optimization, bandits, and online learning.

### 3.3 Practical Impact

**Reduced Computational Costs**: By enabling reliable algorithm selection from 10% of training, LEC can reduce the computational burden of algorithm comparison by 5-10×, making RL more accessible to resource-constrained practitioners.

**Accelerated Deployment**: Practitioners can confidently select algorithms for new tasks without exhaustive experimentation, accelerating the deployment of RL in real-world applications.

**Benchmark Design Guidance**: Understanding which MDP features drive algorithm performance can inform the design of more diagnostic benchmarks that systematically probe algorithm capabilities.

### 3.4 Limitations and Future Directions

**Current Limitations**:
- Requires 10% training for early signals (non-zero cost)
- Limited to model-free, single-agent settings
- No formal theoretical guarantees on prediction accuracy

**Future Extensions**:
- Extend to model-based RL and multi-agent settings
- Develop theoretical analysis of learned complexity measures
- Integrate with automated hyperparameter tuning
- Apply to real-world robotics with sim-to-real transfer

### 3.5 Timeline and Resources

| Phase | Duration | Activities |
|-------|----------|------------|
| Data Collection | 2 months | Run all algorithm-environment pairs, extract features |
| Model Development | 1 month | Implement and validate LEC architecture |
| Experiments | 2 months | Primary experiments, ablations, baselines |
| Analysis & Writing | 1 month | Interpretation, paper preparation |

**Computational Resources**: Approximately 500 GPU-hours total (400 for data collection, 100 for training/experiments).

This research directly addresses the workshop's goal of bringing theorists and experimentalists together by providing a data-driven tool that captures practical algorithm-environment interactions while generating insights amenable to theoretical analysis.