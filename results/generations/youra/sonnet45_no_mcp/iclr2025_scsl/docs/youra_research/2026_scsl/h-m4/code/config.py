"""Configuration for H-M4 Geometry-Phenotype Coupling Experiment"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import yaml

@dataclass
class CheckpointConfig:
    """Checkpoint configuration"""
    path: str
    expected_alignment: float
    expected_wga: float

@dataclass
class PathSamplingConfig:
    """Path sampling configuration"""
    num_samples: int = 20
    methods: List[str] = field(default_factory=lambda: ["fge", "linear"])

@dataclass
class DatasetConfig:
    """Dataset configuration"""
    name: str = "waterbirds"
    version: str = "1.0"
    path: str = "/home/anonymous/data/waterbirds_v1.0"
    download_if_missing: bool = True
    num_groups: int = 4

@dataclass
class DataLoaderConfig:
    """DataLoader configuration"""
    batch_size: int = 128
    num_workers: int = 4
    shuffle_train: bool = False
    shuffle_val: bool = False
    shuffle_test: bool = False
    pin_memory: bool = True

@dataclass
class MetricsConfig:
    """Metrics computation configuration"""
    alignment_method: str = "h-m2"
    minority_groups: List[int] = field(default_factory=lambda: [1, 3])
    alignment_aggregation: str = "mean"
    wga_groups: List[int] = field(default_factory=lambda: [0, 1, 2, 3])
    wga_aggregation: str = "min"

@dataclass
class CorrelationConfig:
    """Correlation analysis configuration"""
    method: str = "spearman"
    alternative: str = "two-sided"
    significance_level: float = 0.01

@dataclass
class SuccessCriteriaConfig:
    """Success criteria for SHOULD_WORK gate"""
    primary_metric: str = "fge_rho"
    primary_threshold: float = -0.6
    primary_comparison: str = "less_than"
    p_value_threshold: float = 0.01
    secondary_metric: str = "linear_rho"
    secondary_threshold: float = -0.7
    partial_rho_range: List[float] = field(default_factory=lambda: [-0.6, -0.3])

@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    output_dir: str = "figures/"
    format: str = "png"
    dpi: int = 300

@dataclass
class OutputConfig:
    """Output configuration"""
    results_dir: str = "results/"
    validation_report: str = "04_validation.md"
    metrics_file: str = "results/metrics.json"
    checkpoint_file: str = "04_checkpoint.yaml"

@dataclass
class ComputeConfig:
    """Compute configuration"""
    device: str = "cuda"
    mixed_precision: bool = False

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: str = "logs/experiment.log"
    console: bool = True

@dataclass
class TrainingConfig:
    """Training configuration for ERM/DRO if checkpoints missing"""
    epochs: int = 5  # Lightweight training for PoC
    lr: float = 0.001
    weight_decay: float = 0.0001
    dro_alpha: float = 0.01  # Group-DRO step size

@dataclass
class ExperimentConfig:
    """Master experiment configuration"""
    version: str = "1.0"
    hypothesis_id: str = "h-m4"
    name: str = "geometry_phenotype_coupling"
    description: str = "Test functional coupling between A(w) and WGA"
    gate_type: str = "SHOULD_WORK"
    random_seed: int = 42

    # Sub-configurations
    path_sampling: PathSamplingConfig = field(default_factory=PathSamplingConfig)
    checkpoints: Dict[str, CheckpointConfig] = field(default_factory=dict)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    dataloader: DataLoaderConfig = field(default_factory=DataLoaderConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    correlation: CorrelationConfig = field(default_factory=CorrelationConfig)
    success_criteria: SuccessCriteriaConfig = field(default_factory=SuccessCriteriaConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    compute: ComputeConfig = field(default_factory=ComputeConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ExperimentConfig":
        """Load configuration from YAML file"""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)

        # Parse nested configurations
        path_sampling = PathSamplingConfig(**config_dict.get("path_sampling", {}))

        checkpoints = {}
        if "checkpoints" in config_dict:
            for key in ["erm", "dro"]:
                if key in config_dict["checkpoints"]:
                    checkpoints[key] = CheckpointConfig(**config_dict["checkpoints"][key])

        dataset = DatasetConfig(**config_dict.get("dataset", {}))
        dataloader = DataLoaderConfig(**config_dict.get("dataloader", {}))

        metrics_dict = config_dict.get("metrics", {})
        metrics = MetricsConfig(
            alignment_method=metrics_dict.get("alignment", {}).get("method", "h-m2"),
            minority_groups=metrics_dict.get("alignment", {}).get("minority_groups", [1, 3]),
            alignment_aggregation=metrics_dict.get("alignment", {}).get("aggregation", "mean"),
            wga_groups=metrics_dict.get("wga", {}).get("groups", [0, 1, 2, 3]),
            wga_aggregation=metrics_dict.get("wga", {}).get("aggregation", "min")
        )

        correlation = CorrelationConfig(**config_dict.get("correlation", {}))

        success_dict = config_dict.get("success_criteria", {})
        success_criteria = SuccessCriteriaConfig(
            primary_metric=success_dict.get("primary", {}).get("metric", "fge_rho"),
            primary_threshold=success_dict.get("primary", {}).get("threshold", -0.6),
            primary_comparison=success_dict.get("primary", {}).get("comparison", "less_than"),
            p_value_threshold=success_dict.get("primary", {}).get("p_value_threshold", 0.01),
            secondary_metric=success_dict.get("secondary", {}).get("metric", "linear_rho"),
            secondary_threshold=success_dict.get("secondary", {}).get("threshold", -0.7),
            partial_rho_range=success_dict.get("partial", {}).get("rho_range", [-0.6, -0.3])
        )

        visualization = VisualizationConfig(**config_dict.get("visualization", {}))
        output = OutputConfig(**config_dict.get("output", {}))
        compute = ComputeConfig(**config_dict.get("compute", {}))
        logging = LoggingConfig(**config_dict.get("logging", {}))
        training = TrainingConfig(**config_dict.get("training", {}))

        exp_dict = config_dict.get("experiment", {})
        return cls(
            version=config_dict.get("version", "1.0"),
            hypothesis_id=config_dict.get("hypothesis_id", "h-m4"),
            name=exp_dict.get("name", "geometry_phenotype_coupling"),
            description=exp_dict.get("description", "Test functional coupling"),
            gate_type=exp_dict.get("gate_type", "SHOULD_WORK"),
            random_seed=exp_dict.get("random_seed", 42),
            path_sampling=path_sampling,
            checkpoints=checkpoints,
            dataset=dataset,
            dataloader=dataloader,
            metrics=metrics,
            correlation=correlation,
            success_criteria=success_criteria,
            visualization=visualization,
            output=output,
            compute=compute,
            logging=logging,
            training=training
        )

    def validate(self) -> None:
        """Validate configuration parameters"""
        assert self.path_sampling.num_samples > 0, "num_samples must be positive"
        assert self.dataset.num_groups == 4, "Waterbirds has exactly 4 groups"
        assert self.dataloader.batch_size > 0, "batch_size must be positive"
        assert self.correlation.method in ["spearman", "pearson"], "Invalid correlation method"
        assert self.success_criteria.primary_threshold < 0, "Expected negative correlation"
        assert 0 < self.correlation.significance_level < 1, "Invalid significance level"
        assert self.compute.device in ["cuda", "cpu"], "Invalid device"
