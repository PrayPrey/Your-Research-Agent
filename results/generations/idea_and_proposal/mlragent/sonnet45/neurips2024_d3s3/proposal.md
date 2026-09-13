# Research Proposal: Adaptive Multi-Fidelity Neural Surrogates with Uncertainty-Driven Sampling

## 1. Title

**Adaptive Multi-Fidelity Neural Surrogates with Uncertainty-Driven Sampling for Efficient Scientific Simulation**

## 2. Introduction

### Background

Scientific discovery increasingly relies on computationally expensive simulation-based investigations across domains ranging from climate modeling and molecular dynamics to electromagnetic wave propagation and materials design. High-fidelity simulations—though accurate—often require hours to days of computational time on specialized hardware, creating bottlenecks in inverse design, uncertainty quantification, and real-time control applications. Conversely, low-fidelity simulations provide rapid approximations but may introduce unacceptable errors that compromise downstream decisions.

Recent advances in neural operators, particularly Fourier Neural Operators (FNOs) and their variants, have demonstrated remarkable success in learning solution operators for parametric partial differential equations (PDEs). These data-driven surrogates can achieve speedups of several orders of magnitude compared to traditional numerical solvers. However, existing approaches face critical limitations: (1) single-fidelity surrogates trained exclusively on high-fidelity data remain expensive to construct, requiring extensive simulation campaigns; (2) multi-fidelity methods with fixed allocation strategies fail to adapt to spatially varying complexity and uncertainty; (3) most neural surrogates lack principled uncertainty quantification, limiting their trustworthiness in safety-critical applications.

The literature reveals emerging solutions to individual aspects of this challenge. DINOZAUR demonstrates efficient Bayesian neural operators with calibrated uncertainty estimates, while Multi-Fidelity Laplace Neural Operators (MF-LNOs) show how to exploit correlations between fidelity levels. However, no existing framework dynamically adapts fidelity selection based on learned uncertainty during inference, potentially wasting computational resources on unnecessary high-fidelity queries while under-sampling critical regions.

### Research Objectives

This research proposes a unified framework for **Adaptive Multi-Fidelity Neural Surrogates (AMFNS)** that addresses three primary objectives:

1. **Develop hierarchical neural operator architectures** that efficiently represent simulation data across multiple fidelity levels with knowledge transfer mechanisms.

2. **Design uncertainty-aware routing mechanisms** that dynamically select appropriate fidelity levels for each query based on epistemic uncertainty estimates and cost-accuracy trade-offs.

3. **Implement active learning strategies** that intelligently acquire high-fidelity training data in regions of high uncertainty, progressively refining the surrogate model.

### Significance

This research addresses fundamental challenges in simulation-based scientific discovery with implications across multiple domains:

- **Computational Efficiency**: By intelligently routing most queries to low-fidelity surrogates and reserving expensive high-fidelity evaluations for uncertain regions, we anticipate 10-100× speedup in simulation campaigns compared to uniform high-fidelity approaches.

- **Uncertainty Quantification**: Principled epistemic uncertainty estimates enable risk-aware decision-making in safety-critical applications such as nuclear fusion control, drug discovery, and autonomous vehicle testing.

- **Resource Optimization**: Adaptive data acquisition strategies reduce the number of expensive high-fidelity simulations required to achieve target accuracy levels, democratizing access to high-quality surrogate models.

- **Broad Applicability**: The framework's domain-agnostic design enables deployment across physics simulations, climate modeling, molecular dynamics, and electromagnetic design problems.

## 3. Methodology

### 3.1 Problem Formulation

Consider a parametric simulation problem where we seek to approximate a solution operator $\mathcal{G}: \mathcal{X} \rightarrow \mathcal{Y}$ mapping input parameters/initial conditions $x \in \mathcal{X}$ to solution fields $y \in \mathcal{Y}$. We assume access to simulation engines at $L$ different fidelity levels, where fidelity $\ell \in \{1, ..., L\}$ provides approximation $\mathcal{G}_\ell$ with computational cost $c_\ell$ and accuracy characterized by error $\epsilon_\ell$, such that $c_1 < c_2 < ... < c_L$ and $\epsilon_1 > \epsilon_2 > ... > \epsilon_L$.

Our goal is to construct a surrogate $\hat{\mathcal{G}}_\theta$ parametrized by neural network weights $\theta$ that:
- Approximates the highest fidelity operator $\mathcal{G}_L$ with bounded error $\|\hat{\mathcal{G}}_\theta - \mathcal{G}_L\| < \delta$
- Minimizes total computational cost during training and inference
- Provides calibrated uncertainty estimates $\sigma^2(x)$ for epistemic uncertainty

### 3.2 Hierarchical Multi-Fidelity Neural Operators

#### Architecture Design

We construct a hierarchical family of neural operators $\{\mathcal{F}_\ell\}_{\ell=1}^L$ based on Fourier Neural Operators with multi-fidelity coupling:

**Base Low-Fidelity Model**: The lowest fidelity network $\mathcal{F}_1$ consists of:
$$\mathcal{F}_1(x) = \mathcal{Q} \circ \mathcal{L}_K^{(1)} \circ ... \circ \mathcal{L}_1^{(1)} \circ \mathcal{P}(x)$$

where $\mathcal{P}$ is a lifting operator projecting inputs to higher dimensions, $\mathcal{L}_k^{(1)}$ are Fourier layers, and $\mathcal{Q}$ is a projection operator. Each Fourier layer is defined as:

$$\mathcal{L}_k(v)(x) = \sigma(W_k v(x) + \mathcal{K}_k(v)(x))$$

where $W_k$ is a local linear transformation and $\mathcal{K}_k$ is a spectral convolution:

$$\mathcal{K}_k(v)(x) = \mathcal{F}^{-1}(R_k \cdot \mathcal{F}(v))(x)$$

with $R_k$ being learnable weights in Fourier space and $\mathcal{F}$ denoting the Fourier transform.

**Multi-Fidelity Correction Networks**: For fidelity levels $\ell > 1$, we employ additive correction architecture:

$$\mathcal{F}_\ell(x) = \mathcal{F}_{\ell-1}(x) + \Delta_\ell(x, \mathcal{F}_{\ell-1}(x))$$

where $\Delta_\ell$ is a correction network that takes both the input $x$ and the lower-fidelity prediction as inputs, learning the residual discrepancy between fidelities.

#### Knowledge Distillation

To facilitate efficient training with limited high-fidelity data, we employ progressive knowledge distillation:

$$\mathcal{L}_{\text{distill}}^{(\ell)} = \mathbb{E}_{x \sim \mathcal{D}_{\ell-1}} \left[\|\mathcal{F}_\ell(x) - \mathcal{G}_\ell(x)\|^2 + \lambda_{\text{KD}} \|\mathcal{F}_\ell(x) - \mathcal{F}_{\ell-1}(x)\|^2\right]$$

where $\mathcal{D}_{\ell-1}$ is the dataset at fidelity $\ell-1$ and $\lambda_{\text{KD}}$ balances fitting accuracy and consistency across fidelities.

### 3.3 Bayesian Uncertainty Quantification

#### Ensemble-Based Epistemic Uncertainty

We adopt a variational Bayesian approach using Monte Carlo dropout and deep ensembles to estimate epistemic uncertainty. For each fidelity level $\ell$, we train an ensemble of $M$ models $\{\mathcal{F}_\ell^{(m)}\}_{m=1}^M$ and compute:

$$\mu_\ell(x) = \frac{1}{M} \sum_{m=1}^M \mathcal{F}_\ell^{(m)}(x)$$

$$\sigma^2_\ell(x) = \frac{1}{M} \sum_{m=1}^M \|\mathcal{F}_\ell^{(m)}(x) - \mu_\ell(x)\|^2$$

where $\sigma^2_\ell(x)$ quantifies pointwise epistemic uncertainty at fidelity $\ell$.

#### Calibrated Uncertainty via Temperature Scaling

To ensure calibrated uncertainty estimates, we apply temperature scaling post-hoc:

$$\tilde{\sigma}^2_\ell(x) = T_\ell \cdot \sigma^2_\ell(x)$$

where temperature parameters $T_\ell$ are optimized on a held-out validation set by minimizing the negative log-likelihood under a Gaussian assumption.

### 3.4 Uncertainty-Aware Routing Mechanism

#### Meta-Network Architecture

We introduce a lightweight routing meta-network $\mathcal{R}_\phi$ parametrized by weights $\phi$ that predicts the optimal fidelity level for each query:

$$\ell^*(x) = \mathcal{R}_\phi(x, \{\sigma^2_\ell(x)\}_{\ell=1}^L)$$

The input to $\mathcal{R}_\phi$ consists of:
1. Encoded input features $\mathcal{E}(x)$ using a small encoder network
2. Uncertainty estimates from all fidelity levels $\{\sigma^2_\ell(x)\}_{\ell=1}^L$
3. Optional contextual information (e.g., computational budget remaining)

#### Cost-Accuracy Objective

The routing network is trained to minimize an expected cost-accuracy trade-off:

$$\mathcal{L}_{\text{route}} = \mathbb{E}_{x \sim \mathcal{D}} \left[\alpha \cdot c_{\ell^*(x)} + (1-\alpha) \cdot \|\mathcal{F}_{\ell^*(x)}(x) - \mathcal{G}_L(x)\|^2\right]$$

where $\alpha \in [0,1]$ balances computational cost and prediction accuracy. This hyperparameter can be adjusted based on application requirements.

#### Decision Policy

For inference, we implement a threshold-based policy that routes queries based on uncertainty:

$$\ell^*(x) = \begin{cases}
1 & \text{if } \sigma^2_1(x) < \tau_1 \\
\ell & \text{if } \tau_{\ell-1} \leq \sigma^2_{\ell-1}(x) < \tau_\ell \\
L & \text{if } \sigma^2_{L-1}(x) \geq \tau_{L-1}
\end{cases}$$

where thresholds $\{\tau_\ell\}$ are learned during meta-network training or set based on error tolerance requirements.

### 3.5 Active Learning Loop

#### Acquisition Function

To efficiently expand the training dataset, we employ an acquisition function that identifies informative samples for high-fidelity evaluation:

$$a(x) = \beta_1 \cdot \sigma^2_L(x) + \beta_2 \cdot \max_{\ell < L} |\mathcal{F}_\ell(x) - \mathcal{F}_L(x)| + \beta_3 \cdot d(x, \mathcal{D}_L)$$

where:
- $\sigma^2_L(x)$ represents epistemic uncertainty at the highest fidelity
- $|\mathcal{F}_\ell(x) - \mathcal{F}_L(x)|$ measures inter-fidelity disagreement
- $d(x, \mathcal{D}_L)$ quantifies distance to existing high-fidelity samples in input space
- $\{\beta_i\}$ are weighting coefficients

#### Batch Selection Strategy

At each active learning iteration $t$, we select a batch $\mathcal{B}_t$ of $B$ samples by solving:

$$\mathcal{B}_t = \arg\max_{|\mathcal{B}|=B} \left[\sum_{x \in \mathcal{B}} a(x) - \gamma \sum_{x, x' \in \mathcal{B}, x \neq x'} \text{sim}(x, x')\right]$$

where $\text{sim}(x, x')$ measures similarity between samples to encourage diversity, and $\gamma$ controls the diversity-exploitation trade-off.

#### Training Algorithm

The complete adaptive training procedure is:

**Algorithm 1: Adaptive Multi-Fidelity Training**

1. **Initialize**: 
   - Collect initial datasets $\mathcal{D}_\ell^{(0)}$ for all fidelities
   - Train base models $\{\mathcal{F}_\ell\}$ on initial data
   
2. **For** $t = 1$ to $T_{\text{max}}$:
   
   a. Compute uncertainty estimates $\sigma^2_\ell(x)$ for candidate pool $\mathcal{X}_{\text{pool}}$
   
   b. Select batch $\mathcal{B}_t$ using acquisition function
   
   c. Query high-fidelity simulator: $\mathcal{D}_L^{(t)} = \mathcal{D}_L^{(t-1)} \cup \{(x, \mathcal{G}_L(x)) : x \in \mathcal{B}_t\}$
   
   d. Update highest fidelity model $\mathcal{F}_L$ via fine-tuning
   
   e. Update routing network $\mathcal{R}_\phi$ with new data
   
   f. **If** $t \mod k_{\text{retrain}} = 0$: Retrain all fidelity models from scratch
   
3. **Return**: Trained models $\{\mathcal{F}_\ell\}$ and routing network $\mathcal{R}_\phi$

### 3.6 Data Collection and Experimental Design

#### Benchmark Domains

We will validate AMFNS across three representative scientific simulation domains:

1. **Fluid Dynamics**: 2D Navier-Stokes equations with varying Reynolds numbers
   - Low fidelity: Coarse mesh (64×64), first-order schemes
   - Medium fidelity: Moderate mesh (128×128), second-order schemes  
   - High fidelity: Fine mesh (256×256), high-order schemes

2. **Molecular Dynamics**: Energy prediction for small organic molecules
   - Low fidelity: Semi-empirical methods (PM6, AM1)
   - Medium fidelity: Density Functional Theory (DFT) with modest basis sets
   - High fidelity: Coupled-cluster methods or large basis DFT

3. **Electromagnetic Wave Propagation**: Scattering from complex geometries
   - Low fidelity: Analytical approximations or simplified geometries
   - Medium fidelity: Finite-difference time-domain with moderate resolution
   - High fidelity: High-order finite element methods

#### Dataset Construction

For each domain, we will generate:
- **Low-fidelity dataset**: 10,000-50,000 samples covering the parameter space
- **Medium-fidelity dataset**: 1,000-5,000 samples with strategic sampling
- **High-fidelity dataset**: Initial 100-500 samples, expanded via active learning to 500-2,000 samples
- **Test set**: 500-1,000 high-fidelity samples for evaluation

### 3.7 Evaluation Metrics

#### Prediction Accuracy

- **Relative L2 Error**: $\epsilon_{\text{rel}} = \frac{\|\hat{\mathcal{G}}(x) - \mathcal{G}_L(x)\|_2}{\|\mathcal{G}_L(x)\|_2}$
- **Mean Absolute Error** (MAE) for quantities of interest
- **R² Score** for correlation analysis

#### Computational Efficiency

- **Speedup Factor**: $S = \frac{\sum_{i=1}^N c_L}{\sum_{i=1}^N c_{\ell^*(x_i)}}$ over $N$ test queries
- **Query Distribution**: Histogram of fidelity levels selected
- **Amortized Cost**: Total training cost normalized by test set performance

#### Uncertainty Quantification

- **Calibration Error**: Expected Calibration Error (ECE) measuring reliability of uncertainty estimates
- **Sharpness**: Average predictive uncertainty $\bar{\sigma}^2 = \frac{1}{N}\sum_{i=1}^N \sigma^2(x_i)$
- **Coverage**: Fraction of true values within predicted confidence intervals

#### Active Learning Efficiency

- **Sample Efficiency Curve**: Test error vs. number of high-fidelity samples
- **Comparison to Baselines**: Random sampling, uncertainty-only, and fixed multi-fidelity strategies

### 3.8 Baseline Comparisons

We will compare AMFNS against:

1. **Single-Fidelity Neural Operators**: Standard FNO trained exclusively on high-fidelity data
2. **Fixed Multi-Fidelity Models**: MF-LNO and MF-DNN with predetermined data allocation
3. **Non-Adaptive Routing**: Using only low-fidelity predictions with high-fidelity correction on fixed subsets
4. **Traditional Multi-Fidelity Methods**: Co-kriging and multi-fidelity Monte Carlo
5. **Active Learning Baselines**: Random acquisition and pure uncertainty sampling without fidelity adaptation

## 4. Expected Outcomes & Impact

### Expected Outcomes

#### Quantitative Improvements

1. **Computational Speedup**: We anticipate 10-100× reduction in total computational cost compared to uniform high-fidelity approaches while maintaining relative errors below 5% on benchmark problems. The speedup will vary by domain, with greater gains in problems exhibiting smooth parameter-to-solution mappings.

2. **Sample Efficiency**: Active learning strategies are expected to reduce the number of required high-fidelity samples by 50-80% compared to random sampling for achieving equivalent accuracy, democratizing access to high-quality surrogate models in resource-constrained settings.

3. **Calibrated Uncertainty**: Uncertainty estimates should achieve Expected Calibration Error (ECE) below 0.05 and 95% coverage of true values within predicted confidence intervals, enabling trustworthy deployment in safety-critical applications.

4. **Adaptive Efficiency**: The routing mechanism should allocate 60-80% of queries to low-fidelity surrogates while reserving high-fidelity evaluations for truly uncertain regions, demonstrating intelligent resource allocation.

#### Methodological Contributions

1. **Unified Framework**: A comprehensive open-source implementation combining hierarchical neural operators, Bayesian uncertainty quantification, adaptive routing, and active learning in a single cohesive framework.

2. **Theoretical Insights**: Analysis of approximation error bounds for multi-fidelity neural operators and convergence guarantees for the adaptive training procedure under regularity assumptions.

3. **Practical Guidelines**: Domain-specific recommendations for fidelity level definition, hyperparameter selection, and deployment strategies based on empirical evaluation across diverse simulation problems.

### Scientific Impact

#### Enabling Applications

1. **Accelerated Inverse Design**: In molecular discovery and materials design, AMFNS will enable rapid exploration of vast chemical spaces by efficiently querying expensive quantum chemistry calculations only when necessary, potentially accelerating drug discovery and materials optimization campaigns.

2. **Real-Time Control**: For applications like nuclear fusion plasma control or autonomous vehicle testing, the framework's ability to provide fast predictions with uncertainty quantification enables model-predictive control strategies that were previously computationally infeasible.

3. **Climate Model Emulation**: Multi-fidelity surrogates can bridge different climate model resolutions, enabling uncertainty quantification in long-term climate projections while managing computational resources efficiently.

4. **Data Assimilation**: In weather forecasting and oceanography, adaptive fidelity selection can optimize the computational budget for ensemble forecasting, allocating high-fidelity runs to uncertain weather regimes.

#### Broader Impacts

1. **Democratization of Simulation**: By reducing computational requirements, AMFNS lowers barriers for researchers and organizations without access to large-scale computing infrastructure, promoting equity in scientific discovery.

2. **Trustworthy AI for Science**: Principled uncertainty quantification addresses a critical gap in neural surrogates, increasing trust and adoption among domain scientists who require reliability guarantees.

3. **Interdisciplinary Collaboration**: The framework's domain-agnostic design facilitates knowledge transfer across scientific disciplines, potentially revealing common patterns in multi-scale physical phenomena.

4. **Educational Resources**: Open-source implementation with tutorials will serve as educational material for training the next generation of researchers at the intersection of machine learning and scientific computing.

### Limitations and Future Directions

#### Known Limitations

1. **Fidelity Hierarchy Assumption**: The framework assumes a clear hierarchy of simulation fidelities, which may not hold in all domains where different solvers provide incomparable trade-offs.

2. **Training Overhead**: Initial ensemble training across multiple fidelities requires non-trivial computational investment, though this is amortized over many inference queries.

3. **Extrapolation Challenges**: Like all data-driven methods, the approach may struggle with parameters far outside the training distribution, requiring careful monitoring of uncertainty in deployment.

#### Future Extensions

1. **Online Adaptation**: Develop continual learning strategies that update surrogate models in real-time as new simulation data becomes available during deployment.

2. **Multi-Task Learning**: Extend the framework to simultaneously learn surrogates for multiple related simulation tasks, sharing representations across problems.

3. **Physics-Informed Priors**: Incorporate known physical constraints and conservation laws as inductive biases to improve data efficiency and extrapolation capabilities.

4. **Hardware-Aware Optimization**: Co-design routing strategies with heterogeneous computing resources (CPUs, GPUs, TPUs) to maximize wall-clock time efficiency rather than pure computational cost.

### Conclusion

The proposed Adaptive Multi-Fidelity Neural Surrogates framework addresses fundamental challenges in simulation-based scientific discovery by intelligently balancing accuracy, computational cost, and uncertainty quantification. Through hierarchical neural operators, uncertainty-aware routing, and active learning, AMFNS promises to accelerate simulation campaigns across diverse domains while providing the reliability guarantees necessary for safety-critical applications. Successful development of this framework will contribute both methodological advances in neural operator learning and practical tools that empower researchers across physics, chemistry, climate science, and engineering to tackle previously intractable problems at the intersection of simulation and machine learning.