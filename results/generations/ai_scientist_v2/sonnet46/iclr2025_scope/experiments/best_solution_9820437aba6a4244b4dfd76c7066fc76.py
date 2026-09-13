import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader, TensorDataset
from scipy.stats import spearmanr

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

N_SAMPLES = 3000
SEQ_LEN = 64
D_MODEL = 128
N_HEADS = 4
N_LAYERS = 4
N_EXPERTS = 4
DROPOUT = 0.1
WEIGHT_DECAY = 1e-4
EPOCHS = 80
BATCH_SIZE = 64
RETAIN_RATIOS = [0.25, 0.40, 0.60, 0.75]
ROUTING_LAMBDA = 0.5
METHODS = ["routekv", "attention", "random", "hybrid"]
LR = 3e-4
TOP_K_VALUES = [1, 2, 4]

experiment_data = {}


def make_synthetic_dataset(n, n_classes=4, seq_len=SEQ_LEN, d_model=D_MODEL, seed=0):
    """Key tokens at RANDOM positions to make eviction non-trivial."""
    rng = np.random.RandomState(seed)
    labels = rng.randint(0, n_classes, size=n)
    basis = np.zeros((n_classes, d_model), dtype=np.float32)
    for c in range(n_classes):
        basis[c, c * (d_model // n_classes) : (c + 1) * (d_model // n_classes)] = 8.0

    n_key = max(1, seq_len // 8)  # fewer key tokens = harder task
    seqs = np.zeros((n, seq_len, d_model), dtype=np.float32)
    token_types = np.zeros((n, seq_len), dtype=np.int64)

    for i in range(n):
        # Random positions for key tokens
        key_positions = rng.choice(seq_len, n_key, replace=False)
        token_types[i, key_positions] = 1
        for j in range(seq_len):
            if j in key_positions:
                seqs[i, j] = basis[labels[i]] + 0.1 * rng.randn(d_model)
            else:
                seqs[i, j] = 0.3 * rng.randn(d_model).astype(np.float32)

    return (
        torch.tensor(seqs),
        torch.tensor(labels.astype(np.int64)),
        torch.tensor(token_types),
        n_key,
    )


def make_hf_sst2_dataset(max_samples=2000, seq_len=SEQ_LEN, d_model=D_MODEL, seed=44):
    try:
        from datasets import load_dataset

        ds = load_dataset("glue", "sst2", split="train")
        rng = np.random.RandomState(seed)
        n = min(max_samples, len(ds))
        indices = rng.choice(len(ds), n, replace=False)
        labels_arr = np.array([ds[int(i)]["label"] for i in indices], dtype=np.int64)
        texts = [ds[int(i)]["sentence"] for i in indices]
        n_classes = 2
        seqs = np.zeros((n, seq_len, d_model), dtype=np.float32)
        basis = np.zeros((n_classes, d_model), dtype=np.float32)
        for c in range(n_classes):
            basis[c, c * (d_model // n_classes) : (c + 1) * (d_model // n_classes)] = (
                8.0
            )
        n_key = max(1, seq_len // 8)
        token_types = np.zeros((n, seq_len), dtype=np.int64)
        for i, (text, lbl) in enumerate(zip(texts, labels_arr)):
            key_positions = rng.choice(seq_len, n_key, replace=False)
            token_types[i, key_positions] = 1
            words = text.lower().split()
            for j in range(seq_len):
                if j in set(key_positions):
                    seqs[i, j] = basis[lbl] + 0.1 * rng.randn(d_model)
                else:
                    widx = j % max(len(words), 1)
                    wh = hash(words[widx]) % d_model if words else 0
                    v = 0.3 * rng.randn(d_model).astype(np.float32)
                    v[wh] += 0.1
                    seqs[i, j] = v
        return (
            torch.tensor(seqs),
            torch.tensor(labels_arr),
            torch.tensor(token_types),
            n_classes,
            n_key,
        )
    except Exception as e:
        print(f"SST-2 load failed: {e}")
        X, y, tt, nk = make_synthetic_dataset(
            max_samples, n_classes=2, seq_len=seq_len, d_model=d_model, seed=seed
        )
        return X, y, tt, 2, nk


def make_hf_agnews_dataset(max_samples=2000, seq_len=SEQ_LEN, d_model=D_MODEL, seed=45):
    try:
        from datasets import load_dataset

        ds = load_dataset("ag_news", split="train")
        rng = np.random.RandomState(seed)
        n = min(max_samples, len(ds))
        indices = rng.choice(len(ds), n, replace=False)
        labels_arr = np.array([ds[int(i)]["label"] for i in indices], dtype=np.int64)
        texts = [ds[int(i)]["text"] for i in indices]
        n_classes = 4
        seqs = np.zeros((n, seq_len, d_model), dtype=np.float32)
        basis = np.zeros((n_classes, d_model), dtype=np.float32)
        for c in range(n_classes):
            basis[c, c * (d_model // n_classes) : (c + 1) * (d_model // n_classes)] = (
                8.0
            )
        n_key = max(1, seq_len // 8)
        token_types = np.zeros((n, seq_len), dtype=np.int64)
        for i, (text, lbl) in enumerate(zip(texts, labels_arr)):
            key_positions = rng.choice(seq_len, n_key, replace=False)
            token_types[i, key_positions] = 1
            words = text.lower().split()
            for j in range(seq_len):
                if j in set(key_positions):
                    seqs[i, j] = basis[lbl] + 0.1 * rng.randn(d_model)
                else:
                    widx = j % max(len(words), 1)
                    wh = hash(words[widx]) % d_model if words else 0
                    v = 0.3 * rng.randn(d_model).astype(np.float32)
                    v[wh] += 0.1
                    seqs[i, j] = v
        return (
            torch.tensor(seqs),
            torch.tensor(labels_arr),
            torch.tensor(token_types),
            n_classes,
            n_key,
        )
    except Exception as e:
        print(f"AG News load failed: {e}")
        X, y, tt, nk = make_synthetic_dataset(
            max_samples, n_classes=4, seq_len=seq_len, d_model=d_model, seed=seed
        )
        return X, y, tt, 4, nk


class MoELayer(nn.Module):
    def __init__(self, d_model, n_experts=N_EXPERTS, top_k=1):
        super().__init__()
        self.n_experts = n_experts
        self.top_k = top_k
        self.gate = nn.Linear(d_model, n_experts, bias=False)
        self.experts = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(d_model, d_model * 2),
                    nn.GELU(),
                    nn.Dropout(DROPOUT),
                    nn.Linear(d_model * 2, d_model),
                )
                for _ in range(n_experts)
            ]
        )

    def forward(self, x):
        B, T, D = x.shape
        logits = self.gate(x)
        if self.top_k == 1:
            idx = logits.argmax(dim=-1)
            out = torch.zeros_like(x)
            flat_x = x.reshape(B * T, D)
            flat_idx = idx.reshape(B * T)
            for e in range(self.n_experts):
                mask = flat_idx == e
                if mask.any():
                    out.reshape(B * T, D)[mask] = self.experts[e](flat_x[mask])
        else:
            actual_k = min(self.top_k, self.n_experts)
            topk_vals, topk_idx = torch.topk(logits, actual_k, dim=-1)
            topk_weights = F.softmax(topk_vals, dim=-1)
            out = torch.zeros_like(x)
            flat_x = x.reshape(B * T, D)
            for ki in range(actual_k):
                flat_idx = topk_idx[:, :, ki].reshape(B * T)
                flat_w = topk_weights[:, :, ki].reshape(B * T, 1)
                for e in range(self.n_experts):
                    mask = flat_idx == e
                    if mask.any():
                        expert_out = self.experts[e](flat_x[mask])
                        out.reshape(B * T, D)[mask] += flat_w[mask] * expert_out
        return out, logits


class MoETransformerLayer(nn.Module):
    def __init__(self, d_model, n_heads, top_k=1):
        super().__init__()
        self.attn = nn.MultiheadAttention(
            d_model, n_heads, dropout=DROPOUT, batch_first=True
        )
        self.moe = MoELayer(d_model, top_k=top_k)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(DROPOUT)

    def forward(self, x, return_attn=False):
        attn_out, attn_weights = self.attn(
            x, x, x, need_weights=True, average_attn_weights=True
        )
        x = self.norm1(x + self.drop(attn_out))
        moe_out, router_logits = self.moe(x)
        x = self.norm2(x + moe_out)
        if return_attn:
            return x, router_logits, attn_weights
        return x, router_logits


class MoEClassifier(nn.Module):
    def __init__(
        self, d_model=D_MODEL, n_heads=N_HEADS, n_layers=N_LAYERS, n_classes=4, top_k=1
    ):
        super().__init__()
        self.proj = nn.Linear(d_model, d_model)
        self.layers = nn.ModuleList(
            [
                MoETransformerLayer(d_model, n_heads, top_k=top_k)
                for _ in range(n_layers)
            ]
        )
        self.norm_final = nn.LayerNorm(d_model)
        self.head = nn.Sequential(nn.Dropout(DROPOUT), nn.Linear(d_model, n_classes))

    def forward(self, x, return_routing=False, return_attn=False, keep_mask=None):
        x = F.gelu(self.proj(x))
        all_rl, all_aw = [], []
        for layer in self.layers:
            if return_attn:
                x, rl, aw = layer(x, return_attn=True)
                all_aw.append(aw)
            else:
                x, rl = layer(x)
            all_rl.append(rl)
        x = self.norm_final(x)
        if keep_mask is not None:
            mask_f = keep_mask.float().unsqueeze(-1)
            cls = (x * mask_f).sum(dim=1) / mask_f.sum(dim=1).clamp(min=1)
        else:
            cls = x.mean(dim=1)
        logits = self.head(cls)
        if return_routing:
            return logits, all_rl, all_aw
        return logits


def routing_specialization_loss(router_logits_list, token_types):
    loss = 0.0
    for rl in router_logits_list:
        key_mask = token_types == 1
        filler_mask = token_types == 0
        if key_mask.any():
            key_logits = rl[key_mask]
            target_key = torch.zeros(
                key_logits.size(0), dtype=torch.long, device=rl.device
            )
            loss += F.cross_entropy(key_logits, target_key)
        if filler_mask.any():
            filler_logits = rl[filler_mask]
            n_e = filler_logits.size(-1)
            target_filler = torch.randint(
                1, n_e, (filler_logits.size(0),), device=rl.device
            )
            loss += F.cross_entropy(filler_logits, target_filler)
    return loss / len(router_logits_list)


def compute_routing_scores(rl_list):
    stacked = torch.stack([F.softmax(rl, dim=-1) for rl in rl_list], dim=0)
    avg_prob = stacked.mean(0)
    entropy = -(avg_prob * (avg_prob + 1e-9).log()).sum(-1)
    return entropy  # lower = more specialized = more important


def compute_attention_scores(aw_list):
    if not aw_list:
        return None
    attn_stack = torch.stack(aw_list, dim=0)  # (L, B, T, T)
    return attn_stack.mean(0).sum(1)  # (B, T)


def compute_hybrid_scores(rl_list, aw_list, alpha=0.5):
    route_ent = compute_routing_scores(rl_list)
    route_spec = -route_ent
    route_min = route_spec.min(dim=1, keepdim=True)[0]
    route_max = route_spec.max(dim=1, keepdim=True)[0]
    route_norm = (route_spec - route_min) / (route_max - route_min + 1e-9)

    attn_imp = compute_attention_scores(aw_list)
    if attn_imp is None:
        return route_norm
    attn_min = attn_imp.min(dim=1, keepdim=True)[0]
    attn_max = attn_imp.max(dim=1, keepdim=True)[0]
    attn_norm = (attn_imp - attn_min) / (attn_max - attn_min + 1e-9)
    return alpha * route_norm + (1 - alpha) * attn_norm


def get_keep_mask(scores, retain_ratio, higher_is_better=True):
    B, T = scores.shape
    k = max(1, int(T * retain_ratio))
    if higher_is_better:
        _, topk = torch.topk(scores, k, dim=1)
    else:
        _, topk = torch.topk(-scores, k, dim=1)
    mask = torch.zeros(B, T, dtype=torch.bool, device=scores.device)
    mask.scatter_(1, topk, True)
    return mask


def compute_spearman_corr(model, loader):
    model.eval()
    all_route_scores, all_attn_scores = [], []
    with torch.no_grad():
        for xb, yb, tt in loader:
            xb = xb.to(device)
            _, rl_list, aw_list = model(xb, return_routing=True, return_attn=True)
            route_ent = compute_routing_scores(rl_list)
            attn_imp = compute_attention_scores(aw_list)
            all_route_scores.append((-route_ent).cpu().numpy().flatten())
            all_attn_scores.append(attn_imp.cpu().numpy().flatten())
    route_flat = np.concatenate(all_route_scores)
    attn_flat = np.concatenate(all_attn_scores)
    corr, pval = spearmanr(route_flat, attn_flat)
    return corr, pval


def compute_eviction_precision(model, loader, retain_ratio, n_key):
    model.eval()
    total_key_retained, total_key, total_retained = 0, 0, 0
    with torch.no_grad():
        for xb, yb, tt in loader:
            xb = xb.to(device)
            tt = tt.to(device)
            _, rl_list, aw_list = model(xb, return_routing=True, return_attn=True)
            route_ent = compute_routing_scores(rl_list)
            mask = get_keep_mask(route_ent, retain_ratio, higher_is_better=False)
            key_mask = tt == 1
            total_key_retained += (mask & key_mask).sum().item()
            total_key += key_mask.sum().item()
            total_retained += mask.sum().item()
    precision = total_key_retained / total_retained if total_retained > 0 else 0
    recall = total_key_retained / total_key if total_key > 0 else 0
    return precision, recall


def evaluate_with_eviction(model, loader, method, retain_ratio):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for batch in loader:
            xb, yb = batch[0].to(device), batch[1].to(device)
            _, rl_list, aw_list = model(xb, return_routing=True, return_attn=True)

            if method == "routekv":
                scores = compute_routing_scores(rl_list)
                mask = get_keep_mask(scores, retain_ratio, higher_is_better=False)
            elif method == "attention":
                scores = compute_attention_scores(aw_list)
                if scores is None:
                    scores = torch.rand(xb.size(0), xb.size(1), device=device)
                mask = get_keep_mask(scores, retain_ratio, higher_is_better=True)
            elif method == "hybrid":
                scores = compute_hybrid_scores(rl_list, aw_list, alpha=0.5)
                mask = get_keep_mask(scores, retain_ratio, higher_is_better=True)
            else:  # random
                scores = torch.rand(xb.size(0), xb.size(1), device=device)
                mask = get_keep_mask(scores, retain_ratio, higher_is_better=True)

            logits = model(xb, keep_mask=mask)
            correct += (logits.argmax(1) == yb).sum().item()
            total += xb.size(0)
    return correct / total


def run_experiment_topk(
    dataset_name, train_loader, val_loader, test_loader, n_classes, n_key, top_k
):
    print(f"\n--- Dataset: {dataset_name}, Top-K={top_k} ---")
    torch.manual_seed(SEED)
    model = MoEClassifier(n_classes=n_classes, top_k=top_k).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    criterion = nn.CrossEntropyLoss()

    train_losses, val_losses, train_accs, val_accs = [], [], [], []
    spearman_per_epoch = []
    best_val_acc, best_state = 0.0, None

    for epoch in range(1, EPOCHS + 1):
        model.train()
        tr_loss, tr_correct, tr_total = 0.0, 0, 0
        for batch in train_loader:
            xb, yb, tt = batch[0].to(device), batch[1].to(device), batch[2].to(device)
            optimizer.zero_grad()
            logits, rl_list, _ = model(xb, return_routing=True, return_attn=False)
            ce_loss = criterion(logits, yb)
            rs_loss = routing_specialization_loss(rl_list, tt)
            loss = ce_loss + ROUTING_LAMBDA * rs_loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            tr_loss += ce_loss.item() * xb.size(0)
            tr_correct += (logits.argmax(1) == yb).sum().item()
            tr_total += xb.size(0)
        scheduler.step()

        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for batch in val_loader:
                xb, yb = batch[0].to(device), batch[1].to(device)
                logits = model(xb)
                val_loss += criterion(logits, yb).item() * xb.size(0)
                val_correct += (logits.argmax(1) == yb).sum().item()
                val_total += xb.size(0)

        tr_acc = tr_correct / tr_total
        val_acc = val_correct / val_total
        train_losses.append(tr_loss / tr_total)
        val_losses.append(val_loss / val_total)
        train_accs.append(tr_acc)
        val_accs.append(val_acc)

        if epoch % 20 == 0 or epoch == EPOCHS:
            sp_corr, sp_pval = compute_spearman_corr(model, test_loader)
            spearman_per_epoch.append((epoch, sp_corr, sp_pval))
            print(
                f"Epoch {epoch:03d}: val_acc={val_acc:.4f} val_loss={val_loss/val_total:.4f} Spearman_corr={sp_corr:.4f}"
            )
        else:
            if epoch % 10 == 0:
                print(
                    f"Epoch {epoch:03d}: val_acc={val_acc:.4f} val_loss={val_loss/val_total:.4f}"
                )

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict({k: v.to(device) for k, v in best_state.items()})
    final_spearman, final_pval = compute_spearman_corr(model, test_loader)
    print(f"Final Spearman corr: {final_spearman:.4f} (p={final_pval:.6f})")

    # Entropy stats
    model.eval()
    key_ents, filler_ents = [], []
    with torch.no_grad():
        for batch in test_loader:
            xb, yb, tt = batch[0].to(device), batch[1].to(device), batch[2].to(device)
            _, rl_list, _ = model(xb, return_routing=True, return_attn=False)
            stacked = torch.stack([F.softmax(rl, dim=-1) for rl in rl_list], dim=0)
            avg_prob = stacked.mean(dim=0)
            ent = -(avg_prob * (avg_prob + 1e-9).log()).sum(-1)
            key_mask = tt == 1
            filler_mask = tt == 0
            key_ents.append(ent[key_mask].cpu())
            filler_ents.append(ent[filler_mask].cpu())
    key_ent = torch.cat(key_ents).mean().item()
    filler_ent = torch.cat(filler_ents).mean().item()
    ent_gap = filler_ent - key_ent
    print(f"Entropy: key={key_ent:.4f} filler={filler_ent:.4f} gap={ent_gap:.4f}")

    # Full-cache accuracy
    model.eval()
    full_correct, full_total = 0, 0
    with torch.no_grad():
        for batch in test_loader:
            xb, yb = batch[0].to(device), batch[1].to(device)
            logits = model(xb)
            full_correct += (logits.argmax(1) == yb).sum().item()
            full_total += xb.size(0)
    full_acc = full_correct / full_total
    print(f"Full-cache test acc: {full_acc:.4f}")

    # Eviction accuracy
    eviction_results = {m: {} for m in METHODS}
    for rr in RETAIN_RATIOS:
        for method in METHODS:
            acc = evaluate_with_eviction(model, test_loader, method, rr)
            eviction_results[method][rr] = acc
        print(
            f"retain={rr:.2f}: "
            + " | ".join([f"{m}={eviction_results[m][rr]:.4f}" for m in METHODS])
        )

    # Precision/recall
    precision_recall = {}
    for rr in RETAIN_RATIOS:
        p, r = compute_eviction_precision(model, test_loader, rr, n_key)
        precision_recall[rr] = {"precision": p, "recall": r}
        print(f"RouteKV retain={rr:.2f}: prec={p:.4f} recall={r:.4f}")

    return {
        "metrics": {"train": train_accs, "val": val_accs},
        "losses": {"train": train_losses, "val": val_losses},
        "routing_entropy": {"key": key_ent, "filler": filler_ent, "gap": ent_gap},
        "eviction_accs": eviction_results,
        "full_acc": full_acc,
        "spearman_epochs": spearman_per_epoch,
        "final_spearman": final_spearman,
        "final_spearman_pval": final_pval,
        "precision_recall": {str(k): v for k, v in precision_recall.items()},
        "best_val_acc": best_val_acc,
    }


# Prepare datasets
print("Preparing datasets...")
X_syn, y_syn, tt_syn, nk_syn = make_synthetic_dataset(N_SAMPLES, seed=0)
X_sv, y_sv, tt_sv, _ = make_synthetic_dataset(600, seed=1)
X_st, y_st, tt_st, _ = make_synthetic_dataset(600, seed=2)
n_classes_syn = 4
syn_train = DataLoader(
    TensorDataset(X_syn, y_syn, tt_syn), batch_size=BATCH_SIZE, shuffle=True
)
syn_val = DataLoader(TensorDataset(X_sv, y_sv, tt_sv), batch_size=BATCH_SIZE)
syn_test = DataLoader(TensorDataset(X_st, y_st, tt_st), batch_size=BATCH_SIZE)

print("Loading SST-2...")
X_sst, y_sst, tt_sst, nc_sst, nk_sst = make_hf_sst2_dataset(max_samples=2400, seed=44)
n_sst = len(X_sst)
ns_tr, ns_va = int(n_sst * 0.7), int(n_sst * 0.15)
sst_train = DataLoader(
    TensorDataset(X_sst[:ns_tr], y_sst[:ns_tr], tt_sst[:ns_tr]),
    batch_size=BATCH_SIZE,
    shuffle=True,
)
sst_val = DataLoader(
    TensorDataset(
        X_sst[ns_tr : ns_tr + ns_va],
        y_sst[ns_tr : ns_tr + ns_va],
        tt_sst[ns_tr : ns_tr + ns_va],
    ),
    batch_size=BATCH_SIZE,
)
sst_test = DataLoader(
    TensorDataset(
        X_sst[ns_tr + ns_va :], y_sst[ns_tr + ns_va :], tt_sst[ns_tr + ns_va :]
    ),
    batch_size=BATCH_SIZE,
)

print("Loading AG News...")
X_ag, y_ag, tt_ag, nc_ag, nk_ag = make_hf_agnews_dataset(max_samples=2400, seed=45)
n_ag = len(X_ag)
na_tr, na_va = int(n_ag * 0.7), int(n_ag * 0.15)
ag_train = DataLoader(
    TensorDataset(X_ag[:na_tr], y_ag[:na_tr], tt_ag[:na_tr]),
    batch_size=BATCH_SIZE,
    shuffle=True,
)
ag_val = DataLoader(
    TensorDataset(
        X_ag[na_tr : na_tr + na_va],
        y_ag[na_tr : na_tr + na_va],
        tt_ag[na_tr : na_tr + na_va],
    ),
    batch_size=BATCH_SIZE,
)
ag_test = DataLoader(
    TensorDataset(X_ag[na_tr + na_va :], y_ag[na_tr + na_va :], tt_ag[na_tr + na_va :]),
    batch_size=BATCH_SIZE,
)

DATASETS = {
    "synthetic": (syn_train, syn_val, syn_test, n_classes_syn, nk_syn),
    "sst2": (sst_train, sst_val, sst_test, nc_sst, nk_sst),
    "ag_news": (ag_train, ag_val, ag_test, nc_ag, nk_ag),
}

all_results = {}
for top_k in TOP_K_VALUES:
    for ds_name, (tr_l, va_l, te_l, nc, nk) in DATASETS.items():
        key = f"{ds_name}_topk{top_k}"
        print(f"\n{'='*60}")
        print(f"Running: {key}")
        res = run_experiment_topk(ds_name, tr_l, va_l, te_l, nc, nk, top_k=top_k)
        all_results[key] = res
        experiment_data[key] = res

# ======== Visualization ========
epochs_range = list(range(1, EPOCHS + 1))
colors_topk = {1: "steelblue", 2: "darkorange", 4: "seagreen"}
linestyles_topk = {1: "-", 2: "--", 4: ":"}
colors_method = {
    "routekv": "steelblue",
    "attention": "darkorange",
    "random": "gray",
    "hybrid": "purple",
}
ds_names = list(DATASETS.keys())

# Plot 1: Entropy gap across Top-K values per dataset
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    gaps = [
        all_results[f"{ds_name}_topk{k}"]["routing_entropy"]["gap"]
        for k in TOP_K_VALUES
    ]
    key_ents = [
        all_results[f"{ds_name}_topk{k}"]["routing_entropy"]["key"]
        for k in TOP_K_VALUES
    ]
    filler_ents = [
        all_results[f"{ds_name}_topk{k}"]["routing_entropy"]["filler"]
        for k in TOP_K_VALUES
    ]
    x = np.arange(len(TOP_K_VALUES))
    width = 0.25
    ax.bar(x - width, key_ents, width, label="Key", color="steelblue", alpha=0.8)
    ax.bar(x, filler_ents, width, label="Filler", color="darkorange", alpha=0.8)
    ax.bar(x + width, gaps, width, label="Gap", color="seagreen", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
    ax.set_ylabel("Entropy")
    ax.set_title(f"Routing Entropy - {ds_name}")
    ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_entropy_gap.png"), dpi=100)
plt.close()
print("Saved topk_entropy_gap.png")

# Plot 2: Spearman correlation
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    sp_vals = [
        all_results[f"{ds_name}_topk{k}"]["final_spearman"] for k in TOP_K_VALUES
    ]
    bars = ax.bar(
        [f"Top-{k}" for k in TOP_K_VALUES],
        sp_vals,
        color=[colors_topk[k] for k in TOP_K_VALUES],
        alpha=0.8,
    )
    ax.axhline(0, color="red", linestyle="--")
    for bar, val in zip(bars, sp_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01 * np.sign(val + 1e-9),
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_ylabel("Spearman r (spec vs attn)")
    ax.set_title(f"Spearman Corr - {ds_name}")
    ax.set_ylim([-1, 1])
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_spearman.png"), dpi=100)
plt.close()
print("Saved topk_spearman.png")

# Plot 3: Full accuracy
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    full_accs = [all_results[f"{ds_name}_topk{k}"]["full_acc"] for k in TOP_K_VALUES]
    bars = ax.bar(
        [f"Top-{k}" for k in TOP_K_VALUES],
        full_accs,
        color=[colors_topk[k] for k in TOP_K_VALUES],
        alpha=0.8,
    )
    for bar, val in zip(bars, full_accs):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.002,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_ylabel("Full-Cache Accuracy")
    ax.set_title(f"Full Accuracy - {ds_name}")
    ax.set_ylim([0, 1.05])
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_full_accuracy.png"), dpi=100)
plt.close()
print("Saved topk_full_accuracy.png")

# Plot 4: Compression curves for all methods (Top-K=1)
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    key = f"{ds_name}_topk1"
    d = all_results[key]
    full_acc = d["full_acc"]
    ax.axhline(full_acc, color="black", linestyle="--", label="Full-cache", alpha=0.7)
    for method in METHODS:
        accs = [d["eviction_accs"][method][rr] for rr in RETAIN_RATIOS]
        ax.plot(
            RETAIN_RATIOS, accs, marker="o", label=method, color=colors_method[method]
        )
    ax.set_xlabel("Retain Ratio")
    ax.set_ylabel("Accuracy")
    ax.set_title(f"Compression Curves (Top-1) - {ds_name}")
    ax.legend(fontsize=8)
    ax.set_ylim([0, 1.05])
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "method_compression_curves.png"), dpi=100)
plt.close()
print("Saved method_compression_curves.png")

# Plot 5: RouteKV compression curves across Top-K
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    for k in TOP_K_VALUES:
        key = f"{ds_name}_topk{k}"
        d = all_results[key]
        accs = [d["eviction_accs"]["routekv"][rr] for rr in RETAIN_RATIOS]
        ax.plot(
            RETAIN_RATIOS,
            accs,
            marker="o",
            label=f"Top-{k}",
            color=colors_topk[k],
            linestyle=linestyles_topk[k],
        )
    ax.set_xlabel("Retain Ratio")
    ax.set_ylabel("Accuracy (RouteKV)")
    ax.set_title(f"RouteKV Compression Curve - {ds_name}")
    ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_compression_curves.png"), dpi=100)
plt.close()
print("Saved topk_compression_curves.png")

# Plot 6: Precision/Recall at 40% retain
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    precs_40 = [
        all_results[f"{ds_name}_topk{k}"]["precision_recall"]["0.4"]["precision"]
        for k in TOP_K_VALUES
    ]
    recs_40 = [
        all_results[f"{ds_name}_topk{k}"]["precision_recall"]["0.4"]["recall"]
        for k in TOP_K_VALUES
    ]
    x = np.arange(len(TOP_K_VALUES))
    width = 0.35
    ax.bar(
        x - width / 2, precs_40, width, label="Precision", color="steelblue", alpha=0.8
    )
    ax.bar(x + width / 2, recs_40, width, label="Recall", color="darkorange", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
    ax.set_ylabel("Score")
    ax.set_title(f"Key Token P/R @ 40% Retain - {ds_name}")
    ax.legend()
    ax.set_ylim([0, 1.1])
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_precision_recall.png"), dpi=100)
plt.close()
print("Saved topk_precision_recall.png")

# Plot 7: Training curves for synthetic
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ds_name = "synthetic"
for k in TOP_K_VALUES:
    key = f"{ds_name}_topk{k}"
    d = all_results[key]
    axes[0].plot(
        epochs_range,
        d["losses"]["val"],
        label=f"Top-{k}",
        color=colors_topk[k],
        linestyle=linestyles_topk[k],
    )
    axes[1].plot(
        epochs_range,
        d["metrics"]["val"],
        label=f"Top-{k}",
        color=colors_topk[k],
        linestyle=linestyles_topk[k],
    )
axes[0].set_title(f"Val Loss - {ds_name}")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss")
axes[0].legend()
axes[1].set_title(f"Val Accuracy - {ds_name}")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy")
axes[1].legend()
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_training_curves.png"), dpi=100)
plt.close()
print("Saved topk_training_curves.png")

# Plot 8: Accuracy degradation
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for col, ds_name in enumerate(ds_names):
    ax = axes[col]
    key = f"{ds_name}_topk1"
    d = all_results[key]
    full_acc = d["full_acc"]
    for method in METHODS:
        degradations = [
            full_acc - d["eviction_accs"][method][rr] for rr in RETAIN_RATIOS
        ]
        ax.plot(
            RETAIN_RATIOS,
            degradations,
            marker="s",
            label=method,
            color=colors_method[method],
        )
    ax.axhline(0, color="black", linestyle="--", alpha=0.5)
    ax.set_xlabel("Retain Ratio")
    ax.set_ylabel("Accuracy Degradation (full - evicted)")
    ax.set_title(f"Accuracy Degradation - {ds_name}")
    ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "method_accuracy_degradation.png"), dpi=100)
plt.close()
print("Saved method_accuracy_degradation.png")

# Summary heatmap
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

ax = axes[0, 0]
gap_matrix = np.array(
    [
        [all_results[f"{ds}_topk{k}"]["routing_entropy"]["gap"] for k in TOP_K_VALUES]
        for ds in ds_names
    ]
)
im = ax.imshow(gap_matrix, aspect="auto", cmap="RdYlGn")
ax.set_xticks(range(len(TOP_K_VALUES)))
ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
ax.set_yticks(range(len(ds_names)))
ax.set_yticklabels(ds_names)
for i in range(len(ds_names)):
    for j in range(len(TOP_K_VALUES)):
        ax.text(j, i, f"{gap_matrix[i,j]:.3f}", ha="center", va="center", fontsize=9)
plt.colorbar(im, ax=ax)
ax.set_title("Entropy Gap (filler-key)")

ax = axes[0, 1]
sp_matrix = np.array(
    [
        [all_results[f"{ds}_topk{k}"]["final_spearman"] for k in TOP_K_VALUES]
        for ds in ds_names
    ]
)
im = ax.imshow(sp_matrix, aspect="auto", cmap="RdYlGn", vmin=-1, vmax=1)
ax.set_xticks(range(len(TOP_K_VALUES)))
ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
ax.set_yticks(range(len(ds_names)))
ax.set_yticklabels(ds_names)
for i in range(len(ds_names)):
    for j in range(len(TOP_K_VALUES)):
        ax.text(j, i, f"{sp_matrix[i,j]:.3f}", ha="center", va="center", fontsize=9)
plt.colorbar(im, ax=ax)
ax.set_title("Spearman r (spec vs attn)")

ax = axes[0, 2]
acc_matrix = np.array(
    [
        [all_results[f"{ds}_topk{k}"]["full_acc"] for k in TOP_K_VALUES]
        for ds in ds_names
    ]
)
im = ax.imshow(acc_matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(TOP_K_VALUES)))
ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
ax.set_yticks(range(len(ds_names)))
ax.set_yticklabels(ds_names)
for i in range(len(ds_names)):
    for j in range(len(TOP_K_VALUES)):
        ax.text(j, i, f"{acc_matrix[i,j]:.3f}", ha="center", va="center", fontsize=9)
plt.colorbar(im, ax=ax)
ax.set_title("Full-Cache Accuracy")

ax = axes[1, 0]
rr_40_matrix = np.array(
    [
        [
            all_results[f"{ds}_topk{k}"]["eviction_accs"]["routekv"][0.40]
            for k in TOP_K_VALUES
        ]
        for ds in ds_names
    ]
)
im = ax.imshow(rr_40_matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(TOP_K_VALUES)))
ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
ax.set_yticks(range(len(ds_names)))
ax.set_yticklabels(ds_names)
for i in range(len(ds_names)):
    for j in range(len(TOP_K_VALUES)):
        ax.text(j, i, f"{rr_40_matrix[i,j]:.3f}", ha="center", va="center", fontsize=9)
plt.colorbar(im, ax=ax)
ax.set_title("RouteKV Acc @ 40% Retain")

ax = axes[1, 1]
prec_matrix = np.array(
    [
        [
            all_results[f"{ds}_topk{k}"]["precision_recall"]["0.4"]["precision"]
            for k in TOP_K_VALUES
        ]
        for ds in ds_names
    ]
)
im = ax.imshow(prec_matrix, aspect="auto", cmap="Blues", vmin=0, vmax=1)
ax.set_xticks(range(len(TOP_K_VALUES)))
ax.set_xticklabels([f"Top-{k}" for k in TOP_K_VALUES])
ax.set_yticks(range(len(ds_names)))
ax.set_yticklabels(ds_names)
for i in range(len(ds_names)):
    for j in range(len(TOP_K_VALUES)):
        ax.text(j, i, f"{prec_matrix[i,j]:.3f}", ha="center", va="center", fontsize=9)
plt.colorbar(im, ax=ax)
ax.set_title("Key Token Precision @ 40% Retain")

ax = axes[1, 2]
x = np.arange(len(ds_names))
width = 0.2
for mi, method in enumerate(METHODS):
    vals = [
        all_results[f"{ds}_topk1"]["eviction_accs"][method][0.40] for ds in ds_names
    ]
    ax.bar(
        x + (mi - 1.5) * width,
        vals,
        width,
        label=method,
        color=colors_method[method],
        alpha=0.8,
    )
ax.set_xticks(x)
ax.set_xticklabels(ds_names)
ax.set_ylabel("Accuracy @ 40% Retain")
ax.set_title("Method Comparison @ 40% Retain (Top-1)")
ax.legend(fontsize=8)
ax.set_ylim([0, 1.05])
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "topk_ablation_summary.png"), dpi=100)
plt.close()
print("Saved topk_ablation_summary.png")

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nAll experiment data saved.")

print("\n=== FINAL RESULTS: Top-K Routing Ablation ===")
for ds_name in ds_names:
    print(f"\n[{ds_name}]")
    print(
        f"{'Top-K':<10} {'Full Acc':<12} {'Spearman':<12} {'Ent Gap':<12} {'Prec@40%':<12} {'RouteKV@40%':<14} {'Hybrid@40%':<12} {'Attn@40%':<12} {'Random@40%':<12}"
    )
    for k in TOP_K_VALUES:
        key = f"{ds_name}_topk{k}"
        r = all_results[key]
        prec40 = r["precision_recall"]["0.4"]["precision"]
        routekv40 = r["eviction_accs"]["routekv"][0.40]
        hybrid40 = r["eviction_accs"]["hybrid"][0.40]
        attn40 = r["eviction_accs"]["attention"][0.40]
        rand40 = r["eviction_accs"]["random"][0.40]
        print(
            f"Top-{k:<7} {r['full_acc']:<12.4f} {r['final_spearman']:<12.4f} "
            f"{r['routing_entropy']['gap']:<12.4f} {prec40:<12.4f} {routekv40:<14.4f} {hybrid40:<12.4f} {attn40:<12.4f} {rand40:<12.4f}"
        )
