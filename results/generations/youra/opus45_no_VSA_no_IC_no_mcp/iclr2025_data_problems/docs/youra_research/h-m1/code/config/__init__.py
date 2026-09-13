"""Configuration for H-M1 Noise-Dilution Mechanism Experiment."""

from dataclasses import dataclass
from typing import Optional
import sys
import os
import importlib.util

h_e1_config_path = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'h-e1', 'code', 'config', 'config.py'
)
spec = importlib.util.spec_from_file_location("h_e1_config_mod", h_e1_config_path)
h_e1_config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h_e1_config)

MODEL_CONFIG = h_e1_config.MODEL_CONFIG
TRAIN_CONFIG = h_e1_config.TRAIN_CONFIG
DATA_CONFIG = h_e1_config.DATA_CONFIG
EVAL_CONFIG = h_e1_config.EVAL_CONFIG


@dataclass
class CurationConfig:
    config_id: str
    perplexity_pct: Optional[int]
    dedup: str = "none"


M1_CONFIGS = [
    CurationConfig("M1-C0", None),
    CurationConfig("M1-C1", 20),
    CurationConfig("M1-C2", 40),
    CurationConfig("M1-C3", 50),
    CurationConfig("M1-C4", 60),
    CurationConfig("M1-C5", 80),
    CurationConfig("M1-C6", 90),
]

LOSS_THRESHOLD = 3.5
CHECKPOINT_TOKENS = [1_000_000_000, 5_000_000_000, 10_000_000_000]
LOG_INTERVAL = 100
BOOTSTRAP_N = 10_000
BOOTSTRAP_PAIR = ("M1-C3", "M1-C0")
