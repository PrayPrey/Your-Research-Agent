---
title: "Logic: H-M4 — Feedback Overhead Efficiency Ratio Measurement"
hypothesis_id: H-M4
phase: 3
date: 2026-08-31
author: yoon303@etri.re.kr
---

# Logic Design: H-M4

Applied: timed-wrapper pattern (perf_counter around external subprocess calls)
Applied: bootstrap-BCa pairwise ratio comparison pattern (scipy.stats.bootstrap)
Applied: checkpoint-resume pattern (JSON incremental persistence)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No H-M3/H-M4 code/ folder exists — ablation mode
**Analyzed Path**: N/A — green-field design from experiment briefs
**Findings**: All verifier patterns derived from 02c_experiment_brief.md and architecture.
Prior hypothesis code is not available on disk; implement from scratch following documented interfaces.

---

## Subtask L-5: TimedFeedbackEvaluator (`code/evaluator.py`)

### L-5-1: `run_repair_loop` — Full Timing Implementation

```python
import time
from typing import Any

class TimedFeedbackEvaluator:
    def __init__(self, category: str, verifier_fn: callable, llm_client: Any) -> None:
        self.category = category  # 'execution' | 'static' | 'type' | 'smt'
        self.verifier_fn = verifier_fn
        self.llm_client = llm_client

    def run_repair_loop(
        self,
        problem: dict,
        initial_code: str,
        max_iters: int = 3,
    ) -> tuple[bool, float, list[float]]:
        """
        Args:
            problem: {task_id, prompt, tests, source}
            initial_code: generated code string (not timed — category-independent)
            max_iters: repair budget (default 3)
        Returns:
            (final_pass: bool, total_overhead_s: float, per_iter_times: list[float])
        Algorithm:
            for iter in range(max_iters):
                t0 = perf_counter()
                feedback, passed = verifier_fn(code, problem)
                t_verify = perf_counter() - t0
                if passed: return early
                t1 = perf_counter()
                code = _repair(code, feedback, problem)
                t_repair = perf_counter() - t1
                record iter_time = t_verify + t_repair
            final_pass check (verifier only, no additional repair overhead recorded)
        """
        code = initial_code
        total_overhead = 0.0
        per_iter_times: list[float] = []

        for _ in range(max_iters):
            t0 = time.perf_counter()
            feedback, passed = self.verifier_fn(code, problem)
            t_verify = time.perf_counter() - t0

            if passed:
                per_iter_times.append(t_verify)
                total_overhead += t_verify
                return True, total_overhead, per_iter_times

            t1 = time.perf_counter()
            code = self._repair(code, feedback, problem)
            t_repair = time.perf_counter() - t1

            iter_time = t_verify + t_repair
            per_iter_times.append(iter_time)
            total_overhead += iter_time

        # Final correctness check — not timed (outside repair budget)
        _, final_pass = self.verifier_fn(code, problem)
        return final_pass, total_overhead, per_iter_times
```

### L-5-2: `_repair` — GPT-4o-mini Repair Call

```python
    def _repair(self, code: str, feedback: str, problem: dict) -> str:
        """
        Args:
            code: current (failing) code string
            feedback: verifier feedback string
            problem: {task_id, prompt, tests}
        Returns:
            repaired code string
        Temperature: 0.0 (deterministic)
        Max tokens: 1024
        """
        prompt = (
            f"Fix the following Python function so it passes all tests.\n\n"
            f"Problem description:\n{problem['prompt']}\n\n"
            f"Current code:\n```python\n{code}\n```\n\n"
            f"Feedback from verifier:\n{feedback}\n\n"
            f"Return ONLY the corrected Python function, no explanation."
        )
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.0,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```python"):
            raw = raw[9:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        return raw.strip()
```

### L-5-3: Edge Cases

```python
# Edge case 1: verifier raises exception (e.g., subprocess timeout, Z3 parse error)
# Wrap verifier_fn call in try/except; on exception return ("ERROR: {e}", False) and record full timeout as overhead

# Edge case 2: empty feedback string
# If feedback == "": substitute "No feedback available. Check for syntax/runtime errors."

# Edge case 3: code extraction from LLM response fails
# If _repair returns empty string: reuse previous code (no-op repair)

# Edge case 4: final pass check after max_iters
# Only checks correctness; overhead NOT added to total_overhead_s (post-budget check)

def _safe_verify(self, code: str, problem: dict, timeout_overhead: float) -> tuple[str, bool]:
    """Wraps verifier with exception handling. Returns (feedback, passed)."""
    try:
        return self.verifier_fn(code, problem)
    except Exception as e:
        return f"ERROR: {e}", False
```

### L-5-4: Per-Problem Result Schema

```python
# Per-problem result dict written to checkpoint and results.json
result_schema = {
    "task_id": str,          # e.g. "HumanEval/0" or "mbpp/11"
    "category": str,         # 'execution' | 'static' | 'type' | 'smt'
    "source": str,           # 'humaneval' | 'mbpp'
    "initial_pass": bool,    # True if initial_code already passed (no repair needed)
    "final_pass": bool,      # True if passed after repair loop
    "total_overhead_s": float,  # sum of all timed iteration times
    "per_iter_times": list[float],  # per-iteration times (len <= max_iters)
    "n_iters": int,          # actual iterations used
    "timeout_hit": bool,     # True if any iteration hit SMT/exec timeout
}
```

---

## Subtask L-4: SMT Verifier (`code/verifiers.py`)

### L-4-1: LLM Constraint Generation Prompt

```python
def _generate_z3_constraints(code: str, problem: dict, llm_client) -> str:
    """
    Generates Z3 Python constraint code from the function implementation.
    Returns: Python string that can be exec'd to run Z3 verification.
    """
    prompt = (
        f"Given this Python function:\n```python\n{code}\n```\n\n"
        f"Write Z3 Python code (using `from z3 import *`) that:\n"
        f"1. Declares symbolic variables for the function inputs\n"
        f"2. Adds constraints modeling the function's behavior\n"
        f"3. Adds assertions from these tests: {problem['tests'][:500]}\n"
        f"4. Calls `s = Solver(); s.add(...); result = s.check()`\n"
        f"5. Prints 'UNSAT' if all constraints satisfied, 'SAT {s.model()}' if counterexample found\n"
        f"Return ONLY executable Python code, no explanation."
    )
    response = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
```

### L-4-2: Z3 Solve Implementation

```python
import subprocess
import tempfile
import os

def _run_z3_code(z3_code: str, timeout: float = 30.0) -> tuple[str, bool]:
    """
    Executes generated Z3 Python code in subprocess.
    Returns: (output_or_error: str, passed: bool)
    passed=True if output contains 'UNSAT' (no counterexample found).
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, prefix='z3_') as f:
        f.write("from z3 import *\n")
        f.write(z3_code)
        tmppath = f.name
    try:
        result = subprocess.run(
            ['python', tmppath],
            capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip() + result.stderr.strip()
        passed = 'UNSAT' in output and 'error' not in output.lower()
        return output, passed
    except subprocess.TimeoutExpired:
        return f"TIMEOUT after {timeout}s", False
    except Exception as e:
        return f"Z3 execution error: {e}", False
    finally:
        os.unlink(tmppath)
```

### L-4-3: SMT Timing — Separate LLM + Z3 Times

```python
def run_smt_verifier(
    code: str, problem: dict, llm_client, timeout: float = 30.0
) -> tuple[str, bool]:
    """
    Times LLM constraint generation + Z3 solve separately.
    Both are summed into total SMT overhead.
    Returns: (feedback: str, passed: bool)
    Note: timing is applied externally by TimedFeedbackEvaluator.
          This function returns feedback for repair loop use.
    """
    # LLM constraint generation (timed externally via perf_counter in TimedFeedbackEvaluator)
    z3_code = _generate_z3_constraints(code, problem, llm_client)

    # Clean up markdown fences from LLM output
    if z3_code.startswith("```python"):
        z3_code = z3_code[9:]
    if z3_code.endswith("```"):
        z3_code = z3_code[:-3]

    # Z3 solve (also timed externally as part of verifier_fn call)
    output, passed = _run_z3_code(z3_code, timeout=timeout)

    if passed:
        feedback = "Z3 verification passed: no counterexample found."
    elif "TIMEOUT" in output:
        feedback = f"Z3 verification timed out after {timeout}s. Simplify function logic."
    elif output.startswith("SAT"):
        feedback = f"Z3 found counterexample: {output}. Fix the implementation logic."
    else:
        feedback = f"Z3 error or parse failure: {output}. Ensure function is well-typed."

    return feedback, passed
```

### L-4-4: SMT Feedback Message Format

```
Feedback format for repair loop:
- PASSED: "Z3 verification passed: no counterexample found."
- TIMEOUT: "Z3 verification timed out after 30s. Simplify function logic or reduce constraints."
- COUNTEREXAMPLE: "Z3 found counterexample: SAT [x=3, y=0]. Fix the implementation logic."
- ERROR: "Z3 error or parse failure: {output}. Ensure function is well-typed and has simple control flow."
```

---

## Subtask L-8: Efficiency Ratio + Stats (`code/stats.py`)

### L-8-1: `compute_efficiency_ratio`

```python
import numpy as np

def compute_efficiency_ratio(
    pass_after: float,      # pass@1 rate after repair loop (0.0-1.0)
    pass_baseline: float,   # vanilla generation pass@1 (0.0-1.0) from H-E1
    mean_overhead_s: float, # mean wall-clock overhead per problem (seconds)
) -> float:
    """
    Δpass@1 / mean overhead seconds.
    Higher = more efficient (more correctness gain per second spent).
    Returns nan if mean_overhead_s <= 0 or delta <= 0.
    """
    delta = pass_after - pass_baseline
    if mean_overhead_s <= 0 or np.isnan(mean_overhead_s):
        return float('nan')
    return delta / mean_overhead_s

def compute_per_problem_ratios(
    results: list[dict],
    baseline_pass: dict[str, bool],
    category: str,
) -> np.ndarray:
    """
    Per-problem efficiency ratio for bootstrap CI.
    For each problem: ratio_i = (final_pass_i - baseline_pass_i) / overhead_s_i
    Returns array of shape (n_problems,).
    """
    cat_results = [r for r in results if r['category'] == category]
    ratios = []
    for r in cat_results:
        task_id = r['task_id']
        baseline = float(baseline_pass.get(task_id, False))
        final = float(r['final_pass'])
        overhead = r['total_overhead_s']
        if overhead > 0:
            ratios.append((final - baseline) / overhead)
        else:
            ratios.append(float('nan'))
    return np.array(ratios, dtype=float)
```

### L-8-2: `bootstrap_ratio_comparison` — BCa Bootstrap

```python
from scipy import stats as scipy_stats

def bootstrap_ratio_comparison(
    ratios_a: np.ndarray,   # per-problem ratios for category A
    ratios_b: np.ndarray,   # per-problem ratios for category B
    n_resamples: int = 10000,
    confidence_level: float = 0.95,
) -> dict:
    """
    Bootstrap BCa CI for mean(ratios_a) - mean(ratios_b).
    Returns:
        {ci_low: float, ci_high: float, p_approx: float,
         mean_diff: float, significant: bool}
    significant=True if CI excludes 0 (p_approx < 0.05).

    Algorithm:
        1. Filter NaN values from both arrays
        2. scipy.stats.bootstrap((a, b), statistic=diff_means, n_resamples, method='BCa')
        3. CI excludes 0 → significant (p<0.05 approximation)
    """
    def diff_means(a, b, axis):
        return np.mean(a, axis=axis) - np.mean(b, axis=axis)

    # Filter NaN
    mask_a = ~np.isnan(ratios_a)
    mask_b = ~np.isnan(ratios_b)
    a_clean = ratios_a[mask_a]
    b_clean = ratios_b[mask_b]

    result = scipy_stats.bootstrap(
        (a_clean, b_clean),
        diff_means,
        n_resamples=n_resamples,
        method='BCa',
        confidence_level=confidence_level,
        paired=False,
        random_state=1,
    )
    ci_low, ci_high = result.confidence_interval
    mean_diff = float(np.mean(a_clean) - np.mean(b_clean))
    significant = not (ci_low <= 0 <= ci_high)

    return {
        'ci_low': float(ci_low),
        'ci_high': float(ci_high),
        'mean_diff': mean_diff,
        'p_approx': 0.04 if significant else 1.0,
        'significant': significant,
    }
```

### L-8-3: Overhead Statistical Tests

```python
from scipy.stats import kruskal, mannwhitneyu

def kruskal_wallis_overhead(overhead_by_cat: dict[str, list[float]]) -> dict:
    """
    Kruskal-Wallis H-test across 4 overhead distributions.
    Input: {'execution': [...], 'static': [...], 'type': [...], 'smt': [...]}
    Returns: {'statistic': float, 'p_value': float, 'significant': bool}
    """
    groups = [overhead_by_cat[cat] for cat in ['execution', 'static', 'type', 'smt']]
    stat, p = kruskal(*groups)
    return {'statistic': float(stat), 'p_value': float(p), 'significant': p < 0.05}

def mannwhitney_pairwise(overhead_by_cat: dict[str, list[float]]) -> dict:
    """
    Pairwise Mann-Whitney U for all 4×3/2=6 category pairs.
    Returns: {(cat_a, cat_b): {'statistic': float, 'p_value': float, 'cat_a_slower': bool}}
    cat_a_slower=True means cat_a has significantly higher overhead than cat_b.
    """
    cats = ['execution', 'static', 'type', 'smt']
    results = {}
    for i, ca in enumerate(cats):
        for cb in cats[i+1:]:
            stat, p = mannwhitneyu(
                overhead_by_cat[ca], overhead_by_cat[cb], alternative='two-sided'
            )
            results[(ca, cb)] = {
                'statistic': float(stat),
                'p_value': float(p),
                'ca_slower': float(np.median(overhead_by_cat[ca])) > float(np.median(overhead_by_cat[cb])),
            }
    return results

def summarize_overhead(overhead_by_cat: dict[str, list[float]]) -> dict[str, dict]:
    """Per-category descriptive stats."""
    summary = {}
    for cat, vals in overhead_by_cat.items():
        arr = np.array(vals)
        summary[cat] = {
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'p95': float(np.percentile(arr, 95)),
            'n': len(vals),
        }
    return summary
```

### L-8-4: Gate Metric Evaluation

```python
CATEGORIES = ['execution', 'static', 'type', 'smt']

def evaluate_gate_metric(
    results: list[dict],
    baseline_pass: dict[str, bool],
) -> dict:
    """
    Evaluates H-M4 primary gate:
      ratio(execution) >= 1.5 × ratio(next-best) AND bootstrap p<0.05

    Returns:
        {
          'ratios': {cat: float},
          'overhead_means': {cat: float},
          'best_category': str,
          'second_best_category': str,
          'ratio_advantage': float,          # ratio(best) / ratio(second_best)
          'bootstrap_result': dict,          # from bootstrap_ratio_comparison
          'gate_passed': bool,               # True if execution wins AND >= 1.5x AND p<0.05
          'execution_is_best': bool,
        }
    """
    # Compute mean overhead per category
    overhead_by_cat = {cat: [] for cat in CATEGORIES}
    for r in results:
        overhead_by_cat[r['category']].append(r['total_overhead_s'])

    overhead_means = {cat: float(np.mean(vals)) for cat, vals in overhead_by_cat.items()}

    # Compute pass@1 per category
    pass_after = {}
    for cat in CATEGORIES:
        cat_results = [r for r in results if r['category'] == cat]
        pass_after[cat] = float(np.mean([r['final_pass'] for r in cat_results]))

    baseline_rate = float(np.mean(list(baseline_pass.values())))

    # Aggregate efficiency ratios
    ratios = {
        cat: compute_efficiency_ratio(pass_after[cat], baseline_rate, overhead_means[cat])
        for cat in CATEGORIES
    }

    # Determine best and second best
    sorted_cats = sorted(CATEGORIES, key=lambda c: ratios.get(c, float('-inf')), reverse=True)
    best_cat = sorted_cats[0]
    second_best_cat = sorted_cats[1]

    # Bootstrap CI for best vs second-best
    per_problem_best = compute_per_problem_ratios(results, baseline_pass, best_cat)
    per_problem_second = compute_per_problem_ratios(results, baseline_pass, second_best_cat)
    bootstrap_result = bootstrap_ratio_comparison(per_problem_best, per_problem_second)

    ratio_advantage = ratios[best_cat] / ratios[second_best_cat] if ratios[second_best_cat] > 0 else float('inf')

    gate_passed = (
        best_cat == 'execution'
        and ratio_advantage >= 1.5
        and bootstrap_result['significant']
    )

    return {
        'ratios': ratios,
        'overhead_means': overhead_means,
        'best_category': best_cat,
        'second_best_category': second_best_cat,
        'ratio_advantage': ratio_advantage,
        'bootstrap_result': bootstrap_result,
        'gate_passed': gate_passed,
        'execution_is_best': best_cat == 'execution',
    }
```

---

## Subtask L-7: Experiment Runner (`code/runner.py`)

### L-7-1: Checkpoint/Resume Logic

```python
import json
from pathlib import Path

def load_checkpoint(path: str) -> list[dict]:
    """Load existing results from checkpoint JSON. Returns [] if not found."""
    p = Path(path)
    if not p.exists():
        return []
    with open(p) as f:
        return json.load(f)

def save_checkpoint(results: list[dict], path: str) -> None:
    """Atomic write via temp file to avoid corruption."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = str(p) + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(results, f, indent=2)
    Path(tmp).rename(p)

def get_completed_keys(results: list[dict]) -> set[tuple[str, str]]:
    """Returns set of (task_id, category) pairs already completed."""
    return {(r['task_id'], r['category']) for r in results}

def run_experiment(
    problems: list[dict],
    categories: list[str],
    checkpoint_path: str,
    baseline_pass: dict[str, bool],
    llm_client,
    verifier_fns: dict[str, callable],
    max_iters: int = 3,
) -> list[dict]:
    """
    Main experiment loop: 538 × 4 = 2,152 repair loop runs.
    Resumes from checkpoint if exists.
    Logs: [H-M4] Category={cat} problem={task_id} overhead={elapsed:.3f}s pass={passed}
    """
    results = load_checkpoint(checkpoint_path)
    completed = get_completed_keys(results)

    for problem in tqdm(problems, desc="Problems"):
        for cat in categories:
            key = (problem['task_id'], cat)
            if key in completed:
                continue  # Resume: skip already done

            evaluator = TimedFeedbackEvaluator(cat, verifier_fns[cat], llm_client)
            initial_code = _generate_initial_code(problem, llm_client)
            initial_pass, _, _ = evaluator.run_repair_loop(problem, initial_code, max_iters=0)

            final_pass, total_overhead_s, per_iter_times = evaluator.run_repair_loop(
                problem, initial_code, max_iters=max_iters
            )

            result = {
                'task_id': problem['task_id'],
                'category': cat,
                'source': problem['source'],
                'initial_pass': bool(baseline_pass.get(problem['task_id'], False)),
                'final_pass': bool(final_pass),
                'total_overhead_s': total_overhead_s,
                'per_iter_times': per_iter_times,
                'n_iters': len(per_iter_times),
                'timeout_hit': total_overhead_s >= 29.0 and cat == 'smt',
            }
            results.append(result)
            completed.add(key)

            print(f"[H-M4] Category={cat} problem={problem['task_id']} "
                  f"overhead={total_overhead_s:.3f}s pass={final_pass}")

            # Checkpoint after every problem×category
            save_checkpoint(results, checkpoint_path)

    return results
```

### L-7-2: Parallel-per-Category Execution (Optional)

```python
from concurrent.futures import ThreadPoolExecutor

def run_experiment_parallel(
    problems: list[dict],
    categories: list[str],
    checkpoint_path: str,
    baseline_pass: dict[str, bool],
    llm_client,
    verifier_fns: dict,
    max_iters: int = 3,
    n_workers: int = 4,  # one thread per category
) -> list[dict]:
    """
    Parallel execution: 4 threads, one per category.
    Each thread processes all 538 problems for its category.
    Checkpoint writes are serialized via threading.Lock.
    # ponytail: global lock on checkpoint writes; per-category locks if write contention observed
    """
    import threading
    lock = threading.Lock()
    results = load_checkpoint(checkpoint_path)
    completed = get_completed_keys(results)

    def run_category(cat: str) -> list[dict]:
        cat_results = []
        evaluator = TimedFeedbackEvaluator(cat, verifier_fns[cat], llm_client)
        for problem in problems:
            key = (problem['task_id'], cat)
            if key in completed:
                continue
            final_pass, total_overhead_s, per_iter_times = evaluator.run_repair_loop(
                problem, _get_initial_code(problem, baseline_pass), max_iters=max_iters
            )
            r = {
                'task_id': problem['task_id'], 'category': cat,
                'source': problem['source'],
                'initial_pass': bool(baseline_pass.get(problem['task_id'], False)),
                'final_pass': bool(final_pass),
                'total_overhead_s': total_overhead_s,
                'per_iter_times': per_iter_times,
                'n_iters': len(per_iter_times),
                'timeout_hit': total_overhead_s >= 29.0 and cat == 'smt',
            }
            with lock:
                results.append(r)
                save_checkpoint(results, checkpoint_path)
            cat_results.append(r)
            print(f"[H-M4] Category={cat} problem={problem['task_id']} "
                  f"overhead={total_overhead_s:.3f}s pass={final_pass}")
        return cat_results

    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        futures = [ex.submit(run_category, cat) for cat in categories]
        for f in futures:
            f.result()

    return results
```

---

## Subtask L-2: Execution Verifier (`code/verifiers.py`)

### L-2-1: Subprocess Execution Harness

```python
import subprocess
import tempfile
import os
import textwrap

def run_execution_verifier(
    code: str,
    problem: dict,
    timeout: float = 10.0,
) -> tuple[str, bool]:
    """
    Executes code + test assertions in subprocess.
    Returns: (feedback: str, passed: bool)
    passed=True if subprocess exits with code 0 and no AssertionError.

    Algorithm:
        1. Write code + test harness to tmpfile.py
        2. subprocess.run(['python', tmpfile], timeout=timeout, capture_output=True)
        3. passed if returncode==0 and 'AssertionError' not in stderr
        4. feedback = stdout+stderr if failed, "All tests passed" if passed
    """
    test_harness = _build_test_harness(code, problem)
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.py', delete=False, prefix='exec_'
    ) as f:
        f.write(test_harness)
        tmppath = f.name

    try:
        result = subprocess.run(
            ['python', tmppath],
            capture_output=True, text=True, timeout=timeout
        )
        passed = result.returncode == 0
        if passed:
            feedback = "All tests passed."
        else:
            output = (result.stdout + result.stderr).strip()
            feedback = output[:1000] if output else "Runtime error (no output)."
        return feedback, passed
    except subprocess.TimeoutExpired:
        return f"Execution timed out after {timeout}s.", False
    except Exception as e:
        return f"Subprocess error: {e}", False
    finally:
        os.unlink(tmppath)

def _build_test_harness(code: str, problem: dict) -> str:
    """Combines function code + test assertions into executable Python."""
    tests = problem.get('tests', '')
    if isinstance(tests, list):
        tests = '\n'.join(tests)
    return f"{code}\n\n# Tests\n{tests}\n"
```

### L-2-2: Test Assertion Feedback Format

```python
def _parse_assertion_failure(stderr: str) -> str:
    """
    Extracts meaningful feedback from AssertionError output.
    Returns structured feedback string for LLM repair.
    """
    lines = stderr.strip().split('\n')
    # Find assertion lines
    assertion_lines = [l for l in lines if 'AssertionError' in l or 'assert' in l.lower()]
    error_lines = [l for l in lines if 'Error' in l or 'Exception' in l]

    if assertion_lines:
        return (
            f"Test assertion failed:\n" +
            '\n'.join(assertion_lines[:3]) +
            "\nFix the function logic so it produces the correct output."
        )
    elif error_lines:
        return (
            f"Runtime error:\n" +
            '\n'.join(error_lines[:3]) +
            "\nFix the syntax/runtime error."
        )
    return f"Tests failed:\n{stderr[:500]}\nFix the function."
```

---

## Data Schemas Summary

| Object | Fields | Notes |
|---|---|---|
| `problem` | task_id, prompt, tests, source | Unified 538-problem schema |
| `result` | task_id, category, source, initial_pass, final_pass, total_overhead_s, per_iter_times, n_iters, timeout_hit | Per-problem×category output |
| `efficiency_ratio` | float | Δpass@1 / mean_overhead_s |
| `bootstrap_result` | ci_low, ci_high, mean_diff, p_approx, significant | BCa 95% CI for ratio comparison |
| `overhead_summary` | mean, median, std, min, max, p95, n | Per-category overhead stats |

## Sanity Check Assertions

```python
# Post-collection sanity checks (from 02c_experiment_brief.md)
assert mean_overhead['execution'] > 0.05, "Execution overhead implausibly low"
assert mean_overhead['smt'] > mean_overhead['execution'], "SMT should be slowest"
assert all(r > 0 for r in ratios.values() if not np.isnan(r)), "All Δpass@1 should be positive"
print(f"Overhead ordering: {sorted(mean_overhead.items(), key=lambda x: x[1])}")
print(f"Efficiency ratios: {ratios}")
```
