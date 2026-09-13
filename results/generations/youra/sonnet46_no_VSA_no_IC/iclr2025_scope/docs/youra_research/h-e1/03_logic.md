---
hypothesis_id: h-e1
phase: 03_logic
date: 2026-08-22
author: yoon303@etri.re.kr
---

# Logic Design: h-e1 — Per-Layer Attention Entropy Stability

Applied: PyTorch output_attentions forward-pass pattern (attention weight extraction per layer)
Applied: Shannon entropy computation pattern (H = -Σ p·log(p+ε), averaged over heads and positions)
Applied: HuggingFace datasets streaming/tokenization pattern (chunk-and-split without padding)
Applied: scipy.stats.spearmanr rank correlation pattern (pairwise vector correlation)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No prior entropy or attention extraction code in project.
All design decisions derived from GAIR-NLP/Entropy-ABF and HuggingFace modeling_llama.py references.

---

## Subtask L-A2-1: chunk_and_split()

**Epic**: A-2 (Data Loading, complexity 7)

### API Signature

```python
def chunk_and_split(
    texts: list[str],
    tokenizer_name: str = "meta-llama/Llama-2-7b-hf",
    seqlen: int = 2048,
    n_subsets: int = 3,
    subset_size: int = 100,
) -> tuple[list[torch.Tensor], list[torch.Tensor], list[torch.Tensor]]:
    """
    Tokenize WikiText-103 texts, chunk into seqlen windows, split into n_subsets.

    Returns:
        (subset_A, subset_B, subset_C) — each a list of `subset_size` tensors of shape (1, seqlen)
    """
```

### Tensor Shapes

| Step | Shape | dtype | Notes |
|------|-------|-------|-------|
| texts | `list[str]` | str | Raw WikiText-103 validation entries |
| concatenated | `str` | str | Single joined string |
| token_ids | `(N_total,)` | int64 | Full tokenization, no truncation |
| chunks | `list[(1, 2048)]` | int64 | Non-overlapping windows; last partial window discarded |
| subset_A | `list[100 × (1, 2048)]` | int64 | chunks[0:100] |
| subset_B | `list[100 × (1, 2048)]` | int64 | chunks[100:200] |
| subset_C | `list[100 × (1, 2048)]` | int64 | chunks[200:300] |

### Pseudo-code

```python
def chunk_and_split(texts, tokenizer_name, seqlen, n_subsets, subset_size):
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    full_text = "\n\n".join(t for t in texts if t.strip())

    # Tokenize without truncation or padding
    token_ids = tokenizer.encode(full_text, add_special_tokens=False)
    token_ids = torch.tensor(token_ids, dtype=torch.long)  # (N_total,)

    # Chunk into non-overlapping seqlen windows
    n_chunks = len(token_ids) // seqlen
    token_ids = token_ids[:n_chunks * seqlen]             # drop remainder
    chunks = token_ids.view(n_chunks, seqlen)             # (n_chunks, seqlen)
    # Add batch dim: each element is (1, seqlen)
    chunk_list = [chunks[i].unsqueeze(0) for i in range(n_chunks)]

    required = n_subsets * subset_size  # 300
    assert len(chunk_list) >= required, f"Need ≥{required} chunks, got {len(chunk_list)}"

    subset_A = chunk_list[0:100]
    subset_B = chunk_list[100:200]
    subset_C = chunk_list[200:300]
    return subset_A, subset_B, subset_C
```

---

## Subtask L-A4-1: compute_layer_entropy()

**Epic**: A-4 (Entropy Computation, complexity 10)

### API Signature

```python
def compute_layer_entropy(
    model: AutoModelForCausalLM,
    input_ids: torch.Tensor,   # (1, seq_len) on model device
    eps: float = 1e-9,
) -> np.ndarray:               # (n_layers,) mean Shannon entropy per layer
    """
    Single forward pass with output_attentions=True.
    Returns per-layer mean entropy (averaged over heads and query positions).
    Deletes attention tensors after use to free VRAM.
    """
```

### Tensor Shapes

| Step | Shape | dtype | Notes |
|------|-------|-------|-------|
| input_ids | `(1, 2048)` | int64 | Single sequence, on device |
| output.attentions | `tuple[32 × (1, 32, 2048, 2048)]` | float32 | Softmax weights; each layer |
| attn (squeezed) | `(32, 2048, 2048)` | float32 (→ numpy) | n_heads × seq × seq |
| H per position | `(32, 2048)` | float64 | H[h,q] = -Σ_k attn[h,q,k]·log(attn[h,q,k]+ε) |
| H mean | scalar | float64 | mean over all heads and positions |
| entropy_per_layer | `(32,)` | float64 | One scalar per layer |

### Memory Note

Each attention tensor `(1, 32, 2048, 2048)` in float32 = 1 × 32 × 2048 × 2048 × 4 bytes ≈ **512 MB**.
Storing all 32 layers simultaneously = ~16 GB. **Must delete each tensor after processing.**

### Pseudo-code

```python
def compute_layer_entropy(model, input_ids, eps=1e-9):
    with torch.no_grad():
        output = model(input_ids, output_attentions=True)
    # output.attentions: tuple of 32 tensors, each (1, 32, 2048, 2048)

    n_layers = len(output.attentions)
    entropy_per_layer = np.zeros(n_layers, dtype=np.float64)

    for layer_idx in range(n_layers):
        attn = output.attentions[layer_idx]      # (1, 32, 2048, 2048)
        attn_np = attn.squeeze(0).float().cpu().numpy()  # (32, 2048, 2048)
        del attn                                  # free VRAM immediately

        # Shannon entropy per (head, query_position)
        # H[h, q] = -sum_k attn_np[h, q, k] * log(attn_np[h, q, k] + eps)
        H = -np.sum(attn_np * np.log(attn_np + eps), axis=-1)  # (32, 2048)
        entropy_per_layer[layer_idx] = H.mean()   # scalar

        del attn_np, H                            # free numpy array

    return entropy_per_layer  # (32,)
```

---

## Subtask L-A4-2: score_subset()

**Epic**: A-4 (Entropy Computation, complexity 10)

### API Signature

```python
def score_subset(
    model: AutoModelForCausalLM,
    sequences: list[torch.Tensor],  # list of (1, 2048) tensors
    eps: float = 1e-9,
    verbose: bool = True,
) -> np.ndarray:                    # (n_layers,) mean entropy over all sequences
    """
    Run compute_layer_entropy() for each sequence, accumulate, return mean.
    Prints progress every 10 sequences if verbose=True.
    """
```

### Tensor Shapes

| Step | Shape | Notes |
|------|-------|-------|
| per-sequence entropy | `(32,)` | output of compute_layer_entropy |
| accumulated | `(N_seq, 32)` | stacked after all sequences |
| mean output | `(32,)` | mean over axis=0 |

### Pseudo-code

```python
def score_subset(model, sequences, eps=1e-9, verbose=True):
    all_entropies = []
    for i, input_ids in enumerate(sequences):
        input_ids = input_ids.to(model.device)
        layer_ent = compute_layer_entropy(model, input_ids, eps=eps)
        all_entropies.append(layer_ent)
        if verbose and (i + 1) % 10 == 0:
            print(f"  Processed {i+1}/{len(sequences)} sequences")

    return np.mean(all_entropies, axis=0)  # (32,)
```

---

## Subtask L-A5-1: compute_spearman()

**Epic**: A-5 (Reporting & Figures, complexity 9)

### API Signature

```python
def compute_spearman(
    entropy_A: np.ndarray,   # (32,) mean entropy for subset A
    entropy_B: np.ndarray,   # (32,) mean entropy for subset B
    entropy_C: np.ndarray,   # (32,) mean entropy for subset C
    gate_threshold: float = 0.8,
) -> dict:
    """
    Compute 3 pairwise Spearman rank correlations.

    Returns:
        {
            "rho_AB": float, "p_AB": float,
            "rho_AC": float, "p_AC": float,
            "rho_BC": float, "p_BC": float,
            "min_rho": float,
            "mean_rho": float,
            "gate_pass": bool,
            "gate_threshold": float,
        }
    """
```

### Pseudo-code

```python
from scipy.stats import spearmanr

def compute_spearman(entropy_A, entropy_B, entropy_C, gate_threshold=0.8):
    rho_AB, p_AB = spearmanr(entropy_A, entropy_B)
    rho_AC, p_AC = spearmanr(entropy_A, entropy_C)
    rho_BC, p_BC = spearmanr(entropy_B, entropy_C)

    min_rho = min(rho_AB, rho_AC, rho_BC)
    mean_rho = (rho_AB + rho_AC + rho_BC) / 3.0

    return {
        "rho_AB": float(rho_AB), "p_AB": float(p_AB),
        "rho_AC": float(rho_AC), "p_AC": float(p_AC),
        "rho_BC": float(rho_BC), "p_BC": float(p_BC),
        "min_rho": float(min_rho),
        "mean_rho": float(mean_rho),
        "gate_pass": bool(min_rho >= gate_threshold),
        "gate_threshold": gate_threshold,
    }
```

---

## Subtask L-A5-2: generate_figures()

**Epic**: A-5 (Reporting & Figures, complexity 9)

### API Signature

```python
def generate_figures(
    spearman: dict,
    entropy_A: np.ndarray,   # (32,)
    entropy_B: np.ndarray,   # (32,)
    entropy_C: np.ndarray,   # (32,)
    figures_dir: str = "figures/",
) -> None:
    """
    Generate and save 4 figures to figures_dir.
    Creates figures_dir if it does not exist.
    """
```

### Figure Specifications

| Figure | Filename | Description |
|--------|----------|-------------|
| 1 | `entropy_stability.png` | Bar chart: 3 pairwise ρ values + horizontal line at 0.8 threshold; color green if ≥0.8 else red |
| 2 | `layer_entropy_per_subset.png` | Line/bar chart: x=layer index 0–31, y=mean entropy; 3 lines (A/B/C) overlaid with legend |
| 3 | `rank_correlation_scatter.png` | 3 scatter subplots: entropy_A vs B, A vs C, B vs C; annotate ρ value on each |
| 4 | `top8_overlap.png` | Table/heatmap: top-8 highest-entropy layers per subset and their overlap count |

### Pseudo-code (figure 1 as example)

```python
import matplotlib.pyplot as plt
import pathlib, numpy as np

def generate_figures(spearman, entropy_A, entropy_B, entropy_C, figures_dir="figures/"):
    pathlib.Path(figures_dir).mkdir(parents=True, exist_ok=True)
    threshold = spearman["gate_threshold"]

    # Figure 1: entropy_stability.png
    rho_vals = [spearman["rho_AB"], spearman["rho_AC"], spearman["rho_BC"]]
    colors = ["green" if r >= threshold else "red" for r in rho_vals]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["ρ(A,B)", "ρ(A,C)", "ρ(B,C)"], rho_vals, color=colors)
    ax.axhline(threshold, color="black", linestyle="--", label=f"threshold={threshold}")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Spearman ρ")
    ax.set_title(f"Entropy Stability — Gate: {'PASS' if spearman['gate_pass'] else 'FAIL'}")
    ax.legend()
    fig.savefig(f"{figures_dir}/entropy_stability.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 2: layer_entropy_per_subset.png
    layers = np.arange(32)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(layers, entropy_A, label="Subset A", alpha=0.8)
    ax.plot(layers, entropy_B, label="Subset B", alpha=0.8)
    ax.plot(layers, entropy_C, label="Subset C", alpha=0.8)
    ax.set_xlabel("Layer Index"); ax.set_ylabel("Mean Entropy")
    ax.set_title("Per-Layer Attention Entropy (3 Subsets)")
    ax.legend(); fig.savefig(f"{figures_dir}/layer_entropy_per_subset.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 3: rank_correlation_scatter.png
    pairs = [("A", "B", entropy_A, entropy_B, spearman["rho_AB"]),
             ("A", "C", entropy_A, entropy_C, spearman["rho_AC"]),
             ("B", "C", entropy_B, entropy_C, spearman["rho_BC"])]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, (la, lb, ea, eb, rho) in zip(axes, pairs):
        ax.scatter(ea, eb, alpha=0.7)
        ax.set_xlabel(f"Entropy {la}"); ax.set_ylabel(f"Entropy {lb}")
        ax.set_title(f"ρ={rho:.3f}")
    fig.savefig(f"{figures_dir}/rank_correlation_scatter.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # Figure 4: top8_overlap.png
    top8_A = set(np.argsort(entropy_A)[::-1][:8])
    top8_B = set(np.argsort(entropy_B)[::-1][:8])
    top8_C = set(np.argsort(entropy_C)[::-1][:8])
    overlap_ABC = top8_A & top8_B & top8_C
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.axis("off")
    table_data = [
        ["Subset A top-8", str(sorted(top8_A))],
        ["Subset B top-8", str(sorted(top8_B))],
        ["Subset C top-8", str(sorted(top8_C))],
        ["3-way overlap", str(sorted(overlap_ABC))],
        ["|overlap|", str(len(overlap_ABC))],
    ]
    ax.table(cellText=table_data, colLabels=["Metric", "Value"], loc="center", cellLoc="left")
    ax.set_title("Top-8 Highest-Entropy Layer Overlap")
    fig.savefig(f"{figures_dir}/top8_overlap.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
```

---

## Memory Budget Estimate

| Component | VRAM |
|-----------|------|
| Llama-2-7B (float16) | ~14 GB |
| Single attention tensor (1, 32, 2048, 2048) float32 | ~512 MB |
| Peak (model + 1 attention tensor) | ~14.5 GB |
| Recommended GPU VRAM | ≥24 GB |

Deleting each attention tensor immediately after entropy computation keeps peak at ~14.5 GB.
