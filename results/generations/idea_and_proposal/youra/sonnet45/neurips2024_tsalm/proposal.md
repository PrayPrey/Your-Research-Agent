# Research Proposal: Time Series Complexity Profiling for Foundation Model Necessity Prediction

## 1. Title

**TSCP: A Lightweight Triage Framework for Predicting Foundation Model Necessity in Time Series Forecasting Through Information-Theoretic Complexity Profiling**

## 2. Introduction

### 2.1 Background

The emergence of foundation models has transformed machine learning across multiple domains, with time series forecasting being no exception. Recent works such as MOMENT, PatchTST, and Time-MoE have demonstrated the potential of large-scale pretrained models for time series tasks. However, a critical paradox has emerged: while foundation models achieve state-of-the-art performance on certain benchmarks, simple linear baselines like LTSF-Linear often match or exceed their performance on many real-world datasets, despite requiring orders of magnitude fewer computational resources.

This phenomenon creates a significant challenge for practitioners. Training and deploying foundation models requires substantial computational infrastructure (GPU clusters, extended training times, large memory footprints), yet the performance gains are highly dataset-dependent and unpredictable a priori. Current practice relies on post-hoc benchmarking—training multiple model classes and comparing their performance—which wastes resources when simpler models would suffice and delays deployment when foundation models are necessary.

The fundamental question remains unanswered: **Can we predict which model class will succeed based on intrinsic properties of the time series data before investing in expensive training?**

Recent evidence suggests this may be possible. Studies have shown that information-theoretic complexity metrics (Lyapunov exponents, Hurst exponents, entropy measures) correlate strongly with time series predictability and forecasting performance. However, no existing framework systematically leverages these metrics for pre-training model selection, leaving practitioners without principled guidelines for resource allocation.

### 2.2 Research Objectives

This research proposes **Time Series Complexity Profiling (TSCP)**, a lightweight triage system that predicts foundation model performance gains over linear baselines before any model training occurs. Our specific objectives are:

**Primary Objective:** Develop and validate an XGBoost-based classifier that predicts foundation model necessity with ≥80% accuracy in <10 seconds per time series, using 6-8 information-theoretic complexity metrics as features.

**Secondary Objectives:**
1. Establish the empirical relationship between complexity metrics and foundation model performance gains across 60-80 benchmark datasets
2. Design a three-tier triage system (Linear Sufficient, Marginal Benefit, Foundation Needed) with learned decision boundaries
3. Demonstrate computational efficiency gains of 10³-10⁵× compared to training foundation models for every problem
4. Validate generalization to out-of-domain datasets with ≥60% zero-shot accuracy
5. Provide interpretable feature importance rankings to understand which complexity properties drive foundation model necessity

### 2.3 Research Significance

**Theoretical Contributions:**
- **Formalization of complexity-performance relationships:** We establish the first systematic framework linking information-theoretic data properties to foundation model performance gaps, providing theoretical grounding for model selection
- **Cross-domain methodology transfer:** We adapt medical triage protocols (Emergency Severity Index) to machine learning model selection, demonstrating novel applications of decision-theoretic frameworks

**Methodological Contributions:**
- **Paradigm shift from post-hoc to predictive:** TSCP transforms model selection from comparative benchmarking (requiring full training) to predictive characterization (requiring only feature extraction)
- **Pre-training model selection framework:** First system enabling resource-efficient model class selection before training investment
- **Adaptive threshold learning:** Data-driven tier boundary optimization accommodating user-specific cost-benefit preferences

**Practical Contributions:**
- **Resource democratization:** Enables practitioners with limited computational budgets to make informed decisions about foundation model necessity
- **Computational savings:** Achieves 10³-10⁵× reduction in computational costs for model selection, with one-time setup amortizing after ~20 problems
- **Risk mitigation:** Prevents wasted resources on unnecessary foundation model training while identifying cases where simple models are insufficient

**Impact on Workshop Themes:**
This work directly addresses multiple workshop topics: (1) **Critiques on Time Series Foundation Models** by systematically identifying their limitations and failure modes, (2) **Analysis of Pretrained Time Series Models** through complexity-based characterization, and (3) **Real-World Applications** by providing practical tools for resource-constrained deployment scenarios.

## 3. Methodology

### 3.1 Research Design Overview

TSCP employs a supervised learning approach with two distinct phases:

**Phase 1 (One-Time Setup):** Train the triage classifier on benchmark datasets with known foundation model performance gaps

**Phase 2 (Deployment):** Apply the trained classifier to new time series for instant model recommendations

The core hypothesis is that complexity metrics extracted from raw time series data contain sufficient information to predict the performance gap between foundation models and linear baselines, enabling pre-training model selection.

### 3.2 Data Collection

#### 3.2.1 Benchmark Dataset Selection

We will compile 60-80 time series datasets spanning five domains to ensure diversity:

**Weather Domain (15-20 datasets):**
- ETTh1, ETTh2, ETTm1, ETTm2 (Electricity Transformer Temperature)
- Weather dataset (21 meteorological indicators)
- NOAA climate data subsets

**Traffic Domain (15-20 datasets):**
- Traffic dataset (San Francisco Bay Area road occupancy)
- PEMS-BAY, METR-LA (traffic speed)
- Uber movement data

**Energy Domain (10-15 datasets):**
- Electricity dataset (370 clients)
- Solar power generation datasets
- Building energy consumption (ASHRAE)

**Medical Domain (10-15 datasets):**
- PhysioNet Challenge datasets
- ECG time series (MIT-BIH)
- Patient vital signs monitoring

**Financial Domain (10-15 datasets):**
- Stock price indices (S&P 500 constituents)
- Cryptocurrency prices
- Exchange rates

**Selection Criteria:**
- Minimum length: 200 time points
- Publicly available and reproducible
- Diverse sampling frequencies (hourly, daily, weekly)
- Varying dimensionality (univariate and multivariate)

#### 3.2.2 Ground Truth Label Generation

For each dataset, we establish ground truth performance gaps through systematic benchmarking:

**Foundation Model Training:**
- Model: PatchTST (primary), MOMENT (validation)
- Configuration: Patch length = 16, stride = 8, 6 encoder layers
- Training: 80/20 train-test split, early stopping on validation loss
- Metric: Mean Squared Error (MSE) on test set

**Linear Baseline Training:**
- Model: LTSF-Linear (primary), ARIMA (validation)
- Configuration: Single linear layer per variate
- Training: Same data splits as foundation model
- Metric: MSE on identical test set

**Performance Gap Calculation:**

$$\text{Gap}(\%) = \frac{\text{MSE}_{\text{linear}} - \text{MSE}_{\text{foundation}}}{\text{MSE}_{\text{linear}}} \times 100$$

**Tier Assignment:**
- Tier 1 (Linear Sufficient): Gap < 5%
- Tier 2 (Marginal Benefit): 5% ≤ Gap < 15%
- Tier 3 (Foundation Needed): Gap ≥ 15%

### 3.3 Complexity Metric Extraction

We extract six core information-theoretic metrics from each time series, with optional extensions to eight metrics:

#### 3.3.1 Core Metrics (6)

**1. Entropy Rate ($H_{\text{rate}}$):**
Measures information content and randomness.

$$H_{\text{rate}} = -\sum_{i=1}^{N} p(x_i) \log_2 p(x_i)$$

where $p(x_i)$ is the probability of observing value $x_i$ in the discretized time series.

**Implementation:** Use histogram-based discretization with 10 bins, computed via `scipy.stats.entropy`.

**2. Sample Entropy ($SampEn$):**
Quantifies regularity and unpredictability.

$$SampEn(m, r, N) = -\ln\left(\frac{A}{B}\right)$$

where $A$ is the number of template matches of length $m+1$, $B$ is matches of length $m$, and $r$ is the tolerance threshold (typically $0.2 \times \text{std}(X)$).

**Implementation:** Use `nolds.sampen` with $m=2$, $r=0.2\sigma$.

**3. Largest Lyapunov Exponent ($\lambda_{\text{max}}$):**
Indicates chaotic behavior and sensitivity to initial conditions.

$$\lambda_{\text{max}} = \lim_{t \to \infty} \frac{1}{t} \ln\left(\frac{|\delta X(t)|}{|\delta X(0)|}\right)$$

where $\delta X(t)$ represents trajectory divergence.

**Implementation:** Use Rosenstein's algorithm via `nolds.lyap_r` with embedding dimension $d=10$.

**4. Hurst Exponent ($H$):**
Characterizes long-range dependence and self-similarity.

$$H = \frac{\log(R/S)}{\log(n)}$$

where $R$ is the range of cumulative deviations and $S$ is the standard deviation.

**Implementation:** Use rescaled range (R/S) analysis via `nolds.hurst_rs`.

**5. Fractal Dimension ($D_f$):**
Measures geometric complexity.

$$D_f = \lim_{\epsilon \to 0} \frac{\log N(\epsilon)}{\log(1/\epsilon)}$$

where $N(\epsilon)$ is the number of boxes of size $\epsilon$ needed to cover the time series trajectory.

**Implementation:** Use Higuchi's method via `pyeeg.hfd` with $k_{\text{max}}=10$.

**6. Autocorrelation Decay Rate ($\tau_{\text{AC}}$):**
Captures temporal structure persistence.

$$\rho(k) = \frac{\sum_{t=1}^{N-k}(x_t - \bar{x})(x_{t+k} - \bar{x})}{\sum_{t=1}^{N}(x_t - \bar{x})^2}$$

$$\tau_{\text{AC}} = \min\{k : |\rho(k)| < 0.1\}$$

**Implementation:** Compute autocorrelation via `statsmodels.tsa.stattools.acf`, find first crossing of 0.1 threshold.

#### 3.3.2 Optional Extensions (2)

**7. Approximate Entropy ($ApEn$):**
Alternative regularity measure, more robust to short series.

**8. Permutation Entropy ($PE$):**
Order-based complexity measure, computationally efficient.

### 3.4 Classifier Training

#### 3.4.1 Feature Engineering

**Preprocessing Pipeline:**
1. **Normalization:** Z-score standardization per time series
2. **Stationarity Check:** Augmented Dickey-Fuller test; apply differencing if $p > 0.05$
3. **Outlier Handling:** Winsorize at 1st and 99th percentiles
4. **Missing Data:** Linear interpolation for gaps <5% of series length

**Feature Matrix Construction:**

$$\mathbf{X} \in \mathbb{R}^{n \times d}$$

where $n$ is the number of datasets (60-80) and $d$ is the number of metrics (6-8).

**Label Vector:**

$$\mathbf{y} \in \{1, 2, 3\}^n$$

representing tier assignments.

#### 3.4.2 XGBoost Configuration

**Model Architecture:**
- Algorithm: XGBoost multi-class classifier
- Objective: `multi:softmax` (direct tier prediction)
- Evaluation metric: Multi-class log loss

**Hyperparameters:**
- `max_depth`: 5 (prevent overfitting on small dataset)
- `n_estimators`: 100
- `learning_rate`: 0.1
- `subsample`: 0.8
- `colsample_bytree`: 0.8
- `min_child_weight`: 3
- `gamma`: 0.1 (regularization)

**Training Procedure:**
1. Split data: 70% training, 15% validation, 15% test
2. 5-fold cross-validation on training set
3. Early stopping on validation log loss (patience = 10)
4. Final model trained on combined training + validation sets
5. Evaluation on held-out test set

**Computational Budget:**
- Training time: <1 GPU-hour (excluding benchmark model training)
- Memory: <2 GB
- Hardware: Single NVIDIA V100 or equivalent

### 3.5 Experimental Design

#### 3.5.1 Experiment 1: Baseline Performance Validation

**Objective:** Verify TSCP achieves ≥80% prediction accuracy.

**Procedure:**
1. Train TSCP on 70% of benchmark datasets
2. Evaluate on 15% validation set (hyperparameter tuning)
3. Final evaluation on 15% test set
4. Compute accuracy, precision, recall, F1-score per tier
5. Analyze confusion matrix for systematic errors

**Success Criteria:**
- Overall accuracy ≥ 80%
- Per-tier F1-score ≥ 0.75
- Pearson correlation between predicted and actual gaps: $r \geq 0.7$

#### 3.5.2 Experiment 2: Comparison with Heuristic Baselines

**Objective:** Demonstrate ≥20 percentage point improvement over simple heuristics.

**Baseline Methods:**
1. **Length-based heuristic:** Tier 3 if $N > 1000$, else Tier 1
2. **Domain-based heuristic:** Tier 3 for weather/traffic, Tier 1 for finance
3. **Variance-based heuristic:** Tier 3 if $\text{std}(X) > \text{median}(\text{std})$
4. **Random baseline:** Uniform random tier assignment

**Evaluation:**
- Compute accuracy for each baseline on test set
- Statistical significance testing: McNemar's test ($\alpha = 0.05$)
- Effect size: Cohen's $\kappa$ for agreement beyond chance

**Success Criteria:**
- TSCP accuracy - Best heuristic accuracy ≥ 20 percentage points
- $p < 0.05$ on McNemar's test

#### 3.5.3 Experiment 3: Feature Importance Analysis

**Objective:** Identify which complexity metrics drive predictions.

**Procedure:**
1. Extract SHAP values for each feature
2. Compute mean absolute SHAP value per metric
3. Rank metrics by importance
4. Ablation study: Remove top-3 metrics, retrain, measure accuracy drop

**Hypothesized Ranking:**
1. Largest Lyapunov Exponent (chaos indicator)
2. Hurst Exponent (long-range dependence)
3. Entropy Rate (randomness)

**Success Criteria:**
- Top-3 metrics account for ≥60% of total feature importance
- Removing top-3 metrics causes ≥15 percentage point accuracy drop

#### 3.5.4 Experiment 4: Out-of-Domain Generalization

**Objective:** Validate generalization to unseen domains.

**Procedure:**
1. **Zero-shot evaluation:** Train on 4 domains, test on 5th (leave-one-domain-out cross-validation)
2. **Few-shot adaptation:** Fine-tune with 5, 10, 20 labeled examples from held-out domain
3. Repeat for all 5 domains
4. Measure accuracy degradation and adaptation efficiency

**Success Criteria:**
- Zero-shot accuracy ≥ 60%
- 20-shot accuracy ≥ 75%
- Accuracy degradation ≤ 20 percentage points vs. in-domain

#### 3.5.5 Experiment 5: Computational Efficiency Validation

**Objective:** Confirm <10 second inference time and quantify savings.

**Procedure:**
1. Measure metric extraction time on CPU (Intel Xeon, 16 cores)
2. Measure XGBoost inference time
3. Compare to foundation model training time (PatchTST on V100)
4. Calculate speedup factor and cost savings

**Metrics:**
- Metric extraction time: $T_{\text{extract}}$
- Classifier inference time: $T_{\text{infer}}$
- Total TSCP time: $T_{\text{TSCP}} = T_{\text{extract}} + T_{\text{infer}}$
- Foundation model training time: $T_{\text{FM}}$
- Speedup: $S = T_{\text{FM}} / T_{\text{TSCP}}$

**Success Criteria:**
- $T_{\text{TSCP}} < 10$ seconds
- $S \geq 10^3$ (conservative estimate)

### 3.6 Evaluation Metrics

**Primary Metrics:**
1. **Classification Accuracy:** Proportion of correct tier predictions
2. **Macro F1-Score:** Harmonic mean of precision and recall, averaged across tiers
3. **Pearson Correlation:** Between predicted and actual performance gaps
4. **Computational Speedup:** Ratio of foundation model training time to TSCP time

**Secondary Metrics:**
1. **Per-Tier Precision/Recall:** Identify systematic biases
2. **Calibration Error:** Expected Calibration Error (ECE) for probability estimates
3. **Feature Importance Stability:** Consistency across cross-validation folds
4. **Cost-Benefit Analysis:** Break-even point (number of problems where setup cost amortizes)

**Statistical Validation:**
- Bootstrap confidence intervals (1000 iterations) for accuracy estimates
- Permutation tests for feature importance significance
- Cross-validation stability analysis (coefficient of variation <10%)

### 3.7 Implementation Details

**Software Stack:**
- Python 3.9+
- Core libraries: `xgboost`, `scikit-learn`, `pandas`, `numpy`
- Complexity metrics: `nolds`, `pyeeg`, `antropy`, `scipy`
- Foundation models: `transformers`, `pytorch`
- Visualization: `matplotlib`, `seaborn`, `shap`

**Reproducibility Measures:**
- Fixed random seeds (42) for all stochastic processes
- Docker container with pinned dependency versions
- Public GitHub repository with complete code and data
- Detailed experiment logs with hyperparameters and results
- Pre-computed complexity metrics for benchmark datasets

**Quality Assurance:**
- Unit tests for each complexity metric implementation
- Integration tests for end-to-end pipeline
- Validation against published metric values on standard datasets
- Code review and documentation standards

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes:**

1. **Validated TSCP Framework:** A production-ready triage system achieving ≥80% accuracy in predicting foundation model necessity, with <10 second inference time and <1 GPU-hour training cost.

2. **Empirical Complexity-Performance Mapping:** Quantified relationships between 6-8 information-theoretic metrics and foundation model performance gains across 60-80 benchmark datasets, with statistical significance testing and confidence intervals.

3. **Feature Importance Hierarchy:** Ranked list of complexity metrics by predictive power, with SHAP-based interpretability analysis revealing which data properties drive foundation model necessity.

4. **Generalization Validation:** Demonstrated out-of-domain performance (≥60% zero-shot, ≥75% with 20-shot adaptation), establishing TSCP's applicability beyond training domains.

5. **Computational Efficiency Proof:** Documented 10³-10⁵× speedup over training foundation models for every problem, with break-even analysis showing cost amortization after ~20 problems.

**Secondary Outcomes:**

6. **Open-Source Software Package:** Python package (`tscp`) with command-line interface, comprehensive documentation, and tutorial notebooks for practitioner adoption.

7. **Benchmark Dataset Repository:** Curated collection of 60-80 time series datasets with pre-computed complexity metrics, ground truth performance gaps, and standardized evaluation protocols.

8. **Methodological Guidelines:** Best practices for complexity metric extraction, preprocessing pipelines, and threshold adaptation for user-specific cost-benefit preferences.

9. **Failure Mode Analysis:** Systematic characterization of cases where TSCP predictions fail, identifying data properties requiring future research (e.g., regime-switching dynamics, extreme non-stationarity).

### 4.2 Scientific Impact

**Theoretical Advances:**

1. **Formalization of Model Selection Theory:** TSCP provides the first rigorous framework linking intrinsic data complexity to extrinsic model performance, bridging information theory and machine learning model selection.

2. **Predictability Bounds:** Establishes empirical relationships between Lyapunov exponents, Hurst exponents, and the performance ceiling of different model classes, contributing to understanding of fundamental limits in time series forecasting.

3. **Cross-Domain Methodology Transfer:** Demonstrates successful adaptation of medical triage protocols to machine learning, opening new research directions in decision-theoretic model selection.

**Methodological Contributions:**

1. **Paradigm Shift:** Transforms model selection from post-hoc comparative benchmarking to pre-training predictive characterization, reducing computational barriers to foundation model adoption.

2. **Interpretable Model Selection:** Unlike black-box AutoML systems, TSCP provides transparent, interpretable recommendations based on well-understood complexity metrics, enabling scientific understanding of model necessity.

3. **Adaptive Framework:** Learned tier boundaries accommodate user-specific cost-benefit preferences, making TSCP applicable across diverse resource constraints and deployment scenarios.

### 4.3 Practical Impact

**Resource Democratization:**

1. **Accessibility:** Enables practitioners with limited computational budgets (e.g., small research labs, developing countries, resource-constrained industries) to make informed decisions about foundation model necessity without expensive trial-and-error.

2. **Environmental Sustainability:** Reduces unnecessary GPU usage by preventing wasteful foundation model training when linear models suffice, contributing to green AI initiatives.

3. **Time-to-Deployment:** Accelerates model selection from days/weeks (training multiple models) to seconds (TSCP inference), enabling rapid prototyping and iteration.

**Industry Applications:**

1. **Cloud Service Optimization:** Cloud providers can use TSCP to recommend appropriate model tiers to customers, optimizing resource allocation and pricing.

2. **AutoML Enhancement:** Integration into AutoML platforms (e.g., AutoGluon, H2O) as a pre-processing step to prune search spaces and reduce computational costs.

3. **Edge Deployment:** Identifies cases where lightweight linear models suffice for edge devices, avoiding unnecessary model compression or distillation.

**Risk Mitigation:**

1. **Prevents Over-Engineering:** Alerts practitioners when foundation models are unlikely to provide meaningful improvements, avoiding wasted development effort.

2. **Identifies Under-Specification:** Flags cases where linear models are insufficient, preventing deployment of inadequate solutions in critical applications (e.g., healthcare, finance).

### 4.4 Workshop Contributions

This research directly addresses three key workshop themes:

**1. Critiques on Time Series Foundation Models:**
- Provides systematic empirical evidence of when foundation models fail to outperform simple baselines
- Identifies data properties (low Lyapunov exponent, high Hurst exponent) associated with foundation model underperformance
- Contributes to understanding limitations and failure modes through interpretable complexity analysis

**2. Analysis of Pretrained Time Series Models:**
- Characterizes foundation model behavior through the lens of information-theoretic complexity
- Reveals which data properties foundation models successfully exploit vs. struggle with
- Provides tools for analyzing pretrained models without expensive retraining

**3. Real-World Applications of Large Time Series Models:**
- Demonstrates practical deployment framework for resource-constrained scenarios
- Validates across five real-world domains (weather, traffic, energy, medical, finance)
- Provides actionable guidelines for practitioners in industry and applied research

### 4.5 Future Research Directions

**Immediate Extensions:**

1. **Multi-Horizon Analysis:** Investigate whether optimal model class depends on forecast horizon, potentially developing horizon-specific triage systems.

2. **Probabilistic Forecasting:** Extend TSCP to predict performance gaps in probabilistic metrics (CRPS, quantile loss) beyond point forecasting.

3. **Multimodal Integration:** Adapt framework for time series with exogenous information (text, images), predicting when multimodal foundation models are necessary.

**Long-Term Directions:**

1. **Online Adaptation:** Develop streaming TSCP variants that update predictions as new data arrives, handling concept drift and regime changes.

2. **Causal Complexity Metrics:** Incorporate causal discovery methods to identify when foundation models are needed to capture complex causal relationships.

3. **Foundation Model Design:** Use TSCP insights to guide architecture design—which components (attention, patching, normalization) are necessary for different complexity profiles?

4. **Theoretical Foundations:** Develop PAC-learning bounds relating sample complexity, data complexity, and model class performance gaps.

### 4.6 Dissemination Plan

**Academic Outputs:**
- Workshop paper submission (4-6 pages)
- Full conference paper at NeurIPS, ICML, or ICLR (9 pages)
- Journal article in JMLR or IEEE TPAMI (20-30 pages)

**Open-Source Release:**
- GitHub repository with MIT license
- PyPI package distribution
- Documentation website with tutorials
- Video demonstrations and walkthroughs

**Community Engagement:**
- Workshop presentation and poster
- Blog posts on Towards Data Science, Medium
- Twitter/X thread with key findings
- Kaggle notebook demonstrating usage

**Industry Outreach:**
- White paper for practitioners
- Webinar for industry data scientists
- Integration proposals to AutoML platforms
- Consultation with cloud service providers

### 4.7 Success Metrics

**Quantitative Indicators:**
- ≥80% classification accuracy (primary goal)
- ≥20 percentage point improvement over heuristics
- ≥100 GitHub stars within 6 months
- ≥50 citations within 2 years
- ≥1000 PyPI downloads within 1 year

**Qualitative Indicators:**
- Adoption by at least one major AutoML platform
- Positive feedback from workshop attendees
- Replication studies by independent researchers
- Integration into time series forecasting courses

**Impact Metrics:**
- Estimated GPU-hours saved by community (target: 10,000+ hours/year)
- Number of domains where TSCP enables new applications
- Diversity of user base (academia, industry, geography)

---

**Conclusion:**

TSCP represents a paradigm shift in time series model selection, transforming expensive post-hoc benchmarking into efficient pre-training prediction. By leveraging information-theoretic complexity metrics and supervised learning, we enable practitioners to make informed decisions about foundation model necessity in seconds rather than days, democratizing access to appropriate modeling choices and advancing our understanding of when and why foundation models are necessary for time series forecasting. This research addresses critical gaps in the time series foundation model literature while providing immediately actionable tools for real-world deployment.