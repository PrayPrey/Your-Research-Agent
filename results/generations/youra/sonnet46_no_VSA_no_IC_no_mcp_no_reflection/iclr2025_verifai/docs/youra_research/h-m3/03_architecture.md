# Architecture: H-M3 Feedback-Guided Repair Loop

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Type:** MECHANISM — incremental from H-M2

Applied: repair-loop-per-iteration-tracking pattern (Olausson 2023 / Reflexion)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 exists)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: H-M2 uses `FeedbackMeasurer` (not separate verifier classes); verifiers are methods on one class (`measure_execution`, `measure_pyright`, `measure_mypy`, `measure_z3`). No standalone `ExecutionVerifier`, `PyrightVerifier`, etc. classes exist. H-M3 must wrap or adapt `FeedbackMeasurer` methods into per-category verifier objects, or call methods directly. Module layout: flat `src/` with `measure.py`, `analyze.py`, `visualize.py`, `write_results.py`, `load_h_m1.py`, `z3_extractor.py`. Entry point: `run_h_m2.py`.

---

## External Dependencies (H-M2 Base Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| FeedbackMeasurer | `from src.measure import FeedbackMeasurer` | `h-m2/code/src/measure.py` |
| Z3ConstraintExtractor | `from src.z3_extractor import Z3ConstraintExtractor` | `h-m2/code/src/z3_extractor.py` |
| load_failing_records | `from src.load_h_m1 import load_failing_records` | `h-m2/code/src/load_h_m1.py` |
| write_records / write_summary | `from src.write_results import write_records, write_summary` | `h-m2/code/src/write_results.py` |

**Note**: H-M2 has NO standalone `ExecutionVerifier` / `PyrightVerifier` classes. PRD spec diverges from actual implementation. H-M3 wraps `FeedbackMeasurer` methods into thin adapter objects.

**Verified from**: `docs/youra_research/h-m2/code/` (actual implementation)

---

## File Structure

H-M3 code lives at `docs/youra_research/h-m3/code/`:

- `run_h_m3.py` — entry point, orchestrates full experiment
- `src/__init__.py`
- `src/verifier_adapters.py` — wraps H-M2 FeedbackMeasurer into per-category verifier objects
- `src/repair_loop.py` — `run_repair_loop()` core logic
- `src/analyze.py` — Spearman correlation + bootstrap CI + ablations
- `src/visualize.py` — 5 required figures
- `src/write_results.py` — JSONL + summary JSON persistence
- `results/h-m3/` — runtime output (results.jsonl, summary.json)
- `figures/` — 5 PNG figures (shared sibling to code/)

---

## Modules

### VerifierAdapters (`src/verifier_adapters.py`)

**Dependencies**: H-M2 `FeedbackMeasurer`, H-M2 `Z3ConstraintExtractor`

```python
import sys, os
# Add h-m2/code to path at import time
H_M2_CODE = Path(__file__).parents[3] / "h-m2" / "code"
sys.path.insert(0, str(H_M2_CODE))

from src.measure import FeedbackMeasurer
from src.z3_extractor import Z3ConstraintExtractor

class BaseVerifier:
    category: str
    def get_feedback(self, solution: str, problem: dict) -> str: ...

class ExecutionVerifier(BaseVerifier):
    def __init__(self, measurer: FeedbackMeasurer): ...
    def get_feedback(self, solution: str, problem: dict) -> str: ...
    # Runs measurer.measure_execution(problem["runnable_with_solution"])

class PyrightVerifier(BaseVerifier):
    def __init__(self, measurer: FeedbackMeasurer): ...
    def get_feedback(self, solution: str, problem: dict) -> str: ...

class MypyVerifier(BaseVerifier):
    def __init__(self, measurer: FeedbackMeasurer): ...
    def get_feedback(self, solution: str, problem: dict) -> str: ...

class Z3Verifier(BaseVerifier):
    def __init__(self, measurer: FeedbackMeasurer, extractor: Z3ConstraintExtractor): ...
    def get_feedback(self, solution: str, problem: dict) -> str: ...

def build_verifiers(measurer: FeedbackMeasurer, extractor: Z3ConstraintExtractor) -> dict[str, BaseVerifier]: ...
# Returns {"execution": ..., "pyright": ..., "mypy": ..., "z3": ...}
```

### RepairLoop (`src/repair_loop.py`)

**Dependencies**: VerifierAdapters, openai

```python
from openai import OpenAI

REPAIR_PROMPT_TEMPLATE: str  # Module-level constant

def call_llm(prompt: str, client: OpenAI, model: str, temperature: float) -> str: ...

def evaluate_solution(solution: str, problem: dict) -> bool: ...
# Runs solution + test harness in subprocess; returns pass/fail

def run_repair_loop(
    problem: dict,           # {task_id, prompt, runnable, code, test_code, entry_point}
    initial_solution: str,
    verifier,                # BaseVerifier instance
    client: OpenAI,
    model: str = "gpt-4o-mini",
    max_iterations: int = 3,
    temperature: float = 0.0,
) -> dict: ...
# Returns: {problem_id, category, iter1_pass, iter2_pass, iter3_pass,
#           iterations_to_pass, feedback_length}

def verify_mechanism(problems_sample: list[dict], verifiers: dict, client: OpenAI) -> None: ...
# Sanity check: fires repair loop once per category, asserts iter1_pass is bool
```

### Analyze (`src/analyze.py`)

**Dependencies**: scipy, numpy, pandas

```python
from scipy.stats import spearmanr
import numpy as np

SPECIFICITY_RANKS: dict[str, int]  # {"pyright": 1, "execution": 2, "mypy": 3, "z3": 4}

def compute_iter_rates(records: list[dict]) -> dict[str, dict]: ...
# Returns {category: {iter1_rate, iter2_rate, iter3_rate, n, n_passed}}

def bootstrap_ci(successes: list[bool], n_bootstrap: int = 1000, ci: float = 0.95) -> tuple[float, float]: ...

def run_spearman(iter_rates: dict[str, dict], include_z3: bool = True) -> dict: ...
# Returns {rho, pval, gate_pass (rho > 0), ranks_used, rates_used}

def run_ablations(records: list[dict]) -> dict: ...
# without_z3, iter2_correlation, by_dataset, bug_type_subgroup

def run_analysis(records: list[dict]) -> dict: ...
# Top-level: iter_rates + spearman (with/without z3) + ablations + gate_result
```

### Visualize (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, pandas, analyze

```python
def plot_bar_iter1_rate(iter_rates: dict, figures_dir: str) -> None: ...
# figures/bar_iter1_rate.png — bar + 95% CI

def plot_line_cumulative_repair(records: list[dict], figures_dir: str) -> None: ...
# figures/line_cumulative_repair.png — 4 lines × 3 iterations

def plot_heatmap_mean_iterations(records: list[dict], figures_dir: str) -> None: ...
# figures/heatmap_mean_iterations.png — bug_type × category

def plot_scatter_length_vs_rate(iter_rates: dict, figures_dir: str) -> None: ...
# figures/scatter_length_vs_rate.png — mean char_count vs iter1_rate + regression

def plot_scatter_z3_subgroup(records: list[dict], figures_dir: str) -> None: ...
# figures/scatter_z3_subgroup.png — Z3 N≈8 with annotation

def generate_all_figures(records: list[dict], iter_rates: dict, figures_dir: str) -> None: ...
```

### WriteResults (`src/write_results.py`)

**Dependencies**: json

```python
def write_records(records: list[dict], path: str) -> None: ...
# JSONL, one record per (problem_id, category) with iter1/2/3_pass + feedback_length

def write_summary(analysis: dict, path: str) -> None: ...
# JSON: iter_rates, spearman_with_z3, spearman_without_z3, gate_result, ablations
```

### Entry Point (`run_h_m3.py`)

**Dependencies**: all src modules, openai, concurrent.futures

```python
def main() -> None: ...
# Step 1: load H-M1 failing solutions (reuse load_failing_records from H-M2)
# Step 2: build verifiers (FeedbackMeasurer + adapters)
# Step 3: verify_mechanism() sanity check
# Step 4: parallel repair loop (4 workers, problem-level)
#         — each problem: run_repair_loop × 4 categories sequentially
# Step 5: run_analysis()
# Step 6: generate_all_figures()
# Step 7: write_records() + write_summary()
# Step 8: print gate verdict
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project scaffold | Create h-m3/code/ structure, copy/adapt write_results.py from H-M2, configure paths | 5 | 1+1+1+2 |
| A-2 | VerifierAdapters | Wrap FeedbackMeasurer methods into BaseVerifier interface; handle raw feedback string extraction from measure dicts | 10 | 2+3+3+2 |
| A-3 | evaluate_solution | Subprocess-based pass/fail for repair output; handle markdown fences, injection of test harness | 12 | 3+2+4+3 |
| A-4 | RepairLoop core | `run_repair_loop()`: prompt build, LLM call, evaluate, per-iter tracking, early exit, feedback_length logging | 14 | 3+3+4+4 |
| A-5 | verify_mechanism | Sanity check function; integration test that fires loop once per category with intentionally wrong solution | 7 | 1+2+2+2 |
| A-6 | load_failing_records reuse | Wire H-M2 `load_failing_records()` for H-M3 context; verify problem dict has needed fields (prompt, runnable, test_code, entry_point) | 8 | 1+3+2+2 |
| A-7 | Parallel experiment runner | ThreadPoolExecutor (4 workers); problem-level parallelism; sequential per-category within problem; result collection + progress logging | 11 | 2+3+3+3 |
| A-8 | Statistical analysis | `compute_iter_rates`, `bootstrap_ci`, `run_spearman` (with/without Z3), ablations (4 types), gate verdict | 13 | 3+2+5+3 |
| A-9 | Visualization | 5 figures (bar, line, heatmap, scatter×2); seaborn heatmap + matplotlib subplots | 11 | 2+2+4+3 |
| A-10 | Result persistence | write_records JSONL + write_summary JSON; schema per PRD FR-8 | 5 | 1+1+2+1 |
| A-11 | Entry point integration | run_h_m3.py wiring all steps; gate verdict print; error handling for partial failures | 9 | 2+2+3+2 |
| A-12 | End-to-end smoke test | Run with N=5 problems × 4 categories; verify output files exist and gate metric computed | 8 | 1+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-3, A-7, A-8, A-9, A-11], Low(4-8): [A-1, A-2, A-5, A-6, A-10, A-12]

**Total complexity**: 113 points across 12 epics

---

## Key Design Notes

- H-M2 has NO standalone verifier classes — `FeedbackMeasurer` must be wrapped. `get_feedback()` returns the raw string (stderr/stdout for execution, raw JSON string for pyright, mypy text output, z3 model string).
- Z3 adapter requires `Z3ConstraintExtractor` for constraint extraction before calling `measure_z3`. Z3Verifier must handle `None` constraints (returns empty string feedback → problem skipped from Z3 repair sequence).
- `evaluate_solution` is a NEW function in H-M3 (H-M2 only measured feedback, never evaluated correctness). It must inject the solution body into the problem's test harness and execute in subprocess.
- Parallelism: problem-level (4 workers), sequential per category within each problem — ensures controlled measurement per PRD NFR.
- figures/ directory at `docs/youra_research/h-m3/figures/` (sibling to code/).
