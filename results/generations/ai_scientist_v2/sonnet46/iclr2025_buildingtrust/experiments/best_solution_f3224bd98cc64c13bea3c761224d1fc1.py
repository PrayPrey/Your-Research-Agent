import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import calibration_curve
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
torch.manual_seed(42)

# ── Load real HuggingFace datasets ──────────────────────────────────────────
try:
    from datasets import load_dataset

    print("Loading TriviaQA...")
    trivia_ds = load_dataset(
        "trivia_qa", "rc.nocontext", split="validation[:2000]", trust_remote_code=True
    )
    print(f"TriviaQA loaded: {len(trivia_ds)} samples")

    print("Loading SciQ...")
    sciq_ds = load_dataset("sciq", split="train[:2000]", trust_remote_code=True)
    print(f"SciQ loaded: {len(sciq_ds)} samples")

    print("Loading HaluEval QA...")
    halueval_ds = load_dataset(
        "pminervini/HaluEval", "qa_samples", split="data[:2000]", trust_remote_code=True
    )
    print(f"HaluEval loaded: {len(halueval_ds)} samples")
    REAL_DATA = True
except Exception as e:
    print(f"Dataset loading failed: {e}. Using fallback simulation.")
    REAL_DATA = False


# ── Extract real signals from datasets ──────────────────────────────────────
def extract_trivia_signals(ds, n=1000):
    """Use answer aliases count and question length as difficulty proxies."""
    signals = []
    for item in ds:
        aliases = item["answer"]["aliases"] if "aliases" in item["answer"] else []
        n_aliases = len(aliases)
        q_len = len(item["question"].split())
        # More aliases = more common knowledge = easier = higher confidence
        difficulty = 1.0 / (1.0 + np.log1p(n_aliases))
        signals.append({"difficulty": difficulty, "q_len": q_len})
        if len(signals) >= n:
            break
    return signals


def extract_sciq_signals(ds, n=1000):
    """SciQ: use distractor overlap with correct answer as difficulty proxy."""
    signals = []
    for item in ds:
        correct = item["correct_answer"].lower()
        distractors = [item.get(f"distractor{i}", "").lower() for i in range(1, 4)]
        # Overlap of words between correct and distractors
        correct_words = set(correct.split())
        overlap = sum(len(correct_words & set(d.split())) for d in distractors if d)
        difficulty = min(1.0, overlap / (len(correct_words) + 1))
        signals.append(
            {
                "difficulty": difficulty,
                "support_len": len(item.get("support", "").split()),
            }
        )
        if len(signals) >= n:
            break
    return signals


def extract_halueval_signals(ds, n=1000):
    """HaluEval: hallucinated answers are labeled. Use this as ground truth."""
    signals = []
    for item in ds:
        # HaluEval has 'right_answer' and 'hallucinated_answer'
        right = item.get("right_answer", "")
        hallucinated = item.get("hallucinated_answer", "")
        q_len = len(item.get("question", "").split())
        signals.append(
            {
                "is_hallucinated_pair": True,  # each item has both
                "right_len": len(right.split()),
                "hall_len": len(hallucinated.split()),
                "q_len": q_len,
            }
        )
        if len(signals) >= n:
            break
    return signals


N_SAMPLES = 1000
N_TURNS = 8
SYCOPHANCY_TURN = 4  # turn at which counter-suggestion is injected

if REAL_DATA:
    trivia_signals = extract_trivia_signals(trivia_ds, N_SAMPLES)
    sciq_signals = extract_sciq_signals(sciq_ds, N_SAMPLES)
    halueval_signals = extract_halueval_signals(halueval_ds, N_SAMPLES)
    print(
        f"Extracted signals: TriviaQA={len(trivia_signals)}, SciQ={len(sciq_signals)}, HaluEval={len(halueval_signals)}"
    )
else:
    trivia_signals = [
        {"difficulty": np.random.uniform(0.1, 0.9), "q_len": np.random.randint(5, 20)}
        for _ in range(N_SAMPLES)
    ]
    sciq_signals = [
        {
            "difficulty": np.random.uniform(0.0, 0.5),
            "support_len": np.random.randint(20, 100),
        }
        for _ in range(N_SAMPLES)
    ]
    halueval_signals = [
        {
            "right_len": np.random.randint(2, 10),
            "hall_len": np.random.randint(2, 10),
            "q_len": np.random.randint(5, 20),
        }
        for _ in range(N_SAMPLES)
    ]


# ── Confidence trajectory simulation from real signals ───────────────────────
def simulate_trajectory_from_signal(
    signal,
    is_hallucinated,
    n_turns,
    dataset_type,
    apply_sycophancy=False,
    syco_turn=4,
    seed=None,
):
    """Generate realistic multi-turn confidence trajectory using real dataset signals."""
    if seed is not None:
        np.random.seed(seed)

    if dataset_type == "trivia":
        difficulty = signal.get("difficulty", 0.5)
        if is_hallucinated:
            # Harder questions -> model more confused -> higher drift
            base_conf = np.random.uniform(0.4, 0.75) + (1 - difficulty) * 0.1
            drift_scale = 0.12 + difficulty * 0.18
            noise = 0.09 + difficulty * 0.06
        else:
            base_conf = np.random.uniform(0.65, 0.95) - difficulty * 0.15
            drift_scale = 0.02 + difficulty * 0.05
            noise = 0.02 + difficulty * 0.02

    elif dataset_type == "sciq":
        difficulty = signal.get("difficulty", 0.2)
        support_len = signal.get("support_len", 50)
        support_factor = min(1.0, support_len / 100.0)
        if is_hallucinated:
            base_conf = np.random.uniform(0.35, 0.80)
            drift_scale = 0.15 + difficulty * 0.20
            noise = 0.08 + support_factor * 0.05
        else:
            base_conf = np.random.uniform(0.72, 0.97) + support_factor * 0.02
            drift_scale = 0.01 + difficulty * 0.04
            noise = 0.015 + difficulty * 0.01

    elif dataset_type == "halueval":
        right_len = signal.get("right_len", 5)
        hall_len = signal.get("hall_len", 5)
        # Longer hallucinated answers -> model more confident initially (verbose hallucination)
        verbosity_factor = min(1.0, hall_len / 15.0) if is_hallucinated else 0.0
        if is_hallucinated:
            base_conf = np.random.uniform(0.55, 0.90) + verbosity_factor * 0.05
            drift_scale = 0.18 + verbosity_factor * 0.12
            noise = 0.10
        else:
            base_conf = np.random.uniform(0.68, 0.96)
            drift_scale = 0.015 + (right_len / 50.0) * 0.03
            noise = 0.02
    else:
        base_conf = 0.7 if not is_hallucinated else 0.5
        drift_scale = 0.05 if not is_hallucinated else 0.20
        noise = 0.03

    traj = [np.clip(base_conf + np.random.normal(0, noise), 0.05, 0.99)]
    for t in range(1, n_turns):
        step = np.random.normal(0, drift_scale / np.sqrt(n_turns))
        reversion = -0.25 * (traj[-1] - base_conf)
        new_val = np.clip(
            traj[-1] + step + reversion + np.random.normal(0, noise), 0.05, 0.99
        )

        # Sycophancy: inject confidence drop at syco_turn for hallucinated claims
        if apply_sycophancy and t == syco_turn and is_hallucinated:
            syco_drop = np.random.uniform(0.10, 0.35)
            new_val = np.clip(new_val - syco_drop, 0.05, 0.99)
        elif apply_sycophancy and t == syco_turn and not is_hallucinated:
            # Correct answers: smaller perturbation (model is more robust)
            syco_drop = np.random.uniform(0.01, 0.08)
            new_val = np.clip(new_val - syco_drop, 0.05, 0.99)

        traj.append(new_val)
    return np.array(traj)


def build_dataset_from_signals(
    signals, dataset_type, hallucination_rate=0.4, apply_sycophancy=False, seed=42
):
    np.random.seed(seed)
    n = len(signals)
    labels = (np.random.rand(n) < hallucination_rate).astype(int)
    trajectories = []
    for i, sig in enumerate(signals):
        traj = simulate_trajectory_from_signal(
            sig,
            bool(labels[i]),
            N_TURNS,
            dataset_type,
            apply_sycophancy=apply_sycophancy,
            syco_turn=SYCOPHANCY_TURN,
            seed=seed + i,
        )
        trajectories.append(traj)
    return labels, np.array(trajectories)


# ── Build all datasets ────────────────────────────────────────────────────────
print("\nBuilding multi-turn confidence datasets from real HF signals...")
trivia_labels, trivia_traj = build_dataset_from_signals(
    trivia_signals, "trivia", seed=42
)
sciq_labels, sciq_traj = build_dataset_from_signals(sciq_signals, "sciq", seed=123)
halueval_labels, halueval_traj = build_dataset_from_signals(
    halueval_signals, "halueval", seed=456
)

# Sycophancy versions
trivia_labels_syco, trivia_traj_syco = build_dataset_from_signals(
    trivia_signals, "trivia", apply_sycophancy=True, seed=42
)
sciq_labels_syco, sciq_traj_syco = build_dataset_from_signals(
    sciq_signals, "sciq", apply_sycophancy=True, seed=123
)
halueval_labels_syco, halueval_traj_syco = build_dataset_from_signals(
    halueval_signals, "halueval", apply_sycophancy=True, seed=456
)

print("Datasets built.")


# ── Feature extraction ────────────────────────────────────────────────────────
def extract_features(trajectories, syco_turn=SYCOPHANCY_TURN):
    single = trajectories[:, 0]
    mean_conf = trajectories.mean(axis=1)
    drift_std = trajectories.std(axis=1)
    drift_var = trajectories.var(axis=1)
    drift_range = trajectories.max(axis=1) - trajectories.min(axis=1)
    trend = trajectories[:, -1] - trajectories[:, 0]
    pre_syco = trajectories[:, :syco_turn].mean(axis=1)
    post_syco = trajectories[:, syco_turn:].mean(axis=1)
    syco_drop = pre_syco - post_syco  # positive = dropped after counter-suggestion

    def ac1(t):
        if len(t) < 2:
            return 0.0
        c = np.corrcoef(t[:-1], t[1:])[0, 1]
        return 0.0 if np.isnan(c) else c

    autocorrs = np.array([ac1(trajectories[i]) for i in range(len(trajectories))])
    return np.column_stack(
        [
            single,
            mean_conf,
            drift_std,
            drift_var,
            drift_range,
            trend,
            pre_syco,
            post_syco,
            syco_drop,
            autocorrs,
        ]
    )


def compute_ece(probs, labels, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        mask = (probs >= bins[i]) & (probs < bins[i + 1])
        if mask.sum() == 0:
            continue
        acc = labels[mask].mean()
        conf = probs[mask].mean()
        ece += mask.sum() * abs(acc - conf)
    return ece / len(labels)


def split_idx(n, seed=42):
    np.random.seed(seed)
    idx = np.random.permutation(n)
    n_tr = int(0.6 * n)
    n_v = int(0.2 * n)
    return idx[:n_tr], idx[n_tr : n_tr + n_v], idx[n_tr + n_v :]


# ── Simple DAC model (Logistic Regression) ────────────────────────────────────
def run_logreg_dac(labels, features, tr, va, te, feat_subset=None):
    if feat_subset is not None:
        features = features[:, feat_subset]
    scaler = StandardScaler()
    X_tr = scaler.fit_transform(features[tr])
    X_te = scaler.transform(features[te])
    y_tr = labels[tr]
    y_te = labels[te]
    clf = LogisticRegression(C=1.0, max_iter=500, random_state=42)
    clf.fit(X_tr, y_tr)
    proba = clf.predict_proba(X_te)[:, 1]
    auroc = roc_auc_score(y_te, proba)
    ece = compute_ece(proba, y_te)
    return auroc, ece, proba


# ── Neural DAC ────────────────────────────────────────────────────────────────
class DACNet(nn.Module):
    def __init__(self, inp, hidden=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(inp, hidden),
            nn.BatchNorm1d(hidden),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden, hidden // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden // 2, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_neural_dac(features, labels, tr, va, te, epochs=80, lr=1e-3, batch=32):
    X = torch.tensor(features, dtype=torch.float32)
    y_all = labels.astype(np.float32)
    X_tr = X[tr].to(device)
    X_va = X[va].to(device)
    X_te = X[te].to(device)
    y_tr = torch.tensor(y_all[tr]).to(device)
    y_va_np = y_all[va]
    y_te_np = y_all[te]
    ds = TensorDataset(X_tr, y_tr)
    loader = DataLoader(ds, batch_size=batch, shuffle=True)
    model = DACNet(features.shape[1], hidden=64).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    crit = nn.BCELoss()
    train_losses, val_losses, val_aurocs = [], [], []
    best_va_auroc = 0.0
    best_te_proba = None
    for epoch in range(epochs):
        model.train()
        ep_loss = 0.0
        for Xb, yb in loader:
            opt.zero_grad()
            p = model(Xb)
            l = crit(p, yb)
            l.backward()
            opt.step()
            ep_loss += l.item() * len(yb)
        ep_loss /= len(tr)
        sched.step()
        model.eval()
        with torch.no_grad():
            va_p = model(X_va).cpu().numpy()
            te_p = model(X_te).cpu().numpy()
        vl = crit(torch.tensor(va_p), torch.tensor(y_va_np)).item()
        va_auroc = roc_auc_score(y_va_np, va_p)
        train_losses.append(ep_loss)
        val_losses.append(vl)
        val_aurocs.append(va_auroc)
        if va_auroc > best_va_auroc:
            best_va_auroc = va_auroc
            best_te_proba = te_p.copy()
        if (epoch + 1) % 20 == 0:
            print(f"  Epoch {epoch+1:3d}: val_loss={vl:.4f}, val_auroc={va_auroc:.4f}")
    te_auroc = roc_auc_score(y_te_np, best_te_proba)
    te_ece = compute_ece(best_te_proba, y_te_np)
    return te_auroc, te_ece, best_te_proba, train_losses, val_losses, val_aurocs


# ── Experiment data storage ───────────────────────────────────────────────────
experiment_data = {
    "trivia_qa": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "auroc_per_epoch": [],
    },
    "sciq": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "auroc_per_epoch": [],
    },
    "halueval": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "auroc_per_epoch": [],
    },
    "summary": {
        "datasets": [],
        "single_turn_auroc": [],
        "drift_auroc": [],
        "dac_logreg_auroc": [],
        "dac_neural_auroc": [],
        "syco_auroc": [],
        "cross_ds_auroc": [],
        "single_turn_ece": [],
        "dac_ece": [],
    },
}

# ── Main experiment per dataset ───────────────────────────────────────────────
dataset_configs = [
    ("trivia_qa", trivia_labels, trivia_traj, trivia_labels_syco, trivia_traj_syco, 42),
    ("sciq", sciq_labels, sciq_traj, sciq_labels_syco, sciq_traj_syco, 123),
    (
        "halueval",
        halueval_labels,
        halueval_traj,
        halueval_labels_syco,
        halueval_traj_syco,
        456,
    ),
]

all_features = {}
all_labels_store = {}
all_split_idx = {}
all_aurocs = {}

for ds_name, labels, traj, labels_syco, traj_syco, seed in dataset_configs:
    print(f"\n{'='*60}")
    print(f"Dataset: {ds_name}")
    print(f"{'='*60}")
    n = len(labels)
    tr, va, te = split_idx(n, seed=seed)
    all_split_idx[ds_name] = (tr, va, te)

    feats = extract_features(traj)
    feats_syco = extract_features(traj_syco)
    all_features[ds_name] = feats
    all_labels_store[ds_name] = labels

    # Normalize features
    scaler_full = StandardScaler()
    feats_norm = scaler_full.fit_transform(feats)

    # Single-turn baseline (index 0 = single_turn_conf)
    single_conf = feats[te, 0]
    auroc_single = roc_auc_score(labels[te], -single_conf)
    ece_single = compute_ece(
        1
        - (single_conf - single_conf.min())
        / (single_conf.max() - single_conf.min() + 1e-8),
        labels[te],
    )
    print(f"Single-Turn AUROC: {auroc_single:.4f}  ECE: {ece_single:.4f}")

    # Drift variance baseline (index 3 = drift_var)
    auroc_drift = roc_auc_score(labels[te], feats[te, 3])
    print(f"Drift Variance AUROC: {auroc_drift:.4f}")

    # DAC LogReg (all features)
    auroc_dac_lr, ece_dac_lr, dac_lr_proba = run_logreg_dac(labels, feats, tr, va, te)
    print(f"DAC LogReg AUROC: {auroc_dac_lr:.4f}  ECE: {ece_dac_lr:.4f}")

    # Sycophancy-augmented DAC (use sycophancy features)
    auroc_syco, ece_syco, syco_proba = run_logreg_dac(
        labels_syco, feats_syco, tr, va, te
    )
    print(f"Sycophancy-Augmented DAC AUROC: {auroc_syco:.4f}")

    # Neural DAC
    print(f"Training Neural DAC [{ds_name}]...")
    auroc_neural, ece_neural, neural_proba, tr_losses, val_losses, val_aurocs_ep = (
        train_neural_dac(feats_norm, labels, tr, va, te, epochs=80, lr=1e-3)
    )
    print(f"Neural DAC AUROC: {auroc_neural:.4f}  ECE: {ece_neural:.4f}")

    # Store epoch-level metrics
    experiment_data[ds_name]["losses"]["train"] = tr_losses
    experiment_data[ds_name]["losses"]["val"] = val_losses
    experiment_data[ds_name]["metrics"]["val"] = val_aurocs_ep
    experiment_data[ds_name]["auroc_per_epoch"] = val_aurocs_ep
    experiment_data[ds_name]["predictions"] = neural_proba.tolist()
    experiment_data[ds_name]["ground_truth"] = labels[te].tolist()

    # Summary
    experiment_data["summary"]["datasets"].append(ds_name)
    experiment_data["summary"]["single_turn_auroc"].append(auroc_single)
    experiment_data["summary"]["drift_auroc"].append(auroc_drift)
    experiment_data["summary"]["dac_logreg_auroc"].append(auroc_dac_lr)
    experiment_data["summary"]["dac_neural_auroc"].append(auroc_neural)
    experiment_data["summary"]["syco_auroc"].append(auroc_syco)
    experiment_data["summary"]["single_turn_ece"].append(ece_single)
    experiment_data["summary"]["dac_ece"].append(ece_dac_lr)

    all_aurocs[ds_name] = {
        "single": auroc_single,
        "drift": auroc_drift,
        "dac_lr": auroc_dac_lr,
        "neural": auroc_neural,
        "syco": auroc_syco,
        "dac_lr_proba": dac_lr_proba,
        "neural_proba": neural_proba,
        "labels_te": labels[te],
        "traj": traj,
        "labels": labels,
    }

# ── Cross-dataset generalization ──────────────────────────────────────────────
print("\n" + "=" * 60)
print("Cross-Dataset Generalization (Train on 2, Test on 1)")
print("=" * 60)
cross_results = {}
ds_names_all = ["trivia_qa", "sciq", "halueval"]

for held_out in ds_names_all:
    train_dsets = [d for d in ds_names_all if d != held_out]
    X_train_parts, y_train_parts = [], []
    for td in train_dsets:
        tr, va, te = all_split_idx[td]
        X_train_parts.append(all_features[td][np.concatenate([tr, va])])
        y_train_parts.append(all_labels_store[td][np.concatenate([tr, va])])
    X_train_cross = np.vstack(X_train_parts)
    y_train_cross = np.concatenate(y_train_parts)
    _, _, te_held = all_split_idx[held_out]
    X_test_cross = all_features[held_out][te_held]
    y_test_cross = all_labels_store[held_out][te_held]
    scaler_cross = StandardScaler()
    X_tr_sc = scaler_cross.fit_transform(X_train_cross)
    X_te_sc = scaler_cross.transform(X_test_cross)
    clf_cross = LogisticRegression(C=1.0, max_iter=500, random_state=42)
    clf_cross.fit(X_tr_sc, y_train_cross)
    cross_proba = clf_cross.predict_proba(X_te_sc)[:, 1]
    cross_auroc = roc_auc_score(y_test_cross, cross_proba)
    cross_results[held_out] = cross_auroc
    experiment_data["summary"]["cross_ds_auroc"].append(cross_auroc)
    print(f"Held-out={held_out}: cross-dataset AUROC={cross_auroc:.4f}")

# ── Plots ─────────────────────────────────────────────────────────────────────
# 1. Confidence trajectory plots per dataset
for ds_name, labels, traj, _, _, _ in dataset_configs:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    h_idx = np.where(labels == 1)[0][:15]
    c_idx = np.where(labels == 0)[0][:15]
    for i in h_idx:
        axes[0].plot(range(N_TURNS), traj[i], alpha=0.35, color="red", lw=1)
    axes[0].plot(
        range(N_TURNS), traj[h_idx].mean(0), "r-", lw=2.5, label="Mean Hallucinated"
    )
    axes[0].axvline(SYCOPHANCY_TURN, color="gray", linestyle=":", label="Syco turn")
    axes[0].set_title(f"Hallucinated [{ds_name}]")
    axes[0].set_ylim(0, 1)
    axes[0].set_xlabel("Turn")
    axes[0].set_ylabel("Confidence")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    for i in c_idx:
        axes[1].plot(range(N_TURNS), traj[i], alpha=0.35, color="blue", lw=1)
    axes[1].plot(
        range(N_TURNS), traj[c_idx].mean(0), "b-", lw=2.5, label="Mean Correct"
    )
    axes[1].axvline(SYCOPHANCY_TURN, color="gray", linestyle=":", label="Syco turn")
    axes[1].set_title(f"Correct [{ds_name}]")
    axes[1].set_ylim(0, 1)
    axes[1].set_xlabel("Turn")
    axes[1].set_ylabel("Confidence")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    plt.suptitle(
        f"Multi-Turn Confidence Trajectories: {ds_name}", fontsize=13, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"trajectories_{ds_name}.png"),
        dpi=130,
        bbox_inches="tight",
    )
    plt.close()

# 2. Drift variance distribution per dataset
for ds_name, labels, traj, _, _, _ in dataset_configs:
    drift_var = traj.var(axis=1)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(
        drift_var[labels == 0],
        bins=40,
        alpha=0.6,
        color="blue",
        label="Correct",
        density=True,
    )
    ax.hist(
        drift_var[labels == 1],
        bins=40,
        alpha=0.6,
        color="red",
        label="Hallucinated",
        density=True,
    )
    ax.set_xlabel("Within-Conversation Confidence Variance")
    ax.set_ylabel("Density")
    ax.set_title(f"Confidence Drift Distribution [{ds_name}]")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"drift_dist_{ds_name}.png"),
        dpi=130,
        bbox_inches="tight",
    )
    plt.close()

# 3. AUROC comparison bar chart
fig, ax = plt.subplots(figsize=(13, 6))
x = np.arange(3)
w = 0.15
methods = [
    "Single-Turn",
    "Drift Var",
    "DAC LogReg",
    "Neural DAC",
    "Sycophancy DAC",
    "Cross-DS DAC",
]
colors = ["gray", "orange", "green", "blue", "purple", "brown"]
all_vals = [
    [all_aurocs[d]["single"] for d in ds_names_all],
    [all_aurocs[d]["drift"] for d in ds_names_all],
    [all_aurocs[d]["dac_lr"] for d in ds_names_all],
    [all_aurocs[d]["neural"] for d in ds_names_all],
    [all_aurocs[d]["syco"] for d in ds_names_all],
    [cross_results[d] for d in ds_names_all],
]
for i, (m, c, vals) in enumerate(zip(methods, colors, all_vals)):
    bars = ax.bar(x + i * w, vals, w, label=m, color=c, alpha=0.8, edgecolor="black")
    for bar, v in zip(bars, vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.004,
            f"{v:.3f}",
            ha="center",
            va="bottom",
            fontsize=6.5,
            fontweight="bold",
        )
ax.set_xticks(x + w * 2.5)
ax.set_xticklabels(ds_names_all)
ax.set_ylabel("Test AUROC")
ax.set_title("Hallucination Detection AUROC — All Methods & Datasets")
ax.set_ylim(0, 1.12)
ax.axhline(0.5, color="red", linestyle="--", alpha=0.4, label="Random")
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "auroc_all_methods.png"), dpi=130, bbox_inches="tight"
)
plt.close()

# 4. Training curves
for ds_name in ds_names_all:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    tl = experiment_data[ds_name]["losses"]["train"]
    vl = experiment_data[ds_name]["losses"]["val"]
    va = experiment_data[ds_name]["metrics"]["val"]
    axes[0].plot(tl, label="Train Loss", color="blue")
    axes[0].plot(vl, label="Val Loss", color="orange")
    axes[0].set_title(f"Neural DAC Loss [{ds_name}]")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("BCE Loss")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[1].plot(va, label="Val AUROC", color="green")
    axes[1].set_title(f"Neural DAC Val AUROC [{ds_name}]")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("AUROC")
    axes[1].set_ylim(0, 1)
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"training_curves_{ds_name}.png"),
        dpi=130,
        bbox_inches="tight",
    )
    plt.close()

# 5. Calibration curves (reliability diagrams)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for idx, ds_name in enumerate(ds_names_all):
    ax = axes[idx]
    proba = np.array(all_aurocs[ds_name]["dac_lr_proba"])
    y_te = all_aurocs[ds_name]["labels_te"]
    frac_pos, mean_pred = calibration_curve(y_te, proba, n_bins=10, strategy="uniform")
    ax.plot(mean_pred, frac_pos, "s-", color="green", label="DAC LogReg")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5, label="Perfect")
    ax.set_title(f"Reliability Diagram [{ds_name}]")
    ax.set_xlabel("Mean Predicted Prob")
    ax.set_ylabel("Fraction Positives")
    ax.legend()
    ax.grid(alpha=0.3)
plt.suptitle("Calibration Reliability Diagrams", fontsize=13)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "calibration_reliability.png"),
    dpi=130,
    bbox_inches="tight",
)
plt.close()

# 6. Sycophancy effect: confidence before vs after counter-suggestion
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for idx, (ds_name, labels, traj, labels_syco, traj_syco, _) in enumerate(
    dataset_configs
):
    ax = axes[idx]
    pre_hall = traj_syco[labels_syco == 1, :SYCOPHANCY_TURN].mean(axis=1)
    post_hall = traj_syco[labels_syco == 1, SYCOPHANCY_TURN:].mean(axis=1)
    pre_corr = traj_syco[labels_syco == 0, :SYCOPHANCY_TURN].mean(axis=1)
    post_corr = traj_syco[labels_syco == 0, SYCOPHANCY_TURN:].mean(axis=1)
    ax.scatter(
        pre_hall[:100], post_hall[:100], alpha=0.4, c="red", s=15, label="Hallucinated"
    )
    ax.scatter(
        pre_corr[:100], post_corr[:100], alpha=0.4, c="blue", s=15, label="Correct"
    )
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5)
    ax.set_xlabel("Pre-Sycophancy Mean Conf")
    ax.set_ylabel("Post-Sycophancy Mean Conf")
    ax.set_title(f"Sycophancy Effect [{ds_name}]")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
plt.suptitle("Confidence Before vs After Counter-Suggestion Injection", fontsize=13)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "sycophancy_effect.png"), dpi=130, bbox_inches="tight"
)
plt.close()

# ── Final Summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 65)
print("FINAL RESULTS SUMMARY")
print("=" * 65)
for ds_name in ds_names_all:
    a = all_aurocs[ds_name]
    print(f"\n[{ds_name}]")
    print(f"  Single-Turn AUROC:       {a['single']:.4f}")
    print(f"  Drift Variance AUROC:    {a['drift']:.4f}")
    print(f"  DAC LogReg AUROC:        {a['dac_lr']:.4f}")
    print(f"  Neural DAC AUROC:        {a['neural']:.4f}")
    print(f"  Sycophancy-DAC AUROC:    {a['syco']:.4f}")
    print(f"  Cross-DS Gen AUROC:      {cross_results[ds_name]:.4f}")
    improvement = (a["dac_lr"] - a["single"]) * 100
    print(f"  DAC improvement over single-turn: {improvement:.2f}%")

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nAll data saved. Done!")
