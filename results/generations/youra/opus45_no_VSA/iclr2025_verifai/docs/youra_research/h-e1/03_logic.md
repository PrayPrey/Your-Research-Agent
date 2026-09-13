# Logic: H-E1 (Feedback Ordering Effect in LLM Code Repair)

**Type**: EXISTENCE (PoC) — allocated tasks: A-4 (Feedback), A-5 (Repair Loop). Budget: 4 subtasks total.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze, designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-4: Feedback Generation [Complexity: 12, Budget: 2 subtasks]

**Applied**: Standard Python (no KB match for repair-feedback truncation; used priority-queue truncation, a common stdlib-only pattern)

### API Signatures

```python
# feedback.py
from dataclasses import dataclass
from sandbox import ExecResult

def get_static_feedback(code: str, token_budget: int = 500) -> str:
    """Runs pylint+mypy on code, returns truncated feedback string."""
    ...

def get_execution_feedback(exec_result: ExecResult, token_budget: int = 500) -> str:
    """Formats failed/passed test info from ExecResult, truncated."""
    ...

def truncate_deterministic(items: list[str], token_budget: int, tokenizer=None) -> str:
    """Greedily joins items (already priority-sorted) until token_budget hit. Deterministic: no randomness, stable sort upstream."""
    ...

def build_feedback_prompt(static_fb: str, exec_fb: str, condition: str) -> str:
    """condition 'A': static_fb + exec_fb; condition 'B': exec_fb + static_fb."""
    ...
```

### Pseudo-code: deterministic truncation

```
truncate_deterministic(items, token_budget):
    # items pre-sorted by caller: errors > warnings > info (static)
    #                             failed tests > pass summary (exec)
    out = []
    used = 0
    for item in items:            # stable order -> reproducible
        cost = count_tokens(item) # tiktoken, same encoder every call
        if used + cost > token_budget:
            break
        out.append(item)
        used += cost
    return "\n".join(out)
```

### Pseudo-code: static feedback priority sort

```
get_static_feedback(code, token_budget):
    pylint_msgs = run_pylint(code)   # list of (severity, msg)
    mypy_msgs   = run_mypy(code)     # list of (severity, msg)
    all_msgs = pylint_msgs + mypy_msgs
    # priority: error(0) > warning(1) > info(2); stable sort preserves tool/line order as tiebreak
    sorted_msgs = sorted(all_msgs, key=lambda m: SEVERITY_RANK[m.severity])
    return truncate_deterministic([m.text for m in sorted_msgs], token_budget)
```

### Tensor Shapes

N/A — this module is text/string only, no tensors.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A4-1 | Static feedback pipeline | pylint+mypy runners, severity ranking, sort, truncate |
| L-A4-2 | Execution feedback + prompt builder | Format ExecResult into failed/pass items, truncate, `build_feedback_prompt` A/B branching |

---

## A-5: Repair Loop [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard Python (sequential loop with early-exit branch; no KB match)

### API Signatures

```python
# repair_loop.py
from dataclasses import dataclass
from data import Problem
from sandbox import ExecResult, run_tests_majority_vote
from feedback import get_static_feedback, get_execution_feedback, build_feedback_prompt
from llm import generate_initial_code, repair_code
from config import ExperimentConfig

@dataclass
class IterationLog:
    problem_id: str
    condition: str      # "A" | "B"
    iteration: int       # 0 = initial gen, 1..n_iterations = repairs
    code: str
    exec_result: ExecResult
    static_fb: str
    exec_fb: str

def run_condition(problem: Problem, condition: str, cfg: ExperimentConfig) -> list[IterationLog]:
    """Runs initial gen + up to cfg.n_iterations repairs for one problem/condition. Stops early if test passes."""
    ...

def run_all(problems: list[Problem], cfg: ExperimentConfig) -> list[IterationLog]:
    """Runs run_condition for both 'A' and 'B' per problem. Returns flattened logs."""
    ...
```

### Pseudo-code: repair loop with early-exit branching

```
run_condition(problem, condition, cfg):
    logs = []
    code = generate_initial_code(problem, cfg)
    result = run_tests_majority_vote(code, problem, cfg)
    logs.append(IterationLog(problem.id, condition, 0, code, result, "", ""))

    for it in range(1, cfg.n_iterations + 1):
        if result.passed:
            break                                    # condition: stop early on pass
        static_fb = get_static_feedback(code, cfg.feedback_token_budget)
        exec_fb   = get_execution_feedback(result, cfg.feedback_token_budget)
        prompt    = build_feedback_prompt(static_fb, exec_fb, condition)  # A/B order branch
        code      = repair_code(problem, code, prompt, cfg)
        result    = run_tests_majority_vote(code, problem, cfg)
        logs.append(IterationLog(problem.id, condition, it, code, result, static_fb, exec_fb))
    return logs

run_all(problems, cfg):
    logs = []
    for p in problems:
        logs += run_condition(p, "A", cfg)
        logs += run_condition(p, "B", cfg)
    return logs
```

### Tensor Shapes

N/A — text/dataclass pipeline, no tensors.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A5-1 | `run_condition` | Initial gen, iteration loop, early-exit on pass, IterationLog collection |
| L-A5-2 | `run_all` | Iterate problems x conditions A/B, flatten logs |

---

## Metrics (A-6, reference only — not in allocated budget, signatures for downstream consistency)

```python
# metrics.py
def pass_at_1(logs: list[IterationLog], condition: str) -> float:
    """Fraction of problems where final iteration (last per problem_id) passed, for given condition."""
    ...

def relative_improvement(pass_a: float, pass_b: float) -> float:
    """(pass_a - pass_b) / pass_b * 100"""
    ...

def bootstrap_ci(logs: list[IterationLog], n_resamples: int = 10000, seed: int = 42) -> tuple[float, float]:
    """Bootstrap resample problem-level pass/fail pairs (A,B); return 95% CI of relative_improvement."""
    ...

def mcnemar_test(logs: list[IterationLog]) -> float:
    """McNemar exact test on paired pass/fail (A vs B per problem); returns p-value."""
    ...
```

Pseudo-code (bootstrap CI):
```
bootstrap_ci(logs, n_resamples, seed):
    rng = np.random.default_rng(seed)
    pairs = [(final_pass(p, "A"), final_pass(p, "B")) for p in problem_ids]  # list of (bool, bool)
    n = len(pairs)
    deltas = []
    for _ in range(n_resamples):
        sample = rng.choice(pairs, size=n, replace=True)
        pa = mean(a for a, b in sample); pb = mean(b for a, b in sample)
        deltas.append(relative_improvement(pa, pb))
    return percentile(deltas, 2.5), percentile(deltas, 97.5)
```

---

## Self-Check

- Deterministic truncation: no randomness, stable sort, same tokenizer -> byte-identical across conditions (NFR-1). ponytail: assumes `count_tokens` is deterministic (tiktoken is); no cache needed at this scale (664 problems x 4 iterations).
- Early-exit in `run_condition` matches PRD FR-6 (stop once test passes) — cuts LLM API cost, satisfies budget in PRD section 8.
- `build_feedback_prompt` is the single source of truth for A/B ordering — both conditions share truncation code, only prompt assembly order differs, guaranteeing equal token budget (FR-6).
