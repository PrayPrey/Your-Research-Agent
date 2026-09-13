"""Random Mathlib tactic sampler."""
import numpy as np
from typing import List, Tuple
import yaml
from pathlib import Path


class TacticSampler:
    """Weighted random tactic sampling from Mathlib distribution."""

    def __init__(self, config_path: str):
        """Load tactic distribution from config."""
        with open(config_path) as f:
            config = yaml.safe_load(f)

        dist = config['tactic_distribution']
        self.tactics = list(dist.keys())
        self.weights = list(dist.values())

        # Validate weights sum to 1.0
        total = sum(self.weights)
        assert abs(total - 1.0) < 0.001, f"Weights sum to {total}, expected 1.0"

        # Normalize just in case
        self.weights = [w / total for w in self.weights]

        # Precompute cumulative distribution
        self.cumulative = np.cumsum(self.weights)

    def sample(self, rng: np.random.Generator) -> str:
        """Sample one tactic from distribution."""
        r = rng.random()
        idx = np.searchsorted(self.cumulative, r)
        return self.tactics[idx]

    def sample_sequence(self, budget: int, seed: int) -> List[str]:
        """Generate tactic sequence for proof search."""
        rng = np.random.default_rng(seed)
        return [self.sample(rng) for _ in range(budget)]


def create_proof_search_script(
    problem_id: str,
    statement: str,
    tactic_sequence: List[str],
    timeout: int = 300
) -> str:
    """Generate Lean script with random tactic sequence."""

    # Use first_success tactic to try tactics in sequence
    # Format: first | tac1 | tac2 | ... | done
    # Each tactic attempts to close the goal; if it succeeds, done
    tactic_lines = '\n    | '.join(['first'] + tactic_sequence + ['sorry'])

    script = f"""-- H-M3 Random Mathlib Tactic Sampling
-- Problem: {problem_id}
-- Tactic budget: {len(tactic_sequence)}

set_option maxHeartbeats 0

theorem {problem_id}_test : {statement} := by
  {tactic_lines}
"""
    return script


def sample_with_goal_selection(
    problem_id: str,
    statement: str,
    budget: int,
    seed: int,
    sampler: TacticSampler
) -> Tuple[str, List[str]]:
    """
    Generate Lean script with random tactics.

    Note: Lean doesn't support dynamic goal selection in subprocess mode.
    We use tactic composition (<;>) to try all tactics sequentially.
    This is a simplified version that tests corpus frequency only.
    """
    tactics = sampler.sample_sequence(budget, seed)
    script = create_proof_search_script(problem_id, statement, tactics)
    return script, tactics
