"""BatchNorm-free verification for H-E1."""
import random
from typing import Dict, List

import torch


def verify_bn_free(state_dict: Dict[str, torch.Tensor]) -> bool:
    """Return True if state_dict contains no BatchNorm parameters."""
    bn_keys = [
        k for k in state_dict.keys()
        if any(s in k.lower() for s in ["bn", "batch_norm", "running_mean", "running_var"])
    ]
    return len(bn_keys) == 0


def verify_zoo_bn_free(
    checkpoints: List[Dict],
    sample_size: int = 5,
    seed: int = 42,
) -> bool:
    """Verify a random sample of zoo checkpoints are BN-free."""
    random.seed(seed)
    sample = random.sample(checkpoints, min(sample_size, len(checkpoints)))
    return all(verify_bn_free(c["state_dict"]) for c in sample)
