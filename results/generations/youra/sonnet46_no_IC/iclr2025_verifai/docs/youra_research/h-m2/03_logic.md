---
title: "Logic: H-M2 Pylint/Mypy Coverage on HumanEval Baseline Failures"
hypothesis_id: h-m2
phase: 3
date: "2026-08-05"
status: complete
---

# Logic: H-M2

Applied: tempfile-static-analysis-with-subprocess-fallback

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M2 extends H-M1/H-E1)
**Status**: h-m1 code exists at `experiments/h-m1/`. h-m2 does NOT call h-m1 code APIs — it only reads h-m1 result files (JSONL/JSON). No shared function calls.
**Analyzed Path**: `experiments/h-m1/` — symbols verified via get_symbols_overview
**Relevant Symbols**: `load_humaneval`, `load_mbpp` (h-m1 data_loader — not used by h-m2; h-m2 reads result artifacts directly)

---

## External Dependencies API

**No h-m1 code APIs called by h-m2.** h-m2 reads result *files* (JSONL/JSON) from h-m1/h-e1, not Python functions. The data contract is the file format, not a Python API.

**Data contract (from h-m1/h-e1 result files):**
```python
# baseline_humaneval.jsonl — one record per line
{"task_id": str, "code": str, "passed": bool}          # flat (h-e1 format)
{"task_id": str, "rounds": [{"code": str, ...}], "passed": bool}  # nested (h-m1 format)

# baseline_results.json — dict or list format
{task_id: {"generated_code": str, "passed": bool}}     # dict format
[{"task_id": str, "generated_code": str, "passed": bool}]  # list format
```

---

## A-2: Static Analyzer [Complexity: 14, Budget: 4 subtasks]

Applied: tempfile-static-analysis-with-subprocess-fallback

### API Signatures

```python
# experiments/h-m2/static_analyzer.py
import os, re, subprocess, json
from io import StringIO
from tempfile import NamedTemporaryFile
from typing import Optional
from mypy import api as mypy_api
from pylint import lint
from pylint.reporters.text import TextReporter


def analyze_file(code: str, task_id: str) -> dict:
    """Run pylint+mypy on code string via temp file. Returns full result dict."""
    # Returns:
    # {
    #   "task_id": str,
    #   "flagged": bool,
    #   "pylint_flagged": bool,
    #   "mypy_flagged": bool,
    #   "pylint_categories": {"E": int, "W": int, "C": int, "R": int, "I": int},
    #   "pylint_message_count": int,
    #   "mypy_error_count": int,
    #   "pylint_output": str,   # truncated to 1000 chars
    #   "mypy_output": str,     # truncated to 500 chars
    #   "error": str,           # only present on exception
    # }
    ...


def _run_pylint(path: str) -> tuple[bool, dict, str]:
    """Run pylint on file at path. Primary: pylint.lint.Run() API. Fallback: subprocess JSON.

    Returns: (flagged: bool, categories: {"E","W","C","R","I" -> int}, raw_output: str)
    """
    ...


def _run_mypy(path: str) -> tuple[bool, int, str]:
    """Run mypy on file at path via mypy.api.run().

    Returns: (flagged: bool, error_count: int, raw_output: str)
    mypy exit code: 0=clean, 1+=errors found
    """
    ...


def run_coverage_measurement(cases: list[dict]) -> list[dict]:
    """Batch analyze all cases. Returns list of analyze_file() result dicts."""
    ...
```

### Pseudo-code: `_run_pylint`

```
1. try:
     buf = StringIO()
     reporter = TextReporter(buf)
     lint.Run([path, "--score=no", "--output-format=text"],
              reporter=reporter, exit=False)
     output = buf.getvalue()
2. except SystemExit, Exception:
     return _pylint_subprocess_fallback(path)

3. categories = {"E": 0, "W": 0, "C": 0, "R": 0, "I": 0}
4. for line in output.splitlines():
     # pylint line format: "path:line:col: Ccode (symbol) message"
     # or: "path:line:col: C0001: message"
     m = re.search(r':\s+([EWCRI])\d{4}', line)
     if m: categories[m.group(1)] += 1
5. flagged = sum(categories.values()) > 0
6. return (flagged, categories, output[:1000])
```

### Pseudo-code: `_pylint_subprocess_fallback` (internal helper)

```
1. cmd = ["python", "-m", "pylint", "--output-format=json", "--score=no", path]
2. r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
3. msgs = json.loads(r.stdout) if r.stdout.strip() else []
   except json.JSONDecodeError: msgs = []
4. categories = {c: sum(1 for m in msgs if m.get("type","").upper()[:1]==c) for c in "EWCRI"}
5. return (len(msgs) > 0, categories, r.stdout[:1000])
```

### Pseudo-code: `_run_mypy`

```
1. out, err, exit_code = mypy_api.run([
       "--ignore-missing-imports",
       "--no-strict-optional",
       "--no-error-summary",
       path
   ])
2. error_count = len([l for l in out.splitlines()
                      if l.strip() and "error:" in l and not l.startswith("Found")])
3. flagged = (exit_code != 0)
4. return (flagged, error_count, out[:500])
```

### Pseudo-code: `analyze_file`

```
1. if not code.strip():
     return {"task_id": task_id, "flagged": False, "error": "empty_code",
             "pylint_flagged": False, "mypy_flagged": False,
             "pylint_categories": {"E":0,"W":0,"C":0,"R":0,"I":0},
             "pylint_message_count": 0, "mypy_error_count": 0,
             "pylint_output": "", "mypy_output": ""}

2. with NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
     f.write(code); tmp_path = f.name

3. result = {task_id, pylint_flagged=False, mypy_flagged=False, flagged=False,
             pylint_categories={"E":0,...}, pylint_message_count=0,
             mypy_error_count=0, pylint_output="", mypy_output=""}

4. try:
     pylint_flagged, cats, pylint_out = _run_pylint(tmp_path)
     result["pylint_flagged"] = pylint_flagged
     result["pylint_categories"] = cats
     result["pylint_message_count"] = sum(cats.values())
     result["pylint_output"] = pylint_out

     mypy_flagged, err_count, mypy_out = _run_mypy(tmp_path)
     result["mypy_flagged"] = mypy_flagged
     result["mypy_error_count"] = err_count
     result["mypy_output"] = mypy_out

     result["flagged"] = pylint_flagged or mypy_flagged

   except Exception as e:
     result["error"] = str(e)

   finally:
     if os.path.exists(tmp_path): os.unlink(tmp_path)

5. return result
```

### Pseudo-code: `run_coverage_measurement`

```
1. results = []
2. for case in tqdm(cases, desc="Static analysis"):
     code = case.get("generated_code") or case.get("completion") or case.get("code", "")
     task_id = case.get("task_id", f"unknown_{len(results)}")
     results.append(analyze_file(code, task_id))
3. return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | analyze_file | Temp file lifecycle, empty-code guard, try/finally cleanup, combine pylint+mypy results |
| L-2-2 | _run_pylint | pylint.lint.Run() API call + regex category parse + subprocess JSON fallback |
| L-2-3 | _run_mypy | mypy.api.run() call + exit-code flagging + error-line count (exclude summary lines) |
| L-2-4 | run_coverage_measurement | tqdm batch loop, code field extraction from multiple possible keys |

---

## A-3: Metrics Computation [Complexity: 9, Budget: 2 subtasks]

Applied: numpy-percentile-bootstrap-ci

### API Signatures

```python
# experiments/h-m2/metrics.py
import numpy as np


def compute_metrics(
    results: list[dict],
    n_bootstrap: int = 10000,
    seed: int = 42,
) -> dict:
    """Compute all coverage metrics + bootstrap CI from analyze_file() results.

    Returns:
    {
      "n_total_failures": int,
      "n_flagged": int,
      "n_unflagged": int,
      "coverage": float,              # n_flagged / n_total
      "coverage_ci_lower": float,     # bootstrap 2.5th percentile
      "coverage_ci_upper": float,     # bootstrap 97.5th percentile
      "coverage_passes_gate": bool,   # coverage < 0.50
      "gate_type": "SHOULD_WORK",
      "pylint_coverage": float,
      "mypy_coverage": float,
      "n_pylint_only": int,
      "n_mypy_only": int,
      "n_both_flagged": int,
      "n_neither": int,
      "pylint_category_totals": {"E": int, "W": int, "C": int, "R": int, "I": int},
    }
    """
    ...


def _bootstrap_ci(
    flags: np.ndarray,   # 1D binary array, dtype int/bool
    n: int,              # n_bootstrap resamples
    seed: int,
) -> tuple[float, float]:
    """Bootstrap 95% CI on proportion. Returns (ci_lower, ci_upper)."""
    ...
```

### Pseudo-code: `_bootstrap_ci`

```
1. rng = np.random.default_rng(seed)
2. means = [rng.choice(flags, len(flags), replace=True).mean() for _ in range(n)]
   # ponytail: list comprehension is O(n*N); fine for n=10000, N~64
3. return tuple(np.percentile(means, [2.5, 97.5]))
```

### Pseudo-code: `compute_metrics`

```
1. n_total = len(results)
2. flags = np.array([1 if r.get("flagged") else 0 for r in results])
3. n_flagged = int(flags.sum())
4. coverage = n_flagged / n_total

5. ci_lower, ci_upper = _bootstrap_ci(flags, n_bootstrap, seed)

6. pylint_flags = [r.get("pylint_flagged", False) for r in results]
   mypy_flags   = [r.get("mypy_flagged", False)   for r in results]
7. n_pylint_only = sum(p and not m for p, m in zip(pylint_flags, mypy_flags))
   n_mypy_only   = sum(m and not p for p, m in zip(pylint_flags, mypy_flags))
   n_both        = sum(p and m     for p, m in zip(pylint_flags, mypy_flags))

8. cat_totals = {"E":0,"W":0,"C":0,"R":0,"I":0}
   for r in results:
     for cat, cnt in r.get("pylint_categories", {}).items():
       cat_totals[cat] = cat_totals.get(cat, 0) + cnt

9. return full metrics dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | compute_metrics | Venn counts (pylint-only/mypy-only/both/neither), category totals, gate eval |
| L-3-2 | _bootstrap_ci | numpy default_rng seeded bootstrap; percentile CI on binary proportion |
