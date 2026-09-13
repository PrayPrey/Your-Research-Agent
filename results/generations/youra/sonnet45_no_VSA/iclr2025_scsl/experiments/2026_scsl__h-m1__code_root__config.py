"""Configuration for h-m1 dose-response experiment"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class DataConfig:
    """Data pipeline configuration"""
    dataset_name: str = "mnist"
    data_root: str = "data/mnist"
    batch_size: int = 64
    num_workers: int = 4
    pin_memory: bool = True

    # Dose-response experimental conditions
    flip_probabilities: List[float] = field(default_factory=lambda: [0.0, 0.3, 0.5, 0.9])

    # MNIST normalization (standard)
    mean: Tuple[float, ...] = (0.1307,)
    std: Tuple[float, ...] = (0.3081,)


@dataclass
class ModelConfig:
    """Model architecture configuration"""
    architecture: str = "standard_cnn"
    in_channels: int = 1
    num_classes: int = 10

    # Regularization (PyTorch MNIST official example)
    dropout_conv: float = 0.25
    dropout_fc: float = 0.5


@dataclass
class TrainingConfig:
    """Training protocol configuration"""
    # Optimizer
    optimizer: str = "adam"
    lr: float = 0.001
    weight_decay: float = 0.0

    # Schedule (PyTorch official example)
    lr_schedule: str = "step"
    scheduler_step: int = 1
    scheduler_gamma: float = 0.7

    # Training duration
    max_epochs: int = 30
    patience: int = 5

    # Gradient management
    gradient_clip_norm: float = 1.0
    gradient_clip_enabled: bool = True
    detect_nan_gradients: bool = True

    # Multi-seed execution
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])

    # Compute
    device: str = "cuda"
    mixed_precision: bool = False


@dataclass
class EvaluationConfig:
    """Evaluation metrics configuration"""
    # Primary metric (hypothesis-specific)
    asymmetric_digits: List[int] = field(default_factory=lambda: [2, 3, 5, 6, 7, 9])
    symmetric_digits: List[int] = field(default_factory=lambda: [0, 1, 8])

    # Statistical test
    correlation_method: str = "spearman"
    alpha: float = 0.05

    # Gate criteria
    gate_type: str = "MUST_WORK"
    gate_rho_threshold: float = 0.0  # Must be < 0 (negative correlation)
    gate_p_threshold: float = 0.05


@dataclass
class VisualizationConfig:
    """Visualization configuration for dose-response analysis"""

    # Figure settings
    figure_dpi: int = 300
    figure_format: str = "png"
    figure_size_single: Tuple[float, float] = (8.0, 6.0)
    figure_size_wide: Tuple[float, float] = (12.0, 5.0)

    # Style
    style: str = "seaborn-v0_8-darkgrid"
    font_size: int = 12
    title_size: int = 14
    label_size: int = 12

    # Colors
    line_color: str = "#2E86AB"
    error_color: str = "#A23B72"
    bar_colors: Tuple[str, str, str] = ("#3A86FF", "#8338EC", "#FF006E")
    heatmap_cmap: str = "coolwarm"

    # Markers and lines
    marker_style: str = "o"
    marker_size: int = 8
    line_width: float = 2.0
    error_capsize: float = 5.0

    # Gate metrics visualization
    gate_pass_color: str = "#06D6A0"
    gate_fail_color: str = "#EF476F"

    # Heatmap settings
    heatmap_annot: bool = True
    heatmap_fmt: str = ".2f"
    heatmap_cbar_label: str = "Accuracy"

    # Output paths (relative to experiment root)
    output_subdir: str = "figures"
    dose_response_filename: str = "dose_response_curve.png"
    heatmap_filename: str = "per_digit_heatmap.png"
    degradation_filename: str = "degradation_bars.png"
    gate_metrics_filename: str = "gate_metrics.png"


@dataclass
class LoggingConfig:
    """Logging configuration"""
    # Logging frequency
    log_every_n_steps: int = 10
    log_epoch_summary: bool = True

    # Console output
    verbose: bool = True
    progress_bar: bool = True

    # File logging
    use_file_logging: bool = True
    log_file: str = "experiment.log"
    metrics_file: str = "metrics.json"
    results_file: str = "results.csv"


@dataclass
class ExperimentConfig:
    """Master configuration container"""

    # Experiment metadata
    experiment_name: str = "h-m1-dose-response"
    hypothesis_id: str = "h-m1"
    seed: int = 42

    # Component configs
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Paths (absolute)
    project_root: Path = Path("/workspace/TEST_scsl")
    output_root: Path = field(init=False)
    checkpoint_dir: Path = field(init=False)
    results_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    figures_dir: Path = field(init=False)

    def __post_init__(self):
        # Resolve paths
        self.output_root = self.project_root / f"experiments/{self.hypothesis_id}/results"
        self.checkpoint_dir = self.output_root / "checkpoints"
        self.results_dir = self.output_root / "results"
        self.logs_dir = self.output_root / "logs"
        self.figures_dir = self.output_root / "figures"

        # Create directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)


def get_config(seed: int = 42, **overrides) -> ExperimentConfig:
    """
    Factory function to create experiment config.

    Args:
        seed: Random seed
        **overrides: Override any config field (e.g., data__batch_size=64)

    Returns:
        ExperimentConfig with all defaults
    """
    config = ExperimentConfig(seed=seed)

    # Apply overrides (nested fields with __)
    for key, value in overrides.items():
        parts = key.split("__")
        obj = config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    return config
