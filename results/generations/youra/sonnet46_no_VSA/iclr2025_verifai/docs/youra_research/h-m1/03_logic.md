# Logic Specification: H-M1 Oracle Isolation Experiment

**Date:** 2026-08-03
**Type:** MECHANISM (PoC)
**Gate:** MUST_WORK — gap >= 0.10, Wilcoxon p < 0.01 (Holm), CU mass >= 0.05

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — new implementation, no base hypothesis code to verify
**Analyzed Path:** N/A (H-E1 output is data, not callable code)
**Relevant Symbols:** None — new implementation; H-E1 programs are text files, not importable modules

---

## Module Overview

Six modules in `h-m1/code/`:

| Module | Responsibility |
|--------|---------------|
| `data_loader.py` | Load ContractEval, EvalPlus inputs, H-E1 program corpus |
| `oracle_isolation.py` | Core per-input oracle evaluation and failure classification |
| `soundness_check.py` | Hypothesis PBT pre-check on reference implementations |
| `statistical_analysis.py` | Wilcoxon, Holm, bootstrap CI |
| `visualization.py` | Figure generation |
| `run_experiment.py` | Orchestration entry point |

---

## A-1: data_loader — Data Loading [Complexity: 2, Budget: 3]

Applied: Standard PyTorch/Python data loading patterns

### API Signatures

```python
# data_loader.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional
import types


@dataclass
class TaskData:
    task_id: str                      # ContractEval task ID (e.g. "HumanEval/0")
    evalplus_task_id: str             # Matched EvalPlus task ID (may differ)
    entry_point: str                  # Function name
    static_inputs: list               # List[list] — 764 inputs, each is list of args
    ground_truth_fn: Callable         # Canonical solution (compiled from evalplus)
    contract_module: types.ModuleType # Loaded ContractEval module with @require/@ensure
    contract_fn: Callable             # icontract-decorated reference function
    task_type: str                    # "humaneval" | "mbpp"
    fallback_generated: bool = False  # True if inputs generated via Hypothesis fallback


@dataclass
class ProgramCorpus:
    task_id: str
    model: str                        # e.g. "gpt-4o-mini"
    programs: list[str]               # Test-passing program source strings from H-E1


def load_contracteval_tasks(
    contracteval_dir: Path,
) -> dict[str, dict]:
    """Load ContractEval JSON/Python files. Returns {task_id: raw_task_dict}."""
    ...


def load_evalplus_inputs(
    task_ids: list[str],
    dataset: str = "humaneval",       # "humaneval" | "mbpp"
) -> dict[str, list[list]]:
    """Load EvalPlus base_input + plus_input. Returns {evalplus_task_id: [args_list]}."""
    # Uses evalplus.data.get_human_eval_plus() / get_mbpp_plus()
    # Returns all inputs as list of argument lists: [[arg1, arg2], ...]
    ...


def align_task_ids(
    contracteval_ids: list[str],
    evalplus_ids: list[str],
) -> tuple[dict[str, str], list[str]]:
    """Match ContractEval IDs to EvalPlus IDs. Returns (matched_map, unmatched_ce_ids).

    Alignment strategy:
    1. Exact match: "HumanEval/0" in both -> direct map
    2. Numeric suffix match: strip prefix, match by integer index
    3. MBPP: "MBPP/1" -> "Mbpp/1" normalization
    Unmatched IDs go to fallback input generation.
    """
    ...


def generate_fallback_inputs(
    contract_fn: Callable,
    n_inputs: int = 764,
    seed: int = 42,
) -> list[list]:
    """Generate inputs via Hypothesis + icontract preconditions for unmatched tasks.

    Uses icontract_hypothesis.make_strategy() to infer valid input strategy from
    @require decorators. Draws n_inputs examples deterministically with seed.
    Falls back to random valid-type inputs if strategy inference fails.
    """
    ...


def load_h_e1_programs(
    h_e1_output_dir: Path,
    models: list[str],
    task_ids: list[str],
) -> dict[str, dict[str, ProgramCorpus]]:
    """Load H-E1 test-passing programs. Returns {task_id: {model: ProgramCorpus}}."""
    # Reads from h-e1/code/ output; only test-passing programs included
    ...


def build_task_data(
    contracteval_dir: Path,
    h_e1_output_dir: Path,
    models: list[str],
    seed: int = 42,
) -> tuple[list[TaskData], dict[str, dict[str, ProgramCorpus]], dict]:
    """Full data loading pipeline. Returns (tasks, corpus, alignment_report).

    alignment_report contains: {overlap_pct, n_matched, n_fallback, unmatched_ids}
    Asserts overlap_pct >= 0.90 or raises RuntimeError to trigger fallback path.
    """
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | EvalPlus loading | `load_evalplus_inputs` using evalplus.data API |
| L-1-2 | Task ID alignment | `align_task_ids` with numeric fallback matching |
| L-1-3 | Fallback generation | `generate_fallback_inputs` via icontract_hypothesis |

---

## A-2: oracle_isolation — Core Oracle Harness [Complexity: 4, Budget: 5]

Applied: Standard subprocess sandbox + icontract decorator pattern

### API Signatures

```python
# oracle_isolation.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
import multiprocessing as mp


@dataclass
class InputResult:
    diff_fail: bool
    contract_fail: bool
    contract_unique: bool             # (not diff_fail) and contract_fail
    category: str                     # "redundant" | "contract_unique" | "differential_only" | "neither"
    diff_exception: Optional[str]     # exception class name if any
    contract_exception: Optional[str] # "ViolationError" | other class name | None
    precond_violated: bool            # True if @require raised before execution
    timeout_a: bool                   # Oracle A timed out
    timeout_b: bool                   # Oracle B timed out


@dataclass
class OracleIsolationResult:
    task_id: str
    model: str
    program_idx: int
    n_inputs: int                     # 764
    n_programs: int                   # number of programs evaluated for this task+model
    diff_failure_rate: float          # sum(diff_fail) / n_inputs
    contract_failure_rate: float      # sum(contract_fail) / n_inputs
    contract_unique_mass: float       # sum(contract_unique) / n_inputs
    oracle_isolation_gap: float       # contract_failure_rate - diff_failure_rate
    per_input_results: list[InputResult]
    n_precond_violated: int           # inputs skipped due to precondition violation
    n_timeout_a: int
    n_timeout_b: int


def exec_with_timeout(
    program_code: str,
    args: list,
    entry_point: str,
    timeout: float = 5.0,
) -> tuple[object, Optional[Exception]]:
    """Execute program_code(entry_point)(*args) in subprocess with timeout.

    Returns (result, None) on success, (None, exception) on failure.
    Uses multiprocessing.Process + Queue for isolation; kills on timeout.
    Output serialized via pickle; unpickling errors treated as execution failure.
    """
    ...


def compare_outputs(
    out_prog: object,
    out_gt: object,
) -> bool:
    """Return True if outputs differ (differential failure).

    Equality semantics:
    - Primitives: ==
    - Floats: math.isclose(rel_tol=1e-6, abs_tol=1e-9) if both are float
    - Lists/tuples: element-wise recursive compare_outputs
    - Sets: == after sorting not applicable; use == directly
    - None: out_prog is None and out_gt is not None -> fail; both None -> pass
    - Type mismatch: always fail (int vs float: cast float to check if int-valued)
    Returns False (no failure) if outputs are considered equal.
    """
    ...


def run_oracle_a(
    program_code: str,
    args: list,
    entry_point: str,
    ground_truth_fn: Callable,
    timeout: float = 5.0,
) -> tuple[bool, bool, Optional[str]]:
    """Run differential oracle. Returns (diff_fail, timed_out, exception_name)."""
    ...


def run_oracle_b(
    contract_fn: Callable,
    program_code: str,
    args: list,
    entry_point: str,
    timeout: float = 5.0,
) -> tuple[bool, bool, bool, Optional[str]]:
    """Run contract oracle. Returns (contract_fail, timed_out, precond_violated, exception_name).

    Contract oracle mechanism:
    1. Substitute program_code body into contract_fn wrapper dynamically
    2. Call patched_contract_fn(*args) — @require fires on entry, @ensure on return
    3. icontract.ViolationError -> contract_fail=True
    4. Other exception -> contract_fail=True (treat as failure)
    Precondition violation: if @require raises, precond_violated=True, contract_fail=True.
    """
    ...


def patch_contract_fn(
    contract_fn: Callable,
    program_code: str,
    entry_point: str,
) -> Callable:
    """Return new callable with program_code body but original icontract decorators.

    Implementation: compile program_code, extract entry_point function object,
    wrap with original contract_fn's __preconditions__ and __postconditions__
    using icontract._checkers.add_precondition / add_postcondition.
    Alternative: exec program_code in isolated namespace, then manually invoke
    contract_fn's pre/post checks around the execed function.
    """
    ...


def classify_input(diff_fail: bool, contract_fail: bool, precond_violated: bool) -> str:
    """Classify single input result into four categories.

    Categories:
    - "redundant":           diff_fail=True  AND contract_fail=True
    - "contract_unique":     diff_fail=False AND contract_fail=True (and not precond_violated)
    - "differential_only":   diff_fail=True  AND contract_fail=False
    - "neither":             diff_fail=False AND contract_fail=False
    - "precond_violated":    precond_violated=True (input outside domain; excluded from gap)

    Note: precond_violated inputs are NOT counted in n_inputs for rate computation
    to avoid inflating contract_failure_rate with domain-exclusion failures.
    """
    ...


def evaluate_oracle_isolation(
    program_code: str,
    task_id: str,
    model: str,
    program_idx: int,
    static_inputs: list[list],
    entry_point: str,
    ground_truth_fn: Callable,
    contract_fn: Callable,
    timeout: float = 5.0,
) -> OracleIsolationResult:
    """Evaluate one program under both oracles across all static inputs.

    For each input x in static_inputs:
    - Run Oracle A (differential): exec program, compare to ground_truth_fn(*x)
    - Run Oracle B (contract): patch contract_fn with program body, call with *x
    - Classify and record InputResult
    Precondition-violated inputs excluded from rate denominators.
    Returns OracleIsolationResult with per_input_results and aggregated rates.
    """
    ...


def evaluate_task(
    task_data: "TaskData",
    corpus: dict[str, "ProgramCorpus"],
    models: list[str],
    timeout: float = 5.0,
    n_workers: int = 4,
) -> dict[str, list[OracleIsolationResult]]:
    """Evaluate all programs for one task across all models. Returns {model: [results]}."""
    ...
```

### Oracle B Body Substitution Logic

```
patch_contract_fn(contract_fn, program_code, entry_point):
  1. exec(program_code, namespace)
  2. impl_fn = namespace[entry_point]  # extracted program function
  3. For each pre in contract_fn.__preconditions__:
       check pre(args) -> raise ViolationError if fails
  4. result = impl_fn(*args)
  5. For each post in contract_fn.__postconditions__:
       check post(result=result, **kwargs) -> raise ViolationError if fails
  6. return result
```

### Failure Classification Edge Cases

| Scenario | Oracle A | Oracle B | Category | Note |
|----------|----------|----------|----------|------|
| Timeout A, success B | True | False | differential_only | Timeout counts as fail for A |
| Timeout A, violation B | True | True | redundant | Both fail regardless of reason |
| Precond violated | N/A | True | precond_violated | Excluded from rate denominator |
| Both timeout | True | True | redundant | Both fail |
| Output equal, postfail | False | True | contract_unique | Key signal |
| Float near-equal | False | False | neither | If within tolerance |

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | exec_with_timeout | Subprocess isolation with Queue-based result return |
| L-2-2 | compare_outputs | Equality semantics including float tolerance |
| L-2-3 | patch_contract_fn | Dynamic body substitution preserving icontract decorators |
| L-2-4 | classify_input | Four-category classification with precond exclusion |
| L-2-5 | evaluate_oracle_isolation | Main per-program evaluation loop |

---

## A-3: soundness_check — Oracle Soundness Pre-check [Complexity: 2, Budget: 3]

Applied: icontract_hypothesis PBT pattern

### API Signatures

```python
# soundness_check.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class SoundnessResult:
    task_id: str
    n_examples: int                   # PBT examples tested
    n_violations: int                 # contract violations on reference impl
    soundness_ok: bool                # True if n_violations == 0
    error_message: Optional[str]      # First violation message if any


def check_reference_soundness(
    task_id: str,
    contract_fn: Callable,
    n_examples: int = 100_000,
    seed: int = 42,
    timeout_seconds: float = 7200.0,  # 2h wall-clock total budget
) -> SoundnessResult:
    """Run Hypothesis PBT on reference contract_fn. Quarantine if >= 1 violation.

    Uses icontract_hypothesis.make_strategy(contract_fn) to generate valid inputs
    consistent with @require preconditions. Runs Hypothesis with
    settings(max_examples=n_examples, database=None, derandomize=True).
    A SoundnessResult with soundness_ok=False means the reference implementation
    itself violates its own contracts -> task is quarantined.
    """
    ...


def run_soundness_precheck(
    tasks: list["TaskData"],
    n_examples: int = 100_000,
    seed: int = 42,
    n_workers: int = 4,
) -> tuple[list["TaskData"], list[SoundnessResult]]:
    """Run soundness check on all tasks. Returns (evaluable_tasks, all_results).

    Quarantine threshold: any task with soundness_ok=False is excluded.
    Fails fast with RuntimeError if quarantine_rate > 0.05 (>5% tasks).
    Reports quarantined task IDs to stdout.
    """
    ...
```

### Soundness Failure Semantics

A reference implementation fails soundness if:
- `@ensure` raises `ViolationError` when the reference fn runs on a valid input (bug in annotation or implementation)
- `@require` raises `ViolationError` when strategy-generated input violates precondition (strategy inference failure — treat as quarantine candidate, log separately)
- Any unhandled exception (type error, index error, etc.)

### Subtasks [2/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | check_reference_soundness | Single-task PBT run |
| L-3-2 | run_soundness_precheck | Parallel pre-check with quarantine logic |

---

## A-4: statistical_analysis — Statistics [Complexity: 2, Budget: 3]

Applied: Standard scipy/numpy statistical pattern

### API Signatures

```python
# statistical_analysis.py
from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class StatisticalReport:
    n_tasks: int
    mean_gap: float
    std_gap: float
    median_gap: float
    mean_cu_mass: float
    std_cu_mass: float
    wilcoxon_stat: float
    p_raw: float
    p_corrected: float                # Holm-corrected
    holm_rejected: bool               # True if p_corrected < 0.01
    ci_lower_gap: float               # bootstrap 95% CI lower bound
    ci_upper_gap: float
    ci_lower_cu: float                # bootstrap 95% CI lower bound for CU mass
    ci_upper_cu: float
    hypothesis_supported: bool        # gap >= 0.10 AND holm_rejected AND ci_lower_cu > 0.03


def compute_wilcoxon(
    gaps: list[float],
    alpha: float = 0.01,
) -> tuple[float, float, float, bool]:
    """Wilcoxon signed-rank on gaps vs 0 (alternative='greater').

    Returns (stat, p_raw, p_corrected, rejected).
    Holm correction: multipletests([p_raw], method='holm')[1][0].
    Note: single test -> Holm correction does not change p_raw, but applied for
    protocol compliance. If gaps contains all-zero entries, returns stat=0, p=1.0.
    """
    ...


def bootstrap_ci(
    values: list[float],
    n_resamples: int = 10_000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap CI on mean(values). Returns (ci_lower, ci_upper).

    np.random.seed(seed); draw n_resamples samples with replacement; percentile CI.
    """
    ...


def compute_statistical_report(
    per_task_gaps: dict[str, float],        # {task_id: gap}
    per_task_cu_mass: dict[str, float],     # {task_id: cu_mass}
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> StatisticalReport:
    """Full statistical analysis. Calls compute_wilcoxon and bootstrap_ci."""
    ...


def stratify_by_model(
    results: dict[str, dict[str, list["OracleIsolationResult"]]],
    model_families: dict[str, str],         # {model: family}
) -> dict[str, StatisticalReport]:
    """Run statistical_report per model family. Returns {family: report}."""
    ...


def stratify_by_task_type(
    results: dict[str, dict[str, list["OracleIsolationResult"]]],
    task_types: dict[str, str],             # {task_id: "humaneval"|"mbpp"}
) -> dict[str, StatisticalReport]:
    """Run statistical_report per task type. Returns {"humaneval": report, "mbpp": report}."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | compute_wilcoxon | Wilcoxon + Holm wrapper |
| L-4-2 | bootstrap_ci | Bootstrap resampling |
| L-4-3 | compute_statistical_report | Full aggregation + stratification |

---

## A-5: visualization — Figures [Complexity: 1, Budget: 2]

### API Signatures

```python
# visualization.py
from __future__ import annotations
from pathlib import Path
from statistical_analysis import StatisticalReport


def plot_gate_metrics(
    report: StatisticalReport,
    output_path: Path,
) -> None:
    """Bar chart: mean gap vs 0.10 threshold; CU mass vs 0.05; with CI error bars."""
    ...


def plot_oracle_breakdown_per_model(
    per_model_fractions: dict[str, dict[str, float]],  # {model: {category: fraction}}
    output_path: Path,
) -> None:
    """Stacked bar per model: redundant/contract_unique/differential_only/neither."""
    ...


def plot_gap_distribution(
    per_task_gaps: dict[str, float],
    output_path: Path,
) -> None:
    """Violin or CDF of per-task oracle-isolation gap across tasks."""
    ...


def plot_scatter_failure_rates(
    per_task_diff_rates: dict[str, float],
    per_task_contract_rates: dict[str, float],
    output_path: Path,
) -> None:
    """Scatter: per-task differential failure rate vs. contract failure rate."""
    ...


def generate_all_figures(
    report: StatisticalReport,
    all_results: dict,
    figures_dir: Path,
) -> None:
    """Generate and save all four figures to figures_dir."""
    ...
```

---

## A-6: run_experiment — Orchestration [Complexity: 2, Budget: 3]

### API Signatures

```python
# run_experiment.py
from __future__ import annotations
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    contracteval_dir: Path
    h_e1_output_dir: Path
    output_dir: Path
    models: list[str] = None          # defaults to all 5
    timeout: float = 5.0
    n_workers: int = 4
    seed: int = 42
    n_bootstrap: int = 10_000
    n_soundness_examples: int = 100_000
    pilot_n_tasks: int = 10           # tasks for pilot run


def run_pilot(config: ExperimentConfig) -> bool:
    """Run oracle isolation on pilot_n_tasks random tasks. Returns True if OK."""
    ...


def aggregate_results(
    all_results: dict[str, dict[str, list["OracleIsolationResult"]]],
) -> dict:
    """Aggregate per-task metrics across all models.

    Returns {
      per_task_gaps: {task_id: mean_gap_across_models},
      per_task_cu_mass: {task_id: mean_cu_mass_across_models},
      mean_diff_failure_rate: float,
      mean_contract_failure_rate: float,
      mean_contract_unique_mass: float,
      oracle_isolation_gap: float,      # overall mean gap
    }
    """
    ...


def verify_oracle_isolation_activated(results: dict) -> tuple[bool, dict]:
    """Verify both oracles ran and produced non-trivial measurements.

    Indicators checked in order (fail-fast: stop at first False):
    1. tasks_evaluated: len(per_task_gaps) >= 300
    2. oracle_a_ran: mean_diff_failure_rate > 0
    3. oracle_b_ran: mean_contract_failure_rate > 0
    4. contract_unique_nonzero: mean_contract_unique_mass > 0
    5. gap_computed: "oracle_isolation_gap" in results

    Returns (all_pass, {indicator_name: bool}).
    """
    ...


def save_results(
    all_results: dict,
    aggregate: dict,
    stat_report: "StatisticalReport",
    output_dir: Path,
) -> None:
    """Save oracle_isolation_results.json, per_task_results.csv, summary_report.md."""
    ...


def main(config: ExperimentConfig) -> int:
    """Full experiment pipeline. Returns 0 on success, 1 on failure.

    Execution order:
    1. load_contracteval_tasks + load_evalplus_inputs + align_task_ids
    2. Assert overlap >= 90%; run generate_fallback_inputs for unmatched
    3. load_h_e1_programs
    4. run_pilot (10 tasks) -> fail fast if misconfigured
    5. run_soundness_precheck -> quarantine unsound tasks
    6. For each (task, model, program): evaluate_oracle_isolation (parallel)
    7. aggregate_results
    8. verify_oracle_isolation_activated -> fail fast if oracle silent
    9. compute_statistical_report
    10. generate_all_figures
    11. save_results
    12. Print summary and gate pass/fail
    """
    ...


if __name__ == "__main__":
    import sys
    config = ExperimentConfig(
        contracteval_dir=Path("path/to/ContractEval"),
        h_e1_output_dir=Path("../h-e1/code/"),
        output_dir=Path("../results/"),
        models=["gpt-4o-mini", "claude-3-haiku", "deepseek-coder-v2-lite",
                "codellama-13b", "codellama-34b"],
    )
    sys.exit(main(config))
```

---

## Key Data Shapes

| Variable | Type/Shape | Note |
|----------|------------|------|
| static_inputs | List[List[Any]], len=764 | Each inner list = positional args |
| per_input_results | List[InputResult], len<=764 | Precond-violated excluded |
| per_task_gaps | Dict[task_id, float] | Up to 364 entries |
| per_task_cu_mass | Dict[task_id, float] | Up to 364 entries |
| gaps (Wilcoxon input) | List[float], len~327-364 | Post-quarantine tasks |
| boot_means | np.ndarray, shape=(10000,) | Bootstrap distribution |
| all_results | Dict[task_id, Dict[model, List[OracleIsolationResult]]] | Full result tree |

---

## Known Edge Cases

**1. Timeout in Oracle A, success in Oracle B**
- Oracle A: `diff_fail=True, timeout_a=True`
- Oracle B: runs on contract_fn which has no timeout coupling — runs independently
- Category: `differential_only` if contract passes, `redundant` if contract fails
- Rationale: timeout is a correctness failure for differential oracle

**2. Precondition violation (input outside domain)**
- `@require` raises `ViolationError` before program body executes
- `precond_violated=True`; input excluded from rate denominator entirely
- Avoids inflating `contract_failure_rate` with domain-exclusion non-events
- Logged separately as `n_precond_violated`

**3. Floating-point equality**
- `compare_outputs` uses `math.isclose(rel_tol=1e-6, abs_tol=1e-9)` for float/float pairs
- For list containing floats: element-wise with same tolerance
- Type mismatch (int vs float): cast float to nearest int if integer-valued, else fail

**4. Oracle B silent (no violations)**
- `verify_oracle_isolation_activated` catches `oracle_b_ran=False`
- Diagnostic: print top-5 tasks with highest expected violation probability (from H-E1 gap data)
- Check: verify icontract decorators present on contract_fn (`hasattr(contract_fn, '__preconditions__')`)

**5. Programs that fail both due to exception (not logical failure)**
- Exception in program exec -> `diff_fail=True` (conservative)
- Same exception propagates if patch_contract_fn re-raises -> `contract_fail=True`
- Category: `redundant`, but `diff_exception` and `contract_exception` recorded for analysis

**6. Program output is mutable (list, dict)**
- Ground truth computed fresh per input: `out_gt = ground_truth_fn(*args)` each time
- No shared state; inputs copied before exec to avoid mutation side effects
