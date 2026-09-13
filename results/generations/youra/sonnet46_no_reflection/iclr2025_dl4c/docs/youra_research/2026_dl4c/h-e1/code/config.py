from dataclasses import dataclass, field
from trl import GRPOConfig, DPOConfig


@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: int = 42
    dtype: str = "bfloat16"

    # Training — GRPO
    grpo_lr: float = 1e-6
    grpo_batch_size: int = 1
    grpo_grad_accum: int = 16
    grpo_num_generations: int = 4
    grpo_beta: float = 0.04
    grpo_steps: int = 1000
    grpo_save_steps: int = 100

    # Training — DPO
    dpo_lr: float = 5e-7
    dpo_batch_size: int = 1
    dpo_grad_accum: int = 16
    dpo_beta: float = 0.1
    dpo_steps: int = 1000
    dpo_save_steps: int = 100

    # Data
    training_dataset: str = "sahil2801/CodeAlpaca-20k"
    kl_prompt_count: int = 100
    dpo_min_pairs: int = 1000

    # Evaluation
    kl_tolerance: float = 0.05
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95
    gate_magnitude: float = 0.20

    # Paths (relative to code directory)
    output_dir: str = "outputs"
    figures_dir: str = "../figures"
    checkpoint_dir: str = "../checkpoints"


def get_config() -> ExperimentConfig:
    return ExperimentConfig()


def make_grpo_config(cfg: ExperimentConfig, output_dir: str) -> GRPOConfig:
    return GRPOConfig(
        output_dir=output_dir,
        learning_rate=cfg.grpo_lr,
        per_device_train_batch_size=cfg.grpo_batch_size,
        gradient_accumulation_steps=cfg.grpo_grad_accum,
        num_generations=cfg.grpo_num_generations,
        beta=cfg.grpo_beta,
        max_steps=cfg.grpo_steps,
        save_steps=cfg.grpo_save_steps,
        seed=cfg.seed,
        bf16=(cfg.dtype == "bfloat16"),
        fp16=(cfg.dtype == "float16"),
        dataloader_num_workers=0,
        remove_unused_columns=False,
        log_completions=False,
        report_to="none",
        gradient_checkpointing=True,
    )


def make_dpo_config(cfg: ExperimentConfig, output_dir: str) -> DPOConfig:
    return DPOConfig(
        output_dir=output_dir,
        learning_rate=cfg.dpo_lr,
        per_device_train_batch_size=cfg.dpo_batch_size,
        gradient_accumulation_steps=cfg.dpo_grad_accum,
        beta=cfg.dpo_beta,
        max_steps=cfg.dpo_steps,
        save_steps=cfg.dpo_save_steps,
        seed=cfg.seed,
        bf16=(cfg.dtype == "bfloat16"),
        fp16=(cfg.dtype == "float16"),
        dataloader_num_workers=0,
        remove_unused_columns=False,
        report_to="none",
    )
