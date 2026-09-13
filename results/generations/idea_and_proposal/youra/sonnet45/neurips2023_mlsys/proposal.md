# Research Proposal: LLM-Guided Reinforcement Learning for Production-Scale Compiler Partitioning in Distributed LLM Training

## 1. Title

**LLM-Guided Reinforcement Learning for Production-Scale Compiler Partitioning in Distributed LLM Training**

## 2. Introduction

### 2.1 Background

The training of large language models (LLMs) has become one of the most computationally intensive tasks in modern machine learning, often requiring thousands of GPUs and consuming millions of dollars per training run. A critical component of this infrastructure is the compiler partitioning strategy, which determines how computational graphs are distributed across devices using techniques such as data parallelism, tensor parallelism, pipeline parallelism, and their combinations (3D parallelism). Current state-of-the-art approaches rely primarily on hand-tuned heuristics (e.g., torchtitan) or search-based methods with limited generalization capabilities (e.g., Alpa).

The compiler partitioning problem for distributed LLM training involves mapping operations in a computational graph to specific devices while minimizing communication overhead, balancing memory constraints, and maximizing hardware utilization. This is fundamentally a combinatorial optimization problem with an exponentially large search space that grows with model size and device count. Traditional approaches face several critical limitations:

1. **Poor Generalization**: Hand-tuned strategies optimized for specific architectures (e.g., GPT-3) fail to transfer effectively to new models with different layer configurations, attention mechanisms, or parameter counts.

2. **Expensive Optimization**: Each new LLM training run requires manual tuning or exhaustive search, consuming valuable engineering time and computational resources.

3. **Environmental Impact**: Suboptimal partitioning strategies waste energy, contributing to the substantial carbon footprint of LLM training (estimated at 500+ tons CO₂ per major training run).

Recent advances in machine learning for systems have demonstrated the potential of reinforcement learning (RL) to learn optimization policies that generalize across problem instances. Simultaneously, the emergence of capable LLMs has opened new possibilities for incorporating domain knowledge through natural language guidance. However, applying these techniques to production-scale compiler partitioning (1000+ GPUs, 70B+ parameter models) remains an open challenge.

### 2.2 Research Objectives

This research proposes a novel two-phase approach that combines reinforcement learning with validated LLM-guided exploration to automate compiler partitioning for production-scale LLM training. Our primary objectives are:

**O1: Develop a Validated LLM-Guided RL Framework**
Design and implement a reinforcement learning system that leverages LLM knowledge about SPMD (Single Program Multiple Data) partitioning strategies, with pre-validation mechanisms to ensure reliability in production environments.

**O2: Achieve Production-Scale Performance Improvements**
Demonstrate >10% end-to-end training speedup compared to state-of-the-art baselines (torchtitan, Alpa) on hold-out test models spanning 70B-175B parameters trained on 1024+ GPUs.

**O3: Establish Generalization Capabilities**
Empirically characterize the learned policy's ability to transfer across diverse transformer architectures without requiring per-model retraining.

**O4: Quantify Economic and Environmental Impact**
Measure cost savings and carbon emission reductions achievable through deployment in production LLM training workflows.

### 2.3 Research Significance

This research addresses a critical gap at the intersection of ML for Systems and sustainable computing. The significance manifests across multiple dimensions:

**Scientific Contribution**: This work will provide the first empirical characterization of learned compiler partitioning generalization at production scale (1000+ GPUs), establishing theoretical bounds on cross-workload transfer learning for distributed systems optimization.

**Methodological Innovation**: The proposed two-phase validation approach—pre-validating LLM knowledge before deployment and conditionally incorporating LLM guidance—represents a novel paradigm for safely integrating large language models into critical systems infrastructure.

**Practical Impact**: With LLM training costs exceeding $10M per run for frontier models, even a 10% speedup translates to $1.2M savings per training run. Across the industry, this could save hundreds of millions of dollars annually while reducing carbon emissions by thousands of tons.

**Alignment with Workshop Goals**: This research directly addresses the workshop's call for work on "applying ML to systems issues that emerge from large-scale training" and "ML for compute sustainability," while advancing the broader goal of establishing best practices for ML for Systems.

## 3. Methodology

### 3.1 Problem Formulation

We formulate compiler partitioning as a Markov Decision Process (MDP) defined by the tuple $\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{P}, \mathcal{R}, \gamma)$:

**State Space** $\mathcal{S}$: Each state $s_t$ represents the current partitioning configuration, encoded as:
$$s_t = \{G_t, P_t, H, M_t\}$$
where:
- $G_t$ is the computational graph with $n$ operations
- $P_t$ is the current partial partitioning assignment
- $H$ represents hardware topology (GPU count, interconnect bandwidth)
- $M_t$ captures memory and communication constraints

**Action Space** $\mathcal{A}$: Following the PartIR framework, actions specify partitioning strategies for operations:
$$a_t = \{\text{strategy}_i, \text{device\_mesh}_i, \text{sharding\_spec}_i\}$$
where strategies include data parallel (DP), tensor parallel (TP), pipeline parallel (PP), and their compositions.

**Reward Function** $\mathcal{R}$: The reward combines multiple objectives:
$$r(s_t, a_t) = -\alpha \cdot T_{\text{exec}}(s_{t+1}) - \beta \cdot C_{\text{comm}}(s_{t+1}) - \lambda \cdot \mathbb{1}[\text{memory\_violation}]$$
where $T_{\text{exec}}$ is execution time, $C_{\text{comm}}$ is communication cost, and the indicator function penalizes memory constraint violations. Hyperparameters $\alpha, \beta, \lambda$ are tuned to prioritize end-to-end training time.

### 3.2 Two-Phase LLM-Guided RL Approach

#### Phase 1: LLM Knowledge Pre-Validation

Before incorporating LLM guidance, we validate its knowledge about SPMD partitioning through targeted prompting:

**Validation Protocol**:
1. Construct a benchmark set of 50 canonical partitioning problems with known optimal solutions
2. Query the LLM (GPT-4 or equivalent) with structured prompts:
   ```
   Given a transformer layer with parameters [specs], 
   running on [hardware topology], suggest an optimal 
   partitioning strategy considering [constraints].
   ```
3. Evaluate LLM suggestions against ground truth using metrics:
   - **Correctness**: Percentage of valid partitioning strategies
   - **Optimality Gap**: Performance difference from known optimal solutions
   - **Consistency**: Agreement across multiple prompts for the same problem

**Validation Threshold**: LLM guidance is enabled only if:
$$\text{Correctness} > 0.85 \text{ AND } \text{Optimality Gap} < 0.20$$

If validation fails, the system falls back to expert heuristics from torchtitan.

#### Phase 2: Conditional LLM-Guided RL Training

**Architecture**: We employ a Proximal Policy Optimization (PPO) agent with the following components:

**Policy Network** $\pi_\theta(a|s)$: A graph neural network (GNN) that processes the computational graph structure:
$$h_i^{(l+1)} = \text{ReLU}\left(W^{(l)} \cdot \text{AGGREGATE}\left(\{h_j^{(l)} : j \in \mathcal{N}(i)\}\right)\right)$$
where $h_i^{(l)}$ represents node embeddings at layer $l$, and $\mathcal{N}(i)$ denotes neighbors of operation $i$.

**Value Network** $V_\phi(s)$: Estimates expected cumulative reward from state $s$.

**LLM Guidance Integration**: When LLM validation succeeds, we incorporate guidance through reward shaping:
$$r'(s_t, a_t) = r(s_t, a_t) + \eta \cdot \text{LLM\_score}(s_t, a_t)$$
where:
$$\text{LLM\_score}(s_t, a_t) = \text{similarity}(a_t, a_{\text{LLM}}(s_t))$$
measures alignment between the RL action and LLM-suggested strategy, with $\eta$ controlling guidance strength (initially 0.1, annealed to 0 over training).

**Training Algorithm**:
```
Initialize policy π_θ and value network V_φ
for epoch = 1 to N_epochs:
    for model_config in training_set:
        Generate episode using π_θ
        Collect trajectory τ = {(s_t, a_t, r_t)}
        
        if LLM_validated:
            Augment rewards with LLM guidance
        
        Compute advantages: A_t = Σ γ^k r_{t+k} - V_φ(s_t)
        
        Update θ using PPO objective:
        L(θ) = E[min(ρ_t A_t, clip(ρ_t, 1-ε, 1+ε) A_t)]
        where ρ_t = π_θ(a_t|s_t) / π_θ_old(a_t|s_t)
        
        Update φ to minimize value loss
    
    Evaluate on validation set
    Adjust η (anneal LLM guidance)
```

### 3.3 Data Collection

**Training Dataset**: We construct a diverse set of 25 transformer architectures spanning:
- **Parameter Scales**: 70B, 100B, 130B, 175B parameters
- **Architecture Variants**: 
  - Standard GPT-style (decoder-only)
  - Llama-style (RoPE embeddings, SwiGLU activations)
  - PaLM-style (parallel attention/FFN)
- **Configuration Diversity**:
  - Hidden dimensions: 8192-16384
  - Attention heads: 64-128
  - Layers: 60-96
  - Sequence lengths: 2048-8192

**Test Dataset**: 10 hold-out architectures not seen during training, including:
- Emerging architectures (e.g., mixture-of-experts variants)
- Intermediate parameter counts (85B, 145B)
- Novel architectural features (e.g., grouped-query attention)

**Hardware Environment**: 
- Primary: 1024 NVIDIA H100 GPUs with NVLink and InfiniBand interconnect
- Secondary: 2048 GPU configuration for scalability testing
- Standardized topology to control for hardware variability

### 3.4 Experimental Design

#### Experiment 1: RL Convergence and Learning Dynamics (SH1)

**Objective**: Validate that LLM-guided RL can learn effective partitioning policies.

**Procedure**:
1. Train RL agent on 25 training models for 500 epochs
2. Track convergence metrics: policy loss, value loss, average reward
3. Compare learning curves: RL+LLM vs. Pure RL vs. Random initialization

**Success Criteria**: 
- Policy converges (reward plateau) within 400 epochs
- Final average reward >50% improvement over random baseline
- LLM-guided variant shows 20% faster convergence than pure RL

#### Experiment 2: Generalization Across Workloads (SH2)

**Objective**: Test policy generalization to unseen models.

**Procedure**:
1. Deploy trained policy on 10 test models (3 independent runs each, n=30)
2. Measure end-to-end training time for 1000 iterations
3. Compare against baseline partitioning strategies

**Metrics**:
- **Speedup**: $S = \frac{T_{\text{baseline}} - T_{\text{RL}}}{T_{\text{baseline}}} \times 100\%$
- **Generalization Gap**: Performance difference between training and test sets
- **Robustness**: Standard deviation across runs

**Statistical Test**: One-tailed paired t-test comparing RL speedup against 10% threshold (α=0.05, target power=0.80)

**Success Criteria**:
- Speedup >10% on >70% of test models (7/10)
- Mean speedup across all test models >12%
- Generalization gap <5%

#### Experiment 3: Comprehensive Baseline Comparison (SH3)

**Objective**: Demonstrate superiority over all existing approaches.

**Baselines**:
1. **torchtitan**: Hand-tuned 3D parallelism (industry standard)
2. **Alpa**: Heuristic-based automatic parallelism
3. **TePDist**: Tensor partitioning with dynamic programming
4. **Pure RL**: RL without LLM guidance
5. **Pure LLM**: Direct LLM suggestions without RL refinement

**Procedure**:
1. Run all methods on identical test set (10 models × 3 runs)
2. Measure: training time, memory efficiency, communication overhead
3. Conduct pairwise statistical comparisons

**Metrics**:
- **Primary**: End-to-end training speedup
- **Secondary**: 
  - Peak memory utilization
  - Communication volume (GB transferred)
  - GPU utilization percentage
  - Energy consumption (kWh)

**Statistical Analysis**:
- Friedman test for overall differences across methods
- Post-hoc Nemenyi test for pairwise comparisons
- Effect size calculation (Cohen's d, target >0.8)

**Success Criteria**:
- RL+LLM significantly outperforms all baselines (p<0.05)
- Mean speedup >10% over best baseline
- No significant degradation in secondary metrics

#### Experiment 4: Ablation Studies

**Components to Ablate**:
1. LLM guidance (compare with/without)
2. GNN architecture (vs. MLP policy network)
3. Reward shaping parameters (α, β, λ)
4. Training set size (10, 15, 20, 25 models)

**Analysis**: Quantify contribution of each component to final performance.

### 3.5 Evaluation Metrics

**Primary Metrics**:
- **Training Speedup**: Percentage reduction in end-to-end training time
- **Cost Savings**: Dollar amount saved per training run
- **Carbon Reduction**: Tons CO₂ equivalent avoided

**Secondary Metrics**:
- **Convergence Speed**: Epochs to reach 90% of final performance
- **Sample Efficiency**: Number of training models needed for generalization
- **Robustness**: Performance variance across runs
- **Scalability**: Performance on 2048 GPU configuration

**Computational Metrics**:
- **Training Cost**: GPU-hours required to train RL policy
- **Inference Latency**: Time to generate partitioning strategy
- **ROI**: Breakeven point (number of deployments to recover training cost)

### 3.6 Implementation Details

**Software Stack**:
- PyTorch 2.x with torchtitan integration
- Ray RLlib for distributed RL training
- PyTorch Geometric for GNN implementation
- OpenAI API for LLM guidance (GPT-4)

**Hyperparameters**:
- Learning rate: 3e-4 (policy), 1e-3 (value)
- PPO clip parameter: ε = 0.2
- Discount factor: γ = 0.99
- GAE parameter: λ = 0.95
- Batch size: 2048 transitions
- LLM guidance strength: η = 0.1 → 0 (linear annealing)

**Reproducibility**:
- Fixed random seeds across all experiments
- Containerized environment (Docker)
- Public release of code, trained models, and datasets
- Detailed logging of all hyperparameters and configurations

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome**: We expect the LLM-guided RL approach to achieve 12-15% average speedup on test models, exceeding the 10% target threshold. Based on preliminary analysis of the search space and baseline performance gaps, this improvement is achievable through:
1. Better tensor parallelism decisions for attention layers (5-7% gain)
2. Optimized pipeline stage boundaries (3-5% gain)
3. Reduced communication overhead through learned sharding strategies (2-3% gain)

**Generalization Characteristics**: We anticipate the learned policy will generalize effectively to architectures within the training distribution (similar parameter scales, standard transformer components) but may require fine-tuning for radically different architectures (e.g., state-space models, novel attention mechanisms).

**LLM Guidance Impact**: We expect LLM guidance to provide:
- 20-30% faster convergence during training
- 2-3% additional performance improvement over pure RL
- Improved sample efficiency (requiring 15-20 training models instead of 25 for comparable performance)

**Failure Modes**: The approach may underperform if:
- Test models have architectural features absent from training data
- Hardware topology differs significantly from training environment
- LLM validation fails, requiring fallback to expert heuristics

### 4.2 Scientific Impact

**Theoretical Contributions**:
1. **Generalization Bounds**: First empirical characterization of learned compiler partitioning generalization at production scale, establishing relationships between architectural similarity and policy transfer effectiveness.

2. **LLM Integration Framework**: Novel methodology for safely incorporating LLM knowledge into critical systems through pre-validation and conditional guidance, applicable beyond compiler optimization.

3. **Scaling Laws**: Empirical data on how RL policy performance scales with training set diversity, model size, and hardware configuration.

**Publications**: Expected outputs include:
- Primary venue: NeurIPS ML for Systems Workshop (2026)
- Extended version: MLSys Conference (2027)
- Systems venue: OSDI/SOSP (2027)

### 4.3 Practical Impact

**Economic Benefits**:
- **Per-Run Savings**: $1.2M for Llama-3-405B scale training (assuming 15% speedup, $8M baseline cost)
- **Industry-Wide Impact**: Potential savings of $500M+ annually across major AI labs
- **ROI**: 100× return after 100 production deployments; breakeven at 3 runs (assuming $40K training cost for RL policy)

**Environmental Benefits**:
- **Carbon Reduction**: ~500 tons CO₂ per major LLM training run
- **Energy Savings**: 15% reduction in GPU-hours translates to ~2.5M kWh per training run
- **Sustainability Metrics**: Contributes to corporate carbon neutrality goals

**Deployment Pathway**:
1. **Phase 1 (Months 1-6)**: Integration with torchtitan, internal testing at partner organizations
2. **Phase 2 (Months 7-12)**: Production deployment for 3-5 LLM training runs, performance monitoring
3. **Phase 3 (Months 13-18)**: Open-source release, community adoption, continuous improvement

### 4.4 Broader Impact

**Democratization of LLM Training**: By reducing optimization complexity, this work lowers barriers for academic institutions and smaller organizations to train large models efficiently.

**Sustainable AI**: Demonstrates concrete pathway for ML to address its own environmental footprint, aligning with growing emphasis on green computing.

**ML for Systems Methodology**: Establishes best practices for:
- Validating learned policies in production systems
- Combining symbolic knowledge (LLMs) with learned policies (RL)
- Measuring and reporting real-world impact of ML for Systems research

**Future Research Directions**: This work opens several promising avenues:
- Online RL adaptation during training runs
- Multi-objective optimization (cost, time, energy)
- Transfer learning across hardware platforms
- Extension to inference serving optimization

### 4.5 Risk Mitigation and Limitations

**Technical Risks**:
- **Mitigation**: Fallback to expert heuristics ensures no performance degradation
- **Validation**: Extensive testing on diverse workloads before production deployment

**Generalization Limitations**:
- **Acknowledged**: Policy may not generalize to non-transformer architectures
- **Future Work**: Expanding training set to include diverse model families

**Reproducibility Challenges**:
- **Addressed**: Public release of code, models, and comprehensive documentation
- **Infrastructure**: Collaboration with cloud providers for community access to large-scale GPU clusters

**Ethical Considerations**:
- **Energy Transparency**: Full reporting of training costs and carbon footprint
- **Dual Use**: Improved efficiency could enable both beneficial and harmful applications of LLMs
- **Access**: Commitment to open-source release to prevent concentration of optimization capabilities

This research represents a significant step toward sustainable, efficient, and automated optimization of large-scale AI infrastructure, directly addressing critical challenges at the intersection of machine learning and systems.