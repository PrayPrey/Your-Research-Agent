"""Utility functions for H-E1 experiment."""
import logging
import random
from pathlib import Path
from typing import Dict, Any

import numpy as np
import torch
import yaml

from config import ExperimentConfig


def set_seed(seed: int) -> None:
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger("h-e1")


def save_results_yaml(results: Dict[str, Any], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(results, f, default_flow_style=False, allow_unicode=True)


def ensure_dirs(cfg: ExperimentConfig) -> None:
    cfg.results_dir.mkdir(parents=True, exist_ok=True)
    cfg.figures_dir.mkdir(parents=True, exist_ok=True)
    cfg.data_dir.mkdir(parents=True, exist_ok=True)
