"""Kronfluence attribution method wrapper."""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from kronfluence import Analyzer, prepare_model
from kronfluence.task import Task
import config


class ClassificationTask(Task):
    """Task definition for CIFAR-10 classification."""

    def compute_train_loss(self, batch, model, sample=False):
        inputs, labels = batch
        logits = model(inputs)
        if sample:
            # For per-sample loss computation
            return nn.functional.cross_entropy(logits, labels, reduction='none')
        return nn.functional.cross_entropy(logits, labels)

    def compute_measurement(self, batch, model):
        inputs, labels = batch
        logits = model(inputs)
        # Return per-sample loss as measurement
        return nn.functional.cross_entropy(logits, labels, reduction='none')


def run_kronfluence(model, train_dataset, test_subset, device):
    """
    Compute Kronfluence (EKFAC) influence scores.
    Returns: (num_test, num_train) score matrix.
    """
    import os
    import shutil

    # Kronfluence uses its own analysis directory
    analysis_dir = os.path.join(config.OUTPUT_DIR, "kronfluence_analysis")
    if os.path.exists(analysis_dir):
        shutil.rmtree(analysis_dir)
    os.makedirs(analysis_dir, exist_ok=True)

    task = ClassificationTask()
    model = model.to(device)

    # Prepare model for Kronfluence
    kron_model = prepare_model(model, task)

    analyzer = Analyzer(
        analysis_name="h_e1_analysis",
        model=kron_model,
        task=task,
        output_dir=analysis_dir,
    )

    # Create data loaders
    train_loader = DataLoader(
        train_dataset, batch_size=config.BATCH_SIZE,
        shuffle=False, num_workers=config.NUM_WORKERS
    )
    test_loader = DataLoader(
        test_subset, batch_size=config.EVAL_BATCH_SIZE,
        shuffle=False, num_workers=0  # Subset doesn't support multiprocessing
    )

    print("  Fitting Kronfluence factors...")
    analyzer.fit_all_factors(
        factors_name="ekfac_factors",
        dataset=train_dataset,
        per_device_batch_size=config.BATCH_SIZE,
    )

    print("  Computing pairwise scores...")
    analyzer.compute_pairwise_scores(
        scores_name="pairwise_scores",
        factors_name="ekfac_factors",
        query_dataset=test_subset,
        train_dataset=train_dataset,
        per_device_query_batch_size=config.EVAL_BATCH_SIZE,
        per_device_train_batch_size=config.BATCH_SIZE,
    )

    scores = analyzer.load_pairwise_scores(scores_name="pairwise_scores")

    # Handle different return types
    if isinstance(scores, dict):
        if "all_modules" in scores:
            scores = scores["all_modules"]
        else:
            # Sum across modules
            scores = sum(scores.values())

    if isinstance(scores, torch.Tensor):
        scores = scores.cpu().numpy()

    return scores  # (num_test, num_train)
