# Research Proposal: Dual Sensitivity Maps for Neural Network Explanation via Lagrangian Perturbation Analysis

## 1. Introduction

### Background

Deep neural networks have achieved remarkable success across diverse domains, from computer vision to natural language processing. However, their "black-box" nature poses significant challenges for understanding why models make specific predictions. This opacity raises concerns in high-stakes applications such as healthcare, autonomous driving, and financial decision-making, where interpretability and accountability are paramount.

Existing explanation methods broadly fall into two categories: gradient-based approaches (e.g., saliency maps, Integrated Gradients) and perturbation-based methods (e.g., LIME, SHAP). Gradient-based methods compute the sensitivity of outputs with respect to inputs but often produce noisy, fragmented explanations that are susceptible to adversarial manipulation. Perturbation-based methods, while more intuitive, lack strong theoretical foundations and can be computationally expensive due to repeated model evaluations.

Duality principles, particularly Lagrangian duality, offer a mathematically rigorous framework for sensitivity analysis that has been extensively utilized in convex optimization. In this context, dual variables (Lagrange multipliers) naturally quantify how the optimal objective value changes in response to constraint perturbations—a property known as the sensitivity theorem. Despite its theoretical elegance, this principle remains largely unexploited in deep learning, primarily because neural networks involve nonconvex optimization landscapes where classical duality results do not directly apply.

Recent advances in constrained neural network training, convex relaxations for neural network verification, and differentiable optimization layers suggest that bridging duality principles with deep learning is increasingly feasible. Works such as DeepLDE (Kim & Kim, 2023) demonstrate the viability of primal-dual methods in neural network training, while research on Lagrangian dual-based theory-guided networks (Rong et al., 2020) shows promise in incorporating constraints meaningfully.

### Research Objectives

This research aims to develop a novel explanation framework called **Dual Sensitivity Maps (DSM)** that leverages Lagrangian duality to provide theoretically grounded, robust, and semantically meaningful explanations for neural network predictions. Our specific objectives are:

1. **Formulate neural network inference as a constrained optimization problem** where input perturbations are bounded by semantically meaningful constraints.

2. **Develop efficient algorithms for computing approximate dual variables** using convex relaxations, local linearizations, and multi-scale aggregation techniques.

3. **Generate Dual Sensitivity Maps** that quantify prediction sensitivity to feature-wise perturbation constraints, interpreting dual multipliers as importance scores.

4. **Validate the framework** through comprehensive experiments comparing DSM against existing explanation methods on standard benchmarks, evaluating robustness, faithfulness, and human interpretability.

### Significance

This research contributes to the ICML Duality Principles workshop's mission by revitalizing duality concepts for modern deep learning applications. By establishing a principled connection between Lagrangian duality and neural network explanation, we address the fundamental gap between classical optimization theory and contemporary machine learning practice. The proposed framework has potential applications beyond explanation, including transfer learning diagnostics, robustness certification, and model adaptation—areas where sensitivity analysis plays a crucial role.

## 2. Methodology

### 2.1 Problem Formulation

Consider a neural network $f_\theta: \mathbb{R}^d \rightarrow \mathbb{R}^K$ parameterized by $\theta$, which maps an input $x \in \mathbb{R}^d$ to a $K$-dimensional output (e.g., class logits). For a given input $x_0$ and target class $y$, we formulate the explanation problem as understanding how the prediction changes under bounded perturbations.

We define the **primal perturbation problem** as:

$$
\begin{aligned}
\min_{\delta} \quad & \mathcal{L}(f_\theta(x_0 + \delta), y) \\
\text{s.t.} \quad & |\delta_i| \leq \epsilon_i, \quad i = 1, \ldots, d
\end{aligned}
$$

where $\mathcal{L}$ is a suitable loss function (e.g., cross-entropy for classification), $\delta \in \mathbb{R}^d$ represents input perturbations, and $\epsilon_i > 0$ are feature-wise perturbation bounds. These bounds can be chosen uniformly or adapted based on semantic feature groupings (e.g., superpixels in images).

The **Lagrangian** associated with this problem is:

$$
L(\delta, \lambda^+, \lambda^-) = \mathcal{L}(f_\theta(x_0 + \delta), y) + \sum_{i=1}^d \lambda_i^+(\delta_i - \epsilon_i) + \sum_{i=1}^d \lambda_i^-(-\delta_i - \epsilon_i)
$$

where $\lambda^+, \lambda^- \in \mathbb{R}_{\geq 0}^d$ are Lagrange multipliers for upper and lower bound constraints, respectively.

By the sensitivity theorem in constrained optimization, the dual variables at optimality measure the rate of change of the optimal objective with respect to constraint relaxation:

$$
\frac{\partial \mathcal{L}^*}{\partial \epsilon_i} \approx -(\lambda_i^{+*} + \lambda_i^{-*})
$$

We interpret the **net dual variable** $\mu_i = \lambda_i^{+*} + \lambda_i^{-*}$ as the sensitivity score for feature $i$: higher values indicate that relaxing the perturbation constraint on feature $i$ would more significantly affect the prediction.

### 2.2 Approximate Dual Computation

Since neural networks are nonconvex, exact duality does not hold, and we cannot directly solve for optimal dual variables. We propose three complementary approaches for computing approximate dual solutions:

#### 2.2.1 Local Linear Approximation (LLA)

We linearize $f_\theta$ around $x_0$ using a first-order Taylor expansion:

$$
f_\theta(x_0 + \delta) \approx f_\theta(x_0) + J_\theta(x_0) \delta
$$

where $J_\theta(x_0) = \nabla_x f_\theta(x_0) \in \mathbb{R}^{K \times d}$ is the Jacobian. For cross-entropy loss with softmax outputs, the linearized problem becomes:

$$
\min_{\delta} \quad c^\top \delta \quad \text{s.t.} \quad -\epsilon \leq \delta \leq \epsilon
$$

where $c = \nabla_x \mathcal{L}(f_\theta(x_0), y)$ is the gradient of the loss. This linear program has a closed-form solution, and dual variables are:

$$
\mu_i^{\text{LLA}} = |c_i|
$$

#### 2.2.2 Convex Relaxation via Interval Bound Propagation (CR-IBP)

For tighter approximations, we employ interval bound propagation to construct convex outer approximations of the neural network's output set. For each layer $l$, we compute lower and upper bounds $[\underline{z}^{(l)}, \overline{z}^{(l)}]$ on activations given input perturbation bounds.

The relaxed dual problem is solved using projected gradient ascent on the Lagrangian:

$$
\max_{\lambda^+, \lambda^- \geq 0} \min_{\delta \in [-\epsilon, \epsilon]} L^{\text{relax}}(\delta, \lambda^+, \lambda^-)
$$

where $L^{\text{relax}}$ uses the convex relaxation of the network.

#### 2.2.3 Multi-Scale Aggregation

To capture sensitivity across different perturbation magnitudes, we solve the dual problem at multiple scales $\{\epsilon^{(s)}\}_{s=1}^S$ with $\epsilon^{(s)} = \alpha^{s-1} \epsilon^{(1)}$ for some scaling factor $\alpha > 1$. The aggregated Dual Sensitivity Map is:

$$
\mu_i^{\text{DSM}} = \sum_{s=1}^S w_s \cdot \mu_i^{(s)}
$$

where $w_s$ are scale-dependent weights (e.g., $w_s \propto 1/s$ to emphasize local sensitivity).

### 2.3 Algorithm Summary

**Algorithm 1: Dual Sensitivity Map Generation**

**Input:** Neural network $f_\theta$, input $x_0$, target class $y$, perturbation scales $\{\epsilon^{(s)}\}_{s=1}^S$, method $\in \{\text{LLA}, \text{CR-IBP}\}$

**Output:** Dual Sensitivity Map $\mu^{\text{DSM}} \in \mathbb{R}^d$

1. Initialize $\mu^{\text{DSM}} = \mathbf{0}$
2. **For** $s = 1$ to $S$ **do**:
   - Set perturbation bound $\epsilon = \epsilon^{(s)}$
   - **If** method = LLA:
     - Compute gradient $c = \nabla_x \mathcal{L}(f_\theta(x_0), y)$
     - Set $\mu^{(s)} = |c|$
   - **Else if** method = CR-IBP:
     - Run interval bound propagation to get relaxed bounds
     - Solve relaxed dual via projected gradient ascent (100 iterations)
     - Extract $\mu^{(s)} = \lambda^{+*} + \lambda^{-*}$
   - Update $\mu^{\text{DSM}} \leftarrow \mu^{\text{DSM}} + w_s \cdot \mu^{(s)}$
3. Normalize: $\mu^{\text{DSM}} \leftarrow \mu^{\text{DSM}} / \|\mu^{\text{DSM}}\|_1$
4. **Return** $\mu^{\text{DSM}}$

### 2.4 Experimental Design

#### 2.4.1 Datasets and Models

- **Image Classification:** CIFAR-10, ImageNet-1k with ResNet-50, VGG-16
- **Text Classification:** SST-2, IMDB with BERT-base
- **Tabular Data:** UCI Adult, COMPAS with MLP

#### 2.4.2 Baseline Methods

- Gradient-based: Vanilla Gradients, Integrated Gradients, SmoothGrad
- Perturbation-based: LIME, SHAP
- Concept-based: TCAV

#### 2.4.3 Evaluation Metrics

1. **Faithfulness (Deletion/Insertion AUC):** Measure prediction change when progressively removing or inserting features ranked by importance scores.

2. **Robustness Score:** Quantify explanation stability under small input perturbations:
$$
R(\mu) = 1 - \mathbb{E}_{\eta \sim \mathcal{N}(0, \sigma^2 I)}\left[\frac{\|\mu(x) - \mu(x+\eta)\|_1}{\|\mu(x)\|_1}\right]
$$

3. **Human Agreement:** Conduct user studies where participants rate explanation quality on Likert scales, measuring alignment with human intuition.

4. **Adversarial Manipulation Resistance:** Evaluate explanation change under adversarial attacks specifically designed to manipulate explanations without changing predictions.

#### 2.4.4 Domain-Shift Sensitivity Extension

We extend DSM to diagnose model adaptation by defining domain-shift constraints:

$$
\|x - x_0\|_{\Sigma} \leq \tau
$$

where $\Sigma$ captures the covariance structure of the target domain. The resulting dual variables indicate which features are most sensitive to distribution shift.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Novel Explanation Framework:** We expect DSM to provide explanations that are more faithful to model behavior than gradient-based methods, as measured by deletion/insertion metrics. The multi-scale aggregation should capture both local and global sensitivity patterns.

2. **Improved Robustness:** Preliminary theoretical analysis suggests that dual variables are more stable than raw gradients under small input perturbations, as they integrate information over the constraint boundary rather than at a single point. We anticipate 20-30% improvement in robustness scores compared to gradient-based baselines.

3. **Theoretical Contributions:** We will establish bounds on the duality gap for our convex relaxation approach, providing guarantees on how well the approximate dual variables reflect true sensitivity. This connects neural network explanation to the rich theory of Lagrangian duality.

4. **Practical Tools:** We will release an open-source library implementing DSM with efficient GPU-accelerated computation, enabling practitioners to generate explanations for large-scale models.

### Broader Impact

**Scientific Impact:** This research revitalizes the application of duality principles in deep learning, potentially inspiring follow-up work on dual-based regularization, constrained learning, and robust optimization for neural networks.

**Societal Impact:** More reliable explanations contribute to trustworthy AI systems. In healthcare, DSM could help clinicians understand diagnostic predictions; in finance, it could support regulatory compliance by providing auditable explanations; in criminal justice, it could identify potential biases in risk assessment models.

**Methodological Extensions:** The framework naturally extends to:
- **Transfer learning:** Identifying features most sensitive to domain shift
- **Fairness analysis:** Measuring sensitivity to protected attributes
- **Model debugging:** Detecting spurious correlations through sensitivity patterns

By bridging classical optimization theory with modern deep learning, this research contributes to a more principled foundation for explainable AI, addressing a critical need as machine learning systems are increasingly deployed in consequential decision-making contexts.