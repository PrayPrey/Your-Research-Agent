# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ML-FMEA-Agriculture-001
**Confidence Level:** 0.85 (HIGH)

**Main Hypothesis:**
In agricultural ML systems, a structured Failure Mode Taxonomy inspired by FMEA can enable predictive risk assessment such that mapping algorithmic properties (architecture family, training data coverage, optimization methods) to failure mode susceptibility via ML-RPN scoring allows pre-deployment identification of high-risk algorithm-context pairs with ROC-AUC > 0.7.

**Alternative Hypothesis (H0):**
Agricultural ML failures are purely context-dependent and idiosyncratic, with no systematic patterns linking algorithmic properties to failure mode susceptibility (ROC-AUC ≤ 0.5 for property-failure correlations).

### 1.2 Variables

| Variable | Type | Operationalization | Measurement Method |
|----------|------|-------------------|-------------------|
| **algorithmic_properties** | Independent | Architecture family (CNN/RNN/Transformer), training data spatial coverage (% geographic regions), training data temporal coverage (months), optimization method (SGD/Adam/etc.), pre-training source | Feature extraction from paper methodology sections |
| **failure_mode_occurrence** | Dependent (Binary) | Binary classification: Did failure mode occur? (Temporal Drift / Spatial Transfer / Data Quality / Multi-Objective / Calibration) | Literature review coding: 1 if failure documented, 0 otherwise |
| **ML-RPN_score** | Dependent (Continuous) | ML-RPN = Severity × Occurrence × Detection (range: 1-1000) | Expert panel scoring using domain-specific rubrics |
| **validation_indicators** | Mediating | OOD performance degradation rate (%), calibration error on shifted data (ECE), Pareto front collapse indicator (binary) | Extracted from paper validation sections |
| **agricultural_context** | Controlled | Crop type (grains/vegetables/fruits), geographic region (temperate/tropical/arid), temporal horizon (seasonal/annual/multi-year), sensor modality (satellite/drone/ground sensors) | Contextual coding from deployment descriptions |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

1. **Algorithmic Property Selection** → **Failure Mode Susceptibility**
   - *Mechanism*: Architecture families have intrinsic biases (e.g., CNNs lack temporal adaptation, RNNs struggle with long-range spatial dependencies). Training data coverage creates vulnerability to out-of-distribution conditions.
   - *Evidence*: Mission Critical (Rolf+ 2024, 75 cit) demonstrates satellite data as distinct modality with specific failure modes when treated with standard CV methods.

2. **Failure Mode Susceptibility** → **Validation-Stage Indicators**
   - *Mechanism*: High-susceptibility algorithms exhibit early warning signals during validation: accelerated OOD performance degradation, elevated calibration errors, Pareto front instability in multi-objective settings.
   - *Evidence*: Suitability Filter (Pouget+ 2025) empirically validates that covariate shift detection during validation predicts deployment performance degradation.

3. **Validation-Stage Indicators** → **ML-RPN Components**
   - *Mechanism*: Validation indicators map to ML-RPN dimensions: OOD degradation rate predicts Detection score (higher degradation = later detection), calibration error predicts Occurrence likelihood, Pareto collapse predicts Severity (multi-objective failures have high SDG impact).
   - *Evidence*: FMEA framework (60+ years reliability engineering) provides systematic mapping from observable indicators to risk scores.

4. **ML-RPN Components** → **Deployment Failure Prediction**
   - *Mechanism*: ML-RPN aggregates risk dimensions (S × O × D) to produce quantitative deployment failure probability. High ML-RPN (>700/1000) indicates algorithm-context mismatch requiring intervention before deployment.
   - *Evidence*: WILDS benchmark (Koh+ Stanford 2021) documents real-world distribution shift degradation that retrospective ML-RPN analysis would have flagged (geographic transfer failures in FMoW, hospital transfer failures in Camelyon).

**Evidence for Causal Links:**
- **Link 1**: Mission Critical paper demonstrates architecture-specific failure patterns in satellite data (distinct modality requires tailored approaches)
- **Link 2**: Suitability Filter validates validation→deployment correlation for covariate shift
- **Link 3**: FMEA literature shows systematic risk assessment via observable indicators in aerospace/automotive domains
- **Link 4**: WILDS and OODRobustBench document post-hoc failure cases that fit predicted patterns

**Key Tension:**
FMEA assumes deterministic cause-effect relationships (material fatigue → component failure), but ML failures are PROBABILISTIC and context-dependent (same CNN architecture may succeed in one region, fail in another). This tension requires ML-RPN to be conditioned on deployment context: ML-RPN(algorithm, agricultural_context) rather than universal algorithm scores.

### 1.4 Key Assumptions

1. **Systematic Failure Patterns Exist**
   - Assumption: Agricultural ML failures exhibit classifiable patterns by mechanism (not purely random)
   - Validation Strategy: Taxonomy construction from 20-30 literature cases; measure inter-rater agreement (target Cohen's κ > 0.7)

2. **Property-Susceptibility Correlations Are Measurable**
   - Assumption: Algorithmic properties have statistically significant correlation with failure modes
   - Validation Strategy: Logistic regression analysis; target ROC-AUC > 0.7 for predictive power

3. **Literature Provides Sufficient Data**
   - Assumption: 20-30 agriculture ML papers with documented failures provide adequate initial taxonomy
   - Validation Strategy: Saturation analysis (do new papers introduce new failure categories after N papers?)

4. **Validation Indicators Predict Deployment Outcomes**
   - Assumption: Validation-stage metrics (OOD performance, calibration) correlate with real-world deployment failures
   - Validation Strategy: Retrospective analysis of papers reporting BOTH validation metrics AND deployment outcomes; measure Pearson correlation

5. **Expert Scoring Achieves Reliability**
   - Assumption: Expert panel can achieve reliable ML-RPN scoring with domain-specific rubrics
   - Validation Strategy: Independent scoring by 3-5 agriculture ML experts; measure inter-rater reliability (target Cohen's κ > 0.7)

### 1.5 Scope & Boundaries

**Applies To:**
- Agricultural ML systems (crop yield prediction, pest detection, irrigation optimization, climate-resilient agriculture)
- Failures documented in peer-reviewed academic literature
- Supervised learning and reinforcement learning approaches
- Deployment contexts with explicit geographic, temporal, and crop-type specifications

**Does NOT Apply To:**
- Other sustainability domains (climate forecasting, biodiversity monitoring, energy systems) without pilot validation
- Proprietary industry ML systems without published failure documentation
- Purely theoretical models without deployment attempts
- Generic robustness benchmarks (CIFAR-C, ImageNet-C) lacking sustainability context

**Known Limitations:**
1. **Literature Bias**: Taxonomy reflects published failures only; may miss unreported industry deployments
2. **Expert Subjectivity**: ML-RPN Severity scoring requires expert judgment despite rubrics (agriculture impact assessment)
3. **Context-Dependency**: ML-RPN scores are context-conditioned; generalization across regions/crops requires empirical validation
4. **Temporal Scope**: Initial taxonomy limited to literature up to 2026; requires periodic updates as new failure modes emerge
5. **Domain Specificity**: Agriculture pilot results do not automatically generalize to climate/biodiversity without validation

### 1.6 Testable Predictions

**Primary Prediction:**
If algorithmic properties (architecture, data coverage) are mapped to failure modes via logistic regression on 20-30 agriculture ML literature cases, then the property-failure classification model will achieve ROC-AUC > 0.7, demonstrating systematic predictive relationships.

**Secondary Predictions:**
1. **Property-Specific Failure Rates:**
   - CNNs without temporal adaptation will exhibit temporal drift failures 2-3× more frequently than RNNs/Transformers with time-aware architectures (χ² test, p < 0.05)
   - Training datasets with <3 geographic regions will exhibit spatial transfer failures 2× more frequently than datasets covering 5+ regions (χ² test, p < 0.05)

2. **Validation Indicator Correlation:**
   - OOD performance degradation rate (measured in validation) will correlate with deployment failure severity with Pearson r > 0.5 (p < 0.01)
   - Calibration error (ECE) will correlate with failure occurrence likelihood with Pearson r > 0.4 (p < 0.05)

3. **ML-RPN Predictive Power:**
   - Algorithm-context pairs with ML-RPN > 700/1000 will have deployment failure rates >60%
   - Algorithm-context pairs with ML-RPN < 300/1000 will have deployment failure rates <20%
   - ROC-AUC for ML-RPN predicting binary deployment outcome (success/failure) > 0.7

**Falsification Criteria:**
- **Primary Falsification**: If property-failure logistic regression achieves ROC-AUC ≤ 0.5 (no better than random), hypothesis is false
- **Secondary Falsification 1**: If validation indicators show NO correlation with deployment outcomes (|Pearson r| < 0.2, p > 0.10), predictive mechanism fails
- **Secondary Falsification 2**: If ML-RPN scores show NO discrimination between successful/failed deployments (ROC-AUC < 0.55), risk assessment framework is invalid
- **Assumption Falsification**: If inter-rater reliability for ML-RPN scoring κ < 0.5, expert judgment too subjective for practical use

### 1.7 SOTA Baseline

**N/A** - This hypothesis does not target SOTA performance improvement. It addresses a GAP (systematic failure mode documentation) rather than incremental performance gains. Comparison baselines are REACTIVE tools (WILDS, OODRobustBench) that document failures post-hoc, whereas ML-FMEA provides PROACTIVE pre-deployment risk assessment.

### 1.8 Statistical Verification Design

**Study Design:** Retrospective literature-based cross-sectional analysis with expert panel validation

**Sample:**
- **Training Set**: 15-20 agriculture ML papers with documented failures (temporal: 2018-2026)
- **Test Set**: 5-10 held-out papers for out-of-sample validation
- **Geographic Coverage**: Global (emphasis on temperate/tropical agriculture)
- **Crop Coverage**: Grains (wheat, rice, corn), vegetables, fruits

**Statistical Tests:**

1. **Property-Failure Association:**
   - **Method**: Logistic regression (binary outcome: failure mode occurred yes/no)
   - **Features**: Architecture family (categorical), training data coverage (continuous), optimization method (categorical)
   - **Metric**: ROC-AUC > 0.7 (success threshold)
   - **Validation**: 5-fold cross-validation on training set, final test on held-out set

2. **Validation-Deployment Correlation:**
   - **Method**: Pearson correlation between validation indicators and deployment failure severity
   - **Variables**: OOD degradation rate (%), calibration error (ECE), deployment failure severity (1-10 scale)
   - **Threshold**: |r| > 0.4, p < 0.05 (statistically significant correlation)

3. **ML-RPN Discrimination:**
   - **Method**: ROC curve analysis for binary classification (deployment success/failure)
   - **Predictor**: ML-RPN score (continuous, range 1-1000)
   - **Threshold**: ROC-AUC > 0.7
   - **Calibration**: Hosmer-Lemeshow goodness-of-fit test (p > 0.05 for good calibration)

4. **Inter-Rater Reliability:**
   - **Method**: Cohen's kappa for pairwise agreement, Fleiss's kappa for multi-rater
   - **Raters**: 3-5 agriculture ML domain experts
   - **Scoring**: ML-RPN components (Severity 1-10, Occurrence 1-10, Detection 1-10)
   - **Threshold**: κ > 0.7 (substantial agreement)

**Power Analysis:**
- **Effect Size**: Medium (Cohen's d = 0.5 for property-failure difference)
- **Alpha**: 0.05 (two-tailed)
- **Power**: 0.80
- **Required N**: 20-25 failure cases per category (achievable with 20-30 papers if papers document multiple failure modes)

**Confounding Control:**
- **Geographic confounding**: Stratify by region (temperate vs. tropical)
- **Temporal confounding**: Control for publication year (account for methodology evolution 2018-2026)
- **Crop-type confounding**: Include crop type as covariate in regression models
- **Sensor modality confounding**: Include sensor type (satellite/drone/ground) as covariate

---

## 2. Contribution Summary

**Theoretical:**
- First FMEA adaptation to ML robustness (paradigm shift from reactive to proactive risk assessment)
- Mechanistic failure classification by WHY (temporal drift, spatial transfer) vs. SYMPTOM (accuracy drop)
- Property-susceptibility predictive framework linking design choices to deployment outcomes

**Methodological:**
- ML-RPN metric (Severity × Occurrence × Detection) for quantitative pre-deployment risk prioritization
- Structured 5-category Failure Mode Taxonomy with inter-rater reliability validation
- Property-susceptibility statistical mapping via logistic regression (ROC-AUC > 0.7 target)
- Early warning indicator framework (OOD degradation, calibration error, Pareto collapse)

**Practical:**
- Pre-deployment risk assessment tool preventing wasted resources ($50K-$500K per agricultural trial)
- Negative results documentation infrastructure addressing workshop CFP requirements
- Algorithm selection decision support for specific deployment contexts
- SDG impact quantification framework linking ML failures to sustainability outcomes

---

## 3. Key Related Work

**Foundational (Cross-Domain):**
1. **FMEA (Reliability Engineering)** - Systematic failure enumeration + RPN framework (60+ years)
2. **Software/Cybersecurity FMEA** - Precedent for probabilistic domains

**Evidence (Phase 1 + Supplementary):**
3. **Mission Critical (Rolf+ 2024, 75 cit)** - SS ID: 0385c1fa107ce68db9f988547bf2d7b708a0c748 - Validates domain-specific failure modes
4. **WILDS (Koh+ 2021)** - Provides failure case dataset for taxonomy construction
5. **Suitability Filter (Pouget+ 2025)** - **CRITICAL**: Validates validation→deployment correlation
6. **ML4CFD (Yagoubi+ 2024)** - SS ID: f5ef710b90030de4a5a26f69d965e156c7e9ce2a - Shows community demand for OOD evaluation

**Tools:**
7. **OODRobustBench** - github.com/oodrobustbench/oodrobustbench - Evaluation protocol for Detection dimension
8. **RobustMLDS'24 Workshop** - Validates Gap 1 existence (negative results documentation needed)

**Theory:**
9. **Minimax Regret Optimization (Agarwal & Zhang 2022, 36 cit)** - SS ID: 4fe3f3e113334998114211f2bb9ff1659100fc14 - Explains why reactive approaches insufficient

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
Construct taxonomy from 15 training papers, apply to 5 test papers. Success: ≥90% classifiable within 5 categories, inter-rater κ > 0.7. Timeline: 2-3 months.

**SH2 (Mechanism):**
Logistic regression predicting failure modes from algorithmic properties. Success: ROC-AUC > 0.7 on test set. Sub-tests: (a) CNNs 2-3× temporal drift, (b) <3 regions 2× spatial transfer, (c) OOD-severity Pearson r > 0.5. Timeline: 1 month.

**SH3 (Comparison):**
Expert panel ML-RPN scoring. Success: ROC-AUC > 0.7 for deployment prediction, κ > 0.7 inter-rater reliability. Comparison: ML-RPN vs. OOD-only vs. calibration-only baselines. Timeline: 1-2 months.

### Readiness Checklist

- [x] Hypothesis clarity (condition, intervention, outcome, mechanism specified)
- [x] Variables operationalized with measurement methods
- [x] Causal mechanism decomposed into 4 testable links
- [x] Assumptions explicit with validation strategies
- [x] Scope and boundaries defined
- [x] Primary prediction quantitative (ROC-AUC > 0.7)
- [x] Secondary predictions with effect sizes
- [x] Statistical tests specified (logistic regression, Pearson r, ROC analysis)
- [x] Falsification criteria explicit
- [x] Feasibility confirmed (MEDIUM difficulty, 4-6 months, standard resources)
- [x] Evidence gathered (Mission Critical, WILDS, Suitability Filter)
- [x] Confounding controlled (geographic, temporal, crop-type, sensor)
- [x] Contributions articulated (theoretical, methodological, practical)
- [x] Phase 2B decomposition ready (SH1-3 testable independently)

### Open Questions

1. **Literature Saturation**: Will 20-30 papers suffice? Mitigation: Saturation analysis; expand to 40-50 if needed.
2. **Expert Panel Recruitment**: Can recruit 3-5 agriculture ML experts? Mitigation: Leverage workshop networks, offer co-authorship.
3. **Context Generalization**: Do correlations hold across temperate vs. tropical? Mitigation: Stratified analysis by region.
4. **Temporal Evolution**: Are failure patterns stable 2018-2026? Mitigation: Include publication year covariate.
5. **Industry Deployment Data**: Do academic failures represent industry? Mitigation: Acknowledge limitation, recommend Phase 3 industry validation.

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
