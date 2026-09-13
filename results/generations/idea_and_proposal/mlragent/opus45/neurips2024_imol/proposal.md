# Research Proposal

## Title
Curiosity-Driven Skill Chaining: Learning Compositional Skills through Intrinsic Motivation over Dynamic Skill Graphs

---

## 1. Introduction

### Background

The ability to acquire, compose, and flexibly deploy a diverse repertoire of skills is a hallmark of human intelligence. From infancy, humans develop simple motor primitives—grasping, reaching, manipulating—and gradually chain them into increasingly sophisticated behaviors such as tool use, cooking, and construction. This developmental trajectory is not guided solely by external rewards but is fundamentally driven by intrinsic motivations: curiosity about novel situations, interest in mastering new competencies, and the satisfaction derived from discovering how actions can be combined in meaningful ways (White, 1959; Berlyne, 1960; Deci & Ryan, 1985).

In artificial intelligence, intrinsically motivated reinforcement learning (RL) has emerged as a promising paradigm for developing autonomous agents capable of open-ended learning (Oudeyer et al., 2007; Schmidhuber, 2021). Recent advances have demonstrated remarkable success in enabling agents to explore complex environments and discover individual skills without explicit external rewards (Pathak et al., 2017; Burda et al., 2019; Eysenbach et al., 2019). However, a critical gap remains: current approaches excel at discovering isolated skills but struggle to autonomously compose them into hierarchical, generalizable behaviors. Existing hierarchical RL methods typically rely on predefined skill hierarchies or manual decomposition of tasks, severely limiting their applicability to truly open-ended environments where the structure of useful skill compositions is unknown a priori.

### Research Objectives

This research proposes **Curiosity-Driven Skill Chaining (CDSC)**, a novel framework that enables artificial agents to autonomously discover not only individual skills but also the compositional relationships between them. Our core objectives are:

1. **Develop a dynamic skill graph representation** that captures learned skills as nodes and their compositional relationships as edges, enabling structured knowledge about skill combinations.

2. **Design a compositional curiosity signal** that intrinsically motivates agents to explore novel skill chains, rewarding the discovery of successful compositions rather than merely individual skill acquisition.

3. **Create a graph-based prediction mechanism** using graph neural networks (GNNs) to identify promising unexplored skill compositions based on structural patterns in the evolving skill graph.

4. **Validate the framework** through comprehensive experiments demonstrating emergent hierarchical skill structures, improved generalization to novel tasks, and curriculum-like progression from simple to complex behaviors.

### Significance

This research addresses fundamental challenges at the intersection of intrinsically motivated learning, hierarchical reinforcement learning, and open-ended skill acquisition. By enabling agents to autonomously discover compositional skill structures, CDSC contributes to the long-standing goal of creating truly autonomous lifelong learning systems. The framework has potential applications in developmental robotics, where robots must acquire complex manipulation skills through exploration, and in virtual agents that must adapt to open-ended environments. Furthermore, by drawing inspiration from developmental psychology, this work strengthens the bridge between cognitive science and machine learning, advancing our understanding of how flexible, compositional intelligence emerges.

---

## 2. Methodology

### 2.1 Problem Formulation

We formulate the problem within a reward-free Markov Decision Process (MDP) framework, defined as $\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{T}, \gamma)$, where $\mathcal{S}$ is the state space, $\mathcal{A}$ is the action space, $\mathcal{T}: \mathcal{S} \times \mathcal{A} \rightarrow \Delta(\mathcal{S})$ is the transition function, and $\gamma$ is the discount factor. The agent's objective is to autonomously discover and learn a library of composable skills that can be chained to achieve complex behaviors.

### 2.2 Skill Representation and Embedding

**Skill Definition**: We define a skill $\sigma_i$ as a temporally extended action policy $\pi_{\sigma_i}: \mathcal{S} \rightarrow \Delta(\mathcal{A})$ with an associated termination condition $\beta_{\sigma_i}: \mathcal{S} \rightarrow [0,1]$. Each skill transforms the environment from an initiation set $\mathcal{I}_{\sigma_i} \subseteq \mathcal{S}$ to an effect set $\mathcal{E}_{\sigma_i} \subseteq \mathcal{S}$.

**Skill Embedding Space**: We learn a continuous embedding function $\phi: \Sigma \rightarrow \mathbb{R}^d$ that maps each skill $\sigma_i$ to a $d$-dimensional vector $\mathbf{z}_i = \phi(\sigma_i)$. The embedding is trained such that skills with high composability potential are proximate in the embedding space. Formally, we optimize:

$$\mathcal{L}_{embed} = \sum_{i,j} \left[ \mathbb{1}[\sigma_i \circ \sigma_j \text{ successful}] \cdot \|\mathbf{z}_i - \mathbf{z}_j\|^2 - \mathbb{1}[\sigma_i \circ \sigma_j \text{ failed}] \cdot \max(0, m - \|\mathbf{z}_i - \mathbf{z}_j\|^2) \right]$$

where $m$ is a margin hyperparameter and $\sigma_i \circ \sigma_j$ denotes sequential execution of skills.

### 2.3 Dynamic Skill Graph

**Graph Structure**: We maintain a dynamic skill graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where vertices $\mathcal{V} = \{\sigma_1, \sigma_2, ..., \sigma_n\}$ represent discovered skills and directed edges $e_{ij} \in \mathcal{E}$ represent successful compositional relationships. Each edge is weighted by the reliability of the composition:

$$w_{ij} = \frac{\text{successful\_chains}(\sigma_i, \sigma_j)}{\text{attempts}(\sigma_i, \sigma_j)}$$

**Graph Update Mechanism**: The skill graph is updated online as the agent explores. When the agent discovers a new skill $\sigma_{new}$, we:
1. Add $\sigma_{new}$ as a new vertex
2. Initialize potential edges to existing skills based on embedding proximity
3. Update edge weights based on composition attempts

### 2.4 Compositional Curiosity Signal

The core innovation of our framework is the **compositional curiosity** intrinsic reward, which motivates exploration of novel skill chains. This signal combines three components:

**Component 1 - Composition Prediction Error**: We train a forward dynamics model $f_\theta$ that predicts the outcome state of skill chains. The prediction error serves as a curiosity signal:

$$r_{pred}(\sigma_i, \sigma_j) = \|s_{actual} - f_\theta(\mathbf{z}_i, \mathbf{z}_j, s_0)\|^2$$

where $s_0$ is the initial state and $s_{actual}$ is the state after executing $\sigma_i \circ \sigma_j$.

**Component 2 - Behavioral Novelty**: We measure the novelty of the resulting behavior using a kernel density estimate over achieved effect states:

$$r_{novelty}(s_{effect}) = -\log \hat{p}(s_{effect})$$

where $\hat{p}$ is estimated from a replay buffer of previously achieved states.

**Component 3 - Graph Structure Novelty**: We reward exploration of structurally novel paths in the skill graph:

$$r_{graph}(e_{ij}) = \frac{1}{1 + \text{path\_count}(e_{ij})}$$

where $\text{path\_count}(e_{ij})$ counts how often edge $e_{ij}$ has been traversed.

**Combined Intrinsic Reward**: The total compositional curiosity signal is:

$$r_{intrinsic} = \alpha \cdot r_{pred} + \beta \cdot r_{novelty} + \gamma \cdot r_{graph}$$

where $\alpha$, $\beta$, and $\gamma$ are weighting hyperparameters tuned via cross-validation.

### 2.5 Graph Neural Network for Composition Prediction

To efficiently guide exploration toward promising skill compositions, we employ a Graph Neural Network (GNN) that predicts the value of unexplored edges based on the current graph structure.

**Architecture**: We use a 3-layer Graph Attention Network (GAT) that takes the skill graph as input and outputs a score for each potential composition:

$$\mathbf{h}_i^{(l+1)} = \sigma\left(\sum_{j \in \mathcal{N}(i)} \alpha_{ij}^{(l)} \mathbf{W}^{(l)} \mathbf{h}_j^{(l)}\right)$$

where $\alpha_{ij}^{(l)}$ are learned attention coefficients and $\mathbf{h}_i^{(0)} = \mathbf{z}_i$.

**Composition Value Prediction**: For each pair of skills $(\sigma_i, \sigma_j)$, we predict the expected intrinsic reward:

$$\hat{r}_{compose}(\sigma_i, \sigma_j) = \text{MLP}([\mathbf{h}_i^{(L)} \| \mathbf{h}_j^{(L)}])$$

This prediction is used to prioritize which skill compositions to attempt next.

### 2.6 Hierarchical Skill Learning Algorithm

**Algorithm: Curiosity-Driven Skill Chaining (CDSC)**

```
Initialize: Skill library Σ = {primitive_skills}, Skill graph G = (Σ, ∅)
Initialize: Skill embeddings φ, Forward model f_θ, GNN predictor
Initialize: Replay buffer D, Novelty buffer N

For each episode:
    1. SKILL SELECTION
       - Compute composition values: v_ij = GNN(G) for all unexplored (i,j)
       - Sample skill chain with probability ∝ softmax(v_ij / τ)
       
    2. SKILL EXECUTION
       - Execute selected skill chain σ_i ∘ σ_j
       - Record trajectory τ = (s_0, a_0, ..., s_T)
       - Compute intrinsic rewards r_intrinsic
       
    3. SKILL DISCOVERY
       - If novel behavior detected (r_novelty > threshold):
           - Extract new skill σ_new from trajectory segment
           - Add σ_new to Σ and G
           
    4. GRAPH UPDATE
       - Update edge weights based on execution success
       - Add/remove edges based on composition outcomes
       
    5. MODEL UPDATE
       - Update skill embeddings φ using L_embed
       - Update forward model f_θ on composition outcomes
       - Update GNN on (composition, reward) pairs
       - Update skill policies using PPO with r_intrinsic
```

### 2.7 Experimental Design

**Environments**: We evaluate CDSC on three progressively complex domains:

1. **Block Manipulation Environment**: A simulated robotic arm must discover and compose manipulation primitives (grasp, lift, rotate, place, stack) to achieve complex configurations.

2. **Craft World**: A grid-based environment where agents must combine resource-gathering and crafting skills to create increasingly complex items.

3. **MuJoCo Locomotion Suite**: Continuous control tasks where locomotion primitives must be composed for navigation in varied terrains.

**Baselines**: We compare against:
- DIAYN (Eysenbach et al., 2019): Diversity-based skill discovery
- ELSIM (Aubret et al., 2020): End-to-end hierarchical skill learning
- MEGA (Pong et al., 2020): Goal-conditioned exploration
- ICM (Pathak et al., 2017): Curiosity-driven exploration without skill structure
- Options Framework with random composition

**Evaluation Metrics**:

1. **Skill Library Quality**: Number and diversity of discovered skills, measured by coverage of the state space and mutual information between skill latents and terminal states.

2. **Compositional Success Rate**: Percentage of attempted skill chains that successfully achieve coherent behaviors.

3. **Hierarchical Depth**: Maximum depth of successfully executed skill chains, indicating emergence of hierarchical structure.

4. **Generalization Score**: Performance on held-out tasks that require novel combinations of learned skills.

5. **Curriculum Emergence**: Correlation between skill complexity and discovery order, measuring whether agents exhibit developmental progression.

6. **Sample Efficiency**: Number of environment interactions required to achieve skill repertoire milestones.

**Ablation Studies**: We systematically ablate each component:
- Compositional curiosity vs. standard curiosity
- GNN-guided exploration vs. random composition selection  
- Dynamic graph structure vs. static skill library
- Each intrinsic reward component individually

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Emergent Hierarchical Skill Structures**: We expect CDSC agents to autonomously discover multi-level skill hierarchies, with higher-order skills composed of lower-level primitives. The skill graph should exhibit hub-like structures where foundational skills serve as common components in multiple complex behaviors.

2. **Improved Generalization**: By learning explicit compositional relationships, CDSC agents should demonstrate superior zero-shot generalization to novel tasks that can be solved by recombining known skills, outperforming flat skill libraries by 30-50% on held-out tasks.

3. **Curriculum-Like Progression**: We anticipate observing developmental trajectories where agents naturally progress from simple to complex skills, mirroring patterns observed in human skill acquisition. Early discovered skills should be simpler and serve as building blocks for later compositions.

4. **Sample-Efficient Exploration**: The GNN-guided composition prediction should significantly improve sample efficiency by directing exploration toward promising skill combinations, reducing wasted attempts on incompatible compositions.

5. **Scalable Skill Libraries**: The dynamic graph structure should enable continued skill acquisition without catastrophic forgetting, with the skill graph growing organically as the agent explores.

### Broader Impact

**Scientific Impact**: This research advances our understanding of how compositional intelligence can emerge from intrinsic motivations alone, providing computational models that may inform theories in developmental psychology and cognitive science.

**Practical Applications**: CDSC has direct applications in robotics, where robots must acquire complex manipulation skills through autonomous exploration. The framework could enable household robots to learn diverse task repertoires without extensive programming.

**Community Contribution**: We will release open-source implementations of CDSC, standardized benchmarks for evaluating compositional skill learning, and the skill graph visualization tools to support reproducibility and future research in the IMOL community.

**Limitations and Future Work**: Current limitations include computational overhead of maintaining and updating the skill graph, and challenges in defining skill boundaries in continuous action spaces. Future work will explore integration with language models for semantic skill descriptions and extension to multi-agent scenarios where agents can share and combine skill graphs.

---

This research represents a significant step toward truly autonomous, open-ended learning systems that can acquire not just individual skills but the compositional structure underlying flexible, intelligent behavior.