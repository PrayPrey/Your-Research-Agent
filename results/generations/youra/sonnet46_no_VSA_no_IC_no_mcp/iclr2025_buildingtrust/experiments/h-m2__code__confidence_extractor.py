"""Extract per-cell accuracy and confidence statistics from loaded JSONL arrays."""
import logging
from dataclasses import dataclass
from typing import Optional
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CellStats:
    accuracy: float
    mean_conf_wrong: Optional[float]
    mean_conf_correct: Optional[float]
    n_wrong: int
    n_correct: int
    n_total: int
    mean_conf_all: float


def extract_cell_stats(data: dict) -> CellStats:
    """Compute accuracy and confidence breakdown from loaded JSONL arrays.

    data keys: conf (float32), correct (int32), pred (int32), label (int32)
    """
    conf    = data["conf"]
    correct = data["correct"].astype(bool)
    n_total = len(conf)

    if n_total == 0:
        raise ValueError("Empty data array — cannot compute stats.")

    accuracy   = float(correct.mean())
    wrong_mask = ~correct

    n_correct = int(correct.sum())
    n_wrong   = int(wrong_mask.sum())

    mean_conf_wrong   = float(conf[wrong_mask].mean())   if n_wrong   > 0 else None
    mean_conf_correct = float(conf[correct].mean())      if n_correct > 0 else None
    mean_conf_all     = float(conf.mean())

    # Degenerate confidence warning
    if conf.std() < 0.01:
        logger.warning("Degenerate confidence distribution (std=%.4f) — check logit normalization.", conf.std())

    return CellStats(
        accuracy=accuracy,
        mean_conf_wrong=mean_conf_wrong,
        mean_conf_correct=mean_conf_correct,
        n_wrong=n_wrong,
        n_correct=n_correct,
        n_total=n_total,
        mean_conf_all=mean_conf_all,
    )
