import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
torch.manual_seed(42)

N_CLAIMS = 1000
N_TURNS = 8
HALLUCINATION_RATE = 0.4
LR = 1e-3
EPOCHS = 100
BATCH_SIZE = 32
HIDDEN_DIM = 128

experiment_data = {
    "raw_trajectory": {
        ds: {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc": [],
        }
        for ds in ["synthetic_qa", "halueval_sim", "sciq_sim"]
    },
    "handcrafted_features": {
        ds: {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc": [],
        }
        for ds in ["synthetic_qa", "halueval_sim", "sciq_sim"]
    },
    "combined_features": {
        ds: {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc": [],
        }
        for ds in ["synthetic_qa", "halueval_sim", "sciq_sim"]
    },
    "minimal_features": {
        ds: {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc": [],
        }
        for ds in ["synthetic_qa", "halueval_sim", "sciq_sim"]
    },
}


def generate_confidence_trajectory(is_hallucinated, n_turns, dataset_type="standard"):
    if dataset_type == "halueval":
        if is_hallucinated:
            base_conf = np.random.uniform(0.6, 0.9)
            drift_magnitude = np.random.uniform(0.2, 0.4)
            noise_std = 0.12
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(-0.05, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.15 * (trajectory[-1] - base_conf * 0.5)
                new_val = np.clip(
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std),
                    0.05,
                    0.99,
                )
                trajectory.append(new_val)
        else:
            base_conf = np.random.uniform(0.70, 0.97)
            drift_magnitude = np.random.uniform(0.01, 0.06)
            noise_std = 0.025
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.35 * (trajectory[-1] - base_conf)
                new_val = np.clip(
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std),
                    0.05,
                    0.99,
                )
                trajectory.append(new_val)
    elif dataset_type == "sciq":
        if is_hallucinated:
            base_conf = np.random.uniform(0.35, 0.80)
            drift_magnitude = np.random.uniform(0.18, 0.38)
            noise_std = 0.11
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.1 * (trajectory[-1] - base_conf)
                new_val = np.clip(
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std),
                    0.05,
                    0.99,
                )
                trajectory.append(new_val)
        else:
            base_conf = np.random.uniform(0.75, 0.99)
            drift_magnitude = np.random.uniform(0.01, 0.05)
            noise_std = 0.02
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.4 * (trajectory[-1] - base_conf)
                new_val = np.clip(
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std),
                    0.05,
                    0.99,
                )
                trajectory.append(new_val)
    else:
        if is_hallucinated:
            base_conf = np.random.uniform(0.4, 0.85)
            drift_magnitude = np.random.uniform(0.15, 0.35)
            noise_std = 0.10
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.2 * (trajectory[-1] - base_conf)
                new_val = np.clip(
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std),
                    0.05,
                    0.99,
                )
                trajectory.append(new_val)
        else:
            base_conf = np.random.uniform(0.65, 0.97)
            drift_magnitude = np.random.uniform(0.02, 0.08)
            noise_std = 0.03
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.3 * (trajectory[-1] - base_conf)
                new_val = np.clip(
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std),
                    0.05,
                    0.99,
                )
                trajectory.append(new_val)
    return np.array(trajectory)


def generate_dataset(
    n_claims, n_turns, hallucination_rate, dataset_type="standard", seed=42
):
    np.random.seed(seed)
    labels = (np.random.rand(n_claims) < hallucination_rate).astype(int)
    trajectories = np.array(
        [
            generate_confidence_trajectory(
                labels[i], n_turns, dataset_type=dataset_type
            )
            for i in range(n_claims)
        ]
    )
    return labels, trajectories


def extract_handcrafted_features(trajectories):
    single_turn_conf = trajectories[:, 0]
    drift_variance = np.var(trajectories, axis=1)
    drift_range = np.max(trajectories, axis=1) - np.min(trajectories, axis=1)
    drift_std = np.std(trajectories, axis=1)
    drift_mean = np.mean(trajectories, axis=1)
    drift_trend = trajectories[:, -1] - trajectories[:, 0]

    def autocorr_lag1(traj):
        if len(traj) < 2:
            return 0
        c = np.corrcoef(traj[:-1], traj[1:])[0, 1]
        return c if not np.isnan(c) else 0.0

    autocorrs = np.nan_to_num(
        np.array([autocorr_lag1(trajectories[i]) for i in range(len(trajectories))]),
        nan=0.0,
    )
    full_features = np.column_stack(
        [
            single_turn_conf,
            drift_variance,
            drift_range,
            drift_std,
            drift_mean,
            drift_trend,
            autocorrs,
        ]
    )
    minimal_features = np.column_stack([single_turn_conf, drift_variance])
    return full_features, minimal_features


def split_data(n_claims, seed=42):
    np.random.seed(seed)
    n_train = int(0.6 * n_claims)
    n_val = int(0.2 * n_claims)
    idx = np.arange(n_claims)
    np.random.shuffle(idx)
    return idx[:n_train], idx[n_train : n_train + n_val], idx[n_train + n_val :]


class DACNet(nn.Module):
    def __init__(self, input_dim, hidden_dim=128):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_neural_dac(
    X_features,
    labels,
    train_idx,
    val_idx,
    test_idx,
    lr=1e-3,
    epochs=100,
    batch_size=32,
    hidden_dim=128,
    weight_decay=1e-4,
    feature_set_name="raw_trajectory",
    dataset_name="synthetic_qa",
):
    scaler = StandardScaler()
    X_train_np = scaler.fit_transform(X_features[train_idx])
    X_val_np = scaler.transform(X_features[val_idx])
    X_test_np = scaler.transform(X_features[test_idx])
    X_train = torch.tensor(X_train_np, dtype=torch.float32).to(device)
    X_val = torch.tensor(X_val_np, dtype=torch.float32).to(device)
    X_test = torch.tensor(X_test_np, dtype=torch.float32).to(device)
    y_all = labels.astype(np.float32)
    y_train = torch.tensor(y_all[train_idx], dtype=torch.float32).to(device)
    y_val_np = y_all[val_idx]
    y_test_np = y_all[test_idx]
    criterion = nn.BCELoss()
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    torch.manual_seed(42)
    model = DACNet(input_dim=X_features.shape[1], hidden_dim=hidden_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    train_losses, val_losses, train_aurocs, val_aurocs = [], [], [], []
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            pred = model(X_batch)
            loss = criterion(pred, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * len(y_batch)
        epoch_loss /= len(train_idx)
        scheduler.step()
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val).cpu().numpy()
            train_pred_all = model(X_train).cpu().numpy()
            val_loss = criterion(torch.tensor(val_pred), torch.tensor(y_val_np)).item()
            train_auroc_nn = roc_auc_score(y_all[train_idx], train_pred_all)
            val_auroc_nn = roc_auc_score(y_val_np, val_pred)
        train_losses.append(epoch_loss)
        val_losses.append(val_loss)
        train_aurocs.append(train_auroc_nn)
        val_aurocs.append(val_auroc_nn)
        experiment_data[feature_set_name][dataset_name]["metrics"]["train"].append(
            float(train_auroc_nn)
        )
        experiment_data[feature_set_name][dataset_name]["metrics"]["val"].append(
            float(val_auroc_nn)
        )
        experiment_data[feature_set_name][dataset_name]["losses"]["train"].append(
            float(epoch_loss)
        )
        experiment_data[feature_set_name][dataset_name]["losses"]["val"].append(
            float(val_loss)
        )
        if (epoch + 1) % 20 == 0:
            print(
                f"  Epoch {epoch+1:3d}: val_loss={val_loss:.4f}, val_auroc={val_auroc_nn:.4f}"
            )
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test).cpu().numpy()
    auroc_test = roc_auc_score(y_test_np, test_pred)
    experiment_data[feature_set_name][dataset_name]["predictions"] = test_pred.tolist()
    experiment_data[feature_set_name][dataset_name]["ground_truth"] = y_test_np.tolist()
    experiment_data[feature_set_name][dataset_name]["auroc"] = auroc_test
    return auroc_test, train_losses, val_losses, train_aurocs, val_aurocs


datasets_config = [
    ("synthetic_qa", "standard", 42),
    ("halueval_sim", "halueval", 123),
    ("sciq_sim", "sciq", 456),
]

feature_sets = {
    "raw_trajectory": "Raw Trajectory (N_TURNS dims)",
    "handcrafted_features": "Hand-crafted Features (7 dims)",
    "combined_features": "Combined Raw + Hand-crafted",
    "minimal_features": "Minimal Features (2 dims)",
}

all_aurocs = {fs: {} for fs in feature_sets}
train_losses_all = {fs: {} for fs in feature_sets}
val_losses_all = {fs: {} for fs in feature_sets}
train_aurocs_all = {fs: {} for fs in feature_sets}
val_aurocs_all = {fs: {} for fs in feature_sets}

for ds_name, ds_type, ds_seed in datasets_config:
    print(f"\n{'='*65}")
    print(f"Dataset: {ds_name} (type={ds_type})")
    print(f"{'='*65}")
    labels, trajectories = generate_dataset(
        N_CLAIMS, N_TURNS, HALLUCINATION_RATE, dataset_type=ds_type, seed=ds_seed
    )
    print(f"Generated {N_CLAIMS} claims, {N_TURNS} turns each")
    print(f"Hallucinated: {labels.sum()}, Correct: {(1-labels).sum()}")
    train_idx, val_idx, test_idx = split_data(N_CLAIMS, seed=ds_seed)
    full_handcrafted, minimal = extract_handcrafted_features(trajectories)
    raw_traj = trajectories
    combined = np.concatenate([raw_traj, full_handcrafted], axis=1)
    feature_matrices = {
        "raw_trajectory": raw_traj,
        "handcrafted_features": full_handcrafted,
        "combined_features": combined,
        "minimal_features": minimal,
    }
    for fs_name, X_feat in feature_matrices.items():
        print(f"\n--- Feature Set: {feature_sets[fs_name]} | {ds_name} ---")
        print(f"    Input dimension: {X_feat.shape[1]}")
        auroc, tl, vl, ta, va = train_neural_dac(
            X_feat,
            labels,
            train_idx,
            val_idx,
            test_idx,
            lr=LR,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            hidden_dim=HIDDEN_DIM,
            weight_decay=1e-4,
            feature_set_name=fs_name,
            dataset_name=ds_name,
        )
        all_aurocs[fs_name][ds_name] = auroc
        train_losses_all[fs_name][ds_name] = tl
        val_losses_all[fs_name][ds_name] = vl
        train_aurocs_all[fs_name][ds_name] = ta
        val_aurocs_all[fs_name][ds_name] = va
        print(f"    Test AUROC: {auroc:.4f}")

print("\n" + "=" * 75)
print("RESULTS SUMMARY: Feature Set Ablation (Test AUROC)")
print("=" * 75)
print(f"{'Feature Set':<35} {'synthetic_qa':>14} {'halueval_sim':>14} {'sciq_sim':>12}")
print("-" * 75)
for fs_name, fs_desc in feature_sets.items():
    row = f"{fs_desc:<35}"
    for ds_name, _, _ in datasets_config:
        row += f" {all_aurocs[fs_name][ds_name]:>14.4f}"
    print(row)

# ── Visualization 1: Bar chart AUROC by feature set per dataset ──
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fs_names = list(feature_sets.keys())
fs_labels = [
    "Raw\nTrajectory",
    "Hand-crafted\n(7 feats)",
    "Combined\nRaw+HC",
    "Minimal\n(2 feats)",
]
colors = ["steelblue", "darkorange", "green", "red"]
for ax_idx, (ds_name, _, _) in enumerate(datasets_config):
    auroc_vals = [all_aurocs[fs][ds_name] for fs in fs_names]
    bars = axes[ax_idx].bar(
        fs_labels, auroc_vals, color=colors, alpha=0.8, edgecolor="black"
    )
    for bar, val in zip(bars, auroc_vals):
        axes[ax_idx].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10,
        )
    axes[ax_idx].set_ylim(0, 1.15)
    axes[ax_idx].set_title(f"{ds_name}", fontsize=12, fontweight="bold")
    axes[ax_idx].set_ylabel("Test AUROC")
    axes[ax_idx].axhline(y=0.5, color="red", linestyle="--", alpha=0.4, label="Random")
    axes[ax_idx].grid(True, alpha=0.3, axis="y")
plt.suptitle(
    "Feature Set Ablation: AUROC Comparison Across Datasets",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "feature_set_ablation_auroc_bars.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# ── Visualization 2: Training curves per dataset ──
for ds_name, _, _ in datasets_config:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    line_styles = ["-", "--", "-.", ":"]
    for i, (fs_name, fs_desc) in enumerate(feature_sets.items()):
        tl = train_losses_all[fs_name][ds_name]
        vl = val_losses_all[fs_name][ds_name]
        ta = train_aurocs_all[fs_name][ds_name]
        va = val_aurocs_all[fs_name][ds_name]
        short_label = ["Raw Traj", "HC (7)", "Combined", "Minimal (2)"][i]
        axes[0].plot(
            tl,
            color=colors[i],
            linestyle=line_styles[i],
            label=f"Train {short_label}",
            alpha=0.8,
        )
        axes[0].plot(
            vl, color=colors[i], linestyle=":", label=f"Val {short_label}", alpha=0.5
        )
        axes[1].plot(
            ta,
            color=colors[i],
            linestyle=line_styles[i],
            label=f"Train {short_label}",
            alpha=0.8,
        )
        axes[1].plot(
            va, color=colors[i], linestyle=":", label=f"Val {short_label}", alpha=0.5
        )
    axes[0].set_title(f"Training Loss [{ds_name}]", fontsize=12)
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("BCE Loss")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)
    axes[1].set_title(f"Validation AUROC [{ds_name}]", fontsize=12)
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("AUROC")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    plt.suptitle(
        f"Feature Set Ablation Training Curves: {ds_name}",
        fontsize=13,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"feature_set_training_curves_{ds_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

# ── Visualization 3: Heatmap ──
fig, ax = plt.subplots(figsize=(10, 5))
ds_names = [d[0] for d in datasets_config]
auroc_matrix = np.array([[all_aurocs[fs][ds] for ds in ds_names] for fs in fs_names])
im = ax.imshow(auroc_matrix, cmap="RdYlGn", vmin=0.5, vmax=1.0, aspect="auto")
plt.colorbar(im, ax=ax, label="Test AUROC")
ax.set_xticks(range(len(ds_names)))
ax.set_xticklabels(ds_names, fontsize=11)
ax.set_yticks(range(len(fs_names)))
ax.set_yticklabels(
    ["Raw Trajectory", "Hand-crafted (7)", "Combined", "Minimal (2)"], fontsize=11
)
for i in range(len(fs_names)):
    for j in range(len(ds_names)):
        ax.text(
            j,
            i,
            f"{auroc_matrix[i, j]:.3f}",
            ha="center",
            va="center",
            fontweight="bold",
            fontsize=12,
            color="black" if auroc_matrix[i, j] > 0.65 else "white",
        )
ax.set_title("Feature Set Ablation: AUROC Heatmap", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "feature_set_auroc_heatmap.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# ── Visualization 4: Average AUROC ──
fig, ax = plt.subplots(figsize=(9, 5))
avg_aurocs = [np.mean([all_aurocs[fs][ds] for ds in ds_names]) for fs in fs_names]
bars = ax.bar(fs_labels, avg_aurocs, color=colors, alpha=0.8, edgecolor="black")
for bar, val in zip(bars, avg_aurocs):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.003,
        f"{val:.4f}",
        ha="center",
        va="bottom",
        fontweight="bold",
        fontsize=11,
    )
ax.set_ylim(0.5, 1.05)
ax.set_ylabel("Average Test AUROC (across datasets)", fontsize=12)
ax.set_title(
    "Feature Set Ablation: Average AUROC Across All Datasets",
    fontsize=13,
    fontweight="bold",
)
ax.axhline(y=0.5, color="red", linestyle="--", alpha=0.4)
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "feature_set_avg_auroc.png"), dpi=150, bbox_inches="tight"
)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nAll data saved to", working_dir)
print("Done!")
