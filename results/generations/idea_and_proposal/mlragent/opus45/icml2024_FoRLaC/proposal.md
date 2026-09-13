# Research Proposal: Bridging Stability Guarantees and Regret Bounds: A Unified Framework for Safe Online Learning in Nonlinear Control Systems

## 1. Introduction

### Background

The deployment of learning-based control systems in safety-critical applications—such as autonomous vehicles, industrial automation, and robotic manipulation—requires algorithms that can simultaneously achieve two seemingly competing objectives: efficient learning from limited data and rigorous stability guarantees throughout operation. This challenge sits at the intersection of two research communities that have historically developed distinct mathematical frameworks and performance measures.

Reinforcement learning (RL) theory has primarily focused on regret minimization and sample complexity as performance metrics, developing sophisticated exploration strategies that enable efficient learning in unknown environments. The canonical result in this domain is the achievement of $\tilde{O}(\sqrt{T})$ regret bounds, indicating that the cumulative suboptimality grows sublinearly with the time horizon $T$. However, standard RL algorithms often prioritize exploration in ways that may temporarily destabilize the system or violate safety constraints—an unacceptable risk in high-stakes applications.

Control theory, by contrast, has developed rich mathematical tools centered on stability, robustness, and constraint satisfaction. Lyapunov functions, barrier certificates, and invariant set theory provide powerful guarantees that system trajectories remain within safe operating regions. Yet classical control approaches often assume known dynamics and may sacrifice learning efficiency when adapting to uncertainty, leading to overly conservative behavior that fails to exploit available data.

Recent work has begun to bridge this gap. Schiffer and Janson (2024, 2025) demonstrated that safety constraints can actually facilitate faster learning in linear systems, achieving $\tilde{O}(\sqrt{T})$ regret while maintaining state constraints. Zhou et al. (2023) extended safe control to nonlinear control-affine systems under adversarial disturbances. Meanwhile, approaches integrating control barrier functions with reinforcement learning have shown promise for discrete-time nonlinear systems. Despite these advances, a unified theoretical framework that explicitly characterizes the fundamental trade-offs between learning efficiency and stability margins for general nonlinear systems remains elusive.

### Research Objectives

This research proposes to develop a comprehensive theoretical framework that bridges the gap between regret-based performance measures from RL and stability guarantees from control theory. Our specific objectives are:

1. **Define and characterize a stability-regret Pareto frontier** that mathematically quantifies the fundamental limits of simultaneously achieving low regret and high stability margins in online learning for nonlinear control systems.

2. **Develop Lyapunov-guided exploration strategies** that constrain exploration decisions using learned certificate functions, ensuring forward invariance of safe sets while enabling efficient learning.

3. **Establish sample complexity bounds** that explicitly depend on the system's stability margin, nonlinearity structure, and the geometry of safe operating regions.

4. **Derive information-theoretic lower bounds** that identify when stability requirements fundamentally limit learning speed and characterize system classes where safety comes "for free."

### Significance

This research addresses a critical barrier to deploying learning-based control in real-world applications. By providing a unified framework with principled trade-off characterizations, practitioners will gain theoretical guidance for algorithm selection and parameter tuning in safety-critical domains. The framework will identify when aggressive exploration is fundamentally incompatible with stability requirements and when safety constraints can actually accelerate learning—a phenomenon observed empirically but lacking theoretical explanation for general nonlinear systems.

## 2. Methodology

### 2.1 Problem Formulation

We consider discrete-time nonlinear control systems of the form:

$$x_{t+1} = f(x_t, u_t) + w_t$$

where $x_t \in \mathcal{X} \subseteq \mathbb{R}^n$ is the state, $u_t \in \mathcal{U} \subseteq \mathbb{R}^m$ is the control input, $f: \mathcal{X} \times \mathcal{U} \to \mathbb{R}^n$ is an unknown nonlinear dynamics function, and $w_t$ is a stochastic disturbance with $\mathbb{E}[w_t] = 0$ and $\|w_t\| \leq \sigma$ almost surely.

**Safety Constraint:** The state must remain within a safe set $\mathcal{S} \subset \mathcal{X}$ defined by a constraint function $h: \mathcal{X} \to \mathbb{R}$ such that $\mathcal{S} = \{x : h(x) \geq 0\}$.

**Performance Objective:** We aim to minimize the cumulative cost $\sum_{t=1}^{T} c(x_t, u_t)$ where $c: \mathcal{X} \times \mathcal{U} \to \mathbb{R}_+$ is a known stage cost.

**Regret Definition:** The regret relative to the optimal safe policy $\pi^*$ is:

$$R(T) = \sum_{t=1}^{T} c(x_t, u_t) - \sum_{t=1}^{T} c(x_t^*, u_t^*)$$

where $(x_t^*, u_t^*)$ denotes the trajectory under $\pi^*$ with full knowledge of $f$.

**Stability Margin:** We define the stability margin $\gamma > 0$ as the largest value such that a Lyapunov function $V: \mathcal{X} \to \mathbb{R}_+$ satisfies:

$$\mathbb{E}[V(x_{t+1}) | x_t, u_t] \leq V(x_t) - \gamma \|x_t\|^2 + \delta$$

for some $\delta > 0$ accounting for disturbances.

### 2.2 Stability-Regret Pareto Frontier

We introduce the concept of a stability-regret Pareto frontier that characterizes achievable performance pairs $(\gamma, R(T))$.

**Definition 1 (Stability-Regret Trade-off Function):** For a given system class $\mathcal{F}$ and safety constraint $\mathcal{S}$, define:

$$\Phi(\gamma) = \inf_{\pi \in \Pi_\gamma} \sup_{f \in \mathcal{F}} \mathbb{E}[R_\pi(T)]$$

where $\Pi_\gamma$ denotes the set of policies achieving stability margin at least $\gamma$.

**Theoretical Contribution 1:** We will derive closed-form expressions for $\Phi(\gamma)$ for structured system classes, including:

- Control-affine systems: $f(x,u) = f_0(x) + g(x)u$
- Lipschitz nonlinear systems with known Lipschitz constant $L_f$
- Systems with known control-Lyapunov functions but unknown dynamics

The derivation will employ techniques from information theory and statistical learning, building on the framework of Russo and Van Roy (2016) for information-theoretic regret bounds.

### 2.3 Lyapunov-Guided Exploration Strategy

We propose an algorithmic framework that integrates exploration with stability certificates.

**Algorithm 1: Lyapunov-Constrained Optimistic Exploration (LCOE)**

**Input:** Initial safe policy $\pi_0$, confidence parameter $\delta$, exploration bonus parameter $\beta_t$

**Initialize:** Dataset $\mathcal{D}_0 = \emptyset$, Lyapunov function estimate $\hat{V}_0$

**For $t = 1, 2, \ldots, T$:**

1. **Dynamics Estimation:** Fit dynamics model $\hat{f}_t$ using $\mathcal{D}_{t-1}$ with uncertainty quantification:
   $$\hat{f}_t(x, u) = \mu_t(x, u), \quad \sigma_t(x, u) = \text{uncertainty estimate}$$

2. **Confidence Set Construction:** Define:
   $$\mathcal{F}_t = \{f : \|f(x,u) - \hat{f}_t(x,u)\| \leq \beta_t \sigma_t(x,u), \forall (x,u)\}$$

3. **Lyapunov Function Update:** Solve for $\hat{V}_t$ satisfying:
   $$\max_{f \in \mathcal{F}_t} \mathbb{E}[\hat{V}_t(f(x_t, u)) | x_t, u] \leq \hat{V}_t(x_t) - \gamma \|x_t\|^2 + \delta_V$$

4. **Safe Exploration Set:** Define admissible actions:
   $$\mathcal{U}_{\text{safe}}(x_t) = \{u \in \mathcal{U} : \min_{f \in \mathcal{F}_t} h(f(x_t, u) - \kappa \sigma_t(x_t, u)) \geq 0\}$$

5. **Optimistic Action Selection:** Choose:
   $$u_t = \arg\min_{u \in \mathcal{U}_{\text{safe}}(x_t)} \left[ c(x_t, u) - \alpha_t \cdot I_t(x_t, u) \right]$$
   where $I_t(x_t, u)$ is an information gain bonus measuring exploration value.

6. **Update:** Execute $u_t$, observe $x_{t+1}$, update $\mathcal{D}_t = \mathcal{D}_{t-1} \cup \{(x_t, u_t, x_{t+1})\}$

**Theoretical Contribution 2:** We will prove that LCOE achieves:

$$R(T) \leq \tilde{O}\left(\sqrt{T \cdot d_{\text{eff}} \cdot \log(1/\delta)}\right) + O\left(\frac{1}{\gamma^2}\right)$$

where $d_{\text{eff}}$ is the effective dimension of the dynamics model class, while maintaining $\mathbb{P}(x_t \in \mathcal{S}, \forall t) \geq 1 - \delta$.

### 2.4 Sample Complexity Analysis

We establish sample complexity bounds that reveal the explicit dependence on system properties.

**Theorem 1 (Sample Complexity with Stability Margin):** For a control-affine system with Lipschitz constants $L_f, L_g$ and stability margin $\gamma$, the number of samples required to learn an $\epsilon$-optimal safe policy satisfies:

$$N(\epsilon, \gamma, \delta) = \tilde{O}\left(\frac{(L_f + L_g)^2 \cdot n \cdot m}{\epsilon^2 \gamma^2} \cdot \log\left(\frac{|\mathcal{S}|}{\delta}\right)\right)$$

where $|\mathcal{S}|$ characterizes the volume of the safe set.

**Theorem 2 (Information-Theoretic Lower Bound):** For any algorithm maintaining stability margin $\gamma$ with probability $1-\delta$, there exists a system instance such that:

$$R(T) \geq \Omega\left(\sqrt{\frac{T}{\gamma}}\right)$$

This lower bound reveals the fundamental cost of stability: requiring larger stability margins necessarily increases regret.

### 2.5 Experimental Validation

We will validate our theoretical framework through comprehensive experiments on:

**Benchmark Systems:**
1. **Inverted Pendulum:** A canonical nonlinear system with state constraints (angle limits)
2. **Cart-Pole with Track Limits:** Safety constraints on cart position
3. **Quadrotor Hovering:** 12-dimensional state space with altitude and velocity constraints
4. **Simulated Autonomous Vehicle:** Lane-keeping with collision avoidance constraints

**Baseline Comparisons:**
- Unconstrained optimistic algorithms (OFU-based methods)
- Conservative robust control (worst-case optimal)
- Control barrier function approaches without optimism
- Risk-aware safe RL methods (Esmaeili et al., 2025)

**Evaluation Metrics:**
1. **Cumulative Regret:** $R(T) = \sum_{t=1}^T c(x_t, u_t) - T \cdot J^*$
2. **Safety Violation Rate:** $\frac{1}{T}\sum_{t=1}^T \mathbf{1}[x_t \notin \mathcal{S}]$
3. **Stability Margin Achieved:** Empirical estimate of $\gamma$ from trajectory data
4. **Sample Efficiency:** Number of samples to achieve $\epsilon$-optimality
5. **Computational Time:** Per-step computation cost

**Experimental Protocol:**
- 50 independent runs per configuration with randomized initial conditions
- Varying safety constraint tightness (distance to constraint boundary)
- Varying system nonlinearity (through parameter scaling)
- Statistical significance testing via bootstrapped confidence intervals

### 2.6 Mathematical Tools

Our analysis will leverage:

1. **Robust Lyapunov Analysis:** Extension of classical Lyapunov methods to handle model uncertainty via:
$$V(x_{t+1}) \leq V(x_t) - \alpha_1(\|x_t\|) + \phi(\|w_t\|)$$
where $\phi$ is a class-$\mathcal{K}$ function bounding disturbance effects.

2. **Eluder Dimension:** Characterizing exploration complexity for nonlinear function classes following Russo and Van Roy's framework.

3. **Control Barrier Functions:** Ensuring forward invariance via:
$$\Delta B(x, u) = B(f(x,u)) - B(x) \geq -\alpha(B(x))$$
where $B$ defines the safe set boundary.

## 3. Expected Outcomes & Impact

### Theoretical Contributions

1. **Unified Framework:** A mathematically rigorous framework connecting regret bounds and stability margins, providing the first complete characterization of achievable trade-offs for nonlinear systems.

2. **Novel Algorithms:** The LCOE algorithm with provable guarantees—achieving $\tilde{O}(\sqrt{T})$ regret while maintaining prescribed stability margins with high probability.

3. **Fundamental Limits:** Information-theoretic lower bounds identifying system classes where safety constraints are "free" (not increasing regret order) versus those requiring explicit trade-offs.

4. **Sample Complexity Characterization:** Precise dependence of sample requirements on stability margin, nonlinearity structure, and safe set geometry.

### Practical Impact

1. **Algorithm Selection Guidance:** Practitioners will have principled criteria for choosing between conservative safe controllers and more exploratory approaches based on their specific safety requirements and performance objectives.

2. **Parameter Tuning:** Explicit trade-off curves will inform the selection of exploration parameters and safety margins in deployed systems.

3. **Certification Framework:** The theoretical guarantees provide a foundation for certifying learning-based controllers in safety-critical applications, potentially informing regulatory standards.

### Broader Impact

This research contributes to the broader goal of deploying machine learning in high-stakes domains by providing theoretical foundations that bridge the gap between learning efficiency and safety guarantees. The framework addresses a key barrier to adoption of RL in industrial automation, autonomous systems, and other safety-critical applications, potentially accelerating the responsible deployment of adaptive control systems. By identifying when aggressive learning is fundamentally incompatible with safety and when it can proceed safely, we enable more informed decision-making in the design and deployment of learning-based control systems.