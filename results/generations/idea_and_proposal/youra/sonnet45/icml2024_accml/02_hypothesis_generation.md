# Phase 2A Extended: Hypothesis Clarification - Summary

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** Round 1 (02a_round_1_discussion.md)
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

**Hypothesis ID:** H-2A-ext-1 (BioLoop-MVB)
**Confidence Level:** High (85%)

**Main Hypothesis:**
A standardized benchmark framework applying clinical trials endpoint methodology (primary/secondary/composite metrics) to lab-in-the-loop protein engineering will enable reproducible comparison of experimental feedback integration strategies, thereby accelerating adoption of iterative ML-experiment systems in biology.

**Core Innovation:**
First standardized benchmark for lab-in-the-loop biological ML that borrows clinical trials' validated endpoint framework (primary: functional hit rate, secondary: diversity & cost, composite: efficiency score) and applies it to protein thermal stability prediction with simulated experimental oracle.

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Main Hypothesis:**
A standardized benchmark framework applying clinical trials endpoint methodology (primary/secondary/composite metrics) to lab-in-the-loop protein engineering will enable reproducible comparison of experimental feedback integration strategies, thereby accelerating adoption of iterative ML-experiment systems in biology.

**Alternative Hypothesis (H0):**
Existing custom evaluation methods are sufficient for comparing lab-in-the-loop feedback strategies; a standardized benchmark framework will not significantly improve reproducibility or adoption of iterative ML-experiment systems.

### 1.2 Key Variables

| Variable Type | Name | Measurement |
|---------------|------|-------------|
| **Independent** | Feedback Integration Strategy | Categorical: likelihood reintegration, Bayesian optimization, active learning |
| **Dependent (Primary)** | Functional Hit Rate | Continuous: % designs with ΔTm > +5°C |
| **Dependent (Composite)** | Experimental Efficiency Score | Continuous: (Hit Rate × Diversity) / Cost |
| **Control** | Experimental Budget | Fixed: 50 oracle queries |

### 1.3 Testable Predictions

**Primary Prediction (P1):**
Feedback strategies will demonstrate measurably different experimental efficiency scores, with at least one method achieving >30% higher efficiency than random baseline (p < 0.05).

**Secondary Predictions:**
- **P2:** Independent teams will replicate baseline methods within ±5% functional hit rate (inter-lab CV < 10%)
- **P3:** Simulated oracle will correlate r > 0.7 with published experimental results (validation: 20 papers)
- **P4:** Method ranking will remain consistent across ≥70% of protein families (Kendall's W > 0.7)

**Falsification Criteria:**
- **Critical Failure:** Oracle correlation r < 0.5 OR no method differentiation (p > 0.05, ANOVA) OR inter-lab CV > 25%

---

## 2. Contribution Summary

**Theoretical:** Establishes endpoint-based evaluation framework for iterative ML-experiment systems, adapting clinical trials methodology to biological AI context.

**Methodological:**
- Simulated oracle approach enables reproducible comparison without wet-lab dependency
- Endpoint framework translation (functional hit rate = responder rate, diversity = safety, cost = burden)
- MVP benchmark philosophy (single-task validation before expansion)

**Practical:**
- Provides biologists evidence-based guidance on feedback method selection
- Extensibility template for RNA/CRISPR/drug discovery benchmarks
- Cost reduction: simulated evaluation during method development phase

**Workshop Alignment:** Directly addresses ICML 2024 "lab-in-the-loop iterative approaches" theme by providing standardized evaluation infrastructure.

---

## 3. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): Simulated Oracle Validity**
ProTherm/FireProtDB can serve as accurate simulated oracle (r > 0.7 with published experiments).

**SH2 (Mechanism): Endpoint Framework Discriminative Power**
Clinical trials-inspired metrics can statistically differentiate feedback strategies (p < 0.05, ANOVA).

**SH3 (Comparison): Reproducibility & Adoption**
Standardized protocol enables independent replication (CV < 10%) and measurable adoption (≥3 external teams within 1 year).

### Readiness Checklist

- ✅ Hypothesis is narrow and specific (protein thermal stability, endpoint metrics defined)
- ✅ Variables are measurable (functional hit rate %, efficiency score, oracle fidelity r)
- ✅ Causal mechanism is explicit (6-link chain: Framework → Adoption)
- ✅ Key assumptions identified & testable (5 assumptions: A1-A5)
- ✅ Scope is bounded (in/out scope, boundary conditions specified)
- ✅ Testable predictions are concrete (4 predictions with quantitative thresholds)
- ✅ Falsification criteria defined (critical failures for rejection)
- ✅ Statistical design appropriate (repeated measures + ANOVA, N=10 families)
- ✅ Related work mapped (9 key papers across 4 categories)
- ✅ Sub-hypotheses preview provided (SH1-SH3 with success criteria)

### Open Questions

1. **Q1:** Exact baseline method hyperparameters (resolution: Phase 4 sensitivity analysis)
2. **Q2:** Oracle validation set selection criteria (resolution: Phase 3 PRD systematic review)
3. **Q3:** Extensibility template design requirements (resolution: Phase 2B task decomposition)
4. **Q4:** Community adoption threshold realism (resolution: Phase 2B measurement protocol)
5. **Q5:** Oracle validation sample size (N=20 sufficient?) (resolution: Phase 3 power analysis)

**Status:** ✅ **READY FOR PHASE 2B VERIFICATION PLANNING**

---

## 4. Implementation Scope

**In Scope:**
- Protein thermal stability prediction (ΔTm) - single task MVP
- 3 baseline feedback methods + random control
- Simulated oracle (ProTherm/FireProtDB)
- Endpoint metrics (primary/secondary/composite)
- Oracle validation study (20 published papers)
- Extensibility template

**Out of Scope:**
- Real wet-lab experiments (validation uses published data only)
- Multi-task benchmark (deferred to post-MVP)
- End-to-end wet-lab automation
- Non-protein domains (RNA/CRISPR are extension pathways)

**Boundary Conditions:**
- Experimental budget: 50 oracle queries
- Initial pool: 1000 sequences (stratified by ΔTm)
- Evaluation horizon: 10 rounds × 5 queries/round
- Oracle acceptance threshold: r > 0.7

---

## 5. Key Related Work

**Lab-in-the-Loop Methods:**
- Calvanese et al. (2025): Likelihood reintegration (6.7%→63.7% improvement) - baseline method
- Drug delivery (2025): Bayesian optimization - baseline method
- CA-SMART (2025): Active learning - baseline method

**Benchmark Methodology:**
- Clinical Trials (FDA): Source of endpoint framework
- ImageNet/GLUE: Benchmark impact pattern

**Protein Engineering:**
- ProTherm, FireProtDB: Oracle data sources

**Workshop Context:**
- PEFT for genomics (Berman et al., 2025): Efficient models complement efficient evaluation
- CytoDINO (Muminov & Pham, 2025): Consumer GPU accessibility

**Differentiation:** First standardized lab-in-the-loop benchmark combining clinical trials methodology + simulated oracle + multi-method comparison.

---

*Generated using YouRA Phase 2A Extended Workflow (YOLO MODE - BATCH)*
*2026-02-08*
*See 02a_extended_hypothesis_full.md for complete documentation*
