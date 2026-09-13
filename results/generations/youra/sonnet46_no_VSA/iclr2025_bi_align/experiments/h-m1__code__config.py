from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class AnalysisConfig:
    # Data
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    required_cols: Tuple[str, ...] = (
        "model_name", "TruthfulQA_MC2", "bbq_accuracy", "MMLU"
    )

    # Gate
    r2_threshold: float = 0.05
    n_min: int = 30

    # Output
    figures_dir: str = "../figures"
    results_dir: str = "./results"
    seed: int = 42

    # Figure sizes
    fig_bar_size: Tuple[float, float] = (7.0, 5.0)
    fig_scatter_size: Tuple[float, float] = (6.0, 5.0)
    fig_heatmap_size: Tuple[float, float] = (5.0, 4.5)
    fig_dpi: int = 150

    # Colors
    color_pass: str = "#2ca02c"
    color_fail: str = "#d62728"
    color_scatter: str = "#1f77b4"
    color_threshold: str = "#ff7f0e"


def load_config(yaml_path: str = None) -> AnalysisConfig:
    if yaml_path is None:
        return AnalysisConfig()
    import yaml
    with open(yaml_path) as f:
        raw = yaml.safe_load(f)
    d = raw.get("data", {})
    g = raw.get("gate", {})
    o = raw.get("output", {})
    fig = raw.get("figures", {})
    return AnalysisConfig(
        data_path=d.get("data_path", AnalysisConfig.data_path),
        r2_threshold=g.get("r2_threshold", AnalysisConfig.r2_threshold),
        n_min=g.get("n_min", AnalysisConfig.n_min),
        figures_dir=o.get("figures_dir", AnalysisConfig.figures_dir),
        results_dir=o.get("results_dir", AnalysisConfig.results_dir),
        seed=raw.get("seed", AnalysisConfig.seed),
        fig_dpi=fig.get("dpi", AnalysisConfig.fig_dpi),
    )
