import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from collections import Counter
import matplotlib.pyplot as plt
import math
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# ── Hyper-parameters ─────────────────────────────────────────────────────────
VOCAB_SIZE = 500
SEQ_LEN = 32
N_REAL = 4000  # total real training sentences
ANCHOR_BUDGET = 400  # real samples in anchor set (10 % of real data)
N_SYNTHETIC = 3600  # synthetic samples per generation
N_GENERATIONS = 5
EPOCHS_PER_GEN = 3
BATCH_SIZE = 64
LR = 3e-4
D_MODEL = 128
N_HEADS = 4
N_LAYERS = 2
TAIL_FRACTION = 0.10  # bottom-10 % by frequency = "tail"
GEN_SAMPLES = 500  # samples generated for evaluation
GEN_LEN = SEQ_LEN

experiment_data = {
    "no_anchor": {"tail_coverage": [], "val_loss": []},
    "random_anchor": {"tail_coverage": [], "val_loss": []},
    "centroid_anchor": {"tail_coverage": [], "val_loss": []},
    "tada": {"tail_coverage": [], "val_loss": []},
}


# ── Corpus generation with Zipfian distribution ───────────────────────────────
def make_zipf_corpus(n_samples, seq_len, vocab_size, alpha=1.2, rng=None):
    """Generate token sequences drawn from a Zipf distribution."""
    if rng is None:
        rng = np.random.default_rng(SEED)
    ranks = np.arange(1, vocab_size + 1, dtype=np.float64)
    probs = 1.0 / ranks**alpha
    probs /= probs.sum()
    corpus = rng.choice(vocab_size, size=(n_samples, seq_len), p=probs)
    return corpus.astype(np.int64)


rng = np.random.default_rng(SEED)
real_corpus = make_zipf_corpus(N_REAL, SEQ_LEN, VOCAB_SIZE, alpha=1.2, rng=rng)

# Compute token frequencies on real corpus
token_counts = Counter(real_corpus.flatten().tolist())
all_tokens = list(range(VOCAB_SIZE))
freqs = np.array([token_counts.get(t, 0) for t in all_tokens], dtype=np.float64)

# Define tail tokens (bottom TAIL_FRACTION by frequency)
n_tail = max(1, int(VOCAB_SIZE * TAIL_FRACTION))
tail_tokens = set(np.argsort(freqs)[:n_tail].tolist())
print(
    f"Tail tokens: {n_tail}  |  most common tail freq: {max(freqs[t] for t in tail_tokens):.0f}"
)


# ── Dataset ───────────────────────────────────────────────────────────────────
class TokenDataset(Dataset):
    def __init__(self, sequences):
        self.data = torch.tensor(sequences, dtype=torch.long)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]


# ── Tiny Transformer LM ───────────────────────────────────────────────────────
class TinyTransformerLM(nn.Module):
    def __init__(self, vocab_size, d_model, n_heads, n_layers, max_len):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.pos_emb = nn.Embedding(max_len, d_model)
        enc_layer = nn.TransformerEncoderLayer(
            d_model, n_heads, dim_feedforward=d_model * 4, dropout=0.1, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        self.head = nn.Linear(d_model, vocab_size)
        self._init_weights()

    def _init_weights(self):
        for p in self.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)

    def forward(self, x):
        B, T = x.shape
        pos = torch.arange(T, device=x.device).unsqueeze(0)
        mask = nn.Transformer.generate_square_subsequent_mask(T, device=x.device)
        h = self.embed(x) + self.pos_emb(pos)
        h = self.encoder(h, mask=mask, is_causal=True)
        return self.head(h)


def make_model():
    m = TinyTransformerLM(VOCAB_SIZE, D_MODEL, N_HEADS, N_LAYERS, SEQ_LEN).to(device)
    return m


# ── Training ──────────────────────────────────────────────────────────────────
def train_one_epoch(model, loader, optimizer):
    model.train()
    total_loss = 0
    n = 0
    for batch in loader:
        batch = batch.to(device)
        x, y = batch[:, :-1], batch[:, 1:]
        logits = model(x)
        loss = F.cross_entropy(logits.reshape(-1, VOCAB_SIZE), y.reshape(-1))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(batch)
        n += len(batch)
    return total_loss / n


def evaluate(model, loader):
    model.eval()
    total_loss = 0
    n = 0
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            x, y = batch[:, :-1], batch[:, 1:]
            logits = model(x)
            loss = F.cross_entropy(logits.reshape(-1, VOCAB_SIZE), y.reshape(-1))
            total_loss += loss.item() * len(batch)
            n += len(batch)
    return total_loss / n


# ── Generation ────────────────────────────────────────────────────────────────
@torch.no_grad()
def generate_sequences(model, n_samples, seq_len, temperature=1.0):
    model.eval()
    # start with token 0 as BOS
    generated = []
    batch_size = min(128, n_samples)
    n_batches = math.ceil(n_samples / batch_size)
    for _ in range(n_batches):
        bs = min(batch_size, n_samples - len(generated))
        seq = torch.zeros(bs, 1, dtype=torch.long, device=device)
        for _ in range(seq_len - 1):
            logits = model(seq)[:, -1, :] / temperature
            probs = torch.softmax(logits, dim=-1)
            nxt = torch.multinomial(probs, 1)
            seq = torch.cat([seq, nxt], dim=1)
        generated.append(seq.cpu().numpy())
    return np.concatenate(generated, axis=0)[:n_samples]


# ── Tail Token Coverage ────────────────────────────────────────────────────────
def tail_token_coverage(sequences, tail_tokens):
    seen = set(sequences.flatten().tolist()) & tail_tokens
    return len(seen) / len(tail_tokens)


# ── Anchor Selection Strategies ────────────────────────────────────────────────
def select_random_anchor(real_corpus, budget, rng_seed):
    idx = np.random.RandomState(rng_seed).permutation(len(real_corpus))[:budget]
    return real_corpus[idx]


def select_centroid_anchor(real_corpus, budget, freqs, rng_seed):
    """Select sequences whose tokens are HIGH-frequency (centroid/common)."""
    scores = np.array([freqs[seq].mean() for seq in real_corpus])
    idx = np.argsort(scores)[::-1][:budget]  # highest avg freq
    return real_corpus[idx]


def select_tada_anchor(real_corpus, budget, freqs, rng_seed):
    """Select sequences whose tokens are LOW-frequency (tail-focused)."""
    scores = np.array([freqs[seq].mean() for seq in real_corpus])
    idx = np.argsort(scores)[:budget]  # lowest avg freq
    return real_corpus[idx]


# ── Full experiment for one strategy ─────────────────────────────────────────
def run_experiment(strategy_name, anchor_set, real_corpus_full):
    """
    strategy_name : str
    anchor_set    : np.ndarray of shape (budget, seq_len) or None
    """
    print(f"\n{'='*60}")
    print(f"  Strategy: {strategy_name}")
    print(f"{'='*60}")

    model = make_model()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    # Initial training on full real data (generation 0)
    train_data = real_corpus_full.copy()

    coverage_list = []
    val_loss_list = []

    for gen in range(N_GENERATIONS):
        print(f"\n  Generation {gen}")

        # Build training set
        if gen == 0:
            combined = train_data  # full real data
        else:
            if anchor_set is not None:
                combined = np.concatenate([synth_data, anchor_set], axis=0)
            else:
                combined = synth_data  # no anchoring

        np.random.shuffle(combined)
        split = int(0.9 * len(combined))
        train_ds = TokenDataset(combined[:split])
        val_ds = TokenDataset(combined[split:])
        train_ld = DataLoader(
            train_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=True
        )
        val_ld = DataLoader(
            val_ds, batch_size=BATCH_SIZE, shuffle=False, drop_last=False
        )

        for ep in range(EPOCHS_PER_GEN):
            tr_loss = train_one_epoch(model, train_ld, optimizer)
            vl_loss = evaluate(model, val_ld)
            print(
                f"    Epoch {ep+1}/{EPOCHS_PER_GEN}: train_loss={tr_loss:.4f}  val_loss={vl_loss:.4f}"
            )

        val_loss_list.append(vl_loss)

        # Generate synthetic data for next generation
        synth_data = generate_sequences(model, N_SYNTHETIC, SEQ_LEN, temperature=1.0)

        # Measure tail token coverage on generated samples
        cov = tail_token_coverage(synth_data, tail_tokens)
        coverage_list.append(cov)
        print(f"  [Gen {gen}] Tail Token Coverage = {cov:.4f}")

    experiment_data[strategy_name]["tail_coverage"] = coverage_list
    experiment_data[strategy_name]["val_loss"] = val_loss_list
    return coverage_list, val_loss_list


# ── Prepare anchor sets ────────────────────────────────────────────────────────
anchor_random = select_random_anchor(real_corpus, ANCHOR_BUDGET, rng_seed=0)
anchor_centroid = select_centroid_anchor(real_corpus, ANCHOR_BUDGET, freqs, rng_seed=0)
anchor_tada = select_tada_anchor(real_corpus, ANCHOR_BUDGET, freqs, rng_seed=0)


# Quick sanity check: compare avg token freq in each anchor set
def mean_anchor_freq(anchor, freqs):
    return freqs[anchor.flatten()].mean()


print(f"\nAnchor set avg token frequency:")
print(f"  Random:   {mean_anchor_freq(anchor_random, freqs):.2f}")
print(f"  Centroid: {mean_anchor_freq(anchor_centroid, freqs):.2f}")
print(f"  TADA:     {mean_anchor_freq(anchor_tada, freqs):.2f}")

# ── Run all strategies ────────────────────────────────────────────────────────
cov_no, vl_no = run_experiment("no_anchor", None, real_corpus)
cov_rnd, vl_rnd = run_experiment("random_anchor", anchor_random, real_corpus)
cov_cen, vl_cen = run_experiment("centroid_anchor", anchor_centroid, real_corpus)
cov_tad, vl_tad = run_experiment("tada", anchor_tada, real_corpus)

# ── Visualisation ─────────────────────────────────────────────────────────────
generations = list(range(N_GENERATIONS))

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

ax = axes[0]
ax.plot(generations, cov_no, "k--o", label="No Anchor")
ax.plot(generations, cov_rnd, "b-o", label="Random Anchor")
ax.plot(generations, cov_cen, "g-s", label="Centroid Anchor")
ax.plot(generations, cov_tad, "r-^", label="TADA (Tail Anchor)", linewidth=2)
ax.set_xlabel("Generation")
ax.set_ylabel("Tail Token Coverage")
ax.set_title("Tail Token Coverage Across Generations")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(0, 1.05)

ax = axes[1]
ax.plot(generations, vl_no, "k--o", label="No Anchor")
ax.plot(generations, vl_rnd, "b-o", label="Random Anchor")
ax.plot(generations, vl_cen, "g-s", label="Centroid Anchor")
ax.plot(generations, vl_tad, "r-^", label="TADA (Tail Anchor)", linewidth=2)
ax.set_xlabel("Generation")
ax.set_ylabel("Validation Loss")
ax.set_title("Validation Loss Across Generations")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "tada_experiment_results.png"), dpi=150)
plt.close()
print(f"\nPlot saved to {working_dir}/tada_experiment_results.png")

# ── Bar chart: final-generation tail coverage ─────────────────────────────────
fig2, ax2 = plt.subplots(figsize=(8, 5))
strategies = ["No Anchor", "Random Anchor", "Centroid Anchor", "TADA"]
final_cov = [cov_no[-1], cov_rnd[-1], cov_cen[-1], cov_tad[-1]]
colors = ["gray", "steelblue", "forestgreen", "crimson"]
bars = ax2.bar(strategies, final_cov, color=colors, edgecolor="black")
ax2.set_ylabel("Tail Token Coverage (final generation)")
ax2.set_title(
    f"Final Generation Tail Coverage (anchor budget = {ANCHOR_BUDGET}/{N_REAL})"
)
ax2.set_ylim(0, 1.05)
for bar, val in zip(bars, final_cov):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        val + 0.02,
        f"{val:.3f}",
        ha="center",
        fontsize=11,
        fontweight="bold",
    )
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "tada_final_coverage_bar.png"), dpi=150)
plt.close()

# ── Print summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY – Tail Token Coverage per Generation")
print("=" * 60)
header = (
    f"{'Gen':>4}  {'No Anchor':>10}  {'Random':>10}  {'Centroid':>10}  {'TADA':>10}"
)
print(header)
for g in generations:
    print(
        f"{g:>4}  {cov_no[g]:>10.4f}  {cov_rnd[g]:>10.4f}  {cov_cen[g]:>10.4f}  {cov_tad[g]:>10.4f}"
    )

print(f"\nFinal generation (Gen {N_GENERATIONS-1}):")
print(f"  No Anchor       : {cov_no[-1]:.4f}")
print(f"  Random Anchor   : {cov_rnd[-1]:.4f}")
print(f"  Centroid Anchor : {cov_cen[-1]:.4f}")
print(f"  TADA            : {cov_tad[-1]:.4f}")
print(f"\nTADA improvement over Random: {cov_tad[-1] - cov_rnd[-1]:+.4f}")
print(f"TADA improvement over No Anchor: {cov_tad[-1] - cov_no[-1]:+.4f}")

# ── Save experiment data ──────────────────────────────────────────────────────
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nExperiment data saved to {working_dir}/experiment_data.npy")
