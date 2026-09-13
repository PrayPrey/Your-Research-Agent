# Uncertainty-Aware Deep Learning for Climate Model Emulation: Bridging the Gap Between Prediction Accuracy and Decision-Making Trust

## 1. Introduction

### Background

Climate change represents one of the most pressing challenges facing humanity, directly impacting multiple United Nations Sustainable Development Goals including climate action (SDG 13), zero hunger (SDG 2), and sustainable cities and communities (SDG 11). Numerical climate models, particularly Earth System Models (ESMs), serve as critical tools for understanding climate dynamics and informing policy decisions. However, these physics-based models require substantial computational resources, with high-resolution simulations often taking weeks to months on supercomputers. This computational burden severely limits their applicability in real-time decision-making contexts such as disaster response, agricultural planning, and infrastructure development.

Deep learning-based climate model emulators have emerged as a promising solution, offering speedups of several orders of magnitude while maintaining reasonable accuracy. Physics-Informed Neural Networks (PINNs) represent a particularly attractive approach, embedding physical laws directly into the learning process through partial differential equations (PDEs). Despite these technical advances, a critical gap exists between model performance on academic benchmarks and successful deployment in sustainability applications. This gap exemplifies a fundamental pitfall in computational sustainability: high prediction accuracy does not automatically translate to stakeholder trust or real-world impact.

The deployment challenge stems from multiple factors. First, climate decisions carry long-term societal and environmental consequences, making decision-makers rightfully cautious about black-box predictions. Second, traditional machine learning metrics (RMSE, R², etc.) fail to capture the reliability and trustworthiness requirements of high-stakes applications. Third, most deep learning approaches provide point estimates without statistically rigorous uncertainty quantification, leaving stakeholders unable to assess prediction reliability. Finally, even when uncertainty estimates exist, they are often presented in technical formats incomprehensible to policymakers, NGO workers, and community leaders who ultimately make implementation decisions.

### Research Objectives

This research proposal aims to develop and validate a comprehensive framework for uncertainty-aware climate model emulation that explicitly addresses the theory-to-deployment gap. The specific objectives are:

1. **Develop hybrid ensemble-PINN architectures** that preserve physical constraints while providing diverse predictions for robust uncertainty estimation
2. **Implement conformal prediction techniques** to deliver statistically valid, distribution-free uncertainty bounds with finite-sample coverage guarantees
3. **Design interpretable uncertainty communication tools** tailored to non-technical sustainability stakeholders
4. **Validate the framework through real-world deployment** in partnership with sustainability organizations on high-impact applications
5. **Establish deployment metrics and best practices** that extend beyond accuracy to measure stakeholder trust, adoption rates, and decision quality

### Significance

This research addresses both primary themes of the CompSust 2023 workshop. For the "theory to deployment" pathway, it provides concrete methodologies and validation procedures for transitioning from academic prototypes to operational systems. For "promises and pitfalls," it directly confronts the documented failure mode where technically sophisticated models fail to achieve real-world impact due to inadequate uncertainty communication.

The expected contributions include: (1) novel algorithmic frameworks combining ensemble methods, physics-informed learning, and conformal prediction; (2) empirically validated uncertainty visualization techniques for sustainability contexts; (3) documented case studies providing replicable deployment patterns; and (4) comprehensive evaluation frameworks that measure success beyond traditional ML metrics. These contributions will benefit both the computational sustainability community and the broader machine learning field by demonstrating rigorous approaches to responsible AI deployment in high-stakes domains.

## 2. Methodology

### 2.1 Data Collection and Preparation

**Climate Model Data**: We will utilize publicly available climate simulation datasets from the Coupled Model Intercomparison Project Phase 6 (CMIP6), focusing on variables critical to sustainability applications: temperature, precipitation, soil moisture, and extreme event indicators. Data will span multiple spatial resolutions (from 1° to 0.25° grids) and temporal scales (daily to monthly aggregations).

**Observational Data**: To ground-truth emulator predictions and calibrate uncertainty estimates, we will incorporate observational datasets including ERA5 reanalysis, satellite measurements (MODIS, GRACE), and in-situ measurements from weather stations and agricultural monitoring networks.

**Application-Specific Data**: For deployment case studies, we will collect domain-specific datasets in partnership with sustainability organizations:
- Crop yield data from agricultural agencies for food security applications
- Hydrological measurements and flood records for disaster preparedness
- Regional climate impact assessments for policy planning

**Data Partitioning**: Following best practices in conformal prediction, data will be split into: training set (60%), calibration set (20%) for uncertainty quantification, and held-out test set (20%) for final evaluation.

### 2.2 Physics-Informed Ensemble Neural Networks

**Architecture Design**: We propose a hybrid ensemble architecture combining the physical consistency of PINNs with the uncertainty quantification capabilities of ensemble methods.

For a climate variable $u(\mathbf{x}, t)$ governed by a PDE:
$$\mathcal{L}[u] = f(\mathbf{x}, t)$$

where $\mathcal{L}$ is a differential operator and $f$ represents forcing terms, each ensemble member $u_i(\mathbf{x}, t; \theta_i)$ is trained with the loss function:

$$\mathcal{J}_i(\theta_i) = \lambda_{\text{data}} \mathcal{J}_{\text{data}}^i + \lambda_{\text{PDE}} \mathcal{J}_{\text{PDE}}^i + \lambda_{\text{BC}} \mathcal{J}_{\text{BC}}^i + \lambda_{\text{diversity}} \mathcal{J}_{\text{diversity}}^i$$

The data loss ensures consistency with observations:
$$\mathcal{J}_{\text{data}}^i = \frac{1}{N_d} \sum_{j=1}^{N_d} \|u_i(\mathbf{x}_j, t_j; \theta_i) - u_j^{\text{obs}}\|^2$$

The PDE loss enforces physical constraints:
$$\mathcal{J}_{\text{PDE}}^i = \frac{1}{N_c} \sum_{k=1}^{N_c} \|\mathcal{L}[u_i](\mathbf{x}_k, t_k) - f(\mathbf{x}_k, t_k)\|^2$$

The boundary condition loss ensures physical validity at domain boundaries:
$$\mathcal{J}_{\text{BC}}^i = \frac{1}{N_b} \sum_{m=1}^{N_b} \|u_i(\mathbf{x}_m, t_m; \theta_i) - g(\mathbf{x}_m, t_m)\|^2$$

The diversity loss promotes ensemble heterogeneity:
$$\mathcal{J}_{\text{diversity}}^i = -\frac{1}{N_d N_e} \sum_{j=1}^{N_d} \sum_{k \neq i}^{N_e} \|u_i(\mathbf{x}_j, t_j; \theta_i) - u_k(\mathbf{x}_j, t_j; \theta_k)\|^2$$

**Ensemble Construction**: We will create diversity through multiple mechanisms:
1. Different random initializations
2. Bootstrapped training data subsets
3. Architectural variations (depth, width, activation functions)
4. Different collocation point sampling strategies for PDE loss

### 2.3 Conformal Prediction for Calibrated Uncertainty Quantification

Conformal prediction provides distribution-free uncertainty estimates with finite-sample coverage guarantees, making it ideal for high-stakes sustainability applications.

**Conformal Framework**: For a desired coverage level $1-\alpha$ (e.g., 90%), we construct prediction intervals that contain the true value with at least this probability.

Given ensemble predictions $\{u_1(\mathbf{x}, t), \ldots, u_{N_e}(\mathbf{x}, t)\}$, we define:
- Ensemble mean: $\bar{u}(\mathbf{x}, t) = \frac{1}{N_e} \sum_{i=1}^{N_e} u_i(\mathbf{x}, t)$
- Ensemble variance: $\sigma^2(\mathbf{x}, t) = \frac{1}{N_e} \sum_{i=1}^{N_e} (u_i(\mathbf{x}, t) - \bar{u}(\mathbf{x}, t))^2$

**Nonconformity Score**: For calibration set examples, we compute:
$$S_j = \frac{|u_j^{\text{obs}} - \bar{u}(\mathbf{x}_j, t_j)|}{\sigma(\mathbf{x}_j, t_j) + \epsilon}$$

where $\epsilon$ prevents division by zero.

**Quantile Calculation**: The conformal quantile is:
$$\hat{q} = \text{Quantile}(S_1, \ldots, S_{N_{\text{cal}}}, 1-\alpha)$$

**Prediction Intervals**: For new inputs, the conformal prediction interval is:
$$[\bar{u}(\mathbf{x}, t) - \hat{q}\sigma(\mathbf{x}, t), \bar{u}(\mathbf{x}, t) + \hat{q}\sigma(\mathbf{x}, t)]$$

**Spatially Adaptive Uncertainty**: To address heteroskedasticity, we implement locally weighted conformal prediction, computing location-specific quantiles:
$$\hat{q}(\mathbf{x}) = \text{WeightedQuantile}(\{S_j, w_j(\mathbf{x})\}_{j=1}^{N_{\text{cal}}}, 1-\alpha)$$

where weights $w_j(\mathbf{x})$ are based on spatial proximity or feature similarity.

### 2.4 Interpretable Uncertainty Communication

**Multi-Level Visualization Framework**: We develop a tiered communication system:

**Level 1 - Executive Summary**: Single-metric trust scores combining prediction confidence and historical accuracy:
$$\text{Trust Score} = \frac{1}{2}(1 - \text{Normalized Uncertainty}) + \frac{1}{2}(\text{Historical Accuracy})$$

**Level 2 - Visual Uncertainty Maps**: Spatially resolved uncertainty visualizations using:
- Color-coded confidence levels (high/medium/low confidence zones)
- Contour plots showing prediction intervals
- Ensemble spread visualizations highlighting agreement/disagreement regions

**Level 3 - Scenario Exploration**: Interactive tools allowing stakeholders to:
- Query specific locations and time periods
- Compare predictions under different emission scenarios
- Explore worst-case and best-case ensemble members

**Level 4 - Technical Details**: For expert users, provide:
- Complete ensemble distributions
- Conformity scores and calibration diagnostics
- Physical constraint satisfaction metrics

### 2.5 Active Learning for Efficient Training

To reduce computational costs and data requirements, we implement uncertainty-driven active learning:

**Acquisition Function**: Select new training points maximizing:
$$a(\mathbf{x}, t) = \alpha_1 \sigma(\mathbf{x}, t) + \alpha_2 \|\mathcal{L}[u](\mathbf{x}, t) - f(\mathbf{x}, t)\| + \alpha_3 d(\mathbf{x}, t)$$

where terms represent epistemic uncertainty, physics constraint violation, and spatial diversity respectively.

### 2.6 Experimental Design and Validation

**Phase 1 - Benchmark Evaluation**: 
- **Datasets**: CMIP6 temperature and precipitation projections
- **Baselines**: Standard PINNs, vanilla ensemble methods, Gaussian process emulators
- **Metrics**: RMSE, calibration error, coverage validity, computational efficiency
- **Evaluation**: K-fold cross-validation with temporal awareness

**Phase 2 - Deployment Case Studies**:

**Case Study 1: Crop Yield Prediction** (partnering with agricultural agencies)
- **Application**: Seasonal yield forecasting for food security planning
- **Variables**: Temperature, precipitation, soil moisture
- **Deployment Metrics**: Prediction accuracy, decision quality (planting recommendations), stakeholder satisfaction surveys
- **Timeline**: Two growing seasons (18 months)

**Case Study 2: Flood Forecasting** (partnering with disaster management organizations)
- **Application**: Urban flood risk assessment under climate change
- **Variables**: Extreme precipitation, runoff, river discharge
- **Deployment Metrics**: Early warning reliability, false alarm rates, evacuation decision quality
- **Timeline**: 12 months including monsoon season

**Case Study 3: Policy Planning** (partnering with regional climate offices)
- **Application**: Long-term climate adaptation planning
- **Variables**: Multi-decadal temperature and precipitation trends
- **Deployment Metrics**: Policy document citations, stakeholder trust surveys, comparative analysis with traditional methods
- **Timeline**: 24 months

**Phase 3 - User Studies**:
- **Participants**: 60 sustainability professionals (policymakers, NGO staff, climate officers)
- **Tasks**: Decision-making scenarios comparing different uncertainty presentation formats
- **Measurements**: Decision quality, confidence, comprehension, trust in predictions
- **Design**: Randomized controlled trials with different visualization approaches

**Evaluation Metrics**:

*Technical Metrics*:
- Prediction accuracy: RMSE, MAE, spatial correlation
- Calibration: Expected Calibration Error (ECE), coverage diagnostics
- Efficiency: Training time, inference speed, sample complexity

*Deployment Metrics*:
- Stakeholder trust: Validated psychometric scales
- Adoption rate: Percentage of recommendations acted upon
- Decision quality: Comparing outcomes to ground truth
- Comprehension: Quiz scores on uncertainty interpretation
- Satisfaction: Likert-scale surveys on usability

*Impact Metrics*:
- Resource efficiency: Reduction in climate model computation requirements
- Decision timeliness: Time from query to actionable insight
- Risk mitigation: Quantified reduction in climate-related losses (where measurable)

## 3. Expected Outcomes & Impact

### Technical Outcomes

**Algorithmic Contributions**: The research will produce novel methodologies at the intersection of physics-informed learning, ensemble methods, and conformal prediction. We expect to demonstrate that hybrid ensemble-PINNs can achieve:
- 2-5× improvement in calibration metrics compared to standard PINNs
- Uncertainty estimates with empirically validated coverage guarantees (±2% of nominal level)
- 40-60% reduction in training data requirements through active learning
- 100-1000× speedup over full climate models while maintaining physical consistency

**Software and Tools**: All algorithms will be released as open-source packages with comprehensive documentation, enabling reproducibility and broader adoption. This includes:
- Modular PyTorch/TensorFlow implementations of ensemble-PINNs
- Conformal prediction libraries for climate applications
- Uncertainty visualization toolkit with customizable templates
- Pre-trained emulators for common climate variables and regions

### Deployment Outcomes

**Validated Best Practices**: Through case studies, we will establish evidence-based guidelines for deploying ML in sustainability contexts, addressing:
- Minimum uncertainty quantification requirements for different decision types
- Stakeholder engagement protocols during model development
- Validation procedures ensuring physical and statistical rigor
- Communication strategies for diverse audiences

**Measurable Impact**: Based on pilot discussions with partner organizations, we anticipate:
- 30-50% increase in stakeholder trust scores compared to black-box models
- 60-80% adoption rate for recommendations (vs. ~20% baseline)
- 25-40% improvement in decision quality metrics (e.g., crop yield optimization, flood preparedness)
- 10-15 sustainability organizations adopting the framework within 2 years

### Scientific Impact

**Addressing Workshop Themes**: This research directly contributes to both CompSust 2023 themes:

*Theory to Deployment Pathway*: We provide a concrete, validated roadmap including:
1. Technical requirements (calibrated uncertainty with coverage guarantees)
2. Communication protocols (multi-level visualization framework)
3. Validation procedures (combining technical and deployment metrics)
4. Partnership models (co-design with end-users)

*Promises and Pitfalls*: We explicitly document the pitfall that prediction accuracy alone is insufficient for deployment, and provide a promise—that properly communicated uncertainty can bridge the trust gap. By publishing comprehensive results including failure modes, we contribute to the community's understanding of what works and what doesn't.

**Broader ML Community**: This work advances uncertainty quantification, conformal prediction, and physics-informed learning research areas while demonstrating their real-world value. The multi-metric evaluation framework establishes standards for responsible AI deployment in high-stakes domains beyond climate.

**Sustainability Impact**: Ultimately, this research aims to democratize access to climate intelligence, enabling better-informed decisions across agriculture, disaster management, and policy planning. By making climate model predictions more accessible, trustworthy, and actionable, we support progress toward multiple UN SDGs, particularly SDG 13 (Climate Action), SDG 2 (Zero Hunger), and SDG 11 (Sustainable Cities).

### Long-term Vision

This project establishes foundations for a new paradigm in computational sustainability where uncertainty is not an afterthought but a central design principle. Success would inspire similar approaches in other sustainability domains (biodiversity monitoring, renewable energy forecasting, urban planning) and demonstrate that the gap between ML research and real-world impact can be systematically bridged through careful attention to uncertainty communication and stakeholder needs. The framework's extensibility ensures continued relevance as both climate science and machine learning methodologies evolve.