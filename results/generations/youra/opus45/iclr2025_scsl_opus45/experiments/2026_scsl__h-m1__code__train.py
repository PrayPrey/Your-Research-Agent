"""Training module for H-M1 experiment.

Implements ERM training loop with per-sample loss trajectory tracking.
Extended from H-E1: tracks ALL 20 epochs (not just 5).
"""

from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import Config
from model import ResNet50Classifier


class LossTrajectoryTracker:
    """Track per-sample loss trajectories across epochs.

    Stores loss values for each sample at each trajectory epoch,
    enabling trajectory feature extraction for curvature analysis.

    Extended from H-E1: default num_epochs changed from 5 to 20.
    """

    def __init__(self, num_samples: int, num_epochs: int = 20):
        """Initialize tracker with pre-allocated matrix.

        Args:
            num_samples: Number of samples to track (4795 for Waterbirds train)
            num_epochs: Number of trajectory epochs to track (default: 20 for H-M1)
        """
        self.num_samples = num_samples
        self.num_epochs = num_epochs
        # Pre-allocate matrix: shape (num_samples, num_epochs)
        self.matrix = np.zeros((num_samples, num_epochs), dtype=np.float32)

    def log_epoch_losses(
        self,
        sample_indices: np.ndarray,
        losses: np.ndarray,
        epoch_idx: int,
    ) -> None:
        """Store losses for a batch at given epoch slot.

        Args:
            sample_indices: Sample indices from dataset, shape (N_batch,)
            losses: Per-sample losses, shape (N_batch,)
            epoch_idx: 0-based epoch index (0..19 for epochs 1..20)
        """
        self.matrix[sample_indices, epoch_idx] = losses

    def get_loss_matrix(self) -> np.ndarray:
        """Return filled loss matrix.

        Returns:
            Loss matrix, shape (num_samples, num_epochs) = (4795, 20)
        """
        return self.matrix


def run_epoch_eval_pass(
    model: ResNet50Classifier,
    eval_loader: DataLoader,
    device: torch.device,
    tracker: LossTrajectoryTracker,
    epoch_idx: int,
) -> None:
    """Run deterministic evaluation pass over full training set.

    Computes per-sample losses and logs them to the tracker.
    Uses no_grad and eval mode for deterministic results.

    Args:
        model: Trained model
        eval_loader: Deterministic dataloader (no augmentation, fixed order)
        device: Compute device
        tracker: Loss trajectory tracker
        epoch_idx: 0-based epoch index for tracker
    """
    model.eval()
    criterion = nn.CrossEntropyLoss(reduction='none')

    with torch.no_grad():
        for images, labels, _, sample_indices in eval_loader:
            images = images.to(device)
            labels = labels.to(device)

            logits = model(images)
            losses = criterion(logits, labels)

            tracker.log_epoch_losses(
                sample_indices.cpu().numpy(),
                losses.cpu().numpy(),
                epoch_idx,
            )


def train(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """ERM training with per-sample loss trajectory tracking.

    Trains for config.epochs epochs, running deterministic eval passes
    after ALL epochs (1 through config.trajectory_epochs=20) to log loss trajectories.

    Extended from H-E1: logs ALL 20 epochs for full curvature analysis.

    Args:
        config: Experiment configuration
        model: Model to train
        train_loader: Training dataloader (with augmentation)
        eval_loader: Evaluation dataloader (deterministic, no augmentation)
        device: Compute device

    Returns:
        Tuple of (trained_model, populated_tracker)
    """
    model = model.to(device)

    # Setup training
    criterion = nn.CrossEntropyLoss(reduction='none')
    optimizer = SGD(
        model.parameters(),
        lr=config.lr,
        momentum=config.momentum,
        weight_decay=config.weight_decay,
    )

    # Initialize tracker with ALL epochs (20 for H-M1)
    num_train_samples = len(eval_loader.dataset)
    tracker = LossTrajectoryTracker(
        num_samples=num_train_samples,
        num_epochs=config.trajectory_epochs,
    )

    # Training loop
    for epoch in range(1, config.epochs + 1):
        model.train()
        epoch_loss = 0.0
        num_batches = 0

        pbar = tqdm(train_loader, desc=f"Epoch {epoch}/{config.epochs}")
        for images, labels, _, _ in pbar:
            images = images.to(device)
            labels = labels.to(device)

            # Forward pass
            logits = model(images)
            per_sample_loss = criterion(logits, labels)
            loss = per_sample_loss.mean()

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = epoch_loss / num_batches
        print(f"Epoch {epoch}: Average Loss = {avg_loss:.4f}")

        # Run eval pass for ALL trajectory epochs (1 through trajectory_epochs=20)
        if epoch <= config.trajectory_epochs:
            print(f"  Running trajectory eval pass for epoch {epoch}...")
            run_epoch_eval_pass(model, eval_loader, device, tracker, epoch - 1)

    return model, tracker
