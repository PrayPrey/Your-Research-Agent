---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
generated: 2026-08-31
author: yoon303@ust.ac.kr
---

Applied: subprocess-isolated verifier pattern
Applied: checkpoint-resume pipeline pattern

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

# Logic: h-e1 — Multi-Verifier Activation Measurement

## A-E3: SMT Pilot + Four Verifiers [Complexity: 16, Budget: 4 subtasks]

### Subtask L-E3-1: ExecutionMonitor.run() — subprocess isolation

**Parent Epic:** E3

**Signature:**
```python
def run(problem_id: str, completion: str, test_code: str, timeout: float = 3.0) -> VerifierResult:
```

**Algorithm:**
1. Record start time
2. Write `completion + "\n" + test_code` to `tempfile.NamedTemporaryFile(suffix=".py", delete=False)`
3. `proc = subprocess.run(["python", tmp_path], capture_output=True, text=True, timeout=timeout)`
4. `activated = proc.returncode != 0`; `signal = (proc.stdout + proc.stderr).strip()`
5. Delete tempfile; return `VerifierResult(activated, signal, latency_ms)`

**Edge cases:**
- `subprocess.TimeoutExpired` → `VerifierResult(activated=False, signal="TIMEOUT", latency_ms=timeout*1000)`
- `SyntaxError` in completion → subprocess exits non-zero → `activated=True`, signal contains traceback
- Empty signal on failure → signal = `"EXIT_CODE_{}".format(proc.returncode)`

---

### Subtask L-E3-2: StaticAnalysis.run() + TypeChecker.run() — parallel mypy/pyright

**Parent Epic:** E3

**Signatures:**
```python
# verifiers/static_analysis.py
def run(completion: str, timeout: float = 10.0) -> VerifierResult:

# verifiers/type_checker.py
def run(completion: str, timeout: float = 10.0) -> VerifierResult:
```

**Algorithm (StaticAnalysis):**
1. Write completion to temp `.py` file
2. `proc = subprocess.run(["mypy", "--strict", tmp_path], capture_output=True, text=True, timeout=timeout)`
3. `activated = proc.returncode != 0`; `signal = proc.stdout.strip()`
4. Cleanup tempfile; return `VerifierResult(activated, signal, latency_ms)`

**Algorithm (TypeChecker):**
1. Write completion to temp `.py` file
2. `proc = subprocess.run(["pyright", "--outputjson", tmp_path], capture_output=True, text=True, timeout=timeout)`
3. Parse `json.loads(proc.stdout)`; `diags = data.get("generalDiagnostics", [])`
4. `activated = len(diags) > 0`; `signal = json.dumps(diags[:5])` (cap at 5 for brevity)
5. Cleanup tempfile; return `VerifierResult(activated, signal, latency_ms)`

**Edge cases (both):**
- `subprocess.TimeoutExpired` → `VerifierResult(False, "TIMEOUT", timeout*1000)`
- `json.JSONDecodeError` in TypeChecker → treat as `diags=[]`, `activated=False`
- Shared pattern: use `try/finally` to guarantee tempfile deletion

---

### Subtask L-E3-3: SmtSolver.run_pilot() — 20-problem gate

**Parent Epic:** E3

**Signature:**
```python
def run_pilot(problems: list[Problem], completions: dict[str, str], n: int = 20, seed: int = 1) -> dict:
```

**Returns:**
```python
{
    "sat_count": int,
    "total": int,
    "sat_rate": float,
    "passed_gate": bool,   # sat_rate >= 0.30
    "pilot_results": list  # [{problem_id, outcome, signal}]
}
```

**Algorithm:**
1. `random.seed(seed); pilot = random.sample(problems, n)`
2. For each problem in pilot:
   a. `result = run(problem.prompt, completions[problem.problem_id])`
   b. Append `{problem_id, outcome: "sat"|"unsat"|"unknown"|"error", signal: result.signal}`
   c. `sat_count += result.activated`
3. `sat_rate = sat_count / n`
4. Return dict with `passed_gate = sat_rate >= 0.30`

**Edge cases:**
- `len(problems) < n` → sample min(n, len(problems))
- Any exception in `run()` → outcome="error", activated=False

---

### Subtask L-E3-4: SmtSolver.run() — Z3 constraint generation + check

**Parent Epic:** E3

**Signature:**
```python
def run(prompt: str, completion: str, timeout: float = 10.0) -> VerifierResult:
```

**Algorithm:**
1. Build LLM message: system="Generate Z3 Python code that encodes the constraints of this problem. Use z3 library. End with `result = s.check()`.", user=prompt
2. `z3_code = openai_client.chat.completions.create(model="gpt-4o-mini", messages=...).choices[0].message.content`
3. Strip markdown fences if present (`re.sub(r"```python|```", "", z3_code)`)
4. Create restricted namespace: `ns = {"__builtins__": {}}; ns.update(z3.__dict__)`
5. `exec(z3_code, ns)` inside `try/except Exception`
6. `outcome = str(ns.get("result", "unknown"))`
7. `activated = outcome == "sat"`
8. Return `VerifierResult(activated, signal=outcome, latency_ms)`

**Edge cases:**
- `exec` raises any exception → `VerifierResult(False, "EXEC_ERROR: "+str(e), latency_ms)`
- LLM returns no valid code → `VerifierResult(False, "NO_Z3_CODE", latency_ms)`
- `timeout` not enforced at exec level (Z3 can hang) → wrap exec in `threading.Timer(timeout, thread.interrupt_main)` or use `signal.alarm(int(timeout))` on Unix

---

## A-E4: Activation Measurement + Gate Check [Complexity: 9, Budget: 2 subtasks]

### Subtask L-E4-1: run_all_verifiers() — orchestration loop

**Parent Epic:** E4

**Signature:**
```python
def run_all_verifiers(
    problems: list[Problem],
    completions: dict[str, str],
    smt_enabled: bool = True,
    out_path: str = "results/verifier_results.jsonl",
) -> dict[str, dict[str, VerifierResult]]:
```

**Algorithm:**
1. Open `out_path` in append mode; load already-processed IDs from existing lines (checkpoint resume)
2. `results: dict[str, dict] = {}`
3. For each problem (skip if already in checkpoint):
   a. `exec_r = execution_monitor.run(problem.problem_id, completions[pid], problem.test_code)`
   b. `static_r = static_analysis.run(completions[pid])`
   c. `type_r = type_checker.run(completions[pid])`
   d. `smt_r = smt_solver.run(problem.prompt, completions[pid]) if smt_enabled else VerifierResult(False, "DISABLED", 0.0)`
   e. Write JSONL line: `{"problem_id": pid, "source": problem.source, "results": {cat: asdict(r) for cat, r in ...}}`
   f. `results[pid] = {"execution": exec_r, "static_analysis": static_r, "type_checking": type_r, "smt_solving": smt_r}`
4. Return `results`

**JSONL schema per line:**
```json
{"problem_id": "HE_0001", "source": "humaneval", "results": {"execution": {"activated": true, "signal": "...", "latency_ms": 42.1}, "static_analysis": {...}, "type_checking": {...}, "smt_solving": {...}}}
```

**Edge cases:**
- Missing completion for problem_id → skip problem, log warning
- Any verifier raises unexpectedly → catch, record `VerifierResult(False, "VERIFIER_ERROR", 0.0)`

---

### Subtask L-E4-2: compute_stats() + gate_check()

**Parent Epic:** E4

**Signatures:**
```python
def compute_stats(results: dict[str, dict[str, VerifierResult]], problems: list[Problem]) -> dict:

def gate_check(stats: dict) -> bool:
```

**compute_stats returns:**
```python
{
    "activation_rates": {"execution": float, "static_analysis": float, "type_checking": float, "smt_solving": float},
    "pairwise_overlap": {"execution_static_analysis": float, ...},   # C(4,2)=6 pairs
    "per_source": {
        "humaneval": {"execution": float, ...},
        "mbpp": {"execution": float, ...}
    },
    "n_total": int,
    "n_per_source": {"humaneval": int, "mbpp": int}
}
```

**Algorithm (compute_stats):**
1. `cats = ["execution", "static_analysis", "type_checking", "smt_solving"]`
2. Build activated sets: `act[cat] = {pid for pid, r in results.items() if r[cat].activated}`
3. `activation_rates[cat] = len(act[cat]) / len(results)`
4. Pairwise overlap: for each pair `(a, b)` in `itertools.combinations(cats, 2)`: `|act[a] & act[b]| / len(results)`; key = `f"{a}_{b}"`
5. Per-source: group problem_ids by source, compute rates within each group

**Algorithm (gate_check):**
1. For each cat, print `f"{cat}: {rate:.1%} {'PASS' if rate>=0.10 else 'FAIL'}"`
2. `passed = all(r >= 0.10 for r in stats["activation_rates"].values())`
3. Print overall PASS/FAIL; return `passed`

**Edge cases:**
- `len(results) == 0` → return zero rates without division error (guard with `n = max(len(results), 1)`)
- SMT disabled → `smt_solving` rate = 0.0 → gate_check will print FAIL for it (expected, caller handles)

---

## Subtask Index

| ID | Subtask | Epic | Description |
|----|---------|------|-------------|
| L-E3-1 | ExecutionMonitor.run() | E3 | Subprocess isolation, timeout, pass/fail |
| L-E3-2 | StaticAnalysis + TypeChecker | E3 | mypy/pyright CLI subprocess wrappers |
| L-E3-3 | SmtSolver.run_pilot() | E3 | 20-problem SAT gate (seed=1) |
| L-E3-4 | SmtSolver.run() | E3 | LLM Z3 codegen + exec + check |
| L-E4-1 | run_all_verifiers() | E4 | Orchestration loop + JSONL checkpoint |
| L-E4-2 | compute_stats() + gate_check() | E4 | Activation rates, overlap, gate |
