# Config: H-E1 (EXISTENCE / PoC)

**Hypothesis:** Higher bandwidth reward signals accelerate PPO convergence vs binary rewards
**Type:** EXISTENCE — single fixed config, no hyperparameter grid

Applied: TRL PPOTrainer custom-reward-function dataclass pattern (Hugging Face RLHF recipes)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: dataclass

---

## Config Schema (`config.py`)

```python
from dataclasses import dataclass, field

REWARD_CONDITIONS = ["binary", "categorical", "high_bandwidth"]
SEEDS = [0, 1, 2, 3, 4]

# High-bandwidth reward weights: 0.5*categorical + 0.3*pass_ratio + 0.2*partial_credit
HIGH_BANDWIDTH_WEIGHTS = (0.5, 0.3, 0.2)

# Categorical error-type scores
ERROR_CATEGORY_SCORES = {
    "passed": 1.0,
    "assertion_error": 0.5,
    "runtime_error": 0.25,
    "syntax_error": 0.0,
}


@dataclass
class ExperimentConfig:
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    learning_rate: float = 1e-5
    batch_size: int = 4
    ppo_epochs: int = 4
    init_kl_coef: float = 0.05
    train_epochs: int = 3
    pass_at_1_threshold: float = 0.3
    seed: int = 0                 # set per-run from SEEDS
    condition: str = "binary"     # set per-run from REWARD_CONDITIONS
    torch_dtype: str = "bfloat16"
    test_timeout_s: float = 5.0
    checkpoint_dir: str = "checkpoints"
```

**Non-standard**: `init_kl_coef=0.05` and `learning_rate=1e-5` are TRL RLHF defaults for 7B models, kept fixed per EXISTENCE scope (no tuning).

---

## A-5: Evaluation Pipeline [Complexity: 10, Budget: 2 subtasks]

**Applied**: pass@1 threshold + samples-to-threshold convergence pattern

### Configuration (Python Dataclass)

```python
@dataclass
class EvalConfig:
    pass_at_1_threshold: float = 0.3   # gate: high_bandwidth reaches this in fewer samples than binary
    eval_timeout_s: float = 5.0        # per test-case execution timeout
    mbpp_test_size: int = 500
    humaneval_test_size: int = 164
    significance_alpha: float = 0.05   # p < 0.05 for condition comparison
    n_seeds: int = 5
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-5-1 | pass@1 + samples_to_threshold | Compute pass@1 on MBPP/HumanEval; find first sample count crossing `pass_at_1_threshold` per (condition, seed) |
| C-5-2 | compare_conditions | Aggregate mean±std across seeds, run significance test (p<0.05), check gate: `samples_to_threshold(high_bandwidth) < samples_to_threshold(binary)` |

---

## YAML Schema (Equivalent Reference)

```yaml
experiment:
  model_id: codellama/CodeLlama-7b-Instruct-hf
  learning_rate: 1.0e-5
  batch_size: 4
  ppo_epochs: 4
  init_kl_coef: 0.05
  train_epochs: 3
  pass_at_1_threshold: 0.3
  torch_dtype: bfloat16
  test_timeout_s: 5.0

reward_conditions: [binary, categorical, high_bandwidth]
seeds: [0, 1, 2, 3, 4]
high_bandwidth_weights: [0.5, 0.3, 0.2]  # categorical, pass_ratio, partial_credit

error_category_scores:
  passed: 1.0
  assertion_error: 0.5
  runtime_error: 0.25
  syntax_error: 0.0

eval:
  pass_at_1_threshold: 0.3
  eval_timeout_s: 5.0
  significance_alpha: 0.05
  n_seeds: 5
```

---

## Notes

- Single fixed config, no ablation matrix — EXISTENCE scope.
- 3 conditions × 5 seeds = 15 total training runs, each 3 epochs.
- `ExperimentConfig` is instantiated per-run with `condition` and `seed` overridden by the training loop (`train.py: main()`).
