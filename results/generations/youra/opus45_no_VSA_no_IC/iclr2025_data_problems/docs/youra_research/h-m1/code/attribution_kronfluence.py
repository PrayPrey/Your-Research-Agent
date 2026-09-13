"""Kronfluence (EK-FAC) attribution method for h-m1."""
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
    """Compute Kronfluence (EK-FAC) influence scores.

    Falls back to gradient dot product if kronfluence unavailable.
    Returns dict with keys 'mem', 'transfer', 'spurious'.
    """
    try:
        from kronfluence.analyzer import Analyzer, prepare_model
        from kronfluence.task import Task
        return _compute_with_kronfluence(model, train_loader, test_loader, probes, cfg, device)
    except ImportError:
        print("kronfluence not available, using gradient dot product fallback")
        return _fallback_gradient_scores(model, train_loader, test_loader, probes, cfg, device)


def _compute_with_kronfluence(model, train_loader, test_loader, probes, cfg, device):
    """Use official kronfluence library."""
    from kronfluence.analyzer import Analyzer, prepare_model
    from kronfluence.task import Task

    train_ds = train_loader.dataset
    test_ds = test_loader.dataset

    # Collect probe indices
    train_indices = sorted({ti for pairs in probes.values() for ti, _ in pairs})
    test_indices = sorted({tj for pairs in probes.values() for _, tj in pairs})

    train_idx_map = {idx: i for i, idx in enumerate(train_indices)}
    test_idx_map = {idx: i for i, idx in enumerate(test_indices)}

    train_subset = Subset(train_ds, train_indices)
    test_subset = Subset(test_ds, test_indices)

    class ClassificationTask(Task):
        def compute_train_loss(self, batch, model, sample=False):
            x, y = batch
            logits = model(x)
            return nn.functional.cross_entropy(logits, y, reduction="sum")

        def compute_measurement(self, batch, model):
            x, y = batch
            logits = model(x)
            return nn.functional.cross_entropy(logits, y, reduction="none")

    task = ClassificationTask()

    with tempfile.TemporaryDirectory() as analysis_dir:
        model_prepared = prepare_model(model, task)
        analyzer = Analyzer(
            analysis_name="h-m1",
            model=model_prepared,
            task=task,
            output_dir=analysis_dir
        )

        # Fit factors on training subset
        analyzer.fit_all_factors(
            factors_name="ekfac",
            dataset=train_subset,
            per_device_batch_size=min(cfg.batch_size, len(train_subset))
        )

        # Compute pairwise scores
        analyzer.compute_pairwise_scores(
            scores_name="pairwise",
            factors_name="ekfac",
            query_dataset=test_subset,
            train_dataset=train_subset,
            per_device_query_batch_size=min(cfg.batch_size, len(test_subset)),
            per_device_train_batch_size=min(cfg.batch_size, len(train_subset))
        )

        score_matrix = analyzer.load_pairwise_scores(scores_name="pairwise")
        # Shape: [num_test, num_train]
        score_matrix = score_matrix["all_modules"].cpu().numpy()

    # Gather per mode
    results = {}
    for mode, pairs in probes.items():
        scores = []
        for ti, tj in pairs:
            i = train_idx_map[ti]
            j = test_idx_map[tj]
            scores.append(score_matrix[j, i])
        results[mode] = np.array(scores)

    return results


def _fallback_gradient_scores(model, train_loader, test_loader, probes, cfg, device):
    """Fallback: compute gradient dot products similar to TracIn but at final checkpoint."""
    train_ds = train_loader.dataset
    test_ds = test_loader.dataset
    criterion = nn.CrossEntropyLoss()

    model.to(device)
    model.eval()

    train_indices = set()
    test_indices = set()
    for pairs in probes.values():
        for ti, tj in pairs:
            train_indices.add(ti)
            test_indices.add(tj)

    # Compute train gradients
    train_grads = {}
    for ti in train_indices:
        x, y = train_ds[ti]
        model.zero_grad()
        logits = model(x.unsqueeze(0).to(device))
        loss = criterion(logits, torch.tensor([y]).to(device))
        loss.backward()
        grads = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])
        train_grads[ti] = grads.detach()

    # Compute test gradients
    test_grads = {}
    for tj in test_indices:
        x, y = test_ds[tj]
        model.zero_grad()
        logits = model(x.unsqueeze(0).to(device))
        loss = criterion(logits, torch.tensor([y]).to(device))
        loss.backward()
        grads = torch.cat([p.grad.flatten() for p in model.parameters() if p.grad is not None])
        test_grads[tj] = grads.detach()

    # Compute dot products
    results = {}
    for mode, pairs in probes.items():
        scores = []
        for ti, tj in pairs:
            dot = torch.dot(train_grads[ti], test_grads[tj]).item()
            scores.append(dot)
        results[mode] = np.array(scores)

    return results
