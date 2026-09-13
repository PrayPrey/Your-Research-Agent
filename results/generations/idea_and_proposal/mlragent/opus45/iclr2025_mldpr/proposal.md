# Research Proposal: Dynamic Dataset Health Scores: Automated Monitoring for ML Repository Sustainability

## 1. Introduction

### Background

Machine learning (ML) research fundamentally depends on datasets for training, validation, and benchmarking. Major repositories such as HuggingFace Datasets, OpenML, and the UCI ML Repository collectively host tens of thousands of datasets that serve millions of researchers worldwide. However, the ML data ecosystem faces a growing crisis of sustainability and quality assurance. Unlike software packages that benefit from mature dependency management and vulnerability tracking systems, ML datasets lack systematic mechanisms for monitoring their ongoing viability and appropriateness for use.

Recent scholarship has illuminated numerous problems in ML data practices: datasets becoming outdated as real-world distributions shift, benchmark saturation leading to overfitting across the research community, ethical issues remaining undiscovered for years, and datasets becoming "orphaned" when maintainers disengage. The seminal work on datasheets for datasets and data cards represented important steps toward better documentation, yet these remain static artifacts that cannot capture the dynamic nature of dataset health. As Winata et al. (2025) argue in their DataRubrics framework, systematic evaluation metrics must move beyond documentation checklists toward automated, continuous assessment.

The challenge of scalable quality assessment is well-documented. Loizou and Tsoumakos (2025) demonstrated with Chunked Data Shapley that even fundamental data valuation tasks become computationally prohibitive at scale. Similarly, the ECOVAL framework (Chundawat et al., 2024) highlights the need for efficient methods that can operate across large data repositories. Current repository practices rely predominantly on reactive measures—responding to user reports, occasional audits, or high-profile exposés of problematic datasets. This approach fundamentally fails to scale and allows silent degradation of the data ecosystem.

### Research Objectives

This research proposes **Dynamic Dataset Health Scores (DDHS)**, a comprehensive automated monitoring system designed to continuously assess and communicate dataset health across multiple dimensions. Our primary objectives are:

1. To develop a multi-dimensional health scoring framework that captures usage patterns, temporal freshness, documentation completeness, maintainer engagement, and ethical considerations.

2. To design scalable algorithms capable of computing health metrics across repositories containing thousands of datasets with minimal computational overhead.

3. To create an integration architecture that enables seamless deployment on existing ML repository platforms.

4. To validate the system's effectiveness through empirical evaluation and user studies demonstrating improved dataset selection decisions.

### Significance

This research addresses a critical gap in the ML data ecosystem by transforming dataset quality assessment from a static, manual process into a dynamic, automated system. By providing researchers with actionable health indicators, DDHS can guide users toward well-maintained datasets, incentivize better data stewardship through transparency, and provide repository administrators with prioritized curation insights. The workshop's emphasis on FAIR and AI-ready datasets, best practices for deprecation, and benchmark overuse makes this research particularly timely and aligned with community needs.

## 2. Methodology

### 2.1 Overall System Architecture

DDHS comprises five interconnected monitoring modules, an aggregation engine, and a presentation layer. Each module operates independently with configurable update frequencies, enabling efficient resource utilization while maintaining current health assessments.

### 2.2 Health Dimension Modules

#### 2.2.1 Usage Saturation Index (USI)

The Usage Saturation Index monitors citation and download patterns to identify benchmark overuse that may indicate community-level overfitting. We define the USI for dataset $d$ at time $t$ as:

$$USI_d(t) = \alpha \cdot C_d(t) + \beta \cdot D_d(t) + \gamma \cdot P_d(t)$$

where $C_d(t)$ represents normalized citation velocity, $D_d(t)$ represents download concentration (Gini coefficient of downloads across time windows), and $P_d(t)$ represents publication saturation (ratio of papers using $d$ to total papers in its domain). Parameters $\alpha$, $\beta$, and $\gamma$ are learned weights optimized through historical analysis of deprecated benchmarks.

Citation velocity is computed as:

$$C_d(t) = \frac{1}{|W|} \sum_{w \in W} \frac{n_w^{cite}}{n_w^{domain}} \cdot \log\left(\frac{t - t_0}{365}\right)$$

where $W$ represents sliding time windows, $n_w^{cite}$ is citations in window $w$, $n_w^{domain}$ is total domain citations, and $t_0$ is the dataset creation date. The logarithmic age factor penalizes datasets that continue accumulating disproportionate usage over extended periods.

#### 2.2.2 Freshness Score (FS)

The Freshness Score assesses temporal drift between a dataset's characteristics and current domain distributions. For datasets in domains with available reference distributions (e.g., web text, image classifications), we compute:

$$FS_d(t) = 1 - \min\left(1, \frac{D_{KL}(P_d || Q_t)}{\tau_d}\right)$$

where $P_d$ is the dataset's distribution, $Q_t$ is an estimated current domain distribution, and $\tau_d$ is a domain-specific threshold. For text datasets, we utilize embedding-based distribution estimation:

$$D_{KL}(P_d || Q_t) \approx \frac{1}{n} \sum_{i=1}^{n} \log \frac{p(e_i | \theta_d)}{p(e_i | \theta_t)}$$

where $e_i$ represents embeddings from a frozen encoder and $\theta_d$, $\theta_t$ are fitted density estimators.

For datasets where reference distributions are unavailable, we employ proxy freshness indicators: metadata currency (schema updates, format modernization), linked resource availability (URLs, external references), and comparative recency within the dataset's category.

#### 2.2.3 Documentation Completeness Score (DCS)

We extend the DataRubrics framework (Winata et al., 2025) to provide automated, continuous documentation assessment. Our scoring function evaluates coverage across mandatory and recommended fields:

$$DCS_d = \sum_{i=1}^{M} w_i^{mand} \cdot \mathbb{1}[f_i^{mand} \text{ present}] + \sum_{j=1}^{R} w_j^{rec} \cdot q(f_j^{rec})$$

where $\mathbb{1}[\cdot]$ is the indicator function for mandatory fields, and $q(f_j^{rec}) \in [0,1]$ represents quality assessment of recommended fields using LLM-based evaluation.

Quality assessment employs a rubric-guided LLM evaluator:

$$q(f) = \text{LLM}_{\text{eval}}(f, \text{rubric}_f, \text{examples}_f)$$

The rubric specifies criteria such as specificity, completeness, and actionability for each documentation field. We calibrate evaluator outputs against human expert ratings to ensure reliability.

#### 2.2.4 Community Responsiveness Index (CRI)

The Community Responsiveness Index measures maintainer engagement through issue response patterns, update frequency, and user interaction quality:

$$CRI_d(t) = \omega_1 \cdot R_d(t) + \omega_2 \cdot U_d(t) + \omega_3 \cdot I_d(t)$$

Response score $R_d(t)$ incorporates response time and resolution rate:

$$R_d(t) = \frac{1}{|Issues|} \sum_{i \in Issues} \left( \frac{\mathbb{1}[\text{responded}_i]}{1 + \log(1 + \Delta t_i)} \cdot \mathbb{1}[\text{resolved}_i] \right)$$

Update frequency $U_d(t)$ tracks meaningful updates (not just metadata changes) normalized by dataset age. Interaction quality $I_d(t)$ uses sentiment analysis on maintainer responses and tracks constructive engagement patterns.

#### 2.2.5 Ethical Alert System (EAS)

The Ethical Alert System integrates multiple detection mechanisms to identify datasets with potential ethical concerns:

1. **Automated Bias Detection**: Integration with fairness toolkits (e.g., Fairlearn, AIF360) for applicable datasets, computing group-level statistics and flagging significant disparities.

2. **Literature Monitoring**: Continuous scanning of arXiv, published venues, and social media for critiques mentioning specific datasets, using named entity recognition and sentiment analysis.

3. **Content Analysis**: For image and text datasets, periodic sampling and analysis using content moderation APIs and custom classifiers for sensitive content.

The EAS produces both a continuous risk score and discrete alert flags:

$$EAS_d = \begin{cases} \text{CRITICAL} & \text{if published critique or confirmed bias} \\ \text{WARNING} & \text{if automated detection flags} \\ \text{CLEAR} & \text{otherwise} \end{cases}$$

### 2.3 Health Score Aggregation

Individual dimension scores are aggregated into an overall Dynamic Dataset Health Score:

$$DDHS_d(t) = \sum_{k=1}^{5} \lambda_k \cdot S_k(d,t) \cdot \mathbb{1}[EAS_d \neq \text{CRITICAL}]$$

where $S_k$ represents individual dimension scores, $\lambda_k$ are importance weights (user-configurable with defaults learned from expert preferences), and critical ethical alerts override the numerical score with explicit warnings.

### 2.4 Scalability Architecture

Following insights from Chunked Data Shapley (Loizou & Tsoumakos, 2025) and ECOVAL (Chundawat et al., 2024), we employ:

1. **Stratified Sampling**: For computationally intensive operations (bias detection, freshness computation), we use importance-weighted sampling rather than exhaustive analysis.

2. **Incremental Updates**: Metrics are updated incrementally as new information arrives rather than recomputing from scratch.

3. **Tiered Computation**: High-traffic datasets receive more frequent updates; dormant datasets are assessed less frequently with longer cache durations.

### 2.5 Experimental Validation

#### Dataset Collection
We will conduct experiments using metadata and datasets from three major repositories: HuggingFace Datasets (>50,000 datasets), OpenML (>20,000 datasets), and UCI ML Repository (>600 datasets).

#### Evaluation Metrics

1. **Predictive Validity**: Correlation between DDHS scores and subsequent dataset deprecation/removal within 12 months (measured by AUC-ROC for deprecation prediction).

2. **User Alignment**: Agreement between computed scores and expert researcher rankings (Kendall's τ correlation).

3. **Computational Efficiency**: Wall-clock time and resource consumption for full repository assessment and incremental updates.

4. **Behavioral Impact**: A/B testing measuring changes in dataset selection patterns when health scores are displayed.

#### Experimental Protocol

1. **Retrospective Validation**: Apply DDHS to historical snapshots and evaluate whether low scores preceded known problems (deprecated datasets, published critiques, retractions).

2. **Expert Survey**: Recruit 50 ML researchers to rank-order datasets within their domains; compare against DDHS rankings.

3. **Scalability Benchmarks**: Measure computation time across repository scales from 100 to 100,000 datasets.

4. **User Study**: Deploy DDHS on a mirror repository with 500 participants, measuring dataset selection changes and user satisfaction.

## 3. Expected Outcomes & Impact

### Technical Outcomes

1. **Open-Source DDHS Implementation**: A modular, extensible framework that repositories can deploy independently, with APIs for custom health dimension integration.

2. **Validated Health Metrics**: Empirically validated formulations for each health dimension with published sensitivity analyses and threshold recommendations.

3. **Benchmark Dataset**: A curated collection of "known problematic" datasets with documented issues for validating future dataset health assessment tools.

### Ecosystem Impact

1. **Improved Dataset Selection**: By surfacing health indicators directly on dataset pages, researchers will make more informed choices, reducing inadvertent use of problematic or oversaturated datasets.

2. **Incentivized Stewardship**: Transparent health scores create incentives for maintainers to improve documentation, respond to issues, and actively curate their datasets—transforming data work from undervalued to recognized.

3. **Repository Prioritization**: Administrators receive actionable insights identifying datasets requiring intervention, enabling efficient allocation of limited curation resources.

4. **Community Health Reports**: Quarterly ecosystem assessments will provide the research community with trend analyses, identifying emerging benchmark saturation and documentation gaps across domains.

### Broader Contributions

This research contributes to the fundamental culture shift in ML data practices called for by the workshop. By making dataset health visible and quantifiable, DDHS transforms abstract concerns about data quality into concrete, actionable metrics. The framework also establishes a foundation for future standardization efforts, potentially informing repository policies and publication venue requirements.

The integration of ethical monitoring addresses growing concerns about bias and harm in ML datasets, while the usage saturation tracking directly targets the benchmark overuse problem that leads to misleading progress estimates. By approaching dataset health holistically rather than through isolated metrics, DDHS recognizes the interconnected nature of data quality challenges and provides a unified framework for addressing them.