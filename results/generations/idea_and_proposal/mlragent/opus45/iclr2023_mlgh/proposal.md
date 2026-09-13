# Research Proposal: Adaptive Federated Learning for Privacy-Preserving Disease Surveillance in Low-Resource Settings

## 1. Introduction

### Background

The COVID-19 pandemic exposed critical vulnerabilities in global health surveillance infrastructure, particularly the inability to rapidly share epidemiological insights across borders while respecting data sovereignty and privacy constraints. Despite remarkable advances in machine learning over the past decade, the field's contributions to pandemic response were modest, largely due to fragmented data ecosystems, centralization requirements, and the disconnect between sophisticated methodologies and practical deployment constraints. Low- and middle-income countries (LMICs), which often possess valuable frontline health data, were systematically excluded from data-driven global health intelligence due to infrastructure limitations, regulatory barriers, and privacy concerns associated with data centralization.

Traditional machine learning approaches for disease surveillance require aggregating sensitive health data in centralized repositories, creating significant barriers to international collaboration. This centralization paradigm conflicts with data protection regulations, national sovereignty concerns, and the practical reality that many regions lack the bandwidth and infrastructure for continuous data transmission. The result is a fragmented global health landscape where critical epidemiological signals remain siloed within national or institutional boundaries, delaying outbreak detection and hampering coordinated response efforts.

Federated learning (FL) offers a promising paradigm shift by enabling collaborative model training without raw data sharing. However, existing FL frameworks are predominantly designed for well-resourced settings with reliable connectivity, homogeneous data distributions, and sufficient local computational capacity. Recent studies have highlighted significant challenges when deploying federated learning in resource-constrained healthcare settings, including infrastructure limitations, data heterogeneity across diverse populations, and the need for model interpretability to inform policy decisions.

### Research Objectives

This research proposes to develop **FedSurv**, an adaptive federated learning framework specifically designed for heterogeneous global health data in resource-constrained environments. Our objectives are:

1. To design communication-efficient federated algorithms that maintain functionality under intermittent connectivity and severe bandwidth constraints typical of LMICs.

2. To incorporate semi-mechanistic disease transmission priors into the federated learning objective, enhancing model interpretability for epidemiologists and policymakers.

3. To develop robust domain adaptation techniques that handle distribution shifts across regions with varying demographics, healthcare systems, and disease reporting practices.

4. To validate the framework on retrospective multi-country infectious disease data, demonstrating both predictive accuracy and practical deployability.

### Significance

This research addresses fundamental gaps at the intersection of machine learning and global health. By enabling privacy-preserving collaboration across heterogeneous health systems, FedSurv could democratize participation in global health intelligence networks, allowing resource-limited regions to contribute to and benefit from collective epidemiological insights. The incorporation of mechanistic priors ensures that model outputs remain interpretable and actionable for public health decision-makers, bridging the gap between sophisticated machine learning methods and policy-relevant applications. Ultimately, this work contributes to proactive pandemic preparedness while addressing structural inequalities in global health surveillance.

## 2. Methodology

### 2.1 System Architecture and Problem Formulation

We consider a federated network of $K$ participating nodes (countries, regions, or health facilities), where each node $k$ possesses local disease surveillance data $\mathcal{D}_k = \{(\mathbf{x}_i^k, y_i^k)\}_{i=1}^{n_k}$. The data includes epidemiological features $\mathbf{x}$ (case counts, demographic indicators, mobility patterns, healthcare capacity metrics) and outcomes $y$ (disease incidence, outbreak indicators, or transmission rates).

The global objective is to learn a predictive model $f_\theta$ parameterized by $\theta$ that minimizes the empirical risk across all nodes while incorporating epidemiological knowledge:

$$\min_\theta \sum_{k=1}^{K} \frac{n_k}{N} \mathcal{L}_k(\theta) + \lambda \mathcal{R}_{\text{epi}}(\theta)$$

where $N = \sum_{k=1}^{K} n_k$, $\mathcal{L}_k(\theta)$ is the local loss at node $k$, and $\mathcal{R}_{\text{epi}}(\theta)$ is a regularization term encoding semi-mechanistic epidemiological constraints.

### 2.2 Communication-Efficient Federated Algorithm

To address bandwidth and connectivity constraints, we propose an adaptive communication protocol with three key components:

**Gradient Compression with Adaptive Sparsification**: Rather than transmitting full model updates, each node computes and transmits only the most significant gradient components. Let $\mathbf{g}_k^t$ denote the local gradient at node $k$ during round $t$. We apply top-$s$ sparsification:

$$\tilde{\mathbf{g}}_k^t = \text{TopS}(\mathbf{g}_k^t + \mathbf{e}_k^{t-1}, s_k^t)$$

where $\mathbf{e}_k^{t-1}$ is the accumulated error from previous rounds (error feedback), and $s_k^t$ is an adaptive sparsity level determined by local bandwidth availability:

$$s_k^t = \min\left(s_{\max}, \frac{B_k^t}{\text{sizeof}(\theta)} \cdot d\right)$$

where $B_k^t$ is the available bandwidth, $d$ is the model dimension, and $s_{\max}$ is the maximum sparsity threshold.

**Asynchronous Aggregation with Staleness Weighting**: To accommodate intermittent connectivity, we employ asynchronous federated averaging with staleness-aware weighting. When the central server receives an update from node $k$ with staleness $\tau_k$ (rounds since the local model was synchronized), the global model is updated as:

$$\theta^{t+1} = \theta^t + \eta \cdot w_k(\tau_k) \cdot (\tilde{\theta}_k - \theta^{t-\tau_k})$$

where $w_k(\tau_k) = \frac{n_k}{N} \cdot \alpha^{\tau_k}$ with decay factor $\alpha \in (0, 1)$ penalizing stale updates.

**Local Computation Adaptation**: Nodes with limited computational resources perform fewer local epochs before synchronization. We dynamically adjust local epochs $E_k$ based on device capacity:

$$E_k = \max\left(1, \left\lfloor E_{\text{base}} \cdot \frac{C_k}{C_{\text{ref}}} \right\rfloor\right)$$

where $C_k$ is the local computational capacity and $C_{\text{ref}}$ is a reference capacity level.

### 2.3 Semi-Mechanistic Epidemiological Priors

To enhance interpretability, we incorporate disease transmission dynamics into the learning objective through physics-informed regularization. We adopt a generalized SEIR (Susceptible-Exposed-Infectious-Recovered) framework where the neural network outputs are constrained to respect epidemiological principles.

Let $\hat{\mathbf{y}}_t = f_\theta(\mathbf{x}_t)$ predict the state vector (incidence, prevalence) at time $t$. The mechanistic regularizer enforces consistency with discrete-time transmission dynamics:

$$\mathcal{R}_{\text{epi}}(\theta) = \sum_{t=1}^{T-1} \left\| \hat{I}_{t+1} - \hat{I}_t - \beta_\theta \frac{\hat{S}_t \hat{I}_t}{N_{\text{pop}}} + \gamma \hat{I}_t \right\|^2$$

where $\hat{S}_t, \hat{I}_t$ are predicted susceptible and infectious populations, $\beta_\theta$ is a learnable transmission rate (output by an auxiliary network head), and $\gamma$ is the recovery rate. This formulation allows the model to learn data-driven corrections to mechanistic dynamics while maintaining epidemiological plausibility.

Additionally, we enforce positivity and conservation constraints through projected gradient descent:

$$\theta \leftarrow \text{Proj}_\Theta\left(\theta - \eta \nabla_\theta \mathcal{L}\right)$$

where $\Theta$ ensures that predicted quantities remain non-negative and population-consistent.

### 2.4 Domain Adaptation for Heterogeneous Distributions

To address distribution shifts across regions, we propose a hierarchical personalization approach combining global knowledge sharing with local adaptation.

**Feature Alignment Layer**: We introduce domain-invariant feature representations through adversarial training. A domain discriminator $D_\phi$ attempts to identify the source node from feature representations $\mathbf{h} = g_\theta(\mathbf{x})$:

$$\mathcal{L}_{\text{domain}} = -\sum_{k=1}^{K} \mathbb{E}_{\mathbf{x} \sim \mathcal{D}_k}\left[\log D_\phi(g_\theta(\mathbf{x}))_k\right]$$

The feature extractor is trained to maximize domain confusion while minimizing prediction loss, promoting transferable representations.

**Adaptive Personalization Layers**: Following hierarchical clustering principles, we partition the model into shared layers $\theta_{\text{shared}}$ (updated globally) and personalized layers $\theta_k^{\text{local}}$ (maintained locally):

$$f_{\theta_k}(\mathbf{x}) = h_{\theta_k^{\text{local}}}(g_{\theta_{\text{shared}}}(\mathbf{x}))$$

Nodes with similar data distributions (determined by gradient similarity clustering) share intermediate semi-global models, enabling knowledge transfer among related populations while preserving local specificity.

### 2.5 Experimental Design and Validation

**Datasets**: We will validate FedSurv using:
1. **Retrospective COVID-19 data**: Multi-country case counts, hospitalization rates, and mobility data from the Johns Hopkins CSSE repository and Google COVID-19 Open Data, spanning 50+ countries with varying data quality and reporting practices.
2. **Dengue surveillance data**: Weekly incidence data from Southeast Asian and Latin American countries (via Project Tycho and WHO databases), exhibiting strong seasonality and regional heterogeneity.
3. **Synthetic benchmark**: A simulation environment based on stochastic SEIR dynamics with controlled distribution shifts and data quality degradation.

**Baselines**: We compare against:
- Centralized training (upper bound, assuming full data access)
- Standard FedAvg with uniform aggregation
- FedProx for heterogeneous settings
- Local-only training (no collaboration)
- SCAFFOLD for variance reduction

**Evaluation Metrics**:
1. **Predictive Performance**: Mean Absolute Error (MAE) and Continuous Ranked Probability Score (CRPS) for incidence forecasting; Area Under ROC Curve (AUC) for outbreak detection.
2. **Communication Efficiency**: Total bytes transmitted per round; convergence rate (rounds to target accuracy).
3. **Robustness**: Performance under simulated connectivity disruptions (random node dropout, delayed synchronization).
4. **Interpretability**: Alignment of learned transmission parameters ($\beta_\theta$) with epidemiologically estimated reproduction numbers; expert evaluation of mechanistic consistency.

**Ablation Studies**: We systematically evaluate the contribution of each component (gradient compression, asynchronous aggregation, mechanistic regularization, domain adaptation) through controlled ablations.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Deployable Framework**: A fully implemented, open-source federated learning system optimized for disease surveillance in resource-constrained settings, with demonstrated functionality under realistic connectivity and computational constraints.

2. **Validated Methodology**: Comprehensive empirical evidence demonstrating that FedSurv achieves predictive performance within 5-10% of centralized training while reducing communication costs by 80%+ compared to standard federated approaches.

3. **Interpretable Predictions**: Models that output not only forecasts but also epidemiologically meaningful parameters (effective reproduction numbers, transmission rates) validated against established epidemiological estimates.

4. **Practical Guidelines**: Documentation of best practices for deploying federated learning in global health contexts, including recommendations for data harmonization, privacy configurations, and stakeholder engagement.

### Broader Impact

This research directly addresses the workshop's central themes by demonstrating how machine learning can be leveraged to promote public health worldwide while respecting the realities of diverse healthcare infrastructures. By enabling equitable participation of LMICs in global health intelligence networks, FedSurv contributes to addressing structural inequalities that were starkly exposed during COVID-19.

The framework supports proactive pandemic preparedness by facilitating continuous, privacy-preserving surveillance that can detect emerging outbreaks before they reach pandemic scale. The incorporation of mechanistic priors ensures that outputs remain actionable for policymakers, bridging the gap between sophisticated machine learning methods and practical public health decision-making.

Ultimately, this work exemplifies the type of collaboration between machine learning researchers and global health practitioners that the workshop seeks to foster—developing methods that are not only technically sophisticated but also practically deployable in the settings where they are most needed.