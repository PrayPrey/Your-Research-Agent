"""
Phase1AnalysisTriModalAggregator - Extends h-e1 TriModalAggregator with Phase 1 checkpoint logging
Task: A-1
Hypothesis: h-m1
"""

import torch
import torch.nn as nn
from typing import Tuple, Dict
import sys
import os

# Import h-e1 base class
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../h-e1/code'))
from models.tri_modal_aggregator import TriModalAggregator


class Phase1AnalysisTriModalAggregator(TriModalAggregator):
    """
    Extension of h-e1 TriModalAggregator with Phase 1 checkpoint logging.

    Tests H-M1: Execution weight should be highest in 0-30% training progress.

    New functionality:
    - Phase 1 checkpoint logging at [0%, 10%, 20%, 30%]
    - Weight trajectory tracking for gate validation
    """

    def __init__(self, config: dict = None, phase1_checkpoints: list = None):
        """
        Args:
            config: Configuration dict (passed to base class)
            phase1_checkpoints: Progress points to log (default: [0.0, 0.1, 0.2, 0.3])
        """
        super().__init__(config or {})

        # Phase 1 checkpoints for hypothesis validation
        self.phase1_checkpoints = phase1_checkpoints or [0.0, 0.1, 0.2, 0.3]

        # Storage for checkpoint data (used by Phase1Analyzer)
        self.checkpoint_data = []

    def log_phase1_checkpoint(self, progress: float, exec_w: float, ai_w: float, human_w: float):
        """
        Log checkpoint data for Phase 1 analysis.

        Args:
            progress: Training progress in [0, 1]
            exec_w: Execution feedback weight
            ai_w: AI feedback weight
            human_w: Human feedback weight
        """
        checkpoint = {
            'progress': progress,
            'execution_weight': exec_w,
            'ai_weight': ai_w,
            'human_weight': human_w,
            'timestamp': torch.cuda.Event(enable_timing=True) if torch.cuda.is_available() else None
        }

        self.checkpoint_data.append(checkpoint)

        print(f"📊 Phase 1 Checkpoint @ {progress:.1%}:")
        print(f"  ⚡ Execution: {exec_w:.3f}")
        print(f"  🤖 AI: {ai_w:.3f}")
        print(f"  👤 Human: {human_w:.3f}")
        print(f"  ✓ Sum: {exec_w + ai_w + human_w:.3f}")

    def forward(self, execution_reward: torch.Tensor,
                ai_reward: torch.Tensor,
                human_reward: torch.Tensor,
                training_progress: float) -> torch.Tensor:
        """
        Forward pass with Phase 1 checkpoint logging.

        Args:
            execution_reward: (B,) tensor of execution feedback scores
            ai_reward: (B,) tensor of AI reward model scores
            human_reward: (B,) tensor of human preference scores
            training_progress: float in [0, 1] - current training progress

        Returns:
            aggregated_reward: (B,) tensor of weighted combination
        """
        # Get base class aggregation
        aggregated = super().forward(execution_reward, ai_reward, human_reward, training_progress)

        # Log Phase 1 checkpoints
        if any(abs(training_progress - cp) < 0.01 for cp in self.phase1_checkpoints):
            exec_w, ai_w, human_w = self.compute_weights(training_progress)
            self.log_phase1_checkpoint(
                progress=training_progress,
                exec_w=exec_w.item(),
                ai_w=ai_w.item(),
                human_w=human_w.item()
            )

        return aggregated

    def get_checkpoint_data(self) -> list:
        """Return all logged checkpoint data for analysis."""
        return self.checkpoint_data
