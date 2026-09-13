from dataclasses import dataclass
from typing import Tuple


@dataclass
class ExperimentConfig:
    # Data
    data_path: str = "../../h-e1/code/data/llm_leaderboard_v1/llm.csv"
    bbq_path: str = "../../h-e1/code/data/bbq_scores/bbq_per_model.csv"
    required_cols: Tuple[str, ...] = (
        "model_name", "TruthfulQA_MC2", "BBQ_accuracy", "MMLU"
    )
    n_min: int = 30

    # Bootstrap
    n_boot: int = 5000
    seed: int = 42
    min_family_size: int = 3

    # Output
    figures_dir: str = "../../figures"
    results_dir: str = "./results"

    # Visualization
    fig_size: Tuple[float, float] = (8.0, 5.0)
    fig_dpi: int = 150
    color_significant: str = "#2ca02c"
    color_null: str = "#ff7f0e"


def load_config(yaml_path: str = None) -> ExperimentConfig:
    """Return ExperimentConfig from defaults, optionally overridden by YAML."""
    if yaml_path is None:
        return ExperimentConfig()
    import yaml
    with open(yaml_path) as f:
        raw = yaml.safe_load(f) or {}
    d = raw.get("data", {})
    b = raw.get("bootstrap", {})
    o = raw.get("output", {})
    fig = raw.get("figures", {})
    fig_size_raw = fig.get("fig_size", list(ExperimentConfig.fig_size))
    return ExperimentConfig(
        data_path=d.get("data_path", ExperimentConfig.data_path),
        required_cols=tuple(d.get("required_cols", list(ExperimentConfig.required_cols))),
        n_min=d.get("n_min", ExperimentConfig.n_min),
        n_boot=b.get("n_boot", ExperimentConfig.n_boot),
        seed=b.get("seed", ExperimentConfig.seed),
        min_family_size=b.get("min_family_size", ExperimentConfig.min_family_size),
        figures_dir=o.get("figures_dir", ExperimentConfig.figures_dir),
        results_dir=o.get("results_dir", ExperimentConfig.results_dir),
        fig_size=tuple(fig_size_raw),
        fig_dpi=fig.get("fig_dpi", ExperimentConfig.fig_dpi),
        color_significant=fig.get("color_significant", ExperimentConfig.color_significant),
        color_null=fig.get("color_null", ExperimentConfig.color_null),
    )
