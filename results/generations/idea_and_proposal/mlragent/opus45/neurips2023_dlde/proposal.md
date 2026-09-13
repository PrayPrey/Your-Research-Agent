# Research Proposal: Adaptive Neural ODE Solvers via Meta-Learned Step Size Controllers

## 1. Introduction

### Background

Neural Ordinary Differential Equations (Neural ODEs) have emerged as a transformative paradigm in deep learning, enabling continuous-depth networks that elegantly bridge classical dynamical systems theory with modern machine learning. Since their introduction by Chen et al. (2018), Neural ODEs have found applications across diverse domains including time-series modeling, generative modeling through continuous normalizing flows, and physics-informed machine learning. The continuous nature of these models offers theoretical advantages such as memory efficiency through adjoint sensitivity methods and principled handling of irregularly-sampled data.

However, the practical deployment of Neural ODEs remains fundamentally constrained by the computational cost of numerical integration. Each forward pass requires solving an initial value problem, and each backward pass for gradient computation demands either solving an augmented ODE system or storing intermediate states. The efficiency of these operations depends critically on the step size selection strategy employed by the numerical solver. Traditional adaptive step size controllers, such as the proportional-integral (PI) and proportional-integral-derivative (PID) controllers used in methods like Dormand-Prince (DOPRI5), were designed for general-purpose scientific computing applications. These controllers rely on hand-crafted heuristics that estimate local truncation error and adjust step sizes accordingly.

The fundamental limitation of classical controllers is their agnosticism to the specific characteristics of learned neural dynamics. Neural ODEs exhibit distinctive properties: their dynamics evolve during training, they often contain regions of varying smoothness, and they may develop stiffness patterns that differ substantially from those encountered in traditional scientific computing. Recent work has highlighted these challenges—Caldana and Hesthaven (2024) demonstrated that stiffness poses particular difficulties for neural ODE inference, while Finlay et al. (2020) showed that regularization can encourage simpler dynamics that are easier to integrate. Despite these advances, the core step size control mechanism remains unchanged from classical numerical analysis.

### Research Objectives

This proposal introduces **MetaStep**, a meta-learned step size controller designed to replace traditional error-based controllers in adaptive ODE solvers for Neural ODEs. Our primary objectives are:

1. **Develop a neural step size controller** that learns to predict optimal step sizes by observing local solution features, error estimates, and integration history.

2. **Create a diverse meta-training framework** that exposes the controller to varied Neural ODE tasks spanning different stiffness regimes, architectural choices, and application domains.

3. **Establish theoretical foundations** connecting learned control policies to classical stability analysis, providing guarantees on accuracy and stability.

4. **Demonstrate practical efficiency gains** through comprehensive empirical evaluation across benchmark tasks, targeting 30-50% reduction in neural function evaluations (NFEs) while maintaining accuracy.

### Significance

This research addresses a critical bottleneck in Neural ODE deployment. Reduced NFEs translate directly to faster training times and lower inference latency—crucial for real-time applications in robotics control, online time-series forecasting, and edge deployment. Unlike architecture-specific optimizations, a learned step size controller offers plug-and-play compatibility with existing Neural ODE models, maximizing practical impact. Furthermore, this work exemplifies the bidirectional exchange between differential equations and deep learning: we use machine learning to improve numerical methods that themselves underpin a class of deep learning models.

## 2. Methodology

### 2.1 Problem Formulation

Consider a Neural ODE defined by the initial value problem:

$$\frac{d\mathbf{z}}{dt} = f_\theta(\mathbf{z}(t), t), \quad \mathbf{z}(t_0) = \mathbf{z}_0$$

where $f_\theta: \mathbb{R}^d \times \mathbb{R} \to \mathbb{R}^d$ is a neural network parameterized by $\theta$. Numerical integration proceeds by computing a sequence of states $\{\mathbf{z}_n\}$ at times $\{t_n\}$, where $t_{n+1} = t_n + h_n$ and $h_n$ is the step size chosen at step $n$.

Traditional adaptive controllers determine $h_{n+1}$ based on an error estimate $\epsilon_n$:

$$h_{n+1} = h_n \cdot \min\left(\alpha_{\max}, \max\left(\alpha_{\min}, \alpha \cdot \left(\frac{\tau}{\epsilon_n}\right)^{1/(p+1)}\right)\right)$$

where $\tau$ is the error tolerance, $p$ is the method order, and $\alpha, \alpha_{\min}, \alpha_{\max}$ are safety factors. Our goal is to replace this heuristic with a learned controller $\pi_\phi$ parameterized by $\phi$:

$$h_{n+1} = \pi_\phi(\mathbf{s}_n)$$

where $\mathbf{s}_n$ is a state representation encoding relevant information about the integration process.

### 2.2 Controller Architecture

The MetaStep controller $\pi_\phi$ is a lightweight neural network (approximately 50K parameters) that processes a feature vector $\mathbf{s}_n$ constructed from:

**Local Features:**
- Current error estimate: $\epsilon_n \in \mathbb{R}$
- Estimated local Lipschitz constant: $\hat{L}_n = \|f_\theta(\mathbf{z}_n + \delta, t_n) - f_\theta(\mathbf{z}_n, t_n)\| / \|\delta\|$
- Dynamics magnitude: $\|f_\theta(\mathbf{z}_n, t_n)\|$
- Jacobian spectral radius approximation: $\hat{\rho}_n$ (via power iteration)

**History Features:**
- Recent step sizes: $(h_{n-1}, h_{n-2}, h_{n-3})$
- Recent error ratios: $(\epsilon_{n-1}/\tau, \epsilon_{n-2}/\tau)$
- Step acceptance history: binary indicators for last 5 steps

**Global Context:**
- Remaining integration interval: $T - t_n$
- Problem dimension: $d$ (embedded)
- Current time fraction: $t_n / T$

The feature vector $\mathbf{s}_n \in \mathbb{R}^{20}$ is processed through a 3-layer MLP with 128 hidden units and ReLU activations, outputting a step size multiplier $\mu_n \in [\mu_{\min}, \mu_{\max}]$:

$$\mu_n = \mu_{\min} + (\mu_{\max} - \mu_{\min}) \cdot \sigma(\text{MLP}_\phi(\mathbf{s}_n))$$

$$h_{n+1} = \mu_n \cdot h_n^{\text{PI}}$$

where $h_n^{\text{PI}}$ is the step size suggested by a baseline PI controller and $\sigma$ is the sigmoid function. This multiplicative formulation ensures stability by anchoring predictions to a reasonable baseline while allowing the learned controller to modulate aggressively when beneficial.

### 2.3 Meta-Training Framework

#### Task Distribution

We construct a diverse meta-training distribution $\mathcal{T}$ comprising:

1. **Synthetic Neural ODEs**: Networks with varied architectures (MLP depths 2-6, widths 32-256, activation functions) initialized randomly and partially trained on synthetic regression targets.

2. **Stiffness-Controlled Systems**: Neural ODEs trained to approximate known stiff systems (Van der Pol, Robertson chemical kinetics) at varying stiffness parameters.

3. **Real-World Inspired Tasks**: Neural ODEs trained on subsets of benchmark datasets (Walker2D dynamics, PhysioNet time-series, FFJORD density estimation).

4. **Multi-Scale Dynamics**: Systems combining slow and fast timescales to stress-test adaptive behavior.

Each task $\mathcal{T}_i$ specifies a Neural ODE $f_{\theta_i}$, integration interval $[0, T_i]$, initial condition distribution $p(\mathbf{z}_0^{(i)})$, and accuracy tolerance $\tau_i$.

#### Reinforcement Learning Training

We formulate controller training as a reinforcement learning problem. At each integration step $n$, the controller observes state $\mathbf{s}_n$, selects action $h_{n+1}$, and receives reward:

$$r_n = -c_{\text{NFE}} - c_{\text{reject}} \cdot \mathbf{1}[\text{step rejected}] - c_{\text{error}} \cdot \max(0, \epsilon_n - \tau)^2$$

where $c_{\text{NFE}}$, $c_{\text{reject}}$, and $c_{\text{error}}$ are cost coefficients balancing efficiency against accuracy. The objective is to maximize expected cumulative reward across the task distribution:

$$\max_\phi \mathbb{E}_{\mathcal{T}_i \sim \mathcal{T}} \mathbb{E}_{\mathbf{z}_0 \sim p(\mathbf{z}_0^{(i)})} \left[ \sum_{n=0}^{N-1} r_n \right]$$

We employ Proximal Policy Optimization (PPO) with the following modifications for our setting:
- **Curriculum learning**: Begin with simple, non-stiff tasks and progressively introduce harder problems.
- **Task batching**: Each PPO update uses trajectories from 32 different tasks to encourage generalization.
- **Error constraint enforcement**: Augment rewards with a Lagrangian penalty for constraint violations, with adaptive dual variables.

### 2.4 Theoretical Analysis

We provide theoretical grounding by analyzing the learned controller's behavior through the lens of classical stability theory.

**Definition (Admissible Controller)**: A step size controller $\pi$ is $(\tau, \delta)$-admissible for a class of problems $\mathcal{F}$ if for all $f \in \mathcal{F}$, the global error satisfies $\|\mathbf{z}(T) - \mathbf{z}_N\| \leq \tau$ with probability at least $1 - \delta$.

**Theorem 1 (Stability Preservation)**: If $\pi_\phi$ satisfies $h_n \leq 2/\hat{L}_n$ for all steps where $\hat{L}_n$ is within factor $\gamma$ of the true local Lipschitz constant, then explicit Euler integration remains stable.

We extend this to higher-order methods by analyzing the learned controller's implicit approximation of stability region boundaries. Empirically, we verify that MetaStep learns to respect stability constraints by visualizing step size decisions in the complex plane relative to method stability regions.

### 2.5 Experimental Design

#### Baselines
- **DOPRI5-PI**: Standard Dormand-Prince with PI controller
- **DOPRI5-PID**: Enhanced PID controller variant
- **TL-NODE**: Taylor-Lagrange Neural ODE (Djeumou et al., 2022)
- **Fixed-Step RK4**: Fixed step size fourth-order Runge-Kutta

#### Benchmark Tasks

1. **Continuous Normalizing Flows**: FFJORD on MNIST, CIFAR-10 density estimation
2. **Time-Series Modeling**: Latent ODE on PhysioNet mortality prediction, MuJoCo dynamics
3. **Physics-Informed Tasks**: Learning Lorenz attractor, double pendulum dynamics
4. **Stiff Systems**: Neural ODEs approximating chemical reaction networks

#### Evaluation Metrics

- **NFE Efficiency**: Total neural function evaluations for fixed accuracy
- **Wall-Clock Time**: End-to-end training and inference time
- **Accuracy**: Final integration error $\|\mathbf{z}(T) - \mathbf{z}_N\|$
- **Rejection Rate**: Fraction of proposed steps rejected
- **Generalization Gap**: Performance difference between meta-training and held-out tasks

#### Ablation Studies

1. Controller architecture (MLP depth, feature selection)
2. Meta-training task diversity
3. Reward function design
4. Baseline anchoring strategy

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Efficiency Gains**: We anticipate 30-50% reduction in NFEs across benchmark tasks, with larger gains (up to 60%) for stiff or multi-scale systems where classical controllers are particularly suboptimal. For continuous normalizing flows on CIFAR-10, we expect training time reduction from approximately 72 hours to under 45 hours on equivalent hardware.

2. **Generalization**: MetaStep should generalize to held-out Neural ODE architectures and problem domains not seen during meta-training, demonstrating that learned patterns in optimal step size selection transfer across tasks.

3. **Theoretical Insights**: Analysis of learned policies will reveal what features are most predictive of optimal step sizes, potentially informing improved hand-crafted controllers for settings where learned controllers are impractical.

4. **Open-Source Release**: We will release MetaStep as a drop-in replacement for standard ODE solvers in PyTorch and JAX ecosystems, with pre-trained controller weights.

### Broader Impact

**Computational Sustainability**: By reducing the computational cost of Neural ODEs, MetaStep contributes to more environmentally sustainable AI development. Large-scale Neural ODE training can require significant energy; efficiency improvements directly translate to reduced carbon footprint.

**Democratization**: Lower computational requirements make Neural ODEs accessible to researchers without access to extensive computing resources, broadening participation in this research area.

**Real-Time Applications**: Faster inference enables deployment of Neural ODEs in latency-critical applications—autonomous vehicles, real-time medical monitoring, and interactive robotics—where current methods are often too slow.

**Cross-Disciplinary Bridge**: This work exemplifies productive synthesis between numerical analysis and machine learning, potentially inspiring similar approaches for other numerical methods (linear solvers, optimization algorithms, PDE discretizations).

### Limitations and Future Work

We acknowledge that meta-learned controllers require upfront training investment and may not outperform specialized hand-tuned controllers for narrow problem classes. Future work will explore online adaptation of controller weights during deployment, extension to implicit solvers for stiff systems, and application to adjoint sensitivity computation for more efficient backward passes.

In conclusion, MetaStep represents a principled approach to improving Neural ODE efficiency by learning step size control strategies that respect the unique characteristics of neural dynamics. By combining meta-learning with numerical analysis insights, we aim to deliver practical speedups while maintaining the theoretical foundations that make Neural ODEs valuable.