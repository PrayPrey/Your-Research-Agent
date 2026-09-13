import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from datasets import load_dataset
from PIL import Image
import torchvision.transforms as transforms

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Initialize experiment data storage for 3 datasets
experiment_data = {
    "mnist_color": {"simclr": {}, "simclr_no_proj": {}, "mae": {}},
    "cifar10_bg": {"simclr": {}, "simclr_no_proj": {}, "mae": {}},
    "fashion_pattern": {"simclr": {}, "simclr_no_proj": {}, "mae": {}},
}

for dataset_name in experiment_data:
    for method in ["simclr", "simclr_no_proj", "mae"]:
        experiment_data[dataset_name][method] = {
            "pretrain_losses": [],
            "avg_accuracy": 0.0,
            "worst_group_accuracy": 0.0,
            "group_accuracies": [],
            "sfrs": 0.0,
            "epochs": [],
        }


# Dataset 1: Color-MNIST (color spuriously correlated with digit)
class ColorMNISTDataset(Dataset):
    def __init__(self, split="train", n_samples=2000, spurious_corr=0.95):
        mnist = load_dataset("mnist", split="train" if split == "train" else "test")
        self.n_samples = min(n_samples, len(mnist))
        self.spurious_corr = spurious_corr
        self.shift_spurious = split == "test"

        self.images = []
        self.labels = []
        self.groups = []

        # Binary classification: digits 0-4 vs 5-9
        colors = [(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)]  # Red vs Blue

        for idx in range(self.n_samples):
            img = np.array(mnist[idx]["image"]).astype(np.float32) / 255.0
            label = 0 if mnist[idx]["label"] < 5 else 1

            if self.shift_spurious:
                spurious_attr = label if idx % 2 == 0 else 1 - label
            else:
                spurious_attr = label if np.random.rand() < spurious_corr else 1 - label

            group = 0 if spurious_attr == label else 1

            # Apply color
            color = colors[spurious_attr]
            colored_img = np.stack(
                [img * color[0], img * color[1], img * color[2]], axis=0
            )

            self.images.append(colored_img)
            self.labels.append(label)
            self.groups.append(group)

        self.images = np.array(self.images, dtype=np.float32)
        self.labels = np.array(self.labels)
        self.groups = np.array(self.groups)

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        return (
            torch.FloatTensor(self.images[idx]),
            torch.LongTensor([self.labels[idx]])[0],
            torch.LongTensor([self.groups[idx]])[0],
        )


# Dataset 2: CIFAR10 with background spurious correlation
class CIFAR10BackgroundDataset(Dataset):
    def __init__(self, split="train", n_samples=2000, spurious_corr=0.95):
        cifar = load_dataset("cifar10", split="train" if split == "train" else "test")
        self.n_samples = min(n_samples, len(cifar))
        self.spurious_corr = spurious_corr
        self.shift_spurious = split == "test"

        self.images = []
        self.labels = []
        self.groups = []

        for idx in range(self.n_samples):
            img = np.array(cifar[idx]["img"]).astype(np.float32) / 255.0
            img = img.transpose(2, 0, 1)  # CHW
            label = 0 if cifar[idx]["label"] < 5 else 1

            if self.shift_spurious:
                spurious_attr = label if idx % 2 == 0 else 1 - label
            else:
                spurious_attr = label if np.random.rand() < spurious_corr else 1 - label

            group = 0 if spurious_attr == label else 1

            # Add checkerboard or dots background pattern
            if spurious_attr == 0:
                for i in range(0, 32, 4):
                    for j in range(0, 32, 4):
                        if (i // 4 + j // 4) % 2 == 0:
                            img[:, i : i + 4, j : j + 4] = (
                                img[:, i : i + 4, j : j + 4] * 0.7 + 0.3
                            )
            else:
                for i in range(2, 32, 6):
                    for j in range(2, 32, 6):
                        img[:, i : i + 2, j : j + 2] = 0.8

            self.images.append(img)
            self.labels.append(label)
            self.groups.append(group)

        self.images = np.array(self.images, dtype=np.float32)
        self.labels = np.array(self.labels)
        self.groups = np.array(self.groups)

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        return (
            torch.FloatTensor(self.images[idx]),
            torch.LongTensor([self.labels[idx]])[0],
            torch.LongTensor([self.groups[idx]])[0],
        )


# Dataset 3: Fashion-MNIST with local pattern stamps
class FashionPatternDataset(Dataset):
    def __init__(self, split="train", n_samples=2000, spurious_corr=0.95):
        fashion = load_dataset(
            "fashion_mnist", split="train" if split == "train" else "test"
        )
        self.n_samples = min(n_samples, len(fashion))
        self.spurious_corr = spurious_corr
        self.shift_spurious = split == "test"

        self.images = []
        self.labels = []
        self.groups = []

        for idx in range(self.n_samples):
            img = np.array(fashion[idx]["image"]).astype(np.float32) / 255.0
            label = 0 if fashion[idx]["label"] < 5 else 1

            if self.shift_spurious:
                spurious_attr = label if idx % 2 == 0 else 1 - label
            else:
                spurious_attr = label if np.random.rand() < spurious_corr else 1 - label

            group = 0 if spurious_attr == label else 1

            # Add local pattern stamp (top-left vs bottom-right)
            if spurious_attr == 0:
                img[2:8, 2:8] = 0.9  # Top-left bright square
            else:
                img[20:26, 20:26] = 0.9  # Bottom-right bright square

            img = np.expand_dims(img, 0)
            self.images.append(img)
            self.labels.append(label)
            self.groups.append(group)

        self.images = np.array(self.images, dtype=np.float32)
        self.labels = np.array(self.labels)
        self.groups = np.array(self.groups)

    def __len__(self):
        return self.n_samples

    def __getitem__(self, idx):
        return (
            torch.FloatTensor(self.images[idx]),
            torch.LongTensor([self.labels[idx]])[0],
            torch.LongTensor([self.groups[idx]])[0],
        )


# Encoder architectures
class ColorEncoder(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(64, embedding_dim),
        )

    def forward(self, x):
        return self.network(x)


class CIFAREncoder(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(3, 64, 3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(128, embedding_dim),
        )

    def forward(self, x):
        return self.network(x)


class FashionEncoder(nn.Module):
    def __init__(self, embedding_dim=128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Conv2d(1, 32, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(64, embedding_dim),
        )

    def forward(self, x):
        return self.network(x)


# SimCLR wrapper
class SimCLR(nn.Module):
    def __init__(self, encoder, embedding_dim=128, projection_dim=64):
        super().__init__()
        self.encoder = encoder
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


# SimCLR without projection head (ABLATION)
class SimCLRNoProjection(nn.Module):
    def __init__(self, encoder, embedding_dim=128):
        super().__init__()
        self.encoder = encoder

    def forward(self, x1, x2):
        h1 = self.encoder(x1)
        h2 = self.encoder(x2)
        return h1, h2

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


# MAE wrapper (simplified for multiple input channels)
class MAE(nn.Module):
    def __init__(self, encoder, in_channels, img_size, embedding_dim=128):
        super().__init__()
        self.encoder = encoder
        self.in_channels = in_channels
        self.img_size = img_size
        latent_size = img_size // 4
        self.decoder = nn.Sequential(
            nn.Linear(embedding_dim, 128 * latent_size * latent_size),
            nn.Unflatten(1, (128, latent_size, latent_size)),
            nn.ConvTranspose2d(128, 64, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, stride=2, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, in_channels, 3, padding=1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        h = self.encoder(x)
        recon = self.decoder(h)
        return recon

    def get_representation(self, x):
        return self.encoder(x)


def augment(x):
    if torch.rand(1) > 0.5:
        x = torch.flip(x, [3])
    noise = torch.randn_like(x) * 0.05
    x = torch.clamp(x + noise, 0, 1)
    return x


def extract_features(model, loader):
    model.eval()
    all_features, all_labels, all_groups = [], [], []
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


def evaluate_worst_group(probe, features, labels, groups):
    predictions = probe.predict(features)
    overall_acc = np.mean(predictions == labels)
    unique_groups = np.unique(groups)
    group_accs = []
    for g in unique_groups:
        group_mask = groups == g
        group_acc = np.mean(predictions[group_mask] == labels[group_mask])
        group_accs.append(group_acc)
    worst_group_acc = min(group_accs)
    sfrs = (overall_acc - worst_group_acc) / (overall_acc + 1e-8)
    return overall_acc, worst_group_acc, group_accs, sfrs


# Dataset configurations
dataset_configs = [
    ("mnist_color", ColorMNISTDataset, ColorEncoder, 3, 28),
    ("cifar10_bg", CIFAR10BackgroundDataset, CIFAREncoder, 3, 32),
    ("fashion_pattern", FashionPatternDataset, FashionEncoder, 1, 28),
]

# Train and evaluate on all datasets
for (
    dataset_name,
    dataset_class,
    encoder_class,
    in_channels,
    img_size,
) in dataset_configs:
    print(f"\n{'='*60}")
    print(f"Processing {dataset_name.upper()}")
    print(f"{'='*60}")

    train_dataset = dataset_class(split="train", n_samples=1500)
    test_dataset = dataset_class(split="test", n_samples=800)
    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

    print(f"Train: {len(train_dataset)}, Test: {len(test_dataset)}")
    print(f"Train groups: {np.bincount(train_dataset.groups)}")
    print(f"Test groups: {np.bincount(test_dataset.groups)}")

    # SimCLR training (with projection head)
    print(f"\nTraining SimCLR (with projection) on {dataset_name}...")
    simclr_encoder = encoder_class(embedding_dim=128).to(device)
    simclr_model = SimCLR(simclr_encoder, embedding_dim=128, projection_dim=64).to(
        device
    )
    simclr_optimizer = torch.optim.Adam(simclr_model.parameters(), lr=1e-3)

    for epoch in range(15):
        simclr_model.train()
        total_loss = 0
        for imgs, _, _ in train_loader:
            imgs = imgs.to(device)
            x1, x2 = augment(imgs), augment(imgs)
            z1, z2 = simclr_model(x1, x2)
            loss = contrastive_loss(z1, z2)
            simclr_optimizer.zero_grad()
            loss.backward()
            simclr_optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        experiment_data[dataset_name]["simclr"]["pretrain_losses"].append(avg_loss)
        experiment_data[dataset_name]["simclr"]["epochs"].append(epoch + 1)
        print(f"Epoch {epoch+1}: SimCLR Loss = {avg_loss:.4f}")

    # SimCLR training WITHOUT projection head (ABLATION)
    print(f"\nTraining SimCLR (NO projection) on {dataset_name}...")
    simclr_no_proj_encoder = encoder_class(embedding_dim=128).to(device)
    simclr_no_proj_model = SimCLRNoProjection(
        simclr_no_proj_encoder, embedding_dim=128
    ).to(device)
    simclr_no_proj_optimizer = torch.optim.Adam(
        simclr_no_proj_model.parameters(), lr=1e-3
    )

    for epoch in range(15):
        simclr_no_proj_model.train()
        total_loss = 0
        for imgs, _, _ in train_loader:
            imgs = imgs.to(device)
            x1, x2 = augment(imgs), augment(imgs)
            z1, z2 = simclr_no_proj_model(x1, x2)
            loss = contrastive_loss(z1, z2)
            simclr_no_proj_optimizer.zero_grad()
            loss.backward()
            simclr_no_proj_optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        experiment_data[dataset_name]["simclr_no_proj"]["pretrain_losses"].append(
            avg_loss
        )
        experiment_data[dataset_name]["simclr_no_proj"]["epochs"].append(epoch + 1)
        print(f"Epoch {epoch+1}: SimCLR (No Proj) Loss = {avg_loss:.4f}")

    # MAE training
    print(f"\nTraining MAE on {dataset_name}...")
    mae_encoder = encoder_class(embedding_dim=128).to(device)
    mae_model = MAE(mae_encoder, in_channels, img_size, embedding_dim=128).to(device)
    mae_optimizer = torch.optim.Adam(mae_model.parameters(), lr=1e-3)

    for epoch in range(15):
        mae_model.train()
        total_loss = 0
        for imgs, _, _ in train_loader:
            imgs = imgs.to(device)
            recon = mae_model(imgs)
            loss = F.mse_loss(recon, imgs)
            mae_optimizer.zero_grad()
            loss.backward()
            mae_optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(train_loader)
        experiment_data[dataset_name]["mae"]["pretrain_losses"].append(avg_loss)
        experiment_data[dataset_name]["mae"]["epochs"].append(epoch + 1)
        print(f"Epoch {epoch+1}: MAE Loss = {avg_loss:.4f}")

    # Evaluation
    print(f"\nEvaluating {dataset_name}...")
    simclr_train_f, simclr_train_l, _ = extract_features(simclr_model, train_loader)
    simclr_test_f, simclr_test_l, simclr_test_g = extract_features(
        simclr_model, test_loader
    )
    simclr_no_proj_train_f, simclr_no_proj_train_l, _ = extract_features(
        simclr_no_proj_model, train_loader
    )
    simclr_no_proj_test_f, simclr_no_proj_test_l, simclr_no_proj_test_g = (
        extract_features(simclr_no_proj_model, test_loader)
    )
    mae_train_f, mae_train_l, _ = extract_features(mae_model, train_loader)
    mae_test_f, mae_test_l, mae_test_g = extract_features(mae_model, test_loader)

    simclr_probe = LogisticRegression(max_iter=1000).fit(simclr_train_f, simclr_train_l)
    simclr_no_proj_probe = LogisticRegression(max_iter=1000).fit(
        simclr_no_proj_train_f, simclr_no_proj_train_l
    )
    mae_probe = LogisticRegression(max_iter=1000).fit(mae_train_f, mae_train_l)

    simclr_avg, simclr_worst, simclr_groups, simclr_sfrs = evaluate_worst_group(
        simclr_probe, simclr_test_f, simclr_test_l, simclr_test_g
    )
    (
        simclr_no_proj_avg,
        simclr_no_proj_worst,
        simclr_no_proj_groups,
        simclr_no_proj_sfrs,
    ) = evaluate_worst_group(
        simclr_no_proj_probe,
        simclr_no_proj_test_f,
        simclr_no_proj_test_l,
        simclr_no_proj_test_g,
    )
    mae_avg, mae_worst, mae_groups, mae_sfrs = evaluate_worst_group(
        mae_probe, mae_test_f, mae_test_l, mae_test_g
    )

    experiment_data[dataset_name]["simclr"].update(
        {
            "avg_accuracy": float(simclr_avg),
            "worst_group_accuracy": float(simclr_worst),
            "group_accuracies": [float(x) for x in simclr_groups],
            "sfrs": float(simclr_sfrs),
        }
    )

    experiment_data[dataset_name]["simclr_no_proj"].update(
        {
            "avg_accuracy": float(simclr_no_proj_avg),
            "worst_group_accuracy": float(simclr_no_proj_worst),
            "group_accuracies": [float(x) for x in simclr_no_proj_groups],
            "sfrs": float(simclr_no_proj_sfrs),
        }
    )

    experiment_data[dataset_name]["mae"].update(
        {
            "avg_accuracy": float(mae_avg),
            "worst_group_accuracy": float(mae_worst),
            "group_accuracies": [float(x) for x in mae_groups],
            "sfrs": float(mae_sfrs),
        }
    )

    print(
        f"SimCLR (w/ proj): Avg={simclr_avg:.3f}, Worst={simclr_worst:.3f}, SFRS={simclr_sfrs:.3f}"
    )
    print(
        f"SimCLR (no proj): Avg={simclr_no_proj_avg:.3f}, Worst={simclr_no_proj_worst:.3f}, SFRS={simclr_no_proj_sfrs:.3f}"
    )
    print(f"MAE: Avg={mae_avg:.3f}, Worst={mae_worst:.3f}, SFRS={mae_sfrs:.3f}")

# Visualization
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
dataset_names = ["mnist_color", "cifar10_bg", "fashion_pattern"]
titles = ["Color-MNIST", "CIFAR10-BG", "Fashion-Pattern"]

for idx, (dname, title) in enumerate(zip(dataset_names, titles)):
    # Loss curves
    axes[idx, 0].plot(
        experiment_data[dname]["simclr"]["epochs"],
        experiment_data[dname]["simclr"]["pretrain_losses"],
        label="SimCLR (w/ proj)",
    )
    axes[idx, 0].plot(
        experiment_data[dname]["simclr_no_proj"]["epochs"],
        experiment_data[dname]["simclr_no_proj"]["pretrain_losses"],
        label="SimCLR (no proj)",
    )
    axes[idx, 0].plot(
        experiment_data[dname]["mae"]["epochs"],
        experiment_data[dname]["mae"]["pretrain_losses"],
        label="MAE",
    )
    axes[idx, 0].set_title(f"{title}: Pretraining Loss")
    axes[idx, 0].set_xlabel("Epoch")
    axes[idx, 0].set_ylabel("Loss")
    axes[idx, 0].legend()
    axes[idx, 0].grid(True)

    # Group accuracies
    axes[idx, 1].bar(
        [
            "SimCLR\n(proj)\nMaj",
            "SimCLR\n(proj)\nMin",
            "SimCLR\n(no)\nMaj",
            "SimCLR\n(no)\nMin",
            "MAE\nMaj",
            "MAE\nMin",
        ],
        experiment_data[dname]["simclr"]["group_accuracies"]
        + experiment_data[dname]["simclr_no_proj"]["group_accuracies"]
        + experiment_data[dname]["mae"]["group_accuracies"],
    )
    axes[idx, 1].set_title(f"{title}: Group Accuracies")
    axes[idx, 1].set_ylabel("Accuracy")
    axes[idx, 1].grid(True, axis="y")
    axes[idx, 1].tick_params(axis="x", labelsize=8)

    # SFRS comparison
    sfrs_vals = [
        experiment_data[dname]["simclr"]["sfrs"],
        experiment_data[dname]["simclr_no_proj"]["sfrs"],
        experiment_data[dname]["mae"]["sfrs"],
    ]
    axes[idx, 2].bar(["SimCLR\n(w/ proj)", "SimCLR\n(no proj)", "MAE"], sfrs_vals)
    axes[idx, 2].set_title(f"{title}: SFRS (Lower=Better)")
    axes[idx, 2].set_ylabel("SFRS")
    axes[idx, 2].grid(True, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_no_projection_comparison.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print(f"\n{'='*60}")
print("FINAL SUMMARY ACROSS ALL DATASETS")
print(f"{'='*60}")
for dname, title in zip(dataset_names, titles):
    print(f"\n{title}:")
    print(
        f"  SimCLR (w/ proj): Worst-Group={experiment_data[dname]['simclr']['worst_group_accuracy']:.3f}, SFRS={experiment_data[dname]['simclr']['sfrs']:.3f}"
    )
    print(
        f"  SimCLR (no proj): Worst-Group={experiment_data[dname]['simclr_no_proj']['worst_group_accuracy']:.3f}, SFRS={experiment_data[dname]['simclr_no_proj']['sfrs']:.3f}"
    )
    print(
        f"  MAE: Worst-Group={experiment_data[dname]['mae']['worst_group_accuracy']:.3f}, SFRS={experiment_data[dname]['mae']['sfrs']:.3f}"
    )
print(f"{'='*60}")
