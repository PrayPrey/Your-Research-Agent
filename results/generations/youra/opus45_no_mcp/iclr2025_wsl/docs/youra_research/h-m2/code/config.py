from dataclasses import dataclass, field

@dataclass
class Config:
    # Data
    data_path: str = "data/dataset_cifar_small_hyp_fix.pt"
    zenodo_doi: str = "10.5281/zenodo.6620869"
    batch_size: int = 256

    # Optimization
    lr: float = 1e-3
    weight_decay: float = 1e-4
    max_epochs: int = 50
    early_stop_patience: int = 10
    lr_scheduler_factor: float = 0.5
    lr_scheduler_patience: int = 5

    # Model dims
    hidden_dim: int = 256
    embed_dim: int = 128
    predictor_hidden: int = 64
    stats_per_layer: int = 4

    # Reproducibility
    seeds: list = field(default_factory=lambda: [0, 1, 2, 3, 4])
    device: str = "cuda"

    # Output
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"

    # H-M2 Alignment (Git Re-Basin)
    use_alignment: bool = True
    alignment_reference_idx: int = 0
    alignment_algorithm: str = "greedy"
    alignment_cache_dir: str = "cache/"
    convergence_threshold: float = 0.95
