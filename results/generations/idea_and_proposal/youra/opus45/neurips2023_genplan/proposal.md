# Research Proposal: Active Inference-Inspired Hierarchical Abstraction for Learning PDDL Domain Models from Experience Traces

## 1. Introduction

### 1.1 Background

Sequential decision-making (SDM) represents one of the most fundamental challenges in artificial intelligence, requiring agents to reason about actions, their consequences, and long-term goals. Two dominant paradigms have emerged to address this challenge, each with complementary strengths and limitations. Deep reinforcement learning (DRL) has demonstrated remarkable success in short-horizon reasoning and control tasks, achieving superhuman performance in games and robotic manipulation. However, DRL methods typically suffer from poor sample efficiency, limited generalization to novel problem instances, and lack of interpretability. In contrast, classical AI planning based on symbolic representations such as the Planning Domain Definition Language (PDDL) offers robust generalization, sample efficiency, and interpretable solutions that transfer effectively across problem instances of varying sizes. The critical limitation of classical planning lies in its dependence on hand-crafted domain models—formal specifications of action preconditions and effects that require significant expertise to design and maintain.

This fundamental gap between data-driven and model-based approaches has motivated substantial research into automated domain model acquisition. Existing approaches fall into two categories: purely symbolic methods that learn action schemas from state transitions but lack differentiability for end-to-end optimization, and neural approaches that learn implicit planning representations but fail to produce interpretable, planner-compatible outputs. Recent advances in neuro-symbolic AI suggest that bridging these paradigms could yield systems that combine the learning capabilities of neural networks with the generalization properties of symbolic planning.

### 1.2 Research Objectives

This research proposes a novel architecture called **Probabilistic Soft-predicate Active Inference (PSAI)** that learns PDDL action schemas directly from planning experience traces. Our primary objectives are:

1. **Develop a hierarchical architecture** inspired by active inference principles that automatically abstracts continuous neural state representations into discrete symbolic predicates suitable for classical planning.

2. **Enable end-to-end differentiable learning** of symbolic planning representations through Gumbel-Softmax relaxation, allowing gradient-based optimization of discrete structures.

3. **Achieve scalable state encoding** through sparse-attention graph neural networks that maintain $O(n \log n)$ complexity while preserving essential relational structure.

4. **Validate generalization capabilities** by demonstrating that learned domain models enable classical planners to solve novel problem instances, including out-of-distribution problems with significantly larger object counts.

### 1.3 Significance

This research addresses a critical barrier to the widespread deployment of classical planning systems: the expertise required to specify domain models. By automating domain model acquisition from experience traces, PSAI would democratize access to powerful planning capabilities. Furthermore, the interpretable symbolic outputs enable verification, debugging, and human oversight—essential properties for safety-critical applications. The theoretical contribution lies in demonstrating how active inference principles can provide a principled framework for bridging continuous neural representations and discrete symbolic structures, with implications beyond planning to broader neuro-symbolic AI research.

---

## 2. Methodology

### 2.1 Problem Formulation

We consider deterministic planning domains where an agent observes state-action-state transitions. Formally, let $\mathcal{D} = \{(s_t, a_t, s_{t+1})\}_{t=1}^{T}$ denote an experience trace, where $s_t \in \mathcal{S}$ represents a state (a set of ground predicates over typed objects), $a_t \in \mathcal{A}$ represents an action, and $s_{t+1}$ is the resulting state. Our goal is to learn a domain model $\mathcal{M} = \langle \mathcal{P}, \mathcal{A}_{schema} \rangle$ consisting of predicate definitions $\mathcal{P}$ and action schemas $\mathcal{A}_{schema}$, where each schema specifies preconditions and effects in PDDL-compatible format.

### 2.2 Architecture Overview

The PSAI architecture operates through four integrated stages, illustrated below:

$$
\text{Experience Traces} \xrightarrow{\text{Stage 1}} \text{Neural Encodings} \xrightarrow{\text{Stage 2}} \text{Hierarchical Abstractions} \xrightarrow{\text{Stage 3}} \text{Soft Predicates} \xrightarrow{\text{Stage 4}} \text{PDDL Output}
$$

### 2.3 Stage 1: Sparse-Attention Graph Neural Network Encoder

States are represented as attributed graphs $G = (V, E, X)$ where vertices $V$ correspond to objects, edges $E$ encode relations, and $X$ contains object features. We employ a sparse-attention GNN that achieves $O(n \log n)$ complexity through top-$k$ attention selection.

**Node Update Rule:**
$$
h_i^{(l+1)} = \sigma\left( W^{(l)} h_i^{(l)} + \sum_{j \in \mathcal{N}_k(i)} \alpha_{ij}^{(l)} W_v^{(l)} h_j^{(l)} \right)
$$

where $\mathcal{N}_k(i)$ denotes the top-$k$ neighbors of node $i$ selected by attention scores:

$$
\alpha_{ij} = \frac{\exp\left( \text{LeakyReLU}\left( a^T [W_q h_i \| W_k h_j] \right) \right)}{\sum_{j' \in \mathcal{N}_k(i)} \exp\left( \text{LeakyReLU}\left( a^T [W_q h_i \| W_k h_{j'}] \right) \right)}
$$

The sparse selection uses approximate nearest neighbor search with $k \in [8, 32]$, enabling scalability to large object counts while preserving essential relational structure.

**State Encoding Output:**
$$
z_s = \text{ReadOut}\left( \{h_i^{(L)}\}_{i \in V} \right) \in \mathbb{R}^d
$$

where ReadOut aggregates node embeddings through attention-weighted pooling.

### 2.4 Stage 2: Active Inference-Inspired Hierarchical Abstraction

Inspired by predictive processing in cognitive science, we implement a three-level hierarchy that progressively abstracts neural encodings into symbolic representations.

**Level 1 - State Predicate Abstraction:**
Given state encoding $z_s$, we compute predicate activation logits:
$$
\ell_p^{(1)} = W_p^{(1)} z_s + b_p^{(1)} \in \mathbb{R}^{|\mathcal{P}| \times |\text{args}|}
$$

**Level 2 - Action Parameter Binding:**
Action parameters are bound through attention over object embeddings:
$$
\beta_{a,k} = \text{softmax}\left( \frac{q_a^{(k)T} H}{\sqrt{d}} \right)
$$

where $q_a^{(k)}$ is the query for the $k$-th parameter of action $a$ and $H = [h_1, \ldots, h_n]$ stacks object embeddings.

**Level 3 - Action Schema Abstraction:**
Action schemas are represented as structured templates with learnable precondition and effect slots:
$$
\text{Schema}(a) = \langle \text{Pre}(a), \text{Eff}^+(a), \text{Eff}^-(a) \rangle
$$

Each component is parameterized by soft predicate assignments learned through the hierarchy.

**Predictive Processing Loss:**
Following active inference principles, each level minimizes prediction error:
$$
\mathcal{L}_{pred} = \sum_{l=1}^{3} \lambda_l \| \mu^{(l)} - f^{(l)}(\mu^{(l+1)}) \|^2
$$

where $\mu^{(l)}$ represents the belief at level $l$ and $f^{(l)}$ is the generative model predicting lower-level representations from higher-level abstractions.

### 2.5 Stage 3: Gumbel-Softmax Relaxation for Differentiable Discrete Learning

To enable gradient flow through discrete predicate selections, we employ Gumbel-Softmax relaxation with temperature annealing.

**Soft Predicate Sampling:**
$$
\tilde{p}_i = \frac{\exp\left( (\ell_i + g_i) / \tau \right)}{\sum_j \exp\left( (\ell_j + g_j) / \tau \right)}
$$

where $g_i \sim \text{Gumbel}(0, 1)$ and $\tau$ is the temperature parameter.

**Temperature Annealing Schedule:**
$$
\tau(t) = \max\left( \tau_{min}, \tau_0 \cdot \exp(-\gamma t) \right)
$$

with $\tau_0 = 1.0$, $\tau_{min} = 0.1$, and $\gamma$ calibrated for convergence over 10k-50k training steps.

**Straight-Through Estimator for Inference:**
During inference, we use hard discretization with straight-through gradients:
$$
p_i^{hard} = \mathbb{1}[i = \arg\max_j \tilde{p}_j]
$$

### 2.6 Stage 4: PDDL Generation

The discretized soft predicates are assembled into valid PDDL syntax through template-based generation.

**Action Schema Template:**
```
(:action {action_name}
  :parameters ({param_list})
  :precondition (and {precond_predicates})
  :effect (and {effect_predicates}))
```

**Predicate Selection:**
For each slot in preconditions and effects, we select predicates where $p_i^{hard} = 1$ and format them with bound parameters from Stage 2.

**Validation:**
Generated PDDL is validated through:
1. Syntactic parsing with standard PDDL parsers
2. Type consistency checking
3. Grounding verification on sample problems

### 2.7 Training Objective

The complete training objective combines multiple losses:

$$
\mathcal{L}_{total} = \mathcal{L}_{recon} + \lambda_1 \mathcal{L}_{pred} + \lambda_2 \mathcal{L}_{plan} + \lambda_3 \mathcal{L}_{entropy}
$$

**Reconstruction Loss:** Ensures learned schemas explain observed transitions:
$$
\mathcal{L}_{recon} = -\sum_{(s,a,s') \in \mathcal{D}} \log P(s' | s, a; \mathcal{M})
$$

**Planning Loss:** Encourages schemas that enable successful planning:
$$
\mathcal{L}_{plan} = -\mathbb{E}_{problem \sim \mathcal{P}_{train}}[\mathbb{1}[\text{Planner}(\mathcal{M}, problem) \text{ succeeds}]]
$$

**Entropy Regularization:** Encourages discrete predicate assignments:
$$
\mathcal{L}_{entropy} = \sum_i H(\tilde{p}_i)
$$

### 2.8 Experimental Design

**Datasets:**
We evaluate on standard IPC benchmark domains:
- **Blocksworld:** 1000 traces, 5-20 blocks (ID), 25-50 blocks (OOD)
- **Logistics:** 1000 traces, 3-8 cities (ID), 10-15 cities (OOD)
- **Gripper:** 1000 traces, 4-12 balls (ID), 15-30 balls (OOD)

Experience traces are generated using optimal planners (Fast Downward) on randomly generated problem instances.

**Baselines:**
1. **Hand-coded PDDL:** Upper bound using expert-designed domain models
2. **ASNets:** Neural network policies trained on planning problems
3. **LOCM/LOCM2:** Classical action model learning from traces
4. **Random Schema:** Randomly generated action schemas (lower bound)

**Evaluation Metrics:**

| Metric | Definition | Target |
|--------|------------|--------|
| Planning Success Rate (ID) | % of in-distribution problems solved | >70% |
| Planning Success Rate (OOD) | % of out-of-distribution problems solved | >50% |
| Schema Semantic Overlap | Jaccard similarity with ground-truth schemas | >80% |
| PDDL Parse Rate | % of generated files passing parser validation | >95% |
| Predicate Convergence | Entropy of soft predicates after annealing | <0.5 |

**Statistical Analysis:**
- Sample size: $n \geq 30$ problems per domain per condition
- Tests: Chi-square for success rates, paired t-tests for continuous metrics
- Significance level: $\alpha = 0.05$ with Bonferroni correction
- Statistical power: 0.8

**Ablation Studies:**
1. Remove hierarchical structure (flat architecture)
2. Replace Gumbel-Softmax with REINFORCE
3. Replace sparse attention with dense attention
4. Vary temperature annealing schedules

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

We anticipate the following outcomes based on our hypothesis and preliminary analysis:

**Primary Outcomes:**
1. PSAI will achieve >70% planning success rate on in-distribution problems across all three benchmark domains, demonstrating that the learned domain models are functionally correct.

2. On out-of-distribution problems (2-3x larger), PSAI will maintain >50% success rate with less than 20% degradation from in-distribution performance, validating the generalization capabilities of symbolic representations.

3. Learned action schemas will exhibit >80% semantic overlap with hand-coded ground truth, indicating that the hierarchical abstraction recovers meaningful symbolic structure.

**Secondary Outcomes:**
1. The sparse-attention GNN will enable scaling to 100+ objects while maintaining planning quality within ±5% of smaller instances.

2. Soft predicates will converge to near-discrete distributions (entropy <0.5) by the end of temperature annealing, confirming that Gumbel-Softmax successfully bridges continuous and discrete representations.

3. >95% of generated PDDL files will pass standard parser validation, demonstrating syntactic correctness.

### 3.2 Theoretical Contributions

This research makes several theoretical contributions to neuro-symbolic AI and automated planning:

1. **Principled Neural-Symbolic Bridge:** We demonstrate that active inference provides a theoretically grounded framework for hierarchical abstraction from continuous to discrete representations, with uncertainty propagation that naturally handles the ambiguity inherent in learning symbolic structures from data.

2. **Differentiable Domain Model Learning:** The combination of Gumbel-Softmax relaxation with hierarchical active inference enables, for the first time, end-to-end gradient-based learning of PDDL-compatible domain models.

3. **Scalable Relational Encoding:** The sparse-attention GNN architecture provides a template for encoding relational structure in planning problems with subquadratic complexity.

### 3.3 Practical Impact

**Democratizing Classical Planning:**
By automating domain model acquisition, PSAI removes a critical barrier to deploying classical planning systems. Domain experts without formal AI training could generate planning capabilities from demonstrations, dramatically expanding the applicability of planning technology.

**Interpretable AI Systems:**
Unlike black-box neural policies, PDDL domain models are human-readable and verifiable. This interpretability is essential for safety-critical applications in robotics, autonomous systems, and healthcare where understanding system behavior is mandatory.

**Transfer and Lifelong Learning:**
Learned symbolic representations enable zero-shot transfer to novel problem instances, supporting lifelong learning scenarios where agents must continuously adapt to new tasks without catastrophic forgetting.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:

1. **Deterministic Domains:** Current formulation assumes deterministic transitions; extending to stochastic domains requires probabilistic PDDL extensions.

2. **Action Template Supervision:** We assume knowledge of action templates (names and arities); fully unsupervised action discovery remains open.

3. **Temporal and Numeric Planning:** STRIPS-style planning excludes temporal constraints and numeric fluents; extending PSAI to PDDL 2.1+ features is future work.

### 3.5 Broader Impact

This research contributes to the workshop's central theme of bridging deep reinforcement learning and classical planning. By demonstrating automated acquisition of symbolic planning representations, we provide a concrete pathway toward AI systems that combine the learning capabilities of neural networks with the generalization and interpretability of symbolic methods. The active inference framework offers a unifying theoretical perspective that may inspire further integration across these historically separate research communities.

---

**Word Count:** ~2,150 words