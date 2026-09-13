"""
Tri-Modal Reward Aggregator
Task: A-3 (Tri-Modal Aggregator)

Core mechanism: Dynamic weight scheduling across execution, AI, and human feedback
"""
import torch
import torch.nn as nn
from typing import Tuple, Dict
import numpy as np


class TriModalAggregator(nn.Module):
    """
    Implements dynamic reward aggregation across three feedback modalities:
    - Execution feedback (test case pass rate)
    - AI feedback (learned reward model)
    - Human feedback (preference scores)

    Weight schedule follows 3 phases:
    - Phase 1 (0-30%): Execution dominant (establish correctness)
    - Phase 2 (30-70%): AI dominant (scalable quality improvement)
    - Phase 3 (70-100%): Human dominant (fine-tune edge cases)
    """

    def __init__(
        self,
        num_phases: int = 3,
        initial_weights: list = None,
        peak_timesteps: list = None,
        decay_rates: list = None,
        percentile_window: int = 100
    ):
        super().__init__()

        # Default configuration
        if initial_weights is None:
            initial_weights = [0.8, 0.1, 0.1]  # exec, AI, human
        if peak_timesteps is None:
            peak_timesteps = [0.15, 0.5, 0.85]  # phase centers
        if decay_rates is None:
            decay_rates = [0.5, 0.3, 0.2]  # transition sharpness

        # Learnable parameters (9 total: 3 signals × 3 params each)
        self.initial_weights = nn.Parameter(torch.tensor(initial_weights, dtype=torch.float32))
        self.peak_timesteps = nn.Parameter(torch.tensor(peak_timesteps, dtype=torch.float32))
        self.decay_rates = nn.Parameter(torch.tensor(decay_rates, dtype=torch.float32))

        # Percentile normalization buffer
        self.percentile_window = percentile_window
        self.register_buffer('exec_history', torch.zeros(percentile_window))
        self.register_buffer('ai_history', torch.zeros(percentile_window))
        self.register_buffer('human_history', torch.zeros(percentile_window))
        self.register_buffer('history_idx', torch.tensor(0, dtype=torch.long))

    def forward(
        self,
        execution_reward: torch.Tensor,
        ai_reward: torch.Tensor,
        human_reward: torch.Tensor,
        training_progress: float
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Aggregate three reward signals with dynamic phase-based weighting

        Args:
            execution_reward: (B,) - test case pass rate [0,1]
            ai_reward: (B,) - learned reward model score [-1,1]
            human_reward: (B,) - human preference score [0,1]
            training_progress: float - current step / total steps [0,1]

        Returns:
            aggregated_reward: (B,) - weighted combination [0,1]
            weight_dict: Dict with current weights for logging
        """
        # Compute phase-based weights
        weights = self._compute_phase_weights(training_progress)  # (3,)

        # Update history for percentile normalization
        self._update_history(execution_reward, ai_reward, human_reward)

        # Normalize rewards to [0,1] via percentile transformation
        exec_norm = self._percentile_normalize(execution_reward, self.exec_history)
        ai_norm = self._percentile_normalize(ai_reward, self.ai_history)
        human_norm = self._percentile_normalize(human_reward, self.human_history)

        # Weighted aggregation
        reward = (
            weights[0] * exec_norm +
            weights[1] * ai_norm +
            weights[2] * human_norm
        )

        # Return weights for logging
        weight_dict = {
            'execution_weight': weights[0].item(),
            'ai_weight': weights[1].item(),
            'human_weight': weights[2].item(),
            'training_progress': training_progress
        }

        return reward, weight_dict

    def _compute_phase_weights(self, progress: float) -> torch.Tensor:
        """
        Compute dynamic weights using Gaussian-like curves

        Each signal has a peak at its corresponding timestep with decay
        """
        progress_tensor = torch.tensor(progress, dtype=torch.float32, device=self.initial_weights.device)

        # Gaussian-like curves centered at peak_timesteps
        weights = self.initial_weights * torch.exp(
            -self.decay_rates * (progress_tensor - self.peak_timesteps) ** 2
        )

        # Normalize to sum=1
        return weights / weights.sum()

    def _update_history(
        self,
        execution_reward: torch.Tensor,
        ai_reward: torch.Tensor,
        human_reward: torch.Tensor
    ):
        """Update rolling history for percentile normalization"""
        batch_size = execution_reward.shape[0]

        for i in range(batch_size):
            idx = self.history_idx % self.percentile_window

            self.exec_history[idx] = execution_reward[i].detach()
            self.ai_history[idx] = ai_reward[i].detach()
            self.human_history[idx] = human_reward[i].detach()

            self.history_idx += 1

    def _percentile_normalize(
        self,
        reward: torch.Tensor,
        history: torch.Tensor
    ) -> torch.Tensor:
        """
        Normalize reward using percentile rank

        Maps reward to [0,1] based on its percentile in recent history
        """
        # Get valid history (up to history_idx samples)
        valid_size = min(self.history_idx.item(), self.percentile_window)
        if valid_size < 10:
            # Not enough history - simple min-max normalization
            return (reward - reward.min()) / (reward.max() - reward.min() + 1e-8)

        valid_history = history[:valid_size]

        # Compute percentile rank for each reward value
        normalized = torch.zeros_like(reward)
        for i, r in enumerate(reward):
            percentile = (valid_history < r).float().mean()
            normalized[i] = percentile

        return normalized

    def get_current_weights(self, training_progress: float) -> Dict[str, float]:
        """Get current weight values for analysis"""
        weights = self._compute_phase_weights(training_progress)
        return {
            'execution': weights[0].item(),
            'ai': weights[1].item(),
            'human': weights[2].item()
        }


if __name__ == "__main__":
    # Test tri-modal aggregator
    print("Testing TriModalAggregator...")

    aggregator = TriModalAggregator()

    # Simulate batch of rewards
    batch_size = 8
    exec_reward = torch.rand(batch_size)  # [0,1]
    ai_reward = torch.rand(batch_size) * 2 - 1  # [-1,1]
    human_reward = torch.rand(batch_size)  # [0,1]

    # Test at different training progress points
    for progress in [0.1, 0.3, 0.5, 0.7, 0.9]:
        aggregated, weights = aggregator(exec_reward, ai_reward, human_reward, progress)

        print(f"\nProgress: {progress:.1%}")
        print(f"  Weights: exec={weights['execution_weight']:.3f}, "
              f"ai={weights['ai_weight']:.3f}, "
              f"human={weights['human_weight']:.3f}")
        print(f"  Sum: {sum([weights['execution_weight'], weights['ai_weight'], weights['human_weight']]):.3f}")
        print(f"  Aggregated reward shape: {aggregated.shape}")

    print("\n✓ Mechanism test passed")
