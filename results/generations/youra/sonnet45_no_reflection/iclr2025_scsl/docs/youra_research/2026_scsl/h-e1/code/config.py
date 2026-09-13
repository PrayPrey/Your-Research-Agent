"""Configuration for h-e1 SCSL experiment."""
from dataclasses import dataclass, field


@dataclass
class DataConfig:
    dataset_name: str = "allenai/c4"
    subset: str = "en"
    tokenizer_name: str = "gpt2"
    seq_length: int = 512
    batch_size: int = 8  # Reduced from 16 to save memory for regularizer
    num_workers: int = 4
    streaming: bool = True
    total_tokens: int = 10_000_000_000  # 10B tokens


@dataclass
class ModelConfig:
    vocab_size: int = 50257
    n_positions: int = 1024
    n_embd: int = 768
    n_layer: int = 12
    n_head: int = 12
    n_inner: int = 3072  # 4 * n_embd
    activation_function: str = "gelu_new"
    resid_pdrop: float = 0.1
    embd_pdrop: float = 0.1
    attn_pdrop: float = 0.1
    layer_norm_epsilon: float = 1e-5
    initializer_range: float = 0.02


@dataclass
class RegularizationConfig:
    n_power_iterations: int = 2  # Reduced from 3 to save memory
    n_hutchinson_probes: int = 3  # Reduced from 5 to save memory
    epsilon: float = 1e-12
    lambda_init: float = 0.01
    lambda_min: float = 1e-4
    lambda_max: float = 1.0
    lambda_decay: float = 0.95
    lambda_growth: float = 1.05
    adaptive_tuning: bool = True


@dataclass
class TrainingConfig:
    learning_rate: float = 3e-4
    weight_decay: float = 0.1
    betas: tuple = (0.9, 0.95)
    warmup_steps: int = 2000
    gradient_accumulation_steps: int = 16  # Increased to maintain effective batch 128 with smaller batch_size
    max_grad_norm: float = 1.0
    seed: int = 42
    eval_interval: int = 500
    checkpoint_interval: int = 10000
    stable_rank_eval_interval: int = 1000
    use_mixed_precision: bool = False  # Disabled for compatibility


@dataclass
class EvaluationConfig:
    eval_batch_size: int = 32
    eval_samples: int = 1000
    perplexity_stride: int = 256
    stable_rank_samples: int = 100
    # Gate targets
    target_sr_reduction: float = 0.20
    target_ppl_deviation: float = 0.01
    target_layer_variance_ratio: float = 2.0
    target_measurement_cv: float = 0.15


@dataclass
class VisualizationConfig:
    output_dir: str = "figures"
    dpi: int = 300
    figsize: tuple = (10, 6)
    style: str = "seaborn-v0_8-darkgrid"
    save_formats: list = field(default_factory=lambda: ["png"])


@dataclass
class ValidationConfig:
    baseline_checkpoint: str = "checkpoints/baseline/final.pt"
    proposed_checkpoint: str = "checkpoints/proposed/final.pt"
    implicit_checkpoint: str = "checkpoints/implicit_control/final.pt"
    report_path: str = "results/gate_validation.json"
    gate_type: str = "MUST_WORK"


@dataclass
class ExperimentConfig:
    """Complete configuration for SCSL experiment variants."""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    regularization: RegularizationConfig = field(default_factory=RegularizationConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)

    variant: str = "baseline"
    output_dir: str = "outputs"
    device: str = "cuda"
    total_steps: int = 0

    def __post_init__(self):
        # Compute total steps from tokens
        tokens_per_step = (
            self.data.batch_size *
            self.training.gradient_accumulation_steps *
            self.data.seq_length
        )
        self.total_steps = self.data.total_tokens // tokens_per_step


def get_baseline_config() -> ExperimentConfig:
    """Standard GPT-2 without regularization."""
    config = ExperimentConfig(variant="baseline")
    config.regularization.lambda_init = 0.0
    config.regularization.adaptive_tuning = False
    config.output_dir = "outputs/baseline"
    return config


def get_proposed_config() -> ExperimentConfig:
    """GPT-2 with stable rank regularization."""
    config = ExperimentConfig(variant="proposed")
    config.regularization.adaptive_tuning = True
    config.output_dir = "outputs/proposed"
    return config


def get_implicit_control_config() -> ExperimentConfig:
    """GPT-2 with adaptive LR (no explicit regularization)."""
    config = ExperimentConfig(variant="implicit_control")
    config.regularization.lambda_init = 0.0
    config.regularization.adaptive_tuning = False
    config.output_dir = "outputs/implicit_control"
    return config
