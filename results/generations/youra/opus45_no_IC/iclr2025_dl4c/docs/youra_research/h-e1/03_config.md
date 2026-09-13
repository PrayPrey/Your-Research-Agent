# Configuration: H-E1 (EXISTENCE / PoC)

**Applied**: No relevant KB pattern found (KB returned diffusion/inductor configs, not applicable) — standard PyTorch/TRL PPO defaults used per PRD FR-4.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Format: Python Dataclass (single fixed config, no variations — EXISTENCE tier)

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    # Model
    model_id: str = "meta-llama/CodeLlama-7b-Instruct-hf"
    torch_dtype: str = "float16"

    # Optimizer (PRD FR-4.2)
    lr: float = 3e-6
    weight_decay: float = 0.01

    # Batch (PRD FR-4.3)
    batch_size: int = 64
    per_device_batch: int = 16
    grad_accum: int = 4

    # Training (PRD FR-4.4)
    episodes: int = 10_000
    checkpoint_every: int = 1000

    # PPO
    clip_eps: float = 0.2
    warmup_ratio: float = 0.1  # linear warmup 10% steps, then linear decay

    # Reward (StepCoder, PRD FR-4.5)
    reward_pass: float = 1.0
    reward_test_fail: float = -0.3
    reward_runtime_error: float = -0.6
    reward_compile_error: float = -1.0

    # Eval
    pass_at_k: tuple = (1, 10)
    eval_n_samples: int = 10  # generations per problem for pass@10

    # Repro
    seed: int = 1

    # Paths
    checkpoint_dir: str = "h-e1/checkpoints"
    log_dir: str = "h-e1/logs"
    figure_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"
```

## Experiment Conditions (2x3 factorial, PRD FR-7)

```python
CONDITIONS = [
    # (condition_id, use_fgo, feedback_type)
    ("FR-7.1", False, "compile"),
    ("FR-7.2", False, "test"),
    ("FR-7.3", False, "combined"),
    ("FR-7.4", True,  "compile"),
    ("FR-7.5", True,  "test"),
    ("FR-7.6", True,  "combined"),
]
```

`feedback_type` selects which reward terms `compute_reward()` applies:
- `"compile"`: reward_pass / reward_compile_error only (no test-fail/runtime distinction)
- `"test"`: full StepCoder reward (pass/fail/runtime/compile)
- `"combined"`: compile check + test reward summed

## YAML Schema (for reproducibility logging, written alongside checkpoints)

```yaml
model_id: meta-llama/CodeLlama-7b-Instruct-hf
lr: 3.0e-6
weight_decay: 0.01
batch_size: 64
per_device_batch: 16
grad_accum: 4
episodes: 10000
checkpoint_every: 1000
clip_eps: 0.2
warmup_ratio: 0.1
reward_pass: 1.0
reward_test_fail: -0.3
reward_runtime_error: -0.6
reward_compile_error: -1.0
seed: 1
condition: FR-7.5
use_fgo: true
feedback_type: test
```

## Subtasks

None — LIGHT tier, 0 subtask budget; config integrated directly into Epic tasks (A-1..A-8).
