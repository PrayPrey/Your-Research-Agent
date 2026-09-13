# Architecture: h-e1 (EXISTENCE PoC)

**Hypothesis:** h-e1 — Formal Repair Tool Operationality and Benchmark Accessibility
**Type:** EXISTENCE (PoC)
**Date:** 2026-05-09

Applied: PoC minimal pipeline pattern
Applied: Python code generation evaluation pipeline

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no prior modules to reuse

---

## File Organization

```
h-e1/
  code/
    data_loader.py
    baseline_generator.py
    syncode_generator.py
    z3_eligibility.py
    mypy_checker.py
    metrics.py
    visualization.py
    run_experiment.py
  data/
    baseline_pool.jsonl
    syncode_pool.jsonl
    z3_eligibility.json
    mypy_results.json
  results/
    metrics.json
  figures/
    gate_metrics.pdf
    gate_metrics.png
    ast_failure_heatmap.pdf
    ast_failure_heatmap.png
    z3_eligibility.pdf
    z3_eligibility.png
    mypy_error_types.pdf
    mypy_error_types.png
```

---

## Module Interfaces

### DataLoader (`code/data_loader.py`)

**Dependencies**: evalplus

```python
from typing import Dict, List, Any

def load_humaneval_plus() -> Dict[str, Dict[str, Any]]: ...
    # Returns dict of 164 problem dicts keyed by task_id
    # Each value: {task_id, prompt, canonical_solution, test}

def load_mbpp_plus() -> Dict[str, Dict[str, Any]]: ...
    # Returns dict of 374 problem dicts keyed by task_id

def validate_datasets(humaneval: dict, mbpp: dict) -> bool: ...
    # Asserts len(humaneval)==164, len(mbpp)==374
```

---

### BaselineGenerator (`code/baseline_generator.py`)

**Dependencies**: transformers, torch, data_loader

```python
from typing import Dict, List

class BaselineGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ): ...

    def load_model(self) -> None: ...
        # AutoModelForCausalLM.from_pretrained(device_map="auto")
        # AutoTokenizer.from_pretrained(...)

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],
        output_path: str,
    ) -> Dict[str, List[str]]: ...
        # Generates N=20 samples per problem with seeds=[0..19]
        # Serializes pool to output_path as JSONL
        # Returns {task_id: [completion_str x 20]}
```

---

### SyncodeGenerator (`code/syncode_generator.py`)

**Dependencies**: syncode, transformers, torch, data_loader

```python
from typing import Dict, List

class SyncodeGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ): ...

    def load_model(self) -> None: ...
        # SynCode(model=model, grammar=grammar, tokenizer=tokenizer, mode=mode)

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],
        output_path: str,
    ) -> Dict[str, List[str]]: ...
        # Grammar-constrained pool generation
        # Logs grammar_decoder.filtered_count per step
        # Serializes pool to output_path as JSONL
        # Returns {task_id: [completion_str x 20]}

    def verify_constraint_active(
        self, pool: Dict[str, List[str]]
    ) -> bool: ...
        # Asserts filtered_count > 0 for >= 50% of problems
```

---

### Z3EligibilityChecker (`code/z3_eligibility.py`)

**Dependencies**: z3-solver, data_loader

```python
from typing import Dict, Tuple

class Z3EligibilityChecker:
    def __init__(self, timeout_ms: int = 2000): ...

    def extract_postconditions(self, problem: dict) -> List[str]: ...
        # Parse docstring asserts for LIA-encodable constraints

    def check_problem(self, problem: dict) -> Tuple[bool, str]: ...
        # Returns (is_eligible, reason)
        # Sets z3.Solver().set("timeout", self.timeout_ms)

    def check_all(
        self,
        problems: Dict[str, dict],
        output_path: str,
    ) -> Dict[str, bool]: ...
        # Runs check_problem on all HumanEval problems
        # Serializes {task_id: bool} to output_path as JSON
        # Returns eligibility dict
```

---

### MypyChecker (`code/mypy_checker.py`)

**Dependencies**: mypy

```python
from typing import Dict, List, Tuple

class MypyChecker:
    def __init__(self): ...

    def check_code(self, code: str) -> Tuple[str, str, int]: ...
        # Calls mypy.api.run() on code string
        # Returns (stdout, stderr, exit_code)

    def parse_output(self, stdout: str) -> List[dict]: ...
        # Parses mypy stdout into structured error list
        # Each: {line, col, error_code, message}

    def check_pool(
        self,
        pool: Dict[str, List[str]],
        output_path: str,
        sample_size: int = 50,
    ) -> Dict[str, Any]: ...
        # Runs mypy on sample_size random completions from pool
        # Serializes results to output_path as JSON
        # Returns {task_id: [{stdout, stderr, exit_code, parsed_errors}]}
```

---

### MetricsEvaluator (`code/metrics.py`)

**Dependencies**: data_loader, baseline_generator (output), syncode_generator (output), z3_eligibility (output), mypy_checker (output)

```python
from typing import Dict, Any

class MetricsEvaluator:
    def compute_ast_failure_rate(
        self, pool: Dict[str, List[str]]
    ) -> Dict[str, float]: ...
        # {task_id: failure_rate} using ast.parse per completion

    def compute_delta_ast(
        self,
        baseline_pool: Dict[str, List[str]],
        syncode_pool: Dict[str, List[str]],
    ) -> float: ...
        # Δ_ast = baseline_rate - syncode_rate (must be > 0)

    def compute_z3_eligibility_rate(
        self, eligibility: Dict[str, bool]
    ) -> float: ...
        # eligible_count / total_humaneval_count (must be >= 0.15)

    def compute_mypy_structured_rate(
        self, mypy_results: Dict[str, Any]
    ) -> float: ...
        # parseable_count / total_checked (must be >= 0.90)

    def evaluate_gate(
        self,
        delta_ast: float,
        z3_rate: float,
        mypy_rate: float,
        output_path: str,
    ) -> Dict[str, Any]: ...
        # Evaluates all three gate conditions
        # Serializes full metrics to output_path as JSON
        # Returns {delta_ast, z3_eligibility_rate, mypy_rate, gate_pass: bool}
```

---

### Visualizer (`code/visualization.py`)

**Dependencies**: matplotlib, seaborn, metrics (output)

```python
class Visualizer:
    def __init__(self, figures_dir: str): ...

    def plot_gate_metrics(
        self, metrics: dict, save_path: str
    ) -> None: ...
        # Bar chart of Δ_ast, z3_rate, mypy_rate vs thresholds

    def plot_ast_failure_heatmap(
        self,
        baseline_rates: Dict[str, float],
        syncode_rates: Dict[str, float],
        save_path: str,
    ) -> None: ...
        # Heatmap: per-problem ast failure rate (baseline vs syncode)

    def plot_z3_eligibility(
        self, eligibility: Dict[str, bool], save_path: str
    ) -> None: ...
        # Bar/pie chart of eligible vs non-eligible problems

    def plot_mypy_error_types(
        self, mypy_results: dict, save_path: str
    ) -> None: ...
        # Distribution of mypy error codes across checked samples

    def save_all(self, metrics: dict, pools: dict, eligibility: dict, mypy_results: dict) -> None: ...
        # Calls all four plot methods, saves .pdf and .png per figure
```

---

### ExperimentRunner (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # Orchestrates full pipeline:
    # 1. Load datasets (DataLoader)
    # 2. Generate baseline pool (BaselineGenerator)
    # 3. Generate syncode pool (SyncodeGenerator)
    # 4. Check z3 eligibility (Z3EligibilityChecker)
    # 5. Run mypy checks (MypyChecker)
    # 6. Compute metrics and evaluate gate (MetricsEvaluator)
    # 7. Generate figures (Visualizer)
    # 8. Print gate PASS/FAIL summary

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Loading Setup | Implement DataLoader with evalplus, validate dataset sizes | 5 | 2+1+1+1 |
| E-2 | Baseline Pool Generation | Load CodeLlama-7B, generate N=20 samples per problem, serialize JSONL | 14 | 4+3+4+3 |
| E-3 | SynCode Pool Generation | Integrate SynCode LogitsProcessor, generate constrained pool, verify constraint active | 16 | 4+4+4+4 |
| E-4 | Z3 Eligibility Checking | Extract postconditions, run Z3 SMT encoding check on all HumanEval problems | 12 | 3+2+4+3 |
| E-5 | mypy Structured Output Check | Run mypy.api.run() on sampled completions, parse structured output | 8 | 2+2+2+2 |
| E-6 | Metrics Computation and Gate Evaluation | Compute Δ_ast, z3_eligibility_rate, mypy_rate; evaluate gate conditions | 10 | 3+3+2+2 |
| E-7 | Visualization | Generate 4 figures (gate_metrics, heatmap, z3_eligibility, mypy_error_types) | 7 | 2+1+2+2 |
| E-8 | Integration and Experiment Runner | Wire all modules in run_experiment.py; end-to-end validation | 9 | 2+3+2+2 |

**Distribution**: Very High (18-20): [], High (14-17): [E-2, E-3], Medium (9-13): [E-4, E-6, E-8], Low (4-8): [E-1, E-5, E-7]

---

## Gate Conditions

| Metric | Threshold | Source |
|--------|-----------|--------|
| Δ_ast | > 0 | metrics.compute_delta_ast() |
| z3_eligibility_rate | >= 0.15 | metrics.compute_z3_eligibility_rate() |
| mypy_structured_output_rate | >= 0.90 | metrics.compute_mypy_structured_rate() |

All three must pass for gate PASS. Any failure → MUST_WORK gate FAIL → route to Phase 0.

---

## Dependencies

```
evalplus>=0.3.0
transformers>=4.35
accelerate
torch
syncode  # pip install syncode or git clone uiuc-focal-lab/syncode
z3-solver
mypy
matplotlib
seaborn
```
