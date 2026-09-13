# Logic: H-E1 (Existence of Orthogonal Error Classes)

**Type:** EXISTENCE (PoC) | **Gate:** Mean Jaccard < 0.3

Applied: Standard PyTorch/stdlib — set-based error classification, no ML training.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## Data Structures

```python
from dataclasses import dataclass, field
from typing import Literal

ErrorSet = set[str]  # e.g. {"pylint:C0114", "mypy:Incompatible return..."}
Category = Literal["static_only", "exec_only", "both", "neither"]

@dataclass
class ProblemResult:
    problem_id: str
    benchmark: Literal["humaneval", "mbpp"]
    code: str
    static_errors: ErrorSet
    exec_errors: ErrorSet
    jaccard: float
    category: Category

@dataclass
class AnalysisResults:
    per_problem: list[ProblemResult] = field(default_factory=list)
    jaccard_scores: list[float] = field(default_factory=list)
    static_only: int = 0
    exec_only: int = 0
    both: int = 0
    neither: int = 0
    mean_jaccard: float = 0.0
    non_overlapping_pct: float = 0.0
```

---

## A-1: Dataset Loading [Complexity: 5]

**Applied**: evalplus standard loader

### API Signatures

```python
def load_problems() -> dict[str, dict]:
    """Load HumanEval+ (164) + MBPP+ (399) = 563 problems, tagged with 'benchmark' key."""
    ...

def get_benchmark(problem_id: str) -> str:
    """Return 'humaneval' if id starts with 'HumanEval/', else 'mbpp'."""
    ...
```

### Pseudo-code

```
1. he = get_human_eval_plus()
2. mb = get_mbpp_plus()
3. for pid in he: he[pid]["benchmark"] = "humaneval"
4. for pid in mb: mb[pid]["benchmark"] = "mbpp"
5. return {**he, **mb}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Load HumanEval+ | Call get_human_eval_plus() |
| L-1-2 | Load MBPP+ | Call get_mbpp_plus() |
| L-1-3 | Tag benchmark | Attach benchmark label per problem |
| L-1-4 | Merge | Combine into single 563-entry dict |

---

## A-2: Code Generation [Complexity: 9]

**Applied**: Seeded single-sample generation (pass@1)

### API Signatures

```python
def build_prompt(problem: dict) -> str:
    """Build prompt from problem['prompt'] (evalplus format)."""
    ...

def generate_code(problem: dict, model_name: str, seed: int = 42) -> str:
    """Generate one code completion. Returns full function source (prompt + completion)."""
    ...

def generate_all(problems: dict[str, dict], model_name: str, seed: int = 42) -> dict[str, str]:
    """Returns {problem_id: code_str} for all 563 problems."""
    ...
```

### Pseudo-code

```
1. for pid, problem in problems.items():
2.     prompt = build_prompt(problem)
3.     if backend == "openai": completion = openai_call(prompt, seed=seed, temperature=0)
4.     else: completion = hf_generate(prompt, seed=seed, do_sample=False)
5.     code[pid] = problem["prompt"] + completion
6. return code
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Prompt builder | Format problem into LLM prompt |
| L-2-2 | OpenAI backend | gpt-3.5-turbo call w/ seed, temp=0 |
| L-2-3 | HF backend | CodeLlama-7B-Instruct greedy decode |
| L-2-4 | Batch loop | generate_all over 563 problems, error-tolerant |

---

## A-3: Static Analysis Pipeline [Complexity: 8]

**Applied**: subprocess wrapper pattern

### API Signatures

```python
def run_pylint(code: str) -> set[str]:
    """Run pylint --output-format=json on code via stdin. Returns {'pylint:<message-id>', ...}."""
    ...

def run_mypy(code: str) -> set[str]:
    """Run mypy on code via stdin. Returns {'mypy:<truncated msg>', ...}."""
    ...

def run_static_analysis(code: str) -> set[str]:
    """Union of run_pylint(code) and run_mypy(code)."""
    ...
```

### Pseudo-code

```
run_pylint(code):
    result = subprocess.run(["pylint", "--output-format=json", "-"], input=code, text=True, capture_output=True, timeout=30)
    items = json.loads(result.stdout or "[]")
    return {f"pylint:{i['message-id']}" for i in items}

run_mypy(code):
    result = subprocess.run(["mypy", "--no-error-summary", "-"], input=code, text=True, capture_output=True, timeout=30)
    return {f"mypy:{line.split('error:')[1].strip()[:50]}" for line in result.stdout.splitlines() if "error:" in line}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | pylint wrapper | subprocess call + JSON parse |
| L-3-2 | mypy wrapper | subprocess call + line parse |
| L-3-3 | Union combiner | run_static_analysis merges both |
| L-3-4 | Timeout/error handling | Catch subprocess timeout/crash, return empty set |

---

## A-4: Execution Analysis Pipeline [Complexity: 8]

**Applied**: evalplus test execution

### API Signatures

```python
def run_execution_tests(problem_id: str, code: str, problem: dict) -> set[str]:
    """Run evalplus test suite for code. Returns failure-type set, e.g. {'exec:wrong_answer'}."""
    ...

def classify_outcome(exc: Exception | None, passed: bool, timed_out: bool) -> str:
    """Map raw execution result to one of: wrong_answer, runtime_error, timeout."""
    ...
```

### Pseudo-code

```
run_execution_tests(problem_id, code, problem):
    failures = set()
    for test_input in problem["base_input"] + problem["plus_input"]:
        try:
            result = execute_with_timeout(code, test_input, timeout=problem.get("timeout", 5))
            if result.timed_out: failures.add("exec:timeout")
            elif result.exception: failures.add("exec:runtime_error")
            elif not result.matches_expected: failures.add("exec:wrong_answer")
        except Exception:
            failures.add("exec:runtime_error")
    return failures
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Sandbox exec | Isolated subprocess/exec with timeout |
| L-4-2 | Outcome classify | Map result to wrong_answer/runtime_error/timeout |
| L-4-3 | evalplus test loading | Pull base+plus inputs per problem |
| L-4-4 | Aggregate | Collect unique failure-type set per problem |

---

## A-5: Jaccard + Categorization [Complexity: 4]

**Applied**: Standard set-similarity formula

### API Signatures

```python
def compute_jaccard(set_a: set[str], set_b: set[str]) -> float:
    """|A ∩ B| / |A ∪ B|. Returns 0.0 if both sets empty."""
    ...

def categorize(static_errors: set[str], exec_errors: set[str]) -> Category:
    """Returns 'static_only' | 'exec_only' | 'both' | 'neither'."""
    ...
```

### Pseudo-code

```
compute_jaccard(a, b):
    if not a and not b: return 0.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0

categorize(static_errors, exec_errors):
    if static_errors and exec_errors: return "both"
    if static_errors: return "static_only"
    if exec_errors: return "exec_only"
    return "neither"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Jaccard fn | Set intersection/union ratio |
| L-5-2 | Categorize fn | 4-way category classification |
| L-5-3 | Per-problem apply | Attach jaccard+category to ProblemResult |
| L-5-4 | Edge case: both empty | Return 0.0, category 'neither' |

---

## A-6: Full Pipeline Orchestration [Complexity: 7]

### API Signatures

```python
def analyze_error_orthogonality(problems: dict[str, dict], model_name: str, seed: int = 42) -> AnalysisResults:
    """Full pipeline: generate -> static -> exec -> jaccard -> aggregate, over all problems."""
    ...

def main() -> None:
    """Entry point: load_problems -> analyze_error_orthogonality -> evaluate_gate -> save results.json -> generate_all_figures."""
    ...
```

### Pseudo-code

```
analyze_error_orthogonality(problems, model_name, seed):
    results = AnalysisResults()
    for pid, problem in problems.items():
        code = generate_code(problem, model_name, seed)
        static_errors = run_static_analysis(code)
        exec_errors = run_execution_tests(pid, code, problem)
        jac = compute_jaccard(static_errors, exec_errors)
        cat = categorize(static_errors, exec_errors)
        results.per_problem.append(ProblemResult(pid, get_benchmark(pid), code, static_errors, exec_errors, jac, cat))
        results.jaccard_scores.append(jac)
        increment results.<cat> counter
    results.mean_jaccard = mean(results.jaccard_scores)
    results.non_overlapping_pct = (static_only + exec_only) / len(problems)
    return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Loop wiring | Sequential generate→static→exec→jaccard per problem |
| L-6-2 | Result accumulation | Append ProblemResult, increment counters |
| L-6-3 | Aggregate metrics | mean_jaccard, non_overlapping_pct |
| L-6-4 | Persist | Write results/results.json (dataclasses.asdict) |

---

## A-7: Gate Evaluation [Complexity: 3]

### API Signatures

```python
def evaluate_gate(results: AnalysisResults, jaccard_gate: float = 0.3, non_overlap_gate: float = 0.7) -> tuple[bool, str]:
    """Returns (gate_passed, message)."""
    ...
```

### Pseudo-code

```
evaluate_gate(results, jaccard_gate, non_overlap_gate):
    gate_passed = results.mean_jaccard < jaccard_gate
    msg = f"Jaccard={results.mean_jaccard:.3f} ({'PASS' if gate_passed else 'FAIL'})"
    if results.non_overlapping_pct >= non_overlap_gate:
        msg += f", Non-overlapping={results.non_overlapping_pct:.1%} (PASS)"
    return gate_passed, msg
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Gate check | mean_jaccard < 0.3 boolean |
| L-7-2 | Secondary check | non_overlapping_pct >= 0.7 |
| L-7-3 | Message format | Human-readable PASS/FAIL string |

---

## A-8: Visualization Suite [Complexity: 6]

### API Signatures

```python
def plot_gate_metrics(results: AnalysisResults, path: str, gate: float = 0.3) -> None:
    """Bar chart: threshold (0.3) vs actual mean_jaccard. REQUIRED figure."""
    ...

def plot_jaccard_histogram(results: AnalysisResults, path: str) -> None:
    """Histogram of results.jaccard_scores across 563 problems."""
    ...

def plot_error_venn(results: AnalysisResults, path: str) -> None:
    """Venn diagram: static-only / exec-only / both counts."""
    ...

def plot_category_breakdown(results: AnalysisResults, path: str) -> None:
    """Stacked bar: static_only, exec_only, both, neither counts."""
    ...

def plot_per_benchmark(results: AnalysisResults, path: str) -> None:
    """Jaccard distribution split by benchmark (humaneval vs mbpp)."""
    ...

def generate_all_figures(results: AnalysisResults, figures_dir: str) -> None:
    """Call all 5 plot functions, save to figures_dir."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Gate bar chart | Required: threshold vs actual |
| L-8-2 | Histogram + Venn | Distribution + overlap visuals |
| L-8-3 | Category + per-benchmark | Stacked bar + split comparison |
| L-8-4 | generate_all_figures | Orchestrate + save all to figures/ |
