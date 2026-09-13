# Architecture: H-E1

**Hypothesis:** H-E1 — EvalPlus Failure Set Data Integrity Verification
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-22
**Applied:** standard verification script pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; JSON schema confirmed from experiment brief direct inspection of h-e1 Run 2 eval_results files

---

## File Structure

- `h-e1/code/`
  - `verify_h_e1.py` — main entrypoint, orchestrates all checks
  - `data_loader.py` — JSON load + failure extraction
  - `api_verifier.py` — EvalPlus API import check + task_id cross-reference
  - `figure_generator.py` — 4 matplotlib figures
  - `report_writer.py` — JSON report + gate logic
- `h-e1/results/`
  - `verification_report.json`
- `h-e1/figures/`
  - `gate_metrics.png`
  - `failure_distribution.png`
  - `completeness_matrix.png`
  - `failing_tests_histogram.png`

---

## Modules

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies**: `json` (stdlib)

```python
ARCHIVE = "docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results"
HE_FILE = "humaneval_samples_eval_results.json"
MBPP_FILE = "mbpp_samples_eval_results.json"

def load_failures(archive: str = ARCHIVE) -> tuple[dict, dict]:
    """Returns (he_failures, mbpp_failures) where each is {task_id: record}."""
    ...

def verify_counts(he_failures: dict, mbpp_failures: dict) -> None:
    """Asserts len(he_failures)==34, len(mbpp_failures)==100, total==134."""
    ...

def verify_fields(failures: dict) -> None:
    """Asserts each record has non-empty solution and plus_fail_tests."""
    ...
```

---

### ApiVerifier (`h-e1/code/api_verifier.py`)

**Dependencies**: `evalplus.data`

```python
def verify_api_accessible() -> tuple[dict, dict]:
    """Imports get_human_eval_plus, get_mbpp_plus; asserts both return non-empty dicts.
    Returns (he_problems, mbpp_problems)."""
    ...

def verify_task_ids(he_failures: dict, mbpp_failures: dict,
                    he_problems: dict, mbpp_problems: dict) -> None:
    """Asserts all 34 HE+ task_ids in he_problems; all 100 MBPP+ in mbpp_problems."""
    ...
```

---

### FigureGenerator (`h-e1/code/figure_generator.py`)

**Dependencies**: `matplotlib`, `numpy`, `data_loader`

```python
FIGURES_DIR = "h-e1/figures"

def plot_gate_metrics(he_count: int, mbpp_count: int, output_dir: str = FIGURES_DIR) -> None:
    """Bar chart: actual vs. expected counts (34/34, 100/100, 134/134)."""
    ...

def plot_failure_distribution(he_count: int, mbpp_count: int, output_dir: str = FIGURES_DIR) -> None:
    """Pie chart: 34 HE+ (25.4%) vs. 100 MBPP+ (74.6%)."""
    ...

def plot_completeness_matrix(he_failures: dict, mbpp_failures: dict,
                              he_problems: dict, mbpp_problems: dict,
                              output_dir: str = FIGURES_DIR) -> None:
    """Heatmap: 134 tasks x {solution_present, plus_fail_tests_present, task_in_api}."""
    ...

def plot_failing_tests_histogram(he_failures: dict, mbpp_failures: dict,
                                  output_dir: str = FIGURES_DIR) -> None:
    """Histogram of plus_fail_tests list lengths across all 134 problems."""
    ...

def generate_all(he_failures: dict, mbpp_failures: dict,
                 he_problems: dict, mbpp_problems: dict,
                 output_dir: str = FIGURES_DIR) -> None:
    """Calls all four plot functions."""
    ...
```

---

### ReportWriter (`h-e1/code/report_writer.py`)

**Dependencies**: `json` (stdlib)

```python
RESULTS_DIR = "h-e1/results"

def write_report(checks: dict, he_count: int, mbpp_count: int,
                 output_dir: str = RESULTS_DIR) -> dict:
    """Writes verification_report.json. Returns report dict with gate field."""
    # report schema:
    # {
    #   "gate": "PASS" | "FAIL",
    #   "he_failures": int,
    #   "mbpp_failures": int,
    #   "total": int,
    #   "checks": {check_name: "PASS" | "FAIL"},
    #   "timestamp": str
    # }
    ...
```

---

### Main (`h-e1/code/verify_h_e1.py`)

**Dependencies**: `data_loader`, `api_verifier`, `figure_generator`, `report_writer`, `logging`

```python
def run_verification() -> dict:
    """Orchestrates all steps; returns final report dict."""
    ...

if __name__ == "__main__":
    run_verification()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | pip install evalplus matplotlib numpy; verify archive path exists; create output dirs | 4 | 1+1+1+1 |
| A-2 | Data Loader | Implement load_failures, verify_counts, verify_fields; covers FR-1 through FR-5 | 9 | 2+2+3+2 |
| A-3 | EvalPlus API Verifier | Implement verify_api_accessible + verify_task_ids; covers FR-6, FR-7 | 7 | 2+2+2+1 |
| A-4 | Figure Generator | Implement all 4 matplotlib figures; covers FR-8 | 10 | 3+2+3+2 |
| A-5 | Report Writer + Main | Implement write_report + run_verification orchestration; covers FR-9 | 7 | 2+2+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4], Low(4-8): [A-1, A-3, A-5]

---

## Data Flow

- `verify_h_e1.py` calls `data_loader.load_failures()` → (he_failures, mbpp_failures)
- `data_loader.verify_counts()` + `verify_fields()` → asserts inline
- `api_verifier.verify_api_accessible()` → (he_problems, mbpp_problems)
- `api_verifier.verify_task_ids()` → asserts inline
- `figure_generator.generate_all()` → 4 PNG files written
- `report_writer.write_report()` → JSON file written, report dict returned

---

## Constants

| Name | Value |
|------|-------|
| ARCHIVE | `docs/youra_research/_archive/20260822T150921_routing_recovery/h-e1/results` |
| HE_EXPECTED | 34 |
| MBPP_EXPECTED | 100 |
| TOTAL_EXPECTED | 134 |
| FIGURES_DIR | `h-e1/figures` |
| RESULTS_DIR | `h-e1/results` |

---

## Dependencies

```
evalplus>=0.3.1
matplotlib>=3.5.0
numpy>=1.21.0
```
stdlib: `json`, `logging`, `pathlib`, `datetime`
