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

torch.manual_seed(42)
np.random.seed(42)


def create_colored_mnist(n_samples=10000, spurious_corr=0.9):
    from torchvision import datasets, transforms

    mnist = datasets.MNIST(root="./data", train=True, download=True)
    images = mnist.data.numpy()[:n_samples]
    labels = mnist.targets.numpy()[:n_samples]
    binary_labels = (labels >= 5).astype(np.int64)
    colored_images = np.zeros((n_samples, 3, 28, 28), dtype=np.float32)
    spurious_labels = np.zeros(n_samples, dtype=np.int64)
    for i in range(n_samples):
        img = images[i].astype(np.float32) / 255.0
        if np.random.random() < spurious_corr:
            color_idx = binary_labels[i]
        else:
            color_idx = 1 - binary_labels[i]
        spurious_labels[i] = color_idx
        if color_idx == 0:
            colored_images[i, 0] = img
        else:
            colored_images[i, 1] = img
    return colored_images, binary_labels, spurious_labels


print("Creating ColoredMNIST dataset...")
np.random.seed(42)
X_train, y_train, spurious_train = create_colored_mnist(
    n_samples=10000, spurious_corr=0.95
)
np.random.seed(43)
X_test, y_test, spurious_test = create_colored_mnist(n_samples=2000, spurious_corr=0.5)

train_mean, train_std = X_train.mean(), X_train.std() + 1e-8
X_train = (X_train - train_mean) / train_std
X_test = (X_test - train_mean) / train_std

train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.LongTensor(y_train))
test_dataset = TensorDataset(torch.FloatTensor(X_test), torch.LongTensor(y_test))


class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.fc1 = nn.Linear(32 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, 2)
        self.pool = nn.MaxPool2d(2, 2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def compute_velocity_signature(grad_history, act_history):
    n_epochs, n_neurons = grad_history.shape
    signatures = {
        "initial_velocity": np.mean(grad_history[:5], axis=0),
        "final_velocity": np.mean(grad_history[-10:], axis=0),
        "plateau_epoch": np.zeros(n_neurons),
        "velocity_decay_rate": np.zeros(n_neurons),
        "activation_growth": np.zeros(n_neurons),
    }
    for i in range(n_neurons):
        initial_grad = np.mean(grad_history[:3, i])
        threshold = initial_grad * 0.5
        plateau_epochs = np.where(grad_history[:, i] < threshold)[0]
        signatures["plateau_epoch"][i] = (
            plateau_epochs[0] if len(plateau_epochs) > 0 else n_epochs
        )
        epochs = np.arange(n_epochs)
        slope, _, _, _, _ = stats.linregress(epochs, grad_history[:, i])
        signatures["velocity_decay_rate"][i] = slope
        signatures["activation_growth"][i] = act_history[-1, i] - act_history[0, i]
    return signatures


def cohens_d(group1, group2):
    n1, n2 = len(group1), len(group2)
    var1, var2 = group1.var(), group2.var()
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (group1.mean() - group2.mean()) / (pooled_std + 1e-8)


def train_with_batch_size(batch_size, n_epochs=50):
    torch.manual_seed(42)
    np.random.seed(42)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

    model = SimpleCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    velocity_data = {"conv1_grad_norms": [], "conv1_activations": []}
    results = {"metrics": {"train": [], "val": []}, "losses": {"train": [], "val": []}}

    activations = {}

    def get_activation(name):
        def hook(model, input, output):
            activations[name] = output.detach()

        return hook

    model.conv1.register_forward_hook(get_activation("conv1"))

    print(f"\nTraining with batch_size={batch_size}...")

    for epoch in range(n_epochs):
        model.train()
        train_loss, correct, total = 0.0, 0, 0
        epoch_conv1_grads, epoch_conv1_acts = [], []

        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()

            conv1_grad = model.conv1.weight.grad.view(16, -1).norm(dim=1).cpu().numpy()
            epoch_conv1_grads.append(conv1_grad)
            epoch_conv1_acts.append(
                activations["conv1"].mean(dim=(0, 2, 3)).cpu().numpy()
            )

            optimizer.step()
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            total += batch_y.size(0)
            correct += predicted.eq(batch_y).sum().item()

        velocity_data["conv1_grad_norms"].append(np.mean(epoch_conv1_grads, axis=0))
        velocity_data["conv1_activations"].append(np.mean(epoch_conv1_acts, axis=0))

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

        results["losses"]["train"].append(avg_train_loss)
        results["losses"]["val"].append(avg_val_loss)
        results["metrics"]["train"].append(train_acc)
        results["metrics"]["val"].append(val_acc)

        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: val_loss={avg_val_loss:.4f}, train_acc={train_acc:.2f}%, val_acc={val_acc:.2f}%"
            )

    conv1_grads = np.array(velocity_data["conv1_grad_norms"])
    conv1_acts = np.array(velocity_data["conv1_activations"])
    conv1_signatures = compute_velocity_signature(conv1_grads, conv1_acts)

    conv1_weights = model.conv1.weight.detach().cpu().numpy()
    channel_preference = np.abs(conv1_weights).sum(axis=(2, 3))
    channel_max = channel_preference.max(axis=1)
    channel_mean = channel_preference.mean(axis=1)
    color_selectivity = channel_max / (channel_mean + 1e-8)

    median_selectivity = np.median(color_selectivity)
    spurious_neurons = color_selectivity > median_selectivity
    core_neurons = ~spurious_neurons

    separation_metrics = {}
    for metric_name in [
        "initial_velocity",
        "final_velocity",
        "plateau_epoch",
        "velocity_decay_rate",
    ]:
        spurious_values = conv1_signatures[metric_name][spurious_neurons]
        core_values = conv1_signatures[metric_name][core_neurons]
        d = cohens_d(spurious_values, core_values)
        separation_metrics[metric_name] = abs(d)

    velocity_signature_separation = np.mean(list(separation_metrics.values()))

    results["velocity_data"] = velocity_data
    results["conv1_signatures"] = conv1_signatures
    results["spurious_neurons"] = spurious_neurons
    results["core_neurons"] = core_neurons
    results["separation_metrics"] = separation_metrics
    results["velocity_signature_separation"] = velocity_signature_separation

    return results


# Hyperparameter tuning for batch size
batch_sizes = [32, 128]
experiment_data = {}

for bs in batch_sizes:
    key = f"batch_size_{bs}"
    results = train_with_batch_size(bs)
    experiment_data[key] = {"colored_mnist": results}
    print(f"\n=== Batch Size {bs} ===")
    print(f"Final train acc: {results['metrics']['train'][-1]:.2f}%")
    print(f"Final val acc: {results['metrics']['val'][-1]:.2f}%")
    print(
        f"velocity_signature_separation: {results['velocity_signature_separation']:.4f}"
    )
    for metric, val in results["separation_metrics"].items():
        print(f"  {metric}: {val:.4f}")

# Visualization
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

for idx, bs in enumerate(batch_sizes):
    key = f"batch_size_{bs}"
    data = experiment_data[key]["colored_mnist"]
    conv1_grads = np.array(data["velocity_data"]["conv1_grad_norms"])
    conv1_acts = np.array(data["velocity_data"]["conv1_activations"])
    spurious_neurons = data["spurious_neurons"]
    core_neurons = data["core_neurons"]

    ax = axes[idx, 0]
    spurious_grads = conv1_grads[:, spurious_neurons].mean(axis=1)
    core_grads = conv1_grads[:, core_neurons].mean(axis=1)
    ax.plot(spurious_grads, label="Spurious", color="red")
    ax.plot(core_grads, label="Core", color="blue")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Mean Gradient Norm")
    ax.set_title(f"Batch Size {bs}: Learning Velocity")
    ax.legend()
    ax.grid(True)

    ax = axes[idx, 1]
    spurious_acts = conv1_acts[:, spurious_neurons].mean(axis=1)
    core_acts = conv1_acts[:, core_neurons].mean(axis=1)
    ax.plot(spurious_acts, label="Spurious", color="red")
    ax.plot(core_acts, label="Core", color="blue")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Mean Activation")
    ax.set_title(f"Batch Size {bs}: Activation Growth")
    ax.legend()
    ax.grid(True)

    ax = axes[idx, 2]
    ax.plot(data["metrics"]["train"], label="Train Acc")
    ax.plot(data["metrics"]["val"], label="Val Acc")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title(f"Batch Size {bs}: Training Progress")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "batch_size_tuning_analysis.png"), dpi=150)
plt.close()

# Summary comparison plot
fig, ax = plt.subplots(figsize=(8, 6))
bs_labels = [str(bs) for bs in batch_sizes]
separations = [
    experiment_data[f"batch_size_{bs}"]["colored_mnist"][
        "velocity_signature_separation"
    ]
    for bs in batch_sizes
]
val_accs = [
    experiment_data[f"batch_size_{bs}"]["colored_mnist"]["metrics"]["val"][-1]
    for bs in batch_sizes
]

x = np.arange(len(batch_sizes))
width = 0.35
ax.bar(x - width / 2, separations, width, label="Velocity Signature Separation")
ax.bar(x + width / 2, [v / 100 for v in val_accs], width, label="Val Acc (normalized)")
ax.set_xlabel("Batch Size")
ax.set_ylabel("Value")
ax.set_title("Batch Size Comparison")
ax.set_xticks(x)
ax.set_xticklabels(bs_labels)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "batch_size_comparison.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\n=== Summary ===")
for bs in batch_sizes:
    key = f"batch_size_{bs}"
    data = experiment_data[key]["colored_mnist"]
    print(
        f"Batch Size {bs}: VSS={data['velocity_signature_separation']:.4f}, Val Acc={data['metrics']['val'][-1]:.2f}%"
    )
print(f"\nResults saved to {working_dir}")
