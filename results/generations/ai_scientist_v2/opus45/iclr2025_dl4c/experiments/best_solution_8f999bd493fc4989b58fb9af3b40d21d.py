import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import random
from collections import defaultdict
import json

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# Mutation types
MUTATION_TYPES = ["off_by_one", "wrong_operator", "wrong_variable", "boundary_error"]


def generate_program_pair(mutation_type, program_id):
    """Generate a correct program and its buggy variant with execution traces."""

    # Simple program templates that produce traceable execution
    if program_id % 4 == 0:
        # Sum computation
        n = random.randint(3, 8)
        correct_code = f"""
result = 0
for i in range({n}):
    result = result + i
"""
        if mutation_type == "off_by_one":
            buggy_code = f"""
result = 0
for i in range({n+1}):
    result = result + i
"""
        elif mutation_type == "wrong_operator":
            buggy_code = f"""
result = 0
for i in range({n}):
    result = result * i
"""
        elif mutation_type == "wrong_variable":
            buggy_code = f"""
result = 0
for i in range({n}):
    result = result + result
"""
        else:  # boundary_error
            buggy_code = f"""
result = 0
for i in range(1, {n}):
    result = result + i
"""

    elif program_id % 4 == 1:
        # Factorial-like computation
        n = random.randint(2, 5)
        correct_code = f"""
result = 1
for i in range(1, {n+1}):
    result = result * i
"""
        if mutation_type == "off_by_one":
            buggy_code = f"""
result = 1
for i in range(1, {n}):
    result = result * i
"""
        elif mutation_type == "wrong_operator":
            buggy_code = f"""
result = 1
for i in range(1, {n+1}):
    result = result + i
"""
        elif mutation_type == "wrong_variable":
            buggy_code = f"""
result = 1
for i in range(1, {n+1}):
    result = i * i
"""
        else:  # boundary_error
            buggy_code = f"""
result = 1
for i in range(0, {n+1}):
    result = result * i
"""

    elif program_id % 4 == 2:
        # Counting computation
        n = random.randint(3, 7)
        threshold = random.randint(1, n - 1)
        correct_code = f"""
count = 0
for i in range({n}):
    if i > {threshold}:
        count = count + 1
"""
        if mutation_type == "off_by_one":
            buggy_code = f"""
count = 0
for i in range({n}):
    if i > {threshold+1}:
        count = count + 1
"""
        elif mutation_type == "wrong_operator":
            buggy_code = f"""
count = 0
for i in range({n}):
    if i < {threshold}:
        count = count + 1
"""
        elif mutation_type == "wrong_variable":
            buggy_code = f"""
count = 0
for i in range({n}):
    if i > {threshold}:
        count = i
"""
        else:  # boundary_error
            buggy_code = f"""
count = 0
for i in range({n}):
    if i >= {threshold}:
        count = count + 1
"""

    else:
        # Accumulator with condition
        n = random.randint(3, 6)
        correct_code = f"""
total = 0
prev = 0
for i in range({n}):
    total = total + prev
    prev = i
"""
        if mutation_type == "off_by_one":
            buggy_code = f"""
total = 0
prev = 0
for i in range({n+1}):
    total = total + prev
    prev = i
"""
        elif mutation_type == "wrong_operator":
            buggy_code = f"""
total = 0
prev = 0
for i in range({n}):
    total = total - prev
    prev = i
"""
        elif mutation_type == "wrong_variable":
            buggy_code = f"""
total = 0
prev = 0
for i in range({n}):
    total = total + i
    prev = i
"""
        else:  # boundary_error
            buggy_code = f"""
total = 0
prev = 1
for i in range({n}):
    total = total + prev
    prev = i
"""

    return correct_code, buggy_code


def execute_and_trace(code, max_steps=50):
    """Execute code and extract variable trace."""
    trace = []
    namespace = {}

    try:
        # Simple tracer using exec with step tracking
        lines = [l for l in code.strip().split("\n") if l.strip()]

        # For simplicity, we'll execute and capture state at key points
        exec(code, namespace)

        # Extract final state as simplified trace
        var_state = {}
        for k, v in namespace.items():
            if not k.startswith("_") and isinstance(v, (int, float)):
                var_state[k] = float(v)

        # Create a simple trace representation
        trace = [
            var_state.get("result", var_state.get("count", var_state.get("total", 0)))
        ]

        # Also trace intermediate values by re-executing with instrumentation
        trace = instrument_and_execute(code, max_steps)

    except Exception as e:
        trace = [{"error": str(e)}]

    return trace


def instrument_and_execute(code, max_steps=50):
    """Execute with simple instrumentation to get variable states."""
    trace = []
    namespace = {"__trace__": trace}

    # Add tracing to assignments
    lines = code.strip().split("\n")
    instrumented_lines = []

    for line in lines:
        instrumented_lines.append(line)
        # After each assignment or loop iteration, capture state
        if "=" in line and "for" not in line and "if" not in line:
            var_name = line.split("=")[0].strip()
            instrumented_lines.append(f"__trace__.append({{'{var_name}': {var_name}}})")

    instrumented_code = "\n".join(instrumented_lines)

    try:
        exec(instrumented_code, namespace)
    except:
        pass

    return trace if trace else [{"empty": 0}]


def extract_divergence_features(correct_trace, buggy_trace, max_len=20):
    """Extract divergence pattern features from trace pair."""
    features = []

    # Find divergence point
    divergence_idx = 0
    for i in range(min(len(correct_trace), len(buggy_trace))):
        if correct_trace[i] != buggy_trace[i]:
            divergence_idx = i
            break
        divergence_idx = i + 1

    # Feature: normalized divergence point
    features.append(divergence_idx / max(len(correct_trace), 1))

    # Feature: trace length difference
    features.append(
        (len(buggy_trace) - len(correct_trace)) / max(len(correct_trace), 1)
    )

    # Feature: value differences at divergence
    for i in range(max_len):
        if i < len(correct_trace) and i < len(buggy_trace):
            ct = correct_trace[i]
            bt = buggy_trace[i]

            # Get numeric values from trace dicts
            cv = list(ct.values())[0] if isinstance(ct, dict) and ct else 0
            bv = list(bt.values())[0] if isinstance(bt, dict) and bt else 0

            cv = float(cv) if isinstance(cv, (int, float)) else 0
            bv = float(bv) if isinstance(bv, (int, float)) else 0

            # Normalized difference
            diff = (bv - cv) / (abs(cv) + 1)
            features.append(diff)

            # Ratio feature
            ratio = bv / (cv + 1e-6) if cv != 0 else bv
            features.append(min(max(ratio, -10), 10))
        else:
            features.append(0)
            features.append(0)

    # Pad or truncate to fixed length
    target_len = 2 + max_len * 2
    features = features[:target_len]
    features.extend([0] * (target_len - len(features)))

    return np.array(features, dtype=np.float32)


def generate_dataset(num_samples=1000):
    """Generate dataset of (divergence_features, mutation_type) pairs."""
    data = []

    for i in range(num_samples):
        mutation_idx = i % len(MUTATION_TYPES)
        mutation_type = MUTATION_TYPES[mutation_idx]

        correct_code, buggy_code = generate_program_pair(mutation_type, i)

        correct_trace = instrument_and_execute(correct_code)
        buggy_trace = instrument_and_execute(buggy_code)

        features = extract_divergence_features(correct_trace, buggy_trace)

        data.append(
            {
                "features": features,
                "label": mutation_idx,
                "mutation_type": mutation_type,
            }
        )

    return data


class DivergenceDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            "features": torch.tensor(item["features"], dtype=torch.float32),
            "label": torch.tensor(item["label"], dtype=torch.long),
        }


class DivergenceClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_classes=4):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        self.classifier = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        encoded = self.encoder(x)
        logits = self.classifier(encoded)
        return logits


# Generate data
print("Generating synthetic dataset...")
all_data = generate_dataset(num_samples=2000)
random.shuffle(all_data)

# Split data
train_size = int(0.7 * len(all_data))
val_size = int(0.15 * len(all_data))

train_data = all_data[:train_size]
val_data = all_data[train_size : train_size + val_size]
test_data = all_data[train_size + val_size :]

print(f"Train: {len(train_data)}, Val: {len(val_data)}, Test: {len(test_data)}")

# Create datasets and loaders
train_dataset = DivergenceDataset(train_data)
val_dataset = DivergenceDataset(val_data)
test_dataset = DivergenceDataset(test_data)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Model setup
input_dim = train_data[0]["features"].shape[0]
model = DivergenceClassifier(
    input_dim=input_dim, hidden_dim=128, num_classes=len(MUTATION_TYPES)
)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training tracking
experiment_data = {
    "dapr_baseline": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "epochs": [],
    }
}

num_epochs = 50
best_val_acc = 0

print("\nStarting training...")
for epoch in range(num_epochs):
    # Training
    model.train()
    train_loss = 0
    train_correct = 0
    train_total = 0

    for batch in train_loader:
        features = batch["features"].to(device)
        labels = batch["label"].to(device)

        optimizer.zero_grad()
        logits = model(features)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer.step()

        train_loss += loss.item() * features.size(0)
        _, predicted = torch.max(logits, 1)
        train_correct += (predicted == labels).sum().item()
        train_total += labels.size(0)

    train_loss /= train_total
    train_acc = train_correct / train_total

    # Validation
    model.eval()
    val_loss = 0
    val_correct = 0
    val_total = 0

    with torch.no_grad():
        for batch in val_loader:
            features = batch["features"].to(device)
            labels = batch["label"].to(device)

            logits = model(features)
            loss = criterion(logits, labels)

            val_loss += loss.item() * features.size(0)
            _, predicted = torch.max(logits, 1)
            val_correct += (predicted == labels).sum().item()
            val_total += labels.size(0)

    val_loss /= val_total
    val_acc = val_correct / val_total

    # Track metrics
    experiment_data["dapr_baseline"]["losses"]["train"].append(train_loss)
    experiment_data["dapr_baseline"]["losses"]["val"].append(val_loss)
    experiment_data["dapr_baseline"]["metrics"]["train"].append(train_acc)
    experiment_data["dapr_baseline"]["metrics"]["val"].append(val_acc)
    experiment_data["dapr_baseline"]["epochs"].append(epoch)

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), os.path.join(working_dir, "best_model.pt"))

    if epoch % 5 == 0:
        print(
            f"Epoch {epoch}: train_loss = {train_loss:.4f}, train_acc = {train_acc:.4f}, validation_loss = {val_loss:.4f}, val_acc = {val_acc:.4f}"
        )

# Final evaluation on test set
model.load_state_dict(torch.load(os.path.join(working_dir, "best_model.pt")))
model.eval()

test_correct = 0
test_total = 0
all_predictions = []
all_labels = []

with torch.no_grad():
    for batch in test_loader:
        features = batch["features"].to(device)
        labels = batch["label"].to(device)

        logits = model(features)
        _, predicted = torch.max(logits, 1)

        test_correct += (predicted == labels).sum().item()
        test_total += labels.size(0)

        all_predictions.extend(predicted.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

test_accuracy = test_correct / test_total
experiment_data["dapr_baseline"]["predictions"] = all_predictions
experiment_data["dapr_baseline"]["ground_truth"] = all_labels

print(f"\n{'='*50}")
print(f"Final Test mutation_type_prediction_accuracy: {test_accuracy:.4f}")
print(f"Best Validation Accuracy: {best_val_acc:.4f}")
print(f"{'='*50}")

# Per-class accuracy
print("\nPer-class accuracy:")
for i, mt in enumerate(MUTATION_TYPES):
    class_mask = np.array(all_labels) == i
    class_acc = np.sum((np.array(all_predictions) == i) & class_mask) / np.sum(
        class_mask
    )
    print(f"  {mt}: {class_acc:.4f}")

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Create visualization
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Loss curves
axes[0].plot(
    experiment_data["dapr_baseline"]["epochs"],
    experiment_data["dapr_baseline"]["losses"]["train"],
    label="Train",
)
axes[0].plot(
    experiment_data["dapr_baseline"]["epochs"],
    experiment_data["dapr_baseline"]["losses"]["val"],
    label="Validation",
)
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss")
axes[0].set_title("Training and Validation Loss")
axes[0].legend()
axes[0].grid(True)

# Accuracy curves
axes[1].plot(
    experiment_data["dapr_baseline"]["epochs"],
    experiment_data["dapr_baseline"]["metrics"]["train"],
    label="Train",
)
axes[1].plot(
    experiment_data["dapr_baseline"]["epochs"],
    experiment_data["dapr_baseline"]["metrics"]["val"],
    label="Validation",
)
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy")
axes[1].set_title("Training and Validation Accuracy")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dapr_training_curves.png"), dpi=150)
plt.close()

# Confusion matrix
from sklearn.metrics import confusion_matrix
import seaborn as sns

cm = confusion_matrix(all_labels, all_predictions)
plt.figure(figsize=(8, 6))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=MUTATION_TYPES,
    yticklabels=MUTATION_TYPES,
)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Confusion Matrix - Mutation Type Prediction")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dapr_confusion_matrix.png"), dpi=150)
plt.close()

print(f"\nPlots saved to {working_dir}")
print(f"\nmutation_type_prediction_accuracy: {test_accuracy:.4f}")
