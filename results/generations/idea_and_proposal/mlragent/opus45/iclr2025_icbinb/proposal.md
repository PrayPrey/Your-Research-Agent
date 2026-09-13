# A Cross-Domain Taxonomy of Deep Learning Failures: From Symptoms to Root Causes

## 1. Introduction

### Background

Deep learning (DL) has achieved remarkable success across numerous benchmark tasks, driving ambitious deployments in real-world applications spanning healthcare, robotics, finance, scientific discovery, and social sciences. However, the transition from controlled laboratory settings to dynamic, real-world conditions frequently reveals practical limitations that benchmark performance fails to anticipate. Models that excel on standardized datasets often exhibit unexpected failures when confronted with distribution shifts, noisy labels, adversarial conditions, or domain-specific constraints that violate underlying assumptions.

The current academic publication ecosystem exacerbates this problem by prioritizing novel methods that achieve state-of-the-art results on established benchmarks, while systematic documentation of failures remains undervalued and fragmented. When failures do surface, discussions typically remain siloed within specific domains—a healthcare researcher struggling with distribution shift may be entirely unaware that roboticists have developed effective solutions for analogous problems. This fragmentation leads to redundant effort, repeated mistakes, and missed opportunities for cross-pollination of diagnostic strategies and solutions.

Existing taxonomies of deep learning faults, while valuable, have focused primarily on software engineering perspectives (Humbatova et al., 2019) or domain-specific issues such as deep reinforcement learning (Nikanjam et al., 2021) and technical debt (Pepe et al., 2024). These works provide important foundations but do not bridge the gap between observable symptoms and fundamental root causes in a manner that enables systematic knowledge transfer across application domains.

### Research Objectives

This research proposes to develop a comprehensive, hierarchical taxonomy that maps deep learning failures from observable symptoms to underlying root causes across diverse application domains. The primary objectives are:

1. **Systematic Aggregation**: Collect and curate failure cases from published literature, workshop submissions (including ICBINB proceedings), and structured practitioner interviews across at least five major application domains.

2. **Hierarchical Classification**: Develop a three-tier taxonomy that links (a) observable failure symptoms, (b) proximate causes, and (c) fundamental root causes, enabling researchers to diagnose issues systematically.

3. **Cross-Domain Mapping**: Identify isomorphic failure patterns that manifest differently across domains but share common underlying mechanisms, cataloging existing solutions with transfer potential.

4. **Open-Source Infrastructure**: Create a searchable, community-maintained database that links failure types to potential mitigations, enabling rapid troubleshooting and collaborative problem-solving.

### Significance

This research addresses a critical gap in the machine learning ecosystem by transforming isolated failure cases into actionable, transferable knowledge. By establishing a common vocabulary and diagnostic framework, researchers across domains can leverage collective experience rather than rediscovering known pitfalls. The taxonomy will accelerate debugging workflows, inform more robust model design, and foster a culture of transparency that advances both the science and practice of deep learning deployment.

## 2. Methodology

### 2.1 Data Collection

#### Literature Mining

We will conduct a systematic review of failure-related publications using a structured protocol:

**Search Strategy**: Query academic databases (Google Scholar, Semantic Scholar, arXiv, ACM Digital Library, IEEE Xplore) using keywords including "deep learning failure," "neural network debugging," "model degradation," "deployment challenges," combined with domain-specific terms for each target area.

**Inclusion Criteria**: Papers must (1) describe a concrete deep learning application, (2) document unexpected or suboptimal outcomes, and (3) provide analysis of contributing factors. We will include both peer-reviewed publications and technical reports from 2015-2024.

**Domain Coverage**: We target five primary domains with distinct characteristics:
- **Healthcare**: Medical imaging, clinical decision support, drug discovery
- **Robotics**: Autonomous navigation, manipulation, human-robot interaction
- **Scientific Discovery**: Physics simulations, materials science, genomics
- **Finance**: Risk modeling, fraud detection, algorithmic trading
- **Social Sciences**: Behavioral prediction, recommendation systems, natural language understanding

**Extraction Template**: For each case, we will extract: (1) application context, (2) model architecture, (3) training/deployment setup, (4) observed failure symptoms, (5) hypothesized causes, (6) attempted mitigations, and (7) outcome of mitigations.

#### Workshop Submission Analysis

We will analyze submissions to ICBINB and related workshops (ML4Health, AI4Science, Robust ML) that document negative results. With appropriate permissions, we will apply the same extraction template to build a complementary dataset of practitioner-reported failures.

#### Semi-Structured Interviews

We will conduct 30-40 semi-structured interviews with ML practitioners across target domains (6-8 per domain). Interview protocols will cover:
- Description of recent deployment challenges
- Diagnostic process and timeline
- Root cause identification (if achieved)
- Solutions attempted and their effectiveness
- Resources consulted during troubleshooting

Interviews will be recorded, transcribed, and coded using qualitative analysis software (NVivo) to identify emergent themes.

### 2.2 Taxonomy Development

#### Hierarchical Structure

We propose a three-tier taxonomy connecting observable symptoms to root causes:

**Tier 1: Observable Symptoms ($S$)**
Observable manifestations that indicate model failure, formalized as:
$$S = \{s_1, s_2, ..., s_n\}$$
where each symptom $s_i$ represents a measurable deviation from expected behavior. Examples include:
- Performance degradation (accuracy drop $\Delta_{acc} > \epsilon$ on new data)
- Prediction instability (high variance $\sigma^2(\hat{y})$ across similar inputs)
- Calibration failure (expected calibration error $ECE > \tau$)
- Latency violations (inference time $t_{inf} > t_{max}$)
- Fairness violations (demographic parity difference $|P(\hat{y}=1|A=0) - P(\hat{y}=1|A=1)| > \delta$)

**Tier 2: Proximate Causes ($P$)**
Immediate technical factors that produce observed symptoms:
$$P = \{p_1, p_2, ..., p_m\}$$
Examples include:
- Covariate shift: $P_{train}(X) \neq P_{test}(X)$
- Label noise: $P(Y_{observed}|X) \neq P(Y_{true}|X)$
- Concept drift: $P_t(Y|X) \neq P_{t'}(Y|X)$ for $t \neq t'$
- Representation collapse: $\text{rank}(H) \ll d$ where $H$ is the hidden representation matrix
- Optimization pathologies: $\|\nabla_\theta \mathcal{L}\| \approx 0$ at non-optimal points

**Tier 3: Root Causes ($R$)**
Fundamental issues in data, model design, or deployment context:
$$R = \{r_1, r_2, ..., r_k\}$$
Examples include:
- Assumption violations (i.i.d. assumption, stationarity, smoothness)
- Insufficient inductive bias for task structure
- Measurement system limitations
- Computational budget constraints
- Sociotechnical misalignment

#### Mapping Functions

We define probabilistic mapping functions between tiers:

**Symptom-to-Proximate**: $P(p_j | s_i, \text{context})$ estimates the likelihood that proximate cause $p_j$ underlies symptom $s_i$ given contextual information (domain, model type, data characteristics).

**Proximate-to-Root**: $P(r_k | p_j, \text{context})$ estimates the likelihood that root cause $r_k$ produces proximate cause $p_j$.

These mappings will be estimated from our collected data using:
$$P(p_j | s_i) = \frac{N(s_i, p_j) + \alpha}{\sum_{j'} N(s_i, p_{j'}) + m\alpha}$$

where $N(s_i, p_j)$ counts co-occurrences in our dataset and $\alpha$ is a smoothing parameter.

#### Cross-Domain Pattern Identification

To identify isomorphic patterns across domains, we compute similarity matrices for failure patterns:

$$\text{Sim}(f_a, f_b) = \frac{|\text{causes}(f_a) \cap \text{causes}(f_b)|}{|\text{causes}(f_a) \cup \text{causes}(f_b)|} \times w_{symptom} + \frac{|\text{mitigations}(f_a) \cap \text{mitigations}(f_b)|}{|\text{mitigations}(f_a) \cup \text{mitigations}(f_b)|} \times w_{mitigation}$$

where $f_a$ and $f_b$ are failure cases from different domains, and $w_{symptom}$, $w_{mitigation}$ are weights determined through validation.

Hierarchical clustering on the similarity matrix will reveal failure archetypes that transcend domain boundaries.

### 2.3 Experimental Validation

#### Taxonomy Coverage and Consistency

**Inter-rater Reliability**: Three trained annotators will independently classify a held-out set of 100 failure cases using the taxonomy. We will measure:
- Cohen's kappa ($\kappa$) for pairwise agreement
- Fleiss' kappa for multi-annotator agreement
- Target: $\kappa > 0.7$ indicating substantial agreement

**Coverage Analysis**: We will compute the proportion of failure cases that can be fully classified within the taxonomy, targeting $>90\%$ coverage with clear extension mechanisms for novel categories.

#### Diagnostic Utility Evaluation

We will evaluate whether the taxonomy accelerates failure diagnosis through a controlled user study:

**Participants**: 40 ML practitioners (graduate students and industry professionals) stratified by experience level.

**Protocol**: Participants receive 10 failure scenarios (5 from familiar domains, 5 from unfamiliar domains) and must identify likely causes. Conditions:
- Control: Access to general ML documentation
- Treatment: Access to taxonomy-based diagnostic tool

**Metrics**:
- Diagnostic accuracy: $\frac{\text{correct cause identifications}}{\text{total scenarios}}$
- Time to diagnosis: seconds from scenario presentation to cause identification
- Solution relevance: expert rating of proposed mitigations (1-5 scale)

**Analysis**: Mixed-effects models accounting for participant experience and scenario difficulty:
$$Y_{ij} = \beta_0 + \beta_1 \text{Condition}_i + \beta_2 \text{Experience}_i + \beta_3 \text{Difficulty}_j + u_i + \epsilon_{ij}$$

#### Cross-Domain Transfer Validation

To validate that the taxonomy enables knowledge transfer, we will:

1. **Solution Transfer Study**: For each identified cross-domain pattern, extract solutions developed in Domain A and evaluate their applicability in Domain B through:
   - Literature review: Has this solution been independently discovered in Domain B?
   - Expert assessment: Domain B practitioners rate solution relevance (1-5)
   - Empirical testing: Where feasible, implement transferred solutions on Domain B failure cases

2. **Prediction Task**: Train a classifier to predict root causes from symptoms using data from $n-1$ domains, evaluate on held-out domain. Compare accuracy to within-domain baselines to quantify transfer benefits.

### 2.4 Infrastructure Development

We will develop an open-source, web-based platform with the following components:

1. **Searchable Database**: PostgreSQL backend with full-text search over failure case descriptions, filterable by domain, symptom, cause, and model type.

2. **Interactive Diagnostic Tool**: Decision-tree interface that guides users from observed symptoms through diagnostic questions to likely causes and recommended mitigations.

3. **Contribution System**: Structured submission forms for community-contributed failure cases with automated validation and expert moderation.

4. **API Access**: RESTful API enabling programmatic queries for integration with debugging workflows.

## 3. Expected Outcomes & Impact

### Direct Deliverables

1. **Comprehensive Taxonomy**: A validated hierarchical classification system covering 50+ symptom types, 30+ proximate causes, and 15+ root cause categories, with documented relationships between tiers.

2. **Annotated Failure Database**: A curated collection of 500+ failure cases across five domains, each annotated with full taxonomy classifications and mitigation outcomes.

3. **Cross-Domain Transfer Catalog**: Documentation of 20+ isomorphic failure patterns with explicit mappings between domain-specific manifestations and transferable solutions.

4. **Open-Source Platform**: A publicly accessible web application and API for taxonomy exploration, failure case submission, and diagnostic support.

5. **Methodological Guidelines**: Best practices documentation for failure case documentation and taxonomy-guided debugging.

### Scientific Impact

This research will establish a foundational framework for systematic study of deep learning failures, enabling:

- **Accelerated Debugging**: By providing structured diagnostic pathways, practitioners can more rapidly identify root causes and appropriate mitigations, reducing time from failure observation to resolution.

- **Cross-Domain Knowledge Transfer**: Explicit mapping of isomorphic patterns will surface solutions developed in one domain that may transfer to others, reducing redundant research effort.

- **Curriculum Development**: The taxonomy provides a structured foundation for teaching ML practitioners about common failure modes and debugging strategies.

- **Research Prioritization**: Frequency analysis of root causes will identify high-impact areas where methodological advances could address multiple failure types simultaneously.

### Community Impact

Aligned with the ICBINB initiative's mission, this work will:

- Foster a culture of transparency by providing infrastructure for sharing negative results
- Reduce stigma around failure documentation by demonstrating its scientific value
- Enable cross-disciplinary collaboration by establishing common vocabulary
- Inform more realistic expectations for deep learning deployment across domains

### Broader Implications

By improving our collective understanding of when and why deep learning fails, this research contributes to:

- **Safer AI Deployment**: Better diagnostic tools enable earlier detection of potential failures in safety-critical applications
- **Resource Efficiency**: Reduced redundant effort in debugging and solution development
- **Equitable AI**: Systematic identification of fairness-related failure patterns across domains

The taxonomy and associated infrastructure will be maintained as a community resource, with governance structures ensuring long-term sustainability and continued relevance as deep learning practice evolves.