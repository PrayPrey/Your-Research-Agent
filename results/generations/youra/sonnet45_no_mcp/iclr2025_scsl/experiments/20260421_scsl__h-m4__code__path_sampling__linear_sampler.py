"""Linear interpolation baseline sampler"""

import numpy as np
import torch
from typing import List, Dict
from .base import PathSampler

class LinearSampler(PathSampler):
    """Linear interpolation baseline (identical to FGE for validation)"""

    def sample(self) -> List[Dict[str, torch.Tensor]]:
        """
        Same as FGESampler - validates FGE is not over-engineered.
        This serves as a sanity check that the coupling exists regardless
        of path type.

        Returns:
            List[Dict] of M=20 checkpoints
        """
        checkpoints = []
        alphas = np.linspace(0, 1, self.num_samples)

        for alpha in alphas:
            checkpoint = {}
            for key in self.endpoint_1.keys():
                checkpoint[key] = (
                    (1 - alpha) * self.endpoint_1[key] +
                    alpha * self.endpoint_2[key]
                )
            checkpoints.append(checkpoint)

        return checkpoints
