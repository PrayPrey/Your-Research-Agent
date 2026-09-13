import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# ─── Experiment data structure ─────────────────────────────────────────────────
experiment_data = {}
for ds in ["biography_synthetic", "fever_synthetic", "squad_synthetic"]:
    for nl in [1, 2]:
        key = f"num_layers_{nl}"
        if key not in experiment_data:
            experiment_data[key] = {}
        experiment_data[key][ds] = {
            "metrics": {
                "CHAR_independent": [],
                "CHAR_cascade": [],
                "AUROC_independent": [],
                "AUROC_cascade": [],
                "CW_AUROC_independent": [],
                "CW_AUROC_cascade": [],
            },
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
            "cascade_scores": [],
            "independent_scores": [],
            "epochs": [],
        }


# ─── Synthetic data generation ────────────────────────────────────────────────
def generate_synthetic_documents(
    n_docs=300,
    max_claims=10,
    cascade_strength=0.7,
    base_error_range=(0.05, 0.25),
    seed_offset=0,
):
    all_docs = []
    for doc_id in range(n_docs):
        random.seed(42 + doc_id + seed_offset)
        np.random.seed(42 + doc_id + seed_offset)
        n_claims = random.randint(5, max_claims)
        claims = []
        base_error_prob = random.uniform(*base_error_range)
        cascade_intensity = 0.0
        for pos in range(n_claims):
            self_uncertainty = np.random.beta(2, 5)
            if pos == 0:
                error_prob = base_error_prob + self_uncertainty * 0.3
            else:
                upstream_influence = cascade_intensity * cascade_strength
                error_prob = min(
                    0.95, base_error_prob + self_uncertainty * 0.3 + upstream_influence
                )
            is_hallucinated = int(np.random.rand() < error_prob)
            if is_hallucinated:
                cascade_intensity = min(1.0, cascade_intensity + 0.3)
            else:
                cascade_intensity = max(0.0, cascade_intensity - 0.1)
            if is_hallucinated:
                observed_uncertainty = np.clip(
                    self_uncertainty + np.random.normal(0.3, 0.1), 0, 1
                )
            else:
                observed_uncertainty = np.clip(
                    self_uncertainty + np.random.normal(-0.05, 0.1), 0, 1
                )
            claims.append(
                {
                    "doc_id": doc_id,
                    "position": pos,
                    "self_uncertainty": float(observed_uncertainty),
                    "is_hallucinated": is_hallucinated,
                    "cascade_intensity_gt": float(cascade_intensity),
                    "n_claims": n_claims,
                }
            )
        all_docs.append(claims)
    return all_docs


def generate_fever_docs(n_docs=300, max_claims=8, cascade_strength=0.65):
    """Simulate FEVER-style claim verification docs with slightly different distribution."""
    return generate_synthetic_documents(
        n_docs=n_docs,
        max_claims=max_claims,
        cascade_strength=cascade_strength,
        base_error_range=(0.10, 0.35),
        seed_offset=10000,
    )


def generate_squad_docs(n_docs=300, max_claims=6, cascade_strength=0.55):
    """Simulate SQuAD-style QA docs with lower cascade strength (shorter contexts)."""
    return generate_synthetic_documents(
        n_docs=n_docs,
        max_claims=max_claims,
        cascade_strength=cascade_strength,
        base_error_range=(0.03, 0.20),
        seed_offset=20000,
    )


def compute_cascade_uncertainty(doc_claims, alpha=0.4):
    cascade_scores = []
    for i, claim in enumerate(doc_claims):
        if i == 0:
            score = claim["self_uncertainty"]
        else:
            upstream_mean = np.mean(cascade_scores)
            score = (1 - alpha) * claim["self_uncertainty"] + alpha * upstream_mean
        cascade_scores.append(score)
    return cascade_scores


def compute_cw_auroc(docs, uncertainty_scores_flat, labels_flat):
    """Cascade-Weighted AUROC: weight each claim by depth * mean_predecessor_uncertainty."""
    score_idx = 0
    weights = []
    for doc in docs:
        n = len(doc)
        doc_scores = uncertainty_scores_flat[score_idx : score_idx + n]
        for i in range(n):
            depth = i  # upstream dependency depth
            if i == 0:
                mean_pred_unc = 0.0
            else:
                mean_pred_unc = float(np.mean(doc_scores[:i]))
            w = (depth / max(n - 1, 1)) * (mean_pred_unc + 1e-8)
            weights.append(w)
        score_idx += n
    weights = np.array(weights, dtype=np.float64)
    weights = weights / (weights.sum() + 1e-10) * len(weights)  # normalize
    # Weighted AUROC via weighted ranking
    try:
        # Use sklearn with sample_weight
        cw_auroc = roc_auc_score(
            labels_flat, uncertainty_scores_flat, sample_weight=weights + 1e-8
        )
    except Exception:
        cw_auroc = 0.5
    return float(cw_auroc)


# ─── Model ────────────────────────────────────────────────────────────────────
class CascadePropagationNet(nn.Module):
    def __init__(self, input_dim=2, hidden_dim=64, output_dim=1, num_layers=1):
        super().__init__()
        self.gru = nn.GRU(
            input_dim,
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2 if num_layers > 1 else 0.0,
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, output_dim),
            nn.Sigmoid(),
        )

    def forward(self, x):
        out, _ = self.gru(x)
        return self.fc(out).squeeze(-1)


# ─── CHAR metric ──────────────────────────────────────────────────────────────
def compute_CHAR(docs, uncertainty_scores_flat, threshold_quantile=0.75):
    score_idx = 0
    high_thresh = np.quantile(uncertainty_scores_flat, threshold_quantile)
    downstream_errors_after_high = []
    downstream_errors_after_low = []
    for doc in docs:
        doc_scores = uncertainty_scores_flat[score_idx : score_idx + len(doc)]
        score_idx += len(doc)
        for i in range(len(doc) - 1):
            pivot_score = doc_scores[i]
            downstream_claims = doc[i + 1 :]
            downstream_error_rate = (
                np.mean([c["is_hallucinated"] for c in downstream_claims])
                if downstream_claims
                else 0
            )
            if pivot_score >= high_thresh:
                downstream_errors_after_high.append(downstream_error_rate)
            else:
                downstream_errors_after_low.append(downstream_error_rate)
    if not downstream_errors_after_low or not downstream_errors_after_high:
        return 1.0
    return np.mean(downstream_errors_after_high) / (
        np.mean(downstream_errors_after_low) + 1e-8
    )


# ─── Data preparation helper ──────────────────────────────────────────────────
MAX_LEN = 10
INPUT_DIM = 2


def pad_doc(claims, max_len=MAX_LEN):
    feats, labels, mask = [], [], []
    for c in claims[:max_len]:
        feats.append([c["self_uncertainty"], c["position"] / max_len])
        labels.append(c["is_hallucinated"])
        mask.append(1)
    while len(feats) < max_len:
        feats.append([0.0, 0.0])
        labels.append(0)
        mask.append(0)
    return feats, labels, mask


def docs_to_tensors(docs):
    X_all, Y_all, M_all = [], [], []
    for doc in docs:
        f, l, m = pad_doc(doc)
        X_all.append(f)
        Y_all.append(l)
        M_all.append(m)
    return (
        np.array(X_all, dtype=np.float32),
        np.array(Y_all, dtype=np.float32),
        np.array(M_all, dtype=np.float32),
    )


# ─── Training & Evaluation ────────────────────────────────────────────────────
EPOCHS = 50
NUM_LAYERS_LIST = [1, 2]
HIDDEN_DIM = 64
LR = 5e-4
BATCH_SIZE = 16

DATASETS = {
    "biography_synthetic": generate_synthetic_documents(
        n_docs=300, max_claims=10, cascade_strength=0.7
    ),
    "fever_synthetic": generate_fever_docs(
        n_docs=300, max_claims=8, cascade_strength=0.65
    ),
    "squad_synthetic": generate_squad_docs(
        n_docs=300, max_claims=6, cascade_strength=0.55
    ),
}

all_test_results = {nl: {} for nl in NUM_LAYERS_LIST}
epochs_arr = np.arange(1, EPOCHS + 1)

for ds_name, all_docs in DATASETS.items():
    print(f'\n{"#"*60}')
    print(f"Dataset: {ds_name}")
    print(f'{"#"*60}')

    n = len(all_docs)
    n_train = int(0.6 * n)
    n_val = int(0.2 * n)

    train_docs = all_docs[:n_train]
    val_docs = all_docs[n_train : n_train + n_val]
    test_docs = all_docs[n_train + n_val :]

    X_all, Y_all, M_all = docs_to_tensors(all_docs)
    X_train_np = X_all[:n_train]
    X_val_np = X_all[n_train : n_train + n_val]
    X_test_np = X_all[n_train + n_val :]

    X_train = torch.tensor(X_train_np).to(device)
    Y_train = torch.tensor(Y_all[:n_train]).to(device)
    M_train = torch.tensor(M_all[:n_train]).to(device)
    X_val = torch.tensor(X_val_np).to(device)
    Y_val = torch.tensor(Y_all[n_train : n_train + n_val]).to(device)
    M_val = torch.tensor(M_all[n_train : n_train + n_val]).to(device)
    X_test = torch.tensor(X_test_np).to(device)
    Y_test = torch.tensor(Y_all[n_train + n_val :]).to(device)
    M_test = torch.tensor(M_all[n_train + n_val :]).to(device)

    train_loader = DataLoader(
        TensorDataset(X_train, Y_train, M_train), batch_size=BATCH_SIZE, shuffle=True
    )
    val_loader = DataLoader(
        TensorDataset(X_val, Y_val, M_val), batch_size=BATCH_SIZE, shuffle=False
    )

    # Precompute baseline scores
    indep_scores_val = [c["self_uncertainty"] for doc in val_docs for c in doc]
    indep_scores_test = [c["self_uncertainty"] for doc in test_docs for c in doc]
    cascade_cf_scores_val = [
        s for doc in val_docs for s in compute_cascade_uncertainty(doc, alpha=0.4)
    ]
    cascade_cf_scores_test = [
        s for doc in test_docs for s in compute_cascade_uncertainty(doc, alpha=0.4)
    ]
    labels_val = np.array([c["is_hallucinated"] for doc in val_docs for c in doc])
    labels_test = np.array([c["is_hallucinated"] for doc in test_docs for c in doc])

    CHAR_indep_val = compute_CHAR(val_docs, np.array(indep_scores_val))
    CHAR_cascade_val = compute_CHAR(val_docs, np.array(cascade_cf_scores_val))

    for num_layers in NUM_LAYERS_LIST:
        exp_key = f"num_layers_{num_layers}"
        print(f'\n{"="*50}')
        print(f"num_layers={num_layers}  |  dataset={ds_name}")
        print(f'{"="*50}')

        torch.manual_seed(42)
        model = CascadePropagationNet(
            input_dim=INPUT_DIM, hidden_dim=HIDDEN_DIM, num_layers=num_layers
        ).to(device)
        optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
        criterion = nn.BCELoss(reduction="none")

        for epoch in range(1, EPOCHS + 1):
            # ── train ──
            model.train()
            train_loss, n_steps = 0.0, 0
            for bX, bY, bM in train_loader:
                bX, bY, bM = bX.to(device), bY.to(device), bM.to(device)
                optimizer.zero_grad()
                pred = model(bX)
                loss = (criterion(pred, bY) * bM).sum() / (bM.sum() + 1e-8)
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                train_loss += loss.item()
                n_steps += 1
            scheduler.step()
            train_loss /= n_steps

            # ── val ──
            model.eval()
            val_loss, n_vsteps = 0.0, 0
            val_preds_all, val_labels_all, val_masks_all = [], [], []
            with torch.no_grad():
                for bX, bY, bM in val_loader:
                    bX, bY, bM = bX.to(device), bY.to(device), bM.to(device)
                    pred = model(bX)
                    loss = (criterion(pred, bY) * bM).sum() / (bM.sum() + 1e-8)
                    val_loss += loss.item()
                    n_vsteps += 1
                    val_preds_all.append(pred.cpu().numpy())
                    val_labels_all.append(bY.cpu().numpy())
                    val_masks_all.append(bM.cpu().numpy())
            val_loss /= n_vsteps

            vp = np.concatenate([p.flatten() for p in val_preds_all])
            vl = np.concatenate([l.flatten() for l in val_labels_all])
            vm = np.concatenate([m.flatten() for m in val_masks_all]).astype(bool)
            vp_m, vl_m = vp[vm], vl[vm]
            vself = X_val_np[:, :, 0].flatten()[vm]

            try:
                auroc_cascade = roc_auc_score(vl_m, vp_m)
            except:
                auroc_cascade = 0.5
            try:
                auroc_indep = roc_auc_score(vl_m, vself)
            except:
                auroc_indep = 0.5

            # CW-AUROC on val
            cw_auroc_indep = compute_cw_auroc(
                val_docs, np.array(indep_scores_val), labels_val
            )
            # rebuild neural scores for val
            val_neural_scores = []
            for i, doc in enumerate(val_docs):
                nr = len(doc)
                val_neural_scores.extend(
                    vp.reshape(len(val_docs), MAX_LEN)[i, :nr].tolist()
                )
            cw_auroc_cascade = compute_cw_auroc(
                val_docs, np.array(val_neural_scores), labels_val
            )

            ed = experiment_data[exp_key][ds_name]
            ed["metrics"]["CHAR_independent"].append(CHAR_indep_val)
            ed["metrics"]["CHAR_cascade"].append(CHAR_cascade_val)
            ed["metrics"]["AUROC_independent"].append(float(auroc_indep))
            ed["metrics"]["AUROC_cascade"].append(float(auroc_cascade))
            ed["metrics"]["CW_AUROC_independent"].append(float(cw_auroc_indep))
            ed["metrics"]["CW_AUROC_cascade"].append(float(cw_auroc_cascade))
            ed["losses"]["train"].append(train_loss)
            ed["losses"]["val"].append(val_loss)
            ed["epochs"].append(epoch)

            if epoch % 10 == 0 or epoch == 1:
                print(
                    f"Epoch {epoch:3d}: val_loss={val_loss:.4f} | AUROC_indep={auroc_indep:.4f} | "
                    f"AUROC_cascade={auroc_cascade:.4f} | CW_AUROC={cw_auroc_cascade:.4f} | "
                    f"CHAR_indep={CHAR_indep_val:.4f} | CHAR_cascade={CHAR_cascade_val:.4f}"
                )

        # ── test ──
        print(
            f"\n=== Final Test Evaluation (num_layers={num_layers}, ds={ds_name}) ==="
        )
        model.eval()
        with torch.no_grad():
            test_preds = model(X_test).cpu().numpy()

        tm = M_test.cpu().numpy().flatten().astype(bool)
        tl = Y_test.cpu().numpy().flatten()[tm]
        tp = test_preds.flatten()[tm]
        tself = X_test_np[:, :, 0].flatten()[tm]

        try:
            auroc_cascade_test = roc_auc_score(tl, tp)
        except:
            auroc_cascade_test = 0.5
        try:
            auroc_indep_test = roc_auc_score(tl, tself)
        except:
            auroc_indep_test = 0.5

        neural_scores_test = []
        for i, doc in enumerate(test_docs):
            nr = len(doc)
            neural_scores_test.extend(test_preds[i, :nr].tolist())

        CHAR_indep_test = compute_CHAR(test_docs, np.array(indep_scores_test))
        CHAR_cascade_test = compute_CHAR(test_docs, np.array(cascade_cf_scores_test))
        CHAR_neural_test = compute_CHAR(test_docs, np.array(neural_scores_test))

        cw_auroc_indep_test = compute_cw_auroc(
            test_docs, np.array(indep_scores_test), labels_test
        )
        cw_auroc_cascade_test = compute_cw_auroc(
            test_docs, np.array(neural_scores_test), labels_test
        )

        print(f"Test AUROC (Independent):  {auroc_indep_test:.4f}")
        print(f"Test AUROC (Cascade GRU):  {auroc_cascade_test:.4f}")
        print(f"Test CW-AUROC (Indep):     {cw_auroc_indep_test:.4f}")
        print(f"Test CW-AUROC (Cascade):   {cw_auroc_cascade_test:.4f}")
        print(f"Test CHAR  (Independent):  {CHAR_indep_test:.4f}")
        print(f"Test CHAR  (Cascade CF):   {CHAR_cascade_test:.4f}")
        print(f"Test CHAR  (Cascade GRU):  {CHAR_neural_test:.4f}")

        ed = experiment_data[exp_key][ds_name]
        ed["test_results"] = {
            "AUROC_independent": float(auroc_indep_test),
            "AUROC_cascade_gru": float(auroc_cascade_test),
            "CW_AUROC_independent": float(cw_auroc_indep_test),
            "CW_AUROC_cascade_gru": float(cw_auroc_cascade_test),
            "CHAR_independent": float(CHAR_indep_test),
            "CHAR_cascade_cf": float(CHAR_cascade_test),
            "CHAR_cascade_gru": float(CHAR_neural_test),
        }
        ed["predictions"] = tp.tolist()
        ed["ground_truth"] = tl.tolist()
        ed["cascade_scores"] = neural_scores_test
        ed["independent_scores"] = indep_scores_test

        if ds_name not in all_test_results[num_layers]:
            all_test_results[num_layers][ds_name] = {}
        all_test_results[num_layers][ds_name] = {
            "auroc_indep": auroc_indep_test,
            "auroc_cascade": auroc_cascade_test,
            "cw_auroc_indep": cw_auroc_indep_test,
            "cw_auroc_cascade": cw_auroc_cascade_test,
            "CHAR_indep": CHAR_indep_test,
            "CHAR_cascade_cf": CHAR_cascade_test,
            "CHAR_neural": CHAR_neural_test,
            "train_losses": ed["losses"]["train"],
            "val_losses": ed["losses"]["val"],
            "auroc_cascade_epochs": ed["metrics"]["AUROC_cascade"],
            "cw_auroc_epochs": ed["metrics"]["CW_AUROC_cascade"],
        }

# ─── Visualizations ───────────────────────────────────────────────────────────
colors_map = {1: "steelblue", 2: "darkorange"}

for ds_name in DATASETS.keys():
    # Training curves
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for nl in NUM_LAYERS_LIST:
        r = all_test_results[nl][ds_name]
        axes[0].plot(
            epochs_arr,
            r["train_losses"],
            label=f"Train (layers={nl})",
            color=colors_map[nl],
            linestyle="-",
        )
        axes[0].plot(
            epochs_arr,
            r["val_losses"],
            label=f"Val (layers={nl})",
            color=colors_map[nl],
            linestyle="--",
        )
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("BCE Loss")
    axes[0].set_title(f"Loss [{ds_name}]")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    for nl in NUM_LAYERS_LIST:
        r = all_test_results[nl][ds_name]
        axes[1].plot(
            epochs_arr,
            r["auroc_cascade_epochs"],
            label=f"AUROC Cascade (layers={nl})",
            color=colors_map[nl],
        )
        axes[1].plot(
            epochs_arr,
            r["cw_auroc_epochs"],
            label=f"CW-AUROC (layers={nl})",
            color=colors_map[nl],
            linestyle="--",
        )
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("AUROC")
    axes[1].set_title(f"Val AUROC & CW-AUROC [{ds_name}]")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    x = np.arange(3)
    width = 0.35
    methods_labels = ["Independent", "Cascade CF", "Cascade GRU"]
    for i, nl in enumerate(NUM_LAYERS_LIST):
        r = all_test_results[nl][ds_name]
        vals = [r["CHAR_indep"], r["CHAR_cascade_cf"], r["CHAR_neural"]]
        offset = (i - 0.5) * width
        axes[2].bar(
            x + offset,
            vals,
            width,
            label=f"layers={nl}",
            color=colors_map[nl],
            alpha=0.8,
        )
    axes[2].axhline(y=1.0, color="red", linestyle="--", linewidth=2, label="Baseline")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(methods_labels)
    axes[2].set_ylabel("CHAR")
    axes[2].set_title(f"Test CHAR [{ds_name}]")
    axes[2].legend()
    axes[2].grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, f"{ds_name}_training_curves.png"), dpi=120)
    plt.close()

    # Cascade analysis + AUROC bar
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    sample_doc = DATASETS[ds_name][0]
    sample_cascade = compute_cascade_uncertainty(sample_doc, alpha=0.4)
    positions = [c["position"] for c in sample_doc]
    self_unc = [c["self_uncertainty"] for c in sample_doc]
    hallucinated = [c["is_hallucinated"] for c in sample_doc]
    bar_colors = ["#d62728" if h else "#2ca02c" for h in hallucinated]
    axes[0].bar(positions, self_unc, color=bar_colors, alpha=0.7)
    axes[0].plot(positions, sample_cascade, "b-o", linewidth=2, label="Cascade Score")
    axes[0].set_xlabel("Claim Position")
    axes[0].set_ylabel("Uncertainty Score")
    axes[0].set_title(f"Uncertainty Propagation [{ds_name}]")
    red_patch = mpatches.Patch(color="#d62728", label="Hallucinated")
    green_patch = mpatches.Patch(color="#2ca02c", label="Correct")
    axes[0].legend(
        handles=[red_patch, green_patch, axes[0].get_legend_handles_labels()[0][0]]
    )
    axes[0].grid(True, alpha=0.3)

    nl_labels = [f"layers={nl}" for nl in NUM_LAYERS_LIST]
    auroc_vals = [
        all_test_results[nl][ds_name]["auroc_cascade"] for nl in NUM_LAYERS_LIST
    ]
    cw_vals = [
        all_test_results[nl][ds_name]["cw_auroc_cascade"] for nl in NUM_LAYERS_LIST
    ]
    x2 = np.arange(len(NUM_LAYERS_LIST))
    w = 0.35
    b1 = axes[1].bar(
        x2 - w / 2, auroc_vals, w, label="AUROC", color="steelblue", alpha=0.8
    )
    b2 = axes[1].bar(
        x2 + w / 2, cw_vals, w, label="CW-AUROC", color="darkorange", alpha=0.8
    )
    axes[1].set_xticks(x2)
    axes[1].set_xticklabels(nl_labels)
    axes[1].set_ylabel("Score")
    axes[1].set_title(f"Test AUROC & CW-AUROC [{ds_name}]")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis="y")
    for bar, val in zip(b1, auroc_vals):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.3f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    for bar, val in zip(b2, cw_vals):
        axes[1].text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{val:.3f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    plt.tight_layout()
    plt.savefig(os.path.join(working_dir, f"{ds_name}_cascade_analysis.png"), dpi=120)
    plt.close()

    # Score distributions
    test_docs = DATASETS[ds_name][
        int(0.6 * len(DATASETS[ds_name])) + int(0.2 * len(DATASETS[ds_name])) :
    ]
    n_train_ = int(0.6 * len(DATASETS[ds_name]))
    n_val_ = int(0.2 * len(DATASETS[ds_name]))
    test_docs_ = DATASETS[ds_name][n_train_ + n_val_ :]
    indep_scores_test_ = np.array(
        [c["self_uncertainty"] for doc in test_docs_ for c in doc]
    )
    labels_test_ = np.array([c["is_hallucinated"] for doc in test_docs_ for c in doc])
    cascade_cf_test_ = np.array(
        [s for doc in test_docs_ for s in compute_cascade_uncertainty(doc, 0.4)]
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for arr, title, ax in zip(
        [indep_scores_test_, cascade_cf_test_], ["Independent", "Cascade CF"], axes
    ):
        ax.hist(
            arr[labels_test_ == 0],
            bins=30,
            alpha=0.6,
            label="Correct",
            color="green",
            density=True,
        )
        ax.hist(
            arr[labels_test_ == 1],
            bins=30,
            alpha=0.6,
            label="Hallucinated",
            color="red",
            density=True,
        )
        ax.set_xlabel("Uncertainty Score")
        ax.set_ylabel("Density")
        ax.set_title(f"{title} Score Dist [{ds_name}]")
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_score_distributions.png"), dpi=120
    )
    plt.close()

# ─── Cross-dataset comparison ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
ds_labels = list(DATASETS.keys())
x = np.arange(len(ds_labels))
w = 0.35

for ax_idx, (metric_key, title) in enumerate(
    [
        ("auroc_cascade", "Test AUROC (Cascade GRU)"),
        ("cw_auroc_cascade", "Test CW-AUROC (Cascade GRU)"),
    ]
):
    for i, nl in enumerate(NUM_LAYERS_LIST):
        vals = [all_test_results[nl][ds][metric_key] for ds in ds_labels]
        offset = (i - 0.5) * w
        bars = axes[ax_idx].bar(
            x + offset, vals, w, label=f"layers={nl}", color=colors_map[nl], alpha=0.8
        )
        for bar, val in zip(bars, vals):
            axes[ax_idx].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.003,
                f"{val:.3f}",
                ha="center",
                fontsize=8,
                fontweight="bold",
            )
    axes[ax_idx].set_xticks(x)
    axes[ax_idx].set_xticklabels(ds_labels, rotation=10)
    axes[ax_idx].set_ylabel("Score")
    axes[ax_idx].set_title(title)
    axes[ax_idx].legend()
    axes[ax_idx].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "cross_dataset_comparison.png"), dpi=120)
plt.close()

# ─── Save all experiment data ─────────────────────────────────────────────────
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nAll results saved to {working_dir}")

# ─── Final summary ────────────────────────────────────────────────────────────
print("\n=== Final Summary ===")
for ds_name in DATASETS.keys():
    print(f"\nDataset: {ds_name}")
    for nl in NUM_LAYERS_LIST:
        r = all_test_results[nl][ds_name]
        print(
            f'  num_layers={nl}: AUROC_indep={r["auroc_indep"]:.4f} | AUROC_cascade={r["auroc_cascade"]:.4f} | '
            f'CW_AUROC_indep={r["cw_auroc_indep"]:.4f} | CW_AUROC_cascade={r["cw_auroc_cascade"]:.4f} | '
            f'CHAR_indep={r["CHAR_indep"]:.4f} | CHAR_cascade_cf={r["CHAR_cascade_cf"]:.4f} | '
            f'CHAR_gru={r["CHAR_neural"]:.4f}'
        )
print("\nCHAR > 1.0 confirms cascade hypothesis.")
