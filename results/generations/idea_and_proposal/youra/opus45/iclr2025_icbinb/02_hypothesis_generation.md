# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-MLHFACS-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under conditions of systematic ML failure documentation with trained raters, if aviation HFACS taxonomy principles are adapted to ML domain (ML-HFACS with 4-level hierarchy and 24 categories), then inter-rater reliability Cohen's κ > 0.7 will be achieved, because hierarchical failure classification is domain-invariant and HFACS has been successfully transferred to healthcare, maritime, and nuclear domains.

**Alternative Hypothesis (H0):**
ML failures do not follow hierarchical causality patterns similar to aviation, and therefore HFACS adaptation will fail to achieve acceptable inter-rater reliability (Cohen's κ ≤ 0.7), indicating that ML failures are fundamentally different from other sociotechnical system failures.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| ML-HFACS taxonomy | Independent | 4-level hierarchy with 24 categories adapted from aviation HFACS | Categorical: Level 1-4 |
| De-identification framework | Independent | Differential privacy ε=1.0 + k-anonymity k=5 | Binary: Applied/Not |
| Failure source | Independent | Industry (n=50) vs Public (n=50) | Categorical |
| Inter-rater reliability | Dependent | Cohen's κ from 3 raters on 30 failures | κ: -1.0 to 1.0, target > 0.7 |
| Taxonomy coverage | Dependent | % of 100 failures classifiable | 0-100%, target > 95% |
| Predictive association | Dependent | Correlation: Level 1-2 factors ↔ deployment failures | 0-1.0, target > 0.7 |
| Rater training | Controlled | Standardized 4-hour training protocol | Fixed: 4 hours |
| Failure documentation quality | Controlled | Minimum 500-word structured report | Fixed: ≥500 words |

### 1.3 Causal Mechanism

**4-Step Causal Chain (N=4):**

```
Step 1: Aviation HFACS → ML-HFACS Adaptation
    ↓
Step 2: ML-HFACS + Training → Rater Competence
    ↓
Step 3: Rater Competence + Reports → Inter-rater Reliability (κ > 0.7)
    ↓
Step 4: Validated Taxonomy + 100 Failures → Predictive Utility Demonstration
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | Vempati 2023 (HFACS/ASRS) | HFACS classifies 53% perceptual, 32% decision errors | Strong |
| Step2 → Step3 | Cohen's κ literature | κ > 0.7 = substantial agreement threshold | Strong |
| Step3 → Step4 | Tiwari 2023 (Near-miss) | Near-miss reporting enables incident prediction | Medium |
| Step4 → Outcome | McGreivy 2024 | 79% weak baselines; failure docs address gap | Strong |

**Key Tension:**
- **Tension:** HFACS works for aviation with FAA regulatory pressure, but ML has no equivalent enforcement. 79% of ML papers use weak baselines (cultural barrier).
- **Resolution:** Test whether voluntary participation with academic credit can substitute for regulatory enforcement. Fallback: public sources.

### 1.4 Key Assumptions

1. **Aviation-ML Transferability** (Critical)
   - HFACS hierarchy applies to ML sociotechnical systems
   - *If Violated:* Taxonomy categories won't map; adds 6+ months for redesign

2. **Industry Participation** (High Risk)
   - 5-10 companies share 50 anonymized failures
   - *If Violated:* Increase public sources to 80-100; delays 3-6 months

3. **Public Source Availability** (Medium Risk)
   - 50 failures from ICBINB papers, blogs, post-mortems
   - *If Violated:* Reduce sample to 70-80; affects statistical power

4. **Taxonomy Learnability** (Medium Risk)
   - 4-hour training sufficient for κ > 0.7
   - *If Violated:* Extend training to 8 hours; add practice cases

5. **De-identification Adequacy** (Technical Risk)
   - DP ε=1.0 + k-anonymity k=5 protects IP
   - *If Violated:* Industry withdraws; rely on public sources only

### 1.5 Scope & Boundaries

**Applies To:**
- ML/DL deployment failures with sufficient documentation (≥500 words)
- English-language reports; US/Europe industry focus
- Sectors: MLOps, healthcare AI, autonomous systems, recommendations

**Does NOT Apply To:**
- Hardware failures, pure algorithmic research failures
- Non-English documentation, regulatory compliance failures

**Limitations:**
- 100 failures may not capture full diversity
- Industry selection bias; temporal snapshot; no causal claims

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Inter-rater Reliability):**
3 independent ML practitioners classifying 30 failures using ML-HFACS after 4-hour training will achieve Cohen's κ > 0.7.

*Measurement:* κ pairwise + Fleiss' κ, p < 0.05
*Success:* κ > 0.7 | *Acceptable:* κ > 0.6 | *Falsification:* κ ≤ 0.4

**Secondary Predictions:**

**P2 (Coverage):** >95% of 100 failures classifiable (≤5% "Other")
**P3 (Source Invariance):** κ_industry ≈ κ_public (no significant difference)
**P4 (Predictive Association):** >70% deployment failures contain Level 1-2 factors
**P5 (De-identification):** 0% source identification by security reviewers

**Falsification Criteria:**

1. **Primary Failure:** κ ≤ 0.4 → ML failures fundamentally different
2. **Taxonomy Failure:** >20% unclassifiable → categories inadequate
3. **Mechanism Failure:** No Level 1-2 association → hierarchy doesn't apply

### 1.7 SOTA Baseline (Optional)

**Not Applicable** - Taxonomy validation project. No existing validated ML failure taxonomy for comparison.

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 30 failures for reliability study (standard for κ estimation)
**Power:** 0.80 | **α:** 0.05

**Tests:**
- Primary: Cohen's κ (pairwise) + Fleiss' κ (multi-rater)
- Coverage: Binomial test for >95%
- Source comparison: Independent samples t-test
- Association: Chi-square for Level 1-2 presence

**Report Format:** κ with 95% CI, effect sizes, p-values, confusion matrices

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does a validated hierarchical taxonomy for ML failures exist that achieves inter-rater reliability κ > 0.7?"
- Maps to: P1 (Primary prediction)
- Type: Empirical | Critical: MUST PASS

**SH2 (Mechanism):**
"Is HFACS adaptation the cause of reliable ML failure classification?"
- Maps to: Causal mechanism (N=4 steps)
- Decomposes to: H-M1 (Adaptation), H-M2 (Training), H-M3 (Reliability), H-M4 (Utility)
- Type: Causal analysis

**SH3 (Comparison):**
"Does ML-HFACS provide value over ad-hoc classification?"
- Maps to: P2, P3
- Type: Comparative empirical

**Total: 6 sub-hypotheses** (2 + N where N=4)

### Readiness Checklist

- [x] "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-MLHFACS-v1
- [x] Confidence: 0.78
- [x] H0 defined
- [x] Variables operationalized with evidence
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 5 testable predictions (P1 primary)
- [x] 3 falsification criteria
- [x] Baselines identified
- [x] SH1/SH2/SH3 ready

### Open Questions

1. **Industry Partnership:** Timeline for recruiting 5-10 partners? Preliminary outreach needed.
2. **IRB Requirements:** Human subjects protocol for rater study?
3. **Taxonomy Granularity:** Exactly 24 categories or domain-specific expansion?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
