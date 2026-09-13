"""ModelZooDataset loading with dual-path fallback for H-E1."""
import logging
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List

import torch
from tqdm import tqdm

from config import ExperimentConfig

logger = logging.getLogger("h-e1")


def load_via_package(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load zoo via modelzoo pip package (preferred)."""
    try:
        from modelzoo.datasets import ModelZooDataset  # type: ignore
    except ImportError:
        raise ImportError("modelzoo package not installed")

    checkpoints = []
    zoo = ModelZooDataset(cfg.zoo_name, split="all", data_dir=str(cfg.data_dir))
    for item in tqdm(zoo, desc="Loading via package"):
        if isinstance(item, (tuple, list)) and len(item) == 2:
            sd, metrics = item
        else:
            raise ValueError(f"Unexpected zoo item format: {type(item)}")

        if isinstance(metrics, dict):
            acc = float(metrics.get("test_accuracy", metrics.get("accuracy", 0.0)))
        else:
            acc = float(metrics)

        checkpoints.append({"state_dict": sd, "test_accuracy": acc})
    return checkpoints


def load_via_files(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load zoo by globbing .pt/.pth files directly."""
    data_dir = Path(cfg.data_dir)
    pt_files = list(data_dir.glob("**/*.pt")) + list(data_dir.glob("**/*.pth"))

    if not pt_files:
        raise FileNotFoundError(f"No .pt/.pth files found in {data_dir}")

    checkpoints = []
    for path in tqdm(pt_files, desc="Loading checkpoints"):
        try:
            ckpt = torch.load(path, map_location="cpu", weights_only=False)
        except Exception as e:
            logger.warning(f"Skipping corrupt file {path}: {e}")
            continue

        # Format A: {'state_dict': ..., 'metrics': {'test_accuracy': float}}
        if isinstance(ckpt, dict) and "state_dict" in ckpt:
            sd = ckpt["state_dict"]
            if "metrics" in ckpt and isinstance(ckpt["metrics"], dict):
                acc = float(ckpt["metrics"].get("test_accuracy", 0.0))
            elif "test_accuracy" in ckpt:
                # Format B: {'state_dict': ..., 'test_accuracy': float}
                acc = float(ckpt["test_accuracy"])
            else:
                logger.warning(f"No accuracy found in {path}, skipping")
                continue
        elif isinstance(ckpt, dict) and all(
            isinstance(v, torch.Tensor) for v in ckpt.values()
        ):
            # Format C: state_dict directly (no accuracy available — skip)
            logger.warning(f"Format C (no accuracy) at {path}, skipping")
            continue
        else:
            logger.warning(f"Unknown checkpoint format at {path}, skipping")
            continue

        if not (0.0 <= acc <= 1.0):
            logger.warning(f"Accuracy {acc} out of range at {path}, skipping")
            continue

        checkpoints.append({"state_dict": sd, "test_accuracy": acc})

    return checkpoints


def load_zoo_checkpoints_from_dataset_pt(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load from preprocessed dataset_mnist_seed.pt (Schurholt Zenodo format).

    The .pt file contains {'trainset': ModelDatasetBase, 'valset': ..., 'testset': ...}.
    Each ModelDatasetBase has:
      - data_in: list of OrderedDict state dicts
      - properties: {'test_acc': [...], 'training_iteration': [...], ...}
    We load all splits and filter to the final training_iteration (max epoch).
    """
    import sys
    sys.path.insert(0, "/tmp/ModelZooDataset/code")

    data_dir = Path(cfg.data_dir)
    pt_candidates = list(data_dir.glob("dataset_mnist*.pt")) + list(data_dir.glob("**/*.pt"))

    dataset_pt = None
    for f in pt_candidates:
        if "dataset_mnist" in f.name:
            dataset_pt = f
            break

    if dataset_pt is None:
        raise FileNotFoundError(f"No dataset_mnist*.pt found in {data_dir}")

    logger.info(f"Loading preprocessed zoo from {dataset_pt}")

    try:
        from checkpoints_to_datasets.dataset_base import ModelDatasetBase  # type: ignore
    except ImportError as e:
        raise ImportError(f"ModelDatasetBase not importable: {e}")

    raw = torch.load(dataset_pt, map_location="cpu", weights_only=False)

    if not isinstance(raw, dict) or "trainset" not in raw:
        raise ValueError(f"Unexpected format: {type(raw)}, keys={list(raw.keys()) if isinstance(raw, dict) else 'N/A'}")

    # Collect all checkpoints across splits, filter to max training_iteration
    all_state_dicts = []
    all_accs = []
    all_iters = []

    for split_name in ["trainset", "valset", "testset"]:
        ds = raw[split_name]
        iters = ds.properties["training_iteration"]
        accs = ds.properties["test_acc"]
        for i, (it, acc) in enumerate(zip(iters, accs)):
            all_state_dicts.append(ds.data_in[i])
            all_accs.append(float(acc))
            all_iters.append(int(it))

    # Filter to final epoch only (max training_iteration)
    max_iter = max(all_iters)
    logger.info(f"Filtering to training_iteration={max_iter} (final epoch)")

    checkpoints = []
    for sd, acc, it in tqdm(
        zip(all_state_dicts, all_accs, all_iters),
        total=len(all_accs),
        desc="Filtering checkpoints",
    ):
        if it == max_iter and 0.0 <= acc <= 1.0:
            checkpoints.append({"state_dict": sd, "test_accuracy": acc})

    logger.info(f"Loaded {len(checkpoints)} final-epoch checkpoints")
    return checkpoints


def load_zoo_checkpoints(cfg: ExperimentConfig) -> List[Dict[str, Any]]:
    """Load zoo checkpoints with fallback chain."""
    # Try 1: pip package
    try:
        result = load_via_package(cfg)
        logger.info(f"Loaded {len(result)} checkpoints via package")
        return result
    except ImportError:
        logger.info("modelzoo package not available, trying dataset .pt file")
    except Exception as e:
        logger.warning(f"Package loading failed: {e}")

    # Try 2: preprocessed dataset .pt (Zenodo download)
    try:
        result = load_zoo_checkpoints_from_dataset_pt(cfg)
        logger.info(f"Loaded {len(result)} checkpoints from dataset .pt")
        return result
    except (FileNotFoundError, ValueError) as e:
        logger.info(f"Dataset .pt not ready: {e}, trying file glob")
    except Exception as e:
        logger.warning(f"Dataset .pt loading failed: {e}")

    # Try 3: direct .pt file glob
    result = load_via_files(cfg)
    logger.info(f"Loaded {len(result)} checkpoints via file glob")
    return result
