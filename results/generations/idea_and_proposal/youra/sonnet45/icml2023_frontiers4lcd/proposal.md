# Training-Time Lyapunov-Certified Diffusion Controllers with Probabilistic Stability Guarantees

## 1. Introduction

### Background

The intersection of machine learning and control theory has emerged as one of the most promising frontiers in modern artificial intelligence research. Safety-critical applications such as autonomous vehicles, robotic manipulation, and aerospace systems demand control policies that simultaneously achieve high performance and provide formal stability guarantees. Traditional control-theoretic approaches, while offering rigorous safety certificates through Lyapunov stability theory, often struggle with high-dimensional state spaces and complex nonlinear dynamics. Conversely, modern deep learning methods excel at learning flexible, high-performance policies but lack the theoretical guarantees essential for deployment in safety-critical domains.

Recent advances in diffusion models have demonstrated remarkable success in generating high-quality samples across various domains, from image synthesis to trajectory planning. Diffusion-based controllers, which frame control as a conditional generation problem, have shown particular promise due to their ability to capture multimodal action distributions and handle long-horizon planning. However, a critical gap remains: existing diffusion-based control methods either lack formal stability guarantees entirely or impose them at inference time through computationally expensive guidance mechanisms.

The state-of-the-art S²Diff method (Cheng et al., 2025) represents a significant step forward by incorporating Lyapunov guidance during the sampling process. However, this approach achieves only approximately 80% stability satisfaction and requires expensive gradient computations at every denoising step, resulting in 2-3x slower sampling compared to unconstrained diffusion. This computational overhead fundamentally limits the applicability of such methods to real-time control scenarios where decisions must be made at frequencies of 10-30 Hz or higher.

Control Lyapunov Function (CLF) theory, pioneered by Lyapunov (1892) and extended to stochastic systems by Kushner (1967), provides a principled framework for certifying stability. A Lyapunov function $V(x)$ serves as an "energy-like" certificate: if $\dot{V}(x) < -\alpha V(x)$ for some $\alpha > 0$ along system trajectories, the system is guaranteed to converge to equilibrium. The challenge lies in discovering valid Lyapunov functions for complex, high-dimensional systems and integrating them seamlessly with modern learning-based control architectures.

### Research Objectives

This research proposes **Training-time Lyapunov-Certified Diffusion Controllers with Probabilistic Stability Guarantees (TLCD-PSG)**, a novel framework that fundamentally shifts when and how stability constraints are enforced. Our primary objectives are:

1. **Theoretical Objective**: Develop a unified mathematical framework connecting diffusion score matching with Control Lyapunov Function theory, establishing probabilistic stability guarantees for training-time Lyapunov integration.

2. **Methodological Objective**: Design and validate a dual-network architecture that jointly learns control policies (via a Score Network) and stability certificates (via a Lyapunov Network) through a carefully designed curriculum learning strategy.

3. **Empirical Objective**: Demonstrate that TLCD-PSG achieves ≥95% Lyapunov satisfaction on test trajectories while maintaining task performance within 10% of unconstrained diffusion policies and achieving 2-3x faster sampling than inference-time guidance methods.

4. **Practical Objective**: Provide an open-source implementation suitable for deployment in real-world safety-critical control applications, with computational requirements compatible with real-time operation.

### Research Significance

This research addresses Gap 1 identified in the Frontiers in Learning, Control, and Dynamical Systems workshop: the need for theoretical foundations enabling diffusion-based control with formal guarantees. The significance of this work spans multiple dimensions:

**Theoretical Contributions**: We establish the first rigorous connection between score-based diffusion models and Lyapunov stability theory, proving that training-time integration of Lyapunov constraints produces controllers satisfying probabilistic stability guarantees of the form $P(\dot{V} < -\alpha V) \geq 1-\delta$. This bridges two previously disparate theoretical frameworks and opens new avenues for certified learning-based control.

**Methodological Innovation**: The proposed dual-network architecture with curriculum learning represents a paradigm shift from inference-time to training-time constraint enforcement. By "baking" stability into the learned score function itself, we eliminate the computational overhead that has plagued previous approaches while achieving stronger guarantees. The three-phase curriculum learning strategy prevents mode collapse while ensuring convergence to stable solutions.

**Practical Impact**: Achieving 2-3x sampling speedup while improving stability satisfaction from ~80% to ≥95% enables deployment in real-time safety-critical applications previously inaccessible to diffusion-based methods. The formal Lyapunov certificates provide a pathway toward regulatory certification in domains such as autonomous driving and medical robotics.

**Interdisciplinary Bridge**: This work exemplifies the synergy between machine learning and control theory, demonstrating how classical stability theory can enhance modern generative models while deep learning enables scalable discovery of Lyapunov functions for complex systems.

## 2. Methodology

### Overall Framework

The TLCD-PSG framework consists of three main components: (1) a dual-network architecture combining score-based diffusion with Lyapunov certification, (2) a joint training objective with curriculum learning, and (3) efficient computational strategies for Lyapunov verification. We detail each component below.

### 2.1 Dual-Network Architecture

**Score Network ($s_\theta$)**: We employ a U-Net architecture with 4 layers to parameterize the score function $s_\theta(x, t)$, where $x \in \mathbb{R}^n$ represents the system state and $t \in [0, T]$ is the diffusion time. The score network learns to approximate the gradient of the log-density: $s_\theta(x, t) \approx \nabla_x \log p_t(x)$. The control action is extracted via:

$$u_\theta(x) = -\sigma^2 s_\theta(x, t=0)$$

where $\sigma^2$ is the diffusion coefficient. This formulation connects the score function to the optimal control through the reverse-time stochastic differential equation:

$$dx = f(x, u_\theta(x))dt + \sigma dW_t$$

**Lyapunov Network ($V_\phi$)**: We parameterize the Lyapunov function using a 3-layer multilayer perceptron (MLP) with a quadratic output layer to ensure positive definiteness:

$$V_\phi(x) = \|h_\phi(x)\|^2$$

where $h_\phi: \mathbb{R}^n \to \mathbb{R}^m$ is the learned feature mapping. This architecture guarantees $V_\phi(x) \geq 0$ and $V_\phi(0) = 0$ by construction. The Lyapunov decrease condition is verified through:

$$\dot{V}_\phi(x) = \nabla V_\phi(x)^T f(x, u_\theta(x))$$

### 2.2 Joint Training Objective

The total loss function combines score matching with Lyapunov constraints:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{diffusion}}(\theta) + \lambda(t) \cdot \mathcal{L}_{\text{Lyap}}(\theta, \phi)$$

**Diffusion Loss**: We employ denoising score matching:

$$\mathcal{L}_{\text{diffusion}}(\theta) = \mathbb{E}_{t, x_0, \epsilon}\left[\left\|s_\theta(x_t, t) - \nabla_{x_t} \log p_{0t}(x_t|x_0)\right\|^2\right]$$

where $x_t = x_0 + \sigma_t \epsilon$ with $\epsilon \sim \mathcal{N}(0, I)$ and $\sigma_t$ is the noise schedule.

**Lyapunov Loss**: We enforce probabilistic Lyapunov decrease through:

$$\mathcal{L}_{\text{Lyap}}(\theta, \phi) = \mathbb{E}_{x \sim \rho}\left[\max\left(0, \dot{V}_\phi(x) + \alpha V_\phi(x)\right)^2\right]$$

where $\rho$ is the state distribution induced by the current policy, and $\alpha > 0$ is the stability margin. The max operator creates a soft constraint that penalizes violations while allowing flexibility in stable regions.

**Curriculum Learning Schedule**: The weight $\lambda(t)$ follows a three-phase schedule over training epochs $e \in [0, E]$:

$$\lambda(e) = \begin{cases}
0 & e \in [0, 0.2E] \text{ (Phase 1: Score learning)} \\
\lambda_{\max} \cdot \frac{e - 0.2E}{0.5E} & e \in [0.2E, 0.7E] \text{ (Phase 2: Gradual integration)} \\
\lambda_{\max} & e \in [0.7E, E] \text{ (Phase 3: Joint optimization)}
\end{cases}$$

This schedule prevents mode collapse by first allowing the score network to learn a flexible distribution (Phase 1), then gradually introducing stability constraints (Phase 2), and finally jointly optimizing both objectives (Phase 3).

### 2.3 Efficient Lyapunov Verification

Computing $\dot{V}_\phi(x)$ requires evaluating $\nabla V_\phi(x)^T f(x, u_\theta(x))$, which involves Jacobian computations that can be expensive. We employ three strategies for computational efficiency:

**Sample-Based Estimation**: Instead of computing exact expectations, we approximate:

$$\mathcal{L}_{\text{Lyap}} \approx \frac{1}{N_{\text{Lyap}}} \sum_{i=1}^{N_{\text{Lyap}}} \max\left(0, \dot{V}_\phi(x_i) + \alpha V_\phi(x_i)\right)^2$$

where $\{x_i\}_{i=1}^{N_{\text{Lyap}}}$ are sampled from rollouts of the current policy. We use $N_{\text{Lyap}} \in [100, 1000]$ samples per batch.

**Jacobian-Free Computation**: We compute $\nabla V_\phi(x)$ via automatic differentiation but approximate $f(x, u_\theta(x))$ using finite differences when the dynamics model is available:

$$f(x, u) \approx \frac{x_{t+\Delta t} - x_t}{\Delta t}$$

**Amortized Training Cost**: While training incurs approximately 30% computational overhead, this cost is amortized over deployment where sampling is 2-3x faster than inference-time guidance methods.

### 2.4 Data Collection

We collect training data through a bootstrapping procedure:

1. **Initial Data Collection**: Generate $D_0 = \{(x_i, u_i, x_i')\}_{i=1}^{N_0}$ using a baseline controller (e.g., SAC, MPC) where $x_i' = x_{i+1}$ is the next state.

2. **Iterative Refinement**: After each training phase, collect additional data $D_k$ using the current policy $u_\theta$ and aggregate: $D = D_0 \cup D_1 \cup \cdots \cup D_K$.

3. **Diversity Maintenance**: Ensure state space coverage by adding exploration noise: $u_{\text{explore}} = u_\theta(x) + \epsilon_u$ where $\epsilon_u \sim \mathcal{N}(0, \sigma_u^2 I)$ with decaying $\sigma_u$.

### 2.5 Experimental Design

**Benchmarks**: We evaluate on three benchmark suites:
- **MuJoCo**: HalfCheetah, Ant, Walker2d, Hopper (continuous control, varying dimensionality)
- **DeepMind Control Suite**: Cartpole, Reacher, Cheetah (physics-based tasks)
- **Safety Gym**: Point, Car, Doggo (explicit safety constraints)

**Baselines**: We compare against six methods:
1. **S²Diff**: Inference-time Lyapunov guidance (primary comparison)
2. **Direct CLF**: Policy learning with Lyapunov constraints (Ames et al., 2014)
3. **Contractive Diffusion**: Alternative stability framework (Abyaneh et al., 2026)
4. **MPC**: Model Predictive Control with online optimization
5. **Unconstrained Diffusion**: Upper bound on task performance
6. **SAC**: Soft Actor-Critic (standard RL baseline)

**Evaluation Metrics**:

1. **Lyapunov Satisfaction Rate (LSR)**:
$$\text{LSR} = \frac{1}{N_{\text{test}}} \sum_{j=1}^{N_{\text{test}}} \mathbb{1}\left[\mathbb{E}_{\tau_j}[\dot{V}(x)] < -\alpha \mathbb{E}_{\tau_j}[V(x)]\right]$$
where $\tau_j$ are test trajectories and $N_{\text{test}} = 1000$. **Target**: LSR ≥ 95%.

2. **Task Performance (Normalized Reward)**:
$$R_{\text{norm}} = \frac{R_{\text{method}} - R_{\text{random}}}{R_{\text{unconstrained}} - R_{\text{random}}}$$
**Target**: $R_{\text{norm}} \geq 0.9$ (within 10% of unconstrained).

3. **Sampling Efficiency (Speedup Factor)**:
$$\text{Speedup} = \frac{T_{\text{S²Diff}}}{T_{\text{TLCD}}}$$
where $T$ is wall-clock time to generate one action. **Target**: Speedup ≥ 2.0.

4. **Training Overhead**:
$$\eta = \frac{T_{\text{train}}^{\text{TLCD}} - T_{\text{train}}^{\text{unconstrained}}}{T_{\text{train}}^{\text{unconstrained}}}$$
**Target**: $\eta \leq 0.3$ (30% overhead).

**Statistical Testing**: We conduct 10 independent runs per method per task with different random seeds. Statistical significance is assessed using:
- **Welch's t-test** for pairwise comparisons (LSR, reward)
- **Wilcoxon signed-rank test** for non-parametric validation
- **Bonferroni correction** for multiple comparisons ($\alpha = 0.05/n_{\text{comparisons}}$)

**Ablation Studies**:
1. **Curriculum necessity**: Compare 3-phase vs. no curriculum ($\lambda = \lambda_{\max}$ from start) vs. reverse curriculum
2. **Lyapunov network architecture**: MLP vs. Input Convex Neural Network (ICNN)
3. **Sample size sensitivity**: $N_{\text{Lyap}} \in \{50, 100, 500, 1000\}$
4. **Stability margin**: $\alpha \in \{0.01, 0.05, 0.1\}$

**Hyperparameter Selection**: We use grid search with cross-validation for:
- $\lambda_{\max} \in \{0.1, 0.5, 1.0, 2.0\}$
- Learning rates: $\eta_\theta, \eta_\phi \in \{10^{-4}, 10^{-3}, 10^{-2}\}$
- Network sizes: Score Network channels $\in \{64, 128, 256\}$, Lyapunov hidden dims $\in \{128, 256, 512\}$

### 2.6 Implementation Details

**Software Stack**:
- **Framework**: PyTorch 2.0+ with CUDA 11.8
- **Base Library**: GenerativeRL (opendilab) extended with Lyapunov modules
- **Simulators**: MuJoCo 2.3, dm_control, Safety Gym
- **Compute**: 4x NVIDIA A100 GPUs (40GB), estimated 200 GPU-hours per full experiment

**Training Protocol**:
- Batch size: 256
- Total epochs: $E = 1000$
- Optimizer: AdamW with $\beta_1 = 0.9, \beta_2 = 0.999$
- Gradient clipping: max norm = 1.0
- Checkpoint frequency: every 50 epochs
- Early stopping: if LSR > 98% and reward plateau for 100 epochs

**Reproducibility**: All code, hyperparameters, and random seeds will be released open-source under MIT license.

## 3. Expected Outcomes & Impact

### Primary Expected Outcomes

**Quantitative Results**: Based on our theoretical analysis and preliminary experiments, we expect:

1. **Stability Guarantees**: TLCD-PSG will achieve LSR ≥ 95% across all benchmark tasks, representing a 15-20% improvement over S²Diff's ~80% satisfaction rate. This improvement stems from training-time integration creating inherently stable score functions rather than post-hoc guidance.

2. **Task Performance**: Normalized rewards $R_{\text{norm}} \geq 0.9$ on MuJoCo and DMC tasks, demonstrating that stability constraints impose minimal performance penalty when properly integrated during training. We anticipate slightly lower performance (5-10% reduction) on highly dynamic tasks like HalfCheetah where aggressive actions are optimal.

3. **Computational Efficiency**: 
   - **Sampling speedup**: 2.5-3.0x faster than S²Diff due to single-pass generation without guidance
   - **Training overhead**: 25-30% increase in training time, acceptable for deployment scenarios
   - **Real-time capability**: Action generation at 20-30 Hz on standard hardware, enabling practical robotics applications

4. **Ablation Insights**:
   - Curriculum learning will improve LSR by ≥10% and diversity metrics by ≥20% compared to no curriculum
   - ICNN architecture for Lyapunov network will show 5-8% better generalization than standard MLP
   - Optimal $N_{\text{Lyap}} \approx 500$ balancing accuracy and computational cost

### Theoretical Contributions

**Theorem 1 (Probabilistic Stability Guarantee)**: Under mild regularity conditions on the dynamics $f$ and assuming the Lyapunov network $V_\phi$ achieves training loss $\mathcal{L}_{\text{Lyap}} < \epsilon$, the learned controller $u_\theta$ satisfies:

$$P\left(\dot{V}_\phi(x) < -\alpha V_\phi(x)\right) \geq 1 - \delta$$

where $\delta = O(\epsilon/\alpha)$. This provides a formal connection between training loss and deployment safety.

**Theorem 2 (Convergence of Joint Training)**: The joint optimization of $\mathcal{L}_{\text{total}}$ with curriculum learning converges to a stationary point $(\theta^*, \phi^*)$ satisfying both score matching accuracy and Lyapunov constraints, with convergence rate $O(1/\sqrt{T})$ under standard assumptions.

These theoretical results will be rigorously proven in the full paper, establishing TLCD-PSG on firm mathematical foundations.

### Methodological Innovations

1. **Dual-Network Co-Training**: The first architecture jointly optimizing generative modeling (score network) and stability certification (Lyapunov network), creating a template for integrating formal guarantees into other generative models.

2. **Probabilistic Lyapunov Loss**: A differentiable, sample-based formulation compatible with stochastic gradient descent, enabling scalable training unlike previous exact verification methods.

3. **Curriculum Learning for Multi-Objective Control**: A principled three-phase schedule preventing mode collapse while ensuring constraint satisfaction, applicable beyond diffusion models to other multi-objective learning problems.

### Practical Impact

**Safety-Critical Deployment**: By achieving ≥95% stability satisfaction with formal Lyapunov certificates, TLCD-PSG enables deployment in applications where current learning-based methods are prohibited:
- **Autonomous vehicles**: Lane-keeping and collision avoidance with provable stability
- **Robotic manipulation**: Contact-rich tasks with guaranteed force limits
- **Aerospace**: Attitude control with certified convergence properties
- **Medical robotics**: Surgical assistance with safety bounds

**Real-Time Control**: The 2-3x sampling speedup enables control frequencies of 20-30 Hz, bridging the gap between offline planning and online reactive control. This opens applications in dynamic environments requiring rapid decision-making.

**Regulatory Certification**: Lyapunov certificates provide interpretable safety guarantees compatible with regulatory frameworks (e.g., ISO 26262 for automotive, DO-178C for aerospace), offering a pathway toward certified AI systems.

**Open-Source Ecosystem**: Our implementation will extend the GenerativeRL library, providing the community with:
- Modular Lyapunov network components
- Curriculum learning schedulers
- Benchmark evaluation scripts
- Pre-trained models for common tasks

### Broader Impact on Research Community

**Bridging Communities**: This work exemplifies productive synergy between machine learning and control theory, encouraging further interdisciplinary collaboration. We expect it to inspire:
- Integration of other formal methods (reachability analysis, barrier functions) into generative models
- Application of diffusion models to additional control domains (hybrid systems, multi-agent coordination)
- Theoretical analysis of other generative models (GANs, VAEs) through control-theoretic lenses

**New Research Directions**:
1. **Adaptive Lyapunov Functions**: Learning time-varying or state-dependent stability margins
2. **Multi-Objective Certificates**: Combining Lyapunov stability with reachability and safety constraints
3. **Distributed Diffusion Control**: Extending to multi-agent systems with coupled dynamics
4. **Robustness Guarantees**: Incorporating adversarial perturbations and model uncertainty

### Limitations and Future Work

**Known Limitations**:
- **Probabilistic guarantees**: 95% satisfaction may be insufficient for zero-failure-tolerance applications (e.g., nuclear systems)
- **Region of attraction**: Validity limited to training distribution; out-of-distribution states may violate stability
- **Continuous control only**: Current formulation does not extend to discrete action spaces
- **Computational overhead**: 30% training increase may be prohibitive for extremely large-scale systems

**Future Extensions**:
1. **PAC-Bayes bounds**: Deriving distribution-dependent generalization guarantees
2. **Online adaptation**: Updating Lyapunov functions during deployment for non-stationary environments
3. **Hybrid systems**: Extending to switched dynamics and contact-rich scenarios
4. **Discrete actions**: Developing alternative certificate functions for combinatorial control

### Timeline and Milestones

**Month 1-2**: Implementation of dual-network architecture and training infrastructure
**Month 3-4**: Baseline experiments on MuJoCo tasks, hyperparameter tuning
**Month 5**: Ablation studies and comparison with S²Diff, CLF methods
**Month 6**: DMC and Safety Gym evaluation, theoretical analysis, paper writing

**Success Criteria**: The project will be considered successful if we achieve at least 3 of 4 primary targets (LSR ≥ 95%, $R_{\text{norm}} \geq 0.9$, Speedup ≥ 2.0, $\eta \leq 0.3$) on at least 6 of 8 benchmark tasks.

---

This research proposal presents a comprehensive plan to develop training-time Lyapunov-certified diffusion controllers, addressing a critical gap in safe learning-based control. By combining rigorous theory, principled methodology, and extensive empirical validation, we aim to enable deployment of diffusion-based controllers in safety-critical applications while advancing the theoretical foundations connecting generative modeling and control theory.