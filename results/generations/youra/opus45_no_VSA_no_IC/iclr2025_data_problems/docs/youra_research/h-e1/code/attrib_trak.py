"""TRAK attribution method wrapper."""

import numpy as np
import torch
from trak import TRAKer
import config


def run_trak(model, train_loader, test_loader, checkpoints, device):
    """
    Compute TRAK influence scores.
    Returns: (num_test, num_train) score matrix.
    """
    model = model.to(device)
    train_set_size = len(train_loader.dataset)
    num_test = len(test_loader.dataset)

    traker = TRAKer(
        model=model,
        task='image_classification',
        train_set_size=train_set_size,
        proj_dim=config.PROJECTION_DIM,
        device=device,
    )

    # Featurize training data for each checkpoint
    for model_id, ckpt_path in enumerate(checkpoints):
        ckpt = torch.load(ckpt_path, map_location=device)
        traker.load_checkpoint(ckpt['model_state_dict'], model_id=model_id)
        for batch in train_loader:
            images, labels = batch
            images, labels = images.to(device), labels.to(device)
            traker.featurize(batch=(images, labels), num_samples=images.shape[0])
    traker.finalize_features()

    # Score test data
    for model_id, ckpt_path in enumerate(checkpoints):
        ckpt = torch.load(ckpt_path, map_location=device)
        traker.start_scoring_checkpoint(
            exp_name='test',
            checkpoint=ckpt['model_state_dict'],
            model_id=model_id,
            num_targets=num_test,
        )
        for batch in test_loader:
            images, labels = batch
            images, labels = images.to(device), labels.to(device)
            traker.score(batch=(images, labels), num_samples=images.shape[0])

    scores = traker.finalize_scores(exp_name='test')  # (train, test)
    return scores.T  # (test, train)
