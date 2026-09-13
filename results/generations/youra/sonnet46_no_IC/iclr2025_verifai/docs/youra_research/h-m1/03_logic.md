---
title: "Logic: H-M1 Execution Test Feedback Iterative Repair"
hypothesis_id: h-m1
phase: 3
date: "2026-08-05"
status: complete
---

# Logic: H-M1

Applied: iterative-repair-loop-with-execution-sandbox

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: API signatures verified from actual H-E1 code at `experiments/h-e1/`
**Analyzed Path**: `experiments/h-e1/`
**Relevant Symbols**:
- `ModelClient.__init__(model, api_key, backend="auto")` — backend auto-detects groq vs hf
- `ModelClient.generate(prompt, max_tokens) -> tuple[str, int]` — returns (text, tokens_used)
- `ModelClient.count_tokens(text) -> int` — approx len//4
- `extract_code(raw_output, entry_point=None) -> str`
- `execute_humaneval(code, problem, timeout=15.0) -> bool`
- `execute_mbpp(code, problem, timeout=15.0) -> bool`
- `_run_in_subprocess(code, timeout) -> bool` — does NOT capture stderr
- `pylint_repair_loop(problem, benchmark, client, executor_fn, analyzer, B, max_rounds, min_remaining) -> dict`
- `run_baseline_condition(problems, benchmark, client, output_path, resume) -> list[dict]`
- `run_pylint_condition(problems, benchmark, client, analyzer, output_path, B, max_rounds, resume) -> list[dict]`
- `compute_metrics(baseline_he, baseline_mbpp, pylint_he, pylint_mbpp) -> dict`

**Critical Notes**:
- H-E1 `_run_in_subprocess` returns `bool` only — H-M1 needs stderr capture, so `run_in_sandbox` is a NEW wrapper
- H-E1 `execute_mbpp` uses `problem["assertion"]` field (evalplus format), not `test_list`
- H-E1 `ModelClient` backend param is `"auto"` default (not `"groq"`), auto-detects from GROQ_API_KEY
- H-E1 round_results use key `"round_num"` (not `"round"`) and `"tokens_generated"` (not `"tokens_used"`)

---

## External Dependencies API (Base Hypothesis)

Signatures verified from `experiments/h-e1/` actual code:

```python
# experiments/h-e1/model_client.py
class ModelClient:
    def __init__(
        self,
        model: str = "llama-3.1-8b-instant",
        api_key: str | None = None,
        backend: str = "auto",  # "auto" | "groq" | "hf" — NOT "groq" default!
    ): ...

    def generate(self, prompt: str, max_tokens: int = 1000) -> tuple[str, int]:
        """Returns (generated_text, tokens_used).""" ...

    def count_tokens(self, text: str) -> int: ...  # approx len(text) // 4

# experiments/h-e1/code_executor.py
def extract_code(raw_output: str, entry_point: str | None = None) -> str: ...
def execute_humaneval(code: str, problem: dict, timeout: float = 15.0) -> bool: ...
def execute_mbpp(code: str, problem: dict, timeout: float = 15.0) -> bool: ...
# NOTE: _run_in_subprocess returns bool, NOT dict — no stderr capture

# experiments/h-e1/evaluator.py
def run_baseline_condition(
    problems: dict,
    benchmark: str,
    client,           # ModelClient
    output_path: str,
    resume: bool = True,
) -> list[dict]: ...

def run_pylint_condition(
    problems: dict,
    benchmark: str,
    client,
    analyzer,         # StaticAnalyzer
    output_path: str,
    B: int = 1000,
    max_rounds: int = 3,
    resume: bool = True,
) -> list[dict]: ...

def compute_metrics(
    baseline_he: list[dict],
    baseline_mbpp: list[dict],
    pylint_he: list[dict],
    pylint_mbpp: list[dict],
) -> dict: ...

# H-E1 round result dict keys (CRITICAL — differ from PRD pseudo-code):
# {"round_num": int, "code": str, "tokens_generated": int, "passed": bool, "feedback_given": str|None}
```

**Verified from**: `experiments/h-e1/` actual implementation.

---

## Data Contracts

### `execution_*.jsonl` (one JSON object per line)
```python
{
    "task_id": str,              # e.g. "HumanEval/0"
    "condition": "execution",
    "benchmark": str,            # "humaneval" | "mbpp"
    "passed": bool,              # final_passed
    "tokens_used": int,
    "rounds": [                  # list, len = rounds_completed + 1
        {
            "round_num": int,           # 0, 1, 2, 3
            "code": str,
            "tokens_generated": int,
            "passed": bool,
            "feedback_type": str | None,     # None for round 0, "execution" for repairs
            "error_snippet": str | None,     # first 200 chars of stderr, None if passed
            "error_type": str | None,        # e.g. "AssertionError", "NameError", None if passed
        }
    ],
}
```

### `round_results_*.json` (required by H-M3)
```python
{
    "HumanEval/0": {
        "round_0": bool,
        "round_1": bool | None,   # None if round not reached
        "round_2": bool | None,
        "round_3": bool | None,
    },
    ...
}
```

### `mcnemar_*.json`
```python
{
    "table": [[int, int], [int, int]],   # [[both_pass, pylint_only], [exec_only, both_fail]]
    "n_discordant": int,                  # pylint_only + exec_only
    "exec_only": int,                     # c: exec passes, pylint fails
    "pylint_only": int,                   # b: pylint passes, exec fails
    "statistic": float,
    "pvalue": float,
    "exact": bool,                        # True if n_discordant < 25
    "significant": bool,                  # pvalue < 0.05
    "direction": str,                     # "execution > pylint" | "pylint >= execution"
    "ci_lower": float,                    # 95% CI lower on (Δ_exec - Δ_pylint)
    "ci_upper": float,                    # 95% CI upper
}
```

### `metrics.json`
```python
{
    # Primary
    "pass_at_1_baseline_humaneval": float,
    "pass_at_1_baseline_mbpp": float,
    "pass_at_1_pylint_humaneval": float,
    "pass_at_1_pylint_mbpp": float,
    "pass_at_1_execution_humaneval_llama": float,
    "pass_at_1_execution_mbpp_llama": float,
    "pass_at_1_execution_humaneval_qwen": float,
    "pass_at_1_execution_mbpp_qwen": float,
    "delta_pylint_humaneval": float,
    "delta_pylint_mbpp": float,
    "delta_execution_humaneval_llama": float,
    "delta_execution_mbpp_llama": float,
    "delta_execution_humaneval_qwen": float,
    "delta_execution_mbpp_qwen": float,
    "delta_diff_humaneval": float,        # Δ_exec_llama - Δ_pylint
    "delta_diff_mbpp": float,
    # McNemar
    "mcnemar_p_humaneval": float,
    "mcnemar_p_mbpp": float,
    "mcnemar_p_qwen_humaneval": float,
    "mcnemar_p_qwen_mbpp": float,
    # Gate
    "gate_passed": bool,
    "gate_reason": str,
    # Per-round (H-M3)
    "per_round_pass_at_1_execution_humaneval": {0: float, 1: float, 2: float, 3: float},
    "per_round_pass_at_1_execution_mbpp": {0: float, 1: float, 2: float, 3: float},
    # Secondary
    "n_humaneval": int,
    "n_mbpp": int,
    "completion_rate_execution_he": float,
    "completion_rate_execution_mbpp": float,
    "token_budget_distribution_humaneval": list[int],
    "token_budget_distribution_mbpp": list[int],
}
```

---

## M-2: Execution Repair Loop [Complexity: 14, Budget: 4 subtasks]

Applied: iterative-repair-loop-with-execution-sandbox

### API Signatures

```python
# experiments/h-m1/code_executor.py  (NEW function added to H-E1 copy)
def run_in_sandbox(
    code: str,
    test_code: str,
    timeout: float = 15.0,
) -> dict:
    """Run code+test in subprocess, capture stderr. Returns {passed, error, returncode}."""
    # {passed: bool, error: str | None, returncode: int}
    ...


# experiments/h-m1/execution_repair_loop.py  (NEW module)
EXECUTION_REPAIR_PROMPT = (
    "The following Python function has a bug:\n\n{prompt}\n\n"
    "Your previous attempt:\n```python\n{code}\n```\n\n"
    "Execution error:\n{error}\n\n"
    "Please fix the function. Return only the corrected Python function."
)


def _extract_error_type(error: str | None) -> str | None:
    """Parse first exception class name from stderr. e.g. 'AssertionError'."""
    ...


def _get_test_code(problem: dict, benchmark: str) -> str:
    """Extract test string from problem dict for sandbox."""
    # humaneval: build "check(entry_point)" block from problem["test"]
    # mbpp: use problem["assertion"] or join problem.get("test_list", [])
    ...


def format_execution_feedback(exec_result: dict, problem: dict) -> str:
    """Format sandbox error for repair prompt.
    exec_result: {passed, error, returncode}; returns error string (max 500 chars).
    """
    ...


def run_unit_tests_in_sandbox(
    code: str,
    test_code: str,
    timeout: int = 15,
) -> dict:
    """Thin alias over run_in_sandbox for interface consistency.
    Returns: {passed: bool, error: str | None, returncode: int}
    """
    ...


def execution_repair_loop(
    problem: dict,
    benchmark: str,          # "humaneval" | "mbpp"
    client,                  # ModelClient
    B: int = 1000,
    max_rounds: int = 3,
    min_remaining: int = 50,
) -> dict:
    """Iterative execution feedback repair within token budget B.

    Returns dict matching execution_*.jsonl schema (minus task_id/benchmark/condition).
    """
    ...


def verify_mechanism(
    problems: dict,          # {task_id: problem_dict}
    benchmark: str,
    client,                  # ModelClient
    n: int = 20,
) -> None:
    """Pilot check: assert feedback applied in >20% of n problems. Raises AssertionError."""
    ...
```

### Pseudo-code: `execution_repair_loop`

```
1. test_code = _get_test_code(problem, benchmark)
2. prompt = build_initial_prompt(problem, benchmark)  # reuse H-E1 helper
3. raw, tokens = client.generate(prompt, max_tokens=min(512, B))
4. code = extract_code(raw, problem.get("entry_point"))
5. tokens_used = tokens
6. exec_result = run_in_sandbox(code, test_code)
7. rounds = [{"round_num": 0, "code": code, "tokens_generated": tokens,
              "passed": exec_result["passed"], "feedback_type": None,
              "error_snippet": None, "error_type": None}]

8. for repair_round in range(1, max_rounds + 1):
     if exec_result["passed"]: break
     remaining = B - tokens_used
     if remaining < min_remaining: break
     error_msg = format_execution_feedback(exec_result, problem)
     repair_prompt = EXECUTION_REPAIR_PROMPT.format(
         prompt=problem.get("prompt", problem.get("text", "")),
         code=code, error=error_msg)
     raw, tokens = client.generate(repair_prompt, max_tokens=min(512, remaining))
     code = extract_code(raw, problem.get("entry_point"))
     tokens_used += tokens
     exec_result = run_in_sandbox(code, test_code)
     rounds.append({"round_num": repair_round, "code": code,
                    "tokens_generated": tokens, "passed": exec_result["passed"],
                    "feedback_type": "execution",
                    "error_snippet": (exec_result["error"] or "")[:200] or None,
                    "error_type": _extract_error_type(exec_result["error"])})

9. return {"passed": exec_result["passed"], "tokens_used": tokens_used, "rounds": rounds}
```

### Pseudo-code: `run_in_sandbox`

```
1. combined = code + "\n\n" + test_code
2. write combined to NamedTemporaryFile(suffix=".py")
3. try:
     result = subprocess.run([sys.executable, "-I", tmp_path],
                             capture_output=True, text=True, timeout=timeout)
     error = result.stderr.strip() or result.stdout.strip() if result.returncode != 0 else None
     return {"passed": result.returncode == 0, "error": error, "returncode": result.returncode}
   except TimeoutExpired:
     return {"passed": False, "error": "TimeoutError: exceeded 15s", "returncode": -1}
   finally:
     os.unlink(tmp_path)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | run_unit_tests_in_sandbox | Subprocess wrapper with stderr capture; cleanup in finally |
| L-2-2 | format_execution_feedback | Truncate error to 500 chars; extract error type for logging |
| L-2-3 | execution_repair_loop | Main loop with budget guard, round logging, early exit on pass |
| L-2-4 | verify_mechanism | Pilot 20 problems, assert >20% got repair round, print summary |

---

## M-3: Execution Condition Runner [Complexity: 12, Budget: 2 subtasks]

Applied: Standard Python JSONL incremental write with resume (mirrors H-E1 run_pylint_condition pattern)

### API Signatures

```python
# experiments/h-m1/evaluator.py  (new functions added)

def run_execution_condition(
    problems: dict,            # {task_id: problem_dict}
    benchmark: str,            # "humaneval" | "mbpp"
    client,                    # ModelClient
    output_path: str,          # directory path
    resume: bool = True,
    B: int = 1000,
    max_rounds: int = 3,
) -> list[dict]:
    """Run execution repair on all problems, write JSONL incrementally.

    Output file: {output_path}/execution_{benchmark}_{model_tag}.jsonl
    Returns list of result dicts matching execution_*.jsonl schema.
    """
    ...


def load_condition_results(jsonl_path: str) -> dict[str, dict]:
    """Load JSONL result file, index by task_id.

    Returns: {task_id: result_dict}
    """
    ...


def load_h_e1_results(h_e1_results_dir: str) -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    """Load H-E1 baseline + pylint results.

    Returns: (baseline_he, baseline_mbpp, pylint_he, pylint_mbpp)
    """
    ...


def extract_round_results(
    results: list[dict],
    max_rounds: int = 3,
) -> dict[str, dict]:
    """Convert execution results to round_results_*.json format for H-M3.

    Returns: {task_id: {round_0: bool, round_1: bool|None, ...}}
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | run_execution_condition | JSONL incremental write; resume via completed_ids set; tqdm progress; model_tag from client.model |
| L-3-2 | load_condition_results | JSONL reader indexed by task_id; skip malformed lines |

---

## M-6: Statistical Tests [Complexity: 13, Budget: 2 subtasks]

Applied: McNemar paired-binary-comparison (statsmodels contingency_tables)

### API Signatures

```python
# experiments/h-m1/statistical_tests.py

import numpy as np
from statsmodels.stats.contingency_tables import mcnemar as statsmodels_mcnemar


def run_mcnemar_test(
    pylint_results: dict[str, dict],     # {task_id: {"passed": bool, ...}}
    execution_results: dict[str, dict],  # {task_id: {"passed": bool, ...}}
    task_ids: list[str],                 # intersection of available task_ids
) -> dict:
    """McNemar test on paired (pylint_pass, exec_pass) outcomes.

    Returns full mcnemar_*.json schema dict (without CI — CI added by caller).
    """
    ...


def bootstrap_ci_delta_diff(
    baseline_pass: np.ndarray,   # bool array [N]
    pylint_pass: np.ndarray,     # bool array [N]
    exec_pass: np.ndarray,       # bool array [N]
    n_bootstrap: int = 10000,
) -> tuple[float, float]:
    """95% CI on (Δ_execution - Δ_pylint) via percentile bootstrap.

    Returns: (ci_lower, ci_upper)
    """
    ...


def compute_gate_result(
    mcnemar_he: dict,    # output of run_mcnemar_test for HumanEval
    mcnemar_mbpp: dict,  # output of run_mcnemar_test for MBPP
) -> dict:
    """Evaluate MUST_WORK gate.

    Returns: {"gate_passed": bool, "gate_reason": str}
    """
    ...
```

### Pseudo-code: `run_mcnemar_test`

```
1. both_pass = pylint_only = exec_only = both_fail = 0
2. for task_id in task_ids:
     p = pylint_results[task_id]["passed"]
     e = execution_results[task_id]["passed"]
     increment appropriate counter
3. table = np.array([[both_pass, pylint_only], [exec_only, both_fail]])
4. n_discordant = pylint_only + exec_only
5. exact = (n_discordant < 25)
6. result = statsmodels_mcnemar(table, exact=exact, correction=not exact)
7. return {
     "table": table.tolist(), "n_discordant": n_discordant,
     "exec_only": exec_only, "pylint_only": pylint_only,
     "statistic": result.statistic, "pvalue": float(result.pvalue),
     "exact": exact, "significant": result.pvalue < 0.05,
     "direction": "execution > pylint" if exec_only > pylint_only else "pylint >= execution"
   }
```

### Pseudo-code: `bootstrap_ci_delta_diff`

```
1. n = len(baseline_pass)
2. diffs = []
3. for _ in range(n_bootstrap):
     idx = np.random.default_rng(seed=None).choice(n, n, replace=True)
     d_exec = exec_pass[idx].mean() - baseline_pass[idx].mean()
     d_pylint = pylint_pass[idx].mean() - baseline_pass[idx].mean()
     diffs.append(d_exec - d_pylint)
4. return tuple(np.percentile(diffs, [2.5, 97.5]))
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_mcnemar_test | Contingency table + statsmodels call; exact vs chi-sq auto-select |
| L-6-2 | bootstrap_ci_delta_diff | 10k resamples; percentile CI; no scipy dependency needed |

---

## M-9: Orchestrator [Complexity: 12, Budget: 2 subtasks]

Applied: Standard Python argparse orchestration (mirrors H-E1 run_experiment.py pattern)

### API Signatures

```python
# experiments/h-m1/run_experiment.py

import argparse


def parse_args() -> argparse.Namespace:
    """CLI argument parser.

    Flags:
      --model STR             default: "llama-3.1-8b-instant"
      --backend STR           default: "auto"
      --token-budget INT      default: 1000
      --max-repair-rounds INT default: 3
      --seed INT              default: 42
      --reuse-h-e1-results    store_true
      --h-e1-results-dir STR  default: "docs/youra_research/h-e1/results/"
      --output-dir STR        default: "results/h-m1/"
      --run-replication       store_true  (run Qwen)
      --pilot-only            store_true  (run verify_mechanism then exit)
    """
    ...


def detect_resume_state(output_dir: str) -> dict:
    """Check existing output files to determine what still needs running.

    Returns: {
        "llama_he_done": bool,
        "llama_mbpp_done": bool,
        "qwen_he_done": bool,
        "qwen_mbpp_done": bool,
        "llama_he_path": str,       # JSONL path
        "llama_mbpp_path": str,
        "qwen_he_path": str,
        "qwen_mbpp_path": str,
        "round_results_done": bool,
        "mcnemar_done": bool,
        "metrics_done": bool,
    }
    """
    ...


def print_gate_result(metrics: dict) -> None:
    """Print MUST_WORK gate verdict to stdout.

    Format:
    ============================================================
    GATE RESULT: PASS | FAIL | EXPLORE
    McNemar HumanEval: p={:.4f} ({significant})
    McNemar MBPP: p={:.4f} ({significant})
    Δ_exec_HE={:+.4f}  Δ_pylint_HE={:+.4f}
    Δ_exec_MBPP={:+.4f}  Δ_pylint_MBPP={:+.4f}
    Routing: PASS→H-M2 | FAIL→investigate | EXPLORE→pylint-parity finding
    ============================================================
    """
    ...


def main() -> None:
    """End-to-end experiment orchestration."""
    ...
```

### Pseudo-code: `main`

```
1. args = parse_args()
2. np.random.seed(args.seed)
3. problems_he = load_humaneval(); problems_mbpp = load_mbpp()
4. client = ModelClient(model=args.model, backend=args.backend)
5. if args.reuse_h_e1_results:
     baseline_he, baseline_mbpp, pylint_he, pylint_mbpp = load_h_e1_results(args.h_e1_results_dir)
   else:
     run H-E1 fallback protocol
6. state = detect_resume_state(args.output_dir)
7. if args.pilot_only:
     verify_mechanism(problems_he, "humaneval", client, n=20); exit(0)
8. run_execution_condition(problems_he, "humaneval", client, args.output_dir, ...)
9. run_execution_condition(problems_mbpp, "mbpp", client, args.output_dir, ...)
10. extract_round_results → save round_results_humaneval_llama.json + mbpp version
11. if args.run_replication:
      qwen_client = ModelClient(model="Qwen/Qwen2.5-Coder-7B-Instruct", backend="hf")
      run_execution_condition(problems_he, "humaneval", qwen_client, ...)
      run_execution_condition(problems_mbpp, "mbpp", qwen_client, ...)
      extract_round_results → save qwen round_results
12. exec_he = load_condition_results(llama_he_jsonl)
    pylint_he_idx = {r["task_id"]: r for r in pylint_he}
    common_ids = list(exec_he.keys() & pylint_he_idx.keys())
    mcnemar_he = run_mcnemar_test(pylint_he_idx, exec_he, common_ids)
    ci_lower, ci_upper = bootstrap_ci_delta_diff(baseline_arr, pylint_arr, exec_arr)
    mcnemar_he["ci_lower"] = ci_lower; mcnemar_he["ci_upper"] = ci_upper
    → save mcnemar_humaneval.json (repeat for mbpp, qwen)
13. metrics = compute_metrics(...); save metrics.json
14. generate_all_figures(metrics, ...)
15. print_gate_result(metrics)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | detect_resume_state | Check existence of expected JSONL/JSON output files; return status dict |
| L-9-2 | print_gate_result | Format gate verdict with p-values, deltas, routing; no external deps |
