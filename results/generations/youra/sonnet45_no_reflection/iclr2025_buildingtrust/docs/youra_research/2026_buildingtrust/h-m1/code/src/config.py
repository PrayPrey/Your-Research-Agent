"""Configuration for H-E1 Experiment"""
from dataclasses import dataclass
from typing import List

@dataclass
class ExperimentConfig:
    """Experiment hyperparameters and settings"""

    # Model configuration
    model_id: str = "gpt2"  # Using GPT-2 for PoC (Llama-3 requires authentication)
    lora_rank: int = 8
    lora_alpha: int = 16  # H-M1: Updated from h-e1 based on PEFT docs
    lora_dropout: float = 0.1
    target_modules: List[str] = None

    # Training configuration
    learning_rate: float = 1e-4
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 2
    max_grad_norm: float = 1.0
    warmup_ratio: float = 0.1

    # Dataset configuration
    max_length: int = 512
    num_proc: int = 4

    # Experiment configuration
    num_replicates: int = 3  # PoC uses 3 instead of 20
    target_dimensions: List[str] = None
    random_seeds: List[int] = None

    # Evaluation configuration
    eval_batch_size: int = 8

    def __post_init__(self):
        if self.target_modules is None:
            # GPT-2 uses c_attn for attention layers
            self.target_modules = ["c_attn"]
        if self.target_dimensions is None:
            self.target_dimensions = ["truthfulness", "fairness", "robustness"]
        if self.random_seeds is None:
            self.random_seeds = [42, 43, 44]

def get_default_config() -> ExperimentConfig:
    """Get default experiment configuration"""
    return ExperimentConfig()
