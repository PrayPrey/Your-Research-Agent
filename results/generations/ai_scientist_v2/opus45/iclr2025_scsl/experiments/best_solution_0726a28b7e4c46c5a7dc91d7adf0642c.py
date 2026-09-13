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

    def forward(self, x, return_features=False, neuron_weights=None):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = x.view(x.size(0), -1)
        features = self.relu(self.fc1(x))
        if neuron_weights is not None:
            features = features * neuron_weights.to(features.device)
        x = self.dropout(features)
        x = self.fc2(x)
        return (x, features) if return_features else x


def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    pooled_std = np.sqrt(
        ((n1 - 1) * np.var(group1) + (n2 - 1) * np.var(group2)) / (n1 + n2 - 2)
    )
    return (np.mean(group1) - np.mean(group2)) / (pooled_std + 1e-8)


def cluster_neurons_by_velocity(grad_history, n_clusters=2):
    n_epochs, n_neurons = grad_history.shape
    features = np.zeros((n_neurons, 4))
    for i in range(n_neurons):
        features[i, 0] = grad_history[:5, i].mean()
        features[i, 1] = grad_history[-10:, i].mean()
        decay_rate = (features[i, 0] - features[i, 1]) / (features[i, 0] + 1e-8)
        features[i, 2] = decay_rate
        threshold = 0.1 * grad_history[:, i].max()
        plateau_idx = np.where(grad_history[:, i] < threshold)[0]
        features[i, 3] = plateau_idx[0] if len(plateau_idx) > 0 else n_epochs
    features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features)
    cluster_plateau_means = [features[labels == c, 3].mean() for c in range(n_clusters)]
    spurious_cluster = np.argmin(cluster_plateau_means)
    spurious_neurons = labels == spurious_cluster
    return spurious_neurons, ~spurious_neurons, features[:, 3]


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


def train_with_velocity_tracking(
    config, train_loader, test_loader, test_y, test_s, input_size=28
):
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
        avg_acc, worst_group, _ = evaluate_with_groups(
            model, test_loader, test_y, test_s
        )

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

        if patience_counter >= config["patience"]:
            break

    if best_model_state:
        model.load_state_dict({k: v.to(device) for k, v in best_model_state.items()})

    fc1_grads = np.array(velocity_data["fc1_grad"])
    spurious_neurons, core_neurons, plateau_epochs = cluster_neurons_by_velocity(
        fc1_grads
    )

    separation_metrics = {
        "plateau_epoch": abs(
            cohens_d(plateau_epochs[spurious_neurons], plateau_epochs[core_neurons])
        ),
        "initial_velocity": abs(
            cohens_d(
                fc1_grads[:5].mean(axis=0)[spurious_neurons],
                fc1_grads[:5].mean(axis=0)[core_neurons],
            )
        ),
        "final_velocity": abs(
            cohens_d(
                fc1_grads[-10:].mean(axis=0)[spurious_neurons],
                fc1_grads[-10:].mean(axis=0)[core_neurons],
            )
        ),
    }
    velocity_signature_separation = np.mean(list(separation_metrics.values()))

    neuron_weights = torch.ones(model.n_hidden)
    neuron_weights[spurious_neurons] = config.get("reweight_factor", 0.3)

    avg_acc_erm, worst_erm, groups_erm = evaluate_with_groups(
        model, test_loader, test_y, test_s
    )
    avg_acc_lvs, worst_lvs, groups_lvs = evaluate_with_groups(
        model, test_loader, test_y, test_s, neuron_weights
    )

    results["velocity_data"] = velocity_data
    results["velocity_signatures"] = {
        "plateau_epochs": plateau_epochs,
        "spurious_neurons": spurious_neurons,
        "core_neurons": core_neurons,
        "separation_metrics": separation_metrics,
        "velocity_signature_separation": velocity_signature_separation,
    }
    results["inference"] = {
        "erm": {"avg": avg_acc_erm, "worst": worst_erm, "groups": groups_erm},
        "lvs": {"avg": avg_acc_lvs, "worst": worst_lvs, "groups": groups_lvs},
    }
    results["model"] = model
    return results


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

# Ablation study: Dropout rates
dropout_rates = [0.0, 0.2, 0.4, 0.6, 0.8]
base_config = {
    "lr": 0.001,
    "batch_size": 128,
    "n_epochs": 60,
    "weight_decay": 5e-4,
    "seed": 42,
    "patience": 15,
    "reweight_factor": 0.3,
}

experiment_data = {}
for dropout_rate in dropout_rates:
    dropout_key = f"dropout_{dropout_rate}"
    experiment_data[dropout_key] = {}
    print(f"\n{'='*60}\nAblation: Dropout Rate = {dropout_rate}\n{'='*60}")

    config = base_config.copy()
    config["dropout"] = dropout_rate

    for dataset_name, data_info in datasets_info.items():
        print(f"\n  Dataset: {dataset_name}")
        train_loader = DataLoader(
            data_info["train"], batch_size=config["batch_size"], shuffle=True
        )
        test_loader = DataLoader(
            data_info["test"], batch_size=config["batch_size"], shuffle=False
        )

        results = train_with_velocity_tracking(
            config,
            train_loader,
            test_loader,
            data_info["test_y"],
            data_info["test_s"],
            data_info["input_size"],
        )
        del results["model"]
        experiment_data[dropout_key][dataset_name] = results

        sep = results["velocity_signatures"]["velocity_signature_separation"]
        erm_worst = results["inference"]["erm"]["worst"]
        lvs_worst = results["inference"]["lvs"]["worst"]
        improvement = lvs_worst - erm_worst
        print(
            f"    separation={sep:.4f}, ERM_worst={erm_worst:.1f}%, LVS_worst={lvs_worst:.1f}%, improvement={improvement:+.1f}%"
        )

# Summary
print("\n" + "=" * 70 + "\nABLATION STUDY SUMMARY: Dropout Rate Impact\n" + "=" * 70)
for dataset_name in datasets_info.keys():
    print(f"\n{dataset_name}:")
    print(
        f"{'Dropout':<10} {'Separation':<12} {'ERM_worst':<12} {'LVS_worst':<12} {'Improvement':<12}"
    )
    print("-" * 58)
    for dropout_rate in dropout_rates:
        dropout_key = f"dropout_{dropout_rate}"
        res = experiment_data[dropout_key][dataset_name]
        sep = res["velocity_signatures"]["velocity_signature_separation"]
        erm_worst = res["inference"]["erm"]["worst"]
        lvs_worst = res["inference"]["lvs"]["worst"]
        improvement = lvs_worst - erm_worst
        print(
            f"{dropout_rate:<10.1f} {sep:<12.4f} {erm_worst:<12.1f} {lvs_worst:<12.1f} {improvement:<+12.1f}"
        )

# Plotting
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
dataset_names = list(datasets_info.keys())

for col, dataset_name in enumerate(dataset_names):
    separations = []
    erm_worsts = []
    lvs_worsts = []

    for dropout_rate in dropout_rates:
        dropout_key = f"dropout_{dropout_rate}"
        res = experiment_data[dropout_key][dataset_name]
        separations.append(res["velocity_signatures"]["velocity_signature_separation"])
        erm_worsts.append(res["inference"]["erm"]["worst"])
        lvs_worsts.append(res["inference"]["lvs"]["worst"])

    # Row 0: Velocity Signature Separation vs Dropout
    axes[0, col].plot(dropout_rates, separations, "bo-", linewidth=2, markersize=8)
    axes[0, col].set_xlabel("Dropout Rate")
    axes[0, col].set_ylabel("Velocity Signature Separation")
    axes[0, col].set_title(f"{dataset_name}\nSeparation vs Dropout")
    axes[0, col].grid(True, alpha=0.3)

    # Row 1: Worst-Group Accuracy vs Dropout
    axes[1, col].plot(
        dropout_rates, erm_worsts, "r^-", label="ERM", linewidth=2, markersize=8
    )
    axes[1, col].plot(
        dropout_rates, lvs_worsts, "gs-", label="LVS", linewidth=2, markersize=8
    )
    axes[1, col].set_xlabel("Dropout Rate")
    axes[1, col].set_ylabel("Worst-Group Accuracy (%)")
    axes[1, col].set_title(f"{dataset_name}\nWorst-Group Acc vs Dropout")
    axes[1, col].legend()
    axes[1, col].grid(True, alpha=0.3)

    # Row 2: Improvement vs Dropout
    improvements = [lvs - erm for lvs, erm in zip(lvs_worsts, erm_worsts)]
    colors = ["green" if imp > 0 else "red" for imp in improvements]
    axes[2, col].bar(dropout_rates, improvements, color=colors, width=0.15, alpha=0.7)
    axes[2, col].axhline(y=0, color="black", linestyle="-", linewidth=0.5)
    axes[2, col].set_xlabel("Dropout Rate")
    axes[2, col].set_ylabel("LVS Improvement (%)")
    axes[2, col].set_title(f"{dataset_name}\nLVS Improvement vs Dropout")
    axes[2, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dropout_ablation_analysis.png"), dpi=150)
plt.close()

# Additional plot: Velocity signatures comparison for different dropout rates
fig2, axes2 = plt.subplots(len(dropout_rates), 3, figsize=(15, 4 * len(dropout_rates)))
for row, dropout_rate in enumerate(dropout_rates):
    dropout_key = f"dropout_{dropout_rate}"
    for col, dataset_name in enumerate(dataset_names):
        res = experiment_data[dropout_key][dataset_name]
        fc1_grads = np.array(res["velocity_data"]["fc1_grad"])
        spurious = res["velocity_signatures"]["spurious_neurons"]

        axes2[row, col].plot(
            fc1_grads[:, spurious].mean(axis=1),
            label="Spurious",
            color="red",
            alpha=0.8,
        )
        axes2[row, col].plot(
            fc1_grads[:, ~spurious].mean(axis=1), label="Core", color="blue", alpha=0.8
        )
        axes2[row, col].set_title(f"{dataset_name} - Dropout={dropout_rate}")
        axes2[row, col].set_xlabel("Epoch")
        axes2[row, col].set_ylabel("Gradient Norm")
        axes2[row, col].legend(fontsize=8)
        axes2[row, col].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dropout_velocity_signatures.png"), dpi=150)
plt.close()

# Save experiment data
np.save(
    os.path.join(working_dir, "experiment_data.npy"), experiment_data, allow_pickle=True
)
print(f"\nResults saved to {working_dir}")
print(
    "Files saved: dropout_ablation_analysis.png, dropout_velocity_signatures.png, experiment_data.npy"
)
