# config.py
# Phase 4 Generated Code for Hypothesis: h-e1
# Generated: 2026-05-12
# Task: A-1 - Configuration Setup

from dataclasses import dataclass, asdict, field
from typing import List
import yaml
from pathlib import Path


@dataclass
class DataConfig:
    """Configuration for dataset loading and preprocessing."""
    glue_tasks: List[str] = field(default_factory=lambda: [
        "cola", "sst2", "mrpc", "qqp", "mnli", "qnli", "rte", "wnli", "stsb"
    ])
    superglue_tasks: List[str] = field(default_factory=lambda: [
        "boolq", "cb", "copa", "multirc", "record", "rte", "wic", "wsc"
    ])
    max_length: int = 512
    batch_size: int = 32
    num_workers: int = 4


@dataclass
class ModelConfig:
    """Configuration for LoRA-MoE model."""
    model_name: str = "mistralai/Mixtral-8x7B-v0.1"
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    num_lora_experts: int = 8
    top_k: int = 2
    target_modules: List[str] = field(default_factory=lambda: [
        "q_proj", "k_proj", "v_proj", "o_proj"
    ])

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.target_modules is None or len(self.target_modules) == 0:
            self.target_modules = ["q_proj", "k_proj", "v_proj", "o_proj"]


@dataclass
class TrainingConfig:
    """Configuration for training procedure."""
    learning_rate: float = 3e-4
    weight_decay: float = 0.01
    num_epochs: int = 5
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 500
    alignment_loss_weight: float = 0.01
    aux_loss_weight: float = 0.01
    seed: int = 42
    mixed_precision: str = "bf16"


@dataclass
class ExperimentConfig:
    """Complete experiment configuration."""
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    output_dir: str
    checkpoint_dir: str
    figures_dir: str

    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentConfig":
        """Load configuration from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            ExperimentConfig instance
        """
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            data=DataConfig(**data.get('data', {})),
            model=ModelConfig(**data.get('model', {})),
            training=TrainingConfig(**data.get('training', {})),
            output_dir=data.get('output_dir', './output'),
            checkpoint_dir=data.get('checkpoint_dir', './checkpoints'),
            figures_dir=data.get('figures_dir', './figures')
        )

    def to_yaml(self, path: str) -> None:
        """Save configuration to YAML file.

        Args:
            path: Path to save YAML file
        """
        data = {
            'data': asdict(self.data),
            'model': asdict(self.model),
            'training': asdict(self.training),
            'output_dir': self.output_dir,
            'checkpoint_dir': self.checkpoint_dir,
            'figures_dir': self.figures_dir
        }

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

    @classmethod
    def get_default(cls) -> "ExperimentConfig":
        """Get default configuration.

        Returns:
            ExperimentConfig with default values
        """
        return cls(
            data=DataConfig(),
            model=ModelConfig(),
            training=TrainingConfig(),
            output_dir='./output',
            checkpoint_dir='./checkpoints',
            figures_dir='./figures'
        )
