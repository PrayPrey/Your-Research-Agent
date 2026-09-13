"""Configuration for H-E1: Reward Information Bandwidth Experiment."""
from dataclasses import dataclass

REWARD_CONDITIONS = ["binary", "categorical", "high_bandwidth"]
SEEDS = [0, 1, 2, 3, 4]

HIGH_BANDWIDTH_WEIGHTS = (0.5, 0.3, 0.2)

ERROR_CATEGORY_SCORES = {
    "passed": 1.0,
    "assertion_error": 0.5,
    "runtime_error": 0.25,
    "syntax_error": 0.0,
}


@dataclass
class ExperimentConfig:
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    learning_rate: float = 1e-5
    batch_size: int = 4
    ppo_epochs: int = 4
    init_kl_coef: float = 0.05
    train_epochs: int = 3
    pass_at_1_threshold: float = 0.3
    seed: int = 0
    condition: str = "binary"
    torch_dtype: str = "bfloat16"
    test_timeout_s: float = 5.0
    checkpoint_dir: str = "checkpoints"
    eval_interval: int = 50
    max_new_tokens: int = 256


@dataclass
class EvalConfig:
    pass_at_1_threshold: float = 0.3
    eval_timeout_s: float = 5.0
    mbpp_test_size: int = 500
    humaneval_test_size: int = 164
    significance_alpha: float = 0.05
    n_seeds: int = 5
