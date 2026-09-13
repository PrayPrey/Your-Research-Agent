"""
Training loop for multi-task LoRA-MoE coordination.
Implements Trainer class with AdamW optimizer and cosine scheduling.
"""
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.utils.data import DataLoader
from typing import Dict, Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from config import TrainingConfig


class Trainer:
    """Multi-task trainer with coordination."""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        config: TrainingConfig,
        device: str = "cuda"
    ):
        """
        Initialize trainer.

        Args:
            model: PyTorch model (BaselineModel or ProposedModel)
            train_loader: Training data loader
            val_loader: Validation data loader
            config: Training configuration
            device: Device to run on (cuda/cpu)
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.device = device

        self.optimizer = setup_optimizer(model, config)
        self.scheduler = setup_scheduler(self.optimizer, config)
        self.task_weights = None  # Updated after validation
        self.global_step = 0

    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """
        Train single epoch.

        Args:
            epoch: Current epoch number

        Returns:
            Dictionary with epoch metrics (loss, task_loss, alignment_loss, aux_loss)
        """
        self.model.train()

        total_loss = 0.0
        total_task_loss = 0.0
        total_alignment_loss = 0.0
        total_aux_loss = 0.0
        num_batches = 0

        for batch_idx, batch in enumerate(self.train_loader):
            # Move batch to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['labels'].to(self.device)
            task_ids = batch['task_ids'].to(self.device)

            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels,
                task_weights=self.task_weights
            )

            # Extract losses
            loss = outputs.get('loss', outputs.get('total_loss', None))
            task_loss = outputs.get('task_loss', loss)
            alignment_loss = outputs.get('alignment_loss', torch.tensor(0.0))
            aux_loss = outputs.get('aux_loss', torch.tensor(0.0))

            # Compute total loss
            if loss is None:
                loss = task_loss + \
                       self.config.alignment_loss_weight * alignment_loss + \
                       self.config.aux_loss_weight * aux_loss

            # Backward pass
            loss.backward()

            # Gradient accumulation
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                # Clip gradients
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

                # Optimizer step
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()

                self.global_step += 1

            # Accumulate metrics
            total_loss += loss.item()
            total_task_loss += task_loss.item() if isinstance(task_loss, torch.Tensor) else task_loss
            total_alignment_loss += alignment_loss.item() if isinstance(alignment_loss, torch.Tensor) else 0.0
            total_aux_loss += aux_loss.item() if isinstance(aux_loss, torch.Tensor) else 0.0
            num_batches += 1

        # Return average metrics
        return {
            'loss': total_loss / num_batches,
            'task_loss': total_task_loss / num_batches,
            'alignment_loss': total_alignment_loss / num_batches,
            'aux_loss': total_aux_loss / num_batches
        }

    def validate(self) -> Dict[str, float]:
        """
        Validate on validation set.

        Returns:
            Dictionary with validation metrics (avg_accuracy, per_task_accuracy)
        """
        self.model.eval()

        total_correct = 0
        total_samples = 0
        task_correct = {}
        task_samples = {}

        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)
                task_ids = batch['task_ids'].to(self.device)

                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                # Get predictions
                logits = outputs['logits']
                predictions = logits.argmax(dim=-1)

                # Compute accuracy
                correct = (predictions == labels).sum().item()
                total_correct += correct
                total_samples += labels.size(0)

                # Per-task accuracy
                for task_id in task_ids.unique():
                    mask = task_ids == task_id
                    task_id_val = task_id.item()

                    if task_id_val not in task_correct:
                        task_correct[task_id_val] = 0
                        task_samples[task_id_val] = 0

                    task_correct[task_id_val] += (predictions[mask] == labels[mask]).sum().item()
                    task_samples[task_id_val] += mask.sum().item()

        # Compute metrics
        avg_accuracy = total_correct / total_samples if total_samples > 0 else 0.0

        per_task_accuracy = {}
        for task_id, correct in task_correct.items():
            per_task_accuracy[f'task_{task_id}'] = correct / task_samples[task_id]

        return {
            'avg_accuracy': avg_accuracy,
            **per_task_accuracy
        }

    def compute_task_weights(self, val_metrics: Dict[str, float]) -> torch.Tensor:
        """
        Compute performance-based task weights.

        Args:
            val_metrics: Dictionary with per-task accuracy

        Returns:
            Tensor of shape [num_tasks] with normalized weights
        """
        # Extract per-task accuracies
        task_accuracies = []
        for key in sorted(val_metrics.keys()):
            if key.startswith('task_'):
                task_accuracies.append(val_metrics[key])

        if not task_accuracies:
            return None

        # Convert to tensor
        accuracies = torch.tensor(task_accuracies, dtype=torch.float32)

        # Higher weight for harder tasks (lower accuracy)
        weights = 1.0 - accuracies

        # Normalize
        weights = weights / weights.sum()

        return weights.to(self.device)

    def save_checkpoint(self, epoch: int, metrics: Dict[str, float], path: str) -> None:
        """
        Save training checkpoint.

        Args:
            epoch: Current epoch
            metrics: Current metrics
            path: Path to save checkpoint
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        torch.save({
            'epoch': epoch,
            'global_step': self.global_step,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict(),
            'metrics': metrics,
            'task_weights': self.task_weights
        }, path)

    def load_checkpoint(self, path: str) -> Dict:
        """
        Load training checkpoint.

        Args:
            path: Path to checkpoint file

        Returns:
            Dictionary with checkpoint metrics
        """
        checkpoint = torch.load(path, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        self.task_weights = checkpoint['task_weights']
        self.global_step = checkpoint.get('global_step', 0)

        return checkpoint['metrics']


def setup_optimizer(model: nn.Module, config: TrainingConfig) -> AdamW:
    """
    Create AdamW optimizer.

    Args:
        model: PyTorch model
        config: Training configuration

    Returns:
        AdamW optimizer
    """
    return AdamW(
        model.parameters(),
        lr=config.learning_rate,
        betas=(0.9, 0.999),
        weight_decay=config.weight_decay
    )


def setup_scheduler(optimizer: AdamW, config: TrainingConfig) -> CosineAnnealingLR:
    """
    Create cosine annealing learning rate scheduler.

    Args:
        optimizer: AdamW optimizer
        config: Training configuration

    Returns:
        CosineAnnealingLR scheduler
    """
    # Estimate total steps
    total_steps = config.num_epochs * 12000 // config.gradient_accumulation_steps

    return CosineAnnealingLR(
        optimizer,
        T_max=total_steps - config.warmup_steps
    )
