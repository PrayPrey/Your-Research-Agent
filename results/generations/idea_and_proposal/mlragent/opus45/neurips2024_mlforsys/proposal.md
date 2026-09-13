# Research Proposal: Carbon-Aware Neural Job Scheduling with Multi-Horizon Carbon Intensity Forecasting

## 1. Introduction

### Background

The rapid expansion of cloud computing and large-scale machine learning has created an unprecedented demand for computational resources, with datacenters now accounting for approximately 1-2% of global electricity consumption and associated carbon emissions projected to triple by 2030. Major cloud providers including Google, Microsoft, and Amazon have committed to ambitious sustainability targets, yet the fundamental job scheduling mechanisms that govern datacenter operations remain largely carbon-agnostic. This disconnect between sustainability goals and operational practices represents both a critical challenge and a significant opportunity for systems research.

Carbon intensity—the amount of CO2 emitted per unit of electricity generated—varies dramatically across time and geography due to fluctuations in renewable energy availability, grid demand patterns, and the mix of generation sources. Studies have demonstrated that strategic temporal and spatial shifting of computational workloads can reduce carbon footprints by 20-40% without substantial performance degradation. However, realizing these benefits requires accurate forecasting of carbon intensity across multiple time horizons and intelligent scheduling algorithms that can navigate the complex trade-offs between carbon reduction, performance objectives, and resource utilization.

Existing approaches to carbon-aware computing suffer from several limitations. First, carbon intensity forecasting methods typically focus on single time horizons, failing to capture the multi-scale temporal patterns essential for both immediate scheduling decisions and longer-term capacity planning. Second, current scheduling algorithms often treat carbon predictions as deterministic, ignoring the inherent uncertainty that can lead to suboptimal or infeasible schedules. Third, the hierarchical nature of datacenter scheduling—spanning strategic placement decisions down to fine-grained resource allocation—has not been adequately addressed in carbon-aware frameworks.

### Research Objectives

This research proposes **CarbonSched**, a comprehensive framework for carbon-aware job scheduling that addresses these limitations through three integrated innovations:

1. **Multi-Horizon Carbon Intensity Forecasting**: Develop a transformer-based model that simultaneously predicts carbon intensity at multiple temporal granularities (15-minute, hourly, daily) while providing calibrated uncertainty estimates.

2. **Hierarchical Reinforcement Learning for Scheduling**: Design a two-level RL architecture where a high-level policy handles strategic decisions about job deferral and geographic placement, while a low-level policy manages fine-grained resource allocation and preemption.

3. **Uncertainty-Aware Carbon Budget Mechanism**: Create a principled framework that guarantees carbon emission caps while minimizing deadline violations through chance-constrained optimization informed by forecast confidence intervals.

### Significance

This research addresses the urgent need for sustainable computing infrastructure by providing a practical, deployable solution that can achieve significant carbon reductions without sacrificing performance. The framework directly supports the ML for Systems workshop's focus on compute sustainability and addresses the emerging systems challenges from large-scale training and serving. By open-sourcing our implementation and evaluation framework, we aim to accelerate the adoption of carbon-aware practices across the cloud computing industry.

## 2. Methodology

### 2.1 System Architecture Overview

CarbonSched consists of three tightly integrated components: (1) a Multi-Horizon Carbon Forecaster (MHCF), (2) a Hierarchical Carbon-Aware Scheduler (HCAS), and (3) a Carbon Budget Controller (CBC). The system operates across geographically distributed datacenters, receiving real-time carbon intensity signals, job arrival streams, and resource availability updates.

### 2.2 Multi-Horizon Carbon Intensity Forecasting

#### Data Sources and Feature Engineering

Our forecasting module integrates multiple data streams:
- **Grid data**: Historical and real-time carbon intensity from electricity grid operators (e.g., ElectricityMap, WattTime)
- **Weather data**: Solar irradiance, wind speed, temperature, and precipitation forecasts from meteorological services
- **Temporal features**: Hour-of-day, day-of-week, holiday indicators, and seasonal patterns
- **Grid topology**: Interconnection capacities, scheduled maintenance, and demand forecasts

For each region $r$ at time $t$, we construct a feature vector $\mathbf{x}_{r,t} \in \mathbb{R}^d$ combining these sources.

#### Transformer-Based Multi-Horizon Model

We employ a temporal fusion transformer architecture that generates predictions at multiple horizons simultaneously. Given a context window of historical observations $\{\mathbf{x}_{r,t-L}, ..., \mathbf{x}_{r,t}\}$, the model outputs:

$$\hat{c}_{r,t+h}, \hat{\sigma}_{r,t+h} = f_\theta(\mathbf{x}_{r,t-L:t}, h) \quad \text{for } h \in \{1, 4, 24, 96\}$$

where $\hat{c}_{r,t+h}$ is the predicted carbon intensity $h$ steps ahead, $\hat{\sigma}_{r,t+h}$ is the predicted uncertainty, and the horizons correspond to 15-minute, 1-hour, 6-hour, and 24-hour forecasts.

The architecture employs:
1. **Variable selection networks** to identify relevant features for each horizon
2. **Multi-head attention** over temporal patterns with horizon-specific query projections
3. **Quantile regression heads** outputting the 10th, 50th, and 90th percentiles

The training loss combines quantile loss across horizons:

$$\mathcal{L}_{forecast} = \sum_{h} \sum_{q \in \{0.1, 0.5, 0.9\}} \lambda_h \cdot \mathcal{L}_q(\hat{c}^{(q)}_{r,t+h}, c_{r,t+h})$$

where $\mathcal{L}_q$ is the pinball loss for quantile $q$ and $\lambda_h$ are horizon-specific weights.

### 2.3 Hierarchical Reinforcement Learning Scheduler

#### Problem Formulation

We formulate carbon-aware scheduling as a hierarchical Markov Decision Process (H-MDP). Jobs arrive with attributes $(d_j, w_j, \tau_j^{arr}, \tau_j^{dead}, p_j)$ representing resource demand, expected runtime, arrival time, deadline, and priority respectively.

**High-Level MDP** (decision interval: 15 minutes):
- **State** $s^H_t$: Queue status across regions, carbon forecasts $\{\hat{c}_{r,t:t+H}\}$, current carbon budget utilization
- **Action** $a^H_t$: For each queued job, decide (defer, assign to region $r$, or reject)
- **Reward**: Weighted combination of negative carbon emissions and deadline satisfaction

**Low-Level MDP** (decision interval: 1 minute):
- **State** $s^L_t$: Regional resource availability, running jobs, immediate carbon intensity
- **Action** $a^L_t$: Resource allocation, job preemption/migration decisions
- **Reward**: Resource utilization efficiency and SLO compliance

#### Policy Architecture

The high-level policy $\pi^H$ employs an attention-based architecture:

$$\pi^H(a^H_t | s^H_t) = \text{softmax}\left(\text{MLP}\left(\text{Attention}(\mathbf{Q}_j, \mathbf{K}_{forecast}, \mathbf{V}_{forecast})\right)\right)$$

where job embeddings form queries attending over regional carbon forecast embeddings.

The low-level policy $\pi^L$ uses a graph neural network to capture resource dependencies:

$$\pi^L(a^L_t | s^L_t, g^H_t) = \text{GNN}(\mathcal{G}_{resources}, g^H_t)$$

where $g^H_t$ is a goal embedding from the high-level policy specifying regional allocation targets.

#### Training Procedure

We employ hierarchical actor-critic training with the following objectives:

**High-level policy gradient**:
$$\nabla_{\theta^H} J = \mathbb{E}\left[\sum_t \nabla_{\theta^H} \log \pi^H(a^H_t|s^H_t) \cdot A^H_t\right]$$

**Low-level policy gradient** with goal-conditioned rewards:
$$\nabla_{\theta^L} J = \mathbb{E}\left[\sum_t \nabla_{\theta^L} \log \pi^L(a^L_t|s^L_t, g^H_t) \cdot A^L_t\right]$$

We use PPO with generalized advantage estimation and employ hindsight experience replay to improve sample efficiency.

### 2.4 Carbon Budget Controller

To provide hard guarantees on carbon emissions, we implement a chance-constrained carbon budget mechanism. Given a carbon budget $B$ for period $T$:

$$\Pr\left[\sum_{t=1}^T \sum_{r} E_{r,t} \cdot c_{r,t} \leq B\right] \geq 1 - \delta$$

where $E_{r,t}$ is energy consumption in region $r$ at time $t$.

Using the forecast uncertainty estimates, we compute a conservative carbon rate limit:

$$\bar{E}_t = \frac{B - \sum_{\tau<t} E_\tau \cdot c_\tau}{\sum_{h=1}^{T-t} \hat{c}^{(0.9)}_{t+h}}$$

This limit is communicated to the RL policies as a constraint, with violations penalized in the reward function:

$$r_t = -\alpha \cdot \text{Carbon}_t + \beta \cdot \text{Throughput}_t - \gamma \cdot \max(0, E_t - \bar{E}_t)^2$$

### 2.5 Experimental Design

#### Datasets

1. **Workload traces**: Google Cluster Traces (2019), Azure Public Dataset, and Alibaba Cluster Trace
2. **Carbon intensity data**: ElectricityMap API covering 5 major regions (US-West, US-East, EU-West, EU-North, Asia-Pacific) at 15-minute granularity for 2022-2024
3. **Weather data**: ERA5 reanalysis data aligned with carbon intensity measurements

#### Baselines

- **Carbon-agnostic**: FIFO, Shortest Job First, Dominant Resource Fairness
- **Static carbon-aware**: Round-robin with carbon threshold, Follow-the-Sun
- **Learning-based**: LACS, LUCA (adapted), Single-horizon RL scheduler

#### Evaluation Metrics

1. **Carbon Metrics**:
   - Total carbon emissions (kg CO2e)
   - Carbon efficiency: jobs completed per kg CO2e
   - Budget compliance rate

2. **Performance Metrics**:
   - Job completion rate within deadline
   - Average job completion time (JCT)
   - 99th percentile JCT (tail latency)

3. **System Metrics**:
   - Resource utilization across regions
   - Migration overhead
   - Scheduling decision latency

#### Experimental Protocol

We conduct experiments through discrete-event simulation with the following configurations:
- **Scale**: 10,000 to 1,000,000 jobs over 30-day periods
- **Job mix**: 60% batch (flexible deadline), 30% service (SLO-bound), 10% urgent
- **Carbon budget scenarios**: Tight (50% of carbon-agnostic baseline), moderate (75%), relaxed (90%)

Ablation studies will isolate contributions of:
1. Multi-horizon vs. single-horizon forecasting
2. Hierarchical vs. flat RL architecture
3. Uncertainty-aware vs. deterministic scheduling

## 3. Expected Outcomes & Impact

### Anticipated Results

Based on preliminary experiments and related work, we expect CarbonSched to achieve:

1. **Carbon Reduction**: 25-35% reduction in carbon emissions compared to carbon-agnostic baselines, with 15-20% improvement over existing carbon-aware methods through better forecasting and uncertainty handling.

2. **Performance Preservation**: Less than 5% degradation in average job completion time and less than 10% increase in tail latency, demonstrating practical deployability.

3. **Budget Compliance**: Greater than 95% compliance with carbon budgets under the moderate scenario, significantly outperforming methods without explicit budget mechanisms.

4. **Forecasting Accuracy**: MAPE below 10% for 1-hour forecasts and below 20% for 24-hour forecasts, with well-calibrated uncertainty estimates (coverage probability within 5% of target).

### Scientific Contributions

1. **Novel multi-horizon forecasting architecture** specifically designed for carbon intensity with integrated uncertainty quantification
2. **First hierarchical RL framework** for carbon-aware scheduling that separates strategic and tactical decisions
3. **Principled carbon budget mechanism** providing probabilistic guarantees while maintaining scheduling flexibility
4. **Comprehensive benchmark suite** for carbon-aware scheduling research

### Broader Impact

This research provides a practical pathway for sustainable cloud computing at scale. By demonstrating that significant carbon reductions are achievable without substantial performance penalties, we aim to accelerate industry adoption of carbon-aware practices. The open-source release of CarbonSched, including trained models and evaluation tools, will enable:

- Cloud providers to integrate carbon awareness into production schedulers
- Researchers to build upon our framework for further innovations
- Policymakers to understand the potential of algorithmic approaches to datacenter decarbonization

As datacenters increasingly face regulatory pressure and customer demand for sustainability, CarbonSched offers a technically rigorous and deployable solution that balances environmental responsibility with operational excellence.