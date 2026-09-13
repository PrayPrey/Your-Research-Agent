"""Configuration for H-C1 CPDR vs RedPajama Defaults Comparison."""

import sys
import os

# Add h-e1 config to path for imports
H_E1_CODE = os.path.join(os.path.dirname(__file__), "..", "..", "h-e1", "code")
sys.path.insert(0, os.path.join(H_E1_CODE, "config"))
sys.path.insert(0, H_E1_CODE)

from config import (
    CurationConfig,
    MODEL_CONFIG,
    TRAIN_CONFIG,
    DATA_CONFIG,
    EVAL_CONFIG,
    DEDUP_MINHASH_PARAMS,
)

# CPDR-optimized (matches H-E1 D2)
CPDR_CONFIG = CurationConfig("CPDR", 50, "fuzzy_0.85")

# RedPajama literature defaults
REDPAJAMA_CONFIG = CurationConfig("RP", 30, "exact")

SEEDS = [42, 43, 44]
IMPROVEMENT_THRESHOLD = 0.01  # gate: CPDR_mean - RP_mean > 1%
SIGNIFICANCE_ALPHA = 0.05
CKPT_ROOT = os.path.join(os.path.dirname(__file__), "checkpoints")
