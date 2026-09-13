# Research Proposal: Verified Neural Contraction Metrics for Provable Regret Bounds in Nonlinear Adaptive Control

## 1. Introduction

### 1.1 Background

Reinforcement learning (RL) has achieved remarkable empirical success across diverse domains, from game playing to robotic manipulation. However, deploying RL algorithms in high-stakes applications—such as autonomous vehicles, industrial automation, and adaptive transportation systems—remains challenging due to the lack of formal theoretical guarantees. Control theory, by contrast, provides rigorous stability and robustness guarantees but traditionally assumes known system dynamics, limiting its applicability when models are uncertain or must be learned online.

This fundamental tension between the flexibility of learning-based approaches and the rigor of control-theoretic guarantees represents one of the most significant open challenges in decision-making under uncertainty. Recent work has begun bridging these communities: Dean et al. (2018) established finite-time regret bounds for adaptive Linear Quadratic Regulator (LQR) control, demonstrating that $R(T) \leq \tilde{O}(\sqrt{T})$ regret is achievable for linear systems. Simchowitz (2020) proved this scaling is information-theoretically optimal. However, extending these results to nonlinear systems has proven difficult, as the perturbation analysis techniques that work elegantly for linear systems do not directly generalize.

Contraction theory, introduced by Lohmiller and Slotine (1998), offers a promising path forward. Unlike Lyapunov stability, which characterizes convergence to equilibrium points, contraction theory guarantees that all system trajectories converge toward each other at an exponential rate. This property—incremental stability—is particularly powerful for adaptive control because it bounds how trajectory perturbations (caused by parameter estimation errors) propagate over time. If a system contracts at rate $\rho \in (0,1)$, then trajectory deviations decay as $\|\delta x(t)\| \leq \rho^t \|\delta x(0)\|$, providing exactly the quantitative bound needed for regret analysis.

Recent advances in neural network verification, particularly the $\alpha,\beta$-CROWN framework (Wang et al., 2021), enable formal certification of neural network properties. Li et al. (2025) demonstrated that contraction conditions for neural network controllers can be verified using these tools, opening the possibility of combining learned controllers with rigorous mathematical guarantees.

### 1.2 Research Objectives

This research aims to develop the first framework providing verified finite-time regret bounds for adaptive control of nonlinear systems. Our specific objectives are:

1. **Develop a joint learning algorithm** for neural contraction metrics $M_\phi(x)$ and controllers $\pi_\theta(x)$ that achieves verifiable contraction rates.

2. **Establish formal verification procedures** using $\alpha,\beta$-CROWN to certify contraction rates $\rho \in (0,1)$ for learned neural network components.

3. **Derive theoretical regret bounds** of the form $R(T) \leq O(\sqrt{T} \cdot \text{poly}(1/(1-\rho), d))$ through trajectory sensitivity analysis enabled by verified contraction.

4. **Empirically validate** the theoretical predictions on benchmark nonlinear control problems with state dimension $d \leq 10$.

### 1.3 Significance

This research addresses a critical gap at the intersection of reinforcement learning and control theory. By providing the first verified regret guarantees for nonlinear adaptive control, we enable:

- **Trustworthy deployment** of learning-based controllers in safety-critical applications where formal guarantees are mandatory.
- **Quantitative performance certificates** that relate system properties (contraction rate, dimension) to expected learning performance.
- **Theoretical unification** of RL regret analysis with control-theoretic stability concepts, advancing both fields.

The framework directly addresses the workshop's focus on "developing a learning theory of decision systems" by providing rigorous performance measures (regret bounds), characterizing fundamental assumptions (incremental stabilizability), and bridging offline verification with online learning.

## 2. Methodology

### 2.1 Problem Formulation

Consider a discrete-time nonlinear dynamical system:
$$x_{t+1} = f(x_t, u_t) + w_t$$
where $x_t \in \mathbb{R}^d$ is the state, $u_t \in \mathbb{R}^m$ is the control input, $f: \mathbb{R}^d \times \mathbb{R}^m \to \mathbb{R}^d$ is an unknown smooth dynamics function, and $w_t$ is bounded process noise with $\|w_t\| \leq \sigma_w$.

The learner interacts with the system over $T$ time steps, incurring stage costs $c(x_t, u_t)$. The cumulative regret is defined as:
$$R(T) = \sum_{t=1}^{T} \left[ c(x_t, u_t) - c(x_t^*, u_t^*) \right]$$
where $(x_t^*, u_t^*)$ denotes the trajectory under the optimal controller with known dynamics.

**Assumption (Incremental Stabilizability):** The system admits a contraction metric, i.e., there exists a positive definite matrix function $M(x) \succ 0$ and contraction rate $\rho \in (0,1)$ such that for any two trajectories $x, x'$ under the same control:
$$\|x' - x\|_{M(f(x,u))} \leq \rho \|x' - x\|_{M(x)}$$
where $\|z\|_{M(x)} = \sqrt{z^\top M(x) z}$ is the Riemannian norm induced by $M(x)$.

### 2.2 Neural Contraction Metric Learning

We parameterize the contraction metric and controller using neural networks:

**Metric Network:** $M_\phi(x): \mathbb{R}^d \to \mathbb{R}^{d \times d}$ outputs a symmetric positive definite matrix. We use the Cholesky parameterization:
$$M_\phi(x) = L_\phi(x) L_\phi(x)^\top + \epsilon I$$
where $L_\phi(x)$ is a lower triangular matrix output by a neural network with architecture $[d, 64, 64, d(d+1)/2]$ and $\epsilon = 10^{-4}$ ensures positive definiteness.

**Controller Network:** $\pi_\theta(x): \mathbb{R}^d \to \mathbb{R}^m$ with architecture $[d, 64, 64, m]$ using ReLU activations.

**Joint Training Objective:** We minimize:
$$\mathcal{L}(\phi, \theta) = \mathcal{L}_{\text{task}} + \lambda_c \mathcal{L}_{\text{contraction}} + \lambda_r \mathcal{L}_{\text{reg}}$$

where:
- $\mathcal{L}_{\text{task}} = \mathbb{E}_{x \sim \mathcal{D}} \left[ \sum_{t=0}^{H} \gamma^t c(x_t, \pi_\theta(x_t)) \right]$ is the task cost over horizon $H$
- $\mathcal{L}_{\text{contraction}} = \mathbb{E}_{x, \delta x} \left[ \max(0, \|\delta x'\|_{M_\phi(x')}^2 - \rho_{\text{target}}^2 \|\delta x\|_{M_\phi(x)}^2) \right]$ penalizes contraction violations
- $\mathcal{L}_{\text{reg}}$ includes weight decay and Lipschitz regularization for verification tractability

The contraction loss is computed by sampling perturbations $\delta x$ and propagating through the linearized dynamics:
$$\delta x' = \frac{\partial f}{\partial x}(x, \pi_\theta(x)) \delta x + \frac{\partial f}{\partial u}(x, \pi_\theta(x)) \frac{\partial \pi_\theta}{\partial x}(x) \delta x$$

**Training Algorithm:**
```
Algorithm 1: Joint Contraction Metric and Controller Learning
Input: Dataset D, target contraction rate ρ_target, epochs E
Output: Trained parameters φ, θ

1: Initialize φ, θ randomly
2: for epoch = 1 to E do
3:     for batch (x, x_next) in D do
4:         Sample perturbations δx ~ N(0, σ²I)
5:         Compute δx' via linearized dynamics
6:         Compute L_contraction using M_φ
7:         Compute L_task via trajectory rollout
8:         Update φ, θ via Adam optimizer
9:     end for
10:    if epoch % 50 == 0 then
11:        Attempt verification (early stopping if successful)
12:    end if
13: end for
```

### 2.3 Formal Verification via α,β-CROWN

After training, we verify the contraction condition using the $\alpha,\beta$-CROWN neural network verifier. The verification problem is formulated as:

**Verification Query:** For all $x \in \mathcal{X}$ (compact state space) and all $\|\delta x\| \leq \delta_{\max}$:
$$\|\delta x'\|_{M_\phi(f(x, \pi_\theta(x)))}^2 \leq \rho^2 \|\delta x\|_{M_\phi(x)}^2$$

This is equivalent to verifying that the neural network computing:
$$g(x, \delta x) = \|\delta x'\|_{M_\phi(x')}^2 - \rho^2 \|\delta x\|_{M_\phi(x)}^2$$
satisfies $g(x, \delta x) \leq 0$ for all inputs in the specified domain.

$\alpha,\beta$-CROWN computes tight linear bounds on the neural network output using:
1. **Bound propagation:** Linear relaxations of ReLU activations
2. **Branch-and-bound:** Splitting input domains when bounds are inconclusive
3. **Optimized bounds:** Gradient-based optimization of relaxation parameters

**Verification Procedure:**
```
Algorithm 2: Contraction Verification
Input: Trained networks M_φ, π_θ, state bounds X, target ρ
Output: Verified contraction rate ρ_verified or FAIL

1: Construct verification network g(x, δx)
2: Initialize ρ_test = ρ_target
3: while ρ_test < 1.0 do
4:     result = αβ-CROWN.verify(g ≤ 0, X, ρ_test)
5:     if result == VERIFIED then
6:         return ρ_verified = ρ_test
7:     else
8:         ρ_test = ρ_test + 0.02  // Relax contraction rate
9:     end if
10: end while
11: return FAIL
```

### 2.4 Regret Bound Derivation

Given a verified contraction rate $\rho$, we derive regret bounds through trajectory sensitivity analysis.

**Theorem (Informal):** Under Assumptions A1-A4, for an incrementally stabilizable system with verified contraction rate $\rho$ and state dimension $d$, the adaptive control regret satisfies:
$$R(T) \leq C \cdot \sqrt{T} \cdot \frac{d^2}{(1-\rho)^2} \cdot \log(T)$$
where $C$ depends on cost function Lipschitz constants and noise bounds.

**Proof Sketch:**

*Step 1 (Trajectory Perturbation Bound):* Let $\hat{x}_t$ be the trajectory under the learned controller with estimated dynamics $\hat{f}$, and $x_t^*$ be the optimal trajectory. The parameter estimation error $\|\hat{f} - f\|$ causes trajectory deviation. By contraction:
$$\|x_t - \hat{x}_t\| \leq \sum_{s=0}^{t-1} \rho^{t-1-s} \|\hat{f}(x_s, u_s) - f(x_s, u_s)\|$$

*Step 2 (Estimation Error Decay):* Using standard online learning analysis, the parameter estimation error after $t$ samples satisfies:
$$\|\hat{f}_t - f\| \leq O\left(\sqrt{\frac{d \log t}{t}}\right)$$

*Step 3 (Regret Integration):* The instantaneous regret is bounded by trajectory deviation times cost Lipschitz constant. Summing over $T$ steps:
$$R(T) \leq L_c \sum_{t=1}^{T} \|x_t - x_t^*\| \leq L_c \sum_{t=1}^{T} \sum_{s=0}^{t-1} \rho^{t-1-s} \cdot O\left(\sqrt{\frac{d}{s}}\right)$$

Evaluating the double sum using the geometric series bound $\sum_{s=0}^{t-1} \rho^{t-1-s} \leq \frac{1}{1-\rho}$ yields the stated bound.

### 2.5 Experimental Design

**Benchmark Systems:**
1. **Inverted Pendulum** ($d=2$): Classic nonlinear control benchmark
2. **Cart-Pole** ($d=4$): Underactuated system with swing-up task
3. **Acrobot** ($d=4$): Double pendulum with single actuator
4. **Polynomial Dynamics** ($d=6,8,10$): Synthetic systems with known contraction metrics for ground truth comparison

**Experimental Protocol:**

*Experiment 1 (Regret Scaling - Primary):*
- For each benchmark, run $n=20$ independent trials
- Vary time horizon $T \in \{1000, 5000, 10000, 50000\}$
- Measure cumulative regret $R(T)$
- Fit $\log R(T) = \alpha \log T + \beta$ via linear regression
- **Success criterion:** Slope $\alpha \leq 0.55$ with 95% CI

*Experiment 2 (Contraction Rate Dependence):*
- Train controllers targeting $\rho_{\text{target}} \in \{0.5, 0.7, 0.8, 0.9, 0.95\}$
- Measure verified $\rho$ and corresponding regret at $T=10000$
- Fit polynomial relationship between $R(T)$ and $1/(1-\rho)$
- **Success criterion:** Polynomial degree $\leq 3$

*Experiment 3 (Linear System Reduction):*
- Apply method to LQR problems
- Compare regret to Dean et al. (2018) baseline
- **Success criterion:** Regret within factor of 2

**Evaluation Metrics:**
- Regret $R(T)$: Primary performance measure
- Verification time: Computational cost of $\alpha,\beta$-CROWN
- Training convergence: Epochs to achieve target contraction
- Verification success rate: Fraction of trained networks that verify

**Statistical Analysis:**
- Linear regression with 95% confidence intervals for slope estimation
- ANOVA across contraction rate conditions
- Bonferroni correction for multiple comparisons
- Minimum $R^2 \geq 0.8$ for meaningful fits

### 2.6 Implementation Details

**Software Stack:**
- PyTorch for neural network training
- $\alpha,\beta$-CROWN (auto_LiRPA) for verification
- MuJoCo for physics simulation
- JAX for automatic differentiation of dynamics

**Computational Requirements:**
- Training: ~2 hours per system on single GPU (NVIDIA A100)
- Verification: 10 minutes to 2 hours depending on dimension
- Total experiments: ~500 GPU-hours

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome:** We expect to demonstrate $\sqrt{T}$ regret scaling (log-log slope $\leq 0.55$) across all benchmark systems with $d \leq 10$. This would provide the first empirical validation of provable regret bounds for nonlinear adaptive control.

**Secondary Outcomes:**
- Polynomial dependence of regret on $1/(1-\rho)$, validating the theoretical bound structure
- Verification success rates $> 80\%$ for properly trained networks
- Verification times $< 10$ minutes for $d \leq 6$, scaling to $\sim 2$ hours for $d = 10$

**Potential Negative Results:**
- If regret slope exceeds 0.7, this would indicate fundamental limitations in the contraction-based approach
- Verification failures would suggest need for alternative certification methods

### 3.2 Scientific Impact

This research makes several contributions to the foundations of RL and control:

1. **Theoretical Contribution:** First framework connecting neural network verification to finite-time regret bounds, establishing a new paradigm for certified learning-based control.

2. **Methodological Contribution:** Practical algorithms for joint learning and verification of contraction metrics, enabling deployment in safety-critical applications.

3. **Unification Contribution:** Bridges contraction theory (control) with regret analysis (RL), demonstrating how stability concepts translate to learning guarantees.

### 3.3 Practical Impact

The framework enables trustworthy deployment of adaptive controllers in:
- **Autonomous vehicles:** Verified stability during online adaptation to changing conditions
- **Industrial automation:** Certified performance bounds for process control
- **Robotics:** Safe learning of manipulation skills with formal guarantees

### 3.4 Limitations and Future Work

**Current Limitations:**
- Scalability to $d > 10$ requires advances in neural network verification
- Continuous-time extension needs additional theoretical development
- Output feedback (partial observability) not addressed

**Future Directions:**
- Probabilistic verification for scalability to higher dimensions
- Extension to POMDPs using observer-based contraction
- Integration with safe exploration for online learning

This research establishes foundations for a new generation of learning-based control systems that combine the flexibility of neural networks with the rigor of formal verification, addressing a critical need identified by both the RL and control communities.