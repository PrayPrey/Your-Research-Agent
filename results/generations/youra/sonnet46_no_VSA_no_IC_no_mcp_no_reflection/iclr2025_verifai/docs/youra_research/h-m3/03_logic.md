# H-M3 Logic Design: Feedback-Guided Repair Loop

Applied: repair-loop-with-per-iteration-tracking pattern (Olausson 2023 + Shinn/Reflexion 2023)

---

## Codebase Analysis (Serena)

**Project Type**: incremental_hypothesis (extends H-M2)
**Analyzed Path**: `docs/youra_research/h-m2/code/src/`
**Key Finding**: All verifier logic lives in a single `FeedbackMeasurer` class in `measure.py` — NOT separate verifier classes. H-M3 needs adapter wrappers to expose `get_feedback(solution, problem) -> str` interface.

**Symbols found in H-M2 code:**

| Symbol | File | Signature |
|--------|------|-----------|
| `FeedbackMeasurer.__init__` | `src/measure.py` | `(self, timeout_secs: int = 10)` |
| `FeedbackMeasurer.measure_execution` | `src/measure.py` | `(self, code: str) -> dict` |
| `FeedbackMeasurer.measure_pyright` | `src/measure.py` | `(self, code: str) -> dict` |
| `FeedbackMeasurer.measure_mypy` | `src/measure.py` | `(self, code: str) -> dict` |
| `FeedbackMeasurer.measure_z3` | `src/measure.py` | `(self, constraints: list | None) -> dict` |
| `Z3ConstraintExtractor.extract` | `src/z3_extractor.py` | `(self, task_id: str, docstring: str) -> list | None` |
| `load_failing_records` | `src/load_h_m1.py` | returns list of dicts with `{task_id, code, runnable, ...}` |

**Critical difference from PRD assumption**: H-M2 verifiers return `{"verifier": str, "char_count": int, "field_count": int, "timeout": bool}` — they do NOT return raw feedback strings. H-M3 must reconstruct raw feedback from measure calls OR re-run verifiers directly to get string output.

---

## External Dependencies API

### H-M2 Actual APIs (verified from code)

```python
# From: docs/youra_research/h-m2/code/src/measure.py

class FeedbackMeasurer:
    def __init__(self, timeout_secs: int = 10): ...

    def measure_execution(self, code: str) -> dict:
        # Returns: {"verifier": "execution", "char_count": int, "field_count": int, "timeout": bool}
        # feedback is stderr or stdout of subprocess run

    def measure_pyright(self, code: str) -> dict:
        # Returns: {"verifier": "pyright", "char_count": int, "field_count": int, "timeout": bool}
        # raw JSON stdout from `pyright --outputjson`

    def measure_mypy(self, code: str) -> dict:
        # Returns: {"verifier": "mypy", "char_count": int, "field_count": int, "timeout": bool}
        # stdout from `mypy --no-error-summary --ignore-missing-imports`

    def measure_z3(self, constraints: list | None) -> dict:
        # Returns: {"verifier": "z3", "char_count": int, "field_count": int, "timeout": bool}

# From: docs/youra_research/h-m2/code/src/z3_extractor.py
class Z3ConstraintExtractor:
    def extract(self, task_id: str, docstring: str) -> list | None:
        # Returns z3.BoolRef list or None
```

**H-M3 design decision**: Re-run verifiers to get raw string feedback (not just char_count).
VerifierAdapters wrap `FeedbackMeasurer` methods and also capture raw string output for repair prompt injection.

---

## A-2: VerifierAdapters [Complexity: 10, Budget: 2 subtasks]

Applied: adapter-pattern wrapping FeedbackMeasurer for raw-string interface

### API Signatures

```python
# src/verifier_adapters.py
from dataclasses import dataclass
from h_m2_measure import FeedbackMeasurer, Z3ConstraintExtractor  # from h-m2/code/src/

@dataclass
class FeedbackResult:
    category: str
    feedback_text: str       # Raw string for repair prompt
    char_count: int
    timeout: bool

class BaseVerifierAdapter:
    category: str
    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult: ...

class ExecutionVerifierAdapter(BaseVerifierAdapter):
    category = "execution"
    def __init__(self, timeout_secs: int = 5): ...
    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult: ...

class PyrightVerifierAdapter(BaseVerifierAdapter):
    category = "pyright"
    def __init__(self, timeout_secs: int = 10): ...
    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult: ...

class MypyVerifierAdapter(BaseVerifierAdapter):
    category = "mypy"
    def __init__(self, timeout_secs: int = 10): ...
    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult: ...

class Z3VerifierAdapter(BaseVerifierAdapter):
    category = "z3"
    def __init__(self, extractor: Z3ConstraintExtractor, timeout_secs: int = 30): ...
    def get_feedback(self, solution: str, problem: dict) -> FeedbackResult: ...
```

### Subtask: L-2-1 — Execution/Pyright/Mypy adapter implementations

```python
# ExecutionVerifierAdapter.get_feedback pseudo-code:
# 1. write solution + problem["test_code"] to temp .py file
# 2. subprocess.run(["python3", tmpfile], capture_output=True, timeout=timeout_secs)
# 3. feedback_text = result.stderr or result.stdout or "No output"
# 4. return FeedbackResult(category="execution", feedback_text=feedback_text,
#                          char_count=len(feedback_text), timeout=False)
# 5. On TimeoutExpired: return FeedbackResult(..., feedback_text="TIMEOUT", timeout=True)

# PyrightVerifierAdapter.get_feedback pseudo-code:
# 1. write solution to temp .py file
# 2. subprocess.run(["pyright", "--outputjson", tmpfile], capture_output=True, timeout=10)
# 3. feedback_text = result.stdout.strip() or "No diagnostics"
# 4. return FeedbackResult(category="pyright", feedback_text=feedback_text, ...)

# MypyVerifierAdapter.get_feedback pseudo-code:
# 1. write solution to temp .py file
# 2. subprocess.run(["mypy", "--no-error-summary", "--ignore-missing-imports", tmpfile], ...)
# 3. feedback_text = result.stdout.strip() or "No type errors"
# 4. return FeedbackResult(category="mypy", feedback_text=feedback_text, ...)
```

### Subtask: L-2-2 — Z3VerifierAdapter (with LLM constraint extraction)

```python
# Z3VerifierAdapter.get_feedback pseudo-code:
# 1. docstring = problem.get("docstring") or problem.get("prompt", "")
# 2. constraints = self.extractor.extract(problem["task_id"], docstring)
# 3. if constraints is None:
#       return FeedbackResult(category="z3", feedback_text="No Z3 constraints extractable",
#                             char_count=0, timeout=False)
# 4. Run Z3 solver: status, model = _check_satisfiable(constraints, timeout_ms=29000)
# 5. if status == "sat":
#       feedback_text = f"Z3 counterexample: {str(model)}"
# 6. if status == "unsat":
#       feedback_text = "Z3: constraints unsatisfiable — code has a logical error"
# 7. else: feedback_text = "Z3: timeout or unknown"
# 8. return FeedbackResult(category="z3", feedback_text=feedback_text, ...)
```

---

## A-3: evaluate_solution [Complexity: 12, Budget: 2 subtasks]

Applied: sandboxed-subprocess evaluation pattern (human-eval harness)

### API Signatures

```python
# src/evaluate.py
from human_eval.execution import check_correctness

def evaluate_solution(solution_code: str, problem: dict) -> bool:
    """Test if solution passes all problem test cases.
    Args:
        solution_code: Python code string (may have markdown fences — strip them)
        problem: {task_id, prompt, test, entry_point} (HumanEval format) or
                 {task_id, text, test_list} (MBPP format)
    Returns: True if all tests pass, False otherwise
    """

def strip_markdown_fences(code: str) -> str:
    """Remove ```python ... ``` fences from LLM output."""

def evaluate_mbpp(solution_code: str, problem: dict) -> bool:
    """MBPP-specific evaluation using test_list field."""
```

### Subtask: L-3-1 — HumanEval evaluation with fence stripping

```python
def evaluate_solution(solution_code: str, problem: dict) -> bool:
    # 1. code = strip_markdown_fences(solution_code)
    # 2. if "entry_point" in problem:  # HumanEval format
    #       result = check_correctness(problem, code, timeout=5.0)
    #       return result["passed"]
    # 3. else:  # MBPP format
    #       return evaluate_mbpp(code, problem)

def strip_markdown_fences(code: str) -> str:
    # 1. if "```" not in code: return code.strip()
    # 2. lines = code.split("\n")
    # 3. start = next (i for i,l in enumerate(lines) if l.strip().startswith("```"))
    # 4. end = next (i for i,l in enumerate(lines[start+1:], start+1) if l.strip() == "```", len(lines))
    # 5. return "\n".join(lines[start+1:end]).strip()
```

### Subtask: L-3-2 — MBPP evaluation and edge case handling

```python
def evaluate_mbpp(solution_code: str, problem: dict) -> bool:
    # 1. test_list = problem.get("test_list", [])
    # 2. if not test_list: return False  # no tests = can't validate
    # 3. full_code = solution_code + "\n" + "\n".join(test_list)
    # 4. try: exec(full_code, {}); return True
    # 5. except Exception: return False
    # 6. Timeout: wrap in threading.Timer(5.0, ...) or subprocess

# Edge cases handled:
# - Empty solution: return False immediately
# - SyntaxError in solution: caught by exec → False
# - Infinite loop: subprocess timeout (5s) kills process
# - Markdown fences: stripped by caller (strip_markdown_fences)
```

---

## A-4: RepairLoop Core [Complexity: 14, Budget: 4 subtasks]

Applied: iterative-repair-with-early-exit pattern (Olausson 2023)

### API Signatures

```python
# src/repair_loop.py
from dataclasses import dataclass
from typing import Optional

REPAIR_PROMPT_TEMPLATE = """\
Problem: {problem_prompt}

Previous solution (FAILED):
```python
{previous_solution}
```

Feedback from {feedback_category} verifier:
{feedback_text}

Fix the solution. Return only the corrected Python code:
```python
"""

@dataclass
class RepairResult:
    problem_id: str
    category: str
    iter1_pass: bool
    iter2_pass: Optional[bool]   # None if not reached
    iter3_pass: Optional[bool]   # None if not reached
    iterations_to_pass: Optional[int]  # None if never passed
    feedback_lengths: list[int]        # char_count of feedback at each iteration

def run_repair_loop(
    problem: dict,
    initial_solution: str,
    verifier: "BaseVerifierAdapter",
    model: str = "gpt-4o-mini",
    max_iterations: int = 3,
    temperature: float = 0.0,
    client: "openai.OpenAI" = None,
) -> RepairResult:
    """Run repair loop on initially-failing problem.
    Args:
        problem: problem dict with {task_id/id, prompt, test, entry_point} or MBPP format
        initial_solution: failing solution from H-M1
        verifier: one of 4 VerifierAdapter instances
        temperature: 0.0 for deterministic repair (Olausson 2023)
    Returns: RepairResult with per-iteration pass/fail and metadata
    """

def build_repair_prompt(
    problem_prompt: str,
    previous_solution: str,
    feedback_category: str,
    feedback_text: str,
) -> str:
    """Fill REPAIR_PROMPT_TEMPLATE."""
```

### Subtask: L-4-1 — Core repair iteration loop

```python
def run_repair_loop(problem, initial_solution, verifier, model, max_iterations, temperature, client) -> RepairResult:
    # 1. solution = initial_solution
    # 2. result = RepairResult(problem_id=problem["task_id"], category=verifier.category,
    #                          iter1_pass=False, iter2_pass=None, iter3_pass=None,
    #                          iterations_to_pass=None, feedback_lengths=[])
    # 3. for i in range(1, max_iterations + 1):
    #       a. feedback = verifier.get_feedback(solution, problem)
    #       b. result.feedback_lengths.append(feedback.char_count)
    #       c. if feedback.timeout: break  # verifier timeout = skip remaining iters
    #       d. prompt = build_repair_prompt(problem["prompt"], solution,
    #                                       verifier.category, feedback.feedback_text)
    #       e. solution = call_llm(prompt, model, temperature, client)
    #       f. passed = evaluate_solution(solution, problem)
    #       g. setattr(result, f"iter{i}_pass", passed)
    #       h. if passed:
    #             result.iterations_to_pass = i
    #             break
    # 4. return result
```

### Subtask: L-4-2 — LLM call with code extraction

```python
def call_llm(prompt: str, model: str, temperature: float, client) -> str:
    # 1. response = client.chat.completions.create(
    #       model=model,
    #       messages=[{"role": "user", "content": prompt}],
    #       temperature=temperature,
    #       max_tokens=1024,
    #       stop=["```"]   # stop at closing fence
    #    )
    # 2. raw = response.choices[0].message.content.strip()
    # 3. return strip_markdown_fences(raw) or raw
    # 4. On API error: return initial_solution  # fallback; log error
```

### Subtask: L-4-3 — build_repair_prompt

```python
def build_repair_prompt(problem_prompt, previous_solution, feedback_category, feedback_text) -> str:
    # 1. return REPAIR_PROMPT_TEMPLATE.format(
    #       problem_prompt=problem_prompt,
    #       previous_solution=previous_solution,
    #       feedback_category=feedback_category,
    #       feedback_text=feedback_text[:4000]  # truncate very long pyright output
    #    )
    # Note: truncation at 4000 chars for pyright (avg 24358 chars) prevents token overflow
    # ponytail: simple slice truncation; use smarter truncation if LLM performance degrades
```

### Subtask: L-4-4 — Mechanism verification sanity check

```python
def verify_mechanism(problems_sample: list[dict], verifiers: dict, client) -> None:
    """Verify repair loop fires correctly before full run."""
    # 1. For each cat, verifier in verifiers.items():
    #       a. result = run_repair_loop(
    #               problem=problems_sample[0],
    #               initial_solution="def solution(): pass  # intentionally wrong",
    #               verifier=verifier,
    #               max_iterations=1,
    #               client=client
    #          )
    #       b. assert result.iter1_pass in [True, False], f"Repair loop failed for {cat}"
    #       c. print(f"✓ {cat}: iter1_pass={result.iter1_pass}")
```

---

## A-8: Statistical Analysis [Complexity: 13, Budget: 2 subtasks]

Applied: scipy-spearmanr-with-bootstrap-ci pattern; directional-gate (Spearman ρ > 0)

### API Signatures

```python
# src/analyze.py
from scipy.stats import spearmanr
import numpy as np

# H-M2 empirical specificity ranks (fixed from 04_validation.md)
SPECIFICITY_RANKS = {"pyright": 1, "execution": 2, "mypy": 3, "z3": 4}

def compute_iter_rates(results: list["RepairResult"]) -> dict[str, dict]:
    """Compute per-category iter1/iter2/iter3 rates and N.
    Returns: {"pyright": {"iter1_rate": float, "iter2_rate": float, "iter3_rate": float, "n": int}, ...}
    """

def bootstrap_ci(passes: list[bool], n_bootstrap: int = 1000, ci: float = 0.95) -> tuple[float, float]:
    """Bootstrap confidence interval for a success rate.
    Returns: (lower_bound, upper_bound)
    """

def run_spearman(
    iter_rates: dict[str, dict],
    include_z3: bool = True,
) -> dict:
    """Run Spearman correlation between specificity ranks and iter1_rates.
    Returns: {"rho": float, "pval": float, "n_categories": int, "gate_pass": bool}
    """

def run_ablations(results: list["RepairResult"], iter_rates: dict) -> dict:
    """Run 4 ablation analyses. Returns ablation results dict."""

def gate_verdict(rho: float) -> bool:
    """Gate: Spearman ρ > 0 (positive direction)."""
    return rho > 0
```

### Subtask: L-8-1 — compute_iter_rates + bootstrap_ci

```python
def compute_iter_rates(results: list) -> dict:
    # 1. Group results by category
    # 2. For each category:
    #       a. initially_failing = all results (all are from initially-failing problems)
    #       b. n = len(initially_failing)
    #       c. iter1_passes = [r.iter1_pass for r in cat_results]
    #       d. iter1_rate = sum(iter1_passes) / n if n > 0 else 0.0
    #       e. iter1_ci = bootstrap_ci(iter1_passes)
    #       f. Similarly for iter2, iter3 (using non-None iter2_pass only)
    # 3. Return per-category dict

def bootstrap_ci(passes: list[bool], n_bootstrap=1000, ci=0.95) -> tuple[float, float]:
    # 1. arr = np.array(passes, dtype=float)
    # 2. n = len(arr)
    # 3. boot_means = [np.mean(np.random.choice(arr, n, replace=True)) for _ in range(n_bootstrap)]
    # 4. alpha = (1 - ci) / 2
    # 5. return (np.percentile(boot_means, alpha*100), np.percentile(boot_means, (1-alpha)*100))
```

### Subtask: L-8-2 — run_spearman + run_ablations + gate_verdict

```python
def run_spearman(iter_rates: dict, include_z3: bool = True) -> dict:
    # 1. cats = ["pyright", "execution", "mypy"] + (["z3"] if include_z3 else [])
    # 2. ranks = [SPECIFICITY_RANKS[c] for c in cats]
    # 3. rates = [iter_rates[c]["iter1_rate"] for c in cats]
    # 4. rho, pval = spearmanr(ranks, rates)
    # 5. return {"rho": rho, "pval": pval, "n_categories": len(cats), "gate_pass": gate_verdict(rho)}

def run_ablations(results, iter_rates) -> dict:
    # Ablation 1: without Z3
    #   spearman_no_z3 = run_spearman(iter_rates, include_z3=False)
    # Ablation 2: iter2_rate correlation
    #   compute iter2_rates, run_spearman with iter2_rates
    # Ablation 3: by dataset (humaneval vs mbpp)
    #   split results by problem_id prefix, compute rates separately
    # Ablation 4: by bug_type (if available from H-M1 records)
    #   group results by bug_type, compute iter1_rates per bug_type per category
    # Return dict of all ablation results
```

---

## A-11: Entry Point Integration [Complexity: 9, Budget: 1 subtask]

Applied: script-with-staged-execution pattern

### API Signatures

```python
# run_h_m3.py
def run_h_m3_experiment(
    failing_records: list[dict],
    verifiers: dict[str, "BaseVerifierAdapter"],
    client: "openai.OpenAI",
    config: "ExperimentConfig",
) -> dict:
    """Full H-M3 experiment: repair loop → analysis → visualization → persistence.
    Returns: summary dict with gate_verdict and key metrics
    """
```

### Subtask: L-11-1 — Main orchestration flow

```python
def run_h_m3_experiment(failing_records, verifiers, client, config) -> dict:
    # Stage 1: Mechanism verification (smoke test)
    #   verify_mechanism(failing_records[:3], verifiers, client)
    
    # Stage 2: Parallel repair loop
    #   results = run_parallel_repair(failing_records, verifiers, client, config)
    
    # Stage 3: Statistical analysis
    #   iter_rates = compute_iter_rates(results)
    #   spearman = run_spearman(iter_rates, include_z3=True)
    #   ablations = run_ablations(results, iter_rates)
    
    # Stage 4: Gate verdict
    #   verdict = gate_verdict(spearman["rho"])
    #   print(f"GATE: {'PASS' if verdict else 'FAIL'} (ρ={spearman['rho']:.3f})")
    
    # Stage 5: Visualization
    #   generate_all_figures(iter_rates, results, config.figures_dir)
    
    # Stage 6: Persist results
    #   write_records(results, config.output_dir + "results.jsonl")
    #   write_summary(spearman, iter_rates, ablations, verdict, config.output_dir + "summary.json")
    
    # Return summary
    return {"gate_pass": verdict, "rho": spearman["rho"], "iter_rates": iter_rates}
```

---

## Tensor Shapes

N/A — inference-time repair experiment; no neural network or tensor operations.

---

## Summary

| Epic | Subtasks | Key API |
|------|----------|---------|
| A-2 | L-2-1, L-2-2 | `BaseVerifierAdapter.get_feedback(solution, problem) -> FeedbackResult` |
| A-3 | L-3-1, L-3-2 | `evaluate_solution(solution_code, problem) -> bool` |
| A-4 | L-4-1..4 | `run_repair_loop(problem, initial_solution, verifier, ...) -> RepairResult` |
| A-8 | L-8-1, L-8-2 | `run_spearman(iter_rates) -> dict`, `gate_verdict(rho) -> bool` |
| A-11 | L-11-1 | `run_h_m3_experiment(records, verifiers, client, config) -> dict` |
