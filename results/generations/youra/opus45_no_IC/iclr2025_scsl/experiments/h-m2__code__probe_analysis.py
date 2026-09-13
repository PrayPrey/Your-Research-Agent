"""Epoch-wise linear probe training."""
import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from tqdm import tqdm
from feature_cache import load_frozen_backbone, extract_epoch_features

def train_epoch_probes(X_train, y_bird_train, y_bg_train, X_test, y_bird_test, y_bg_test, C=1.0, max_iter=1000):
    """Train spurious and core probes, return test accuracies."""
    clf_spurious = LogisticRegression(C=C, max_iter=max_iter, solver="lbfgs")
    clf_spurious.fit(X_train, y_bg_train)
    spurious_acc = clf_spurious.score(X_test, y_bg_test)

    clf_core = LogisticRegression(C=C, max_iter=max_iter, solver="lbfgs")
    clf_core.fit(X_train, y_bird_train)
    core_acc = clf_core.score(X_test, y_bird_test)

    return {"spurious_acc": spurious_acc, "core_acc": core_acc}

def run_all_epochs(ckpt_paths, loaders, device, cache_dir, C=1.0, max_iter=1000):
    """Run probe analysis for all epochs."""
    results = {}
    epochs = sorted(ckpt_paths.keys())

    for epoch in tqdm(epochs, desc="Probing epochs"):
        backbone = load_frozen_backbone(ckpt_paths[epoch])

        train_cache = os.path.join(cache_dir, f"train_epoch_{epoch:03d}.npz")
        test_cache = os.path.join(cache_dir, f"test_epoch_{epoch:03d}.npz")

        X_train, y_bird_train, y_bg_train = extract_epoch_features(backbone, loaders["train"], device, train_cache)
        X_test, y_bird_test, y_bg_test = extract_epoch_features(backbone, loaders["test"], device, test_cache)

        result = train_epoch_probes(X_train, y_bird_train, y_bg_train, X_test, y_bird_test, y_bg_test, C, max_iter)
        results[epoch] = result
        print(f"Epoch {epoch}: spurious={result['spurious_acc']:.4f}, core={result['core_acc']:.4f}")

    return results
