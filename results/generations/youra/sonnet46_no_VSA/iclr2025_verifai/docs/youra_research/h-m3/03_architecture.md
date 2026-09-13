# Architecture: H-M3 Adaptive PBT Contribution Experiment

**Applied: incremental-hypothesis reuse pattern** (H-M1 static oracle results reused; only Exp B is new)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3 extends H-M1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: H-M1 uses flat module layout with function-level APIs (no classes). Key modules: `data_loader.py` (functions: `load_contracteval`, `load_evalplus_data`, `load_h1_corpus`, `verify_task_overlap`), `statistical_analysis.py` (functions + `AggregatedStats` dataclass, `bootstrap_ci`, `wilcoxon_holm`), `visualization.py` (function-per-plot pattern, `_save` helper). H-M3 follows identical layout and reuses these directly via `sys.path.insert`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_contracteval | `from data_loader import load_contracteval` | `h-m1/code/data_loader.py` |
| load_evalplus_data | `from data_loader import load_evalplus_data` | `h-m1/code/data_loader.py` |
| load_h1_corpus | `from data_loader import load_h1_corpus` | `h-m1/code/data_loader.py` |
| verify_task_overlap | `from data_loader import verify_task_overlap` | `h-m1/code/data_loader.py` |
| bootstrap_ci | `from statistical_analysis import bootstrap_ci` | `h-m1/code/statistical_analysis.py` |
| wilcoxon_holm | `from statistical_analysis import wilcoxon_holm` | `h-m1/code/statistical_analysis.py` |
| _save (viz helper) | `from visualization import _save` | `h-m1/code/visualization.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

**H-M1 results path constants** (from actual `data_loader.py` path resolution pattern):
- ContractEval JSONL: resolved via `Path(__file__).parent.parent.parent / "_archive" / ... / "ContractEval.jsonl"`
- H-E1 samples: `h-e1/code/data/samples/*.jsonl`
- H-M1 Exp A results: `h-m1/results/oracle_isolation_results.json`

---

## Base Code Reuse

### Reused from H-M1 (no modification)

| Module | Functions | Notes |
|--------|-----------|-------|
| `data_loader.py` | `load_contracteval`, `load_h1_corpus`, `verify_task_overlap` | Add via sys.path to h-m1/code/ |
| `statistical_analysis.py` | `bootstrap_ci`, `wilcoxon_holm` | Reused as-is |
| `visualization.py` | `_save` helper | Reused as-is |

### New modules (H-M3 only)

- `data_loader.py` — thin H-M3 wrapper: adds `load_exp_a_results()`
- `compatibility_check.py` — 20-task pre-check for filter rate calibration
- `experiment_b_runner.py` — core adaptive PBT (icontract-hypothesis)
- `yield_checker.py` — per-task yield analysis + quarantine logic
- `adaptive_contribution.py` — paired Exp_B − Exp_A computation + stats
- `visualization.py` — H-M3 figures (reuses `_save` from H-M1)
- `run_experiment.py` — orchestration entry point

---

## File Organization

```
h-m3/code/
├── data_loader.py
├── compatibility_check.py
├── experiment_b_runner.py
├── yield_checker.py
├── adaptive_contribution.py
├── visualization.py
└── run_experiment.py
h-m3/results/
├── experiment_b_results.jsonl
├── per_task_adaptive_contribution.csv
├── low_yield_tasks.csv
└── summary_report.md
h-m3/figures/
├── gate_metrics_adaptive_contribution.png
├── scatter_exp_a_vs_exp_b.png
├── adaptive_gap_distribution.png
├── filter_rate_distribution.png
├── model_stratified_contribution.png
└── task_type_breakdown.png
```

---

## Module Interfaces

### data_loader (`h-m3/code/data_loader.py`)

**Dependencies**: h-m1/code/data_loader (via sys.path), json, pathlib

```python
H1_CODE_DIR: Path  # = Path(__file__).parent.parent.parent / "h-m1" / "code"
H1_RESULTS_DIR: Path  # = Path(__file__).parent.parent.parent / "h-m1" / "results"

def load_exp_a_results(results_path: str | None = None) -> list[dict]: ...
    # Loads h-m1/results/oracle_isolation_results.json
    # Returns list of {task_id, model, program_idx, static_failure_rate, failed_inputs}

def load_contracteval_tasks() -> dict: ...
    # Thin wrapper: sys.path.insert(0, H1_CODE_DIR); from data_loader import load_contracteval

def load_llm_corpus() -> dict: ...
    # Thin wrapper: from data_loader import load_h1_corpus; returns {model: {task_id: [code_str]}}
```

---

### compatibility_check (`h-m3/code/compatibility_check.py`)

**Dependencies**: data_loader, experiment_b_runner, random

```python
def run_compatibility_precheck(
    tasks: dict,
    corpus: dict,
    n_tasks: int = 20,
    seed: int = 42,
    min_valid: int = 100,
    max_filter_rate: float = 0.95,
) -> dict: ...
    # Samples n_tasks from tasks; runs experiment_b_runner.run_triple on one program per task
    # Returns {task_id: {filter_rate, n_valid, passed: bool}}

def check_precheck_gate(precheck_results: dict, min_passing: int = 15) -> tuple[bool, dict]: ...
    # Returns (gate_passed, summary). Gate: >=15/20 tasks with n_valid >= 100
```

---

### experiment_b_runner (`h-m3/code/experiment_b_runner.py`)

**Dependencies**: icontract, icontract_hypothesis, hypothesis, signal, multiprocessing

```python
@dataclass
class TripleResult:
    task_id: str
    model: str
    program_idx: int
    adaptive_failure_rate: float
    n_valid: int
    n_failures: int
    filter_rate: float
    error: str | None

def run_triple(
    llm_code: str,
    contracteval_task: dict,
    task_id: str,
    model: str,
    program_idx: int,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
) -> TripleResult: ...
    # Wraps llm_code with @require/@ensure from contracteval_task
    # Runs icontract_hypothesis.test_with_inferred_strategy
    # Catches ViolationError, StrategyInferenceError, TimeoutError
    # ponytail: SIGALRM timeout (same pattern as h-m1/code), not multiprocessing timeout

def run_experiment_b(
    tasks: dict,
    corpus: dict,
    budget: int = 5000,
    timeout_secs: int = 60,
    rng_seed: int = 42,
    n_workers: int = 16,
    output_path: str = "results/experiment_b_results.jsonl",
) -> list[TripleResult]: ...
    # multiprocessing.Pool over (model, task_id, program_idx) triples
    # Writes each TripleResult to JSONL incrementally
    # Returns all results

def verify_experiment_b_activated(results: list[TripleResult]) -> tuple[bool, dict]: ...
    # Checks: yield_sufficient, filter_not_total, adaptive_gap_measurable, triples_covered
    # Gate: >= 3/4 indicators pass
```

---

### yield_checker (`h-m3/code/yield_checker.py`)

**Dependencies**: pandas, dataclasses

```python
def compute_yield_stats(results: list[dict]) -> dict: ...
    # Groups by task_id; computes mean n_valid, mean filter_rate per task
    # Returns {task_id: {mean_n_valid, mean_filter_rate, low_yield: bool}}

def get_low_yield_tasks(
    yield_stats: dict,
    filter_rate_threshold: float = 0.95,
    min_valid: int = 100,
) -> list[str]: ...
    # Returns task_ids where low_yield=True

def get_excluded_tasks(yield_stats: dict) -> list[str]: ...
    # Tasks where ALL triples have n_valid = 0 (exclude from paired comparison)

def save_low_yield_report(
    yield_stats: dict,
    out_path: str = "results/low_yield_tasks.csv",
) -> None: ...
```

---

### adaptive_contribution (`h-m3/code/adaptive_contribution.py`)

**Dependencies**: numpy, scipy, pandas, h-m1/code/statistical_analysis (via sys.path)

```python
@dataclass
class ContributionStats:
    mean_adaptive_gap: float
    wilcoxon_stat: float
    wilcoxon_p_raw: float
    wilcoxon_p_holm: float
    ci_lower: float
    ci_upper: float
    fraction_tasks_gt_threshold: float  # tasks where mean_gap > 0.03
    by_model: dict  # {model: mean_gap}
    by_task_type: dict  # {"humaneval": mean_gap, "mbpp": mean_gap}
    gate_passed: bool
    n_paired_triples: int

def join_exp_a_b(
    exp_a: list[dict],
    exp_b: list[dict],
    excluded_tasks: list[str],
) -> tuple[list[float], list[float], list[dict]]: ...
    # Inner join on (task_id, model, program_idx)
    # Returns (exp_a_rates, exp_b_rates, paired_records)

def compute_adaptive_contribution(
    exp_a_rates: list[float],
    exp_b_rates: list[float],
    paired_records: list[dict],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> ContributionStats: ...
    # Wilcoxon signed-rank (alternative="greater") + Holm
    # bootstrap_ci on mean(exp_b - exp_a)
    # Per-model and per-task-type sub-analyses with Holm correction
    # Gate: mean_gap > 0 AND p_holm < 0.05

def save_results(
    stats: ContributionStats,
    paired_records: list[dict],
    results_dir: str = "results/",
) -> None: ...
    # Writes per_task_adaptive_contribution.csv and summary_report.md
```

---

### visualization (`h-m3/code/visualization.py`)

**Dependencies**: matplotlib, seaborn, numpy, pathlib

```python
def plot_gate_metrics(
    stats: "ContributionStats",
    out_path: str = "figures/gate_metrics_adaptive_contribution.png",
) -> None: ...

def plot_scatter_exp_a_vs_exp_b(
    paired_records: list[dict],
    out_path: str = "figures/scatter_exp_a_vs_exp_b.png",
) -> None: ...

def plot_adaptive_gap_distribution(
    paired_records: list[dict],
    out_path: str = "figures/adaptive_gap_distribution.png",
) -> None: ...

def plot_filter_rate_distribution(
    yield_stats: dict,
    out_path: str = "figures/filter_rate_distribution.png",
) -> None: ...

def plot_model_stratified(
    stats: "ContributionStats",
    out_path: str = "figures/model_stratified_contribution.png",
) -> None: ...

def plot_task_type_breakdown(
    stats: "ContributionStats",
    out_path: str = "figures/task_type_breakdown.png",
) -> None: ...
```

---

### run_experiment (`h-m3/code/run_experiment.py`)

**Dependencies**: all h-m3 modules, sys, json, pathlib

```python
# Entry point — no public API; run as __main__
# Execution order:
#   1. load_exp_a_results, load_contracteval_tasks, load_llm_corpus
#   2. run_compatibility_precheck -> check_precheck_gate (stop if fail)
#   3. run_experiment_b -> write experiment_b_results.jsonl
#   4. verify_experiment_b_activated (stop if <3/4 indicators pass)
#   5. compute_yield_stats -> save_low_yield_report
#   6. join_exp_a_b -> compute_adaptive_contribution -> save_results
#   7. all plot_* functions -> save to figures/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading + H-M1 bridge | `data_loader.py`: load Exp A results, corpus, ContractEval; sys.path bridge to h-m1; validate 364 tasks present | 8 | 2+2+2+2 |
| A-2 | Compatibility pre-check | `compatibility_check.py`: 20-task sample run, filter-rate calibration, gate check | 9 | 2+2+3+2 |
| A-3 | Experiment B runner — single triple | `experiment_b_runner.py`: icontract-hypothesis wrapping, SIGALRM timeout, TripleResult, StrategyInferenceError handling | 15 | 4+3+4+4 |
| A-4 | Experiment B runner — parallelism + JSONL output | multiprocessing.Pool over triples, incremental JSONL write, activation verifier | 13 | 3+3+4+3 |
| A-5 | Yield checker | `yield_checker.py`: per-task yield stats, low-yield flagging, excluded tasks (n_valid=0 all programs) | 7 | 2+2+2+1 |
| A-6 | Adaptive contribution computation | `adaptive_contribution.py`: join Exp A/B, Wilcoxon+Holm, bootstrap CI, per-model/task-type sub-analyses, ContributionStats | 14 | 3+3+4+4 |
| A-7 | Results persistence | `save_results` in adaptive_contribution.py: per_task CSV, summary_report.md | 6 | 1+2+2+1 |
| A-8 | Visualization (6 figures) | `visualization.py`: gate bar chart, scatter A vs B, gap histogram, filter histogram, model bars, task-type bars | 10 | 3+2+3+2 |
| A-9 | Orchestration + E2E run | `run_experiment.py`: wire all modules, precheck gate stop, activation verifier stop, full pipeline | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-6], Medium(9-13): [A-2, A-4, A-8, A-9], Low(4-8): [A-1, A-5, A-7]
