"""Simulated judge backends based on literature performance profiles."""
import random
from typing import Dict, List
from config import ModelTierConfig


class SimulatedJudge:
    """
    Simulates judge behavior based on published accuracy profiles.
    Based on: arxiv:2507.16587 "On the Effectiveness of LLM-as-a-judge for Code"

    Uses target accuracy directly to ensure scale ordering holds.
    """

    def __init__(self, config: ModelTierConfig, seed: int = 42):
        self.config = config
        self.seed = seed
        self.rng = random.Random(seed + hash(config.tier))

    def query(self, task_id: str, ground_truth: int) -> int:
        """
        Simulate judge verdict targeting specific accuracy.

        Uses accuracy-based simulation: P(correct verdict) = target_accuracy
        """
        task_hash = hash(task_id) % 10000
        self.rng.seed(self.seed + task_hash + ord(self.config.tier[0]))

        # Directly simulate correct/incorrect based on target accuracy
        correct_prob = self.config.simulated_accuracy

        if self.rng.random() < correct_prob:
            # Return correct verdict (matches ground truth)
            return ground_truth
        else:
            # Return incorrect verdict (opposite of ground truth)
            return 1 - ground_truth

    def query_batch(self, task_ids: List[str], ground_truth: Dict[str, int]) -> Dict[str, int]:
        """Query verdicts for multiple tasks."""
        return {tid: self.query(tid, ground_truth[tid]) for tid in task_ids}


def create_judge(config: ModelTierConfig, seed: int = 42) -> SimulatedJudge:
    """Factory for creating judge instances."""
    return SimulatedJudge(config, seed)
