"""Random sampling from testable pool."""

import random
from typing import List, Dict


class RandomSampler:
    """Sample testable hypotheses without replacement."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def sample_testable(self, hypotheses: List[Dict], k: int = 20) -> List[Dict]:
        """Sample k hypotheses from testable subset.

        Returns: Random sample without replacement
        """
        testable = [h for h in hypotheses if h['system_classification'] == 'testable']

        if len(testable) < k:
            print(f"Warning: Only {len(testable)} testable hypotheses (< {k}). Using all available.")
            return testable

        return random.sample(testable, k)
