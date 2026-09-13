import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import pandas as pd

# Setup working directory
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds
np.random.seed(42)
torch.manual_seed(42)

# Initialize experiment data storage
experiment_data = {"dropout_rate_tuning": {}}


# Generate synthetic data simulating human-LLM collaboration
def generate_synthetic_collaboration_data(n_samples=2000):
    """
    Generate synthetic data for human-LLM collaboration study.
    Features: uncertainty_communication_type, llm_accuracy, task_difficulty, user_expertise
    Labels: user_decision (0=reject, 1=accept), llm_correct (0=wrong, 1=correct)
    """
    # Communication types: 0=textual, 1=numerical, 2=visual
    comm_types = np.random.randint(0, 3, n_samples)

    # LLM uncertainty scores (0-1, where higher = more certain)
    llm_certainty = np.random.beta(2, 2, n_samples)

    # LLM correctness based on certainty (higher certainty -> more likely correct)
    llm_correct = (np.random.random(n_samples) < (0.5 + 0.4 * llm_certainty)).astype(
        int
    )

    # Task difficulty (0-1)
    task_difficulty = np.random.beta(2, 2, n_samples)

    # User expertise (0-1)
    user_expertise = np.random.beta(2, 2, n_samples)

    # Simulate user decisions based on communication type and other factors
    user_decisions = np.zeros(n_samples, dtype=int)

    for i in range(n_samples):
        # Base probability of accepting LLM suggestion
        accept_prob = llm_certainty[i]

        # Adjust based on communication type effectiveness
        if comm_types[i] == 0:  # Textual - moderate effectiveness
            accept_prob *= 0.8
        elif comm_types[i] == 1:  # Numerical - less effective, can be over-trusted
            accept_prob = 0.7 + 0.3 * llm_certainty[i]
        elif comm_types[i] == 2:  # Visual - more effective calibration
            if llm_correct[i] == 1:
                accept_prob *= 1.1
            else:
                accept_prob *= 0.6

        # Adjust for user expertise
        accept_prob += 0.1 * user_expertise[i] * (1 if llm_correct[i] else -1)

        # Adjust for task difficulty
        accept_prob -= 0.1 * task_difficulty[i]

        accept_prob = np.clip(accept_prob, 0.1, 0.9)
        user_decisions[i] = 1 if np.random.random() < accept_prob else 0

    # Create feature matrix
    features = np.column_stack(
        [comm_types, llm_certainty, task_difficulty, user_expertise, llm_correct]
    )

    return features, user_decisions, llm_correct


# Generate data
print("Generating synthetic collaboration data...")
features, user_decisions, llm_correct = generate_synthetic_collaboration_data(2000)

# Split data
X_train, X_val, y_train, y_val, llm_correct_train, llm_correct_val = train_test_split(
    features, user_decisions, llm_correct, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train)}, Validation samples: {len(X_val)}")


# Custom Dataset
class CollaborationDataset(Dataset):
    def __init__(self, features, user_decisions, llm_correct):
        self.features = torch.FloatTensor(features)
        self.user_decisions = torch.LongTensor(user_decisions)
        self.llm_correct = torch.LongTensor(llm_correct)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return self.features[idx], self.user_decisions[idx], self.llm_correct[idx]


# Create datasets and dataloaders
train_dataset = CollaborationDataset(X_train, y_train, llm_correct_train)
val_dataset = CollaborationDataset(X_val, y_val, llm_correct_val)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)


# Neural network to predict user decisions
class DecisionPredictor(nn.Module):
    def __init__(self, input_dim=5, hidden_dim=64, dropout_rate=0.3):
        super(DecisionPredictor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, 2),  # Binary classification: accept or reject
        )

    def forward(self, x):
        return self.network(x)


# Calculate appropriate reliance rate
def calculate_appropriate_reliance(user_decisions, llm_correct):
    """
    Calculate appropriate reliance rate:
    - Correct acceptance: user accepts when LLM is correct
    - Correct rejection: user rejects when LLM is incorrect
    """
    user_decisions = (
        user_decisions.cpu().numpy()
        if torch.is_tensor(user_decisions)
        else user_decisions
    )
    llm_correct = (
        llm_correct.cpu().numpy() if torch.is_tensor(llm_correct) else llm_correct
    )

    correct_acceptances = np.sum((user_decisions == 1) & (llm_correct == 1))
    correct_rejections = np.sum((user_decisions == 0) & (llm_correct == 0))
    total = len(user_decisions)

    return (correct_acceptances + correct_rejections) / total


# Training function
def train_model(dropout_rate, num_epochs=50):
    """Train model with specific dropout rate"""
    print(f"\n{'='*60}")
    print(f"Training with dropout_rate = {dropout_rate}")
    print(f"{'='*60}")

    # Set seeds for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)

    # Initialize model
    model = DecisionPredictor(dropout_rate=dropout_rate).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Storage for this dropout rate
    results = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "appropriate_reliance_rates": {"train": [], "val": []},
        "epochs": [],
    }

    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_predictions = []
        train_true_decisions = []
        train_llm_correct_list = []

        for features_batch, decisions_batch, llm_correct_batch in train_loader:
            features_batch = features_batch.to(device)
            decisions_batch = decisions_batch.to(device)
            llm_correct_batch = llm_correct_batch.to(device)

            optimizer.zero_grad()
            outputs = model(features_batch)
            loss = criterion(outputs, decisions_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()

            _, predicted = torch.max(outputs, 1)
            train_predictions.extend(predicted.cpu().numpy())
            train_true_decisions.extend(decisions_batch.cpu().numpy())
            train_llm_correct_list.extend(llm_correct_batch.cpu().numpy())

        train_loss /= len(train_loader)
        train_arr = calculate_appropriate_reliance(
            np.array(train_true_decisions), np.array(train_llm_correct_list)
        )

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_predictions = []
        val_true_decisions = []
        val_llm_correct_list = []

        with torch.no_grad():
            for features_batch, decisions_batch, llm_correct_batch in val_loader:
                features_batch = features_batch.to(device)
                decisions_batch = decisions_batch.to(device)
                llm_correct_batch = llm_correct_batch.to(device)

                outputs = model(features_batch)
                loss = criterion(outputs, decisions_batch)

                val_loss += loss.item()

                _, predicted = torch.max(outputs, 1)
                val_predictions.extend(predicted.cpu().numpy())
                val_true_decisions.extend(decisions_batch.cpu().numpy())
                val_llm_correct_list.extend(llm_correct_batch.cpu().numpy())

        val_loss /= len(val_loader)
        val_arr = calculate_appropriate_reliance(
            np.array(val_true_decisions), np.array(val_llm_correct_list)
        )

        # Store metrics
        results["losses"]["train"].append(train_loss)
        results["losses"]["val"].append(val_loss)
        results["appropriate_reliance_rates"]["train"].append(train_arr)
        results["appropriate_reliance_rates"]["val"].append(val_arr)
        results["epochs"].append(epoch)

        if epoch % 10 == 0 or epoch == num_epochs - 1:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, "
                f"train_ARR={train_arr:.4f}, val_ARR={val_arr:.4f}"
            )

    # Store final predictions
    results["predictions"] = val_predictions
    results["ground_truth"] = val_true_decisions

    return results


# Hyperparameter tuning: Test different dropout rates
dropout_rates = [0.1, 0.2, 0.3, 0.4, 0.5]
print(f"\n{'='*60}")
print("Starting Dropout Rate Hyperparameter Tuning")
print(f"Testing dropout rates: {dropout_rates}")
print(f"{'='*60}")

for dropout_rate in dropout_rates:
    results = train_model(dropout_rate, num_epochs=50)
    experiment_data["dropout_rate_tuning"][f"dropout_{dropout_rate}"] = results

# Analysis and comparison
print("\n" + "=" * 60)
print("HYPERPARAMETER TUNING RESULTS")
print("=" * 60)

best_dropout = None
best_val_arr = 0.0
summary_results = []

for dropout_rate in dropout_rates:
    key = f"dropout_{dropout_rate}"
    results = experiment_data["dropout_rate_tuning"][key]

    final_val_arr = results["appropriate_reliance_rates"]["val"][-1]
    best_val_arr_epoch = max(results["appropriate_reliance_rates"]["val"])
    final_val_loss = results["losses"]["val"][-1]
    best_val_loss = min(results["losses"]["val"])

    summary_results.append(
        {
            "dropout_rate": dropout_rate,
            "final_val_arr": final_val_arr,
            "best_val_arr": best_val_arr_epoch,
            "final_val_loss": final_val_loss,
            "best_val_loss": best_val_loss,
        }
    )

    print(f"\nDropout Rate: {dropout_rate}")
    print(f"  Final Val ARR: {final_val_arr:.4f}")
    print(f"  Best Val ARR: {best_val_arr_epoch:.4f}")
    print(f"  Final Val Loss: {final_val_loss:.4f}")
    print(f"  Best Val Loss: {best_val_loss:.4f}")

    if final_val_arr > best_val_arr:
        best_val_arr = final_val_arr
        best_dropout = dropout_rate

print(f"\n{'='*60}")
print(f"BEST DROPOUT RATE: {best_dropout} (Final Val ARR: {best_val_arr:.4f})")
print(f"{'='*60}")

# Create comprehensive visualizations
fig = plt.figure(figsize=(16, 12))

# Plot 1: Validation ARR comparison across dropout rates
ax1 = plt.subplot(3, 3, 1)
for dropout_rate in dropout_rates:
    key = f"dropout_{dropout_rate}"
    results = experiment_data["dropout_rate_tuning"][key]
    ax1.plot(
        results["epochs"],
        results["appropriate_reliance_rates"]["val"],
        label=f"dropout={dropout_rate}",
        linewidth=2,
    )
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Validation ARR")
ax1.set_title("Validation ARR vs Dropout Rate")
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Validation Loss comparison
ax2 = plt.subplot(3, 3, 2)
for dropout_rate in dropout_rates:
    key = f"dropout_{dropout_rate}"
    results = experiment_data["dropout_rate_tuning"][key]
    ax2.plot(
        results["epochs"],
        results["losses"]["val"],
        label=f"dropout={dropout_rate}",
        linewidth=2,
    )
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Validation Loss")
ax2.set_title("Validation Loss vs Dropout Rate")
ax2.legend()
ax2.grid(True, alpha=0.3)

# Plot 3: Final validation ARR bar chart
ax3 = plt.subplot(3, 3, 3)
final_val_arrs = [s["final_val_arr"] for s in summary_results]
colors = ["green" if dr == best_dropout else "skyblue" for dr in dropout_rates]
bars = ax3.bar([str(dr) for dr in dropout_rates], final_val_arrs, color=colors)
ax3.set_xlabel("Dropout Rate")
ax3.set_ylabel("Final Validation ARR")
ax3.set_title("Final Validation ARR by Dropout Rate")
ax3.grid(True, axis="y", alpha=0.3)
for bar, val in zip(bars, final_val_arrs):
    height = bar.get_height()
    ax3.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# Plot 4: Training ARR for best dropout
ax4 = plt.subplot(3, 3, 4)
best_key = f"dropout_{best_dropout}"
best_results = experiment_data["dropout_rate_tuning"][best_key]
ax4.plot(
    best_results["epochs"],
    best_results["appropriate_reliance_rates"]["train"],
    label="Train ARR",
    linewidth=2,
)
ax4.plot(
    best_results["epochs"],
    best_results["appropriate_reliance_rates"]["val"],
    label="Val ARR",
    linewidth=2,
)
ax4.set_xlabel("Epoch")
ax4.set_ylabel("ARR")
ax4.set_title(f"Best Model (dropout={best_dropout}): Train vs Val ARR")
ax4.legend()
ax4.grid(True, alpha=0.3)

# Plot 5: Training Loss for best dropout
ax5 = plt.subplot(3, 3, 5)
ax5.plot(
    best_results["epochs"],
    best_results["losses"]["train"],
    label="Train Loss",
    linewidth=2,
)
ax5.plot(
    best_results["epochs"], best_results["losses"]["val"], label="Val Loss", linewidth=2
)
ax5.set_xlabel("Epoch")
ax5.set_ylabel("Loss")
ax5.set_title(f"Best Model (dropout={best_dropout}): Train vs Val Loss")
ax5.legend()
ax5.grid(True, alpha=0.3)

# Plot 6: Best validation ARR bar chart
ax6 = plt.subplot(3, 3, 6)
best_val_arrs = [s["best_val_arr"] for s in summary_results]
bars = ax6.bar([str(dr) for dr in dropout_rates], best_val_arrs, color=colors)
ax6.set_xlabel("Dropout Rate")
ax6.set_ylabel("Best Validation ARR")
ax6.set_title("Best Validation ARR by Dropout Rate")
ax6.grid(True, axis="y", alpha=0.3)
for bar, val in zip(bars, best_val_arrs):
    height = bar.get_height()
    ax6.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# Plot 7: Overfitting analysis (Train-Val gap)
ax7 = plt.subplot(3, 3, 7)
for dropout_rate in dropout_rates:
    key = f"dropout_{dropout_rate}"
    results = experiment_data["dropout_rate_tuning"][key]
    train_arr = np.array(results["appropriate_reliance_rates"]["train"])
    val_arr = np.array(results["appropriate_reliance_rates"]["val"])
    gap = train_arr - val_arr
    ax7.plot(results["epochs"], gap, label=f"dropout={dropout_rate}", linewidth=2)
ax7.set_xlabel("Epoch")
ax7.set_ylabel("ARR Gap (Train - Val)")
ax7.set_title("Overfitting Analysis: Train-Val ARR Gap")
ax7.legend()
ax7.grid(True, alpha=0.3)
ax7.axhline(y=0, color="k", linestyle="--", alpha=0.3)

# Plot 8: Final validation loss bar chart
ax8 = plt.subplot(3, 3, 8)
final_val_losses = [s["final_val_loss"] for s in summary_results]
bars = ax8.bar([str(dr) for dr in dropout_rates], final_val_losses, color=colors)
ax8.set_xlabel("Dropout Rate")
ax8.set_ylabel("Final Validation Loss")
ax8.set_title("Final Validation Loss by Dropout Rate")
ax8.grid(True, axis="y", alpha=0.3)
for bar, val in zip(bars, final_val_losses):
    height = bar.get_height()
    ax8.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# Plot 9: ARR by Communication Type for best model
ax9 = plt.subplot(3, 3, 9)
comm_type_names = ["Textual", "Numerical", "Visual"]
arr_by_type = []
for comm_type in range(3):
    mask = X_val[:, 0] == comm_type
    if np.sum(mask) > 0:
        arr = calculate_appropriate_reliance(y_val[mask], llm_correct_val[mask])
        arr_by_type.append(arr)
    else:
        arr_by_type.append(0)

ax9.bar(comm_type_names, arr_by_type, color=["blue", "orange", "green"])
ax9.set_xlabel("Communication Type")
ax9.set_ylabel("ARR")
ax9.set_title(f"Best Model: ARR by Communication Type")
ax9.set_ylim([0, 1])
ax9.grid(True, axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dropout_tuning_results.png"), dpi=300)
print(
    f"\nVisualization saved to {os.path.join(working_dir, 'dropout_tuning_results.png')}"
)

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

# Save summary table
summary_df = pd.DataFrame(summary_results)
summary_df.to_csv(os.path.join(working_dir, "dropout_tuning_summary.csv"), index=False)
print(
    f"Summary table saved to {os.path.join(working_dir, 'dropout_tuning_summary.csv')}"
)

print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(f"Best Dropout Rate: {best_dropout}")
print(f"Best Final Validation ARR: {best_val_arr:.4f}")
print(
    f"Improvement over baseline (0.3): {(best_val_arr - summary_results[2]['final_val_arr']):.4f}"
)
print("=" * 60)
