import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset, WeightedRandomSampler
import matplotlib.pyplot as plt

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {}


# ============================================================
# DATASETS
# ============================================================
def make_spurious_dataset(
    n_total=5000, d_core=8, d_spurious=8, spurious_corr=0.90, seed=42
):
    rng = np.random.RandomState(seed)
    n_maj = int(n_total * spurious_corr)
    n_min = n_total - n_maj

    def make_group(n, y, s):
        core = rng.randn(n, d_core) * 1.0
        core[:, 0] += (2 * y - 1) * 1.5
        spurious = rng.randn(n, d_spurious) * 0.5
        spurious[:, 0] += (2 * s - 1) * 4.0
        x = np.concatenate([core, spurious], axis=1).astype(np.float32)
        return x, np.full(n, y, np.int64), np.full(n, 2 * y + s, np.int64)

    n_per = n_maj // 2
    m_per = max(n_min // 2, 50)
    parts = [
        make_group(n_per, 0, 0),
        make_group(n_per, 1, 1),
        make_group(m_per, 0, 1),
        make_group(m_per, 1, 0),
    ]
    X = np.vstack([p[0] for p in parts])
    Y = np.concatenate([p[1] for p in parts])
    G = np.concatenate([p[2] for p in parts])
    return X, Y, G


def make_balanced_eval(n_per_group=300, d_core=8, d_spurious=8, seed=99):
    rng = np.random.RandomState(seed)
    parts = []
    for y in [0, 1]:
        for s in [0, 1]:
            core = rng.randn(n_per_group, d_core) * 1.0
            core[:, 0] += (2 * y - 1) * 1.5
            spurious = rng.randn(n_per_group, d_spurious) * 0.5
            spurious[:, 0] += (2 * s - 1) * 4.0
            x = np.concatenate([core, spurious], axis=1).astype(np.float32)
            parts.append(
                (
                    x,
                    np.full(n_per_group, y, np.int64),
                    np.full(n_per_group, 2 * y + s, np.int64),
                )
            )
    X = np.vstack([p[0] for p in parts])
    Y = np.concatenate([p[1] for p in parts])
    G = np.concatenate([p[2] for p in parts])
    return X, Y, G


def extract_text_features(texts, max_vocab=500, seed=0):
    from collections import Counter

    all_words = []
    for t in texts:
        all_words.extend(t.lower().split())
    word_counts = Counter(all_words)
    stopwords = {
        "the",
        "a",
        "an",
        "is",
        "it",
        "in",
        "of",
        "and",
        "to",
        "was",
        "i",
        "for",
        "this",
        "that",
        "with",
        "on",
        "at",
        "be",
        "are",
        "as",
        "its",
        "by",
        "from",
    }
    vocab = [w for w, c in word_counts.most_common(600) if w not in stopwords][
        :max_vocab
    ]
    word2idx = {w: i for i, w in enumerate(vocab)}
    features = np.zeros((len(texts), max_vocab + 8), dtype=np.float32)
    for i, t in enumerate(texts):
        words = t.lower().split()
        n_words = max(len(words), 1)
        for w in words:
            if w in word2idx:
                features[i, word2idx[w]] += 1.0 / n_words
        pos_w = sum(
            1
            for w in words
            if w
            in [
                "good",
                "great",
                "excellent",
                "love",
                "best",
                "wonderful",
                "perfect",
                "amazing",
            ]
        )
        neg_w = sum(
            1
            for w in words
            if w
            in [
                "bad",
                "terrible",
                "awful",
                "hate",
                "worst",
                "horrible",
                "boring",
                "disappointing",
            ]
        )
        features[i, max_vocab] = len(words) / 50.0
        features[i, max_vocab + 1] = pos_w / n_words
        features[i, max_vocab + 2] = neg_w / n_words
        features[i, max_vocab + 3] = (pos_w - neg_w) / n_words
        features[i, max_vocab + 4] = t.count("!") / n_words
        features[i, max_vocab + 5] = t.count("?") / n_words
        features[i, max_vocab + 6] = float(len(t) > 100)
        features[i, max_vocab + 7] = float(len(words) > 20)
    return features


def load_sst2_spurious(n_train=3000, n_eval=600, seed=42):
    print("  Loading SST2...")
    try:
        from datasets import load_dataset

        ds_train = load_dataset("glue", "sst2", split="train")
        ds_val = load_dataset("glue", "sst2", split="validation")
        texts_tr = [ds_train["sentence"][i] for i in range(min(n_train, len(ds_train)))]
        labels_tr = np.array(
            [ds_train["label"][i] for i in range(len(texts_tr))], dtype=np.int64
        )
        texts_val = [ds_val["sentence"][i] for i in range(min(n_eval, len(ds_val)))]
        labels_val = np.array(
            [ds_val["label"][i] for i in range(len(texts_val))], dtype=np.int64
        )
        all_feats = extract_text_features(texts_tr + texts_val, max_vocab=300)
        X_tr = all_feats[: len(texts_tr)]
        X_val = all_feats[len(texts_tr) :]
        len_tr = np.array([len(t) for t in texts_tr])
        len_median = np.median(len_tr)
        spurious_tr = (len_tr > len_median).astype(np.int64)
        spurious_val = (np.array([len(t) for t in texts_val]) > len_median).astype(
            np.int64
        )
        G_tr = (labels_tr * 2 + spurious_tr).astype(np.int64)
        G_val = (labels_val * 2 + spurious_val).astype(np.int64)
        print(f"  SST2 train: {X_tr.shape}, groups: {np.bincount(G_tr, minlength=4)}")
        return X_tr, labels_tr, G_tr, X_val, labels_val, G_val
    except Exception as e:
        print(f"  SST2 load failed: {e}. Using synthetic fallback.")
        X_tr, Y_tr, G_tr = make_spurious_dataset(n_total=n_train, seed=seed)
        X_val, Y_val, G_val = make_balanced_eval(n_per_group=150, seed=seed + 1)
        return X_tr, Y_tr, G_tr, X_val, Y_val, G_val


def load_imdb_spurious(n_train=3000, n_eval=600, seed=42):
    print("  Loading IMDB...")
    try:
        from datasets import load_dataset

        ds = load_dataset("imdb", split="train")
        idx = np.random.RandomState(seed).permutation(len(ds))
        texts_tr = [ds["text"][int(i)][:500] for i in idx[:n_train]]
        labels_tr = np.array(
            [ds["label"][int(i)] for i in idx[:n_train]], dtype=np.int64
        )
        texts_val = [ds["text"][int(i)][:500] for i in idx[n_train : n_train + n_eval]]
        labels_val = np.array(
            [ds["label"][int(i)] for i in idx[n_train : n_train + n_eval]],
            dtype=np.int64,
        )
        all_feats = extract_text_features(texts_tr + texts_val, max_vocab=300)
        X_tr = all_feats[: len(texts_tr)]
        X_val = all_feats[len(texts_tr) :]
        len_tr = np.array([len(t) for t in texts_tr])
        len_median = np.median(len_tr)
        spurious_tr = (len_tr > len_median).astype(np.int64)
        spurious_val = (np.array([len(t) for t in texts_val]) > len_median).astype(
            np.int64
        )
        G_tr = (labels_tr * 2 + spurious_tr).astype(np.int64)
        G_val = (labels_val * 2 + spurious_val).astype(np.int64)
        print(f"  IMDB train: {X_tr.shape}, groups: {np.bincount(G_tr, minlength=4)}")
        return X_tr, labels_tr, G_tr, X_val, labels_val, G_val
    except Exception as e:
        print(f"  IMDB load failed: {e}. Using synthetic fallback.")
        X_tr, Y_tr, G_tr = make_spurious_dataset(n_total=n_train, seed=seed + 10)
        X_val, Y_val, G_val = make_balanced_eval(n_per_group=150, seed=seed + 11)
        return X_tr, Y_tr, G_tr, X_val, Y_val, G_val


def load_tweet_eval_spurious(n_train=3000, n_eval=600, seed=42):
    print("  Loading Tweet Eval...")
    try:
        from datasets import load_dataset

        ds = load_dataset("tweet_eval", "sentiment", split="train")
        idx = np.random.RandomState(seed).permutation(len(ds))
        raw_labels = [ds["label"][int(i)] for i in idx[: n_train + n_eval]]
        bin_labels = [0 if l == 0 else 1 for l in raw_labels]
        texts_all = [str(ds["text"][int(i)]) for i in idx[: n_train + n_eval]]
        labels_all = np.array(bin_labels, dtype=np.int64)
        texts_tr = texts_all[:n_train]
        labels_tr = labels_all[:n_train]
        texts_val = texts_all[n_train : n_train + n_eval]
        labels_val = labels_all[n_train : n_train + n_eval]
        all_feats = extract_text_features(texts_tr + texts_val, max_vocab=300)
        X_tr = all_feats[:n_train]
        X_val = all_feats[n_train:]
        len_tr = np.array([len(t) for t in texts_tr])
        len_median = np.median(len_tr)
        spurious_tr = (len_tr > len_median).astype(np.int64)
        spurious_val = (np.array([len(t) for t in texts_val]) > len_median).astype(
            np.int64
        )
        G_tr = (labels_tr * 2 + spurious_tr).astype(np.int64)
        G_val = (labels_val * 2 + spurious_val).astype(np.int64)
        print(f"  Tweet train: {X_tr.shape}, groups: {np.bincount(G_tr, minlength=4)}")
        return X_tr, labels_tr, G_tr, X_val, labels_val, G_val
    except Exception as e:
        print(f"  Tweet Eval load failed: {e}. Using synthetic fallback.")
        X_tr, Y_tr, G_tr = make_spurious_dataset(n_total=n_train, seed=seed + 20)
        X_val, Y_val, G_val = make_balanced_eval(n_per_group=150, seed=seed + 21)
        return X_tr, Y_tr, G_tr, X_val, Y_val, G_val


# ============================================================
# MODEL
# ============================================================
class MLP(nn.Module):
    def __init__(self, in_dim, hidden=256, n_classes=2, dropout=0.3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.BatchNorm1d(hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden // 2),
            nn.BatchNorm1d(hidden // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden // 2, hidden // 4),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden // 4, n_classes)

    def forward(self, x):
        return self.classifier(self.features(x))


# ============================================================
# HELPERS
# ============================================================
def make_group_balanced_sampler(G_train):
    G = np.array(G_train)
    groups, counts = np.unique(G, return_counts=True)
    weights = np.zeros(len(G), dtype=np.float64)
    for g, c in zip(groups, counts):
        weights[G == g] = 1.0 / c
    return WeightedRandomSampler(weights=weights, num_samples=len(G), replacement=True)


def compute_grad_norm_ratio(model, easy_x, easy_y, hard_x, hard_y, criterion):
    model.zero_grad()
    loss_e = criterion(model(easy_x.to(device)), easy_y.to(device))
    loss_e.backward()
    gnorm_e = (
        sum(p.grad.norm().item() ** 2 for p in model.parameters() if p.grad is not None)
        ** 0.5
    )
    model.zero_grad()
    loss_h = criterion(model(hard_x.to(device)), hard_y.to(device))
    loss_h.backward()
    gnorm_h = (
        sum(p.grad.norm().item() ** 2 for p in model.parameters() if p.grad is not None)
        ** 0.5
    )
    model.zero_grad()
    if gnorm_e < 1e-10:
        return 1.0
    return gnorm_h / (gnorm_e + 1e-10)


def detect_plateau_stagnation(
    loss_history, window=10, min_epochs=15, stagnation_thresh=0.005
):
    if len(loss_history) < min_epochs + window:
        return False
    recent = np.array(loss_history[-window:])
    older = np.array(loss_history[-(window * 2) : -window])
    return (recent.mean() > 0.1) and (
        abs(recent.mean() - older.mean()) < stagnation_thresh
    )


# ============================================================
# INTERVENTION LOSS FUNCTIONS
# ============================================================
def group_reweighted_loss(logits, labels, groups, hard_weight=5.0):
    n_groups = 4
    group_counts = torch.zeros(n_groups, device=device)
    for g in range(n_groups):
        group_counts[g] = (groups == g).float().sum()
    max_count = group_counts.max()
    sample_weights = torch.ones(len(labels), device=device)
    for g in range(n_groups):
        if group_counts[g] > 0 and group_counts[g] < max_count * 0.5:
            sample_weights[groups == g] = hard_weight
    losses = F.cross_entropy(logits, labels, reduction="none")
    return (losses * sample_weights).mean()


def group_dro_loss(logits, labels, groups):
    n_groups = 4
    group_losses = torch.zeros(n_groups, device=device)
    for g in range(n_groups):
        mask = groups == g
        if mask.sum() > 0:
            group_losses[g] = F.cross_entropy(logits[mask], labels[mask])
    active = group_losses[group_losses > 0]
    if len(active) == 0:
        return F.cross_entropy(logits, labels)
    return active.max()


def focal_loss(logits, labels, gamma=2.0):
    ce_loss = F.cross_entropy(logits, labels, reduction="none")
    pt = torch.exp(-ce_loss)
    return (((1 - pt) ** gamma) * ce_loss).mean()


# ============================================================
# EVALUATION
# ============================================================
def evaluate(model, loader, device):
    model.eval()
    all_preds, all_labels, all_groups = [], [], []
    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()
    with torch.no_grad():
        for xb, yb, gb in loader:
            xb, yb = xb.to(device), yb.to(device)
            out = model(xb)
            total_loss += criterion(out, yb).item() * xb.size(0)
            all_preds.append(out.argmax(1).cpu().numpy())
            all_labels.append(yb.cpu().numpy())
            all_groups.append(gb.numpy())
    preds = np.concatenate(all_preds)
    labels = np.concatenate(all_labels)
    groups = np.concatenate(all_groups)
    avg_loss = total_loss / len(labels)
    overall_acc = (preds == labels).mean()
    group_accs = {
        int(g): float((preds[groups == g] == labels[groups == g]).mean())
        for g in np.unique(groups)
    }
    worst_group_acc = min(group_accs.values()) if group_accs else 0.0
    return avg_loss, overall_acc, worst_group_acc, group_accs


# ============================================================
# TRAINING: TASI with configurable intervention loss
# ============================================================
def run_tasi_experiment(
    intervention_loss_type,
    X_tr,
    Y_tr,
    G_tr,
    X_val,
    Y_val,
    G_val,
    in_dim,
    n_epochs=80,
    lr=3e-4,
    wd=1e-3,
    batch_size=128,
    seed=42,
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = MLP(in_dim=in_dim, hidden=256, n_classes=2, dropout=0.2).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)
    criterion = nn.CrossEntropyLoss()

    dataset = TensorDataset(
        torch.FloatTensor(X_tr), torch.LongTensor(Y_tr), torch.LongTensor(G_tr)
    )
    sampler = make_group_balanced_sampler(G_tr)
    loader = DataLoader(dataset, batch_size=batch_size, sampler=sampler)
    val_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_val), torch.LongTensor(Y_val), torch.LongTensor(G_val)
        ),
        batch_size=512,
        shuffle=False,
    )

    easy_idx = np.where((G_tr == 0) | (G_tr == 3))[0]
    hard_idx = np.where((G_tr == 1) | (G_tr == 2))[0]
    rng = np.random.RandomState(seed)

    def get_signal_batches(n=64):
        ei = rng.choice(easy_idx, min(n, len(easy_idx)), replace=False)
        hi = rng.choice(hard_idx, min(n, len(hard_idx)), replace=False)
        return (torch.FloatTensor(X_tr[ei]), torch.LongTensor(Y_tr[ei])), (
            torch.FloatTensor(X_tr[hi]),
            torch.LongTensor(Y_tr[hi]),
        )

    train_losses, val_losses, val_accs, wg_accs = [], [], [], []
    grad_ratios, plateau_flags, intervention_flags = [], [], []
    plateau_epoch = None
    tasi_state = "watching"
    tasi_counter = 0
    INTERVENTION_DURATION = 15
    COOLDOWN_DURATION = 15

    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0.0
        n_samples = 0
        for xb, yb, gb in loader:
            xb, yb, gb = xb.to(device), yb.to(device), gb.to(device)
            optimizer.zero_grad()
            out = model(xb)
            if tasi_state == "intervening":
                if intervention_loss_type == "group_reweighted":
                    loss = group_reweighted_loss(out, yb, gb, hard_weight=5.0)
                elif intervention_loss_type == "group_dro":
                    loss = group_dro_loss(out, yb, gb)
                elif intervention_loss_type == "focal":
                    loss = focal_loss(out, yb, gamma=2.0)
                else:
                    loss = criterion(out, yb)
            else:
                loss = criterion(out, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item() * xb.size(0)
            n_samples += xb.size(0)
        scheduler.step()
        train_loss = epoch_loss / n_samples
        train_losses.append(train_loss)

        in_plateau = False
        gnorm_ratio = 1.0
        if len(easy_idx) > 10 and len(hard_idx) > 10:
            easy_b, hard_b = get_signal_batches(64)
            gnorm_ratio = compute_grad_norm_ratio(
                model, easy_b[0], easy_b[1], hard_b[0], hard_b[1], criterion
            )
            in_plateau = detect_plateau_stagnation(
                train_losses, window=8, min_epochs=12, stagnation_thresh=0.008
            )
            if len(grad_ratios) >= 3:
                if np.mean(grad_ratios[-3:]) < 0.5 and train_loss > 0.15:
                    in_plateau = True
        grad_ratios.append(gnorm_ratio)
        plateau_flags.append(int(in_plateau))

        intervention_active = False
        if tasi_state == "watching":
            if in_plateau:
                tasi_state = "intervening"
                tasi_counter = 0
                if plateau_epoch is None:
                    plateau_epoch = epoch
                print(f"    [TASI-{intervention_loss_type}] Plateau at epoch {epoch}")
        elif tasi_state == "intervening":
            tasi_counter += 1
            intervention_active = True
            if tasi_counter >= INTERVENTION_DURATION:
                tasi_state = "cooldown"
                tasi_counter = 0
                print(
                    f"    [TASI-{intervention_loss_type}] Intervention ended at epoch {epoch}"
                )
        elif tasi_state == "cooldown":
            tasi_counter += 1
            if tasi_counter >= COOLDOWN_DURATION:
                tasi_state = "watching"
                tasi_counter = 0
        intervention_flags.append(int(intervention_active))

        val_loss, val_acc, wg_acc, grp_accs = evaluate(model, val_loader, device)
        val_losses.append(val_loss)
        val_accs.append(val_acc)
        wg_accs.append(wg_acc)

        if epoch % 20 == 0 or epoch == n_epochs - 1:
            print(
                f"    Epoch {epoch:3d}: train={train_loss:.4f}, val={val_loss:.4f}, val_acc={val_acc:.4f}, wg={wg_acc:.4f}, intv={intervention_active}"
            )

    return {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "val_accs": val_accs,
        "wg_accs": wg_accs,
        "grad_ratios": grad_ratios,
        "plateau_flags": plateau_flags,
        "intervention_flags": intervention_flags,
        "plateau_epoch": plateau_epoch,
        "best_wg_acc": float(max(wg_accs)),
        "final_wg_acc": float(wg_accs[-1]),
        "best_val_acc": float(max(val_accs)),
        "final_val_acc": float(val_accs[-1]),
    }


def run_baseline_experiment(
    base_method,
    X_tr,
    Y_tr,
    G_tr,
    X_val,
    Y_val,
    G_val,
    in_dim,
    n_epochs=80,
    lr=3e-4,
    wd=1e-3,
    batch_size=128,
    seed=42,
):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = MLP(in_dim=in_dim, hidden=256, n_classes=2, dropout=0.2).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_epochs)
    criterion = nn.CrossEntropyLoss()

    dataset = TensorDataset(
        torch.FloatTensor(X_tr), torch.LongTensor(Y_tr), torch.LongTensor(G_tr)
    )
    use_bal = base_method == "ERM_Balanced"
    if use_bal:
        sampler = make_group_balanced_sampler(G_tr)
        loader = DataLoader(dataset, batch_size=batch_size, sampler=sampler)
    else:
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(
        TensorDataset(
            torch.FloatTensor(X_val), torch.LongTensor(Y_val), torch.LongTensor(G_val)
        ),
        batch_size=512,
        shuffle=False,
    )

    train_losses, val_losses, val_accs, wg_accs = [], [], [], []

    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0.0
        n_samples = 0
        for xb, yb, gb in loader:
            xb, yb, gb = xb.to(device), yb.to(device), gb.to(device)
            optimizer.zero_grad()
            out = model(xb)
            if base_method == "Group_DRO":
                gl = torch.zeros(4, device=device)
                for g in range(4):
                    mk = gb == g
                    if mk.sum() > 0:
                        gl[g] = criterion(out[mk], yb[mk])
                loss = gl[gl > 0].max()
            else:
                loss = criterion(out, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item() * xb.size(0)
            n_samples += xb.size(0)
        scheduler.step()
        tl = epoch_loss / n_samples
        train_losses.append(tl)
        vl, va, wga, _ = evaluate(model, val_loader, device)
        val_losses.append(vl)
        val_accs.append(va)
        wg_accs.append(wga)
        if epoch % 20 == 0 or epoch == n_epochs - 1:
            print(
                f"    Epoch {epoch:3d}: train={tl:.4f}, val={vl:.4f}, val_acc={va:.4f}, wg={wga:.4f}"
            )

    return {
        "train_losses": train_losses,
        "val_losses": val_losses,
        "val_accs": val_accs,
        "wg_accs": wg_accs,
        "grad_ratios": [1.0] * n_epochs,
        "plateau_flags": [0] * n_epochs,
        "intervention_flags": [0] * n_epochs,
        "plateau_epoch": None,
        "best_wg_acc": float(max(wg_accs)),
        "final_wg_acc": float(wg_accs[-1]),
        "best_val_acc": float(max(val_accs)),
        "final_val_acc": float(val_accs[-1]),
    }


# ============================================================
# EXPERIMENT CONFIG
# ============================================================
TASI_VARIANTS = [
    ("TASI_GroupReweighted", "group_reweighted"),
    ("TASI_GroupDRO", "group_dro"),
    ("TASI_Focal", "focal"),
]
BASELINES = [("ERM", None), ("ERM_Balanced", None), ("Group_DRO", None)]
ALL_METHODS = BASELINES + TASI_VARIANTS
N_EPOCHS = 80
BATCH_SIZE = 128

datasets_to_run = []

print("\n" + "=" * 60)
print("Preparing Synthetic Dataset")
X_syn_tr, Y_syn_tr, G_syn_tr = make_spurious_dataset(
    n_total=4000, spurious_corr=0.90, seed=42
)
X_syn_val, Y_syn_val, G_syn_val = make_balanced_eval(n_per_group=300, seed=99)
X_mean = X_syn_tr.mean(0)
X_std = X_syn_tr.std(0) + 1e-8
X_syn_tr_n = (X_syn_tr - X_mean) / X_std
X_syn_val_n = (X_syn_val - X_mean) / X_std
print(
    f"Synthetic train: {X_syn_tr.shape}, groups: {np.bincount(G_syn_tr, minlength=4)}"
)
datasets_to_run.append(
    (
        "synthetic",
        X_syn_tr_n,
        Y_syn_tr,
        G_syn_tr,
        X_syn_val_n,
        Y_syn_val,
        G_syn_val,
        X_syn_tr.shape[1],
        3e-4,
        1e-3,
    )
)

print("\n" + "=" * 60)
print("Preparing SST2 Dataset")
X_sst_tr, Y_sst_tr, G_sst_tr, X_sst_val, Y_sst_val, G_sst_val = load_sst2_spurious(
    n_train=3000, n_eval=600
)
Xm = X_sst_tr.mean(0)
Xs = X_sst_tr.std(0) + 1e-8
X_sst_tr_n = (X_sst_tr - Xm) / Xs
X_sst_val_n = (X_sst_val - Xm) / Xs
datasets_to_run.append(
    (
        "sst2",
        X_sst_tr_n,
        Y_sst_tr,
        G_sst_tr,
        X_sst_val_n,
        Y_sst_val,
        G_sst_val,
        X_sst_tr.shape[1],
        1e-3,
        1e-4,
    )
)

print("\n" + "=" * 60)
print("Preparing IMDB Dataset")
X_imdb_tr, Y_imdb_tr, G_imdb_tr, X_imdb_val, Y_imdb_val, G_imdb_val = (
    load_imdb_spurious(n_train=3000, n_eval=600)
)
Xm2 = X_imdb_tr.mean(0)
Xs2 = X_imdb_tr.std(0) + 1e-8
X_imdb_tr_n = (X_imdb_tr - Xm2) / Xs2
X_imdb_val_n = (X_imdb_val - Xm2) / Xs2
datasets_to_run.append(
    (
        "imdb",
        X_imdb_tr_n,
        Y_imdb_tr,
        G_imdb_tr,
        X_imdb_val_n,
        Y_imdb_val,
        G_imdb_val,
        X_imdb_tr.shape[1],
        1e-3,
        1e-4,
    )
)

print("\n" + "=" * 60)
print("Preparing Tweet Eval Dataset")
X_tw_tr, Y_tw_tr, G_tw_tr, X_tw_val, Y_tw_val, G_tw_val = load_tweet_eval_spurious(
    n_train=3000, n_eval=600
)
Xm3 = X_tw_tr.mean(0)
Xs3 = X_tw_tr.std(0) + 1e-8
X_tw_tr_n = (X_tw_tr - Xm3) / Xs3
X_tw_val_n = (X_tw_val - Xm3) / Xs3
datasets_to_run.append(
    (
        "tweet_eval",
        X_tw_tr_n,
        Y_tw_tr,
        G_tw_tr,
        X_tw_val_n,
        Y_tw_val,
        G_tw_val,
        X_tw_tr.shape[1],
        1e-3,
        1e-4,
    )
)

# ============================================================
# RUN ALL EXPERIMENTS
# ============================================================
all_results = {}

for ds_config in datasets_to_run:
    ds_name = ds_config[0]
    X_tr_n, Y_tr, G_tr = ds_config[1], ds_config[2], ds_config[3]
    X_val_n, Y_val, G_val = ds_config[4], ds_config[5], ds_config[6]
    in_dim, lr, wd = ds_config[7], ds_config[8], ds_config[9]

    print(f"\n{'='*60}")
    print(f"Running experiments on: {ds_name.upper()}")
    experiment_data[ds_name] = {}
    all_results[ds_name] = {}

    for method_name, intv_type in ALL_METHODS:
        print(f"\n  --- Method: {method_name} ---")
        if method_name.startswith("TASI"):
            result = run_tasi_experiment(
                intervention_loss_type=intv_type,
                X_tr=X_tr_n,
                Y_tr=Y_tr,
                G_tr=G_tr,
                X_val=X_val_n,
                Y_val=Y_val,
                G_val=G_val,
                in_dim=in_dim,
                n_epochs=N_EPOCHS,
                lr=lr,
                wd=wd,
                batch_size=BATCH_SIZE,
                seed=42,
            )
        else:
            result = run_baseline_experiment(
                base_method=method_name,
                X_tr=X_tr_n,
                Y_tr=Y_tr,
                G_tr=G_tr,
                X_val=X_val_n,
                Y_val=Y_val,
                G_val=G_val,
                in_dim=in_dim,
                n_epochs=N_EPOCHS,
                lr=lr,
                wd=wd,
                batch_size=BATCH_SIZE,
                seed=42,
            )

        experiment_data[ds_name][method_name] = result
        all_results[ds_name][method_name] = {
            "best_wg_acc": result["best_wg_acc"],
            "final_wg_acc": result["final_wg_acc"],
            "best_val_acc": result["best_val_acc"],
            "final_val_acc": result["final_val_acc"],
        }
        print(
            f"  [{method_name}] Best WG={result['best_wg_acc']:.4f}, Final WG={result['final_wg_acc']:.4f}, Best Val={result['best_val_acc']:.4f}"
        )

# ============================================================
# FINAL SUMMARY
# ============================================================
method_names = [m for m, _ in ALL_METHODS]
print("\n" + "=" * 60)
print("FINAL SUMMARY - Best Worst-Group Accuracy")
print("=" * 60)
print(f"{'Dataset':<15} {'Method':<22} {'Best WG':>8} {'Final WG':>9} {'Best Acc':>9}")
print("-" * 67)
for ds_name in all_results:
    for mn in method_names:
        r = all_results[ds_name][mn]
        print(
            f"{ds_name:<15} {mn:<22} {r['best_wg_acc']:>8.4f} {r['final_wg_acc']:>9.4f} {r['best_val_acc']:>9.4f}"
        )
    print()

# ============================================================
# PLOTS
# ============================================================
epochs_arr = np.arange(N_EPOCHS)
method_colors = {
    "ERM": "steelblue",
    "ERM_Balanced": "orange",
    "Group_DRO": "green",
    "TASI_GroupReweighted": "red",
    "TASI_GroupDRO": "purple",
    "TASI_Focal": "brown",
}
method_ls = {
    "ERM": "-",
    "ERM_Balanced": "--",
    "Group_DRO": ":",
    "TASI_GroupReweighted": "-.",
    "TASI_GroupDRO": "-",
    "TASI_Focal": "--",
}

for ds_name in experiment_data:
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"{ds_name.upper()}: TASI Intervention Loss Ablation", fontsize=14)
    ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]
    for mn in method_names:
        r = experiment_data[ds_name][mn]
        c = method_colors[mn]
        ls = method_ls[mn]
        lw = 2.5 if mn.startswith("TASI") else 1.5
        ax1.plot(epochs_arr, r["train_losses"], color=c, ls=ls, label=mn, linewidth=lw)
        ax2.plot(epochs_arr, r["val_losses"], color=c, ls=ls, label=mn, linewidth=lw)
        ax3.plot(epochs_arr, r["val_accs"], color=c, ls=ls, label=mn, linewidth=lw)
        ax4.plot(epochs_arr, r["wg_accs"], color=c, ls=ls, label=mn, linewidth=lw)
        if mn.startswith("TASI"):
            for ep in range(N_EPOCHS):
                if r["intervention_flags"][ep]:
                    ax4.axvline(x=ep, color=c, alpha=0.04)
            if r["plateau_epoch"] is not None:
                ax4.axvline(
                    x=r["plateau_epoch"], color=c, alpha=0.5, ls=":", linewidth=1.5
                )
    for ax, title in zip(
        [ax1, ax2, ax3, ax4],
        ["Training Loss", "Val Loss", "Val Accuracy", "Worst-Group Accuracy"],
    ):
        ax.set_title(title)
        ax.set_xlabel("Epoch")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        os.path.join(working_dir, f"{ds_name}_intervention_loss_ablation.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

# Summary bar chart
tasi_method_names = [m for m, _ in TASI_VARIANTS]
baseline_names = [m for m, _ in BASELINES]

fig, axes = plt.subplots(1, len(experiment_data), figsize=(6 * len(experiment_data), 6))
if len(experiment_data) == 1:
    axes = [axes]
for ax, ds_name in zip(axes, experiment_data.keys()):
    all_mn = baseline_names + tasi_method_names
    best_wg = [all_results[ds_name][mn]["best_wg_acc"] for mn in all_mn]
    colors = [method_colors[mn] for mn in all_mn]
    bars = ax.bar(all_mn, best_wg, color=colors, alpha=0.85)
    for bar, v in zip(bars, best_wg):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{v:.3f}",
            ha="center",
            fontsize=9,
            fontweight="bold",
        )
    ax.set_title(f"{ds_name.upper()}\nBest Worst-Group Accuracy")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3, axis="y")
    ax.tick_params(axis="x", rotation=20)
plt.suptitle(
    "TASI Intervention Loss Strategy Ablation\nBest Worst-Group Accuracy",
    fontsize=13,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "intervention_loss_ablation_summary.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# TASI variants WG accuracy trajectories
fig, axes = plt.subplots(1, len(experiment_data), figsize=(5 * len(experiment_data), 5))
if len(experiment_data) == 1:
    axes = [axes]
for ax, ds_name in zip(axes, experiment_data.keys()):
    for mn in tasi_method_names:
        r = experiment_data[ds_name][mn]
        ax.plot(
            epochs_arr,
            r["wg_accs"],
            color=method_colors[mn],
            ls=method_ls[mn],
            label=mn,
            linewidth=2.5,
        )
    best_baseline_wg = max(
        all_results[ds_name][bn]["best_wg_acc"] for bn in baseline_names
    )
    ax.axhline(
        y=best_baseline_wg,
        color="black",
        ls="--",
        linewidth=1.5,
        label=f"Best baseline ({best_baseline_wg:.3f})",
    )
    ax.set_title(f"{ds_name.upper()}: TASI Variants\nWorst-Group Accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("WG Accuracy")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
plt.suptitle(
    "TASI Intervention Loss Strategy: WG Accuracy Trajectories",
    fontsize=13,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "tasi_variants_wg_trajectories.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

# Restructure experiment_data for the required format and save
save_data = {}
for mn in method_names:
    save_data[mn] = {}
    for ds_name in experiment_data:
        r = experiment_data[ds_name][mn]
        save_data[mn][ds_name] = {
            "metrics": {"train": r["val_accs"], "val": r["val_accs"]},
            "losses": {"train": r["train_losses"], "val": r["val_losses"]},
            "wg_accs": r["wg_accs"],
            "grad_ratios": r["grad_ratios"],
            "plateau_flags": r["plateau_flags"],
            "intervention_flags": r["intervention_flags"],
            "plateau_epoch": r["plateau_epoch"],
            "best_wg_acc": r["best_wg_acc"],
            "final_wg_acc": r["final_wg_acc"],
            "best_val_acc": r["best_val_acc"],
            "final_val_acc": r["final_val_acc"],
        }

np.save(os.path.join(working_dir, "experiment_data.npy"), save_data)
print("\nAll results saved to working directory.")
print("Plots saved:")
for ds_name in experiment_data:
    print(f"  - {ds_name}_intervention_loss_ablation.png")
print("  - intervention_loss_ablation_summary.png")
print("  - tasi_variants_wg_trajectories.png")
