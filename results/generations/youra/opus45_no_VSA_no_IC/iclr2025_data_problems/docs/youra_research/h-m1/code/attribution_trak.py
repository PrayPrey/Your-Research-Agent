"""TRAK attribution method for h-m1."""
import os
import tempfile

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from trak import TRAKer
from trak.projectors import BasicProjector, CudaProjector

from config import ExperimentConfig


def compute_trak_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict,
    cfg: ExperimentConfig,
    device: torch.device
) -> dict:
    """Compute TRAK influence scores for probe pairs.

    Returns dict with keys 'mem', 'transfer', 'spurious', each mapping to np.ndarray.
    """
    train_ds = train_loader.dataset
    test_ds = test_loader.dataset

    # Collect all unique probe indices
    train_indices = set()
    test_indices = set()
    for mode, pairs in probes.items():
        for ti, tj in pairs:
            train_indices.add(ti)
            test_indices.add(tj)

    train_indices = sorted(train_indices)
    test_indices = sorted(test_indices)

    # Create index mappings
    train_idx_map = {idx: i for i, idx in enumerate(train_indices)}
    test_idx_map = {idx: i for i, idx in enumerate(test_indices)}

    # Subset datasets for efficiency
    train_subset = Subset(train_ds, train_indices)
    test_subset = Subset(test_ds, test_indices)

    train_sub_loader = DataLoader(train_subset, batch_size=cfg.batch_size, shuffle=False, num_workers=2)
    test_sub_loader = DataLoader(test_subset, batch_size=cfg.batch_size, shuffle=False, num_workers=2)

    # Use temp dir for TRAK cache
    with tempfile.TemporaryDirectory() as save_dir:
        projector_type = CudaProjector if torch.cuda.is_available() else BasicProjector

        traker = TRAKer(
            model=model,
            task="image_classification",
            train_set_size=len(train_subset),
            save_dir=save_dir,
            proj_dim=cfg.trak_proj_dim,
            projector=projector_type,
            device=device,
            use_half_precision=cfg.trak_use_half_precision,
        )

        # Featurize training set
        traker.load_checkpoint(model.state_dict(), model_id=0)
        for batch_idx, (x, y) in enumerate(train_sub_loader):
            start = batch_idx * cfg.batch_size
            end = min(start + len(x), len(train_subset))
            batch_indices = list(range(start, end))
            traker.featurize(batch=(x.to(device), y.to(device)), inds=torch.tensor(batch_indices))
        traker.finalize_features(model_ids=[0])

        # Score test set
        traker.start_scoring_checkpoint(
            exp_name="scoring",
            checkpoint=model.state_dict(),
            model_id=0,
            num_targets=len(test_subset)
        )
        for batch_idx, (x, y) in enumerate(test_sub_loader):
            start = batch_idx * cfg.batch_size
            end = min(start + len(x), len(test_subset))
            batch_indices = list(range(start, end))
            traker.score(batch=(x.to(device), y.to(device)), inds=torch.tensor(batch_indices))

        # shape: [num_train, num_test]
        score_matrix = traker.finalize_scores(exp_name="scoring").cpu().numpy()

    # Gather scores per mode
    results = {}
    for mode, pairs in probes.items():
        scores = []
        for ti, tj in pairs:
            i = train_idx_map[ti]
            j = test_idx_map[tj]
            scores.append(score_matrix[i, j])
        results[mode] = np.array(scores)

    return results
