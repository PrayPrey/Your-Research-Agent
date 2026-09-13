"""Training module for H-M2 trajectory generation."""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from tqdm import tqdm

from models import get_model, get_flattened_params


def train_single_seed(
    architecture: str,
    train_loader: DataLoader,
    seed: int,
    n_epochs: int,
    learning_rate: float,
    momentum: float,
    device: str
) -> Tuple[torch.Tensor, torch.Tensor, np.ndarray]:
    """
    Train a single model with given seed.

    Returns:
        initial_weights: Flattened parameter vector at initialization
        final_weights: Flattened parameter vector after training
        loss_history: Loss per epoch (shape: [n_epochs])
    """
    # Set seed for reproducibility
    torch.manual_seed(seed)
    if device == "cuda":
        torch.cuda.manual_seed(seed)

    # Initialize model
    model = get_model(architecture).to(device)

    # Save initial weights
    initial_weights = get_flattened_params(model).cpu()

    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=momentum)

    # Training loop
    loss_history = []

    for epoch in range(n_epochs):
        epoch_losses = []

        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()

            epoch_losses.append(loss.item())

        # Average loss for this epoch
        avg_loss = np.mean(epoch_losses)
        loss_history.append(avg_loss)

    # Save final weights
    final_weights = get_flattened_params(model).cpu()

    return initial_weights, final_weights, np.array(loss_history)


def train_condition(
    architecture: str,
    dataset: str,
    train_loader: DataLoader,
    n_seeds: int,
    n_epochs: int,
    learning_rate: float,
    momentum: float,
    device: str,
    save_dir: Path
) -> None:
    """
    Train models for all seeds in a condition.

    Saves artifacts to:
        {save_dir}/{architecture}_{dataset}/seed_{i}/initial_weights.pt
        {save_dir}/{architecture}_{dataset}/seed_{i}/final_weights.pt
        {save_dir}/{architecture}_{dataset}/seed_{i}/loss_history.npy
    """
    condition = f"{architecture}_{dataset}"
    condition_dir = save_dir / condition
    condition_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nTraining condition: {condition}")
    for seed in tqdm(range(n_seeds), desc=f"{condition}"):
        seed_dir = condition_dir / f"seed_{seed}"
        seed_dir.mkdir(exist_ok=True)

        # Train model
        initial_weights, final_weights, loss_history = train_single_seed(
            architecture=architecture,
            train_loader=train_loader,
            seed=seed,
            n_epochs=n_epochs,
            learning_rate=learning_rate,
            momentum=momentum,
            device=device
        )

        # Save artifacts
        torch.save(initial_weights, seed_dir / "initial_weights.pt")
        torch.save(final_weights, seed_dir / "final_weights.pt")
        np.save(seed_dir / "loss_history.npy", loss_history)

    print(f"✓ Completed {condition}: {n_seeds} seeds saved")
