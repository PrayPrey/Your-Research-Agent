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


def apply_random_augmentation(model):
    aug_type = np.random.choice(["permute", "scale", "sign_flip"])
    if aug_type == "permute":
        return permute_neurons(model)
    elif aug_type == "scale":
        scale = np.random.uniform(0.9, 1.1)
        return scale_weights(model, scale)
    else:
        return sign_flip_weights(model)


def compute_functional_similarity(model1, model2, data_loader):
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
    correlations = []
    for i in range(all_outputs1.shape[1]):
        corr, _ = pearsonr(all_outputs1[:, i], all_outputs2[:, i])
        correlations.append(corr)
    return np.mean(correlations)


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


print("\n" + "=" * 50)
print("Training WITHOUT augmentation (baseline)...")
print("=" * 50)

X_train_tensor = torch.FloatTensor(X_train).to(device)
y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1).to(device)
X_val_tensor = torch.FloatTensor(X_val).to(device)
y_val_tensor = torch.FloatTensor(y_val).unsqueeze(1).to(device)

experiment_data["without_augmentation"] = {
    "metrics": {"train": [], "val": []},
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

    experiment_data["without_augmentation"]["losses"]["train"].append(train_loss)
    experiment_data["without_augmentation"]["losses"]["val"].append(val_loss)
    experiment_data["without_augmentation"]["metrics"]["val"].append(val_mae)
    experiment_data["without_augmentation"]["epochs"].append(epoch)

    if epoch % 10 == 0:
        print(
            f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_MAE={val_mae:.4f}"
        )

predictor_no_aug.eval()
with torch.no_grad():
    final_pred_no_aug = predictor_no_aug(X_val_tensor).cpu().numpy().flatten()
experiment_data["without_augmentation"]["predictions"] = final_pred_no_aug.tolist()

# Hyperparameter tuning for num_augmentations_per_model
num_augmentations_values = [2, 4, 8, 16]

for num_augs in num_augmentations_values:
    print("\n" + "=" * 50)
    print(f"Training WITH {num_augs} augmentations per model...")
    print("=" * 50)

    experiment_data[f"num_aug_{num_augs}"] = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "functional_similarity": [],
        "predictions": [],
        "ground_truth": y_val.tolist(),
        "epochs": [],
        "num_augmentations": num_augs,
    }

    X_train_aug = [X_train]
    y_train_aug = [y_train]

    print(f"Generating {num_augs} augmented samples per model...")
    for idx, model in enumerate(
        tqdm(model_zoo[:split_idx], desc=f"Augmenting (n={num_augs})")
    ):
        for _ in range(num_augs):
            aug_model = apply_random_augmentation(model)
            aug_features = extract_weight_features(aug_model)
            X_train_aug.append(aug_features.reshape(1, -1))
            y_train_aug.append([accuracies[idx]])
            func_sim = compute_functional_similarity(model, aug_model, test_loader)
            experiment_data[f"num_aug_{num_augs}"]["functional_similarity"].append(
                func_sim
            )

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

        experiment_data[f"num_aug_{num_augs}"]["losses"]["train"].append(train_loss)
        experiment_data[f"num_aug_{num_augs}"]["losses"]["val"].append(val_loss)
        experiment_data[f"num_aug_{num_augs}"]["metrics"]["val"].append(val_mae)
        experiment_data[f"num_aug_{num_augs}"]["epochs"].append(epoch)

        if epoch % 10 == 0:
            print(
                f"Epoch {epoch}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_MAE={val_mae:.4f}"
            )

    predictor_with_aug.eval()
    with torch.no_grad():
        final_pred_with_aug = predictor_with_aug(X_val_tensor).cpu().numpy().flatten()
    experiment_data[f"num_aug_{num_augs}"]["predictions"] = final_pred_with_aug.tolist()

print("\n" + "=" * 50)
print("HYPERPARAMETER TUNING RESULTS SUMMARY")
print("=" * 50)

baseline_mae = experiment_data["without_augmentation"]["metrics"]["val"][-1]
print(f"\nBaseline (no augmentation) - Final Validation MAE: {baseline_mae:.4f}")

best_num_aug = None
best_mae = float("inf")

for num_augs in num_augmentations_values:
    final_mae = experiment_data[f"num_aug_{num_augs}"]["metrics"]["val"][-1]
    mean_func_sim = np.mean(
        experiment_data[f"num_aug_{num_augs}"]["functional_similarity"]
    )
    std_func_sim = np.std(
        experiment_data[f"num_aug_{num_augs}"]["functional_similarity"]
    )
    improvement = baseline_mae - final_mae

    print(f"\nnum_augmentations={num_augs}:")
    print(f"  Final Validation MAE: {final_mae:.4f}")
    print(f"  Improvement over baseline: {improvement:.4f}")
    print(f"  Functional Similarity: {mean_func_sim:.4f} ± {std_func_sim:.4f}")
    print(f"  Training set size: {split_idx * (1 + num_augs)}")

    if final_mae < best_mae:
        best_mae = final_mae
        best_num_aug = num_augs

print(f"\n{'='*50}")
print(f"BEST HYPERPARAMETER: num_augmentations_per_model = {best_num_aug}")
print(f"Best Validation MAE: {best_mae:.4f}")
print(f"{'='*50}")

fig, axes = plt.subplots(2, 3, figsize=(18, 12))

axes[0, 0].plot(
    experiment_data["without_augmentation"]["epochs"],
    experiment_data["without_augmentation"]["metrics"]["val"],
    label="No Aug (Baseline)",
    linewidth=2,
    marker="o",
    markersize=3,
)
for num_augs in num_augmentations_values:
    axes[0, 0].plot(
        experiment_data[f"num_aug_{num_augs}"]["epochs"],
        experiment_data[f"num_aug_{num_augs}"]["metrics"]["val"],
        label=f"n_aug={num_augs}",
        linewidth=2,
        marker="s",
        markersize=3,
    )
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Validation MAE (%)")
axes[0, 0].set_title("Validation MAE vs Epochs")
axes[0, 0].legend()
axes[0, 0].grid(True)

axes[0, 1].plot(
    experiment_data["without_augmentation"]["epochs"],
    experiment_data["without_augmentation"]["losses"]["val"],
    label="No Aug (Baseline)",
    linewidth=2,
    marker="o",
    markersize=3,
)
for num_augs in num_augmentations_values:
    axes[0, 1].plot(
        experiment_data[f"num_aug_{num_augs}"]["epochs"],
        experiment_data[f"num_aug_{num_augs}"]["losses"]["val"],
        label=f"n_aug={num_augs}",
        linewidth=2,
        marker="s",
        markersize=3,
    )
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Validation Loss (MSE)")
axes[0, 1].set_title("Validation Loss vs Epochs")
axes[0, 1].legend()
axes[0, 1].grid(True)

final_maes = [baseline_mae] + [
    experiment_data[f"num_aug_{n}"]["metrics"]["val"][-1]
    for n in num_augmentations_values
]
x_labels = ["No Aug"] + [str(n) for n in num_augmentations_values]
colors = ["gray"] + ["blue", "green", "orange", "red"]
bars = axes[0, 2].bar(x_labels, final_maes, color=colors, alpha=0.7, edgecolor="black")
axes[0, 2].set_xlabel("Number of Augmentations per Model")
axes[0, 2].set_ylabel("Final Validation MAE (%)")
axes[0, 2].set_title("Final Validation MAE Comparison")
axes[0, 2].grid(True, axis="y")
for i, bar in enumerate(bars):
    height = bar.get_height()
    axes[0, 2].text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{final_maes[i]:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )

for num_augs in num_augmentations_values:
    func_sims = experiment_data[f"num_aug_{num_augs}"]["functional_similarity"]
    axes[1, 0].hist(
        func_sims, bins=20, alpha=0.5, label=f"n_aug={num_augs}", edgecolor="black"
    )
axes[1, 0].set_xlabel("Functional Similarity Score")
axes[1, 0].set_ylabel("Frequency")
axes[1, 0].set_title("Distribution of Functional Similarity")
axes[1, 0].legend()
axes[1, 0].grid(True)

y_val_plot = np.array(experiment_data["without_augmentation"]["ground_truth"])
pred_no_aug_plot = np.array(experiment_data["without_augmentation"]["predictions"])
axes[1, 1].scatter(y_val_plot, pred_no_aug_plot, alpha=0.6, label="No Aug", s=50)
for num_augs in num_augmentations_values:
    pred_aug = np.array(experiment_data[f"num_aug_{num_augs}"]["predictions"])
    axes[1, 1].scatter(y_val_plot, pred_aug, alpha=0.5, label=f"n_aug={num_augs}", s=40)
axes[1, 1].plot(
    [y_val_plot.min(), y_val_plot.max()],
    [y_val_plot.min(), y_val_plot.max()],
    "k--",
    linewidth=2,
    label="Perfect Prediction",
)
axes[1, 1].set_xlabel("Ground Truth Accuracy (%)")
axes[1, 1].set_ylabel("Predicted Accuracy (%)")
axes[1, 1].set_title("Predictions vs Ground Truth")
axes[1, 1].legend()
axes[1, 1].grid(True)

training_sizes = [split_idx] + [split_idx * (1 + n) for n in num_augmentations_values]
axes[1, 2].plot(
    training_sizes, final_maes, marker="o", linewidth=2, markersize=8, color="purple"
)
axes[1, 2].set_xlabel("Training Set Size")
axes[1, 2].set_ylabel("Final Validation MAE (%)")
axes[1, 2].set_title("Validation MAE vs Training Set Size")
axes[1, 2].grid(True)
for i, (size, mae) in enumerate(zip(training_sizes, final_maes)):
    axes[1, 2].annotate(
        f"{mae:.3f}",
        xy=(size, mae),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=8,
    )

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "hyperparameter_tuning_results.png"), dpi=150)
print(
    f"\nPlot saved to {os.path.join(working_dir, 'hyperparameter_tuning_results.png')}"
)

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Experiment data saved to {os.path.join(working_dir, 'experiment_data.npy')}")

print("\nExperiment completed successfully!")
