# Architecture: H-M1 (SA Metric Correlation with Functional Correctness)

**Type**: MECHANISM | **Gate**: MUST_WORK

Applied: subprocess-wrapper-with-timeout-pattern (reused from H-E1 design; KB had no direct correlation-analysis match, low relevance)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1) — but no actual code found
**Status**: `h-e1/code/` does not exist yet (only `03_architecture.md` spec present, no implementation on disk). Falling back to spec-only reuse; SA wrapper interfaces re-implemented fresh in H-M1 following H-E1's documented design (pylint/mypy/radon subprocess wrappers with timeout).
**Analyzed Path**: `h-e1/code/` (checked via glob — not found)
**Findings**: No prior implementation to import; H-M1 re-implements SA wrappers locally per H-E1 spec, adds pass@1 execution + correlation layer on top.

---

## File Structure

- `code/config.py` - fixed config (timeouts, paths, thresholds)
- `code/dataset.py` - load HumanEval + MBPP, dedupe to 591 samples
- `code/sa_tools.py` - pylint/mypy/radon subprocess wrappers (from H-E1 design)
- `code/completions.py` - load/generate LLM completions (JSONL)
- `code/eval_pass1.py` - execute test cases, binary pass/fail
- `code/metrics.py` - orchestrate SA extraction across samples → DataFrame
- `code/correlate.py` - point-biserial + partial correlation (LOC control)
- `code/visualize.py` - bar chart, scatter plots, heatmap
- `code/run.py` - main pipeline orchestration
- `requirements.txt` - pinned versions (scipy, pingouin, pandas, matplotlib, datasets)

---

## Module Interfaces

### config.py

```python
TIMEOUT_SEC: int = 30
TEST_TIMEOUT_SEC: int = 5
RESULTS_DIR: str = "results"
FIGURES_DIR: str = "figures"
CORR_THRESHOLD: float = 0.35
ALPHA: float = 0.05
```

### dataset.py (`code/dataset.py`)

**Dependencies**: config, datasets (HF), human_eval

```python
@dataclass
class Problem:
    task_id: str
    source: str  # "humaneval" | "mbpp"
    prompt: str
    canonical_solution: str
    test: str

def load_humaneval() -> list[Problem]: ...
def load_mbpp_sanitized() -> list[Problem]: ...
def load_all_problems() -> list[Problem]: ...  # dedupe -> 591
```

### completions.py (`code/completions.py`)

**Dependencies**: dataset, json

```python
@dataclass
class Completion:
    task_id: str
    completion: str

def load_completions_jsonl(path: str) -> list[Completion]: ...
def generate_completions(problems: list, api_fn: Callable) -> list[Completion]: ...  # optional, Option B
```

### eval_pass1.py (`code/eval_pass1.py`)

**Dependencies**: subprocess, config, dataset, completions

```python
def run_test(problem: Problem, completion: str, timeout: int = 5) -> bool: ...
def evaluate_all(problems: list[Problem], completions: list[Completion]) -> dict[str, bool]: ...  # task_id -> passed
```

### sa_tools.py (`code/sa_tools.py`)

**Dependencies**: subprocess, json, tempfile, config

```python
@dataclass
class ToolResult:
    success: bool
    metric: float | int | None
    error: str | None

def run_pylint(code_path: str, timeout: int = 30) -> ToolResult: ...
def run_mypy(code_path: str, timeout: int = 30) -> ToolResult: ...
def run_radon(code_path: str, timeout: int = 30) -> ToolResult: ...
```

### metrics.py (`code/metrics.py`)

**Dependencies**: sa_tools, eval_pass1, dataset, completions, pandas

```python
def compute_loc(code: str) -> int: ...
def build_dataframe(
    problems: list[Problem],
    completions: list[Completion],
    passed: dict[str, bool],
) -> pd.DataFrame: ...  # columns: task_id, passed, pylint_score, mypy_errors, radon_cc, loc
```

### correlate.py (`code/correlate.py`)

**Dependencies**: scipy.stats, pingouin, pandas, config

```python
def point_biserial(df: pd.DataFrame, metric: str) -> tuple[float, float]: ...  # r, p
def partial_corr_loc(df: pd.DataFrame, metric: str) -> tuple[float, float]: ...  # r_partial, p_partial
def compute_all_correlations(df: pd.DataFrame) -> dict: ...  # per-metric r_raw/p_raw/r_partial/p_partial
def determine_pass(results: dict, threshold: float = 0.35, alpha: float = 0.05) -> bool: ...
```

### visualize.py (`code/visualize.py`)

**Dependencies**: matplotlib, pandas, config

```python
def plot_bar_chart(results: dict, threshold: float, out_path: str) -> None: ...
def plot_scatter(df: pd.DataFrame, metric: str, out_path: str) -> None: ...  # jittered
def plot_heatmap(df: pd.DataFrame, out_path: str) -> None: ...
def generate_all_figures(df: pd.DataFrame, results: dict) -> None: ...
```

### run.py (`code/run.py`)

**Dependencies**: all modules above, json

```python
def main() -> None: ...
# 1. load_all_problems -> 591
# 2. load_completions_jsonl (or generate)
# 3. evaluate_all -> passed dict
# 4. build_dataframe -> df with SA metrics + loc + passed
# 5. compute_all_correlations -> results
# 6. determine_pass -> bool
# 7. write results/h_m1_correlations.json, h_m1_data.csv, h_m1_summary.json
# 8. generate_all_figures
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup & config | Project skeleton, requirements.txt, config.py | 5 | 1+1+1+2 |
| M-2 | Dataset loading | HumanEval + MBPP load, dedupe to 591 | 8 | 3+2+2+1 |
| M-3 | SA tool wrappers | pylint/mypy/radon subprocess wrappers (re-impl from H-E1 spec) | 8 | 2+1+2+3 |
| M-4 | Completions loading | JSONL loader + optional API generation path | 6 | 2+2+1+1 |
| M-5 | Pass@1 evaluation | Test execution harness, 5s timeout, binary outcome | 9 | 3+2+2+2 |
| M-6 | Metrics aggregation | Build DataFrame: SA metrics + LOC + passed per sample | 8 | 2+3+1+2 |
| M-7 | Correlation analysis | point-biserial + partial correlation (LOC control), pass/fail determination | 10 | 2+3+3+2 |
| M-8 | Visualization | Bar chart, scatter plots, correlation heatmap | 6 | 2+1+1+2 |
| M-9 | Full pipeline run | Orchestrate run.py, write result files, verify N>=500 and gate condition | 9 | 2+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M-5, M-6, M-7, M-9], Low(4-8): [M-1, M-2, M-3, M-4, M-8]

---

## External Dependencies (Base Hypothesis)

No importable code from H-E1 (implementation not yet present on disk). SA wrapper *design* (subprocess + timeout + JSON parse pattern) is reused conceptually per `h-e1/03_architecture.md`, re-implemented in `h-m1/code/sa_tools.py`.

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (Applied line only)
- [x] Interface-only module code
- [x] 9 Epic tasks (within 6-12 MECHANISM range) with complexity
- [x] Codebase Analysis (Serena) section included
- [x] Total length < 500 lines
