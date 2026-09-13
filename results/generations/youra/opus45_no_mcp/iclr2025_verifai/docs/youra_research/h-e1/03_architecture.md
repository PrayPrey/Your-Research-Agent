# Architecture: H-E1 (Existence of Orthogonal Error Classes)

**Type:** EXISTENCE (PoC) | **Tier:** LIGHT | **Gate:** Mean Jaccard < 0.3

Applied: analysis-pipeline pattern (generate → dual-analyze → compare, no training loop)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. Archon/Serena MCP unavailable in this environment (per 02c_experiment_brief.md); design derived directly from PRD pseudo-code.

---

## File Structure

```
h-e1/code/
  config.py
  generate.py
  static_analysis.py
  exec_analysis.py
  jaccard.py
  run_analysis.py
  evaluate.py
  visualize.py
```

---

## Modules

### config.py

**Dependencies**: none

```python
MODEL_NAME: str = "gpt-3.5-turbo"  # or codellama/CodeLlama-7b-Instruct-hf
SEED: int = 42
JACCARD_GATE: float = 0.3
NON_OVERLAP_GATE: float = 0.7
OUTPUT_DIR: str = "results/"
FIGURES_DIR: str = "figures/"
```

### generate.py (`code/generate.py`)

**Dependencies**: config

```python
def load_problems() -> dict:  # {problem_id: problem}
def generate_code(problem: dict, model_name: str) -> str: ...
def generate_all(problems: dict) -> dict:  # {problem_id: code_str}
```

### static_analysis.py (`code/static_analysis.py`)

**Dependencies**: none

```python
def run_pylint(code: str) -> set[str]: ...
def run_mypy(code: str) -> set[str]: ...
def run_static_analysis(code: str) -> set[str]:  # union of pylint+mypy error codes
```

### exec_analysis.py (`code/exec_analysis.py`)

**Dependencies**: evalplus

```python
def run_execution_tests(problem_id: str, code: str, problem: dict) -> set[str]:
    # failure types: wrong_answer, runtime_error, timeout
```

### jaccard.py (`code/jaccard.py`)

**Dependencies**: none

```python
def compute_jaccard(set_a: set, set_b: set) -> float: ...
def categorize(static_errors: set, exec_errors: set) -> str:
    # "static_only" | "exec_only" | "both" | "neither"
```

### run_analysis.py (`code/run_analysis.py`)

**Dependencies**: generate, static_analysis, exec_analysis, jaccard, config

```python
def analyze_error_orthogonality(problems: dict) -> dict:
    # returns {jaccard_scores, static_only, exec_only, both,
    #          mean_jaccard, non_overlapping_pct, per_problem: [...]}
def main() -> None: ...  # entry point, writes results/results.json
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: config

```python
def evaluate_gate(results: dict) -> tuple[bool, str]: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: config, matplotlib

```python
def plot_gate_metrics(results: dict, path: str) -> None: ...        # required
def plot_jaccard_histogram(results: dict, path: str) -> None: ...
def plot_error_venn(results: dict, path: str) -> None: ...
def plot_category_breakdown(results: dict, path: str) -> None: ...
def plot_per_benchmark(results: dict, path: str) -> None: ...
def generate_all_figures(results: dict) -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Dataset loading | Load HumanEval+/MBPP+ via evalplus (563 problems) | 5 | 1+1+2+1 |
| A-2 | Code generation | Generate 1 solution/problem via LLM API, seeded | 9 | 2+3+3+1 |
| A-3 | Static analysis pipeline | pylint+mypy subprocess wrappers, error set extraction | 8 | 2+2+3+1 |
| A-4 | Execution analysis pipeline | evalplus test execution, failure-type extraction | 8 | 2+3+2+1 |
| A-5 | Jaccard + categorization | Compute per-problem Jaccard, overlap category counts | 4 | 1+1+1+1 |
| A-6 | Full pipeline orchestration | Wire generate→static→exec→jaccard over 563 problems, persist results | 7 | 2+2+2+1 |
| A-7 | Gate evaluation | Compute mean Jaccard, non-overlap %, PASS/FAIL check | 3 | 1+1+1+0 |
| A-8 | Visualization suite | 4 required figures + gate bar chart, saved to figures/ | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-7, A-8]

---

## External Dependencies

None (green-field). Third-party libs only: `evalplus`, `pylint`, `mypy`, `transformers` or `openai`, `matplotlib`.
