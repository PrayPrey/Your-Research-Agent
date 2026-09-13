"""H-M2 Configuration: 7-Variant IFEval Gate."""
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    base_model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    reward_model_id: str = "OpenAssistant/reward-model-deberta-v3-large-v2"
    torch_dtype: str = "bfloat16"
    device_map: str = "auto"


@dataclass
class DataConfig:
    ultrafeedback_id: str = "openbmb/UltraFeedback"
    ultrafeedback_split: str = "train"
    ifeval_id: str = "google/IFEval"
    ifeval_train_ratio: float = 0.7
    ifeval_num_prompts: int = 541
    max_prompt_length: int = 512
    max_new_tokens: int = 256


@dataclass
class RewardConfig:
    alpha: float = 0.5
    beta: float = 0.5
    ifeval_soft_margin: float = 0.1


@dataclass
class PPOConfig:
    learning_rate: float = 1.41e-5
    batch_size: int = 8
    mini_batch_size: int = 2
    gradient_accumulation_steps: int = 8
    ppo_epochs: int = 4
    kl_coeff: float = 0.05
    clip_range: float = 0.2
    value_clip_range: float = 0.2
    total_steps: int = 1000
    seed: int = 1  # H-M2: NFR-2 fixed seed


@dataclass
class LoggingConfig:
    log_interval: int = 10
    checkpoint_interval: int = 250
    output_dir: str = "checkpoints"
    figures_dir: str = "figures"


@dataclass
class ExperimentConfig:
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


@dataclass
class ModelVariant:
    name: str
    alpha: float
    beta: float
    train: bool
    reward_mode: str  # "none" | "helpfulness_only" | "quality_only" | "combined"


VARIANTS: list[ModelVariant] = [
    ModelVariant("B1", 0.0, 0.0, train=False, reward_mode="none"),
    ModelVariant("B2", 1.0, 0.0, train=True, reward_mode="helpfulness_only"),
    ModelVariant("B3", 0.0, 0.0, train=True, reward_mode="quality_only"),
    ModelVariant("T1", 0.2, 0.8, train=True, reward_mode="combined"),
    ModelVariant("T2", 0.4, 0.6, train=True, reward_mode="combined"),
    ModelVariant("T3", 0.6, 0.4, train=True, reward_mode="combined"),
    ModelVariant("T4", 0.8, 0.2, train=True, reward_mode="combined"),
]


def build_config(variant: ModelVariant) -> ExperimentConfig:
    """Build config with variant's alpha/beta."""
    cfg = ExperimentConfig()
    cfg.reward = RewardConfig(alpha=variant.alpha, beta=variant.beta)
    cfg.ppo.seed = 1
    return cfg


@dataclass
class EvalConfig:
    ifeval_test_size: int = 500
    gate_threshold_pp: float = 0.02
    metrics: tuple[str, ...] = ("strict_accuracy", "loose_accuracy")
    constraint_categories: int = 25


@dataclass
class VizConfig:
    out_dir: str = "h-m2/results/figures"
    gate_chart_name: str = "gate_comparison.png"
    breakdown_chart_name: str = "constraint_breakdown.png"
    tradeoff_chart_name: str = "alpha_beta_tradeoff.png"
    dpi: int = 150
