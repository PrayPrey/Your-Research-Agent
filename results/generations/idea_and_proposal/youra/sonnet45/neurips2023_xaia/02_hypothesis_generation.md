# Phase 2A Extended: Hypothesis Clarification Summary

**Date:** 2026-02-08
**Author:** Pray
**Hypothesis ID:** H-SAVF-001 (Stakeholder-Adaptive XAI Validation Framework)
**Status:** ✅ Ready for Phase 2B Verification Planning

---

## Core Hypothesis

**Main Hypothesis:**
A meta-learned calibration mechanism can map domain-specific XAI validation metrics (clinical expert evaluation, procedural compliance review, statistical parity tests, user comprehension assessments) to a unified multi-dimensional effectiveness profile across healthcare and fairness domains, achieving >0.7 inter-domain correlation when stakeholder types are matched (clinician-to-clinician, auditor-to-auditor), thereby enabling the first objective cross-domain XAI effectiveness comparison.

**Confidence Level:** Medium-High (70%)

**Alternative Hypothesis (H0):**
Domain-specific XAI validation metrics are incommensurable and cannot be calibrated to produce meaningful cross-domain effectiveness comparisons (inter-domain correlation <0.5).

---

## Key Variables

**Independent Variables:**
- IV1: Stakeholder Type (clinician, auditor, end-user, researcher)
- IV2: Domain (healthcare, fairness)
- IV3: XAI System (10 systems per domain: LIME, SHAP, Grad-CAM, counterfactual, etc.)

**Dependent Variables:**
- DV1: Domain-Specific Metric Score (clinical accuracy 0-100, statistical parity -1 to +1)
- DV2: Calibrated Effectiveness Profile [accuracy, trust, comprehension, fairness] (0-1)^4
- DV3: Inter-Domain Correlation (Spearman ρ, target >0.7)

**Control Variables:**
- CV1: Stakeholder Expertise (years of experience)
- CV2: XAI System Complexity (simple/medium/complex)
- CV3: Evaluation Task (standardized vignettes)

---

## Testable Predictions

**P1 (Primary):** Cross-domain correlation ≥0.7 via meta-learned calibration (vs baseline <0.3)

**P2:** Stakeholder classification accuracy ≥80%

**P3:** Within-domain validity maintained (ρ ≥0.8 vs gold standards)

**P4:** Multi-dimensional profile outperforms single-score by ≥15 percentage points

**Falsification Criteria:**
- Cross-domain ρ < 0.5 → H0 validated (domains incommensurable)
- Within-domain ρ < 0.6 → Calibration degrades validity
- No improvement over naive baseline (Δρ < 0.1) → Meta-learning adds no value

---

## Causal Mechanism

```
Stakeholder Type + Domain → Native Metric Selection
                          → Domain-Specific Score
                          → Meta-Learned Calibration
                          → Calibrated Effectiveness Profile
                          → Cross-Domain Rankings
                          → Inter-Domain Correlation
```

**Key Innovation:** Meta-learning learns stakeholder → metric preference mapping and calibration function f: (domain_metric, stakeholder_type, domain) → [accuracy, trust, comprehension, fairness]

**Key Tension:** Commensurability vs. domain-specificity trade-off resolved through multi-dimensional profile (preserves domain weights) + stakeholder matching (like-to-like comparison)

---

## Key Assumptions

**A1:** Stakeholder archetypes exist and generalize (clinician, auditor, end-user, researcher)
**A2:** XAI effectiveness is multi-dimensional (accuracy, trust, comprehension, fairness measurable in both domains)
**A3:** Meta-learning generalizes to validation metrics (not just model parameters)
**A4:** Stakeholder consensus provides valid ground truth (inter-rater reliability ≥0.7)
**A5:** 2-domain pilot generalizes to broader framework (healthcare + fairness → 6 domains)

---

## Scope & Boundaries

**Included:**
- Domains: Healthcare (medical imaging) + Fairness (algorithmic decisions)
- Stakeholders: 4 archetypes, 80 total evaluators (20 per archetype)
- XAI Systems: 20 total (10 per domain)
- Validation: Stakeholder consensus on relative system rankings

**Excluded:**
- Domains not tested: Natural science, NLP, law (future work)
- Intrinsic interpretability (only post-hoc explanations)
- Adversarial robustness, computational cost, dynamic systems

---

## Sub-Hypotheses for Phase 2B

**SH1 (Existence):** Stakeholder archetypes exist and are detectable (≥80% classification accuracy)

**SH2 (Mechanism):** Meta-learning can calibrate heterogeneous metrics (≥0.8 within-domain, ≥0.7 cross-domain)

**SH3 (Comparison):** Multi-dimensional profile outperforms single-score (Δρ ≥0.15)

**SH4 (Generalization - Optional):** Framework generalizes to NLP domain without retraining (ρ ≥0.6)

---

## Contribution Summary

**Theoretical:**
- T1: Stakeholder-type as bridging variable for cross-domain validation
- T2: Meta-learning framework for validation metric calibration (novel application)
- T3: Multi-dimensional effectiveness profile model

**Methodological:**
- M1: Stakeholder-adaptive validation protocol (automated classification + metric selection)
- M2: Cross-domain XAI validation benchmark (20 systems, 80 evaluators)
- M3: Stakeholder consensus validation approach (validation without absolute ground truth)

**Practical:**
- P1: First objective cross-domain XAI effectiveness comparison tool
- P2: Domain-specific validation preserved + cross-domain comparability added
- P3: Transferability evidence generation for new domains

---

## Key Related Work

**RW1:** Deck et al. (2023) - Critical analysis of XAI-fairness validation claims → SAVF addresses critique
**RW2:** Aoki et al. (2024) - Explanation type affects stakeholder perception → Core evidence for adaptation
**RW3:** Danilevsky et al. (2021) - NLP validation is ad-hoc → Exemplifies problem SAVF solves
**RW4:** Khade (2025) - Healthcare requires clinical assessment → Informs domain-specific metrics
**RW5:** Tjoa & Guan (2019) - Multi-stakeholder requirements → Validates archetype approach
**RW6:** Finn et al. (2017) MAML - Meta-learning foundation → Transferred to validation calibration
**RW7:** Gupta et al. (2025) - Cross-domain XAI transfer successful → Supports feasibility

---

## Statistical Design

**Sample Size:**
- 20 XAI systems (10 per domain)
- 80 stakeholder evaluators (20 per archetype)
- 800 total evaluations

**Primary Analysis:**
- Spearman rank correlation (healthcare vs fairness system rankings)
- Null: ρ = 0, Alternative: ρ > 0.5
- Significance: α = 0.05 (one-tailed)
- Target effect: ρ = 0.7 (large effect)

**Secondary Analyses:**
- Within-domain validity (calibrated vs gold standard, ρ ≥0.8)
- Stakeholder classification accuracy (≥80%)
- Multi-D vs single-score comparison (Δρ ≥0.15)
- Inter-rater reliability (ICC ≥0.7)

**Controls:**
- Stakeholder expertise (covariate)
- XAI system complexity (balanced selection)
- Evaluation task (standardized vignettes)

---

## SOTA Baseline

**Current SOTA:** Domain-specific validation only (no cross-domain comparison possible)
- Healthcare: Radiologist consensus (κ ≈ 0.7-0.9)
- Fairness: Statistical parity thresholds (SPD < 0.1)

**SAVF vs. SOTA:**
- SOTA: High within-domain validity, zero cross-domain comparability
- SAVF: Maintains within-domain (ρ ≥0.8) + enables cross-domain (ρ ≥0.7)

**Performance Targets:**
- Minimum Viable: ρ = 0.5 (moderate correlation)
- Target: ρ = 0.7 (strong correlation)
- Aspirational: ρ > 0.8 (approaching gold standard reliability)

---

## Open Questions for Phase 2B

**Q1 (HIGH):** Meta-learning architecture selection (MAML vs Prototypical Networks vs Reptile)?
**Q2 (HIGH):** How to operationalize "trust" and "comprehension" dimensions?
**Q3 (MEDIUM):** 4 archetypes vs 8 archetypes (granularity trade-off)?
**Q4 (MEDIUM):** What domain characteristics enable/prevent calibration transferability?
**Q5 (HIGH):** Is stakeholder consensus valid ground truth or confounded by biases?
**Q6 (HIGH):** 7-10 month timeline feasible given recruitment + IRB delays?
**Q7 (MEDIUM):** Should calibration function be interpretable or black-box acceptable?
**Q8 (LOW):** Negative results contingency plan (salvage strategies)?

---

## Phase 2B Readiness Checklist

✅ **Completed:**
- [x] Core hypothesis with quantitative predictions
- [x] Operationalized variables (IV, DV, CV)
- [x] Causal mechanism with evidence
- [x] Key assumptions stated
- [x] Scope boundaries defined
- [x] Testable predictions + falsification criteria
- [x] Statistical design with power analysis
- [x] SOTA baseline comparison
- [x] Contribution summary
- [x] Related work distinctions
- [x] Sub-hypothesis decomposition

✅ **Ready for Phase 2B:**
- [x] Scientifically testable
- [x] Variables operationally defined
- [x] Sample size justified
- [x] Statistical tests pre-specified
- [x] Confounds controlled
- [x] Novelty established
- [x] Gap alignment clear (Phase 1 Gap 1 - P0)

⚠️ **Requires Phase 2B:**
- [ ] Meta-learning architecture selection
- [ ] Dimension operationalization protocols
- [ ] Stakeholder recruitment protocol
- [ ] XAI system selection criteria
- [ ] Calibration training details
- [ ] Stakeholder consensus protocol design

---

## Timeline Estimate

**Total:** 7-10 months

**Phase 1:** Metric library + stakeholder taxonomy (2-3 months)
**Phase 2:** Classifier + calibration model (3-4 months)
**Phase 3:** Empirical validation (2-3 months)

**Resource Requirements:**
- Computational: Moderate (meta-learning training, NLP classification)
- Human: High (80 stakeholder evaluators, recruitment effort)
- Data: Moderate (20 XAI systems + domain validation metrics)

---

## Next Steps

**Immediate (Phase 2B - Verification Planning):**
1. Decompose main hypothesis into detailed sub-hypotheses (SH1-4)
2. Design verification experiments for each sub-hypothesis
3. Establish success criteria and gate conditions
4. Create detailed experimental protocol
5. Address open questions (Q1-8)
6. Develop resource plan and timeline

**Expected Phase 2B Outputs:**
- Verification roadmap with 4 sub-hypothesis experiments
- Detailed protocols (stakeholder recruitment, calibration training, consensus validation)
- Risk mitigation strategies
- IRB materials preparation
- Budget and resource allocation
- Gate 2B: Decision to proceed to Phase 2C (experiment design)

---

**Full Documentation:** See `02a_extended_hypothesis_full.md` for complete scientific clarification with all details, evidence, and open questions.

---

*Phase 2A Extended Workflow Complete*
*Generated: 2026-02-08*
*Status: ✅ Ready for Phase 2B Verification Planning*
