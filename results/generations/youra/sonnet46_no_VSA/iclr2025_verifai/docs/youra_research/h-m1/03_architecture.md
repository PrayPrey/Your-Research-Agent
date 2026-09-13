# Architecture: H-M1 Oracle Isolation Experiment

**Hypothesis ID:** H-M1 — MECHANISM (PoC)
**Date:** 2026-08-03
**Applied:** exec_with_timeout/SIGALRM pattern from H-E1; bootstrap_ci extended for dual-oracle; load_contracteval reused directly

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns verified from H-E1 actual code
**Analyzed Path:** `docs/youra_research/h-e1/code/`
**Findings:** H-E1 uses SIGALRM-based `exec_with_timeout` (oracle_checker.py:17, contract_checker.py:26), JSONL streaming results, `bootstrap_ci` with `numpy.default_rng`, `load_contracteval` returning `{task_id: dict}` with fields `canonical_solution_with_contract`, `contract_violating_test`, `base_input`, `plus_input`. H-M1 extends these patterns: replaces CVT inputs with EvalPlus 764 static inputs; adds Oracle A (differential) alongside Oracle B (contract).

---

## System Overview

Pipeline (bullet form, no ASCII diagrams per output constraints):

- **data_loader.py** — loads ContractEval JSONL + EvalPlus static inputs + H-E1 program corpus; verifies task ID overlap; generates fallback inputs for unmatched tasks
- **soundness_check.py** — Hypothesis PBT (100k examples) on reference impls; emits `(valid_task_ids, quarantined_task_ids)`
- **oracle_isolation.py** — dual-oracle harness: per-(model, task, program) triple evaluates all 764 inputs under Oracle A and Oracle B simultaneously; classifies each pair; streams JSONL results
- **statistical_analysis.py** — Wilcoxon signed-rank + Holm correction + bootstrap 95% CI; per-task and aggregate; stratification by model and task type
- **visualization.py** — 4 figure outputs to `h-m1/figures/`
- **run_experiment.py** — linear orchestrator: phases 1–7 in sequence; writes `experiment_results.json`

Data flow:

```
ContractEval JSONL  →  load_contracteval()       →  tasks {task_id: dict}
EvalPlus API        →  load_evalplus_inputs()    →  static_inputs {task_id: list[list]}
H-E1 data/samples/ →  load_h1_corpus()          →  corpus {model: {task_id: list[str]}}
                                                            ↓
                                           soundness_check.py
                                                            ↓  valid_task_ids
                                           oracle_isolation.py  ← multiprocessing.Pool
                                                            ↓  list[TaskProgramResult]
                                           statistical_analysis.py
                                                            ↓  AggregatedStats
                                           visualization.py → figures/
                                           run_experiment.py → results/
```

---

## Component Architecture

### DataLoader (`code/data_loader.py`)

**Dependencies:** evalplus (pip), pathlib, json, signal (stdlib)
**Reuses:** `load_contracteval` — copied from H-E1 `data_loader.py` with identical signature; JSONL format unchanged

```python
# Copied from h-e1/code/data_loader.py — identical
def load_contracteval(jsonl_path: str) -> dict[str, dict]:
    # Returns {task_id: {entry_point, canonical_solution,
    #   canonical_solution_with_contract, contract,
    #   contract_violating_test, base_input, plus_input}}
    ...

def load_evalplus_inputs(
    task_ids: set[str],
) -> dict[str, list[list]]:
    # evalplus.data.get_human_eval_plus() + get_mbpp_plus()
    # Concatenates base_input + plus_input per task (up to 764 entries)
    # Returns {task_id: [[arg1, arg2, ...], ...]}
    ...

def load_h1_corpus(
    h1_samples_dir: str,
    valid_task_ids: set[str],
) -> dict[str, dict[str, list[str]]]:
    # Reads h-e1/code/data/samples/{model}.jsonl
    # Returns {model: {task_id: [code_str, ...]}} — test-passing programs only
    ...

def verify_task_overlap(
    contracteval_ids: set[str],
    evalplus_ids: set[str],
    threshold: float = 0.90,
) -> tuple[set[str], set[str]]:
    # Returns (matched_ids, unmatched_ids)
    # Raises ValueError if overlap fraction < threshold
    ...

def generate_fallback_inputs(
    task: dict,
    n: int = 764,
    seed: int = 42,
) -> list[list]:
    # Hypothesis-based input generation for unmatched tasks
    # Uses icontract_hypothesis.infer_strategy() on canonical_solution_with_contract
    # ponytail: FilteredStrategy fallback; upgrade to full CVT gen if coverage < 50%
    ...
```

---

### SoundnessCheck (`code/soundness_check.py`)

**Dependencies:** data_loader, icontract_hypothesis, hypothesis, signal, json, multiprocessing
**Reuses:** `exec_with_timeout` and `_timeout_handler` — copied from H-E1 `oracle_checker.py` (identical SIGALRM pattern)

H-M1 soundness differs from H-E1: uses Hypothesis PBT (100k examples) rather than CVT inputs, because EvalPlus static inputs are not CVTs. Fallback to CVT-based check if strategy inference fails.

```python
def _timeout_handler(signum, frame) -> None: ...  # SIGALRM; copied from H-E1

def exec_with_timeout(
    code_str: str,
    entry_point: str,
    timeout: int = 30,
) -> tuple[object | None, str | None]:
    # Identical to H-E1 oracle_checker.exec_with_timeout
    ...

def check_reference_soundness(
    task: dict,
    n_examples: int = 100_000,
    seed: int = 42,
    timeout: int = 120,
) -> dict:
    # exec canonical_solution_with_contract; run icontract_hypothesis.test_with_inferred_strategy()
    # quarantine=True if ViolationError raised (reference unsound) or timeout
    # Returns {task_id, quarantined, n_violations, error}
    ...

def run_soundness_precheck(
    tasks: dict[str, dict],
    results_path: str = "results/soundness_precheck.jsonl",
    n_examples: int = 100_000,
    seed: int = 42,
    timeout_per_task: int = 120,
    n_workers: int = 4,
) -> tuple[set[str], set[str]]:
    # multiprocessing.Pool(n_workers).imap_unordered over tasks
    # Streams JSONL; warns if quarantine_rate > 0.05
    # Returns (valid_task_ids, quarantined_task_ids)
    ...
```

---

### OracleIsolation (`code/oracle_isolation.py`)

**Dependencies:** data_loader, icontract, signal, json, multiprocessing, dataclasses
**Core module** — implements two-oracle parallel evaluation harness.

```python
from dataclasses import dataclass

@dataclass
class InputResult:
    diff_fail: bool        # Oracle A: f(x) != gt(x) or exception
    contract_fail: bool    # Oracle B: ViolationError or exception
    contract_unique: bool  # diff_fail=False AND contract_fail=True
    timeout: bool
    error: str | None

@dataclass
class TaskProgramResult:
    task_id: str
    model: str
    program_idx: int
    diff_failure_rate: float
    contract_failure_rate: float
    contract_unique_mass: float
    oracle_isolation_gap: float      # contract_failure_rate - diff_failure_rate
    n_inputs: int
    n_redundant: int
    n_contract_unique: int
    n_differential_only: int
    n_neither: int
    n_errors: int

def _exec_program(
    code_str: str,
    entry_point: str,
    timeout: int = 5,
) -> tuple[object | None, str | None]:
    # SIGALRM exec; same pattern as H-E1 contract_checker.exec_with_timeout
    ...

def _build_contract_fn(
    program_code: str,
    entry_point: str,
    contract_source: str,
) -> object | None:
    # Injects LLM program body into canonical_solution_with_contract source via AST
    # Preserves icontract @require/@ensure decorator stack
    # Returns callable or None on failure
    # ponytail: AST body swap; upgrade to icontract programmatic API if edge cases arise
    ...

def _evaluate_single_input(
    prog_fn: object,
    gt_fn: object,
    contract_fn: object,
    inputs: list,
    timeout: int = 5,
) -> InputResult:
    # Oracle A: prog_fn(*inputs) == gt_fn(*inputs)
    # Oracle B: contract_fn(*inputs) raises ViolationError?
    # Both under SIGALRM timeout
    ...

def evaluate_program_isolation(
    program_code: str,
    task: dict,
    static_inputs: list[list],
    timeout_per_input: int = 5,
) -> TaskProgramResult:
    # Builds prog_fn, gt_fn, contract_fn
    # Runs _evaluate_single_input for each input in static_inputs
    # Aggregates counts; computes rates
    ...

def _worker_fn(args: tuple) -> TaskProgramResult:
    # Unpacks (program_code, task, static_inputs, timeout_per_input, model, idx)
    # Calls evaluate_program_isolation; safe for multiprocessing (no shared state)
    ...

def run_oracle_isolation(
    corpus: dict[str, dict[str, list[str]]],
    tasks: dict[str, dict],
    static_inputs: dict[str, list[list]],
    valid_task_ids: set[str],
    results_path: str = "results/isolation_results.jsonl",
    timeout_per_input: int = 5,
    n_workers: int = 8,
) -> list[TaskProgramResult]:
    # Builds work items: (model, task_id, program_code, idx) for all valid tasks
    # multiprocessing.Pool(n_workers).imap_unordered(_worker_fn)
    # Streams JSONL as results arrive; returns all results
    # ponytail: global pool over (model, task, program) triples; per-model sub-pools if memory pressure
    ...

def verify_activation(
    results: list[TaskProgramResult],
) -> tuple[bool, dict]:
    # FR-6: both oracles fired (mean_diff_rate > 0, mean_contract_rate > 0)
    # ≥300 tasks evaluated; contract_unique_count > 0 for ≥50% tasks
    # Returns (activated: bool, indicators: dict)
    ...
```

**Contract function injection — key design:**

Oracle B requires running the LLM program body under the reference's icontract decorators. Approach:

```python
# 1. Parse canonical_solution_with_contract source with ast.parse()
# 2. Replace function body AST nodes with LLM program body nodes
# 3. ast.unparse() + exec() → decorated function with LLM implementation
# This preserves @icontract.require/@icontract.ensure decorator stack
# gt_fn: exec canonical_solution (no decorators) for Oracle A comparison
```

---

### StatisticalAnalysis (`code/statistical_analysis.py`)

**Dependencies:** numpy, scipy, statsmodels, dataclasses
**Reuses:** `bootstrap_ci` — copied from H-E1 `metrics.py` (identical numpy default_rng pattern); extended for dual-oracle

```python
from dataclasses import dataclass

@dataclass
class AggregatedStats:
    # Primary gate metrics
    mean_isolation_gap: float
    wilcoxon_stat: float
    wilcoxon_p_raw: float
    wilcoxon_p_corrected: float    # Holm correction
    gap_ci_lower: float            # bootstrap 95%
    gap_ci_upper: float
    # Secondary gate metrics
    mean_contract_unique_mass: float
    cu_ci_lower: float
    cu_ci_upper: float
    # Coverage
    n_tasks_evaluated: int
    n_programs_total: int
    task_coverage_rate: float
    # Gate decision
    gate_passed: bool              # gap>=0.10 AND p_corrected<0.01 AND cu_ci_lower>0.03
    # Stratification
    by_model: dict[str, dict]
    by_task_type: dict[str, dict]  # "humaneval+" vs "mbpp+"

def compute_per_task_stats(
    results: list[TaskProgramResult],
) -> dict[str, dict]:
    # Aggregates across programs per task
    # Returns {task_id: {mean_gap, mean_cu_mass, n_programs, task_type}}
    ...

def wilcoxon_holm(
    per_task_gaps: list[float],
) -> tuple[float, float, float]:
    # scipy.stats.wilcoxon(gaps, alternative='greater')
    # statsmodels.stats.multitest.multipletests([p_raw], method='holm')
    # Returns (stat, p_raw, p_corrected)
    ...

def bootstrap_ci(
    values: list[float],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> tuple[float, float]:
    # numpy default_rng(seed).choice — identical to H-E1 metrics.bootstrap_ci
    ...

def aggregate_stats(
    results: list[TaskProgramResult],
    task_metadata: dict[str, dict],
    n_bootstrap: int = 10_000,
    seed: int = 42,
    gap_threshold: float = 0.10,
    cu_threshold: float = 0.05,
    cu_ci_threshold: float = 0.03,
    p_threshold: float = 0.01,
) -> AggregatedStats: ...

def save_results(
    stats: AggregatedStats,
    per_task: dict[str, dict],
    results_dir: str,
) -> None:
    # Writes oracle_isolation_results.json and per_task_results.csv
    ...
```

---

### Visualization (`code/visualization.py`)

**Dependencies:** matplotlib, numpy

```python
def plot_gate_metrics(
    stats: AggregatedStats,
    out_path: str = "figures/gate_metrics_comparison.png",
) -> None:
    # Required (FR-7): bar chart — mean gap vs 0.10; CU mass vs 0.05; with 95% CI error bars
    ...

def plot_oracle_breakdown_by_model(
    results: list[TaskProgramResult],
    out_path: str = "figures/oracle_failure_breakdown.png",
) -> None:
    # Stacked bar: redundant / contract_unique / differential_only / neither per model
    ...

def plot_gap_distribution(
    per_task_gaps: dict[str, float],
    out_path: str = "figures/gap_distribution.png",
) -> None:
    # Violin or CDF of per-task oracle-isolation gap across tasks
    ...

def plot_scatter_failure_rates(
    per_task: dict[str, dict],
    out_path: str = "figures/scatter_failure_rates.png",
) -> None:
    # Scatter: per-task diff_failure_rate (x) vs contract_failure_rate (y)
    ...
```

---

### RunExperiment (`code/run_experiment.py`)

**Dependencies:** all above modules, dataclasses, pathlib, json, sys

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    contracteval_jsonl: str         # path to ContractEval JSONL
    h1_samples_dir: str             # path to h-e1/code/data/samples/
    results_dir: str = "results"
    figures_dir: str = "figures"
    timeout_per_input: int = 5
    n_workers: int = 8
    seed: int = 42
    soundness_n_examples: int = 100_000
    soundness_timeout: int = 120
    n_bootstrap: int = 10_000
    gap_threshold: float = 0.10
    cu_threshold: float = 0.05
    cu_ci_threshold: float = 0.03
    p_threshold: float = 0.01
    overlap_threshold: float = 0.90

def default_config() -> Config: ...

def main() -> dict:
    # Phases:
    # 1. Load ContractEval + EvalPlus + H-E1 corpus
    # 2. Verify task ID overlap; generate fallback inputs for unmatched
    # 3. Oracle soundness pre-check (parallel, JSONL streaming)
    # 4. Oracle isolation evaluation (parallel, JSONL streaming)
    # 5. verify_activation() — fail fast if oracles silent
    # 6. aggregate_stats() + save_results()
    # 7. plot_*() — 4 figures
    # 8. Write experiment_results.json
    # Returns experiment_results dict
    # sys.exit(0 if gate_passed else 1)
    ...
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path / Usage | File Location |
|--------|---------------------|---------------|
| `load_contracteval` | Copied to `h-m1/code/data_loader.py` (identical) | `h-e1/code/data_loader.py:6` |
| `exec_with_timeout` pattern | Copied to `soundness_check.py` and `oracle_isolation.py` | `h-e1/code/oracle_checker.py:17`, `contract_checker.py:26` |
| `bootstrap_ci` | Copied to `statistical_analysis.py` (identical numpy logic) | `h-e1/code/metrics.py:27` |
| H-E1 program corpus | Read from path; no import | `h-e1/code/data/samples/{model}.jsonl` |

**Verified from:** `docs/youra_research/h-e1/code/` actual implementation (not spec).

Note: H-M1 copies rather than imports H-E1 functions to keep code self-contained. Functions are short enough that duplication is the lazy choice.

---

## Parallelism Strategy

Work unit: `(model, task_id, program_code, program_idx)` triple.

- Scale: 5 models × ~330 valid tasks × ~10 programs = ~16,500 triples, each evaluating 764 inputs
- `multiprocessing.Pool(n_workers=8).imap_unordered(_worker_fn)` over triples
- SIGALRM timeout (5s) per individual input evaluation inside each worker
- Results streamed to JSONL as they complete — experiment is resumable from partial results
- `ponytail: global pool; per-model sub-pools only if memory pressure observed at runtime`

---

## Pre-check & Fallback

**Soundness pre-check:**
1. For each ContractEval task: exec `canonical_solution_with_contract`, run Hypothesis PBT (100k examples, seed=42)
2. If `icontract.ViolationError` raised → quarantine (reference unsound)
3. If strategy inference fails → fallback to H-E1 CVT-based check (`check_reference_impl` pattern)
4. Timeout > 120s per task → quarantine
5. Quarantine rate > 5% → WARN; proceed if ≥300 tasks valid

**Task ID overlap fallback:**
1. `verify_task_overlap()` asserts ≥90% overlap
2. For unmatched tasks: `generate_fallback_inputs()` via Hypothesis with icontract preconditions
3. Seed=42 for all fallback generation; fallback inputs count noted in results

---

## Statistical Analysis Architecture

```
results: list[TaskProgramResult]
    ↓ compute_per_task_stats()
per_task: {task_id: {mean_gap, mean_cu_mass, n_programs, task_type}}
    ↓
per_task_gaps: list[float]  (one per task, averaged across programs)
    ├──→ wilcoxon_holm(gaps)
    │      scipy.stats.wilcoxon(gaps, alternative='greater')
    │      multipletests([p_raw], method='holm')
    │
    └──→ bootstrap_ci(gaps, n_bootstrap=10_000, seed=42)
           numpy.default_rng(42).choice(gaps, (10_000, n_tasks), replace=True).mean(axis=1)
           np.percentile(boot_means, [2.5, 97.5])

Same bootstrap_ci applied to per_task_cu_mass list for CU metric CI.
Stratification: filter results by model or task_type before aggregation.
```

---

## Output Architecture

### `results/oracle_isolation_results.json`

```json
{
  "hypothesis_id": "h-m1",
  "gate_passed": true,
  "mean_isolation_gap": 0.153,
  "gap_ci_lower": 0.121,
  "gap_ci_upper": 0.187,
  "wilcoxon_stat": 12400.0,
  "wilcoxon_p_raw": 0.0003,
  "wilcoxon_p_corrected": 0.0003,
  "mean_contract_unique_mass": 0.071,
  "cu_ci_lower": 0.052,
  "cu_ci_upper": 0.093,
  "n_tasks_evaluated": 331,
  "n_quarantined": 33,
  "task_coverage_rate": 0.910,
  "n_programs_total": 3310,
  "by_model": {
    "gpt-4o-mini": {"mean_gap": 0.16, "mean_cu_mass": 0.08, "n_tasks": 331}
  },
  "by_task_type": {
    "humaneval+": {"mean_gap": 0.14, "n_tasks": 200},
    "mbpp+": {"mean_gap": 0.17, "n_tasks": 131}
  }
}
```

### `results/per_task_results.csv`

Columns: `task_id, task_type, model, program_idx, diff_failure_rate, contract_failure_rate, oracle_isolation_gap, contract_unique_mass, n_inputs, n_redundant, n_contract_unique, n_differential_only, n_neither, n_errors`

### `figures/`

| File | FR | Content |
|------|----|---------|
| `gate_metrics_comparison.png` | FR-7 required | Gap vs 0.10 threshold + CU mass vs 0.05 with CI bars |
| `oracle_failure_breakdown.png` | FR-7 optional | Stacked bar per model (4 categories) |
| `gap_distribution.png` | FR-7 optional | Violin of per-task isolation gap distribution |
| `scatter_failure_rates.png` | FR-7 optional | Diff rate vs contract rate scatter per task |

---

## Execution Phases

| Phase | Module | Description | Est. Wall-clock |
|-------|--------|-------------|-----------------|
| 1. Load data | data_loader | ContractEval JSONL + EvalPlus API + H-E1 corpus | 2–5 min |
| 2. Verify overlap | data_loader | Task ID alignment; fallback input gen | 1–2 min |
| 3. Soundness pre-check | soundness_check | 100k PBT × ~364 tasks (parallel, 4 workers) | 30–60 min |
| 4. Oracle isolation eval | oracle_isolation | Dual-oracle × 764 inputs × all programs (8 workers) | 2–3 h |
| 5. Activation verify | oracle_isolation | FR-6 fail-fast checks | < 1 min |
| 6. Statistical analysis | statistical_analysis | Wilcoxon + Holm + bootstrap (10k resamples) | 1–2 min |
| 7. Figures | visualization | 4 matplotlib figures | < 1 min |
| 8. Write results | run_experiment | JSON + CSV + experiment_results.json | < 1 min |
| **Total** | | 8-core machine, seed=42 | **~3–4 h** |

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading & alignment | `load_evalplus_inputs`, `load_h1_corpus`, `verify_task_overlap`, `generate_fallback_inputs`; copy `load_contracteval` from H-E1 | 10 | 2+2+3+3 |
| A-2 | Soundness pre-check | `check_reference_soundness` with Hypothesis PBT; parallel `run_soundness_precheck`; quarantine + warn logic | 11 | 3+3+3+2 |
| A-3 | Contract function injection | AST body-swap: inject LLM code into `canonical_solution_with_contract` preserving icontract decorator stack; validate on known-bad programs | 16 | 4+4+4+4 |
| A-4 | Dual-oracle evaluation | `_evaluate_single_input`, `evaluate_program_isolation`, dataclasses; Oracle A + Oracle B + classification logic | 14 | 4+3+4+3 |
| A-5 | Multiprocessing pipeline | `_worker_fn`, `run_oracle_isolation` with Pool + JSONL streaming; `verify_activation` FR-6 | 12 | 3+3+3+3 |
| A-6 | Statistical analysis | `wilcoxon_holm`, `bootstrap_ci`, `aggregate_stats`, stratification, `save_results` | 11 | 3+3+3+2 |
| A-7 | Visualization | 4 figure functions; gate metrics bar (required); 3 optional | 7 | 2+2+2+1 |
| A-8 | Orchestration & config | `Config`, `default_config`, `main` pipeline; `experiment_results.json`; gate exit code | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-4], Medium(9-13): [A-1, A-2, A-5, A-6], Low(4-8): [A-7, A-8]

---

*H-M1 Phase 3 architecture — generated 2026-08-03*
*Base hypothesis code verified from: `docs/youra_research/h-e1/code/`*
