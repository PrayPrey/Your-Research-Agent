# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - Moral Curriculum Learning)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MCL-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions of LLM fine-tuning for value alignment, if training data is structured as a Kohlberg-inspired moral curriculum with progressive complexity stages (preconventional → conventional → postconventional) and stage advancement requires demonstrated mastery (80-90% alignment), then the model will achieve superior moral reasoning generalization compared to flat RLHF training, because progressive foundation-building enables robust transfer to novel ethical dilemmas similar to human moral development.

**Alternative Hypothesis (H0):**
There is no significant difference in moral reasoning generalization between LLMs trained with Kohlberg-structured moral curriculum (MCL) and those trained with standard flat RLHF/DPO methods when controlling for total training compute and data volume.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Moral Curriculum Structure | Independent | 6-stage curriculum based on Kohlberg levels (Stages 1-2: preconventional, 3-4: conventional, 5-6: postconventional), operationalized via Rest's DIT scoring methodology | 6 discrete stages with DIT P-score thresholds (<30, 30-50, >50) |
| Stage Mastery Threshold | Independent | Alignment score on held-out moral dilemmas required before stage advancement | 80-90% (hyperparameter, validation-tuned) |
| Value Alignment Score | Dependent | Agreement rate with human moral judgments on standardized benchmarks (ETHICS, MoralBench, Moral Machine) | 0-100% alignment |
| Moral Generalization | Dependent | Performance on novel moral dilemmas not seen during training (held-out test set) | Measured as accuracy delta vs. training distribution |
| Base Model Architecture | Controlled | Fixed LLM architecture across all experimental conditions | Llama-2 7B/13B or equivalent |
| Total Training Compute | Controlled | Equal FLOPs budget across curriculum and baseline conditions | Fixed FLOP budget (e.g., 10^18 FLOPs) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Kohlberg-Structured Curriculum
    ↓ (creates)
Step 2: Stage-Appropriate Moral Representations
    ↓ (enables)
Step 3: Hierarchical Foundation for Complex Reasoning
    ↓ (produces)
Outcome: Superior Generalization to Novel Moral Dilemmas
```

**Detailed Mechanism:**

1. **Step 1 → Step 2 (Curriculum → Representations):** The Kohlberg-structured curriculum organizes training data by moral complexity, causing the model to learn distinct internal representations for each complexity level.

2. **Step 2 → Step 3 (Representations → Foundation):** Stage mastery requirements ensure the model has robust representations of simpler moral concepts before encountering complex scenarios.

3. **Step 3 → Outcome (Foundation → Generalization):** Models with hierarchically-organized moral foundations generalize better to novel dilemmas because they can decompose unfamiliar scenarios into component moral principles.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Hacohen & Weinshall 2019 | Curriculum learning improves representation quality through ordered exposure | Strong |
| Step 1 → Step 2 | Fayek et al. 2020 | Progressive learning framework demonstrates stage-based representation learning | Strong |
| Step 2 → Step 3 | Kohlberg (1969) | Human moral development follows hierarchical progression with stage prerequisites | Medium (cross-domain) |
| Step 2 → Step 3 | Rest's DIT research | Moral reasoning complexity is measurable and follows developmental hierarchy | Strong |
| Step 3 → Outcome | Piloto et al. 2022 | Developmental psychology-inspired AI achieves superior generalization in intuitive physics | Strong (precedent) |
| Step 3 → Outcome | Coleman et al. 2025 | LLMs can be evaluated on Kohlberg stages, suggesting stages are computationally meaningful | Medium |

**Key Tension:**
- **Tension:** Piloto et al. 2022 successfully transferred developmental psychology concepts to AI for intuitive physics, but moral reasoning may have fundamentally different computational properties than physical reasoning.
- **Resolution:** This verification plan tests whether the developmental-to-AI transfer pattern holds for moral domains specifically, with Stage 1 experiments validating Kohlberg stage mappability before full curriculum training.

### 1.4 Key Assumptions

1. **Moral reasoning has hierarchical complexity structure**
   - Evidence: Kohlberg's 60+ years of validated research; Rest's DIT provides quantitative scoring
   - Consequence if violated: Curriculum structure provides no advantage; stages are arbitrary groupings

2. **Kohlberg's stages map to computationally distinct complexity levels**
   - Evidence: Coleman et al. 2025 shows LLMs can be evaluated on stages; MoralBench provides stage-annotated scenarios
   - Consequence if violated: Training curriculum has no learning signal benefit over random ordering

3. **Mastery of simpler moral concepts enables complex moral reasoning**
   - Evidence: Curriculum learning literature (Hacohen & Weinshall 2019); educational scaffolding theory
   - Consequence if violated: Stage-gated training provides no transfer benefit; flat training is equally effective

4. **Curriculum learning benefits transfer to moral reasoning domain**
   - Evidence: Curriculum benefits demonstrated in NLP, vision, RL domains; Piloto et al. 2022 cross-domain precedent
   - Consequence if violated: Domain-specific factors nullify curriculum benefits for moral tasks

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- LLM value alignment training (fine-tuning phase)
- Moral reasoning tasks with definable complexity gradients
- English-language moral scenarios (initial scope)
- Models with sufficient capacity (≥7B parameters)

**Where Hypothesis Does NOT Apply:**
- Pre-training phase (curriculum requires fine-tuning context)
- Non-moral NLP tasks (factual knowledge, general reasoning)
- Real-time moral decision systems (training methodology only)

**Known Limitations:**
- Kohlberg's framework has Western individualistic bias (Gilligan's critique)
- Stage boundaries may be fuzzy rather than discrete
- Initial experiments limited to English-language benchmarks

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Moral Generalization vs. RLHF Baseline):**
LLMs trained with MCL will achieve ≥10% higher accuracy on novel moral dilemmas (held-out test set) compared to LLMs trained with standard flat RLHF, when controlling for total training compute.

*Measurement:*
- Metric: Accuracy on held-out moral reasoning benchmark (MoralBench/ETHICS novel subset)
- Target: MCL accuracy - RLHF accuracy ≥ 10 percentage points
- Statistical test: Paired t-test, n ≥ 20 runs, p < 0.05

**Secondary Predictions:**

**P2 (Stage-Wise Learning Efficiency):**
MCL will demonstrate monotonically increasing training time per stage (Stage 1 fastest, Stage 6 slowest), reflecting complexity gradient.

**P3 (Robustness to Distribution Shift):**
MCL-trained models will show smaller performance degradation on out-of-distribution moral scenarios compared to RLHF baselines.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure:** MCL accuracy on novel dilemmas ≤ RLHF accuracy (no improvement or worse)
2. **Mechanism Failure:** Stage mastery shows no correlation with subsequent stage performance
3. **Curriculum Failure:** Random ordering of moral scenarios performs equivalently to Kohlberg ordering

### 1.7 SOTA Baseline (Optional)

*Not applicable - This hypothesis targets a novel methodology rather than SOTA performance comparison.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect expected)
- Required runs: n ≥ 20 per condition
- Statistical power: 0.8
- Significance level: α = 0.05

**Test Specification:**
- Primary comparison: Paired t-test (same base model, different training methods)
- Multiple comparison correction: Bonferroni for 3 predictions
- Report format: Mean ± Std Dev, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does progressive moral curriculum training (MCL) produce measurably different learning dynamics compared to flat RLHF training?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical comparison
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 3-step causal mechanism (curriculum → representations → foundation → generalization) the actual cause of any observed improvements?"
- Maps to: Causal mechanism (N=3 steps)
- Phase 2B will decompose into 3 sub-hypotheses:
  - H-M1: Curriculum structure creates stage-appropriate representations
  - H-M2: Stage mastery builds hierarchical foundations
  - H-M3: Hierarchical foundations enable compositional generalization
- Verification type: Causal analysis, ablation studies

**SH3 (Comparison):**
"Does MCL outperform RLHF baselines on moral generalization metrics?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical

**Total sub-hypotheses in Phase 2B:** 2 + 3 = 5 (SH1, H-M1, H-M2, H-M3, SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-MCL-v1)
- [x] Confidence level specified (0.78)
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Causal chain length (N=3) determined
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions)
- [x] Falsification criteria are defined (3 criteria)
- [x] Baselines are identified for comparison (RLHF, DPO)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Which existing moral reasoning datasets can be most effectively annotated with Kohlberg stage labels?

2. **Compute Requirements:** What is the minimum model scale required to observe curriculum learning benefits in moral reasoning?

3. **Priority Verification Order:** Should we first validate Kohlberg stage mappability before full curriculum training?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
