# Research Proposal: Hierarchical Foundation Model Planning with Learned Temporal Abstractions for Long-Horizon Decision Making

## 1. Title

**Hierarchical Foundation Model Planning with Learned Temporal Abstractions for Long-Horizon Decision Making**

## 2. Introduction

### Background

Foundation models pretrained on massive vision and language datasets have revolutionized AI by demonstrating exceptional capabilities across diverse downstream tasks. Models such as GPT-4, CLIP, and Flamingo exhibit remarkable zero-shot and few-shot learning abilities, leveraging broad semantic understanding acquired during pretraining. However, as these models are increasingly deployed in sequential decision-making applications—including robotics, autonomous driving, interactive agents, and embodied AI—their limitations in long-horizon planning and multi-step reasoning become apparent.

Traditional reinforcement learning (RL) and planning methods excel at sequential optimization through trial-and-error learning but typically operate in task-specific settings without access to broad prior knowledge. While these approaches have achieved superhuman performance in domains like board games and Atari, they suffer from sample inefficiency and poor generalization to novel scenarios. The fundamental challenge lies in the gap between foundation models' rich semantic understanding and RL's ability to perform temporal credit assignment and sequential optimization.

Recent work has begun exploring this intersection. Reinforcement Learning from Human Feedback (RLHF) has successfully aligned language models with human preferences, while vision-language models have been integrated as perception modules in embodied agents. However, a critical unsolved problem persists: **how can we leverage foundation models' world knowledge to automatically discover meaningful temporal abstractions for long-horizon decision making?**

Hierarchical reinforcement learning (HRL) offers a promising framework by decomposing complex tasks into subtasks through temporal abstractions. Classical HRL approaches like the options framework and feudal architectures require extensive reward engineering and task-specific design. Recent work on temporal abstraction in autoregressive models (Kobayashi et al., 2025) and option-aware value learning (Ahn et al., 2025) demonstrates progress, but these methods do not fully exploit the semantic reasoning capabilities of modern foundation models.

### Research Objectives

This research proposes a novel hierarchical framework that bridges foundation models and sequential decision making through **automatic discovery of semantic temporal abstractions**. Our specific objectives are:

1. **Develop an unsupervised method** for discovering semantically meaningful subgoals by analyzing foundation model representations across successful task demonstrations
2. **Design a hierarchical architecture** where a high-level planner (fine-tuned foundation model) generates subgoal sequences and low-level policies execute these subgoals via RL
3. **Create a foundation model-based reward shaping mechanism** that guides low-level policy learning toward achieving intermediate subgoals
4. **Demonstrate improved sample efficiency and generalization** on long-horizon manipulation, navigation, and multi-task benchmarks
5. **Provide theoretical analysis** of how temporal abstraction reduces effective horizon length and improves credit assignment

### Significance

This research addresses critical challenges at the intersection of foundation models and decision making:

- **Sample Efficiency**: By decomposing long-horizon tasks into shorter subtasks with reusable skills, our approach significantly reduces the sample complexity of learning
- **Generalization**: Leveraging foundation models' semantic understanding enables zero-shot and few-shot generalization to novel task compositions
- **Interpretability**: Semantic subgoals provide human-interpretable intermediate representations, facilitating debugging and human-AI collaboration
- **Scalability**: Automatic subgoal discovery eliminates manual reward engineering, enabling deployment across diverse domains
- **Theoretical Contribution**: Our framework provides insights into how temporal abstraction in foundation models can be formalized and optimized

## 3. Methodology

### 3.1 Overall Framework

Our hierarchical framework consists of three main components:

1. **Semantic Subgoal Discovery Module**: Automatically identifies temporal abstractions from foundation model embeddings
2. **High-Level Planner**: A fine-tuned foundation model that generates subgoal sequences conditioned on task descriptions
3. **Low-Level Policy Network**: RL-trained policies that achieve individual subgoals with foundation model-based reward shaping

### 3.2 Data Collection

**Demonstration Dataset Collection**: We collect multi-modal demonstration data across diverse environments:

- **Robotic Manipulation**: 10K+ trajectories from simulation (RLBench, Meta-World) and real-world robot platforms performing tasks like "pick and place," "drawer opening," and "object assembly"
- **Navigation**: 5K+ trajectories in embodied AI environments (Habitat, AI2-THOR) with language-annotated goals
- **Interactive Agents**: 3K+ human demonstrations of tool use and multi-step reasoning tasks

Each trajectory $\tau = \{(s_t, a_t, o_t)\}_{t=0}^T$ includes:
- State observations $s_t$ (RGB images, depth, proprioception)
- Actions $a_t$
- Language annotations $o_t$ describing intermediate goals (collected via crowdsourcing)

**Foundation Model Selection**: We employ pretrained vision-language models (e.g., CLIP, Flamingo) as our base encoder $f_\theta: \mathcal{S} \rightarrow \mathbb{R}^d$ that maps states to $d$-dimensional embeddings.

### 3.3 Semantic Subgoal Discovery

**Step 1: Embedding Extraction**

For each trajectory $\tau_i$ in our dataset, we extract foundation model embeddings:
$$\mathbf{z}_t^{(i)} = f_\theta(s_t^{(i)})$$

**Step 2: Temporal Clustering**

We apply a temporal-aware clustering algorithm to identify natural "semantic waypoints." Unlike standard k-means, we incorporate temporal structure through Dynamic Time Warping (DTW):

$$d_{DTW}(\tau_i, \tau_j) = \min_{\phi} \sum_{(t,t') \in \phi} \|\mathbf{z}_t^{(i)} - \mathbf{z}_{t'}^{(j)}\|_2$$

where $\phi$ is an alignment path. We then perform hierarchical agglomerative clustering to obtain $K$ subgoal clusters $\{C_1, ..., C_K\}$.

**Step 3: Subgoal Prototype Learning**

For each cluster $C_k$, we learn a prototype representation $\mathbf{g}_k$ by solving:
$$\mathbf{g}_k = \arg\min_{\mathbf{g}} \sum_{\mathbf{z} \in C_k} \|\mathbf{z} - \mathbf{g}\|_2^2 + \lambda \mathcal{R}(\mathbf{g})$$

where $\mathcal{R}(\mathbf{g})$ is a regularizer encouraging semantic coherence with language descriptions through contrastive learning:
$$\mathcal{R}(\mathbf{g}_k) = -\log \frac{\exp(\text{sim}(\mathbf{g}_k, \mathbf{l}_k)/\tau)}{\sum_{j=1}^K \exp(\text{sim}(\mathbf{g}_k, \mathbf{l}_j)/\tau)}$$

where $\mathbf{l}_k$ are language embeddings of cluster annotations and $\tau$ is a temperature parameter.

**Step 4: Subgoal Sequence Labeling**

Each demonstration trajectory is segmented into subgoal sequences:
$$\tau_i \rightarrow [(s_0^{(i)}, g_1), (s_{t_1}^{(i)}, g_2), ..., (s_{t_{m-1}}^{(i)}, g_m)]$$

where $g_j \in \{1, ..., K\}$ are subgoal labels assigned when $\mathbf{z}_t$ enters cluster $C_{g_j}$.

### 3.4 High-Level Planner Training

We fine-tune a vision-language foundation model (e.g., GPT-4V or Flamingo) to predict subgoal sequences:

**Input Format**: 
- Task description (language): "Pick up the red block and place it in the drawer"
- Initial state observation: $s_0$

**Output Format**: Sequence of subgoal descriptions $[g_1, g_2, ..., g_m]$

**Training Objective**: Supervised learning on labeled trajectory segments:
$$\mathcal{L}_{plan} = -\sum_{i=1}^N \sum_{j=1}^{m_i} \log P(g_j^{(i)} | s_0^{(i)}, \text{task}_i, g_{<j}; \theta_{plan})$$

We employ LoRA (Low-Rank Adaptation) for parameter-efficient fine-tuning, updating only a small number of parameters while preserving pretrained knowledge.

### 3.5 Low-Level Policy Learning

**Policy Architecture**: For each subgoal $g_k$, we train a goal-conditioned policy $\pi_k(a | s, \mathbf{g}_k)$ using Soft Actor-Critic (SAC).

**State Space**: $s \in \mathcal{S}$ (visual observations + proprioception)

**Action Space**: $a \in \mathcal{A}$ (continuous control or discrete actions)

**Foundation Model-Based Reward Shaping**:
$$r_t = r_t^{task} + \alpha \cdot r_t^{FM}$$

where $r_t^{task}$ is the sparse task reward and:
$$r_t^{FM} = -\|\mathbf{z}_t - \mathbf{g}_k\|_2 + \beta \cdot \max(0, \text{sim}(\mathbf{z}_t, \mathbf{l}_k) - \gamma)$$

This reward encourages the agent to reach states whose foundation model embeddings are close to the target subgoal prototype while maintaining semantic alignment.

**Option Termination**: Each option terminates when:
$$\|\mathbf{z}_t - \mathbf{g}_k\|_2 < \epsilon$$

**Training Algorithm**: We employ an alternating optimization scheme:

```
Algorithm 1: Hierarchical Policy Training
Input: Demonstration dataset D, foundation model f_θ, subgoal prototypes {g_k}
Output: High-level planner π_high, low-level policies {π_k}

1. Pre-train π_high via supervised learning on D
2. Initialize low-level policies {π_k} randomly
3. For episode = 1 to N_episodes:
4.   Sample task and initial state s_0
5.   Generate subgoal sequence [g_1, ..., g_m] ~ π_high(·|s_0, task)
6.   For j = 1 to m:
7.     Execute π_{g_j} until termination or timeout
8.     Collect transition data for π_{g_j}
9.     Update π_{g_j} using SAC with shaped rewards
10.  If task succeeded: Fine-tune π_high with REINFORCE
11. Return π_high, {π_k}
```

### 3.6 Experimental Design

**Environments and Benchmarks**:

1. **RLBench**: 10 long-horizon manipulation tasks (>50 steps)
2. **Meta-World ML45**: Multi-task robotic manipulation
3. **ALFRED**: Embodied AI household tasks with language instructions
4. **MiniGrid**: Navigation with compositional task structures

**Baselines**:
- Flat RL (SAC, PPO) without hierarchy
- Hierarchical RL (HIRO, HAC) with hand-designed subgoals
- LLM-based planning (SayCan, Code-as-Policies) without learned low-level skills
- Recent foundation model + RL methods (RT-2, PALM-E)

**Evaluation Metrics**:

1. **Sample Efficiency**: Success rate vs. number of environment interactions
2. **Task Success Rate**: Percentage of successfully completed tasks
3. **Generalization**: Zero-shot performance on novel task compositions and unseen objects
4. **Subgoal Quality**: 
   - Temporal segmentation accuracy (intersection-over-union with human annotations)
   - Semantic coherence (CLIP similarity between discovered subgoals and language descriptions)
5. **Computational Efficiency**: Wall-clock training time and inference latency

**Ablation Studies**:
- Effect of foundation model choice (CLIP, Flamingo, BLIP-2)
- Impact of number of subgoal clusters $K$
- Contribution of foundation model reward shaping vs. sparse rewards
- Comparison of clustering algorithms (DTW-based vs. standard k-means)

**Training Details**:
- Foundation model: Frozen CLIP-ViT-L/14 or fine-tuned Flamingo-9B
- High-level planner: GPT-3.5 fine-tuned with LoRA (rank=16)
- Low-level policies: 3-layer MLPs (256 hidden units) with SAC
- Hyperparameters: $\alpha=0.5$, $\beta=0.1$, $\gamma=0.7$, $\epsilon=0.1$
- Training budget: 5M environment steps per task

### 3.7 Theoretical Analysis

We provide sample complexity bounds showing how temporal abstraction reduces effective horizon length. For a task with horizon $T$ decomposed into $m$ subgoals each requiring $T/m$ steps:

**Theorem (Informal)**: Under Lipschitz continuity assumptions, the sample complexity of our hierarchical approach is:
$$\tilde{O}\left(m \cdot \left(\frac{T}{m}\right)^2\right) = \tilde{O}\left(\frac{T^2}{m}\right)$$

compared to $\tilde{O}(T^2)$ for flat RL, achieving a $m$-fold improvement.

We also analyze how foundation model embedding quality (measured by downstream task performance) correlates with subgoal discovery quality and overall system performance.

## 4. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Results**:
1. **Sample Efficiency Improvement**: 3-5× reduction in environment interactions needed to achieve 80% success rate compared to flat RL baselines
2. **Task Success Rate**: >85% on long-horizon manipulation tasks (vs. <60% for baselines)
3. **Generalization**: >70% zero-shot success on novel task compositions (vs. <40% for task-specific methods)
4. **Subgoal Quality**: >0.75 IoU with human-annotated task segments; >0.8 CLIP similarity with language descriptions

**Qualitative Results**:
1. **Interpretable Task Decomposition**: Discovered subgoals align with human intuition (e.g., "grasp object," "navigate to target," "place object")
2. **Skill Reusability**: Learned low-level policies transfer across tasks sharing common subgoals
3. **Failure Mode Analysis**: Hierarchical structure enables identifying whether failures occur in planning or execution

**Open-Source Contributions**:
1. **Codebase**: Full implementation including subgoal discovery, hierarchical training pipeline, and evaluation suite
2. **Dataset**: Annotated multi-modal demonstration dataset with semantic subgoal labels
3. **Benchmark**: Standardized evaluation protocol for foundation model-based hierarchical RL

### Scientific Impact

**Advancing Foundation Models for Decision Making**:
This research directly addresses core questions posed in the workshop:
- Provides a principled, scalable algorithm for integrating foundation models into decision-making pipelines
- Demonstrates how vision-language models trained without action data can guide action selection through learned temporal abstractions
- Establishes evaluation protocols for measuring foundation model contributions to long-horizon planning

**Theoretical Contributions**:
- Formalizes the relationship between foundation model embedding quality and hierarchical planning performance
- Provides sample complexity analysis showing quantitative benefits of learned temporal abstraction
- Connects representation learning in foundation models to classical HRL theory

**Methodological Innovations**:
- First approach to automatically discover semantic subgoals through foundation model clustering
- Novel foundation model-based reward shaping mechanism that preserves semantic meaning
- Scalable framework applicable across vision, language, and multi-modal domains

### Practical Impact

**Robotics and Embodied AI**:
- Enables robots to perform complex long-horizon tasks with minimal task-specific programming
- Facilitates natural language interaction by grounding commands in learned semantic subgoals
- Reduces deployment time through transfer of learned skills across tasks

**Autonomous Systems**:
- Improves sample efficiency for training autonomous vehicles in simulation
- Provides interpretable decision-making for safety-critical applications
- Enables compositional generalization to novel driving scenarios

**Interactive Agents and Tools**:
- Enhances multi-step reasoning in dialogue agents and personal assistants
- Enables agents to learn complex tool use through hierarchical decomposition
- Supports debugging through transparent intermediate goals

**Broader Societal Impact**:
- Democratizes access to capable decision-making AI by reducing data and computational requirements
- Improves AI safety through interpretable hierarchical structures
- Advances human-AI collaboration by providing common semantic abstractions

### Future Directions

This research opens several promising avenues:
1. **Online Subgoal Discovery**: Extending to continual learning settings where subgoals evolve with experience
2. **Multi-Agent Coordination**: Applying hierarchical abstractions to collaborative multi-agent tasks
3. **Foundation Model Fine-Tuning**: Co-training foundation models and policies end-to-end
4. **Theoretical Understanding**: Deeper analysis of when and why certain temporal abstractions emerge

By bridging the semantic richness of foundation models with the sequential optimization power of reinforcement learning through principled temporal abstraction, this research takes a significant step toward general-purpose decision-making agents that combine broad knowledge with efficient learning.