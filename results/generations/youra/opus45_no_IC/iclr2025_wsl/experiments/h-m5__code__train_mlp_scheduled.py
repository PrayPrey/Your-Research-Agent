"""H-M5: MLP training with AdamW + CosineAnnealingLR per PRD FR-3.1/3.2."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from torch.optim.lr_scheduler import CosineAnnealingLR

from mlp_model_wide import MLPMatchedWide


def train_mlp_on_subset(
    train_dataset: TensorDataset,
    input_dim: int,
    seed: int,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    device: str = "cpu",
) -> nn.Module:
    """Train MLPMatchedWide with AdamW + CosineAnnealingLR.

    Returns model in eval mode.
    """
    torch.manual_seed(seed)

    model = MLPMatchedWide(input_dim).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = CosineAnnealingLR(optimizer, T_max=epochs)
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

        scheduler.step()

    model.eval()
    return model


if __name__ == "__main__":
    X = torch.randn(100, 50000)
    y = torch.randn(100, 1)
    ds = TensorDataset(X, y)

    model = train_mlp_on_subset(ds, input_dim=50000, seed=0, epochs=5, device="cpu")
    print(f"Model trained. Output shape: {model(X[:1]).shape}")
