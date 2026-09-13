"""Simple neural network classifier for calibration PoC.

For EXISTENCE hypothesis, we use a simple MLP instead of Tree-LSTM
to validate the calibration methodology quickly.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleClassifier(nn.Module):
    """Simple MLP for pairwise comparison."""

    def __init__(self, input_dim=10, hidden_dim=64, num_classes=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        """
        Args:
            x: [B, input_dim]
        Returns:
            logits: [B, num_classes]
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        logits = self.fc3(x)
        return logits


def train_epoch(model, train_loader, optimizer, device='cuda'):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0

    criterion = nn.CrossEntropyLoss()

    for features, labels in train_loader:
        features = features.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        logits = model(features)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        pred = logits.argmax(dim=1)
        correct += (pred == labels).sum().item()
        total += labels.size(0)

    avg_loss = total_loss / len(train_loader)
    accuracy = correct / total
    return avg_loss, accuracy


def validate_epoch(model, val_loader, device='cuda'):
    """Validate and return loss, accuracy, logits, labels."""
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0

    all_logits = []
    all_labels = []

    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for features, labels in val_loader:
            features = features.to(device)
            labels = labels.to(device)

            logits = model(features)
            loss = criterion(logits, labels)

            total_loss += loss.item()
            pred = logits.argmax(dim=1)
            correct += (pred == labels).sum().item()
            total += labels.size(0)

            all_logits.append(logits.cpu())
            all_labels.append(labels.cpu())

    avg_loss = total_loss / len(val_loader)
    accuracy = correct / total
    all_logits = torch.cat(all_logits, dim=0)
    all_labels = torch.cat(all_labels, dim=0)

    return avg_loss, accuracy, all_logits, all_labels


def train_fold(
    model,
    train_loader,
    val_loader,
    max_epochs=50,
    patience=10,
    lr=1e-3,
    device='cuda'
):
    """Train model on single fold with early stopping."""
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)

    best_val_loss = float('inf')
    epochs_no_improve = 0
    best_model_state = None

    history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }

    for epoch in range(max_epochs):
        train_loss, train_acc = train_epoch(model, train_loader, optimizer, device)
        val_loss, val_acc, _, _ = validate_epoch(model, val_loader, device)

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        if (epoch + 1) % 5 == 0:
            print(f"  Epoch {epoch+1}/{max_epochs}: "
                  f"train_loss={train_loss:.4f}, train_acc={train_acc:.3f}, "
                  f"val_loss={val_loss:.4f}, val_acc={val_acc:.3f}")

        # Early stopping
        if val_loss < best_val_loss - 1e-4:
            best_val_loss = val_loss
            epochs_no_improve = 0
            best_model_state = model.state_dict().copy()
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"  Early stopping at epoch {epoch+1}")
                break

    # Restore best model
    if best_model_state is not None:
        model.load_state_dict(best_model_state)

    return model, history
