"""Configuration for H-M2 scale-ensemble experiment."""
from dataclasses import dataclass


import os

_BASE = os.path.dirname(os.path.abspath(__file__))
_HE1 = os.path.join(_BASE, "..", "..", "h-e1", "code", "outputs")


@dataclass
class EnsembleConfig:
    judges: tuple = ("7B", "70B", "proprietary")
    he1_results_path: str = os.path.join(_HE1, "results.csv")
    he1_contingency_path: str = os.path.join(_HE1, "contingency.csv")
    he1_metrics_path: str = os.path.join(_HE1, "metrics.csv")
    n_expected_problems: int = 164  # HumanEval problems

    # Statistical thresholds
    p_value_threshold: float = 0.05
    improvement_target: float = 0.03  # 3% accuracy improvement

    # Ablation
    ab3_exclude_judge: str = "7B"

    # Reproducibility
    seed: int = 42

    # Output
    comparison_csv_path: str = "outputs/comparison.csv"
    mcnemar_json_path: str = "outputs/mcnemar_results.json"
    figures_dir: str = "outputs/figures/"


CFG = EnsembleConfig()
