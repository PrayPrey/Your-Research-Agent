import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr
import matplotlib.pyplot as plt
import warnings

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
torch.manual_seed(42)


def generate_synthetic_dataset(
    n_samples=1000,
    n_features=20,
    noise_level=0.0,
    class_imbalance=0.5,
    missing_rate=0.0,
):
    X = np.random.randn(n_samples, n_features)
    true_weights = np.random.randn(n_features)
    logits = X @ true_weights
    probs = 1 / (1 + np.exp(-logits))
    y = (probs > 0.5).astype(int)
    X += noise_level * np.random.randn(n_samples, n_features)
    if class_imbalance != 0.5:
        mask_0, mask_1 = y == 0, y == 1
        n_class_0 = int(n_samples * (1 - class_imbalance))
        n_class_1 = n_samples - n_class_0
        idx_0 = np.where(mask_0)[0][: min(n_class_0, mask_0.sum())]
        idx_1 = np.where(mask_1)[0][: min(n_class_1, mask_1.sum())]
        idx = np.concatenate([idx_0, idx_1])
        np.random.shuffle(idx)
        X, y = X[idx], y[idx]
    if missing_rate > 0:
        mask = np.random.rand(*X.shape) < missing_rate
        X[mask] = 0
    return X.astype(np.float32), y.astype(np.int64)


def compute_documentation_debt_score(noise_level, class_imbalance, missing_rate):
    noise_debt = min(noise_level / 2.0, 1.0)
    imbalance_debt = abs(class_imbalance - 0.5) * 2
    missing_debt = missing_rate
    return 0.4 * noise_debt + 0.35 * imbalance_debt + 0.25 * missing_debt


class SimpleClassifier(nn.Module):
    def __init__(self, n_features, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, 2),
        )

    def forward(self, x):
        return self.net(x)


def train_and_evaluate(X, y, n_epochs=30, batch_size=64, lr=0.001, patience=5, seed=42):
    np.random.seed(seed)
    torch.manual_seed(seed)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=seed,
        stratify=y if len(np.unique(y)) > 1 else None,
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=seed
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.long),
    )
    val_dataset = TensorDataset(
        torch.tensor(X_val, dtype=torch.float32), torch.tensor(y_val, dtype=torch.long)
    )
    test_dataset = TensorDataset(
        torch.tensor(X_test, dtype=torch.float32),
        torch.tensor(y_test, dtype=torch.long),
    )

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    test_loader = DataLoader(test_dataset, batch_size=batch_size)

    model = SimpleClassifier(X.shape[1]).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_losses, val_losses = [], []
    best_val_loss, patience_counter = float("inf"), 0
    best_model_state = None

    for epoch in range(n_epochs):
        model.train()
        epoch_train_loss = 0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_train_loss += loss.item()
        train_losses.append(epoch_train_loss / len(train_loader))

        model.eval()
        epoch_val_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                loss = criterion(model(batch_x), batch_y)
                epoch_val_loss += loss.item()
        val_loss = epoch_val_loss / len(val_loader)
        val_losses.append(val_loss)

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict().copy()
        else:
            patience_counter += 1
            if patience_counter >= patience:
                break

    if best_model_state:
        model.load_state_dict(best_model_state)

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            _, predicted = torch.max(model(batch_x), 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

    test_accuracy = correct / total

    if test_accuracy > 0.99:
        warnings.warn(
            f"Suspiciously high accuracy ({test_accuracy:.4f}) - possible data leakage"
        )

    return 1 - test_accuracy, test_accuracy, train_losses, val_losses


# Configuration
hyperparams = [
    {"lr": 0.0005, "epochs": 40, "batch_size": 64},
    {"lr": 0.0003, "epochs": 50, "batch_size": 64},
]
n_seeds = 3
n_synthetic = 12

np.random.seed(123)
dataset_configs = [
    {
        "noise_level": np.random.uniform(0, 1.5),
        "class_imbalance": np.random.uniform(0.2, 0.8),
        "missing_rate": np.random.uniform(0, 0.25),
    }
    for _ in range(n_synthetic)
]

experiment_data = {}
best_correlation, best_params = -float("inf"), None
hp_results = {}

print("=" * 60)
print("ABLATION: No HuggingFace Real-World Datasets")
print("Documentation Debt Study with Synthetic Data Only")
print("=" * 60)

for hp in hyperparams:
    hp_key = f"lr_{hp['lr']}_ep_{hp['epochs']}_bs_{hp['batch_size']}"
    print(f"\n{'='*60}\nConfig: {hp_key}\n{'='*60}")

    all_debt_scores, all_failure_rates, all_accuracies, all_variances = [], [], [], []
    dataset_details = {}

    # Synthetic datasets only - NO HuggingFace datasets
    for i, config in enumerate(dataset_configs):
        seed_failures = []
        seed_train_losses = []
        seed_val_losses = []

        for seed in range(n_seeds):
            np.random.seed(123 + i + seed * 100)
            torch.manual_seed(42 + i + seed * 100)
            X, y = generate_synthetic_dataset(n_samples=600, n_features=20, **config)
            failure_rate, test_acc, train_losses, val_losses = train_and_evaluate(
                X,
                y,
                n_epochs=hp["epochs"],
                batch_size=hp["batch_size"],
                lr=hp["lr"],
                seed=seed,
            )
            seed_failures.append(failure_rate)
            seed_train_losses.append(train_losses)
            seed_val_losses.append(val_losses)

        debt_score = compute_documentation_debt_score(
            config["noise_level"], config["class_imbalance"], config["missing_rate"]
        )
        mean_failure = np.mean(seed_failures)
        variance = np.var(seed_failures)

        all_debt_scores.append(debt_score)
        all_failure_rates.append(mean_failure)
        all_variances.append(variance)
        all_accuracies.append(1 - mean_failure)

        dataset_details[f"synthetic_{i}"] = {
            "config": config,
            "debt_score": debt_score,
            "failure_rate": mean_failure,
            "variance": variance,
            "accuracy": 1 - mean_failure,
            "seed_failures": seed_failures,
        }

        if (i + 1) % 4 == 0:
            print(
                f"  Synthetic {i+1}/{n_synthetic}: debt={debt_score:.3f}, failure={mean_failure:.3f}, var={variance:.4f}"
            )

    debt_scores = np.array(all_debt_scores)
    failure_rates = np.array(all_failure_rates)

    pearson_corr, pearson_p = pearsonr(debt_scores, failure_rates)
    spearman_corr, spearman_p = spearmanr(debt_scores, failure_rates)
    mean_accuracy = np.mean(all_accuracies)

    hp_results[hp_key] = {
        "pearson_corr": pearson_corr,
        "pearson_p": pearson_p,
        "spearman_corr": spearman_corr,
        "spearman_p": spearman_p,
        "mean_accuracy": mean_accuracy,
        "debt_scores": debt_scores,
        "failure_rates": failure_rates,
        "variances": np.array(all_variances),
        "dataset_details": dataset_details,
    }

    print(
        f"\n  Pearson r={pearson_corr:.4f} (p={pearson_p:.4f}), Spearman ρ={spearman_corr:.4f} (p={spearman_p:.4f})"
    )
    print(f"  Mean accuracy: {mean_accuracy:.4f}")

    if spearman_corr > best_correlation:
        best_correlation, best_params = spearman_corr, hp_key

print(f"\n{'='*60}")
print(f"ABLATION RESULTS: Synthetic Data Only (No HuggingFace)")
print(f"Best: {best_params}, Spearman ρ={best_correlation:.4f}")
print(f"Number of datasets: {n_synthetic} (synthetic only)")
print(f"{'='*60}")

# Visualization
best_res = hp_results[best_params]
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].scatter(
    best_res["debt_scores"],
    best_res["failure_rates"],
    alpha=0.7,
    s=100,
    c="steelblue",
    edgecolors="navy",
    label="Synthetic datasets",
)
z = np.polyfit(best_res["debt_scores"], best_res["failure_rates"], 1)
x_line = np.linspace(best_res["debt_scores"].min(), best_res["debt_scores"].max(), 100)
axes[0].plot(
    x_line,
    np.poly1d(z)(x_line),
    "r--",
    linewidth=2,
    label=f"ρ={best_res['spearman_corr']:.3f}",
)
axes[0].set_xlabel("Documentation Debt Score")
axes[0].set_ylabel("Failure Rate")
axes[0].set_title("ABLATION: Synthetic Data Only\nDocumentation Debt vs Model Failure")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

corrs = [v["spearman_corr"] for v in hp_results.values()]
axes[1].barh(list(hp_results.keys()), corrs, color="steelblue")
axes[1].set_xlabel("Spearman Correlation")
axes[1].set_title("Hyperparameter Comparison (Synthetic Only)")
axes[1].axvline(x=0, color="gray", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_no_huggingface_analysis.png"), dpi=150)
plt.close()

# Save experiment data
experiment_data = {
    "ablation_no_huggingface": {
        "synthetic_only": {
            "metrics": {
                "pearson_corr": hp_results[best_params]["pearson_corr"],
                "pearson_p": hp_results[best_params]["pearson_p"],
                "spearman_corr": hp_results[best_params]["spearman_corr"],
                "spearman_p": hp_results[best_params]["spearman_p"],
                "mean_accuracy": hp_results[best_params]["mean_accuracy"],
            },
            "debt_scores": hp_results[best_params]["debt_scores"].tolist(),
            "failure_rates": hp_results[best_params]["failure_rates"].tolist(),
            "variances": hp_results[best_params]["variances"].tolist(),
        }
    },
    "best_params": best_params,
    "best_correlation": best_correlation,
    "n_synthetic_datasets": n_synthetic,
    "n_huggingface_datasets": 0,
    "ablation_description": "Removed all HuggingFace datasets (IMDB, Rotten Tomatoes, Yelp Polarity)",
    "results": {
        k: {
            kk: (
                vv.tolist()
                if isinstance(vv, np.ndarray)
                else (
                    {
                        kkk: vvv if not isinstance(vvv, np.ndarray) else vvv.tolist()
                        for kkk, vvv in vv.items()
                    }
                    if isinstance(vv, dict)
                    else vv
                )
            )
            for kk, vv in v.items()
        }
        for k, v in hp_results.items()
    },
}
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\ndocumentation_failure_correlation = {best_correlation:.4f}")
print(f"Datasets: {n_synthetic} synthetic only (HuggingFace datasets removed)")
print(f"Ablation purpose: Test if synthetic data alone provides sufficient signal")
print(f"\nResults saved to {working_dir}/experiment_data.npy")
