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

torch.manual_seed(42)
np.random.seed(42)

experiment_data = {}


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
train_subset = torch.utils.data.Subset(trainset, range(5000))
test_subset = torch.utils.data.Subset(testset, range(1000))
train_loader = DataLoader(train_subset, batch_size=128, shuffle=True)
test_loader = DataLoader(test_subset, batch_size=128, shuffle=False)


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


print("Creating model zoo...")
num_models = 50
model_zoo = []
accuracies = []
for i in tqdm(range(num_models), desc="Training models"):
    model, acc = train_single_model(hidden_dim=128, epochs=5)
    model_zoo.append(model)
    accuracies.append(acc)
print(f"Model zoo created with {num_models} models")
print(f"Accuracy range: {min(accuracies):.2f}% - {max(accuracies):.2f}%")


def permute_neurons(model, layer_idx=1):
    augmented_model = SimpleMLP(hidden_dim=128).to(device)
    augmented_model.load_state_dict(model.state_dict())
    if layer_idx == 1:
        hidden_dim = augmented_model.fc1.weight.shape[0]
        perm = torch.randperm(hidden_dim)
        augmented_model.fc1.weight.data = augmented_model.fc1.weight.data[perm, :]
        augmented_model.fc1.bias.data = augmented_model.fc1.bias.data[perm]
        augmented_model.fc2.weight.data = augmented_model.fc2.weight.data[:, perm]
    return augmented_model


def scale_weights(model, scale_factor=1.1):
    augmented_model = SimpleMLP(hidden_dim=128).to(device)
    augmented_model.load_state_dict(model.state_dict())
    augmented_model.fc1.weight.data *= scale_factor
    augmented_model.fc1.bias.data *= scale_factor
    augmented_model.fc2.weight.data /= scale_factor
    return augmented_model


def sign_flip_weights(model):
    augmented_model = SimpleMLP(hidden_dim=128).to(device)
    augmented_model.load_state_dict(model.state_dict())
    hidden_dim = augmented_model.fc1.weight.shape[0]
    flip_mask = (torch.rand(hidden_dim) > 0.5).float() * 2 - 1
    flip_mask = flip_mask.to(device)
    augmented_model.fc1.weight.data *= flip_mask.unsqueeze(1)
    augmented_model.fc1.bias.data *= flip_mask
    augmented_model.fc2.weight.data *= flip_mask.unsqueeze(0)
    return augmented_model


def apply_augmentation(model, aug_type):
    if aug_type == "permute":
        return permute_neurons(model)
    elif aug_type == "scale":
        scale = np.random.uniform(0.9, 1.1)
        return scale_weights(model, scale)
    elif aug_type == "sign_flip":
        return sign_flip_weights(model)
    elif aug_type == "mixed":
        chosen_aug = np.random.choice(["permute", "scale", "sign_flip"])
        return apply_augmentation(model, chosen_aug)
    else:
        raise ValueError(f"Unknown augmentation type: {aug_type}")


def compute_functional_similarity(model1, model2, data_loader):
    model1.eval()
    model2.eval()
    all_outputs1 = []
    all_outputs2 = []
    with torch.no_grad():
        for inputs, _ in data_loader:
            inputs = inputs.to(device)
            outputs1 = F.softmax(model1(inputs), dim=1)
            outputs2 = F.softmax(model2(inputs), dim=1)
            all_outputs1.append(outputs1.cpu().numpy())
            all_outputs2.append(outputs2.cpu().numpy())
    all_outputs1 = np.concatenate(all_outputs1, axis=0)
    all_outputs2 = np.concatenate(all_outputs2, axis=0)

    # Compute KL divergence for FES
    epsilon = 1e-8
    kl_divs = []
    for i in range(all_outputs1.shape[0]):
        p = all_outputs1[i] + epsilon
        q = all_outputs2[i] + epsilon
        kl = np.sum(p * np.log(p / q))
        kl_divs.append(kl)
    mean_kl = np.mean(kl_divs)
    fes = 1.0 / (1.0 + mean_kl)  # FES metric

    return fes


def extract_weight_features(model):
    features = []
    for param in model.parameters():
        features.append(param.data.cpu().flatten())
    return torch.cat(features).numpy()


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

split_idx = int(0.7 * len(X))
X_train, X_val = X[:split_idx], X[split_idx:]
y_train, y_val = y[:split_idx], y[split_idx:]
print(f"Train: {X_train.shape}, Val: {X_val.shape}")


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


print("\n" + "=" * 70)
print("ABLATION STUDY: Augmentation Type Diversity")
print("=" * 70)

# Train baseline without augmentation
print("\n" + "=" * 50)
print("Training WITHOUT augmentation (baseline)...")
print("=" * 50)

X_train_tensor = torch.FloatTensor(X_train).to(device)
y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1).to(device)
X_val_tensor = torch.FloatTensor(X_val).to(device)
y_val_tensor = torch.FloatTensor(y_val).unsqueeze(1).to(device)

experiment_data["no_augmentation"] = {
    "metrics": {"train": [], "val": [], "fes": []},
    "losses": {"train": [], "val": []},
    "predictions": [],
    "ground_truth": y_val.tolist(),
    "epochs": [],
}

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

    predictor_no_aug.eval()
    with torch.no_grad():
        val_outputs = predictor_no_aug(X_val_tensor)
        val_loss = criterion(val_outputs, y_val_tensor).item()
        val_mae = torch.mean(torch.abs(val_outputs - y_val_tensor)).item()

    experiment_data["no_augmentation"]["losses"]["train"].append(train_loss)
    experiment_data["no_augmentation"]["losses"]["val"].append(val_loss)
    experiment_data["no_augmentation"]["metrics"]["val"].append(val_mae)
    experiment_data["no_augmentation"]["epochs"].append(epoch)

    if epoch % 10 == 0:
        print(
            f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_MAE={val_mae:.4f}"
        )

predictor_no_aug.eval()
with torch.no_grad():
    final_pred_no_aug = predictor_no_aug(X_val_tensor).cpu().numpy().flatten()
experiment_data["no_augmentation"]["predictions"] = final_pred_no_aug.tolist()

# Ablation: Test different augmentation types
augmentation_types = ["permute", "scale", "sign_flip", "mixed"]
num_augmentations_per_model = 8

for aug_type in augmentation_types:
    print("\n" + "=" * 50)
    print(f"Training WITH '{aug_type}' augmentation...")
    print("=" * 50)

    experiment_data[f"aug_{aug_type}"] = {
        "metrics": {"train": [], "val": [], "fes": []},
        "losses": {"train": [], "val": []},
        "functional_similarity": [],
        "predictions": [],
        "ground_truth": y_val.tolist(),
        "epochs": [],
        "augmentation_type": aug_type,
    }

    X_train_aug = [X_train]
    y_train_aug = [y_train]

    print(f"Generating augmented samples using '{aug_type}'...")
    for idx, model in enumerate(
        tqdm(model_zoo[:split_idx], desc=f"Augmenting ({aug_type})")
    ):
        for _ in range(num_augmentations_per_model):
            aug_model = apply_augmentation(model, aug_type)
            aug_features = extract_weight_features(aug_model)
            X_train_aug.append(aug_features.reshape(1, -1))
            y_train_aug.append([accuracies[idx]])
            func_sim = compute_functional_similarity(model, aug_model, test_loader)
            experiment_data[f"aug_{aug_type}"]["functional_similarity"].append(func_sim)

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

        predictor_with_aug.eval()
        with torch.no_grad():
            val_outputs = predictor_with_aug(X_val_tensor)
            val_loss = criterion(val_outputs, y_val_tensor).item()
            val_mae = torch.mean(torch.abs(val_outputs - y_val_tensor)).item()

        # Compute FES metric
        mean_fes = np.mean(experiment_data[f"aug_{aug_type}"]["functional_similarity"])

        experiment_data[f"aug_{aug_type}"]["losses"]["train"].append(train_loss)
        experiment_data[f"aug_{aug_type}"]["losses"]["val"].append(val_loss)
        experiment_data[f"aug_{aug_type}"]["metrics"]["val"].append(val_mae)
        experiment_data[f"aug_{aug_type}"]["metrics"]["fes"].append(mean_fes)
        experiment_data[f"aug_{aug_type}"]["epochs"].append(epoch)

        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_MAE={val_mae:.4f}, FES={mean_fes:.4f}"
            )

    predictor_with_aug.eval()
    with torch.no_grad():
        final_pred_with_aug = predictor_with_aug(X_val_tensor).cpu().numpy().flatten()
    experiment_data[f"aug_{aug_type}"]["predictions"] = final_pred_with_aug.tolist()

print("\n" + "=" * 70)
print("ABLATION STUDY RESULTS SUMMARY")
print("=" * 70)

baseline_mae = experiment_data["no_augmentation"]["metrics"]["val"][-1]
print(f"\nBaseline (no augmentation) - Final Validation MAE: {baseline_mae:.4f}")

best_aug_type = None
best_mae = float("inf")

for aug_type in augmentation_types:
    final_mae = experiment_data[f"aug_{aug_type}"]["metrics"]["val"][-1]
    mean_func_sim = np.mean(experiment_data[f"aug_{aug_type}"]["functional_similarity"])
    std_func_sim = np.std(experiment_data[f"aug_{aug_type}"]["functional_similarity"])
    improvement = baseline_mae - final_mae

    print(f"\nAugmentation Type: '{aug_type}':")
    print(f"  Final Validation MAE: {final_mae:.4f}")
    print(
        f"  Improvement over baseline: {improvement:.4f} ({improvement/baseline_mae*100:.2f}%)"
    )
    print(
        f"  FES (Functional Equivalence Score): {mean_func_sim:.4f} ± {std_func_sim:.4f}"
    )

    if final_mae < best_mae:
        best_mae = final_mae
        best_aug_type = aug_type

print(f"\n{'='*70}")
print(f"BEST AUGMENTATION TYPE: '{best_aug_type}'")
print(f"Best Validation MAE: {best_mae:.4f}")
print(
    f"Improvement: {baseline_mae - best_mae:.4f} ({(baseline_mae - best_mae)/baseline_mae*100:.2f}%)"
)
print(f"{'='*70}")

# Visualization
fig, axes = plt.subplots(2, 3, figsize=(20, 12))

# Plot 1: Validation MAE over epochs
axes[0, 0].plot(
    experiment_data["no_augmentation"]["epochs"],
    experiment_data["no_augmentation"]["metrics"]["val"],
    label="No Aug (Baseline)",
    linewidth=2.5,
    marker="o",
    markersize=4,
    color="gray",
)
colors_aug = ["blue", "green", "orange", "red"]
for i, aug_type in enumerate(augmentation_types):
    axes[0, 0].plot(
        experiment_data[f"aug_{aug_type}"]["epochs"],
        experiment_data[f"aug_{aug_type}"]["metrics"]["val"],
        label=f"{aug_type}",
        linewidth=2,
        marker="s",
        markersize=3,
        color=colors_aug[i],
    )
axes[0, 0].set_xlabel("Epoch", fontsize=12)
axes[0, 0].set_ylabel("Validation MAE (%)", fontsize=12)
axes[0, 0].set_title(
    "Validation MAE vs Epochs (Augmentation Type Ablation)",
    fontsize=13,
    fontweight="bold",
)
axes[0, 0].legend(fontsize=10)
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Validation Loss over epochs
axes[0, 1].plot(
    experiment_data["no_augmentation"]["epochs"],
    experiment_data["no_augmentation"]["losses"]["val"],
    label="No Aug (Baseline)",
    linewidth=2.5,
    marker="o",
    markersize=4,
    color="gray",
)
for i, aug_type in enumerate(augmentation_types):
    axes[0, 1].plot(
        experiment_data[f"aug_{aug_type}"]["epochs"],
        experiment_data[f"aug_{aug_type}"]["losses"]["val"],
        label=f"{aug_type}",
        linewidth=2,
        marker="s",
        markersize=3,
        color=colors_aug[i],
    )
axes[0, 1].set_xlabel("Epoch", fontsize=12)
axes[0, 1].set_ylabel("Validation Loss (MSE)", fontsize=12)
axes[0, 1].set_title("Validation Loss vs Epochs", fontsize=13, fontweight="bold")
axes[0, 1].legend(fontsize=10)
axes[0, 1].grid(True, alpha=0.3)

# Plot 3: Final MAE comparison bar chart
final_maes = [baseline_mae] + [
    experiment_data[f"aug_{aug_type}"]["metrics"]["val"][-1]
    for aug_type in augmentation_types
]
x_labels = ["No Aug"] + augmentation_types
colors_bar = ["gray"] + colors_aug
bars = axes[0, 2].bar(
    x_labels, final_maes, color=colors_bar, alpha=0.7, edgecolor="black", linewidth=1.5
)
axes[0, 2].set_xlabel("Augmentation Type", fontsize=12)
axes[0, 2].set_ylabel("Final Validation MAE (%)", fontsize=12)
axes[0, 2].set_title("Final Validation MAE Comparison", fontsize=13, fontweight="bold")
axes[0, 2].grid(True, axis="y", alpha=0.3)
for i, bar in enumerate(bars):
    height = bar.get_height()
    axes[0, 2].text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{final_maes[i]:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

# Plot 4: Functional similarity distributions (with error handling)
for i, aug_type in enumerate(augmentation_types):
    func_sims = experiment_data[f"aug_{aug_type}"]["functional_similarity"]
    # Check if data has sufficient variance for histogram
    if len(func_sims) > 0:
        data_range = np.ptp(func_sims)  # peak to peak (max - min)
        if data_range > 1e-6:  # If there's some variance
            # Determine number of bins based on data range
            n_bins = min(20, max(5, int(len(func_sims) / 10)))
            axes[1, 0].hist(
                func_sims,
                bins=n_bins,
                alpha=0.5,
                label=f"{aug_type}",
                edgecolor="black",
                color=colors_aug[i],
            )
        else:
            # For constant data, plot a vertical line instead
            axes[1, 0].axvline(
                x=np.mean(func_sims),
                color=colors_aug[i],
                linewidth=3,
                alpha=0.7,
                label=f"{aug_type} (constant)",
            )
axes[1, 0].set_xlabel("FES Score", fontsize=12)
axes[1, 0].set_ylabel("Frequency", fontsize=12)
axes[1, 0].set_title("Distribution of FES by Aug Type", fontsize=13, fontweight="bold")
axes[1, 0].legend(fontsize=10)
axes[1, 0].grid(True, alpha=0.3)

# Plot 5: Predictions vs Ground Truth
y_val_plot = np.array(experiment_data["no_augmentation"]["ground_truth"])
pred_no_aug_plot = np.array(experiment_data["no_augmentation"]["predictions"])
axes[1, 1].scatter(
    y_val_plot,
    pred_no_aug_plot,
    alpha=0.6,
    label="No Aug",
    s=60,
    color="gray",
    edgecolors="black",
    linewidths=0.5,
)
for i, aug_type in enumerate(augmentation_types):
    pred_aug = np.array(experiment_data[f"aug_{aug_type}"]["predictions"])
    axes[1, 1].scatter(
        y_val_plot,
        pred_aug,
        alpha=0.5,
        label=f"{aug_type}",
        s=50,
        color=colors_aug[i],
        edgecolors="black",
        linewidths=0.5,
    )
axes[1, 1].plot(
    [y_val_plot.min(), y_val_plot.max()],
    [y_val_plot.min(), y_val_plot.max()],
    "k--",
    linewidth=2.5,
    label="Perfect Prediction",
)
axes[1, 1].set_xlabel("Ground Truth Accuracy (%)", fontsize=12)
axes[1, 1].set_ylabel("Predicted Accuracy (%)", fontsize=12)
axes[1, 1].set_title("Predictions vs Ground Truth", fontsize=13, fontweight="bold")
axes[1, 1].legend(fontsize=9)
axes[1, 1].grid(True, alpha=0.3)

# Plot 6: Mean FES by augmentation type
mean_func_sims = [
    np.mean(experiment_data[f"aug_{aug_type}"]["functional_similarity"])
    for aug_type in augmentation_types
]
std_func_sims = [
    np.std(experiment_data[f"aug_{aug_type}"]["functional_similarity"])
    for aug_type in augmentation_types
]
axes[1, 2].bar(
    augmentation_types,
    mean_func_sims,
    yerr=std_func_sims,
    color=colors_aug,
    alpha=0.7,
    edgecolor="black",
    linewidth=1.5,
    capsize=5,
)
axes[1, 2].set_xlabel("Augmentation Type", fontsize=12)
axes[1, 2].set_ylabel("Mean FES Score", fontsize=12)
axes[1, 2].set_title("FES by Augmentation Type", fontsize=13, fontweight="bold")
axes[1, 2].grid(True, axis="y", alpha=0.3)
for i, (aug_type, mean_sim) in enumerate(zip(augmentation_types, mean_func_sims)):
    axes[1, 2].text(
        i,
        mean_sim + std_func_sims[i] + 0.01,
        f"{mean_sim:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "augmentation_type_ablation_results.png"), dpi=150
)
print(
    f"\nPlot saved to {os.path.join(working_dir, 'augmentation_type_ablation_results.png')}"
)

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\n" + "=" * 70)
print("ABLATION STUDY INSIGHTS")
print("=" * 70)
print("\nKey Findings:")
print(f"1. Best performing augmentation: '{best_aug_type}' (MAE: {best_mae:.4f})")
print(f"2. Baseline MAE: {baseline_mae:.4f}")
print(
    f"3. Best improvement: {baseline_mae - best_mae:.4f} ({(baseline_mae - best_mae)/baseline_mae*100:.2f}%)"
)

print("\nFES (Functional Equivalence Score) Analysis:")
for aug_type in augmentation_types:
    mean_sim = np.mean(experiment_data[f"aug_{aug_type}"]["functional_similarity"])
    print(f"  {aug_type}: {mean_sim:.4f}")

print("\nConclusion:")
if best_aug_type == "mixed":
    print("  The mixed augmentation strategy (combining all types) performs best,")
    print(
        "  suggesting that augmentation diversity is valuable for learning weight-space"
    )
    print("  to accuracy mappings.")
else:
    print(f"  The '{best_aug_type}' augmentation alone performs best, indicating that")
    print("  specific symmetry-preserving transformations may be more valuable than")
    print("  augmentation diversity for this task.")

print("\nExperiment completed successfully!")
