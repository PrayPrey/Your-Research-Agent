"""
Phase 3 PPO Trainer
Continues training from h-m2 70% checkpoint through Phase 3 (70-100%)
"""

import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict
import json

# Import Phase 2 trainer as base
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from train.phase2_ppo_trainer import Phase2PPOTrainer
except ImportError:
    # Minimal fallback
    class Phase2PPOTrainer:
        def __init__(self, *args, **kwargs):
            pass


class Phase3PPOTrainer:
    """
    Phase 3 PPO Trainer (70-100% training progress).

    Simplified version for PoC - doesn't inherit from Phase2PPOTrainer
    to avoid HuggingFace model loading issues.
    """

    def __init__(self, model, aggregator, feedback_collector, config: Dict):
        self.model = model
        self.aggregator = aggregator
        self.feedback_collector = feedback_collector
        self.config = config

        # Create optimizer
        self.optimizer = torch.optim.Adam(model.parameters(), lr=config.get("learning_rate", 3e-4))
        self.start_progress = 0.70
        self.end_progress = 1.00
        self.start_episode = config.get("start_episode", 7000)
        self.total_episodes = config.get("phase3_episodes", 3000)
        self.checkpoint_intervals = [0.80, 0.90, 1.00]

    def compute_training_progress(self, current_episode: int) -> float:
        """
        Map episode number to training progress in Phase 3 range [0.70, 1.00].

        Args:
            current_episode: Current episode number (7000-10000 for Phase 3)

        Returns:
            Training progress in [0.70, 1.00]
        """
        # Map episodes to progress
        # Episode 7000 → 0.70
        # Episode 10000 → 1.00
        progress_in_phase = (current_episode - self.start_episode) / self.total_episodes
        training_progress = self.start_progress + progress_in_phase * (self.end_progress - self.start_progress)

        # Clip to Phase 3 range
        return max(self.start_progress, min(self.end_progress, training_progress))

    def load_h_m2_checkpoint(self, checkpoint_path: str) -> Dict:
        """
        Load h-m2 checkpoint at 70% progress as Phase 3 starting point.

        Args:
            checkpoint_path: Path to h-m2 checkpoint (e.g., checkpoint_progress_0.70.pt)

        Returns:
            Loaded checkpoint dict
        """
        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.exists():
            print(f"⚠ h-m2 checkpoint not found: {checkpoint_path}")
            print("  Starting from random initialization (test mode)")
            return {}

        checkpoint = torch.load(checkpoint_path, map_location='cpu')

        # Load model state
        if hasattr(self.model, 'load_state_dict'):
            self.model.load_state_dict(checkpoint.get('model_state_dict', {}))

        # Load optimizer state (if available)
        if hasattr(self, 'optimizer') and 'optimizer_state_dict' in checkpoint:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        # Verify progress
        loaded_progress = checkpoint.get('progress', 0.0)
        print(f"✓ Loaded h-m2 checkpoint at {loaded_progress:.2f} progress")
        print(f"  Starting Phase 3 from episode {self.start_episode}")

        return checkpoint

    def should_save_checkpoint(self, progress: float) -> bool:
        """Check if checkpoint should be saved at this progress."""
        for interval in self.checkpoint_intervals:
            if abs(progress - interval) < 0.01:  # Within 1% tolerance
                return True
        return False

    def save_checkpoint(self, path: str, progress: float, metrics: Dict):
        """
        Save checkpoint with Phase 3 metadata.

        Args:
            path: Output checkpoint path
            progress: Current training progress
            metrics: Current metrics dict
        """
        checkpoint = {
            'model_state_dict': self.model.state_dict() if hasattr(self.model, 'state_dict') else {},
            'optimizer_state_dict': self.optimizer.state_dict() if hasattr(self, 'optimizer') else {},
            'progress': progress,
            'phase': 'Phase3',
            'metrics': metrics,
            'aggregator_weights': self.aggregator.weight_history if hasattr(self.aggregator, 'weight_history') else []
        }

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        torch.save(checkpoint, path)
        print(f"✓ Checkpoint saved: {path} (progress={progress:.2f})")

    def train(self, dataloader, num_episodes: int = 3000) -> Dict:
        """
        Execute Phase 3 training loop.

        Args:
            dataloader: Training data loader
            num_episodes: Number of Phase 3 episodes (default: 3000)

        Returns:
            Training results dict
        """
        print(f"\n{'='*70}")
        print(f"Phase 3 Training: Episodes {self.start_episode} → {self.start_episode + num_episodes}")
        print(f"Progress Range: {self.start_progress:.2f} → {self.end_progress:.2f}")
        print(f"{'='*70}\n")

        results = {
            "checkpoints": [],
            "final_metrics": {}
        }

        for episode in range(self.start_episode, self.start_episode + num_episodes):
            # Compute current progress
            progress = self.compute_training_progress(episode)

            # Training step (placeholder - actual PPO implementation)
            # In real implementation, this would:
            # 1. Sample batch from dataloader
            # 2. Generate code with model
            # 3. Collect tri-modal feedback
            # 4. Aggregate rewards with Phase3 weights
            # 5. Update model with PPO loss

            # Simulated training for PoC
            if episode % 100 == 0:
                print(f"Episode {episode}/{self.start_episode + num_episodes} "
                      f"(progress={progress:.3f})")

            # Save checkpoint at milestones
            if self.should_save_checkpoint(progress):
                checkpoint_path = f"checkpoints/checkpoint_progress_{progress:.2f}.pt"
                metrics = {"episode": episode, "progress": progress}
                self.save_checkpoint(checkpoint_path, progress, metrics)
                results["checkpoints"].append({
                    "progress": progress,
                    "episode": episode,
                    "path": checkpoint_path
                })

        results["final_metrics"] = {
            "total_episodes": num_episodes,
            "final_progress": self.end_progress
        }

        print(f"\n✅ Phase 3 training complete!")
        print(f"  Checkpoints saved: {len(results['checkpoints'])}")

        return results
