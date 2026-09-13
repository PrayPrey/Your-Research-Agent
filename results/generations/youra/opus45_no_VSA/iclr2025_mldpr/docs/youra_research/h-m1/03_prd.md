# Product Requirements Document: h-m1

**Hypothesis:** Preprocessing entropy mediates ≥30% of the metadata→variance effect; preprocessing entropy differs across metadata quartiles while model hyperparameter entropy does not

**Type:** MECHANISM
**Date:** 2026-08-09
**Author:** Anonymous

---

## Executive Summary

This document specifies requirements for implementing a mediation analysis to test whether preprocessing entropy is the causal mechanism through which metadata completeness reduces reproducibility variance. Building on h-e1's validated finding (42.1% IQR reduction), this experiment tests whether preprocessing entropy mediates ≥30% of that effect.

---

## Problem Statement

h-e1 established that metadata completeness correlates with reduced reproducibility variance. However, correlation does not establish mechanism. This hypothesis tests whether preprocessing entropy (the diversity of preprocessing approaches used across runs) is the causal mediator: better metadata → more consistent preprocessing → lower variance.

**Null Hypothesis:** Preprocessing entropy does not mediate the metadata→variance relationship (indirect effect <15% or p>0.10).

---

## Functional Requirements

### FR-1: Data Collection Module

**FR-1.1:** Query OpenML API for datasets with ≥10 matched runs (same flow, same hyperparameters)
**FR-1.2:** Compute metadata completeness score using 5-field checklist (description, attribute info, version, license, creator)
**FR-1.3:** Extract preprocessing components from flow descriptions
**FR-1.4:** Compute reproducibility variance (IQR) across matched runs

### FR-2: Entropy Computation Module

**FR-2.1:** Compute preprocessing entropy (H_prep) as Shannon entropy of preprocessing component distribution
**FR-2.2:** Compute hyperparameter entropy (H_hyp) as Shannon entropy of hyperparameter value distribution
**FR-2.3:** Handle edge cases (empty lists → entropy = 0)

### FR-3: Mediation Analysis Module

**FR-3.1:** Implement mediation analysis using pingouin.mediation_analysis
**FR-3.2:** Include controls: intrinsic stability, popularity, algorithm family
**FR-3.3:** Bootstrap CI computation (n_boot=1000, seed=42)
**FR-3.4:** Compute indirect effect, total effect, proportion mediated

### FR-4: Sub-prediction Tests

**FR-4.1:** P2a test: Compare H_prep across metadata quartiles (t-test Q4 vs Q1)
**FR-4.2:** P2b test: Compare H_hyp across metadata quartiles (expect NS, p>0.10)

### FR-5: Visualization Module

**FR-5.1:** Generate mediation path diagram with effect sizes and CIs
**FR-5.2:** Generate box plots of H_prep by metadata quartile
**FR-5.3:** Generate box plots of H_hyp by metadata quartile
**FR-5.4:** Generate bootstrap distribution histogram
**FR-5.5:** Save all figures to h-m1/figures/

---

## Non-Functional Requirements

### NFR-1: Statistical Rigor
- Bootstrap iterations: 1000 minimum
- Random seed: 42 (fixed for reproducibility)
- Significance level: alpha=0.05

### NFR-2: Sample Size
- Minimum 200 datasets (from h-e1 validation)
- Use full OpenML dataset meeting criteria (no arbitrary subsampling)

### NFR-3: Dependencies
- pingouin>=0.6.1
- statsmodels>=0.14.1
- scipy>=1.10.0
- openml>=0.14.0
- pandas, numpy, matplotlib

---

## Success Criteria

### Primary Gate (MUST_WORK)
| Metric | Threshold | Falsification |
|--------|-----------|---------------|
| Proportion Mediated | ≥30% | <15% |
| Indirect Effect p-value | <0.05 | >0.10 |
| Sobel Z | \|Z\|>1.96 | \|Z\|<1.96 |

### Sub-predictions
| ID | Test | Success | Failure |
|----|------|---------|---------|
| P2a | H_prep(Q4) vs H_prep(Q1) | ≥30% reduction, p<0.05 | p>0.10 |
| P2b | H_hyp(Q4) vs H_hyp(Q1) | NS (p>0.10) | p<0.05 |

---

## Dependencies

### Upstream
- h-e1: VALIDATED (provides existence confirmation)
- Phase 2C: COMPLETED (provides experiment design)

### Downstream
- h-c1, h-c2: Blocked until h-m1 passes MUST_WORK gate

---

## Data Flow

```
OpenML API → Data Collection → Entropy Computation → Mediation Analysis → Results
                                                   ↓
                                            Visualization
```

---

## Acceptance Criteria

1. Code runs without error on full OpenML dataset
2. Mediation analysis produces valid statistics (no NaN/Inf)
3. Proportion mediated ≥30% with p<0.05
4. Sub-prediction P2a shows significant difference
5. Sub-prediction P2b shows non-significant difference
6. All required figures generated and saved
