---
title: "Architecture: H-E1 Pylint/Mypy Iterative Repair PoC"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: 3
date: "2026-08-05"
status: complete
---

# Architecture: H-E1

Applied: subprocess-based pylint/mypy integration pattern (cyb3rlab/CodeEnhancer)
Applied: iterative repair loop with token budget (Johin2/iterative-code-repair)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior hypothesis codebase. Patterns sourced from external references (Johin2/iterative-code-repair, cyb3rlab/CodeEnhancer) as documented in Phase 2C.

---

## File Structure

```
experiments/h-e1/
├── run_experiment.py      # Entry point + orchestration
├── data_loader.py         # HumanEval + MBPP loading
├── model_client.py        # Groq API wrapper
├── code_executor.py       # Sandboxed subprocess execution
├── static_analyzer.py     # pylint + mypy subprocess runner
├── repair_loop.py         # Iterative repair logic + token budget
├── evaluator.py           # pass@1 computation + metrics.json
├── visualizer.py          # 4 figures → docs/youra_research/h-e1/figures/
└── requirements.txt

results/
├── baseline_humaneval.jsonl
├── baseline_mbpp.jsonl
├── pylint_humaneval.jsonl
├── pylint_mbpp.jsonl
├── pylint_coverage.jsonl
└── metrics.json

docs/youra_research/h-e1/figures/
├── figure1_pass_at_1_comparison.png
├── figure2_per_round_trajectory.png
├── figure3_token_budget_distribution.png
└── figure4_pylint_coverage_analysis.png
```

---

## Modules

### DataLoader (`experiments/h-e1/data_loader.py`)

**Dependencies**: evalplus, datasets (HuggingFace)

```python
def load_humaneval() -> dict[str, dict]: ...
# Returns: {task_id: {prompt, canonical_solution, test, entry_point}}
# Source: evalplus.data.get_human_eval_plus() — 164 problems

def load_mbpp() -> dict[str, dict]: ...
# Returns: {task_id: {text, code, test_list, test_setup_code}}
# Source: evalplus.data.get_mbpp_plus() — 374 problems
```

---

### ModelClient (`experiments/h-e1/model_client.py`)

**Dependencies**: groq

```python
class ModelClient:
    def __init__(self, model: str = "llama-3.1-8b-instant", api_key: str = None): ...
    def generate(self, prompt: str, max_tokens: int = 1000) -> tuple[str, int]: ...
    # Returns: (generated_text, tokens_used)
    # Config: temperature=0.0, seed=42
    def count_tokens(self, text: str) -> int: ...
```

---

### CodeExecutor (`experiments/h-e1/code_executor.py`)

**Dependencies**: subprocess, tempfile (stdlib)

```python
def execute_humaneval(code: str, problem: dict, timeout: float = 15.0) -> bool: ...
# Runs problem["test"] in isolated subprocess

def execute_mbpp(code: str, test_list: list[str], timeout: float = 15.0) -> bool: ...
# Executes test_list assertions in namespace with generated code

def extract_code(raw_output: str, entry_point: str = None) -> str: ...
# Strips markdown fences, extracts function body
```

---

### StaticAnalyzer (`experiments/h-e1/static_analyzer.py`)

**Dependencies**: subprocess, tempfile (stdlib)

```python
def run_pylint_mypy(code: str, timeout: float = 30.0) -> str | None: ...
# Returns: formatted feedback string, or None if no issues
# Calls: pylint --output-format=text --score=no {tmp}
# Calls: mypy --ignore-missing-imports {tmp}
# Cleans up temp file in finally block

def get_pylint_categories(code: str) -> dict[str, int]: ...
# Returns: {"error": n, "warning": n, "convention": n, "refactor": n}
# Used for pylint_coverage metric in FR-3
```

---

### RepairLoop (`experiments/h-e1/repair_loop.py`)

**Dependencies**: ModelClient, StaticAnalyzer, CodeExecutor

```python
REPAIR_PROMPT_TEMPLATE = """The following Python code has static analysis issues:
{previous_code}

Static analysis feedback:
{pylint_mypy_output}

Please fix the code to address these issues while maintaining functional correctness.
Return only the corrected function."""

def pylint_repair_loop(
    problem: dict,
    benchmark: str,            # "humaneval" | "mbpp"
    client: ModelClient,
    B: int = 1000,
    max_rounds: int = 3,
    min_remaining: int = 100,
) -> dict: ...
# Returns: {final_code, passed, rounds: [{round, code, passed, tokens, feedback}]}
# Stops if: tokens_used >= B, or remaining < min_remaining, or no pylint issues

def build_initial_prompt(problem: dict, benchmark: str) -> str: ...
def build_repair_prompt(code: str, feedback: str) -> str: ...
```

---

### Evaluator (`experiments/h-e1/evaluator.py`)

**Dependencies**: CodeExecutor, json (stdlib)

```python
def run_baseline(
    problems: dict,
    benchmark: str,
    client: ModelClient,
    output_path: str,
    resume: bool = True,
) -> list[dict]: ...
# Writes baseline_{benchmark}.jsonl incrementally; skips completed task_ids

def run_pylint_condition(
    problems: dict,
    benchmark: str,
    client: ModelClient,
    output_path: str,
    resume: bool = True,
) -> list[dict]: ...
# Writes pylint_{benchmark}.jsonl incrementally

def compute_metrics(
    baseline_he: list[dict],
    baseline_mbpp: list[dict],
    pylint_he: list[dict],
    pylint_mbpp: list[dict],
) -> dict: ...
# Returns metrics.json content:
# {pass@1_baseline_he, pass@1_baseline_mbpp,
#  pass@1_pylint_he, pass@1_pylint_mbpp,
#  delta_pylint_he, delta_pylint_mbpp,
#  per_round_pass@1_he, per_round_pass@1_mbpp,
#  pylint_coverage_fraction, token_budget_distribution}
```

---

### Visualizer (`experiments/h-e1/visualizer.py`)

**Dependencies**: matplotlib, json (stdlib)

```python
def plot_pass_at_1_comparison(metrics: dict, out_dir: str) -> None: ...
# Figure 1: 4-bar chart (baseline/pylint × HE/MBPP)

def plot_per_round_trajectory(pylint_he: list, pylint_mbpp: list, out_dir: str) -> None: ...
# Figure 2: line plot rounds 0-3 for both benchmarks

def plot_token_budget_distribution(pylint_he: list, pylint_mbpp: list, out_dir: str) -> None: ...
# Figure 3: histogram of tokens_used per problem

def plot_pylint_coverage(coverage_data: list, out_dir: str) -> None: ...
# Figure 4: stacked bar (error/warning/convention/not_flagged) for baseline failures

def generate_all_figures(metrics: dict, pylint_he: list, pylint_mbpp: list, out_dir: str) -> None: ...
```

---

### Orchestrator (`experiments/h-e1/run_experiment.py`)

**Dependencies**: All modules above, argparse (stdlib)

```python
def parse_args() -> argparse.Namespace: ...
# --model, --backend, --token-budget, --max-repair-rounds, --seed, --output-dir

def main() -> None: ...
# 1. Load HumanEval + MBPP
# 2. Init ModelClient
# 3. run_baseline() for both benchmarks (with resume)
# 4. run_pylint_condition() for both benchmarks (with resume)
# 5. compute_metrics() → results/metrics.json + results/summary.md
# 6. generate_all_figures() → docs/youra_research/h-e1/figures/
# 7. Print final Δ_pylint values
```

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| E-1 | Data & Model Setup | Implement data_loader.py (HumanEval + MBPP via evalplus) and model_client.py (Groq API, greedy, token counting) | data_loader.py, model_client.py, requirements.txt | 8/20 (Medium) | Size=2 + Deps=2 + Algo=2 + Integ=2 |
| E-2 | Code Execution Sandbox | Implement code_executor.py: sandboxed subprocess execution (15s timeout), code extraction from LLM output (strip markdown, handle fences) | code_executor.py | 10/20 (Medium) | Size=2 + Deps=2 + Algo=3 + Integ=3 |
| E-3 | Static Analyzer | Implement static_analyzer.py: pylint + mypy subprocess calls (30s timeout), feedback formatting, category counting for coverage metric | static_analyzer.py | 9/20 (Medium) | Size=2 + Deps=2 + Algo=3 + Integ=2 |
| E-4 | Repair Loop | Implement repair_loop.py: token budget tracking, max_rounds guard, min_remaining guard, per-round result logging, prompt templates | repair_loop.py | 13/20 (High) | Size=3 + Deps=3 + Algo=4 + Integ=3 |
| E-5 | Evaluator + Results | Implement evaluator.py: baseline and pylint condition runners with incremental JSONL writes (resume support), compute_metrics(), summary.md | evaluator.py | 14/20 (High) | Size=3 + Deps=4 + Algo=3 + Integ=4 |
| E-6 | Visualization + Orchestration | Implement visualizer.py (4 figures) and run_experiment.py (argparse CLI, end-to-end orchestration) | visualizer.py, run_experiment.py | 12/20 (High) | Size=3 + Deps=3 + Algo=3 + Integ=3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [E-5], Medium(9-13): [E-2, E-3, E-4, E-6], Low(4-8): [E-1]

---

## Module Dependency Graph

- `run_experiment.py` → all modules
- `evaluator.py` → `repair_loop.py`, `code_executor.py`, `model_client.py`
- `repair_loop.py` → `static_analyzer.py`, `model_client.py`, `code_executor.py`
- `visualizer.py` → stdlib only (matplotlib)
- `data_loader.py` → evalplus only
- `static_analyzer.py` → subprocess/tempfile (stdlib)
- `code_executor.py` → subprocess/tempfile (stdlib)

---

## Key Constraints (Implementation Notes)

- **Resume support**: All JSONL writers check existing task_ids before writing; skip completed problems
- **Token budget guard**: Skip repair round if remaining < 100 tokens (NFR-3)
- **Pylint failure gate**: If pylint crashes ≥50% of problems → log error and surface for pivot decision
- **All 538 problems required**: No subset shortcuts — PoC validity requires full HumanEval (164) + MBPP (374)
- **Seed**: 42 fixed throughout; Groq greedy = temperature=0.0
- **Figures output**: `docs/youra_research/h-e1/figures/` (relative to repo root, not experiments/)
