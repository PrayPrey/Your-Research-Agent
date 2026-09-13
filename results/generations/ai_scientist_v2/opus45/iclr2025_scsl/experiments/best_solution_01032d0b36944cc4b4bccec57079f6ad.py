import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from scipy import stats

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
        color_idx = (
            binary_labels[i]
            if np.random.random() < spurious_corr
            else 1 - binary_labels[i]
        )
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
        color_idx = (
            binary_labels[i]
            if np.random.random() < spurious_corr
            else 1 - binary_labels[i]
        )
        spurious_labels[i] = color_idx
        colored_images[i, 0 if color_idx == 0 else 2] = img
    return colored_images, binary_labels, spurious_labels


def create_colored_cifar10(n_samples=10000, spurious_corr=0.9):
    from datasets import load_dataset

    dataset = load_dataset("cifar10", split="train")
    indices = list(range(min(n_samples, len(dataset))))
    animals = [2, 3, 4, 5, 6, 7]
    binary_labels = np.array(
        [0 if dataset[i]["label"] in animals else 1 for i in indices], dtype=np.int64
    )
    colored_images = np.zeros((len(indices), 3, 32, 32), dtype=np.float32)
    spurious_labels = np.zeros(len(indices), dtype=np.int64)
    for idx, i in enumerate(indices):
        img = np.array(dataset[i]["img"]).astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)
        color_idx = (
            binary_labels[idx]
            if np.random.random() < spurious_corr
            else 1 - binary_labels[idx]
        )
        spurious_labels[idx] = color_idx
        colored_images[idx] = img
        bw = 4
        colored_images[idx, 0 if color_idx == 0 else 2, :bw, :] = 1.0
        colored_images[idx, 0 if color_idx == 0 else 2, -bw:, :] = 1.0
        colored_images[idx, 0 if color_idx == 0 else 2, :, :bw] = 1.0
        colored_images[idx, 0 if color_idx == 0 else 2, :, -bw:] = 1.0
    return colored_images, binary_labels, spurious_labels


class ImprovedCNN(nn.Module):
    def __init__(self, input_size=28, dropout=0.3):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(dropout)
        self.relu = nn.ReLU()
        final_size = input_size // 8
        self.fc1 = nn.Linear(128 * final_size * final_size, 128)
        self.fc2 = nn.Linear(128, 2)

    def forward(self, x):
        x = self.pool(self.relu(self.bn1(self.conv1(x))))
        x = self.pool(self.relu(self.bn2(self.conv2(x))))
        x = self.pool(self.relu(self.bn3(self.conv3(x))))
        x = x.view(x.size(0), -1)
        x = self.dropout(self.relu(self.fc1(x)))
        return self.fc2(x)


def ema_smooth(data, alpha=0.3):
    smoothed = np.zeros_like(data)
    smoothed[0] = data[0]
    for i in range(1, len(data)):
        smoothed[i] = alpha * data[i] + (1 - alpha) * smoothed[i - 1]
    return smoothed


def compute_velocity_signature(grad_history):
    n_epochs, n_neurons = grad_history.shape
    smoothed = np.array([ema_smooth(grad_history[:, i]) for i in range(n_neurons)]).T
    signatures = {
        "initial_velocity": np.mean(smoothed[:5], axis=0),
        "final_velocity": np.mean(smoothed[-10:], axis=0),
        "plateau_epoch": np.zeros(n_neurons),
        "velocity_ratio": np.zeros(n_neurons),
    }
    for i in range(n_neurons):
        initial = np.mean(smoothed[:5, i]) + 1e-8
        final = np.mean(smoothed[-10:, i]) + 1e-8
        signatures["velocity_ratio"][i] = initial / final
        threshold = initial * 0.3
        plateau_epochs = np.where(smoothed[5:, i] < threshold)[0]
        signatures["plateau_epoch"][i] = (
            plateau_epochs[0] + 5 if len(plateau_epochs) > 0 else n_epochs
        )
    return signatures, smoothed


def cohens_d(g1, g2):
    if len(g1) < 2 or len(g2) < 2:
        return 0.0
    pooled_std = np.sqrt(
        ((len(g1) - 1) * g1.var() + (len(g2) - 1) * g2.var()) / (len(g1) + len(g2) - 2)
    )
    return abs((g1.mean() - g2.mean()) / (pooled_std + 1e-8))


def train_model(config, train_loader, test_loader, input_size=28):
    torch.manual_seed(42)
    np.random.seed(42)
    model = ImprovedCNN(input_size=input_size, dropout=config.get("dropout", 0.3)).to(
        device
    )
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config["lr"],
        weight_decay=config.get("weight_decay", 1e-4),
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=config["n_epochs"]
    )

    velocity_data = {"conv1_grad": [], "conv2_grad": [], "conv3_grad": []}
    results = {"metrics": {"train": [], "val": []}, "losses": {"train": [], "val": []}}
    activations = {}

    def hook(name):
        def fn(m, i, o):
            activations[name] = o.detach()

        return fn

    model.conv1.register_forward_hook(hook("conv1"))
    model.conv2.register_forward_hook(hook("conv2"))
    model.conv3.register_forward_hook(hook("conv3"))

    for epoch in range(config["n_epochs"]):
        model.train()
        train_loss, correct, total = 0.0, 0, 0
        epoch_grads = {"conv1": [], "conv2": [], "conv3": []}

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            for name, layer in [
                ("conv1", model.conv1),
                ("conv2", model.conv2),
                ("conv3", model.conv3),
            ]:
                g = (
                    layer.weight.grad.view(layer.out_channels, -1)
                    .norm(dim=1)
                    .cpu()
                    .numpy()
                )
                epoch_grads[name].append(g)
            optimizer.step()
            train_loss += loss.item()
            _, pred = outputs.max(1)
            total += batch_y.size(0)
            correct += pred.eq(batch_y).sum().item()

        scheduler.step()
        for name in epoch_grads:
            velocity_data[f"{name}_grad"].append(np.mean(epoch_grads[name], axis=0))

        train_acc = 100.0 * correct / total
        model.eval()
        val_loss, correct, total = 0.0, 0, 0
        with torch.no_grad():
            for batch_x, batch_y in test_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item()
                _, pred = outputs.max(1)
                total += batch_y.size(0)
                correct += pred.eq(batch_y).sum().item()

        val_acc = 100.0 * correct / total
        results["losses"]["train"].append(train_loss / len(train_loader))
        results["losses"]["val"].append(val_loss / len(test_loader))
        results["metrics"]["train"].append(train_acc)
        results["metrics"]["val"].append(val_acc)
        if epoch % 10 == 0:
            print(
                f"  Epoch {epoch}: val_loss={val_loss/len(test_loader):.4f}, train_acc={train_acc:.1f}%, val_acc={val_acc:.1f}%"
            )

    # Analyze velocity signatures for conv1
    conv1_grads = np.array(velocity_data["conv1_grad"])
    signatures, smoothed_grads = compute_velocity_signature(conv1_grads)

    weights = model.conv1.weight.detach().cpu().numpy()
    channel_pref = np.abs(weights).sum(axis=(2, 3))
    selectivity = channel_pref.max(axis=1) / (channel_pref.mean(axis=1) + 1e-8)
    spurious_neurons = selectivity > np.median(selectivity)

    sep_metrics = {}
    for m in ["initial_velocity", "final_velocity", "plateau_epoch", "velocity_ratio"]:
        sep_metrics[m] = cohens_d(
            signatures[m][spurious_neurons], signatures[m][~spurious_neurons]
        )

    velocity_signature_separation = np.mean(list(sep_metrics.values()))
    results["velocity_data"] = velocity_data
    results["velocity_signatures"] = {
        "signatures": signatures,
        "smoothed_grads": smoothed_grads,
        "spurious_neurons": spurious_neurons,
        "separation_metrics": sep_metrics,
        "velocity_signature_separation": velocity_signature_separation,
    }
    return results


# Create datasets
print("Creating datasets...")
torch.manual_seed(42)
np.random.seed(42)

datasets_info = {}
for name, create_fn, size in [
    ("colored_mnist", create_colored_mnist, 28),
    ("colored_fashion_mnist", create_colored_fashion_mnist, 28),
    ("colored_cifar10", create_colored_cifar10, 32),
]:
    print(f"Loading {name}...")
    X_tr, y_tr, _ = create_fn(n_samples=10000, spurious_corr=0.95)
    X_te, y_te, _ = create_fn(n_samples=2000, spurious_corr=0.5)
    mean, std = X_tr.mean(), X_tr.std() + 1e-8
    X_tr, X_te = (X_tr - mean) / std, (X_te - mean) / std
    datasets_info[name] = {
        "train": TensorDataset(torch.FloatTensor(X_tr), torch.LongTensor(y_tr)),
        "test": TensorDataset(torch.FloatTensor(X_te), torch.LongTensor(y_te)),
        "input_size": size,
    }

config = {
    "lr": 0.001,
    "batch_size": 128,
    "n_epochs": 50,
    "dropout": 0.3,
    "weight_decay": 1e-4,
}
experiment_data = {}

for ds_name, data in datasets_info.items():
    print(f"\n--- {ds_name} ---")
    train_loader = DataLoader(
        data["train"], batch_size=config["batch_size"], shuffle=True
    )
    test_loader = DataLoader(
        data["test"], batch_size=config["batch_size"], shuffle=False
    )
    results = train_model(config, train_loader, test_loader, data["input_size"])
    experiment_data[ds_name] = results
    print(
        f"  Final: val_acc={results['metrics']['val'][-1]:.2f}%, velocity_separation={results['velocity_signatures']['velocity_signature_separation']:.4f}"
    )

# Visualization
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for col, ds in enumerate(datasets_info):
    axes[0, col].plot(experiment_data[ds]["metrics"]["val"], label="Val Acc")
    axes[0, col].set_title(f"{ds} - Accuracy")
    axes[0, col].legend()
    axes[0, col].grid(True)

    grads = experiment_data[ds]["velocity_signatures"]["smoothed_grads"]
    spur = experiment_data[ds]["velocity_signatures"]["spurious_neurons"]
    axes[1, col].plot(grads[:, spur].mean(axis=1), "r-", label="Spurious")
    axes[1, col].plot(grads[:, ~spur].mean(axis=1), "b-", label="Core")
    axes[1, col].set_title(f"{ds} - Velocity (EMA)")
    axes[1, col].legend()
    axes[1, col].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "improved_velocity_analysis.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nResults saved to {working_dir}")
