# PRD: h-m2 Pareto-Optimal ECE Analysis

**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Gate:** SHOULD_WORK
**Date:** 2026-08-28

---

## 1. Executive Summary

Validate whether Pareto-optimal models (those not dominated on both TruthfulQA and AdvGLUE) exhibit significantly better calibration (lower ECE) than non-Pareto models.

---

## 2. Problem Statement

H-E1 established positive correlation between TruthfulQA and AdvGLUE. This hypothesis tests a mechanism: do models at the Pareto frontier of this tradeoff space also demonstrate superior calibration?

---

## 3. Functional Requirements

### FR-1: Data Loading
- Load h-e1 results from `h-e1/code/results/scores.csv`
- Required columns: model, family, params, truthfulqa_mc1, advglue_avg

### FR-2: Pareto Frontier Identification
- Implement O(n²) dominance check algorithm
- Model is Pareto-optimal if no other model dominates on BOTH metrics
- Expected: 4-6 models on frontier, 8-10 non-Pareto

### FR-3: ECE Computation
- 15-bin Expected Calibration Error
- Reuse h-m1/code/ece.py if available, else implement synthetic ECE
- ECE range [0,1], lower = better calibration

### FR-4: Statistical Analysis
- Welch's t-test (unequal variances)
- Compare Pareto vs non-Pareto ECE distributions
- Report: t-statistic, p-value, means, Cohen's d

### FR-5: Visualization
- Pareto frontier scatter plot (TruthfulQA vs AdvGLUE)
- ECE comparison box plot by group

### FR-6: Baseline Comparisons
- Random split baseline (compare ECE between random halves)
- Size-matched control (control for model params)

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- Runtime < 30 seconds (synthetic ECE)

### NFR-2: Dependencies
- numpy, pandas, scipy, matplotlib only
- No GPU required

### NFR-3: Reproducibility
- Fixed random seed for synthetic ECE

---

## 5. Success Criteria

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| t-test p-value | < 0.05 | Significant difference |
| Mean ECE (Pareto) | < Mean ECE (non-Pareto) | Pareto models better calibrated |
| N (Pareto) | >= 3 | Sufficient sample |
| N (non-Pareto) | >= 5 | Sufficient sample |
| Cohen's d | > 0.5 | Medium+ effect size |

---

## 6. Data Sources

| Source | Type | Path |
|--------|------|------|
| h-e1 scores | derived | h-e1/code/results/scores.csv |
| ECE values | computed | per-model 15-bin ECE |

---

## 7. Risks

| Risk | Probability | Mitigation |
|------|-------------|------------|
| Small sample (N=14) | High | Report effect size alongside p-value |
| Synthetic ECE | High | Document as PoC |
| Pareto frontier too small | Medium | Relaxed criterion if <3 models |

---

*PRD Complete - Ready for Architecture*
