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
    "uniform_1_10": {
        "weight_forensics": {
            "metrics": {"train": [], "val": [], "test": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "r2_scores": {"train": [], "val": []},
            "epochs": [],
            "imbalance_ratios": [],
        }
    },
    "log_uniform_1_10": {
        "weight_forensics": {
            "metrics": {"train": [], "val": [], "test": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "r2_scores": {"train": [], "val": []},
            "epochs": [],
            "imbalance_ratios": [],
        }
    },
    "log_uniform_1_20": {
        "weight_forensics": {
            "metrics": {"train": [], "val": [], "test": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "r2_scores": {"train": [], "val": []},
            "epochs": [],
            "imbalance_ratios": [],
        }
    },
}


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

train_labels = np.array(full_train.targets)
class_indices = {c: np.where(train_labels == c)[0] for c in range(10)}


def make_imbalanced_loader(
    imbalance_ratio, minority_classes=None, n_majority=300, batch_size=128
):
    if minority_classes is None:
        minority_classes = list(range(5, 10))
    majority_classes = [c for c in range(10) if c not in minority_classes]
    n_minority = max(1, int(n_majority / imbalance_ratio))
    selected = []
    for c in majority_classes:
        idx = class_indices[c].copy()
        np.random.shuffle(idx)
        selected.extend(idx[:n_majority].tolist())
    for c in minority_classes:
        idx = class_indices[c].copy()
        np.random.shuffle(idx)
        selected.extend(idx[:n_minority].tolist())
    subset = Subset(full_train, selected)
    return DataLoader(
        subset, batch_size=batch_size, shuffle=True, num_workers=0, drop_last=False
    )


def train_small_model(loader, epochs=6):
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


def build_model_zoo(imbalance_ratios, config_name):
    N = len(imbalance_ratios)
    weight_features_list = []
    targets_list = []
    print(f"\nBuilding model zoo for '{config_name}' with {N} models...")
    print(
        f"  Ratio stats: min={imbalance_ratios.min():.3f}, max={imbalance_ratios.max():.3f}, "
        f"mean={imbalance_ratios.mean():.3f}, median={np.median(imbalance_ratios):.3f}"
    )
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
        if (i + 1) % 40 == 0:
            elapsed = time.time() - t0
            print(f"  Trained {i+1}/{N} models | elapsed: {elapsed:.1f}s")
    X = np.stack(weight_features_list)
    y = np.array(targets_list, dtype=np.float32)
    print(f"  Feature matrix: {X.shape}, built in {time.time()-t0:.1f}s")
    return X, y


def train_meta_model(X, y, config_name, exp_dict, meta_epochs=150):
    X_mean = X.mean(0)
    X_std = X.std(0) + 1e-8
    X_norm = (X - X_mean) / X_std
    y_min, y_max = y.min(), y.max()
    y_norm = (y - y_min) / (y_max - y_min)

    X_tv, X_test, y_tv, y_test = train_test_split(
        X_norm, y_norm, test_size=0.15, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_tv, y_tv, test_size=0.15, random_state=42
    )
    print(f"  Split: train={len(X_train)}, val={len(X_val)}, test={len(X_test)}")

    def to_tensor(arr):
        return torch.tensor(arr, dtype=torch.float32).to(device)

    X_train_t = to_tensor(X_train)
    y_train_t = to_tensor(y_train).unsqueeze(1)
    X_val_t = to_tensor(X_val)
    y_val_t = to_tensor(y_val).unsqueeze(1)
    X_test_t = to_tensor(X_test)

    train_ds = TensorDataset(X_train_t, y_train_t)
    train_dl = DataLoader(train_ds, batch_size=32, shuffle=True)

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

    print(f"  Training meta-model for {meta_epochs} epochs...")
    for epoch in range(1, meta_epochs + 1):
        meta_model.train()
        train_losses, train_preds, train_true = [], [], []
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

        exp_dict["losses"]["train"].append(train_loss)
        exp_dict["losses"]["val"].append(val_loss)
        exp_dict["r2_scores"]["train"].append(train_r2)
        exp_dict["r2_scores"]["val"].append(val_r2)
        exp_dict["epochs"].append(epoch)

        if epoch % 30 == 0 or epoch == 1:
            print(
                f"  Epoch {epoch:3d}: val_loss={val_loss:.4f} | train_r2={train_r2:.4f} | val_r2={val_r2:.4f}"
            )

    meta_model.eval()
    with torch.no_grad():
        test_pred_norm = meta_model(X_test_t).cpu().numpy().flatten()

    test_pred = test_pred_norm * (y_max - y_min) + y_min
    test_true = y_test * (y_max - y_min) + y_min
    test_r2 = r2_score(test_true, test_pred)
    print(f"  TEST R²: {test_r2:.4f}")

    exp_dict["predictions"] = test_pred.tolist()
    exp_dict["ground_truth"] = test_true.tolist()
    exp_dict["metrics"]["test"].append(test_r2)

    return meta_model, test_r2, test_pred, test_true, feat_dim, y_min, y_max


N_MODELS = 200
np.random.seed(42)

configs = {
    "uniform_1_10": np.random.uniform(1.0, 10.0, N_MODELS),
    "log_uniform_1_10": np.exp(np.random.uniform(np.log(1.0), np.log(10.0), N_MODELS)),
    "log_uniform_1_20": np.exp(np.random.uniform(np.log(1.0), np.log(20.0), N_MODELS)),
}

results = {}
for config_name, imbalance_ratios in configs.items():
    print(f"\n{'='*60}")
    print(f"Configuration: {config_name}")
    print(f"{'='*60}")
    exp_dict = experiment_data[config_name]["weight_forensics"]
    exp_dict["imbalance_ratios"] = imbalance_ratios.tolist()
    X, y = build_model_zoo(imbalance_ratios, config_name)
    meta_model, test_r2, test_pred, test_true, feat_dim, y_min, y_max = (
        train_meta_model(X, y, config_name, exp_dict, meta_epochs=150)
    )
    results[config_name] = {
        "test_r2": test_r2,
        "test_pred": test_pred,
        "test_true": test_true,
        "meta_model": meta_model,
        "feat_dim": feat_dim,
        "imbalance_ratios": imbalance_ratios,
        "X": X,
        "y": y,
    }

print(f"\n{'='*60}")
print("COMPARISON SUMMARY")
print(f"{'='*60}")
for config_name, res in results.items():
    print(f"  {config_name:25s}: Test R² = {res['test_r2']:.4f}")

best_config = max(results.keys(), key=lambda k: results[k]["test_r2"])
print(
    f"\n  Best configuration: {best_config} (R²={results[best_config]['test_r2']:.4f})"
)

# ── Visualizations ─────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 3, figsize=(18, 15))
config_list = list(configs.keys())
colors = ["steelblue", "darkorange", "forestgreen"]

for row, (config_name, color) in enumerate(zip(config_list, colors)):
    exp_dict = experiment_data[config_name]["weight_forensics"]
    res = results[config_name]
    test_r2 = res["test_r2"]

    ax = axes[row, 0]
    ax.plot(exp_dict["losses"]["train"], label="Train Loss", color=color)
    ax.plot(exp_dict["losses"]["val"], label="Val Loss", color=color, linestyle="--")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss")
    ax.set_title(f"{config_name}\nTraining Loss")
    ax.legend()
    ax.grid(True)

    ax = axes[row, 1]
    ax.plot(exp_dict["r2_scores"]["train"], label="Train R²", color=color)
    ax.plot(exp_dict["r2_scores"]["val"], label="Val R²", color=color, linestyle="--")
    ax.axhline(y=test_r2, color="red", linestyle="-.", label=f"Test R²={test_r2:.3f}")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("R² Score")
    ax.set_title(f"{config_name}\nR² Score")
    ax.legend()
    ax.grid(True)

    ax = axes[row, 2]
    test_pred = np.array(res["test_pred"])
    test_true = np.array(res["test_true"])
    ax.scatter(test_true, test_pred, alpha=0.7, color=color, edgecolors="k", s=60)
    mn = min(test_true.min(), test_pred.min())
    mx = max(test_true.max(), test_pred.max())
    ax.plot([mn, mx], [mn, mx], "r--", lw=2, label="Perfect")
    ax.set_xlabel("True Imbalance Ratio")
    ax.set_ylabel("Predicted Imbalance Ratio")
    ax.set_title(f"{config_name}\nPred vs True (R²={test_r2:.3f})")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_results.png"),
    dpi=120,
    bbox_inches="tight",
)
plt.close()
print(f"Saved main results figure.")

# Distribution comparison
fig2, axes2 = plt.subplots(1, 3, figsize=(18, 5))
for ax, (config_name, color) in zip(axes2, zip(config_list, colors)):
    ratios = np.array(results[config_name]["imbalance_ratios"])
    ax.hist(ratios, bins=30, color=color, alpha=0.7, edgecolor="black")
    ax.set_xlabel("Imbalance Ratio")
    ax.set_ylabel("Count")
    ax.set_title(
        f"{config_name}\nRatio Distribution (R²={results[config_name]['test_r2']:.3f})"
    )
    ax.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "ratio_distributions.png"), dpi=120, bbox_inches="tight"
)
plt.close()
print(f"Saved ratio distributions figure.")

# Feature importance comparison
fig3, axes3 = plt.subplots(1, 3, figsize=(18, 5))
for ax, (config_name, color) in zip(axes3, zip(config_list, colors)):
    meta_model = results[config_name]["meta_model"]
    first_layer_weights = meta_model[0].weight.data.cpu().numpy()
    feat_importance = np.abs(first_layer_weights).mean(0)
    top_k = 20
    top_idx = np.argsort(feat_importance)[-top_k:][::-1]
    ax.bar(range(top_k), feat_importance[top_idx], color=color, alpha=0.8)
    ax.set_xlabel("Feature Index (top-20)")
    ax.set_ylabel("Avg |Weight|")
    ax.set_title(f"{config_name}\nTop-20 Feature Importance")
    ax.set_xticks(range(top_k))
    ax.set_xticklabels(top_idx, rotation=45, fontsize=8)
    ax.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "feature_importance.png"), dpi=120, bbox_inches="tight"
)
plt.close()
print(f"Saved feature importance figure.")

# R² comparison bar chart
fig4, ax4 = plt.subplots(figsize=(8, 5))
test_r2_vals = [results[c]["test_r2"] for c in config_list]
bars = ax4.bar(config_list, test_r2_vals, color=colors, alpha=0.8, edgecolor="black")
ax4.set_ylabel("Test R² Score")
ax4.set_title("Test R² Comparison Across Sampling Strategies")
for bar, val in zip(bars, test_r2_vals):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.4f}",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
ax4.set_ylim(0, max(test_r2_vals) * 1.15)
ax4.grid(True, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "r2_comparison.png"), dpi=120, bbox_inches="tight"
)
plt.close()
print(f"Saved R² comparison figure.")

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
np.save(
    os.path.join(working_dir, "weight_features_uniform_1_10.npy"),
    results["uniform_1_10"]["X"],
)
np.save(
    os.path.join(working_dir, "weight_features_log_uniform_1_10.npy"),
    results["log_uniform_1_10"]["X"],
)
np.save(
    os.path.join(working_dir, "weight_features_log_uniform_1_20.npy"),
    results["log_uniform_1_20"]["X"],
)
np.save(
    os.path.join(working_dir, "targets_uniform_1_10.npy"), results["uniform_1_10"]["y"]
)
np.save(
    os.path.join(working_dir, "targets_log_uniform_1_10.npy"),
    results["log_uniform_1_10"]["y"],
)
np.save(
    os.path.join(working_dir, "targets_log_uniform_1_20.npy"),
    results["log_uniform_1_20"]["y"],
)
print(f"Saved all experiment data to {working_dir}/")

print(f"\n{'='*60}")
print(f"FINAL RESULTS SUMMARY")
print(f"  Model Zoo Size per config : {N_MODELS}")
print(f"  Feature Dimension         : {results['uniform_1_10']['feat_dim']}")
for config_name in config_list:
    ed = experiment_data[config_name]["weight_forensics"]
    tr2 = ed["r2_scores"]["train"][-1]
    vr2 = ed["r2_scores"]["val"][-1]
    tstr2 = ed["metrics"]["test"][0]
    print(f"\n  [{config_name}]")
    print(f"    Train R²  : {tr2:.4f}")
    print(f"    Val R²    : {vr2:.4f}")
    print(f"    Test R²   : {tstr2:.4f}")
print(
    f"\n  Best Config : {best_config} (Test R²={results[best_config]['test_r2']:.4f})"
)
print(f"{'='*60}")
