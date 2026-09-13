# Research Proposal: Structural Adapter for Table-Aware Prompting: Reducing In-Context Example Requirements for LLM Table Reasoning

## 1. Introduction

### 1.1 Background

Tables represent one of the most ubiquitous data formats in the modern data landscape, dominating enterprise databases, scientific repositories, and web content. According to recent analyses, the majority of datasets indexed by Google Dataset Search conform to tabular formats such as CSV files, and the three most widely-used database management systems are designed specifically for relational data. Despite this prevalence, tables have historically been underserved by the deep learning revolution that has transformed natural language processing and computer vision.

Large Language Models (LLMs) have demonstrated remarkable capabilities across diverse reasoning tasks, yet they exhibit systematic limitations when processing tabular data. Unlike natural language, which flows sequentially, tables encode information through two-dimensional positional relationships—the meaning of a cell depends critically on its row and column context. Current LLMs lack explicit mechanisms to comprehend these 2D structural relationships, leading to degraded performance on table understanding tasks such as question answering, fact verification, and data analysis.

Existing approaches to enhance LLM table reasoning fall into two categories, each with significant limitations. Fine-tuning approaches, exemplified by models like TaPas and TAPEX, achieve strong performance but require substantial computational resources and produce task-specific models that lack generalization. Prompting-based approaches preserve the flexibility of frozen LLMs but typically require numerous in-context examples to achieve reasonable accuracy, consuming valuable context window budget and increasing inference costs.

Recent work has revealed promising directions for bridging this gap. Schema-ICL demonstrated that explicit schema scaffolding can improve LLM reasoning by up to 36% on complex reasoning benchmarks, suggesting that structural information, when properly presented, significantly reduces the cognitive burden on LLMs. Simultaneously, vision-language adapters such as BLIP-2 and LLaVA have established that lightweight projection networks can effectively translate specialized encodings into the language model's embedding space without modifying the base model. However, no existing method systematically combines specialized table encoders with frozen LLMs to reduce in-context example requirements for table reasoning.

### 1.2 Research Objectives

This research proposes SATA-SP (Structural Adapter for Table-Aware Structural Prompting), a novel framework that injects learned structural prompts into frozen LLMs to improve table reasoning efficiency. Our primary objectives are:

1. **Develop a parameter-efficient adapter architecture** that translates TAPAS-style structural embeddings into soft prompt tokens compatible with frozen LLMs.

2. **Demonstrate significant reduction in in-context example requirements** (target: 50% reduction) while maintaining comparable accuracy on standard table QA benchmarks.

3. **Validate zero-shot transfer capabilities** across diverse table domains and task types without domain-specific adapter retraining.

4. **Establish the causal mechanism** through systematic ablation studies that isolate the contribution of structural scaffolding to performance improvements.

### 1.3 Significance

This research addresses a critical gap in the table representation learning landscape with broad implications:

**Scientific Contribution:** SATA-SP establishes a new paradigm for enhancing LLM table understanding through structural prompt injection, providing theoretical insights into how explicit positional scaffolding reduces cognitive load on language models.

**Practical Impact:** By reducing in-context example requirements, SATA-SP enables more efficient deployment of LLMs for table-intensive applications in data analysis, business intelligence, and scientific research, where context window budget is a precious resource.

**Methodological Innovation:** The cross-modal projection approach from table encoders to language model space opens new research directions for multimodal learning with structured data.

## 2. Methodology

### 2.1 Overview of SATA-SP Framework

SATA-SP operates through a three-stage pipeline that transforms raw tables into structurally-enriched prompts for frozen LLMs:

**Stage 1: Structural Encoding** — TAPAS-style embeddings capture row/column positional relationships
**Stage 2: Cross-Modal Projection** — A lightweight projection network translates structural embeddings into soft prompt tokens
**Stage 3: Structural Prompt Injection** — Prepended structural prompts provide explicit positional scaffolding to the LLM

### 2.2 Stage 1: TAPAS-Style Structural Encoding

Given a table $T$ with $R$ rows and $C$ columns, we first serialize each cell $c_{i,j}$ and compute structural embeddings that capture positional relationships.

**Cell Representation:**
For each cell $c_{i,j}$ containing text $t_{i,j}$, we compute:

$$e_{i,j} = \text{BERT}(t_{i,j}) + E_{row}(i) + E_{col}(j) + E_{rank}(r_{i,j})$$

where:
- $\text{BERT}(t_{i,j}) \in \mathbb{R}^{d}$ is the contextualized embedding of cell text
- $E_{row}(i) \in \mathbb{R}^{d}$ is the learned row position embedding
- $E_{col}(j) \in \mathbb{R}^{d}$ is the learned column position embedding  
- $E_{rank}(r_{i,j}) \in \mathbb{R}^{d}$ encodes numerical rank within the column (for sortable columns)

**Structural Attention:**
We apply structural self-attention to capture inter-cell relationships:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}} + M_{struct}\right)V$$

where $M_{struct}$ is a structural bias matrix encoding row/column alignment:

$$M_{struct}[i,j] = \alpha \cdot \mathbb{1}[\text{same\_row}(i,j)] + \beta \cdot \mathbb{1}[\text{same\_col}(i,j)]$$

**Table-Level Representation:**
We aggregate cell embeddings into a fixed-size table representation using learned pooling:

$$h_{table} = \text{AttentionPool}(\{e_{i,j}\}_{i \in [R], j \in [C]}) \in \mathbb{R}^{d \times k}$$

where $k$ is the number of structural summary vectors (hyperparameter: $k \in \{8, 16, 32\}$).

### 2.3 Stage 2: Cross-Modal Projection Network

The projection network $\mathcal{P}$ transforms structural embeddings into soft prompt tokens compatible with the target LLM's embedding space.

**Architecture:**
We employ a lightweight transformer-based projector:

$$\mathcal{P}(h_{table}) = \text{MLP}(\text{TransformerBlock}^{L}(h_{table} + Q_{learnable}))$$

where:
- $Q_{learnable} \in \mathbb{R}^{n \times d}$ are $n$ learnable query tokens
- $L$ is the number of transformer layers (hyperparameter: $L \in \{2, 3\}$)
- The output dimension matches the target LLM's embedding dimension $d_{LLM}$

**Output:**
The projection produces $n$ soft prompt tokens:

$$P_{struct} = \mathcal{P}(h_{table}) \in \mathbb{R}^{n \times d_{LLM}}$$

### 2.4 Stage 3: Structural Prompt Injection

The structural prompts are prepended to the serialized table input before feeding to the frozen LLM.

**Input Construction:**
Given a question $q$ and table $T$, the final input to the LLM is:

$$\text{Input} = [P_{struct}; \text{Serialize}(T); \text{Tokenize}(q)]$$

where $\text{Serialize}(T)$ converts the table to markdown format with pipe delimiters.

**Inference:**
The frozen LLM processes the augmented input:

$$\text{Answer} = \text{LLM}(\text{Input})$$

The structural prompts $P_{struct}$ provide explicit positional scaffolding, reducing the LLM's burden of inferring structural relationships from the serialized representation.

### 2.5 Training Procedure

**Training Objective:**
We train only the structural encoder and projection network while keeping the LLM frozen. The training objective combines:

$$\mathcal{L} = \mathcal{L}_{QA} + \lambda \mathcal{L}_{struct}$$

where:
- $\mathcal{L}_{QA}$ is the cross-entropy loss for question answering
- $\mathcal{L}_{struct}$ is a structural consistency loss encouraging the model to preserve row/column relationships

**Structural Consistency Loss:**

$$\mathcal{L}_{struct} = \sum_{(i,j) \in \text{SameRow}} \|e_i - e_j\|_2 + \sum_{(i,j) \in \text{SameCol}} \|e_i - e_j\|_2$$

**Training Data:**
We curate a diverse training corpus of approximately 50,000 tables from:
- WikiTableQuestions training set (14,149 examples)
- SQA (Sequential Question Answering) dataset
- Spider text-to-SQL dataset (tables only)
- Synthetic tables with programmatically generated QA pairs

### 2.6 Experimental Design

#### 2.6.1 Datasets and Benchmarks

| Dataset | Task | Size | Metrics |
|---------|------|------|---------|
| WikiTableQuestions | Table QA | 22,033 | Exact Match Accuracy |
| TabFact | Fact Verification | 118,439 | Binary Accuracy |
| FeTaQA | Free-form Table QA | 10,330 | BLEU, ROUGE-L |
| SQA | Sequential QA | 17,553 | Sequence Accuracy |

#### 2.6.2 Baselines

1. **Direct Prompting:** Standard few-shot prompting with serialized tables
2. **Chain-of-Table:** Iterative table operations with LLM reasoning
3. **Self-Augmentation:** Table Meets LLM self-augmentation approach
4. **Binder:** Program-aided reasoning with LLMs

#### 2.6.3 Experimental Conditions

**Primary Experiment (In-Context Efficiency):**
- Vary number of in-context examples: 0, 1, 2, 4, 8 shots
- Compare SATA-SP vs. baselines at each shot level
- Measure examples required to reach 70% accuracy threshold

**Ablation Studies:**
- **A1:** Remove structural prompts (projection network only)
- **A2:** Remove positional embeddings (content only)
- **A3:** Random structural prompts (untrained projection)
- **A4:** Vary prompt token count (8, 16, 32)

**Transfer Experiments:**
- Train on WikiTableQuestions, evaluate zero-shot on TabFact and FeTaQA
- Measure domain transfer without adapter retraining

**Structural Complexity Analysis:**
- Stratify tables by complexity (rows × columns)
- Compare relative improvement across complexity bins

#### 2.6.4 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Exact Match Accuracy | Percentage of exactly correct answers | ≥70% |
| In-Context Efficiency | Examples to reach accuracy threshold | 50% reduction |
| Zero-Shot Transfer | Accuracy without domain-specific training | ≥60% |
| Inference Latency | Additional time from structural encoding | <100ms |

#### 2.6.5 Statistical Analysis

- **Sample Size:** Minimum 25 examples per condition
- **Statistical Tests:** Independent samples t-test with Bonferroni correction ($\alpha = 0.05/3$)
- **Effect Size:** Report Cohen's d with 95% confidence intervals
- **Significance Threshold:** $p < 0.017$ (corrected)

### 2.7 Implementation Details

**LLM Backends:**
- GPT-3.5-turbo (API-based, frozen)
- Llama-2-7B (local deployment, frozen)

**Structural Encoder:**
- BERT-base initialization for cell encoder
- 6-layer transformer for structural attention
- Hidden dimension: 768

**Projection Network:**
- 2-layer transformer with cross-attention
- 32 learnable query tokens
- Output dimension: 4096 (Llama-2) or 1536 (GPT-3.5)

**Training Configuration:**
- Optimizer: AdamW with learning rate 1e-4
- Batch size: 32
- Training epochs: 10
- Hardware: 4× NVIDIA A100 GPUs

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect SATA-SP to achieve equivalent accuracy (≥70%) on WikiTableQuestions with 50% fewer in-context examples compared to direct prompting baselines. Specifically:
- Baseline: 4-shot prompting achieves ~70% accuracy
- SATA-SP: 2-shot prompting achieves ≥70% accuracy

**Secondary Outcomes:**
- **P2 (Zero-Shot Transfer):** ≥60% accuracy on TabFact and FeTaQA without domain-specific training, compared to ≤50% for baselines
- **P3 (Structural Complexity Benefit):** Larger relative improvements (>15%) for complex tables (>10 columns) compared to simple tables (<5 columns)

**Ablation Insights:**
- Removing structural prompts expected to degrade performance by >10%
- Removing positional embeddings expected to show largest degradation
- Random prompts expected to perform no better than baseline

### 3.2 Scientific Impact

**Theoretical Contributions:**
1. **Cognitive Load Theory for LLMs:** Empirical validation that explicit structural scaffolding reduces the reasoning burden on LLMs, extending cognitive load theory to neural language models
2. **Cross-Modal Projection for Structured Data:** Demonstration that vision-language adapter techniques transfer effectively to the table-language domain
3. **Structural Bottleneck Hypothesis:** Evidence that structural understanding is a primary bottleneck in LLM table reasoning

**Methodological Contributions:**
1. **Parameter-Efficient Table Adaptation:** A new paradigm for enhancing LLM table capabilities without costly fine-tuning
2. **Structural Prompt Design:** Principles for designing effective structural prompts for tabular data
3. **Evaluation Framework:** Standardized metrics for measuring in-context efficiency in table reasoning

### 3.3 Practical Impact

**Immediate Applications:**
- **Data Analysis Assistants:** More efficient LLM-powered tools for business intelligence and data exploration
- **Question Answering Systems:** Reduced API costs and latency for table-based QA applications
- **Enterprise Search:** Enhanced retrieval and understanding of tabular content in document repositories

**Broader Impact:**
- **Democratization:** Lower computational barriers for deploying table-aware AI systems
- **Sustainability:** Reduced inference costs contribute to more environmentally sustainable AI
- **Accessibility:** Enables table understanding capabilities on smaller, locally-deployable models

### 3.4 Limitations and Future Directions

**Known Limitations:**
1. Scope limited to standard relational tables (≤100 rows, ≤20 columns)
2. Does not address nested/hierarchical table structures
3. Requires adapter training on diverse table corpora
4. Adds inference latency (~50-100ms) from structural encoding

**Future Research Directions:**
1. Extension to multi-table reasoning and cross-sheet references
2. Integration with retrieval-augmented generation for large table collections
3. Application to domain-specific tables (medical, financial, legal)
4. Exploration of structural prompts for other structured data formats (JSON, XML, graphs)

### 3.5 Timeline and Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Data Preparation | Month 1-2 | Curated training corpus, preprocessing pipeline |
| Model Development | Month 3-4 | SATA-SP implementation, initial training |
| Primary Experiments | Month 5-6 | WikiTableQuestions evaluation, baseline comparisons |
| Ablation & Transfer | Month 7-8 | Ablation studies, zero-shot transfer experiments |
| Analysis & Writing | Month 9-10 | Statistical analysis, paper preparation |

This research proposal presents a rigorous plan to develop and validate SATA-SP, a novel approach for enhancing LLM table reasoning through structural prompt injection. By bridging specialized table encoders with frozen LLMs, we aim to establish a parameter-efficient paradigm with broad applications in data analysis, question answering, and beyond.