# Logic: H-E1
# Code Embedding Distribution Distinctiveness Analysis

**Hypothesis Type**: EXISTENCE (PoC)
**Phase**: 3 — Logic Design
**Date**: 2026-08-02

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — new implementation
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## L-E2-1: CodeBERT Batched Mean-Pool Encoder [Complexity: 11, Budget: 1]

**Applied**: HuggingFace transformers mean-pool pattern (attention-mask weighted)

### API Signature

```python
# src/h_e1/embedder.py

def encode_codebert(
    texts: list[str],
    tokenizer: AutoTokenizer,
    model: AutoModel,
    batch_size: int = 32,
    device: str = "cuda",
    max_length: int = 512,
) -> torch.Tensor:  # (N, 768) float32, L2-normalized
    """Mean-pool last hidden states weighted by attention_mask. Returns unit vectors."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, L] | L <= max_length=512 |
| attention_mask | [B, L] | 0/1 pad mask |
| last_hidden_state | [B, L, 768] | from model output |
| mask_expanded | [B, L, 1] | broadcast for weighted mean |
| pooled | [B, 768] | sum(hidden * mask) / sum(mask) |
| output | (N, 768) | all batches stacked, L2-normalized |

### Pseudo-code

```
model.eval(); model.to(device)
all_embs = []
effective_batch = batch_size
for chunk in chunks(texts, effective_batch):
    try:
        enc = tokenizer(chunk, padding=True, truncation=True,
                        max_length=512, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model(**enc)
        mask = enc["attention_mask"].unsqueeze(-1).float()   # [B, L, 1]
        pooled = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)  # [B, 768]
        all_embs.append(F.normalize(pooled, dim=-1).cpu())
    except RuntimeError:  # OOM
        effective_batch = batch_size // 4
        torch.cuda.empty_cache()
        re-queue chunk with effective_batch

logging.info(f"Encoded {len(texts)} problems for {source} with codebert")
return torch.cat(all_embs, dim=0)  # (N, 768)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1-1 | codebert_mean_pool | Batched encode with OOM fallback |

---

## L-E2-2: MiniLM Encoder + encode_all_corpora Orchestrator [Complexity: 11, Budget: 1]

**Applied**: sentence-transformers normalize_embeddings pattern

### API Signatures

```python
# src/h_e1/embedder.py

def encode_minilm(
    texts: list[str],
    batch_size: int = 32,
) -> torch.Tensor:  # (N, 384) float32, L2-normalized
    """Encode via all-MiniLM-L6-v2 with normalize_embeddings=True."""
    ...

def encode_all_corpora(
    corpora: dict[str, list[str]],
    batch_size: int = 32,
    device: str = "cuda",
) -> dict[str, dict[str, torch.Tensor]]:
    # returns {corpus_name: {"codebert": Tensor(N,768), "minilm": Tensor(N,384)}}
    """Encode all corpora with both encoders. Logs per-corpus counts."""
    ...
```

### Pseudo-code

```
# encode_minilm
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embs = model.encode(texts, batch_size=batch_size,
                    normalize_embeddings=True, show_progress_bar=True,
                    convert_to_tensor=True)
return embs.cpu().float()  # (N, 384)

# encode_all_corpora
tokenizer, cb_model = AutoTokenizer/AutoModel.from_pretrained("microsoft/codebert-base")
cb_model.to(device).eval()
results = {}
for name, texts in corpora.items():
    N = len(texts)
    results[name] = {
        "codebert": encode_codebert(texts, tokenizer, cb_model, batch_size, device),
        "minilm": encode_minilm(texts, batch_size),
    }
    logging.info(f"Encoded {N} problems for {name} with codebert")
    logging.info(f"Encoded {N} problems for {name} with minilm")
return results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-2-1 | minilm_and_orchestrator | encode_minilm + encode_all_corpora wiring |

---

## L-E3-1: Similarity Matrix + Gate Evaluation [Complexity: 9, Budget: 1]

**Applied**: PyTorch matmul cosine on L2-normalized tensors (dot product == cosine)

### API Signatures

```python
# src/h_e1/similarity.py

SOURCES = ["humaneval_train", "mbpp_train", "leetcode", "equal_mix"]  # rows
BENCHMARKS = ["humaneval_plus", "mbpp_plus"]                          # cols

def mean_pairwise_cosine(
    src: torch.Tensor,  # (N, D) L2-normalized
    tgt: torch.Tensor,  # (M, D) L2-normalized
) -> float:
    # (src @ tgt.T).mean().item() — valid for unit vectors
    ...

def compute_similarity_matrix(
    embeddings: dict[str, dict[str, torch.Tensor]],
) -> dict[str, np.ndarray]:
    # returns {"codebert": ndarray(4,2), "minilm": ndarray(4,2)}
    # rows: SOURCES order, cols: BENCHMARKS order
    ...

def evaluate_gate(
    sim_matrices: dict[str, np.ndarray],
) -> dict:
    # returns {
    #   "gate_satisfied": bool,    # any of 16 values < 0.95
    #   "min_sim": float,
    #   "max_sim": float,
    #   "mean_sim": float,
    #   "std_sim": float,
    #   "all_values": list[float]  # 16 values flat (both encoders)
    # }
    ...
```

### Pseudo-code

```
# mean_pairwise_cosine
return (src.cpu() @ tgt.cpu().T).mean().item()

# compute_similarity_matrix
result = {}
for encoder in ["codebert", "minilm"]:
    mat = np.zeros((4, 2))
    for i, src_name in enumerate(SOURCES):
        for j, bm_name in enumerate(BENCHMARKS):
            mat[i, j] = mean_pairwise_cosine(
                embeddings[src_name][encoder],
                embeddings[bm_name][encoder],
            )
    result[encoder] = mat
return result

# evaluate_gate
all_values = [v for mat in sim_matrices.values() for v in mat.flatten().tolist()]
return {
    "gate_satisfied": min(all_values) < 0.95,
    "min_sim": min(all_values),
    "max_sim": max(all_values),
    "mean_sim": float(np.mean(all_values)),
    "std_sim": float(np.std(all_values)),
    "all_values": all_values,
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1-1 | similarity_and_gate | 4x2 matrix + gate check over 16 values |

---

## L-E4-1: Heatmap Generation [Complexity: 10, Budget: 1]

**Applied**: Standard seaborn heatmap with matplotlib subplots

### API Signature

```python
# src/h_e1/visualize.py

def plot_heatmaps(
    sim_matrices: dict[str, np.ndarray],  # {"codebert": (4,2), "minilm": (4,2)}
    output_dir: str,
    threshold: float = 0.95,
) -> None:
    # side-by-side subplots: CodeBERT (left) + MiniLM (right)
    # seaborn heatmap, annot=True, fmt=".3f"
    # horizontal threshold line at 0.95 annotated
    # saves: {output_dir}/similarity_heatmaps.png
    ...
```

### Pseudo-code

```
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, (encoder, mat) in zip(axes, sim_matrices.items()):
    sns.heatmap(mat, ax=ax, annot=True, fmt=".3f",
                xticklabels=["HumanEval+", "MBPP+"],
                yticklabels=["HumanEval-train", "MBPP-train", "LeetCode", "Equal-mix"],
                vmin=0.0, vmax=1.0, cmap="Blues")
    ax.set_title(f"{encoder.upper()} — Mean Pairwise Cosine Similarity")
    # threshold annotation: text + horizontal line (categorical axis uses data coords)
    ax.axhline(y=len(SOURCES) * threshold, color="red", ls="--", lw=1.5)
    ax.text(len(BENCHMARKS) + 0.05, len(SOURCES) * threshold,
            f"threshold={threshold}", color="red", va="center", fontsize=9)

os.makedirs(output_dir, exist_ok=True)
fig.tight_layout()
fig.savefig(os.path.join(output_dir, "similarity_heatmaps.png"), dpi=150, bbox_inches="tight")
plt.close(fig)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1-1 | plot_heatmaps | Dual-encoder side-by-side heatmap PNG |

---

## L-E4-2: Main Experiment Runner [Complexity: 10, Budget: 1]

**Applied**: Standard pipeline runner pattern

### API Signature

```python
# src/h_e1/run_experiment.py

def main(
    batch_size: int = 32,
    device: str = "cuda",
    seed: int = 42,
    figures_dir: str = "docs/youra_research/h-e1/figures",
    skip_tsne: bool = False,
) -> dict:
    # 1. load_all_corpora(seed=seed)
    # 2. encode_all_corpora(corpora, batch_size, device)
    # 3. compute_similarity_matrix(embeddings)
    # 4. evaluate_gate(sim_matrices)
    # 5. plot_heatmaps(sim_matrices, figures_dir)
    # 6. print 4x2 table + gate result
    # 7. return gate_result for downstream use
    """Full pipeline: load -> embed -> similarity -> gate -> visualize -> summary."""
    ...
```

### Pseudo-code

```
random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
if device == "cuda" and not torch.cuda.is_available():
    logging.warning("CUDA unavailable, falling back to CPU"); device = "cpu"

corpora = load_all_corpora(seed=seed)
embeddings = encode_all_corpora(corpora, batch_size=batch_size, device=device)
sim_matrices = compute_similarity_matrix(embeddings)
gate_result = evaluate_gate(sim_matrices)
plot_heatmaps(sim_matrices, output_dir=figures_dir, threshold=0.95)
if not skip_tsne:
    plot_tsne(embeddings, output_dir=figures_dir, encoder="codebert")

# print 4x2 table per encoder
for encoder, mat in sim_matrices.items():
    print(f"\n{encoder.upper()} Similarity Matrix (rows=sources, cols=benchmarks):")
    for i, src in enumerate(SOURCES):
        row = "  ".join(f"{mat[i,j]:.4f}" for j in range(len(BENCHMARKS)))
        print(f"  {src:<20} {row}")
status = "SATISFIED" if gate_result["gate_satisfied"] else "FAILED"
print(f"\nGate: {status} | min={gate_result['min_sim']:.4f} "
      f"mean={gate_result['mean_sim']:.4f} std={gate_result['std_sim']:.4f}")

return gate_result

if __name__ == "__main__":
    import fire; fire.Fire(main)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-2-1 | main_runner | Full pipeline wiring + summary print |

---

## Subtask Budget Summary

| ID | Parent Epic | Description | Budget |
|----|-------------|-------------|--------|
| L-E2-1-1 | E2 (complexity 11) | codebert_mean_pool | 1/1 |
| L-E2-2-1 | E2 (complexity 11) | minilm_and_orchestrator | 1/1 |
| L-E3-1-1 | E3 (complexity 9) | similarity_and_gate | 1/1 |
| L-E4-1-1 | E4 (complexity 10) | plot_heatmaps | 1/1 |
| L-E4-2-1 | E4 (complexity 10) | main_runner | 1/1 |

**Total**: 5/5 subtasks used
