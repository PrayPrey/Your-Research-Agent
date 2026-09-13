"""H-M4 Configuration: Probe vs Output-Level Baselines"""
from dataclasses import dataclass


@dataclass(frozen=True)
class HM4Config:
    seed: int = 42
    model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    torch_dtype: str = "float16"

    # H-M1 cache / H-M3 probe reuse
    h_m1_cache_folder: str = "../../h-m1/code/cache"
    h_m3_code_path: str = "../../h-m3/code"
    n_train: int = 9500
    n_val: int = 200  # PoC validation: reduced from 1700

    # Probe params (identical to H-M3)
    probe_c: float = 1e-3
    probe_max_iter: int = 2000
    probe_solver: str = "lbfgs"
    probe_class_weight: str = "balanced"

    # Generation
    max_new_tokens: int = 50
    do_sample: bool = False

    # Gates
    delta_gate: float = 0.05
    probe_auroc_min: float = 0.88

    # Output paths
    figures_dir: str = "figures"
    gate_comparison_fig: str = "figures/gate_comparison.png"
    roc_curve_fig: str = "figures/roc_curve.png"
    dist_fig: str = "figures/confidence_distributions.png"
    scatter_fig: str = "figures/score_scatter.png"
    results_json: str = "results.json"
