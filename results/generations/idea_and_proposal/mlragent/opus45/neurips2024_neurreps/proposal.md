# Research Proposal: Equivariant World Models for Robotic Manipulation via Learned Symmetry Discovery

## 1. Introduction

### Background

The intersection of geometric deep learning and robotics represents one of the most promising frontiers in machine learning research. World models—internal representations that enable agents to predict future states and plan actions—are fundamental to sample-efficient robot learning. However, current approaches to learning world models typically require enormous amounts of interaction data, often millions of transitions, making practical deployment challenging and costly.

Recent advances in geometric deep learning have demonstrated that incorporating symmetry priors into neural network architectures can dramatically improve sample efficiency, generalization, and robustness (Bronstein et al., 2021). In robotics specifically, SE(3)-equivariant networks have shown remarkable improvements in manipulation tasks by explicitly respecting the geometric structure of 3D space (Zhang & She, 2026; Hoang et al., 2025). The principle underlying these successes mirrors observations in neuroscience: neural circuits in biological systems often preserve the geometric and topological structure of the signals they process, suggesting a fundamental computational strategy for efficient information processing.

However, a critical limitation persists in current equivariant approaches: they assume the relevant symmetry groups are known a priori. In practice, robotic manipulation tasks exhibit complex, partial, or approximate symmetries that are difficult to specify beforehand. A task involving pouring liquid, for instance, may exhibit rotational symmetry around the vertical axis but break this symmetry when the cup approaches full capacity. Similarly, manipulating deformable objects introduces state-dependent symmetries that evolve during interaction.

### Research Objectives

This research proposes to develop a novel framework for jointly learning world models and their underlying symmetry structure from robotic interaction data. Our specific objectives are:

1. **Symmetry Discovery**: Develop a differentiable module that identifies approximate equivariances from state-action trajectories using continuous Lie algebra parameterization.

2. **Adaptive Architecture**: Design equivariant network architectures that dynamically adjust their structure based on discovered symmetries without requiring manual specification.

3. **Controlled Symmetry Breaking**: Create regularization mechanisms that encourage models to respect learned symmetries while permitting task-specific adaptations where necessary.

4. **Empirical Validation**: Demonstrate significant improvements in sample efficiency, prediction accuracy, and downstream policy performance on robotic manipulation benchmarks.

### Significance

This research addresses a fundamental gap between theoretical advances in geometric deep learning and practical robotic applications. By enabling automatic symmetry discovery, we eliminate the need for expert knowledge in specifying geometric priors, democratizing access to equivariant methods. Furthermore, this work provides insights into how biological neural systems might similarly discover and exploit environmental structure—a question of deep relevance to computational neuroscience. The convergence of principles across artificial and biological systems suggests substrate-agnostic computational strategies that merit systematic investigation.

## 2. Methodology

### 2.1 Problem Formulation

We consider a Markov Decision Process (MDP) defined by the tuple $(\mathcal{S}, \mathcal{A}, T, R)$, where $\mathcal{S}$ is the state space, $\mathcal{A}$ is the action space, $T: \mathcal{S} \times \mathcal{A} \rightarrow \mathcal{S}$ is the transition function, and $R: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}$ is the reward function. Our goal is to learn a world model $\hat{T}_\theta$ that approximates the true dynamics while discovering and exploiting underlying symmetries.

A function $f: \mathcal{X} \rightarrow \mathcal{Y}$ is equivariant with respect to a group $G$ if:

$$f(\rho_\mathcal{X}(g) \cdot x) = \rho_\mathcal{Y}(g) \cdot f(x), \quad \forall g \in G, x \in \mathcal{X}$$

where $\rho_\mathcal{X}$ and $\rho_\mathcal{Y}$ are group representations on the input and output spaces, respectively.

### 2.2 Framework Architecture

Our framework consists of three interconnected components:

#### Component 1: Symmetry Discovery Module

We parameterize candidate symmetries using the Lie algebra $\mathfrak{g}$ of potential symmetry groups. For a Lie group $G$, elements near the identity can be expressed as $g = \exp(\sum_{i=1}^{k} \alpha_i A_i)$, where $\{A_i\}$ form a basis for $\mathfrak{g}$ and $\alpha_i \in \mathbb{R}$.

Given a dataset of state-action-next-state transitions $\mathcal{D} = \{(s_t, a_t, s_{t+1})\}$, we define the symmetry discovery objective. Let $\phi_\omega: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}^k$ be a neural network that outputs Lie algebra coefficients $\alpha = (\alpha_1, ..., \alpha_k)$. The symmetry score for a candidate transformation $g_\alpha = \exp(\sum_i \alpha_i A_i)$ is computed as:

$$\mathcal{L}_{sym}(\omega) = \mathbb{E}_{(s,a,s') \sim \mathcal{D}} \left[ \left\| T(g_\alpha \cdot s, g_\alpha \cdot a) - g_\alpha \cdot T(s, a) \right\|^2 \right]$$

To discover symmetries that hold approximately across the dataset, we introduce a symmetry consistency loss:

$$\mathcal{L}_{cons}(\omega) = \text{Var}_{(s,a,s') \sim \mathcal{D}} \left[ \phi_\omega(s, a) \right] - \lambda_1 \left\| \mathbb{E}[\phi_\omega(s,a)] \right\|^2$$

The first term encourages low variance in discovered symmetries (consistency), while the second term prevents collapse to trivial solutions by encouraging non-zero symmetry parameters.

#### Component 2: Adaptive Equivariant World Model

We design an adaptive equivariant architecture that incorporates discovered symmetries through learnable equivariant layers. The world model takes the form:

$$\hat{s}_{t+1} = f_\theta(s_t, a_t; G_\omega)$$

where $G_\omega$ represents the discovered symmetry group parameterized by $\omega$.

The core building block is an adaptive equivariant layer. Given discovered Lie algebra coefficients $\alpha = \phi_\omega(s, a)$, we construct equivariant kernels using the following procedure:

1. **Basis Construction**: Generate a set of equivariant basis functions $\{\psi_j^G\}$ for the estimated group $G_\omega$:

$$\psi_j^G(x) = \int_G \rho(g)^{-1} \psi_j(\rho(g) \cdot x) dg$$

where the integral is approximated via Monte Carlo sampling over $G_\omega$.

2. **Adaptive Convolution**: The equivariant convolution is defined as:

$$[f \star_G \kappa](x) = \sum_j w_j \int_G \psi_j^G(g^{-1} \cdot x) \kappa(g) dg$$

where $w_j$ are learnable weights and $\kappa$ is a learnable kernel.

3. **Soft Equivariance**: To handle approximate symmetries, we introduce a temperature-controlled interpolation:

$$\hat{f}(x) = \sigma(\beta) f_{equiv}(x) + (1 - \sigma(\beta)) f_{free}(x)$$

where $\beta$ is a learned parameter controlling the degree of equivariance enforcement, $\sigma$ is the sigmoid function, $f_{equiv}$ is the equivariant pathway, and $f_{free}$ is an unconstrained pathway.

#### Component 3: Symmetry-Aware Regularization

We introduce a regularization scheme that balances symmetry preservation with task-specific flexibility:

$$\mathcal{L}_{reg} = \lambda_2 \mathcal{L}_{equiv} + \lambda_3 \mathcal{L}_{break}$$

The equivariance loss enforces consistency with discovered symmetries:

$$\mathcal{L}_{equiv} = \mathbb{E}_{s,a,g \sim G_\omega} \left[ \left\| \hat{T}_\theta(g \cdot s, g \cdot a) - g \cdot \hat{T}_\theta(s, a) \right\|^2 \right]$$

The controlled symmetry-breaking loss allows necessary violations:

$$\mathcal{L}_{break} = -H(\pi_{break}) + \lambda_4 \left\| \pi_{break} \right\|_1$$

where $\pi_{break}$ is a learned distribution over symmetry-breaking events and $H$ denotes entropy. This encourages sparse, high-entropy breaking patterns.

### 2.3 Training Procedure

The complete training objective combines prediction accuracy with symmetry-related losses:

$$\mathcal{L}_{total} = \mathcal{L}_{pred} + \mathcal{L}_{sym} + \mathcal{L}_{cons} + \mathcal{L}_{reg}$$

where:

$$\mathcal{L}_{pred} = \mathbb{E}_{(s,a,s') \sim \mathcal{D}} \left[ \left\| \hat{T}_\theta(s, a) - s' \right\|^2 \right]$$

**Algorithm 1: Joint Symmetry Discovery and World Model Learning**

```
Input: Dataset D, learning rates η_θ, η_ω, hyperparameters λ_1, λ_2, λ_3, λ_4
Initialize: World model parameters θ, symmetry discovery parameters ω

For epoch = 1 to N:
    For batch (s, a, s') in D:
        1. Compute symmetry parameters: α = φ_ω(s, a)
        2. Construct group elements: G_ω = {exp(Σ_i α_i A_i)}
        3. Forward pass through adaptive equivariant world model
        4. Compute L_pred, L_sym, L_cons, L_reg
        5. Update θ ← θ - η_θ ∇_θ L_total
        6. Update ω ← ω - η_ω ∇_ω L_total
    End For
    Anneal temperature β for soft equivariance
End For

Output: Learned world model T̂_θ, discovered symmetries G_ω
```

### 2.4 Experimental Design

**Benchmarks**: We evaluate on three robotic manipulation environments of increasing complexity:

1. **Block Pushing (Isaac Gym)**: A tabletop task with explicit SE(2) symmetry, serving as a validation environment.

2. **Pouring Task (MuJoCo)**: Liquid pouring with partial rotational symmetry that breaks near capacity limits.

3. **Deformable Object Manipulation (SoftGym)**: Cloth folding with complex, state-dependent symmetries.

**Baselines**: We compare against:
- Standard MLP world models (no geometric priors)
- Fixed SE(3)-equivariant networks (EquiForm, HEPi)
- Symmetry-aware world models with manually specified groups
- Data augmentation approaches simulating equivariance

**Evaluation Metrics**:

1. **Prediction Error**: Multi-step prediction MSE over rollout horizons of 10, 50, and 100 steps.

2. **Sample Efficiency**: Number of environment interactions required to achieve threshold prediction accuracy.

3. **Symmetry Alignment**: Cosine similarity between learned Lie algebra coefficients and ground-truth symmetry generators (where available).

4. **Policy Performance**: When used for model-based RL, we measure task success rate and cumulative reward.

5. **Generalization**: Zero-shot transfer performance to novel object poses, sizes, and configurations.

**Data Collection**: For each environment, we collect trajectories using random exploration and scripted policies, with dataset sizes ranging from 1K to 100K transitions to evaluate sample efficiency curves.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Sample Efficiency Gains**: We anticipate 5-10x reduction in required training interactions compared to non-equivariant baselines. Preliminary theoretical analysis suggests that exploiting $k$-dimensional symmetry groups should reduce sample complexity by a factor proportional to $|G|$, the volume of the symmetry group.

2. **Improved Generalization**: Models should demonstrate robust generalization to novel object poses and configurations unseen during training, with less than 20% performance degradation on out-of-distribution test sets.

3. **Interpretable Symmetry Representations**: The discovered Lie algebra coefficients should align with physical intuition—for instance, identifying rotational symmetry around the gravitational axis in pouring tasks.

4. **Adaptive Symmetry Breaking**: The framework should learn to appropriately break symmetries when task constraints require it, such as near workspace boundaries or object capacity limits.

5. **Downstream Policy Improvements**: When integrated with model-based reinforcement learning algorithms (e.g., MBPO, Dreamer), we expect 30-50% improvements in final task performance and training stability.

### Broader Impact

**Scientific Contributions**: This work advances the theoretical understanding of symmetry in learned representations, providing algorithmic tools for automatic symmetry discovery. The framework bridges geometric deep learning with practical robotics applications, addressing a critical gap in current methodology.

**Neuroscience Implications**: Our approach offers a computational model for how biological systems might discover environmental structure through interaction. The learned symmetry representations may provide testable hypotheses about geometric encoding in motor cortex and sensory systems.

**Practical Applications**: Data-efficient world models are essential for deploying robots in diverse, unstructured environments where extensive data collection is impractical. Applications include manufacturing, healthcare robotics, and domestic assistance.

**Methodological Innovation**: The adaptive equivariant architecture and soft equivariance mechanism introduce novel techniques applicable beyond robotics to any domain with unknown or approximate symmetries.

### Limitations and Future Directions

We acknowledge several limitations. First, Lie algebra parameterization restricts discovered symmetries to continuous groups, excluding discrete symmetries. Future work should extend to mixed continuous-discrete discovery. Second, computational overhead from symmetry discovery may limit real-time applications; efficient approximations merit investigation. Finally, extending this framework to visual observations (point clouds, images) rather than privileged state information remains an important direction for practical deployment.

This research contributes to the broader vision articulated by the NeurReps workshop: understanding the deep, substrate-agnostic principles by which neural systems—biological and artificial—form useful representations of the world through geometric structure.