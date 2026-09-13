from dataclasses import dataclass
import os

@dataclass
class Config:
    seed: int = 0
    n_models: int = 1000
    train_frac: float = 0.8
    lr: float = 1e-3
    weight_decay: float = 1e-4
    epochs: int = 50
    batch_size: int = 32
    nfn_channels: int = 32
    mlp_hidden_dim: int = 256
    mlp_num_layers: int = 3
    scheduler_t_max: int = 50
    scheduler_eta_min: float = 1e-6
    r2_diff_threshold: float = 0.05

    @property
    def checkpoint_dir(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "checkpoints")

    @property
    def figure_dir(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "figures")

    @property
    def results_path(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), "results.json")
