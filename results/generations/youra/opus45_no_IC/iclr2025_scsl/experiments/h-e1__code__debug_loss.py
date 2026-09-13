"""Debug loss distribution at different epochs."""
import numpy as np
import torch
from config import Config
from data import download_waterbirds, get_dataloaders, is_minority, WaterbirdsDataset
from model import build_resnet18, OnsetDelayTracker
from train import set_seed, train_erm

cfg = Config()
set_seed(cfg.seed)

print("Loading data...")
download_waterbirds(cfg.data_root, cfg.data_url)
loaders = get_dataloaders(cfg.data_root, cfg.batch_size, cfg.num_workers,
                          cfg.img_size, cfg.norm_mean, cfg.norm_std)

train_dataset = WaterbirdsDataset(cfg.data_root, "train", transform=None)
n_train = len(train_dataset)
minority_mask = is_minority(train_dataset.y, train_dataset.place)

print(f"N={n_train}, minority={minority_mask.sum()} ({100*minority_mask.mean():.1f}%)")

model = build_resnet18(cfg.num_classes, cfg.pretrained)
tracker = OnsetDelayTracker(n_train, cfg.n_epochs, cfg.onset_threshold)

print(f"Training {cfg.n_epochs} epochs...")
tracker = train_erm(model, loaders, tracker, cfg.n_epochs, cfg.lr, cfg.momentum, cfg.weight_decay, cfg.device)

loss_mat = tracker.get_loss_history()

for T in [5, 10, 15, 20, 30, 50]:
    loss_T = loss_mat[:, T]
    valid = ~np.isnan(loss_T)

    minority_loss = loss_T[minority_mask & valid]
    majority_loss = loss_T[~minority_mask & valid]

    print(f"\nEpoch {T}:")
    print(f"  Majority: mean={majority_loss.mean():.6f}, median={np.median(majority_loss):.6f}")
    print(f"  Minority: mean={minority_loss.mean():.6f}, median={np.median(minority_loss):.6f}")

    for p in [80, 85, 90, 95]:
        thresh = np.percentile(loss_T[valid], p)
        pred = loss_T[valid] > thresh
        n_pred = pred.sum()

        true_minority = minority_mask[valid]
        tp = (pred & true_minority).sum()
        fp = (pred & ~true_minority).sum()
        fn = (~pred & true_minority).sum()

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        print(f"  P{p}: thresh={thresh:.6f}, pred={n_pred}, prec={precision:.3f}, recall={recall:.3f}")
