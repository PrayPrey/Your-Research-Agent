# Research Proposal: Physics-Constrained Flow Matching with Extreme Value Theory for Physically Consistent Climate Extreme Generation

## 1. Introduction

### 1.1 Background

Climate change poses an existential threat to human civilization, with extreme weather events—heat waves, precipitation extremes, and compound hazards—becoming increasingly frequent and severe. Accurate climate projections are essential for adaptation planning and risk assessment, yet current modeling approaches face fundamental limitations in simulating these critical extreme events. Traditional numerical climate models, while physically interpretable and capable of simulating counterfactual scenarios, require exhaustive tuning and remain computationally prohibitive at resolutions necessary to capture localized extremes. Meanwhile, the recent surge in AI-based weather and climate forecasting has demonstrated remarkable skill in medium-range prediction, with models like GraphCast and Pangu-Weather achieving operational-quality forecasts at a fraction of the computational cost.

However, a critical gap persists at the intersection of physical consistency and statistical accuracy for extreme events. Current AI-based climate models face a fundamental tension: they either satisfy physical conservation laws OR capture statistical tail distributions, but rarely achieve both simultaneously. Unconstrained generative models, including diffusion-based and flow-matching approaches, can produce physically implausible extremes with energy and mass conservation violations on the order of $10^{-2}$. Conversely, physics-constrained approaches that enforce conservation laws tend to underrepresent rare event statistics, as the constraint manifold may not align with the tails of observed extreme distributions. This dichotomy severely limits the trustworthiness of AI-generated climate projections for risk assessment applications where both physical plausibility and accurate tail statistics are paramount.

The challenge is further compounded by the nature of climate extremes themselves. High Impact-Low Likelihood (HILL) events are inherently undersampled in observational records such as ERA5 reanalysis data. Substantial decadal variability in modes of climate variability, including the El Niño-Southern Oscillation (ENSO), limits the ability of purely data-driven approaches to extrapolate reliably into future climate states. These factors demand methodological innovations that can leverage physical principles while accurately representing the statistical properties of rare events.

### 1.2 Research Objectives

This research proposes EVT-CFM (Extreme Value Theory-guided Constrained Flow Matching), a novel framework that combines Physics-Constrained Flow Matching (PCFM) with Extreme Value Theory (EVT) guidance to generate climate extreme events that are simultaneously physically consistent and statistically accurate. Our specific objectives are:

1. **Develop a constraint projection mechanism** that enforces hard conservation laws (energy, mass, moisture) during flow-matching generation to numerical precision ($<10^{-6}$), adapting recent advances in physics-constrained flow matching to high-dimensional climate grids.

2. **Integrate EVT-parameterized tail guidance** using Generalized Pareto Distribution (GPD) parameters fitted from historical extremes to steer the generative sampling process toward statistically correct extreme tails.

3. **Validate the combined framework** on ERA5/CMIP6 data, demonstrating that EVT-CFM achieves both conservation law satisfaction and tail distribution accuracy without requiring model retraining.

4. **Establish falsification criteria** and rigorous statistical verification protocols to ensure scientific reproducibility and identify boundary conditions for the method's applicability.

### 1.3 Significance

This research addresses a critical need identified by the climate modeling community: the development of hybrid physics-ML approaches that maintain physical interpretability while leveraging the representational power of deep generative models. By achieving both hard physical constraints and accurate extreme statistics, EVT-CFM would enable:

- **Trustworthy climate risk assessment** for adaptation planning, where physically implausible extremes could lead to misallocated resources
- **Improved dynamical downscaling** of coarse-resolution climate projections with physically consistent high-resolution extreme events
- **Enhanced uncertainty quantification** for climate projections by generating ensembles that respect both physical laws and observed tail statistics

The zero-shot inference capability of our approach—requiring no retraining of base flow models—makes it immediately applicable to existing pretrained climate models, accelerating the translation of methodological advances into operational climate services.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathbf{x} \in \mathbb{R}^d$ represent a climate state vector (temperature, pressure, humidity, wind components) on a spatial grid with $d = O(10^5-10^6)$ degrees of freedom. We consider a pretrained flow-matching model that learns a velocity field $v_\theta(\mathbf{x}, t)$ transporting samples from a prior distribution $p_0$ to the data distribution $p_1$ via the ODE:

$$\frac{d\mathbf{x}}{dt} = v_\theta(\mathbf{x}, t), \quad t \in [0, 1]$$

Our goal is to modify the sampling process such that generated samples satisfy:
1. **Conservation constraints:** $\mathbf{g}(\mathbf{x}) = \mathbf{0}$ where $\mathbf{g}: \mathbb{R}^d \rightarrow \mathbb{R}^m$ encodes energy, mass, and moisture conservation
2. **Tail distribution accuracy:** The distribution of extreme values follows a Generalized Pareto Distribution with parameters $(\xi, \sigma, \mu)$ fitted from observations

### 2.2 Physics-Constrained Flow Matching (PCFM)

We adapt the PCFM framework to climate applications by projecting flow trajectories onto the constraint manifold $\mathcal{M} = \{\mathbf{x} : \mathbf{g}(\mathbf{x}) = \mathbf{0}\}$ during ODE integration.

**Conservation Law Specification:**

For climate states, we define three primary constraints:

1. **Global energy conservation:**
$$g_1(\mathbf{x}) = \sum_{i} \rho_i c_p T_i \Delta V_i - E_0 = 0$$

2. **Mass conservation:**
$$g_2(\mathbf{x}) = \sum_{i} \rho_i \Delta V_i - M_0 = 0$$

3. **Moisture conservation:**
$$g_3(\mathbf{x}) = \sum_{i} q_i \rho_i \Delta V_i - Q_0 = 0$$

where $T_i$, $\rho_i$, $q_i$ are temperature, density, and specific humidity at grid cell $i$, and $E_0$, $M_0$, $Q_0$ are reference values.

**Constraint Projection via Newton Iteration:**

At each ODE integration step, after computing the unconstrained update $\tilde{\mathbf{x}}_{t+\Delta t} = \mathbf{x}_t + \Delta t \cdot v_\theta(\mathbf{x}_t, t)$, we project onto $\mathcal{M}$:

$$\mathbf{x}_{t+\Delta t} = \tilde{\mathbf{x}}_{t+\Delta t} - \mathbf{J}^\dagger \mathbf{g}(\tilde{\mathbf{x}}_{t+\Delta t})$$

where $\mathbf{J} = \nabla_\mathbf{x} \mathbf{g}$ is the constraint Jacobian and $\mathbf{J}^\dagger = \mathbf{J}^T(\mathbf{J}\mathbf{J}^T)^{-1}$ is its pseudoinverse. For convergence to tolerance $\epsilon = 10^{-6}$, we iterate:

$$\mathbf{x}^{(k+1)} = \mathbf{x}^{(k)} - \mathbf{J}^\dagger(\mathbf{x}^{(k)}) \mathbf{g}(\mathbf{x}^{(k)})$$

until $\|\mathbf{g}(\mathbf{x}^{(k)})\|_2 < \epsilon$, typically requiring 2-3 iterations.

**Patch-Based Scaling:**

To handle high-dimensional climate grids, we employ patch-based constraint projection. The global domain is partitioned into overlapping patches $\{P_j\}$, with local constraints enforced per patch and boundary consistency maintained through iterative refinement:

$$\mathbf{x}_{P_j}^{(k+1)} = \text{Project}_{P_j}(\mathbf{x}_{P_j}^{(k)}) + \lambda \sum_{P_l \in \mathcal{N}(P_j)} (\mathbf{x}_{P_l \cap P_j} - \mathbf{x}_{P_j \cap P_l})$$

where $\mathcal{N}(P_j)$ denotes neighboring patches and $\lambda$ controls boundary smoothing.

### 2.3 EVT-Parameterized Tail Guidance

**GPD Parameter Estimation:**

For each climate variable and spatial location, we fit GPD parameters from historical extreme events exceeding threshold $\mu$ (set at the 95th percentile via mean residual life plot analysis):

$$P(X > x | X > \mu) = \left(1 + \xi \frac{x - \mu}{\sigma}\right)^{-1/\xi}$$

Parameters $(\xi, \sigma)$ are estimated via maximum likelihood from ERA5 data (1979-2020), with $\xi \in [-0.5, 0.5]$ capturing tail behavior (heavy-tailed for $\xi > 0$, bounded for $\xi < 0$).

**Tail-Guided Sampling:**

We modify the flow velocity to incorporate EVT guidance through a score-like correction term:

$$\tilde{v}_\theta(\mathbf{x}, t) = v_\theta(\mathbf{x}, t) + \alpha(t) \nabla_\mathbf{x} \log p_{\text{EVT}}(\mathbf{x})$$

where $p_{\text{EVT}}(\mathbf{x})$ is the EVT-implied density for extreme regions and $\alpha(t)$ is a time-dependent weighting that increases toward $t=1$ to guide final samples toward correct tail statistics:

$$\alpha(t) = \alpha_0 \cdot \mathbb{1}[\mathbf{x} > \mu] \cdot t^2$$

The EVT score is computed as:

$$\nabla_\mathbf{x} \log p_{\text{EVT}}(\mathbf{x}) = -\frac{1 + \xi}{\sigma + \xi(\mathbf{x} - \mu)} \cdot \mathbb{1}[\mathbf{x} > \mu]$$

### 2.4 Combined EVT-CFM Algorithm

**Algorithm 1: EVT-CFM Sampling**

```
Input: Pretrained flow model v_θ, constraint function g, GPD parameters (ξ, σ, μ), 
       tolerance ε, guidance strength α₀
Output: Physically consistent extreme climate sample x₁

1. Sample x₀ ~ p₀ (standard Gaussian)
2. For t = 0 to 1 with step Δt:
   a. Compute EVT-guided velocity: ṽ = v_θ(x_t, t) + α(t)∇log p_EVT(x_t)
   b. Euler step: x̃_{t+Δt} = x_t + Δt · ṽ
   c. Constraint projection (Newton iteration):
      k = 0
      While ||g(x̃)|| > ε and k < max_iter:
         x̃ ← x̃ - J†(x̃)g(x̃)
         k ← k + 1
   d. x_{t+Δt} ← x̃
3. Return x₁
```

### 2.5 Experimental Design

**Data:**
- ERA5 reanalysis (1979-2020) at 0.25° and 1° resolution
- CMIP6 historical simulations for cross-validation
- Variables: 2m temperature, total precipitation, mean sea level pressure, specific humidity

**Base Models:**
- ClimateDiffuse or ArchesWeatherGen (pretrained flow-matching climate models)
- Weights frozen; EVT-CFM applied at inference only

**Experimental Conditions:**

| Condition | PCFM | EVT Guidance | Purpose |
|-----------|------|--------------|---------|
| Baseline (unconstrained) | ✗ | ✗ | Lower bound |
| PCFM-only | ✓ | ✗ | Isolate physics effect |
| EVT-only | ✗ | ✓ | Isolate tail guidance effect |
| EVT-CFM (full) | ✓ | ✓ | Proposed method |

**Evaluation Metrics:**

1. **Conservation violation:** $\mathcal{V} = \|\mathbf{g}(\mathbf{x})\|_2$ (target: $<10^{-6}$)
2. **Tail accuracy:** QQ-plot $R^2$ against fitted GPD (target: $>0.95$); KS statistic (target: $<0.1$)
3. **Spatial coherence:** Variogram correlation with observed extremes (target: $r > 0.8$); Moran's I (target: $>0.6$)
4. **Computational overhead:** Wall-clock time relative to unconstrained sampling

**Statistical Verification:**
- $n \geq 30$ independent runs per configuration
- Paired t-tests for conservation metrics with Bonferroni correction
- Two-sample KS tests for distribution comparisons
- Report: mean ± SD, 95% CI, Cohen's d effect size

**Falsification Criteria:**
1. Conservation violation $> 10^{-3}$
2. Newton iterations fail to converge for $>10\%$ of samples
3. QQ-plot $R^2 < 0.8$ OR KS statistic $> 0.2$
4. Combined EVT-CFM performs worse than either component alone

### 2.6 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

1. **H-M1 (PCFM → Conservation):** Vary constraint tolerance from $10^{-8}$ to $10^{-3}$; measure conservation violation scaling
2. **H-M2 (Conservation → Physical states):** Analyze intermediate states at $t \in \{0.25, 0.5, 0.75\}$ for physical plausibility
3. **H-M3 (EVT → Tail guidance):** Compare GPD vs. alternative tail models (GEV, empirical)
4. **H-M4 (Combined effect):** Test for interference between PCFM and EVT guidance

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

We anticipate EVT-CFM will achieve:

1. **Conservation law satisfaction to numerical precision** ($<10^{-6}$), representing a 4-order-of-magnitude improvement over unconstrained generation ($\sim 10^{-2}$)

2. **Accurate tail statistics** with QQ-plot $R^2 > 0.95$ for precipitation and temperature extremes, compared to $R^2 \sim 0.7-0.8$ for physics-only approaches

3. **Maintained spatial coherence** with variogram correlations $>0.8$, ensuring generated extremes exhibit realistic spatial patterns

4. **Acceptable computational overhead** of 1.5-3x relative to unconstrained sampling, enabling practical deployment

### 3.2 Scientific Impact

This research contributes to multiple areas:

**Machine Learning for Climate:** EVT-CFM demonstrates that hard physical constraints and accurate tail statistics are not mutually exclusive, opening new directions for trustworthy climate AI.

**Extreme Value Theory:** The integration of EVT into generative model sampling provides a principled framework for rare event generation applicable beyond climate science.

**Hybrid Physics-ML Modeling:** The zero-shot constraint enforcement paradigm enables rapid deployment of physics-informed corrections to existing pretrained models.

### 3.3 Practical Applications

- **Climate risk assessment:** Generate physically plausible extreme event ensembles for infrastructure stress testing
- **Dynamical downscaling:** Produce high-resolution extremes from coarse climate projections with conservation guarantees
- **Reanalysis augmentation:** Supplement observational records with synthetic extremes for improved statistical characterization

### 3.4 Limitations and Future Work

We acknowledge limitations including potential patch boundary artifacts, the requirement for sufficient historical extremes ($>30$ threshold exceedances) for robust GPD fitting, and applicability restricted to variables with well-defined conservation laws. Future work will extend EVT-CFM to compound extremes, investigate hierarchical constraint structures, and explore applications to paleoclimate reconstruction.