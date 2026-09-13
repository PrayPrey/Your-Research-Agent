"""Configuration for H-M2 DPO Boundary Preservation experiment."""
from dataclasses import dataclass, field
from typing import List
import random
import numpy as np
import torch


@dataclass
class HM2Config:
    base_model: str = "meta-llama/Llama-2-7b-hf"
    ref_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"
    beta: float = 0.1
    max_length: int = 512
    max_prompt_length: int = 256
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "v_proj", "k_proj", "o_proj"]
    )
    per_device_train_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    learning_rate: float = 5e-7
    num_train_epochs: int = 1
    bf16: bool = True
    gradient_checkpointing: bool = True
    output_dir: str = "./dpo_model_h-m2"
    metrics_output_path: str = "./boundary_sharpness_metrics.json"
    plot_output_path: str = "./margin_comparison.png"
    hm1_metrics_path: str = "../../../h-m1/code/smoothness_metrics.json"
    hm1_checkpoint_path: str = "../../../h-m1/code/reward_model_h-m1_quick/final"
    seed: int = 42
    logging_steps: int = 50
    eval_steps: int = 500
    save_steps: int = 1000
    max_grad_norm: float = 1.0
    test_sample_size: int = 1000
    boundary_margin_threshold: float = 0.1
    boundary_case_count: int = 500
    threshold_boundary_accuracy: float = 0.55
    threshold_confident_ratio: float = 0.3
    threshold_sharpness_ratio: float = 1.0
    generation_max_new_tokens: int = 128


def get_dpo_config(cfg: HM2Config):
    """Build TRL DPOConfig from HM2Config."""
    from trl import DPOConfig
    return DPOConfig(
        output_dir=cfg.output_dir,
        beta=cfg.beta,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        num_train_epochs=cfg.num_train_epochs,
        learning_rate=cfg.learning_rate,
        max_length=cfg.max_length,
        max_prompt_length=cfg.max_prompt_length,
        bf16=cfg.bf16,
        gradient_checkpointing=cfg.gradient_checkpointing,
        logging_steps=cfg.logging_steps,
        eval_strategy="steps",
        eval_steps=cfg.eval_steps,
        save_strategy="steps",
        save_steps=cfg.save_steps,
        seed=cfg.seed,
        max_grad_norm=cfg.max_grad_norm,
        remove_unused_columns=False,
    )


def get_peft_config(cfg: HM2Config):
    """Build LoRA config for DPO policy."""
    from peft import LoraConfig, TaskType
    return LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=cfg.lora_target_modules,
        task_type=TaskType.CAUSAL_LM,
    )


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
