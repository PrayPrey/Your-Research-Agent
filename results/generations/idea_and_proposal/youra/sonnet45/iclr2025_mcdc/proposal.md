# Research Proposal: LoRA-MoE Framework for Collaborative Deep Learning

## 1. Title

**Scaling Mixture-of-Experts to 100+ Specialists via Hierarchical LoRA Routing: A Framework for Collaborative and Continual Deep Learning**

---

## 2. Introduction

### 2.1 Background

The contemporary paradigm of deep learning has been dominated by the "bigger is better" philosophy, where model performance scales with increasing model size and training data. However, this approach faces critical sustainability challenges. Large-scale models like GPT-4 and PaLM require enormous computational resources for training, and when these models become deprecated, they are typically discarded entirely in favor of new models trained from scratch. This practice represents a fundamental inefficiency in the machine learning development lifecycle.

This monolithic approach contrasts sharply with established principles in software engineering, where modularity enables code reusability, collaborative development, and incremental improvements. In software systems, developers routinely import and integrate independently-developed modules, allowing teams to build upon existing work rather than reinventing solutions. Similarly, biological systems demonstrate the advantages of modularity through functional specialization, enabling rapid adaptation and resilience to environmental changes.

Despite these compelling precedents, machine learning models remain largely monolithic black-box systems where functionalities are entangled within billions of parameters. Any attempt to modify specific capabilities risks catastrophic forgetting or unpredictable performance degradation across the entire model. This architectural rigidity prevents collaborative development scenarios where multiple independent teams could contribute specialized components to a unified system.

Recent advances in two distinct research directions offer potential solutions to this challenge. First, Mixture-of-Experts (MoE) architectures have demonstrated that sparse activation of specialized sub-networks can achieve competitive performance while reducing computational costs. Models like Switch Transformer and GLaM employ 8-64 expert modules, routing inputs to relevant specialists based on learned gating mechanisms. Second, Parameter-Efficient Fine-Tuning (PEFT) methods, particularly Low-Rank Adaptation (LoRA), have shown that task-specific adaptations can be captured in lightweight low-rank matrices, enabling efficient specialization without full model retraining.

However, these paradigms have remained largely separate. Standard MoE architectures use heavy feed-forward network (FFN) experts, limiting scalability to dozens of experts due to parameter overhead. Meanwhile, PEFT methods typically operate in single-task or sequential multi-task settings, lacking mechanisms for dynamic expert selection across hundreds of specialized modules.

### 2.2 Research Gap

The critical gap lies in enabling **collaborative, decentralized development of large-scale models** where hundreds of independent teams can contribute specialized components that compose into unified systems without centralized coordination or catastrophic forgetting. Existing approaches face three fundamental limitations:

1. **Limited Expert Scalability**: Standard MoE architectures with FFN experts cannot scale beyond 64 experts due to prohibitive parameter costs (each expert contains millions of parameters).

2. **Lack of Collaborative Training Mechanisms**: Current training paradigms require centralized data access and coordinated training, preventing scenarios where teams train specialists independently on proprietary or domain-specific data.

3. **Catastrophic Forgetting in Continual Learning**: Adding new capabilities to existing models typically requires full retraining or sophisticated regularization techniques that still risk performance degradation on previous tasks.

### 2.3 Research Objectives

This research proposes **LoRA-MoE**, the first framework that unifies PEFT and MoE paradigms by treating independently-trained LoRA adapters as lightweight expert specialists in a hierarchical Mixture-of-Experts architecture. The primary objectives are:

**O1. Extreme Expert Scaling**: Demonstrate that LoRA's parameter efficiency enables scaling to 100-1000 experts (10-100× more than standard MoE) while maintaining comparable task performance and reducing active parameter count by 10-100×.

**O2. Hierarchical Routing for Lightweight Experts**: Develop a two-level routing mechanism that exploits LoRA's rank-space structure to efficiently select relevant experts from large pools, reducing router complexity from $O(d \times N)$ to $O(d \times G + d \times K \times N/G)$ where $G$ is the number of task-family groups.

**O3. Collaborative Development Protocol**: Establish a training pipeline enabling independent teams to train domain-specific LoRA experts in parallel (Phase 1), followed by centralized router training (Phase 2), supporting decentralized collaborative model development.

**O4. Continual Learning via Expert Addition**: Validate that new experts can be added to the system without retraining existing components, mitigating catastrophic forgetting through architectural modularity.

### 2.4 Research Hypothesis

**Main Hypothesis**: Treating independently-trained LoRA (Low-Rank Adaptation) adapters as lightweight expert specialists in a hierarchical Mixture-of-Experts architecture enables scaling to 100+ experts with comparable task performance to standard FFN-based MoE while significantly reducing active parameter count (by 10-100×) and computational cost.

**Testable Predictions**:

- **P1 (Performance-Efficiency Trade-off)**: LoRA-MoE with N=100 experts (rank r=16, top-K=4) will achieve active parameter count <10% of 8-expert FFN-MoE baseline AND MMLU accuracy within ±2% of FFN-MoE baseline.

- **P2 (Hierarchical Routing Efficiency)**: Hierarchical routing (2-level: 10 task-family groups → top-4 experts) will reduce router FLOPs by ≥60% compared to flat routing AND maintain expert diversity with utilization >80%.

- **P3 (Load Balancing Effectiveness)**: Load balancing auxiliary loss with λ=0.01 will achieve expert utilization rate >80% (≥80/100 experts activated >1% of validation samples) AND task performance degradation <1% versus no load balancing.

### 2.5 Significance

This research addresses core challenges identified in the ICLR 2025 Workshop on Modularity for Collaborative, Decentralized, and Continual Deep Learning:

**Theoretical Significance**: The work provides the first unified framework bridging PEFT and MoE paradigms, establishing theoretical foundations for capacity scaling laws in lightweight expert systems and formalizing routing mechanisms in low-rank parameter subspaces.

**Methodological Significance**: The hierarchical LoRA-aware routing algorithm and independent expert training protocol offer novel solutions for collaborative model development, enabling distributed teams to contribute specialized components without centralized coordination.

**Practical Significance**: By enabling 100-1000 expert scaling with minimal parameter overhead, LoRA-MoE supports:
- **Sustainable Model Evolution**: Incremental capability addition without full retraining
- **Collaborative Development**: Multi-team contributions to unified models
- **Continual Learning**: Architectural mitigation of catastrophic forgetting
- **Resource Efficiency**: 10-100× reduction in active parameters compared to standard MoE

The framework directly addresses the workshop's emphasis on model recycling, upcycling, and collaborative training, offering a practical pathway toward more sustainable and modular deep learning systems.

---

## 3. Methodology

### 3.1 Overall Framework Architecture

The LoRA-MoE framework consists of three primary components: (1) a base pre-trained language model, (2) a pool of independently-trained LoRA expert modules, and (3) a hierarchical routing mechanism. The architecture operates by dynamically selecting and activating a sparse subset of experts for each input token, combining their outputs with the base model's representations.

**Mathematical Formulation**: For an input token representation $\mathbf{h} \in \mathbb{R}^d$ at layer $l$, the LoRA-MoE transformation is:

$$\mathbf{h}' = \mathbf{h} + \sum_{i=1}^{K} w_i \cdot \text{LoRA}_i(\mathbf{h})$$

where $K$ is the number of activated experts (top-K selection), $w_i$ are routing weights from the gating network, and $\text{LoRA}_i(\mathbf{h})$ represents the $i$-th expert's transformation:

$$\text{LoRA}_i(\mathbf{h}) = \mathbf{B}_i \mathbf{A}_i \mathbf{h}$$

with $\mathbf{A}_i \in \mathbb{R}^{r \times d}$ and $\mathbf{B}_i \in \mathbb{R}^{d \times r}$ being low-rank matrices where $r \ll d$ (typically $r=16$, $d=4096$).

### 3.2 Phase 1: Independent Expert Training

**Objective**: Train N=100 task-specific LoRA experts independently on diverse domains without coordination.

**Data Collection**:
- **Dataset**: FLAN (Fine-tuned Language Net) task mixture containing 1,836 tasks across 473 datasets
- **Task Sampling**: Select 100 diverse tasks spanning categories: question answering, sentiment analysis, natural language inference, summarization, translation, commonsense reasoning
- **Task Distribution**: Ensure balanced coverage across task families (10 families × 10 tasks each)
- **Data Volume**: 50,000 training examples per task (5M total examples)

**Training Protocol**:
1. **Base Model**: Initialize from pre-trained LLaMA-2 7B model
2. **LoRA Configuration**: 
   - Rank: $r \in \{8, 16, 32\}$ (primary experiments use $r=16$)
   - Target modules: Query and Value projection matrices in all attention layers
   - Scaling factor: $\alpha = 32$
3. **Optimization**:
   - Optimizer: AdamW with $\beta_1=0.9$, $\beta_2=0.999$
   - Learning rate: $3 \times 10^{-4}$ with cosine decay
   - Batch size: 128 examples per task
   - Training steps: 10,000 steps per expert
   - Gradient clipping: max norm = 1.0
4. **Parallelization**: All 100 experts trained simultaneously on separate GPU clusters (no inter-expert communication)

**Expert Diversity Validation**: After training, compute pairwise expert similarity to verify specialization:

$$\text{Similarity}(i, j) = \frac{\langle \text{vec}(\mathbf{B}_i\mathbf{A}_i), \text{vec}(\mathbf{B}_j\mathbf{A}_j) \rangle}{\|\text{vec}(\mathbf{B}_i\mathbf{A}_i)\| \|\text{vec}(\mathbf{B}_j\mathbf{A}_j)\|}$$

**Success Criterion**: >70% of expert pairs should have cosine similarity <0.3, indicating diverse specializations.

### 3.3 Phase 2: Hierarchical Router Training

**Objective**: Learn a two-level routing mechanism that selects relevant experts from the pool of 100 specialists.

**Architecture Design**:

**Level 1 (Task-Family Router)**: Coarse-grained selection of expert groups
- **Input**: Token representation $\mathbf{h} \in \mathbb{R}^d$
- **Grouping**: 100 experts organized into G=10 task-family groups (10 experts per group)
- **Gating Network**: 
  $$\mathbf{g}_{\text{group}} = \text{Softmax}(\mathbf{W}_{\text{group}} \mathbf{h} + \mathbf{b}_{\text{group}})$$
  where $\mathbf{W}_{\text{group}} \in \mathbb{R}^{G \times d}$
- **Selection**: Choose top-M=4 groups with highest gating scores

**Level 2 (Expert Router)**: Fine-grained selection within chosen groups
- **Input**: Concatenation of $\mathbf{h}$ and rank-space projection features
- **Rank-Space Features**: For each expert $i$, compute:
  $$\mathbf{f}_i = [\mathbf{U}_i^T \mathbf{h}; \mathbf{V}_i^T \mathbf{h}]$$
  where $\mathbf{U}_i, \mathbf{V}_i$ are left/right singular vectors from SVD of $\mathbf{B}_i\mathbf{A}_i$
- **Gating Network** (per group):
  $$\mathbf{g}_{\text{expert}}^{(m)} = \text{Softmax}(\mathbf{W}_{\text{expert}}^{(m)} [\mathbf{h}; \mathbf{f}_i] + \mathbf{b}_{\text{expert}}^{(m)})$$
- **Selection**: Choose top-K=4 experts across all selected groups

**Training Data**:
- **Mixed-Task Dataset**: Sample 10M tokens uniformly from all 100 task datasets
- **Batch Composition**: Each batch contains examples from 8-12 different tasks
- **Sequence Length**: 512 tokens per example

**Loss Function**:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \lambda_1 \mathcal{L}_{\text{group-balance}} + \lambda_2 \mathcal{L}_{\text{expert-balance}}$$

where:

**Task Loss** (standard language modeling):
$$\mathcal{L}_{\text{task}} = -\sum_{t=1}^{T} \log P(x_t | x_{<t})$$

**Group-Level Load Balancing**:
$$\mathcal{L}_{\text{group-balance}} = G \cdot \sum_{g=1}^{G} f_g \cdot P_g$$

where $f_g$ is the fraction of tokens routed to group $g$ and $P_g$ is the average gating probability for group $g$.

**Expert-Level Load Balancing**:
$$\mathcal{L}_{\text{expert-balance}} = N \cdot \sum_{i=1}^{N} f_i \cdot P_i$$

**Hyperparameters**: $\lambda_1 = 0.01$, $\lambda_2 = 0.01$ (tuned via validation performance)

**Optimization**:
- Freeze all LoRA expert parameters ($\mathbf{A}_i, \mathbf{B}_i$)
- Train only router parameters ($\mathbf{W}_{\text{group}}, \mathbf{W}_{\text{expert}}$)
- Optimizer: AdamW with learning rate $1 \times 10^{-4}$
- Training steps: 50,000 steps
- Hardware: 8× A100 80GB GPUs

### 3.4 Phase 3: Optional End-to-End Fine-Tuning

**Objective**: Jointly optimize router and expert parameters for improved coordination.

**Protocol**:
1. Initialize from Phase 2 checkpoint (trained router + frozen experts)
2. Unfreeze all parameters (router + all LoRA experts)
3. Train with reduced learning rate: $1 \times 10^{-5}$ for 10,000 steps
4. Use same loss function as Phase 2

**Computational Cost**: ~30% of Phase 2 cost due to shorter training duration

### 3.5 Baseline Implementations

**Baseline 1: Standard FFN-MoE**
- **Architecture**: 8 expert FFN modules (4096 → 16384 → 4096 dimensions)
- **Routing**: Top-2 expert selection with standard load balancing
- **Training**: End-to-end training on mixed-task dataset (10M tokens)
- **Active Parameters**: Base (7B) + 2×FFN experts ≈ 7.537B per forward pass

**Baseline 2: Dense Fine-Tuned Model**
- **Architecture**: Single LLaMA-2 7B with full parameter fine-tuning
- **Training**: Mixed-task dataset (10M tokens)
- **Active Parameters**: 7B (all parameters active)

**Baseline 3: Flat LoRA-MoE (Ablation)**
- **Architecture**: Same 100 LoRA experts as main model
- **Routing**: Single-level top-K=4 selection (no hierarchical grouping)
- **Purpose**: Isolate hierarchical routing contribution

### 3.6 Experimental Design

**3.6.1 Factorial Design**

**Factors**:
- **Factor 1 (Architecture)**: LoRA-MoE, FFN-MoE, Dense (3 levels)
- **Factor 2 (Routing)**: Hierarchical, Flat (2 levels, applies only to LoRA-MoE)
- **Factor 3 (LoRA Rank)**: r ∈ {8, 16, 32} (3 levels, applies only to LoRA-MoE)

**Conditions**: 3 (architectures) × 2 (routing for LoRA-MoE) × 3 (ranks) + 2 (baselines) = 11 total conditions

**Replication**: 3 independent training runs per condition with different random seeds

**3.6.2 Evaluation Benchmarks**

**Primary Benchmark: MMLU (Massive Multitask Language Understanding)**
- **Tasks**: 57 subjects across STEM, humanities, social sciences
- **Format**: 5-shot multiple choice
- **Metrics**: Accuracy per subject, macro-average across subjects
- **Sample Size**: 14,042 test examples total

**Secondary Benchmark: BigBench-Hard**
- **Tasks**: 23 challenging tasks from BIG-Bench
- **Format**: Zero-shot and few-shot (task-dependent)
- **Metrics**: Task-specific metrics (accuracy, exact match, F1)
- **Sample Size**: ~8,000 test examples total

**Tertiary Benchmark: FLAN Held-Out Tasks**
- **Tasks**: 20 tasks from FLAN not used in expert training
- **Purpose**: Evaluate generalization to unseen task types
- **Format**: Task-specific (QA, classification, generation)

**3.6.3 Evaluation Metrics**

**Performance Metrics**:
1. **Task Accuracy**: Percentage of correct predictions per benchmark
2. **Macro-Average Accuracy**: Unweighted mean across all tasks
3. **Performance Gap**: $\Delta = \text{Acc}_{\text{LoRA-MoE}} - \text{Acc}_{\text{FFN-MoE}}$

**Efficiency Metrics**:
1. **Active Parameter Count**: 
   $$P_{\text{active}} = P_{\text{base}} + K \times (2 \times d \times r)$$
   for LoRA-MoE with rank $r$ and top-K selection
   
2. **Active Parameter Ratio**: 
   $$R_{\text{param}} = \frac{P_{\text{active}}^{\text{LoRA-MoE}}}{P_{\text{active}}^{\text{FFN-MoE}}}$$
   
3. **Inference Latency**: Tokens processed per second on A100 GPU
4. **FLOPs per Token**: Floating-point operations for forward pass

**Routing Metrics**:
1. **Expert Utilization Rate**: 
   $$U = \frac{1}{N} \sum_{i=1}^{N} \mathbb{1}[f_i > 0.01]$$
   where $f_i$ is fraction of validation tokens routed to expert $i$
   
2. **Load Balance Factor**: 
   $$B = \frac{N \cdot \max_i f_i}{\sum_i f_i}$$
   (ideal value = 1.0, higher indicates imbalance)
   
3. **Router FLOPs**: Computational cost of routing decision
   - Hierarchical: $d \times G + d \times K \times (N/G)$
   - Flat: $d \times N$

**Diversity Metrics**:
1. **Inter-Expert Similarity**: Pairwise cosine similarity of expert weight matrices
2. **Task-Expert Affinity**: Correlation between task categories and expert activation patterns

### 3.7 Statistical Analysis Plan

**3.7.1 Hypothesis Testing**

**Test 1: Performance Equivalence**
- **Null Hypothesis**: $H_0: |\mu_{\text{LoRA-MoE}} - \mu_{\text{FFN-MoE}}| \geq 2\%$ (performance gap ≥2%)
- **Alternative**: $H_1: |\mu_{\text{LoRA-MoE}} - \mu_{\text{FFN-MoE}}| < 2\%$ (performance within ±2%)
- **Test**: Two one-sided tests (TOST) for equivalence
- **Significance Level**: α = 0.05
- **Power**: 0.8 (based on N=3 runs, expected SD=1.2% from pilot studies)

**Test 2: Parameter Efficiency**
- **Null Hypothesis**: $H_0: R_{\text{param}} \geq 0.5$ (active parameter ratio ≥50%)
- **Alternative**: $H_1: R_{\text{param}} < 0.1$ (active parameter ratio <10%)
- **Test**: One-sample t-test (one-tailed)
- **Significance Level**: α = 0.0167 (Bonferroni correction for 3 tests)

**Test 3: Expert Utilization**
- **Null Hypothesis**: $H_0: U \leq 0.6$ (utilization ≤60%)
- **Alternative**: $H_1: U > 0.8$ (utilization >80%)
- **Test**: One-sample proportion test
- **Significance Level**: α = 0.0167

**3.7.2 Ablation Studies**

**Ablation 1: Hierarchical vs. Flat Routing**
- **Comparison**: LoRA-MoE (hierarchical) vs. LoRA-MoE (flat)
- **Metrics**: Accuracy, router FLOPs, expert utilization
- **Analysis**: Paired t-test across 57 MMLU tasks

**Ablation 2: LoRA Rank Sensitivity**
- **Comparison**: r ∈ {8, 16, 32}
- **Metrics**: Accuracy, active parameters, training time
- **Analysis**: One-way ANOVA with post-hoc Tukey HSD

**Ablation 3: Load Balancing Weight**
- **Comparison**: λ ∈ {0, 0.001, 0.01, 0.1}
- **Metrics**: Accuracy, expert utilization, load balance factor
- **Analysis**: Regression analysis (λ vs. metrics)

**Ablation 4: Top-K Selection**
- **Comparison**: K ∈ {1, 2, 4, 8}
- **Metrics**: Accuracy, active parameters, latency
- **Analysis**: Pareto frontier analysis (accuracy vs. efficiency)

**Ablation 5: Rank-Space Features**
- **Comparison**: Router with vs. without rank-space projection features
- **Metrics**: Accuracy, routing quality (measured by expert-task affinity)
- **Analysis**: Paired t-test

**3.7.3 Scaling Analysis**

**Expert Count Scaling**: Train LoRA-MoE variants with N ∈ {25, 50, 100, 200} experts
- **Hypothesis**: Performance scales logarithmically with expert count
- **Analysis**: Fit scaling law $\text{Acc}(N) = a - b \cdot N^{-c}$ via least-squares regression

**Computational Scaling**: Measure training time and inference latency vs. N
- **Analysis**: Linear regression of log(time) vs. log(N)

### 3.8 Continual Learning Experiment

**Objective**: Validate expert addition without catastrophic forgetting

**Protocol**:
1. **Initial Training**: Train LoRA-MoE with 80 experts on 80 tasks
2. **Evaluation**: Measure accuracy on all 80 tasks (baseline performance)
3. **Expert Addition**: Train 20 new LoRA experts on 20 new tasks independently
4. **Router Update**: Add new experts to pool, retrain router only (freeze all 100 experts)
5. **Evaluation**: Measure accuracy on:
   - Original 80 tasks (test for forgetting)
   - New 20 tasks (test for new capability acquisition)
   - Mixed evaluation (overall performance)

**Metrics**:
- **Backward Transfer**: $\text{BWT} = \frac{1}{80} \sum_{i=1}^{80} (\text{Acc}_i^{\text{after}} - \text{Acc}_i^{\text{before}})$
- **Forward Transfer**: $\text{FWT} = \frac{1}{20} \sum_{j=1}^{20} \text{Acc}_j^{\text{new}}$
- **Forgetting**: $F = \max(0, -\text{BWT})$

**Success Criterion**: BWT > -1% (minimal forgetting) AND FWT > 60% (effective new task learning)

### 3.9 Computational Resources

**Training Infrastructure**:
- **Phase 1 (Expert Training)**: 100 experts × 8 A100 GPUs × 12 hours = 9,600 GPU-hours
- **Phase 2 (Router Training)**: 8 A100 GPUs × 48 hours = 384 GPU-hours
- **Phase 3 (Fine-Tuning)**: 8 A100 GPUs × 12 hours = 96 GPU-hours
- **Total**: ~10,080 GPU-hours (~$30,000 at cloud pricing)

**Baseline Training**:
- **FFN-MoE**: 8 A100 GPUs × 72 hours = 576 GPU-hours
- **Dense Model**: 8 A100 GPUs × 48 hours = 384 GPU-hours

**Evaluation**: 1 A100 GPU × 24 hours per model = 264 GPU-hours total

**Storage**: ~500GB for model checkpoints, ~2TB for training data

---

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**4.1.1 Primary Outcomes**

**Outcome 1: Validated Extreme Expert Scaling**
We expect to demonstrate that LoRA-MoE with 100 experts (rank r=16, top-K=4) achieves:
- **Performance**: MMLU accuracy of 63-65% (within ±2% of FFN-MoE baseline at ~65%)
- **Efficiency**: Active parameter count of ~7.005B (vs. ~7.537B for FFN-MoE), representing 93% reduction in expert parameters
- **Utilization**: >80% of experts activated across validation set, indicating effective specialization without collapse

This outcome validates the core hypothesis that LoRA's parameter efficiency enables 10-100× expert scaling while maintaining competitive performance through diversity-via-quantity compensation.

**Outcome 2: Hierarchical Routing Efficiency**
We expect hierarchical routing to demonstrate:
- **Computational Savings**: 60-70% reduction in router FLOPs compared to flat routing (from $O(d \times N)$ to $O(d \times G + d \times K \times N/G)$)
- **Maintained Performance**: <1% accuracy degradation compared to flat routing
- **Improved Interpretability**: Clear task-family groupings in Level 1 routing patterns

This outcome establishes that hierarchical decomposition effectively manages routing complexity at scale.

**Outcome 3: Collaborative Training Viability**
The independent expert training protocol (Phase 1) is expected to produce:
- **Diverse Specializations**: >70% of expert pairs with cosine similarity <0.3
- **Successful Composition**: Router training (Phase 2) achieves >95% of end-to-end training performance
- **Training Efficiency**: Phase 1 parallelization reduces wall-clock time by ~10× compared to sequential training

This outcome demonstrates practical feasibility of decentralized collaborative model development.

**4.1.2 Secondary Outcomes**

**Outcome 4: Continual Learning Capability**
The expert addition experiment is expected to show:
- **Minimal Forgetting**: Backward transfer (BWT) > -1% on original 80 tasks
- **Effective Learning**: Forward transfer (FWT) > 60% on new 20 tasks
- **Efficient Updates**: Router retraining requires <10% of original training cost

This validates architectural mitigation of catastrophic forgetting.

**Outcome 5: Scaling Laws for Lightweight Experts**
Analysis across N ∈ {25, 50, 100, 200} experts is expected to reveal:
- **Performance Scaling**: Logarithmic improvement following $\text{Acc}(N) = a - b \cdot N^{-c}$ with $c \approx 0.3$
- **Efficiency Scaling**: Linear growth in total parameters but constant active parameters (due to fixed top-K)
- **Optimal Operating Point**: N=100-200 experts with r=16, K=4 balancing performance and efficiency

**Outcome 6: Rank-Space Routing Effectiveness**
Ablation studies are expected to demonstrate:
- **Feature Importance**: Rank-space projection features improve routing accuracy by 2-3% over standard hidden state features
- **Rank Sensitivity**: Optimal rank r=16 balancing expert capacity and parameter efficiency
- **Load Balancing**: λ=0.01 achieves >80% utilization with <1% performance cost

### 4.2 Theoretical Impact

**Impact 1: Unified PEFT-MoE Framework**
This research establishes the first theoretical bridge between Parameter-Efficient Fine-Tuning and Mixture-of-Experts paradigms. The framework demonstrates that low-rank adaptation modules can serve as effective expert specialists, challenging the assumption that experts must be full-rank feed-forward networks. This unification opens new research directions exploring other PEFT methods (adapters, prefix tuning) as expert architectures.

**Impact 2: Capacity Scaling Theory for Lightweight Experts**
The derived scaling laws provide theoretical justification for extreme expert scaling despite individual capacity constraints. The relationship:

$$\text{Capacity}(N, r) \approx N \times r \times \phi(d)$$

where $\phi(d)$ is an expressivity factor dependent on model dimension, predicts crossover points where quantity compensates for low-rank limitations. This theory guides architectural design decisions for future modular systems.

**Impact 3: Rank-Space Routing Formalism**
The formalization of routing in low-rank parameter subspaces introduces a novel perspective on expert selection. Rather than treating experts as black-box functions, the framework exploits mathematical structure (SVD decomposition, subspace projections) for routing decisions. This opens theoretical questions about optimal subspace partitioning and task-to-subspace mapping.

### 4.3 Methodological Impact

**Impact 1: Hierarchical LoRA-Aware Routing Algorithm**
The two-level routing mechanism with rank-space features provides a reusable template for scaling MoE architectures beyond 100 experts. The algorithm's $O(d \times G + d \times K \times N/G)$ complexity enables practical deployment of 500-1000 expert systems, previously infeasible with flat routing. This methodology transfers to other domains (vision, multimodal) where PEFT methods are applicable.

**Impact 2: Independent Expert Training Protocol**
The three-phase training pipeline (independent expert training → router training → optional fine-tuning) establishes a practical framework for collaborative model development. This protocol enables:
- **Distributed Development**: Teams train experts on proprietary data without sharing
- **Incremental Contribution**: New experts added without retraining existing components
- **Modular Evaluation**: Individual expert quality assessed independently

This methodology addresses the workshop's core challenge of enabling collaborative deep learning.

**Impact 3: Load-Balanced Hierarchical Training**
The extended load balancing loss for hierarchical MoE with PEFT experts provides a solution to expert collapse at multiple hierarchy levels. The dual-level balancing ($\mathcal{L}_{\text{group-balance}} + \mathcal{L}_{\text{expert-balance}}$) prevents both coarse-grained (group) and fine-grained (expert) underutilization, a problem not addressed in standard MoE training.

### 4.4 Practical Impact

**Impact 1: Sustainable Model Evolution**
LoRA-MoE enables incremental model improvement without full retraining, directly addressing the unsustainable "train from scratch" paradigm. Organizations can:
- **Upcycle Existing Models**: Convert deprecated models into expert pools
- **Continuous Improvement**: Add new experts as new domains emerge
- **Version Control**: Maintain expert libraries with version tracking

This reduces the environmental and economic costs of large-scale model development.

**Impact 2: Democratized LLM Development**
By enabling 100+ teams to contribute specialized experts independently, LoRA-MoE lowers barriers to participation in large-scale model development. Smaller organizations or research groups can:
- **Contribute Domain Expertise**: Train experts on specialized domains (medical, legal, scientific)
- **Preserve Data Privacy**: Train on proprietary data without sharing
- **Compose Capabilities**: Benefit from others' experts via shared routing

This democratization aligns with the workshop's emphasis on collaborative and decentralized training.

**Impact 3: Efficient Continual Learning**
The architectural mitigation of catastrophic forgetting through expert addition provides a practical solution for lifelong learning systems. Applications include:
- **Adaptive Assistants**: Personal AI systems that learn new user preferences without forgetting old ones
- **Domain Adaptation**: Models that expand to new domains (e.g., medical → legal) without performance degradation
- **Curriculum Learning**: Sequential skill acquisition in educational AI systems

**Impact 4: Resource-Constrained Deployment**
The 10-100× reduction in active parameters enables deployment on resource-constrained devices:
- **Edge Deployment**: Mobile devices can run 100-expert models with selective expert loading
- **Inference Optimization**: Dynamic expert selection reduces computational cost per query
- **Memory Efficiency**: Store expert pool on disk, load only activated experts to GPU memory

### 4.5 Broader Impact on the Field

**Alignment with Workshop Themes**:

1. **Mixture-of-Experts Architectures**: Advances MoE by demonstrating PEFT modules as lightweight experts, enabling 10-100× scaling beyond current 8-64 expert systems.

2. **Routing of Specialized Experts (MoErging)**: Provides first learned routing mechanism for PEFT modules, extending gradient-free composition methods (LoraHub) to neural routing.

3. **Upcycling and MoE-fication**: Establishes protocol for converting existing LoRA checkpoints into expert pools, enabling model recycling.

4. **Model Merging**: Extends static merging (model soups) to dynamic routing-based composition, learning when to activate which experts.

5. **Continual Learning**: Demonstrates architectural solution to catastrophic forgetting through modular expert addition.

6. **Collaborative Training**: Enables decentralized multi-team development through independent expert training protocol.

**Future Research Directions Enabled**:

1. **Cross-Modal LoRA-MoE**: Extending framework to vision-language models with modality-specific expert pools
2. **Federated LoRA-MoE**: Combining with federated learning for privacy-preserving collaborative training
3. **Automated Expert Discovery**: Learning optimal task-to-expert groupings via meta-learning
4. **Sparse Expert Activation**: Exploring top-1 or top-0.5 (probabilistic) routing for extreme efficiency
5. **Hierarchical Depth**: Extending to 3+ level routing for 1000+ expert systems

**Potential Limitations and Risks**:

1. **Router Overfitting**: Risk of router learning spurious task-expert correlations; mitigated by load balancing and diverse training data
2. **Expert Redundancy**: Possibility of multiple experts learning similar specializations; addressed by diversity metrics and initialization strategies
3. **Scalability Ceiling**: Unknown performance at 500-1000 expert scale; requires future validation
4. **Domain Specificity**: Initial validation on language models; generalization to other domains requires additional research

### 4.6 Expected Publications and Dissemination

**Target Venues**:
- **Primary**: ICLR 2026 (main conference or MCDC Workshop follow-up)
- **Secondary**: NeurIPS 2026, ICML 2026
- **Domain-Specific**: ACL 2026 (for NLP applications), CVPR 2026 (if extended to vision)

**Planned Artifacts**:
1. **Open-Source Implementation**: PyTorch library for LoRA-MoE training and inference
2. **Pre-Trained Models**: 100-expert LoRA-MoE checkpoint on FLAN tasks
3. **Expert Zoo**: Repository of task-specific LoRA experts for community use
4. **Benchmark Suite**: Evaluation protocols for modular MoE systems

**Community Engagement**:
- Workshop presentations at ICLR MCDC and related venues
- Tutorial sessions on collaborative model development
- Collaboration with industry partners for real-world deployment case studies

This research directly addresses the ICLR 2025 Workshop's call for "new paradigms in designing neural network architectures based on modularity, functional specialization, and model recycling," providing both theoretical foundations and practical tools for collaborative, decentralized, and continual deep learning.