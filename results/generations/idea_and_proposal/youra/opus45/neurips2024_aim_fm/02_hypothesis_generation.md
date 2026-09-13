# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (TPMOL - Round 1)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-TPMOL-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under clinical deployment conditions requiring trustworthy AI, if constrained Pareto multi-objective optimization (TPMOL) is applied to jointly train explainability (via Attention Consistency Regularization), robustness (via adversarial training), and privacy (via Explanation-Level Differential Privacy) objectives, then Medical Foundation Models will achieve superior unified trustworthiness scores (all three dimensions improved simultaneously) compared to single-objective approaches, because multi-objective Pareto optimization with CAGrad can find solutions that balance competing objectives while accuracy constraints prevent diagnostic performance degradation.

**Alternative Hypothesis (H0):**
There is no synergistic benefit from jointly optimizing explainability, robustness, and privacy in Medical Foundation Models; single-objective optimization for each dimension independently achieves equivalent or better results than multi-objective TPMOL, and attempting to optimize all three simultaneously leads to unacceptable trade-offs in at least one dimension or diagnostic accuracy.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Optimization Approach | Independent | Single-objective (baseline) vs TPMOL multi-objective training with CAGrad optimizer | Binary: {Single, TPMOL} |
| Explainability Score | Dependent | Attention Consistency Regularization (ACR) score measuring attention map stability under input perturbations | 0.0 - 1.0 (higher = more consistent) |
| Robustness Score | Dependent | Certified robust accuracy under PGD attacks (ε=8/255) | 0% - 100% (target: >70%) |
| Privacy Score | Dependent | Explanation-Level Differential Privacy (ELDP) ε value | ε ∈ [0.1, 10] (lower = more private, target: ε ≤ 1.0) |
| Diagnostic Accuracy | Dependent (Constrained) | AUC-ROC on CheXpert/MIMIC-CXR benchmark | Constraint: ≥ 0.85 |
| Base Model Architecture | Controlled | BiomedCLIP ViT-B/16 with LoRA adaptation (rank=16) | Fixed |
| Dataset | Controlled | CheXpert or MIMIC-CXR chest X-ray datasets | Fixed per experiment |
| Training Hyperparameters | Controlled | Learning rate, batch size, epochs | Fixed across conditions |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Step 1: Governance-to-Technical Translation
    FUTURE-AI 6-principle structure → Multi-objective loss function design
    ↓
Step 2: Conflict-Averse Optimization
    Multi-objective losses → CAGrad gradient conflict resolution
    ↓
Step 3: Pareto Solution Discovery
    CAGrad optimization → Pareto-optimal trustworthiness solutions
    ↓
Step 4: Constrained Clinical Deployment
    Pareto solutions + AUC≥0.85 constraint → Clinically deployable MFM
    ↓
    [OUTCOME: Unified Trustworthiness]
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | FUTURE-AI (BMJ 2024) | 117 experts validated 6 unified principles for trustworthy medical AI | Strong |
| Step 2 → Step 3 | CAGrad (NeurIPS 2021) | Provable convergence to Pareto-stationary point | Strong |
| Step 3 → Step 4 | Ferrara (2026) | Theoretical explainability-robustness synergy | Medium |
| Step 4 → Outcome | Mohammadi et al. (2026) | DP at ε≈10 maintains clinical performance | Medium |

**Key Tension:**
- **Tension:** Mohammadi et al. (2026) shows strict privacy (ε≈1) causes accuracy loss, but Ferrara (2026) suggests explainability-robustness synergy.
- **Resolution:** ELDP applies DP noise post-training to explanations, potentially decoupling privacy from training quality.

### 1.4 Key Assumptions

1. **Differentiable Loss Formulation** - Evidence: ACR is fully differentiable (Zhao 2026)
   - *If violated:* Requires non-gradient methods

2. **Pareto Solution Existence** - Evidence: Ferrara (2026) theoretical synergy
   - *If violated:* Hypothesis fundamentally fails

3. **CAGrad Domain Transfer** - Evidence: Validated on image tasks (NYU-v2)
   - *If violated:* May require domain-specific modifications

4. **ACR-Clinical Correlation** - Evidence: Attention-guided methods achieve SOTA in medical imaging
   - *If violated:* Requires human evaluation study

### 1.5 Scope & Boundaries

**Applies to:** Medical image classification (chest X-ray, retinal, dermatology), VL-MFMs, clinical deployment requiring compliance

**Does NOT apply to:** Medical NLP, real-time surgical assistance, video analysis, generative models

**Limitations:** ELDP is novel/unvalidated, ACR may not capture all clinical requirements, ~20% compute overhead

### 1.6 Testable Predictions

**Primary Prediction (P1):**
If TPMOL is applied, then all three trustworthiness metrics improve over single-objective baselines:
- ACR Score: ≥ 0.80
- Robust Accuracy: ≥ 70% (PGD ε=8/255)
- Privacy: ELDP ε ≤ 1.0
- **Constraint:** Diagnostic AUC ≥ 0.85

*Measurement:* Paired t-test, n ≥ 25 runs vs 3 single-objective baselines

**Secondary Predictions:**
- **P2:** ACR maintains attention consistency ≥ 0.80 under perturbations
- **P3:** ELDP achieves ε ≤ 1.0 without degrading ACR (within 5%)
- **P4:** CAGrad converges within 50 epochs without gradient explosion

**Falsification Criteria:**
1. Any trustworthiness metric worse than corresponding single-objective baseline
2. Diagnostic AUC < 0.85 (constraint violation)
3. >20% degradation in one dimension to achieve another
4. CAGrad convergence failure within 100 epochs

### 1.7 SOTA Baseline

*Not applicable - unified trustworthiness is novel; baselines are single-objective approaches*

### 1.8 Statistical Verification Design

- **Sample Size:** n ≥ 25 per condition (4 conditions)
- **Effect Size:** Cohen's d = 0.6 (medium)
- **Test:** One-way ANOVA with Tukey HSD
- **Significance:** α = 0.05 with Bonferroni correction
- **Report:** Mean ± SD, 95% CI, Cohen's d, adjusted p-values

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Can TPMOL achieve improvements in all three trustworthiness dimensions while maintaining AUC ≥ 0.85?"
- Verification: Empirical comparison
- Critical: MUST PASS to proceed

**SH2 (Mechanism):**
"Is the 4-step causal mechanism the actual cause of improvement?"
- Decomposes to H-M1 through H-M4 (one per causal link)
- Verification: Ablation studies
- Critical: Determines explanatory power

**SH3 (Comparison):**
"Does TPMOL outperform single-objective baselines in unified trustworthiness?"
- Verification: Comparative empirical
- Critical: Determines practical value

**Total Sub-Hypotheses:** 6 (SH1 + 4 mechanism + SH3)

### Readiness Checklist

- [x] "If-Then-Because" format
- [x] Hypothesis ID: H-TPMOL-v1
- [x] Confidence: 0.78
- [x] H0 defined
- [x] Variables operationalized
- [x] Causal mechanism with evidence (N=4)
- [x] Key tension + resolution
- [x] Assumptions with consequences
- [x] 4 testable predictions
- [x] Falsification criteria
- [x] Baselines identified
- [x] SH1/SH2/SH3 defined

### Open Questions

1. **Resources:** Single A100 + ~20% overhead for CAGrad
2. **Data:** CheXpert/MIMIC-CXR require DUAs
3. **ELDP:** No prior implementation - design from DP literature
4. **Priority:** Start with SH1 (existence) before mechanism ablations

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
