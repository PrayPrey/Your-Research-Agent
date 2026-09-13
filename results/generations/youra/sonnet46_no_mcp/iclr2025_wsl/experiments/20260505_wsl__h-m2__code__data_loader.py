"""NFNWeightDataset and data loading for H-M2: NFN Equivariant Encoder."""
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

logger = logging.getLogger("h-m2")

# ModelZoos repo path for dataset loading
_MODELZOOS_CODE = "/tmp/ModelZooDataset/code"


def _load_raw_splits(cfg) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Load dataset_mnist_hyp_rand.pt and extract final-epoch checkpoints per split.
    Reused from h-m1 (identical logic).
    """
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
        raise ValueError(
            f"Unexpected dataset format: keys={list(raw.keys()) if isinstance(raw, dict) else type(raw)}"
        )

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


def _discover_weight_keys(state_dict: Dict) -> List[str]:
    """Discover actual weight keys from state_dict at runtime, ordered by layer index."""
    keys = [k for k in state_dict.keys() if isinstance(state_dict[k], torch.Tensor)]
    # Sort by numeric index in key (e.g. module_list.0.weight before module_list.3.weight)
    def sort_key(k):
        import re
        nums = re.findall(r'\d+', k)
        return [int(n) for n in nums]
    return sorted(keys, key=sort_key)


class NFNWeightDataset(Dataset):
    """Yields (weight_list, flat_w_normalized, acc) per checkpoint.

    weight_list: List[Tensor] — per-layer tensors (float32, cpu) for NFN forward
    flat_w_normalized: Tensor — z-score normalized flat vector for permutation compatibility
    acc: scalar Tensor
    """

    def __init__(
        self,
        checkpoints: List[Dict],
        weight_key_order: List[str],
        mean: Optional[torch.Tensor] = None,
        std: Optional[torch.Tensor] = None,
    ):
        self.checkpoints = checkpoints
        self.weight_key_order = weight_key_order
        self.mean = mean
        self.std = std
        first_flat = self._flatten(checkpoints[0]["state_dict"])
        self.input_dim = first_flat.shape[0]

    def _extract_weight_list(self, state_dict: Dict) -> List[torch.Tensor]:
        """Returns ordered list of per-layer weight tensors (float32, cpu)."""
        return [state_dict[k].float().cpu() for k in self.weight_key_order]

    def _flatten(self, state_dict: Dict) -> torch.Tensor:
        """Flatten state_dict to 1D float32 tensor (same as h-m1)."""
        if "_flat_weights" in state_dict:
            return state_dict["_flat_weights"].float().cpu()
        parts = []
        for k in self.weight_key_order:
            if k in state_dict and isinstance(state_dict[k], torch.Tensor):
                parts.append(state_dict[k].float().cpu().flatten())
        return torch.cat(parts) if parts else torch.zeros(1)

    def __len__(self) -> int:
        return len(self.checkpoints)

    def __getitem__(self, idx: int) -> Tuple[List[torch.Tensor], torch.Tensor, torch.Tensor]:
        ckpt = self.checkpoints[idx]
        weight_list = self._extract_weight_list(ckpt["state_dict"])
        flat_w = self._flatten(ckpt["state_dict"])
        if self.mean is not None and self.std is not None:
            flat_w = (flat_w - self.mean) / (self.std + 1e-8)
        acc = torch.tensor(float(ckpt["test_accuracy"]), dtype=torch.float32)
        return weight_list, flat_w, acc


def collate_nfn(batch):
    """Custom collate: stack weight_list per-layer across batch.

    Returns: (List[Tensor(B,...)], Tensor(B, input_dim), Tensor(B,))
    """
    weight_lists, flat_ws, accs = zip(*batch)
    n_layers = len(weight_lists[0])
    batched_weights = [
        torch.stack([item[i] for item in weight_lists]) for i in range(n_layers)
    ]
    flat_w_batch = torch.stack(flat_ws)
    acc_batch = torch.stack(accs)
    return batched_weights, flat_w_batch, acc_batch


def load_and_split_dataset_nfn(cfg) -> Tuple[
    "NFNWeightDataset", "NFNWeightDataset", "NFNWeightDataset",
    torch.Tensor, torch.Tensor,
    List[Dict],
]:
    """Load Schurholt zoo, build NFNWeightDataset splits with z-score from train."""
    train_ckpts, val_ckpts, test_ckpts = _load_raw_splits(cfg)
    all_checkpoints = train_ckpts + val_ckpts + test_ckpts

    logger.info(
        f"Total checkpoints: {len(all_checkpoints)} "
        f"(train={len(train_ckpts)}, val={len(val_ckpts)}, test={len(test_ckpts)})"
    )

    # Discover actual weight keys from first checkpoint
    weight_key_order = _discover_weight_keys(train_ckpts[0]["state_dict"])
    logger.info(f"Discovered {len(weight_key_order)} weight keys: {weight_key_order}")

    # Compute z-score normalization stats from training set flat vectors
    logger.info("Computing z-score normalization from training set...")
    tmp_ds = NFNWeightDataset(train_ckpts, weight_key_order)
    all_flat = torch.stack(
        [tmp_ds._flatten(c["state_dict"]) for c in tqdm(train_ckpts, desc="Computing stats")]
    )
    train_mean = all_flat.mean(dim=0)
    train_std = all_flat.std(dim=0)
    logger.info(f"input_dim={tmp_ds.input_dim}, mean.norm={train_mean.norm():.4f}")

    train_ds = NFNWeightDataset(train_ckpts, weight_key_order, train_mean, train_std)
    val_ds = NFNWeightDataset(val_ckpts, weight_key_order, train_mean, train_std)
    test_ds = NFNWeightDataset(test_ckpts, weight_key_order, train_mean, train_std)

    return train_ds, val_ds, test_ds, train_mean, train_std, all_checkpoints


def build_dataloaders_nfn(
    train_ds: "NFNWeightDataset",
    val_ds: "NFNWeightDataset",
    test_ds: "NFNWeightDataset",
    cfg,
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Build DataLoaders with collate_nfn."""
    train_loader = DataLoader(
        train_ds, batch_size=cfg.batch_size, shuffle=True,
        num_workers=0, collate_fn=collate_nfn
    )
    val_loader = DataLoader(
        val_ds, batch_size=cfg.batch_size, shuffle=False,
        num_workers=0, collate_fn=collate_nfn
    )
    test_loader = DataLoader(
        test_ds, batch_size=cfg.batch_size, shuffle=False,
        num_workers=0, collate_fn=collate_nfn
    )
    return train_loader, val_loader, test_loader
