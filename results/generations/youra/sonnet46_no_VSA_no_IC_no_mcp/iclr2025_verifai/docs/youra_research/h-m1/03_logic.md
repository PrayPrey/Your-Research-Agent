---
hypothesis_id: H-M1
hypothesis_type: MECHANISM
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
base_hypothesis: H-E1
---

# Logic: H-M1 — Monotonic Mypy Error Reduction via Execution+Mypy Repair Loop

Applied: subprocess-tempfile pattern for static analysis integration
Applied: iterative-repair-loop with dual feedback channels
Applied: spearman-rank-correlation for monotonicity verification

> **Note**: Tensor shapes not applicable — this is a CLI pipeline experiment with no neural components.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 extension)
**Status**: H-E1 code analyzed via Read tool
**Analyzed Path**: `docs/youra_research/h-e1/code/pipeline.py`
**Relevant Symbols**:
- `run_mypy(code: str) -> tuple[bool, int]` — returns (has_error, error_count); H-M1 needs mypy_stdout too, so we extend the return signature
- `evaluate_solution(task_id: str, code: str, problem: dict) -> bool` — used as-is for exec feedback
- `generate_solution(client, problem, seed)` — used for initial generation
- `extract_code(response_text: str) -> str` — used after each repair generation
- `build_prompt(problem: dict) -> str` — used for initial prompt only

**Key Finding**: H-E1's `run_mypy` returns `(has_error, error_count)` as a 2-tuple. H-M1 needs the full mypy stdout for the repair prompt, so `repair_loop.py` calls `subprocess` directly (same flags) to get stdout as well, OR wraps `run_mypy` and does a second mypy pass to get stdout. Simpler: re-implement `run_mypy_with_output(code) -> tuple[bool, int, str]` in `repair_loop.py` that returns `(has_error, error_count, mypy_stdout)`.

---

## External Dependencies API

Verified from `docs/youra_research/h-e1/code/pipeline.py`:

```python
# H-E1 functions imported via sys.path into h-m1/code/pipeline.py

def evaluate_solution(task_id: str, code: str, problem: dict) -> bool:
    """Run EvalPlus test suite; return True=PASS."""
    ...

def run_mypy(code: str) -> tuple[bool, int]:
    """Return (has_error, error_count). Timeout -> (False, 0)."""
    ...

def generate_solution(client: OpenAI, problem: dict, seed: int) -> str:
    """Generate initial solution at temperature=0.8."""
    ...

def extract_code(response_text: str) -> str:
    """Strip markdown fences from LLM response."""
    ...

def build_prompt(problem: dict) -> str:
    """Build initial function completion prompt."""
    ...

def load_problems(benchmark: str) -> dict:
    """Load MBPP+ or HumanEval+ problem dict via evalplus."""
    ...
```

**Import pattern in h-m1/code/pipeline.py:**
```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code"))
from pipeline import (
    load_problems, build_prompt, extract_code,
    generate_solution, evaluate_solution, run_mypy,
    MYPY_FLAGS, MYPY_TIMEOUT,
)
```

---

## A-2: Repair Loop Core [Complexity: 16, Budget: 4 subtasks]

### API Signatures

```python
# repair_loop.py

def run_mypy_with_output(code: str, timeout: int = 10) -> tuple[bool, int, str]:
    """Run mypy; return (has_error, error_count, mypy_stdout)."""
    ...

def build_repair_prompt(
    problem: dict,
    prev_solution: str,
    exec_feedback: str,
    mypy_stdout: str,
) -> str:
    """Construct Condition B repair prompt with both feedback signals."""
    ...

def _generate_repair(
    client: OpenAI,
    prompt: str,
    max_tokens: int = 2048,
    max_retries: int = 3,
) -> str:
    """Call GPT-4o-mini at temperature=0.0 with backoff; return extracted code."""
    ...

def repair_loop_condition_b(
    client: OpenAI,
    task_id: str,
    problem: dict,
    seed: int = 42,
    k_max: int = 5,
) -> list[dict]:
    """Run k=1..5 repair rounds with execution+mypy feedback.

    Returns list of dicts per round:
      {"task_id": str, "benchmark": str, "round": int,
       "mypy_error_count": int, "mypy_stdout": str,
       "exec_passed": bool, "repaired": bool, "solution": str}
    Early-exits if exec_passed=True.
    """
    ...

def run_all_benchmarks(
    client: OpenAI,
    benchmarks: list[str],
    seed: int = 42,
    k_max: int = 5,
) -> list[dict]:
    """Run repair loop across all benchmarks; return flat record list."""
    ...
```

---

## L-A2-1: run_mypy_with_output() [Subtask 1/4]

### API Signature

```python
def run_mypy_with_output(code: str, timeout: int = 10) -> tuple[bool, int, str]:
    """
    Write code to tempfile, run mypy with standard H-E1 flags.
    Returns (has_error, error_count, mypy_stdout).
    Timeout or FileNotFoundError -> (False, 0, "").
    """
    ...
```

### Pseudo-code

```
MYPY_FLAGS = ["--ignore-missing-imports", "--no-strict-optional"]

def run_mypy_with_output(code, timeout=10):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp = f.name

        result = subprocess.run(
            ["mypy", *MYPY_FLAGS, tmp],
            capture_output=True, text=True, timeout=timeout,
        )
        error_lines = [l for l in result.stdout.splitlines() if "error:" in l]
        error_count = len(error_lines)
        has_error = result.returncode != 0
        return (has_error, error_count, result.stdout)

    except FileNotFoundError:
        raise  # caller (run.py) exits with install instructions

    except subprocess.TimeoutExpired:
        logging.warning(f"mypy timeout ({timeout}s) — counting as 0 errors")
        return (False, 0, "")

    finally:
        if tmp:
            pathlib.Path(tmp).unlink(missing_ok=True)
```

**Key invariants:**
- Always deletes tempfile (finally block)
- Returns stdout even on returncode=0 (for informational use)
- Timeout = 10s (reduced from H-E1's 30s for throughput at k=5 rounds)

---

## L-A2-2: build_repair_prompt() [Subtask 2/4]

### API Signature

```python
def build_repair_prompt(
    problem: dict,
    prev_solution: str,
    exec_feedback: str,
    mypy_stdout: str,
) -> str:
    """
    Construct Condition B repair prompt.
    Includes both execution feedback AND full mypy stdout.
    Returns prompt string ready for LLM.
    """
    ...
```

### Pseudo-code

```
def build_repair_prompt(problem, prev_solution, exec_feedback, mypy_stdout):
    problem_prompt = problem.get("prompt", problem.get("text", ""))

    parts = [
        f"Problem: {problem_prompt}",
        "",
        "Previous solution:",
        f"{prev_solution}",
        "",
        "Execution feedback:",
        f"{exec_feedback if exec_feedback else '(no execution output)'}",
        "",
        "Type checker (mypy) feedback:",
        f"{mypy_stdout if mypy_stdout else '(no mypy errors)'}",
        "",
        "Please fix the above errors and provide a corrected solution.",
    ]
    return "\n".join(parts)
```

**Key invariants:**
- Full `mypy_stdout` included, not just error count — LLM sees line numbers and error types
- `exec_feedback` is the test failure string from evaluate_solution (extract from EvalPlus result)
- Empty strings handled gracefully with placeholder text

---

## L-A2-3: _generate_repair() [Subtask 3/4]

### API Signature

```python
def _generate_repair(
    client: OpenAI,
    prompt: str,
    max_tokens: int = 2048,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> str:
    """
    Call GPT-4o-mini at temperature=0.0 with exponential backoff.
    Returns extracted code string.
    Raises RuntimeError after max_retries exhausted.
    """
    ...
```

### Pseudo-code

```
def _generate_repair(client, prompt, max_tokens=2048, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=max_tokens,
            )
            raw = response.choices[0].message.content
            return extract_code(raw)  # from H-E1 pipeline

        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM repair failed after {max_retries} attempts: {e}")
            delay = base_delay * (2 ** attempt)
            logging.warning(f"LLM error (attempt {attempt+1}): {e}. Retrying in {delay}s")
            time.sleep(delay)
```

**Key invariants:**
- temperature=0.0 (deterministic, unlike initial generation at 0.8)
- extract_code() applied to response to strip markdown fences
- No `seed` param needed (temperature=0.0 makes it effectively deterministic)

---

## L-A2-4: repair_loop_condition_b() + run_all_benchmarks() [Subtask 4/4]

### Pseudo-code: repair_loop_condition_b

```
def repair_loop_condition_b(client, task_id, problem, seed=42, k_max=5):
    records = []
    benchmark = "mbpp" if task_id.startswith("Mbpp") else "humaneval"

    # Initial generation (temperature=0.8, inherited from H-E1)
    initial_prompt = build_prompt(problem)
    solution = generate_solution(client, problem, seed)  # temp=0.8

    for k in range(1, k_max + 1):
        # Record mypy state BEFORE repair
        _, mypy_count, mypy_stdout = run_mypy_with_output(solution)
        logging.info(f"mypy_errors_round_{k}: {mypy_count}")  # activation indicator

        # Run EvalPlus evaluation
        exec_passed = evaluate_solution(task_id, solution, problem)
        # Get exec feedback string for repair prompt
        exec_feedback = "" if exec_passed else _get_exec_feedback(task_id, solution, problem)

        record = {
            "task_id": task_id,
            "benchmark": benchmark,
            "round": k,
            "mypy_error_count": mypy_count,
            "mypy_stdout": mypy_stdout,
            "exec_passed": exec_passed,
            "repaired": k > 1,
            "solution": solution,
        }
        records.append(record)

        if exec_passed:
            break  # early exit — no more repair needed

        if k < k_max:
            # Build repair prompt and generate next solution
            repair_prompt = build_repair_prompt(problem, solution, exec_feedback, mypy_stdout)
            solution = _generate_repair(client, repair_prompt)

    return records
```

### Pseudo-code: run_all_benchmarks

```
def run_all_benchmarks(client, benchmarks, seed=42, k_max=5):
    all_records = []
    for benchmark in benchmarks:
        problems = load_problems(benchmark)
        total = len(problems)
        for i, (task_id, problem) in enumerate(problems.items()):
            logging.info(f"[{benchmark}] {i+1}/{total}: {task_id}")
            try:
                records = repair_loop_condition_b(client, task_id, problem, seed, k_max)
                all_records.extend(records)
            except Exception as e:
                logging.error(f"Skipping {task_id}: {e}")
    return all_records
```

**Key invariants:**
- `logging.info(f"mypy_errors_round_{k}: {mypy_count}")` — required activation indicator log
- Early exit on `exec_passed=True` — records only rounds attempted
- Exception safety: log and skip on persistent LLM error (don't crash full run)
- `_get_exec_feedback` extracts test failure string from EvalPlus (may return "" if API doesn't expose it)

---

## A-4: Analysis Module [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# analysis.py

def compute_mean_errors_per_round(
    records: list[dict],
    benchmark: str,
    k_max: int = 5,
) -> dict[int, dict]:
    """Return {round_k: {"mean": float, "std": float, "n": int}}
    over problems with ≥1 mypy error at round 1 for the given benchmark."""
    ...

def compute_spearman(
    mean_errors_per_round: dict[int, dict],
) -> tuple[float, float]:
    """Return (rho, pval) from scipy.stats.spearmanr on mean error trajectory."""
    ...

def verify_mechanism_activated(
    records: list[dict],
    benchmark: str = "mbpp+",
) -> tuple[bool, dict]:
    """Return (activated, indicators). activated = log_found AND rho_negative."""
    ...

def aggregate_results(
    records: list[dict],
    k_max: int = 5,
) -> dict:
    """Return summary dict per benchmark: trajectory + spearman + gate."""
    ...
```

---

## L-A4-1: compute_mean_errors_per_round() + compute_spearman() [Subtask 1/2]

### Pseudo-code: compute_mean_errors_per_round

```
def compute_mean_errors_per_round(records, benchmark, k_max=5):
    # Filter to this benchmark
    bench_records = [r for r in records if r["benchmark"] == benchmark.replace("+", "")]

    # Find problems with ≥1 mypy error at round 1
    round1 = {r["task_id"]: r["mypy_error_count"]
               for r in bench_records if r["round"] == 1}
    eligible_tasks = {tid for tid, cnt in round1.items() if cnt > 0}

    result = {}
    for k in range(1, k_max + 1):
        # For early-exit problems: use 0 (exec passed, no errors remain)
        errors_at_k = []
        for task_id in eligible_tasks:
            k_records = [r for r in bench_records if r["task_id"] == task_id and r["round"] == k]
            if k_records:
                errors_at_k.append(k_records[0]["mypy_error_count"])
            else:
                errors_at_k.append(0)  # early exit = exec passed = 0 errors

        n = len(errors_at_k)
        mean = statistics.mean(errors_at_k) if n > 0 else 0.0
        std = statistics.stdev(errors_at_k) if n > 1 else 0.0
        result[k] = {"mean": mean, "std": std, "n": n}

    return result
```

### Pseudo-code: compute_spearman

```
from scipy.stats import spearmanr

def compute_spearman(mean_errors_per_round):
    rounds = sorted(mean_errors_per_round.keys())  # [1, 2, 3, 4, 5]
    means = [mean_errors_per_round[k]["mean"] for k in rounds]
    rho, pval = spearmanr(rounds, means)
    return float(rho), float(pval)
```

**Key invariants:**
- Only eligible tasks (mypy_error_count > 0 at round 1) included in analysis
- Early-exit problems (exec passed before round k) contribute 0 to round k mean
- `statistics.stdev` requires n > 1; guard against single-element lists

---

## L-A4-2: verify_mechanism_activated() + aggregate_results() [Subtask 2/2]

### Pseudo-code: verify_mechanism_activated

```
def verify_mechanism_activated(records, benchmark="mbpp+"):
    mean_errors = compute_mean_errors_per_round(records, benchmark)
    rho, pval = compute_spearman(mean_errors)

    # Check activation indicator logs exist
    rounds_found = set(r["round"] for r in records
                       if r["benchmark"] == benchmark.replace("+", ""))
    log_found = all(k in rounds_found for k in range(1, 6))

    indicators = {
        "log_found": log_found,
        "rho_negative": rho < 0,
        "round5_less_than_round1": (
            mean_errors.get(5, {}).get("mean", float("inf")) <
            mean_errors.get(1, {}).get("mean", 0.0)
        ),
        "rho": rho,
        "pval": pval,
    }
    activated = indicators["log_found"] and indicators["rho_negative"]
    return activated, indicators
```

### Pseudo-code: aggregate_results

```
def aggregate_results(records, k_max=5):
    summary = {}
    benchmarks = list(set(r["benchmark"] for r in records))
    for benchmark in benchmarks:
        mean_errors = compute_mean_errors_per_round(records, benchmark, k_max)
        rho, pval = compute_spearman(mean_errors)
        summary[benchmark] = {
            "n_problems": len(set(r["task_id"] for r in records
                                  if r["benchmark"] == benchmark)),
            "n_with_initial_mypy_errors": mean_errors.get(1, {}).get("n", 0),
            "mean_errors_by_round": {
                k: v for k, v in mean_errors.items()
            },
            "spearman_rho": rho,
            "p_value": pval,
            "round5_less_than_round1": (
                mean_errors.get(5, {}).get("mean", float("inf")) <
                mean_errors.get(1, {}).get("mean", 0.0)
            ),
            "gate_passed": rho < 0,
        }
    return summary
```

**Key invariants:**
- `gate_passed` = `rho < 0` on MBPP+ (primary gate)
- `benchmark` field in records stores "mbpp" or "humaneval" (without "+"); filtering accounts for this
- Returns summary keyed by raw benchmark string from records

---

## Subtasks [6/9 used — within logic budget]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A2-1 | run_mypy_with_output | Extended mypy wrapper returning stdout for repair prompt |
| L-A2-2 | build_repair_prompt | Condition B prompt with execution+mypy dual feedback |
| L-A2-3 | _generate_repair | GPT-4o-mini at temp=0.0 with exponential backoff |
| L-A2-4 | repair_loop_condition_b + run_all_benchmarks | Core repair loop + benchmark iterator |
| L-A4-1 | compute_mean_errors_per_round + compute_spearman | Per-round trajectory stats + Spearman ρ |
| L-A4-2 | verify_mechanism_activated + aggregate_results | Gate check + full summary aggregation |
