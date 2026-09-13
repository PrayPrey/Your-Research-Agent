"""difficulty_reward_callback.py — H-M2: Live TRL callback for difficulty-stratified reward monitoring.

For future live-callback use when training with TRL >= 0.7.
H-M2 post-hoc analysis uses analyze_reward_fractions.py instead.
"""
from collections import defaultdict
from typing import Optional

import numpy as np
from transformers import TrainerCallback, TrainerControl, TrainerState


class DifficultyRewardCallback(TrainerCallback):
    """Live callback — use only if re-running training with TRL >= 0.7."""

    def __init__(self, difficulty_field: str = "difficulty") -> None:
        self.difficulty_field = difficulty_field
        self.bucket_indicators: dict[str, list[float]] = defaultdict(list)

    def on_step_end(
        self,
        args,
        state: TrainerState,
        control: TrainerControl,
        rewards: Optional[list[float]] = None,
        batch: Optional[dict] = None,
        **kwargs,
    ) -> None:
        """Accumulate reward>0 indicators per difficulty bucket."""
        if rewards is None or batch is None:
            return
        difficulties = batch.get(self.difficulty_field, [])
        for diff, r in zip(difficulties, rewards):
            self.bucket_indicators[diff].append(float(r > 0))

    def compute_fractions(self) -> dict[str, float]:
        """Return mean non-zero fraction per bucket; {} if no data."""
        return {
            k: float(np.mean(v)) if v else 0.0
            for k, v in self.bucket_indicators.items()
        }

    def log_summary(self) -> dict[str, float]:
        """Print and return fractions dict."""
        fracs = self.compute_fractions()
        for k, v in fracs.items():
            print(f"[H-M2] {k}: nonzero_fraction={v:.4f}")
        return fracs


def verify_trl_version() -> bool:
    """Return True if trl >= 0.7."""
    import trl
    from packaging.version import Version
    return Version(trl.__version__) >= Version("0.7")


def verify_mechanism_activated(
    callback: DifficultyRewardCallback,
) -> tuple[bool, dict]:
    """Check competition bucket > 0.10 and all 3 buckets present."""
    fracs = callback.compute_fractions()
    required_full = {"introductory", "interview", "competition"}
    required_short = {"intro", "interview", "competition"}
    all_present = required_full.issubset(fracs.keys()) or required_short.issubset(fracs.keys())
    comp_key = "competition"
    comp_frac = fracs.get(comp_key, 0.0)
    indicators = {
        "fractions": fracs,
        "all_buckets_present": all_present,
        "competition_fraction": comp_frac,
        "gate_passed": comp_frac > 0.10,
    }
    passed = all_present and comp_frac > 0.10
    return passed, indicators
