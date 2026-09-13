# Logic Design: h-m3 — Execution+mypy vs Execution-only Repair

**Hypothesis ID:** h-m3
**Date:** 2026-08-26
**Type:** MECHANISM (INCREMENTAL — extends h-m2)
**Budget:** 10 subtasks

Applied: iterative-repair-loop-pattern
Applied: multi-seed-statistical-averaging
Applied: welch-t-test-per-problem-delta
Applied: mypy-subprocess-permissive-mode
Applied: token-count-confound-logging

---

## Codebase Analysis (Direct Read)

**h-m2/code/ actual structure verified:**

```
h-m2/code/
├── repair_loop.py   # run_condition_a, run_condition_b, run_mypy, _build_prompt_a/b, _llm_repair
├── run.py           # main(): single seed, single dataset (humaneval+ only), checkpoint dict
├── analysis.py      # compute_differential, per_round_repair_rates
├── config.py        # ExperimentConfig dataclass
└── visualize.py     # generate_all_figures
```

**Key verified signatures from actual code (not specs):**

| Function | Actual Signature | Notes |
|----------|-----------------|-------|
| `run_condition_a` | `(client: OpenAI, task_id: str, problem: dict, seed: int = 42, k_max: int = 5) -> dict` | Returns `{task_id, rounds, initial_mypy_errors, final_passed, condition}` |
| `run_condition_b` | `(client: OpenAI, task_id: str, problem: dict, seed: int = 42, k_max: int = 5) -> dict` | Same schema; rounds include `mypy_error_count` |
| `run_mypy` | `(code: str, timeout: int = 10) -> tuple[int, str]` | Returns `(error_count, stdout)` |
| `_build_prompt_a` | `(problem: dict, prev_solution: str, exec_feedback: str) -> str` | No mypy |
| `_build_prompt_b` | `(problem: dict, prev_solution: str, exec_feedback: str, mypy_stdout: str) -> str` | Appends mypy block |
| `_llm_repair` | `(client: OpenAI, prompt: str, max_tokens: int = 2048, max_retries: int = 3, base_delay: float = 1.0) -> str` | temperature=0.0 |
| `compute_differential` | `(results_a: list, results_b: list) -> dict` | h-m2 differential; h-m3 replaces with pass@1 delta |
| `generate_solution` | imported from h-e1/pipeline.py | `(client, problem, seed) -> str` |
| `evaluate_solution` | imported from h-e1/pipeline.py | `(task_id, solution, problem) -> bool` |
| `load_problems` | imported from h-e1/pipeline.py | `(benchmark: str) -> dict` — MBPP+ support must be verified |

**Critical finding:** h-m2 `run.py` is single-seed, single-dataset. h-m3 must extend to 3 seeds × 2 datasets with composite checkpoint key `(dataset, seed, condition, task_id)`.

**Token logging:** NOT present in h-m2. Added new in h-m3 via `_count_tokens(prompt: str) -> int`.

---

## External Dependencies API

From `h-e1/code/pipeline.py` (verified via h-m2 import statements):

```python
# Verified imports used in h-m2/code/repair_loop.py lines 17-23
from pipeline import (
    extract_code,        # (text: str) -> str — extracts code block from LLM response
    generate_solution,   # (client: OpenAI, problem: dict, seed: int) -> str
    evaluate_solution,   # (task_id: str, solution: str, problem: dict) -> bool
    load_problems,       # (benchmark: str) -> dict[str, dict]
    MYPY_FLAGS,          # list[str] = ["--ignore-missing-imports", "--no-strict-optional"]
)
```

**h-m3 adds** `--no-error-summary` to mypy flags (config-level override, not changing h-e1).

---

## Epic A-2: Repair Loop Core (Complexity 14)

### Subtask L-2-1: `_count_tokens`

```python
def _count_tokens(prompt: str) -> int:
    """Approximate token count via word-split (no tiktoken dependency)."""
    # pseudocode:
    # return len(prompt.split()) * 4 // 3  # rough 1.33 words/token estimate
    # OR: use tiktoken if available, else fallback
    ...
```

**Signature:** `(prompt: str) -> int`
**Used by:** `run_condition_a_h3`, `run_condition_b_h3` to log `prompt_tokens` per round.

### Subtask L-2-2: `run_condition_a_h3`

Extends h-m2 `run_condition_a` — adds token logging and seed parameter threaded through.

```python
def run_condition_a_h3(
    client: OpenAI,
    task_id: str,
    problem: dict,
    seed: int = 42,
    k_max: int = 5,
) -> dict:
    """Execution-only repair loop with token logging. Extends h-m2 run_condition_a."""
    # pseudocode:
    # solution = generate_solution(client, problem, seed)
    # initial_mypy_errors, _ = run_mypy(solution)
    # rounds = []
    # for k in 1..k_max:
    #     exec_passed = evaluate_solution(task_id, solution, problem)
    #     if not exec_passed and k < k_max:
    #         prompt = _build_prompt_a(problem, solution, exec_feedback)
    #         token_count = _count_tokens(prompt)
    #         solution = _llm_repair(client, prompt)
    #         rounds.append({round: k, exec_passed: bool, prompt_tokens: int})
    #     else:
    #         rounds.append({round: k, exec_passed: bool, prompt_tokens: 0})
    #     if exec_passed: break
    # return {task_id, condition:"A", seed, rounds, initial_mypy_errors, final_passed}
    ...
```

**Returns:** `dict` with keys `{task_id, condition, seed, rounds, initial_mypy_errors, final_passed}`
**Rounds schema:** `[{round: int, exec_passed: bool, prompt_tokens: int}]`

### Subtask L-2-3: `run_condition_b_h3`

Extends h-m2 `run_condition_b` — adds token logging.

```python
def run_condition_b_h3(
    client: OpenAI,
    task_id: str,
    problem: dict,
    seed: int = 42,
    k_max: int = 5,
) -> dict:
    """Execution+mypy repair loop with token logging. Extends h-m2 run_condition_b."""
    # pseudocode:
    # solution = generate_solution(client, problem, seed)
    # initial_mypy_errors, _ = run_mypy(solution)
    # rounds = []
    # for k in 1..k_max:
    #     mypy_count, mypy_stdout = run_mypy(solution)
    #     exec_passed = evaluate_solution(task_id, solution, problem)
    #     if not exec_passed and k < k_max:
    #         prompt = _build_prompt_b(problem, solution, exec_feedback, mypy_stdout)
    #         token_count = _count_tokens(prompt)
    #         if mypy_count > 0:
    #             logger.info(f"MYPY_FEEDBACK_ADDED: {mypy_count} errors for {task_id} round {k}")
    #         solution = _llm_repair(client, prompt)
    #         rounds.append({round:k, exec_passed:bool, mypy_error_count:int, prompt_tokens:int})
    #     else:
    #         rounds.append({round:k, exec_passed:bool, mypy_error_count:mypy_count, prompt_tokens:0})
    #     if exec_passed: break
    # return {task_id, condition:"B", seed, rounds, initial_mypy_errors, final_passed}
    ...
```

**Returns:** same schema as `run_condition_a_h3` but rounds include `mypy_error_count: int`.

### Subtask L-2-4: `_build_prompt_a` / `_build_prompt_b` token parity check

```python
def assert_prompt_length_difference(problem: dict, solution: str) -> dict:
    """Measure token delta between Condition A and B prompts for same input."""
    # pseudocode:
    # prompt_a = _build_prompt_a(problem, solution, exec_feedback)
    # mypy_count, mypy_stdout = run_mypy(solution)
    # prompt_b = _build_prompt_b(problem, solution, exec_feedback, mypy_stdout)
    # return {tokens_a: _count_tokens(prompt_a), tokens_b: _count_tokens(prompt_b),
    #         delta: _count_tokens(prompt_b) - _count_tokens(prompt_a)}
    ...
```

Used in confound analysis (h-m2 identified context-length as primary confound target).

---

## Epic A-3: Multi-Seed Orchestrator (Complexity 13)

### Subtask L-3-1: composite checkpoint design

**Checkpoint key:** `f"{dataset}__{seed}__{condition}__{task_id}"`

```python
def _load_checkpoint_h3(path: pathlib.Path) -> dict:
    """Load checkpoint; keys are composite 'dataset__seed__condition__task_id'."""
    # pseudocode:
    # if path.exists(): return json.loads(path.read_text())
    # return {"completed": {}, "results": []}
    # completed[composite_key] = True
    # results: flat list of result dicts (each has dataset, seed, condition fields)
    ...
```

```python
def _make_key(dataset: str, seed: int, condition: str, task_id: str) -> str:
    """Composite checkpoint key for 3D experiment space."""
    return f"{dataset}__{seed}__{condition}__{task_id}"
```

### Subtask L-3-2: `run_experiment_loop`

```python
def run_experiment_loop(
    client: OpenAI,
    cfg: "ExperimentConfig",
    checkpoint_path: pathlib.Path,
) -> list[dict]:
    """Outer loop: datasets × seeds × conditions × problems."""
    # pseudocode:
    # ckpt = _load_checkpoint_h3(checkpoint_path)
    # results = ckpt["results"]
    # for dataset in cfg.datasets:  # ["humaneval+", "mbpp+"]
    #     problems = load_problems(dataset)
    #     for seed in cfg.seeds:    # [42, 123, 456]
    #         for condition in cfg.conditions:  # ["A", "B"]
    #             for task_id, problem in problems.items():
    #                 key = _make_key(dataset, seed, condition, task_id)
    #                 if key in ckpt["completed"]: continue
    #                 if condition == "A":
    #                     result = run_condition_a_h3(client, task_id, problem, seed, cfg.k_max)
    #                 else:
    #                     result = run_condition_b_h3(client, task_id, problem, seed, cfg.k_max)
    #                 result.update({"dataset": dataset, "seed": seed})
    #                 results.append(result)
    #                 ckpt["completed"][key] = True
    #                 ckpt["results"] = results
    #                 _save_checkpoint(checkpoint_path, ckpt)
    # return results
    ...
```

---

## Epic A-4: Statistical Analysis (Complexity 12)

### Subtask L-4-1: `compute_per_problem_delta`

```python
def compute_per_problem_delta(
    results: list[dict],
    dataset: str,
) -> tuple[list[float], list[float]]:
    """Per-problem pass@1 averaged over seeds and rounds, for Conditions A and B.

    Returns (pass_a_per_problem, pass_b_per_problem) parallel lists over problems.
    """
    # pseudocode:
    # Filter results by dataset
    # Group by (task_id, condition) → aggregate over seeds and rounds
    # For each task_id:
    #   pass_a[i] = mean over seeds of (1 if any round passed else 0)
    #   pass_b[i] = same for condition B
    # Return parallel lists (same task_id order)
    ...
```

**Shape:** `pass_a_per_problem: list[float]` length = n_problems (378 for MBPP+, 164 for HumanEval+)

### Subtask L-4-2: `welch_test` + `confound_analysis`

```python
def welch_test(
    pass_a: list[float],
    pass_b: list[float],
) -> dict:
    """Welch's t-test on per-problem delta. Returns gate metrics."""
    # pseudocode:
    # from scipy import stats
    # t_stat, p_value = stats.ttest_ind(pass_b, pass_a, equal_var=False)
    # absolute_improvement = mean(pass_b) - mean(pass_a)
    # gate_passed = p_value < 0.05 and absolute_improvement >= 0.01
    # return {t_stat, p_value, absolute_improvement, gate_passed, n_problems}
    ...
```

```python
def confound_analysis(results: list[dict], dataset: str) -> dict:
    """Compute mean token delta (Condition B - A) per round. h-m2 confound control."""
    # pseudocode:
    # For each round k in 1..5:
    #   tokens_a_k = mean prompt_tokens over (condition==A, round==k, dataset)
    #   tokens_b_k = mean prompt_tokens over (condition==B, round==k, dataset)
    #   delta_k = tokens_b_k - tokens_a_k
    # return {per_round_delta: {1: float, 2: float, ...}, mean_delta: float}
    ...
```

---

## Epic A-8: Unit Tests (Complexity 10)

### Subtask L-8-1: `test_repair_loop.py`

```python
# test_repair_loop.py — minimal self-check
def test_count_tokens():
    """Token count is positive for non-empty prompt."""
    assert _count_tokens("hello world") > 0

def test_build_prompt_b_includes_mypy():
    """Condition B prompt includes mypy section when errors present."""
    problem = {"prompt": "def foo(): pass"}
    prompt = _build_prompt_b(problem, "def foo(): pass", "exec failed", "error: type mismatch")
    assert "mypy" in prompt.lower() or "type checker" in prompt.lower()

def test_condition_b_longer_than_a():
    """Condition B prompt is longer than A when mypy has output."""
    problem = {"prompt": "def foo(): pass"}
    pa = _build_prompt_a(problem, "def foo(): pass", "exec failed")
    pb = _build_prompt_b(problem, "def foo(): pass", "exec failed", "error: X")
    assert len(pb) > len(pa)

def test_checkpoint_key_unique():
    """Composite key includes all 4 dimensions."""
    key = _make_key("humaneval+", 42, "A", "HumanEval/0")
    assert "humaneval+" in key and "42" in key and "_A_" in key or "__A__" in key

if __name__ == "__main__":
    test_count_tokens()
    test_build_prompt_b_includes_mypy()
    test_condition_b_longer_than_a()
    test_checkpoint_key_unique()
    print("All tests passed.")
```

### Subtask L-8-2: `test_analysis.py`

```python
# test_analysis.py — minimal self-check for statistical analysis
def test_welch_detects_difference():
    """Welch test detects known difference between two distributions."""
    import numpy as np
    pass_a = [0.5] * 100
    pass_b = [0.6] * 100  # 10pp improvement
    result = welch_test(pass_a, pass_b)
    assert result["p_value"] < 0.05
    assert result["absolute_improvement"] > 0.09

def test_welch_no_difference():
    """Welch test does not reject when distributions are equal."""
    pass_a = [0.5] * 100
    pass_b = [0.5] * 100
    result = welch_test(pass_a, pass_b)
    assert result["gate_passed"] == False

def test_confound_analysis_returns_per_round():
    """confound_analysis returns delta for all 5 rounds."""
    result = confound_analysis([], "mbpp+")
    # empty results → zeros
    assert isinstance(result["per_round_delta"], dict)

if __name__ == "__main__":
    test_welch_detects_difference()
    test_welch_no_difference()
    test_confound_analysis_returns_per_round()
    print("All analysis tests passed.")
```

---

## Tensor Shapes / Data Schemas

N/A — NLP task, no tensor operations. Key data schemas:

**Result record (per problem, per seed, per condition):**
```python
{
    "task_id": str,           # e.g. "mbpp/1", "HumanEval/0"
    "dataset": str,           # "humaneval+" | "mbpp+"
    "condition": str,         # "A" | "B"
    "seed": int,              # 42 | 123 | 456
    "initial_mypy_errors": int,
    "final_passed": bool,
    "rounds": [
        {
            "round": int,           # 1..5
            "exec_passed": bool,
            "mypy_error_count": int,  # Condition B only (0 for A)
            "prompt_tokens": int,     # 0 if no repair prompt (passed immediately)
        }
    ]
}
```

**Per-problem delta vector (for Welch test):**
```python
# Shape: (n_problems,) float — mean over seeds × rounds
pass_a_per_problem: list[float]  # len=378 for MBPP+
pass_b_per_problem: list[float]  # len=378 for MBPP+
delta_per_problem: list[float]   # pass_b - pass_a, element-wise
```
