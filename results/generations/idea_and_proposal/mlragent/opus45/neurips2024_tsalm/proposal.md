# Research Proposal

## Title
**Probing What Time Series Foundation Models Actually Learn: A Systematic Analysis Framework Through Synthetic Controlled Experiments**

---

## 1. Introduction

### Background

The emergence of foundation models has fundamentally transformed machine learning paradigms across multiple domains. In natural language processing and computer vision, large-scale pretrained models have demonstrated remarkable capabilities in zero-shot and few-shot transfer learning, enabling practitioners to leverage vast amounts of pretraining knowledge for diverse downstream tasks. Recently, this paradigm has begun to permeate the time series community, with several time series foundation models (TSFMs) being developed and open-sourced, including TimesFM, Chronos, Moirai, and Lag-Llama. These models have shown impressive empirical performance across various forecasting benchmarks, promising a new era of generalizable time series analysis.

However, despite their empirical success, TSFMs remain fundamentally opaque compared to classical statistical methods. Traditional approaches like ARIMA, exponential smoothing, and state-space models offer clear interpretability—practitioners can directly observe how trend, seasonality, and noise components are modeled and extrapolated. In contrast, TSFMs operate as black boxes, providing little insight into what temporal patterns they capture, whether they truly learn generalizable time series concepts, or if they merely memorize dataset-specific features.

Recent studies have begun to address this interpretability gap. Pandey et al. (2025) investigated the internal representations of TSFMs, revealing that early layers capture local patterns while deeper layers encode more abstract features. Santamaria-Valenzuela et al. (2025) evaluated the interpretability of latent spaces in TSFMs for visual analytics, noting that even fine-tuned models exhibit limited embedding interpretability. While these works provide valuable insights, a systematic framework for understanding *what* TSFMs learn through controlled experiments remains absent.

### Research Objectives

This research proposes to develop a comprehensive probing framework for systematically analyzing the capabilities and limitations of TSFMs using carefully designed synthetic time series with known, controllable properties. Our specific objectives are:

1. **Design controlled synthetic benchmarks** that isolate fundamental time series components (trend, seasonality, level shifts, noise distributions, long-range dependencies) and their systematic combinations.

2. **Develop diagnostic probing tasks** that test whether TSFMs can detect, extrapolate, and generalize across specific temporal patterns and their parameter variations.

3. **Conduct comparative analysis** benchmarking multiple state-of-the-art TSFMs against classical statistical methods to identify where foundation models excel versus fail.

4. **Create a taxonomy of TSFM capabilities** and provide actionable insights for model architecture improvements.

5. **Release an open-source diagnostic toolkit** enabling the research community to probe future TSFMs systematically.

### Significance

Understanding what TSFMs learn is crucial for multiple reasons. First, in high-stakes domains such as healthcare, finance, and energy, the opacity of these models hinders trust and adoption. Second, without mechanistic understanding, model improvement relies on trial-and-error rather than principled design. Third, identifying specific failure modes enables practitioners to make informed decisions about when to use TSFMs versus classical methods. This research bridges the gap between empirical success and mechanistic understanding, contributing foundational knowledge to the rapidly evolving field of time series foundation models.

---

## 2. Methodology

### 2.1 Controlled Synthetic Benchmark Design

We design a comprehensive suite of synthetic time series generators that produce data with precisely controlled properties. This approach allows us to isolate specific temporal phenomena and systematically test model understanding.

#### 2.1.1 Component-Level Generators

**Trend Components**: We generate various trend types including:
- Linear trends: $y_t^{trend} = \alpha + \beta t$
- Polynomial trends: $y_t^{trend} = \sum_{k=0}^{K} \alpha_k t^k$
- Exponential trends: $y_t^{trend} = \alpha e^{\beta t}$
- Piecewise linear trends with controllable breakpoints

**Seasonality Components**: We implement seasonal patterns with configurable parameters:
$$y_t^{season} = \sum_{j=1}^{J} A_j \sin\left(\frac{2\pi t}{P_j} + \phi_j\right)$$
where $A_j$ is amplitude, $P_j$ is period, and $\phi_j$ is phase shift. We systematically vary:
- Single seasonality with periods $P \in \{4, 7, 12, 24, 52, 365\}$
- Multiple overlapping seasonalities
- Non-integer and unusual periods to test generalization

**Level Shifts and Regime Changes**: We generate:
- Abrupt level shifts: $y_t^{shift} = \mu_0 \cdot \mathbb{1}_{t < \tau} + \mu_1 \cdot \mathbb{1}_{t \geq \tau}$
- Gradual regime transitions using sigmoid functions
- Multiple regime changes with varying frequencies

**Noise Distributions**: We implement diverse noise models:
- Gaussian: $\epsilon_t \sim \mathcal{N}(0, \sigma^2)$
- Heavy-tailed (Student-t): $\epsilon_t \sim t_\nu$
- Heteroscedastic: $\epsilon_t \sim \mathcal{N}(0, \sigma_t^2)$ with time-varying variance
- Autocorrelated noise: AR(p) processes

**Long-Range Dependencies**: We generate processes exhibiting:
- ARFIMA models with fractional integration parameter $d \in (0, 0.5)$
- Long-memory processes with Hurst exponent $H \in (0.5, 1)$

#### 2.1.2 Compositional Benchmark Suite

Beyond isolated components, we create systematic combinations:
$$y_t = y_t^{trend} + y_t^{season} + y_t^{shift} + \epsilon_t$$

We design a factorial experiment varying:
- Presence/absence of each component
- Parameter values within each component
- Signal-to-noise ratios
- Time series length (short: 50-100, medium: 200-500, long: 1000+)

### 2.2 Probing Task Design

We develop three categories of diagnostic tasks to comprehensively assess TSFM capabilities.

#### 2.2.1 Detection Tasks

These tasks test whether models can identify the presence of specific patterns:

**Pattern Classification Probes**: Given a time series, predict which components are present. We extract model embeddings and train lightweight classifiers:
$$P(\text{component } c \text{ present} | \mathbf{z}) = \sigma(\mathbf{w}_c^\top \mathbf{z} + b_c)$$
where $\mathbf{z}$ is the model's internal representation.

**Change Point Detection**: Test whether models can identify regime change locations by analyzing prediction uncertainty or representation shifts.

#### 2.2.2 Extrapolation Tasks

These tasks evaluate whether models correctly continue patterns:

**Trend Extrapolation**: Given history with trend, measure extrapolation accuracy:
$$\text{Trend Error} = \frac{1}{H}\sum_{h=1}^{H} |\hat{y}_{T+h}^{trend} - y_{T+h}^{trend}|$$

**Seasonal Continuation**: Assess phase and amplitude preservation:
$$\text{Phase Error} = |\hat{\phi} - \phi|, \quad \text{Amplitude Error} = |\hat{A} - A|$$

**Combined Pattern Forecasting**: Evaluate forecasts on composite series with ground-truth decomposition available.

#### 2.2.3 Generalization Tasks

These tasks assess transfer to unseen parameter ranges:

**Out-of-Distribution Seasonal Periods**: Train/evaluate split where test periods are outside training distribution (e.g., train on periods $\{7, 12, 24\}$, test on $\{5, 17, 30\}$).

**Amplitude and Trend Strength Generalization**: Test on parameter values not seen during pretraining.

**Length Generalization**: Evaluate on sequence lengths substantially different from pretraining.

### 2.3 Model Selection and Implementation

#### 2.3.1 Time Series Foundation Models

We benchmark the following TSFMs:
- **TimesFM** (Google): Decoder-only architecture with patched inputs
- **Chronos** (Amazon): T5-based model with tokenized time series
- **Moirai** (Salesforce): Universal forecasting model with mixture distributions
- **Lag-Llama** (ServiceNow): LLaMA-based autoregressive model

#### 2.3.2 Classical Baselines

We compare against interpretable statistical methods:
- **ARIMA/SARIMA**: For trend and seasonality modeling
- **ETS (Exponential Smoothing)**: State-space formulation with explicit components
- **Prophet**: Additive model with trend, seasonality, and holidays
- **Theta Method**: Simple but robust benchmark

#### 2.3.3 Implementation Details

For each TSFM, we:
1. Use official pretrained checkpoints without fine-tuning (zero-shot evaluation)
2. Extract intermediate representations from multiple layers
3. Evaluate both point forecasts and probabilistic predictions where applicable

### 2.4 Experimental Design

#### 2.4.1 Evaluation Protocol

**Forecasting Metrics**:
- Mean Absolute Error (MAE): $\frac{1}{H}\sum_{h=1}^{H}|y_{T+h} - \hat{y}_{T+h}|$
- Mean Absolute Scaled Error (MASE): Normalized by in-sample naive forecast error
- Continuous Ranked Probability Score (CRPS) for probabilistic forecasts:
$$\text{CRPS}(F, y) = \int_{-\infty}^{\infty} (F(z) - \mathbb{1}_{z \geq y})^2 dz$$

**Probing Metrics**:
- Detection accuracy, precision, recall, F1 for pattern classification
- Representation separability via silhouette scores
- Extrapolation error decomposed by component type

#### 2.4.2 Experimental Conditions

We design experiments to answer specific research questions:

**Experiment 1 - Component Detection**: 
- Generate 10,000 time series per component type
- Extract embeddings from each TSFM layer
- Train linear probes and measure classification accuracy

**Experiment 2 - Extrapolation Accuracy**:
- Generate 5,000 series per complexity level
- Evaluate forecasting across horizons $H \in \{1, 6, 12, 24, 48\}$
- Compare accuracy on series with/without specific components

**Experiment 3 - Generalization Boundaries**:
- Create train/test splits with controlled distribution shifts
- Measure performance degradation as function of distribution distance

**Experiment 4 - Failure Mode Identification**:
- Systematic grid search over parameter combinations
- Identify regions of parameter space with poor performance
- Analyze common characteristics of failure cases

### 2.5 Analysis Framework

#### 2.5.1 Representation Analysis

We analyze internal representations using:
- **Centered Kernel Alignment (CKA)**: Compare layer representations across models
- **Singular Value Decomposition**: Examine representation dimensionality
- **Probing Classifiers**: Linear and nonlinear probes for component detection

#### 2.5.2 Attribution Analysis

For understanding which input features drive predictions:
- Attention pattern analysis for transformer-based models
- Gradient-based saliency: $\frac{\partial \hat{y}_{T+h}}{\partial y_t}$ for each input timestep
- Ablation studies removing specific temporal segments

#### 2.5.3 Statistical Testing

We employ rigorous statistical methodology:
- Paired t-tests with Bonferroni correction for multiple comparisons
- Effect size reporting (Cohen's d)
- Confidence intervals via bootstrap resampling

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Taxonomy of TSFM Capabilities**: We expect to produce a comprehensive categorization of what current TSFMs can and cannot learn, organized by:
- Temporal pattern type (trend, seasonality, level shifts, etc.)
- Pattern complexity (simple vs. composite)
- Generalization requirements (interpolation vs. extrapolation)

**Quantitative Capability Profiles**: For each TSFM, we will provide detailed profiles showing:
- Detection accuracy for each component type across layers
- Extrapolation accuracy as function of forecast horizon and pattern type
- Generalization boundaries in parameter space

**Identified Failure Modes**: We anticipate discovering specific failure modes such as:
- Inability to extrapolate certain trend types beyond training distribution
- Phase drift in long-horizon seasonal forecasting
- Sensitivity to unusual seasonal periods
- Degradation with heavy-tailed noise

**Actionable Insights for Model Improvement**: Based on our analysis, we will provide recommendations for:
- Architecture modifications addressing identified weaknesses
- Training data composition to improve specific capabilities
- Ensemble strategies combining TSFMs with classical methods

**Open-Source Diagnostic Toolkit**: We will release:
- Synthetic data generators with full parameterization
- Probing task implementations
- Evaluation pipelines compatible with major TSFMs
- Visualization tools for capability analysis

### 3.2 Scientific Impact

This research contributes to the fundamental understanding of deep learning for time series:
- **Bridging Theory and Practice**: Moving beyond benchmark leaderboards to mechanistic understanding
- **Informing Architecture Design**: Providing evidence-based guidance for future TSFM development
- **Establishing Evaluation Standards**: Creating rigorous protocols for TSFM assessment

### 3.3 Practical Impact

For practitioners deploying TSFMs:
- **Informed Model Selection**: Understanding which model to use for specific pattern types
- **Trust Calibration**: Knowing when to trust TSFM predictions versus classical methods
- **Hybrid System Design**: Guidance on combining TSFMs with interpretable models

### 3.4 Community Impact

The open-source toolkit will:
- Enable reproducible research on TSFM interpretability
- Provide standardized benchmarks for future model comparison
- Lower barriers to rigorous TSFM evaluation

---

## 4. Conclusion

This research proposal presents a systematic framework for understanding what time series foundation models actually learn through controlled synthetic experiments. By designing benchmarks with known ground truth, developing comprehensive probing tasks, and conducting rigorous comparative analysis, we aim to illuminate the black box of TSFMs. The expected outcomes—a capability taxonomy, identified failure modes, and an open-source diagnostic toolkit—will advance both scientific understanding and practical deployment of these powerful models. As TSFMs continue to evolve and gain adoption, this foundational understanding becomes increasingly critical for responsible and effective use in real-world applications.