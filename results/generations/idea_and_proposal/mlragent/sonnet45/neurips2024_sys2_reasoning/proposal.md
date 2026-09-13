# Research Proposal: Explicit Compositional Decomposition Networks (ECDN)

## 1. Title

**Explicit Compositional Decomposition Networks (ECDN): Benchmarking and Enabling System-2 Reasoning through Verifiable Subtask Graphs**

## 2. Introduction

### Background

The distinction between System-1 and System-2 reasoning, originally proposed in cognitive science, has become increasingly relevant in understanding the limitations of modern large language models (LLMs). System-1 reasoning is characterized by fast, automatic, and associative processing—largely what current neural networks excel at through pattern matching and retrieval. In contrast, System-2 reasoning involves slow, deliberate, and compositional thinking that requires explicit manipulation of abstract concepts, rule-based inference, and systematic generalization to novel situations.

Despite remarkable progress in scaling transformer-based models, contemporary LLMs demonstrate persistent failures in tasks requiring true compositional reasoning. The fundamental challenge lies in distinguishing whether models are engaging in genuine reasoning through systematic rule application or merely retrieving sophisticated memorized patterns from training data. This ambiguity poses critical concerns for AI safety, as we cannot reliably predict model behavior in out-of-distribution scenarios or verify the correctness of intermediate reasoning steps.

Recent research has explored various approaches to enhance reasoning capabilities. EVR+ (Liang et al., 2023) introduced explicit symbolic operators for compositional reasoning, while ExoViP (Wang et al., 2024) proposed verification modules for multi-step visual reasoning. However, these approaches either lack robust mechanisms for preventing error propagation or fail to provide contamination-resistant evaluation frameworks that definitively separate memorization from reasoning.

The integration of neural and symbolic approaches—termed neurosymbolic AI—offers promising directions by combining the flexibility of neural networks with the interpretability and compositionality of symbolic systems. Yet, a critical question remains unresolved: should System-2 reasoning be implemented implicitly within model architectures or explicitly through engineered systems operating around the model?

### Research Objectives

This research proposes Explicit Compositional Decomposition Networks (ECDN), a hybrid framework designed to address three fundamental objectives:

1. **Develop an explicit, verifiable reasoning architecture** that decomposes complex problems into atomic subtasks organized as directed acyclic graphs (DAGs), where each node represents a verifiable reasoning step with formal input/output constraints.

2. **Create a contamination-resistant benchmarking suite** that generates evaluation tasks through programmatic composition of primitive operations, ensuring that test cases represent truly novel combinations never encountered during training.

3. **Establish interpretable reasoning traces** that enable post-hoc verification and error attribution, addressing critical AI safety concerns by making the reasoning process transparent and auditable.

### Significance

This research directly addresses several workshop questions: (1) It proposes that System-2 reasoning requires explicit architectural mechanisms rather than purely emergent properties from scale; (2) It advocates for a hybrid implementation where symbolic planning operates externally while neural models execute subtasks; (3) It provides rigorous benchmarking methodology to measure genuine systematic generalization while avoiding data contamination.

The significance extends beyond academic contributions. Verifiable reasoning traces have immediate implications for high-stakes domains like medical diagnosis, legal reasoning, and scientific discovery, where understanding *why* a model reaches specific conclusions is as important as the conclusions themselves. Furthermore, the contamination-resistant evaluation framework addresses growing concerns about benchmark saturation and unreliable performance metrics in the era of massive pre-training datasets.

## 3. Methodology

### 3.1 System Architecture

ECDN consists of four interconnected components operating in a cyclic reasoning loop:

#### 3.1.1 Task Decomposition Planner

The decomposition planner transforms a complex input task $T$ into a directed acyclic graph $G = (V, E)$, where:

- Each vertex $v_i \in V$ represents an atomic subtask with a well-defined operation $op_i$ from a finite operation set $\mathcal{O}$
- Each edge $e_{ij} \in E$ represents a data dependency from subtask $v_i$ to $v_j$
- The graph structure $G$ satisfies topological ordering constraints

Formally, given task $T$ and context $C$, the planner learns a mapping:

$$\pi_\theta: (T, C) \rightarrow G = (V, E)$$

where $\theta$ represents learnable parameters. We implement $\pi_\theta$ as a graph neural network (GNN) trained to predict subtask graphs from task embeddings. The GNN architecture uses a hierarchical encoder:

1. **Task Encoder**: Transforms natural language task $T$ into embedding $\mathbf{h}_T \in \mathbb{R}^d$ using a pre-trained language model
2. **Graph Generator**: Autoregressively generates nodes and edges:
   - At step $t$, predict next node operation: $p(op_t | \mathbf{h}_T, V_{<t}) = \text{softmax}(W_o \mathbf{h}_t + \mathbf{b}_o)$
   - Predict edges to previous nodes: $p(e_{jt} | op_t, V_{<t}) = \sigma(W_e[\mathbf{h}_j; \mathbf{h}_t])$
3. **Termination Detector**: Predicts when decomposition is complete based on coverage of task requirements

The operation set $\mathcal{O}$ includes primitives such as: {RETRIEVE, COMPARE, AGGREGATE, CALCULATE, CLASSIFY, TRANSFORM, FILTER}, each with typed input/output specifications.

#### 3.1.2 Subtask Execution Engine

Each subtask $v_i$ with operation $op_i$ is executed by a specialized neural module. We employ a mixture-of-experts (MoE) approach where different operation types route to different expert models:

$$\text{Execute}(v_i) = \sum_{k=1}^K g_k(op_i) \cdot \text{Expert}_k(\text{inputs}(v_i))$$

where $g_k(op_i)$ represents gating weights for operation type $op_i$, and $\text{inputs}(v_i)$ aggregates outputs from predecessor nodes according to edge structure.

For interpretability, each expert model is constrained to be relatively small (e.g., 100M-1B parameters) and specialized to its operation domain. This modularity enables targeted improvements and debugging.

#### 3.1.3 Verification Module

The verification module validates each subtask output before propagating to dependent nodes. For subtask $v_i$ producing output $o_i$, we define multiple verification strategies:

**Formal Constraint Verification**: For operations with formal specifications, verify that $o_i$ satisfies type constraints and semantic properties:

$$\text{Valid}_{\text{formal}}(o_i) = \bigwedge_{c \in C_{op_i}} c(o_i)$$

where $C_{op_i}$ represents the constraint set for operation $op_i$.

**Consistency Verification**: Check consistency with alternative execution paths when multiple decomposition strategies exist:

$$\text{Valid}_{\text{consist}}(o_i) = \mathbb{I}[\text{similarity}(o_i, o_i^{\text{alt}}) > \tau]$$

where $o_i^{\text{alt}}$ comes from an alternative decomposition and $\tau$ is a similarity threshold.

**Confidence-Based Verification**: Use calibrated uncertainty estimates:

$$\text{Valid}_{\text{conf}}(o_i) = \mathbb{I}[\text{Conf}(o_i | \text{inputs}(v_i)) > \delta]$$

where $\text{Conf}(\cdot)$ represents calibrated confidence and $\delta$ is a threshold.

The final verification decision combines these strategies:

$$\text{Verify}(v_i, o_i) = \alpha_1 \text{Valid}_{\text{formal}}(o_i) + \alpha_2 \text{Valid}_{\text{consist}}(o_i) + \alpha_3 \text{Valid}_{\text{conf}}(o_i) > \gamma$$

When verification fails, the system either (1) re-executes with alternative decomposition, (2) requests human feedback for that specific subtask, or (3) reports failure with error localization.

#### 3.1.4 Answer Integration Module

After all subtasks are verified, the integration module synthesizes the final answer by aggregating outputs from terminal nodes (nodes with no outgoing edges):

$$A = \text{Integrate}(\{o_i : v_i \in V_{\text{terminal}}\}, G)$$

The integration process maintains a complete reasoning trace $\mathcal{T} = (G, \{o_i\}_{i=1}^{|V|}, \{s_i\}_{i=1}^{|V|})$ where $s_i$ represents verification status for each node.

### 3.2 Training Methodology

#### 3.2.1 Data Collection and Annotation

We construct a training dataset through three complementary approaches:

**Approach 1: Reverse Engineering from Existing Benchmarks**
- Take complex reasoning tasks from MATH, GSM8K, StrategyQA, and similar datasets
- Manually annotate gold-standard decomposition graphs
- Create ~50,000 annotated examples covering diverse reasoning types

**Approach 2: Synthetic Generation from Primitives**
- Define formal semantics for each operation in $\mathcal{O}$
- Programmatically compose operations into valid DAGs
- Generate input tasks and ground-truth answers through execution
- Create ~500,000 synthetic examples with guaranteed valid decompositions

**Approach 3: Weak Supervision from LLM Traces**
- Prompt powerful LLMs (GPT-4, Claude) to show step-by-step reasoning
- Parse intermediate steps into candidate subtask graphs
- Filter using verification modules
- Create ~200,000 weakly supervised examples

#### 3.2.2 Training Procedure

The training follows a multi-stage curriculum:

**Stage 1: Subtask Executor Pre-training**
Train individual expert models on operation-specific datasets:

$$\mathcal{L}_{\text{exec}} = \mathbb{E}_{(x, y, op) \sim \mathcal{D}_{\text{ops}}}[\ell(f_{\text{Expert}_{op}}(x), y)]$$

where $\ell$ is task-appropriate loss (cross-entropy for classification, MSE for regression, etc.).

**Stage 2: Decomposition Planner Training**
Train the graph planner using supervised learning on annotated decompositions:

$$\mathcal{L}_{\text{plan}} = \mathbb{E}_{(T, G^*) \sim \mathcal{D}_{\text{ann}}}[\ell_{\text{graph}}(\pi_\theta(T), G^*)]$$

where $\ell_{\text{graph}}$ measures structural similarity using graph edit distance and node-wise operation classification loss.

**Stage 3: End-to-End Reinforcement Learning**
Fine-tune the complete system using policy gradient methods where the reward combines:

$$R(T, G, \{o_i\}) = \lambda_1 \mathbb{I}[A = A^*] + \lambda_2 \frac{\sum_i \text{Verify}(v_i, o_i)}{|V|} - \lambda_3 |V|$$

This reward encourages correct final answers, high verification rates, and parsimony in decomposition complexity.

**Stage 4: Verification Module Calibration**
Train verification modules using both positive examples (verified correct executions) and negative examples (injected errors):

$$\mathcal{L}_{\text{verify}} = \mathbb{E}_{(v_i, o_i, y_{\text{correct}}) \sim \mathcal{D}_{\text{verify}}}[\text{BCE}(\text{Verify}(v_i, o_i), y_{\text{correct}})]$$

where BCE represents binary cross-entropy loss.

### 3.3 Contamination-Resistant Benchmark Suite

To rigorously evaluate systematic generalization, we develop the **Compositional Reasoning Out-of-Distribution (CROOD)** benchmark:

#### 3.3.1 Primitive Operation Bank
Define 50 atomic operations spanning:
- Mathematical operations (arithmetic, algebra, calculus)
- Logical operations (conjunction, disjunction, negation, quantification)
- Retrieval operations (entity lookup, relation extraction)
- Comparison operations (numerical, categorical, temporal)
- Aggregation operations (counting, averaging, extrema)

#### 3.3.2 Compositional Task Generation

Generate test tasks through controlled composition:

**Depth Generalization**: Create tasks requiring composition chains longer than any training example:
- Training: max depth $d_{\text{train}} = 5$
- Testing: depths $d \in \{6, 7, 8, 9, 10\}$

**Width Generalization**: Create tasks with more parallel subtasks:
- Training: max width $w_{\text{train}} = 3$
- Testing: widths $w \in \{4, 5, 6\}$

**Novel Combinations**: Identify operation pairs $(op_i, op_j)$ never co-occurring in training data, then create tasks requiring both:

$$\mathcal{T}_{\text{novel}} = \{T : \exists \text{ path in } G_T \text{ containing both } op_i \text{ and } op_j\}$$

**Cross-Domain Transfer**: Combine operations from different domains (e.g., mathematical reasoning on entities from commonsense knowledge).

#### 3.3.3 Evaluation Metrics

We measure multiple aspects of systematic generalization:

**Accuracy Metrics**:
- $\text{Acc}_{\text{final}}$: Correctness of final answer
- $\text{Acc}_{\text{subtask}}$: Average correctness of individual subtask outputs
- $\text{Acc}_{\text{structure}}$: Graph edit distance between predicted and optimal decomposition

**Reasoning Quality Metrics**:
- $\text{Verify}_{\text{rate}}$: Proportion of subtasks passing verification
- $\text{Error}_{\text{prop}}$: Fraction of final errors attributable to error propagation vs. initial mistakes
- $\text{Depth}_{\text{recovery}}$: Ability to recover from errors at different graph depths

**Efficiency Metrics**:
- $\text{Parsimony}$: Ratio of subtasks used to minimum necessary
- $\text{Latency}$: Total inference time
- $\text{Compute}$: FLOPs consumed

**Generalization Gap**:
$$\Delta_{\text{gen}} = \text{Acc}_{\text{in-dist}} - \text{Acc}_{\text{out-of-dist}}$$

A small $\Delta_{\text{gen}}$ indicates robust systematic generalization.

### 3.4 Experimental Design

#### 3.4.1 Baseline Comparisons

We compare ECDN against:

1. **End-to-End Neural Baselines**: GPT-4, Claude-3, Llama-3 (70B) with standard prompting
2. **Chain-of-Thought Methods**: Few-shot CoT, Zero-shot CoT, Self-Consistency
3. **Decomposition Methods**: Least-to-Most prompting, recursive decomposition
4. **Neurosymbolic Methods**: EVR+, Program-of-Thought
5. **Search-Based Methods**: Tree-of-Thought, Graph-of-Thought

#### 3.4.2 Ablation Studies

To isolate contributions of each component:

1. **Verification Ablation**: Remove verification module ($\alpha_1 = \alpha_2 = \alpha_3 = 0$)
2. **Planning Ablation**: Use fixed decomposition strategies instead of learned planner
3. **Specialization Ablation**: Replace MoE with single monolithic executor
4. **Architecture Ablation**: Implement planning implicitly within a single model vs. explicit external system

#### 3.4.3 Human Evaluation

Conduct human studies (n=100 participants) to assess:
- **Interpretability**: Can humans understand the reasoning trace?
- **Trustworthiness**: Do humans find verified traces more reliable?
- **Error Diagnosis**: How quickly can humans identify error sources?

#### 3.4.4 Computational Requirements

- **Training**: 8×A100 GPUs, approximately 14 days for full curriculum
- **Inference**: Single A100 GPU, <10 seconds per task for depth ≤10
- **Benchmark Generation**: Automated pipeline producing 100K test cases

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Technical Outcomes**:

1. **Improved Systematic Generalization**: We anticipate ECDN will achieve significantly smaller generalization gaps compared to baselines:
   - Expected $\Delta_{\text{gen}} < 10\%$ for depth generalization (vs. >30% for CoT methods)
   - Expected $\Delta_{\text{gen}} < 15\%$ for novel combinations (vs. >40% for end-to-end models)

2. **Verifiable Reasoning Traces**: >85% of subtasks should pass verification on in-distribution tasks, with interpretable error localization when failures occur.

3. **Contamination-Resistant Benchmark**: The CROOD benchmark will provide a reliable testbed for measuring genuine reasoning capabilities, updated regularly with programmatically generated novel compositions.

4. **Empirical Insights**: Detailed ablation studies will reveal whether explicit symbolic planning provides advantages over implicit emergent planning, addressing the workshop's core question about implementation strategies.

**Theoretical Outcomes**:

1. **Formalization of Compositionality**: A rigorous mathematical framework characterizing compositional reasoning in terms of graph properties, operation semantics, and generalization bounds.

2. **Error Attribution Theory**: Theoretical analysis of how verification at different graph levels affects error propagation, potentially yielding bounds on downstream error rates.

### 4.2 Scientific Impact

**Advancing System-2 Reasoning Research**:

This work directly addresses the workshop's central questions by:
- Demonstrating that System-2 reasoning benefits from explicit external mechanisms rather than relying solely on scale
- Providing empirical evidence for hybrid neurosymbolic approaches
- Establishing rigorous benchmarking standards that prevent contamination

**Broader ML Contributions**:

1. **Interpretability**: The explicit decomposition graphs provide unprecedented transparency into model reasoning, advancing XAI research.

2. **Compositional Learning**: Insights into which compositional structures generalize well vs. poorly will inform future architecture design.

3. **Evaluation Methodology**: The programmatic benchmark generation approach can be adapted to other domains requiring contamination-resistant evaluation.

### 4.3 Practical Impact

**AI Safety and Alignment**:

Verifiable reasoning traces enable:
- Detection of reasoning failures before deployment
- Auditing of high-stakes decisions
- Identification of systematic biases in reasoning patterns

**Domain Applications**:

1. **Scientific Discovery**: Transparent reasoning over complex scientific hypotheses
2. **Medical Diagnosis**: Interpretable diagnostic chains that clinicians can verify
3. **Legal Analysis**: Traceable legal reasoning for case analysis
4. **Education**: Pedagogical tools that demonstrate proper problem-solving strategies

### 4.4 Limitations and Future Work

**Known Limitations**:

1. **Scalability**: Graph-based planning may face computational challenges for extremely complex tasks (depth >15)
2. **Operation Coverage**: The finite operation set $\mathcal{O}$ may not cover all reasoning patterns
3. **Annotation Cost**: Creating high-quality decomposition annotations is labor-intensive

**Future Directions**:

1. **Learned Operation Discovery**: Extend $\mathcal{O}$ through meta-learning on new task distributions
2. **Hierarchical Abstraction**: Enable subtask graphs to contain composite operations, creating multi-level reasoning hierarchies
3. **Interactive Verification**: Incorporate human-in-the-loop verification for critical reasoning steps
4. **Cross-Modal Reasoning**: Extend framework to visual, auditory, and multimodal reasoning tasks

### 4.5 Resource Sharing and Reproducibility

We commit to open-sourcing:
- Complete ECDN implementation
- Full CROOD benchmark with generation code
- Pre-trained models and decomposition annotations
- Evaluation scripts and baseline implementations

This enables the research community to:
- Validate our findings independently
- Build upon the framework for novel applications
- Continuously extend the benchmark to prevent saturation

## Conclusion

Explicit Compositional Decomposition Networks represent a principled approach to imbuing neural systems with System-2 reasoning capabilities through explicit, verifiable decomposition mechanisms. By combining symbolic planning with neural execution and introducing contamination-resistant evaluation, this research addresses critical gaps in current reasoning systems. The hybrid architecture provides a concrete answer to whether System-2 reasoning should be implicit or explicit: we argue that explicit external mechanisms offer superior interpretability, verifiability, and systematic generalization—essential properties for trustworthy AI systems deployed in high-stakes environments.

The proposed work bridges theoretical insights from cognitive science, practical engineering of neurosymbolic systems, and rigorous empirical evaluation, positioning it to make substantial contributions to the workshop's core themes while providing actionable pathways toward more reliable and interpretable AI reasoning systems.