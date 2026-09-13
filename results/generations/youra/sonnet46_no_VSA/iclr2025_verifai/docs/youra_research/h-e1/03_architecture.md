# Architecture: H-E1 — ContractEval Contract-Strength Gap Existence Verification

Applied: pipeline-orchestration pattern (from Archon KB search — HuggingFace diffusers philosophy, adapted for sequential eval pipeline)
Applied: sequential-experiment pattern (not applicable from KB — novel domain, reference only)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: `src/` (does not exist)
**Findings**: New implementation from scratch. No prior patterns to reuse.

---

## Overview

EXISTENCE PoC pipeline. No model training. Pure Python evaluation pipeline:

```
data loading → oracle soundness pre-check → code generation → test-pass filter
    → PBT contract checking → metric aggregation → visualization
```

**File layout** (`h-e1/code/`):
- `data_loader.py` — ContractEval loader
- `code_generator.py` — evalplus wrapper
- `oracle_checker.py` — soundness pre-check (100k budget PBT on reference impls)
- `contract_checker.py` — icontract-hypothesis PBT (5k budget, 60s timeout)
- `metrics.py` — gap computation + bootstrap 95% CI
- `figures.py` — matplotlib/seaborn plots
- `run_experiment.py` — orchestration entry point
- `config.py` — single fixed config dataclass

---

## Modules

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies**: stdlib (json, os, pathlib)

```python
def load_contracteval(data_dir: str = "./ContractEval/data") -> dict[str, dict]: ...
# returns {task_id: {task_id, entry_point, prompt, contracts, reference_impl}}

def get_z3_tractable_ids(contracteval_tasks: dict) -> set[str]: ...
# returns task_ids tagged as Z3-tractable (for sanity check FR-8)
```

---

### CodeGenerator (`h-e1/code/code_generator.py`)

**Dependencies**: subprocess, pathlib, evalplus (CLI invocation)

```python
MODELS: list[str]  # 5 model identifiers

def generate_samples(
    model: str,
    dataset: str,  # "humaneval" | "mbpp"
    output_dir: str,
    n: int = 10,
    temperature: float = 0.8,
) -> pathlib.Path: ...
# shells out to `evalplus.codegen`; returns path to .jsonl

def run_evalplus_filter(
    samples_path: pathlib.Path,
    dataset: str,
    base_only: bool = True,
) -> pathlib.Path: ...
# shells out to `evalplus.evaluate`; returns path to filtered results jsonl

def load_passing_samples(filtered_path: pathlib.Path) -> dict[str, list[str]]: ...
# returns {task_id: [passing_code_str, ...]}
```

---

### OracleChecker (`h-e1/code/oracle_checker.py`)

**Dependencies**: icontract, icontract_hypothesis, hypothesis, tqdm

```python
def check_reference_impl(
    task: dict,
    budget: int = 100_000,
    seed: int = 42,
    timeout_per_task: int = 30,  # seconds; total wall-clock bounded by caller
) -> dict: ...
# returns {task_id, quarantined: bool, violation_count: int, error: str|None}

def run_soundness_precheck(
    tasks: dict[str, dict],
    budget: int = 100_000,
    seed: int = 42,
    results_path: str = "results/oracle_precheck.jsonl",
) -> tuple[set[str], set[str]]: ...
# returns (valid_task_ids, quarantined_task_ids); logs to jsonl
```

---

### ContractChecker (`h-e1/code/contract_checker.py`)

**Dependencies**: icontract, icontract_hypothesis, hypothesis, tqdm

```python
def check_program_contract(
    reference_impl,       # callable with @icontract decorators
    generated_code: str,  # source string of LLM-generated program
    entry_point: str,
    budget: int = 5000,
    seed: int = 42,
    timeout: int = 60,
) -> dict: ...
# returns {violated: bool, n_failures: int, n_total: int, gap: float, error: str|None}

def run_contract_checking(
    tasks: dict[str, dict],
    passing_samples: dict[str, list[str]],  # {task_id: [code, ...]}
    model: str,
    valid_task_ids: set[str],
    budget: int = 5000,
    seed: int = 42,
    timeout: int = 60,
    results_path: str = "results/pbt_results_{model}_{dataset}.jsonl",
) -> list[dict]: ...
# streams results to jsonl; returns list of result dicts
```

---

### Metrics (`h-e1/code/metrics.py`)

**Dependencies**: numpy, scipy

```python
def compute_per_task_gap(pbt_results: list[dict]) -> dict[str, float]: ...
# {task_id: fraction of passing programs violating >= 1 contract}

def bootstrap_ci(
    gaps: list[float],
    n_bootstrap: int = 10_000,
    seed: int = 42,
) -> tuple[float, float]: ...
# returns (ci_lower, ci_upper) at 95%

def aggregate_metrics(
    pbt_results_all_models: list[dict],
    z3_tractable_ids: set[str],
) -> dict: ...
# returns {mean_gap, ci_lower, ci_upper, n_tasks, n_programs,
#          gate_passed, tractable_gap, n_quarantined}
```

---

### Figures (`h-e1/code/figures.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_gap_vs_baseline(
    mean_gap: float,
    ci_lower: float,
    ci_upper: float,
    out_path: str = "figures/gap_vs_baseline.png",
) -> None: ...

def plot_per_model_boxplot(
    pbt_results: list[dict],
    out_path: str = "figures/per_model_gap.png",
) -> None: ...

def plot_per_task_histogram(
    per_task_gap: dict[str, float],
    out_path: str = "figures/per_task_histogram.png",
) -> None: ...

def plot_cumulative_gap(
    per_task_gap: dict[str, float],
    out_path: str = "figures/cumulative_gap.png",
) -> None: ...

def plot_soundness_summary(
    valid_ids: set[str],
    quarantined_ids: set[str],
    out_path: str = "figures/soundness_summary.png",
) -> None: ...
```

---

### Config (`h-e1/code/config.py`)

**Dependencies**: dataclasses, pathlib

```python
@dataclass
class Config:
    # Data
    contracteval_dir: str = "./ContractEval/data"
    samples_dir: str = "data/samples"
    results_dir: str = "results"
    figures_dir: str = "figures"

    # Models
    models: list[str] = field(default_factory=lambda: [
        "gpt-4o-mini",
        "claude-3-haiku-20240307",
        "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct",
        "codellama/CodeLlama-13b-Instruct-hf",
        "codellama/CodeLlama-34b-Instruct-hf",
    ])

    # PBT
    oracle_budget: int = 100_000
    pbt_budget: int = 5_000
    pbt_seed: int = 42
    pbt_timeout: int = 60
    n_samples: int = 10
    temperature: float = 0.8
    n_bootstrap: int = 10_000
    gate_threshold: float = 0.01
```

---

### Orchestrator (`h-e1/code/run_experiment.py`)

**Dependencies**: all above modules, tqdm, json, pathlib

```python
def main(cfg: Config = Config()) -> None: ...
# Sequential pipeline:
#   1. load_contracteval()
#   2. run_soundness_precheck() → valid_ids, quarantined_ids
#   3. for model in cfg.models:
#       generate_samples(); run_evalplus_filter(); load_passing_samples()
#       run_contract_checking()
#   4. aggregate_metrics()
#   5. save results/summary.json + results/summary_report.md
#   6. all plot_*() calls
```

---

## Epic Tasks

| ID | Task | Description | Target Files | Complexity | Level |
|----|------|-------------|-------------|------------|-------|
| A-1 | Data + Config Setup | Clone ContractEval, implement loader, verify 364 tasks parse, write Config | `data_loader.py`, `config.py` | 6 (2+1+1+2) | Low |
| A-2 | Oracle Soundness Pre-check | Implement reference-impl PBT with icontract-hypothesis, 100k budget, quarantine logic | `oracle_checker.py` | 11 (2+2+4+3) | Medium |
| A-3 | Code Generation + Filter | Wrap evalplus CLI for 5 models, load passing samples | `code_generator.py` | 10 (2+3+2+3) | Medium |
| A-4 | Contract Checker | Core PBT loop per generated program, 5k budget, 60s timeout, stream to jsonl | `contract_checker.py` | 13 (3+3+4+3) | Medium |
| A-5 | Metrics + Gate Check | Per-task gap, bootstrap CI, gate evaluation, summary.json | `metrics.py` | 9 (2+2+3+2) | Medium |
| A-6 | Figures | 5 plots (bar, boxplot, histogram, cumulative, soundness summary) | `figures.py` | 7 (2+2+1+2) | Low |
| A-7 | Orchestration + E2E Run | Wire all modules in run_experiment.py, end-to-end smoke test | `run_experiment.py` | 10 (2+4+2+2) | Medium |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-4, A-5, A-7], Low(4-8): [A-1, A-6]

**Total complexity budget**: 66 points across 7 tasks (LIGHT tier, ≤15 tasks — satisfied at 7)
