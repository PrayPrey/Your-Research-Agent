# Logic: H-M2 — Static Analysis Feedback Loop

**Applied**: subprocess+tempfile+JSON stdlib pattern (no KB match; standard practice)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No prior code to reuse (h-m1/code/ absent, mechanisms unrelated). Designing new APIs.
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Static Analyzer Integration [Complexity: 12, Budget: 3+2+4+3]

**Applied**: subprocess.run with tempfile + timeout + JSON parse (stdlib only)

### API Signatures

```python
# analyzers.py
import subprocess, tempfile, json, os
from typing import Optional

class AnalyzerError(Exception):
    """Raised on timeout or unparseable output."""

class BanditAnalyzer:
    def run(self, code: str, timeout_s: int = 30) -> list[dict]:
        """Write code to temp .py, run `bandit -f json`, return results[] or [] on timeout."""
        ...

class PylintAnalyzer:
    def run(self, code: str, timeout_s: int = 30) -> list[dict]:
        """Write code to temp .py, run `pylint --output-format=json`, return messages[] or [] on timeout."""
        ...

def _run_subprocess_json(cmd: list[str], timeout_s: int, results_key: Optional[str] = None) -> list[dict]:
    """Shared helper: run cmd, parse stdout JSON, catch TimeoutExpired/JSONDecodeError -> []."""
    ...
```

### Pseudo-code

```
BanditAnalyzer.run(code, timeout_s):
    1. tmp = tempfile.NamedTemporaryFile(suffix=".py", delete=False); tmp.write(code)
    2. try: proc = subprocess.run(["bandit", "-f", "json", tmp.name],
                                   capture_output=True, text=True, timeout=timeout_s)
    3. except subprocess.TimeoutExpired: return []
    4. finally: os.unlink(tmp.name)
    5. try: data = json.loads(proc.stdout)
    6. except json.JSONDecodeError: return []
    7. return data.get("results", [])   # bandit exits nonzero when issues found -- do NOT check returncode

PylintAnalyzer.run(code, timeout_s):
    same flow; parse stdout as JSON array directly (pylint json = list[dict])
    pylint also exits nonzero on lint findings -- ignore returncode, only use stdout
```

### Tensor Shapes

N/A (no tensors; list[dict] of issue records: `{"filename", "issue_text"/"message", "line_number"/"line", "issue_severity"/"symbol"}`)

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Temp file lifecycle | Write code to NamedTemporaryFile, cleanup in finally |
| L-3-2 | Bandit subprocess wrapper | Build cmd, run with timeout, parse `results` key |
| L-3-3 | Pylint subprocess wrapper | Build cmd, run with timeout, parse top-level list |
| L-3-4 | Shared error handling | TimeoutExpired -> [], JSONDecodeError -> [], never raise on nonzero exit |

---

## A-6: Iteration Controller [Complexity: 14, Budget: 3+4+4+3]

**Applied**: iterate-until-convergence with early termination (per architecture)

### API Signatures

```python
# feedback_loop.py
from typing import TypedDict

class IterationRecord(TypedDict):
    iteration: int
    code: str
    security_count: int
    reliability_count: int

class LoopResult(TypedDict):
    initial: dict          # {"code": str, "security_count": int, "reliability_count": int}
    final: dict             # same shape, last iteration state
    iterations: int         # count of refine() calls performed
    history: list[IterationRecord]

class IterationController:
    def __init__(
        self,
        generator: "CodeGenerator",
        bandit: "BanditAnalyzer",
        pylint: "PylintAnalyzer",
        max_iterations: int = 5,
        timeout_s: int = 30,
    ): ...

    def run(self, initial_code: str, prompt: str, temperature: float, max_new_tokens: int) -> LoopResult: ...
```

### Pseudo-code

```
run(initial_code, prompt, temperature, max_new_tokens):
    1. code = initial_code
    2. bandit_issues, pylint_issues = analyze(code)   # bandit.run(), pylint.run()
    3. sec0, rel0 = count_issues(bandit_issues, pylint_issues)  # metrics.count_issues
    4. initial = {"code": code, "security_count": sec0, "reliability_count": rel0}
    5. history = [{"iteration": 0, "code": code, "security_count": sec0, "reliability_count": rel0}]
    6. for i in range(1, max_iterations + 1):
        a. if sec0 == 0 and rel0 == 0: break              # early termination, no issues
        b. feedback = format_issues_for_prompt(bandit_issues, pylint_issues)
        c. code = generator.refine(prompt, code, feedback, temperature, max_new_tokens)
        d. bandit_issues, pylint_issues = analyze(code)
        e. sec0, rel0 = count_issues(bandit_issues, pylint_issues)
        f. history.append({"iteration": i, "code": code, "security_count": sec0, "reliability_count": rel0})
    7. final = {"code": code, "security_count": sec0, "reliability_count": rel0}
    8. return {"initial": initial, "final": final, "iterations": len(history) - 1, "history": history}

analyze(code):
    bandit_issues = bandit.run(code, timeout_s)
    pylint_issues = pylint.run(code, timeout_s)
    return bandit_issues, pylint_issues
```

**Convergence note**: break check happens BEFORE refine (step 6a), so `iterations` reflects actual refine() calls, not analysis passes. Loop exits early once `sec0 == 0 and rel0 == 0`; otherwise runs full `max_iterations`.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Controller init + analyze() helper | Store deps, shared analyze(code) -> (bandit_issues, pylint_issues) |
| L-6-2 | Main loop skeleton | for-loop, history accumulation, initial state capture |
| L-6-3 | Convergence + refine wiring | Early-break check, format_issues_for_prompt + generator.refine() call |
| L-6-4 | Result assembly | Build LoopResult dict, iterations count = len(history)-1 |

---

## A-4: Feedback Formatter [Complexity: 6, Budget: 2+1+2+1]

**Applied**: structured text template, line-anchored issue injection (per Blyth et al. 2025 insight)

### API Signatures

```python
# feedback_formatter.py
def format_issues_for_prompt(bandit_issues: list[dict], pylint_issues: list[dict]) -> str:
    """Merge+format issues as 'Line N: [SECURITY/RELIABILITY] description', sorted by line."""
    ...

def build_refine_prompt(original_prompt: str, code: str, feedback: str) -> str:
    """Compose full refine prompt: original task + current code + feedback + fix instruction."""
    ...
```

### Pseudo-code

```
format_issues_for_prompt(bandit_issues, pylint_issues):
    1. lines = []
    2. for issue in bandit_issues:
        line_no = issue["line_number"]; desc = issue["issue_text"]
        lines.append((line_no, f"Line {line_no}: [SECURITY] {desc}"))
    3. for issue in pylint_issues:
        line_no = issue["line"]; desc = issue["message"]
        lines.append((line_no, f"Line {line_no}: [RELIABILITY] {desc}"))
    4. lines.sort(key=lambda x: x[0])
    5. return "\n".join(text for _, text in lines) or "No issues found."

build_refine_prompt(original_prompt, code, feedback):
    return f"{original_prompt}\n\nCurrent code:\n```python\n{code}\n```\n\n" \
           f"Static analysis found these issues:\n{feedback}\n\n" \
           f"Fix the issues above while preserving functionality. Return only the corrected code."
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Bandit/Pylint field extraction | Pull line_number/line + issue_text/message from each source's schema |
| L-4-2 | Merge + sort + join | Combine both lists, sort by line, join into text block |
| L-4-3 | Refine prompt template | build_refine_prompt() combining original task, code, feedback |

---

## A-7: Metrics Calculator [Complexity: 4, Budget: 1+1+1+1]

**Applied**: pure functions, division-by-zero guard

### API Signatures

```python
# metrics.py
def count_issues(bandit_results: list[dict], pylint_results: list[dict]) -> dict:
    """Returns {"security": int, "reliability": int}."""
    return {"security": len(bandit_results), "reliability": len(pylint_results)}

def issue_reduction(initial: int, final: int) -> float:
    """(initial - final) / initial; 0.0 if initial == 0."""
    return 0.0 if initial == 0 else (initial - final) / initial
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | count_issues + issue_reduction | Both pure functions, zero-division guard on issue_reduction |

---

## Evaluator (`evaluate.py`) — supporting logic, no dedicated subtask (rolled into A-10)

```python
def evaluate_condition(loop_results: list[dict]) -> dict:
    """
    Aggregate over prompts:
      security_issue_reduction = mean(issue_reduction(r["initial"]["security_count"], r["final"]["security_count"]) for r in loop_results)
      reliability_issue_reduction = same for reliability_count
      mean_iterations = mean(r["iterations"] for r in loop_results)
      initial_security = mean(r["initial"]["security_count"] for r in loop_results)
      final_security = mean(r["final"]["security_count"] for r in loop_results)
      initial_reliability / final_reliability analogous
    Returns dict with all above keys.
    """
    ...

def check_gate(agg_results: dict) -> bool:
    """PASS iff final_security < initial_security AND final_reliability < initial_reliability."""
    return (agg_results["final_security"] < agg_results["initial_security"]
            and agg_results["final_reliability"] < agg_results["initial_reliability"])
```

---

## Self-Check

```python
if __name__ == "__main__":
    assert issue_reduction(10, 3) == 0.7
    assert issue_reduction(0, 0) == 0.0
    assert count_issues([{}, {}], [{}]) == {"security": 2, "reliability": 1}
    print("metrics self-check OK")
```
