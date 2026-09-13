"""Abstract base class for path sampling strategies"""

from abc import ABC, abstractmethod
from typing import List, Dict
import torch

class PathSampler(ABC):
    """Abstract base for checkpoint sampling strategies"""

    def __init__(
        self,
        endpoint_1: Dict[str, torch.Tensor],
        endpoint_2: Dict[str, torch.Tensor],
        num_samples: int = 20
    ):
        """
        Args:
            endpoint_1: First endpoint state_dict (ERM)
            endpoint_2: Second endpoint state_dict (DRO)
            num_samples: Number of checkpoints to sample
        """
        self.endpoint_1 = endpoint_1
        self.endpoint_2 = endpoint_2
        self.num_samples = num_samples

        # Validate endpoints have same keys
        assert set(endpoint_1.keys()) == set(endpoint_2.keys()), \
            "Endpoints must have same parameter keys"

    @abstractmethod
    def sample(self) -> List[Dict[str, torch.Tensor]]:
        """
        Sample checkpoints along path.

        Returns:
            List of M state_dicts (checkpoints)
        """
        pass
