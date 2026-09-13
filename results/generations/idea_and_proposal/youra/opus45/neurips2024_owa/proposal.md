# Research Proposal: Adaptive Orthogonal Subspace Transformers for Compositional Generalization in Open-World Agents

## 1. Introduction

### 1.1 Background

The development of artificial intelligence has witnessed remarkable achievements in specialized domains, from game-playing systems that surpass human champions to language models capable of sophisticated reasoning. However, the real world presents a fundamentally different challenge: it is open-ended, dynamic, and requires agents to simultaneously reason about abstract concepts while making concrete decisions in novel situations. Open-world environments—characterized by infinite task diversity, dynamic rule changes, and the need for continuous learning—represent the next frontier for AI agent development.

A critical capability for open-world agents is the seamless integration of reasoning (e.g., question answering, logical inference, dialogue) and decision-making (e.g., planning, control, action selection). Human cognition naturally interleaves these processes: we reason about our goals, make decisions based on that reasoning, observe outcomes, and update our understanding accordingly. Yet current AI architectures struggle to achieve this integration effectively, particularly when confronted with novel combinations of reasoning and decision tasks.

The dominant paradigm of unified transformer architectures, while powerful, suffers from a fundamental limitation: representational interference. When reasoning and decision-making processes compete for the same embedding space, the model experiences catastrophic forgetting during continual learning and exhibits poor compositional transfer to novel task combinations. Empirical observations suggest that standard unified transformers achieve only approximately 30% zero-shot accuracy on novel task combinations, severely limiting their utility in open-world settings.

Intriguingly, neuroscience research provides a potential solution. Studies of the prefrontal cortex reveal that biological neural systems employ orthogonal neural codes to prevent memory interference while maintaining the ability to integrate information across cognitive domains. Park et al. (2025) demonstrated that prefrontal neurons encode different task contexts in geometrically orthogonal subspaces, enabling rapid switching between tasks without interference. This biological principle remains largely unexploited in artificial neural network design.

### 1.2 Research Objectives

This research proposes Adaptive Orthogonal Subspace Transformers (A-OST), a novel architecture that separates reasoning and decision representations into geometrically-orthogonal subspaces while enabling controlled information sharing. Our primary objectives are:

1. **Develop the A-OST architecture** that implements SVD-based orthogonal projection layers with tunable constraint strength, enabling principled separation of reasoning and decision representations.

2. **Validate the compositional generalization hypothesis** that orthogonal subspace separation improves zero-shot transfer to novel task combinations by more than 40% compared to standard unified transformers.

3. **Establish the causal mechanism** linking orthogonal separation to reduced representational interference and improved compositional transfer through systematic ablation studies.

4. **Create Dynamic GameBench**, a novel evaluation benchmark featuring mid-episode rule changes to rigorously test open-world agent capabilities.

### 1.3 Significance

This research addresses fundamental questions about building open-world agents that can generalize compositionally across reasoning and decision-making tasks. The significance extends across multiple dimensions:

**Scientific Contribution:** We establish geometric constraints as a principled approach for building compositionally generalizable agents, bridging insights from neuroscience to artificial intelligence architecture design.

**Practical Impact:** Open-world agents with improved compositional generalization will enable more robust AI systems for robotics, game AI, workflow automation, and embodied AI applications where novel task combinations are the norm rather than the exception.

**Methodological Advancement:** The Dynamic GameBench evaluation framework provides the research community with a rigorous tool for measuring compositional generalization in open-world settings.

## 2. Methodology

### 2.1 Architecture Design

#### 2.1.1 Overview

The A-OST architecture extends standard transformer models with three key components: (1) a learned token role classifier, (2) SVD-based orthogonal projection layers, and (3) gated cross-subspace attention bridges. The architecture operates on the principle that reasoning and decision tokens should occupy geometrically orthogonal subspaces while maintaining controlled interaction pathways.

#### 2.1.2 Token Role Classification

Given an input sequence of tokens $\mathbf{X} = [\mathbf{x}_1, \mathbf{x}_2, ..., \mathbf{x}_n]$ with embeddings $\mathbf{H} \in \mathbb{R}^{n \times d}$, we first classify each token into reasoning (R), decision (D), or hybrid (H) roles using a learned classifier:

$$p(r_i | \mathbf{h}_i) = \text{softmax}(\mathbf{W}_c \mathbf{h}_i + \mathbf{b}_c)$$

where $r_i \in \{R, D, H\}$, $\mathbf{W}_c \in \mathbb{R}^{3 \times d}$, and $\mathbf{b}_c \in \mathbb{R}^3$. The classifier is trained end-to-end with the main architecture using auxiliary supervision from task labels.

For hybrid tokens, we compute soft assignments:

$$\alpha_i^R = p(R | \mathbf{h}_i), \quad \alpha_i^D = p(D | \mathbf{h}_i)$$

#### 2.1.3 SVD-Based Orthogonal Projection

We construct orthogonal projection matrices using Singular Value Decomposition. Let $\mathbf{U} \in \mathbb{R}^{d \times d}$ be an orthonormal basis obtained from SVD of a learned weight matrix. We partition $\mathbf{U}$ into reasoning and decision subspaces:

$$\mathbf{U} = [\mathbf{U}_R | \mathbf{U}_D]$$

where $\mathbf{U}_R \in \mathbb{R}^{d \times d_R}$ and $\mathbf{U}_D \in \mathbb{R}^{d \times d_D}$ with $d_R + d_D = d$.

The projection operators are defined as:

$$\mathbf{P}_R = \mathbf{U}_R \mathbf{U}_R^\top, \quad \mathbf{P}_D = \mathbf{U}_D \mathbf{U}_D^\top$$

By construction, $\mathbf{P}_R \mathbf{P}_D = \mathbf{0}$, ensuring geometric orthogonality.

To enable adaptive constraint strength, we introduce a softness parameter $\lambda \in [0, 1]$:

$$\tilde{\mathbf{P}}_R = \lambda \mathbf{P}_R + (1 - \lambda) \mathbf{I}, \quad \tilde{\mathbf{P}}_D = \lambda \mathbf{P}_D + (1 - \lambda) \mathbf{I}$$

When $\lambda = 1$, projections are strictly orthogonal; when $\lambda = 0$, the architecture reduces to a standard transformer.

Token representations are projected as:

$$\mathbf{h}_i^R = \tilde{\mathbf{P}}_R \mathbf{h}_i, \quad \mathbf{h}_i^D = \tilde{\mathbf{P}}_D \mathbf{h}_i$$

For hybrid tokens:

$$\mathbf{h}_i^{\text{proj}} = \alpha_i^R \mathbf{h}_i^R + \alpha_i^D \mathbf{h}_i^D$$

#### 2.1.4 Gated Cross-Subspace Attention

To enable controlled information flow between subspaces without reintroducing interference, we implement gated cross-subspace attention. Let $\mathbf{H}^R$ and $\mathbf{H}^D$ denote the collections of reasoning and decision token representations.

The cross-subspace attention from reasoning to decision is computed as:

$$\mathbf{A}_{R \rightarrow D} = \text{softmax}\left(\frac{\mathbf{Q}_D (\mathbf{K}_R)^\top}{\sqrt{d_k}}\right) \mathbf{V}_R$$

where $\mathbf{Q}_D = \mathbf{H}^D \mathbf{W}_Q^{R \rightarrow D}$, $\mathbf{K}_R = \mathbf{H}^R \mathbf{W}_K^{R \rightarrow D}$, $\mathbf{V}_R = \mathbf{H}^R \mathbf{W}_V^{R \rightarrow D}$.

A learned gating mechanism controls the strength of cross-subspace information flow:

$$g_{R \rightarrow D} = \sigma(\mathbf{w}_g^\top [\mathbf{H}^R; \mathbf{H}^D] + b_g)$$

The final update to decision representations is:

$$\mathbf{H}^D \leftarrow \mathbf{H}^D + g_{R \rightarrow D} \cdot \mathbf{A}_{R \rightarrow D}$$

Symmetric operations define $\mathbf{A}_{D \rightarrow R}$ and $g_{D \rightarrow R}$.

#### 2.1.5 Training Objective

The total training loss combines task-specific losses with orthogonality regularization:

$$\mathcal{L} = \mathcal{L}_{\text{task}} + \beta \mathcal{L}_{\text{orth}} + \gamma \mathcal{L}_{\text{class}}$$

where:

$$\mathcal{L}_{\text{orth}} = \sum_{i,j: r_i \neq r_j} \max(0, \cos(\mathbf{h}_i^{\text{proj}}, \mathbf{h}_j^{\text{proj}}) - \tau)$$

penalizes cosine similarity above threshold $\tau$ between tokens of different roles, and $\mathcal{L}_{\text{class}}$ is cross-entropy loss for token role classification.

### 2.2 Dynamic GameBench Design

#### 2.2.1 Benchmark Overview

We develop Dynamic GameBench, a novel evaluation framework for testing compositional generalization in open-world agents. The benchmark features:

1. **Base Games:** A collection of 10 diverse game environments spanning navigation, resource management, combat, and puzzle-solving.

2. **Reasoning Tasks:** 15 reasoning task types including spatial reasoning, causal inference, counterfactual reasoning, and multi-step planning.

3. **Mid-Episode Rule Changes:** At random intervals during episodes, game rules change (e.g., gravity reversal, resource value changes, new obstacles), requiring agents to adapt their reasoning and decision-making on-the-fly.

4. **Compositional Splits:** Training covers 60% of game-reasoning combinations; testing evaluates zero-shot transfer to held-out combinations.

#### 2.2.2 Task Composition Matrix

We define a composition matrix $\mathbf{C} \in \{0, 1\}^{10 \times 15}$ where $C_{ij} = 1$ indicates game $i$ paired with reasoning task $j$. Training uses combinations where $C_{ij} = 1$; evaluation tests combinations where $C_{ij} = 0$.

### 2.3 Experimental Design

#### 2.3.1 Model Configurations

**Base Architecture:** LLaMA-7B transformer backbone with A-OST modifications.

**Experimental Conditions:**
- **A-OST-Full:** Complete architecture with $\lambda = 0.7$, subspace ratio 0.5, gate strength 0.3
- **A-OST-Strict:** $\lambda = 1.0$ (strict orthogonality)
- **A-OST-Soft:** $\lambda = 0.5$ (soft orthogonality)
- **Baseline-Unified:** Standard transformer without orthogonal constraints
- **Baseline-Modular:** Separate reasoning and decision modules with no interaction
- **Baseline-MoE:** Mixture-of-experts architecture

#### 2.3.2 Ablation Studies

**λ Sweep:** Test $\lambda \in \{0.0, 0.3, 0.5, 0.7, 0.9, 1.0\}$ to identify optimal constraint strength.

**Subspace Ratio Sweep:** Test reasoning:decision ratios of 0.3:0.7, 0.5:0.5, 0.7:0.3.

**Gate Strength Sweep:** Test cross-subspace attention gate strengths of 0.1, 0.3, 0.5.

**Component Ablations:**
- Remove token classifier (random assignment)
- Remove orthogonal projection (standard attention)
- Remove cross-subspace attention (complete isolation)

#### 2.3.3 Evaluation Metrics

**Primary Metrics:**

1. **Compositional Transfer Accuracy (CTA):** Zero-shot accuracy on novel task combinations in Dynamic GameBench.

2. **Representation Interference Score (RIS):** Average cosine similarity between reasoning and decision token representations:
$$\text{RIS} = \frac{1}{|R| \cdot |D|} \sum_{i \in R} \sum_{j \in D} \cos(\mathbf{h}_i, \mathbf{h}_j)$$

3. **Adaptation Data Efficiency (ADE):** Number of samples required to reach 90% of baseline performance on new decision domains.

**Secondary Metrics:**

4. **Token Classification Accuracy:** Accuracy of learned role classifier.

5. **Cross-Subspace Information Flow:** Measured via attention weight analysis.

6. **Computational Overhead:** Training time and inference latency compared to baseline.

#### 2.3.4 Statistical Analysis

**Sample Size:** $n \geq 25$ independent training runs per condition.

**Statistical Tests:** 
- Paired t-tests for primary comparisons ($\alpha = 0.05$, one-tailed)
- Effect size: Cohen's d > 0.5 required for practical significance
- Bonferroni correction for multiple comparisons

**Reporting:** Mean, standard deviation, 95% confidence intervals, p-values, and effect sizes.

### 2.4 Implementation Details

**Training Infrastructure:** 8× NVIDIA A100 GPUs, estimated 2 weeks training time per configuration.

**Hyperparameters:**
- Learning rate: $3 \times 10^{-5}$ with cosine decay
- Batch size: 32
- Orthogonality loss weight $\beta = 0.1$
- Classification loss weight $\gamma = 0.05$
- Orthogonality threshold $\tau = 0.3$

**Data:** Standard agent training mixture including instruction-following, reasoning benchmarks, and decision-making trajectories.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate the following outcomes:

**Primary Prediction (P1):** A-OST will achieve >60% zero-shot accuracy on novel task combinations in Dynamic GameBench, compared to approximately 30% for standard unified transformers. This represents a >40% absolute improvement in compositional transfer.

**Secondary Prediction (P2):** Orthogonal projection will reduce the Representation Interference Score to <0.3, compared to >0.7 in standard transformers, validating the mechanism of interference reduction.

**Secondary Prediction (P3):** A-OST will require 40% fewer adaptation samples to reach 90% baseline performance when transferring to novel decision domains, demonstrating improved data efficiency.

**Optimal Configuration:** We predict $\lambda \in [0.5, 0.9]$ will yield optimal performance, with strict orthogonality ($\lambda = 1.0$) potentially limiting necessary interactions and no orthogonality ($\lambda = 0$) providing no benefit.

### 3.2 Falsification Criteria

The hypothesis will be rejected if:
1. Compositional transfer accuracy remains ≤40% (primary failure)
2. Interference score remains >0.5 despite orthogonal constraints (mechanism failure)
3. No advantage observed on any dimension compared to baselines (comparative failure)

### 3.3 Scientific Impact

This research establishes geometric constraints as a principled approach for building compositionally generalizable open-world agents. The key scientific contributions include:

1. **Theoretical Framework:** Formalizing the relationship between representational geometry and compositional generalization in neural networks.

2. **Architectural Innovation:** Demonstrating that neuroscience-inspired orthogonal coding principles can be effectively implemented in transformer architectures.

3. **Evaluation Methodology:** Providing Dynamic GameBench as a rigorous tool for measuring compositional generalization under dynamic conditions.

### 3.4 Practical Applications

The A-OST architecture enables more robust AI agents across multiple domains:

**Robotics:** Robots that can reason about novel object configurations while adapting manipulation strategies in real-time.

**Game AI:** Game-playing agents that generalize to new game modes and rule variations without retraining.

**Workflow Automation:** LLM agents that compose reasoning and action capabilities for novel automation tasks.

**Embodied AI:** Agents that navigate and interact in dynamic environments requiring continuous reasoning-decision integration.

### 3.5 Broader Impact

By improving compositional generalization, this research contributes to the development of AI systems that are more robust, adaptable, and aligned with human expectations of intelligent behavior. The explicit separation of reasoning and decision processes also enhances interpretability, as researchers can analyze each subspace independently to understand agent behavior.

### 3.6 Limitations and Future Directions

**Current Limitations:**
- Token classification accuracy bounds overall performance
- Computational overhead of approximately 10-15% during training
- Evaluation limited to game-based environments

**Future Directions:**
- Extension to larger models (70B+ parameters) with sparse projection implementations
- Application to real-world robotics and embodied AI settings
- Investigation of hierarchical orthogonal subspaces for more complex task decompositions
- Integration with continual learning frameworks for lifelong open-world agents

This research represents a significant step toward building AI agents capable of human-like compositional generalization in open-world environments, bridging fundamental insights from neuroscience with practical advances in machine learning architecture design.