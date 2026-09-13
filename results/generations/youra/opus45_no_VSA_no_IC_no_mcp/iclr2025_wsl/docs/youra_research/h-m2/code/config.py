from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # Data
    data_dir: str = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_wsl/docs/youra_research/h-e1/code/data/mnist_inrs"
    batch_size: int = 64
    num_workers: int = 2
    train_split: float = 0.8

    # Model architecture
    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    dws_hidden: int = 128
    mlp_hidden: List[int] = field(default_factory=lambda: [512, 256, 128])
    dropout: float = 0.1
    num_classes: int = 10

    # Training
    lr: float = 1e-4
    weight_decay: float = 1e-2
    epochs: int = 10  # ponytail: PoC - ceiling AUC 1.0 at 20 epochs, reduce further
    cosine_t_max: int = 10
    device: str = "cuda"

    seed: int = 42  # For data split consistency

    # h-m2 specific: sample efficiency
    seeds: List[int] = field(default_factory=lambda: [42, 123, 7])
    fractions: List[float] = field(default_factory=lambda: [0.25, 0.50, 1.0])

    # Tracking (inherited, unused in h-m2)
    track_every: int = 1
    snapshot_every: int = 10

    # Output paths
    results_path: str = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_wsl/docs/youra_research/h-m2/code/outputs/results.json"
    fig_dir: str = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_wsl/docs/youra_research/h-m2/figures"
