"""Training module for H-M2 experiment.

Implements three training regimes:
1. ERM (baseline) - standard cross-entropy
2. GroupDRO - worst-group loss minimization with exponentiated gradient
3. Random Reweighting - variance-matched sample weights control
"""

from typing import Tuple, Optional

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import SGD
from torch.utils.data import DataLoader
from tqdm import tqdm

from config import Config
from model import ResNet50Classifier


class LossTrajectoryTracker:
    """Track per-sample loss trajectories across epochs.

    Stores loss values for each sample at each trajectory epoch,
    enabling trajectory feature extraction for minority group detection.
    """

    def __init__(self, num_samples: int, num_epochs: int = 5):
        """Initialize tracker with pre-allocated matrix.

        Args:
            num_samples: Number of samples to track (4795 for Waterbirds train)
            num_epochs: Number of trajectory epochs to track (default: 5)
        """
        self.num_samples = num_samples
        self.num_epochs = num_epochs
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
            epoch_idx: 0-based epoch index (0..4 for epochs 1..5)
        """
        self.matrix[sample_indices, epoch_idx] = losses

    def get_loss_matrix(self) -> np.ndarray:
        """Return filled loss matrix.

        Returns:
            Loss matrix, shape (num_samples, num_epochs) = (4795, 5)
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


def train_erm(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """ERM training with per-sample loss trajectory tracking.

    Standard cross-entropy loss with uniform sample weighting.

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

    criterion = nn.CrossEntropyLoss(reduction='none')
    optimizer = SGD(
        model.parameters(),
        lr=config.lr,
        momentum=config.momentum,
        weight_decay=config.weight_decay_erm,
    )

    num_train_samples = len(eval_loader.dataset)
    tracker = LossTrajectoryTracker(
        num_samples=num_train_samples,
        num_epochs=config.trajectory_epochs,
    )

    for epoch in range(1, config.epochs + 1):
        model.train()
        epoch_loss = 0.0
        num_batches = 0

        pbar = tqdm(train_loader, desc=f"[ERM] Epoch {epoch}/{config.epochs}")
        for images, labels, _, _ in pbar:
            images = images.to(device)
            labels = labels.to(device)

            logits = model(images)
            per_sample_loss = criterion(logits, labels)
            loss = per_sample_loss.mean()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = epoch_loss / num_batches
        print(f"[ERM] Epoch {epoch}: Average Loss = {avg_loss:.4f}")

        if epoch <= config.trajectory_epochs:
            run_epoch_eval_pass(model, eval_loader, device, tracker, epoch - 1)

    return model, tracker


def train_groupdro(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    group_counts: np.ndarray,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker, np.ndarray]:
    """GroupDRO training with exponentiated gradient weight updates.

    Implements worst-group loss minimization via dynamically adjusted
    group weights using exponentiated gradient descent.

    Args:
        config: Experiment configuration
        model: Model to train
        train_loader: Training dataloader
        eval_loader: Evaluation dataloader
        device: Compute device
        group_counts: Per-group sample counts, shape (4,)

    Returns:
        Tuple of (trained_model, populated_tracker, group_weights_history)
        group_weights_history: shape (epochs, 4)
    """
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(reduction='none')
    optimizer = SGD(
        model.parameters(),
        lr=config.lr,
        momentum=config.momentum,
        weight_decay=config.weight_decay_gdro,
    )

    num_train_samples = len(eval_loader.dataset)
    tracker = LossTrajectoryTracker(
        num_samples=num_train_samples,
        num_epochs=config.trajectory_epochs,
    )

    # Initialize group weights uniformly
    group_weights = torch.ones(config.num_groups, device=device) / config.num_groups
    group_weights_history = []

    for epoch in range(1, config.epochs + 1):
        model.train()
        epoch_loss = 0.0
        num_batches = 0

        pbar = tqdm(train_loader, desc=f"[GroupDRO] Epoch {epoch}/{config.epochs}")
        for images, labels, group_ids, _ in pbar:
            images = images.to(device)
            labels = labels.to(device)
            group_ids = group_ids.to(device)

            logits = model(images)
            per_sample_loss = criterion(logits, labels)

            # Compute per-group mean loss
            group_losses = torch.zeros(config.num_groups, device=device)
            for g in range(config.num_groups):
                mask = (group_ids == g)
                if mask.any():
                    group_losses[g] = per_sample_loss[mask].mean()

            # Exponentiated gradient update (detach for weight update)
            with torch.no_grad():
                group_weights = group_weights * torch.exp(config.groupdro_gamma * group_losses.detach())
                group_weights = group_weights / group_weights.sum()

            # Weighted loss for model update
            loss = (group_losses * group_weights.detach()).sum()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}", "max_w": f"{group_weights.max().item():.3f}"})

        avg_loss = epoch_loss / num_batches
        print(f"[GroupDRO] Epoch {epoch}: Average Loss = {avg_loss:.4f}, Weights = {group_weights.cpu().numpy().round(3)}")

        # Save weights after each epoch
        group_weights_history.append(group_weights.cpu().numpy().copy())

        if epoch <= config.trajectory_epochs:
            run_epoch_eval_pass(model, eval_loader, device, tracker, epoch - 1)

    return model, tracker, np.stack(group_weights_history)


def compute_variance_matched_weights(
    group_counts: np.ndarray,
    num_samples: int,
    group_ids: np.ndarray,
    groupdro_gamma: float,
    seed: int,
) -> np.ndarray:
    """Sample per-sample weights matching GroupDRO gradient variance.

    Generates random weights from log-normal distribution with variance
    matching the expected GroupDRO weight variance.

    Args:
        group_counts: Per-group sample counts, shape (4,)
        num_samples: Total training samples
        group_ids: Per-sample group assignments, shape (num_samples,)
        groupdro_gamma: GroupDRO gamma parameter
        seed: Random seed for reproducibility

    Returns:
        weights: shape (num_samples,), normalized to sum to 1
    """
    rng = np.random.default_rng(seed)

    # Estimate target variance from GroupDRO effective weights
    # At convergence, group weights approx proportional to exp(gamma * avg_group_loss)
    # Use inverse group count as proxy for expected loss (minority = higher loss)
    inv_counts = 1.0 / (group_counts + 1e-8)
    group_effective_weights = np.exp(groupdro_gamma * inv_counts / inv_counts.max())
    group_effective_weights = group_effective_weights / group_effective_weights.sum()

    # Assign each sample its group's effective weight
    per_sample_group_weight = group_effective_weights[group_ids]
    target_var = np.var(per_sample_group_weight)

    # Sample from log-normal to match variance
    # For log-normal: sigma^2 = ln(1 + var/mean^2)
    mean_weight = 1.0 / num_samples
    sigma = np.sqrt(np.log(1 + target_var / (mean_weight ** 2 + 1e-8)))
    sigma = max(sigma, 0.1)  # Ensure some variance

    raw_weights = rng.lognormal(mean=0.0, sigma=sigma, size=num_samples)
    weights = raw_weights / raw_weights.sum()

    return weights.astype(np.float32)


def train_random_reweight(
    config: Config,
    model: ResNet50Classifier,
    train_loader: DataLoader,
    eval_loader: DataLoader,
    device: torch.device,
    random_weights: np.ndarray,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]:
    """Random reweighting training with pre-computed variance-matched weights.

    Control condition: applies random sample weights that match GroupDRO
    gradient variance but without group-specific targeting.

    Args:
        config: Experiment configuration
        model: Model to train
        train_loader: Training dataloader
        eval_loader: Evaluation dataloader
        device: Compute device
        random_weights: Pre-computed sample weights, shape (num_samples,)

    Returns:
        Tuple of (trained_model, populated_tracker)
    """
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(reduction='none')
    optimizer = SGD(
        model.parameters(),
        lr=config.lr,
        momentum=config.momentum,
        weight_decay=config.weight_decay_erm,  # Use ERM weight decay
    )

    num_train_samples = len(eval_loader.dataset)
    tracker = LossTrajectoryTracker(
        num_samples=num_train_samples,
        num_epochs=config.trajectory_epochs,
    )

    random_weights_tensor = torch.from_numpy(random_weights).float().to(device)

    for epoch in range(1, config.epochs + 1):
        model.train()
        epoch_loss = 0.0
        num_batches = 0

        pbar = tqdm(train_loader, desc=f"[Random] Epoch {epoch}/{config.epochs}")
        for images, labels, _, sample_indices in pbar:
            images = images.to(device)
            labels = labels.to(device)
            sample_indices = sample_indices.to(device)

            logits = model(images)
            per_sample_loss = criterion(logits, labels)

            # Apply pre-computed random weights
            batch_weights = random_weights_tensor[sample_indices]
            loss = (per_sample_loss * batch_weights).sum() / (batch_weights.sum() + 1e-8)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1
            pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = epoch_loss / num_batches
        print(f"[Random] Epoch {epoch}: Average Loss = {avg_loss:.4f}")

        if epoch <= config.trajectory_epochs:
            run_epoch_eval_pass(model, eval_loader, device, tracker, epoch - 1)

    return model, tracker
