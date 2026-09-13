"""H-M4: Configuration constants and model metadata."""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

CODE_DIR = Path(__file__).parent
H_M3_RESULTS_DIR = CODE_DIR.parent.parent / "h-m3" / "results"
EXP_B_CSV = H_M3_RESULTS_DIR / "experiment_b_per_model_task_rates.csv"
CONTRACT_EVAL_JSON = CODE_DIR.parent.parent.parent / "data" / "ContractEval" / "data" / "contract_eval_tasks.json"
RESULTS_DIR = CODE_DIR.parent / "results"
FIGURES_DIR = CODE_DIR.parent / "figures"

# Gate thresholds
TAU_THRESHOLD = 0.6
DELTA_R2_THRESHOLD = 0.10
GAP_THRESHOLD = 0.10
ALPHA = 0.05

# Bootstrap
N_BOOTSTRAP = 1000
SEED = 42

MODEL_SIZES = {
    "gpt-4o-mini":            8.0,
    "deepseek-coder-v2-lite": 16.0,
    "claude-3-haiku":         20.0,
    "codellama-34b":          34.0,
    "codellama-13b":          13.0,
}

MODEL_FAMILIES = {
    "gpt-4o-mini":            "openai",
    "deepseek-coder-v2-lite": "deepseek",
    "claude-3-haiku":         "anthropic",
    "codellama-34b":          "meta",
    "codellama-13b":          "meta",
}

PASS_AT_1_FALLBACK = {
    "gpt-4o-mini":            {"humaneval_plus": 0.835, "mbpp_plus": 0.722},
    "deepseek-coder-v2-lite": {"humaneval_plus": 0.823, "mbpp_plus": 0.751},
    "claude-3-haiku":         {"humaneval_plus": 0.730, "mbpp_plus": 0.660},
    "codellama-34b":          {"humaneval_plus": 0.650, "mbpp_plus": 0.600},
    "codellama-13b":          {"humaneval_plus": 0.580, "mbpp_plus": 0.530},
}


@dataclass
class FigureConfig:
    dpi: int = 300
    output_dir: Path = FIGURES_DIR
    scatter_figsize: tuple = (7, 7)
    bar_figsize: tuple = (8, 5)
    histogram_figsize: tuple = (7, 4)
    heatmap_figsize: tuple = (8, 6)
    model_colors: Optional[dict] = None
    threshold_color: str = "red"
    threshold_linestyle: str = "--"
    threshold_linewidth: float = 1.5

    def __post_init__(self):
        if self.model_colors is None:
            self.model_colors = {
                "gpt-4o-mini":            "#4C72B0",
                "deepseek-coder-v2-lite": "#DD8452",
                "claude-3-haiku":         "#55A868",
                "codellama-34b":          "#C44E52",
                "codellama-13b":          "#8172B2",
            }


@dataclass
class PlotConfig:
    scatter_label_offset: float = 0.01
    scatter_alpha: float = 0.8
    scatter_point_size: int = 80
    bar_order: Optional[List[str]] = None
    perm_hist_bins: int = 50
    perm_observed_color: str = "red"
    perm_null_color: str = "steelblue"
    perm_null_alpha: float = 0.7


@dataclass
class PathConfig:
    exp_b_csv: Path = EXP_B_CSV
    contract_eval_json: Path = CONTRACT_EVAL_JSON
    results_dir: Path = RESULTS_DIR
    figures_dir: Path = FIGURES_DIR
    evalplus_source: str = "fallback"


@dataclass
class ValidationConfig:
    min_models: int = 3  # lowered from 5 to allow partial-model runs
    min_tasks_per_model: int = 100
    max_nan_rate: float = 0.10


@dataclass
class SubgroupConfig:
    task_types: Optional[List[str]] = None
    divergence_threshold: float = 0.2
    min_tasks_per_subgroup: int = 50

    def __post_init__(self):
        if self.task_types is None:
            self.task_types = ["humaneval_plus", "mbpp_plus"]
