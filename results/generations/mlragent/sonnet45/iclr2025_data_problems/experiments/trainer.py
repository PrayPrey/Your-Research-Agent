"""
Multi-stage training framework.
"""

import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from typing import Dict, List, Tuple, Optional
from copy import deepcopy
import numpy as np
from tqdm import tqdm


class MultiStageTrainer:
    """Trainer for multi-stage foundation model training."""

    def __init__(self, model: nn.Module, config: dict, device: torch.device):
        self.model = model
        self.config = config
        self.device = device

        self.stage_checkpoints = {}
        self.training_history = {
            "pretraining": {"losses": [], "perplexities": []},
            "instruction_tuning": {"losses": [], "accuracies": []},
            "alignment": {"losses": [], "preference_accuracy": []}
        }

    def train_stage(self, stage: str, dataloader, stage_config: dict,
                   save_checkpoint: bool = True) -> Dict:
        """
        Train one stage.

        Args:
            stage: Stage name ('pretraining', 'instruction_tuning', 'alignment')
            dataloader: DataLoader for the stage
            stage_config: Configuration for this stage
            save_checkpoint: Whether to save checkpoint after training

        Returns:
            metrics: Dictionary of training metrics
        """
        print(f"\n{'='*50}")
        print(f"Training Stage: {stage}")
        print(f"{'='*50}")

        self.model.train()

        # Setup optimizer
        optimizer = AdamW(
            self.model.parameters(),
            lr=stage_config["learning_rate"],
            weight_decay=stage_config["weight_decay"]
        )

        # Learning rate scheduler
        total_steps = len(dataloader) * stage_config["num_epochs"]
        scheduler = CosineAnnealingLR(optimizer, T_max=total_steps)

        # Training loop
        epoch_losses = []

        for epoch in range(stage_config["num_epochs"]):
            epoch_loss = 0.0
            num_batches = 0

            pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{stage_config['num_epochs']}")

            for batch in pbar:
                optimizer.zero_grad()

                # Move to device
                batch = {k: v.to(self.device) for k, v in batch.items() if isinstance(v, torch.Tensor)}

                # Compute loss based on stage
                if stage == "alignment":
                    loss = self.model.compute_preference_loss(
                        batch["chosen"],
                        batch["rejected"]
                    )
                else:
                    loss = self.model.compute_loss(
                        batch["input_ids"],
                        batch["labels"]
                    )

                # Backward pass
                loss.backward()

                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)

                optimizer.step()
                scheduler.step()

                epoch_loss += loss.item()
                num_batches += 1

                pbar.set_postfix({"loss": loss.item()})

            # Average loss for epoch
            avg_loss = epoch_loss / num_batches
            epoch_losses.append(avg_loss)

            print(f"Epoch {epoch+1}/{stage_config['num_epochs']}, Loss: {avg_loss:.4f}")

            # Store in history
            self.training_history[stage]["losses"].append(avg_loss)

        # Save checkpoint
        if save_checkpoint:
            self.stage_checkpoints[stage] = deepcopy(self.model.state_dict())

        metrics = {
            "stage": stage,
            "final_loss": epoch_losses[-1],
            "losses": epoch_losses
        }

        return metrics

    def evaluate(self, test_dataloader, stage: str = "pretraining") -> Dict:
        """
        Evaluate model.

        Args:
            test_dataloader: Test data loader
            stage: Stage to evaluate (determines metric type)

        Returns:
            metrics: Dictionary of evaluation metrics
        """
        self.model.eval()

        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in test_dataloader:
                batch = {k: v.to(self.device) for k, v in batch.items() if isinstance(v, torch.Tensor)}

                if "chosen" in batch:
                    loss = self.model.compute_preference_loss(
                        batch["chosen"],
                        batch["rejected"]
                    )
                else:
                    loss = self.model.compute_loss(
                        batch["input_ids"],
                        batch["labels"]
                    )

                total_loss += loss.item()
                num_batches += 1

        avg_loss = total_loss / num_batches
        perplexity = np.exp(avg_loss)

        metrics = {
            "loss": avg_loss,
            "perplexity": perplexity
        }

        return metrics

    def load_checkpoint(self, stage: str):
        """Load model checkpoint from a specific stage."""
        if stage in self.stage_checkpoints:
            self.model.load_state_dict(self.stage_checkpoints[stage])
        else:
            print(f"Warning: No checkpoint found for stage {stage}")

    def get_checkpoint(self, stage: str) -> Optional[nn.Module]:
        """Get model checkpoint for a stage."""
        if stage in self.stage_checkpoints:
            model_copy = deepcopy(self.model)
            model_copy.load_state_dict(self.stage_checkpoints[stage])
            return model_copy
        return None

    def train_all_stages(self, dataloaders: Dict[str, torch.utils.data.DataLoader],
                        stage_configs: Dict[str, dict]) -> Dict:
        """
        Train all stages sequentially.

        Args:
            dataloaders: Dictionary of dataloaders for each stage
            stage_configs: Dictionary of configs for each stage

        Returns:
            all_metrics: Dictionary containing metrics for all stages
        """
        all_metrics = {}

        stages = ["pretraining", "instruction_tuning", "alignment"]

        for stage in stages:
            metrics = self.train_stage(
                stage=stage,
                dataloader=dataloaders[stage],
                stage_config=stage_configs[stage],
                save_checkpoint=True
            )

            all_metrics[stage] = metrics

            # Evaluate after each stage
            if "test" in dataloaders:
                eval_metrics = self.evaluate(dataloaders["test"], stage=stage)
                print(f"\nTest metrics after {stage}:")
                print(f"  Loss: {eval_metrics['loss']:.4f}")
                print(f"  Perplexity: {eval_metrics['perplexity']:.4f}")

                all_metrics[stage]["test_loss"] = eval_metrics["loss"]
                all_metrics[stage]["test_perplexity"] = eval_metrics["perplexity"]

        return all_metrics

    def compute_ground_truth_value(self, dataloader, test_dataloader,
                                   stage: str, stage_config: dict,
                                   num_samples: int = 50) -> np.ndarray:
        """
        Compute ground truth data value by leave-one-out.

        Args:
            dataloader: Training data loader
            test_dataloader: Test data loader
            stage: Stage name
            stage_config: Stage configuration
            num_samples: Number of samples to compute ground truth for

        Returns:
            ground_truth_values: Array of ground truth values
        """
        print(f"\nComputing ground truth values for {stage}...")

        # Get all training samples
        all_samples = []
        for batch in dataloader:
            for i in range(len(batch["sample_ids"])):
                sample = {k: v[i] for k, v in batch.items()}
                all_samples.append(sample)

        # Limit to num_samples
        all_samples = all_samples[:num_samples]

        # Baseline performance (with all data)
        baseline_checkpoint = self.stage_checkpoints.get(stage)
        if baseline_checkpoint:
            self.model.load_state_dict(baseline_checkpoint)

        baseline_metrics = self.evaluate(test_dataloader, stage)
        baseline_perf = -baseline_metrics["loss"]  # Negative loss as performance

        # Compute leave-one-out performance
        ground_truth_values = []

        for idx, sample in enumerate(tqdm(all_samples, desc="Computing ground truth")):
            # Create dataset without this sample
            loo_samples = [s for i, s in enumerate(all_samples) if i != idx]

            # Reset model to previous stage
            if stage == "pretraining":
                # Reset to random initialization
                from model import create_model
                self.model = create_model(self.config["model_config"]).to(self.device)
            else:
                # Load previous stage checkpoint
                prev_stage_map = {
                    "instruction_tuning": "pretraining",
                    "alignment": "instruction_tuning"
                }
                prev_stage = prev_stage_map[stage]
                if prev_stage in self.stage_checkpoints:
                    self.model.load_state_dict(self.stage_checkpoints[prev_stage])

            # Train on LOO dataset (quick training)
            self.model.train()
            optimizer = AdamW(
                self.model.parameters(),
                lr=stage_config["learning_rate"]
            )

            # Train for fewer epochs for efficiency
            for _ in range(2):  # Just 2 epochs
                for s in loo_samples:
                    optimizer.zero_grad()

                    # Create batch from single sample
                    sample_batch = {}
                    for k, v in s.items():
                        if isinstance(v, torch.Tensor):
                            sample_batch[k] = v.unsqueeze(0).to(self.device)
                        elif k != "sample_id" and k != "stage":
                            sample_batch[k] = torch.tensor([v]).to(self.device)

                    if "chosen" in sample_batch:
                        loss = self.model.compute_preference_loss(
                            sample_batch["chosen"],
                            sample_batch["rejected"]
                        )
                    else:
                        loss = self.model.compute_loss(
                            sample_batch["input_ids"],
                            sample_batch["labels"]
                        )

                    loss.backward()
                    optimizer.step()

            # Evaluate
            loo_metrics = self.evaluate(test_dataloader, stage)
            loo_perf = -loo_metrics["loss"]

            # Ground truth value is difference
            value = baseline_perf - loo_perf
            ground_truth_values.append(value)

        return np.array(ground_truth_values)
