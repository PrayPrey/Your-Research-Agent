# Product Requirements Document: H-E1 Benchmark Data Validation

**Date:** 2026-07-12  
**Author:** Anonymous  
**Hypothesis:** h-e1 - Papers with Code benchmark database contains ≥100 classification benchmarks (2019-2024) with ≥5 independent reproduction attempts each  
**Phase:** 3 - Implementation Planning  
**Type:** EXISTENCE (PoC Validation)

---

## Executive Summary

### Purpose
Validate the foundational hypothesis that sufficient benchmark data exists in the Papers with Code database to support a large-scale reproducibility study. This is a data availability check (EXISTENCE hypothesis) that determines study feasibility.

### Success Criteria
- **Primary:** Identify ≥100 classification benchmarks (2019-2024) with ≥5 independent results each
- **Secondary:** Verify statistical power sufficiency (Cohen's d=0.57, α=0.05, β=0.20)
- **Gate:** MUST_WORK - If <100 benchmarks found, ABANDON study (infeasible)

### Implementation Scope
- **Type:** API-based data collection + statistical validation
- **Complexity:** Low (no ML training, pure data analysis)
- **Timeline:** ~50 minutes execution time
- **Resources:** Standard CPU, 500MB memory, stable internet

---

## Problem Statement

### Research Question
Does the Papers with Code benchmark database contain sufficient samples for a reproducibility meta-analysis?

### Context
Before investing in mechanism/comparison hypotheses (H-M1, H-M2, H-M3), we must confirm:
1. Papers with Code has adequate benchmark coverage (≥100 samples)
2. Each benchmark has multiple independent reproduction attempts (≥5 results)
3. Sample size supports detecting medium effects (Cohen's d=0.57)

### Gate Condition
**MUST_WORK:** If validation fails, entire study is infeasible. This is NOT a "try and iterate" hypothesis—it's a binary feasibility gate.

---

## Functional Requirements

### FR-1: Data Collection Engine
**Priority:** CRITICAL  
**Description:** Programmatic data collection from Papers with Code REST API

**Specifications:**
- Use `https://paperswithcode.com/api/v1/` endpoints
- Query `/benchmarks/` with filters: `task=classification`, `published_after=2019-01-01`, `published_before=2024-12-31`
- For each benchmark, fetch `/results/` to count independent reproductions
- Rate limiting: 1 request/second (conservative, API limit is 1000/hour)
- Store raw JSON responses for reproducibility audit

**Acceptance Criteria:**
- Successfully retrieve benchmark list without HTTP errors
- Parse JSON to structured DataFrame
- Handle API rate limits gracefully (retry with exponential backoff)
- Log all API calls for reproducibility

**Dependencies:**
- External: Papers with Code API availability
- Libraries: `requests` (HTTP client), `pandas` (data manipulation)

---

### FR-2: Inclusion Criteria Filter
**Priority:** CRITICAL  
**Description:** Filter benchmarks by reproducibility threshold

**Specifications:**
- Apply filter: `result_count >= 5` (at least 5 independent reproductions)
- Secondary filter: Metric type = "accuracy" OR "F1" (standardized metrics only)
- Exclude: Regression tasks, generative tasks, non-classification domains

**Acceptance Criteria:**
- Filtered DataFrame contains only valid benchmarks
- Each row has: `benchmark_id`, `name`, `task`, `metric_type`, `result_count`
- No null values in required columns

**Dependencies:**
- FR-1 (Data Collection Engine)

---

### FR-3: Hypothesis Validation Logic
**Priority:** CRITICAL  
**Description:** Binary pass/fail validation against threshold

**Specifications:**
- Count total benchmarks after filtering: `N = len(filtered_df)`
- Check primary condition: `N >= 100`
- Return validation result: `{"passes": bool, "count": int, "threshold": 100}`

**Acceptance Criteria:**
- Clear pass/fail output
- Threshold comparison is exact (not rounded or approximate)
- Result logged for verification_state.yaml update

**Dependencies:**
- FR-2 (Inclusion Criteria Filter)

---

### FR-4: Statistical Power Analysis
**Priority:** HIGH  
**Description:** Verify sample size supports downstream hypothesis testing

**Specifications:**
- Calculate required N for two-sample t-test:
  - Effect size: d = 0.57 (medium effect, from Phase 2B)
  - Alpha: α = 0.05 (two-tailed)
  - Power: 1-β = 0.80
- Formula: `N_required = 2 * ((z_alpha + z_beta) / d)^2`
- Compare: `N_actual >= N_required`

**Acceptance Criteria:**
- Power analysis result: `{"power_sufficient": bool, "required_n": int, "actual_n": int}`
- Uses scipy.stats.norm for z-scores (no manual calculation)

**Dependencies:**
- FR-2 (Inclusion Criteria Filter)

---

### FR-5: Domain Coverage Validation
**Priority:** MEDIUM  
**Description:** Ensure benchmarks span multiple ML domains (CV, NLP, multimodal)

**Specifications:**
- Group benchmarks by `task` field
- Count unique domains: `n_domains = len(df['task'].unique())`
- Generate distribution: `df['task'].value_counts()`
- Check: `n_domains >= 2` (avoid single-domain bias)

**Acceptance Criteria:**
- Domain distribution dictionary: `{"CV": 80, "NLP": 30, ...}`
- Visual output: pie chart showing proportions

**Dependencies:**
- FR-2 (Inclusion Criteria Filter)

---

### FR-6: Reproduction Depth Analysis
**Priority:** MEDIUM  
**Description:** Analyze distribution of reproduction attempts per benchmark

**Specifications:**
- Calculate: `median_results = df['result_count'].median()`
- Target: Median ≥7 (sufficient variance for CV calculation in H-M3)
- Generate histogram: bins = [5-10, 11-20, 21-50, 50+]

**Acceptance Criteria:**
- Median reproduction count calculated
- Histogram saved to `{hypothesis_folder}/figures/reproduction_depth.png`

**Dependencies:**
- FR-2 (Inclusion Criteria Filter)

---

### FR-7: Visualization Generation
**Priority:** MEDIUM  
**Description:** Generate required figures for PoC validation report

**Specifications:**
Generate 5 figures (all saved to `{hypothesis_folder}/figures/`):
1. **Gate Metric Comparison** (Bar Chart)
   - X-axis: ["Threshold (100)", "Actual Count"]
   - Y-axis: Benchmark count
   - Color: Green if passes, Red if fails
   - Required for gate validation

2. **Reproduction Depth Distribution** (Histogram)
   - X-axis: Reproduction count bins (5-10, 11-20, 21-50, 50+)
   - Y-axis: Frequency (benchmark count)

3. **Domain Coverage** (Pie Chart)
   - Segments: CV, NLP, Multimodal, Other
   - Labels: Percentage + absolute count

4. **Timeline Distribution** (Line Chart)
   - X-axis: Publication year (2019-2024)
   - Y-axis: Cumulative benchmark count

5. **Power Analysis** (Bar Chart)
   - X-axis: ["Required N (80% power)", "Actual N"]
   - Y-axis: Sample size

**Acceptance Criteria:**
- All 5 figures saved as PNG files
- Figures use matplotlib/seaborn default styling
- Each figure has title, axis labels, and legend (if applicable)

**Dependencies:**
- FR-2, FR-4, FR-5, FR-6

---

### FR-8: Validation Report Generation
**Priority:** HIGH  
**Description:** Generate 04_validation.md with PoC results

**Specifications:**
- Structured report with sections:
  - Executive Summary (pass/fail, key metrics)
  - Data Collection Results (API query summary)
  - Primary Metrics (benchmark count, threshold, power analysis)
  - Secondary Metrics (domain coverage, reproduction depth)
  - Figures (embed all 5 figures)
  - Conclusion (gate decision, next steps)

**Acceptance Criteria:**
- File saved to: `{hypothesis_folder}/04_validation.md`
- Includes inline figure references: `![Caption](figures/filename.png)`
- Clear PASS/FAIL statement in Executive Summary

**Dependencies:**
- FR-3, FR-4, FR-5, FR-6, FR-7

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** CRITICAL  
**Requirement:** All API calls and filtering operations must be fully reproducible

**Specifications:**
- Log all API requests with timestamps
- Store raw JSON responses in `{hypothesis_folder}/data/raw/`
- Document API version and query parameters
- Use deterministic filtering (no random sampling)

**Acceptance Criteria:**
- Re-running script produces identical results
- Raw data files available for manual verification

---

### NFR-2: Execution Time
**Priority:** HIGH  
**Requirement:** Total execution time ≤60 minutes

**Specifications:**
- Data collection: ≤30 minutes (rate limiting: 1 req/sec)
- Filtering + validation: ≤10 minutes
- Visualization: ≤10 minutes
- Report generation: ≤10 minutes

**Acceptance Criteria:**
- Script completes within 60 minutes
- Progress logging shows time per stage

---

### NFR-3: Error Handling
**Priority:** HIGH  
**Requirement:** Graceful failure with clear error messages

**Specifications:**
- HTTP errors: Retry 3 times with exponential backoff
- JSON parsing errors: Log malformed responses, skip and continue
- Missing data: Report count of skipped benchmarks
- API quota exceeded: Save partial results and report

**Acceptance Criteria:**
- No silent failures
- Error logs saved to `{hypothesis_folder}/logs/errors.log`
- Partial results recoverable if script interrupted

---

### NFR-4: Data Storage
**Priority:** MEDIUM  
**Requirement:** Efficient storage of raw and processed data

**Specifications:**
- Raw JSON: `{hypothesis_folder}/data/raw/*.json`
- Processed DataFrame: `{hypothesis_folder}/data/processed/benchmarks.csv`
- Total size estimate: <50MB

**Acceptance Criteria:**
- Data organized in clear folder structure
- CSV file human-readable for manual inspection

---

## Data Requirements

### Input Data
**Source:** Papers with Code REST API  
**Endpoint:** `https://paperswithcode.com/api/v1/benchmarks/`  
**Format:** JSON (REST API responses)

**Query Parameters:**
- `task=classification`
- `published_after=2019-01-01`
- `published_before=2024-12-31`

**Expected Volume:** ~4000 total benchmarks → ~150-300 after filtering

---

### Output Data
**Primary Output:** Filtered benchmark DataFrame  
**Format:** pandas DataFrame → CSV export

**Schema:**
| Column | Type | Description |
|--------|------|-------------|
| `benchmark_id` | string | Unique identifier |
| `name` | string | Benchmark name |
| `task` | string | ML task type (CV, NLP, etc.) |
| `metric_type` | string | "accuracy" or "f1" |
| `result_count` | int | Number of independent reproductions |
| `publication_year` | int | Year published (2019-2024) |

**Storage Location:** `{hypothesis_folder}/data/processed/benchmarks.csv`

---

## Success Metrics

### Primary Metric: Benchmark Count
**Definition:** Total classification benchmarks with ≥5 reproductions  
**Target:** ≥100 benchmarks  
**Measurement:** `len(filtered_df)`  
**Gate:** MUST_WORK - If <100, ABANDON study

---

### Secondary Metric: Statistical Power
**Definition:** Sample size sufficient for Cohen's d=0.57 detection  
**Target:** `N >= N_required` (calculated via power analysis)  
**Measurement:** `scipy.stats` power calculation  
**Gate:** Informational (not blocking)

---

### Secondary Metric: Domain Coverage
**Definition:** Number of ML domains represented  
**Target:** ≥2 domains (CV + NLP minimum)  
**Measurement:** `len(df['task'].unique())`  
**Gate:** Informational (not blocking)

---

### Secondary Metric: Reproduction Depth
**Definition:** Median reproductions per benchmark  
**Target:** ≥7 results (sufficient variance for CV)  
**Measurement:** `df['result_count'].median()`  
**Gate:** Informational (not blocking)

---

## Dependencies and Constraints

### External Dependencies
1. **Papers with Code API**
   - Availability: Public, no authentication required
   - Rate Limit: 1000 requests/hour
   - Risk: API downtime or quota changes
   - Mitigation: Local caching, retry logic

2. **Python Libraries**
   - `requests` (HTTP client)
   - `pandas` (data manipulation)
   - `scipy` (power analysis)
   - `matplotlib`/`seaborn` (visualization)

### Internal Dependencies
- **Phase 2C Output:** 02c_experiment_brief.md (already exists)
- **Verification State:** verification_state.yaml (for status updates)

### Constraints
- **No Model Training:** This is a data validation study, not ML experiment
- **No Baseline Comparison:** Instead, compare against statistical null hypothesis
- **Single Run:** No epochs, iterations, or hyperparameter tuning

---

## Appendix: Phase 2C Completeness Check

### Dataset Coverage
✓ Primary dataset: Papers with Code benchmark database  
✓ Source: REST API (`https://paperswithcode.com/api/v1/`)  
✓ Scope: Classification tasks, 2019-2024, ≥5 results  
✓ Preprocessing: API query → JSON parsing → DataFrame filtering

### Model Coverage
N/A - This is an observational study, not a model experiment  
**Baseline Comparison:** Statistical null hypothesis (H0: random sampling yields <100)

### Evaluation Coverage
✓ Primary metric: Benchmark count (threshold: ≥100)  
✓ Secondary metrics: Power analysis, domain coverage, reproduction depth  
✓ Visualization: 5 figures (gate metric, distribution, coverage, timeline, power)

### Ablation Coverage
N/A - No ablation studies for data validation experiments

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-07-12 | Anonymous | Initial PRD from Phase 2C experiment brief |

---

**Next Steps:**
1. Architecture design (Step 3) - Define module structure and file organization
2. Logic design (Step 5) - API signatures and validation algorithms
3. Config design (Step 5) - API parameters and filtering thresholds
4. Task generation (Step 9) - Break into 5-15 implementation tasks

---

*Generated by YouRA Phase 3: Implementation Planning*  
*Source: h-e1/02c_experiment_brief.md*  
*Gate: MUST_WORK (foundational hypothesis)*
