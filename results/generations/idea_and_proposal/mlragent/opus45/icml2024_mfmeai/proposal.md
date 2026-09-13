# Research Proposal: Hierarchical Skill Abstraction Framework for Bridging Multi-modal Foundation Models with Low-level Robot Control

## 1. Introduction

### Background

The emergence of Multi-modal Foundation Models (MFMs) such as GPT-4V, CLIP, and Gemini has revolutionized artificial intelligence by demonstrating remarkable capabilities in understanding and reasoning across visual, linguistic, and other sensory modalities. These models exhibit impressive high-level cognitive abilities, including scene understanding, task planning, and contextual reasoning. Concurrently, the field of Embodied AI has progressed significantly, with robots increasingly expected to operate in unstructured, open-ended environments alongside humans.

However, a fundamental disconnect persists between the abstract reasoning capabilities of MFMs and the precise, real-time motor control requirements of physical robots. This "semantic-to-motor gap" represents one of the most pressing challenges in deploying MFM-powered embodied agents. While an MFM can understand a command like "carefully place the fragile vase on the shelf," translating this understanding into appropriate force modulation, trajectory planning, and reactive adjustments remains problematic.

Current approaches to bridging this gap fall into two categories, each with significant limitations. The first involves fine-tuning entire foundation models for specific robotic tasks, which is computationally prohibitive and often leads to catastrophic forgetting of general capabilities. The second relies on predefined action primitives that map MFM outputs to discrete motor commands, severely limiting the expressiveness and adaptability of robot behaviors. Recent works such as SkillDiffuser and GSL have made progress in hierarchical skill learning, yet they lack principled mechanisms for seamlessly integrating MFM's rich semantic understanding with continuous, reactive motor control.

### Research Objectives

This research proposes **SkillBridge**, a novel hierarchical framework designed to bridge MFMs with low-level robot control through learnable skill token abstractions. Our specific objectives are:

1. To develop a learnable skill token library that encodes parameterized motor skills as intermediate representations between semantic MFM outputs and continuous motor commands.
2. To design lightweight adapter mechanisms that efficiently translate MFM's multimodal reasoning into skill token sequences without requiring full model fine-tuning.
3. To create a diffusion-based skill execution module that generates smooth, reactive trajectories conditioned on skill tokens.
4. To validate the framework's effectiveness across diverse manipulation tasks requiring both semantic understanding and precise motor control.

### Significance

This research addresses a critical bottleneck in practical MFM-powered robotics. By introducing a principled intermediate representation layer, SkillBridge enables:
- **Computational Efficiency**: Avoiding expensive full-model fine-tuning while preserving MFM's general capabilities.
- **Enhanced Expressiveness**: Moving beyond discrete action primitives to continuous, parameterized skill representations.
- **Improved Generalization**: Facilitating transfer of learned skills across tasks through compositional skill token combinations.
- **Practical Deployability**: Enabling real-time reactive control essential for safe human-robot interaction.

## 2. Methodology

### 2.1 System Architecture Overview

SkillBridge comprises three interconnected modules: (1) a Skill Token Library, (2) an MFM Skill Decoder, and (3) a Diffusion-based Skill Executor. The architecture maintains the frozen MFM backbone while learning lightweight intermediate representations that bridge semantic understanding with motor execution.

### 2.2 Skill Token Library

The Skill Token Library $\mathcal{S} = \{s_1, s_2, ..., s_K\}$ consists of $K$ learnable embedding vectors, where each token $s_i \in \mathbb{R}^d$ encodes a parameterized motor skill. Unlike discrete action primitives, each skill token represents a continuous family of behaviors characterized by semantic attributes and execution parameters.

Each skill token $s_i$ is associated with:
- A semantic descriptor $\phi_i \in \mathbb{R}^{d_s}$ capturing the skill's high-level meaning (e.g., "grasp," "push," "rotate")
- A parameter space $\Theta_i \subset \mathbb{R}^{d_p}$ defining continuous modulation factors (e.g., force magnitude, velocity profile, precision level)

The skill token embedding is computed as:

$$s_i = \text{MLP}_{\text{skill}}([\phi_i; \theta_i])$$

where $\theta_i \in \Theta_i$ represents specific parameter instantiation and $[\cdot;\cdot]$ denotes concatenation.

**Skill Token Initialization**: We initialize skill tokens using a clustering approach on demonstration trajectories. Given a dataset of expert demonstrations $\mathcal{D} = \{(\tau_j, l_j)\}_{j=1}^N$ where $\tau_j$ is a trajectory and $l_j$ is the language instruction, we:

1. Extract trajectory segments using change-point detection based on velocity and contact state transitions
2. Encode segments using a temporal convolutional encoder $E_\tau$
3. Apply k-means clustering to obtain initial skill prototypes
4. Align prototypes with language descriptions using CLIP embeddings

### 2.3 MFM Skill Decoder

The MFM Skill Decoder translates the frozen MFM's multimodal representations into skill token sequences. Given visual observation $v_t$ and language instruction $l$, the MFM produces a contextualized representation:

$$h_{\text{MFM}} = \text{MFM}_{\text{frozen}}(v_t, l)$$

We introduce lightweight adapter layers $\mathcal{A}$ consisting of bottleneck transformers that process MFM outputs:

$$h_{\text{adapted}} = \mathcal{A}(h_{\text{MFM}}) = \text{FFN}(\text{CrossAttn}(Q_a, h_{\text{MFM}}, h_{\text{MFM}}))$$

where $Q_a \in \mathbb{R}^{M \times d}$ are learnable query tokens and $M$ is the maximum skill sequence length.

**Skill Token Selection**: The adapted representations are used to compute attention weights over the skill token library:

$$\alpha_{ij} = \frac{\exp(h_{\text{adapted}}^{(i)} \cdot s_j / \sqrt{d})}{\sum_{k=1}^K \exp(h_{\text{adapted}}^{(i)} \cdot s_k / \sqrt{d})}$$

The selected skill sequence $\hat{S} = [\hat{s}_1, ..., \hat{s}_M]$ is computed via soft attention:

$$\hat{s}_i = \sum_{j=1}^K \alpha_{ij} s_j$$

**Parameter Prediction**: For each selected skill, we predict continuous parameters using a parameter head:

$$\hat{\theta}_i = \text{MLP}_{\text{param}}([h_{\text{adapted}}^{(i)}; \hat{s}_i])$$

### 2.4 Diffusion-based Skill Executor

The Skill Executor generates smooth, reactive trajectories conditioned on skill tokens using a conditional diffusion policy. We adopt a denoising diffusion probabilistic model (DDPM) framework.

**Forward Process**: Given a ground-truth action sequence $a_{0:H}$ over horizon $H$, the forward process adds Gaussian noise:

$$q(a^{(n)}|a^{(n-1)}) = \mathcal{N}(a^{(n)}; \sqrt{1-\beta_n}a^{(n-1)}, \beta_n I)$$

where $\beta_n$ is the noise schedule and $n \in \{1, ..., N\}$ indexes diffusion steps.

**Reverse Process**: The denoising network $\epsilon_\theta$ predicts noise conditioned on skill tokens and proprioceptive state:

$$p_\theta(a^{(n-1)}|a^{(n)}, c) = \mathcal{N}(a^{(n-1)}; \mu_\theta(a^{(n)}, n, c), \sigma_n^2 I)$$

where the conditioning signal $c = [\hat{s}; \hat{\theta}; o_{\text{prop}}]$ combines the skill token, predicted parameters, and proprioceptive observations.

The denoising network architecture employs a U-Net with cross-attention layers:

$$\epsilon_\theta(a^{(n)}, n, c) = \text{UNet}(a^{(n)}, \text{CrossAttn}(a^{(n)}, c))$$

**Reactive Execution**: To enable reactive adjustments during execution, we implement a receding horizon approach. At each control step $t$, we:
1. Re-encode current observation $v_t$
2. Update skill parameters based on execution feedback
3. Generate action chunk $a_{t:t+H'}$ with shortened horizon $H' < H$
4. Execute first action and repeat

### 2.5 Training Procedure

**Stage 1: Skill Token Pre-training**
We pre-train the skill token library using contrastive learning on demonstration data:

$$\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(z_\tau, z_l)/\tau)}{\sum_{l' \in \mathcal{B}} \exp(\text{sim}(z_\tau, z_{l'})/\tau)}$$

where $z_\tau$ and $z_l$ are encoded trajectory segment and language description, $\mathcal{B}$ is the batch, and $\tau$ is temperature.

**Stage 2: Joint Training**
We jointly train the adapter layers, parameter predictor, and diffusion executor:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{diffusion}} + \lambda_1 \mathcal{L}_{\text{skill}} + \lambda_2 \mathcal{L}_{\text{param}}$$

where:
- $\mathcal{L}_{\text{diffusion}} = \mathbb{E}_{n, a_0, \epsilon}[||\epsilon - \epsilon_\theta(a^{(n)}, n, c)||^2]$
- $\mathcal{L}_{\text{skill}} = \text{CE}(\alpha, y_{\text{skill}})$ is skill classification loss
- $\mathcal{L}_{\text{param}} = ||\hat{\theta} - \theta^*||^2$ is parameter regression loss

### 2.6 Data Collection

**Simulation Data**: We utilize IsaacGym and MuJoCo simulators to generate large-scale demonstrations across diverse manipulation tasks including pick-and-place, tool use, and articulated object manipulation. We procedurally generate 500+ task variations with domain randomization.

**Real-World Data**: We collect 50 hours of teleoperation data using a Franka Emika robot with a 3D SpaceMouse interface. Tasks include tabletop manipulation with varying object properties (fragile, heavy, deformable) and environmental constraints.

### 2.7 Experimental Design

**Benchmarks**:
1. **CALVIN**: Multi-task long-horizon manipulation benchmark
2. **RLBench**: 100 manipulation tasks with language instructions
3. **Real-world evaluation**: 20 tasks on physical Franka robot

**Baselines**:
1. RT-2: End-to-end vision-language-action model
2. SkillDiffuser: Hierarchical diffusion with discrete skills
3. SPECI: Continual imitation learning framework
4. Direct MFM + motion primitives

**Evaluation Metrics**:
- **Task Success Rate (SR)**: Percentage of successfully completed tasks
- **Semantic Alignment Score (SAS)**: Cosine similarity between executed behavior and instruction embedding
- **Motion Smoothness (MS)**: Average jerk magnitude across trajectories
- **Reactive Adaptation Score (RAS)**: Success rate under perturbations
- **Computational Efficiency**: Inference time and GPU memory usage

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Performance Improvements**: We anticipate SkillBridge will achieve 15-25% higher task success rates compared to existing hierarchical approaches on long-horizon manipulation tasks, particularly for tasks requiring both semantic understanding and precise force control.

2. **Enhanced Generalization**: The compositional nature of skill tokens should enable zero-shot transfer to novel task combinations, with expected 40%+ success on unseen task compositions versus <20% for baselines.

3. **Computational Efficiency**: By keeping the MFM frozen and learning lightweight adapters, we expect 10x reduction in training compute compared to full fine-tuning approaches while maintaining comparable performance.

4. **Interpretability**: The discrete skill token selection provides human-interpretable intermediate representations, enabling diagnosis and debugging of failure cases.

### Broader Impact

This research directly addresses the critical challenge of deploying MFM-powered robots in real-world settings. The SkillBridge framework has potential applications in:

- **Manufacturing**: Enabling flexible automation with natural language task specification
- **Healthcare**: Assisting with manipulation tasks requiring both semantic understanding and gentle, precise movements
- **Domestic Robotics**: Powering household robots that understand contextual instructions

The principled hierarchical abstraction approach established in this work provides a foundation for future research in MFM-embodied AI integration, contributing to the broader goal of creating generally capable robotic systems that can safely and effectively operate alongside humans in diverse, open-ended environments.