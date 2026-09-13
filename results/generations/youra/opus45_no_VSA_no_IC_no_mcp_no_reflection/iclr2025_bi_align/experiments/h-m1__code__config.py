"""H-M1 Configuration: Combined PPO Reward Training."""
from dataclasses import dataclass, field
from typing import Literal


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
    alpha: float = 0.5   # R_helpfulness weight
    beta: float = 0.5    # R_IFEval weight
    ifeval_soft_margin: float = 0.1


@dataclass
class PPOConfig:
    learning_rate: float = 1.41e-5
    batch_size: int = 8  # reduced for memory
    mini_batch_size: int = 2
    gradient_accumulation_steps: int = 8  # effective batch 64
    ppo_epochs: int = 4
    kl_coeff: float = 0.05
    clip_range: float = 0.2
    value_clip_range: float = 0.2
    total_steps: int = 1000
    seed: int = 42


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


# Ablation variants
T1_COMBINED = RewardConfig(alpha=0.5, beta=0.5)
B2_HELPFULNESS_ONLY = RewardConfig(alpha=1.0, beta=0.0)
ABLATION_ALPHA_DOMINANT = RewardConfig(alpha=0.7, beta=0.3)
ABLATION_BETA_DOMINANT = RewardConfig(alpha=0.3, beta=0.7)

# Recovery config for divergence
PPO_RECOVERY = PPOConfig(learning_rate=5e-6, kl_coeff=0.1)
