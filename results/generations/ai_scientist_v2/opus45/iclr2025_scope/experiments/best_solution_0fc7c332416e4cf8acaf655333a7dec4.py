import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from scipy.stats import spearmanr
import matplotlib.pyplot as plt

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)

# Experiment data tracking for hyperparameter tuning
experiment_data = {
    "pred_hidden_tuning": {
        "synthetic_kv": {
            "metrics": {"train": {}, "val": {}},
            "losses": {"train": {}, "val": {}},
            "predictions": {},
            "ground_truth": {},
            "spearman_correlations": {},
            "best_val_corr": {},
        }
    }
}


class SyntheticKVDataset(Dataset):
    def __init__(
        self, num_samples=1000, seq_len=128, hidden_dim=64, num_layers=6, seed=42
    ):
        np.random.seed(seed)
        torch.manual_seed(seed)
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.hidden_dim = hidden_dim
        self.early_layer_reps = []
        self.positions = []
        self.late_layer_importance = []

        for _ in range(num_samples):
            early_rep = torch.randn(seq_len, hidden_dim)
            pos = torch.arange(seq_len).float() / seq_len
            importance = torch.zeros(seq_len)
            importance[:5] = 0.8 + 0.2 * torch.rand(5)
            norms = early_rep.norm(dim=1)
            norm_importance = (norms - norms.min()) / (norms.max() - norms.min() + 1e-8)
            importance += 0.3 * norm_importance
            periodic = 0.2 * torch.sin(pos * 4 * np.pi)
            importance += periodic
            num_key_tokens = np.random.randint(3, 8)
            key_positions = np.random.choice(seq_len, num_key_tokens, replace=False)
            importance[key_positions] += 0.5
            importance = (importance - importance.min()) / (
                importance.max() - importance.min() + 1e-8
            )
            importance += 0.1 * torch.rand(seq_len)
            importance = torch.clamp(importance, 0, 1)
            self.early_layer_reps.append(early_rep)
            self.positions.append(pos)
            self.late_layer_importance.append(importance)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return {
            "early_rep": self.early_layer_reps[idx],
            "position": self.positions[idx],
            "importance": self.late_layer_importance[idx],
        }


class ImportancePredictor(nn.Module):
    def __init__(self, hidden_dim=64, pos_dim=16, pred_hidden=128):
        super().__init__()
        self.pos_encoder = nn.Sequential(
            nn.Linear(1, pos_dim), nn.ReLU(), nn.Linear(pos_dim, pos_dim)
        )
        self.predictor = nn.Sequential(
            nn.Linear(hidden_dim + pos_dim, pred_hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(pred_hidden, pred_hidden // 2),
            nn.ReLU(),
            nn.Linear(pred_hidden // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, early_rep, position):
        batch_size, seq_len, _ = early_rep.shape
        pos_encoded = self.pos_encoder(position.unsqueeze(-1))
        combined = torch.cat([early_rep, pos_encoded], dim=-1)
        importance = self.predictor(combined).squeeze(-1)
        return importance


def train_epoch(model, dataloader, optimizer, criterion):
    model.train()
    total_loss = 0
    all_preds, all_targets = [], []
    for batch in dataloader:
        early_rep = batch["early_rep"].to(device)
        position = batch["position"].to(device)
        importance = batch["importance"].to(device)
        optimizer.zero_grad()
        pred_importance = model(early_rep, position)
        loss = criterion(pred_importance, importance)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        all_preds.append(pred_importance.detach().cpu().numpy())
        all_targets.append(importance.cpu().numpy())
    all_preds = np.concatenate(all_preds, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)
    correlations = [
        spearmanr(all_preds[i], all_targets[i])[0]
        for i in range(len(all_preds))
        if not np.isnan(spearmanr(all_preds[i], all_targets[i])[0])
    ]
    avg_corr = np.mean(correlations) if correlations else 0
    return total_loss / len(dataloader), avg_corr


def validate(model, dataloader, criterion):
    model.eval()
    total_loss = 0
    all_preds, all_targets = [], []
    with torch.no_grad():
        for batch in dataloader:
            early_rep = batch["early_rep"].to(device)
            position = batch["position"].to(device)
            importance = batch["importance"].to(device)
            pred_importance = model(early_rep, position)
            loss = criterion(pred_importance, importance)
            total_loss += loss.item()
            all_preds.append(pred_importance.cpu().numpy())
            all_targets.append(importance.cpu().numpy())
    all_preds = np.concatenate(all_preds, axis=0)
    all_targets = np.concatenate(all_targets, axis=0)
    correlations = [
        spearmanr(all_preds[i], all_targets[i])[0]
        for i in range(len(all_preds))
        if not np.isnan(spearmanr(all_preds[i], all_targets[i])[0])
    ]
    avg_corr = np.mean(correlations) if correlations else 0
    return total_loss / len(dataloader), avg_corr, all_preds, all_targets


# Create datasets with fixed seeds for fair comparison
print("Creating synthetic datasets...")
train_dataset = SyntheticKVDataset(
    num_samples=2000, seq_len=128, hidden_dim=64, seed=42
)
val_dataset = SyntheticKVDataset(num_samples=500, seq_len=128, hidden_dim=64, seed=123)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Hyperparameter tuning for pred_hidden
pred_hidden_values = [64, 128, 256, 512]
num_epochs = 50
results_summary = {}

print("\n=== Starting Hyperparameter Tuning for pred_hidden ===\n")

for pred_hidden in pred_hidden_values:
    print(f"\n--- Training with pred_hidden={pred_hidden} ---")
    torch.manual_seed(42)
    np.random.seed(42)

    model = ImportancePredictor(hidden_dim=64, pos_dim=16, pred_hidden=pred_hidden).to(
        device
    )
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.MSELoss()

    train_losses, val_losses = [], []
    train_corrs, val_corrs = [], []
    best_val_corr = -1
    best_preds, best_targets = None, None

    for epoch in range(num_epochs):
        train_loss, train_corr = train_epoch(model, train_loader, optimizer, criterion)
        val_loss, val_corr, val_preds, val_targets = validate(
            model, val_loader, criterion
        )

        train_losses.append(train_loss)
        val_losses.append(val_loss)
        train_corrs.append(train_corr)
        val_corrs.append(val_corr)

        if val_corr > best_val_corr:
            best_val_corr = val_corr
            best_preds = val_preds.copy()
            best_targets = val_targets.copy()
            torch.save(
                model.state_dict(),
                os.path.join(working_dir, f"best_model_pred_hidden_{pred_hidden}.pt"),
            )

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(
                f"Epoch {epoch+1}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, train_spearman={train_corr:.4f}, val_spearman={val_corr:.4f}"
            )

    # Store results
    key = str(pred_hidden)
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["losses"]["train"][
        key
    ] = train_losses
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["losses"]["val"][
        key
    ] = val_losses
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["metrics"]["train"][
        key
    ] = train_corrs
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["metrics"]["val"][
        key
    ] = val_corrs
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["predictions"][
        key
    ] = best_preds
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["ground_truth"][
        key
    ] = best_targets
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["best_val_corr"][
        key
    ] = best_val_corr
    experiment_data["pred_hidden_tuning"]["synthetic_kv"]["spearman_correlations"][
        key
    ] = val_corrs

    results_summary[pred_hidden] = {
        "best_val_corr": best_val_corr,
        "final_train_corr": train_corrs[-1],
        "final_val_loss": val_losses[-1],
    }
    print(
        f"pred_hidden={pred_hidden}: Best validation Spearman correlation = {best_val_corr:.4f}"
    )

# Find best configuration
best_pred_hidden = max(
    results_summary.keys(), key=lambda x: results_summary[x]["best_val_corr"]
)
print(f"\n=== Hyperparameter Tuning Results ===")
print(f"Best pred_hidden value: {best_pred_hidden}")
print(
    f"Best validation Spearman correlation: {results_summary[best_pred_hidden]['best_val_corr']:.4f}"
)

print("\nAll results:")
for ph in pred_hidden_values:
    print(
        f"  pred_hidden={ph}: val_spearman={results_summary[ph]['best_val_corr']:.4f}"
    )

# Visualization 1: Training curves comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = plt.cm.viridis(np.linspace(0, 1, len(pred_hidden_values)))

for i, pred_hidden in enumerate(pred_hidden_values):
    key = str(pred_hidden)
    axes[0].plot(
        experiment_data["pred_hidden_tuning"]["synthetic_kv"]["losses"]["val"][key],
        label=f"pred_hidden={pred_hidden}",
        color=colors[i],
    )
    axes[1].plot(
        experiment_data["pred_hidden_tuning"]["synthetic_kv"]["metrics"]["val"][key],
        label=f"pred_hidden={pred_hidden}",
        color=colors[i],
    )

axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Validation Loss (MSE)")
axes[0].set_title("Validation Loss vs Epoch for Different pred_hidden Values")
axes[0].legend()
axes[0].grid(True)

axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Validation Spearman Correlation")
axes[1].set_title("Validation Spearman Correlation vs Epoch")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pred_hidden_tuning_curves.png"), dpi=150)
plt.close()

# Visualization 2: Bar chart of best validation correlations
fig, ax = plt.subplots(figsize=(8, 5))
x_pos = range(len(pred_hidden_values))
best_corrs = [results_summary[ph]["best_val_corr"] for ph in pred_hidden_values]
bars = ax.bar(x_pos, best_corrs, color=colors)
ax.set_xticks(x_pos)
ax.set_xticklabels([str(ph) for ph in pred_hidden_values])
ax.set_xlabel("pred_hidden Value")
ax.set_ylabel("Best Validation Spearman Correlation")
ax.set_title("Hyperparameter Tuning: pred_hidden vs Performance")
ax.grid(True, axis="y")
for i, (bar, corr) in enumerate(zip(bars, best_corrs)):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{corr:.4f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pred_hidden_comparison.png"), dpi=150)
plt.close()

# Visualization 3: Prediction samples for best model
best_key = str(best_pred_hidden)
best_preds = experiment_data["pred_hidden_tuning"]["synthetic_kv"]["predictions"][
    best_key
]
best_targets = experiment_data["pred_hidden_tuning"]["synthetic_kv"]["ground_truth"][
    best_key
]

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
sample_indices = [0, 10, 20, 30]
for i, idx in enumerate(sample_indices):
    ax = axes[i // 2, i % 2]
    ax.plot(best_targets[idx], label="Actual Importance", alpha=0.7)
    ax.plot(best_preds[idx], label="Predicted Importance", alpha=0.7)
    sample_corr, _ = spearmanr(best_preds[idx], best_targets[idx])
    ax.set_xlabel("Token Position")
    ax.set_ylabel("Importance Score")
    ax.set_title(
        f"Sample {idx+1} (Spearman: {sample_corr:.3f}) - pred_hidden={best_pred_hidden}"
    )
    ax.legend()
    ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "best_model_prediction_samples.png"), dpi=150)
plt.close()

# Visualization 4: Correlation scatter for best model
fig, ax = plt.subplots(figsize=(6, 6))
flat_preds = best_preds.flatten()
flat_targets = best_targets.flatten()
subsample_idx = np.random.choice(
    len(flat_preds), min(5000, len(flat_preds)), replace=False
)
ax.scatter(flat_targets[subsample_idx], flat_preds[subsample_idx], alpha=0.3, s=1)
ax.plot([0, 1], [0, 1], "r--", label="Perfect prediction")
overall_corr = results_summary[best_pred_hidden]["best_val_corr"]
ax.set_xlabel("Actual Importance")
ax.set_ylabel("Predicted Importance")
ax.set_title(
    f"Best Model (pred_hidden={best_pred_hidden}) - Spearman: {overall_corr:.3f}"
)
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "best_model_correlation_scatter.png"), dpi=150)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\n=== Final Results ===")
print(f"Best pred_hidden: {best_pred_hidden}")
print(
    f"importance_prediction_accuracy (Spearman correlation): {results_summary[best_pred_hidden]['best_val_corr']:.4f}"
)

print(f"\nAll results and visualizations saved to: {working_dir}")
print(f"- Tuning curves: pred_hidden_tuning_curves.png")
print(f"- Comparison bar chart: pred_hidden_comparison.png")
print(f"- Best model predictions: best_model_prediction_samples.png")
print(f"- Correlation scatter: best_model_correlation_scatter.png")
print(f"- Experiment data: experiment_data.npy")
