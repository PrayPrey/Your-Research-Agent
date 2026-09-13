# Research Proposal: Training-Time Control Barrier Function Integration for Inherently Safe Diffusion Policies in Contact-Rich Manipulation

## 1. Introduction

### 1.1 Background

The pursuit of robots with human-level abilities represents one of the most ambitious challenges in artificial intelligence and robotics. While recent advances have demonstrated remarkable capabilities in specific domains—from drone racing to table tennis—achieving robust, safe performance in unstructured environments like household assistance remains elusive. Contact-rich manipulation tasks, such as cooking or tidying up, require robots to interact physically with diverse objects while maintaining safety constraints that humans navigate intuitively.

Diffusion models have emerged as a powerful paradigm for robot policy learning, offering expressive action distributions that capture the multimodality inherent in manipulation tasks. The Diffusion Policy framework introduced by Chi et al. (2023) demonstrated state-of-the-art performance on contact-rich manipulation benchmarks by modeling action sequences as denoising diffusion processes. However, these policies lack inherent safety guarantees—a critical limitation for real-world deployment where robots must operate alongside humans and fragile objects.

Control Barrier Functions (CBFs) provide a principled mathematical framework for ensuring safety in dynamical systems. A CBF $h: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}$ defines a safe set $\mathcal{C} = \{(s,a) : h(s,a) \geq 0\}$, and actions satisfying the CBF constraint guarantee forward invariance of this safe set. Recent work, notably CoBL-Diffusion (2024), has integrated CBF constraints into diffusion policies by filtering unsafe actions during the inference-time denoising process. While effective, this approach incurs significant computational overhead (30-50% latency increase) and fundamentally treats safety as a post-hoc correction rather than an intrinsic policy property.

### 1.2 Research Gap and Motivation

A fundamental gap exists in current safe robot learning: existing methods apply safety constraints at inference time, filtering unsafe actions after they are generated. This paradigm has three critical limitations:

1. **Computational Overhead**: Inference-time safety filtering requires additional forward passes through the CBF network at each denoising step, creating latency that limits real-time deployment.

2. **Distribution Mismatch**: The policy learns to generate actions without awareness of safety constraints, leading to frequent corrections and suboptimal behavior near constraint boundaries.

3. **Reactive Rather Than Proactive Safety**: Post-hoc filtering cannot shape the underlying action distribution to inherently avoid unsafe regions—it can only reject unsafe samples after generation.

For contact-rich manipulation requiring human-level dexterity, robots need policies that are *inherently* safe—avoiding unsafe regions by design rather than correction. This motivates our central research question: **Can we embed safety directly into diffusion policy learning to eliminate the inference-time safety overhead while achieving superior safety-performance trade-offs?**

### 1.3 Research Objectives

This research proposes a novel framework for integrating Control Barrier Function constraints during diffusion policy training via Lagrangian relaxation. Our specific objectives are:

1. **Develop a training-time CBF integration mechanism** that shapes the diffusion policy's action distribution to inherently avoid unsafe regions.

2. **Design a stable optimization procedure** using learned Lagrangian multipliers and phased training to balance task performance and safety objectives.

3. **Demonstrate superior safety-performance trade-offs** compared to inference-time methods on contact-rich manipulation benchmarks.

4. **Achieve real-time deployment capability** by eliminating inference-time safety overhead.

### 1.4 Significance

This research addresses a critical barrier to deploying robots in human environments. By embedding safety into the learning process itself, we enable:

- **Real-time safe manipulation**: Zero inference overhead enables deployment on resource-constrained robotic platforms.
- **Inherently safe policies**: Action distributions that naturally avoid unsafe regions, reducing reliance on reactive safety systems.
- **Scalable safety integration**: A general framework applicable to diverse manipulation tasks with learnable safety constraints.

The proposed approach bridges the gap between the expressiveness of diffusion policies and the formal safety guarantees of control-theoretic methods, contributing to the broader goal of robots with human-level abilities operating safely in unstructured environments.

## 2. Methodology

### 2.1 Problem Formulation

We consider contact-rich manipulation tasks formulated as a constrained Markov Decision Process (CMDP) $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, r, c, \gamma)$, where $\mathcal{S}$ is the state space, $\mathcal{A}$ is the continuous action space, $P$ is the transition dynamics, $r$ is the task reward, $c$ is the safety cost function, and $\gamma$ is the discount factor.

A Control Barrier Function $h: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}$ defines the safe set:

$$\mathcal{C} = \{(s, a) \in \mathcal{S} \times \mathcal{A} : h(s, a) \geq 0\}$$

Our goal is to learn a diffusion policy $\pi_\theta$ that maximizes task success while ensuring actions remain within the safe set $\mathcal{C}$.

### 2.2 Diffusion Policy Background

A diffusion policy models the action distribution $p_\theta(a|s)$ through an iterative denoising process. Starting from Gaussian noise $a^K \sim \mathcal{N}(0, I)$, the policy iteratively refines actions through $K$ denoising steps:

$$a^{k-1} = \frac{1}{\sqrt{\alpha_k}}\left(a^k - \frac{1-\alpha_k}{\sqrt{1-\bar{\alpha}_k}}\epsilon_\theta(a^k, s, k)\right) + \sigma_k z$$

where $\epsilon_\theta$ is the learned noise prediction network, $\alpha_k$ are the noise schedule parameters, and $z \sim \mathcal{N}(0, I)$.

The standard training objective minimizes the denoising score matching loss:

$$\mathcal{L}_{\text{task}} = \mathbb{E}_{a^0 \sim \mathcal{D}, k, \epsilon}\left[\|\epsilon - \epsilon_\theta(a^k, s, k)\|^2\right]$$

where $\mathcal{D}$ is the demonstration dataset and $a^k$ is the noised action at step $k$.

### 2.3 Training-Time CBF Integration

#### 2.3.1 Neural CBF Architecture

We parameterize the CBF as a neural network $h_\phi: \mathcal{S} \times \mathcal{A} \rightarrow \mathbb{R}$ with a 3-layer MLP architecture:

$$h_\phi(s, a) = W_3 \cdot \text{ReLU}(W_2 \cdot \text{ReLU}(W_1 \cdot [s; a] + b_1) + b_2) + b_3$$

The CBF is pre-trained on demonstration data with collision labels using a margin-based loss:

$$\mathcal{L}_{\text{CBF}} = \mathbb{E}_{(s,a,y) \sim \mathcal{D}_{\text{safety}}}\left[\max(0, \delta - y \cdot h_\phi(s, a))\right]$$

where $y \in \{-1, +1\}$ indicates unsafe/safe labels and $\delta > 0$ is the margin.

#### 2.3.2 CBF-Conditioned Training Loss

We introduce a safety loss that penalizes actions violating the CBF constraint:

$$\mathcal{L}_{\text{safety}} = \mathbb{E}_{a^0 \sim p_\theta(\cdot|s), s \sim \mathcal{D}}\left[\max(0, -h_\phi(s, a^0))\right]$$

This loss provides gradient signal only when actions enter unsafe regions, guiding the policy to shape its distribution away from constraint boundaries.

#### 2.3.3 Lagrangian Relaxation

We formulate the constrained optimization problem using Lagrangian relaxation:

$$\min_\theta \max_{\lambda \geq 0} \mathcal{L}(\theta, \lambda) = \mathcal{L}_{\text{task}}(\theta) + \lambda \cdot \mathcal{L}_{\text{safety}}(\theta)$$

The Lagrangian multiplier $\lambda$ is learned via dual gradient ascent:

$$\lambda_{t+1} = \max\left(0, \lambda_t + \alpha_\lambda \cdot \mathcal{L}_{\text{safety}}(\theta_t)\right)$$

where $\alpha_\lambda$ is the dual learning rate. This mechanism dynamically balances task and safety objectives: when safety violations are high, $\lambda$ increases to prioritize safety; when violations are low, $\lambda$ decreases to focus on task performance.

#### 2.3.4 Phased Training Procedure

To ensure stable learning dynamics, we employ a two-phase training procedure:

**Phase 1: Frozen CBF Training** (70% of training)
- Fix the pre-trained CBF parameters $\phi$
- Train only the diffusion policy $\theta$ with the combined loss
- Initialize $\lambda_0 = 1.0$

**Phase 2: Joint Fine-Tuning** (30% of training)
- Unfreeze CBF parameters $\phi$
- Jointly optimize $\theta$ and $\phi$ with reduced learning rate for $\phi$
- Continue Lagrangian multiplier updates

The complete training algorithm is presented in Algorithm 1.

---

**Algorithm 1: Training-Time CBF Integration for Diffusion Policies**

**Input:** Demonstration dataset $\mathcal{D}$, safety-labeled dataset $\mathcal{D}_{\text{safety}}$, pre-trained CBF $h_\phi$

**Hyperparameters:** Learning rates $\alpha_\theta$, $\alpha_\lambda$, $\alpha_\phi$; phase transition ratio $\rho = 0.7$; total iterations $T$

1. Initialize diffusion policy $\epsilon_\theta$, Lagrangian multiplier $\lambda \leftarrow 1.0$
2. **for** $t = 1$ to $T$ **do**
3. $\quad$ Sample batch $(s, a^0) \sim \mathcal{D}$, noise level $k \sim \text{Uniform}(1, K)$
4. $\quad$ Compute noised actions: $a^k = \sqrt{\bar{\alpha}_k} a^0 + \sqrt{1-\bar{\alpha}_k} \epsilon$
5. $\quad$ Compute task loss: $\mathcal{L}_{\text{task}} = \|\epsilon - \epsilon_\theta(a^k, s, k)\|^2$
6. $\quad$ Generate denoised actions: $\hat{a}^0 \sim p_\theta(\cdot|s)$
7. $\quad$ Compute safety loss: $\mathcal{L}_{\text{safety}} = \max(0, -h_\phi(s, \hat{a}^0))$
8. $\quad$ Compute total loss: $\mathcal{L} = \mathcal{L}_{\text{task}} + \lambda \cdot \mathcal{L}_{\text{safety}}$
9. $\quad$ Update policy: $\theta \leftarrow \theta - \alpha_\theta \nabla_\theta \mathcal{L}$
10. $\quad$ Update multiplier: $\lambda \leftarrow \max(0, \lambda + \alpha_\lambda \cdot \mathcal{L}_{\text{safety}})$
11. $\quad$ **if** $t > \rho T$ **then** // Phase 2: Joint fine-tuning
12. $\quad\quad$ Update CBF: $\phi \leftarrow \phi - \alpha_\phi \nabla_\phi \mathcal{L}_{\text{CBF}}$
13. $\quad$ **end if**
14. **end for**

**Output:** Trained diffusion policy $\epsilon_\theta$

---

### 2.4 Experimental Design

#### 2.4.1 Benchmark and Tasks

We evaluate on the CALVIN benchmark, a comprehensive simulation environment for contact-rich manipulation with a Franka Panda robot arm. CALVIN provides:
- 34 distinct manipulation tasks (e.g., opening drawers, stacking blocks, rotating objects)
- Long-horizon task sequences requiring chained skills
- Realistic contact dynamics and visual observations

We define safety constraints based on:
- **Collision avoidance**: Preventing end-effector collisions with obstacles
- **Force limits**: Constraining contact forces below damage thresholds
- **Workspace boundaries**: Keeping the robot within safe operational limits

Safety labels are automatically generated using the simulator's collision detection and force sensing.

#### 2.4.2 Baselines

We compare against three baselines:

1. **Vanilla Diffusion Policy**: Standard diffusion policy without safety constraints (Chi et al., 2023)

2. **CoBL-Diffusion**: State-of-the-art inference-time CBF integration that modifies the denoising process to satisfy CBF constraints

3. **SRL-VIC**: Safe reinforcement learning with variable impedance control, representing post-hoc safety filtering approaches

#### 2.4.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Safety Violation Rate | Percentage of timesteps where $h(s,a) < 0$ | $< 2\%$ |
| Task Success Rate | Percentage of episodes achieving goal state | $\geq 82\%$ |
| Inference Latency | Wall-clock time per action (ms) | No increase vs. vanilla |
| Distribution Shift | KL divergence from vanilla policy in unsafe regions | Measurable decrease |

#### 2.4.4 Statistical Analysis

- **Sample Size**: $n = 100$ rollouts per condition (exceeding minimum $n = 25$ for Cohen's $d = 0.8$, power $= 0.8$)
- **Primary Test**: Two-sample t-test for safety violation rate comparison ($\alpha = 0.05$, one-tailed)
- **Secondary Tests**: Paired t-test for task success, Welch's t-test for latency comparison
- **Effect Size**: Report Cohen's $d$ for all comparisons

#### 2.4.5 Ablation Studies

To validate the causal mechanism, we conduct ablations:

1. **CBF Loss Only**: Remove Lagrangian balancing (fixed $\lambda = 1.0$)
2. **No Phased Training**: Joint training from initialization
3. **Inference-Time Hybrid**: Apply our trained policy with additional inference-time CBF filtering

#### 2.4.6 Distribution Analysis

To verify that training-time integration genuinely shapes the action distribution, we:
1. Sample 10,000 actions from each policy conditioned on states near constraint boundaries
2. Compute empirical density in safe vs. unsafe regions
3. Calculate KL divergence: $D_{KL}(p_{\text{ours}} \| p_{\text{vanilla}})$ restricted to unsafe regions

### 2.5 Implementation Details

- **Diffusion Architecture**: DDPM scheduler with $K = 100$ denoising steps, U-Net noise predictor
- **CBF Architecture**: 3-layer MLP (256-256-1) with ReLU activations
- **Training**: AdamW optimizer, $\alpha_\theta = 1 \times 10^{-4}$, $\alpha_\lambda = 1 \times 10^{-3}$, $\alpha_\phi = 1 \times 10^{-5}$
- **Compute**: Estimated 56 GPU hours (NVIDIA A100) total

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate the following outcomes:

**Primary Outcome (P1 - Safety Improvement)**:
Our training-time CBF integration will achieve safety violation rates below 2%, representing a 60-80% reduction compared to CoBL-Diffusion (5-10%) and an 85-90% reduction compared to vanilla diffusion policy (15-20%). This improvement stems from the fundamental difference between shaping the action distribution during training versus filtering at inference time.

**Secondary Outcome (P2 - Inference Efficiency)**:
The trained policy will achieve equivalent inference latency to vanilla diffusion policy (approximately 15-25ms per action), eliminating the 30-50% overhead incurred by inference-time CBF methods. This enables real-time deployment on standard robotic hardware without specialized acceleration.

**Secondary Outcome (P3 - Task Performance)**:
Task success rates will remain at or above 82%, demonstrating that safety integration does not significantly compromise manipulation capability. The Lagrangian balancing mechanism ensures the policy does not collapse to overly conservative behavior.

**Mechanistic Validation**:
Ablation studies will confirm that each component contributes to the overall performance:
- Removing Lagrangian balancing will increase safety violations by 50-100%
- Removing phased training will destabilize learning, reducing both safety and task success
- Distribution analysis will show measurably lower action density in unsafe regions

### 3.2 Falsification Criteria

The hypothesis will be rejected if any of the following conditions are observed:
1. Safety violation rate exceeds 15% (worse than post-hoc filtering)
2. Task success rate falls below 75% (significant performance degradation)
3. No measurable distribution shift in unsafe regions (mechanism not functioning)
4. CoBL-Diffusion achieves equivalent or better safety-performance trade-off

### 3.3 Scientific Impact

This research contributes to multiple areas:

**Safe Robot Learning**: We introduce a paradigm shift from reactive (inference-time) to proactive (training-time) safety integration. This principle extends beyond diffusion policies to other generative models for robot control.

**Constrained Policy Optimization**: The Lagrangian relaxation framework with phased training provides a stable approach for incorporating hard constraints into diffusion model training, applicable to constraints beyond safety (e.g., energy efficiency, smoothness).

**Real-Time Deployment**: By eliminating inference-time overhead, we enable deployment of safe manipulation policies on resource-constrained platforms, bridging the gap between research demonstrations and practical applications.

### 3.4 Practical Impact

**Household Robotics**: Safe manipulation policies are essential for robots operating in homes alongside humans and fragile objects. Our approach enables robots to perform tasks like cooking and tidying with inherent safety guarantees.

**Industrial Automation**: Contact-rich assembly tasks require precise force control within safety limits. Training-time safety integration ensures consistent safe behavior without computational overhead that could disrupt real-time control loops.

**Healthcare Robotics**: Assistive robots must maintain strict safety constraints when interacting with patients. Inherently safe policies reduce reliance on external safety systems and increase trust in human-robot collaboration.

### 3.5 Limitations and Future Work

**Current Limitations**:
- Requires pre-training the CBF, adding to overall training time
- Assumes safety constraints can be expressed as CBFs (may not capture all safety requirements)
- Evaluated only in simulation; real-world transfer requires additional validation

**Future Directions**:
- Extend to vision-based CBFs for safety constraints defined in image space
- Investigate curriculum learning for CBF integration to handle initially uninformative gradients
- Validate on physical robot platforms with real-world contact dynamics
- Explore multi-agent settings where safety constraints involve other robots or humans

### 3.6 Conclusion

This research proposes a fundamental advancement in safe robot learning by integrating Control Barrier Function constraints during diffusion policy training rather than at inference time. Through Lagrangian relaxation and phased training, we shape the policy's action distribution to inherently avoid unsafe regions, achieving superior safety-performance trade-offs with zero inference overhead. Success in this research will contribute significantly to the goal of deploying robots with human-level abilities in unstructured environments, where safety is not an afterthought but an intrinsic property of intelligent behavior.