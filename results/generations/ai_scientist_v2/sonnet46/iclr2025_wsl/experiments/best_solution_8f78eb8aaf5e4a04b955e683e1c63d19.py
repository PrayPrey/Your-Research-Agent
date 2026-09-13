import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Subset
import torchvision
import torchvision.transforms as transforms
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import r2_score
from datasets import load_dataset
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import time
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

N_MODELS = 300
META_EPOCHS = 150
TRAIN_EPOCHS = 6
N_FOLDS = 5

experiment_data = {}


# ── Tiny CNN for 32x32 RGB ────────────────────────────────────────
class TinyCNN(nn.Module):
    def __init__(self, num_classes=10, in_channels=3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(4),
        )
        self.classifier = nn.Sequential(
            nn.Linear(64 * 4 * 4, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        return self.classifier(self.features(x).flatten(1))


class TinyCNN_small(nn.Module):
    """For 28x28 grayscale"""

    def __init__(self, num_classes=10, in_channels=1):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(32 * 7 * 7, 64), nn.ReLU(), nn.Linear(64, num_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x).flatten(1))


def extract_rich_features(model):
    """Extract rich weight statistics including spectral features."""
    feats = []
    layer_names = []
    for name, p in model.named_parameters():
        w = p.data.cpu().numpy().flatten()
        layer_names.append(name)
        # Basic statistics
        feats.extend(
            [
                w.mean(),
                w.std(),
                np.percentile(w, 5),
                np.percentile(w, 25),
                np.percentile(w, 50),
                np.percentile(w, 75),
                np.percentile(w, 95),
                np.abs(w).mean(),
                np.abs(w).max(),
                (w > 0).mean(),
                float(np.sum(np.abs(w) < 1e-4)) / max(len(w), 1),
                np.abs(w).var(),
            ]
        )
        # Higher-order moments
        if w.std() > 1e-8:
            skew = float(np.mean(((w - w.mean()) / w.std()) ** 3))
            kurt = float(np.mean(((w - w.mean()) / w.std()) ** 4))
        else:
            skew, kurt = 0.0, 0.0
        feats.extend([skew, kurt])
        # Spectral features for weight matrices
        pw = p.data.cpu().numpy()
        if pw.ndim >= 2:
            mat = pw.reshape(pw.shape[0], -1)
            if mat.shape[0] >= 2 and mat.shape[1] >= 2:
                try:
                    sv = np.linalg.svd(mat, compute_uv=False)
                    sv = sv[: min(8, len(sv))]
                    feats.extend(
                        [
                            sv[0],
                            sv[-1],
                            sv[0] / (sv[-1] + 1e-8),
                            np.sum(sv[:4]) / (np.sum(sv) + 1e-8),
                            float(np.sum(sv > 1e-3)),
                        ]
                    )
                except:
                    feats.extend([0.0] * 5)
            else:
                feats.extend([0.0] * 5)
        else:
            feats.extend([0.0] * 5)
    return np.array(feats, dtype=np.float32), layer_names


def train_small_model(loader, model, epochs=6):
    model = model.to(device)
    opt = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    model.train()
    for _ in range(epochs):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad()
            loss = criterion(model(xb), yb)
            loss.backward()
            opt.step()
        sched.step()
    return model


def build_meta_model(feat_dim, hidden=256):
    return nn.Sequential(
        nn.Linear(feat_dim, hidden),
        nn.LayerNorm(hidden),
        nn.ReLU(),
        nn.Dropout(0.4),
        nn.Linear(hidden, 128),
        nn.LayerNorm(128),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(128, 64),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(64, 1),
    ).to(device)


def train_meta_kfold(X_norm, y, feat_dim, meta_epochs=150, n_folds=5, seed=42):
    """K-fold cross-validation for reliable R² estimation."""
    y_min, y_max = y.min(), y.max()
    y_scaled = (y - y_min) / (y_max - y_min + 1e-8)

    kf = KFold(n_splits=n_folds, shuffle=True, random_state=seed)
    fold_test_r2s = []
    all_train_r2 = []
    all_val_r2 = []
    best_fold_data = None

    for fold, (train_idx, test_idx) in enumerate(kf.split(X_norm)):
        X_tr, X_te = X_norm[train_idx], X_norm[test_idx]
        y_tr, y_te = y_scaled[train_idx], y_scaled[test_idx]

        X_tr_t = torch.tensor(X_tr, dtype=torch.float32).to(device)
        y_tr_t = torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1).to(device)
        X_te_t = torch.tensor(X_te, dtype=torch.float32).to(device)

        dl = DataLoader(TensorDataset(X_tr_t, y_tr_t), batch_size=32, shuffle=True)
        meta = build_meta_model(feat_dim)
        opt = optim.Adam(meta.parameters(), lr=1e-3, weight_decay=5e-4)
        sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=meta_epochs)
        crit = nn.MSELoss()

        fold_train_r2s, fold_val_r2s, fold_train_loss, fold_val_loss = [], [], [], []

        for epoch in range(1, meta_epochs + 1):
            meta.train()
            ep_preds, ep_true, ep_loss = [], [], []
            for xb, yb in dl:
                opt.zero_grad()
                pred = meta(xb)
                loss = crit(pred, yb)
                loss.backward()
                opt.step()
                ep_loss.append(loss.item())
                ep_preds.append(pred.detach().cpu().numpy())
                ep_true.append(yb.cpu().numpy())
            sched.step()

            tr2 = r2_score(
                np.concatenate(ep_true).flatten(), np.concatenate(ep_preds).flatten()
            )
            tl = np.mean(ep_loss)

            meta.eval()
            with torch.no_grad():
                vp = meta(X_te_t).cpu().numpy().flatten()
            vl = np.mean((vp - y_te) ** 2)
            vr2 = r2_score(y_te, vp)

            fold_train_r2s.append(tr2)
            fold_val_r2s.append(vr2)
            fold_train_loss.append(tl)
            fold_val_loss.append(vl)

        all_train_r2.append(fold_train_r2s)
        all_val_r2.append(fold_val_r2s)

        meta.eval()
        with torch.no_grad():
            tp = meta(X_te_t).cpu().numpy().flatten()
        test_r2 = r2_score(y_te, tp)
        fold_test_r2s.append(test_r2)

        test_pred_orig = tp * (y_max - y_min + 1e-8) + y_min
        test_true_orig = y_te * (y_max - y_min + 1e-8) + y_min

        if best_fold_data is None or test_r2 > (
            best_fold_data["test_r2"] if best_fold_data else -1
        ):
            best_fold_data = {
                "losses": {"train": fold_train_loss, "val": fold_val_loss},
                "r2_scores": {"train": fold_train_r2s, "val": fold_val_r2s},
                "metrics": {"train": fold_train_r2s, "val": fold_val_r2s},
                "test_r2": test_r2,
                "predictions": test_pred_orig.tolist(),
                "ground_truth": test_true_orig.tolist(),
            }

        print(f"  Fold {fold+1}/{n_folds}: test_r2={test_r2:.4f}")

    mean_r2 = np.mean(fold_test_r2s)
    std_r2 = np.std(fold_test_r2s)
    print(f"  => K-Fold R²: {mean_r2:.4f} ± {std_r2:.4f}")

    best_fold_data["kfold_mean_r2"] = mean_r2
    best_fold_data["kfold_std_r2"] = std_r2
    best_fold_data["all_fold_r2s"] = fold_test_r2s
    best_fold_data["mean_train_r2_by_epoch"] = np.mean(all_train_r2, axis=0).tolist()
    best_fold_data["mean_val_r2_by_epoch"] = np.mean(all_val_r2, axis=0).tolist()
    return best_fold_data


def layer_importance_ablation(X_norm, y, layer_sizes, feat_dim, n_features_per_layer):
    """Measure importance of each layer's weight features."""
    y_min, y_max = y.min(), y.max()
    y_scaled = (y - y_min) / (y_max - y_min + 1e-8)
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_norm, y_scaled, test_size=0.2, random_state=42
    )

    # Full model baseline
    meta = build_meta_model(feat_dim)
    opt = optim.Adam(meta.parameters(), lr=1e-3, weight_decay=5e-4)
    dl = DataLoader(
        TensorDataset(
            torch.tensor(X_tr).to(device),
            torch.tensor(y_tr, dtype=torch.float32).unsqueeze(1).to(device),
        ),
        batch_size=32,
        shuffle=True,
    )
    for _ in range(80):
        meta.train()
        for xb, yb in dl:
            opt.zero_grad()
            loss = nn.MSELoss()(meta(xb), yb)
            loss.backward()
            opt.step()
    meta.eval()
    with torch.no_grad():
        base_r2 = r2_score(
            y_te, meta(torch.tensor(X_te).to(device)).cpu().numpy().flatten()
        )

    # Ablate each layer group
    importance = []
    start = 0
    for lsize in layer_sizes:
        end = start + lsize
        X_ablated = X_norm.copy()
        X_ablated[:, start:end] = 0.0
        with torch.no_grad():
            ablated_r2 = r2_score(
                y_te,
                meta(torch.tensor(X_ablated[len(X_tr) :]).to(device))
                .cpu()
                .numpy()
                .flatten(),
            )
        importance.append(base_r2 - ablated_r2)
        start = end
    return importance, base_r2


# ════════════════════════════════════════════════════════════════════
# DATASET 1: CIFAR-10 (torchvision) — Class Imbalance + Noise (Joint)
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("DATASET 1: CIFAR-10 — Class Imbalance (torchvision)")
print("=" * 60)

transform_cifar = transforms.Compose(
    [
        transforms.ToTensor(),
        transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    ]
)
cifar_train = torchvision.datasets.CIFAR10(
    root="./working/data", train=True, download=True, transform=transform_cifar
)
cifar_labels = np.array(cifar_train.targets)
cifar_class_idx = {c: np.where(cifar_labels == c)[0] for c in range(10)}


def make_cifar_imbalanced_noisy_loader(ratio, noise_rate, seed=0):
    np.random.seed(seed)
    minority = list(range(5, 10))
    majority = list(range(0, 5))
    n_maj = 400
    n_min = max(1, int(n_maj / ratio))
    selected, selected_lbl = [], []
    for c in majority:
        idx = cifar_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_maj]
        selected.extend(chosen.tolist())
        selected_lbl.extend(cifar_labels[chosen].tolist())
    for c in minority:
        idx = cifar_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_min]
        selected.extend(chosen.tolist())
        selected_lbl.extend(cifar_labels[chosen].tolist())
    # Apply label noise
    lbls = np.array(selected_lbl)
    n_noisy = int(noise_rate * len(lbls))
    if n_noisy > 0:
        noise_pos = np.random.choice(len(lbls), n_noisy, replace=False)
        lbls[noise_pos] = np.random.randint(0, 10, n_noisy)
    subset = Subset(cifar_train, selected)
    # Override labels with noisy ones
    imgs_t = torch.stack([cifar_train[i][0] for i in selected])
    lbls_t = torch.tensor(lbls, dtype=torch.long)
    ds = TensorDataset(imgs_t, lbls_t)
    return DataLoader(ds, batch_size=128, shuffle=True, num_workers=0)


np.random.seed(42)
cifar_ratios = np.random.uniform(1.0, 15.0, N_MODELS)
cifar_noises = np.random.uniform(0.0, 0.35, N_MODELS)
cifar_feats, cifar_imbalance_targets, cifar_noise_targets = [], [], []
t0 = time.time()
for i, (ratio, noise) in enumerate(zip(cifar_ratios, cifar_noises)):
    torch.manual_seed(i + 100)
    loader = make_cifar_imbalanced_noisy_loader(ratio, noise, seed=i + 100)
    model = train_small_model(loader, TinyCNN(10, 3), TRAIN_EPOCHS)
    feats, _ = extract_rich_features(model)
    cifar_feats.append(feats)
    cifar_imbalance_targets.append(ratio)
    cifar_noise_targets.append(noise)
    if (i + 1) % 75 == 0:
        print(f"  CIFAR-10: {i+1}/{N_MODELS} | {time.time()-t0:.0f}s")

X_cifar = np.stack(cifar_feats)
y_cifar_imb = np.array(cifar_imbalance_targets, dtype=np.float32)
y_cifar_noise = np.array(cifar_noise_targets, dtype=np.float32)
X_cifar_n = (X_cifar - X_cifar.mean(0)) / (X_cifar.std(0) + 1e-8)
feat_dim_cifar = X_cifar_n.shape[1]
print(f"CIFAR-10 feature dim: {feat_dim_cifar}")

print("Training meta-model: CIFAR-10 Imbalance (K-fold)...")
cifar_imb_result = train_meta_kfold(
    X_cifar_n, y_cifar_imb, feat_dim_cifar, META_EPOCHS, N_FOLDS
)
experiment_data["cifar10_imbalance"] = cifar_imb_result

print("Training meta-model: CIFAR-10 Noise Rate (K-fold)...")
cifar_noise_result = train_meta_kfold(
    X_cifar_n, y_cifar_noise, feat_dim_cifar, META_EPOCHS, N_FOLDS
)
experiment_data["cifar10_noise"] = cifar_noise_result

np.save(os.path.join(working_dir, "cifar10_features.npy"), X_cifar)
np.save(os.path.join(working_dir, "cifar10_targets_imb.npy"), y_cifar_imb)
np.save(os.path.join(working_dir, "cifar10_targets_noise.npy"), y_cifar_noise)

# ════════════════════════════════════════════════════════════════════
# DATASET 2: HuggingFace CIFAR-100 — Label Noise Rate
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("DATASET 2: HuggingFace CIFAR-100 — Label Noise Rate")
print("=" * 60)

hf_cifar100 = load_dataset("cifar100", split="train")
print(f"CIFAR-100 loaded: {len(hf_cifar100)} samples")
assert len(hf_cifar100) > 40000, f"Expected CIFAR-100 ~50k, got {len(hf_cifar100)}"

c100_imgs = np.array([np.array(ex["img"]) for ex in hf_cifar100])
c100_lbls = np.array([ex["fine_label"] for ex in hf_cifar100])
assert c100_imgs.shape[1:] == (
    32,
    32,
    3,
), f"Expected 32x32x3, got {c100_imgs.shape[1:]}"
print(f"CIFAR-100 shape verified: {c100_imgs.shape}")
NUM_C100 = 100

c100_mean = np.array([0.5071, 0.4867, 0.4408])
c100_std = np.array([0.2675, 0.2565, 0.2761])


def make_c100_noisy_imb_loader(noise_rate, ratio, seed=0, n_per_class=35):
    np.random.seed(seed)
    selected_idx, selected_lbl = [], []
    # Apply both noise and imbalance (half classes are minority)
    minority_classes = list(range(50, 100))
    majority_classes = list(range(0, 50))
    n_min = max(1, int(n_per_class / ratio))
    for c in majority_classes:
        idx = np.where(c100_lbls == c)[0]
        np.random.shuffle(idx)
        chosen = idx[:n_per_class]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(c100_lbls[chosen].tolist())
    for c in minority_classes:
        idx = np.where(c100_lbls == c)[0]
        np.random.shuffle(idx)
        chosen = idx[:n_min]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(c100_lbls[chosen].tolist())
    lbls = np.array(selected_lbl)
    n_noisy = int(noise_rate * len(lbls))
    if n_noisy > 0:
        noise_pos = np.random.choice(len(lbls), n_noisy, replace=False)
        lbls[noise_pos] = np.random.randint(0, NUM_C100, n_noisy)
    imgs_sel = c100_imgs[selected_idx]
    X_t = torch.tensor(imgs_sel, dtype=torch.float32).permute(0, 3, 1, 2) / 255.0
    for c in range(3):
        X_t[:, c] = (X_t[:, c] - c100_mean[c]) / c100_std[c]
    y_t = torch.tensor(lbls, dtype=torch.long)
    return DataLoader(
        TensorDataset(X_t, y_t), batch_size=256, shuffle=True, num_workers=0
    )


np.random.seed(42)
c100_noises = np.random.uniform(0.0, 0.4, N_MODELS)
c100_ratios = np.random.uniform(1.0, 10.0, N_MODELS)
c100_feats, c100_noise_targets, c100_ratio_targets = [], [], []
t0 = time.time()
for i, (nr, rt) in enumerate(zip(c100_noises, c100_ratios)):
    torch.manual_seed(i + 200)
    loader = make_c100_noisy_imb_loader(nr, rt, seed=i + 200, n_per_class=35)
    model = train_small_model(loader, TinyCNN(NUM_C100, 3), TRAIN_EPOCHS)
    feats, _ = extract_rich_features(model)
    c100_feats.append(feats)
    c100_noise_targets.append(nr)
    c100_ratio_targets.append(rt)
    if (i + 1) % 75 == 0:
        print(f"  CIFAR-100: {i+1}/{N_MODELS} | {time.time()-t0:.0f}s")

X_c100 = np.stack(c100_feats)
y_c100_noise = np.array(c100_noise_targets, dtype=np.float32)
y_c100_ratio = np.array(c100_ratio_targets, dtype=np.float32)
X_c100_n = (X_c100 - X_c100.mean(0)) / (X_c100.std(0) + 1e-8)
feat_dim_c100 = X_c100_n.shape[1]

print("Training meta-model: CIFAR-100 Noise (K-fold)...")
c100_noise_result = train_meta_kfold(
    X_c100_n, y_c100_noise, feat_dim_c100, META_EPOCHS, N_FOLDS
)
experiment_data["cifar100_noise"] = c100_noise_result

print("Training meta-model: CIFAR-100 Imbalance (K-fold)...")
c100_imb_result = train_meta_kfold(
    X_c100_n, y_c100_ratio, feat_dim_c100, META_EPOCHS, N_FOLDS
)
experiment_data["cifar100_imbalance"] = c100_imb_result

np.save(os.path.join(working_dir, "cifar100_features.npy"), X_c100)
np.save(os.path.join(working_dir, "cifar100_targets_noise.npy"), y_c100_noise)
np.save(os.path.join(working_dir, "cifar100_targets_imb.npy"), y_c100_ratio)

# ════════════════════════════════════════════════════════════════════
# DATASET 3: HuggingFace Fashion-MNIST — Class Imbalance
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("DATASET 3: HuggingFace Fashion-MNIST — Class Imbalance + Noise")
print("=" * 60)

hf_fmnist = load_dataset("fashion_mnist", split="train")
print(f"Fashion-MNIST loaded: {len(hf_fmnist)} samples")
assert len(hf_fmnist) > 50000, f"Expected ~60k, got {len(hf_fmnist)}"

fmnist_imgs_raw = np.array([np.array(ex["image"]) for ex in hf_fmnist])
fmnist_lbls = np.array([ex["label"] for ex in hf_fmnist])
if fmnist_imgs_raw.ndim == 3:
    fmnist_imgs_raw = fmnist_imgs_raw[:, :, :, np.newaxis]
assert fmnist_imgs_raw.shape[1:3] == (
    28,
    28,
), f"Expected 28x28, got {fmnist_imgs_raw.shape}"
print(f"Fashion-MNIST shape verified: {fmnist_imgs_raw.shape}")

fmnist_class_idx = {c: np.where(fmnist_lbls == c)[0] for c in range(10)}
fmnist_mean, fmnist_std = 0.2860, 0.3530


def make_fmnist_imb_noisy_loader(ratio, noise_rate, seed=0):
    np.random.seed(seed)
    minority = list(range(5, 10))
    majority = list(range(0, 5))
    n_maj = 500
    n_min = max(1, int(n_maj / ratio))
    selected_idx, selected_lbl = [], []
    for c in majority:
        idx = fmnist_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_maj]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(fmnist_lbls[chosen].tolist())
    for c in minority:
        idx = fmnist_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_min]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(fmnist_lbls[chosen].tolist())
    lbls = np.array(selected_lbl)
    n_noisy = int(noise_rate * len(lbls))
    if n_noisy > 0:
        noise_pos = np.random.choice(len(lbls), n_noisy, replace=False)
        lbls[noise_pos] = np.random.randint(0, 10, n_noisy)
    imgs_sel = fmnist_imgs_raw[selected_idx]
    if imgs_sel.ndim == 3:
        imgs_sel = imgs_sel[:, :, :, np.newaxis]
    X_t = torch.tensor(imgs_sel, dtype=torch.float32).permute(0, 3, 1, 2) / 255.0
    X_t = (X_t - fmnist_mean) / fmnist_std
    y_t = torch.tensor(lbls, dtype=torch.long)
    return DataLoader(
        TensorDataset(X_t, y_t), batch_size=128, shuffle=True, num_workers=0
    )


np.random.seed(42)
fmnist_ratios = np.random.uniform(1.0, 12.0, N_MODELS)
fmnist_noises = np.random.uniform(0.0, 0.35, N_MODELS)
fmnist_feats, fmnist_ratio_targets, fmnist_noise_targets = [], [], []
t0 = time.time()
for i, (ratio, noise) in enumerate(zip(fmnist_ratios, fmnist_noises)):
    torch.manual_seed(i + 300)
    loader = make_fmnist_imb_noisy_loader(ratio, noise, seed=i + 300)
    model = train_small_model(loader, TinyCNN_small(10, 1), TRAIN_EPOCHS)
    feats, _ = extract_rich_features(model)
    fmnist_feats.append(feats)
    fmnist_ratio_targets.append(ratio)
    fmnist_noise_targets.append(noise)
    if (i + 1) % 75 == 0:
        print(f"  FashionMNIST: {i+1}/{N_MODELS} | {time.time()-t0:.0f}s")

X_fmnist = np.stack(fmnist_feats)
y_fmnist_ratio = np.array(fmnist_ratio_targets, dtype=np.float32)
y_fmnist_noise = np.array(fmnist_noise_targets, dtype=np.float32)
X_fmnist_n = (X_fmnist - X_fmnist.mean(0)) / (X_fmnist.std(0) + 1e-8)
feat_dim_fmnist = X_fmnist_n.shape[1]

print("Training meta-model: FashionMNIST Imbalance (K-fold)...")
fmnist_imb_result = train_meta_kfold(
    X_fmnist_n, y_fmnist_ratio, feat_dim_fmnist, META_EPOCHS, N_FOLDS
)
experiment_data["fashionmnist_imbalance"] = fmnist_imb_result

print("Training meta-model: FashionMNIST Noise (K-fold)...")
fmnist_noise_result = train_meta_kfold(
    X_fmnist_n, y_fmnist_noise, feat_dim_fmnist, META_EPOCHS, N_FOLDS
)
experiment_data["fashionmnist_noise"] = fmnist_noise_result

np.save(os.path.join(working_dir, "fmnist_features.npy"), X_fmnist)
np.save(os.path.join(working_dir, "fmnist_targets_ratio.npy"), y_fmnist_ratio)
np.save(os.path.join(working_dir, "fmnist_targets_noise.npy"), y_fmnist_noise)

# ════════════════════════════════════════════════════════════════════
# DATASET 4: HuggingFace SVHN — Class Imbalance
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("DATASET 4: HuggingFace SVHN — Class Imbalance")
print("=" * 60)

hf_svhn = load_dataset("svhn", "cropped_digits", split="train")
print(f"SVHN loaded: {len(hf_svhn)} samples")
assert len(hf_svhn) > 50000, f"Expected SVHN ~73k, got {len(hf_svhn)}"

svhn_imgs = np.array([np.array(ex["image"]) for ex in hf_svhn])
svhn_lbls = np.array([ex["label"] for ex in hf_svhn])
assert svhn_imgs.shape[1:] == (
    32,
    32,
    3,
), f"Expected 32x32x3, got {svhn_imgs.shape[1:]}"
print(f"SVHN shape verified: {svhn_imgs.shape}")

svhn_class_idx = {c: np.where(svhn_lbls == c)[0] for c in range(10)}
svhn_mean = np.array([0.4377, 0.4438, 0.4728])
svhn_std = np.array([0.1980, 0.2010, 0.1970])


def make_svhn_imb_loader(ratio, noise_rate, seed=0):
    np.random.seed(seed)
    minority = list(range(5, 10))
    majority = list(range(0, 5))
    n_maj = 400
    n_min = max(1, int(n_maj / ratio))
    selected_idx, selected_lbl = [], []
    for c in majority:
        idx = svhn_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_maj]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(svhn_lbls[chosen].tolist())
    for c in minority:
        idx = svhn_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_min]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(svhn_lbls[chosen].tolist())
    lbls = np.array(selected_lbl)
    n_noisy = int(noise_rate * len(lbls))
    if n_noisy > 0:
        noise_pos = np.random.choice(len(lbls), n_noisy, replace=False)
        lbls[noise_pos] = np.random.randint(0, 10, n_noisy)
    imgs_sel = svhn_imgs[selected_idx]
    X_t = torch.tensor(imgs_sel, dtype=torch.float32).permute(0, 3, 1, 2) / 255.0
    for c in range(3):
        X_t[:, c] = (X_t[:, c] - svhn_mean[c]) / svhn_std[c]
    y_t = torch.tensor(lbls, dtype=torch.long)
    return DataLoader(
        TensorDataset(X_t, y_t), batch_size=128, shuffle=True, num_workers=0
    )


np.random.seed(42)
svhn_ratios = np.random.uniform(1.0, 15.0, N_MODELS)
svhn_noises = np.random.uniform(0.0, 0.35, N_MODELS)
svhn_feats, svhn_ratio_targets, svhn_noise_targets = [], [], []
t0 = time.time()
for i, (ratio, noise) in enumerate(zip(svhn_ratios, svhn_noises)):
    torch.manual_seed(i + 400)
    loader = make_svhn_imb_loader(ratio, noise, seed=i + 400)
    model = train_small_model(loader, TinyCNN(10, 3), TRAIN_EPOCHS)
    feats, layer_names_svhn = extract_rich_features(model)
    svhn_feats.append(feats)
    svhn_ratio_targets.append(ratio)
    svhn_noise_targets.append(noise)
    if (i + 1) % 75 == 0:
        print(f"  SVHN: {i+1}/{N_MODELS} | {time.time()-t0:.0f}s")

X_svhn = np.stack(svhn_feats)
y_svhn_ratio = np.array(svhn_ratio_targets, dtype=np.float32)
y_svhn_noise = np.array(svhn_noise_targets, dtype=np.float32)
X_svhn_n = (X_svhn - X_svhn.mean(0)) / (X_svhn.std(0) + 1e-8)
feat_dim_svhn = X_svhn_n.shape[1]

print("Training meta-model: SVHN Imbalance (K-fold)...")
svhn_imb_result = train_meta_kfold(
    X_svhn_n, y_svhn_ratio, feat_dim_svhn, META_EPOCHS, N_FOLDS
)
experiment_data["svhn_imbalance"] = svhn_imb_result

print("Training meta-model: SVHN Noise (K-fold)...")
svhn_noise_result = train_meta_kfold(
    X_svhn_n, y_svhn_noise, feat_dim_svhn, META_EPOCHS, N_FOLDS
)
experiment_data["svhn_noise"] = svhn_noise_result

np.save(os.path.join(working_dir, "svhn_features.npy"), X_svhn)
np.save(os.path.join(working_dir, "svhn_targets_ratio.npy"), y_svhn_ratio)
np.save(os.path.join(working_dir, "svhn_targets_noise.npy"), y_svhn_noise)

# ════════════════════════════════════════════════════════════════════
# Cross-Dataset Transfer Matrix
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("CROSS-DATASET TRANSFER MATRIX (Imbalance)")
print("=" * 60)

datasets_for_transfer = {
    "cifar10": (X_cifar_n, y_cifar_imb),
    "cifar100": (X_c100_n, y_c100_ratio),
    "fmnist": (X_fmnist_n, y_fmnist_ratio),
    "svhn": (X_svhn_n, y_svhn_ratio),
}
transfer_matrix = {}


def train_transfer_meta(X_src, y_src, feat_dim, epochs=100):
    y_min, y_max = y_src.min(), y_src.max()
    y_sc = (y_src - y_min) / (y_max - y_min + 1e-8)
    X_t = torch.tensor(X_src, dtype=torch.float32).to(device)
    y_t = torch.tensor(y_sc, dtype=torch.float32).unsqueeze(1).to(device)
    dl = DataLoader(TensorDataset(X_t, y_t), batch_size=32, shuffle=True)
    meta = build_meta_model(feat_dim)
    opt = optim.Adam(meta.parameters(), lr=1e-3, weight_decay=5e-4)
    for ep in range(epochs):
        meta.train()
        for xb, yb in dl:
            opt.zero_grad()
            nn.MSELoss()(meta(xb), yb).backward()
            opt.step()
    return meta, y_min, y_max


for src_name, (X_src, y_src) in datasets_for_transfer.items():
    fd = X_src.shape[1]
    meta_tr, y_min_s, y_max_s = train_transfer_meta(X_src, y_src, fd, epochs=100)
    meta_tr.eval()
    for tgt_name, (X_tgt, y_tgt) in datasets_for_transfer.items():
        fd_tgt = X_tgt.shape[1]
        fd_common = min(fd, fd_tgt)
        X_tgt_aligned = X_tgt[:, :fd_common]

        # Rebuild same-dim meta if needed
        if fd_common != fd:
            meta_eval, _, _ = train_transfer_meta(
                X_src[:, :fd_common], y_src, fd_common, epochs=100
            )
        else:
            meta_eval = meta_tr

        meta_eval.eval()
        y_tgt_sc = (y_tgt - y_tgt.min()) / (y_tgt.max() - y_tgt.min() + 1e-8)
        with torch.no_grad():
            preds = (
                meta_eval(torch.tensor(X_tgt_aligned, dtype=torch.float32).to(device))
                .cpu()
                .numpy()
                .flatten()
            )
        r2 = r2_score(y_tgt_sc, preds)
        transfer_matrix[(src_name, tgt_name)] = r2
        print(f"  {src_name} → {tgt_name}: R²={r2:.4f}")

experiment_data["transfer_matrix"] = {
    f"{k[0]}_to_{k[1]}": v for k, v in transfer_matrix.items()
}

# ════════════════════════════════════════════════════════════════════
# Detection Power Curves
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("DETECTION POWER CURVES — CIFAR-10 Imbalance")
print("=" * 60)

shift_thresholds = [1.5, 2.0, 3.0, 5.0, 8.0, 12.0]
detection_r2s = []
for threshold in shift_thresholds:
    mask = y_cifar_imb <= threshold
    if mask.sum() < 20:
        detection_r2s.append(0.0)
        continue
    X_sub = X_cifar_n[mask]
    y_sub = y_cifar_imb[mask]
    if len(np.unique(y_sub)) < 3:
        detection_r2s.append(0.0)
        continue
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_sub, y_sub, test_size=0.25, random_state=42
    )
    y_min_s, y_max_s = y_tr.min(), y_tr.max()
    if y_max_s - y_min_s < 1e-6:
        detection_r2s.append(0.0)
        continue
    y_tr_sc = (y_tr - y_min_s) / (y_max_s - y_min_s + 1e-8)
    y_te_sc = (y_te - y_min_s) / (y_max_s - y_min_s + 1e-8)
    meta_pw = build_meta_model(X_sub.shape[1])
    opt_pw = optim.Adam(meta_pw.parameters(), lr=1e-3, weight_decay=5e-4)
    dl_pw = DataLoader(
        TensorDataset(
            torch.tensor(X_tr, dtype=torch.float32).to(device),
            torch.tensor(y_tr_sc, dtype=torch.float32).unsqueeze(1).to(device),
        ),
        batch_size=16,
        shuffle=True,
    )
    for _ in range(80):
        meta_pw.train()
        for xb, yb in dl_pw:
            opt_pw.zero_grad()
            nn.MSELoss()(meta_pw(xb), yb).backward()
            opt_pw.step()
    meta_pw.eval()
    with torch.no_grad():
        preds_pw = (
            meta_pw(torch.tensor(X_te, dtype=torch.float32).to(device))
            .cpu()
            .numpy()
            .flatten()
        )
    r2_pw = r2_score(y_te_sc, preds_pw)
    detection_r2s.append(max(0, r2_pw))
    print(f"  Threshold ≤{threshold:.1f}: n={mask.sum()}, R²={r2_pw:.4f}")

experiment_data["detection_power"] = {
    "thresholds": shift_thresholds,
    "r2s": detection_r2s,
}

# ════════════════════════════════════════════════════════════════════
# Save all data
# ════════════════════════════════════════════════════════════════════
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# ════════════════════════════════════════════════════════════════════
# Visualizations
# ════════════════════════════════════════════════════════════════════
ds_configs = {
    "CIFAR-10\nImbalance": ("cifar10_imbalance", "steelblue"),
    "CIFAR-10\nNoise": ("cifar10_noise", "royalblue"),
    "CIFAR-100\nNoise": ("cifar100_noise", "darkorange"),
    "CIFAR-100\nImbalance": ("cifar100_imbalance", "sandybrown"),
    "FashionMNIST\nImbalance": ("fashionmnist_imbalance", "green"),
    "FashionMNIST\nNoise": ("fashionmnist_noise", "limegreen"),
    "SVHN\nImbalance": ("svhn_imbalance", "purple"),
    "SVHN\nNoise": ("svhn_noise", "mediumpurple"),
}

# Figure 1: R² learning curves (mean across folds)
fig, axes = plt.subplots(2, 4, figsize=(20, 10))
axes_flat = axes.flatten()
for ax, (label, (key, color)) in zip(axes_flat, ds_configs.items()):
    data = experiment_data[key]
    epochs = range(1, len(data["mean_train_r2_by_epoch"]) + 1)
    ax.plot(epochs, data["mean_train_r2_by_epoch"], color=color, label="Train (mean)")
    ax.plot(
        epochs,
        data["mean_val_r2_by_epoch"],
        color=color,
        linestyle="--",
        label="Val (mean)",
    )
    ax.axhline(
        data["kfold_mean_r2"],
        color="red",
        linestyle=":",
        lw=2,
        label=f"KFold R²={data['kfold_mean_r2']:.3f}±{data['kfold_std_r2']:.3f}",
    )
    ax.set_title(label, fontsize=10)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("R²")
    ax.legend(fontsize=7)
    ax.grid(True)
    ax.set_ylim(-0.2, 1.05)
plt.suptitle("Weight Forensics: R² Learning Curves (K-Fold, N=300)", fontsize=13)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_r2_curves.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved R² curves figure")

# Figure 2: Summary bar chart
fig2, ax2 = plt.subplots(figsize=(14, 6))
labels_list = list(ds_configs.keys())
r2_list = [experiment_data[v[0]]["kfold_mean_r2"] for v in ds_configs.values()]
std_list = [experiment_data[v[0]]["kfold_std_r2"] for v in ds_configs.values()]
colors_list = [v[1] for v in ds_configs.values()]
x = np.arange(len(labels_list))
bars = ax2.bar(
    x,
    r2_list,
    yerr=std_list,
    capsize=5,
    color=colors_list,
    edgecolor="black",
    alpha=0.85,
)
ax2.set_xticks(x)
ax2.set_xticklabels(
    [l.replace("\n", " ") for l in labels_list], rotation=20, ha="right"
)
ax2.set_ylabel("K-Fold Mean Test R²")
ax2.set_title(
    "Weight Forensics: Distributional Property Decoding R² (K-Fold, N=300)", fontsize=12
)
ax2.set_ylim(0, 1.1)
ax2.grid(True, axis="y")
for bar, val, std in zip(bars, r2_list, std_list):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + std + 0.02,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
        fontweight="bold",
    )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_summary_bar.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved summary bar chart")

# Figure 3: Cross-dataset transfer matrix heatmap
ds_names_transfer = ["cifar10", "cifar100", "fmnist", "svhn"]
mat = np.zeros((4, 4))
for i, src in enumerate(ds_names_transfer):
    for j, tgt in enumerate(ds_names_transfer):
        mat[i, j] = transfer_matrix.get((src, tgt), 0.0)
fig3, ax3 = plt.subplots(figsize=(8, 6))
im = ax3.imshow(mat, cmap="RdYlGn", vmin=-0.2, vmax=1.0)
ax3.set_xticks(range(4))
ax3.set_yticks(range(4))
ax3.set_xticklabels(["CIFAR-10", "CIFAR-100", "FashionMNIST", "SVHN"])
ax3.set_yticklabels(["CIFAR-10", "CIFAR-100", "FashionMNIST", "SVHN"])
ax3.set_xlabel("Target Dataset")
ax3.set_ylabel("Source Dataset")
ax3.set_title("Cross-Dataset Transfer R² (Train→Test, Imbalance)")
for i in range(4):
    for j in range(4):
        ax3.text(
            j,
            i,
            f"{mat[i,j]:.3f}",
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white" if mat[i, j] < 0.3 else "black",
        )
plt.colorbar(im, ax=ax3, label="Transfer R²")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_transfer_matrix.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved transfer matrix heatmap")

# Figure 4: Detection power curve
fig4, ax4 = plt.subplots(figsize=(8, 5))
ax4.plot(shift_thresholds, detection_r2s, "bo-", lw=2, markersize=8)
ax4.fill_between(shift_thresholds, detection_r2s, alpha=0.2)
ax4.axhline(0, color="red", linestyle="--", label="Chance level")
ax4.set_xlabel("Max Imbalance Ratio (subset ≤ threshold)")
ax4.set_ylabel("Test R²")
ax4.set_title("Detection Power Curve: Min Detectable Imbalance (CIFAR-10)")
ax4.legend()
ax4.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_detection_power.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved detection power curve")

# Figure 5: Pred vs True for best 4 experiments
best_keys = sorted(
    ds_configs.keys(),
    key=lambda l: experiment_data[ds_configs[l][0]]["kfold_mean_r2"],
    reverse=True,
)[:4]
fig5, axes5 = plt.subplots(1, 4, figsize=(18, 5))
for ax, label in zip(axes5, best_keys):
    key, color = ds_configs[label]
    data = experiment_data[key]
    gt = np.array(data["ground_truth"])
    pr = np.array(data["predictions"])
    ax.scatter(gt, pr, alpha=0.5, color=color, s=25)
    mn, mx = min(gt.min(), pr.min()), max(gt.max(), pr.max())
    ax.plot([mn, mx], [mn, mx], "r--", lw=2)
    ax.set_title(
        f"{label.replace(chr(10),' ')}\nKFold R²={data['kfold_mean_r2']:.3f}",
        fontsize=9,
    )
    ax.set_xlabel("True")
    ax.set_ylabel("Predicted")
    ax.grid(True)
plt.suptitle("Weight Forensics: Best 4 Experiments — Predicted vs. True", fontsize=12)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "weight_forensics_pred_vs_true.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved pred vs true figure")

# ════════════════════════════════════════════════════════════════════
# Final Summary
# ════════════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("WEIGHT FORENSICS — FINAL RESULTS SUMMARY")
print("=" * 60)
all_r2s = []
for label, (key, _) in ds_configs.items():
    data = experiment_data[key]
    r2_mean = data["kfold_mean_r2"]
    r2_std = data["kfold_std_r2"]
    all_r2s.append(r2_mean)
    print(f"  {label.replace(chr(10),' '):30s} | KFold R²={r2_mean:.4f} ± {r2_std:.4f}")

print("\nTransfer R² (diagonal = in-distribution):")
for i, src in enumerate(ds_names_transfer):
    for j, tgt in enumerate(ds_names_transfer):
        print(f"  {src} → {tgt}: {mat[i,j]:.4f}")

print(f"\nOverall Distributional Property Decoding R² (avg): {np.mean(all_r2s):.4f}")
print(
    f"Best experiment: {max(ds_configs.keys(), key=lambda l: experiment_data[ds_configs[l][0]]['kfold_mean_r2'])}"
)
print(f"Saved all results to {working_dir}")
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("experiment_data.npy saved.")
