import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds for reproducibility
np.random.seed(42)
torch.manual_seed(42)

# Experiment data tracking
experiment_data = {
    "uncertainty_classification": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "per_class_accuracy": [],
    }
}

# Define uncertainty types
UNCERTAINTY_TYPES = {
    0: "factual_knowledge_gap",
    1: "reasoning_path_ambiguity",
    2: "query_underspecification",
    3: "temporal_contextual_limitation",
}


def generate_synthetic_data(n_samples_per_class=500, feature_dim=256):
    """
    Generate synthetic hidden state features with distinct patterns for each uncertainty type.
    Each type has characteristic signatures that simulates what we'd expect from real LLM internals.
    """
    all_features = []
    all_labels = []

    for class_idx in range(4):
        # Base features with class-specific patterns
        features = np.random.randn(n_samples_per_class, feature_dim) * 0.5

        if (
            class_idx == 0
        ):  # Factual knowledge gap - low activation in knowledge-related dims
            features[:, :64] *= 0.2  # Weak activation in "knowledge" dimensions
            features[:, 64:128] += np.random.randn(n_samples_per_class, 64) * 0.8
            features[:, 200:220] += 1.5  # High uncertainty signal

        elif (
            class_idx == 1
        ):  # Reasoning path ambiguity - multiple competing activations
            features[:, 50:100] += np.sin(np.linspace(0, 4 * np.pi, 50)) * 1.2
            features[:, 100:150] += np.cos(np.linspace(0, 4 * np.pi, 50)) * 1.2
            features[:, 150:180] += (
                np.random.choice([-1, 1], (n_samples_per_class, 30)) * 0.8
            )

        elif class_idx == 2:  # Query underspecification - sparse, diffuse activations
            sparse_mask = np.random.binomial(1, 0.3, (n_samples_per_class, feature_dim))
            features *= sparse_mask
            features[:, 180:200] += 2.0  # Ambiguity detector signal

        elif (
            class_idx == 3
        ):  # Temporal/contextual limitation - specific temporal markers
            features[:, :30] += 1.8  # Temporal awareness dimensions
            features[:, 220:256] += np.linspace(0, 2, 36)  # Time-sensitive gradient
            features[:, 128:160] *= 0.3  # Low general knowledge activation

        all_features.append(features)
        all_labels.extend([class_idx] * n_samples_per_class)

    X = np.vstack(all_features).astype(np.float32)
    y = np.array(all_labels, dtype=np.int64)

    # Normalize features
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)

    return X, y


class UncertaintyProbe(nn.Module):
    """Lightweight MLP probe for uncertainty type classification."""

    def __init__(self, input_dim=256, hidden_dim=128, num_classes=4, dropout=0.3):
        super(UncertaintyProbe, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes),
        )

    def forward(self, x):
        return self.network(x)


def train_epoch(model, dataloader, criterion, optimizer, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for features, labels in dataloader:
        features = features.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(features)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()

    return total_loss / len(dataloader), correct / total


def evaluate(model, dataloader, criterion, device):
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for features, labels in dataloader:
            features = features.to(device)
            labels = labels.to(device)

            outputs = model(features)
            loss = criterion(outputs, labels)

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    accuracy = accuracy_score(all_labels, all_preds)
    return (
        total_loss / len(dataloader),
        accuracy,
        np.array(all_preds),
        np.array(all_labels),
    )


# Generate synthetic data
print("Generating synthetic uncertainty-labeled data...")
X, y = generate_synthetic_data(n_samples_per_class=500, feature_dim=256)
print(f"Total samples: {len(y)}, Feature dimension: {X.shape[1]}")
print(f"Class distribution: {np.bincount(y)}")

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

print(f"Train: {len(y_train)}, Val: {len(y_val)}, Test: {len(y_test)}")

# Create DataLoaders
train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.LongTensor(y_train))
val_dataset = TensorDataset(torch.FloatTensor(X_val), torch.LongTensor(y_val))
test_dataset = TensorDataset(torch.FloatTensor(X_test), torch.LongTensor(y_test))

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Initialize model, loss, optimizer
model = UncertaintyProbe(input_dim=256, hidden_dim=128, num_classes=4, dropout=0.3).to(
    device
)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", patience=5, factor=0.5
)

# Training loop
num_epochs = 50
best_val_acc = 0
best_model_state = None

print("\nTraining Uncertainty Probe...")
print("-" * 60)

for epoch in range(num_epochs):
    train_loss, train_acc = train_epoch(
        model, train_loader, criterion, optimizer, device
    )
    val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)

    scheduler.step(val_loss)

    experiment_data["uncertainty_classification"]["losses"]["train"].append(train_loss)
    experiment_data["uncertainty_classification"]["losses"]["val"].append(val_loss)
    experiment_data["uncertainty_classification"]["metrics"]["train"].append(train_acc)
    experiment_data["uncertainty_classification"]["metrics"]["val"].append(val_acc)

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        best_model_state = model.state_dict().copy()

    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(
            f"Epoch {epoch+1:3d}: train_loss = {train_loss:.4f}, train_acc = {train_acc:.4f}, "
            f"validation_loss = {val_loss:.4f}, val_acc = {val_acc:.4f}"
        )

# Load best model and evaluate on test set
model.load_state_dict(best_model_state)
test_loss, test_acc, test_preds, test_labels = evaluate(
    model, test_loader, criterion, device
)

experiment_data["uncertainty_classification"]["predictions"] = test_preds.tolist()
experiment_data["uncertainty_classification"]["ground_truth"] = test_labels.tolist()

print("\n" + "=" * 60)
print("FINAL TEST RESULTS")
print("=" * 60)
print(f"\nuncertainty_type_classification_accuracy = {test_acc:.4f}")
print(f"\nClassification Report:")
print(
    classification_report(
        test_labels, test_preds, target_names=[UNCERTAINTY_TYPES[i] for i in range(4)]
    )
)

# Per-class accuracy
conf_matrix = confusion_matrix(test_labels, test_preds)
per_class_acc = conf_matrix.diagonal() / conf_matrix.sum(axis=1)
experiment_data["uncertainty_classification"][
    "per_class_accuracy"
] = per_class_acc.tolist()

print("\nPer-class accuracy:")
for i, acc in enumerate(per_class_acc):
    print(f"  {UNCERTAINTY_TYPES[i]}: {acc:.4f}")

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Visualization: Training curves
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

epochs = range(1, num_epochs + 1)
axes[0].plot(
    epochs,
    experiment_data["uncertainty_classification"]["losses"]["train"],
    label="Train",
)
axes[0].plot(
    epochs,
    experiment_data["uncertainty_classification"]["losses"]["val"],
    label="Validation",
)
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss")
axes[0].set_title("Training and Validation Loss")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(
    epochs,
    experiment_data["uncertainty_classification"]["metrics"]["train"],
    label="Train",
)
axes[1].plot(
    epochs,
    experiment_data["uncertainty_classification"]["metrics"]["val"],
    label="Validation",
)
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy")
axes[1].set_title("Training and Validation Accuracy")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "training_curves.png"), dpi=150)
plt.close()

# Visualization: Confusion matrix
fig, ax = plt.subplots(figsize=(8, 6))
im = ax.imshow(conf_matrix, cmap="Blues")
ax.set_xticks(range(4))
ax.set_yticks(range(4))
ax.set_xticklabels(
    [UNCERTAINTY_TYPES[i][:12] for i in range(4)], rotation=45, ha="right"
)
ax.set_yticklabels([UNCERTAINTY_TYPES[i][:12] for i in range(4)])
ax.set_xlabel("Predicted")
ax.set_ylabel("True")
ax.set_title("Confusion Matrix - Uncertainty Type Classification")

# Add text annotations
for i in range(4):
    for j in range(4):
        text = ax.text(
            j,
            i,
            conf_matrix[i, j],
            ha="center",
            va="center",
            color="white" if conf_matrix[i, j] > conf_matrix.max() / 2 else "black",
        )

plt.colorbar(im)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "confusion_matrix.png"), dpi=150)
plt.close()

# Visualization: Per-class accuracy bar chart
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(
    range(4), per_class_acc, color=["#2ecc71", "#3498db", "#e74c3c", "#f39c12"]
)
ax.set_xticks(range(4))
ax.set_xticklabels([UNCERTAINTY_TYPES[i].replace("_", "\n") for i in range(4)])
ax.set_ylabel("Accuracy")
ax.set_title("Per-Class Accuracy for Uncertainty Type Classification")
ax.set_ylim(0, 1)
ax.axhline(y=test_acc, color="r", linestyle="--", label=f"Overall: {test_acc:.3f}")
ax.legend()

for bar, acc in zip(bars, per_class_acc):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{acc:.3f}",
        ha="center",
        va="bottom",
    )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "per_class_accuracy.png"), dpi=150)
plt.close()

print(f"\nPlots saved to {working_dir}")
print("\n" + "=" * 60)
print(f"FINAL METRIC: uncertainty_type_classification_accuracy = {test_acc:.4f}")
print("=" * 60)
