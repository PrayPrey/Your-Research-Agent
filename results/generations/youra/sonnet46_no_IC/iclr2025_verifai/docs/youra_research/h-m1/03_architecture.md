---
title: "Architecture: H-M1 Execution Test Feedback Iterative Repair — Mechanism Comparison"
hypothesis_id: h-m1
hypothesis_type: MECHANISM
phase: 3
date: "2026-08-05"
status: complete
---

# Architecture: H-M1

Applied: iterative-repair-loop-with-execution-sandbox (Johin2/iterative-code-repair)
Applied: paired-binary-comparison-McNemar (statsmodels contingency_tables)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 extends to H-M1)
**Status**: H-E1 code found and analyzed at `experiments/h-e1/`
**Analyzed Path**: `experiments/h-e1/`
**Findings**: H-E1 implements ModelClient (groq + HF backends), DataLoader (load_humaneval/load_mbpp), CodeExecutor (extract_code, execute_humaneval, execute_mbpp, _run_in_subprocess), RepairLoop (RoundResult, pylint_repair_loop), Evaluator (run_baseline_condition, run_pylint_condition, compute_metrics), Visualizer (5 plot functions). All reusable with minimal adaptation.

---

## File Structure

```
experiments/h-m1/
├── run_experiment.py          # Entry point + orchestration (new)
├── data_loader.py             # Reuse from H-E1 (copy or symlink)
├── model_client.py            # Reuse from H-E1 + Qwen model support
├── code_executor.py           # Reuse from H-E1 (sandbox + extract_code)
├── execution_repair_loop.py   # NEW: execution feedback repair logic
├── statistical_tests.py       # NEW: McNemar + bootstrap CI
├── evaluator.py               # Extend H-E1: add execution condition runner
├── visualizer.py              # Extend H-E1: add 3 new figures
└── requirements.txt

results/h-m1/
├── execution_humaneval_llama.jsonl
├── execution_mbpp_llama.jsonl
├── execution_humaneval_qwen.jsonl
├── execution_mbpp_qwen.jsonl
├── round_results_humaneval_llama.json   # REQUIRED BY H-M3
├── round_results_mbpp_llama.json        # REQUIRED BY H-M3
├── round_results_humaneval_qwen.json
├── round_results_mbpp_qwen.json
├── mcnemar_humaneval.json
├── mcnemar_mbpp.json
├── mcnemar_qwen_humaneval.json
├── mcnemar_qwen_mbpp.json
└── metrics.json

docs/youra_research/h-m1/figures/
├── figure1_delta_comparison.png
├── figure2_per_round_trajectory.png
├── figure3_replication_comparison.png
├── figure4_token_budget_distribution.png
└── figure5_error_type_analysis.png
```

---

## External Dependencies (H-E1 Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| load_humaneval | `from data_loader import load_humaneval` | `experiments/h-e1/data_loader.py` |
| load_mbpp | `from data_loader import load_mbpp` | `experiments/h-e1/data_loader.py` |
| ModelClient | `from model_client import ModelClient` | `experiments/h-e1/model_client.py` |
| extract_code | `from code_executor import extract_code` | `experiments/h-e1/code_executor.py` |
| execute_humaneval | `from code_executor import execute_humaneval` | `experiments/h-e1/code_executor.py` |
| execute_mbpp | `from code_executor import execute_mbpp` | `experiments/h-e1/code_executor.py` |

**Verified from**: `experiments/h-e1/` (actual implementation via Serena)

**Note on ModelClient**: H-E1 `ModelClient.__init__` takes `model`, `api_key`, `backend` — supports Groq and HF. Qwen model reuses same class with `model="Qwen/Qwen2.5-Coder-7B-Instruct"` and `backend="hf"`.

---

## Modules

### DataLoader (`experiments/h-m1/data_loader.py`)

**Dependencies**: evalplus (pip)
**Action**: Copy from H-E1 unchanged.

```python
def load_humaneval() -> dict[str, dict]: ...
# Returns: {task_id: {prompt, canonical_solution, test, entry_point}} — 164 problems

def load_mbpp() -> dict[str, dict]: ...
# Returns: {task_id: {text, code, test_list, test_setup_code}} — 374 problems
```

---

### ModelClient (`experiments/h-m1/model_client.py`)

**Dependencies**: groq, transformers, torch
**Action**: Copy from H-E1 unchanged. Qwen model uses existing `backend="hf"` path.

```python
class ModelClient:
    def __init__(self, model: str, api_key: str = None, backend: str = "groq"): ...
    # backend: "groq" | "hf"
    # Verified: H-E1 model_client.py lines 7-21

    def generate(self, prompt: str, max_tokens: int = 1000) -> tuple[str, int]: ...
    # Returns: (generated_text, tokens_used); temperature=0.0, seed=42

    def count_tokens(self, text: str) -> int: ...
```

---

### CodeExecutor (`experiments/h-m1/code_executor.py`)

**Dependencies**: subprocess, tempfile (stdlib)
**Action**: Copy from H-E1 unchanged. `_run_in_subprocess` is the sandbox used by execution_repair_loop.

```python
def extract_code(raw_output: str, entry_point: str = None) -> str: ...
# Strips markdown fences, extracts function body

def execute_humaneval(code: str, problem: dict, timeout: float = 15.0) -> bool: ...
# Runs problem["test"] in isolated subprocess (python -I)

def execute_mbpp(code: str, test_list: list[str], timeout: float = 15.0) -> bool: ...
# Executes test_list assertions

def run_in_sandbox(code: str, test_code: str, timeout: float = 15.0) -> dict: ...
# NEW wrapper for execution_repair_loop:
# Returns: {passed: bool, error: str | None, returncode: int}
# Combines code + test_code, runs in subprocess, captures stderr
```

---

### ExecutionRepairLoop (`experiments/h-m1/execution_repair_loop.py`)

**Dependencies**: ModelClient, CodeExecutor
**Action**: NEW module — core of H-M1.

```python
EXECUTION_REPAIR_PROMPT = (
    "The following Python function has a bug:\n\n{prompt}\n\n"
    "Your previous attempt:\n```python\n{code}\n```\n\n"
    "Execution error:\n{error}\n\n"
    "Please fix the function. Return only the corrected Python function."
)

def execution_repair_loop(
    problem: dict,
    benchmark: str,           # "humaneval" | "mbpp"
    client: ModelClient,
    B: int = 1000,
    max_rounds: int = 3,
    min_remaining: int = 50,
) -> dict: ...
# Returns: {
#   final_code: str, passed: bool, tokens_used: int,
#   rounds: [{round: int, code: str, passed: bool,
#             feedback_type: str | None, error_snippet: str | None}]
# }
# Round 0: generate from prompt; rounds 1-3: repair with execution error
# Stops if: tests pass, tokens_used >= B, remaining < min_remaining, round > max_rounds

def verify_mechanism(
    problems: dict,
    benchmark: str,
    client: ModelClient,
    n: int = 20,
) -> None: ...
# Pilot check: assert feedback applied in >20% of n problems
# Raises AssertionError if mechanism not active
```

---

### StatisticalTests (`experiments/h-m1/statistical_tests.py`)

**Dependencies**: statsmodels, scipy, numpy
**Action**: NEW module.

```python
def run_mcnemar_test(
    pylint_results: dict[str, dict],    # {task_id: {passed: bool}}
    execution_results: dict[str, dict], # {task_id: {passed: bool}}
    task_ids: list[str],
) -> dict: ...
# Returns: {table, n_discordant, exec_only, pylint_only,
#           statistic, pvalue, exact, significant, direction}
# exact=True if n_discordant < 25 (binomial), else chi-square

def bootstrap_ci_delta_diff(
    pylint_pass: np.ndarray,     # bool array, length N
    exec_pass: np.ndarray,       # bool array, length N
    baseline_pass: np.ndarray,   # bool array, length N
    n_bootstrap: int = 10000,
) -> tuple[float, float]: ...
# Returns: (ci_lower, ci_upper) — 95% CI on (Δ_execution - Δ_pylint)

def compute_gate_result(
    mcnemar_he: dict,
    mcnemar_mbpp: dict,
) -> dict: ...
# Returns: {gate_passed: bool, reason: str}
# gate_passed: both p<0.05 AND exec_only > pylint_only on BOTH benchmarks
```

---

### Evaluator (`experiments/h-m1/evaluator.py`)

**Dependencies**: ModelClient, ExecutionRepairLoop, CodeExecutor, json (stdlib)
**Action**: Extend H-E1 evaluator — add execution condition runner, extend compute_metrics.

```python
def load_h_e1_results(
    h_e1_results_dir: str,
) -> tuple[list[dict], list[dict], list[dict], list[dict]]: ...
# Returns: (baseline_he, baseline_mbpp, pylint_he, pylint_mbpp)
# Reads from h-e1 results jsonl files

def run_execution_condition(
    problems: dict,
    benchmark: str,           # "humaneval" | "mbpp"
    client: ModelClient,
    output_path: str,
    resume: bool = True,
    B: int = 1000,
    max_rounds: int = 3,
) -> list[dict]: ...
# Writes execution_{benchmark}_{model_tag}.jsonl incrementally (resume by task_id)
# Each record: {task_id, rounds, tokens_used, final_passed}

def extract_round_results(
    results: list[dict],
    max_rounds: int = 3,
) -> dict[str, dict]: ...
# Returns: {task_id: {round_0: bool, round_1: bool, round_2: bool, round_3: bool}}
# CRITICAL: this dict is saved as round_results_*.json for H-M3

def compute_metrics(
    baseline_he: list[dict],
    baseline_mbpp: list[dict],
    pylint_he: list[dict],
    pylint_mbpp: list[dict],
    exec_he_llama: list[dict],
    exec_mbpp_llama: list[dict],
    exec_he_qwen: list[dict],
    exec_mbpp_qwen: list[dict],
    mcnemar_he: dict,
    mcnemar_mbpp: dict,
    mcnemar_qwen_he: dict,
    mcnemar_qwen_mbpp: dict,
) -> dict: ...
# Returns metrics.json content with all delta, pass@1, McNemar, CI, gate fields
```

---

### Visualizer (`experiments/h-m1/visualizer.py`)

**Dependencies**: matplotlib, json (stdlib)
**Action**: Extend H-E1 visualizer — add 3 new figures, keep existing 2.

```python
FIGURE_RC: dict  # shared matplotlib rcParams

def plot_delta_comparison(metrics: dict, out_dir: str) -> None: ...
# Figure 1 (MANDATORY): 4-bar chart Δ_exec/Δ_pylint × HE/MBPP; CI error bars; McNemar p annotation

def plot_per_round_trajectory(
    exec_he: list[dict],
    exec_mbpp: list[dict],
    pylint_he: list[dict],
    pylint_mbpp: list[dict],
    out_dir: str,
) -> None: ...
# Figure 2 (MANDATORY): line plot rounds 0-3 exec vs pylint on both benchmarks

def plot_replication_comparison(metrics: dict, out_dir: str) -> None: ...
# Figure 3: side-by-side Δ for Llama vs Qwen on both benchmarks

def plot_token_budget_distribution(
    exec_he: list[dict],
    exec_mbpp: list[dict],
    out_dir: str,
) -> None: ...
# Figure 4: histogram of tokens_used per problem in execution condition

def plot_error_type_analysis(
    exec_he: list[dict],
    exec_mbpp: list[dict],
    out_dir: str,
) -> None: ...
# Figure 5: bar chart of error_type distribution + repair success rate by error type

def generate_all_figures(
    metrics: dict,
    exec_he_llama: list[dict],
    exec_mbpp_llama: list[dict],
    pylint_he: list[dict],
    pylint_mbpp: list[dict],
    out_dir: str,
) -> None: ...
```

---

### Orchestrator (`experiments/h-m1/run_experiment.py`)

**Dependencies**: All modules above, argparse (stdlib)

```python
def parse_args() -> argparse.Namespace: ...
# --model (llama-3.1-8b-instant | Qwen/Qwen2.5-Coder-7B-Instruct)
# --backend (groq | hf)
# --token-budget (default 1000)
# --max-repair-rounds (default 3)
# --seed (default 42)
# --reuse-h-e1-results (flag)
# --h-e1-results-dir (default docs/youra_research/h-e1/results/)
# --output-dir (default results/h-m1/)
# --run-replication (flag — also run Qwen)
# --pilot-only (flag — run verify_mechanism on 20 problems then exit)

def main() -> None: ...
# 1. Load HumanEval + MBPP via data_loader
# 2. Init ModelClient (Llama)
# 3. Load H-E1 results (baseline + pylint) or re-run fallback
# 4. verify_mechanism() pilot check (20 problems)
# 5. run_execution_condition() Llama HE + MBPP (with resume)
# 6. extract_round_results() → save round_results_*.json (H-M3 data)
# 7. If --run-replication: init Qwen ModelClient, run_execution_condition() Qwen
# 8. run_mcnemar_test() × 4 (HE/MBPP × Llama/Qwen) → save mcnemar_*.json
# 9. compute_metrics() → save metrics.json + summary.md
# 10. generate_all_figures() → docs/youra_research/h-m1/figures/
# 11. Print gate result (PASS / FAIL / EXPLORE routing)
```

---

## Module Dependency Graph

- `run_experiment.py` → all modules
- `evaluator.py` → `execution_repair_loop.py`, `code_executor.py`, `model_client.py`, `statistical_tests.py`
- `execution_repair_loop.py` → `model_client.py`, `code_executor.py`
- `statistical_tests.py` → statsmodels, scipy, numpy
- `visualizer.py` → matplotlib (stdlib-only otherwise)
- `data_loader.py` → evalplus
- `code_executor.py` → subprocess, tempfile (stdlib)
- `model_client.py` → groq, transformers

---

## Epic Tasks

| ID | Task | Description | Files | Complexity | Breakdown |
|----|------|-------------|-------|------------|-----------|
| M-1 | Project Setup + H-E1 Reuse | Copy data_loader.py, model_client.py, code_executor.py from H-E1. Add run_in_sandbox() to code_executor. Pin requirements.txt with statsmodels/scipy additions. | data_loader.py, model_client.py, code_executor.py, requirements.txt | 7 | Size=2+Deps=2+Algo=1+Integ=2 |
| M-2 | Execution Repair Loop | Implement execution_repair_loop.py: round 0 generate, sandbox execute, error format, repair prompt, budget tracking, per-round logging. Includes verify_mechanism() pilot check. | execution_repair_loop.py | 14 | Size=3+Deps=3+Algo=5+Integ=3 |
| M-3 | Execution Condition Runner (Llama) | Implement run_execution_condition() in evaluator.py: incremental JSONL write with resume, per-problem tqdm progress, task_id deduplication. Run on HumanEval (164) + MBPP (374). | evaluator.py (partial) | 12 | Size=3+Deps=3+Algo=3+Integ=3 |
| M-4 | Round Results Export (H-M3 data) | Implement extract_round_results() → round_results_*.json. Schema: {task_id: {round_0..3: bool}}. Validate all task_ids present before saving. | evaluator.py (partial) | 8 | Size=2+Deps=2+Algo=2+Integ=2 |
| M-5 | Replication Model (Qwen) | Run same execution condition with Qwen2.5-Coder-7B-Instruct via ModelClient(backend="hf"). Save execution_*_qwen.jsonl and round_results_*_qwen.json. | evaluator.py (partial), run_experiment.py | 10 | Size=2+Deps=3+Algo=2+Integ=3 |
| M-6 | Statistical Tests Module | Implement statistical_tests.py: McNemar (exact if discordant<25 else chi-sq), bootstrap_ci_delta_diff (10k resamples), compute_gate_result. | statistical_tests.py | 13 | Size=3+Deps=3+Algo=4+Integ=3 |
| M-7 | Metric Computation + Summary | Implement compute_metrics() aggregating all pass@1, deltas, CIs, McNemar results into metrics.json. Generate summary.md with gate verdict. | evaluator.py (partial) | 11 | Size=3+Deps=3+Algo=3+Integ=2 |
| M-8 | Visualization (5 figures) | Implement visualizer.py extending H-E1: figure1 delta bar+CI+p-value, figure2 per-round trajectory, figure3 replication, figure4 token histogram, figure5 error-type analysis. | visualizer.py | 13 | Size=3+Deps=2+Algo=4+Integ=4 |
| M-9 | Orchestrator + CLI | Implement run_experiment.py: argparse CLI, end-to-end flow with --reuse-h-e1-results, --run-replication, --pilot-only flags, resume detection, gate result print. | run_experiment.py | 12 | Size=3+Deps=4+Algo=2+Integ=3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-2], Medium(9-13): [M-3, M-5, M-6, M-7, M-8, M-9], Low(4-8): [M-1, M-4]

---

## Key Constraints (Implementation Notes)

- **H-E1 result paths**: `docs/youra_research/h-e1/results/{baseline,pylint}_{humaneval,mbpp}.jsonl` — load via `load_h_e1_results()`; if missing, re-run H-E1 protocol as fallback
- **round_results_*.json schema**: `{task_id: {round_0: bool, round_1: bool | null, round_2: bool | null, round_3: bool | null}}` — null if round not reached; H-M3 consumes this
- **Token budget guard**: `remaining = B - tokens_used; if remaining < 50: break` in repair loop
- **Sandbox**: `python -I {tmp}.py` with 15s timeout; cleanup in finally; never exec() in main process
- **McNemar exact vs. approx**: `exact = (n_discordant < 25)` — auto-selected; both cases handled
- **Resume detection**: check existing task_ids in output JSONL before starting each condition
- **Qwen via HF**: `ModelClient(model="Qwen/Qwen2.5-Coder-7B-Instruct", backend="hf")` — reuses H-E1 `_load_hf_direct` / `_generate_hf` path
- **Figures output**: `docs/youra_research/h-m1/figures/` (absolute from repo root)
- **Gate logic**: `gate_passed = mcnemar_he["pvalue"] < 0.05 AND mcnemar_mbpp["pvalue"] < 0.05 AND mcnemar_he["exec_only"] > mcnemar_he["pylint_only"] AND mcnemar_mbpp["exec_only"] > mcnemar_mbpp["pylint_only"]`
