"""
Training utilities for the Mutual Calibration Framework.
Implements the joint optimization objective and training procedures.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from typing import Dict, List, Tuple, Optional
import numpy as np
from models import (
    MutualCalibrationFramework, MCFStatic, BaselineAI, TransparencyPlusAI
)


def compute_ece(predictions: torch.Tensor, targets: torch.Tensor, n_bins: int = 10) -> torch.Tensor:
    """
    Compute Expected Calibration Error.

    Args:
        predictions: Softmax probabilities (batch, num_classes)
        targets: True labels (batch,)
        n_bins: Number of bins for calibration

    Returns:
        ECE value
    """
    confidences, pred_labels = predictions.max(dim=1)
    accuracies = (pred_labels == targets).float()

    ece = torch.zeros(1, device=predictions.device)
    bin_boundaries = torch.linspace(0, 1, n_bins + 1, device=predictions.device)

    for i in range(n_bins):
        in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i + 1])
        prop_in_bin = in_bin.float().mean()

        if prop_in_bin > 0:
            avg_confidence = confidences[in_bin].mean()
            avg_accuracy = accuracies[in_bin].mean()
            ece += prop_in_bin * torch.abs(avg_accuracy - avg_confidence)

    return ece


class MCFTrainer:
    """
    Trainer for the Mutual Calibration Framework.
    Implements the joint optimization objective.
    """

    def __init__(
        self,
        model: MutualCalibrationFramework,
        loss_weights: Dict[str, float],
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        device: str = "cuda"
    ):
        self.model = model.to(device)
        self.loss_weights = loss_weights
        self.device = device

        self.optimizer = torch.optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )

        self.history = {
            "train_loss": [],
            "val_loss": [],
            "train_accuracy": [],
            "val_accuracy": [],
            "train_ece": [],
            "val_ece": [],
            "train_arr": [],
            "val_arr": []
        }

    def compute_loss(
        self,
        outputs: Dict[str, torch.Tensor],
        targets: torch.Tensor,
        human_decisions: Optional[torch.Tensor] = None,
        human_correct: Optional[torch.Tensor] = None,
        ai_better: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Compute the joint optimization objective.

        Args:
            outputs: Model outputs dict
            targets: True labels
            human_decisions: Simulated human decisions (for reliance loss)
            human_correct: Whether human was correct (for deference loss)
            ai_better: Whether AI was better than human (for deference loss)

        Returns:
            Total loss and breakdown dict
        """
        predictions = outputs["predictions"]
        confidence = outputs["confidence"].squeeze(-1)
        deference = outputs["deference"].squeeze(-1)

        # Accuracy loss (cross-entropy)
        loss_accuracy = F.cross_entropy(
            predictions.log() + 1e-8, targets
        )

        # Calibration loss (ECE)
        loss_calibration = compute_ece(predictions, targets)

        # Initialize optional losses
        loss_reliance = torch.tensor(0.0, device=self.device)
        loss_deference = torch.tensor(0.0, device=self.device)

        # Reliance loss (if human interaction data provided)
        if human_decisions is not None:
            ai_correct = (predictions.argmax(dim=1) == targets).float()
            human_followed_ai = (human_decisions == predictions.argmax(dim=1)).float()

            # Penalize over-reliance when AI is wrong
            over_reliance_penalty = human_followed_ai * (1 - ai_correct)
            # Penalize under-reliance when AI is correct
            under_reliance_penalty = (1 - human_followed_ai) * ai_correct

            loss_reliance = (over_reliance_penalty + under_reliance_penalty).mean()

        # Deference loss (if ground truth for optimal deference provided)
        if ai_better is not None:
            # Target: defer to human (d=1) when human is better (ai_better=0)
            optimal_deference = 1 - ai_better.float()
            loss_deference = F.mse_loss(deference, optimal_deference)

        # Total loss
        total_loss = (
            self.loss_weights["accuracy"] * loss_accuracy +
            self.loss_weights["calibration"] * loss_calibration +
            self.loss_weights["reliance"] * loss_reliance +
            self.loss_weights["deference"] * loss_deference
        )

        loss_breakdown = {
            "total": total_loss.item(),
            "accuracy": loss_accuracy.item(),
            "calibration": loss_calibration.item(),
            "reliance": loss_reliance.item(),
            "deference": loss_deference.item()
        }

        return total_loss, loss_breakdown

    def train_epoch(
        self,
        train_loader: DataLoader,
        human_simulator=None,
        user=None
    ) -> Dict[str, float]:
        """Train for one epoch."""
        self.model.train()
        total_losses = []
        all_preds = []
        all_targets = []
        all_confidences = []

        for batch in train_loader:
            x, y = batch[0].to(self.device), batch[1].to(self.device)

            self.optimizer.zero_grad()

            outputs = self.model(x)
            predictions = outputs["predictions"]

            # Simulate human decisions if simulator provided
            human_decisions = None
            ai_better = None
            if human_simulator is not None and user is not None:
                ai_preds = predictions.argmax(dim=1)
                human_only = human_simulator.simulate_human_only_decision(user, y)
                ai_correct = (ai_preds == y).float()
                human_correct = (human_only == y).float()
                ai_better = (ai_correct > human_correct).float()

                # Simulate collaborative decision
                human_decisions, _ = human_simulator.simulate_collaborative_decision(
                    user, y, ai_preds,
                    outputs["confidence"].squeeze(-1),
                    outputs["deference"].squeeze(-1)
                )

            loss, loss_breakdown = self.compute_loss(
                outputs, y, human_decisions, None, ai_better
            )

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
            self.optimizer.step()

            total_losses.append(loss_breakdown)
            all_preds.append(predictions.detach())
            all_targets.append(y)
            all_confidences.append(outputs["confidence"].squeeze(-1).detach())

        # Aggregate metrics
        all_preds = torch.cat(all_preds)
        all_targets = torch.cat(all_targets)
        all_confidences = torch.cat(all_confidences)

        accuracy = (all_preds.argmax(dim=1) == all_targets).float().mean().item()
        ece = compute_ece(all_preds, all_targets).item()

        avg_losses = {
            k: np.mean([l[k] for l in total_losses])
            for k in total_losses[0].keys()
        }

        return {
            "loss": avg_losses["total"],
            "accuracy": accuracy,
            "ece": ece,
            **avg_losses
        }

    def evaluate(
        self,
        val_loader: DataLoader,
        human_simulator=None,
        user=None
    ) -> Dict[str, float]:
        """Evaluate on validation set."""
        self.model.eval()
        total_losses = []
        all_preds = []
        all_targets = []
        all_confidences = []
        all_deferences = []

        arr_values = []

        with torch.no_grad():
            for batch in val_loader:
                x, y = batch[0].to(self.device), batch[1].to(self.device)

                outputs = self.model(x)
                predictions = outputs["predictions"]

                human_decisions = None
                ai_better = None
                if human_simulator is not None and user is not None:
                    ai_preds = predictions.argmax(dim=1)
                    human_only = human_simulator.simulate_human_only_decision(user, y)
                    ai_correct = (ai_preds == y).float()
                    human_correct = (human_only == y).float()
                    ai_better = (ai_correct > human_correct).float()

                    human_decisions, metrics = human_simulator.simulate_collaborative_decision(
                        user, y, ai_preds,
                        outputs["confidence"].squeeze(-1),
                        outputs["deference"].squeeze(-1),
                        outputs.get("deference"),
                        None  # recommendation_type not used for MCF in this context
                    )
                    arr_values.append(metrics["appropriate_reliance_rate"])

                loss, loss_breakdown = self.compute_loss(
                    outputs, y, human_decisions, None, ai_better
                )

                total_losses.append(loss_breakdown)
                all_preds.append(predictions)
                all_targets.append(y)
                all_confidences.append(outputs["confidence"].squeeze(-1))
                all_deferences.append(outputs["deference"].squeeze(-1))

        all_preds = torch.cat(all_preds)
        all_targets = torch.cat(all_targets)

        accuracy = (all_preds.argmax(dim=1) == all_targets).float().mean().item()
        ece = compute_ece(all_preds, all_targets).item()

        avg_losses = {
            k: np.mean([l[k] for l in total_losses])
            for k in total_losses[0].keys()
        }

        result = {
            "loss": avg_losses["total"],
            "accuracy": accuracy,
            "ece": ece,
            **avg_losses
        }

        if arr_values:
            result["arr"] = np.mean(arr_values)

        return result

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
        patience: int = 10,
        human_simulator=None,
        user=None
    ) -> Dict:
        """
        Full training loop with early stopping.
        """
        best_val_loss = float('inf')
        patience_counter = 0
        best_state = None

        for epoch in range(epochs):
            train_metrics = self.train_epoch(train_loader, human_simulator, user)
            val_metrics = self.evaluate(val_loader, human_simulator, user)

            # Update history
            self.history["train_loss"].append(train_metrics["loss"])
            self.history["val_loss"].append(val_metrics["loss"])
            self.history["train_accuracy"].append(train_metrics["accuracy"])
            self.history["val_accuracy"].append(val_metrics["accuracy"])
            self.history["train_ece"].append(train_metrics["ece"])
            self.history["val_ece"].append(val_metrics["ece"])
            if "arr" in val_metrics:
                self.history["val_arr"].append(val_metrics["arr"])

            # Learning rate scheduling
            self.scheduler.step(val_metrics["loss"])

            # Early stopping
            if val_metrics["loss"] < best_val_loss:
                best_val_loss = val_metrics["loss"]
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch + 1}")
                break

        # Restore best model
        if best_state is not None:
            self.model.load_state_dict(best_state)

        return self.history


class BaselineTrainer:
    """
    Trainer for baseline models (BaselineAI, TransparencyPlusAI).
    """

    def __init__(
        self,
        model: nn.Module,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        device: str = "cuda"
    ):
        self.model = model.to(device)
        self.device = device

        self.optimizer = torch.optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )

        self.history = {
            "train_loss": [],
            "val_loss": [],
            "train_accuracy": [],
            "val_accuracy": []
        }

    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]:
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0

        for batch in train_loader:
            x, y = batch[0].to(self.device), batch[1].to(self.device)

            self.optimizer.zero_grad()

            if isinstance(self.model, TransparencyPlusAI):
                probs, conf, importance = self.model(x)
            else:
                probs, conf = self.model(x)

            loss = F.cross_entropy(probs.log() + 1e-8, y)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item() * x.size(0)
            correct += (probs.argmax(dim=1) == y).sum().item()
            total += x.size(0)

        return {
            "loss": total_loss / total,
            "accuracy": correct / total
        }

    def evaluate(self, val_loader: DataLoader) -> Dict[str, float]:
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in val_loader:
                x, y = batch[0].to(self.device), batch[1].to(self.device)

                if isinstance(self.model, TransparencyPlusAI):
                    probs, conf, importance = self.model(x)
                else:
                    probs, conf = self.model(x)

                loss = F.cross_entropy(probs.log() + 1e-8, y)

                total_loss += loss.item() * x.size(0)
                correct += (probs.argmax(dim=1) == y).sum().item()
                total += x.size(0)

        return {
            "loss": total_loss / total,
            "accuracy": correct / total
        }

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int,
        patience: int = 10
    ) -> Dict:
        best_val_loss = float('inf')
        patience_counter = 0
        best_state = None

        for epoch in range(epochs):
            train_metrics = self.train_epoch(train_loader)
            val_metrics = self.evaluate(val_loader)

            self.history["train_loss"].append(train_metrics["loss"])
            self.history["val_loss"].append(val_metrics["loss"])
            self.history["train_accuracy"].append(train_metrics["accuracy"])
            self.history["val_accuracy"].append(val_metrics["accuracy"])

            self.scheduler.step(val_metrics["loss"])

            if val_metrics["loss"] < best_val_loss:
                best_val_loss = val_metrics["loss"]
                best_state = {k: v.cpu().clone() for k, v in self.model.state_dict().items()}
                patience_counter = 0
            else:
                patience_counter += 1

            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch + 1}")
                break

        if best_state is not None:
            self.model.load_state_dict(best_state)

        return self.history
