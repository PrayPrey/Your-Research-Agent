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
NUM_CONTEXTS = 4  # factual_error, reasoning_flaw, value_conflict, preference_mismatch
NUM_STRATEGIES = 4  # direct_correction, socratic_questioning, evidence_presentation, gentle_suggestion
CONTEXT_NAMES = [
    "factual_error",
    "reasoning_flaw",
    "value_conflict",
    "preference_mismatch",
]
STRATEGY_NAMES = ["direct_correction", "socratic", "evidence", "gentle_suggestion"]


# Synthetic data generation
def generate_synthetic_data(n_samples=1000):
    """Generate synthetic user-AI interaction data"""
    data = []
    for _ in range(n_samples):
        context_type = np.random.randint(0, NUM_CONTEXTS)
        user_confidence = np.random.uniform(0.3, 1.0)
        user_correct = np.random.random() < 0.4  # 40% chance user is correct

        # User features: context_type (one-hot), confidence, correctness indicator
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


# Simulated user receptivity model
def simulate_user_receptivity(
    context_type, strategy, user_confidence, base_receptivity=0.5
):
    """Simulate how receptive a user is to a given disagreement strategy"""
    # Strategy effectiveness matrix: rows=context, cols=strategy
    # Higher values = better match between context and strategy
    effectiveness = np.array(
        [
            [0.9, 0.5, 0.8, 0.4],  # factual_error: direct/evidence work best
            [0.4, 0.9, 0.7, 0.5],  # reasoning_flaw: socratic works best
            [0.2, 0.5, 0.6, 0.9],  # value_conflict: gentle suggestion best
            [0.3, 0.6, 0.5, 0.8],  # preference_mismatch: gentle/socratic
        ]
    )

    strategy_match = effectiveness[context_type, strategy]

    # High confidence users are less receptive
    confidence_penalty = (user_confidence - 0.5) * 0.3

    receptivity = base_receptivity + strategy_match * 0.4 - confidence_penalty
    receptivity = np.clip(receptivity, 0.1, 0.95)

    # Stochastic acceptance
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


# CCD Strategy Selection Model
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
        logits = self.network(x)
        return logits

    def select_strategy(self, x, temperature=1.0):
        logits = self.forward(x)
        probs = torch.softmax(logits / temperature, dim=-1)
        strategy = torch.multinomial(probs, 1).squeeze(-1)
        return strategy, probs


# Training function using REINFORCE
def train_ccd_model(model, train_loader, val_loader, epochs=50, lr=0.001):
    optimizer = optim.Adam(model.parameters(), lr=lr)

    train_losses = []
    val_acceptance_rates = []

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        epoch_rewards = []

        for batch in train_loader:
            features = batch["features"].to(device)
            context_types = batch["context_type"].numpy()
            user_confidences = batch["user_confidence"].numpy()
            user_corrects = batch["user_correct"].numpy()

            optimizer.zero_grad()

            # Select strategies
            strategies, probs = model.select_strategy(features)
            strategies_np = strategies.cpu().numpy()

            # Simulate user responses and compute rewards
            rewards = []
            for i in range(len(strategies_np)):
                if user_corrects[i]:
                    # User is correct, AI should not disagree strongly
                    # Reward for not using direct correction
                    reward = 0.5 if strategies_np[i] != 0 else 0.0
                else:
                    # User is incorrect, AI should disagree
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], strategies_np[i], user_confidences[i]
                    )
                    reward = 1.0 if accepts else -0.1
                rewards.append(reward)

            rewards = torch.FloatTensor(rewards).to(device)
            epoch_rewards.extend(rewards.cpu().numpy())

            # REINFORCE loss
            log_probs = torch.log(
                probs.gather(1, strategies.unsqueeze(1)).squeeze(1) + 1e-8
            )
            loss = -torch.mean(log_probs * rewards)

            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        # Validation
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

    model.eval() if mode == "ccd" else None

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
                    continue  # Only count disagreements when user is wrong

                total_disagreements += 1

                if mode == "sycophantic":
                    # Sycophantic baseline: never disagrees effectively
                    accepted_disagreements += 0
                elif mode == "blunt":
                    # Blunt truth-telling: always uses direct correction
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], 0, user_confidences[i]
                    )
                    if accepts:
                        accepted_disagreements += 1
                elif mode == "ccd":
                    # CCD: uses learned strategy
                    strategy, _ = model.select_strategy(features[i : i + 1])
                    strategy = strategy.item()
                    accepts, _ = simulate_user_receptivity(
                        context_types[i], strategy, user_confidences[i]
                    )
                    if accepts:
                        accepted_disagreements += 1
                elif mode == "random":
                    # Random strategy selection
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

# Initialize experiment data tracking
experiment_data = {
    "ccd": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
    },
    "baselines": {
        "sycophantic": [],
        "blunt": [],
        "random": [],
    },
}

# Train CCD model
print("\n" + "=" * 50)
print("Training CCD Model...")
print("=" * 50)

ccd_model = CCDModel().to(device)
train_losses, val_acceptance_rates = train_ccd_model(
    ccd_model, train_loader, val_loader, epochs=50
)

experiment_data["ccd"]["losses"]["train"] = train_losses
experiment_data["ccd"]["metrics"]["val"] = val_acceptance_rates

# Evaluate all conditions
print("\n" + "=" * 50)
print("Final Evaluation on Validation Set")
print("=" * 50)

# Run multiple evaluations for stable estimates
n_eval_runs = 10
results = defaultdict(list)

for _ in range(n_eval_runs):
    results["sycophantic"].append(evaluate_model(None, val_loader, "sycophantic"))
    results["blunt"].append(evaluate_model(None, val_loader, "blunt"))
    results["random"].append(evaluate_model(None, val_loader, "random"))
    results["ccd"].append(evaluate_model(ccd_model, val_loader, "ccd"))

# Compute means and stds
final_results = {}
for method in results:
    mean = np.mean(results[method])
    std = np.std(results[method])
    final_results[method] = {"mean": mean, "std": std}
    experiment_data["baselines"][method] = results[method] if method != "ccd" else None

print("\nDisagreement Acceptance Rates:")
print("-" * 40)
for method in ["sycophantic", "blunt", "random", "ccd"]:
    print(
        f"{method:15s}: {final_results[method]['mean']:.4f} ± {final_results[method]['std']:.4f}"
    )

print(
    f"\n** Final disagreement_acceptance_rate (CCD): {final_results['ccd']['mean']:.4f} **"
)

# Analyze strategy distribution by context
print("\n" + "=" * 50)
print("CCD Strategy Selection Analysis")
print("=" * 50)

ccd_model.eval()
strategy_counts = np.zeros((NUM_CONTEXTS, NUM_STRATEGIES))

with torch.no_grad():
    for batch in val_loader:
        features = batch["features"].to(device)
        context_types = batch["context_type"].numpy()

        strategies, _ = ccd_model.select_strategy(features)
        strategies = strategies.cpu().numpy()

        for ctx, strat in zip(context_types, strategies):
            strategy_counts[ctx, strat] += 1

# Normalize
strategy_dist = strategy_counts / strategy_counts.sum(axis=1, keepdims=True)

print("\nStrategy Distribution by Context Type:")
print(f"{'Context':<20} | " + " | ".join([f"{s:<12}" for s in STRATEGY_NAMES]))
print("-" * 80)
for i, ctx_name in enumerate(CONTEXT_NAMES):
    row = f"{ctx_name:<20} | " + " | ".join(
        [f"{strategy_dist[i,j]:.2f}        " for j in range(NUM_STRATEGIES)]
    )
    print(row)

# Visualization
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Plot 1: Training curves
ax1 = axes[0]
ax1.plot(train_losses, label="Training Loss")
ax1.set_xlabel("Epoch")
ax1.set_ylabel("Loss")
ax1.set_title("CCD Training Loss")
ax1.legend()
ax1.grid(True)

# Plot 2: Validation acceptance rate over training
ax2 = axes[1]
ax2.plot(val_acceptance_rates, label="CCD", color="green")
ax2.axhline(
    y=final_results["blunt"]["mean"],
    color="red",
    linestyle="--",
    label="Blunt Baseline",
)
ax2.axhline(
    y=final_results["random"]["mean"],
    color="orange",
    linestyle="--",
    label="Random Baseline",
)
ax2.axhline(y=0, color="gray", linestyle="--", label="Sycophantic (0)")
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Disagreement Acceptance Rate")
ax2.set_title("Validation Acceptance Rate During Training")
ax2.legend()
ax2.grid(True)

# Plot 3: Final comparison bar chart
ax3 = axes[2]
methods = ["Sycophantic", "Blunt", "Random", "CCD"]
means = [final_results[m.lower()]["mean"] for m in methods]
stds = [final_results[m.lower()]["std"] for m in methods]
colors = ["gray", "red", "orange", "green"]
bars = ax3.bar(methods, means, yerr=stds, color=colors, capsize=5)
ax3.set_ylabel("Disagreement Acceptance Rate")
ax3.set_title("Final Performance Comparison")
ax3.set_ylim(0, 1)
for bar, mean in zip(bars, means):
    ax3.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.05,
        f"{mean:.3f}",
        ha="center",
        va="bottom",
    )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ccd_experiment_results.png"), dpi=150)
plt.close()

# Plot strategy distribution heatmap
fig, ax = plt.subplots(figsize=(10, 6))
im = ax.imshow(strategy_dist, cmap="YlGnBu", aspect="auto")
ax.set_xticks(range(NUM_STRATEGIES))
ax.set_xticklabels(STRATEGY_NAMES, rotation=45, ha="right")
ax.set_yticks(range(NUM_CONTEXTS))
ax.set_yticklabels(CONTEXT_NAMES)
ax.set_xlabel("Strategy")
ax.set_ylabel("Context Type")
ax.set_title("CCD Learned Strategy Distribution by Context")
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
experiment_data["final_results"] = {
    k: {"mean": v["mean"], "std": v["std"]} for k, v in final_results.items()
}
experiment_data["strategy_distribution"] = strategy_dist
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\nResults saved to {working_dir}")
print("Figures saved: ccd_experiment_results.png, ccd_strategy_distribution.png")
