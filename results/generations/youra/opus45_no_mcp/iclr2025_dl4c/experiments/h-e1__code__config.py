"""Configuration for h-e1 Error-Type Gating experiment."""
from dataclasses import dataclass, field
from typing import List

SEED = 42
MODEL_NAME = "Salesforce/codet5-small"  # ponytail: small model for PoC, use codet5-large for full
LR = 5e-5
BATCH_SIZE = 8
TOTAL_STEPS = 50_000
WARMUP_STEPS = 500
MAX_INPUT_LEN = 512
MAX_OUTPUT_LEN = 256
PASS_THRESHOLD = 0.30

U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError',
                 'TypeError', 'AttributeError', 'KeyError', 'IndexError'}
U_IGNORE_ERRORS = {'RuntimeError', 'RecursionError', 'MemoryError',
                   'TimeoutError', 'AssertionError'}


@dataclass
class ModelConfig:
    base_model: str = "Salesforce/codet5-large"
    max_input_length: int = 512
    max_output_length: int = 256


@dataclass
class TrainingConfig:
    learning_rate: float = 5e-5
    batch_size: int = 8
    epochs: int = 5
    total_steps: int = 50_000
    warmup_steps: int = 500
    optimizer: str = "AdamW"
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    weight_decay: float = 0.01
    entropy_bonus: float = 0.01
    seed: int = 42


@dataclass
class RewardConfig:
    fine_penalty: float = -1.0
    coarse_penalty: float = -0.1
    pass_reward: float = 1.0
    gating_mode: str = "fine_gated"


@dataclass
class EvalConfig:
    checkpoint_interval: int = 1000
    pass_at_1_threshold: float = 0.30
    test_set_size: int = 5000
    execution_timeout: int = 30


@dataclass
class ExperimentConfig:
    seeds: List[int] = field(default_factory=lambda: [42])
    conditions: List[str] = field(default_factory=lambda: ["fine_always", "fine_gated"])
    gpu: str = "A100-40GB"
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)


def get_config():
    return ExperimentConfig()
