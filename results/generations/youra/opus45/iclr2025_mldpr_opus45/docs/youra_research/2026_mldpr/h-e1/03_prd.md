# Product Requirements Document: h-e1

**Hypothesis:** DTW-based Time Series Clustering of HuggingFace Dataset Download Trajectories
**Date:** 2026-03-27
**Author:** Anonymous
**Version:** 1.0
**Status:** Draft

---

## Executive Summary

This PRD defines the requirements for implementing hypothesis h-e1: validating the existence of meaningful clustering structure in HuggingFace dataset download trajectories using DTW-based TimeSeriesKMeans clustering. This is a foundational EXISTENCE hypothesis with a MUST_WORK gate that determines whether the entire verification chain can proceed.

**Key Objective:** Demonstrate that HuggingFace datasets partition into 3-8 distinct trajectory clusters with silhouette score >0.25 and bootstrap Jaccard stability >0.65.

---

## Problem Statement

### Background
The HuggingFace ecosystem hosts thousands of datasets with varying adoption patterns. Understanding these patterns requires identifying recurring trajectory archetypes in download dynamics. Before exploring mechanisms (why patterns exist), we must first establish that meaningful clustering structure exists at all.

### Problem Definition
There is currently no validated evidence that HuggingFace dataset download trajectories exhibit meaningful clustering structure. Without this foundation, subsequent hypotheses about lifecycle phases and adoption mechanisms cannot be tested.

### Impact
- **If clustering exists:** Enables hierarchical taxonomy research (H-M1, H-M2, H-M3)
- **If clustering fails:** Entire research direction must be reconsidered

---

## Functional Requirements

### FR-1: Data Collection Module

**FR-1.1: HuggingFace API Integration**
- Query HuggingFace Hub API for all datasets
- Extract dataset metadata (creation date, download counts)
- Collect monthly download time series
- **Implementation:** `huggingface_hub.HfApi()`

**FR-1.2: Dataset Filtering**
- Filter datasets created between 2020-2024
- Require minimum 12 months of download history
- Require minimum 100 total downloads
- Target population: >= 500 qualifying datasets

**FR-1.3: Data Quality Validation**
- Validate < 10% missing values per series
- Handle monotonicity validation for cumulative downloads
- Log data quality metrics

### FR-2: Preprocessing Pipeline

**FR-2.1: Log Transformation**
- Apply `np.log1p(downloads)` to handle exponential growth
- Preserve zero values safely

**FR-2.2: Normalization**
- Apply Z-score normalization using `TimeSeriesScalerMeanVariance()`
- Handle variable-length series via tslearn padding

**FR-2.3: Format Conversion**
- Convert to tslearn 3D format: (n_samples, max_len, 1)
- Use `to_time_series_dataset()` for conversion

### FR-3: Baseline Model Implementation

**FR-3.1: Feature Extraction**
- Extract summary statistics: mean, std, trend slope
- Compute trend via linear regression coefficient

**FR-3.2: K-Means Clustering**
- Implement `sklearn.cluster.KMeans` on summary features
- Run for k in range [3, 8]
- Record silhouette scores for comparison

### FR-4: Proposed Model Implementation

**FR-4.1: DTW TimeSeriesKMeans**
- Implement `tslearn.clustering.TimeSeriesKMeans`
- Use `metric="dtw"` for shape-based clustering
- Parameters: `max_iter=10`, `n_init=2`, `random_state=42`

**FR-4.2: Optimal k Selection**
- Iterate k from 3 to 8
- Compute silhouette score for each k
- Select k with maximum silhouette score

**FR-4.3: Bootstrap Stability**
- Implement 100-iteration bootstrap
- Sample 80% of data with replacement
- Compute Jaccard similarity between original and bootstrap assignments
- Report mean Jaccard stability score

### FR-5: Evaluation Module

**FR-5.1: Primary Metrics**
| Metric | Threshold | Required |
|--------|-----------|----------|
| Silhouette Score | > 0.25 | Yes |
| Optimal k | in [3, 8] | Yes |

**FR-5.2: Secondary Metrics**
| Metric | Threshold | Required |
|--------|-----------|----------|
| Bootstrap Jaccard | > 0.65 | Yes |

**FR-5.3: Comparison Metrics**
- DTW silhouette vs Baseline silhouette
- Report improvement percentage

### FR-6: Visualization Requirements

**FR-6.1: Required Figures (Mandatory)**
- Gate Metrics Comparison: Bar chart showing silhouette score vs threshold (0.25)

**FR-6.2: Additional Figures (Autonomous)**
- Silhouette Analysis Plot: Score vs number of clusters (k)
- Cluster Centroids: Time series plot of cluster centers
- Cluster Distribution: Histogram of cluster sizes
- t-SNE Visualization: 2D projection of clustered trajectories

**FR-6.3: Figure Output**
- Save all figures to `h-e1/figures/` directory
- Use PNG format with 300 DPI
- Include descriptive titles and axis labels

### FR-7: Results Persistence

**FR-7.1: Metrics Output**
- Save results to `h-e1/04_validation.md`
- Include all metric values with pass/fail status
- Record execution timestamp and seed

**FR-7.2: Model Artifacts**
- Save cluster centers
- Save cluster labels
- Save preprocessing parameters

---

## Non-Functional Requirements

### NFR-1: Performance
- Complete full pipeline in < 30 minutes on single GPU
- Handle >= 500 time series efficiently

### NFR-2: Reproducibility
- Fixed random seed (42) for all stochastic operations
- Log all hyperparameters and preprocessing steps

### NFR-3: Code Quality
- Type hints for all functions
- Docstrings with parameter descriptions
- Modular design with clear separation of concerns

### NFR-4: Error Handling
- Graceful handling of API rate limits
- Logging of all errors with context
- Checkpoint capability for long-running operations

---

## Technical Specifications

### Dependencies
```
tslearn>=0.6.0
scikit-learn>=1.0.0
huggingface_hub>=0.20.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

### Hardware Requirements
- Single GPU (optional, DTW is CPU-based)
- Minimum 16GB RAM for large dataset handling

### API Dependencies
- HuggingFace Hub API (public, rate-limited)

---

## Success Criteria

### Gate Condition: MUST_WORK

**Pass Criteria (ALL must be true):**
1. `silhouette_score > 0.25`
2. `optimal_k in [3, 8]`
3. `jaccard_stability > 0.65`

**Consequence of Failure:**
- STOP entire verification chain
- Route to Phase 0 for hypothesis reassessment

### Mechanism Verification
- Model has `cluster_centers_` attribute (fitted)
- Clustering produces measurable separation (silhouette > 0)
- DTW approach >= 90% of baseline performance

---

## Data Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  HuggingFace    │────▶│  Preprocessing   │────▶│  DTW Clustering │
│  API Collection │     │  (log + z-score) │     │  (k in [3,8])   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Validation     │◀────│  Bootstrap       │◀────│  Silhouette     │
│  Report         │     │  Stability       │     │  Evaluation     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## Acceptance Criteria

### AC-1: Data Collection
- [ ] Successfully queries HuggingFace API
- [ ] Filters >= 500 qualifying datasets
- [ ] Extracts complete download time series

### AC-2: Preprocessing
- [ ] Log transformation applied correctly
- [ ] Z-score normalization with zero mean, unit variance
- [ ] Converted to tslearn format

### AC-3: Clustering
- [ ] DTW TimeSeriesKMeans runs without error
- [ ] Iterates through k = [3, 4, 5, 6, 7, 8]
- [ ] Selects optimal k by silhouette

### AC-4: Evaluation
- [ ] Silhouette score computed correctly
- [ ] Bootstrap Jaccard stability computed
- [ ] All metrics logged with thresholds

### AC-5: Visualization
- [ ] All required figures generated
- [ ] Saved to h-e1/figures/

### AC-6: Gate Validation
- [ ] Pass/Fail determination based on thresholds
- [ ] Results written to 04_validation.md

---

## Traceability

| Requirement | Source |
|-------------|--------|
| Silhouette > 0.25 | Phase 2B hypothesis specification |
| k in [3, 8] | Phase 2B hypothesis specification |
| Jaccard > 0.65 | Phase 2B hypothesis specification |
| DTW metric | Literature (Aghabozorgi et al., 2015) |
| tslearn implementation | Phase 2C GitHub research |
| Bootstrap 100x | Phase 2B success criteria |

---

## Appendix

### A. Phase 2C Reference
- Source: `h-e1/02c_experiment_brief.md`
- Contains: Full experiment specification with pseudo-code

### B. Hypothesis Chain
```
h-e1 (EXISTENCE) ──▶ h-m1 (MECHANISM) ──▶ h-m2 (MECHANISM) ──▶ h-m3 (MECHANISM)
     │                    │                    │                    │
  MUST_WORK           MUST_WORK           SHOULD_WORK          SHOULD_WORK
```

---

*Generated by Phase 3 Implementation Planning*
*Source: Phase 2C Experiment Brief (h-e1/02c_experiment_brief.md)*
