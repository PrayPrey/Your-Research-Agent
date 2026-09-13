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
from collections import defaultdict
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ─── Reproducibility ──────────────────────────────────────────────────────────
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# ─── Experiment data store ────────────────────────────────────────────────────
experiment_data = {
    "biography_synthetic": {
        "metrics": {
            "CHAR_independent": [],
            "CHAR_cascade": [],
            "AUROC_independent": [],
            "AUROC_cascade": [],
        },
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "cascade_scores": [],
        "independent_scores": [],
        "epochs": [],
    }
}


# ─── Synthetic Data Generation ────────────────────────────────────────────────
def generate_synthetic_documents(n_docs=200, max_claims=10, cascade_strength=0.7):
    """
    Generate synthetic documents with cascade hallucination structure.
    Each document has `max_claims` atomic claims.
    Early hallucinated claims propagate corruption downstream.
    Returns:
        claims_list: list of dicts with uncertainty_score, is_hallucinated, position, doc_id
    """
    all_docs = []
    for doc_id in range(n_docs):
        n_claims = random.randint(5, max_claims)
        claims = []
        # Base error probability for this doc
        base_error_prob = random.uniform(0.05, 0.25)

        cascade_active = False
        cascade_intensity = 0.0

        for pos in range(n_claims):
            # Self uncertainty score (raw): mix of noise + position effect
            self_uncertainty = np.random.beta(2, 5)  # baseline: low uncertainty

            if pos == 0:
                # First claim: no upstream influence
                error_prob = base_error_prob + self_uncertainty * 0.3
            else:
                # Cascade: if upstream was uncertain/hallucinated, inflate error prob
                upstream_influence = cascade_intensity * cascade_strength
                error_prob = min(
                    0.95, base_error_prob + self_uncertainty * 0.3 + upstream_influence
                )

            is_hallucinated = int(np.random.rand() < error_prob)

            # Update cascade state
            if is_hallucinated:
                cascade_active = True
                cascade_intensity = min(1.0, cascade_intensity + 0.3)
            else:
                cascade_intensity = max(0.0, cascade_intensity - 0.1)

            # Observed uncertainty score (what a UQ method would output)
            # Hallucinated claims tend to have higher uncertainty
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


# ─── Cascade Uncertainty Propagation ─────────────────────────────────────────
def compute_cascade_uncertainty(doc_claims, alpha=0.4):
    """
    Forward-propagate uncertainty through claims in a document.
    cascade_score[i] = (1-alpha)*self_uncertainty[i] + alpha*mean(cascade_scores[:i])
    Returns list of cascade-aware uncertainty scores.
    """
    cascade_scores = []
    for i, claim in enumerate(doc_claims):
        if i == 0:
            score = claim["self_uncertainty"]
        else:
            upstream_mean = np.mean(cascade_scores)
            score = (1 - alpha) * claim["self_uncertainty"] + alpha * upstream_mean
        cascade_scores.append(score)
    return cascade_scores


# ─── Neural Propagation Model ─────────────────────────────────────────────────
class CascadePropagationNet(nn.Module):
    """
    A small GRU-based model that learns to propagate uncertainty through claims.
    Input: sequence of [self_uncertainty, position_ratio] per claim
    Output: cascade-aware uncertainty score per claim
    """

    def __init__(self, input_dim=2, hidden_dim=32, output_dim=1):
        super().__init__()
        self.gru = nn.GRU(input_dim, hidden_dim, num_layers=1, batch_first=True)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 16),
            nn.ReLU(),
            nn.Linear(16, output_dim),
            nn.Sigmoid(),
        )

    def forward(self, x):
        # x: (batch, seq_len, input_dim)
        out, _ = self.gru(x)  # out: (batch, seq_len, hidden_dim)
        scores = self.fc(out)  # (batch, seq_len, 1)
        return scores.squeeze(-1)  # (batch, seq_len)


# ─── Prepare Data ─────────────────────────────────────────────────────────────
print("Generating synthetic documents...")
all_docs = generate_synthetic_documents(n_docs=300, max_claims=10, cascade_strength=0.7)

MAX_LEN = 10
INPUT_DIM = 2


def pad_doc(claims, max_len=MAX_LEN):
    """Pad/truncate document claims to max_len."""
    feats, labels, mask = [], [], []
    for i, c in enumerate(claims[:max_len]):
        feats.append([c["self_uncertainty"], c["position"] / max_len])
        labels.append(c["is_hallucinated"])
        mask.append(1)
    # Pad
    while len(feats) < max_len:
        feats.append([0.0, 0.0])
        labels.append(0)
        mask.append(0)
    return feats, labels, mask


X_all, Y_all, M_all = [], [], []
for doc in all_docs:
    f, l, m = pad_doc(doc)
    X_all.append(f)
    Y_all.append(l)
    M_all.append(m)

X_all = np.array(X_all, dtype=np.float32)
Y_all = np.array(Y_all, dtype=np.float32)
M_all = np.array(M_all, dtype=np.float32)

# Train/val/test split
n = len(all_docs)
n_train = int(0.6 * n)
n_val = int(0.2 * n)

X_train = torch.tensor(X_all[:n_train]).to(device)
Y_train = torch.tensor(Y_all[:n_train]).to(device)
M_train = torch.tensor(M_all[:n_train]).to(device)

X_val = torch.tensor(X_all[n_train : n_train + n_val]).to(device)
Y_val = torch.tensor(Y_all[n_train : n_train + n_val]).to(device)
M_val = torch.tensor(M_all[n_train : n_train + n_val]).to(device)

X_test = torch.tensor(X_all[n_train + n_val :]).to(device)
Y_test = torch.tensor(Y_all[n_train + n_val :]).to(device)
M_test = torch.tensor(M_all[n_train + n_val :]).to(device)

train_dataset = TensorDataset(X_train, Y_train, M_train)
val_dataset = TensorDataset(X_val, Y_val, M_val)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

print(
    f"Train docs: {n_train}, Val docs: {n_val}, Test docs: {len(all_docs)-n_train-n_val}"
)

# ─── Model, Loss, Optimizer ───────────────────────────────────────────────────
model = CascadePropagationNet(input_dim=INPUT_DIM, hidden_dim=32).to(device)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.BCELoss(reduction="none")


# ─── CHAR Metric ──────────────────────────────────────────────────────────────
def compute_CHAR(docs, uncertainty_scores_flat, threshold_quantile=0.75):
    """
    Compute Cascade Hallucination Amplification Rate.
    uncertainty_scores_flat: flat list of uncertainty scores per claim (aligned with docs).
    Returns CHAR value.
    """
    score_idx = 0
    high_thresh = np.quantile(uncertainty_scores_flat, threshold_quantile)

    downstream_errors_after_high = []
    downstream_errors_after_low = []

    for doc in docs:
        doc_scores = uncertainty_scores_flat[score_idx : score_idx + len(doc)]
        score_idx += len(doc)

        for i in range(len(doc) - 1):  # pivot at i, downstream is i+1..end
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

    avg_high = np.mean(downstream_errors_after_high)
    avg_low = np.mean(downstream_errors_after_low)

    CHAR = avg_high / (avg_low + 1e-8)
    return CHAR


# ─── Training Loop ────────────────────────────────────────────────────────────
EPOCHS = 30
print("\nStarting training...")

for epoch in range(1, EPOCHS + 1):
    model.train()
    train_loss = 0.0
    n_train_steps = 0

    for batch_X, batch_Y, batch_M in train_loader:
        batch_X = batch_X.to(device)
        batch_Y = batch_Y.to(device)
        batch_M = batch_M.to(device)

        optimizer.zero_grad()
        pred = model(batch_X)  # (batch, seq_len)
        loss = criterion(pred, batch_Y)  # (batch, seq_len)
        # Mask padding
        loss = (loss * batch_M).sum() / (batch_M.sum() + 1e-8)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
        n_train_steps += 1

    train_loss /= n_train_steps

    # Validation
    model.eval()
    val_loss = 0.0
    n_val_steps = 0
    val_preds_all = []
    val_labels_all = []
    val_masks_all = []

    with torch.no_grad():
        for batch_X, batch_Y, batch_M in val_loader:
            batch_X = batch_X.to(device)
            batch_Y = batch_Y.to(device)
            batch_M = batch_M.to(device)

            pred = model(batch_X)
            loss = criterion(pred, batch_Y)
            loss = (loss * batch_M).sum() / (batch_M.sum() + 1e-8)
            val_loss += loss.item()
            n_val_steps += 1

            val_preds_all.append(pred.cpu().numpy())
            val_labels_all.append(batch_Y.cpu().numpy())
            val_masks_all.append(batch_M.cpu().numpy())

    val_loss /= n_val_steps

    # Flatten for metrics (only non-padded)
    val_preds_flat = np.concatenate([p.flatten() for p in val_preds_all])
    val_labels_flat = np.concatenate([l.flatten() for l in val_labels_all])
    val_masks_flat = np.concatenate([m.flatten() for m in val_masks_all])

    mask_bool = val_masks_flat.astype(bool)
    val_preds_masked = val_preds_flat[mask_bool]
    val_labels_masked = val_labels_flat[mask_bool]

    # AUROC - cascade model
    try:
        auroc_cascade = roc_auc_score(val_labels_masked, val_preds_masked)
    except Exception:
        auroc_cascade = 0.5

    # AUROC - independent (just self_uncertainty from X_val[:,0])
    val_X_np = X_val.cpu().numpy()
    val_self_unc_flat = val_X_np[:, :, 0].flatten()[mask_bool]
    try:
        auroc_independent = roc_auc_score(val_labels_masked, val_self_unc_flat)
    except Exception:
        auroc_independent = 0.5

    # CHAR - using validation docs
    val_docs = all_docs[n_train : n_train + n_val]

    # Independent scores (flat, only actual claims)
    indep_scores_list = []
    for doc in val_docs:
        for c in doc:
            indep_scores_list.append(c["self_uncertainty"])

    # Cascade (closed-form) scores
    cascade_cf_scores_list = []
    for doc in val_docs:
        scores = compute_cascade_uncertainty(doc, alpha=0.4)
        cascade_cf_scores_list.extend(scores)

    CHAR_independent = compute_CHAR(val_docs, indep_scores_list)
    CHAR_cascade = compute_CHAR(val_docs, cascade_cf_scores_list)

    experiment_data["biography_synthetic"]["metrics"]["CHAR_independent"].append(
        CHAR_independent
    )
    experiment_data["biography_synthetic"]["metrics"]["CHAR_cascade"].append(
        CHAR_cascade
    )
    experiment_data["biography_synthetic"]["metrics"]["AUROC_independent"].append(
        auroc_independent
    )
    experiment_data["biography_synthetic"]["metrics"]["AUROC_cascade"].append(
        auroc_cascade
    )
    experiment_data["biography_synthetic"]["losses"]["train"].append(train_loss)
    experiment_data["biography_synthetic"]["losses"]["val"].append(val_loss)
    experiment_data["biography_synthetic"]["epochs"].append(epoch)

    if epoch % 5 == 0 or epoch == 1:
        print(
            f"Epoch {epoch:3d}: val_loss={val_loss:.4f} | "
            f"AUROC_indep={auroc_independent:.4f} | AUROC_cascade={auroc_cascade:.4f} | "
            f"CHAR_indep={CHAR_independent:.4f} | CHAR_cascade={CHAR_cascade:.4f}"
        )

# ─── Final Test Evaluation ────────────────────────────────────────────────────
print("\n=== Final Test Evaluation ===")
model.eval()
test_docs = all_docs[n_train + n_val :]

with torch.no_grad():
    test_preds = model(X_test).cpu().numpy()  # (n_test, max_len)

test_masks = M_test.cpu().numpy()
test_labels = Y_test.cpu().numpy()

# Flatten masked
mask_bool_test = test_masks.flatten().astype(bool)
test_preds_flat = test_preds.flatten()[mask_bool_test]
test_labels_flat = test_labels.flatten()[mask_bool_test]
test_X_np = X_test.cpu().numpy()
test_self_unc_flat = test_X_np[:, :, 0].flatten()[mask_bool_test]

try:
    auroc_cascade_test = roc_auc_score(test_labels_flat, test_preds_flat)
except Exception:
    auroc_cascade_test = 0.5
try:
    auroc_indep_test = roc_auc_score(test_labels_flat, test_self_unc_flat)
except Exception:
    auroc_indep_test = 0.5

# CHAR on test docs
indep_scores_test = []
for doc in test_docs:
    for c in doc:
        indep_scores_test.append(c["self_uncertainty"])

cascade_cf_scores_test = []
for doc in test_docs:
    scores = compute_cascade_uncertainty(doc, alpha=0.4)
    cascade_cf_scores_test.extend(scores)

# Neural model scores for test docs
neural_scores_test = []
for i, doc in enumerate(test_docs):
    n_real = len(doc)
    neural_scores_test.extend(test_preds[i, :n_real].tolist())

CHAR_indep_test = compute_CHAR(test_docs, indep_scores_test)
CHAR_cascade_test = compute_CHAR(test_docs, cascade_cf_scores_test)
CHAR_neural_test = compute_CHAR(test_docs, neural_scores_test)

print(f"Test AUROC (Independent):  {auroc_indep_test:.4f}")
print(f"Test AUROC (Cascade GRU):  {auroc_cascade_test:.4f}")
print(f"Test CHAR  (Independent):  {CHAR_indep_test:.4f}")
print(f"Test CHAR  (Cascade CF):   {CHAR_cascade_test:.4f}")
print(f"Test CHAR  (Cascade GRU):  {CHAR_neural_test:.4f}")

# Save test results
experiment_data["biography_synthetic"]["test_results"] = {
    "AUROC_independent": float(auroc_indep_test),
    "AUROC_cascade_gru": float(auroc_cascade_test),
    "CHAR_independent": float(CHAR_indep_test),
    "CHAR_cascade_cf": float(CHAR_cascade_test),
    "CHAR_cascade_gru": float(CHAR_neural_test),
}
experiment_data["biography_synthetic"]["predictions"] = test_preds_flat.tolist()
experiment_data["biography_synthetic"]["ground_truth"] = test_labels_flat.tolist()
experiment_data["biography_synthetic"]["cascade_scores"] = neural_scores_test
experiment_data["biography_synthetic"]["independent_scores"] = indep_scores_test

# ─── Visualizations ───────────────────────────────────────────────────────────
epochs_arr = np.array(experiment_data["biography_synthetic"]["epochs"])

# 1. Training curves
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].plot(
    epochs_arr,
    experiment_data["biography_synthetic"]["losses"]["train"],
    label="Train Loss",
)
axes[0].plot(
    epochs_arr,
    experiment_data["biography_synthetic"]["losses"]["val"],
    label="Val Loss",
)
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("BCE Loss")
axes[0].set_title("Training & Validation Loss")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

axes[1].plot(
    epochs_arr,
    experiment_data["biography_synthetic"]["metrics"]["AUROC_independent"],
    label="Independent",
    linestyle="--",
)
axes[1].plot(
    epochs_arr,
    experiment_data["biography_synthetic"]["metrics"]["AUROC_cascade"],
    label="Cascade GRU",
)
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("AUROC")
axes[1].set_title("AUROC: Independent vs Cascade")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

axes[2].plot(
    epochs_arr,
    experiment_data["biography_synthetic"]["metrics"]["CHAR_independent"],
    label="CHAR Independent",
    linestyle="--",
)
axes[2].plot(
    epochs_arr,
    experiment_data["biography_synthetic"]["metrics"]["CHAR_cascade"],
    label="CHAR Cascade CF",
)
axes[2].axhline(y=1.0, color="red", linestyle=":", label="Baseline (1.0)")
axes[2].set_xlabel("Epoch")
axes[2].set_ylabel("CHAR")
axes[2].set_title("CHAR: Independent vs Cascade")
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "biography_synthetic_training_curves.png"), dpi=120
)
plt.close()

# 2. Cascade visualization for a sample document
sample_doc = all_docs[0]
sample_cascade = compute_cascade_uncertainty(sample_doc, alpha=0.4)
positions = [c["position"] for c in sample_doc]
self_unc = [c["self_uncertainty"] for c in sample_doc]
hallucinated = [c["is_hallucinated"] for c in sample_doc]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

bar_colors = ["#d62728" if h else "#2ca02c" for h in hallucinated]
axes[0].bar(positions, self_unc, color=bar_colors, alpha=0.7, label="Self Uncertainty")
axes[0].plot(positions, sample_cascade, "b-o", label="Cascade Score", linewidth=2)
axes[0].set_xlabel("Claim Position")
axes[0].set_ylabel("Uncertainty Score")
axes[0].set_title("Uncertainty Propagation in Sample Document")
red_patch = mpatches.Patch(color="#d62728", label="Hallucinated")
green_patch = mpatches.Patch(color="#2ca02c", label="Correct")
axes[0].legend(
    handles=[red_patch, green_patch] + axes[0].get_legend_handles_labels()[0][1:]
)
axes[0].grid(True, alpha=0.3)

# 3. CHAR bar chart comparison
methods = ["Independent", "Cascade CF", "Cascade GRU"]
char_vals = [CHAR_indep_test, CHAR_cascade_test, CHAR_neural_test]
colors = ["steelblue", "darkorange", "green"]
bars = axes[1].bar(methods, char_vals, color=colors, alpha=0.8)
axes[1].axhline(
    y=1.0, color="red", linestyle="--", linewidth=2, label="Baseline (no cascade)"
)
axes[1].set_ylabel("CHAR (higher = stronger cascade detection)")
axes[1].set_title("CHAR Comparison on Test Set")
axes[1].legend()
for bar, val in zip(bars, char_vals):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{val:.3f}",
        ha="center",
        fontsize=11,
        fontweight="bold",
    )
axes[1].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "biography_synthetic_cascade_analysis.png"), dpi=120
)
plt.close()

# 4. Uncertainty score distributions
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Distribution of uncertainty scores by hallucination label
all_test_indep = np.array(indep_scores_test)
all_test_labels = np.array([c["is_hallucinated"] for doc in test_docs for c in doc])

axes[0].hist(
    all_test_indep[all_test_labels == 0],
    bins=30,
    alpha=0.6,
    label="Correct",
    color="green",
    density=True,
)
axes[0].hist(
    all_test_indep[all_test_labels == 1],
    bins=30,
    alpha=0.6,
    label="Hallucinated",
    color="red",
    density=True,
)
axes[0].set_xlabel("Independent Uncertainty Score")
axes[0].set_ylabel("Density")
axes[0].set_title("Independent Uncertainty Score Distribution")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

all_test_cascade_cf = np.array(cascade_cf_scores_test)
axes[1].hist(
    all_test_cascade_cf[all_test_labels == 0],
    bins=30,
    alpha=0.6,
    label="Correct",
    color="green",
    density=True,
)
axes[1].hist(
    all_test_cascade_cf[all_test_labels == 1],
    bins=30,
    alpha=0.6,
    label="Hallucinated",
    color="red",
    density=True,
)
axes[1].set_xlabel("Cascade-Aware Uncertainty Score")
axes[1].set_ylabel("Density")
axes[1].set_title("Cascade-Aware Uncertainty Score Distribution")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "biography_synthetic_score_distributions.png"), dpi=120
)
plt.close()


# 5. CHAR by claim position (do early uncertain claims predict later errors more?)
def compute_CHAR_by_position(
    docs, uncertainty_scores_flat, threshold_quantile=0.75, n_bins=4
):
    """Compute CHAR separately for each position bin."""
    score_idx = 0
    all_doc_scores = []
    for doc in docs:
        doc_scores = uncertainty_scores_flat[score_idx : score_idx + len(doc)]
        all_doc_scores.append(doc_scores)
        score_idx += len(doc)

    high_thresh = np.quantile(uncertainty_scores_flat, threshold_quantile)

    # Bin positions: early, mid-early, mid-late, late
    position_bins = np.linspace(0, 1, n_bins + 1)
    CHAR_per_bin = []

    for bin_i in range(n_bins):
        bin_low = position_bins[bin_i]
        bin_high = position_bins[bin_i + 1]

        errors_after_high = []
        errors_after_low = []

        for doc_i, doc in enumerate(docs):
            doc_scores = all_doc_scores[doc_i]
            n = len(doc)

            for pos in range(n - 1):
                pos_ratio = pos / max(n - 1, 1)
                if not (
                    bin_low <= pos_ratio < bin_high
                    or (bin_i == n_bins - 1 and pos_ratio <= bin_high)
                ):
                    continue

                pivot_score = doc_scores[pos]
                downstream_claims = doc[pos + 1 :]
                downstream_error_rate = np.mean(
                    [c["is_hallucinated"] for c in downstream_claims]
                )

                if pivot_score >= high_thresh:
                    errors_after_high.append(downstream_error_rate)
                else:
                    errors_after_low.append(downstream_error_rate)

        if errors_after_low and errors_after_high:
            CHAR_per_bin.append(
                np.mean(errors_after_high) / (np.mean(errors_after_low) + 1e-8)
            )
        else:
            CHAR_per_bin.append(1.0)

    return CHAR_per_bin


CHAR_by_pos_indep = compute_CHAR_by_position(test_docs, indep_scores_test)
CHAR_by_pos_cascade = compute_CHAR_by_position(test_docs, cascade_cf_scores_test)

fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(4)
width = 0.35
ax.bar(
    x - width / 2,
    CHAR_by_pos_indep,
    width,
    label="Independent",
    color="steelblue",
    alpha=0.8,
)
ax.bar(
    x + width / 2,
    CHAR_by_pos_cascade,
    width,
    label="Cascade CF",
    color="darkorange",
    alpha=0.8,
)
ax.axhline(y=1.0, color="red", linestyle="--", linewidth=2, label="Baseline")
ax.set_xticks(x)
ax.set_xticklabels(
    ["Early\n(0-25%)", "Mid-Early\n(25-50%)", "Mid-Late\n(50-75%)", "Late\n(75-100%)"]
)
ax.set_ylabel("CHAR")
ax.set_title(
    "CHAR by Claim Position: Do Early Uncertain Claims Predict More Downstream Errors?"
)
ax.legend()
ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "biography_synthetic_CHAR_by_position.png"), dpi=120
)
plt.close()

# ─── Save all experiment data ─────────────────────────────────────────────────
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nAll results saved to {working_dir}")
print("\n=== Summary ===")
print(f"Final Test CHAR (Independent):  {CHAR_indep_test:.4f}")
print(f"Final Test CHAR (Cascade CF):   {CHAR_cascade_test:.4f}")
print(f"Final Test CHAR (Cascade GRU):  {CHAR_neural_test:.4f}")
print(f"Final Test AUROC (Independent): {auroc_indep_test:.4f}")
print(f"Final Test AUROC (Cascade GRU): {auroc_cascade_test:.4f}")
print(
    f"\nCHAR > 1.0 confirms cascade hypothesis: early uncertain claims predict downstream hallucinations."
)
