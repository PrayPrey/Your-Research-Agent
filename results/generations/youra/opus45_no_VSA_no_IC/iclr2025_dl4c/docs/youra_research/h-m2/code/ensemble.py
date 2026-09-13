"""Ensemble methods for H-M2."""
import numpy as np


def majority_vote(verdicts: dict) -> bool:
    """2-of-3 majority vote."""
    return sum(verdicts.values()) >= 2


def weighted_majority(verdicts: dict, weights: dict) -> bool:
    """Weighted majority vote by per-judge accuracy."""
    weighted_sum = sum(weights.get(j, 1.0) * v for j, v in verdicts.items())
    threshold = sum(weights.get(j, 1.0) for j in verdicts) / 2
    return weighted_sum > threshold


def unanimous_flag(verdicts: dict) -> bool:
    """True if all judges agree."""
    return len(set(verdicts.values())) == 1


def two_tier_subset(verdicts: dict, exclude: str = "7B") -> bool:
    """AB3: Vote excluding one judge. Tie-break: proprietary wins."""
    remaining = {k: v for k, v in verdicts.items() if k != exclude}
    votes = list(remaining.values())
    if votes[0] == votes[1]:
        return votes[0]
    # Tie-break with proprietary
    return remaining.get("proprietary", votes[0])


def random_ensemble(verdicts: dict, rng: np.random.Generator) -> bool:
    """AB4: Random selection among judges."""
    return rng.choice(list(verdicts.values()))
