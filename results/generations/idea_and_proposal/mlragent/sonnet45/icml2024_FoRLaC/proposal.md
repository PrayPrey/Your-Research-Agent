# Adaptive Excitation Design for Sample-Efficient Learning in Nonlinear Control Systems

## 1. Title

**Adaptive Excitation Design for Sample-Efficient Learning in Nonlinear Control Systems: A Control-Theoretic Framework for Safe Reinforcement Learning**

## 2. Introduction

### Background

The intersection of reinforcement learning (RL) and control theory represents a critical frontier in addressing large-scale stochastic dynamic programming problems. While RL has demonstrated remarkable success in domains with abundant data and relaxed safety requirements, its application to high-stakes control problems—such as industrial automation, autonomous vehicles, and supply chain optimization—remains limited due to insufficient theoretical guarantees and sample inefficiency. Conversely, classical control theory provides robust stability guarantees and well-understood system identification techniques but struggles with the complexity and adaptability required for modern learning-based systems.

A fundamental tension exists in the exploration-exploitation tradeoff for nonlinear control systems. Classical system identification in control theory relies on the principle of **persistent excitation**: the notion that input signals must be sufficiently "rich" to enable accurate parameter estimation. This concept, formalized through spectral conditions on excitation signals, ensures identifiability of system parameters. However, traditional excitation approaches are typically open-loop and designed offline, limiting their adaptability to online learning scenarios where system dynamics may be partially unknown or time-varying.

In contrast, RL approaches exploration through various strategies—from ε-greedy policies to intrinsic motivation and posterior sampling—that rarely incorporate control-theoretic insights about system structure. This disconnect leads to two critical problems: (1) sample inefficiency due to uninformed exploration that fails to exploit known structural properties of control systems, and (2) potential safety violations during learning, as exploration strategies may drive the system into unsafe or unstable regions.

Recent work has begun addressing safety in RL through Control Barrier Functions (CBFs) and Lyapunov-based methods, as evidenced by Luo et al. (2022) and Cohen & Belta (2021). However, these approaches primarily focus on constraint satisfaction rather than optimizing the information acquisition process itself. Furthermore, existing sample complexity bounds for nonlinear control learning either assume restrictive linearity conditions or provide loose guarantees that scale poorly with system complexity.

### Research Objectives

This research proposes a unified framework that bridges control-theoretic excitation design with adaptive RL exploration, specifically targeting nonlinear control systems. Our primary objectives are:

1. **Develop an adaptive excitation design methodology** that synthesizes exploration policies by maximizing information acquisition (measured through Fisher information geometry) while respecting safety constraints encoded through Control Lyapunov Functions (CLFs) and Control Barrier Functions (CBFs).

2. **Establish a hierarchical learning architecture** that decomposes the learning problem into fast and slow timescales: local linearization for rapid parameter updates guided by control-theoretic excitation principles, and global nonlinear structure learning through meta-RL policies that optimize long-horizon information acquisition.

3. **Derive finite-sample complexity bounds** that explicitly characterize the relationship between excitation persistence measures, degrees of system nonlinearity (measured through Lipschitz constants and higher-order smoothness), and learning sample requirements, extending classical identifiability results to online settings with probabilistic safety guarantees.

4. **Validate the framework empirically** on robotic manipulation and control tasks, demonstrating significant improvements in sample efficiency (target: 3-5× reduction) compared to state-of-the-art model-based RL while maintaining provable stability and safety.

### Significance

This research addresses critical gaps at the intersection of RL and control theory:

- **Theoretical Impact**: By formalizing the connection between persistent excitation and RL exploration, we provide a principled foundation for sample-efficient learning in nonlinear systems with stability guarantees—a longstanding open problem in both communities.

- **Practical Impact**: The framework enables deployment of learning-based control in safety-critical applications where current RL methods are unsuitable, potentially transforming industrial automation, robotics, and autonomous systems.

- **Interdisciplinary Bridge**: This work creates concrete theoretical and algorithmic bridges between control theory and RL, facilitating knowledge transfer and collaborative innovation between communities that have historically operated in parallel.

## 3. Methodology

### 3.1 Problem Formulation

We consider continuous-time nonlinear control systems of the form:

$$\dot{x}(t) = f(x(t), u(t), \theta) + w(t)$$

where $x(t) \in \mathcal{X} \subseteq \mathbb{R}^n$ is the state, $u(t) \in \mathcal{U} \subseteq \mathbb{R}^m$ is the control input, $\theta \in \Theta \subseteq \mathbb{R}^p$ represents unknown system parameters, and $w(t)$ is process noise with bounded variance $\sigma_w^2$.

**Assumptions:**
- (A1) The function $f$ is $L_f$-Lipschitz continuous in $(x,u)$ and $\beta$-smooth (twice differentiable with bounded Hessian).
- (A2) There exists a known safe set $\mathcal{X}_{safe} \subset \mathcal{X}$ with a control barrier function $h: \mathcal{X} \rightarrow \mathbb{R}$ satisfying standard CBF conditions.
- (A3) A control Lyapunov function $V: \mathcal{X} \rightarrow \mathbb{R}_+$ exists certifying stabilizability of the system.

**Objective:** Design a learning algorithm that, with probability at least $1-\delta$:
1. Maintains safety: $x(t) \in \mathcal{X}_{safe}$ for all $t \geq 0$
2. Achieves sublinear regret: $\text{Regret}(T) = \sum_{t=0}^{T} c(x_t, u_t) - \sum_{t=0}^{T} c(x_t^*, u_t^*) = O(\sqrt{T})$
3. Learns system parameters: $\|\hat{\theta}_T - \theta^*\| \leq \epsilon$ with sample complexity $O(\text{poly}(n,m,p,L_f,\beta,1/\epsilon))$

### 3.2 Adaptive Information-Geometric Excitation Design

#### 3.2.1 Fisher Information Matrix

For parameter estimation, we construct the Fisher Information Matrix (FIM) that quantifies the information content of observations about unknown parameters. For discrete-time observations with sampling period $\Delta t$, the FIM is:

$$\mathcal{I}(\theta) = \mathbb{E}\left[\left(\frac{\partial \log p(x_{t+1}|x_t, u_t, \theta)}{\partial \theta}\right)\left(\frac{\partial \log p(x_{t+1}|x_t, u_t, \theta)}{\partial \theta}\right)^T\right]$$

Under Gaussian noise assumptions, this simplifies to:

$$\mathcal{I}(\theta) = \frac{1}{\sigma_w^2} \mathbb{E}\left[\left(\frac{\partial f(x_t, u_t, \theta)}{\partial \theta}\right)^T\left(\frac{\partial f(x_t, u_t, \theta)}{\partial \theta}\right)\right]$$

#### 3.2.2 Safe Excitation Optimization

At each decision epoch $t$, we solve the following constrained optimization:

$$u_t^* = \arg\max_{u \in \mathcal{U}} \text{tr}\left(\mathcal{I}_t(\theta | x_t, u)\right) + \lambda V_t(x_t, u)$$

subject to:
- Safety constraint: $\nabla h(x_t)^T f(x_t, u, \hat{\theta}_t) \geq -\alpha h(x_t)$ (CBF condition)
- Stability constraint: $\nabla V(x_t)^T f(x_t, u, \hat{\theta}_t) \leq -\gamma V(x_t)$ (CLF condition)

where $\mathcal{I}_t$ is the instantaneous FIM contribution, $V_t$ represents the learned value function, and $\lambda$ balances exploration and exploitation.

#### 3.2.3 Persistent Excitation Measure

We introduce a novel **adaptive persistence metric** $\rho_T$ that extends classical persistent excitation to online nonlinear settings:

$$\rho_T = \lambda_{\min}\left(\frac{1}{T}\sum_{t=1}^{T} \frac{\partial f(x_t, u_t, \hat{\theta}_t)}{\partial \theta}\left(\frac{\partial f(x_t, u_t, \hat{\theta}_t)}{\partial \theta}\right)^T\right)$$

The condition $\rho_T \geq \rho_{min} > 0$ ensures sufficient information accumulation for parameter convergence.

### 3.3 Hierarchical Learning Architecture

#### 3.3.1 Fast Timescale: Local Linear Approximation

At fast timescale $\tau \in [0, T_{fast}]$, we linearize the system around the current state-parameter estimate:

$$\Delta \dot{x} = A(x_t, u_t, \hat{\theta}_t) \Delta x + B(x_t, u_t, \hat{\theta}_t) \Delta u$$

where $A = \frac{\partial f}{\partial x}$ and $B = \frac{\partial f}{\partial u}$.

We apply **recursive least squares (RLS)** with forgetting factor $\lambda_{RLS}$ for rapid local parameter updates:

$$\hat{\theta}_{t+1} = \hat{\theta}_t + K_t(y_t - \hat{y}_t)$$
$$K_t = P_t \Phi_t^T(R + \Phi_t P_t \Phi_t^T)^{-1}$$
$$P_{t+1} = \frac{1}{\lambda_{RLS}}(P_t - K_t \Phi_t P_t)$$

where $\Phi_t = \frac{\partial f}{\partial \theta}|_{x_t, u_t, \hat{\theta}_t}$ and $P_t$ is the parameter covariance matrix.

#### 3.3.2 Slow Timescale: Global Nonlinear Meta-Policy

At slow timescale $k \in \{1, 2, \ldots, K\}$ (where each epoch spans $T_{fast}$ steps), we optimize a meta-policy $\pi_\phi$ that selects high-level exploration strategies. The meta-policy is parameterized by a neural network with parameters $\phi$ and trained using Proximal Policy Optimization (PPO).

**Meta-state representation:**
$$s_k = [x_k, \hat{\theta}_k, \text{vec}(P_k), \rho_k, V(x_k), h(x_k)]$$

**Meta-reward:**
$$r_k = \underbrace{\Delta \log|\mathcal{I}_k|}_{\text{information gain}} - \underbrace{\alpha_1 \mathbb{1}[h(x) < h_{min}]}_{\text{safety penalty}} - \underbrace{\alpha_2 \|\nabla V\|}_{\text{stability cost}} + \underbrace{\alpha_3 R_{task}}_{\text{task reward}}$$

The meta-policy outputs parameters for the local excitation design, such as exploration temperature $\lambda_k$, safety margin $\alpha_k$, and reference tracking targets.

### 3.4 Theoretical Analysis Framework

#### 3.4.1 Sample Complexity Bound

We derive the following finite-sample bound for parameter estimation error:

**Theorem 1 (Informal):** Under assumptions (A1)-(A3), with persistent excitation condition $\rho_T \geq \rho_{min}$, the parameter estimation error satisfies with probability at least $1-\delta$:

$$\|\hat{\theta}_T - \theta^*\| \leq O\left(\sqrt{\frac{p \log(pT/\delta)}{\rho_{min} T}} + \frac{L_f \beta}{\rho_{min}} \sqrt{\frac{\log(1/\delta)}{T}}\right)$$

The proof leverages martingale concentration inequalities and local linearization error bounds that depend explicitly on the Lipschitz constant $L_f$ and smoothness $\beta$.

#### 3.4.2 Regret Bound

**Theorem 2 (Informal):** The proposed algorithm achieves regret:

$$\text{Regret}(T) \leq \tilde{O}\left(\sqrt{\beta L_f n m p T} + \frac{L_f^2}{\rho_{min}} \sqrt{T}\right)$$

This bound decomposes regret into exploration cost (first term) and parametric uncertainty (second term), showing explicit dependence on system properties.

### 3.5 Algorithmic Implementation

**Algorithm 1: Hierarchical Adaptive Excitation Learning (HAEL)**

```
Input: Initial state x_0, safety functions h and V, horizon T
Output: Learned parameters θ_T, control policy π

Initialize: θ_0, P_0, meta-policy π_φ
for meta-episode k = 1 to K do
    // Slow timescale: Update meta-policy
    Sample meta-state s_k = [x_k, θ_k, vec(P_k), ρ_k, V(x_k), h(x_k)]
    Select exploration parameters λ_k ~ π_φ(s_k)
    
    for t = k*T_fast to (k+1)*T_fast do
        // Fast timescale: Local learning and control
        Compute local FIM: I_t(θ | x_t, u)
        Solve safe excitation optimization:
            u_t = argmax tr(I_t) + λ_k V_t(x_t,u)
            s.t. CBF and CLF constraints
        Execute u_t, observe x_{t+1}
        Update θ_t using RLS with forgetting
        Update covariance P_t
        Compute persistence ρ_t
    end for
    
    // Compute meta-reward and update meta-policy
    r_k = Δlog|I_k| - penalties + R_task
    Update π_φ using PPO with (s_k, λ_k, r_k)
end for
```

### 3.6 Experimental Design

#### 3.6.1 Simulation Environments

We will validate the framework on three benchmark tasks:

1. **Inverted Pendulum with Unknown Parameters**: 
   - State: $x = [\theta, \dot{\theta}]$ (angle, angular velocity)
   - Unknown parameters: mass $m$, length $l$, damping $d$
   - Safety constraint: $|\theta| \leq \theta_{max}$

2. **Robotic Manipulator (7-DOF Arm)**:
   - State: Joint angles and velocities $x \in \mathbb{R}^{14}$
   - Unknown parameters: Link masses, friction coefficients
   - Safety: Joint limits and collision avoidance (CBF)
   - Task: Reach target with minimal time and energy

3. **Quadrotor with Aerodynamic Uncertainty**:
   - State: Position, orientation, velocities $x \in \mathbb{R}^{12}$
   - Unknown: Drag coefficients, motor constants
   - Safety: Altitude and velocity bounds
   - Task: Trajectory tracking in turbulent conditions

#### 3.6.2 Baseline Comparisons

We compare HAEL against:
- **Model-Based RL**: PETS (Probabilistic Ensembles with Trajectory Sampling)
- **Safe RL**: Safe PPO with CBF constraints, RCPO (Reward Constrained Policy Optimization)
- **Adaptive Control**: Model Reference Adaptive Control (MRAC), L1-adaptive control
- **Combined Approaches**: MPC-guided RL (Kostelac et al., 2025)

#### 3.6.3 Evaluation Metrics

1. **Sample Efficiency**: Number of environment interactions to achieve 90% of optimal performance
2. **Safety Violations**: Percentage of episodes with constraint violations, severity of violations
3. **Parameter Convergence**: $\|\hat{\theta}_T - \theta^*\|$ versus time
4. **Regret**: Cumulative cost difference from optimal policy
5. **Computational Cost**: Wall-clock time per control decision
6. **Robustness**: Performance under model mismatch (30% parameter variations) and disturbances

#### 3.6.4 Ablation Studies

To isolate the contribution of each component:
1. Remove hierarchical structure (single-timescale learning)
2. Replace information-geometric excitation with ε-greedy exploration
3. Remove safety constraints (unconstrained optimization)
4. Compare different persistence measures ($\rho_T$ vs classical definitions)
5. Vary meta-policy update frequencies

## 4. Expected Outcomes & Impact

### Expected Theoretical Contributions

1. **Unified Framework**: A mathematically rigorous framework connecting persistent excitation from control theory to exploration in RL, providing the first sample complexity bounds for nonlinear systems that explicitly incorporate control-theoretic excitation measures.

2. **Novel Bounds**: Finite-sample complexity results showing polynomial dependence on system dimension and properties (Lipschitz constants, smoothness), demonstrating $O(\sqrt{T})$ regret for smooth nonlinear systems—improving upon existing results that scale linearly or lack explicit constants.

3. **Safety-Exploration Trade-off**: Formal characterization of the fundamental trade-off between information acquisition and constraint satisfaction, quantifying how safety requirements necessarily increase sample complexity.

### Expected Empirical Outcomes

1. **Sample Efficiency**: 3-5× reduction in samples required to achieve target performance compared to state-of-the-art model-based RL methods (PETS, MBPO) across benchmark tasks.

2. **Safety Guarantees**: Zero or near-zero constraint violations (target: <1% of episodes) while maintaining competitive learning speed—a significant improvement over standard safe RL methods that often sacrifice sample efficiency for safety.

3. **Robustness**: Demonstrated stability under 30% parameter variations and significant disturbances, with graceful performance degradation rather than catastrophic failure.

4. **Scalability**: Successful application to high-dimensional systems (7-DOF manipulator, 12-state quadrotor) with reasonable computational requirements (< 10ms per control cycle).

### Broader Impact

**For Control Theory Community:**
- Provides modern learning-theoretic tools and sample complexity analysis for adaptive control problems
- Offers principled methods for handling high-dimensional nonlinear systems that classical approaches struggle with
- Demonstrates how data-driven approaches can complement traditional control design

**For RL Community:**
- Introduces control-theoretic structure (persistent excitation, Lyapunov stability) as inductive biases for sample-efficient learning
- Provides theoretical foundations for safe exploration beyond constraint satisfaction
- Establishes connections to classical identification theory that can inspire new algorithmic designs

**For Applications:**
- Enables deployment of learning-based control in safety-critical domains (medical robotics, industrial automation, aerospace) where current RL methods are unsuitable
- Reduces commissioning time and cost for adaptive control systems by minimizing data requirements
- Provides certificates of safety and stability required for regulatory approval in high-stakes applications

**Long-term Vision:**
This research establishes a foundation for "learning-enabled control theory"—a discipline that systematically incorporates online learning into control systems design while preserving the safety, stability, and performance guarantees that make control theory applicable to real-world systems. By bridging theoretical and algorithmic gaps between RL and control, we anticipate this work will catalyze a new generation of adaptive, safe, and sample-efficient autonomous systems capable of operating in complex, uncertain environments.

The proposed framework also opens several exciting future directions: extension to partial observability (POMDPs), multi-agent coordination with distributed learning, integration with offline data for hybrid learning, and application to large-scale network control problems (power grids, traffic systems) where both safety and adaptability are paramount.