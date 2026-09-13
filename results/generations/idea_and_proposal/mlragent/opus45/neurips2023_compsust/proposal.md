# Research Proposal: Adaptive Domain Shift Detection for Sustainable Deployment of ML Models in Environmental Monitoring

## 1. Introduction

### Background

Computational sustainability leverages machine learning (ML) and artificial intelligence to address pressing global challenges outlined in the United Nations Sustainable Development Goals (UN SDGs), including climate action, life on land, and sustainable agriculture. While significant advances have been made in developing sophisticated ML models for environmental monitoring applications—ranging from biodiversity tracking to renewable energy forecasting—a critical gap exists between theoretical performance and real-world deployment reliability.

One of the most insidious challenges facing deployed sustainability models is **distribution shift**: the gradual or sudden divergence between training data distributions and real-world operational conditions. Environmental systems are inherently non-stationary. Climate change alters species migration patterns and habitat characteristics, urban development transforms air quality dynamics, agricultural practices evolve in response to market conditions, and sensors degrade over time. These factors cause ML models to fail silently—continuing to produce predictions without signaling their diminished reliability. Unlike controlled laboratory settings where models are evaluated on held-out test sets from the same distribution, deployed models face ever-changing conditions that systematically violate the independent and identically distributed (i.i.d.) assumption fundamental to most ML training paradigms.

The consequences of undetected model degradation in sustainability applications are severe. Flawed biodiversity assessments may lead to misguided conservation policies. Unreliable renewable energy forecasts can destabilize grid operations and undermine the economic viability of clean energy transitions. Inaccurate agricultural yield predictions may result in food security vulnerabilities. Perhaps most critically, silent model failures erode stakeholder trust—a precious commodity that, once lost, is difficult to rebuild and essential for the broader adoption of computational sustainability solutions.

### Research Objectives

This research proposes the development of **ADAPT-Sus** (Adaptive Domain shift detection And Performance Tracking for Sustainability), a lightweight, uncertainty-aware monitoring framework designed to continuously evaluate deployed sustainability models for domain shift and performance degradation. The specific objectives are:

1. **Develop a unified theoretical framework** combining conformal prediction, streaming drift detection, and performance proxy metrics to provide calibrated, real-time assessments of model reliability.

2. **Create efficient algorithms** suitable for deployment in resource-constrained environments typical of environmental monitoring stations.

3. **Validate the framework** across three representative sustainability domains: biodiversity monitoring, renewable energy forecasting, and agricultural yield prediction.

4. **Produce deployable artifacts** including an open-source toolkit, benchmark datasets with documented distribution shifts, and practical guidelines for implementing "graceful degradation" strategies.

### Significance

This research directly addresses the NeurIPS 2023 Computational Sustainability Workshop's theme of "Promises and Pitfalls from Theory to Deployment." By ensuring that models fail safely and transparently rather than silently, ADAPT-Sus will:

- Bridge the theory-to-deployment gap by providing practitioners with actionable tools for monitoring deployed models
- Build the stakeholder trust necessary for real-world adoption of computational sustainability solutions
- Prevent duplicated effort by establishing common failure detection methodologies
- Enable adaptive maintenance strategies that extend model useful lifetimes

## 2. Methodology

### 2.1 Framework Overview

ADAPT-Sus integrates three complementary components operating in concert:

1. **Conformal Prediction Module (CPM)**: Provides distribution-free uncertainty quantification with coverage guarantees
2. **Streaming Drift Detection Module (SDDM)**: Identifies shifts in input feature distributions using memory-efficient algorithms
3. **Performance Proxy Module (PPM)**: Estimates model degradation when ground truth labels are unavailable

### 2.2 Conformal Prediction Module

We employ adaptive conformal prediction to construct prediction sets with guaranteed coverage rates that remain valid under distribution shift. For a deployed model $f$ producing predictions $\hat{y}$ and a user-specified coverage level $1-\alpha$, we construct prediction sets $C(x)$ such that:

$$P(y \in C(x)) \geq 1 - \alpha$$

**Algorithm 1: Adaptive Conformal Prediction**

1. Maintain a sliding window of recent calibration examples $\{(x_i, y_i)\}_{i=t-w}^{t-1}$ where labels are available
2. Compute nonconformity scores: $s_i = |y_i - f(x_i)|$ for regression or $s_i = 1 - f(x_i)_{y_i}$ for classification
3. Determine the adaptive threshold: $\hat{q}_t = \text{Quantile}_{1-\alpha}\left(\{s_i\}_{i=t-w}^{t-1}\right)$
4. For new input $x_t$, construct prediction set: $C(x_t) = \{y : s(x_t, y) \leq \hat{q}_t\}$

To detect when the model becomes unreliable, we monitor the **prediction set size** and **empirical coverage rate**. Define the alert metric:

$$A_t = \frac{|C(x_t)|}{|C|_{\text{baseline}}} + \lambda \cdot \left| \frac{1}{w}\sum_{i=t-w}^{t-1} \mathbb{1}[y_i \in C(x_i)] - (1-\alpha) \right|$$

where $|C|_{\text{baseline}}$ is the average prediction set size during a stable reference period, and $\lambda$ balances the two terms. An alert is triggered when $A_t$ exceeds a calibrated threshold $\tau_A$.

### 2.3 Streaming Drift Detection Module

For efficient feature drift detection in streaming settings, we employ a combination of univariate and multivariate methods:

**Univariate Drift Detection**: For each feature $j$, we maintain an online estimate of the reference distribution using the Count-Min Sketch data structure. We compute the Kolmogorov-Smirnov statistic between the reference distribution $P_{\text{ref}}^{(j)}$ and the recent window distribution $P_{\text{recent}}^{(j)}$:

$$D_{KS}^{(j)} = \sup_x |F_{\text{ref}}^{(j)}(x) - F_{\text{recent}}^{(j)}(x)|$$

**Multivariate Drift Detection**: We employ Maximum Mean Discrepancy (MMD) with random Fourier features for computational efficiency:

$$\widehat{\text{MMD}}^2 = \frac{1}{m^2}\sum_{i,j} k(x_i, x_j) + \frac{1}{n^2}\sum_{i,j} k(x'_i, x'_j) - \frac{2}{mn}\sum_{i,j} k(x_i, x'_j)$$

where $k$ is approximated using $D$ random Fourier features: $k(x, x') \approx \phi(x)^T\phi(x')$ with $\phi(x) = \sqrt{\frac{2}{D}}[\cos(\omega_1^T x + b_1), ..., \cos(\omega_D^T x + b_D)]$.

**Algorithm 2: Streaming Drift Detection**

1. Initialize reference sketches from deployment baseline period
2. For each incoming batch of data:
   - Update recent window statistics using exponential moving average
   - Compute $D_{KS}^{(j)}$ for each feature and $\widehat{\text{MMD}}^2$ for multivariate shift
   - Aggregate: $D_{\text{drift}} = \max_j D_{KS}^{(j)} + \beta \cdot \widehat{\text{MMD}}^2$
3. Trigger drift alert if $D_{\text{drift}} > \tau_D$ (calibrated during validation)

### 2.4 Performance Proxy Module

When ground truth labels are unavailable (common in real-time deployment), we estimate performance degradation using proxy metrics correlated with actual accuracy:

1. **Prediction Confidence Distribution Shift**: Track changes in the distribution of model confidence scores:
$$\Delta_{\text{conf}} = \text{JS}(P_{\text{conf}}^{\text{ref}} || P_{\text{conf}}^{\text{recent}})$$
where JS denotes Jensen-Shannon divergence.

2. **Disagreement Rate with Ensemble**: For critical applications, maintain a lightweight ensemble and monitor disagreement:
$$R_{\text{disagree}} = \frac{1}{|B|}\sum_{x \in B} \mathbb{1}[f_1(x) \neq f_2(x)]$$

3. **Temporal Consistency**: For time-series applications, measure prediction volatility:
$$V_t = \text{Var}(\{\hat{y}_{t-k}, ..., \hat{y}_t\})$$

The combined performance proxy score is:
$$P_{\text{proxy}} = w_1 \cdot \Delta_{\text{conf}} + w_2 \cdot R_{\text{disagree}} + w_3 \cdot V_t$$

Weights $w_1, w_2, w_3$ are learned during a validation phase where ground truth is available.

### 2.5 Experimental Design

**Datasets and Domains**:

1. **Biodiversity Monitoring**: iNaturalist species classification with temporal splits simulating climate-induced distribution shifts; camera trap images from the Snapshot Serengeti dataset with seasonal and sensor degradation variations.

2. **Renewable Energy Forecasting**: NREL Solar Radiation Database with synthetic and natural drift scenarios including seasonal changes and grid topology modifications.

3. **Agricultural Yield Prediction**: USDA crop yield data combined with satellite imagery (Sentinel-2), with drought years serving as natural distribution shift events.

**Synthetic Shift Injection**: To systematically evaluate detection capabilities, we inject controlled shifts:
- Covariate shift: $x' = x + \epsilon$, $\epsilon \sim \mathcal{N}(0, \sigma^2 I)$
- Label shift: Modifying class priors $P(y)$
- Concept drift: Gradual rotation of decision boundaries

**Evaluation Metrics**:

1. **Detection Performance**: Area under ROC curve (AUC) for shift detection; time-to-detection (TTD) measuring latency from shift onset to alert.

2. **Calibration Quality**: Expected Calibration Error (ECE) for conformal prediction sets:
$$\text{ECE} = \sum_{b=1}^{B} \frac{n_b}{N}|\text{acc}(b) - \text{conf}(b)|$$

3. **Operational Metrics**: Computational overhead (latency, memory); false positive rate at fixed detection thresholds.

4. **End-to-End Impact**: Reduction in undetected performance degradation episodes compared to baseline (no monitoring) and existing methods.

**Baselines**: We compare against:
- Static threshold monitoring on prediction confidence
- ADWIN (Adaptive Windowing) for drift detection
- Deep Ensemble uncertainty quantification
- Recent methods from the literature including Byzantine-robust federated conformal prediction

## 3. Expected Outcomes & Impact

### Deliverables

1. **ADAPT-Sus Toolkit**: An open-source Python library implementing all framework components, designed for easy integration with common ML deployment pipelines (MLflow, Kubeflow, custom APIs). The toolkit will include:
   - Plug-and-play modules for different model types
   - Configurable alerting thresholds with automatic calibration
   - Dashboard for real-time monitoring visualization

2. **Benchmark Datasets**: Curated datasets across three sustainability domains with documented distribution shifts, including metadata describing shift types, magnitudes, and temporal characteristics. These will serve as standardized evaluation resources for the community.

3. **Deployment Guidelines**: A practitioner-oriented document detailing:
   - Best practices for implementing graceful degradation strategies
   - Decision frameworks for when to retrain, fine-tune, or decommission models
   - Case studies from experimental deployments

### Expected Results

We anticipate that ADAPT-Sus will:
- Detect distribution shifts 40-60% faster than existing methods while maintaining false positive rates below 5%
- Reduce undetected model degradation episodes by over 70% compared to no-monitoring baselines
- Demonstrate computational efficiency suitable for edge deployment (sub-second inference overhead, <100MB memory footprint)

### Broader Impact

This research will advance the computational sustainability agenda by:

1. **Enabling Trustworthy Deployment**: By providing transparent model reliability assessments, ADAPT-Sus will help build the stakeholder confidence essential for real-world adoption of ML-driven sustainability solutions.

2. **Reducing Resource Waste**: Early detection of model degradation prevents continued operation of unreliable systems, avoiding flawed decisions and wasted computational resources on retraining at inappropriate times.

3. **Establishing Community Standards**: The benchmark datasets and evaluation protocols will provide common ground for comparing future advances in deployment monitoring.

4. **Bridging Research and Practice**: By engaging with non-profit partners in sustainability domains, this research will ensure that theoretical advances translate into practical tools that serve real conservation, energy, and agricultural needs.

The framework's emphasis on lightweight, efficient algorithms addresses the resource constraints faced by many environmental monitoring deployments, particularly in remote or developing regions where computational infrastructure may be limited. By enabling models to fail gracefully rather than silently, ADAPT-Sus will help ensure that the promises of computational sustainability are realized in practice, while honestly acknowledging and mitigating the pitfalls inherent in deploying ML systems in dynamic, real-world environments.