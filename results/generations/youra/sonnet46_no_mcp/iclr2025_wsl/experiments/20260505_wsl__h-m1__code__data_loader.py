"""WeightDataset and data loading for H-M1: Flat MLP Permutation Sensitivity."""
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

logger = logging.getLogger("h-m1")

# ModelZoos repo path for dataset loading
_MODELZOOS_CODE = "/tmp/ModelZooDataset/code"


class WeightDataset(Dataset):
    """Dataset of flattened weight vectors with z-score normalization."""

    def __init__(
        self,
        checkpoints: List[Dict],
        mean: Optional[torch.Tensor] = None,
        std: Optional[torch.Tensor] = None,
    ):
        self.checkpoints = checkpoints
        self.mean = mean
        self.std = std
        first_flat = self._flatten(checkpoints[0]["state_dict"])
        self.input_dim = first_flat.shape[0]

    def _flatten(self, state_dict) -> torch.Tensor:
        """Flatten state_dict to 1D float32 tensor, handles _flat_weights format."""
        if "_flat_weights" in state_dict:
            return state_dict["_flat_weights"].float().cpu()
        parts = []
        for k, v in state_dict.items():
            if isinstance(v, torch.Tensor):
                parts.append(v.float().cpu().flatten())
        return torch.cat(parts)

    def __len__(self) -> int:
        return len(self.checkpoints)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        ckpt = self.checkpoints[idx]
        flat_w = self._flatten(ckpt["state_dict"])
        if self.mean is not None and self.std is not None:
            flat_w = (flat_w - self.mean) / (self.std + 1e-8)
        acc = torch.tensor(float(ckpt["test_accuracy"]), dtype=torch.float32)
        return flat_w, acc


def _load_raw_splits(cfg) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Load dataset_mnist_hyp_rand.pt and extract final-epoch checkpoints per split."""
    if _MODELZOOS_CODE not in sys.path:
        sys.path.insert(0, _MODELZOOS_CODE)

    data_dir = Path(cfg.data_dir)
    candidates = list(data_dir.glob("*.pt"))
    if not candidates:
        raise FileNotFoundError(f"No .pt file found in {data_dir}")
    pt_file = candidates[0]
    logger.info(f"Loading {pt_file}")

    raw = torch.load(pt_file, map_location="cpu", weights_only=False)
    if not isinstance(raw, dict) or "trainset" not in raw:
        raise ValueError(f"Unexpected dataset format: keys={list(raw.keys()) if isinstance(raw, dict) else type(raw)}")

    splits = {}
    for split_name in ["trainset", "valset", "testset"]:
        ds = raw[split_name]
        props = ds.properties
        iters = props["training_iteration"]
        accs = props["test_acc"]
        max_iter = max(iters)
        ckpts = []
        for i, (it, acc) in enumerate(zip(iters, accs)):
            if it == max_iter and 0.0 <= float(acc) <= 1.0:
                ckpts.append({"state_dict": ds.data_in[i], "test_accuracy": float(acc)})
        splits[split_name] = ckpts
        logger.info(f"  {split_name}: {len(ckpts)} final-epoch checkpoints (max_iter={max_iter})")

    return splits["trainset"], splits["valset"], splits["testset"]


def load_and_split_dataset(cfg) -> Tuple[
    "WeightDataset", "WeightDataset", "WeightDataset",
    torch.Tensor, torch.Tensor,
    List[Dict],
]:
    """Load Schurholt zoo, apply standard train/val/test splits, z-score normalize from train."""
    train_ckpts, val_ckpts, test_ckpts = _load_raw_splits(cfg)
    all_checkpoints = train_ckpts + val_ckpts + test_ckpts

    logger.info(f"Total checkpoints: {len(all_checkpoints)} (train={len(train_ckpts)}, val={len(val_ckpts)}, test={len(test_ckpts)})")

    # Compute z-score normalization stats from training set only
    logger.info("Computing z-score normalization from training set...")
    tmp_ds = WeightDataset(train_ckpts)
    all_flat = torch.stack([tmp_ds._flatten(c["state_dict"]) for c in tqdm(train_ckpts, desc="Computing stats")])
    train_mean = all_flat.mean(dim=0)
    train_std = all_flat.std(dim=0)
    logger.info(f"input_dim={tmp_ds.input_dim}, mean.norm={train_mean.norm():.4f}")

    train_ds = WeightDataset(train_ckpts, train_mean, train_std)
    val_ds = WeightDataset(val_ckpts, train_mean, train_std)
    test_ds = WeightDataset(test_ckpts, train_mean, train_std)

    return train_ds, val_ds, test_ds, train_mean, train_std, all_checkpoints


def build_dataloaders(
    train_ds: "WeightDataset",
    val_ds: "WeightDataset",
    test_ds: "WeightDataset",
    cfg,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Build DataLoaders with batch_size from config."""
    train_loader = DataLoader(train_ds, batch_size=cfg.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_ds, batch_size=cfg.batch_size, shuffle=False, num_workers=0)
    return train_loader, val_loader, test_loader
