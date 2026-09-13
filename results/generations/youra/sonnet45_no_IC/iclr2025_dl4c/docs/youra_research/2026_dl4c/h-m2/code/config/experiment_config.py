"""
Experiment Configuration for h-e1: Tri-Modal RL Framework
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class DataConfig:
    """Dataset configuration"""
    dataset_name: str = "humaneval_mbpp_combined"
    humaneval_split: str = "test"
    mbpp_train_split: str = "train"
    mbpp_test_split: str = "test"
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    max_length: int = 512
    batch_size: int = 32
    num_workers: int = 4
    cache_dir: str = "../data/datasets"


@dataclass
class ModelConfig:
    """Model architecture configuration"""
    model_name: str = "Salesforce/codegen-350M-mono"  # Smaller for PoC
    max_length: int = 512
    temperature: float = 0.8
    top_p: float = 0.95
    num_return_sequences: int = 1


@dataclass
class TriModalAggregatorConfig:
    """Tri-modal reward aggregator configuration"""
    num_phases: int = 3
    # Initial weights for each signal (exec, AI, human)
    initial_weights: List[float] = field(default_factory=lambda: [0.8, 0.1, 0.1])
    # Peak timesteps for each phase (0-30%, 30-70%, 70-100%)
    peak_timesteps: List[float] = field(default_factory=lambda: [0.15, 0.5, 0.85])
    # Decay rates (transition sharpness)
    decay_rates: List[float] = field(default_factory=lambda: [0.5, 0.3, 0.2])
    # Percentile for normalization
    percentile_window: int = 100


@dataclass
class FeedbackConfig:
    """Feedback collection configuration"""
    # Execution feedback
    execution_timeout: float = 5.0  # seconds per test
    sandbox_enabled: bool = True

    # AI feedback (reward model)
    reward_model_path: Optional[str] = None
    reward_model_name: str = "microsoft/codebert-base"  # Fallback

    # Human feedback
    annotation_cache_path: str = "./data/annotations/cache.json"
    fallback_score: float = 0.5  # When annotation unavailable


@dataclass
class PPOConfig:
    """PPO training configuration"""
    learning_rate: float = 5e-5
    batch_size: int = 32
    mini_batch_size: int = 8
    ppo_epochs: int = 4
    max_grad_norm: float = 1.0
    clip_range: float = 0.2
    clip_range_vf: float = 0.2
    vf_coef: float = 0.5
    ent_coef: float = 0.01
    gamma: float = 0.99
    gae_lambda: float = 0.95
    target_kl: float = 0.01

    # Training schedule
    total_steps: int = 10000  # PoC: 10k steps
    gradient_accumulation_steps: int = 1
    warmup_steps: int = 500
    logging_steps: int = 10
    save_steps: int = 1000
    eval_steps: int = 500


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration"""
    # Sub-configs
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    aggregator: TriModalAggregatorConfig = field(default_factory=TriModalAggregatorConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    ppo: PPOConfig = field(default_factory=PPOConfig)

    # Experiment metadata
    experiment_name: str = "h-e1-trimodal-poc"
    seed: int = 42
    device: str = "cuda"
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./models"
    log_dir: str = "./logs"

    # Baseline configurations
    baseline_types: List[str] = field(default_factory=lambda: [
        "execution_only",
        "human_only",
        "ai_only",
        "trimodal"
    ])

    # Gate criteria (MUST_WORK)
    must_work_criteria: dict = field(default_factory=lambda: {
        "code_runs": True,
        "mechanism_implemented": True,
        "metrics_measurable": True,
        "minimum_improvement": 0.0  # PoC: any positive direction
    })


def load_config(config_path: Optional[str] = None) -> ExperimentConfig:
    """Load experiment configuration"""
    if config_path is None:
        return ExperimentConfig()

    import json
    with open(config_path, 'r') as f:
        config_dict = json.load(f)

    # TODO: Deserialize into ExperimentConfig
    return ExperimentConfig(**config_dict)
