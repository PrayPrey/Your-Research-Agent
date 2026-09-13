import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import pandas as pd

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds
np.random.seed(42)
torch.manual_seed(42)

# Initialize experiment data storage
experiment_data = {
    "supportive": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "appropriate_reliance": [],
        "predictions": [],
        "ground_truth": [],
    },
    "challenging": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "appropriate_reliance": [],
        "predictions": [],
        "ground_truth": [],
    },
    "adaptive": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "appropriate_reliance": [],
        "predictions": [],
        "ground_truth": [],
    },
}


# Generate synthetic decision-making task data
def generate_synthetic_data(n_samples=5000):
    """
    Generate synthetic data for decision tasks with:
    - Task features (complexity, domain characteristics)
    - Ground truth decisions
    - AI recommendations (with some error rate)
    - Cognitive load indicators (response latency, confidence)
    """
    # Task features: 10-dimensional feature space
    X = np.random.randn(n_samples, 10)

    # Task complexity (derived from feature magnitude)
    task_complexity = np.linalg.norm(X, axis=1)
    task_complexity = (task_complexity - task_complexity.min()) / (
        task_complexity.max() - task_complexity.min()
    )

    # Ground truth decisions (binary classification)
    # Decision boundary: weighted sum of features
    weights_true = np.random.randn(10)
    decision_scores = X @ weights_true
    y_true = (decision_scores > 0).astype(int)

    # AI recommendations (85% accuracy on average)
    ai_accuracy = 0.85
    y_ai = y_true.copy()
    error_mask = np.random.rand(n_samples) > ai_accuracy
    y_ai[error_mask] = 1 - y_ai[error_mask]

    # AI confidence (higher when correct)
    ai_confidence = np.random.beta(8, 2, n_samples)  # High confidence
    ai_confidence[error_mask] = np.random.beta(3, 3, n_samples)[
        error_mask
    ]  # Lower when wrong

    # Human baseline cognitive load (increases with task complexity)
    base_cognitive_load = task_complexity + np.random.normal(0, 0.1, n_samples)
    base_cognitive_load = np.clip(base_cognitive_load, 0, 1)

    # Response latency (correlated with cognitive load)
    response_latency = base_cognitive_load * 5 + np.random.normal(0, 0.5, n_samples)
    response_latency = np.clip(response_latency, 0.5, 10)

    # Human confidence (inversely related to cognitive load)
    human_confidence = 1 - base_cognitive_load + np.random.normal(0, 0.1, n_samples)
    human_confidence = np.clip(human_confidence, 0.1, 1.0)

    return {
        "X": X.astype(np.float32),
        "y_true": y_true,
        "y_ai": y_ai,
        "ai_confidence": ai_confidence.astype(np.float32),
        "task_complexity": task_complexity.astype(np.float32),
        "cognitive_load": base_cognitive_load.astype(np.float32),
        "response_latency": response_latency.astype(np.float32),
        "human_confidence": human_confidence.astype(np.float32),
    }


print("Generating synthetic data...")
data = generate_synthetic_data(n_samples=5000)

# Split data
train_idx, val_idx = train_test_split(
    np.arange(len(data["X"])), test_size=0.2, random_state=42
)


# Dataset class
class DecisionDataset(Dataset):
    def __init__(self, data, indices):
        self.X = data["X"][indices]
        self.y_true = data["y_true"][indices]
        self.y_ai = data["y_ai"][indices]
        self.ai_confidence = data["ai_confidence"][indices]
        self.task_complexity = data["task_complexity"][indices]
        self.cognitive_load = data["cognitive_load"][indices]
        self.response_latency = data["response_latency"][indices]
        self.human_confidence = data["human_confidence"][indices]

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return {
            "X": torch.FloatTensor(self.X[idx]),
            "y_true": torch.LongTensor([self.y_true[idx]])[0],
            "y_ai": torch.LongTensor([self.y_ai[idx]])[0],
            "ai_confidence": torch.FloatTensor([self.ai_confidence[idx]]),
            "task_complexity": torch.FloatTensor([self.task_complexity[idx]]),
            "cognitive_load": torch.FloatTensor([self.cognitive_load[idx]]),
            "response_latency": torch.FloatTensor([self.response_latency[idx]]),
            "human_confidence": torch.FloatTensor([self.human_confidence[idx]]),
        }


train_dataset = DecisionDataset(data, train_idx)
val_dataset = DecisionDataset(data, val_idx)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)


# Model: Human decision-making simulator under different AI conditions
class HumanDecisionModel(nn.Module):
    def __init__(self, input_dim=10, hidden_dim=64):
        super(HumanDecisionModel, self).__init__()
        # Process task features
        self.task_encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )

        # Process AI recommendation and interaction style
        # Input: AI recommendation, AI confidence, interaction_style (supportive/challenging indicator)
        self.ai_encoder = nn.Sequential(
            nn.Linear(3, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )

        # Process cognitive state
        self.cognitive_encoder = nn.Sequential(
            nn.Linear(
                3, hidden_dim
            ),  # cognitive_load, response_latency, human_confidence
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )

        # Final decision
        self.decision_head = nn.Sequential(
            nn.Linear(hidden_dim * 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 2),  # Binary decision
        )

    def forward(
        self,
        X,
        y_ai,
        ai_confidence,
        cognitive_load,
        response_latency,
        human_confidence,
        interaction_style,
    ):
        # Encode task
        task_repr = self.task_encoder(X)

        # Encode AI recommendation with interaction style
        ai_input = torch.stack(
            [y_ai.float(), ai_confidence.squeeze(-1), interaction_style], dim=1
        )
        ai_repr = self.ai_encoder(ai_input)

        # Encode cognitive state
        cognitive_input = torch.stack(
            [
                cognitive_load.squeeze(-1),
                response_latency.squeeze(-1),
                human_confidence.squeeze(-1),
            ],
            dim=1,
        )
        cognitive_repr = self.cognitive_encoder(cognitive_input)

        # Combine and predict
        combined = torch.cat([task_repr, ai_repr, cognitive_repr], dim=1)
        logits = self.decision_head(combined)
        return logits


# Training function
def train_epoch(model, loader, optimizer, criterion, condition_type, device):
    model.train()
    total_loss = 0
    correct = 0
    total = 0

    for batch in loader:
        # Move batch to device
        X = batch["X"].to(device)
        y_true = batch["y_true"].to(device)
        y_ai = batch["y_ai"].to(device)
        ai_confidence = batch["ai_confidence"].to(device)
        cognitive_load = batch["cognitive_load"].to(device)
        response_latency = batch["response_latency"].to(device)
        human_confidence = batch["human_confidence"].to(device)

        # Determine interaction style based on condition
        batch_size = X.size(0)
        if condition_type == "supportive":
            # Always supportive (value: 1.0)
            interaction_style = torch.ones(batch_size, device=device)
        elif condition_type == "challenging":
            # Always challenging (value: -1.0)
            interaction_style = -torch.ones(batch_size, device=device)
        else:  # adaptive
            # Adaptive: supportive when high cognitive load, challenging when low
            interaction_style = torch.where(
                cognitive_load.squeeze(-1) > 0.5,
                torch.ones(batch_size, device=device),  # Supportive when high load
                -torch.ones(batch_size, device=device),  # Challenging when low load
            )

        optimizer.zero_grad()
        logits = model(
            X,
            y_ai,
            ai_confidence,
            cognitive_load,
            response_latency,
            human_confidence,
            interaction_style,
        )
        loss = criterion(logits, y_true)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        pred = logits.argmax(dim=1)
        correct += (pred == y_true).sum().item()
        total += y_true.size(0)

    return total_loss / len(loader), correct / total


# Evaluation function
def evaluate(model, loader, criterion, condition_type, device):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0

    all_y_true = []
    all_y_ai = []
    all_y_pred = []
    all_cognitive_load = []

    with torch.no_grad():
        for batch in loader:
            X = batch["X"].to(device)
            y_true = batch["y_true"].to(device)
            y_ai = batch["y_ai"].to(device)
            ai_confidence = batch["ai_confidence"].to(device)
            cognitive_load = batch["cognitive_load"].to(device)
            response_latency = batch["response_latency"].to(device)
            human_confidence = batch["human_confidence"].to(device)

            batch_size = X.size(0)
            if condition_type == "supportive":
                interaction_style = torch.ones(batch_size, device=device)
            elif condition_type == "challenging":
                interaction_style = -torch.ones(batch_size, device=device)
            else:  # adaptive
                interaction_style = torch.where(
                    cognitive_load.squeeze(-1) > 0.5,
                    torch.ones(batch_size, device=device),
                    -torch.ones(batch_size, device=device),
                )

            logits = model(
                X,
                y_ai,
                ai_confidence,
                cognitive_load,
                response_latency,
                human_confidence,
                interaction_style,
            )
            loss = criterion(logits, y_true)

            total_loss += loss.item()
            pred = logits.argmax(dim=1)
            correct += (pred == y_true).sum().item()
            total += y_true.size(0)

            all_y_true.extend(y_true.cpu().numpy())
            all_y_ai.extend(y_ai.cpu().numpy())
            all_y_pred.extend(pred.cpu().numpy())
            all_cognitive_load.extend(cognitive_load.cpu().numpy())

    accuracy = correct / total

    # Calculate Appropriate Reliance Score
    all_y_true = np.array(all_y_true)
    all_y_ai = np.array(all_y_ai)
    all_y_pred = np.array(all_y_pred)

    # When AI is correct
    ai_correct_mask = all_y_ai == all_y_true
    agreement_when_ai_correct = (
        np.mean(all_y_pred[ai_correct_mask] == all_y_ai[ai_correct_mask])
        if ai_correct_mask.sum() > 0
        else 0
    )

    # When AI is incorrect
    ai_incorrect_mask = all_y_ai != all_y_true
    disagreement_when_ai_incorrect = (
        np.mean(all_y_pred[ai_incorrect_mask] != all_y_ai[ai_incorrect_mask])
        if ai_incorrect_mask.sum() > 0
        else 0
    )

    # Appropriate Reliance Score
    appropriate_reliance = (
        agreement_when_ai_correct + disagreement_when_ai_incorrect
    ) / 2

    return (
        total_loss / len(loader),
        accuracy,
        appropriate_reliance,
        all_y_pred,
        all_y_true,
    )


# Train models for each condition
conditions = ["supportive", "challenging", "adaptive"]
models = {}
n_epochs = 50

print("\n" + "=" * 60)
print("Training models for each condition...")
print("=" * 60)

for condition in conditions:
    print(f"\n{'='*60}")
    print(f"Training: {condition.upper()} condition")
    print(f"{'='*60}")

    model = HumanDecisionModel(input_dim=10, hidden_dim=64).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    best_val_loss = float("inf")

    for epoch in range(n_epochs):
        train_loss, train_acc = train_epoch(
            model, train_loader, optimizer, criterion, condition, device
        )
        val_loss, val_acc, val_appropriate_reliance, val_pred, val_true = evaluate(
            model, val_loader, criterion, condition, device
        )

        # Store metrics
        experiment_data[condition]["losses"]["train"].append(train_loss)
        experiment_data[condition]["losses"]["val"].append(val_loss)
        experiment_data[condition]["metrics"]["train"].append(train_acc)
        experiment_data[condition]["metrics"]["val"].append(val_acc)
        experiment_data[condition]["appropriate_reliance"].append(
            val_appropriate_reliance
        )

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch+1:3d}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, "
                f"train_acc={train_acc:.4f}, val_acc={val_acc:.4f}, "
                f"appropriate_reliance={val_appropriate_reliance:.4f}"
            )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            models[condition] = model

    # Store final predictions and ground truth
    _, _, _, final_pred, final_true = evaluate(
        model, val_loader, criterion, condition, device
    )
    experiment_data[condition]["predictions"] = final_pred
    experiment_data[condition]["ground_truth"] = final_true

# Final evaluation and comparison
print("\n" + "=" * 60)
print("FINAL EVALUATION RESULTS")
print("=" * 60)

final_results = {}
for condition in conditions:
    model = models[condition]
    val_loss, val_acc, val_appropriate_reliance, _, _ = evaluate(
        model, val_loader, criterion, condition, device
    )
    final_results[condition] = {
        "accuracy": val_acc,
        "appropriate_reliance": val_appropriate_reliance,
    }
    print(f"\n{condition.upper()}:")
    print(f"  Validation Accuracy: {val_acc:.4f}")
    print(f"  Appropriate Reliance Score: {val_appropriate_reliance:.4f}")

# Visualization
print("\n" + "=" * 60)
print("Generating visualizations...")
print("=" * 60)

# Plot 1: Training curves
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Loss curves
for condition in conditions:
    axes[0, 0].plot(
        experiment_data[condition]["losses"]["train"],
        label=f"{condition} (train)",
        alpha=0.7,
    )
    axes[0, 1].plot(
        experiment_data[condition]["losses"]["val"],
        label=f"{condition} (val)",
        alpha=0.7,
    )

axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("Training Loss")
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Loss")
axes[0, 1].set_title("Validation Loss")
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

# Accuracy curves
for condition in conditions:
    axes[1, 0].plot(
        experiment_data[condition]["metrics"]["train"],
        label=f"{condition} (train)",
        alpha=0.7,
    )
    axes[1, 1].plot(
        experiment_data[condition]["metrics"]["val"],
        label=f"{condition} (val)",
        alpha=0.7,
    )

axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Accuracy")
axes[1, 0].set_title("Training Accuracy")
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].set_xlabel("Epoch")
axes[1, 1].set_ylabel("Accuracy")
axes[1, 1].set_title("Validation Accuracy")
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "training_curves.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# Plot 2: Appropriate Reliance Score comparison
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

for condition in conditions:
    ax.plot(
        experiment_data[condition]["appropriate_reliance"],
        label=condition,
        linewidth=2,
        alpha=0.8,
    )

ax.set_xlabel("Epoch", fontsize=12)
ax.set_ylabel("Appropriate Reliance Score", fontsize=12)
ax.set_title("Appropriate Reliance Score Over Training", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Random baseline")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "appropriate_reliance_comparison.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Plot 3: Final comparison bar chart
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

conditions_list = list(final_results.keys())
accuracies = [final_results[c]["accuracy"] for c in conditions_list]
reliances = [final_results[c]["appropriate_reliance"] for c in conditions_list]

x_pos = np.arange(len(conditions_list))

axes[0].bar(x_pos, accuracies, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
axes[0].set_xticks(x_pos)
axes[0].set_xticklabels([c.capitalize() for c in conditions_list])
axes[0].set_ylabel("Accuracy", fontsize=12)
axes[0].set_title(
    "Final Decision Accuracy by Condition", fontsize=13, fontweight="bold"
)
axes[0].set_ylim([0, 1])
axes[0].grid(True, alpha=0.3, axis="y")

axes[1].bar(x_pos, reliances, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels([c.capitalize() for c in conditions_list])
axes[1].set_ylabel("Appropriate Reliance Score", fontsize=12)
axes[1].set_title(
    "Final Appropriate Reliance by Condition", fontsize=13, fontweight="bold"
)
axes[1].set_ylim([0, 1])
axes[1].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "final_comparison.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

# Summary statistics
print("\n" + "=" * 60)
print("SUMMARY STATISTICS")
print("=" * 60)

for condition in conditions:
    print(f"\n{condition.upper()} Condition:")
    print(
        f"  Final Training Accuracy: {experiment_data[condition]['metrics']['train'][-1]:.4f}"
    )
    print(
        f"  Final Validation Accuracy: {experiment_data[condition]['metrics']['val'][-1]:.4f}"
    )
    print(
        f"  Final Appropriate Reliance: {experiment_data[condition]['appropriate_reliance'][-1]:.4f}"
    )
    print(
        f"  Best Appropriate Reliance: {max(experiment_data[condition]['appropriate_reliance']):.4f}"
    )

# Find best performing condition
best_condition = max(
    final_results, key=lambda x: final_results[x]["appropriate_reliance"]
)
print(f"\n{'='*60}")
print(f"BEST PERFORMING CONDITION: {best_condition.upper()}")
print(
    f"  Appropriate Reliance Score: {final_results[best_condition]['appropriate_reliance']:.4f}"
)
print(f"  Accuracy: {final_results[best_condition]['accuracy']:.4f}")
print(f"{'='*60}")

print("\nExperiment complete! All plots saved to working directory.")
