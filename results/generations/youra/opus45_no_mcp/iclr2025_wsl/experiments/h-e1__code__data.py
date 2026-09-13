"""Data loading for H-E1: Model Zoo Dataset Validity.

Loads CIFAR-10 Model Zoo from Zenodo (Schurholt et al. 2022, NeurIPS).
DOI: 10.5281/zenodo.6620869
"""

import os
import sys
import types
import subprocess
import numpy as np
import torch
from pathlib import Path

ZENODO_RECORD_ID = "6620869"
DATASET_FILE = "dataset_cifar_small_hyp_fix.pt"
DATASET_URL = f"https://zenodo.org/api/records/{ZENODO_RECORD_ID}/files/{DATASET_FILE}/content"
EXPECTED_SIZE = 1823561025  # 1.7GB
CACHE_DIR = Path.home() / ".cache" / "model_zoos" / "cifar10"


def _setup_stub_modules():
    """Create stub modules for checkpoints_to_datasets to enable unpickling."""
    checkpoints_to_datasets = types.ModuleType("checkpoints_to_datasets")
    dataset_base = types.ModuleType("checkpoints_to_datasets.dataset_base")

    class ModelDatasetBase:
        def __setstate__(self, state):
            self.__dict__.update(state)

    dataset_base.ModelDatasetBase = ModelDatasetBase
    checkpoints_to_datasets.dataset_base = dataset_base
    sys.modules["checkpoints_to_datasets"] = checkpoints_to_datasets
    sys.modules["checkpoints_to_datasets.dataset_base"] = dataset_base


def download_with_wget(url: str, dest: Path) -> None:
    """Download file using wget with resume support."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["wget", "-c", "-q", "--show-progress", url, "-O", str(dest)]
    print(f"Downloading with wget: {dest.name}")
    subprocess.run(cmd, check=True)


def load_accuracies() -> np.ndarray:
    """Load Model Zoo test_accuracy labels from Zenodo.

    Downloads ~1.7GB dataset on first run, caches locally.
    Raises RuntimeError if download fails (NO mock fallback).
    """
    cache_path = CACHE_DIR / DATASET_FILE

    if not cache_path.exists() or cache_path.stat().st_size < EXPECTED_SIZE:
        print(f"Downloading CIFAR-10 Model Zoo from Zenodo ({ZENODO_RECORD_ID})...")
        print(f"URL: {DATASET_URL}")
        print(f"Cache: {cache_path}")
        try:
            download_with_wget(DATASET_URL, cache_path)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Failed to download Model Zoo dataset from Zenodo.\n"
                f"Error: {e}\n\n"
                f"Manual download: https://zenodo.org/record/{ZENODO_RECORD_ID}\n"
                f"File: {DATASET_FILE}\n"
                f"Place at: {cache_path}"
            ) from e

        if cache_path.stat().st_size < EXPECTED_SIZE:
            raise RuntimeError(
                f"Download incomplete: {cache_path.stat().st_size} < {EXPECTED_SIZE} bytes"
            )
    else:
        print(f"Loading cached Model Zoo from {cache_path}")

    print("Loading .pt file (may take a moment)...")
    _setup_stub_modules()
    data = torch.load(cache_path, map_location="cpu", weights_only=False)

    # Model Zoo format: dict with trainset/valset/testset, each with .properties['test_acc']
    all_acc = []
    for split in ['trainset', 'valset', 'testset']:
        if split in data and hasattr(data[split], 'properties'):
            props = data[split].properties
            if 'test_acc' in props:
                acc = props['test_acc']
                if hasattr(acc, 'numpy'):
                    acc = acc.numpy()
                all_acc.append(np.array(acc, dtype=np.float32))
                print(f"  {split}: {len(acc)} models")

    if not all_acc:
        raise RuntimeError(f"No test_acc found in dataset. Keys: {list(data.keys())}")

    accuracies = np.concatenate(all_acc)
    print(f"Loaded {len(accuracies)} model accuracies from Model Zoo")
    return _postprocess(accuracies)


def _postprocess(accuracies: np.ndarray) -> np.ndarray:
    """Filter NaN/corrupted, normalize to [0,100]."""
    valid_mask = ~np.isnan(accuracies) & np.isfinite(accuracies)
    accuracies = accuracies[valid_mask]

    # Convert [0,1] to [0,100] percentage
    if accuracies.max() <= 1.0:
        accuracies = accuracies * 100.0

    if len(accuracies) < 500:
        raise ValueError(f"Too few valid samples: {len(accuracies)} < 500")

    return accuracies
