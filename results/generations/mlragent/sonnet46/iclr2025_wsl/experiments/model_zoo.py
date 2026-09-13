"""
Model Zoo: Train many small neural networks on CIFAR-10 with varied hyperparameters.
This creates the dataset for weight space learning experiments.

We use a smaller MLP (hidden=32) to keep weight dimensions manageable (~100K).
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader, Subset
import random


DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
HIDDEN_SIZE = 32   # Fixed hidden size for consistent weight dimensions
INPUT_DIM = 32 * 32 * 3   # 3072
OUTPUT_DIM = 10


class SmallMLP(nn.Module):
    """Small 3-layer MLP for weight space experiments."""
    def __init__(self, hidden_size=HIDDEN_SIZE, dropout=0.0):
        super().__init__()
        self.fc1 = nn.Linear(INPUT_DIM, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, OUTPUT_DIM)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.hidden_size = hidden_size

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)
        return x

    def get_weight_vector(self):
        """Flatten all weights into a single vector."""
        weights = []
        for param in self.parameters():
            weights.append(param.data.cpu().flatten())
        return torch.cat(weights)


def compute_weight_dim(hidden_size=HIDDEN_SIZE):
    """Compute total weight dimension."""
    # fc1: (hidden x 3072) + hidden
    # fc2: (hidden x hidden) + hidden
    # fc3: (10 x hidden) + 10
    return (hidden_size * INPUT_DIM + hidden_size +
            hidden_size * hidden_size + hidden_size +
            OUTPUT_DIM * hidden_size + OUTPUT_DIM)


def get_cifar10_loaders(subset_size=5000, test_size=1000, batch_size=128):
    """Load CIFAR-10 with a small subset for fast training."""
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
    ])

    data_dir = "/tmp/cifar10_data"
    train_dataset = datasets.CIFAR10(data_dir, train=True, download=True, transform=transform)
    test_dataset = datasets.CIFAR10(data_dir, train=False, download=True, transform=transform)

    train_indices = list(range(subset_size))
    test_indices = list(range(test_size))

    train_loader = DataLoader(
        Subset(train_dataset, train_indices),
        batch_size=batch_size, shuffle=True, num_workers=2, pin_memory=True
    )
    test_loader = DataLoader(
        Subset(test_dataset, test_indices),
        batch_size=batch_size, shuffle=False, num_workers=2, pin_memory=True
    )
    return train_loader, test_loader


def train_model(model, train_loader, test_loader, lr, weight_decay, num_epochs=15):
    """Train a model and return its test accuracy."""
    model = model.to(DEVICE)
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=weight_decay)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)
    criterion = nn.CrossEntropyLoss()

    train_losses, val_losses = [], []

    for epoch in range(num_epochs):
        model.train()
        total_loss = 0.0
        for x, y in train_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            optimizer.zero_grad()
            loss = criterion(model(x), y)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        train_losses.append(total_loss / len(train_loader))
        scheduler.step()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(DEVICE), y.to(DEVICE)
                val_loss += criterion(model(x), y).item()
        val_losses.append(val_loss / len(test_loader))

    # Final test accuracy
    model.eval()
    correct = total = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            correct += (model(x).argmax(1) == y).sum().item()
            total += y.size(0)

    return correct / total, train_losses, val_losses


def build_model_zoo(num_models=200, save_dir="/tmp/model_zoo"):
    """Train a zoo of models with varied hyperparameters."""
    os.makedirs(save_dir, exist_ok=True)

    train_loader, test_loader = get_cifar10_loaders()

    lr_options = [0.001, 0.003, 0.01, 0.03, 0.05, 0.1]
    wd_options = [0.0, 1e-5, 1e-4, 1e-3, 5e-3]
    dropout_options = [0.0, 0.1, 0.2, 0.3]

    zoo_metadata = []
    weight_vectors = []

    print(f"Training {num_models} models (hidden_size={HIDDEN_SIZE})...")
    print(f"Weight dim per model: {compute_weight_dim()}")

    for i in range(num_models):
        lr = random.choice(lr_options)
        wd = random.choice(wd_options)
        dropout = random.choice(dropout_options)

        torch.manual_seed(i * 42)
        model = SmallMLP(hidden_size=HIDDEN_SIZE, dropout=dropout)

        test_acc, train_losses, val_losses = train_model(
            model, train_loader, test_loader, lr=lr, weight_decay=wd, num_epochs=15
        )

        weight_vec = model.get_weight_vector().numpy()
        weight_vectors.append(weight_vec)

        metadata = {
            "model_id": i,
            "lr": lr,
            "weight_decay": wd,
            "hidden_size": HIDDEN_SIZE,
            "dropout": dropout,
            "test_accuracy": float(test_acc),
            "final_train_loss": float(train_losses[-1]),
            "final_val_loss": float(val_losses[-1]),
        }
        zoo_metadata.append(metadata)

        if (i + 1) % 20 == 0:
            print(f"  [{i+1}/{num_models}] acc={test_acc:.3f}, lr={lr}, dropout={dropout}")

    weight_matrix = np.array(weight_vectors)
    np.save(os.path.join(save_dir, "weights.npy"), weight_matrix)

    with open(os.path.join(save_dir, "metadata.json"), "w") as f:
        json.dump(zoo_metadata, f, indent=2)

    accs = [m["test_accuracy"] for m in zoo_metadata]
    print(f"\nZoo: {num_models} models, weight_dim={weight_matrix.shape[1]}")
    print(f"Accuracy: mean={np.mean(accs):.3f}, std={np.std(accs):.3f}, range=[{np.min(accs):.3f}, {np.max(accs):.3f}]")

    return weight_matrix, zoo_metadata


if __name__ == "__main__":
    build_model_zoo(num_models=200)
