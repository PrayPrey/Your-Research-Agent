from dataclasses import dataclass, field
from typing import List, Tuple, Optional


@dataclass
class ExperimentConfig:
    tasks: List[str] = field(default_factory=lambda: ["backdoor", "accuracy"])
    architectures: List[str] = field(default_factory=lambda: ["mlp", "dws", "nft"])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    n_train: int = 600
    n_test: int = 200
    epochs: int = 100
    lr: float = 1e-4
    batch_size: int = 32
    hidden_dim: int = 128
    weight_shapes: Optional[List[Tuple[int, int]]] = None
    param_count_tolerance: float = 0.10
    anova_alpha: float = 0.05
    device: str = "cuda"
    results_path: str = "outputs/results.json"
    fig_dir: str = "../figures"


@dataclass
class ExperimentResult:
    task: str
    architecture: str
    seed: int
    metric_value: float
    secondary_metric: Optional[float] = None
    train_time: float = 0.0
