from dataclasses import dataclass, field


@dataclass
class Config:
    data_dir: str = "data/mnist_inrs"
    data_url: str = "https://www.dropbox.com/scl/fi/4xmx2e3yzz7u8a0xw6n0n/mnist_inrs.zip?rlkey=ys9cz4wqxqwxsxzjxvqxzxzjx&dl=1"
    batch_size: int = 64
    num_workers: int = 2
    train_split: float = 0.8

    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    dws_hidden: int = 128
    mlp_hidden: list = field(default_factory=lambda: [512, 256, 128])
    dropout: float = 0.1
    num_classes: int = 10

    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    cosine_t_max: int = 50
    seed: int = 42
    device: str = "cuda"

    results_path: str = "results/results.json"
    fig_dir: str = "results/figures"
    checkpoint_dir: str = "results/checkpoints"
