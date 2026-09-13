"""Random baseline for PoC comparison."""

import random
from typing import List


class RandomBaseline:
    """Random confound flagging baseline."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def predict(self, n_samples: int) -> List[str]:
        """Generate random predictions. Returns: list of 'confounded' or 'unconfounded'."""
        return [random.choice(["confounded", "unconfounded"]) for _ in range(n_samples)]
