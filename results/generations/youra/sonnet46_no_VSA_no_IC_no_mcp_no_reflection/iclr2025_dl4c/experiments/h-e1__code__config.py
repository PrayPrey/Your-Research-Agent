from dataclasses import dataclass, asdict
import yaml
import os


@dataclass
class GRPOConfig:
    # Model
    model_name: str = "deepseek-ai/deepseek-coder-6.7b-instruct"
    dtype: str = "bfloat16"

    # Data
    dataset_name: str = "codeparrot/apps"
    min_test_cases: int = 5
    max_prompt_tokens: int = 1024

    # GRPO rollout
    group_size: int = 8
    prompt_batch_size: int = 4  # reduced from 64 to fit GPU memory
    max_new_tokens: int = 256   # reduced from 512 for memory
    temperature: float = 1.0

    # Optimization
    learning_rate: float = 1e-6
    clip_ratio: float = 0.2
    kl_beta: float = 0.01
    warmup_steps: int = 10
    train_steps: int = 500

    # Checkpointing
    checkpoint_step: int = 200
    output_dir: str = "outputs"

    # Sandbox
    sandbox_timeout: int = 5

    # Experiment
    reward_mode: str = "binary"
    seed: int = 42


def load_config(path: str = None) -> GRPOConfig:
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        return GRPOConfig(**{k: v for k, v in data.items() if hasattr(GRPOConfig, k)})
    return GRPOConfig()


def save_config(cfg: GRPOConfig, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w") as f:
        yaml.dump(asdict(cfg), f, default_flow_style=False)
