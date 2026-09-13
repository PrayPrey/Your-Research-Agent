import os
from dataclasses import dataclass, field
from typing import List, Optional

os.environ["CUDA_VISIBLE_DEVICES"] = os.getenv("CUDA_VISIBLE_DEVICES", "0")
os.environ["WANDB_DISABLED"] = os.getenv("WANDB_DISABLED", "true")
os.environ["WANDB_PROJECT"] = os.getenv("WANDB_PROJECT", "youra-h-e1")


@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])


@dataclass
class TrainingConfig:
    model_name: str = ""
    condition: str = ""
    output_dir: str = ""
    max_seq_length: int = 32768
    per_device_train_batch_size: int = 1
    gradient_accumulation_steps: int = 16
    num_train_epochs: int = 1
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    lr_scheduler_type: str = "cosine"
    seed: int = 42
    kv_budget_ratio: float = 0.5
    fp16: bool = True
    bf16: bool = False
    dataloader_num_workers: int = 4
    save_strategy: str = "no"
    logging_steps: int = 10
    report_to: str = "none"
    run_name: Optional[str] = None
    lora: LoRAConfig = field(default_factory=LoRAConfig)


def get_all_configs() -> List[TrainingConfig]:
    BASE_OUTPUT = "outputs/h-e1"
    return [
        TrainingConfig(
            model_name="meta-llama/Llama-2-7b-hf",
            condition="baseline",
            output_dir=f"{BASE_OUTPUT}/llama2-7b-baseline",
            run_name="h-e1-llama2-baseline",
        ),
        TrainingConfig(
            model_name="meta-llama/Llama-2-7b-hf",
            condition="eviction-aware",
            output_dir=f"{BASE_OUTPUT}/llama2-7b-eviction-aware",
            run_name="h-e1-llama2-eviction",
        ),
        TrainingConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            condition="baseline",
            output_dir=f"{BASE_OUTPUT}/mistral-7b-baseline",
            run_name="h-e1-mistral-baseline",
        ),
        TrainingConfig(
            model_name="mistralai/Mistral-7B-v0.1",
            condition="eviction-aware",
            output_dir=f"{BASE_OUTPUT}/mistral-7b-eviction-aware",
            run_name="h-e1-mistral-eviction",
        ),
    ]


def validate_config(cfg: TrainingConfig) -> None:
    assert cfg.condition in ("baseline", "eviction-aware"), \
        f"condition must be 'baseline' or 'eviction-aware', got: {cfg.condition}"
    assert cfg.model_name != "", "model_name must be set"
    assert cfg.output_dir != "", "output_dir must be set"
    assert 0.0 < cfg.kv_budget_ratio < 1.0, \
        f"kv_budget_ratio must be in (0, 1), got: {cfg.kv_budget_ratio}"
    assert cfg.lora.rank > 0 and (cfg.lora.rank & (cfg.lora.rank - 1)) == 0, \
        f"LoRA rank should be power of 2, got: {cfg.lora.rank}"
    assert not (cfg.fp16 and cfg.bf16), "fp16 and bf16 cannot both be True"
    os.makedirs(cfg.output_dir, exist_ok=True)
