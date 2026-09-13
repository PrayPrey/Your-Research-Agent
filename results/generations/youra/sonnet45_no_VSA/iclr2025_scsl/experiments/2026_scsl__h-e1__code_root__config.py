"""
Master configuration for H-E1 Joint SAM+DRO Experiment
Usage:
    from config import get_config
    config = get_config(condition="joint_sam_dro", seed=42)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple, List


@dataclass
class DataConfig:
    """Data pipeline configuration"""
    # Dataset
    dataset_name: str = "waterbirds"
    data_root: str = "data/waterbirds"

    # Splits
    train_split: str = "train"
    val_split: str = "val"
    test_split: str = "test"

    # Data loading
    batch_size: int = 32
    num_workers: int = 4
    pin_memory: bool = True

    # Augmentation (ImageNet standard)
    crop_size: int = 224
    resize_size: int = 256
    horizontal_flip_prob: float = 0.5
    color_jitter: bool = True

    # Normalization (ImageNet stats)
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225)


@dataclass
class ModelConfig:
    """Model architecture configuration"""
    # Architecture
    architecture: str = "resnet50"
    pretrained: bool = True
    num_classes: int = 2

    # Environment classifier (PG-DRO only)
    env_classifier_arch: str = "resnet18"
    env_num_groups: int = 4
    env_pretrain_epochs: int = 10
    env_labeled_samples: int = 100
    env_min_accuracy: float = 0.8  # Validation threshold


@dataclass
class PGDROConfig:
    """PG-DRO optimizer configuration"""
    # Hyperparameter (grid search)
    C: float = 0.5  # {0.1, 0.5, 1.0, 2.0}

    # Group reweighting
    initial_group_weights: str = "uniform"  # [1/4, 1/4, 1/4, 1/4]
    normalize_weights: bool = True

    # Base optimizer
    base_lr: float = 1e-4
    momentum: float = 0.9
    weight_decay: float = 1e-4

    # Training
    total_epochs: int = 200
    validate_every: int = 5
    early_stopping_patience: int = 20


@dataclass
class SAMConfig:
    """SAM optimizer configuration"""
    # Hyperparameter (grid search)
    rho: float = 0.05  # {0.01, 0.05, 0.1, 0.2}

    # Perturbation computation
    adaptive: bool = False  # Use fixed ρ (not adaptive SAM)

    # Base optimizer
    base_lr: float = 1e-4
    momentum: float = 0.9
    weight_decay: float = 1e-4

    # Training (match PG-DRO compute budget)
    total_epochs: int = 100  # 2x forward → half epochs
    validate_every: int = 5
    early_stopping_patience: int = 20


@dataclass
class SequentialConfig:
    """Sequential PG-DRO → SAM optimizer configuration"""
    # Stage 1: PG-DRO (inherit best C)
    stage1_epochs: int = 200
    stage1_C: float = 0.5  # From PG-DRO grid search result

    # Stage 2: SAM (inherit best ρ)
    stage2_epochs: int = 100
    stage2_rho: float = 0.05  # From SAM grid search result

    # Shared
    base_lr: float = 1e-4
    momentum: float = 0.9
    weight_decay: float = 1e-4
    validate_every: int = 5
    early_stopping_patience: int = 20

    # Environment classifier
    freeze_env_classifier_stage2: bool = True  # Use stage 1 Q̂(x)


@dataclass
class JointSAMDROConfig:
    """Joint SAM+DRO optimizer configuration"""
    # Hyperparameters (4D search space)
    rho: float = 0.05          # SAM perturbation: {0.01, 0.05, 0.1}
    C: float = 0.5             # DRO reweighting: {0.1, 0.5, 1.0}
    lambda1: float = 1.0       # Worst-group sharpness: {0.5, 1.0, 2.0}
    lambda2: float = 0.5       # Variance penalty: {0.1, 0.5, 1.0}

    # Group perturbation
    num_groups: int = 4
    per_group_perturbation: bool = True
    normalize_group_gradients: bool = True

    # Sharpness computation
    compute_sharpness_every_step: bool = True

    # Base optimizer
    base_lr: float = 1e-4
    momentum: float = 0.9
    weight_decay: float = 1e-4

    # Training (match compute budget: 50 epochs × 5 forward ≈ 250 forward passes)
    total_epochs: int = 50
    validate_every: int = 5
    early_stopping_patience: int = 20

    # Group reweighting (DRO component)
    initial_group_weights: str = "uniform"
    normalize_weights: bool = True


@dataclass
class TrainingConfig:
    """Training orchestration configuration"""
    # LR schedule
    lr_schedule: str = "cosine"
    lr_warmup_epochs: int = 0
    lr_min: float = 0.0

    # Model selection
    selection_metric: str = "worst_group_val_accuracy"
    selection_mode: str = "max"

    # Early stopping
    early_stopping_patience: int = 20
    early_stopping_min_delta: float = 0.0

    # Checkpointing
    checkpoint_every: int = 10
    save_best_only: bool = False  # Save both best + periodic

    # Reproducibility
    seed: int = 42
    deterministic: bool = True
    benchmark: bool = False

    # Gradient management
    gradient_clip_norm: float = 1.0
    gradient_clip_enabled: bool = True
    detect_nan_gradients: bool = True

    # Compute
    device: str = "cuda"
    mixed_precision: bool = False  # Not needed for ResNet-50


@dataclass
class EvaluationConfig:
    """Evaluation and logging configuration"""
    # Metrics computation
    compute_per_group_accuracy: bool = True
    compute_worst_group_accuracy: bool = True
    compute_average_accuracy: bool = True
    compute_group_variance: bool = True

    # Statistical testing
    statistical_test: str = "paired_t_test"
    alpha: float = 0.05
    min_effect_size: float = 0.5  # Cohen's d

    # Logging backends
    use_wandb: bool = False  # Disabled for unattended mode
    use_tensorboard: bool = False
    use_file_logging: bool = True

    # WandB
    wandb_project: str = "h-e1-joint-sam-dro"
    wandb_entity: Optional[str] = None  # Use default

    # File paths
    log_file: str = "experiment.log"
    metrics_file: str = "metrics.json"
    results_file: str = "results.csv"

    # Validation artifacts
    save_gradient_analysis: bool = True  # cos(∇L_worst, ∇L_avg)
    save_compute_profile: bool = True    # FLOPs, wall-clock time
    save_env_classifier_quality: bool = True  # Q̂(x) accuracy


@dataclass
class LoggingConfig:
    """Detailed logging configuration"""
    # What to log per epoch
    log_train_loss: bool = True
    log_per_group_train_loss: bool = True
    log_val_accuracy: bool = True
    log_per_group_val_accuracy: bool = True
    log_worst_group_val_accuracy: bool = True
    log_group_weights: bool = True  # For DRO methods
    log_sharpness: bool = True      # For SAM/Joint
    log_lr: bool = True
    log_grad_norm: bool = True

    # Logging frequency
    log_every_n_steps: int = 10
    log_epoch_summary: bool = True

    # Console output
    verbose: bool = True
    progress_bar: bool = True


@dataclass
class ExperimentConfig:
    """Master configuration container"""

    # Experiment metadata
    experiment_name: str = "h-e1-joint-sam-dro"
    condition: str = "joint_sam_dro"  # {pg_dro, sam, sequential, joint_sam_dro}
    seed: int = 42

    # Component configs
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Condition-specific optimizer config (set dynamically)
    optimizer: Optional[object] = None

    # Paths (absolute)
    project_root: Path = Path("/workspace/TEST_scsl")
    data_root: Path = field(init=False)
    output_root: Path = field(init=False)
    checkpoint_dir: Path = field(init=False)
    results_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)

    def __post_init__(self):
        # Resolve paths
        self.data_root = self.project_root / "data"
        self.output_root = self.project_root / f"outputs/{self.condition}/seed{self.seed}"
        self.checkpoint_dir = self.output_root / "checkpoints"
        self.results_dir = self.output_root / "results"
        self.logs_dir = self.output_root / "logs"

        # Create directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Set condition-specific optimizer config
        if self.condition == "pg_dro":
            self.optimizer = PGDROConfig()
        elif self.condition == "sam":
            self.optimizer = SAMConfig()
        elif self.condition == "sequential":
            self.optimizer = SequentialConfig()
        elif self.condition == "joint_sam_dro":
            self.optimizer = JointSAMDROConfig()
        else:
            raise ValueError(f"Unknown condition: {self.condition}")


def get_config(condition: str, seed: int = 42, **overrides) -> ExperimentConfig:
    """
    Factory function to create experiment config.

    Args:
        condition: Optimizer condition (pg_dro, sam, sequential, joint_sam_dro)
        seed: Random seed
        **overrides: Override any config field (e.g., data__batch_size=64)

    Returns:
        ExperimentConfig with condition-specific optimizer
    """
    config = ExperimentConfig(condition=condition, seed=seed)

    # Apply overrides (nested fields with __)
    for key, value in overrides.items():
        parts = key.split("__")
        obj = config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)

    return config
