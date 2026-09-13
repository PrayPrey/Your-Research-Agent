# Config: h-m1
# Reward Density Mechanism Verification — Log Analysis

**Applied**: Standard log-analysis config pattern (hardcoded dict, paths-only, no new hyperparameters)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (direct file read of h-e1/code/config.py)
**Config Files Found**: `h-e1/code/config.py` (hardcoded dict — not dataclass)
**Pattern Used**: hardcoded dict (matching H-E1 pattern for consistency)

---

## Inherited Configuration (Base Hypothesis)

### Config from Actual Code

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified)
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

**Verified from**: `h-e1/code/config.py` (actual implementation — hardcoded dict, not dataclass)

**Key facts confirmed from actual code:**
- `log_dir` = `"h-e1/logs"` (H-M1 reads logs from here)
- `save_steps` = 500, `max_steps` = 5000 → 10 checkpoints per condition
- `curriculum_step` = 2500 → early phase boundary
- H-E1 logs per-step (5000 rows per CSV), not per-checkpoint

---

## A-6: TrainingWrapper Config [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard subprocess wrapper pattern (hardcoded dict)

```python
# h-m1/code/run_training.py
TRAINING_CONFIG = {
    "h_e1_train_script": "h-e1/code/training/train.py",
    "log_dir": "h-e1/logs",
    "conditions": ["curriculum", "uniform", "easy_only", "hard_only"],
    "cuda_device": "0",
    "min_rows": 10,
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Training invocation parameters | `TRAINING_CONFIG` dict with `h_e1_train_script`, `log_dir`, `conditions`, `cuda_device` |
| C-6-2 | Error handling config | `min_rows=10` sufficiency threshold; subprocess return code checked per condition; non-zero triggers sys.exit(1) |

---

## A-5: Main Analyzer Config [Complexity: 9, Budget: 1 subtask]

**Applied**: Standard analysis paths config pattern (hardcoded dict)

```python
# h-m1/code/analysis/analyze_reward_density.py
ANALYSIS_CONFIG = {
    "log_dir": "h-e1/logs",
    "figures_dir": "h-m1/figures",
    "results_dir": "h-m1/results",
    "results_file": "h-m1/results/wilcoxon_results.json",
    "significance_threshold": 0.05,
    "analysis_window_early": [0, 2500],    # steps 500-2500 (5 checkpoints)
    "analysis_window_late": [2501, 5000],  # steps 3000-5000 (5 checkpoints)
    "conditions": ["curriculum", "uniform", "easy_only", "hard_only"],
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Analysis config dict | `ANALYSIS_CONFIG` with all path params, `significance_threshold=0.05`, `analysis_window_early/late` boundaries matching `curriculum_step=2500` from H-E1 |

---

## Notes

- H-M1 introduces NO new model hyperparameters — all training config is inherited from H-E1 unchanged.
- `significance_threshold=0.05` is standard (non-custom, no rationale needed).
- `analysis_window_early` boundary 2500 matches H-E1 `curriculum_step` exactly.
- Both new config dicts use hardcoded dict format to match H-E1 `config.py` style.
