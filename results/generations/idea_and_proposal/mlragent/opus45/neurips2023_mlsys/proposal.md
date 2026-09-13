# Research Proposal: Carbon-Aware Neural Compiler Optimization for Distributed LLM Training

## 1. Introduction

### Background

The rapid advancement of large language models (LLMs) has revolutionized artificial intelligence, enabling unprecedented capabilities in natural language understanding, generation, and reasoning. However, this progress comes at a substantial environmental cost. Training state-of-the-art models like GPT-4 or LLaMA-3 requires thousands of GPUs or TPUs operating continuously for weeks or months, consuming megawatt-hours of electricity. Recent estimates suggest that training a single large model can emit hundreds of tons of CO₂ equivalent—comparable to the lifetime emissions of several automobiles.

Current ML compiler frameworks such as XLA, MLIR-based systems, and emerging tools like nncase optimize distributed training primarily for throughput, memory efficiency, and communication overhead. While these objectives are critical for practical deployment, they overlook a fundamental reality: the carbon intensity of electricity varies dramatically across time and geography. A computation executed during peak solar generation in California may produce a fraction of the emissions compared to the same computation during coal-heavy evening hours in the Midwest. This temporal and spatial variability presents an untapped opportunity for carbon optimization.

Existing carbon-aware computing approaches have primarily focused on inference workloads (e.g., EcoServe) or coarse-grained load balancing strategies. However, the unique characteristics of distributed LLM training—including its iterative nature, communication patterns, and checkpoint requirements—demand specialized solutions at the compiler level. The compiler, positioned between the model definition and hardware execution, represents an ideal intervention point for integrating carbon awareness into the training pipeline.

### Research Objectives

This research proposes **CarbonPartition**, a learned compiler optimization framework that makes carbon-awareness a first-class citizen in distributed LLM training decisions. Our specific objectives are:

1. **Develop a multi-objective optimization framework** that jointly considers training throughput, memory utilization, and carbon emissions in compiler partitioning and scheduling decisions.

2. **Design a graph neural network architecture** capable of encoding computation graphs, hardware topology, and carbon intensity signals to predict optimal partitioning strategies.

3. **Create a reinforcement learning agent** that learns to make real-time scheduling and placement decisions based on carbon intensity forecasts while respecting training deadlines.

4. **Establish reproducible benchmarks** for carbon-aware compiler optimization, providing the research community with standardized evaluation protocols.

### Significance

This research addresses the intersection of three critical areas highlighted by the ML for Systems workshop: (1) applying ML to compiler optimization, (2) addressing systems challenges in large-scale LLM training, and (3) promoting compute sustainability. By demonstrating that significant carbon reductions (15-25%) are achievable with minimal throughput degradation (<5%), we aim to shift the paradigm in how the community approaches compiler design for distributed training. Furthermore, our open-source benchmarks will accelerate reproducible research in carbon-aware systems.

## 2. Methodology

### 2.1 Problem Formulation

We formalize carbon-aware compiler optimization for distributed LLM training as a constrained multi-objective optimization problem. Let $G = (V, E)$ represent the computation graph where vertices $V$ correspond to operations (e.g., matrix multiplications, attention computations) and edges $E$ represent data dependencies. The distributed training cluster consists of $N$ devices across $R$ geographic regions, each with time-varying carbon intensity $c_r(t)$ (gCO₂/kWh).

The compiler must determine:
- **Partitioning strategy** $\pi: V \rightarrow \{1, ..., N\}$ mapping operations to devices
- **Scheduling function** $\sigma: V \rightarrow \mathbb{R}^+$ determining execution start times
- **Placement decisions** $\rho: V \rightarrow \{1, ..., R\}$ for geographically distributable operations

The optimization objective is:

$$\min_{\pi, \sigma, \rho} \quad \alpha \cdot T_{total}(\pi, \sigma) + (1-\alpha) \cdot C_{total}(\pi, \sigma, \rho)$$

subject to:
$$T_{total}(\pi, \sigma) \leq T_{deadline}$$
$$M_d(\pi) \leq M_d^{max} \quad \forall d \in \{1, ..., N\}$$

where $T_{total}$ is the total training time, $C_{total}$ is cumulative carbon emissions, $\alpha \in [0,1]$ is a user-specified trade-off parameter, and $M_d(\pi)$ represents memory usage on device $d$.

The carbon emission for a training iteration is computed as:

$$C_{total} = \sum_{v \in V} P_v \cdot \tau_v \cdot c_{\rho(v)}(\sigma(v))$$

where $P_v$ is the power consumption of operation $v$, $\tau_v$ is its execution duration, and $c_{\rho(v)}(\sigma(v))$ is the carbon intensity at the assigned region and time.

### 2.2 System Architecture

CarbonPartition consists of four integrated components:

**Component 1: Computation Graph Encoder (CGE)**

We employ a hierarchical graph neural network to encode the computation graph along with hardware and carbon context. For each node $v$, we construct initial features:

$$\mathbf{h}_v^{(0)} = [\mathbf{e}_{op(v)} \| \text{FLOPS}(v) \| \text{MemReq}(v) \| \mathbf{e}_{dtype(v)}]$$

where $\mathbf{e}_{op(v)}$ is a learned embedding for operation type and $\|$ denotes concatenation.

The GNN performs message passing across $L$ layers:

$$\mathbf{m}_v^{(l)} = \text{AGG}\left(\left\{\text{MLP}_e\left(\mathbf{h}_u^{(l-1)} \| \mathbf{h}_v^{(l-1)} \| \mathbf{e}_{(u,v)}\right) : u \in \mathcal{N}(v)\right\}\right)$$

$$\mathbf{h}_v^{(l)} = \text{MLP}_n\left(\mathbf{h}_v^{(l-1)} \| \mathbf{m}_v^{(l)}\right)$$

We additionally incorporate global context through cross-attention with hardware topology embeddings $\mathbf{H}_{hw}$ and carbon intensity forecasts $\mathbf{C}_{forecast}$:

$$\mathbf{g} = \text{CrossAttn}(\text{READOUT}(\{\mathbf{h}_v^{(L)}\}), [\mathbf{H}_{hw} \| \mathbf{C}_{forecast}])$$

**Component 2: Carbon Intensity Forecasting Module (CIFM)**

Accurate carbon intensity prediction is essential for proactive scheduling. We integrate a temporal forecasting model that processes historical carbon intensity data $\{c_r(t-k)\}_{k=0}^{K}$ for each region:

$$\hat{c}_r(t+\Delta) = \text{Transformer}_{temporal}(\{c_r(t-k)\}_{k=0}^{K}, \mathbf{e}_{weather}, \mathbf{e}_{time})$$

where $\mathbf{e}_{weather}$ encodes weather forecasts (affecting renewable generation) and $\mathbf{e}_{time}$ encodes time-of-day and day-of-week patterns. We leverage publicly available data from sources like WattTime and ElectricityMap.

**Component 3: Reinforcement Learning Scheduler (RLS)**

The scheduling agent operates over a Markov Decision Process defined as:

- **State** $s_t = (\mathbf{g}, \mathbf{H}_{hw}, \hat{\mathbf{C}}_{forecast}, \mathbf{q}_t)$ where $\mathbf{q}_t$ represents the current execution queue state
- **Action** $a_t = (\pi_t, \sigma_t, \rho_t)$ specifying partitioning, scheduling, and placement for the next batch of operations
- **Reward** $r_t = -\alpha \cdot \Delta T_t - (1-\alpha) \cdot \Delta C_t + \beta \cdot \mathbb{1}[\text{constraints satisfied}]$

We train the agent using Proximal Policy Optimization (PPO) with the policy network:

$$\pi_\theta(a_t | s_t) = \text{MLP}_{policy}(\mathbf{g} \| \mathbf{H}_{hw} \| \hat{\mathbf{C}}_{forecast} \| \mathbf{q}_t)$$

**Component 4: Adaptive Trade-off Controller (ATC)**

To handle varying user requirements and real-time conditions, we implement an adaptive controller that dynamically adjusts $\alpha$ based on:

$$\alpha_{adaptive}(t) = \alpha_{base} + \gamma \cdot \left(\frac{T_{elapsed}}{T_{deadline}} - \frac{t_{wall}}{t_{deadline}^{wall}}\right)$$

This allows the system to become more aggressive in carbon optimization when ahead of schedule and prioritize throughput when falling behind.

### 2.3 Training Procedure

**Phase 1: Supervised Pre-training**

We pre-train the GNN encoder using a dataset of computation graphs paired with expert-designed partitioning strategies from existing compilers (XLA, Megatron-LM). The loss function combines partitioning prediction and throughput estimation:

$$\mathcal{L}_{pretrain} = \mathcal{L}_{CE}(\hat{\pi}, \pi^*) + \lambda \cdot \mathcal{L}_{MSE}(\hat{T}, T^*)$$

**Phase 2: Reinforcement Learning Fine-tuning**

Using a simulation environment built on realistic hardware models and carbon intensity traces, we fine-tune the complete system end-to-end:

$$\mathcal{L}_{RL} = -\mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^{T} \gamma^t r_t\right]$$

We incorporate curriculum learning, starting with small models (125M parameters) and progressively scaling to larger architectures (7B+ parameters).

### 2.4 Experimental Design

**Datasets and Workloads:**
- Computation graphs from GPT-2 (125M, 355M, 774M, 1.5B), LLaMA-7B, and LLaMA-13B
- Carbon intensity traces from 10 geographic regions (US, Europe, Asia) spanning 12 months
- Hardware configurations: homogeneous (8×A100, 32×A100) and heterogeneous (A100 + V100 mixed) clusters

**Baselines:**
1. XLA default partitioning (throughput-optimized)
2. Megatron-LM pipeline parallelism
3. Carbon-agnostic round-robin scheduling
4. Static carbon-aware heuristics (always prefer greenest region)
5. AutoFL-style RL without carbon awareness

**Evaluation Metrics:**
- **Primary**: Carbon emissions (kgCO₂), Training throughput (samples/second), End-to-end training time
- **Secondary**: Memory utilization efficiency, Communication overhead, Energy consumption (kWh)
- **Trade-off**: Pareto frontier analysis of throughput vs. carbon

**Ablation Studies:**
1. Impact of carbon forecast accuracy on optimization quality
2. Contribution of each component (GNN encoder, RL scheduler, adaptive controller)
3. Sensitivity to trade-off parameter $\alpha$
4. Scalability analysis with increasing cluster size

## 3. Expected Outcomes & Impact

### Quantitative Outcomes

Based on preliminary analysis and related work, we anticipate:
- **15-25% reduction in carbon emissions** compared to carbon-agnostic baselines
- **<5% throughput degradation** under typical operating conditions
- **>90% accuracy** in carbon intensity forecasting over 24-hour horizons
- **Near-linear scalability** to clusters with 1000+ devices

### Scientific Contributions

1. **Novel formulation** of carbon-aware compiler optimization as a learnable multi-objective problem
2. **First integrated framework** combining GNN-based graph encoding with RL-based scheduling for carbon optimization
3. **Reproducible benchmarks** and open-source implementation enabling future research

### Broader Impact

This research directly addresses the sustainability imperative in AI development. As LLM training scales continue to grow, carbon-aware optimization will become essential for responsible AI development. Our framework provides:

- **Practical tools** for organizations seeking to reduce their AI carbon footprint
- **Policy-relevant metrics** demonstrating achievable trade-offs between performance and sustainability
- **Foundation for future research** in sustainable ML systems

By presenting this work at the ML for Systems workshop, we aim to catalyze community efforts toward standardized carbon-aware benchmarks and establish best practices for environmentally responsible LLM training. The open-source release of our framework, benchmarks, and carbon intensity datasets will lower barriers for researchers and practitioners to adopt carbon-aware optimization in their workflows.