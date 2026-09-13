"""H-M3 Configuration: Linear Correctness Probe"""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HM3Config:
    seed: int = 42
    d_model: int = 4096
    n_train: int = 9500
    n_val: int = 1700
    layer: str = "l19"  # Using H-M1 cache (L19, 60% depth) - close to L15 spec
    h_m1_cache_folder: str = "../h-m1/code/cache"

    baseline_n_seeds: int = 5

    probe_C: float = 1e-3
    probe_max_iter: int = 2000
    probe_solver: str = "lbfgs"
    probe_class_weight: str = "balanced"

    mlp_hidden_layer_sizes: tuple = (256,)
    mlp_max_iter: int = 500
    mlp_early_stopping: bool = True

    auroc_gate: float = 0.70
    mechanism_auroc_min: float = 0.55
    weight_norm_min: float = 1e-6
    pred_std_min: float = 0.01

    figures_dir: str = "figures"
    gate_comparison_fig: str = "figures/gate_comparison.png"
    roc_curve_fig: str = "figures/roc_curve.png"
    results_json: str = "results.json"
