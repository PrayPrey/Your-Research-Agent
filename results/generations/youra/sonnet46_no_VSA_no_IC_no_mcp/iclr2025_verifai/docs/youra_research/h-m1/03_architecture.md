# H-M1 Architecture

Applied: iterative-repair-loop
Applied: mypy-feedback-channel
Applied: spearman-correlation-verification

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 extension)
**Status**: Patterns found from base code (Read tool)
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has flat file layout — `pipeline.py` owns all core logic (load, generate, evaluate, run_mypy, aggregate). `run.py` is the entry point. `visualize.py` owns all figure generation. All imports are local via `sys.path.insert`. H-M1 extends this pattern with two new files (`repair_loop.py`, `analysis.py`) and replaces `run.py` and `visualize.py`.

---

## File Organization

```
docs/youra_research/h-m1/code/
├── pipeline.py        # Re-exports H-E1 functions + adds repair prompt builder
├── repair_loop.py     # Condition B repair loop (NEW)
├── analysis.py        # Spearman ρ computation + trajectory stats (NEW)
├── visualize.py       # H-M1 figures (NEW — replaces H-E1 visualize.py)
└── run.py             # Experiment entry point (NEW)

docs/youra_research/h-m1/
├── results/           # JSONL + summary JSON
└── figures/           # PNG outputs
```

---

## External Dependencies (Base Hypothesis)

| Function | Import Path | File Location |
|----------|-------------|---------------|
| `load_problems` | `from pipeline import load_problems` | `h-e1/code/pipeline.py` |
| `build_prompt` | `from pipeline import build_prompt` | `h-e1/code/pipeline.py` |
| `extract_code` | `from pipeline import extract_code` | `h-e1/code/pipeline.py` |
| `evaluate_solution` | `from pipeline import evaluate_solution` | `h-e1/code/pipeline.py` |
| `run_mypy` | `from pipeline import run_mypy` | `h-e1/code/pipeline.py` |
| `generate_solution` | `from pipeline import generate_solution` | `h-e1/code/pipeline.py` |

**Verified from**: `docs/youra_research/h-e1/code/pipeline.py`

H-M1 `pipeline.py` adds `sys.path.insert` to H-E1 code dir and re-exports these, plus adds `build_repair_prompt`.

---

## Module Definitions

### pipeline (`code/pipeline.py`)

**Dependencies**: H-E1 pipeline (via sys.path), openai

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code"))

# Re-export from H-E1
from pipeline import (  # noqa: F401
    load_problems,
    build_prompt,
    extract_code,
    generate_solution,
    evaluate_solution,
    run_mypy,
    MYPY_FLAGS,
    MYPY_TIMEOUT,
)

SEED = 42
BENCHMARKS = ["mbpp+", "humaneval+"]
K_MAX = 5
RESULTS_DIR = pathlib.Path("docs/youra_research/h-m1/results")

def build_repair_prompt(
    problem: dict,
    prev_solution: str,
    exec_feedback: str,
    mypy_stdout: str,
) -> str: ...
```

---

### repair_loop (`code/repair_loop.py`)

**Dependencies**: pipeline, openai

```python
from openai import OpenAI

def repair_loop_condition_b(
    client: OpenAI,
    task_id: str,
    problem: dict,
    seed: int,
    k_max: int = 5,
) -> list[dict]:
    """Run k=1..5 repair rounds with execution+mypy feedback.

    Returns list of dicts:
      {"task_id", "round", "mypy_error_count", "mypy_stdout",
       "exec_passed", "solution"}
    Early-exits if exec_passed=True.
    """
    ...

def run_all_benchmarks(
    client: OpenAI,
    benchmarks: list[str],
    seed: int,
    k_max: int = 5,
) -> list[dict]:
    """Run repair loop across all benchmarks; return flat record list."""
    ...
```

---

### analysis (`code/analysis.py`)

**Dependencies**: scipy, statistics

```python
def compute_mean_errors_per_round(
    records: list[dict],
    benchmark: str,
    k_max: int = 5,
) -> dict[int, dict]:
    """Return {round_k: {"mean": float, "std": float, "n": int}}
    over problems with ≥1 mypy error at round 1."""
    ...

def compute_spearman(
    mean_errors_per_round: dict[int, dict],
) -> tuple[float, float]:
    """Return (rho, pval) from scipy.stats.spearmanr on trajectory."""
    ...

def verify_mechanism_activated(
    records: list[dict],
    benchmark: str = "mbpp+",
) -> tuple[bool, dict]:
    """Return (activated, indicators) where indicators includes rho, pval,
    log_found, rho_negative, round5_less_than_round1."""
    ...

def aggregate_results(
    records: list[dict],
    k_max: int = 5,
) -> dict:
    """Return summary dict per benchmark: trajectory + spearman + gate."""
    ...
```

---

### visualize (`code/visualize.py`)

**Dependencies**: matplotlib, numpy, analysis

```python
import pathlib

FIGURES_DIR = pathlib.Path("docs/youra_research/h-m1/figures")

def plot_error_trajectory(
    mean_errors: dict[str, dict[int, dict]],
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Line plot: mean mypy error count ± std vs round k, per benchmark."""
    ...

def plot_gate_bar(
    summary: dict,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Bar chart: mean error count per round for MBPP+ and HumanEval+."""
    ...

def plot_per_problem_heatmap(
    records: list[dict],
    benchmark: str,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Heatmap: problems × rounds of mypy error count."""
    ...

def plot_error_distribution(
    records: list[dict],
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None:
    """Box plots: distribution of per-problem mypy error counts per round."""
    ...

def generate_all_figures(
    records: list[dict],
    summary: dict,
    figures_dir: pathlib.Path = FIGURES_DIR,
) -> None: ...
```

---

### run (`code/run.py`)

**Dependencies**: pipeline, repair_loop, analysis, visualize, openai

```python
def main() -> None:
    """Entry point. Loads env, verifies mypy, runs repair loop,
    computes Spearman ρ, saves results + figures, logs gate result."""
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project scaffold | Create h-m1/code/ dir, pipeline.py with H-E1 re-exports and build_repair_prompt | 6 (2+1+1+2) | Module_Size=2, Deps=1, Algo=1, Integ=2 |
| A-2 | Repair loop core | Implement repair_loop_condition_b: initial gen → k rounds of exec+mypy feedback | 16 (4+3+5+4) | Module_Size=4, Deps=3, Algo=5, Integ=4 |
| A-3 | Benchmark runner | Implement run_all_benchmarks: iterate problems × benchmarks, collect records | 10 (3+2+2+3) | Module_Size=3, Deps=2, Algo=2, Integ=3 |
| A-4 | Analysis module | Implement compute_mean_errors_per_round, compute_spearman, verify_mechanism_activated, aggregate_results | 12 (3+2+4+3) | Module_Size=3, Deps=2, Algo=4, Integ=3 |
| A-5 | Visualization | Implement all 4 figure functions + generate_all_figures for H-M1 | 10 (3+2+3+2) | Module_Size=3, Deps=2, Algo=3, Integ=2 |
| A-6 | run.py entry point | Orchestrate: env check, repair loop, analysis, save results, gate evaluation | 9 (2+3+1+3) | Module_Size=2, Deps=3, Algo=1, Integ=3 |
| A-7 | Integration test | Dry-run on 2 problems per benchmark, verify records shape and Spearman call | 7 (2+2+1+2) | Module_Size=2, Deps=2, Algo=1, Integ=2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2], Medium(9-13): [A-3, A-4, A-5, A-6], Low(4-8): [A-1, A-7]
