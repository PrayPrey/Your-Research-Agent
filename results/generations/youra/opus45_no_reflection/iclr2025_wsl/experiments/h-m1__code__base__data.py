"""Data loading module for H-E1 experiment."""

import os
import requests
import numpy as np
import torch
from torchvision.datasets import CIFAR10


def download_zenodo_dataset(url: str, dest: str) -> str:
    """Download file from Zenodo if not present."""
    if os.path.exists(dest):
        print(f"Dataset already exists: {dest}")
        return dest

    os.makedirs(os.path.dirname(dest), exist_ok=True)
    print(f"Downloading from {url}...")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(dest, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                pct = 100 * downloaded / total_size
                print(f"\rProgress: {pct:.1f}%", end="", flush=True)

    print(f"\nDownloaded: {dest}")
    return dest


def load_model_zoo(path: str) -> dict:
    """Load Small CNN Zoo dataset from .pt file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model zoo not found: {path}")

    print(f"Loading model zoo from {path}...")
    data = torch.load(path, map_location='cpu', weights_only=False)
    print(f"Loaded model zoo with {len(data)} entries")
    return data


def load_cifar10_ground_truth(root: str) -> np.ndarray:
    """Load CIFAR-10 test set ground truth labels."""
    os.makedirs(root, exist_ok=True)
    test_dataset = CIFAR10(root=root, train=False, download=True)
    ground_truth = np.array(test_dataset.targets)
    print(f"Loaded CIFAR-10 ground truth: {ground_truth.shape}")
    return ground_truth


def get_model_predictions(model_zoo: dict) -> dict:
    """Extract per-model predicted labels from model zoo dataset.

    Returns:
        dict: {model_id: predictions}, predictions shape (10000,)
    """
    predictions = {}

    # Inspect model zoo structure
    if isinstance(model_zoo, dict):
        # Check for 'predictions' key
        if 'predictions' in model_zoo:
            preds_data = model_zoo['predictions']
        elif 'train' in model_zoo or 'test' in model_zoo:
            # ModelZooDataset format: dict with 'train'/'test' splits
            preds_data = model_zoo.get('test', model_zoo)
        else:
            preds_data = model_zoo
    elif hasattr(model_zoo, '__len__'):
        # List of model entries
        preds_data = {f"model_{i}": entry for i, entry in enumerate(model_zoo)}
    else:
        raise ValueError(f"Unknown model zoo format: {type(model_zoo)}")

    # Extract predictions per model
    for model_id, entry in preds_data.items():
        if isinstance(entry, dict):
            # Entry is dict with 'predictions' or 'preds' key
            if 'predictions' in entry:
                pred = entry['predictions']
            elif 'preds' in entry:
                pred = entry['preds']
            elif 'logits' in entry:
                pred = entry['logits']
            else:
                continue
        elif isinstance(entry, (torch.Tensor, np.ndarray)):
            pred = entry
        else:
            continue

        # Convert to numpy
        if isinstance(pred, torch.Tensor):
            pred = pred.numpy()

        # Handle logits (N, 10) vs labels (N,)
        if pred.ndim == 2:
            pred = pred.argmax(axis=-1)

        # Skip malformed predictions
        if pred.shape[0] != 10000:
            continue

        predictions[str(model_id)] = pred.astype(np.int64)

    print(f"Extracted predictions for {len(predictions)} models")
    return predictions
