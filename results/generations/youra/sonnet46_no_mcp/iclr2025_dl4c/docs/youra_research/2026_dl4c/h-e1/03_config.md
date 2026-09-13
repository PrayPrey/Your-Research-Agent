# Config: H-E1 — Difficulty-Stratified Curriculum GRPO

**Hypothesis:** H-E1 | **Type:** EXISTENCE (PoC) | **Date:** 2026-05-02

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict

---

## Base CONFIG (code/config.py)

Applied: Standard TRL GRPO training config pattern

```python
CONFIG = {
    # Model
    "model_id": "deepseek-ai/deepseek-coder-7b-base-v1.5",

    # GRPO generation
    "num_generations": 8,
    "max_new_tokens": 512,
    "temperature": 1.0,

    # Training
    "learning_rate": 1e-6,
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "max_steps": 5000,
    "save_steps": 500,
    "seed": 42,

    # Curriculum
    "curriculum_step": 2500,

    # Paths
    "output_dir": "h-e1/checkpoints",
    "log_dir": "h-e1/logs",
    "results_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",

    # Reward
    "reward_timeout": 10.0,
    "reward_epsilon": 1e-8,

    # Logging
    "reward_density_flush_interval": 100,
}

CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]
```

---

## GRPOConfig (used in train.py)

Applied: TRL GRPOConfig default pattern

```python
from trl import GRPOConfig

def build_grpo_config(condition: str) -> GRPOConfig:
    return GRPOConfig(
        output_dir=f"{CONFIG['output_dir']}/{condition}",
        num_generations=CONFIG["num_generations"],
        max_new_tokens=CONFIG["max_new_tokens"],
        temperature=CONFIG["temperature"],
        learning_rate=CONFIG["learning_rate"],
        per_device_train_batch_size=CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=CONFIG["gradient_accumulation_steps"],
        max_steps=CONFIG["max_steps"],
        save_steps=CONFIG["save_steps"],
        seed=CONFIG["seed"],
        bf16=True,
        logging_steps=10,
        dataloader_num_workers=0,
        remove_unused_columns=False,
    )
```

---

## A-2: Reward Function [Complexity: 8, Budget: 1 subtask]

Applied: Standard subprocess execution reward pattern

```python
# Parameters used in reward.py — drawn directly from CONFIG
REWARD_TIMEOUT: float = CONFIG["reward_timeout"]    # 10.0s per test execution
REWARD_EPSILON: float = CONFIG["reward_epsilon"]    # 1e-8, prevents div-by-zero in std

# Binary reward values (hardcoded constants)
REWARD_PASS: float = 1.0
REWARD_FAIL: float = 0.0
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | reward_impl | Implement `run_unit_tests` (subprocess, timeout) + `execution_reward_fn` (TRL callable API) + `compute_reward_density` (std > 0 check) |

---

## A-3: Curriculum Callbacks [Complexity: 9, Budget: 2 subtasks]

Applied: TrainerCallback CSV logging pattern

```python
# Parameters used in callbacks.py — drawn directly from CONFIG
CURRICULUM_STEP: int = CONFIG["curriculum_step"]          # 2500, phase switch point
LOG_DIR: str = CONFIG["log_dir"]                          # "h-e1/logs"
FLUSH_INTERVAL: int = CONFIG["reward_density_flush_interval"]  # flush CSV every 100 steps

# CSV output filename pattern (one file per condition)
# f"{LOG_DIR}/reward_density_{condition}.csv"
# Columns: step, reward_density
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | curriculum_callback | Implement `CurriculumCallback`: `on_step_begin` calls `dataset.set_step(state.global_step)`; logs phase switch message at step `curriculum_step` |
| C-3-2 | reward_density_callback | Implement `RewardDensityCallback`: `on_step_end` appends `(step, density)` to CSV; `finalize()` flushes and closes file handle |
