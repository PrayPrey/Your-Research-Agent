import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

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
    "with_cognitive_load": {
        "supportive": {
            "metrics": {
                "appropriate_reliance": [],
                "decision_accuracy": [],
                "agreement_rate": [],
            },
            "losses": [],
            "epochs": [],
        },
        "challenging": {
            "metrics": {
                "appropriate_reliance": [],
                "decision_accuracy": [],
                "agreement_rate": [],
            },
            "losses": [],
            "epochs": [],
        },
        "adaptive": {
            "metrics": {
                "appropriate_reliance": [],
                "decision_accuracy": [],
                "agreement_rate": [],
            },
            "losses": [],
            "epochs": [],
        },
    },
    "without_cognitive_load": {
        "supportive": {
            "metrics": {
                "appropriate_reliance": [],
                "decision_accuracy": [],
                "agreement_rate": [],
            },
            "losses": [],
            "epochs": [],
        },
        "challenging": {
            "metrics": {
                "appropriate_reliance": [],
                "decision_accuracy": [],
                "agreement_rate": [],
            },
            "losses": [],
            "epochs": [],
        },
        "adaptive": {
            "metrics": {
                "appropriate_reliance": [],
                "decision_accuracy": [],
                "agreement_rate": [],
            },
            "losses": [],
            "epochs": [],
        },
    },
}


# Generate synthetic dataset
def generate_decision_task_data(n_samples=2000, n_features=20):
    X = np.random.randn(n_samples, n_features).astype(np.float32)
    weights = np.random.randn(n_features)
    logits = X @ weights + np.random.randn(n_samples) * 0.5
    y_true = (logits > 0).astype(np.float32)
    task_complexity = np.abs(logits) / (np.abs(logits).max())
    task_complexity = 1 - task_complexity
    return X, y_true, task_complexity


# Human decision model with cognitive load control
class HumanDecisionModel(nn.Module):
    def __init__(self, input_dim=20, hidden_dim=64, use_cognitive_load=True):
        super(HumanDecisionModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)
        self.dropout = nn.Dropout(0.3)
        self.use_cognitive_load = use_cognitive_load

    def forward(self, x, cognitive_load=None):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))

        # Apply cognitive load noise only if enabled
        if self.use_cognitive_load and cognitive_load is not None and self.training:
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

X_train_t = torch.FloatTensor(X_train).to(device)
y_train_t = torch.FloatTensor(y_train).to(device)
complexity_train_t = torch.FloatTensor(complexity_train).to(device)
X_test_t = torch.FloatTensor(X_test).to(device)
y_test_t = torch.FloatTensor(y_test).to(device)
complexity_test_t = torch.FloatTensor(complexity_test).to(device)

# Train AI assistant model
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
            test_acc = ((torch.sigmoid(test_logits) > 0.5) == y_test_t).float().mean()
            print(f"AI Assistant Epoch {epoch+1}: test_acc={test_acc.item():.4f}")


# Simulation function with cognitive load control
def simulate_interaction(
    human_model,
    ai_model,
    X,
    y_true,
    cognitive_load,
    interaction_mode,
    adaptive_threshold=0.6,
    use_cognitive_load=True,
):
    human_model.eval()
    ai_model.eval()

    with torch.no_grad():
        # Pass cognitive load only if enabled
        cl = cognitive_load if use_cognitive_load else None
        human_logits = human_model(X, cl).squeeze()
        human_initial = torch.sigmoid(human_logits) > 0.5
        human_confidence = torch.abs(torch.sigmoid(human_logits) - 0.5) * 2

        ai_logits = ai_model(X).squeeze()
        ai_recommendation = torch.sigmoid(ai_logits) > 0.5
        ai_correct = ai_recommendation == y_true

        if interaction_mode == "supportive":
            ai_challenges = torch.zeros_like(human_initial, dtype=torch.bool)
        elif interaction_mode == "challenging":
            ai_challenges = ai_recommendation != human_initial
        else:  # adaptive
            # If cognitive load is disabled, adaptive mode uses a different criterion
            if use_cognitive_load:
                high_cognitive_load = cognitive_load > adaptive_threshold
                ai_challenges = (ai_recommendation != human_initial) & (
                    ~high_cognitive_load
                )
            else:
                # Without cognitive load, adaptive becomes similar to challenging
                ai_challenges = ai_recommendation != human_initial

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


# Training and evaluation
print("\n" + "=" * 80)
print("ABLATION STUDY: WITH vs WITHOUT Cognitive Load")
print("=" * 80)

modes = ["supportive", "challenging", "adaptive"]
n_epochs = 100
ablation_conditions = [("with_cognitive_load", True), ("without_cognitive_load", False)]

for ablation_name, use_cognitive_load in ablation_conditions:
    print(f"\n{'='*80}")
    print(f"ABLATION: {ablation_name.upper().replace('_', ' ')}")
    print(f"{'='*80}")

    for mode in modes:
        print(f"\n{'-'*80}")
        print(f"Training with {mode.upper()} AI interaction mode")
        print(f"{'-'*80}")

        human_model = HumanDecisionModel(
            input_dim=20, hidden_dim=64, use_cognitive_load=use_cognitive_load
        ).to(device)
        human_optimizer = optim.Adam(human_model.parameters(), lr=0.001)
        human_criterion = nn.BCEWithLogitsLoss()

        for epoch in range(n_epochs):
            human_model.train()
            human_optimizer.zero_grad()

            # Pass cognitive load to training only if enabled
            cl = complexity_train_t if use_cognitive_load else None
            train_logits = human_model(X_train_t, cl).squeeze()
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
                    adaptive_threshold=0.6,
                    use_cognitive_load=use_cognitive_load,
                )

                human_model.eval()
                with torch.no_grad():
                    cl_val = complexity_test_t if use_cognitive_load else None
                    val_logits = human_model(X_test_t, cl_val).squeeze()
                    val_loss = human_criterion(val_logits, y_test_t)

                experiment_data[ablation_name][mode]["epochs"].append(epoch + 1)
                experiment_data[ablation_name][mode]["losses"].append(val_loss.item())
                experiment_data[ablation_name][mode]["metrics"][
                    "appropriate_reliance"
                ].append(test_results["appropriate_reliance"])
                experiment_data[ablation_name][mode]["metrics"][
                    "decision_accuracy"
                ].append(test_results["decision_accuracy"])
                experiment_data[ablation_name][mode]["metrics"][
                    "agreement_rate"
                ].append(test_results["agreement_rate"])

                print(
                    f"Epoch {epoch+1}: val_loss={val_loss.item():.4f}, "
                    f"appropriate_reliance={test_results['appropriate_reliance']:.4f}, "
                    f"decision_accuracy={test_results['decision_accuracy']:.4f}, "
                    f"agreement_rate={test_results['agreement_rate']:.4f}"
                )

# Final comparison
print("\n" + "=" * 80)
print("FINAL RESULTS COMPARISON")
print("=" * 80)

for ablation_name, _ in ablation_conditions:
    print(f"\n{ablation_name.upper().replace('_', ' ')}:")
    for mode in modes:
        ar = experiment_data[ablation_name][mode]["metrics"]["appropriate_reliance"][-1]
        da = experiment_data[ablation_name][mode]["metrics"]["decision_accuracy"][-1]
        agr = experiment_data[ablation_name][mode]["metrics"]["agreement_rate"][-1]
        print(f"  {mode.capitalize()}: AR={ar:.4f}, DA={da:.4f}, AGR={agr:.4f}")

# Visualizations
print("\nGenerating visualizations...")

# Plot 1: Appropriate Reliance comparison across ablations
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for idx, (ablation_name, _) in enumerate(ablation_conditions):
    ax = axes[idx]
    for mode in modes:
        ax.plot(
            experiment_data[ablation_name][mode]["epochs"],
            experiment_data[ablation_name][mode]["metrics"]["appropriate_reliance"],
            marker="o",
            label=mode.capitalize(),
            linewidth=2,
        )
    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Appropriate Reliance Score", fontsize=12)
    ax.set_title(
        f"{ablation_name.replace('_', ' ').title()}", fontsize=13, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_appropriate_reliance.png"), dpi=300)
plt.close()

# Plot 2: Decision Accuracy comparison
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
for idx, (ablation_name, _) in enumerate(ablation_conditions):
    ax = axes[idx]
    for mode in modes:
        ax.plot(
            experiment_data[ablation_name][mode]["epochs"],
            experiment_data[ablation_name][mode]["metrics"]["decision_accuracy"],
            marker="s",
            label=mode.capitalize(),
            linewidth=2,
        )
    ax.set_xlabel("Epoch", fontsize=12)
    ax.set_ylabel("Decision Accuracy", fontsize=12)
    ax.set_title(
        f"{ablation_name.replace('_', ' ').title()}", fontsize=13, fontweight="bold"
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_decision_accuracy.png"), dpi=300)
plt.close()

# Plot 3: Bar chart comparing final metrics across ablations
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
metrics = ["appropriate_reliance", "decision_accuracy", "agreement_rate"]
metric_labels = ["Appropriate Reliance", "Decision Accuracy", "Agreement Rate"]

for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
    x = np.arange(len(modes))
    width = 0.35

    with_cl = [
        experiment_data["with_cognitive_load"][mode]["metrics"][metric][-1]
        for mode in modes
    ]
    without_cl = [
        experiment_data["without_cognitive_load"][mode]["metrics"][metric][-1]
        for mode in modes
    ]

    bars1 = axes[idx].bar(
        x - width / 2,
        with_cl,
        width,
        label="With Cognitive Load",
        alpha=0.8,
        color="#3498db",
    )
    bars2 = axes[idx].bar(
        x + width / 2,
        without_cl,
        width,
        label="Without Cognitive Load",
        alpha=0.8,
        color="#e74c3c",
    )

    axes[idx].set_ylabel(label, fontsize=11)
    axes[idx].set_title(label, fontsize=12, fontweight="bold")
    axes[idx].set_xticks(x)
    axes[idx].set_xticklabels([m.capitalize() for m in modes])
    axes[idx].legend(fontsize=9)
    axes[idx].grid(True, alpha=0.3, axis="y")
    axes[idx].set_ylim([0, 1])

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            axes[idx].text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height:.3f}",
                ha="center",
                va="bottom",
                fontsize=9,
            )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_final_comparison.png"), dpi=300)
plt.close()

# Plot 4: Direct difference visualization
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
    differences = []
    for mode in modes:
        with_cl = experiment_data["with_cognitive_load"][mode]["metrics"][metric][-1]
        without_cl = experiment_data["without_cognitive_load"][mode]["metrics"][metric][
            -1
        ]
        diff = with_cl - without_cl
        differences.append(diff)

    colors = ["#2ecc71" if d > 0 else "#e74c3c" for d in differences]
    bars = axes[idx].bar(modes, differences, color=colors, alpha=0.8)
    axes[idx].axhline(y=0, color="black", linestyle="-", linewidth=0.8)
    axes[idx].set_ylabel(f"{label} Difference", fontsize=11)
    axes[idx].set_title(
        f"{label}\n(With CL - Without CL)", fontsize=12, fontweight="bold"
    )
    axes[idx].grid(True, alpha=0.3, axis="y")

    for bar in bars:
        height = bar.get_height()
        axes[idx].text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{height:+.3f}",
            ha="center",
            va="bottom" if height > 0 else "top",
            fontsize=10,
        )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_differences.png"), dpi=300)
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(
    f"\nAll experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}"
)

print("\n" + "=" * 80)
print("ABLATION STUDY COMPLETE")
print("=" * 80)
print(f"Visualizations saved to: {working_dir}")
print("Generated plots:")
print("  - ablation_appropriate_reliance.png")
print("  - ablation_decision_accuracy.png")
print("  - ablation_final_comparison.png")
print("  - ablation_differences.png")
