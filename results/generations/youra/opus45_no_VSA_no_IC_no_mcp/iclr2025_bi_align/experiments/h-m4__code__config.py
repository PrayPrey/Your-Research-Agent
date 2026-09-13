"""H-M4 Configuration: Differential Benchmark Profiles"""
from dataclasses import dataclass, field
from typing import List
import os
import random
import numpy as np
import torch


@dataclass
class HM4Config:
    # Base model
    base_model: str = "meta-llama/Llama-2-7b-hf"

    # Checkpoint resolution (h-m3 outputs)
    checkpoint_root: str = "../h-m3/code/checkpoints"
    seeds: List[int] = field(default_factory=lambda: [42, 137, 256, 512, 1024])
    methods: List[str] = field(default_factory=lambda: ["dpo", "rlhf"])

    # Benchmark dataset paths
    truthfulqa_path: str = "truthfulqa/truthful_qa"
    truthfulqa_subset: str = "multiple_choice"
    hh_rlhf_path: str = "Anthropic/hh-rlhf"
    hh_helpful_data_dir: str = "helpful-base"
    hh_harmless_data_dir: str = "harmless-base"

    # Eval settings
    max_length: int = 512
    batch_size: int = 8
    device: str = "cuda"

    # Effect size thresholds (from PRD FR-5)
    d_large_threshold: float = 0.3
    d_small_threshold: float = 0.15
    profile_corr_threshold: float = 0.8
    correlation_diff_threshold: float = 0.3

    # Output paths
    output_dir: str = "./outputs"
    results_path: str = "./outputs/benchmark_results.json"
    analysis_path: str = "./outputs/differential_analysis.json"
    profile_plot_path: str = "./outputs/profile_comparison.png"

    seed: int = 42

    # Simulation mode (no trained checkpoints available from h-m3)
    simulation_mode: bool = True

    def __post_init__(self):
        os.makedirs(self.output_dir, exist_ok=True)


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def resolve_checkpoint_path(cfg: HM4Config, method: str, seed: int) -> str:
    """Resolve checkpoint path for a given method and seed."""
    return os.path.join(cfg.checkpoint_root, f"{method}_seed_{seed}")


def verify_checkpoints_exist(cfg: HM4Config) -> dict:
    """Verify all 10 checkpoint paths exist."""
    found = []
    missing = []
    for method in cfg.methods:
        for seed in cfg.seeds:
            path = resolve_checkpoint_path(cfg, method, seed)
            if os.path.exists(path):
                found.append(path)
            else:
                missing.append(path)
    return {"found": found, "missing": missing, "all_present": len(missing) == 0}


def model_id(method: str, seed: int) -> str:
    """Generate model identifier."""
    return f"{method}_seed{seed}"
