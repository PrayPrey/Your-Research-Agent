# Research Proposal: IRT-HAIC: Adaptive Evaluation of AI-HCI Systems Using Multidimensional Item Response Theory

## 1. Introduction

### 1.1 Background

The convergence of Artificial Intelligence (AI) and Human-Computer Interaction (HCI) has produced a new generation of interactive systems—including reinforcement learning from human feedback (RLHF) chatbots, human-in-the-loop design tools, and fairness-aware recommender systems—that fundamentally reshape how humans and machines collaborate. As these systems proliferate across domains from healthcare to creative industries, the need for rigorous, scalable, and equitable evaluation methodologies has become paramount. However, current evaluation practices face three critical limitations that impede progress in the field.

First, existing evaluation methods rely predominantly on lengthy fixed-form assessments that impose substantial burden on users. A typical comprehensive evaluation may require 30-50 items to assess multiple quality dimensions, leading to respondent fatigue, reduced data quality, and practical barriers to deployment at scale. Second, evaluation instruments lack standardization across diverse user populations, making cross-system and cross-demographic comparisons unreliable. Third, and perhaps most critically, current approaches cannot efficiently measure the multidimensional constructs essential to AI-HCI system quality—including interaction alignment (how well the system responds to user intent), trust calibration (the correspondence between user trust and actual system performance), and socio-relational fairness (equitable treatment across demographic groups)—while simultaneously ensuring measurement fairness.

These limitations create significant barriers to the advancement of AI-HCI research and practice. Without efficient, standardized, and fair evaluation methods, researchers cannot reliably compare systems, practitioners cannot make informed deployment decisions, and the field cannot establish the empirical foundations necessary for theoretical progress.

### 1.2 Research Objectives

This research proposes IRT-HAIC (Item Response Theory for Human-AI Collaboration), a novel evaluation framework that addresses these limitations by modeling AI-HCI system quality as latent traits using Multidimensional Item Response Theory (MIRT) and enabling Computer Adaptive Testing (CAT) for efficient, invariant measurement. Our specific objectives are:

1. **Develop and validate a multidimensional latent trait model** for AI-HCI system quality encompassing three core dimensions: interaction alignment, trust calibration accuracy, and socio-relational fairness.

2. **Construct and calibrate a 100-item evaluation bank** using a stratified sample of n=1,000 users across 3-5 AI-HCI system types, establishing item parameters (difficulty, discrimination, guessing) that enable adaptive testing.

3. **Implement and validate a CAT algorithm** that achieves equivalent measurement precision (SE < 0.3) with at least 40% fewer items compared to fixed-form evaluation.

4. **Demonstrate measurement invariance** across major demographic groups (ΔCFI < 0.01), ensuring equitable evaluation regardless of user characteristics.

### 1.3 Significance

This research makes four primary contributions to the intersection of AI and HCI. Theoretically, it establishes that AI-HCI interaction quality can be conceptualized and measured as stable latent traits, providing a psychometric foundation for the field. Methodologically, it introduces adaptive testing to AI-HCI evaluation, demonstrating that principled item selection can dramatically reduce assessment burden while maintaining precision. Practically, it delivers a validated evaluation framework that researchers and practitioners can deploy immediately. Finally, from an equity perspective, it ensures that evaluation instruments function equivalently across demographic groups, addressing fairness concerns that are increasingly central to responsible AI development.

## 2. Methodology

### 2.1 Theoretical Framework

The IRT-HAIC framework rests on the premise that observable responses to evaluation items are probabilistic functions of underlying latent traits. We adopt the Multidimensional Two-Parameter Logistic (M2PL) model, which specifies the probability of a positive response to item $i$ given a vector of latent traits $\boldsymbol{\theta}$ as:

$$P(X_i = 1 | \boldsymbol{\theta}) = \frac{1}{1 + \exp(-(\mathbf{a}_i^T \boldsymbol{\theta} + d_i))}$$

where $\mathbf{a}_i$ is the vector of discrimination parameters indicating how strongly item $i$ relates to each latent dimension, and $d_i$ is the intercept parameter related to item difficulty. For our three-dimensional model:

$$\boldsymbol{\theta} = (\theta_1, \theta_2, \theta_3)^T$$

representing interaction alignment, trust calibration accuracy, and socio-relational fairness, respectively.

The causal mechanism underlying IRT-HAIC operates through four sequential steps:

**Step 1: Latent Traits → Item Response Patterns.** Users' underlying AI-HCI interaction quality ($\boldsymbol{\theta}$) probabilistically determines their responses to evaluation items via the item characteristic function. Users with higher latent trait values have higher probabilities of endorsing items indicating quality.

**Step 2: Item Response Patterns → MIRT Parameter Estimation.** Observed response patterns across the calibration sample enable maximum likelihood estimation of item parameters and the latent trait covariance structure. We employ marginal maximum likelihood estimation with an EM algorithm.

**Step 3: MIRT Parameters → Adaptive Item Selection.** Calibrated item parameters enable the CAT algorithm to select maximally informative items. We use the Kullback-Leibler (KL) information criterion for multidimensional CAT:

$$KL_i(\hat{\boldsymbol{\theta}}) = \int P(X_i | \boldsymbol{\theta}) \log \frac{P(X_i | \boldsymbol{\theta})}{P(X_i | \hat{\boldsymbol{\theta}})} d\boldsymbol{\theta}$$

The item maximizing expected KL information is selected at each step.

**Step 4: Adaptive Selection → Efficient Measurement with Invariance.** Optimal item selection achieves equivalent precision with fewer items; Multi-Group MIRT validates that this efficiency holds across demographic groups.

### 2.2 Data Collection

**Participant Recruitment.** We will recruit n=1,000 participants through a combination of crowdsourcing platforms (Prolific, MTurk) and industry partnerships, using stratified sampling to ensure representation across:
- Age groups: 18-29, 30-44, 45-59, 60+
- Education levels: High school, Bachelor's, Graduate
- Technology experience: Low, Medium, High (self-reported)
- Gender: Male, Female, Non-binary
- Geographic region: North America, Europe, Asia-Pacific

Each stratum will contain minimum n=50 participants to enable measurement invariance testing.

**AI-HCI Systems Under Evaluation.** Participants will evaluate 3-5 AI-HCI system types:
1. RLHF-based conversational agents (e.g., customer service chatbots)
2. Human-in-the-loop design tools (e.g., AI-assisted graphic design)
3. Fairness-aware recommender systems (e.g., job recommendation platforms)
4. Explainable ML decision support systems (e.g., medical diagnosis aids)
5. Active learning annotation interfaces

Each participant will interact with one system type for 10 minutes before completing the evaluation.

**Item Bank Development.** The 100-item bank will be developed through:
1. Literature review to identify existing validated items
2. Expert panel (n=8 HCI and psychometrics experts) using modified Delphi method
3. Cognitive interviews (n=20) to assess item clarity
4. Pilot testing (n=100) for initial psychometric screening

Items will be distributed across dimensions: ~35 items for interaction alignment, ~35 for trust calibration, ~30 for socio-relational fairness, with some items loading on multiple dimensions.

### 2.3 Algorithmic Procedures

**Phase 1: Item Calibration**

1. Administer full 100-item bank to calibration sample (n=1,000)
2. Conduct exploratory factor analysis (EFA) on random half (n=500) to verify three-factor structure
3. Fit M2PL model using confirmatory approach on remaining half (n=500)
4. Estimate item parameters using marginal maximum likelihood:

$$L(\boldsymbol{\xi}) = \prod_{j=1}^{N} \int \prod_{i=1}^{I} P(x_{ij} | \boldsymbol{\theta})^{x_{ij}} [1 - P(x_{ij} | \boldsymbol{\theta})]^{1-x_{ij}} g(\boldsymbol{\theta}) d\boldsymbol{\theta}$$

where $\boldsymbol{\xi}$ represents all item parameters and $g(\boldsymbol{\theta})$ is the population distribution of latent traits.

5. Evaluate model fit using RMSEA (target < 0.08), CFI (target > 0.90), and SRMR (target < 0.08)
6. Test local independence using Q3 statistics; flag item pairs with residual correlations > 0.2

**Phase 2: CAT Algorithm Implementation**

The adaptive testing algorithm proceeds as follows:

```
Algorithm: IRT-HAIC Adaptive Evaluation
Input: Calibrated item bank B, stopping criteria (SE_threshold = 0.3, max_items = 30)
Output: Latent trait estimates θ̂, standard errors SE

1. Initialize: θ̂ = (0, 0, 0), administered_items = ∅
2. While SE(θ̂) > SE_threshold AND |administered_items| < max_items:
   a. For each item i ∈ B \ administered_items:
      - Compute expected KL information: KL_i(θ̂)
   b. Select item i* = argmax_i KL_i(θ̂)
   c. Administer item i*, observe response x_i*
   d. Update θ̂ using Expected A Posteriori (EAP) estimation:
      θ̂ = E[θ | x_1, ..., x_k] = ∫ θ L(θ | x) π(θ) dθ / ∫ L(θ | x) π(θ) dθ
   e. Update SE using posterior standard deviation
   f. administered_items = administered_items ∪ {i*}
3. Return θ̂, SE
```

**Phase 3: Measurement Invariance Testing**

We will conduct Multi-Group MIRT analysis following the sequential constraint approach:

1. **Configural invariance:** Fit M2PL model separately for each demographic group; verify same factor structure
2. **Metric invariance:** Constrain discrimination parameters ($\mathbf{a}_i$) equal across groups; test ΔCFI < 0.01
3. **Scalar invariance:** Additionally constrain intercepts ($d_i$) equal; test ΔCFI < 0.01

Items failing invariance tests will be flagged for Differential Item Functioning (DIF) analysis using logistic regression:

$$\log \frac{P(X_i = 1)}{P(X_i = 0)} = \beta_0 + \beta_1 \theta + \beta_2 G + \beta_3 (\theta \times G)$$

where $G$ is group membership. Significant $\beta_2$ indicates uniform DIF; significant $\beta_3$ indicates non-uniform DIF.

### 2.4 Experimental Design for Validation

**Experiment 1: Efficiency Validation (Within-Subjects)**

- Participants: n=100 (subset of calibration sample)
- Design: Each participant completes both CAT and fixed-form (30 items) evaluation
- Counterbalancing: Order randomized; 2-week washout between conditions
- Primary outcome: Number of items to achieve SE < 0.3
- Analysis: Paired t-test; equivalence testing for precision comparison

**Experiment 2: Convergent Validity**

- Participants: n=200
- Measures: IRT-HAIC latent trait estimates + established scales:
  - System Usability Scale (SUS) for interaction alignment
  - Trust calibration index (Wischnewski et al., 2023) for trust calibration
  - Procedural justice scale for socio-relational fairness
- Analysis: Pearson correlations; target r ≥ 0.6

**Experiment 3: Predictive Validity**

- Participants: n=300 with 90-day follow-up
- Outcome: System retention/continued use
- Analysis: Logistic regression predicting retention from latent trait quartiles

**Experiment 4: Test-Retest Reliability**

- Participants: n=100
- Design: CAT administration at baseline and 2-week follow-up
- Analysis: Intraclass correlation coefficient (ICC); target ICC > 0.70

### 2.5 Evaluation Metrics

| Metric | Target | Interpretation |
|--------|--------|----------------|
| RMSEA | < 0.08 | Acceptable model fit |
| CFI | > 0.90 | Good comparative fit |
| Mean items to SE < 0.3 | ≤ 18 | 40% efficiency gain |
| ΔCFI (invariance) | < 0.01 | Measurement equivalence |
| Convergent validity (r) | ≥ 0.6 | Strong construct validity |
| Test-retest ICC | > 0.70 | Adequate temporal stability |
| Q3 residual correlations | < 0.2 | Local independence satisfied |

### 2.6 Software and Implementation

All analyses will be conducted in R using:
- `mirt` package for MIRT model estimation
- `catR` package for CAT simulation and implementation
- `lavaan` package for CFA and invariance testing
- Custom Shiny application for participant-facing CAT administration

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1 - Efficiency):** We predict that IRT-HAIC will achieve measurement precision (SE < 0.3) with an average of 18 items or fewer, representing at least 40% reduction compared to the 30-item fixed-form baseline. This prediction is grounded in prior work demonstrating 60% efficiency gains in AI evaluation using IRT (Zhuang et al., 2023); our conservative 40% target accounts for the additional complexity of multidimensional measurement.

**Secondary Outcomes:**
- P2 (Convergent Validity): Latent trait estimates will correlate r ≥ 0.6 with established measures
- P3 (Predictive Validity): High interaction alignment will predict ≥15% higher 90-day retention
- P4 (Measurement Invariance): ΔCFI < 0.01 across all demographic comparisons
- P5 (Construct Structure): EFA will reveal 2-4 factors explaining ≥60% of variance
- P6 (DIF Detection): Items flagged for DIF will show larger demographic disparities in traditional metrics

**Falsification Conditions:** The hypothesis will be rejected if: (1) model fit fails (RMSEA > 0.08 or CFI < 0.90); (2) efficiency gains fall below 20%; (3) measurement invariance fails for any major demographic group; (4) convergent validity correlations fall below r = 0.4; or (5) local independence assumptions are violated.

### 3.2 Scientific Impact

This research will establish psychometric foundations for AI-HCI evaluation that have been notably absent from the field. By demonstrating that interaction quality can be modeled as stable latent traits, we provide theoretical grounding for comparative evaluation across systems and populations. The validated three-dimensional model (interaction alignment, trust calibration, socio-relational fairness) offers a parsimonious yet comprehensive framework for understanding what constitutes quality in human-AI collaboration.

### 3.3 Practical Impact

The IRT-HAIC framework will enable:
- **Reduced evaluation burden:** 40% fewer items means faster, less fatiguing assessments
- **Scalable deployment:** Efficient evaluation enables large-scale A/B testing and continuous monitoring
- **Standardized comparison:** Calibrated item bank allows meaningful cross-system benchmarking
- **Equitable assessment:** Measurement invariance ensures fair evaluation across user populations

### 3.4 Broader Impact

By embedding fairness considerations directly into the evaluation methodology through measurement invariance testing and DIF detection, IRT-HAIC advances responsible AI development practices. The framework provides tools to identify and remediate evaluation items that function differently across demographic groups, supporting the broader goal of equitable AI-HCI systems.

### 3.5 Deliverables

1. Validated 100-item evaluation bank with calibrated parameters
2. Open-source CAT implementation (R package and web application)
3. Technical documentation and user guidelines
4. Peer-reviewed publications detailing methodology and validation results

### 3.6 Limitations and Future Directions

We acknowledge several limitations: the framework requires substantial initial calibration effort (n=1,000 users); results may not generalize to non-English-speaking populations without translation and re-validation; and annual recalibration may be necessary as AI systems evolve. Future work will address cold-start problems for new systems through transfer learning approaches and extend the framework to additional languages and cultural contexts.