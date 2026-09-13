# Research Proposal: Compositional Skill Libraries with Symbolic Abstractions for Zero-Shot Policy Transfer

## 1. Introduction

### Background

Sequential decision-making (SDM) lies at the heart of intelligent behavior, requiring agents to reason about actions, their consequences, and long-term goals. While humans excel at generalizing from few examples and transferring learned skills to novel situations, artificial agents continue to struggle with these capabilities. Deep reinforcement learning (RL) has achieved remarkable success in specific domains—from game playing to robotic manipulation—yet these successes often rely on extensive training data and fail to generalize beyond narrow task distributions. Even minor environmental changes can necessitate complete retraining, limiting the practical deployment of learned policies.

The complementary strengths of classical AI planning and modern deep learning suggest a promising path forward. Symbolic planning methods, particularly those based on the Planning Domain Definition Language (PDDL), offer robust generalization through abstract state representations and compositional action models. These systems can solve novel problem instances within a domain without additional learning. However, they require hand-crafted domain models and struggle with perceptual complexity and continuous control. Conversely, deep RL excels at learning from raw sensory inputs and handling continuous action spaces but lacks the systematic compositionality that enables broad generalization.

Recent work has begun bridging these paradigms. Hierarchical reinforcement learning decomposes policies into reusable sub-policies or skills, while neuro-symbolic approaches integrate neural perception with symbolic reasoning. The literature reveals several key advances: disentangled task representations enable zero-shot policy transfer across compositional tasks (Wu et al., 2022), hierarchical neuro-symbolic frameworks combine symbolic planners with transformer-based policies (Baheri & Alm, 2025), and relational reinforcement learning extracts interpretable logical rules from neural policies (Hazra & De Raedt, 2023). Despite this progress, critical challenges remain: learned skills lack the formal precondition-effect semantics needed for principled composition, skill discovery methods do not produce human-interpretable abstractions, and the integration of symbolic planning with neural execution remains brittle.

### Research Objectives

This research proposes **Compositional Skill Libraries with Symbolic Abstractions (CSLSA)**, a novel framework that learns reusable neural skills paired with automatically induced symbolic descriptions, enabling zero-shot policy transfer to unseen problem configurations. Our specific objectives are:

1. **Develop an information-theoretic skill discovery module** that extracts diverse, temporally extended behaviors from demonstration or exploration data, optimized for both coverage and distinctiveness.

2. **Design a neuro-symbolic abstraction layer** that automatically induces PDDL-style precondition-effect descriptions for each discovered skill through differentiable logic programming, capturing applicability conditions and expected state transitions.

3. **Create a hybrid planning-execution architecture** where a symbolic planner composes skills for novel goals by reasoning over induced abstractions, while neural skill policies handle low-level control.

4. **Validate the framework** on procedurally generated environments, demonstrating zero-shot generalization to unseen goal configurations and domain variants.

### Significance

This research addresses fundamental challenges in AI: bridging the gap between data-driven learning and structured reasoning, enabling systematic skill reuse, and providing interpretable explanations of agent behavior. Success would advance both scientific understanding of generalizable decision-making and practical applications in robotics, automated systems, and human-AI collaboration. The induced symbolic abstractions additionally offer transparency, allowing human operators to understand, verify, and modify agent capabilities.

## 2. Methodology

### 2.1 Overview

The CSLSA framework consists of three integrated components operating in a pipeline: (1) skill discovery from interaction data, (2) symbolic abstraction induction for discovered skills, and (3) symbolic planning with neural execution for novel tasks. We detail each component below.

### 2.2 Skill Discovery Module

We extract a diverse library of temporally extended skills using a variational approach based on information-theoretic objectives. Let $\mathcal{S}$ denote the state space and $\mathcal{A}$ the action space. A skill $z \in \mathcal{Z}$ is a latent variable that modulates a low-level policy $\pi_\theta(a|s, z)$.

**Objective Function:** We maximize the mutual information between skills and their induced state trajectories while ensuring skill diversity:

$$\mathcal{L}_{\text{skill}} = I(z; \tau) - \beta \cdot H(z|s_0) = \mathbb{E}_{z, \tau}[\log q_\phi(z|\tau)] + H(z) - \beta \cdot H(z|s_0)$$

where $\tau = (s_0, a_0, s_1, \ldots, s_T)$ is a trajectory, $q_\phi(z|\tau)$ is a learned discriminator that infers skills from trajectories, and $\beta$ controls the trade-off between skill distinctiveness and state-conditional diversity.

**Skill Termination:** Each skill includes a learned termination function $\psi_\omega(s, z) \in [0, 1]$ predicting the probability of skill completion, enabling variable-length skill execution:

$$\mathcal{L}_{\text{term}} = -\mathbb{E}_{z, \tau}\left[\sum_{t=0}^{T} \gamma^t \left( c_t \log \psi_\omega(s_t, z) + (1-c_t) \log(1-\psi_\omega(s_t, z)) \right)\right]$$

where $c_t \in \{0, 1\}$ indicates skill completion at timestep $t$.

**Training Procedure:** Skills are learned from a dataset $\mathcal{D}$ containing either expert demonstrations or exploration trajectories. We alternate between: (a) sampling skills and executing them to collect trajectories, (b) updating the discriminator $q_\phi$ to distinguish skills, and (c) updating the skill policy $\pi_\theta$ and termination function $\psi_\omega$ via policy gradients.

### 2.3 Neuro-Symbolic Abstraction Layer

For each discovered skill $z_i$, we automatically induce symbolic preconditions $\text{Pre}(z_i)$ and effects $\text{Eff}(z_i)$ expressed in first-order logic, compatible with PDDL planners.

**Symbolic State Representation:** We define a set of predicate templates $\mathcal{P} = \{p_1, p_2, \ldots, p_K\}$ grounded by objects in the environment (e.g., `at(agent, ?loc)`, `holding(?obj)`, `door_open(?door)`). A neural predicate classifier $f_\xi: \mathcal{S} \rightarrow [0, 1]^{|\mathcal{G}|}$ maps continuous states to probabilistic groundings $\mathcal{G}$ over predicate instances.

**Differentiable Logic Programming:** We learn preconditions and effects using a differentiable inductive logic programming approach. For skill $z_i$, we parameterize:

$$\text{Pre}(z_i) = \bigwedge_{j} w_{ij}^{\text{pre}} \cdot p_j \quad \text{(soft conjunction)}$$
$$\text{Eff}(z_i) = \{(p_j, \Delta_{ij}) : w_{ij}^{\text{eff}} > \epsilon\}$$

where $w_{ij}^{\text{pre}}, w_{ij}^{\text{eff}} \in [0, 1]$ are learnable weights indicating predicate relevance, and $\Delta_{ij} \in \{\text{add}, \text{del}\}$ specifies whether predicate $p_j$ is added or deleted.

**Training Objective:** Given skill execution traces $(s_{\text{init}}, z_i, s_{\text{final}}, \text{success})$, we optimize:

$$\mathcal{L}_{\text{abstract}} = \mathcal{L}_{\text{pre}} + \lambda_1 \mathcal{L}_{\text{eff}} + \lambda_2 \mathcal{L}_{\text{sparse}}$$

where:
- **Precondition Loss:** $\mathcal{L}_{\text{pre}} = -\mathbb{E}\left[\text{success} \cdot \log \sigma(\text{Pre}(z_i)(s_{\text{init}})) + (1-\text{success}) \cdot \log(1 - \sigma(\text{Pre}(z_i)(s_{\text{init}})))\right]$
- **Effect Loss:** $\mathcal{L}_{\text{eff}} = \mathbb{E}\left[\|f_\xi(s_{\text{final}}) - \text{Apply}(\text{Eff}(z_i), f_\xi(s_{\text{init}}))\|^2\right]$
- **Sparsity Regularization:** $\mathcal{L}_{\text{sparse}} = \sum_{i,j} |w_{ij}^{\text{pre}}| + |w_{ij}^{\text{eff}}|$

The function $\text{Apply}(\cdot)$ simulates effect application using differentiable operations on predicate probabilities.

**Discretization:** After training, we threshold weights to obtain crisp logical formulas: $\text{Pre}(z_i) = \{p_j : w_{ij}^{\text{pre}} > \tau_{\text{pre}}\}$.

### 2.4 Symbolic Planning with Neural Execution

Given a novel task specified by initial state $s_0$ and goal $g$, the system operates as follows:

**Step 1 - Symbolic State Extraction:** Compute symbolic state $\hat{s}_0 = \text{Discretize}(f_\xi(s_0))$.

**Step 2 - Skill Plan Generation:** Use an off-the-shelf PDDL planner (e.g., Fast Downward) with the induced domain model $\mathcal{D} = \langle \mathcal{P}, \{(z_i, \text{Pre}(z_i), \text{Eff}(z_i))\}_{i=1}^N \rangle$ to find a skill sequence $\mathbf{z}^* = (z_{k_1}, z_{k_2}, \ldots, z_{k_M})$ achieving goal $g$.

**Step 3 - Neural Execution:** Sequentially execute each skill using the neural policy:
```
for z in z*:
    while not ψ_ω(s, z) > τ_term:
        a ~ π_θ(·|s, z)
        s ← env.step(a)
```

**Replanning:** If execution monitoring detects deviation from expected effects (via predicate classifier), trigger replanning from the current state.

### 2.5 Experimental Design

**Environments:** We evaluate on three procedurally generated domains:
1. **MiniGrid:** Grid worlds with keys, doors, and goal objects, varying in layout, object positions, and required skill sequences.
2. **BEHAVIOR-100:** Household tasks requiring manipulation skills, with varying object configurations and goal specifications.
3. **Crafting World:** A custom environment requiring resource gathering and item crafting with compositional dependencies.

**Data Collection:** For each domain, we collect 10,000 trajectories from a mixture of scripted policies and random exploration. Skill discovery uses 80% for training, 20% for validation.

**Baselines:**
- **Flat PPO/SAC:** Standard deep RL without hierarchy
- **DIAYN:** Information-theoretic skill discovery without symbolic abstraction
- **HRL (Option-Critic):** Hierarchical RL with learned options
- **DERRL:** Deep Explainable Relational RL (Hazra & De Raedt, 2023)
- **Oracle Symbolic:** Hand-crafted PDDL with neural low-level policies

**Evaluation Metrics:**
1. **Zero-Shot Success Rate:** Percentage of novel test tasks solved without additional training
2. **Skill Reuse Rate:** Proportion of discovered skills utilized across test tasks
3. **Sample Efficiency:** Number of environment interactions needed for skill learning
4. **Abstraction Accuracy:** Precision/recall of induced preconditions and effects against ground truth (where available)
5. **Plan Quality:** Number of skill executions to reach goals (normalized by optimal)
6. **Interpretability Score:** Human evaluation of symbolic description clarity (Likert scale)

**Generalization Tests:**
- **Compositional:** Novel combinations of training goals
- **Structural:** Different environment layouts
- **Object Transfer:** New object instances of known categories
- **Scale:** Larger environments than training

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Zero-Shot Generalization:** We hypothesize CSLSA will achieve 40-60% higher zero-shot success rates compared to flat RL baselines and 15-25% improvement over purely neural hierarchical methods on compositional test tasks.

2. **Interpretable Skill Descriptions:** The induced symbolic abstractions will achieve >85% precision and >75% recall against human-annotated precondition-effect specifications, providing human-readable explanations of learned behaviors.

3. **Efficient Skill Reuse:** The learned skill library will demonstrate >70% skill reuse across diverse test tasks, validating the compositionality of discovered behaviors.

4. **Sample Efficiency Gains:** By leveraging symbolic planning for high-level decisions, CSLSA will require 3-5x fewer environment interactions than end-to-end methods for solving novel task configurations.

5. **Robust Planning:** The hybrid architecture will successfully handle tasks requiring 10+ sequential skill applications, where flat policies typically fail due to credit assignment challenges.

### Broader Impact

**Scientific Contributions:** This work advances the theoretical understanding of how symbolic abstraction enables systematic generalization in learned systems. The differentiable logic programming approach for abstraction induction provides a principled methodology applicable beyond RL to program synthesis and concept learning.

**Practical Applications:** The framework directly benefits robotics, where pre-trained skill libraries with interpretable descriptions can accelerate deployment to new tasks. Industrial applications include warehouse automation, household assistance robots, and manufacturing systems requiring flexible task adaptation.

**Interpretability and Trust:** By producing human-readable skill descriptions, CSLSA addresses critical needs for AI transparency. Operators can inspect, verify, and modify skill applicability conditions, facilitating human-AI collaboration and regulatory compliance in safety-critical domains.

**Limitations and Future Work:** Current limitations include reliance on predefined predicate templates and potential brittleness when neural perception fails. Future work will explore automatic predicate invention through language grounding and robustness improvements through uncertainty-aware planning.

In summary, this research bridges the complementary strengths of symbolic AI and deep learning, offering a principled approach to skill composition that promises significant advances in generalizable sequential decision-making.