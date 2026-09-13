# Configuration: H-M2 (Bidirectional Reward Gate)

**Type:** MECHANISM | **Format:** Python Dataclass

Applied: reward-model-wrapper-pattern (weighted-sum composition, reused from H-M1)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1, VALIDATED)
**Status**: config classes verified from actual H-M1 code (per h-m1/03_config.md, itself Serena-verified against `h-m1/code/config.py`)
**Config Files Found**: `h-m1/code/config.py` (`Config`, `PPOConfig`, `RewardConfig`, `DataConfig`, `ModelConfig`, `LoggingConfig`)
**Pattern Used**: dataclass

`h-m1.code.config.Config` fields verified: `model.base_model_id`, `data.ifeval_train_ratio=0.7`, `reward.alpha`, `reward.beta`, `reward.ifeval_soft_margin`, `ppo.learning_rate=1.41e-5`, `ppo.batch_size=64`, `ppo.kl_coeff=0.05`, `ppo.total_steps=1000`, `ppo.seed=42`. H-M2 does not modify these — only adds `ModelVariant` wrapper and overrides `seed=1` per NFR-2.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE) — imported, not reimplemented
from h_m1.code.config import Config, ModelConfig, DataConfig, RewardConfig, PPOConfig, LoggingConfig

# Inherited defaults (unmodified): base_model_id, ifeval_train_ratio=0.7,
# ifeval_soft_margin=0.1, learning_rate=1.41e-5, batch_size=64, kl_coeff=0.05, total_steps=1000
```

---

## Configuration (Python Dataclasses)

```python
from dataclasses import dataclass
from h_m1.code.config import Config


@dataclass
class ModelVariant:
    name: str          # "B1".."B3", "T1".."T4"
    alpha: float
    beta: float
    train: bool         # False only for B1 (SFT-only, no PPO)
    reward_mode: str      # "none" | "helpfulness_only" | "quality_only" | "combined"


VARIANTS: list[ModelVariant] = [
    ModelVariant("B1", 0.0, 0.0, train=False, reward_mode="none"),
    ModelVariant("B2", 1.0, 0.0, train=True, reward_mode="helpfulness_only"),
    ModelVariant("B3", 0.0, 0.0, train=True, reward_mode="quality_only"),
    ModelVariant("T1", 0.2, 0.8, train=True, reward_mode="combined"),
    ModelVariant("T2", 0.4, 0.6, train=True, reward_mode="combined"),
    ModelVariant("T3", 0.6, 0.4, train=True, reward_mode="combined"),
    ModelVariant("T4", 0.8, 0.2, train=True, reward_mode="combined"),
]


def build_config(variant: ModelVariant) -> Config:
    """Returns h_m1 Config with reward.alpha/beta set from variant,
    ppo.seed overridden to 1 (NFR-2), all other fields = H-M1 defaults."""
    cfg = Config()
    cfg.reward.alpha = variant.alpha
    cfg.reward.beta = variant.beta
    cfg.ppo.seed = 1  # H-M2 fixed seed, overrides H-M1 default (42)
    return cfg
```

### PPO Training (inherited from H-M1, seed overridden)

```python
# cfg.ppo fields used as-is except seed:
# learning_rate=1.41e-5, batch_size=64, mini_batch_size=8, ppo_epochs=4,
# kl_coeff=0.05, clip_range=0.2, value_clip_range=0.2, total_steps=1000
# seed: int = 1   # NFR-2, overrides H-M1 default of 42
```

### Evaluation Config

```python
@dataclass
class EvalConfig:
    ifeval_test_size: int = 500        # ~30% held-out split (FR-3.1)
    gate_threshold_pp: float = 0.02    # ≥2pp gate (FR-4.2)
    metrics: tuple[str, ...] = ("strict_accuracy", "loose_accuracy")
    constraint_categories: int = 25    # FR-3.1
```

### Visualization Config

```python
@dataclass
class VizConfig:
    out_dir: str = "h-m2/results/figures"
    gate_chart_name: str = "gate_comparison.png"
    breakdown_chart_name: str = "constraint_breakdown.png"
    tradeoff_chart_name: str = "alpha_beta_tradeoff.png"
    dpi: int = 150
```

---

## Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-M2-1 | Variant + eval + viz configs | `ModelVariant`, `VARIANTS`, `build_config`, `EvalConfig`, `VizConfig` in `h-m2/code/config.py` |
