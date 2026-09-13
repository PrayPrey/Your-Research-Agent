# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CACP-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under multi-modal scientific foundation model deployment conditions, if constraint violations are incorporated into conformal prediction nonconformity scores (α = e_pred + λ_d * e_constraint), then uncertainty bounds will correlate with constraint satisfaction AND coverage guarantees will be preserved, because constraint violations serve as an additional uncertainty signal that conformal prediction's finite-sample guarantees can accommodate without distributional assumptions.

**Alternative Hypothesis (H0):**
Incorporating constraint violations into nonconformity scores either: (a) does not improve uncertainty-constraint correlation beyond standard conformal prediction, OR (b) violates the finite-sample coverage guarantees of conformal prediction, OR (c) fails to scale to foundation models beyond 100M parameters.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Constraint violation magnitude (e_constraint) | Independent | \|\|C(y_pred) - C_target\|\| computed via neurosymbolic constraint checker with domain-specific rules (conservation laws, symmetries, structural rules) | [0.0, ∞); lower is better |
| Domain-specific weight (λ_d) | Independent | Learned parameter per modality via validation set optimization | [0.1, 10.0] |
| Modality type | Controlled | Categorical: protein structure, materials properties, molecular dynamics - each with modality-specific calibration sets | {protein, materials, molecular} |
| Calibration error (ECE) | Dependent | Expected Calibration Error measured as mean absolute gap between confidence and accuracy across bins | [0%, 50%]; target: <15% |
| Coverage rate | Dependent | Empirical fraction of true values within prediction intervals at specified confidence level | [0%, 100%]; target: ≥90% |
| Constraint satisfaction rate | Dependent | Percentage of predictions satisfying domain-specific scientific constraints | [0%, 100%]; target: ≥99% |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Constraint Specification (Symbolic Rules)
    ↓ [Formalization]
Step 2: Constraint Violation Computation (e_constraint)
    ↓ [Score Augmentation]
Step 3: Augmented Nonconformity Score (α = e_pred + λ_d * e_constraint)
    ↓ [Conformal Prediction]
Step 4: Calibrated Prediction Intervals
    ↓ [Joint Guarantee]
Outcome: Simultaneous UQ + Constraint Satisfaction
```

**Mechanism Description:**

1. **Step 1 → Step 2**: Domain-specific scientific constraints (conservation laws, symmetries, structural rules) are encoded as symbolic rules and evaluated through a differentiable constraint checker (CANUF-inspired architecture). The constraint checker computes e_constraint = ||C(y_pred) - C_target||.

2. **Step 2 → Step 3**: Constraint violations are incorporated into the conformal prediction framework by augmenting the standard nonconformity score. The composite score α = e_pred + λ_d * e_constraint ensures that predictions violating constraints receive higher nonconformity scores.

3. **Step 3 → Step 4**: The augmented nonconformity scores are used in the standard conformal prediction calibration procedure to construct prediction intervals. Higher scores (more constraint violations) lead to wider intervals.

4. **Step 4 → Outcome**: Predictions with high constraint violations receive wider uncertainty bounds, naturally signaling unreliability. Coverage guarantees are preserved because conformal prediction only requires exchangeability, not specific score structure.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | CANUF (2026) | Differentiable constraint extraction with 91.4% precision | Strong |
| Step 2 → Step 3 | PILE Score (ICLR 2026) | Physics residuals serve as valid uncertainty indicators | Strong |
| Step 3 → Step 4 | Physics-Informed CP (ICML 2025) | CP with physics residuals provides guaranteed coverage | Strong |
| Step 4 → Outcome | CANUF (2026) | 34.7% ECE reduction + 99.2% constraint satisfaction | Strong |

**Key Tension:**
- **Tension:** CANUF (2026) achieves constraint satisfaction through Bayesian deep learning with variational inference, while Physics-Informed CP (2025) uses conformal prediction without Bayesian methods. The optimal integration strategy is unclear.
- **Resolution:** This verification plan tests whether conformal prediction's score-based approach can achieve comparable or better results than Bayesian methods when constraint violations are used as nonconformity scores, potentially offering computational advantages at scale.

### 1.4 Key Assumptions

| # | Assumption | Evidence | Consequence if Violated |
|---|------------|----------|------------------------|
| A1 | Constraint violations are measurable and differentiable (or approximable) | CANUF demonstrates differentiable constraint evaluation | Must use relaxation techniques or surrogate gradients; may increase computational cost |
| A2 | Scientific constraints can be formalized as symbolic rules | Domain-specific constraint libraries exist for physics, chemistry, biology | Limits applicability to domains with well-defined constraints; excludes qualitative/emergent properties |
| A3 | CP coverage guarantees hold with constraint-augmented scores | CP theory requires only exchangeability, not specific score structure | Core theoretical contribution invalidated; hypothesis fundamentally wrong |
| A4 | Cross-modal consistency is meaningful and quantifiable | Multi-modal scientific data shares underlying physical principles | Multi-modal framework reduces to single-modal approach; still useful but less novel |

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Scientific foundation models with formalizable constraints (100M-1B parameters)
- Domains with explicit conservation laws, symmetries, or structural rules
- Protein structure prediction, materials property prediction, molecular dynamics
- Settings where calibrated uncertainty is required for downstream decision-making

**Where Hypothesis Does NOT Apply:**
- Emergent properties without explicit constraint formulations
- Purely qualitative scientific predictions (e.g., natural language explanations)
- Models without calibration data (conformal prediction requires calibration set)
- Real-time applications where constraint checking overhead is prohibitive

**Known Limitations:**
- Requires domain expertise to specify constraint rules
- Calibration set needed per modality (data overhead)
- Scaling validated only to 1B parameters (larger models untested)
- λ_d tuning may require hyperparameter search per domain

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (ECE Improvement vs CANUF Baseline 34.7%):**
CACP will achieve Expected Calibration Error reduction ≥35% compared to standard Bayesian neural networks, matching or exceeding CANUF's 34.7% improvement while providing distribution-free coverage guarantees.

*Measurement*:
- ECE reduction ≥35% with p < 0.05
- Statistical test: Paired t-test, n ≥ 15 runs (same random seeds)
- Comparison: CACP vs BNN baseline and CACP vs CANUF

*Basis*:
CANUF achieves 34.7% ECE reduction through Bayesian + neurosymbolic approach. CACP targets the same constraint-aware UQ through conformal prediction, hypothesizing comparable calibration with simpler theoretical guarantees.

*Success Criteria for Phase 2B*:
- Primary: ECE reduction ≥35% (p < 0.05)
- Falsification: ECE reduction <25% triggers rejection (significantly worse than CANUF)

**Secondary Predictions:**

**P2 (Coverage Guarantee Preservation):**
CACP maintains empirical coverage rate within ±2% of nominal level (e.g., 88-92% for 90% nominal) across all modalities.

*Measurement*: Coverage gap = |Empirical coverage - Nominal coverage|
*Threshold*: Coverage gap ≤ 2%

**P3 (Constraint Satisfaction Rate):**
CACP achieves ≥99% constraint satisfaction rate, matching CANUF's 99.2% while using conformal prediction framework.

*Measurement*: Percentage of predictions satisfying domain-specific constraints
*Threshold*: Constraint satisfaction ≥99%

**P4 (Cross-Modal Consistency):**
Cross-modal predictions (when applicable) show uncertainty correlation coefficient ρ ≥ 0.7.

*Measurement*: Pearson correlation between uncertainty estimates across modalities
*Threshold*: ρ ≥ 0.7

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: ECE reduction <25% (significantly worse than CANUF baseline)
2. **Coverage Failure**: Empirical coverage deviates >5% from nominal (CP guarantee violated)
3. **Constraint Failure**: Constraint satisfaction <95% (core benefit lost)
4. **Scalability Failure**: Method fails to complete on 1B-parameter model within 10x baseline inference time

### 1.7 SOTA Baseline (SOTA Comparison Mode)

**SOTA Benchmark Summary:**

| Method | Metric | Performance | Dataset | Year |
|--------|--------|-------------|---------|------|
| CANUF | ECE Reduction | 34.7% | Materials Project (140K+), QM9 | 2026 |
| CANUF | Constraint Satisfaction | 99.2% | Materials Project, QM9 | 2026 |
| Standard BNN | ECE | Baseline (0%) | Various | - |
| Physics-Informed CP | Coverage | Guaranteed (finite-sample) | PDEs, Plasma | 2025 |

**Statistics:**
- SOTA Mean ECE Reduction: 34.7%
- Performance Tier: HIGH improvement domain (>30% improvement possible)
- Ceiling Room: ~65% (theoretical minimum ECE = 0%)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): ~0.8 (large effect expected based on CANUF results)
- Required runs: n ≥ 15 per condition
- Statistical power: 0.8

**Test Specification:**
- Method: Paired t-test (same random seeds across conditions)
- Significance level: α = 0.05 (one-tailed for improvement)
- Multiple comparison correction: Bonferroni for P1-P4

**Report Format:**
- Mean ± Std Dev for all metrics
- 95% Confidence Interval
- Cohen's d effect size
- p-value with correction

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Total Sub-Hypotheses for Phase 2B:** 2 + 4 = 6 sub-hypotheses

**SH1 (Existence):**
"Does constraint-augmented conformal prediction produce calibrated uncertainty estimates for scientific foundation models?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism - 4 sub-hypotheses):**
Phase 2B will decompose into 4 mechanism sub-hypotheses (H-M1 through H-M4):
- H-M1: "Constraint specification → Constraint violation computation" (differentiable constraint checking works)
- H-M2: "Constraint violation → Augmented nonconformity score" (score augmentation is valid)
- H-M3: "Augmented score → Calibrated intervals" (CP guarantees preserved)
- H-M4: "Calibrated intervals → Joint UQ + constraint satisfaction" (practical benefits realized)

**SH3 (Comparison):**
"Does CACP match or exceed CANUF's performance (34.7% ECE reduction, 99.2% constraint satisfaction) while providing distribution-free guarantees?"
- Maps to: Secondary predictions (P2, P3)
- Verification type: Comparative empirical
- Critical: Determines practical value vs. existing approaches

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-CACP-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence_for_links table)
- [x] Causal chain length (N=4) determined and documented
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist (4 predictions: P1 primary, P2-P4 secondary)
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison (CANUF, Standard CP, BNN)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** What compute is needed for 1B-parameter FM constraint checking? Estimate: 2-4x inference overhead (sparse graph optimization can reduce this).

2. **Data Availability:** Are calibration sets available for all three modalities (protein, materials, molecular)? Materials Project (140K+) and QM9 are available; protein datasets (AlphaFold DB) may require careful subset selection.

3. **Priority Verification Order:** Recommend H-M3 first (CP guarantee preservation is theoretical core), then H-M1 (constraint checking feasibility), then H-M2/H-M4 (empirical validation).

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
