# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1: IRT-HAIC)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-IRT-HAIC-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under standardized evaluation conditions, if AI-HCI system quality is modeled as latent traits using Multidimensional Item Response Theory (MIRT), then adaptive evaluation will achieve equivalent measurement precision with 40% fewer items while maintaining measurement invariance across demographic groups, because latent trait estimation optimally selects informative items based on posterior ability distributions.

**Alternative Hypothesis (H0):**
AI-HCI system quality cannot be reliably modeled as latent traits; adaptive testing based on MIRT will NOT achieve meaningful efficiency gains (≤15% reduction) over fixed-form evaluation, OR measurement invariance will fail across at least one major demographic group (ΔCFI > 0.01).

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| AI-HCI System Type | Independent | Categorical: RLHF chatbots, HITL design tools, fairness-aware recommenders | 3-5 system categories |
| User Population Characteristics | Independent | Demographics (age, education, tech experience) stratified sampling | n=1000 stratified |
| Evaluation Item Characteristics | Independent | Item difficulty (b), discrimination (a), guessing (c) parameters from calibration | b: [-3, +3], a: [0.5, 2.5], c: [0, 0.25] |
| Latent Trait Estimates (θ) | Dependent | MIRT M2PL model output: θ vector for interaction alignment, trust calibration, socio-relational fairness | θ: [-3, +3] per dimension |
| Measurement Precision (SEM) | Dependent | Standard Error of Measurement from Fisher Information | Target: SE < 0.3 |
| Trust Calibration Index | Dependent | CI = 1 - \|Trust_Score - Performance_Score\| | 0.0 (miscalibrated) to 1.0 (perfect) |
| Item Presentation Order | Controlled | Randomized within adaptive algorithm constraints | N/A |
| Evaluation Context | Controlled | Standardized online survey platform, 10-minute time limit | Fixed |
| CAT Stopping Rule | Controlled | SE < 0.3 or max 30 items | Fixed algorithm |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Latent Traits → Item Response Patterns
    ↓
Step 2: Item Response Patterns → MIRT Parameter Estimation
    ↓
Step 3: MIRT Parameters → Adaptive Item Selection
    ↓
Step 4: Adaptive Selection → Efficient Measurement with Invariance
    ↓
    OUTCOME: Standardized, efficient, fair AI-HCI evaluation
```

**Step 1: Latent Traits → Item Response Patterns**
The user's underlying AI-HCI interaction quality (θ) probabilistically determines responses to evaluation items via the item characteristic function P(X=1|θ,a,b,c). Three latent dimensions: (1) Interaction Alignment, (2) Trust Calibration Accuracy, (3) Socio-Relational Fairness.

**Step 2: Item Response Patterns → MIRT Parameter Estimation**
Observed response patterns across n=1000 users enable maximum likelihood estimation of item parameters (a,b,c) and latent trait covariance structure using M2PL model.

**Step 3: MIRT Parameters → Adaptive Item Selection**
Calibrated item parameters enable CAT algorithm to select maximally informative items using Kullback-Leibler information criterion, targeting SE < 0.3.

**Step 4: Adaptive Selection → Efficient Measurement with Invariance**
Optimal item selection achieves equivalent precision with ~40% fewer items; Multi-Group MIRT validates measurement invariance across demographic groups.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Martinez-Plumed et al. (2019) | IRT successfully extracts latent ability from ML classifier response patterns | Strong |
| Step 2 → Step 3 | Strugatski & Alexandron (2024) | Person-fit statistics detect deviations from expected IRT patterns | Strong |
| Step 3 → Step 4 | IRT for LLMs (Zhuang et al., 2023) | CAT achieves 60% efficiency gains in AI evaluation | Strong |
| Step 4 → Outcome | ConSiDERS Framework (2024) | Multi-dimensional evaluation frameworks are feasible at scale | Medium |

**Key Tension:**
- **Tension:** IRT assumes stable latent traits, but AI systems evolve rapidly (Lindström et al., 2025 critique). Trust calibration is dynamic, not static (Wischnewski et al., 2023).
- **Resolution:** This verification plan tests temporal stability via test-retest reliability (2-week interval); annual recalibration protocol addresses system evolution.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | AI-HCI quality exists as stable latent traits | IRT validated in psychometrics 70+ years; Martinez-Plumed et al. (2019) applied to AI | Model fit fails (RMSEA > 0.08); hypothesis rejected |
| A2 | Local independence holds (items conditionally independent given θ) | Standard IRT assumption; testable via Q3 statistics | Biased parameter estimation; need testlet models |
| A3 | Latent trait distributions approximately multivariate normal | Required for M2PL; common in large samples | Non-parametric IRT alternatives needed |
| A4 | n=1000 stratified sample is representative | Power analysis supports this for MIRT | Generalizability limited; need larger sample |
| A5 | Expert consensus validates EFA construct structure | Two-phase approach provides empirical + expert validation | Construct validity threatened; iterate construct discovery |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- AI-HCI systems with human-in-the-loop evaluation
- Users ≥18 years, English-speaking
- Evaluation contexts with 10+ minute interaction windows
- Systems deployable on standard web platforms

**Where Hypothesis Does NOT Apply:**
- Fully autonomous AI without human interaction
- Real-time/streaming evaluation (latency constraints)
- Non-English languages (item bank requires translation/validation)
- Children/minors (different consent and item complexity requirements)
- Edge devices with limited computational resources

**Known Limitations:**
- Sample generalizability: Results may not transfer to non-Western populations
- Temporal stability: Annual recalibration required as AI systems evolve
- Cold-start problem: New systems require minimum item exposure before trait estimation
- Resource intensity: Initial calibration requires n=1000 users (subsequent CAT is efficient)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Efficiency vs Fixed-Form):**
IRT-HAIC adaptive testing will achieve measurement precision (SE < 0.3) with ≤18 items on average, representing ≥40% reduction compared to fixed-form 30-item evaluation.

*Measurement:*
- Mean items to convergence in CAT vs. fixed 30-item form
- SEM equivalence test: CAT_SE ≈ Fixed_SE (within 0.05)
- Statistical test: Paired t-test, n ≥ 100 users

*Basis:*
IRT for LLMs (Zhuang et al., 2023) demonstrated ~60% efficiency gains; conservative 40% target accounts for multi-dimensional complexity.

*Success Criteria for Phase 2B:*
- Primary: Mean items ≤ 18 with SE < 0.3 (p < 0.05)
- Falsification: Mean items > 24 OR SE > 0.35 triggers rejection

**Secondary Predictions:**

**P2 (Convergent Validity):**
Latent trait estimates (θ) will correlate r ≥ 0.6 with existing validated measures:
- Interaction Alignment θ₁ ↔ User satisfaction (SUS-like scales)
- Trust Calibration θ₂ ↔ Trust calibration indices (Wischnewski et al.)
- Socio-Relational Fairness θ₃ ↔ Procedural justice scales

**P3 (Predictive Validity):**
Users with higher interaction alignment (θ₁) will show ≥15% higher 90-day retention rate compared to lowest quartile.

**P4 (Measurement Invariance):**
Multi-Group MIRT will demonstrate configural, metric, and scalar invariance across ≥3 demographic groups (ΔCFI < 0.01, ΔRMSEA < 0.015).

**P5 (Construct Structure):**
EFA will reveal 2-4 factors explaining ≥60% of variance, with simple structure (loadings > 0.4 on primary factor, < 0.3 on others).

**P6 (DIF Detection):**
Items flagged for Differential Item Functioning will show ≥20% larger demographic disparities in traditional metrics, validating DIF detection utility.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Model Fit Failure:** RMSEA > 0.08 OR CFI < 0.90 (latent structure invalid)
2. **Efficiency Failure:** CAT requires > 24 items on average (< 20% improvement)
3. **Invariance Failure:** ΔCFI > 0.01 for any major demographic comparison
4. **Validity Failure:** Convergent correlations r < 0.4 with validated measures
5. **Assumption Violation:** Q3 statistics show > 30% of item pairs with residual r > 0.2

### 1.7 SOTA Baseline (Not Applicable)

This hypothesis develops a new evaluation framework rather than improving on existing performance benchmarks. No SOTA comparison mode applicable.

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- MIRT calibration: n = 1000 (standard for 3-dimension MIRT with 100 items)
- CAT efficiency validation: n = 100 (within-subjects comparison)
- Measurement invariance: n = 200 per demographic group (minimum 3 groups)
- Statistical power: 0.80 for medium effect sizes (d = 0.5)

**Test Specifications:**

| Analysis | Method | Significance | Reporting |
|----------|--------|--------------|-----------|
| Model Fit | CFA/MIRT | RMSEA < 0.08, CFI > 0.90 | Fit indices, residuals |
| Efficiency | Paired t-test | α = 0.05, one-tailed | Mean difference, 95% CI, Cohen's d |
| Invariance | Multi-Group MIRT | ΔCFI < 0.01, ΔRMSEA < 0.015 | Configural/metric/scalar models |
| Validity | Pearson correlation | α = 0.05 | r, 95% CI, p-value |
| DIF | Logistic regression | α = 0.01 (Bonferroni) | Effect size, flagged items |

**Required Software:**
- R packages: mirt, lavaan, ltm, catR
- Item bank management: custom platform or Concerto

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does AI-HCI interaction quality exist as measurable latent traits that satisfy IRT model assumptions?"
- Maps to: P1 (Model Fit), P5 (Construct Structure)
- Verification type: Empirical (EFA/CFA on n=250 pilot)
- Critical: MUST PASS for framework validity

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism the actual pathway from latent traits to efficient measurement?"
- Maps to: Causal links 1-4
- Verification type: Sequential validation
- Will decompose into 4 sub-hypotheses in Phase 2B:
  - H-M1: Latent traits → Item response patterns (IRT model fit)
  - H-M2: Response patterns → MIRT calibration (parameter stability)
  - H-M3: MIRT parameters → CAT selection (information gain)
  - H-M4: CAT → Efficiency + Invariance (outcome achievement)
- Total sub-hypotheses: 4 (based on N=4 causal chain length)

**SH3 (Comparison):**
"Does IRT-HAIC outperform fixed-form evaluation on efficiency while maintaining validity?"
- Maps to: P1 (Efficiency), P2 (Convergent Validity), P4 (Invariance)
- Verification type: Comparative empirical (within-subjects design)
- Critical: Determines practical value

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-IRT-HAIC-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table included)
- [x] Causal chain length (N=4) determined and documented
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (6 predictions, P1 marked as primary)
- [x] Falsification criteria are defined (5 rejection conditions)
- [x] Baselines are identified for comparison (HumanAgencyBench, ConSiDERS)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Collection Strategy:** How to recruit n=1000 stratified users across 5 AI-HCI system types? Industry partnership vs. crowdsourcing trade-offs?

2. **Item Bank Development:** What is the optimal ratio of items per construct? How many expert rounds for Delphi panel content validation?

3. **Cold-Start Protocol:** How to evaluate new AI-HCI systems before item calibration? Transfer learning from similar systems?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
