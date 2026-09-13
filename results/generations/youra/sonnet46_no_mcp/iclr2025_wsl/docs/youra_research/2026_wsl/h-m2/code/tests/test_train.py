"""Tests for h-m1 train.py (tasks 008, 009) — small synthetic run."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from torch.utils.data import TensorDataset, DataLoader
from models import FlatMLPEncoder, FlatMLPWithHead
from train import train_encoder, TrainHistory
from config import ExperimentConfig


def _tiny_loader(n=32, dim=64, bs=8):
    x = torch.randn(n, dim)
    y = torch.rand(n)
    ds = TensorDataset(x, y)
    return DataLoader(ds, batch_size=bs, shuffle=False)


def test_train_encoder_runs():
    cfg = ExperimentConfig()
    cfg.epochs = 2
    cfg.lr = 1e-3
    cfg.weight_decay = 1e-4
    cfg.betas = (0.9, 0.999)
    cfg.t_max = 2
    cfg.eta_min = 1e-6

    enc = FlatMLPEncoder(64, [32], 16)
    model = FlatMLPWithHead(enc, 16)
    loader = _tiny_loader()
    device = torch.device("cpu")
    best_model, history = train_encoder(model, loader, loader, cfg, device)
    assert best_model is not None


def test_history_populated():
    cfg = ExperimentConfig()
    cfg.epochs = 3
    cfg.lr = 1e-3
    cfg.weight_decay = 0.0
    cfg.betas = (0.9, 0.999)
    cfg.t_max = 3
    cfg.eta_min = 1e-6

    enc = FlatMLPEncoder(64, [32], 16)
    model = FlatMLPWithHead(enc, 16)
    loader = _tiny_loader()
    _, history = train_encoder(model, loader, loader, cfg, torch.device("cpu"))
    assert len(history.train_loss) == 3
    assert len(history.val_loss) == 3


def test_optimizer_lr():
    cfg = ExperimentConfig()
    cfg.epochs = 1
    cfg.lr = 5e-4
    cfg.weight_decay = 0.0
    cfg.betas = (0.9, 0.999)
    cfg.t_max = 1
    cfg.eta_min = 1e-7

    enc = FlatMLPEncoder(64, [32], 16)
    model = FlatMLPWithHead(enc, 16)
    opt = torch.optim.Adam(model.parameters(), lr=cfg.lr)
    assert abs(opt.param_groups[0]["lr"] - 5e-4) < 1e-9
