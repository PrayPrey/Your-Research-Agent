"""
Evaluation system for multi-task LoRA-MoE coordination.
Implements per-task metrics and super-additive gain computation.
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, List
import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DataConfig


class Evaluator:
    """Multi-task evaluation system."""

    def __init__(self, model: nn.Module, config: DataConfig, device: str = "cuda"):
        """
        Initialize evaluator.

        Args:
            model: PyTorch model to evaluate
            config: Data configuration
            device: Device to run evaluation on
        """
        self.model = model
        self.config = config
        self.device = device
        self.task_names = config.glue_tasks + config.superglue_tasks

    def evaluate_task(self, task_name: str, dataloader: DataLoader) -> Dict[str, float]:
        """
        Evaluate single task.

        Args:
            task_name: Name of the task
            dataloader: DataLoader for the task

        Returns:
            Dictionary with accuracy, f1, loss metrics
        """
        self.model.eval()

        total_correct = 0
        total_samples = 0
        total_loss = 0.0
        num_batches = 0

        with torch.no_grad():
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['labels'].to(self.device)

                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                # Get predictions
                logits = outputs['logits']
                predictions = logits.argmax(dim=-1)

                # Compute accuracy
                correct = (predictions == labels).sum().item()
                total_correct += correct
                total_samples += labels.size(0)

                # Accumulate loss
                if 'loss' in outputs and outputs['loss'] is not None:
                    total_loss += outputs['loss'].item()
                    num_batches += 1

        # Compute metrics
        accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0

        return {
            'accuracy': accuracy,
            'loss': avg_loss,
            'num_samples': total_samples
        }

    def evaluate_all_tasks(self, dataloaders: Dict[str, DataLoader]) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all tasks.

        Args:
            dataloaders: Dictionary mapping task names to DataLoaders

        Returns:
            Dictionary with per-task results
        """
        results = {}
        for task_name, dataloader in dataloaders.items():
            print(f"Evaluating task: {task_name}")
            results[task_name] = self.evaluate_task(task_name, dataloader)

        return results

    def compute_aggregate_metrics(self, task_results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Compute aggregate metrics across all tasks.

        Args:
            task_results: Dictionary with per-task results

        Returns:
            Dictionary with aggregate metrics (avg_accuracy, std_accuracy)
        """
        accuracies = [results['accuracy'] for results in task_results.values()]

        return {
            'avg_accuracy': np.mean(accuracies),
            'std_accuracy': np.std(accuracies),
            'min_accuracy': np.min(accuracies),
            'max_accuracy': np.max(accuracies)
        }

    def compute_super_additive_gain(
        self,
        baseline: float,
        lora_only: float,
        moe_only: float,
        proposed: float
    ) -> float:
        """
        Compute super-additive gain.

        Formula: proposed - (lora_only + moe_only - baseline)

        Args:
            baseline: Baseline accuracy (frozen Mixtral)
            lora_only: LoRA-only accuracy
            moe_only: MoE-only accuracy
            proposed: Proposed coordinated model accuracy

        Returns:
            Gain value (positive = super-additive, negative = sub-additive)
        """
        additive_baseline = lora_only + moe_only - baseline
        gain = proposed - additive_baseline

        return gain


def compute_expert_utilization_entropy(expert_probs: torch.Tensor) -> float:
    """
    Compute entropy of expert utilization.

    Args:
        expert_probs: Tensor of shape [num_samples, num_experts] with routing probabilities

    Returns:
        Entropy value (higher = more balanced utilization)
    """
    # Average expert usage across samples
    avg_probs = expert_probs.mean(dim=0)

    # Compute entropy: -sum(p * log(p))
    # Add small epsilon to avoid log(0)
    epsilon = 1e-10
    entropy = -(avg_probs * torch.log(avg_probs + epsilon)).sum().item()

    return entropy


def compute_routing_alignment(
    lora_probs: torch.Tensor,
    moe_probs: torch.Tensor
) -> float:
    """
    Compute alignment between LoRA and MoE routing distributions.

    Args:
        lora_probs: Tensor of shape [num_samples, num_lora_experts]
        moe_probs: Tensor of shape [num_samples, num_moe_experts]

    Returns:
        Correlation coefficient (Pearson correlation)
    """
    # Ensure same number of experts (pad if needed)
    if lora_probs.shape[1] != moe_probs.shape[1]:
        max_experts = max(lora_probs.shape[1], moe_probs.shape[1])

        if lora_probs.shape[1] < max_experts:
            padding = torch.zeros(
                lora_probs.shape[0],
                max_experts - lora_probs.shape[1],
                device=lora_probs.device
            )
            lora_probs = torch.cat([lora_probs, padding], dim=1)

        if moe_probs.shape[1] < max_experts:
            padding = torch.zeros(
                moe_probs.shape[0],
                max_experts - moe_probs.shape[1],
                device=moe_probs.device
            )
            moe_probs = torch.cat([moe_probs, padding], dim=1)

    # Flatten to 1D
    lora_flat = lora_probs.flatten()
    moe_flat = moe_probs.flatten()

    # Compute Pearson correlation
    lora_mean = lora_flat.mean()
    moe_mean = moe_flat.mean()

    lora_centered = lora_flat - lora_mean
    moe_centered = moe_flat - moe_mean

    numerator = (lora_centered * moe_centered).sum()
    denominator = torch.sqrt((lora_centered ** 2).sum() * (moe_centered ** 2).sum())

    if denominator == 0:
        return 0.0

    correlation = (numerator / denominator).item()

    return correlation
