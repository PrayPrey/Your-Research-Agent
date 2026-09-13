# Temporal Dataset Cards: Version-Aware Documentation for Evolving ML Datasets

## 1. Title

**Temporal Dataset Cards: A Version-Aware Documentation Framework for Tracking, Propagating, and Managing Evolving Machine Learning Datasets**

## 2. Introduction

### 2.1 Background

The machine learning research ecosystem has increasingly recognized datasets as fundamental artifacts that profoundly influence research outcomes, model development, and benchmarking practices. However, current dataset documentation practices operate under a problematic assumption: that datasets are static, immutable objects. In reality, widely-used ML datasets undergo continuous evolution through bug fixes, sample additions or removals, annotation corrections, and quality improvements. This disconnect between documentation practices and dataset reality creates a reproducibility crisis where researchers citing "the same dataset" may actually be working with substantially different data artifacts.

Recent studies have exposed the severity of this issue. Research on recommender systems datasets revealed that papers claiming to use identical datasets often produced incomparable results due to undocumented dataset versions (van den Akker et al., 2021). The problem extends beyond individual research groups—major dataset repositories including UCI Machine Learning Repository, HuggingFace Datasets, and OpenML currently lack comprehensive mechanisms for tracking dataset evolution, propagating critical updates, and linking specific versions to research outcomes.

The consequences of this gap are multifaceted. First, **reproducibility suffers** when papers fail to specify exact dataset versions, making it impossible to replicate experiments precisely. Second, **quality issues persist** as discoveries of biases, consent violations, or annotation errors in datasets are not systematically propagated to users of earlier versions. Third, **dataset deprecation remains ad hoc** without standardized procedures for communicating why datasets should no longer be used and which versions are affected. Fourth, **impact assessment is nearly impossible** as repositories cannot identify which models or papers depend on specific dataset versions.

### 2.2 Research Objectives

This research proposes **Temporal Dataset Cards**, a comprehensive version-aware documentation framework designed to address the complete lifecycle of evolving ML datasets. Our primary objectives are:

1. **Design a temporal metadata layer** that extends existing dataset card frameworks (e.g., Datasheets for Datasets, Dataset Nutrition Labels) with structured version tracking, semantic versioning, and rich changelog documentation.

2. **Develop retrospective annotation mechanisms** that enable critical information discovered post-publication (biases, privacy violations, quality issues) to be backpropagated to all affected dataset versions with appropriate warnings and deprecation notices.

3. **Create automated impact tracing tools** that identify research papers, models, and benchmarks using specific dataset versions and quantify how results vary across versions.

4. **Implement repository integration infrastructure** through APIs and plugins for major ML data repositories (HuggingFace, OpenML, UCI) to enforce version pinning in citations and enable temporal queries.

5. **Establish best practices and guidelines** for dataset versioning, documentation standards, and deprecation procedures that can be adopted across the ML community.

### 2.3 Significance

This research addresses multiple critical themes identified in the workshop call: comprehensive data documentation, best practices for revising and deprecating datasets, dataset reproducibility, repository design challenges, and data curation quality assurance. By providing infrastructure for version-aware dataset management, this work has potential to:

- **Improve research reproducibility** by enabling precise specification and retrieval of exact dataset versions used in experiments
- **Accelerate quality issue propagation** through automated notification systems when problems are discovered
- **Enable longitudinal dataset studies** examining how dataset evolution affects model performance and research conclusions
- **Support better dataset governance** with clear audit trails and deprecation procedures
- **Facilitate meta-research** on dataset usage patterns and their impact on ML research trajectories

The framework is designed to be repository-agnostic and extensible, ensuring broad applicability across diverse ML subdisciplines and data modalities.

## 3. Methodology

### 3.1 Temporal Metadata Layer Design

#### 3.1.1 Core Schema Architecture

We propose extending existing dataset card schemas with a temporal metadata layer structured as follows:

$$
\mathcal{D} = \{V_1, V_2, ..., V_n\}
$$

where each version $V_i$ contains:

$$
V_i = (M_i, \Delta_i, T_i, A_i, S_i)
$$

with:
- $M_i$: Core metadata (authors, description, license)
- $\Delta_i$: Changelog describing transformations from $V_{i-1}$
- $T_i$: Timestamp and semantic version identifier
- $A_i$: Retrospective annotations (warnings, deprecation notices)
- $S_i$: Statistical signature (distribution metrics, sample counts)

The semantic versioning follows the pattern `MAJOR.MINOR.PATCH` where:
- **MAJOR**: Incompatible changes (schema modifications, significant sample alterations)
- **MINOR**: Backward-compatible additions (new samples, features)
- **PATCH**: Bug fixes and corrections (annotation fixes, duplicates removal)

#### 3.1.2 Changelog Specification

Each changelog $\Delta_i$ captures granular operations:

$$
\Delta_i = \{op_1, op_2, ..., op_k\}
$$

where each operation $op_j$ is structured as:

```json
{
  "operation_type": ["ADD", "DELETE", "MODIFY", "SPLIT", "MERGE"],
  "affected_samples": [list of sample identifiers],
  "field": "specific field modified",
  "rationale": "human-readable explanation",
  "impact_level": ["BREAKING", "COMPATIBLE", "PATCH"],
  "timestamp": "ISO 8601 timestamp"
}
```

We will develop automated diff-generation tools that compare successive dataset versions and produce structured changelogs by:

1. Computing content-based hashes for each sample: $h(s) = \text{SHA-256}(s)$
2. Identifying additions: $A = \{s \in V_i : h(s) \notin H_{i-1}\}$
3. Identifying deletions: $D = \{s \in V_{i-1} : h(s) \notin H_i\}$
4. Identifying modifications through fuzzy matching with threshold $\theta$

#### 3.1.3 Statistical Signatures

To enable quantitative version comparison, we compute statistical signatures $S_i$ including:

- **Distribution metrics**: Mean, variance, skewness, kurtosis for numerical features
- **Category distributions**: Frequency tables for categorical variables
- **Label balance**: Class distribution for supervised tasks
- **Correlation structures**: Pairwise feature correlations

Statistical divergence between versions is measured using:

$$
D_{KL}(V_i || V_j) = \sum_{x} P_i(x) \log \frac{P_i(x)}{P_j(x)}
$$

where $P_i(x)$ represents the empirical distribution of feature $x$ in version $V_i$.

### 3.2 Retrospective Annotation System

#### 3.2.1 Annotation Types and Propagation Rules

We define a taxonomy of retrospective annotations:

1. **CRITICAL**: Privacy violations, consent issues, legal concerns
2. **WARNING**: Discovered biases, quality issues, representational harms
3. **DEPRECATION**: Dataset retirement with recommended alternatives
4. **CORRECTION**: Errata for documentation or metadata

Propagation rules determine which versions receive annotations:

$$
\text{Propagate}(a, V_i) = \begin{cases}
\text{True} & \text{if } \text{affected\_samples}(a) \subseteq V_i \\
\text{False} & \text{otherwise}
\end{cases}
$$

#### 3.2.2 Annotation Interface

We will implement a web-based interface allowing dataset maintainers and community members to submit retrospective annotations with required fields:

- Issue description and severity classification
- Affected version range (from version $V_x$ to $V_y$)
- Specific samples or features affected (if applicable)
- Supporting evidence (citations, analysis results)
- Recommended actions for users

Annotations undergo review before propagation, with different approval thresholds based on severity (CRITICAL annotations require maintainer approval, WARNINGS may be community-flagged).

### 3.3 Automated Impact Tracing

#### 3.3.1 Citation Graph Construction

To identify research artifacts using specific dataset versions, we construct a citation graph:

$$
G = (N, E)
$$

where:
- $N = P \cup M \cup D$ (papers, models, datasets)
- $E = \{(n_i, d_j, v_k)\}$ representing node $n_i$ using dataset $d_j$ version $v_k$

We build this graph through:

1. **Automated paper parsing**: Using models like SAVeD (Frenk & Shraga, 2025) to extract dataset citations from papers
2. **Repository metadata extraction**: Querying HuggingFace Hub, Papers With Code, and arXiv
3. **Model card analysis**: Parsing training data declarations from model documentation
4. **DOI resolution**: Tracking dataset DOIs to specific versions

#### 3.3.2 Result Variance Quantification

For papers $P_1, ..., P_m$ reporting results on dataset versions $V_1, ..., V_n$, we quantify cross-version variance:

$$
\sigma^2_{\text{version}} = \frac{1}{n} \sum_{i=1}^{n} (R_i - \bar{R})^2
$$

where $R_i$ is the reported metric (accuracy, F1, etc.) on version $V_i$ and $\bar{R}$ is the mean across versions.

We compute statistical significance using ANOVA:

$$
F = \frac{\text{MS}_{\text{between}}}{\text{MS}_{\text{within}}} = \frac{\sum_{i=1}^{n} n_i(\bar{R}_i - \bar{R})^2/(n-1)}{\sum_{i=1}^{n}\sum_{j=1}^{n_i}(R_{ij} - \bar{R}_i)^2/(N-n)}
$$

to determine whether version differences significantly impact research outcomes.

### 3.4 Repository Integration Infrastructure

#### 3.4.1 API Design

We will develop RESTful APIs with the following core endpoints:

```
GET /datasets/{dataset_id}/versions
  Returns: List of all versions with metadata

GET /datasets/{dataset_id}/versions/{version_id}
  Returns: Specific version with full temporal card

GET /datasets/{dataset_id}/versions/{version_id}/changelog
  Returns: Detailed changelog for specified version

GET /datasets/{dataset_id}/versions/{version_id}/annotations
  Returns: Retrospective annotations for this version

POST /datasets/{dataset_id}/versions/{version_id}/annotations
  Creates: New retrospective annotation

GET /datasets/{dataset_id}/impact?version={version_id}
  Returns: Papers and models using this version

GET /datasets/{dataset_id}/compare?v1={vid1}&v2={vid2}
  Returns: Statistical comparison between versions
```

#### 3.4.2 Repository Plugins

We will implement native plugins for major repositories:

**HuggingFace Datasets Integration**:
- Extend `DatasetInfo` class with temporal metadata fields
- Modify `load_dataset()` to require version specification
- Implement `dataset.version_history()` and `dataset.get_version(v)` methods

**OpenML Integration**:
- Extend dataset metadata schema with temporal layer
- Implement version-aware dataset ID system (e.g., `dataset_id:version`)
- Create OpenML flow versioning linked to dataset versions

**UCI ML Repository Integration**:
- Develop version manifest files stored alongside datasets
- Implement deprecation warning system in download interfaces
- Create temporal metadata viewer for dataset pages

#### 3.4.3 Version Pinning Enforcement

To ensure reproducibility, we implement:

1. **Citation generation tools** that automatically include version identifiers:
   ```
   @dataset{dataset_name_v2.3.1,
     title={Dataset Name},
     version={2.3.1},
     url={https://...},
     DOI={10.xxxx/dataset.v2.3.1}
   }
   ```

2. **Download warnings** when users access datasets without version specification

3. **Dependency management** integration with ML frameworks:
   ```python
   # requirements.txt style
   datasets==2.8.0
   my_dataset==2.3.1
   ```

### 3.5 Data Collection and Experimental Design

#### 3.5.1 Case Study Datasets

We will validate our framework using three case study datasets representing different evolution patterns:

1. **ImageNet**: Major revisions, widespread use, known quality issues
2. **SQuAD**: Multiple versions with different task formulations
3. **Common Crawl**: Continuous updates, massive scale, privacy concerns

For each dataset, we will:
- Reconstruct complete version history from available documentation
- Create temporal dataset cards with full changelog reconstruction
- Apply retrospective annotations for known issues
- Trace impact across research literature

#### 3.5.2 Experimental Validation

**Experiment 1: Reproducibility Improvement**
- Hypothesis: Version-specific citations reduce result variance
- Method: Compare result reproducibility for papers with vs. without version pinning
- Metrics: Standard deviation of reproduced results, reproduction success rate
- Dataset: 50 papers from different ML domains using case study datasets

**Experiment 2: Impact Tracing Accuracy**
- Hypothesis: Automated tracing identifies ≥90% of actual dataset usage
- Method: Compare automated tracing against manual paper review
- Metrics: Precision, recall, F1 for citation extraction
- Dataset: 200 papers from arXiv and major ML conferences

**Experiment 3: Annotation Propagation Effectiveness**
- Hypothesis: Retrospective annotations reach affected users within 30 days
- Method: Track annotation propagation through repository notification systems
- Metrics: Time to notification, user acknowledgment rate
- Dataset: Simulated annotations on case study datasets

**Experiment 4: Statistical Signature Sensitivity**
- Hypothesis: Statistical signatures detect meaningful version differences
- Method: Compute signatures across versions, correlate with reported result variance
- Metrics: Correlation between $D_{KL}$ and performance variance
- Dataset: All versions of case study datasets with multiple benchmark results

**Experiment 5: User Study on Temporal Cards**
- Hypothesis: Temporal cards improve user understanding of dataset evolution
- Method: User study with ML researchers performing version selection tasks
- Metrics: Task completion accuracy, time, satisfaction scores (Likert scale)
- Participants: 30 ML researchers with varying experience levels

#### 3.5.3 Evaluation Metrics

We will evaluate the framework across multiple dimensions:

1. **Technical Performance**:
   - Changelog generation accuracy (precision/recall vs. ground truth)
   - API response time and scalability ($<$ 500ms for version queries)
   - Storage overhead (target $<$ 10% increase over base dataset)

2. **Reproducibility Impact**:
   - Reduction in result variance: $\frac{\sigma^2_{\text{after}} - \sigma^2_{\text{before}}}{\sigma^2_{\text{before}}}$
   - Reproduction success rate improvement
   - Time to successful reproduction

3. **Usability Metrics**:
   - System Usability Scale (SUS) scores from user study
   - Task completion rates for version navigation
   - Adoption rates in participating repositories

4. **Community Adoption**:
   - Number of datasets with temporal cards after 6 months
   - Repository integration completion status
   - Citations of framework in research papers

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

This research is expected to produce the following concrete deliverables:

1. **Temporal Dataset Card Specification**: A comprehensive schema and documentation standard that extends existing dataset card frameworks with version-aware capabilities, including formal specifications, JSON schemas, and validation tools.

2. **Open-Source Software Infrastructure**:
   - Python library for creating, managing, and querying temporal dataset cards
   - Repository plugins for HuggingFace, OpenML, and UCI ML Repository
   - Web-based interfaces for viewing temporal cards and submitting annotations
   - Automated changelog generation and diff tools

3. **Impact Tracing Toolkit**: Tools for automatically identifying papers and models using specific dataset versions, including:
   - Citation extraction models trained on ML literature
   - Result variance quantification algorithms
   - Visualization dashboards showing dataset usage over time

4. **Empirical Findings**: Published analyses demonstrating:
   - Quantified impact of dataset versioning on reproducibility
   - Case studies of how dataset evolution affected research outcomes
   - Patterns in dataset changes across different ML domains
   - Effectiveness of retrospective annotations in propagating quality issues

5. **Community Guidelines**: Best practice recommendations for:
   - When to increment major vs. minor vs. patch versions
   - How to document dataset changes comprehensively
   - Procedures for dataset deprecation and sunsetting
   - Standards for retrospective annotation submission and review

### 4.2 Scientific Impact

The framework addresses fundamental challenges in ML reproducibility and dataset governance:

**For Researchers**: Temporal dataset cards provide precise specification of experimental conditions, enabling exact replication of prior work. Researchers can confidently compare their results to prior work knowing they are using identical data, and can systematically study how model performance varies across dataset versions.

**For Dataset Curators**: The framework provides structured tools for communicating changes, deprecation decisions, and quality issues. Curators gain visibility into how their datasets are used and can responsibly manage dataset lifecycles with clear audit trails.

**For Repository Administrators**: Integration with major repositories establishes standardized versioning infrastructure, reduces support burden from version-related questions, and enables better dataset governance at scale.

**For Meta-Research**: The impact tracing infrastructure enables large-scale studies of how datasets influence research trajectories, which versions become canonical, and how quality issues propagate through the literature.

### 4.3 Practical Impact

Beyond scientific contributions, this work has immediate practical applications:

1. **Improved Benchmark Reliability**: Leaderboards can specify exact dataset versions, eliminating ambiguity about what data was used for evaluation and enabling fair comparisons.

2. **Faster Issue Response**: When biases or privacy violations are discovered, automated propagation ensures all affected users are notified quickly, reducing harm from continued use of problematic data.

3. **Better Resource Allocation**: Funding agencies and institutions can make informed decisions about dataset maintenance by understanding usage patterns and dependencies.

4. **Enhanced Education**: Students learning ML can understand that datasets evolve, developing more sophisticated understanding of data's role in research.

5. **Legal and Ethical Compliance**: Clear version tracking and annotation systems support compliance with data protection regulations (GDPR, CCPA) by documenting consent status, data provenance, and privacy considerations for each version.

### 4.4 Broader Impact and Long-Term Vision

This research contributes to a cultural shift in how the ML community treats data artifacts. By establishing infrastructure that makes version tracking effortless and expected, we move toward a future where:

- **Dataset citations are as precise as software citations**, with version-specific DOIs and BibTeX entries
- **Dataset evolution is transparent and documented**, with rich histories accessible to all users
- **Quality issues are rapidly propagated**, preventing continued harm from problematic datasets
- **Meta-research on datasets is possible**, enabling systematic study of data's influence on ML progress
- **Responsible dataset sunsetting becomes standard**, with clear migration paths when datasets are deprecated

The framework is designed to be extensible to emerging challenges, including:
- Versioning for foundation model training data
- Synthetic data provenance tracking
- Federated dataset version coordination
- Cross-repository version reconciliation

### 4.5 Dissemination and Adoption Strategy

To maximize impact, we will:

1. **Engage repositories early**: Collaborate with HuggingFace, OpenML, and UCI administrators throughout development to ensure practical feasibility and address implementation concerns.

2. **Publish across venues**: Target machine learning conferences (NeurIPS, ICML, ICLR), data management venues (VLDB, SIGMOD), and reproducibility-focused workshops.

3. **Provide migration tooling**: Develop scripts to convert existing datasets to temporal card format, reducing adoption barriers.

4. **Create documentation and tutorials**: Comprehensive guides, video tutorials, and example implementations to onboard users.

5. **Build community**: Establish working groups with dataset maintainers, repository administrators, and researchers to refine standards and coordinate adoption.

6. **Seek standardization**: Work with organizations like MLCommons, W3C, and ISO to establish temporal dataset cards as recognized standards.

By addressing the fundamental gap between static documentation practices and dynamic dataset reality, this research has potential to meaningfully improve reproducibility, transparency, and responsibility in machine learning research. The proposed framework provides practical infrastructure for better dataset governance while establishing conceptual foundations for treating datasets as living artifacts that evolve alongside the research they support.