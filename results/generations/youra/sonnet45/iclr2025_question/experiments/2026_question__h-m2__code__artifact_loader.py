"""Artifact loading for H-M2 analysis."""

import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple


def verify_all_artifacts_exist(
    results_path: Path,
    conditions: List[str],
    n_seeds: int
) -> Tuple[bool, List[str]]:
    """
    Verify all artifact files exist.

    Returns:
        (all_exist: bool, missing_files: List[str])
    """
    missing_files = []

    for condition in conditions:
        for seed in range(n_seeds):
            seed_dir = results_path / condition / f"seed_{seed}"

            # Check for required files
            required_files = [
                seed_dir / "initial_weights.pt",
                seed_dir / "final_weights.pt",
                seed_dir / "loss_history.npy"
            ]

            for file_path in required_files:
                if not file_path.exists():
                    missing_files.append(str(file_path))

    all_exist = len(missing_files) == 0
    return all_exist, missing_files


def load_initial_weights(
    results_path: Path,
    condition: str,
    n_seeds: int
) -> Dict[int, torch.Tensor]:
    """
    Load initial weights for all seeds.

    Returns:
        Dict mapping seed -> parameter tensor [n_params]
    """
    weights_dict = {}

    for seed in range(n_seeds):
        weight_path = results_path / condition / f"seed_{seed}" / "initial_weights.pt"
        if not weight_path.exists():
            raise FileNotFoundError(f"Missing: {weight_path}")
        weights_dict[seed] = torch.load(weight_path, map_location='cpu')

    return weights_dict


def load_final_weights(
    results_path: Path,
    condition: str,
    n_seeds: int
) -> Dict[int, torch.Tensor]:
    """
    Load final weights for all seeds.

    Returns:
        Dict mapping seed -> parameter tensor [n_params]
    """
    weights_dict = {}

    for seed in range(n_seeds):
        weight_path = results_path / condition / f"seed_{seed}" / "final_weights.pt"
        if not weight_path.exists():
            raise FileNotFoundError(f"Missing: {weight_path}")
        weights_dict[seed] = torch.load(weight_path, map_location='cpu')

    return weights_dict


def load_loss_trajectories(
    results_path: Path,
    condition: str,
    n_seeds: int
) -> np.ndarray:
    """
    Load loss trajectories for all seeds.

    Returns:
        Array [n_seeds, n_epochs]
    """
    trajectories = []

    for seed in range(n_seeds):
        loss_path = results_path / condition / f"seed_{seed}" / "loss_history.npy"
        if not loss_path.exists():
            raise FileNotFoundError(f"Missing: {loss_path}")

        loss_history = np.load(loss_path)
        trajectories.append(loss_history)

    return np.array(trajectories)
