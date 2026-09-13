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

# Set seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)


# Create ColoredMNIST dataset
def create_colored_mnist(n_samples=10000, spurious_corr=0.9):
    """Create a simplified ColoredMNIST: binary classification (0-4 vs 5-9) with color as spurious feature."""
    from torchvision import datasets, transforms

    mnist = datasets.MNIST(root="./data", train=True, download=True)
    images = mnist.data.numpy()[:n_samples]
    labels = mnist.targets.numpy()[:n_samples]

    # Binary task: 0-4 -> class 0, 5-9 -> class 1
    binary_labels = (labels >= 5).astype(np.int64)

    # Create colored images (3 channels)
    colored_images = np.zeros((n_samples, 3, 28, 28), dtype=np.float32)
    spurious_labels = np.zeros(n_samples, dtype=np.int64)  # 0=red, 1=green

    for i in range(n_samples):
        img = images[i].astype(np.float32) / 255.0

        # Spurious correlation: class 0 -> red, class 1 -> green (with probability spurious_corr)
        if np.random.random() < spurious_corr:
            color = binary_labels[i]  # aligned
        else:
            color = 1 - binary_labels[i]  # misaligned

        spurious_labels[i] = color

        if color == 0:  # Red
            colored_images[i, 0] = img
            colored_images[i, 1] = img * 0.1
            colored_images[i, 2] = img * 0.1
        else:  # Green
            colored_images[i, 0] = img * 0.1
            colored_images[i, 1] = img
            colored_images[i, 2] = img * 0.1

    return colored_images, binary_labels, spurious_labels


# Simple CNN model
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(32 * 7 * 7, 64)
        self.fc2 = nn.Linear(64, 2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 32 * 7 * 7)
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x

    def get_fc1_activations(self, x):
        x = self.pool(self.relu(self.conv1(x)))
        x = self.pool(self.relu(self.conv2(x)))
        x = x.view(-1, 32 * 7 * 7)
        return self.relu(self.fc1(x))


# Create datasets
print("Creating ColoredMNIST dataset...")
X_train, y_train, spurious_train = create_colored_mnist(
    n_samples=10000, spurious_corr=0.9
)
X_test, y_test, spurious_test = create_colored_mnist(
    n_samples=2000, spurious_corr=0.5
)  # balanced test

# Convert to tensors
X_train_t = torch.FloatTensor(X_train)
y_train_t = torch.LongTensor(y_train)
spurious_train_t = torch.LongTensor(spurious_train)

X_test_t = torch.FloatTensor(X_test)
y_test_t = torch.LongTensor(y_test)
spurious_test_t = torch.LongTensor(spurious_test)

train_dataset = TensorDataset(X_train_t, y_train_t, spurious_train_t)
test_dataset = TensorDataset(X_test_t, y_test_t, spurious_test_t)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False)

# Initialize model
model = SimpleCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Tracking structures for Learning Velocity Signatures
n_epochs = 30
n_fc1_neurons = 64

# Store gradient magnitudes per neuron per epoch
gradient_history = np.zeros((n_epochs, n_fc1_neurons))
activation_history = np.zeros((n_epochs, n_fc1_neurons))

experiment_data = {
    "colored_mnist": {
        "metrics": {"train_acc": [], "val_acc": [], "val_loss": []},
        "losses": {"train": [], "val": []},
        "gradient_history": None,
        "activation_history": None,
        "neuron_spurious_correlation": None,
        "velocity_signature_separation": None,
    }
}

print("Starting training with velocity tracking...")

for epoch in range(n_epochs):
    model.train()
    train_loss = 0
    correct = 0
    total = 0

    epoch_gradients = []

    for batch_idx, (data, target, spurious) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)

        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()

        # Capture gradients for fc1 layer before optimizer step
        if model.fc1.weight.grad is not None:
            grad_per_neuron = (
                model.fc1.weight.grad.abs().mean(dim=1).detach().cpu().numpy()
            )
            epoch_gradients.append(grad_per_neuron)

        optimizer.step()

        train_loss += loss.item()
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()

    # Average gradients across batches for this epoch
    gradient_history[epoch] = np.mean(epoch_gradients, axis=0)

    train_acc = 100.0 * correct / total
    avg_train_loss = train_loss / len(train_loader)

    # Compute activations on a subset of training data
    model.eval()
    with torch.no_grad():
        sample_data = X_train_t[:1000].to(device)
        activations = model.get_fc1_activations(sample_data).cpu().numpy()
        activation_history[epoch] = activations.mean(axis=0)

    # Validation
    model.eval()
    val_loss = 0
    correct = 0
    total = 0

    with torch.no_grad():
        for data, target, spurious in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            loss = criterion(output, target)
            val_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()

    val_acc = 100.0 * correct / total
    avg_val_loss = val_loss / len(test_loader)

    experiment_data["colored_mnist"]["metrics"]["train_acc"].append(train_acc)
    experiment_data["colored_mnist"]["metrics"]["val_acc"].append(val_acc)
    experiment_data["colored_mnist"]["metrics"]["val_loss"].append(avg_val_loss)
    experiment_data["colored_mnist"]["losses"]["train"].append(avg_train_loss)
    experiment_data["colored_mnist"]["losses"]["val"].append(avg_val_loss)

    print(
        f"Epoch {epoch}: train_loss = {avg_train_loss:.4f}, validation_loss = {avg_val_loss:.4f}, train_acc = {train_acc:.2f}%, val_acc = {val_acc:.2f}%"
    )

# Compute neuron-spurious correlation to identify spurious vs core neurons
print("\nComputing neuron-spurious correlations...")
model.eval()
with torch.no_grad():
    all_activations = model.get_fc1_activations(X_train_t.to(device)).cpu().numpy()

neuron_spurious_corr = np.zeros(n_fc1_neurons)
neuron_core_corr = np.zeros(n_fc1_neurons)

for i in range(n_fc1_neurons):
    neuron_spurious_corr[i] = np.abs(
        np.corrcoef(all_activations[:, i], spurious_train)[0, 1]
    )
    neuron_core_corr[i] = np.abs(np.corrcoef(all_activations[:, i], y_train)[0, 1])

# Classify neurons: high spurious corr = spurious neuron, high core corr = core neuron
spurious_threshold = np.percentile(neuron_spurious_corr, 75)
core_threshold = np.percentile(neuron_core_corr, 75)

spurious_neurons = neuron_spurious_corr > spurious_threshold
core_neurons = (neuron_core_corr > core_threshold) & (~spurious_neurons)

print(
    f"Identified {spurious_neurons.sum()} spurious neurons and {core_neurons.sum()} core neurons"
)

# Compute Learning Velocity metrics
# Velocity = rate of change of gradient magnitude
velocity = np.diff(gradient_history, axis=0)  # (n_epochs-1, n_neurons)


# Compute velocity signature features for each neuron
def compute_velocity_features(gradient_hist, velocity):
    """Compute velocity signature features for each neuron."""
    n_neurons = gradient_hist.shape[1]
    features = {}

    # Initial velocity (first 5 epochs average)
    features["initial_velocity"] = np.mean(gradient_hist[:5], axis=0)

    # Plateau timing (epoch where gradient drops below 50% of initial)
    plateau_epoch = np.zeros(n_neurons)
    for i in range(n_neurons):
        initial = gradient_hist[:3, i].mean()
        if initial > 0:
            below_threshold = gradient_hist[:, i] < (0.5 * initial)
            if np.any(below_threshold):
                plateau_epoch[i] = np.argmax(below_threshold)
            else:
                plateau_epoch[i] = len(gradient_hist)
    features["plateau_epoch"] = plateau_epoch

    # Post-plateau gradient magnitude (last 5 epochs average)
    features["post_plateau_grad"] = np.mean(gradient_hist[-5:], axis=0)

    # Velocity decay rate (negative slope of velocity over time)
    features["velocity_decay"] = np.zeros(n_neurons)
    for i in range(n_neurons):
        if len(velocity) > 1:
            slope, _, _, _, _ = stats.linregress(
                np.arange(len(velocity)), velocity[:, i]
            )
            features["velocity_decay"][i] = -slope

    return features


velocity_features = compute_velocity_features(gradient_history, velocity)


# Compute velocity signature separation (Cohen's d)
def cohens_d(group1, group2):
    """Compute Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return (np.mean(group1) - np.mean(group2)) / pooled_std


# Compute separation for each velocity feature
separations = {}
for feature_name, feature_values in velocity_features.items():
    spurious_vals = feature_values[spurious_neurons]
    core_vals = feature_values[core_neurons]
    d = cohens_d(spurious_vals, core_vals)
    separations[feature_name] = d
    print(f"{feature_name}: Cohen's d = {d:.4f}")

# Overall velocity signature separation (average absolute Cohen's d across features)
velocity_signature_separation = np.mean([np.abs(d) for d in separations.values()])
print(f"\n=== velocity_signature_separation = {velocity_signature_separation:.4f} ===")

# Store results
experiment_data["colored_mnist"]["gradient_history"] = gradient_history
experiment_data["colored_mnist"]["activation_history"] = activation_history
experiment_data["colored_mnist"]["neuron_spurious_correlation"] = neuron_spurious_corr
experiment_data["colored_mnist"]["neuron_core_correlation"] = neuron_core_corr
experiment_data["colored_mnist"]["velocity_features"] = velocity_features
experiment_data["colored_mnist"]["separations"] = separations
experiment_data["colored_mnist"][
    "velocity_signature_separation"
] = velocity_signature_separation

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Visualization
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Plot 1: Gradient history for spurious vs core neurons
ax = axes[0, 0]
epochs = np.arange(n_epochs)
if spurious_neurons.sum() > 0:
    ax.plot(
        epochs,
        gradient_history[:, spurious_neurons].mean(axis=1),
        "r-",
        label="Spurious neurons",
        linewidth=2,
    )
    ax.fill_between(
        epochs,
        gradient_history[:, spurious_neurons].mean(axis=1)
        - gradient_history[:, spurious_neurons].std(axis=1),
        gradient_history[:, spurious_neurons].mean(axis=1)
        + gradient_history[:, spurious_neurons].std(axis=1),
        alpha=0.3,
        color="red",
    )
if core_neurons.sum() > 0:
    ax.plot(
        epochs,
        gradient_history[:, core_neurons].mean(axis=1),
        "b-",
        label="Core neurons",
        linewidth=2,
    )
    ax.fill_between(
        epochs,
        gradient_history[:, core_neurons].mean(axis=1)
        - gradient_history[:, core_neurons].std(axis=1),
        gradient_history[:, core_neurons].mean(axis=1)
        + gradient_history[:, core_neurons].std(axis=1),
        alpha=0.3,
        color="blue",
    )
ax.set_xlabel("Epoch")
ax.set_ylabel("Gradient Magnitude")
ax.set_title("Gradient History: Spurious vs Core Neurons")
ax.legend()

# Plot 2: Activation history
ax = axes[0, 1]
if spurious_neurons.sum() > 0:
    ax.plot(
        epochs,
        activation_history[:, spurious_neurons].mean(axis=1),
        "r-",
        label="Spurious neurons",
        linewidth=2,
    )
if core_neurons.sum() > 0:
    ax.plot(
        epochs,
        activation_history[:, core_neurons].mean(axis=1),
        "b-",
        label="Core neurons",
        linewidth=2,
    )
ax.set_xlabel("Epoch")
ax.set_ylabel("Mean Activation")
ax.set_title("Activation History: Spurious vs Core Neurons")
ax.legend()

# Plot 3: Plateau epoch distribution
ax = axes[0, 2]
if spurious_neurons.sum() > 0 and core_neurons.sum() > 0:
    ax.hist(
        velocity_features["plateau_epoch"][spurious_neurons],
        alpha=0.6,
        label="Spurious",
        color="red",
        bins=10,
    )
    ax.hist(
        velocity_features["plateau_epoch"][core_neurons],
        alpha=0.6,
        label="Core",
        color="blue",
        bins=10,
    )
ax.set_xlabel("Plateau Epoch")
ax.set_ylabel("Count")
ax.set_title(f"Plateau Timing (Cohen's d = {separations['plateau_epoch']:.2f})")
ax.legend()

# Plot 4: Initial velocity distribution
ax = axes[1, 0]
if spurious_neurons.sum() > 0 and core_neurons.sum() > 0:
    ax.hist(
        velocity_features["initial_velocity"][spurious_neurons],
        alpha=0.6,
        label="Spurious",
        color="red",
        bins=10,
    )
    ax.hist(
        velocity_features["initial_velocity"][core_neurons],
        alpha=0.6,
        label="Core",
        color="blue",
        bins=10,
    )
ax.set_xlabel("Initial Velocity")
ax.set_ylabel("Count")
ax.set_title(f"Initial Velocity (Cohen's d = {separations['initial_velocity']:.2f})")
ax.legend()

# Plot 5: Training/validation curves
ax = axes[1, 1]
ax.plot(
    experiment_data["colored_mnist"]["metrics"]["train_acc"],
    label="Train Acc",
    color="green",
)
ax.plot(
    experiment_data["colored_mnist"]["metrics"]["val_acc"],
    label="Val Acc",
    color="orange",
)
ax.set_xlabel("Epoch")
ax.set_ylabel("Accuracy (%)")
ax.set_title("Training Progress")
ax.legend()

# Plot 6: Neuron correlation scatter
ax = axes[1, 2]
ax.scatter(neuron_spurious_corr, neuron_core_corr, alpha=0.6)
ax.axvline(spurious_threshold, color="red", linestyle="--", label="Spurious threshold")
ax.axhline(core_threshold, color="blue", linestyle="--", label="Core threshold")
ax.set_xlabel("Spurious Correlation")
ax.set_ylabel("Core Correlation")
ax.set_title("Neuron Correlation Map")
ax.legend()

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "lvs_coloredmnist_results.png"), dpi=150)
plt.close()

print(f"\nResults saved to {working_dir}")
print(f"Final velocity_signature_separation: {velocity_signature_separation:.4f}")
