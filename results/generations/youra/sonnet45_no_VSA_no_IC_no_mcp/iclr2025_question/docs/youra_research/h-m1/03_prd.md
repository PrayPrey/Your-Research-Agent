# Product Requirements Document: H-M1 Correlation Analysis

**Date:** 2026-08-25
**Hypothesis:** H-M1 (MECHANISM)
**Version:** 1.0

## Executive Summary

Implement statistical correlation analysis to test whether 10-sample overhead (O_10) correlates with full-dataset overhead (O_full) across 32 ML research hypotheses. Success threshold: r >0.7.

**Gate Type:** MUST_WORK (framework validity depends on result)

## Problem Statement

The Pilot-Driven Viability Gates framework assumes micro-pilot overhead predicts full-scale overhead. H-M1 tests this core assumption using the corpus from H-E1. Without correlation r >0.7, extrapolation from Gate 1 (10-sample micro-pilot) to full-scale predictions is invalid.

## Functional Requirements

### FR-1: Data Loading
Load retrospective corpus from H-E1 output:
- **Input:** `experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json`
- **Format:** JSON with 32 entries containing overhead_measurements
- **Fields:** micro_pilot.overhead_percent (O_10), full_scale.overhead_percent (O_full), hypothesis_type

### FR-2: Global Correlation Analysis
- Compute Pearson correlation r between O_10 and O_full arrays (n=32)
- Compute p-value for statistical significance (threshold p <0.05)
- Fit linear regression O_full = k × O_10 to get scaling factor k
- Calculate R² score for goodness of fit (target R² >0.5)

### FR-3: Per-Type Scaling Analysis
- Group corpus by hypothesis_type (attention, gradient, regularization, normalization)
- Fit per-type linear regressions: k_attention, k_gradient, k_regularization, k_normalization
- Compute coefficient of variation (CV) across k values
- Test consistency: CV <30% = consistent scaling, CV >50% = requires per-type calibration

### FR-4: Baseline Comparison
- Baseline model: r = 0 (null hypothesis, no correlation)
- Compare achieved r against baseline
- Test threshold: r >0.7 (success), 0.5 ≤ r <0.7 (explore non-linear), r <0.5 (abandon)

### FR-5: Visualization
Generate 3 required figures (saved to h-m1/figures/):
1. **Correlation Scatter Plot** (mandatory): O_10 vs O_full with regression line, colored by hypothesis_type
   - Annotate with r value and p-value
2. **Per-Type Scaling Factors**: Bar chart of k values by type
3. **Residual Plot**: Prediction error vs O_10 to check linearity assumption

## Data Specification

### Dataset: Retrospective ML Overhead Corpus v1.0
- **Source:** H-E1 validation output (local file)
- **Size:** 32 papers
- **Stratification:** Low=11, Mid=11, High=10 (CV=0.044)
- **Access:** Local file read (no download required)

## Non-Functional Requirements

### NFR-1: Statistical Validity
- Use scipy.stats.pearsonr for standard Pearson correlation
- Two-tailed p-value test at α=0.05 significance level

### NFR-2: Reproducibility
- Set random seed (not applicable for deterministic correlation)
- Document library versions: scipy, sklearn, numpy

### NFR-3: Performance
- Execution time <1 minute (statistical analysis on 32 data points)

## Success Criteria

### Primary: r >0.7
- Pearson correlation coefficient exceeds 0.7
- p-value <0.05 (statistically significant)

### Secondary: CV <30%
- Scaling factor k consistent across hypothesis types
- Coefficient of variation <30%

## Dependencies

### Python Packages
- scipy (pearsonr, stats)
- sklearn (LinearRegression, r2_score)
- numpy (array operations, std, mean)
- matplotlib (visualization)
- json (data loading)

### External Data
- H-E1 corpus: `experiments/h-e1_corpus_collection/data/retrospective_corpus/papers_metadata.json`

## Out of Scope

- Non-linear correlation models (only if 0.5 ≤ r <0.7)
- Per-hypothesis overhead prediction
- Calibration implementation (Phase 6 if needed)

## Acceptance Criteria

- [ ] Corpus loaded (32 entries verified)
- [ ] Global Pearson r >0.7 achieved
- [ ] p-value <0.05 (statistically significant)
- [ ] CV <30% for per-type scaling factors
- [ ] All 3 visualizations generated
- [ ] Results saved to 04_validation.md

## Phase 4 Guidance

**PoC Success Check:**
1. Code runs without error
2. r >0.7 (exceeds baseline r=0 and meets threshold)
3. p <0.05 (statistically significant)
4. CV <30% (consistent scaling)

**Failure Response:**
- IF r <0.5: ABANDON (mark gate.satisfied=false)
- IF 0.5 ≤ r <0.7: EXPLORE non-linear models (Phase 5 modification)
