# Config: h-e2 (EXISTENCE PoC)

Applied: minimal single-config pattern for EXISTENCE hypotheses (no hyperparameter grid/ablation)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict (config.py)

---

## Config (Hardcoded Dict — `code/config.py`)

```python
CONFIG = {
    # Model
    "model_id": "codellama/CodeLlama-7b-Instruct-hf",
    "temperature": 0.7,
    "max_tokens": 512,

    # Refinement
    "k_iters": 3,

    # Datasets
    "datasets": {
        "humaneval": {"path": "openai_humaneval", "split": "test"},
        "mbpp": {"path": "mbpp", "split": "test"},
    },

    # Evaluation
    "seed": 42,
    "conditions": ["zero_shot", "ai_critic", "random_baseline"],

    # Output
    "figures_dir": "figures/",
}
```

Non-standard: none — all values taken directly from PRD (FR-2, FR-3, NFR-1).

## A-7: Execution & Pass@1 Evaluation [Complexity: 9, Budget: 1 subtask]

**Applied**: standard sandboxed exec + pass@1 aggregation (no KB pattern needed — trivial exec/subprocess use)

### Configuration (uses `CONFIG` above; no separate eval dataclass)

```python
EVAL_CONFIG = {
    "timeout_sec": 10,        # per-test-case exec timeout
    "k_iters": CONFIG["k_iters"],   # 3 -> iteration curve k=0..3
    "seed": CONFIG["seed"],
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | pass@1 + iteration curve | Run code via subprocess/exec with timeout, aggregate boolean pass results into pass@1 per condition and per iteration (k=0..3) |

---

## YAML Schema (optional file form of `CONFIG`)

```yaml
model_id: codellama/CodeLlama-7b-Instruct-hf
temperature: 0.7
max_tokens: 512
k_iters: 3
seed: 42
datasets:
  humaneval:
    path: openai_humaneval
    split: test
  mbpp:
    path: mbpp
    split: test
conditions: [zero_shot, ai_critic, random_baseline]
figures_dir: figures/
```

---

## Self-Validation

- [x] ONE format only (dict, no dataclass)
- [x] No hyperparameter grid/ablation (EXISTENCE scope)
- [x] Single seed (42)
- [x] A-7 subtask count = 1 (within budget)
- [x] Codebase Analysis (Serena) section included
