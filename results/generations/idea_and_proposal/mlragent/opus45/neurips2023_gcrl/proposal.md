# Research Proposal: Goal-Conditioned RL via Contrastive World Models for Molecular Discovery

## 1. Introduction

### Background

Molecular discovery stands at the frontier of computational chemistry and drug design, where the goal is to identify novel molecules with specific desired properties such as binding affinity, solubility, synthesizability, and safety profiles. Traditional approaches to molecular optimization rely heavily on expert-crafted reward functions or expensive high-throughput screening, which are often inadequate for capturing the nuanced relationships between molecular structure and function. Goal-conditioned reinforcement learning (GCRL) offers a compelling alternative by allowing users to specify desired outcomes directly—potentially through target molecular properties or exemplar molecules—rather than engineering complex reward functions.

However, applying GCRL to molecular discovery presents unique challenges that distinguish it from conventional robotics or game-playing domains. First, the goal space in molecular optimization is continuous, high-dimensional, and often only partially observable through expensive computational simulations or wet-lab experiments. Second, the chemical space is astronomically large (estimated at $10^{60}$ drug-like molecules), making exploration extremely challenging. Third, standard distance metrics in molecular space (e.g., Tanimoto similarity on fingerprints) fail to capture meaningful notions of goal proximity, as chemically similar molecules can have vastly different properties and vice versa.

Recent advances in self-supervised representation learning, particularly contrastive learning methods, have demonstrated remarkable success in learning semantically meaningful embeddings across various domains. Simultaneously, world models have emerged as powerful tools for sample-efficient reinforcement learning by enabling planning in learned latent spaces. The intersection of these approaches with GCRL presents an exciting opportunity to address the fundamental challenges of molecular optimization.

### Research Objectives

This research proposes **MolGCRL** (Molecular Goal-Conditioned Reinforcement Learning), a novel framework that integrates contrastive world models with goal-conditioned policy learning for molecular discovery. Our primary objectives are:

1. **Develop a contrastive representation learning scheme** that maps molecular graphs and target properties into a shared latent space where Euclidean distance meaningfully reflects both synthesizability (reachability through chemical transformations) and property similarity.

2. **Learn a latent dynamics model** that accurately predicts the effects of chemical reactions in the learned representation space, enabling efficient planning and goal-reaching.

3. **Design a goal-conditioned policy** that leverages hindsight experience replay in the learned latent space to achieve sample-efficient molecular optimization.

4. **Validate the framework** on challenging multi-objective drug design benchmarks, demonstrating improved sample efficiency and generalization compared to existing methods.

### Significance

This research addresses critical gaps at the intersection of GCRL, representation learning, and molecular discovery. By establishing principled connections between contrastive learning objectives and goal-conditioned value functions, we provide theoretical grounding for why learned representations should facilitate effective goal-reaching. The practical significance is substantial: successful molecular optimization algorithms could accelerate drug discovery pipelines, reduce development costs, and enable personalized medicine approaches. Furthermore, our framework exemplifies how GCRL can be adapted to domains with continuous, high-dimensional goal spaces and sparse feedback—insights transferable to other challenging application areas.

## 2. Methodology

### 2.1 Problem Formulation

We formalize molecular optimization as a Goal-Conditioned Markov Decision Process (GC-MDP) defined by the tuple $(\mathcal{S}, \mathcal{A}, \mathcal{G}, P, r, \gamma)$, where:
- $\mathcal{S}$: State space of molecular graphs $s = (V, E)$ with node features (atoms) and edge features (bonds)
- $\mathcal{A}$: Action space of valid chemical transformations (reactions, functional group additions/removals)
- $\mathcal{G}$: Goal space of target molecular properties $g \in \mathbb{R}^d$ (e.g., QED, LogP, binding affinity)
- $P(s'|s, a)$: Transition dynamics defined by chemical reaction rules
- $r(s, a, g) = -\|f(s') - g\|_2$: Sparse reward based on property similarity at episode end
- $\gamma$: Discount factor

The objective is to learn a goal-conditioned policy $\pi(a|s, g)$ that maximizes expected return:
$$J(\pi) = \mathbb{E}_{g \sim p(g), \tau \sim \pi}\left[\sum_{t=0}^{T} \gamma^t r(s_t, a_t, g)\right]$$

### 2.2 Contrastive Representation Learning

#### Molecular Encoder Architecture

We employ a Graph Neural Network (GNN) encoder $\phi_\theta: \mathcal{S} \rightarrow \mathbb{R}^k$ that maps molecular graphs to latent representations. Specifically, we use a Message Passing Neural Network (MPNN) with attention mechanisms:

$$h_v^{(l+1)} = \text{MLP}\left(h_v^{(l)} + \sum_{u \in \mathcal{N}(v)} \alpha_{uv} \cdot W^{(l)} h_u^{(l)}\right)$$

where $\alpha_{uv}$ are learned attention weights and $\mathcal{N}(v)$ denotes the neighbors of atom $v$. The graph-level representation is obtained through a readout function:
$$z_s = \phi_\theta(s) = \text{ReadOut}(\{h_v^{(L)}\}_{v \in V})$$

#### Temporal Contrastive Objective

The core insight of MolGCRL is to learn representations where Euclidean distance corresponds to reachability through chemical transformations. We define positive pairs as molecules reachable within $k$ transformation steps and negative pairs as random molecules from the dataset.

Given a trajectory $\tau = (s_0, a_0, s_1, \ldots, s_T)$, the contrastive loss is:
$$\mathcal{L}_{\text{contrast}} = -\mathbb{E}_{\tau}\left[\sum_{t=0}^{T-k} \log \frac{\exp(\text{sim}(z_{s_t}, z_{s_{t+k}})/\tau)}{\sum_{j} \exp(\text{sim}(z_{s_t}, z_{s_j})/\tau)}\right]$$

where $\text{sim}(z_1, z_2) = z_1^\top z_2 / (\|z_1\| \|z_2\|)$ is cosine similarity and $\tau$ is a temperature parameter.

#### Property-Aligned Representation

To ensure the latent space also captures property similarity, we introduce a property prediction head $\psi_\eta: \mathbb{R}^k \rightarrow \mathbb{R}^d$ and add a supervised loss:
$$\mathcal{L}_{\text{prop}} = \mathbb{E}_{s \sim \mathcal{D}}\left[\|\psi_\eta(\phi_\theta(s)) - f(s)\|_2^2\right]$$

where $f(s)$ returns the ground-truth properties. The combined representation objective is:
$$\mathcal{L}_{\text{repr}} = \mathcal{L}_{\text{contrast}} + \lambda_{\text{prop}} \mathcal{L}_{\text{prop}}$$

### 2.3 Latent Dynamics Model

We learn a forward dynamics model $T_\omega: \mathbb{R}^k \times \mathcal{A} \rightarrow \mathbb{R}^k$ that predicts the next-state representation given the current latent state and action:
$$\hat{z}_{t+1} = T_\omega(z_t, a_t)$$

The dynamics model is trained to minimize prediction error:
$$\mathcal{L}_{\text{dyn}} = \mathbb{E}_{\tau}\left[\sum_{t=0}^{T-1} \|T_\omega(\phi_\theta(s_t), a_t) - \text{sg}(\phi_\theta(s_{t+1}))\|_2^2\right]$$

where $\text{sg}(\cdot)$ denotes stop-gradient to prevent representation collapse.

### 2.4 Goal-Conditioned Policy Learning

#### Latent Goal Representation

Goals (target properties) are encoded using a property encoder $\xi_\mu: \mathbb{R}^d \rightarrow \mathbb{R}^k$ that maps property vectors to the same latent space as molecular representations:
$$z_g = \xi_\mu(g)$$

This encoder is trained jointly with the molecular encoder using an alignment loss:
$$\mathcal{L}_{\text{align}} = \mathbb{E}_{s \sim \mathcal{D}}\left[\|\xi_\mu(f(s)) - \phi_\theta(s)\|_2^2\right]$$

#### Policy Architecture and Training

The goal-conditioned policy $\pi_\nu(a|z_s, z_g)$ is parameterized as a neural network operating in the latent space. We use Soft Actor-Critic (SAC) with the following modifications:

1. **Latent Goal-Conditioned Q-function**: 
$$Q_\chi(z_s, a, z_g) = \text{MLP}([z_s; a; z_g])$$

2. **Latent Distance Reward**: Instead of sparse property-based rewards, we use dense rewards based on latent distance:
$$r_{\text{latent}}(s, a, g) = -\|z_{s'} - z_g\|_2 + \beta \cdot \mathbb{1}[\|z_{s'} - z_g\|_2 < \epsilon]$$

where $\beta$ is a bonus for reaching the goal region.

#### Hindsight Experience Replay in Latent Space

We employ Hindsight Experience Replay (HER) adapted for continuous goal spaces. For each trajectory, we relabel goals using:
1. **Future strategy**: Sample future states as achieved goals
2. **Property interpolation**: Create synthetic goals by interpolating between achieved properties

The relabeled transitions $(s_t, a_t, s_{t+1}, g')$ where $g' = f(s_{t+k})$ for some $k > 0$ provide dense learning signals.

### 2.5 Complete Training Algorithm

The complete MolGCRL training procedure is summarized in Algorithm 1:

**Algorithm 1: MolGCRL Training**
```
Initialize: Encoder φ_θ, property head ψ_η, dynamics model T_ω, 
           goal encoder ξ_μ, policy π_ν, Q-function Q_χ
Initialize: Replay buffer D, molecular dataset D_mol

For each iteration:
    # Data Collection
    Sample goal g ~ p(g)
    Collect trajectory τ using π_ν with ε-greedy exploration
    Store τ in D
    
    # Representation Learning (every N_repr steps)
    Sample batch B from D ∪ D_mol
    Update θ, η by minimizing L_repr
    Update ω by minimizing L_dyn
    Update μ by minimizing L_align
    
    # Policy Learning
    Sample batch B' from D
    Apply HER to create relabeled transitions
    Compute latent representations for states and goals
    Update χ, ν using SAC objectives in latent space
```

### 2.6 Experimental Design

#### Datasets and Benchmarks

1. **ZINC250K**: Standard molecular optimization benchmark with single-objective tasks (QED, LogP)
2. **GuacaMol**: Multi-objective optimization suite with synthesis-aware metrics
3. **DockingBench**: Protein-ligand binding affinity optimization using AutoDock Vina

#### Baseline Methods

- **Mol-AIR**: Adaptive intrinsic reward RL for molecular generation
- **REINVENT**: Standard policy gradient with reward shaping
- **GCPN**: Graph Convolutional Policy Network
- **RationaleRL**: Rationale-guided molecular generation
- **Random Search**: Uniform sampling baseline

#### Evaluation Metrics

1. **Sample Efficiency**: Number of oracle calls to achieve target property thresholds
2. **Success Rate**: Percentage of generated molecules achieving all target properties
3. **Diversity**: Internal diversity measured by average pairwise Tanimoto distance
4. **Novelty**: Percentage of generated molecules not in training set
5. **Synthesizability**: SA score and retrosynthetic accessibility (RAScore)
6. **Generalization**: Performance on held-out target properties

#### Ablation Studies

We conduct ablations to understand component contributions:
- Contrastive objective vs. reconstruction-based representation learning
- Temporal positive pairs vs. random positive pairs
- Latent dynamics model vs. model-free policy learning
- HER in latent space vs. property space

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Sample Efficiency**: We anticipate MolGCRL will require 3-5× fewer oracle evaluations compared to reward-shaping baselines, critical for expensive property evaluations.

2. **Superior Multi-Objective Optimization**: The learned latent space should enable better Pareto front coverage for conflicting objectives (e.g., potency vs. selectivity).

3. **Enhanced Generalization**: By learning transferable representations, MolGCRL should generalize to novel target properties with minimal fine-tuning.

4. **Interpretable Goal Representations**: The aligned latent space will enable visualization and interpretation of goal-reaching trajectories.

### Broader Impact

**Scientific Contributions**: This work establishes formal connections between contrastive learning and goal-conditioned value functions, showing that temporal contrastive objectives implicitly learn a potential function for goal-reaching. These insights extend beyond molecular discovery to any domain with structured state transitions.

**Practical Applications**: Successful deployment could accelerate early-stage drug discovery by enabling chemists to specify target profiles directly, reducing reliance on hand-crafted scoring functions. The framework naturally extends to materials design, catalyst optimization, and other molecular engineering challenges.

**Community Impact**: We will release MolGCRL as an open-source library with pre-trained models and comprehensive benchmarks, fostering reproducibility and enabling broader adoption of GCRL in computational chemistry.

**Limitations and Risks**: Learned models may exhibit biases present in training data, potentially overlooking novel chemical scaffolds. We will address this through diverse data collection and explicit novelty-seeking exploration.