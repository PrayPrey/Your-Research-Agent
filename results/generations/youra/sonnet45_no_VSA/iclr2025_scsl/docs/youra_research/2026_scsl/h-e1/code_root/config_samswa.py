"""
Configuration for H-E1 SAM+SWA Joint Training
Based on PRD/Architecture/Logic/Config documents from Phase 3
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple, List, Optional


@dataclass
class ColoredMNISTConfig:
    """ColoredMNIST spurious correlation benchmark"""
    data_root: str = "data/colored_mnist"
    resolution: int = 14
    num_channels: int = 3

    binary_split: Tuple[int, int] = (5, 5)
    train_correlation: float = 0.90
    test_correlation: float = 0.10

    train_size: int = 50000
    val_size: int = 10000
    test_size: int = 10000
    num_groups: int = 4

    batch_size: int = 128
    num_workers: int = 4
    pin_memory: bool = True


@dataclass
class CelebAConfig:
    """CelebA via WILDS benchmark"""
    data_root: str = "data/celeba"
    wilds_version: str = "2.0.0"
    task: str = "blond_hair"
    spurious_attribute: str = "male"

    input_size: int = 224
    resize_size: int = 256
    crop_size: int = 224

    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225)

    horizontal_flip: bool = True
    random_crop: bool = True
    color_jitter: bool = False
    num_groups: int = 4

    batch_size: int = 64
    num_workers: int = 4
    pin_memory: bool = True


@dataclass
class ERMConfig:
    """ERM baseline configuration"""
    optimizer: str = "sgd"
    lr: float = 0.001
    lr_celeba: float = 0.0001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    epochs: int = 100
    epochs_celeba: int = 50
    criterion: str = "binary_crossentropy"


@dataclass
class SAMConfig:
    """SAM-only configuration"""
    rho: float = 0.05
    adaptive: bool = False

    base_optimizer: str = "sgd"
    lr: float = 0.001
    lr_celeba: float = 0.0001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    epochs: int = 100
    epochs_celeba: int = 50
    disable_bn_second_pass: bool = True


@dataclass
class SWAConfig:
    """SWA-only configuration"""
    swa_start: float = 0.75
    swa_lr: float = 0.05

    base_optimizer: str = "sgd"
    lr: float = 0.001
    lr_celeba: float = 0.0001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    epochs: int = 100
    epochs_celeba: int = 50
    update_bn_after_training: bool = True


@dataclass
class JointSAMSWAConfig:
    """Joint SAM+SWA configuration (PROPOSED)"""
    rho: float = 0.05
    adaptive: bool = False
    disable_bn_second_pass: bool = True

    swa_start: float = 0.75
    swa_lr: float = 0.05
    update_bn_after_training: bool = True

    base_optimizer: str = "sgd"
    lr: float = 0.001
    lr_celeba: float = 0.0001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    epochs: int = 100
    epochs_celeba: int = 50


@dataclass
class SequentialConfig:
    """Sequential SAM→SWA configuration (Control)"""
    sam_epochs: int = 75
    sam_epochs_celeba: int = 38
    sam_rho: float = 0.05

    swa_epochs: int = 25
    swa_epochs_celeba: int = 12
    swa_lr: float = 0.05

    base_optimizer: str = "sgd"
    lr: float = 0.001
    lr_celeba: float = 0.0001
    momentum: float = 0.9
    weight_decay: float = 0.0001

    disable_bn_second_pass: bool = True
    update_bn_after_training: bool = True


@dataclass
class TrainingConfig:
    """Shared training configuration"""
    model_architecture: str = "resnet18"
    pretrained: bool = True
    num_classes: int = 2

    gradient_clip_norm: float = 1.0
    gradient_clip_enabled: bool = True
    detect_nan_gradients: bool = True

    validate_every: int = 5
    validate_every_celeba: int = 2

    save_best_only: bool = True
    selection_metric: str = "worst_group_val_accuracy"

    seed: int = 42
    deterministic: bool = True
    device: str = "cuda"
    mixed_precision: bool = False


@dataclass
class ExperimentOrchestrationConfig:
    """50-run experiment orchestration"""
    methods: List[str] = field(default_factory=lambda: [
        "ERM", "SAM", "SWA", "Joint", "Sequential"
    ])
    datasets: List[str] = field(default_factory=lambda: [
        "ColoredMNIST", "CelebA"
    ])
    seeds: List[int] = field(default_factory=lambda: [
        42, 123, 456, 789, 2024
    ])

    log_dir: str = "outputs/h-e1"
    use_tensorboard: bool = False
    use_wandb: bool = False
    log_interval: int = 10

    checkpoint_dir: str = "outputs/h-e1/checkpoints"
    checkpoint_every: int = 10
    save_best_checkpoint: bool = True

    statistical_test: str = "paired_t_test"
    alpha: float = 0.0125
    bootstrap_samples: int = 1000
    confidence_level: float = 0.95

    results_file: str = "outputs/h-e1/results.csv"
    analysis_file: str = "outputs/h-e1/statistical_analysis.json"
    report_file: str = "outputs/h-e1/validation_report.md"

    max_gpu_hours: float = 35.0
    early_stop_if_over_budget: bool = True


@dataclass
class H_E1_MasterConfig:
    """Master configuration for H-E1 SAM+SWA Joint Training"""
    experiment_name: str = "h-e1-sam-swa-joint"
    hypothesis_type: str = "EXISTENCE"
    method: str = "Joint"
    dataset: str = "ColoredMNIST"
    seed: int = 42

    data: Optional[object] = None
    training: Optional[object] = None
    orchestration: ExperimentOrchestrationConfig = field(
        default_factory=ExperimentOrchestrationConfig
    )

    project_root: Path = Path("/workspace/TEST_scsl")

    def __post_init__(self):
        if self.dataset == "ColoredMNIST":
            self.data = ColoredMNISTConfig()
        elif self.dataset == "CelebA":
            self.data = CelebAConfig()
        else:
            raise ValueError(f"Unknown dataset: {self.dataset}")

        if self.method == "ERM":
            self.training = ERMConfig()
        elif self.method == "SAM":
            self.training = SAMConfig()
        elif self.method == "SWA":
            self.training = SWAConfig()
        elif self.method == "Joint":
            self.training = JointSAMSWAConfig()
        elif self.method == "Sequential":
            self.training = SequentialConfig()
        else:
            raise ValueError(f"Unknown method: {self.method}")


def get_config(method: str, dataset: str, seed: int = 42) -> H_E1_MasterConfig:
    """
    Factory function to create experiment config.

    Args:
        method: Training method (ERM, SAM, SWA, Joint, Sequential)
        dataset: Dataset name (ColoredMNIST, CelebA)
        seed: Random seed

    Returns:
        H_E1_MasterConfig with method/dataset-specific configs
    """
    return H_E1_MasterConfig(method=method, dataset=dataset, seed=seed)
