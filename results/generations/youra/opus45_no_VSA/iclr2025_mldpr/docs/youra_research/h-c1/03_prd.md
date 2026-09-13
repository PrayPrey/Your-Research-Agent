# Product Requirements Document: h-c1

**Date:** 2026-08-09
**Author:** YouRA Research Pipeline
**Hypothesis:** The metadata-variance effect persists in first-50-runs subsample (within 90 days of dataset upload), ruling out reverse causality from community convergence
**Phase:** Implementation Planning (Phase 3)

---

## Executive Summary

This PRD defines requirements for h-c1, a temporal robustness check validating that the metadata-completeness effect observed in h-e1 persists in early-run subsamples. By restricting analysis to the first 50 runs within 90 days of dataset upload, we test whether the effect exists before community convergence could artificially reduce variance—ruling out reverse causality.

**Key Deliverables:**
1. Temporal subsample filter for OpenML runs
2. Recomputed IQR analysis on filtered data
3. Effect persistence comparison (early vs full sample)
4. Statistical validation report

---

## Problem Statement

### Background
h-e1 established that metadata completeness correlates with reduced reproducibility variance (42.1% IQR reduction). However, an alternative explanation exists: over time, the ML community converges on optimal preprocessing, reducing variance naturally while also improving metadata quality. This would create correlation without metadata being causal.

### Goal
Demonstrate that the metadata effect persists in early runs (before community convergence possible), thereby ruling out reverse causality.

### Success Criteria
| Criterion | Threshold |
|-----------|-----------|
| Early-run relative IQR reduction | ≥20% |
| Effect persistence ratio | ≥50% of h-e1 effect |
| Statistical significance | p < 0.05 |

---

## Functional Requirements

### FR-1: Data Loading (REUSE from h-e1)
**Priority:** P0
**Description:** Load h-e1 processed dataset with run-level accuracy scores and metadata completeness scores.

**Acceptance Criteria:**
- Load `h-e1/results/analysis_dataset.parquet`
- Verify columns: `data_id`, `run_id`, `upload_time`, `accuracy`, `metadata_completeness_score`
- Minimum 500 datasets with ≥5 runs each

### FR-2: Temporal Subsample Filter
**Priority:** P0
**Description:** Filter runs to first 50 within 90 days of dataset upload.

**Acceptance Criteria:**
- Input: Full run dataset with `upload_time` and dataset `upload_date`
- Filter: `days_since_upload <= 90` AND rank within dataset ≤ 50
- Output: Filtered DataFrame with same schema
- Logging: Report filter statistics (datasets retained, runs retained, compression ratio)

### FR-3: Sample Size Validation
**Priority:** P0
**Description:** Verify sufficient sample size after filtering.

**Acceptance Criteria:**
- Minimum 100 datasets with ≥5 matched runs in early window
- If threshold not met: WARNING with actual counts, proceed anyway

### FR-4: IQR Computation on Subsample
**Priority:** P0
**Description:** Recompute IQR per dataset on filtered runs.

**Acceptance Criteria:**
- Use same `compute_reproducibility_iqr()` function as h-e1
- Output: DataFrame with `data_id`, `iqr_early`, `metadata_quartile`

### FR-5: Quartile Effect Analysis
**Priority:** P0
**Description:** Compare bottom vs top metadata quartile IQR in early runs.

**Acceptance Criteria:**
- Compute mean IQR for Q1 (low metadata) vs Q4 (high metadata)
- Compute relative reduction: `(IQR_Q1 - IQR_Q4) / IQR_Q1 * 100`
- Bootstrap 95% CI with 1000 iterations

### FR-6: Effect Persistence Comparison
**Priority:** P0
**Description:** Compare early-run effect to h-e1 full-sample effect.

**Acceptance Criteria:**
- Load h-e1 effect: 42.1% relative IQR reduction
- Compute persistence ratio: `early_effect / full_effect`
- PASS if ratio ≥ 0.5 (effect ≥ 21%)

### FR-7: Results Export
**Priority:** P0
**Description:** Export results to standard format.

**Acceptance Criteria:**
- JSON: `h-c1/results/h_c1_effects.json`
- Fields: `early_run_effect_pct`, `full_sample_effect_pct`, `persistence_ratio`, `p_value`, `pass`

### FR-8: Visualization
**Priority:** P1
**Description:** Generate comparison figures.

**Required Figures:**
1. `effect_comparison.png`: Side-by-side bar chart (early vs full effect)
2. `temporal_decay.png`: Effect size vs days-since-upload (optional)

---

## Non-Functional Requirements

### NFR-1: Performance
- Analysis completes in < 5 minutes on standard hardware
- Memory usage < 4GB peak

### NFR-2: Reproducibility
- Random seed: 42 for all bootstrap operations
- Deterministic output given same input

### NFR-3: Compatibility
- Python 3.9+
- Dependencies: pandas, numpy, scipy, statsmodels, matplotlib

---

## Data Specifications

### Input Data
| Source | Path | Format |
|--------|------|--------|
| h-e1 analysis dataset | `h-e1/results/analysis_dataset.parquet` | Parquet |
| h-e1 effect summary | `h-e1/results/h_e1_effects.json` | JSON |

### Output Data
| Artifact | Path | Format |
|----------|------|--------|
| h-c1 effects | `h-c1/results/h_c1_effects.json` | JSON |
| Effect comparison figure | `h-c1/figures/effect_comparison.png` | PNG |
| Validation report | `h-c1/04_validation.md` | Markdown |

---

## Dependencies

### Code Dependencies (REUSE from h-e1)
| Function | Source | Usage |
|----------|--------|-------|
| `compute_reproducibility_iqr()` | h-e1 | Reuse directly |
| `compute_quartile_effect()` | h-e1 | Reuse directly |
| `fit_mixed_model()` | h-e1 | Reuse directly |

### Data Dependencies
- h-e1 must be VALIDATED with PASS status
- `analysis_dataset.parquet` must exist with temporal columns

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Insufficient early runs | FAIL | Relax to first 100 runs / 180 days |
| h-e1 data missing temporal columns | BLOCK | Re-run h-e1 data collection |
| Effect disappears in early runs | SHOULD_WORK FAIL | Document as evidence of reverse causality |

---

## Appendix: Phase 2C Completeness Checklist

- [x] Baseline model: h-e1 full-sample (reuse)
- [x] Proposed model: Early-run subsample analysis
- [x] Primary metric: Relative IQR reduction
- [x] Secondary metric: Effect persistence ratio
- [x] Statistical test: Bootstrap CI, p-value
- [x] Visualization: Effect comparison bar chart
- [x] Success threshold: ≥20% effect, ≥50% persistence
