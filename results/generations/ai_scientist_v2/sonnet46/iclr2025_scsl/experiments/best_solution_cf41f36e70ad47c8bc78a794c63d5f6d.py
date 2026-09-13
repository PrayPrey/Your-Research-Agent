import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
import matplotlib.pyplot as plt
from collections import defaultdict

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {}

# ============================================================
# UTILITIES
# ============================================================


class MLP(nn.Module):
    def __init__(self, in_dim, hidden=128, n_classes=2, dropout=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden // 2),
            nn.ReLU(),
        )
        self.head = nn.Linear(hidden // 2, n_classes)

    def forward(self, x):
        return self.head(self.net(x))

    def get_features(self, x):
        return self.net(x)


def evaluate_groups(model, loader, criterion, device):
    model.eval()
    preds, labels, groups, losses_list = [], [], [], []
    with torch.no_grad():
        for xb, yb, gb in loader:
            xb, yb = xb.to(device), yb.to(device)
            out = model(xb)
            loss = criterion(out, yb)
            preds.append(out.argmax(1).cpu().numpy())
            labels.append(yb.cpu().numpy())
            groups.append(gb.numpy())
            losses_list.append(loss.item())
    preds = np.concatenate(preds)
    labels = np.concatenate(labels)
    groups = np.concatenate(groups)
    overall_acc = (preds == labels).mean()
    avg_loss = np.mean(losses_list)
    group_accs = {}
    for g in np.unique(groups):
        m = groups == g
        if m.sum() > 0:
            group_accs[int(g)] = float((preds[m] == labels[m]).mean())
    worst_group = min(group_accs.values()) if group_accs else 0.0
    return avg_loss, float(overall_acc), float(worst_group), group_accs


def make_balanced_sampler(Y, G):
    """Group-balanced sampler: equal weight per group."""
    groups = G
    group_counts = np.bincount(groups)
    group_weights = 1.0 / (group_counts + 1e-8)
    sample_weights = torch.tensor([group_weights[g] for g in groups], dtype=torch.float)
    return WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)


def compute_grad_alignment(model, easy_x, easy_y, hard_x, hard_y, criterion, device):
    """Cosine similarity between gradients of easy and hard samples."""
    model.zero_grad()
    loss_e = criterion(model(easy_x.to(device)), easy_y.to(device))
    loss_e.backward()
    grad_e = torch.cat(
        [p.grad.flatten() for p in model.parameters() if p.grad is not None]
    ).clone()
    model.zero_grad()
    loss_h = criterion(model(hard_x.to(device)), hard_y.to(device))
    loss_h.backward()
    grad_h = torch.cat(
        [p.grad.flatten() for p in model.parameters() if p.grad is not None]
    ).clone()
    model.zero_grad()
    cos = F.cosine_similarity(grad_e.unsqueeze(0), grad_h.unsqueeze(0)).item()
    return cos


def detect_plateau_tasi(
    loss_history,
    grad_align_history,
    min_epochs=15,
    stag_window=8,
    stag_thresh=0.002,
    align_thresh=0.5,
):
    """Detect plateau: loss stagnating AND gradient alignment high (both on spurious)."""
    if len(loss_history) < min_epochs:
        return False
    recent = loss_history[-stag_window:]
    loss_change = abs(recent[-1] - recent[0])
    stagnating = loss_change < stag_thresh
    if len(grad_align_history) < 3:
        return stagnating
    recent_align = np.mean(grad_align_history[-3:])
    # High alignment means model uses same direction for easy/hard => shortcut
    return stagnating and (recent_align > align_thresh)


# ============================================================
# TASI TRAINING
# ============================================================


def train_method(
    method,
    X_tr,
    Y_tr,
    G_tr,
    val_loader,
    in_dim,
    n_epochs=80,
    lr=1e-3,
    wd=1e-4,
    batch_size=128,
    seed=42,
    device=device,
):
    torch.manual_seed(seed)
    np.random.seed(seed)

    model = MLP(in_dim=in_dim, hidden=256, n_classes=int(Y_tr.max() + 1)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)

    # Group-balanced sampler for all methods (fixes collapse issue)
    sampler = make_balanced_sampler(Y_tr, G_tr)
    dataset = TensorDataset(
        torch.FloatTensor(X_tr), torch.LongTensor(Y_tr), torch.LongTensor(G_tr)
    )
    train_loader = DataLoader(dataset, batch_size=batch_size, sampler=sampler)

    # For TASI: easy/hard split
    easy_mask = (G_tr == 0) | (
        G_tr == 3
    )  # majority groups (spurious aligns with label)
    hard_mask = (G_tr == 1) | (G_tr == 2)  # minority groups
    if easy_mask.sum() > 16 and hard_mask.sum() > 16:
        idx_e = np.where(easy_mask)[0][: min(256, easy_mask.sum())]
        idx_h = np.where(hard_mask)[0][: min(256, hard_mask.sum())]
        easy_x = torch.FloatTensor(X_tr[idx_e])
        easy_y = torch.LongTensor(Y_tr[idx_e])
        hard_x = torch.FloatTensor(X_tr[idx_h])
        hard_y = torch.LongTensor(Y_tr[idx_h])
    else:
        easy_x = easy_y = hard_x = hard_y = None

    loss_history = []
    grad_align_history = []
    tasi_state = "watching"
    tasi_counter = 0
    INTERV_DURATION = 10
    COOLDOWN = 15
    plateau_epoch = None
    intervention_epochs = []

    metrics = {
        "train_loss": [],
        "val_loss": [],
        "val_acc": [],
        "worst_group_acc": [],
        "grad_alignment": [],
        "intervention_active": [],
        "plateau_detected": [],
    }

    for epoch in range(n_epochs):
        # Compute gradient alignment every 3 epochs
        if epoch % 3 == 0 and easy_x is not None:
            try:
                ga = compute_grad_alignment(
                    model, easy_x, easy_y, hard_x, hard_y, criterion, device
                )
                grad_align_history.append(ga)
            except Exception:
                grad_align_history.append(0.0)
        elif len(grad_align_history) == 0:
            grad_align_history.append(0.0)

        # Determine intervention status
        intervention_active = False
        in_plateau = False

        if method == "TASI":
            in_plateau = detect_plateau_tasi(
                loss_history,
                grad_align_history,
                min_epochs=12,
                stag_window=6,
                stag_thresh=0.003,
                align_thresh=0.3,
            )
            if tasi_state == "watching":
                if in_plateau:
                    tasi_state = "intervening"
                    tasi_counter = 0
                    plateau_epoch = epoch
                    intervention_active = True
                    intervention_epochs.append(epoch)
            elif tasi_state == "intervening":
                tasi_counter += 1
                intervention_active = True
                intervention_epochs.append(epoch)
                if tasi_counter >= INTERV_DURATION:
                    tasi_state = "cooldown"
                    tasi_counter = 0
            elif tasi_state == "cooldown":
                tasi_counter += 1
                if tasi_counter >= COOLDOWN:
                    tasi_state = "watching"
                    tasi_counter = 0
        elif method == "GroupDRO":
            intervention_active = True  # always reweight

        # Train one epoch
        model.train()
        epoch_losses = []
        for xb, yb, gb in train_loader:
            xb, yb, gb = xb.to(device), yb.to(device), gb.to(device)
            optimizer.zero_grad()
            out = model(xb)

            if method == "GroupDRO":
                # Per-group loss, maximize worst group
                per_sample_loss = F.cross_entropy(out, yb, reduction="none")
                group_losses = torch.zeros(4, device=device)
                for g in range(4):
                    gm = gb == g
                    if gm.sum() > 0:
                        group_losses[g] = per_sample_loss[gm].mean()
                loss = group_losses.max()

            elif method == "TASI" and intervention_active:
                # Hard-sample upweighting intervention
                per_sample_loss = F.cross_entropy(out, yb, reduction="none")
                # Identify high-loss samples as proxy for hard/minority
                with torch.no_grad():
                    loss_vals = per_sample_loss.detach()
                    threshold = loss_vals.median()
                    hard_w = torch.where(
                        loss_vals > threshold,
                        torch.full_like(loss_vals, 2.5),
                        torch.ones_like(loss_vals),
                    )
                loss = (per_sample_loss * hard_w).mean()
                # Also add feature diversity regularization
                feats = model.get_features(xb)
                feat_var = feats.var(dim=0).mean()
                loss = loss - 0.05 * feat_var

            else:
                loss = F.cross_entropy(out, yb)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_losses.append(loss.item())

        scheduler.step()
        train_loss = np.mean(epoch_losses)
        loss_history.append(train_loss)

        val_loss, val_acc, wg_acc, grp_accs = evaluate_groups(
            model, val_loader, criterion, device
        )

        metrics["train_loss"].append(train_loss)
        metrics["val_loss"].append(val_loss)
        metrics["val_acc"].append(val_acc)
        metrics["worst_group_acc"].append(wg_acc)
        metrics["grad_alignment"].append(
            grad_align_history[-1] if grad_align_history else 0.0
        )
        metrics["intervention_active"].append(int(intervention_active))
        metrics["plateau_detected"].append(int(in_plateau))

        if epoch % 20 == 0 or epoch == n_epochs - 1:
            print(
                f"  [{method}] Ep {epoch:3d}: train={train_loss:.4f}, val={val_loss:.4f}, "
                f"acc={val_acc:.4f}, wg={wg_acc:.4f}, intv={intervention_active}"
            )

    if method == "TASI":
        metrics["plateau_epoch"] = plateau_epoch
        metrics["intervention_epochs"] = intervention_epochs
        print(
            f"  [TASI] Plateau at epoch {plateau_epoch}, total interventions: {len(intervention_epochs)}"
        )

    return model, metrics


# ============================================================
# DATASET BUILDERS
# ============================================================


def build_synthetic_dataset(n_train=5000, n_val=2000, spurious_corr=0.85, seed=0):
    """Create controlled spurious correlation dataset."""
    rng = np.random.RandomState(seed)

    def make_split(n, corr, seed2):
        rng2 = np.random.RandomState(seed2)
        n_maj = int(n * corr)
        n_min = n - n_maj
        n_per_maj = n_maj // 2
        n_per_min = n_min // 2

        parts = []
        for y, s in [(0, 0), (1, 1)]:  # majority: y matches s
            for n_s, label, spur in [(n_per_maj, y, s)]:
                core = rng2.randn(n_s, 8)
                core[:, 0] += (2 * label - 1) * 2.0
                sp_feat = rng2.randn(n_s, 8) * 0.5
                sp_feat[:, 0] += (2 * spur - 1) * 4.0
                x = np.concatenate([core, sp_feat], axis=1).astype(np.float32)
                parts.append(
                    (
                        x,
                        np.full(n_s, label, np.int64),
                        np.full(n_s, 2 * label + spur, np.int64),
                    )
                )
        for y, s in [(0, 1), (1, 0)]:  # minority: y mismatches s
            n_s = n_per_min
            core = rng2.randn(n_s, 8)
            core[:, 0] += (2 * y - 1) * 2.0
            sp_feat = rng2.randn(n_s, 8) * 0.5
            sp_feat[:, 0] += (2 * s - 1) * 4.0
            x = np.concatenate([core, sp_feat], axis=1).astype(np.float32)
            parts.append(
                (x, np.full(n_s, y, np.int64), np.full(n_s, 2 * y + s, np.int64))
            )

        X = np.vstack([p[0] for p in parts])
        Y = np.concatenate([p[1] for p in parts])
        G = np.concatenate([p[2] for p in parts])
        return X, Y, G

    X_tr, Y_tr, G_tr = make_split(n_train, spurious_corr, seed)
    X_v, Y_v, G_v = make_split(n_val, 0.5, seed + 1)  # balanced val/test
    X_te, Y_te, G_te = make_split(n_val, 0.5, seed + 2)
    return (X_tr, Y_tr, G_tr), (X_v, Y_v, G_v), (X_te, Y_te, G_te)


def build_hf_nlp_dataset(
    hf_name,
    hf_config,
    splits,
    label_col,
    text_col,
    n_train=3000,
    n_val=1000,
    seed=42,
    binary_label_fn=None,
    vocab_size=500,
    pca_dims=50,
):
    """Load HuggingFace NLP dataset, build TF-IDF features, create spurious correlation."""
    from datasets import load_dataset
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD

    print(f"  Loading {hf_name}/{hf_config}...")
    ds_train = load_dataset(hf_name, hf_config, split=splits[0])
    ds_val = load_dataset(hf_name, hf_config, split=splits[1])

    def process_split(ds, n, seed_s):
        rng = np.random.RandomState(seed_s)
        texts = [str(t) for t in ds[text_col][:n]]
        labels = [int(l) for l in ds[label_col][:n]]
        if binary_label_fn:
            labels = [binary_label_fn(l) for l in labels]
        return texts, np.array(labels, dtype=np.int64)

    texts_tr, Y_tr_raw = process_split(ds_train, n_train, seed)
    texts_v, Y_v_raw = process_split(ds_val, n_val, seed + 1)

    # Build TF-IDF features
    vectorizer = TfidfVectorizer(
        max_features=vocab_size, ngram_range=(1, 2), sublinear_tf=True, min_df=3
    )
    X_tr_tfidf = vectorizer.fit_transform(texts_tr).toarray().astype(np.float32)
    X_v_tfidf = vectorizer.transform(texts_v).toarray().astype(np.float32)

    # SVD for dimensionality reduction
    svd = TruncatedSVD(n_components=pca_dims, random_state=seed)
    X_tr_svd = svd.fit_transform(X_tr_tfidf).astype(np.float32)
    X_v_svd = svd.transform(X_v_tfidf).astype(np.float32)

    # Create spurious feature: text length (proxy for writing style)
    tr_lens = np.array([len(t) for t in texts_tr], dtype=np.float32)
    v_lens = np.array([len(t) for t in texts_v], dtype=np.float32)
    len_median = np.median(tr_lens)
    spur_tr = (tr_lens > len_median).astype(np.int64)
    spur_v = (v_lens > len_median).astype(np.int64)

    # Inject spurious correlation into training features
    rng = np.random.RandomState(seed + 10)
    spurious_strength = 3.0
    for i in range(len(X_tr_svd)):
        X_tr_svd[i, -1] += spurious_strength * (2 * spur_tr[i] - 1)
    for i in range(len(X_v_svd)):
        X_v_svd[i, -1] += spurious_strength * (2 * spur_v[i] - 1)

    # Groups: 0=(y=0,s=0), 1=(y=0,s=1), 2=(y=1,s=0), 3=(y=1,s=1)
    G_tr = (Y_tr_raw * 2 + spur_tr).astype(np.int64)
    G_v = (Y_v_raw * 2 + spur_v).astype(np.int64)

    # Normalize
    mu = X_tr_svd.mean(0)
    sig = X_tr_svd.std(0) + 1e-8
    X_tr_n = (X_tr_svd - mu) / sig
    X_v_n = (X_v_svd - mu) / sig

    print(f"  {hf_name}: tr={X_tr_n.shape}, groups_tr={np.bincount(G_tr, minlength=4)}")
    print(f"  {hf_name}: val={X_v_n.shape}, groups_v={np.bincount(G_v, minlength=4)}")
    return (X_tr_n, Y_tr_raw, G_tr), (X_v_n, Y_v_raw, G_v)


# ============================================================
# RUN ALL EXPERIMENTS
# ============================================================

METHODS_TO_RUN = ["ERM", "GroupDRO", "TASI"]
N_EPOCHS = 80
LR = 1e-3
WD = 1e-4
BATCH = 128

# ---- DATASET 1: Synthetic ----
print("\n" + "=" * 60)
print("DATASET 1: Synthetic Spurious Correlation (spurious_corr=0.85)")
(X_str, Y_str, G_str), (X_sv, Y_sv, G_sv), (X_ste, Y_ste, G_ste) = (
    build_synthetic_dataset(n_train=5000, n_val=2000, spurious_corr=0.85, seed=0)
)

# Normalize
mu_s = X_str.mean(0)
sig_s = X_str.std(0) + 1e-8
X_str_n = (X_str - mu_s) / sig_s
X_sv_n = (X_sv - mu_s) / sig_s
X_ste_n = (X_ste - mu_s) / sig_s

syn_val_loader = DataLoader(
    TensorDataset(
        torch.FloatTensor(X_sv_n), torch.LongTensor(Y_sv), torch.LongTensor(G_sv)
    ),
    batch_size=512,
)
syn_test_loader = DataLoader(
    TensorDataset(
        torch.FloatTensor(X_ste_n), torch.LongTensor(Y_ste), torch.LongTensor(G_ste)
    ),
    batch_size=512,
)
criterion_eval = nn.CrossEntropyLoss()

experiment_data["synthetic"] = {}
for method in METHODS_TO_RUN:
    print(f"\n[Synthetic] {method}")
    model, metrics = train_method(
        method,
        X_str_n,
        Y_str,
        G_str,
        syn_val_loader,
        in_dim=16,
        n_epochs=N_EPOCHS,
        lr=LR,
        wd=WD,
        batch_size=BATCH,
        device=device,
    )
    _, test_acc, test_wg, test_grps = evaluate_groups(
        model, syn_test_loader, criterion_eval, device
    )
    metrics["test_acc"] = test_acc
    metrics["test_wg"] = test_wg
    print(f"  [Synthetic/{method}] Test: acc={test_acc:.4f}, wg={test_wg:.4f}")
    experiment_data["synthetic"][method] = metrics

# ---- DATASET 2: SST2 (glue) ----
print("\n" + "=" * 60)
print("DATASET 2: SST2 from HuggingFace (glue/sst2)")
try:
    (X_sst_tr, Y_sst_tr, G_sst_tr), (X_sst_v, Y_sst_v, G_sst_v) = build_hf_nlp_dataset(
        "glue",
        "sst2",
        ["train", "validation"],
        "label",
        "sentence",
        n_train=4000,
        n_val=800,
        seed=42,
        pca_dims=40,
    )
    sst_val_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_sst_v),
            torch.LongTensor(Y_sst_v),
            torch.LongTensor(G_sst_v),
        ),
        batch_size=256,
    )
    experiment_data["sst2"] = {}
    for method in METHODS_TO_RUN:
        print(f"\n[SST2] {method}")
        model, metrics = train_method(
            method,
            X_sst_tr,
            Y_sst_tr,
            G_sst_tr,
            sst_val_loader,
            in_dim=40,
            n_epochs=N_EPOCHS,
            lr=5e-4,
            wd=1e-4,
            batch_size=BATCH,
            device=device,
        )
        _, val_acc, val_wg, _ = evaluate_groups(
            model, sst_val_loader, criterion_eval, device
        )
        metrics["test_acc"] = val_acc
        metrics["test_wg"] = val_wg
        print(f"  [SST2/{method}] Val: acc={val_acc:.4f}, wg={val_wg:.4f}")
        experiment_data["sst2"][method] = metrics
    SST2_OK = True
except Exception as e:
    print(f"  SST2 failed: {e}")
    SST2_OK = False

# ---- DATASET 3: Tweet Eval Sentiment ----
print("\n" + "=" * 60)
print("DATASET 3: Tweet Eval Sentiment from HuggingFace")
try:
    (X_tw_tr, Y_tw_tr, G_tw_tr), (X_tw_v, Y_tw_v, G_tw_v) = build_hf_nlp_dataset(
        "tweet_eval",
        "sentiment",
        ["train", "validation"],
        "label",
        "text",
        n_train=4000,
        n_val=800,
        seed=42,
        pca_dims=40,
        binary_label_fn=lambda l: 1 if l >= 1 else 0,
    )
    tw_val_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_tw_v),
            torch.LongTensor(Y_tw_v),
            torch.LongTensor(G_tw_v),
        ),
        batch_size=256,
    )
    experiment_data["tweet_eval"] = {}
    for method in METHODS_TO_RUN:
        print(f"\n[TweetEval] {method}")
        model, metrics = train_method(
            method,
            X_tw_tr,
            Y_tw_tr,
            G_tw_tr,
            tw_val_loader,
            in_dim=40,
            n_epochs=N_EPOCHS,
            lr=5e-4,
            wd=1e-4,
            batch_size=BATCH,
            device=device,
        )
        _, val_acc, val_wg, _ = evaluate_groups(
            model, tw_val_loader, criterion_eval, device
        )
        metrics["test_acc"] = val_acc
        metrics["test_wg"] = val_wg
        print(f"  [TweetEval/{method}] Val: acc={val_acc:.4f}, wg={val_wg:.4f}")
        experiment_data["tweet_eval"][method] = metrics
    TW_OK = True
except Exception as e:
    print(f"  TweetEval failed: {e}")
    TW_OK = False

# ---- DATASET 4: AG News (3rd HuggingFace dataset) ----
print("\n" + "=" * 60)
print("DATASET 4: AG News from HuggingFace (spurious: article length)")
try:
    (X_ag_tr, Y_ag_tr, G_ag_tr), (X_ag_v, Y_ag_v, G_ag_v) = build_hf_nlp_dataset(
        "ag_news",
        None,
        ["train", "test"],
        "label",
        "text",
        n_train=4000,
        n_val=800,
        seed=42,
        pca_dims=40,
        binary_label_fn=lambda l: 1 if l >= 2 else 0,
    )
    ag_val_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_ag_v),
            torch.LongTensor(Y_ag_v),
            torch.LongTensor(G_ag_v),
        ),
        batch_size=256,
    )
    experiment_data["ag_news"] = {}
    for method in METHODS_TO_RUN:
        print(f"\n[AGNews] {method}")
        model, metrics = train_method(
            method,
            X_ag_tr,
            Y_ag_tr,
            G_ag_tr,
            ag_val_loader,
            in_dim=40,
            n_epochs=N_EPOCHS,
            lr=5e-4,
            wd=1e-4,
            batch_size=BATCH,
            device=device,
        )
        _, val_acc, val_wg, _ = evaluate_groups(
            model, ag_val_loader, criterion_eval, device
        )
        metrics["test_acc"] = val_acc
        metrics["test_wg"] = val_wg
        print(f"  [AGNews/{method}] Val: acc={val_acc:.4f}, wg={val_wg:.4f}")
        experiment_data["ag_news"][method] = metrics
    AG_OK = True
except Exception as e:
    print(f"  AGNews failed: {e}")
    AG_OK = False

# ============================================================
# PLOTS
# ============================================================


def plot_dataset_results(ds_key, ds_title, methods, exp_data, out_dir):
    if ds_key not in exp_data:
        return
    data = exp_data[ds_key]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"{ds_title}: Training Curves", fontsize=14)
    colors = {"ERM": "steelblue", "GroupDRO": "orange", "TASI": "green"}
    linestyles = {"ERM": "-", "GroupDRO": "--", "TASI": "-."}

    for method in methods:
        if method not in data:
            continue
        m = data[method]
        epochs = range(len(m["train_loss"]))
        c = colors.get(method, "black")
        ls = linestyles.get(method, "-")
        axes[0].plot(epochs, m["train_loss"], color=c, ls=ls, label=method, lw=2)
        axes[1].plot(epochs, m["val_acc"], color=c, ls=ls, label=method, lw=2)
        axes[2].plot(epochs, m["worst_group_acc"], color=c, ls=ls, label=method, lw=2)
        # Mark TASI interventions
        if method == "TASI" and "intervention_epochs" in m and m["intervention_epochs"]:
            for ie in m["intervention_epochs"][:1]:
                axes[2].axvline(
                    x=ie, color="red", alpha=0.5, ls=":", lw=1.5, label="TASI interv."
                )

    for ax, title, ylabel in zip(
        axes,
        ["Training Loss", "Validation Accuracy", "Worst-Group Accuracy"],
        ["Loss", "Accuracy", "Worst-Group Acc"],
    ):
        ax.set_title(title)
        ax.set_xlabel("Epoch")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(
        os.path.join(out_dir, f"{ds_key}_curves.png"), dpi=150, bbox_inches="tight"
    )
    plt.close()

    # Gradient alignment for TASI
    if "TASI" in data and data["TASI"]["grad_alignment"]:
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        ga = data["TASI"]["grad_alignment"]
        ax2.plot(range(len(ga)), ga, color="purple", lw=2)
        ax2.axhline(0.3, color="red", ls="--", alpha=0.7, label="Plateau threshold")
        if data["TASI"].get("plateau_epoch") is not None:
            ax2.axvline(
                data["TASI"]["plateau_epoch"],
                color="orange",
                ls="--",
                lw=2,
                label=f'Plateau detected (ep {data["TASI"]["plateau_epoch"]})',
            )
        ax2.set_title(f"{ds_title}: TASI Gradient Alignment (Easy vs Hard)")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Cosine Similarity")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            os.path.join(out_dir, f"{ds_key}_tasi_grad_align.png"),
            dpi=150,
            bbox_inches="tight",
        )
        plt.close()


for ds_key, ds_title in [
    ("synthetic", "Synthetic Spurious"),
    ("sst2", "SST2 (HuggingFace)"),
    ("tweet_eval", "TweetEval (HuggingFace)"),
    ("ag_news", "AG News (HuggingFace)"),
]:
    plot_dataset_results(ds_key, ds_title, METHODS_TO_RUN, experiment_data, working_dir)

# Summary bar chart
all_ds_keys = [
    k for k in ["synthetic", "sst2", "tweet_eval", "ag_news"] if k in experiment_data
]
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Final Results: All Datasets", fontsize=14)

for ax_idx, metric_key in enumerate(["test_acc", "test_wg"]):
    ax = axes[ax_idx]
    n_ds = len(all_ds_keys)
    n_m = len(METHODS_TO_RUN)
    x = np.arange(n_ds)
    w = 0.25
    colors_m = ["steelblue", "orange", "green"]
    for j, method in enumerate(METHODS_TO_RUN):
        vals = []
        for ds_key in all_ds_keys:
            if method in experiment_data[ds_key]:
                vals.append(experiment_data[ds_key][method].get(metric_key, 0.0))
            else:
                vals.append(0.0)
        bars = ax.bar(
            x + j * w - w, vals, w, label=method, color=colors_m[j], alpha=0.8
        )
        for b in bars:
            ax.text(
                b.get_x() + b.get_width() / 2,
                b.get_height() + 0.005,
                f"{b.get_height():.3f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(all_ds_keys, rotation=15, ha="right")
    ax.set_ylabel("Accuracy")
    ax.set_title("Overall Test Acc" if ax_idx == 0 else "Worst-Group Acc")
    ax.legend()
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "final_summary_bar.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# TASI plateau detection analysis
fig, axes = plt.subplots(1, len(all_ds_keys), figsize=(5 * len(all_ds_keys), 5))
if len(all_ds_keys) == 1:
    axes = [axes]
fig.suptitle(
    "TASI Plateau Detection: Worst-Group Acc with Intervention Markers", fontsize=13
)
for ax, ds_key in zip(axes, all_ds_keys):
    if "TASI" not in experiment_data[ds_key]:
        continue
    m = experiment_data[ds_key]["TASI"]
    wg = m["worst_group_acc"]
    intv = m["intervention_active"]
    ax.plot(range(len(wg)), wg, "g-", lw=2, label="TASI WG Acc")
    if "ERM" in experiment_data[ds_key]:
        ax.plot(
            range(len(experiment_data[ds_key]["ERM"]["worst_group_acc"])),
            experiment_data[ds_key]["ERM"]["worst_group_acc"],
            "b--",
            lw=2,
            label="ERM WG Acc",
        )
    # Shade intervention periods
    intv_arr = np.array(intv)
    in_intv = False
    start = 0
    for ep in range(len(intv_arr)):
        if intv_arr[ep] and not in_intv:
            start = ep
            in_intv = True
        elif not intv_arr[ep] and in_intv:
            ax.axvspan(
                start,
                ep,
                alpha=0.2,
                color="red",
                label="Intervention" if start == ep else "",
            )
            in_intv = False
    pe = m.get("plateau_epoch")
    if pe is not None:
        ax.axvline(pe, color="orange", ls="--", lw=2, label=f"Plateau ep={pe}")
    ax.set_title(ds_key)
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Worst-Group Acc")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "tasi_plateau_analysis.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# Save all data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nExperiment data saved.")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
for ds_key in all_ds_keys:
    print(f"\n--- {ds_key} ---")
    best_wg = -1
    best_method = None
    for method in METHODS_TO_RUN:
        if method not in experiment_data[ds_key]:
            continue
        m = experiment_data[ds_key][method]
        print(
            f'  {method:12s}: test_acc={m.get("test_acc", 0):.4f}, test_wg={m.get("test_wg", 0):.4f}, '
            f'best_val_wg={max(m["worst_group_acc"]):.4f}'
        )
        if m.get("test_wg", 0) > best_wg:
            best_wg = m.get("test_wg", 0)
            best_method = method
    print(f"  => Best: {best_method} with WG={best_wg:.4f}")
    if "TASI" in experiment_data[ds_key]:
        pe = experiment_data[ds_key]["TASI"].get("plateau_epoch")
        n_intv = len(experiment_data[ds_key]["TASI"].get("intervention_epochs", []))
        print(f"  => TASI plateau detected at epoch {pe}, {n_intv} intervention epochs")

print("=" * 60)
print("Validation Loss per epoch (last 5 epochs per dataset/method):")
for ds_key in all_ds_keys:
    for method in METHODS_TO_RUN:
        if method in experiment_data[ds_key]:
            vl = experiment_data[ds_key][method]["val_loss"]
            print(
                f'  {ds_key}/{method}: last val_losses = {[f"{x:.4f}" for x in vl[-5:]]}'
            )
