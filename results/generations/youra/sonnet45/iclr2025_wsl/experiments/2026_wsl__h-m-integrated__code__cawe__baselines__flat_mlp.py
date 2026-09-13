"""
Flat-Weight MLP Baseline Model.
Naive baseline that concatenates all weights without architecture awareness.
"""
import torch
import torch.nn as nn


class FlatWeightMLP(nn.Module):
    """
    Flat-Weight MLP Baseline.

    Architecture:
        - Flatten all model weights into a single vector
        - Pass through MLP layers
        - Output generalization gap prediction

    Used for baseline comparison (Δρ = ρ_CAWE - ρ_baseline)
    """

    def __init__(self, input_dim: int):
        super().__init__()
        self.input_dim = input_dim

        self.network = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )

    def forward(self, weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through baseline MLP.

        Args:
            weights: Flattened weight vector (input_dim,)

        Returns:
            prediction: Generalization gap prediction (scalar)
        """
        prediction = self.network(weights)
        return prediction.squeeze()


def train_flat_baseline(train_loader, val_loader, lr, weight_decay, epochs, patience, device):
    """Train Flat-Weight MLP baseline.

    Args:
        train_loader: Training data loader
        val_loader: Validation data loader
        lr: Learning rate
        weight_decay: Weight decay for regularization
        epochs: Maximum training epochs
        patience: Early stopping patience
        device: Device to train on

    Returns:
        Trained FlatWeightMLP model
    """
    # Determine input dimension from first batch
    first_batch = next(iter(train_loader))
    weights, _, _ = first_batch
    flat_dim = sum(v[0].numel() for v in weights.values())

    model = FlatWeightMLP(input_dim=flat_dim).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.MSELoss()

    best_val_loss = float('inf')
    patience_counter = 0

    for epoch in range(epochs):
        # Training
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            weights, arch_family_batch, targets = batch

            # Flatten weights for each sample in batch
            batch_size = len(arch_family_batch)
            flat_weights = []
            for i in range(batch_size):
                flat_input = torch.cat([v[i].flatten() for v in weights.values()])
                flat_weights.append(flat_input)
            flat_weights = torch.stack(flat_weights).to(device)
            targets = targets.to(device)

            optimizer.zero_grad()
            predictions = model(flat_weights)
            loss = criterion(predictions, targets)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

        train_loss /= len(train_loader)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                weights, arch_family_batch, targets = batch

                # Flatten weights
                batch_size = len(arch_family_batch)
                flat_weights = []
                for i in range(batch_size):
                    flat_input = torch.cat([v[i].flatten() for v in weights.values()])
                    flat_weights.append(flat_input)
                flat_weights = torch.stack(flat_weights).to(device)
                targets = targets.to(device)

                predictions = model(flat_weights)
                loss = criterion(predictions, targets)
                val_loss += loss.item()

        val_loss /= len(val_loader)

        print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_state = model.state_dict().copy()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch+1}")
                break

    # Load best model
    model.load_state_dict(best_state)
    return model
