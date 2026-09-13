# Physics-Guided Active Learning for Sample-Efficient Simulation-Based Inference

## 1. Title

**Physics-Guided Active Learning for Sample-Efficient Simulation-Based Inference in Expensive PDE-Governed Simulators**

## 2. Introduction

### 2.1 Background

Bayesian parameter inference in expensive PDE-governed simulators represents a critical bottleneck in modern scientific computing and engineering. Applications spanning computational fluid dynamics (CFD), plasma physics, structural mechanics, and climate modeling require quantifying uncertainty in model parameters to enable risk-aware decision-making. However, traditional Markov Chain Monte Carlo (MCMC) methods are computationally prohibitive when individual simulations require minutes to hours, necessitating simulation-based inference (SBI) approaches that learn surrogate models of the likelihood or posterior distribution.

Recent advances in neural density estimation have enabled amortized SBI methods that can perform Bayesian inference with substantially fewer simulator evaluations than MCMC. Sequential Neural Posterior Estimation (SNPE) and related techniques use normalizing flows to learn posterior distributions from simulation data, reducing computational requirements from millions to tens of thousands of simulations. However, even 10,000-50,000 simulations remain prohibitively expensive for many critical applications. For instance, calibrating fusion reactor models using BOUT++ simulations requires approximately 70 days of continuous computation, while aerodynamic design optimization with OpenFOAM CFD simulations can take weeks, preventing rapid prototyping and uncertainty quantification in time-sensitive engineering contexts.

Two parallel research directions offer promising solutions to this bottleneck, yet remain largely disconnected in the literature. First, **active learning for SBI** strategically selects which simulations to run based on information-theoretic acquisition functions, achieving 5-20× reductions in simulation budgets by focusing computational resources on maximally informative parameter regions. Second, **physics-informed machine learning** incorporates known governing equations as soft constraints during model training, reducing the effective search space by eliminating physically infeasible parameter configurations. Physics-Informed Neural Networks (PINNs) and related approaches have demonstrated that PDE residual penalties can improve sample efficiency by 50-90% in forward simulation tasks.

Despite these advances, no existing work synergistically combines physics-informed priors with active acquisition strategies for simulation-based inference. Active SBI methods ignore physics constraints, wasting valuable simulations on infeasible parameter regions. Conversely, physics-informed approaches rely on passive sampling strategies that fail to exploit the sequential nature of Bayesian inference. This represents a critical gap: the potential multiplicative benefits of combining search space reduction through physics constraints with intelligent sample selection through active learning remain unexplored.

### 2.2 Research Objectives

This research proposes **Physics-Guided Active Learning for Simulation-Based Inference (PAGAL-SBI)**, a novel framework that integrates PDE-based physics constraints with information-theoretic active acquisition to achieve 10-100× reductions in simulation budgets while maintaining posterior accuracy within 5% of baseline methods. Our specific objectives are:

1. **Develop a unified theoretical framework** that combines physics-informed priors with expected information gain (EIG) acquisition for likelihood-free inference, establishing sample complexity bounds that demonstrate sublinear scaling with parameter dimension.

2. **Design and implement the PAGAL-SBI algorithm** with practical components including differentiable physics via automatic differentiation, adaptive cold-start protocols, batched acquisition for parallel computing, and online surrogate model updates.

3. **Empirically validate the approach** across three diverse PDE-governed simulators (Navier-Stokes CFD, linear elasticity FEM, magnetohydrodynamics) at varying dimensionalities (d ∈ {5, 10, 20}), demonstrating both efficiency gains and mechanistic understanding through rigorous ablation studies.

4. **Establish practical applicability** by demonstrating that acquisition overhead remains below 10% of simulation time and that the method scales to realistic engineering problems with 20+ parameters.

### 2.3 Research Hypothesis

We hypothesize that integrating physics-informed priors with information-theoretic active learning acquisition functions reduces simulation budgets by **10-100×** for Bayesian parameter inference in expensive PDE-governed simulators, compared to standard passive simulation-based inference, while maintaining posterior accuracy within 5% KL divergence from ground truth posteriors.

The causal mechanism operates through two synergistic pathways:

1. **Physics-informed priors** (implemented via PDE residual penalties) reduce the effective search space by 50-90% by assigning low probability mass to parameter configurations that violate governing equations.

2. **Expected information gain acquisition** selects maximally informative samples that reduce posterior uncertainty most efficiently, avoiding redundant simulations in well-characterized regions.

We hypothesize that these mechanisms combine multiplicatively rather than additively: a 50% search space reduction combined with 5-20× active learning efficiency yields 10-100× total reduction. This synergy arises because physics constraints enable more accurate surrogate models with fewer samples, which in turn improves EIG estimation quality, creating a positive feedback loop.

### 2.4 Significance

This research addresses a critical bottleneck in computational science and engineering with transformative potential across multiple domains:

**Scientific Impact:** PAGAL-SBI enables previously intractable uncertainty quantification tasks, compressing 70-day fusion reactor calibrations to 3.5 days, enabling nightly recalibration cycles that can accelerate plasma physics research. For climate modeling, reducing monthly recalibration from 208 days to 6 days enables rapid assimilation of new observational data.

**Methodological Impact:** This work establishes the first theoretical and algorithmic framework combining physics constraints with active acquisition for likelihood-free inference, bridging the gap between physics-informed machine learning and Bayesian experimental design communities. The open-source `pagal-sbi` package will provide practitioners with production-ready tools built on established libraries (`sbi`, `jax`).

**Engineering Impact:** Real-time structural health monitoring becomes feasible by reducing inference from 100 hours to 5 hours, enabling rapid damage assessment after seismic events. Aerodynamic design with uncertainty quantification becomes practical for rapid prototyping cycles, reducing design iteration time from weeks to days.

**Broader Relevance to Workshop:** This work directly addresses the workshop's focus on "techniques to speed-up simulation" and "probabilistic inverse problems," demonstrating how differentiable physics and active learning can synergistically improve simulation-based workflows. The approach is domain-agnostic, applicable to any PDE-governed simulator with known governing equations, making it relevant across the workshop's diverse application areas from graphics to molecular systems.

## 3. Methodology

### 3.1 Problem Formulation

We consider Bayesian parameter inference for expensive PDE-governed simulators. Let $\theta \in \Theta \subset \mathbb{R}^d$ denote unknown parameters, $x \in \mathcal{X}$ denote observable simulation outputs, and $\mathcal{S}(\theta)$ denote the expensive simulator. The forward model is:

$$x = \mathcal{S}(\theta) + \epsilon, \quad \epsilon \sim \mathcal{N}(0, \Sigma)$$

Given observed data $x_{\text{obs}}$, our goal is to approximate the posterior distribution:

$$p(\theta | x_{\text{obs}}) \propto p(x_{\text{obs}} | \theta) p(\theta)$$

where the likelihood $p(x | \theta)$ is intractable due to the expensive simulator $\mathcal{S}$. Standard SBI requires $N_{\text{sim}} \approx 10^4$-$10^5$ simulator evaluations, which is prohibitive when $\mathcal{S}(\theta)$ requires minutes to hours.

**Physics Constraints:** We assume access to governing PDEs that constrain feasible parameter values. For example, in Navier-Stokes CFD, parameters must satisfy conservation laws. We encode this as a PDE residual function $\mathcal{R}_{\text{PDE}}(\theta)$ that measures violation of governing equations.

### 3.2 PAGAL-SBI Framework

Our approach combines three key components:

#### 3.2.1 Physics-Informed Prior

We define a physics-informed prior that penalizes PDE violations:

$$p_{\text{phys}}(\theta) \propto p_0(\theta) \exp\left(-\lambda \|\mathcal{R}_{\text{PDE}}(\theta)\|^2\right)$$

where $p_0(\theta)$ is an uninformed base prior (e.g., uniform over $\Theta$), $\lambda > 0$ controls physics constraint strength, and $\mathcal{R}_{\text{PDE}}(\theta)$ is the PDE residual computed via automatic differentiation.

**Implementation via JAX:** We implement $\mathcal{R}_{\text{PDE}}$ using JAX's automatic differentiation to compute spatial derivatives. For example, for 2D Navier-Stokes with parameters $\theta = (\nu, \rho, u_{\text{inlet}})$ (viscosity, density, inlet velocity):

$$\mathcal{R}_{\text{PDE}}(\theta) = \left\|\rho\left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) + \nabla p - \nu \nabla^2 \mathbf{u}\right\|_{L^2}$$

evaluated on a coarse grid (e.g., $32 \times 32$) for computational efficiency.

#### 3.2.2 Neural Surrogate Model

To enable rapid evaluation for acquisition function optimization, we train a neural surrogate $\hat{\mathcal{S}}_\phi: \Theta \to \mathcal{X}$ using Fourier Neural Operators (FNO):

$$\hat{\mathcal{S}}_\phi(\theta) = \text{FNO}_\phi(\theta)$$

The FNO architecture consists of:
- **Input encoding:** $\theta \to \mathbb{R}^{64}$ via MLP
- **Fourier layers:** 4 layers with modes $(k_{\max}^x, k_{\max}^y) = (12, 12)$
- **Output projection:** $\mathbb{R}^{64} \to \mathcal{X}$ via MLP

Training objective combines data fidelity and physics constraints:

$$\mathcal{L}_{\text{surrogate}} = \mathbb{E}_{(\theta, x) \sim \mathcal{D}}\left[\|x - \hat{\mathcal{S}}_\phi(\theta)\|^2\right] + \lambda_{\text{sur}} \mathbb{E}_{\theta \sim p_{\text{phys}}}\left[\|\mathcal{R}_{\text{PDE}}(\hat{\mathcal{S}}_\phi(\theta))\|^2\right]$$

where $\mathcal{D} = \{(\theta_i, x_i)\}_{i=1}^{N}$ is the current simulation dataset.

#### 3.2.3 Physics-Informed Active Acquisition

We select new simulation parameters by maximizing expected information gain (EIG) with physics-informed sampling:

$$\theta_{\text{next}} = \arg\max_{\theta \in \Theta} \text{EIG}(\theta) \cdot p_{\text{phys}}(\theta)$$

where the EIG is approximated via:

$$\text{EIG}(\theta) = \mathbb{E}_{x \sim p(x|\theta)}\left[D_{\text{KL}}(p(\theta|x, \mathcal{D}) \| p(\theta|\mathcal{D}))\right]$$

**Monte Carlo Approximation:** We estimate EIG using $M=1000$ samples:

$$\widehat{\text{EIG}}(\theta) \approx \frac{1}{M}\sum_{j=1}^M \log \frac{p(\theta | x_j, \mathcal{D})}{p(\theta | \mathcal{D})}, \quad x_j \sim \hat{\mathcal{S}}_\phi(\theta) + \mathcal{N}(0, \Sigma)$$

where posterior densities are evaluated using the current neural density estimator (Masked Autoregressive Flow).

**Batched Acquisition:** For parallel computing, we select top-$K$ candidates:

$$\{\theta_{\text{next}}^{(1)}, \ldots, \theta_{\text{next}}^{(K)}\} = \text{Top-K}_{\theta \in \Theta}\left[\text{EIG}(\theta) \cdot p_{\text{phys}}(\theta)\right]$$

using gradient-based optimization (Adam) initialized from $10d$ random physics-filtered samples.

### 3.3 Complete PAGAL-SBI Algorithm

**Algorithm 1: PAGAL-SBI**

**Input:** Simulator $\mathcal{S}$, observed data $x_{\text{obs}}$, PDE residual $\mathcal{R}_{\text{PDE}}$, budget $N_{\text{max}}$

**Output:** Posterior approximation $q_\psi(\theta | x_{\text{obs}})$

1. **Initialization (Cold Start):**
   - Sample $n_0 = \max(10d, 50)$ candidates from $p_0(\theta)$
   - Filter: Accept if $\|\mathcal{R}_{\text{PDE}}(\theta)\| < \delta_{\text{phys}}$
   - Run simulator: $\mathcal{D}_0 = \{(\theta_i, \mathcal{S}(\theta_i))\}_{i=1}^{n_0}$
   - Train initial surrogate $\hat{\mathcal{S}}_\phi$ until validation error $< 10\%$
   - Train initial posterior $q_\psi^{(0)}(\theta | x)$ using MAF on $\mathcal{D}_0$

2. **Active Learning Loop:** For $t = 1, \ldots, T$ until $N_{\text{sim}} \geq N_{\text{max}}$:
   
   a. **Acquisition:**
      - Sample $10d$ candidates from $p_{\text{phys}}(\theta)$
      - Optimize $\theta_{\text{next}}^{(k)} = \arg\max \text{EIG}(\theta) \cdot p_{\text{phys}}(\theta)$ for $k=1,\ldots,K$
   
   b. **Simulation:**
      - Run simulator in parallel: $x_k = \mathcal{S}(\theta_{\text{next}}^{(k)})$ for $k=1,\ldots,K$
      - Update dataset: $\mathcal{D}_t = \mathcal{D}_{t-1} \cup \{(\theta_{\text{next}}^{(k)}, x_k)\}_{k=1}^K$
   
   c. **Model Update:**
      - Incrementally update surrogate $\hat{\mathcal{S}}_\phi$ with new data
      - Retrain posterior $q_\psi^{(t)}(\theta | x)$ on full $\mathcal{D}_t$
   
   d. **Convergence Check:**
      - If $\mathbb{E}_{\theta \sim q_\psi^{(t)}(\cdot|x_{\text{obs}})}[\text{EIG}(\theta)] < \epsilon_{\text{conv}}$: STOP

3. **Return:** Final posterior $q_\psi^{(T)}(\theta | x_{\text{obs}})$

**Hyperparameters:**
- Physics penalty: $\lambda = 5.0$
- Surrogate penalty: $\lambda_{\text{sur}} = 1.0$
- Physics threshold: $\delta_{\text{phys}} = 0.1$
- Batch size: $K = 10$
- Convergence threshold: $\epsilon_{\text{conv}} = 0.01$

### 3.4 Experimental Design

#### 3.4.1 Benchmark Simulators

We evaluate PAGAL-SBI on three diverse PDE-governed simulators:

**Benchmark 1: Navier-Stokes CFD (OpenFOAM)**
- **Problem:** Infer aerodynamic parameters from drag/lift coefficients
- **Parameters:** $\theta = (\nu, \rho, u_{\text{inlet}}, p_{\text{outlet}}, \alpha)$ (viscosity, density, inlet velocity, outlet pressure, angle of attack)
- **Dimensions:** $d \in \{5, 10, 20\}$ (adding turbulence model parameters for higher $d$)
- **Observations:** $x = (C_D, C_L, p_{\text{wake}})$ (drag coefficient, lift coefficient, wake pressure)
- **Simulation time:** ~5 minutes per run (2D RANS, 50k cells)
- **PDE residual:** Navier-Stokes momentum and continuity equations

**Benchmark 2: Linear Elasticity FEM (Abaqus)**
- **Problem:** Infer material properties from displacement measurements
- **Parameters:** $\theta = (E_1, \ldots, E_n, \nu_1, \ldots, \nu_m)$ (Young's moduli, Poisson ratios for different regions)
- **Dimensions:** $d \in \{5, 10, 20\}$
- **Observations:** $x = (u_1, \ldots, u_k)$ (displacements at sensor locations)
- **Simulation time:** ~3 minutes per run (3D mesh, 100k elements)
- **PDE residual:** Linear elasticity equilibrium equations $\nabla \cdot \sigma + f = 0$

**Benchmark 3: Magnetohydrodynamics (BOUT++)**
- **Problem:** Infer tokamak magnetic field parameters from plasma profiles
- **Parameters:** $\theta = (B_0, q_{\text{safety}}, \beta, \kappa, \delta)$ (toroidal field, safety factor, plasma beta, elongation, triangularity)
- **Dimensions:** $d \in \{5, 10, 20\}$ (adding transport coefficients for higher $d$)
- **Observations:** $x = (n_e(r), T_e(r), \phi(r))$ (electron density, temperature, potential profiles)
- **Simulation time:** ~10 minutes per run (2D tokamak geometry)
- **PDE residual:** MHD equations (mass, momentum, energy conservation)

#### 3.4.2 Experimental Conditions

**Factorial Design:** $3 \text{ simulators} \times 3 \text{ dimensions} \times 4 \text{ methods} \times 10 \text{ seeds} = 360$ trials

**Methods (Ablation Study):**
1. **Baseline:** Standard SNPE-C with uniform prior, random sampling
2. **Physics-Only:** Physics-informed prior $p_{\text{phys}}(\theta)$ with random sampling
3. **Active-Only:** Uninformed prior $p_0(\theta)$ with EIG acquisition
4. **PAGAL-SBI (Combined):** Physics-informed prior + EIG acquisition

**Ground Truth Posteriors:** For each benchmark, we compute reference posteriors using:
- **MCMC:** 100,000 samples via No-U-Turn Sampler (NUTS) with surrogate likelihood
- **Validation:** Ensure $\hat{R} < 1.01$ (Gelman-Rubin diagnostic) and ESS $> 10,000$

#### 3.4.3 Evaluation Metrics

**Primary Outcome: Simulation Budget**
$$N_{\text{sim}} = \text{number of simulator calls until convergence}$$

Convergence criterion: $D_{\text{KL}}(q_\psi(\theta|x_{\text{obs}}) \| p_{\text{ref}}(\theta|x_{\text{obs}})) < 0.05$

**Secondary Outcomes:**

1. **Posterior Accuracy:**
$$\text{KL-Ratio} = \frac{D_{\text{KL}}(q_\psi \| p_{\text{ref}})}{D_{\text{KL}}(q_{\text{baseline}} \| p_{\text{ref}})}$$

Success: KL-Ratio $\leq 1.05$ (within 5% of baseline)

2. **Acquisition Overhead:**
$$\text{Overhead} = \frac{\sum_{t=1}^T t_{\text{acq}}^{(t)}}{\sum_{i=1}^{N_{\text{sim}}} t_{\text{sim}}^{(i)}}$$

Success: Overhead $< 0.10$ (less than 10% of simulation time)

3. **Scalability:**
Fit power law $N_{\text{sim}} = C \cdot d^\alpha$ via log-linear regression:
$$\log(N_{\text{sim}}) = \log(C) + \alpha \log(d)$$

Success: $\alpha \in [0.5, 0.8]$ (sublinear scaling)

4. **Synergy Metric:**
$$\text{Synergy} = \frac{N_{\text{baseline}}}{N_{\text{combined}}} - \left(\frac{N_{\text{baseline}}}{N_{\text{physics}}} + \frac{N_{\text{baseline}}}{N_{\text{active}}} - 1\right)$$

Success: Synergy $> 0$ (multiplicative effect beyond additive contributions)

#### 3.4.4 Statistical Analysis

**Hypothesis Tests:**

1. **Main Effect (H1):** PAGAL-SBI achieves $\geq 10\times$ reduction
   - **Test:** Paired t-test on $\log(N_{\text{sim}})$ between PAGAL-SBI and Baseline
   - **Correction:** Bonferroni for 3 simulators ($\alpha = 0.01/3 = 0.0033$)
   - **Power:** $n=10$ seeds provides 95% power to detect effect size $d \geq 2.0$

2. **Ablation (H2):** Synergy between physics and active learning
   - **Test:** Two-way ANOVA with factors {Physics: Yes/No} × {Active: Yes/No}
   - **Interaction:** $F$-test for Physics × Active interaction term
   - **Success:** Significant interaction ($p < 0.01$) in $\geq 2/3$ benchmarks

3. **Scalability (H3):** Sublinear scaling with dimension
   - **Test:** $F$-test comparing slopes $\alpha_{\text{PAGAL}}$ vs $\alpha_{\text{baseline}}$
   - **Success:** $\alpha_{\text{PAGAL}} < \alpha_{\text{baseline}}$ with $p < 0.01$

4. **Quality (H4):** Non-inferiority in posterior accuracy
   - **Test:** One-sided $t$-test with margin $\delta = 0.05$
   - **Null:** KL-Ratio $> 1.05$ (inferior)
   - **Success:** Reject null with 90% confidence in all benchmarks

**Reproducibility:**
- All code released on GitHub with MIT license
- Docker containers with frozen dependencies
- Random seeds documented for all experiments
- Simulation outputs archived on Zenodo (DOI)

### 3.5 Implementation Details

**Software Stack:**
- **Differentiable Physics:** JAX 0.4.x for automatic differentiation
- **SBI Framework:** `sbi` 0.22.x (PyTorch-based)
- **Neural Operators:** Custom FNO implementation in JAX
- **Simulators:** OpenFOAM 10, Abaqus 2023, BOUT++ 5.0
- **Compute:** 4× NVIDIA A100 GPUs (40GB), 128 CPU cores

**Computational Budget:**
- **Per trial:** ~50 GPU-hours (surrogate training) + simulator time
- **Total:** 360 trials × 50 GPU-hours = 18,000 GPU-hours (~75 days on 4 GPUs)
- **Simulator time:** Varies by benchmark (3-10 min/sim × 100-1000 sims/trial)

**Open-Source Package (`pagal-sbi`):**
```python
from pagal_sbi import PAGALSBI
from pagal_sbi.physics import NavierStokesResidual

# Define physics constraints
physics = NavierStokesResidual(grid_size=32)

# Initialize PAGAL-SBI
inference = PAGALSBI(
    simulator=openfoam_wrapper,
    physics_residual=physics,
    prior=uniform_prior,
    lambda_physics=5.0
)

# Run inference
posterior = inference.run(
    x_obs=observed_data,
    budget=1000,
    batch_size=10
)
```

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Quantitative Results:**

1. **Simulation Budget Reduction:** We expect PAGAL-SBI to achieve 10-100× reduction in simulation budgets across all three benchmarks:
   - **CFD (Navier-Stokes):** 20,000 → 200-1,000 simulations (20-100× reduction)
   - **FEM (Elasticity):** 15,000 → 300-1,500 simulations (10-50× reduction)
   - **MHD (BOUT++):** 30,000 → 500-2,000 simulations (15-60× reduction)

2. **Posterior Accuracy Preservation:** KL divergence within 5% of baseline (KL-Ratio ≤ 1.05) for all benchmarks, demonstrating that efficiency gains do not compromise inference quality.

3. **Computational Efficiency:** Acquisition overhead below 10% of total simulation time, confirming practical applicability for expensive simulators.

4. **Scalability:** Sublinear scaling exponent $\alpha \in [0.5, 0.8]$ compared to baseline $\alpha \approx 1.0$, demonstrating improved scaling to higher-dimensional parameter spaces.

5. **Synergy Demonstration:** Positive synergy metric in ≥50% of benchmarks, confirming that physics constraints and active learning combine multiplicatively rather than additively.

**Mechanistic Understanding:**

Through ablation studies, we will quantify the individual contributions:
- **Physics-informed priors:** 2-5× reduction via search space reduction (50-80% acceptance rate decrease)
- **Active acquisition:** 5-20× reduction via intelligent sample selection
- **Combined effect:** 10-100× reduction via synergistic interaction

### 4.2 Scientific Impact

**Theoretical Contributions:**

1. **Sample Complexity Bounds:** We will establish the first theoretical framework for physics-informed active SBI, proving that:
$$N_{\text{sim}} \leq C \cdot d \cdot \log(1/\epsilon)$$
compared to standard SBI's $O(d^2/\epsilon)$ complexity, where $\epsilon$ is posterior approximation error.

2. **Information Decomposition:** We will formalize how physics constraints and data information combine:
$$I(\theta; x) = I_{\text{phys}}(\theta) + I_{\text{data}}(\theta; x) - I_{\text{redundant}}$$
providing theoretical justification for the synergy mechanism.

**Methodological Contributions:**

1. **Unified Framework:** PAGAL-SBI bridges physics-informed machine learning and Bayesian experimental design, creating a new research direction at their intersection.

2. **Practical Algorithm:** The complete implementation with adaptive cold-start, batched acquisition, and online model updates provides a production-ready tool for practitioners.

3. **Open-Source Ecosystem:** The `pagal-sbi` package built on `sbi` and `jax` will enable widespread adoption and extension by the community.

### 4.3 Practical Impact

**Application-Specific Transformations:**

1. **Fusion Energy (BOUT++):**
   - **Current:** 70 days for reactor calibration → **PAGAL-SBI:** 3.5 days
   - **Impact:** Enable nightly recalibration cycles, accelerating plasma physics research and reactor optimization

2. **Aerodynamic Design (OpenFOAM):**
   - **Current:** 17 days for uncertainty quantification → **PAGAL-SBI:** 16 hours
   - **Impact:** Enable rapid prototyping with UQ, reducing design iteration cycles from weeks to days

3. **Structural Health Monitoring (Abaqus):**
   - **Current:** 100 hours for damage assessment → **PAGAL-SBI:** 5 hours
   - **Impact:** Enable real-time post-earthquake structural evaluation, improving emergency response

4. **Climate Modeling (WRF):**
   - **Current:** 208 days for monthly recalibration → **PAGAL-SBI:** 6 days
   - **Impact:** Enable rapid assimilation of new observational data, improving forecast accuracy

**Economic Impact:**

Assuming cloud computing costs of $3/GPU-hour:
- **Baseline SBI:** 20,000 sims × 5 min × $0.25/hour = $4,167 per inference task
- **PAGAL-SBI:** 500 sims × 5 min × $0.25/hour = $104 per inference task
- **Savings:** $4,063 per task (97.5% cost reduction)

For organizations running 100+ inference tasks annually, this translates to $400K+ annual savings.

### 4.4 Broader Impact on Workshop Themes

**Relevance to Workshop Topics:**

1. **Differentiable Simulators:** Demonstrates how automatic differentiation enables physics-informed priors for inverse problems

2. **Probabilistic Inverse Problems:** Advances simulation-based inference with physics-guided active learning

3. **Techniques to Speed-up Simulation:** Achieves 10-100× acceleration through intelligent sample selection

4. **Improving Simulation Accuracy:** Physics constraints reduce sim2real gap by enforcing governing equations

5. **Datasets and Software:** Provides open-source tools and benchmark datasets for community use

**Cross-Domain Applicability:**

The PAGAL-SBI framework is domain-agnostic, applicable to any PDE-governed simulator:
- **Graphics:** Differentiable rendering with physics-based light transport
- **Molecular Systems:** Protein folding with physics-informed potentials
- **Wireless:** EM wave propagation with Maxwell's equations
- **Manufacturing:** Thermal process simulation with heat equations

### 4.5 Limitations and Future Work

**Known Limitations:**

1. **Physics Knowledge Requirement:** Requires access to governing PDEs (not applicable to black-box simulators)
2. **Dimensionality:** Validated up to $d=20$; higher dimensions may require additional techniques
3. **PDE Approximation:** Coarse-grid residual evaluation may miss fine-scale physics violations

**Future Research Directions:**

1. **Multi-Fidelity Extension:** Combine PAGAL-SBI with coarse-grid simulators for further speedups
2. **Physics Misspecification:** Develop robustness to approximate or incomplete governing equations
3. **Non-PDE Constraints:** Extend to other domain knowledge (conservation laws, symmetries, bounds)
4. **Adaptive Physics Weighting:** Learn optimal $\lambda$ during inference rather than fixing a priori
5. **Distributed Computing:** Scale to massively parallel HPC environments with asynchronous acquisition

### 4.6 Success Criteria

The research will be considered successful if:

1. **Efficiency:** ≥10× simulation budget reduction in ≥2/3 benchmarks (6/9 conditions)
2. **Quality:** Posterior accuracy within 5% of baseline in all benchmarks (9/9 conditions)
3. **Synergy:** Demonstrated multiplicative effect beyond additive contributions in ≥1/2 benchmarks
4. **Scalability:** Sublinear scaling ($\alpha < 0.8$) in ≥2/3 benchmarks
5. **Practicality:** Acquisition overhead <10% in all benchmarks
6. **Reproducibility:** All results reproducible from open-source code and archived data

**Dissemination Plan:**

- **Publication:** Target NeurIPS/ICML (main conference) or specialized venues (UAI, AISTATS)
- **Workshop Presentation:** Submit to this workshop and related venues (SciML, UQ)
- **Software Release:** GitHub repository with documentation, tutorials, and examples
- **Community Engagement:** Tutorials at summer schools, blog posts, video demonstrations

This comprehensive research plan establishes PAGAL-SBI as a transformative approach to simulation-based inference, with rigorous validation, broad applicability, and significant practical impact across computational science and engineering domains.