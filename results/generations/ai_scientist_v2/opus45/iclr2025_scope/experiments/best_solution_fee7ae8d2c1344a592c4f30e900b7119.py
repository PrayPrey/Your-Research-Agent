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

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)

# Experiment data tracking
experiment_data = {
    "synthetic_kv": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "spearman_correlations": [],
    }
}


# Synthetic data generation - simulates early layer representations and late layer attention patterns
class SyntheticKVDataset(Dataset):
    def __init__(self, num_samples=1000, seq_len=128, hidden_dim=64, num_layers=6):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.hidden_dim = hidden_dim

        self.early_layer_reps = []
        self.positions = []
        self.late_layer_importance = []

        for _ in range(num_samples):
            # Generate early layer representations
            early_rep = torch.randn(seq_len, hidden_dim)

            # Positional information (normalized)
            pos = torch.arange(seq_len).float() / seq_len

            # Generate importance scores based on learnable patterns
            # Pattern 1: First few tokens are important (like [CLS] or system tokens)
            importance = torch.zeros(seq_len)
            importance[:5] = 0.8 + 0.2 * torch.rand(5)

            # Pattern 2: Tokens with high L2 norm in early rep are important
            norms = early_rep.norm(dim=1)
            norm_importance = (norms - norms.min()) / (norms.max() - norms.min() + 1e-8)
            importance += 0.3 * norm_importance

            # Pattern 3: Periodic importance (simulates recurring patterns)
            periodic = 0.2 * torch.sin(pos * 4 * np.pi)
            importance += periodic

            # Pattern 4: Random "key" tokens (simulates entities in RAG)
            num_key_tokens = np.random.randint(3, 8)
            key_positions = np.random.choice(seq_len, num_key_tokens, replace=False)
            importance[key_positions] += 0.5

            # Normalize to [0, 1]
            importance = (importance - importance.min()) / (
                importance.max() - importance.min() + 1e-8
            )

            # Add some noise to simulate real attention patterns
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


# Lightweight Importance Prediction Module
class ImportancePredictor(nn.Module):
    def __init__(self, hidden_dim=64, pos_dim=16, pred_hidden=128):
        super().__init__()

        # Position encoding
        self.pos_encoder = nn.Sequential(
            nn.Linear(1, pos_dim), nn.ReLU(), nn.Linear(pos_dim, pos_dim)
        )

        # Main prediction network
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
        # early_rep: [batch, seq_len, hidden_dim]
        # position: [batch, seq_len]

        batch_size, seq_len, _ = early_rep.shape

        # Encode position
        pos_encoded = self.pos_encoder(
            position.unsqueeze(-1)
        )  # [batch, seq_len, pos_dim]

        # Concatenate features
        combined = torch.cat(
            [early_rep, pos_encoded], dim=-1
        )  # [batch, seq_len, hidden_dim + pos_dim]

        # Predict importance
        importance = self.predictor(combined).squeeze(-1)  # [batch, seq_len]

        return importance


# Training function
def train_epoch(model, dataloader, optimizer, criterion):
    model.train()
    total_loss = 0
    all_preds = []
    all_targets = []

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

    # Compute Spearman correlation
    correlations = []
    for i in range(len(all_preds)):
        corr, _ = spearmanr(all_preds[i], all_targets[i])
        if not np.isnan(corr):
            correlations.append(corr)

    avg_corr = np.mean(correlations) if correlations else 0
    return total_loss / len(dataloader), avg_corr


# Validation function
def validate(model, dataloader, criterion):
    model.eval()
    total_loss = 0
    all_preds = []
    all_targets = []

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

    # Compute Spearman correlation
    correlations = []
    for i in range(len(all_preds)):
        corr, _ = spearmanr(all_preds[i], all_targets[i])
        if not np.isnan(corr):
            correlations.append(corr)

    avg_corr = np.mean(correlations) if correlations else 0
    return total_loss / len(dataloader), avg_corr, all_preds, all_targets


# Create datasets
print("Creating synthetic datasets...")
train_dataset = SyntheticKVDataset(num_samples=2000, seq_len=128, hidden_dim=64)
val_dataset = SyntheticKVDataset(num_samples=500, seq_len=128, hidden_dim=64)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Initialize model
model = ImportancePredictor(hidden_dim=64, pos_dim=16, pred_hidden=128).to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.MSELoss()

# Training loop
num_epochs = 50
best_val_corr = -1
print("\nStarting training...")

for epoch in range(num_epochs):
    train_loss, train_corr = train_epoch(model, train_loader, optimizer, criterion)
    val_loss, val_corr, val_preds, val_targets = validate(model, val_loader, criterion)

    experiment_data["synthetic_kv"]["losses"]["train"].append(train_loss)
    experiment_data["synthetic_kv"]["losses"]["val"].append(val_loss)
    experiment_data["synthetic_kv"]["metrics"]["train"].append(train_corr)
    experiment_data["synthetic_kv"]["metrics"]["val"].append(val_corr)
    experiment_data["synthetic_kv"]["spearman_correlations"].append(val_corr)

    if val_corr > best_val_corr:
        best_val_corr = val_corr
        # Save best predictions
        experiment_data["synthetic_kv"]["predictions"] = val_preds
        experiment_data["synthetic_kv"]["ground_truth"] = val_targets
        torch.save(model.state_dict(), os.path.join(working_dir, "best_model.pt"))

    if (epoch + 1) % 10 == 0 or epoch == 0:
        print(
            f"Epoch {epoch+1}: train_loss = {train_loss:.4f}, validation_loss = {val_loss:.4f}, "
            f"train_spearman = {train_corr:.4f}, val_spearman = {val_corr:.4f}"
        )

print(f"\nBest validation Spearman correlation: {best_val_corr:.4f}")

# Final evaluation
model.load_state_dict(torch.load(os.path.join(working_dir, "best_model.pt")))
final_loss, final_corr, final_preds, final_targets = validate(
    model, val_loader, criterion
)

print(f"\n=== Final Results ===")
print(f"importance_prediction_accuracy (Spearman correlation): {final_corr:.4f}")
print(f"Final validation loss (MSE): {final_loss:.4f}")

# Visualization 1: Training curves
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(experiment_data["synthetic_kv"]["losses"]["train"], label="Train")
axes[0].plot(experiment_data["synthetic_kv"]["losses"]["val"], label="Validation")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss (MSE)")
axes[0].set_title("Training and Validation Loss")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(experiment_data["synthetic_kv"]["metrics"]["train"], label="Train")
axes[1].plot(experiment_data["synthetic_kv"]["metrics"]["val"], label="Validation")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Spearman Correlation")
axes[1].set_title("Importance Prediction Accuracy")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pko_training_curves.png"), dpi=150)
plt.close()

# Visualization 2: Predicted vs Actual importance for sample sequences
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
sample_indices = [0, 10, 20, 30]

for i, idx in enumerate(sample_indices):
    ax = axes[i // 2, i % 2]
    ax.plot(final_targets[idx], label="Actual Importance", alpha=0.7)
    ax.plot(final_preds[idx], label="Predicted Importance", alpha=0.7)
    sample_corr, _ = spearmanr(final_preds[idx], final_targets[idx])
    ax.set_xlabel("Token Position")
    ax.set_ylabel("Importance Score")
    ax.set_title(f"Sample {idx+1} (Spearman: {sample_corr:.3f})")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pko_prediction_samples.png"), dpi=150)
plt.close()

# Visualization 3: Correlation scatter plot
fig, ax = plt.subplots(figsize=(6, 6))
flat_preds = final_preds.flatten()
flat_targets = final_targets.flatten()
# Subsample for visualization
subsample_idx = np.random.choice(
    len(flat_preds), min(5000, len(flat_preds)), replace=False
)
ax.scatter(flat_targets[subsample_idx], flat_preds[subsample_idx], alpha=0.3, s=1)
ax.plot([0, 1], [0, 1], "r--", label="Perfect prediction")
ax.set_xlabel("Actual Importance")
ax.set_ylabel("Predicted Importance")
ax.set_title(f"Prediction vs Actual (Overall Spearman: {final_corr:.3f})")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pko_correlation_scatter.png"), dpi=150)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\nAll results and visualizations saved to: {working_dir}")
print(f"- Training curves: pko_training_curves.png")
print(f"- Prediction samples: pko_prediction_samples.png")
print(f"- Correlation scatter: pko_correlation_scatter.png")
print(f"- Experiment data: experiment_data.npy")
