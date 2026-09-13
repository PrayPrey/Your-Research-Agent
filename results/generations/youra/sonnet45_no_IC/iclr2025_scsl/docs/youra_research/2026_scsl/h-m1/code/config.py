"""Configuration for H-E1 Repository Maintenance Classification Experiment."""

from dataclasses import dataclass, field
from typing import Tuple
import os


@dataclass
class ModelConfig:
    """Logistic Regression training configuration."""

    test_size: float = 0.20
    random_state: int = 42
    stratify: bool = True
    max_iter: int = 1000
    solver: str = 'lbfgs'
    class_weight: str = 'balanced'
    normalize_features: bool = True
    model_save_path: str = 'models/lr_classifier.pkl'
    scaler_save_path: str = 'models/feature_scaler.pkl'


@dataclass
class EvaluationConfig:
    """Evaluation metrics and gate thresholds."""

    accuracy_threshold: float = 0.75
    f1_threshold: float = 0.73
    compute_metrics: Tuple[str, ...] = ('accuracy', 'precision', 'recall', 'f1', 'roc_auc')
    output_dict: bool = True
    zero_division: int = 0
    report_path: str = 'outputs/metrics.json'


@dataclass
class ExperimentConfig:
    """End-to-end experiment pipeline configuration."""

    github_api_token: str = field(default_factory=lambda: os.environ.get('GITHUB_TOKEN', ''))
    dataset_size: int = 120  # Real GitHub API data collection from Papers with Code benchmarks (120 repos for unauthenticated API, target was 2000)
    year_range: Tuple[int, int] = (2020, 2024)
    min_stars: int = 32
    data_output_path: str = 'data/raw_metadata.csv'
    label_threshold_days: int = 180
    figures_output_path: str = 'figures/'
    figure_dpi: int = 300
    figure_format: str = 'png'
    model_config: ModelConfig = field(default_factory=ModelConfig)
    eval_config: EvaluationConfig = field(default_factory=EvaluationConfig)

    def __post_init__(self):
        if not self.model_config:
            self.model_config = ModelConfig()
        if not self.eval_config:
            self.eval_config = EvaluationConfig()
