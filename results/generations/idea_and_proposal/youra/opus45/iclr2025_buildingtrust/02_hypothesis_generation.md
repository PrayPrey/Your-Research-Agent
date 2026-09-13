# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (TrustFrontier - Round 1)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TrustFrontier-v1
**Confidence Level:** 0.83

**Main Hypothesis:**
Under the condition of multi-dimensional LLM evaluation requirements, if Pareto-based Multi-Attribute Utility aggregation (TrustFrontier) is applied to trustworthiness dimensions, then practitioners can identify optimal trade-off configurations and actionable improvement paths, because non-additive aggregation captures dimension interactions while Pareto analysis reveals configurations where no dimension improves without degrading another.

**Alternative Hypothesis (H0):**
Standard weighted-average aggregation of trustworthiness dimensions provides equivalent decision-making utility to Pareto-based MAUT, with no additional benefit from explicit trade-off analysis or non-additive aggregation.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Trustworthiness dimensions | Independent | 7 dimensions from Liu 2023 taxonomy: reliability, safety, fairness, robustness, explainability, social norms, misuse resistance - measured via TrustLLM/DecodingTrust benchmarks | 7 dimensions, raw scores vary by metric type |
| Aggregation method | Independent | Choquet integral with fuzzy measures vs. weighted average baseline | Binary: TrustFrontier vs. Baseline |
| Domain preference profile | Independent | Healthcare (safety-first), Finance (fairness-first), General (balanced) - pre-defined weight vectors | 3 profiles with different priority orderings |
| Unified trustworthiness score | Dependent | Choquet integral output normalized to interpretable scale | [0, 1] where 1 = fully trustworthy |
| Pareto frontier position | Dependent | Euclidean distance to computed Pareto frontier | [0, ∞) where 0 = Pareto optimal |
| Improvement recommendations | Dependent | Ranked list of dimension improvements with expected utility gain | Ordered list with quantified gains |
| Benchmark data sources | Controlled | Fixed to TrustLLM (6 dimensions) and DecodingTrust benchmarks | Constant across experiments |

### 1.3 Causal Mechanism

**Causal Chain (4 Steps):**

```
Step 1: Raw Benchmark Scores → Normalized Utility Values
        (Utility function transformation)
              ↓
Step 2: Normalized Utilities + Fuzzy Measures → Aggregated Score
        (Choquet integral non-additive aggregation)
              ↓
Step 3: Aggregated Utilities Across Models → Pareto Frontier
        (Multi-objective optimization computation)
              ↓
Step 4: Pareto Frontier + Model Position → Actionable Recommendations
        (Distance analysis and improvement path generation)
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Bias and Fairness Survey (926 citations) | Metrics can operate at embedding, probability, and text levels with normalization | Strong |
| Step 2 → Step 3 | Trustworthy LLMs Survey (487 citations) | Alignment effectiveness varies across dimensions, indicating interactions exist | Strong |
| Step 3 → Step 4 | MAUT/Pareto literature (cross-domain) | Pareto frontiers enable identification of non-dominated solutions | Strong |
| Step 4 → Outcome | TrustLLM benchmark (Huang 2024) | Unified evaluation enables comparative analysis across 16 models | Medium |

**Key Tension:**
- **Tension:** Liu 2023 identifies 7 dimensions with 29 sub-categories, but TrustLLM benchmark only covers 6 dimensions empirically. Explainability dimension has weakest benchmark coverage.
- **Resolution:** This verification plan will use proxy metrics from XAI literature (SHAP faithfulness, attention entropy) for explainability, with explicit validation of proxy meaningfulness.

### 1.4 Key Assumptions

1. **Benchmark Coverage Assumption:** Existing benchmarks (TrustLLM, DecodingTrust) provide sufficient coverage of all 7 trustworthiness dimensions.
   - Evidence: TrustLLM covers 6/7 dimensions across 30+ datasets
   - *Consequence if violated:* Framework would have blind spots for uncovered dimensions; would need to develop new benchmarks

2. **Proxy Metric Validity Assumption:** Proxy metrics from XAI literature (SHAP faithfulness, attention entropy) can meaningfully represent explainability utility.
   - Evidence: EvalxNLP framework (2025) evaluates 8 XAI techniques for faithfulness and plausibility
   - *Consequence if violated:* Explainability dimension would be unreliable; may need human evaluation as fallback

3. **Interdependency Stability Assumption:** Dimension interdependencies are stable within model families (base, instruction-tuned, RLHF) and can be learned from benchmark data.
   - Evidence: Trustworthy LLMs Survey shows alignment affects dimensions differently, suggesting learnable patterns
   - *Consequence if violated:* Would need model-family-specific Choquet parameters or abandon non-additive aggregation

4. **Preference Consistency Assumption:** Stakeholder preferences within domains (healthcare, finance) are consistent enough for pre-defined profiles.
   - Evidence: Aegis2.0 safety taxonomy shows domain-specific risk categorizations exist
   - *Consequence if violated:* Would need per-organization preference elicitation rather than domain profiles

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Production LLMs with benchmark coverage (GPT-4, Claude, Llama, Mistral families)
- Deployment contexts requiring multi-dimensional trust assessment
- Organizations needing explicit trade-off documentation (regulated industries)
- Comparative evaluation of multiple candidate models

**Where It Does NOT Apply:**
- Single-dimension evaluation needs (pure safety or pure fairness focus)
- Models without existing benchmark evaluations (requires benchmark data as input)
- Real-time evaluation during inference (framework is for offline comparative analysis)
- Domains with no established preference profiles (would require custom elicitation)

**Known Limitations:**
- Choquet integral adds computational complexity vs. weighted average
- High-dimensional Pareto visualization (7D) requires dimensionality reduction
- Framework effectiveness depends on benchmark quality and coverage
- Pre-defined domain profiles may not match specific organizational needs

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Trade-off Visibility):**
TrustFrontier reveals dimension trade-offs that are invisible to single-dimension benchmarks and weighted-average aggregation.

*Measurement:*
- Metric: Number of non-dominated configurations identified on Pareto frontier
- Success: ≥3 distinct Pareto-optimal configurations per model family
- Statistical test: Chi-square test for frontier diversity vs. single-point weighted average, p < 0.05

*Basis:*
Multi-objective optimization theory guarantees Pareto frontiers reveal trade-offs when objectives conflict. Evidence from Trustworthy LLMs Survey suggests dimension conflicts exist (safety vs. utility).

*Success Criteria for Phase 2B:*
- Primary: Pareto frontier contains ≥3 non-dominated solutions per model family
- Falsification: If all models collapse to single point (no trade-offs visible), hypothesis fails

**Secondary Predictions:**

**P2 (Actionable Improvement Paths):**
For models below the Pareto frontier, TrustFrontier generates improvement recommendations that, if followed, move the model closer to the frontier without degrading other dimensions.

*Measurement:*
- Metric: Percentage of recommendations that correctly identify improvable dimensions
- Success: ≥80% recommendation accuracy validated by dimension-specific re-evaluation
- Statistical test: Binomial test against 50% random baseline, p < 0.05

**P3 (Domain-Specific Ranking Divergence):**
When different domain profiles (healthcare vs. finance) are applied, model rankings change meaningfully, demonstrating profile utility.

*Measurement:*
- Metric: Kendall's tau correlation between healthcare and finance rankings
- Success: τ < 0.7 (indicating meaningful divergence, not identical rankings)
- Statistical test: Kendall's tau with confidence interval

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure (Trade-off Invisibility):** Pareto frontier collapses to single point for all model families, indicating no meaningful trade-offs exist between trustworthiness dimensions.

2. **Mechanism Failure (Aggregation Equivalence):** Choquet integral produces rankings statistically indistinguishable from simple weighted average (Kendall's tau > 0.95 with weighted average baseline).

3. **Practical Failure (Recommendation Inutility):** Improvement recommendations achieve <50% accuracy (no better than random), indicating actionable diagnostics provide no value.

### 1.7 SOTA Baseline (Not Applicable)

*This hypothesis targets framework development, not performance improvement over existing methods.*

**Comparison Baselines:**
- TrustVis (Sun 2025): Multi-dimensional visualization without Pareto analysis
- TrustLLM weighted average: Simple aggregation baseline
- Single-dimension benchmarks: Dimension-specific evaluations

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Models evaluated: Minimum 16 models (following TrustLLM coverage)
- Model families: 4 families (GPT, Claude, Llama, Mistral) × 4 variants each
- Runs per model: 3 benchmark runs for stability assessment

**Test Specifications:**
- P1 (Frontier diversity): Chi-square test, α = 0.05
- P2 (Recommendation accuracy): Binomial test, α = 0.05, power = 0.8
- P3 (Ranking divergence): Kendall's tau with 95% CI

**Report Format:**
- Effect sizes with confidence intervals
- Visualization: Parallel coordinates for Pareto frontier, heatmaps for correlations
- Sensitivity analysis for Choquet parameter variations

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can heterogeneous LLM trustworthiness metrics be meaningfully normalized into comparable utility scales using domain-appropriate transformation functions?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical validation with expert evaluation
- Critical: MUST PASS - if normalization fails, entire framework fails

**SH2 (Mechanism):**
"Does the proposed 4-step causal mechanism (normalization → aggregation → Pareto computation → recommendations) operate as theorized?"
- Maps to: Causal mechanism (4 steps)
- Phase 2B will decompose into 4 sub-hypotheses:
  - H-M1: Utility normalization preserves dimension semantics
  - H-M2: Choquet integral captures meaningful interactions
  - H-M3: Pareto computation yields diverse frontier
  - H-M4: Recommendations align with ground-truth improvements
- Verification type: Causal analysis with ablation studies

**SH3 (Comparison):**
"Does TrustFrontier provide decision-making utility beyond weighted-average aggregation and single-dimension benchmarks?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical evaluation
- Critical: Determines practical value of the framework

**Total sub-hypotheses in Phase 2B:** 6 (SH1 + 4×SH2 + SH3)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-TrustFrontier-v1
- [x] Confidence level specified: 0.83
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (4 steps, evidence table complete)
- [x] Causal chain length determined: N = 4
- [x] Key tension identified and resolution proposed (explainability coverage)
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (3 predictions with P1 marked primary)
- [x] Falsification criteria defined (3 failure conditions)
- [x] Baselines identified: TrustVis, weighted average, single-dimension benchmarks
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B

### Open Questions

1. **Data Availability:** Do TrustLLM and DecodingTrust provide raw per-dimension scores (not just aggregated), and are they accessible for the target 16+ models?

2. **Choquet Parameter Learning:** What is the minimum number of models needed to reliably learn fuzzy measure parameters for the Choquet integral?

3. **Validation Protocol:** How will we validate that improvement recommendations are "correct" without actually retraining models? (Proposed: expert panel evaluation or ablation proxy)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
