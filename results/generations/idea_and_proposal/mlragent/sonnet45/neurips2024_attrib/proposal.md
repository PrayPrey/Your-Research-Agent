# Causal Data Provenance Graphs for Tracing Emergent Capabilities in Large Language Models

## 1. Introduction

### Background

The rapid advancement of large language models (LLMs) has been driven by the confluence of three factors: architectural innovations, algorithmic improvements, and increasingly large-scale training datasets. While we can measure the impressive capabilities these models exhibit—from multilingual reasoning to complex code generation—our understanding of how specific training data compositions give rise to these emergent behaviors remains limited. This knowledge gap poses significant challenges for model development, debugging, compliance, and safety.

Current data attribution methods, such as influence functions and example-based attribution, treat training examples as independent contributors to model behavior. However, this independence assumption fundamentally misrepresents how knowledge is structured and learned. In reality, training data exhibits rich interdependencies: Wikipedia articles cite primary sources, code repositories depend on libraries, scientific papers build on prior work, and multilingual parallel corpora provide bridging knowledge between languages. These dependencies create compositional effects where capabilities emerge not from individual examples, but from specific combinations of data sources.

This limitation becomes critical when addressing pressing questions in modern ML development: Why does removing a specific data source cause catastrophic forgetting of seemingly unrelated capabilities? How does contamination in one dataset propagate through dependent sources? Which combinations of data sources are necessary and sufficient for a particular emergent capability? Without frameworks to reason about data interdependencies, we are left with expensive trial-and-error approaches to dataset curation and limited tools for debugging model failures.

Recent work has begun exploring the intersection of causal reasoning and LLMs, with approaches using LLMs for causal graph discovery and applying causal frameworks to understand model behavior. However, these efforts have not addressed the fundamental challenge of constructing causal provenance graphs specifically for training data attribution at scale, nor have they developed methods to track how data combinations drive capability emergence during training.

### Research Objectives

This research proposes to develop **Causal Data Provenance Graphs (CDPGs)**, a novel framework for attributing emergent capabilities in large language models to combinations of training data sources. The specific objectives are:

1. **Design hierarchical data provenance graphs** that explicitly represent semantic and temporal dependencies among training examples, clustering related data into meaningful subgraphs
2. **Develop efficient influence tracking mechanisms** using gradient-based sketching techniques that operate over data subgraphs rather than individual examples, enabling scalability to billion-parameter models
3. **Establish interventional analysis protocols** for systematically measuring how specific data source combinations contribute to capability emergence through controlled ablation studies
4. **Validate the framework** on capabilities with known data requirements (e.g., multilingual reasoning, domain-specific knowledge) and demonstrate practical applications to contamination detection and data mixture optimization

### Significance

This research addresses critical needs in the ML community:

**Scientific Impact**: By moving beyond example-level attribution to subgraph-level causal analysis, this work will provide the first principled framework for understanding how data composition drives emergent capabilities, advancing our theoretical understanding of deep learning.

**Practical Impact**: The proposed methods will enable practitioners to (1) debug model failures by identifying missing or problematic data combinations, (2) trace contamination propagation through dependency chains, (3) optimize data acquisition strategies by identifying high-value data combinations, and (4) ensure regulatory compliance by providing transparent capability-to-data mappings.

**Methodological Innovation**: The integration of causal graph theory with scalable influence tracking represents a novel approach that bridges interpretability research, causal inference, and large-scale machine learning systems.

## 2. Methodology

### 2.1 Causal Data Provenance Graph Construction

#### 2.1.1 Graph Formalization

We define a Causal Data Provenance Graph as $G = (V, E, \mathcal{C})$ where:

- $V = \{d_1, d_2, ..., d_N\}$ represents training examples
- $E \subseteq V \times V$ represents directed dependencies, where $(d_i, d_j) \in E$ indicates that $d_j$ depends on or derives from $d_i$
- $\mathcal{C}: V \rightarrow 2^V$ maps each node to its cluster (subgraph) based on semantic similarity

We distinguish three types of edges:

1. **Explicit dependencies**: Citations, code imports, data derivations (e.g., translated texts)
2. **Semantic dependencies**: Discovered through embedding similarity, where $(d_i, d_j) \in E$ if $\text{sim}(\phi(d_i), \phi(d_j)) > \tau$ and $d_i$ temporally precedes $d_j$
3. **Functional dependencies**: Examples that co-activate similar model components, discovered through activation pattern analysis

#### 2.1.2 Hierarchical Clustering Algorithm

We construct a hierarchical clustering $\mathcal{H} = \{C_1^{(l)}, C_2^{(l)}, ..., C_{k_l}^{(l)}\}_{l=1}^L$ across $L$ levels:

**Algorithm 1: Hierarchical CDPG Construction**

```
Input: Training dataset D, embedding function φ, similarity threshold τ
Output: Hierarchical graph G with clusters C

1. Initialize G = (D, ∅, ∅)
2. For each level l from 1 to L:
   a. Compute embeddings: {φ(d_i) | d_i ∈ D}
   b. Perform spectral clustering with k_l clusters
   c. For each cluster C_j^(l):
      - Identify cluster centroid c_j = mean({φ(d) | d ∈ C_j^(l)})
      - Add intra-cluster edges based on similarity > τ
   d. Identify inter-cluster edges using citation/dependency metadata
3. Create super-nodes for level l+1 from level l clusters
4. Return multi-level graph G
```

The hierarchical structure enables efficient influence tracking at multiple granularities: fine-grained for critical capabilities and coarse-grained for broader attribution patterns.

### 2.2 Influence Tracking via Gradient-Based Sketching

#### 2.2.1 Subgraph Influence Functions

Traditional influence functions estimate the effect of removing example $z_i$ on model parameters $\theta$:

$$\mathcal{I}(z_i) = -H_{\theta}^{-1} \nabla_{\theta} L(z_i, \theta)$$

where $H_{\theta}$ is the Hessian. We extend this to subgraph influence:

$$\mathcal{I}_G(C_j) = -H_{\theta}^{-1} \sum_{z_i \in C_j} w_{ij} \nabla_{\theta} L(z_i, \theta)$$

where $w_{ij}$ are weights determined by the graph structure:

$$w_{ij} = \frac{1}{|C_j|} \left(1 + \alpha \cdot \text{PageRank}_{G}(z_i)\right)$$

The PageRank term accounts for the centrality of each example within the dependency graph, giving higher weight to foundational examples.

#### 2.2.2 Efficient Sketching Algorithm

Computing exact subgraph influences is intractable for large models. We develop a sketching approach:

**Algorithm 2: Gradient-Based Influence Sketching**

```
Input: Model θ, subgraphs {C_1, ..., C_k}, sketch dimension m
Output: Influence sketches {S_1, ..., S_k}

1. Initialize random projection matrix P ∈ ℝ^(m×p) where p = dim(θ)
2. For each checkpoint t during training:
   a. For each subgraph C_j:
      - Sample batch B_j ~ C_j
      - Compute gradient: g_j = ∇_θ L(B_j, θ_t)
      - Update sketch: S_j^(t) = S_j^(t-1) + P · g_j
   b. Periodically compute capability scores on held-out tasks
3. For each capability κ:
   a. Compute gradient: g_κ = ∇_θ L_κ(θ_final)
   b. Project: g_κ' = P · g_κ
   c. Rank subgraphs by: score(C_j, κ) = ⟨S_j^(final), g_κ'⟩
4. Return ranked attributions
```

This approach reduces memory from $O(|V| \cdot p)$ to $O(k \cdot m)$ where $k \ll |V|$ and $m \ll p$, making it tractable for billion-parameter models.

### 2.3 Interventional Analysis Framework

#### 2.3.1 Systematic Ablation Protocol

We measure causal effects through controlled interventions:

**Experiment Design:**

1. **Single-Subgraph Ablation**: For each $C_j$, train model $\theta_{-j}$ without $C_j$, measure capability degradation:
   $$\Delta_j(\kappa) = \text{Performance}(\theta, \kappa) - \text{Performance}(\theta_{-j}, \kappa)$$

2. **Pairwise Interaction**: For pairs $(C_i, C_j)$, estimate interaction effects:
   $$\Delta_{ij}(\kappa) = \Delta_{i \cup j}(\kappa) - \Delta_i(\kappa) - \Delta_j(\kappa)$$
   
   Positive $\Delta_{ij}$ indicates synergistic combinations.

3. **Targeted Addition**: Starting from base model $\theta_0$ trained on core data, sequentially add subgraphs in order of predicted influence, measuring capability emergence.

#### 2.3.2 Causal Effect Estimation

We employ a regression-based approach to estimate causal effects while controlling for confounders:

$$\mathbb{E}[\kappa | \text{do}(C_j = 1)] = \beta_j + \sum_{C_i \in \text{Pa}(C_j)} \gamma_i \mathbb{I}[C_i \in D]$$

where $\text{Pa}(C_j)$ are parent nodes in the CDPG. We use doubly-robust estimation:

$$\hat{\Delta}_j = \frac{1}{n} \sum_{k=1}^n \left[ \frac{\kappa_k \mathbb{I}[C_j \in D_k]}{\hat{p}(C_j | X_k)} - \frac{\kappa_k (1-\mathbb{I}[C_j \in D_k])}{1-\hat{p}(C_j | X_k)} \right]$$

### 2.4 Data Collection and Experimental Design

#### 2.4.1 Controlled Validation Datasets

We construct three controlled settings with known data-capability relationships:

1. **Multilingual Reasoning**: Using parallel corpora from OPUS, we create graphs where edges connect parallel texts. Expected capability: translation and cross-lingual transfer depend on language pair coverage.

2. **Mathematical Reasoning**: Using ProofWiki and arXiv math papers, we build dependency graphs based on theorem citations. Expected capability: formal proof generation requires foundational definitions and lemmas.

3. **Code Generation**: Using GitHub repositories, we construct dependency graphs from import statements. Expected capability: API usage requires documentation and example code.

#### 2.4.2 Large-Scale Validation

For real-world validation, we apply our framework to:

- **C4 dataset** (~365GB): Build semantic graphs using sentence embeddings
- **The Pile** (~825GB): Construct multi-source graphs with cross-dataset dependencies
- **Model scales**: 125M, 1.3B, and 6.7B parameter models to study scaling effects

#### 2.4.3 Evaluation Metrics

**Attribution Quality:**
- **Precision@K**: Fraction of top-K attributed subgraphs that are truly necessary (validated through ablation)
- **Recall@K**: Fraction of necessary subgraphs captured in top-K
- **Faithfulness**: Correlation between predicted influence scores and measured performance degradation: $\rho(\text{score}(C_j, \kappa), \Delta_j(\kappa))$

**Capability Prediction:**
- **Emergence Prediction Error**: $\text{MAE}(\hat{\kappa}, \kappa_{\text{actual}})$ when predicting capability from data composition
- **Contamination Detection**: AUROC for identifying contaminated evaluation examples through provenance tracing

**Computational Efficiency:**
- **Attribution Time**: Wall-clock time to attribute capability to data subgraphs
- **Memory Overhead**: Additional memory required during training for influence tracking
- **Scaling Coefficient**: How attribution cost scales with model size and dataset size

### 2.5 Implementation Details

**Graph Construction:**
- Sentence embeddings: Sentence-BERT for semantic similarity
- Clustering: Leiden algorithm for efficient community detection
- Graph storage: Neo4j for efficient subgraph queries

**Training Infrastructure:**
- Framework: PyTorch with custom gradient hooks for influence tracking
- Distributed training: FSDP for large models
- Checkpointing: Save influence sketches every 1000 steps

**Baseline Comparisons:**
- TracIn: Example-based influence tracking
- DataInf: Scalable data attribution
- Dataset cartography: Confidence-based characterization

## 3. Expected Outcomes & Impact

### 3.1 Scientific Contributions

**Theoretical Advances:**

1. **Compositional Attribution Theory**: We expect to establish formal bounds on the error of subgraph-level attribution compared to example-level attribution, showing when coarse-grained analysis is sufficient:

   $$|\mathcal{I}_G(C_j) - \sum_{z_i \in C_j} \mathcal{I}(z_i)| \leq \epsilon(\text{modularity}(C_j))$$

2. **Capability Emergence Characterization**: Our interventional analyses should reveal whether capabilities emerge through:
   - **Threshold effects**: Requiring minimum data quantity
   - **Diversity effects**: Requiring coverage of data subgraphs
   - **Synergy effects**: Requiring specific combinations

3. **Scaling Laws for Data Composition**: We anticipate discovering power-law relationships between subgraph coverage and capability strength:

   $$\text{Performance}(\kappa) = \alpha \cdot \left(\sum_{C_j \in \mathcal{R}_\kappa} |C_j|\right)^\beta$$

   where $\mathcal{R}_\kappa$ are relevant subgraphs for capability $\kappa$.

### 3.2 Methodological Outcomes

**Practical Tools:**

1. **CDPG Library**: Open-source implementation supporting:
   - Automatic graph construction from common data formats
   - Efficient influence tracking integrated with standard training loops
   - Visualization tools for capability-to-data attribution maps

2. **Contamination Tracing System**: Tools to:
   - Identify evaluation examples with training data provenance
   - Trace contamination propagation through dependency chains
   - Quantify contamination severity based on graph distance

3. **Data Mixture Optimizer**: Algorithm to recommend data composition for target capabilities:
   ```
   Input: Target capabilities {κ_1, ..., κ_n}, available subgraphs {C_1, ..., C_k}
   Output: Optimal mixture weights {w_1, ..., w_k}
   
   Solve: max_w Σ_i utility(κ_i, Σ_j w_j · score(C_j, κ_i))
   Subject to: Σ_j w_j = 1, w_j ≥ 0, cost(w) ≤ budget
   ```

### 3.3 Empirical Findings

We expect to demonstrate:

1. **Improved Attribution Accuracy**: 30-50% improvement in Precision@10 over example-based baselines when identifying data sources for complex capabilities

2. **Computational Efficiency**: Sketch-based tracking adding <5% training overhead while enabling attribution that would otherwise require full retraining

3. **Contamination Detection**: >90% AUROC in detecting contaminated evaluation examples through provenance analysis

4. **Capability Engineering**: Demonstrating targeted capability improvement through data mixture optimization based on CDPG analysis

### 3.4 Broader Impact

**For ML Practitioners:**
- **Debugging**: Rapidly identify missing or problematic data combinations causing capability gaps
- **Data Acquisition**: Make informed decisions about which data sources to prioritize for desired capabilities
- **Compliance**: Provide auditable trails linking model capabilities to training data for regulatory purposes

**For Research Community:**
- **Benchmark Development**: Enable construction of cleaner benchmarks through systematic contamination detection
- **Data Efficiency**: Guide research on minimum data requirements for capabilities
- **Interpretability**: Bridge data attribution and mechanistic interpretability by connecting data sources to model components

**For AI Safety:**
- **Capability Control**: Better understand and potentially restrict emergence of undesired capabilities
- **Bias Tracing**: Attribute model biases to specific data sources and their dependencies
- **Transparency**: Provide stakeholders with clear explanations of how training data compositions drive behaviors

### 3.5 Limitations and Future Work

**Expected Limitations:**

1. **Graph Construction Quality**: Semantic dependencies may be noisy, requiring human validation for critical applications
2. **Causal Assumptions**: Our framework assumes stable data-capability relationships, which may not hold when capabilities emerge from complex interactions
3. **Computational Constraints**: While more efficient than full retraining, large-scale interventional analysis remains expensive

**Future Directions:**

1. **Active Learning Integration**: Use attribution maps to guide active data collection
2. **Cross-Model Transfer**: Investigate whether provenance graphs transfer across architectures
3. **Temporal Dynamics**: Study how data influence evolves during training
4. **Multi-Modal Extension**: Extend framework to vision-language models with heterogeneous data sources

This research will provide the ML community with principled tools for understanding and controlling how training data composition drives emergent capabilities, enabling more reliable, efficient, and transparent model development at scale.