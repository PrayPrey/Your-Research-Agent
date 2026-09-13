# Product Requirements Document (PRD)
# H-C1: Tactic Budget Equalization Feasibility Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Status**: Draft  
**Complexity Tier**: LOW

---

## Executive Summary

Build post-hoc statistical analysis tool to validate H-C1 gate criterion (CV ≤ 100%) using H-E1 tactic count data. No new experiments — pure data analysis. Deliverables: Python script, validation report, visualizations.

**Scope**: Single-script statistical pipeline (pandas + scipy + matplotlib)  
**Timeline**: 1 day  
**Budget**: 15-25 implementation tokens  
**Risk**: LOW (no infrastructure, no Lean runtime dependency)

---

## Problem Statement

### Background

H-C1 validates that tactic evaluation count can serve as fair comparison metric between lean-auto and LLM-guided prover. H-E1 baseline measured mean=9.2±4.1 tactic evaluations per solved problem (N=32).

### Core Problem

**Question**: Is tactic count distribution stable enough (CV ≤ 100%) to use as computational budget metric?

**Why It Matters**:
- LLM inference latency ≠ search depth difference
- Need quantitative fairness control for Phase 5 baseline comparison
- Budget recommendation (mean+1.4σ ≈ 15) feeds into H-M1/M2/M3 LeanCopilot runs

### Success Criteria

**Primary Gate**: CV ≤ 100% → PASS (tactic budget feasible)  
**Secondary**: Coverage ≥ 70% (budget captures most baseline strategies)  
**Output**: Validation report with gate decision + budget recommendation

---

## Requirements

### Functional Requirements

#### FR-1: Data Loading

**Priority**: MUST HAVE

**Description**: Load H-E1 results and filter to solved problems with valid tactic counts.

**Input**: `h-e1/code/data/results/results.csv` (N=244 rows)

**Output**: Pandas DataFrame with `problem_id`, `outcome`, `tactic_count` (N≈32 after filtering)

**Validation**:
- Filter: `outcome == 'SOLVED' AND tactic_count.notna()`
- Expected N=32 (84% extraction coverage from H-E1)
- Warn if N < 20 (insufficient sample)

**Edge Cases**:
- Missing CSV file → fail fast with error message
- Empty filter result → fail with "no solved problems found"
- Non-numeric tactic_count → coerce to NaN and exclude

---

#### FR-2: Descriptive Statistics

**Priority**: MUST HAVE

**Description**: Compute summary statistics for tactic count distribution.

**Metrics**:
- Mean (μ)
- Standard deviation (σ)
- Median
- Coefficient of Variation (CV = σ/μ)
- IQR (Q3 - Q1)
- 95% confidence intervals for mean/std (bootstrap or t-distribution)

**Output**: JSON dict `summary.json`:
```json
{
  "n": 32,
  "mean": 9.2,
  "std": 4.1,
  "median": 8.0,
  "cv": 0.45,
  "iqr": 5.0,
  "ci_mean_lower": 7.8,
  "ci_mean_upper": 10.6
}
```

**Validation**:
- CV expected ≈ 0.45 (from H-E1 report)
- Median expected ≈ 8.0

---

#### FR-3: Budget Recommendation

**Priority**: MUST HAVE

**Description**: Apply decision tree to recommend tactic budget based on CV.

**Decision Logic**:
```python
if cv <= 0.5:
    budget = ceil(mean + std)
    estimator = "mean+1σ"
elif cv <= 1.0:
    budget = ceil(mean + 1.4 * std)
    estimator = "mean+1.4σ"
else:
    budget = None
    estimator = "unreliable"
```

**Output**: Budget integer + estimator string

**Validation**:
- CV=0.45 → budget = ceil(9.2 + 1.4×4.1) = ceil(14.94) = 15
- Compute coverage: P(tactic_count ≤ budget)
- Expected coverage ≈ 80% for budget=15

---

#### FR-4: Gate Decision

**Priority**: MUST HAVE

**Description**: Evaluate MUST_WORK gate criterion.

**Logic**:
```python
if cv <= 1.0:
    gate_result = "PASS"
    verdict = f"CV={cv:.2f} ≤ 1.0, tactic budget feasible"
else:
    gate_result = "FAIL"
    verdict = f"CV={cv:.2f} > 1.0, variance too high"
```

**Output**: Gate decision string ("PASS" / "FAIL")

**Side Effects**: Update verification_state.yaml with gate result

---

#### FR-5: Visualization

**Priority**: SHOULD HAVE

**Description**: Generate 3-panel figure (histogram, box plot, ECDF).

**Panel 1: Histogram**
- Bins: 15 (adaptive based on data range)
- Overlays: Budget line (red dashed), mean line (blue)
- Labels: X="Tactic Count", Y="Frequency"

**Panel 2: Box Plot**
- Outlier detection (IQR × 1.5 rule)
- Budget line (red dashed)

**Panel 3: ECDF (Empirical Cumulative Distribution)**
- X="Tactic Count", Y="Cumulative Probability"
- Budget line with coverage annotation
- Points: marker='o', size=4

**Output**: `tactic_budget_analysis.png` (1500×400 px, 150 dpi)

**Libraries**: matplotlib 3.7+

---

#### FR-6: Validation Report

**Priority**: MUST HAVE

**Description**: Generate markdown report with gate decision and statistics.

**Template**:
```markdown
# H-C1 Validation Report

## Summary Statistics
- **Sample Size**: {n}
- **Mean**: {mean:.1f}
- **Std Dev**: {std:.1f}
- **CV**: {cv:.2f} ({cv*100:.0f}%)
- **Median**: {median:.1f}
- **IQR**: {iqr:.1f}

## Budget Recommendation
- **Budget**: {budget} tactic evaluations
- **Estimator**: {estimator}
- **Coverage**: {coverage:.1%} of baseline solves

## Gate Decision
- **Criterion**: CV ≤ 1.0
- **Observed CV**: {cv:.2f}
- **Result**: {gate_result}

## Interpretation
{verdict}

## Downstream Implications
- Apply budget={budget} to H-M1/M2/M3 LeanCopilot runs
- Report both raw and budget-constrained success rates in Phase 5
```

**Output**: `h-c1/04_validation.md`

**Validation**: Render report and verify gate_result matches CV threshold

---

### Non-Functional Requirements

#### NFR-1: Performance

- **Execution Time**: < 30 seconds on standard laptop (data analysis + plotting)
- **Memory**: < 500 MB (small CSV dataset)
- **I/O**: Single CSV read, 2 file writes (JSON + PNG)

#### NFR-2: Maintainability

- **Code Style**: PEP 8 compliant, type hints for public functions
- **Documentation**: Docstrings for all functions (Google style)
- **Testing**: None required (one-off analysis script, manual validation)

#### NFR-3: Reproducibility

- **Random Seed**: Set `np.random.seed(42)` for bootstrap CI (if used)
- **Dependency Pinning**: Document versions in requirements.txt
- **Data Provenance**: Log H-E1 results.csv SHA256 hash in summary.json

#### NFR-4: Error Handling

- Missing input file → fail fast with file path
- Insufficient sample (N < 20) → warning + proceed with caveat
- Invalid data (negative tactic counts) → filter out with log message

---

## Technical Approach

### Architecture

**Pattern**: Single-script data pipeline (no classes needed)

**Structure**:
```
analyze_tactic_budget.py
├── load_data()          # FR-1
├── compute_stats()      # FR-2
├── recommend_budget()   # FR-3
├── evaluate_gate()      # FR-4
├── plot_distribution()  # FR-5
└── write_report()       # FR-6
```

**Flow**:
1. Load CSV → filter solved problems with tactic counts
2. Compute stats → save summary.json
3. Recommend budget → compute coverage
4. Evaluate gate → PASS/FAIL decision
5. Plot distribution → save PNG
6. Write markdown report

**No Infrastructure**: No database, no API, no web server — pure filesystem I/O.

---

### Data Schema

#### Input: results.csv

```csv
problem_id,source,outcome,time_s,tactic_count
aime_1983_p1,AMC,SOLVED,45.3,7
amc12a_2019_p6,AMC,SOLVED,12.1,5
imo_1959_p1,IMO,SOLVED,234.7,18
aime_1990_p3,AIME,TIMEOUT,300.0,
...
```

**Columns**:
- `problem_id`: string (unique key)
- `source`: string (AMC/AIME/IMO)
- `outcome`: enum (SOLVED/TIMEOUT/ERROR)
- `time_s`: float (wall-clock seconds)
- `tactic_count`: int | NaN (empty string → NaN)

**Load Code**:
```python
import pandas as pd
df = pd.read_csv('results.csv', dtype={'tactic_count': 'Int64'})
```

---

#### Output: summary.json

```json
{
  "data_provenance": {
    "source_file": "h-e1/code/data/results/results.csv",
    "sha256": "abc123...",
    "timestamp": "2026-08-20T10:30:00Z"
  },
  "sample": {
    "n_total": 244,
    "n_solved": 38,
    "n_with_tactic_count": 32,
    "extraction_coverage": 0.84
  },
  "statistics": {
    "mean": 9.2,
    "std": 4.1,
    "median": 8.0,
    "cv": 0.45,
    "iqr": 5.0,
    "min": 3,
    "max": 20,
    "q1": 6.0,
    "q3": 11.0
  },
  "budget": {
    "value": 15,
    "estimator": "mean+1.4σ",
    "coverage": 0.81
  },
  "gate": {
    "criterion": "CV ≤ 1.0",
    "cv": 0.45,
    "result": "PASS"
  }
}
```

---

### Dependencies

**Python**: 3.10+

**Libraries**:
```
pandas==2.0.3
numpy==1.24.4
scipy==1.11.2
matplotlib==3.7.2
```

**No Heavy Dependencies**: No torch, no transformers, no Lean runtime.

---

## Implementation Plan

### Phase 1: Core Analysis (3 hours)

**Tasks**:
1. Set up project structure (`h-c1/code/analyze_tactic_budget.py`)
2. Implement `load_data()` with filtering logic
3. Implement `compute_stats()` with scipy descriptive stats
4. Implement `recommend_budget()` decision tree
5. Implement `evaluate_gate()` with PASS/FAIL logic
6. Write unit tests for edge cases (N < 20, missing file)

**Deliverable**: Working script (no visualization yet)

---

### Phase 2: Visualization (2 hours)

**Tasks**:
1. Implement `plot_distribution()` with 3-panel layout
2. Add budget line overlays
3. Tune aesthetics (colors, labels, legend)
4. Generate sample figure with H-E1 data

**Deliverable**: `tactic_budget_analysis.png`

---

### Phase 3: Reporting (2 hours)

**Tasks**:
1. Implement `write_report()` template rendering
2. Generate `04_validation.md`
3. Validate gate decision matches CV threshold
4. Add sensitivity analysis section (budget=10, 15, 20)

**Deliverable**: Complete validation report

---

### Phase 4: Integration (1 hour)

**Tasks**:
1. Run full pipeline on H-E1 data
2. Verify summary.json matches H-E1 report statistics
3. Update verification_state.yaml with gate result
4. Archive outputs in `h-c1/code/data/results/`

**Deliverable**: Phase 4 ready for validation

---

## Testing Strategy

### Validation Approach

**No Automated Tests**: One-off analysis script, manual validation sufficient.

**Manual Checks**:
1. Load H-E1 results.csv → verify N=32 after filtering
2. Compute stats → compare to H-E1 report (mean≈9.2, std≈4.1)
3. Budget recommendation → verify coverage ≈ 80%
4. Gate decision → verify CV=0.45 → PASS
5. Visualization → inspect histogram for right-skew shape
6. Report → read markdown, verify prose matches numbers

**Smoke Test**: Run script with sample CSV (5 rows) to catch import errors.

---

## Risk Analysis

### R-1: Sample Size Too Small (N < 20)

**Probability**: LOW (H-E1 achieved N=32)

**Impact**: MEDIUM (wider confidence intervals)

**Mitigation**:
- Add warning message if N < 20
- Report 95% CI on mean/std estimates
- Proceed with analysis but flag as "pilot-only"

**Fallback**: Recommend larger H-E1 run if N < 15.

---

### R-2: Tactic Extraction Coverage < 80%

**Probability**: REALIZED (H-E1 achieved 84%, acceptable)

**Impact**: LOW (N=32 still sufficient)

**Mitigation**:
- Document coverage limitation in validation report
- Investigate missing tactic counts (trace log parsing failures from H-E1)
- Conservative approach: Exclude missing data (don't impute)

**Fallback**: If coverage < 50%, recommend improving trace parser.

---

### R-3: High Variance (CV > 100%)

**Probability**: VERY LOW (H-E1 observed CV=45%)

**Impact**: HIGH (gate failure)

**Mitigation**:
- Recompute CV with outlier removal (IQR × 1.5 rule)
- Generate diagnostic plots (Q-Q plot, histogram)
- Document limitation in report

**Fallback**: Pivot to timeout-based fairness metric (report H-C1 as FAIL, proceed with H-C1-alt).

---

## Deliverables

### Code

**File**: `h-c1/code/analyze_tactic_budget.py`

**Structure**:
```python
#!/usr/bin/env python3
"""
H-C1 Tactic Budget Analysis
Post-hoc statistical validation of tactic count distribution.
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import json
from pathlib import Path

def load_data(csv_path: str) -> pd.DataFrame:
    """Load H-E1 results and filter to solved problems."""
    ...

def compute_stats(tactic_counts: np.ndarray) -> dict:
    """Compute descriptive statistics."""
    ...

def recommend_budget(stats: dict) -> tuple[int, str]:
    """Apply decision tree to recommend budget."""
    ...

def evaluate_gate(cv: float) -> tuple[str, str]:
    """Evaluate MUST_WORK gate criterion."""
    ...

def plot_distribution(tactic_counts: np.ndarray, budget: int, output_path: str):
    """Generate 3-panel visualization."""
    ...

def write_report(stats: dict, budget: int, gate_result: str, output_path: str):
    """Generate markdown validation report."""
    ...

if __name__ == "__main__":
    # Pipeline execution
    df = load_data("h-e1/code/data/results/results.csv")
    stats = compute_stats(df['tactic_count'].values)
    budget, estimator = recommend_budget(stats)
    gate_result, verdict = evaluate_gate(stats['cv'])
    plot_distribution(df['tactic_count'].values, budget, "tactic_budget_analysis.png")
    write_report(stats, budget, gate_result, "04_validation.md")
    print(f"Gate Decision: {gate_result}")
```

---

### Outputs

1. **summary.json**: Machine-readable statistics
2. **tactic_budget_analysis.png**: 3-panel visualization
3. **04_validation.md**: Gate decision report
4. **analyze_tactic_budget.py**: Analysis script

**Archive Location**: `h-c1/code/data/results/`

---

## Timeline

**Total Duration**: 1 day (8 hours)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Core analysis | 3 hours | Working script |
| Visualization | 2 hours | PNG figure |
| Reporting | 2 hours | Validation report |
| Integration | 1 hour | Updated verification_state.yaml |

**No Parallelization**: Single-threaded workflow (no dependencies).

---

## Acceptance Criteria

### Must Have

- [ ] Script loads H-E1 results.csv and filters to N≈32 solved problems
- [ ] Computes mean, std, median, CV, IQR
- [ ] Recommends budget=15 with estimator="mean+1.4σ"
- [ ] Evaluates gate: CV=0.45 ≤ 1.0 → PASS
- [ ] Generates 3-panel figure (histogram, box plot, ECDF)
- [ ] Writes 04_validation.md with gate decision
- [ ] Saves summary.json with complete statistics

### Should Have

- [ ] 95% confidence intervals on mean/std
- [ ] Coverage analysis (percentage ≤ budget)
- [ ] Sensitivity table (budget=10, 15, 20 vs coverage)
- [ ] Data provenance (SHA256 hash, timestamp)

### Could Have

- [ ] Outlier investigation (identify problems with tactic_count > Q3 + 1.5×IQR)
- [ ] Skewness/kurtosis metrics
- [ ] Bootstrap resampling for robust CI estimation

### Won't Have

- [ ] Automated testing (manual validation sufficient)
- [ ] Web dashboard (matplotlib PNG sufficient)
- [ ] Database persistence (filesystem JSON sufficient)
- [ ] Real-time streaming (one-off batch analysis)

---

## Success Metrics

**Primary**: Gate decision matches CV threshold (CV=0.45 → PASS)  
**Secondary**: Budget recommendation matches H-E1 report (budget=15)  
**Quality**: Validation report is self-contained and actionable for Phase 5

---

## Open Questions

1. **Q**: Should we compute bootstrap CI or use t-distribution for mean/std CI?  
   **A**: Use t-distribution (faster, N=32 near normal regime).

2. **Q**: What if H-E1 results.csv is missing tactic_count for some SOLVED problems?  
   **A**: Exclude them (conservative approach, no imputation).

3. **Q**: Should we investigate outliers (tactic_count > 20)?  
   **A**: Report outlier count but don't remove (real search complexity).

---

## Approval

**Prepared By**: Phase 3 Implementation Planning Agent  
**Reviewed By**: (pending)  
**Approved By**: (pending)  

**Status**: Ready for Architecture Design

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-08-20 | Initial draft |
