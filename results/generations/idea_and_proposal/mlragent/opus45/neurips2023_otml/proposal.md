# Research Proposal: Adaptive Cost Learning for Optimal Transport in Cross-Domain Few-Shot Learning

## 1. Introduction

### Background

Optimal transport (OT) has emerged as a powerful mathematical framework for comparing and aligning probability distributions, with applications spanning generative modeling, domain adaptation, and computational biology. The fundamental OT problem seeks to find the most efficient way to transform one distribution into another, where efficiency is measured through a cost function that quantifies the expense of moving mass between locations. While classical OT theory predominantly relies on pre-defined cost functions such as Euclidean distance or squared Euclidean distance, these fixed metrics often fail to capture the complex semantic relationships inherent in high-dimensional feature spaces encountered in modern machine learning applications.

Cross-domain few-shot learning presents a particularly challenging scenario where models must rapidly adapt to novel tasks in target domains using only a handful of labeled examples, while the source and target domains may exhibit significant distributional shift. In such settings, the choice of cost function for OT-based alignment becomes critically important—a poorly chosen cost function can lead to semantically meaningless alignments that hinder rather than help knowledge transfer. Current approaches to this challenge either employ fixed geometric metrics that ignore semantic structure, or require substantial labeled data to learn appropriate cost functions, creating a fundamental tension in data-scarce scenarios.

Recent advances in inverse optimal transport (Ma et al., 2020) have demonstrated the feasibility of learning cost functions from observed transport plans, while neural optimal transport methods (Asadulaev et al., 2022) have extended OT computation to general cost functionals. However, these approaches are not designed for few-shot scenarios where task-specific adaptation must occur with minimal data. Similarly, while meta-learning frameworks like ALFA have shown promise in adapting hyperparameters across tasks, the specific challenge of meta-learning OT cost functions for cross-domain alignment remains unexplored.

### Research Objectives

This research proposes **Meta-Cost Optimal Transport (MC-OT)**, a novel framework that meta-learns task-adaptive cost functions for optimal transport-based domain alignment in few-shot learning settings. Our specific objectives are:

1. To develop a parameterized cost network architecture that generates instance-pair transport costs conditioned on task-specific context, enabling rapid adaptation to new domains with minimal examples.

2. To formulate a principled bi-level optimization framework where outer-loop meta-learning of cost function parameters is coupled with inner-loop entropic optimal transport for feature alignment.

3. To design regularization mechanisms that encourage learned cost functions to satisfy desirable metric properties while maintaining flexibility for semantic cost learning.

4. To empirically validate the framework across diverse cross-domain few-shot learning benchmarks and analyze the interpretability of learned cost structures.

### Significance

This research addresses a critical gap at the intersection of optimal transport theory and meta-learning, with significant implications for data-scarce applications. By enabling OT-based methods to automatically discover appropriate cost functions from limited supervision, MC-OT can unlock principled distribution alignment in domains where labeled data is expensive or scarce, such as medical imaging, rare language translation, and scientific discovery applications. Furthermore, the interpretable nature of learned cost functions can provide insights into cross-domain semantic relationships, advancing our understanding of transfer learning dynamics.

## 2. Methodology

### 2.1 Problem Formulation

Consider a meta-learning setup with a distribution over tasks $p(\mathcal{T})$. Each task $\mathcal{T}_i$ consists of a support set $\mathcal{S}_i = \{(x_j^s, y_j^s)\}_{j=1}^{K}$ with $K$ examples per class from the source domain, and a query set $\mathcal{Q}_i = \{(x_j^q, y_j^q)\}_{j=1}^{M}$ from a potentially shifted target domain. Our goal is to learn a cost function parameterization that enables effective OT-based alignment across domains for rapid few-shot adaptation.

Let $\mu = \frac{1}{n}\sum_{i=1}^{n}\delta_{x_i^s}$ and $\nu = \frac{1}{m}\sum_{j=1}^{m}\delta_{x_j^q}$ denote the empirical distributions over source and target features, respectively. The entropic regularized optimal transport problem is:

$$\min_{\mathbf{P} \in \Pi(\mu, \nu)} \langle \mathbf{C}, \mathbf{P} \rangle - \epsilon H(\mathbf{P})$$

where $\Pi(\mu, \nu)$ is the set of valid transport plans with marginals $\mu$ and $\nu$, $\mathbf{C} \in \mathbb{R}^{n \times m}$ is the cost matrix, $\epsilon > 0$ is the entropic regularization parameter, and $H(\mathbf{P}) = -\sum_{ij} P_{ij}(\log P_{ij} - 1)$ is the entropy.

### 2.2 Meta-Cost Network Architecture

We introduce a cost network $c_\theta: \mathcal{X} \times \mathcal{X} \times \mathbb{R}^d \rightarrow \mathbb{R}^+$ that computes transport costs between feature pairs, conditioned on a task context vector. The architecture comprises three components:

**Task Context Encoder:** Given support set $\mathcal{S}$, we compute a task context vector:
$$\mathbf{z}_\mathcal{T} = \frac{1}{|\mathcal{S}|}\sum_{(x,y) \in \mathcal{S}} g_\phi(\text{Enc}(x), \text{Emb}(y))$$

where $\text{Enc}(\cdot)$ is a pre-trained feature encoder, $\text{Emb}(\cdot)$ is a learnable label embedding, and $g_\phi$ is a small MLP that fuses feature and label information.

**Pairwise Feature Processor:** For each pair of source feature $\mathbf{f}_i^s = \text{Enc}(x_i^s)$ and target feature $\mathbf{f}_j^q = \text{Enc}(x_j^q)$, we compute:
$$\mathbf{h}_{ij} = [\mathbf{f}_i^s; \mathbf{f}_j^q; \mathbf{f}_i^s - \mathbf{f}_j^q; \mathbf{f}_i^s \odot \mathbf{f}_j^q]$$

where $[\cdot;\cdot]$ denotes concatenation and $\odot$ is element-wise multiplication.

**Context-Conditioned Cost Head:** The final cost is computed as:
$$c_\theta(x_i^s, x_j^q, \mathbf{z}_\mathcal{T}) = \text{softplus}\left(\text{MLP}_\theta([\mathbf{h}_{ij}; \mathbf{z}_\mathcal{T}])\right)$$

The softplus activation ensures non-negativity of costs.

### 2.3 Bi-Level Optimization Framework

MC-OT employs a bi-level optimization structure. The inner loop solves entropic OT given the current cost function, while the outer loop updates cost function parameters across tasks.

**Inner Loop (OT Computation):** Given cost matrix $\mathbf{C}^{(\theta, \mathcal{T})}$ where $C_{ij} = c_\theta(x_i^s, x_j^q, \mathbf{z}_\mathcal{T})$, we solve entropic OT using the Sinkhorn algorithm:

$$\mathbf{P}^* = \text{diag}(\mathbf{u}) \mathbf{K} \text{diag}(\mathbf{v})$$

where $\mathbf{K} = \exp(-\mathbf{C}^{(\theta, \mathcal{T})}/\epsilon)$ and $(\mathbf{u}, \mathbf{v})$ are obtained through iterative scaling:
$$\mathbf{u}^{(t+1)} = \mathbf{a} / (\mathbf{K}\mathbf{v}^{(t)}), \quad \mathbf{v}^{(t+1)} = \mathbf{b} / (\mathbf{K}^\top\mathbf{u}^{(t+1)})$$

with $\mathbf{a}, \mathbf{b}$ being the marginal constraints.

**Feature Alignment via OT:** Using the optimal transport plan $\mathbf{P}^*$, we compute aligned target features:
$$\tilde{\mathbf{f}}_j^q = \sum_{i=1}^{n} \frac{P_{ij}^*}{\sum_{i'} P_{i'j}^*} \mathbf{f}_i^s$$

**Classification Loss:** We train a task-specific classifier $h_\psi$ on aligned features and compute:
$$\mathcal{L}_{\text{cls}}(\theta, \psi; \mathcal{T}) = \frac{1}{|\mathcal{Q}|}\sum_{(x_j^q, y_j^q) \in \mathcal{Q}} \ell_{\text{CE}}(h_\psi(\tilde{\mathbf{f}}_j^q), y_j^q)$$

**Outer Loop (Meta-Learning):** The cost network parameters are updated by aggregating gradients across sampled tasks:
$$\theta \leftarrow \theta - \alpha \nabla_\theta \mathbb{E}_{\mathcal{T} \sim p(\mathcal{T})}[\mathcal{L}_{\text{cls}}(\theta, \psi^*(\theta); \mathcal{T})]$$

### 2.4 Metric Regularization

To encourage learned costs to exhibit desirable metric properties, we introduce regularization losses:

**Symmetry Regularization:**
$$\mathcal{L}_{\text{sym}} = \mathbb{E}_{x, x'}[|c_\theta(x, x', \mathbf{z}) - c_\theta(x', x, \mathbf{z})|]$$

**Triangle Inequality Relaxation:**
$$\mathcal{L}_{\text{tri}} = \mathbb{E}_{x, x', x''}[\max(0, c_\theta(x, x'', \mathbf{z}) - c_\theta(x, x', \mathbf{z}) - c_\theta(x', x'', \mathbf{z}) - \delta)]$$

where $\delta > 0$ is a slack parameter allowing soft violations.

**Identity Regularization:**
$$\mathcal{L}_{\text{id}} = \mathbb{E}_{x}[c_\theta(x, x, \mathbf{z})^2]$$

The total training objective becomes:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{cls}} + \lambda_1 \mathcal{L}_{\text{sym}} + \lambda_2 \mathcal{L}_{\text{tri}} + \lambda_3 \mathcal{L}_{\text{id}}$$

### 2.5 Experimental Design

**Datasets:** We evaluate on established cross-domain few-shot learning benchmarks:
- **Meta-Dataset:** A large-scale benchmark comprising 10 diverse image datasets
- **BSCD-FSL:** Biological/cross-domain few-shot learning benchmark with significant domain shifts
- **Mini-ImageNet → CUB:** Standard cross-domain transfer setup

**Baselines:** We compare against:
- Fixed-cost OT methods (Euclidean, cosine)
- DeepJDOT (Damodaran et al., 2018)
- Learned inverse OT (Ma et al., 2020)
- Standard meta-learning methods (MAML, ProtoNet)
- OT-based few-shot methods (OTAT)

**Evaluation Metrics:**
- Few-shot classification accuracy (1-shot, 5-shot)
- 95% confidence intervals over 600 episodes
- Wasserstein distance reduction after alignment
- Cost function interpretability analysis via t-SNE visualization

**Implementation Details:** We use a ResNet-18 backbone pre-trained on ImageNet. The cost network consists of 3-layer MLPs with 256 hidden units. Meta-training uses Adam optimizer with learning rate $10^{-4}$, batch size of 4 tasks, and 50 inner Sinkhorn iterations with $\epsilon = 0.1$.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Few-Shot Accuracy:** We anticipate MC-OT to achieve 3-5% absolute improvement in cross-domain few-shot classification accuracy compared to fixed-cost OT baselines, with the largest gains observed under significant domain shift.

2. **Interpretable Cost Structures:** Analysis of learned cost matrices should reveal semantically meaningful patterns—features from semantically related classes should exhibit lower transport costs, even across domain boundaries.

3. **Convergence Analysis:** We expect to demonstrate stable bi-level optimization convergence, with learned costs progressively better capturing cross-domain semantic structure over meta-training.

4. **Ablation Insights:** Systematic ablations will quantify the contribution of task-context conditioning, metric regularization, and architectural choices.

### Broader Impact

This research advances the integration of optimal transport theory with meta-learning, establishing principled methods for data-efficient distribution alignment. The immediate applications include:

- **Medical Imaging:** Enabling cross-institutional diagnostic model adaptation with limited patient data while respecting privacy constraints.
- **Low-Resource NLP:** Facilitating translation and understanding for rare languages where parallel corpora are scarce.
- **Scientific Discovery:** Supporting few-shot classification in domains like drug discovery and materials science where labeled examples are expensive.

Theoretically, MC-OT provides a template for learning other OT components (regularization strength, marginal constraints) in a task-adaptive manner, opening avenues for fully adaptive optimal transport in machine learning. The interpretability of learned cost functions also contributes to the broader goal of understanding transfer learning dynamics and domain relationships.