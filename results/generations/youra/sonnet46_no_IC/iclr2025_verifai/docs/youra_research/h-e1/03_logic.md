---
title: "Logic: H-E1 Pylint/Mypy Iterative Repair PoC"
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
phase: 3
date: "2026-08-05"
status: complete
budget: 7 subtasks (E-4: 4, E-5: 3)
---

# Logic: H-E1

Applied: token-budget-bounded repair loop pattern (Johin2/iterative-code-repair)
Applied: incremental JSONL write with resume-by-task_id pattern (standard eval harness)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase to analyze — new experiment from scratch
**Analyzed Path**: N/A
**Findings**: All API designs sourced from Phase 2C reference implementations (Johin2/iterative-code-repair, cyb3rlab/CodeEnhancer, NEUIR/INTERVENOR). No local symbols to verify.

---

## Epic E-4: Repair Loop (`repair_loop.py`)

### L-4-1: `count_tokens()` — Token Counter

```python
def count_tokens(text: str) -> int:
    """
    Estimate output token count for budget tracking.
    
    Uses word-split approximation (4 chars ≈ 1 token) sufficient for budget
    enforcement; exact tokenizer not required since B=1000 is a soft ceiling.
    Groq API returns usage.completion_tokens — prefer that when available.
    
    Args:
        text: Generated code string from LLM
    Returns:
        Approximate token count (int ≥ 0)
    """
    # pseudo-code
    if text is None or text == "":
        return 0
    # Approximation: avg 4 chars per token (standard for code)
    return max(1, len(text) // 4)
```

**Invariants:**
- Never returns negative
- Returns 0 for empty string
- Caller (ModelClient.generate) should prefer Groq's `usage.completion_tokens` over this estimate

**Edge cases:**
- Very short code (1-2 lines): may undercount — acceptable since min_remaining=100 guards
- Unicode/non-ASCII: char-based approximation still safe (overestimates slightly)

---

### L-4-2: `build_repair_prompt()` — Repair Prompt Constructor

```python
INITIAL_PROMPT_TEMPLATE = """\
Complete the following Python function:

{problem_prompt}

Return only the function code, no explanation."""

REPAIR_PROMPT_TEMPLATE = """\
The following Python code has static analysis issues:

```python
{previous_code}
```

Static analysis feedback:
{pylint_mypy_output}

Please fix the code to address these issues while maintaining functional correctness.
Return only the corrected function, no explanation."""


def build_initial_prompt(problem: dict, benchmark: str) -> str:
    """
    Build Round 0 generation prompt for a problem.
    
    Args:
        problem: Problem dict {prompt/text, entry_point, ...}
        benchmark: "humaneval" | "mbpp"
    Returns:
        Formatted prompt string for LLM
    """
    # pseudo-code
    if benchmark == "humaneval":
        return INITIAL_PROMPT_TEMPLATE.format(problem_prompt=problem["prompt"])
    else:  # mbpp
        return INITIAL_PROMPT_TEMPLATE.format(problem_prompt=problem["text"])


def build_repair_prompt(previous_code: str, feedback: str) -> str:
    """
    Build repair prompt from code + pylint/mypy feedback.
    
    Args:
        previous_code: Code from previous round (already extracted, no fences)
        feedback: Formatted pylint/mypy output string (non-empty)
    Returns:
        Formatted repair prompt string
    """
    return REPAIR_PROMPT_TEMPLATE.format(
        previous_code=previous_code,
        pylint_mypy_output=feedback
    )
```

**Invariants:**
- `build_repair_prompt` only called when feedback is non-None/non-empty
- `previous_code` passed in already stripped of markdown fences (done by `extract_code`)

---

### L-4-3: `pylint_repair_loop()` — Main Repair Loop

```python
from dataclasses import dataclass, field

@dataclass
class RoundResult:
    round_num: int
    code: str
    tokens_generated: int
    passed: bool
    feedback_given: str | None  # None for round 0 (no feedback yet)


def pylint_repair_loop(
    problem: dict,
    benchmark: str,            # "humaneval" | "mbpp"
    client: "ModelClient",
    executor_fn: callable,     # execute_humaneval or execute_mbpp
    analyzer: "StaticAnalyzer",
    B: int = 1000,
    max_rounds: int = 3,
    min_remaining: int = 100,
) -> dict:
    """
    Iterative pylint/mypy repair loop within token budget B.
    
    Generates initial solution (round 0), then repairs up to max_rounds times
    using pylint/mypy feedback, stopping when: budget exhausted, no issues found,
    or max_rounds reached.
    
    Args:
        problem: Problem dict from load_humaneval() or load_mbpp()
        benchmark: "humaneval" | "mbpp" — controls prompt template + executor
        client: ModelClient with generate() method
        executor_fn: Function(code, problem_or_tests) -> bool
        analyzer: StaticAnalyzer with run_pylint_mypy() method
        B: Total output token budget per problem
        max_rounds: Maximum repair iterations (default 3)
        min_remaining: Skip repair if remaining tokens < this threshold
    
    Returns:
        {
            "task_id": str,
            "condition": "pylint",
            "final_code": str,
            "passed": bool,
            "tokens_used": int,
            "rounds_completed": int,
            "round_results": list[RoundResult as dict]
        }
    """
    # pseudo-code
    tokens_used = 0
    round_results = []
    
    # Round 0: initial generation
    initial_prompt = build_initial_prompt(problem, benchmark)
    code, tokens = client.generate(initial_prompt, max_tokens=min(B, 512))
    code = extract_code(code, problem.get("entry_point"))
    tokens_used += tokens
    passed = executor_fn(code, problem)
    
    round_results.append(RoundResult(
        round_num=0, code=code, tokens_generated=tokens,
        passed=passed, feedback_given=None
    ))
    
    # Repair rounds 1..max_rounds
    for repair_round in range(1, max_rounds + 1):
        remaining = B - tokens_used
        if remaining < min_remaining:
            break  # budget exhausted
        
        feedback = analyzer.run_pylint_mypy(code)
        if feedback is None:
            break  # no static issues — early exit
        
        repair_prompt = build_repair_prompt(code, feedback)
        repaired_code, tokens = client.generate(repair_prompt, max_tokens=remaining)
        repaired_code = extract_code(repaired_code, problem.get("entry_point"))
        tokens_used += tokens
        code = repaired_code
        passed = executor_fn(code, problem)
        
        round_results.append(RoundResult(
            round_num=repair_round, code=code, tokens_generated=tokens,
            passed=passed, feedback_given=feedback
        ))
    
    return {
        "task_id": problem.get("task_id", problem.get("task_id")),
        "condition": "pylint",
        "final_code": code,
        "passed": passed,
        "tokens_used": tokens_used,
        "rounds_completed": len(round_results) - 1,  # excludes round 0
        "round_results": [vars(r) for r in round_results]
    }
```

**Invariants:**
- Always completes at least round 0 (initial generation)
- `tokens_used` never exceeds B + one round's tokens (can slightly exceed B on last round — acceptable)
- `feedback_given` is None for round 0, non-None for repair rounds
- Early exit on no issues means pylint repair can terminate in 0 repair rounds

**Edge cases:**
- `extract_code` fails (no valid code): return raw output, mark passed=False
- `client.generate` raises exception: propagate up; caller (run_pylint_condition) catches and logs

---

### L-4-4: `RoundResult` Dataclass

```python
from dataclasses import dataclass

@dataclass
class RoundResult:
    """Per-round data for iterative repair tracking."""
    round_num: int           # 0 = initial, 1..3 = repair rounds
    code: str                # Extracted code at end of this round
    tokens_generated: int    # Tokens used in this round's generation
    passed: bool             # Whether final_code passes all tests
    feedback_given: str | None  # Pylint/mypy feedback that triggered this repair
                                # None for round_num == 0
    
    def as_dict(self) -> dict:
        return {
            "round_num": self.round_num,
            "code": self.code,
            "tokens_generated": self.tokens_generated,
            "passed": self.passed,
            "feedback_given": self.feedback_given,
        }
```

**Serialization:** `vars(round_result)` or `round_result.as_dict()` → JSON-serializable dict for JSONL output

---

## Epic E-5: Evaluator + Results (`evaluator.py`)

### L-5-1: `run_baseline_condition()` — Baseline Evaluator

```python
def run_baseline_condition(
    problems: dict,
    benchmark: str,
    client: "ModelClient",
    output_path: str,
    resume: bool = True,
) -> list[dict]:
    """
    Run single-shot baseline generation for all problems in a benchmark.
    
    Writes results incrementally to {output_path}/baseline_{benchmark}.jsonl.
    If resume=True, loads existing results and skips already-completed task_ids.
    
    Args:
        problems: Dict {task_id -> problem_dict} from load_humaneval/load_mbpp
        benchmark: "humaneval" | "mbpp"
        client: ModelClient
        output_path: Directory for JSONL output (e.g., "results/")
        resume: If True, skip task_ids already in output file
    
    Returns:
        List of result dicts:
        [{task_id, condition="baseline", benchmark, passed, code, tokens_used}]
    """
    # pseudo-code
    out_file = f"{output_path}/baseline_{benchmark}.jsonl"
    
    # Load existing if resume
    completed_ids = set()
    existing_results = []
    if resume and os.path.exists(out_file):
        with open(out_file) as f:
            for line in f:
                r = json.loads(line)
                completed_ids.add(r["task_id"])
                existing_results.append(r)
    
    results = existing_results.copy()
    executor_fn = get_executor(benchmark)  # execute_humaneval or execute_mbpp
    
    with open(out_file, "a") as f:
        for task_id, problem in tqdm(problems.items(), desc=f"Baseline {benchmark}"):
            if task_id in completed_ids:
                continue
            
            prompt = build_initial_prompt(problem, benchmark)
            code_raw, tokens = client.generate(prompt, max_tokens=512)
            code = extract_code(code_raw, problem.get("entry_point"))
            passed = executor_fn(code, problem)
            
            result = {
                "task_id": task_id,
                "condition": "baseline",
                "benchmark": benchmark,
                "passed": passed,
                "code": code,
                "tokens_used": tokens,
            }
            results.append(result)
            f.write(json.dumps(result) + "\n")
            f.flush()
    
    return results
```

**Invariants:**
- Output file written atomically per-line (flush after each write)
- Resume never re-runs completed task_ids
- All 164 (HumanEval) or 374 (MBPP) problems processed — no subset

---

### L-5-2: `run_pylint_condition()` — Pylint Repair Evaluator

```python
def run_pylint_condition(
    problems: dict,
    benchmark: str,
    client: "ModelClient",
    analyzer: "StaticAnalyzer",
    output_path: str,
    B: int = 1000,
    max_rounds: int = 3,
    resume: bool = True,
) -> list[dict]:
    """
    Run pylint/mypy iterative repair condition for all problems.
    
    Calls pylint_repair_loop() per problem, writes full round_results to JSONL.
    
    Args:
        problems: Problem dict
        benchmark: "humaneval" | "mbpp"
        client: ModelClient
        analyzer: StaticAnalyzer
        output_path: Results directory
        B: Token budget per problem
        max_rounds: Max repair rounds
        resume: Skip completed task_ids
    
    Returns:
        List of result dicts with full round_results per problem
    """
    # pseudo-code (mirrors run_baseline_condition with repair loop)
    out_file = f"{output_path}/pylint_{benchmark}.jsonl"
    
    completed_ids = set()
    existing_results = []
    if resume and os.path.exists(out_file):
        with open(out_file) as f:
            for line in f:
                r = json.loads(line)
                completed_ids.add(r["task_id"])
                existing_results.append(r)
    
    results = existing_results.copy()
    executor_fn = get_executor(benchmark)
    
    with open(out_file, "a") as f:
        for task_id, problem in tqdm(problems.items(), desc=f"Pylint {benchmark}"):
            if task_id in completed_ids:
                continue
            try:
                result = pylint_repair_loop(
                    problem, benchmark, client, executor_fn, analyzer,
                    B=B, max_rounds=max_rounds
                )
                result["benchmark"] = benchmark
                result["task_id"] = task_id
            except Exception as e:
                result = {
                    "task_id": task_id, "benchmark": benchmark,
                    "condition": "pylint", "passed": False,
                    "error": str(e), "tokens_used": 0, "rounds_completed": 0,
                    "round_results": []
                }
            results.append(result)
            f.write(json.dumps(result) + "\n")
            f.flush()
    
    return results
```

**Invariants:**
- Exceptions per-problem are caught and logged (never crash the full run)
- All 538 problems processed regardless of individual failures

---

### L-5-3: `compute_metrics()` — Metrics Aggregator

```python
def compute_metrics(
    baseline_he: list[dict],
    baseline_mbpp: list[dict],
    pylint_he: list[dict],
    pylint_mbpp: list[dict],
) -> dict:
    """
    Compute all primary and secondary metrics from condition results.
    
    Args:
        baseline_he: Results from run_baseline_condition(..., "humaneval")
        baseline_mbpp: Results from run_baseline_condition(..., "mbpp")
        pylint_he: Results from run_pylint_condition(..., "humaneval")
        pylint_mbpp: Results from run_pylint_condition(..., "mbpp")
    
    Returns:
        MetricsDict with all fields required by FR-3
    """
    # pseudo-code
    
    def pass_at_1(results: list[dict]) -> float:
        if not results:
            return float("nan")
        return sum(r["passed"] for r in results) / len(results)
    
    def per_round_pass_at_1(results: list[dict]) -> dict[int, float]:
        """pass@1 at each round (0..3) across all problems."""
        round_passes = {}
        for r in results:
            for rr in r.get("round_results", []):
                rn = rr["round_num"]
                if rn not in round_passes:
                    round_passes[rn] = []
                round_passes[rn].append(rr["passed"])
        return {rn: sum(v)/len(v) for rn, v in round_passes.items()}
    
    def pylint_coverage_fraction(baseline_results: list[dict], pylint_results: list[dict]) -> dict:
        """Fraction of baseline failures that got ≥1 pylint issue in round 1 feedback."""
        failed_ids = {r["task_id"] for r in baseline_results if not r["passed"]}
        flagged = 0
        total_failures = len(failed_ids)
        for r in pylint_results:
            if r["task_id"] not in failed_ids:
                continue
            # check if round 1 had any feedback
            round_results = r.get("round_results", [])
            if len(round_results) > 1 and round_results[1].get("feedback_given"):
                flagged += 1
        coverage = flagged / total_failures if total_failures > 0 else 0.0
        return {"humaneval_coverage": coverage, "total_failures": total_failures, "flagged": flagged}
    
    p1_base_he = pass_at_1(baseline_he)
    p1_base_mbpp = pass_at_1(baseline_mbpp)
    p1_pylint_he = pass_at_1(pylint_he)
    p1_pylint_mbpp = pass_at_1(pylint_mbpp)
    
    metrics = {
        "pass_at_1_baseline_humaneval": p1_base_he,
        "pass_at_1_baseline_mbpp": p1_base_mbpp,
        "pass_at_1_pylint_humaneval": p1_pylint_he,
        "pass_at_1_pylint_mbpp": p1_pylint_mbpp,
        "delta_pylint_humaneval": p1_pylint_he - p1_base_he,
        "delta_pylint_mbpp": p1_pylint_mbpp - p1_base_mbpp,
        "per_round_pass_at_1_humaneval": per_round_pass_at_1(pylint_he),
        "per_round_pass_at_1_mbpp": per_round_pass_at_1(pylint_mbpp),
        "pylint_coverage": pylint_coverage_fraction(baseline_he, pylint_he),
        "token_budget_distribution_humaneval": [r.get("tokens_used", 0) for r in pylint_he],
        "token_budget_distribution_mbpp": [r.get("tokens_used", 0) for r in pylint_mbpp],
        "n_humaneval": len(baseline_he),
        "n_mbpp": len(baseline_mbpp),
    }
    return metrics
```

**Output shape:**
```python
MetricsDict = {
    "pass_at_1_baseline_humaneval": float,   # ~0.671 expected
    "pass_at_1_baseline_mbpp": float,        # ~0.556 expected
    "pass_at_1_pylint_humaneval": float,     # unknown
    "pass_at_1_pylint_mbpp": float,          # unknown
    "delta_pylint_humaneval": float,         # primary metric: Δ_pylint
    "delta_pylint_mbpp": float,              # primary metric: Δ_pylint
    "per_round_pass_at_1_humaneval": {0: float, 1: float, 2: float, 3: float},
    "per_round_pass_at_1_mbpp": {0: float, 1: float, 2: float, 3: float},
    "pylint_coverage": {"humaneval_coverage": float, "total_failures": int, "flagged": int},
    "token_budget_distribution_humaneval": list[int],   # one per problem
    "token_budget_distribution_mbpp": list[int],
    "n_humaneval": 164,
    "n_mbpp": 374,
}
```

**Invariants:**
- `delta_pylint_*` is always finite if both pass@1 values are finite
- `per_round_pass_at_1` has round 0 for all problems (always run)
- PoC gate: `delta_pylint_humaneval` and `delta_pylint_mbpp` must both be non-NaN

---

## Data Shapes Summary

| Object | Type | Shape/Schema |
|--------|------|-------------|
| HumanEval problems | dict | {task_id → {prompt, canonical_solution, test, entry_point}} |
| MBPP problems | dict | {task_id → {text, code, test_list, test_setup_code}} |
| Baseline result | dict | {task_id, condition, benchmark, passed, code, tokens_used} |
| Pylint result | dict | {task_id, condition, benchmark, passed, final_code, tokens_used, rounds_completed, round_results} |
| RoundResult | dict | {round_num, code, tokens_generated, passed, feedback_given} |
| MetricsDict | dict | See L-5-3 output shape above |
| JSONL line | str | json.dumps(result) + "\n" |

---

## Key Invariants (Cross-Module)

1. `task_id` is the join key between baseline and pylint results — must match exactly
2. `passed` field computed at time of each round — not re-evaluated later
3. `extract_code()` applied to ALL LLM outputs before any evaluation or feedback generation
4. Token budget `B=1000` applies to TOTAL output tokens per problem (cumulative across rounds)
5. All 538 problems (164 HE + 374 MBPP) must appear in output JSONL — no skipping on error
