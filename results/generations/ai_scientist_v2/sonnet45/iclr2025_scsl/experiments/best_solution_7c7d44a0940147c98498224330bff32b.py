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

# Initialize experiment data storage
experiment_data = {
    "simclr": {
        "pretrain_losses": [],
        "linear_probe_train_losses": [],
        "linear_probe_val_losses": [],
        "avg_accuracy": 0.0,
        "worst_group_accuracy": 0.0,
        "group_accuracies": [],
    },
    "mae": {
        "pretrain_losses": [],
        "linear_probe_train_losses": [],
        "linear_probe_val_losses": [],
        "avg_accuracy": 0.0,
        "worst_group_accuracy": 0.0,
        "group_accuracies": [],
    },
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
            label = idx % 2  # 0: circle, 1: square

            # Determine spurious attribute (texture: 0=horizontal, 1=vertical)
            if shift_spurious:
                # Test set: 50% correlation holds, 50% broken
                if idx % 2 == 0:
                    spurious_attr = label  # Correlation holds
                    group = 0  # Majority group
                else:
                    spurious_attr = 1 - label  # Correlation broken
                    group = 1  # Minority group
            else:
                # Training set: high correlation
                if np.random.rand() < spurious_corr:
                    spurious_attr = label  # Correlated
                else:
                    spurious_attr = 1 - label  # Anti-correlated
                group = 0 if spurious_attr == label else 1

            # Create image with STRONG spurious texture and WEAK true shape
            img = np.zeros((img_size, img_size), dtype=np.float32)

            # Add STRONG spurious texture (more prominent)
            texture_intensity = 0.7
            if spurious_attr == 0:  # Horizontal lines
                for i in range(0, img_size, 3):
                    img[i : i + 2, :] = texture_intensity
            else:  # Vertical lines
                for i in range(0, img_size, 3):
                    img[:, i : i + 2] = texture_intensity

            # Add WEAK true shape on top (less prominent, with noise)
            center = img_size // 2
            radius = 8
            shape_intensity = 0.4
            noise = np.random.normal(0, 0.1, (img_size, img_size))

            if label == 0:  # Circle
                y, x = np.ogrid[:img_size, :img_size]
                mask = (x - center) ** 2 + (y - center) ** 2 <= radius**2
                img[mask] = np.clip(img[mask] + shape_intensity + noise[mask], 0, 1)
            else:  # Square
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
        img = torch.FloatTensor(self.images[idx]).unsqueeze(0)  # Add channel dimension
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
print(f"Train groups distribution: {np.bincount(train_dataset.groups)}")
print(f"Test groups distribution: {np.bincount(test_dataset.groups)}")

# Visualize samples
fig, axes = plt.subplots(2, 4, figsize=(12, 6))
for i in range(4):
    axes[0, i].imshow(train_dataset.images[i], cmap="gray")
    axes[0, i].set_title(
        f"Train: L={train_dataset.labels[i]}, S={train_dataset.spurious_attrs[i]}"
    )
    axes[0, i].axis("off")

    axes[1, i].imshow(test_dataset.images[i], cmap="gray")
    axes[1, i].set_title(
        f"Test: L={test_dataset.labels[i]}, S={test_dataset.spurious_attrs[i]}"
    )
    axes[1, i].axis("off")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dataset_samples.png"))
plt.close()


# Shared Encoder
class Encoder(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(1, 32, 3, stride=2, padding=1),  # 28 -> 14
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),  # 14 -> 7
            nn.ReLU(),
            nn.Conv2d(64, 128, 3, stride=2, padding=1),  # 7 -> 4
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),  # -> 1x1
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

    # Create labels: positive pairs are (i, i+batch_size)
    labels = torch.arange(batch_size).to(device)
    labels = torch.cat([labels + batch_size, labels])

    # Mask out self-similarities
    mask = torch.eye(2 * batch_size, dtype=torch.bool).to(device)
    similarity_matrix = similarity_matrix.masked_fill(mask, -9e15)

    # Compute loss
    loss = F.cross_entropy(similarity_matrix, labels)
    return loss


# MAE Model with fixed decoder dimensions
class MAE(nn.Module):
    def __init__(self, embedding_dim=128, mask_ratio=0.75):
        super().__init__()
        self.encoder = Encoder(embedding_dim)
        self.mask_ratio = mask_ratio

        # Decoder: explicitly design to output 28x28
        # Start from 7x7 feature map
        self.decoder_fc = nn.Linear(embedding_dim, 128 * 7 * 7)
        self.decoder_network = nn.Sequential(
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1),  # 7 -> 14
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1),  # 14 -> 28
            nn.ReLU(),
            nn.Conv2d(32, 1, kernel_size=3, padding=1),  # 28 -> 28
            nn.Sigmoid(),
        )

    def forward(self, x):
        batch_size, channels, height_orig, width_orig = x.shape
        assert (
            height_orig == 28 and width_orig == 28
        ), f"Expected 28x28 input, got {height_orig}x{width_orig}"

        # Encode
        encoded = self.encoder(x)

        # Decode
        decoder_input = self.decoder_fc(encoded)
        decoder_input = decoder_input.view(batch_size, 128, 7, 7)
        reconstructed = self.decoder_network(decoder_input)

        assert (
            reconstructed.shape == x.shape
        ), f"Decoder output {reconstructed.shape} != input {x.shape}"
        return reconstructed

    def get_representation(self, x):
        return self.encoder(x)


# Simple augmentation for contrastive learning
def augment(x):
    # Random horizontal flip
    if torch.rand(1) > 0.5:
        x = torch.flip(x, [3])
    # Random noise
    noise = torch.randn_like(x) * 0.1
    x = torch.clamp(x + noise, 0, 1)
    return x


# Pre-train SimCLR
print("\n" + "=" * 50)
print("Pre-training SimCLR...")
print("=" * 50)
simclr_model = SimCLR(embedding_dim=128, projection_dim=64).to(device)
simclr_optimizer = torch.optim.Adam(simclr_model.parameters(), lr=1e-3)

simclr_epochs = 20
for epoch in range(simclr_epochs):
    simclr_model.train()
    total_loss = 0
    for imgs, _, _ in train_loader:
        imgs = imgs.to(device)

        # Create two augmented views
        x1 = augment(imgs)
        x2 = augment(imgs)

        z1, z2 = simclr_model(x1, x2)
        loss = contrastive_loss(z1, z2)

        simclr_optimizer.zero_grad()
        loss.backward()
        simclr_optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / len(train_loader)
    experiment_data["simclr"]["pretrain_losses"].append(avg_loss)
    print(f"Epoch {epoch+1}/{simclr_epochs}: SimCLR Loss = {avg_loss:.4f}")

# Pre-train MAE
print("\n" + "=" * 50)
print("Pre-training MAE...")
print("=" * 50)
mae_model = MAE(embedding_dim=128, mask_ratio=0.75).to(device)
mae_optimizer = torch.optim.Adam(mae_model.parameters(), lr=1e-3)

mae_epochs = 20
for epoch in range(mae_epochs):
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
    experiment_data["mae"]["pretrain_losses"].append(avg_loss)
    print(f"Epoch {epoch+1}/{mae_epochs}: MAE Loss = {avg_loss:.4f}")


# Extract features for linear probing
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


print("\n" + "=" * 50)
print("Extracting features...")
print("=" * 50)

# SimCLR features
simclr_train_features, simclr_train_labels, simclr_train_groups = extract_features(
    simclr_model, train_loader
)
simclr_test_features, simclr_test_labels, simclr_test_groups = extract_features(
    simclr_model, test_loader
)

# MAE features
mae_train_features, mae_train_labels, mae_train_groups = extract_features(
    mae_model, train_loader
)
mae_test_features, mae_test_labels, mae_test_groups = extract_features(
    mae_model, test_loader
)

print(f"SimCLR train features shape: {simclr_train_features.shape}")
print(f"SimCLR test features shape: {simclr_test_features.shape}")
print(f"MAE train features shape: {mae_train_features.shape}")
print(f"MAE test features shape: {mae_test_features.shape}")

# Train linear probes
print("\n" + "=" * 50)
print("Training linear probes...")
print("=" * 50)

simclr_probe = LogisticRegression(max_iter=1000, random_state=42)
simclr_probe.fit(simclr_train_features, simclr_train_labels)

mae_probe = LogisticRegression(max_iter=1000, random_state=42)
mae_probe.fit(mae_train_features, mae_train_labels)


# Evaluate with group-wise accuracy
def evaluate_worst_group(probe, features, labels, groups):
    predictions = probe.predict(features)

    # Overall accuracy
    overall_acc = np.mean(predictions == labels)

    # Group-wise accuracy
    unique_groups = np.unique(groups)
    group_accs = []
    for g in unique_groups:
        group_mask = groups == g
        group_pred = predictions[group_mask]
        group_label = labels[group_mask]
        group_acc = np.mean(group_pred == group_label)
        group_accs.append(group_acc)
        print(f"  Group {g}: {np.sum(group_mask)} samples, accuracy = {group_acc:.4f}")

    worst_group_acc = min(group_accs)
    return overall_acc, worst_group_acc, group_accs


print("\nSimCLR Evaluation:")
simclr_avg_acc, simclr_worst_acc, simclr_group_accs = evaluate_worst_group(
    simclr_probe, simclr_test_features, simclr_test_labels, simclr_test_groups
)
print(
    f"SimCLR - Average Accuracy: {simclr_avg_acc:.4f}, Worst-Group Accuracy: {simclr_worst_acc:.4f}"
)

print("\nMAE Evaluation:")
mae_avg_acc, mae_worst_acc, mae_group_accs = evaluate_worst_group(
    mae_probe, mae_test_features, mae_test_labels, mae_test_groups
)
print(
    f"MAE - Average Accuracy: {mae_avg_acc:.4f}, Worst-Group Accuracy: {mae_worst_acc:.4f}"
)

# Store results
experiment_data["simclr"]["avg_accuracy"] = float(simclr_avg_acc)
experiment_data["simclr"]["worst_group_accuracy"] = float(simclr_worst_acc)
experiment_data["simclr"]["group_accuracies"] = [float(x) for x in simclr_group_accs]

experiment_data["mae"]["avg_accuracy"] = float(mae_avg_acc)
experiment_data["mae"]["worst_group_accuracy"] = float(mae_worst_acc)
experiment_data["mae"]["group_accuracies"] = [float(x) for x in mae_group_accs]

# Visualize results
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Pre-training losses
axes[0].plot(experiment_data["simclr"]["pretrain_losses"], label="SimCLR")
axes[0].plot(experiment_data["mae"]["pretrain_losses"], label="MAE")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Pre-training Loss")
axes[0].set_title("Pre-training Losses")
axes[0].legend()
axes[0].grid(True)

# Average vs Worst-Group Accuracy
models = ["SimCLR", "MAE"]
avg_accs = [simclr_avg_acc, mae_avg_acc]
worst_accs = [simclr_worst_acc, mae_worst_acc]

x = np.arange(len(models))
width = 0.35

axes[1].bar(x - width / 2, avg_accs, width, label="Average Accuracy", alpha=0.8)
axes[1].bar(x + width / 2, worst_accs, width, label="Worst-Group Accuracy", alpha=0.8)
axes[1].set_ylabel("Accuracy")
axes[1].set_title("Average vs Worst-Group Accuracy")
axes[1].set_xticks(x)
axes[1].set_xticklabels(models)
axes[1].legend()
axes[1].grid(True, axis="y")

# Group-wise comparison
axes[2].plot(
    ["Group 0\n(Majority)", "Group 1\n(Minority)"],
    simclr_group_accs,
    "o-",
    label="SimCLR",
    linewidth=2,
    markersize=8,
)
axes[2].plot(
    ["Group 0\n(Majority)", "Group 1\n(Minority)"],
    mae_group_accs,
    "s-",
    label="MAE",
    linewidth=2,
    markersize=8,
)
axes[2].set_ylabel("Accuracy")
axes[2].set_title("Group-wise Accuracy Comparison")
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "results_comparison.png"))
plt.close()

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print("\n" + "=" * 50)
print("FINAL RESULTS")
print("=" * 50)
print(f"SimCLR - Worst-Group Accuracy: {simclr_worst_acc:.4f}")
print(f"MAE - Worst-Group Accuracy: {mae_worst_acc:.4f}")
print(f"Gap (SimCLR - MAE): {simclr_worst_acc - mae_worst_acc:.4f}")
print("=" * 50)
