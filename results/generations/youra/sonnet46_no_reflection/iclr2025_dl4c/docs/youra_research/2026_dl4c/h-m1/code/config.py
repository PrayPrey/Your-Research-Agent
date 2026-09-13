import os
import yaml
from dataclasses import dataclass, asdict
from trl import GRPOConfig, DPOConfig


@dataclass
class ExperimentConfig:
    """H-E1 config preserved for compatibility (used by generate_solutions shim)."""
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: int = 42
    dtype: str = "bfloat16"
    grpo_lr: float = 1e-6
    grpo_batch_size: int = 1
    grpo_grad_accum: int = 16
    grpo_num_generations: int = 4
    grpo_beta: float = 0.04
    grpo_steps: int = 1000
    grpo_save_steps: int = 100
    dpo_lr: float = 5e-7
    dpo_batch_size: int = 1
    dpo_grad_accum: int = 16
    dpo_beta: float = 0.1
    dpo_steps: int = 1000
    dpo_save_steps: int = 100
    training_dataset: str = "sahil2801/CodeAlpaca-20k"
    kl_prompt_count: int = 100
    dpo_min_pairs: int = 1000
    kl_tolerance: float = 0.05
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95
    gate_magnitude: float = 0.20
    output_dir: str = "outputs"
    figures_dir: str = "../figures"
    checkpoint_dir: str = "../checkpoints"


def get_config() -> ExperimentConfig:
    return ExperimentConfig()


def make_grpo_config(cfg: ExperimentConfig, output_dir: str) -> GRPOConfig:
    return GRPOConfig(
        output_dir=output_dir,
        learning_rate=cfg.grpo_lr,
        per_device_train_batch_size=cfg.grpo_batch_size,
        gradient_accumulation_steps=cfg.grpo_grad_accum,
        num_generations=cfg.grpo_num_generations,
        beta=cfg.grpo_beta,
        max_steps=cfg.grpo_steps,
        save_steps=cfg.grpo_save_steps,
        seed=cfg.seed,
        bf16=(cfg.dtype == "bfloat16"),
        fp16=(cfg.dtype == "float16"),
        dataloader_num_workers=0,
        remove_unused_columns=False,
        log_completions=False,
        report_to="none",
        gradient_checkpointing=True,
    )


def make_dpo_config(cfg: ExperimentConfig, output_dir: str) -> DPOConfig:
    return DPOConfig(
        output_dir=output_dir,
        learning_rate=cfg.dpo_lr,
        per_device_train_batch_size=cfg.dpo_batch_size,
        gradient_accumulation_steps=cfg.dpo_grad_accum,
        beta=cfg.dpo_beta,
        max_steps=cfg.dpo_steps,
        save_steps=cfg.dpo_save_steps,
        seed=cfg.seed,
        bf16=(cfg.dtype == "bfloat16"),
        fp16=(cfg.dtype == "float16"),
        dataloader_num_workers=0,
        remove_unused_columns=False,
        report_to="none",
    )


@dataclass
class M1ExperimentConfig:
    # Paths (relative to code directory)
    h_e1_code_path: str = "../../h-e1/code"
    h_e1_checkpoint_base: str = "../../h-e1/checkpoints"
    grpo_binary_checkpoint_dir: str = "../../h-e1/checkpoints/grpo"
    grpo_errortype_checkpoint_dir: str = "../../h-e1/checkpoints/grpo"
    dpo_checkpoint_dir: str = "../../h-e1/checkpoints/dpo"
    sft_model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    output_dir: str = "../outputs"
    figures_dir: str = "../figures"

    # Experiment
    seed: int = 1
    kl_tolerance: float = 0.15
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95
    dtype: str = "bfloat16"
    max_new_tokens: int = 512

    # Gate thresholds
    mann_whitney_alpha: float = 0.05
    spearman_rho_threshold: float = 0.5
    num_checkpoint_pairs: int = 27
    min_total_edits: int = 1

    # Smoke test scale
    smoke_test_problems: int = 10
    smoke_test_pairs: int = 3


def get_m1_config() -> M1ExperimentConfig:
    return M1ExperimentConfig()


def load_config_from_yaml(path: str) -> M1ExperimentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    fields = M1ExperimentConfig.__dataclass_fields__
    return M1ExperimentConfig(**{k: v for k, v in data.items() if k in fields})


def save_config_to_yaml(cfg: M1ExperimentConfig, path: str) -> None:
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(asdict(cfg), f, default_flow_style=False)


def validate_config(cfg: M1ExperimentConfig) -> None:
    assert 0 < cfg.mann_whitney_alpha < 1, "mann_whitney_alpha must be in (0,1)"
    assert 0 < cfg.spearman_rho_threshold <= 1, "spearman_rho_threshold must be in (0,1]"
    assert 0 < cfg.kl_tolerance < 10, "kl_tolerance must be in (0,10)"
    assert cfg.bootstrap_samples >= 100, "bootstrap_samples must be >= 100"
    assert cfg.num_checkpoint_pairs >= 1, "num_checkpoint_pairs must be >= 1"
    assert cfg.min_total_edits >= 0, "min_total_edits must be >= 0"
    assert cfg.seed >= 0, "seed must be >= 0"
