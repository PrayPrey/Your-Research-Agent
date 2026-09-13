from dataclasses import dataclass, field

@dataclass
class Config:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    epochs_celeba: int = 50
    seed: int = 42

    smoothing_window: int = 5
    detection_threshold: float = -0.01
    search_fraction: float = 0.5

    ablation_smoothing_windows: list = field(default_factory=lambda: [3, 5, 7])
    ablation_thresholds: list = field(default_factory=lambda: [-0.005, -0.01, -0.02])

    datasets: list = field(default_factory=lambda: ["waterbirds", "celebA"])
    data_root: str = "./data"
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./checkpoints"
    checkpoint_every: int = 1

CONFIG = Config()
