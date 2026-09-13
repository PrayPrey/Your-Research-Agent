# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PCAF-v1
**Confidence Level:** 0.81 (High)

**Main Hypothesis:**
Under the condition of deploying DP-trained ML models in GDPR-regulated jurisdictions, if we apply Privacy Compliance Indicators (PCIs) that map ε/δ parameters to GDPR principles (data minimization, purpose limitation, storage limitation), then organizations can construct auditable compliance arguments with quantified uncertainty, because PCIs operationalize the qualitative-to-quantitative translation through information-theoretic bounds validated by regulatory decomposition methodology.

**Alternative Hypothesis (H0):**
There is no systematic relationship between differential privacy parameters (ε/δ) and GDPR compliance; any compliance argumentation must rely on ad-hoc expert judgment without formal quantitative grounding, and formal PCIs provide no additional value over informal ε recommendations.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| ε (epsilon) | Independent | Privacy budget parameter from DP-SGD (Abadi 2016) | ε ∈ [0.1, 10]; practical range [1, 8] for LLMs (Li 2021) |
| δ (delta) | Independent | Failure probability bound from DP | δ < 1/n for n training samples; typically 10⁻⁵ |
| data_sensitivity_level | Independent | Categorical based on GDPR Article 9 | Low (public) / Medium (business) / High (PII/special categories) |
| PCI_score | Dependent | Normalized compliance indicator derived from ε via information gain bounds | [0, 1] where higher = better compliance alignment |
| threshold_recommendation | Dependent | Confidence interval for compliance alignment | [ε_min, ε_max] with 95% CI; e.g., [0.5, 2.0] for Medium sensitivity |
| jurisdiction | Controlled | Regulatory framework | GDPR (EU) only; excludes CCPA, LGPD |
| use_case_category | Controlled | ML model deployment categories | Training / Inference / Fine-tuning |

### 1.3 Causal Mechanism

**5-Step Causal Chain (N=5):**

```
ε/δ Parameters → Information Gain Bounds → PCIs → Threshold Recommendations → Compliance Arguments → Expert Validation
```

**Step 1: ε/δ → Information Gain Bounds**
- *Mechanism*: Differential privacy guarantees bound the information any adversary can gain about individual records. ε directly controls the log-likelihood ratio bound.
- *Evidence*: Abadi 2016 moments accountant, Mironov RDP formalization
- *Falsification*: If ε values within recommended range still permit significant privacy attacks

**Step 2: Information Gain Bounds → Privacy Compliance Indicators (PCIs)**
- *Mechanism*: Translate information-theoretic bounds into GDPR-aligned metrics
  - PCI-DM: Maps ε to data minimization (information gain ≤ threshold)
  - PCI-PL: Maps inference attack success probability to purpose limitation
  - PCI-SL: Maps temporal ε accumulation to storage limitation risk
- *Evidence*: Novel contribution inspired by Buscemi 2025 legal→technical decomposition methodology
- *Falsification*: If GDPR principles fundamentally resist quantification

**Step 3: PCIs → Threshold Recommendations with Confidence Intervals**
- *Mechanism*: Aggregate PCI scores with sensitivity-level context to produce ε ranges rather than point estimates. 3 profiles: Low/Medium/High sensitivity.
- *Evidence*: NIST SP 800-226 evaluation guidelines, Li 2021 practical ε ranges for LLMs
- *Falsification*: If context-dependency is too high for pre-configured profiles

**Step 4: Threshold Recommendations → Structured Compliance Arguments**
- *Mechanism*: Generate formal argumentation following Buscemi 2025 methodology with explicit assumptions, limitations, and audit trails
- *Evidence*: Buscemi 2025 AI Act verification structure adaptable to GDPR
- *Falsification*: If argumentation structure does not satisfy legal standards

**Step 5: Compliance Arguments → Expert Validation & Regulatory Acceptance**
- *Mechanism*: Arguments require privacy law expert review before deployment and cross-validation against EDPB guidance
- *Evidence*: Cummings & Desai 2018 advocate DP for GDPR compliance
- *Falsification*: If expert validation is prohibitively expensive or produces irreconcilable recommendations

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| ε/δ → Info Bounds | Abadi 2016, Mironov 2017 | DP-SGD provides provable ε/δ bounds via moments accountant; RDP enables tighter composition | Strong |
| Info Bounds → PCIs | Buscemi 2025 (methodology) | Legal requirements CAN be systematically decomposed into operational sub-requirements | Medium |
| PCIs → Thresholds | NIST SP 800-226, Li 2021 | Official DP evaluation guidelines + practical ε ranges [1-8] for LLMs | Strong |
| Thresholds → Arguments | Buscemi 2025 (structure) | AI Act verification structure provides reusable template for compliance argumentation | Medium |
| Arguments → Validation | Cummings & Desai 2018 | DP advocated as preferred method for GDPR-compliant ML; formal arguments needed | Medium |

**Key Tension:**

*Tension*: Cummings & Desai (2018) advocate DP as sufficient for GDPR compliance, but Khalid (2023) demonstrates that formal privacy definitions for GDPR lack quantitative DP mapping. GDPR is intentionally principle-based (qualitative), while DP provides mathematical guarantees (quantitative).

*Resolution*: PCAF does NOT claim to provide "verification" or "certification" (overclaiming). Instead, it provides "argumentation support" with explicit uncertainty quantification. The framework acknowledges interpretive rather than definitive legal validity. Expert validation (Step 5) bridges the epistemological gap between technical and legal domains.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | If Violated |
|---|------------|---------------------|-------------|
| A1 | GDPR principles can be operationalized into measurable privacy risk metrics | Khalid 2023 provides formal privacy definitions; Buscemi 2025 demonstrates legal→technical decomposition | Framework becomes purely theoretical with no practical application |
| A2 | Regulatory enforcement patterns provide implicit threshold guidance | EDPB guidance documents, DPA enforcement decisions | Thresholds become arbitrary without empirical grounding |
| A3 | DP guarantees meaningfully correspond to regulatory intent | Cummings & Desai 2018 position paper; NIST SP 800-226 validates DP evaluation | DP becomes irrelevant to GDPR compliance; alternative technical measures needed |
| A4 | Context (sensitivity, use case) significantly affects appropriate thresholds | Li 2021 shows ε ranges vary for LLMs; GDPR Article 9 distinguishes data categories | Single-threshold approach would suffice; 3-profile system adds unnecessary complexity |

### 1.5 Scope & Boundaries

**Applies To:**
- DP-trained ML models (DP-SGD, federated learning with DP)
- GDPR-regulated jurisdictions (EU, EEA, UK GDPR)
- Model deployment scenarios: training, fine-tuning, inference
- Organizations seeking formal compliance argumentation

**Does NOT Apply To:**
- Non-DP privacy methods (homomorphic encryption alone, secure MPC without DP)
- Jurisdictions without GDPR-like principles (though methodology may transfer)
- Real-time compliance certification (PCAF is argumentation support, not certification)
- Use cases where DP is fundamentally inappropriate

**Known Limitations:**
1. **Interpretive, not definitive**: PCAF generates argumentation support, not legal certification
2. **Expert validation required**: Outputs must be reviewed by privacy law experts before regulatory use
3. **Regulatory evolution**: GDPR interpretation evolves; thresholds require periodic review
4. **Jurisdiction-specific**: EDPB guidance varies; parameterization needed for different member states

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (PCI Validity)**: If ε ≤ PCI-recommended threshold for a given sensitivity level, then the generated compliance argument will satisfy expert review criteria for regulatory sufficiency.

*Measurement*:
- Expert acceptance rate ≥ 70% for generated compliance arguments
- Argumentation completeness score ≥ 0.8 (all required elements present)
- p < 0.05 for expert rating difference vs. ad-hoc ε selection baseline

*Basis*: Domain standard for expert agreement in regulatory compliance assessments. No existing SOTA baseline (novel framework).

*Success Criteria for Phase 2B*:
- Primary: Expert acceptance rate > 70%
- Threshold calibration: 80% of recommended ε ranges align with EDPB implicit guidance

**Secondary Predictions:**

**P2 (Mechanism Validation)**: The PCI decomposition accurately reflects GDPR principle operationalization.
- PCI-DM correctly maps ε to data minimization in ≥80% of test cases
- PCI-PL correctly maps inference attack risk to purpose limitation in ≥75% of test cases
- PCI-SL correctly maps temporal ε to storage limitation risk in ≥75% of test cases

**P3 (Threshold Utility)**: Confidence intervals provide actionable guidance for practitioners.
- 90% of generated threshold recommendations are within ±1.0 of expert consensus
- 3 sensitivity profiles (Low/Medium/High) cover ≥85% of practical use cases
- Practitioner usability rating ≥ 4.0/5.0 in pilot deployment

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Expert acceptance rate < 50%
   - Indicates compliance arguments are not meeting regulatory review standards

2. **Mechanism Failure**: PCI decomposition accuracy < 60% across all 3 indicators
   - Indicates GDPR principles cannot be operationalized as proposed

3. **Threshold Failure**: ≥30% of recommended ε ranges contradict EDPB implicit guidance
   - Indicates threshold recommendation engine produces unreliable outputs

4. **Expert Disagreement**: Inter-rater reliability (Krippendorff's α) < 0.6
   - Indicates fundamental methodological issues in the framework

5. **Practical Inapplicability**: ≥50% of real-world use cases fall outside 3 sensitivity profiles
   - Indicates insufficient coverage for practical deployment

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Mode: Absolute Performance (Novel Framework)**

No existing SOTA baseline available for formal DP-to-GDPR compliance mapping frameworks. This is a novel contribution addressing Gap 1 identified in Phase 1 research.

**Comparison Baselines for Phase 2B:**
- Ad-hoc ε selection (current practice): Informal recommendations without systematic justification
- Informal compliance arguments: Natural language claims without structured evidence
- No formal mapping (status quo): Organizations deploy DP without GDPR-specific analysis

*PCAF will be evaluated against these baselines on expert acceptance rate and argumentation completeness.*

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Primary metric: Expert acceptance rate
- Expected effect: 70% acceptance vs. 40% baseline (ad-hoc)
- Power analysis: n ≥ 30 compliance argument evaluations
- Expert panel: Minimum 3 privacy law experts with GDPR specialization

**Test Specifications:**
| Metric | Test | Threshold | Significance |
|--------|------|-----------|--------------|
| Expert acceptance rate | One-sample proportion test | ≥70% | p < 0.05 |
| PCI decomposition accuracy | Chi-square goodness-of-fit | ≥75% | p < 0.05 |
| Threshold calibration | Agreement analysis vs. EDPB | ≥80% alignment | Cohen's κ > 0.6 |
| Expert inter-rater reliability | Krippendorff's alpha | α > 0.6 | - |

**Report Format:**
- Mean acceptance rate with 95% CI
- Per-PCI accuracy breakdown
- Threshold recommendation distribution
- Qualitative expert feedback summary

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Do Privacy Compliance Indicators (PCIs) produce measurable compliance scores that correlate with expert assessments of GDPR alignment?"
- Maps to: Primary prediction (expert acceptance rate ≥70%)
- Verification type: Empirical validation with expert panel
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism) - 5 Sub-hypotheses:**
"Is the 5-step causal chain the actual mechanism producing compliance argumentation?"

Phase 2B will decompose this into:
- **H-M1**: ε/δ → Information gain bounds (Abadi/Mironov foundation)
- **H-M2**: Information bounds → PCIs (novel PCI decomposition)
- **H-M3**: PCIs → Threshold recommendations (NIST/Li validation)
- **H-M4**: Thresholds → Compliance arguments (Buscemi methodology)
- **H-M5**: Arguments → Expert validation acceptance

Verification type: Causal analysis with step-by-step validation
Critical: Determines explanatory power of PCAF

**SH3 (Comparison):**
"Does PCAF outperform ad-hoc ε selection and informal compliance arguments on expert acceptance rate and argumentation completeness?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical (vs. baselines)
- Critical: Determines practical value over status quo

**Total Sub-hypotheses for Phase 2B: 7** (1 + 5 + 1)

### Readiness Checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Hypothesis in "Under [C], if [X], then [Y] because [Z]" format | ✅ Complete |
| 2 | Hypothesis ID assigned | ✅ H-PCAF-v1 |
| 3 | Confidence level specified | ✅ 0.81 |
| 4 | Alternative hypothesis (H0) defined | ✅ Complete |
| 5 | All variables have operationalization from evidence | ✅ 7 variables with ranges |
| 6 | Causal mechanism has evidence at each step | ✅ 5 steps with evidence table |
| 7 | Causal chain length (N) determined | ✅ N=5 |
| 8 | Key tension identified with resolution | ✅ Cummings vs Khalid resolved |
| 9 | Key assumptions list consequences if violated | ✅ 4 assumptions with consequences |
| 10 | At least 2 testable predictions exist | ✅ P1 (primary), P2, P3 |
| 11 | Falsification criteria defined | ✅ 5 rejection conditions |
| 12 | Baselines identified for comparison | ✅ Ad-hoc, informal, status quo |
| 13 | SH1, SH2, SH3 clear starting points | ✅ Generated with N=5 |

**All 13 checklist items verified ✅**

### Open Questions

1. **Expert Panel Composition**: How many privacy law experts with GDPR specialization are needed for validation? Minimum 3 recommended, but optimal panel size and selection criteria require Phase 2B specification.

2. **PCI Mathematical Formalization**: What exact mathematical functions will translate ε values to PCI scores? Current evidence provides conceptual framework (information gain bounds) but formal equations need derivation.

3. **Threshold Calibration Data Source**: How will EDPB guidance be systematically analyzed to extract implicit thresholds? DPA enforcement decision corpus needs identification and accessibility assessment.

4. **Priority Verification Order**: Should SH1 (existence) be fully validated before SH2 (mechanism) testing begins? Or can mechanism validation proceed in parallel? Recommend sequential: SH1 → SH2 → SH3.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
