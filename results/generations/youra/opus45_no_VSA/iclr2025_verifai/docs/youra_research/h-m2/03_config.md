# Config: h-m2

**Type**: MECHANISM (statistical log analysis) — minimal config, 0 subtasks.

Applied: no matching KB pattern found — standard hardcoded dict used.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no existing config code to reuse; h-e1 is data-only)
**Config Files Found**: None
**Pattern Used**: dict

---

## Configuration

```python
CONFIG = {
    "input_path": "../h-e1/code/results/h-e1_iteration_logs.jsonl",
    "conditions": {
        "cascade": "static_first",
        "reverse": "exec_first",
    },
    "iter_from": 1,
    "iter_to": 2,
    "mcnemar_exact": True,
    "alpha": 0.05,
    "results_path": "code/results/h-m2_results.json",
    "figures_dir": "figures/",
}
```

No hyperparameters to tune — deterministic computation over existing logs. No seed needed (no randomness).

## Subtasks

None (0 budget; MECHANISM stats analysis, no config-level decomposition needed).
