# Product Requirements Document: h-m2

**Date:** 2026-08-28
**Hypothesis:** Pre-2019 DNSI (computed on 2009-2018 SOTA data) predicts post-2019 generalization gap measurements with R² > 0.3
**Type:** MECHANISM (Temporal Prediction)
**Phase:** 3 - Implementation Planning

---

## Executive Summary

This experiment tests whether DNSI computed on historical SOTA data (2009-2018) predicts future generalization gaps measured after 2019. Success (R² > 0.3) would demonstrate DNSI's predictive utility for anticipating benchmark saturation effects.

---

## Problem Statement

Current benchmark evaluation treats accuracy metrics in isolation. DNSI (validated in h-e1) captures cumulative improvement entropy. If pre-2019 DNSI predicts post-2019 gaps, researchers could identify benchmarks approaching saturation before new test sets are created.

---

## Functional Requirements

### FR-1: Data Preparation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1 | Load SOTA histories from h-e1 data cache | MUST |
| FR-1.2 | Apply temporal filter (cutoff: 2019-01-01) | MUST |
| FR-1.3 | Compute pre-2019 DNSI for 4 benchmarks | MUST |
| FR-1.4 | Load post-2019 gap ground truth from published papers | MUST |

### FR-2: Temporal DNSI Computation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1 | Extend h-e1 DNSIComputer with cutoff_date parameter | MUST |
| FR-2.2 | Filter SOTA entries before computing windowed improvements | MUST |
| FR-2.3 | Require minimum 5 years pre-cutoff history | SHOULD |
| FR-2.4 | Return None for insufficient data | MUST |

### FR-3: Regression Analysis

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1 | OLS regression: pre-2019 DNSI (X) → post-2019 gap (Y) | MUST |
| FR-3.2 | Compute R² and adjusted R² | MUST |
| FR-3.3 | Bootstrap R² with 10,000 iterations | MUST |
| FR-3.4 | Leave-one-out cross-validation R² | MUST |
| FR-3.5 | Report 95% confidence interval | MUST |

### FR-4: Evaluation Pipeline

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1 | Primary metric: R² > 0.3 = PASS | MUST |
| FR-4.2 | Secondary: LOO-CV R² > 0.1 | SHOULD |
| FR-4.3 | Verify negative slope (expected direction) | SHOULD |
| FR-4.4 | Gate: R² < 0.1 = FAIL (SHOULD_WORK) | MUST |

### FR-5: Visualization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1 | Scatter plot: DNSI vs Gap with regression line | MUST |
| FR-5.2 | Bootstrap R² distribution histogram | SHOULD |
| FR-5.3 | LOO prediction vs actual chart | SHOULD |

---

## Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Reproducibility | Fixed random seed for bootstrap |
| NFR-2 | Performance | Complete analysis in < 60 seconds |
| NFR-3 | Compatibility | Reuse h-e1 data structures |
| NFR-4 | Robustness | Handle missing/insufficient data gracefully |

---

## Data Specifications

### Input Data

| Source | Format | Location |
|--------|--------|----------|
| SOTA Histories | JSON | h-e1/code/data/pwc/*.json |
| Gap Ground Truth | Python dict | Hardcoded from papers |

### Gap Ground Truth (from literature)

| Benchmark | Gap | Source |
|-----------|-----|--------|
| ImageNet | 12.5% | Recht et al. 2019 |
| CIFAR-10 | 4.0% | Recht et al. 2019 |
| CIFAR-100 | 5.0% | Recht (scaled) |
| ObjectNet | 42.5% | Barbu et al. 2019 |

---

## Success Criteria

| Criterion | Threshold | Gate Type |
|-----------|-----------|-----------|
| R² | > 0.3 | SHOULD_WORK |
| LOO-CV R² | > 0.1 | Informational |
| CI lower bound | > 0.1 | Informational |
| Slope direction | Negative | Expected |

### Failure Criteria

- R² < 0.1 → Gate FAILS (no predictive relationship)

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| h-e1 validation | Prerequisite | COMPLETED |
| h-e1 DNSI code | Code reuse | Available |
| scipy, sklearn | Library | Standard |
| numpy | Library | Standard |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Small N (n=4) | HIGH | Bootstrap CI, LOO-CV, frame as pilot |
| Overfitting | MODERATE | LOO-CV provides honest estimate |
| Temporal boundary | LOW | Fixed cutoff, all gaps published 2019+ |

---

## Implementation Notes

- Extend TemporalDNSIComputer from h-e1 DNSIComputer
- Single main.py script with TemporalPredictionAnalyzer class
- Output: JSON results + PNG figures + markdown report
