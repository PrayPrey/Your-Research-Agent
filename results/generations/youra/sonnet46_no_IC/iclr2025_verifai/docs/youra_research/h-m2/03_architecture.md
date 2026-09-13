---
title: "Architecture: H-M2 Pylint/Mypy Coverage on HumanEval Baseline Failures"
hypothesis_id: h-m2
hypothesis_type: MECHANISM
phase: 3
date: "2026-08-05"
status: complete
---

# Architecture: H-M2

Applied: measurement-only-script-per-file (no neural architecture)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 extends H-M1/H-E1)
**Status**: No `code/` directory found — H-M1 used flat scripts under `experiments/h-m1/`
**Analyzed Path**: `docs/youra_research/h-m1/` (results only; no source code directory exists)
**Findings**: H-M1 results stored as JSONL. Primary data source for H-M2 is `docs/youra_research/h-e1/results/baseline_humaneval.jsonl` — each line has `task_id`, `code`, `passed` fields (flat, no nesting). H-M1 execution JSONL has `rounds[0].code` (nested). H-E1 baseline is the simpler/preferred source.

---

## File Structure

```
experiments/h-m2/
├── run_experiment.py      # Entry point + orchestration
├── data_loader.py         # Load baseline failures from H-E1/H-M1
├── static_analyzer.py     # pylint+mypy per-file measurement
├── metrics.py             # Coverage fraction + bootstrap CI
├── visualizer.py          # 3 required figures
└── requirements.txt

results/h-m2/
├── coverage_results.json  # Per-task analysis results
├── metrics.json           # All computed metrics
└── summary.md             # Human-readable summary

docs/youra_research/h-m2/figures/
├── figure1_coverage_comparison.png
├── figure2_pylint_categories.png
└── figure3_venn_overlap.png
```

---

## External Dependencies (Base Hypothesis)

### Data Paths (Verified from Actual Results)

| File | Format | Code Field | Condition Field |
|------|--------|------------|-----------------|
| `docs/youra_research/h-e1/results/baseline_humaneval.jsonl` | JSONL | `code` (flat) | `condition=="baseline"`, `passed==False` |
| `docs/youra_research/h-m1/results/execution_humaneval_llama.jsonl` | JSONL | `rounds[0]["code"]` (nested) | `passed==False` |

**Priority**: H-E1 baseline JSONL first (flat `code` field, simpler). H-M1 execution JSONL as fallback.

---

## Module Definitions

### DataLoader (`experiments/h-m2/data_loader.py`)

**Dependencies**: stdlib (json, os, pathlib)

```python
BASELINE_SOURCES = [
    "docs/youra_research/h-e1/results/baseline_humaneval.jsonl",
    "docs/youra_research/h-m1/results/execution_humaneval_llama.jsonl",
    "docs/youra_research/h-m1/results/baseline_results.json",
    "docs/youra_research/h-e1/results/baseline_results.json",
]

def load_baseline_failures(sources: list[str] = BASELINE_SOURCES) -> list[dict]:
    """Load HumanEval baseline failure cases. Returns list of {task_id, code}."""
    ...

def _extract_code(record: dict) -> str:
    """Extract code string from flat or nested (rounds[0].code) format."""
    ...
```

---

### StaticAnalyzer (`experiments/h-m2/static_analyzer.py`)

**Dependencies**: pylint, mypy, stdlib (tempfile, os, io, subprocess)

```python
def analyze_file(code: str, task_id: str) -> dict:
    """
    Run pylint+mypy on code string via temp file.
    Returns {task_id, flagged, pylint_flagged, mypy_flagged,
             pylint_categories: {E,W,C,R,I}, pylint_message_count,
             mypy_error_count, pylint_output, mypy_output, error?}
    """
    ...

def _run_pylint(path: str) -> tuple[bool, dict, str]:
    """Primary: pylint.lint.Run() API. Fallback: subprocess json output."""
    ...

def _run_mypy(path: str) -> tuple[bool, int, str]:
    """mypy.api.run(['--ignore-missing-imports', '--no-strict-optional', path])"""
    ...

def run_coverage_measurement(cases: list[dict]) -> list[dict]:
    """Iterate cases, call analyze_file per case, return results list."""
    ...
```

---

### Metrics (`experiments/h-m2/metrics.py`)

**Dependencies**: numpy

```python
def compute_metrics(results: list[dict], n_bootstrap: int = 10000, seed: int = 42) -> dict:
    """
    Returns {n_total_failures, n_flagged, coverage, coverage_ci_lower,
             coverage_ci_upper, coverage_passes_gate, pylint_coverage,
             mypy_coverage, n_pylint_only, n_mypy_only, n_both_flagged,
             n_neither, pylint_category_totals: {E,W,C,R,I}}
    """
    ...

def _bootstrap_ci(flags: np.ndarray, n: int, seed: int) -> tuple[float, float]:
    """Bootstrap 95% CI on mean of binary array."""
    ...
```

---

### Visualizer (`experiments/h-m2/visualizer.py`)

**Dependencies**: matplotlib, metrics dict, results list

```python
def generate_figures(metrics: dict, results: list[dict], output_dir: str) -> None:
    """Generate and save all 3 required figures to output_dir."""
    ...

def _figure1_coverage_comparison(metrics: dict, ax) -> None:
    """Bar chart: combined/pylint/mypy coverage vs 50% threshold + CI errorbar."""
    ...

def _figure2_pylint_categories(metrics: dict, ax) -> None:
    """Bar chart: E/W/C/R flag counts."""
    ...

def _figure3_venn_overlap(metrics: dict, ax) -> None:
    """Manual Venn: pylint-only / mypy-only / both / neither counts."""
    ...
```

---

### Orchestrator (`experiments/h-m2/run_experiment.py`)

**Dependencies**: DataLoader, StaticAnalyzer, Metrics, Visualizer, argparse, json, os

```python
def parse_args() -> argparse.Namespace:
    """--h-e1-results, --h-m1-results, --output-dir, --figures-dir, --seed, --n-bootstrap"""
    ...

def main() -> None:
    """
    1. load_baseline_failures()
    2. run_coverage_measurement()
    3. save coverage_results.json
    4. compute_metrics()
    5. save metrics.json
    6. generate_figures()
    7. write summary.md
    8. print gate assessment
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Loading | Implement DataLoader: JSONL parsing, flat+nested code extraction, sanity checks [50,100] | 7 | 2+1+2+2 |
| A-2 | Static Analyzer | Implement analyze_file: pylint API + mypy API + subprocess fallback + temp file cleanup | 14 | 3+3+4+4 |
| A-3 | Metrics Computation | Coverage fraction, bootstrap CI (n=10000), per-category totals, Venn counts | 9 | 2+2+3+2 |
| A-4 | Visualization | 3 figures: coverage bar+CI, category breakdown, Venn diagram | 9 | 3+2+2+2 |
| A-5 | Orchestration | run_experiment.py: argparse CLI, pipeline wiring, JSON+MD output, gate print | 8 | 2+2+2+2 |
| A-6 | Validation & Docs | requirements.txt, end-to-end smoke test, README with CLI example | 5 | 1+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4], Low(4-8): [A-1, A-5, A-6]
