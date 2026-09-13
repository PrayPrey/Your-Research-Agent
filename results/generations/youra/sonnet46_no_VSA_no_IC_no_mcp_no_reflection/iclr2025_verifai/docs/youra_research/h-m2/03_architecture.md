# H-M2 Architecture

**Applied**: measurement-pipeline pattern (subprocess verifiers + statistical comparison)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Patterns found from actual H-M1 code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: `execute_solution()` returns `{passed, error, error_type, tmp_path, code}` dict. `classify_bug_type(code, execution_result)` handles Pyright internally via `_run_pyright()`. Both reused directly — H-M2 adds measurement layer on top.

---

## File/Module Layout

- `run_h_m2.py` — main entry point
- `src/load_h_m1.py` — load H-M1 failing solutions from results.jsonl
- `src/z3_extractor.py` — LLM-based Z3 constraint extraction from docstrings
- `src/measure.py` — 4-verifier feedback measurement pipeline
- `src/analyze.py` — Kruskal-Wallis + Dunn post-hoc + effect size
- `src/visualize.py` — 5 required figures
- `src/write_results.py` — persist results.jsonl and summary.json
- `results/h-m2/results.jsonl` — per-problem per-verifier records
- `results/h-m2/summary.json` — aggregated stats
- `figures/` — 5 output figures

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| execute_solution | `from src.execute import execute_solution` | `h-m1/code/src/execute.py` |
| classify_bug_type | `from src.classify import classify_bug_type` | `h-m1/code/src/classify.py` |
| Problem | `from src.data_loader import Problem` | `h-m1/code/src/data_loader.py` |

**Note**: H-M2 does not re-run execution or classification — it reads pre-computed H-M1 results.jsonl. These imports are available if needed for type references only.

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation)

---

## Module Interfaces

### LoadH1Results (`src/load_h_m1.py`)

**Dependencies**: stdlib json, pathlib

```python
def load_failing_records(results_path: str = "results/h-m1/results.jsonl") -> list[dict]: ...
# Returns list of {task_id, source, passed, bug_type, code, prompt, test_code, ...}
# Filters to passed==False only
```

---

### Z3ConstraintExtractor (`src/z3_extractor.py`)

**Dependencies**: openai, z3-solver

```python
class Z3ConstraintExtractor:
    def __init__(self, client, model: str = "gpt-4o-mini", timeout_secs: int = 10): ...
    def extract(self, task_id: str, docstring: str) -> list | None: ...
    # Returns z3 constraint list or None if extraction fails/not applicable
    # Prompts GPT-4o-mini to produce Z3 Python expressions from docstring
    # ~40% coverage expected; None → field_count=0, char_count=0
```

---

### FeedbackMeasurer (`src/measure.py`)

**Dependencies**: subprocess, json, tempfile, os, z3-solver, Z3ConstraintExtractor

```python
class FeedbackMeasurer:
    def __init__(self, timeout_secs: int = 10): ...

    def measure_execution(self, code: str) -> dict: ...
    # Returns {"verifier": "execution", "char_count": int, "field_count": 1, "timeout": bool}
    # Runs code via subprocess, captures stderr

    def measure_pyright(self, code: str) -> dict: ...
    # Returns {"verifier": "pyright", "char_count": int, "field_count": int, "timeout": bool}
    # pyright --outputjson; field_count = sum(len(e) for e in generalDiagnostics)

    def measure_mypy(self, code: str) -> dict: ...
    # Returns {"verifier": "mypy", "char_count": int, "field_count": int, "timeout": bool}
    # field_count = count of lines with ": error:"

    def measure_z3(self, constraints: list | None) -> dict: ...
    # Returns {"verifier": "z3", "char_count": int, "field_count": int, "timeout": bool}
    # char_count=len(str(model)), field_count=len(model) if sat; else 0s

    def measure_all(self, code: str, z3_constraints: list | None) -> list[dict]: ...
    # Returns list of 4 measurement dicts (one per verifier), sequential
```

---

### StatisticalAnalyzer (`src/analyze.py`)

**Dependencies**: scipy, scikit-posthocs, pandas

```python
def run_analysis(records: list[dict]) -> dict: ...
# records: list of {task_id, verifier, char_count, field_count, bug_type, ...}
# Returns:
#   {
#     "per_verifier": {verifier: {mean, median, std, n}},
#     "kruskal_wallis": {"H": float, "p": float},
#     "effect_size_epsilon2": float,
#     "dunn_pvalues": dict,          # pairwise Bonferroni-corrected
#     "ordering_confirmed": bool,    # SMT >= {pyright,mypy} > execution
#     "pairwise_diff_pct": dict,     # % diff between adjacent categories
#   }
```

---

### Visualizer (`src/visualize.py`)

**Dependencies**: matplotlib, seaborn, pandas

```python
def plot_bar_mean_char_count(df: "pd.DataFrame", out_dir: str) -> None: ...
# figures/bar_mean_char_count.png — mean char_count per verifier with 95% CI

def plot_box_char_count(df: "pd.DataFrame", out_dir: str) -> None: ...
# figures/box_char_count.png — distribution per verifier

def plot_heatmap_char_bug_type(df: "pd.DataFrame", out_dir: str) -> None: ...
# figures/heatmap_char_bug_type.png — char_count vs bug_type cross-tab

def plot_cdf_char_count(df: "pd.DataFrame", out_dir: str) -> None: ...
# figures/cdf_char_count.png — CDF per verifier

def plot_scatter_char_field(df: "pd.DataFrame", out_dir: str) -> None: ...
# figures/scatter_char_field.png — char_count vs field_count per verifier

def generate_all_figures(records: list[dict], out_dir: str = "figures/") -> None: ...
```

---

### ResultWriter (`src/write_results.py`)

**Dependencies**: json, pathlib

```python
def write_records(records: list[dict], path: str = "results/h-m2/results.jsonl") -> None: ...
# One line per (task_id, verifier) measurement

def write_summary(analysis: dict, path: str = "results/h-m2/summary.json") -> None: ...
```

---

### Entry Point (`run_h_m2.py`)

**Dependencies**: all src modules, concurrent.futures

```python
def main() -> None: ...
# 1. load_failing_records() → failing list
# 2. verify_tool_activation() sanity check on sample
# 3. Z3ConstraintExtractor for each record (batch, 4 workers)
# 4. FeedbackMeasurer.measure_all() per record (4 workers, verifiers sequential)
# 5. run_analysis(records)
# 6. generate_all_figures(records)
# 7. write_records / write_summary
# 8. print gate result: ordering_confirmed + KW p-value
```

---

## Record Schema

```python
# results/h-m2/results.jsonl — one record per (task_id, verifier)
{
    "task_id": str,
    "source": str,           # "humaneval" | "mbpp"
    "bug_type": str,         # from H-M1 classification
    "verifier": str,         # "execution" | "pyright" | "mypy" | "z3"
    "char_count": int,
    "field_count": int,
    "timeout": bool
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & H-M1 loader | Project structure, load_h_m1.py, verify H-M1 results.jsonl accessible | 6 | 1+2+1+2 |
| A-2 | Execution verifier | measure_execution() in FeedbackMeasurer; subprocess stderr capture | 7 | 2+2+1+2 |
| A-3 | Pyright verifier | measure_pyright(); reuse _run_pyright pattern from H-M1 classify.py | 7 | 2+2+2+1 |
| A-4 | mypy verifier | measure_mypy(); subprocess, parse ": error:" lines | 6 | 2+1+2+1 |
| A-5 | Z3 constraint extractor | Z3ConstraintExtractor; GPT-4o-mini prompt → z3 constraints; ~40% coverage | 15 | 3+3+5+4 |
| A-6 | Z3 verifier | measure_z3(); z3 Solver + sat/unsat + model measurement | 12 | 3+3+4+2 |
| A-7 | measure_all + parallel runner | FeedbackMeasurer.measure_all(); concurrent.futures for 4-worker problem parallelism | 9 | 2+3+2+2 |
| A-8 | Statistical analysis | run_analysis(); kruskal, Dunn posthoc, ε², ordering_confirmed flag | 13 | 3+2+5+3 |
| A-9 | Visualization | 5 figures via matplotlib/seaborn | 10 | 2+2+3+3 |
| A-10 | Result persistence + entry point | write_records/write_summary, run_h_m2.py orchestration, sanity check | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-5], Medium(9-13): [A-6, A-7, A-8, A-9], Low(4-8): [A-1, A-2, A-3, A-4, A-10]
