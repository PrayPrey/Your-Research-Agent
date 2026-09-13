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
    "learning_rate_1e-3": {
        "synthetic_qa": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc_single_turn": [],
            "auroc_drift": [],
            "auroc_dac": [],
            "auroc_neural": [],
            "drift_scores": [],
            "single_turn_confidence": [],
            "labels": [],
        },
        "halueval_sim": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc_single_turn": [],
            "auroc_drift": [],
            "auroc_dac": [],
            "auroc_neural": [],
            "drift_scores": [],
            "single_turn_confidence": [],
            "labels": [],
        },
        "sciq_sim": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc_single_turn": [],
            "auroc_drift": [],
            "auroc_dac": [],
            "auroc_neural": [],
            "drift_scores": [],
            "single_turn_confidence": [],
            "labels": [],
        },
    },
    "learning_rate_1e-4": {
        "synthetic_qa": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc_single_turn": [],
            "auroc_drift": [],
            "auroc_dac": [],
            "auroc_neural": [],
            "drift_scores": [],
            "single_turn_confidence": [],
            "labels": [],
        },
        "halueval_sim": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc_single_turn": [],
            "auroc_drift": [],
            "auroc_dac": [],
            "auroc_neural": [],
            "drift_scores": [],
            "single_turn_confidence": [],
            "labels": [],
        },
        "sciq_sim": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "auroc_single_turn": [],
            "auroc_drift": [],
            "auroc_dac": [],
            "auroc_neural": [],
            "drift_scores": [],
            "single_turn_confidence": [],
            "labels": [],
        },
    },
}

N_CLAIMS = 1000
N_TURNS = 8
HALLUCINATION_RATE = 0.4


def generate_confidence_trajectory(is_hallucinated, n_turns, dataset_type="standard"):
    if dataset_type == "halueval":
        # HaluEval-style: hallucinations have high initial confidence but sharp drops
        if is_hallucinated:
            base_conf = np.random.uniform(0.6, 0.9)
            drift_magnitude = np.random.uniform(0.2, 0.4)
            noise_std = 0.12
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(-0.05, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.15 * (trajectory[-1] - base_conf * 0.5)
                new_val = (
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
                )
                new_val = np.clip(new_val, 0.05, 0.99)
                trajectory.append(new_val)
        else:
            base_conf = np.random.uniform(0.70, 0.97)
            drift_magnitude = np.random.uniform(0.01, 0.06)
            noise_std = 0.025
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.35 * (trajectory[-1] - base_conf)
                new_val = (
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
                )
                new_val = np.clip(new_val, 0.05, 0.99)
                trajectory.append(new_val)
    elif dataset_type == "sciq":
        # SciQ-style: science domain, hallucinations oscillate more, correct are very stable
        if is_hallucinated:
            base_conf = np.random.uniform(0.35, 0.80)
            drift_magnitude = np.random.uniform(0.18, 0.38)
            noise_std = 0.11
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.1 * (trajectory[-1] - base_conf)
                new_val = (
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
                )
                new_val = np.clip(new_val, 0.05, 0.99)
                trajectory.append(new_val)
        else:
            base_conf = np.random.uniform(0.75, 0.99)
            drift_magnitude = np.random.uniform(0.01, 0.05)
            noise_std = 0.02
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.4 * (trajectory[-1] - base_conf)
                new_val = (
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
                )
                new_val = np.clip(new_val, 0.05, 0.99)
                trajectory.append(new_val)
    else:
        # Standard synthetic_qa
        if is_hallucinated:
            base_conf = np.random.uniform(0.4, 0.85)
            drift_magnitude = np.random.uniform(0.15, 0.35)
            noise_std = 0.10
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.2 * (trajectory[-1] - base_conf)
                new_val = (
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
                )
                new_val = np.clip(new_val, 0.05, 0.99)
                trajectory.append(new_val)
        else:
            base_conf = np.random.uniform(0.65, 0.97)
            drift_magnitude = np.random.uniform(0.02, 0.08)
            noise_std = 0.03
            trajectory = [base_conf]
            for t in range(1, n_turns):
                step = np.random.normal(0, drift_magnitude / np.sqrt(n_turns))
                reversion = -0.3 * (trajectory[-1] - base_conf)
                new_val = (
                    trajectory[-1] + step + reversion + np.random.normal(0, noise_std)
                )
                new_val = np.clip(new_val, 0.05, 0.99)
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


def extract_features(trajectories):
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

    autocorrs = np.array(
        [autocorr_lag1(trajectories[i]) for i in range(len(trajectories))]
    )
    autocorrs = np.nan_to_num(autocorrs, nan=0.0)
    return (
        single_turn_conf,
        drift_variance,
        drift_range,
        drift_std,
        drift_mean,
        drift_trend,
        autocorrs,
    )


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
    trajectories,
    labels,
    train_idx,
    val_idx,
    test_idx,
    lr,
    epochs,
    batch_size=32,
    hidden_dim=128,
    weight_decay=1e-4,
    dataset_name="synthetic_qa",
    lr_key="learning_rate_1e-3",
):
    X_traj = torch.tensor(trajectories, dtype=torch.float32)
    y_all = labels.astype(np.float32)
    X_train = X_traj[train_idx].to(device)
    X_val = X_traj[val_idx].to(device)
    X_test = X_traj[test_idx].to(device)
    y_train = torch.tensor(y_all[train_idx], dtype=torch.float32).to(device)
    y_val_np = y_all[val_idx]
    y_test_np = y_all[test_idx]
    criterion = nn.BCELoss()
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    torch.manual_seed(42)
    model = DACNet(input_dim=X_traj.shape[1], hidden_dim=hidden_dim).to(device)
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
        experiment_data[lr_key][dataset_name]["metrics"]["train"].append(
            float(train_auroc_nn)
        )
        experiment_data[lr_key][dataset_name]["metrics"]["val"].append(
            float(val_auroc_nn)
        )
        experiment_data[lr_key][dataset_name]["losses"]["train"].append(
            float(epoch_loss)
        )
        experiment_data[lr_key][dataset_name]["losses"]["val"].append(float(val_loss))
        if (epoch + 1) % 20 == 0:
            print(
                f"  Epoch {epoch+1:3d}: val_loss={val_loss:.4f}, val_auroc={val_auroc_nn:.4f}"
            )
    model.eval()
    with torch.no_grad():
        test_pred = model(X_test).cpu().numpy()
    auroc_test = roc_auc_score(y_test_np, test_pred)
    return (
        auroc_test,
        test_pred,
        train_losses,
        val_losses,
        train_aurocs,
        val_aurocs,
        model,
    )


def run_dataset_experiment(
    dataset_name,
    dataset_type,
    n_claims=1000,
    n_turns=8,
    hallucination_rate=0.4,
    seed=42,
):
    print(f"\n{'='*60}")
    print(f"Dataset: {dataset_name} (type={dataset_type})")
    print(f"{'='*60}")
    labels, trajectories = generate_dataset(
        n_claims, n_turns, hallucination_rate, dataset_type=dataset_type, seed=seed
    )
    print(f"Generated {n_claims} claims, {n_turns} turns each")
    print(f"Hallucinated: {labels.sum()}, Correct: {(1-labels).sum()}")
    train_idx, val_idx, test_idx = split_data(n_claims, seed=seed)
    (
        single_turn_conf,
        drift_variance,
        drift_range,
        drift_std,
        drift_mean,
        drift_trend,
        autocorrs,
    ) = extract_features(trajectories)
    print(
        f"Drift variance - Hallucinated: {drift_variance[labels==1].mean():.4f}, Correct: {drift_variance[labels==0].mean():.4f}"
    )
    # Baselines
    single_turn_score = -single_turn_conf
    auroc_single_test = roc_auc_score(labels[test_idx], single_turn_score[test_idx])
    auroc_drift_test = roc_auc_score(labels[test_idx], drift_variance[test_idx])
    print(f"Single-Turn AUROC: {auroc_single_test:.4f}")
    print(f"Drift Variance AUROC: {auroc_drift_test:.4f}")
    # DAC LogReg
    feature_matrix = np.column_stack(
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
    scaler = StandardScaler()
    X_train_lr = scaler.fit_transform(feature_matrix[train_idx])
    X_val_lr = scaler.transform(feature_matrix[val_idx])
    X_test_lr = scaler.transform(feature_matrix[test_idx])
    y_train_lr = labels[train_idx]
    y_test_lr = labels[test_idx]
    dac_model = LogisticRegression(C=0.5, max_iter=1000, random_state=42)
    dac_model.fit(X_train_lr, y_train_lr)
    dac_test_proba = dac_model.predict_proba(X_test_lr)[:, 1]
    auroc_dac_test = roc_auc_score(y_test_lr, dac_test_proba)
    print(f"DAC (LogReg) AUROC: {auroc_dac_test:.4f}")
    results = {
        "labels": labels,
        "trajectories": trajectories,
        "train_idx": train_idx,
        "val_idx": val_idx,
        "test_idx": test_idx,
        "single_turn_conf": single_turn_conf,
        "drift_variance": drift_variance,
        "auroc_single_test": auroc_single_test,
        "auroc_drift_test": auroc_drift_test,
        "auroc_dac_test": auroc_dac_test,
    }
    return results


# ─────────────────────────────────────────────
# Run all three datasets
# ─────────────────────────────────────────────
datasets_config = [
    ("synthetic_qa", "standard", 42),
    ("halueval_sim", "halueval", 123),
    ("sciq_sim", "sciq", 456),
]

all_results = {}
for ds_name, ds_type, ds_seed in datasets_config:
    all_results[ds_name] = run_dataset_experiment(ds_name, ds_type, seed=ds_seed)

# ─────────────────────────────────────────────
# Train Neural DAC for both LRs on all datasets
# ─────────────────────────────────────────────
EPOCHS_1e3 = 100
EPOCHS_1e4 = 200
BATCH_SIZE = 32
HIDDEN_DIM = 128

neural_aurocs = {"learning_rate_1e-3": {}, "learning_rate_1e-4": {}}
neural_preds = {"learning_rate_1e-3": {}, "learning_rate_1e-4": {}}
train_losses_all = {"learning_rate_1e-3": {}, "learning_rate_1e-4": {}}
val_losses_all = {"learning_rate_1e-3": {}, "learning_rate_1e-4": {}}
train_aurocs_all = {"learning_rate_1e-3": {}, "learning_rate_1e-4": {}}
val_aurocs_all = {"learning_rate_1e-3": {}, "learning_rate_1e-4": {}}

for ds_name, _, _ in datasets_config:
    res = all_results[ds_name]
    labels = res["labels"]
    trajectories = res["trajectories"]
    train_idx = res["train_idx"]
    val_idx = res["val_idx"]
    test_idx = res["test_idx"]

    print(f"\n{'='*55}")
    print(f"Neural DAC LR=1e-3 | {ds_name}")
    print(f"{'='*55}")
    auroc_1e3, pred_1e3, tl_1e3, vl_1e3, ta_1e3, va_1e3, _ = train_neural_dac(
        trajectories,
        labels,
        train_idx,
        val_idx,
        test_idx,
        lr=1e-3,
        epochs=EPOCHS_1e3,
        batch_size=BATCH_SIZE,
        hidden_dim=HIDDEN_DIM,
        weight_decay=1e-4,
        dataset_name=ds_name,
        lr_key="learning_rate_1e-3",
    )
    neural_aurocs["learning_rate_1e-3"][ds_name] = auroc_1e3
    neural_preds["learning_rate_1e-3"][ds_name] = pred_1e3
    train_losses_all["learning_rate_1e-3"][ds_name] = tl_1e3
    val_losses_all["learning_rate_1e-3"][ds_name] = vl_1e3
    train_aurocs_all["learning_rate_1e-3"][ds_name] = ta_1e3
    val_aurocs_all["learning_rate_1e-3"][ds_name] = va_1e3
    print(f"Neural DAC (LR=1e-3) Test AUROC [{ds_name}]: {auroc_1e3:.4f}")

    print(f"\n{'='*55}")
    print(f"Neural DAC LR=1e-4 | {ds_name}")
    print(f"{'='*55}")
    auroc_1e4, pred_1e4, tl_1e4, vl_1e4, ta_1e4, va_1e4, _ = train_neural_dac(
        trajectories,
        labels,
        train_idx,
        val_idx,
        test_idx,
        lr=1e-4,
        epochs=EPOCHS_1e4,
        batch_size=BATCH_SIZE,
        hidden_dim=HIDDEN_DIM,
        weight_decay=1e-5,
        dataset_name=ds_name,
        lr_key="learning_rate_1e-4",
    )
    neural_aurocs["learning_rate_1e-4"][ds_name] = auroc_1e4
    neural_preds["learning_rate_1e-4"][ds_name] = pred_1e4
    train_losses_all["learning_rate_1e-4"][ds_name] = tl_1e4
    val_losses_all["learning_rate_1e-4"][ds_name] = vl_1e4
    train_aurocs_all["learning_rate_1e-4"][ds_name] = ta_1e4
    val_aurocs_all["learning_rate_1e-4"][ds_name] = va_1e4
    print(f"Neural DAC (LR=1e-4) Test AUROC [{ds_name}]: {auroc_1e4:.4f}")

    # Store in experiment_data
    for lr_key, pred, auroc in [
        ("learning_rate_1e-3", pred_1e3, auroc_1e3),
        ("learning_rate_1e-4", pred_1e4, auroc_1e4),
    ]:
        experiment_data[lr_key][ds_name]["predictions"] = pred.tolist()
        experiment_data[lr_key][ds_name]["ground_truth"] = labels[test_idx].tolist()
        experiment_data[lr_key][ds_name]["auroc_single_turn"] = [
            res["auroc_single_test"]
        ]
        experiment_data[lr_key][ds_name]["auroc_drift"] = [res["auroc_drift_test"]]
        experiment_data[lr_key][ds_name]["auroc_dac"] = [res["auroc_dac_test"]]
        experiment_data[lr_key][ds_name]["auroc_neural"] = [auroc]
        experiment_data[lr_key][ds_name]["drift_scores"] = res[
            "drift_variance"
        ].tolist()
        experiment_data[lr_key][ds_name]["single_turn_confidence"] = res[
            "single_turn_conf"
        ].tolist()
        experiment_data[lr_key][ds_name]["labels"] = labels.tolist()

# ─────────────────────────────────────────────
# Results Summary
# ─────────────────────────────────────────────
print("\n" + "=" * 65)
print("RESULTS SUMMARY (Test Set)")
print("=" * 65)
for ds_name, _, _ in datasets_config:
    res = all_results[ds_name]
    print(f"\n[{ds_name}]")
    print(f"  Single-Turn Confidence AUROC:    {res['auroc_single_test']:.4f}")
    print(f"  Drift Variance AUROC:            {res['auroc_drift_test']:.4f}")
    print(f"  DAC (Logistic Regression) AUROC: {res['auroc_dac_test']:.4f}")
    print(
        f"  Neural DAC (LR=1e-3) AUROC:      {neural_aurocs['learning_rate_1e-3'][ds_name]:.4f}"
    )
    print(
        f"  Neural DAC (LR=1e-4) AUROC:      {neural_aurocs['learning_rate_1e-4'][ds_name]:.4f}"
    )
    imp_lr = (
        neural_aurocs["learning_rate_1e-4"][ds_name]
        - neural_aurocs["learning_rate_1e-3"][ds_name]
    ) * 100
    imp_vs_single = (
        neural_aurocs["learning_rate_1e-4"][ds_name] - res["auroc_single_test"]
    ) * 100
    print(f"  Improvement LR=1e-4 vs LR=1e-3: {imp_lr:.2f}%")
    print(f"  Improvement Neural(1e-4) vs Single: {imp_vs_single:.2f}%")

# ─────────────────────────────────────────────
# Visualizations
# ─────────────────────────────────────────────
for ds_name, _, _ in datasets_config:
    res = all_results[ds_name]
    labels = res["labels"]
    trajectories = res["trajectories"]
    drift_variance = res["drift_variance"]

    # Confidence trajectories
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    hallu_idx = np.where(labels == 1)[0][:20]
    correct_idx = np.where(labels == 0)[0][:20]
    for i in hallu_idx:
        axes[0].plot(
            range(N_TURNS), trajectories[i], alpha=0.4, color="red", linewidth=1
        )
    axes[0].plot(
        range(N_TURNS),
        trajectories[hallu_idx].mean(axis=0),
        "r-",
        linewidth=2.5,
        label="Mean (Hallucinated)",
    )
    axes[0].set_title(f"Confidence Trajectories: Hallucinated [{ds_name}]", fontsize=12)
    axes[0].set_xlabel("Conversation Turn")
    axes[0].set_ylabel("Expressed Confidence")
    axes[0].set_ylim(0, 1)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    for i in correct_idx:
        axes[1].plot(
            range(N_TURNS), trajectories[i], alpha=0.4, color="blue", linewidth=1
        )
    axes[1].plot(
        range(N_TURNS),
        trajectories[correct_idx].mean(axis=0),
        "b-",
        linewidth=2.5,
        label="Mean (Correct)",
    )
    axes[1].set_title(f"Confidence Trajectories: Correct [{ds_name}]", fontsize=12)
    axes[1].set_xlabel("Conversation Turn")
    axes[1].set_ylabel("Expressed Confidence")
    axes[1].set_ylim(0, 1)
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    plt.suptitle(f"Confidence Drift: {ds_name}", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"confidence_trajectories_{ds_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # Drift variance distribution
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
    ax.set_title(f"Distribution of Confidence Drift [{ds_name}]")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"drift_variance_distribution_{ds_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # Training curves comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    tl_1e3 = train_losses_all["learning_rate_1e-3"][ds_name]
    vl_1e3 = val_losses_all["learning_rate_1e-3"][ds_name]
    ta_1e3 = train_aurocs_all["learning_rate_1e-3"][ds_name]
    va_1e3 = val_aurocs_all["learning_rate_1e-3"][ds_name]
    tl_1e4 = train_losses_all["learning_rate_1e-4"][ds_name]
    vl_1e4 = val_losses_all["learning_rate_1e-4"][ds_name]
    ta_1e4 = train_aurocs_all["learning_rate_1e-4"][ds_name]
    va_1e4 = val_aurocs_all["learning_rate_1e-4"][ds_name]
    axes[0].plot(tl_1e3, label="Train(LR=1e-3)", color="blue", linestyle="-")
    axes[0].plot(vl_1e3, label="Val(LR=1e-3)", color="blue", linestyle="--")
    axes[0].plot(tl_1e4, label="Train(LR=1e-4)", color="orange", linestyle="-")
    axes[0].plot(vl_1e4, label="Val(LR=1e-4)", color="orange", linestyle="--")
    axes[0].set_title(f"Neural DAC Training Loss [{ds_name}]")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("BCE Loss")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    axes[1].plot(ta_1e3, label="Train AUROC(LR=1e-3)", color="blue", linestyle="-")
    axes[1].plot(va_1e3, label="Val AUROC(LR=1e-3)", color="blue", linestyle="--")
    axes[1].plot(ta_1e4, label="Train AUROC(LR=1e-4)", color="orange", linestyle="-")
    axes[1].plot(va_1e4, label="Val AUROC(LR=1e-4)", color="orange", linestyle="--")
    axes[1].set_title(f"Neural DAC AUROC [{ds_name}]")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("AUROC")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"neural_dac_training_curves_{ds_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # AUROC bar chart
    fig, ax = plt.subplots(figsize=(10, 5))
    methods = [
        "Single-Turn\nConfidence",
        "Drift\nVariance",
        "DAC\n(LogReg)",
        "Neural DAC\n(LR=1e-3)",
        "Neural DAC\n(LR=1e-4)",
    ]
    aurocs = [
        res["auroc_single_test"],
        res["auroc_drift_test"],
        res["auroc_dac_test"],
        neural_aurocs["learning_rate_1e-3"][ds_name],
        neural_aurocs["learning_rate_1e-4"][ds_name],
    ]
    colors = ["gray", "orange", "green", "blue", "purple"]
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
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("AUROC (Test Set)", fontsize=12)
    ax.set_title(f"Hallucination Detection AUROC [{ds_name}]", fontsize=13)
    ax.axhline(y=0.5, color="red", linestyle="--", alpha=0.5, label="Random Baseline")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"auroc_comparison_{ds_name}.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

# Cross-dataset AUROC comparison
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(datasets_config))
width = 0.15
ds_names = [d[0] for d in datasets_config]
metrics_labels = [
    "Single-Turn",
    "Drift Var",
    "DAC LogReg",
    "Neural 1e-3",
    "Neural 1e-4",
]
colors = ["gray", "orange", "green", "blue", "purple"]
for i, (metric_label, color) in enumerate(zip(metrics_labels, colors)):
    vals = []
    for ds_name in ds_names:
        res = all_results[ds_name]
        if metric_label == "Single-Turn":
            vals.append(res["auroc_single_test"])
        elif metric_label == "Drift Var":
            vals.append(res["auroc_drift_test"])
        elif metric_label == "DAC LogReg":
            vals.append(res["auroc_dac_test"])
        elif metric_label == "Neural 1e-3":
            vals.append(neural_aurocs["learning_rate_1e-3"][ds_name])
        else:
            vals.append(neural_aurocs["learning_rate_1e-4"][ds_name])
    ax.bar(
        x + i * width,
        vals,
        width,
        label=metric_label,
        color=color,
        alpha=0.8,
        edgecolor="black",
    )
ax.set_xlabel("Dataset")
ax.set_ylabel("Test AUROC")
ax.set_title("Cross-Dataset AUROC Comparison")
ax.set_xticks(x + width * 2)
ax.set_xticklabels(ds_names)
ax.legend()
ax.set_ylim(0, 1.1)
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "cross_dataset_auroc_comparison.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nAll data saved to", working_dir)
print("Done!")
