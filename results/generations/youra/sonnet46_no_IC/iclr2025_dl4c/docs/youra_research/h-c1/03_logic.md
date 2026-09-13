---
hypothesis_id: "h-c1"
document_type: "Logic"
phase: "Phase 3"
generated_at: "2026-08-04"
---

# Logic: H-C1 — Doctest Prevalence Pilot Scanner

Applied: Standard Python stdlib patterns (subprocess isolation, reservoir sampling, AST walk)

---

## 1. Executive Summary

Three-phase sequential pipeline scanning 10,000 Python files from The Stack. Phase A is a trivial string check. Phase B uses stdlib `ast` + `doctest.DocTestParser`. Phase C runs isolated subprocesses via `ProcessPoolExecutor(4)`. No model training.

---

## 2. Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project — no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## 3. API Signatures

```python
# data_loader.py
def load_python_stream(seed: int = 42, buffer_size: int = 10000) -> IterableDataset: ...
def quality_filter(sample: dict) -> bool: ...
def reservoir_sample(stream: IterableDataset, n: int = 10000) -> list[dict]: ...

# scanner.py
def phase_a(source: str) -> bool: ...
def phase_b(source: str) -> dict: ...  # {'ast_positive': bool, 'n_examples': int, 'error': str|None}
def phase_c_worker(source: str, timeout: int = 5) -> dict: ...  # {'passed': bool, 'error_type': str|None}
def run_all_phases(samples: list[dict], n_workers: int = 4) -> list[dict]: ...

# token_estimator.py
def estimate_tokens(source: str) -> int: ...
def sum_tokens(sources: list[str]) -> float: ...

# results.py
def build_aggregate(per_file: list[dict], duration: float) -> dict: ...
def write_json(aggregate: dict, path: str) -> None: ...
def write_jsonl(per_file: list[dict], path: str) -> None: ...

# visualize.py
def generate_all(aggregate: dict, per_file: list[dict], out_dir: str) -> None: ...

# gate.py
def run_gate_check(aggregate: dict) -> str: ...  # 'PASS' | 'SCOPE' | 'PIVOT'
```

---

## 4. Subtask Implementations

### E-1: Data Streaming & Sampling [Complexity: 9, Budget: 2 subtasks]

#### L-1-1: `reservoir_sample()` — reservoir sampling

Uses first-N strategy on a pre-shuffled stream (HuggingFace `.shuffle()` provides randomness; reservoir Algorithm R is not needed since the stream is already shuffled with seed=42).

```python
def reservoir_sample(stream: IterableDataset, n: int = 10000) -> list[dict]:
    """Collect first n quality-passing samples from shuffled stream."""
    samples = []
    for item in tqdm(stream, desc="Sampling"):
        if quality_filter(item):
            samples.append(item)
            if len(samples) >= n:
                break
    return samples
```

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | reservoir_sample | First-N from shuffled stream with quality gate |

#### L-1-2: `quality_filter()` — The Stack filters

```python
def quality_filter(sample: dict) -> bool:
    """True if avg_line_len<=100, max_line_len<=1000, alphanum_frac>=0.25."""
    src = sample.get("content", "")
    if not src:
        return False
    lines = src.splitlines() or [""]
    avg_len = sum(len(l) for l in lines) / len(lines)
    max_len = max(len(l) for l in lines)
    total = len(src)
    alphanum = sum(c.isalnum() for c in src)
    alphanum_frac = alphanum / total if total > 0 else 0.0
    return avg_len <= 100 and max_len <= 1000 and alphanum_frac >= 0.25
```

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-2 | quality_filter | avg_line_len, max_line_len, alphanum_frac computation |

---

### E-2: Phase A + B Scanner [Complexity: 10, Budget: 3 subtasks]

#### L-2-1: `phase_b()` — AST walk + DocTestParser

```python
def phase_b(source: str) -> dict:
    """Parse AST, extract doctest examples from all docstring-bearing nodes."""
    result = {'ast_positive': False, 'n_examples': 0, 'error': None}
    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        result['error'] = f"SyntaxError: {e}"
        return result
    except Exception as e:
        result['error'] = f"ParseError: {e}"
        return result

    parser = doctest.DocTestParser()
    node_types = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)
    for node in ast.walk(tree):
        if not isinstance(node, node_types):
            continue
        docstring = ast.get_docstring(node)
        if not docstring:
            continue
        try:
            examples = parser.get_examples(docstring)
        except Exception:
            continue
        result['n_examples'] += len(examples)

    result['ast_positive'] = result['n_examples'] > 0
    return result
```

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | phase_b | AST walk over FunctionDef/AsyncFunctionDef/ClassDef/Module, DocTestParser |

#### L-2-2: Error handling protocol

| Error | Handling | `error` field value |
|-------|----------|---------------------|
| `SyntaxError` on `ast.parse` | Return early, `ast_positive=False` | `"SyntaxError: {msg}"` |
| `UnicodeDecodeError` | Caught in `run_all_phases` before phase_b; skip file | `"UnicodeDecodeError"` |
| `Exception` on `ast.parse` | Return early | `"ParseError: {msg}"` |
| Empty docstring (`None`) | Skip node silently | — |
| `Exception` on `parser.get_examples` | Skip node, continue walk | — |

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-2 | error_handling | SyntaxError / UnicodeDecodeError / empty docstring protocol |

#### L-2-3: Per-file result dict schema

```python
# Per-file result dict — one entry per sampled file
{
    "file_id": str,            # index 0..9999 as string
    "content_len": int,        # len(source)
    "phase_a": bool,           # '>>>' in source
    "phase_b": bool,           # ast_positive
    "n_doctest_examples": int, # total examples found by DocTestParser (0 if phase_b=False)
    "phase_c": bool,           # returncode == 0 (None if not run)
    "error_type": str | None,  # 'timeout'|'import_error'|'assertion_error'|'exception'|None
    "parse_error": str | None, # SyntaxError/UnicodeDecodeError msg or None
    "estimated_tokens": int,   # estimate_tokens(source) for phase_c=True files, else 0
}
```

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-3 | per_file_schema | Field definitions for per_file_results.jsonl |

---

### E-3: Phase C Execution Engine [Complexity: 14, Budget: 4 subtasks]

#### L-3-1: `phase_c_worker()` — subprocess wrapper

```python
def phase_c_worker(source: str, timeout: int = 5) -> dict:
    """Run doctest suite in isolated subprocess. Returns {'passed': bool, 'error_type': str|None}."""
    wrapper = _build_wrapper(source)
    try:
        proc = subprocess.run(
            [sys.executable, "-c", wrapper],
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {'passed': False, 'error_type': 'timeout'}
    except Exception as e:
        return {'passed': False, 'error_type': f'exception: {e}'}

    if proc.returncode == 0:
        return {'passed': True, 'error_type': None}
    return {'passed': False, 'error_type': _classify_error(proc.returncode, proc.stderr)}
```

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | phase_c_worker | subprocess.run wrapper with timeout, returncode semantics |

#### L-3-2: Error classification — `_classify_error()`

```python
def _classify_error(returncode: int, stderr: bytes) -> str:
    """Classify failure from returncode and stderr text."""
    stderr_str = stderr.decode("utf-8", errors="replace")
    if "ImportError" in stderr_str or "ModuleNotFoundError" in stderr_str:
        return "import_error"
    if "AssertionError" in stderr_str or "Failed example" in stderr_str:
        return "assertion_error"
    if "DocTestFailure" in stderr_str or "UnexpectedException" in stderr_str:
        return "wrong_output"
    return "exception"
```

Returncode semantics:
- `0` → all doctests passed
- `1` → doctest failures (assertion_error / wrong_output)
- `2` → Python syntax / import error
- non-zero + TimeoutExpired → timeout (caught before returncode check)

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-2 | error_classification | Classify timeout/import_error/assertion_error/exception |

#### L-3-3: `run_all_phases()` — ProcessPoolExecutor integration

```python
def run_all_phases(samples: list[dict], n_workers: int = 4) -> list[dict]:
    per_file = []
    ast_positive_indices = []

    # Phase A + B: single-threaded
    for i, sample in enumerate(tqdm(samples, desc="Phase A+B")):
        source = sample.get("content", "")
        rec = {
            "file_id": str(i), "content_len": len(source),
            "phase_a": False, "phase_b": False, "n_doctest_examples": 0,
            "phase_c": None, "error_type": None, "parse_error": None,
            "estimated_tokens": 0,
        }
        try:
            rec["phase_a"] = phase_a(source)
            if rec["phase_a"]:
                b = phase_b(source)
                rec["phase_b"] = b["ast_positive"]
                rec["n_doctest_examples"] = b["n_examples"]
                rec["parse_error"] = b["error"]
                if rec["phase_b"]:
                    ast_positive_indices.append(i)
        except UnicodeDecodeError as e:
            rec["parse_error"] = f"UnicodeDecodeError: {e}"
        per_file.append(rec)

    # Phase C: parallel
    ast_sources = [(i, samples[i]["content"]) for i in ast_positive_indices]
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(phase_c_worker, src): idx
                   for idx, src in ast_sources}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Phase C"):
            idx = futures[future]
            try:
                c = future.result(timeout=10)  # executor-level safety margin
            except TimeoutError:
                c = {'passed': False, 'error_type': 'timeout'}
            except Exception as e:
                c = {'passed': False, 'error_type': f'exception: {e}'}
            per_file[idx]["phase_c"] = c["passed"]
            per_file[idx]["error_type"] = c["error_type"]
            if c["passed"]:
                per_file[idx]["estimated_tokens"] = estimate_tokens(samples[idx]["content"])

    return per_file
```

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-3 | executor_integration | Submit AST-positive files, collect futures, handle TimeoutError |

#### L-3-4: Subprocess wrapper template — `_build_wrapper()`

```python
def _build_wrapper(source: str) -> str:
    """Build the -c string passed to subprocess.run."""
    # Uses base64 to avoid shell quoting issues with arbitrary source code
    import base64
    encoded = base64.b64encode(source.encode("utf-8")).decode("ascii")
    return (
        "import base64, types, doctest, sys\n"
        f"src = base64.b64decode('{encoded}').decode('utf-8')\n"
        "mod = types.ModuleType('__scanned__')\n"
        "exec(compile(src, '__scanned__', 'exec'), mod.__dict__)\n"
        "results = doctest.testmod(mod, verbose=False)\n"
        "sys.exit(0 if results.failed == 0 else 1)\n"
    )
```

Key design decisions:
- base64-encode source to avoid quoting issues with triple-quotes, backslashes, etc.
- `types.ModuleType` provides a clean module namespace for `doctest.testmod()`
- `sys.exit(0)` iff `results.failed == 0`; subprocess never writes to disk

Subtasks:

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-4 | wrapper_template | base64-encoded source in subprocess -c string |

---

## 5. Data Shapes

### Per-file result dict (per_file_results.jsonl — one JSON object per line)

| Field | Type | Set when |
|-------|------|----------|
| `file_id` | `str` | always |
| `content_len` | `int` | always |
| `phase_a` | `bool` | always |
| `phase_b` | `bool` | phase_a=True |
| `n_doctest_examples` | `int` | phase_a=True |
| `phase_c` | `bool \| None` | phase_b=True |
| `error_type` | `str \| None` | phase_b=True, phase_c=False |
| `parse_error` | `str \| None` | on SyntaxError/UnicodeDecodeError |
| `estimated_tokens` | `int` | phase_c=True |

### Aggregate result dict (results.json)

```python
{
    "n_sampled": 10000,
    "n_pattern_positive": int,          # sum(phase_a)
    "n_ast_positive": int,              # sum(phase_b)
    "n_executable_positive": int,       # sum(phase_c == True)
    "doctest_pattern_rate": float,      # n_pattern_positive / 10000
    "doctest_ast_rate": float,          # n_ast_positive / 10000
    "doctest_executable_rate": float,   # n_executable_positive / 10000
    "estimated_full_subset_executable_files": int,  # rate * 12_960_052
    "estimated_token_pool_M": float,    # sum(estimated_tokens) / 1e6
    "scan_duration_seconds": float,
    "seed": 42,
    "dataset": "bigcode/the-stack-dedup",
    "filter": "data/python",
}
```

---

## 6. Applied KB Patterns

Applied: Standard Python stdlib patterns (no relevant KB matches for corpus scanning or subprocess isolation — low similarity scores, PyTorch/OpenAI docs returned)
- `subprocess.run([sys.executable, "-c", ...], capture_output=True, timeout=N)` — stdlib isolation pattern
- `ProcessPoolExecutor` with `as_completed` — stdlib parallel worker pattern
- `ast.walk` + `ast.get_docstring` — stdlib AST traversal
- `doctest.DocTestParser().get_examples()` — stdlib doctest extraction
- First-N from pre-shuffled stream — sufficient given HuggingFace `.shuffle(seed=42)`; Algorithm R not needed
