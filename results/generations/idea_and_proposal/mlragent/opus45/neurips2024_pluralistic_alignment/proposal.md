# Research Proposal: Democratic Reward Aggregation via Liquid Democracy for Pluralistic AI Alignment

## 1. Introduction

### Background

The alignment of artificial intelligence systems with human values and preferences has emerged as one of the most pressing challenges in contemporary AI research. As large language models (LLMs) and other AI systems become increasingly integrated into decision-making processes affecting millions of people, ensuring these systems reflect the diverse tapestry of human values becomes paramount. Current alignment methodologies, predominantly Reinforcement Learning from Human Feedback (RLHF), typically aggregate human preferences through simplistic mechanisms such as majority voting or arithmetic averaging. While computationally tractable, these approaches suffer from fundamental limitations: they systematically marginalize minority viewpoints, collapse nuanced disagreements into false consensus, and fail to preserve the structured nature of value pluralism that characterizes real human societies.

Recent scholarship has begun to address these limitations. Sorensen et al. (2024) proposed a roadmap distinguishing between Overton, steerable, and distributional pluralism, providing conceptual clarity for the field. Adams et al. (2025) introduced steerable pluralistic models using few-shot comparative regression, while Srewa et al. (2025) leveraged federated learning to preserve privacy while achieving pluralistic alignment. Micha (2025) developed axiomatic approaches to reward design, revealing limitations in standard aggregation methods. Despite these advances, a critical gap remains: existing methods lack mechanisms for structured delegation of preference authority—a feature that has proven essential in human governance systems for balancing individual voice with collective efficiency.

Human societies have long grappled with the challenge of aggregating diverse preferences into collective decisions. Among the governance innovations developed to address this challenge, liquid democracy stands out as particularly promising for AI alignment contexts. In liquid democracy, individuals may either vote directly on issues or delegate their voting power to trusted representatives, who may further delegate, creating transitive chains of trust. This system combines the legitimacy of direct democracy with the efficiency and expertise-leveraging capabilities of representative systems. Crucially, liquid democracy naturally preserves minority clusters—groups with coherent but minority viewpoints maintain their collective voice rather than being diluted through averaging.

### Research Objectives

This research proposes to develop and evaluate a novel reward modeling framework for pluralistic AI alignment inspired by liquid democracy principles. Our specific objectives are:

1. **Design a delegation-based preference aggregation system** where human annotators can either provide direct preference labels or delegate their judgment to trusted annotators on specific topics, constructing a dynamic delegation graph.

2. **Develop a graph neural network architecture** that propagates preference signals through the delegation network while explicitly preserving minority value coalitions rather than collapsing to majority consensus.

3. **Create multi-head reward models** that maintain distinct reward signals for identified value coalitions, enabling controllable generation aligned with specific stakeholder communities.

4. **Validate the framework** through comprehensive experiments demonstrating improved representation of structured disagreement and enhanced controllability compared to baseline approaches.

### Significance

This research bridges governance theory with machine learning practice, offering several significant contributions. First, it provides a principled mechanism for incorporating diverse stakeholder input that respects both individual autonomy and collective efficiency. Second, it addresses the key challenge identified in the literature regarding the scalability of pluralistic models by leveraging delegation to reduce annotation burden while maintaining representational fidelity. Third, by preserving distinct value coalitions rather than forcing artificial consensus, our approach enables downstream applications to make explicit, transparent choices about whose values to prioritize in specific contexts—a crucial capability for accountable AI deployment.

## 2. Methodology

### 2.1 Data Collection and Delegation Graph Construction

#### Annotator Recruitment and Profiling
We recruit a diverse pool of $N$ annotators stratified across demographic dimensions (age, geography, political orientation, cultural background) and domain expertise. Each annotator $a_i$ completes an initial values survey based on established instruments (Schwartz Values Survey, Moral Foundations Questionnaire) producing a value profile vector $\mathbf{v}_i \in \mathbb{R}^d$.

#### Preference Annotation with Delegation Option
For each prompt-response pair $(x, y_1, y_2)$ requiring preference judgment, annotators choose between:
- **Direct voting**: Providing preference label $p_i \in \{y_1 \succ y_2, y_2 \succ y_1, \text{tie}\}$
- **Delegation**: Selecting a trusted delegate $a_j$ for this judgment, optionally specifying topic scope

#### Delegation Graph Construction
We construct a directed weighted graph $G = (V, E, W)$ where:
- Vertices $V = \{a_1, ..., a_N\}$ represent annotators
- Edge $(a_i, a_j) \in E$ exists if $a_i$ has delegated to $a_j$
- Edge weight $w_{ij}$ reflects delegation frequency and topic similarity:

$$w_{ij} = \frac{n_{ij}}{n_i} \cdot \text{sim}(\mathbf{v}_i, \mathbf{v}_j)$$

where $n_{ij}$ is the number of times $a_i$ delegated to $a_j$, $n_i$ is $a_i$'s total delegations, and $\text{sim}(\cdot, \cdot)$ is cosine similarity between value profiles.

#### Topic-Conditioned Delegation
Recognizing that trust may be topic-specific, we partition the prompt space into $K$ topics using clustering on prompt embeddings. Each annotator maintains topic-specific delegation preferences, yielding $K$ delegation subgraphs $\{G^{(k)}\}_{k=1}^K$.

### 2.2 Graph Neural Network for Preference Propagation

#### Preference Signal Initialization
For prompt-response pair $t$, we initialize preference signals for annotators who voted directly:

$$\mathbf{h}_i^{(0)}(t) = \begin{cases} \text{embed}(p_i^t) & \text{if } a_i \text{ voted directly} \\ \mathbf{0} & \text{if } a_i \text{ delegated} \end{cases}$$

where $\text{embed}(\cdot)$ maps preference labels to learned embeddings.

#### Delegation-Aware Message Passing
We develop a novel message-passing scheme that propagates preferences through delegation chains while preserving minority clusters. At layer $\ell$:

$$\mathbf{m}_i^{(\ell)} = \sum_{j \in \mathcal{D}(i)} \alpha_{ij}^{(\ell)} \mathbf{h}_j^{(\ell-1)}$$

where $\mathcal{D}(i)$ denotes annotators to whom $a_i$ has delegated (direct and transitive), and attention weights are computed as:

$$\alpha_{ij}^{(\ell)} = \frac{\exp(\text{score}(\mathbf{h}_i^{(\ell-1)}, \mathbf{h}_j^{(\ell-1)}, w_{ij}))}{\sum_{k \in \mathcal{D}(i)} \exp(\text{score}(\mathbf{h}_i^{(\ell-1)}, \mathbf{h}_k^{(\ell-1)}, w_{ik}))}$$

The score function incorporates both learned compatibility and edge weights:

$$\text{score}(\mathbf{h}_i, \mathbf{h}_j, w_{ij}) = \mathbf{W}_q \mathbf{h}_i \cdot \mathbf{W}_k \mathbf{h}_j + \lambda \log(w_{ij})$$

#### Cluster-Preserving Regularization
To prevent minority viewpoints from being overwhelmed during propagation, we introduce a cluster-preservation loss. Let $\{C_1, ..., C_M\}$ be value coalitions identified via spectral clustering on the delegation graph. We regularize:

$$\mathcal{L}_{\text{cluster}} = -\sum_{m=1}^M \log \frac{\sum_{i,j \in C_m} \text{sim}(\mathbf{h}_i^{(L)}, \mathbf{h}_j^{(L)})}{\sum_{i \in C_m, k \notin C_m} \text{sim}(\mathbf{h}_i^{(L)}, \mathbf{h}_k^{(L)})}$$

This encourages intra-cluster coherence while maintaining inter-cluster distinctiveness.

### 2.3 Multi-Head Reward Model Training

#### Coalition Identification
Using the final-layer representations $\{\mathbf{h}_i^{(L)}\}$, we identify $M$ stable value coalitions through community detection on the similarity graph. Each coalition $C_m$ represents a coherent value perspective.

#### Multi-Head Architecture
We train a reward model with $M$ coalition-specific heads plus one aggregate head:

$$R_m(x, y) = \text{MLP}_m(\text{LM}(x, y))$$

where $\text{LM}(\cdot)$ is a frozen language model encoder. The aggregate reward is:

$$R_{\text{agg}}(x, y) = \sum_{m=1}^M \phi_m R_m(x, y)$$

with coalition weights $\phi_m$ determined by delegation-weighted coalition sizes.

#### Training Objective
For each preference pair, the loss combines coalition-specific and aggregate terms:

$$\mathcal{L}_{\text{reward}} = \sum_{m=1}^M \sum_{t \in T_m} -\log \sigma(R_m(x^t, y_w^t) - R_m(x^t, y_l^t)) + \mathcal{L}_{\text{cluster}}$$

where $T_m$ contains preference pairs with dominant signal from coalition $C_m$, and $(y_w, y_l)$ denotes preferred and dispreferred responses.

### 2.4 Experimental Design

#### Datasets
We conduct experiments on three datasets:
1. **Anthropic HH-RLHF**: Standard alignment dataset, augmented with simulated delegation structure
2. **GlobalOpinionQA**: Cross-cultural opinion dataset with natural value diversity
3. **Custom Pluralistic Corpus**: New dataset collected using our delegation protocol with 500 annotators across 10 countries

#### Baselines
- **Majority Vote Aggregation**: Standard RLHF with preference averaging
- **Federated Learning (PluralLLM)**: Privacy-preserving distributed training
- **Steerable Pluralism**: Few-shot adaptation approach
- **Mixture of Experts**: Per-annotator reward heads without delegation structure

#### Evaluation Metrics
1. **Coalition Representation Fidelity (CRF)**: Measures how well identified coalitions correspond to ground-truth value clusters:
$$\text{CRF} = \text{NMI}(\hat{C}, C^*)$$

2. **Minority Preservation Score (MPS)**: Proportion of minority preferences correctly ranked by coalition-specific heads

3. **Controllability Index (CI)**: Correlation between selected coalition head and generated content alignment

4. **Delegation Efficiency (DE)**: Reduction in annotation burden versus accuracy trade-off

5. **Downstream Task Performance**: Win rates in human evaluation comparing generations from different reward heads

#### Experimental Protocol
We conduct ablation studies examining: (1) impact of delegation graph structure, (2) number of GNN layers, (3) cluster-preservation regularization strength, and (4) coalition granularity. Statistical significance is assessed via bootstrap confidence intervals with $n=1000$ resamples.

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following key outcomes from this research:

**Technical Contributions**: A fully-specified algorithmic framework for delegation-based reward modeling, including open-source implementations of the delegation graph construction, GNN architecture, and multi-head reward model. We expect to demonstrate that our approach achieves 15-25% improvement in minority preservation scores compared to majority-vote baselines while maintaining competitive aggregate performance.

**Empirical Findings**: Comprehensive experimental results demonstrating the conditions under which liquid democracy-inspired aggregation outperforms alternatives, including analysis of optimal delegation graph density, coalition granularity, and the relationship between annotator diversity and model pluralism.

**Dataset Contributions**: A novel pluralistic preference dataset with explicit delegation structure, enabling future research on structured preference aggregation. This dataset will include rich metadata on annotator values, enabling analysis of delegation patterns across demographic and ideological dimensions.

**Theoretical Insights**: Analysis connecting our approach to social choice theory, including characterization of which axioms (e.g., Pareto efficiency, non-dictatorship) are satisfied by our aggregation mechanism.

### Broader Impact

This research addresses fundamental challenges in AI governance and democratic technology design. By providing mechanisms for structured representation of diverse values, our framework enables:

1. **Accountable Pluralism**: Rather than hiding value trade-offs within opaque aggregation, our multi-head approach makes value coalitions explicit, enabling transparent discussion of whose values AI systems should prioritize in specific contexts.

2. **Scalable Participation**: The delegation mechanism allows broad participation without requiring every stakeholder to evaluate every decision, addressing the scalability challenge identified in prior work while maintaining representational legitimacy.

3. **Minority Protection**: By explicitly preserving minority clusters, our approach addresses concerns about AI systems systematically marginalizing underrepresented perspectives—a crucial consideration for equitable AI deployment.

4. **Interdisciplinary Bridge**: This work demonstrates how governance innovations can inform technical AI systems, potentially inspiring further cross-pollination between political science, social choice theory, and machine learning.

The proposed framework has direct applications in content moderation, personalized recommendation systems, and any domain where AI must navigate genuine value pluralism. By grounding technical development in democratic theory, we contribute to the broader project of developing AI systems that genuinely serve diverse human communities.