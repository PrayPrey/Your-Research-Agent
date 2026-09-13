---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
generated: 2026-08-31
author: yoon303@ust.ac.kr
---

Applied: subprocess-isolated verifier pattern, checkpoint-resume pipeline

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior hypothesis code.

---

# Architecture: h-e1 — Multi-Verifier Activation Measurement

## File Organization

```
h-e1/code/
├── run_experiment.py        # entry point: orchestrates full pipeline
├── data_loader.py           # HumanEval + MBPP loading + unified schema
├── generate_completions.py  # GPT-4o-mini generation + JSONL checkpoint
├── verifiers/
│   ├── __init__.py
│   ├── execution_monitor.py # subprocess execution against unit tests
│   ├── static_analysis.py   # mypy --strict subprocess call
│   ├── type_checker.py      # pyright --outputjson subprocess call
│   └── smt_solver.py        # LLM constraint gen + Z3 check
├── measure_activation.py    # aggregation, gate check, stats output
├── visualize.py             # 5 figures
└── requirements.txt
```

Results layout:
- `results/completions.jsonl`
- `results/smt_pilot_results.json`
- `results/verifier_results.jsonl`
- `results/activation_stats.json`
- `figures/*.png`

---

## Module Structure

### DataLoader (`data_loader.py`)

**Dependencies**: human-eval, datasets

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Problem:
    problem_id: str      # "HE_0001" or "MB_0001"
    prompt: str
    test_code: str
    entry_point: str
    source: str          # "humaneval" | "mbpp"

def load_problems() -> List[Problem]: ...
```

---

### CompletionGenerator (`generate_completions.py`)

**Dependencies**: openai, DataLoader

```python
from typing import List
from data_loader import Problem

def generate_completions(
    problems: List[Problem],
    checkpoint_path: str = "results/completions.jsonl",
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 512,
) -> dict[str, str]:
    """Returns {problem_id: completion_code}. Skips already-cached."""
    ...
```

---

### VerifierResult (shared type, top of each verifier file)

```python
from dataclasses import dataclass

@dataclass
class VerifierResult:
    activated: bool
    signal: str
    latency_ms: float
```

---

### ExecutionMonitor (`verifiers/execution_monitor.py`)

**Dependencies**: human-eval (check_correctness), subprocess

```python
from verifiers import VerifierResult

def run(problem_id: str, completion: str, test_code: str, timeout: float = 3.0) -> VerifierResult: ...
```

---

### StaticAnalysis (`verifiers/static_analysis.py`)

**Dependencies**: subprocess (mypy CLI), tempfile

```python
from verifiers import VerifierResult

def run(completion: str, timeout: float = 10.0) -> VerifierResult: ...
```

---

### TypeChecker (`verifiers/type_checker.py`)

**Dependencies**: subprocess (pyright CLI), json, tempfile

```python
from verifiers import VerifierResult

def run(completion: str, timeout: float = 10.0) -> VerifierResult: ...
```

---

### SmtSolver (`verifiers/smt_solver.py`)

**Dependencies**: openai, z3-solver

```python
from verifiers import VerifierResult

def run_pilot(problems: list, n: int = 20, seed: int = 1) -> dict:
    """Returns pilot stats. Gate: sat_rate >= 0.30."""
    ...

def run(prompt: str, completion: str, timeout: float = 10.0) -> VerifierResult: ...
```

---

### ActivationMeasurer (`measure_activation.py`)

**Dependencies**: all verifiers, DataLoader

```python
def run_all_verifiers(
    problems: list,
    completions: dict[str, str],
    smt_enabled: bool = True,
    out_path: str = "results/verifier_results.jsonl",
) -> dict[str, dict]:
    """Returns {problem_id: {category: VerifierResult}}."""
    ...

def compute_stats(results: dict) -> dict:
    """Returns activation_rates, pairwise_overlap, per_source breakdown."""
    ...

def gate_check(stats: dict) -> bool:
    """Prints pass/fail per category. Returns True if all >= 0.10."""
    ...
```

---

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, pandas, numpy

```python
def plot_activation_rates(stats: dict, out: str = "figures/activation_rates.png") -> None: ...
def plot_overlap_matrix(stats: dict, out: str = "figures/overlap_matrix.png") -> None: ...
def plot_by_source(stats: dict, out: str = "figures/activation_by_source.png") -> None: ...
def plot_signal_length(results: dict, out: str = "figures/signal_length_dist.png") -> None: ...
def plot_smt_pilot(pilot: dict, out: str = "figures/smt_pilot.png") -> None: ...
```

---

## Proposed Epic Tasks

### Epic E1: Setup + Data Loading
- **Description:** Project scaffold, requirements.txt, DataLoader implementation loading HumanEval (164) + MBPP (374) into unified Problem schema
- **Files:** `requirements.txt`, `data_loader.py`
- **Complexity:** 6/20 (Module_Size=1 + Dependencies=2 + Algorithm=1 + Integration=2)
- **Type:** data-pipeline

### Epic E2: Completion Generation with Checkpoint
- **Description:** GPT-4o-mini single-shot generation for 538 problems; JSONL checkpoint so re-runs skip already-generated completions; exponential backoff on API errors
- **Files:** `generate_completions.py`
- **Complexity:** 8/20 (Module_Size=2 + Dependencies=2 + Algorithm=1 + Integration=3)
- **Type:** data-pipeline

### Epic E3: SMT Pilot + Four Verifiers
- **Description:** Implement all 4 verifiers (execution_monitor, static_analysis, type_checker, smt_solver). Run 20-problem SMT pilot (seed=1) first; gate check ≥30% SAT; if failed, disable SMT for full run. Each verifier returns VerifierResult with activated/signal/latency_ms.
- **Files:** `verifiers/__init__.py`, `verifiers/execution_monitor.py`, `verifiers/static_analysis.py`, `verifiers/type_checker.py`, `verifiers/smt_solver.py`
- **Complexity:** 16/20 (Module_Size=4 + Dependencies=4 + Algorithm=4 + Integration=4)
- **Type:** evaluation

### Epic E4: Activation Measurement + Gate Check
- **Description:** Run all verifiers over 538 problems; write per-problem JSONL; compute activation_rates, pairwise overlap, per-source breakdown; gate check all ≥0.10; exit 0/1
- **Files:** `measure_activation.py`
- **Complexity:** 9/20 (Module_Size=2 + Dependencies=3 + Algorithm=2 + Integration=2)
- **Type:** evaluation

### Epic E5: Visualization + Run Orchestration
- **Description:** 5 matplotlib figures (activation bar, overlap heatmap, by-source grouped bar, signal length boxplot, SMT pilot bar); top-level run_experiment.py wiring all stages in order
- **Files:** `visualize.py`, `run_experiment.py`
- **Complexity:** 8/20 (Module_Size=2 + Dependencies=2 + Algorithm=1 + Integration=3)
- **Type:** evaluation

---

**Distribution**: High(14-17): [E3], Medium(9-13): [E4], Low(4-8): [E1, E2, E5]

**Total complexity budget**: 47 (well within LIGHT tier)
