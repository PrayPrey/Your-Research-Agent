# Architecture: H-E1 — Runtime Error Prevalence in LLM-Generated Code

**Hypothesis Type**: EXISTENCE
**Date**: 2026-03-30
**Pattern Applied**: subprocess-execution-pattern, proportion-confint-wilson-CI

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Organization

```
code/
  config.py       - experiment configuration dataclass
  data.py         - MBPP dataset loading and prompt formatting
  model.py        - CodeLlama inference wrapper
  executor.py     - subprocess code execution and error categorization
  evaluate.py     - prevalence calculation, persistence, visualization
  train.py        - main experiment runner (entry point)
  results/
    execution_results.json
    metrics.yaml
    figures/
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510
    max_new_tokens: int = 512
    temperature: float = 0.0
    execution_timeout: int = 10
    seed: int = 1
    results_dir: str = "results"
    figures_dir: str = "results/figures"
    output_json: str = "results/execution_results.json"
    output_metrics: str = "results/metrics.yaml"
    gate_threshold: float = 0.30
    ci_confidence: float = 0.95
```

---

### DataLoader (`code/data.py`)

**Dependencies**: Config

```python
def load_mbpp_test(config: ExperimentConfig) -> list[dict]: ...
# Returns list of {task_id, text, code, test_list} for IDs 11-510
# Uses load_dataset("mbpp"), filters task_id in [11, 510], asserts len==500

def format_prompt(problem: dict) -> str: ...
# MBPP standard prompt: "You are an expert Python programmer..." + [BEGIN]
```

---

### CodeGenerator (`code/model.py`)

**Dependencies**: Config

```python
class CodeGenerator:
    def __init__(self, config: ExperimentConfig): ...
    def load(self) -> None: ...
    # Loads tokenizer + model (float16, device_map="auto")

    def generate(self, prompt: str) -> str: ...
    # Single inference call, returns extracted code

    def generate_batch(self, problems: list[dict]) -> list[str]: ...
    # Iterates problems, calls generate(), returns list of code strings

    def extract_code(self, raw_output: str) -> str: ...
    # Extracts between [BEGIN]/[DONE] markers or returns full response
```

---

### Executor (`code/executor.py`)

**Dependencies**: Config

```python
from enum import Enum
from typing import Optional

class ErrorCategory(Enum):
    PASS = "pass"
    RUNTIME_ERROR = "runtime_error"
    WRONG_OUTPUT = "wrong_output"
    SYNTAX_ERROR = "syntax_error"
    TIMEOUT = "timeout"

def execute_code(code: str, tests: list[str], timeout: int = 10) -> tuple[ErrorCategory, Optional[str]]: ...
# Runs subprocess ["python", "-c", code + "\n" + joined_tests]
# capture_output=True, text=True, timeout=timeout
# Returns (ErrorCategory, stderr or None)

def categorize_stderr(returncode: int, stderr: str) -> ErrorCategory: ...
# returncode==0 -> PASS
# "SyntaxError" in stderr -> SYNTAX_ERROR
# "Traceback (most recent call last):" in stderr -> RUNTIME_ERROR
# else -> WRONG_OUTPUT
# TimeoutExpired caught in execute_code -> TIMEOUT
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config, ErrorCategory

```python
def calculate_prevalence(results: list[dict]) -> dict: ...
# Computes runtime_errors/total_failures
# Uses proportion_confint(runtime_errors, total_failures, alpha=0.05, method='wilson')
# Returns {prevalence, ci_lower, ci_upper, n_runtime, n_failures, n_total, n_pass}

def check_gate(metrics: dict, threshold: float = 0.30) -> bool: ...
# Returns metrics["ci_lower"] >= threshold

def save_results(results: list[dict], config: ExperimentConfig) -> None: ...
# Writes execution_results.json (per-problem) and metrics.yaml (aggregate)

def plot_error_distribution(results: list[dict], figures_dir: str) -> None: ...
# Pie chart: PASS / RUNTIME_ERROR / WRONG_OUTPUT / SYNTAX_ERROR / TIMEOUT counts

def plot_runtime_error_types(results: list[dict], figures_dir: str) -> None: ...
# Bar chart: TypeError, ValueError, IndexError, KeyError, NameError, etc.
# Parsed from last line of stderr for RUNTIME_ERROR entries

def plot_prevalence_ci(metrics: dict, figures_dir: str) -> None: ...
# Point estimate + 95% Wilson CI error bars vs gate threshold line

def plot_gate_comparison(metrics: dict, figures_dir: str) -> None: ...
# Bar chart: target (0.30) vs actual prevalence with pass/fail annotation
```

---

### Runner (`code/train.py`)

**Dependencies**: Config, DataLoader, CodeGenerator, Executor, Evaluator

```python
def run_experiment(config: ExperimentConfig) -> dict: ...
# 1. load_mbpp_test(config) -> 500 problems
# 2. CodeGenerator(config).load()
# 3. generate_batch(problems) -> generated_codes
# 4. execute_code per problem -> results list
# 5. calculate_prevalence(results) -> metrics
# 6. save_results + all plots
# 7. check_gate -> log PASS/FAIL
# Returns metrics dict

def main() -> None: ...
# Parses optional CLI args, instantiates ExperimentConfig
# Sets CUDA_VISIBLE_DEVICES, calls run_experiment, prints gate result
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Config | Project structure, ExperimentConfig dataclass, results dir creation | 5 | 1+1+1+2 |
| A-2 | Data Loading | MBPP load via HuggingFace, filter IDs 11-510, prompt formatting | 7 | 2+1+2+2 |
| A-3 | Model Integration | CodeLlama-7B-Instruct load float16, generate, extract_code | 10 | 3+2+3+2 |
| A-4 | Execution Engine | Subprocess execution, timeout handling, error categorization by stderr | 9 | 2+1+3+3 |
| A-5 | Evaluation & Gate | Wilson CI prevalence calc, gate check, JSON/YAML persistence | 8 | 2+2+2+2 |
| A-6 | Visualization | 4 figures: pie, runtime type bar, CI plot, gate comparison | 7 | 2+1+2+2 |
| A-7 | Integration & Run | Full runner wiring all modules, 500-problem experiment, logging | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-7], Low(4-8): [A-1, A-2, A-5, A-6]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| transformers | >=4.35.0 | CodeLlama model loading and inference |
| datasets | >=2.14.0 | MBPP dataset via HuggingFace |
| torch | >=2.0.0 | GPU inference (float16) |
| scipy | >=1.10.0 | Wilson CI via proportion_confint |
| matplotlib | >=3.7.0 | 4 visualization figures |

---

## Experiment Scale

- Dataset: 500 problems (MBPP test split, IDs 11-510)
- Model: CodeLlama-7B-Instruct (7B params, float16, single GPU)
- Execution: subprocess per problem, 10s timeout
- Expected runtime: 2-4 hours total
- Gate: runtime_error_prevalence CI lower bound >= 0.30
