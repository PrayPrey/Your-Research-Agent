# Phase 2A Extended: Hypothesis Summary for Phase 2B

**Date:** 2026-02-06
**Author:** Pray
**Hypothesis ID:** H-FL-FAIRPRIV-001
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Executive Summary

**Main Hypothesis:**
Federated learning systems exhibit a Pareto-efficient fairness-privacy tradeoff characterized by a frontier F(ε, δ), and practitioners can select context-appropriate operating points through regulatory-validated scalarization weights α that translate legal requirements (GDPR, AI Act, HIPAA, fair lending laws) into quantitative optimization objectives.

**Confidence Level:** 0.90 (High)

**Target Gap:** Gap 1 - Fairness-Privacy Tradeoff Optimization in Federated Learning

---

## Core Research Variables

| Variable Type | Key Variables | Range/Values |
|--------------|---------------|--------------|
| **Independent** | Privacy Budget (ε), Scalarization Weight (α), Fairness Metric Type | ε ∈ [0.1, 10], α ∈ [0, 1], {DP, EO, EqOpp} |
| **Dependent** | Model Accuracy, Fairness Violation (δ), Privacy Leakage | Continuous metrics |
| **Controlled** | Dataset, Client Distribution, Model Architecture | {FEMNIST, CelebA, Adult Income}, Clients: 10-100, Non-IID levels |

---

## Testable Predictions

**P1. Pareto Frontier Existence:**
- Negative correlation ρ(ε, δ) < -0.7 across all datasets
- No interior points dominate frontier points (Pareto optimality)

**P2. Scalarization Weight Impact:**
- Spearman correlation ρ_s(α, selected_ε) > 0.8
- Regulatory contexts select appropriate frontier regions (EU GDPR: low ε, US Fair Lending: low δ)

**P3. Baseline Superiority:**
- Pareto framework achieves lower combined loss than single-objective baselines (PPFL, Fair FL) at α = 0.5

**Falsification Criteria:**
- If ρ(ε, δ) > -0.3 → No Pareto tradeoff
- If baselines Pareto-dominate our framework → Optimization failed
- If legal experts reject weight calibration → Regulatory alignment invalid

---

## Sub-Hypothesis Decomposition (Phase 2B Preview)

**SH1 (Existence):** Pareto frontier F(ε, δ) exists with ρ(ε, δ) < -0.7 and Pareto dominance properties
- **Verification:** ε-constraint frontier computation on 3 datasets × 3 fairness metrics
- **Effort:** 2-3 weeks

**SH2 (Mechanism):** Scalarization weight α systematically shifts operating point selection (ρ_s > 0.8)
- **Verification:** α-sweep training {0.1, 0.3, 0.5, 0.7, 0.9}
- **Effort:** 1-2 weeks
- **Dependency:** Requires SH1

**SH3 (Comparison):** Pareto framework Pareto-dominates single-objective baselines
- **Verification:** Paired t-test on combined loss vs PPFL and Fair FL
- **Effort:** 2-3 weeks
- **Dependency:** Requires SH1, SH2

**SH4 (Legal Validation):** Legal experts validate regulatory weight calibration (≥2/3 agreement)
- **Verification:** Semi-structured interviews with GDPR, HIPAA, Fair Lending specialists
- **Effort:** 3-4 weeks
- **Dependency:** Requires SH2

**SH5 (Case Studies):** Framework receives compliance approval for 3 real-world scenarios (≥2/3)
- **Verification:** EU AI Act healthcare, US HIPAA, US Fair Lending case studies
- **Effort:** 4-6 weeks
- **Dependency:** Requires SH1-SH4

---

## Three Core Contributions

### 1. Theoretical: Pareto Formalization
**What:** First formalization of fairness-privacy tradeoff as Pareto bi-objective optimization in FL
**Gap:** Chen et al. 2023 documented tension; no prior work provides optimization framework
**Impact:** Shifts research from problem documentation to algorithmic solutions

### 2. Methodological: Regulatory Context Mapping
**What:** Novel legal-to-technical translation framework mapping GDPR/AI Act/HIPAA to scalarization weights
**Gap:** No existing work systematically translates regulatory requirements to optimization preferences
**Impact:** Enables justified, auditable tradeoff decisions for compliance

### 3. Practical: Compliance Tool
**What:** Open-source end-to-end tool for GDPR/AI Act compliance in FL deployments
**Gap:** Fragmented tooling (PPFL for privacy, fairness libraries for centralized ML); no integrated solution
**Impact:** Reduces deployment barriers for regulated industries (healthcare, finance)

---

## Key Related Work

**Foundation:**
- Chen et al. 2023 (75 cites): Documented fairness-privacy tension → **Our solution: Pareto optimization**

**Methodology:**
- Yin et al. 2021 (587 cites): PPFL protocols → **Our extension: FL + bi-objective optimization**
- Pareto efficiency (Economics) → **Our transfer: Fairness-privacy resource allocation**

**Legal Compliance:**
- Brauneck et al. 2023 (68 cites): GDPR + FL proof → **Our extension: Add fairness constraints**
- Deck et al. 2024: AI Act fairness interpretation → **Our operationalization: Weight calibration**

**Baselines:**
- PPFL (privacy-only): Low ε, high δ
- Fair FL (fairness-only): Low δ, high ε
- **Our framework:** Pareto-optimal (ε, δ) pairs balancing both

---

## Implementation Difficulty

**Level:** MEDIUM (3-6 months estimated)

**Technology Stack:**
- FL: TensorFlow Federated / PySyft
- Privacy: Opacus / TensorFlow Privacy
- Fairness: Fairlearn
- Optimization: SciPy + custom ε-constraint

**Complexity Drivers:**
- Bi-objective optimization + FL protocol extension
- Legal expert collaboration (not technical)
- Case study validation overhead

**Mitigations:**
- All components have open-source implementations
- Standard FL benchmarks available (FEMNIST, CelebA, Adult Income)
- ε-constraint algorithm is textbook method

---

## Phase 2B Readiness

**Status:** ✅ **95% READY**

**Complete:**
- ✅ Variables defined (independent, dependent, controlled)
- ✅ Causal mechanism specified with evidence
- ✅ Testable predictions formulated (P1, P2, P3)
- ✅ Falsification criteria established
- ✅ Statistical design complete (2,700 training runs, power > 0.99)
- ✅ Sub-hypotheses identified (SH1-SH5) with dependencies
- ✅ Baseline comparisons defined (PPFL, Fair FL, Chen et al.)
- ✅ Related work mapped (12+ key papers)
- ✅ Technology stack identified
- ✅ Assumptions explicit (A1-A5) with testability plans

**Minor Gaps:**
- ⚠️ Expert recruitment logistics (time-consuming but standard practice)
- ⚠️ Implementation effort (3-6 months) - manageable for research timeline

**Blockers:** None

**Next Phase:** Phase 2B - Verification Planning
- Decompose SH1-SH5 into detailed experiments
- Design evaluation protocols (datasets, metrics, statistical tests)
- Establish implementation roadmap with resource allocation
- Define experiment dependencies and execution order

---

## Open Questions for Phase 2B

**High Priority (Affects Legal Validation):**
- **OQ2:** Do demographic parity and equalized odds capture all legal fairness requirements? May need domain-specific metrics.
- **OQ4:** How to handle cross-jurisdictional conflicts (EU GDPR vs US Fair Lending)? Separate models or compromise operating point?

**Medium Priority (Affects Robustness):**
- **OQ3:** What if Pareto frontier is non-convex? (ε-constraint handles this; may adjust scalarization)
- **OQ5:** How stable is frontier under data distribution shift? (May need recomputation frequency analysis)

**Low Priority (Engineering Optimizations):**
- **OQ1:** Optimal grid density for frontier approximation? (20 levels vs adaptive sampling)
- **OQ6:** Computational overhead scalability? (Pareto approximation algorithms if exact computation too costly)

**Future Work:**
- **OQ7:** Incentive compatibility for FL clients? (Separate research question; out of scope)

---

## Regulatory Context Mapping (Core Innovation)

| Regulatory Context | Legal Priority | Scalarization Weight α | Expected Operating Point |
|-------------------|----------------|----------------------|------------------------|
| **EU GDPR** (strict privacy) | Privacy > Fairness | α = 0.3 | ε < 2.5, δ ≤ 0.15 |
| **US HIPAA** (healthcare privacy) | Privacy ≈ Fairness | α = 0.5 | ε ≈ 2.0, δ ≤ 0.10 |
| **US Fair Lending** (ECOA fairness) | Fairness > Privacy | α = 0.7 | ε ≤ 4.0, δ < 0.08 |

**Validation Method:** Legal expert review (SH4) + case study approval (SH5)

---

## Success Criteria Summary

**Quantitative:**
- ✅ Pareto frontier correlation ρ(ε, δ) < -0.7 on all datasets
- ✅ Scalarization impact ρ_s(α, ε) > 0.8
- ✅ Baseline superiority p < 0.025 (Bonferroni-corrected)

**Qualitative:**
- ✅ ≥2/3 legal experts validate weight calibration
- ✅ ≥2/3 case studies receive compliance approval

**Robustness:**
- ✅ Weight sensitivity: operating point stable under ±20% α variation
- ✅ Cross-dataset validation: correlation holds on all 3 datasets
- ✅ Non-IID stress test: correlation ρ(ε, δ) < -0.5 even under extreme heterogeneity

**Hypothesis PASSES if:** All quantitative + ≥1 qualitative + ≥2 robustness checks succeed

**Hypothesis FALSIFIED if:** Any falsification criterion triggered (Section above)

---

## Related Files

- **Full Hypothesis Document:** `02a_extended_hypothesis_full.md` (comprehensive 100+ page version with all details)
- **Phase 2A Round Discussion:** `02a_round_2_discussion.md` (Party Mode validation, Judge verdict: FEASIBLE 0.90)
- **Phase 2A Validated Hypotheses:** `02a_validated_hypotheses.md` (Round 2 selected as FEASIBLE)
- **Phase 1 Research Data:** `01_targeted_research.md` (35 sources: 23 Scholar + 12 Archon)
- **Phase 0 Brainstorm:** `00_brainstorm_session.md` (Research question origin)

---

**Generated:** 2026-02-06
**Workflow:** Phase 2A Extended (YOLO MODE - Batch Execution)
**Execution Time:** Fully automated (no user interaction)
**Status:** ✅ COMPLETE - Ready for Phase 2B Verification Planning

---

*This summary provides the essential information for Phase 2B planning. For complete mathematical formulations, detailed statistical designs, comprehensive related work analysis, and full assumption justifications, refer to `02a_extended_hypothesis_full.md`.*
