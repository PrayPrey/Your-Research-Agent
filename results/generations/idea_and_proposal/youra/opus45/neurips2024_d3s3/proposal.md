# Research Proposal: Gradient-Guided Predictive Coding Networks for Sample-Efficient Simulation-Based Inference

## 1. Introduction

### 1.1 Background

Simulation-based inference (SBI) has emerged as a powerful paradigm for scientific discovery, enabling researchers to perform Bayesian inference in complex systems where the likelihood function is intractable but simulations can be generated from a forward model. This approach has found applications across diverse scientific domains, including physics modeling, molecular design, cosmology, and climate science. However, a fundamental challenge persists: SBI methods typically require thousands to millions of expensive simulator evaluations to accurately estimate posterior distributions, creating a significant computational bottleneck in domains where each simulation is costly.

Recent advances in machine learning have produced two complementary approaches to address inference challenges. First, differentiable simulators—implemented in autodiff frameworks such as JAX and PyTorch—provide gradient information $\partial x/\partial \theta$ that characterizes how simulation outputs change with respect to parameters. Zeghal et al. (2022) demonstrated that incorporating these gradients into Neural Posterior Estimation (NPE) can improve sample efficiency by approximately 2×. Second, Predictive Coding Networks (PCNs) offer a biologically-inspired framework for hierarchical inference, where each layer minimizes local prediction errors through iterative settling dynamics. Recent theoretical work by van Zwol et al. (2024) established mathematical equivalence between PCN inference and variational inference, while the JPC library (2024) demonstrated that ODE-based settling achieves rapid convergence.

Despite these advances, a critical gap remains: no existing method combines the gradient information from differentiable simulators with the hierarchical inference capabilities of PCNs. Current gradient-augmented approaches use gradients only during training, missing potential benefits during inference. Meanwhile, PCN-based methods ignore available gradient information entirely. This disconnect limits sample efficiency in precisely the domains where computational constraints are most severe.

### 1.2 Research Objectives

This research proposes **Gradient-Guided Predictive Coding (G2PC)**, a novel architecture that injects differentiable simulator gradients as layer-wise error signals within a PCN framework for posterior estimation. Our primary objectives are:

1. **Develop the G2PC architecture** that integrates simulator gradients into PCN settling dynamics through a principled error signal transformation mechanism.

2. **Demonstrate superior sample efficiency** by achieving target posterior accuracy (C2ST < 0.55) with >50% fewer simulations compared to standard NPE baselines.

3. **Validate the causal mechanism** through systematic ablation studies that isolate the contributions of gradient injection, settling iterations, and hierarchical depth.

4. **Establish practical guidelines** for applying G2PC across different problem characteristics, including parameter dimensionality and posterior complexity.

### 1.3 Significance

This research addresses a fundamental bottleneck in simulation-based scientific discovery. By dramatically reducing the number of required simulations, G2PC would enable practical Bayesian inference in domains where computational budgets are severely constrained—such as climate modeling, drug discovery, and nuclear fusion regulation. The integration of gradient information with hierarchical inference represents a novel theoretical contribution that bridges differentiable programming and predictive coding theory. Furthermore, success would validate the broader principle that combining complementary sources of information (gradients and hierarchical structure) yields synergistic benefits beyond either approach alone.

---

## 2. Methodology

### 2.1 Problem Formulation

Consider a simulator $f: \Theta \rightarrow \mathcal{X}$ that maps parameters $\theta \in \Theta \subseteq \mathbb{R}^d$ to observations $x \in \mathcal{X} \subseteq \mathbb{R}^m$. Given a prior $p(\theta)$ and observed data $x_{\text{obs}}$, our goal is to estimate the posterior distribution $p(\theta | x_{\text{obs}})$. In the SBI setting, we cannot evaluate the likelihood $p(x|\theta)$ directly, but we can sample $(\theta, x)$ pairs by drawing $\theta \sim p(\theta)$ and computing $x = f(\theta)$.

When the simulator is differentiable, we additionally have access to the Jacobian:

$$J(\theta) = \frac{\partial f(\theta)}{\partial \theta} \in \mathbb{R}^{m \times d}$$

Our hypothesis states that incorporating $J(\theta)$ as layer-wise error signals in a PCN architecture will constrain the posterior landscape, achieving superior sample efficiency compared to methods that ignore or underutilize this gradient information.

### 2.2 G2PC Architecture

The G2PC architecture consists of $L$ hierarchical layers, each maintaining latent representations $z^{(l)} \in \mathbb{R}^{h_l}$ for $l = 1, \ldots, L$. The architecture operates through four key mechanisms:

**Step 1: Gradient Computation**

For each training pair $(\theta, x)$, we compute the simulator Jacobian via automatic differentiation:

$$J(\theta) = \nabla_\theta f(\theta)$$

We also compute a gradient-derived feature vector that captures local sensitivity information:

$$g(\theta) = \text{vec}\left(\frac{J(\theta)^T J(\theta)}{\|J(\theta)\|_F + \epsilon}\right)$$

where $\epsilon > 0$ prevents numerical instability.

**Step 2: Error Signal Generation**

At each PCN layer $l$, we generate prediction errors that incorporate both standard reconstruction errors and gradient-guided signals. The total error at layer $l$ is:

$$\varepsilon^{(l)} = \underbrace{(z^{(l)} - \hat{z}^{(l)})}_{\text{reconstruction error}} + \lambda_g \cdot \underbrace{W_g^{(l)} \cdot \phi(g(\theta), z^{(l-1)})}_{\text{gradient-guided error}}$$

where $\hat{z}^{(l)} = f_\theta^{(l)}(z^{(l+1)})$ is the top-down prediction from layer $l+1$, $W_g^{(l)}$ is a learnable projection matrix, $\phi(\cdot, \cdot)$ is a nonlinear combination function (implemented as a small MLP), and $\lambda_g$ is a hyperparameter controlling gradient influence.

**Step 3: ODE-Based Settling Dynamics**

During inference, latent representations evolve according to precision-weighted dynamics:

$$\frac{dz^{(l)}}{dt} = -\Pi^{(l)} \varepsilon^{(l)} + \Pi^{(l+1)} (W^{(l+1)})^T \varepsilon^{(l+1)}$$

where $\Pi^{(l)}$ is a learnable precision matrix at layer $l$. We solve this ODE using an adaptive 2nd-order solver (Heun's method) for $T_{\text{settle}}$ iterations:

$$z^{(l)}_{t+1} = z^{(l)}_t + \frac{\Delta t}{2}\left(k_1 + k_2\right)$$

where $k_1 = f(z^{(l)}_t)$ and $k_2 = f(z^{(l)}_t + \Delta t \cdot k_1)$.

**Step 4: Hierarchical Posterior Estimation**

After settling, the final latent representation $z^{(1)}$ is decoded into posterior parameters. For a Gaussian posterior approximation:

$$\mu_\theta = W_\mu z^{(1)} + b_\mu, \quad \log \sigma_\theta = W_\sigma z^{(1)} + b_\sigma$$

For more flexible posteriors, we use a normalizing flow conditioned on $z^{(1)}$:

$$q_\phi(\theta | x) = \text{NormalizingFlow}(z^{(1)}; \phi)$$

### 2.3 Training Procedure

**Loss Function:**

The total training loss combines the standard NPE loss with PCN energy terms:

$$\mathcal{L} = \underbrace{-\mathbb{E}_{(\theta,x)\sim p(\theta,x)}[\log q_\phi(\theta|x)]}_{\text{NPE loss}} + \alpha \sum_{l=1}^{L} \underbrace{\|\varepsilon^{(l)}\|^2_{\Pi^{(l)}}}_{\text{precision-weighted prediction error}}$$

where $\|\varepsilon\|^2_\Pi = \varepsilon^T \Pi \varepsilon$ and $\alpha$ balances the two objectives.

**Training Algorithm:**

```
Algorithm 1: G2PC Training
Input: Prior p(θ), Simulator f, Training budget N_sim
Output: Trained G2PC network parameters φ

1. Initialize network parameters φ randomly
2. For iteration i = 1 to N_iter:
   a. Sample θ ~ p(θ)
   b. Compute x = f(θ) and J(θ) = ∇_θ f(θ)
   c. Compute gradient features g(θ)
   d. Forward pass: compute z^(l) for all layers
   e. Settling: run ODE dynamics for T_settle iterations
   f. Compute loss L and update φ via Adam optimizer
3. Return φ
```

### 2.4 Experimental Design

**Benchmarks:**

We evaluate on three standard SBI benchmarks of increasing complexity:

1. **Two Moons** ($d=2$, $m=2$): A simple benchmark with a crescent-shaped posterior, useful for visualization and rapid iteration.

2. **SLCP** (Simple Likelihood Complex Posterior, $d=5$, $m=8$): A benchmark with a multi-modal posterior that tests the method's ability to capture complex distributions.

3. **Lotka-Volterra** ($d=4$, $m=20$): A predator-prey dynamical system that represents realistic scientific modeling scenarios.

**Baselines:**

1. **Standard NPE**: Neural Posterior Estimation without gradient information (Papamakarios et al., 2019)
2. **Gradient-NPE**: NPE augmented with simulator gradients during training only (Zeghal et al., 2022)
3. **Standard PCN**: Predictive Coding Network without gradient injection

**Evaluation Metrics:**

1. **C2ST (Classifier Two-Sample Test)**: Measures posterior quality; values near 0.5 indicate indistinguishable samples from the true posterior. Target: C2ST < 0.55.

2. **Sample Efficiency**: Number of simulations required to achieve target C2ST < 0.55.

3. **Inference Time**: Wall-clock time per posterior sample (milliseconds).

4. **Training Time**: Total wall-clock time including gradient computation overhead.

**Experimental Protocol:**

For each method and benchmark:
- Run 25 independent trials with different random seeds
- Vary simulation budget $N_{\text{sim}} \in \{100, 250, 500, 1000, 2500, 5000, 10000\}$
- Record C2ST at each budget level
- Measure time metrics on standardized hardware (NVIDIA A100 GPU)

**Ablation Studies:**

1. **Settling Iterations**: Vary $T_{\text{settle}} \in \{1, 5, 10, 20, 50\}$ to validate the contribution of iterative refinement.

2. **Hierarchical Depth**: Vary $L \in \{3, 5, 7\}$ to identify optimal architecture depth.

3. **Gradient Influence**: Vary $\lambda_g \in \{0, 0.1, 0.5, 1.0\}$ to isolate gradient contribution.

4. **Inference-Time Gradients**: Compare gradient injection during training only vs. training and inference.

**Statistical Analysis:**

- Primary test: Paired t-test comparing simulation counts to reach target C2ST
- Significance level: $\alpha = 0.05$ (one-tailed), with Bonferroni correction for multiple comparisons ($\alpha_{\text{adj}} = 0.017$)
- Effect size: Cohen's d with target $d \geq 0.8$
- Report: Mean ± Std Dev, 95% CI, p-value

### 2.5 Implementation Details

- **Framework**: JAX with Flax for neural network components
- **PCN Implementation**: Built on JPC library for ODE-based settling
- **Normalizing Flows**: Neural Spline Flows with 5 coupling layers
- **Network Capacity**: ~500K parameters matched across all methods
- **Optimizer**: Adam with learning rate $10^{-4}$, cosine annealing
- **Precision Matrices**: Initialized as identity, learned during training

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect G2PC to achieve target posterior accuracy (C2ST < 0.55) with >50% fewer simulations than standard NPE across all three benchmarks. Based on Zeghal et al.'s (2022) demonstration of 2× improvement with gradient-augmented NPE, and the additional benefits of hierarchical PCN inference, we anticipate:

- Two Moons: ~60% reduction in simulation budget
- SLCP: ~50% reduction in simulation budget  
- Lotka-Volterra: ~45% reduction in simulation budget

**Mechanism Validation (P2):** We expect settling iterations $T_{\text{settle}} > 10$ to produce significantly better C2ST than feedforward inference ($T_{\text{settle}} = 1$), with diminishing returns beyond $T_{\text{settle}} \approx 20$. This would validate that iterative refinement—not just architectural changes—contributes to improved performance.

**Depth Scaling (P3):** We expect optimal performance at hierarchical depth $L \in \{3, 5\}$ for standard benchmarks, with potential instability at $L > 7$ without additional stabilization techniques.

### 3.2 Potential Challenges and Mitigations

1. **Gradient Computation Overhead**: If gradient computation significantly increases training time, we will explore gradient caching and amortization strategies.

2. **Settling Convergence**: If settling fails to converge within reasonable iterations, we will investigate adaptive step sizes and momentum-based dynamics.

3. **Multi-Modal Posteriors**: If G2PC struggles with complex multi-modal posteriors (SLCP), we will explore mixture density outputs and ensemble methods.

### 3.3 Scientific Impact

**Theoretical Contributions:**
- First principled integration of differentiable simulator gradients with predictive coding inference
- Novel error signal formulation that bridges autodiff and biological plausibility
- Theoretical analysis of gradient-guided settling dynamics convergence

**Practical Contributions:**
- Open-source G2PC implementation compatible with existing SBI toolkits
- Practical guidelines for hyperparameter selection across problem types
- Benchmark results establishing new sample efficiency standards

### 3.4 Broader Impact

Success in this research would have far-reaching implications for simulation-based scientific discovery:

1. **Climate Science**: Enable more comprehensive uncertainty quantification in climate models where each simulation requires substantial computational resources.

2. **Drug Discovery**: Accelerate molecular design by reducing the number of expensive quantum chemistry simulations required for Bayesian optimization.

3. **Physics**: Facilitate parameter inference in particle physics and cosmology where simulations are computationally intensive.

4. **Engineering**: Enable real-time Bayesian inference in manufacturing and wireless systems where rapid adaptation is critical.

By reducing simulation requirements by >50%, G2PC would effectively double the scope of problems tractable with current computational budgets, democratizing access to rigorous Bayesian inference across scientific domains.

### 3.5 Future Directions

This work opens several avenues for future research:

1. **Extension to Non-Differentiable Simulators**: Developing surrogate gradient estimators for black-box simulators
2. **Scaling to High Dimensions**: Investigating sparse PCN architectures for $d > 50$
3. **Active Learning Integration**: Combining G2PC with adaptive simulation selection strategies
4. **Real-World Applications**: Validating on domain-specific simulators in physics, chemistry, and engineering

---

## 4. Conclusion

This proposal presents G2PC, a novel architecture that combines differentiable simulator gradients with predictive coding networks for sample-efficient simulation-based inference. By injecting gradient information as layer-wise error signals and leveraging hierarchical iterative refinement, G2PC addresses a critical gap in current SBI methods. Our rigorous experimental design, including comprehensive ablations and statistical analysis, will validate both the practical benefits and underlying mechanisms of this approach. Success would establish new standards for sample efficiency in SBI and enable practical Bayesian inference in simulation-constrained scientific domains.