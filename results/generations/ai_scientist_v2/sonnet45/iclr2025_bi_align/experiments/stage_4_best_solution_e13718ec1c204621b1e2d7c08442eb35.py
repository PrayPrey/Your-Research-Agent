import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from collections import defaultdict

# Setup
working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds
np.random.seed(42)
torch.manual_seed(42)

# Initialize experiment data structure
experiment_data = {
    "supportive": {
        "metrics": {
            "appropriate_reliance": [],
            "decision_accuracy": [],
            "agreement_rate": [],
        },
        "losses": [],
        "cognitive_loads": [],
        "epochs": [],
    },
    "challenging": {
        "metrics": {
            "appropriate_reliance": [],
            "decision_accuracy": [],
            "agreement_rate": [],
        },
        "losses": [],
        "cognitive_loads": [],
        "epochs": [],
    },
    "adaptive": {
        "metrics": {
            "appropriate_reliance": [],
            "decision_accuracy": [],
            "agreement_rate": [],
        },
        "losses": [],
        "cognitive_loads": [],
        "epochs": [],
    },
}


# Generate synthetic dataset for decision-making tasks
def generate_decision_task_data(n_samples=2000, n_features=20):
    """
    Generate synthetic data for collaborative decision-making
    Features represent task characteristics (e.g., medical symptoms, financial indicators)
    """
    X = np.random.randn(n_samples, n_features).astype(np.float32)
    # True labels (ground truth)
    weights = np.random.randn(n_features)
    logits = X @ weights + np.random.randn(n_samples) * 0.5
    y_true = (logits > 0).astype(np.float32)

    # Task complexity (affects cognitive load)
    task_complexity = np.abs(logits) / (np.abs(logits).max())  # normalized difficulty
    task_complexity = 1 - task_complexity  # higher = more difficult

    return X, y_true, task_complexity


# Human decision model (influenced by cognitive load)
class HumanDecisionModel(nn.Module):
    def __init__(self, input_dim=20, hidden_dim=64):
        super(HumanDecisionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x, cognitive_load=None):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))

        # If under high cognitive load, add noise to simulate degraded performance
        if cognitive_load is not None and self.training:
            noise = torch.randn_like(x) * cognitive_load.unsqueeze(1) * 0.5
            x = x + noise

        x = self.fc3(x)
        return x


# AI assistant model
class AIAssistantModel(nn.Module):
    def __init__(self, input_dim=20, hidden_dim=64):
        super(AIAssistantModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# Generate data
print("Generating synthetic decision-making data...")
X, y_true, task_complexity = generate_decision_task_data(n_samples=2000, n_features=20)
X_train, X_test, y_train, y_test, complexity_train, complexity_test = train_test_split(
    X, y_true, task_complexity, test_size=0.3, random_state=42
)

# Convert to tensors
X_train_t = torch.FloatTensor(X_train).to(device)
y_train_t = torch.FloatTensor(y_train).to(device)
complexity_train_t = torch.FloatTensor(complexity_train).to(device)
X_test_t = torch.FloatTensor(X_test).to(device)
y_test_t = torch.FloatTensor(y_test).to(device)
complexity_test_t = torch.FloatTensor(complexity_test).to(device)

# Train AI assistant model (this will provide recommendations)
print("\nTraining AI Assistant model...")
ai_model = AIAssistantModel(input_dim=20, hidden_dim=64).to(device)
ai_optimizer = optim.Adam(ai_model.parameters(), lr=0.001)
ai_criterion = nn.BCEWithLogitsLoss()

for epoch in range(50):
    ai_model.train()
    ai_optimizer.zero_grad()
    ai_logits = ai_model(X_train_t).squeeze()
    ai_loss = ai_criterion(ai_logits, y_train_t)
    ai_loss.backward()
    ai_optimizer.step()

    if (epoch + 1) % 10 == 0:
        ai_model.eval()
        with torch.no_grad():
            test_logits = ai_model(X_test_t).squeeze()
            test_loss = ai_criterion(test_logits, y_test_t)
            test_acc = ((torch.sigmoid(test_logits) > 0.5) == y_test_t).float().mean()
            print(
                f"AI Assistant Epoch {epoch+1}: train_loss={ai_loss.item():.4f}, test_loss={test_loss.item():.4f}, test_acc={test_acc.item():.4f}"
            )


# Function to simulate human-AI interaction
def simulate_interaction(
    human_model,
    ai_model,
    X,
    y_true,
    cognitive_load,
    interaction_mode,
    adaptive_threshold=0.6,
):
    """
    Simulate human-AI collaborative decision making
    interaction_mode: 'supportive', 'challenging', or 'adaptive'
    """
    human_model.eval()
    ai_model.eval()

    with torch.no_grad():
        # Get initial human decision
        human_logits = human_model(X, cognitive_load).squeeze()
        human_initial = torch.sigmoid(human_logits) > 0.5
        human_confidence = torch.abs(torch.sigmoid(human_logits) - 0.5) * 2  # 0 to 1

        # Get AI recommendation
        ai_logits = ai_model(X).squeeze()
        ai_recommendation = torch.sigmoid(ai_logits) > 0.5
        ai_correct = ai_recommendation == y_true

        # Determine AI behavior based on mode
        if interaction_mode == "supportive":
            # AI always agrees/supports human
            ai_challenges = torch.zeros_like(human_initial, dtype=torch.bool)
        elif interaction_mode == "challenging":
            # AI always challenges when disagrees
            ai_challenges = ai_recommendation != human_initial
        else:  # adaptive
            # AI challenges only when cognitive load is low
            high_cognitive_load = cognitive_load > adaptive_threshold
            ai_challenges = (ai_recommendation != human_initial) & (
                ~high_cognitive_load
            )

        # Human final decision (may change if AI challenges and human has low confidence)
        change_decision = ai_challenges & (human_confidence < 0.6)
        human_final = human_initial.clone()
        human_final[change_decision] = ai_recommendation[change_decision]

        # Calculate metrics
        agreement_with_ai = (human_final == ai_recommendation).float()

        # Appropriate reliance score
        agreement_when_ai_correct = (
            agreement_with_ai[ai_correct].mean()
            if ai_correct.sum() > 0
            else torch.tensor(0.0)
        )
        disagreement_when_ai_incorrect = (
            (1 - agreement_with_ai[~ai_correct]).mean()
            if (~ai_correct).sum() > 0
            else torch.tensor(0.0)
        )
        appropriate_reliance = (
            agreement_when_ai_correct + disagreement_when_ai_incorrect
        ) / 2

        # Decision accuracy
        decision_accuracy = (human_final == y_true).float().mean()

        # Overall agreement rate
        agreement_rate = agreement_with_ai.mean()

    return {
        "appropriate_reliance": appropriate_reliance.item(),
        "decision_accuracy": decision_accuracy.item(),
        "agreement_rate": agreement_rate.item(),
        "human_final": human_final,
        "ai_recommendation": ai_recommendation,
    }


# Train human decision models and evaluate different interaction modes
print("\n" + "=" * 80)
print("Training Human Decision Models and Evaluating Interaction Modes")
print("=" * 80)

modes = ["supportive", "challenging", "adaptive"]
n_epochs = 100

for mode in modes:
    print(f"\n{'='*80}")
    print(f"Training with {mode.upper()} AI interaction mode")
    print(f"{'='*80}")

    # Create new human model for this condition
    human_model = HumanDecisionModel(input_dim=20, hidden_dim=64).to(device)
    human_optimizer = optim.Adam(human_model.parameters(), lr=0.001)
    human_criterion = nn.BCEWithLogitsLoss()

    for epoch in range(n_epochs):
        human_model.train()

        # Training phase
        human_optimizer.zero_grad()
        train_logits = human_model(X_train_t, complexity_train_t).squeeze()
        train_loss = human_criterion(train_logits, y_train_t)
        train_loss.backward()
        human_optimizer.step()

        # Evaluation phase
        if (epoch + 1) % 10 == 0:
            # Simulate interaction on test set
            test_results = simulate_interaction(
                human_model,
                ai_model,
                X_test_t,
                y_test_t,
                complexity_test_t,
                mode,
                adaptive_threshold=0.6,
            )

            # Compute validation loss
            human_model.eval()
            with torch.no_grad():
                val_logits = human_model(X_test_t, complexity_test_t).squeeze()
                val_loss = human_criterion(val_logits, y_test_t)

            # Store metrics
            experiment_data[mode]["epochs"].append(epoch + 1)
            experiment_data[mode]["losses"].append(val_loss.item())
            experiment_data[mode]["metrics"]["appropriate_reliance"].append(
                test_results["appropriate_reliance"]
            )
            experiment_data[mode]["metrics"]["decision_accuracy"].append(
                test_results["decision_accuracy"]
            )
            experiment_data[mode]["metrics"]["agreement_rate"].append(
                test_results["agreement_rate"]
            )
            experiment_data[mode]["cognitive_loads"].append(
                complexity_test_t.mean().item()
            )

            print(
                f"Epoch {epoch+1}: validation_loss = {val_loss.item():.4f}, "
                f"appropriate_reliance = {test_results['appropriate_reliance']:.4f}, "
                f"decision_accuracy = {test_results['decision_accuracy']:.4f}, "
                f"agreement_rate = {test_results['agreement_rate']:.4f}"
            )

# Final evaluation and comparison
print("\n" + "=" * 80)
print("FINAL RESULTS COMPARISON")
print("=" * 80)

final_results = {}
for mode in modes:
    final_results[mode] = {
        "appropriate_reliance": experiment_data[mode]["metrics"][
            "appropriate_reliance"
        ][-1],
        "decision_accuracy": experiment_data[mode]["metrics"]["decision_accuracy"][-1],
        "agreement_rate": experiment_data[mode]["metrics"]["agreement_rate"][-1],
        "final_loss": experiment_data[mode]["losses"][-1],
    }
    print(f"\n{mode.upper()} AI:")
    print(
        f"  Appropriate Reliance Score: {final_results[mode]['appropriate_reliance']:.4f}"
    )
    print(f"  Decision Accuracy: {final_results[mode]['decision_accuracy']:.4f}")
    print(f"  Agreement Rate: {final_results[mode]['agreement_rate']:.4f}")
    print(f"  Final Validation Loss: {final_results[mode]['final_loss']:.4f}")

# Visualizations
print("\nGenerating visualizations...")

# Plot 1: Appropriate Reliance Score over epochs
fig, ax = plt.subplots(figsize=(10, 6))
for mode in modes:
    ax.plot(
        experiment_data[mode]["epochs"],
        experiment_data[mode]["metrics"]["appropriate_reliance"],
        marker="o",
        label=mode.capitalize(),
        linewidth=2,
    )
ax.set_xlabel("Epoch", fontsize=12)
ax.set_ylabel("Appropriate Reliance Score", fontsize=12)
ax.set_title(
    "Appropriate Reliance Score Across AI Interaction Modes",
    fontsize=14,
    fontweight="bold",
)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "appropriate_reliance_comparison.png"), dpi=300)
plt.close()

# Plot 2: Decision Accuracy over epochs
fig, ax = plt.subplots(figsize=(10, 6))
for mode in modes:
    ax.plot(
        experiment_data[mode]["epochs"],
        experiment_data[mode]["metrics"]["decision_accuracy"],
        marker="s",
        label=mode.capitalize(),
        linewidth=2,
    )
ax.set_xlabel("Epoch", fontsize=12)
ax.set_ylabel("Decision Accuracy", fontsize=12)
ax.set_title(
    "Decision Accuracy Across AI Interaction Modes", fontsize=14, fontweight="bold"
)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "decision_accuracy_comparison.png"), dpi=300)
plt.close()

# Plot 3: Agreement Rate over epochs
fig, ax = plt.subplots(figsize=(10, 6))
for mode in modes:
    ax.plot(
        experiment_data[mode]["epochs"],
        experiment_data[mode]["metrics"]["agreement_rate"],
        marker="^",
        label=mode.capitalize(),
        linewidth=2,
    )
ax.set_xlabel("Epoch", fontsize=12)
ax.set_ylabel("Agreement Rate with AI", fontsize=12)
ax.set_title(
    "Human-AI Agreement Rate Across Interaction Modes", fontsize=14, fontweight="bold"
)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "agreement_rate_comparison.png"), dpi=300)
plt.close()

# Plot 4: Bar chart of final metrics
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
metrics_to_plot = ["appropriate_reliance", "decision_accuracy", "agreement_rate"]
metric_labels = ["Appropriate Reliance", "Decision Accuracy", "Agreement Rate"]

for idx, (metric, label) in enumerate(zip(metrics_to_plot, metric_labels)):
    values = [final_results[mode][metric] for mode in modes]
    bars = axes[idx].bar(
        modes, values, color=["#2ecc71", "#e74c3c", "#3498db"], alpha=0.8
    )
    axes[idx].set_ylabel(label, fontsize=11)
    axes[idx].set_ylim([0, 1])
    axes[idx].set_title(label, fontsize=12, fontweight="bold")
    axes[idx].grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        axes[idx].text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "final_metrics_comparison.png"), dpi=300)
plt.close()

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(
    f"\nAll experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}"
)

print("\n" + "=" * 80)
print("EXPERIMENT COMPLETE")
print("=" * 80)
print(f"Visualizations saved to: {working_dir}")
print("Generated plots:")
print("  - appropriate_reliance_comparison.png")
print("  - decision_accuracy_comparison.png")
print("  - agreement_rate_comparison.png")
print("  - final_metrics_comparison.png")
