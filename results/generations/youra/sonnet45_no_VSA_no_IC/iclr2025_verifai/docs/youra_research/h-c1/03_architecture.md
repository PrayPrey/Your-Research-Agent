# Architecture Specification
# H-C1: Tactic Budget Feasibility Analysis

**Version**: 1.0  
**Date**: 2026-08-20  
**Applied Patterns**: Pandas pipeline (Archon KB)  
**Codebase**: Green-field - single script

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: Single-script statistical analysis, no existing code patterns.

---

## System Overview

Data pipeline: CSV → filter → stats → budget logic → visualization → markdown report.

**Flow**:
1. Load H-E1 results.csv (244 rows) → filter to solved + valid tactic_count (N≈32)
2. Compute stats (mean, std, CV) → save summary.json
3. Apply decision tree (CV threshold) → recommend budget
4. Evaluate gate (CV ≤ 1.0) → PASS/FAIL
5. Plot 3-panel figure → save PNG
6. Write validation report → 04_validation.md

**Dependencies**: pandas → scipy → matplotlib (linear pipeline, no parallelism)

---

## Module Design

### analyze_tactic_budget.py (`h-c1/code/analyze_tactic_budget.py`)

**Dependencies**: pandas, numpy, scipy, matplotlib, json, pathlib

```python
#!/usr/bin/env python3
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import json
from pathlib import Path
from typing import Tuple

def load_data(csv_path: str) -> pd.DataFrame:
    """Load H-E1 results and filter to solved problems with tactic counts."""
    ...

def compute_stats(tactic_counts: np.ndarray) -> dict:
    """Compute descriptive statistics (mean, std, CV, IQR, CI)."""
    ...

def recommend_budget(stats: dict) -> Tuple[int, str, float]:
    """Apply decision tree to recommend budget. Returns (budget, estimator, coverage)."""
    ...

def evaluate_gate(cv: float) -> Tuple[str, str]:
    """Evaluate MUST_WORK gate. Returns (gate_result, verdict)."""
    ...

def plot_distribution(tactic_counts: np.ndarray, budget: int, stats: dict, output_path: str) -> None:
    """Generate 3-panel figure (histogram, boxplot, ECDF)."""
    ...

def write_report(stats: dict, budget: int, estimator: str, coverage: float, 
                 gate_result: str, verdict: str, output_path: str) -> None:
    """Generate markdown validation report."""
    ...

if __name__ == "__main__":
    # Pipeline execution
    df = load_data("../h-e1/code/data/results/results.csv")
    stats = compute_stats(df['tactic_count'].values)
    budget, estimator, coverage = recommend_budget(stats)
    gate_result, verdict = evaluate_gate(stats['cv'])
    plot_distribution(df['tactic_count'].values, budget, stats, "data/results/tactic_budget_analysis.png")
    write_report(stats, budget, estimator, coverage, gate_result, verdict, "04_validation.md")
    print(f"Gate Decision: {gate_result} (CV={stats['cv']:.2f})")
```

---

## Error Handling

**Strategy**: Fail fast on critical errors, warn on data quality issues.

| Error | Handling |
|-------|----------|
| Missing CSV file | Raise FileNotFoundError with path |
| Empty filter result (N=0) | Raise ValueError("No solved problems with tactic counts") |
| Small sample (N < 20) | Log warning, compute stats with caveat, flag in report |
| Invalid tactic_count (negative, non-numeric) | Filter out with logging, report in summary.json |
| Missing output directory | Create parent directories with Path.mkdir(parents=True) |

**Implementation**:
```python
def load_data(csv_path: str) -> pd.DataFrame:
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"H-E1 results not found: {csv_path}")
    df = pd.read_csv(csv_path, dtype={'tactic_count': 'Int64'})
    filtered = df[(df['outcome'] == 'SOLVED') & df['tactic_count'].notna()]
    if len(filtered) == 0:
        raise ValueError("No solved problems with valid tactic counts")
    if len(filtered) < 20:
        print(f"WARNING: Small sample size N={len(filtered)} (< 20)")
    return filtered
```

---

## File I/O Patterns

**Input**:
- `h-e1/code/data/results/results.csv` (read once, ~10 KB)

**Output**:
- `h-c1/code/data/results/summary.json` (stats + metadata, ~2 KB)
- `h-c1/code/data/results/tactic_budget_analysis.png` (3-panel plot, ~150 KB)
- `h-c1/04_validation.md` (gate report, ~2 KB)

**Pattern**: Single read, multiple writes. No database, no streaming.

**Path Resolution**:
```python
# Assume script runs from h-c1/code/
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data" / "results"
DATA_DIR.mkdir(parents=True, exist_ok=True)

H_E1_RESULTS = BASE_DIR.parent.parent / "h-e1" / "code" / "data" / "results" / "results.csv"
SUMMARY_JSON = DATA_DIR / "summary.json"
PLOT_PNG = DATA_DIR / "tactic_budget_analysis.png"
REPORT_MD = BASE_DIR.parent / "04_validation.md"
```

---

## Data Schema

**Input DataFrame** (post-filter):
```python
pd.DataFrame({
    'problem_id': str,
    'source': str,        # AMC/AIME/IMO
    'outcome': str,       # Always 'SOLVED' after filter
    'time_s': float,
    'tactic_count': int   # No NaNs after filter
})
```

**summary.json**:
```json
{
  "data_provenance": {
    "source_file": "h-e1/code/data/results/results.csv",
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
    "q3": 11.0,
    "ci_mean_lower": 7.8,
    "ci_mean_upper": 10.6
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

## Dependency Graph

```
load_data() → compute_stats() → recommend_budget() → evaluate_gate()
                ↓                        ↓                    ↓
          plot_distribution()      write_report()
```

**Execution Order**:
1. `load_data()` - reads CSV, returns DataFrame
2. `compute_stats()` - computes mean/std/CV from array
3. `recommend_budget()` - uses stats dict
4. `evaluate_gate()` - uses CV from stats dict
5. `plot_distribution()` - uses raw array + budget + stats
6. `write_report()` - uses all computed values

**No Circular Dependencies**: Linear pipeline, each function outputs to next.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Implement load_data() with filtering and validation | 8 | read(2) + filter(2) + validate(2) + error_handling(2) |
| A-2 | Statistical Analysis | Implement compute_stats() with scipy descriptive stats | 10 | mean/std(2) + CV(1) + IQR(2) + CI_computation(3) + dict_assembly(2) |
| A-3 | Budget Logic | Implement recommend_budget() decision tree and coverage | 9 | decision_tree(3) + ceil_logic(1) + coverage_calc(3) + validation(2) |
| A-4 | Gate Evaluation | Implement evaluate_gate() with PASS/FAIL logic | 6 | threshold_check(2) + verdict_string(2) + output_format(2) |
| A-5 | Visualization | Implement plot_distribution() 3-panel matplotlib figure | 14 | histogram(4) + boxplot(3) + ECDF(4) + layout(2) + styling(1) |
| A-6 | Report Generation | Implement write_report() markdown template rendering | 10 | template(3) + formatting(2) + file_write(2) + validation(3) |
| A-7 | Pipeline Integration | Wire main() with error handling and JSON output | 9 | path_resolution(3) + main_flow(2) + json_save(2) + logging(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-2, A-3, A-7], Low(4-8): [A-1, A-4, A-6]

**Total Complexity**: 66 (reasonable for 200-line script)

---

## Implementation Notes

**Statistics Computation** (A-2):
```python
def compute_stats(tactic_counts: np.ndarray) -> dict:
    mean = np.mean(tactic_counts)
    std = np.std(tactic_counts, ddof=1)
    cv = std / mean
    ci = stats.t.interval(0.95, len(tactic_counts)-1, 
                          loc=mean, 
                          scale=stats.sem(tactic_counts))
    return {
        'n': len(tactic_counts),
        'mean': mean,
        'std': std,
        'cv': cv,
        'median': np.median(tactic_counts),
        'iqr': np.percentile(tactic_counts, 75) - np.percentile(tactic_counts, 25),
        'min': np.min(tactic_counts),
        'max': np.max(tactic_counts),
        'q1': np.percentile(tactic_counts, 25),
        'q3': np.percentile(tactic_counts, 75),
        'ci_mean_lower': ci[0],
        'ci_mean_upper': ci[1]
    }
```

**Budget Decision Tree** (A-3):
```python
def recommend_budget(stats: dict) -> Tuple[int, str, float]:
    cv = stats['cv']
    mean = stats['mean']
    std = stats['std']
    
    if cv <= 0.5:
        budget = int(np.ceil(mean + std))
        estimator = "mean+1σ"
    elif cv <= 1.0:
        budget = int(np.ceil(mean + 1.4 * std))
        estimator = "mean+1.4σ"
    else:
        return None, "unreliable", 0.0
    
    # Compute coverage from raw data (not stats dict)
    # Caller must pass tactic_counts array separately
    return budget, estimator, coverage
```

**ECDF Plot** (A-5):
```python
def plot_ecdf(ax, tactic_counts, budget):
    sorted_data = np.sort(tactic_counts)
    ecdf = np.arange(1, len(sorted_data)+1) / len(sorted_data)
    ax.plot(sorted_data, ecdf, marker='o', markersize=4, linestyle='none')
    ax.axvline(budget, color='red', linestyle='--', label=f'Budget={budget}')
    coverage = np.sum(tactic_counts <= budget) / len(tactic_counts)
    ax.text(budget, 0.5, f'{coverage:.1%}', ha='left')
    ax.set_xlabel('Tactic Count')
    ax.set_ylabel('Cumulative Probability')
    ax.legend()
```

---

## Validation Checklist

- [ ] Script loads H-E1 results.csv without errors
- [ ] Filter produces N=32 (verify against H-E1 report)
- [ ] Computed CV matches H-E1 baseline (≈0.45)
- [ ] Budget recommendation = 15 with estimator="mean+1.4σ"
- [ ] Gate decision = PASS (CV ≤ 1.0)
- [ ] Coverage ≈ 80% (verify from ECDF plot)
- [ ] summary.json is valid JSON with all fields
- [ ] PNG renders correctly (3 panels, budget line visible)
- [ ] 04_validation.md is readable markdown
- [ ] Pipeline runs in < 30 seconds
