import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets, transforms
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)


# Simple MLP for MNIST
class SimpleMLP(nn.Module):
    def __init__(self, hidden_size=128):
        super().__init__()
        self.fc1 = nn.Linear(784, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 10)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        return self.fc3(x)


def extract_weight_features(model):
    """Extract statistical features from model weights."""
    features = []
    for name, param in model.named_parameters():
        if "weight" in name:
            w = param.detach().cpu().numpy().flatten()
            features.extend(
                [
                    np.mean(w),
                    np.std(w),
                    np.linalg.norm(w),
                    np.min(w),
                    np.max(w),
                    np.percentile(w, 25),
                    np.percentile(w, 75),
                ]
            )
    return np.array(features, dtype=np.float32)


def train_and_collect_checkpoints(
    hidden_size, lr, num_epochs=20, checkpoint_interval=1
):
    """Train an MLP and collect checkpoints."""
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
    )
    train_dataset = datasets.MNIST(
        "./data", train=True, download=True, transform=transform
    )
    test_dataset = datasets.MNIST("./data", train=False, transform=transform)

    # Use subset for speed
    train_subset = torch.utils.data.Subset(train_dataset, range(5000))
    test_subset = torch.utils.data.Subset(test_dataset, range(1000))

    train_loader = DataLoader(train_subset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_subset, batch_size=256)

    model = SimpleMLP(hidden_size).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    checkpoints = []

    for epoch in range(num_epochs):
        model.train()
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

        if epoch % checkpoint_interval == 0:
            checkpoints.append(extract_weight_features(model))

    # Final test accuracy
    model.eval()
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1)
            correct += pred.eq(target).sum().item()

    final_accuracy = correct / len(test_subset)
    return checkpoints, final_accuracy


# Generate training trajectories
print("Generating training trajectories...")
trajectories = []
final_accuracies = []

# Different hyperparameter combinations
hidden_sizes = [32, 64, 128, 256]
learning_rates = [0.0001, 0.0005, 0.001, 0.005, 0.01]

num_trajectories = 40
configs = [(hs, lr) for hs in hidden_sizes for lr in learning_rates][:num_trajectories]

for i, (hs, lr) in enumerate(configs):
    print(f"Training trajectory {i+1}/{len(configs)}: hidden_size={hs}, lr={lr}")
    checkpoints, acc = train_and_collect_checkpoints(hs, lr, num_epochs=20)
    trajectories.append(checkpoints)
    final_accuracies.append(acc)
    print(f"  Final accuracy: {acc:.4f}")

# Normalize and pad trajectories
max_len = max(len(t) for t in trajectories)
feature_dim = trajectories[0][0].shape[0]

# Pad trajectories and create masks
padded_trajectories = np.zeros(
    (len(trajectories), max_len, feature_dim), dtype=np.float32
)
for i, t in enumerate(trajectories):
    for j, cp in enumerate(t):
        padded_trajectories[i, j] = cp

# Normalize features
mean = padded_trajectories.mean(axis=(0, 1), keepdims=True)
std = padded_trajectories.std(axis=(0, 1), keepdims=True) + 1e-8
padded_trajectories = (padded_trajectories - mean) / std

final_accuracies = np.array(final_accuracies, dtype=np.float32)


# CTF Model: LSTM that processes checkpoint sequences
class CTFModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers, batch_first=True, dropout=0.1
        )
        self.fc = nn.Sequential(nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Linear(32, 1))

    def forward(self, x, seq_len=None):
        # x: (batch, seq_len, feature_dim)
        lstm_out, (h_n, c_n) = self.lstm(x)
        # Use last hidden state
        if seq_len is not None:
            # Get output at seq_len position
            batch_size = x.size(0)
            last_outputs = []
            for i in range(batch_size):
                last_outputs.append(lstm_out[i, seq_len - 1])
            last_output = torch.stack(last_outputs)
        else:
            last_output = lstm_out[:, -1, :]
        return self.fc(last_output).squeeze(-1)


# Split data
n_train = int(0.7 * len(trajectories))
n_val = int(0.15 * len(trajectories))

indices = np.random.permutation(len(trajectories))
train_idx = indices[:n_train]
val_idx = indices[n_train : n_train + n_val]
test_idx = indices[n_train + n_val :]

X_train = torch.tensor(padded_trajectories[train_idx])
y_train = torch.tensor(final_accuracies[train_idx])
X_val = torch.tensor(padded_trajectories[val_idx])
y_val = torch.tensor(final_accuracies[val_idx])
X_test = torch.tensor(padded_trajectories[test_idx])
y_test = torch.tensor(final_accuracies[test_idx])

# Use only first 20% of checkpoints for prediction
early_fraction = 0.2
early_len = max(1, int(max_len * early_fraction))
print(f"\nUsing first {early_len} checkpoints (out of {max_len}) for prediction")

X_train_early = X_train[:, :early_len, :]
X_val_early = X_val[:, :early_len, :]
X_test_early = X_test[:, :early_len, :]

# Training
model = CTFModel(input_dim=feature_dim, hidden_dim=64, num_layers=2).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

experiment_data = {
    "ctf_mnist": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "epochs": [],
    }
}

num_epochs = 100
best_val_loss = float("inf")
best_model_state = None

print("\nTraining CTF model...")
for epoch in range(num_epochs):
    model.train()
    X_batch = X_train_early.to(device)
    y_batch = y_train.to(device)

    optimizer.zero_grad()
    predictions = model(X_batch, seq_len=early_len)
    loss = criterion(predictions, y_batch)
    loss.backward()
    optimizer.step()

    train_loss = loss.item()

    # Validation
    model.eval()
    with torch.no_grad():
        X_val_batch = X_val_early.to(device)
        y_val_batch = y_val.to(device)
        val_predictions = model(X_val_batch, seq_len=early_len)
        val_loss = criterion(val_predictions, y_val_batch).item()

        # Compute correlation on validation
        if len(y_val) > 2:
            val_corr, _ = pearsonr(val_predictions.cpu().numpy(), y_val.numpy())
        else:
            val_corr = 0.0

    experiment_data["ctf_mnist"]["losses"]["train"].append(train_loss)
    experiment_data["ctf_mnist"]["losses"]["val"].append(val_loss)
    experiment_data["ctf_mnist"]["metrics"]["val"].append(
        val_corr if not np.isnan(val_corr) else 0.0
    )
    experiment_data["ctf_mnist"]["epochs"].append(epoch)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_model_state = model.state_dict().copy()

    if epoch % 10 == 0:
        print(
            f"Epoch {epoch}: validation_loss = {val_loss:.4f}, val_correlation = {val_corr:.4f}"
        )

# Load best model and evaluate on test set
model.load_state_dict(best_model_state)
model.eval()

with torch.no_grad():
    X_test_batch = X_test_early.to(device)
    test_predictions = model(X_test_batch, seq_len=early_len).cpu().numpy()
    test_actual = y_test.numpy()

# Compute forecast correlation
if len(test_actual) > 2:
    forecast_correlation, p_value = pearsonr(test_predictions, test_actual)
else:
    forecast_correlation = 0.0
    p_value = 1.0

print(f"\n{'='*50}")
print(f"FINAL RESULTS")
print(f"{'='*50}")
print(f"forecast_correlation = {forecast_correlation:.4f}")
print(f"p-value = {p_value:.4f}")
print(f"Test samples: {len(test_actual)}")
print(f"Predicted range: [{test_predictions.min():.4f}, {test_predictions.max():.4f}]")
print(f"Actual range: [{test_actual.min():.4f}, {test_actual.max():.4f}]")

experiment_data["ctf_mnist"]["predictions"] = test_predictions.tolist()
experiment_data["ctf_mnist"]["ground_truth"] = test_actual.tolist()
experiment_data["ctf_mnist"]["forecast_correlation"] = forecast_correlation
experiment_data["ctf_mnist"]["final_accuracies"] = final_accuracies.tolist()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Training and validation loss
axes[0].plot(experiment_data["ctf_mnist"]["losses"]["train"], label="Train Loss")
axes[0].plot(experiment_data["ctf_mnist"]["losses"]["val"], label="Val Loss")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss (MSE)")
axes[0].set_title("Training Progress")
axes[0].legend()
axes[0].grid(True)

# Plot 2: Predicted vs Actual accuracy
axes[1].scatter(test_actual, test_predictions, alpha=0.7)
axes[1].plot(
    [test_actual.min(), test_actual.max()],
    [test_actual.min(), test_actual.max()],
    "r--",
    label="Perfect prediction",
)
axes[1].set_xlabel("Actual Final Accuracy")
axes[1].set_ylabel("Predicted Final Accuracy")
axes[1].set_title(f"CTF Predictions (corr={forecast_correlation:.3f})")
axes[1].legend()
axes[1].grid(True)

# Plot 3: Distribution of final accuracies
axes[2].hist(final_accuracies, bins=15, edgecolor="black", alpha=0.7)
axes[2].set_xlabel("Final Test Accuracy")
axes[2].set_ylabel("Count")
axes[2].set_title("Distribution of Final Accuracies")
axes[2].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ctf_results.png"), dpi=150)
plt.close()

print(f"\nResults saved to {working_dir}")
print(f"forecast_correlation = {forecast_correlation:.4f}")
