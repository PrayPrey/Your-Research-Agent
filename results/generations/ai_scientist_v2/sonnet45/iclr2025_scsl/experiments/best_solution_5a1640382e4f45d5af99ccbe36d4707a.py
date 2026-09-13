import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize experiment data storage with hyperparameter tuning structure
experiment_data = {
    "learning_rate_tuning": {
        "simclr": {},
        "mae": {},
    }
}


# Create synthetic dataset with spurious correlations
class SpuriousDataset(Dataset):
    def __init__(
        self, n_samples=2000, img_size=28, spurious_corr=0.95, shift_spurious=False
    ):
        self.n_samples = n_samples
        self.img_size = img_size
        self.spurious_corr = spurious_corr
        self.shift_spurious = shift_spurious

        self.images = []
        self.labels = []
        self.spurious_attrs = []
        self.groups = []

        for idx in range(n_samples):
            label = idx % 2

            if shift_spurious:
                if idx % 2 == 0:
                    spurious_attr = label
                    group = 0
                else:
                    spurious_attr = 1 - label
                    group = 1
            else:
                if np.random.rand() < spurious_corr:
                    spurious_attr = label
                else:
                    spurious_attr = 1 - label
                group = 0 if spurious_attr == label else 1

            img = np.zeros((img_size, img_size), dtype=np.float32)

            texture_intensity = 0.7
            if spurious_attr == 0:
                for i in range(0, img_size, 3):
                    img[i : i + 2, :] = texture_intensity
            else:
                for i in range(0, img_size, 3):
                    img[:, i : i + 2] = texture_intensity

            center = img_size // 2
            radius = 8
            shape_intensity = 0.4
            noise = np.random.normal(0, 0.1, (img_size, img_size))

            if label == 0:
                y, x = np.ogrid[:img_size, :img_size]
                mask = (x - center) ** 2 + (y - center) ** 2 <= radius**2
                img[mask] = np.clip(img[mask] + shape_intensity + noise[mask], 0, 1)
            else:
                img[
                    center - radius : center + radius, center - radius : center + radius
                ] = np.clip(
                    img[
                        center - radius : center + radius,
                        center - radius : center + radius,
                    ]
                    + shape_intensity
                    + noise[
                        center - radius : center + radius,
                        center - radius : center + radius,
                    ],
                    0,
                    1,
                )

            self.images.append(img)
            self.labels.append(label)
            self.spurious_attrs.append(spurious_attr)
            self.groups.append(group)

        self.images = np.array(self.images)
        self.labels = np.array(self.labels)
        self.spurious_attrs = np.array(self.spurious_attrs)
        self.groups = np.array(self.groups)

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        img = torch.FloatTensor(self.images[idx]).unsqueeze(0)
        label = torch.LongTensor([self.labels[idx]])[0]
        group = torch.LongTensor([self.groups[idx]])[0]
        return img, label, group


# Create datasets
print("Creating datasets...")
train_dataset = SpuriousDataset(
    n_samples=2000, spurious_corr=0.95, shift_spurious=False
)
test_dataset = SpuriousDataset(n_samples=1000, spurious_corr=0.95, shift_spurious=True)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

print(f"Train dataset: {len(train_dataset)} samples")
print(f"Test dataset: {len(test_dataset)} samples")


# Shared Encoder
class Encoder(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(1, 32, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(128, embedding_dim),
        )

    def forward(self, x):
        return self.network(x)


# SimCLR Model
class SimCLR(nn.Module):
    def __init__(self, embedding_dim=128, projection_dim=64):
        super().__init__()
        self.encoder = Encoder(embedding_dim)
        self.projection_head = nn.Sequential(
            nn.Linear(embedding_dim, embedding_dim),
            nn.ReLU(),
            nn.Linear(embedding_dim, projection_dim),
        )

    def forward(self, x1, x2):
        h1 = self.encoder(x1)
        h2 = self.encoder(x2)
        z1 = self.projection_head(h1)
        z2 = self.projection_head(h2)
        return z1, z2

    def get_representation(self, x):
        return self.encoder(x)


def contrastive_loss(z1, z2, temperature=0.5):
    batch_size = z1.shape[0]
    z = torch.cat([z1, z2], dim=0)
    z = F.normalize(z, dim=1)

    similarity_matrix = torch.mm(z, z.t()) / temperature

    labels = torch.arange(batch_size).to(device)
    labels = torch.cat([labels + batch_size, labels])

    mask = torch.eye(2 * batch_size, dtype=torch.bool).to(device)
    similarity_matrix = similarity_matrix.masked_fill(mask, -9e15)

    loss = F.cross_entropy(similarity_matrix, labels)
    return loss


# MAE Model
class MAE(nn.Module):
    def __init__(self, embedding_dim=128, mask_ratio=0.75):
        super().__init__()
        self.encoder = Encoder(embedding_dim)
        self.mask_ratio = mask_ratio

        self.decoder_fc = nn.Linear(embedding_dim, 128 * 7 * 7)
        self.decoder_network = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 1, kernel_size=3, padding=1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        batch_size, channels, height_orig, width_orig = x.shape

        encoded = self.encoder(x)

        decoder_input = self.decoder_fc(encoded)
        decoder_input = decoder_input.view(batch_size, 128, 7, 7)
        reconstructed = self.decoder_network(decoder_input)

        return reconstructed

    def get_representation(self, x):
        return self.encoder(x)


# Simple augmentation
def augment(x):
    if torch.rand(1) > 0.5:
        x = torch.flip(x, [3])
    noise = torch.randn_like(x) * 0.1
    x = torch.clamp(x + noise, 0, 1)
    return x


# Extract features
def extract_features(model, loader):
    model.eval()
    all_features = []
    all_labels = []
    all_groups = []

    with torch.no_grad():
        for imgs, labels, groups in loader:
            imgs = imgs.to(device)
            features = model.get_representation(imgs).cpu().numpy()
            all_features.append(features)
            all_labels.append(labels.numpy())
            all_groups.append(groups.numpy())

    return (
        np.vstack(all_features),
        np.concatenate(all_labels),
        np.concatenate(all_groups),
    )


# Evaluate worst group
def evaluate_worst_group(probe, features, labels, groups):
    predictions = probe.predict(features)

    overall_acc = np.mean(predictions == labels)

    unique_groups = np.unique(groups)
    group_accs = []
    for g in unique_groups:
        group_mask = groups == g
        group_pred = predictions[group_mask]
        group_label = labels[group_mask]
        group_acc = np.mean(group_pred == group_label)
        group_accs.append(group_acc)

    worst_group_acc = min(group_accs)
    return overall_acc, worst_group_acc, group_accs


# Hyperparameter tuning: learning rates
learning_rates = [5e-4, 1e-3, 3e-3, 5e-3]
epochs = 20

# Train and evaluate SimCLR for different learning rates
print("\n" + "=" * 50)
print("Hyperparameter Tuning: SimCLR Learning Rate")
print("=" * 50)

for lr in learning_rates:
    print(f"\n--- Training SimCLR with lr={lr} ---")

    # Initialize model
    simclr_model = SimCLR(embedding_dim=128, projection_dim=64).to(device)
    simclr_optimizer = torch.optim.Adam(simclr_model.parameters(), lr=lr)

    # Pre-train
    pretrain_losses = []
    for epoch in range(epochs):
        simclr_model.train()
        total_loss = 0
        for imgs, _, _ in train_loader:
            imgs = imgs.to(device)

            x1 = augment(imgs)
            x2 = augment(imgs)

            z1, z2 = simclr_model(x1, x2)
            loss = contrastive_loss(z1, z2)

            simclr_optimizer.zero_grad()
            loss.backward()
            simclr_optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        pretrain_losses.append(avg_loss)
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")

    # Extract features
    train_features, train_labels, train_groups = extract_features(
        simclr_model, train_loader
    )
    test_features, test_labels, test_groups = extract_features(
        simclr_model, test_loader
    )

    # Train linear probe
    probe = LogisticRegression(max_iter=1000, random_state=42)
    probe.fit(train_features, train_labels)

    # Evaluate
    avg_acc, worst_acc, group_accs = evaluate_worst_group(
        probe, test_features, test_labels, test_groups
    )

    print(f"Results: Avg Acc={avg_acc:.4f}, Worst-Group Acc={worst_acc:.4f}")

    # Store results
    experiment_data["learning_rate_tuning"]["simclr"][f"lr_{lr}"] = {
        "learning_rate": float(lr),
        "pretrain_losses": [float(x) for x in pretrain_losses],
        "avg_accuracy": float(avg_acc),
        "worst_group_accuracy": float(worst_acc),
        "group_accuracies": [float(x) for x in group_accs],
    }

# Train and evaluate MAE for different learning rates
print("\n" + "=" * 50)
print("Hyperparameter Tuning: MAE Learning Rate")
print("=" * 50)

for lr in learning_rates:
    print(f"\n--- Training MAE with lr={lr} ---")

    # Initialize model
    mae_model = MAE(embedding_dim=128, mask_ratio=0.75).to(device)
    mae_optimizer = torch.optim.Adam(mae_model.parameters(), lr=lr)

    # Pre-train
    pretrain_losses = []
    for epoch in range(epochs):
        mae_model.train()
        total_loss = 0
        for imgs, _, _ in train_loader:
            imgs = imgs.to(device)

            reconstructed = mae_model(imgs)
            loss = F.mse_loss(reconstructed, imgs)

            mae_optimizer.zero_grad()
            loss.backward()
            mae_optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        pretrain_losses.append(avg_loss)
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1}/{epochs}: Loss = {avg_loss:.4f}")

    # Extract features
    train_features, train_labels, train_groups = extract_features(
        mae_model, train_loader
    )
    test_features, test_labels, test_groups = extract_features(mae_model, test_loader)

    # Train linear probe
    probe = LogisticRegression(max_iter=1000, random_state=42)
    probe.fit(train_features, train_labels)

    # Evaluate
    avg_acc, worst_acc, group_accs = evaluate_worst_group(
        probe, test_features, test_labels, test_groups
    )

    print(f"Results: Avg Acc={avg_acc:.4f}, Worst-Group Acc={worst_acc:.4f}")

    # Store results
    experiment_data["learning_rate_tuning"]["mae"][f"lr_{lr}"] = {
        "learning_rate": float(lr),
        "pretrain_losses": [float(x) for x in pretrain_losses],
        "avg_accuracy": float(avg_acc),
        "worst_group_accuracy": float(worst_acc),
        "group_accuracies": [float(x) for x in group_accs],
    }

# Find best learning rates
print("\n" + "=" * 50)
print("HYPERPARAMETER TUNING RESULTS")
print("=" * 50)

print("\nSimCLR Results:")
best_simclr_lr = None
best_simclr_worst_acc = -1
for lr_key, results in experiment_data["learning_rate_tuning"]["simclr"].items():
    lr = results["learning_rate"]
    worst_acc = results["worst_group_accuracy"]
    print(f"  lr={lr}: Worst-Group Acc={worst_acc:.4f}")
    if worst_acc > best_simclr_worst_acc:
        best_simclr_worst_acc = worst_acc
        best_simclr_lr = lr

print(
    f"\nBest SimCLR learning rate: {best_simclr_lr} (Worst-Group Acc={best_simclr_worst_acc:.4f})"
)

print("\nMAE Results:")
best_mae_lr = None
best_mae_worst_acc = -1
for lr_key, results in experiment_data["learning_rate_tuning"]["mae"].items():
    lr = results["learning_rate"]
    worst_acc = results["worst_group_accuracy"]
    print(f"  lr={lr}: Worst-Group Acc={worst_acc:.4f}")
    if worst_acc > best_mae_worst_acc:
        best_mae_worst_acc = worst_acc
        best_mae_lr = lr

print(
    f"\nBest MAE learning rate: {best_mae_lr} (Worst-Group Acc={best_mae_worst_acc:.4f})"
)

# Visualize results
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# SimCLR: Pretrain losses for different LRs
for lr_key, results in experiment_data["learning_rate_tuning"]["simclr"].items():
    lr = results["learning_rate"]
    axes[0, 0].plot(results["pretrain_losses"], label=f"lr={lr}")
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("SimCLR: Pretraining Loss vs Learning Rate")
axes[0, 0].legend()
axes[0, 0].grid(True)

# SimCLR: Worst-group accuracy vs LR
simclr_lrs = [
    results["learning_rate"]
    for results in experiment_data["learning_rate_tuning"]["simclr"].values()
]
simclr_worst_accs = [
    results["worst_group_accuracy"]
    for results in experiment_data["learning_rate_tuning"]["simclr"].values()
]
axes[0, 1].plot(simclr_lrs, simclr_worst_accs, "o-", linewidth=2, markersize=8)
axes[0, 1].set_xlabel("Learning Rate")
axes[0, 1].set_ylabel("Worst-Group Accuracy")
axes[0, 1].set_title("SimCLR: Worst-Group Accuracy vs Learning Rate")
axes[0, 1].set_xscale("log")
axes[0, 1].grid(True)

# SimCLR: Group-wise accuracy for best LR
best_simclr_results = experiment_data["learning_rate_tuning"]["simclr"][
    f"lr_{best_simclr_lr}"
]
axes[0, 2].bar(
    ["Group 0", "Group 1"], best_simclr_results["group_accuracies"], alpha=0.7
)
axes[0, 2].set_ylabel("Accuracy")
axes[0, 2].set_title(f"SimCLR: Group Accuracy (Best LR={best_simclr_lr})")
axes[0, 2].grid(True, axis="y")

# MAE: Pretrain losses for different LRs
for lr_key, results in experiment_data["learning_rate_tuning"]["mae"].items():
    lr = results["learning_rate"]
    axes[1, 0].plot(results["pretrain_losses"], label=f"lr={lr}")
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Loss")
axes[1, 0].set_title("MAE: Pretraining Loss vs Learning Rate")
axes[1, 0].legend()
axes[1, 0].grid(True)

# MAE: Worst-group accuracy vs LR
mae_lrs = [
    results["learning_rate"]
    for results in experiment_data["learning_rate_tuning"]["mae"].values()
]
mae_worst_accs = [
    results["worst_group_accuracy"]
    for results in experiment_data["learning_rate_tuning"]["mae"].values()
]
axes[1, 1].plot(mae_lrs, mae_worst_accs, "s-", linewidth=2, markersize=8)
axes[1, 1].set_xlabel("Learning Rate")
axes[1, 1].set_ylabel("Worst-Group Accuracy")
axes[1, 1].set_title("MAE: Worst-Group Accuracy vs Learning Rate")
axes[1, 1].set_xscale("log")
axes[1, 1].grid(True)

# MAE: Group-wise accuracy for best LR
best_mae_results = experiment_data["learning_rate_tuning"]["mae"][f"lr_{best_mae_lr}"]
axes[1, 2].bar(["Group 0", "Group 1"], best_mae_results["group_accuracies"], alpha=0.7)
axes[1, 2].set_ylabel("Accuracy")
axes[1, 2].set_title(f"MAE: Group Accuracy (Best LR={best_mae_lr})")
axes[1, 2].grid(True, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "learning_rate_tuning_results.png"))
plt.close()

# Comparison plot
fig, ax = plt.subplots(1, 1, figsize=(10, 6))
x = np.arange(len(learning_rates))
width = 0.35

ax.bar(x - width / 2, simclr_worst_accs, width, label="SimCLR", alpha=0.8)
ax.bar(x + width / 2, mae_worst_accs, width, label="MAE", alpha=0.8)
ax.set_ylabel("Worst-Group Accuracy")
ax.set_xlabel("Learning Rate")
ax.set_title("Worst-Group Accuracy: SimCLR vs MAE across Learning Rates")
ax.set_xticks(x)
ax.set_xticklabels([f"{lr}" for lr in learning_rates])
ax.legend()
ax.grid(True, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "comparison_learning_rates.png"))
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print("\n" + "=" * 50)
print("FINAL SUMMARY")
print("=" * 50)
print(f"Best SimCLR: lr={best_simclr_lr}, Worst-Group Acc={best_simclr_worst_acc:.4f}")
print(f"Best MAE: lr={best_mae_lr}, Worst-Group Acc={best_mae_worst_acc:.4f}")
print(f"Improvement (SimCLR - MAE): {best_simclr_worst_acc - best_mae_worst_acc:.4f}")
print("=" * 50)
