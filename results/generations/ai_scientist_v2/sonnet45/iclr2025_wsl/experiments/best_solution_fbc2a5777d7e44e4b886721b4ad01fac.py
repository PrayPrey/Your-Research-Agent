import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, TensorDataset
import torchvision
import torchvision.transforms as transforms
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from tqdm import tqdm

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Set random seeds
torch.manual_seed(42)
np.random.seed(42)

experiment_data = {
    "with_augmentation": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "functional_similarity": [],
        "epochs": [],
    },
    "without_augmentation": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "functional_similarity": [],
        "epochs": [],
    },
}


# Simple MLP architecture for CIFAR-10
class SimpleMLP(nn.Module):
    def __init__(self, hidden_dim=128):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(3072, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 10)

    def forward(self, x):
        x = x.view(x.size(0), -1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# Load CIFAR-10
print("Loading CIFAR-10...")
transform = transforms.Compose(
    [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
)

trainset = torchvision.datasets.CIFAR10(
    root="./data", train=True, download=True, transform=transform
)
testset = torchvision.datasets.CIFAR10(
    root="./data", train=False, download=True, transform=transform
)

# Use subset for faster training
train_subset = torch.utils.data.Subset(trainset, range(5000))
test_subset = torch.utils.data.Subset(testset, range(1000))

train_loader = DataLoader(train_subset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_subset, batch_size=128, shuffle=False)


# Function to train a single model
def train_single_model(hidden_dim=128, epochs=10):
    model = SimpleMLP(hidden_dim=hidden_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    for epoch in range(epochs):
        model.train()
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

    # Evaluate accuracy
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    accuracy = 100 * correct / total
    return model, accuracy


# Create model zoo
print("Creating model zoo...")
num_models = 50  # Small zoo for low-data regime
model_zoo = []
accuracies = []

for i in tqdm(range(num_models), desc="Training models"):
    model, acc = train_single_model(hidden_dim=128, epochs=5)
    model_zoo.append(model)
    accuracies.append(acc)

print(f"Model zoo created with {num_models} models")
print(f"Accuracy range: {min(accuracies):.2f}% - {max(accuracies):.2f}%")


# Symmetry-aware augmentation operations
def permute_neurons(model, layer_idx=1):
    """Permute neurons in a hidden layer (preserving function)"""
    augmented_model = SimpleMLP(hidden_dim=128).to(device)
    augmented_model.load_state_dict(model.state_dict())

    if layer_idx == 1:
        # Permute hidden layer 1
        hidden_dim = augmented_model.fc1.weight.shape[0]
        perm = torch.randperm(hidden_dim)

        # Permute outgoing weights of fc1
        augmented_model.fc1.weight.data = augmented_model.fc1.weight.data[perm, :]
        augmented_model.fc1.bias.data = augmented_model.fc1.bias.data[perm]

        # Permute incoming weights of fc2
        augmented_model.fc2.weight.data = augmented_model.fc2.weight.data[:, perm]

    return augmented_model


def scale_weights(model, scale_factor=1.1):
    """Scale weights with compensation (preserving function with ReLU)"""
    augmented_model = SimpleMLP(hidden_dim=128).to(device)
    augmented_model.load_state_dict(model.state_dict())

    # Scale fc1 output weights and compensate in fc2 input weights
    augmented_model.fc1.weight.data *= scale_factor
    augmented_model.fc1.bias.data *= scale_factor
    augmented_model.fc2.weight.data /= scale_factor

    return augmented_model


def sign_flip_weights(model):
    """Sign flip with compensation for ReLU networks"""
    augmented_model = SimpleMLP(hidden_dim=128).to(device)
    augmented_model.load_state_dict(model.state_dict())

    # Randomly flip signs of some neurons
    hidden_dim = augmented_model.fc1.weight.shape[0]
    flip_mask = (torch.rand(hidden_dim) > 0.5).float() * 2 - 1  # -1 or 1
    flip_mask = flip_mask.to(device)

    # Apply sign flip to fc1 output
    augmented_model.fc1.weight.data *= flip_mask.unsqueeze(1)
    augmented_model.fc1.bias.data *= flip_mask

    # Compensate in fc2 input
    augmented_model.fc2.weight.data *= flip_mask.unsqueeze(0)

    return augmented_model


def apply_random_augmentation(model):
    """Randomly apply one of the symmetry operations"""
    aug_type = np.random.choice(["permute", "scale", "sign_flip"])
    if aug_type == "permute":
        return permute_neurons(model)
    elif aug_type == "scale":
        scale = np.random.uniform(0.9, 1.1)
        return scale_weights(model, scale)
    else:
        return sign_flip_weights(model)


# Compute functional similarity
def compute_functional_similarity(model1, model2, data_loader):
    """Compute correlation between model predictions"""
    model1.eval()
    model2.eval()

    all_outputs1 = []
    all_outputs2 = []

    with torch.no_grad():
        for inputs, _ in data_loader:
            inputs = inputs.to(device)
            outputs1 = model1(inputs)
            outputs2 = model2(inputs)
            all_outputs1.append(outputs1.cpu().numpy())
            all_outputs2.append(outputs2.cpu().numpy())

    all_outputs1 = np.concatenate(all_outputs1, axis=0)
    all_outputs2 = np.concatenate(all_outputs2, axis=0)

    # Compute mean correlation across all output dimensions
    correlations = []
    for i in range(all_outputs1.shape[1]):
        corr, _ = pearsonr(all_outputs1[:, i], all_outputs2[:, i])
        correlations.append(corr)

    return np.mean(correlations)


# Test augmentation quality
print("\nTesting augmentation functional similarity...")
test_model = model_zoo[0]
aug_similarities = []

for aug_type, aug_func in [
    ("permute", lambda m: permute_neurons(m)),
    ("scale", lambda m: scale_weights(m, 1.05)),
    ("sign_flip", lambda m: sign_flip_weights(m)),
]:
    aug_model = aug_func(test_model)
    similarity = compute_functional_similarity(test_model, aug_model, test_loader)
    aug_similarities.append(similarity)
    print(f"{aug_type} functional similarity: {similarity:.4f}")


# Extract weight features from models
def extract_weight_features(model):
    """Extract flattened weights as features"""
    features = []
    for param in model.parameters():
        features.append(param.data.cpu().flatten())
    return torch.cat(features).numpy()


# Create weight-space dataset
print("\nCreating weight-space dataset...")
X = []
y = []

for model, acc in zip(model_zoo, accuracies):
    features = extract_weight_features(model)
    X.append(features)
    y.append(acc)

X = np.array(X)
y = np.array(y)

print(f"Weight-space dataset shape: {X.shape}")

# Split into train/val
split_idx = int(0.7 * len(X))
X_train, X_val = X[:split_idx], X[split_idx:]
y_train, y_val = y[:split_idx], y[split_idx:]

print(f"Train: {X_train.shape}, Val: {X_val.shape}")


# Simple property predictor (MLP)
class PropertyPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim=256):
        super(PropertyPredictor, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)
        self.fc3 = nn.Linear(hidden_dim, 1)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return x


# Train property predictor WITHOUT augmentation
print("\n" + "=" * 50)
print("Training WITHOUT augmentation...")
print("=" * 50)

X_train_tensor = torch.FloatTensor(X_train).to(device)
y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1).to(device)
X_val_tensor = torch.FloatTensor(X_val).to(device)
y_val_tensor = torch.FloatTensor(y_val).unsqueeze(1).to(device)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader_pred = DataLoader(train_dataset, batch_size=8, shuffle=True)

predictor_no_aug = PropertyPredictor(X_train.shape[1]).to(device)
optimizer = torch.optim.Adam(predictor_no_aug.parameters(), lr=0.0001)
criterion = nn.MSELoss()

epochs = 50
for epoch in range(epochs):
    predictor_no_aug.train()
    train_loss = 0
    for batch_X, batch_y in train_loader_pred:
        optimizer.zero_grad()
        outputs = predictor_no_aug(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    train_loss /= len(train_loader_pred)

    # Validation
    predictor_no_aug.eval()
    with torch.no_grad():
        val_outputs = predictor_no_aug(X_val_tensor)
        val_loss = criterion(val_outputs, y_val_tensor).item()
        val_mae = torch.mean(torch.abs(val_outputs - y_val_tensor)).item()

    experiment_data["without_augmentation"]["losses"]["train"].append(train_loss)
    experiment_data["without_augmentation"]["losses"]["val"].append(val_loss)
    experiment_data["without_augmentation"]["metrics"]["val"].append(val_mae)
    experiment_data["without_augmentation"]["epochs"].append(epoch)

    if epoch % 10 == 0:
        print(
            f"Epoch {epoch}: train_loss = {train_loss:.4f}, validation_loss = {val_loss:.4f}, val_MAE = {val_mae:.4f}"
        )

# Train property predictor WITH augmentation
print("\n" + "=" * 50)
print("Training WITH augmentation...")
print("=" * 50)

# Create augmented dataset
X_train_aug = [X_train]
y_train_aug = [y_train]

print("Generating augmented samples...")
for idx, model in enumerate(tqdm(model_zoo[:split_idx])):
    # Generate 4 augmented versions per model
    for _ in range(4):
        aug_model = apply_random_augmentation(model)
        aug_features = extract_weight_features(aug_model)
        X_train_aug.append(aug_features.reshape(1, -1))
        y_train_aug.append([accuracies[idx]])

        # Compute functional similarity for this augmentation
        func_sim = compute_functional_similarity(model, aug_model, test_loader)
        experiment_data["with_augmentation"]["functional_similarity"].append(func_sim)

X_train_aug = np.concatenate(X_train_aug, axis=0)
y_train_aug = np.concatenate(y_train_aug, axis=0)

print(f"Augmented training set size: {X_train_aug.shape}")

X_train_aug_tensor = torch.FloatTensor(X_train_aug).to(device)
y_train_aug_tensor = torch.FloatTensor(y_train_aug).unsqueeze(1).to(device)

train_dataset_aug = TensorDataset(X_train_aug_tensor, y_train_aug_tensor)
train_loader_aug = DataLoader(train_dataset_aug, batch_size=32, shuffle=True)

predictor_with_aug = PropertyPredictor(X_train.shape[1]).to(device)
optimizer_aug = torch.optim.Adam(predictor_with_aug.parameters(), lr=0.0001)

for epoch in range(epochs):
    predictor_with_aug.train()
    train_loss = 0
    for batch_X, batch_y in train_loader_aug:
        optimizer_aug.zero_grad()
        outputs = predictor_with_aug(batch_X)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer_aug.step()
        train_loss += loss.item()

    train_loss /= len(train_loader_aug)

    # Validation
    predictor_with_aug.eval()
    with torch.no_grad():
        val_outputs = predictor_with_aug(X_val_tensor)
        val_loss = criterion(val_outputs, y_val_tensor).item()
        val_mae = torch.mean(torch.abs(val_outputs - y_val_tensor)).item()

    experiment_data["with_augmentation"]["losses"]["train"].append(train_loss)
    experiment_data["with_augmentation"]["losses"]["val"].append(val_loss)
    experiment_data["with_augmentation"]["metrics"]["val"].append(val_mae)
    experiment_data["with_augmentation"]["epochs"].append(epoch)

    if epoch % 10 == 0:
        print(
            f"Epoch {epoch}: train_loss = {train_loss:.4f}, validation_loss = {val_loss:.4f}, val_MAE = {val_mae:.4f}"
        )

# Compute final functional similarity statistics
mean_func_sim = np.mean(experiment_data["with_augmentation"]["functional_similarity"])
std_func_sim = np.std(experiment_data["with_augmentation"]["functional_similarity"])

print("\n" + "=" * 50)
print("RESULTS SUMMARY")
print("=" * 50)
print(f"Functional Similarity Score (mean): {mean_func_sim:.4f} ± {std_func_sim:.4f}")
print(f"\nFinal Validation MAE:")
print(
    f"  Without augmentation: {experiment_data['without_augmentation']['metrics']['val'][-1]:.4f}"
)
print(
    f"  With augmentation: {experiment_data['with_augmentation']['metrics']['val'][-1]:.4f}"
)
print(
    f"\nImprovement: {(experiment_data['without_augmentation']['metrics']['val'][-1] - experiment_data['with_augmentation']['metrics']['val'][-1]):.4f}"
)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Validation loss
axes[0, 0].plot(
    experiment_data["without_augmentation"]["epochs"],
    experiment_data["without_augmentation"]["losses"]["val"],
    label="Without Aug",
    marker="o",
    markersize=3,
)
axes[0, 0].plot(
    experiment_data["with_augmentation"]["epochs"],
    experiment_data["with_augmentation"]["losses"]["val"],
    label="With Aug",
    marker="s",
    markersize=3,
)
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Validation Loss (MSE)")
axes[0, 0].set_title("Validation Loss Comparison")
axes[0, 0].legend()
axes[0, 0].grid(True)

# Plot 2: Validation MAE
axes[0, 1].plot(
    experiment_data["without_augmentation"]["epochs"],
    experiment_data["without_augmentation"]["metrics"]["val"],
    label="Without Aug",
    marker="o",
    markersize=3,
)
axes[0, 1].plot(
    experiment_data["with_augmentation"]["epochs"],
    experiment_data["with_augmentation"]["metrics"]["val"],
    label="With Aug",
    marker="s",
    markersize=3,
)
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Validation MAE (%)")
axes[0, 1].set_title("Validation MAE Comparison")
axes[0, 1].legend()
axes[0, 1].grid(True)

# Plot 3: Functional similarity distribution
axes[1, 0].hist(
    experiment_data["with_augmentation"]["functional_similarity"],
    bins=30,
    edgecolor="black",
    alpha=0.7,
)
axes[1, 0].axvline(
    mean_func_sim,
    color="red",
    linestyle="--",
    linewidth=2,
    label=f"Mean: {mean_func_sim:.3f}",
)
axes[1, 0].set_xlabel("Functional Similarity Score")
axes[1, 0].set_ylabel("Frequency")
axes[1, 0].set_title("Distribution of Functional Similarity Scores")
axes[1, 0].legend()
axes[1, 0].grid(True)

# Plot 4: Predictions vs Ground Truth
predictor_no_aug.eval()
predictor_with_aug.eval()
with torch.no_grad():
    pred_no_aug = predictor_no_aug(X_val_tensor).cpu().numpy().flatten()
    pred_with_aug = predictor_with_aug(X_val_tensor).cpu().numpy().flatten()

axes[1, 1].scatter(y_val, pred_no_aug, alpha=0.6, label="Without Aug", s=50)
axes[1, 1].scatter(y_val, pred_with_aug, alpha=0.6, label="With Aug", s=50)
axes[1, 1].plot(
    [y_val.min(), y_val.max()],
    [y_val.min(), y_val.max()],
    "k--",
    linewidth=2,
    label="Perfect Prediction",
)
axes[1, 1].set_xlabel("Ground Truth Accuracy (%)")
axes[1, 1].set_ylabel("Predicted Accuracy (%)")
axes[1, 1].set_title("Predictions vs Ground Truth")
axes[1, 1].legend()
axes[1, 1].grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "symmetry_aware_augmentation_results.png"), dpi=150
)
print(
    f"\nPlot saved to {os.path.join(working_dir, 'symmetry_aware_augmentation_results.png')}"
)

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\nExperiment completed successfully!")
