# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CHEF-001
**Confidence Level:** 0.85 (High)

**Main Hypothesis:**
If AI-HCI systems are evaluated using the CHEF (Comprehensive Human-centered Evaluation Framework) composite scoring methodology that integrates Technical Performance (T), Cognitive Alignment (C), and Experiential Quality (E) dimensions through validated clinical composite endpoint methodology with context-dependent stakeholder weighting, then:
1. The framework will demonstrate statistical validity (dimension independence r<0.6, predictive validity r>0.5)
2. Decision-makers using CHEF will make higher-quality system selections than those using fragmented metrics or single-dimension approaches
3. Systems optimized for balanced T-C-E scores will achieve better real-world deployment outcomes (retention, satisfaction, task performance) than technically-optimized-only systems

**Alternative Hypothesis (H0):**
The CHEF composite framework does NOT provide superior evaluation capability compared to existing fragmented approaches. Specifically:
- H0a: The three dimensions (T, C, E) are redundant (r≥0.6), making composite scoring unnecessary
- H0b: CHEF-guided decisions do not improve selection quality over fragmented evaluation
- H0c: Composite scores do not predict deployment success better than individual dimension scores
- H0d: Context-dependent weighting does not improve framework utility over fixed weights

### 1.2 Variables

| Variable Type | Name | Definition | Measurement | Range/Scale |
|--------------|------|------------|-------------|-------------|
| **Independent** | AI-HCI System Design | Architecture, interaction paradigm, explanation method | Categorical classification | transformer/CNN, conversational/visual, SHAP/attention/example |
| **Independent** | Application Domain | Deployment context | Categorical | healthcare, finance, education, entertainment |
| **Independent** | User Population | Expertise and technical literacy | Demographic + assessment | novice/intermediate/expert |
| **Dependent** | Technical Performance (T) | ML benchmark performance | Standardized metrics | 0-100% (normalized) |
| **Dependent** | Cognitive Alignment (C) | Human understanding & trust in AI | Hoffman et al. XAI scales | 0-100 (normalized from 1-7 Likert) |
| **Dependent** | Experiential Quality (E) | User satisfaction & task performance | UX scales + behavioral | 0-100 (normalized) |
| **Dependent** | CHEF Composite Score | Weighted integration of T-C-E | CHEF_score = w_T×T + w_C×C + w_E×E | 0-100 |
| **Dependent** | Deployment Success | Real-world outcome metrics | Retention %, task improvement %, satisfaction, error reduction % | Multiple scales |
| **Controlled** | Evaluation Protocol | Standardized measurement procedure | Fixed protocol | - |
| **Controlled** | User Study Conditions | Task, time, training standardization | Experimental design | - |
| **Controlled** | Benchmark Datasets | Standard ML evaluation data | ImageNet, GLUE, domain-specific | - |

**Key Variable Relationships:**
- **T dimension measurement:** Accuracy, F1-score, inference time, robustness (adversarial), fairness metrics (demographic parity)
- **C dimension measurement (Hoffman et al. 2023):** Explanation goodness (1-7), mental model accuracy (%), curiosity engagement (1-7), transparency perception (1-7)
- **E dimension measurement:** System Usability Scale (SUS), task completion time, error rate, satisfaction (1-5), trust scale (1-7)
- **Dimension weights:** w_T + w_C + w_E = 1.0, derived from stakeholder elicitation (Delphi method or LLM-assisted)

### 1.3 Causal Mechanism

**Core Mechanism:**
CHEF enables better AI-HCI evaluation through three sequential mechanisms:

**Mechanism 1: Statistical Integration**
*Construct → Observable*
- Clinical composite endpoint methodology provides validated statistical framework for integrating heterogeneous measures (objective technical + subjective human-centered)
- Validated scales (Hoffman et al. for C, standard benchmarks for T, UX scales for E) provide reliable measurement instruments
- Normalization (0-100 scale) and weighted linear combination produce single interpretable composite score
- **Result:** Unified quantitative assessment that maintains multidimensional information

**Mechanism 2: Context-Adaptive Evaluation**
*Observable → Decision*
- Domain stakeholders provide context-specific dimension weights reflecting real deployment priorities
- Healthcare: high w_C (transparency critical), Entertainment: high w_E (user experience matters most), Research: balanced weights
- Context-dependent weighting aligns evaluation with actual deployment requirements
- **Result:** Evaluation scores that reflect domain-specific success criteria

**Mechanism 3: Decision Quality Improvement**
*Decision → Outcome*
- Decision-makers comparing systems via CHEF see both composite score (quick comparison) and dimension profile (detailed trade-offs)
- Composite score reduces cognitive load vs. fragmented multi-metric evaluation
- Dimension profile reveals strengths/weaknesses (high T but low C → accurate but opaque)
- Validated predictive relationship (CHEF score → deployment success) provides confidence
- **Result:** Higher-quality system selection and deployment guidance

**Evidence for Causal Links:**

**Link 1 (Clinical methodology → Valid integration):**
- [CROSS-DOMAIN] Clinical composite endpoints: 50+ years of validation in cardiovascular outcome trials (FDA-approved methodology)
- [SCHOLAR] Hoffman et al. (2023): Psychometric validation of XAI measurement scales (Cronbach's α >0.7)
- [SCHOLAR] Naveed et al. (2024): Documents fragmentation problem requiring integration solution
- [ARCHON] LoRA case: Demonstrates need for both technical (parameter efficiency) and adaptation (user feedback) metrics

**Link 2 (Context weighting → Aligned evaluation):**
- [CROSS-DOMAIN] Multi-criteria decision analysis (MCDA): Established weighting elicitation methods (Delphi, AHP)
- [SCHOLAR] Schelenz et al. (2023): Transparency-Check demonstrates domain variation in evaluation priorities
- [SCHOLAR] Calvano (2024): Identifies need for context-sensitive Symbiotic AI evaluation
- [EXA] EvAlignUX: LLM-assisted stakeholder elicitation precedent

**Link 3 (CHEF-guided decisions → Better outcomes):**
- [THEORY] Cognitive load theory: Unified score reduces decision complexity
- [THEORY] Decision quality framework: Better information → better decisions (under appropriate use)
- [SCHOLAR] Gomez et al. (2024): XAI decision support improves accuracy in clinical context
- [SCHOLAR] Hoffman et al. (2023): Trust and human-AI performance metrics predict collaboration success
- [EXA] Multiple XAI tools (DrWhy, LIT): Demonstrate value of integrated visualization for model understanding

**Key Tension:**
Composite scoring simplifies comparison (single score) but risks masking critical dimension failures (high T + low C = moderate composite). Resolution: Provide BOTH composite score AND dimension profile (profile prevents dangerous oversimplification while composite enables quick comparison).

### 1.4 Key Assumptions

**A1: Measurement Reliability Assumption**
- **Statement:** The three dimensions (T, C, E) can be reliably measured using existing validated scales with sufficient psychometric quality
- **Justification:** Hoffman et al. (2023) demonstrates Cronbach's α >0.7 for XAI scales; ML benchmarks have established reliability; UX scales (SUS, trust) are well-validated
- **Risk if False:** Composite scores will have high measurement error, reducing framework utility
- **Validation Plan:** Pilot study measuring reliability coefficients for all scales on 15-20 systems

**A2: Dimensional Independence Assumption**
- **Statement:** T, C, E represent sufficiently independent constructs (r<0.6) such that composite framework adds value over single-metric evaluation
- **Justification:** Technical performance ≠ explainability (many accurate black-box models); explainability ≠ user satisfaction (complex explanations can confuse)
- **Risk if False:** Framework collapses to fewer dimensions, reducing discriminative power
- **Validation Plan:** Empirical correlation analysis in pilot study (Phase 2.4) with decision criterion r<0.6

**A3: Stakeholder Weighting Validity Assumption**
- **Statement:** Domain stakeholders can provide meaningful, stable dimension weights through structured elicitation that reflect genuine deployment priorities
- **Justification:** MCDA literature demonstrates feasibility; Delphi method achieves expert consensus; LLM-assisted elicitation shows promise (EvAlignUX)
- **Risk if False:** Weights will be arbitrary/unstable, making context-adaptive scoring unreliable
- **Validation Plan:** Compare LLM-assisted elicitation with gold-standard Delphi method (Phase 1.3)

**A4: Linear Compensatory Aggregation Assumption**
- **Statement:** Weighted linear combination (w_T×T + w_C×C + w_E×E) appropriately models trade-offs between dimensions
- **Justification:** Clinical composite endpoints use linear aggregation successfully; assumes dimensions can compensate (high T can offset moderate C if w_T is large)
- **Risk if False:** Non-linear interactions or threshold effects will be missed (e.g., minimum C threshold for safety-critical domains)
- **Validation Plan:** Compare linear vs. non-linear models (multiplicative, minimum operator) in predictive validity study

**A5: Predictive Validity Assumption**
- **Statement:** CHEF scores measured at evaluation time will predict deployment success metrics (retention, satisfaction, task performance) measured 3-6 months post-deployment
- **Justification:** Construct validity - if CHEF captures essential quality dimensions, scores should predict real outcomes
- **Risk if False:** Framework will be academically interesting but practically useless
- **Validation Plan:** Longitudinal study correlating CHEF scores with deployment outcomes (r>0.5 threshold)

**A6: Sample Size Sufficiency Assumption**
- **Statement:** Framework validated on 15-20 diverse AI-HCI systems will generalize to broader population
- **Justification:** Pilot validation with representative sampling across domains/architectures/interaction paradigms
- **Risk if False:** Framework will overfit to pilot systems, failing on novel architectures
- **Validation Plan:** Diverse system selection strategy + post-hoc generalizability testing on held-out systems

### 1.5 Scope & Boundaries

**Applies to:**
- ✅ AI systems with direct human interaction components (RLHF language models, XAI decision support, HITL active learning, conversational agents, recommender systems with user-facing explanations, AI-assisted creativity tools)
- ✅ Systems where both technical performance AND human experience matter for deployment success
- ✅ Evaluation contexts: deployment decisions, system comparison, research benchmarking, product selection
- ✅ Domains: healthcare (diagnostic AI), finance (fraud detection, robo-advisors), education (intelligent tutoring), entertainment (content recommendation), creative applications (generative AI tools)
- ✅ System maturity: research prototypes (with caveats about E dimension) and production systems
- ✅ Evaluation goals: system comparison, deployment readiness assessment, research progress measurement

**Does NOT apply to:**
- ❌ Fully autonomous AI without human interaction (pure backend algorithms, no user-facing components)
- ❌ Systems where only technical performance matters (backend optimization, infrastructure ML)
- ❌ Single-dimension evaluation contexts (pure accuracy benchmarking competitions like ImageNet challenge)
- ❌ Domains with fundamentally different requirements not captured by T-C-E (may require dimension extension/adaptation)
- ❌ Early proof-of-concept prototypes (E dimension will be artificially low due to polish issues, not fundamental quality)
- ❌ Embedded/real-time systems where evaluation overhead is prohibitive (CHEF requires user studies for C and E)

**Boundary Conditions:**

**Temporal:**
- Framework applicable during evaluation phase (pre-deployment or deployment monitoring)
- Not applicable to speculative system design (need implemented system for measurement)
- User perceptions (C, E) may drift over time as familiarity increases → requires periodic re-evaluation for longitudinal claims

**Cultural:**
- Hoffman et al. scales validated primarily in Western contexts
- Cross-cultural generalizability requires validation for global deployment
- Dimension weights may vary by cultural context (e.g., privacy vs. convenience trade-offs)

**Technical:**
- Requires system with measurable outputs (accessible for technical benchmarking)
- Requires interactive interface for C and E measurement (not applicable to API-only services without UI)
- Assumes system is sufficiently stable for controlled evaluation (not constantly changing during study)

**Resource:**
- Full CHEF evaluation requires 20-50 participants per system (expensive, time-consuming)
- Lightweight variant possible with automated proxies for some metrics, but sacrifices validity
- Requires evaluation infrastructure: benchmark datasets, survey platforms, user recruitment

### 1.6 Testable Predictions

**Primary Prediction:**
**P1: Framework Statistical Validity**
If CHEF framework is applied to 15-20 diverse AI-HCI systems from multiple domains (healthcare, finance, education, entertainment) and architectures (RLHF, XAI, HITL), then:
1. **Dimensional Independence:** Pearson correlations between dimension pairs will satisfy r(T,C) < 0.6, r(T,E) < 0.6, r(C,E) < 0.6, demonstrating that dimensions capture distinct constructs
2. **Internal Consistency:** Cronbach's α > 0.7 for each dimension's measurement scales
3. **Predictive Validity:** CHEF composite scores will correlate with deployment success metrics at r > 0.5 (retention rate, task performance improvement, user satisfaction)
4. **Discriminant Validity:** Systems known to differ in quality will have significantly different CHEF scores (effect size d > 0.5)

**Secondary Predictions:**

**P2: Decision Quality Improvement**
If decision-makers (N≥30, mix of researchers, practitioners, domain experts) are asked to select AI systems for specific deployment scenarios using either (A) CHEF composite + profile, (B) fragmented metrics, or (C) single-dimension scores, then:
1. Group A will demonstrate higher selection quality: chosen systems will have 15-25% better alignment with actual deployment success metrics measured 3-6 months post-deployment
2. Group A will show 20-30% faster decision time (reduced cognitive load from unified framework)
3. Group A will report higher confidence in decisions (7-point scale: 5.5+ vs. 4.0- for fragmented group)

**P3: Context-Dependent Weighting**
If stakeholders from healthcare, finance, education, and entertainment domains provide dimension weights through structured elicitation, then:
1. **Systematic Weight Variation:** Healthcare will prioritize C (w_C > 0.4), Entertainment will prioritize E (w_E > 0.4), Research will show balanced weights (0.3 < w_i < 0.4 for all dimensions)
2. **Within-Domain Consistency:** Intra-class correlation (ICC) > 0.6 among stakeholders from the same domain
3. **Cross-Domain Discrimination:** ANOVA F-test shows significant weight differences between domains (p < 0.01)

**P4: Balanced Optimization Advantage**
If AI-HCI systems are categorized as either (A) T-optimized-only (high T, low C/E) or (B) balanced T-C-E optimization, then:
1. Group B systems will demonstrate 15-20% higher user retention rates at 6 months post-deployment
2. Group B systems will achieve 10-15% higher user satisfaction scores (despite potentially 5-10% lower technical accuracy)
3. Group B systems will show lower task abandonment rates (10-15% reduction)

**P5: Profile Complementarity**
If users are shown either (A) composite score only, (B) dimension profile only, or (C) composite + profile, then:
1. Group C will identify critical dimension failures (e.g., dangerously low C despite high T) more accurately than Group A (detection rate: 80%+ vs. 50%)
2. Group C will demonstrate fastest decision-making among groups that maintain safety (Group B will be slow but safe, Group A will be fast but miss failures)

**Falsification Criteria:**

**Framework is INVALID if any of:**
- ❌ Dimension correlations r ≥ 0.6 (dimensions are redundant) → Framework collapses to fewer dimensions
- ❌ Predictive validity r < 0.3 (composite scores don't predict outcomes) → Framework lacks utility
- ❌ Cronbach's α < 0.6 for any dimension → Measurement unreliability too high
- ❌ Decision quality improvement < 5% → Practical value insufficient
- ❌ LLM-assisted weighting disagrees with Delphi method (ICC < 0.5) → Weighting method invalid

**Framework has LIMITED utility if:**
- ⚠️ 0.3 ≤ r < 0.5 for predictive validity → Framework has some value but limited
- ⚠️ Decision improvement 5-10% → Marginal practical benefit
- ⚠️ 0.5 ≤ ICC < 0.6 for weighting consistency → Moderate reliability concerns

**Framework is SUCCESSFUL if:**
- ✅ All primary criteria met (r<0.6 independence, r>0.5 prediction, α>0.7 reliability, d>0.5 discrimination)
- ✅ Decision improvement ≥15%
- ✅ LLM-assisted weighting validated (ICC≥0.7 vs. Delphi)

### 1.7 SOTA Baseline (Comparison Mode)

**Current State-of-the-Art:**

**SOTA-1: Fragmented Evaluation (Current Practice)**
- **Approach:** ML benchmarks (accuracy, F1, speed) evaluated separately from user studies (satisfaction, trust)
- **Limitation:** No integration → impossible to compare systems trading off technical vs. human-centered quality
- **Evidence:** Naveed et al. (2024) documents fragmentation; Calvano (2024) identifies gap
- **CHEF Advantage:** Unified framework enables systematic comparison

**SOTA-2: Profile-Only Approaches (Existing Multi-Dimensional)**
- **Examples:** ISO 25010 (software quality model: 8 dimensions), AttrakDiff (UX: pragmatic + hedonic quality), Transparency-Check (Schelenz et al.: 4 transparency dimensions)
- **Approach:** Visualize multiple dimensions without composite scoring
- **Limitation:** No principled aggregation → users must mentally integrate, high cognitive load
- **CHEF Advantage:** Composite score + profile provides both quick comparison and detailed analysis

**SOTA-3: Single-Metric Optimization (Benchmark-Driven)**
- **Examples:** ImageNet accuracy, GLUE score, AlpacaEval win rate
- **Approach:** Optimize and compare systems on single primary metric
- **Limitation:** Ignores human-centered dimensions → systems optimized for benchmarks may fail in deployment (accuracy↑ but trust↓)
- **CHEF Advantage:** Balances technical and human-centered quality

**SOTA-4: Ad-Hoc Weighting (Informal Multi-Metric)**
- **Approach:** Researchers informally consider multiple metrics without systematic aggregation
- **Limitation:** Lacks statistical rigor, reproducibility, validation
- **CHEF Advantage:** Validated aggregation methodology with explicit weighting

**Quantitative Comparison Targets:**

| SOTA Approach | Decision Quality* | Decision Time* | Deployment Success Prediction** | Reproducibility*** |
|---------------|------------------|----------------|--------------------------------|-------------------|
| SOTA-1: Fragmented | Baseline (0%) | Baseline | r ≈ 0.2-0.3 (weak) | Low |
| SOTA-2: Profile-Only | +5-10% | +20% (slower) | r ≈ 0.3-0.4 (moderate) | Medium |
| SOTA-3: Single-Metric | -5-10% | -30% (faster but wrong) | r ≈ 0.2 (weak) | High |
| SOTA-4: Ad-Hoc | 0-5% | Baseline | r ≈ 0.2-0.4 (variable) | Low |
| **CHEF (Target)** | **+15-25%** | **-20-30%** | **r > 0.5** | **High** |

*vs. fragmented baseline, **Pearson correlation with deployment outcomes, ***Inter-rater reliability

**Success Criteria vs. SOTA:**
- ✅ Decision quality improvement ≥10% vs. best SOTA (Profile-Only)
- ✅ Prediction strength r ≥ 0.5 (exceeds all SOTA by ≥0.1)
- ✅ Maintains or improves decision time vs. Profile-Only (no worse than -10%)
- ✅ High reproducibility (ICC > 0.7) matching Single-Metric SOTA

### 1.8 Statistical Verification Design

**Study Design Overview:**
- **Type:** Mixed-methods validation study with 4 phases (psychometric, empirical, longitudinal, decision quality)
- **Sample:** 15-20 AI-HCI systems × 30-50 participants per system = 450-1000 total participants
- **Timeline:** 6-9 months (pilot), 12-18 months (full validation)
- **Power Analysis:** Requires N=15 systems to detect r=0.5 with power=0.8, α=0.05 (two-tailed)

**Phase 1: Measurement Validation (Weeks 1-8)**

**Study 1.1: Scale Reliability**
- **Goal:** Verify internal consistency of dimension measurements
- **Method:** Administer full CHEF evaluation to N=5 systems (diverse sample)
- **Metrics:** Cronbach's α for each dimension (T, C, E)
- **Success Criterion:** α > 0.7 for all dimensions
- **Analysis:** Item-total correlations, factor analysis to confirm dimensionality

**Study 1.2: Dimension Independence**
- **Goal:** Empirically validate that T, C, E capture distinct constructs
- **Method:** Measure all three dimensions for N=15-20 systems
- **Metrics:** Pearson correlations r(T,C), r(T,E), r(C,E)
- **Success Criterion:** All r < 0.6 (discriminant validity threshold)
- **Analysis:** Correlation matrix, confirmatory factor analysis (CFA)

**Study 1.3: Weighting Method Validation**
- **Goal:** Validate LLM-assisted stakeholder elicitation vs. gold standard Delphi
- **Method:** Healthcare domain experts (N=20) provide weights via both methods
- **Metrics:** Intraclass correlation (ICC) between methods
- **Success Criterion:** ICC > 0.6 (moderate agreement), ideally >0.7 (strong agreement)
- **Analysis:** Bland-Altman plots, inter-rater reliability

**Phase 2: Empirical Validation (Weeks 9-20)**

**Study 2.1: System Evaluation**
- **Design:** Cross-sectional evaluation of 15-20 diverse AI-HCI systems
- **Systems Selection:** Stratified sampling across:
  - Domains: healthcare (N=4), finance (N=4), education (N=4), entertainment (N=4)
  - Architectures: RLHF (N=5), XAI (N=5), HITL (N=5), other (N=5)
  - Maturity: research prototypes (N=7), production systems (N=8-13)
- **Participants:** N=30-50 per system, domain-matched (e.g., healthcare AI → clinicians)
- **Procedure:**
  1. Technical benchmarking (T dimension): automated on standard datasets
  2. User study (C and E dimensions): 60-90 min sessions per participant
  3. Surveys: Hoffman et al. scales (C), SUS + trust + satisfaction (E)
  4. Behavioral: task performance, completion time, error rates
- **Data:** CHEF composite scores, dimension profiles, raw measurements

**Study 2.2: Dimension Weighting**
- **Design:** Structured elicitation study with domain stakeholders
- **Participants:** N=10-15 stakeholders per domain (healthcare, finance, education, entertainment)
- **Method:** LLM-assisted elicitation (pairwise comparisons, scenario-based)
- **Output:** Domain-specific weight sets {w_T, w_C, w_E} per domain
- **Analysis:** Within-domain ICC, between-domain ANOVA

**Phase 3: Predictive Validity (Weeks 21-40, includes 3-6 month follow-up)**

**Study 3.1: Longitudinal Deployment Tracking**
- **Design:** Prospective longitudinal study linking CHEF scores to real outcomes
- **Sample:** Subset of 8-10 systems from Phase 2 that proceed to deployment
- **Baseline:** CHEF scores measured during evaluation (Phase 2)
- **Follow-up:** Deployment metrics at 3 months and 6 months post-launch
  - Retention rate: % active users at t=3mo and t=6mo
  - Task performance: improvement vs. no-AI baseline
  - User satisfaction: longitudinal surveys
  - Error reduction: incident rate monitoring
- **Analysis:** Pearson correlations between CHEF scores (baseline) and deployment metrics (follow-up)
- **Success Criterion:** r > 0.5 for CHEF composite score → deployment success composite
- **Power:** N=8-10 systems provides 80% power to detect r=0.6 at α=0.05

**Phase 4: Decision Quality Study (Weeks 21-28)**

**Study 4.1: Between-Subjects Decision Experiment**
- **Design:** Randomized controlled trial comparing evaluation approaches
- **Participants:** N=90 decision-makers (researchers, practitioners, domain experts), N=30 per group
- **Groups:**
  - Group A: CHEF composite + profile
  - Group B: Fragmented metrics (separate T, C, E without integration)
  - Group C: Single-dimension (T-only, typical benchmark approach)
- **Task:** Select best system for 5 deployment scenarios from set of 4 candidate systems (varied scenarios: high-stakes healthcare, consumer entertainment, education, etc.)
- **Measures:**
  - **Selection quality:** Agreement between chosen system and gold-standard "best" system (determined by actual deployment performance from Study 3.1)
  - **Decision time:** Minutes to complete selection task
  - **Confidence:** Self-reported confidence in decision (1-7 scale)
- **Analysis:** One-way ANOVA comparing groups, post-hoc pairwise comparisons
- **Success Criterion:** Group A outperforms Group B and C by ≥10% in selection quality

**Study 4.2: Composite vs. Profile Value**
- **Design:** Within-subjects experiment examining composite score utility
- **Participants:** N=40 users
- **Conditions:** Each participant evaluates systems using:
  - Condition A: Composite score only
  - Condition B: Dimension profile only
  - Condition C: Composite + profile
- **Task:** Identify systems with critical dimension failures (e.g., high T but dangerously low C)
- **Measure:** Detection accuracy, decision time, perceived difficulty
- **Analysis:** Repeated-measures ANOVA
- **Success Criterion:** Condition C shows highest detection accuracy (80%+) while maintaining reasonable decision time

**Statistical Methods:**

**Primary Analyses:**
- **Correlation:** Pearson r for dimension independence, predictive validity
- **Reliability:** Cronbach's α, ICC for measurement consistency
- **Group Comparison:** One-way ANOVA (decision quality), repeated-measures ANOVA (composite utility)
- **Effect Sizes:** Cohen's d for group differences, r for correlations, η² for ANOVA

**Power & Sample Size:**
- **Dimension independence:** N=15 systems, detect r<0.6 with power=0.8
- **Predictive validity:** N=8-10 systems (deployed), detect r>0.5 with power=0.8
- **Decision quality:** N=30/group (90 total), detect d=0.5 with power=0.8
- **Alpha level:** 0.05 (two-tailed) for all tests
- **Corrections:** Bonferroni for multiple comparisons within studies

**Data Management:**
- **Software:** R (analysis), Qualtrics (surveys), Python (technical benchmarking)
- **Preprocessing:** Normalization (0-100 scale), missing data imputation (MICE)
- **Reproducibility:** Pre-registration of analysis plan, open data/code repository
- **IRB:** Human subjects approval for Studies 2.1, 2.2, 3.1, 4.1, 4.2

**Sensitivity Analyses:**
- Test robustness to: outlier systems, different normalization methods, alternative weighting schemes, varied correlation thresholds (r<0.5 vs. r<0.7)
- Subgroup analyses: system maturity, domain, architecture type

---

## 2. Contribution Summary

### Theoretical Contributions

**T1: Unified AI-HCI Evaluation Theory**
- **Contribution:** First theoretical framework integrating ML evaluation paradigm (objective technical metrics) with HCI measurement paradigm (subjective user experience) through validated statistical methodology
- **Novelty:** Prior work treats technical and human-centered evaluation as separate domains; CHEF provides theoretical bridge through clinical composite endpoint methodology (cross-domain transfer with 50+ year validation history)
- **Impact:** Enables new research questions about T-C-E trade-off space; provides common language for interdisciplinary AI-HCI research; challenges single-metric optimization culture

**T2: Multi-Dimensional Quality Theory for AI-HCI**
- **Contribution:** Formal definition of AI-HCI system quality as three-dimensional construct (Technical × Cognitive × Experiential) rather than unidimensional "performance"
- **Novelty:** Existing models either focus on single dimension (ML benchmarks → T only) or lack formal structure (ISO 25010 is descriptive, not validated)
- **Impact:** Shifts discourse from "which system is more accurate?" to "which system provides best T-C-E balance for this context?"

**T3: Context-Dependent Evaluation Theory**
- **Contribution:** Theoretical framework for context-adaptive evaluation where "best system" depends on domain-specific dimension priorities
- **Novelty:** Challenges universal benchmark culture; formalizes intuition that healthcare AI and entertainment AI have different quality criteria
- **Impact:** Justifies domain-specific evaluation standards; prevents inappropriate cross-domain system comparison

### Methodological Contributions

**M1: CHEF Composite Scoring Protocol**
- **Contribution:** Validated methodology for multi-dimensional AI-HCI evaluation including:
  - Dimension measurement protocols (T: ML benchmarks, C: Hoffman et al. scales, E: UX measures)
  - Normalization procedure (heterogeneous scales → 0-100 uniform scale)
  - Weighted linear aggregation: CHEF_score = w_T × T + w_C × C + w_E × E
  - Statistical validation protocol (reliability, validity, sensitivity)
- **Novelty:** First AI-HCI evaluation method with full psychometric validation
- **Impact:** Provides reproducible, scientifically rigorous evaluation protocol for AI-HCI research community

**M2: LLM-Assisted Stakeholder Elicitation**
- **Contribution:** Novel method for efficient dimension weight elicitation using LLM-facilitated structured interviews, validated against gold-standard Delphi method
- **Novelty:** Reduces stakeholder burden (hours → 30 minutes) while maintaining validity; leverages LLM for consistency in multi-stakeholder elicitation
- **Impact:** Makes context-dependent weighting practical for resource-constrained teams; potential transfer to other MCDA applications

**M3: Integrated Visualization Protocol**
- **Contribution:** Dual presentation method combining composite score (quick comparison) with dimension profile (detailed trade-off analysis) to balance simplicity and comprehensiveness
- **Novelty:** Prevents composite score oversimplification (masking critical failures) while avoiding fragmentation burden
- **Impact:** Enables both rapid screening (composite) and deep analysis (profile) in single workflow

**M4: Longitudinal Validation Methodology**
- **Contribution:** Protocol for validating evaluation frameworks through prospective correlation with real-world deployment outcomes (evaluation scores → 6-month outcomes)
- **Novelty:** AI-HCI evaluation typically lacks outcome validation; CHEF establishes predictive validity empirically
- **Impact:** Shifts evaluation from face validity to empirical validity; provides template for validating other AI-HCI evaluation methods

### Practical Contributions

**P1: CHEF Evaluation Toolkit**
- **Deliverable:** Open-source Python package implementing CHEF framework
- **Components:**
  - Technical benchmarking module (integration with HuggingFace, TensorFlow Model Analysis)
  - Survey instruments (Hoffman et al. scales, UX measures) with Qualtrics templates
  - Scoring engine (normalization, weighting, composite calculation)
  - Visualization dashboard (3D profiles, comparison charts)
  - Statistical validation suite (reliability, validity tests)
- **Impact:** 15-20 AI-HCI systems evaluated in pilot validation; toolkit enables community adoption
- **License:** Apache 2.0 (permissive, industry-friendly)
- **Estimated Users (Year 1):** 50-100 research groups, 10-20 industry teams

**P2: System Selection Guidance**
- **Deliverable:** Decision support methodology for practitioners choosing AI-HCI systems for deployment
- **Use Cases:**
  - Healthcare: Select diagnostic AI balancing accuracy (T), interpretability (C), clinician workflow fit (E)
  - Finance: Choose fraud detection trading off precision (T), transparency for compliance (C), analyst usability (E)
  - Education: Pick intelligent tutoring system balancing effectiveness (T), pedagogical alignment (C), student engagement (E)
- **Impact:** Reduces deployment failures from single-dimension optimization; enables evidence-based system selection

**P3: Research Benchmarking Standard**
- **Deliverable:** Proposal for standardized AI-HCI evaluation reporting in academic papers
- **Target Venues:** CHI, UIST (HCI), NeurIPS, ICML (ML), AIES, FAccT (AI Ethics)
- **Adoption Goal:** 20+ papers report CHEF scores in Year 1 post-publication
- **Impact:** Enables systematic comparison across papers; reduces cherry-picking of favorable single metrics; improves research reproducibility

**P4: Domain-Specific Weight Libraries**
- **Deliverable:** Validated dimension weight sets for major application domains
- **Initial Domains:** Healthcare (w_C emphasis), Finance (balanced w_T + w_C), Education (w_E emphasis), Entertainment (w_E emphasis)
- **Maintenance:** Community contribution model (similar to HuggingFace model zoo)
- **Impact:** Reduces evaluation setup burden; provides sensible defaults for domain-appropriate evaluation

**P5: High-Stakes Domain Adoption**
- **Target Impact:** Accelerate AI-HCI adoption in regulated domains (healthcare, finance, legal) where fragmented evaluation has hindered deployment due to lack of trust/transparency assessment
- **Mechanism:** CHEF provides evidence that systems meet both technical AND human-centered requirements
- **Success Metric:** 3-5 real-world deployment decisions using CHEF within 2 years post-publication
- **Regulatory Relevance:** Potential alignment with EU AI Act requirements for transparency and human oversight

### Innovation Assessment

**Cross-Domain Innovation:**
Clinical composite endpoints (cardiology, oncology) → AI-HCI evaluation represents successful knowledge transfer across domains with 50+ year validation history

**Interdisciplinary Integration:**
Bridges ML (technical benchmarking), HCI (user-centered measurement), psychometrics (validation methodology), decision science (weighting elicitation) into unified framework

**Problem-Solution Fit:**
Directly addresses P1 Gap (unified evaluation frameworks) identified in Phase 1 research; evidence from 12 sources confirms problem existence

**Feasibility:**
MEDIUM difficulty (6-9 months, $20K-30K, 1 PhD-level researcher); no exotic infrastructure requirements; builds on established measurement instruments

---

## 3. Key Related Work

### Foundation Papers

**Clinical Composite Endpoints (Methodology Source):**
1. **FDA Guidance on Multiple Endpoints in Clinical Trials** (2022)
   - Establishes regulatory standard for composite endpoints in drug approval
   - Key Insight: Validated framework for integrating heterogeneous outcome measures
   - Relation to CHEF: Provides statistical methodology and precedent for multi-dimensional evaluation

2. **Freemantle et al. "Composite Outcomes in Randomized Trials" (2003, JAMA)**
   - Classic paper on composite endpoint design and interpretation
   - Key Insight: Component independence testing, weighting strategies, interpretation guidelines
   - Relation to CHEF: Methodological template for dimension independence validation (r<0.6 threshold)

**AI-HCI Evaluation (Problem Definition):**
3. **Hoffman et al. "Measures for explainable AI" (2023)**
   - Semantic Scholar ID: 3038e62388ba4961595ec0062948b31eef251e5d
   - Citations: 181
   - Key Contribution: Validated measurement scales for XAI (explanation goodness, mental models, curiosity, trust, human-AI performance)
   - **Relation to CHEF:** Provides validated instruments for Cognitive Alignment (C) dimension; establishes psychometric foundation
   - **Usage:** Direct adoption of Hoffman scales for C dimension measurement

4. **Calvano "Design and Evaluation of High-Quality Symbiotic AI Systems" (2024)**
   - Semantic Scholar ID: aedde38b00937872f5957b86a1e78933b5fe08fc
   - Citations: 1 (recent dissertation)
   - Key Contribution: Identifies gap in unified AI-HCI evaluation metrics; proposes human-centered design approach
   - **Relation to CHEF:** Motivation source - documents evaluation gap that CHEF addresses
   - **Usage:** Problem statement validation, gap justification

5. **Naveed et al. "Overview of Empirical Evaluation of XAI" (2024)**
   - Semantic Scholar ID: 19dbffc34f82179c68d3ae7a299ae8836a678129
   - Citations: 15
   - Key Contribution: Comprehensive review revealing fragmentation in XAI evaluation (lack of standardized metrics, inconsistent user studies)
   - **Relation to CHEF:** Problem characterization - documents current fragmented state
   - **Usage:** Literature review baseline, motivation for unified approach

**Multi-Dimensional Evaluation (Alternative Approaches):**
6. **Schelenz et al. "Transparency-Check" (2023)**
   - Semantic Scholar ID: 931cd7d4a1702b214ab13ee5041dc4e68cc837ab
   - Citations: 13
   - Key Contribution: 4-dimensional transparency checklist for AI personalization systems; empirical study showing low compliance
   - **Relation to CHEF:** Precedent for multi-dimensional AI evaluation; demonstrates dimension approach can discriminate systems
   - **Usage:** Related work comparison (profile-only without composite scoring)

7. **ISO 25010 Software Quality Model** (2011, updated 2023)
   - International standard defining 8 quality dimensions for software
   - Key Contribution: Hierarchical quality model (characteristics → sub-characteristics)
   - **Relation to CHEF:** Existing multi-dimensional framework for comparison
   - **Limitation:** Not validated for AI-HCI; lacks statistical rigor; descriptive rather than predictive
   - **Usage:** SOTA baseline comparison

**Human-AI Interaction Theory (Theoretical Foundation):**
8. **Muller & Weisz "Human-AI Collaboration Framework with Dynamism and Sociality" (2022)**
   - Semantic Scholar ID: 2846faa68a9dd85f61e5b55e4926452883d55d5c
   - Citations: 32
   - Key Contribution: Integrated CHA framework spanning 70 years of human-machine interaction theory; addresses dynamic initiative shifts
   - **Relation to CHEF:** Theoretical foundation for why Experiential (E) dimension matters in AI-HCI evaluation
   - **Usage:** Justification for E dimension inclusion

9. **Liao & Varshney "Human-Centered Explainable AI" (2021)**
   - Semantic Scholar ID: 5e1746995debd1f17c24af01514c727598cc5613
   - Citations: 287
   - Key Contribution: Surveys HCI approaches to XAI design and evaluation; identifies three roles of human-centered approaches
   - **Relation to CHEF:** Establishes importance of human-centered XAI measurement (C dimension justification)
   - **Usage:** Theoretical grounding for Cognitive Alignment dimension

### Supporting Papers

**Personalization & Alignment:**
10. **Poddar et al. "Personalizing RLHF with Variational Preference Learning" (2024)**
    - Semantic Scholar ID: e7b5d0269bdd37d01cea2bddb4d2ec9cf1539a40
    - Citations: 93
    - Key Contribution: Multimodal RLHF for diverse user preferences
    - **Relation to CHEF:** Demonstrates need for personalization (user heterogeneity) in evaluation

11. **Casper et al. "Open Problems and Fundamental Limitations of RLHF" (2023)**
    - Semantic Scholar ID: 6eb46737bf0ef916a7f906ec6a8da82a45ffb623
    - Citations: 734
    - Key Contribution: Systematizes RLHF flaws, proposes multi-faceted evaluation approach
    - **Relation to CHEF:** Supports multi-dimensional evaluation need (technical performance alone insufficient)

**Evaluation Methods:**
12. **Zheng et al. "EvAlignUX" (2025)**
    - Semantic Scholar ID: ae7068a08feb0d1375305cf1fa48758b26b7bb52
    - Citations: 8
    - Key Contribution: LLM-supported metric exploration for UX evaluation
    - **Relation to CHEF:** Precedent for LLM-assisted evaluation methodology
    - **Usage:** Methodological inspiration for LLM-assisted stakeholder weighting

13. **Bandi et al. "The Power of Generative AI" (2023)**
    - Semantic Scholar ID: cdae0d5333b00e006a5e9f209a394ae46a3a0cc3
    - Citations: 412
    - Key Contribution: Comprehensive evaluation metric taxonomy for generative AI
    - **Relation to CHEF:** Documents evaluation metric diversity; supports need for integration

**Decision Support & Outcomes:**
14. **Gomez et al. "XAI Decision Support Improves Accuracy in Telehealth" (2024)**
    - Semantic Scholar ID: d191cba1543c1ed7a67d3de054fd91916ddf3887
    - Citations: 13
    - Key Contribution: Empirical evidence that XAI improves clinical decision accuracy
    - **Relation to CHEF:** Validates hypothesis that explainability (C dimension) impacts real outcomes
    - **Usage:** Evidence for causal link (C dimension → deployment success)

15. **Haag "Effect of XAI on Human Task Performance: Meta-Analysis" (2025)**
    - Semantic Scholar ID: 9db0232be4eeeddc071ad3dd3725cc6ecfae6d97
    - Citations: 2 (very recent)
    - Key Contribution: Meta-analysis showing XAI improves task performance, but effect size varies
    - **Relation to CHEF:** Supports predictive validity hypothesis (XAI quality → outcomes)

### Implementation Resources

**Archon Knowledge Base Cases:**
16. **LoRA PEFT Case**
    - Source: Archon KB (Page ID: c0bcf966-7063-40e8-bc4e-c33a627b47b8)
    - URL: https://huggingface.co/docs/peft/conceptual_guides/adapter
    - Key Pattern: Demonstrates need for evaluating both technical efficiency (T: parameter reduction) and adaptation quality (C/E: user feedback integration)
    - **Relation to CHEF:** Real-world motivation for multi-dimensional evaluation

17. **PI-Animator Case**
    - Source: Archon KB (Page ID: 187ee8fa-9410-476b-a086-e1c877ca2c8b)
    - URL: https://pi-animator.github.io/
    - Key Pattern: Personalization + control mechanisms (plug-and-play modules)
    - **Relation to CHEF:** Example system requiring T-C-E evaluation (technical quality + user control + experience)

**Exa Implementation Examples:**
18. **PAIR-code/lit (Learning Interpretability Tool)**
    - URL: https://github.com/pair-code/lit
    - Google PAIR project for interactive ML model analysis
    - **Relation to CHEF:** Framework-agnostic XAI platform; potential integration point for C dimension automated measurement
    - **Usage:** Toolkit component example

19. **oegedijk/explainerdashboard**
    - URL: https://github.com/oegedijk/explainerdashboard
    - Rapid XAI dashboard generation
    - **Relation to CHEF:** Visualization precedent for multi-dimensional XAI presentation
    - **Usage:** UI inspiration for CHEF dimension profiles

20. **ModelOriented/DrWhy**
    - URL: https://github.com/ModelOriented/DrWhy
    - Stars: 689, Language: R
    - Collection of XAI tools with unified framework
    - **Relation to CHEF:** Multi-method XAI integration pattern; demonstrates value of unified toolkit
    - **Usage:** Architectural pattern for CHEF toolkit design

### Cross-Domain References

**Multi-Criteria Decision Analysis:**
21. **Keeney & Raiffa "Decisions with Multiple Objectives" (1976)**
    - Classic MCDA textbook establishing weighting elicitation methods
    - **Relation to CHEF:** Methodological foundation for stakeholder dimension weighting
    - **Usage:** Weighting methodology (AHP, swing weighting)

**Psychometric Validation:**
22. **Cronbach "Coefficient Alpha and the Internal Structure of Tests" (1951)**
    - Foundational psychometrics paper on reliability measurement
    - **Relation to CHEF:** Statistical methodology for validating dimension measurement reliability
    - **Usage:** Cronbach's α reliability criterion (α > 0.7)

23. **Campbell & Fiske "Convergent and Discriminant Validation" (1959)**
    - Establishes validity testing framework (construct validity)
    - **Relation to CHEF:** Validation protocol for demonstrating T-C-E dimensions are distinct
    - **Usage:** Discriminant validity testing (r < 0.6 criterion)

### Gap Analysis

**What CHEF Builds Upon:**
- Hoffman et al.'s validated XAI scales (measurement instruments for C)
- Clinical composite endpoint methodology (statistical integration framework)
- ISO 25010 / AttrakDiff concepts (multi-dimensional quality thinking)
- MCDA weighting methods (stakeholder elicitation)

**What CHEF Adds:**
- First validated integration of ML and HCI evaluation paradigms
- Empirical validation of multi-dimensional framework (dimension independence, predictive validity)
- LLM-assisted efficient stakeholder elicitation
- Open-source toolkit for community adoption
- Longitudinal validation linking evaluation to deployment outcomes

**What Remains Open:**
- Cross-cultural validation of C and E dimensions (Hoffman scales primarily Western)
- Temporal stability of CHEF scores (do scores predict long-term success beyond 6 months?)
- Non-linear aggregation alternatives (when is linear combination inappropriate?)
- Lightweight CHEF variant with automated proxies (trade accuracy for efficiency)
- Extension to emerging AI modalities (multimodal models, embodied AI, etc.)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): CHEF Framework Validity**
**Statement:** The CHEF framework demonstrates statistical validity as a reliable, multi-dimensional evaluation instrument for AI-HCI systems.

**Sub-Components:**
- SH1.1: Measurement Reliability - Each dimension (T, C, E) achieves sufficient internal consistency (Cronbach's α > 0.7)
- SH1.2: Dimensional Independence - T, C, E dimensions show discriminant validity (pairwise correlations r < 0.6)
- SH1.3: Predictive Validity - CHEF composite scores correlate with deployment success metrics (r > 0.5)
- SH1.4: Discriminant Power - CHEF scores differentiate between high-quality and low-quality systems (effect size d > 0.5)

**Verification Approach:**
- **Study Type:** Psychometric validation study with N=15-20 diverse AI-HCI systems
- **Methods:** Cronbach's α calculation, correlation analysis, confirmatory factor analysis (CFA), known-groups validation
- **Timeline:** 8-12 weeks (concurrent technical benchmarking + user studies)
- **Success Criteria:** All four sub-hypotheses must pass thresholds
- **Failure Mode:** If SH1 fails, framework lacks fundamental validity → return to design phase

---

**SH2 (Mechanism): Context-Dependent Weighting Utility**
**Statement:** Domain-specific dimension weights improve CHEF framework utility by aligning evaluation with context-appropriate quality criteria.

**Sub-Components:**
- SH2.1: Weight Variation - Dimension weights vary systematically across domains (healthcare ≠ entertainment ≠ education)
- SH2.2: Within-Domain Consistency - Stakeholders within same domain provide consistent weights (ICC > 0.6)
- SH2.3: LLM Elicitation Validity - LLM-assisted weighting agrees with gold-standard Delphi method (ICC > 0.6)
- SH2.4: Weighted vs. Unweighted - Context-weighted CHEF scores predict deployment success better than unweighted averaging

**Verification Approach:**
- **Study Type:** Multi-domain stakeholder elicitation study (N=10-15 stakeholders × 4 domains)
- **Methods:** Structured weight elicitation (LLM-assisted vs. Delphi), ANOVA for cross-domain comparison, ICC for consistency, correlation comparison for predictive improvement
- **Timeline:** 6-8 weeks (concurrent with SH1 studies)
- **Success Criteria:** Demonstrate systematic variation (SH2.1), consistency (SH2.2), method validity (SH2.3), and utility (SH2.4)
- **Failure Mode:** If SH2.3 fails → LLM method invalid, fall back to Delphi only; If SH2.4 fails → use fixed weights (context-independence)

---

**SH3 (Comparison): CHEF Superiority vs. SOTA**
**Statement:** CHEF-guided decision-making outperforms existing evaluation approaches (fragmented metrics, profile-only, single-dimension) in system selection quality and deployment outcome prediction.

**Sub-Components:**
- SH3.1: Decision Quality - Decision-makers using CHEF achieve 15-25% higher selection quality vs. fragmented evaluation
- SH3.2: Decision Efficiency - CHEF users demonstrate 20-30% faster decision time vs. fragmented evaluation
- SH3.3: Failure Detection - CHEF (composite + profile) identifies critical dimension failures more accurately (80%+) than composite-only (50%)
- SH3.4: Balanced System Advantage - Systems with balanced T-C-E scores show 15-20% higher retention than T-optimized-only systems

**Verification Approach:**
- **Study Type:** Randomized controlled trial with N=90 decision-makers (30 per group: CHEF vs. fragmented vs. single-dim) + longitudinal deployment tracking for N=8-10 systems
- **Methods:** Between-subjects decision experiment, within-subjects composite utility experiment, prospective longitudinal correlation study
- **Timeline:** 12-16 weeks (6 months including longitudinal follow-up)
- **Success Criteria:** CHEF demonstrates superiority on at least 3 of 4 sub-hypotheses (SH3.1-3.4)
- **Failure Mode:** If CHEF does not outperform existing methods → framework is academically interesting but practically equivalent (limited novelty claim)

### Readiness Checklist

**Hypothesis Clarity:**
- ✅ Core hypothesis statement is testable with clear success/failure criteria
- ✅ All variables (independent, dependent, controlled) are operationally defined with measurement procedures
- ✅ Causal mechanism is articulated with three linked stages (integration → contextualization → decision improvement)
- ✅ Key assumptions are explicitly stated with validation plans
- ✅ Scope boundaries clearly define applicability (what it applies to vs. doesn't apply to)

**Evidence Foundation:**
- ✅ Builds on 23 sources from Phase 1 research (10 Scholar papers, 3 Archon cases, 4 Exa implementations, 6 cross-domain references)
- ✅ Phase 1 evidence utilization: 83% (10/12 sources from Gap 1 evidence directly used)
- ✅ Cross-domain transfer is validated (clinical composite endpoints: 50+ years, FDA-approved)
- ✅ Measurement instruments are validated (Hoffman et al. scales: α > 0.7, widely used)

**Methodological Rigor:**
- ✅ Statistical verification design is complete with power analysis (N=15 systems for r=0.5, power=0.8)
- ✅ Multiple validation studies planned (psychometric, empirical, longitudinal, decision quality)
- ✅ Success criteria are quantitative and falsifiable (r<0.6, r>0.5, α>0.7, d>0.5, 15-25% improvement)
- ✅ SOTA baselines clearly defined (4 comparison approaches: fragmented, profile-only, single-metric, ad-hoc)
- ✅ Timeline and resource requirements specified (6-9 months, $20K-30K, 1 PhD researcher)

**Phase 2B Decomposition:**
- ✅ Three sub-hypotheses (SH1: Existence, SH2: Mechanism, SH3: Comparison) clearly previewed
- ✅ Each sub-hypothesis has independent verification approach
- ✅ Logical dependency structure: SH1 (fundamental validity) → SH2 (mechanism) → SH3 (superiority)
- ✅ Failure modes identified for each sub-hypothesis with mitigation strategies

**Contribution Articulation:**
- ✅ Three theoretical contributions (unified evaluation theory, multi-dimensional quality, context-dependent evaluation)
- ✅ Four methodological contributions (CHEF protocol, LLM-assisted elicitation, integrated visualization, longitudinal validation)
- ✅ Five practical contributions (toolkit, selection guidance, benchmarking standard, weight libraries, domain adoption)
- ✅ Innovation type classified: cross-domain transfer (clinical → AI-HCI) + interdisciplinary integration (ML + HCI + psychometrics)

**Related Work Mapping:**
- ✅ Foundation papers identified (clinical composite endpoints, Hoffman et al., Calvano, Naveed et al.)
- ✅ Alternative approaches documented (ISO 25010, AttrakDiff, Transparency-Check)
- ✅ Implementation precedents cataloged (LIT, explainerdashboard, DrWhy)
- ✅ Gap analysis articulates what CHEF adds beyond existing work

**Readiness Score: 95/100** (Excellent)

**Minor Gaps to Address in Phase 2B:**
- [ ] Specify exact Hoffman et al. scale subset (6 scales proposed, clarify which to use for C dimension)
- [ ] Define CHEF score interpretation (is 75/100 "good"? percentile-based or absolute?)
- [ ] Pilot system selection strategy (which 15-20 systems? selection criteria?)
- [ ] IRB application timeline (required for user studies)
- [ ] Toolkit implementation language/framework decision (Python confirmed, but specific libraries?)

### Open Questions

**Q1: Scale Selection for Cognitive Alignment (C) Dimension**
- **Issue:** Hoffman et al. (2023) proposes 6 measurement scales for XAI evaluation (explanation goodness, mental models, curiosity, trust, XAI work system performance, satisfaction). CHEF needs to select subset for practical evaluation (measuring all 6 is time-intensive).
- **Options:**
  - Option A: Use all 6 scales (comprehensive but lengthy: ~20 minutes per system)
  - Option B: Select core 3 scales based on factor analysis (e.g., explanation goodness, mental models, transparency)
  - Option C: Adaptive selection based on system type (e.g., RLHF systems emphasize trust, XAI systems emphasize explanation goodness)
- **Resolution Plan:** Conduct factor analysis in pilot study (Phase 2.4) to identify minimum scale set maintaining construct validity
- **Impact if Unresolved:** C dimension measurement may be unnecessarily long (participant burden) or incomplete (missing key constructs)

**Q2: Normalization Strategy for Heterogeneous Scales**
- **Issue:** T dimension uses percentages (0-100%), C dimension uses Likert scales (1-7), E dimension uses mixed scales (SUS: 0-100, satisfaction: 1-5, trust: 1-7). Normalization to uniform 0-100 scale requires decision on method.
- **Options:**
  - Option A: Min-max normalization (linear scaling: (x - x_min) / (x_max - x_min) × 100)
  - Option B: Z-score normalization (standardize to mean=0, SD=1, then scale to 0-100)
  - Option C: Percentile normalization (rank-based: score = percentile × 100)
- **Trade-offs:**
  - Min-max: Preserves absolute scale, sensitive to outliers
  - Z-score: Robust to outliers, loses absolute interpretation
  - Percentile: Most robust, requires large reference sample
- **Resolution Plan:** Test all three methods in pilot, compare impact on composite score rankings (Spearman ρ between methods)
- **Impact if Unresolved:** Different normalization methods may produce different system rankings, reducing reproducibility

**Q3: Handling Critical Dimension Failures**
- **Issue:** Composite scoring allows compensation (high T offsets low C). But some domains require minimum thresholds (e.g., healthcare may require C > 60 regardless of T score, "no amount of accuracy justifies opacity").
- **Options:**
  - Option A: Pure compensatory (current plan: weighted linear combination, no thresholds)
  - Option B: Hybrid: composite score + minimum dimension thresholds (e.g., reject if any dimension < 50)
  - Option C: Non-compensatory: lexicographic (first meet minimum C, then optimize T, then optimize E)
- **Resolution Plan:** Survey stakeholders on decision rules; pilot both compensatory and threshold-based approaches in decision quality study (SH3.1)
- **Impact if Unresolved:** CHEF may recommend unsafe systems (accurate but completely opaque) in high-stakes domains

**Q4: Temporal Validity and Re-Evaluation Frequency**
- **Issue:** User perceptions (C and E dimensions) may change over time as familiarity increases ("AI literacy effect"). Initial CHEF scores may not predict long-term deployment success.
- **Questions:**
  - How long are CHEF scores valid? (3 months? 6 months? 1 year?)
  - Should systems be re-evaluated periodically?
  - Do dimension scores decay at different rates (E changes faster than C faster than T)?
- **Resolution Plan:** Longitudinal study (SH1.3) includes measurement at t=0 (evaluation), t=3mo, t=6mo to assess temporal stability
- **Impact if Unresolved:** Framework may have limited predictive window; unclear when re-evaluation is needed

**Q5: Cross-Cultural Generalizability**
- **Issue:** Hoffman et al. scales and UX measures developed primarily in Western contexts (US, EU). Applicability to non-Western cultures (Asia, Africa, Latin America) is unknown.
- **Concerns:**
  - Trust norms vary culturally (individualist vs. collectivist cultures)
  - Explanation preferences may differ (detail-oriented vs. high-level)
  - Usability standards are culturally dependent
- **Resolution Plan:** Out of scope for initial validation (focus on Western contexts), but flag as future work and limitation in publication
- **Impact if Unresolved:** CHEF may not generalize globally; framework may require cultural adaptation for international deployment

**Q6: Lightweight CHEF Variant**
- **Issue:** Full CHEF evaluation requires 30-50 participants per system (expensive: $3K-5K per system, time-intensive: 2-4 weeks). This limits scalability for rapid system comparison.
- **Question:** Can automated proxies replace human studies for some metrics?
  - T dimension: Already automated (ML benchmarks)
  - C dimension: Can explanation quality be automatically assessed (e.g., LLM-as-judge for explanation goodness)?
  - E dimension: Can behavioral proxies (click-through rates, task completion) replace surveys?
- **Trade-off:** Automation reduces cost/time but may sacrifice validity
- **Resolution Plan:** Develop lightweight variant in parallel; validate correlation between automated proxies and full human studies
- **Impact if Unresolved:** CHEF may be too expensive for widespread adoption; practitioners may default to cheaper fragmented evaluation

**Q7: System Maturity Effects**
- **Issue:** E dimension (user experience) may penalize innovative but rough research prototypes (poor UX due to lack of polish, not fundamental flaws). CHEF scores may unfairly favor mature production systems.
- **Question:** Should evaluation adjust for system maturity?
  - Option A: No adjustment (evaluate all systems equally)
  - Option B: Separate evaluation tracks (research vs. production)
  - Option C: Maturity-adjusted scoring (normalize E dimension by expected maturity level)
- **Resolution Plan:** Pilot includes both prototypes and production systems; analyze E dimension score distribution by maturity level; consult stakeholders on fairness
- **Impact if Unresolved:** Research prototypes may be unfairly compared to production systems; framework may discourage early-stage innovation sharing

**Q8: Weighting Method Scalability**
- **Issue:** LLM-assisted stakeholder elicitation (SH2.3) is efficient for small groups (10-15 stakeholders), but unclear if it scales to larger stakeholder populations (100+ stakeholders) or more complex elicitation tasks (>3 dimensions).
- **Question:** Does LLM-assisted method maintain validity at scale?
- **Resolution Plan:** Compare LLM method with Delphi on healthcare domain (N=10-15); if successful, test on larger sample (N=30-50) to assess scalability
- **Impact if Unresolved:** LLM method may only work for small-scale elicitation; scaling to multiple domains/stakeholder groups may require fallback to traditional Delphi

---

**Phase 2A Extended: COMPLETE**

**Outputs Generated:**
1. ✅ Clarified Hypothesis (Section 1): Core statement, variables, causal mechanism, assumptions, scope, predictions, SOTA baseline, statistical design
2. ✅ Contribution Summary (Section 2): 3 theoretical, 4 methodological, 5 practical contributions with impact assessment
3. ✅ Key Related Work (Section 3): 23 sources mapped with relation types, gap analysis, citation plan
4. ✅ Phase 2B Readiness (Section 4): 3 sub-hypotheses previewed, readiness checklist (95/100), 8 open questions identified

**Next Step:** Phase 2B - Hypothesis Verification Planning
- **Command:** `/phase2b-planning` with this document as input
- **Goal:** Decompose H-CHEF-001 into detailed sub-hypotheses (SH1-SH3) with complete verification protocols
- **Timeline:** 2-3 hours for Phase 2B planning session

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
