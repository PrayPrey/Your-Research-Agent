# Causal Circuit Discovery: Using Targeted Interventions to Map Decision-Making Mechanisms in Large Language Models

## 1. Introduction

### Background

Large Language Models (LLMs) have demonstrated remarkable capabilities across diverse tasks, from natural language understanding to complex reasoning and decision-making. These models, trained on vast amounts of unstructured data using self-supervised learning objectives, have achieved performance levels that sometimes exceed human experts. However, their deployment in safety-critical domains such as healthcare, policy-making, and legal systems is hindered by a fundamental limitation: we lack systematic understanding of *how* these models arrive at their decisions.

Current interpretability approaches predominantly rely on observational analysis, including attention visualization, gradient-based attribution methods, and probing classifiers. While these techniques can reveal correlations between model components and behaviors, they cannot establish causal relationships—a critical distinction when we need to predict model behavior under novel conditions or distribution shifts. As Alvarez-Melis and Jaakkola (2017) noted, understanding causal relationships rather than mere associations is essential for interpreting black-box model predictions.

Recent work has begun exploring the intersection of causality and large models. Zhang et al. (2023) assessed LLMs' ability to answer causal questions, concluding that while models can leverage existing causal knowledge, they cannot yet discover new causal relationships or provide reliable answers for high-stakes decisions. Gkountouras et al. (2024) demonstrated the potential of integrating causal world models with LLMs, while Bazgir et al. (2025) envisioned causal LLM agents for biomedicine. However, a critical gap remains: we lack principled methods to discover and validate the *internal* causal mechanisms by which LLMs process information and generate outputs.

### Research Objectives

This research proposes a comprehensive framework for **Causal Circuit Discovery** that systematically identifies, validates, and maps the causal decision-making mechanisms within LLMs. The primary objectives are:

1. **Develop a principled intervention methodology** that combines causal inference theory with mechanistic interpretability techniques to identify causal dependencies between model components
2. **Formalize causal graph discovery algorithms** that construct directed acyclic graphs (DAGs) representing information flow through LLM architectures for specific tasks
3. **Establish counterfactual validation protocols** that verify discovered causal circuits and predict model behavior under distribution shifts
4. **Create task-specific causal atlases** that document reusable causal mechanisms across different capabilities and model scales

### Significance

This research addresses multiple critical challenges at the intersection of causality and large models. First, it provides a "causality of large models" framework that systematically reveals how these systems work, addressing the interpretability crisis that hampers their deployment in high-stakes domains. Second, by establishing causal rather than correlational understanding, the methodology enables robust predictions about model behavior under interventions and novel conditions—crucial for trustworthiness guarantees. Third, the approach facilitates targeted debugging and improvement by identifying specific causal pathways responsible for failures or biases. Finally, the framework bridges theoretical causality research with practical LLM deployment needs, creating actionable tools for practitioners while advancing our scientific understanding of these complex systems.

## 2. Methodology

### 2.1 Theoretical Framework

Our approach integrates structural causal models (SCMs) with mechanistic interpretability. We formalize an LLM as a composition of functional modules $M = \{m_1, m_2, ..., m_n\}$, where each module $m_i$ represents a model component (attention head, MLP layer, or residual stream position). For a given input $x$ and output $y$, we model the information flow as a SCM:

$$\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{F})$$

where $\mathcal{V}$ represents variables (module activations), $\mathcal{E}$ represents directed edges (causal dependencies), and $\mathcal{F}$ represents the functional relationships. Each variable $v_i \in \mathcal{V}$ corresponds to the activation of module $m_i$, and satisfies:

$$v_i = f_i(pa(v_i), \epsilon_i)$$

where $pa(v_i)$ denotes the parent variables in the causal graph and $\epsilon_i$ represents exogenous noise.

### 2.2 Systematic Intervention Design

**Activation Patching Protocol**: We implement a comprehensive intervention strategy based on activation patching (also called causal tracing). For each module $m_i$:

1. **Clean Run**: Execute the model on a clean input $x$ to obtain baseline activations $\{a_1^{\text{clean}}, ..., a_n^{\text{clean}}\}$ and output $y^{\text{clean}}$

2. **Corrupted Run**: Execute the model on a corrupted input $x'$ (designed to alter specific information while preserving structure) to obtain corrupted activations $\{a_1^{\text{corrupt}}, ..., a_n^{\text{corrupt}}\}$ and output $y^{\text{corrupt}}$

3. **Intervention**: For each module $m_i$, replace its activation during the corrupted run with the clean activation: $a_i^{\text{corrupt}} \leftarrow a_i^{\text{clean}}$, obtaining restored output $y^{\text{restore}, i}$

4. **Causal Effect Measurement**: Quantify the causal effect of module $m_i$ as:

$$CE(m_i) = \mathcal{D}(y^{\text{restore}, i}, y^{\text{clean}}) - \mathcal{D}(y^{\text{corrupt}}, y^{\text{clean}})$$

where $\mathcal{D}$ is a task-appropriate distance metric (e.g., KL divergence for probability distributions, exact match for discrete outputs).

**Path Patching**: To identify causal pathways between modules, we implement path-specific interventions:

$$CE(m_i \rightarrow m_j) = \mathcal{D}(y^{\text{path-restore}, i \rightarrow j}, y^{\text{clean}}) - \mathcal{D}(y^{\text{corrupt}}, y^{\text{clean}})$$

This measures the causal effect transmitted specifically through the path from $m_i$ to $m_j$.

**Ablation Studies**: Complementary to patching, we perform systematic ablations:

$$CE_{\text{ablate}}(m_i) = \mathcal{D}(y^{\text{ablate}, i}, y^{\text{clean}})$$

where $a_i$ is set to zero or mean-pooled activations.

### 2.3 Causal Graph Discovery Algorithm

We propose a novel algorithm, **Iterative Causal Circuit Discovery (ICCD)**, that constructs task-specific causal graphs:

**Algorithm: ICCD**

**Input**: Model $M$, task dataset $\mathcal{D}_{\text{task}} = \{(x_k, y_k)\}_{k=1}^K$, significance threshold $\tau$

**Output**: Causal graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$

1. **Initialization**: 
   - $\mathcal{V} \leftarrow$ all model components
   - $\mathcal{E} \leftarrow \emptyset$
   - Compute average causal effects: $\overline{CE}(m_i) = \frac{1}{K}\sum_{k=1}^K CE(m_i; x_k)$

2. **Component Selection**:
   - $\mathcal{V}_{\text{active}} \leftarrow \{m_i : \overline{CE}(m_i) > \tau\}$
   - Update $\mathcal{V} \leftarrow \mathcal{V}_{\text{active}}$

3. **Edge Discovery**:
   - For each ordered pair $(m_i, m_j) \in \mathcal{V} \times \mathcal{V}$ where $m_i$ precedes $m_j$ in model architecture:
     - Compute $\overline{CE}(m_i \rightarrow m_j) = \frac{1}{K}\sum_{k=1}^K CE(m_i \rightarrow m_j; x_k)$
     - If $\overline{CE}(m_i \rightarrow m_j) > \tau$:
       - Add edge $m_i \rightarrow m_j$ to $\mathcal{E}$

4. **Conditional Independence Testing**:
   - For each edge $(m_i, m_j) \in \mathcal{E}$:
     - Identify potential mediators $\mathcal{M}_{ij} = \{m_k : m_i \rightarrow m_k \rightarrow m_j \text{ in } \mathcal{G}\}$
     - Compute conditional causal effect: $CE(m_i \rightarrow m_j | \mathcal{M}_{ij})$
     - If $CE(m_i \rightarrow m_j | \mathcal{M}_{ij}) < \tau$:
       - Remove direct edge $m_i \rightarrow m_j$ (effect is fully mediated)

5. **Return** $\mathcal{G}$

### 2.4 Counterfactual Validation

To validate discovered causal circuits, we implement three complementary validation strategies:

**1. Counterfactual Prediction Accuracy**: For held-out test cases, we predict model outputs under novel interventions using the discovered causal graph $\mathcal{G}$ and Pearl's do-calculus:

$$P(y | do(m_i = a')) = \sum_{pa(m_i)} P(y | m_i = a', pa(m_i)) P(pa(m_i))$$

We measure validation accuracy as:

$$\text{CPA} = \frac{1}{|\mathcal{D}_{\text{test}}|} \sum_{(x,y) \in \mathcal{D}_{\text{test}}} \mathbb{1}[\mathcal{D}(y^{\text{predicted}}, y^{\text{actual}}) < \epsilon]$$

**2. Circuit Sufficiency Testing**: We implement a minimal circuit by removing all components not in the discovered causal graph and verify that task performance is preserved:

$$\text{Sufficiency} = \frac{\text{Performance}(M_{\text{circuit}})}{\text{Performance}(M_{\text{full}})}$$

**3. Distribution Shift Robustness**: We evaluate whether causal circuits identified on in-distribution data predict model behavior under systematic distribution shifts (e.g., domain transfer, adversarial perturbations, systematic prompt variations).

### 2.5 Experimental Design

**Phase 1: Task Selection and Dataset Construction**

We will focus on three diverse task categories to demonstrate generalizability:

1. **Factual Recall**: Country-capital associations, scientific facts (e.g., "The capital of France is [MASK]")
2. **Algorithmic Reasoning**: Multi-digit addition, parity checking, simple logical inference
3. **Linguistic Processing**: Subject-verb agreement, coreference resolution, sentiment classification

For each task, we construct datasets with 1,000 training examples for causal discovery and 500 test examples for validation. Each example includes clean inputs and systematic corruptions designed to ablate specific information (e.g., replacing entity names with random tokens, shuffling word order).

**Phase 2: Model Selection**

We will conduct experiments across multiple model scales to assess how causal mechanisms scale:

- GPT-2 Small (117M parameters)
- GPT-2 Medium (345M parameters)
- GPT-2 Large (774M parameters)
- Llama-2-7B (7B parameters)

**Phase 3: Baseline Comparisons**

We compare our causal circuit discovery approach against existing interpretability methods:

1. **Attention-based attribution**: Visualizing attention weights to identify "important" heads
2. **Gradient-based attribution**: Integrated gradients and attention rollout
3. **Probing classifiers**: Training linear probes on intermediate representations
4. **LIME/SHAP**: Model-agnostic explanation methods

**Phase 4: Evaluation Metrics**

- **Precision and Recall**: Compared against ground-truth circuits (for synthetic tasks with known mechanisms)
- **Counterfactual Prediction Accuracy (CPA)**: As defined in Section 2.4
- **Circuit Complexity**: Number of components and edges in discovered circuits (preference for parsimony)
- **Sufficiency Score**: Performance retention when using only circuit components
- **Robustness**: Performance under distribution shifts
- **Faithfulness**: Correlation between causal effect magnitudes and actual impact on model decisions

### 2.6 Implementation Details

All experiments will be implemented using PyTorch and the TransformerLens library for mechanistic interpretability. Interventions will be applied using custom forward hooks. Statistical significance will be assessed using bootstrap resampling (1,000 iterations) with Bonferroni correction for multiple comparisons. Computational experiments will be conducted on NVIDIA A100 GPUs with mixed-precision training. Code and discovered causal atlases will be released as open-source resources to facilitate reproducibility and future research.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**1. Methodological Contributions**

This research will produce a comprehensive, validated framework for causal circuit discovery in LLMs. The ICCD algorithm will provide researchers and practitioners with a principled tool for mapping causal mechanisms, moving beyond correlational interpretability methods. We expect to demonstrate that causal circuits can be discovered with high precision (>0.85) and sufficiency (>0.90) across diverse tasks, establishing the viability of mechanistic causal analysis.

**2. Task-Specific Causal Atlases**

We will construct detailed causal atlases documenting the mechanisms underlying factual recall, algorithmic reasoning, and linguistic processing in transformer models. These atlases will reveal:

- Which attention heads implement specific computational primitives (e.g., induction heads for copying, previous token heads for context)
- How MLP layers transform representations to encode task-relevant features
- Multi-step causal pathways showing how information flows from input to output
- Shared vs. task-specific circuits across different capabilities

**3. Scaling Laws for Causal Mechanisms**

By analyzing circuits across model scales (117M to 7B parameters), we will characterize how causal mechanisms evolve with model capacity. We hypothesize that larger models implement more modular, specialized circuits while smaller models rely on polysemantic components that participate in multiple causal pathways.

**4. Robustness and Failure Mode Characterization**

The counterfactual validation phase will reveal how causal circuits respond to distribution shifts. We expect to identify:

- Fragile circuits that fail under modest perturbations (indicating unreliable reasoning)
- Robust circuits that maintain causal structure across domains
- Systematic failure modes where specific circuit components produce incorrect outputs

**5. Predictive Models of Behavior**

The discovered causal graphs will enable quantitative predictions of model behavior under novel interventions without requiring expensive inference. This will support:

- Targeted model editing by modifying specific circuit components
- Uncertainty quantification by identifying when inputs activate unreliable circuits
- Safety verification by exhaustively testing critical causal pathways

### Impact

**Scientific Impact**

This research directly addresses the "causality of large models" theme by providing rigorous tools to understand *how* LLMs work. By formalizing the connection between structural causal models and neural network mechanistic interpretability, we bridge theoretical causality research with practical deep learning analysis. The framework will establish causal circuit discovery as a complement to existing interpretability paradigms, emphasizing mechanisms over associations.

The work will advance our understanding of emergent capabilities in large models. By revealing the causal structure underlying tasks like factual recall and reasoning, we can test hypotheses about whether these capabilities arise from explicit algorithmic circuits or distributed statistical associations—a fundamental question in understanding why large models work so well.

**Practical Impact**

For practitioners deploying LLMs in high-stakes domains, this research provides actionable tools for verification and debugging. The ability to map causal circuits enables:

- **Targeted auditing**: Identifying and testing the specific mechanisms responsible for sensitive decisions (e.g., in medical diagnosis or legal reasoning)
- **Failure prediction**: Detecting when inputs activate unreliable circuits before deployment
- **Model improvement**: Editing or fine-tuning specific circuit components without disrupting overall performance
- **Trust calibration**: Providing stakeholders with interpretable causal explanations rather than black-box predictions

**Broader Implications**

This framework contributes to the "causality for large models" theme by demonstrating how causal inference principles can improve LLM trustworthiness. The counterfactual validation protocols establish rigorous standards for evaluating whether interpretability methods actually capture model mechanisms or merely correlational artifacts.

For the AI safety community, causal circuit discovery provides a foundation for mechanistic anomaly detection and adversarial robustness. By understanding the causal pathways that produce correct outputs, we can detect when inputs trigger abnormal circuits or when distribution shifts disrupt critical causal dependencies.

Finally, the task-specific causal atlases will serve as scientific artifacts documenting the "anatomy" of language model capabilities, much like neural circuit diagrams in neuroscience. These resources will accelerate future research by providing reusable building blocks and validated benchmarks for interpretability methods.

### Limitations and Future Directions

While this research establishes a foundation for causal circuit discovery, several limitations suggest directions for future work:

1. **Scalability**: Current intervention methods may become computationally prohibitive for models with hundreds of billions of parameters. Developing approximate or hierarchical intervention strategies will be crucial.

2. **Multimodal models**: Extending the framework to vision-language models will require adapting intervention techniques for visual representations.

3. **Temporal dynamics**: For tasks involving long-context reasoning or multi-turn dialogue, capturing temporal causal dependencies will require extensions to the static causal graph formalism.

4. **Automated circuit interpretation**: While we discover *which* components participate in circuits, understanding *what computation* they implement remains challenging and may benefit from integration with LLM-based automated analysis (as suggested by Takayama et al., 2024).

Despite these limitations, this research represents a significant step toward principled, causal understanding of large language models—a critical foundation for deploying these powerful systems responsibly in real-world applications.

---

**Word Count**: Approximately 2,000 words