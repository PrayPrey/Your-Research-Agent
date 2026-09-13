# Research Proposal: Hierarchical Skill Distillation for Democratized Reincarnating Reinforcement Learning

## 1. Introduction

### Background

Reinforcement learning (RL) has achieved remarkable success in domains ranging from game playing to robotic control. However, the dominant paradigm of "tabula rasa" learning—training agents from scratch without leveraging prior knowledge—creates significant barriers to progress. Training state-of-the-art RL agents often requires millions of environment interactions and substantial computational resources, effectively limiting cutting-edge research to well-funded laboratories. This computational inequality undermines the democratization of RL research and slows collective scientific progress.

The emerging paradigm of "reincarnating RL" addresses these inefficiencies by leveraging prior computational work to accelerate training across design iterations or when transferring between agents. Recent approaches have explored various forms of prior computation, including learned network weights for fine-tuning, offline datasets, pretrained representations, and foundation models. However, current transfer mechanisms face critical limitations: transferring full policies creates storage and adaptation bottlenecks, while raw offline data requires substantial computational resources for reprocessing. Moreover, monolithic policy transfers often fail when source and target tasks differ in structure or objectives.

### Research Objectives

This research proposes a novel framework for **Hierarchical Skill Distillation (HSD)** that compresses large-scale trained RL policies into compact, composable skill libraries. Our primary objectives are:

1. **Develop automatic skill extraction methods** that identify and segment temporally extended behaviors from expert trajectories using information-theoretic principles and state-space analysis.

2. **Design efficient skill compression techniques** that distill extracted skills into lightweight, portable policy networks with explicit preconditions and termination conditions.

3. **Create a standardized skill composition interface** enabling researchers to efficiently query, sequence, and fine-tune skills from shared libraries using hierarchical policies.

4. **Validate the framework** through comprehensive experiments demonstrating significant reductions in computational requirements while maintaining or improving task performance.

### Significance

This research directly addresses the democratization challenge in reincarnating RL. By enabling efficient sharing of modular skill libraries rather than monolithic policies, we lower the barrier to entry for computationally constrained researchers. The proposed approach has three key advantages: (1) **Modularity**—skills can be selectively reused and recombined for novel tasks; (2) **Efficiency**—compressed skill representations reduce storage by 10-50x compared to full policies; (3) **Adaptability**—hierarchical composition allows rapid fine-tuning for task variations without retraining primitive skills. These contributions align with the workshop's vision of making large-scale RL problems accessible to the broader research community.

## 2. Methodology

### 2.1 Problem Formulation

We consider a setting where a resource-rich laboratory has trained a high-performing policy $\pi_{expert}$ on a complex task defined by MDP $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R, \gamma)$. Our goal is to extract and compress the knowledge embedded in $\pi_{expert}$ into a skill library $\mathcal{L} = \{(\omega_i, \pi_i, \beta_i, \phi_i)\}_{i=1}^{K}$, where each skill $\omega_i$ consists of a lightweight policy $\pi_i$, termination function $\beta_i$, and precondition embedding $\phi_i$. A downstream researcher can then leverage $\mathcal{L}$ to accelerate learning on related tasks with minimal computational overhead.

### 2.2 Automatic Skill Extraction

#### 2.2.1 Trajectory Collection and Preprocessing

We first collect a dataset of expert trajectories $\mathcal{D} = \{\tau_1, \tau_2, ..., \tau_N\}$ by rolling out $\pi_{expert}$ in the environment, where each trajectory $\tau_j = \{(s_0, a_0), (s_1, a_1), ..., (s_T, a_T)\}$.

#### 2.2.2 State-Space Clustering for Skill Boundaries

We identify natural skill boundaries using a combination of state-space clustering and behavioral change detection. First, we learn a state encoder $f_\theta: \mathcal{S} \rightarrow \mathbb{R}^d$ using a contrastive learning objective:

$$\mathcal{L}_{contrastive} = -\mathbb{E}_{(s_t, s_{t+k}) \sim \mathcal{D}} \left[ \log \frac{\exp(f_\theta(s_t)^\top f_\theta(s_{t+k}) / \tau)}{\sum_{s^- \in \mathcal{N}} \exp(f_\theta(s_t)^\top f_\theta(s^-) / \tau)} \right]$$

where $s_{t+k}$ represents temporally proximate states (positive pairs) and $\mathcal{N}$ contains negative samples from different trajectory segments.

We then apply hierarchical clustering on the encoded states to identify $M$ distinct state regions $\{C_1, C_2, ..., C_M\}$. Skill boundaries are detected at transition points where $f_\theta(s_t)$ moves from one cluster to another:

$$b_t = \mathbb{1}[\text{cluster}(s_t) \neq \text{cluster}(s_{t+1})]$$

#### 2.2.3 Mutual Information Maximization for Skill Refinement

To ensure extracted skills are behaviorally coherent, we refine segmentation using mutual information maximization. For each candidate skill segment $\omega$, we maximize:

$$I(\omega; \tau_{s:t}) = H(\omega) - H(\omega | \tau_{s:t})$$

where $\tau_{s:t}$ represents the trajectory segment from step $s$ to $t$. We implement this using a variational lower bound with a skill discriminator $q_\psi(\omega | \tau_{s:t})$:

$$\mathcal{L}_{MI} = \mathbb{E}_{\omega, \tau_{s:t}} [\log q_\psi(\omega | \tau_{s:t})]$$

The final skill extraction combines boundary detection and MI maximization through an iterative refinement process that alternates between updating cluster assignments and skill discriminators until convergence.

### 2.3 Skill Compression via Distillation

#### 2.3.1 Lightweight Policy Networks

For each extracted skill $\omega_i$, we distill the corresponding behavioral segments into a compact policy network $\pi_i(a|s; \theta_i)$. We employ a two-stage distillation process:

**Stage 1: Behavioral Cloning**
$$\mathcal{L}_{BC} = -\mathbb{E}_{(s,a) \sim \mathcal{D}_{\omega_i}} [\log \pi_i(a|s; \theta_i)]$$

where $\mathcal{D}_{\omega_i}$ contains state-action pairs from trajectory segments labeled as skill $\omega_i$.

**Stage 2: DAgger-style Refinement**
To address distribution shift, we iteratively collect corrective data by rolling out $\pi_i$ and querying $\pi_{expert}$ for corrections:

$$\mathcal{D}_{\omega_i} \leftarrow \mathcal{D}_{\omega_i} \cup \{(s, \pi_{expert}(s)) : s \sim \rho^{\pi_i}\}$$

#### 2.3.2 Termination Function Learning

Each skill requires an explicit termination condition $\beta_i(s) \in [0, 1]$ indicating the probability of skill completion. We train termination functions using skill boundary labels:

$$\mathcal{L}_{term} = -\mathbb{E}_{s \sim \mathcal{D}_{\omega_i}} [y_s \log \beta_i(s) + (1-y_s) \log(1-\beta_i(s))]$$

where $y_s = 1$ if state $s$ corresponds to a skill boundary and $y_s = 0$ otherwise.

#### 2.3.3 Precondition Embedding

To enable efficient skill selection, we learn precondition embeddings $\phi_i \in \mathbb{R}^p$ that encode the state distributions where skill $\omega_i$ is applicable:

$$\phi_i = \frac{1}{|\mathcal{D}_{\omega_i}^{init}|} \sum_{s \in \mathcal{D}_{\omega_i}^{init}} f_\theta(s)$$

where $\mathcal{D}_{\omega_i}^{init}$ contains initial states of skill $\omega_i$ segments.

#### 2.3.4 Network Compression

To achieve 10-50x storage reduction, we apply structured pruning and quantization to each skill policy:

1. **Pruning**: Remove neurons with weight magnitudes below threshold $\epsilon_{prune}$
2. **Quantization**: Convert weights to 8-bit integers using post-training quantization
3. **Knowledge Distillation**: Fine-tune compressed networks to match original outputs:

$$\mathcal{L}_{KD} = \text{KL}(\pi_i^{compressed}(\cdot|s) \| \pi_i^{original}(\cdot|s))$$

### 2.4 Skill Composition Interface

#### 2.4.1 Hierarchical Policy Architecture

We design a two-level hierarchical policy where a high-level controller $\pi_H(\omega|s)$ selects skills from the library, and low-level skill policies $\pi_\omega(a|s)$ execute primitive actions:

$$\pi(a|s) = \sum_{\omega \in \mathcal{L}} \pi_H(\omega|s) \cdot \pi_\omega(a|s)$$

#### 2.4.2 Skill Query Mechanism

The high-level policy queries skills based on precondition compatibility:

$$\text{compatibility}(s, \omega_i) = \exp\left(-\|f_\theta(s) - \phi_i\|^2 / \sigma^2\right)$$

Skills with compatibility below threshold $\tau_{compat}$ are masked from selection.

#### 2.4.3 Fine-tuning Protocol

Downstream users can fine-tune the hierarchical system using:

1. **Frozen Skills**: Train only $\pi_H$ while keeping skill policies fixed
2. **Full Fine-tuning**: Update both levels with reduced learning rate for skills
3. **Skill Augmentation**: Add new task-specific skills to the library

The training objective combines task reward with skill regularization:

$$\mathcal{L}_{finetune} = -\mathbb{E}_{\pi}[R(s,a)] + \lambda \text{KL}(\pi_\omega \| \pi_\omega^{pretrained})$$

### 2.5 Experimental Design

#### 2.5.1 Benchmark Environments

We evaluate on two established benchmark suites:

1. **Atari Games**: 10 games spanning different skill requirements (Breakout, Seaquest, Montezuma's Revenge, etc.)
2. **MuJoCo Locomotion**: HalfCheetah, Ant, Humanoid with varying task objectives

#### 2.5.2 Baselines

- **Tabula Rasa**: Standard PPO/SAC training from scratch
- **Full Policy Transfer**: Fine-tuning entire pretrained policies
- **Offline RL**: CQL/IQL on collected trajectories
- **Option-Critic**: End-to-end hierarchical learning without skill distillation

#### 2.5.3 Evaluation Metrics

1. **Sample Efficiency**: Environment interactions to reach 90% of expert performance
2. **Computational Cost**: GPU hours for training
3. **Storage Efficiency**: Model size in MB
4. **Transfer Success Rate**: Percentage of target tasks where library improves over baselines
5. **Skill Reusability**: Average number of tasks utilizing each skill

#### 2.5.4 Ablation Studies

- Impact of skill granularity (varying $K$)
- Compression ratio vs. performance trade-off
- Precondition embedding dimensionality
- Fine-tuning strategies comparison

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative Improvements**: We expect skill libraries to achieve:
   - 5-10x reduction in sample complexity compared to tabula rasa learning
   - 10-50x reduction in storage requirements compared to full policy transfer
   - Comparable or superior final performance to full policy fine-tuning

2. **Qualitative Contributions**:
   - Open-source skill library release for Atari and MuJoCo benchmarks
   - Standardized API specification for skill library format and composition
   - Comprehensive analysis of skill transferability across related tasks

3. **Methodological Advances**:
   - Novel information-theoretic skill extraction algorithm
   - Efficient compression techniques preserving behavioral fidelity
   - Hierarchical composition framework with theoretical grounding

### Broader Impact

This research directly supports the democratization of reinforcement learning. By enabling efficient sharing of modular skill libraries, we lower computational barriers that currently exclude resource-limited researchers from working on complex RL problems. The proposed standardized interfaces could catalyze a collaborative ecosystem where the community incrementally builds and improves shared skill repositories, analogous to how pretrained language models transformed NLP research.

Furthermore, our framework addresses key challenges identified in reincarnating RL: handling suboptimality of prior computation through selective skill reuse, enabling continual agent improvement through library expansion, and providing clear evaluation protocols for benchmarking transfer efficiency. The modular nature of skill libraries also facilitates interpretability and debugging, as researchers can inspect and validate individual skills before deployment.

The practical implications extend to real-world applications where computational efficiency is paramount, including robotics, autonomous systems, and interactive AI. By making sophisticated behavioral capabilities accessible through lightweight, reusable components, we bridge the gap between large-scale RL research and practical deployment scenarios.