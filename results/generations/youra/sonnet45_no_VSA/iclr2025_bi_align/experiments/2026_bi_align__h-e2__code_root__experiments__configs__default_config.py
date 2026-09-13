from dataclasses import dataclass, field
from typing import Literal

@dataclass
class ErrorThresholds:
    cnn_median: float = 0.10
    transformer_median: float = 0.15
    p95_all: float = 0.25

@dataclass
class StatisticalTest:
    method: str = "wilcoxon"
    alpha: float = 0.05
    alternative: str = "less"
    zero_method: str = "wilcox"

@dataclass
class EvaluationConfig:
    error_thresholds: ErrorThresholds = field(default_factory=ErrorThresholds)
    statistical_test: StatisticalTest = field(default_factory=StatisticalTest)
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    export_csv: bool = True
    generate_plots: bool = True

@dataclass
class ModelRegistry:
    cnn_models: list[str] = field(default_factory=lambda: [
        "resnet18", "resnet34", "resnet50", "vgg16",
        "densenet121", "mobilenet_v2", "efficientnet_b0", "shufflenet_v2_x1_0"
    ])
    transformer_models: list[str] = field(default_factory=lambda: [
        "bert-base-uncased", "roberta-base", "gpt2", "t5-small",
        "distilbert-base-uncased", "albert-base-v2",
        "microsoft/deberta-base", "google/vit-base-patch16-224"
    ])
    default_num_classes: int = 10

@dataclass
class AblationConfig:
    baseline_iters: int = 2
    proposed_iters: int = 3
    use_stratified: bool = True

@dataclass
class WilcoxonParams:
    alternative: str = "less"
    zero_method: str = "wilcox"
    correction: bool = False
    mode: str = "auto"

@dataclass
class StatisticalValidationConfig:
    ablation: AblationConfig = field(default_factory=AblationConfig)
    wilcoxon: WilcoxonParams = field(default_factory=WilcoxonParams)
    significance_level: float = 0.05
    export_ablation_results: bool = True
    ablation_csv: str = "ablation_2iter_results.csv"

@dataclass
class DatasetConfig:
    root: str = "./data"
    batch_size: int = 128
    max_length: int = 128
    imagenet_batch_size: int = 64
    wmt14_batch_size: int = 32

@dataclass
class StratifiedSamplingConfig:
    quantiles: list[float] = field(default_factory=lambda: [0.5, 0.75, 0.95, 0.99])
    min_samples_per_bin: int = 100
    enabled: bool = True

@dataclass
class OptimizerConfig:
    name: Literal["adam", "adamw", "sgd"]
    adam_lr: float = 0.0001
    adam_betas: tuple[float, float] = (0.9, 0.999)
    adamw_weight_decay: float = 0.01
    sgd_lr: float = 0.1
    sgd_momentum: float = 0.9

@dataclass
class ProfilingConfig:
    device: str = "cuda:0"
    num_ground_truth_iters: int = 10
    num_lightweight_iters: int = 3
    reset_between_experiments: bool = True
    track_segment_level: bool = True

@dataclass
class ExperimentConfig:
    seed: int = 42
    device: str = "cuda:0"
    
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    stratified_sampling: StratifiedSamplingConfig = field(default_factory=StratifiedSamplingConfig)
    optimizer: OptimizerConfig = None
    profiling: ProfilingConfig = field(default_factory=ProfilingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    statistical: StatisticalValidationConfig = field(default_factory=StatisticalValidationConfig)
    
    verbose: bool = True
    log_level: str = "INFO"

def create_optimizer_config(name: Literal["adam", "adamw", "sgd"]) -> OptimizerConfig:
    return OptimizerConfig(name=name)

def set_global_seed(seed: int):
    import random
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
