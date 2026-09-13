# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-GCFS-v1
**Confidence Level:** 0.82

**Main Hypothesis:**
Under multi-domain classification settings with domain labels, if per-feature gradient variance across domains is computed and used to weight features (CausalScore = 1/(1+Var)), then out-of-distribution accuracy will exceed ERM baselines because features with low gradient variance represent causal (domain-invariant) relationships while features with high gradient variance represent spurious (domain-specific) correlations.

**Alternative Hypothesis (H0):**
There is no systematic relationship between per-feature gradient variance and feature causality; GCFS-weighted models will not outperform ERM on out-of-distribution test domains.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Per-feature gradient variance | Independent | Var_d[∇_f L_d] computed across all training domains for each feature dimension | 0.0 - 10.0 (normalized) |
| OOD test accuracy | Dependent | Classification accuracy on held-out test domain using leave-one-domain-out protocol | 70% - 95% |
| Model architecture | Controlled | ResNet-50 pretrained on ImageNet | Fixed |
| Training procedure | Controlled | Standard DomainBed training protocol with fixed hyperparameters | Fixed |
| Number of training domains | Confounding | Number of source domains available for gradient variance estimation | 3-5 (DomainBed standard) |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Gradient Computation
    ↓
Step 2: Variance Measurement → CausalScore Assignment
    ↓
Step 3: Feature Weighting → OOD Performance Improvement
    ↓
Outcome: Improved OOD Accuracy vs ERM
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | IRM (Arjovsky 2019), Fishr (Rame 2022) | Gradient-based invariance penalties are effective for capturing relationship heterogeneity | Strong |
| Step2 → Step3 | Unified Causal View (Wang & Veitch 2022) | Causal invariance is tied to stable mechanisms across environments | Strong |
| Step3 → Outcome | DomainBed (Gulrajani 2020), Risks of IRM (Rosenfeld 2020) | Feature selection based on invariance can improve OOD when properly implemented | Medium |

**Key Tension:**
- **Tension:** "Risks of IRM" (Rosenfeld 2020) demonstrates that IRM fails when test domains are dissimilar to training, yet GCFS relies on similar invariance assumptions.
- **Resolution:** GCFS differs from IRM by providing interpretable per-feature causal scores rather than implicit penalties. This allows diagnosis of when invariance assumptions are violated.

### 1.4 Key Assumptions

1. **Causal features exhibit stable gradient-to-label relationships across domains**
   - Consequence if violated: CausalScores will not distinguish causal from spurious features; GCFS degenerates to uniform weighting (≈ ERM)

2. **Domain labels represent meaningful distribution shifts**
   - Consequence if violated: Gradient variance will not capture spurious correlations; all features will have similar scores

3. **Gradient variance is a computationally tractable proxy for relationship heterogeneity**
   - Consequence if violated: Computational overhead may outweigh benefits; approximation errors may dominate

4. **Sufficient training domains are available (≥3)**
   - Consequence if violated: Variance estimates will be unreliable; GCFS may overfit to spurious domain-specific patterns

### 1.5 Scope & Boundaries

**Applies to:**
- Multi-domain image classification tasks with explicit domain labels
- Standard DG benchmarks: PACS, VLCS, OfficeHome, TerraIncognita, DomainNet
- Settings with ≥3 training domains

**Does NOT apply to:**
- Single-domain settings, unsupervised DG without domain labels
- Non-classification tasks (regression, generation)

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (OOD Accuracy vs SOTA 85.0% ± 3.5%)**:
GCFS-weighted models will achieve OOD test accuracy > 87.5% (averaged across DomainBed benchmarks)

*Measurement*:
- OOD accuracy > 87.5% with p < 0.05
- Statistical test: Paired t-test vs ERM baseline, n ≥ 25 runs

*Success Criteria for Phase 2B*:
- Primary: Accuracy > 87.5% (p < 0.05)
- Falsification: Accuracy ≤ 82.0% triggers rejection

**Secondary Predictions:**

**P2 (Mechanism Validation)**:
Features with high CausalScore (top 20%) will have lower gradient variance than features with low CausalScore (bottom 20%) by at least 2x ratio.

**P3 (Interpretability Advantage)**:
On synthetic datasets with known causal structure, CausalScores will correlate with ground-truth causal features (Spearman ρ > 0.6).

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:
1. **Primary Failure**: OOD accuracy ≤ 82.0%
2. **Mechanism Failure**: CausalScore variance ratio < 1.5x
3. **Comparative Failure**: GCFS performs worse than ERM on >50% of benchmarks

### 1.7 SOTA Baseline

| Method | Average OOD Accuracy |
|--------|---------------------|
| ERM | 68.9% |
| IRM | 68.5% |
| CORAL | 70.3% |

**SOTA Mean:** ~69% | **Std Dev:** ~3.5% | **Target:** >72% (3% improvement)

### 1.8 Statistical Verification Design

**Sample Size:** n ≥ 25 runs (5 benchmarks × 5 seeds)
**Statistical Test:** Paired t-test, α = 0.05 (one-tailed)
**Effect Size:** Cohen's d ≈ 0.71
**Report Format:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does gradient variance heterogeneity exist across domains such that features can be differentiated into high-variance and low-variance groups?"

**SH2 (Mechanism):**
"Is gradient variance a valid proxy for feature causality?" (Will decompose to H-M1, H-M2, H-M3)
- H-M1: Gradient computation accurately reflects feature importance
- H-M2: Variance measurement distinguishes causal from spurious
- H-M3: Feature weighting by CausalScore improves OOD accuracy

**SH3 (Comparison):**
"Does GCFS outperform ERM and existing DG methods (IRM, DANN, CORAL) on standard benchmarks?"

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-GCFS-v1
- [x] Confidence level specified: 0.82
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence
- [x] Causal mechanism has evidence at each step (N=3 steps)
- [x] Key tension identified and resolution proposed
- [x] Key assumptions list consequences if violated
- [x] At least 2 testable predictions exist
- [x] Falsification criteria are defined
- [x] Baselines are identified for comparison
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Resource Requirements:** Computational overhead of GCFS vs ERM (~5-10% estimated)
2. **Data Availability:** DomainBed datasets accessible and configured?
3. **Implementation Priority:** Start with PACS (easier) or TerraIncognita (harder)?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work (8 sources with full citations)

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
