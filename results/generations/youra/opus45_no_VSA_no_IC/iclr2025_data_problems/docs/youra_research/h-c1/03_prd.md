# Product Requirements Document: h-c1

**Date:** 2026-08-24
**Hypothesis:** Mode profiles are stable within methods: split-half reliability Cronbach's alpha > 0.8
**Type:** CONDITION
**Gate:** SHOULD_WORK

---

## Executive Summary

This experiment measures the internal consistency (reliability) of mode profiles produced by each attribution method (TRAK, TracIn, Kronfluence). Using Cronbach's alpha on mode sensitivity scores from h-m1, we determine whether the 3-mode profile (memorization, feature transfer, spurious) is a stable measurement within each method.

---

## Problem Statement

h-m1 demonstrated that different attribution methods have different mode sensitivities. However, for these profiles to be scientifically meaningful, they must be stable (reliable). This experiment tests whether split-half reliability Cronbach's alpha > 0.8 for each method's mode profile.

---

## Functional Requirements

### FR-1: Data Loading (from h-m1)

**FR-1.1: Attribution Scores**
- Load attribution scores from h-m1 outputs
- Format: NPZ file with keys `{method}_{mode}` for each combination
- Shape: (1000,) per key (1000 probe pairs per mode)

**FR-1.2: Data Validation**
- Verify all 9 score arrays present (3 methods × 3 modes)
- Check for NaN/Inf values
- Confirm sample size ≥ 500 per array

### FR-2: Reliability Analysis

**FR-2.1: Mode Profile Matrix Construction**
- For each method: build (n_probes × 3) matrix
- Columns: memorization, feature_transfer, spurious scores
- Rows: probe pairs (subjects in psychometric terms)

**FR-2.2: Cronbach's Alpha Computation**
- Use pingouin.cronbach_alpha() for each method
- Return alpha value and 95% confidence interval
- Handle missing values with pairwise deletion

**FR-2.3: Item-Total Correlations**
- Compute correlation of each mode with total score
- Identifies which modes contribute most to reliability

### FR-3: Success Evaluation

**FR-3.1: Gate Check**
- Pass: alpha > 0.8 for all 3 methods
- Fail: any alpha < 0.8
- Record exact values and CIs

### FR-4: Visualization

**FR-4.1: Gate Metrics Comparison (Required)**
- Bar chart: Cronbach's alpha per method
- Error bars: 95% CI
- Threshold line at alpha = 0.8

**FR-4.2: Additional Figures (Autonomous)**
- Reliability heatmap (mode × method item-total correlations)
- Alpha-if-dropped analysis per method

---

## Non-Functional Requirements

### NFR-1: Dependencies
- pingouin for Cronbach's alpha
- pandas, numpy for data handling
- matplotlib/seaborn for visualization

### NFR-2: Determinism
- Cronbach's alpha is deterministic given data
- No random seeds needed

### NFR-3: Modularity
- Separate data loading from analysis
- Reusable reliability functions

---

## Success Criteria

| Criterion | Threshold |
|-----------|-----------|
| Code runs without error | No runtime exceptions |
| Alpha computed for all methods | 3 valid alpha values |
| Gate pass | All alphas > 0.8 |

---

## Dependencies

### External Libraries
- pingouin (pip install pingouin)
- pandas, numpy
- matplotlib, seaborn

### Data Dependencies
- h-m1/outputs/attribution_scores.npz (from prerequisite)

---

## Constraints

- Task Budget: SIMPLIFIED tier (statistical analysis only)
- Epic Range: 3-5 epics
- No neural network training required

---

*Generated from Phase 2C experiment brief: 02c_experiment_brief.md*
