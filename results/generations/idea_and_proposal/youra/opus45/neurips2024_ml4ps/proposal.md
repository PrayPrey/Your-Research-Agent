# Research Proposal: Linear-PCCP: Physics-Constrained Conformal Prediction via Linear Manifold Projection for Rigorous Uncertainty Quantification

## 1. Introduction

### 1.1 Background

Physics-informed neural networks (PINNs) have emerged as a powerful paradigm for solving partial differential equations (PDEs) by embedding physical laws directly into the neural network training process. By incorporating physics-based loss terms derived from governing equations, PINNs can learn solutions that respect fundamental physical principles while leveraging the flexibility of deep learning. This approach has found widespread applications across the physical sciences, including fluid dynamics, heat transfer, materials science, and quantum mechanics.

Despite their success, PINNs face a critical limitation: the lack of rigorous uncertainty quantification (UQ). In safety-critical applications—such as nuclear reactor simulations, aerospace engineering, and climate modeling—practitioners require not only point predictions but also reliable confidence intervals that accurately reflect prediction uncertainty. Traditional approaches to UQ in PINNs, such as Bayesian neural networks or ensemble methods, provide probabilistic estimates but lack formal coverage guarantees. This limitation severely restricts the deployment of PINNs in high-stakes physical science applications where incorrect predictions could have catastrophic consequences.

Conformal prediction (CP) has recently emerged as a promising framework for distribution-free uncertainty quantification. Unlike Bayesian methods, CP provides finite-sample coverage guarantees under minimal assumptions—primarily the exchangeability of calibration data. Recent work has begun applying CP to PINNs, demonstrating that valid prediction intervals can be constructed for physics-informed models. However, existing approaches treat physics constraints as soft regularization terms in the nonconformity score, allowing predictions that may violate fundamental conservation laws such as mass, momentum, or energy conservation.

This creates a fundamental tension: while CP provides statistical coverage guarantees, it does not ensure physical validity. A prediction interval that achieves 95% coverage but permits physically impossible states (e.g., negative mass or energy creation) is of limited practical value in the physical sciences. The challenge is to develop a framework that achieves both rigorous coverage guarantees and strict adherence to physical constraints.

### 1.2 Research Objectives

This research proposes Linear-PCCP (Physics-Constrained Conformal Prediction via Linear Manifold Projection), a novel framework that achieves simultaneous coverage guarantees and zero physics violations for PINNs. Our specific objectives are:

1. **Develop a theoretical framework** that proves coverage preservation under linear manifold projection, establishing the mathematical foundations for physics-constrained conformal prediction.

2. **Design and implement the Linear-PCCP algorithm** that projects conformal prediction sets onto linear constraint manifolds derived from conservation laws, ensuring all predictions satisfy $Ax = b$ constraints exactly.

3. **Validate the framework empirically** on standard PINN benchmark PDEs (Burgers equation, Navier-Stokes equations, heat equation), demonstrating target coverage rates with zero physics violations.

4. **Compare Linear-PCCP against existing methods**, including soft-constraint CP and unconstrained CP, to quantify improvements in physics validity and interval efficiency.

### 1.3 Significance

This research addresses a critical gap at the intersection of machine learning and physical sciences. By providing the first hard-constraint uncertainty quantification framework with formal coverage guarantees, Linear-PCCP enables trustworthy PINN deployment in safety-critical applications. The significance extends in multiple directions:

- **For Physical Sciences:** Practitioners gain reliable uncertainty estimates that respect physical laws, enabling confident decision-making in high-stakes applications.
- **For Machine Learning:** The framework advances conformal prediction theory by establishing conditions under which geometric projections preserve coverage guarantees.
- **For Interdisciplinary Research:** Linear-PCCP exemplifies the bidirectional benefits of ML-physics integration, using physical insights to improve ML methodology.

## 2. Methodology

### 2.1 Problem Formulation

Consider a PINN trained to solve a PDE with solution $u(x, t)$ where $x \in \Omega \subset \mathbb{R}^d$ and $t \in [0, T]$. The PINN produces predictions $\hat{u}(x, t; \theta)$ parameterized by neural network weights $\theta$. We assume the physical system satisfies linear conservation constraints expressible as:

$$Ay = b$$

where $A \in \mathbb{R}^{m \times n}$ is the constraint matrix, $y \in \mathbb{R}^n$ represents the discretized solution vector, and $b \in \mathbb{R}^m$ encodes boundary conditions and source terms. Such constraints arise naturally from:

- **Mass conservation:** $\nabla \cdot (\rho \mathbf{v}) = 0$ discretized as linear equations
- **Momentum balance:** Linear momentum equations in incompressible flow
- **Boundary conditions:** Dirichlet conditions $u|_{\partial\Omega} = g$

Our goal is to construct prediction sets $\mathcal{C}(x, t)$ such that:
1. $\mathbb{P}(u(x,t) \in \mathcal{C}(x,t)) \geq 1 - \alpha$ (coverage guarantee)
2. $\forall \tilde{u} \in \mathcal{C}(x,t): A\tilde{u} = b$ (physics constraint satisfaction)

### 2.2 Linear-PCCP Algorithm

The Linear-PCCP framework consists of three main components: physics-aware nonconformity scoring, linear manifold projection, and calibrated prediction set construction.

#### 2.2.1 Physics-Aware Nonconformity Scoring

Given a calibration dataset $\mathcal{D}_{cal} = \{(x_i, t_i, u_i)\}_{i=1}^{n}$ with true solutions $u_i$ and PINN predictions $\hat{u}_i$, we define the physics-aware nonconformity score:

$$R(x_i, t_i, u_i) = \|u_i - \hat{u}_i\|_2 + \lambda \|A\hat{u}_i - b\|_2$$

where $\lambda > 0$ balances prediction accuracy and constraint violation. The first term measures prediction error, while the second penalizes physics violations in the base PINN predictions.

#### 2.2.2 Linear Manifold Projection

The key innovation of Linear-PCCP is projecting prediction sets onto the constraint manifold $\mathcal{M} = \{y : Ay = b\}$. For any prediction $\hat{u}$, the orthogonal projection onto $\mathcal{M}$ is:

$$\hat{u}_{proj} = P\hat{u} + A^{\dagger}b$$

where $P = I - A^T(AA^T)^{-1}A$ is the projection matrix onto the null space of $A$, and $A^{\dagger} = A^T(AA^T)^{-1}$ is the Moore-Penrose pseudoinverse. This projection satisfies:

$$A\hat{u}_{proj} = A(P\hat{u} + A^{\dagger}b) = AP\hat{u} + AA^{\dagger}b = 0 + b = b$$

ensuring exact constraint satisfaction.

**Theorem 1 (Coverage Preservation under Linear Projection):** Let $\{(X_i, Y_i)\}_{i=1}^{n+1}$ be exchangeable random variables. If $\mathcal{C}_{\alpha}$ is a conformal prediction set with coverage $1-\alpha$, then the projected set $\mathcal{C}_{\alpha}^{proj} = \{Py + A^{\dagger}b : y \in \mathcal{C}_{\alpha}\}$ maintains coverage $1-\alpha$ when the true solution lies on the constraint manifold.

*Proof Sketch:* The projection $\pi: y \mapsto Py + A^{\dagger}b$ is an affine transformation. Since the true solution $u^* \in \mathcal{M}$, we have $\pi(u^*) = u^*$. The exchangeability of calibration scores is preserved under deterministic transformations, and the coverage guarantee follows from standard conformal prediction theory applied to the projected space.

#### 2.2.3 Complete Algorithm

**Algorithm 1: Linear-PCCP**

**Input:** Trained PINN $f_\theta$, calibration set $\mathcal{D}_{cal}$, constraint matrix $A$, constraint vector $b$, coverage level $1-\alpha$

**Output:** Physics-constrained prediction sets $\mathcal{C}^{proj}(x, t)$

1. **Compute projection operator:**
   - $P \leftarrow I - A^T(AA^T)^{-1}A$
   - $c \leftarrow A^{\dagger}b = A^T(AA^T)^{-1}b$

2. **Project calibration predictions:**
   - For each $(x_i, t_i, u_i) \in \mathcal{D}_{cal}$:
     - $\hat{u}_i \leftarrow f_\theta(x_i, t_i)$
     - $\hat{u}_i^{proj} \leftarrow P\hat{u}_i + c$

3. **Compute projected nonconformity scores:**
   - $R_i \leftarrow \|u_i - \hat{u}_i^{proj}\|_2$ for $i = 1, \ldots, n$

4. **Calibrate coverage quantile:**
   - $\hat{q} \leftarrow \text{Quantile}(\{R_1, \ldots, R_n\}, \lceil(n+1)(1-\alpha)\rceil/n)$

5. **Construct prediction sets for test points:**
   - For test point $(x^*, t^*)$:
     - $\hat{u}^* \leftarrow f_\theta(x^*, t^*)$
     - $\hat{u}^{*,proj} \leftarrow P\hat{u}^* + c$
     - $\mathcal{C}^{proj}(x^*, t^*) \leftarrow \{y \in \mathcal{M} : \|y - \hat{u}^{*,proj}\|_2 \leq \hat{q}\}$

**Return:** $\mathcal{C}^{proj}$

### 2.3 Experimental Design

#### 2.3.1 Benchmark PDEs

We validate Linear-PCCP on three standard PINN benchmarks with increasing complexity:

1. **Burgers Equation (1D):**
$$\frac{\partial u}{\partial t} + u\frac{\partial u}{\partial x} = \nu \frac{\partial^2 u}{\partial x^2}$$
Linear constraints: Dirichlet boundary conditions $u(0,t) = u(1,t) = 0$

2. **Heat Equation (2D):**
$$\frac{\partial u}{\partial t} = \alpha \nabla^2 u$$
Linear constraints: Energy conservation $\int_\Omega u \, d\Omega = E_0$ (discretized)

3. **Navier-Stokes (2D, incompressible):**
$$\nabla \cdot \mathbf{v} = 0, \quad \frac{\partial \mathbf{v}}{\partial t} + (\mathbf{v} \cdot \nabla)\mathbf{v} = -\nabla p + \nu \nabla^2 \mathbf{v}$$
Linear constraints: Mass conservation (divergence-free condition)

#### 2.3.2 Data Collection

For each PDE:
- **Training data:** 10,000 collocation points for PINN training
- **Calibration data:** $n = 500$ points with ground truth solutions (from high-fidelity numerical solvers)
- **Test data:** 500 points for coverage and violation evaluation
- **Ground truth:** Spectral methods (Burgers), finite element (Heat), finite volume (Navier-Stokes)

#### 2.3.3 PINN Architecture

All experiments use a controlled architecture:
- **Network:** 4 hidden layers × 50 neurons, tanh activation
- **Training:** Adam optimizer, 50,000 epochs, learning rate $10^{-3}$
- **Physics loss weight:** $\lambda_{physics} = 1.0$

#### 2.3.4 Baselines

1. **Unconstrained CP:** Standard conformal prediction without physics constraints
2. **Soft-Constraint CP:** Physics violation as regularization in nonconformity score (Yu et al. 2025)
3. **Ensemble PINN:** Uncertainty from ensemble variance (no coverage guarantees)

#### 2.3.5 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Coverage Rate | $\frac{1}{N_{test}}\sum_{i=1}^{N_{test}} \mathbf{1}[u_i \in \mathcal{C}(x_i, t_i)]$ | $\geq 1-\alpha$ |
| Physics Violation Rate | $\frac{1}{N_{test}}\sum_{i=1}^{N_{test}} \mathbf{1}[\|A\hat{u}_i - b\|_2 > \epsilon]$ | $= 0\%$ |
| Interval Width | $\frac{1}{N_{test}}\sum_{i=1}^{N_{test}} \text{width}(\mathcal{C}(x_i, t_i))$ | Minimize |
| Computational Overhead | Wall-clock time ratio vs. unconstrained CP | $< 2\times$ |

#### 2.3.6 Statistical Analysis

- **Coverage validation:** One-sided binomial test, $H_0$: coverage $< 1-\alpha$, significance $\alpha_{stat} = 0.05$
- **Violation verification:** Exact count with tolerance $\epsilon = 10^{-10}$
- **Width comparison:** Paired t-test between Linear-PCCP and baselines
- **Multiple testing:** Bonferroni correction across PDEs and methods

### 2.4 Ablation Studies

To validate the causal mechanism, we conduct ablations:

1. **Projection ablation:** Compare coverage with/without manifold projection
2. **Score ablation:** Physics-aware vs. standard nonconformity scores
3. **Constraint complexity:** Vary number of constraints $m$ in $A$
4. **Calibration size:** Vary $n \in \{100, 250, 500, 1000\}$

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical analysis and preliminary investigations, we anticipate:

**Primary Outcome (P1):** Linear-PCCP will achieve target coverage rates ($\geq 1-\alpha$) while maintaining exactly zero physics violations across all benchmark PDEs. Specifically:
- Coverage: $90.2\% \pm 1.5\%$ for $\alpha = 0.10$, $95.1\% \pm 1.2\%$ for $\alpha = 0.05$
- Physics violations: $0\%$ (hard constraint by construction)

**Secondary Outcomes:**
- **P2:** Linear-PCCP will match soft-constraint CP coverage while achieving strictly better physics validity (0% vs. estimated 2-5% violations for soft constraints)
- **P3:** Projected intervals will be 10-20% narrower than unconstrained CP due to constraint-induced dimensionality reduction

**Computational Performance:** Projection overhead of $O(m^2n + m^3)$ will add approximately 50% computational cost, acceptable for offline UQ applications.

### 3.2 Scientific Impact

**For Uncertainty Quantification:** Linear-PCCP establishes a new paradigm for physics-constrained UQ, demonstrating that hard constraints and coverage guarantees are compatible. This opens research directions for nonlinear constraint handling and adaptive constraint selection.

**For Physics-Informed Machine Learning:** By providing rigorous UQ, Linear-PCCP addresses a key barrier to PINN adoption in safety-critical applications. The framework can be integrated with existing PINN architectures without retraining.

**For Conformal Prediction Theory:** Our coverage preservation theorem under linear projection extends CP theory to constrained prediction spaces, with potential applications beyond physics to any domain with linear constraints.

### 3.3 Broader Impact

**Trustworthy AI for Science:** Linear-PCCP contributes to the broader goal of trustworthy AI in scientific applications by providing predictions that are both statistically reliable and physically meaningful.

**Interdisciplinary Bridge:** The framework exemplifies productive ML-physics collaboration, using physical insights (conservation laws) to improve ML methodology (conformal prediction).

**Practical Deployment:** By eliminating physics violations, Linear-PCCP enables PINN deployment in regulated industries (nuclear, aerospace, medical devices) where physical validity is a certification requirement.

### 3.4 Limitations and Future Work

**Current Limitations:**
- Restricted to linear constraints; nonlinear conservation laws require extensions
- Requires explicit constraint matrix $A$; implicit constraints need reformulation
- Computational scaling limits applicability to very high-dimensional systems

**Future Directions:**
- Extend to nonlinear constraints via iterative projection or constraint linearization
- Develop adaptive methods for constraint discovery from data
- Integrate with real-time inference systems for online UQ

In conclusion, Linear-PCCP represents a significant advance in physics-constrained uncertainty quantification, providing the theoretical foundations and practical algorithms for trustworthy PINN deployment in safety-critical physical science applications.