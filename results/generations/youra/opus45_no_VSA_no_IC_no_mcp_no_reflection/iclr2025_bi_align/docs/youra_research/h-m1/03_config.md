# Configuration: H-M1 (Combined PPO Reward)

**Type:** MECHANISM | **Format:** Python Dataclass

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1, VALIDATED prerequisite)
**Status**: Config classes verified from actual H-E1 code
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`, `model.py`
**Pattern Used**: dataclass

Verified from `h-e1/code/model.py`: `IFEvalRewardSignal(soft_margin: float = 0.1)`, method `forward(response: str, constraints: list[dict]) -> torch.Tensor`. H-E1 used `model_id: str = "mistralai/Mistral-7B-Instruct-v0.2"` — H-M1 uses a different base model (Llama-3-8B-Instruct) per PRD, so `model_id` is NOT inherited, only `soft_margin` and the reward module interface are reused.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/model.py (ACTUAL CODE) — reused as-is, not reimplemented
# class IFEvalRewardSignal(nn.Module):
#     def __init__(self, soft_margin: float = 0.1): ...
#     def forward(self, response: str, constraints: list[dict]) -> torch.Tensor: ...
IFEVAL_SOFT_MARGIN: float = 0.1  # inherited default from H-E1
```

---

## Configuration (Python Dataclasses)

**Applied**: Standard TRL PPOTrainer config pattern

```python
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ModelConfig:
    base_model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    reward_model_id: str = "OpenAssistant/reward-model-deberta-v3-large-v2"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"


@dataclass
class DataConfig:
    ultrafeedback_id: str = "openbmb/UltraFeedback"
    ultrafeedback_split: str = "train"
    ifeval_id: str = "google/IFEval"
    ifeval_train_ratio: float = 0.7  # 70/30 train/test split
    ifeval_num_prompts: int = 541
    max_prompt_length: int = 512
    max_new_tokens: int = 512


@dataclass
class RewardConfig:
    alpha: float = 0.5   # R_helpfulness weight
    beta: float = 0.5    # R_IFEval weight
    ifeval_soft_margin: float = 0.1  # inherited from H-E1 IFEvalRewardSignal


@dataclass
class PPOConfig:
    learning_rate: float = 1.41e-5
    batch_size: int = 64
    mini_batch_size: int = 8
    ppo_epochs: int = 4
    kl_coeff: float = 0.05          # init_kl_coef in trl.PPOConfig
    clip_range: float = 0.2         # cliprange
    value_clip_range: float = 0.2   # cliprange_value
    total_steps: int = 1000
    seed: int = 42


@dataclass
class LoggingConfig:
    log_interval: int = 10          # reward/kl/loss metrics
    checkpoint_interval: int = 250  # model checkpoint + IFEval eval
    output_dir: str = "h-m1/checkpoints"
    logger: Literal["wandb", "tensorboard"] = "wandb"


@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
```

### Ablation Variants (FR-6, PRD Section 3)

```python
# T1-Combined (primary, gate-relevant)
T1_COMBINED = RewardConfig(alpha=0.5, beta=0.5)

# B2-Helpfulness-Only (single-objective baseline)
B2_HELPFULNESS_ONLY = RewardConfig(alpha=1.0, beta=0.0)

# Ablation: helpfulness-dominant
ABLATION_ALPHA_DOMINANT = RewardConfig(alpha=0.7, beta=0.3)

# Ablation: controllability-dominant
ABLATION_BETA_DOMINANT = RewardConfig(alpha=0.3, beta=0.7)

# B1-SFT: no RL — PPO not run; use base model as-is (no RewardConfig needed)
```

### Failure-Response Overrides (Section 8, brief)

```python
# If KL > 10.0 or NaN losses observed:
PPO_RECOVERY = PPOConfig(learning_rate=5e-6, kl_coeff=0.1)
```

---

## YAML Configuration Schema

```yaml
# h-m1/config.yaml
model:
  base_model_id: meta-llama/Meta-Llama-3-8B-Instruct
  reward_model_id: OpenAssistant/reward-model-deberta-v3-large-v2
  torch_dtype: bfloat16
  device_map: auto

data:
  ultrafeedback_id: openbmb/UltraFeedback
  ultrafeedback_split: train
  ifeval_id: google/IFEval
  ifeval_train_ratio: 0.7
  ifeval_num_prompts: 541
  max_prompt_length: 512
  max_new_tokens: 512

reward:
  alpha: 0.5
  beta: 0.5
  ifeval_soft_margin: 0.1

ppo:
  learning_rate: 1.41e-5
  batch_size: 64
  mini_batch_size: 8
  ppo_epochs: 4
  kl_coeff: 0.05
  clip_range: 0.2
  value_clip_range: 0.2
  total_steps: 1000
  seed: 42

logging:
  log_interval: 10
  checkpoint_interval: 250
  output_dir: h-m1/checkpoints
  logger: wandb
```

---

## Subtasks [4/4 used — within FULL tier budget]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M1-1 | Config dataclasses | `ModelConfig`, `DataConfig`, `RewardConfig`, `PPOConfig`, `LoggingConfig`, `ExperimentConfig` in `config.py` |
| C-M1-2 | Ablation variant constants | `T1_COMBINED`, `B2_HELPFULNESS_ONLY`, `ABLATION_ALPHA_DOMINANT`, `ABLATION_BETA_DOMINANT` |
| C-M1-3 | YAML schema | `config.yaml` mirroring dataclass defaults for external overrides |
| C-M1-4 | Recovery config | `PPO_RECOVERY` override for divergence failure response (Section 8) |
