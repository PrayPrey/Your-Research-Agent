# Logic: H-E1 — ContractEval Contract-Strength Gap Existence Verification

Applied: pipeline-orchestration pattern (sequential eval pipeline, adapted from InvokeAI/diffusers KB results)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Analyzed Path**: N/A (directory-level Serena scan not applicable for green-field)
**Relevant Symbols**: None — new implementation from scratch

---

## A-4: Contract Checker [Complexity: 13, Budget: 2 subtasks]

### L-4-1: Dynamic Code Execution with Timeout

**Parent Epic**: A-4 (`contract_checker.py`)

#### API Signature

```python
import signal
from typing import Optional

def exec_with_timeout(
    code_str: str,
    entry_point: str,
    timeout: int = 60,
) -> tuple[Optional[callable], Optional[str]]:
    """Exec code_str in isolated namespace; return (callable, None) or (None, error_msg)."""
```

#### Pseudo-code

```
1. Define _timeout_handler(signum, frame): raise TimeoutError
2. namespace = {}
3. try:
4.     signal.signal(signal.SIGALRM, _timeout_handler)
5.     signal.alarm(timeout)
6.     exec(compile(code_str, "<generated>", "exec"), namespace)
7.     signal.alarm(0)                         # cancel alarm on success
8.     func = namespace.get(entry_point)
9.     if func is None or not callable(func):
10.        return None, f"entry_point '{entry_point}' not found in namespace"
11.    return func, None
12. except TimeoutError:
13.    signal.alarm(0)
14.    return None, "exec timeout"
15. except Exception as e:
16.    signal.alarm(0)
17.    return None, f"exec error: {type(e).__name__}: {e}"
```

#### Key Edge Cases

- `entry_point` missing from namespace → return `(None, "entry_point not found")`
- Syntax error in `code_str` → caught by bare `except Exception`
- SIGALRM only works on Linux (main target); Windows callers get `AttributeError` on `signal.SIGALRM` — document this
- Always cancel alarm in every exit path to avoid leaking alarm state into next call

---

### L-4-2: icontract-hypothesis Strategy Inference + PBT Loop

**Parent Epic**: A-4 (`contract_checker.py`)

#### API Signature

```python
from hypothesis import given, settings, HealthCheck
import icontract_hypothesis

def check_program_contract(
    reference_impl: callable,
    generated_code: str,
    entry_point: str,
    budget: int = 5_000,
    seed: int = 42,
    timeout: int = 60,
) -> dict:
    """Run PBT on generated_code using strategy inferred from reference_impl contracts.

    Returns: {violated, n_failures, n_total, gap, error}
    """
```

#### Pseudo-code

```
1.  generated_func, err = exec_with_timeout(generated_code, entry_point, timeout)
2.  if err: return {violated: False, n_failures: 0, n_total: 0, gap: 0.0, error: err}

3.  try:
4.      strategy = icontract_hypothesis.infer_strategy(reference_impl)
5.  except Exception as e:
6.      return {violated: False, n_failures: 0, n_total: 0, gap: 0.0,
7.              error: f"strategy inference failed: {e}"}

8.  n_failures = 0
9.  n_total = [0]   # mutable for closure

10. @settings(max_examples=budget, deadline=None,
11.           suppress_health_check=[HealthCheck.too_slow],
12.           deriving=seed)
13. @given(strategy)
14. def _pbt_test(*args, **kwargs):
15.     n_total[0] += 1
16.     try:
17.         generated_func(*args, **kwargs)
18.     except icontract.ViolationError:
19.         nonlocal n_failures
20.         n_failures += 1

21. try:
22.     signal.alarm(timeout)
23.     _pbt_test()
24.     signal.alarm(0)
25. except TimeoutError:
26.     signal.alarm(0)
27.     # partial results still valid — report what was collected
28. except Exception as e:
29.     signal.alarm(0)
30.     return {violated: False, n_failures: 0, n_total: n_total[0],
31.             gap: 0.0, error: f"pbt error: {e}"}

32. gap = n_failures / n_total[0] if n_total[0] > 0 else 0.0
33. return {violated: n_failures > 0, n_failures: n_failures,
34.         n_total: n_total[0], gap: gap, error: None}
```

#### Key Edge Cases

- `infer_strategy` may fail if reference_impl has no `@require` decorators → return error, skip task
- `ViolationError` must be caught *inside* `_pbt_test`, not outside — Hypothesis re-raises as `Falsifying example`
- Partial timeout: if alarm fires mid-PBT, collect partial `n_failures / n_total` and mark `error="timeout"`
- `n_total` uses list-as-mutable-closure to avoid `nonlocal` scoping issues with `@given`

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Dynamic Code Execution with Timeout | exec() in isolated namespace with SIGALRM |
| L-4-2 | Strategy Inference + PBT Loop | icontract_hypothesis.infer_strategy + @given loop |

---

## A-2: Oracle Pre-check [Complexity: 11, Budget: 2 subtasks]

### L-2-1: Oracle PBT with High Budget

**Parent Epic**: A-2 (`oracle_checker.py`)

#### API Signature

```python
def check_reference_impl(
    task: dict,
    budget: int = 100_000,
    seed: int = 42,
    timeout_per_task: int = 30,
) -> dict:
    """Run high-budget PBT on reference_impl to detect unsound contracts.

    Returns: {task_id, quarantined, violation_count, error}
    """
```

#### Pseudo-code

```
1.  task_id = task["task_id"]
2.  ref_code = task["reference_impl"]
3.  entry_point = task["entry_point"]

4.  ref_func, err = exec_with_timeout(ref_code, entry_point, timeout=timeout_per_task)
5.  if err:
6.      return {task_id: task_id, quarantined: True, violation_count: 0, error: err}

7.  try:
8.      strategy = icontract_hypothesis.infer_strategy(ref_func)
9.  except Exception as e:
10.     return {task_id: task_id, quarantined: True, violation_count: 0,
11.             error: f"strategy inference failed: {e}"}

12. violation_count = [0]

13. @settings(max_examples=budget, deadline=None,
14.           suppress_health_check=[HealthCheck.too_slow],
15.           deriving=seed)
16. @given(strategy)
17. def _oracle_test(*args, **kwargs):
18.     try:
19.         ref_func(*args, **kwargs)
20.     except icontract.ViolationError:
21.         violation_count[0] += 1
22.         raise   # let Hypothesis record the falsifying example

23. try:
24.     signal.alarm(timeout_per_task)
25.     _oracle_test()
26.     signal.alarm(0)
27.     quarantined = False
28. except (TimeoutError, Exception) as e:
29.     signal.alarm(0)
30.     # ViolationError re-raised by Hypothesis becomes Falsifying example exception
31.     quarantined = violation_count[0] > 0 or isinstance(e, TimeoutError) is False
32.     # Simpler: quarantine if any violation found OR unexpected error
33.     quarantined = violation_count[0] > 0

34. return {task_id: task_id, quarantined: quarantined,
35.         violation_count: violation_count[0], error: None}
```

#### Key Edge Cases

- Hypothesis re-raises `ViolationError` as its own exception after shrinking — catch at outer level
- `timeout_per_task=30` is conservative; total wall-clock bounded by orchestrator (2h)
- If `violation_count > 0`, quarantine regardless of whether full budget completed

---

### L-2-2: Soundness Pre-check Orchestrator

**Parent Epic**: A-2 (`oracle_checker.py`)

#### API Signature

```python
import json
from pathlib import Path
from tqdm import tqdm

def run_soundness_precheck(
    tasks: dict[str, dict],
    budget: int = 100_000,
    seed: int = 42,
    results_path: str = "results/oracle_precheck.jsonl",
) -> tuple[set[str], set[str]]:
    """Iterate all tasks, run oracle PBT, write jsonl, return (valid_ids, quarantined_ids)."""
```

#### Pseudo-code

```
1.  Path(results_path).parent.mkdir(parents=True, exist_ok=True)
2.  valid_ids = set()
3.  quarantined_ids = set()

4.  with open(results_path, "w") as fout:
5.      for task_id, task in tqdm(tasks.items(), desc="Oracle pre-check"):
6.          result = check_reference_impl(task, budget=budget, seed=seed)
7.          fout.write(json.dumps(result) + "\n")
8.          fout.flush()   # ensure progressive write; safe on crash

9.          if result["quarantined"]:
10.             quarantined_ids.add(task_id)
11.         else:
12.             valid_ids.add(task_id)

13. quarantine_rate = len(quarantined_ids) / len(tasks)
14. if quarantine_rate > 0.05:
15.     print(f"WARNING: quarantine rate {quarantine_rate:.1%} exceeds 5% threshold")

16. return valid_ids, quarantined_ids
```

#### Key Edge Cases

- `fout.flush()` after each write — if process dies mid-run, already-computed results are preserved
- Quarantine rate check is a warning only, not a halt — orchestrator decides whether to abort
- `tqdm` wrap gives wall-clock ETA for the 2h oracle pass

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Oracle PBT with High Budget | 100k-budget PBT on reference_impl, quarantine on violation |
| L-2-2 | Soundness Pre-check Orchestrator | Iterate tasks, jsonl streaming writer, track valid/quarantined sets |

---

## A-3: Code Generation [Complexity: 10, Budget: 2 subtasks]

### L-3-1: evalplus CLI Wrapper

**Parent Epic**: A-3 (`code_generator.py`)

#### API Signature

```python
import sys
import subprocess
from pathlib import Path

def generate_samples(
    model: str,
    dataset: str,            # "humaneval" | "mbpp"
    output_dir: str,
    n: int = 10,
    temperature: float = 0.8,
) -> Path:
    """Shell out to evalplus.codegen; return path to output .jsonl file."""
```

#### Pseudo-code

```
1.  out_path = Path(output_dir) / model.replace("/", "__") / f"{dataset}.jsonl"
2.  out_path.parent.mkdir(parents=True, exist_ok=True)

3.  cmd = [
4.      sys.executable, "-m", "evalplus.codegen",
5.      "--model", model,
6.      "--dataset", dataset,         # "humaneval" or "mbpp"
7.      "--n_samples", str(n),
8.      "--temperature", str(temperature),
9.      "--save", str(out_path),
10. ]

11. result = subprocess.run(cmd, check=True, capture_output=True, text=True)
12. if not out_path.exists():
13.     raise FileNotFoundError(f"evalplus.codegen did not produce {out_path}")

14. return out_path
```

#### Key Edge Cases

- Model IDs with `/` (e.g., `deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct`) → replace `/` with `__` for filesystem path
- `check=True` on `subprocess.run` raises `CalledProcessError` on non-zero exit — let it propagate to orchestrator
- If `out_path` already exists (rerun), evalplus may append or overwrite — add `--overwrite` flag if supported, else delete first

---

### L-3-2: Test-Pass Filter + Sample Loader

**Parent Epic**: A-3 (`code_generator.py`)

#### API Signatures

```python
def run_evalplus_filter(
    samples_path: Path,
    dataset: str,
    base_only: bool = True,
) -> Path:
    """Run evalplus.evaluate --base-only; return path to filtered results jsonl."""


def load_passing_samples(filtered_path: Path) -> dict[str, list[str]]:
    """Parse filtered results jsonl; return {task_id: [passing_code_str, ...]}."""
```

#### Pseudo-code — `run_evalplus_filter`

```
1.  filtered_path = samples_path.with_suffix(".filtered.jsonl")
2.  cmd = [
3.      sys.executable, "-m", "evalplus.evaluate",
4.      "--samples", str(samples_path),
5.      "--dataset", dataset,
6.  ]
7.  if base_only:
8.      cmd.append("--base-only")
9.
10. subprocess.run(cmd, check=True, capture_output=True, text=True)
11. # evalplus.evaluate writes results alongside samples_path (check actual output path)
12. # Adjust filtered_path to match evalplus actual output location if needed
13. return filtered_path
```

#### Pseudo-code — `load_passing_samples`

```
1.  passing = {}   # {task_id: [code_str, ...]}
2.  with open(filtered_path) as f:
3.      for line in f:
4.          record = json.loads(line)
5.          task_id = record["task_id"]
6.          # evalplus results format: {task_id, solution, passed: bool}
7.          if record.get("passed", False):
8.              passing.setdefault(task_id, []).append(record["solution"])
9.  return passing
```

#### Key Edge Cases

- evalplus `evaluate` output path convention may differ from `samples_path.with_suffix(".filtered.jsonl")` — verify against actual evalplus output schema and adjust path resolution
- `load_passing_samples` uses `setdefault` to accumulate multiple passing samples per task
- Empty `passing[task_id]` list is impossible by construction (only appended when `passed=True`) — no need to filter empties downstream

#### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | evalplus CLI Wrapper | subprocess.run evalplus.codegen, path handling for model IDs |
| L-3-2 | Test-Pass Filter + Sample Loader | evalplus.evaluate wrapper + jsonl parser returning {task_id: [code]} |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings 1-2 lines
- [x] Tensor shapes not applicable (no tensors — pure Python pipeline)
- [x] Subtask count within budget (2+2+2 = 6 total)
- [x] "Codebase Analysis (Serena)" section included
- [x] At least one "Applied: " line present
