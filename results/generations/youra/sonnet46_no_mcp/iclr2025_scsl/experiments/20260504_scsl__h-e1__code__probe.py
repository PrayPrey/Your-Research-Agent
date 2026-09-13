import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from typing import Tuple

from config import ExperimentConfig, ProbeConfig
from data.waterbirds import get_waterbirds_loader
from data.celeba import get_celeba_loader
from train import build_model


def extract_features(
    model: nn.Module,
    loader: DataLoader,
    device: str,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Extract avgpool features from frozen model via forward hook."""
    model.eval()
    hook_outputs = []

    def _hook(module, input, output):
        # avgpool output: (B, 2048, 1, 1) -> flatten to (B, 2048)
        hook_outputs.append(output.squeeze(-1).squeeze(-1).detach().cpu())

    handle = model.avgpool.register_forward_hook(_hook)

    core_labels = []
    spurious_labels = []

    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            model(images)
            core_labels.append(batch["core_label"].numpy())
            spurious_labels.append(batch["spurious_label"].numpy())

    handle.remove()

    features = torch.cat(hook_outputs, dim=0).numpy()
    core_arr = np.concatenate(core_labels)
    spurious_arr = np.concatenate(spurious_labels)
    return features, core_arr, spurious_arr


def fit_probe(
    features: np.ndarray,
    labels: np.ndarray,
    cfg: ProbeConfig,
) -> float:
    """Fit L2 logistic regression probe. Returns accuracy on held-out 20% split."""
    # Split val set 80/20 to avoid trivial in-sample accuracy
    X_tr, X_te, y_tr, y_te = train_test_split(
        features, labels, test_size=0.2, random_state=cfg.random_state,
        stratify=labels if len(np.unique(labels)) > 1 else None,
    )
    probe = LogisticRegression(
        C=cfg.C,
        max_iter=cfg.max_iter,
        solver=cfg.solver,
        random_state=cfg.random_state,
    )
    probe.fit(X_tr, y_tr)
    return float(probe.score(X_te, y_te))


def run_probe_battery(
    cfg: ExperimentConfig,
    seed: int,
    device: str,
) -> pd.DataFrame:
    """Per-checkpoint loop: load -> extract -> probe x2 -> delta -> discard."""
    if cfg.train.dataset == "waterbirds":
        val_loader = get_waterbirds_loader(
            cfg.train.data_root, "val", cfg.train.batch_size,
            cfg.train.num_workers, augment=False
        )
    else:
        val_loader = get_celeba_loader(
            cfg.train.data_root, "val", cfg.train.batch_size,
            cfg.train.num_workers, augment=False
        )

    model = build_model().to(device)
    ckpt_dir = os.path.join(cfg.train.checkpoint_dir, f"seed_{seed}")

    checkpoint_epochs = list(range(
        cfg.train.checkpoint_interval,
        cfg.train.epochs + 1,
        cfg.train.checkpoint_interval,
    ))

    records = []
    for t in checkpoint_epochs:
        ckpt_path = os.path.join(ckpt_dir, f"epoch_{t:03d}.pt")
        if not os.path.exists(ckpt_path):
            continue
        state = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(state)

        feats, core_lbls, spur_lbls = extract_features(model, val_loader, device)
        spur_acc = fit_probe(feats, spur_lbls, cfg.probe)
        core_acc = fit_probe(feats, core_lbls, cfg.probe)
        delta = spur_acc - core_acc
        del feats

        records.append({
            "epoch": t,
            "spurious_acc": spur_acc,
            "core_acc": core_acc,
            "delta": delta,
        })

    return pd.DataFrame(records)


def run_all_seeds(
    cfg: ExperimentConfig,
    device: str,
) -> pd.DataFrame:
    """Multi-seed orchestration. Returns combined DataFrame with seed column."""
    results = []
    for seed in cfg.train.seeds:
        print(f"  Probing seed {seed}...")
        df_seed = run_probe_battery(cfg, seed, device)
        df_seed["seed"] = seed
        results.append(df_seed)
    return pd.concat(results, ignore_index=True)
