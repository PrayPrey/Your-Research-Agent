from dataclasses import dataclass, field


@dataclass
class TrainingConfig:
    lr: float = 1e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    max_length: int = 1024
    max_new_tokens: int = 512
    seed: int = 42
    precision: str = "bfloat16"
    grad_clip: float = 1.0
    warmup_steps: int = 100
    lr_schedule: str = "cosine"


@dataclass
class GRPOConfig:
    num_generations: int = 8   # G rollouts per prompt
    beta: float = 0.04
    temperature_rollout: float = 0.8


@dataclass
class RewardConfig:
    timeout: float = 3.0
    temperature_eval: float = 0.2


@dataclass
class PathsConfig:
    checkpoints_dir: str = "checkpoints"
    results_dir: str = "results/h-e1"
    logs_dir: str = "logs"
    figures_dir: str = "docs/youra_research/h-e1/figures"


@dataclass
class BootstrapConfig:
    n_boot: int = 1000
    seed: int = 42
    ci_level: float = 0.95
    gate_ratio: float = 1.5


@dataclass
class ExperimentConfig:
    model_name: str = "deepseek-ai/deepseek-coder-7b-base"
    fallback_model_name: str = "deepseek-ai/deepseek-coder-1b3-base"
    ceiling_check_threshold: float = 0.90
    training: TrainingConfig = field(default_factory=TrainingConfig)
    grpo: GRPOConfig = field(default_factory=GRPOConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    reward_monitoring_path: str = "logs/reward_monitoring.jsonl"
    config_dump_path: str = "logs/config_dump.json"
    bigcode_harness_commit: str = "FILL_BEFORE_RUN"


def make_config_dict(cfg: ExperimentConfig = None) -> dict:
    """Flat dict for passing to train() functions (matches architecture signatures)."""
    if cfg is None:
        cfg = ExperimentConfig()
    return {
        "model_name": cfg.model_name,
        "fallback_model_name": cfg.fallback_model_name,
        "ceiling_check_threshold": cfg.ceiling_check_threshold,
        "lr": cfg.training.lr,
        "batch_size": cfg.training.batch_size,
        "grad_accum": cfg.training.grad_accum,
        "epochs": cfg.training.epochs,
        "max_length": cfg.training.max_length,
        "max_new_tokens": cfg.training.max_new_tokens,
        "seed": cfg.training.seed,
        "precision": cfg.training.precision,
        "grad_clip": cfg.training.grad_clip,
        "warmup_steps": cfg.training.warmup_steps,
        "lr_schedule": cfg.training.lr_schedule,
        "num_generations": cfg.grpo.num_generations,
        "beta": cfg.grpo.beta,
        "temperature_rollout": cfg.grpo.temperature_rollout,
        "timeout": cfg.reward.timeout,
        "temperature_eval": cfg.reward.temperature_eval,
        "checkpoints_dir": cfg.paths.checkpoints_dir,
        "results_dir": cfg.paths.results_dir,
        "logs_dir": cfg.paths.logs_dir,
        "figures_dir": cfg.paths.figures_dir,
        "n_boot": cfg.bootstrap.n_boot,
        "bootstrap_seed": cfg.bootstrap.seed,
        "ci_level": cfg.bootstrap.ci_level,
        "gate_ratio": cfg.bootstrap.gate_ratio,
        "reward_monitoring_path": cfg.reward_monitoring_path,
        "config_dump_path": cfg.config_dump_path,
    }


DATA_CONFIG = {
    "hf_id": "codeparrot/apps",
    "split": "train",
    "min_test_cases": 1,
    "max_length": 1024,
    "truncation": True,
    "padding": "max_length",
    "difficulty_map": {
        "introductory": "intro",
        "interview": "interview",
        "competition": "competition",
    },
}

EVAL_CONFIG = {
    "tasks": {
        "humaneval": "humaneval",
        "mbpp": "mbpp",
        "lcb_easy": "livecodebench",
        "lcb_medium": "livecodebench",
        "lcb_hard": "livecodebench",
    },
    "lcb_difficulty_flag": {
        "lcb_easy": "easy",
        "lcb_medium": "medium",
        "lcb_hard": "hard",
    },
    "n_samples": 1,
    "temperature": 0.2,
    "output_pattern": "results/h-e1/{model_tag}_{task_name}.json",
    "harness_commit": "FILL_BEFORE_RUN",
}
