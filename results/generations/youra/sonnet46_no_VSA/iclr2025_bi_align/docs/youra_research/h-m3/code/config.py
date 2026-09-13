from dataclasses import dataclass
from typing import Tuple
import os


@dataclass
class ExperimentConfig:
    # Paths
    h_m2_results_path: str = "../../h-m2/code/results/h_m2_results.json"
    h_m1_pairs_csv: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    bbq_csv: str = "../../h-e1/code/data/bbq_scores/bbq_per_model.csv"
    results_dir: str = "./results"
    figures_dir: str = "../../figures/h-m3"

    # Scenario boundaries (pre-specified, immutable)
    scenario_a_bound: float = 0.20
    scenario_b_bound: float = 0.40
    scenario_c_bound: float = -0.20

    # Ablation boundary variants
    tight_a: float = 0.15
    tight_b: float = 0.35
    tight_c: float = -0.15
    wide_a: float = 0.25
    wide_b: float = 0.45
    wide_c: float = -0.25

    # Tier 2
    n_min_harmbench: int = 20
    fuzzy_threshold: int = 75

    # Bootstrap (Tier 2 re-analysis only)
    n_boot: int = 5000
    seed: int = 42

    # Figures
    fig_dpi: int = 300
    fig_size: Tuple[float, float] = (9.0, 5.0)
    heatmap_cmap: str = "RdBu_r"
    heatmap_vmin: float = -1.0
    heatmap_vmax: float = 1.0
    heatmap_annot_fmt: str = ".2f"
    heatmap_fig_size: Tuple[float, float] = (6.0, 5.0)

    # Output schema
    output_filename: str = "h_m3_results.json"


def load_config() -> ExperimentConfig:
    return ExperimentConfig()
