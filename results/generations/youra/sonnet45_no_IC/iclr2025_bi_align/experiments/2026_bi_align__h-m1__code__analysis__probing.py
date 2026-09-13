"""
Linear Probing Classifiers
Preference classification and attribute regression probes
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple
from sklearn.metrics import r2_score
import numpy as np

class PreferenceProbe(nn.Module):
    """Linear probe for binary preference classification."""

    def __init__(self, hidden_dim: int = 1600, num_classes: int = 2):
        super().__init__()
        self.linear = nn.Linear(hidden_dim, num_classes)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            hidden_states: [B, H] hidden representations

        Returns:
            [B, 2] logits
        """
        return self.linear(hidden_states)


class AttributeProbe(nn.Module):
    """Linear probe for attribute regression (3 attributes, 5 levels each)."""

    def __init__(
        self,
        hidden_dim: int = 1600,
        num_attributes: int = 3,
        num_levels: int = 5
    ):
        super().__init__()
        self.num_attributes = num_attributes
        self.num_levels = num_levels

        # Separate linear layer per attribute
        self.attr_heads = nn.ModuleList([
            nn.Linear(hidden_dim, num_levels)
            for _ in range(num_attributes)
        ])

    def forward(self, hidden_states: torch.Tensor) -> List[torch.Tensor]:
        """
        Forward pass.

        Args:
            hidden_states: [B, H] hidden representations

        Returns:
            List of 3 × [B, 5] logits (one per attribute)
        """
        return [head(hidden_states) for head in self.attr_heads]


class ProbeTrainer:
    """Trainer for linear probing classifiers."""

    def __init__(
        self,
        probe: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: str = "cuda",
        task_type: str = "preference"
    ):
        self.probe = probe
        self.optimizer = optimizer
        self.device = torch.device(device)
        self.task_type = task_type
        self.probe.to(self.device)

    def train_epoch(
        self,
        hidden_states: torch.Tensor,
        labels: torch.Tensor
    ) -> float:
        """Train for one epoch."""
        self.probe.train()
        self.optimizer.zero_grad()

        hidden_states = hidden_states.to(self.device)
        labels = labels.to(self.device)

        if self.task_type == "preference":
            # Binary classification
            logits = self.probe(hidden_states)
            loss = F.cross_entropy(logits, labels)
        else:
            # Attribute regression (multi-head classification)
            attr_logits = self.probe(hidden_states)
            # labels: [B, 3] with values 1-5, convert to 0-4
            labels_idx = (labels - 1).long()  # [B, 3]
            losses = []
            for i, logits in enumerate(attr_logits):
                losses.append(F.cross_entropy(logits, labels_idx[:, i]))
            loss = sum(losses) / len(losses)

        loss.backward()
        self.optimizer.step()

        return loss.item()

    def evaluate(
        self,
        hidden_states: torch.Tensor,
        labels: torch.Tensor
    ) -> dict:
        """Evaluate probe."""
        self.probe.eval()

        with torch.no_grad():
            hidden_states = hidden_states.to(self.device)
            labels = labels.to(self.device)

            if self.task_type == "preference":
                # Binary classification accuracy
                logits = self.probe(hidden_states)
                preds = logits.argmax(dim=1)
                accuracy = (preds == labels).float().mean().item()
                return {'accuracy': accuracy}
            else:
                # Attribute regression R²
                attr_logits = self.probe(hidden_states)
                labels_idx = (labels - 1).long()  # [B, 3]

                # Convert logits to predictions (argmax + 1 to get 1-5 scale)
                preds = []
                for logits in attr_logits:
                    preds.append(logits.argmax(dim=1) + 1)
                preds = torch.stack(preds, dim=1).float()  # [B, 3]

                # Compute R² per attribute
                r2_scores = []
                for i in range(3):
                    r2 = r2_score(
                        labels[:, i].cpu().numpy(),
                        preds[:, i].cpu().numpy()
                    )
                    r2_scores.append(r2)

                # Return mean R²
                return {'r2': np.mean(r2_scores)}

    def train(
        self,
        train_data: Tuple[torch.Tensor, torch.Tensor],
        val_data: Tuple[torch.Tensor, torch.Tensor],
        epochs: int = 20
    ) -> dict:
        """
        Full training loop.

        Args:
            train_data: (hidden_states, labels)
            val_data: (hidden_states, labels)
            epochs: Number of training epochs

        Returns:
            {'train_history': list, 'val_history': list, 'val_accuracy' or 'val_r2': float}
        """
        train_hidden, train_labels = train_data
        val_hidden, val_labels = val_data

        train_history = []
        val_history = []

        for epoch in range(epochs):
            # Train
            train_loss = self.train_epoch(train_hidden, train_labels)

            # Evaluate
            train_metrics = self.evaluate(train_hidden, train_labels)
            val_metrics = self.evaluate(val_hidden, val_labels)

            if self.task_type == "preference":
                train_history.append(train_metrics['accuracy'])
                val_history.append(val_metrics['accuracy'])
                metric_name = "Accuracy"
                metric_val = val_metrics['accuracy']
            else:
                train_history.append(train_metrics['r2'])
                val_history.append(val_metrics['r2'])
                metric_name = "R²"
                metric_val = val_metrics['r2']

            if (epoch + 1) % 5 == 0:
                print(f"  Epoch {epoch+1}/{epochs}: {metric_name} = {metric_val:.3f}")

        result = {
            'train_history': train_history,
            'val_history': val_history
        }

        if self.task_type == "preference":
            result['val_accuracy'] = val_history[-1]
        else:
            result['val_r2'] = val_history[-1]

        return result
