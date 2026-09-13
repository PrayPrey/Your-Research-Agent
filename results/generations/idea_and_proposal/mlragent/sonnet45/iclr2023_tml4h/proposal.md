# Research Proposal: Conformal Prediction with Causal Calibration for Trustworthy Clinical Decision Support

## 1. Title

**Causally-Calibrated Conformal Prediction: A Framework for Fair and Interpretable Uncertainty Quantification in Clinical Decision Support Systems**

## 2. Introduction

### Background

Machine learning (ML) has demonstrated remarkable performance in healthcare applications, from diagnostic imaging to treatment recommendation and risk prediction. Despite these successes, the translation of ML models into clinical practice remains limited. A fundamental barrier is the lack of trustworthy uncertainty quantification: clinicians require not only accurate predictions but also reliable confidence estimates to make informed decisions, particularly in high-stakes scenarios where errors can have life-threatening consequences.

Traditional ML approaches typically provide point predictions without meaningful uncertainty estimates. Even when probabilistic methods are employed, the resulting confidence intervals often lack theoretical guarantees and may be poorly calibrated across different patient populations. This is particularly problematic given the well-documented presence of dataset biases, spurious correlations, and shortcut learning in medical data. For instance, ML models may learn to associate certain demographics with disease outcomes not due to causal biological mechanisms but due to healthcare access disparities or documentation biases in electronic health records.

Conformal prediction has emerged as a promising framework for distribution-free uncertainty quantification, offering finite-sample coverage guarantees without strong distributional assumptions. However, standard conformal methods can produce miscalibrated prediction sets across patient subgroups when applied to biased medical datasets. The prediction intervals may be too narrow for underrepresented populations (providing false confidence) or too wide for well-represented groups (limiting clinical utility). This undermines both fairness and trustworthiness.

Recent advances in causal inference provide tools to distinguish genuine causal relationships from spurious correlations. Meanwhile, emerging work has begun exploring the intersection of conformal prediction with fairness considerations and hierarchical uncertainty quantification. However, a systematic framework that integrates causal reasoning into conformal calibration to simultaneously address generalization, fairness, and explainability in clinical settings remains an open challenge.

### Research Objectives

This research proposes to develop and validate a novel framework—**Causally-Calibrated Conformal Prediction (C³P)**—that combines causal inference with conformal prediction to provide reliable, fair, and interpretable uncertainty estimates for clinical decision support. The specific objectives are:

1. **Develop causal discovery methods** tailored to multimodal medical data to identify spurious correlations and confounding factors that lead to shortcut learning
2. **Design causally-informed conformity scores** that condition on causal mechanisms rather than all available covariates, preventing bias amplification
3. **Establish stratified calibration procedures** ensuring valid coverage guarantees across clinically-relevant subgroups defined by causal variables
4. **Create interpretable prediction intervals** where interval width reflects true epistemic uncertainty rather than dataset artifacts
5. **Validate the framework** on multiple clinical tasks and demonstrate improved fairness, generalization, and trustworthiness compared to standard approaches

### Significance

This research addresses critical gaps at the intersection of trustworthy ML and healthcare:

- **Fairness**: By explicitly modeling causal structures, the framework protects vulnerable populations from biased predictions that arise from spurious correlations in training data
- **Generalization**: Causal conditioning enables prediction sets that remain valid under distribution shift, including temporal changes and geographic variations
- **Explainability**: The causal graph provides clinicians with transparent insight into which factors genuinely influence predictions versus artifacts
- **Clinical adoption**: Provable coverage guarantees combined with fairness and interpretability can increase clinician trust and facilitate regulatory approval

The impact extends beyond individual clinical applications to establish principled methodologies for trustworthy uncertainty quantification in high-stakes ML deployment.

## 3. Methodology

### 3.1 Overview

The C³P framework consists of four integrated components: (1) causal structure learning, (2) causally-informed conformity score design, (3) stratified conformal calibration, and (4) adaptive prediction set generation. We detail each component below.

### 3.2 Causal Structure Learning

**Objective**: Discover the causal graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where nodes $\mathcal{V}$ represent variables (features $X$, outcome $Y$, potential confounders $C$) and directed edges $\mathcal{E}$ encode causal relationships.

**Algorithm**:

1. **Constraint-based discovery**: Apply conditional independence tests to identify the Markov equivalence class of causal structures. For continuous variables, use partial correlation tests; for mixed data types, employ kernel-based conditional independence tests:
   $$\text{CI}(X_i, X_j | \mathbf{X}_S) \iff X_i \perp\!\!\!\perp X_j | \mathbf{X}_S$$
   where $\mathbf{X}_S$ is a conditioning set.

2. **Score-based refinement**: Within the equivalence class, employ Bayesian information criterion (BIC) scoring with structural equation models (SEMs) to select the most plausible graph:
   $$\text{Score}(\mathcal{G}) = \log P(\mathbf{D}|\mathcal{G}) - \frac{d}{2}\log n$$
   where $\mathbf{D}$ is the data, $d$ is the model degrees of freedom, and $n$ is sample size.

3. **Domain knowledge integration**: Incorporate clinical expert knowledge as constraints (e.g., demographic variables cannot be caused by disease outcomes) using structured priors.

4. **Multimodal extension**: For heterogeneous data (imaging, text, structured records), learn modality-specific subgraphs and then integrate via cross-modal edges using attention-based mechanisms to weight inter-modal dependencies.

**Output**: A causal DAG $\hat{\mathcal{G}}$ with identified causal parents $\text{Pa}(Y)$ of the outcome and confounders $C$ that create spurious associations.

### 3.3 Causally-Informed Conformity Scores

**Standard conformal prediction**: Given calibration data $\{(X_i, Y_i)\}_{i=1}^n$, compute conformity scores $s_i = s(X_i, Y_i)$ measuring how well each sample conforms to the model. For regression with predictor $\hat{\mu}$:
$$s_i = |Y_i - \hat{\mu}(X_i)|$$

**Problem**: Standard scores condition on all features $X$, incorporating both causal and spurious associations.

**Proposed causally-informed scores**: Define conformity scores that condition only on causal parents and adjust for confounders:

For regression:
$$s_i^{\text{causal}} = |Y_i - \hat{\mu}(\text{Pa}(Y)_i)| \cdot w(C_i)$$

where $w(C_i)$ is a weighting function that downweights samples with confounder values that are overrepresented in training data:
$$w(C_i) = \min\left(1, \frac{\bar{p}(C)}{p_{\text{train}}(C_i)}\right)^{\alpha}$$

Here $p_{\text{train}}(C_i)$ is the empirical density of confounders in training data, $\bar{p}(C)$ is the target (uniform) density, and $\alpha \in [0,1]$ controls the strength of reweighting.

For classification with probability predictor $\hat{\pi}(y|X)$:
$$s_i^{\text{causal}} = 1 - \hat{\pi}(Y_i | \text{Pa}(Y)_i) \cdot w(C_i)$$

**Rationale**: By conditioning only on causal parents and reweighting by confounders, these scores reflect genuine predictive uncertainty rather than sampling artifacts.

### 3.4 Stratified Conformal Calibration

**Objective**: Ensure valid coverage across clinically-relevant subgroups.

**Algorithm**:

1. **Subgroup definition**: Using the causal graph, identify protected attributes $A \subseteq C$ (e.g., race, sex, socioeconomic status) and clinically-meaningful stratification variables $S$ (e.g., disease severity, comorbidity profiles).

2. **Group-conditional calibration**: For each group $g \in \mathcal{G} = A \times S$, construct group-specific prediction sets. Split data into training $\mathcal{D}_{\text{train}}$, calibration $\mathcal{D}_{\text{cal}}$, and test $\mathcal{D}_{\text{test}}$.

3. **Compute group quantiles**: For each group $g$ with calibration samples $\{(X_i, Y_i)\}_{i \in \mathcal{I}_g}$:
   $$\hat{q}_g(\alpha) = \text{Quantile}\left(\{s_i^{\text{causal}}\}_{i \in \mathcal{I}_g}, \frac{\lceil (|\mathcal{I}_g|+1)(1-\alpha) \rceil}{|\mathcal{I}_g|}\right)$$

4. **Adaptive group assignment**: For test sample $X_{\text{new}}$, identify group membership $g(X_{\text{new}})$ and construct prediction set:
   $$\mathcal{C}(X_{\text{new}}) = \{y : s(X_{\text{new}}, y) \leq \hat{q}_{g(X_{\text{new}})}(\alpha)\}$$

**Theoretical guarantee**: Under the exchangeability assumption within groups, this provides:
$$P(Y_{\text{new}} \in \mathcal{C}(X_{\text{new}}) | G = g) \geq 1 - \alpha, \quad \forall g$$

### 3.5 Interpretable Prediction Set Generation

**Width-based uncertainty interpretation**: The prediction interval width $w_i = |\mathcal{C}(X_i)|$ provides an interpretable measure of epistemic uncertainty:

$$w_i = \hat{q}_{g(X_i)}(\alpha) - \hat{q}_{g(X_i)}(1-\alpha)$$

**Decomposition**: Decompose uncertainty into aleatoric (irreducible) and epistemic (model) components using ensemble methods:

$$\text{Var}[Y|X] = \underbrace{\mathbb{E}_{\theta}[\text{Var}[Y|X,\theta]]}_{\text{aleatoric}} + \underbrace{\text{Var}_{\theta}[\mathbb{E}[Y|X,\theta]]}_{\text{epistemic}}$$

where $\theta$ indexes models in the ensemble.

**Visualization**: Provide clinicians with:
- Prediction interval plots with causal factor annotations
- Comparison of interval widths across subgroups to identify fairness issues
- Causal pathway diagrams showing which factors contribute to uncertainty

### 3.6 Data Collection and Experimental Design

**Datasets**: Validate across three diverse clinical tasks:

1. **MIMIC-IV**: ICU mortality and readmission prediction using structured EHR data (demographics, vitals, lab values, medications)
2. **CheXpert**: Chest X-ray diagnosis with demographic information to assess fairness across age, sex, and race
3. **Type 2 Diabetes Risk**: Multi-site cohort study with longitudinal data to test temporal and geographic generalization

**Experimental protocol**:

1. **Baseline comparisons**: Compare C³P against:
   - Standard conformal prediction (full covariate conditioning)
   - Mondrian conformal prediction (simple stratification without causal reasoning)
   - Bayesian uncertainty quantification (Gaussian processes, Bayesian neural networks)
   - Ensemble methods (deep ensembles, Monte Carlo dropout)

2. **Evaluation metrics**:
   - **Coverage**: Empirical coverage $\frac{1}{n}\sum_{i=1}^n \mathbb{1}(Y_i \in \mathcal{C}(X_i))$ overall and per group
   - **Efficiency**: Average prediction set size $\frac{1}{n}\sum_{i=1}^n |\mathcal{C}(X_i)|$
   - **Fairness**: Coverage disparity $\max_{g,g'} |Cov_g - Cov_{g'}|$ and size disparity across groups
   - **Calibration**: Expected calibration error (ECE) and reliability diagrams
   - **Generalization**: Coverage maintenance under temporal and geographic distribution shift

3. **Ablation studies**:
   - Effect of causal graph quality (oracle vs. learned graphs)
   - Impact of conformity score weighting ($\alpha$ parameter)
   - Sensitivity to calibration set size
   - Contribution of each component (causal conditioning, reweighting, stratification)

4. **Clinical validation**:
   - Retrospective evaluation on held-out patient cohorts
   - Clinician survey assessing interpretability and trust (5-point Likert scale)
   - Comparison of decision-making with and without C³P uncertainty estimates

### 3.7 Implementation Details

**Software framework**: Implement in Python using:
- PyTorch for neural network models
- `causal-learn` for causal discovery algorithms
- `MAPIE` and custom extensions for conformal prediction
- `fairlearn` for fairness metrics

**Computational requirements**: Training on standard GPU workstations (NVIDIA A100). Causal discovery is the bottleneck; employ approximate methods for graphs with >100 nodes.

**Hyperparameter tuning**: Use nested cross-validation to select:
- Model architecture and regularization
- Causal discovery algorithm parameters
- Reweighting strength $\alpha$
- Stratification granularity

## 4. Expected Outcomes & Impact

### Expected Outcomes

1. **Theoretical contributions**:
   - Formal characterization of when causal conditioning improves conformal prediction coverage under distribution shift
   - Finite-sample coverage guarantees for stratified causal conformal prediction
   - Bounds on fairness metrics (coverage disparity) as a function of confounder adjustment

2. **Methodological advances**:
   - Scalable algorithms for causal structure learning in multimodal medical data
   - Novel conformity scores that integrate causal reasoning and fairness considerations
   - Adaptive stratification schemes balancing group-specific coverage and efficiency

3. **Empirical validation**:
   - Demonstration of 10-20% reduction in coverage disparity across demographic groups compared to baselines while maintaining nominal coverage (95%)
   - Improved generalization: coverage degradation under temporal shift reduced by 15-25%
   - Efficiency gains: 5-15% smaller prediction sets compared to fairness-aware baselines with equivalent coverage
   - Clinician preference: ≥80% agreement that C³P intervals are more trustworthy and interpretable than standard methods

4. **Software and benchmarks**:
   - Open-source implementation of the C³P framework
   - Benchmark datasets with causal graphs for reproducible evaluation
   - Standardized fairness and uncertainty evaluation protocols

### Impact

**Scientific impact**: This research advances the theoretical foundations of trustworthy ML by bridging causal inference and uncertainty quantification. It provides a principled framework for addressing fairness, generalization, and explainability simultaneously—challenges that are often treated in isolation. The work will contribute to multiple communities: conformal prediction, causal inference, fairness in ML, and healthcare AI.

**Clinical impact**: By providing reliable, fair, and interpretable uncertainty estimates, C³P can accelerate ML adoption in clinical practice. Specific applications include:
- Treatment selection under uncertainty (e.g., choosing between treatment options when predictions have wide intervals)
- Risk stratification with fairness guarantees (e.g., ensuring equitable triage across patient populations)
- Clinical trial enrollment (e.g., identifying patients for whom current evidence is insufficient)
- Human-AI collaboration (e.g., flagging cases requiring expert review based on uncertainty)

**Regulatory and ethical impact**: The framework addresses key concerns raised by regulatory bodies (FDA, EMA) regarding ML transparency and fairness. Provable coverage guarantees and explicit fairness metrics can support regulatory submissions. The causal interpretability component aids in satisfying explainability requirements.

**Broader societal impact**: By preventing bias amplification and ensuring equitable uncertainty quantification, this work contributes to reducing healthcare disparities. It provides tools to identify and mitigate unfair ML predictions that could harm vulnerable populations, aligning with principles of beneficence and justice in medical ethics.

**Future directions**: This research opens several avenues for extension:
- Active learning strategies that use causal uncertainty to guide data collection
- Federated learning with causally-calibrated conformal prediction for privacy-preserving multi-site collaboration
- Integration with causal effect estimation for personalized treatment recommendations
- Extension to time-series and longitudinal prediction tasks with temporal causal models

In conclusion, the proposed C³P framework represents a significant step toward trustworthy ML in healthcare, addressing fundamental challenges in uncertainty quantification, fairness, and interpretability through the principled integration of causal inference and conformal prediction.