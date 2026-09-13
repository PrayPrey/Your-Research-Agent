"""Probe: LinearProbe + extraction + training (adapted from H-E1)."""

import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import roc_auc_score
from tqdm import tqdm

from hooks import HiddenStateExtractor


class LinearProbe(nn.Module):
    def __init__(self, hidden_dim: int = 4096):
        super().__init__()
        self.classifier = nn.Linear(hidden_dim, 1)

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        logits = self.classifier(hidden_states)
        return torch.sigmoid(logits)


def extract_all_layers(
    model,
    tokenizer,
    layer_indices: list,
    examples: list,
    batch_size: int = 32,
) -> tuple:
    """Forward-pass batches through model w/ HiddenStateExtractor; collect last-token state per layer."""
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    layer_buffers = {idx: [] for idx in layer_indices}
    all_labels = []

    with HiddenStateExtractor(model, layer_indices) as extractor:
        for i in tqdm(range(0, len(examples), batch_size), desc="Extracting hidden states"):
            batch = examples[i:i+batch_size]
            prompts = [e["prompt"] for e in batch]

            enc = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(model.device)

            with torch.no_grad():
                model(**enc)

            for idx in layer_indices:
                h = extractor.hidden_states[idx][:, -1, :].float()
                layer_buffers[idx].append(h)

            all_labels.extend(e["label"] for e in batch)
            extractor.hidden_states.clear()

    states = {idx: torch.cat(layer_buffers[idx], dim=0) for idx in layer_indices}
    labels = torch.tensor(all_labels, dtype=torch.long)
    return states, labels


def train_probe(hidden_states: torch.Tensor, labels: torch.Tensor, cfg) -> tuple:
    """AdamW-trained probe. Returns (probe.cpu(), loss_per_epoch)."""
    probe = LinearProbe(hidden_dim=hidden_states.shape[1])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    probe = probe.to(device)
    hidden_states = hidden_states.to(device)
    labels = labels.float().to(device)

    optimizer = torch.optim.AdamW(probe.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    criterion = nn.BCELoss()

    loss_per_epoch = []
    n_samples = hidden_states.shape[0]

    for epoch in range(cfg.epochs):
        indices = torch.randperm(n_samples, device=device)
        epoch_loss = 0.0
        n_batches = 0

        for i in range(0, n_samples, cfg.batch_size):
            batch_idx = indices[i:i+cfg.batch_size]
            batch_h = hidden_states[batch_idx]
            batch_y = labels[batch_idx]

            optimizer.zero_grad()
            preds = probe(batch_h).squeeze()
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1

        avg_loss = epoch_loss / n_batches
        loss_per_epoch.append(avg_loss)

    return probe.cpu(), loss_per_epoch


def evaluate_auroc(probe, hidden_states: torch.Tensor, labels: torch.Tensor) -> tuple:
    probe.eval()
    with torch.no_grad():
        preds = probe(hidden_states).squeeze().numpy()
    labels_np = labels.numpy()
    auroc = roc_auc_score(labels_np, preds)
    return auroc, preds, labels_np
