from dataclasses import dataclass, field
from typing import Tuple, Literal
import yaml


@dataclass
class DataConfig:
    dataset_name: str = "wikitext"
    dataset_subset: str = "wikitext-103-raw-v1"
    calibration_size: int = 1000
    validation_size: int = 200
    max_length: int = 512
    cache_dir: str = "./data/wikitext103_distillation"
    num_workers: int = 4
    pin_memory: bool = True


@dataclass
class TeacherConfig:
    model_name: str = "gpt2"
    n_layer: int = 12
    n_head: int = 12
    n_embd: int = 768
    vocab_size: int = 50257
    freeze: bool = True


@dataclass
class StudentConfig:
    architecture: str = "mamba_ssm"
    d_model: int = 768
    n_layer: int = 12
    vocab_size: int = 50257
    ssm_d_state: int = 16
    ssm_d_conv: int = 4
    ssm_expand: int = 2


@dataclass
class LossConfig:
    loss_type: str = "layer_wise_mse"
    normalization: bool = True
    epsilon: float = 1e-8


@dataclass
class OptimizerConfig:
    optimizer_type: str = "adamw"
    lr: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    eps: float = 1e-8
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    warmup_steps: int = 10
    total_steps: int = 100


@dataclass
class TrainingConfig:
    max_steps: int = 100
    batch_size: int = 32
    gradient_accumulation_steps: int = 4
    mixed_precision: bool = True
    logging_steps: int = 10
    eval_steps: int = 50
    checkpoint_steps: int = 50
    early_stop_threshold: float = 0.1
    seed: int = 42


@dataclass
class ExperimentConfig:
    hypothesis_id: str = "h-e1"
    experiment_name: str = "layer_wise_mse_distillation"
    output_dir: str = "experiments/h-e1"

    data: DataConfig = field(default_factory=DataConfig)
    teacher: TeacherConfig = field(default_factory=TeacherConfig)
    student: StudentConfig = field(default_factory=StudentConfig)
    loss: LossConfig = field(default_factory=LossConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str):
        with open(path, 'w') as f:
            yaml.dump(self.__dict__, f, default_flow_style=False)
