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
            "ccs": {"train": [], "val": []},
            "epochs": [],
        },
        "boolq": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "ccs": {"train": [], "val": []},
            "epochs": [],
        },
        "hellaswag": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "ccs": {"train": [], "val": []},
            "epochs": [],
        },
    },
    "normalized": {
        "squad": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "ccs": {"train": [], "val": []},
            "epochs": [],
        },
        "boolq": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "ccs": {"train": [], "val": []},
            "epochs": [],
        },
        "hellaswag": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "arr": {"train": [], "val": []},
            "tcs": {"train": [], "val": []},
            "tce": {"train": [], "val": []},
            "ccs": {"train": [], "val": []},
            "epochs": [],
        },
    },
}


# Feature Scaler for standardization
class FeatureScaler:
    def __init__(self):
        self.mean = None
        self.std = None

    def fit(self, features):
        """Compute mean and std from training data."""
        self.mean = np.mean(features, axis=0)
        self.std = np.std(features, axis=0)
        self.std = np.where(self.std == 0, 1, self.std)

    def transform(self, features):
        """Standardize features to zero mean and unit variance."""
        if self.mean is None or self.std is None:
            raise ValueError("Scaler must be fitted before transform")
        return (features - self.mean) / self.std

    def fit_transform(self, features):
        """Fit and transform in one step."""
        self.fit(features)
        return self.transform(features)


# Generate synthetic data
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


# Adaptive Modality Selector Network
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


# Calculate Component Contribution Score
def calculate_ccs(
    tce_baseline, tce_ablated, arr_baseline, arr_ablated, tcs_baseline, tcs_ablated
):
    """Calculate Component Contribution Score (CCS)."""
    # Avoid division by zero
    tce_term = 0.0
    if tce_baseline > 1e-8:
        tce_term = 0.4 * (tce_ablated - tce_baseline) / tce_baseline

    arr_term = 0.0
    if arr_baseline > 1e-8:
        arr_term = 0.3 * (arr_baseline - arr_ablated) / arr_baseline

    tcs_term = 0.0
    if tcs_baseline > 1e-8:
        tcs_term = 0.3 * (tcs_baseline - tcs_ablated) / tcs_baseline

    return tce_term + arr_term + tcs_term


# Training function with early stopping
def train_model(
    model,
    train_loader,
    val_loader,
    dataset_name,
    ablation_type,
    baseline_metrics=None,
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
            loss_modality = criterion_modality(modality_outputs, optimal_modality_batch)
            loss = loss_decision + 0.3 * loss_modality

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
                loss_modality = criterion_modality(
                    modality_outputs, optimal_modality_batch
                )
                loss = loss_decision + 0.3 * loss_modality

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

        # Calculate CCS if baseline metrics are provided
        train_ccs = 0.0
        val_ccs = 0.0
        if baseline_metrics is not None:
            train_ccs = calculate_ccs(
                baseline_metrics["train_tce"],
                train_tce,
                baseline_metrics["train_arr"],
                train_arr,
                baseline_metrics["train_tcs"],
                train_tcs,
            )
            val_ccs = calculate_ccs(
                baseline_metrics["val_tce"],
                val_tce,
                baseline_metrics["val_arr"],
                val_arr,
                baseline_metrics["val_tcs"],
                val_tcs,
            )

        # Store metrics
        experiment_data[ablation_type][dataset_name]["losses"]["train"].append(
            train_loss
        )
        experiment_data[ablation_type][dataset_name]["losses"]["val"].append(val_loss)
        experiment_data[ablation_type][dataset_name]["arr"]["train"].append(train_arr)
        experiment_data[ablation_type][dataset_name]["arr"]["val"].append(val_arr)
        experiment_data[ablation_type][dataset_name]["tcs"]["train"].append(train_tcs)
        experiment_data[ablation_type][dataset_name]["tcs"]["val"].append(val_tcs)
        experiment_data[ablation_type][dataset_name]["tce"]["train"].append(train_tce)
        experiment_data[ablation_type][dataset_name]["tce"]["val"].append(val_tce)
        experiment_data[ablation_type][dataset_name]["ccs"]["train"].append(train_ccs)
        experiment_data[ablation_type][dataset_name]["ccs"]["val"].append(val_ccs)
        experiment_data[ablation_type][dataset_name]["epochs"].append(epoch)

        # Combined metric for early stopping
        combined_metric = val_arr + val_tcs - val_tce

        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}"
            )
            print(
                f"  Val - ARR={val_arr:.4f}, TCS={val_tcs:.4f}, TCE={val_tce:.4f}, CCS={val_ccs:.4f}"
            )

        # Early stopping
        if combined_metric > best_metric:
            best_metric = combined_metric
            best_epoch = epoch
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}. Best epoch: {best_epoch}")
                break

    model.load_state_dict(best_model_state)
    return model, best_epoch


# Load and process datasets
print("\n=== Loading HuggingFace Datasets ===\n")

datasets_config = {}

# SQuAD
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

    datasets_config["squad"] = {
        "train_features": squad_train_features,
        "val_features": squad_val_features,
        "train_decisions": squad_train_decisions,
        "val_decisions": squad_val_decisions,
        "train_llm_correct": squad_train_llm_correct,
        "val_llm_correct": squad_val_llm_correct,
        "train_modality": squad_train_modality,
        "val_modality": squad_val_modality,
        "loaded": True,
    }
    print(f"SQuAD - Train: {len(squad_train_features)}, Val: {len(squad_val_features)}")
except Exception as e:
    print(f"Error loading SQuAD: {e}")
    datasets_config["squad"] = {"loaded": False}

# BoolQ
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

    datasets_config["boolq"] = {
        "train_features": boolq_train_features,
        "val_features": boolq_val_features,
        "train_decisions": boolq_train_decisions,
        "val_decisions": boolq_val_decisions,
        "train_llm_correct": boolq_train_llm_correct,
        "val_llm_correct": boolq_val_llm_correct,
        "train_modality": boolq_train_modality,
        "val_modality": boolq_val_modality,
        "loaded": True,
    }
    print(f"BoolQ - Train: {len(boolq_train_features)}, Val: {len(boolq_val_features)}")
except Exception as e:
    print(f"Error loading BoolQ: {e}")
    datasets_config["boolq"] = {"loaded": False}

# HellaSwag
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

    datasets_config["hellaswag"] = {
        "train_features": hellaswag_train_features,
        "val_features": hellaswag_val_features,
        "train_decisions": hellaswag_train_decisions,
        "val_decisions": hellaswag_val_decisions,
        "train_llm_correct": hellaswag_train_llm_correct,
        "val_llm_correct": hellaswag_val_llm_correct,
        "train_modality": hellaswag_train_modality,
        "val_modality": hellaswag_val_modality,
        "loaded": True,
    }
    print(
        f"HellaSwag - Train: {len(hellaswag_train_features)}, Val: {len(hellaswag_val_features)}"
    )
except Exception as e:
    print(f"Error loading HellaSwag: {e}")
    datasets_config["hellaswag"] = {"loaded": False}

# Train models on each dataset with both ablation types
print("\n=== Training Models: Baseline vs. Normalized Features ===\n")

best_epochs = {"baseline": {}, "normalized": {}}
baseline_final_metrics = {}

for dataset_name in ["squad", "boolq", "hellaswag"]:
    if not datasets_config[dataset_name]["loaded"]:
        continue

    print(f"\n{'='*60}")
    print(f"DATASET: {dataset_name.upper()}")
    print(f"{'='*60}")

    # BASELINE: No feature normalization (raw features)
    print(f"\n### BASELINE: {dataset_name.upper()} - Raw Features ###")

    train_dataset_baseline = ModalityDataset(
        datasets_config[dataset_name]["train_features"],
        datasets_config[dataset_name]["train_decisions"],
        datasets_config[dataset_name]["train_llm_correct"],
        datasets_config[dataset_name]["train_modality"],
    )
    val_dataset_baseline = ModalityDataset(
        datasets_config[dataset_name]["val_features"],
        datasets_config[dataset_name]["val_decisions"],
        datasets_config[dataset_name]["val_llm_correct"],
        datasets_config[dataset_name]["val_modality"],
    )

    train_loader_baseline = DataLoader(
        train_dataset_baseline, batch_size=32, shuffle=True
    )
    val_loader_baseline = DataLoader(val_dataset_baseline, batch_size=32, shuffle=False)

    model_baseline = AdaptiveModalityModel().to(device)
    model_baseline, best_epoch_baseline = train_model(
        model_baseline,
        train_loader_baseline,
        val_loader_baseline,
        dataset_name,
        "baseline",
        baseline_metrics=None,
        num_epochs=50,
        patience=10,
    )
    best_epochs["baseline"][dataset_name] = best_epoch_baseline

    # Store baseline final metrics for CCS calculation
    baseline_final_metrics[dataset_name] = {
        "train_tce": experiment_data["baseline"][dataset_name]["tce"]["train"][-1],
        "train_arr": experiment_data["baseline"][dataset_name]["arr"]["train"][-1],
        "train_tcs": experiment_data["baseline"][dataset_name]["tcs"]["train"][-1],
        "val_tce": experiment_data["baseline"][dataset_name]["tce"]["val"][-1],
        "val_arr": experiment_data["baseline"][dataset_name]["arr"]["val"][-1],
        "val_tcs": experiment_data["baseline"][dataset_name]["tcs"]["val"][-1],
    }

    # ABLATION: Feature normalization (standardized features)
    print(f"\n### ABLATION: {dataset_name.upper()} - Normalized Features ###")

    scaler = FeatureScaler()
    train_features_normalized = scaler.fit_transform(
        datasets_config[dataset_name]["train_features"]
    )
    val_features_normalized = scaler.transform(
        datasets_config[dataset_name]["val_features"]
    )

    train_dataset_normalized = ModalityDataset(
        train_features_normalized,
        datasets_config[dataset_name]["train_decisions"],
        datasets_config[dataset_name]["train_llm_correct"],
        datasets_config[dataset_name]["train_modality"],
    )
    val_dataset_normalized = ModalityDataset(
        val_features_normalized,
        datasets_config[dataset_name]["val_decisions"],
        datasets_config[dataset_name]["val_llm_correct"],
        datasets_config[dataset_name]["val_modality"],
    )

    train_loader_normalized = DataLoader(
        train_dataset_normalized, batch_size=32, shuffle=True
    )
    val_loader_normalized = DataLoader(
        val_dataset_normalized, batch_size=32, shuffle=False
    )

    model_normalized = AdaptiveModalityModel().to(device)
    model_normalized, best_epoch_normalized = train_model(
        model_normalized,
        train_loader_normalized,
        val_loader_normalized,
        dataset_name,
        "normalized",
        baseline_metrics=baseline_final_metrics[dataset_name],
        num_epochs=50,
        patience=10,
    )
    best_epochs["normalized"][dataset_name] = best_epoch_normalized

# Visualizations
datasets = [d for d in ["squad", "boolq", "hellaswag"] if datasets_config[d]["loaded"]]
colors_baseline = ["#2E86AB", "#A23B72", "#F18F01"]
colors_normalized = ["#06AED5", "#DD1C77", "#FFAA00"]

if len(datasets) > 0:
    fig = plt.figure(figsize=(20, 16))
    gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)

    # Row 1: TCE comparison across datasets
    ax1 = fig.add_subplot(gs[0, 0])
    for i, dataset in enumerate(datasets):
        ax1.plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["tce"]["val"],
            label=f"{dataset.upper()} (Baseline)",
            color=colors_baseline[i],
            linewidth=2,
            linestyle="-",
        )
        ax1.plot(
            experiment_data["normalized"][dataset]["epochs"],
            experiment_data["normalized"][dataset]["tce"]["val"],
            label=f"{dataset.upper()} (Normalized)",
            color=colors_normalized[i],
            linewidth=2,
            linestyle="--",
        )
    ax1.set_xlabel("Epoch", fontsize=11)
    ax1.set_ylabel("Trust Calibration Error", fontsize=11)
    ax1.set_title("TCE: Baseline vs Normalized", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=8, loc="best")
    ax1.grid(True, alpha=0.3)

    # Row 1: ARR comparison
    ax2 = fig.add_subplot(gs[0, 1])
    for i, dataset in enumerate(datasets):
        ax2.plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["arr"]["val"],
            label=f"{dataset.upper()} (Baseline)",
            color=colors_baseline[i],
            linewidth=2,
            linestyle="-",
        )
        ax2.plot(
            experiment_data["normalized"][dataset]["epochs"],
            experiment_data["normalized"][dataset]["arr"]["val"],
            label=f"{dataset.upper()} (Normalized)",
            color=colors_normalized[i],
            linewidth=2,
            linestyle="--",
        )
    ax2.set_xlabel("Epoch", fontsize=11)
    ax2.set_ylabel("Appropriate Reliance Rate", fontsize=11)
    ax2.set_title("ARR: Baseline vs Normalized", fontsize=13, fontweight="bold")
    ax2.legend(fontsize=8, loc="best")
    ax2.grid(True, alpha=0.3)

    # Row 1: TCS comparison
    ax3 = fig.add_subplot(gs[0, 2])
    for i, dataset in enumerate(datasets):
        ax3.plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["tcs"]["val"],
            label=f"{dataset.upper()} (Baseline)",
            color=colors_baseline[i],
            linewidth=2,
            linestyle="-",
        )
        ax3.plot(
            experiment_data["normalized"][dataset]["epochs"],
            experiment_data["normalized"][dataset]["tcs"]["val"],
            label=f"{dataset.upper()} (Normalized)",
            color=colors_normalized[i],
            linewidth=2,
            linestyle="--",
        )
    ax3.set_xlabel("Epoch", fontsize=11)
    ax3.set_ylabel("Trust Calibration Score", fontsize=11)
    ax3.set_title("TCS: Baseline vs Normalized", fontsize=13, fontweight="bold")
    ax3.legend(fontsize=8, loc="best")
    ax3.grid(True, alpha=0.3)

    # Row 2: Loss curves for each dataset
    for i, dataset in enumerate(datasets):
        ax = fig.add_subplot(gs[1, i])
        ax.plot(
            experiment_data["baseline"][dataset]["epochs"],
            experiment_data["baseline"][dataset]["losses"]["val"],
            label="Baseline",
            color=colors_baseline[i],
            linewidth=2,
            linestyle="-",
        )
        ax.plot(
            experiment_data["normalized"][dataset]["epochs"],
            experiment_data["normalized"][dataset]["losses"]["val"],
            label="Normalized",
            color=colors_normalized[i],
            linewidth=2,
            linestyle="--",
        )
        ax.set_xlabel("Epoch", fontsize=10)
        ax.set_ylabel("Validation Loss", fontsize=10)
        ax.set_title(f"{dataset.upper()} - Loss", fontsize=12, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    # Row 3: Final metrics comparison (bar charts)
    metrics_names = ["TCE", "ARR", "TCS"]
    for metric_idx, metric_key in enumerate(["tce", "arr", "tcs"]):
        ax = fig.add_subplot(gs[2, metric_idx])

        x_pos = np.arange(len(datasets))
        width = 0.35

        baseline_vals = [
            experiment_data["baseline"][d][metric_key]["val"][-1] for d in datasets
        ]
        normalized_vals = [
            experiment_data["normalized"][d][metric_key]["val"][-1] for d in datasets
        ]

        ax.bar(
            x_pos - width / 2,
            baseline_vals,
            width,
            label="Baseline",
            alpha=0.8,
            color="#2A9D8F",
        )
        ax.bar(
            x_pos + width / 2,
            normalized_vals,
            width,
            label="Normalized",
            alpha=0.8,
            color="#E76F51",
        )

        ax.set_xlabel("Dataset", fontsize=11)
        ax.set_ylabel(metrics_names[metric_idx], fontsize=11)
        ax.set_title(
            f"Final {metrics_names[metric_idx]} Comparison",
            fontsize=12,
            fontweight="bold",
        )
        ax.set_xticks(x_pos)
        ax.set_xticklabels([d.upper() for d in datasets], fontsize=9)
        ax.legend(fontsize=9)
        ax.grid(True, axis="y", alpha=0.3)

    # Row 4: Improvement analysis with safe division
    ax4_1 = fig.add_subplot(gs[3, 0])
    improvements_tce = []
    for dataset in datasets:
        baseline_tce = experiment_data["baseline"][dataset]["tce"]["val"][-1]
        normalized_tce = experiment_data["normalized"][dataset]["tce"]["val"][-1]
        if baseline_tce > 1e-8:
            improvement = ((baseline_tce - normalized_tce) / baseline_tce) * 100
        else:
            improvement = 0.0
        improvements_tce.append(improvement)

    ax4_1.bar(
        range(len(datasets)),
        improvements_tce,
        color=["#2A9D8F" if x > 0 else "#E63946" for x in improvements_tce],
        alpha=0.8,
    )
    ax4_1.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
    ax4_1.set_xlabel("Dataset", fontsize=11)
    ax4_1.set_ylabel("TCE Improvement (%)", fontsize=11)
    ax4_1.set_title(
        "TCE Improvement with Normalization", fontsize=12, fontweight="bold"
    )
    ax4_1.set_xticks(range(len(datasets)))
    ax4_1.set_xticklabels([d.upper() for d in datasets], fontsize=9)
    ax4_1.grid(True, axis="y", alpha=0.3)

    ax4_2 = fig.add_subplot(gs[3, 1])
    improvements_arr = []
    for dataset in datasets:
        baseline_arr = experiment_data["baseline"][dataset]["arr"]["val"][-1]
        normalized_arr = experiment_data["normalized"][dataset]["arr"]["val"][-1]
        if baseline_arr > 1e-8:
            improvement = ((normalized_arr - baseline_arr) / baseline_arr) * 100
        else:
            improvement = 0.0
        improvements_arr.append(improvement)

    ax4_2.bar(
        range(len(datasets)),
        improvements_arr,
        color=["#2A9D8F" if x > 0 else "#E63946" for x in improvements_arr],
        alpha=0.8,
    )
    ax4_2.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
    ax4_2.set_xlabel("Dataset", fontsize=11)
    ax4_2.set_ylabel("ARR Improvement (%)", fontsize=11)
    ax4_2.set_title(
        "ARR Improvement with Normalization", fontsize=12, fontweight="bold"
    )
    ax4_2.set_xticks(range(len(datasets)))
    ax4_2.set_xticklabels([d.upper() for d in datasets], fontsize=9)
    ax4_2.grid(True, axis="y", alpha=0.3)

    ax4_3 = fig.add_subplot(gs[3, 2])
    best_epochs_baseline = [best_epochs["baseline"][d] for d in datasets]
    best_epochs_normalized = [best_epochs["normalized"][d] for d in datasets]

    x_pos = np.arange(len(datasets))
    width = 0.35
    ax4_3.bar(
        x_pos - width / 2,
        best_epochs_baseline,
        width,
        label="Baseline",
        alpha=0.8,
        color="#2A9D8F",
    )
    ax4_3.bar(
        x_pos + width / 2,
        best_epochs_normalized,
        width,
        label="Normalized",
        alpha=0.8,
        color="#E76F51",
    )
    ax4_3.set_xlabel("Dataset", fontsize=11)
    ax4_3.set_ylabel("Best Epoch", fontsize=11)
    ax4_3.set_title("Convergence Speed Comparison", fontsize=12, fontweight="bold")
    ax4_3.set_xticks(x_pos)
    ax4_3.set_xticklabels([d.upper() for d in datasets], fontsize=9)
    ax4_3.legend(fontsize=9)
    ax4_3.grid(True, axis="y", alpha=0.3)

    plt.savefig(
        os.path.join(working_dir, "ablation_feature_normalization.png"),
        dpi=300,
        bbox_inches="tight",
    )
    print(
        f"\nPlot saved to {os.path.join(working_dir, 'ablation_feature_normalization.png')}"
    )
    plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

# Final summary
print("\n" + "=" * 80)
print("ABLATION STUDY RESULTS: FEATURE NORMALIZATION")
print("=" * 80)

for dataset in datasets:
    print(f"\n{dataset.upper()}:")
    print(f"  BASELINE (Raw Features):")
    print(
        f"    Final Val TCE: {experiment_data['baseline'][dataset]['tce']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val ARR: {experiment_data['baseline'][dataset]['arr']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val TCS: {experiment_data['baseline'][dataset]['tcs']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val CCS: {experiment_data['baseline'][dataset]['ccs']['val'][-1]:.4f}"
    )
    print(f"    Best Epoch: {best_epochs['baseline'][dataset]}")

    print(f"  NORMALIZED (Standardized Features):")
    print(
        f"    Final Val TCE: {experiment_data['normalized'][dataset]['tce']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val ARR: {experiment_data['normalized'][dataset]['arr']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val TCS: {experiment_data['normalized'][dataset]['tcs']['val'][-1]:.4f}"
    )
    print(
        f"    Final Val CCS: {experiment_data['normalized'][dataset]['ccs']['val'][-1]:.4f}"
    )
    print(f"    Best Epoch: {best_epochs['normalized'][dataset]}")

# Average improvements
print("\n" + "=" * 80)
print("AVERAGE IMPROVEMENTS WITH FEATURE NORMALIZATION")
print("=" * 80)

avg_tce_baseline = np.mean(
    [experiment_data["baseline"][d]["tce"]["val"][-1] for d in datasets]
)
avg_tce_normalized = np.mean(
    [experiment_data["normalized"][d]["tce"]["val"][-1] for d in datasets]
)
avg_arr_baseline = np.mean(
    [experiment_data["baseline"][d]["arr"]["val"][-1] for d in datasets]
)
avg_arr_normalized = np.mean(
    [experiment_data["normalized"][d]["arr"]["val"][-1] for d in datasets]
)
avg_tcs_baseline = np.mean(
    [experiment_data["baseline"][d]["tcs"]["val"][-1] for d in datasets]
)
avg_tcs_normalized = np.mean(
    [experiment_data["normalized"][d]["tcs"]["val"][-1] for d in datasets]
)
avg_ccs_normalized = np.mean(
    [experiment_data["normalized"][d]["ccs"]["val"][-1] for d in datasets]
)

print(f"\nBaseline (Raw Features):")
print(f"  Avg TCE: {avg_tce_baseline:.4f}")
print(f"  Avg ARR: {avg_arr_baseline:.4f}")
print(f"  Avg TCS: {avg_tcs_baseline:.4f}")

print(f"\nNormalized (Standardized Features):")
print(f"  Avg TCE: {avg_tce_normalized:.4f}")
print(f"  Avg ARR: {avg_arr_normalized:.4f}")
print(f"  Avg TCS: {avg_tcs_normalized:.4f}")
print(f"  Avg CCS: {avg_ccs_normalized:.4f}")

print(f"\nRelative Improvement:")
if avg_tce_baseline > 1e-8:
    print(
        f"  TCE: {((avg_tce_baseline - avg_tce_normalized) / avg_tce_baseline * 100):+.2f}%"
    )
else:
    print(f"  TCE: N/A (baseline near zero)")
if avg_arr_baseline > 1e-8:
    print(
        f"  ARR: {((avg_arr_normalized - avg_arr_baseline) / avg_arr_baseline * 100):+.2f}%"
    )
else:
    print(f"  ARR: N/A (baseline near zero)")
if avg_tcs_baseline > 1e-8:
    print(
        f"  TCS: {((avg_tcs_normalized - avg_tcs_baseline) / avg_tcs_baseline * 100):+.2f}%"
    )
else:
    print(f"  TCS: N/A (baseline near zero)")

print("=" * 80)
print("Ablation study complete!")
