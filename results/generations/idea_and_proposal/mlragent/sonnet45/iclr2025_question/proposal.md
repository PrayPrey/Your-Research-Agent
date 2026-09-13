# Research Proposal: Semantic Consistency Graphs for Detecting and Quantifying Hallucinations in Multi-Turn LLM Conversations

## 1. Title

**Semantic Consistency Graphs for Detecting and Quantifying Hallucinations in Multi-Turn LLM Conversations: A Graph-Based Framework for Longitudinal Uncertainty Quantification**

## 2. Introduction

### Background

Large Language Models (LLMs) have achieved remarkable capabilities in generating coherent and contextually appropriate responses across diverse domains. However, their propensity to hallucinate—generating plausible but factually incorrect or internally inconsistent information—poses critical challenges for deployment in high-stakes applications such as healthcare diagnostics, legal consultation, and financial advising. While existing research has made significant progress in detecting hallucinations in isolated responses, a critical gap remains in understanding and quantifying uncertainty across multi-turn conversational contexts.

Current uncertainty quantification methods predominantly focus on single-response evaluation, employing techniques such as perplexity-based detection, semantic embedding analysis, and spectral graph analysis of attention mechanisms. Recent work by Noël (2025) demonstrated that graph signal processing can effectively detect hallucinations by analyzing spectral patterns in transformer attention graphs, achieving 88.75% accuracy. Similarly, Chen et al. (2025) introduced multi-dimensional uncertainty quantification through tensor decomposition of semantic similarity matrices. However, these approaches treat each response independently, failing to capture temporal inconsistencies that emerge as LLMs navigate complex, multi-turn dialogues.

The temporal dimension of LLM reliability presents unique challenges. A model may provide a confident response in turn $t$, only to contradict itself in turn $t+k$, while maintaining high per-response confidence throughout. This longitudinal inconsistency is particularly problematic in conversational AI applications where users build mental models based on accumulated information across dialogue history. In healthcare consultations, for instance, an LLM might suggest one treatment approach early in conversation and contradict it later, potentially leading to harmful decisions despite each individual response appearing credible.

### Research Objectives

This research proposes a novel framework called **Semantic Consistency Graphs (SCGs)** to address the critical gap in longitudinal hallucination detection and uncertainty quantification. Our primary objectives are:

1. **Develop a scalable graph-based representation** that captures semantic relationships between claims across conversation history, enabling efficient tracking of consistency patterns in multi-turn dialogues.

2. **Design computational methods** for real-time inconsistency detection through graph-based anomaly detection algorithms that identify contradiction clusters and temporal coherence violations.

3. **Formulate conversation-level uncertainty metrics** that aggregate local inconsistencies into interpretable, actionable uncertainty scores with fine-grained explanations.

4. **Establish benchmark datasets and evaluation protocols** specifically designed for assessing hallucination detection in multi-turn conversational contexts.

5. **Validate the framework** across diverse domains and conversation types to demonstrate practical applicability and generalizability.

### Significance

This research addresses several critical needs in reliable AI deployment. First, it provides a principled approach to longitudinal consistency monitoring, enabling systems to detect when LLMs exceed their knowledge boundaries across extended interactions. Second, by offering interpretable explanations through graph visualization of contradictions, it facilitates human oversight and informed decision-making. Third, the framework's computational efficiency makes it suitable for real-time deployment, unlike resource-intensive ensemble methods or multi-sampling approaches. Finally, this work establishes a new evaluation paradigm that moves beyond single-response metrics toward conversation-coherence assessment, better reflecting real-world usage patterns of conversational AI systems.

## 3. Methodology

### 3.1 Semantic Consistency Graph Construction

The foundation of our approach is the dynamic construction of Semantic Consistency Graphs that evolve as conversations progress. We formalize the SCG as a directed, weighted graph $G_t = (V_t, E_t, W_t)$ at conversation turn $t$, where:

- $V_t = \{c_1, c_2, ..., c_n\}$ represents the set of atomic claims extracted from all responses up to turn $t$
- $E_t \subseteq V_t \times V_t$ represents semantic relationships between claims
- $W_t: E_t \rightarrow [-1, 1]$ assigns weights encoding relationship strength and type

**Claim Extraction Pipeline:**

For each LLM response $r_t$ at turn $t$, we extract atomic claims using a two-stage process:

1. **Sentence Decomposition**: Parse $r_t$ into sentences $\{s_1, s_2, ..., s_m\}$ using dependency parsing
2. **Atomic Claim Generation**: For each sentence $s_i$, apply a fine-tuned T5-based model to generate atomic, self-contained claims $\{c_{i,1}, c_{i,2}, ..., c_{i,k}\}$

The claim extraction model is trained on a curated dataset of conversational responses with human-annotated atomic claims. We employ instruction-tuning with prompts like: "Extract atomic, verifiable claims from: [sentence]. Each claim should be independently understandable without context."

**Edge Weight Computation:**

For each pair of claims $(c_i, c_j)$, we compute the edge weight $w_{ij}$ through a hybrid approach:

$$w_{ij} = \alpha \cdot \text{sim}(c_i, c_j) + (1-\alpha) \cdot \text{NLI}(c_i, c_j)$$

where:
- $\text{sim}(c_i, c_j)$ is the cosine similarity between semantic embeddings using SentenceBERT
- $\text{NLI}(c_i, c_j) \in \{-1, 0, 1\}$ represents contradiction, neutrality, or entailment from a natural language inference model
- $\alpha \in [0,1]$ is a tunable parameter balancing semantic similarity and logical relationship (default $\alpha = 0.4$)

This formulation captures both semantic proximity and logical consistency, with $w_{ij} \approx 1$ indicating strong support, $w_{ij} \approx 0$ indicating independence, and $w_{ij} \approx -1$ indicating contradiction.

### 3.2 Graph-Based Inconsistency Detection

**Local Inconsistency Identification:**

We identify inconsistency patterns through spectral analysis of the graph Laplacian. Define the normalized Laplacian:

$$\mathcal{L} = I - D^{-1/2}WD^{-1/2}$$

where $D$ is the degree matrix and $W$ is the weighted adjacency matrix. Claims involved in contradictions exhibit high Dirichlet energy:

$$E_D(c_i) = \sum_{j \in N(i)} w_{ij}(f_i - f_j)^2$$

where $f_i$ is the embedding of claim $c_i$ and $N(i)$ denotes the neighborhood of node $i$.

**Contradiction Cluster Detection:**

We apply a modified Louvain community detection algorithm to identify clusters of mutually contradicting claims. The modularity function is adapted to prioritize negative-weight edges:

$$Q = \frac{1}{2m}\sum_{ij}\left[w_{ij} - \frac{k_ik_j}{2m}\right]\delta(c_i, c_j) \cdot \mathbb{I}(w_{ij} < -\tau)$$

where $\tau$ is a contradiction threshold (default $\tau = 0.3$), $k_i$ is the degree of node $i$, $m$ is the total edge weight, and $\delta(c_i, c_j)$ indicates community membership.

**Temporal Inconsistency Scoring:**

For each new claim $c_t$ introduced at turn $t$, we compute a temporal inconsistency score:

$$\text{TI}(c_t) = \frac{1}{|V_{t-1}|}\sum_{c_i \in V_{t-1}} \max(0, -w_{ti}) \cdot \exp\left(-\frac{t - \tau(c_i)}{\lambda}\right)$$

where $\tau(c_i)$ is the turn when claim $c_i$ was introduced, and $\lambda$ is a temporal decay parameter controlling how much historical claims influence current inconsistency (default $\lambda = 5$ turns).

### 3.3 Conversation-Level Uncertainty Quantification

We aggregate local inconsistencies into conversation-level uncertainty scores through multiple dimensions:

**Claim-Level Uncertainty:**

For each claim $c_i$, define:

$$U_{\text{claim}}(c_i) = \beta_1 \cdot E_D(c_i) + \beta_2 \cdot \frac{|\{j: w_{ij} < -\tau\}|}{|V|} + \beta_3 \cdot \text{entropy}(\mathbf{w}_i)$$

where $\mathbf{w}_i$ is the vector of edge weights from $c_i$, and $\beta_1, \beta_2, \beta_3$ are learned weights.

**Turn-Level Uncertainty:**

For turn $t$, aggregate uncertainties of all claims introduced:

$$U_{\text{turn}}(t) = \frac{1}{|C_t|}\sum_{c_i \in C_t} U_{\text{claim}}(c_i) + \gamma \cdot \max_{c_i \in C_t} U_{\text{claim}}(c_i)$$

where $C_t$ is the set of claims from turn $t$, and $\gamma$ weights the importance of maximum uncertainty.

**Conversation-Level Uncertainty:**

Overall conversation uncertainty at turn $T$:

$$U_{\text{conv}}(T) = \frac{1}{T}\sum_{t=1}^T U_{\text{turn}}(t) + \delta \cdot \frac{|\text{contradiction\_clusters}|}{|V_T|}$$

where $\delta$ weights the proportion of claims involved in contradiction clusters.

### 3.4 Experimental Design

**Dataset Construction:**

We will create a comprehensive benchmark dataset comprising:

1. **Synthetic Contradictory Dialogues**: 5,000 conversations with programmatically injected contradictions across varying temporal distances (2-20 turns apart)
2. **Human-Annotated Conversations**: 2,000 real LLM conversations from domains including medical consultations (simulated), legal advice, technical support, and educational tutoring, with expert annotations of contradictions and hallucinations
3. **Adversarial Dialogues**: 1,000 conversations designed to elicit contradictions through adversarial prompting strategies

**Baseline Comparisons:**

We will compare SCG against:
- Single-response hallucination detectors (perplexity-based, SelfCheckGPT)
- Semantic embedding-based uncertainty quantification (Grewal et al., 2024)
- Multi-dimensional uncertainty frameworks (Chen et al., 2025)
- Graph signal processing approaches (Noël, 2025) applied per-turn

**Evaluation Metrics:**

1. **Contradiction Detection**: Precision, Recall, F1-score for identifying contradictory claim pairs
2. **Temporal Accuracy**: Mean temporal distance error for detected contradictions
3. **Conversation-Level AUC**: Area under ROC curve for conversations classified as consistent/inconsistent
4. **Computational Efficiency**: Time complexity per turn, memory footprint
5. **Interpretability**: Human evaluation of explanation quality (20 expert annotators rating clarity and usefulness on 5-point Likert scale)

**Ablation Studies:**

- Impact of claim extraction quality
- Effectiveness of semantic similarity vs. NLI components
- Temporal decay parameter sensitivity
- Graph size and pruning strategies for efficiency

### 3.5 Implementation Details

The framework will be implemented in Python using PyTorch for neural components and NetworkX for graph operations. Claim extraction will use fine-tuned Flan-T5-Base (250M parameters). Semantic embeddings will use all-MiniLM-L6-v2 (22M parameters). NLI will use a fine-tuned DeBERTa-v3-base model. All experiments will be conducted on NVIDIA A100 GPUs with systematic hyperparameter optimization using Optuna.

## 4. Expected Outcomes & Impact

### Expected Outcomes

**Technical Contributions:**

1. **Scalable Hallucination Detection Framework**: A computationally efficient system capable of processing multi-turn conversations in real-time (target: <500ms per turn for conversations up to 50 turns)

2. **Novel Uncertainty Metrics**: A suite of interpretable uncertainty scores capturing temporal, semantic, and logical consistency dimensions with theoretical grounding in graph theory and information theory

3. **Benchmark Dataset**: The first comprehensive dataset specifically designed for evaluating longitudinal consistency in conversational AI, with fine-grained annotations enabling reproducible research

4. **Empirical Validation**: Demonstrated improvements over single-response baselines with expected 15-25% relative improvement in F1-score for contradiction detection and 30-40% improvement in early detection (identifying contradictions before they cascade)

**Interpretability and Explainability:**

The SCG framework provides inherently interpretable explanations by visualizing subgraphs of contradictory claims. Users can:
- Identify which specific claims contradict each other
- Trace the temporal evolution of inconsistencies
- Understand the severity through quantitative uncertainty scores
- Receive actionable insights about when to seek human verification

### Impact on Reliable AI Deployment

**High-Stakes Domain Applications:**

In healthcare, the framework can flag when an AI medical assistant provides inconsistent diagnostic suggestions, preventing potential harm. In legal consultations, it can identify when advice contradicts across conversation turns, prompting lawyer review. In financial advising, it can detect when recommendations about risk tolerance or investment strategies are inconsistent.

**Advancing Uncertainty Quantification Theory:**

This work extends uncertainty quantification from single predictions to temporal sequences, introducing graph-theoretic perspectives to conversational AI reliability. The theoretical framework provides foundations for future research on:
- Causal consistency in generative models
- Temporal knowledge boundaries in LLMs
- Multi-agent conversation consistency

**Industry and Societal Impact:**

By providing practical tools for detecting unreliable LLM behavior in conversational contexts, this research:
- Reduces liability risks for organizations deploying conversational AI
- Enhances user trust through transparency about model limitations
- Enables safer human-AI collaboration in critical decision-making
- Establishes best practices for conversational AI evaluation

**Open Research Directions:**

This work opens several research avenues:
- Extension to multimodal consistency (vision-language contradictions)
- Active learning strategies for soliciting clarifying information when uncertainty is high
- Personalized consistency standards based on user expertise and risk tolerance
- Cross-lingual consistency tracking in multilingual conversations

### Broader Implications

The SCG framework represents a paradigm shift from instantaneous to longitudinal evaluation of AI systems. As foundation models become increasingly conversational and agentic, tools for tracking consistency across extended interactions will be essential. This research establishes foundational methodologies, metrics, and benchmarks that can generalize beyond LLMs to other sequential decision-making AI systems, including embodied agents, recommendation systems, and autonomous vehicles where temporal consistency is paramount for safety and reliability.

By addressing the critical gap between single-response accuracy and conversation-level coherence, this research contributes to the broader vision of trustworthy AI systems that can reliably operate in high-stakes, real-world applications while maintaining appropriate epistemic humility about their limitations.