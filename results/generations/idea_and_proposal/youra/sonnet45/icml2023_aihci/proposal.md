# CHEF: A Validated Composite Framework for AI-HCI System Evaluation

## 1. Introduction

### 1.1 Background

The convergence of artificial intelligence (AI) and human-computer interaction (HCI) has created unprecedented opportunities for intelligent systems that augment human capabilities. From reinforcement learning with human feedback (RLHF) powering conversational agents to explainable AI (XAI) supporting clinical decision-making, modern AI systems increasingly require direct human interaction to achieve their intended purpose. However, this convergence has exposed a critical methodological gap: the evaluation paradigms inherited from machine learning and HCI remain fundamentally incompatible.

Traditional machine learning evaluation emphasizes technical performance metrics—accuracy, F1-score, inference speed, and robustness—measured through standardized benchmarks like ImageNet or GLUE. These objective, quantitative measures enable systematic comparison and reproducible research but ignore the human experience of interacting with AI systems. Conversely, HCI evaluation prioritizes user-centered qualities—usability, satisfaction, trust, and task performance—assessed through user studies and qualitative methods. While these subjective measures capture essential aspects of human-AI collaboration, they lack the statistical rigor and standardization that enable cross-study comparison.

This fragmentation creates severe practical consequences. Decision-makers selecting AI systems for deployment in critical domains like healthcare, finance, and education face an impossible cognitive burden: mentally integrating incompatible metrics across technical and human-centered dimensions. A diagnostic AI system might achieve 95% accuracy (excellent technical performance) but generate explanations that confuse clinicians (poor cognitive alignment), leading to low adoption despite superior technical capabilities. Current evaluation approaches provide no principled method to compare such systems against alternatives that trade 5% accuracy for substantially better explainability.

Recent research has documented this evaluation crisis. Naveed et al. (2024) conducted a comprehensive review of XAI evaluation practices, revealing severe fragmentation: inconsistent metrics, lack of standardized user study protocols, and minimal cross-study comparability. Calvano (2024) identified the absence of unified evaluation frameworks as a primary barrier to deploying high-quality "Symbiotic AI" systems that effectively collaborate with humans. Hoffman et al. (2023) made significant progress by developing psychometrically validated measurement scales for XAI evaluation, but these instruments measure only the cognitive alignment dimension without integration with technical performance or broader experiential quality.

Existing multi-dimensional frameworks offer partial solutions but lack scientific rigor. ISO 25010 defines eight software quality dimensions but provides only descriptive taxonomies without validated measurement instruments or aggregation methods. AttrakDiff measures pragmatic and hedonic UX quality but ignores technical performance entirely. Schelenz et al.'s (2023) Transparency-Check evaluates AI systems across four transparency dimensions but presents results as profiles without composite scoring, forcing users to perform mental integration. None of these frameworks have demonstrated predictive validity—the ability to forecast real-world deployment success based on evaluation scores.

The clinical research community solved an analogous problem decades ago through composite endpoint methodology. Cardiovascular outcome trials routinely integrate heterogeneous measures (mortality, hospitalization, quality of life) into validated composite endpoints that guide treatment decisions and regulatory approval. This methodology, refined over 50+ years and codified in FDA guidance (2022), provides a scientifically rigorous template for multi-dimensional evaluation that the AI-HCI community has yet to adopt.

### 1.2 Research Objectives

This research proposes CHEF (Comprehensive Human-centered Evaluation Framework), a validated composite framework that integrates three essential dimensions of AI-HCI system quality:

1. **Technical Performance (T)**: Machine learning benchmark performance including accuracy, robustness, fairness, and efficiency
2. **Cognitive Alignment (C)**: Human understanding, trust, and mental model accuracy measured through validated XAI scales
3. **Experiential Quality (E)**: User satisfaction, task performance, and system usability assessed via standard UX instruments

The primary research objectives are:

**O1: Framework Development and Validation**
Develop the CHEF composite scoring methodology by adapting clinical composite endpoint techniques to AI-HCI evaluation, including:
- Dimension measurement protocols using validated instruments (Hoffman et al. scales for C, standard benchmarks for T, UX scales for E)
- Normalization procedures to convert heterogeneous scales to uniform 0-100 range
- Weighted linear aggregation: $\text{CHEF}_{\text{score}} = w_T \times T + w_C \times C + w_E \times E$ where $w_T + w_C + w_E = 1.0$
- Statistical validation demonstrating dimensional independence ($r < 0.6$), measurement reliability (Cronbach's $\alpha > 0.7$), and predictive validity ($r > 0.5$ with deployment outcomes)

**O2: Context-Dependent Weighting Methodology**
Develop and validate an LLM-assisted stakeholder elicitation method for determining domain-specific dimension weights that reflect context-appropriate quality criteria:
- Demonstrate systematic weight variation across domains (healthcare emphasizes C, entertainment emphasizes E)
- Validate LLM-assisted elicitation against gold-standard Delphi method (ICC > 0.6)
- Establish within-domain consistency (ICC > 0.6 among stakeholders from same domain)
- Show that context-weighted scores predict deployment success better than unweighted averaging

**O3: Comparative Effectiveness Evaluation**
Empirically demonstrate CHEF superiority over existing evaluation approaches through randomized controlled trials:
- Decision quality: CHEF-guided system selection achieves 15-25% better alignment with actual deployment success
- Decision efficiency: 20-30% faster decision-making compared to fragmented metric evaluation
- Failure detection: Composite + profile presentation identifies critical dimension failures with 80%+ accuracy
- Balanced optimization advantage: Systems with balanced T-C-E scores show 15-20% higher user retention than T-optimized-only systems

**O4: Open-Source Toolkit and Community Adoption**
Develop and disseminate practical tools enabling widespread CHEF adoption:
- Python package implementing full CHEF evaluation pipeline (benchmarking, survey administration, scoring, visualization)
- Standardized reporting protocol for academic publications
- Domain-specific weight libraries (healthcare, finance, education, entertainment)
- Validation on 15-20 diverse AI-HCI systems demonstrating framework applicability

### 1.3 Research Significance

This research addresses critical theoretical, methodological, and practical gaps at the intersection of AI and HCI:

**Theoretical Significance**

CHEF provides the first unified theoretical framework integrating ML evaluation paradigms (objective technical metrics) with HCI measurement paradigms (subjective user experience) through validated statistical methodology. This represents a fundamental shift from viewing AI-HCI quality as unidimensional "performance" to recognizing it as a three-dimensional construct (Technical × Cognitive × Experiential) where trade-offs are explicit and context-dependent. The framework challenges the single-metric optimization culture prevalent in ML research, demonstrating that systems optimized solely for benchmark accuracy may fail in deployment due to poor human-centered qualities.

The context-dependent evaluation theory formalizes the intuition that "best system" depends on domain-specific priorities: healthcare AI requires high cognitive alignment (transparency for clinical decision-making), entertainment AI prioritizes experiential quality (user engagement), while research applications may value balanced performance. This theoretical contribution justifies domain-specific evaluation standards and prevents inappropriate cross-domain system comparison.

**Methodological Significance**

CHEF introduces four methodological innovations:

1. **Validated Composite Scoring Protocol**: The first AI-HCI evaluation method with complete psychometric validation (reliability, construct validity, predictive validity), adapted from clinical composite endpoint methodology with 50+ years of validation history.

2. **LLM-Assisted Stakeholder Elicitation**: A novel method reducing stakeholder burden from hours (traditional Delphi method) to 30 minutes while maintaining validity (ICC > 0.6 vs. gold standard), making context-dependent weighting practical for resource-constrained teams.

3. **Integrated Visualization**: Dual presentation combining composite scores (enabling quick comparison) with dimension profiles (revealing detailed trade-offs) prevents oversimplification while avoiding fragmentation burden.

4. **Longitudinal Validation Methodology**: Protocol for validating evaluation frameworks through prospective correlation with real-world deployment outcomes (evaluation scores → 6-month retention, satisfaction, task performance), shifting AI-HCI evaluation from face validity to empirical validity.

**Practical Significance**

CHEF directly addresses urgent needs in high-stakes AI deployment domains:

**Healthcare**: Enables evidence-based selection of diagnostic AI systems balancing accuracy (patient safety), interpretability (regulatory compliance, clinical trust), and workflow integration (adoption). Current fragmented evaluation has hindered AI adoption in clinical settings despite technical maturity.

**Finance**: Supports fraud detection and robo-advisor selection trading off precision (financial loss prevention), transparency (regulatory requirements like EU AI Act), and analyst usability (operational efficiency).

**Education**: Guides intelligent tutoring system selection balancing learning effectiveness (student outcomes), pedagogical alignment (teacher trust), and student engagement (retention).

The open-source toolkit democratizes rigorous AI-HCI evaluation, enabling small research groups and startups to conduct validation studies previously requiring substantial resources. The standardized reporting protocol improves research reproducibility and enables systematic cross-study comparison, addressing the fragmentation crisis documented by Naveed et al. (2024).

Expected community impact includes: (1) 50-100 research groups adopting CHEF toolkit in Year 1, (2) 20+ academic papers reporting CHEF scores establishing benchmarking standard, (3) 3-5 real-world deployment decisions using CHEF in regulated domains within 2 years, and (4) potential alignment with EU AI Act transparency and human oversight requirements, accelerating compliant AI system development.

By providing a scientifically rigorous, practically feasible framework for unified AI-HCI evaluation, this research aims to accelerate the deployment of AI systems that excel not only in technical performance but also in human-centered qualities essential for real-world success.

---

## 2. Methodology

### 2.1 Research Design Overview

This research employs a mixed-methods validation study design comprising four sequential phases conducted over 12-18 months:

- **Phase 1: Measurement Validation** (Weeks 1-8): Psychometric validation of dimension measurement instruments
- **Phase 2: Empirical Validation** (Weeks 9-20): Cross-sectional evaluation of diverse AI-HCI systems
- **Phase 3: Predictive Validity** (Weeks 21-40): Longitudinal tracking linking evaluation scores to deployment outcomes
- **Phase 4: Comparative Effectiveness** (Weeks 21-28): Randomized controlled trial comparing CHEF to existing approaches

The study will evaluate 15-20 diverse AI-HCI systems selected through stratified sampling across domains (healthcare, finance, education, entertainment), architectures (RLHF, XAI, HITL, generative AI), and maturity levels (research prototypes, production systems). Each system will be assessed by 30-50 domain-matched participants (total N=450-1000), with a subset of 8-10 systems tracked longitudinally for deployment outcome validation.

### 2.2 CHEF Framework Specification

#### 2.2.1 Dimension Definitions and Measurement

**Technical Performance (T) Dimension**

The T dimension captures objective machine learning performance through standardized benchmarks. Measurement protocol:

$$T = \frac{1}{5}\left(\text{Accuracy}_{\text{norm}} + \text{Robustness}_{\text{norm}} + \text{Efficiency}_{\text{norm}} + \text{Fairness}_{\text{norm}} + \text{F1}_{\text{norm}}\right)$$

Where each component is normalized to 0-100 scale:

- **Accuracy**: Task-specific metric (classification accuracy, BLEU score for generation, mean average precision for retrieval) benchmarked on standard datasets (ImageNet, GLUE, domain-specific test sets)
- **Robustness**: Performance under adversarial perturbations or distribution shift (measured via adversarial accuracy on datasets like ImageNet-C, CIFAR-10-C)
- **Efficiency**: Inference time and computational cost (normalized inverse: $100 \times (1 - \frac{t_{\text{system}}}{t_{\text{max}}})$ where $t_{\text{max}}$ is slowest baseline)
- **Fairness**: Demographic parity or equalized odds across protected groups (normalized: $100 \times (1 - \text{disparity})$)
- **F1-score**: Harmonic mean of precision and recall (for classification tasks)

Normalization uses min-max scaling: $x_{\text{norm}} = \frac{x - x_{\text{min}}}{x_{\text{max}} - x_{\text{min}}} \times 100$, where $x_{\text{min}}$ and $x_{\text{max}}$ are determined from reference baselines or theoretical bounds.

**Cognitive Alignment (C) Dimension**

The C dimension measures human understanding, trust, and mental model accuracy using validated XAI scales from Hoffman et al. (2023). Core measurement instruments:

1. **Explanation Goodness Scale** (7-point Likert): "The explanations provided by this system are clear and understandable" (5 items, $\alpha = 0.82$)
2. **Mental Model Accuracy**: Objective assessment via prediction tasks ("Given this input, what will the system output?") scored as percentage correct
3. **Transparency Perception Scale** (7-point Likert): "I understand how this system makes decisions" (4 items, $\alpha = 0.78$)

Composite C score calculation:

$$C = \frac{1}{3}\left(\text{ExplanationGoodness}_{\text{norm}} + \text{MentalModelAccuracy} + \text{Transparency}_{\text{norm}}\right)$$

Likert scales normalized: $x_{\text{norm}} = \frac{x - 1}{7 - 1} \times 100$ (1-7 scale → 0-100)

Mental model accuracy already in percentage (0-100).

**Experiential Quality (E) Dimension**

The E dimension captures user satisfaction, task performance, and system usability through standard UX instruments:

1. **System Usability Scale (SUS)**: 10-item questionnaire yielding 0-100 score (industry standard, $\alpha = 0.91$)
2. **Task Performance**: Objective behavioral metrics
   - Task completion rate (percentage of tasks successfully completed)
   - Task completion time (normalized inverse: faster = better)
   - Error rate (normalized inverse: fewer errors = better)
3. **User Satisfaction**: 5-point Likert scale ("Overall, I am satisfied with this system", 3 items, $\alpha = 0.85$)
4. **Trust Scale**: 7-point Likert adapted from Hoffman et al. ("I trust this system to help me with my tasks", 4 items, $\alpha = 0.80$)

Composite E score:

$$E = \frac{1}{4}\left(\text{SUS} + \text{TaskPerformance}_{\text{norm}} + \text{Satisfaction}_{\text{norm}} + \text{Trust}_{\text{norm}}\right)$$

Where:
- SUS already 0-100
- Task performance: $\frac{1}{3}(\text{CompletionRate} + (100 - \text{TimeNorm}) + (100 - \text{ErrorRate}))$
- Satisfaction: $(x - 1)/(5 - 1) \times 100$
- Trust: $(x - 1)/(7 - 1) \times 100$

#### 2.2.2 Composite Scoring Methodology

The CHEF composite score integrates the three dimensions through weighted linear aggregation:

$$\text{CHEF}_{\text{score}} = w_T \times T + w_C \times C + w_E \times E$$

Subject to constraint: $w_T + w_C + w_E = 1.0$ and $w_i \geq 0$ for all $i$.

**Weight Determination**: Context-dependent weights are elicited from domain stakeholders through structured methods:

**LLM-Assisted Elicitation Protocol**:
1. Stakeholder completes pairwise comparison tasks: "For [domain] applications, is [dimension A] more important than [dimension B]?"
2. LLM (GPT-4 or equivalent) conducts structured interview exploring trade-off scenarios: "Would you accept 10% lower accuracy for 20% better explainability?"
3. Analytical Hierarchy Process (AHP) converts pairwise comparisons to weights
4. Consistency check: If consistency ratio > 0.1, stakeholder reviews inconsistent judgments
5. Final weights: Median across stakeholders from same domain

**Gold-Standard Delphi Method** (for validation):
1. Round 1: Stakeholders independently assign weights
2. Round 2: Stakeholders see anonymized group distribution, revise weights
3. Round 3: Final weights after seeing Round 2 distribution
4. Convergence criterion: Interquartile range < 0.15 for each weight

**Default Weight Sets** (derived from pilot stakeholder studies):
- Healthcare: $w_T = 0.30, w_C = 0.45, w_E = 0.25$ (transparency critical)
- Finance: $w_T = 0.40, w_C = 0.35, w_E = 0.25$ (balanced technical + compliance)
- Education: $w_T = 0.30, w_C = 0.30, w_E = 0.40$ (engagement matters)
- Entertainment: $w_T = 0.20, w_C = 0.20, w_E = 0.60$ (user experience dominant)
- Research: $w_T = 0.35, w_C = 0.35, w_E = 0.30$ (balanced evaluation)

### 2.3 Data Collection Procedures

#### 2.3.1 System Selection Strategy

Systems selected through stratified sampling to ensure diversity:

**Stratification Dimensions**:
- **Domain**: Healthcare (N=4), Finance (N=4), Education (N=4), Entertainment (N=4)
- **Architecture**: RLHF language models (N=5), XAI decision support (N=5), HITL active learning (N=5), Generative AI tools (N=5)
- **Maturity**: Research prototypes (N=7), Production systems (N=8-13)
- **Interaction Paradigm**: Conversational (N=6), Visual (N=6), Mixed-initiative (N=8)

**Inclusion Criteria**:
- System has implemented user-facing interface (not API-only)
- System is sufficiently stable for controlled evaluation (not constantly changing)
- Technical benchmarks are available or can be computed
- System developers consent to evaluation and data sharing

**Example Systems** (illustrative):
- Healthcare: Diagnostic AI with SHAP explanations, clinical decision support chatbot
- Finance: Fraud detection dashboard with counterfactual explanations, robo-advisor
- Education: Intelligent tutoring system, automated essay feedback tool
- Entertainment: Content recommendation with explanations, AI-assisted creative writing tool

#### 2.3.2 Participant Recruitment

**Sample Size Calculation**:
Per system: N=30-50 participants (power analysis: detect effect size d=0.5 with power=0.8, α=0.05 requires N≥34)

Total participants: 15 systems × 40 participants (median) = 600 participants

**Recruitment Strategy**:
- **Domain Matching**: Participants recruited from target user population (clinicians for healthcare AI, financial analysts for finance AI, students for education AI)
- **Expertise Levels**: Stratified sampling across novice (40%), intermediate (40%), expert (20%) to capture user heterogeneity
- **Demographics**: Balanced gender (50/50 target), age distribution (18-65), technical literacy (assessed via pre-screening)

**Recruitment Channels**:
- University participant pools (education, general systems)
- Professional networks (healthcare: medical schools, finance: industry partnerships)
- Online platforms (Prolific, CloudResearch for general population studies)
- Compensation: $25-40/hour depending on expertise level and session length

**Inclusion Criteria**:
- Age ≥18 years
- Fluent in English (survey instruments validated in English)
- Domain experience (for domain-specific systems): ≥1 year professional experience or equivalent training
- No prior exposure to evaluated system (to avoid familiarity bias)

#### 2.3.3 Evaluation Session Protocol

**Session Structure** (90 minutes total):

**Part 1: Orientation (10 min)**
- Informed consent, demographics survey
- Brief system introduction (standardized 5-minute tutorial)
- Practice task (not scored)

**Part 2: Technical Performance Assessment (Automated, Parallel)**
- Conducted by research team using standard benchmarks
- No participant involvement (objective metrics)

**Part 3: Cognitive Alignment Assessment (30 min)**
- Participants complete 3-5 representative tasks with system
- After each task: Explanation goodness survey (5 items, 7-point Likert)
- Mental model assessment: 10 prediction questions ("What will system do if...?")
- Transparency perception survey (4 items, 7-point Likert)

**Part 4: Experiential Quality Assessment (40 min)**
- Participants complete 5-7 realistic tasks (domain-specific scenarios)
- Behavioral data logged: completion time, errors, interaction patterns
- Post-task surveys:
  - System Usability Scale (SUS): 10 items
  - Satisfaction: 3 items, 5-point Likert
  - Trust: 4 items, 7-point Likert

**Part 5: Debrief (10 min)**
- Open-ended feedback
- Compensation and thank you

**Standardization Measures**:
- Identical task sets across participants for same system
- Randomized task order to control for learning effects
- Standardized instructions (scripted)
- Controlled environment (quiet room, standardized hardware)

### 2.4 Statistical Validation Studies

#### 2.4.1 Phase 1: Measurement Validation

**Study 1.1: Scale Reliability**

**Objective**: Verify internal consistency of dimension measurements

**Method**:
- Administer full CHEF evaluation to N=5 diverse systems (pilot sample)
- Calculate Cronbach's α for each dimension:

$$\alpha = \frac{k}{k-1}\left(1 - \frac{\sum_{i=1}^k \sigma_{y_i}^2}{\sigma_x^2}\right)$$

where $k$ = number of items, $\sigma_{y_i}^2$ = variance of item $i$, $\sigma_x^2$ = variance of total score

**Success Criterion**: $\alpha > 0.7$ for T, C, and E dimensions (acceptable internal consistency)

**Analysis**:
- Item-total correlations (identify poorly performing items)
- Factor analysis (confirm unidimensionality within each dimension)
- Test-retest reliability (subset of N=20 participants repeat evaluation after 2 weeks, ICC > 0.7)

**Study 1.2: Dimensional Independence**

**Objective**: Empirically validate that T, C, E capture distinct constructs

**Method**:
- Measure all three dimensions for N=15-20 systems
- Calculate Pearson correlations: $r(T,C)$, $r(T,E)$, $r(C,E)$

$$r_{xy} = \frac{\sum_{i=1}^n (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^n (x_i - \bar{x})^2 \sum_{i=1}^n (y_i - \bar{y})^2}}$$

**Success Criterion**: All pairwise correlations $r < 0.6$ (discriminant validity threshold from Campbell & Fiske, 1959)

**Analysis**:
- Correlation matrix with 95% confidence intervals
- Confirmatory Factor Analysis (CFA) testing three-factor model:

$$\chi^2 / df < 3, \text{CFI} > 0.90, \text{RMSEA} < 0.08$$

- Comparison to alternative models (two-factor, single-factor) via likelihood ratio tests

**Study 1.3: Weighting Method Validation**

**Objective**: Validate LLM-assisted stakeholder elicitation vs. gold-standard Delphi

**Method**:
- Healthcare domain experts (N=20) provide dimension weights via both methods
- Calculate Intraclass Correlation Coefficient (ICC) between methods:

$$\text{ICC} = \frac{\sigma_{\text{between}}^2}{\sigma_{\text{between}}^2 + \sigma_{\text{within}}^2}$$

**Success Criterion**: ICC > 0.6 (moderate agreement), ideally > 0.7 (strong agreement)

**Analysis**:
- Bland-Altman plots (visualize agreement, identify systematic bias)
- Paired t-tests (test for mean differences between methods)
- Time efficiency comparison (minutes to complete elicitation)

#### 2.4.2 Phase 2: Empirical Validation

**Study 2.1: System Evaluation**

**Design**: Cross-sectional evaluation of 15-20 diverse AI-HCI systems

**Procedure**:
1. Technical benchmarking (T dimension): Automated evaluation on standard datasets
2. User studies (C and E dimensions): N=30-50 participants per system, 90-minute sessions
3. Data collection: CHEF composite scores, dimension profiles, raw measurements

**Analysis**:
- Descriptive statistics: Mean, SD, range for each dimension and composite score
- System comparison: One-way ANOVA testing differences across systems
- Profile visualization: Radar charts showing T-C-E profiles for each system

**Study 2.2: Dimension Weighting**

**Design**: Structured elicitation study with domain stakeholders

**Participants**: N=10-15 stakeholders per domain (healthcare, finance, education, entertainment), total N=40-60

**Method**:
- LLM-assisted elicitation (30-minute sessions)
- Delphi method (3 rounds, 2 weeks total) for validation subset

**Analysis**:
- Within-domain consistency: ICC among stakeholders from same domain
- Between-domain variation: One-way ANOVA testing weight differences across domains

$$F = \frac{\text{MS}_{\text{between}}}{\text{MS}_{\text{within}}}$$

- Post-hoc pairwise comparisons (Tukey HSD) identifying which domains differ significantly

#### 2.4.3 Phase 3: Predictive Validity

**Study 3.1: Longitudinal Deployment Tracking**

**Design**: Prospective longitudinal study linking CHEF scores to real outcomes

**Sample**: Subset of 8-10 systems from Phase 2 that proceed to deployment

**Timeline**:
- Baseline (t=0): CHEF scores measured during evaluation
- Follow-up 1 (t=3 months): Deployment metrics collected
- Follow-up 2 (t=6 months): Final deployment metrics

**Deployment Metrics**:

$$\text{DeploymentSuccess} = \frac{1}{4}(\text{Retention} + \text{TaskImprovement} + \text{Satisfaction} + \text{ErrorReduction})$$

Where:
- **Retention**: Percentage of initial users still active at t=6 months
- **Task Improvement**: Performance gain vs. no-AI baseline (percentage improvement)
- **Satisfaction**: Longitudinal survey (1-5 scale, normalized to 0-100)
- **Error Reduction**: Decrease in task errors vs. baseline (percentage reduction)

**Analysis**:
- Pearson correlation between CHEF scores (baseline) and deployment success (6-month):

$$r_{\text{CHEF,Success}} = \frac{\text{Cov}(\text{CHEF}, \text{Success})}{\sigma_{\text{CHEF}} \sigma_{\text{Success}}}$$

**Success Criterion**: $r > 0.5$ (large effect size, Cohen, 1988)

- Regression analysis: $\text{Success} = \beta_0 + \beta_1 T + \beta_2 C + \beta_3 E + \epsilon$ (test which dimensions predict outcomes)
- Comparison: CHEF composite vs. individual dimensions (which predicts better?)

**Power Analysis**: N=8-10 systems provides 80% power to detect $r=0.6$ at $\alpha=0.05$ (two-tailed)

#### 2.4.4 Phase 4: Comparative Effectiveness

**Study 4.1: Decision Quality Experiment**

**Design**: Randomized controlled trial comparing evaluation approaches

**Participants**: N=90 decision-makers (researchers, practitioners, domain experts)

**Groups** (N=30 each):
- **Group A**: CHEF composite + profile
- **Group B**: Fragmented metrics (separate T, C, E without integration)
- **Group C**: Single-dimension (T-only, typical benchmark approach)

**Task**: Select best system for 5 deployment scenarios from set of 4 candidate systems

**Scenarios** (varied stakes and domains):
1. High-stakes healthcare: Diagnostic AI for emergency department
2. Consumer entertainment: Content recommendation for streaming service
3. Education: Intelligent tutoring for high school mathematics
4. Finance: Fraud detection for credit card transactions
5. Research: Data analysis assistant for scientific computing

**Measures**:
- **Selection Quality**: Agreement with gold-standard "best" system (determined by actual deployment performance from Study 3.1)

$$\text{Quality} = \frac{\text{Number of correct selections}}{5 \text{ scenarios}} \times 100\%$$

- **Decision Time**: Minutes to complete all 5 selections
- **Confidence**: Self-reported confidence (1-7 scale) averaged across scenarios

**Analysis**:
- One-way ANOVA comparing groups on quality, time, confidence
- Post-hoc pairwise comparisons (Bonferroni correction)
- Effect sizes: Cohen's $d$ for group differences

$$d = \frac{\bar{x}_1 - \bar{x}_2}{s_{\text{pooled}}}$$

**Success Criterion**: Group A outperforms Group B and C by ≥10% in selection quality (effect size $d > 0.5$)

**Study 4.2: Composite vs. Profile Value**

**Design**: Within-subjects experiment examining composite score utility

**Participants**: N=40 users

**Conditions** (counterbalanced order):
- **Condition A**: Composite score only (single number per system)
- **Condition B**: Dimension profile only (T-C-E breakdown, no composite)
- **Condition C**: Composite + profile (both presented)

**Task**: Identify systems with critical dimension failures (e.g., high T but dangerously low C) from set of 10 systems

**Measures**:
- **Detection Accuracy**: Percentage of critical failures correctly identified
- **Decision Time**: Seconds to complete task
- **Perceived Difficulty**: 1-7 scale

**Analysis**:
- Repeated-measures ANOVA: $F = \frac{\text{MS}_{\text{condition}}}{\text{MS}_{\text{error}}}$
- Post-hoc pairwise comparisons (Bonferroni correction)
- Interaction effects: Does accuracy-time trade-off differ by condition?

**Success Criterion**: Condition C shows highest detection accuracy (80%+) while maintaining reasonable decision time (no worse than 20% slower than Condition A)

### 2.5 Evaluation Metrics

**Primary Metrics**:

1. **Framework Validity**:
   - Dimensional independence: Pearson $r < 0.6$ for all dimension pairs
   - Measurement reliability: Cronbach's $\alpha > 0.7$ for each dimension
   - Predictive validity: $r > 0.5$ between CHEF scores and deployment success
   - Discriminant validity: Effect size $d > 0.5$ between high/low quality systems

2. **Decision Quality**:
   - Selection accuracy: Percentage agreement with gold-standard best system
   - Decision time: Minutes to complete system selection task
   - Confidence: Self-reported confidence in decisions (1-7 scale)

3. **Deployment Outcomes**:
   - User retention: Percentage of users active at 6 months
   - Task performance: Improvement vs. no-AI baseline
   - User satisfaction: Longitudinal survey scores
   - Error reduction: Decrease in task errors vs. baseline

**Secondary Metrics**:

4. **Weighting Method**:
   - Inter-method agreement: ICC between LLM-assisted and Delphi
   - Within-domain consistency: ICC among stakeholders from same domain
   - Cross-domain variation: F-statistic from ANOVA on weights

5. **Usability**:
   - Toolkit adoption: Number of research groups using CHEF (Year 1 target: 50-100)
   - Evaluation time: Hours to complete full CHEF assessment per system
   - Reporting compliance: Percentage of papers reporting CHEF scores (Year 1 target: 20+)

### 2.6 Data Analysis Plan

**Software**: R (statistical analysis), Python (technical benchmarking, toolkit implementation), Qualtrics (survey administration)

**Preprocessing**:
- Missing data: Multiple imputation (MICE algorithm) if <10% missing, listwise deletion if >10%
- Outlier detection: Identify values >3 SD from mean, investigate but retain unless data entry error
- Normalization: Min-max scaling to 0-100 for all dimensions

**Statistical Tests**:
- Correlations: Pearson $r$ (parametric), Spearman $\rho$ (non-parametric backup)
- Group comparisons: One-way ANOVA (parametric), Kruskal-Wallis (non-parametric backup)
- Reliability: Cronbach's $\alpha$, ICC (two-way random effects model)
- Regression: Multiple linear regression, check assumptions (normality, homoscedasticity, multicollinearity)

**Multiple Comparisons Correction**: Bonferroni correction for post-hoc tests ($\alpha_{\text{adjusted}} = \alpha / k$ where $k$ = number of comparisons)

**Power and Sample Size**: All studies powered at 0.8 to detect medium-to-large effects ($d=0.5$, $r=0.5$) at $\alpha=0.05$ (two-tailed)

**Sensitivity Analyses**:
- Test robustness to: outlier systems, different normalization methods (min-max vs. z-score vs. percentile), alternative weighting schemes (equal weights vs. context-dependent), varied correlation thresholds ($r<0.5$ vs. $r<0.7$)
- Subgroup analyses: System maturity (prototype vs. production), domain, architecture type

**Reproducibility**:
- Pre-registration of analysis plan on Open Science Framework (OSF)
- Open data repository (anonymized participant data, system scores)
- Open-source code (GitHub: CHEF toolkit, analysis scripts)
- IRB approval for all human subjects research

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Research Outcomes

**Outcome 1: Validated CHEF Framework**

We expect to demonstrate that the CHEF framework achieves all statistical validation criteria:

- **Dimensional Independence**: Pearson correlations between T-C, T-E, and C-E dimensions will be $r < 0.6$ (95% CI: 0.3-0.55), confirming that the three dimensions capture distinct constructs. This validates the theoretical claim that technical performance, cognitive alignment, and experiential quality are separable aspects of AI-HCI system quality.

- **Measurement Reliability**: Cronbach's $\alpha$ will exceed 0.7 for all three dimensions (expected: T: $\alpha = 0.75$, C: $\alpha = 0.82$, E: $\alpha = 0.88$), demonstrating that dimension measurements are internally consistent and reproducible.

- **Predictive Validity**: CHEF composite scores will correlate with 6-month deployment success metrics at $r > 0.5$ (expected: $r = 0.58$, 95% CI: 0.42-0.71), providing empirical evidence that evaluation scores predict real-world outcomes. Individual dimension analysis will reveal that C dimension shows strongest correlation with user retention ($r = 0.52$), while T dimension predicts task performance improvement ($r = 0.48$).

- **Discriminant Power**: Systems known to differ in quality (based on deployment outcomes) will show significantly different CHEF scores with large effect sizes ($d > 0.8$), confirming the framework's ability to differentiate high-quality from low-quality systems.

**Outcome 2: Context-Dependent Weighting Validation**

Domain-specific dimension weights will show systematic variation:

- **Healthcare**: $w_C = 0.45 \pm 0.08$ (highest cognitive alignment weight, reflecting transparency requirements)
- **Finance**: $w_T = 0.40 \pm 0.07$, $w_C = 0.35 \pm 0.06$ (balanced technical + compliance)
- **Education**: $w_E = 0.40 \pm 0.09$ (highest experiential quality weight, reflecting engagement importance)
- **Entertainment**: $w_E = 0.60 \pm 0.10$ (dominant experiential focus)

ANOVA will confirm significant between-domain variation ($F > 8.0$, $p < 0.001$), while within-domain consistency will be strong (ICC > 0.7). LLM-assisted elicitation will achieve moderate-to-strong agreement with Delphi method (ICC = 0.68, 95% CI: 0.55-0.78) while reducing stakeholder time burden by 75% (30 minutes vs. 2 hours).

Context-weighted CHEF scores will predict deployment success significantly better than unweighted averaging ($\Delta r = 0.12$, $p < 0.05$), validating the utility of domain-specific weighting.

**Outcome 3: CHEF Superiority Over Existing Approaches**

The randomized controlled trial will demonstrate CHEF advantages:

- **Decision Quality**: Group A (CHEF) will achieve 22% higher selection accuracy than Group B (fragmented metrics) and 35% higher than Group C (single-dimension), with effect sizes $d = 0.72$ and $d = 1.15$ respectively.

- **Decision Efficiency**: CHEF users will complete system selection 25% faster than fragmented metric users (12 minutes vs. 16 minutes, $p < 0.01$), demonstrating reduced cognitive load.

- **Failure Detection**: Composite + profile presentation (Condition C) will achieve 82% accuracy in identifying critical dimension failures, compared to 48% for composite-only (Condition A) and 75% for profile-only (Condition B), confirming the value of integrated presentation.

- **Balanced Optimization Advantage**: Systems with balanced T-C-E scores (all dimensions >60) will show 18% higher 6-month user retention than T-optimized-only systems (T>80, C or E <50), providing empirical evidence that multi-dimensional quality matters for deployment success.

**Outcome 4: Open-Source Toolkit and Community Resources**

The CHEF toolkit will include:

- **Python Package** (`chef-eval`): 5,000+ lines of code implementing full evaluation pipeline
  - Technical benchmarking module (integration with HuggingFace Evaluate, TensorFlow Model Analysis)
  - Survey administration (Qualtrics API integration, Hoffman et al. scales)
  - Scoring engine (normalization, weighting, composite calculation)
  - Visualization dashboard (interactive 3D profiles, comparison charts using Plotly)
  - Statistical validation suite (reliability tests, CFA, correlation analysis)

- **Documentation**: Comprehensive user guide (100+ pages), API reference, tutorial notebooks

- **Domain Weight Libraries**: Validated weight sets for 4 domains (healthcare, finance, education, entertainment) with usage guidelines

- **Standardized Reporting Template**: LaTeX/Word templates for academic papers reporting CHEF scores

Expected adoption: 50-100 research groups in Year 1, 20+ papers reporting CHEF scores, 3-5 real-world deployment decisions using CHEF within 2 years.

### 3.2 Theoretical Impact

**Paradigm Shift in AI-HCI Evaluation**

CHEF challenges the dominant single-metric optimization paradigm in ML research by demonstrating that:

1. **Multi-dimensional quality is empirically distinct**: The finding that T, C, and E dimensions are weakly correlated ($r < 0.6$) provides empirical evidence that technical performance alone is insufficient for characterizing AI-HCI system quality. This validates human-centered AI principles with quantitative data.

2. **Trade-offs are explicit and measurable**: The framework makes quality trade-offs transparent (e.g., "System A has 5% higher accuracy but 15% lower explainability than System B"), enabling informed decision-making rather than implicit prioritization of technical metrics.

3. **Context determines "best"**: The demonstration that optimal dimension weights vary by domain (healthcare ≠ entertainment) formalizes the intuition that universal benchmarks are inappropriate for AI-HCI systems. This theoretical contribution justifies domain-specific evaluation standards.

**Integration of ML and HCI Paradigms**

CHEF provides the first validated bridge between ML evaluation culture (objective, quantitative, benchmark-driven) and HCI evaluation culture (subjective, qualitative, user-centered). This integration:

- Enables interdisciplinary collaboration by providing common language and metrics
- Legitimizes human-centered evaluation in ML venues (NeurIPS, ICML) by demonstrating statistical rigor
- Brings quantitative rigor to HCI evaluation (CHI, UIST) through validated measurement instruments

The cross-domain transfer of clinical composite endpoint methodology demonstrates that mature evaluation frameworks from other fields can accelerate AI-HCI research, opening pathways for future methodological innovation.

### 3.3 Methodological Impact

**Advancing AI-HCI Evaluation Science**

CHEF introduces four methodological innovations with broad applicability:

1. **Psychometric Validation Protocol**: The comprehensive validation approach (reliability, construct validity, predictive validity) establishes a template for future AI-HCI evaluation frameworks. Researchers proposing new evaluation methods will be expected to demonstrate similar rigor.

2. **LLM-Assisted Stakeholder Elicitation**: If validated (ICC > 0.6 vs. Delphi), this method will enable efficient multi-stakeholder input for evaluation frameworks, decision-making tools, and participatory design processes. Potential applications extend beyond AI-HCI to broader HCI research.

3. **Longitudinal Outcome Validation**: The protocol for linking evaluation scores to deployment outcomes shifts AI-HCI evaluation from face validity ("this seems like a good measure") to empirical validity ("this measure predicts real success"). This raises the bar for evaluation research.

4. **Integrated Visualization**: The dual presentation approach (composite + profile) provides a design pattern for communicating multi-dimensional information, applicable to dashboards, decision support tools, and research reporting.

**Reproducibility and Standardization**

The open-source toolkit and standardized reporting protocol will improve research reproducibility:

- **Cross-study comparison**: Researchers using CHEF can directly compare systems across papers, reducing fragmentation
- **Meta-analysis enablement**: Standardized metrics enable quantitative synthesis of findings across studies
- **Reduced cherry-picking**: Comprehensive evaluation discourages selective reporting of favorable metrics

Expected impact: 30% reduction in evaluation metric heterogeneity in AI-HCI papers within 3 years of publication.

### 3.4 Practical Impact

**Accelerating AI Deployment in High-Stakes Domains**

CHEF directly addresses barriers to AI adoption in regulated domains:

**Healthcare**: Current fragmented evaluation has hindered clinical AI adoption despite technical maturity. CHEF enables evidence-based selection of diagnostic AI systems that balance accuracy (patient safety), interpretability (regulatory compliance, clinical trust), and workflow integration (adoption). Expected impact:

- 3-5 healthcare organizations use CHEF for AI procurement decisions within 2 years
- Alignment with FDA guidance on AI/ML medical devices (transparency, human oversight)
- Potential integration into clinical AI evaluation standards (e.g., American Medical Informatics Association guidelines)

**Finance**: Regulatory requirements (EU AI Act, financial services regulations) demand transparency and human oversight. CHEF provides systematic evaluation of compliance-relevant dimensions (cognitive alignment = transparency). Expected impact:

- 2-3 financial institutions adopt CHEF for AI risk assessment
- Potential alignment with EU AI Act conformity assessment procedures
- Industry standard for evaluating robo-advisors and fraud detection systems

**Education**: Intelligent tutoring systems require balancing learning effectiveness (technical performance), pedagogical alignment (cognitive alignment), and student engagement (experiential quality). CHEF enables evidence-based selection. Expected impact:

- 5-10 school districts or universities use CHEF for educational AI procurement
- Integration into educational technology evaluation frameworks (e.g., ISTE standards)

**Democratizing Rigorous Evaluation**

The open-source toolkit reduces barriers to conducting high-quality AI-HCI evaluation:

- **Small research groups**: Can conduct validation studies previously requiring substantial resources (estimated cost reduction: $10K-20K per system evaluation)
- **Startups**: Can demonstrate system quality to investors and customers through standardized metrics
- **Non-profits**: Can evaluate AI tools for social good applications with limited budgets

Expected adoption: 100+ organizations (academic + industry + non-profit) use CHEF toolkit within 2 years.

**Influencing AI Development Practices**

By demonstrating that balanced T-C-E optimization leads to better deployment outcomes (18% higher retention), CHEF will incentivize developers to prioritize human-centered qualities:

- **ML conferences**: Increased emphasis on explainability and usability in system papers
- **Industry**: Product teams allocate resources to cognitive alignment and experiential quality, not just accuracy
- **Funding agencies**: Grant proposals evaluated on multi-dimensional quality, not just technical innovation

Expected cultural shift: 25% increase in ML papers reporting human-centered metrics (C, E dimensions) within 3 years.

### 3.5 Broader Impacts

**Ethical AI Development**

CHEF's cognitive alignment dimension (C) directly measures transparency and explainability, which are essential for:

- **Accountability**: Users can understand AI decisions, enabling challenge and redress
- **Fairness**: Explainability reveals potential biases, enabling mitigation
- **Trust**: Transparency builds appropriate reliance on AI systems

By elevating cognitive alignment to equal status with technical performance, CHEF incentivizes development of AI systems that are not only accurate but also understandable and trustworthy. This aligns with responsible AI principles and regulatory requirements (EU AI Act, NIST AI Risk Management Framework).

**Reducing AI Deployment Failures**

Current single-metric optimization has led to high-profile AI deployment failures (e.g., healthcare AI with high accuracy but low clinical adoption due to poor explainability). CHEF's multi-dimensional evaluation will reduce such failures by:

- Identifying systems with critical dimension weaknesses before deployment
- Guiding iterative improvement (dimension profiles reveal specific areas needing work)
- Setting realistic expectations (composite scores reflect overall quality, not just peak technical performance)

Expected impact: 15-20% reduction in AI deployment failures (measured by premature discontinuation) in domains adopting CHEF.

**Advancing Human-AI Collaboration**

By demonstrating that experiential quality (E) predicts deployment success, CHEF provides empirical evidence for investing in human-AI interaction design. This will:

- Shift resources from pure algorithm development to interaction design
- Elevate HCI expertise in AI development teams
- Improve human-AI collaboration outcomes (task performance, user satisfaction)

Expected long-term impact: AI systems that are not just technically capable but genuinely useful and usable, accelerating beneficial AI adoption across society.

**Limitations and Future Work**

While CHEF represents a significant advance, several limitations warrant future research:

1. **Cross-cultural validation**: Current instruments validated primarily in Western contexts; extension to non-Western cultures requires additional validation
2. **Temporal stability**: Long-term predictive validity (>6 months) remains unknown; longitudinal studies needed
3. **Emerging modalities**: Framework developed for current AI-HCI systems; adaptation needed for future modalities (embodied AI, brain-computer interfaces)
4. **Lightweight variants**: Full CHEF evaluation is resource-intensive; automated proxy development could improve scalability
5. **Non-linear aggregation**: Linear weighting may be inappropriate for some contexts (e.g., minimum thresholds in safety-critical domains); alternative aggregation methods warrant exploration

These limitations provide rich opportunities for future research, ensuring CHEF evolves with the rapidly advancing AI-HCI landscape.

---

**Word Count**: 7,847 words

This research proposal presents a comprehensive plan to develop, validate, and disseminate CHEF—a scientifically rigorous, practically feasible framework for unified AI-HCI system evaluation. By integrating technical performance, cognitive alignment, and experiential quality through validated composite scoring methodology, CHEF addresses a critical gap hindering AI deployment in high-stakes domains. The expected outcomes—validated framework, open-source toolkit, empirical evidence of superiority over existing approaches—will advance both AI-HCI evaluation science and practical system selection, ultimately accelerating the development and deployment of AI systems that excel in both technical and human-centered dimensions.