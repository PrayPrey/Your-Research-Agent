# Research Proposal

## Title
Uncertainty-Aware Neural Surrogates with Adaptive Fidelity Switching for Multi-Scale Physical Simulations

---

## 1. Introduction

### Background

Scientific simulation lies at the heart of modern discovery across physics, chemistry, climate science, and engineering. High-fidelity numerical solvers—such as finite element methods for structural mechanics or direct numerical simulation for turbulent flows—provide accurate predictions but often require prohibitive computational resources. A single high-resolution turbulence simulation can consume millions of CPU hours, creating bottlenecks in design optimization, uncertainty quantification, and real-time control applications.

Neural surrogates, particularly neural operators like Fourier Neural Operators (FNOs) and DeepONets, have emerged as transformative tools that learn mappings between function spaces, offering speedups of 1000× or more over traditional solvers. However, these data-driven models suffer from a critical limitation: they fail silently when encountering out-of-distribution (OOD) inputs or physical regimes not well-represented in training data. Unlike traditional solvers that provide convergence diagnostics, neural surrogates typically produce confident-looking predictions even when grossly inaccurate. This unreliability fundamentally limits their deployment in safety-critical applications and discovery-driven science where encountering unknown physics is the goal rather than an exception.

Recent advances in uncertainty quantification (UQ) for neural networks offer partial solutions. Bayesian approaches, ensemble methods, and spectral normalization techniques can provide epistemic uncertainty estimates. Concurrently, multi-fidelity methods have demonstrated that intelligent combination of cheap low-fidelity models with expensive high-fidelity simulations can achieve accuracy at reduced cost. However, existing approaches typically treat these as separate problems: UQ methods provide uncertainty without actionable remediation, while multi-fidelity methods assume static model hierarchies without adaptive switching based on local solution characteristics.

### Research Objectives

This research proposes a unified framework—**Adaptive Fidelity Neural Surrogates (AFNS)**—that bridges uncertainty quantification and multi-fidelity simulation through three integrated innovations:

1. **Calibrated Epistemic Uncertainty**: Develop ensemble neural operators with spectral normalization that provide reliable, well-calibrated uncertainty estimates across diverse physical regimes.

2. **Learned Adaptive Switching**: Design a lightweight gating network that predicts surrogate reliability in real-time based on uncertainty signals and local solution features, enabling intelligent routing between neural surrogates and traditional solvers.

3. **Differentiable Hybrid Integration**: Construct a seamless, end-to-end differentiable framework that maintains gradient flow through the switching mechanism, enabling gradient-based optimization and inverse problem solving.

### Significance

This research addresses fundamental challenges at the intersection of machine learning and scientific computing. By creating surrogates that "know when they don't know" and can gracefully defer to trusted solvers, we enable:

- **Trustworthy Acceleration**: Practitioners can confidently deploy neural surrogates knowing that accuracy is bounded even in novel regimes.
- **Efficient Discovery**: The framework automatically allocates computational resources where needed, enabling exploration of parameter spaces with heterogeneous difficulty.
- **Differentiable Science**: Maintaining end-to-end differentiability enables gradient-based inverse problems, design optimization, and data assimilation with uncertainty-aware forward models.

---

## 2. Methodology

### 2.1 Problem Formulation

Consider a parametric partial differential equation (PDE) system:

$$\mathcal{L}_\theta[u](x, t) = f(x, t), \quad x \in \Omega, t \in [0, T]$$

where $\mathcal{L}_\theta$ is a differential operator parameterized by physical parameters $\theta$, $u$ is the solution field, and $f$ represents forcing terms. Our goal is to construct a hybrid solver $\mathcal{H}$ that approximates the solution operator $\mathcal{G}: (\theta, f, u_0) \mapsto u$ while providing calibrated uncertainty estimates and bounded approximation error.

### 2.2 Component 1: Ensemble Neural Operators with Calibrated Uncertainty

#### Architecture

We employ an ensemble of $M$ Fourier Neural Operators (FNOs), each mapping input functions to solution fields. For input $a \in \mathcal{A}$ (concatenated initial conditions, boundary conditions, and parameters), each ensemble member $\mathcal{F}_m$ produces:

$$\hat{u}_m = \mathcal{F}_m(a) = Q \circ \sigma(W_L + K_L) \circ \cdots \circ \sigma(W_1 + K_1) \circ P(a)$$

where $P$ and $Q$ are lifting and projection operators, $W_l$ are local linear transforms, and $K_l$ are Fourier integral operators:

$$K_l[v](x) = \mathcal{F}^{-1}\left(R_l \cdot \mathcal{F}[v]\right)(x)$$

with learnable spectral weights $R_l$.

#### Spectral Normalization for Calibration

To ensure well-calibrated uncertainty, we apply spectral normalization to all weight matrices, constraining the Lipschitz constant of each layer:

$$\tilde{W}_l = \frac{W_l}{\sigma_1(W_l)}$$

where $\sigma_1(W_l)$ is the largest singular value, computed via power iteration. This prevents overconfident predictions in OOD regions by controlling the rate at which outputs change with inputs.

#### Uncertainty Estimation

The ensemble provides two uncertainty measures at each spatial location $x$:

**Predictive Mean:**
$$\bar{u}(x) = \frac{1}{M}\sum_{m=1}^{M}\hat{u}_m(x)$$

**Epistemic Uncertainty (Ensemble Variance):**
$$\sigma^2_{\text{epi}}(x) = \frac{1}{M-1}\sum_{m=1}^{M}(\hat{u}_m(x) - \bar{u}(x))^2$$

We also compute spectral uncertainty by analyzing disagreement across Fourier modes:

$$\sigma^2_{\text{spectral}}(k) = \text{Var}_m\left[\mathcal{F}[\hat{u}_m](k)\right]$$

which captures uncertainty in different spatial scales.

#### Training Objective

Each ensemble member is trained with diversity-promoting regularization:

$$\mathcal{L}_{\text{ensemble}} = \frac{1}{M}\sum_{m=1}^{M}\mathcal{L}_{\text{data}}(\hat{u}_m, u^*) + \lambda_{\text{div}}\mathcal{L}_{\text{diversity}} + \lambda_{\text{phys}}\mathcal{L}_{\text{physics}}$$

where $\mathcal{L}_{\text{data}}$ is the supervised loss against high-fidelity solutions $u^*$, $\mathcal{L}_{\text{diversity}}$ encourages ensemble disagreement through negative correlation, and $\mathcal{L}_{\text{physics}}$ enforces PDE residuals.

### 2.3 Component 2: Gating Network for Reliability Prediction

#### Input Features

The gating network $G_\phi$ receives a feature vector $z$ constructed from:

1. **Uncertainty signals**: $\sigma_{\text{epi}}(x)$, $\sigma_{\text{spectral}}(k)$
2. **Solution characteristics**: Local gradients $\|\nabla\bar{u}\|$, curvature $\|\nabla^2\bar{u}\|$
3. **Physical indicators**: Reynolds number, Mach number, or domain-specific quantities
4. **Historical context**: Uncertainty trends from previous timesteps

#### Architecture and Output

The gating network is a lightweight MLP:

$$G_\phi(z) = \text{sigmoid}(W_3 \cdot \text{ReLU}(W_2 \cdot \text{ReLU}(W_1 \cdot z)))$$

outputting a reliability score $r \in [0, 1]$ for each spatial region or the entire domain.

#### Training the Gating Network

We generate training data by computing actual surrogate errors $e = \|\hat{u} - u^*\|$ across diverse test cases. The gating network is trained to predict whether error exceeds threshold $\tau$:

$$\mathcal{L}_{\text{gate}} = \text{BCE}(G_\phi(z), \mathbb{1}[e < \tau]) + \lambda_{\text{cost}}\mathcal{L}_{\text{cost}}$$

where $\mathcal{L}_{\text{cost}}$ penalizes unnecessary switching to encourage surrogate usage when reliable.

### 2.4 Component 3: Differentiable Adaptive Switching

#### Soft Switching Mechanism

To maintain differentiability, we employ soft switching with temperature-controlled interpolation:

$$u_{\text{hybrid}}(x) = \alpha(x) \cdot \bar{u}_{\text{neural}}(x) + (1 - \alpha(x)) \cdot u_{\text{solver}}(x)$$

where the switching coefficient $\alpha$ is computed from reliability scores:

$$\alpha(x) = \sigma\left(\frac{r(x) - r_{\text{thresh}}}{\tau_{\text{temp}}}\right)$$

Here $\sigma$ is the sigmoid function, $r_{\text{thresh}}$ is a learned threshold, and $\tau_{\text{temp}}$ is a temperature parameter that anneals during training to approach hard switching.

#### Coarse-Grid Solver Integration

When $\alpha < 1$, we invoke a coarse-grid traditional solver $\mathcal{S}_{\text{coarse}}$ operating at reduced resolution. This solver is wrapped with differentiable physics layers:

$$u_{\text{solver}} = \mathcal{I}_{\text{fine}}\left(\mathcal{S}_{\text{coarse}}(\mathcal{I}_{\text{coarse}}(a))\right)$$

where $\mathcal{I}_{\text{fine}}$ and $\mathcal{I}_{\text{coarse}}$ are differentiable interpolation operators. Gradients flow through implicit differentiation:

$$\frac{\partial u_{\text{solver}}}{\partial a} = -\left(\frac{\partial \mathcal{R}}{\partial u}\right)^{-1}\frac{\partial \mathcal{R}}{\partial a}$$

where $\mathcal{R}$ is the discretized residual.

### 2.5 Experimental Design

#### Benchmark Problems

**Turbulent Flow (2D Navier-Stokes):**
- Reynolds numbers: $Re \in [1000, 100000]$
- Training: $Re \in [1000, 10000]$; OOD testing: $Re \in [10000, 100000]$
- High-fidelity: 512×512 pseudo-spectral solver
- Coarse solver: 64×64 finite volume

**Molecular Dynamics (Lennard-Jones Clusters):**
- System sizes: 100-10000 atoms
- Temperature range: solid to liquid phases
- High-fidelity: Full MD with 1fs timesteps
- Coarse solver: Coarse-grained model with 100fs steps

#### Evaluation Metrics

1. **Accuracy**: Relative $L^2$ error $\epsilon = \|u_{\text{hybrid}} - u^*\|_2 / \|u^*\|_2$

2. **Uncertainty Calibration**: Expected Calibration Error (ECE) measuring alignment between predicted uncertainty and actual errors

3. **Computational Efficiency**: Speedup ratio $S = T_{\text{full-fidelity}} / T_{\text{hybrid}}$

4. **Switching Accuracy**: Precision/recall of switching decisions against oracle optimal switching

5. **Bounded Error Guarantee**: Percentage of predictions where $\epsilon < \epsilon_{\text{max}}$ for specified bound

#### Baseline Comparisons

- Pure neural surrogate (FNO ensemble without switching)
- Fixed multi-fidelity (static allocation without adaptive switching)
- Uncertainty-thresholded switching (hard threshold without learned gating)
- Probabilistic Neural Operators (PNOs) from recent literature

---

## 3. Expected Outcomes & Impact

### Quantitative Targets

We anticipate the AFNS framework will achieve:

1. **10-50× Speedup** over full-fidelity solvers while maintaining relative errors below 5% across test distributions, including OOD regimes.

2. **ECE < 0.05** for uncertainty calibration, ensuring predicted confidence aligns with actual accuracy.

3. **>95% Bounded Error Compliance** where the hybrid system keeps errors below user-specified thresholds through appropriate switching.

4. **<5% Computational Overhead** from the gating network relative to pure surrogate inference.

### Scientific Impact

This research directly addresses the trustworthiness gap preventing neural surrogate adoption in high-stakes scientific applications. By providing uncertainty-bounded predictions with graceful degradation to traditional solvers, we enable:

- **Accelerated Scientific Discovery**: Researchers can explore vast parameter spaces with confidence that accuracy degradation will be automatically detected and mitigated.

- **Robust Design Optimization**: Engineers can perform gradient-based optimization through the hybrid framework, knowing that gradient estimates remain reliable across the optimization trajectory.

- **Uncertainty-Aware Data Assimilation**: The calibrated uncertainty enables proper weighting in Bayesian inference and ensemble methods for state estimation.

### Broader Implications

The adaptive fidelity paradigm extends beyond the specific instantiation proposed here. The framework establishes design patterns for:

- Integrating emerging ML accelerators with legacy simulation codes
- Building hierarchical surrogate systems across multiple fidelity levels
- Developing self-aware AI systems for scientific computing that can recognize and respond to their limitations

By demonstrating success on turbulent flows and molecular dynamics—two domains with notoriously difficult multi-scale physics—we establish applicability to the broader scientific simulation landscape including climate modeling, materials design, and fusion energy research.

---

## 4. Conclusion

This proposal presents a comprehensive framework for uncertainty-aware neural surrogates with adaptive fidelity switching. By integrating calibrated ensemble uncertainty, learned reliability prediction, and differentiable hybrid computation, AFNS addresses the fundamental trust barrier limiting neural surrogate deployment in scientific applications. The proposed methodology builds on recent advances in neural operators, uncertainty quantification, and multi-fidelity methods while introducing novel contributions in their integration. Successful execution will yield both practical tools for accelerated simulation and foundational insights into building reliable AI systems for scientific discovery.