# Research Proposal: Adaptive Privacy Budget Allocation for Continual Federated Learning with Distribution Shifts

## 1. Introduction

### Background

Federated learning (FL) has emerged as a transformative paradigm for training machine learning models across distributed devices while keeping data localized, offering inherent privacy benefits by design. Since its introduction in 2016, FL has seen widespread adoption in practical applications ranging from mobile keyboard prediction to healthcare analytics. However, real-world deployments face a critical challenge: data distributions are not static but evolve continuously as user behaviors, preferences, and contexts change over time. This phenomenon, known as distribution shift or concept drift, necessitates continual model adaptation to maintain performance.

Simultaneously, differential privacy (DP) has become the gold standard for providing formal privacy guarantees in federated settings. DP mechanisms inject calibrated noise into the learning process, ensuring that individual contributions cannot be reverse-engineered from model updates. However, a fundamental tension exists between continual learning and differential privacy: privacy budgets accumulate over time due to the composition theorem of DP, meaning that continuous adaptation eventually exhausts the total privacy budget, rendering further learning impossible while maintaining privacy guarantees.

Current approaches to differentially private federated learning predominantly employ fixed, uniform privacy budget allocation strategies—spending the same amount of privacy budget ε in each training round regardless of the underlying data dynamics. This one-size-fits-all approach is suboptimal because: (1) during stable periods with minimal distribution shift, aggressive learning wastes privacy budget on marginal improvements; (2) during significant shifts requiring substantial model updates, insufficient privacy budget may be allocated, resulting in poor adaptation. Recent work by Kiani et al. (2025) demonstrated that time-adaptive privacy spending can improve utility, while Bhope et al. (2025) showed that mixture-of-experts approaches can address distribution shifts effectively. However, no existing work combines shift-aware detection with adaptive privacy allocation in a unified framework.

### Research Objectives

This research proposes an **Adaptive Privacy Budget Allocation (APBA)** framework for continual federated learning that dynamically distributes privacy budgets based on detected distribution shifts. Our specific objectives are:

1. **Develop a privacy-preserving shift detection mechanism** using federated analytics to estimate distribution divergence across training rounds without exposing raw client data.

2. **Design an adaptive budget scheduler** that intelligently allocates more privacy budget during periods of significant distribution shifts while conserving budget during stable periods.

3. **Provide rigorous theoretical guarantees** ensuring that the adaptive scheme satisfies end-to-end differential privacy under the composition framework.

4. **Validate the framework empirically** on realistic benchmarks with temporal distribution shifts, demonstrating practical improvements in the privacy-utility trade-off.

### Significance

This research addresses a critical gap between theoretical differential privacy guarantees and practical continual federated learning requirements. By enabling sustainable long-term privacy-preserving federated deployments, our work has significant implications for:

- **Industry practitioners** deploying FL systems that must adapt to evolving user behaviors while maintaining privacy compliance (e.g., GDPR, CCPA).
- **Academic researchers** seeking realistic assumptions for theoretical studies in federated settings.
- **Society at large** by enabling privacy-preserving AI systems that remain effective over extended operational lifetimes.

## 2. Methodology

### 2.1 System Overview

Our APBA framework operates in a cross-device federated learning setting with a central server coordinating $N$ clients over $T$ total training rounds. The framework consists of three integrated components: (1) Federated Shift Detection Module, (2) Adaptive Budget Scheduler, and (3) Privacy-Preserving Training Protocol.

### 2.2 Federated Shift Detection Module

We propose a lightweight, privacy-preserving mechanism to detect distribution shifts using federated analytics on gradient statistics rather than raw data.

**Step 1: Local Gradient Feature Extraction**

At each round $t$, participating clients compute local gradient updates $g_i^{(t)} = \nabla_\theta \mathcal{L}_i(\theta^{(t-1)})$ on their local data. Instead of sharing raw gradients, each client computes a compressed representation:

$$h_i^{(t)} = \text{TopK}\left(\text{sign}(g_i^{(t)}) \odot |g_i^{(t)}|^{1/2}\right)$$

where TopK selects the $k$ largest magnitude components, and the sign-magnitude decomposition reduces communication while preserving directional information.

**Step 2: Privacy-Preserving Aggregation**

The server aggregates these representations using secure aggregation:

$$\bar{h}^{(t)} = \frac{1}{|S_t|} \sum_{i \in S_t} h_i^{(t)} + \mathcal{N}(0, \sigma_{\text{detect}}^2 I)$$

where $S_t$ is the set of participating clients and Gaussian noise is added for local differential privacy with parameter $\sigma_{\text{detect}}$.

**Step 3: Shift Magnitude Estimation**

We estimate distribution shift by computing the cosine dissimilarity between aggregated gradient features across a sliding window:

$$\Delta^{(t)} = 1 - \frac{\bar{h}^{(t)} \cdot \bar{h}^{(t-w:t-1)}}{||\bar{h}^{(t)}|| \cdot ||\bar{h}^{(t-w:t-1)}||}$$

where $\bar{h}^{(t-w:t-1)}$ is the exponential moving average over the previous $w$ rounds. High $\Delta^{(t)}$ indicates significant distribution shift.

### 2.3 Adaptive Budget Scheduler

Given a total privacy budget $\varepsilon_{\text{total}}$ for the entire training horizon $T$, we dynamically allocate per-round budgets based on detected shifts.

**Budget Allocation Function**

We define the per-round privacy budget as:

$$\varepsilon^{(t)} = \varepsilon_{\text{base}} + \varepsilon_{\text{adaptive}} \cdot \phi(\Delta^{(t)})$$

where $\varepsilon_{\text{base}}$ is a minimum baseline allocation, $\varepsilon_{\text{adaptive}}$ is the adaptive component, and $\phi(\cdot)$ is a monotonically increasing activation function:

$$\phi(\Delta) = \frac{\exp(\beta \cdot (\Delta - \tau)) - 1}{\exp(\beta \cdot (1 - \tau)) - 1} \cdot \mathbf{1}[\Delta > \tau]$$

Here, $\tau$ is a threshold below which minimal adaptation occurs, and $\beta$ controls the sensitivity to shifts.

**Budget Reservoir Management**

To ensure the total budget constraint is satisfied, we maintain a privacy reservoir $R^{(t)}$:

$$R^{(t)} = \varepsilon_{\text{total}} - \sum_{s=1}^{t-1} \varepsilon^{(s)}$$

The adaptive component is scaled by the remaining horizon:

$$\varepsilon_{\text{adaptive}}^{(t)} = \min\left(\varepsilon_{\text{max}}, \frac{R^{(t)} - (T-t) \cdot \varepsilon_{\text{base}}}{1 + \gamma(T-t)}\right)$$

where $\gamma > 0$ ensures budget remains available for future rounds.

### 2.4 Privacy-Preserving Training Protocol

**Local Training with Clipping**

Each client performs local SGD with gradient clipping:

$$\tilde{g}_i^{(t)} = g_i^{(t)} \cdot \min\left(1, \frac{C}{||g_i^{(t)}||_2}\right)$$

where $C$ is the clipping bound ensuring bounded sensitivity.

**Noise Calibration**

The noise multiplier for round $t$ is calibrated based on the allocated budget:

$$\sigma^{(t)} = \frac{C \cdot \sqrt{2 \ln(1.25/\delta)}}{|S_t| \cdot \varepsilon^{(t)}}$$

**Aggregation**

The global model update is:

$$\theta^{(t)} = \theta^{(t-1)} + \eta \left(\frac{1}{|S_t|}\sum_{i \in S_t} \tilde{g}_i^{(t)} + \mathcal{N}(0, (\sigma^{(t)})^2 I)\right)$$

### 2.5 Theoretical Privacy Guarantees

**Theorem 1 (End-to-End Privacy):** Under the APBA framework, the entire training process satisfies $(\varepsilon_{\text{total}}, \delta)$-differential privacy where:

$$\varepsilon_{\text{total}} = \sum_{t=1}^{T} \varepsilon^{(t)} + \varepsilon_{\text{detect}}$$

and $\varepsilon_{\text{detect}}$ accounts for the privacy cost of shift detection.

**Proof Sketch:** By the sequential composition theorem and the post-processing property of DP, the total privacy loss is bounded by the sum of per-round losses. The shift detection module operates on already-privatized gradient features, adding only $\varepsilon_{\text{detect}}$ to the total budget through moments accountant analysis.

**Theorem 2 (Utility Improvement):** Under mild assumptions on shift frequency and magnitude, APBA achieves lower expected loss compared to uniform allocation:

$$\mathbb{E}[\mathcal{L}_{\text{APBA}}] \leq \mathbb{E}[\mathcal{L}_{\text{uniform}}] - \Omega\left(\sqrt{\text{Var}(\Delta^{(t)})}\right)$$

### 2.6 Experimental Design

**Datasets and Benchmarks**

1. **Federated EMNIST with Temporal Shifts**: We simulate temporal user evolution by gradually rotating digit classes and introducing new writing styles.

2. **Reddit Comments (Next-Word Prediction)**: Natural language data with inherent temporal drift as language patterns evolve over months.

3. **Stack Overflow (Tag Prediction)**: Programming Q&A data with technology trend shifts.

4. **Synthetic Rotating Gaussians**: Controlled benchmark where shift magnitude and frequency are precisely controllable.

**Baselines**

- Uniform DP allocation (standard DP-FedAvg)
- Time-adaptive spending (Kiani et al., 2025)
- Non-private continual FL (upper bound)
- Dordis (Jiang et al., 2022) for dropout-resilient comparison

**Evaluation Metrics**

1. **Model Utility**: Test accuracy/perplexity averaged over time
2. **Privacy Budget Efficiency**: Utility achieved per unit of privacy budget spent
3. **Adaptation Speed**: Rounds required to recover performance after shift
4. **Cumulative Regret**: $\sum_{t=1}^{T} (\mathcal{L}^{(t)} - \mathcal{L}^{*(t)})$ where $\mathcal{L}^{*(t)}$ is optimal loss

**Experimental Protocol**

- Total privacy budget: $\varepsilon_{\text{total}} \in \{1, 4, 8\}$
- Training horizon: $T = 500$ rounds
- Clients per round: 100 out of 10,000 total
- Three independent runs with different random seeds
- Statistical significance testing via paired t-tests

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Quantitative Improvements**: We anticipate 20-30% improvement in model utility under identical privacy budgets compared to uniform allocation, with larger gains in high-shift scenarios.

2. **Efficient Shift Detection**: The proposed federated analytics mechanism is expected to detect distribution shifts with >85% precision while consuming <5% of the total privacy budget.

3. **Sustainable Long-term Deployment**: The framework will enable federated models to maintain utility over 2-3× longer operational periods compared to fixed allocation strategies.

4. **Theoretical Contributions**: Formal privacy guarantees under adaptive allocation with tighter composition bounds than naive analysis.

### Broader Impact

**For Practitioners**: This work provides immediately deployable algorithms for production federated learning systems, with reference implementations compatible with existing frameworks like TensorFlow Federated and PySyft.

**For Researchers**: Our theoretical framework opens new directions for studying the interplay between distribution shift, continual learning, and differential privacy, with realistic assumptions grounded in practical constraints.

**For Society**: By enabling sustainable privacy-preserving AI systems, this research supports the responsible deployment of machine learning in sensitive domains such as healthcare, finance, and personal devices, advancing the goal of beneficial AI that respects individual privacy rights.

**Open Science Commitment**: We will release all code, experimental configurations, and synthetic benchmarks to facilitate reproducibility and encourage follow-up research in this important area bridging federated learning theory and practice.