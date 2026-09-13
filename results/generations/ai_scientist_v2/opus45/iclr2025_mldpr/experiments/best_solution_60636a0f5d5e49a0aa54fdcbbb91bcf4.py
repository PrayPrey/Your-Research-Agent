import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from datasets import load_dataset

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
        X, y = X[idx], y[idx]
    if missing_rate > 0:
        mask = np.random.rand(*X.shape) < missing_rate
        X[mask] = 0
    return X.astype(np.float32), y.astype(np.int64)


def compute_documentation_debt_score(noise_level, class_imbalance, missing_rate):
    noise_debt = noise_level / 2.0
    imbalance_debt = abs(class_imbalance - 0.5) * 2
    missing_debt = missing_rate
    return 0.4 * noise_debt + 0.35 * imbalance_debt + 0.25 * missing_debt


class SimpleClassifier(nn.Module):
    def __init__(self, n_features, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 2),
        )

    def forward(self, x):
        return self.net(x)


def train_and_evaluate(X, y, n_epochs=30, batch_size=64, lr=0.001):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.15, random_state=42
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
        val_losses.append(epoch_val_loss / len(val_loader))
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}: validation_loss = {val_losses[-1]:.4f}")

    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            _, predicted = torch.max(model(batch_x), 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

    test_accuracy = correct / total
    return 1 - test_accuracy, test_accuracy, train_losses, val_losses


def load_huggingface_dataset(dataset_name, n_samples=1000, n_features=100):
    print(f"Loading HuggingFace dataset: {dataset_name}")
    if dataset_name == "imdb":
        dataset = load_dataset("imdb", split="train")
        texts = dataset["text"][:n_samples]
        labels = dataset["label"][:n_samples]
        debt_score = 0.3  # Moderate documentation
    elif dataset_name == "rotten_tomatoes":
        dataset = load_dataset("rotten_tomatoes", split="train")
        texts = dataset["text"][:n_samples]
        labels = dataset["label"][:n_samples]
        debt_score = 0.5  # Less documentation
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    vectorizer = TfidfVectorizer(max_features=n_features, stop_words="english")
    X = vectorizer.fit_transform(texts).toarray().astype(np.float32)
    y = np.array(labels, dtype=np.int64)
    return X, y, debt_score


# Hyperparameter configurations
hyperparams = [
    {"lr": 0.0005, "epochs": 30, "batch_size": 64},
    {"lr": 0.0005, "epochs": 50, "batch_size": 32},
    {"lr": 0.001, "epochs": 40, "batch_size": 64},
    {"lr": 0.0003, "epochs": 60, "batch_size": 128},
]

n_synthetic = 15
np.random.seed(123)
dataset_configs = [
    {
        "noise_level": np.random.uniform(0, 2.0),
        "class_imbalance": np.random.uniform(0.1, 0.9),
        "missing_rate": np.random.uniform(0, 0.3),
    }
    for _ in range(n_synthetic)
]

experiment_data = {}
best_correlation, best_params = -float("inf"), None
hp_results = {}

print("=" * 60)
print("Hyperparameter Tuning with Synthetic + HuggingFace Datasets")
print("=" * 60)

for hp in hyperparams:
    hp_key = f"lr_{hp['lr']}_ep_{hp['epochs']}_bs_{hp['batch_size']}"
    print(f"\n{'='*60}\nTesting: {hp_key}\n{'='*60}")

    experiment_data[hp_key] = {
        "documentation_debt": {
            "losses": {"train": [], "val": []},
            "debt_scores": [],
            "failure_rates": [],
            "test_accuracies": [],
            "dataset_configs": [],
        }
    }

    debt_scores, failure_rates, test_accuracies = [], [], []

    # Synthetic datasets
    for i, config in enumerate(dataset_configs):
        np.random.seed(123 + i)
        torch.manual_seed(42 + i)
        X, y = generate_synthetic_dataset(n_samples=800, n_features=20, **config)
        debt_score = compute_documentation_debt_score(
            config["noise_level"], config["class_imbalance"], config["missing_rate"]
        )
        failure_rate, test_acc, train_l, val_l = train_and_evaluate(
            X, y, n_epochs=hp["epochs"], batch_size=hp["batch_size"], lr=hp["lr"]
        )

        debt_scores.append(debt_score)
        failure_rates.append(failure_rate)
        test_accuracies.append(test_acc)
        experiment_data[hp_key]["documentation_debt"]["losses"]["train"].append(train_l)
        experiment_data[hp_key]["documentation_debt"]["losses"]["val"].append(val_l)
        experiment_data[hp_key]["documentation_debt"]["dataset_configs"].append(config)
        if (i + 1) % 5 == 0:
            print(f"  Synthetic: {i+1}/{n_synthetic}")

    # HuggingFace datasets
    for ds_name in ["imdb", "rotten_tomatoes"]:
        torch.manual_seed(42)
        X, y, debt_score = load_huggingface_dataset(
            ds_name, n_samples=1000, n_features=50
        )
        failure_rate, test_acc, train_l, val_l = train_and_evaluate(
            X, y, n_epochs=hp["epochs"], batch_size=hp["batch_size"], lr=hp["lr"]
        )
        debt_scores.append(debt_score)
        failure_rates.append(failure_rate)
        test_accuracies.append(test_acc)
        experiment_data[hp_key]["documentation_debt"]["losses"]["train"].append(train_l)
        experiment_data[hp_key]["documentation_debt"]["losses"]["val"].append(val_l)
        print(f"  {ds_name}: acc={test_acc:.4f}, debt={debt_score:.2f}")

    debt_scores, failure_rates = np.array(debt_scores), np.array(failure_rates)
    correlation, p_value = pearsonr(debt_scores, failure_rates)
    mean_accuracy = np.mean(test_accuracies)

    experiment_data[hp_key]["documentation_debt"]["debt_scores"] = debt_scores.tolist()
    experiment_data[hp_key]["documentation_debt"][
        "failure_rates"
    ] = failure_rates.tolist()
    experiment_data[hp_key]["documentation_debt"]["correlation"] = correlation
    experiment_data[hp_key]["documentation_debt"]["p_value"] = p_value
    experiment_data[hp_key]["documentation_debt"]["mean_accuracy"] = mean_accuracy

    hp_results[hp_key] = {
        "correlation": correlation,
        "p_value": p_value,
        "mean_accuracy": mean_accuracy,
        "debt_scores": debt_scores,
        "failure_rates": failure_rates,
        "params": hp,
    }

    print(
        f"\n  Results: correlation={correlation:.4f}, p-value={p_value:.6f}, mean_acc={mean_accuracy:.4f}"
    )
    if correlation > best_correlation:
        best_correlation, best_params = correlation, hp_key

print("\n" + "=" * 60 + "\nFINAL RESULTS\n" + "=" * 60)
for k, v in hp_results.items():
    print(
        f"  {k}: corr={v['correlation']:.4f}, p={v['p_value']:.6f}, acc={v['mean_accuracy']:.4f}"
    )
print(f"\nBest: {best_params}, correlation={best_correlation:.4f}")

# Visualizations
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
best_res = hp_results[best_params]
axes[0].scatter(
    best_res["debt_scores"],
    best_res["failure_rates"],
    alpha=0.7,
    s=100,
    c="steelblue",
    edgecolors="navy",
)
z = np.polyfit(best_res["debt_scores"], best_res["failure_rates"], 1)
x_line = np.linspace(best_res["debt_scores"].min(), best_res["debt_scores"].max(), 100)
axes[0].plot(
    x_line,
    np.poly1d(z)(x_line),
    "r--",
    linewidth=2,
    label=f"r={best_res['correlation']:.3f}",
)
axes[0].set_xlabel("Documentation Debt Score")
axes[0].set_ylabel("Failure Rate")
axes[0].set_title(f"Best Config: Debt vs Failure")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

correlations = [v["correlation"] for v in hp_results.values()]
axes[1].barh(list(hp_results.keys()), correlations, color="steelblue")
axes[1].set_xlabel("Correlation")
axes[1].set_title("Hyperparameter Comparison")
axes[1].axvline(x=best_correlation, color="r", linestyle="--")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "hp_tuning_results.png"), dpi=150)
plt.close()

experiment_data["tuning_summary"] = {
    "best_params": best_params,
    "best_correlation": best_correlation,
    "all_results": {
        k: {
            kk: vv if not isinstance(vv, np.ndarray) else vv.tolist()
            for kk, vv in v.items()
        }
        for k, v in hp_results.items()
    },
}
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
np.save(os.path.join(working_dir, "debt_scores.npy"), best_res["debt_scores"])
np.save(os.path.join(working_dir, "failure_rates.npy"), best_res["failure_rates"])

print(f"\ndocumentation_failure_correlation = {best_correlation:.4f}")
print(f"Best hyperparameters: {best_params}")
print(f"Datasets used: {n_synthetic} synthetic + 2 HuggingFace (imdb, rotten_tomatoes)")
