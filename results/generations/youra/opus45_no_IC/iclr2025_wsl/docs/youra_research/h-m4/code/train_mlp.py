"""H-M4: MLP training loop."""

import sys
import os

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

H_M3_CODE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "h-m3", "code")
sys.path.insert(0, H_M3_CODE_DIR)

from mlp_model import MLPMatched


def train_mlp_on_subset(
    train_dataset: TensorDataset,
    input_dim: int,
    seed: int,
    epochs: int = 50,
    batch_size: int = 32,
    lr: float = 1e-3,
    device: str = "cpu",
) -> nn.Module:
    """Train MLPMatched on dataset with AdamW/MSE.

    Returns model in eval mode.
    """
    torch.manual_seed(seed)

    model = MLPMatched(input_dim).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    model.train()
    for epoch in range(epochs):
        epoch_loss = 0.0
        for x_batch, y_batch in loader:
            x_batch = x_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()
            pred = model(x_batch)
            loss = loss_fn(pred, y_batch)
            loss.backward()
            optimizer.step()

            epoch_loss += loss.item()

    model.eval()
    return model


if __name__ == "__main__":
    X = torch.randn(100, 32)
    y = torch.randn(100, 1)
    ds = TensorDataset(X, y)

    model = train_mlp_on_subset(ds, input_dim=32, seed=0, epochs=5)
    print(f"Model trained. Output shape: {model(X[:1]).shape}")
