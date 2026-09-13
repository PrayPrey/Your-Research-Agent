# Architecture: H-M1 — Granularity Effect on Repair Success

**Applied**: subprocess-execution-pattern, scipy-anova-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from actual H-E1 code (files read directly; Serena project activation unavailable)
**Analyzed Path**: `docs/youra_research/20260330_verifai/h-e1/code/`
**Findings**: Flat module layout; local imports (`from config import ExperimentConfig`). `execute_code()` and `ErrorCategory` in `executor.py` are directly reusable. `CodeGenerator` in `model.py` provides `generate(prompt) -> str`. H-E1 results JSON keys: `task_id`, `category`, `stderr`, `generated_code`.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ErrorCategory | `from executor import ErrorCategory` | `h-e1/code/executor.py` |
| execute_code | `from executor import execute_code` | `h-e1/code/executor.py` |
| CodeGenerator | `from model import CodeGenerator` | `h-e1/code/model.py` |
| ExperimentConfig (H-E1) | `from config import ExperimentConfig` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/20260330_verifai/h-e1/code/` (actual implementation)

**Note**: H-M1 code lives in its own directory. Reuse is achieved by copying executor.py or importing via sys.path manipulation; the architecture below defines self-contained h-m1 modules that replicate the execute_code interface rather than cross-import.

---

## File Organization

- `h-m1/code/config.py` — experiment configuration dataclass
- `h-m1/code/data.py` — load H-E1 results + MBPP dataset
- `h-m1/code/feedback.py` — granularity formatter (G0-G4) + repair prompt constructor
- `h-m1/code/executor.py` — code execution and verification (adapted from H-E1)
- `h-m1/code/repair.py` — repair generation pipeline using CodeGenerator
- `h-m1/code/analyze.py` — ANOVA + Tukey HSD statistical analysis
- `h-m1/code/evaluate.py` — results persistence + visualization
- `h-m1/code/train.py` — main experiment runner (entry point)
- `h-m1/results/` — repair_results.json, metrics.yaml, posthoc.yaml
- `h-m1/figures/` — all visualization outputs

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field

GRANULARITY_LEVELS = ["G0", "G1", "G2", "G3", "G4"]

@dataclass
class RepairConfig:
    # Model (same as H-E1)
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False
    seed: int = 1

    # Data
    h_e1_results_path: str = "../h-e1/results/execution_results.json"
    mbpp_dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510

    # Execution
    execution_timeout: int = 10

    # Paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_json: str = "results/repair_results.json"
    output_metrics: str = "results/metrics.yaml"
    output_posthoc: str = "results/posthoc.yaml"

    # Gate
    anova_alpha: float = 0.05
    eta_squared_threshold: float = 0.02
```

---

### Data (`code/data.py`)

**Dependencies**: Config

```python
from config import RepairConfig

def load_runtime_error_cases(config: RepairConfig) -> list[dict]:
    """Load 304 runtime error cases from H-E1 execution_results.json.

    Returns list of dicts: {task_id, generated_code, category, stderr}
    Filters to category == 'runtime_error' only.
    """
    ...

def load_mbpp_index(config: RepairConfig) -> dict[int, dict]:
    """Load MBPP test split and return dict keyed by task_id.

    Returns {task_id: {text, test_list}} for tasks in [task_id_min, task_id_max].
    """
    ...

def parse_error_info(stderr: str) -> dict:
    """Parse stderr string into structured error_info dict.

    Returns: {type: str, message: str, line: int|None, traceback: str}
    Extracts error type from last line, message body, line number from traceback.
    """
    ...
```

---

### Feedback (`code/feedback.py`)

**Dependencies**: none

```python
GRANULARITY_LEVELS = ["G0", "G1", "G2", "G3", "G4"]

def format_feedback(error_info: dict, level: str) -> str:
    """Format error feedback at specified granularity level.

    Args:
        error_info: {type, message, line, traceback}
        level: one of G0..G4
    Returns:
        Formatted feedback string per granularity spec.
    """
    ...

def construct_repair_prompt(
    code: str,
    task_text: str,
    error_info: dict,
    granularity: str,
) -> str:
    """Build Self-Debug style repair prompt with controlled granularity.

    Args:
        code: Buggy generated code from H-E1
        task_text: MBPP problem description
        error_info: Parsed error dict
        granularity: G0..G4
    Returns:
        Formatted prompt string ready for model.generate()
    """
    ...
```

---

### Executor (`code/executor.py`)

**Dependencies**: none (adapted from H-E1 executor.py)

```python
from enum import Enum
from typing import Optional

class ErrorCategory(Enum):
    PASS = "pass"
    RUNTIME_ERROR = "runtime_error"
    WRONG_OUTPUT = "wrong_output"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"

def execute_and_verify(
    code: str,
    test_list: list[str],
    timeout: int = 10,
) -> bool:
    """Execute repaired code against MBPP test assertions.

    Returns True if all tests pass (returncode == 0), False otherwise.
    Handles TimeoutExpired gracefully.
    """
    ...

def execute_code(
    code: str,
    tests: list[str],
    timeout: int = 10,
) -> tuple[ErrorCategory, Optional[str]]:
    """Full execution returning category + stderr (H-E1 interface preserved)."""
    ...
```

---

### Repair (`code/repair.py`)

**Dependencies**: Config, Feedback, Executor

```python
import sys
sys.path.insert(0, "../h-e1/code")
from model import CodeGenerator  # reuse H-E1 CodeGenerator directly

from config import RepairConfig
from feedback import construct_repair_prompt
from executor import execute_and_verify

def run_repair_experiment(
    runtime_cases: list[dict],
    mbpp_index: dict[int, dict],
    generator: CodeGenerator,
    config: RepairConfig,
) -> list[dict]:
    """Run 304 cases × 5 granularity levels = 1,520 repair attempts.

    For each (case, granularity):
      - Build repair prompt
      - Generate repaired code via generator.generate()
      - Execute and record binary success

    Returns:
        List of result dicts:
        {task_id, granularity, repaired_code, success, execution_time}
    Saves checkpoint after each case for resume capability.
    """
    ...

def load_checkpoint(checkpoint_path: str) -> list[dict]:
    """Load partial results for resume from checkpoint JSON."""
    ...

def save_checkpoint(results: list[dict], checkpoint_path: str) -> None:
    """Persist current results to checkpoint file."""
    ...
```

---

### Analyze (`code/analyze.py`)

**Dependencies**: Config

```python
import numpy as np
from scipy.stats import f_oneway
from scipy.stats import tukey_hsd
from config import RepairConfig, GRANULARITY_LEVELS

def aggregate_by_granularity(results: list[dict]) -> dict[str, list[int]]:
    """Aggregate binary success values per granularity level.

    Returns: {G0: [0,1,...], G1: [...], ..., G4: [...]}
    """
    ...

def run_anova(groups: dict[str, list[int]]) -> dict:
    """Run one-way ANOVA across 5 granularity groups.

    Returns:
        {f_statistic, p_value, eta_squared, gate_passed,
         success_rates: {G0..G4}, n_per_group}
    """
    ...

def run_posthoc(groups: dict[str, list[int]]) -> dict:
    """Run Tukey HSD post-hoc if ANOVA significant (p < 0.05).

    Returns:
        {G0_vs_G1: {statistic, p_value, significant}, ...} for all pairs
    """
    ...
```

---

### Evaluate (`code/evaluate.py`)

**Dependencies**: Config, Analyze

```python
import json, yaml
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from config import RepairConfig, GRANULARITY_LEVELS

def save_results(
    results: list[dict],
    metrics: dict,
    posthoc: dict | None,
    config: RepairConfig,
) -> None:
    """Save repair_results.json, metrics.yaml, posthoc.yaml."""
    ...

def plot_success_rate_bar(groups: dict[str, list[int]], figures_dir: str) -> None:
    """Bar chart: repair success rate per granularity with 95% CI error bars."""
    ...

def plot_granularity_curve(groups: dict[str, list[int]], figures_dir: str) -> None:
    """Line plot: repair rate vs granularity level (G0 -> G4)."""
    ...

def plot_anova_summary(metrics: dict, figures_dir: str) -> None:
    """F-statistic, p-value, eta-squared visualization."""
    ...

def plot_gate_comparison(metrics: dict, figures_dir: str, alpha: float = 0.05) -> None:
    """Bar chart: ANOVA p-value vs 0.05 threshold."""
    ...

def plot_posthoc_heatmap(posthoc: dict, figures_dir: str) -> None:
    """Heatmap of Tukey HSD p-values for all granularity pairs (if ANOVA significant)."""
    ...

def plot_error_type_breakdown(results: list[dict], groups: dict, figures_dir: str) -> None:
    """Stratified repair success by error type (IndexError, TypeError, etc.)."""
    ...

def generate_all_figures(
    results: list[dict],
    groups: dict[str, list[int]],
    metrics: dict,
    posthoc: dict | None,
    config: RepairConfig,
) -> None:
    """Generate all required figures and save to config.figures_dir."""
    ...
```

---

### Train / Main Runner (`code/train.py`)

**Dependencies**: Config, Data, Repair, Analyze, Evaluate

```python
import argparse, os, sys
from config import RepairConfig
from data import load_runtime_error_cases, load_mbpp_index, parse_error_info
from repair import run_repair_experiment, load_checkpoint
from analyze import aggregate_by_granularity, run_anova, run_posthoc
from evaluate import save_results, generate_all_figures

# reuse H-E1 CodeGenerator
sys.path.insert(0, "../h-e1/code")
from model import CodeGenerator

def main() -> None:
    """Entry point: parse args, run experiment, report gate result.

    Pipeline:
      1. Load H-E1 runtime error cases (304)
      2. Load MBPP index for task text + test_list
      3. Load CodeLlama-7B-Instruct (same as H-E1)
      4. Run 1,520 repair attempts (304 × 5 granularity levels)
      5. ANOVA analysis
      6. Post-hoc Tukey HSD (if significant)
      7. Save results + generate figures
      8. Report gate: ANOVA p < 0.05

    CLI args: --gpu INT, --results-dir STR, --h-e1-results STR
    Exit code: 0 if gate passes, 1 if fails.
    """
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config.py, requirements.txt | 5 | 1+1+1+2 |
| A-2 | Data Loading | load_runtime_error_cases + load_mbpp_index + parse_error_info | 9 | 2+2+3+2 |
| A-3 | Feedback Formatter | format_feedback (G0-G4) + construct_repair_prompt | 8 | 2+1+3+2 |
| A-4 | Executor Module | execute_and_verify adapted from H-E1; binary success only | 7 | 2+2+2+1 |
| A-5 | Repair Pipeline | run_repair_experiment: 304×5 loop, checkpoint/resume | 14 | 3+3+4+4 |
| A-6 | ANOVA Analysis | aggregate_by_granularity + run_anova + eta_squared | 11 | 2+2+4+3 |
| A-7 | Tukey HSD Post-hoc | run_posthoc using scipy.stats.tukey_hsd, pairwise dict | 10 | 2+2+4+2 |
| A-8 | Results Persistence | save_results: JSON + YAML outputs, path creation | 6 | 1+2+1+2 |
| A-9 | Visualization | All 6 figures: bar, line, anova summary, gate, heatmap, breakdown | 12 | 3+2+3+4 |
| A-10 | Main Runner | train.py: pipeline orchestration, CLI args, gate verdict, exit code | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-6, A-7, A-9, A-10, A-2], Low(4-8): [A-1, A-3, A-4, A-8]

---

## Data Flow

- `h-e1/results/execution_results.json` -> `data.py:load_runtime_error_cases()` -> 304 runtime error dicts
- MBPP HuggingFace -> `data.py:load_mbpp_index()` -> task text + test_list per task_id
- stderr strings -> `data.py:parse_error_info()` -> structured {type, message, line, traceback}
- (case, granularity) -> `feedback.py:construct_repair_prompt()` -> prompt string
- prompt -> `CodeGenerator.generate()` (H-E1 model.py) -> repaired code string
- repaired code + test_list -> `executor.py:execute_and_verify()` -> bool
- 1,520 bool results -> `analyze.py:aggregate_by_granularity()` -> groups dict
- groups -> `analyze.py:run_anova()` -> ANOVA metrics (gate decision)
- groups -> `analyze.py:run_posthoc()` -> pairwise Tukey HSD (if p < 0.05)
- all results -> `evaluate.py` -> JSON/YAML files + 6 figures

---

## Key Interface Contracts

**H-E1 execution_results.json record** (verified from actual code):
```
{task_id: int, category: str, stderr: str|null, generated_code: str}
```

**parse_error_info output**:
```
{type: str, message: str, line: int|None, traceback: str}
```

**repair result record**:
```
{task_id: int, granularity: str, repaired_code: str, success: bool, execution_time: float}
```

**ANOVA metrics output**:
```
{f_statistic: float, p_value: float, eta_squared: float, gate_passed: bool,
 success_rates: {G0..G4: float}, n_per_group: int}
```
