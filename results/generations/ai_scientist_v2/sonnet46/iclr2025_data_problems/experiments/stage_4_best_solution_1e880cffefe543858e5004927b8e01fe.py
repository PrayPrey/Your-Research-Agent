import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from collections import Counter

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

VOCAB_SIZE = 500
SEQ_LEN = 32
N_REAL = 2000
ANCHOR_SIZE = 200
BATCH_SIZE = 64
EPOCHS_PER_GEN = 5
N_GENERATIONS = 5
N_SYNTH = 2000
GEN_SAMPLES = 500
TAIL_FRAC = 0.10
D_MODEL = 128
N_HEAD = 4
N_LAYERS = 2
DIM_FF = 256

LR_VALUES = [1e-4, 3e-4, 1e-3, 3e-3]

rng = np.random.default_rng(SEED)
ranks = np.arange(1, VOCAB_SIZE + 1, dtype=np.float32)
freq_weights = 1.0 / ranks
freq_weights /= freq_weights.sum()


def make_real_corpus(n=N_REAL, seq_len=SEQ_LEN):
    seqs = []
    for _ in range(n):
        tokens = rng.choice(VOCAB_SIZE, size=seq_len, p=freq_weights) + 1
        seqs.append(tokens.tolist())
    return seqs


REAL_CORPUS = make_real_corpus()

sorted_by_freq = np.argsort(freq_weights)
n_tail = int(VOCAB_SIZE * TAIL_FRAC)
TAIL_TOKENS = set((sorted_by_freq[:n_tail] + 1).tolist())
print(
    f"Tail tokens: {len(TAIL_TOKENS)} tokens (indices {min(TAIL_TOKENS)}..{max(TAIL_TOKENS)})"
)


class SeqDataset(Dataset):
    def __init__(self, seqs):
        self.data = [torch.tensor(s, dtype=torch.long) for s in seqs]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=512):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        pos = torch.arange(0, max_len).unsqueeze(1).float()
        div = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(pos * div)
        pe[:, 1::2] = torch.cos(pos * div)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]


class SmallGPT(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(VOCAB_SIZE + 1, D_MODEL, padding_idx=0)
        self.pe = PositionalEncoding(D_MODEL)
        enc_layer = nn.TransformerEncoderLayer(
            D_MODEL, N_HEAD, DIM_FF, dropout=0.1, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(enc_layer, num_layers=N_LAYERS)
        self.head = nn.Linear(D_MODEL, VOCAB_SIZE + 1)

    def forward(self, x):
        sz = x.size(1)
        mask = torch.triu(torch.ones(sz, sz, device=x.device), diagonal=1).bool()
        e = self.pe(self.embed(x))
        out = self.transformer(e, mask=mask)
        return self.head(out)


def make_model():
    return SmallGPT().to(device)


def train_model(model, seqs, epochs=EPOCHS_PER_GEN, lr=3e-4):
    ds = SeqDataset(seqs)
    dl = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=False)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    losses = []
    for ep in range(epochs):
        ep_loss = 0.0
        n = 0
        for batch in dl:
            batch = batch.to(device)
            inp, tgt = batch[:, :-1], batch[:, 1:]
            logits = model(inp)
            loss = F.cross_entropy(
                logits.reshape(-1, VOCAB_SIZE + 1), tgt.reshape(-1), ignore_index=0
            )
            opt.zero_grad()
            loss.backward()
            opt.step()
            ep_loss += loss.item() * batch.size(0)
            n += batch.size(0)
        avg = ep_loss / n
        losses.append(avg)
        print(f"  epoch {ep+1}/{epochs} loss={avg:.4f}")
    return losses


@torch.no_grad()
def generate_sequences(model, n=N_SYNTH, seq_len=SEQ_LEN):
    model.eval()
    seqs = []
    bs = 128
    for start in range(0, n, bs):
        cur = min(bs, n - start)
        tokens = torch.randint(1, VOCAB_SIZE + 1, (cur, 1), device=device)
        for _ in range(seq_len - 1):
            logits = model(tokens)[:, -1, :]
            logits[:, 0] = -1e9
            probs = F.softmax(logits, dim=-1)
            nxt = torch.multinomial(probs, 1)
            tokens = torch.cat([tokens, nxt], dim=1)
        seqs.extend(tokens.cpu().tolist())
    return seqs


def tail_token_coverage(seqs):
    seen = set()
    for s in seqs:
        seen.update(s)
    return len(seen & TAIL_TOKENS) / len(TAIL_TOKENS)


def compute_perplexity(model, seqs, max_seqs=500):
    model.eval()
    ds = SeqDataset(seqs[:max_seqs])
    dl = DataLoader(ds, batch_size=64, shuffle=False)
    total_loss = 0.0
    total_tok = 0
    with torch.no_grad():
        for batch in dl:
            batch = batch.to(device)
            inp, tgt = batch[:, :-1], batch[:, 1:]
            logits = model(inp)
            loss = F.cross_entropy(
                logits.reshape(-1, VOCAB_SIZE + 1),
                tgt.reshape(-1),
                ignore_index=0,
                reduction="sum",
            )
            total_loss += loss.item()
            total_tok += (tgt != 0).sum().item()
    return math.exp(total_loss / max(total_tok, 1))


def token_freq_vector(seqs):
    counts = Counter(t for s in seqs for t in s)
    vec = np.zeros(VOCAB_SIZE + 1)
    for t, c in counts.items():
        vec[t] = c
    s = vec.sum()
    return vec / s if s > 0 else vec


def kl_divergence(p, q, eps=1e-10):
    mask = p > 0
    return float(np.sum(p[mask] * np.log((p[mask] + eps) / (q[mask] + eps))))


REAL_FREQ = token_freq_vector(REAL_CORPUS)


def anchor_random(real_corpus, k=ANCHOR_SIZE):
    idx = random.sample(range(len(real_corpus)), k)
    return [real_corpus[i] for i in idx]


def anchor_tail(real_corpus, k=ANCHOR_SIZE):
    scores = [sum(1 for t in seq if t in TAIL_TOKENS) for seq in real_corpus]
    order = np.argsort(scores)[::-1]
    return [real_corpus[i] for i in order[:k]]


def anchor_centroid(real_corpus, k=ANCHOR_SIZE):
    scores = [sum(1 for t in seq if t not in TAIL_TOKENS) for seq in real_corpus]
    order = np.argsort(scores)[::-1]
    return [real_corpus[i] for i in order[:k]]


GOLDEN_REAL_FRAC = 0.38

strategies = {
    "TADA (tail anchor)": anchor_tail,
    "Random anchor": anchor_random,
    "Centroid anchor": anchor_centroid,
    "Golden-ratio baseline": None,
    "No anchor (collapse)": None,
}

# experiment_data structure: lr_value -> strategy -> metrics
experiment_data = {}

for lr in LR_VALUES:
    lr_key = f"lr_{lr}"
    print(f"\n{'#'*70}")
    print(f"# Learning Rate: {lr}")
    print(f"{'#'*70}")

    experiment_data[lr_key] = {
        name: {
            "tail_coverage": [],
            "perplexity": [],
            "kl_divergence": [],
            "train_losses": [],
        }
        for name in strategies
    }

    for strat_name, anchor_fn in strategies.items():
        print(f"\n{'='*60}")
        print(f"Strategy: {strat_name} | LR: {lr}")
        print("=" * 60)

        # Reset seeds for reproducibility per strategy
        random.seed(SEED)
        np.random.seed(SEED)
        torch.manual_seed(SEED)

        model = make_model()
        print(f"[Gen 0] Train on real corpus ({len(REAL_CORPUS)} seqs)")
        losses = train_model(model, REAL_CORPUS, lr=lr)
        experiment_data[lr_key][strat_name]["train_losses"].append(losses)

        gen_seqs = generate_sequences(model, n=GEN_SAMPLES)
        ttc = tail_token_coverage(gen_seqs)
        ppl = compute_perplexity(model, REAL_CORPUS)
        kl = kl_divergence(REAL_FREQ, token_freq_vector(gen_seqs))
        experiment_data[lr_key][strat_name]["tail_coverage"].append(ttc)
        experiment_data[lr_key][strat_name]["perplexity"].append(ppl)
        experiment_data[lr_key][strat_name]["kl_divergence"].append(kl)
        print(f"[Gen 0] TailCoverage={ttc:.4f} PPL={ppl:.2f} KL={kl:.4f}")

        synth_pool = generate_sequences(model, n=N_SYNTH)

        for gen in range(1, N_GENERATIONS + 1):
            print(f"\n[Gen {gen}]")
            if strat_name == "No anchor (collapse)":
                train_seqs = synth_pool
            elif strat_name == "Golden-ratio baseline":
                n_real_mix = int(GOLDEN_REAL_FRAC * (N_SYNTH + ANCHOR_SIZE))
                n_real_mix = min(n_real_mix, len(REAL_CORPUS))
                real_mix = random.sample(REAL_CORPUS, n_real_mix)
                train_seqs = real_mix + synth_pool
            else:
                anchor = anchor_fn(REAL_CORPUS, ANCHOR_SIZE)
                train_seqs = anchor + synth_pool

            random.shuffle(train_seqs)
            print(f"  Training on {len(train_seqs)} sequences")
            model = make_model()
            losses = train_model(model, train_seqs, lr=lr)
            experiment_data[lr_key][strat_name]["train_losses"].append(losses)

            gen_seqs = generate_sequences(model, n=GEN_SAMPLES)
            ttc = tail_token_coverage(gen_seqs)
            ppl = compute_perplexity(model, REAL_CORPUS)
            kl = kl_divergence(REAL_FREQ, token_freq_vector(gen_seqs))
            experiment_data[lr_key][strat_name]["tail_coverage"].append(ttc)
            experiment_data[lr_key][strat_name]["perplexity"].append(ppl)
            experiment_data[lr_key][strat_name]["kl_divergence"].append(kl)
            print(f"[Gen {gen}] TailCoverage={ttc:.4f} PPL={ppl:.2f} KL={kl:.4f}")

            synth_pool = generate_sequences(model, n=N_SYNTH)

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nExperiment data saved.")

# ─── Plots ────────────────────────────────────────────────────────────────────
gens = list(range(N_GENERATIONS + 1))
colors = {
    "TADA (tail anchor)": "green",
    "Random anchor": "blue",
    "Centroid anchor": "orange",
    "Golden-ratio baseline": "purple",
    "No anchor (collapse)": "red",
}
linestyles = {
    "TADA (tail anchor)": "-",
    "Random anchor": "--",
    "Centroid anchor": "-.",
    "Golden-ratio baseline": ":",
    "No anchor (collapse)": "-",
}

lr_line_styles = ["-", "--", "-.", ":"]
lr_markers = ["o", "s", "^", "D"]

# Plot 1: Per-LR plots (one figure per LR, 3 metrics)
for lr in LR_VALUES:
    lr_key = f"lr_{lr}"
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"LR = {lr}", fontsize=14)
    for strat_name in strategies:
        d = experiment_data[lr_key][strat_name]
        c = colors[strat_name]
        ls = linestyles[strat_name]
        axes[0].plot(
            gens, d["tail_coverage"], color=c, ls=ls, marker="o", label=strat_name
        )
        axes[1].plot(
            gens, d["perplexity"], color=c, ls=ls, marker="o", label=strat_name
        )
        axes[2].plot(
            gens, d["kl_divergence"], color=c, ls=ls, marker="o", label=strat_name
        )
    axes[0].set_title("Tail Token Coverage (↑)")
    axes[0].set_xlabel("Generation")
    axes[0].set_ylabel("Coverage")
    axes[1].set_title("Perplexity on Real Data (↓)")
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("PPL")
    axes[2].set_title("KL Divergence from Real (↓)")
    axes[2].set_xlabel("Generation")
    axes[2].set_ylabel("KL")
    for ax in axes:
        ax.legend(fontsize=7)
        ax.grid(True)
    plt.tight_layout()
    fname = os.path.join(working_dir, f"metrics_lr_{lr}.png")
    plt.savefig(fname, dpi=150)
    plt.close()
    print(f"Plot saved: metrics_lr_{lr}.png")

# Plot 2: LR comparison per strategy
for strat_name in strategies:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f"Strategy: {strat_name} - LR Comparison", fontsize=12)
    for i, lr in enumerate(LR_VALUES):
        lr_key = f"lr_{lr}"
        d = experiment_data[lr_key][strat_name]
        axes[0].plot(
            gens,
            d["tail_coverage"],
            ls=lr_line_styles[i],
            marker=lr_markers[i],
            label=f"LR={lr}",
        )
        axes[1].plot(
            gens,
            d["perplexity"],
            ls=lr_line_styles[i],
            marker=lr_markers[i],
            label=f"LR={lr}",
        )
        axes[2].plot(
            gens,
            d["kl_divergence"],
            ls=lr_line_styles[i],
            marker=lr_markers[i],
            label=f"LR={lr}",
        )
    axes[0].set_title("Tail Token Coverage (↑)")
    axes[0].set_xlabel("Generation")
    axes[0].set_ylabel("Coverage")
    axes[1].set_title("Perplexity on Real Data (↓)")
    axes[1].set_xlabel("Generation")
    axes[1].set_ylabel("PPL")
    axes[2].set_title("KL Divergence from Real (↓)")
    axes[2].set_xlabel("Generation")
    axes[2].set_ylabel("KL")
    for ax in axes:
        ax.legend(fontsize=8)
        ax.grid(True)
    plt.tight_layout()
    safe_name = (
        strat_name.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "")
    )
    fname = os.path.join(working_dir, f"lr_comparison_{safe_name}.png")
    plt.savefig(fname, dpi=150)
    plt.close()
    print(f"Plot saved: lr_comparison_{safe_name}.png")

# Plot 3: Aggregate - best LR per metric across all strategies at final gen
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle(
    "LR Tuning: Final Generation Metrics (Averaged Across Strategies)", fontsize=12
)
metrics = ["tail_coverage", "kl_divergence", "perplexity"]
metric_labels = ["Tail Coverage (↑)", "KL Divergence (↓)", "Perplexity (↓)"]

for mi, (metric, mlabel) in enumerate(zip(metrics, metric_labels)):
    avg_vals = []
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        vals = [experiment_data[lr_key][s][metric][-1] for s in strategies]
        avg_vals.append(np.mean(vals))
    axes[mi].bar(
        [str(lr) for lr in LR_VALUES],
        avg_vals,
        color=["blue", "green", "orange", "red"],
    )
    axes[mi].set_title(mlabel)
    axes[mi].set_xlabel("Learning Rate")
    axes[mi].set_ylabel(metric.replace("_", " ").title())
    axes[mi].grid(True, axis="y")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "lr_tuning_summary.png"), dpi=150)
plt.close()
print("Plot saved: lr_tuning_summary.png")

# ─── Summary table ────────────────────────────────────────────────────────────
print("\n" + "=" * 90)
print(
    f"{'LR':<10} {'Strategy':<30} {'TailCov G0':>10} {'TailCov GN':>10} {'PPL GN':>8} {'KL GN':>8}"
)
print("-" * 90)
for lr in LR_VALUES:
    lr_key = f"lr_{lr}"
    for strat_name in strategies:
        d = experiment_data[lr_key][strat_name]
        tc0 = d["tail_coverage"][0]
        tcN = d["tail_coverage"][-1]
        pN = d["perplexity"][-1]
        kN = d["kl_divergence"][-1]
        print(
            f"{lr:<10} {strat_name:<30} {tc0:>10.4f} {tcN:>10.4f} {pN:>8.2f} {kN:>8.4f}"
        )
print("=" * 90)

# Find best LR
print("\n─── Best LR per strategy (by final KL divergence) ───")
for strat_name in strategies:
    best_lr = None
    best_kl = float("inf")
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        kl = experiment_data[lr_key][strat_name]["kl_divergence"][-1]
        if kl < best_kl:
            best_kl = kl
            best_lr = lr
    print(f"  {strat_name:<30}: best LR = {best_lr} (KL={best_kl:.4f})")

print("\n─── Best LR per strategy (by final Tail Coverage) ───")
for strat_name in strategies:
    best_lr = None
    best_tc = -1
    for lr in LR_VALUES:
        lr_key = f"lr_{lr}"
        tc = experiment_data[lr_key][strat_name]["tail_coverage"][-1]
        if tc > best_tc:
            best_tc = tc
            best_lr = lr
    print(f"  {strat_name:<30}: best LR = {best_lr} (TailCov={best_tc:.4f})")
