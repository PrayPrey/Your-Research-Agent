"""Configuration for H-M1 RLHF Reward Model Smoothing experiment."""
from dataclasses import dataclass
import random
import numpy as np
import torch


@dataclass
class HM1Config:
    # Model / data
    base_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"
    max_length: int = 512

    # Splits
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
    max_grad_norm: float = 1.0
    bf16: bool = True
    gradient_checkpointing: bool = True
    logging_steps: int = 50
    eval_steps: int = 500
    save_steps: int = 1000
    checkpoint_steps: tuple = (1000, 5000, 10000)

    # Paths
    output_dir: str = "./reward_model_h-m1"
    metrics_output_path: str = "./smoothness_metrics.json"
    plot_output_path: str = "./reward_distribution.png"
    seed: int = 42

    # Success thresholds
    threshold_gradient_norm: float = 10.0
    threshold_bimodality: float = 0.55
    threshold_interp_error: float = 0.3


def get_reward_config(cfg: HM1Config):
    import torch
    from trl import RewardConfig
    use_bf16 = cfg.bf16 and torch.cuda.is_available()
    return RewardConfig(
        output_dir=cfg.output_dir,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        num_train_epochs=cfg.num_train_epochs,
        learning_rate=cfg.learning_rate,
        max_length=cfg.max_length,
        center_rewards_coefficient=cfg.center_rewards_coefficient,
        max_grad_norm=cfg.max_grad_norm,
        bf16=use_bf16,
        gradient_checkpointing=cfg.gradient_checkpointing,
        logging_steps=cfg.logging_steps,
        eval_strategy="steps",
        eval_steps=cfg.eval_steps,
        save_strategy="steps",
        save_steps=cfg.save_steps,
        seed=cfg.seed,
        remove_unused_columns=False,
    )


def get_peft_config(cfg: HM1Config):
    from peft import LoraConfig
    return LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=list(cfg.lora_target_modules),
        modules_to_save=["score"],
        task_type="SEQ_CLS",
    )


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
