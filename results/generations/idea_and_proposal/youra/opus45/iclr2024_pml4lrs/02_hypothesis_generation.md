# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GACFIS-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under the condition of model compression for deployment in resource-constrained settings, if group-conditional Fisher Information is used to identify and protect endemic features (weights disproportionately important for minority groups), then the accuracy gap between majority and minority demographic groups will be reduced by >30% compared to standard compression methods, because endemic features encode minority-specific patterns that are systematically deprioritized by global importance metrics.

**Alternative Hypothesis (H0):**
Standard model compression methods do not disproportionately harm minority group accuracy, OR group-conditional Fisher Information does not provide meaningful differentiation between majority-critical and minority-critical weights, resulting in no fairness improvement from the GACFIS approach.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Compression method | Independent | GACFIS vs. standard QAT/magnitude pruning | Categorical: {GACFIS, Standard-QAT, Magnitude-Pruning} |
| Fairness weighting λ | Independent | Controls endemic feature protection strength in loss function | Continuous: 0.0-1.0, default 0.5 |
| Compression ratio | Independent | Target model size reduction | Discrete: {4x, 8x, 16x} |
| Accuracy gap between groups | Dependent | \|Acc_majority - Acc_minority\| post-compression | Continuous: 0-100%, target <5% |
| Equalized odds ratio | Dependent | min(TPR_min/TPR_maj, FPR_maj/FPR_min) | Continuous: 0-1.0, target >0.85 |
| Model size | Dependent | Parameters/memory footprint | MB or parameter count |
| Inference latency | Dependent | Time per inference on target hardware | Milliseconds |
| Model architecture | Controlled | Fixed architecture throughout experiments | ResNet18, MobileNetV2 |
| Training data | Controlled | Same dataset for all conditions | COMPAS, Adult Income, CelebA |
| Evaluation protocol | Controlled | Same test split, random seeds | Fixed 5 seeds, stratified split |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Minority Underrepresentation in Training
    ↓
    Minority groups contribute fewer samples → lower gradient magnitudes
    for minority-specific features during training
    ↓
Step 2: Biased Importance Estimation
    ↓
    Global Fisher Information F(w) = E[(∂L/∂w)²] dominated by majority
    group → minority-critical weights assigned lower importance scores
    ↓
Step 3: Unfair Compression
    ↓
    Standard compression removes/approximates low-importance weights first
    → disproportionate loss of minority-critical features
    ↓
[OUTCOME]: Increased accuracy gap between demographic groups
```

**GACFIS Intervention Point:** Step 2 - Compute group-conditional Fisher Information to identify endemic features and adjust importance scoring.

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Li et al. (2024) | Group-level generalization depends on group covariance and minority fraction | Strong |
| Step 2 → Step 3 | Kamal & Talbert (2024) | Compression type/amount substantially impacts fairness on COMPAS | Strong |
| Step 3 → Outcome | Vlontzou et al. (2025) | 40-57% equalized odds improvement achievable with proper mitigation | Strong |

**Key Tension:**
- **Tension:** Li et al. (2024) suggests increasing minority fraction doesn't necessarily improve minority generalization, while our hypothesis assumes protecting minority-specific weights will improve minority accuracy.
- **Resolution:** Li et al. focuses on training-time interventions, while GACFIS intervenes at compression-time. The findings are compatible: minority features may be learned adequately during training but lost during compression.

### 1.4 Key Assumptions

1. **Minority features are separable in weight space**
   - Consequence if violated: Endemic Feature Score shows no variance → GACFIS reduces to standard compression

2. **Demographic labels available during compression**
   - Consequence if violated: Must use unsupervised proxy → potential fairness-proxy mismatch

3. **Diagonal Fisher approximation is sufficient**
   - Consequence if violated: Must use K-FAC or full Fisher → 10-100x computational overhead

4. **Fairness-accuracy tradeoff is tractable**
   - Consequence if violated: GACFIS may require unacceptable accuracy sacrifice → limited practical applicability

### 1.5 Scope & Boundaries

**Applies to:**
- Classification tasks with binary or multi-class outputs
- Datasets with known demographic attributes (binary demographic splits)
- Image classification (CelebA) and tabular data (COMPAS, Adult Income)
- Model compression via pruning and quantization (4x-16x)

**Does NOT apply to:**
- Regression tasks, intersectional fairness, unlabeled demographics
- Generative models, extreme compression ratios (>32x)

**Known Limitations:**
- Requires demographic labels (privacy concern)
- Binary demographic focus; intersectionality not addressed
- Diagonal Fisher approximation; ~20-40% additional training time

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Accuracy Gap Reduction vs. Standard Compression)**:
GACFIS will reduce the post-compression accuracy gap between majority and minority groups by >30% compared to standard compression methods at the same compression ratio.

*Measurement*:
- Gap Reduction = (Gap_standard - Gap_GACFIS) / Gap_standard × 100%
- Target: Gap Reduction > 30% with p < 0.05
- Statistical test: Paired t-test, n ≥ 20 runs

*Success Criteria for Phase 2B*:
- Primary: Gap Reduction > 30% (p < 0.05)
- Falsification: Gap Reduction ≤ 10% OR GACFIS gap ≥ standard compression gap

**Secondary Predictions:**

**P2 (Equalized Odds Improvement)**:
GACFIS will improve equalized odds ratio from baseline <0.7 to >0.85 after compression.

**P3 (Fairness-Accuracy Tradeoff Curve)**:
As fairness weighting λ increases, fairness improves while overall accuracy decreases, with Pareto-optimal λ* achieving >30% fairness improvement at <5% accuracy cost.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Gap Reduction ≤ 10% across all configurations
2. **Mechanism Failure**: Endemic Feature Score shows no variance (σ < 0.1)
3. **Comparative Failure**: GACFIS worse than standard on BOTH accuracy AND fairness
4. **Tradeoff Failure**: 30% fairness improvement requires >15% accuracy cost

### 1.7 Statistical Verification Design

**Sample Size**: n ≥ 20 runs (5 seeds × 4 datasets)
**Statistical Test**: Paired t-test with Bonferroni correction
**Significance Level**: α = 0.05
**Report Format**: Mean ± Std Dev, 95% CI, Cohen's d, p-values

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does fairness degradation from model compression exist and is it measurable using equalized odds and accuracy gap metrics on standard fairness benchmarks?"
- Verification type: Empirical measurement
- Critical: MUST PASS to establish problem exists

**SH2 (Mechanism):**
"Is group-conditional Fisher Information the mechanism through which GACFIS identifies and protects endemic features?"
- Decomposes to 3 sub-hypotheses (H-M1 through H-M3):
  - H-M1: Minority weights have lower global Fisher Information scores
  - H-M2: Endemic Feature Score identifies minority-critical weights
  - H-M3: Protecting endemic features preserves minority accuracy
- Verification type: Causal analysis with ablation studies

**SH3 (Comparison):**
"Does GACFIS outperform standard compression methods on fairness while maintaining acceptable accuracy?"
- Verification type: Comparative empirical with statistical testing

**Total Sub-Hypotheses for Phase 2B:** 5 (SH1 + 3 mechanism + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-GACFIS-v1
- [x] Confidence level: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] Variables operationalized with evidence
- [x] Causal mechanism with N=3 steps and evidence table
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (P1 primary)
- [x] 4 falsification criteria defined
- [x] Baselines identified (QAT, magnitude pruning)
- [x] SH1, SH2, SH3 ready for Phase 2B

### Open Questions

1. **Data Availability:** Are demographic-labeled compression benchmarks available beyond COMPAS/Adult/CelebA?

2. **Computational Resources:** Minimum hardware for 20-40% overhead group-conditional Fisher computation?

3. **Priority Verification Order:** SH1 first (validate problem exists) or parallel with SH2 given Kamal & Talbert evidence?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
