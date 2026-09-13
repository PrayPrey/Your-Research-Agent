import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
torch.manual_seed(42)

experiment_data = {
    "synthetic_qa": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "auroc_single_turn": [],
        "auroc_drift": [],
        "auroc_dac": [],
        "drift_scores": [],
        "single_turn_confidence": [],
        "labels": [],
        "confidence_trajectories_hallucinated": [],
        "confidence_trajectories_correct": [],
    }
}

# ─────────────────────────────────────────────
# 1. Synthetic Data Generation
# ─────────────────────────────────────────────
N_CLAIMS = 1000  # number of distinct factual claims
N_TURNS = 8  # turns per conversation
HALLUCINATION_RATE = 0.4  # 40% of claims are hallucinated

labels = (np.random.rand(N_CLAIMS) < HALLUCINATION_RATE).astype(int)  # 1=hallucinated


def generate_confidence_trajectory(is_hallucinated, n_turns, base_noise=0.05):
    """
    Simulate confidence scores across turns.
    Hallucinated: high drift (large variance, possible trend reversals)
    Correct: low drift (stable confidence, small noise)
    """
    if is_hallucinated:
        # Higher base uncertainty + high drift
        base_conf = np.random.uniform(0.4, 0.85)
        drift_magnitude = np.random.uniform(0.15, 0.35)
        noise_std = 0.10
        # Random walk with mean reversion
        trajectory = [base_conf]
        for t in range(1, n_turns):
            step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
            reversion = -0.2 * (trajectory[-1] - base_conf)
            new_val = trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
            new_val = np.clip(new_val, 0.05, 0.99)
            trajectory.append(new_val)
    else:
        # Low drift, high consistent confidence
        base_conf = np.random.uniform(0.65, 0.97)
        drift_magnitude = np.random.uniform(0.02, 0.08)
        noise_std = 0.03
        trajectory = [base_conf]
        for t in range(1, n_turns):
            step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
            reversion = -0.3 * (trajectory[-1] - base_conf)
            new_val = trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
            new_val = np.clip(new_val, 0.05, 0.99)
            trajectory.append(new_val)
    return np.array(trajectory)


# Generate trajectories
trajectories = np.array(
    [generate_confidence_trajectory(labels[i], N_TURNS) for i in range(N_CLAIMS)]
)

print(f"Generated {N_CLAIMS} claims, {N_TURNS} turns each")
print(f"Hallucinated: {labels.sum()}, Correct: {(1-labels).sum()}")

# ─────────────────────────────────────────────
# 2. Feature Extraction
# ─────────────────────────────────────────────
# Single-turn confidence: just the first turn
single_turn_conf = trajectories[:, 0]  # first turn confidence

# Drift features
drift_variance = np.var(trajectories, axis=1)
drift_range = np.max(trajectories, axis=1) - np.min(trajectories, axis=1)
drift_std = np.std(trajectories, axis=1)
drift_mean = np.mean(trajectories, axis=1)
drift_trend = trajectories[:, -1] - trajectories[:, 0]  # final - initial


# Auto-correlation as stability measure
def autocorr_lag1(traj):
    if len(traj) < 2:
        return 0
    return np.corrcoef(traj[:-1], traj[1:])[0, 1]


autocorrs = np.array([autocorr_lag1(trajectories[i]) for i in range(N_CLAIMS)])
autocorrs = np.nan_to_num(autocorrs, nan=0.0)

print(f"\nDrift variance stats:")
print(f"  Hallucinated mean: {drift_variance[labels==1].mean():.4f}")
print(f"  Correct mean:      {drift_variance[labels==0].mean():.4f}")

# ─────────────────────────────────────────────
# 3. Train/Val/Test Split
# ─────────────────────────────────────────────
n_train = int(0.6 * N_CLAIMS)
n_val = int(0.2 * N_CLAIMS)
idx = np.arange(N_CLAIMS)
np.random.shuffle(idx)

train_idx = idx[:n_train]
val_idx = idx[n_train : n_train + n_val]
test_idx = idx[n_train + n_val :]

print(f"\nSplit: train={len(train_idx)}, val={len(val_idx)}, test={len(test_idx)}")

# ─────────────────────────────────────────────
# 4. Baseline AUROC: Single-Turn Confidence
# ─────────────────────────────────────────────
# Higher confidence → less likely hallucinated → use negative confidence as score
single_turn_score = -single_turn_conf  # negate: higher score = more hallucinated

auroc_single_train = roc_auc_score(labels[train_idx], single_turn_score[train_idx])
auroc_single_val = roc_auc_score(labels[val_idx], single_turn_score[val_idx])
auroc_single_test = roc_auc_score(labels[test_idx], single_turn_score[test_idx])

print(f"\nSingle-Turn Confidence AUROC:")
print(f"  Train: {auroc_single_train:.4f}")
print(f"  Val:   {auroc_single_val:.4f}")
print(f"  Test:  {auroc_single_test:.4f}")

# ─────────────────────────────────────────────
# 5. Drift-Only AUROC
# ─────────────────────────────────────────────
auroc_drift_train = roc_auc_score(labels[train_idx], drift_variance[train_idx])
auroc_drift_val = roc_auc_score(labels[val_idx], drift_variance[val_idx])
auroc_drift_test = roc_auc_score(labels[test_idx], drift_variance[test_idx])

print(f"\nDrift Variance AUROC:")
print(f"  Train: {auroc_drift_train:.4f}")
print(f"  Val:   {auroc_drift_val:.4f}")
print(f"  Test:  {auroc_drift_test:.4f}")

# ─────────────────────────────────────────────
# 6. DAC: Drift-Augmented Calibration (Logistic Regression)
# ─────────────────────────────────────────────
feature_matrix = np.column_stack(
    [
        single_turn_conf,  # single turn confidence
        drift_variance,  # variance across turns
        drift_range,  # range
        drift_std,  # std dev
        drift_mean,  # mean confidence
        drift_trend,  # trend direction
        autocorrs,  # stability (autocorrelation)
    ]
)

scaler = StandardScaler()
X_train = scaler.fit_transform(feature_matrix[train_idx])
X_val = scaler.transform(feature_matrix[val_idx])
X_test = scaler.transform(feature_matrix[test_idx])
y_train = labels[train_idx]
y_val = labels[val_idx]
y_test = labels[test_idx]

dac_model = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
dac_model.fit(X_train, y_train)

dac_train_proba = dac_model.predict_proba(X_train)[:, 1]
dac_val_proba = dac_model.predict_proba(X_val)[:, 1]
dac_test_proba = dac_model.predict_proba(X_test)[:, 1]

auroc_dac_train = roc_auc_score(y_train, dac_train_proba)
auroc_dac_val = roc_auc_score(y_val, dac_val_proba)
auroc_dac_test = roc_auc_score(y_test, dac_test_proba)

print(f"\nDAC (Drift-Augmented Calibration) AUROC:")
print(f"  Train: {auroc_dac_train:.4f}")
print(f"  Val:   {auroc_dac_val:.4f}")
print(f"  Test:  {auroc_dac_test:.4f}")


# ─────────────────────────────────────────────
# 7. Neural DAC Model
# ─────────────────────────────────────────────
class DACNet(nn.Module):
    def __init__(self, input_dim, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


# Use full trajectory as input to neural model
traj_features = trajectories  # (N, N_TURNS)

X_traj_train = torch.tensor(traj_features[train_idx], dtype=torch.float32).to(device)
X_traj_val = torch.tensor(traj_features[val_idx], dtype=torch.float32).to(device)
X_traj_test = torch.tensor(traj_features[test_idx], dtype=torch.float32).to(device)
y_train_t = torch.tensor(y_train, dtype=torch.float32).to(device)
y_val_t = torch.tensor(y_val, dtype=torch.float32).to(device)

neural_model = DACNet(input_dim=N_TURNS, hidden_dim=64).to(device)
optimizer = torch.optim.Adam(neural_model.parameters(), lr=1e-3, weight_decay=1e-4)
criterion = nn.BCELoss()

train_dataset = TensorDataset(X_traj_train, y_train_t)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

EPOCHS = 50
train_losses, val_losses = [], []
train_aurocs, val_aurocs = [], []

print("\nTraining Neural DAC Model...")
for epoch in range(EPOCHS):
    neural_model.train()
    epoch_loss = 0.0
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        pred = neural_model(X_batch)
        loss = criterion(pred, y_batch)
        loss.backward()
        optimizer.step()
        epoch_loss += loss.item() * len(y_batch)
    epoch_loss /= len(train_idx)

    neural_model.eval()
    with torch.no_grad():
        val_pred = neural_model(X_traj_val).cpu().numpy()
        train_pred_all = neural_model(X_traj_train).cpu().numpy()
        val_loss = criterion(
            torch.tensor(val_pred), torch.tensor(y_val.astype(np.float32))
        ).item()
        train_auroc_nn = roc_auc_score(y_train, train_pred_all)
        val_auroc_nn = roc_auc_score(y_val, val_pred)

    train_losses.append(epoch_loss)
    val_losses.append(val_loss)
    train_aurocs.append(train_auroc_nn)
    val_aurocs.append(val_auroc_nn)

    experiment_data["synthetic_qa"]["metrics"]["train"].append(train_auroc_nn)
    experiment_data["synthetic_qa"]["metrics"]["val"].append(val_auroc_nn)
    experiment_data["synthetic_qa"]["losses"]["train"].append(epoch_loss)
    experiment_data["synthetic_qa"]["losses"]["val"].append(val_loss)

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch {epoch+1:3d}: val_loss = {val_loss:.4f}, val_auroc = {val_auroc_nn:.4f}"
        )

neural_model.eval()
with torch.no_grad():
    neural_test_pred = neural_model(X_traj_test).cpu().numpy()
auroc_neural_test = roc_auc_score(y_test, neural_test_pred)
print(f"\nNeural DAC Test AUROC: {auroc_neural_test:.4f}")

# ─────────────────────────────────────────────
# 8. Results Summary
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("RESULTS SUMMARY (Test Set)")
print("=" * 55)
print(f"Single-Turn Confidence AUROC:     {auroc_single_test:.4f}")
print(f"Drift Variance AUROC:             {auroc_drift_test:.4f}")
print(f"DAC (Logistic Regression) AUROC:  {auroc_dac_test:.4f}")
print(f"Neural DAC AUROC:                 {auroc_neural_test:.4f}")
print(
    f"\nImprovement (DAC vs Single-Turn): {(auroc_dac_test - auroc_single_test)*100:.2f}%"
)
print(
    f"Improvement (Neural vs Single):   {(auroc_neural_test - auroc_single_test)*100:.2f}%"
)

# ─────────────────────────────────────────────
# 9. Visualizations
# ─────────────────────────────────────────────
# 9a. Confidence trajectories
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

hallu_idx = np.where(labels == 1)[0][:20]
correct_idx = np.where(labels == 0)[0][:20]

for i in hallu_idx:
    axes[0].plot(range(N_TURNS), trajectories[i], alpha=0.4, color="red", linewidth=1)
axes[0].plot(
    range(N_TURNS),
    trajectories[hallu_idx].mean(axis=0),
    "r-",
    linewidth=2.5,
    label="Mean (Hallucinated)",
)
axes[0].set_title("Confidence Trajectories: Hallucinated Claims", fontsize=13)
axes[0].set_xlabel("Conversation Turn")
axes[0].set_ylabel("Expressed Confidence")
axes[0].set_ylim(0, 1)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

for i in correct_idx:
    axes[1].plot(range(N_TURNS), trajectories[i], alpha=0.4, color="blue", linewidth=1)
axes[1].plot(
    range(N_TURNS),
    trajectories[correct_idx].mean(axis=0),
    "b-",
    linewidth=2.5,
    label="Mean (Correct)",
)
axes[1].set_title("Confidence Trajectories: Correct Claims", fontsize=13)
axes[1].set_xlabel("Conversation Turn")
axes[1].set_ylabel("Expressed Confidence")
axes[1].set_ylim(0, 1)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.suptitle(
    "Confidence Drift: Hallucinated vs Correct Claims", fontsize=15, fontweight="bold"
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "confidence_trajectories.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# 9b. Drift variance distribution
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(
    drift_variance[labels == 0],
    bins=40,
    alpha=0.6,
    color="blue",
    label="Correct",
    density=True,
)
ax.hist(
    drift_variance[labels == 1],
    bins=40,
    alpha=0.6,
    color="red",
    label="Hallucinated",
    density=True,
)
ax.set_xlabel("Within-Conversation Confidence Variance (Drift)")
ax.set_ylabel("Density")
ax.set_title("Distribution of Confidence Drift by Hallucination Label")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "drift_variance_distribution.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# 9c. Training curves
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(train_losses, label="Train Loss", color="blue")
axes[0].plot(val_losses, label="Val Loss", color="orange")
axes[0].set_title("Neural DAC Training Loss")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("BCE Loss")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(train_aurocs, label="Train AUROC", color="blue")
axes[1].plot(val_aurocs, label="Val AUROC", color="orange")
axes[1].set_title("Neural DAC AUROC During Training")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("AUROC")
axes[1].legend()
axes[1].grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "neural_dac_training_curves.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# 9d. AUROC comparison bar chart
fig, ax = plt.subplots(figsize=(8, 5))
methods = ["Single-Turn\nConfidence", "Drift\nVariance", "DAC\n(LogReg)", "Neural\nDAC"]
aurocs = [auroc_single_test, auroc_drift_test, auroc_dac_test, auroc_neural_test]
colors = ["gray", "orange", "green", "blue"]
bars = ax.bar(methods, aurocs, color=colors, alpha=0.8, edgecolor="black")
for bar, val in zip(bars, aurocs):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontweight="bold",
    )
ax.set_ylim(0, 1.05)
ax.set_ylabel("AUROC (Test Set)", fontsize=12)
ax.set_title("Hallucination Detection AUROC: Method Comparison", fontsize=13)
ax.axhline(y=0.5, color="red", linestyle="--", alpha=0.5, label="Random Baseline")
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "auroc_comparison.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# ─────────────────────────────────────────────
# 10. Save All Data
# ─────────────────────────────────────────────
experiment_data["synthetic_qa"]["predictions"] = neural_test_pred.tolist()
experiment_data["synthetic_qa"]["ground_truth"] = y_test.tolist()
experiment_data["synthetic_qa"]["auroc_single_turn"] = [auroc_single_test]
experiment_data["synthetic_qa"]["auroc_drift"] = [auroc_drift_test]
experiment_data["synthetic_qa"]["auroc_dac"] = [auroc_dac_test]
experiment_data["synthetic_qa"]["drift_scores"] = drift_variance.tolist()
experiment_data["synthetic_qa"]["single_turn_confidence"] = single_turn_conf.tolist()
experiment_data["synthetic_qa"]["labels"] = labels.tolist()
experiment_data["synthetic_qa"]["confidence_trajectories_hallucinated"] = trajectories[
    labels == 1
].tolist()
experiment_data["synthetic_qa"]["confidence_trajectories_correct"] = trajectories[
    labels == 0
].tolist()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nAll data saved to", working_dir)
print("Done!")
