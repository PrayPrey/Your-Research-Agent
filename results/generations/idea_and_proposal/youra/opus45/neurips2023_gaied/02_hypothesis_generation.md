# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-SRALT-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of structured educational domains (programming, STEM), if an LLM tutoring system integrates (1) independent Deep Knowledge Tracing for mastery prediction and (2) spacing-effect-optimized review scheduling, then long-term retention at 4-week intervals will be 20%+ higher than non-spaced LLM tutoring AND DKT predictions will correlate with actual retention at r > 0.7, because the spacing effect enhances memory consolidation while DKT provides accurate mastery forecasting validated against delayed outcomes.

**Alternative Hypothesis (H0):**
There is no significant difference in 4-week retention between LLM tutoring with SRALT integration and standard LLM tutoring without spaced repetition/DKT components. DKT predictions do not correlate meaningfully (r ≤ 0.3) with actual long-term retention outcomes.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Spaced Repetition Integration | Independent | Binary: SM-2 algorithm-based review scheduling present vs. absent | {0, 1} |
| DKT Integration | Independent | Binary: Independent DKT model for mastery prediction present vs. absent | {0, 1} |
| Long-term Retention | Dependent | Assessment accuracy at 4-week delayed test (% correct) | 0-100% |
| Prediction-Outcome Correlation | Dependent | Pearson correlation between DKT predictions and actual 4-week retention | -1.0 to 1.0 |
| Subject Domain | Controlled | Fixed to programming education (Python basics) | Python fundamentals |
| Student Population | Controlled | Undergraduate CS students, no prior Python experience | N ≥ 50 |
| LLM Base Model | Controlled | Fixed LLM (e.g., GPT-4 or equivalent) | Single model |

### 1.3 Causal Mechanism

**Causal Chain (N=4 Steps):**

```
[DKT Model] → [Mastery State Estimation] → [Spacing Scheduler] → [LLM Tutor Dialogue] → [Long-term Retention + Validation Data]
```

**Step 1: DKT Model → Mastery State Estimation**
- Mechanism: DKT processes interaction sequences to estimate concept-level mastery probabilities
- Evidence: Neural sequence modeling captures learning dynamics (Casalino et al. 2021)
- Falsification: DKT fails to generalize to new student populations (cold-start problem) OR interaction data is too sparse

**Step 2: Mastery Estimation → Spacing Scheduler**
- Mechanism: Mastery predictions inform optimal review timing via SM-2 algorithm
- Evidence: Lower mastery concepts need shorter intervals; high mastery allows longer gaps (Dunlosky 2013)
- Falsification: SM-2 parameters are miscalibrated for the domain OR mastery predictions are too noisy to inform scheduling

**Step 3: Spacing Scheduler → LLM Tutor Dialogue**
- Mechanism: Scheduled reviews trigger contextual tutoring interactions
- Evidence: LLM generates personalized review questions and explanations based on learner state (MAIC - Yu et al. 2024)
- Falsification: LLM fails to generate pedagogically appropriate content OR students disengage from review sessions

**Step 4: LLM Dialogue + Spaced Reviews → Long-term Retention + Validation Data**
- Mechanism: Repeated spaced interactions consolidate memory AND generate prediction-outcome pairs for self-validation
- Evidence: Delayed assessments provide ground truth for DKT forecast accuracy (Katz et al. 2021 - 3-week retention)
- Falsification: Assessment items are not equivalent across timepoints OR attrition creates selection bias in validation data

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Casalino et al. 2021 | DKT models capture student mastery trajectories | Strong |
| Step2 → Step3 | Dunlosky 2013 meta-analysis | Distributed practice is HIGH utility across domains | Strong |
| Step3 → Step4 | Yu et al. 2024 (MAIC) | 100K+ learning records demonstrate LLM tutoring at scale | Medium |
| Step4 → Outcome | Katz et al. 2021 | Spacing effect persists at 3-week retention interval | Strong |

**Key Tension:**
- Tension: Hooshyar et al. (2025) shows DKT outperforms LLMs for mastery prediction (AUC=0.83), but LLMs provide richer tutoring dialogues than traditional DKT-based ITS
- Resolution: SRALT uses a HYBRID architecture where DKT handles prediction (its strength) and LLM handles dialogue generation (its strength), addressing the tension by combining best-of-both

### 1.4 Key Assumptions

1. **Spacing effect transfers to LLM tutoring dialogues**
   - Evidence: Dunlosky 2013 meta-analysis shows distributed practice has HIGH utility across domains including complex materials
   - Consequence if violated: Retention improvement may be smaller than expected; need to test with pilot study

2. **DKT achieves AUC > 0.80 on programming education data**
   - Evidence: Hooshyar 2025 reports DKT AUC=0.83 across educational domains
   - Consequence if violated: Mastery predictions will be unreliable; need domain-specific DKT training data

3. **Students will engage with delayed review sessions**
   - Mitigation: Engagement tracking + push notifications + gamification
   - Consequence if violated: Attrition bias will affect longitudinal validation; need intent-to-treat analysis

4. **Assessment quality is consistent across timepoints**
   - Control: Standardized question bank with item difficulty calibration
   - Consequence if violated: Retention measurements will be confounded by assessment difficulty variation

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Structured educational domains with clear concept hierarchies (programming, mathematics, STEM)
- Students with moderate engagement levels who complete assigned reviews
- LLM tutoring contexts where dialogue-based interaction is primary mode
- Retention intervals of 1-12 weeks (validated range for spacing effect)

**Where It Does NOT Apply:**
- Open-ended creative domains without clear mastery criteria
- Highly personalized learning paths where concept structure varies per student
- Very short retention intervals (< 1 day) or very long intervals (> 6 months)
- Populations with extremely low engagement (< 30% review completion)

**Known Limitations:**
- Student attrition over longitudinal periods may bias results
- Cold-start problem for DKT with new students (need 5-10 interactions minimum)
- Confounding variables (motivation, prior knowledge) cannot be fully controlled in real deployments

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Retention Improvement vs. Baseline)**:
Students using SRALT will achieve 4-week retention accuracy > 20% higher than students using standard LLM tutoring without spaced repetition.

*Measurement*:
- Retention accuracy (% correct) on delayed test at 4 weeks
- Comparison: SRALT group vs. Control group (same LLM tutor, no spacing/DKT)
- Statistical test: Independent samples t-test, p < 0.05

*Basis*:
Domain standard for meaningful educational intervention effect. Dunlosky 2013 meta-analysis indicates distributed practice produces large effect sizes (d > 0.5) relative to massed practice.

*Success Criteria for Phase 2B*:
- Primary: Mean retention difference > 20 percentage points (p < 0.05, one-tailed)
- Falsification: Mean retention difference ≤ 5 percentage points triggers rejection

**Secondary Predictions:**

**P2 (DKT Prediction Accuracy)**:
DKT predictions will correlate with actual 4-week retention at r > 0.7

*Measurement*:
- Pearson correlation between DKT-predicted mastery at end of learning phase and actual 4-week test scores
- Sample: All students who completed both learning and delayed assessment phases

*Success Criteria*:
- r > 0.7 (strong correlation) with p < 0.01
- Falsification: r ≤ 0.3 (weak correlation) triggers mechanism revision

**P3 (Self-Validation Capability)**:
The system will generate sufficient prediction-validation pairs to detect DKT drift within a semester deployment.

*Measurement*:
- Number of complete prediction-outcome cycles per student
- Minimum threshold: 10 cycles per student for statistical power

*Success Criteria*:
- ≥ 80% of students complete ≥ 10 prediction-validation cycles
- DKT recalibration feasible with collected data

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Retention difference ≤ 5% between SRALT and control groups
   (No meaningful benefit from spacing/DKT integration)

2. **Mechanism Failure**: DKT prediction-retention correlation r ≤ 0.3
   (DKT cannot accurately predict long-term outcomes)

3. **System Failure**: < 50% of students complete delayed assessments
   (Self-validation architecture infeasible due to attrition)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

*Not applicable - Absolute performance validation mode selected.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Expected effect size (Cohen's d): 0.8 (large effect based on spacing effect literature)
- Required sample size: n ≥ 26 per group (power = 0.8, α = 0.05, one-tailed)
- Recommended: n = 50 per group to account for attrition

**Test Specification:**
- Primary outcome: Independent samples t-test (SRALT vs. Control)
- Secondary outcome: Pearson correlation with Fisher z transformation
- Significance level: α = 0.05 (one-tailed for directional hypothesis)
- Report format: Mean difference, 95% CI, Cohen's d, p-value

**Design:**
- Randomized controlled trial with within-subject delayed testing
- Same random seeds for LLM generation across conditions
- Blinded assessment (graders unaware of condition)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the spacing effect transfer from laboratory settings to LLM tutoring dialogues in programming education?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison (SRALT vs. Control)
- Critical: MUST PASS for hypothesis to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism (DKT → Scheduling → Dialogue → Retention) the actual cause of improved outcomes?"
- Maps to: Causal mechanism (4 steps)
- Decomposes into: H-M1 (DKT mastery estimation), H-M2 (Spacing scheduling), H-M3 (Dialogue generation), H-M4 (Retention + validation)
- Verification type: Causal analysis with ablation studies
- Total mechanism sub-hypotheses: 4

**SH3 (Comparison):**
"Does SRALT outperform standard LLM tutoring on both retention AND prediction accuracy?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value and self-validation capability

**Total Sub-Hypotheses for Phase 2B:** 2 + 4 = 6 (SH1 + SH2×4 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-SRALT-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table complete)
- [x] Causal chain length determined: N = 4
- [x] Key tension identified (DKT vs. LLM strengths) and resolution proposed (hybrid)
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 total, primary marked)
- [x] Falsification criteria are defined (3 rejection conditions)
- [x] Baselines identified for comparison (MAIC, standard LLM tutor)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability**: Is there existing DKT training data for Python programming education, or does this need to be collected in a pilot study?

2. **Technical Feasibility**: What is the latency impact of running DKT inference during LLM tutoring sessions? Can this be optimized for real-time interaction?

3. **Priority Verification Order**: Should SH1 (existence) be tested first in a smaller pilot before investing in full system development for SH2 (mechanism)?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
