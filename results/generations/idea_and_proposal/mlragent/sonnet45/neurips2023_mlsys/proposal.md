# Carbon-Aware Dynamic Resource Allocation for LLM Training via Multi-Objective Reinforcement Learning

## 1. Introduction

### Background

The exponential growth of Large Language Models (LLMs) has transformed artificial intelligence capabilities, but at a significant environmental cost. Training state-of-the-art models like GPT-4 or PaLM requires thousands of GPU/TPU accelerators operating continuously for weeks or months, consuming megawatt-hours of electricity and generating substantial carbon emissions. Recent estimates suggest that training a single large-scale LLM can emit as much CO₂ as several transatlantic flights, with the AI industry's aggregate carbon footprint growing at an alarming rate.

Current distributed training systems optimize primarily for computational efficiency and cost, treating energy as a uniform resource with fixed environmental impact. However, electrical grid carbon intensity varies dramatically across time and geography—fluctuating by factors of 5-10x within a single day depending on renewable energy availability, demand patterns, and generation mix. During high renewable generation periods (e.g., sunny afternoons with abundant solar power), the carbon cost of computation drops significantly, while fossil fuel-heavy periods carry much higher environmental burdens.

Existing carbon-aware computing approaches employ simple heuristics: delaying batch jobs to low-carbon periods, geographic load balancing, or crude pause-resume mechanisms. These methods fail to address the complex constraints of distributed LLM training, where: (1) strict synchronization requirements across thousands of devices create communication bottlenecks, (2) gradient staleness affects convergence quality, (3) checkpoint/restart overhead is substantial, and (4) training deadlines impose hard constraints. The literature reveals critical gaps: while LUCA demonstrates carbon-aware job scheduling in manufacturing and SLA-MORL optimizes HPC resource allocation, no existing work addresses the unique challenges of carbon-aware optimization for large-scale, distributed LLM training with its intricate parallelism strategies and stringent performance requirements.

### Research Objectives

This research proposes a novel **Multi-Objective Reinforcement Learning framework for Carbon-Aware Dynamic Resource Allocation (MORL-CADRA)** that intelligently manages distributed LLM training to minimize carbon emissions while maintaining training efficiency. Our specific objectives are:

1. **Design a comprehensive multi-objective RL framework** that balances four competing objectives: training throughput, model convergence quality, deadline adherence, and carbon footprint reduction.

2. **Develop adaptive action spaces** encompassing dynamic batch size adjustment, cross-region workload migration, parallelism strategy modulation (data/pipeline/tensor parallelism), and intelligent task scheduling during carbon intensity fluctuations.

3. **Create a realistic simulation environment** integrating historical carbon intensity data from multiple grid regions, accurate distributed training dynamics, and communication overhead modeling for reproducible benchmarking.

4. **Demonstrate substantial carbon reductions** (target: 20-40%) with minimal training time overhead (<5%) across diverse LLM architectures and training scenarios.

5. **Establish open benchmarks and datasets** for carbon-aware ML systems optimization, facilitating reproducible research in this emerging domain.

### Significance

This research addresses a critical intersection of machine learning, systems optimization, and environmental sustainability—directly aligned with the ML for Systems workshop's emphasis on LLM training challenges and compute sustainability. The significance spans multiple dimensions:

**Environmental Impact**: With AI training's carbon footprint projected to grow exponentially, even modest percentage reductions translate to thousands of tons of avoided CO₂ emissions annually across the industry.

**Economic Value**: Carbon-aware optimization can reduce operational costs through strategic use of cheaper renewable energy periods and improved resource efficiency.

**Scientific Advancement**: This work pioneers the application of multi-objective RL to carbon-aware systems optimization, establishing methodological foundations for a critical emerging research area.

**Policy Relevance**: As regulatory frameworks increasingly require carbon accounting and reduction, our framework provides actionable mechanisms for AI organizations to meet sustainability commitments without sacrificing innovation velocity.

## 2. Methodology

### 2.1 Problem Formulation

We formulate carbon-aware LLM training as a **Constrained Multi-Objective Markov Decision Process (CMO-MDP)** defined by the tuple $\langle \mathcal{S}, \mathcal{A}, \mathcal{T}, \mathcal{R}, \gamma, \mathcal{C} \rangle$:

**State Space** $\mathcal{S}$: At timestep $t$, the state $s_t$ comprises:
- Carbon intensity vector: $\mathbf{c}_t = [c_t^1, c_t^2, ..., c_t^R] \in \mathbb{R}^R$ (gCO₂/kWh for $R$ regions)
- Predicted carbon trajectory: $\hat{\mathbf{c}}_{t:t+H} \in \mathbb{R}^{R \times H}$ (forecast horizon $H$)
- Training progress metrics: loss $L_t$, gradient norm $||\nabla_t||$, learning rate $\eta_t$
- Current resource allocation: $\mathbf{a}_{t-1}$ (previous action)
- Communication topology state: bandwidth utilization $\mathbf{b}_t$, latency $\boldsymbol{\tau}_t$
- Remaining time to deadline: $T_{rem} = T_{deadline} - t$

**Action Space** $\mathcal{A}$: The agent selects composite actions:

$$\mathbf{a}_t = \{\alpha_t, \mathbf{m}_t, \boldsymbol{\pi}_t, \delta_t\}$$

where:
- $\alpha_t \in [0.5, 2.0]$: batch size scaling factor
- $\mathbf{m}_t \in \{0,1\}^{N \times R}$: migration matrix assigning $N$ model partitions to $R$ regions
- $\boldsymbol{\pi}_t = (\pi_t^{data}, \pi_t^{pipeline}, \pi_t^{tensor})$: parallelism degree tuple
- $\delta_t \in \{0, 1\}$: binary pause/continue decision

**Transition Dynamics** $\mathcal{T}$: State transitions follow training system dynamics:

$$s_{t+1} = f(s_t, a_t, \xi_t)$$

where $\xi_t$ represents stochastic elements (actual carbon intensity realizations, network variability, hardware failures).

**Multi-Objective Reward** $\mathcal{R}$: We define a vector reward:

$$\mathbf{r}_t = [r_t^{throughput}, r_t^{quality}, r_t^{carbon}, r_t^{deadline}]^T$$

with components:

1. **Throughput reward**: 
$$r_t^{throughput} = \frac{\text{tokens\_processed}_t}{\text{baseline\_throughput}}$$

2. **Quality reward** (penalizes convergence degradation):
$$r_t^{quality} = -\lambda_q \cdot \max(0, L_t - L_t^{expected})$$

3. **Carbon reward** (negative emissions):
$$r_t^{carbon} = -\sum_{i=1}^{N} P_i \cdot c_{region(i),t} \cdot \Delta t$$

where $P_i$ is power consumption of partition $i$, $region(i)$ maps partition to region.

4. **Deadline adherence reward**:
$$r_t^{deadline} = -\lambda_d \cdot \max(0, \frac{T_{rem}^{expected} - T_{rem}}{T_{total}})$$

**Constraints** $\mathcal{C}$:
- Total resource budget: $\sum_{i,r} m_{i,r,t} \leq N_{max}$
- Migration frequency limit: $||\mathbf{m}_t - \mathbf{m}_{t-1}||_0 \leq M_{max}$ (max migrations per step)
- Convergence guarantee: $P(L_{final} \leq L_{target}) \geq 1 - \epsilon$

### 2.2 Multi-Objective RL Framework

We employ **Pareto-Conditioned Networks (PCN)** combined with **Multi-Objective Proximal Policy Optimization (MOPPO)** to handle the multi-objective optimization:

**Policy Architecture**: The policy network $\pi_\theta(a|s, \mathbf{w})$ is conditioned on preference vector $\mathbf{w} \in \Delta^{K-1}$ (simplex over $K=4$ objectives):

$$\pi_\theta(\mathbf{a}_t | s_t, \mathbf{w}) = \text{Softmax}(\text{MLP}([s_t; \mathbf{w}]))$$

The network architecture consists of:
- State encoder: Multi-head attention over temporal carbon intensity sequences
- Cross-attention between carbon forecasts and training state
- Separate decoder heads for each action component
- Value network: $V_\phi(s_t, \mathbf{w}) \rightarrow \mathbb{R}^K$ estimating expected returns for each objective

**Training Algorithm**:

1. **Data Collection**: Collect trajectories using current policy $\pi_{\theta_{old}}$ with diverse preference vectors $\mathbf{w} \sim \text{Dirichlet}(\alpha)$

2. **Pareto Front Approximation**: Maintain archive $\mathcal{A}$ of non-dominated solutions

3. **MOPPO Update**: For each objective $k$:

$$\mathcal{L}_k(\theta) = \mathbb{E}_t \left[ \min \left( \frac{\pi_\theta}{\pi_{\theta_{old}}} \hat{A}_t^k, \text{clip}\left(\frac{\pi_\theta}{\pi_{\theta_{old}}}, 1-\epsilon, 1+\epsilon\right) \hat{A}_t^k \right) \right]$$

where $\hat{A}_t^k$ is the advantage estimate for objective $k$.

4. **Scalarization**: Aggregate losses using dynamic weights:

$$\mathcal{L}_{total} = \sum_{k=1}^K w_k \mathcal{L}_k - \beta H(\pi_\theta)$$

with entropy bonus $H(\pi_\theta)$ for exploration.

5. **Adaptive Weight Adjustment**: Update $\mathbf{w}$ based on Pareto front coverage and constraint violations.

### 2.3 Carbon Intensity Prediction Module

Accurate carbon forecasting is critical. We implement a **hierarchical temporal fusion transformer**:

$$\hat{\mathbf{c}}_{t:t+H} = \text{TFT}(\mathbf{c}_{t-W:t}, \mathbf{x}_t^{exog})$$

where $\mathbf{x}_t^{exog}$ includes exogenous features: time-of-day, weather forecasts, historical renewable generation patterns. The model is pre-trained on two years of historical data from EIA and ElectricityMaps APIs covering major datacenter regions (US-East, US-West, EU-West, Asia-Pacific).

### 2.4 Distributed Training Simulator

To enable reproducible research without requiring actual large-scale infrastructure, we develop **CarbonSim-LLM**, a high-fidelity simulator modeling:

**Communication Patterns**: Implement collective communication primitives (AllReduce, AllGather) with realistic bandwidth/latency models:

$$T_{comm} = \alpha + \beta \cdot \text{message\_size} + \gamma \cdot \text{num\_devices}$$

**Parallelism Strategies**: Support data, pipeline, and tensor parallelism with accurate memory and compute modeling based on Megatron-LM specifications.

**Migration Overhead**: Model checkpoint serialization ($O(\text{model\_size})$), network transfer ($O(\text{model\_size} / \text{bandwidth})$), and deserialization costs.

**Carbon Accounting**: Integrate real-time power consumption models for A100/H100 GPUs under different utilization levels:

$$P_{GPU}(u) = P_{idle} + (P_{max} - P_{idle}) \cdot u^{1.3}$$

where $u$ is utilization and the exponent captures superlinear power scaling.

### 2.5 Experimental Design

**Baseline Methods**:
1. **Carbon-Agnostic**: Standard distributed training (Megatron-LM defaults)
2. **Simple Pause-Resume**: Pause training when carbon intensity exceeds threshold
3. **Geographic Load Balancing**: Static allocation favoring low-carbon regions
4. **Rule-Based Scheduler**: Heuristic combining carbon intensity and utilization
5. **Single-Objective RL**: RL optimizing only carbon (no quality/throughput consideration)

**Training Scenarios**:
- **Small-scale**: GPT-2 (1.5B parameters) on 64 GPUs
- **Medium-scale**: GPT-3 variant (7B parameters) on 256 GPUs  
- **Large-scale**: LLaMA-style model (30B parameters) on 1024 GPUs

**Datacenter Configurations**:
- Multi-region: 4 datacenters (Virginia, Oregon, Ireland, Singapore)
- Carbon intensity profiles: Historical data (2022-2024) with 15-minute granularity
- Network topology: Realistic inter-region latencies (20-150ms) and bandwidth (10-100 Gbps)

**Evaluation Metrics**:

1. **Carbon Efficiency**: 
$$\eta_{carbon} = \frac{\text{CO}_2^{baseline} - \text{CO}_2^{MORL}}{\text{CO}_2^{baseline}} \times 100\%$$

2. **Training Time Overhead**: 
$$\Delta T = \frac{T_{MORL} - T_{baseline}}{T_{baseline}} \times 100\%$$

3. **Convergence Quality**: Final validation loss and perplexity

4. **Pareto Optimality**: Hypervolume indicator measuring Pareto front quality

5. **Deadline Success Rate**: Percentage of runs meeting deadline constraints

6. **Cost Efficiency**: Total energy cost considering time-of-use pricing

**Ablation Studies**:
- Impact of carbon forecast accuracy (perfect vs. realistic predictions)
- Effect of action space components (migration vs. batch scaling vs. parallelism adjustment)
- Sensitivity to preference weights and constraint thresholds
- Scalability analysis varying model size and cluster size

**Implementation**: 
- Framework: PyTorch with DeepSpeed/Megatron integration
- RL library: Custom MOPPO implementation extending Stable-Baselines3
- Simulation: CarbonSim-LLM in Python with GPU acceleration for rollouts
- Carbon data: Real-time APIs (ElectricityMaps, WattTime) + historical datasets

### 2.6 Reproducibility Provisions

To ensure reproducibility and enable community research:

1. **Open-source release**: Complete codebase, simulator, and trained models on GitHub
2. **Datasets**: Curated carbon intensity time series and training traces
3. **Benchmarks**: Standardized evaluation protocols and leaderboard infrastructure
4. **Documentation**: Detailed hyperparameters, architectural specifications, and training logs
5. **Containerization**: Docker images with complete environment configurations

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Results**: We anticipate demonstrating:
- **20-40% carbon emission reductions** compared to carbon-agnostic training across diverse scenarios
- **<5% training time overhead** in deadline-constrained settings, with potential time savings when deadlines are flexible
- **15-25% cost reductions** by exploiting temporal electricity price variations correlated with carbon intensity
- **Pareto front improvements** of 30-50% in hypervolume metric versus single-objective baselines
- **Robust performance** across geographic regions and seasonal carbon intensity patterns

**Qualitative Contributions**:

1. **Methodological Framework**: A principled multi-objective RL approach for carbon-aware systems optimization, applicable beyond LLM training to other large-scale ML workloads.

2. **Action Space Innovation**: Novel adaptive mechanisms (parallelism modulation, intelligent migration) that expand the solution space beyond simple scheduling heuristics.

3. **Simulation Infrastructure**: CarbonSim-LLM provides the community with a realistic testbed for reproducible research without requiring massive infrastructure.

4. **Benchmark Establishment**: Standardized evaluation protocols and datasets filling a critical gap in carbon-aware ML systems research.

**Insights and Analysis**:
- Characterization of carbon-throughput-quality tradeoff surfaces for different model architectures
- Identification of optimal migration strategies under varying carbon intensity volatility
- Quantification of forecast accuracy requirements for effective carbon-aware optimization
- Guidelines for practitioners on preference weight selection based on organizational priorities

### Impact

**Scientific Impact**: This research establishes foundational principles for carbon-aware ML systems, bridging reinforcement learning, distributed systems, and sustainability science. The multi-objective optimization framework advances RL methodology for complex systems problems with competing constraints. Expected publications span top-tier venues (NeurIPS, ICML, OSDI, EuroSys) and catalyze follow-on research in related domains (federated learning, edge computing, scientific computing).

**Industrial Impact**: Cloud providers (AWS, Google Cloud, Azure) and AI organizations (OpenAI, Anthropic, Meta) face mounting pressure to reduce carbon footprints. MORL-CADRA provides immediately deployable technology for achieving sustainability targets without compromising AI capability development. Preliminary industry partnerships for pilot deployments are underway, with potential for widespread adoption given compatibility with existing training frameworks.

**Environmental Impact**: If adopted at scale, this technology could prevent millions of tons of CO₂ emissions annually. A conservative estimate suggests that applying our methods to just 10% of large-scale AI training workloads could avoid ~500,000 tons CO₂/year—equivalent to removing 100,000 cars from roads. Beyond direct emission reductions, the framework incentivizes renewable energy utilization, potentially accelerating grid decarbonization through increased demand-side flexibility.

**Policy and Societal Impact**: As AI regulation evolves, frameworks like MORL-CADRA provide concrete mechanisms for implementing carbon accounting and reduction mandates. The work informs policy discussions on AI sustainability, offering evidence-based insights into feasible reduction targets. By demonstrating that environmental responsibility and AI progress are compatible rather than contradictory, this research supports broader societal acceptance of AI technology.

**Educational Impact**: The open-source release, comprehensive documentation, and reproducible benchmarks create valuable resources for education at the intersection of AI, systems, and sustainability. Course modules, tutorials, and workshop materials will train the next generation of researchers equipped to build environmentally conscious AI systems.

**Long-term Vision**: This research represents an initial step toward holistic sustainable AI systems that optimize not only carbon emissions but also water consumption, rare earth mineral usage, and broader environmental externalities. The multi-objective optimization framework provides a foundation for incorporating additional sustainability objectives as measurement and modeling capabilities mature. Ultimately, we envision AI systems that operate within planetary boundaries while delivering transformative societal benefits—a critical challenge for the coming decades.