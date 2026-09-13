"""Training loop for adversarial probing."""
import torch
import torch.nn as nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, TensorDataset
import math

from grl import grl_alpha_schedule
from probes import AdversarialProber, BaselineRewardProbe


def train_adversarial_probe(
    prober: AdversarialProber,
    h_train: torch.Tensor,
    bai_labels: torch.Tensor,
    reward_labels: torch.Tensor,
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 1e-4,
    loss_lambda: float = 1.0,
    device: str = "cuda",
):
    """Train adversarial prober with GRL alpha schedule."""
    prober = prober.to(device)
    h_train = h_train.to(device)
    bai_labels = bai_labels.float().to(device)
    reward_labels = reward_labels.float().to(device)

    dataset = TensorDataset(h_train, bai_labels, reward_labels)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    opt = AdamW(prober.parameters(), lr=lr, weight_decay=0.01)
    bce = nn.BCEWithLogitsLoss()

    steps_per_epoch = len(loader)
    global_step = 0

    for epoch in range(epochs):
        prober.train()
        epoch_loss = 0.0

        for h_b, bai_b, rew_b in loader:
            alpha = grl_alpha_schedule(global_step, steps_per_epoch)
            prober.set_alpha(alpha)

            bai_logits, reward_logits = prober(h_b)
            bai_loss = bce(bai_logits, bai_b)
            reward_loss = bce(reward_logits, rew_b)
            loss = bai_loss + loss_lambda * reward_loss

            opt.zero_grad()
            loss.backward()
            opt.step()

            epoch_loss += loss.item()
            global_step += 1

        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(loader):.4f}, Alpha: {alpha:.3f}")

    return prober


def train_baseline_reward_probe(
    hidden_dim: int,
    h_train: torch.Tensor,
    reward_labels: torch.Tensor,
    epochs: int = 3,
    batch_size: int = 32,
    lr: float = 1e-4,
    device: str = "cuda",
):
    """Train baseline reward probe (no GRL) for R² comparison."""
    probe = BaselineRewardProbe(hidden_dim).to(device)
    h_train = h_train.to(device)
    reward_labels = reward_labels.float().to(device)

    dataset = TensorDataset(h_train, reward_labels)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    opt = AdamW(probe.parameters(), lr=lr, weight_decay=0.01)
    bce = nn.BCEWithLogitsLoss()

    for epoch in range(epochs):
        probe.train()
        for h_b, rew_b in loader:
            logits = probe(h_b)
            loss = bce(logits, rew_b)
            opt.zero_grad()
            loss.backward()
            opt.step()

    return probe
