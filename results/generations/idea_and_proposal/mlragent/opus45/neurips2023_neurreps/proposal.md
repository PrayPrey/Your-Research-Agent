# Equivariant World Models for Robust Robotic Manipulation via Learned Symmetry Discovery

## 1. Introduction

### Background

The intersection of geometric deep learning and neuroscience has revealed a profound computational principle: both biological and artificial neural systems benefit from encoding the geometric and topological structure of the data they process. In neuroscience, evidence from head direction cells, grid cells, and motor cortex demonstrates that neural circuits naturally mirror the geometric structure of the systems they represent. Concurrently, the field of geometric deep learning has shown that incorporating geometric priors—particularly symmetry constraints—into neural network architectures yields substantial improvements in computational efficiency, robustness, and generalization.

Robotic manipulation presents a compelling application domain for these principles. A fundamental challenge in robotics is generalization: policies trained to manipulate objects in specific configurations frequently fail when objects are rotated, translated, or presented in novel arrangements. This brittleness severely limits deployment in unstructured real-world environments where objects appear in arbitrary poses and configurations.

Equivariant neural networks offer a principled solution by encoding symmetries directly into network architectures. Recent work has demonstrated the effectiveness of SE(3)-equivariant policies for robotic manipulation, achieving improved sample efficiency and generalization to unseen object poses. However, these approaches typically assume that the relevant symmetry group is known a priori and exactly satisfied by the environment. In practice, real-world manipulation involves objects and environments with unknown, approximate, or partially broken symmetries. Gravity breaks vertical translation symmetry, friction breaks certain rotational symmetries, and object-specific properties introduce additional symmetry-breaking factors that are difficult to enumerate manually.

### Research Objectives

This research proposes a novel framework for jointly learning world models and discovering their underlying symmetry structures directly from interaction data. Our objectives are threefold:

1. **Symmetry Discovery**: Develop a differentiable module that identifies approximate Lie group structures from state-action transitions without manual specification.

2. **Equivariant World Modeling**: Design latent dynamics models that enforce discovered symmetries while maintaining flexibility to capture symmetry-breaking factors.

3. **Symmetry-Aware Control**: Implement model-predictive control schemes that leverage the learned symmetry-aware representations for robust manipulation.

### Significance

This work bridges geometric deep learning theory with practical robotic learning by removing the requirement for manual symmetry specification. The framework contributes to the NeurReps themes of learning group structure in data, equivariant world models for robotics, and the dynamics of neural representations. Success would demonstrate that geometric principles—identified as fundamental to both biological and artificial neural computation—can be discovered rather than prescribed, moving toward more autonomous and adaptive robotic systems.

## 2. Methodology

### 2.1 Problem Formulation

We consider a robotic manipulation environment as a Markov Decision Process (MDP) defined by state space $\mathcal{S}$, action space $\mathcal{A}$, transition dynamics $p(s_{t+1}|s_t, a_t)$, and reward function $r(s_t, a_t)$. We assume there exists an unknown symmetry group $G$ under which the dynamics are approximately equivariant:

$$p(g \cdot s_{t+1} | g \cdot s_t, \rho(g) \cdot a_t) \approx p(s_{t+1} | s_t, a_t), \quad \forall g \in G$$

where $g \cdot s$ denotes the group action on states and $\rho(g)$ is the representation acting on actions.

Our goal is to learn a latent world model with encoder $\phi: \mathcal{S} \rightarrow \mathcal{Z}$, dynamics model $f: \mathcal{Z} \times \mathcal{A} \rightarrow \mathcal{Z}$, and decoder $\psi: \mathcal{Z} \rightarrow \mathcal{S}$, while simultaneously discovering the symmetry group $G$.

### 2.2 Symmetry Discovery Module

We parameterize the unknown symmetry group as a Lie group through its Lie algebra. For a $d$-dimensional Lie algebra, we learn $k$ infinitesimal generators $\{V_1, \ldots, V_k\}$ represented as vector fields on the latent space $\mathcal{Z}$.

**Infinitesimal Generator Estimation**: Given a batch of transitions $\{(s_t^{(i)}, a_t^{(i)}, s_{t+1}^{(i)})\}_{i=1}^N$, we encode states into latent space: $z_t^{(i)} = \phi(s_t^{(i)})$. We parameterize each generator $V_j$ as a neural network $V_j: \mathcal{Z} \rightarrow T\mathcal{Z}$ mapping latent states to tangent vectors.

The generators must satisfy the Lie algebra closure property. We enforce this through a structure constant regularizer:

$$\mathcal{L}_{\text{structure}} = \sum_{i,j} \left\| [V_i, V_j] - \sum_k c_{ij}^k V_k \right\|^2$$

where $[V_i, V_j]$ is the Lie bracket and $c_{ij}^k$ are learnable structure constants constrained to satisfy the Jacobi identity.

**Group Action Approximation**: Given a generator $V_j$ and a scalar parameter $\epsilon$, we approximate the group action using the exponential map:

$$g_j(\epsilon) \cdot z \approx z + \epsilon V_j(z) + \frac{\epsilon^2}{2} \nabla V_j(z) \cdot V_j(z) + O(\epsilon^3)$$

For computational efficiency, we use a second-order approximation in practice.

### 2.3 Equivariant Latent Dynamics Model

The dynamics model $f_\theta: \mathcal{Z} \times \mathcal{A} \rightarrow \mathcal{Z}$ is designed to respect the discovered symmetries. We construct $f_\theta$ using equivariant layers with respect to the learned group action.

**Equivariance Constraint**: The dynamics should satisfy:

$$f_\theta(g \cdot z, \rho(g) \cdot a) = g \cdot f_\theta(z, a), \quad \forall g \in G$$

We enforce this through a differentiable symmetry regularizer applied during training:

$$\mathcal{L}_{\text{equiv}} = \mathbb{E}_{z, a, \epsilon, j} \left[ \left\| f_\theta(g_j(\epsilon) \cdot z, \rho_j(\epsilon) \cdot a) - g_j(\epsilon) \cdot f_\theta(z, a) \right\|^2 \right]$$

where $\epsilon \sim \mathcal{U}(-\epsilon_{\max}, \epsilon_{\max})$ and $j$ is sampled uniformly over discovered generators.

**Symmetry-Breaking Factors**: To capture approximate symmetries, we introduce a learned symmetry-breaking correction term:

$$f_\theta(z, a) = f_\theta^{\text{equiv}}(z, a) + \lambda \cdot f_\theta^{\text{break}}(z, a)$$

where $f_\theta^{\text{equiv}}$ is constrained to be equivariant, $f_\theta^{\text{break}}$ is unconstrained, and $\lambda$ is a learnable gating parameter that modulates the contribution of symmetry-breaking effects.

### 2.4 Complete Training Objective

The full training objective combines world model reconstruction, symmetry discovery, and equivariance enforcement:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{recon}} + \alpha \mathcal{L}_{\text{dynamics}} + \beta \mathcal{L}_{\text{equiv}} + \gamma \mathcal{L}_{\text{structure}} + \delta \mathcal{L}_{\text{sparse}}$$

where:

**Reconstruction Loss**:
$$\mathcal{L}_{\text{recon}} = \mathbb{E}_{s} \left[ \| \psi(\phi(s)) - s \|^2 \right]$$

**Dynamics Prediction Loss**:
$$\mathcal{L}_{\text{dynamics}} = \mathbb{E}_{s_t, a_t, s_{t+1}} \left[ \| \psi(f_\theta(\phi(s_t), a_t)) - s_{t+1} \|^2 \right]$$

**Sparsity Regularizer** (to discover minimal symmetry groups):
$$\mathcal{L}_{\text{sparse}} = \sum_j \| V_j \|_1$$

Hyperparameters $\alpha, \beta, \gamma, \delta$ control the relative importance of each term.

### 2.5 Model-Predictive Control with Symmetry Augmentation

For control, we employ Cross-Entropy Method (CEM) planning in the learned latent space with symmetry-based trajectory augmentation.

**Algorithm 1: Symmetry-Aware MPC**
```
Input: Current state s_t, goal state s_g, planning horizon H
1. Encode: z_t = φ(s_t), z_g = φ(s_g)
2. Initialize action sequences {a_{t:t+H}^{(i)}}_{i=1}^M from prior
3. For iteration = 1 to max_iter:
   a. For each sequence i:
      - Predict trajectory: z_{t+1:t+H}^{(i)} using f_θ
      - Sample symmetry transformation: g ~ G (using learned generators)
      - Augment: z̃^{(i)} = g · z^{(i)}, ã^{(i)} = ρ(g) · a^{(i)}
   b. Evaluate costs for original and augmented trajectories
   c. Select elite samples and update action distribution
4. Return first action of best sequence
```

The symmetry augmentation effectively expands the planning distribution, improving robustness to state estimation errors and enabling better exploration of the solution space.

### 2.6 Experimental Design

**Simulation Environments**:
1. **Object Rearrangement**: Tabletop manipulation with rigid objects of varying shapes (cubes, cylinders, T-shapes) requiring pick-and-place operations.
2. **Peg Insertion**: Precision assembly task with rotational symmetries.
3. **Cable Manipulation**: Deformable object manipulation with approximate symmetries.

**Real Robot Experiments**:
We will deploy on a Franka Emika Panda arm with RGB-D sensing. Tasks include:
- Block stacking with randomized initial poses
- Tool use (spatula, tongs) with novel objects
- Multi-object rearrangement

**Baselines**:
1. Standard world models (Dreamer-v3)
2. Hand-specified SE(3)-equivariant models (ET-SEED, EquiForm)
3. Data augmentation approaches (DrQ, RAD)
4. Symmetry-constrained models with fixed groups

**Evaluation Metrics**:
1. **Sample Efficiency**: Task success rate as a function of environment interactions
2. **Generalization**: Zero-shot transfer performance on held-out object poses (rotation angles unseen during training)
3. **Robustness**: Performance under observation noise, pose perturbations, and partial occlusions
4. **Symmetry Recovery**: Comparison of discovered generators with ground-truth symmetries (where known)
5. **Planning Efficiency**: Computational cost and success rate of MPC under varying horizons

**Ablation Studies**:
- Impact of symmetry regularization strength $\beta$
- Number of learned generators $k$
- Contribution of symmetry-breaking term
- Second-order vs. first-order generator approximation

## 3. Expected Outcomes & Impact

### Expected Results

We anticipate the following quantitative outcomes:

1. **Sample Efficiency**: 5-10× reduction in environment interactions required to achieve 90% task success rate compared to non-equivariant world models, consistent with theoretical predictions from geometric deep learning that symmetry reduces the effective dimensionality of the learning problem.

2. **Generalization**: >80% zero-shot success rate on object poses rotated up to 180° from training distribution, compared to <30% for standard approaches.

3. **Robustness**: <15% performance degradation under 10% observation noise, compared to >40% degradation for non-equivariant baselines.

4. **Symmetry Discovery Accuracy**: Recovery of ground-truth symmetry generators with <10° angular error for environments with known SE(2) or SO(3) symmetries.

### Scientific Contributions

1. **Methodological**: A novel differentiable framework for joint symmetry discovery and equivariant world model learning, removing the requirement for manual symmetry specification.

2. **Theoretical**: Analysis of conditions under which approximate symmetries can be reliably discovered from finite interaction data, connecting to statistical learning theory in geometric settings.

3. **Empirical**: Comprehensive benchmarking demonstrating the practical benefits of learned equivariance for robotic manipulation.

### Broader Impact

This work addresses a fundamental limitation in deploying geometric deep learning principles to real-world robotics. By enabling symmetry discovery rather than prescription, the framework moves toward robotic systems that can autonomously identify and exploit environmental structure—a capability that appears to be present in biological neural systems.

The convergence with neuroscience findings is particularly significant: biological motor systems appear to discover and leverage symmetries through experience rather than having them hardcoded. Our computational framework provides a testable model for how such symmetry discovery might occur, potentially informing both robotics and computational neuroscience.

If successful, this research will contribute to the broader goal identified by the NeurReps community: understanding the substrate-agnostic principles by which neural systems—biological or artificial—form useful geometric representations of the world. The framework may generalize beyond manipulation to other domains where unknown symmetries structure the environment, including navigation, multi-agent systems, and physical reasoning.