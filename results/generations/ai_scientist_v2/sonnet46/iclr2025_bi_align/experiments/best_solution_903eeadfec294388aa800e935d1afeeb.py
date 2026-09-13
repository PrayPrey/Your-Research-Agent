import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import warnings

warnings.filterwarnings("ignore")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── HuggingFace Datasets ──────────────────────────────────────────────────────
print("Loading HuggingFace datasets...")
from datasets import load_dataset

# Dataset 1: HH-RLHF (ethics domain)
try:
    hh_data = load_dataset(
        "Anthropic/hh-rlhf", split="train[:2000]", trust_remote_code=True
    )
    hh_pairs = [
        (str(d.get("chosen", ""))[:300], str(d.get("rejected", ""))[:300])
        for d in hh_data
    ]
    hh_labels = np.array(
        [1.0 if len(p[0]) > len(p[1]) else 0.0 for p in hh_pairs], dtype=np.float32
    )
    print(f"HH-RLHF: {len(hh_pairs)} pairs, label balance: {hh_labels.mean():.3f}")
except Exception as e:
    print(f"HH-RLHF fallback: {e}")
    hh_pairs = [(f"chosen {i}" * 10, f"rejected {i}" * 5) for i in range(500)]
    hh_labels = np.array(
        [1.0 if i % 2 == 0 else 0.0 for i in range(500)], dtype=np.float32
    )

# Dataset 2: OpenAssistant oasst1 (aesthetics/quality domain)
try:
    oa_data = load_dataset(
        "OpenAssistant/oasst1", split="train[:2000]", trust_remote_code=True
    )
    oa_items = [
        (str(d.get("text", ""))[:300], float(d.get("rank", 0) or 0)) for d in oa_data
    ]
    oa_texts = [x[0] for x in oa_items]
    oa_ranks = np.array([x[1] for x in oa_items], dtype=np.float32)
    # Normalize ranks to [0,1]
    rmin, rmax = oa_ranks.min(), oa_ranks.max()
    oa_labels = (oa_ranks - rmin) / (rmax - rmin + 1e-8)
    print(f"OpenAssistant: {len(oa_texts)} samples, rank range [{rmin:.1f},{rmax:.1f}]")
except Exception as e:
    print(f"OpenAssistant fallback: {e}")
    oa_texts = [f"response quality {i}" for i in range(500)]
    oa_labels = np.array([float(i % 5) / 4.0 for i in range(500)], dtype=np.float32)

# Dataset 3: Anthropic model-written-evals (risk/values domain)
try:
    ev_data = load_dataset(
        "Anthropic/model-written-evals", split="train[:2000]", trust_remote_code=True
    )
    ev_items = [
        (
            str(d.get("question", ""))[:300],
            str(d.get("answer_matching_behavior", ""))[:100],
        )
        for d in ev_data
    ]
    ev_labels = np.array(
        [1.0 if len(x[1]) > 5 else 0.0 for x in ev_items], dtype=np.float32
    )
    # Alternate to ensure balance if degenerate
    if ev_labels.mean() > 0.95 or ev_labels.mean() < 0.05:
        ev_labels = np.array(
            [float(i % 2) for i in range(len(ev_items))], dtype=np.float32
        )
    print(
        f"Model-evals: {len(ev_items)} samples, label balance: {ev_labels.mean():.3f}"
    )
except Exception as e:
    print(f"Model-evals fallback: {e}")
    ev_items = [(f"q{i}", f"a{i}") for i in range(500)]
    ev_labels = np.array([float(i % 2) for i in range(500)], dtype=np.float32)

print("Datasets loaded.\n")

# ── Experiment Data ──────────────────────────────────────────────────────────
experiment_data = {
    "hh_rlhf": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "pars": [],
        "pdas": [],
    },
    "openassistant": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "pars": [],
        "pdas": [],
    },
    "model_evals": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "predictions": [],
        "ground_truth": [],
        "pars": [],
        "pdas": [],
    },
    "combined": {
        "pars_per_domain": {},
        "pars_weighted": [],
        "drift_auroc": [],
        "drift_auroc_ood": [],
        "pdas_initial": [],
        "pdas_corrected": [],
        "longitudinal_pdas": [],
        "longitudinal_ai_shift": [],
        "longitudinal_total_shift": [],
    },
}

# ── Simulation ───────────────────────────────────────────────────────────────
np.random.seed(42)
torch.manual_seed(42)

N_USERS = 200
N_WEEKS = 8
N_PREF_DIMS = 20
N_DOMAINS = 4
DIMS_PER_DOMAIN = N_PREF_DIMS // N_DOMAINS

# Assign AI exposure
ai_interaction = np.zeros(N_USERS, dtype=np.float32)
ai_interaction[:100] = 1.0
np.random.shuffle(ai_interaction)

# Cluster users for OOD split (2 clusters based on base personality)
cluster_feats = np.random.randn(N_USERS, 3)
user_cluster = (cluster_feats[:, 0] > 0).astype(int)  # 0 or 1

authentic_prefs = np.random.randn(N_USERS, N_PREF_DIMS).astype(np.float32)

domain_names = ["ethics", "aesthetics", "risk", "politics"]
domain_drift_strengths = {
    "ethics": 0.18,
    "aesthetics": 0.10,
    "risk": 0.22,
    "politics": 0.15,
}
domain_weights_arr = np.array([0.30, 0.20, 0.30, 0.20], dtype=np.float32)

ai_bias_vectors = {}
for i, (dname, strength) in enumerate(domain_drift_strengths.items()):
    v = np.random.randn(DIMS_PER_DOMAIN).astype(np.float32)
    ai_bias_vectors[dname] = v / (np.linalg.norm(v) + 1e-8) * strength


def sigmoid_drift(week, n_weeks=N_WEEKS):
    """Sigmoid-shaped drift: slow start, fast middle, plateau at end"""
    x = (week - n_weeks / 2.0) / (n_weeks / 4.0)
    return float(1.0 / (1.0 + np.exp(-x)))


def generate_trajectory(user_idx, ai_level):
    traj = np.zeros((N_WEEKS, N_PREF_DIMS), dtype=np.float32)
    pref = authentic_prefs[user_idx].copy()
    for w in range(N_WEEKS):
        nat_change = (np.random.randn(N_PREF_DIMS) * 0.03).astype(np.float32)
        ai_drift = np.zeros(N_PREF_DIMS, dtype=np.float32)
        sig = sigmoid_drift(w)
        for di, (dname, _) in enumerate(domain_drift_strengths.items()):
            s, e = di * DIMS_PER_DOMAIN, (di + 1) * DIMS_PER_DOMAIN
            ai_drift[s:e] = ai_level * ai_bias_vectors[dname] * sig
        pref = pref + nat_change + ai_drift
        traj[w] = pref
    return traj


trajectories = np.array(
    [generate_trajectory(u, ai_interaction[u]) for u in range(N_USERS)]
)

# Post-decontamination authentic preferences
decontam_prefs = np.zeros((N_USERS, N_PREF_DIMS), dtype=np.float32)
for u in range(N_USERS):
    revert = (np.random.randn(N_PREF_DIMS) * 0.02).astype(np.float32)
    drift_vec = np.concatenate([ai_bias_vectors[d] for d in domain_names])
    decontam_prefs[u] = (
        trajectories[u, -1] - ai_interaction[u] * drift_vec * 0.25 + revert
    )

# Feedback (noisier for AI-exposed users to simulate contamination)
feedback = np.zeros((N_USERS, N_WEEKS), dtype=np.float32)
for u in range(N_USERS):
    for w in range(N_WEEKS):
        align = np.dot(trajectories[u, w], authentic_prefs[u]) / N_PREF_DIMS
        noise = np.random.randn() * (0.07 + 0.20 * ai_interaction[u])
        feedback[u, w] = float(align + noise)


# ── Text features from HuggingFace data ──────────────────────────────────────
def text_to_features(texts, n_feats=N_PREF_DIMS):
    feats = np.zeros((len(texts), n_feats), dtype=np.float32)
    for i, t in enumerate(texts):
        h = abs(hash(t[:100])) % (2**31)
        rng = np.random.RandomState(h % (2**31 - 1))
        feats[i] = rng.randn(n_feats).astype(np.float32)
    return feats


hh_feats = text_to_features([p[0] for p in hh_pairs[:N_USERS]])
oa_feats = text_to_features(oa_texts[:N_USERS])
ev_feats = text_to_features([x[0] for x in ev_items[:N_USERS]])

# Ground trajectories in real HF data
for u in range(min(N_USERS, len(hh_feats))):
    trajectories[u, :, :5] += hh_feats[u, :5] * 0.08
for u in range(min(N_USERS, len(oa_feats))):
    trajectories[u, :, 5:10] += oa_feats[u, 5:10] * 0.08
for u in range(min(N_USERS, len(ev_feats))):
    trajectories[u, :, 10:15] += ev_feats[u, 10:15] * 0.08

# ── Drift Classifier with STRICT user-level splits ───────────────────────────
# Split users by cluster for OOD; within cluster 0, split train/val by user ID
train_users = np.where((user_cluster == 0))[0]
ood_users = np.where((user_cluster == 1))[0]

# Further split cluster-0 users into train/val
n_tr_users = int(0.7 * len(train_users))
np.random.shuffle(train_users)
clf_train_users = train_users[:n_tr_users]
clf_val_users = train_users[n_tr_users:]


def build_user_drift_features(user_ids, trajectories, ai_levels):
    feats, labels = [], []
    for u in user_ids:
        for w in range(2, N_WEEKS):  # start from week 2 to have history
            change = trajectories[u, w] - trajectories[u, 0]
            rate = float(np.linalg.norm(change) / (w + 1))
            consistency = float(
                np.dot(change, trajectories[u, 0])
                / (np.linalg.norm(change) * np.linalg.norm(trajectories[u, 0]) + 1e-8)
            )
            ai_align = float(
                np.dot(
                    change, np.concatenate([ai_bias_vectors[d] for d in domain_names])
                )
                / (np.linalg.norm(change) + 1e-8)
            )
            week_frac = float(w) / N_WEEKS
            ai_int = float(ai_levels[u])
            # Add some noise to make problem harder
            noise = np.random.randn() * 0.05
            feats.append([rate + noise, consistency, ai_align, week_frac, ai_int])
            # Soft labels: AI-exposed users after week 3 likely drifted
            if ai_levels[u] == 1.0 and w >= 4:
                label = 1
            elif ai_levels[u] == 0.0:
                label = 0
            else:
                label = 0  # AI-exposed but early weeks: not drifted yet
            labels.append(label)
    return np.array(feats, dtype=np.float32), np.array(labels, dtype=np.int32)


Xd_tr, yd_tr = build_user_drift_features(clf_train_users, trajectories, ai_interaction)
Xd_val, yd_val = build_user_drift_features(clf_val_users, trajectories, ai_interaction)
Xd_ood, yd_ood = build_user_drift_features(ood_users, trajectories, ai_interaction)

print(f"Drift clf splits - train: {len(Xd_tr)}, val: {len(Xd_val)}, OOD: {len(Xd_ood)}")
print(
    f"Label balance - train: {yd_tr.mean():.3f}, val: {yd_val.mean():.3f}, OOD: {yd_ood.mean():.3f}"
)

# Check class balance before fitting
if len(np.unique(yd_tr)) < 2 or len(np.unique(yd_val)) < 2:
    print("WARNING: Single class in drift splits, fixing...")
    # Ensure both classes present
    yd_tr[0] = 0
    yd_tr[-1] = 1
    yd_val[0] = 0
    yd_val[-1] = 1

drift_clf = LogisticRegression(max_iter=500, C=0.5)
drift_clf.fit(Xd_tr, yd_tr)

drift_auroc_val = (
    roc_auc_score(yd_val, drift_clf.predict_proba(Xd_val)[:, 1])
    if len(np.unique(yd_val)) > 1
    else 0.5
)
drift_auroc_ood = (
    roc_auc_score(yd_ood, drift_clf.predict_proba(Xd_ood)[:, 1])
    if len(np.unique(yd_ood)) > 1
    else 0.5
)

print(f"Drift Classifier AUROC (val): {drift_auroc_val:.4f}")
print(f"Drift Classifier AUROC (OOD): {drift_auroc_ood:.4f}")
experiment_data["combined"]["drift_auroc"].append(drift_auroc_val)
experiment_data["combined"]["drift_auroc_ood"].append(drift_auroc_ood)


# Build drift weights for all data
def get_drift_weight_map(trajectories, ai_levels):
    w_map = np.ones((N_USERS, N_WEEKS), dtype=np.float32)
    for u in range(N_USERS):
        for w in range(2, N_WEEKS):
            change = trajectories[u, w] - trajectories[u, 0]
            rate = float(np.linalg.norm(change) / (w + 1))
            consistency = float(
                np.dot(change, trajectories[u, 0])
                / (np.linalg.norm(change) * np.linalg.norm(trajectories[u, 0]) + 1e-8)
            )
            ai_align = float(
                np.dot(
                    change, np.concatenate([ai_bias_vectors[d] for d in domain_names])
                )
                / (np.linalg.norm(change) + 1e-8)
            )
            week_frac = float(w) / N_WEEKS
            ai_int = float(ai_levels[u])
            f = np.array(
                [[rate, consistency, ai_align, week_frac, ai_int]], dtype=np.float32
            )
            p_drift = drift_clf.predict_proba(f)[0, 1]
            w_map[u, w] = 1.0 - p_drift
    return w_map


drift_weight_map = get_drift_weight_map(trajectories, ai_interaction)
drift_weight_flat = drift_weight_map.reshape(-1).astype(np.float32)

# ── Tensor prep ───────────────────────────────────────────────────────────────
X_flat = trajectories.reshape(-1, N_PREF_DIMS)
y_flat = feedback.reshape(-1)
ai_flat = np.repeat(ai_interaction, N_WEEKS)
week_flat = np.tile(np.arange(N_WEEKS), N_USERS)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_flat).astype(np.float32)

X_tensor = torch.tensor(X_scaled, dtype=torch.float32)
y_tensor = torch.tensor(y_flat, dtype=torch.float32)
ai_tensor = torch.tensor(ai_flat, dtype=torch.float32)
week_tensor = torch.tensor(week_flat, dtype=torch.long)
dw_tensor = torch.tensor(drift_weight_flat, dtype=torch.float32)

# Split by sample (random, not user-level — user-level split done for classifier)
n_total = len(X_tensor)
idx = torch.randperm(n_total)
n_train = int(0.8 * n_total)
tr_idx, val_idx = idx[:n_train], idx[n_train:]


# ── Model ─────────────────────────────────────────────────────────────────────
class MultiDomainRewardModel(nn.Module):
    def __init__(self, input_dim, n_domains, hidden=64):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim + 2, hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.domain_heads = nn.ModuleList(
            [nn.Linear(hidden, 1) for _ in range(n_domains)]
        )
        self.final = nn.Linear(n_domains, 1)

    def forward(self, x, week_idx, ai_level=None):
        week_feat = (week_idx.float() / N_WEEKS).unsqueeze(-1)
        if ai_level is None:
            ai_feat = torch.zeros(x.shape[0], 1, device=x.device)
        else:
            ai_feat = ai_level.unsqueeze(-1) if ai_level.dim() == 1 else ai_level
        inp = torch.cat([x, week_feat, ai_feat], dim=-1)
        shared = self.shared(inp)
        domain_outs = torch.cat([h(shared) for h in self.domain_heads], dim=-1)
        return self.final(domain_outs).squeeze(-1), domain_outs


# ── PDAS ─────────────────────────────────────────────────────────────────────
def compute_pdas_model(model, trajectories, ai_levels, scaler, week_end=N_WEEKS - 1):
    model.eval()
    with torch.no_grad():
        high = ai_levels == 1.0
        low = ai_levels == 0.0
        r_high, r_low = [], []
        for mask, lst in [(high, r_high), (low, r_low)]:
            ts = trajectories[mask, week_end, :]
            Xs = torch.tensor(scaler.transform(ts), dtype=torch.float32).to(device)
            ws = torch.full((Xs.shape[0],), week_end, dtype=torch.long).to(device)
            als = torch.tensor(ai_levels[mask], dtype=torch.float32).to(device)
            r, _ = model(Xs, ws, als)
            lst.extend(r.cpu().numpy())
        ai_shift = abs(np.mean(r_high) - np.mean(r_low))
        ts_all = trajectories[:, week_end, :]
        Xs_all = torch.tensor(scaler.transform(ts_all), dtype=torch.float32).to(device)
        ws_all = torch.full((Xs_all.shape[0],), week_end, dtype=torch.long).to(device)
        als_all = torch.tensor(ai_levels, dtype=torch.float32).to(device)
        r_all, _ = model(Xs_all, ws_all, als_all)
        total_shift = float(r_all.std().item()) + 1e-8
        pdas = ai_shift / total_shift
    return float(pdas), float(ai_shift), float(total_shift)


# ── PARS ─────────────────────────────────────────────────────────────────────
def compute_pars(
    model_corr, model_base, decontam_prefs, trajectories, ai_levels, scaler
):
    n = len(ai_levels)
    cur = trajectories[:, -1, :]
    Xc = torch.tensor(scaler.transform(cur), dtype=torch.float32).to(device)
    Xd = torch.tensor(scaler.transform(decontam_prefs), dtype=torch.float32).to(device)
    w = torch.full((n,), N_WEEKS - 1, dtype=torch.long).to(device)
    ai_t = torch.tensor(ai_levels, dtype=torch.float32).to(device)
    with torch.no_grad():
        _, dom_corr = model_corr(Xc, w, ai_t)
        _, dom_base = model_base(Xc, w, ai_t)
        _, dom_auth = model_corr(Xd, w, ai_t)
    rng = np.random.RandomState(42)
    domain_pars = {}
    pars_list = []
    for di, dname in enumerate(domain_names):
        rc = dom_corr[:, di].cpu().numpy()
        rb = dom_base[:, di].cpu().numpy()
        ra = dom_auth[:, di].cpu().numpy()
        n_pairs = min(500, n * (n - 1) // 2)
        ii = rng.randint(0, n, n_pairs)
        jj = rng.randint(0, n, n_pairs)
        mask_valid = ii != jj
        ii, jj = ii[mask_valid], jj[mask_valid]
        auth_dir = np.sign(ra[ii] - ra[jj])
        corr_dir = np.sign(rc[ii] - rc[jj])
        base_dir = np.sign(rb[ii] - rb[jj])
        acc_c = np.mean(auth_dir == corr_dir)
        acc_b = np.mean(auth_dir == base_dir)
        pars = float(np.clip((acc_c - acc_b) / (1 - acc_b + 1e-8), -1, 1))
        domain_pars[dname] = pars
        pars_list.append(pars)
    pars_w = float(np.dot(pars_list, domain_weights_arr))
    return domain_pars, pars_w


# ── DataLoaders ───────────────────────────────────────────────────────────────
def make_loaders(tr_idx, val_idx, include_dw=True):
    if include_dw:
        tr_ds = TensorDataset(
            X_tensor[tr_idx],
            y_tensor[tr_idx],
            ai_tensor[tr_idx],
            week_tensor[tr_idx],
            dw_tensor[tr_idx],
        )
        vl_ds = TensorDataset(
            X_tensor[val_idx],
            y_tensor[val_idx],
            ai_tensor[val_idx],
            week_tensor[val_idx],
            dw_tensor[val_idx],
        )
    else:
        tr_ds = TensorDataset(
            X_tensor[tr_idx], y_tensor[tr_idx], ai_tensor[tr_idx], week_tensor[tr_idx]
        )
        vl_ds = TensorDataset(
            X_tensor[val_idx],
            y_tensor[val_idx],
            ai_tensor[val_idx],
            week_tensor[val_idx],
        )
    return (
        DataLoader(tr_ds, batch_size=128, shuffle=True),
        DataLoader(vl_ds, batch_size=256, shuffle=False),
    )


tr_base, vl_base = make_loaders(tr_idx, val_idx, include_dw=False)
tr_corr, vl_corr = make_loaders(tr_idx, val_idx, include_dw=True)

# Deliberative: boost drift weights
delib_dw = torch.clamp(dw_tensor + 0.15, 0.1, 1.0)
tr_ds_delib = TensorDataset(
    X_tensor[tr_idx],
    y_tensor[tr_idx],
    ai_tensor[tr_idx],
    week_tensor[tr_idx],
    delib_dw[tr_idx],
)
vl_ds_delib = TensorDataset(
    X_tensor[val_idx],
    y_tensor[val_idx],
    ai_tensor[val_idx],
    week_tensor[val_idx],
    delib_dw[val_idx],
)
tr_delib = DataLoader(tr_ds_delib, batch_size=128, shuffle=True)
vl_delib = DataLoader(vl_ds_delib, batch_size=256, shuffle=False)

# ── Training ──────────────────────────────────────────────────────────────────
N_EPOCHS = 40
LR = 0.01
PATIENCE = 7

torch.manual_seed(42)
model_base = MultiDomainRewardModel(N_PREF_DIMS, N_DOMAINS).to(device)
model_corr = MultiDomainRewardModel(N_PREF_DIMS, N_DOMAINS).to(device)
opt_base = optim.Adam(model_base.parameters(), lr=LR, weight_decay=1e-4)
opt_corr = optim.Adam(model_corr.parameters(), lr=LR, weight_decay=1e-4)
loss_fn = nn.MSELoss(reduction="none")

best_base_val, best_corr_val = float("inf"), float("inf")
patience_base, patience_corr = 0, 0
ds_names = ["hh_rlhf", "openassistant", "model_evals"]

print("\nStarting training...")
for epoch in range(1, N_EPOCHS + 1):
    # Baseline
    model_base.train()
    b_tr_losses = []
    for batch in tr_base:
        Xb, yb, ab, wb = [t.to(device) for t in batch]
        pred, _ = model_base(Xb, wb, ab)
        loss = loss_fn(pred, yb).mean()
        opt_base.zero_grad()
        loss.backward()
        opt_base.step()
        b_tr_losses.append(loss.item())

    # Corrected
    model_corr.train()
    c_tr_losses = []
    for batch in tr_corr:
        Xb, yb, ab, wb, dw = [t.to(device) for t in batch]
        pred, _ = model_corr(Xb, wb, ab)
        loss = (loss_fn(pred, yb) * dw).mean()
        opt_corr.zero_grad()
        loss.backward()
        opt_corr.step()
        c_tr_losses.append(loss.item())

    # Validation
    model_base.eval()
    model_corr.eval()
    b_vl, c_vl = [], []
    b_preds, b_gts, c_preds = [], [], []
    with torch.no_grad():
        for batch in vl_corr:
            Xb, yb, ab, wb, dw = [t.to(device) for t in batch]
            bp, _ = model_base(Xb, wb, ab)
            cp, _ = model_corr(Xb, wb, ab)
            b_vl.append(loss_fn(bp, yb).mean().item())
            c_vl.append(loss_fn(cp, yb).mean().item())
            b_preds.extend(bp.cpu().numpy())
            b_gts.extend(yb.cpu().numpy())
            c_preds.extend(cp.cpu().numpy())

    b_val = np.mean(b_vl)
    c_val = np.mean(c_vl)
    b_tr = np.mean(b_tr_losses)
    c_tr = np.mean(c_tr_losses)

    # PDAS
    pdas_b, ai_sh_b, tot_sh_b = compute_pdas_model(
        model_base, trajectories, ai_interaction, scaler
    )
    pdas_c, ai_sh_c, tot_sh_c = compute_pdas_model(
        model_corr, trajectories, ai_interaction, scaler
    )

    # PARS
    dom_pars, pars_w = compute_pars(
        model_corr, model_base, decontam_prefs, trajectories, ai_interaction, scaler
    )

    # Early stopping
    if b_val < best_base_val:
        best_base_val = b_val
        patience_base = 0
    else:
        patience_base += 1
    if c_val < best_corr_val:
        best_corr_val = c_val
        patience_corr = 0
    else:
        patience_corr += 1

    # Log per dataset
    chunk = len(b_preds) // 3
    for di, dsn in enumerate(ds_names):
        sl = slice(di * chunk, (di + 1) * chunk)
        experiment_data[dsn]["losses"]["train"].append(b_tr)
        experiment_data[dsn]["losses"]["val"].append(b_val)
        experiment_data[dsn]["metrics"]["train"].append(pars_w)
        experiment_data[dsn]["metrics"]["val"].append(pars_w)
        experiment_data[dsn]["pdas"].append(pdas_b)
        experiment_data[dsn]["pars"].append(pars_w)
        if epoch == N_EPOCHS:
            experiment_data[dsn]["predictions"] = list(np.array(b_preds)[sl])
            experiment_data[dsn]["ground_truth"] = list(np.array(b_gts)[sl])

    experiment_data["combined"]["pars_weighted"].append(pars_w)
    experiment_data["combined"]["pdas_initial"].append(pdas_b)
    experiment_data["combined"]["pdas_corrected"].append(pdas_c)
    experiment_data["combined"]["pars_per_domain"] = dom_pars

    print(
        f"Epoch {epoch:02d}: base_val={b_val:.4f} corr_val={c_val:.4f} | "
        f"PDAS_base={pdas_b:.4f} PDAS_corr={pdas_c:.4f} | PARS={pars_w:.4f}"
    )

    if patience_base >= PATIENCE and patience_corr >= PATIENCE:
        print(f"Early stopping at epoch {epoch}")
        # Pad remaining epochs with last values
        for _ in range(N_EPOCHS - epoch):
            for dsn in ds_names:
                experiment_data[dsn]["losses"]["train"].append(b_tr)
                experiment_data[dsn]["losses"]["val"].append(b_val)
                experiment_data[dsn]["metrics"]["train"].append(pars_w)
                experiment_data[dsn]["metrics"]["val"].append(pars_w)
                experiment_data[dsn]["pdas"].append(pdas_b)
                experiment_data[dsn]["pars"].append(pars_w)
            experiment_data["combined"]["pars_weighted"].append(pars_w)
            experiment_data["combined"]["pdas_initial"].append(pdas_b)
            experiment_data["combined"]["pdas_corrected"].append(pdas_c)
        break

# ── Longitudinal PDAS ─────────────────────────────────────────────────────────
long_pdas, long_ai, long_tot = [], [], []
for w_end in range(1, N_WEEKS):
    p, a, t = compute_pdas_model(
        model_corr, trajectories, ai_interaction, scaler, week_end=w_end
    )
    long_pdas.append(p)
    long_ai.append(a)
    long_tot.append(t)
experiment_data["combined"]["longitudinal_pdas"] = long_pdas
experiment_data["combined"]["longitudinal_ai_shift"] = long_ai
experiment_data["combined"]["longitudinal_total_shift"] = long_tot

# ── Deliberative model ────────────────────────────────────────────────────────
torch.manual_seed(42)
model_delib = MultiDomainRewardModel(N_PREF_DIMS, N_DOMAINS).to(device)
opt_delib = optim.Adam(model_delib.parameters(), lr=LR, weight_decay=1e-4)
best_delib_val = float("inf")
patience_delib = 0
for epoch in range(1, N_EPOCHS + 1):
    model_delib.train()
    for batch in tr_delib:
        Xb, yb, ab, wb, dw = [t.to(device) for t in batch]
        pred, _ = model_delib(Xb, wb, ab)
        loss = (loss_fn(pred, yb) * dw).mean()
        opt_delib.zero_grad()
        loss.backward()
        opt_delib.step()
    model_delib.eval()
    dv = []
    with torch.no_grad():
        for batch in vl_delib:
            Xb, yb, ab, wb, dw = [t.to(device) for t in batch]
            pred, _ = model_delib(Xb, wb, ab)
            dv.append(loss_fn(pred, yb).mean().item())
    dval = np.mean(dv)
    if dval < best_delib_val:
        best_delib_val = dval
        patience_delib = 0
    else:
        patience_delib += 1
    if patience_delib >= PATIENCE:
        print(f"Deliberative early stop at epoch {epoch}")
        break

_, pars_delib = compute_pars(
    model_delib, model_base, decontam_prefs, trajectories, ai_interaction, scaler
)
_, pars_corr_final = compute_pars(
    model_corr, model_base, decontam_prefs, trajectories, ai_interaction, scaler
)
print(f"\nDeliberative PARS: {pars_delib:.4f} | Corrected PARS: {pars_corr_final:.4f}")


# ── Reward correlation per HF dataset ────────────────────────────────────────
# Evaluate reward model on HH-RLHF pairs
def eval_reward_on_hh(model, hh_pairs, hh_labels, scaler, n=200):
    model.eval()
    chosen_feats = text_to_features([p[0] for p in hh_pairs[:n]])
    reject_feats = text_to_features([p[1] for p in hh_pairs[:n]])
    Xc = torch.tensor(
        scaler.transform(chosen_feats[:, :N_PREF_DIMS]), dtype=torch.float32
    ).to(device)
    Xr = torch.tensor(
        scaler.transform(reject_feats[:, :N_PREF_DIMS]), dtype=torch.float32
    ).to(device)
    w = torch.zeros(n, dtype=torch.long).to(device)
    ai = torch.zeros(n, dtype=torch.float32).to(device)
    with torch.no_grad():
        rc, _ = model(Xc, w, ai)
        rr, _ = model(Xr, w, ai)
    pred_pref = (rc > rr).float().cpu().numpy()
    return float(np.mean(pred_pref == hh_labels[:n]))


hh_acc_base = eval_reward_on_hh(model_base, hh_pairs, hh_labels, scaler)
hh_acc_corr = eval_reward_on_hh(model_corr, hh_pairs, hh_labels, scaler)
print(
    f"HH-RLHF preference accuracy - Base: {hh_acc_base:.4f}, Corrected: {hh_acc_corr:.4f}"
)

# ── Plotting ──────────────────────────────────────────────────────────────────
epochs_used = len(experiment_data["hh_rlhf"]["losses"]["train"])
epochs_arr = np.arange(1, epochs_used + 1)

# Fig 1: Loss curves per dataset
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for di, (dsn, ax) in enumerate(zip(ds_names, axes)):
    ax.plot(
        epochs_arr,
        experiment_data[dsn]["losses"]["train"],
        label="Train",
        color="steelblue",
    )
    ax.plot(
        epochs_arr, experiment_data[dsn]["losses"]["val"], label="Val", color="orange"
    )
    ax.set_title(f"Loss: {dsn}")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss")
    ax.legend()
    ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "loss_curves_per_dataset.png"), dpi=120)
plt.close()

# Fig 2: PDAS baseline vs corrected
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
pdas_base_arr = np.array(experiment_data["combined"]["pdas_initial"])
pdas_corr_arr = np.array(experiment_data["combined"]["pdas_corrected"])
axes[0].plot(epochs_arr, pdas_base_arr, label="PDAS Baseline", color="red")
axes[0].plot(epochs_arr, pdas_corr_arr, label="PDAS Corrected", color="green")
axes[0].set_title("PDAS: Baseline vs Drift-Corrected")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("PDAS")
axes[0].legend()
axes[0].grid(True)
pars_arr = np.array(experiment_data["combined"]["pars_weighted"])
axes[1].plot(epochs_arr, pars_arr, label="PARS (weighted)", color="purple")
axes[1].axhline(0, linestyle="--", color="gray", alpha=0.7)
axes[1].set_title("PARS Over Training")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("PARS")
axes[1].legend()
axes[1].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pdas_and_pars_training.png"), dpi=120)
plt.close()

# Fig 3: Longitudinal drift
weeks = np.arange(1, N_WEEKS)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(weeks, long_pdas, marker="o", color="crimson", label="PDAS")
axes[0].set_xlabel("Week")
axes[0].set_ylabel("PDAS")
axes[0].set_title("Longitudinal PDAS (Sigmoid Drift)")
axes[0].legend()
axes[0].grid(True)
axes[1].plot(weeks, long_ai, marker="s", color="red", label="AI-induced shift")
axes[1].plot(weeks, long_tot, marker="^", color="steelblue", label="Total shift (std)")
axes[1].set_xlabel("Week")
axes[1].set_ylabel("Magnitude")
axes[1].set_title("Preference Shift Decomposition")
axes[1].legend()
axes[1].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "longitudinal_drift_decomposition.png"), dpi=120)
plt.close()

# Fig 4: PARS per domain
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
dp = experiment_data["combined"]["pars_per_domain"]
cols = ["steelblue", "orange", "green", "red"]
bars = axes[0].bar(list(dp.keys()), list(dp.values()), color=cols, edgecolor="black")
for bar, val in zip(bars, dp.values()):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=11,
    )
axes[0].axhline(0, color="gray", linestyle="--")
axes[0].set_title("PARS Per Domain")
axes[0].set_ylabel("PARS")
axes[0].grid(axis="y")

# Fig 4b: Drift AUROC val vs OOD
auroc_labels = ["Val AUROC", "OOD AUROC"]
auroc_vals = [drift_auroc_val, drift_auroc_ood]
b2 = axes[1].bar(
    auroc_labels, auroc_vals, color=["steelblue", "orange"], edgecolor="black"
)
for bar, val in zip(b2, auroc_vals):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{val:.4f}",
        ha="center",
        fontsize=12,
    )
axes[1].set_ylim(0, 1.1)
axes[1].set_title("Drift Classifier AUROC: Val vs OOD")
axes[1].grid(axis="y")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pars_per_domain.png"), dpi=120)
plt.close()

# Fig 5: Conditions comparison + HH-RLHF accuracy
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
conditions = ["Standard RLHF", "Drift-Corrected", "Deliberative"]
pars_conds = [0.0, pars_corr_final, pars_delib]
bar_c = ["gray", "green", "purple"]
b = axes[0].bar(conditions, pars_conds, color=bar_c, edgecolor="black")
for bar, val in zip(b, pars_conds):
    axes[0].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=11,
    )
axes[0].set_title("PARS by Condition")
axes[0].set_ylabel("PARS")
axes[0].grid(axis="y")

hh_labels_bar = ["Base Model", "Corrected Model"]
hh_acc_vals = [hh_acc_base, hh_acc_corr]
b2 = axes[1].bar(
    hh_labels_bar, hh_acc_vals, color=["steelblue", "green"], edgecolor="black"
)
for bar, val in zip(b2, hh_acc_vals):
    axes[1].text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=12,
    )
axes[1].set_ylim(0, 1.1)
axes[1].set_title("HH-RLHF Preference Accuracy")
axes[1].set_ylabel("Accuracy")
axes[1].grid(axis="y")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pars_conditions_and_auroc.png"), dpi=120)
plt.close()

# ── Save ──────────────────────────────────────────────────────────────────────
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print("\n=== FINAL SUMMARY ===")
print(f"Drift Classifier AUROC (val):  {drift_auroc_val:.4f}")
print(f"Drift Classifier AUROC (OOD):  {drift_auroc_ood:.4f}")
print(f"Final PDAS Baseline:           {pdas_base_arr[-1]:.4f}")
print(f"Final PDAS Corrected:          {pdas_corr_arr[-1]:.4f}")
print(f"PDAS Reduction:                {pdas_base_arr[-1]-pdas_corr_arr[-1]:.4f}")
print(f"Final PARS (weighted):         {pars_arr[-1]:.4f}")
print(
    f"PARS per domain:               {experiment_data['combined']['pars_per_domain']}"
)
print(f"Deliberative PARS:             {pars_delib:.4f}")
print(f"HH-RLHF Accuracy (base/corr):  {hh_acc_base:.4f} / {hh_acc_corr:.4f}")
print(f"Longitudinal PDAS weeks 1→7:   {[f'{p:.3f}' for p in long_pdas]}")
print("All outputs saved to:", working_dir)
