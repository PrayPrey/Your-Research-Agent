# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-IB-FAIR-SYNTH-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under conditions of tabular data generation with LLMs, if information flow is controlled through a variational Information Bottleneck at the sequence representation level combined with ensemble teacher distillation (privacy teacher + fairness teacher), then synthetic data will simultaneously achieve differential privacy guarantees (ε ≤ target), fairness constraints (SPD < 0.1, EO < 0.1), and high utility (accuracy within 5% of non-private baseline) because the IB compresses representations to suppress individual-identifying and sensitive-attribute information while preserving task-relevant features, and ensemble teachers specialize in optimizing conflicting objectives through weighted distillation.

**Alternative Hypothesis (H0):**
Controlling information flow through IB combined with ensemble teacher distillation does NOT improve the privacy-fairness-utility trade-off compared to naive sequential application of privacy and fairness techniques, or the approach introduces irreconcilable conflicts that prevent simultaneous optimization.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| IB Compression Rate (β) | Independent | Lagrangian multiplier in IB objective controlling compression strength | 0.001 - 1.0 |
| Ensemble Weight Distribution | Independent | Weights for privacy teacher (α_p) vs fairness teacher (α_f) where α_p + α_f = 1 | α_p, α_f ∈ [0.2, 0.8] |
| DP Budget (ε) | Independent | Rényi DP epsilon parameter for privacy accounting | 1.0 - 10.0 |
| Privacy Loss | Dependent | Rényi DP ε achieved + MIA success rate (AUC) | ε ≤ target, MIA AUC < 0.6 |
| Fairness Gap | Dependent | Statistical Parity Difference (SPD) and Equalized Odds (EO) between protected groups | SPD < 0.1, EO < 0.1 |
| Utility Score | Dependent | Downstream classification accuracy on synthetic data vs real data baseline | Within 5% of baseline |
| Protected Attribute | Controlled | Binary sensitive attribute (e.g., gender, race) held constant | Fixed per dataset |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: LLM Encoding
   LLM encodes tabular data → Sequence representations contain both task-relevant and sensitive information

Step 2: IB Compression
   Variational IB layer compresses representations → Suppresses individual-identifying information while preserving utility

Step 3: Ensemble Specialization
   Ensemble teachers specialize objectives → Privacy teacher optimizes DP, Fairness teacher optimizes demographic parity

Step 4: Balanced Distillation
   Weighted distillation combines teachers → Student model achieves balanced privacy-fairness-utility trade-off
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | TabLLM, MALLM-GAN | LLM effectively captures tabular statistics in latent space | Strong |
| Step2 → Step3 | RFIB (2022), Privacy for Fairness (2024) | IB compresses while preserving utility; LDP enhances fairness through IB | Strong |
| Step3 → Step4 | PFGuard (ICLR 2025) | Ensemble teachers resolve privacy-fairness conflicts | Strong |
| Step4 → Outcome | PFGuard (ICLR 2025), PF-WGAN (2025) | Ensemble learning achieves DP + fairness convergence simultaneously | Strong |

**Key Tension:**
- **Tension:** Privacy mechanisms may suppress minority group representations needed for fairness (privacy-fairness conflict identified by PFGuard)
- **Resolution:** Ensemble teacher approach with staged training resolves conflicts by allowing each teacher to specialize, then balancing through weighted distillation

### 1.4 Key Assumptions

1. **LLM latent space captures meaningful tabular patterns**
   - Evidence: TabLLM, MALLM-GAN, GPT-4o outperforms CTGAN in zero-shot generation
   - Consequence if violated: Framework would fail at Step 1; mitigation requires tabular-specific architecture

2. **Variational IB can be applied to sequence-level representations**
   - Evidence: RFIB (2022) successfully applied IB to tabular classification with variational bounds
   - Consequence if violated: Cannot control information flow; would need alternative compression method

3. **Ensemble distillation balances conflicting objectives**
   - Evidence: PFGuard (ICLR 2025) demonstrates ensemble resolves privacy-fairness conflicts
   - Consequence if violated: One objective would dominate; need alternative multi-objective optimization

4. **InfoNCE provides tractable MI estimation**
   - Evidence: Contrastive learning literature shows InfoNCE scales to high dimensions
   - Consequence if violated: IB objective becomes intractable; need sampling-based approximations

### 1.5 Scope & Boundaries

**Applies to:**
- Tabular data with binary sensitive attributes
- Moderate-sized datasets (10K - 1M rows)
- Tabular-adapted LLM architectures
- Standard fairness metrics (SPD, EO)
- Differential privacy with Rényi accounting

**Does NOT apply to:**
- Very high-dimensional tabular data (>1000 columns)
- Real-time generation requirements (<100ms latency)
- Non-binary sensitive attributes without modification
- Image or text modalities

**Known Limitations:**
- Sequence-level IB may miss fine-grained per-token patterns
- Computational overhead approximately 1.5x baseline LLM fine-tuning
- Requires careful β tuning via validation set Pareto frontier

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Privacy-Fairness-Utility Balance)**:
IB-FAIR-SYNTH will achieve the privacy-fairness-utility triple constraint: ε ≤ 8.0, SPD < 0.1, and downstream accuracy within 5% of non-private baseline, outperforming naive sequential combination of DP and fairness techniques.

*Measurement*:
- Privacy: Rényi DP ε via composition theorem + MIA AUC < 0.6
- Fairness: SPD < 0.1, EO difference < 0.1
- Utility: Classification accuracy within 5% of real data baseline
- Statistical test: Paired t-test across 5 random seeds, p < 0.05

*Basis*:
PFGuard demonstrates ensemble approach achieves DP + fairness simultaneously. RFIB shows IB maintains utility while enforcing fairness. PF-WGAN achieves balanced trade-off across three objectives.

*Success Criteria for Phase 2B*:
- Primary: All three constraints met simultaneously (ε ≤ 8.0, SPD < 0.1, accuracy drop ≤ 5%)
- Falsification: Any single constraint violated by >50% (ε > 12, SPD > 0.15, accuracy drop > 7.5%)

**Secondary Predictions:**

**P2 (Mechanism Validation - IB Contribution)**:
Increasing IB compression rate β will monotonically improve privacy (lower MIA AUC) and fairness (lower SPD) at the cost of utility, demonstrating IB's role in information suppression.

**P3 (Ensemble Teacher Balance)**:
Equal weighting of privacy and fairness teachers (α_p = α_f = 0.5) will achieve Pareto-optimal trade-off, while extreme weightings (α_p > 0.8 or α_f > 0.8) will sacrifice one objective.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Cannot achieve all three constraints simultaneously on ANY of the 4 benchmark datasets (Adult, COMPAS, German Credit, Bank Marketing)

2. **Mechanism Failure**: IB compression rate β shows no effect on privacy/fairness metrics (< 5% change across β range)

3. **Ensemble Failure**: Single-teacher models match or exceed ensemble performance (ensemble provides no benefit)

4. **Comparative Failure**: Naive sequential DP + fairness achieves equivalent or better results than IB-FAIR-SYNTH

### 1.7 Statistical Verification Design

**Sample Size**: Minimum n ≥ 20 runs per configuration (5 seeds × 4 datasets)

**Statistical Test**:
- Paired t-test for within-method comparisons
- Wilcoxon signed-rank test for non-normal distributions
- Significance level: α = 0.05

**Report Format**:
- Mean ± Std Dev for all metrics
- 95% Confidence Intervals
- Effect size (Cohen's d) for primary comparisons

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does IB-FAIR-SYNTH achieve the triple constraint (privacy ε ≤ 8.0, fairness SPD < 0.1, utility within 5%) on standard tabular benchmarks?"
- Maps to: Primary prediction P1
- Verification type: Empirical validation
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is the proposed 4-step causal mechanism (LLM encoding → IB compression → Ensemble specialization → Balanced distillation) the actual cause of the achieved trade-off?"

Phase 2B will decompose into 4 sub-hypotheses:
- **H-M1:** LLM encoding captures tabular structure adequately
- **H-M2:** IB compression controls information flow (β sensitivity analysis)
- **H-M3:** Ensemble teachers specialize effectively (ablation: single vs. ensemble)
- **H-M4:** Weighted distillation achieves balance (weight sensitivity analysis)

**SH3 (Comparison):**
"Does IB-FAIR-SYNTH outperform naive sequential application of DP + fairness techniques and single-objective baselines?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value over existing approaches

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-IB-FAIR-SYNTH-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=4 steps, evidence table provided)
- [x] Causal chain length (N=4) determined and stored
- [x] Key tension identified (privacy-fairness conflict) and resolution proposed (ensemble approach)
- [x] Key assumptions list consequences if violated (4 assumptions with mitigations)
- [x] At least 2 testable predictions exist with primary marked (P1 primary, P2/P3 secondary)
- [x] Falsification criteria are defined (4 failure conditions)
- [x] Baselines are identified for comparison (CTGAN, DP-CTGAN, FairTabGen, PF-WGAN)
- [x] SH1, SH2, SH3 are clear starting points for Phase 2B decomposition

### Open Questions

1. **Resource Requirements:** What computational resources are needed for ensemble teacher training? Estimate: 1.5x baseline, single A100 GPU sufficient for tabular datasets.

2. **Data Availability:** Are Adult, COMPAS, German Credit, Bank Marketing datasets readily available with documented sensitive attributes? Yes - all are standard fairness benchmarks.

3. **Implementation Priority:** Should we validate IB mechanism first (SH2) or existence (SH1)? Recommend: SH1 first (quick validation), then SH2 for mechanism understanding.

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-12*
