# Research Proposal: Derivative-Informed Convex Neural Operators for Provable Finite-Sample Optimal Transport

## 1. Title

**DICNO: Derivative-Informed Convex Neural Operators for Provable Finite-Sample Optimal Transport with Monge-Ampère PDE Constraints**

---

## 2. Introduction

### 2.1 Background

Optimal transport (OT) has emerged as a foundational mathematical framework with profound implications across machine learning, providing principled methods for comparing probability distributions, learning generative models, and performing domain adaptation. The classical Monge problem seeks a transport map $T: \mathcal{X} \rightarrow \mathcal{Y}$ that pushes a source distribution $\mu$ to a target distribution $\nu$ while minimizing transportation cost. Under the squared-Euclidean cost $c(x,y) = \|x-y\|^2$, Brenier's theorem guarantees that the optimal transport map takes the form $T^* = \nabla \phi^*$, where $\phi^*$ is a convex potential satisfying the Monge-Ampère partial differential equation:

$$\det(D^2\phi(x)) = \frac{f(x)}{g(\nabla\phi(x))}$$

where $f$ and $g$ denote the density functions of $\mu$ and $\nu$, respectively.

Recent years have witnessed remarkable progress in neural network-based approaches to optimal transport. Input Convex Neural Networks (ICNNs) have been employed to parameterize convex potentials, ensuring that the learned map $\nabla \phi_\theta$ automatically satisfies the structural requirements of Brenier maps. Simultaneously, advances in neural operators and physics-informed neural networks have demonstrated the power of incorporating PDE constraints into learning frameworks. However, a critical gap persists: **existing neural OT methods lack finite-sample convergence guarantees**, limiting their deployment in applications requiring reliability assurances such as single-cell genomics, medical imaging, and financial modeling.

### 2.2 Research Gap and Motivation

Current neural OT approaches suffer from three fundamental limitations:

1. **Absence of Sample Complexity Theory:** While empirical performance is often impressive, practitioners cannot predict how many samples are needed to achieve a desired accuracy level. This contrasts sharply with classical statistical OT estimators, which enjoy well-characterized convergence rates.

2. **Neglect of PDE Structure:** Most neural OT methods treat the problem purely as a regression or optimization task, ignoring the rich geometric structure encoded in the Monge-Ampère equation. This structural information, when properly leveraged, should accelerate convergence and improve generalization.

3. **Lack of Error Decomposition:** Without understanding how different error sources (approximation, statistical, PDE residual) contribute to total error, it is impossible to systematically improve methods or provide theoretical guarantees.

Recent work on Derivative-Informed Fourier Neural Operators (DIFNO) has demonstrated that jointly learning functions and their derivatives under PDE constraints yields universal approximation with improved sample efficiency for semi-linear PDEs. Concurrently, advances in convex neural architectures have established principled initialization and training procedures for ICNNs. This proposal bridges these developments to address the fundamental challenge of provable finite-sample optimal transport.

### 2.3 Research Objectives

This research aims to:

1. **Develop DICNO**, a novel architecture that combines ICNN convexity guarantees with derivative-informed training under Monge-Ampère PDE constraints.

2. **Establish theoretical foundations** for finite-sample convergence, deriving explicit polynomial rates through a three-way error decomposition: $\varepsilon_{\text{total}} \leq \varepsilon_{\text{approx}} + \varepsilon_{\text{stat}} + \varepsilon_{\text{PDE}}$.

3. **Validate empirically** that the proposed method achieves polynomial convergence rates $O(n^{-\alpha})$ with $\alpha \geq 0.3$ across synthetic and real-world benchmarks.

4. **Demonstrate practical impact** on applications including domain adaptation and single-cell trajectory inference.

### 2.4 Significance

Success in this research would establish the **first finite-sample theory for neural optimal transport with hard PDE constraints**, bridging computational OT and provable machine learning. This has immediate implications for:

- **Trustworthy AI:** Enabling deployment of neural OT in safety-critical applications requiring reliability guarantees.
- **Scientific Computing:** Providing a template for incorporating PDE structure into neural network learning with provable benefits.
- **Theoretical Foundations:** Advancing understanding of how geometric constraints improve statistical efficiency in deep learning.

---

## 3. Methodology

### 3.1 Problem Formulation

Let $\mu$ and $\nu$ be probability distributions on $\mathbb{R}^d$ with densities $f$ and $g$, respectively, satisfying $C^{1,\alpha}$ Hölder continuity with bounded support. We seek to learn the Brenier potential $\phi^*$ such that $T^* = \nabla \phi^*$ is the optimal transport map minimizing:

$$W_2^2(\mu, \nu) = \inf_{T: T_\#\mu = \nu} \int_{\mathbb{R}^d} \|x - T(x)\|^2 \, d\mu(x)$$

Given $n$ i.i.d. samples $\{x_i\}_{i=1}^n \sim \mu$ and $\{y_j\}_{j=1}^n \sim \nu$, our goal is to learn $\phi_\theta$ such that the transport error $\|\nabla\phi_\theta - T^*\|_{L^2(\mu)}$ decreases at a polynomial rate in $n$.

### 3.2 DICNO Architecture

**3.2.1 Input Convex Neural Network Base**

We parameterize the potential $\phi_\theta: \mathbb{R}^d \rightarrow \mathbb{R}$ using an ICNN with $L$ layers and width $W$:

$$z_0 = x, \quad z_{\ell+1} = \sigma(W_\ell^{(z)} z_\ell + W_\ell^{(x)} x + b_\ell), \quad \phi_\theta(x) = w^\top z_L + b_L$$

where $\sigma$ is a convex, non-decreasing activation (e.g., softplus), and $W_\ell^{(z)} \geq 0$ element-wise. This architecture guarantees convexity of $\phi_\theta$, ensuring $\nabla\phi_\theta$ is a valid Brenier map candidate.

**3.2.2 Derivative-Informed Training**

Following the DIFNO paradigm, we jointly train on function values and derivatives. The transport map and Hessian are computed via automatic differentiation:

$$T_\theta(x) = \nabla_x \phi_\theta(x), \quad H_\theta(x) = D^2_x \phi_\theta(x)$$

**3.2.3 Hutchinson Hessian Estimation**

Computing the full Hessian $H_\theta \in \mathbb{R}^{d \times d}$ is expensive for large $d$. We employ the Hutchinson trace estimator with $k$ random vectors $\{v_i\}_{i=1}^k$ where $v_i \sim \mathcal{N}(0, I_d)$:

$$\text{tr}(H_\theta) \approx \frac{1}{k} \sum_{i=1}^k v_i^\top H_\theta v_i$$

For the determinant constraint, we use the identity $\log\det(H) = \text{tr}(\log H)$ and approximate via:

$$\log\det(H_\theta) \approx \frac{1}{k} \sum_{i=1}^k v_i^\top (\log H_\theta) v_i$$

computed using matrix-free methods with $k = O(\log d)$ vectors.

### 3.3 Loss Function Design

The DICNO loss comprises three components:

**3.3.1 Transport Loss**

Using the dual formulation of OT, we minimize:

$$\mathcal{L}_{\text{transport}} = \frac{1}{n}\sum_{i=1}^n \phi_\theta(x_i) + \frac{1}{n}\sum_{j=1}^n \phi_\theta^*(y_j)$$

where $\phi_\theta^*$ is the Legendre transform, approximated via:

$$\phi_\theta^*(y) \approx \max_{x \in \{x_i\}} \left[ \langle x, y \rangle - \phi_\theta(x) \right]$$

**3.3.2 Derivative-Informed Loss**

When ground-truth transport maps are available (synthetic settings) or can be approximated:

$$\mathcal{L}_{\text{deriv}} = \frac{1}{n}\sum_{i=1}^n \|T_\theta(x_i) - T^*(x_i)\|^2 + \lambda_H \|H_\theta(x_i) - H^*(x_i)\|_F^2$$

**3.3.3 Monge-Ampère PDE Loss**

The hard constraint enforcing the Monge-Ampère equation:

$$\mathcal{L}_{\text{MA}} = \frac{1}{n}\sum_{i=1}^n \left| \log\det(H_\theta(x_i)) - \log\frac{f(x_i)}{g(T_\theta(x_i))} \right|^2$$

**3.3.4 Total Loss**

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{transport}} + \lambda_1 \mathcal{L}_{\text{deriv}} + \lambda_2 \mathcal{L}_{\text{MA}}$$

with hyperparameters $\lambda_1, \lambda_2 > 0$ balancing the terms.

### 3.4 Theoretical Framework: Three-Way Error Decomposition

**Theorem (Informal).** Under Assumptions A1-A4, the total transport error admits the decomposition:

$$\|T_\theta - T^*\|_{L^2(\mu)} \leq \underbrace{C_1 \cdot \text{poly}(d) \cdot (LW)^{-\beta}}_{\varepsilon_{\text{approx}}} + \underbrace{C_2 \cdot n^{-1/2} \cdot d^{1/2}}_{\varepsilon_{\text{stat}}} + \underbrace{C_3 \cdot k^{-1/2} \cdot \|\mathcal{L}_{\text{MA}}\|^{1/2}}_{\varepsilon_{\text{PDE}}}$$

where:
- $\varepsilon_{\text{approx}}$: Neural network approximation error, decreasing with architecture capacity
- $\varepsilon_{\text{stat}}$: Statistical estimation error from finite samples
- $\varepsilon_{\text{PDE}}$: PDE residual error from imperfect Monge-Ampère satisfaction

**Proof Sketch:**
1. ICNN universal approximation guarantees $\varepsilon_{\text{approx}} \rightarrow 0$ as $L, W \rightarrow \infty$
2. Concentration inequalities bound empirical process deviations, yielding $\varepsilon_{\text{stat}} = O(n^{-1/2})$
3. Hutchinson estimator variance analysis gives $\varepsilon_{\text{PDE}} = O(k^{-1/2})$
4. Triangle inequality combines the terms

### 3.5 Experimental Design

**3.5.1 Datasets and Benchmarks**

| Benchmark | Source $\mu$ | Target $\nu$ | Ground Truth | Purpose |
|-----------|-------------|--------------|--------------|---------|
| Gaussian-to-Gaussian | $\mathcal{N}(0, \Sigma_1)$ | $\mathcal{N}(m, \Sigma_2)$ | Analytical | Rate verification |
| 2D Synthetic | Mixture of Gaussians | Transformed mixture | Numerical | Visualization |
| MNIST↔USPS | MNIST digits | USPS digits | None | Domain adaptation |
| Single-cell | scRNA-seq day 0 | scRNA-seq day 7 | None | Biological application |

**3.5.2 Sample Size Experiments**

For each benchmark, we train DICNO with sample sizes $n \in \{10^2, 3\times10^2, 10^3, 3\times10^3, 10^4, 3\times10^4, 10^5, 10^6\}$, performing 5 independent runs per configuration.

**3.5.3 Evaluation Metrics**

1. **L2 Transport Error:** $\mathcal{E}_{\text{L2}} = \sqrt{\frac{1}{n_{\text{test}}}\sum_{i=1}^{n_{\text{test}}} \|T_\theta(x_i) - T^*(x_i)\|^2}$

2. **Monge-Ampère Residual:** $\mathcal{R}_{\text{MA}} = \frac{1}{n_{\text{test}}}\sum_{i=1}^{n_{\text{test}}} |\det(H_\theta(x_i)) - f(x_i)/g(T_\theta(x_i))|$

3. **Wasserstein Distance:** $W_2(\hat{\nu}, \nu)$ where $\hat{\nu} = (T_\theta)_\# \mu$

4. **Convergence Rate:** Estimated $\alpha$ from linear regression on $\log(\mathcal{E}_{\text{L2}})$ vs $\log(n)$

**3.5.4 Baseline Methods**

1. **Neural EOT:** Entropic OT with neural dual potentials (Wang & Goldfeld 2024)
2. **Monge Gap:** ICNN with soft Monge gap regularization (Uscidda 2023)
3. **Convex PINN:** Physics-informed neural network for Monge-Ampère (Caboussat 2025)
4. **Standard ICNN:** ICNN without derivative-informed training or PDE constraints

**3.5.5 Ablation Studies**

To verify the causal mechanism, we conduct ablations:

| Ablation | Removed Component | Tests |
|----------|-------------------|-------|
| A1 | Derivative-informed loss ($\lambda_1 = 0$) | Necessity of Hessian training |
| A2 | MA constraint ($\lambda_2 = 0$) | Necessity of PDE enforcement |
| A3 | ICNN → standard MLP | Necessity of convexity |
| A4 | Hutchinson → full Hessian | Efficiency vs accuracy tradeoff |

**3.5.6 Statistical Analysis**

- **Primary Test:** One-tailed t-test for $\alpha > 0.1$ at significance level 0.05
- **Correlation Analysis:** Pearson correlation between $\mathcal{R}_{\text{MA}}$ and $\mathcal{E}_{\text{L2}}$, requiring $r^2 \geq 0.5$
- **Confidence Intervals:** Bootstrap 95% CIs for rate estimates

### 3.6 Implementation Details

**Architecture:** ICNN with $L=6$ layers, width $W=256$, softplus activation
**Optimizer:** Adam with learning rate $10^{-3}$, cosine annealing
**Hutchinson Vectors:** $k = \lceil 2\log d \rceil$
**Hyperparameters:** $\lambda_1 = 0.1$, $\lambda_2 = 1.0$ (tuned on validation)
**Hardware:** NVIDIA A100 GPU, estimated 48 GPU-hours for full experiments

### 3.7 Falsification Criteria

The hypothesis is falsified if:
1. **Rate Failure:** Estimated $\alpha \leq 0.1$ or no statistically significant power-law relationship
2. **Mechanism Failure:** Correlation $r^2 < 0.5$ between MA residual and transport error
3. **Comparative Failure:** DICNO underperforms all baselines on all benchmarks
4. **Numerical Failure:** Training diverges or convexity violated in >50% of runs

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome:** We expect DICNO to achieve polynomial convergence rates with $\alpha \geq 0.3$, significantly outperforming the $O(n^{-1/d})$ curse-of-dimensionality rates of non-parametric OT estimators. On the Gaussian-to-Gaussian benchmark with analytical ground truth, we anticipate:

- L2 transport error decreasing from $\sim 0.5$ at $n=100$ to $\sim 0.01$ at $n=10^5$
- Strong correlation ($r^2 > 0.7$) between MA residual and transport error
- 2-5× improvement in sample efficiency over Neural EOT and Monge Gap baselines

**Secondary Outcomes:**
- Validated three-way error decomposition with empirically measurable components
- Ablation studies confirming necessity of each architectural component
- Practical guidelines for hyperparameter selection ($\lambda_1, \lambda_2, k$)

### 4.2 Theoretical Contributions

1. **First Finite-Sample Theory for Neural OT with PDE Constraints:** Establishing explicit polynomial rates bridges the gap between empirical neural OT methods and classical statistical OT theory.

2. **Extension of DIFNO to Fully Nonlinear PDEs:** Demonstrating that derivative-informed training transfers from semi-linear to fully nonlinear (Monge-Ampère) settings expands the applicability of physics-informed neural operators.

3. **Unified Error Decomposition Framework:** The three-way decomposition provides a principled approach to understanding and improving neural OT methods.

### 4.3 Practical Impact

**Domain Adaptation:** Provable transport maps enable reliable transfer learning with quantifiable uncertainty, critical for deploying ML models across distribution shifts.

**Single-Cell Genomics:** Trajectory inference with convergence guarantees allows biologists to trust computational predictions of cellular differentiation pathways.

**Generative Modeling:** Understanding sample complexity informs data collection strategies for training flow-based generative models.

### 4.4 Broader Impact

This research contributes to the broader goal of **trustworthy machine learning** by demonstrating that incorporating mathematical structure (convexity, PDEs) into neural architectures yields not only empirical improvements but also theoretical guarantees. The methodology—combining architectural constraints with physics-informed training—provides a template applicable beyond optimal transport to other inverse problems governed by PDEs.

### 4.5 Limitations and Future Work

**Limitations:**
- Theory restricted to smooth distributions with bounded support
- Computational cost scales with dimension due to Hessian estimation
- Rate constants may be pessimistic; tightening requires refined analysis

**Future Directions:**
- Extension to non-Euclidean costs and Gromov-Wasserstein settings
- Adaptation to unbalanced OT for measures of different mass
- Application to high-dimensional single-cell data ($d > 1000$) with dimensionality reduction

### 4.6 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Phase 1 | Months 1-3 | Architecture implementation, synthetic experiments |
| Phase 2 | Months 4-6 | Theoretical analysis, rate derivation |
| Phase 3 | Months 7-9 | Real-world benchmarks, ablation studies |
| Phase 4 | Months 10-12 | Paper writing, code release, documentation |

---

**Conclusion:** This proposal presents DICNO, a principled approach to neural optimal transport that combines ICNN convexity guarantees with derivative-informed training under Monge-Ampère PDE constraints. By establishing the first finite-sample convergence theory for neural OT with hard PDE enforcement, this research bridges computational optimal transport and provable machine learning, with immediate applications in domain adaptation, generative modeling, and computational biology.