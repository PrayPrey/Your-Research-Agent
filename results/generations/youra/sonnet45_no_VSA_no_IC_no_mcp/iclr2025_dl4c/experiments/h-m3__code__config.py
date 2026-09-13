"""Configuration for h-m3: Supervised AI Feedback Model"""
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class DataConfig:
    """Dataset configuration"""
    cache_dir: str = ".data_cache/datasets/humaneval_mbpp"
    train_ratio: float = 0.7
    val_ratio: float = 0.15
    test_ratio: float = 0.15
    random_seed: int = 42
    min_test_samples: int = 170  # Gate requirement

@dataclass
class ModelConfig:
    """Model architecture configuration"""
    model_name: str = "microsoft/codebert-base"
    cache_dir: str = ".data_cache/models/codebert"
    max_length: int = 512
    num_labels: int = 1  # Regression
    dropout: float = 0.1

@dataclass
class TrainingConfig:
    """Training hyperparameters"""
    output_dir: str = "./outputs/supervised_feedback"
    num_train_epochs: int = 5
    per_device_train_batch_size: int = 8
    learning_rate: float = 2e-5
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    eval_strategy: str = "epoch"
    save_strategy: str = "epoch"
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_loss"
    early_stopping_patience: int = 2
    logging_steps: int = 10

@dataclass
class ExperimentConfig:
    """Full experiment configuration"""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)

    # Gate criteria
    gate_correlation_threshold: float = 0.7
    gate_pvalue_threshold: float = 0.05

    # Baselines (from h-e1)
    baseline_ai_human_corr: float = 0.485  # h-e1 average

def get_config() -> ExperimentConfig:
    return ExperimentConfig()
