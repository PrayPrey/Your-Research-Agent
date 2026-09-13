"""
config.py — ExperimentConfig dataclass + load_config()
H-M1: NLI distribution analysis (statistical analysis, no GPU)
"""
from dataclasses import dataclass, field
from typing import Tuple, Dict
import yaml


@dataclass
class ExperimentConfig:
    # Data paths
    h_e1_results_path: str = "../../h-e1/results/h-e1_results.json"
    halueval_hf_id: str = "pminervini/HaluEval"
    tasks: Tuple[str, ...] = ("dialogue", "qa", "summarization")
    hf_config_names: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "dialogue", "qa": "qa", "summarization": "summarization"
    })
    # HaluEval column names (same as h-e1)
    premise_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "knowledge", "qa": "knowledge", "summarization": "document"
    })
    hypothesis_right_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "right_response", "qa": "right_answer", "summarization": "right_summary"
    })
    hypothesis_hall_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "hallucinated_response", "qa": "hallucinated_answer",
        "summarization": "hallucinated_summary"
    })
    # Statistical thresholds
    kl_threshold: float = 0.05
    wilcoxon_alpha: float = 0.05
    near_uniform_threshold: float = 0.05
    near_uniform_warn_threshold: float = 0.50
    wilcoxon_tasks_required: int = 2
    seed: int = 42
    # Output
    results_dir: str = "../results"
    figures_dir: str = "../figures"
    results_filename: str = "h_m1_results.json"
    summary_filename: str = "h_m1_summary.json"
    # Figure settings
    fig_gate_figsize: Tuple[float, float] = (10.0, 8.0)
    fig_dpi: int = 150
    fig_bar_color_pass: str = "#2196F3"
    fig_bar_color_fail: str = "#F44336"
    fig_threshold_color: str = "#FF9800"
    fig_violin_figsize: Tuple[float, float] = (14.0, 10.0)
    fig_violin_color_hall: str = "#E91E63"
    fig_violin_color_corr: str = "#4CAF50"
    fig_uniform_ref_color: str = "#9E9E9E"
    fig_kl_summary_figsize: Tuple[float, float] = (12.0, 6.0)
    fig_box_figsize: Tuple[float, float] = (12.0, 6.0)
    fig_box_color_hall: str = "#FF9800"
    fig_box_color_corr: str = "#2196F3"
    fig_near_uniform_figsize: Tuple[float, float] = (8.0, 6.0)
    fig_near_uniform_target_color: str = "#F44336"


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    """Load YAML config into ExperimentConfig dataclass."""
    try:
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
    except FileNotFoundError:
        return ExperimentConfig()

    if raw is None:
        return ExperimentConfig()

    # Convert list → tuple for tasks and *_figsize fields
    if "tasks" in raw and isinstance(raw["tasks"], list):
        raw["tasks"] = tuple(raw["tasks"])

    for key in list(raw.keys()):
        if key.endswith("_figsize") and isinstance(raw[key], list):
            raw[key] = tuple(raw[key])

    # Only pass fields that exist in ExperimentConfig
    valid_fields = {f.name for f in ExperimentConfig.__dataclass_fields__.values()}
    filtered = {k: v for k, v in raw.items() if k in valid_fields}

    return ExperimentConfig(**filtered)
