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

# Define learning rates to test
ai_learning_rates = [0.0001, 0.0005, 0.001, 0.005, 0.01]
human_learning_rates = [0.0001, 0.0005, 0.001, 0.005, 0.01]

# Initialize experiment data structure
experiment_data = {
    "hyperparameter_tuning": {
        "learning_rates": {
            "ai_lrs": ai_learning_rates,
            "human_lrs": human_learning_rates,
        },
        "results": {},
    }
}


# Generate synthetic dataset for decision-making tasks
def generate_decision_task_data(n_samples=2000, n_features=20):
    X = np.random.randn(n_samples, n_features).astype(np.float32)
    weights = np.random.randn(n_features)
    logits = X @ weights + np.random.randn(n_samples) * 0.5
    y_true = (logits > 0).astype(np.float32)
    task_complexity = np.abs(logits) / (np.abs(logits).max())
    task_complexity = 1 - task_complexity
    return X, y_true, task_complexity


# Human decision model
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
    human_model.eval()
    ai_model.eval()
    with torch.no_grad():
        human_logits = human_model(X, cognitive_load).squeeze()
        human_initial = torch.sigmoid(human_logits) > 0.5
        human_confidence = torch.abs(torch.sigmoid(human_logits) - 0.5) * 2

        ai_logits = ai_model(X).squeeze()
        ai_recommendation = torch.sigmoid(ai_logits) > 0.5
        ai_correct = ai_recommendation == y_true

        if interaction_mode == "supportive":
            ai_challenges = torch.zeros_like(human_initial, dtype=torch.bool)
        elif interaction_mode == "challenging":
            ai_challenges = ai_recommendation != human_initial
        else:
            high_cognitive_load = cognitive_load > adaptive_threshold
            ai_challenges = (ai_recommendation != human_initial) & (
                ~high_cognitive_load
            )

        change_decision = ai_challenges & (human_confidence < 0.6)
        human_final = human_initial.clone()
        human_final[change_decision] = ai_recommendation[change_decision]

        agreement_with_ai = (human_final == ai_recommendation).float()
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
        decision_accuracy = (human_final == y_true).float().mean()
        agreement_rate = agreement_with_ai.mean()

    return {
        "appropriate_reliance": appropriate_reliance.item(),
        "decision_accuracy": decision_accuracy.item(),
        "agreement_rate": agreement_rate.item(),
    }


# Hyperparameter tuning loop
print("\n" + "=" * 80)
print("HYPERPARAMETER TUNING: Learning Rate Optimization")
print("=" * 80)

modes = ["supportive", "challenging", "adaptive"]
n_epochs = 100
ai_epochs = 50

for ai_lr in ai_learning_rates:
    print(f"\n{'='*80}")
    print(f"Training AI Assistant with learning rate: {ai_lr}")
    print(f"{'='*80}")

    # Train AI assistant model
    torch.manual_seed(42)
    ai_model = AIAssistantModel(input_dim=20, hidden_dim=64).to(device)
    ai_optimizer = optim.Adam(ai_model.parameters(), lr=ai_lr)
    ai_criterion = nn.BCEWithLogitsLoss()

    ai_train_losses = []
    ai_test_losses = []
    ai_test_accs = []

    for epoch in range(ai_epochs):
        ai_model.train()
        ai_optimizer.zero_grad()
        ai_logits = ai_model(X_train_t).squeeze()
        ai_loss = ai_criterion(ai_logits, y_train_t)
        ai_loss.backward()
        ai_optimizer.step()

        ai_model.eval()
        with torch.no_grad():
            test_logits = ai_model(X_test_t).squeeze()
            test_loss = ai_criterion(test_logits, y_test_t)
            test_acc = ((torch.sigmoid(test_logits) > 0.5) == y_test_t).float().mean()

        ai_train_losses.append(ai_loss.item())
        ai_test_losses.append(test_loss.item())
        ai_test_accs.append(test_acc.item())

        if (epoch + 1) % 10 == 0:
            print(
                f"AI Epoch {epoch+1}: train_loss={ai_loss.item():.4f}, test_loss={test_loss.item():.4f}, test_acc={test_acc.item():.4f}"
            )

    for human_lr in human_learning_rates:
        print(f"\n  Testing Human LR: {human_lr}")

        config_key = f"ai_lr_{ai_lr}_human_lr_{human_lr}"
        experiment_data["hyperparameter_tuning"]["results"][config_key] = {
            "ai_lr": ai_lr,
            "human_lr": human_lr,
            "ai_train_losses": ai_train_losses,
            "ai_test_losses": ai_test_losses,
            "ai_test_accs": ai_test_accs,
            "modes": {},
        }

        for mode in modes:
            torch.manual_seed(42)
            human_model = HumanDecisionModel(input_dim=20, hidden_dim=64).to(device)
            human_optimizer = optim.Adam(human_model.parameters(), lr=human_lr)
            human_criterion = nn.BCEWithLogitsLoss()

            mode_data = {
                "epochs": [],
                "train_losses": [],
                "val_losses": [],
                "metrics": {
                    "appropriate_reliance": [],
                    "decision_accuracy": [],
                    "agreement_rate": [],
                },
            }

            for epoch in range(n_epochs):
                human_model.train()
                human_optimizer.zero_grad()
                train_logits = human_model(X_train_t, complexity_train_t).squeeze()
                train_loss = human_criterion(train_logits, y_train_t)
                train_loss.backward()
                human_optimizer.step()

                if (epoch + 1) % 10 == 0:
                    test_results = simulate_interaction(
                        human_model,
                        ai_model,
                        X_test_t,
                        y_test_t,
                        complexity_test_t,
                        mode,
                    )

                    human_model.eval()
                    with torch.no_grad():
                        val_logits = human_model(X_test_t, complexity_test_t).squeeze()
                        val_loss = human_criterion(val_logits, y_test_t)

                    mode_data["epochs"].append(epoch + 1)
                    mode_data["train_losses"].append(train_loss.item())
                    mode_data["val_losses"].append(val_loss.item())
                    mode_data["metrics"]["appropriate_reliance"].append(
                        test_results["appropriate_reliance"]
                    )
                    mode_data["metrics"]["decision_accuracy"].append(
                        test_results["decision_accuracy"]
                    )
                    mode_data["metrics"]["agreement_rate"].append(
                        test_results["agreement_rate"]
                    )

            experiment_data["hyperparameter_tuning"]["results"][config_key]["modes"][
                mode
            ] = mode_data
            print(
                f"    {mode}: AR={mode_data['metrics']['appropriate_reliance'][-1]:.4f}, "
                f"Acc={mode_data['metrics']['decision_accuracy'][-1]:.4f}, "
                f"Agr={mode_data['metrics']['agreement_rate'][-1]:.4f}, "
                f"Loss={mode_data['val_losses'][-1]:.4f}"
            )

# Analyze results and find optimal learning rates
print("\n" + "=" * 80)
print("HYPERPARAMETER TUNING RESULTS")
print("=" * 80)

best_configs = {}
for mode in modes:
    best_score = -1
    best_config = None

    for config_key, config_data in experiment_data["hyperparameter_tuning"][
        "results"
    ].items():
        mode_data = config_data["modes"][mode]
        # Composite score: weighted average of metrics
        final_ar = mode_data["metrics"]["appropriate_reliance"][-1]
        final_acc = mode_data["metrics"]["decision_accuracy"][-1]
        final_agr = mode_data["metrics"]["agreement_rate"][-1]
        composite_score = 0.5 * final_ar + 0.4 * final_acc + 0.1 * final_agr

        if composite_score > best_score:
            best_score = composite_score
            best_config = {
                "config_key": config_key,
                "ai_lr": config_data["ai_lr"],
                "human_lr": config_data["human_lr"],
                "appropriate_reliance": final_ar,
                "decision_accuracy": final_acc,
                "agreement_rate": final_agr,
                "composite_score": composite_score,
            }

    best_configs[mode] = best_config
    print(f"\n{mode.upper()} Mode - Best Configuration:")
    print(f"  AI Learning Rate: {best_config['ai_lr']}")
    print(f"  Human Learning Rate: {best_config['human_lr']}")
    print(f"  Appropriate Reliance: {best_config['appropriate_reliance']:.4f}")
    print(f"  Decision Accuracy: {best_config['decision_accuracy']:.4f}")
    print(f"  Agreement Rate: {best_config['agreement_rate']:.4f}")
    print(f"  Composite Score: {best_config['composite_score']:.4f}")

experiment_data["hyperparameter_tuning"]["best_configs"] = best_configs

# Visualization 1: Heatmap of composite scores for each mode
for mode in modes:
    composite_scores = np.zeros((len(ai_learning_rates), len(human_learning_rates)))

    for i, ai_lr in enumerate(ai_learning_rates):
        for j, human_lr in enumerate(human_learning_rates):
            config_key = f"ai_lr_{ai_lr}_human_lr_{human_lr}"
            mode_data = experiment_data["hyperparameter_tuning"]["results"][config_key][
                "modes"
            ][mode]
            final_ar = mode_data["metrics"]["appropriate_reliance"][-1]
            final_acc = mode_data["metrics"]["decision_accuracy"][-1]
            final_agr = mode_data["metrics"]["agreement_rate"][-1]
            composite_scores[i, j] = 0.5 * final_ar + 0.4 * final_acc + 0.1 * final_agr

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(composite_scores, cmap="viridis", aspect="auto")
    ax.set_xticks(np.arange(len(human_learning_rates)))
    ax.set_yticks(np.arange(len(ai_learning_rates)))
    ax.set_xticklabels([f"{lr:.4f}" for lr in human_learning_rates])
    ax.set_yticklabels([f"{lr:.4f}" for lr in ai_learning_rates])
    ax.set_xlabel("Human Learning Rate", fontsize=12)
    ax.set_ylabel("AI Learning Rate", fontsize=12)
    ax.set_title(
        f"Composite Score Heatmap - {mode.capitalize()} Mode",
        fontsize=14,
        fontweight="bold",
    )

    for i in range(len(ai_learning_rates)):
        for j in range(len(human_learning_rates)):
            text = ax.text(
                j,
                i,
                f"{composite_scores[i, j]:.3f}",
                ha="center",
                va="center",
                color="w",
                fontsize=9,
            )

    plt.colorbar(im, ax=ax, label="Composite Score")
    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, f"lr_heatmap_{mode}.png"), dpi=300)
    plt.close()

# Visualization 2: Training curves for best configurations
fig, axes = plt.subplots(3, 3, figsize=(18, 12))

for idx, mode in enumerate(modes):
    best_config = best_configs[mode]
    config_key = best_config["config_key"]
    config_data = experiment_data["hyperparameter_tuning"]["results"][config_key]
    mode_data = config_data["modes"][mode]

    # Plot appropriate reliance
    axes[idx, 0].plot(
        mode_data["epochs"],
        mode_data["metrics"]["appropriate_reliance"],
        marker="o",
        linewidth=2,
        color="#2ecc71",
    )
    axes[idx, 0].set_xlabel("Epoch")
    axes[idx, 0].set_ylabel("Appropriate Reliance")
    axes[idx, 0].set_title(
        f"{mode.capitalize()} - AR (AI LR={best_config['ai_lr']}, Human LR={best_config['human_lr']})"
    )
    axes[idx, 0].grid(True, alpha=0.3)

    # Plot decision accuracy
    axes[idx, 1].plot(
        mode_data["epochs"],
        mode_data["metrics"]["decision_accuracy"],
        marker="s",
        linewidth=2,
        color="#3498db",
    )
    axes[idx, 1].set_xlabel("Epoch")
    axes[idx, 1].set_ylabel("Decision Accuracy")
    axes[idx, 1].set_title(f"{mode.capitalize()} - Accuracy")
    axes[idx, 1].grid(True, alpha=0.3)

    # Plot validation loss
    axes[idx, 2].plot(
        mode_data["epochs"],
        mode_data["val_losses"],
        marker="^",
        linewidth=2,
        color="#e74c3c",
    )
    axes[idx, 2].set_xlabel("Epoch")
    axes[idx, 2].set_ylabel("Validation Loss")
    axes[idx, 2].set_title(f"{mode.capitalize()} - Val Loss")
    axes[idx, 2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "best_lr_training_curves.png"), dpi=300)
plt.close()

# Visualization 3: Comparison of best learning rates across modes
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
metrics_to_plot = ["appropriate_reliance", "decision_accuracy", "agreement_rate"]
metric_labels = ["Appropriate Reliance", "Decision Accuracy", "Agreement Rate"]

for idx, (metric, label) in enumerate(zip(metrics_to_plot, metric_labels)):
    values = [best_configs[mode][metric] for mode in modes]
    bars = axes[idx].bar(
        modes, values, color=["#2ecc71", "#e74c3c", "#3498db"], alpha=0.8
    )
    axes[idx].set_ylabel(label, fontsize=11)
    axes[idx].set_ylim([0, 1])
    axes[idx].set_title(f"Best {label}", fontsize=12, fontweight="bold")
    axes[idx].grid(True, alpha=0.3, axis="y")

    for bar, mode in zip(bars, modes):
        height = bar.get_height()
        ai_lr = best_configs[mode]["ai_lr"]
        human_lr = best_configs[mode]["human_lr"]
        axes[idx].text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:.3f}\nAI:{ai_lr}\nH:{human_lr}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "best_lr_metrics_comparison.png"), dpi=300)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(
    f"\nAll experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}"
)

print("\n" + "=" * 80)
print("HYPERPARAMETER TUNING COMPLETE")
print("=" * 80)
print(f"Visualizations saved to: {working_dir}")
print("Generated plots:")
print("  - lr_heatmap_supportive.png")
print("  - lr_heatmap_challenging.png")
print("  - lr_heatmap_adaptive.png")
print("  - best_lr_training_curves.png")
print("  - best_lr_metrics_comparison.png")
