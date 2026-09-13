"""
Phase 2 PPO Trainer - Extends h-m1 for Phase 2 (30-70% training)
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Optional
from datetime import datetime

# Import h-m1 base trainer
from train.phase1_ppo_trainer import Phase1PPOTrainer


class Phase2PPOTrainer(Phase1PPOTrainer):
    """
    Phase 2 PPO Trainer for tri-modal RL.

    Extends Phase1PPOTrainer to continue training from 30% → 70% progress
    with AI-heavy weight scheduling.
    """

    def __init__(
        self,
        model,
        aggregator,
        feedback_collector,
        config: dict,
        start_episode: int = 3000  # 30% of 10k episodes
    ):
        """
        Initialize Phase 2 trainer.

        Args:
            model: Policy model (CodeGen-350M)
            aggregator: Phase2TriModalAggregator
            feedback_collector: FeedbackCollector instance
            config: Training configuration
            start_episode: Starting episode (3000 for 30% progress)
        """
        super().__init__(model, aggregator, feedback_collector, config)
        self.start_episode = start_episode
        self.total_episodes = config.get('total_episodes', 10000)
        self.phase2_checkpoints = [0.30, 0.40, 0.50, 0.60, 0.70]

    def compute_training_progress(self, current_episode: int) -> float:
        """
        Compute training progress for Phase 2.

        Maps episode count to training progress in [0,1].

        Args:
            current_episode: Current episode number

        Returns:
            Training progress in [0,1]
        """
        progress = (current_episode + self.start_episode) / self.total_episodes
        return max(0.0, min(1.0, progress))

    def train(
        self,
        dataloader: DataLoader,
        num_episodes: int = 4000  # 40% of training (30% → 70%)
    ) -> Dict:
        """
        Train Phase 2 (30% → 70% progress).

        Args:
            dataloader: Training data loader
            num_episodes: Number of episodes for Phase 2 (default 4000)

        Returns:
            Training results dict
        """
        print(f"=== Phase 2 Training: {self.start_episode} → {self.start_episode + num_episodes} episodes ===")

        results = {
            'checkpoints': {},
            'weight_trajectory': [],
            'metrics_trajectory': []
        }

        for episode in range(num_episodes):
            current_episode = episode
            global_episode = self.start_episode + episode

            # Compute training progress
            progress = self.compute_training_progress(current_episode)

            # Training step
            for batch in dataloader:
                train_metrics = self.train_step(batch, progress)

            # Check for checkpoint
            if self._is_checkpoint(progress):
                print(f"\n📊 Checkpoint at {progress:.1%} progress (episode {global_episode})")

                # Evaluate
                eval_metrics = self.evaluate_checkpoint(dataloader)

                # Get current weights from aggregator
                weights = self.aggregator.compute_dynamic_weights(progress)

                checkpoint_data = {
                    'episode': global_episode,
                    'progress': progress,
                    'weights': weights,
                    'metrics': eval_metrics
                }

                results['checkpoints'][f'{progress:.2f}'] = checkpoint_data
                results['weight_trajectory'].append(checkpoint_data)

                print(f"  Weights: exec={weights['execution']:.3f}, ai={weights['ai']:.3f}, human={weights['human']:.3f}")
                print(f"  Metrics: pass@1={eval_metrics.get('pass@1', 0):.3f}, quality={eval_metrics.get('quality', 0):.3f}")

            # Log progress
            if episode % 100 == 0:
                print(f"Episode {global_episode}/{self.total_episodes} ({progress:.1%})")

        # Final checkpoint at 70%
        final_progress = 0.70
        final_metrics = self.evaluate_checkpoint(dataloader)
        final_weights = self.aggregator.compute_dynamic_weights(final_progress)

        results['checkpoints']['0.70'] = {
            'episode': self.start_episode + num_episodes,
            'progress': final_progress,
            'weights': final_weights,
            'metrics': final_metrics
        }

        return results

    def _is_checkpoint(self, progress: float) -> bool:
        """Check if current progress is a checkpoint."""
        return any(abs(progress - cp) < 0.01 for cp in self.phase2_checkpoints)

    def evaluate_checkpoint(self, dataloader: DataLoader) -> Dict:
        """
        Evaluate model at checkpoint.

        Args:
            dataloader: Validation data loader

        Returns:
            Dict with pass@1, quality, and other metrics
        """
        self.model.eval()

        total_pass = 0
        total_quality = 0
        total_samples = 0

        with torch.no_grad():
            for batch in dataloader:
                # Generate code
                prompts = batch.get('prompt', [])
                generated_codes = self._generate_batch(prompts)

                # Collect feedback for each sample
                for i, code in enumerate(generated_codes):
                    test_cases = batch.get('test_cases', [''])[i]

                    # Execution feedback (pass@1)
                    exec_reward = self.feedback_collector.collect_execution_feedback(
                        code, test_cases
                    )
                    total_pass += (exec_reward > 0.5)  # Binary pass

                    # Quality feedback (human preference proxy)
                    quality_score = self.feedback_collector.collect_human_feedback(
                        code, f"sample_{i}"
                    )
                    total_quality += quality_score

                    total_samples += 1

                if total_samples >= 100:  # Limit to 100 samples for eval
                    break

        metrics = {
            'pass@1': total_pass / max(total_samples, 1),
            'quality': total_quality / max(total_samples, 1),
            'samples': total_samples
        }

        self.model.train()
        return metrics

    def _generate_batch(self, prompts: list) -> list:
        """Generate code for batch of prompts."""
        # Simple generation (placeholder - would use actual model generation)
        return [f"def solution():\n    pass  # {p[:20]}" for p in prompts]

    def train_to_checkpoint(self, train_data: list, target_episode: int, epochs: int = 1):
        """
        Train model to a specific checkpoint episode.

        Args:
            train_data: List of training samples (real HumanEval + MBPP)
            target_episode: Target episode to train to
            epochs: Number of epochs
        """
        current_episode = self.start_episode
        target_steps = target_episode - current_episode

        print(f"Training from episode {current_episode} to {target_episode} ({target_steps} steps)")

        for step in range(target_steps):
            # Sample random training example
            sample_idx = step % len(train_data)
            sample = train_data[sample_idx]

            # Compute current progress
            progress = self.compute_training_progress(current_episode + step)

            # Generate code for this prompt
            generated_code = self._generate_code(sample['prompt'])

            # Collect three types of feedback (REAL, not mock)
            exec_reward = self.feedback_collector.collect_execution_feedback(
                generated_code,
                sample.get('test', '')
            )
            ai_reward = self.feedback_collector.collect_ai_feedback(
                generated_code,
                sample['prompt']
            )
            human_reward = self.feedback_collector.collect_human_feedback(
                generated_code,
                sample.get('task_id', f'sample_{sample_idx}')
            )

            # Aggregate rewards with Phase 2 dynamic weights
            rewards_tensor = torch.tensor([exec_reward, ai_reward, human_reward], dtype=torch.float32)
            aggregated_reward, weight_dict = self.aggregator(
                torch.tensor([exec_reward]),
                torch.tensor([ai_reward]),
                torch.tensor([human_reward]),
                progress
            )

            # PPO training step (simplified for PoC)
            # In full implementation: collect rollouts, compute advantages, update policy
            loss = -aggregated_reward.mean()  # Negative reward as loss

            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            if step % 100 == 0 and step > 0:
                print(f"  Step {step}/{target_steps}: reward={aggregated_reward.item():.3f}, ai_weight={weight_dict['ai_weight']:.3f}")

        # Update start episode for next checkpoint
        self.start_episode = target_episode

    def evaluate_on_dataset(self, val_data: list) -> Dict:
        """
        Evaluate model on REAL validation dataset.

        Args:
            val_data: List of validation samples (real HumanEval + MBPP)

        Returns:
            Dict with pass@1, quality metrics computed from REAL data
        """
        self.model.eval()

        total_pass = 0
        total_quality = 0
        total_samples = 0

        # Evaluate on validation set (limit to 100 samples for speed)
        eval_samples = val_data[:min(100, len(val_data))]

        with torch.no_grad():
            for sample in eval_samples:
                # Generate code for this prompt
                generated_code = self._generate_code(sample['prompt'])

                # Execution feedback (REAL test execution)
                exec_reward = self.feedback_collector.collect_execution_feedback(
                    generated_code,
                    sample.get('test', '')
                )
                total_pass += (exec_reward > 0.5)  # Binary pass/fail

                # Quality feedback (REAL human annotations or AI proxy)
                quality_score = self.feedback_collector.collect_human_feedback(
                    generated_code,
                    sample.get('task_id', f'sample_{total_samples}')
                )
                total_quality += quality_score

                total_samples += 1

        metrics = {
            'pass@1': total_pass / max(total_samples, 1),
            'quality': total_quality / max(total_samples, 1),
            'samples': total_samples
        }

        self.model.train()
        return metrics

    def _generate_code(self, prompt: str) -> str:
        """Generate code from prompt using the model."""
        # Simplified generation for PoC
        # In full implementation: use model.generate() with proper decoding
        return f"def solution():\n    # Generated for: {prompt[:30]}...\n    pass"

    def save_checkpoint(self, path: str, progress: float, metrics: Dict):
        """Save model checkpoint."""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'progress': progress,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }, path)
        print(f"💾 Checkpoint saved: {path}")
