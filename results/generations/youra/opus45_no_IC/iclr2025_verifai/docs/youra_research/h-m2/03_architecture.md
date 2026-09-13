# Architecture: H-M2 — Static Analysis Feedback Loop

**Tier**: FULL | **Type**: MECHANISM

Applied: subprocess-based static analyzer wrapper (Bandit+Pylint JSON output parsing, per cyb3rlab/CodeEnhancer pattern)
Applied: iterate-until-convergence loop with early termination on zero issues

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: `h-m1/code/` does not exist on disk (base hypothesis has no persisted implementation to reuse); H-M2's mechanism (static analysis subprocess loop) is unrelated to H-M1's grammar-constrained decoding, so no code reuse applies regardless.
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Reused only the `ExperimentConfig` dataclass pattern and orchestrator structure documented in `h-m1/03_architecture.md` for consistency.

---

## File Organization

```
h-m2/code/
├── config.py
├── data_loader.py
├── generator.py         # CodeGenerator (baseline + feedback-aware)
├── analyzers.py          # BanditAnalyzer, PylintAnalyzer
├── feedback_formatter.py # issues -> LLM prompt text
├── feedback_loop.py       # IterationController
├── metrics.py             # issue counting, reduction calc
├── evaluate.py            # compare initial vs final, gate check
├── visualize.py
├── run_experiment.py      # orchestrator
└── figures/
```

---

## Module Interfaces

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    dataset_id: str = "s2e-lab/SecurityEval"
    temperature: float = 0.2
    max_new_tokens: int = 512
    max_iterations: int = 5
    analysis_timeout_s: int = 30
    seed: int = 1
    device: str = "cuda"
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### DataLoader (`data_loader.py`)

**Dependencies**: Config, datasets

```python
def load_security_eval_prompts(dataset_id: str) -> list[dict]: ...
    # returns [{"id": str, "prompt": str, "cwe": str}, ...], Python-only filtered
```

### CodeGenerator (`generator.py`)

**Dependencies**: Config, transformers

```python
class CodeGenerator:
    def __init__(self, model_id: str, device: str, seed: int): ...
    def generate(self, prompt: str, temperature: float, max_new_tokens: int) -> str: ...
    def refine(self, code: str, feedback: str, temperature: float, max_new_tokens: int) -> str: ...
        # refine = generate() with feedback appended to prompt template
```

### Analyzers (`analyzers.py`)

**Dependencies**: subprocess, json (stdlib)

```python
class BanditAnalyzer:
    def run(self, code: str, timeout_s: int) -> list[dict]: ...
        # writes code to temp file, runs `bandit -f json`, returns results list

class PylintAnalyzer:
    def run(self, code: str, timeout_s: int) -> list[dict]: ...
        # writes code to temp file, runs `pylint --output-format=json`, returns messages
```

### FeedbackFormatter (`feedback_formatter.py`)

**Dependencies**: none

```python
def format_issues_for_prompt(bandit_issues: list[dict], pylint_issues: list[dict]) -> str: ...
    # returns structured text: "Line N: [SECURITY/RELIABILITY] description"
```

### IterationController (`feedback_loop.py`)

**Dependencies**: CodeGenerator, BanditAnalyzer, PylintAnalyzer, FeedbackFormatter, metrics

```python
class IterationController:
    def __init__(self, generator: CodeGenerator, bandit: BanditAnalyzer, pylint: PylintAnalyzer, max_iterations: int, timeout_s: int): ...
    def run(self, initial_code: str) -> dict: ...
        # loop: analyze -> if no issues break -> format feedback -> refine -> repeat
        # returns {"initial": dict, "final": dict, "iterations": int, "history": list[dict]}
```

### Metrics (`metrics.py`)

**Dependencies**: none

```python
def count_issues(bandit_results: list[dict], pylint_results: list[dict]) -> dict: ...
    # returns {"security": int, "reliability": int}
def issue_reduction(initial: int, final: int) -> float: ...
    # (initial - final) / initial, 0.0 if initial == 0
```

### Evaluator (`evaluate.py`)

**Dependencies**: metrics

```python
def evaluate_condition(loop_results: list[dict]) -> dict: ...
    # aggregates security_issue_reduction, reliability_issue_reduction, mean iterations
def check_gate(agg_results: dict) -> bool: ...
    # final_security < initial_security AND final_reliability < initial_reliability
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, Evaluator outputs

```python
def plot_gate_metrics_comparison(initial: dict, final: dict, out_path: str) -> None: ...
def plot_issue_reduction_over_iterations(history: list[dict], out_path: str) -> None: ...
def plot_cwe_distribution(prompts: list[dict], out_path: str) -> None: ...
```

### Orchestrator (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. load config + set seed
    # 2. load SecurityEval prompts (Python-only)
    # 3. generate baseline code per prompt (CodeGenerator.generate)
    # 4. run IterationController per prompt -> collect loop_results
    # 5. evaluate_condition + check_gate
    # 6. generate figures + summary table
```

---

## External Dependencies (Base Hypothesis)

No code reuse from H-M1: mechanisms are unrelated (grammar-constrained decoding vs. static-analysis feedback loop), and `h-m1/code/` does not exist on disk. Only the `ExperimentConfig` dataclass shape and orchestrator flow pattern were carried over conceptually from `h-m1/03_architecture.md` (no import).

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffolding | ExperimentConfig, dirs, seeding | 5 | 1+1+1+2 |
| A-2 | Data loading | Load SecurityEval via datasets, filter Python, extract CWE | 6 | 2+2+1+1 |
| A-3 | Static analyzer integration | BanditAnalyzer + PylintAnalyzer subprocess wrappers, temp-file handling, timeout | 12 | 3+2+4+3 |
| A-4 | Feedback formatter | Convert Bandit/Pylint JSON to structured LLM prompt text | 6 | 2+1+2+1 |
| A-5 | Code generator | CodeGenerator with generate() + refine() (feedback-injected prompt) | 10 | 3+3+2+2 |
| A-6 | Iteration controller | Feedback loop: analyze -> format -> refine -> repeat until convergence or max_iterations | 14 | 3+4+4+3 |
| A-7 | Metrics calculator | count_issues, issue_reduction functions | 4 | 1+1+1+1 |
| A-8 | Baseline generation run | Generate initial code for all 121 prompts, persist | 8 | 2+2+2+2 |
| A-9 | Feedback loop run | Execute IterationController across all prompts, persist history | 10 | 2+3+2+3 |
| A-10 | Evaluation & gate check | Aggregate reductions, PASS/FAIL determination | 6 | 2+1+2+1 |
| A-11 | Visualization | Gate bar chart, iteration line plot, CWE distribution | 7 | 2+2+1+2 |
| A-12 | End-to-end orchestration | Wire all modules, logging, error handling | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-6], Medium(9-13): [A-3, A-5, A-9], Low(4-8): [A-1, A-2, A-4, A-7, A-8, A-10, A-11, A-12]
