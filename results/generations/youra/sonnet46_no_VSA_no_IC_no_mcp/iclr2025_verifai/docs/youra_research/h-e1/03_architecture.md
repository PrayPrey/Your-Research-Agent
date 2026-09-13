---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Architecture: H-E1 — Type Error Prevalence in LLM-Generated Python Code

Applied: observational-pipeline (generate → evaluate → analyze → aggregate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── pipeline.py       # all pipeline logic (generate, evaluate, mypy, aggregate)
│   ├── visualize.py      # figure generation
│   └── run.py            # CLI entry point
├── figures/
└── results/
```

Three files total. All pipeline logic in `pipeline.py` — no unnecessary module split.

---

## Module Definitions

### Pipeline (`code/pipeline.py`)

**Dependencies**: openai, evalplus, mypy (subprocess), stdlib (tempfile, subprocess, json, pathlib)

```python
# Constants
SEEDS = [42, 123, 456]
BENCHMARKS = {"mbpp+": "get_mbpp_plus", "humaneval+": "get_human_eval_plus"}
MYPY_FLAGS = ["--ignore-missing-imports", "--no-strict-optional"]
MYPY_TIMEOUT = 30
RESULTS_DIR = pathlib.Path("docs/youra_research/h-e1/results")

def load_problems(benchmark: str) -> dict: ...
# Returns: dict[task_id, problem_dict] via evalplus API

def build_prompt(problem: dict) -> str: ...
# Returns: function completion prompt string

def extract_code(response_text: str) -> str: ...
# Strips markdown fences, returns raw Python code

def generate_solution(client: OpenAI, problem: dict, seed: int) -> str: ...
# Calls gpt-4o-mini with temperature=0.8, seed=seed, max_tokens=1024

def evaluate_solution(task_id: str, code: str, problem: dict) -> bool: ...
# Runs EvalPlus test suite; returns True=PASS

def run_mypy(code: str) -> tuple[bool, int]: ...
# Returns (has_error, error_count); timeout → (False, 0)

def run_benchmark(client: OpenAI, benchmark: str, seed: int) -> list[dict]: ...
# Returns list of result dicts for one benchmark × one seed
# dict keys: task_id, seed, benchmark, passed, has_mypy_error, error_count

def aggregate(results: list[dict]) -> dict: ...
# Returns summary: per benchmark per seed fraction + mean/std across seeds

def verify_mechanism_activated(results: list[dict]) -> tuple[bool, dict]: ...
# Returns (activated, indicators) where indicators has mypy_ran, errors_found,
# fraction_computed, sample_size_sufficient

def save_results(results: list[dict], summary: dict) -> None: ...
# Writes JSONL per benchmark/seed + summary.json to RESULTS_DIR
```

### Visualize (`code/visualize.py`)

**Dependencies**: matplotlib, json, pathlib

```python
FIGURES_DIR = pathlib.Path("docs/youra_research/h-e1/figures")

def plot_gate_metrics(summary: dict) -> None: ...
# Bar chart: type_error_fraction vs 0.10 threshold, std error bars
# Saves: figures/gate_metrics.png (REQUIRED)

def plot_error_type_dist(results: list[dict]) -> None: ...
# Bar chart of mypy error categories; saves figures/error_type_dist.png

def plot_error_count_hist(results: list[dict]) -> None: ...
# Histogram of error counts per failing solution; saves figures/error_count_hist.png

def plot_seed_consistency(summary: dict) -> None: ...
# Box plot of type_error_fraction across 3 seeds; saves figures/seed_consistency.png

def generate_all_figures(results: list[dict], summary: dict) -> None: ...
# Calls all plot functions above
```

### Entry Point (`code/run.py`)

**Dependencies**: pipeline, visualize, openai, dotenv, logging

```python
def main() -> None: ...
# 1. load_dotenv() — OPENAI_API_KEY
# 2. verify mypy installed (FileNotFoundError → exit with instructions)
# 3. for each benchmark × seed: run_benchmark() → collect results
# 4. aggregate() → summary
# 5. verify_mechanism_activated() → log indicators
# 6. save_results()
# 7. generate_all_figures()
# 8. log gate evaluation result (PASS/BORDERLINE/FAIL)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Project setup | requirements.txt, .env.example, directory creation, mypy install check | 4 | 1+1+1+1 |
| E2 | Generation module | build_prompt, extract_code, generate_solution with retry/backoff | 8 | 2+2+2+2 |
| E3 | Evaluation + mypy | evaluate_solution (EvalPlus), run_mypy subprocess with timeout | 10 | 3+2+3+2 |
| E4 | Aggregation + persistence | aggregate, verify_mechanism_activated, save_results | 7 | 2+1+2+2 |
| E5 | Figures + entry point | visualize.py (4 figures), run.py orchestration, gate logging | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [E3, E5], Low(4-8): [E1, E2, E4]

---

## Notes

- `evaluate_solution` must handle EvalPlus sandbox execution — check evalplus API for `check_correctness` or equivalent callable before implementing
- Retry logic in `generate_solution`: exponential backoff, max 3 retries, log and skip on persistent failure
- `run_mypy` timeout path returns `(False, 0)` — conservative, avoids false positives
- All paths use `pathlib.Path` and are relative to repo root; `run.py` must be invoked from repo root
