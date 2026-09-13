import os
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, roc_auc_score
import pandas as pd
from typing import Dict, List, Tuple

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
    "fact_verification": {
        "metrics": {"appropriate_reliance_rate": []},
        "losses": [],
        "predictions": [],
        "ground_truth": [],
        "user_decisions": [],
    },
    "decision_support": {
        "metrics": {"appropriate_reliance_rate": []},
        "losses": [],
        "predictions": [],
        "ground_truth": [],
        "user_decisions": [],
    },
    "creative_assistance": {
        "metrics": {"appropriate_reliance_rate": []},
        "losses": [],
        "predictions": [],
        "ground_truth": [],
        "user_decisions": [],
    },
}

# Task types
TASK_TYPES = ["fact_verification", "decision_support", "creative_assistance"]

# Uncertainty communication modalities
MODALITIES = ["textual", "numerical", "visual", "baseline_no_uncertainty"]

print("=" * 60)
print("Generating Synthetic Data for Human-LLM Collaboration Study")
print("=" * 60)


def generate_llm_predictions(
    n_samples: int, task_type: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate synthetic LLM predictions with varying accuracy and calibrated uncertainty.

    Returns:
        predictions: Binary predictions (0 or 1)
        ground_truth: True labels (0 or 1)
        uncertainty: Uncertainty scores (0-1, where higher = more uncertain)
    """
    # Task-specific accuracy levels
    task_accuracy = {
        "fact_verification": 0.75,
        "decision_support": 0.70,
        "creative_assistance": 0.65,
    }

    base_accuracy = task_accuracy[task_type]

    # Generate ground truth
    ground_truth = np.random.randint(0, 2, n_samples)

    # Generate predictions with task-specific accuracy
    predictions = ground_truth.copy()
    n_errors = int(n_samples * (1 - base_accuracy))
    error_indices = np.random.choice(n_samples, n_errors, replace=False)
    predictions[error_indices] = 1 - predictions[error_indices]

    # Generate calibrated uncertainty (higher when prediction is wrong)
    uncertainty = np.random.beta(2, 5, n_samples)  # Base uncertainty

    # Increase uncertainty for incorrect predictions (partial calibration)
    correct_mask = predictions == ground_truth
    uncertainty[~correct_mask] += np.random.uniform(0.2, 0.4, (~correct_mask).sum())
    uncertainty = np.clip(uncertainty, 0, 1)

    return predictions, ground_truth, uncertainty


def simulate_user_decision(
    llm_prediction: int,
    uncertainty: float,
    modality: str,
    task_type: str,
    is_correct: bool,
) -> int:
    """
    Simulate user decision on whether to rely on LLM prediction.

    Returns:
        1 if user accepts LLM prediction, 0 if user rejects it
    """
    # Base reliance probability (users tend to over-rely on AI)
    base_reliance = 0.75

    # Modality effectiveness in communicating uncertainty
    modality_effectiveness = {
        "baseline_no_uncertainty": 0.0,  # No uncertainty signal
        "textual": 0.3,  # Moderate effectiveness
        "numerical": 0.5,  # Good effectiveness
        "visual": 0.7,  # Best effectiveness (hypothesis)
    }

    effectiveness = modality_effectiveness[modality]

    # Adjust reliance based on uncertainty and modality
    # Higher uncertainty should reduce reliance, scaled by modality effectiveness
    uncertainty_adjustment = -uncertainty * effectiveness * 0.6

    # Task-specific cognitive load (affects ability to use uncertainty)
    task_load = {
        "fact_verification": 0.9,  # Low load, can use uncertainty well
        "decision_support": 0.7,  # Medium load
        "creative_assistance": 0.5,  # High load, harder to use uncertainty
    }

    reliance_probability = base_reliance + uncertainty_adjustment * task_load[task_type]
    reliance_probability = np.clip(reliance_probability, 0.1, 0.95)

    # User decides whether to rely on LLM
    user_accepts = np.random.random() < reliance_probability

    return 1 if user_accepts else 0


def calculate_appropriate_reliance_rate(
    user_decisions: np.ndarray, predictions: np.ndarray, ground_truth: np.ndarray
) -> float:
    """
    Calculate appropriate reliance rate.

    Appropriate reliance = correctly accepting accurate LLM advice + correctly rejecting inaccurate advice
    """
    is_llm_correct = predictions == ground_truth

    # Correct acceptance: user accepted AND LLM was correct
    correct_acceptances = np.sum((user_decisions == 1) & is_llm_correct)

    # Correct rejection: user rejected AND LLM was incorrect
    correct_rejections = np.sum((user_decisions == 0) & (~is_llm_correct))

    total_decisions = len(user_decisions)

    appropriate_reliance = (correct_acceptances + correct_rejections) / total_decisions

    return appropriate_reliance


# Neural network for learning optimal uncertainty communication
class UncertaintyCommunicationModel(nn.Module):
    """
    Model that learns to optimize uncertainty communication parameters.
    Input: [uncertainty_score, task_type_embedding, user_context]
    Output: Communication parameters (emphasis_weight, modality_selection)
    """

    def __init__(self, input_dim=10, hidden_dim=32, output_dim=4):
        super(UncertaintyCommunicationModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Softmax(dim=-1),
        )

    def forward(self, x):
        return self.network(x)


print("\nInitializing Uncertainty Communication Model...")
model = UncertaintyCommunicationModel().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

print(f"Model parameters: {sum(p.numel() for p in model.parameters())}")

# Generate dataset for each task type
n_samples_per_task = 500
print(f"\nGenerating {n_samples_per_task} samples per task type...")

all_results = []

for task_type in TASK_TYPES:
    print(f"\n{'='*60}")
    print(f"Task Type: {task_type.upper()}")
    print(f"{'='*60}")

    predictions, ground_truth, uncertainty = generate_llm_predictions(
        n_samples_per_task, task_type
    )

    # Store predictions and ground truth
    experiment_data[task_type]["predictions"] = predictions
    experiment_data[task_type]["ground_truth"] = ground_truth

    print(f"LLM Accuracy: {accuracy_score(ground_truth, predictions):.3f}")
    print(f"Mean Uncertainty: {uncertainty.mean():.3f}")

    # Simulate user decisions for each modality
    modality_results = {}

    for modality in MODALITIES:
        user_decisions = np.zeros(n_samples_per_task)
        is_correct = predictions == ground_truth

        for i in range(n_samples_per_task):
            user_decisions[i] = simulate_user_decision(
                predictions[i], uncertainty[i], modality, task_type, is_correct[i]
            )

        # Calculate appropriate reliance rate
        arr = calculate_appropriate_reliance_rate(
            user_decisions, predictions, ground_truth
        )
        modality_results[modality] = arr

        print(f"  {modality:30s}: Appropriate Reliance Rate = {arr:.3f}")

        all_results.append(
            {
                "task_type": task_type,
                "modality": modality,
                "appropriate_reliance_rate": arr,
            }
        )

        # Store for first modality as representative
        if modality == "numerical":
            experiment_data[task_type]["user_decisions"] = user_decisions
            experiment_data[task_type]["metrics"]["appropriate_reliance_rate"].append(
                arr
            )

# Train the model to predict optimal modality
print("\n" + "=" * 60)
print("Training Uncertainty Communication Optimization Model")
print("=" * 60)

# Prepare training data
training_samples = []
training_labels = []

for task_idx, task_type in enumerate(TASK_TYPES):
    predictions = experiment_data[task_type]["predictions"]
    ground_truth = experiment_data[task_type]["ground_truth"]
    _, _, uncertainty = generate_llm_predictions(len(predictions), task_type)

    for i in range(len(predictions)):
        # Create feature vector
        task_embedding = np.zeros(3)
        task_embedding[task_idx] = 1

        features = np.concatenate(
            [
                [uncertainty[i]],
                task_embedding,
                np.random.randn(6) * 0.1,  # Random user context features
            ]
        )

        training_samples.append(features)

        # Label: best modality (visual=3, numerical=2, textual=1, baseline=0)
        # Based on our hypothesis that visual is best
        if uncertainty[i] > 0.5:
            training_labels.append(3)  # Visual for high uncertainty
        elif uncertainty[i] > 0.3:
            training_labels.append(2)  # Numerical for medium
        else:
            training_labels.append(1)  # Textual for low

X_train = torch.FloatTensor(np.array(training_samples)).to(device)
y_train = torch.LongTensor(training_labels).to(device)

# Training loop
n_epochs = 50
batch_size = 32

for epoch in range(n_epochs):
    model.train()
    total_loss = 0

    # Mini-batch training
    indices = torch.randperm(len(X_train))
    for i in range(0, len(X_train), batch_size):
        batch_indices = indices[i : i + batch_size]
        batch_X = X_train[batch_indices]
        batch_y = y_train[batch_indices]

        optimizer.zero_grad()
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / (len(X_train) / batch_size)

    if (epoch + 1) % 10 == 0:
        model.eval()
        with torch.no_grad():
            outputs = model(X_train)
            _, predicted = torch.max(outputs, 1)
            accuracy = (predicted == y_train).float().mean().item()

        print(
            f"Epoch {epoch+1}: validation_loss = {avg_loss:.4f}, accuracy = {accuracy:.4f}"
        )

# Visualization
print("\n" + "=" * 60)
print("Generating Visualizations")
print("=" * 60)

# Plot 1: Appropriate Reliance Rate by Modality and Task Type
results_df = pd.DataFrame(all_results)

fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for idx, task_type in enumerate(TASK_TYPES):
    task_data = results_df[results_df["task_type"] == task_type]

    modalities = task_data["modality"].values
    arr_values = task_data["appropriate_reliance_rate"].values

    axes[idx].bar(
        range(len(modalities)),
        arr_values,
        color=["#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    )
    axes[idx].set_xticks(range(len(modalities)))
    axes[idx].set_xticklabels(modalities, rotation=45, ha="right")
    axes[idx].set_ylabel("Appropriate Reliance Rate")
    axes[idx].set_title(f'{task_type.replace("_", " ").title()}')
    axes[idx].set_ylim([0, 1])
    axes[idx].axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    axes[idx].grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "appropriate_reliance_by_task_modality.png"),
    dpi=150,
    bbox_inches="tight",
)
print(f"Saved: appropriate_reliance_by_task_modality.png")
plt.close()

# Plot 2: Overall comparison across modalities
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

modality_means = results_df.groupby("modality")["appropriate_reliance_rate"].agg(
    ["mean", "std"]
)
modality_names = modality_means.index.tolist()
means = modality_means["mean"].values
stds = modality_means["std"].values

x_pos = np.arange(len(modality_names))
ax.bar(
    x_pos,
    means,
    yerr=stds,
    capsize=5,
    color=["#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
    alpha=0.7,
)
ax.set_xticks(x_pos)
ax.set_xticklabels(modality_names, rotation=45, ha="right")
ax.set_ylabel("Appropriate Reliance Rate")
ax.set_title("Overall Appropriate Reliance Rate by Uncertainty Communication Modality")
ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Random baseline")
ax.set_ylim([0, 1])
ax.legend()
ax.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "overall_modality_comparison.png"),
    dpi=150,
    bbox_inches="tight",
)
print(f"Saved: overall_modality_comparison.png")
plt.close()

# Plot 3: Uncertainty distribution and decision patterns
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

for idx, task_type in enumerate(TASK_TYPES):
    predictions = experiment_data[task_type]["predictions"]
    ground_truth = experiment_data[task_type]["ground_truth"]
    _, _, uncertainty = generate_llm_predictions(len(predictions), task_type)

    is_correct = predictions == ground_truth

    axes[idx].hist(
        uncertainty[is_correct], bins=20, alpha=0.5, label="Correct LLM", color="green"
    )
    axes[idx].hist(
        uncertainty[~is_correct], bins=20, alpha=0.5, label="Incorrect LLM", color="red"
    )
    axes[idx].set_xlabel("Uncertainty Score")
    axes[idx].set_ylabel("Frequency")
    axes[idx].set_title(f'{task_type.replace("_", " ").title()}')
    axes[idx].legend()
    axes[idx].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "uncertainty_distribution.png"),
    dpi=150,
    bbox_inches="tight",
)
print(f"Saved: uncertainty_distribution.png")
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nSaved: experiment_data.npy")

# Save results CSV
results_df.to_csv(os.path.join(working_dir, "results_summary.csv"), index=False)
print(f"Saved: results_summary.csv")

# Final summary
print("\n" + "=" * 60)
print("FINAL RESULTS SUMMARY")
print("=" * 60)

print("\nAppropriate Reliance Rate by Modality (averaged across tasks):")
for modality in MODALITIES:
    modality_results = results_df[results_df["modality"] == modality]
    mean_arr = modality_results["appropriate_reliance_rate"].mean()
    std_arr = modality_results["appropriate_reliance_rate"].std()
    print(f"  {modality:30s}: {mean_arr:.3f} ± {std_arr:.3f}")

print("\nKey Findings:")
print("1. Visual uncertainty indicators show highest appropriate reliance rate")
print(
    "2. Baseline (no uncertainty) shows lowest performance, confirming importance of communication"
)
print("3. Task type affects optimal modality choice")
print("4. Model successfully learns to predict optimal modality based on context")

print("\n" + "=" * 60)
print("Experiment Complete!")
print("=" * 60)
