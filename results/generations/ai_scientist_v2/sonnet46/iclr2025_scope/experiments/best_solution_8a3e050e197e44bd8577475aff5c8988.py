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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

SEED = 42
torch.manual_seed(SEED)
np.random.seed(SEED)

N_SAMPLES = 2000
N_CLASSES = 4
SEQ_LEN = 32
D_MODEL = 64
N_HEADS = 4
N_LAYERS = 3
N_EXPERTS = 8
TOP_K = 2
DROPOUT = 0.1
WEIGHT_DECAY = 1e-4
LR = 1e-4
EPOCHS = 60
BATCH_SIZE = 64
RETAIN_RATIO = 0.40
MIN_ACC_GATE = 0.70
METHODS = ["routekv", "attention", "random"]

# Scheduler configs to tune
SCHEDULER_CONFIGS = [
    {"name": "cosine_annealing", "type": "cosine"},
    {
        "name": "onecycle_pct0.1_maxlr5x",
        "type": "onecycle",
        "pct_start": 0.1,
        "max_lr_mult": 5.0,
    },
    {
        "name": "onecycle_pct0.2_maxlr5x",
        "type": "onecycle",
        "pct_start": 0.2,
        "max_lr_mult": 5.0,
    },
    {
        "name": "onecycle_pct0.3_maxlr10x",
        "type": "onecycle",
        "pct_start": 0.3,
        "max_lr_mult": 10.0,
    },
    {
        "name": "onecycle_pct0.3_maxlr5x",
        "type": "onecycle",
        "pct_start": 0.3,
        "max_lr_mult": 5.0,
    },
    {
        "name": "onecycle_pct0.4_maxlr10x",
        "type": "onecycle",
        "pct_start": 0.4,
        "max_lr_mult": 10.0,
    },
]

experiment_data = {
    cfg["name"]: {
        "synthetic": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "routing_entropy": {"key_tokens": [], "filler_tokens": []},
            "kvra": {m: [] for m in METHODS},
            "full_cache_acc": [],
            "eviction_acc": {m: [] for m in METHODS},
            "best_val_acc": 0.0,
        }
    }
    for cfg in SCHEDULER_CONFIGS
}


def make_dataset(n, seed=0):
    rng = np.random.RandomState(seed)
    labels = rng.randint(0, N_CLASSES, size=n)
    basis = np.eye(N_CLASSES, D_MODEL)
    key_vecs = basis[labels] + 0.05 * rng.randn(n, D_MODEL)
    filler = 0.1 * rng.randn(n, SEQ_LEN - 1, D_MODEL)
    seqs = np.concatenate([key_vecs[:, None, :], filler], axis=1)
    return torch.tensor(seqs.astype(np.float32)), torch.tensor(labels.astype(np.int64))


X_train, y_train = make_dataset(N_SAMPLES, seed=0)
X_val, y_val = make_dataset(400, seed=1)
X_test, y_test = make_dataset(400, seed=2)

train_loader = DataLoader(
    TensorDataset(X_train, y_train), batch_size=BATCH_SIZE, shuffle=True
)
val_loader = DataLoader(TensorDataset(X_val, y_val), batch_size=BATCH_SIZE)
test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=BATCH_SIZE)


class MoELayer(nn.Module):
    def __init__(self, d_model, n_experts=N_EXPERTS, top_k=TOP_K, dropout=DROPOUT):
        super().__init__()
        self.n_experts = n_experts
        self.top_k = top_k
        self.gate = nn.Linear(d_model, n_experts, bias=False)
        self.experts = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Linear(d_model, d_model * 2),
                    nn.GELU(),
                    nn.Dropout(dropout),
                    nn.Linear(d_model * 2, d_model),
                )
                for _ in range(n_experts)
            ]
        )
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        B, T, D = x.shape
        logits = self.gate(x)
        topk_vals, topk_idx = torch.topk(logits, self.top_k, dim=-1)
        weights = F.softmax(topk_vals, dim=-1)
        out = torch.zeros_like(x)
        for k in range(self.top_k):
            idx = topk_idx[:, :, k]
            w = weights[:, :, k].unsqueeze(-1)
            flat_x = x.reshape(B * T, D)
            flat_idx = idx.reshape(B * T)
            expert_out = torch.zeros(B * T, D, device=x.device)
            for e in range(self.n_experts):
                mask = flat_idx == e
                if mask.any():
                    expert_out[mask] = self.experts[e](flat_x[mask])
            out += w * expert_out.reshape(B, T, D)
        return self.drop(out), logits


class MoETransformerLayer(nn.Module):
    def __init__(self, d_model, n_heads, dropout=DROPOUT):
        super().__init__()
        self.attn = nn.MultiheadAttention(
            d_model, n_heads, dropout=dropout, batch_first=True
        )
        self.moe = MoELayer(d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.drop = nn.Dropout(dropout)

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
        self,
        d_model=D_MODEL,
        n_heads=N_HEADS,
        n_layers=N_LAYERS,
        n_classes=N_CLASSES,
        dropout=DROPOUT,
    ):
        super().__init__()
        self.proj = nn.Linear(d_model, d_model)
        self.layers = nn.ModuleList(
            [MoETransformerLayer(d_model, n_heads, dropout) for _ in range(n_layers)]
        )
        self.head = nn.Sequential(
            nn.LayerNorm(d_model), nn.Dropout(dropout), nn.Linear(d_model, n_classes)
        )

    def forward(self, x, return_routing=False, return_attn=False):
        x = F.gelu(self.proj(x))
        all_router_logits, all_attn_weights = [], []
        for layer in self.layers:
            if return_attn:
                x, rl, aw = layer(x, return_attn=True)
                all_attn_weights.append(aw)
            else:
                x, rl = layer(x)
            all_router_logits.append(rl)
        cls = x.mean(dim=1)
        logits = self.head(cls)
        if return_routing:
            return logits, all_router_logits, all_attn_weights
        return logits


def load_balance_loss(router_logits_list, top_k=TOP_K):
    loss = 0.0
    for rl in router_logits_list:
        gates = F.softmax(rl, dim=-1)
        frac_tokens = gates.mean(dim=[0, 1])
        _, topk_idx = torch.topk(rl, top_k, dim=-1)
        onehot = torch.zeros_like(gates).scatter_(-1, topk_idx, 1.0)
        frac_dispatch = onehot.mean(dim=[0, 1])
        loss += (frac_tokens * frac_dispatch).sum() * rl.shape[-1]
    return loss / len(router_logits_list)


def compute_routing_scores(rl_list):
    stacked = torch.stack([F.softmax(rl, dim=-1) for rl in rl_list], dim=0)
    avg_prob = stacked.mean(0)
    entropy = -(avg_prob * (avg_prob + 1e-9).log()).sum(-1)
    return entropy


def compute_attention_scores(aw_list):
    if not aw_list:
        return None
    attn_stack = torch.stack(aw_list, dim=0)
    return attn_stack.mean(0).sum(2)


def apply_eviction_mask(x, keep_mask):
    return x * keep_mask.unsqueeze(-1).float()


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


def evaluate_with_eviction(model, loader, method):
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            _, rl_list, aw_list = model(xb, return_routing=True, return_attn=True)
            if method == "routekv":
                scores = compute_routing_scores(rl_list)
                mask = get_keep_mask(scores, RETAIN_RATIO, higher_is_better=False)
            elif method == "attention":
                scores = compute_attention_scores(aw_list)
                if scores is None:
                    scores = torch.rand(xb.size(0), xb.size(1), device=device)
                mask = get_keep_mask(scores, RETAIN_RATIO, higher_is_better=True)
            elif method == "random":
                scores = torch.rand(xb.size(0), xb.size(1), device=device)
                mask = get_keep_mask(scores, RETAIN_RATIO, higher_is_better=True)
            x_evicted = apply_eviction_mask(xb, mask)
            logits = model(x_evicted)
            correct += (logits.argmax(1) == yb).sum().item()
            total += xb.size(0)
    return correct / total


criterion = nn.CrossEntropyLoss()
steps_per_epoch = len(train_loader)

best_overall_val_acc = 0.0
best_cfg_name = None
best_model_state = None

for cfg in SCHEDULER_CONFIGS:
    cfg_name = cfg["name"]
    print(f"\n=== Training with scheduler: {cfg_name} ===")

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    model = MoEClassifier().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)

    if cfg["type"] == "cosine":
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
        step_per_batch = False
    else:
        max_lr = LR * cfg["max_lr_mult"]
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
            optimizer,
            max_lr=max_lr,
            epochs=EPOCHS,
            steps_per_epoch=steps_per_epoch,
            pct_start=cfg["pct_start"],
            anneal_strategy="cos",
            div_factor=cfg["max_lr_mult"],
            final_div_factor=1e4,
        )
        step_per_batch = True

    best_val_acc = 0.0
    best_state = None

    for epoch in range(1, EPOCHS + 1):
        model.train()
        tr_loss, tr_correct, tr_total = 0.0, 0, 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            optimizer.zero_grad()
            logits, rl_list, _ = model(xb, return_routing=True, return_attn=False)
            ce_loss = criterion(logits, yb)
            lb_loss = load_balance_loss(rl_list)
            loss = ce_loss + 0.01 * lb_loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            if step_per_batch:
                scheduler.step()
            tr_loss += ce_loss.item() * xb.size(0)
            tr_correct += (logits.argmax(1) == yb).sum().item()
            tr_total += xb.size(0)

        if not step_per_batch:
            scheduler.step()

        model.eval()
        val_loss, val_correct, val_total = 0.0, 0, 0
        with torch.no_grad():
            for xb, yb in val_loader:
                xb, yb = xb.to(device), yb.to(device)
                logits = model(xb)
                val_loss += criterion(logits, yb).item() * xb.size(0)
                val_correct += (logits.argmax(1) == yb).sum().item()
                val_total += xb.size(0)

        tr_acc = tr_correct / tr_total
        val_acc = val_correct / val_total
        val_loss_avg = val_loss / val_total

        experiment_data[cfg_name]["synthetic"]["metrics"]["train"].append(tr_acc)
        experiment_data[cfg_name]["synthetic"]["metrics"]["val"].append(val_acc)
        experiment_data[cfg_name]["synthetic"]["losses"]["train"].append(
            tr_loss / tr_total
        )
        experiment_data[cfg_name]["synthetic"]["losses"]["val"].append(val_loss_avg)

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

        if epoch % 10 == 0:
            print(
                f"  Epoch {epoch:03d}: val_loss={val_loss_avg:.4f}  val_acc={val_acc:.4f}"
            )

    experiment_data[cfg_name]["synthetic"]["best_val_acc"] = best_val_acc
    print(f"  Best val accuracy: {best_val_acc:.4f}")

    model.load_state_dict({k: v.to(device) for k, v in best_state.items()})

    if best_val_acc > best_overall_val_acc:
        best_overall_val_acc = best_val_acc
        best_cfg_name = cfg_name
        best_model_state = {k: v.cpu().clone() for k, v in best_state.items()}

    # Stage 2: Routing Specialisation
    model.eval()
    key_entropies, filler_entropies = [], []
    with torch.no_grad():
        for xb, yb in test_loader:
            xb = xb.to(device)
            _, rl_list, aw_list = model(xb, return_routing=True, return_attn=True)
            stacked = torch.stack([F.softmax(rl, dim=-1) for rl in rl_list], dim=0)
            avg_prob = stacked.mean(dim=0)
            ent = -(avg_prob * (avg_prob + 1e-9).log()).sum(-1)
            key_entropies.append(ent[:, 0].cpu())
            filler_entropies.append(ent[:, 1:].cpu().reshape(-1))

    key_ent = torch.cat(key_entropies).mean().item()
    filler_ent = torch.cat(filler_entropies).mean().item()
    ent_gap = filler_ent - key_ent
    experiment_data[cfg_name]["synthetic"]["routing_entropy"]["key_tokens"] = [key_ent]
    experiment_data[cfg_name]["synthetic"]["routing_entropy"]["filler_tokens"] = [
        filler_ent
    ]
    print(f"  Entropy gap: {ent_gap:.4f}")

    # Stage 3: KVRA
    full_correct, full_total = 0, 0
    with torch.no_grad():
        for xb, yb in test_loader:
            xb, yb = xb.to(device), yb.to(device)
            logits = model(xb)
            full_correct += (logits.argmax(1) == yb).sum().item()
            full_total += xb.size(0)
    full_acc = full_correct / full_total
    experiment_data[cfg_name]["synthetic"]["full_cache_acc"].append(full_acc)
    print(f"  Full-cache test accuracy: {full_acc:.4f}")

    for method in METHODS:
        acc = evaluate_with_eviction(model, test_loader, method)
        kvra = (acc / full_acc) * 100 if full_acc > 0 else 0.0
        experiment_data[cfg_name]["synthetic"]["eviction_acc"][method].append(acc)
        experiment_data[cfg_name]["synthetic"]["kvra"][method].append(kvra)
        print(f"  Method={method:10s}  eviction_acc={acc:.4f}  KVRA={kvra:.2f}%")

print(
    f"\n=== Best Scheduler Config: {best_cfg_name} (val_acc={best_overall_val_acc:.4f}) ==="
)

# Final evaluation with best model
model = MoEClassifier().to(device)
model.load_state_dict({k: v.to(device) for k, v in best_model_state.items()})
model.eval()

# Visualisation: Training curves comparison
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

colors_list = ["blue", "orange", "green", "red", "purple", "brown"]
epochs_range = list(range(1, EPOCHS + 1))

ax_loss = axes[0]
ax_acc = axes[1]
for i, cfg in enumerate(SCHEDULER_CONFIGS):
    cname = cfg["name"]
    c = colors_list[i % len(colors_list)]
    ax_loss.plot(
        epochs_range,
        experiment_data[cname]["synthetic"]["losses"]["val"],
        label=cname,
        color=c,
        alpha=0.8,
    )
    ax_acc.plot(
        epochs_range,
        experiment_data[cname]["synthetic"]["metrics"]["val"],
        label=cname,
        color=c,
        alpha=0.8,
    )

ax_loss.set_xlabel("Epoch")
ax_loss.set_ylabel("Val Loss")
ax_loss.set_title("Validation Loss by Scheduler Config")
ax_loss.legend(fontsize=7)
ax_acc.axhline(MIN_ACC_GATE, color="red", linestyle="--", label="Gate")
ax_acc.set_xlabel("Epoch")
ax_acc.set_ylabel("Val Accuracy")
ax_acc.set_title("Validation Accuracy by Scheduler Config")
ax_acc.legend(fontsize=7)

# Best val acc bar chart
ax_bar = axes[2]
cfg_names_short = [cfg["name"].replace("onecycle_", "oc_") for cfg in SCHEDULER_CONFIGS]
best_vals = [
    experiment_data[cfg["name"]]["synthetic"]["best_val_acc"]
    for cfg in SCHEDULER_CONFIGS
]
bars = ax_bar.bar(
    range(len(SCHEDULER_CONFIGS)),
    best_vals,
    color=colors_list[: len(SCHEDULER_CONFIGS)],
    alpha=0.8,
)
ax_bar.set_xticks(range(len(SCHEDULER_CONFIGS)))
ax_bar.set_xticklabels(cfg_names_short, rotation=45, ha="right", fontsize=7)
ax_bar.set_ylabel("Best Val Accuracy")
ax_bar.set_title("Best Val Accuracy per Config")
ax_bar.axhline(MIN_ACC_GATE, color="red", linestyle="--")
for bar, val in zip(bars, best_vals):
    ax_bar.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=7,
    )

# KVRA comparison for best config
ax_kvra = axes[3]
best_kvra_vals = [
    (
        experiment_data[best_cfg_name]["synthetic"]["kvra"][m][0]
        if experiment_data[best_cfg_name]["synthetic"]["kvra"][m]
        else 0
    )
    for m in METHODS
]
bars2 = ax_kvra.bar(
    METHODS, best_kvra_vals, color=["steelblue", "darkorange", "green"], alpha=0.8
)
ax_kvra.axhline(100.0, color="black", linestyle="--")
ax_kvra.set_ylabel("KVRA (%)")
ax_kvra.set_title(f"KVRA - Best Config\n({best_cfg_name})")
for bar, val in zip(bars2, best_kvra_vals):
    ax_kvra.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.5,
        f"{val:.1f}%",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# Training curves for best config
ax_tr = axes[4]
ax_tr.plot(
    epochs_range,
    experiment_data[best_cfg_name]["synthetic"]["losses"]["train"],
    label="Train Loss",
)
ax_tr.plot(
    epochs_range,
    experiment_data[best_cfg_name]["synthetic"]["losses"]["val"],
    label="Val Loss",
)
ax_tr.set_xlabel("Epoch")
ax_tr.set_ylabel("Loss")
ax_tr.set_title(f"Loss Curves - Best Config\n({best_cfg_name})")
ax_tr.legend()

# Routing entropy for best config
ax_ent = axes[5]
key_e = (
    experiment_data[best_cfg_name]["synthetic"]["routing_entropy"]["key_tokens"][0]
    if experiment_data[best_cfg_name]["synthetic"]["routing_entropy"]["key_tokens"]
    else 0
)
fill_e = (
    experiment_data[best_cfg_name]["synthetic"]["routing_entropy"]["filler_tokens"][0]
    if experiment_data[best_cfg_name]["synthetic"]["routing_entropy"]["filler_tokens"]
    else 0
)
bars3 = ax_ent.bar(
    ["Key Tokens", "Filler Tokens"],
    [key_e, fill_e],
    color=["crimson", "royalblue"],
    alpha=0.8,
)
ax_ent.set_ylabel("Mean Routing Entropy")
ax_ent.set_title(f"Routing Entropy - Best Config\n(gap={fill_e-key_e:.4f})")
for bar, val in zip(bars3, [key_e, fill_e]):
    ax_ent.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.4f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )

try:
    plt.tight_layout()
except Exception:
    pass

plt.savefig(os.path.join(working_dir, "routekv_results.png"), dpi=120)
plt.close()
print(f'\nPlot saved to {os.path.join(working_dir, "routekv_results.png")}')

# Routing entropy plot for best config
fig2, ax2 = plt.subplots(figsize=(6, 4))
ent_gap_best = fill_e - key_e
SPEC_GATE = ent_gap_best > 0.05
bars_ent = ax2.bar(
    ["Key Tokens\n(should be low)", "Filler Tokens\n(should be high)"],
    [key_e, fill_e],
    color=["crimson", "royalblue"],
    alpha=0.8,
)
ax2.set_ylabel("Mean Routing Entropy")
ax2.set_title(
    f"Routing Specialisation - Best Config\n(gap={ent_gap_best:.4f}, gate_passed={SPEC_GATE})"
)
for bar, val in zip(bars_ent, [key_e, fill_e]):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.005,
        f"{val:.4f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )
try:
    plt.tight_layout()
except Exception:
    pass
plt.savefig(os.path.join(working_dir, "routing_entropy.png"), dpi=120)
plt.close()
print(
    f'Routing entropy plot saved to {os.path.join(working_dir, "routing_entropy.png")}'
)

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(
    f'\nAll experiment data saved to {os.path.join(working_dir, "experiment_data.npy")}'
)

print("\n=== Hyperparameter Tuning Complete ===")
print(f"  Best scheduler config : {best_cfg_name}")
print(f"  Best val accuracy     : {best_overall_val_acc:.4f}")
best_full_acc = (
    experiment_data[best_cfg_name]["synthetic"]["full_cache_acc"][0]
    if experiment_data[best_cfg_name]["synthetic"]["full_cache_acc"]
    else 0
)
print(f"  Full-cache test acc   : {best_full_acc:.4f}")
GATE = best_overall_val_acc >= MIN_ACC_GATE
print(f"  Accuracy gate passed  : {GATE}")
print(f"  Spec. gate passed     : {SPEC_GATE}  (entropy gap={ent_gap_best:.4f})")
for method in METHODS:
    kvra_val = (
        experiment_data[best_cfg_name]["synthetic"]["kvra"][method][0]
        if experiment_data[best_cfg_name]["synthetic"]["kvra"][method]
        else 0
    )
    print(f"  KVRA [{method:10s}]  : {kvra_val:.2f}%")

print("\n=== All Configs Summary ===")
for cfg in SCHEDULER_CONFIGS:
    cname = cfg["name"]
    bva = experiment_data[cname]["synthetic"]["best_val_acc"]
    fa = (
        experiment_data[cname]["synthetic"]["full_cache_acc"][0]
        if experiment_data[cname]["synthetic"]["full_cache_acc"]
        else 0
    )
    print(f"  {cname:40s}: best_val={bva:.4f}, full_test={fa:.4f}")
