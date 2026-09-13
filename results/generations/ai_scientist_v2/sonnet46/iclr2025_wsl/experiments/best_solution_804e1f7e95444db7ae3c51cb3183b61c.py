import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Subset
import torchvision
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import time

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {
    "weight_forensics": {
        "metrics": {"train": [], "val": [], "test": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "r2_scores": {"train": [], "val": []},
        "epochs": [],
    }
}


# ── Tiny CNN (target network) ─────────────────────────────────────────────────
class TinyCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(32 * 8 * 8, 64), nn.ReLU(), nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x).flatten(1))


def extract_weight_features(model):
    """Extract statistical features from each layer's weights."""
    feats = []
    for p in model.parameters():
        w = p.data.cpu().numpy().flatten()
        feats.extend(
            [
                w.mean(),
                w.std(),
                np.percentile(w, 10),
                np.percentile(w, 25),
                np.percentile(w, 50),
                np.percentile(w, 75),
                np.percentile(w, 90),
                np.abs(w).mean(),
                (w > 0).mean(),
                w.var(),
            ]
        )
    return np.array(feats, dtype=np.float32)


# ── Load CIFAR-10 once ────────────────────────────────────────────────────────
transform = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ]
)
print("Loading CIFAR-10...")
full_train = torchvision.datasets.CIFAR10(
    root="./working/data", train=True, download=True, transform=transform
)
full_test = torchvision.datasets.CIFAR10(
    root="./working/data", train=False, download=True, transform=transform
)

# Pre-separate indices by class
train_labels = np.array(full_train.targets)
class_indices = {c: np.where(train_labels == c)[0] for c in range(10)}


def make_imbalanced_loader(
    imbalance_ratio, minority_classes=None, n_majority=400, batch_size=128
):
    """
    imbalance_ratio: majority_count / minority_count
    minority_classes: which classes are minority (default: classes 5-9)
    """
    if minority_classes is None:
        minority_classes = list(range(5, 10))
    majority_classes = [c for c in range(10) if c not in minority_classes]

    n_minority = max(1, int(n_majority / imbalance_ratio))
    selected = []
    for c in majority_classes:
        idx = class_indices[c]
        np.random.shuffle(idx)
        selected.extend(idx[:n_majority].tolist())
    for c in minority_classes:
        idx = class_indices[c]
        np.random.shuffle(idx)
        selected.extend(idx[:n_minority].tolist())

    subset = Subset(full_train, selected)
    return DataLoader(
        subset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False
    )


def train_small_model(loader, epochs=8):
    model = TinyCNN(num_classes=10).to(device)
    opt = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            opt.step()
    return model


# ── Build Model Zoo ───────────────────────────────────────────────────────────
N_MODELS = 200
imbalance_ratios = np.random.uniform(1.0, 10.0, N_MODELS)

weight_features_list = []
targets_list = []

print(f"Building model zoo with {N_MODELS} models...")
t0 = time.time()
for i, ratio in enumerate(imbalance_ratios):
    np.random.seed(i)
    torch.manual_seed(i)
    loader = make_imbalanced_loader(
        imbalance_ratio=ratio, n_majority=300, batch_size=128
    )
    model = train_small_model(loader, epochs=6)
    feats = extract_weight_features(model)
    weight_features_list.append(feats)
    targets_list.append(ratio)
    if (i + 1) % 20 == 0:
        elapsed = time.time() - t0
        print(
            f"  Trained {i+1}/{N_MODELS} models | "
            f"elapsed: {elapsed:.1f}s | "
            f"ratio range: [{min(imbalance_ratios[:i+1]):.2f}, "
            f"{max(imbalance_ratios[:i+1]):.2f}]"
        )

X = np.stack(weight_features_list)  # (N, feat_dim)
y = np.array(targets_list, dtype=np.float32)
print(f"Feature matrix shape: {X.shape}, target shape: {y.shape}")
print(f"Model zoo built in {time.time()-t0:.1f}s")

# ── Normalize features ────────────────────────────────────────────────────────
X_mean = X.mean(0)
X_std = X.std(0) + 1e-8
X_norm = (X - X_mean) / X_std

# Normalize targets to [0,1] range
y_min, y_max = y.min(), y.max()
y_norm = (y - y_min) / (y_max - y_min)

# ── Train / Val / Test split ──────────────────────────────────────────────────
X_tv, X_test, y_tv, y_test = train_test_split(
    X_norm, y_norm, test_size=0.15, random_state=42
)
X_train, X_val, y_train, y_val = train_test_split(
    X_tv, y_tv, test_size=0.15, random_state=42
)
print(f"Split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")


def to_tensor(arr):
    return torch.tensor(arr, dtype=torch.float32).to(device)


X_train_t = to_tensor(X_train)
y_train_t = to_tensor(y_train).unsqueeze(1)
X_val_t = to_tensor(X_val)
y_val_t = to_tensor(y_val).unsqueeze(1)
X_test_t = to_tensor(X_test)
y_test_t = to_tensor(y_test).unsqueeze(1)

train_ds = TensorDataset(X_train_t, y_train_t)
train_dl = DataLoader(train_ds, batch_size=32, shuffle=True)

# ── Meta-model MLP ────────────────────────────────────────────────────────────
feat_dim = X_norm.shape[1]
meta_model = nn.Sequential(
    nn.Linear(feat_dim, 256),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 1),
).to(device)

optimizer = optim.Adam(meta_model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=100)
criterion = nn.MSELoss()

META_EPOCHS = 150
print(f"\nTraining meta-model for {META_EPOCHS} epochs...")

for epoch in range(1, META_EPOCHS + 1):
    meta_model.train()
    train_losses = []
    train_preds, train_true = [], []
    for xb, yb in train_dl:
        optimizer.zero_grad()
        pred = meta_model(xb)
        loss = criterion(pred, yb)
        loss.backward()
        optimizer.step()
        train_losses.append(loss.item())
        train_preds.append(pred.detach().cpu().numpy())
        train_true.append(yb.detach().cpu().numpy())
    scheduler.step()

    train_loss = np.mean(train_losses)
    train_preds_np = np.concatenate(train_preds).flatten()
    train_true_np = np.concatenate(train_true).flatten()
    train_r2 = r2_score(train_true_np, train_preds_np)

    meta_model.eval()
    with torch.no_grad():
        val_pred = meta_model(X_val_t).cpu().numpy().flatten()
        val_true = y_val_t.cpu().numpy().flatten()
        val_loss = criterion(
            to_tensor(val_pred).unsqueeze(1), to_tensor(val_true).unsqueeze(1)
        ).item()
        val_r2 = r2_score(val_true, val_pred)

    experiment_data["weight_forensics"]["losses"]["train"].append(train_loss)
    experiment_data["weight_forensics"]["losses"]["val"].append(val_loss)
    experiment_data["weight_forensics"]["r2_scores"]["train"].append(train_r2)
    experiment_data["weight_forensics"]["r2_scores"]["val"].append(val_r2)
    experiment_data["weight_forensics"]["epochs"].append(epoch)

    if epoch % 10 == 0 or epoch == 1:
        print(
            f"Epoch {epoch:3d}: val_loss={val_loss:.4f} | "
            f"train_r2={train_r2:.4f} | val_r2={val_r2:.4f}"
        )

# ── Test evaluation ───────────────────────────────────────────────────────────
meta_model.eval()
with torch.no_grad():
    test_pred_norm = meta_model(X_test_t).cpu().numpy().flatten()

# Denormalize
test_pred = test_pred_norm * (y_max - y_min) + y_min
test_true = y_test * (y_max - y_min) + y_min

test_r2 = r2_score(test_true, test_pred)
print(f"\n{'='*50}")
print(f"TEST R² Score: {test_r2:.4f}")
print(f"{'='*50}")

experiment_data["weight_forensics"]["predictions"] = test_pred.tolist()
experiment_data["weight_forensics"]["ground_truth"] = test_true.tolist()
experiment_data["weight_forensics"]["metrics"]["test"].append(test_r2)

# ── Visualizations ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 1. Loss curves
ax = axes[0]
ax.plot(experiment_data["weight_forensics"]["losses"]["train"], label="Train Loss")
ax.plot(experiment_data["weight_forensics"]["losses"]["val"], label="Val Loss")
ax.set_xlabel("Epoch")
ax.set_ylabel("MSE Loss")
ax.set_title("Meta-Model Training Loss")
ax.legend()
ax.grid(True)

# 2. R² curves
ax = axes[1]
ax.plot(experiment_data["weight_forensics"]["r2_scores"]["train"], label="Train R²")
ax.plot(experiment_data["weight_forensics"]["r2_scores"]["val"], label="Val R²")
ax.axhline(y=test_r2, color="red", linestyle="--", label=f"Test R²={test_r2:.3f}")
ax.set_xlabel("Epoch")
ax.set_ylabel("R² Score")
ax.set_title("R² Score over Training")
ax.legend()
ax.grid(True)

# 3. Predicted vs True
ax = axes[2]
ax.scatter(test_true, test_pred, alpha=0.7, color="steelblue", edgecolors="k", s=60)
mn, mx = min(test_true.min(), test_pred.min()), max(test_true.max(), test_pred.max())
ax.plot([mn, mx], [mn, mx], "r--", lw=2, label="Perfect prediction")
ax.set_xlabel("True Imbalance Ratio")
ax.set_ylabel("Predicted Imbalance Ratio")
ax.set_title(f"Predicted vs True (Test R²={test_r2:.3f})")
ax.legend()
ax.grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_results.png"),
    dpi=120,
    bbox_inches="tight",
)
plt.close()
print(f"Saved figure to {working_dir}/weight_forensics_results.png")

# Feature importance via weight magnitude of first layer
first_layer_weights = meta_model[0].weight.data.cpu().numpy()
feat_importance = np.abs(first_layer_weights).mean(0)
top_k = 20
top_idx = np.argsort(feat_importance)[-top_k:][::-1]

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.bar(range(top_k), feat_importance[top_idx])
ax2.set_xlabel("Feature Index (top-20)")
ax2.set_ylabel("Avg |Weight|")
ax2.set_title("Top-20 Most Important Weight Features for Imbalance Detection")
ax2.set_xticks(range(top_k))
ax2.set_xticklabels(top_idx, rotation=45)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "feature_importance.png"), dpi=120, bbox_inches="tight"
)
plt.close()
print(f"Saved feature importance figure.")

# ── Save experiment data ──────────────────────────────────────────────────────
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
np.save(os.path.join(working_dir, "weight_features.npy"), X)
np.save(os.path.join(working_dir, "targets.npy"), y)
print(f"Saved experiment data to {working_dir}/")

print(f"\n{'='*50}")
print(f"FINAL RESULTS SUMMARY")
print(f"  Model Zoo Size      : {N_MODELS}")
print(f"  Feature Dimension   : {feat_dim}")
print(
    f"  Train R²            : {experiment_data['weight_forensics']['r2_scores']['train'][-1]:.4f}"
)
print(
    f"  Val R²              : {experiment_data['weight_forensics']['r2_scores']['val'][-1]:.4f}"
)
print(f"  Test R²             : {test_r2:.4f}")
print(f"{'='*50}")
