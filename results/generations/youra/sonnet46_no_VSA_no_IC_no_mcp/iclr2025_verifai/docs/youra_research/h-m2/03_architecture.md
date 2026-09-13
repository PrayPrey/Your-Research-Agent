---
hypothesis_id: H-M2
hypothesis_type: MECHANISM
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
base_hypothesis: H-M1
---

# Architecture: H-M2 — Mypy Feedback Specificity for Type-Related Failures

Applied: [INFERRED] iterative-repair-loop pattern (Archon MCP unavailable)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension
**Status**: Patterns found from base code (read directly — Serena MCP unavailable)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 has `repair_loop.py` (Condition B loop with mypy), `analysis.py`, `visualize.py`, `config.py`, `run.py`. Imports `pipeline.py` from `h-e1/code/` for `extract_code`, `generate_solution`, `evaluate_solution`, `load_problems`, `MYPY_FLAGS`. H-M2 reuses all five files; adds `condition_a_runner.py`, `category_labeling.py`, `load_condition_b.py` as the only new modules.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| run_mypy_with_output | `from h_m1_repair_loop import run_mypy_with_output` | `h-m1/code/repair_loop.py` |
| ExperimentConfig | `from h_m1_config import ExperimentConfig` | `h-m1/code/config.py` |
| generate_solution / evaluate_solution | `from pipeline import generate_solution, evaluate_solution` | `h-e1/code/pipeline.py` (via h-m1) |

> H-M2 `code/` runs from `docs/youra_research/h-m2/code/`. Sys-path additions needed for h-m1 and h-e1 imports — follow the pattern in `h-m1/code/repair_loop.py` lines 13-23.

---

## Module Structure

### config.py (`docs/youra_research/h-m2/code/config.py`)

**Dependencies**: stdlib only

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    model: str = "gpt-4o-mini"
    initial_temperature: float = 0.8
    repair_temperature: float = 0.0
    max_tokens: int = 2048
    seed: int = 42
    k_max: int = 5
    mypy_timeout: int = 10
    max_retries: int = 3
    retry_base_delay: float = 1.0
    h_m1_results: str = "docs/youra_research/h-m1/results/humaneval_all_rounds.jsonl"
    results_dir: str = "docs/youra_research/h-m2/results"
    figures_dir: str = "docs/youra_research/h-m2/figures"
```

---

### load_condition_b.py (`docs/youra_research/h-m2/code/load_condition_b.py`)

**Dependencies**: config.py

```python
def load_h_m1_results(jsonl_path: str) -> dict:
    """
    Returns: {task_id: [{round_k, mypy_error_count, exec_passed}]}
    """
    ...

def extract_initial_mypy_errors(h_m1_records: dict) -> dict:
    """
    Returns: {task_id: int}  — mypy error count at round k=1 (pre-repair)
    """
    ...

def extract_cond_b_pass_at_k(h_m1_records: dict, k: int = 5) -> dict:
    """
    Returns: {task_id: bool}  — whether problem passed EvalPlus at round k under Cond B
    """
    ...
```

---

### category_labeling.py (`docs/youra_research/h-m2/code/category_labeling.py`)

**Dependencies**: load_condition_b.py

```python
def label_problems(initial_mypy_errors: dict, failing_task_ids: set) -> dict:
    """
    Returns: {"type_error": [task_id, ...], "non_type_error": [task_id, ...]}
    Criteria: type_error if mypy_errors > 0; non_type_error if mypy_errors == 0 and failed.
    """
    ...

def verify_labels(labels: dict, expected_type_count: int = 20) -> None:
    """Assert type_error count matches H-M1 findings; warn if not."""
    ...
```

---

### condition_a_runner.py (`docs/youra_research/h-m2/code/condition_a_runner.py`)

**Dependencies**: config.py; h-e1/pipeline.py (generate_solution, evaluate_solution, extract_code)

```python
def build_condition_a_repair_prompt(problem: dict, prev_solution: str, exec_feedback: str) -> str:
    """Execution-only prompt — no mypy section."""
    ...

def run_condition_a_problem(
    problem: dict,
    task_id: str,
    client,
    cfg: Config,
) -> list[dict]:
    """
    Runs k=1..5 repair loop for one problem under Condition A.
    Returns: [{task_id, round_k, exec_passed, condition: "A"}]
    Early-exits if exec_passed.
    """
    ...

def run_condition_a_benchmark(
    problems: dict,
    benchmark: str,
    cfg: Config,
    checkpoint_path: str,
) -> dict:
    """
    Runs Condition A for all problems in benchmark with checkpoint/resume.
    Returns: {task_id: [{round_k, exec_passed}]}
    """
    ...
```

---

### analysis.py (`docs/youra_research/h-m2/code/analysis.py`)

**Dependencies**: category_labeling.py, load_condition_b.py

```python
def repair_rate(results: dict, task_ids: list, k: int = 5) -> float:
    """Fraction of task_ids that pass at any round <= k."""
    ...

def compute_differential(
    cond_a_results: dict,
    cond_b_pass_at_k: dict,
    labels: dict,
    k: int = 5,
) -> dict:
    """
    Returns:
      {
        "type":     {"A": float, "B": float, "delta": float},
        "non_type": {"A": float, "B": float, "delta": float},
        "differential": float,   # delta_type - delta_non (PRIMARY GATE)
        "gate_passed": bool,
        "mechanism_activated": bool,
      }
    """
    ...

def verify_mechanism(results: dict) -> bool:
    """Logs [H-M2] mechanism line; returns mechanism_activated bool."""
    ...
```

---

### visualize.py (`docs/youra_research/h-m2/code/visualize.py`)

**Dependencies**: analysis.py, matplotlib, numpy

```python
def plot_gate_metrics(results: dict, figures_dir: str) -> None:
    """Bar chart: delta_type vs delta_non with zero line. Saves gate_metrics.png."""
    ...

def plot_repair_rates_4bar(results: dict, figures_dir: str) -> None:
    """4-bar: rate_A_type, rate_B_type, rate_A_non, rate_B_non."""
    ...

def plot_round_curves(
    cond_a_results: dict,
    h_m1_records: dict,
    labels: dict,
    figures_dir: str,
) -> None:
    """4 cumulative pass-rate curves (category x condition) vs round k."""
    ...

def plot_heatmap(results: dict, figures_dir: str) -> None:
    """category x condition repair rate heatmap."""
    ...
```

---

### run.py (`docs/youra_research/h-m2/code/run.py`)

**Dependencies**: all modules above; evalplus, openai

```python
def main() -> None:
    """
    CLI entry point. Orchestrates:
    1. Load H-M1 Condition B data
    2. Label problems
    3. Run Condition A (HumanEval+ then MBPP+) with checkpoint/resume
    4. Compute differential analysis
    5. Generate all figures
    6. Persist results (summary.json, category_labels.json)
    """
    ...

if __name__ == "__main__":
    main()
```

---

## File Organization

```
docs/youra_research/h-m2/
  code/
    config.py
    load_condition_b.py
    category_labeling.py
    condition_a_runner.py
    analysis.py
    visualize.py
    run.py
  results/
    condition_a_humaneval.jsonl
    condition_a_mbpp.jsonl
    category_labels.json
    summary.json
  figures/
    gate_metrics.png
    *.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffolding | config.py + results/figures dirs | 5 | 1+1+1+2 |
| A-2 | Load Condition B data | load_condition_b.py: parse h-m1 JSONL, extract initial mypy errors and k=5 pass flags | 7 | 2+2+1+2 |
| A-3 | Category labeling | category_labeling.py: type_error vs non_type_error assignment + verify vs H-M1 counts | 6 | 2+2+1+1 |
| A-4 | Condition A runner | condition_a_runner.py: execution-only repair loop with checkpoint/resume for HumanEval+ + MBPP+ | 14 | 3+3+4+4 |
| A-5 | Differential analysis | analysis.py: repair_rate, compute_differential, verify_mechanism with logging | 9 | 2+2+3+2 |
| A-6 | Visualization | visualize.py: gate_metrics.png (required) + 3 autonomous figures | 8 | 2+2+2+2 |
| A-7 | Integration & run.py | Orchestrate all modules; end-to-end smoke test with 2 problems | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-5, A-7], Low(4-8): [A-1, A-2, A-3, A-6]
