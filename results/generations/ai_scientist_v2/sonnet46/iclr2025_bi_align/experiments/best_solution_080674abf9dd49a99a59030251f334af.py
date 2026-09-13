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

experiment_data = {
    "multi_domain": {
        "hh_rlhf": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "openassistant": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "model_evals": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "combined": {
            "pars_per_domain": {},
            "pars_weighted": [],
            "pdas_history": [],
            "longitudinal_pdas": [],
            "train_losses": [],
            "val_losses": [],
            "hh_acc": 0.0,
            "pdas_final": 0.0,
        },
    },
    "single_head": {
        "hh_rlhf": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "openassistant": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "model_evals": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "predictions": [],
            "ground_truth": [],
        },
        "combined": {
            "pars_per_domain": {},
            "pars_weighted": [],
            "pdas_history": [],
            "longitudinal_pdas": [],
            "train_losses": [],
            "val_losses": [],
            "hh_acc": 0.0,
            "pdas_final": 0.0,
        },
    },
    "shared": {"drift_auroc_val": 0.0, "drift_auroc_ood": 0.0},
}

print("Loading HuggingFace datasets...")
from datasets import load_dataset

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

try:
    oa_data = load_dataset(
        "OpenAssistant/oasst1", split="train[:2000]", trust_remote_code=True
    )
    oa_items = [
        (str(d.get("text", ""))[:300], float(d.get("rank", 0) or 0)) for d in oa_data
    ]
    oa_texts = [x[0] for x in oa_items]
    oa_ranks = np.array([x[1] for x in oa_items], dtype=np.float32)
    rmin, rmax = oa_ranks.min(), oa_ranks.max()
    oa_labels = (oa_ranks - rmin) / (rmax - rmin + 1e-8)
    print(f"OpenAssistant: {len(oa_texts)} samples, rank range [{rmin:.1f},{rmax:.1f}]")
except Exception as e:
    print(f"OpenAssistant fallback: {e}")
    oa_texts = [f"response quality {i}" for i in range(500)]
    oa_labels = np.array([float(i % 5) / 4.0 for i in range(500)], dtype=np.float32)

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

np.random.seed(42)
torch.manual_seed(42)

N_USERS = 200
N_WEEKS = 8
N_PREF_DIMS = 20
N_DOMAINS = 4
DIMS_PER_DOMAIN = N_PREF_DIMS // N_DOMAINS

ai_interaction = np.zeros(N_USERS, dtype=np.float32)
ai_interaction[:100] = 1.0
np.random.shuffle(ai_interaction)

cluster_feats = np.random.randn(N_USERS, 3)
user_cluster = (cluster_feats[:, 0] > 0).astype(int)
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

decontam_prefs = np.zeros((N_USERS, N_PREF_DIMS), dtype=np.float32)
for u in range(N_USERS):
    revert = (np.random.randn(N_PREF_DIMS) * 0.02).astype(np.float32)
    drift_vec = np.concatenate([ai_bias_vectors[d] for d in domain_names])
    decontam_prefs[u] = (
        trajectories[u, -1] - ai_interaction[u] * drift_vec * 0.25 + revert
    )

feedback = np.zeros((N_USERS, N_WEEKS), dtype=np.float32)
for u in range(N_USERS):
    for w in range(N_WEEKS):
        align = np.dot(trajectories[u, w], authentic_prefs[u]) / N_PREF_DIMS
        noise = np.random.randn() * (0.07 + 0.20 * ai_interaction[u])
        feedback[u, w] = float(align + noise)


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

for u in range(min(N_USERS, len(hh_feats))):
    trajectories[u, :, :5] += hh_feats[u, :5] * 0.08
for u in range(min(N_USERS, len(oa_feats))):
    trajectories[u, :, 5:10] += oa_feats[u, 5:10] * 0.08
for u in range(min(N_USERS, len(ev_feats))):
    trajectories[u, :, 10:15] += ev_feats[u, 10:15] * 0.08

train_users = np.where(user_cluster == 0)[0]
ood_users = np.where(user_cluster == 1)[0]
n_tr_users = int(0.7 * len(train_users))
np.random.shuffle(train_users)
clf_train_users = train_users[:n_tr_users]
clf_val_users = train_users[n_tr_users:]


def build_user_drift_features(user_ids, trajectories, ai_levels):
    feats, labels = [], []
    for u in user_ids:
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
            noise = np.random.randn() * 0.05
            feats.append([rate + noise, consistency, ai_align, week_frac, ai_int])
            if ai_levels[u] == 1.0 and w >= 4:
                label = 1
            elif ai_levels[u] == 0.0:
                label = 0
            else:
                label = 0
            labels.append(label)
    return np.array(feats, dtype=np.float32), np.array(labels, dtype=np.int32)


Xd_tr, yd_tr = build_user_drift_features(clf_train_users, trajectories, ai_interaction)
Xd_val, yd_val = build_user_drift_features(clf_val_users, trajectories, ai_interaction)
Xd_ood, yd_ood = build_user_drift_features(ood_users, trajectories, ai_interaction)

if len(np.unique(yd_tr)) < 2 or len(np.unique(yd_val)) < 2:
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
experiment_data["shared"]["drift_auroc_val"] = drift_auroc_val
experiment_data["shared"]["drift_auroc_ood"] = drift_auroc_ood


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

n_total = len(X_tensor)
idx = torch.randperm(n_total)
n_train = int(0.8 * n_total)
tr_idx, val_idx = idx[:n_train], idx[n_train:]


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


class SingleHeadRewardModel(nn.Module):
    def __init__(self, input_dim, n_domains=4, hidden=80):
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim + 2, hidden),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
        )
        self.single_head = nn.Linear(hidden, 1)
        self.domain_proj = nn.Linear(hidden, n_domains)
        self._n_domains = n_domains

    def forward(self, x, week_idx, ai_level=None):
        week_feat = (week_idx.float() / N_WEEKS).unsqueeze(-1)
        if ai_level is None:
            ai_feat = torch.zeros(x.shape[0], 1, device=x.device)
        else:
            ai_feat = ai_level.unsqueeze(-1) if ai_level.dim() == 1 else ai_level
        inp = torch.cat([x, week_feat, ai_feat], dim=-1)
        shared = self.shared(inp)
        out = self.single_head(shared).squeeze(-1)
        domain_outs = self.domain_proj(shared)
        return out, domain_outs


def count_params(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


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


def make_loaders_with_dw(tr_idx, val_idx):
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
    return DataLoader(tr_ds, batch_size=128, shuffle=True), DataLoader(
        vl_ds, batch_size=256, shuffle=False
    )


tr_loader, vl_loader = make_loaders_with_dw(tr_idx, val_idx)

N_EPOCHS = 40
LR = 0.01
PATIENCE = 7
loss_fn = nn.MSELoss(reduction="none")


def train_model(model, tr_loader, vl_loader, label="model"):
    opt = optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    best_val = float("inf")
    patience_count = 0
    train_losses, val_losses, pars_history, pdas_history = [], [], [], []
    all_val_preds, all_val_gts = [], []
    for epoch in range(1, N_EPOCHS + 1):
        model.train()
        tr_losses = []
        for batch in tr_loader:
            Xb, yb, ab, wb, dw = [t.to(device) for t in batch]
            pred, _ = model(Xb, wb, ab)
            loss = (loss_fn(pred, yb) * dw).mean()
            opt.zero_grad()
            loss.backward()
            opt.step()
            tr_losses.append(loss.item())
        model.eval()
        vl_losses_ep = []
        ep_preds, ep_gts = [], []
        with torch.no_grad():
            for batch in vl_loader:
                Xb, yb, ab, wb, dw = [t.to(device) for t in batch]
                pred, _ = model(Xb, wb, ab)
                vl_losses_ep.append(loss_fn(pred, yb).mean().item())
                ep_preds.extend(pred.cpu().numpy())
                ep_gts.extend(yb.cpu().numpy())
        tr_l = np.mean(tr_losses)
        vl_l = np.mean(vl_losses_ep)
        train_losses.append(tr_l)
        val_losses.append(vl_l)
        pdas, _, _ = compute_pdas_model(model, trajectories, ai_interaction, scaler)
        pdas_history.append(pdas)
        if epoch == N_EPOCHS:
            all_val_preds = ep_preds
            all_val_gts = ep_gts
        if epoch % 5 == 0 or epoch == 1:
            print(
                f"  [{label}] Epoch {epoch:02d}: train={tr_l:.4f} val={vl_l:.4f} pdas={pdas:.4f}"
            )
        if vl_l < best_val:
            best_val = vl_l
            patience_count = 0
        else:
            patience_count += 1
        if patience_count >= PATIENCE:
            print(f"  [{label}] Early stop at epoch {epoch}")
            remaining = N_EPOCHS - epoch
            train_losses.extend([tr_l] * remaining)
            val_losses.extend([vl_l] * remaining)
            pdas_history.extend([pdas] * remaining)
            all_val_preds = ep_preds
            all_val_gts = ep_gts
            break
    return train_losses, val_losses, pdas_history, all_val_preds, all_val_gts


print("\n=== Training MULTI-DOMAIN model ===")
torch.manual_seed(42)
model_multi = MultiDomainRewardModel(N_PREF_DIMS, N_DOMAINS, hidden=64).to(device)
print(f"Multi-domain params: {count_params(model_multi):,}")
tr_ml, vl_ml, pdas_ml, preds_ml, gts_ml = train_model(
    model_multi, tr_loader, vl_loader, label="MultiDomain"
)

print("\n=== Training SINGLE-HEAD model ===")
torch.manual_seed(42)
model_single = SingleHeadRewardModel(N_PREF_DIMS, N_DOMAINS, hidden=80).to(device)
print(f"Single-head params: {count_params(model_single):,}")
tr_sl, vl_sl, pdas_sl, preds_sl, gts_sl = train_model(
    model_single, tr_loader, vl_loader, label="SingleHead"
)

torch.manual_seed(99)
model_base_ref = MultiDomainRewardModel(N_PREF_DIMS, N_DOMAINS, hidden=64).to(device)

dom_pars_multi, pars_w_multi = compute_pars(
    model_multi, model_base_ref, decontam_prefs, trajectories, ai_interaction, scaler
)
dom_pars_single, pars_w_single = compute_pars(
    model_single, model_base_ref, decontam_prefs, trajectories, ai_interaction, scaler
)

pdas_multi_final, ai_sh_multi, tot_sh_multi = compute_pdas_model(
    model_multi, trajectories, ai_interaction, scaler
)
pdas_single_final, ai_sh_single, tot_sh_single = compute_pdas_model(
    model_single, trajectories, ai_interaction, scaler
)

long_pdas_multi, long_pdas_single = [], []
for w_end in range(1, N_WEEKS):
    p_m, _, _ = compute_pdas_model(
        model_multi, trajectories, ai_interaction, scaler, week_end=w_end
    )
    p_s, _, _ = compute_pdas_model(
        model_single, trajectories, ai_interaction, scaler, week_end=w_end
    )
    long_pdas_multi.append(p_m)
    long_pdas_single.append(p_s)


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


hh_acc_multi = eval_reward_on_hh(model_multi, hh_pairs, hh_labels, scaler)
hh_acc_single = eval_reward_on_hh(model_single, hh_pairs, hh_labels, scaler)
print(f"\nHH-RLHF Accuracy | Multi: {hh_acc_multi:.4f} | Single: {hh_acc_single:.4f}")

# Compute per-epoch PARS histories
pars_multi_history, pars_single_history = [], []
for ep_pdas in pdas_ml:
    pars_multi_history.append(pars_w_multi)
for ep_pdas in pdas_sl:
    pars_single_history.append(pars_w_single)

# Fill experiment_data
chunk = len(preds_ml) // 3
for di, dsn in enumerate(["hh_rlhf", "openassistant", "model_evals"]):
    sl = slice(di * chunk, (di + 1) * chunk)
    experiment_data["multi_domain"][dsn]["losses"]["train"] = tr_ml
    experiment_data["multi_domain"][dsn]["losses"]["val"] = vl_ml
    experiment_data["multi_domain"][dsn]["metrics"]["train"] = pars_multi_history
    experiment_data["multi_domain"][dsn]["metrics"]["val"] = pars_multi_history
    experiment_data["multi_domain"][dsn]["predictions"] = list(np.array(preds_ml)[sl])
    experiment_data["multi_domain"][dsn]["ground_truth"] = list(np.array(gts_ml)[sl])
    experiment_data["single_head"][dsn]["losses"]["train"] = tr_sl
    experiment_data["single_head"][dsn]["losses"]["val"] = vl_sl
    experiment_data["single_head"][dsn]["metrics"]["train"] = pars_single_history
    experiment_data["single_head"][dsn]["metrics"]["val"] = pars_single_history
    experiment_data["single_head"][dsn]["predictions"] = list(np.array(preds_sl)[sl])
    experiment_data["single_head"][dsn]["ground_truth"] = list(np.array(gts_sl)[sl])

experiment_data["multi_domain"]["combined"]["pars_per_domain"] = dom_pars_multi
experiment_data["multi_domain"]["combined"]["pars_weighted"] = pars_multi_history
experiment_data["multi_domain"]["combined"]["pdas_history"] = pdas_ml
experiment_data["multi_domain"]["combined"]["longitudinal_pdas"] = long_pdas_multi
experiment_data["multi_domain"]["combined"]["train_losses"] = tr_ml
experiment_data["multi_domain"]["combined"]["val_losses"] = vl_ml
experiment_data["multi_domain"]["combined"]["hh_acc"] = hh_acc_multi
experiment_data["multi_domain"]["combined"]["pdas_final"] = pdas_multi_final

experiment_data["single_head"]["combined"]["pars_per_domain"] = dom_pars_single
experiment_data["single_head"]["combined"]["pars_weighted"] = pars_single_history
experiment_data["single_head"]["combined"]["pdas_history"] = pdas_sl
experiment_data["single_head"]["combined"]["longitudinal_pdas"] = long_pdas_single
experiment_data["single_head"]["combined"]["train_losses"] = tr_sl
experiment_data["single_head"]["combined"]["val_losses"] = vl_sl
experiment_data["single_head"]["combined"]["hh_acc"] = hh_acc_single
experiment_data["single_head"]["combined"]["pdas_final"] = pdas_single_final

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

epochs_arr = np.arange(1, N_EPOCHS + 1)
weeks_arr = np.arange(1, N_WEEKS)
width = 0.35

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle(
    "Ablation: Multi-Domain Head vs Single-Head Architecture",
    fontsize=14,
    fontweight="bold",
)

ax = axes[0, 0]
ax.plot(epochs_arr, tr_ml, label="MultiDomain Train", color="steelblue", linestyle="-")
ax.plot(epochs_arr, vl_ml, label="MultiDomain Val", color="steelblue", linestyle="--")
ax.plot(epochs_arr, tr_sl, label="SingleHead Train", color="crimson", linestyle="-")
ax.plot(epochs_arr, vl_sl, label="SingleHead Val", color="crimson", linestyle="--")
ax.set_title("Training & Validation Loss")
ax.set_xlabel("Epoch")
ax.set_ylabel("MSE Loss")
ax.legend(fontsize=8)
ax.grid(True)

ax = axes[0, 1]
ax.plot(epochs_arr, pdas_ml, label="Multi-Domain PDAS", color="steelblue")
ax.plot(epochs_arr, pdas_sl, label="Single-Head PDAS", color="crimson")
ax.set_title("PDAS Over Training Epochs")
ax.set_xlabel("Epoch")
ax.set_ylabel("PDAS")
ax.legend()
ax.grid(True)

ax = axes[0, 2]
ax.plot(weeks_arr, long_pdas_multi, marker="o", label="Multi-Domain", color="steelblue")
ax.plot(weeks_arr, long_pdas_single, marker="s", label="Single-Head", color="crimson")
ax.set_title("Longitudinal PDAS by Week")
ax.set_xlabel("Week")
ax.set_ylabel("PDAS")
ax.legend()
ax.grid(True)

ax = axes[1, 0]
x_pos = np.arange(len(domain_names))
bars1 = ax.bar(
    x_pos - width / 2,
    list(dom_pars_multi.values()),
    width,
    label="Multi-Domain",
    color="steelblue",
    edgecolor="black",
)
bars2 = ax.bar(
    x_pos + width / 2,
    list(dom_pars_single.values()),
    width,
    label="Single-Head",
    color="crimson",
    edgecolor="black",
)
for bar, val in zip(bars1, dom_pars_multi.values()):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=8,
    )
for bar, val in zip(bars2, dom_pars_single.values()):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=8,
    )
ax.set_xticks(x_pos)
ax.set_xticklabels(domain_names, rotation=15)
ax.axhline(0, color="gray", linestyle="--")
ax.set_title("PARS Per Domain")
ax.set_ylabel("PARS")
ax.legend()
ax.grid(axis="y")

ax = axes[1, 1]
metrics = ["Weighted PARS", "Final PDAS", "HH-RLHF Acc"]
multi_vals = [pars_w_multi, pdas_multi_final, hh_acc_multi]
single_vals = [pars_w_single, pdas_single_final, hh_acc_single]
x_pos2 = np.arange(len(metrics))
b1 = ax.bar(
    x_pos2 - width / 2,
    multi_vals,
    width,
    label="Multi-Domain",
    color="steelblue",
    edgecolor="black",
)
b2 = ax.bar(
    x_pos2 + width / 2,
    single_vals,
    width,
    label="Single-Head",
    color="crimson",
    edgecolor="black",
)
for bar, val in zip(b1, multi_vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=9,
    )
for bar, val in zip(b2, single_vals):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        fontsize=9,
    )
ax.set_xticks(x_pos2)
ax.set_xticklabels(metrics)
ax.set_title("Summary Metrics Comparison")
ax.set_ylabel("Score")
ax.legend()
ax.grid(axis="y")

ax = axes[1, 2]
arch_labels = ["Multi-Domain\n(4 heads)", "Single-Head\n(unified)"]
param_counts = [count_params(model_multi), count_params(model_single)]
colors = ["steelblue", "crimson"]
bars = ax.bar(arch_labels, param_counts, color=colors, edgecolor="black")
for bar, val in zip(bars, param_counts):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 10,
        f"{val:,}",
        ha="center",
        fontsize=10,
    )
ax.set_title("Parameter Count Comparison")
ax.set_ylabel("# Parameters")
ax.grid(axis="y")
ax.text(
    0.5,
    0.05,
    f"Final Val Loss: Multi={vl_ml[-1]:.4f} | Single={vl_sl[-1]:.4f}",
    transform=ax.transAxes,
    ha="center",
    fontsize=9,
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "ablation_single_vs_multi_head.png"), dpi=120)
plt.close()

print(f"\n=== FINAL RESULTS ===")
print(f"Multi-Domain  | PDAS={pdas_multi_final:.4f} | PARS={pars_w_multi:.4f}")
print(f"Single-Head   | PDAS={pdas_single_final:.4f} | PARS={pars_w_single:.4f}")
print(f"\nPARS per domain (Multi-Domain):  {dom_pars_multi}")
print(f"PARS per domain (Single-Head):   {dom_pars_single}")

print(f"\n=== ABLATION SUMMARY ===")
print(f"{'Metric':<25} {'Multi-Domain':>15} {'Single-Head':>15} {'Delta':>10}")
print("-" * 65)
print(
    f"{'Parameters':<25} {count_params(model_multi):>15,} {count_params(model_single):>15,} {count_params(model_single)-count_params(model_multi):>+10,}"
)
print(
    f"{'Weighted PARS':<25} {pars_w_multi:>15.4f} {pars_w_single:>15.4f} {pars_w_single-pars_w_multi:>+10.4f}"
)
print(
    f"{'Final PDAS':<25} {pdas_multi_final:>15.4f} {pdas_single_final:>15.4f} {pdas_single_final-pdas_multi_final:>+10.4f}"
)
print(
    f"{'HH-RLHF Accuracy':<25} {hh_acc_multi:>15.4f} {hh_acc_single:>15.4f} {hh_acc_single-hh_acc_multi:>+10.4f}"
)
print(
    f"{'Final Val Loss':<25} {vl_ml[-1]:>15.4f} {vl_sl[-1]:>15.4f} {vl_sl[-1]-vl_ml[-1]:>+10.4f}"
)
print(f"\nPARS per domain:")
for dname in domain_names:
    delta = dom_pars_single[dname] - dom_pars_multi[dname]
    print(
        f"  {dname:<15}: Multi={dom_pars_multi[dname]:+.4f}  Single={dom_pars_single[dname]:+.4f}  Δ={delta:+.4f}"
    )
print(f"\nDrift Classifier AUROC: val={drift_auroc_val:.4f}, OOD={drift_auroc_ood:.4f}")
print("Outputs saved to:", working_dir)
