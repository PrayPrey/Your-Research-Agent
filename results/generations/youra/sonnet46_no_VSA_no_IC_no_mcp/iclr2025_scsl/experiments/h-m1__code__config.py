from dataclasses import dataclass, field
from typing import List
import os


@dataclass
class ExperimentConfig:
    # --- Paths ---
    data_root: str = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/data"
    waterbirds_root: str = "/home/PrayPrey/.wilds_cache"
    cub_root: str = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/data/CUB_200_2011"
    places365_root: str = "/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/data/places365"
    checkpoint_dir: str = "./checkpoints/h-m1"
    results_dir: str = "./results/h-m1"
    figures_dir: str = "./docs/youra_research/h-m1/figures"

    # --- Dataset ---
    image_size: int = 224
    normalize_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalize_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    n_places365: int = 10000

    # --- Training ---
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
    epochs: int = 50
    batch_size: int = 256
    lr: float = 0.03
    momentum: float = 0.9
    weight_decay: float = 1e-4
    temperature: float = 0.5

    # --- Model ---
    proj_hidden_dim: int = 2048
    proj_out_dim: int = 128
    backbone_out_dim: int = 2048

    # --- Linear Probe ---
    probe_C: float = 1.0
    probe_max_iter: int = 1000
    probe_solver: str = "lbfgs"

    # --- Mechanism Verification ---
    mechanism_pixel_diff_threshold: float = 0.05

    # --- Device ---
    device: str = "cuda"

    # --- Collapse Detection ---
    collapse_task_acc_threshold: float = 0.534

    def checkpoint_path(self, condition: str, seed: int) -> str:
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        return f"{self.checkpoint_dir}/{condition}_seed{seed}_epoch{self.epochs}.pt"

    def result_path(self, condition: str, seed: int) -> str:
        os.makedirs(self.results_dir, exist_ok=True)
        return f"{self.results_dir}/{condition}_seed{seed}.json"
