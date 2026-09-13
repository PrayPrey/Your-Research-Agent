# Product Requirements Document: h-e1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis:** Rankings shift significantly between ImageNet and ImageNet-V2 (Kendall-τ < 0.90 with p < 0.001)
**Type:** EXISTENCE (PoC)

---

## Executive Summary

This experiment validates whether ImageNet model rankings shift significantly when evaluated on ImageNet-V2. The core hypothesis is that Kendall-τ correlation between rankings drops below 0.90 with statistical significance (p < 0.001), demonstrating that benchmark choice materially affects model comparisons.

**Scope:** Statistical analysis of published accuracy data (no model training required).

---

## Problem Statement

Current ML research assumes ImageNet rankings generalize. If rankings shift significantly on ImageNet-V2, conclusions about "best models" may be benchmark-dependent rather than reflecting true generalization ability.

**Success Metric:** Kendall-τ < 0.90 with p < 0.001

---

## Functional Requirements

### FR-1: Data Collection
- Fetch ImageNet top-1 accuracy data from Papers With Code API
- Fetch ImageNet-V2 top-1 accuracy data from Papers With Code API
- Merge datasets on model name
- Minimum 30 models with both benchmarks

### FR-2: Ranking Computation
- Compute rankings for each benchmark (higher accuracy = rank 1)
- Handle ties using standard rank method

### FR-3: Statistical Analysis
- Compute Kendall-τ correlation between rankings
- Compute p-value for correlation significance
- Bootstrap 95% confidence intervals (10,000 iterations)

### FR-4: Hypothesis Testing
- Test: τ < 0.90 with p < 0.001
- Report CI upper bound < 0.95 as supporting evidence

### FR-5: Visualization
- Ranking scatter plot (ImageNet rank vs V2 rank)
- Accuracy drop histogram
- Gate metrics comparison bar chart

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seed for bootstrap
- All data sources documented
- Code produces identical results on re-run

### NFR-2: Statistical Rigor
- Minimum n=30 for statistical power
- Two-sided p-value from scipy.stats.kendalltau
- Percentile method for bootstrap CI

---

## Data Specifications

| Dataset | Source | Format | Size |
|---------|--------|--------|------|
| ImageNet Leaderboard | Papers With Code API | JSON/CSV | ~200 models |
| ImageNet-V2 Leaderboard | Papers With Code API | JSON/CSV | ~100 models |
| Merged Dataset | Computed | DataFrame | ≥30 models |

**Required Fields:**
- `model_name`: str
- `imagenet_top1`: float (0-100)
- `imagenet_v2_top1`: float (0-100)
- `architecture_family`: str (optional, for h-m3)

---

## Success Criteria

| Metric | Threshold | Priority |
|--------|-----------|----------|
| Kendall-τ | < 0.90 | Primary (Gate) |
| p-value | < 0.001 | Primary (Gate) |
| 95% CI upper | < 0.95 | Secondary |
| Sample size | ≥ 30 | Prerequisite |

---

## Dependencies

- Python 3.8+
- scipy >= 1.7.0
- pandas >= 1.3.0
- numpy >= 1.20.0
- matplotlib >= 3.4.0
- requests >= 2.25.0

---

## Out of Scope

- Model training or fine-tuning
- New model architectures
- ImageNet-V2 dataset download (using published accuracy values only)
- Real-time inference

---

## Timeline

| Phase | Duration | Output |
|-------|----------|--------|
| Data Collection | 1 hour | merged_rankings.csv |
| Statistical Analysis | 30 min | kendall_results.json |
| Visualization | 30 min | figures/*.png |
| Total | ~2 hours | 04_validation.md |

---

*Generated for Phase 3 Implementation Planning*
