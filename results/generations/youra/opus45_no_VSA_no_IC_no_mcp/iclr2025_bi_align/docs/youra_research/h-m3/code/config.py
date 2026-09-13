"""Configuration for H-M3 Attractor Analysis experiment."""
from dataclasses import dataclass, field
from typing import List
import random
import numpy as np
import torch


@dataclass
class HM3Config:
    # Base model
    base_model: str = "meta-llama/Llama-2-7b-hf"
    dataset_name: str = "Anthropic/hh-rlhf"

    # Multi-seed config
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    quick_seeds: List[int] = field(default_factory=lambda: [42, 137])  # For quick validation
    methods: List[str] = field(default_factory=lambda: ["dpo", "rlhf"])

    # Training config (shared across methods)
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

    # DPO-specific
    beta: float = 0.1

    # PPO-specific (RLHF)
    ppo_batch_size: int = 32
    ppo_mini_batch_size: int = 4
    ppo_epochs: int = 4
    ppo_learning_rate: float = 1.41e-5

    # Paths
    output_root: str = "./h-m3_models"
    hm1_reward_checkpoint: str = "../../../h-m1/code/reward_model_h-m1_quick/final"

    # Analysis config
    n_probes: int = 1000
    n_probes_quick: int = 100
    probe_batch_size: int = 8

    # Thresholds (from experiment brief)
    silhouette_threshold: float = 0.1
    clustering_gap_threshold: float = 0.05
    cohens_d_threshold: float = 0.3
    p_value_threshold: float = 0.05

    # Output paths
    metrics_output_path: str = "./clustering_metrics.json"
    embeddings_output_path: str = "./behavior_embeddings.npy"
    visualization_path: str = "./attractor_visualization.png"
    heatmap_path: str = "./similarity_heatmap.png"

    seed: int = 42
    logging_steps: int = 50


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def get_peft_config(cfg: HM3Config):
    """Build LoRA config."""
    from peft import LoraConfig, TaskType
    return LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        lora_dropout=cfg.lora_dropout,
        target_modules=cfg.lora_target_modules,
        task_type=TaskType.CAUSAL_LM,
    )


def model_id(method: str, seed: int) -> str:
    """Generate model identifier."""
    return f"{method}_seed{seed}"
