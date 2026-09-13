from dataclasses import dataclass, field


@dataclass
class ZooConfig:
    zoo_path: str = "data/cifar10_zoo.npz"
    osf_url: str = "https://osf.io/hbm72/"
    expected_n_models: int = 10_000


@dataclass
class AuditConfig:
    spearman_threshold: float = 0.95
    seed: int = 42
    split_ratios: list = field(default_factory=lambda: [0.8, 0.1, 0.1])


@dataclass
class DataLoaderConfig:
    batch_size: int = 64
    shuffle: bool = True
    num_workers: int = 0
    pin_memory: bool = True


@dataclass
class EncoderConfig:
    lr_candidates: list
    batch_size: int
    epochs: int
    lr_schedule: str
    hidden_dim: int


ENCODER_CONFIGS: dict = {
    "FlatMLP": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=256,
        epochs=50,
        lr_schedule="none",
        hidden_dim=256,
    ),
    "DWSNet": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=256,
        epochs=50,
        lr_schedule="none",
        hidden_dim=256,
    ),
    "NFT": EncoderConfig(
        lr_candidates=[1e-5, 1e-4, 5e-4],
        batch_size=64,
        epochs=100,
        lr_schedule="cosine",
        hidden_dim=128,
    ),
    "GNN": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=256,
        epochs=50,
        lr_schedule="cosine",
        hidden_dim=128,
    ),
}

SPEARMAN_AUDIT_THRESHOLD: float = 0.95


@dataclass
class ExperimentConfig:
    zoo: ZooConfig = field(default_factory=ZooConfig)
    encoders: dict = field(default_factory=lambda: ENCODER_CONFIGS)
    loader: DataLoaderConfig = field(default_factory=DataLoaderConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    n_trials: int = 3
    gate_threshold: float = 0.5
    figures_dir: str = "figures"
    seed: int = 42
    device: str = "cuda:0"
