# Product Requirements Document: H-C1
# Boundary Condition Test — Logistic Pipeline on 30–49 Entry Benchmarks

---
stepsCompleted:
  - Executive Summary
  - Problem Statement
  - Functional Requirements
  - Non-Functional Requirements
  - Success Criteria
  - Data Specification
  - Dependencies
---

## Executive Summary

H-C1 tests whether the logistic fitting pipeline (validated in H-E1 through H-M4 for ≥50-entry benchmarks) degrades measurably when applied to benchmarks with 30–49 leaderboard entries. This is a scope boundary test — not a new model design. The entire pipeline is reused verbatim from H-E1/H-M4; only the input benchmark selection changes. The experiment answers: "Is the ≥50-entry restriction empirically justified, or can the pipeline handle ≥30-entry benchmarks?"

**Key deliverable:** A comparison report showing convergence rate, R², and parameter plausibility for the 30–49 entry group vs. the ≥50 entry control group (H-E1 results).

---

## Problem Statement

### Research Question
Does the logistic fitting pipeline fail or degrade when applied to benchmarks with 30–49 leaderboard entries?

### Context
- H-E1/H-M4 validated the pipeline on GLUE (≥200 entries, R²>0.9) and SuperGLUE (≥50 entries, R²>0.9).
- The ≥50-entry restriction was imposed based on theoretical reasoning (3-parameter logistic requires data spanning all three phases: growth, inflection, plateau).
- H-C1 tests whether this theoretical threshold corresponds to empirical degradation at 30–49 entries.

### Hypothesis Under Test
**H-C1 SUPPORTED** (≥50 threshold confirmed) if for the 30–49 group:
- Convergence rate < 70% (vs. 100% for ≥50), OR
- Mean R² < 0.7 (vs. >0.9 for ≥50), OR
- Plausibility rate < 70% (vs. 100% for ≥50)

**H-C1 NOT SUPPORTED** (scope should expand to ≥30) if all metrics for 30–49 group are comparable to ≥50 group.

---

## Functional Requirements

### FR-1: Benchmark Discovery (30–49 Entry Filter)
- **Source:** Papers With Code API (`paperswithcode-client`)
- **Filter:** `30 <= result_count <= 49` AND `≥2019 date coverage` AND `single composite metric`
- **Target:** 3–5 qualifying benchmarks (minimum 3 for statistical validity)
- **Fallback:** If <3 found, log warning; proceed with available benchmarks (minimum 1)
- **Control group:** Load H-E1 results (GLUE, SuperGLUE) as the ≥50-entry baseline

### FR-2: Data Retrieval and Preprocessing
Identical pipeline to H-E1:
- `client.benchmark_results(benchmark_id=...)` → extract (date, metric_value)
- Parse dates → months-since-earliest-submission
- Normalize metric to [0,1] (min-max within benchmark)
- Deduplicate: keep best score per (model, month)

### FR-3: Logistic Fitting (Reused from H-E1)
```python
def logistic(t, K, r, t0):
    return K / (1 + np.exp(-r * (t - t0)))

curve_fit(logistic, times, scores,
          p0=[0.95, 0.5, 18],
          bounds=([0.8, 0.1, 6], [1.0, 2.0, 48]),
          maxfev=5000)
```
- Identical to H-E1 validated code — zero parameter changes
- Record: convergence (bool), R², params (K, r, t0), CI widths, plausibility

### FR-4: Plausibility Assessment
Reused from H-M3/H-M4:
- `K < 0.999` (not at upper bound)
- `r > 0.05` (nonzero growth rate)
- `6 < t0 < 48` (inflection within observed range)

### FR-5: Comparative Evaluation
Compute for 30–49 group vs. ≥50 control:

| Metric | Definition | Failure Threshold (H-C1 supported) |
|--------|------------|-------------------------------------|
| Convergence rate | % benchmarks converged | < 70% |
| Mean R² | Mean over converged fits | < 0.7 |
| Plausibility rate | % with plausible params | < 70% |
| K boundary hit rate | % with K ≥ 0.999 | > 30% |

### FR-6: Ablation Studies
Four variants must be tested for each 30–49-entry benchmark:

| Variant ID | Description | Change from baseline |
|------------|-------------|----------------------|
| ABL-1 | Strict threshold | Failure = R² < 0.5 |
| ABL-2 | Loose threshold | Failure = R² < 0.8 |
| ABL-3 | Boundary split | Sub-group 30–39 vs. 40–49 |
| ABL-4 | No bounds | `curve_fit` without parameter bounds |

### FR-7: Mechanism Activation Verification
```python
def verify_boundary_test_activated(results_small, results_control):
    indicators = {
        "small_group_found": len(results_small) >= 3,
        "control_available": len(results_control) >= 2,
        "any_failure_small": len([r for r in results_small if r["converged"]]) < len(results_small),
        "r2_delta_measurable": bool(...)
    }
    return indicators["small_group_found"] and indicators["control_available"], indicators
```

### FR-8: Visualization
**Required (mandatory):**
- Gate metrics comparison bar chart: convergence rate, mean R², plausibility rate for 30–49 vs. ≥50 groups

**Additional (Phase 4 autonomous determination):**
- R² distribution histogram (30–49 overlaid with ≥50 control)
- Fitted curve overlays per 30–49 benchmark (or convergence failure note)
- Parameter scatter K vs. r, annotated with H-E1 values
- Convergence failure map table

All figures saved to: `docs/youra_research/h-c1/figures/`

### FR-9: Results Persistence
- Save per-benchmark fit results to `experiment_results.json`
- Save comparison table to `figures/comparison_table.csv`
- Logging to `experiment.log`

---

## Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed seed (seed=1 for any random ops; deterministic scipy fitting)
- All API results cached to `data/h-c1/` to avoid re-fetching
- Version pin: `paperswithcode-client`, `scipy`, `numpy`

### NFR-2: Performance
- CPU only; < 5 seconds total execution (no GPU required)
- API calls: use pagination to enumerate all benchmarks efficiently

### NFR-3: Error Handling
- `RuntimeError` from `curve_fit`: caught, logged as convergence failure
- HTTP 429 from PwC API: exponential backoff (3 retries)
- < 3 qualifying benchmarks found: log warning, proceed with available

### NFR-4: Code Reuse
- Import logistic fitting code from `h-m4/code/` or re-implement identically
- Zero deviation from H-E1 pipeline — controlled comparison requirement

---

## Success Criteria

### Experiment Success (regardless of hypothesis outcome)
1. ≥1 benchmark with 30–49 entries processed through the pipeline
2. Comparison metrics computed (convergence rate, R², plausibility)
3. Gate decision made: H-C1 SUPPORTED or NOT SUPPORTED
4. Ablation study results reported

### H-C1 SUPPORTED (≥50 threshold empirically confirmed)
- At least one: convergence rate < 70%, mean R² < 0.7, or plausibility rate < 70% for the 30–49 group vs. ≥50 control

### H-C1 NOT SUPPORTED (expand scope to ≥30)
- All metrics for 30–49 group comparable to ≥50 group → recommend lowering threshold

---

## Data Specification

### Primary Data: 30–49 Entry Benchmarks
- **Source:** Papers With Code API
- **Method:** Programmatic — `paperswithcode-client`
- **Filter:** `30 <= result_count <= 49`, ≥2019 date coverage, single metric
- **Download code:**
```python
from paperswithcode import PapersWithCodeClient
client = PapersWithCodeClient()
all_benchmarks = []
page = 1
while True:
    result = client.benchmark_list(page=page, items_per_page=100)
    all_benchmarks.extend(result.results)
    if not result.next_page or page >= result.next_page: break
    page += 1
small = [b for b in all_benchmarks if 30 <= b.result_count <= 49]
```
- **Cache path:** `data/h-c1/benchmarks_30_49.json`
- **Auto-download:** Yes (API call; no manual download required)

### Control Data: ≥50 Entry Benchmarks (from H-E1/H-M4)
- **Source:** Stored results from H-E1/H-M4 validation
- **Benchmarks:** GLUE, SuperGLUE
- **Location:** `docs/youra_research/h-m4/experiment_results.json`
- **Manual download required:** No (already computed; read from file)

---

## Dependencies

### Section 7.1: Python Packages
```
paperswithcode-client>=0.2.0
scipy>=1.7.0
numpy>=1.21.0
matplotlib>=3.4.0
pandas>=1.3.0
```
**Install command:** `pip install paperswithcode-client scipy numpy matplotlib pandas`

### Section 7.2: External Repositories
- `paperswithcode/paperswithcode-client` — official Python client (pip installable; no git clone needed)

### Section 7.3: Previous Hypothesis Artifacts
- `docs/youra_research/h-m4/experiment_results.json` — control group results (H-E1/H-M4 validated fits)
- `docs/youra_research/h-m4/code/` — reference for logistic fitting implementation

---

*Generated by Phase 3 Implementation Planning — H-C1*
*Date: 2026-08-25*
*Source: 02c_experiment_brief.md*
