import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── reproducibility ──────────────────────────────────────────────────────────
np.random.seed(42)
torch.manual_seed(42)

# ── experiment_data container ────────────────────────────────────────────────
experiment_data = {
    "longitudinal_preferences": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "pdas_per_epoch": [],
        "predictions": [],
        "ground_truth": [],
        "pdas_baseline": None,
        "pdas_recalibrated": None,
    }
}

# ════════════════════════════════════════════════════════════════════════════
# 1.  SYNTHETIC DATA GENERATION
# ════════════════════════════════════════════════════════════════════════════
N_USERS = 200
N_TIMESTEPS = 8
N_PREF_DIMS = 16  # number of preference probe dimensions
N_HIGH_AI = 100  # users with heavy AI interaction
N_LOW_AI = 100  # control group

# Authentic preference evolution (random-walk, same for both groups)
authentic_drift_scale = 0.05

# AI-induced drift: systematic push toward a "modal AI preference" vector
ai_modal_pref = np.random.randn(N_PREF_DIMS) * 0.5
ai_drift_scale = 0.12  # stronger than authentic drift


def generate_user_preferences(
    n_users, n_timesteps, n_dims, ai_influence=False, ai_drift_scale=0.12
):
    """Returns (n_users, n_timesteps, n_dims) preference array."""
    prefs = np.zeros((n_users, n_timesteps, n_dims))
    # initial preferences
    prefs[:, 0, :] = np.random.randn(n_users, n_dims)
    for t in range(1, n_timesteps):
        authentic_noise = np.random.randn(n_users, n_dims) * authentic_drift_scale
        if ai_influence:
            # pull toward ai_modal_pref
            ai_pull = (ai_modal_pref - prefs[:, t - 1, :]) * ai_drift_scale
            prefs[:, t, :] = prefs[:, t - 1, :] + authentic_noise + ai_pull
        else:
            prefs[:, t, :] = prefs[:, t - 1, :] + authentic_noise
    return prefs


high_ai_prefs = generate_user_preferences(
    N_HIGH_AI,
    N_TIMESTEPS,
    N_PREF_DIMS,
    ai_influence=True,
    ai_drift_scale=ai_drift_scale,
)
low_ai_prefs = generate_user_preferences(
    N_LOW_AI, N_TIMESTEPS, N_PREF_DIMS, ai_influence=False
)


# Ground-truth labels: 1 = AI-induced drift segment, 0 = authentic
# We mark a timestep as AI-drifted if the high-AI user's shift direction
# correlates strongly with the modal AI preference direction.
def compute_shift_labels(prefs, threshold=0.3):
    """Returns (n_users, n_timesteps-1) binary labels."""
    labels = np.zeros((prefs.shape[0], prefs.shape[1] - 1))
    modal_norm = ai_modal_pref / (np.linalg.norm(ai_modal_pref) + 1e-9)
    for u in range(prefs.shape[0]):
        for t in range(prefs.shape[1] - 1):
            delta = prefs[u, t + 1] - prefs[u, t]
            delta_norm = delta / (np.linalg.norm(delta) + 1e-9)
            cos_sim = np.dot(delta_norm, modal_norm)
            labels[u, t] = 1 if cos_sim > threshold else 0
    return labels


high_ai_labels = compute_shift_labels(high_ai_prefs)
low_ai_labels = compute_shift_labels(low_ai_prefs)


# ════════════════════════════════════════════════════════════════════════════
# 2.  PDAS COMPUTATION  (counterfactual comparison)
# ════════════════════════════════════════════════════════════════════════════
def compute_pdas(high_ai_prefs, low_ai_prefs):
    """
    PDAS = AI-induced shift magnitude / total shift magnitude.
    AI-induced shift for user i at time t ≈
        ||Δhigh_ai[i,t]|| - mean(||Δlow_ai[:,t]||)   (clipped to ≥ 0)
    """
    total_ai_induced = 0.0
    total_shift = 0.0
    for t in range(N_TIMESTEPS - 1):
        delta_high = np.linalg.norm(
            high_ai_prefs[:, t + 1] - high_ai_prefs[:, t], axis=1
        )
        delta_low = np.linalg.norm(low_ai_prefs[:, t + 1] - low_ai_prefs[:, t], axis=1)
        baseline = delta_low.mean()
        ai_induced = np.maximum(0, delta_high - baseline).sum()
        total_ai_induced += ai_induced
        total_shift += delta_high.sum()
    pdas = total_ai_induced / (total_shift + 1e-9)
    return float(pdas)


pdas_baseline = compute_pdas(high_ai_prefs, low_ai_prefs)
print(f"Baseline PDAS (before recalibration): {pdas_baseline:.4f}")
experiment_data["longitudinal_preferences"]["pdas_baseline"] = pdas_baseline


# ════════════════════════════════════════════════════════════════════════════
# 3.  REWARD MODEL
# ════════════════════════════════════════════════════════════════════════════
class RewardModel(nn.Module):
    def __init__(self, input_dim, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def build_reward_dataset(prefs, weights=None):
    """
    Build (preference_vector, reward_score) pairs.
    Reward = dot product with a fixed 'authentic value' direction.
    """
    authentic_dir = np.ones(N_PREF_DIMS) / np.sqrt(N_PREF_DIMS)
    X, y, w = [], [], []
    for u in range(prefs.shape[0]):
        for t in range(prefs.shape[1]):
            x_vec = prefs[u, t]
            reward = float(np.dot(x_vec, authentic_dir))
            X.append(x_vec)
            y.append(reward)
            sample_w = weights[u, t] if weights is not None else 1.0
            w.append(sample_w)
    return (
        np.array(X, dtype=np.float32),
        np.array(y, dtype=np.float32),
        np.array(w, dtype=np.float32),
    )


# ── normalise preference inputs ──────────────────────────────────────────────
scaler = StandardScaler()

# Baseline: train on ALL high-AI data (contaminated)
all_high_prefs = high_ai_prefs  # (100, 8, 16)
X_base, y_base, w_base = build_reward_dataset(all_high_prefs)
scaler.fit(X_base)
X_base_norm = scaler.transform(X_base).astype(np.float32)

# Split 80/20
n_total = X_base_norm.shape[0]
n_train = int(0.8 * n_total)
idx = np.random.permutation(n_total)
train_idx, val_idx = idx[:n_train], idx[n_train:]


def make_loader(X, y, w, idx, batch_size=64, shuffle=True):
    Xt = torch.tensor(X[idx])
    yt = torch.tensor(y[idx])
    wt = torch.tensor(w[idx])
    ds = TensorDataset(Xt, yt, wt)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle)


train_loader = make_loader(X_base_norm, y_base, w_base, train_idx)
val_loader = make_loader(X_base_norm, y_base, w_base, val_idx, shuffle=False)


def train_reward_model(
    train_loader, val_loader, n_epochs=30, lr=1e-3, label="baseline"
):
    model = RewardModel(N_PREF_DIMS).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss(reduction="none")
    train_losses, val_losses = [], []

    for epoch in range(1, n_epochs + 1):
        model.train()
        epoch_loss = 0.0
        for Xb, yb, wb in train_loader:
            Xb, yb, wb = Xb.to(device), yb.to(device), wb.to(device)
            pred = model(Xb)
            loss = (criterion(pred, yb) * wb).mean()
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * Xb.size(0)
        epoch_loss /= len(train_loader.dataset)

        model.eval()
        val_loss = 0.0
        preds_all, gt_all = [], []
        with torch.no_grad():
            for Xb, yb, wb in val_loader:
                Xb, yb, wb = Xb.to(device), yb.to(device), wb.to(device)
                pred = model(Xb)
                loss = (criterion(pred, yb) * wb).mean()
                val_loss += loss.item() * Xb.size(0)
                preds_all.append(pred.cpu().numpy())
                gt_all.append(yb.cpu().numpy())
        val_loss /= len(val_loader.dataset)

        train_losses.append(epoch_loss)
        val_losses.append(val_loss)

        # PDAS-like metric per epoch: use val predictions vs ground truth
        preds_np = np.concatenate(preds_all)
        gt_np = np.concatenate(gt_all)
        epoch_pdas = float(
            np.mean(np.abs(preds_np - gt_np)) / (np.mean(np.abs(gt_np)) + 1e-9)
        )

        experiment_data["longitudinal_preferences"]["losses"]["train"].append(
            epoch_loss
        )
        experiment_data["longitudinal_preferences"]["losses"]["val"].append(val_loss)
        experiment_data["longitudinal_preferences"]["metrics"]["train"].append(
            epoch_loss
        )
        experiment_data["longitudinal_preferences"]["metrics"]["val"].append(val_loss)
        experiment_data["longitudinal_preferences"]["pdas_per_epoch"].append(epoch_pdas)

        print(
            f"[{label}] Epoch {epoch:3d}: train_loss={epoch_loss:.4f}  "
            f"val_loss={val_loss:.4f}  epoch_PDAS={epoch_pdas:.4f}"
        )

    experiment_data["longitudinal_preferences"]["predictions"] = preds_all[-1].tolist()
    experiment_data["longitudinal_preferences"]["ground_truth"] = gt_all[-1].tolist()
    return model, train_losses, val_losses


print("\n── Training BASELINE reward model (contaminated) ──")
model_base, tl_base, vl_base = train_reward_model(
    train_loader, val_loader, n_epochs=30, label="baseline"
)


# ════════════════════════════════════════════════════════════════════════════
# 4.  RECALIBRATION  – down-weight AI-contaminated samples
# ════════════════════════════════════════════════════════════════════════════
def compute_sample_weights(prefs, low_ai_prefs):
    """
    Weight = 1 - normalised AI-induced drift for each (user, timestep) sample.
    High drift → low weight.
    """
    modal_norm = ai_modal_pref / (np.linalg.norm(ai_modal_pref) + 1e-9)
    n_u, n_t, n_d = prefs.shape
    weights = np.ones((n_u, n_t))
    baseline_shift = np.mean(
        np.linalg.norm(low_ai_prefs[:, 1:] - low_ai_prefs[:, :-1], axis=2)
    )

    for u in range(n_u):
        for t in range(1, n_t):
            delta = prefs[u, t] - prefs[u, t - 1]
            delta_norm = delta / (np.linalg.norm(delta) + 1e-9)
            cos_sim = np.dot(delta_norm, modal_norm)
            shift_mag = np.linalg.norm(delta)
            ai_score = max(0.0, cos_sim) * max(0.0, shift_mag - baseline_shift)
            weights[u, t] = 1.0 / (1.0 + ai_score)
    # normalise to [0.1, 1]
    weights = 0.1 + 0.9 * (weights - weights.min()) / (
        weights.max() - weights.min() + 1e-9
    )
    return weights


recal_weights = compute_sample_weights(all_high_prefs, low_ai_prefs)
X_recal, y_recal, w_recal = build_reward_dataset(all_high_prefs, weights=recal_weights)
X_recal_norm = scaler.transform(X_recal).astype(np.float32)

train_loader_r = make_loader(X_recal_norm, y_recal, w_recal, train_idx)
val_loader_r = make_loader(X_recal_norm, y_recal, w_recal, val_idx, shuffle=False)

print("\n── Training RECALIBRATED reward model ──")
model_recal, tl_recal, vl_recal = train_reward_model(
    train_loader_r, val_loader_r, n_epochs=30, label="recalibrated"
)

# ════════════════════════════════════════════════════════════════════════════
# 5.  POST-RECALIBRATION PDAS
# ════════════════════════════════════════════════════════════════════════════
# Simulate recalibrated preferences: high-weight timesteps dominate
recal_weights_norm = recal_weights / recal_weights.sum(axis=1, keepdims=True)
recal_prefs = np.zeros_like(all_high_prefs)
for u in range(N_HIGH_AI):
    for t in range(N_TIMESTEPS):
        # blend toward weighted mean (down-weight drifted steps)
        recal_prefs[u, t] = all_high_prefs[u, t] * recal_weights[u, t]

pdas_recalibrated = compute_pdas(recal_prefs, low_ai_prefs)
print(f"\nRecalibrated PDAS (after recalibration): {pdas_recalibrated:.4f}")
experiment_data["longitudinal_preferences"]["pdas_recalibrated"] = pdas_recalibrated

# ════════════════════════════════════════════════════════════════════════════
# 6.  VISUALISATIONS
# ════════════════════════════════════════════════════════════════════════════
epochs = list(range(1, 31))

# — loss curves ——————————————————————————————————————————————————————————────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(epochs, tl_base, label="Baseline Train", color="steelblue")
axes[0].plot(epochs, vl_base, label="Baseline Val", color="steelblue", linestyle="--")
axes[0].plot(epochs, tl_recal, label="Recalibrated Train", color="darkorange")
axes[0].plot(
    epochs, vl_recal, label="Recalibrated Val", color="darkorange", linestyle="--"
)
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("MSE Loss")
axes[0].set_title("Reward Model Training Loss")
axes[0].legend()

# — preference trajectories ——————————————————————————————————————————————————
dim = 0  # visualise first preference dimension
mean_high = high_ai_prefs[:, :, dim].mean(axis=0)
mean_low = low_ai_prefs[:, :, dim].mean(axis=0)
axes[1].plot(
    range(N_TIMESTEPS), mean_high, marker="o", label="High-AI users", color="red"
)
axes[1].plot(
    range(N_TIMESTEPS), mean_low, marker="s", label="Low-AI users", color="green"
)
axes[1].axhline(
    ai_modal_pref[dim], color="purple", linestyle=":", label="AI Modal Pref"
)
axes[1].set_xlabel("Time Step")
axes[1].set_ylabel("Preference Dim 0")
axes[1].set_title("Preference Trajectory (Dim 0)")
axes[1].legend()
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "reward_model_loss_and_preference_trajectory.png"),
    dpi=120,
)
plt.close()

# — PDAS summary ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(
    ["Baseline PDAS", "Recalibrated PDAS"],
    [pdas_baseline, pdas_recalibrated],
    color=["crimson", "steelblue"],
    width=0.4,
)
for bar, val in zip(bars, [pdas_baseline, pdas_recalibrated]):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.4f}",
        ha="center",
        fontsize=12,
    )
ax.set_ylim(0, 1)
ax.set_ylabel("PDAS")
ax.set_title("Preference Drift Attribution Score")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pdas_comparison.png"), dpi=120)
plt.close()

# — per-epoch PDAS proxy ─────────────────────────────────────────────────────
pdas_arr = np.array(experiment_data["longitudinal_preferences"]["pdas_per_epoch"])
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(epochs, pdas_arr[:30], label="Baseline epoch-PDAS", color="crimson")
ax.plot(epochs, pdas_arr[30:], label="Recalibrated epoch-PDAS", color="steelblue")
ax.set_xlabel("Epoch")
ax.set_ylabel("PDAS proxy")
ax.set_title("Per-Epoch PDAS Proxy During Training")
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "per_epoch_pdas.png"), dpi=120)
plt.close()

# ════════════════════════════════════════════════════════════════════════════
# 7.  FINAL SUMMARY & SAVE
# ════════════════════════════════════════════════════════════════════════════
print("\n══════════════════════════════════════════")
print("  FINAL RESULTS SUMMARY")
print("══════════════════════════════════════════")
print(f"  Baseline   PDAS : {pdas_baseline:.4f}")
print(f"  Recalibrated PDAS: {pdas_recalibrated:.4f}")
print(f"  PDAS Reduction   : {pdas_baseline - pdas_recalibrated:.4f}")
print(f"  Final baseline val loss    : {vl_base[-1]:.4f}")
print(f"  Final recalibrated val loss: {vl_recal[-1]:.4f}")
print("══════════════════════════════════════════")

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
np.save(os.path.join(working_dir, "high_ai_prefs.npy"), high_ai_prefs)
np.save(os.path.join(working_dir, "low_ai_prefs.npy"), low_ai_prefs)
np.save(os.path.join(working_dir, "recal_weights.npy"), recal_weights)
print("\nAll results saved to", working_dir)
