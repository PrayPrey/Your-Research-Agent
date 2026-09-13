# Logic: H-M1 (ΔPass₁₂ Trajectory Analysis)

**Type**: MECHANISM (SHOULD_WORK) — allocated tasks: M-2 (Trajectory), M-3 (McNemar). Budget: 2 subtasks total.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — h-e1's Python code (`h-e1/code/`) does not exist yet (file not present, execution pending per architecture doc). h-m1 does NOT import h-e1 modules; it only reads h-e1's output JSONL as a plain data file at runtime. No API signature verification needed — this is a data contract, not a code dependency.
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## M-2: Trajectory Computation [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard Python/stdlib (no KB match for pass@k trajectory pattern, similarity <0.35; simple set-based cumulative computation)

### API Signatures

```python
# trajectory.py
def compute_delta_pass_12(logs: list[dict], condition: str) -> dict:
    """ΔPass12 for one condition. Returns:
    {delta_pass_12: float, pass_at_iter_1: float, pass_at_iter_2: float,
     n_problems: int, newly_solved_iter_2: set[str]}"""
    ...

def compute_cumulative_trajectory(logs: list[dict], condition: str) -> dict[int, float]:
    """Cumulative pass@1 at iter 1,2,3 for trajectory plot. {1: p1, 2: p2, 3: p3}"""
    ...

def compare_conditions(logs: list[dict], cfg: AnalysisConfig) -> dict:
    """Returns {static_first: dict, exec_first: dict, delta_diff: float,
    hypothesis_supported: bool}  # hypothesis_supported = delta(static_first) > delta(exec_first)"""
    ...
```

### Pseudo-code

```
compute_delta_pass_12(logs, condition):
    sub = [r for r in logs if r.condition == condition]
    problems = {r.problem_id for r in sub}
    solved_by = lambda max_iter: {r.problem_id for r in sub
                                   if r.iteration <= max_iter and r.passed}
    solved_1 = solved_by(1)
    solved_2 = solved_by(2)              # cumulative: solved by iter 1 OR 2
    n = len(problems)
    pass_1 = len(solved_1) / n
    pass_2 = len(solved_2) / n
    newly_solved_2 = solved_2 - solved_1
    return dict(delta_pass_12=pass_2 - pass_1, pass_at_iter_1=pass_1,
                pass_at_iter_2=pass_2, n_problems=n,
                newly_solved_iter_2=newly_solved_2)

compute_cumulative_trajectory(logs, condition):
    sub = [r for r in logs if r.condition == condition]
    problems = {r.problem_id for r in sub}
    n = len(problems)
    out = {}
    for it in (1, 2, 3):
        solved = {r.problem_id for r in sub if r.iteration <= it and r.passed}
        out[it] = len(solved) / n
    return out

compare_conditions(logs, cfg):
    static, exec_ = cfg.conditions   # ("static_first", "exec_first")
    d_static = compute_delta_pass_12(logs, static)
    d_exec   = compute_delta_pass_12(logs, exec_)
    diff = d_static["delta_pass_12"] - d_exec["delta_pass_12"]
    return dict(static_first=d_static, exec_first=d_exec,
                delta_diff=diff, hypothesis_supported=diff > 0)
```

### Tensor Shapes

N/A — dict/set-based analysis, no tensors.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1 | Trajectory functions | `compute_delta_pass_12`, `compute_cumulative_trajectory`, `compare_conditions` — all set/dict based, no external deps beyond stdlib |

---

## M-3: McNemar Statistical Test [Complexity: 8, Budget: 1 subtask]

**Applied**: scipy.stats (no KB match; standard exact-binomial/chi2 dual-path per PRD FR-4 spec)

### API Signatures

```python
# stats.py
def mcnemar_test(static_newly_solved: set, exec_newly_solved: set,
                  all_problems: set) -> dict:
    """McNemar paired test on newly-solved-at-iter-2 sets.
    Returns {p_value: float, static_only: int, exec_only: int, method: str}"""
    ...
```

### Pseudo-code

```
mcnemar_test(static_newly_solved, exec_newly_solved, all_problems):
    # b = solved by static_first only, c = solved by exec_first only
    b = len(static_newly_solved - exec_newly_solved)
    c = len(exec_newly_solved - static_newly_solved)

    if b + c < 25:
        # exact binomial (scipy.stats.binomtest), per brief pseudocode
        result = scipy.stats.binomtest(k=min(b, c), n=b + c, p=0.5)
        p_value = result.pvalue
        method = "exact_binomial"
    else:
        # chi2 approximation with continuity correction
        chi2_stat = (abs(b - c) - 1) ** 2 / (b + c)
        p_value = 1 - scipy.stats.chi2.cdf(chi2_stat, df=1)
        method = "chi2_approx"

    return dict(p_value=p_value, static_only=b, exec_only=c, method=method)
```

### Tensor Shapes

N/A — scalar statistical test, no tensors.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-1 | `mcnemar_test` | b/c count from newly-solved sets, exact binomial (b+c<25) or chi2-approx branch, matches PRD FR-4 |

---

## External Dependencies

### Data Contract (From h-e1, Not Code Import)

h-m1 reads h-e1's output JSONL as plain data — no Python import, no API signatures to verify.

```python
# Each record in h-e1_iteration_logs.jsonl (loaded by data_loader.py, not in this budget):
{"problem_id": str, "condition": "static_first" | "exec_first",
 "iteration": 1 | 2 | 3, "passed": bool}
```

**Note**: File not yet present (h-e1 execution pending). `data_loader.py` (M-1, not in this logic budget) must fail fast on missing/malformed file per NFR-1.

---

## Self-Check

- `compute_delta_pass_12`/`compute_cumulative_trajectory` use pure set arithmetic → deterministic, byte-identical across runs (NFR-2).
- `mcnemar_test` branch threshold (b+c<25) matches PRD FR-4 / brief pseudocode exactly — no invented threshold.
- ponytail: `min(b, c)` in binomtest assumes two-sided test convention (scipy default); no config knob added since PRD does not request tunable alpha routing beyond `cfg.alpha` (already in architecture's `AnalysisConfig`).
