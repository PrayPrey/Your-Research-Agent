"""
Phase 3 Tri-Modal Reward Aggregator
Extension of Phase2TriModalAggregator for Phase 3 (70-100% training progress)

Key Changes from Phase 2:
- Human feedback weight increases from 0.40 (70%) to 0.70 (100%)
- Execution weight decays from 0.40 to ~0.20
- AI weight maintains mid-level support (~0.20-0.30)
"""

import torch
import torch.nn as nn
from typing import Dict, Tuple
import json
from pathlib import Path

# Import Phase 2 aggregator as base
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from models.phase2_tri_modal_aggregator import Phase2TriModalAggregator
except ImportError:
    # Fallback if import fails - define minimal base
    class Phase2TriModalAggregator(nn.Module):
        def __init__(self, config=None):
            super().__init__()
            self.config = config or {}

        def compute_dynamic_weights(self, training_progress: float) -> Dict[str, float]:
            # Phase 2 default (not used in Phase 3)
            return {"execution": 0.33, "ai": 0.33, "human": 0.34}


class Phase3TriModalAggregator(Phase2TriModalAggregator):
    """
    Phase 3 (70-100%): Human feedback weight increases to correct AI biases
    and improve edge case quality.

    Gate Criterion 1: Human weight at 100% > Human weight at 70%
    """

    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.phase3_start = 0.70
        self.phase3_end = 1.00
        self.weight_history = []  # Track weights for gate validation

    def compute_dynamic_weights(self, training_progress: float) -> Dict[str, float]:
        """
        Compute Phase 3 weight schedule (70-100% progress).

        Human weight increases linearly from 0.40 to 0.70
        Execution weight decays from 0.40 to 0.20
        AI weight maintains mid-level (~0.20-0.30)

        Args:
            training_progress: float in [0.70, 1.00]

        Returns:
            dict with keys: execution, ai, human
        """
        # Clip to Phase 3 range
        progress = max(self.phase3_start, min(self.phase3_end, training_progress))

        # Normalize to [0, 1] within Phase 3
        t = (progress - self.phase3_start) / (self.phase3_end - self.phase3_start)

        # Phase 3 weight schedule
        w_execution = 0.400 - 0.200 * t  # 0.40 → 0.20 (linear decay)
        w_ai = 0.200 + 0.100 * (1 - abs(2*t - 1))  # ~0.20-0.30 (mild peak at mid-phase)
        w_human = 0.400 + 0.300 * t  # 0.40 → 0.70 (linear increase)

        # Normalize to sum=1.0
        total = w_execution + w_ai + w_human
        weights = {
            "execution": w_execution / total,
            "ai": w_ai / total,
            "human": w_human / total,
            "progress": progress
        }

        # Track for gate validation
        self.weight_history.append(weights.copy())

        return weights

    def forward(self, exec_reward: torch.Tensor, ai_reward: torch.Tensor,
                human_reward: torch.Tensor, training_progress: float) -> torch.Tensor:
        """
        Aggregate three reward signals with Phase 3 dynamic weights.

        Args:
            exec_reward: Execution feedback reward (pass@1)
            ai_reward: AI quality feedback reward
            human_reward: Human preference reward
            training_progress: Current training progress [0.70, 1.00]

        Returns:
            Aggregated reward tensor
        """
        weights = self.compute_dynamic_weights(training_progress)

        w_e = torch.tensor(weights["execution"], device=exec_reward.device)
        w_a = torch.tensor(weights["ai"], device=ai_reward.device)
        w_h = torch.tensor(weights["human"], device=human_reward.device)

        aggregated = w_e * exec_reward + w_a * ai_reward + w_h * human_reward

        return aggregated

    def validate_human_weight_increase(self) -> Tuple[bool, Dict]:
        """
        Gate Criterion 1: Verify human weight increases from 70% to 100%.

        Returns:
            (passed, details) tuple
        """
        if len(self.weight_history) < 2:
            return False, {"error": "Insufficient weight history"}

        # Get weights at 70% and 100% (first and last in Phase 3)
        w_70 = self.weight_history[0]["human"]
        w_100 = self.weight_history[-1]["human"]

        passed = w_100 > w_70

        details = {
            "w_human_70": round(w_70, 4),
            "w_human_100": round(w_100, 4),
            "increase": round(w_100 - w_70, 4),
            "passed": passed,
            "criterion": "w_human(100%) > w_human(70%)"
        }

        return passed, details

    def save_weight_history(self, output_path: str):
        """Save weight trajectory for analysis and visualization."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.weight_history, f, indent=2)

        print(f"✓ Weight history saved: {output_path}")
