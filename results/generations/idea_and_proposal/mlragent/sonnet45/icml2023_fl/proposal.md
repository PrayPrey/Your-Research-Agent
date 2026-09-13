# Federated Continual Learning with Adaptive Client Selection for Mitigating Catastrophic Forgetting under Distribution Shift

## 1. Introduction

### Background

Federated Learning (FL) has emerged as a transformative paradigm for collaborative machine learning, enabling multiple clients to jointly train models without sharing raw data. Since its introduction in 2016, FL has made remarkable progress in both theoretical foundations and practical deployments across domains such as mobile keyboard prediction, healthcare monitoring, and IoT applications. However, a critical gap persists between theoretical FL research and real-world applications: most existing approaches assume static data distributions, while practical deployments face continuously evolving data streams where client distributions shift heterogeneously over time.

This temporal drift phenomenon manifests in various forms. In mobile keyboard prediction, user vocabularies and typing patterns evolve as language trends change. In healthcare monitoring, patient conditions and sensor readings drift with seasonal variations and disease progression. In recommendation systems, user preferences shift with emerging trends and life events. These scenarios exemplify the challenge of **catastrophic forgetting** in federated settings—where models trained on new data distributions lose performance on previously learned patterns, leading to degraded service quality and user dissatisfaction.

Recent literature has begun addressing this challenge. Kokkula et al. (2026) demonstrated client-side experience replay for temporal drift, while Bhope et al. (2025) introduced mixture-of-experts frameworks for shift-aware adaptation. However, these approaches either require significant client-side storage (limiting scalability), lack privacy-preserving guarantees for shared memory mechanisms, or fail to dynamically adapt client selection strategies based on temporal distribution characteristics. The FPPL framework (He et al., 2024) avoids rehearsal through prototype learning but doesn't explicitly handle continuous temporal shifts without task boundaries.

### Research Objectives

This research proposes a comprehensive **Federated Continual Learning with Adaptive Client Selection (FCL-ACS)** framework that addresses the following objectives:

1. **Develop privacy-preserving drift detection mechanisms** that identify temporal distribution shifts across clients using lightweight statistical signatures without violating privacy constraints
2. **Design memory-augmented federated architectures** that maintain compact, differentially-private episodic memories representing historical distributions through secure aggregation
3. **Create adaptive client selection strategies** that balance exploration of novel distributions with exploitation of historical knowledge using multi-armed bandit approaches
4. **Formulate federated regularization techniques** that consolidate important weights collaboratively across clients to prevent catastrophic forgetting
5. **Validate the framework** on realistic federated continual learning benchmarks with evolving distribution shifts

### Significance

This research bridges the critical gap between FL theory and practice by enabling long-lived federated systems that gracefully adapt to evolving user behaviors. The significance includes:

- **Practical Impact**: Enables sustainable FL deployments in production environments where data distributions naturally evolve, reducing model retraining costs and improving user experience
- **Privacy Preservation**: Maintains differential privacy guarantees while implementing continual learning mechanisms, addressing regulatory requirements (GDPR, HIPAA)
- **Resource Efficiency**: Reduces communication costs through intelligent client selection and compact memory representations suitable for resource-constrained devices
- **Theoretical Contributions**: Advances understanding of the interplay between distribution shift, catastrophic forgetting, and federated optimization under realistic temporal dynamics

## 2. Methodology

### 2.1 Problem Formulation

Consider a federated learning system with $N$ clients. At round $t$, each client $i$ has local data $\mathcal{D}_i^{(t)} = \{(x_j, y_j)\}$ drawn from a time-varying distribution $P_i^{(t)}(X, Y)$. The goal is to learn a global model $w^{(t)}$ that minimizes:

$$\min_{w} \mathbb{E}_{t}\left[\sum_{i=1}^{N} p_i \mathbb{E}_{(x,y) \sim P_i^{(t)}} [\ell(f(x; w), y)]\right]$$

subject to constraints:
- Privacy: Shared information satisfies $(\epsilon, \delta)$-differential privacy
- Memory: Client-side storage limited to $M$ samples
- Forgetting: Performance on $P_i^{(t-k)}$ degrades minimally for $k > 0$

### 2.2 Architecture Overview

FCL-ACS consists of four interconnected components:

#### 2.2.1 Dynamic Client Clustering with Drift Detection

**Statistical Signature Extraction**: Each client $i$ computes lightweight distribution signatures using:

$$s_i^{(t)} = \{\mu_i^{(t)}, \Sigma_i^{(t)}, H_i^{(t)}\}$$

where $\mu_i^{(t)}$ is the feature mean, $\Sigma_i^{(t)}$ is the covariance (low-rank approximation), and $H_i^{(t)}$ is the label histogram. These are computed locally without sharing raw data.

**Drift Detection Mechanism**: We employ Maximum Mean Discrepancy (MMD) to detect distribution shifts:

$$\text{MMD}^2(P_i^{(t)}, P_i^{(t-\tau)}) = \left\|\mathbb{E}_{x \sim P_i^{(t)}}[\phi(x)] - \mathbb{E}_{x \sim P_i^{(t-\tau)}}[\phi(x)]\right\|^2_{\mathcal{H}}$$

where $\phi(\cdot)$ maps to a reproducing kernel Hilbert space. Using the unbiased estimator with Gaussian kernel $k(x, x') = \exp(-\|x-x'\|^2/2\sigma^2)$:

$$\widehat{\text{MMD}}^2 = \frac{1}{m^2}\sum_{i,j}k(x_i, x_j) + \frac{1}{n^2}\sum_{i,j}k(x'_i, x'_j) - \frac{2}{mn}\sum_{i,j}k(x_i, x'_j)$$

A shift is detected when $\widehat{\text{MMD}}^2 > \theta_{\text{drift}}$, where $\theta_{\text{drift}}$ is determined via bootstrap hypothesis testing.

**Privacy-Preserving Clustering**: Clients are clustered using privacy-preserving k-means on aggregated signatures:

$$C^{(t)} = \{C_1^{(t)}, \ldots, C_K^{(t)}\} = \underset{\{C_k\}}{\arg\min} \sum_{k=1}^{K} \sum_{i \in C_k} \|s_i^{(t)} - \bar{s}_k^{(t)}\|^2 + \eta_{\text{DP}}$$

where $\eta_{\text{DP}} \sim \mathcal{N}(0, \sigma_{\text{DP}}^2)$ provides differential privacy with $\sigma_{\text{DP}} = \frac{2\Delta_2 \sqrt{2\log(1.25/\delta)}}{\epsilon}$ and sensitivity $\Delta_2$.

#### 2.2.2 Memory-Augmented Global Model

**Episodic Memory Construction**: Maintain a global episodic memory $\mathcal{M}^{(t)} = \{(\tilde{x}_j, \tilde{y}_j, \tau_j)\}_{j=1}^{M_{\text{global}}}$ storing synthetic representative samples with timestamps.

**Secure Aggregation Protocol for Memory**:
1. Clients generate local prototypes using k-means clustering: $\mathcal{P}_i = \{p_{i,c}\}_{c=1}^{C_i}$
2. Add calibrated Gaussian noise for local differential privacy: $\tilde{p}_{i,c} = p_{i,c} + \mathcal{N}(0, \sigma_{\text{LDP}}^2 I)$
3. Server aggregates prototypes using secure aggregation: $\bar{p}_c = \frac{1}{|S|}\sum_{i \in S} \tilde{p}_{i,c}$
4. Update global memory by selecting diverse samples maximizing:

$$\mathcal{M}^{(t)} = \underset{|\mathcal{M}'|=M_{\text{global}}}{\arg\max} \sum_{j=1}^{M_{\text{global}}} \min_{j' \neq j} \|\tilde{x}_j - \tilde{x}_{j'}\|_2 + \lambda_{\text{temp}} \cdot \text{age}(\tau_j)$$

This ensures diversity and temporal coverage while satisfying $(\epsilon_{\text{mem}}, \delta_{\text{mem}})$-DP through composition.

#### 2.2.3 Adaptive Client Selection via Multi-Armed Bandits

**Contextual Bandit Formulation**: Model client selection as a combinatorial contextual bandit where:
- **Context**: $c_i^{(t)} = [s_i^{(t)}, \text{MMD}_i^{(t)}, \text{age}_i^{(t)}, \text{cluster}_i^{(t)}]$
- **Action**: Select subset $S^{(t)} \subset \{1, \ldots, N\}$ with $|S^{(t)}| = K$
- **Reward**: Improvement on validation metrics balancing new and old distributions

**Selection Strategy**: Use Upper Confidence Bound (UCB) approach with exploration-exploitation trade-off:

$$\text{score}_i^{(t)} = \underbrace{\hat{\mu}_i^{(t)}}_{\text{exploitation}} + \beta \underbrace{\sqrt{\frac{\log t}{n_i^{(t)}}}}_{\text{exploration}} + \gamma \underbrace{\text{MMD}_i^{(t)}}_{\text{novelty}}$$

where $\hat{\mu}_i^{(t)}$ is the empirical reward from client $i$, $n_i^{(t)}$ is selection count, and $\beta, \gamma$ balance exploration vs. novelty.

**Cluster-Aware Sampling**: Ensure representation from each cluster:

$$S^{(t)} = \bigcup_{k=1}^{K} \underset{i \in C_k^{(t)}}{\text{top-}m_k} \text{score}_i^{(t)}$$

where $\sum_{k=1}^{K} m_k = K$ and $m_k \propto |C_k^{(t)}|$ ensures proportional representation.

#### 2.2.4 Federated Elastic Weight Consolidation

**Importance Weight Computation**: Adapt Elastic Weight Consolidation (EWC) for federated settings. Each client $i$ computes local Fisher Information Matrix (FIM) diagonal:

$$F_{i,j}^{(t)} = \mathbb{E}_{(x,y) \sim \mathcal{D}_i^{(t)}}\left[\left(\frac{\partial \log p(y|x; w)}{\partial w_j}\right)^2\right]$$

**Federated Aggregation of Importance**: Aggregate importance weights using weighted averaging:

$$\bar{F}_j^{(t)} = \frac{\sum_{i \in S^{(t)}} n_i F_{i,j}^{(t)}}{\sum_{i \in S^{(t)}} n_i} + \mathcal{N}(0, \sigma_{\text{FIM}}^2)$$

where noise ensures DP. Store consolidated weights: $w_{\text{old}}^{(t)} = w^{(t)}$.

**Regularized Objective**: Clients optimize:

$$\mathcal{L}_i^{(t)}(w) = \underbrace{\mathbb{E}_{(x,y) \sim \mathcal{D}_i^{(t)}}[\ell(f(x; w), y)]}_{\text{current task}} + \underbrace{\frac{\lambda_{\text{EWC}}}{2}\sum_{j} \bar{F}_j^{(t)}(w_j - w_{\text{old},j}^{(t)})^2}_{\text{consolidation}} + \underbrace{\mathbb{E}_{(x,y) \sim \mathcal{M}^{(t)}}[\ell(f(x; w), y)]}_{\text{memory replay}}$$

This prevents drift on important parameters while learning new patterns.

### 2.3 Training Algorithm

**Algorithm 1: FCL-ACS Training Protocol**

```
Server:
  Initialize: w^(0), M^(0) = ∅, statistics {s_i} = ∅
  For round t = 1 to T:
    1. Receive client signatures {s_i^(t)} from all clients
    2. Detect drift: Compute MMD_i^(t) for each client
    3. Update clusters: C^(t) = PrivateKMeans({s_i^(t)})
    4. Adaptive selection: S^(t) = SelectClients(C^(t), MMD^(t))
    5. Broadcast: Send w^(t), M^(t), F̄^(t) to S^(t)
    6. Receive: Collect updates {Δw_i, P_i} from S^(t)
    7. Update memory: M^(t+1) = UpdateMemory(M^(t), {P_i})
    8. Aggregate: w^(t+1) = w^(t) + η · (1/|S^(t)|) Σ_{i∈S^(t)} Δw_i
    9. Update FIM: F̄^(t+1) = AggregrateFIM({F_i})

Client i (if selected):
  Receive: w^(t), M^(t), F̄^(t)
  For epoch e = 1 to E:
    1. Sample batch B_i from D_i^(t)
    2. Sample memory batch B_M from M^(t)
    3. Compute loss: L = L_task(B_i) + λ_EWC·L_EWC(w, w_old, F̄) + λ_M·L_task(B_M)
    4. Update: w_i ← w_i - α·∇L
  Compute: Local FIM F_i, prototypes P_i, signature s_i^(t)
  Send: Δw_i = w_i - w^(t), F_i, P_i, s_i^(t) to server
```

### 2.4 Privacy Analysis

**Theorem 1** (Privacy Guarantee): FCL-ACS satisfies $(\epsilon_{\text{total}}, \delta_{\text{total}})$-differential privacy where:

$$\epsilon_{\text{total}} = \epsilon_{\text{cluster}} + \epsilon_{\text{mem}} + T \cdot \epsilon_{\text{FIM}} + \epsilon_{\text{grad}}$$

through advanced composition, with:
- $\epsilon_{\text{cluster}}$: Gaussian mechanism for clustering
- $\epsilon_{\text{mem}}$: Prototype aggregation privacy
- $\epsilon_{\text{FIM}}$: Fisher information sharing
- $\epsilon_{\text{grad}}$: Gradient perturbation (DP-SGD)

### 2.5 Experimental Design

#### 2.5.1 Datasets and Benchmarks

**Synthetic Federated Continual Learning Benchmarks**:
1. **Rotated CIFAR-10**: 100 clients, 5 temporal phases with incremental rotations (0°, 15°, 30°, 45°, 60°)
2. **Federated CLOC**: Real-world camera location dataset with temporal shifts
3. **Stack Overflow Next-Word Prediction**: Natural language temporal drift over 2-year period
4. **Google Speech Commands**: Acoustic environment shifts across time

**Distribution Shift Scenarios**:
- **Covariate Shift**: Feature distributions change, labels remain consistent
- **Label Shift**: Class proportions evolve over time
- **Concept Drift**: Decision boundaries change gradually
- **Hybrid Shifts**: Combined covariate and label shifts

#### 2.5.2 Baseline Methods

Compare FCL-ACS against:
1. **FedAvg**: Standard federated averaging (no continual learning)
2. **FedProx**: Proximal regularization for heterogeneity
3. **Client-side Experience Replay** (Kokkula et al., 2026)
4. **FPPL** (He et al., 2024): Prototype-augmented prompts
5. **ShiftEx** (Bhope et al., 2025): Mixture of experts
6. **Re-weighted Softmax** (Legate et al., 2023)

#### 2.5.3 Evaluation Metrics

**Performance Metrics**:
1. **Average Accuracy**: $\bar{A}^{(t)} = \frac{1}{t}\sum_{\tau=1}^{t} A_{\tau}$ on all distributions seen until round $t$
2. **Backward Transfer**: $BWT = \frac{1}{T-1}\sum_{i=1}^{T-1}(A_{T,i} - A_{i,i})$ measuring forgetting
3. **Forward Transfer**: $FWT = \frac{1}{T-1}\sum_{i=2}^{T}(A_{i-1,i} - A_{0,i})$ measuring knowledge transfer
4. **Final Average Accuracy**: $FAA = \frac{1}{T}\sum_{i=1}^{T} A_{T,i}$

**Efficiency Metrics**:
1. **Communication Cost**: Total bytes transmitted
2. **Client Selection Diversity**: Entropy of selection distribution
3. **Memory Overhead**: Storage per client and server
4. **Computational Cost**: FLOPs per round

**Privacy Metrics**:
1. **Privacy Budget Consumption**: Track $(\epsilon, \delta)$ over time
2. **Membership Inference Attack Success Rate**: Audit privacy empirically

#### 2.5.4 Experimental Configuration

**Hyperparameters**:
- Clients: $N = 100$ (cross-device), $N = 10$ (cross-silo)
- Selection per round: $K = 10$ (10%)
- Local epochs: $E = 5$
- Learning rate: $\alpha = 0.01$ with cosine annealing
- EWC strength: $\lambda_{\text{EWC}} = 1000$
- Memory replay: $\lambda_M = 0.5$
- Memory size: $M_{\text{global}} = 5000$, $M_{\text{client}} = 100$
- Privacy: $\epsilon_{\text{total}} = 8$, $\delta = 10^{-5}$
- UCB parameters: $\beta = 0.5$, $\gamma = 0.3$

**Statistical Validation**:
- Run each experiment with 5 random seeds
- Report mean and 95% confidence intervals
- Conduct paired t-tests for significance ($p < 0.05$)

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Performance Improvements**:
1. **Catastrophic Forgetting Reduction**: Expect >30% improvement in backward transfer compared to FedAvg, demonstrating reduced forgetting through combined EWC and memory replay
2. **Distribution Shift Adaptation**: Anticipate 20-25% higher average accuracy under temporal drift scenarios compared to non-adaptive baselines
3. **Privacy-Utility Trade-off**: Achieve competitive performance within ε=8 privacy budget, outperforming methods without privacy guarantees when privacy constraints are applied fairly

**Algorithmic Insights**:
1. **Client Selection Dynamics**: Demonstrate that adaptive selection converges to optimal exploration-exploitation balance within 50-100 rounds
2. **Memory Efficiency**: Show that compact episodic memory (≈1% of total data) captures sufficient distributional diversity
3. **Clustering Effectiveness**: Validate that drift-based clustering identifies 3-5 distinct temporal regimes in realistic scenarios

**Practical Deployment Guidelines**:
1. Configuration recommendations for different application domains (mobile, healthcare, IoT)
2. Trade-off analysis between privacy budget, memory size, and forgetting metrics
3. Client selection frequency optimization based on drift detection rates

### 3.2 Scientific Impact

**Theoretical Contributions**:
1. **Convergence Analysis**: Provide theoretical bounds on forgetting under federated continual learning with non-IID temporal shifts
2. **Privacy-Forgetting Trade-off**: Formalize the fundamental limits connecting differential privacy guarantees with catastrophic forgetting mitigation
3. **Bandit Regret Bounds**: Establish regret bounds for adaptive client selection under distribution shift

**Methodological Advances**:
1. First comprehensive framework integrating drift detection, adaptive selection, and privacy-preserving memory in federated continual learning
2. Novel application of multi-armed bandits for temporal exploration-exploitation in FL
3. Federated EWC formulation enabling collaborative importance weight estimation

### 3.3 Practical Impact

**Industry Applications**:
1. **Mobile Keyboard Prediction**: Enable long-lived models adapting to evolving language trends without periodic retraining
2. **Healthcare Monitoring**: Support continual adaptation to patient condition changes while maintaining HIPAA compliance
3. **Recommendation Systems**: Gracefully handle user preference evolution and seasonal trends
4. **IoT Predictive Maintenance**: Adapt to equipment aging and environmental changes

**System Design Implications**:
1. Reduce model retraining frequency by 60-70%, decreasing operational costs
2. Improve user experience through better personalization under evolving behaviors
3. Enable sustainable FL deployments with multi-year lifespans

**Broader Impact**:
1. **Open Source Contributions**: Release FCL-ACS implementation in TensorFlow Federated and Flower frameworks
2. **Benchmark Datasets**: Contribute realistic federated continual learning benchmarks to the community
3. **Best Practices**: Publish deployment guidelines for production federated continual learning systems

**Societal Considerations**:
1. **Privacy Enhancement**: Strengthen privacy protections for users participating in long-term federated learning
2. **Fairness**: Adaptive selection may improve fairness by ensuring representation across diverse client populations
3. **Environmental**: Reduced retraining needs decrease computational carbon footprint

### 3.4 Future Research Directions

This work opens several promising research avenues:

1. **Federated Lifelong Learning**: Extend to open-world scenarios with unknown task boundaries and emerging classes
2. **Personalization Integration**: Combine global continual learning with client-specific personalization
3. **Multi-Modal Continual Learning**: Adapt framework for federated learning across vision, language, and sensor modalities
4. **Theoretical Foundations**: Develop PAC-learning bounds for federated continual learning
5. **Hardware Acceleration**: Design efficient implementations for edge devices with neuromorphic computing

### 3.5 Validation of Success

Success criteria for the research include:

1. **Performance Thresholds**: Achieve BWT > -10% and FAA > 70% on benchmark datasets
2. **Publication**: Accept papers at top-tier ML conferences (NeurIPS, ICML, ICLR) and FL workshops
3. **Community Adoption**: Achieve >100 GitHub stars and integration requests from industrial partners
4. **Real-World Deployment**: Pilot deployment in at least one production federated learning system
5. **Reproducibility**: Provide comprehensive experimental artifacts enabling full reproducibility

## Conclusion

This research proposal presents FCL-ACS, a comprehensive framework addressing the critical challenge of catastrophic forgetting under distribution shifts in practical federated learning systems. By integrating privacy-preserving drift detection, adaptive client selection, memory-augmented architectures, and federated regularization, FCL-ACS bridges the gap between theoretical FL research and real-world deployments facing temporal dynamics. The expected outcomes include significant reductions in catastrophic forgetting, improved adaptation to evolving distributions, and practical deployment guidelines—collectively enabling sustainable, long-lived federated learning systems that maintain privacy guarantees while gracefully adapting to changing user behaviors. This work contributes to the workshop's mission of bringing FL theory closer to practice, with immediate applicability to production systems in mobile, healthcare, and IoT domains.