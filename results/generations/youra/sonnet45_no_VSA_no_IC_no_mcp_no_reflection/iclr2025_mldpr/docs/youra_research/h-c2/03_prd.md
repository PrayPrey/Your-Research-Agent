# Product Requirements Document (PRD): h-c2

**Date:** 2026-08-28  
**Hypothesis:** h-c2 - Low-confidence expert responses (<3/5 confidence) achieve >30% standard deviation in saturation year estimates for major benchmarks (ImageNet, GLUE, SQuAD)  
**Author:** Anonymous  
**Status:** Draft

---

## Executive Summary

### Purpose
Validate that low-confidence expert survey responses exhibit significantly higher temporal dispersion (>30% standard deviation) in benchmark saturation estimates compared to the high-confidence baseline established in h-c1.

### Scope
Statistical analysis of expert survey data stratified by confidence levels, focusing on the low-confidence subset (<3/5) across three major benchmarks: ImageNet, GLUE, and SQuAD.

### Success Criteria
- At least one benchmark demonstrates std_dev_pct > 0.30 (BEST_EFFORT gate)
- Sample size n ≥ 10 per benchmark for statistical validity
- Code executes without errors on h-c1 survey data

---

## Problem Statement

### Background
h-c1 established that high-confidence expert responses (≥4/5) show 76-93% agreement on benchmark saturation timing, with tight temporal clustering around modal dates. This hypothesis examines the inverse relationship: whether low-confidence responses demonstrate proportionally higher disagreement.

### Core Challenge
Quantify expert uncertainty by measuring temporal dispersion in low-confidence estimates, validating that confidence scores correlate with estimate reliability.

### Hypothesis Gate
**Type:** BEST_EFFORT  
**Condition:** Pass if any benchmark shows >30% std dev in low-confidence responses

### Prerequisites
- **h-c1:** High-confidence expert agreement validation (COMPLETED, gate SATISFIED)
  - Provides baseline: 76-93% agreement (low dispersion)
  - Provides data: expert survey responses with confidence stratification

---

## Functional Requirements

### FR-1: Data Loading and Filtering
**Priority:** P0 (Critical)

Load expert survey responses from h-c1 and filter by confidence threshold.

**Input:**
- File: `docs/youra_research/h-c1/data/expert_survey_responses.csv` (symlink/reuse)
- Fields: expert_id, benchmark, saturation_year_estimate, confidence_score (1-5)

**Processing:**
- Filter: `confidence_score < 3`
- Validate: Minimum n ≥ 10 per benchmark

**Output:**
- Filtered DataFrame with low-confidence responses only

**Acceptance Criteria:**
- Correctly loads h-c1 CSV data
- Applies confidence filter (<3/5)
- Validates sample size before analysis

---

### FR-2: Temporal Data Normalization
**Priority:** P0 (Critical)

Convert YYYY-MM date strings to decimal years for uniform statistical analysis.

**Input:**
- saturation_year_estimate field (format: YYYY-MM or YYYY)

**Processing:**
```python
year_decimal = pd.to_datetime(date_str).dt.year + pd.to_datetime(date_str).dt.month / 12.0
```

**Output:**
- Decimal year values (e.g., 2019.5 for 2019-06)

**Acceptance Criteria:**
- Handles both YYYY-MM and YYYY formats
- Produces consistent decimal scale

---

### FR-3: Standard Deviation Calculation by Benchmark
**Priority:** P0 (Critical)

Compute std dev of saturation year estimates for each benchmark in low-confidence subset.

**Input:**
- Low-confidence responses grouped by benchmark (ImageNet, GLUE, SQuAD)

**Processing:**
- Group by benchmark
- Calculate: std_dev, mean, std_dev_pct = (std_dev / mean) * 100
- Check: n ≥ 10 for each group

**Output:**
```python
{
  'ImageNet': {
    'std_dev': 1.2,
    'std_dev_pct': 0.06,
    'mean': 2019.5,
    'n': 15,
    'gate_pass': False
  },
  'GLUE': {...},
  'SQuAD': {...}
}
```

**Acceptance Criteria:**
- Correctly groups by benchmark
- Validates sample size (n ≥ 10)
- Computes std dev as percentage of mean

---

### FR-4: Gate Validation Logic
**Priority:** P0 (Critical)

Determine if BEST_EFFORT gate is satisfied (any benchmark > 30% std dev).

**Input:**
- Benchmark-wise std dev results from FR-3

**Processing:**
```python
gate_satisfied = any(benchmark['std_dev_pct'] > 0.30 for benchmark in results.values())
```

**Output:**
- Boolean gate result
- List of passing benchmarks (if any)

**Acceptance Criteria:**
- Correctly evaluates 30% threshold
- Reports which benchmarks pass

---

### FR-5: Distribution Visualization
**Priority:** P1 (High)

Generate histogram of saturation year estimates faceted by benchmark.

**Input:**
- Low-confidence responses with year_decimal values

**Output:**
- Figure: `docs/youra_research/h-c2/figures/distribution_by_benchmark.png`
- 3-panel histogram (ImageNet, GLUE, SQuAD)
- 30% threshold line overlay

**Acceptance Criteria:**
- Correctly facets by benchmark
- Shows temporal distribution
- Saves to figures/ subfolder

---

### FR-6: Confidence Stratification Comparison
**Priority:** P2 (Medium)

Compare std dev across all confidence bins (1, 2, 3, 4, 5) using box plot.

**Input:**
- Full h-c1 survey data (all confidence levels)

**Output:**
- Figure: `docs/youra_research/h-c2/figures/std_dev_by_confidence.png`
- Box plot showing dispersion vs confidence score

**Acceptance Criteria:**
- Shows increasing dispersion as confidence decreases
- Includes all 5 confidence bins

---

### FR-7: Sample Size Validation Chart
**Priority:** P2 (Medium)

Display sample counts per benchmark to verify n ≥ 10 threshold.

**Input:**
- Low-confidence responses grouped by benchmark

**Output:**
- Figure: `docs/youra_research/h-c2/figures/sample_sizes.png`
- Bar chart with n=10 threshold line

**Acceptance Criteria:**
- Shows sample size for each benchmark
- Highlights benchmarks below threshold (if any)

---

## Non-Functional Requirements

### NFR-1: Code Reusability
Reuse h-c1 expert survey dataset via symlink or file path reference (no duplicate downloads).

### NFR-2: Statistical Validity
Reject benchmarks with n < 10 from gate evaluation (report as "insufficient_samples").

### NFR-3: Execution Performance
Complete analysis in <30 seconds on standard dataset (expected n ~100-200 total responses).

### NFR-4: Figure Quality
All plots saved at 300 DPI, publication-ready format.

---

## Data Specifications

### Input Data
**Source:** `docs/youra_research/h-c1/data/expert_survey_responses.csv`  
**Schema:**
- expert_id: string
- benchmark: categorical (ImageNet, GLUE, SQuAD)
- saturation_year_estimate: string (YYYY-MM or YYYY)
- confidence_score: integer (1-5)

**Expected Volume:** ~100-200 rows (from h-c1 survey)

### Output Data
**Primary Result:** `docs/youra_research/h-c2/results/std_dev_analysis.json`  
**Schema:**
```json
{
  "ImageNet": {
    "std_dev": float,
    "std_dev_pct": float,
    "mean": float,
    "n": int,
    "gate_pass": bool
  },
  ...
  "gate_satisfied": bool
}
```

---

## Evaluation Metrics

### Primary Metrics
1. **Standard Deviation (years):** Absolute temporal dispersion
2. **Standard Deviation %:** Relative to mean year (primary gate metric)
3. **Sample Size (n):** Per-benchmark response count

### Gate Metrics
- **Gate Threshold:** std_dev_pct > 0.30 for at least one benchmark
- **Sample Validity:** n ≥ 10 per benchmark

### Success Criteria
- BEST_EFFORT gate passes if ANY benchmark meets threshold
- Statistical validity maintained (sample size check)

---

## Dependencies

### Prerequisite Hypotheses
- **h-c1:** Provides expert survey dataset with confidence scores

### External Dependencies
- pandas: Data manipulation, groupby operations
- numpy: Statistical functions (std, mean)
- matplotlib/seaborn: Visualization

### Data Dependencies
- h-c1 expert survey responses must be available at expected path

---

## Implementation Constraints

### Task Budget
**Tier:** LIGHT (EXISTENCE hypothesis)  
**Total Max:** 15 tasks  
**Epic Range:** 4-8 tasks

### Complexity Constraints
- No model training required (data analysis only)
- Minimal infrastructure (local execution, no GPUs)
- Single-file implementation feasible

### Scope Limitations
- Analysis limited to three benchmarks (ImageNet, GLUE, SQuAD)
- Confidence threshold fixed at 3/5 (no hyperparameter tuning)
- Temporal scale fixed at decimal years

---

## Open Questions

1. **Data Availability:** Confirm h-c1 survey data includes confidence scores for all responses
2. **Date Format:** Verify consistency of YYYY-MM vs YYYY formats in h-c1 data
3. **Threshold Justification:** 30% std dev chosen based on domain knowledge — validate against literature if needed

---

## Appendix

### Reference: h-c1 Baseline Results
- ImageNet: 92.9% agreement, modal 2019-06, n=38 high-conf
- GLUE: 76.3% agreement, modal 2020-03, n=38 high-conf
- SQuAD: 89.5% agreement, modal 2019-10, n=38 high-conf

Expected inverse: Low-conf should show <70% agreement, >30% std dev.

### Statistical Interpretation
30% std dev on year 2020 ≈ ±7.2 months dispersion around mean (wide temporal spread indicating no consensus).
