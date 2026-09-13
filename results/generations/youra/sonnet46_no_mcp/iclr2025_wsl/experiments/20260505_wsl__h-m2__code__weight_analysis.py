"""Core weight analysis functions for H-E1 permutation orbit analysis."""
from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn.functional as F

from config import ExperimentConfig


def flatten_weights(state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
    """Flatten all weight/bias tensors into a single float32 CPU vector.

    Handles flat pre-vectorized weights (_flat_weights format from dataset .pt).
    """
    # Pre-vectorized format from Zenodo dataset loader
    if "_flat_weights" in state_dict or (
        len(state_dict) == 1 and "weights_flat" in state_dict
    ):
        w = state_dict.get("weights_flat", next(iter(state_dict.values())))
        result = w.detach().float().flatten().cpu()
        assert result.dtype == torch.float32
        return result

    tensors = [
        p.detach().float().flatten()
        for k, p in state_dict.items()
        if "weight" in k or "bias" in k
    ]
    if not tensors:
        raise ValueError("No weight or bias tensors found in state_dict")

    result = torch.cat(tensors).cpu()
    assert result.dtype == torch.float32
    assert result.device.type == "cpu"
    return result


def compute_cosine_distance(w1: torch.Tensor, w2: torch.Tensor) -> float:
    """Return cosine distance = 1 - cosine_similarity, in [0, 2]."""
    w1f = w1.float().unsqueeze(0)
    w2f = w2.float().unsqueeze(0)
    return float((1.0 - F.cosine_similarity(w1f, w2f)).item())


def stratified_pair_sample(
    checkpoints: List[Dict[str, Any]],
    n_per_decile: int = 50,
    acc_threshold: float = 0.01,
    seed: int = 42,
) -> List[Tuple[Dict, Dict, int]]:
    """Sample model pairs stratified by accuracy decile.

    Returns list of (checkpoint_i, checkpoint_j, decile_index) tuples.
    """
    np.random.seed(seed)
    accuracies = np.array([c["test_accuracy"] for c in checkpoints])
    decile_bins = np.percentile(accuracies, np.arange(0, 110, 10))

    pairs: List[Tuple[Dict, Dict, int]] = []
    for d in range(10):
        lo, hi = decile_bins[d], decile_bins[d + 1]
        in_decile = [c for c in checkpoints if lo <= c["test_accuracy"] <= hi]

        indices = list(range(len(in_decile)))
        np.random.shuffle(indices)

        sampled = 0
        for ii, i in enumerate(indices):
            for j in indices[ii + 1:]:
                if abs(in_decile[i]["test_accuracy"] - in_decile[j]["test_accuracy"]) < acc_threshold:
                    pairs.append((in_decile[i], in_decile[j], d))
                    sampled += 1
                    if sampled >= n_per_decile:
                        break
            if sampled >= n_per_decile:
                break

    return pairs
