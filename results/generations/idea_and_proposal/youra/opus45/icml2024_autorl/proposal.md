# Research Proposal: Two-Phase Meta-Learned Expert Primitives for Compositional In-Context Reinforcement Learning

## 1. Introduction

### 1.1 Background

Reinforcement learning (RL) has achieved remarkable successes across diverse domains, from mastering complex games like Go and StarCraft to controlling nuclear fusion reactors and optimizing logistics systems. However, beneath these headline achievements lies a persistent challenge: RL algorithms remain notoriously brittle and sensitive to implementation details, hyperparameter choices, and environmental variations. This brittleness severely limits the practical applicability of RL, particularly when deploying algorithms to novel problem domains where extensive engineering and tuning are infeasible.

The emerging field of Automated Reinforcement Learning (AutoRL) seeks to address these limitations by developing methods that can automatically adapt to new tasks and environments without manual intervention. Within this space, three distinct research communities have made significant progress: meta-reinforcement learning, which learns learning algorithms that can quickly adapt to new tasks; AutoML for RL, which automates the selection and configuration of RL components; and more recently, large language models (LLMs) and in-context learning approaches that leverage transformer architectures to implement RL algorithms implicitly through context conditioning.

In-context reinforcement learning (ICRL) represents a particularly promising direction. Methods such as Algorithm Distillation (AD) demonstrate that transformers can learn to implement RL algorithms by conditioning on trajectory histories, effectively performing "learning" through forward passes without explicit gradient updates at test time. Decision-Pretrained Transformer (DPT) extends this by showing that supervised pretraining can produce agents capable of in-context exploration and exploitation. However, these monolithic approaches struggle with cross-domain generalization—when faced with tasks that differ substantially from training distributions, performance degrades significantly.

Recent work has begun exploring Mixture-of-Experts (MoE) architectures for ICRL. The T2MIR framework introduces token-wise and task-wise MoE mechanisms trained end-to-end, demonstrating improved capacity over monolithic baselines. However, end-to-end training conflates two distinct learning objectives: acquiring specialized skill primitives and learning to compose them appropriately. This conflation may limit the emergence of truly modular, reusable primitives that can be flexibly recombined for novel tasks.

### 1.2 Research Objectives

This research proposes a novel **two-phase training paradigm** for compositional in-context reinforcement learning. Our central hypothesis is that explicitly separating the learning of specialized expert primitives from the learning of compositional routing produces superior cross-domain generalization compared to both monolithic ICRL methods and end-to-end MoE approaches.

Specifically, our objectives are:

1. **Develop a two-phase MoE-ICRL architecture** where Phase 1 meta-learns diverse, specialized expert policy modules with explicit diversity regularization, and Phase 2 trains a transformer-based in-context router to compose these frozen primitives via soft attention.

2. **Demonstrate superior cross-domain generalization** on held-out task categories from the Meta-World ML45 benchmark, achieving >15% improvement over monolithic ICRL baselines (AD, DPT) and >5% improvement over end-to-end MoE approaches (T2MIR).

3. **Validate the compositional mechanism** by showing that expert primitives exhibit meaningful specialization (high utilization entropy) and that the router produces semantically coherent attention patterns across similar tasks.

4. **Establish theoretical and empirical foundations** for compositional structure in AutoRL systems, providing a principled approach to building generalizable RL agents.

### 1.3 Significance

This research addresses a fundamental challenge in AutoRL: how to build RL systems that generalize beyond their training distributions to truly novel task categories. By establishing that two-phase training produces superior compositional structure compared to end-to-end approaches, we provide both a practical methodology for improving ICRL systems and theoretical insights into the role of modularity in generalization. The proposed approach bridges meta-learning, AutoML, and in-context learning communities, contributing to the cross-pollination of ideas that is essential for advancing AutoRL.

## 2. Methodology

### 2.1 Problem Formulation

We consider the meta-reinforcement learning setting where an agent must quickly adapt to new tasks drawn from a task distribution $p(\mathcal{T})$. Each task $\mathcal{T}_i$ is a Markov Decision Process (MDP) defined by tuple $(\mathcal{S}, \mathcal{A}, P_i, R_i, \gamma)$ with shared state space $\mathcal{S}$, action space $\mathcal{A}$, discount factor $\gamma$, but task-specific transition dynamics $P_i$ and reward function $R_i$.

In the in-context RL setting, the agent receives a context trajectory $\tau_{1:t} = \{(s_1, a_1, r_1), ..., (s_t, a_t, r_t)\}$ from interactions with the current task and must produce actions that maximize expected return without explicit parameter updates.

### 2.2 Architecture Overview

Our MoE-ICRL architecture consists of two components:

**Expert Modules:** A set of $K$ small transformer-based policy networks $\{\pi_{\theta_k}\}_{k=1}^K$, each with 2-3 layers and approximately 1M parameters. Each expert processes the current state $s_t$ and produces an action distribution.

**In-Context Router:** A transformer network $R_\phi$ that processes the trajectory context $\tau_{1:t}$ and produces soft attention weights $\alpha = (\alpha_1, ..., \alpha_K)$ over experts.

The final policy is a mixture:

$$\pi(a|s_t, \tau_{1:t}) = \sum_{k=1}^K \alpha_k(\tau_{1:t}) \cdot \pi_{\theta_k}(a|s_t)$$

where $\alpha_k(\tau_{1:t}) = \text{softmax}(R_\phi(\tau_{1:t}))_k$.

### 2.3 Phase 1: Meta-Learning Expert Primitives

In Phase 1, we meta-learn the expert modules to develop diverse, specialized skill primitives. We employ a multi-task meta-learning objective with explicit diversity regularization.

**Base Meta-Learning Objective:** Each expert is trained on a subset of training tasks using MAML-style optimization:

$$\mathcal{L}_{\text{meta}}(\theta_k) = \mathbb{E}_{\mathcal{T}_i \sim p(\mathcal{T})} \left[ \mathcal{L}_{\mathcal{T}_i}(\theta_k - \alpha \nabla_{\theta_k} \mathcal{L}_{\mathcal{T}_i}(\theta_k)) \right]$$

where $\mathcal{L}_{\mathcal{T}_i}$ is the policy gradient loss on task $\mathcal{T}_i$.

**Diversity Regularization:** To prevent expert collapse (where all experts converge to similar policies), we introduce a diversity loss based on pairwise policy divergence:

$$\mathcal{L}_{\text{div}} = -\lambda_{\text{div}} \sum_{j \neq k} D_{\text{KL}}(\pi_{\theta_j} \| \pi_{\theta_k})$$

where $D_{\text{KL}}$ is computed over a batch of states sampled from the replay buffer.

**Task Assignment:** We employ a soft clustering mechanism where each task is probabilistically assigned to experts based on performance. Let $p(k|\mathcal{T}_i)$ denote the probability of assigning task $\mathcal{T}_i$ to expert $k$:

$$p(k|\mathcal{T}_i) \propto \exp(\beta \cdot J_k(\mathcal{T}_i))$$

where $J_k(\mathcal{T}_i)$ is the expected return of expert $k$ on task $\mathcal{T}_i$ and $\beta$ is a temperature parameter.

**Combined Phase 1 Objective:**

$$\mathcal{L}_{\text{Phase1}} = \sum_{k=1}^K \mathbb{E}_{\mathcal{T}_i \sim p(\mathcal{T})} \left[ p(k|\mathcal{T}_i) \cdot \mathcal{L}_{\text{meta}}(\theta_k) \right] + \mathcal{L}_{\text{div}}$$

### 2.4 Phase 2: Training the In-Context Router

After Phase 1 converges, we freeze all expert parameters $\{\theta_k\}_{k=1}^K$ and train only the router $R_\phi$.

**Data Collection:** We collect trajectory datasets by rolling out the mixture policy on training tasks, storing tuples $(\tau_{1:t}, s_t, a^*, \mathcal{T}_i)$ where $a^*$ is the action from the best-performing expert for task $\mathcal{T}_i$.

**Router Architecture:** The router is a causal transformer that processes trajectory tokens:

$$h_t = \text{Transformer}_\phi([\text{embed}(s_1, a_1, r_1), ..., \text{embed}(s_t, a_t, r_t)])$$

$$\alpha = \text{softmax}(W_\alpha h_t + b_\alpha)$$

**Router Training Objective:** We train the router using a combination of behavioral cloning and entropy regularization:

$$\mathcal{L}_{\text{router}} = -\mathbb{E}_{(\tau, s, a^*)} \left[ \log \pi(a^*|s, \tau) \right] + \lambda_{\text{ent}} H(\alpha)$$

where $H(\alpha) = -\sum_k \alpha_k \log \alpha_k$ encourages exploration of different expert combinations.

**Load Balancing:** To ensure all experts are utilized, we add an auxiliary load balancing loss:

$$\mathcal{L}_{\text{balance}} = K \cdot \sum_{k=1}^K f_k \cdot P_k$$

where $f_k$ is the fraction of tokens routed to expert $k$ and $P_k$ is the average routing probability for expert $k$.

**Combined Phase 2 Objective:**

$$\mathcal{L}_{\text{Phase2}} = \mathcal{L}_{\text{router}} + \lambda_{\text{bal}} \mathcal{L}_{\text{balance}}$$

### 2.5 Experimental Design

**Benchmark:** Meta-World ML45, containing 45 distinct robotic manipulation tasks. We use 40 tasks for training and hold out 5 task categories for evaluation: door-open, drawer-close, hammer, peg-insert-side, and sweep-into.

**Baselines:**
- **Algorithm Distillation (AD):** Monolithic transformer trained on learning histories
- **Decision-Pretrained Transformer (DPT):** Supervised pretraining for in-context RL
- **MAML:** Gradient-based meta-learning baseline
- **PEARL:** Context-based meta-RL with latent task inference
- **T2MIR:** End-to-end MoE for ICRL (primary comparison)

**Ablations:**
- Number of experts: $K \in \{8, 16, 32\}$
- Diversity coefficient: $\lambda_{\text{div}} \in \{0.01, 0.1, 1.0\}$
- Two-phase vs. end-to-end training
- With/without load balancing

**Evaluation Metrics:**

1. **Success Rate:** Percentage of episodes achieving task goal on held-out categories (50 episodes per task, 5 seeds minimum, 20 seeds for statistical tests)

2. **Sample Efficiency:** Environment steps required to reach 50% success threshold

3. **Expert Utilization Entropy:** $H(\bar{\alpha}) = -\sum_k \bar{\alpha}_k \log \bar{\alpha}_k$ where $\bar{\alpha}_k$ is the average attention weight for expert $k$ across evaluation episodes

4. **Task-Attention Consistency:** Cosine similarity of attention distributions between tasks from the same category

**Statistical Analysis:**
- One-way ANOVA with Tukey HSD post-hoc tests
- Significance level $\alpha = 0.05$ with Bonferroni correction
- Report mean ± standard deviation, 95% confidence intervals, Cohen's d effect sizes
- Minimum 20 random seeds for primary comparisons

**Computational Requirements:** Estimated 4-8 GPU-days on A100 for full experiments with $K=32$ experts.

### 2.6 Verification of Causal Mechanism

To validate our hypothesized causal mechanism, we design specific experiments for each link:

**Link 1 (Meta-training → Specialized Primitives):** Compare expert specialization (measured by entropy and task-expert assignment patterns) between Phase 1 training with and without diversity regularization.

**Link 2 (Primitives → Router Composition):** Analyze attention patterns to verify that (a) similar tasks produce similar attention distributions (cosine similarity > 0.7), and (b) held-out tasks produce novel attention combinations not seen during training.

**Link 3 (Composition → Generalization):** Ablate the number of experts and measure correlation between expert diversity and held-out performance.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** MoE-ICRL with two-phase training will achieve >15% higher success rate on Meta-World ML45 held-out categories compared to AD and DPT baselines, and >5% higher than T2MIR. We expect absolute success rates of approximately 65-75% on held-out tasks versus 45-55% for monolithic baselines and 55-65% for T2MIR.

**Secondary Predictions:**
- **P2:** Expert utilization entropy $H(\alpha) > 1.5$ nats for $K=8$, indicating meaningful specialization rather than collapse
- **P3:** Task-attention consistency within categories exceeds 0.7 cosine similarity
- **P4:** Two-phase training produces measurably higher expert diversity than end-to-end T2MIR training

**Falsification Criteria:** The hypothesis will be considered falsified if: (1) success rate does not exceed AD baseline, (2) expert entropy falls below 0.5 nats, (3) no discernible task-category structure in attention patterns, or (4) no measurable advantage over T2MIR.

### 3.2 Scientific Impact

This research will establish **compositional structure as a principled approach to AutoRL generalization**. By demonstrating that explicit separation of primitive learning from composition learning produces superior results, we provide theoretical grounding for modular approaches to meta-RL. The findings will inform the design of future ICRL systems and contribute to understanding how transformers can implement compositional reasoning for sequential decision-making.

### 3.3 Practical Impact

The two-phase MoE-ICRL framework offers a practical methodology for building RL systems that generalize to novel task categories without retraining. This addresses a critical barrier to RL deployment in real-world settings where task distributions shift over time. The modular architecture also provides interpretability benefits—practitioners can inspect which experts are activated for different tasks, enabling debugging and trust-building.

### 3.4 Broader Contributions

By bridging meta-learning, AutoML, and in-context learning communities, this work contributes to the cross-pollination of ideas essential for AutoRL progress. The explicit comparison with T2MIR and other baselines will clarify the relative merits of different architectural and training choices, providing guidance for future research directions. We will release code and trained models to facilitate reproducibility and further investigation.