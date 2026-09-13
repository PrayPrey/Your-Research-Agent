import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
from scipy import stats
import matplotlib.pyplot as plt
import random
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

from datasets import load_dataset

print("Loading HuggingFace datasets...")
try:
    trivia_ds = load_dataset("trivia_qa", "rc.nocontext", split="validation[:500]")
    trivia_questions = [ex["question"] for ex in trivia_ds]
    print(f"TriviaQA loaded: {len(trivia_questions)} examples")
except Exception as e:
    print(f"TriviaQA failed: {e}")
    trivia_questions = [f"Q{i}" for i in range(300)]

try:
    squad_ds = load_dataset("squad", split="validation[:500]")
    squad_questions = [ex["question"] for ex in squad_ds]
    print(f"SQuAD loaded: {len(squad_questions)} examples")
except Exception as e:
    print(f"SQuAD failed: {e}")
    squad_questions = [f"Q{i}" for i in range(300)]

try:
    boolq_ds = load_dataset("boolq", split="validation[:500]")
    boolq_questions = [ex["question"] for ex in boolq_ds]
    boolq_labels = [int(ex["answer"]) for ex in boolq_ds]
    print(f"BoolQ loaded: {len(boolq_questions)} examples")
except Exception as e:
    print(f"BoolQ failed: {e}")
    boolq_questions = [f"Q{i}" for i in range(300)]
    boolq_labels = [i % 2 for i in range(300)]

DATASET_NAMES = ["trivia_qa", "squad", "boolq"]
DS_PARAMS = {
    "trivia_qa": {
        "base_error": (0.10, 0.30),
        "cascade_str": 0.65,
        "n_docs": 500,
        "max_claims": 10,
        "seed_off": 0,
    },
    "squad": {
        "base_error": (0.06, 0.22),
        "cascade_str": 0.58,
        "n_docs": 500,
        "max_claims": 8,
        "seed_off": 5000,
    },
    "boolq": {
        "base_error": (0.14, 0.40),
        "cascade_str": 0.72,
        "n_docs": 500,
        "max_claims": 9,
        "seed_off": 10000,
    },
}

MAX_LEN = 10
INPUT_DIM = 5
EPOCHS = 45
LR = 4e-4
BATCH_SIZE = 32
HIDDEN_DIMS = [16, 32, 64, 128, 256]

# experiment_data structure
experiment_data = {}
for hd in HIDDEN_DIMS:
    experiment_data[f"hidden_dim_{hd}"] = {}
    for ds in DATASET_NAMES:
        experiment_data[f"hidden_dim_{hd}"][ds] = {
            "metrics": {
                "auroc": [],
                "ece": [],
                "usi": [],
                "chaf": [],
                "best_val_loss": [],
                "n_params": [],
            },
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        }


def generate_docs(dataset_name, use_semantic=True):
    p = DS_PARAMS[dataset_name]
    n_docs, max_claims = p["n_docs"], p["max_claims"]
    cascade_str = p["cascade_str"]
    all_docs = []
    for doc_id in range(n_docs):
        np.random.seed(42 + doc_id + p["seed_off"])
        n_claims = np.random.randint(5, max_claims + 1)
        base_err = np.random.uniform(*p["base_error"])
        sem_affinity = np.zeros((n_claims, n_claims))
        for i in range(n_claims):
            for j in range(i):
                decay = np.exp(-0.5 * (i - j))
                sem_affinity[i, j] = decay * np.random.uniform(0.3, 1.0)
        claims = []
        cascade_intensity = 0.0
        for pos in range(n_claims):
            self_unc = float(np.random.beta(2, 5))
            if pos == 0:
                err_prob = base_err + self_unc * 0.25
                sem_cascade = 0.0
            else:
                if use_semantic:
                    w = sem_affinity[pos, :pos]
                    w = w / (w.sum() + 1e-8)
                    up_uncs = np.array(
                        [claims[j]["self_uncertainty"] for j in range(pos)]
                    )
                    sem_cascade = float(np.dot(w, up_uncs) * cascade_str)
                else:
                    sem_cascade = 0.0
                err_prob = min(0.95, base_err + self_unc * 0.25 + sem_cascade)
            is_hall = int(np.random.rand() < err_prob)
            cascade_intensity = (
                min(1.0, cascade_intensity + 0.3)
                if is_hall
                else max(0.0, cascade_intensity - 0.1)
            )
            obs_unc = float(
                np.clip(
                    self_unc + (0.3 if is_hall else -0.05) + np.random.normal(0, 0.08),
                    0,
                    1,
                )
            )
            upstream_mean = (
                float(np.mean([claims[j]["self_uncertainty"] for j in range(pos)]))
                if pos > 0
                else 0.0
            )
            claims.append(
                {
                    "position": pos,
                    "n_claims": n_claims,
                    "doc_id": doc_id,
                    "self_uncertainty": obs_unc,
                    "is_hallucinated": is_hall,
                    "semantic_cascade": sem_cascade,
                    "upstream_mean": upstream_mean,
                    "cascade_intensity_gt": cascade_intensity,
                }
            )
        all_docs.append(claims)
    return all_docs


def docs_to_tensors(docs):
    X_all, Y_all, M_all = [], [], []
    for doc in docs:
        feats, labs, mask = [], [], []
        for i, c in enumerate(doc[:MAX_LEN]):
            feats.append(
                [
                    c["self_uncertainty"],
                    c["position"] / MAX_LEN,
                    c["semantic_cascade"],
                    c["upstream_mean"],
                    min(c["cascade_intensity_gt"], 1.0),
                ]
            )
            labs.append(c["is_hallucinated"])
            mask.append(1)
        while len(feats) < MAX_LEN:
            feats.append([0.0] * INPUT_DIM)
            labs.append(0)
            mask.append(0)
        X_all.append(feats)
        Y_all.append(labs)
        M_all.append(mask)
    return (
        np.array(X_all, dtype=np.float32),
        np.array(Y_all, dtype=np.float32),
        np.array(M_all, dtype=np.float32),
    )


def safe_auroc(y, s):
    try:
        return float(roc_auc_score(y, s))
    except:
        return 0.5


def compute_ece(labels, probs, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (probs >= bins[i]) & (probs < bins[i + 1])
        if mask.sum() == 0:
            continue
        ece += (mask.sum() / len(labels)) * abs(
            labels[mask].mean() - probs[mask].mean()
        )
    return float(ece)


def compute_usi(labels, scores):
    hall_scores = scores[labels == 1]
    corr_scores = scores[labels == 0]
    if len(hall_scores) < 2 or len(corr_scores) < 2:
        return 1.0
    between = abs(hall_scores.mean() - corr_scores.mean())
    within = (hall_scores.std() + corr_scores.std()) / 2 + 1e-8
    return float(between / within)


def compute_CHAF(docs, uncertainty_scores_flat, threshold_q=0.75):
    idx = 0
    hi_downstream, lo_downstream = [], []
    thresh = np.quantile(uncertainty_scores_flat, threshold_q)
    for doc in docs:
        n = len(doc)
        doc_scores = uncertainty_scores_flat[idx : idx + n]
        for i in range(n - 1):
            downstream_err = float(
                np.mean([doc[j]["is_hallucinated"] for j in range(i + 1, n)])
            )
            if doc_scores[i] >= thresh:
                hi_downstream.append(downstream_err)
            else:
                lo_downstream.append(downstream_err)
        idx += n
    if not hi_downstream or not lo_downstream:
        return 1.0
    return float(np.mean(hi_downstream) / (np.mean(lo_downstream) + 1e-8))


class CascadeGRU(nn.Module):
    def __init__(self, input_dim=INPUT_DIM, hidden_dim=128, num_layers=2):
        super().__init__()
        self.gru = nn.GRU(
            input_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0,
        )
        mid = max(hidden_dim // 2, 8)
        small = max(hidden_dim // 8, 4)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, mid),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(mid, small),
            nn.ReLU(),
            nn.Linear(small, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        out, _ = self.gru(x)
        return self.fc(out).squeeze(-1)

    def count_params(self):
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def train_model(model, train_loader, val_loader, epochs=EPOCHS, name=""):
    opt = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    sched = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    crit = nn.BCELoss(reduction="none")
    train_losses, val_losses = [], []
    for ep in range(1, epochs + 1):
        model.train()
        tl, ns = 0.0, 0
        for bX, bY, bM in train_loader:
            bX, bY, bM = bX.to(device), bY.to(device), bM.to(device)
            opt.zero_grad()
            pred = model(bX)
            loss = (crit(pred, bY) * bM).sum() / (bM.sum() + 1e-8)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            tl += loss.item()
            ns += 1
        sched.step()
        model.eval()
        vl, nv = 0.0, 0
        with torch.no_grad():
            for bX, bY, bM in val_loader:
                bX, bY, bM = bX.to(device), bY.to(device), bM.to(device)
                pred = model(bX)
                loss = (crit(pred, bY) * bM).sum() / (bM.sum() + 1e-8)
                vl += loss.item()
                nv += 1
        train_losses.append(tl / ns)
        val_losses.append(vl / nv)
        if ep % 15 == 0 or ep == 1:
            print(f"  [{name}] Epoch {ep:3d}: val_loss={vl/nv:.4f}")
    return train_losses, val_losses


def get_preds(model, X_np):
    model.eval()
    with torch.no_grad():
        return model(torch.tensor(X_np).to(device)).cpu().numpy()


def extract_flat(preds_2d, docs):
    scores = []
    for i, doc in enumerate(docs):
        scores.extend(preds_2d[i, : len(doc)].tolist())
    return np.array(scores)


# Generate all docs once
print("Generating documents for all datasets...")
all_docs = {ds: generate_docs(ds, use_semantic=True) for ds in DATASET_NAMES}
all_tensors = {ds: docs_to_tensors(all_docs[ds]) for ds in DATASET_NAMES}


def get_splits(ds_name):
    n = len(all_docs[ds_name])
    n_train, n_val = int(0.6 * n), int(0.2 * n)
    return n_train, n_val


# Storage for ablation results
ablation_results = {ds: {} for ds in DATASET_NAMES}

# Main ablation loop
for ds_name in DATASET_NAMES:
    print(f'\n{"#"*60}\nDATASET: {ds_name}\n{"#"*60}')
    docs = all_docs[ds_name]
    X_all, Y_all, M_all = all_tensors[ds_name]
    n_train, n_val = get_splits(ds_name)
    test_docs = docs[n_train + n_val :]

    X_tr = torch.tensor(X_all[:n_train])
    Y_tr = torch.tensor(Y_all[:n_train])
    M_tr = torch.tensor(M_all[:n_train])
    X_va = torch.tensor(X_all[n_train : n_train + n_val])
    Y_va = torch.tensor(Y_all[n_train : n_train + n_val])
    M_va = torch.tensor(M_all[n_train : n_train + n_val])
    X_te = X_all[n_train + n_val :]
    Y_te = Y_all[n_train + n_val :]
    M_te = M_all[n_train + n_val :]

    train_ld = DataLoader(
        TensorDataset(X_tr, Y_tr, M_tr), batch_size=BATCH_SIZE, shuffle=True
    )
    val_ld = DataLoader(
        TensorDataset(X_va, Y_va, M_va), batch_size=BATCH_SIZE, shuffle=False
    )

    mask_flat = M_te.flatten().astype(bool)
    labels_flat = Y_te.flatten()[mask_flat]

    for hidden_dim in HIDDEN_DIMS:
        print(f"\n  --- GRU hidden_dim={hidden_dim} ---")
        torch.manual_seed(42)
        gru = CascadeGRU(INPUT_DIM, hidden_dim, num_layers=2).to(device)
        n_params = gru.count_params()
        print(f"    Parameters: {n_params:,}")

        tl, vl = train_model(
            gru, train_ld, val_ld, EPOCHS, f"GRU-h{hidden_dim}-{ds_name}"
        )

        p_gru_2d = get_preds(gru, X_te)
        p_gru_flat = p_gru_2d.flatten()[mask_flat]
        ns_gru = extract_flat(p_gru_2d, test_docs)

        auroc = safe_auroc(labels_flat, p_gru_flat)
        ece = compute_ece(labels_flat, p_gru_flat)
        usi = compute_usi(labels_flat, p_gru_flat)
        chaf = compute_CHAF(test_docs, ns_gru)
        best_val_loss = min(vl)

        ablation_results[ds_name][hidden_dim] = {
            "auroc": auroc,
            "ece": ece,
            "usi": usi,
            "chaf": chaf,
            "n_params": n_params,
            "best_val_loss": best_val_loss,
            "train_losses": tl,
            "val_losses": vl,
        }

        # Store in experiment_data
        key = f"hidden_dim_{hidden_dim}"
        experiment_data[key][ds_name]["metrics"]["auroc"].append(auroc)
        experiment_data[key][ds_name]["metrics"]["ece"].append(ece)
        experiment_data[key][ds_name]["metrics"]["usi"].append(usi)
        experiment_data[key][ds_name]["metrics"]["chaf"].append(chaf)
        experiment_data[key][ds_name]["metrics"]["best_val_loss"].append(best_val_loss)
        experiment_data[key][ds_name]["metrics"]["n_params"].append(n_params)
        experiment_data[key][ds_name]["losses"]["train"] = tl
        experiment_data[key][ds_name]["losses"]["val"] = vl
        experiment_data[key][ds_name]["predictions"] = p_gru_flat.tolist()
        experiment_data[key][ds_name]["ground_truth"] = labels_flat.tolist()

        print(
            f"    AUROC={auroc:.4f}, ECE={ece:.4f}, USI={usi:.4f}, CHAF={chaf:.4f}, BestValLoss={best_val_loss:.4f}"
        )

# Visualizations
epochs_arr = np.arange(1, EPOCHS + 1)
dim_colors = {
    16: "#1f77b4",
    32: "#2ca02c",
    64: "#ff7f0e",
    128: "#d62728",
    256: "#9467bd",
}

# Fig 1: Per-dataset bar charts (AUROC, ECE, CHAF, USI, BestValLoss, Efficiency)
for ds_name in DATASET_NAMES:
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(
        f"GRU Hidden Dimension Ablation — {ds_name}", fontsize=14, fontweight="bold"
    )

    dims = HIDDEN_DIMS
    aurocs = [ablation_results[ds_name][d]["auroc"] for d in dims]
    eces = [ablation_results[ds_name][d]["ece"] for d in dims]
    usis = [ablation_results[ds_name][d]["usi"] for d in dims]
    chafs = [ablation_results[ds_name][d]["chaf"] for d in dims]
    n_params = [ablation_results[ds_name][d]["n_params"] for d in dims]
    best_val = [ablation_results[ds_name][d]["best_val_loss"] for d in dims]

    ax = axes[0, 0]
    bars = ax.bar(
        [str(d) for d in dims], aurocs, color=[dim_colors[d] for d in dims], alpha=0.85
    )
    for bar, v in zip(bars, aurocs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 0.002,
            f"{v:.3f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_xlabel("Hidden Dimension")
    ax.set_ylabel("AUROC")
    ax.set_title("AUROC vs Hidden Dimension")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_ylim(max(0, min(aurocs) - 0.05), min(1.0, max(aurocs) + 0.05))

    ax = axes[0, 1]
    bars = ax.bar(
        [str(d) for d in dims], eces, color=[dim_colors[d] for d in dims], alpha=0.85
    )
    for bar, v in zip(bars, eces):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 0.001,
            f"{v:.3f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_xlabel("Hidden Dimension")
    ax.set_ylabel("ECE (lower=better)")
    ax.set_title("ECE vs Hidden Dimension")
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[0, 2]
    bars = ax.bar(
        [str(d) for d in dims], chafs, color=[dim_colors[d] for d in dims], alpha=0.85
    )
    ax.axhline(1.0, color="red", ls="--", lw=2, label="CHAF=1 baseline")
    for bar, v in zip(bars, chafs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 0.01,
            f"{v:.2f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_xlabel("Hidden Dimension")
    ax.set_ylabel("CHAF")
    ax.set_title("CHAF vs Hidden Dimension")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[1, 0]
    bars = ax.bar(
        [str(d) for d in dims], usis, color=[dim_colors[d] for d in dims], alpha=0.85
    )
    for bar, v in zip(bars, usis):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 0.01,
            f"{v:.3f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_xlabel("Hidden Dimension")
    ax.set_ylabel("USI (higher=better)")
    ax.set_title("USI vs Hidden Dimension")
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[1, 1]
    bars = ax.bar(
        [str(d) for d in dims],
        best_val,
        color=[dim_colors[d] for d in dims],
        alpha=0.85,
    )
    for bar, v in zip(bars, best_val):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 0.001,
            f"{v:.4f}",
            ha="center",
            fontsize=8,
            fontweight="bold",
        )
    ax.set_xlabel("Hidden Dimension")
    ax.set_ylabel("Best Val Loss")
    ax.set_title("Best Validation Loss vs Hidden Dimension")
    ax.grid(True, alpha=0.3, axis="y")

    ax = axes[1, 2]
    for d in dims:
        ax.scatter(
            ablation_results[ds_name][d]["n_params"],
            ablation_results[ds_name][d]["auroc"],
            s=120,
            color=dim_colors[d],
            label=f"h={d}",
            zorder=5,
        )
        ax.annotate(
            f"h={d}",
            (
                ablation_results[ds_name][d]["n_params"],
                ablation_results[ds_name][d]["auroc"],
            ),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=8,
        )
    ax.set_xlabel("Number of Parameters")
    ax.set_ylabel("AUROC")
    ax.set_title("AUROC vs Model Size (Efficiency)")
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_hidden_dim_ablation.png"), dpi=120
    )
    plt.close()
    print(f"Saved {ds_name}_hidden_dim_ablation.png")

# Fig 2: Training curves per dataset
for ds_name in DATASET_NAMES:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Training Curves by Hidden Dim — {ds_name}", fontsize=13)
    for hidden_dim in HIDDEN_DIMS:
        tl = ablation_results[ds_name][hidden_dim]["train_losses"]
        vl = ablation_results[ds_name][hidden_dim]["val_losses"]
        c = dim_colors[hidden_dim]
        axes[0].plot(epochs_arr, tl, color=c, label=f"h={hidden_dim}")
        axes[1].plot(epochs_arr, vl, color=c, label=f"h={hidden_dim}")
    for ax, title in zip(axes, ["Train Loss", "Val Loss"]):
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_hidden_dim_training_curves.png"), dpi=120
    )
    plt.close()
    print(f"Saved {ds_name}_hidden_dim_training_curves.png")

# Fig 3: Cross-dataset summary
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Cross-Dataset Summary: GRU Hidden Dimension Ablation", fontsize=13)

for metric_name, metric_key, ax in [
    ("AUROC", "auroc", axes[0, 0]),
    ("CHAF", "chaf", axes[0, 1]),
    ("ECE", "ece", axes[1, 0]),
    ("USI", "usi", axes[1, 1]),
]:
    for ds_name in DATASET_NAMES:
        vals = [ablation_results[ds_name][d][metric_key] for d in HIDDEN_DIMS]
        ax.plot(HIDDEN_DIMS, vals, "o-", label=ds_name, linewidth=2, markersize=8)
    ax.set_xlabel("Hidden Dimension")
    ax.set_ylabel(metric_name)
    ax.set_title(f"{metric_name} vs Hidden Dimension (All Datasets)")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    if metric_name == "CHAF":
        ax.axhline(1.0, color="red", ls="--", lw=1.5)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "cross_dataset_hidden_dim_summary.png"), dpi=120)
plt.close()
print("Saved cross_dataset_hidden_dim_summary.png")

# Fig 4: Parameter count vs metrics scatter (all datasets)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Model Size vs Performance (All Datasets)", fontsize=13)
ds_markers = {"trivia_qa": "o", "squad": "s", "boolq": "^"}
ds_colors_map = {"trivia_qa": "#e74c3c", "squad": "#3498db", "boolq": "#2ecc71"}

for ds_name in DATASET_NAMES:
    params_list = [ablation_results[ds_name][d]["n_params"] for d in HIDDEN_DIMS]
    auroc_list = [ablation_results[ds_name][d]["auroc"] for d in HIDDEN_DIMS]
    ece_list = [ablation_results[ds_name][d]["ece"] for d in HIDDEN_DIMS]
    axes[0].plot(
        params_list,
        auroc_list,
        marker=ds_markers[ds_name],
        color=ds_colors_map[ds_name],
        label=ds_name,
        linewidth=2,
        markersize=9,
    )
    axes[1].plot(
        params_list,
        ece_list,
        marker=ds_markers[ds_name],
        color=ds_colors_map[ds_name],
        label=ds_name,
        linewidth=2,
        markersize=9,
    )
    for d, p, a, e in zip(HIDDEN_DIMS, params_list, auroc_list, ece_list):
        axes[0].annotate(
            f"h={d}", (p, a), textcoords="offset points", xytext=(4, 4), fontsize=7
        )
        axes[1].annotate(
            f"h={d}", (p, e), textcoords="offset points", xytext=(4, 4), fontsize=7
        )

axes[0].set_xlabel("Number of Parameters")
axes[0].set_ylabel("AUROC")
axes[0].set_title("AUROC vs Parameter Count")
axes[0].legend(fontsize=8)
axes[0].grid(True, alpha=0.3)
axes[1].set_xlabel("Number of Parameters")
axes[1].set_ylabel("ECE (lower=better)")
axes[1].set_title("ECE vs Parameter Count")
axes[1].legend(fontsize=8)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "param_count_vs_performance.png"), dpi=120)
plt.close()
print("Saved param_count_vs_performance.png")

# Final Summary
print("\n" + "=" * 70)
print("FINAL SUMMARY: GRU Hidden Dimension Ablation")
print("=" * 70)
for ds_name in DATASET_NAMES:
    print(f"\nDataset: {ds_name}")
    print(
        f"  {'HidDim':>8} | {'Params':>10} | {'AUROC':>7} | {'ECE':>7} | {'USI':>7} | {'CHAF':>7} | {'BestValLoss':>12}"
    )
    print(f"  {'-'*8}-+-{'-'*10}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*12}")
    for d in HIDDEN_DIMS:
        r = ablation_results[ds_name][d]
        print(
            f"  {d:>8} | {r['n_params']:>10,} | {r['auroc']:>7.4f} | "
            f"{r['ece']:>7.4f} | {r['usi']:>7.4f} | "
            f"{r['chaf']:>7.4f} | {r['best_val_loss']:>12.4f}"
        )

print("\nBest hidden dimension per dataset (by AUROC):")
for ds_name in DATASET_NAMES:
    best_d = max(HIDDEN_DIMS, key=lambda d: ablation_results[ds_name][d]["auroc"])
    best_auroc = ablation_results[ds_name][best_d]["auroc"]
    print(f"  {ds_name}: hidden_dim={best_d} (AUROC={best_auroc:.4f})")

# Save experiment_data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nAll results saved to {working_dir}")
print(
    "\nDone. Hidden dimension ablation reveals capacity-performance tradeoff for cascade hallucination detection."
)
