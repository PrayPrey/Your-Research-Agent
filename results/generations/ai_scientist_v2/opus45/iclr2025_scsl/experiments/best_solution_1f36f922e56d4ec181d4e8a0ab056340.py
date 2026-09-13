import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")


def create_colored_mnist(n_samples=10000, spurious_corr=0.9):
    from torchvision import datasets

    mnist = datasets.MNIST(root="./data", train=True, download=True)
    images = mnist.data.numpy()[:n_samples]
    labels = mnist.targets.numpy()[:n_samples]
    binary_labels = (labels >= 5).astype(np.int64)
    colored_images = np.zeros((n_samples, 3, 28, 28), dtype=np.float32)
    spurious_labels = np.zeros(n_samples, dtype=np.int64)
    for i in range(n_samples):
        img = images[i].astype(np.float32) / 255.0
        aligned = np.random.random() < spurious_corr
        color_idx = binary_labels[i] if aligned else 1 - binary_labels[i]
        spurious_labels[i] = color_idx
        colored_images[i, color_idx] = img
    return colored_images, binary_labels, spurious_labels


def create_colored_fashion_mnist(n_samples=10000, spurious_corr=0.9):
    from datasets import load_dataset

    dataset = load_dataset("fashion_mnist", split="train")
    images = np.array([np.array(img) for img in dataset["image"][:n_samples]])
    labels = np.array(dataset["label"][:n_samples])
    tops = [0, 2, 3, 4, 6]
    binary_labels = np.array([0 if l in tops else 1 for l in labels], dtype=np.int64)
    colored_images = np.zeros((n_samples, 3, 28, 28), dtype=np.float32)
    spurious_labels = np.zeros(n_samples, dtype=np.int64)
    for i in range(n_samples):
        img = images[i].astype(np.float32) / 255.0
        aligned = np.random.random() < spurious_corr
        color_idx = binary_labels[i] if aligned else 1 - binary_labels[i]
        spurious_labels[i] = color_idx
        colored_images[i, 0 if color_idx == 0 else 2] = img
    return colored_images, binary_labels, spurious_labels


def create_colored_cifar10(n_samples=10000, spurious_corr=0.9):
    from datasets import load_dataset

    dataset = load_dataset("cifar10", split="train")
    animals = [2, 3, 4, 5, 6, 7]
    binary_labels = np.array(
        [
            0 if dataset[i]["label"] in animals else 1
            for i in range(min(n_samples, len(dataset)))
        ],
        dtype=np.int64,
    )
    colored_images = np.zeros((len(binary_labels), 3, 32, 32), dtype=np.float32)
    spurious_labels = np.zeros(len(binary_labels), dtype=np.int64)
    for idx in range(len(binary_labels)):
        img = np.array(dataset[idx]["img"]).astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        aligned = np.random.random() < spurious_corr
        color_idx = binary_labels[idx] if aligned else 1 - binary_labels[idx]
        spurious_labels[idx] = color_idx
        colored_images[idx] = img
        bw = 4
        channel = 0 if color_idx == 0 else 2
        colored_images[idx, channel, :bw, :] = 1.0
        colored_images[idx, channel, -bw:, :] = 1.0
        colored_images[idx, channel, :, :bw] = 1.0
        colored_images[idx, channel, :, -bw:] = 1.0
    return colored_images, binary_labels, spurious_labels


class ImprovedCNN(nn.Module):
    def __init__(self, input_size=28, dropout_rate=0.3, n_hidden=128):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(dropout_rate)
        self.relu = nn.ReLU()
        final_size = input_size // 4
        self.fc1 = nn.Linear(64 * final_size * final_size, n_hidden)
        self.fc2 = nn.Linear(n_hidden, 2)
        self.n_hidden = n_hidden

    def forward(self, x, neuron_weights=None):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = x.view(x.size(0), -1)
        features = self.relu(self.fc1(x))
        if neuron_weights is not None:
            features = features * neuron_weights.to(features.device)
        x = self.dropout(features)
        x = self.fc2(x)
        return x


def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    pooled_std = np.sqrt(
        ((n1 - 1) * np.var(group1) + (n2 - 1) * np.var(group2)) / (n1 + n2 - 2)
    )
    return (np.mean(group1) - np.mean(group2)) / (pooled_std + 1e-8)


def cluster_neurons_multi_feature(grad_history, n_clusters=2):
    """Multi-feature clustering using all 4 features"""
    n_epochs, n_neurons = grad_history.shape
    features = np.zeros((n_neurons, 4))
    for i in range(n_neurons):
        features[i, 0] = grad_history[:5, i].mean()  # initial velocity
        features[i, 1] = grad_history[-10:, i].mean()  # final velocity
        features[i, 2] = (features[i, 0] - features[i, 1]) / (
            features[i, 0] + 1e-8
        )  # decay rate
        threshold = 0.1 * grad_history[:, i].max()
        plateau_idx = np.where(grad_history[:, i] < threshold)[0]
        features[i, 3] = plateau_idx[0] if len(plateau_idx) > 0 else n_epochs
    features_norm = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_norm)
    cluster_plateau_means = [features[labels == c, 3].mean() for c in range(n_clusters)]
    spurious_cluster = np.argmin(cluster_plateau_means)
    spurious_neurons = labels == spurious_cluster
    return spurious_neurons, ~spurious_neurons, features


def cluster_neurons_single_feature(grad_history, n_clusters=2):
    """Single-feature clustering using only plateau epoch"""
    n_epochs, n_neurons = grad_history.shape
    plateau_epochs = np.zeros(n_neurons)
    for i in range(n_neurons):
        threshold = 0.1 * grad_history[:, i].max()
        plateau_idx = np.where(grad_history[:, i] < threshold)[0]
        plateau_epochs[i] = plateau_idx[0] if len(plateau_idx) > 0 else n_epochs
    features = plateau_epochs.reshape(-1, 1)
    features_norm = (features - features.mean()) / (features.std() + 1e-8)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_norm)
    cluster_means = [plateau_epochs[labels == c].mean() for c in range(n_clusters)]
    spurious_cluster = np.argmin(cluster_means)
    spurious_neurons = labels == spurious_cluster
    return spurious_neurons, ~spurious_neurons, plateau_epochs


def evaluate_with_groups(model, loader, y_true, s_true, neuron_weights=None):
    model.eval()
    all_preds = []
    with torch.no_grad():
        for batch_x, _ in loader:
            batch_x = batch_x.to(device)
            outputs = model(batch_x, neuron_weights=neuron_weights)
            _, preds = outputs.max(1)
            all_preds.extend(preds.cpu().numpy())
    all_preds = np.array(all_preds)
    groups = {}
    for y in [0, 1]:
        for s in [0, 1]:
            mask = (y_true == y) & (s_true == s)
            if mask.sum() > 0:
                groups[(y, s)] = (all_preds[mask] == y_true[mask]).mean() * 100
    avg_acc = (all_preds == y_true).mean() * 100
    worst_group = min(groups.values()) if groups else 0
    return avg_acc, worst_group, groups


def train_and_analyze(config, train_loader, test_loader, test_y, test_s, input_size=28):
    torch.manual_seed(config.get("seed", 42))
    np.random.seed(config.get("seed", 42))
    model = ImprovedCNN(input_size=input_size, dropout_rate=config["dropout"]).to(
        device
    )
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(), lr=config["lr"], weight_decay=config["weight_decay"]
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config["n_epochs"]
    )

    velocity_data = {"fc1_grad": []}
    results = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "worst_group": [],
    }
    best_val_loss, patience_counter, best_model_state = float("inf"), 0, None

    for epoch in range(config["n_epochs"]):
        model.train()
        train_loss, correct, total = 0.0, 0, 0
        epoch_grads = []

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            epoch_grads.append(model.fc1.weight.grad.norm(dim=1).cpu().numpy())
            optimizer.step()
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            total += batch_y.size(0)
            correct += predicted.eq(batch_y).sum().item()

        scheduler.step()
        velocity_data["fc1_grad"].append(np.mean(epoch_grads, axis=0))
        train_acc = 100.0 * correct / total
        avg_train_loss = train_loss / len(train_loader)

        model.eval()
        val_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                total += batch_y.size(0)
                correct += predicted.eq(batch_y).sum().item()

        val_acc = 100.0 * correct / total
        avg_val_loss = val_loss / len(test_loader)
        _, worst_group, _ = evaluate_with_groups(model, test_loader, test_y, test_s)

        results["losses"]["train"].append(avg_train_loss)
        results["losses"]["val"].append(avg_val_loss)
        results["metrics"]["train"].append(train_acc)
        results["metrics"]["val"].append(val_acc)
        results["worst_group"].append(worst_group)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_model_state = {
                k: v.cpu().clone() for k, v in model.state_dict().items()
            }
            patience_counter = 0
        else:
            patience_counter += 1

        if epoch % 10 == 0:
            print(
                f"  Epoch {epoch}: train={train_acc:.1f}%, val={val_acc:.1f}%, worst={worst_group:.1f}%"
            )

        if patience_counter >= config["patience"]:
            print(f"  Early stopping at epoch {epoch}")
            break

    if best_model_state:
        model.load_state_dict({k: v.to(device) for k, v in best_model_state.items()})

    fc1_grads = np.array(velocity_data["fc1_grad"])

    # Multi-feature clustering
    spurious_multi, core_multi, features_multi = cluster_neurons_multi_feature(
        fc1_grads
    )
    # Single-feature clustering (plateau epoch only)
    spurious_single, core_single, plateau_epochs = cluster_neurons_single_feature(
        fc1_grads
    )

    # Compute separation metrics for both approaches
    def compute_separation(spurious, core, features_all, plateau):
        sep = {
            "plateau_epoch": abs(cohens_d(plateau[spurious], plateau[core])),
            "initial_velocity": abs(
                cohens_d(
                    fc1_grads[:5].mean(axis=0)[spurious],
                    fc1_grads[:5].mean(axis=0)[core],
                )
            ),
            "final_velocity": abs(
                cohens_d(
                    fc1_grads[-10:].mean(axis=0)[spurious],
                    fc1_grads[-10:].mean(axis=0)[core],
                )
            ),
        }
        return sep, np.mean(list(sep.values()))

    sep_multi, avg_sep_multi = compute_separation(
        spurious_multi, core_multi, features_multi, features_multi[:, 3]
    )
    sep_single, avg_sep_single = compute_separation(
        spurious_single, core_single, None, plateau_epochs
    )

    # Evaluate with neuron reweighting
    weight_factor = config.get("reweight_factor", 0.3)

    neuron_weights_multi = torch.ones(model.n_hidden)
    neuron_weights_multi[spurious_multi] = weight_factor

    neuron_weights_single = torch.ones(model.n_hidden)
    neuron_weights_single[spurious_single] = weight_factor

    avg_acc_erm, worst_erm, groups_erm = evaluate_with_groups(
        model, test_loader, test_y, test_s
    )
    avg_acc_multi, worst_multi, groups_multi = evaluate_with_groups(
        model, test_loader, test_y, test_s, neuron_weights_multi
    )
    avg_acc_single, worst_single, groups_single = evaluate_with_groups(
        model, test_loader, test_y, test_s, neuron_weights_single
    )

    # Agreement between clustering methods
    agreement = (spurious_multi == spurious_single).mean() * 100

    results["velocity_data"] = velocity_data
    results["multi_feature"] = {
        "spurious_neurons": spurious_multi,
        "separation_metrics": sep_multi,
        "avg_separation": avg_sep_multi,
        "n_spurious": spurious_multi.sum(),
        "inference": {
            "avg": avg_acc_multi,
            "worst": worst_multi,
            "groups": groups_multi,
        },
    }
    results["single_feature"] = {
        "spurious_neurons": spurious_single,
        "plateau_epochs": plateau_epochs,
        "separation_metrics": sep_single,
        "avg_separation": avg_sep_single,
        "n_spurious": spurious_single.sum(),
        "inference": {
            "avg": avg_acc_single,
            "worst": worst_single,
            "groups": groups_single,
        },
    }
    results["erm"] = {"avg": avg_acc_erm, "worst": worst_erm, "groups": groups_erm}
    results["clustering_agreement"] = agreement
    results["model"] = model
    return results


# Create datasets
print("Creating datasets...")
torch.manual_seed(42)
np.random.seed(42)
datasets_info = {}

print("Loading ColoredMNIST...")
X_train_cm, y_train_cm, s_train_cm = create_colored_mnist(
    n_samples=10000, spurious_corr=0.95
)
X_test_cm, y_test_cm, s_test_cm = create_colored_mnist(
    n_samples=2000, spurious_corr=0.5
)
mean_cm, std_cm = X_train_cm.mean(), X_train_cm.std() + 1e-8
datasets_info["colored_mnist"] = {
    "train": TensorDataset(
        torch.FloatTensor((X_train_cm - mean_cm) / std_cm), torch.LongTensor(y_train_cm)
    ),
    "test": TensorDataset(
        torch.FloatTensor((X_test_cm - mean_cm) / std_cm), torch.LongTensor(y_test_cm)
    ),
    "test_y": y_test_cm,
    "test_s": s_test_cm,
    "input_size": 28,
}

print("Loading ColoredFashionMNIST...")
X_train_fm, y_train_fm, s_train_fm = create_colored_fashion_mnist(
    n_samples=10000, spurious_corr=0.95
)
X_test_fm, y_test_fm, s_test_fm = create_colored_fashion_mnist(
    n_samples=2000, spurious_corr=0.5
)
mean_fm, std_fm = X_train_fm.mean(), X_train_fm.std() + 1e-8
datasets_info["colored_fashion_mnist"] = {
    "train": TensorDataset(
        torch.FloatTensor((X_train_fm - mean_fm) / std_fm), torch.LongTensor(y_train_fm)
    ),
    "test": TensorDataset(
        torch.FloatTensor((X_test_fm - mean_fm) / std_fm), torch.LongTensor(y_test_fm)
    ),
    "test_y": y_test_fm,
    "test_s": s_test_fm,
    "input_size": 28,
}

print("Loading ColoredCIFAR10...")
X_train_cf, y_train_cf, s_train_cf = create_colored_cifar10(
    n_samples=10000, spurious_corr=0.95
)
X_test_cf, y_test_cf, s_test_cf = create_colored_cifar10(
    n_samples=2000, spurious_corr=0.5
)
mean_cf, std_cf = X_train_cf.mean(), X_train_cf.std() + 1e-8
datasets_info["colored_cifar10"] = {
    "train": TensorDataset(
        torch.FloatTensor((X_train_cf - mean_cf) / std_cf), torch.LongTensor(y_train_cf)
    ),
    "test": TensorDataset(
        torch.FloatTensor((X_test_cf - mean_cf) / std_cf), torch.LongTensor(y_test_cf)
    ),
    "test_y": y_test_cf,
    "test_s": s_test_cf,
    "input_size": 32,
}

config = {
    "lr": 0.001,
    "batch_size": 128,
    "n_epochs": 60,
    "dropout": 0.4,
    "weight_decay": 5e-4,
    "seed": 42,
    "patience": 15,
    "reweight_factor": 0.3,
}

# Run ablation study
experiment_data = {"multi_feature": {}, "single_feature": {}}

for dataset_name, data_info in datasets_info.items():
    print(f"\n{'='*50}\nDataset: {dataset_name}\n{'='*50}")
    train_loader = DataLoader(
        data_info["train"], batch_size=config["batch_size"], shuffle=True
    )
    test_loader = DataLoader(
        data_info["test"], batch_size=config["batch_size"], shuffle=False
    )

    results = train_and_analyze(
        config,
        train_loader,
        test_loader,
        data_info["test_y"],
        data_info["test_s"],
        data_info["input_size"],
    )
    del results["model"]

    # Store results for both ablation types
    experiment_data["multi_feature"][dataset_name] = {
        "metrics": results["metrics"],
        "losses": results["losses"],
        "worst_group": results["worst_group"],
        "spurious_neurons": results["multi_feature"]["spurious_neurons"],
        "separation_metrics": results["multi_feature"]["separation_metrics"],
        "avg_separation": results["multi_feature"]["avg_separation"],
        "n_spurious": int(results["multi_feature"]["n_spurious"]),
        "inference": results["multi_feature"]["inference"],
        "erm": results["erm"],
        "velocity_data": results["velocity_data"],
    }
    experiment_data["single_feature"][dataset_name] = {
        "metrics": results["metrics"],
        "losses": results["losses"],
        "worst_group": results["worst_group"],
        "spurious_neurons": results["single_feature"]["spurious_neurons"],
        "plateau_epochs": results["single_feature"]["plateau_epochs"],
        "separation_metrics": results["single_feature"]["separation_metrics"],
        "avg_separation": results["single_feature"]["avg_separation"],
        "n_spurious": int(results["single_feature"]["n_spurious"]),
        "inference": results["single_feature"]["inference"],
        "erm": results["erm"],
        "velocity_data": results["velocity_data"],
    }
    experiment_data["multi_feature"][dataset_name]["clustering_agreement"] = results[
        "clustering_agreement"
    ]
    experiment_data["single_feature"][dataset_name]["clustering_agreement"] = results[
        "clustering_agreement"
    ]

    print(f"\nResults for {dataset_name}:")
    print(
        f"  ERM: avg={results['erm']['avg']:.1f}%, worst={results['erm']['worst']:.1f}%"
    )
    print(
        f"  Multi-feature: separation={results['multi_feature']['avg_separation']:.4f}, avg={results['multi_feature']['inference']['avg']:.1f}%, worst={results['multi_feature']['inference']['worst']:.1f}%"
    )
    print(
        f"  Single-feature: separation={results['single_feature']['avg_separation']:.4f}, avg={results['single_feature']['inference']['avg']:.1f}%, worst={results['single_feature']['inference']['worst']:.1f}%"
    )
    print(f"  Clustering agreement: {results['clustering_agreement']:.1f}%")

# Summary
print(
    "\n"
    + "=" * 70
    + "\nABLATION STUDY SUMMARY: Single vs Multi-Feature Clustering\n"
    + "=" * 70
)
print(
    f"{'Dataset':<25} {'Method':<15} {'Separation':<12} {'Worst-Group':<12} {'Improvement':<12}"
)
print("-" * 70)

for ds in datasets_info:
    erm_worst = experiment_data["multi_feature"][ds]["erm"]["worst"]
    for method in ["multi_feature", "single_feature"]:
        sep = experiment_data[method][ds]["avg_separation"]
        worst = experiment_data[method][ds]["inference"]["worst"]
        improvement = worst - erm_worst
        method_name = (
            "Multi (4-feat)" if method == "multi_feature" else "Single (plateau)"
        )
        print(
            f"{ds:<25} {method_name:<15} {sep:<12.4f} {worst:<12.1f} {improvement:+.1f}%"
        )
    print()

# Plotting
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
dataset_names = list(datasets_info.keys())

for col, ds in enumerate(dataset_names):
    # Row 0: Accuracy curves
    axes[0, col].plot(
        experiment_data["multi_feature"][ds]["metrics"]["train"],
        label="Train",
        alpha=0.8,
    )
    axes[0, col].plot(
        experiment_data["multi_feature"][ds]["metrics"]["val"], label="Val", alpha=0.8
    )
    axes[0, col].set_title(f"{ds}\nAccuracy")
    axes[0, col].legend()
    axes[0, col].grid(True)
    axes[0, col].set_xlabel("Epoch")
    axes[0, col].set_ylabel("Accuracy (%)")

    # Row 1: Velocity signatures comparison
    fc1_grads = np.array(
        experiment_data["multi_feature"][ds]["velocity_data"]["fc1_grad"]
    )
    spurious_multi = experiment_data["multi_feature"][ds]["spurious_neurons"]
    spurious_single = experiment_data["single_feature"][ds]["spurious_neurons"]

    axes[1, col].plot(
        fc1_grads[:, spurious_multi].mean(axis=1),
        label="Spurious (multi)",
        color="red",
        linestyle="-",
        alpha=0.8,
    )
    axes[1, col].plot(
        fc1_grads[:, ~spurious_multi].mean(axis=1),
        label="Core (multi)",
        color="blue",
        linestyle="-",
        alpha=0.8,
    )
    axes[1, col].plot(
        fc1_grads[:, spurious_single].mean(axis=1),
        label="Spurious (single)",
        color="orange",
        linestyle="--",
        alpha=0.8,
    )
    axes[1, col].plot(
        fc1_grads[:, ~spurious_single].mean(axis=1),
        label="Core (single)",
        color="cyan",
        linestyle="--",
        alpha=0.8,
    )
    axes[1, col].set_title(f"Velocity Signatures")
    axes[1, col].legend(fontsize=7)
    axes[1, col].grid(True)
    axes[1, col].set_xlabel("Epoch")
    axes[1, col].set_ylabel("Gradient Norm")

    # Row 2: Worst-group accuracy comparison
    erm_worst = experiment_data["multi_feature"][ds]["erm"]["worst"]
    multi_worst = experiment_data["multi_feature"][ds]["inference"]["worst"]
    single_worst = experiment_data["single_feature"][ds]["inference"]["worst"]

    x = np.arange(3)
    bars = axes[2, col].bar(
        x, [erm_worst, multi_worst, single_worst], color=["gray", "blue", "orange"]
    )
    axes[2, col].set_xticks(x)
    axes[2, col].set_xticklabels(["ERM", "Multi-feat", "Single-feat"], rotation=15)
    axes[2, col].set_title(f"Worst-Group Accuracy")
    axes[2, col].set_ylabel("Accuracy (%)")
    axes[2, col].grid(True, axis="y")

    for bar, val in zip(bars, [erm_worst, multi_worst, single_worst]):
        axes[2, col].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{val:.1f}",
            ha="center",
            fontsize=9,
        )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_single_vs_multi_feature.png"), dpi=150)
plt.close()

# Additional comparison plot
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Separation comparison
datasets = list(datasets_info.keys())
x = np.arange(len(datasets))
width = 0.35
multi_seps = [experiment_data["multi_feature"][ds]["avg_separation"] for ds in datasets]
single_seps = [
    experiment_data["single_feature"][ds]["avg_separation"] for ds in datasets
]

axes[0].bar(
    x - width / 2, multi_seps, width, label="Multi-feature", color="blue", alpha=0.7
)
axes[0].bar(
    x + width / 2, single_seps, width, label="Single-feature", color="orange", alpha=0.7
)
axes[0].set_xticks(x)
axes[0].set_xticklabels([ds.replace("colored_", "") for ds in datasets], rotation=15)
axes[0].set_ylabel("Separation Score")
axes[0].set_title("Cluster Separation Comparison")
axes[0].legend()
axes[0].grid(True, axis="y")

# Worst-group improvement comparison
multi_improve = [
    experiment_data["multi_feature"][ds]["inference"]["worst"]
    - experiment_data["multi_feature"][ds]["erm"]["worst"]
    for ds in datasets
]
single_improve = [
    experiment_data["single_feature"][ds]["inference"]["worst"]
    - experiment_data["single_feature"][ds]["erm"]["worst"]
    for ds in datasets
]

axes[1].bar(
    x - width / 2, multi_improve, width, label="Multi-feature", color="blue", alpha=0.7
)
axes[1].bar(
    x + width / 2,
    single_improve,
    width,
    label="Single-feature",
    color="orange",
    alpha=0.7,
)
axes[1].set_xticks(x)
axes[1].set_xticklabels([ds.replace("colored_", "") for ds in datasets], rotation=15)
axes[1].set_ylabel("Worst-Group Improvement (%)")
axes[1].set_title("Worst-Group Accuracy Improvement vs ERM")
axes[1].legend()
axes[1].grid(True, axis="y")
axes[1].axhline(y=0, color="black", linestyle="-", linewidth=0.5)

# Clustering agreement
agreements = [
    experiment_data["multi_feature"][ds]["clustering_agreement"] for ds in datasets
]
axes[2].bar(x, agreements, color="green", alpha=0.7)
axes[2].set_xticks(x)
axes[2].set_xticklabels([ds.replace("colored_", "") for ds in datasets], rotation=15)
axes[2].set_ylabel("Agreement (%)")
axes[2].set_title("Clustering Method Agreement")
axes[2].grid(True, axis="y")
axes[2].set_ylim(0, 100)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_comparison_summary.png"), dpi=150)
plt.close()

# Save experiment data
np.save(
    os.path.join(working_dir, "experiment_data.npy"), experiment_data, allow_pickle=True
)
print(f"\nResults saved to {working_dir}")
print(
    "Generated files: ablation_single_vs_multi_feature.png, ablation_comparison_summary.png, experiment_data.npy"
)
