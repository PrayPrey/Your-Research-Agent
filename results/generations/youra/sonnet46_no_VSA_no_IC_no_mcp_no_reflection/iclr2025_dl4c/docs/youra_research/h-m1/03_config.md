# H-M1 Configuration

**Hypothesis**: H-M1 — Ratio vs Binary Reward Policy Target Shift  
**Type**: MECHANISM (extends H-E1)  
**Date**: 2026-08-31

Applied: Standard PyTorch/TRL GRPO dataclass config pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)  
**Status**: Config classes verified from H-E1 actual code  
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`  
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class GRPOConfig:
    # Model
    model_name: str = "deepseek-ai/deepseek-coder-6.7b-instruct"
    dtype: str = "bfloat16"

    # Data
    dataset_name: str = "codeparrot/apps"
    min_test_cases: int = 5
    max_prompt_tokens: int = 1024

    # GRPO rollout
    group_size: int = 8
    prompt_batch_size: int = 4
    max_new_tokens: int = 256
    temperature: float = 1.0

    # Optimization
    learning_rate: float = 1e-6
    clip_ratio: float = 0.2
    kl_beta: float = 0.01
    warmup_steps: int = 10
    train_steps: int = 500

    # Checkpointing
    checkpoint_step: int = 200
    output_dir: str = "outputs"

    # Sandbox
    sandbox_timeout: int = 5

    # Experiment
    reward_mode: str = "binary"
    seed: int = 42
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## A-6: HM1Config Dataclass [Budget: core task]

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class HM1Config(GRPOConfig):
    # Override H-E1 defaults to match PRD spec
    train_steps: int = 1000
    kl_beta: float = 0.04           # Non-standard: PRD specifies 0.04 (H-E1 used 0.01)
    warmup_steps: int = 100         # Non-standard: PRD specifies 100 (H-E1 used 10)
    max_new_tokens: int = 512       # Non-standard: PRD specifies 512 (H-E1 used 256)
    max_prompt_tokens: int = 512    # Non-standard: PRD specifies 512 (H-E1 used 1024)
    sandbox_timeout: int = 3        # Non-standard: PRD specifies 3s (H-E1 used 5s)
    output_dir: str = "outputs/h-m1"

    # Checkpointing (multi-step, replaces single checkpoint_step)
    checkpoint_steps: List[int] = field(default_factory=lambda: [200, 400, 600, 800, 1000])

    # Evaluation schedule
    eval_humaneval_at_steps: List[int] = field(default_factory=lambda: [200, 400, 600, 800, 1000])
    eval_mbpp_at_step: int = 1000
    eval_apps_val_at_step: int = 1000

    # APPS validation holdout
    apps_val_size: int = 500

    # Statistical analysis
    bootstrap_n: int = 1000

    # Monitoring thresholds
    fraction_partial_alert_threshold: float = 0.05
```

---

## A-7: VisualizerConfig [Complexity: 1, Budget: 1 subtask]

Applied: Standard matplotlib output config pattern

```python
@dataclass
class VisualizerConfig:
    figure_dpi: int = 300
    figure_format: str = "png"
    color_binary: str = "#1f77b4"
    color_ratio: str = "#ff7f0e"
    output_dir: str = "docs/youra_research/h-m1/figures"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | VisualizerConfig | Dataclass with DPI, format, colors, output_dir |

---

## Experiment YAML Configs

Two condition configs for copy-paste use in run scripts:

### Binary Condition

```yaml
# config_binary.yaml
model_name: "deepseek-ai/deepseek-coder-6.7b-instruct"
dtype: "bfloat16"
dataset_name: "codeparrot/apps"
min_test_cases: 5
max_prompt_tokens: 512
group_size: 8
prompt_batch_size: 1
max_new_tokens: 512
temperature: 1.0
learning_rate: 1.0e-6
clip_ratio: 0.2
kl_beta: 0.04
warmup_steps: 100
train_steps: 1000
checkpoint_steps: [200, 400, 600, 800, 1000]
output_dir: "outputs/h-m1/binary"
sandbox_timeout: 3
reward_mode: "binary"
seed: 42
eval_humaneval_at_steps: [200, 400, 600, 800, 1000]
eval_mbpp_at_step: 1000
eval_apps_val_at_step: 1000
apps_val_size: 500
bootstrap_n: 1000
fraction_partial_alert_threshold: 0.05
```

### Ratio Condition

```yaml
# config_ratio.yaml  — identical to binary except:
model_name: "deepseek-ai/deepseek-coder-6.7b-instruct"
dtype: "bfloat16"
dataset_name: "codeparrot/apps"
min_test_cases: 5
max_prompt_tokens: 512
group_size: 8
prompt_batch_size: 1
max_new_tokens: 512
temperature: 1.0
learning_rate: 1.0e-6
clip_ratio: 0.2
kl_beta: 0.04
warmup_steps: 100
train_steps: 1000
checkpoint_steps: [200, 400, 600, 800, 1000]
output_dir: "outputs/h-m1/ratio"
sandbox_timeout: 3
reward_mode: "ratio"
seed: 42
eval_humaneval_at_steps: [200, 400, 600, 800, 1000]
eval_mbpp_at_step: 1000
eval_apps_val_at_step: 1000
apps_val_size: 500
bootstrap_n: 1000
fraction_partial_alert_threshold: 0.05
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale for non-standard values (kl_beta, warmup_steps, max_new_tokens, sandbox_timeout)
- [x] Subtask count within budget (1/1)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] H-E1 actual code verified (field names: model_name, dtype, dataset_name, min_test_cases, max_prompt_tokens, group_size, prompt_batch_size, max_new_tokens, temperature, learning_rate, clip_ratio, kl_beta, warmup_steps, train_steps, checkpoint_step, output_dir, sandbox_timeout, reward_mode, seed)
- [x] Inherited Configuration section included
