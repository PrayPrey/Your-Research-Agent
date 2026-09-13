"""
Phase 2 Tri-Modal Aggregator with AI Feedback Peak Scheduling
Extends h-m1 Phase1TriModalAggregator for Phase 2 (30-70% progress)
"""

import torch
import torch.nn as nn
from torch import Tensor
from typing import Dict, Tuple
import numpy as np

# Import h-m1 base class
from models.phase1_tri_modal_aggregator import Phase1AnalysisTriModalAggregator


class Phase2TriModalAggregator(Phase1AnalysisTriModalAggregator):
    """
    Phase 2 Tri-Modal Aggregator with AI Peak Scheduling.

    Extends Phase 1 aggregator to Phase 2 training range (30-70% progress).
    Implements Gaussian AI weight peak at ~50% progress.
    """

    def __init__(
        self,
        config: dict = None,
        phase2_checkpoints: list = None,
        ai_peak_progress: float = 0.50
    ):
        """
        Initialize Phase 2 aggregator.

        Args:
            config: Configuration dict (reuse from h-m1)
            phase2_checkpoints: Checkpoint progress points [0.30, 0.40, 0.50, 0.60, 0.70]
            ai_peak_progress: Progress value for AI weight peak (default 0.50)
        """
        # Initialize parent with Phase 2 checkpoints
        super().__init__(
            config,
            phase1_checkpoints=phase2_checkpoints or [0.30, 0.40, 0.50, 0.60, 0.70]
        )

        self.phase2_start = 0.30
        self.phase2_end = 0.70
        self.ai_peak_progress = ai_peak_progress
        self.phase2_weight_log = []  # Track weights for analysis

    def compute_dynamic_weights(self, training_progress: float) -> Dict[str, float]:
        """
        Compute Phase 2 weights with AI peak at ~50%.

        Weight schedule:
        - Execution: Decays from 0.50 → 0.20 (linear)
        - AI: Gaussian peak at 0.50 progress (max ~0.60)
        - Human: Increases from 0.10 → 0.20 (linear)

        Args:
            training_progress: Training progress in [0,1]

        Returns:
            Dict with keys 'execution', 'ai', 'human' (normalized to sum=1.0)
        """
        # Clip to Phase 2 range
        progress = max(self.phase2_start, min(training_progress, self.phase2_end))

        # Normalize to [0,1] within Phase 2
        phase2_progress = (progress - self.phase2_start) / (self.phase2_end - self.phase2_start)

        # Execution weight: Linear decay 0.50 → 0.20
        exec_weight = 0.50 - 0.30 * phase2_progress

        # AI weight: Gaussian peak centered at 0.50 (50% of Phase 2)
        # Peak height: ~0.60, width controlled by variance
        variance = 0.05
        ai_weight = 0.60 * np.exp(-((phase2_progress - 0.5) ** 2) / (2 * variance))
        ai_weight = max(0.10, ai_weight)  # Floor at 0.10

        # Human weight: Linear increase 0.10 → 0.20
        human_weight = 0.10 + 0.10 * phase2_progress

        # Normalize to sum = 1.0
        total = exec_weight + ai_weight + human_weight
        weights = {
            'execution': exec_weight / total,
            'ai': ai_weight / total,
            'human': human_weight / total
        }

        return weights

    def forward(
        self,
        execution_reward: Tensor,
        ai_reward: Tensor,
        human_reward: Tensor,
        training_progress: float
    ) -> Tensor:
        """
        Forward pass with Phase 2 AI peak scheduling.

        Args:
            execution_reward: Execution feedback rewards [B]
            ai_reward: AI feedback rewards [B]
            human_reward: Human feedback rewards [B]
            training_progress: Current training progress [0,1]

        Returns:
            Aggregated reward [B]
        """
        # Compute dynamic weights for Phase 2
        weights = self.compute_dynamic_weights(training_progress)

        # Aggregate rewards with dynamic weights
        aggregated = (
            weights['execution'] * execution_reward +
            weights['ai'] * ai_reward +
            weights['human'] * human_reward
        )

        # Log weights at checkpoints
        if any(abs(training_progress - cp) < 0.001 for cp in self.checkpoints):
            self.phase2_weight_log.append({
                'progress': training_progress,
                'weights': weights.copy()
            })

        return aggregated

    def find_ai_weight_peak(self) -> Tuple[float, Dict[str, float]]:
        """
        Find AI weight peak location in Phase 2.

        Returns:
            Tuple of (peak_progress, weights_at_peak)
        """
        if not self.phase2_weight_log:
            # Compute theoretical peak
            peak_progress = self.ai_peak_progress
            weights = self.compute_dynamic_weights(peak_progress)
            return peak_progress, weights

        # Find actual peak from logged weights
        max_ai_weight = 0.0
        peak_entry = None

        for entry in self.phase2_weight_log:
            ai_w = entry['weights']['ai']
            if ai_w > max_ai_weight:
                max_ai_weight = ai_w
                peak_entry = entry

        if peak_entry:
            return peak_entry['progress'], peak_entry['weights']
        else:
            return self.ai_peak_progress, self.compute_dynamic_weights(self.ai_peak_progress)

    def log_phase2_checkpoint(self, progress: float, weights: Dict[str, float]):
        """Log checkpoint data for Phase 2 analysis."""
        self.phase2_weight_log.append({
            'progress': progress,
            'weights': weights.copy()
        })
