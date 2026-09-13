# Product Requirements Document: H-M5

**Hypothesis:** Modality Divergence (Phase Transition Effect)
**Statement:** Post-2021 Pearson correlation between CV and NLP Gini series drops below 0.4 from pre-2020 baseline of >0.6
**Date:** 2026-08-18
**Author:** Anonymous
**Version:** 1.0

---

## Executive Summary

This PRD specifies the implementation requirements for validating hypothesis H-M5, which tests whether foundation model emergence caused modality-specific benchmark concentration dynamics to diverge. The experiment analyzes Pearson correlation between Computer Vision (CV) and Natural Language Processing (NLP) Gini coefficient time series across pre-2020 and post-2021 periods, using Fisher z-test to establish statistical significance of correlation drop.

**Success Criteria:** Pre-2020 correlation r > 0.6 (unified dynamics) AND post-2021 correlation r < 0.4 (diverged dynamics) AND Fisher z-test p < 0.05.

---

## Problem Statement

### Research Question
Did foundation model emergence cause benchmark concentration dynamics to fragment along modality lines?

### Background
Previous hypotheses (H-M1 through H-M4) established that foundation models emerged circa 2019-2021, emergent-capability benchmarks proliferated post-2020, researcher attention shifted to these new benchmarks, and traditional benchmarks persist with reduced dominance. H-M5 tests the final piece: whether these changes caused the previously unified benchmark ecosystem to fragment into modality-specific dynamics.

### Hypothesis Context
- **Type:** MECHANISM
- **Gate:** SHOULD_WORK
- **Prerequisites:** H-M4 (Traditional Benchmark Persistence with Reduced Dominance) - COMPLETED, PASS

---

## Functional Requirements

### FR-1: Data Loading and Preprocessing

**FR-1.1: Load PWC Dataset**
- Source: HuggingFace `pwc-archive/datasets`
- Method: `datasets.load_dataset("pwc-archive/datasets", split="train")`
- Output: Raw dataset records with task and temporal metadata

**FR-1.2: Modality Classification**
- Extract modality from task field using keyword matching:
  - CV: image, vision, object detection, segmentation
  - NLP: text, language, nlp, translation, summarization
  - Audio: audio, speech, sound
  - Tabular: tabular, structured
  - Other: unmatched tasks
- Output: Dataset with `modality` column

**FR-1.3: Temporal Aggregation**
- Aggregate benchmark usage counts by month and modality
- Time range: 2018-01 to 2024-12 (minimum)
- Output: Monthly counts per modality per benchmark

### FR-2: Gini Coefficient Computation

**FR-2.1: Per-Modality Gini Calculation**
- Compute Gini coefficient for benchmark usage distribution within each modality
- Formula: G = (2 * Σ(i * x_i)) / (n * Σx_i) - (n+1)/n
- Handle edge cases: empty counts → NaN, single benchmark → 0

**FR-2.2: Time Series Construction**
- Build monthly Gini series for CV, NLP, Audio, Tabular modalities
- Output: pandas DataFrame with DatetimeIndex, columns per modality
- Minimum 72 time points (6 years monthly)

### FR-3: Correlation Analysis

**FR-3.1: Period-Based Correlation**
- Pre-2020 period: All months before 2020-01
- Post-2021 period: All months from 2021-01 onwards
- Compute Pearson correlation between CV and NLP Gini series for each period

**FR-3.2: Rolling Correlation**
- Compute 6-month rolling window correlation between CV and NLP
- Output: Time series of correlation values for visualization

**FR-3.3: Fisher Z-Test**
- Compare pre-2020 vs post-2021 correlations using Fisher z-transformation
- z' = arctanh(r)
- z_stat = (z1 - z2) / sqrt(1/(n1-3) + 1/(n2-3))
- p-value from standard normal distribution

### FR-4: Baseline Model (Null Hypothesis)

**FR-4.1: Unified Concentration Model**
- Assumption: All modalities follow same concentration dynamics
- Expected: Correlation r > 0.5 between any modality pair throughout study period
- Implementation: Compute overall Gini (all modalities combined) as reference

### FR-5: Gate Evaluation

**FR-5.1: Success Criteria Check**
- Gate PASS requires ALL:
  1. r_pre > 0.6 (pre-2020 CV-NLP correlation)
  2. r_post < 0.4 (post-2021 CV-NLP correlation)
  3. Fisher z-test p < 0.05 (significant difference)

**FR-5.2: Failure Pivot**
- If gate fails, analyze domain-pair specific correlations:
  - CV-Audio, NLP-Audio, CV-Tabular, NLP-Tabular
  - Document which pairs diverged vs remained correlated

### FR-6: Visualization

**FR-6.1: Required Figure - Gate Metrics Comparison**
- Bar chart: r_pre vs r_post
- Horizontal threshold lines at 0.6 and 0.4
- Clear pass/fail indication

**FR-6.2: Rolling Correlation Time Series**
- Line plot of 6-month rolling CV-NLP correlation
- Vertical reference lines at 2020-01 and 2021-01
- X-axis: dates, Y-axis: correlation coefficient

**FR-6.3: Modality Gini Trajectories**
- Multi-line plot showing monthly Gini for each modality
- Color-coded by modality (CV, NLP, Audio, Tabular)
- Shared x-axis timeline

**FR-6.4: Correlation Heatmap**
- 2x2 or larger matrix showing all modality-pair correlations
- Separate panels for pre-2020 and post-2021 periods

---

## Non-Functional Requirements

### NFR-1: Performance
- Dataset loading: < 60 seconds
- Full analysis pipeline: < 5 minutes
- Memory usage: < 4GB RAM

### NFR-2: Reproducibility
- Fixed random seed where applicable
- Version-pinned dependencies
- Clear data provenance documentation

### NFR-3: Robustness
- Graceful handling of missing data (NaN in Gini series)
- Fallback for API timeouts (use cached data)
- Minimum sample size checks for statistical validity

---

## Data Specifications

### Input Data
| Field | Source | Type |
|-------|--------|------|
| Benchmark metadata | pwc-archive/datasets | JSON/Parquet |
| Task hierarchy | PWC task field | String |
| Temporal data | PWC date fields | Datetime |

### Output Data
| File | Content |
|------|---------|
| 04_validation.md | Validation report with metrics |
| figures/gate_metrics.png | Required gate visualization |
| figures/rolling_correlation.png | Correlation time series |
| figures/gini_trajectories.png | Modality Gini plots |

---

## Success Metrics

| Metric | Threshold | Description |
|--------|-----------|-------------|
| r_pre | > 0.6 | Pre-2020 CV-NLP correlation |
| r_post | < 0.4 | Post-2021 CV-NLP correlation |
| p_value | < 0.05 | Fisher z-test significance |
| n_pre | ≥ 24 | Pre-2020 sample size (months) |
| n_post | ≥ 36 | Post-2021 sample size (months) |

---

## Dependencies

### Software Dependencies
- Python 3.9+
- pandas >= 2.0
- numpy >= 1.24
- scipy >= 1.10
- matplotlib >= 3.7
- datasets (HuggingFace) >= 2.14

### Data Dependencies
- HuggingFace: pwc-archive/datasets
- Prerequisite: H-M4 validation (PASS)

### Upstream Dependencies
- Phase 2C: 02c_experiment_brief.md (COMPLETED)

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| PWC data incomplete | High | Semantic Scholar supplementation |
| Modality misclassification | Medium | Manual audit sample |
| Insufficient time points | Medium | Extend date range |
| Volume confound | High | Dual reporting (raw + normalized) |

---

## Appendix: Traceability to Phase 2C

| Phase 2C Item | PRD Coverage |
|---------------|--------------|
| PWC Dataset | FR-1.1 |
| Modality extraction | FR-1.2 |
| Gini computation | FR-2.1, FR-2.2 |
| Period correlations | FR-3.1 |
| Fisher z-test | FR-3.3 |
| Gate criteria | FR-5.1 |
| Visualizations | FR-6.1 - FR-6.4 |
| Failure pivot | FR-5.2 |

---

*Generated by Phase 3 Implementation Planning Workflow*
*Next: Architecture Design (03_architecture.md)*
