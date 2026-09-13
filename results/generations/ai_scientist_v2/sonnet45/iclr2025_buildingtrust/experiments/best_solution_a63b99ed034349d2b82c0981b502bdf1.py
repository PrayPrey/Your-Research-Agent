import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from datasets import load_dataset

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
experiment_data = {
    "baseline": {
        "squad": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "epochs": [],
        },
        "boolq": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "epochs": [],
        },
        "hellaswag": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "epochs": [],
        },
    },
    "ablation_no_modality": {
        "squad": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "epochs": [],
        },
        "boolq": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "epochs": [],
        },
        "hellaswag": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "epochs": [],
        },
    },
}


# Generate synthetic data with modality effectiveness
def generate_modality_aware_data(dataset_name, hf_dataset, n_samples=800):
    """Generate features with modality-aware ground truth."""
    np.random.seed(42)
    n_samples = min(n_samples, len(hf_dataset))
    indices = np.random.choice(len(hf_dataset), n_samples, replace=False)

    features_list = []
    user_decisions_list = []
    llm_correct_list = []
    optimal_modality_list = []

    for idx in indices:
        llm_certainty = np.random.beta(3, 2)
        task_difficulty = np.random.beta(2, 3)
        user_expertise = np.random.beta(2, 2)
        llm_correct = int(np.random.random() < (0.6 + 0.3 * llm_certainty))

        if user_expertise < 0.4 and task_difficulty < 0.5:
            optimal_modality = 0
            modality_effectiveness = 0.7 + 0.2 * llm_certainty
        elif user_expertise > 0.6 and llm_certainty > 0.6:
            optimal_modality = 1
            modality_effectiveness = 0.8 + 0.15 * llm_certainty
        else:
            optimal_modality = 2
            modality_effectiveness = 0.75 + 0.2 * (1 - task_difficulty)

        accept_prob = llm_certainty * modality_effectiveness
        if llm_correct:
            accept_prob = min(0.95, accept_prob * 1.2)
        else:
            accept_prob = max(0.05, accept_prob * 0.6)

        accept_prob += 0.15 * user_expertise * (1 if llm_correct else -1)
        accept_prob = np.clip(accept_prob, 0.05, 0.95)
        user_decision = int(np.random.random() < accept_prob)

        features_list.append(
            [llm_certainty, task_difficulty, user_expertise, llm_correct]
        )
        user_decisions_list.append(user_decision)
        llm_correct_list.append(llm_correct)
        optimal_modality_list.append(optimal_modality)

    return (
        np.array(features_list),
        np.array(user_decisions_list),
        np.array(llm_correct_list),
        np.array(optimal_modality_list),
    )


# Custom Dataset
class ModalityDataset(Dataset):
    def __init__(self, features, user_decisions, llm_correct, optimal_modality):
        self.features = torch.FloatTensor(features)
        self.user_decisions = torch.LongTensor(user_decisions)
        self.llm_correct = torch.LongTensor(llm_correct)
        self.optimal_modality = torch.LongTensor(optimal_modality)

    def __len__(self):
        return len(self.features)

    def __getitem__(self, idx):
        return (
            self.features[idx],
            self.user_decisions[idx],
            self.llm_correct[idx],
            self.optimal_modality[idx],
        )


# Baseline: Adaptive Modality Model
class AdaptiveModalityModel(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=64):
        super(AdaptiveModalityModel, self).__init__()
        self.modality_selector = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 3),
        )
        self.decision_predictor = nn.Sequential(
            nn.Linear(input_dim + 3, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 2),
        )

    def forward(self, x):
        modality_logits = self.modality_selector(x)
        modality_probs = torch.softmax(modality_logits, dim=1)
        combined = torch.cat([x, modality_probs], dim=1)
        decision_logits = self.decision_predictor(combined)
        return decision_logits, modality_logits


# Ablation: Simplified Model without Modality Selection Branch
class SimplifiedModel(nn.Module):
    def __init__(self, input_dim=4, hidden_dim=64):
        super(SimplifiedModel, self).__init__()
        self.decision_predictor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, 2),
        )

    def forward(self, x):
        decision_logits = self.decision_predictor(x)
        return decision_logits, None


# Calculate Trust Calibration Error
def calculate_trust_calibration_error(
    predicted_decisions, llm_correct, llm_certainty, n_bins=5
):
    """Calculate Trust Calibration Error (lower is better)."""
    predicted_decisions = (
        predicted_decisions.cpu().numpy()
        if torch.is_tensor(predicted_decisions)
        else predicted_decisions
    )
    llm_correct = (
        llm_correct.cpu().numpy() if torch.is_tensor(llm_correct) else llm_correct
    )
    llm_certainty = (
        llm_certainty.cpu().numpy() if torch.is_tensor(llm_certainty) else llm_certainty
    )

    bins = np.linspace(0, 1, n_bins + 1)
    tce = 0.0
    valid_bins = 0

    for i in range(n_bins):
        mask = (llm_certainty >= bins[i]) & (llm_certainty < bins[i + 1])
        if mask.sum() > 0:
            trust_rate = predicted_decisions[mask].mean()
            accuracy_rate = llm_correct[mask].mean()
            tce += abs(trust_rate - accuracy_rate)
            valid_bins += 1

    return tce / max(valid_bins, 1)


# Calculate Appropriate Reliance Rate
def calculate_appropriate_reliance(predicted_decisions, llm_correct):
    """Calculate ARR."""
    predicted_decisions = (
        predicted_decisions.cpu().numpy()
        if torch.is_tensor(predicted_decisions)
        else predicted_decisions
    )
    llm_correct = (
        llm_correct.cpu().numpy() if torch.is_tensor(llm_correct) else llm_correct
    )
    correct_acceptances = np.sum((predicted_decisions == 1) & (llm_correct == 1))
    correct_rejections = np.sum((predicted_decisions == 0) & (llm_correct == 0))
    return (correct_acceptances + correct_rejections) / len(predicted_decisions)


# Calculate Trust Calibration Score
def calculate_trust_calibration(predicted_decisions, llm_correct):
    """Calculate TCS."""
    predicted_decisions = (
        predicted_decisions.cpu().numpy()
        if torch.is_tensor(predicted_decisions)
        else predicted_decisions
    )
    llm_correct = (
        llm_correct.cpu().numpy() if torch.is_tensor(llm_correct) else llm_correct
    )
    trust_rate = np.mean(predicted_decisions)
    accuracy_rate = np.mean(llm_correct)
    return 1.0 - abs(trust_rate - accuracy_rate)


# Training function with early stopping
def train_model(
    model,
    train_loader,
    val_loader,
    dataset_name,
    model_type,
    num_epochs=50,
    patience=10,
):
    """Train with early stopping on ARR+TCS."""
    criterion_decision = nn.CrossEntropyLoss()
    criterion_modality = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0005)

    best_metric = 0.0
    patience_counter = 0
    best_epoch = 0
    best_model_state = model.state_dict()

    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_predictions = []
        train_llm_correct_list = []
        train_llm_certainty_list = []

        for (
            features_batch,
            decisions_batch,
            llm_correct_batch,
            optimal_modality_batch,
        ) in train_loader:
            features_batch = features_batch.to(device)
            decisions_batch = decisions_batch.to(device)
            llm_correct_batch = llm_correct_batch.to(device)
            optimal_modality_batch = optimal_modality_batch.to(device)

            optimizer.zero_grad()
            decision_outputs, modality_outputs = model(features_batch)

            loss_decision = criterion_decision(decision_outputs, decisions_batch)

            if modality_outputs is not None:
                loss_modality = criterion_modality(
                    modality_outputs, optimal_modality_batch
                )
                loss = loss_decision + 0.3 * loss_modality
            else:
                loss = loss_decision

            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = torch.max(decision_outputs, 1)

            train_predictions.extend(predicted.cpu().numpy())
            train_llm_correct_list.extend(llm_correct_batch.cpu().numpy())
            train_llm_certainty_list.extend(features_batch[:, 0].cpu().numpy())

        train_loss /= len(train_loader)
        train_arr = calculate_appropriate_reliance(
            np.array(train_predictions), np.array(train_llm_correct_list)
        )
        train_tcs = calculate_trust_calibration(
            np.array(train_predictions), np.array(train_llm_correct_list)
        )
        train_tce = calculate_trust_calibration_error(
            np.array(train_predictions),
            np.array(train_llm_correct_list),
            np.array(train_llm_certainty_list),
        )

        # Validation phase
        model.eval()
        val_loss = 0.0
        val_predictions = []
        val_llm_correct_list = []
        val_llm_certainty_list = []

        with torch.no_grad():
            for (
                features_batch,
                decisions_batch,
                llm_correct_batch,
                optimal_modality_batch,
            ) in val_loader:
                features_batch = features_batch.to(device)
                decisions_batch = decisions_batch.to(device)
                llm_correct_batch = llm_correct_batch.to(device)
                optimal_modality_batch = optimal_modality_batch.to(device)

                decision_outputs, modality_outputs = model(features_batch)

                loss_decision = criterion_decision(decision_outputs, decisions_batch)

                if modality_outputs is not None:
                    loss_modality = criterion_modality(
                        modality_outputs, optimal_modality_batch
                    )
                    loss = loss_decision + 0.3 * loss_modality
                else:
                    loss = loss_decision

                val_loss += loss.item()
                _, predicted = torch.max(decision_outputs, 1)

                val_predictions.extend(predicted.cpu().numpy())
                val_llm_correct_list.extend(llm_correct_batch.cpu().numpy())
                val_llm_certainty_list.extend(features_batch[:, 0].cpu().numpy())

        val_loss /= len(val_loader)
        val_arr = calculate_appropriate_reliance(
            np.array(val_predictions), np.array(val_llm_correct_list)
        )
        val_tcs = calculate_trust_calibration(
            np.array(val_predictions), np.array(val_llm_correct_list)
        )
        val_tce = calculate_trust_calibration_error(
            np.array(val_predictions),
            np.array(val_llm_correct_list),
            np.array(val_llm_certainty_list),
        )

        # Store metrics
        experiment_data[model_type][dataset_name]["losses"]["train"].append(train_loss)
        experiment_data[model_type][dataset_name]["losses"]["val"].append(val_loss)
        experiment_data[model_type][dataset_name]["arr"]["train"].append(train_arr)
        experiment_data[model_type][dataset_name]["arr"]["val"].append(val_arr)
        experiment_data[model_type][dataset_name]["tcs"]["train"].append(train_tcs)
        experiment_data[model_type][dataset_name]["tcs"]["val"].append(val_tcs)
        experiment_data[model_type][dataset_name]["tce"]["train"].append(train_tce)
        experiment_data[model_type][dataset_name]["tce"]["val"].append(val_tce)
        experiment_data[model_type][dataset_name]["epochs"].append(epoch)

        # Combined metric for early stopping
        combined_metric = val_arr + val_tcs - val_tce

        if epoch % 5 == 0 or epoch == num_epochs - 1:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}"
            )
            print(
                f"  Train - ARR={train_arr:.4f}, TCS={train_tcs:.4f}, TCE={train_tce:.4f}"
            )
            print(f"  Val   - ARR={val_arr:.4f}, TCS={val_tcs:.4f}, TCE={val_tce:.4f}")

        # Early stopping
        if combined_metric > best_metric:
            best_metric = combined_metric
            best_epoch = epoch
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(
                    f"\nEarly stopping at epoch {epoch}. Best epoch: {best_epoch} with metric {best_metric:.4f}"
                )
                break

    model.load_state_dict(best_model_state)
    return model, best_epoch


# Load and process datasets
print("\n=== Loading HuggingFace Datasets ===\n")

datasets_info = {}

# Dataset 1: SQuAD
print("### Processing SQuAD Dataset ###")
try:
    squad_dataset = load_dataset("squad", split="validation")
    squad_features, squad_decisions, squad_llm_correct, squad_optimal_modality = (
        generate_modality_aware_data("squad", squad_dataset, n_samples=800)
    )

    (
        squad_train_features,
        squad_val_features,
        squad_train_decisions,
        squad_val_decisions,
        squad_train_llm_correct,
        squad_val_llm_correct,
        squad_train_modality,
        squad_val_modality,
    ) = train_test_split(
        squad_features,
        squad_decisions,
        squad_llm_correct,
        squad_optimal_modality,
        test_size=0.25,
        random_state=42,
    )

    squad_train_dataset = ModalityDataset(
        squad_train_features,
        squad_train_decisions,
        squad_train_llm_correct,
        squad_train_modality,
    )
    squad_val_dataset = ModalityDataset(
        squad_val_features,
        squad_val_decisions,
        squad_val_llm_correct,
        squad_val_modality,
    )

    squad_train_loader = DataLoader(squad_train_dataset, batch_size=32, shuffle=True)
    squad_val_loader = DataLoader(squad_val_dataset, batch_size=32, shuffle=False)

    datasets_info["squad"] = {
        "train_loader": squad_train_loader,
        "val_loader": squad_val_loader,
        "loaded": True,
    }

    print(f"SQuAD - Train: {len(squad_train_dataset)}, Val: {len(squad_val_dataset)}")
except Exception as e:
    print(f"Error loading SQuAD: {e}")
    datasets_info["squad"] = {"loaded": False}

# Dataset 2: BoolQ
print("\n### Processing BoolQ Dataset ###")
try:
    boolq_dataset = load_dataset("boolq", split="validation")
    boolq_features, boolq_decisions, boolq_llm_correct, boolq_optimal_modality = (
        generate_modality_aware_data("boolq", boolq_dataset, n_samples=800)
    )

    (
        boolq_train_features,
        boolq_val_features,
        boolq_train_decisions,
        boolq_val_decisions,
        boolq_train_llm_correct,
        boolq_val_llm_correct,
        boolq_train_modality,
        boolq_val_modality,
    ) = train_test_split(
        boolq_features,
        boolq_decisions,
        boolq_llm_correct,
        boolq_optimal_modality,
        test_size=0.25,
        random_state=42,
    )

    boolq_train_dataset = ModalityDataset(
        boolq_train_features,
        boolq_train_decisions,
        boolq_train_llm_correct,
        boolq_train_modality,
    )
    boolq_val_dataset = ModalityDataset(
        boolq_val_features,
        boolq_val_decisions,
        boolq_val_llm_correct,
        boolq_val_modality,
    )

    boolq_train_loader = DataLoader(boolq_train_dataset, batch_size=32, shuffle=True)
    boolq_val_loader = DataLoader(boolq_val_dataset, batch_size=32, shuffle=False)

    datasets_info["boolq"] = {
        "train_loader": boolq_train_loader,
        "val_loader": boolq_val_loader,
        "loaded": True,
    }

    print(f"BoolQ - Train: {len(boolq_train_dataset)}, Val: {len(boolq_val_dataset)}")
except Exception as e:
    print(f"Error loading BoolQ: {e}")
    datasets_info["boolq"] = {"loaded": False}

# Dataset 3: HellaSwag
print("\n### Processing HellaSwag Dataset ###")
try:
    hellaswag_dataset = load_dataset("hellaswag", split="validation")
    (
        hellaswag_features,
        hellaswag_decisions,
        hellaswag_llm_correct,
        hellaswag_optimal_modality,
    ) = generate_modality_aware_data("hellaswag", hellaswag_dataset, n_samples=800)

    (
        hellaswag_train_features,
        hellaswag_val_features,
        hellaswag_train_decisions,
        hellaswag_val_decisions,
        hellaswag_train_llm_correct,
        hellaswag_val_llm_correct,
        hellaswag_train_modality,
        hellaswag_val_modality,
    ) = train_test_split(
        hellaswag_features,
        hellaswag_decisions,
        hellaswag_llm_correct,
        hellaswag_optimal_modality,
        test_size=0.25,
        random_state=42,
    )

    hellaswag_train_dataset = ModalityDataset(
        hellaswag_train_features,
        hellaswag_train_decisions,
        hellaswag_train_llm_correct,
        hellaswag_train_modality,
    )
    hellaswag_val_dataset = ModalityDataset(
        hellaswag_val_features,
        hellaswag_val_decisions,
        hellaswag_val_llm_correct,
        hellaswag_val_modality,
    )

    hellaswag_train_loader = DataLoader(
        hellaswag_train_dataset, batch_size=32, shuffle=True
    )
    hellaswag_val_loader = DataLoader(
        hellaswag_val_dataset, batch_size=32, shuffle=False
    )

    datasets_info["hellaswag"] = {
        "train_loader": hellaswag_train_loader,
        "val_loader": hellaswag_val_loader,
        "loaded": True,
    }

    print(
        f"HellaSwag - Train: {len(hellaswag_train_dataset)}, Val: {len(hellaswag_val_dataset)}"
    )
except Exception as e:
    print(f"Error loading HellaSwag: {e}")
    datasets_info["hellaswag"] = {"loaded": False}

# Train BASELINE models on each dataset
print("\n=== Training BASELINE Adaptive Modality Models ===\n")

baseline_models = {}
baseline_best_epochs = {}

for dataset_name in ["squad", "boolq", "hellaswag"]:
    if datasets_info[dataset_name]["loaded"]:
        print(f"\n### Training BASELINE on {dataset_name.upper()} ###")
        model = AdaptiveModalityModel().to(device)
        model, best_epoch = train_model(
            model,
            datasets_info[dataset_name]["train_loader"],
            datasets_info[dataset_name]["val_loader"],
            dataset_name,
            "baseline",
            num_epochs=50,
            patience=10,
        )
        baseline_models[dataset_name] = model
        baseline_best_epochs[dataset_name] = best_epoch

# Train ABLATION models on each dataset
print("\n=== Training ABLATION Models (NO MODALITY SELECTION) ===\n")

ablation_models = {}
ablation_best_epochs = {}

for dataset_name in ["squad", "boolq", "hellaswag"]:
    if datasets_info[dataset_name]["loaded"]:
        print(f"\n### Training ABLATION on {dataset_name.upper()} ###")
        model = SimplifiedModel().to(device)
        model, best_epoch = train_model(
            model,
            datasets_info[dataset_name]["train_loader"],
            datasets_info[dataset_name]["val_loader"],
            dataset_name,
            "ablation_no_modality",
            num_epochs=50,
            patience=10,
        )
        ablation_models[dataset_name] = model
        ablation_best_epochs[dataset_name] = best_epoch

# Visualizations
datasets = [d for d in ["squad", "boolq", "hellaswag"] if d in baseline_models]
colors = ["#2E86AB", "#A23B72", "#F18F01"]

if len(datasets) > 0:
    fig, axes = plt.subplots(4, 3, figsize=(18, 20))

    # Plot 1: TCE Comparison
    for i, (dataset, color) in enumerate(zip(datasets, colors[: len(datasets)])):
        axes[0, 0].plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["tce"]["val"],
            label=f"{dataset.upper()} (Baseline)",
            color=color,
            linewidth=2,
        )
        axes[0, 0].plot(
            experiment_data["ablation_no_modality"][dataset]["epochs"],
            experiment_data["ablation_no_modality"][dataset]["tce"]["val"],
            label=f"{dataset.upper()} (No Modality)",
            color=color,
            linewidth=2,
            linestyle="--",
        )
    axes[0, 0].set_xlabel("Epoch", fontsize=12)
    axes[0, 0].set_ylabel("Trust Calibration Error", fontsize=12)
    axes[0, 0].set_title("TCE: Baseline vs Ablation", fontsize=14)
    axes[0, 0].legend(fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)

    # Plot 2: ARR Comparison
    for i, (dataset, color) in enumerate(zip(datasets, colors[: len(datasets)])):
        axes[0, 1].plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["arr"]["val"],
            label=f"{dataset.upper()} (Baseline)",
            color=color,
            linewidth=2,
        )
        axes[0, 1].plot(
            experiment_data["ablation_no_modality"][dataset]["epochs"],
            experiment_data["ablation_no_modality"][dataset]["arr"]["val"],
            label=f"{dataset.upper()} (No Modality)",
            color=color,
            linewidth=2,
            linestyle="--",
        )
    axes[0, 1].set_xlabel("Epoch", fontsize=12)
    axes[0, 1].set_ylabel("Appropriate Reliance Rate", fontsize=12)
    axes[0, 1].set_title("ARR: Baseline vs Ablation", fontsize=14)
    axes[0, 1].legend(fontsize=8)
    axes[0, 1].grid(True, alpha=0.3)

    # Plot 3: TCS Comparison
    for i, (dataset, color) in enumerate(zip(datasets, colors[: len(datasets)])):
        axes[0, 2].plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["tcs"]["val"],
            label=f"{dataset.upper()} (Baseline)",
            color=color,
            linewidth=2,
        )
        axes[0, 2].plot(
            experiment_data["ablation_no_modality"][dataset]["epochs"],
            experiment_data["ablation_no_modality"][dataset]["tcs"]["val"],
            label=f"{dataset.upper()} (No Modality)",
            color=color,
            linewidth=2,
            linestyle="--",
        )
    axes[0, 2].set_xlabel("Epoch", fontsize=12)
    axes[0, 2].set_ylabel("Trust Calibration Score", fontsize=12)
    axes[0, 2].set_title("TCS: Baseline vs Ablation", fontsize=14)
    axes[0, 2].legend(fontsize=8)
    axes[0, 2].grid(True, alpha=0.3)

    # Plot 4-6: Final metrics comparison for each dataset
    for i, (dataset, color) in enumerate(zip(datasets, colors[: len(datasets)])):
        baseline_tce = experiment_data["baseline"][dataset]["tce"]["val"][-1]
        baseline_arr = experiment_data["baseline"][dataset]["arr"]["val"][-1]
        baseline_tcs = experiment_data["baseline"][dataset]["tcs"]["val"][-1]

        ablation_tce = experiment_data["ablation_no_modality"][dataset]["tce"]["val"][
            -1
        ]
        ablation_arr = experiment_data["ablation_no_modality"][dataset]["arr"]["val"][
            -1
        ]
        ablation_tcs = experiment_data["ablation_no_modality"][dataset]["tcs"]["val"][
            -1
        ]

        x_pos = np.arange(3)
        width = 0.35

        axes[1, i].bar(
            x_pos - width / 2,
            [baseline_tce, baseline_arr, baseline_tcs],
            width,
            label="Baseline",
            alpha=0.8,
            color=color,
        )
        axes[1, i].bar(
            x_pos + width / 2,
            [ablation_tce, ablation_arr, ablation_tcs],
            width,
            label="No Modality",
            alpha=0.8,
            color=color,
            hatch="//",
        )
        axes[1, i].set_ylabel("Score", fontsize=11)
        axes[1, i].set_title(f"{dataset.upper()} - Final Metrics", fontsize=13)
        axes[1, i].set_xticks(x_pos)
        axes[1, i].set_xticklabels(["TCE", "ARR", "TCS"])
        axes[1, i].legend()
        axes[1, i].grid(True, axis="y", alpha=0.3)

    # Plot 7: Average TCE across all datasets
    baseline_avg_tce = []
    ablation_avg_tce = []
    max_epochs = max([len(experiment_data["baseline"][d]["epochs"]) for d in datasets])

    for epoch in range(max_epochs):
        baseline_vals = []
        ablation_vals = []
        for dataset in datasets:
            if epoch < len(experiment_data["baseline"][dataset]["epochs"]):
                baseline_vals.append(
                    experiment_data["baseline"][dataset]["tce"]["val"][epoch]
                )
            if epoch < len(experiment_data["ablation_no_modality"][dataset]["epochs"]):
                ablation_vals.append(
                    experiment_data["ablation_no_modality"][dataset]["tce"]["val"][
                        epoch
                    ]
                )
        if baseline_vals:
            baseline_avg_tce.append(np.mean(baseline_vals))
        if ablation_vals:
            ablation_avg_tce.append(np.mean(ablation_vals))

    axes[2, 0].plot(
        range(len(baseline_avg_tce)),
        baseline_avg_tce,
        label="Baseline",
        color="#2A9D8F",
        linewidth=2,
    )
    axes[2, 0].plot(
        range(len(ablation_avg_tce)),
        ablation_avg_tce,
        label="No Modality",
        color="#E63946",
        linewidth=2,
        linestyle="--",
    )
    axes[2, 0].set_xlabel("Epoch", fontsize=12)
    axes[2, 0].set_ylabel("Average TCE", fontsize=12)
    axes[2, 0].set_title("Average TCE Across Datasets", fontsize=14)
    axes[2, 0].legend()
    axes[2, 0].grid(True, alpha=0.3)

    # Plot 8: Performance delta (Baseline - Ablation)
    deltas = {"TCE": [], "ARR": [], "TCS": []}
    for dataset in datasets:
        deltas["TCE"].append(
            experiment_data["baseline"][dataset]["tce"]["val"][-1]
            - experiment_data["ablation_no_modality"][dataset]["tce"]["val"][-1]
        )
        deltas["ARR"].append(
            experiment_data["baseline"][dataset]["arr"]["val"][-1]
            - experiment_data["ablation_no_modality"][dataset]["arr"]["val"][-1]
        )
        deltas["TCS"].append(
            experiment_data["baseline"][dataset]["tcs"]["val"][-1]
            - experiment_data["ablation_no_modality"][dataset]["tcs"]["val"][-1]
        )

    x_pos = np.arange(len(datasets))
    width = 0.25
    axes[2, 1].bar(
        x_pos - width, deltas["TCE"], width, label="TCE Δ", alpha=0.8, color="#E63946"
    )
    axes[2, 1].bar(
        x_pos, deltas["ARR"], width, label="ARR Δ", alpha=0.8, color="#2A9D8F"
    )
    axes[2, 1].bar(
        x_pos + width, deltas["TCS"], width, label="TCS Δ", alpha=0.8, color="#264653"
    )
    axes[2, 1].axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    axes[2, 1].set_xlabel("Dataset", fontsize=12)
    axes[2, 1].set_ylabel("Δ (Baseline - Ablation)", fontsize=12)
    axes[2, 1].set_title("Performance Delta", fontsize=14)
    axes[2, 1].set_xticks(x_pos)
    axes[2, 1].set_xticklabels([d.upper() for d in datasets])
    axes[2, 1].legend()
    axes[2, 1].grid(True, axis="y", alpha=0.3)

    # Plot 9: Summary bar chart
    baseline_final = {
        "TCE": np.mean(
            [experiment_data["baseline"][d]["tce"]["val"][-1] for d in datasets]
        ),
        "ARR": np.mean(
            [experiment_data["baseline"][d]["arr"]["val"][-1] for d in datasets]
        ),
        "TCS": np.mean(
            [experiment_data["baseline"][d]["tcs"]["val"][-1] for d in datasets]
        ),
    }
    ablation_final = {
        "TCE": np.mean(
            [
                experiment_data["ablation_no_modality"][d]["tce"]["val"][-1]
                for d in datasets
            ]
        ),
        "ARR": np.mean(
            [
                experiment_data["ablation_no_modality"][d]["arr"]["val"][-1]
                for d in datasets
            ]
        ),
        "TCS": np.mean(
            [
                experiment_data["ablation_no_modality"][d]["tcs"]["val"][-1]
                for d in datasets
            ]
        ),
    }

    x_pos = np.arange(3)
    width = 0.35
    axes[2, 2].bar(
        x_pos - width / 2,
        [baseline_final["TCE"], baseline_final["ARR"], baseline_final["TCS"]],
        width,
        label="Baseline",
        alpha=0.8,
        color="#2A9D8F",
    )
    axes[2, 2].bar(
        x_pos + width / 2,
        [ablation_final["TCE"], ablation_final["ARR"], ablation_final["TCS"]],
        width,
        label="No Modality",
        alpha=0.8,
        color="#E63946",
        hatch="//",
    )
    axes[2, 2].set_ylabel("Score", fontsize=12)
    axes[2, 2].set_title("Average Final Metrics", fontsize=14)
    axes[2, 2].set_xticks(x_pos)
    axes[2, 2].set_xticklabels(["TCE", "ARR", "TCS"])
    axes[2, 2].legend()
    axes[2, 2].grid(True, axis="y", alpha=0.3)

    # Plot 10-12: Loss curves comparison for each dataset
    for i, (dataset, color) in enumerate(zip(datasets, colors[: len(datasets)])):
        axes[3, i].plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["losses"]["val"],
            label="Baseline",
            color=color,
            linewidth=2,
        )
        axes[3, i].plot(
            experiment_data["ablation_no_modality"][dataset]["epochs"],
            experiment_data["ablation_no_modality"][dataset]["losses"]["val"],
            label="No Modality",
            color=color,
            linewidth=2,
            linestyle="--",
        )
        axes[3, i].set_xlabel("Epoch", fontsize=11)
        axes[3, i].set_ylabel("Validation Loss", fontsize=11)
        axes[3, i].set_title(f"{dataset.upper()} - Loss Comparison", fontsize=13)
        axes[3, i].legend()
        axes[3, i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, "ablation_comparison.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(f"\nPlot saved to {os.path.join(working_dir, 'ablation_comparison.png')}")

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

# Final summary
print("\n" + "=" * 80)
print("ABLATION STUDY RESULTS: BASELINE vs NO MODALITY SELECTION")
print("=" * 80)

for dataset in datasets:
    print(f"\n{dataset.upper()}:")
    print("  BASELINE:")
    print(
        f"    Final Val TCE: {experiment_data['baseline'][dataset]['tce']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val ARR: {experiment_data['baseline'][dataset]['arr']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val TCS: {experiment_data['baseline'][dataset]['tcs']['val'][-1]:.4f}"
    )
    print(f"    Best Epoch: {baseline_best_epochs[dataset]}")
    print("  ABLATION (No Modality):")
    print(
        f"    Final Val TCE: {experiment_data['ablation_no_modality'][dataset]['tce']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val ARR: {experiment_data['ablation_no_modality'][dataset]['arr']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val TCS: {experiment_data['ablation_no_modality'][dataset]['tcs']['val'][-1]:.4f}"
    )
    print(f"    Best Epoch: {ablation_best_epochs[dataset]}")
    print("  DELTA (Baseline - Ablation):")
    print(
        f"    TCE: {experiment_data['baseline'][dataset]['tce']['val'][-1] - experiment_data['ablation_no_modality'][dataset]['tce']['val'][-1]:.4f}"
    )
    print(
        f"    ARR: {experiment_data['baseline'][dataset]['arr']['val'][-1] - experiment_data['ablation_no_modality'][dataset]['arr']['val'][-1]:.4f}"
    )
    print(
        f"    TCS: {experiment_data['baseline'][dataset]['tcs']['val'][-1] - experiment_data['ablation_no_modality'][dataset]['tcs']['val'][-1]:.4f}"
    )

if len(datasets) > 0:
    baseline_avg_tce = np.mean(
        [experiment_data["baseline"][d]["tce"]["val"][-1] for d in datasets]
    )
    baseline_avg_arr = np.mean(
        [experiment_data["baseline"][d]["arr"]["val"][-1] for d in datasets]
    )
    baseline_avg_tcs = np.mean(
        [experiment_data["baseline"][d]["tcs"]["val"][-1] for d in datasets]
    )

    ablation_avg_tce = np.mean(
        [experiment_data["ablation_no_modality"][d]["tce"]["val"][-1] for d in datasets]
    )
    ablation_avg_arr = np.mean(
        [experiment_data["ablation_no_modality"][d]["arr"]["val"][-1] for d in datasets]
    )
    ablation_avg_tcs = np.mean(
        [experiment_data["ablation_no_modality"][d]["tcs"]["val"][-1] for d in datasets]
    )

    print("\n" + "=" * 80)
    print("AVERAGE RESULTS ACROSS ALL DATASETS:")
    print("=" * 80)
    print(
        f"BASELINE    - TCE: {baseline_avg_tce:.4f}, ARR: {baseline_avg_arr:.4f}, TCS: {baseline_avg_tcs:.4f}"
    )
    print(
        f"ABLATION    - TCE: {ablation_avg_tce:.4f}, ARR: {ablation_avg_arr:.4f}, TCS: {ablation_avg_tcs:.4f}"
    )
    print(
        f"DELTA (B-A) - TCE: {baseline_avg_tce - ablation_avg_tce:.4f}, ARR: {baseline_avg_arr - ablation_avg_arr:.4f}, TCS: {baseline_avg_tcs - ablation_avg_tcs:.4f}"
    )
    print("=" * 80)

    print("\nINTERPRETATION:")
    if (
        baseline_avg_arr > ablation_avg_arr
        and baseline_avg_tcs > ablation_avg_tcs
        and baseline_avg_tce < ablation_avg_tce
    ):
        print("✓ Modality selection branch IMPROVES performance across all metrics")
    elif (
        baseline_avg_arr < ablation_avg_arr
        and baseline_avg_tcs < ablation_avg_tcs
        and baseline_avg_tce > ablation_avg_tce
    ):
        print("✗ Modality selection branch DEGRADES performance - ablation is better")
    else:
        print(
            "○ Mixed results - modality selection has varied impact on different metrics"
        )
    print("=" * 80)

print("\n✓ Ablation study complete!")
