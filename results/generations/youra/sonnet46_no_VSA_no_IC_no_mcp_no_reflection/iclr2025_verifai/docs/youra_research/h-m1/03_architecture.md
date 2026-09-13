# H-M1 Architecture

## Component Diagram

```
DataLoader → Generator → Executor → Classifier → ResultWriter
    │            │           │            │             │
    │            │           │            │             └─ results.jsonl
    │            │           │            └─ bug_type (type_error/runtime_error/logic_error)
    │            │           └─ execution result (pass/fail + exception)
    │            └─ generated code (GPT-4o-mini, single-shot)
    └─ 538 problems (HumanEval + MBPP)
```

## File/Module Layout

```
run_h_m1.py          # main entry point
src/
  generate.py        # GPT-4o-mini generation loop
  execute.py         # sandboxed execution wrapper (human_eval harness)
  classify.py        # 3-class bug type classifier (Pyright + exception parsing)
  evaluate.py        # distribution analysis + spot-check
  visualize.py       # figures
results/h-m1/
  results.jsonl      # per-problem records
  summary.json       # aggregated distribution stats
figures/             # output plots
```

## Data Flow

```
problem text
  → generate_solution()   → generated code
  → execute_solution()    → execution result (pass | fail + exception trace)
  → classify_bug_type()   → bug_type ∈ {type_error, runtime_error, logic_error}
  → append record         → results/h-m1/results.jsonl
  → compute_distribution()→ results/h-m1/summary.json
  → visualize             → figures/
```

## Key Interfaces

```python
def load_problems() -> dict:
    """Return {task_id: problem_dict} for 538 HumanEval+MBPP problems."""

def generate_solution(client, problem: dict) -> str:
    """Single-shot GPT-4o-mini completion; return generated code string."""

def execute_solution(code: str, test: str) -> str:
    """Run code+test in sandbox; return 'pass' or exception trace string."""

def classify_bug_type(code: str, execution_result: str, tmp_path: str) -> str:
    """Return one of 'type_error', 'runtime_error', 'logic_error'."""

def compute_distribution(records: list[dict]) -> dict:
    """Return counts/fractions per bug_type; flag if any type > 80%."""
```

## Classification Logic

- `type_error` — Pyright reports a type error in the generated code
- `runtime_error` — execution raises a non-assertion exception (NameError, TypeError at runtime, etc.)
- `logic_error` — code runs without exception but assertion fails (wrong output)
- Only failed solutions are classified; passing solutions are recorded as `bug_type: null`

## Distribution Check

`compute_distribution` flags the result as non-mixed if any single bug type
exceeds 80% of total failures. H-M1 hypothesis: the distribution is mixed
(all three types present, none dominant).

## Output Artifacts

| Artifact | Description |
|---|---|
| `results/h-m1/results.jsonl` | One JSON record per problem: `{task_id, source, passed, bug_type, ...}` |
| `results/h-m1/summary.json` | Counts, fractions, mixed flag, total problems, pass rate |
| `figures/` | Bar chart of bug type distribution, pass/fail breakdown |
