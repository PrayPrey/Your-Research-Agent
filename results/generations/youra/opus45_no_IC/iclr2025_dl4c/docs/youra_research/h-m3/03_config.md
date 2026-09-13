# Configuration: H-M3 (Dense Credit Assignment — Convergence Efficiency)

**Type:** MECHANISM | **Budget:** per architecture (B-1..B-9)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M2)
**Status:** Config classes verified from actual H-M2 code (`h-m2/code/config.py`), not from `h-m2/03_config.md` spec (spec uses dataclasses; actual code uses plain dicts — field names differ: e.g. `clip_epsilon` not `clip_eps`, no `lr` field only `learning_rate`).
**Config Files Found:** `h-m2/code/config.py` (`TRAINING_CONFIG`, `DATA_CONFIG`, `PIPELINE_CONFIG`)
**Pattern Used:** Hardcoded dict (matching H-M2 actual code style, for consistency)

**Applied:** Standard PPO hyperparameter defaults (TRL/OpenRLHF conventions) + periodic-eval convergence tracking pattern from experiment brief.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m2/code/config.py (ACTUAL CODE - verified field names)
TRAINING_CONFIG = {
    "algorithm": "ppo",
    "learning_rate": 1e-5,       # NOT "lr"
    "lr_schedule": "cosine",
    "batch_size": 16,
    "per_device_batch": 4,
    "ppo_epochs": 4,
    "clip_epsilon": 0.2,          # NOT "clip_eps"
    "gae_lambda": 0.95,
    "gamma": 1.0,
    "max_grad_norm": 1.0,
    "weight_decay": 0.01,
}
```

**Verified from**: `h-m2/code/config.py` (actual implementation)

H-M3 reuses `TRAINING_CONFIG` verbatim for optimizer/PPO hyperparameters (NFR-3: no new model changes). Only training-loop control fields (`training_steps`, `checkpoint_every`) are overridden per H-M3 requirements below.

---

## A-1: Convergence Measurement Config [B-2, B-3]

**Applied:** Periodic-eval learning-curve pattern (experiment brief Algorithm)

### Configuration (Hardcoded dict)
```python
CONVERGENCE_CONFIG = {
    "max_steps": 5000,
    "eval_interval": 100,
    "target_pass1": 0.5,
    "checkpoint_every": 500,   # NFR-2
}
```

### Subtasks
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-1 | Loop skeleton | max_steps loop, sample_batch, generate, reward |
| C-2-2 | Periodic eval | every eval_interval steps, compute pass@1, append to learning_curve |
| C-2-3 | Steps-to-target | record first step where pass1 >= target_pass1 |

---

## A-2: Experiment / Conditions Config [B-2, B-6]

**Applied:** Standard ablation-condition dict pattern (matches H-M2 A-3)

### Configuration (Hardcoded dict)
```python
CONDITIONS = ["standard", "fgo"]   # maps to run_condition(condition=...)

SEEDS = [42, 123, 456]

EXPERIMENT_CONFIG = {
    "conditions": CONDITIONS,
    "seeds": SEEDS,
    "output_dir": "./results/h-m3",
    "checkpoint_dir": "./checkpoints/h-m3",
}
```

### Subtasks
| ID | Subtask | Description |
|----|---------|--------------|
| C-2-4 | Condition x seed loop | 2 conditions x 3 seeds = 6 runs in run_experiment.py |

---

## A-3: Dataset & Model Config (Reused from H-M2) [B-1]

**Applied:** Reuse H-M2 `DATA_CONFIG` verbatim (no new logic)

### Configuration (Hardcoded dict)
```python
# Reused as-is from h-m2/code/config.py
DATA_CONFIG = {
    "humaneval_dataset": "openai/openai_humaneval",
    "mbpp_dataset": "google-research-datasets/mbpp",
    "mbpp_split": "test",
    "model_name": "meta-llama/CodeLlama-7b-Instruct-hf",
    "max_new_tokens": 256,
    "generation_temperature": 0.8,
    "generation_top_p": 0.95,
    "device": "cuda",
    "dtype": "bfloat16",
    "max_length": 512,   # H-M3 tokenization requirement (FR-3.3), not in H-M2 config
}
```

### Subtasks
| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Copy/import config.py | Copy DATA_CONFIG + TRAINING_CONFIG from h-m2/code into h-m3/code (per architecture note: copy if no cross-package import) |

---

## A-4: Gate / Stats Thresholds [B-7, B-9]

**Applied:** Standard gate-threshold dict pattern

### Configuration (Hardcoded dict)
```python
GATE_THRESHOLDS = {
    "steps_to_target_ratio_max": 0.6,   # FGO steps < 60% of Standard steps
    "sample_efficiency_min_ratio": 1.5,  # FGO > 1.5x Standard (secondary, FR-4.4)
}

GATE_TYPE = "SHOULD_WORK"
```

### Subtasks
| ID | Subtask | Description |
|----|---------|--------------|
| C-7-1 | Gate check | Compare FGO vs Standard steps_to_target_ratio and final_pass1 against GATE_THRESHOLDS |

---

## Full h-m3/code/config.py Schema (Copy-Paste Ready)

```python
"""Configuration for H-M3 experiment: Dense Credit Assignment Convergence Efficiency."""

# Reused verbatim from h-m2/code/config.py
DATA_CONFIG = {
    "humaneval_dataset": "openai/openai_humaneval",
    "mbpp_dataset": "google-research-datasets/mbpp",
    "mbpp_split": "test",
    "model_name": "meta-llama/CodeLlama-7b-Instruct-hf",
    "max_new_tokens": 256,
    "generation_temperature": 0.8,
    "generation_top_p": 0.95,
    "device": "cuda",
    "dtype": "bfloat16",
    "max_length": 512,
}

TRAINING_CONFIG = {
    "algorithm": "ppo",
    "learning_rate": 1e-5,
    "lr_schedule": "cosine",
    "batch_size": 16,
    "per_device_batch": 4,
    "ppo_epochs": 4,
    "clip_epsilon": 0.2,
    "gae_lambda": 0.95,
    "gamma": 1.0,
    "max_grad_norm": 1.0,
    "weight_decay": 0.01,
}

CONVERGENCE_CONFIG = {
    "max_steps": 5000,
    "eval_interval": 100,
    "target_pass1": 0.5,
    "checkpoint_every": 500,
}

EXPERIMENT_CONFIG = {
    "conditions": ["standard", "fgo"],
    "seeds": [42, 123, 456],
    "output_dir": "./results/h-m3",
    "checkpoint_dir": "./checkpoints/h-m3",
}

GATE_THRESHOLDS = {
    "steps_to_target_ratio_max": 0.6,
    "sample_efficiency_min_ratio": 1.5,
}

GATE_TYPE = "SHOULD_WORK"
```

---

## YAML Schema (Experiment Run Manifest)

For Phase 4 run tracking / reproducibility (one file per run: `runs/{condition}_{seed}.yaml`):

```yaml
run_id: fgo_seed42
condition: fgo          # standard | fgo
seed: 42
max_steps: 5000
eval_interval: 100
target_pass1: 0.5
checkpoint_every: 500
training:
  learning_rate: 1.0e-5
  batch_size: 16
  clip_epsilon: 0.2
  gae_lambda: 0.95
  gamma: 1.0
model_name: meta-llama/CodeLlama-7b-Instruct-hf
output_dir: ./results/h-m3
```

### Subtasks
| ID | Subtask | Description |
|----|---------|--------------|
| C-9-1 | YAML writer | Dump per-run manifest to `runs/{condition}_{seed}.yaml` in run_experiment.py |

---

**Total subtasks allocated:** 8 (within B-2/B-3/B-6/B-7/B-9 budgets; B-1/B-4/B-5/B-8 have no config-specific subtasks beyond copy-wiring noted in A-3)
