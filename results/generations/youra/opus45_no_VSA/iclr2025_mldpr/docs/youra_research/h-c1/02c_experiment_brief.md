# Experiment Design: h-c1

**Date:** 2026-08-09
**Author:** YouRA Research Pipeline
**Hypothesis Statement:** The metadata-variance effect persists in first-50-runs subsample (within 90 days of dataset upload), ruling out reverse causality from community convergence
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **CONDITION/ROBUSTNESS Template** - Testing temporal robustness via early-run subsample analysis.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (VALIDATED, PASS with 42.1% IQR reduction)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c1
- **Type:** CONDITION (Robustness Check)
- **Prerequisites:** h-e1 (must pass before h-c1)

### Gate Condition
**SHOULD_WORK:** Pipeline continues with warnings if this test fails, but failure weakens causal claims about metadata completeness by suggesting reverse causality (community convergence improving variance over time, not metadata).

### Causal Logic Being Tested
- **Alternative hypothesis (reverse causality):** Over time, community learns optimal preprocessing → variance decreases → metadata improves (correlation without metadata being causal)
- **Test:** If effect persists in first-50-runs (before community convergence possible), reverse causality is ruled out

---

## Continuation Context

### h-e1 Validated Results (Building Upon)
| Metric | h-e1 Result | Threshold |
|--------|-------------|-----------|
| Relative IQR reduction | 42.1% | ≥20% |
| Absolute IQR reduction | 0.0197 | ≥0.01 |
| 95% CI | [39.1%, 51.7%] | excludes <10% |
| p-value | <0.0001 | <0.05 |

### Reuse from h-e1
- **Data collection pipeline:** REUSE (same OpenML API calls)
- **Metadata completeness scorer:** REUSE
- **Mixed-effects model specification:** REUSE
- **Analysis code:** REUSE with temporal filter modification

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct results for OpenML temporal analysis. Key findings from ML variance literature:
- **PyTorch randomness:** Seed control for reproducibility (pytorch.org/docs/stable/notes/randomness.html)
- **Diffusers documentation:** Variance analysis patterns in ML pipelines

### Archon Code Examples

Limited relevance - Archon KB focused on ML model training, not statistical analysis on OpenML metadata.

### Exa GitHub Implementations

**Repository 1**: openml/openml-python (Official)
- **URL**: https://openml.github.io/openml-python/
- **Relevance**: Direct API for temporal filtering via `upload_time` field
- **Key Code**: `openml.runs.list_runs()` returns DataFrame with `upload_time` column
- **Temporal Filter**: Filter runs by `upload_time` relative to dataset `upload_date`

**Repository 2**: Academic Papers on ML Variance
- **Source**: Bouthillier et al. (2021) "Accounting for Variance in ML Benchmarks" (MLSys)
- **Key Insight**: Bootstrap resampling for variance estimation, permutation tests for significance
- **Relevance**: Statistical methodology for reproducibility variance analysis

**Repository 3**: LMEM for ML Evaluation
- **Source**: ar5iv.labs.arxiv.org/html/2302.04054 "Towards Inferential Reproducibility"
- **Key Insight**: Linear Mixed Effects Models (LMEMs) + Variance Component Analysis (VCA)
- **Relevance**: Statistical framework for analyzing variance sources with random effects

### 🎯 Implementation Priority Assessment

This is a **statistical analysis** experiment, not ML model training. Priority:
1. **OpenML Python API** (official implementation) - for data collection
2. **statsmodels** (standard library) - for mixed-effects regression
3. **scipy/numpy** (standard library) - for statistical tests

**Recommended Implementation Path:**
- Primary: OpenML Python API + statsmodels + scipy
- Fallback: Direct REST API calls if rate-limited
- Justification: Official API provides `upload_time` field needed for temporal filtering

### Code Analysis (Serena MCP)

*Skipped* - This is a statistical analysis experiment, not neural network architecture. Code patterns are simple (API calls + pandas + statsmodels).

---

## Experiment Specification

### Dataset

**Type:** programmatic-api
**Source:** OpenML REST API
**Endpoint:** `openml.org/api/v1/`
**Time Window:** 2019-01-01 to 2024-12-31

#### Temporal Subsample Filter (h-c1 Specific)
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| First N runs | 50 | Early adoption period |
| Time window | ≤90 days from dataset upload | Before community convergence |
| Minimum runs in window | ≥5 | Statistical power |

**Loading Information** (for Phase 4 download):
- Method: programmatic-api
- Identifier: OpenML Python API v0.14+
- Code:
```python
import openml
from datetime import timedelta

def get_early_runs(dataset_id, max_runs=50, max_days=90):
    """Get first 50 runs within 90 days of dataset upload."""
    dataset = openml.datasets.get_dataset(dataset_id)
    upload_date = pd.to_datetime(dataset.upload_date)
    cutoff = upload_date + timedelta(days=max_days)
    
    runs = openml.evaluations.list_evaluations(
        function='predictive_accuracy',
        data=[dataset_id],
        output_format='dataframe'
    )
    runs['upload_time'] = pd.to_datetime(runs['upload_time'])
    early_runs = runs[runs['upload_time'] <= cutoff].head(max_runs)
    return early_runs
```

### Models

#### Baseline Model (Statistical)

**Model Type:** h-e1 Full-Sample Analysis
**Architecture:** Mixed-effects regression on ALL runs (same as h-e1)
**Purpose:** Comparison baseline showing effect in full sample

**Loading Information** (for Phase 4 download):
- Method: Reuse h-e1 results
- Identifier: `h-e1/results/h_e1_effects.json`
- Code: `baseline_effect = json.load(open('h-e1/results/h_e1_effects.json'))`

#### Proposed Model (Statistical)

**Model Type:** h-c1 Early-Run Subsample Analysis
**Architecture:** Same mixed-effects regression, restricted to first-50-runs subsample

**Core Mechanism Implementation:**

```python
# Core Mechanism: Temporal Subsample Filter for Reverse Causality Test
# Based on: OpenML API + h-e1 mixed-effects framework

def filter_early_runs(runs_df, datasets_df, max_runs=50, max_days=90):
    """
    Filter to first N runs within M days of dataset upload.
    Tests whether metadata effect persists before community convergence.
    
    Args:
        runs_df: DataFrame with run_id, data_id, upload_time, value
        datasets_df: DataFrame with data_id, upload_date
        max_runs: Maximum runs per dataset (default: 50)
        max_days: Maximum days from upload (default: 90)
    
    Returns:
        DataFrame: Filtered early runs only
    """
    # Merge to get dataset upload dates
    merged = runs_df.merge(
        datasets_df[['data_id', 'upload_date']], 
        on='data_id'
    )
    
    # Compute days since upload
    merged['days_since_upload'] = (
        pd.to_datetime(merged['upload_time']) - 
        pd.to_datetime(merged['upload_date'])
    ).dt.days
    
    # Filter: within time window
    in_window = merged[merged['days_since_upload'] <= max_days]
    
    # Filter: first N runs per dataset
    early_runs = (
        in_window
        .sort_values(['data_id', 'upload_time'])
        .groupby('data_id')
        .head(max_runs)
    )
    
    return early_runs

def run_temporal_robustness_test(df, df_early):
    """
    Compare full-sample vs early-run effect sizes.
    """
    full_effect = compute_quartile_effect(df)  # From h-e1
    early_effect = compute_quartile_effect(df_early)
    
    return {
        'full_sample_effect': full_effect['relative_reduction_pct'],
        'early_run_effect': early_effect['relative_reduction_pct'],
        'effect_persists': early_effect['relative_reduction_pct'] >= 20
    }
```

### Training Protocol

**N/A** - This is a statistical analysis, not model training.

**Analysis Protocol:**
| Step | Description |
|------|-------------|
| 1 | Load h-e1 processed data (`analysis_dataset.parquet`) |
| 2 | Apply temporal subsample filter (first 50 runs, ≤90 days) |
| 3 | Verify ≥5 matched runs per dataset in subsample |
| 4 | Recompute IQR on filtered subsample |
| 5 | Fit same mixed-effects model as h-e1 |
| 6 | Compute quartile effect on subsample |
| 7 | Compare to h-e1 full-sample effect |

**Seed:** 42 (for bootstrap CI if needed)

### Evaluation

**Primary Metrics:**
| Metric | Definition |
|--------|------------|
| Early-run relative IQR reduction | `(IQR_bottom_early - IQR_top_early) / IQR_bottom_early * 100` |
| Effect persistence ratio | `early_run_effect / full_sample_effect` |

**Success Criteria:**
| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Early-run effect | ≥20% relative IQR reduction | Same as h-e1 threshold |
| Effect persistence | ≥50% of full-sample effect | `early_effect / full_effect ≥ 0.5` |
| Statistical significance | p < 0.05 | Mixed-effects β1 coefficient |

**Falsification Criteria:**
| Condition | Interpretation |
|-----------|----------------|
| Effect <10% in early runs | Reverse causality likely |
| Effect direction reversed | Strong evidence of reverse causality |
| CI includes 0 | Effect not robust to temporal subsetting |

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: statistical-analysis
- Library: statsmodels, scipy, numpy
- Code:
```python
import statsmodels.formula.api as smf
from scipy import stats
import numpy as np

# Reuse h-e1 analysis functions
from h_e1_analysis import fit_mixed_model, compute_quartile_effect
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Early-Run vs Full-Sample Effect Comparison**: Side-by-side bar chart showing IQR reduction percentages

#### Additional Figures (LLM Autonomous)
1. **Temporal decay plot**: Effect size vs days-since-upload (shows if effect diminishes with time)
2. **Run count distribution**: Histogram of runs per dataset in early vs full sample
3. **Confidence interval comparison**: Forest plot of full-sample vs early-run effects with CIs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-c1/figures/`.

---

## 🔬 Robustness Success Check

**h-c1 Pass Condition:**
1. Code runs without error
2. Early-run subsample has ≥100 datasets with ≥5 matched runs each
3. Relative IQR reduction ≥20% in early-run subsample
4. Effect persistence ratio ≥50% (early/full ≥ 0.5)

**Interpretation:**
- **PASS:** Metadata effect is robust; reverse causality ruled out
- **FAIL (SHOULD_WORK):** Effect may be due to community convergence; causal claim weakened but pipeline continues

---

## Appendix: Reference Implementations

### A. OpenML Python API Documentation
- **Source:** https://openml.github.io/openml-python/
- **Key Functions:**
  - `openml.evaluations.list_evaluations()` - Returns `upload_time` field
  - `openml.datasets.get_dataset()` - Returns `upload_date` field
  - `openml.runs.list_runs()` - Alternative run listing with temporal data

### B. Statistical Methodology References
- **Bouthillier et al. (2021):** "Accounting for Variance in Machine Learning Benchmarks" MLSys
  - Bootstrap resampling, permutation tests for variance analysis
- **ar5iv 2302.04054:** "Towards Inferential Reproducibility of Machine Learning Research"
  - LMEMs for variance component analysis
- **Bosma et al. (2024):** "Reproducibility of Training Deep Learning Models"
  - Permutation test calibration for model comparison

### C. h-e1 Code Reuse Mapping
| h-e1 Function | h-c1 Usage |
|---------------|------------|
| `collect_datasets()` | REUSE |
| `get_matched_runs()` | REUSE + add temporal filter |
| `compute_metadata_score()` | REUSE |
| `compute_reproducibility_iqr()` | REUSE on filtered data |
| `fit_mixed_model()` | REUSE |
| `compute_quartile_effect()` | REUSE |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- Phase 2C experiment design started
- Archon KB search completed (limited relevance)
- Exa GitHub search completed (OpenML API + academic papers)
- Serena analysis skipped (statistical analysis, not NN)
- Experiment specification synthesized

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
