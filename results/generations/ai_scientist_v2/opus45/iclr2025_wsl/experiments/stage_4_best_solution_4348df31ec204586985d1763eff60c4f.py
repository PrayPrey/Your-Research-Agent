import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from scipy.stats import spearmanr, pearsonr
import matplotlib.pyplot as plt
from datasets import load_dataset

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)


# Simple MLP for image classification
class SimpleMLP(nn.Module):
    def __init__(self, input_dim=784, hidden_size=128, num_classes=10):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
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
                    np.abs(w).mean(),  # L1 norm per element
                ]
            )
    return np.array(features, dtype=np.float32)


def load_hf_dataset(name, train_size=5000, test_size=1000):
    """Load dataset from HuggingFace."""
    print(f"Loading {name} from HuggingFace...")

    if name == "mnist":
        ds = load_dataset("ylecun/mnist")
        input_dim = 784
        img_key = "image"
    elif name == "fashion_mnist":
        ds = load_dataset("zalando-datasets/fashion_mnist")
        input_dim = 784
        img_key = "image"
    elif name == "cifar10":
        ds = load_dataset("uoft-cs/cifar10")
        input_dim = 3072
        img_key = "img"
    else:
        raise ValueError(f"Unknown dataset: {name}")

    def process_images(examples, img_key, input_dim):
        images = []
        for img in examples[img_key]:
            img_arr = np.array(img, dtype=np.float32)
            if len(img_arr.shape) == 2:
                img_arr = img_arr / 255.0
            else:
                img_arr = img_arr.transpose(2, 0, 1) / 255.0
            images.append(img_arr.flatten())
        return images

    train_data = ds["train"]
    test_data = ds["test"]

    train_indices = np.random.choice(
        len(train_data), min(train_size, len(train_data)), replace=False
    )
    test_indices = np.random.choice(
        len(test_data), min(test_size, len(test_data)), replace=False
    )

    train_images = process_images(train_data.select(train_indices), img_key, input_dim)
    train_labels = [train_data[int(i)]["label"] for i in train_indices]
    test_images = process_images(test_data.select(test_indices), img_key, input_dim)
    test_labels = [test_data[int(i)]["label"] for i in test_indices]

    X_train = torch.tensor(np.array(train_images), dtype=torch.float32)
    y_train = torch.tensor(train_labels, dtype=torch.long)
    X_test = torch.tensor(np.array(test_images), dtype=torch.float32)
    y_test = torch.tensor(test_labels, dtype=torch.long)

    # Normalize
    mean = X_train.mean()
    std = X_train.std()
    X_train = (X_train - mean) / (std + 1e-8)
    X_test = (X_test - mean) / (std + 1e-8)

    return X_train, y_train, X_test, y_test, input_dim


def train_and_collect_checkpoints(
    X_train,
    y_train,
    X_test,
    y_test,
    input_dim,
    hidden_size,
    lr,
    num_epochs=25,
    weight_decay=0.0,
):
    """Train model and collect checkpoints."""
    train_dataset = TensorDataset(X_train, y_train)
    test_dataset = TensorDataset(X_test, y_test)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=256)

    model = SimpleMLP(input_dim=input_dim, hidden_size=hidden_size, num_classes=10).to(
        device
    )
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    criterion = nn.CrossEntropyLoss()

    checkpoints = []
    train_accs = []

    for epoch in range(num_epochs):
        model.train()
        correct, total = 0, 0
        for data, target in train_loader:
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            correct += (output.argmax(1) == target).sum().item()
            total += target.size(0)

        checkpoints.append(extract_weight_features(model))
        train_accs.append(correct / total)

    # Final test accuracy
    model.eval()
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            correct += (output.argmax(1) == target).sum().item()

    final_accuracy = correct / len(y_test)
    return checkpoints, final_accuracy, train_accs


# CTF Models
class CTFModelLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=64, num_layers=2, dropout=0.3):
        super().__init__()
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers, batch_first=True, dropout=dropout
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Dropout(dropout), nn.Linear(32, 1)
        )

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :]).squeeze(-1)


class CTFModelTransformer(nn.Module):
    def __init__(
        self, input_dim, hidden_dim=64, num_heads=4, num_layers=2, dropout=0.3
    ):
        super().__init__()
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        self.pos_encoding = nn.Parameter(torch.randn(1, 100, hidden_dim) * 0.1)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 2,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32), nn.ReLU(), nn.Dropout(dropout), nn.Linear(32, 1)
        )

    def forward(self, x):
        x = self.input_proj(x)
        x = x + self.pos_encoding[:, : x.size(1), :]
        x = self.transformer(x)
        return self.fc(x[:, -1, :]).squeeze(-1)


# Generate trajectories for all three datasets
datasets_config = {
    "mnist": {"name": "mnist", "train_size": 4000, "test_size": 800},
    "fashion_mnist": {"name": "fashion_mnist", "train_size": 4000, "test_size": 800},
    "cifar10": {"name": "cifar10", "train_size": 4000, "test_size": 800},
}

# Wider hyperparameter ranges for more diversity
hidden_sizes = [32, 64, 128, 256]
learning_rates = [0.0001, 0.0005, 0.001, 0.003, 0.01]
weight_decays = [0.0, 0.001]

all_trajectories = []
all_final_accuracies = []
all_dataset_labels = []

experiment_data = {}

for ds_name, ds_config in datasets_config.items():
    print(f"\n{'='*50}")
    print(f"Processing dataset: {ds_name}")
    print(f"{'='*50}")

    X_train, y_train, X_test, y_test, input_dim = load_hf_dataset(
        ds_config["name"], ds_config["train_size"], ds_config["test_size"]
    )

    trajectories = []
    final_accuracies = []

    configs = [
        (hs, lr, wd)
        for hs in hidden_sizes
        for lr in learning_rates
        for wd in weight_decays
    ]
    np.random.shuffle(configs)
    configs = configs[:20]  # Limit per dataset

    for i, (hs, lr, wd) in enumerate(configs):
        print(f"  [{ds_name}] Training {i+1}/{len(configs)}: hs={hs}, lr={lr}, wd={wd}")
        checkpoints, acc, _ = train_and_collect_checkpoints(
            X_train,
            y_train,
            X_test,
            y_test,
            input_dim,
            hs,
            lr,
            num_epochs=25,
            weight_decay=wd,
        )
        trajectories.append(checkpoints)
        final_accuracies.append(acc)
        all_dataset_labels.append(ds_name)
        print(f"    Final accuracy: {acc:.4f}")

    all_trajectories.extend(trajectories)
    all_final_accuracies.extend(final_accuracies)

    experiment_data[ds_name] = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "final_accuracies": final_accuracies,
        "spearman_correlation": None,
    }

print(f"\nTotal trajectories: {len(all_trajectories)}")
print(
    f"Accuracy range: [{min(all_final_accuracies):.4f}, {max(all_final_accuracies):.4f}]"
)
print(f"Accuracy std: {np.std(all_final_accuracies):.4f}")

# Pad and normalize trajectories
max_len = max(len(t) for t in all_trajectories)
feature_dim = all_trajectories[0][0].shape[0]

padded_trajectories = np.zeros(
    (len(all_trajectories), max_len, feature_dim), dtype=np.float32
)
for i, t in enumerate(all_trajectories):
    for j, cp in enumerate(t):
        padded_trajectories[i, j] = cp

mean = padded_trajectories.mean(axis=(0, 1), keepdims=True)
std = padded_trajectories.std(axis=(0, 1), keepdims=True) + 1e-8
padded_trajectories = (padded_trajectories - mean) / std

final_accuracies = np.array(all_final_accuracies, dtype=np.float32)

# Split data
n_train = int(0.7 * len(all_trajectories))
n_val = int(0.15 * len(all_trajectories))

indices = np.random.permutation(len(all_trajectories))
train_idx, val_idx, test_idx = (
    indices[:n_train],
    indices[n_train : n_train + n_val],
    indices[n_train + n_val :],
)

X_train = torch.tensor(padded_trajectories[train_idx])
y_train = torch.tensor(final_accuracies[train_idx])
X_val = torch.tensor(padded_trajectories[val_idx])
y_val = torch.tensor(final_accuracies[val_idx])
X_test = torch.tensor(padded_trajectories[test_idx])
y_test = torch.tensor(final_accuracies[test_idx])

# Use first 20% checkpoints
early_fraction = 0.2
early_len = max(1, int(max_len * early_fraction))
print(f"\nUsing first {early_len} checkpoints (out of {max_len})")

X_train_early = X_train[:, :early_len, :]
X_val_early = X_val[:, :early_len, :]
X_test_early = X_test[:, :early_len, :]

# Train both models and compare
results = {}

for model_name, ModelClass in [
    ("LSTM", CTFModelLSTM),
    ("Transformer", CTFModelTransformer),
]:
    print(f"\n{'='*50}")
    print(f"Training CTF Model: {model_name}")
    print(f"{'='*50}")

    model = ModelClass(input_dim=feature_dim, hidden_dim=64).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    criterion = nn.MSELoss()
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=10, factor=0.5)

    train_losses, val_losses, val_spearman = [], [], []
    best_val_loss = float("inf")
    best_model_state = None
    patience_counter = 0

    for epoch in range(150):
        model.train()
        optimizer.zero_grad()
        predictions = model(X_train_early.to(device))
        loss = criterion(predictions, y_train.to(device))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        train_loss = loss.item()

        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_early.to(device))
            val_loss = criterion(val_pred, y_val.to(device)).item()
            spearman_corr, _ = spearmanr(val_pred.cpu().numpy(), y_val.numpy())
            spearman_corr = 0.0 if np.isnan(spearman_corr) else spearman_corr

        train_losses.append(train_loss)
        val_losses.append(val_loss)
        val_spearman.append(spearman_corr)
        scheduler.step(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_state = {
                k: v.cpu().clone() for k, v in model.state_dict().items()
            }
            patience_counter = 0
        else:
            patience_counter += 1

        if epoch % 20 == 0:
            print(
                f"Epoch {epoch}: validation_loss = {val_loss:.4f}, spearman_correlation = {spearman_corr:.4f}"
            )

        if patience_counter > 30:
            print(f"Early stopping at epoch {epoch}")
            break

    # Evaluate
    model.load_state_dict({k: v.to(device) for k, v in best_model_state.items()})
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test_early.to(device)).cpu().numpy()

    test_spearman, _ = spearmanr(test_pred, y_test.numpy())
    test_pearson, _ = pearsonr(test_pred, y_test.numpy())

    results[model_name] = {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "val_spearman": val_spearman,
        "test_predictions": test_pred,
        "test_spearman": test_spearman,
        "test_pearson": test_pearson,
    }

    print(f"\n{model_name} Test Results:")
    print(f"  spearman_correlation = {test_spearman:.4f}")
    print(f"  pearson_correlation = {test_pearson:.4f}")

# Store results
best_model = max(results.keys(), key=lambda k: results[k]["test_spearman"])
experiment_data["combined"] = {
    "metrics": {"train": [], "val": results[best_model]["val_spearman"]},
    "losses": {
        "train": results[best_model]["train_losses"],
        "val": results[best_model]["val_losses"],
    },
    "predictions": results[best_model]["test_predictions"].tolist(),
    "ground_truth": y_test.numpy().tolist(),
    "spearman_correlation": results[best_model]["test_spearman"],
    "model_comparison": {
        k: {"spearman": v["test_spearman"], "pearson": v["test_pearson"]}
        for k, v in results.items()
    },
}

# Final summary
print(f"\n{'='*60}")
print("FINAL RESULTS SUMMARY")
print(f"{'='*60}")
print(f"Best model: {best_model}")
print(f"spearman_correlation = {results[best_model]['test_spearman']:.4f}")

for name, res in results.items():
    print(f"\n{name}:")
    print(f"  Test Spearman: {res['test_spearman']:.4f}")
    print(f"  Test Pearson: {res['test_pearson']:.4f}")

# Save data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Visualization
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Loss curves for best model
axes[0, 0].plot(results[best_model]["train_losses"], label="Train", alpha=0.7)
axes[0, 0].plot(results[best_model]["val_losses"], label="Val", alpha=0.7)
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title(f"{best_model} Training Progress")
axes[0, 0].legend()
axes[0, 0].grid(True)

# Spearman correlation over training
axes[0, 1].plot(results[best_model]["val_spearman"])
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Spearman Correlation")
axes[0, 1].set_title("Validation Spearman Correlation")
axes[0, 1].grid(True)

# Predictions vs actual
axes[0, 2].scatter(y_test.numpy(), results[best_model]["test_predictions"], alpha=0.6)
lims = [
    min(y_test.min(), results[best_model]["test_predictions"].min()),
    max(y_test.max(), results[best_model]["test_predictions"].max()),
]
axes[0, 2].plot(lims, lims, "r--", label="Perfect")
axes[0, 2].set_xlabel("Actual Accuracy")
axes[0, 2].set_ylabel("Predicted Accuracy")
axes[0, 2].set_title(f"CTF Predictions (ρ={results[best_model]['test_spearman']:.3f})")
axes[0, 2].legend()
axes[0, 2].grid(True)

# Model comparison
model_names = list(results.keys())
spearman_vals = [results[m]["test_spearman"] for m in model_names]
axes[1, 0].bar(model_names, spearman_vals, color=["steelblue", "coral"])
axes[1, 0].set_ylabel("Test Spearman Correlation")
axes[1, 0].set_title("Model Comparison")
axes[1, 0].grid(True, axis="y")

# Accuracy distribution by dataset
for i, ds_name in enumerate(datasets_config.keys()):
    accs = experiment_data[ds_name]["final_accuracies"]
    axes[1, 1].hist(accs, bins=10, alpha=0.5, label=ds_name)
axes[1, 1].set_xlabel("Final Accuracy")
axes[1, 1].set_ylabel("Count")
axes[1, 1].set_title("Accuracy Distribution by Dataset")
axes[1, 1].legend()
axes[1, 1].grid(True)

# Per-dataset breakdown
ds_labels = np.array(all_dataset_labels)[test_idx]
for ds_name in datasets_config.keys():
    mask = ds_labels == ds_name
    if mask.sum() > 2:
        sp, _ = spearmanr(
            results[best_model]["test_predictions"][mask], y_test.numpy()[mask]
        )
        axes[1, 2].bar(ds_name, sp if not np.isnan(sp) else 0)
axes[1, 2].set_ylabel("Spearman Correlation")
axes[1, 2].set_title("Per-Dataset Test Performance")
axes[1, 2].grid(True, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ctf_multi_dataset_results.png"), dpi=150)
plt.close()

print(f"\nResults saved to {working_dir}")
print(f"spearman_correlation = {results[best_model]['test_spearman']:.4f}")
