import importlib.util
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import List

import yaml

# Load h-e1 config via importlib to avoid circular import (both files named config.py)
_h_e1_config_path = os.path.join(os.path.dirname(__file__), "../../h-e1/code/config.py")
_spec = importlib.util.spec_from_file_location("h_e1_config", _h_e1_config_path)
_h_e1_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_h_e1_config)
BaseGRPOConfig = _h_e1_config.GRPOConfig
# Alias so h-e1 sibling modules (data.py, rewards.py) that do
# `from config import GRPOConfig` continue to work when h-m1/code is on sys.path
GRPOConfig = BaseGRPOConfig
# Aliases for h-e1 sibling modules
load_config = _h_e1_config.load_config
save_config = _h_e1_config.save_config


@dataclass
class HM1Config(BaseGRPOConfig):
    # Override H-E1 defaults for H-M1
    train_steps: int = 1000
    kl_beta: float = 0.04
    warmup_steps: int = 100
    max_new_tokens: int = 512
    max_prompt_tokens: int = 512
    sandbox_timeout: int = 3
    output_dir: str = "outputs/h-m1"

    # Multi-step checkpointing (replaces single checkpoint_step)
    checkpoint_steps: List[int] = field(default_factory=lambda: [200, 400, 600, 800, 1000])

    # Evaluation schedules
    eval_humaneval_at_steps: List[int] = field(default_factory=lambda: [200, 400, 600, 800, 1000])
    eval_mbpp_at_step: int = 1000
    eval_apps_val_at_step: int = 1000

    # APPS validation holdout
    apps_val_size: int = 500

    # Statistical analysis
    bootstrap_n: int = 1000

    # Monitoring
    fraction_partial_alert_threshold: float = 0.05


@dataclass
class VisualizerConfig:
    figure_dpi: int = 300
    figure_format: str = "png"
    color_binary: str = "#1f77b4"
    color_ratio: str = "#ff7f0e"
    output_dir: str = "docs/youra_research/h-m1/figures"


def load_hm1_config(path: str = None) -> HM1Config:
    if path and os.path.exists(path):
        with open(path) as f:
            data = yaml.safe_load(f)
        valid = {k: v for k, v in data.items() if hasattr(HM1Config, k)}
        return HM1Config(**valid)
    return HM1Config()


def save_hm1_config(cfg: HM1Config, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    with open(path, "w") as f:
        yaml.dump(asdict(cfg), f, default_flow_style=False)
