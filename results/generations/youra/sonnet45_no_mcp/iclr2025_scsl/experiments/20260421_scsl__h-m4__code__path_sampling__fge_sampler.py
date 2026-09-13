"""Fast Geometric Ensembling (FGE) path sampler"""

import numpy as np
import torch
from typing import List, Dict
from .base import PathSampler

class FGESampler(PathSampler):
    """Fast Geometric Ensembling path sampler (linear interpolation)"""

    def sample(self) -> List[Dict[str, torch.Tensor]]:
        """
        Linear interpolation: θ(α) = (1-α)θ₁ + αθ₂

        Algorithm:
        1. For α in linspace(0, 1, M):
        2.   For each parameter key:
        3.     Interpolate: θ[key] = (1-α)*θ₁[key] + α*θ₂[key]
        4.   Append interpolated state_dict to checkpoints

        Returns:
            List[Dict] of M=20 checkpoints
        """
        checkpoints = []
        alphas = np.linspace(0, 1, self.num_samples)

        for alpha in alphas:
            checkpoint = {}
            for key in self.endpoint_1.keys():
                # Linear interpolation
                checkpoint[key] = (
                    (1 - alpha) * self.endpoint_1[key] +
                    alpha * self.endpoint_2[key]
                )
            checkpoints.append(checkpoint)

        return checkpoints
