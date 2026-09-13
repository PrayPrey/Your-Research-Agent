"""Configuration loader for h-e1 smoke test experiment."""

import yaml
from dataclasses import dataclass
from typing import List
from pathlib import Path


@dataclass
class ExperimentConfig:
    name: str
    hypothesis_id: str
    description: str
    seed: int


@dataclass
class ModelConfig:
    name: str
    trust_remote_code: bool
    torch_dtype: str
    device_map: str


@dataclass
class QuantizationConfig:
    load_in_4bit: bool
    bnb_4bit_quant_type: str
    bnb_4bit_compute_dtype: str
    bnb_4bit_use_double_quant: bool


@dataclass
class LoRAConfig:
    r: int
    lora_alpha: int
    target_modules: List[str]
    lora_dropout: float
    bias: str
    task_type: str


@dataclass
class DataConfig:
    dataset_name: str
    dataset_config: str
    split: str
    sequence_length: int
    num_test_sequences: int
    batch_size: int


@dataclass
class ValidationConfig:
    logit_range_min: float
    logit_range_max: float
    gradient_min: float
    gradient_max: float
    check_ssm_states: bool


@dataclass
class LoggingConfig:
    log_level: str
    log_file: str
    save_results_json: bool
    results_file: str


@dataclass
class H_E1_Config:
    experiment: ExperimentConfig
    model: ModelConfig
    quantization: QuantizationConfig
    lora: LoRAConfig
    data: DataConfig
    validation: ValidationConfig
    logging: LoggingConfig


def load_config(config_path: str) -> H_E1_Config:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)

    return H_E1_Config(
        experiment=ExperimentConfig(**config_dict['experiment']),
        model=ModelConfig(**config_dict['model']),
        quantization=QuantizationConfig(**config_dict['quantization']),
        lora=LoRAConfig(**config_dict['lora']),
        data=DataConfig(**config_dict['data']),
        validation=ValidationConfig(**config_dict['validation']),
        logging=LoggingConfig(**config_dict['logging'])
    )


def validate_config(config: H_E1_Config) -> None:
    """Validate configuration values."""
    assert config.experiment.seed >= 0, "Seed must be non-negative"
    assert config.lora.r > 0, "LoRA rank must be positive"
    assert config.lora.lora_alpha > 0, "LoRA alpha must be positive"
    assert config.data.sequence_length > 0, "Sequence length must be positive"
    assert config.data.num_test_sequences > 0, "Number of test sequences must be positive"
    assert config.validation.gradient_min < config.validation.gradient_max, \
        "Gradient min must be less than max"
