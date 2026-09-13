# Research Proposal: Diffusion Models as Stochastic Optimal Controllers: Unifying Score Matching with Hamilton-Jacobi-Bellman Theory

## 1. Introduction

### Background

Diffusion models have emerged as one of the most powerful paradigms in generative modeling, achieving state-of-the-art results in image synthesis, audio generation, and molecular design. These models operate by learning to reverse a gradual noising process, transforming samples from a simple prior distribution (typically Gaussian) into samples from a complex target distribution. The theoretical foundation of diffusion models relies on stochastic differential equations (SDEs), where the forward process gradually corrupts data and the reverse process learns to denoise it through score function estimation.

Concurrently, stochastic optimal control theory provides a principled mathematical framework for sequential decision-making under uncertainty. Central to this theory is the Hamilton-Jacobi-Bellman (HJB) equation, a partial differential equation whose solution—the value function—characterizes optimal control policies. Despite the apparent structural similarities between diffusion model sampling (which involves controlled stochastic dynamics) and stochastic optimal control, a comprehensive theoretical and algorithmic framework that fully exploits this connection remains underdeveloped.

Recent work has begun exploring these connections. Berner et al. (2024) established fundamental links between stochastic optimal control and SDE-based generative models, while Han et al. (2025) proposed a stochastic control framework for fine-tuning diffusion models. However, these efforts have not fully leveraged the HJB framework to derive novel training objectives with improved gradient properties, nor have they systematically developed control-theoretic samplers with formal convergence guarantees. Furthermore, the potential for transferring robust control techniques to handle distribution shift and sampling errors in diffusion models remains largely unexplored.

### Research Objectives

This research aims to develop a unified theoretical and algorithmic framework that reformulates diffusion model training and sampling as stochastic optimal control problems. Our specific objectives are:

1. **Theoretical Unification**: Derive the precise correspondence between score functions in diffusion models and optimal feedback controllers through the HJB equation, establishing that the gradient of the value function equals the learned score.

2. **Control-Theoretic Training**: Develop novel training objectives based on policy iteration and temporal difference (TD) learning that offer computational and statistical advantages over standard denoising score matching.

3. **Accelerated Sampling**: Design model predictive control (MPC)-based samplers with adaptive step-size selection, achieving faster sampling with formal convergence guarantees.

4. **Robust Generative Modeling**: Transfer insights from robust control theory to develop diffusion models that are resilient to distribution shift and model misspecification.

### Significance

This research addresses fundamental questions at the intersection of machine learning, control theory, and dynamical systems. By establishing a rigorous bridge between these fields, we enable bidirectional transfer of techniques: control theory gains access to powerful function approximation methods from deep learning, while generative modeling benefits from decades of theoretical development in stability analysis, convergence proofs, and robust control design. The practical implications include faster sampling algorithms (targeting 2-5× reduction in function evaluations), improved training stability, and formal guarantees that are crucial for safety-critical applications.

## 2. Methodology

### 2.1 Theoretical Framework: HJB Formulation for Diffusion Models

**Forward and Reverse SDEs**: Consider the standard diffusion model framework. The forward process is defined by:
$$dX_t = f(X_t, t)dt + g(t)dW_t$$
where $f(x,t)$ is the drift, $g(t)$ is the diffusion coefficient, and $W_t$ is a Wiener process. Starting from data distribution $p_0(x)$, this process gradually transforms samples toward a tractable prior $p_T(x) \approx \mathcal{N}(0, \sigma_T^2 I)$.

The reverse process, running backward from $t=T$ to $t=0$, is given by:
$$dX_t = \left[f(X_t, t) - g(t)^2 \nabla_x \log p_t(X_t)\right]dt + g(t)d\bar{W}_t$$
where $\bar{W}_t$ is a reverse-time Wiener process and $\nabla_x \log p_t(x)$ is the score function.

**Stochastic Optimal Control Reformulation**: We reformulate the reverse diffusion as a stochastic optimal control problem. Define the controlled dynamics:
$$dX_t = \left[f(X_t, t) + g(t)^2 u(X_t, t)\right]dt + g(t)dW_t$$
where $u(x,t)$ is the control policy. The objective is to minimize:
$$J(u) = \mathbb{E}\left[\int_0^T \frac{1}{2}g(t)^2\|u(X_t, t)\|^2 dt + \Phi(X_T)\right]$$
where $\Phi(X_T) = -\log p_0(X_T)$ is the terminal cost encouraging samples to match the data distribution.

**HJB Equation Derivation**: The value function $V(x,t) = \inf_u J(u|X_t=x)$ satisfies the HJB equation:
$$-\frac{\partial V}{\partial t} = \inf_u \left\{f(x,t)^\top \nabla_x V + \frac{1}{2}g(t)^2 \text{tr}(\nabla^2_{xx} V) + g(t)^2 u^\top \nabla_x V + \frac{1}{2}g(t)^2\|u\|^2\right\}$$

Taking the first-order optimality condition yields the optimal control:
$$u^*(x,t) = -\nabla_x V(x,t)$$

Substituting back, we obtain:
$$-\frac{\partial V}{\partial t} = f(x,t)^\top \nabla_x V + \frac{1}{2}g(t)^2 \text{tr}(\nabla^2_{xx} V) - \frac{1}{2}g(t)^2\|\nabla_x V\|^2$$

**Key Theorem**: We establish that $V(x,t) = -\log p_{T-t}(x) + C(t)$, where $C(t)$ is a time-dependent constant. Consequently:
$$u^*(x,t) = -\nabla_x V(x,t) = \nabla_x \log p_{T-t}(x) = s_\theta(x, T-t)$$

This proves that the optimal controller equals the score function, providing a principled control-theoretic interpretation of score matching.

### 2.2 Control-Theoretic Training Objectives

**Policy Iteration Training**: Inspired by policy iteration in reinforcement learning, we propose an alternating optimization scheme:

1. **Policy Evaluation**: Given current policy $u_k$, compute the associated value function $V_k$ by solving:
$$-\frac{\partial V_k}{\partial t} = f^\top \nabla V_k + \frac{1}{2}g^2 \text{tr}(\nabla^2 V_k) + g^2 u_k^\top \nabla V_k + \frac{1}{2}g^2\|u_k\|^2$$

2. **Policy Improvement**: Update the policy as $u_{k+1}(x,t) = -\nabla_x V_k(x,t)$.

In practice, we parameterize both $u_\theta(x,t)$ and $V_\phi(x,t)$ with neural networks and minimize:
$$\mathcal{L}_{\text{PI}}(\theta, \phi) = \mathbb{E}_{t, x_t}\left[\left\|\frac{\partial V_\phi}{\partial t} + \mathcal{H}(x_t, \nabla V_\phi, \nabla^2 V_\phi, u_\theta)\right\|^2 + \lambda\|u_\theta + \nabla_x V_\phi\|^2\right]$$

where $\mathcal{H}$ is the Hamiltonian and $\lambda$ is a coupling coefficient.

**Temporal Difference Training**: We develop a TD-learning objective leveraging the Bellman equation structure:
$$\mathcal{L}_{\text{TD}}(\theta) = \mathbb{E}_{t, x_t, x_{t+\Delta t}}\left[\left(V_\phi(x_t, t) - \int_t^{t+\Delta t} c(x_s, u_\theta) ds - V_\phi(x_{t+\Delta t}, t+\Delta t)\right)^2\right]$$

where $c(x,u) = \frac{1}{2}g(t)^2\|u\|^2$ is the running cost. This objective provides lower-variance gradients compared to standard score matching in high-dimensional settings.

### 2.3 MPC-Based Accelerated Sampling

**Receding Horizon Control**: We design an adaptive sampler based on MPC principles. At each sampling step with state $x_t$, we solve a finite-horizon optimal control problem:
$$\min_{u_{t:t+H}} \mathbb{E}\left[\int_t^{t+H} c(x_s, u_s) ds + V_\phi(x_{t+H}, t+H)\right]$$

where $H$ is the prediction horizon and $V_\phi$ serves as the terminal value function approximation.

**Adaptive Step-Size Selection**: We propose an adaptive discretization scheme:
$$\Delta t_k = \min\left\{\Delta t_{\max}, \frac{\epsilon}{\|s_\theta(x_k, t_k)\| + \delta}\right\}$$

where $\epsilon$ is a tolerance parameter and $\delta$ prevents division by zero. This allocates computational resources to regions requiring fine-grained sampling (high score magnitude) while taking larger steps in simpler regions.

**Convergence Analysis**: We establish convergence guarantees under Lipschitz continuity assumptions on the score network. Specifically, if $\|s_\theta(x,t) - \nabla \log p_t(x)\| \leq \epsilon_s$ uniformly, then the sampling distribution $\hat{p}_0$ satisfies:
$$W_2(\hat{p}_0, p_0) \leq C_1 \epsilon_s + C_2 \sum_k \Delta t_k^2$$

where $W_2$ is the Wasserstein-2 distance and $C_1, C_2$ are constants depending on problem parameters.

### 2.4 Experimental Design

**Datasets and Benchmarks**: We evaluate on:
- **Synthetic**: Gaussian mixtures, Swiss roll, and checkerboard distributions
- **Image Generation**: CIFAR-10, CelebA-64, and ImageNet-64
- **Molecular Generation**: QM9 dataset for 3D molecule generation

**Baselines**: We compare against:
- Standard denoising score matching (DSM)
- DDPM and DDIM samplers
- DPM-Solver and related ODE-based accelerated samplers
- Recent control-theoretic approaches (Berner et al., 2024; Han et al., 2025)

**Evaluation Metrics**:
- **Sample Quality**: FID, IS (images); Validity, Uniqueness (molecules)
- **Sampling Efficiency**: Number of function evaluations (NFE) to reach target quality
- **Training Stability**: Gradient variance, loss convergence curves
- **Distribution Matching**: KL divergence, Wasserstein distance (synthetic data)

**Ablation Studies**:
1. Impact of prediction horizon $H$ in MPC sampling
2. Comparison of policy iteration vs. TD training objectives
3. Adaptive vs. fixed step-size selection
4. Sensitivity to score estimation errors

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Theoretical Contributions**:
- A rigorous mathematical framework establishing the equivalence between optimal feedback controllers and score functions via HJB theory
- Formal convergence rates for MPC-based diffusion samplers under standard regularity assumptions
- Characterization of the relationship between control cost functionals and training objectives

**Algorithmic Contributions**:
- Novel policy iteration and TD-learning training algorithms with potentially improved gradient properties
- Adaptive MPC-based sampling achieving 2-5× reduction in function evaluations while maintaining sample quality
- Robust training procedures leveraging $H_\infty$ control principles for distribution shift resilience

**Empirical Results**:
- Demonstration of faster convergence during training compared to standard score matching
- State-of-the-art sampling efficiency on benchmark image and molecular generation tasks
- Improved robustness to out-of-distribution inputs and model misspecification

### Broader Impact

This research contributes to multiple communities:

**Machine Learning**: Provides principled alternatives to heuristic sampling schedules and training procedures, potentially improving diffusion models across all application domains.

**Control Theory**: Demonstrates the applicability of classical control techniques to modern generative AI problems, revitalizing interest in HJB-based methods through neural network approximations.

**Interdisciplinary Research**: Strengthens the bridge between learning and control, enabling researchers from both fields to leverage complementary tools and perspectives.

**Practical Applications**: Faster sampling enables real-time applications of diffusion models in robotics, autonomous systems, and interactive content generation, while formal guarantees support deployment in safety-critical domains.

### Limitations and Future Directions

We acknowledge potential limitations: the computational overhead of MPC at sampling time may offset efficiency gains in some settings, and the value function approximation introduces additional complexity. Future work will explore connections to mean-field games for multi-agent settings, risk-sensitive control formulations for uncertainty quantification, and extensions to discrete diffusion models through hybrid optimal control theory.