"""Debug: check onset delay distribution."""
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
loaders = get_dataloaders(
    cfg.data_root, cfg.batch_size, cfg.num_workers,
    cfg.img_size, cfg.norm_mean, cfg.norm_std
)

train_dataset = WaterbirdsDataset(cfg.data_root, "train", transform=None)
n_train = len(train_dataset)
minority_mask = is_minority(train_dataset.y, train_dataset.place)

print(f"N={n_train}, minority={minority_mask.sum()}")

model = build_resnet18(cfg.num_classes, cfg.pretrained)
tracker = OnsetDelayTracker(n_train, cfg.n_epochs, cfg.onset_threshold)

print(f"Training {cfg.n_epochs} epochs...")
tracker = train_erm(
    model, loaders, tracker,
    cfg.n_epochs, cfg.lr, cfg.momentum, cfg.weight_decay, cfg.device
)

d_i = tracker.get_onset_delays()
print(f"\nd_i stats:")
print(f"  min={d_i.min()}, max={d_i.max()}, mean={d_i[d_i>=0].mean():.1f}")
print(f"  d_i=-1 (never onset): {(d_i==-1).sum()}")
print(f"  d_i>T_early({cfg.t_early}): {(d_i>cfg.t_early).sum()}")

print(f"\nBy group:")
print(f"  Majority: min={d_i[~minority_mask].min()}, max={d_i[~minority_mask].max()}, mean={d_i[~minority_mask][d_i[~minority_mask]>=0].mean():.1f}")
print(f"  Minority: min={d_i[minority_mask].min()}, max={d_i[minority_mask].max()}, mean={d_i[minority_mask][d_i[minority_mask]>=0].mean():.1f}")

# Check first few epochs of loss matrix
loss_mat = tracker.get_loss_history()
print(f"\nLoss matrix shape: {loss_mat.shape}")
print(f"Epoch 0 loss: mean={np.nanmean(loss_mat[:,0]):.4f}, min={np.nanmin(loss_mat[:,0]):.4f}, max={np.nanmax(loss_mat[:,0]):.4f}")
print(f"Epoch 1 loss: mean={np.nanmean(loss_mat[:,1]):.4f}")
print(f"Epoch 5 loss: mean={np.nanmean(loss_mat[:,5]):.4f}")
print(f"Epoch 10 loss: mean={np.nanmean(loss_mat[:,10]):.4f}")
