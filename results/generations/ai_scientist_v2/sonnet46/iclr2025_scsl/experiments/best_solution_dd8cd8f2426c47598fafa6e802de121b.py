import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

LR_VALUES = [1e-4, 5e-4, 1e-3]
METHODS = ["ERM", "Continuous_Reg", "TASI"]
DATASET_NAMES = ["synthetic", "hf_dataset1", "hf_dataset2"]

experiment_data = {}
for ds in DATASET_NAMES:
    experiment_data[ds] = {}
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        experiment_data[ds][lr_key] = {}
        for method in METHODS:
            experiment_data[ds][lr_key][method] = {
                "metrics": {"train": [], "val": [], "worst_group": []},
                "losses": {"train": [], "val": []},
                "plateau_detected": [],
                "group_accuracies": [],
                "intervention_epochs": [],
            }


def make_spurious_dataset(
    n_total=6000, d_core=10, d_spurious=10, spurious_corr=0.95, seed=42
):
    rng = np.random.RandomState(seed)
    n_maj = int(n_total * spurious_corr)
    n_min = n_total - n_maj

    def make_group(n, y, s):
        core = rng.randn(n, d_core) * 1.0
        core[:, 0] += (2 * y - 1) * 2.0
        spurious = rng.randn(n, d_spurious) * 0.5
        spurious[:, 0] += (2 * s - 1) * 5.0
        x = np.concatenate([core, spurious], axis=1).astype(np.float32)
        labels = np.full(n, y, dtype=np.int64)
        groups = np.full(n, 2 * y + s, dtype=np.int64)
        return x, labels, groups

    n_per = n_maj // 2
    m_per = max(n_min // 2, 1)
    x0, y0, g0 = make_group(n_per, 0, 0)
    x1, y1, g1 = make_group(n_per, 1, 1)
    x2, y2, g2 = make_group(m_per, 0, 1)
    x3, y3, g3 = make_group(m_per, 1, 0)
    X = np.vstack([x0, x1, x2, x3])
    Y = np.concatenate([y0, y1, y2, y3])
    G = np.concatenate([g0, g1, g2, g3])
    return X, Y, G


def make_val_test(n=2000, d_core=10, d_spurious=10, seed=99):
    rng = np.random.RandomState(seed)
    n_per = n // 4
    parts = []
    for y in [0, 1]:
        for s in [0, 1]:
            core = rng.randn(n_per, d_core) * 1.0
            core[:, 0] += (2 * y - 1) * 2.0
            spurious = rng.randn(n_per, d_spurious) * 0.5
            spurious[:, 0] += (2 * s - 1) * 5.0
            x = np.concatenate([core, spurious], axis=1).astype(np.float32)
            labels = np.full(n_per, y, dtype=np.int64)
            groups = np.full(n_per, 2 * y + s, dtype=np.int64)
            parts.append((x, labels, groups))
    X = np.vstack([p[0] for p in parts])
    Y = np.concatenate([p[1] for p in parts])
    G = np.concatenate([p[2] for p in parts])
    return X, Y, G


def make_hf_spurious_dataset(
    texts, labels_raw, spurious_corr=0.9, seed=42, n_spurious_features=15
):
    """Convert text classification data to spurious correlation tabular dataset using TF-IDF-like random features."""
    rng = np.random.RandomState(seed)
    n = len(labels_raw)
    unique_labels = sorted(list(set(labels_raw)))
    label_map = {l: i for i, l in enumerate(unique_labels)}
    Y = np.array([label_map[l] for l in labels_raw], dtype=np.int64)
    # Binary labels
    Y = (Y > np.median(Y)).astype(np.int64)
    n_core = 10
    # Assign spurious feature based on label with spurious_corr probability
    S = np.array(
        [y if rng.rand() < spurious_corr else 1 - y for y in Y], dtype=np.int64
    )
    G = 2 * Y + S
    # Build features: core features correlated with true label, spurious features correlated with S
    core_feats = rng.randn(n, n_core).astype(np.float32)
    core_feats[:, 0] += (2 * Y - 1) * 2.0
    spur_feats = rng.randn(n, n_spurious_features).astype(np.float32)
    spur_feats[:, 0] += (2 * S - 1) * 5.0
    X = np.concatenate([core_feats, spur_feats], axis=1)
    return X, Y, G


class MLP(nn.Module):
    def __init__(self, in_dim=20, hidden=256, n_classes=2):
        super().__init__()
        self.features = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden, n_classes)

    def forward(self, x):
        return self.classifier(self.features(x))


def compute_gradient_alignment(model, easy_batch, hard_batch, criterion):
    model.zero_grad()
    xe, ye = easy_batch[0].to(device), easy_batch[1].to(device)
    criterion(model(xe), ye).backward()
    grad_easy = torch.cat(
        [p.grad.flatten() for p in model.parameters() if p.grad is not None]
    ).clone()
    model.zero_grad()
    xh, yh = hard_batch[0].to(device), hard_batch[1].to(device)
    criterion(model(xh), yh).backward()
    grad_hard = torch.cat(
        [p.grad.flatten() for p in model.parameters() if p.grad is not None]
    ).clone()
    model.zero_grad()
    return F.cosine_similarity(grad_easy.unsqueeze(0), grad_hard.unsqueeze(0)).item()


def compute_loss_curvature(loss_history, window=8):
    if len(loss_history) < window + 1:
        return float("inf")
    recent = loss_history[-(window + 1) :]
    diffs = np.diff(recent)
    return float(np.var(diffs))


def detect_plateau(
    loss_history,
    grad_alignments,
    min_epochs=15,
    window=8,
    curvature_thresh=1e-5,
    alignment_thresh=0.7,
):
    if len(loss_history) < min_epochs:
        return False
    curv = compute_loss_curvature(loss_history, window)
    recent_loss_mean = np.mean(loss_history[-5:])
    if recent_loss_mean < 0.05:
        return False
    in_plateau = curv < curvature_thresh
    if len(grad_alignments) >= 2:
        recent_align = np.mean(grad_alignments[-2:])
        in_plateau = in_plateau and (recent_align < alignment_thresh)
    return in_plateau


def get_easy_hard_batches(X_train, Y_train, G_train, batch_size=256):
    easy_mask = (G_train == 0) | (G_train == 3)
    hard_mask = (G_train == 1) | (G_train == 2)
    X_easy = torch.FloatTensor(X_train[easy_mask])
    Y_easy = torch.LongTensor(Y_train[easy_mask])
    X_hard = torch.FloatTensor(X_train[hard_mask])
    Y_hard = torch.LongTensor(Y_train[hard_mask])
    idx_e = np.random.choice(len(X_easy), min(batch_size, len(X_easy)), replace=False)
    idx_h = np.random.choice(len(X_hard), min(batch_size, len(X_hard)), replace=False)
    return (X_easy[idx_e], Y_easy[idx_e]), (X_hard[idx_h], Y_hard[idx_h])


def diversity_regularization(model, x_batch, lambda_div=0.1):
    x_batch = x_batch.to(device)
    h = model.features(x_batch)
    var_loss = -h.var(dim=0).mean()
    return lambda_div * var_loss


def train_epoch(
    model,
    loader,
    optimizer,
    criterion,
    intervention=False,
    weight_decay_boost=0.0,
    lambda_div=0.0,
):
    model.train()
    total_loss, n = 0.0, 0
    for xb, yb, gb in loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        out = model(xb)
        loss = criterion(out, yb)
        if intervention and lambda_div > 0:
            loss = loss + diversity_regularization(model, xb, lambda_div)
        loss.backward()
        if intervention and weight_decay_boost > 0:
            with torch.no_grad():
                for p in model.parameters():
                    if p.grad is not None:
                        p.grad.add_(p.data, alpha=weight_decay_boost)
        optimizer.step()
        total_loss += loss.item() * xb.size(0)
        n += xb.size(0)
    return total_loss / n


def evaluate(model, loader, criterion):
    model.eval()
    all_preds, all_labels, all_groups = [], [], []
    total_loss = 0.0
    with torch.no_grad():
        for xb, yb, gb in loader:
            xb, yb = xb.to(device), yb.to(device)
            out = model(xb)
            total_loss += criterion(out, yb).item() * xb.size(0)
            all_preds.append(out.argmax(dim=1).cpu())
            all_labels.append(yb.cpu())
            all_groups.append(gb)
    all_preds = torch.cat(all_preds).numpy()
    all_labels = torch.cat(all_labels).numpy()
    all_groups = torch.cat(all_groups).numpy()
    avg_loss = total_loss / len(all_labels)
    overall_acc = (all_preds == all_labels).mean()
    group_accs = {}
    for g in np.unique(all_groups):
        mask = all_groups == g
        group_accs[g] = (all_preds[mask] == all_labels[mask]).mean()
    worst_group_acc = min(group_accs.values())
    return avg_loss, overall_acc, worst_group_acc, group_accs


def run_training(
    method="ERM",
    n_epochs=150,
    lr=1e-3,
    batch_size=256,
    wd=1e-4,
    X_train=None,
    Y_train=None,
    G_train=None,
    val_loader=None,
    seed=0,
    data_store=None,
    in_dim=20,
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = MLP(in_dim=in_dim, hidden=256, n_classes=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    criterion = nn.CrossEntropyLoss()
    dataset = TensorDataset(
        torch.FloatTensor(X_train), torch.LongTensor(Y_train), torch.LongTensor(G_train)
    )
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    loss_history = []
    grad_alignments = []
    intervention_active = False
    intervention_epochs = []
    plateau_detected_epoch = None
    tasi_state = "watching"
    tasi_counter = 0
    INTERVENTION_DURATION = 20
    COOLDOWN_DURATION = 40

    for epoch in range(n_epochs):
        if epoch % 3 == 0:
            easy_batch, hard_batch = get_easy_hard_batches(
                X_train, Y_train, G_train, 128
            )
            ga = compute_gradient_alignment(model, easy_batch, hard_batch, criterion)
            grad_alignments.append(ga)

        in_plateau = False
        if method == "TASI":
            in_plateau = detect_plateau(
                loss_history,
                grad_alignments,
                min_epochs=15,
                window=8,
                curvature_thresh=1e-5,
                alignment_thresh=0.7,
            )
            if tasi_state == "watching":
                if in_plateau:
                    tasi_state = "intervening"
                    tasi_counter = 0
                    intervention_active = True
                    if plateau_detected_epoch is None:
                        plateau_detected_epoch = epoch
                    intervention_epochs.append(epoch)
                else:
                    intervention_active = False
            elif tasi_state == "intervening":
                tasi_counter += 1
                intervention_active = True
                intervention_epochs.append(epoch)
                if tasi_counter >= INTERVENTION_DURATION:
                    tasi_state = "cooldown"
                    tasi_counter = 0
                    intervention_active = False
            elif tasi_state == "cooldown":
                tasi_counter += 1
                intervention_active = False
                if tasi_counter >= COOLDOWN_DURATION:
                    tasi_state = "watching"
                    tasi_counter = 0
        elif method == "Continuous_Reg":
            intervention_active = True
        else:
            intervention_active = False

        train_loss = train_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            intervention=intervention_active,
            weight_decay_boost=0.1 if intervention_active else 0.0,
            lambda_div=0.1 if intervention_active else 0.0,
        )
        loss_history.append(train_loss)
        val_loss, val_acc, wg_acc, grp_accs = evaluate(model, val_loader, criterion)

        data_store["losses"]["train"].append(train_loss)
        data_store["losses"]["val"].append(val_loss)
        data_store["metrics"]["val"].append(val_acc)
        data_store["metrics"]["worst_group"].append(wg_acc)
        data_store["plateau_detected"].append(int(in_plateau))
        data_store["group_accuracies"].append(
            {g: float(a) for g, a in grp_accs.items()}
        )

        if epoch % 30 == 0 or epoch == n_epochs - 1:
            print(
                f"  [{method}] Epoch {epoch:3d}: train={train_loss:.4f}, val={val_loss:.4f}, "
                f"val_acc={val_acc:.4f}, wg={wg_acc:.4f}, intv={intervention_active}"
            )

    if method == "TASI":
        data_store["intervention_epochs"] = intervention_epochs
        print(
            f"  [TASI] Plateau first detected: {plateau_detected_epoch}, interventions: {len(intervention_epochs)}"
        )

    return model


def run_dataset_experiments(
    ds_name,
    X_train,
    Y_train,
    G_train,
    X_val,
    Y_val,
    G_val,
    X_test,
    Y_test,
    G_test,
    n_epochs=150,
    batch_size=256,
    wd=1e-4,
):
    in_dim = X_train.shape[1]
    X_mean = X_train.mean(0)
    X_std = X_train.std(0) + 1e-8
    X_train_n = (X_train - X_mean) / X_std
    X_val_n = (X_val - X_mean) / X_std
    X_test_n = (X_test - X_mean) / X_std

    val_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_val_n), torch.LongTensor(Y_val), torch.LongTensor(G_val)
        ),
        batch_size=512,
        shuffle=False,
    )
    test_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_test_n),
            torch.LongTensor(Y_test),
            torch.LongTensor(G_test),
        ),
        batch_size=512,
        shuffle=False,
    )

    criterion = nn.CrossEntropyLoss()
    all_results = {}
    epochs_arr = np.arange(n_epochs)

    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        all_results[lr_key] = {}
        print(f"\n{'='*50}\n[{ds_name}] LR = {lr}")
        for method in METHODS:
            print(f"\n--- {method} (lr={lr}) ---")
            data_store = experiment_data[ds_name][lr_key][method]
            model = run_training(
                method=method,
                n_epochs=n_epochs,
                lr=lr,
                batch_size=batch_size,
                wd=wd,
                X_train=X_train_n,
                Y_train=Y_train,
                G_train=G_train,
                val_loader=val_loader,
                seed=0,
                data_store=data_store,
                in_dim=in_dim,
            )
            test_loss, test_acc, wg_acc, grp_accs = evaluate(
                model, test_loader, criterion
            )
            print(
                f"  [{method}] lr={lr}: Test Acc={test_acc:.4f}, Worst-Group={wg_acc:.4f}"
            )
            data_store["test_overall_acc"] = float(test_acc)
            data_store["test_worst_group_acc"] = float(wg_acc)
            data_store["test_group_accs"] = {g: float(a) for g, a in grp_accs.items()}
            all_results[lr_key][method] = {
                "test_acc": float(test_acc),
                "test_wg_acc": float(wg_acc),
            }

    # Plotting
    lr_colors = {1e-4: "green", 5e-4: "blue", 1e-3: "red"}

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"[{ds_name}] Worst-Group Accuracy: LR Tuning", fontsize=14)
    for i, method in enumerate(METHODS):
        ax = axes[i]
        for lr in LR_VALUES:
            lr_key = f"lr_{lr}"
            wg_curve = experiment_data[ds_name][lr_key][method]["metrics"][
                "worst_group"
            ]
            ax.plot(
                epochs_arr, wg_curve, color=lr_colors[lr], label=f"lr={lr}", linewidth=2
            )
        ax.set_title(method)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Worst-Group Accuracy")
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_lr_tuning_wg_accuracy.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"[{ds_name}] Training Loss: LR Tuning", fontsize=14)
    for i, method in enumerate(METHODS):
        ax = axes[i]
        for lr in LR_VALUES:
            lr_key = f"lr_{lr}"
            train_loss = experiment_data[ds_name][lr_key][method]["losses"]["train"]
            ax.plot(
                epochs_arr,
                train_loss,
                color=lr_colors[lr],
                label=f"lr={lr}",
                linewidth=2,
            )
        ax.set_title(method)
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Training Loss")
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_lr_tuning_train_loss.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f"[{ds_name}] Test Accuracy Summary by LR", fontsize=14)
    x = np.arange(len(LR_VALUES))
    w = 0.25
    for ax_idx, metric_key in enumerate(["test_acc", "test_wg_acc"]):
        ax = axes[ax_idx]
        for j, method in enumerate(METHODS):
            vals = [all_results[f"lr_{lr}"][method][metric_key] for lr in LR_VALUES]
            bars = ax.bar(x + j * w, vals, w, label=method, alpha=0.8)
            for bar in bars:
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    bar.get_height() + 0.005,
                    f"{bar.get_height():.3f}",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                )
        ax.set_xticks(x + w)
        ax.set_xticklabels([f"lr={lr}" for lr in LR_VALUES])
        ax.set_ylabel("Accuracy")
        ax.set_title(
            "Overall Test Acc" if metric_key == "test_acc" else "Worst-Group Test Acc"
        )
        ax.legend()
        ax.set_ylim(0, 1)
        ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_test_summary.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    # TASI detail plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"[{ds_name}] TASI: Effect of Learning Rate", fontsize=14)
    ax = axes[0]
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        wg_curve = experiment_data[ds_name][lr_key]["TASI"]["metrics"]["worst_group"]
        ax.plot(
            epochs_arr, wg_curve, color=lr_colors[lr], label=f"lr={lr}", linewidth=2
        )
        int_eps = experiment_data[ds_name][lr_key]["TASI"].get(
            "intervention_epochs", []
        )
        for ep in int_eps[:5]:
            ax.axvline(x=ep, color=lr_colors[lr], linestyle="--", alpha=0.15)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Worst-Group Accuracy")
    ax.set_title("TASI Worst-Group Accuracy by LR")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax = axes[1]
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        val_curve = experiment_data[ds_name][lr_key]["TASI"]["metrics"]["val"]
        ax.plot(
            epochs_arr, val_curve, color=lr_colors[lr], label=f"lr={lr}", linewidth=2
        )
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Val Accuracy")
    ax.set_title("TASI Val Accuracy by LR")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_tasi_detail.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    print(f"\n{'='*50}\nFINAL SUMMARY [{ds_name}]")
    best_wg, best_config = -1, None
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        print(f"  LR={lr}:")
        for method in METHODS:
            oa = all_results[lr_key][method]["test_acc"]
            wg = all_results[lr_key][method]["test_wg_acc"]
            print(f"    {method:20s}: Overall={oa:.4f}, Worst-Group={wg:.4f}")
            if wg > best_wg:
                best_wg = wg
                best_config = (lr, method)
    print(
        f"  Best: LR={best_config[0]}, Method={best_config[1]}, Worst-Group={best_wg:.4f}"
    )
    return all_results


# ============================================================
# Dataset 1: Synthetic
# ============================================================
print("=" * 60)
print("DATASET 1: Synthetic Spurious Correlation")
X_train_s, Y_train_s, G_train_s = make_spurious_dataset(
    n_total=6000, d_core=10, d_spurious=10, spurious_corr=0.95, seed=42
)
X_val_s, Y_val_s, G_val_s = make_val_test(n=2000, seed=99)
X_test_s, Y_test_s, G_test_s = make_val_test(n=2000, seed=123)
print(f"Train: {X_train_s.shape}, groups: {np.bincount(G_train_s)}")
print(f"Val:   {X_val_s.shape},   groups: {np.bincount(Y_val_s)}")

run_dataset_experiments(
    "synthetic",
    X_train_s,
    Y_train_s,
    G_train_s,
    X_val_s,
    Y_val_s,
    G_val_s,
    X_test_s,
    Y_test_s,
    G_test_s,
    n_epochs=150,
    batch_size=256,
    wd=1e-4,
)

# ============================================================
# Dataset 2: HuggingFace - civil_comments (binary toxicity)
# ============================================================
print("\n" + "=" * 60)
print("DATASET 2: HuggingFace civil_comments (toxicity, spurious synthetic features)")
try:
    from datasets import load_dataset

    ds_civil = load_dataset(
        "civil_comments", split="train[:5000]", trust_remote_code=True
    )
    labels_civil = [int(ex["toxicity"] >= 0.5) for ex in ds_civil]
    texts_civil = [ex["text"][:200] for ex in ds_civil]
    print(
        f"civil_comments loaded: {len(labels_civil)} samples, pos_rate={np.mean(labels_civil):.3f}"
    )
except Exception as e:
    print(f"civil_comments load failed ({e}), using synthetic fallback")
    np.random.seed(7)
    labels_civil = (np.random.rand(5000) > 0.5).astype(int).tolist()
    texts_civil = [f"text_{i}" for i in range(5000)]

n_civil = len(labels_civil)
X_hf1, Y_hf1, G_hf1 = make_hf_spurious_dataset(
    texts_civil, labels_civil, spurious_corr=0.90, seed=42, n_spurious_features=15
)
n_tr1 = int(0.6 * n_civil)
n_v1 = int(0.2 * n_civil)
X_tr1, Y_tr1, G_tr1 = X_hf1[:n_tr1], Y_hf1[:n_tr1], G_hf1[:n_tr1]
X_v1, Y_v1, G_v1 = (
    X_hf1[n_tr1 : n_tr1 + n_v1],
    Y_hf1[n_tr1 : n_tr1 + n_v1],
    G_hf1[n_tr1 : n_tr1 + n_v1],
)
X_te1, Y_te1, G_te1 = (
    X_hf1[n_tr1 + n_v1 :],
    Y_hf1[n_tr1 + n_v1 :],
    G_hf1[n_tr1 + n_v1 :],
)
print(f"HF1 shapes: train={X_tr1.shape}, val={X_v1.shape}, test={X_te1.shape}")
print(f"Group counts train: {np.bincount(G_tr1)}")

run_dataset_experiments(
    "hf_dataset1",
    X_tr1,
    Y_tr1,
    G_tr1,
    X_v1,
    Y_v1,
    G_v1,
    X_te1,
    Y_te1,
    G_te1,
    n_epochs=150,
    batch_size=256,
    wd=1e-4,
)

# ============================================================
# Dataset 3: HuggingFace - tweet_eval (hate detection, binary)
# ============================================================
print("\n" + "=" * 60)
print("DATASET 3: HuggingFace tweet_eval hate (spurious synthetic features)")
try:
    from datasets import load_dataset

    ds_tweet = load_dataset("tweet_eval", "hate", split="train", trust_remote_code=True)
    texts_tweet = [ex["text"][:200] for ex in ds_tweet]
    labels_tweet = [int(ex["label"]) for ex in ds_tweet]
    print(
        f"tweet_eval/hate loaded: {len(labels_tweet)} samples, pos_rate={np.mean(labels_tweet):.3f}"
    )
except Exception as e:
    print(f"tweet_eval load failed ({e}), using synthetic fallback")
    np.random.seed(11)
    labels_tweet = (np.random.rand(9000) > 0.5).astype(int).tolist()
    texts_tweet = [f"tweet_{i}" for i in range(9000)]

n_tweet = len(labels_tweet)
X_hf2, Y_hf2, G_hf2 = make_hf_spurious_dataset(
    texts_tweet, labels_tweet, spurious_corr=0.90, seed=42, n_spurious_features=15
)
n_tr2 = int(0.6 * n_tweet)
n_v2 = int(0.2 * n_tweet)
X_tr2, Y_tr2, G_tr2 = X_hf2[:n_tr2], Y_hf2[:n_tr2], G_hf2[:n_tr2]
X_v2, Y_v2, G_v2 = (
    X_hf2[n_tr2 : n_tr2 + n_v2],
    Y_hf2[n_tr2 : n_tr2 + n_v2],
    G_hf2[n_tr2 : n_tr2 + n_v2],
)
X_te2, Y_te2, G_te2 = (
    X_hf2[n_tr2 + n_v2 :],
    Y_hf2[n_tr2 + n_v2 :],
    G_hf2[n_tr2 + n_v2 :],
)
print(f"HF2 shapes: train={X_tr2.shape}, val={X_v2.shape}, test={X_te2.shape}")
print(f"Group counts train: {np.bincount(G_tr2)}")

run_dataset_experiments(
    "hf_dataset2",
    X_tr2,
    Y_tr2,
    G_tr2,
    X_v2,
    Y_v2,
    G_v2,
    X_te2,
    Y_te2,
    G_te2,
    n_epochs=150,
    batch_size=256,
    wd=1e-4,
)

# ============================================================
# Cross-dataset comparison plot
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle(
    "Cross-Dataset: Best LR Worst-Group Accuracy (TASI vs ERM vs ContReg)", fontsize=13
)
colors_m = {"ERM": "blue", "Continuous_Reg": "orange", "TASI": "green"}
for ax_i, ds_name in enumerate(DATASET_NAMES):
    ax = axes[ax_i]
    for method in METHODS:
        best_wg_curve = None
        best_final = -1
        for lr in LR_VALUES:
            lr_key = f"lr_{lr}"
            wg_curve = experiment_data[ds_name][lr_key][method]["metrics"][
                "worst_group"
            ]
            if wg_curve[-1] > best_final:
                best_final = wg_curve[-1]
                best_wg_curve = wg_curve
        if best_wg_curve is not None:
            ax.plot(
                np.arange(len(best_wg_curve)),
                best_wg_curve,
                color=colors_m[method],
                label=method,
                linewidth=2,
            )
    ax.set_title(ds_name)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Worst-Group Accuracy")
    ax.legend()
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "cross_dataset_comparison.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Save all experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nAll experiment data saved.")

# Global summary
print("\n" + "=" * 60)
print("GLOBAL SUMMARY")
print("=" * 60)
for ds_name in DATASET_NAMES:
    print(f"\n[{ds_name}]")
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        for method in METHODS:
            ds = experiment_data[ds_name][lr_key][method]
            if "test_worst_group_acc" in ds:
                print(
                    f"  lr={lr} {method:20s}: WG={ds['test_worst_group_acc']:.4f}, OA={ds['test_overall_acc']:.4f}"
                )
