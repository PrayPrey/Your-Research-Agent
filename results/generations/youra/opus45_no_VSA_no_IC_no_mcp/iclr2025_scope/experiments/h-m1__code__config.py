from dataclasses import dataclass, field
from typing import Literal
import os

@dataclass
class ModelConfig:
    hidden_dim: int = 768
    embedding_dim: int = 32
    num_tasks: int = 6

@dataclass
class TrainingConfig:
    lr: float = 1e-4
    batch_size: int = 32
    epochs: int = 10
    optimizer: Literal["adam", "adamw", "sgd"] = "adamw"
    l2_reg_C: float = 1.0
    seed: int = 42

@dataclass
class DataConfig:
    dataset_root: str = "data/superglue"
    tasks: list[str] = field(default_factory=lambda: ["boolq", "cb", "copa", "rte", "wic", "wsc"])
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15

@dataclass
class EvaluationConfig:
    metrics: list[str] = field(default_factory=lambda: ["accuracy", "silhouette_score"])
    silhouette_threshold: float = 0.25
    accuracy_threshold: float = 0.125

@dataclass
class AblationConfig:
    embedding_dim_variants: list[int] = field(default_factory=lambda: [16, 32, 64])

@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    ablation: AblationConfig = field(default_factory=AblationConfig)

    def __post_init__(self):
        valid_tasks = {"boolq", "cb", "copa", "rte", "wic", "wsc"}
        assert set(self.data.tasks) <= valid_tasks, "unknown task in tasks list"
        assert abs(self.data.train_split + self.data.val_split + self.data.test_split - 1.0) < 1e-6
        assert self.training.batch_size > 0 and self.training.epochs > 0


def load_config() -> ExperimentConfig:
    cfg = ExperimentConfig()
    cfg.training.lr = float(os.environ.get("HM1_LR", cfg.training.lr))
    cfg.training.batch_size = int(os.environ.get("HM1_BATCH_SIZE", cfg.training.batch_size))
    cfg.training.epochs = int(os.environ.get("HM1_EPOCHS", cfg.training.epochs))
    cfg.model.embedding_dim = int(os.environ.get("HM1_EMBEDDING_DIM", cfg.model.embedding_dim))
    cfg.data.dataset_root = os.environ.get("HM1_DATA_ROOT", cfg.data.dataset_root)
    return cfg
