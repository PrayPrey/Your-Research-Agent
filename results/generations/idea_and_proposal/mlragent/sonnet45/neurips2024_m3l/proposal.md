# Research Proposal: Theoretical Analysis of Learning Rate Warmup via Continuous-Time Approximations

## 1. Title

**Understanding Learning Rate Warmup through Stochastic Differential Equation Analysis at the Edge of Stability: A Continuous-Time Framework for Principled Warmup Schedule Design**

## 2. Introduction

### Background

The training of modern large-scale deep learning models, particularly transformers and foundation models with billions of parameters, has revealed a critical dependence on learning rate warmup—a technique where the learning rate is gradually increased from near-zero to a target value during initial training iterations. Despite its ubiquitous adoption in state-of-the-art models (BERT, GPT series, Vision Transformers), learning rate warmup remains poorly understood theoretically. Practitioners rely on heuristics and empirical tuning, which becomes prohibitively expensive when training costs can reach millions of dollars for a single run.

Recent observations of the Edge of Stability (EoS) phenomenon—where gradient descent operates stably with learning rates exceeding the traditional stability threshold—have challenged classical optimization theory. Standard convergence analyses assume learning rates small enough to guarantee monotonic loss decrease, yet modern practice routinely violates these assumptions with superior empirical performance. This disconnect between theory and practice is particularly acute for warmup: without understanding *why* warmup prevents early-stage divergence, we cannot make principled decisions about warmup duration, schedule shape, or adaptation to new architectures and scales.

The literature on continuous-time approximations of discrete optimization algorithms offers a promising avenue for theoretical understanding. Stochastic differential equations (SDEs) can capture the interplay between gradient descent's deterministic drift and stochastic gradient noise's diffusion effects. However, existing SDE analyses typically assume fixed, small learning rates within the stable regime, rendering them inadequate for analyzing warmup schedules that intentionally traverse from very small to large (potentially beyond-stable) learning rates.

### Research Objectives

This research aims to develop a rigorous theoretical framework for understanding learning rate warmup through continuous-time SDE approximations that remain valid at large learning rates near or beyond classical stability thresholds. Specifically, we will:

1. **Derive novel SDE approximations** for gradient-based optimization with time-varying learning rates under realistic loss landscape assumptions that account for local curvature variations
2. **Establish validity conditions** for these approximations in the beyond-stable regime, explicitly characterizing discretization errors as functions of instantaneous learning rate, batch size, and loss geometry
3. **Characterize the stabilization mechanism** of warmup by analyzing how gradual learning rate increase controls the interaction between gradient noise magnitude and loss curvature
4. **Develop principled warmup schedule design** based on model architecture parameters (depth, width, initialization scale), optimization hyperparameters (batch size, target learning rate), and dataset statistics

### Significance

This research addresses fundamental gaps at the intersection of optimization theory and deep learning practice:

- **Theoretical Impact**: Extending SDE approximation theory beyond the stable regime fills a critical gap in understanding modern optimization dynamics, providing mathematical tools for analyzing non-classical training phenomena
- **Practical Impact**: Principled warmup schedules can substantially reduce the computational cost of hyperparameter tuning for large models, with potential savings of millions of dollars per training run
- **Bridging Theory and Practice**: By explaining a widely-used but theoretically opaque technique, this work exemplifies how mathematical analysis can guide empirical deep learning, fostering closer integration between theory and practice in the large model era

## 3. Methodology

### 3.1 Mathematical Framework

#### 3.1.1 Problem Setup

Consider the optimization problem:
$$\min_{\theta \in \mathbb{R}^d} L(\theta) = \mathbb{E}_{\xi \sim \mathcal{D}}[\ell(\theta; \xi)]$$

where $\theta$ represents model parameters, $L(\theta)$ is the population loss, and $\ell(\theta; \xi)$ is the per-sample loss for data point $\xi$ from distribution $\mathcal{D}$.

The discrete-time stochastic gradient descent with time-varying learning rate follows:
$$\theta_{k+1} = \theta_k - \alpha_k \hat{\nabla} L(\theta_k)$$

where $\alpha_k = \alpha(k)$ is the learning rate at iteration $k$, and $\hat{\nabla} L(\theta_k) = \frac{1}{B}\sum_{i=1}^B \nabla \ell(\theta_k; \xi_i^{(k)})$ is the mini-batch gradient with batch size $B$.

For warmup, we consider schedules of the form:
$$\alpha(k) = \begin{cases}
\alpha_{\text{target}} \cdot \min\left(1, \frac{k}{K_{\text{warmup}}}\right) & k \leq K_{\text{warmup}} \\
\alpha_{\text{target}} & k > K_{\text{warmup}}
\end{cases}$$

#### 3.1.2 Continuous-Time SDE Approximation

We derive a continuous-time approximation by introducing pseudo-time $t = k \alpha_{\text{unit}}$ where $\alpha_{\text{unit}}$ is a reference learning rate scale. The corresponding SDE takes the form:

$$d\theta_t = -\gamma(t) \nabla L(\theta_t) dt + \sqrt{2\gamma(t)D(\theta_t)} dW_t$$

where:
- $\gamma(t) = \alpha(t/\alpha_{\text{unit}})$ is the time-varying learning rate function in continuous time
- $D(\theta_t) = \frac{1}{B}\text{Cov}_{\xi}[\nabla \ell(\theta_t; \xi)]$ is the gradient covariance matrix (noise)
- $W_t$ is a $d$-dimensional Wiener process

**Key Innovation**: Unlike standard derivations assuming constant small $\gamma$, we explicitly track how time-varying $\gamma(t)$ affects both drift and diffusion terms, accounting for the modulation of effective noise by the learning rate schedule.

#### 3.1.3 Loss Landscape Assumptions

We model the loss landscape with the following assumptions that capture realistic non-convex geometry:

**Assumption 1 (Local Smoothness)**: For all $\theta, \theta'$ in a neighborhood $\mathcal{N}(\theta_0, R)$ of the trajectory:
$$\|\nabla L(\theta) - \nabla L(\theta')\| \leq \beta(\theta)\|\theta - \theta'\|$$
where $\beta(\theta)$ is a position-dependent smoothness constant satisfying $\beta_{\min} \leq \beta(\theta) \leq \beta_{\max}$.

**Assumption 2 (Gradient Noise Structure)**: The gradient noise satisfies:
$$\mathbb{E}_{\xi}[\nabla \ell(\theta; \xi)] = \nabla L(\theta)$$
$$\text{Tr}(D(\theta)) \leq \sigma^2(1 + \|\nabla L(\theta)\|^2)$$
capturing that noise magnitude can grow with gradient norm (realistic for deep networks).

**Assumption 3 (Bounded Hessian Spectrum)**: The Hessian's largest eigenvalue is bounded:
$$\lambda_{\max}(\nabla^2 L(\theta)) \leq \Lambda(\theta)$$
where $\Lambda(\theta)$ varies spatially but satisfies $\Lambda_{\min} \leq \Lambda(\theta) \leq \Lambda_{\max}$.

### 3.2 Theoretical Analysis

#### 3.2.1 Discretization Error Characterization

**Theorem 1 (Approximation Validity)**: Under Assumptions 1-3, for learning rates satisfying $\gamma(t) \leq \gamma_{\max}(t)$ where:
$$\gamma_{\max}(t) = \frac{2}{\Lambda(\theta_t)} \cdot \frac{1}{1 + \sqrt{d/B}}$$

the discrete iterates $\theta_k$ and continuous trajectory $\theta_t$ satisfy:
$$\mathbb{E}\|\theta_k - \theta_{k\alpha_{\text{unit}}}\|^2 \leq C \cdot \alpha_{\text{unit}}^2 \cdot \exp\left(\int_0^{k\alpha_{\text{unit}}} \gamma(s)\Lambda(\theta_s) ds\right)$$

for a constant $C$ depending on $\sigma^2$, $d$, $B$, and trajectory length.

**Proof Sketch**: 
1. Expand discrete update using Taylor series, retaining second-order terms
2. Take expectations and apply Itô's lemma to the continuous SDE
3. Bound the difference recursively using Grönwall's inequality with time-varying coefficients
4. The key insight is that the exponential factor accumulates the product $\gamma(t)\Lambda(\theta_t)$, which warmup keeps controlled

This theorem extends existing SDE approximation results to time-varying learning rates and provides explicit dependence on the learning rate schedule through the integral term.

#### 3.2.2 Stability Analysis at the Edge

**Theorem 2 (Warmup Stabilization Mechanism)**: Consider a warmup schedule $\gamma(t) = \gamma_{\text{target}} \cdot \min(1, t/T_{\text{warmup}})$. If the target learning rate satisfies $\gamma_{\text{target}} \Lambda_0 \leq 2 + \epsilon$ (beyond the classical stability threshold of 2) for small $\epsilon > 0$, and:
$$T_{\text{warmup}} \geq \frac{\log(\gamma_{\text{target}}\Lambda_0 B/d)}{\gamma_{\text{target}}(\Lambda_0 - \delta)}$$

for some $\delta < \Lambda_0$, then with probability at least $1 - \delta'$:
$$\sup_{t \in [0, T_{\text{warmup}}]} \|\theta_t - \theta_0\| \leq R_{\text{safe}}$$

where $R_{\text{safe}}$ is a radius within which the loss landscape assumptions hold.

**Proof Strategy**:
1. Decompose the trajectory variance into drift-dominated and diffusion-dominated phases
2. During warmup, show that $\gamma(t)$ grows slowly enough that drift compresses the distribution before diffusion can cause divergence
3. Use martingale concentration inequalities to bound trajectory excursions
4. The logarithmic dependence on $B/d$ ratio captures the interplay between batch noise and parameter dimension

This theorem formalizes the intuition that warmup prevents early catastrophic divergence by allowing the gradient flow to establish a reasonable loss basin before strong noise kicks in.

#### 3.2.3 Optimal Warmup Duration

**Theorem 3 (Warmup Duration Scaling)**: For a neural network with depth $L$, width $m$, initialized with scale $\sigma_{\text{init}}$, training with batch size $B$ toward target learning rate $\gamma_{\text{target}}$, the optimal warmup duration (minimizing time to reach loss threshold $L_{\text{threshold}}$) scales as:

$$K_{\text{warmup}}^* \asymp \frac{1}{\gamma_{\text{target}}} \cdot \log\left(\frac{L \cdot m \cdot \sigma_{\text{init}}^2}{B}\right)$$

**Proof Outline**:
1. Model initialization landscape curvature using neural tangent kernel theory: $\Lambda_0 \approx L/\sigma_{\text{init}}^2$
2. Gradient noise scales as $\text{Tr}(D_0) \approx L \cdot m \cdot \|\nabla L_0\|^2 / B$
3. Apply Theorem 2 with optimal $\delta$ that balances warmup duration against convergence rate
4. The logarithmic factor captures the ratio of effective noise to batch smoothing

This provides actionable guidance: doubling model size increases optimal warmup duration by a constant additive factor, not multiplicatively.

### 3.3 Experimental Design

#### 3.3.1 Data Collection and Model Selection

We will conduct experiments across multiple scales and architectures:

**Vision Tasks**:
- CIFAR-10/100: ResNet-{18, 50}, Vision Transformer (ViT-Small)
- ImageNet: ResNet-{50, 101}, ViT-{Base, Large}

**Language Tasks**:
- WikiText-103: Transformer (12-layer, 768-dim)
- C4 Dataset: Transformer scaling from 125M to 1.3B parameters

**Architecture Parameters**: Systematically vary depth ($L \in \{6, 12, 24\}$), width ($m \in \{512, 768, 1024\}$), initialization scale ($\sigma_{\text{init}} \in \{0.02, 0.1, 0.5\}$).

#### 3.3.2 Warmup Schedule Variations

For each configuration, test:
1. **No warmup** (baseline)
2. **Linear warmup** with durations $K_w \in \{100, 500, 1000, 5000, 10000\}$ steps
3. **Theory-predicted optimal** warmup from Theorem 3
4. **Exponential warmup**: $\alpha(k) = \alpha_{\text{target}}(1 - e^{-k/K_w})$
5. **Polynomial warmup**: $\alpha(k) = \alpha_{\text{target}}(k/K_w)^p$ for $p \in \{0.5, 1, 2\}$

#### 3.3.3 Measurements and Validation

**Primary Metrics**:
1. **Training Loss Trajectory**: Record $L(\theta_k)$ every 10 steps
2. **Gradient Norm Evolution**: $\|\nabla L(\theta_k)\|$ every 10 steps
3. **Parameter Displacement**: $\|\theta_k - \theta_0\|$ every 100 steps
4. **Sharpness**: Approximate $\lambda_{\max}(\nabla^2 L(\theta_k))$ using Lanczos iteration every 500 steps

**SDE Approximation Validation**:
1. Numerically integrate the derived SDE using Euler-Maruyama with small timesteps
2. Compare continuous trajectory $\theta_t$ with discrete $\theta_k$ at matched pseudo-times
3. Compute $\mathbb{E}\|\theta_k - \theta_{k\alpha_{\text{unit}}}\|^2$ empirically over 10 random seeds
4. Verify the bound in Theorem 1 holds with predicted constant $C$

**Edge of Stability Testing**:
1. Measure effective sharpness $\alpha_k \lambda_{\max}(\theta_k)$ throughout training
2. Identify when training enters EoS regime ($\alpha_k \lambda_{\max} > 2$)
3. Correlate warmup completion timing with EoS entry timing
4. Test prediction from Theorem 2 on trajectory excursion bounds

**Ablation Studies**:
1. **Batch size scaling**: Vary $B \in \{32, 128, 512, 2048\}$ and validate $K_{\text{warmup}}^* \propto \log(1/B)$
2. **Architecture scaling**: Validate $K_{\text{warmup}}^* \propto \log(L \cdot m)$ by comparing models of different scales
3. **Initialization impact**: Test theoretical prediction on $\sigma_{\text{init}}$ dependence

#### 3.3.4 Computational Infrastructure

- **Small-scale experiments** (CIFAR, WikiText): 8× NVIDIA A100 GPUs
- **Large-scale experiments** (ImageNet, C4): 64× NVIDIA A100 GPUs with distributed training
- **Total compute budget**: ~5,000 GPU-hours
- **Software stack**: PyTorch 2.0, DeepSpeed for distributed training, Weights & Biases for tracking

### 3.4 Algorithm Development

Based on theoretical insights, we will develop:

**Algorithm 1: Theory-Guided Adaptive Warmup**

```
Input: Model architecture (L, m), initialization scale σ_init,
       batch size B, target learning rate α_target
       
1. Estimate initial sharpness: Λ_0 ← L/σ_init²
2. Estimate gradient noise: σ² ← L·m·||∇L(θ_0)||²/B
3. Compute optimal warmup: 
   K_warmup ← (1/α_target)·log(L·m·σ_init²/B)
4. For k = 1, 2, ..., K_warmup:
   α_k ← α_target·min(1, k/K_warmup)
   θ_k+1 ← θ_k - α_k·∇L̂(θ_k)
   
   # Adaptive adjustment based on realized sharpness
   If k % 100 == 0:
      Λ_k ← estimate_sharpness(θ_k)
      If α_k·Λ_k > 2.5:  # Approaching instability
         K_warmup ← K_warmup × 1.1
```

This algorithm incorporates theoretical predictions while allowing adaptive correction based on observed training dynamics.

## 4. Expected Outcomes & Impact

### 4.1 Theoretical Contributions

1. **Novel SDE Framework**: The first rigorous continuous-time approximation for gradient descent with time-varying learning rates valid at the Edge of Stability, extending the mathematical toolkit for analyzing modern optimization

2. **Mechanistic Understanding of Warmup**: Formal characterization of how warmup stabilizes training by controlling the gradient noise-curvature interaction, resolving a long-standing question about this ubiquitous technique

3. **Scaling Laws for Warmup**: Precise mathematical relationships between optimal warmup duration and model/optimization hyperparameters, enabling principled schedule design

4. **Bridging Classical and Modern Optimization Theory**: Theoretical framework that gracefully degrades to classical results in the small learning rate limit while explaining beyond-stable phenomena

### 4.2 Practical Impact

1. **Computational Cost Reduction**: Eliminating trial-and-error warmup tuning can save 30-50% of hyperparameter search costs for large model training—potentially millions of dollars per major training run

2. **Improved Training Efficiency**: Theory-guided warmup schedules may enable faster convergence by optimally balancing early stability with rapid learning rate increase

3. **Architecture-Specific Guidelines**: Practitioners will gain principled rules for adapting warmup to new architectures (e.g., different normalization schemes, activation functions) without extensive empirical tuning

4. **Foundation Model Training**: Particular benefits for pretraining regimes where multiple data passes and careful hyperparameter selection are critical

### 4.3 Validation and Expected Results

**Hypothesis 1**: Theory-predicted warmup durations will achieve within 10% of empirically optimal convergence speed across tested architectures, validated by extensive experiments on vision and language tasks.

**Hypothesis 2**: SDE approximation error bounds (Theorem 1) will be empirically tight within a factor of 2-3 for tested learning rate schedules, confirming the continuous-time framework's validity.

**Hypothesis 3**: Training runs with insufficient warmup (< 50% of theoretical optimum) will exhibit 20-40% higher early-stage gradient norm variance and occasional loss spikes, while excessive warmup (> 200% of optimum) will show 15-25% slower convergence to target loss.

**Hypothesis 4**: The logarithmic scaling laws (Theorem 3) will explain > 85% of variance in empirically optimal warmup duration across different model scales, batch sizes, and initialization schemes.

### 4.4 Broader Impact

**For the ML Theory Community**: This work demonstrates how classical mathematical tools (SDE theory, stability analysis) can be extended and adapted to explain modern deep learning phenomena, potentially inspiring similar approaches for other theoretically opaque techniques.

**For ML Practitioners**: Providing principled, actionable guidance for a critical hyperparameter reduces the gap between theory and practice, making large-scale training more accessible to researchers without massive computational resources for hyperparameter tuning.

**For the Foundation Models Era**: As models scale to trillions of parameters, the cost of empirical hyperparameter tuning becomes prohibitive. Theory-guided methods become not just useful but essential for sustainable progress.

**Limitations and Future Work**: This research focuses specifically on learning rate warmup and gradient-based optimization. Natural extensions include:
- Analyzing other learning rate schedules (cosine decay, step decay) within the same SDE framework
- Extending to adaptive optimizers (Adam, AdaGrad) with time-varying adaptation rates
- Incorporating momentum and acceleration methods
- Analyzing warmup's interaction with other techniques (gradient clipping, layer-wise learning rates)

**Reproducibility**: All code, experimental configurations, and data will be released open-source, enabling full reproducibility and community extension of this work.

---

**Word Count**: Approximately 2,000 words

This proposal presents a comprehensive research plan that bridges fundamental mathematical theory with practical deep learning concerns, directly addressing the workshop's focus on reconciling optimization theory with modern practice through continuous-time approximations and Edge of Stability analysis.