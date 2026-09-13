import sys
import logging
from pathlib import Path
from typing import Tuple, List, Optional

import torch
from torch.utils.data import DataLoader

logger = logging.getLogger(__name__)


def _add_hm1_to_path(cfg) -> None:
    hm1 = str(Path(cfg.hm1_code_dir).resolve())
    if hm1 not in sys.path:
        sys.path.insert(0, hm1)


def _add_hm2_to_path(cfg) -> None:
    hm2 = str(Path(cfg.hm2_code_dir).resolve())
    if hm2 not in sys.path:
        sys.path.insert(0, hm2)


def _import_hm1_loaders(cfg):
    """Import h-m1 data loader functions using importlib to avoid name collision."""
    import importlib.util
    hm1_dl = Path(cfg.hm1_code_dir).resolve() / "data_loader.py"
    spec = importlib.util.spec_from_file_location("hm1_data_loader", str(hm1_dl))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _import_hm2_loaders(cfg):
    """Import h-m2 data loader functions using importlib to avoid name collision."""
    import importlib.util
    hm2_dl = Path(cfg.hm2_code_dir).resolve() / "data_loader.py"
    spec = importlib.util.spec_from_file_location("hm2_data_loader", str(hm2_dl))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_mnist_flat(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
    """Load MNIST-CNN zoo as flat vectors (for FlatMLP + DeepSets).
    Returns: train_loader, val_loader, test_loader, input_dim
    """
    _add_hm1_to_path(cfg)
    hm1 = _import_hm1_loaders(cfg)

    cfg_copy = _clone_cfg_with_data_dir(cfg, cfg.mnist_data_dir)
    train_ds, val_ds, test_ds, _, _, _ = hm1.load_and_split_dataset(cfg_copy)
    train_loader, val_loader, test_loader = hm1.build_dataloaders(train_ds, val_ds, test_ds, cfg_copy)
    input_dim = train_ds.input_dim
    logger.info(f"MNIST flat loaded: input_dim={input_dim}, train={len(train_ds)}, val={len(val_ds)}, test={len(test_ds)}")
    return train_loader, val_loader, test_loader, input_dim


def load_mnist_nfn(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, List[tuple]]:
    """Load MNIST-CNN zoo as structured weight lists (for NFNEncoder).
    Returns: train_loader, val_loader, test_loader, weight_shapes
    """
    _add_hm2_to_path(cfg)
    hm2 = _import_hm2_loaders(cfg)

    cfg_copy = _clone_cfg_with_data_dir(cfg, cfg.mnist_data_dir)
    train_ds, val_ds, test_ds, _, _, _ = hm2.load_and_split_dataset_nfn(cfg_copy)
    train_loader, val_loader, test_loader = hm2.build_dataloaders_nfn(train_ds, val_ds, test_ds, cfg_copy)
    weight_shapes = get_weight_shapes_from_nfn_dataset(train_ds)
    logger.info(f"MNIST NFN loaded: weight_shapes={weight_shapes[:3]}..., train={len(train_ds)}")
    return train_loader, val_loader, test_loader, weight_shapes


def load_cifar_flat(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, int]:
    """Load CIFAR-10 zoo as flat vectors.
    Returns: train_loader, val_loader, test_loader, input_dim
    """
    _add_hm1_to_path(cfg)
    hm1 = _import_hm1_loaders(cfg)

    cfg_copy = _clone_cfg_with_data_dir(cfg, cfg.cifar_data_dir)
    train_ds, val_ds, test_ds, _, _, _ = hm1.load_and_split_dataset(cfg_copy)
    train_loader, val_loader, test_loader = hm1.build_dataloaders(train_ds, val_ds, test_ds, cfg_copy)
    input_dim = train_ds.input_dim
    logger.info(f"CIFAR flat loaded: input_dim={input_dim}")
    return train_loader, val_loader, test_loader, input_dim


def load_cifar_nfn(cfg) -> Tuple[DataLoader, DataLoader, DataLoader, List[tuple]]:
    """Load CIFAR-10 zoo as structured weight lists.
    Returns: train_loader, val_loader, test_loader, weight_shapes
    """
    _add_hm2_to_path(cfg)
    hm2 = _import_hm2_loaders(cfg)

    cfg_copy = _clone_cfg_with_data_dir(cfg, cfg.cifar_data_dir)
    train_ds, val_ds, test_ds, _, _, _ = hm2.load_and_split_dataset_nfn(cfg_copy)
    train_loader, val_loader, test_loader = hm2.build_dataloaders_nfn(train_ds, val_ds, test_ds, cfg_copy)
    weight_shapes = get_weight_shapes_from_nfn_dataset(train_ds)
    logger.info(f"CIFAR NFN loaded: weight_shapes={weight_shapes[:3]}...")
    return train_loader, val_loader, test_loader, weight_shapes


def download_cifar_zoo(cfg) -> bool:
    """Check if CIFAR-10 zoo is available. Attempt clone if not cached.
    Returns True if available.
    """
    cifar_path = Path(cfg.cifar_data_dir)
    # Check for .pt file
    pt_files = list(cifar_path.glob("*.pt")) if cifar_path.exists() else []
    if pt_files:
        logger.info(f"CIFAR-10 zoo found at {cifar_path}: {pt_files[0].name}")
        return True

    logger.warning(f"CIFAR-10 zoo not found at {cifar_path}")
    logger.warning("Attempting download from ModelZoos/ModelZooDataset...")

    import subprocess
    import os

    cache_dir = cifar_path
    cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1",
             "https://github.com/ModelZoos/ModelZooDataset", "/tmp/ModelZooDataset"],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            # Try running download script
            dl_result = subprocess.run(
                ["python", "download_zoo.py", "--zoo", "cifar10",
                 "--output", str(cache_dir)],
                cwd="/tmp/ModelZooDataset",
                capture_output=True, text=True, timeout=600
            )
            if dl_result.returncode == 0:
                pt_files = list(cache_dir.glob("*.pt"))
                if pt_files:
                    logger.info(f"CIFAR-10 downloaded successfully")
                    return True
    except Exception as e:
        logger.warning(f"CIFAR-10 download failed: {e}")

    logger.warning("CIFAR-10 unavailable — will skip CIFAR-10 steps")
    return False


def get_weight_shapes_from_nfn_dataset(dataset) -> List[tuple]:
    """Extract per-layer weight shapes from NFNWeightDataset."""
    if hasattr(dataset, 'weight_key_order') and hasattr(dataset, 'checkpoints'):
        sample = dataset.checkpoints[0]["state_dict"]
        return [sample[k].shape for k in dataset.weight_key_order]
    # Fallback: infer from first item
    first_item = dataset[0]
    weight_list = first_item[0]  # List[Tensor]
    return [tuple(w.shape[1:]) if w.dim() > 1 else tuple(w.shape) for w in weight_list]


def _clone_cfg_with_data_dir(cfg, data_dir):
    """Return a lightweight namespace with data_dir set."""
    import types
    cfg_copy = types.SimpleNamespace(**cfg.__dict__)
    cfg_copy.data_dir = Path(data_dir)
    return cfg_copy
