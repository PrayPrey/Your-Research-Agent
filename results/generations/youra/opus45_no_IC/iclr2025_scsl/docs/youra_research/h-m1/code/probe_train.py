"""Probe training and evaluation for H-M1."""
import torch
import torch.nn as nn
from torch.optim import SGD
from sklearn.metrics import accuracy_score
from tqdm import tqdm

from probe_model import load_frozen_backbone, LinearProbeAnalysis


def train_probe(
    probe: nn.Linear,
    backbone: nn.Module,
    loader,
    label_idx: int,
    epochs: int,
    lr: float,
    device: str,
) -> nn.Linear:
    probe = probe.to(device)
    optimizer = SGD(probe.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    analyzer = LinearProbeAnalysis(backbone)

    for epoch in range(epochs):
        probe.train()
        for batch in loader:
            imgs = batch[0].to(device)
            labels = batch[label_idx].to(device)
            feats = analyzer.extract_features(imgs)
            logits = probe(feats)
            loss = criterion(logits, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    return probe


def eval_probe(
    probe: nn.Linear,
    backbone: nn.Module,
    loader,
    label_idx: int,
    device: str,
) -> float:
    probe.eval()
    analyzer = LinearProbeAnalysis(backbone)
    all_preds, all_labels = [], []

    with torch.no_grad():
        for batch in loader:
            imgs = batch[0].to(device)
            labels = batch[label_idx]
            feats = analyzer.extract_features(imgs)
            logits = probe(feats)
            preds = logits.argmax(dim=1).cpu()
            all_preds.extend(preds.tolist())
            all_labels.extend(labels.tolist())

    return accuracy_score(all_labels, all_preds)


def run_probes_for_checkpoint(
    ckpt_path: str,
    loaders: dict,
    feature_dim: int,
    probe_epochs: int,
    lr: float,
    device: str,
) -> dict:
    backbone = load_frozen_backbone(ckpt_path, device=device)

    spurious_probe = nn.Linear(feature_dim, 2)
    spurious_probe = train_probe(spurious_probe, backbone, loaders["train"], label_idx=2, epochs=probe_epochs, lr=lr, device=device)
    spurious_acc = eval_probe(spurious_probe, backbone, loaders["test"], label_idx=2, device=device)

    core_probe = nn.Linear(feature_dim, 2)
    core_probe = train_probe(core_probe, backbone, loaders["train"], label_idx=1, epochs=probe_epochs, lr=lr, device=device)
    core_acc = eval_probe(core_probe, backbone, loaders["test"], label_idx=1, device=device)

    return {"spurious_acc": spurious_acc, "core_acc": core_acc}
