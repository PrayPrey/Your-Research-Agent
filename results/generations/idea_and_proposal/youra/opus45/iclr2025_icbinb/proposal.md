# Research Proposal: ML-HFACS: Adapting Aviation's Human Factors Taxonomy for Systematic Classification of Deep Learning Deployment Failures

## 1. Introduction

### 1.1 Background

Deep learning (DL) has achieved remarkable success on benchmark tasks across computer vision, natural language processing, and scientific discovery. However, the translation of these benchmark achievements to real-world deployment remains fraught with challenges. A growing body of evidence suggests that DL systems frequently fail in unexpected ways when deployed in dynamic, real-world conditions—failures that are often poorly documented, inadequately understood, and rarely shared across domains.

The current publication ecosystem exacerbates this problem. Academic incentives favor reporting positive results on standardized benchmarks, while negative results and deployment failures remain largely unpublished. Recent analyses reveal that 79% of machine learning papers use weak baselines, suggesting systematic issues in how the field evaluates and reports model performance. More critically, when failures do occur in production systems—whether in healthcare diagnostics, autonomous vehicles, or recommendation systems—discussions remain siloed within specific domains, preventing the identification of common failure patterns that could inform safer deployment practices across the field.

This fragmentation stands in stark contrast to mature engineering disciplines. Aviation, in particular, offers a compelling model for systematic failure analysis. Following decades of accident investigation, the aviation industry developed the Human Factors Analysis and Classification System (HFACS)—a hierarchical taxonomy that enables systematic classification of accident causes across four levels: organizational influences, unsafe supervision, preconditions for unsafe acts, and unsafe acts themselves. HFACS has proven remarkably transferable, successfully adapting to healthcare, maritime, nuclear, and mining domains, suggesting that hierarchical failure classification may be domain-invariant for complex sociotechnical systems.

### 1.2 Research Objectives

This research proposes to develop and validate ML-HFACS: a systematic taxonomy for classifying deep learning deployment failures adapted from aviation's HFACS framework. Our specific objectives are:

1. **Taxonomy Development:** Adapt the 4-level HFACS hierarchy to create ML-HFACS with 24 categories specifically designed for ML deployment failures, mapping aviation concepts to ML-specific failure modes.

2. **Validation Study:** Empirically validate ML-HFACS through an inter-rater reliability study, demonstrating that trained practitioners can consistently classify ML failures using the taxonomy (target: Cohen's κ > 0.7).

3. **Failure Pattern Analysis:** Apply the validated taxonomy to 100 documented ML failures to identify common patterns, particularly examining the role of organizational and supervisory factors in deployment failures.

4. **Community Resource Creation:** Establish a shareable, validated framework that enables cross-domain failure pattern identification and supports the broader ICBINB initiative's goal of learning from negative results.

### 1.3 Significance

This research addresses a critical gap in the ML research ecosystem. By providing a validated, systematic framework for failure classification, ML-HFACS will enable:

- **Cross-domain learning:** Practitioners in healthcare AI can learn from autonomous vehicle failures, and vice versa, when failures share common underlying causes.
- **Predictive insights:** Understanding that organizational factors (Level 1-2) frequently contribute to deployment failures can inform proactive risk mitigation.
- **Cultural change:** A shared vocabulary for discussing failures supports the transparency and learning culture that the ICBINB initiative promotes.
- **Safer deployment:** Systematic failure documentation enables the ML community to move beyond anecdotal lessons toward evidence-based deployment practices.

## 2. Methodology

### 2.1 Research Design Overview

This research follows a three-phase design: (1) taxonomy development through systematic adaptation of HFACS, (2) validation through inter-rater reliability assessment, and (3) application to a corpus of 100 ML deployment failures. The study employs mixed methods, combining qualitative taxonomy development with quantitative reliability assessment.

### 2.2 Phase 1: ML-HFACS Taxonomy Development

#### 2.2.1 HFACS Adaptation Framework

The original HFACS framework comprises four hierarchical levels:

$$\text{HFACS} = \{L_1: \text{Organizational}, L_2: \text{Supervisory}, L_3: \text{Preconditions}, L_4: \text{Unsafe Acts}\}$$

We adapt each level to ML deployment contexts:

**Level 1 - Organizational Influences (6 categories):**
- Resource Management: Compute budget allocation, data infrastructure investment
- Organizational Climate: Publication pressure, benchmark-focused culture
- Organizational Process: MLOps maturity, deployment protocols, monitoring practices

**Level 2 - Unsafe Supervision (6 categories):**
- Inadequate Supervision: Insufficient model monitoring, lack of domain expert oversight
- Planned Inappropriate Operations: Deploying models beyond validated domains
- Failed to Correct Problems: Ignoring drift alerts, dismissing edge case reports
- Supervisory Violations: Bypassing validation protocols for speed-to-deployment

**Level 3 - Preconditions for Unsafe Acts (6 categories):**
- Data Quality Issues: Distribution shift, label noise, sampling bias
- Model Limitations: Assumption violations, representation misalignment, scalability constraints
- Environmental Factors: Hardware constraints, integration complexity, regulatory requirements
- Team Factors: Communication gaps between ML engineers and domain experts

**Level 4 - Unsafe Acts (6 categories):**
- Errors: Decision errors (wrong model selection), skill-based errors (implementation bugs), perceptual errors (misinterpreting metrics)
- Violations: Routine violations (skipping validation), exceptional violations (deploying untested models)

#### 2.2.2 Category Refinement Process

Categories will be refined through:
1. Literature review of 50 documented ML failures to identify recurring themes
2. Expert consultation with 5 ML practitioners from diverse domains
3. Iterative refinement based on pilot classification of 10 failures

### 2.3 Phase 2: Validation Study

#### 2.3.1 Data Collection

**Sample Composition:**
- Total failures: $n = 100$
- Industry sources: $n_{ind} = 50$ (anonymized reports from partner companies)
- Public sources: $n_{pub} = 50$ (ICBINB papers, technical blogs, post-mortems)

**Inclusion Criteria:**
- Documented ML/DL deployment failure
- Minimum 500-word structured description
- English language
- Sufficient detail to identify causal factors

**De-identification Protocol:**
For industry sources, we apply differential privacy with privacy budget $\epsilon = 1.0$ combined with $k$-anonymity where $k = 5$:

$$\Pr[\mathcal{M}(D) \in S] \leq e^{\epsilon} \cdot \Pr[\mathcal{M}(D') \in S]$$

where $\mathcal{M}$ is the anonymization mechanism, $D$ and $D'$ are neighboring datasets, and $S$ is any subset of outputs.

#### 2.3.2 Rater Training Protocol

**Participants:** 3 independent ML practitioners with ≥3 years deployment experience

**Training Protocol (4 hours):**
1. Hour 1: HFACS principles and ML-HFACS category definitions
2. Hour 2: Worked examples with 5 pre-classified failures
3. Hour 3: Practice classification of 5 failures with feedback
4. Hour 4: Calibration discussion and protocol clarification

**Classification Procedure:**
Each rater independently classifies a subset of 30 failures, assigning:
- Primary level (L1-L4)
- Primary category within level
- Secondary contributing factors (if applicable)
- Confidence rating (1-5 scale)

#### 2.3.3 Inter-Rater Reliability Assessment

**Primary Metric:** Cohen's kappa for pairwise agreement:

$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

where $p_o$ is observed agreement and $p_e$ is expected agreement by chance.

**Multi-Rater Extension:** Fleiss' kappa for 3 raters:

$$\kappa_F = \frac{\bar{P} - \bar{P_e}}{1 - \bar{P_e}}$$

where $\bar{P}$ is mean observed agreement and $\bar{P_e}$ is mean expected agreement.

**Success Criteria:**
- Primary success: $\kappa > 0.7$ (substantial agreement)
- Acceptable: $\kappa > 0.6$ (moderate-substantial agreement)
- Falsification threshold: $\kappa \leq 0.4$ (fair or worse agreement)

**Statistical Power:**
Sample size $n = 30$ failures provides 80% power to detect $\kappa = 0.7$ against null hypothesis $\kappa_0 = 0.4$ at $\alpha = 0.05$.

### 2.4 Phase 3: Failure Pattern Analysis

#### 2.4.1 Full Corpus Classification

Following validation, the complete corpus of 100 failures will be classified using consensus coding:
1. Two raters independently classify each failure
2. Disagreements resolved through discussion
3. Third rater adjudicates persistent disagreements

#### 2.4.2 Pattern Analysis

**Coverage Analysis:**
Calculate taxonomy coverage as:

$$\text{Coverage} = \frac{n_{classified}}{n_{total}} \times 100\%$$

Target: >95% classifiable (≤5% requiring "Other" category)

**Level Distribution Analysis:**
For each failure $f_i$, identify all contributing levels $L(f_i) \subseteq \{L_1, L_2, L_3, L_4\}$

**Predictive Association Test:**
Test hypothesis that deployment failures disproportionately involve organizational/supervisory factors:

$$H_1: P(L_1 \cup L_2 | \text{deployment failure}) > 0.7$$

Using binomial test with $\alpha = 0.05$.

**Cross-Domain Pattern Identification:**
Apply hierarchical clustering to failure profiles:

$$d(f_i, f_j) = 1 - \frac{|L(f_i) \cap L(f_j)|}{|L(f_i) \cup L(f_j)|}$$

to identify failure clusters that span multiple application domains.

### 2.5 Evaluation Metrics Summary

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Inter-rater reliability (κ) | > 0.7 | Cohen's κ pairwise, Fleiss' κ multi-rater |
| Taxonomy coverage | > 95% | Proportion classifiable |
| Source invariance | $\kappa_{ind} \approx \kappa_{pub}$ | Independent samples t-test |
| Level 1-2 association | > 70% | Binomial test |
| De-identification success | 0% identification | Security review |

### 2.6 Timeline and Resources

**Timeline:** 12 months total
- Months 1-3: Taxonomy development and refinement
- Months 4-6: Data collection and de-identification
- Months 7-9: Rater training and reliability study
- Months 10-12: Full corpus analysis and dissemination

**Resources Required:**
- 3 trained raters (40 hours each)
- Industry partnerships (5-10 companies)
- IRB approval for human subjects (rater study)

## 3. Expected Outcomes & Impact

### 3.1 Primary Outcomes

**Validated Taxonomy:** ML-HFACS will provide the first empirically validated framework for classifying ML deployment failures. With target inter-rater reliability κ > 0.7, the taxonomy will meet standards for substantial agreement, enabling consistent failure classification across practitioners and organizations.

**Failure Pattern Database:** The classified corpus of 100 failures will constitute a foundational resource for the ML community, enabling:
- Identification of common failure patterns across domains
- Quantification of organizational vs. technical failure contributions
- Evidence-based recommendations for deployment risk mitigation

**Predictive Insights:** We hypothesize that >70% of deployment failures will involve Level 1-2 (organizational/supervisory) factors, challenging the common assumption that ML failures are primarily technical. This finding would have significant implications for how organizations approach ML deployment.

### 3.2 Broader Impact

**Cross-Domain Learning:** By providing a shared vocabulary for failure discussion, ML-HFACS enables practitioners in healthcare, robotics, finance, and other domains to learn from each other's failures. A recommendation system failure caused by distribution shift shares underlying causes with a medical imaging failure from the same root cause—ML-HFACS makes these connections visible.

**Cultural Transformation:** This research directly supports the ICBINB initiative's mission of promoting transparency about negative results. A validated taxonomy legitimizes failure documentation as a scholarly contribution, potentially shifting incentives toward more honest reporting of deployment challenges.

**Safer AI Deployment:** As ML systems increasingly affect human welfare—in healthcare decisions, autonomous vehicles, and criminal justice—systematic failure analysis becomes a safety imperative. ML-HFACS provides the foundation for evidence-based safety practices analogous to those that transformed aviation from a dangerous endeavor to one of the safest forms of transportation.

### 3.3 Limitations and Future Directions

**Limitations:**
- Sample of 100 failures may not capture full diversity of failure modes
- Industry selection bias toward companies willing to share failures
- Temporal snapshot; failure patterns may evolve with technology
- Correlation, not causation, for Level 1-2 associations

**Future Directions:**
- Expand taxonomy through community contribution
- Develop automated failure classification using NLP
- Create predictive models for deployment risk assessment
- Establish ongoing failure reporting infrastructure

### 3.4 Contribution to ICBINB Goals

This research embodies the ICBINB philosophy that "there is more to machine learning research than tables with bold numbers." By systematically documenting and classifying failures, we create value from negative results that would otherwise remain hidden. The validated taxonomy provides a concrete tool for the community to continue this work, transforming isolated failures into collective learning opportunities.

The ultimate vision is an ML community that treats failure documentation with the same rigor as benchmark improvements—where sharing a well-analyzed failure is as valued as reporting a state-of-the-art result. ML-HFACS provides the methodological foundation for this cultural transformation.