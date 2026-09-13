# Research Proposal

## Title: Cross-Table Relational Pre-training via Foreign Key-Aware Contrastive Learning

---

## 1. Introduction

### Background

Tables constitute one of the most prevalent data structures in the modern data landscape. From enterprise databases to public datasets, tabular data forms the backbone of data management, analysis, and decision-making pipelines. According to recent surveys, relational databases dominate the database management ecosystem, with the top three most-used systems all designed for structured, relational data. Despite this ubiquity, table representation learning has historically lagged behind advances in natural language and image representation learning.

Recent years have witnessed remarkable progress in table representation learning, with models like BERT-based table encoders demonstrating strong performance on tasks such as table understanding, semantic parsing, and question answering. Pre-training paradigms have proven particularly effective, enabling models to learn rich representations that transfer well to downstream tasks. Models such as TaBERT, TAPAS, and GraPPa have achieved impressive results on benchmarks like Spider and WikiTableQuestions by learning joint representations of textual queries and tabular data.

However, a critical limitation persists: **existing table representation methods predominantly focus on single tables in isolation**, effectively ignoring the relational structure that connects tables in real-world databases. In enterprise settings, databases typically comprise dozens or hundreds of interconnected tables linked through foreign key relationships, forming complex relational schemas. Tasks such as multi-table question answering, complex text-to-SQL generation spanning multiple tables, schema matching, and cross-table entity resolution fundamentally require understanding these inter-table relationships.

Recent work has attempted to address multi-table challenges through various approaches. UNJOIN (2025) simplifies multi-table schemas by merging columns into single-table representations, while PSM-SQL (2025) employs progressive schema learning with multi-granularity semantics. MultiTabQA (2023) tackles multi-table question answering by generating tabular answers. However, these approaches either simplify away the relational structure or address specific downstream tasks without learning generalizable cross-table representations during pre-training.

### Research Objectives

This research proposes **RelTableBERT**, a novel pre-training framework that explicitly models inter-table relationships through foreign key-aware contrastive learning. Our primary objectives are:

1. **Develop a relational graph-based representation** that captures the structural connections between tables in relational databases through foreign key relationships.

2. **Design novel pre-training objectives** that learn semantically meaningful representations of cross-table relationships, enabling models to understand how columns and rows across different tables relate to each other.

3. **Introduce cross-table attention mechanisms** that condition column representations on information from related foreign tables, enabling rich contextual understanding of relational semantics.

4. **Validate the approach comprehensively** on multi-table benchmarks spanning text-to-SQL generation, schema matching, and cross-table entity resolution.

### Significance

This research addresses a fundamental gap in table representation learning with significant implications for both research and practice. By learning to represent cross-table relationships during pre-training, RelTableBERT will enable:

- More accurate text-to-SQL generation for complex queries spanning multiple tables
- Improved schema understanding for database design and integration tasks
- Better LLM-based data analysis systems that can reason over entire relational databases
- Enhanced enterprise data management through automated schema matching and entity resolution

---

## 2. Methodology

### 2.1 Overview

RelTableBERT extends existing table encoders with three key innovations: (1) a relational graph construction module that models foreign key relationships, (2) foreign key-aware contrastive pre-training objectives, and (3) a cross-table attention mechanism. We describe each component in detail below.

### 2.2 Relational Graph Construction

Given a relational database $\mathcal{D} = \{T_1, T_2, ..., T_n\}$ containing $n$ tables, we construct a relational graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where:

- **Nodes** $\mathcal{V}$: Each table $T_i$ is represented as a node. Additionally, we create column-level nodes $c_{i,j}$ for each column $j$ in table $T_i$.
- **Edges** $\mathcal{E}$: Edges connect columns involved in foreign key relationships. For a foreign key constraint $FK(T_i.c_a, T_j.c_b)$ indicating that column $c_a$ in table $T_i$ references column $c_b$ in table $T_j$, we create an edge $e = (c_{i,a}, c_{j,b})$ with edge type "foreign_key".

We also define **join paths** as sequences of edges connecting two tables through intermediate foreign key relationships:

$$P(T_i, T_j) = \{e_1, e_2, ..., e_k\} \text{ where } e_l \in \mathcal{E}$$

### 2.3 Base Table Encoder

For each table $T_i$, we first obtain initial representations using a BERT-based encoder. Given a table with schema $S_i = \{c_{i,1}, c_{i,2}, ..., c_{i,m}\}$ and rows $R_i = \{r_1, r_2, ..., r_p\}$, we linearize the table following established practices:

$$\text{Input}_i = [\text{CLS}] \oplus \text{TableName} \oplus [\text{SEP}] \oplus c_{i,1} \oplus v_{1,1} \oplus ... \oplus c_{i,m} \oplus v_{1,m} \oplus [\text{SEP}] \oplus ...$$

where $v_{j,k}$ represents sample values from row $j$, column $k$. The base encoder produces:

$$\mathbf{H}_i = \text{Encoder}(\text{Input}_i) \in \mathbb{R}^{L \times d}$$

where $L$ is the sequence length and $d$ is the hidden dimension.

### 2.4 Cross-Table Attention Mechanism

To enable information flow across related tables, we introduce a cross-table attention layer. For a column $c_{i,a}$ with foreign key relationship to column $c_{j,b}$, we compute cross-table attention as:

$$\mathbf{Q} = \mathbf{W}_Q \mathbf{h}_{c_{i,a}}, \quad \mathbf{K} = \mathbf{W}_K \mathbf{H}_j, \quad \mathbf{V} = \mathbf{W}_V \mathbf{H}_j$$

$$\text{CrossAttn}(\mathbf{h}_{c_{i,a}}, \mathbf{H}_j) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$

The updated column representation incorporates information from the foreign table:

$$\mathbf{h}'_{c_{i,a}} = \mathbf{h}_{c_{i,a}} + \alpha \cdot \text{CrossAttn}(\mathbf{h}_{c_{i,a}}, \mathbf{H}_j)$$

where $\alpha$ is a learnable gating parameter.

### 2.5 Pre-training Objectives

We propose three complementary pre-training objectives:

#### 2.5.1 Foreign Key-Aware Contrastive Learning (FKCL)

This objective learns to distinguish semantically related column pairs (connected via foreign keys) from unrelated pairs. For a batch of column pairs, let $\mathcal{P}^+ = \{(c_i, c_j) | FK(c_i, c_j) \in \mathcal{E}\}$ be positive pairs and $\mathcal{P}^-$ be randomly sampled negative pairs.

The contrastive loss is defined as:

$$\mathcal{L}_{\text{FKCL}} = -\sum_{(c_i, c_j) \in \mathcal{P}^+} \log \frac{\exp(\text{sim}(\mathbf{h}_{c_i}, \mathbf{h}_{c_j}) / \tau)}{\sum_{(c_i, c_k) \in \mathcal{P}^+ \cup \mathcal{P}^-} \exp(\text{sim}(\mathbf{h}_{c_i}, \mathbf{h}_{c_k}) / \tau)}$$

where $\text{sim}(\cdot, \cdot)$ is cosine similarity and $\tau$ is a temperature hyperparameter.

#### 2.5.2 Join Path Prediction (JPP)

This auxiliary task trains the model to predict valid join sequences between table pairs. Given tables $T_i$ and $T_j$, the model must predict whether a valid join path exists and, if so, the sequence of intermediate tables.

We formulate this as a sequence classification task:

$$\mathcal{L}_{\text{JPP}} = -\sum_{(T_i, T_j)} \sum_{t=1}^{|P|} \log P(T^{(t)} | T_i, T_j, T^{(1)}, ..., T^{(t-1)})$$

where $T^{(t)}$ is the $t$-th table in the join path $P(T_i, T_j)$.

#### 2.5.3 Masked Column Prediction with Relational Context (MCP-R)

Extending standard masked language modeling, we mask columns and require the model to predict them using both local table context and cross-table relational information:

$$\mathcal{L}_{\text{MCP-R}} = -\sum_{c_{\text{mask}}} \log P(c_{\text{mask}} | \mathbf{H}_{\text{local}}, \mathbf{H}_{\text{cross}})$$

The total pre-training loss is:

$$\mathcal{L}_{\text{total}} = \lambda_1 \mathcal{L}_{\text{FKCL}} + \lambda_2 \mathcal{L}_{\text{JPP}} + \lambda_3 \mathcal{L}_{\text{MCP-R}}$$

### 2.6 Data Collection and Pre-training Corpus

We construct a large-scale pre-training corpus from multiple sources:

1. **Public Database Schemas**: Spider, BIRD, WikiSQL databases with explicit foreign key annotations
2. **Synthetic Relational Databases**: Generated using schema templates with realistic foreign key patterns
3. **Enterprise Database Snapshots**: Anonymized schemas from database benchmarks (TPC-H, TPC-DS)

We estimate approximately 50,000 relational schemas containing 500,000+ tables with 2 million+ foreign key relationships.

### 2.7 Experimental Design

#### Downstream Tasks and Benchmarks

1. **Multi-Table Text-to-SQL**: Spider benchmark (cross-domain), BIRD benchmark
2. **Schema Matching**: Valentine benchmark, Fabricated datasets
3. **Cross-Table Entity Resolution**: Magellan benchmark datasets
4. **Multi-Table Question Answering**: MultiTabQA benchmark

#### Baselines

- Single-table encoders: TaBERT, TAPAS, GraPPa
- Multi-table approaches: UNJOIN, PSM-SQL
- Large language models: GPT-4, CodeLlama (with schema prompting)

#### Evaluation Metrics

- **Text-to-SQL**: Exact Match Accuracy (EM), Execution Accuracy (EX)
- **Schema Matching**: Precision, Recall, F1-Score
- **Entity Resolution**: Precision, Recall, F1-Score
- **QA**: Exact Match, Token-level F1

#### Ablation Studies

We will conduct ablations to assess the contribution of each component:
- Removing FKCL objective
- Removing JPP objective
- Removing cross-table attention
- Varying the number of foreign key hops considered

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **State-of-the-art Performance on Multi-Table Benchmarks**: We anticipate RelTableBERT will achieve 3-5% absolute improvement in execution accuracy on Spider's multi-table queries compared to existing baselines. For schema matching tasks, we expect 5-8% F1 improvement.

2. **Pre-trained Model and Code Release**: We will release the pre-trained RelTableBERT model, training code, and evaluation scripts to facilitate reproducibility and future research.

3. **New Benchmark Dataset**: We will curate and release a cross-table evaluation benchmark specifically designed to assess relational understanding capabilities.

4. **Empirical Insights**: Comprehensive analysis of how foreign key-aware pre-training affects downstream task performance, including attention visualization and probing studies.

### Research Impact

This work addresses a fundamental limitation in table representation learning with broad implications:

**For NLP Research**: RelTableBERT will advance the state-of-the-art in semantic parsing and structured data understanding, providing a foundation for more sophisticated database-grounded language understanding.

**For Database Research**: The learned representations can enhance query optimization, schema design recommendations, and automated database administration tasks.

**For Enterprise Applications**: Improved cross-table understanding directly benefits enterprise data management, enabling more accurate natural language interfaces to complex database systems, automated data integration, and intelligent data cataloging.

**For LLM Development**: As LLMs increasingly interact with structured data, RelTableBERT provides specialized representations that can augment general-purpose language models through retrieval-augmented generation or fine-tuning.

### Limitations and Future Directions

We acknowledge potential limitations including computational overhead from cross-table attention and challenges in scaling to very large schemas. Future work will explore efficient attention mechanisms and hierarchical schema representations to address these concerns.

---

## 4. Conclusion

This proposal presents RelTableBERT, a novel pre-training framework that bridges a critical gap in table representation learning by explicitly modeling cross-table relationships through foreign key-aware contrastive learning. By learning from relational structure during pre-training, RelTableBERT promises to enable more accurate reasoning over multi-table databases, with significant implications for text-to-SQL generation, schema understanding, and LLM-based data analysis systems.