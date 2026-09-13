# Research Proposal: Distribution-Adaptive Representation Learning for Robust Decision-Focused Optimization Under Temporal Shift

## 1. Introduction

### 1.1 Background

Computational sustainability leverages computational methods to address the United Nations Sustainable Development Goals, spanning domains from energy management to environmental conservation. A critical challenge in these domains is the integration of machine learning predictions with downstream optimization problems—a paradigm known as Decision-Focused Learning (DFL). Unlike traditional two-stage approaches that separately optimize prediction accuracy and decision quality, DFL trains predictive models end-to-end by backpropagating through the optimization layer, directly minimizing decision regret rather than prediction error.

However, sustainability applications present a fundamental challenge that current DFL methods inadequately address: temporal distribution shift. Energy demand patterns shift seasonally and with climate change; water resource availability varies with precipitation cycles; agricultural yields respond to evolving weather patterns and policy interventions. These shifts are not merely statistical nuisances—they fundamentally alter the mapping from features to optimal decisions. A solar energy scheduling system trained on summer data may make catastrophically poor decisions during winter months, not because predictions are inaccurate, but because the relationship between predictions and optimal scheduling decisions has changed.

Current approaches to handling distribution shift in DFL fall into three categories, each with significant limitations. Standard DFL methods ignore distribution shift entirely, assuming stationarity that rarely holds in sustainability domains. Worst-case robust methods like Gen-DFL and 3D-Learning hedge against adversarial shifts through generative sampling or diffusion-based worst-case search, but this conservatism sacrifices average-case performance on the gradual, predictable shifts typical in sustainability applications. Domain adaptation methods enforce prediction-invariant representations, but this invariance may discard precisely the features most relevant to decision quality under shift.

### 1.2 Research Objectives

This research proposes Distribution-Adaptive Representation Learning (DARL), a novel framework that addresses the critical gap between DFL and distribution shift robustness. Our primary objectives are:

1. **Develop a principled framework** for distribution-conditional decision-focused learning that explicitly adapts decision mappings based on detected distribution context while preserving decision-relevant features.

2. **Design and validate** a distribution embedding network that captures shift characteristics from unlabeled data, enabling adaptation without requiring labeled samples from shifted distributions.

3. **Demonstrate empirical superiority** over existing methods on sustainability benchmarks with temporal distribution shift, achieving decision regret degradation ratios below 15% (compared to >20% for standard DFL).

4. **Establish theoretical foundations** for when explicit distribution conditioning outperforms implicit robustness methods, particularly for gradual temporal shifts characteristic of sustainability domains.

### 1.3 Significance

This research directly addresses the CompSust 2023 theme of "Promises and Pitfalls from Theory to Deployment." The gap between benchmark performance and real-world deployment often stems from distribution shift—a system that performs excellently on historical data may fail when deployed in changing conditions. By developing methods that explicitly handle temporal shift, we enable more reliable deployment of optimization systems in sustainability applications.

The significance extends beyond immediate applications. DARL represents a new paradigm for robust decision-focused learning: rather than seeking prediction invariance or worst-case robustness, we optimize for decision quality preservation under principled adaptation. This paradigm shift has implications for any domain where predictions feed into downstream optimization under non-stationary conditions.

## 2. Methodology

### 2.1 Problem Formulation

Consider a predict-then-optimize problem where we observe features $x \in \mathcal{X}$, predict parameters $\hat{c} = f_\theta(x)$ for an optimization problem, and solve:

$$\hat{y} = \arg\min_{y \in \mathcal{Y}} \hat{c}^\top y \quad \text{s.t.} \quad Ay \leq b$$

where $\mathcal{Y}$ is the feasible region defined by constraints $Ay \leq b$. The true optimal decision under ground-truth parameters $c^*$ is $y^* = \arg\min_{y \in \mathcal{Y}} (c^*)^\top y$. Decision regret is defined as:

$$R(x, c^*) = (c^*)^\top \hat{y} - (c^*)^\top y^*$$

In the distribution shift setting, we have access to training data from multiple distributions $\{P_1, P_2, \ldots, P_K\}$ representing different temporal contexts (e.g., seasons, policy regimes). At test time, we encounter data from a potentially novel distribution $P_{\text{test}}$ that may differ from all training distributions.

### 2.2 DARL Architecture

DARL consists of three components: a shared encoder, a distribution embedding network, and a distribution-conditional decision head.

**Shared Encoder $f_\theta$:** Maps input features to a latent representation:
$$z = f_\theta(x) \in \mathbb{R}^{d_z}$$

This encoder is trained end-to-end to extract decision-relevant features shared across distributions.

**Distribution Embedding Network $g_\phi$:** Given a batch of unlabeled samples $\{x_1, \ldots, x_n\}$ from a distribution $P$, computes a distribution embedding:
$$d = g_\phi(\{x_1, \ldots, x_n\}) \in \mathbb{R}^{d_d}$$

We implement $g_\phi$ using a Set Transformer architecture that processes variable-sized sets permutation-invariantly:

$$g_\phi(\{x_i\}) = \text{SetTransformer}(\{f_\theta(x_i)\}_{i=1}^n)$$

The Set Transformer uses induced set attention blocks (ISAB) with $m$ inducing points:
$$\text{ISAB}_m(X) = \text{MAB}(X, \text{MAB}(I, X))$$

where $\text{MAB}$ denotes multihead attention blocks and $I \in \mathbb{R}^{m \times d_z}$ are learnable inducing points.

**Distribution-Conditional Decision Head $h_\psi$:** Produces cost predictions conditioned on both the instance representation and distribution embedding:
$$\hat{c} = h_\psi(z, d) = W_2 \cdot \text{ReLU}(W_1 [z; d] + b_1) + b_2$$

where $[z; d]$ denotes concatenation. The decision is then obtained by solving the optimization problem with predicted costs $\hat{c}$.

### 2.3 Training Objective

The training objective combines decision regret minimization with smoothness regularization:

$$\mathcal{L}(\theta, \phi, \psi) = \sum_{k=1}^K \mathbb{E}_{(x, c^*) \sim P_k} \left[ R_k(x, c^*) \right] + \lambda \cdot \mathcal{L}_{\text{smooth}}$$

where $R_k$ denotes regret computed with distribution embedding $d_k = g_\phi(\mathcal{B}_k)$ for batch $\mathcal{B}_k$ from distribution $P_k$.

The smoothness regularization encourages gradual adaptation across similar distributions:

$$\mathcal{L}_{\text{smooth}} = \sum_{k, k': \text{adjacent}} \| h_\psi(\cdot, d_k) - h_\psi(\cdot, d_{k'}) \|_F^2$$

where "adjacent" refers to temporally consecutive distributions (e.g., consecutive months or seasons).

**Gradient Computation:** We backpropagate through the optimization layer using differentiable optimization techniques. For linear programs, we use the implicit differentiation approach:

$$\frac{\partial y^*}{\partial \hat{c}} = -\left( \frac{\partial^2 \mathcal{L}}{\partial y^2} \right)^{-1} \frac{\partial^2 \mathcal{L}}{\partial y \partial \hat{c}}$$

implemented via cvxpylayers for convex problems or surrogate gradient methods for combinatorial problems.

### 2.4 Data Collection and Benchmark Adaptation

We adapt the Wild-Time benchmark for decision-focused evaluation, creating three sustainability-relevant tasks:

**Task 1: Energy Scheduling (Knapsack Variant)**
- Base dataset: Electricity demand forecasting from Wild-Time
- Optimization: Schedule energy storage charging/discharging to minimize costs
- Temporal shift: Seasonal demand patterns, policy-induced price changes
- Objective: $\min_y c^\top y$ s.t. $\sum_i y_i \leq B$, $y_i \in \{0, 1\}$

**Task 2: Resource Allocation (Assignment Problem)**
- Base dataset: Water treatment demand prediction
- Optimization: Allocate treatment capacity across facilities
- Temporal shift: Seasonal water usage, climate-driven demand
- Objective: $\min_{Y} \sum_{i,j} c_{ij} y_{ij}$ s.t. $\sum_j y_{ij} = 1$, $\sum_i y_{ij} \leq k_j$

**Task 3: Supply Chain Logistics (Shortest Path)**
- Base dataset: Traffic/logistics demand from Wild-Time
- Optimization: Route selection under uncertain travel times
- Temporal shift: Seasonal traffic patterns, infrastructure changes
- Objective: Shortest path with predicted edge costs

For each task, we partition data into $K=12$ monthly distributions, using years 1-3 for training and year 4 for testing with varying shift severity.

### 2.5 Experimental Design

**Baselines:**
1. **Standard DFL**: End-to-end training without shift handling
2. **Two-Stage**: Separate prediction (MSE loss) and optimization
3. **Gen-DFL**: Generative sampling from distribution tails for robustness
4. **3D-Learning**: Diffusion-based worst-case distribution search
5. **DANN-DFL**: Domain-adversarial neural network adapted for DFL

**Ablation Studies:**
- DARL w/o distribution embedder (fixed $d$)
- DARL w/o smoothness regularization ($\lambda = 0$)
- DARL with mean pooling instead of Set Transformer

**Evaluation Metrics:**

*Primary Metric - Decision Regret Degradation Ratio (DRDR):*
$$\text{DRDR} = \frac{\mathbb{E}_{P_{\text{test}}}[R(x, c^*)]}{\mathbb{E}_{P_{\text{train}}}[R(x, c^*)]}$$

*Secondary Metrics:*
- Absolute decision regret on shifted distributions
- Adaptation smoothness: $\text{Var}_k[R_k]$ across shift levels
- Computational overhead: training and inference time ratios

**Statistical Analysis:**
- 5 random seeds per configuration
- Paired t-tests with Bonferroni correction for primary comparisons
- Two-way ANOVA (method × shift severity) for interaction effects
- Bootstrap confidence intervals (1000 resamples) for robustness

**Hyperparameter Selection:**
- Distribution embedding dimension $d_d \in \{16, 32, 64, 128\}$
- Smoothness regularization $\lambda \in \{0.01, 0.1, 1.0\}$
- Batch size for distribution embedding $n \in \{50, 100, 200, 500\}$
- Selection via validation on held-out distributions (months 11-12 of training years)

### 2.6 Implementation Details

- Framework: PyTorch with cvxpylayers for differentiable optimization
- Encoder architecture: 3-layer MLP with 256 hidden units
- Set Transformer: 2 ISAB layers with 32 inducing points
- Optimizer: Adam with learning rate $10^{-3}$, weight decay $10^{-4}$
- Training: 100 epochs with early stopping on validation regret
- Hardware: Single NVIDIA A100 GPU

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome:** DARL will achieve decision regret degradation ratio below 1.15 (i.e., <15% regret increase under shift), compared to >1.20 for standard DFL. This represents a meaningful improvement in deployment reliability for sustainability applications.

**Secondary Outcomes:**
- DARL will outperform worst-case methods (Gen-DFL, 3D-Learning) by >5% on average regret for gradual temporal shifts, demonstrating that explicit adaptation outperforms conservative hedging when shifts are predictable.
- Ablation studies will confirm that the distribution embedding network contributes >10% of the improvement, validating the core architectural innovation.
- Smoothness regularization will reduce regret variance across shift levels by >20%, enabling more predictable performance under deployment.

### 3.2 Theoretical Contributions

This research establishes a new paradigm for robust decision-focused learning: **decision-adaptive representation learning**. Unlike prediction-invariant approaches that may discard decision-relevant information, DARL optimizes for decision quality preservation under principled adaptation. We will provide theoretical analysis characterizing when explicit distribution conditioning outperforms implicit robustness, particularly for smooth temporal shifts.

### 3.3 Practical Impact

**Immediate Applications:**
- Energy grid operators can deploy scheduling systems that adapt to seasonal patterns without retraining
- Water utilities can maintain optimization quality across climate-driven demand shifts
- Supply chain managers can handle policy-induced distribution changes gracefully

**Deployment Pathway:**
Following the CompSust 2023 theme, we will document the path from theory to deployment:
1. Open-source release of DARL implementation and benchmark adaptations
2. Collaboration with sustainability practitioners to validate on real-world data
3. Development of deployment guidelines including data requirements and monitoring protocols

### 3.4 Broader Impact

This research addresses a critical barrier to deploying ML-based optimization in sustainability domains: the brittleness of learned systems under distribution shift. By enabling robust deployment, DARL can accelerate the adoption of computational methods for sustainability challenges, contributing to UN SDGs including affordable clean energy (SDG 7), sustainable cities (SDG 11), and climate action (SDG 13).

The methodology generalizes beyond sustainability to any domain where predictions feed into optimization under non-stationary conditions, including healthcare resource allocation, financial portfolio optimization, and autonomous systems planning.

### 3.5 Limitations and Future Work

**Acknowledged Limitations:**
- DARL requires unlabeled data from shifted distributions during training
- Computational overhead of ~20-30% over standard DFL
- Current formulation assumes optimization structure remains constant across distributions

**Future Directions:**
- Extension to online/streaming settings with continuous adaptation
- Handling of optimization structure changes across distributions
- Integration with uncertainty quantification for risk-aware decisions
- Theoretical analysis of sample complexity for distribution embedding

This research represents a significant step toward reliable deployment of decision-focused learning in sustainability applications, addressing the critical gap between benchmark performance and real-world impact that motivates the CompSust 2023 workshop.