# Research Proposal: Unifying Diffusion Models and Optimal Control: Score Matching as Hamilton-Jacobi-Bellman Optimality

## 1. Introduction

### 1.1 Background

Diffusion models have emerged as the dominant paradigm in generative modeling, achieving state-of-the-art performance across diverse domains including image synthesis, audio generation, and molecular design. These models operate by learning to reverse a gradual noising process: starting from data, a forward stochastic differential equation (SDE) progressively corrupts samples into pure noise, while a learned reverse-time SDE reconstructs data from noise. The training objective—denoising score matching (DSM)—asks neural networks to estimate the score function $\nabla \log p(x,t)$ at each noise level. Despite remarkable empirical success, with models like DALL-E, Stable Diffusion, and Imagen revolutionizing creative AI, the theoretical foundations explaining *why* score matching works so effectively remain incomplete.

Separately, stochastic optimal control (SOC) theory provides a rigorous mathematical framework for sequential decision-making under uncertainty. The Hamilton-Jacobi-Bellman (HJB) equation characterizes optimal policies through the value function $V(x,t)$, which satisfies a nonlinear partial differential equation encoding the principle of optimality. Control theory has deep connections to physics, economics, and reinforcement learning, offering principled tools for analyzing dynamical systems.

Recent work has begun exploring connections between these fields. Song et al. (2020) unified score-based models under an SDE framework, while Domingo-Enrich et al. (2024) formulated diffusion sampling as stochastic optimal control. Huang et al. (2021) derived score matching from variational principles. However, a fundamental question remains unanswered: **Is there a deep mathematical equivalence between denoising score matching and HJB optimality conditions?**

### 1.2 Research Objectives

This research aims to establish a rigorous mathematical unification between diffusion models and stochastic optimal control theory. Our specific objectives are:

1. **Theoretical Unification**: Prove that denoising score matching objectives are mathematically equivalent to HJB optimality conditions when the log-probability density is identified as the negative value function.

2. **Mechanistic Understanding**: Establish the precise causal chain connecting log-probability identification, score-control correspondence, and loss function equivalence.

3. **Algorithmic Innovation**: Develop and validate control-theoretic training modifications inspired by temporal difference (TD) learning that improve convergence efficiency.

4. **Framework Synthesis**: Demonstrate that both probabilistic (ELBO) and control-theoretic (SOC) perspectives emerge as special cases of the unified HJB framework.

### 1.3 Significance

This research addresses a fundamental gap in our understanding of generative models. By establishing score matching as HJB optimality, we provide:

- **Theoretical Justification**: A principled explanation for why score matching succeeds, moving beyond empirical observation to mathematical necessity.
- **Design Principles**: Control-theoretic insights for designing improved training objectives, noise schedules, and sampling algorithms.
- **Cross-Disciplinary Bridge**: A unified language connecting machine learning, control theory, and stochastic analysis communities.
- **Practical Improvements**: Concrete algorithmic modifications with potential for faster training and better sample quality.

---

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Diffusion Model Preliminaries

Consider a forward SDE that transforms data distribution $p_0(x)$ into a tractable prior $p_T(x) \approx \mathcal{N}(0, \sigma_T^2 I)$:

$$dx = f(x,t)dt + g(t)dW_t$$

where $f(x,t)$ is the drift coefficient, $g(t)$ is the diffusion coefficient, and $W_t$ is a standard Wiener process. The marginal density $p(x,t)$ evolves according to the Fokker-Planck equation:

$$\frac{\partial p}{\partial t} = -\nabla \cdot (fp) + \frac{g^2}{2}\Delta p$$

The reverse-time SDE, which generates samples, takes the form:

$$dx = \left[f(x,t) - g(t)^2 \nabla \log p(x,t)\right]dt + g(t)d\bar{W}_t$$

where $\bar{W}_t$ is a reverse-time Wiener process. The score function $s(x,t) = \nabla \log p(x,t)$ is the critical quantity that must be learned.

#### 2.1.2 Stochastic Optimal Control Formulation

We formulate the reverse-time generation process as a stochastic optimal control problem. Consider the controlled SDE:

$$dx = \left[f(x,t) + g(t)^2 u(x,t)\right]dt + g(t)d\bar{W}_t$$

where $u(x,t)$ is the control policy. The objective is to minimize the expected cost:

$$J[u] = \mathbb{E}\left[\int_0^T \frac{g(t)^2}{2}\|u(x_t,t)\|^2 dt + \Phi(x_T)\right]$$

where $\Phi(x_T)$ is the terminal cost encoding the target distribution.

The value function $V(x,t)$ satisfies the HJB equation:

$$-\frac{\partial V}{\partial t} = \min_u \left\{(f + g^2 u)^\top \nabla V + \frac{g^2}{2}\Delta V + \frac{g^2}{2}\|u\|^2\right\}$$

#### 2.1.3 Core Equivalence Derivation

**Step 1: Log-Probability as Negative Value Function**

We propose the identification:
$$V(x,t) = -\log p(x,t) + C(t)$$

where $C(t)$ is a time-dependent normalization constant.

**Step 2: Score Function as Optimal Control**

Taking gradients of the identification:
$$\nabla V(x,t) = -\nabla \log p(x,t) = -s(x,t)$$

The optimal control from HJB first-order conditions is:
$$u^*(x,t) = -\nabla V(x,t) = s(x,t)$$

This establishes that the score function IS the optimal control signal.

**Step 3: HJB Residual Equals Score Matching Loss**

Substituting $u^* = -\nabla V$ into the HJB equation and using $V = -\log p$:

$$\frac{\partial \log p}{\partial t} = f^\top \nabla \log p + \frac{g^2}{2}\Delta \log p + \frac{g^2}{2}\|\nabla \log p\|^2$$

This is precisely the backward Kolmogorov equation for log-densities. The HJB residual for a parameterized approximation $s_\theta$ becomes:

$$\mathcal{R}_{\text{HJB}}(x,t;\theta) = \left\|s_\theta(x,t) - \nabla \log p(x,t)\right\|^2$$

which equals the denoising score matching objective up to weighting factors.

### 2.2 Experimental Design

#### 2.2.1 Phase 1: Mathematical Validation on Tractable Distributions

**Objective**: Verify the theoretical equivalence on distributions where both DSM loss and HJB residual are analytically computable.

**Setup**:
- **Distributions**: 1D and 2D Gaussian mixtures, Ornstein-Uhlenbeck processes
- **SDE Types**: VP-SDE with $f(x,t) = -\frac{1}{2}\beta(t)x$, $g(t) = \sqrt{\beta(t)}$; VE-SDE with $f(x,t) = 0$, $g(t) = \sqrt{\frac{d[\sigma^2(t)]}{dt}}$

**Procedure**:
1. Compute analytical score functions $\nabla \log p(x,t)$ for Gaussian mixtures under forward diffusion
2. Evaluate DSM loss: $\mathcal{L}_{\text{DSM}} = \mathbb{E}_{t,x_0,\epsilon}\left[\|s_\theta(x_t,t) - \nabla \log p(x_t|x_0)\|^2\right]$
3. Evaluate HJB residual: $\mathcal{R}_{\text{HJB}} = \mathbb{E}_{t,x}\left[\left\|s_\theta + \nabla V_{\text{true}}\right\|^2\right]$
4. Compute Pearson correlation between losses across 1000 noise levels $t \in [0,T]$

**Success Criterion**: Correlation $r > 0.99$ between DSM loss and HJB residual.

#### 2.2.2 Phase 2: Numerical Verification on Standard Benchmarks

**Objective**: Validate that the theoretical equivalence holds in practical high-dimensional settings.

**Datasets**:
- CIFAR-10 (32×32×3 images, 50K training samples)
- CelebA-HQ 64×64 (30K images)

**Architecture**: Standard U-Net following Song et al. (2020) with:
- 128 base channels, channel multipliers [1, 2, 2, 2]
- Self-attention at 16×16 resolution
- GroupNorm, SiLU activations

**Procedure**:
1. Train score networks using standard DSM objective
2. At checkpoints, estimate HJB residual via Monte Carlo sampling
3. Compare loss landscapes and gradient directions

**Metrics**:
- Gradient alignment: $\cos(\nabla_\theta \mathcal{L}_{\text{DSM}}, \nabla_\theta \mathcal{R}_{\text{HJB}})$
- Loss correlation across training iterations

#### 2.2.3 Phase 3: Control-Theoretic Training Modifications

**Objective**: Test whether TD-inspired modifications improve training efficiency.

**Proposed Modifications**:

1. **TD-Style Bootstrapping**: Replace full denoising targets with bootstrapped estimates:
$$\mathcal{L}_{\text{TD}} = \mathbb{E}\left[\|s_\theta(x_t,t) - \text{sg}[s_\theta(x_{t-\delta},t-\delta) + \text{correction}]\|^2\right]$$
where $\text{sg}[\cdot]$ denotes stop-gradient.

2. **Eligibility Traces**: Incorporate multi-step returns:
$$\mathcal{L}_{\lambda} = (1-\lambda)\sum_{n=1}^{\infty}\lambda^{n-1}\mathcal{L}^{(n)}$$

3. **Value Function Regularization**: Add HJB consistency penalty:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{DSM}} + \alpha \mathcal{R}_{\text{HJB-approx}}$$

**Experimental Protocol**:
- 25 independent runs per method (different random seeds)
- Training budget: 500K iterations on CIFAR-10
- Learning rate: 2e-4 with linear warmup and cosine decay
- Batch size: 128
- EMA decay: 0.9999

**Evaluation Metrics**:
- **Convergence Speed**: Iterations to reach 90% of final FID
- **Final Quality**: FID-50K, Inception Score
- **Training Stability**: Loss variance across runs

**Statistical Analysis**:
- Paired t-test comparing convergence iterations (same seeds)
- Effect size: Cohen's d with 95% confidence intervals
- Significance threshold: $\alpha = 0.05$ (one-tailed)

#### 2.2.4 Phase 4: Framework Unification Validation

**Objective**: Demonstrate that ELBO and SOC perspectives are special cases of HJB framework.

**Approach**:
1. **ELBO Recovery**: Show that choosing terminal cost $\Phi(x_T) = -\log p_{\text{prior}}(x_T)$ and running cost proportional to KL divergence recovers the variational lower bound.

2. **Adjoint Matching Recovery**: Demonstrate that the adjoint equations from Domingo-Enrich et al. (2024) emerge from HJB optimality conditions with specific boundary conditions.

**Validation**: Mathematical derivation with explicit assumption mapping between frameworks.

### 2.3 Implementation Details

**Software Stack**:
- PyTorch 2.0+ with torch.compile optimization
- JAX/Flax for automatic differentiation of HJB residuals
- Weights & Biases for experiment tracking

**Computational Resources**:
- Phase 1-2: 4× NVIDIA A100 GPUs
- Phase 3: 8× A100 GPUs for parallel seed runs
- Estimated compute: ~2000 GPU-hours total

**Code Availability**: All code will be released under MIT license with reproducibility scripts.

---

## 3. Expected Outcomes & Impact

### 3.1 Theoretical Contributions

1. **Formal Equivalence Theorem**: A rigorous mathematical proof establishing that denoising score matching is equivalent to HJB optimality under specified regularity conditions (bounded score, Lipschitz densities).

2. **Unified Framework**: A comprehensive theoretical framework subsuming both probabilistic (ELBO) and control-theoretic (SOC) perspectives as special cases.

3. **Approximation Bounds**: Quantitative analysis of the gap between infinite-capacity HJB optimality and finite-network training, providing guidance for architecture design.

### 3.2 Algorithmic Contributions

1. **TD-Inspired Training**: Novel training objectives leveraging temporal difference ideas, with expected 10-20% faster convergence to equivalent sample quality.

2. **HJB-Regularized Training**: A principled regularization scheme enforcing HJB consistency, potentially improving training stability.

3. **Noise Schedule Design**: Control-theoretic principles for optimal noise schedule selection based on value function smoothness.

### 3.3 Expected Quantitative Results

| Experiment | Metric | Baseline | Expected Improvement |
|------------|--------|----------|---------------------|
| Toy Problems | DSM-HJB Correlation | N/A | $r > 0.99$ |
| CIFAR-10 Convergence | Iterations to FID < 10 | 400K | 320K-360K (10-20% faster) |
| CIFAR-10 Final FID | FID-50K | 2.5 | 2.3-2.5 (maintained or improved) |
| Training Stability | Loss Std Dev | 0.15 | < 0.12 |

### 3.4 Broader Impact

**Scientific Impact**:
- Establishes a new theoretical foundation for understanding generative models
- Opens pathways for importing decades of control theory results into machine learning
- Provides a unified language for cross-disciplinary collaboration

**Practical Impact**:
- More efficient training of large-scale diffusion models, reducing computational costs
- Principled design guidelines for practitioners developing new generative architectures
- Potential applications in scientific domains (drug discovery, materials science) where theoretical guarantees matter

**Community Impact**:
- Bridges the gap between the machine learning, control theory, and stochastic analysis communities
- Provides educational materials connecting these traditionally separate fields
- Releases open-source implementations enabling reproducibility and extension

### 3.5 Limitations and Future Directions

**Known Limitations**:
- Regularity conditions may not hold at distribution boundaries
- Discrete-time training introduces approximation gaps from continuous-time theory
- Computational overhead of HJB residual evaluation may limit practical applicability

**Future Directions**:
- Extension to discrete diffusion models and non-Markovian processes
- Application to reinforcement learning via diffusion policies
- Development of adaptive algorithms that automatically tune control-theoretic hyperparameters

---

## 4. Conclusion

This research proposal presents a systematic investigation into the mathematical equivalence between denoising score matching and Hamilton-Jacobi-Bellman optimality. By establishing that score functions are optimal control signals and that training objectives emerge from HJB conditions, we provide both theoretical justification for existing methods and principled pathways for algorithmic innovation. The proposed methodology combines rigorous mathematical derivation with comprehensive empirical validation, ensuring that theoretical insights translate into practical improvements. Success in this research will fundamentally advance our understanding of diffusion models while opening new frontiers at the intersection of machine learning, control theory, and dynamical systems.