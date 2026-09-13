# Product Requirements Document: H-E1

**Hypothesis:** PELT change-point detection identifies statistically significant change point in aggregate Gini coefficient time series within 2019-2022 window at α=0.05

**Date:** 2026-08-18
**Type:** EXISTENCE (Proof of Concept)
**Tier:** LIGHT (max 15 tasks)

---

## 1. Executive Summary

This experiment validates whether a statistically significant structural break exists in benchmark concentration (measured by Gini coefficient) during 2019-2022. Using PELT change-point detection on Papers With Code historical data, we test if the foundation model emergence period shows measurable disruption in benchmark usage patterns.

**Success Criteria:**
- Change point detected in 2019-2022 window
- BIC(segmented model) < BIC(monotonic model)
- p-value < 0.05 for model comparison

---

## 2. Problem Statement

Existing research (Koch et al. 2021) reports Gini coefficient ~0.6-0.7 for benchmark concentration 2015-2020, but does not test for structural breaks coinciding with foundation model emergence. We need to verify whether a phase transition occurred.

---

## 3. Functional Requirements

### FR-1: Data Pipeline
- **FR-1.1**: Load Papers With Code evaluation tables from HuggingFace
- **FR-1.2**: Parse task-dataset-metric triplets with timestamps
- **FR-1.3**: Filter to 2018-01-01 through 2024-12-31
- **FR-1.4**: Aggregate to monthly benchmark usage counts
- **FR-1.5**: Compute monthly Gini coefficient of benchmark distribution

### FR-2: Baseline Model (H0)
- **FR-2.1**: Fit single linear trend to entire 2018-2024 Gini series
- **FR-2.2**: Calculate R², residuals, BIC for monotonic model

### FR-3: Proposed Model (H1)
- **FR-3.1**: Apply PELT algorithm with RBF kernel (ruptures library)
- **FR-3.2**: Use BIC-based penalty selection: `pen = log(n) * variance(signal)`
- **FR-3.3**: Minimum segment length: 3 months
- **FR-3.4**: Fit segmented linear trends to each segment
- **FR-3.5**: Calculate BIC for segmented model

### FR-4: Statistical Validation
- **FR-4.1**: Check if change point falls in 2019-2022 (indices 12-48)
- **FR-4.2**: Compare BIC: segmented < monotonic
- **FR-4.3**: Report significance level

### FR-5: Ablation Variants
- **FR-5.1**: PELT model variants: `"rbf"` (primary), `"l1"`, `"l2"`
- **FR-5.2**: Penalty sensitivity: ±20% around BIC-optimal

### FR-6: Visualization
- **FR-6.1**: Gini time series with detected change points marked
- **FR-6.2**: Segmented vs monotonic fit comparison
- **FR-6.3**: Gate metrics bar chart (primary/secondary thresholds)

---

## 4. Data Specification

### Primary Dataset
- **Name**: Papers With Code Evaluation Tables
- **Source**: `pwc-archive/evaluation-tables` (HuggingFace)
- **Format**: JSON with task-dataset-metric-paper associations
- **Size**: ~326,000 evaluation table rows
- **Time Range**: 2018-2024 (monthly aggregation)
- **Output**: ~72 monthly Gini values

### Loading Code
```python
from datasets import load_dataset
eval_tables = load_dataset("pwc-archive/evaluation-tables")
```

---

## 5. Non-Functional Requirements

- **NFR-1**: Experiment completes in <10 minutes on standard hardware
- **NFR-2**: All results reproducible (PELT is deterministic)
- **NFR-3**: Figures saved to `{hypothesis_folder}/figures/`

---

## 6. Success Criteria

| Metric | Threshold | Type |
|--------|-----------|------|
| Change point in 2019-2022 | Required | Gate |
| BIC improvement | segmented < monotonic | Gate |
| p-value | < 0.05 | Secondary |

---

## 7. Dependencies

### 7.1 Python Packages
- ruptures>=1.1.0 (PELT implementation)
- scipy>=1.9.0 (statistics)
- numpy>=1.21.0 (numerical)
- pandas>=1.4.0 (data handling)
- matplotlib>=3.5.0 (visualization)
- datasets>=2.0.0 (HuggingFace loader)

### 7.2 Reference Implementations
- ruptures: https://github.com/deepcharles/ruptures
- Gini coefficient: pysal.inequality or custom implementation

---

## 8. Constraints

- EXISTENCE experiment: single run sufficient (no randomness)
- LIGHT tier: max 15 implementation tasks
- No GPU required (statistical analysis only)
