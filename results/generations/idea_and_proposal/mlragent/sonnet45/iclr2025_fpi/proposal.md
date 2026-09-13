# Research Proposal: Adaptive Variance Reduction for Learned MCMC Samplers via Meta-Learned Control Variates

## 1. Title

**Adaptive Variance Reduction for Learned MCMC Samplers via Meta-Learned Control Variates: A Bi-Level Optimization Framework for Reliable Probabilistic Inference**

## 2. Introduction

### Background

Markov Chain Monte Carlo (MCMC) methods remain fundamental tools for sampling from complex, unnormalized probability distributions in applications ranging from Bayesian inference to molecular dynamics simulations. Recent advances in deep learning have sparked significant interest in learned samplers—neural network-based approaches that learn transition kernels, proposals, or transport maps to accelerate sampling convergence. These methods, including neural transport operators, normalizing flows, and learned Hamiltonian Monte Carlo variants, have demonstrated impressive convergence speedups on specific benchmark problems.

However, a critical limitation impedes their widespread adoption in high-stakes scientific applications: **high variance in expectation estimates**. While learned samplers may achieve rapid mixing and fast convergence in distribution, the estimators derived from their samples often exhibit variance significantly higher than classical methods. This variance instability makes them unreliable for uncertainty quantification in critical domains such as drug discovery, climate modeling, and engineering design, where precise credible intervals and risk assessments are essential.

Classical variance reduction techniques—including control variates, Rao-Blackwellization, and antithetic sampling—have been successfully applied to traditional MCMC methods for decades. Control variates, in particular, exploit known expectations of correlated random variables to reduce estimator variance. However, these techniques have seen limited integration with modern learned samplers for two primary reasons: (1) they typically require problem-specific analytical derivations, and (2) the optimal control variate functions may differ substantially across the distribution of tasks encountered during meta-training.

### Research Objectives

This research proposes a novel **meta-learning framework for adaptive variance reduction** that jointly optimizes:

1. A neural sampler (parameterized transition kernel or transport operator)
2. A control variate network that learns optimal variance reduction functions across a distribution of sampling tasks

Our specific objectives are:

- **Objective 1**: Develop a bi-level optimization framework that simultaneously learns sampling efficiency and variance reduction in the outer and inner loops respectively
- **Objective 2**: Design neural architectures for control variate networks that can generalize across related sampling tasks while adapting to task-specific statistics
- **Objective 3**: Establish theoretical convergence guarantees for the joint optimization procedure and derive variance reduction bounds
- **Objective 4**: Validate the framework on challenging applications in Bayesian inverse problems and molecular dynamics simulations, demonstrating 2-5× variance reduction compared to vanilla learned samplers

### Significance

This research addresses a critical gap at the intersection of classical statistical methods and modern machine learning for sampling. The significance of this work includes:

**Theoretical Impact**: We bridge variance reduction theory from classical statistics with representation learning, providing new theoretical insights into how neural networks can learn optimal control variates. This connection opens avenues for principled design of variance-aware learned samplers.

**Practical Impact**: By reducing variance while maintaining sampling efficiency, our framework enables deployment of learned samplers in high-stakes scientific applications where reliability is paramount. This is particularly crucial for inverse problems in medical imaging, uncertainty quantification in climate models, and rare event simulation in molecular dynamics.

**Methodological Impact**: The meta-learning framework for control variates represents a paradigm shift from problem-specific variance reduction to learned, adaptive strategies that transfer across related tasks. This approach aligns with the workshop's focus on "learning meets sampling" and addresses the challenge of making learned samplers practically viable.

## 3. Methodology

### 3.1 Problem Formulation

Let $\pi(\mathbf{x}) \propto \exp(-U(\mathbf{x}))$ denote an unnormalized target distribution over $\mathbf{x} \in \mathcal{X} \subseteq \mathbb{R}^d$, where $U(\mathbf{x})$ is the energy function. Our goal is to estimate expectations:

$$\mathbb{E}_{\pi}[f(\mathbf{x})] = \int f(\mathbf{x})\pi(\mathbf{x})d\mathbf{x}$$

for various test functions $f: \mathcal{X} \rightarrow \mathbb{R}$.

**Standard MCMC Estimator**: Given samples $\{\mathbf{x}_i\}_{i=1}^N$ from a Markov chain with stationary distribution $\pi$, the standard estimator is:

$$\hat{\mu}_f = \frac{1}{N}\sum_{i=1}^N f(\mathbf{x}_i)$$

with asymptotic variance $\sigma^2_f/N$ where $\sigma^2_f = \text{Var}_{\pi}(f) + 2\sum_{k=1}^{\infty}\text{Cov}(f(\mathbf{x}_0), f(\mathbf{x}_k))$.

**Control Variate Estimator**: For a control variate $g(\mathbf{x})$ with known expectation $\mathbb{E}_{\pi}[g(\mathbf{x})] = \mu_g$, the control variate estimator is:

$$\hat{\mu}_f^{\text{CV}} = \frac{1}{N}\sum_{i=1}^N \left[f(\mathbf{x}_i) - \alpha(g(\mathbf{x}_i) - \mu_g)\right]$$

where the optimal coefficient $\alpha^* = \text{Cov}_{\pi}(f,g)/\text{Var}_{\pi}(g)$ minimizes variance.

### 3.2 Meta-Learning Framework Architecture

#### 3.2.1 Neural Sampler Component

We parameterize the learned sampler using a neural transition kernel $T_{\theta}: \mathcal{X} \times \mathcal{X} \rightarrow \mathbb{R}_+$ with parameters $\theta$. For concreteness, we consider a learned Langevin dynamics formulation:

$$\mathbf{x}_{t+1} = \mathbf{x}_t - \epsilon \nabla U(\mathbf{x}_t) + \epsilon S_{\theta}(\mathbf{x}_t, U) + \sqrt{2\epsilon}\boldsymbol{\xi}_t$$

where $S_{\theta}$ is a neural network that learns corrective score functions, and $\boldsymbol{\xi}_t \sim \mathcal{N}(0, \mathbf{I})$.

#### 3.2.2 Control Variate Network

The control variate network $g_{\phi}: \mathcal{X} \times \mathcal{U} \rightarrow \mathbb{R}$ takes as input a state $\mathbf{x}$ and task embedding $\mathbf{z} \in \mathcal{U}$ (encoding the energy function $U$), producing a control variate function. The network architecture consists of:

1. **Task Encoder**: $\text{Enc}_{\psi}: U \rightarrow \mathbf{z} \in \mathbb{R}^{d_z}$ that embeds the target distribution
2. **State Processor**: Deep set or graph neural network for permutation invariance
3. **Control Variate Head**: Outputs $g_{\phi}(\mathbf{x}, \mathbf{z})$ with guaranteed zero mean via architectural constraints

To ensure $\mathbb{E}_{\pi}[g_{\phi}(\mathbf{x}, \mathbf{z})] = 0$, we use the parameterization:

$$g_{\phi}(\mathbf{x}, \mathbf{z}) = h_{\phi}(\mathbf{x}, \mathbf{z}) - \frac{1}{K}\sum_{j=1}^K h_{\phi}(\mathbf{x}_j^{\text{ref}}, \mathbf{z})$$

where $\{\mathbf{x}_j^{\text{ref}}\}$ are reference samples from $\pi$ maintained in a buffer.

### 3.3 Bi-Level Optimization Procedure

#### 3.3.1 Task Distribution

We consider a distribution over sampling tasks $p(\mathcal{T})$, where each task $\mathcal{T} = (U, \{f_k\}_{k=1}^{K_f})$ consists of an energy function and a set of test functions.

#### 3.3.2 Inner Loop: Task-Specific Adaptation

For a given task $\mathcal{T}$, the inner loop optimizes sampling trajectories to minimize:

$$\mathcal{L}_{\text{inner}}(\theta, \phi; \mathcal{T}) = \mathcal{L}_{\text{sampling}}(\theta; \mathcal{T}) + \lambda_{\text{var}}\mathcal{L}_{\text{variance}}(\theta, \phi; \mathcal{T})$$

where:

**Sampling Loss** (KL divergence minimization via score matching):
$$\mathcal{L}_{\text{sampling}}(\theta; \mathcal{T}) = \mathbb{E}_{\mathbf{x} \sim q_{\theta}}\left[\|\nabla\log q_{\theta}(\mathbf{x}) - \nabla\log\pi(\mathbf{x})\|^2\right]$$

**Variance Loss**:
$$\mathcal{L}_{\text{variance}}(\theta, \phi; \mathcal{T}) = \sum_{k=1}^{K_f} \text{Var}_{q_{\theta}}\left[f_k(\mathbf{x}) - \alpha_k g_{\phi}(\mathbf{x}, \mathbf{z})\right]$$

The optimal coefficient $\alpha_k$ is computed as:
$$\alpha_k = \frac{\sum_{i=1}^N f_k(\mathbf{x}_i)g_{\phi}(\mathbf{x}_i, \mathbf{z})}{\sum_{i=1}^N g_{\phi}(\mathbf{x}_i, \mathbf{z})^2}$$

#### 3.3.3 Outer Loop: Meta-Optimization

The outer loop optimizes control variate parameters across the task distribution:

$$\min_{\phi, \psi} \mathbb{E}_{\mathcal{T} \sim p(\mathcal{T})}\left[\mathcal{L}_{\text{meta}}(\phi, \psi, \theta^*(\mathcal{T}); \mathcal{T})\right]$$

where $\theta^*(\mathcal{T})$ represents the adapted sampler parameters after $K$ inner loop steps. The meta-objective combines:

$$\mathcal{L}_{\text{meta}} = \mathcal{L}_{\text{variance}} + \lambda_{\text{cor}}\mathcal{L}_{\text{correlation}} + \lambda_{\text{reg}}\mathcal{L}_{\text{regularization}}$$

**Correlation Loss** (encourages high correlation between control variates and test functions):
$$\mathcal{L}_{\text{correlation}} = -\sum_{k=1}^{K_f} |\text{Corr}(f_k(\mathbf{x}), g_{\phi}(\mathbf{x}, \mathbf{z}))|$$

**Regularization** (prevents overfitting and ensures smooth control variates):
$$\mathcal{L}_{\text{regularization}} = \|\phi\|^2 + \mathbb{E}_{\mathbf{x}}\|\nabla_{\mathbf{x}} g_{\phi}(\mathbf{x}, \mathbf{z})\|^2$$

### 3.4 Algorithmic Implementation

**Algorithm 1: Meta-Learned Control Variates for MCMC**

```
Input: Task distribution p(T), step sizes η_θ, η_φ, iterations M_outer, K_inner
Output: Sampler parameters θ, control variate parameters φ, ψ

1: Initialize θ, φ, ψ randomly
2: for m = 1 to M_outer do
3:   Sample batch of tasks {T_j} ~ p(T)
4:   for each task T_j do
5:     # Inner loop: adapt sampler
6:     θ_j^(0) ← θ
7:     Encode task: z_j ← Enc_ψ(U_j)
8:     for k = 1 to K_inner do
9:       Generate samples {x_i} using T_θ_j^(k)
10:      Compute L_inner(θ_j^(k), φ; T_j)
11:      θ_j^(k+1) ← θ_j^(k) - η_θ ∇_θ L_inner
12:    end for
13:    θ_j^* ← θ_j^(K_inner)
14:    
15:    # Compute meta-gradients
16:    Generate validation samples {x_i^val} using T_θ_j^*
17:    Compute L_meta(φ, ψ, θ_j^*; T_j)
18:  end for
19:  
20:  # Outer loop: update control variates
21:  φ ← φ - η_φ ∇_φ Σ_j L_meta(φ, ψ, θ_j^*; T_j)
22:  ψ ← ψ - η_φ ∇_ψ Σ_j L_meta(φ, ψ, θ_j^*; T_j)
23:  
24:  # Update base sampler (optional)
25:  θ ← θ - η_θ ∇_θ Σ_j L_sampling(θ_j^*; T_j)
26: end for
```

### 3.5 Experimental Design

#### 3.5.1 Benchmark Tasks

**Track 1: Synthetic Distributions**
- Multi-modal Gaussian mixtures (2D-20D)
- Funnel distributions (Neal's funnel, various dimensions)
- Strongly log-concave distributions with varying condition numbers

**Track 2: Bayesian Inverse Problems**
- Logistic regression with various datasets (MNIST, CIFAR-10 subsets)
- Bayesian neural network posteriors (small architectures)
- Deblurring and inpainting problems with Gaussian priors

**Track 3: Molecular Dynamics**
- Alanine dipeptide in implicit solvent
- Small protein folding (Trp-cage)
- Lennard-Jones clusters (13-55 particles)

#### 3.5.2 Baseline Comparisons

We compare against:
1. **Classical MCMC**: Hamiltonian Monte Carlo (HMC), NUTS
2. **Learned Samplers**: Neural Transport (Rezende et al.), Flow-based MCMC (Gabrie et al.)
3. **Variance Reduction Baselines**: Fixed analytical control variates (when available), Rao-Blackwellization
4. **Ablations**: Our method without meta-learning (task-specific control variates), without bi-level optimization

#### 3.5.3 Evaluation Metrics

**Primary Metrics**:
1. **Variance Reduction Factor (VRF)**: 
$$\text{VRF} = \frac{\text{Var}(\hat{\mu}_f)}{\text{Var}(\hat{\mu}_f^{\text{CV}})}$$

2. **Effective Sample Size (ESS)**:
$$\text{ESS} = \frac{N}{1 + 2\sum_{k=1}^{\infty}\rho_k}$$
where $\rho_k$ are lag-$k$ autocorrelations

3. **Mean Squared Error (MSE)** for expectation estimates (when ground truth available)

**Secondary Metrics**:
- Convergence diagnostics: $\hat{R}$ statistic, Geweke diagnostics
- Computational cost: wall-clock time, gradient evaluations
- Sample quality: Maximum Mean Discrepancy (MMD) to target distribution
- Generalization: zero-shot performance on held-out task families

#### 3.5.4 Implementation Details

- **Neural Architectures**: ResNet-style networks for $S_{\theta}$, attention-based encoders for task embedding
- **Optimization**: Adam optimizer with learning rate scheduling, gradient clipping
- **Hardware**: Experiments on NVIDIA A100 GPUs
- **Software**: JAX for automatic differentiation and vectorization, implementations released as open-source

### 3.6 Theoretical Analysis

We will provide theoretical analysis addressing:

1. **Convergence Guarantees**: Prove that under Lipschitz and strong convexity assumptions, the bi-level optimization converges to a stationary point of the meta-objective

2. **Variance Reduction Bounds**: Derive upper bounds on achievable variance reduction as a function of the representational capacity of $g_{\phi}$ and correlation structure in task distribution

3. **Generalization Analysis**: Apply PAC-Bayes bounds to characterize generalization error of meta-learned control variates to new tasks

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Outcomes**:
- **2-5× variance reduction** in expectation estimates compared to vanilla learned samplers across benchmark tasks
- **1.5-3× improvement in ESS** per unit computational cost
- **30-50% reduction in wall-clock time** to achieve target MSE on Bayesian inverse problems
- **Successful transfer** to held-out task families with <20% performance degradation

**Qualitative Outcomes**:
- Novel neural architectures for adaptive control variates that can be integrated into existing learned samplers
- Comprehensive benchmark suite for evaluating variance in learned MCMC methods
- Open-source implementation enabling reproducibility and community adoption
- Theoretical framework connecting representation learning with classical variance reduction

### 4.2 Scientific Impact

**Advancing Probabilistic Inference**: This work addresses a fundamental limitation of learned samplers—high variance—that has hindered their adoption in scientific applications. By demonstrating that variance reduction can be learned rather than hand-crafted, we establish learned samplers as viable alternatives to classical methods for high-stakes applications.

**Bridging Classical and Modern Methods**: The framework provides a principled way to incorporate decades of statistical knowledge (control variates, Rao-Blackwellization) into modern deep learning architectures. This cross-pollination can inspire similar integrations in other areas where classical methods remain dominant.

**Enabling New Applications**: Reliable, low-variance learned samplers unlock applications previously inaccessible due to computational constraints:
- Real-time uncertainty quantification in medical imaging
- Accelerated drug discovery through efficient conformational sampling
- Improved Bayesian optimization for engineering design

### 4.3 Practical Impact

**Tool for Practitioners**: The open-source implementation will provide practitioners with:
- Drop-in replacement for existing MCMC samplers with automatic variance reduction
- Pre-trained control variate networks for common task families
- Diagnostic tools for monitoring variance in learned samplers

**Benchmark for Community**: Our benchmark suite addresses the workshop's call for benchmarks and datasets, providing:
- Standardized evaluation protocols for variance in learned samplers
- Diverse task families spanning synthetic problems to real-world applications
- Baseline results facilitating fair comparisons

**Educational Resource**: Detailed ablation studies and visualizations will serve as educational materials demonstrating:
- When and why learned control variates outperform fixed approaches
- Trade-offs between sampling efficiency and variance reduction
- Failure modes and limitations of the approach

### 4.4 Alignment with Workshop Goals

This proposal directly addresses multiple workshop themes:

- **Classical sampling approaches and how learning accelerates them**: We demonstrate how meta-learning enhances classical control variates
- **Understanding sampling from theoretical perspectives**: We provide convergence analysis and variance reduction bounds
- **Applications to Bayesian inference and natural sciences**: Comprehensive evaluation on inverse problems and molecular dynamics
- **Challenges and open problems**: We address the critical challenge of variance instability in learned samplers

The bi-level optimization framework and meta-learned control variates represent a novel methodological contribution that bridges statistics, optimization, and deep learning—exemplifying the "learning meets sampling" philosophy central to the workshop.

### 4.5 Future Directions

Success of this work would enable several promising extensions:
- **Multi-fidelity approaches**: Learning control variates using cheap low-fidelity simulations
- **Adaptive allocation**: Dynamically allocating computational budget between sampling and variance reduction
- **Connections to reinforcement learning**: Framing control variate learning as a policy optimization problem
- **Extensions to other estimators**: Applying meta-learned variance reduction to importance sampling and sequential Monte Carlo

This research establishes a foundation for the next generation of variance-aware learned samplers, making them reliable tools for scientific discovery and decision-making under uncertainty.