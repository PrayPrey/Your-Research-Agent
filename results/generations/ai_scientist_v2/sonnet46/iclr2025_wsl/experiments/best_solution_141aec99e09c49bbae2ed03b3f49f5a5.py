import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import torchvision
import torchvision.transforms as transforms
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score
from sklearn.decomposition import PCA
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


def extract_rich_features(model):
    feats = []
    for name, p in model.named_parameters():
        w = p.data.cpu().numpy().flatten()
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
        if w.std() > 1e-8:
            skew = float(np.mean(((w - w.mean()) / w.std()) ** 3))
            kurt = float(np.mean(((w - w.mean()) / w.std()) ** 4))
        else:
            skew, kurt = 0.0, 0.0
        feats.extend([skew, kurt])
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
    return np.array(feats, dtype=np.float32)


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
            criterion(model(xb), yb).backward()
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

        if best_fold_data is None or test_r2 > best_fold_data["test_r2"]:
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


# Load CIFAR-10
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
NUM_CLASSES = 10

print("Pre-stacking CIFAR-10 images...")
all_cifar_imgs = torch.stack([cifar_train[i][0] for i in range(len(cifar_train))])
all_cifar_lbls = torch.tensor(cifar_labels, dtype=torch.long)
print("Done pre-stacking.")


def apply_noise(lbls, noise_rate, noise_type, num_classes, seed):
    np.random.seed(seed)
    lbls = lbls.copy()
    n = len(lbls)
    n_noisy = int(noise_rate * n)
    if n_noisy == 0:
        return lbls
    noise_pos = np.random.choice(n, n_noisy, replace=False)
    if noise_type == "uniform":
        lbls[noise_pos] = np.random.randint(0, num_classes, n_noisy)
    elif noise_type == "symmetric_flip":
        for idx in noise_pos:
            current = lbls[idx]
            choices = [c for c in range(num_classes) if c != current]
            lbls[idx] = np.random.choice(choices)
    elif noise_type == "asymmetric_pairwise":
        for idx in noise_pos:
            lbls[idx] = (lbls[idx] + 1) % num_classes
    return lbls


def make_cifar_noisy_loader(noise_rate, noise_type, seed=0):
    np.random.seed(seed)
    n_per_class = 200
    selected_idx, selected_lbl = [], []
    for c in range(NUM_CLASSES):
        idx = cifar_class_idx[c].copy()
        np.random.shuffle(idx)
        chosen = idx[:n_per_class]
        selected_idx.extend(chosen.tolist())
        selected_lbl.extend(cifar_labels[chosen].tolist())
    lbls = np.array(selected_lbl)
    lbls = apply_noise(lbls, noise_rate, noise_type, NUM_CLASSES, seed=seed + 9999)
    imgs_t = all_cifar_imgs[selected_idx]
    lbls_t = torch.tensor(lbls, dtype=torch.long)
    ds = TensorDataset(imgs_t, lbls_t)
    return DataLoader(ds, batch_size=128, shuffle=True, num_workers=0)


# ABLATION: Three Noise Types
print("\n" + "=" * 60)
print("ABLATION: Noise Type Effect on Weight Forensics (CIFAR-10)")
print("=" * 60)

noise_types = ["uniform", "symmetric_flip", "asymmetric_pairwise"]
noise_type_labels = {
    "uniform": "Uniform Random",
    "symmetric_flip": "Symmetric Flip",
    "asymmetric_pairwise": "Asymmetric Pairwise",
}

np.random.seed(42)
noise_rates_all = np.random.uniform(0.0, 0.5, N_MODELS)

noise_type_results = {}
noise_type_features = {}
noise_type_targets = {}

for noise_type in noise_types:
    print(f"\n--- Noise Type: {noise_type_labels[noise_type]} ---")
    feats_list = []
    t0 = time.time()
    for i, nr in enumerate(noise_rates_all):
        torch.manual_seed(i + 500)
        loader = make_cifar_noisy_loader(nr, noise_type, seed=i + 500)
        model = train_small_model(loader, TinyCNN(NUM_CLASSES, 3), TRAIN_EPOCHS)
        feats = extract_rich_features(model)
        feats_list.append(feats)
        if (i + 1) % 75 == 0:
            print(f"  [{noise_type}] {i+1}/{N_MODELS} | {time.time()-t0:.0f}s")

    X = np.stack(feats_list)
    y = noise_rates_all.astype(np.float32)
    X_n = (X - X.mean(0)) / (X.std(0) + 1e-8)
    feat_dim = X_n.shape[1]
    noise_type_features[noise_type] = X_n
    noise_type_targets[noise_type] = y

    print(f"Training meta-model for noise_type={noise_type} (K-fold)...")
    result = train_meta_kfold(X_n, y, feat_dim, META_EPOCHS, N_FOLDS)
    noise_type_results[noise_type] = result
    print(
        f"  [{noise_type}] KFold R²={result['kfold_mean_r2']:.4f} ± {result['kfold_std_r2']:.4f}"
    )

# Store in experiment_data with proper nested structure
experiment_data["noise_type_ablation"] = {}
for noise_type in noise_types:
    result = noise_type_results[noise_type]
    experiment_data["noise_type_ablation"][noise_type] = {
        "metrics": result["metrics"],
        "losses": result["losses"],
        "predictions": result["predictions"],
        "ground_truth": result["ground_truth"],
        "kfold_mean_r2": result["kfold_mean_r2"],
        "kfold_std_r2": result["kfold_std_r2"],
        "all_fold_r2s": result["all_fold_r2s"],
        "mean_train_r2_by_epoch": result["mean_train_r2_by_epoch"],
        "mean_val_r2_by_epoch": result["mean_val_r2_by_epoch"],
        "test_r2": result["test_r2"],
    }

# Cross Noise-Type Transfer
print("\n" + "=" * 60)
print("CROSS NOISE-TYPE TRANSFER MATRIX")
print("=" * 60)


def train_meta_full(X_norm, y, feat_dim, epochs=100):
    y_min, y_max = y.min(), y.max()
    y_sc = (y - y_min) / (y_max - y_min + 1e-8)
    X_t = torch.tensor(X_norm, dtype=torch.float32).to(device)
    y_t = torch.tensor(y_sc, dtype=torch.float32).unsqueeze(1).to(device)
    dl = DataLoader(TensorDataset(X_t, y_t), batch_size=32, shuffle=True)
    meta = build_meta_model(feat_dim)
    opt = optim.Adam(meta.parameters(), lr=1e-3, weight_decay=5e-4)
    for _ in range(epochs):
        meta.train()
        for xb, yb in dl:
            opt.zero_grad()
            nn.MSELoss()(meta(xb), yb).backward()
            opt.step()
    return meta, y_min, y_max


cross_transfer = {}
for src_type in noise_types:
    X_src = noise_type_features[src_type]
    y_src = noise_type_targets[src_type]
    fd = X_src.shape[1]
    meta_src, y_min_s, y_max_s = train_meta_full(X_src, y_src, fd, epochs=100)
    meta_src.eval()
    for tgt_type in noise_types:
        X_tgt = noise_type_features[tgt_type]
        y_tgt = noise_type_targets[tgt_type]
        y_tgt_sc = (y_tgt - y_tgt.min()) / (y_tgt.max() - y_tgt.min() + 1e-8)
        with torch.no_grad():
            preds = (
                meta_src(torch.tensor(X_tgt, dtype=torch.float32).to(device))
                .cpu()
                .numpy()
                .flatten()
            )
        r2 = r2_score(y_tgt_sc, preds)
        cross_transfer[(src_type, tgt_type)] = r2
        print(
            f"  {noise_type_labels[src_type]} → {noise_type_labels[tgt_type]}: R²={r2:.4f}"
        )

experiment_data["cross_noise_type_transfer"] = {
    f"{k[0]}_to_{k[1]}": v for k, v in cross_transfer.items()
}

# PCA visualization
print("\n" + "=" * 60)
print("FEATURE SEPARABILITY BY NOISE TYPE")
print("=" * 60)

X_combined = np.concatenate([noise_type_features[nt] for nt in noise_types], axis=0)
y_type_labels_arr = np.concatenate(
    [np.full(N_MODELS, i) for i, nt in enumerate(noise_types)], axis=0
)

pca = PCA(n_components=2, random_state=42)
X_pca = pca.fit_transform(X_combined)
experiment_data["pca_variance_ratio"] = pca.explained_variance_ratio_.tolist()
print(f"PCA explained variance: {pca.explained_variance_ratio_}")

# Save numpy arrays
np.save(
    os.path.join(working_dir, "noise_type_features.npy"),
    {nt: noise_type_features[nt] for nt in noise_types},
)
np.save(
    os.path.join(working_dir, "noise_type_targets.npy"),
    {nt: noise_type_targets[nt] for nt in noise_types},
)
np.save(os.path.join(working_dir, "pca_embedding.npy"), X_pca)

# Visualizations
colors = {
    "uniform": "steelblue",
    "symmetric_flip": "darkorange",
    "asymmetric_pairwise": "green",
}

# Figure 1: R² Learning Curves
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
for ax, noise_type in zip(axes, noise_types):
    data = noise_type_results[noise_type]
    epochs_range = range(1, len(data["mean_train_r2_by_epoch"]) + 1)
    ax.plot(
        epochs_range,
        data["mean_train_r2_by_epoch"],
        color=colors[noise_type],
        label="Train (mean)",
    )
    ax.plot(
        epochs_range,
        data["mean_val_r2_by_epoch"],
        color=colors[noise_type],
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
    ax.set_title(f"{noise_type_labels[noise_type]}", fontsize=11)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("R²")
    ax.legend(fontsize=8)
    ax.grid(True)
    ax.set_ylim(-0.2, 1.05)
plt.suptitle("Noise Type Ablation: R² Learning Curves (K-Fold, N=300)", fontsize=13)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "noise_type_r2_curves.png"), dpi=100, bbox_inches="tight"
)
plt.close()
print("Saved noise type R² curves")

# Figure 2: Summary bar chart
fig2, ax2 = plt.subplots(figsize=(10, 6))
labels_plot = [noise_type_labels[nt] for nt in noise_types]
r2_vals = [noise_type_results[nt]["kfold_mean_r2"] for nt in noise_types]
std_vals = [noise_type_results[nt]["kfold_std_r2"] for nt in noise_types]
color_vals = [colors[nt] for nt in noise_types]
x = np.arange(len(noise_types))
bars = ax2.bar(
    x,
    r2_vals,
    yerr=std_vals,
    capsize=8,
    color=color_vals,
    edgecolor="black",
    alpha=0.85,
    width=0.5,
)
ax2.set_xticks(x)
ax2.set_xticklabels(labels_plot, fontsize=12)
ax2.set_ylabel("K-Fold Mean Test R²", fontsize=12)
ax2.set_title(
    "Noise Type Ablation: Noise Rate Prediction R² by Noise Type\n(CIFAR-10, N=300 models)",
    fontsize=12,
)
ax2.set_ylim(0, 1.1)
ax2.grid(True, axis="y")
for bar, val, std in zip(bars, r2_vals, std_vals):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + std + 0.02,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "noise_type_summary_bar.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved noise type summary bar chart")

# Figure 3: Cross noise-type transfer matrix
mat_transfer = np.zeros((3, 3))
for i, src in enumerate(noise_types):
    for j, tgt in enumerate(noise_types):
        mat_transfer[i, j] = cross_transfer.get((src, tgt), 0.0)

fig3, ax3 = plt.subplots(figsize=(8, 6))
im = ax3.imshow(mat_transfer, cmap="RdYlGn", vmin=-0.3, vmax=1.0)
short_labels = ["Uniform", "Sym. Flip", "Asym. Pair."]
ax3.set_xticks(range(3))
ax3.set_yticks(range(3))
ax3.set_xticklabels(short_labels, fontsize=11)
ax3.set_yticklabels(short_labels, fontsize=11)
ax3.set_xlabel("Target Noise Type", fontsize=12)
ax3.set_ylabel("Source Noise Type", fontsize=12)
ax3.set_title(
    "Cross Noise-Type Transfer R²\n(Train on source type, test on target type)",
    fontsize=12,
)
for i in range(3):
    for j in range(3):
        ax3.text(
            j,
            i,
            f"{mat_transfer[i,j]:.3f}",
            ha="center",
            va="center",
            fontsize=12,
            fontweight="bold",
            color="white" if mat_transfer[i, j] < 0.3 else "black",
        )
plt.colorbar(im, ax=ax3, label="Transfer R²")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "noise_type_transfer_matrix.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved cross noise-type transfer matrix")

# Figure 4: PCA visualization
fig4, ax4 = plt.subplots(figsize=(9, 7))
pca_markers = ["o", "s", "^"]
pca_color_list = ["steelblue", "darkorange", "green"]
for i, nt in enumerate(noise_types):
    start = i * N_MODELS
    end = (i + 1) * N_MODELS
    sc = ax4.scatter(
        X_pca[start:end, 0],
        X_pca[start:end, 1],
        c=noise_type_targets[nt],
        cmap="viridis",
        alpha=0.5,
        s=20,
        marker=pca_markers[i],
        label=noise_type_labels[nt],
    )
ax4.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)", fontsize=11)
ax4.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)", fontsize=11)
ax4.set_title(
    "PCA of Weight Features by Noise Type\n(Color = noise rate, marker = noise type)",
    fontsize=11,
)
ax4.legend(fontsize=10)
ax4.grid(True)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "noise_type_pca.png"), dpi=100, bbox_inches="tight"
)
plt.close()
print("Saved PCA visualization")

# Figure 5: Pred vs True scatter
fig5, axes5 = plt.subplots(1, 3, figsize=(16, 5))
for ax, noise_type in zip(axes5, noise_types):
    data = noise_type_results[noise_type]
    gt = np.array(data["ground_truth"])
    pr = np.array(data["predictions"])
    ax.scatter(gt, pr, alpha=0.5, color=colors[noise_type], s=25)
    mn, mx = min(gt.min(), pr.min()), max(gt.max(), pr.max())
    ax.plot([mn, mx], [mn, mx], "r--", lw=2)
    ax.set_title(
        f"{noise_type_labels[noise_type]}\nKFold R²={data['kfold_mean_r2']:.3f}",
        fontsize=10,
    )
    ax.set_xlabel("True Noise Rate")
    ax.set_ylabel("Predicted Noise Rate")
    ax.grid(True)
plt.suptitle("Noise Type Ablation: Predicted vs True Noise Rate", fontsize=12)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "noise_type_pred_vs_true.png"),
    dpi=100,
    bbox_inches="tight",
)
plt.close()
print("Saved pred vs true for noise types")

# Final Summary
print("\n" + "=" * 60)
print("NOISE TYPE ABLATION — FINAL RESULTS SUMMARY")
print("=" * 60)
for noise_type in noise_types:
    data = noise_type_results[noise_type]
    print(
        f"  {noise_type_labels[noise_type]:30s} | KFold R²={data['kfold_mean_r2']:.4f} ± {data['kfold_std_r2']:.4f}"
    )

print("\nCross Noise-Type Transfer R²:")
for i, src in enumerate(noise_types):
    for j, tgt in enumerate(noise_types):
        mark = " ◄ DIAGONAL" if i == j else ""
        print(
            f"  {noise_type_labels[src]:25s} → {noise_type_labels[tgt]:25s}: {mat_transfer[i,j]:.4f}{mark}"
        )

print(f"\nPCA explained variance (2 components): {pca.explained_variance_ratio_}")

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nSaved all results to {working_dir}")
print("experiment_data.npy saved.")
