"""H-M3 experiment configuration."""
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-m3"
    conditions: list = field(default_factory=lambda: ['A', 'B', 'C', 'D', 'E', 'F'])
    seeds: list = field(default_factory=lambda: [42, 123, 456])

    weight_dim: int = 50890
    n_labels: int = 3
    label_names: list = field(default_factory=lambda: [
        "test_accuracy", "generalization_gap", "learning_rate"
    ])
    val_fraction: float = 0.1
    test_fraction: float = 0.1

    embed_dim: int = 256
    n_layers: int = 4
    nhead: int = 8
    dim_feedforward: int = 512
    dropout: float = 0.1

    lr: float = 1e-3
    weight_decay: float = 1e-4
    adam_betas: tuple = (0.9, 0.999)
    batch_size: int = 64
    max_epochs: int = 100
    es_patience: int = 10
    lr_patience: int = 5
    lr_factor: float = 0.5
    min_lr: float = 1e-5

    n_boot: int = 1000
    boot_seed: int = 42
    delta_threshold: float = 0.05

    canon_eps: float = 1e-8
    signflip_tie_value: float = 1.0

    results_path: str = "results.json"
    figures_dir: str = "../figures"
    checkpoint_dir: str = "checkpoints"

    run_frozen_experiment: bool = True
    frozen_conditions: list = field(default_factory=lambda: ['B', 'C', 'D'])


DEFAULT_CONFIG = ExperimentConfig()
