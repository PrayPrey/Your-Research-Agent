"""
Phase1PPOTrainer - Extends h-e1 SimplifiedPPOTrainer with progress tracking and checkpoints
Task: A-2
Hypothesis: h-m1
"""

import torch
import os
import sys
from typing import Dict

# Ensure h-e1 is in sys.path BEFORE any imports
_h_e1_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../h-e1/code'))
if _h_e1_path not in sys.path:
    sys.path.insert(1, _h_e1_path)  # Insert after h-m1

# Now we can import from train.ppo_trainer  (will find h-e1's version)
import importlib
import importlib.util

# Direct file import to avoid package conflicts
_ppo_trainer_path = os.path.join(_h_e1_path, "train", "ppo_trainer.py")
spec = importlib.util.spec_from_file_location("h_e1_ppo_trainer", _ppo_trainer_path)
h_e1_ppo = importlib.util.module_from_spec(spec)
sys.modules['h_e1_ppo_trainer'] = h_e1_ppo
spec.loader.exec_module(h_e1_ppo)
SimplifiedPPOTrainer = h_e1_ppo.SimplifiedPPOTrainer

# Import Phase 1 components from h-m1
from utils.checkpoint_logger import CheckpointLogger


class Phase1PPOTrainer(SimplifiedPPOTrainer):
    """
    Extension of h-e1 SimplifiedPPOTrainer with Phase 1 progress tracking.

    Adds:
    - Training progress computation
    - Checkpoint evaluation at [0%, 10%, 20%, 30%, 70%, 100%]
    - Pass@1 tracking for Phase 1 analysis
    """

    def __init__(self, model_name: str, aggregator, feedback_collector, config: dict):
        """
        Args:
            model_name: HuggingFace model identifier
            aggregator: Phase1AnalysisTriModalAggregator instance
            feedback_collector: FeedbackCollector instance
            config: Training configuration
        """
        super().__init__(model_name, aggregator, feedback_collector, config)

        # Phase 1 checkpoint configuration
        self.checkpoint_milestones = [0.0, 0.1, 0.2, 0.3, 0.7, 1.0]

        # Checkpoint logger
        checkpoint_dir = config.get('checkpoint_dir', './checkpoints')
        self.checkpoint_logger = CheckpointLogger(checkpoint_dir)

        # Track checkpoints triggered
        self.triggered_checkpoints = set()

    def compute_training_progress(self, current_episode: int, total_episodes: int) -> float:
        """
        Compute training progress as fraction complete.

        Args:
            current_episode: Current episode number
            total_episodes: Total episodes to train

        Returns:
            progress: float in [0, 1]
        """
        return current_episode / total_episodes

    def evaluate_checkpoint(self, dataloader) -> float:
        """
        Evaluate pass@1 on validation set.

        Args:
            dataloader: Validation data loader

        Returns:
            pass_at_1: Pass@1 score
        """
        # Use evaluator from base class
        if hasattr(self, 'evaluator'):
            metrics = self.evaluator.evaluate(self.model, dataloader)
            return metrics.get('pass_at_1', 0.0)
        else:
            # Fallback: simple pass rate
            correct = 0
            total = 0

            self.model.eval()
            with torch.no_grad():
                for batch in dataloader:
                    # Generate code and test
                    outputs = self.model.generate(
                        batch['input_ids'],
                        max_length=512,
                        num_return_sequences=1
                    )

                    # Check correctness (simplified)
                    for i, output in enumerate(outputs):
                        code = self.tokenizer.decode(output, skip_special_tokens=True)
                        test_cases = batch.get('test_cases', [[]])[i]

                        # Collect execution feedback
                        feedback = self.feedback_collector.collect_execution_feedback(code, test_cases)

                        if feedback > 0.5:  # Passed
                            correct += 1
                        total += 1

                    if total >= 100:  # Limit evaluation size
                        break

            self.model.train()
            return correct / total if total > 0 else 0.0

    def train(self, train_dataloader, val_dataloader=None, total_episodes: int = 10000) -> dict:
        """
        Training loop with Phase 1 checkpoint logging.

        Args:
            train_dataloader: Training data loader
            val_dataloader: Validation data loader
            total_episodes: Total episodes to train

        Returns:
            training_history: Dict with metrics
        """
        print(f"🚀 Starting Phase 1 PPO Training ({total_episodes} episodes)")
        print(f"📊 Checkpoints at: {[f'{m:.0%}' for m in self.checkpoint_milestones]}")

        for episode in range(total_episodes):
            # Compute progress
            progress = self.compute_training_progress(episode, total_episodes)

            # Check if checkpoint milestone reached
            for milestone in self.checkpoint_milestones:
                if abs(progress - milestone) < (1 / total_episodes) and milestone not in self.triggered_checkpoints:
                    print(f"\n{'=' * 60}")
                    print(f"📍 CHECKPOINT @ {milestone:.0%} progress (episode {episode}/{total_episodes})")
                    print(f"{'=' * 60}")

                    # Evaluate pass@1
                    if val_dataloader:
                        pass_at_1 = self.evaluate_checkpoint(val_dataloader)
                        print(f"✓ Pass@1: {pass_at_1:.3f}")

                        # Log to checkpoint logger
                        self.checkpoint_logger.log_pass_at_1(milestone, pass_at_1)

                    # Get current weights from aggregator
                    exec_w, ai_w, human_w = self.aggregator.compute_weights(torch.tensor(progress))

                    # Log weights
                    self.checkpoint_logger.log_weights(
                        progress=milestone,
                        exec_w=exec_w.item(),
                        ai_w=ai_w.item(),
                        human_w=human_w.item()
                    )

                    # Save full checkpoint
                    checkpoint_data = {
                        'episode': episode,
                        'execution_weight': exec_w.item(),
                        'ai_weight': ai_w.item(),
                        'human_weight': human_w.item(),
                        'pass_at_1': pass_at_1 if val_dataloader else None
                    }

                    self.checkpoint_logger.save_full_checkpoint(milestone, checkpoint_data)

                    # Save model checkpoint
                    checkpoint_path = os.path.join(
                        self.checkpoint_logger.checkpoint_dir,
                        f"model_progress_{int(milestone * 100):03d}.pt"
                    )
                    torch.save({
                        'episode': episode,
                        'model_state_dict': self.model.state_dict(),
                        'optimizer_state_dict': self.optimizer.state_dict(),
                        'progress': milestone
                    }, checkpoint_path)

                    print(f"{'=' * 60}\n")

                    self.triggered_checkpoints.add(milestone)

            # Regular training step (use base class implementation)
            batch = next(iter(train_dataloader))
            self.train_step(batch, progress)

        print("✅ Phase 1 Training Complete!")

        return {'checkpoints_triggered': len(self.triggered_checkpoints)}
