# Logic Design: H-E1 (Clustering Transformer Hidden States)

**Type**: EXISTENCE (PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - designing new APIs
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Hidden State Clustering Pipeline [Complexity: PoC, Budget: 1]

**Applied**: Standard sklearn KMeans + HuggingFace transformers (no KB pattern needed for PoC)

### API Signatures

```python
def extract_cls_embeddings(
    texts: list[str],
    model_name: str = "bert-base-uncased",
    batch_size: int = 32,
    device: str = "cuda",
) -> np.ndarray:
    """Extract last-layer [CLS] embeddings. Returns [N, 768]."""
    ...

def run_clustering(
    embeddings: np.ndarray,
    k: int = 8,
    seed: int = 42,
) -> np.ndarray:
    """KMeans clustering. embeddings: [N, 768] -> cluster_ids: [N]"""
    ...

def compute_metrics(
    cluster_ids: np.ndarray,
    task_labels: np.ndarray,
) -> dict[str, float]:
    """Purity/ARI/NMI. Both inputs [N] -> {"purity": f, "ari": f, "nmi": f}"""
    ...

def main() -> None:
    """Load SuperGLUE val splits -> extract -> cluster -> evaluate -> plot."""
    ...
```

### Tensor / Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [B, 512] | tokenizer output, padded/truncated |
| hidden_states | [B, 512, 768] | last layer, from `outputs.hidden_states[-1]` |
| cls_embeddings | [B, 768] | `hidden_states[:, 0, :]` |
| all_embeddings | [N, 768] | N = sum of samples across 8 tasks |
| task_labels | [N] | int, 0-7 (one per SuperGLUE task) |
| cluster_ids | [N] | int, 0-7 (KMeans assignment) |

### Pseudo-code (Main Pipeline)

```
1. tasks = ["boolq", "cb", "copa", "multirc", "record", "rte", "wic", "wsc"]
2. for task_idx, task in enumerate(tasks):
     ds = load_dataset("super_glue", task, split="validation")
     texts = extract_text_fields(ds, task)   # task-specific field concat
     embs = extract_cls_embeddings(texts)    # [n_task, 768]
     all_embeddings.append(embs)
     all_labels.append([task_idx] * len(texts))
3. X = concat(all_embeddings)                # [N, 768]
4. y_task = concat(all_labels)                # [N]
5. cluster_ids = run_clustering(X, k=8, seed=42)   # [N]
6. metrics = compute_metrics(cluster_ids, y_task)
7. assert-based gate check: metrics["purity"] > 0.125
8. save metrics.json, plot bar chart + t-SNE scatter to figures/
```

**Extraction pseudo-code (per batch, no_grad)**:
```
with torch.no_grad():
    enc = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
    out = model(**enc, output_hidden_states=True)
    cls = out.hidden_states[-1][:, 0, :]   # [B, 768]
```

### Purity Computation Formula

```
purity = (1/N) * sum over clusters c of max over tasks t of |{i : cluster(i)=c, task(i)=t}|
```
i.e., for each cluster, count the most common true task label in it, sum these max-counts, divide by N.

```python
def purity_score(cluster_ids, task_labels):
    N = len(cluster_ids)
    total = 0
    for c in np.unique(cluster_ids):
        mask = cluster_ids == c
        if mask.sum() == 0:
            continue
        counts = np.bincount(task_labels[mask])
        total += counts.max()
    return total / N
```

ARI/NMI: use `sklearn.metrics.adjusted_rand_score`, `sklearn.metrics.normalized_mutual_info_score` directly (no custom logic).

### Edge Cases

- **Empty cluster** (KMeans assigns 0 points to a cluster c): skip in purity sum (mask.sum()==0 guard above) — does not inflate/deflate purity incorrectly since that cluster contributes 0.
- **Text too long**: tokenizer truncates at max_length=512; no manual chunking needed for PoC.
- **Task field mismatch**: each SuperGLUE task has different input fields (e.g., `question`+`passage` for BoolQ, `premise`+`hypothesis` for RTE) — `extract_text_fields` must branch per task name; use `[SEP]`-joined concatenation of the task's text fields.
- **GPU unavailable**: `device="cuda" if torch.cuda.is_available() else "cpu"` fallback; inference-only so CPU is acceptable for PoC scale.
- **Dataset split has no labels visible for test-only SuperGLUE tasks**: use `validation` split only (per PRD FR-1), never `test`.
- **KMeans non-determinism**: fixed `random_state=42` per PRD; single seed only (out of scope: multi-seed).

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | Data + extraction | Load 8 SuperGLUE val splits, tokenize, extract [CLS] embeddings |
| L-A1-2 | Clustering + metrics | KMeans K=8, purity/ARI/NMI computation, gate check |
| L-A1-3 | Visualization | Bar chart (metrics vs thresholds), t-SNE scatter colored by task |
