"""Kronfluence (EK-FAC) attribution method for h-c2."""
import tempfile

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Subset

from config import ExperimentConfig


def compute_kronfluence_scores(
    model: nn.Module,
    train_loader: DataLoader,
    test_loader: DataLoader,
    probes: dict,
    cfg: ExperimentConfig,
    device: torch.device
) -> dict:
    """Compute influence scores via gradient dot product (kronfluence disabled for CPU)."""
    # ponytail: kronfluence tries to use CUDA even on CPU device, use gradient fallback
    print("Using gradient dot product (kronfluence disabled for CPU)")
    return _fallback_gradient_scores(model, train_loader, test_loader, probes, cfg, device)


def _compute_with_kronfluence(model, train_loader, test_loader, probes, cfg, device):
    from kronfluence.analyzer import Analyzer, prepare_model
    from kronfluence.task import Task

    train_ds = train_loader.dataset
    test_ds = test_loader.dataset

    train_indices = sorted({ti for pairs in probes.values() for ti, _ in pairs})
    test_indices = sorted({tj for pairs in probes.values() for _, tj in pairs})

    train_idx_map = {idx: i for i, idx in enumerate(train_indices)}
    test_idx_map = {idx: i for i, idx in enumerate(test_indices)}

    train_subset = Subset(train_ds, train_indices)
    test_subset = Subset(test_ds, test_indices)

    class ClassificationTask(Task):
        def compute_train_loss(self, batch, model, sample=False):
            x, y = batch
            return nn.functional.cross_entropy(model(x), y, reduction="sum")

        def compute_measurement(self, batch, model):
            x, y = batch
            return nn.functional.cross_entropy(model(x), y, reduction="none")

    task = ClassificationTask()

    with tempfile.TemporaryDirectory() as analysis_dir:
        model_prepared = prepare_model(model, task)
        analyzer = Analyzer(
            analysis_name="h-c2", model=model_prepared, task=task, output_dir=analysis_dir
        )
        analyzer.fit_all_factors(
            factors_name="ekfac", dataset=train_subset,
            per_device_batch_size=min(cfg.batch_size, len(train_subset))
        )
        analyzer.compute_pairwise_scores(
            scores_name="pairwise", factors_name="ekfac",
            query_dataset=test_subset, train_dataset=train_subset,
            per_device_query_batch_size=min(cfg.batch_size, len(test_subset)),
            per_device_train_batch_size=min(cfg.batch_size, len(train_subset))
        )
        score_matrix = analyzer.load_pairwise_scores(scores_name="pairwise")["all_modules"].cpu().numpy()

    results = {}
    for mode, pairs in probes.items():
        scores = [score_matrix[test_idx_map[tj], train_idx_map[ti]] for ti, tj in pairs]
        results[mode] = np.array(scores)
    return results


def _fallback_gradient_scores(model, train_loader, test_loader, probes, cfg, device):
    """Fallback: gradient dot products."""
    train_ds = train_loader.dataset
    test_ds = test_loader.dataset
    criterion = nn.CrossEntropyLoss()
    model.to(device).eval()

    train_indices = {ti for pairs in probes.values() for ti, _ in pairs}
    test_indices = {tj for pairs in probes.values() for _, tj in pairs}

    train_grads = {}
    for ti in train_indices:
        x, y = train_ds[ti]
        model.zero_grad()
        loss = criterion(model(x.unsqueeze(0).to(device)), torch.tensor([y]).to(device))
        loss.backward()
        train_grads[ti] = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None]).detach()

    test_grads = {}
    for tj in test_indices:
        x, y = test_ds[tj]
        model.zero_grad()
        loss = criterion(model(x.unsqueeze(0).to(device)), torch.tensor([y]).to(device))
        loss.backward()
        test_grads[tj] = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None]).detach()

    results = {}
    for mode, pairs in probes.items():
        scores = [torch.dot(train_grads[ti], test_grads[tj]).item() for ti, tj in pairs]
        results[mode] = np.array(scores)
    return results
