# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-12
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CC-ACCP-v1
**Confidence Level:** 0.84

**Main Hypothesis:**
Under the condition of molecular property prediction tasks with known activity cliff pairs, if molecules are clustered by their proximity to activity cliff pairs (using Tanimoto similarity to known cliff pairs) and separate conformal thresholds are computed per cluster, then the resulting prediction intervals will achieve 90% coverage within each cluster (including cliff-adjacent molecules) because activity cliff proximity directly correlates with prediction difficulty, making cluster-specific calibration more appropriate than global calibration.

**Alternative Hypothesis (H0):**
Activity cliff proximity does not correlate with prediction difficulty, and cluster-conditioned conformal prediction provides no improvement in conditional coverage over standard marginal conformal prediction.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Activity cliff proximity score | Independent | Tanimoto similarity to nearest known activity cliff pair; computed from ECFP4 molecular fingerprints | 0.0-1.0 (continuous); clusters: <0.4 (non-cliff), 0.4-0.7 (borderline), >0.7 (cliff-adjacent) |
| Cluster-conditional coverage rate | Dependent | Proportion of true values falling within prediction intervals, measured separately per cluster | Target: 90% ± 5% per cluster |
| Prediction interval width | Dependent | Upper bound minus lower bound of conformal prediction interval | Expected: 0.5-2.0 pIC50 units (wider for cliff-adjacent) |
| Base model architecture | Controlled | Fixed D-MPNN via Chemprop with default hyperparameters | Chemprop v2.x |
| Target coverage level | Controlled | Fixed at 90% (α=0.1) | 0.9 |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Activity cliff proximity score → Molecule clustering
   ↓
Step 2: Molecule clustering → Cluster-specific conformal thresholds
   ↓
Step 3: Cluster-specific thresholds → Conditional coverage guarantee
   ↓
Outcome: Reliable prospective validation for molecular ML models
```

**Step 1: Activity cliff proximity → Molecule clustering**
- Mechanism: Structurally similar molecules to known cliff pairs share prediction difficulty patterns
- Evidence: van Tilborg 2022 showed all 24 ML methods struggle with activity cliffs
- Falsification: If non-cliff and cliff-adjacent molecules have identical error distributions

**Step 2: Molecule clustering → Cluster-specific thresholds**
- Mechanism: Split conformal prediction with cluster conditioning computes separate nonconformity score quantiles per group
- Evidence: Rakhshaninejad 2025 DTI paper demonstrates cluster-conditioned CP works for molecular data
- Falsification: If clusters are too small (<100 molecules), calibration becomes unreliable

**Step 3: Cluster-specific thresholds → Conditional coverage**
- Mechanism: Conformal prediction theory guarantees coverage when calibration and test distributions match within each cluster
- Evidence: CoDrug 2023 proves weighted conformal prediction maintains coverage under covariate shift
- Falsification: If scaffold splits show >10% coverage gap

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | van Tilborg 2022 (MoleculeACE) | Activity cliffs cause systematic ML failures across all 24 tested methods | Strong |
| Step2 → Step3 | Rakhshaninejad 2025 (DTI-CP) | Cluster-conditioned CP achieves tighter intervals and reliable subgroup coverage | Strong |
| Step3 → Outcome | CoDrug 2023 (NeurIPS) | Weighted conformal prediction reduces coverage gap by 35% under distribution shift | Strong |

**Key Tension:**
- **Tension:** CoDrug addresses covariate shift using density estimation, while CC-ACCP uses activity cliff proximity clustering. Both claim to improve coverage, but target different failure modes.
- **Resolution:** This verification plan tests whether activity cliff-specific clustering provides complementary or superior benefits to general covariate shift correction.

### 1.4 Key Assumptions

1. **Activity cliff identification assumption:**
   - Statement: Activity cliff pairs can be reliably identified using Tanimoto similarity threshold (>0.9 similarity, >100x potency difference)
   - Consequence if violated: Clustering would be based on noise, leading to random performance

2. **Calibration data sufficiency assumption:**
   - Statement: Sufficient calibration data exists per cluster (minimum ~100 molecules each)
   - Consequence if violated: Coverage guarantees become unreliable; intervals may be too wide or too narrow

3. **Cluster boundary generalization assumption:**
   - Statement: Cluster boundaries (0.4, 0.7 Tanimoto thresholds) generalize across different molecular targets
   - Consequence if violated: Would need target-specific threshold tuning, reducing practical utility

4. **Prediction difficulty correlation assumption:**
   - Statement: Activity cliff proximity is a meaningful predictor of model error
   - Consequence if violated: Clustering provides no information gain over random clustering

### 1.5 Scope & Boundaries

**Applies to:**
- Regression tasks on molecular property prediction (pIC50, pKi, Ki, EC50)
- Single-task molecular property prediction
- Datasets with identifiable activity cliff pairs

**Does NOT apply to:**
- Classification tasks, multi-task learning, generative design
- Datasets without activity cliff annotations

**Known Limitations:**
- Requires pre-computed activity cliff annotations
- Fixed cluster boundaries may not be optimal for all targets
- Does not address temporal distribution shift

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Coverage Gap vs CoDrug 35% baseline):**
CC-ACCP will achieve cluster-conditional coverage gap reduction >40% compared to standard conformal prediction, outperforming CoDrug's 35% coverage gap reduction on activity cliff-containing datasets.

*Measurement*:
- Coverage gap = |Target coverage (90%) - Empirical coverage|
- Statistical test: Paired t-test across 30 MoleculeACE datasets, n ≥ 25 runs
- Significance: p < 0.05

*Success Criteria*:
- Primary: Coverage gap reduction >40% (p < 0.05)
- Falsification: Coverage gap reduction ≤20% triggers rejection

**Secondary Predictions:**

**P2 (Cliff-Adjacent Cluster Coverage):**
The cliff-adjacent cluster will show the largest improvement in coverage compared to standard CP, with coverage gap reduction >50% in this subgroup.

**P3 (Interval Width Trade-off):**
Prediction intervals for cliff-adjacent molecules will be 20-50% wider than non-cliff molecules, reflecting appropriately higher uncertainty.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure**: Coverage gap reduction ≤20%
2. **Mechanism Failure**: Activity cliff proximity shows no correlation with prediction error (r < 0.1)
3. **Comparative Failure**: CC-ACCP performs worse than standard marginal CP on any cluster
4. **Generalization Failure**: Coverage gap exceeds 15% on scaffold-split evaluation

### 1.7 SOTA Baseline

| Method | Metric | Performance | Year |
|--------|--------|-------------|------|
| CoDrug | Coverage gap reduction | 35% | 2023 |
| Cluster-conditioned CP (DTI) | Subgroup coverage | Improved vs marginal CP | 2025 |
| Standard CP | Coverage gap | 0% (baseline) | - |

### 1.8 Statistical Verification Design

**Sample Size:** 30 MoleculeACE datasets × 5 random seeds = 150 experiments
**Statistical Test:** Paired t-test, α = 0.05 (one-tailed)
**Effect Size Target:** Cohen's d > 0.5 (medium)
**Report Format:** Mean difference, 95% CI, Cohen's d, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does activity cliff proximity correlate with molecular property prediction error?"
- Verification type: Empirical correlation analysis
- Critical: MUST PASS for Phase 2B to proceed

**SH2 (Mechanism):**
"Is activity cliff-aware clustering → cluster-specific calibration → conditional coverage the actual causal chain?"
- Phase 2B decomposes into 3 sub-hypotheses (H-M1, H-M2, H-M3)
- Verification type: Causal analysis with ablations

**SH3 (Comparison):**
"Does CC-ACCP outperform CoDrug and standard CP on coverage gap reduction?"
- Verification type: Comparative empirical on 30 datasets

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-CC-ACCP-v1)
- [x] Confidence level specified (0.84)
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=3 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] 3 testable predictions (primary marked)
- [x] 4 falsification criteria defined
- [x] Baselines identified (CoDrug, standard CP)
- [x] SH1, SH2, SH3 ready

### Open Questions

1. **Resource Requirements:** Standard GPU (~1 hour/dataset), MoleculeACE datasets (public), 2-3 weeks total
2. **Data Availability:** MoleculeACE (GitHub), Chemprop (open-source), MAPIE (conformal prediction)
3. **Priority Order:** SH1 (Existence) → SH2-M1 (Clustering) → SH3 (Comparison) → SH2-M2, SH2-M3 (Full mechanism)

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-12*
