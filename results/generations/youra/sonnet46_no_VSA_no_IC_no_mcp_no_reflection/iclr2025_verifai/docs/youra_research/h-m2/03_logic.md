# H-M2 Logic Design

Applied: measurement-pipeline pattern (subprocess verifiers + statistical comparison)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from H-M1 architecture doc (actual code confirmed in 03_architecture.md Findings section)
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Relevant Symbols**: `execute_solution`, `classify_bug_type`, `_run_pyright` — reused via import; H-M2 modules are green-field on top.

---

## External Dependencies API

### API Signatures (From Actual H-M1 Code)

```python
# From: docs/youra_research/h-m1/code/src/execute.py
def execute_solution(code: str, test: str) -> dict:
    """Run code+test in subprocess. Returns execution result dict."""
    # Returns: {"passed": bool, "error": str|None, "error_type": str|None, "tmp_path": str|None, "code": str}

# From: docs/youra_research/h-m1/code/src/classify.py
def classify_bug_type(code: str, execution_result: dict) -> str:
    """Classify bug type from code and execution result. Uses _run_pyright() internally."""
    # Returns: one of "type_error" | "logic_error" | "syntax_error" | "runtime_error" | "unknown"

# Note: H-M2 does NOT call these at runtime — reads pre-computed H-M1 results.jsonl only.
# These are referenced for type consistency in load_h_m1.py.
```

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation, confirmed in 03_architecture.md)

---

## A-5: Z3ConstraintExtractor [Complexity: 15, Budget: 4 subtasks]

Applied: LLM-as-extractor pattern with restricted exec namespace

### API Signatures

```python
# src/z3_extractor.py
import z3
from openai import OpenAI

SYSTEM_PROMPT = """You are a formal verification assistant.
Given a Python function docstring, output ONLY valid Z3 Python expressions as a JSON list of strings.
Each string must be a valid Z3 BoolRef expression using z3 variables.
Declare variables using z3.Int(), z3.Real(), z3.String() as needed.
Return [] if constraints cannot be expressed in Z3.
Example output: ["z3.And(x >= 0, x <= 100)", "z3.Length(s) > 0"]"""

USER_TEMPLATE = """Docstring:
{docstring}

Return a JSON list of Z3 constraint strings. No explanation, no markdown."""

class Z3ConstraintExtractor:
    def __init__(self, client: OpenAI, model: str = "gpt-4o-mini", timeout_secs: int = 10):
        """LLM-based Z3 constraint extractor from docstrings."""
        ...

    def extract(self, task_id: str, docstring: str) -> list | None:
        """Extract Z3 constraints from docstring. Returns list or None on failure.
        Returns: list of z3.BoolRef (empty list = no constraints), None = extraction failed
        """
        ...

    def _call_llm(self, docstring: str) -> list[str] | None:
        """Call GPT-4o-mini, parse JSON response. Returns list of expr strings or None."""
        ...

    def _safe_eval(self, expr_strings: list[str]) -> list | None:
        """Evaluate expr strings in restricted z3 namespace. Returns z3 objects or None."""
        ...
```

### Subtask: L-5-1 — GPT-4o-mini prompt template

```python
def _call_llm(self, docstring: str) -> list[str] | None:
    # 1. Build messages: [system=SYSTEM_PROMPT, user=USER_TEMPLATE.format(docstring=docstring)]
    # 2. client.chat.completions.create(model=self.model, messages=..., temperature=0, max_tokens=512)
    # 3. Parse response.choices[0].message.content as JSON
    # 4. Validate: isinstance(result, list) and all(isinstance(s, str) for s in result)
    # 5. Return list[str] or None on any exception
```

### Subtask: L-5-2 — Z3 expression safety evaluation

```python
SAFE_Z3_NS = {
    "z3": z3,
    "Int": z3.Int, "Real": z3.Real, "Bool": z3.Bool,
    "String": z3.String, "And": z3.And, "Or": z3.Or,
    "Not": z3.Not, "If": z3.If, "Implies": z3.Implies,
    "Length": z3.Length, "SubString": z3.SubString,
    # NO: __builtins__, open, exec, eval, import
}

def _safe_eval(self, expr_strings: list[str]) -> list | None:
    # For each expr_str in expr_strings:
    #   result = eval(expr_str, {"__builtins__": {}}, SAFE_Z3_NS)
    #   validate isinstance(result, z3.BoolRef)
    # Return list of z3.BoolRef, or None if any eval raises
    # ponytail: restricted namespace, not sandbox; sufficient for LLM-generated z3 exprs
```

### Subtask: L-5-3 — Z3Solver constraint validation (satisfiability check)

```python
# Called from measure_z3(), not from extractor directly
# Extractor only returns constraints; solver is in measure.py

def _check_satisfiable(constraints: list, timeout_ms: int = 9000) -> tuple[str, object | None]:
    """Check if constraints are satisfiable. Returns (status, model|None).
    status: "sat" | "unsat" | "unknown" | "timeout"
    """
    # 1. solver = z3.Solver()
    # 2. solver.set("timeout", timeout_ms)
    # 3. solver.add(*constraints)
    # 4. result = solver.check()
    # 5. if result == z3.sat: return ("sat", solver.model())
    # 6. if result == z3.unsat: return ("unsat", None)
    # 7. else: return ("unknown", None)  # z3.unknown = timeout
```

### Subtask: L-5-4 — Coverage tracking and fallback

```python
def extract(self, task_id: str, docstring: str) -> list | None:
    # 1. if not docstring or len(docstring) < 10: return None
    # 2. expr_strings = self._call_llm(docstring)
    # 3. if expr_strings is None or len(expr_strings) == 0: return None
    # 4. constraints = self._safe_eval(expr_strings)
    # 5. if constraints is None: return None
    # 6. return constraints  # may be empty list [] = valid but no constraints

# Callers treat None → char_count=0, field_count=0 (no Z3 measurement possible)
# [] → solver runs with no constraints → always sat → model empty → char_count=2, field_count=0
# Expected ~40% return non-None; rest None
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | LLM prompt template | GPT-4o-mini call, JSON parse, validation |
| L-5-2 | Safe eval namespace | Restricted z3-only exec namespace |
| L-5-3 | Satisfiability check | z3.Solver with timeout, sat/unsat/unknown |
| L-5-4 | Coverage + fallback | None propagation, early exit on bad docstring |

---

## A-8: StatisticalAnalyzer [Complexity: 13, Budget: 2 subtasks]

Applied: Standard scipy Kruskal-Wallis + scikit-posthocs Dunn pipeline

### API Signatures

```python
# src/analyze.py
import scipy.stats
import scikit_posthocs as sp
import pandas as pd

def run_analysis(records: list[dict]) -> dict:
    """Run Kruskal-Wallis + Dunn + ε² on char_count across 4 verifiers.
    records: [{task_id, verifier, char_count, field_count, bug_type, timeout}, ...]
    Returns analysis dict with ordering_confirmed flag.
    """
    ...

def _epsilon_squared(H: float, n: int) -> float:
    """ε² = H / (n - 1). Effect size for Kruskal-Wallis."""
    ...

def _ordering_confirmed(per_verifier_means: dict[str, float], dunn_pvalues: dict) -> bool:
    """Check SMT >= {pyright, mypy} > execution by mean char_count and Dunn p-values."""
    ...
```

### Subtask: L-8-1 — Kruskal-Wallis + Dunn + ε² pipeline

```python
def run_analysis(records: list[dict]) -> dict:
    # 1. df = pd.DataFrame(records)
    # 2. Filter timeout==False for primary analysis (timeout records noted separately)
    # 3. groups = {v: df[df.verifier==v]["char_count"].values for v in ["execution","pyright","mypy","z3"]}
    # 4. Validate: each group must have n >= 2; drop groups with n < 2
    # 5. H, p = scipy.stats.kruskal(*[g for g in groups.values() if len(g) >= 2])
    # 6. n_total = sum(len(g) for g in groups.values())
    # 7. eps2 = H / (n_total - 1)
    # 8. dunn_df = sp.posthoc_dunn(df[~df.timeout], val_col="char_count", group_col="verifier", p_adjust="bonferroni")
    # 9. per_verifier = {v: {"mean": g.mean(), "median": float(np.median(g)), "std": g.std(), "n": len(g)} for v, g in groups.items()}
    # 10. return {"per_verifier": per_verifier, "kruskal_wallis": {"H": H, "p": p},
    #             "effect_size_epsilon2": eps2, "dunn_pvalues": dunn_df.to_dict(),
    #             "ordering_confirmed": _ordering_confirmed(per_verifier_means, dunn_df),
    #             "pairwise_diff_pct": _pairwise_diff_pct(per_verifier)}
```

### Subtask: L-8-2 — ordering_confirmed logic and pairwise diff%

```python
def _ordering_confirmed(per_verifier: dict, dunn_df: "pd.DataFrame") -> bool:
    # Ordering to confirm: z3_mean >= pyright_mean AND z3_mean >= mypy_mean
    #                      AND pyright_mean > exec_mean AND mypy_mean > exec_mean
    # Also check Dunn p < 0.05 for (z3 vs execution) and ({pyright,mypy} vs execution)
    means = {v: per_verifier[v]["mean"] for v in per_verifier}
    smt_ge_static = means.get("z3", 0) >= means.get("pyright", 0) and means.get("z3", 0) >= means.get("mypy", 0)
    static_gt_exec = means.get("pyright", 0) > means.get("execution", 0) and means.get("mypy", 0) > means.get("execution", 0)
    # Dunn significance for z3 vs execution
    try:
        p_z3_exec = dunn_df.loc["z3", "execution"]
        sig = p_z3_exec < 0.05
    except (KeyError, TypeError):
        sig = False  # missing z3 data (>80% timeout fallback)
    return smt_ge_static and static_gt_exec and sig

def _pairwise_diff_pct(per_verifier: dict) -> dict:
    # Returns % difference between adjacent category means
    # adjacent pairs: (z3, pyright), (z3, mypy), (pyright, execution), (mypy, execution)
    pairs = [("z3", "pyright"), ("z3", "mypy"), ("pyright", "execution"), ("mypy", "execution")]
    result = {}
    for a, b in pairs:
        ma, mb = per_verifier.get(a, {}).get("mean", 0), per_verifier.get(b, {}).get("mean", 0)
        if mb > 0:
            result[f"{a}_vs_{b}"] = round((ma - mb) / mb * 100, 1)
        else:
            result[f"{a}_vs_{b}"] = None
    return result
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | KW + Dunn + ε² pipeline | Data validation, scipy/posthocs calls, per_verifier stats |
| L-8-2 | ordering_confirmed + pairwise diff% | Mean ordering check, Dunn p gate, % diff computation |

---

## A-6: Z3 Verifier [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch — z3-solver Python API with signal-based timeout

### API Signatures

```python
# src/measure.py (method of FeedbackMeasurer)

def measure_z3(self, constraints: list | None) -> dict:
    """Measure Z3 feedback specificity from extracted constraints.
    constraints: list of z3.BoolRef | None
    Returns: {"verifier": "z3", "char_count": int, "field_count": int, "timeout": bool}
    """
    ...
```

### Subtask: L-6-1 — measure_z3() sat/unsat/timeout handling

```python
def measure_z3(self, constraints: list | None) -> dict:
    base = {"verifier": "z3", "char_count": 0, "field_count": 0, "timeout": False}

    # Case 1: No constraints extracted
    if constraints is None:
        return base  # char_count=0, field_count=0 — sparse data, handled in analysis

    # Case 2: Run solver with timeout
    try:
        status, model = _check_satisfiable(constraints, timeout_ms=self.timeout_secs * 1000 - 500)
    except Exception:
        return {**base, "timeout": True}

    # Case 3: sat → measure model
    if status == "sat" and model is not None:
        model_str = str(model)           # e.g. "[x = 5, y = 3]"
        char_count = len(model_str)      # len of model string
        field_count = len(model)         # number of declarations in model
        return {"verifier": "z3", "char_count": char_count, "field_count": field_count, "timeout": False}

    # Case 4: unsat → constraints unsatisfiable (bug confirmed, no counterexample)
    if status == "unsat":
        # char_count = len("unsat") = 5 to distinguish from None case
        return {"verifier": "z3", "char_count": 5, "field_count": 0, "timeout": False}

    # Case 5: unknown/timeout
    return {**base, "timeout": True}
    # ponytail: unsat gets char_count=5 to avoid zero-inflation; revisit if analysis treats unsat differently
```

### Subtask: L-6-2 — Timeout/exception recovery and sparse data handling

```python
# Sparse data protocol for analyze.py:
# - None constraints → char_count=0, field_count=0, timeout=False
#   These are EXCLUDED from Z3 group in Kruskal-Wallis (they represent missing data, not zero feedback)
#   Filter: df[(df.verifier=="z3") & (df.char_count > 0 | df.timeout==True)] for Z3 group
#   If filtered Z3 group < 10% of failing solutions → log warning, reduce to 3-category analysis

# Timeout recovery in measure_z3:
# - z3.Solver.set("timeout", ms) is the primary mechanism (z3 internal)
# - Wrap entire call in try/except to catch z3 internals raising z3types.Z3Exception
# - Do NOT use threading/signal for z3 timeout — z3's own timeout is sufficient and safer

def _check_satisfiable(constraints: list, timeout_ms: int = 9500) -> tuple[str, object | None]:
    import z3
    solver = z3.Solver()
    solver.set("timeout", timeout_ms)
    if constraints:
        solver.add(*constraints)
    result = solver.check()
    if result == z3.sat:
        return ("sat", solver.model())
    elif result == z3.unsat:
        return ("unsat", None)
    else:  # z3.unknown — timeout or resource limit
        return ("unknown", None)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | measure_z3() sat/unsat/model | char_count/field_count from model; unsat sentinel; None passthrough |
| L-6-2 | Timeout recovery + sparse data | z3 internal timeout, exception guard, analysis exclusion rule |

---

## Tensor Shapes

N/A — this is a measurement pipeline, not a neural network. No tensor operations.

---

## Summary

| Epic | Subtasks | Key Design Decision |
|------|----------|---------------------|
| A-5 | L-5-1..4 | Restricted eval namespace; None = missing, [] = valid empty |
| A-8 | L-8-1..2 | Filter timeout before KW; unconfirmed if z3 missing |
| A-6 | L-6-1..2 | z3 internal timeout; unsat → sentinel 5 chars, not 0 |
