from dataclasses import dataclass


@dataclass
class CoxConfig:
    panel_path: str = "docs/youra_research/h-e1/h_e2_panel_with_diversity.csv"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    results_path: str = "docs/youra_research/h-m1/experiment_results.json"

    duration_col: str = "duration"
    event_col: str = "event"
    base_covariates: tuple = ("task_age", "log_publication_volume", "benchmark_introduction_year")
    diversity_col: str = "log_unique_paper_count_at_intro_z"
    km_col: str = "log_unique_paper_count_at_intro"

    penalizer: float = 0.1
    penalizer_fallback: float = 0.5
    lrt_df: int = 1
    p_threshold: float = 0.05
    hr_effect_threshold: float = 0.10


@dataclass
class FigureConfig:
    dpi: int = 150
    color_pass: str = "#2ecc71"
    color_fail: str = "#e74c3c"
    color_neutral: str = "#3498db"


CFG = CoxConfig()
FIG_CFG = FigureConfig()
