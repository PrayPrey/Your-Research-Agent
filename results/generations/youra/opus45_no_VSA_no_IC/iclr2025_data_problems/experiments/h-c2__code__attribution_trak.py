"""TRAK attribution method for h-c2."""
import tempfile

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset
from trak import TRAKer

from config import ExperimentConfig


def compute_trak_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict,
    cfg: ExperimentConfig,
    device: torch.device
) -> dict:
    """Compute TRAK influence scores for probe pairs across 3 modes."""
    train_ds = train_loader.dataset
    test_ds = test_loader.dataset

    train_indices = sorted({ti for pairs in probes.values() for ti, _ in pairs})
    test_indices = sorted({tj for pairs in probes.values() for _, tj in pairs})

    train_idx_map = {idx: i for i, idx in enumerate(train_indices)}
    test_idx_map = {idx: i for i, idx in enumerate(test_indices)}

    train_subset = Subset(train_ds, train_indices)
    test_subset = Subset(test_ds, test_indices)

    train_sub_loader = DataLoader(train_subset, batch_size=cfg.batch_size, shuffle=False, num_workers=2)
    test_sub_loader = DataLoader(test_subset, batch_size=cfg.batch_size, shuffle=False, num_workers=2)

    with tempfile.TemporaryDirectory() as save_dir:
        traker = TRAKer(
            model=model,
            task="image_classification",
            train_set_size=len(train_subset),
            save_dir=save_dir,
            proj_dim=cfg.trak_proj_dim,
            device=device,
            use_half_precision=cfg.trak_use_half_precision,
        )

        traker.load_checkpoint(model.state_dict(), model_id=0)
        for batch_idx, (x, y) in enumerate(train_sub_loader):
            start = batch_idx * cfg.batch_size
            end = min(start + len(x), len(train_subset))
            traker.featurize(batch=(x.to(device), y.to(device)), inds=torch.tensor(list(range(start, end))))
        traker.finalize_features(model_ids=[0])

        traker.start_scoring_checkpoint(
            exp_name="scoring", checkpoint=model.state_dict(), model_id=0, num_targets=len(test_subset)
        )
        for batch_idx, (x, y) in enumerate(test_sub_loader):
            start = batch_idx * cfg.batch_size
            end = min(start + len(x), len(test_subset))
            traker.score(batch=(x.to(device), y.to(device)), inds=torch.tensor(list(range(start, end))))

        scores_result = traker.finalize_scores(exp_name="scoring")
        score_matrix = np.array(scores_result) if hasattr(scores_result, '__array__') else scores_result.cpu().numpy()

    results = {}
    for mode, pairs in probes.items():
        scores = [score_matrix[train_idx_map[ti], test_idx_map[tj]] for ti, tj in pairs]
        results[mode] = np.array(scores)
    return results
