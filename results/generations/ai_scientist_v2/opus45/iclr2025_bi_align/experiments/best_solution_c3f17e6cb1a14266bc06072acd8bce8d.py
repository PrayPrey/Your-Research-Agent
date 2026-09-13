import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
from collections import defaultdict

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Constants
NUM_CONTEXTS = 4
NUM_STRATEGIES = 4
CONTEXT_NAMES = [
    "factual_error",
    "reasoning_flaw",
    "value_conflict",
    "preference_mismatch",
]
STRATEGY_NAMES = ["direct_correction", "socratic", "evidence", "gentle_suggestion"]


def generate_synthetic_data(n_samples=1000):
    """Generate synthetic user-AI interaction data"""
    data = []
    for _ in range(n_samples):
        context_type = np.random.randint(0, NUM_CONTEXTS)
        user_confidence = np.random.uniform(0.3, 1.0)
        user_correct = np.random.random() < 0.4
        context_onehot = np.zeros(NUM_CONTEXTS)
        context_onehot[context_type] = 1
        features = np.concatenate([context_onehot, [user_confidence]])
        data.append(
            {
                "features": features,
                "context_type": context_type,
                "user_confidence": user_confidence,
                "user_correct": user_correct,
            }
        )
    return data


def simulate_user_receptivity(
    context_type, strategy, user_confidence, base_receptivity=0.5
):
    """Simulate how receptive a user is to a given disagreement strategy"""
    effectiveness = np.array(
        [
            [0.9, 0.5, 0.8, 0.4],
            [0.4, 0.9, 0.7, 0.5],
            [0.2, 0.5, 0.6, 0.9],
            [0.3, 0.6, 0.5, 0.8],
        ]
    )
    strategy_match = effectiveness[context_type, strategy]
    confidence_penalty = (user_confidence - 0.5) * 0.3
    receptivity = base_receptivity + strategy_match * 0.4 - confidence_penalty
    receptivity = np.clip(receptivity, 0.1, 0.95)
    accepts = np.random.random() < receptivity
    return accepts, receptivity


class InteractionDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            "features": torch.FloatTensor(item["features"]),
            "context_type": item["context_type"],
            "user_confidence": item["user_confidence"],
            "user_correct": item["user_correct"],
        }


class CCDModel(nn.Module):
    def __init__(
        self, input_dim=NUM_CONTEXTS + 1, hidden_dim=32, num_strategies=NUM_STRATEGIES
    ):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_strategies),
        )

    def forward(self, x):
        return self.network(x)

    def select_strategy(self, x, temperature=1.0):
        logits = self.forward(x)
        probs = torch.softmax(logits / temperature, dim=-1)
        strategy = torch.multinomial(probs, 1).squeeze(-1)
        return strategy, probs


def train_ccd_model(model, train_loader, val_loader, epochs=50, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)
    train_losses = []
    val_acceptance_rates = []

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0

        for batch in train_loader:
            features = batch["features"].to(device)
            context_types = batch["context_type"].numpy()
            user_confidences = batch["user_confidence"].numpy()
            user_corrects = batch["user_correct"].numpy()

            optimizer.zero_grad()
            strategies, probs = model.select_strategy(features)
            strategies_np = strategies.cpu().numpy()

            rewards = []
            for i in range(len(strategies_np)):
                if user_corrects[i]:
                    reward = 0.5 if strategies_np[i] != 0 else 0.0
                else:
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], strategies_np[i], user_confidences[i]
                    )
                    reward = 1.0 if accepts else -0.1
                rewards.append(reward)

            rewards = torch.FloatTensor(rewards).to(device)
            log_probs = torch.log(
                probs.gather(1, strategies.unsqueeze(1)).squeeze(1) + 1e-8
            )
            loss = -torch.mean(log_probs * rewards)

            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        val_acceptance = evaluate_model(model, val_loader, "ccd")
        val_acceptance_rates.append(val_acceptance)
        train_losses.append(epoch_loss / len(train_loader))

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch+1}: train_loss = {train_losses[-1]:.4f}, val_acceptance_rate = {val_acceptance:.4f}"
            )

    return train_losses, val_acceptance_rates


def evaluate_model(model, data_loader, mode="ccd"):
    """Evaluate a model on the given data"""
    total_disagreements = 0
    accepted_disagreements = 0

    if mode == "ccd":
        model.eval()

    with torch.no_grad():
        for batch in data_loader:
            features = (
                batch["features"].to(device) if mode == "ccd" else batch["features"]
            )
            context_types = batch["context_type"].numpy()
            user_confidences = batch["user_confidence"].numpy()
            user_corrects = batch["user_correct"].numpy()

            for i in range(len(context_types)):
                if user_corrects[i]:
                    continue
                total_disagreements += 1

                if mode == "sycophantic":
                    accepted_disagreements += 0
                elif mode == "blunt":
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], 0, user_confidences[i]
                    )
                    if accepts:
                        accepted_disagreements += 1
                elif mode == "ccd":
                    strategy, _ = model.select_strategy(features[i : i + 1])
                    strategy = strategy.item()
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], strategy, user_confidences[i]
                    )
                    if accepts:
                        accepted_disagreements += 1
                elif mode == "random":
                    strategy = np.random.randint(0, NUM_STRATEGIES)
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], strategy, user_confidences[i]
                    )
                    if accepts:
                        accepted_disagreements += 1

    return accepted_disagreements / max(total_disagreements, 1)


# Main experiment
print("Generating synthetic data...")
all_data = generate_synthetic_data(n_samples=2000)
train_data = all_data[:1600]
val_data = all_data[1600:]

train_dataset = InteractionDataset(train_data)
val_dataset = InteractionDataset(val_data)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

# Initialize experiment data tracking for hyperparameter tuning
experiment_data = {
    "epochs_tuning": {
        "epochs_50": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "epochs_100": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
    },
    "baselines": {},
    "final_results": {},
}

# Hyperparameter tuning: epochs
epoch_values = [50, 100]
epoch_results = {}

for n_epochs in epoch_values:
    print("\n" + "=" * 50)
    print(f"Training CCD Model with {n_epochs} epochs...")
    print("=" * 50)

    # Reset seed for fair comparison
    torch.manual_seed(42)
    np.random.seed(42)

    ccd_model = CCDModel().to(device)
    train_losses, val_acceptance_rates = train_ccd_model(
        ccd_model, train_loader, val_loader, epochs=n_epochs
    )

    # Store results
    key = f"epochs_{n_epochs}"
    experiment_data["epochs_tuning"][key]["losses"]["train"] = train_losses
    experiment_data["epochs_tuning"][key]["metrics"]["val"] = val_acceptance_rates

    # Evaluate final performance
    n_eval_runs = 10
    results = []
    for _ in range(n_eval_runs):
        results.append(evaluate_model(ccd_model, val_loader, "ccd"))

    epoch_results[n_epochs] = {
        "model": ccd_model,
        "train_losses": train_losses,
        "val_acceptance_rates": val_acceptance_rates,
        "final_mean": np.mean(results),
        "final_std": np.std(results),
        "eval_runs": results,
    }

    print(
        f"\nEpochs={n_epochs}: Final acceptance rate = {epoch_results[n_epochs]['final_mean']:.4f} ± {epoch_results[n_epochs]['final_std']:.4f}"
    )

# Evaluate baselines
print("\n" + "=" * 50)
print("Evaluating Baselines...")
print("=" * 50)

n_eval_runs = 10
baseline_results = defaultdict(list)
for _ in range(n_eval_runs):
    baseline_results["sycophantic"].append(
        evaluate_model(None, val_loader, "sycophantic")
    )
    baseline_results["blunt"].append(evaluate_model(None, val_loader, "blunt"))
    baseline_results["random"].append(evaluate_model(None, val_loader, "random"))

for method in baseline_results:
    experiment_data["baselines"][method] = {
        "mean": np.mean(baseline_results[method]),
        "std": np.std(baseline_results[method]),
        "runs": baseline_results[method],
    }

# Print comparison
print("\n" + "=" * 50)
print("Hyperparameter Tuning Results: Epochs")
print("=" * 50)
print("\nDisagreement Acceptance Rates:")
print("-" * 40)
print(f"{'Method':<20} {'Mean':>10} {'Std':>10}")
print("-" * 40)
for n_epochs in epoch_values:
    print(
        f"CCD (epochs={n_epochs}){'':<5} {epoch_results[n_epochs]['final_mean']:>10.4f} {epoch_results[n_epochs]['final_std']:>10.4f}"
    )
print("-" * 40)
print(
    f"{'Sycophantic':<20} {experiment_data['baselines']['sycophantic']['mean']:>10.4f} {experiment_data['baselines']['sycophantic']['std']:>10.4f}"
)
print(
    f"{'Blunt':<20} {experiment_data['baselines']['blunt']['mean']:>10.4f} {experiment_data['baselines']['blunt']['std']:>10.4f}"
)
print(
    f"{'Random':<20} {experiment_data['baselines']['random']['mean']:>10.4f} {experiment_data['baselines']['random']['std']:>10.4f}"
)

# Determine best epochs setting
best_epochs = max(epoch_values, key=lambda x: epoch_results[x]["final_mean"])
print(
    f"\n** Best epochs setting: {best_epochs} with acceptance rate {epoch_results[best_epochs]['final_mean']:.4f} **"
)

# Store final results
experiment_data["final_results"] = {
    "best_epochs": best_epochs,
    "epochs_comparison": {
        n: {
            "mean": epoch_results[n]["final_mean"],
            "std": epoch_results[n]["final_std"],
        }
        for n in epoch_values
    },
}

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Training loss comparison
ax1 = axes[0, 0]
for n_epochs in epoch_values:
    ax1.plot(epoch_results[n_epochs]["train_losses"], label=f"Epochs={n_epochs}")
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Training Loss")
ax1.set_title("Training Loss Comparison (Epochs Tuning)")
ax1.legend()
ax1.grid(True)

# Plot 2: Validation acceptance rate comparison
ax2 = axes[0, 1]
for n_epochs in epoch_values:
    ax2.plot(
        epoch_results[n_epochs]["val_acceptance_rates"], label=f"Epochs={n_epochs}"
    )
ax2.axhline(
    y=experiment_data["baselines"]["blunt"]["mean"],
    color="red",
    linestyle="--",
    label="Blunt Baseline",
)
ax2.axhline(
    y=experiment_data["baselines"]["random"]["mean"],
    color="orange",
    linestyle="--",
    label="Random Baseline",
)
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Validation Acceptance Rate")
ax2.set_title("Validation Acceptance Rate During Training")
ax2.legend()
ax2.grid(True)

# Plot 3: Final performance bar chart
ax3 = axes[1, 0]
methods = ["Sycophantic", "Blunt", "Random"] + [
    f"CCD (epochs={n})" for n in epoch_values
]
means = [
    experiment_data["baselines"]["sycophantic"]["mean"],
    experiment_data["baselines"]["blunt"]["mean"],
    experiment_data["baselines"]["random"]["mean"],
] + [epoch_results[n]["final_mean"] for n in epoch_values]
stds = [
    experiment_data["baselines"]["sycophantic"]["std"],
    experiment_data["baselines"]["blunt"]["std"],
    experiment_data["baselines"]["random"]["std"],
] + [epoch_results[n]["final_std"] for n in epoch_values]
colors = ["gray", "red", "orange", "green", "blue"]
bars = ax3.bar(methods, means, yerr=stds, color=colors, capsize=5)
ax3.set_ylabel("Disagreement Acceptance Rate")
ax3.set_title("Final Performance Comparison")
ax3.set_ylim(0, 1)
ax3.tick_params(axis="x", rotation=45)
for bar, mean in zip(bars, means):
    ax3.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.05,
        f"{mean:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# Plot 4: Convergence analysis (moving average of loss)
ax4 = axes[1, 1]
window = 5
for n_epochs in epoch_values:
    losses = epoch_results[n_epochs]["train_losses"]
    if len(losses) >= window:
        smoothed = np.convolve(losses, np.ones(window) / window, mode="valid")
        ax4.plot(
            range(window - 1, len(losses)),
            smoothed,
            label=f"Epochs={n_epochs} (smoothed)",
        )
ax4.set_xlabel("Epoch")
ax4.set_ylabel("Training Loss (Moving Avg)")
ax4.set_title(f"Convergence Analysis (window={window})")
ax4.legend()
ax4.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "epochs_tuning_results.png"), dpi=150)
plt.close()

# Additional plot: Detailed training curves
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Loss derivative to check convergence
ax1 = axes[0]
for n_epochs in epoch_values:
    losses = epoch_results[n_epochs]["train_losses"]
    loss_diff = np.diff(losses)
    ax1.plot(loss_diff, label=f"Epochs={n_epochs}", alpha=0.7)
ax1.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Loss Change (derivative)")
ax1.set_title("Training Loss Rate of Change")
ax1.legend()
ax1.grid(True)

# Acceptance rate improvement over epochs
ax2 = axes[1]
for n_epochs in epoch_values:
    rates = epoch_results[n_epochs]["val_acceptance_rates"]
    ax2.plot(rates, label=f"Epochs={n_epochs}")
    # Mark final value
    ax2.scatter([len(rates) - 1], [rates[-1]], s=100, zorder=5)
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Validation Acceptance Rate")
ax2.set_title("Acceptance Rate Progress (with final values marked)")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "epochs_convergence_analysis.png"), dpi=150)
plt.close()

# Strategy distribution analysis for best model
best_model = epoch_results[best_epochs]["model"]
best_model.eval()
strategy_counts = np.zeros((NUM_CONTEXTS, NUM_STRATEGIES))

with torch.no_grad():
    for batch in val_loader:
        features = batch["features"].to(device)
        context_types = batch["context_type"].numpy()
        strategies, _ = best_model.select_strategy(features)
        strategies = strategies.cpu().numpy()
        for ctx, strat in zip(context_types, strategies):
            strategy_counts[ctx, strat] += 1

strategy_dist = strategy_counts / strategy_counts.sum(axis=1, keepdims=True)
experiment_data["strategy_distribution"] = strategy_dist

print("\nStrategy Distribution by Context Type (Best Model):")
print(f"{'Context':<20} | " + " | ".join([f"{s:<12}" for s in STRATEGY_NAMES]))
print("-" * 80)
for i, ctx_name in enumerate(CONTEXT_NAMES):
    row = f"{ctx_name:<20} | " + " | ".join(
        [f"{strategy_dist[i,j]:.2f}        " for j in range(NUM_STRATEGIES)]
    )
    print(row)

# Save strategy distribution heatmap
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(strategy_dist, cmap="YlGnBu", aspect="auto")
ax.set_xticks(range(NUM_STRATEGIES))
ax.set_xticklabels(STRATEGY_NAMES, rotation=45, ha="right")
ax.set_yticks(range(NUM_CONTEXTS))
ax.set_yticklabels(CONTEXT_NAMES)
ax.set_xlabel("Strategy")
ax.set_ylabel("Context Type")
ax.set_title(f"CCD Learned Strategy Distribution (Best: epochs={best_epochs})")
plt.colorbar(im, label="Probability")

for i in range(NUM_CONTEXTS):
    for j in range(NUM_STRATEGIES):
        ax.text(
            j, i, f"{strategy_dist[i,j]:.2f}", ha="center", va="center", color="black"
        )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ccd_strategy_distribution.png"), dpi=150)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\nResults saved to {working_dir}")
print(
    "Figures saved: epochs_tuning_results.png, epochs_convergence_analysis.png, ccd_strategy_distribution.png"
)
print(
    f"\n** Final best disagreement_acceptance_rate (CCD, epochs={best_epochs}): {epoch_results[best_epochs]['final_mean']:.4f} **"
)
