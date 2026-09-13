from dataclasses import dataclass, field

@dataclass
class Config:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 10  # ponytail: PoC smoke test, full 100 for Phase 5
    epochs_celeba: int = 50
    seed: int = 42

    smoothing_window: int = 5
    detection_threshold: float = -0.01
    search_fraction: float = 0.5

    lr_milestones: list = field(default_factory=lambda: [30, 60])
    lr_gamma: float = 0.1

    track_gradients: bool = True
    minority_group_id: int = 3
    majority_group_id: int = 0
    gradient_aggregation: str = "epoch_mean"

    correlation_threshold: float = 0.7
    inflection_detection_window: int = 5

    datasets: list = field(default_factory=lambda: ["waterbirds"])
    data_root: str = "./data"
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./checkpoints"
    checkpoint_every: int = 1

CONFIG = Config()
