"""Configuration dataclasses for H-M1 IPCR Routing experiment."""
from dataclasses import dataclass, field
from typing import List

@dataclass
class LoRAConfig:
    rank: int = 16
    alpha: int = 32
    dropout: float = 0.05
    target_modules: List[str] = field(default_factory=lambda: ["q_proj", "v_proj"])
    bias: str = "none"
    task_type: str = "CAUSAL_LM"

@dataclass
class RouterConfig:
    encoder_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    num_adapters: int = 8

@dataclass
class TrainingConfig:
    lr: float = 2e-4
    batch_size: int = 8
    epochs: int = 3
    optimizer: str = "adamw"
    weight_decay: float = 0.01
    seed: int = 42
    base_model: str = "mistralai/Mistral-7B-Instruct-v0.1"
    max_seq_length: int = 512
    gradient_accumulation_steps: int = 4

@dataclass
class EvaluationConfig:
    held_out_families: int = 8
    min_samples: int = 500
    seed: int = 42
    metrics: List[str] = field(default_factory=lambda: ["accuracy", "rouge", "exact_match"])
    significance_alpha: float = 0.05
    max_gen_length: int = 128

@dataclass
class ExperimentConfig:
    lora: LoRAConfig = field(default_factory=LoRAConfig)
    router: RouterConfig = field(default_factory=RouterConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    dataset_name: str = "Open-Orca/FLAN"
    output_dir: str = "results"
    checkpoint_dir: str = "checkpoints"
    figures_dir: str = "figures"
