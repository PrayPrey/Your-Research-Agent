# Configuration: H-M1 RLHF Reward Model Smoothing

Applied: TRL RewardTrainer + PEFT LoRA config pattern (dataclass, single source of truth)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (matches architecture's `03_architecture.md` green-field finding)
**Config Files Found**: None
**Pattern Used**: dataclass (single `HM1Config`, mirrors architecture spec)

---

## M1-1: Config & Scaffolding [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/TRL/PEFT dataclass defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class HM1Config:
    # Model / data
    base_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"
    dataset_subsets: tuple = ("helpful-base", "helpful-online", "harmless-base")
    max_length: int = 512

    # Splits
    train_frac: float = 0.90
    val_frac: float = 0.05
    test_frac: float = 0.05
    test_sample_size: int = 5000
    interpolation_pair_count: int = 500
    n_interp_steps: int = 10

    # LoRA
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: tuple = ("q_proj", "v_proj", "k_proj", "o_proj")

    # Training
    per_device_train_batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 1e-4
    num_train_epochs: int = 1
    center_rewards_coefficient: float = 0.01
    max_grad_norm: float = 1.0  # Non-standard: clipping per brief Section 10 risk mitigation
    bf16: bool = True
    gradient_checkpointing: bool = True
    logging_steps: int = 50
    eval_steps: int = 500
    save_steps: int = 1000
    checkpoint_steps: tuple = (1000, 5000, 10000)

    # Paths / repro
    output_dir: str = "./reward_model_h-m1"
    metrics_output_path: str = "./smoothness_metrics.json"
    plot_output_path: str = "./reward_distribution.png"
    seed: int = 42

    # Success thresholds
    threshold_gradient_norm: float = 10.0
    threshold_bimodality: float = 0.55
    threshold_interp_error: float = 0.3


def get_reward_config(cfg: HM1Config) -> "trl.RewardConfig":
    from trl import RewardConfig
    return RewardConfig(
        output_dir=cfg.output_dir,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        num_train_epochs=cfg.num_train_epochs,
        learning_rate=cfg.learning_rate,
        max_length=cfg.max_length,
        center_rewards_coefficient=cfg.center_rewards_coefficient,
        max_grad_norm=cfg.max_grad_norm,
        bf16=cfg.bf16,
        gradient_checkpointing=cfg.gradient_checkpointing,
        logging_steps=cfg.logging_steps,
        eval_strategy="steps",
        eval_steps=cfg.eval_steps,
        save_strategy="steps",
        save_steps=cfg.save_steps,
        seed=cfg.seed,
    )


def get_peft_config(cfg: HM1Config) -> "peft.LoraConfig":
    from peft import LoraConfig
    return LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=list(cfg.lora_target_modules),
        modules_to_save=["score"],
        task_type="SEQ_CLS",
    )
```

### Subtasks [4/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Define HM1Config | All fields above with defaults |
| C-1-2 | get_reward_config() | Build trl.RewardConfig from HM1Config |
| C-1-3 | get_peft_config() | Build peft.LoraConfig from HM1Config |
| C-1-4 | Seed utility | `set_seed(cfg.seed)` wrapper (torch/numpy/random) |

---

## Environment Variables

```bash
export HF_TOKEN="<hf_access_token>"          # required: gated meta-llama/Llama-2-7b-hf
export HF_HOME="./.cache/huggingface"          # optional: dataset/model cache location
export CUDA_VISIBLE_DEVICES="0"                # single A100 80GB per brief compute reqs
```

## Config Usage (Downstream Modules)

All modules (`data.py`, `model.py`, `train.py`, `metrics/*`, `baselines.py`, `evaluate.py`) accept a single `HM1Config` instance — no per-module config duplication. Thresholds (`threshold_*` fields) are read directly by `evaluate.py` for PASS/FAIL determination against PRD Section 6 primary criteria.
