# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (Round 1 - BAQI Framework)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-BAQI-v1
**Confidence Level:** 0.80

**Main Hypothesis:**
Under condition [multi-turn human-AI dialogue interactions with 10-50 turns], if [the Bidirectional Alignment Quality Index (BAQI) framework integrating AI Alignment Score (AAS), Human Agency Score (HAS), and Co-adaptation Trajectory (CAT) is applied using Pareto multi-objective optimization], then [alignment evaluation will achieve stronger correlation (r > 0.6) with long-term user satisfaction and autonomy preservation than unidirectional metrics (RLHF reward scores alone)] because [bidirectional measurement captures both AI adaptation quality AND human agency preservation dynamics that single-metric approaches systematically miss, as demonstrated by HumanAgencyBench findings that "agency support does not appear to consistently result from RLHF"].

**Alternative Hypothesis (H0):**
There is no significant difference in correlation with long-term user satisfaction between BAQI composite scores and unidirectional RLHF reward scores (r_BAQI ≤ r_RLHF, p > 0.05), indicating that human agency metrics and co-adaptation trajectory do not provide additional predictive value beyond traditional AI alignment measures.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| AI Alignment Score (AAS) | Independent | Normalized reward model outputs from RLHF-trained models, scaled to [0,1] | 0.0 - 1.0 (higher = better alignment) |
| Human Agency Score (HAS) | Independent | LLM-as-judge evaluation of 6 HumanAgencyBench dimensions per turn, averaged | 0.0 - 1.0 (higher = better agency support) |
| Co-adaptation Trajectory (CAT) | Independent | Linear regression slope of HAS scores across interaction + variance measure | Slope: [-0.05, +0.05] per turn; Variance: [0, 0.3] |
| BAQI Composite Index | Dependent | Pareto frontier analysis identifying non-dominated {AAS, HAS, CAT} configurations | Pareto rank 1-N (lower = better) |
| Long-term User Satisfaction | Dependent | User-reported satisfaction at interaction end (7-point Likert scale) | 1-7 (7 = highest satisfaction) |
| Autonomy Preservation | Dependent | Self-reported autonomy via adapted 9-item GHAIs scale | 9-63 (higher = greater perceived autonomy) |
| Interaction History | Controlled | Standardized multi-turn dialogues with fixed turn counts (10, 25, 50 turns) | Fixed per experimental condition |

### 1.3 Causal Mechanism

```
Step 1: AI Alignment Score (AAS) → AI Response Quality
        ↓
Step 2: Human Agency Score (HAS) → Perceived Autonomy
        ↓
Step 3: Co-adaptation Trajectory (CAT) → Trust Calibration
        ↓
Step 4: {AAS + HAS + CAT via Pareto} → Long-term User Satisfaction
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Training Helpful & Harmless (Anthropic, 2022) | RLHF produces models preferred by humans 70%+ of time | Strong |
| Step2 → Step3 | HumanAgencyBench (2025) | LLM-as-judge achieves correlation with human evaluators on 6 dimensions | Strong |
| Step3 → Step4 | FABRIC (2023) | Iterative feedback produces measurable improvement trajectories | Medium |
| Step4 → Outcome | Beyond Preferences (2024) | Pure preference satisfaction without agency leads to disempowerment | Medium |

**Key Tension:**
- **Tension:** HumanAgencyBench (2025) finds "Agency support does not appear to consistently result from RLHF," suggesting AAS and HAS may be orthogonal or even inversely correlated in some systems.
- **Resolution:** This tension is precisely why BAQI uses Pareto optimization rather than weighted averaging—to identify configurations that achieve both high AAS AND high HAS without forcing a trade-off assumption. The verification plan will explicitly test whether AAS-HAS correlation is positive, negative, or near-zero across different AI systems.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|--------------------|-----------------------|
| A1 | HumanAgencyBench 6 dimensions can be reliably automated via LLM-as-judge with >0.7 inter-rater reliability | HumanAgencyBench paper reports LLM evaluator correlation with humans | HAS component becomes unreliable; would need human annotation (not scalable) |
| A2 | Co-adaptation patterns are detectable within 10-50 turn interaction sequences | FABRIC paper shows detectable improvement over iterative rounds | CAT component adds noise rather than signal; longer sequences needed |
| A3 | Users can accurately report satisfaction and perceived autonomy post-interaction | GHAIs scale validated in psychology literature (CFA-confirmed) | Ground truth labels are unreliable; need behavioral proxies |
| A4 | RLHF reward models provide meaningful AI alignment signal across domains | Anthropic RLHF paper (3,559 citations); Safe RLHF (556 citations) | AAS component fails to capture alignment; need domain-specific reward models |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- AI assistants with multi-turn dialogue interactions (chatbots, copilots, agents)
- Interactions spanning 10-50 turns with consistent user identity
- Systems where both AI behavior quality AND user agency matter

**Where Hypothesis Does NOT Apply:**
- Single-turn queries (no trajectory to measure)
- Non-conversational AI systems (image generators, recommendation engines without dialogue)
- Fully autonomous AI agents without human oversight

**Known Limitations:**
- LLM-as-judge reliability varies across models and dimensions (calibration required)
- Individual user variation in agency perception may dominate population-level patterns
- CAT metrics are novel and require extensive pilot validation

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (BAQI-Satisfaction Correlation):**
BAQI composite scores will achieve significantly stronger correlation with long-term user satisfaction than RLHF reward scores alone.

*Measurement:*
- r(BAQI, Satisfaction) > r(AAS, Satisfaction) with p < 0.05
- Expected effect: r_BAQI ≥ 0.6 vs r_AAS ≤ 0.4
- Statistical test: Fisher's z-test for correlation comparison, n ≥ 100 interactions

*Success Criteria:*
- Primary: r(BAQI, Satisfaction) - r(AAS, Satisfaction) ≥ 0.15 (p < 0.05)
- Falsification: r(BAQI, Satisfaction) ≤ r(AAS, Satisfaction) triggers hypothesis rejection

**Secondary Predictions:**

**P2 (CAT-Agency Correlation):**
Negative co-adaptation trajectory (declining HAS slope) will correlate with lower user-reported autonomy preservation (r > 0.4, p < 0.05).

**P3 (Pareto Dominance):**
Pareto-optimal BAQI configurations will show no single-metric baseline dominating across all evaluation dimensions.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** r(BAQI, Satisfaction) ≤ r(AAS, Satisfaction) - No predictive advantage
2. **Mechanism Failure:** LLM-as-judge HAS scores show <0.6 correlation with human evaluators
3. **Trajectory Failure:** CAT slope shows no significant correlation with user outcomes (r < 0.2)
4. **Integration Failure:** Simple weighted average of AAS+HAS outperforms Pareto optimization

### 1.7 Statistical Verification Design

**Sample Size:** n ≥ 100 human-AI interactions with complete metrics
**Primary Test:** Fisher's z-test for comparing dependent correlations
**Power:** 0.80, Alpha: 0.05 (one-tailed)
**Report Format:** Correlation coefficients with 95% CI, Fisher's z statistic, effect size

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does the BAQI framework produce reliable, replicable scores across different AI systems and interaction contexts?"
- Maps to: Primary prediction
- Verification type: Empirical reliability testing
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the three-component causal mechanism (AAS → HAS → CAT → Satisfaction) the actual explanation for BAQI's predictive advantage?"
- Maps to: Causal mechanism (4 steps)
- Decomposes into 4 sub-hypotheses: H-M1 (AAS), H-M2 (HAS), H-M3 (CAT), H-M4 (Pareto)
- Verification type: Causal analysis

**SH3 (Comparison):**
"Does BAQI outperform existing unidirectional baselines on predicting user outcomes?"
- Maps to: Secondary predictions
- Baselines: RLHF-only, HumanAgencyBench-only, User-satisfaction-only, Simple-average
- Verification type: Comparative empirical

**Total sub-hypotheses:** 2 + 4 = **6 sub-hypotheses**

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-BAQI-v1
- [x] Confidence level: 0.80
- [x] Alternative hypothesis (H0) defined
- [x] All 7 variables operationalized with evidence
- [x] Causal mechanism: 4 steps with evidence table
- [x] Key tension identified with resolution
- [x] 4 key assumptions with consequences
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria defined
- [x] 4 baselines identified
- [x] SH1, SH2, SH3 clear starting points

### Open Questions

1. **Resource Requirements:** LLM-as-judge compute, 100+ multi-turn dialogues needed, user study recruitment
2. **Data Availability:** HumanAgencyBench test cases available; need new dialogues with labels
3. **Technical Feasibility:** LLM-as-judge calibration, Pareto computation complexity
4. **Priority Order:** H-M2 (HAS reliability) → SH1 (Overall reliability) → H-M3 (CAT) → SH3 (Baselines)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (7 sources with citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
