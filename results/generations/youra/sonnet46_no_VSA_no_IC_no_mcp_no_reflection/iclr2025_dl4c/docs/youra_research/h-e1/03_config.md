# Config: H-E1
## Binary vs Ratio Reward Signal in GRPO Training

**Hypothesis:** H-E1 | **Type:** EXISTENCE (PoC)
**Date:** 2026-08-31

Applied: Single-dataclass config pattern (one source of truth, imported by all modules)
Applied: DAPO paper defaults (arXiv 2503.14476) for GRPO hyperparameters
Applied: Hardcoded seed + dtype for reproducibility

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field - new config design, Serena skipped
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## GRPOConfig Dataclass

```python
# code/config.py
from dataclasses import dataclass

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
    prompt_batch_size: int = 64
    max_new_tokens: int = 512
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
    reward_mode: str = "binary"   # "binary" or "ratio"
    seed: int = 42
```

---

## YAML Schema (`configs/experiment_config.yaml`)

```yaml
model_name: "deepseek-ai/deepseek-coder-6.7b-instruct"
dtype: "bfloat16"

dataset_name: "codeparrot/apps"
min_test_cases: 5
max_prompt_tokens: 1024

group_size: 8
prompt_batch_size: 64
max_new_tokens: 512
temperature: 1.0

learning_rate: 1.0e-6
clip_ratio: 0.2
kl_beta: 0.01
warmup_steps: 10
train_steps: 500

checkpoint_step: 200
output_dir: "outputs"

sandbox_timeout: 5

reward_mode: "binary"   # override to "ratio" for ratio condition
seed: 42
```

---

## Environment Setup

```
torch==2.3.1
transformers==4.44.0
trl==0.9.6
datasets==2.20.0
accelerate==0.33.0
numpy==1.26.4
scipy==1.13.1
matplotlib==3.9.1
pandas==2.2.2
```

Install:
```bash
pip install torch==2.3.1 transformers==4.44.0 trl==0.9.6 datasets==2.20.0 \
    accelerate==0.33.0 numpy==1.26.4 scipy==1.13.1 matplotlib==3.9.1 pandas==2.2.2
```

---

## Hyperparameter Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| learning_rate | 1e-6 | DAPO paper standard for 7B RLEF fine-tuning; prevents catastrophic forgetting |
| group_size | 8 | Standard GRPO G; balances advantage estimation quality vs. GPU memory |
| clip_ratio | 0.2 | Standard PPO/GRPO ε; conservative policy update bound |
| kl_beta | 0.01 | Light KL regularization; keeps model close to base without blocking learning |
| prompt_batch_size | 64 | DAPO default; fits 6.7B model on typical 40GB GPU with G=8 |
| max_new_tokens | 512 | Sufficient for APPS solutions; caps rollout compute |
| temperature | 1.0 | Maximum diversity within group; essential for non-degenerate advantage estimates |
| warmup_steps | 10 | Minimal warmup for EXISTENCE PoC; avoids large early gradient spikes |
| train_steps | 500 | Sufficient to detect gradient norm signal difference; per PRD requirement |
| checkpoint_step | 200 | Mid-run eval point to catch early signal divergence |
| sandbox_timeout | 5 | Prevents runaway code execution; standard PoC safety margin |
| min_test_cases | 5 | Ensures ratio reward has non-trivial granularity (vs. binary = 0/1) |
| seed | 42 | Single fixed seed per EXISTENCE protocol |
| dtype | bfloat16 | Standard for 7B inference/training on modern GPUs; memory-efficient |

---

## Condition Matrix

| Field | binary_condition | ratio_condition |
|-------|-----------------|-----------------|
| reward_mode | "binary" | "ratio" |
| All other fields | identical | identical |
