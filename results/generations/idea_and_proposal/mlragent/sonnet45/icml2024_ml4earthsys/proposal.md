# Research Proposal: Hierarchical Uncertainty Quantification for Physics-ML Hybrid Climate Models via Deep Ensembles with Physics Constraints

## 1. Introduction

### Background

Climate change represents one of the most pressing challenges facing human civilization, with far-reaching implications for global ecosystems, economies, and societies. Accurate climate projections are essential for informing adaptation strategies and mitigation policies that require multi-billion dollar investments. Traditional climate models based on numerical simulations of physical equations have been the gold standard for decades, offering interpretability and the ability to simulate hypothetical scenarios. However, these models face significant computational constraints, particularly in representing subgrid-scale processes such as cloud formation, convection, and turbulence, which occur at scales too fine to be explicitly resolved in global climate models.

Recent advances in machine learning have opened new avenues for climate modeling, particularly through hybrid physics-ML approaches where neural networks emulate computationally expensive parameterizations of subgrid processes. These hybrid models promise orders of magnitude speedup while maintaining physical consistency. Despite this promise, their adoption by the climate science community has been limited by a critical challenge: the lack of reliable uncertainty quantification (UQ). Climate projections inherently involve multiple sources of uncertainty, including epistemic uncertainty arising from limited training data and model specification, and aleatoric uncertainty stemming from the chaotic nature of climate dynamics.

The importance of robust UQ becomes especially acute when considering High Impact-Low Likelihood (HILL) events such as extreme heat waves, unprecedented precipitation patterns, or potential climate tipping points. These events are undersampled in observational datasets like ERA5 reanalysis, yet they are precisely the scenarios that policymakers need to understand for effective risk management. Furthermore, substantial decadal variability in climate modes such as the El-Niño Southern Oscillation (ENSO) limits the ability of purely data-driven models to extrapolate reliably into future climate states that may differ significantly from historical conditions.

### Research Objectives

This research proposes to develop a comprehensive framework for hierarchical uncertainty quantification in physics-ML hybrid climate models, specifically targeting ML-based parameterizations of subgrid processes. The primary objectives are:

1. **Develop physics-constrained deep ensemble architectures** that enforce conservation laws (energy, mass, momentum) while maintaining diversity for robust uncertainty estimation.

2. **Design multi-fidelity calibration methods** that leverage both high-resolution simulations and sparse observational data to produce well-calibrated uncertainty estimates across spatial and temporal scales.

3. **Implement physics-based out-of-distribution (OOD) detection mechanisms** to identify when ML emulators encounter climate states beyond their training distribution, particularly relevant for future climate scenarios.

4. **Quantify uncertainty propagation** through coupled climate system components to understand how parameterization uncertainty cascades through atmosphere-ocean-land interactions.

5. **Validate the framework** on critical climate prediction tasks including temperature and precipitation extremes, with particular attention to HILL events and climate tipping points.

### Significance

This research addresses a fundamental bottleneck in the adoption of ML methods for climate modeling. By providing reliable, physically consistent uncertainty estimates, the proposed framework will:

- **Enable trustworthy climate projections**: Domain scientists and policymakers can distinguish between genuine climate variability and model uncertainty, improving risk assessment and decision-making.

- **Accelerate hybrid model development**: Providing tools for UQ reduces the barrier to entry for ML methods in operational climate models, potentially catalyzing a paradigm shift in climate modeling.

- **Improve extreme event prediction**: Better characterization of uncertainty for HILL events will enhance preparedness for climate-related disasters.

- **Advance ML methodology**: The integration of physics constraints with ensemble methods and multi-fidelity approaches contributes to the broader field of uncertainty quantification in scientific machine learning.

## 2. Methodology

### 2.1 Overall Framework Architecture

The proposed framework consists of four interconnected components: (1) physics-constrained ensemble generation, (2) multi-fidelity uncertainty calibration, (3) OOD detection and flagging, and (4) uncertainty propagation analysis. We describe each component in detail below.

### 2.2 Physics-Constrained Deep Ensemble Architecture

#### 2.2.1 Ensemble Design

We adopt a deep ensemble approach where $M$ neural networks $\{f_\theta^{(m)}\}_{m=1}^M$ are trained independently with different random initializations to capture epistemic uncertainty. Each ensemble member emulates a specific parameterization (e.g., convection, cloud microphysics) mapping coarse-grid state variables $\mathbf{x} \in \mathbb{R}^d$ to subgrid tendencies $\mathbf{y} \in \mathbb{R}^p$.

To ensure diversity while maintaining accuracy, we employ:
- **Varied architectures**: Different ensemble members use distinct architectures (fully connected, convolutional, attention-based) suited to different physical processes.
- **Bootstrap sampling**: Each member is trained on a bootstrap sample of the training data.
- **Adversarial training**: Incorporate adversarial examples during training to improve robustness.

#### 2.2.2 Physics-Informed Constraints

We integrate physical constraints through multiple mechanisms:

**Hard Constraints via Architecture**: Design network architectures with built-in conservation properties. For mass conservation, we use:
$$f_\theta(\mathbf{x}) = \nabla \times \mathbf{g}_\theta(\mathbf{x})$$
where $\mathbf{g}_\theta$ is a learned vector potential, ensuring the divergence-free property required for mass conservation.

**Soft Constraints via Loss Functions**: The training loss combines data fidelity with physics-based penalties:
$$\mathcal{L}(\theta) = \mathcal{L}_{\text{data}}(\theta) + \lambda_1 \mathcal{L}_{\text{energy}}(\theta) + \lambda_2 \mathcal{L}_{\text{momentum}}(\theta) + \lambda_3 \mathcal{L}_{\text{mass}}(\theta)$$

where:
- $\mathcal{L}_{\text{data}}(\theta) = \frac{1}{N}\sum_{i=1}^N \|\mathbf{y}_i - f_\theta(\mathbf{x}_i)\|^2$ measures prediction accuracy
- $\mathcal{L}_{\text{energy}}(\theta)$ penalizes violations of energy conservation
- $\mathcal{L}_{\text{momentum}}(\theta)$ enforces momentum conservation
- $\mathcal{L}_{\text{mass}}(\theta)$ enforces mass conservation

For energy conservation, we define:
$$\mathcal{L}_{\text{energy}}(\theta) = \frac{1}{N}\sum_{i=1}^N \left|\Delta E_i - \left(Q_i - W_i\right)\right|^2$$
where $\Delta E_i$ is the predicted energy change, $Q_i$ is heat input, and $W_i$ is work done.

**Physics-Informed Regularization**: We add a regularization term that encourages physically plausible behavior:
$$\mathcal{R}(\theta) = \|\nabla_\mathbf{x} f_\theta(\mathbf{x})\|_F^2$$
constraining the smoothness of predicted tendencies.

#### 2.2.3 Heteroscedastic Uncertainty Modeling

Each ensemble member $f_\theta^{(m)}$ outputs both a mean prediction $\boldsymbol{\mu}^{(m)}(\mathbf{x})$ and an aleatoric uncertainty estimate $\boldsymbol{\sigma}^{(m)}(\mathbf{x})$ by predicting parameters of a probability distribution:
$$p(\mathbf{y}|\mathbf{x}, \theta^{(m)}) = \mathcal{N}(\mathbf{y}; \boldsymbol{\mu}^{(m)}(\mathbf{x}), \text{diag}(\boldsymbol{\sigma}^{(m)}(\mathbf{x})^2))$$

The negative log-likelihood loss for training becomes:
$$\mathcal{L}_{\text{NLL}}(\theta^{(m)}) = \frac{1}{N}\sum_{i=1}^N \left[\frac{\|\mathbf{y}_i - \boldsymbol{\mu}^{(m)}(\mathbf{x}_i)\|^2}{2\boldsymbol{\sigma}^{(m)}(\mathbf{x}_i)^2} + \log \boldsymbol{\sigma}^{(m)}(\mathbf{x}_i)\right]$$

### 2.3 Multi-Fidelity Uncertainty Calibration

Climate modeling uniquely offers multiple data sources with varying fidelity and cost:
- **High-fidelity**: Expensive high-resolution simulations (few samples)
- **Low-fidelity**: Coarse-resolution simulations (abundant samples)
- **Observational**: Real-world data (sparse, noisy, limited coverage)

#### 2.3.1 Multi-Fidelity Training Strategy

We adopt a two-stage training approach:

**Stage 1 - Low-Fidelity Pre-training**: Train ensemble members on abundant coarse-resolution data to learn general patterns:
$$\theta_{\text{LF}}^{(m)*} = \arg\min_{\theta^{(m)}} \mathcal{L}(\theta^{(m)}; \mathcal{D}_{\text{LF}})$$

**Stage 2 - High-Fidelity Fine-tuning**: Fine-tune on limited high-resolution data with transfer learning:
$$\theta_{\text{HF}}^{(m)*} = \arg\min_{\theta^{(m)}} \mathcal{L}(\theta^{(m)}; \mathcal{D}_{\text{HF}}) + \beta\|\theta^{(m)} - \theta_{\text{LF}}^{(m)*}\|^2$$

where $\beta$ controls the strength of regularization toward the pre-trained weights.

#### 2.3.2 Calibration with Conformal Prediction

To ensure well-calibrated prediction intervals, we employ conformal prediction adapted for multi-fidelity settings. For a target coverage level $1-\alpha$, we compute calibrated prediction intervals:

1. Split high-fidelity data into training $\mathcal{D}_{\text{train}}$ and calibration $\mathcal{D}_{\text{cal}}$ sets
2. Train ensemble on $\mathcal{D}_{\text{train}}$
3. Compute ensemble predictions and nonconformity scores on $\mathcal{D}_{\text{cal}}$:
$$s_i = |\mathbf{y}_i - \bar{\boldsymbol{\mu}}(\mathbf{x}_i)|$$
where $\bar{\boldsymbol{\mu}}(\mathbf{x}) = \frac{1}{M}\sum_{m=1}^M \boldsymbol{\mu}^{(m)}(\mathbf{x})$
4. Determine quantile $q = \text{Quantile}_{1-\alpha}(\{s_i\})$
5. Construct prediction intervals: $[\bar{\boldsymbol{\mu}}(\mathbf{x}) - q, \bar{\boldsymbol{\mu}}(\mathbf{x}) + q]$

#### 2.3.3 Observational Data Integration

To further calibrate predictions against sparse observational data, we use a Bayesian correction:
$$p(\mathbf{y}|\mathbf{x}, \mathcal{D}_{\text{obs}}) \propto p(\mathbf{y}|\mathbf{x}, \mathcal{D}_{\text{sim}}) \cdot p(\mathcal{D}_{\text{obs}}|\mathbf{y})$$

This allows incorporating observational constraints while maintaining physical consistency from simulations.

### 2.4 Out-of-Distribution Detection

#### 2.4.1 Physics-Based Anomaly Scores

We develop a composite OOD detection score combining statistical and physics-based indicators:

**Ensemble Disagreement**: Measure epistemic uncertainty through ensemble variance:
$$U_{\text{epi}}(\mathbf{x}) = \frac{1}{M}\sum_{m=1}^M \|\boldsymbol{\mu}^{(m)}(\mathbf{x}) - \bar{\boldsymbol{\mu}}(\mathbf{x})\|^2$$

**Physics Violation Score**: Quantify the degree of constraint violation:
$$U_{\text{phys}}(\mathbf{x}) = w_1 \cdot E_{\text{viol}}(\mathbf{x}) + w_2 \cdot M_{\text{viol}}(\mathbf{x}) + w_3 \cdot P_{\text{viol}}(\mathbf{x})$$
where $E_{\text{viol}}$, $M_{\text{viol}}$, $P_{\text{viol}}$ measure energy, momentum, and mass conservation violations respectively.

**Mahalanobis Distance**: Measure distance from training distribution:
$$U_{\text{maha}}(\mathbf{x}) = \sqrt{(\mathbf{x} - \boldsymbol{\mu}_{\text{train}})^T \boldsymbol{\Sigma}_{\text{train}}^{-1} (\mathbf{x} - \boldsymbol{\mu}_{\text{train}})}$$

**Composite OOD Score**:
$$U_{\text{OOD}}(\mathbf{x}) = \alpha_1 U_{\text{epi}}(\mathbf{x}) + \alpha_2 U_{\text{phys}}(\mathbf{x}) + \alpha_3 U_{\text{maha}}(\mathbf{x})$$

When $U_{\text{OOD}}(\mathbf{x})$ exceeds a threshold $\tau$, the system flags the prediction as potentially unreliable.

### 2.5 Uncertainty Propagation Analysis

To understand how parameterization uncertainty affects overall climate predictions, we implement forward uncertainty propagation through the coupled climate model:

1. **Sample from ensemble**: Generate $K$ realizations from the ensemble posterior
2. **Run climate simulations**: Execute full climate model simulations with each sampled parameterization
3. **Analyze output statistics**: Compute mean, variance, and higher-order moments of climate variables
4. **Sensitivity analysis**: Use Sobol indices to decompose output variance:
$$S_i = \frac{\text{Var}_{x_i}[E_{x_{\sim i}}(Y|x_i)]}{\text{Var}(Y)}$$
where $S_i$ quantifies the contribution of input parameter $i$ to output variance.

### 2.6 Experimental Design and Validation

#### 2.6.1 Data Collection

**Training Data**:
- **High-resolution simulations**: 100-year runs of cloud-resolving models (e.g., SAM, WRF) at ~1km resolution
- **Coarse-resolution simulations**: 1000-year runs of CESM2 at ~100km resolution
- **Observational data**: ARM site measurements, satellite retrievals (CERES, CloudSat)

**Test Scenarios**:
- Historical period (1980-2020): Validation against reanalysis
- Future projections (2080-2100): SSP2-4.5 and SSP5-8.5 scenarios
- ENSO extreme phases: Strong El Niño and La Niña events

#### 2.6.2 Baseline Methods

Compare against:
- Single deterministic neural network
- Monte Carlo Dropout (Gal & Ghahramani, 2016)
- Standard deep ensembles without physics constraints
- Bayesian neural networks with variational inference
- Traditional climate model parameterizations

#### 2.6.3 Evaluation Metrics

**Predictive Performance**:
- Root Mean Squared Error (RMSE): $\text{RMSE} = \sqrt{\frac{1}{N}\sum_{i=1}^N (\mathbf{y}_i - \bar{\boldsymbol{\mu}}(\mathbf{x}_i))^2}$
- Mean Absolute Error (MAE)
- Temporal correlation for time-series predictions

**Uncertainty Calibration**:
- **Prediction Interval Coverage Probability (PICP)**: Fraction of true values within predicted intervals
$$\text{PICP} = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[\mathbf{y}_i \in [\bar{\boldsymbol{\mu}}(\mathbf{x}_i) - q, \bar{\boldsymbol{\mu}}(\mathbf{x}_i) + q]]$$
Target: PICP $\approx 1-\alpha$ for coverage level $\alpha$

- **Continuous Ranked Probability Score (CRPS)**: Measures calibration of probabilistic forecasts
$$\text{CRPS}(\mathbf{y}, F) = \int_{-\infty}^{\infty} (F(z) - \mathbb{1}[z \geq \mathbf{y}])^2 dz$$

- **Reliability diagrams**: Plot observed frequency vs. predicted probability

**Physics Consistency**:
- Energy conservation error: $E_{\text{err}} = \frac{1}{N}\sum_{i=1}^N |\Delta E_i - (Q_i - W_i)|$
- Mass conservation violation rate
- Momentum budget closure

**OOD Detection Performance**:
- AUROC for distinguishing in-distribution vs. OOD samples
- False positive rate at 95% true positive rate

**Climate-Specific Metrics**:
- Accuracy in capturing extreme percentiles (95th, 99th)
- Skill in predicting climate indices (ENSO, NAO)
- Performance on HILL events (defined as >3σ events)

#### 2.6.4 Ablation Studies

Conduct systematic ablation studies to assess component contributions:
1. Effect of physics constraints vs. unconstrained ensembles
2. Impact of multi-fidelity training vs. single-fidelity
3. Value of OOD detection mechanisms
4. Sensitivity to ensemble size $M$
5. Importance of different physics constraint terms ($\lambda_1, \lambda_2, \lambda_3$)

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Technical Deliverables**:

1. **Open-source software framework**: A modular, well-documented Python package implementing the proposed UQ methods, compatible with major climate modeling frameworks (CESM, E3SM, GFDL).

2. **Calibrated uncertainty estimates**: Demonstrable improvement in uncertainty calibration metrics (PICP within 5% of nominal coverage, CRPS reduction of 20-30% vs. baselines) for key climate variables including temperature, precipitation, and cloud cover.

3. **Physics-consistent predictions**: Ensemble predictions that maintain conservation properties with violation rates <1% for energy, mass, and momentum budgets, compared to 5-10% for unconstrained ML models.

4. **Improved extreme event prediction**: Enhanced skill scores (15-25% improvement in RMSE) for HILL events, particularly for temperature extremes beyond the 99th percentile and unprecedented precipitation patterns.

5. **OOD detection capability**: Reliable flagging of out-of-distribution climate states with AUROC >0.85, enabling climate scientists to identify when model predictions require additional scrutiny.

6. **Uncertainty decomposition**: Quantitative attribution of prediction uncertainty to epistemic (model) vs. aleatoric (inherent variability) sources, and identification of dominant uncertainty propagation pathways through climate system components.

**Scientific Contributions**:

1. **Methodological advances**: Novel integration of physics constraints with ensemble methods and multi-fidelity calibration, advancing the field of uncertainty quantification in scientific machine learning.

2. **Climate science insights**: Better characterization of uncertainty in climate tipping points (e.g., AMOC collapse, Arctic sea ice loss, Amazon rainforest dieback) and identification of early warning signals for critical transitions.

3. **Improved process understanding**: Uncertainty sensitivity analysis revealing which subgrid processes contribute most to prediction uncertainty, guiding future model development priorities.

### 3.2 Impact

**Immediate Impact (1-3 years)**:

- **Accelerated hybrid model adoption**: By providing trustworthy UQ tools, reduce barriers to operational deployment of ML-based parameterizations in major climate models (CESM, UKESM, MPI-ESM), potentially achieving 10-100x speedups in climate projections.

- **Enhanced risk assessment**: Enable more nuanced climate risk analysis for stakeholders by providing calibrated probability distributions for extreme events, improving disaster preparedness and infrastructure planning.

- **Community resource**: The open-source framework will serve as a benchmark and development platform for the climate ML community, fostering collaborative research.

**Medium-term Impact (3-7 years)**:

- **Operational climate services**: Integration into climate projection systems used by IPCC assessments and national climate agencies, improving the reliability of information used for multi-billion dollar adaptation investments.

- **Paradigm shift in climate modeling**: Demonstrated success could catalyze broader acceptance of hybrid physics-ML approaches, transforming the field from skepticism to strategic integration.

- **Cross-domain applications**: Extension of the UQ framework to related Earth system domains including ocean modeling, hydrology, and air quality prediction.

**Long-term Impact (7+ years)**:

- **Improved climate projections**: More accurate and better-calibrated long-term climate projections, reducing the "deep uncertainty" that currently hampers climate policy decisions.

- **Scientific ML methodology**: The physics-constrained ensemble approach could influence uncertainty quantification practices across scientific computing domains (fluid dynamics, materials science, systems biology).

- **Decision support transformation**: Enable new classes of climate-informed decision-making tools that properly account for multiple uncertainty sources, from agricultural planning to financial risk assessment.

### 3.3 Broader Implications

This research addresses a critical gap at the intersection of machine learning and climate science. By demonstrating that ML methods can provide not just accurate predictions but also reliable uncertainty estimates that respect physical principles, this work has the potential to transform how the climate science community views and adopts AI technologies. The framework's emphasis on interpretability through physics constraints and explicit OOD detection aligns with the scientific values of the domain science community, potentially accelerating AI adoption where purely data-driven approaches have faced resistance.

Furthermore, the hierarchical approach to uncertainty—from ensemble diversity capturing epistemic uncertainty, to heteroscedastic modeling capturing aleatoric uncertainty, to physics-based anomaly detection—provides a template for trustworthy AI in high-stakes scientific applications. The methods developed here could inform AI safety practices more broadly, particularly for applications where physical consistency and reliable uncertainty quantification are paramount.

Ultimately, by enabling more efficient yet trustworthy climate projections, this research contributes to humanity's ability to understand and respond to climate change—one of the defining challenges of our time. The improved characterization of climate risks, particularly for extreme events and potential tipping points, has direct implications for protecting vulnerable populations, preserving ecosystems, and guiding the transition to a sustainable future.