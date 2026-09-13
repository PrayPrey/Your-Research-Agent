import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from collections import defaultdict

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ─────────────────────────────────────────────
# Experiment data storage
# ─────────────────────────────────────────────
experiment_data = {
    "ERM": {
        "metrics": {"train": [], "val": [], "worst_group": []},
        "losses": {"train": [], "val": []},
        "plateau_detected": [],
        "group_accuracies": [],
    },
    "TASI": {
        "metrics": {"train": [], "val": [], "worst_group": []},
        "losses": {"train": [], "val": []},
        "plateau_detected": [],
        "group_accuracies": [],
        "intervention_epochs": [],
    },
    "Continuous_Reg": {
        "metrics": {"train": [], "val": [], "worst_group": []},
        "losses": {"train": [], "val": []},
        "plateau_detected": [],
        "group_accuracies": [],
    },
}


# ─────────────────────────────────────────────
# Synthetic Dataset with Spurious Correlations
# Groups: (y=0, spurious=0), (y=0, spurious=1),
#         (y=1, spurious=0), (y=1, spurious=1)
# Majority: y matches spurious feature (easy shortcut)
# Minority: y != spurious feature (hard, core only)
# ─────────────────────────────────────────────
def make_spurious_dataset(
    n_total=5000, d_core=10, d_spurious=10, spurious_corr=0.95, noise=0.1, seed=42
):
    rng = np.random.RandomState(seed)
    n_maj = int(n_total * spurious_corr)
    n_min = n_total - n_maj

    def make_group(n, y, s, rng):
        core = rng.randn(n, d_core) * 0.5
        core[:, 0] += (2 * y - 1) * 2.0  # core feature carries label
        spurious = rng.randn(n, d_spurious) * 0.5
        spurious[:, 0] += (2 * s - 1) * 3.0  # spurious feature is stronger signal
        x = np.concatenate([core, spurious], axis=1)
        noise_arr = rng.randn(n, d_core + d_spurious) * noise
        x += noise_arr
        labels = np.full(n, y, dtype=np.int64)
        groups = np.full(n, 2 * y + s, dtype=np.int64)  # group id
        spurious_attr = np.full(n, s, dtype=np.int64)
        return x, labels, groups, spurious_attr

    # Majority: y==spurious
    n_per = n_maj // 2
    x0, y0, g0, s0 = make_group(n_per, 0, 0, rng)
    x1, y1, g1, s1 = make_group(n_per, 1, 1, rng)
    # Minority: y!=spurious
    m_per = n_min // 2
    x2, y2, g2, s2 = make_group(m_per, 0, 1, rng)
    x3, y3, g3, s3 = make_group(m_per, 1, 0, rng)

    X = np.vstack([x0, x1, x2, x3]).astype(np.float32)
    Y = np.concatenate([y0, y1, y2, y3])
    G = np.concatenate([g0, g1, g2, g3])
    S = np.concatenate([s0, s1, s2, s3])
    return X, Y, G, S


def make_val_test(n=2000, d_core=10, d_spurious=10, seed=99):
    """Balanced val/test with all groups equal"""
    rng = np.random.RandomState(seed)
    n_per = n // 4
    groups_data = []
    for y in [0, 1]:
        for s in [0, 1]:
            core = rng.randn(n_per, d_core) * 0.5
            core[:, 0] += (2 * y - 1) * 2.0
            spurious = rng.randn(n_per, d_spurious) * 0.5
            spurious[:, 0] += (2 * s - 1) * 3.0
            x = np.concatenate([core, spurious], axis=1).astype(np.float32)
            labels = np.full(n_per, y, dtype=np.int64)
            groups = np.full(n_per, 2 * y + s, dtype=np.int64)
            groups_data.append((x, labels, groups))
    X = np.vstack([g[0] for g in groups_data])
    Y = np.concatenate([g[1] for g in groups_data])
    G = np.concatenate([g[2] for g in groups_data])
    return X, Y, G


# ─────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────
class MLP(nn.Module):
    def __init__(self, in_dim=20, hidden=128, n_classes=2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, n_classes),
        )

    def forward(self, x):
        return self.net(x)


# ─────────────────────────────────────────────
# TASI Detection Signals
# ─────────────────────────────────────────────
def compute_gradient_alignment(model, easy_batch, hard_batch, criterion):
    """Compute cosine similarity between gradients on easy vs hard samples"""
    model.zero_grad()
    xe, ye = easy_batch
    xe, ye = xe.to(device), ye.to(device)
    loss_e = criterion(model(xe), ye)
    loss_e.backward()
    grad_easy = torch.cat(
        [p.grad.flatten() for p in model.parameters() if p.grad is not None]
    ).clone()

    model.zero_grad()
    xh, yh = hard_batch
    xh, yh = xh.to(device), yh.to(device)
    loss_h = criterion(model(xh), yh)
    loss_h.backward()
    grad_hard = torch.cat(
        [p.grad.flatten() for p in model.parameters() if p.grad is not None]
    ).clone()

    model.zero_grad()
    cos_sim = F.cosine_similarity(grad_easy.unsqueeze(0), grad_hard.unsqueeze(0)).item()
    return cos_sim


def compute_loss_curvature(loss_history, window=5):
    """Detect plateau: low variance in recent loss changes"""
    if len(loss_history) < window + 1:
        return 0.0
    recent = loss_history[-(window + 1) :]
    diffs = np.diff(recent)
    return float(np.var(diffs))


def detect_plateau(
    loss_history, grad_alignments, window=8, curvature_thresh=1e-5, alignment_thresh=0.5
):
    """Return True if currently in shortcut plateau"""
    curv = compute_loss_curvature(loss_history, window)
    in_plateau = curv < curvature_thresh
    if len(grad_alignments) > 0:
        recent_align = np.mean(grad_alignments[-min(3, len(grad_alignments)) :])
        in_plateau = in_plateau and (recent_align < alignment_thresh)
    return in_plateau


# ─────────────────────────────────────────────
# Evaluation
# ─────────────────────────────────────────────
def evaluate(model, loader, criterion, groups_tensor):
    model.eval()
    all_preds, all_labels, all_groups = [], [], []
    total_loss = 0.0
    with torch.no_grad():
        for i, (xb, yb, gb) in enumerate(loader):
            xb, yb = xb.to(device), yb.to(device)
            out = model(xb)
            loss = criterion(out, yb)
            total_loss += loss.item() * xb.size(0)
            preds = out.argmax(dim=1).cpu()
            all_preds.append(preds)
            all_labels.append(yb.cpu())
            all_groups.append(gb)
    all_preds = torch.cat(all_preds).numpy()
    all_labels = torch.cat(all_labels).numpy()
    all_groups = torch.cat(all_groups).numpy()

    avg_loss = total_loss / len(all_labels)
    overall_acc = (all_preds == all_labels).mean()

    # Per-group accuracy
    group_accs = {}
    for g in np.unique(all_groups):
        mask = all_groups == g
        group_accs[g] = (all_preds[mask] == all_labels[mask]).mean()
    worst_group_acc = min(group_accs.values())
    return avg_loss, overall_acc, worst_group_acc, group_accs


# ─────────────────────────────────────────────
# Training Functions
# ─────────────────────────────────────────────
def get_easy_hard_batches(X_train, Y_train, G_train, batch_size=256):
    """Easy: majority groups (y==spurious), Hard: minority groups (y!=spurious)"""
    easy_mask = (G_train == 0) | (G_train == 3)  # y==spurious
    hard_mask = (G_train == 1) | (G_train == 2)  # y!=spurious

    X_easy = torch.FloatTensor(X_train[easy_mask])
    Y_easy = torch.LongTensor(Y_train[easy_mask])
    X_hard = torch.FloatTensor(X_train[hard_mask])
    Y_hard = torch.LongTensor(Y_train[hard_mask])

    # Sample batch
    idx_e = np.random.choice(len(X_easy), min(batch_size, len(X_easy)), replace=False)
    idx_h = np.random.choice(len(X_hard), min(batch_size, len(X_hard)), replace=False)
    return (X_easy[idx_e], Y_easy[idx_e]), (X_hard[idx_h], Y_hard[idx_h])


def diversity_regularization(model, x_batch, lambda_div=0.1):
    """Feature diversity reg: penalize representation collapse"""
    x_batch = x_batch.to(device)
    # Get second-to-last layer representations
    with torch.no_grad():
        h = model.net[:4](x_batch)  # through 2nd ReLU
    h_active = model.net[:4](x_batch)
    # Penalize low variance across batch
    var_loss = -h_active.var(dim=0).mean()
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
    total_loss = 0.0
    n = 0
    for xb, yb, gb in loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()
        out = model(xb)
        loss = criterion(out, yb)

        if intervention and lambda_div > 0:
            div_loss = diversity_regularization(model, xb, lambda_div)
            loss = loss + div_loss

        loss.backward()

        if intervention and weight_decay_boost > 0:
            # Apply extra gradient step towards weight decay
            with torch.no_grad():
                for p in model.parameters():
                    if p.grad is not None:
                        p.grad.add_(p.data, alpha=weight_decay_boost)

        optimizer.step()
        total_loss += loss.item() * xb.size(0)
        n += xb.size(0)
    return total_loss / n


def run_training(
    method="ERM",
    n_epochs=100,
    lr=1e-3,
    batch_size=256,
    wd=1e-4,
    X_train=None,
    Y_train=None,
    G_train=None,
    val_loader=None,
    seed=0,
):
    torch.manual_seed(seed)
    np.random.seed(seed)

    model = MLP(in_dim=20, hidden=128, n_classes=2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    criterion = nn.CrossEntropyLoss()

    dataset = TensorDataset(
        torch.FloatTensor(X_train), torch.LongTensor(Y_train), torch.LongTensor(G_train)
    )
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    loss_history = []
    grad_alignments = []
    plateau_flags = []
    intervention_active = False
    intervention_epochs = []
    post_plateau_count = 0
    plateau_detected_epoch = None
    intervention_cooldown = 0

    key = method
    for epoch in range(n_epochs):
        # Compute gradient alignment signal every 5 epochs
        if epoch % 5 == 0:
            easy_batch, hard_batch = get_easy_hard_batches(
                X_train, Y_train, G_train, 128
            )
            ga = compute_gradient_alignment(model, easy_batch, hard_batch, criterion)
            grad_alignments.append(ga)

        # Decide intervention
        in_plateau = False
        if method == "TASI":
            in_plateau = detect_plateau(
                loss_history,
                grad_alignments,
                window=8,
                curvature_thresh=5e-5,
                alignment_thresh=0.7,
            )
            if in_plateau and plateau_detected_epoch is None:
                plateau_detected_epoch = epoch

            # Activate intervention when plateau detected, for limited duration
            if in_plateau and intervention_cooldown == 0:
                intervention_active = True
                intervention_epochs.append(epoch)
                post_plateau_count = 0
            elif intervention_active:
                post_plateau_count += 1
                if post_plateau_count > 10:  # transient: only 10 epochs
                    intervention_active = False
                    intervention_cooldown = 20  # cooldown before next
            if intervention_cooldown > 0:
                intervention_cooldown -= 1
        elif method == "Continuous_Reg":
            intervention_active = True  # always on

        # Train one epoch
        train_loss = train_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            intervention=intervention_active,
            weight_decay_boost=0.05 if intervention_active else 0.0,
            lambda_div=0.05 if intervention_active else 0.0,
        )
        loss_history.append(train_loss)

        # Evaluate
        val_loss, val_acc, wg_acc, grp_accs = evaluate(
            model, val_loader, criterion, None
        )

        experiment_data[key]["losses"]["train"].append(train_loss)
        experiment_data[key]["losses"]["val"].append(val_loss)
        experiment_data[key]["metrics"]["val"].append(val_acc)
        experiment_data[key]["metrics"]["worst_group"].append(wg_acc)
        experiment_data[key]["plateau_detected"].append(int(in_plateau))
        experiment_data[key]["group_accuracies"].append(
            {g: float(a) for g, a in grp_accs.items()}
        )

        if epoch % 10 == 0 or epoch == n_epochs - 1:
            print(
                f"[{method}] Epoch {epoch:3d}: train_loss={train_loss:.4f}, "
                f"val_loss={val_loss:.4f}, val_acc={val_acc:.4f}, "
                f"worst_group_acc={wg_acc:.4f}, "
                f"intervention={intervention_active}"
            )

    if method == "TASI":
        experiment_data[key]["intervention_epochs"] = intervention_epochs
        print(f"[TASI] Plateau first detected at epoch: {plateau_detected_epoch}")
        print(f"[TASI] Intervention epochs: {intervention_epochs}")

    return model


# ─────────────────────────────────────────────
# Main Execution
# ─────────────────────────────────────────────
print("=" * 60)
print("Creating synthetic spurious correlation dataset...")
X_train, Y_train, G_train, S_train = make_spurious_dataset(
    n_total=6000, d_core=10, d_spurious=10, spurious_corr=0.95, seed=42
)

X_val, Y_val, G_val = make_val_test(n=2000, d_core=10, d_spurious=10, seed=99)
X_test, Y_test, G_test = make_val_test(n=2000, d_core=10, d_spurious=10, seed=123)

print(f"Train: {X_train.shape}, group distribution: {np.bincount(G_train)}")
print(f"Val:   {X_val.shape},   group distribution: {np.bincount(G_val)}")
print(f"Test:  {X_test.shape},  group distribution: {np.bincount(G_test)}")

# Normalize features
X_mean = X_train.mean(0)
X_std = X_train.std(0) + 1e-8
X_train = (X_train - X_mean) / X_std
X_val = (X_val - X_mean) / X_std
X_test = (X_test - X_mean) / X_std

val_dataset = TensorDataset(
    torch.FloatTensor(X_val), torch.LongTensor(Y_val), torch.LongTensor(G_val)
)
val_loader = DataLoader(val_dataset, batch_size=512, shuffle=False)

test_dataset = TensorDataset(
    torch.FloatTensor(X_test), torch.LongTensor(Y_test), torch.LongTensor(G_test)
)
test_loader = DataLoader(test_dataset, batch_size=512, shuffle=False)

N_EPOCHS = 120
LR = 1e-3
BATCH_SIZE = 256
WD = 1e-4

print("\n" + "=" * 60)
print("Training ERM (baseline)...")
model_erm = run_training(
    "ERM",
    n_epochs=N_EPOCHS,
    lr=LR,
    batch_size=BATCH_SIZE,
    wd=WD,
    X_train=X_train,
    Y_train=Y_train,
    G_train=G_train,
    val_loader=val_loader,
    seed=0,
)

print("\n" + "=" * 60)
print("Training Continuous Regularization (ablation)...")
model_cont = run_training(
    "Continuous_Reg",
    n_epochs=N_EPOCHS,
    lr=LR,
    batch_size=BATCH_SIZE,
    wd=WD,
    X_train=X_train,
    Y_train=Y_train,
    G_train=G_train,
    val_loader=val_loader,
    seed=0,
)

print("\n" + "=" * 60)
print("Training TASI (proposed method)...")
model_tasi = run_training(
    "TASI",
    n_epochs=N_EPOCHS,
    lr=LR,
    batch_size=BATCH_SIZE,
    wd=WD,
    X_train=X_train,
    Y_train=Y_train,
    G_train=G_train,
    val_loader=val_loader,
    seed=0,
)

# ─────────────────────────────────────────────
# Final Test Evaluation
# ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("FINAL TEST EVALUATION")
criterion = nn.CrossEntropyLoss()
for name, model in [
    ("ERM", model_erm),
    ("Continuous_Reg", model_cont),
    ("TASI", model_tasi),
]:
    test_loss, test_acc, wg_acc, grp_accs = evaluate(
        model, test_loader, criterion, None
    )
    print(f"[{name}] Test Acc={test_acc:.4f}, Worst-Group Acc={wg_acc:.4f}")
    print(f"  Group accs: {grp_accs}")
    experiment_data[name]["test_overall_acc"] = float(test_acc)
    experiment_data[name]["test_worst_group_acc"] = float(wg_acc)
    experiment_data[name]["test_group_accs"] = {
        g: float(a) for g, a in grp_accs.items()
    }

# ─────────────────────────────────────────────
# Visualization
# ─────────────────────────────────────────────
epochs = np.arange(N_EPOCHS)
colors = {"ERM": "blue", "Continuous_Reg": "orange", "TASI": "red"}

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    "TASI vs Baselines: Shortcut Plateau Detection & Intervention", fontsize=14
)

# Plot 1: Training loss
ax = axes[0, 0]
for method in ["ERM", "Continuous_Reg", "TASI"]:
    ax.plot(
        epochs,
        experiment_data[method]["losses"]["train"],
        color=colors[method],
        label=method,
        alpha=0.8,
    )
# Mark TASI intervention epochs
for ep in experiment_data["TASI"].get("intervention_epochs", []):
    ax.axvline(x=ep, color="red", linestyle="--", alpha=0.3)
ax.set_xlabel("Epoch")
ax.set_ylabel("Training Loss")
ax.set_title("Training Loss (red dashed = TASI intervention)")
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Validation loss
ax = axes[0, 1]
for method in ["ERM", "Continuous_Reg", "TASI"]:
    ax.plot(
        epochs,
        experiment_data[method]["losses"]["val"],
        color=colors[method],
        label=method,
        alpha=0.8,
    )
ax.set_xlabel("Epoch")
ax.set_ylabel("Validation Loss")
ax.set_title("Validation Loss")
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Worst-group accuracy
ax = axes[1, 0]
for method in ["ERM", "Continuous_Reg", "TASI"]:
    wg = experiment_data[method]["metrics"]["worst_group"]
    ax.plot(epochs, wg, color=colors[method], label=method, linewidth=2)
for ep in experiment_data["TASI"].get("intervention_epochs", []):
    ax.axvline(x=ep, color="red", linestyle="--", alpha=0.3)
ax.set_xlabel("Epoch")
ax.set_ylabel("Worst-Group Accuracy")
ax.set_title("Worst-Group Accuracy (Primary Metric)")
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Overall val accuracy
ax = axes[1, 1]
for method in ["ERM", "Continuous_Reg", "TASI"]:
    va = experiment_data[method]["metrics"]["val"]
    ax.plot(epochs, va, color=colors[method], label=method, linewidth=2)
plateau_erm = experiment_data["ERM"]["plateau_detected"]
plateau_tasi = experiment_data["TASI"]["plateau_detected"]
ax2 = ax.twinx()
ax2.fill_between(epochs, plateau_tasi, alpha=0.1, color="red", label="TASI plateau")
ax2.set_ylabel("Plateau Detected (TASI)", color="red")
ax.set_xlabel("Epoch")
ax.set_ylabel("Overall Val Accuracy")
ax.set_title("Overall Validation Accuracy + Plateau Signal")
ax.legend(loc="lower right")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "tasi_training_curves.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# Summary bar chart
fig, ax = plt.subplots(1, 1, figsize=(8, 5))
methods = ["ERM", "Continuous_Reg", "TASI"]
wg_test = [experiment_data[m]["test_worst_group_acc"] for m in methods]
overall_test = [experiment_data[m]["test_overall_acc"] for m in methods]
x = np.arange(len(methods))
w = 0.35
bars1 = ax.bar(
    x - w / 2,
    overall_test,
    w,
    label="Overall Acc",
    color=["blue", "orange", "red"],
    alpha=0.7,
)
bars2 = ax.bar(
    x + w / 2,
    wg_test,
    w,
    label="Worst-Group Acc",
    color=["blue", "orange", "red"],
    alpha=1.0,
)
ax.set_xticks(x)
ax.set_xticklabels(methods)
ax.set_ylabel("Test Accuracy")
ax.set_title("Test Accuracy Summary (Overall vs Worst-Group)")
ax.legend()
ax.set_ylim(0, 1)
for bar in bars1:
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        bar.get_height() + 0.01,
        f"{bar.get_height():.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
for bar in bars2:
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        bar.get_height() + 0.01,
        f"{bar.get_height():.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "tasi_test_summary.png"), dpi=150, bbox_inches="tight"
)
plt.close()

print("\nPlots saved to working_dir.")

# ─────────────────────────────────────────────
# Save experiment data
# ─────────────────────────────────────────────
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("Experiment data saved.")

# Final summary
print("\n" + "=" * 60)
print("FINAL SUMMARY")
for method in ["ERM", "Continuous_Reg", "TASI"]:
    wg = experiment_data[method]["test_worst_group_acc"]
    oa = experiment_data[method]["test_overall_acc"]
    print(f"  {method:20s}: Overall={oa:.4f}, Worst-Group={wg:.4f}")
print("=" * 60)
